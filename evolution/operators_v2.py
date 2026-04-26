"""Mutation and crossover operators for V2/V3 game evolution.

Replaces the V1 operators (which mutated expression trees) with operators
that work on V2/V3's structured rule components: placement, capture,
propagation, win condition, turn structure, topology, topology type,
and action types.
"""

from __future__ import annotations

import copy
import uuid

import numpy as np

from config import EvolutionConfig
from game_engine.rules import (
    ActionRule,
    CARule,
    PlacementRule,
    CaptureRule,
    PropagationRule,
    WinCondition,
    TurnStructure,
    ACTION_TYPES,
    MOVE_CONSTRAINTS,
    PLACEMENT_TARGETS,
    PLACEMENT_CONSTRAINTS,
    CAPTURE_TYPES,
    PROPAGATION_TYPES,
    WIN_CONDITION_TYPES,
    TURN_TYPES,
)
from game_engine.game_def_v2 import GameDefV2
from game_engine.topology import TopologicalSpace, TOPOLOGY_TYPES, EXPERIMENTAL_TOPOLOGIES


# Default maximum total cells when computing axis_size for topology mutations.
_MAX_TOTAL_CELLS = 64

# Maximum number of dimensions allowed.  Set from run.py / EvolutionaryLoop
# based on GameConfig.max_dimensions.  Default 6 matches config.py default.
_MAX_DIMENSIONS = 6


# ======================================================================
# Consistency fixups
# ======================================================================

def _fix_consistency(game: GameDefV2, audit_soft_rules: bool = False) -> None:
    """Fix known rule inconsistencies in-place.

    - Enforce minimum axis_size (4 for 2D/3D, 3 for 4D+).
    - Hex topology requires num_dimensions == 2; demote to grid.
    - Custodian capture on hex/moore → change to surround.
    - At least one action type must be enabled; default to place.
    - Majority win condition (removed in V3) → change to connection.
    - Move-only games must have capture != "none".
    - Cascade propagation requires custodian capture; demote to none.
    - Vestigial influence: demote to none when win != threshold.
    - Connection win condition requires axis_size >= 3; demote to territory.
    - Connection: ensure P1 and P2 connect different axes.
    - target_dimension must be in [0, num_dimensions - 1].
    - Outnumber threshold must be >= 2.
    - Threshold win condition must respect influence floor and ceiling.
    - Multi-place only on boards with >= 100 cells.
    """
    # Enforce dimension bounds
    if game.num_dimensions > _MAX_DIMENSIONS:
        game.num_dimensions = _MAX_DIMENSIONS
        game.axis_size = TopologicalSpace.compute_axis_size(
            game.num_dimensions, _MAX_TOTAL_CELLS
        )

    # Enforce minimum axis_size: 4 for 2D/3D, 3 for 4D+
    min_axis = 4 if game.num_dimensions <= 3 else 3
    if game.axis_size < min_axis:
        game.axis_size = min_axis

    # Hex topology requires 2D (V3)
    if game.topology_type == "hex" and game.num_dimensions != 2:
        game.topology_type = "grid"

    # Custodian capture incompatible with hex/moore (V3)
    if (
        game.capture_rule.capture_type == "custodian"
        and game.topology_type in ("hex", "moore")
    ):
        game.capture_rule.capture_type = "surround"

    # moore + surround is structurally inert — 8-neighbour liberty count means
    # interior stones almost never die. Generator already downgrades this to
    # grid; mirror it here so mutation/crossover can't reintroduce it.
    if (
        game.capture_rule.capture_type == "surround"
        and game.topology_type == "moore"
    ):
        game.topology_type = "grid"

    # At least one action type must be enabled (V3)
    if not game.action_rule.action_types:
        game.action_rule.action_types = ("place",)

    # Majority win removed in V3 — upgrade to connection
    if game.win_condition.condition_type == "majority":
        game.win_condition.condition_type = "connection"

    # Move-only games must have capture (V3)
    if (
        game.action_rule.has_move()
        and not game.action_rule.has_place()
        and game.capture_rule.capture_type == "none"
    ):
        game.capture_rule.capture_type = "surround"

    # Cascade propagation only works with custodian capture
    # (cascade+surround is provably inert: removing stones creates liberties)
    if (
        game.propagation_rule.prop_type == "cascade"
        and game.capture_rule.capture_type != "custodian"
    ):
        game.propagation_rule.prop_type = "none"

    # Sierpinski only earns its keep with path-routing/territory wins;
    # threshold-race is structurally inert on the fractal substrate
    # (R17 fractal-spike Pairs A+B at Δ Overall 0.00 each). Mirror the
    # generator's quick_reject so a mutation that flips win_condition
    # to threshold gets demoted to connection rather than rejected.
    # Audit mode skips this demotion so the combo can train and we can
    # validate the prior post-run.
    if (
        not audit_soft_rules
        and game.topology_type == "sierpinski"
        and game.win_condition.condition_type == "threshold"
    ):
        game.win_condition.condition_type = "connection"

    # Influence <-> threshold consistency:
    # Vestigial influence: only threshold win uses board_values
    if (
        game.propagation_rule.prop_type == "influence"
        and game.win_condition.condition_type != "threshold"
    ):
        game.propagation_rule.prop_type = "none"
    # Threshold requires influence propagation (otherwise board_values = 0)
    if (
        game.win_condition.condition_type == "threshold"
        and game.propagation_rule.prop_type != "influence"
    ):
        game.propagation_rule.prop_type = "influence"

    # Connection win needs axis_size >= 3 and num_dimensions >= 2
    if game.win_condition.condition_type == "connection" and (
        game.axis_size < 3 or game.num_dimensions < 2
    ):
        game.win_condition.condition_type = "territory"

    # Clamp target_dimension to valid range
    if game.num_dimensions > 0:
        game.win_condition.target_dimension = min(
            max(game.win_condition.target_dimension, 0),
            game.num_dimensions - 1,
        )

    # Connection: ensure P1 and P2 connect different axes
    if game.win_condition.condition_type == "connection":
        dim_p1 = game.win_condition.target_dimension
        dim_p2 = game.win_condition.target_dimension_p2
        # Clamp P2 dimension to valid range
        if dim_p2 >= 0:
            dim_p2 = min(max(dim_p2, 0), game.num_dimensions - 1)
        # Auto-assign or fix collision
        if dim_p2 < 0 or dim_p2 == dim_p1:
            dim_p2 = (dim_p1 + 1) % game.num_dimensions
        game.win_condition.target_dimension_p2 = dim_p2

    # Outnumber threshold must be >= 2 (threshold=1 auto-captures everything)
    if (
        game.capture_rule.capture_type == "outnumber"
        and game.capture_rule.threshold < 2
    ):
        game.capture_rule.threshold = 2

    # Threshold win condition: floor based on influence achievability
    if game.win_condition.condition_type == "threshold":
        strength = game.propagation_rule.strength
        radius = game.propagation_rule.radius
        min_threshold = 10.0 * strength * (1.0 + radius)
        if game.win_condition.threshold < min_threshold:
            game.win_condition.threshold = min_threshold
        # Cap: threshold must be reachable
        total_cells = game.axis_size ** game.num_dimensions
        cells_in_radius = min(
            total_cells, (2 * radius + 1) ** game.num_dimensions
        )
        max_threshold = (total_cells // 2) * strength * cells_in_radius * 0.8
        if max_threshold > min_threshold and game.win_condition.threshold > max_threshold:
            game.win_condition.threshold = max_threshold

    # Multi-place only on boards with >= 100 cells
    total_cells = game.axis_size ** game.num_dimensions
    if game.turn_structure.turn_type == "multi_place" and total_cells < 100:
        game.turn_structure.turn_type = "alternating"
        game.turn_structure.pieces_per_turn = 1

    # Simultaneous: place-only (movement under simultaneous not yet supported)
    if game.turn_structure.turn_type == "simultaneous":
        game.turn_structure.pieces_per_turn = 1
        if game.action_rule.has_move():
            game.action_rule.action_types = ("place",)

    # CA games: capture and propagation must be "none"
    if game.ca_rule is not None:
        game.capture_rule.capture_type = "none"
        game.propagation_rule.prop_type = "none"


# ======================================================================
# CA crossover helper
# ======================================================================

_CA_SWAP = {0: 0, 1: 2, 2: 1}


def _crossover_ca_rules(
    ca_a: CARule | None,
    ca_b: CARule | None,
    rng: np.random.Generator,
) -> CARule | None:
    """Crossover two CA rules. Returns None if neither parent has CA.

    If both have CA: blend only the "primary" entries (state=0 with f<=e,
    and state=1 for all f,e) from parent A or B, then derive state=0 mirror
    entries and the full state=2 row from the blended primary entries.
    This preserves the player-swap symmetry invariant even when A and B
    differ. Independent per-entry sampling across all keys would break the
    invariant with probability proportional to the parents' differences
    (observed in R14 as a cumulative bias).

    If only one has CA: the child gets CA with 50% probability.
    """
    if ca_a is None and ca_b is None:
        return None

    if ca_a is not None and ca_b is not None:
        max_nbrs = max(ca_a.max_neighbors, ca_b.max_neighbors)
        new_table: dict[tuple[int, int, int], int] = {}
        for f in range(max_nbrs + 1):
            for e in range(max_nbrs + 1):
                # Empty cells: sample once per unordered pair, mirror both ways.
                if f <= e:
                    src_empty = ca_a.transition_table if rng.random() < 0.5 else ca_b.transition_table
                    v_empty = src_empty.get((0, f, e), 0)
                    new_table[(0, f, e)] = v_empty
                    new_table[(0, e, f)] = v_empty
                # State 1: sample from A or B. State 2 derived by swap.
                src_own = ca_a.transition_table if rng.random() < 0.5 else ca_b.transition_table
                v_own = src_own.get((1, f, e), 1)
                new_table[(1, f, e)] = v_own
                new_table[(2, e, f)] = _CA_SWAP[v_own]
        steps = ca_a.steps_per_turn if rng.random() < 0.5 else ca_b.steps_per_turn
        return CARule(
            transition_table=new_table,
            steps_per_turn=steps,
            max_neighbors=max_nbrs,
        )

    # Only one parent has CA: child gets it with 50% probability
    if rng.random() < 0.5:
        source = ca_a if ca_a is not None else ca_b
        return copy.deepcopy(source)
    return None


# ======================================================================
# MutationOperatorV2
# ======================================================================

class MutationOperatorV2:
    """Mutation operators for V2/V3 structured-rule games."""

    def __init__(
        self,
        config: EvolutionConfig,
        rng: np.random.Generator,
        audit_soft_rules: bool = False,
    ) -> None:
        self.config = config
        self.rng = rng
        self.audit_soft_rules = audit_soft_rules

    def mutate_game(self, game: GameDefV2) -> GameDefV2:
        """Mutate a V2/V3 game definition.

        Creates a deep copy and applies one or more mutations chosen at
        random from: placement, capture, propagation, win condition,
        topology, turn structure, topology type, and action types.
        Always generates a new game_id and tracks parentage in metadata.
        """
        child = copy.deepcopy(game)
        mutation_types: list[str] = []

        # Roll for each mutation type
        roll_placement = self.rng.random() < 0.30
        roll_capture = self.rng.random() < 0.25
        roll_propagation = self.rng.random() < 0.25
        roll_win = self.rng.random() < 0.25
        roll_topology = self.rng.random() < 0.15
        roll_turn = self.rng.random() < 0.20
        roll_topology_type = self.rng.random() < 0.15
        roll_action_types = self.rng.random() < 0.20
        roll_ca_rule = game.ca_rule is not None and self.rng.random() < 0.35
        roll_ca_steps = game.ca_rule is not None and self.rng.random() < 0.20

        # Ensure at least one fires; default to placement
        if not any([
            roll_placement, roll_capture, roll_propagation,
            roll_win, roll_topology, roll_turn,
            roll_topology_type, roll_action_types,
            roll_ca_rule, roll_ca_steps,
        ]):
            roll_placement = True

        if roll_placement:
            mutation_types.append("placement")
            self._mutate_placement(child)

        if roll_capture:
            mutation_types.append("capture")
            self._mutate_capture(child)

        if roll_propagation:
            mutation_types.append("propagation")
            self._mutate_propagation(child)

        if roll_win:
            mutation_types.append("win_condition")
            self._mutate_win_condition(child)

        if roll_topology:
            mutation_types.append("topology")
            self._mutate_topology(child)

        if roll_turn:
            mutation_types.append("turn_structure")
            self._mutate_turn_structure(child)

        if roll_topology_type:
            mutation_types.append("topology_type")
            self._mutate_topology_type(child)

        if roll_action_types:
            mutation_types.append("action_types")
            self._mutate_action_types(child)

        if roll_ca_rule:
            mutation_types.append("ca_rule")
            self._mutate_ca_rule(child)

        if roll_ca_steps:
            mutation_types.append("ca_steps")
            self._mutate_ca_steps(child)

        # Fix any inconsistencies introduced by the mutations
        _fix_consistency(child, audit_soft_rules=self.audit_soft_rules)

        # Assign new identity and parentage
        new_id = uuid.uuid4().hex[:12]
        generation = game.metadata.get("generation", 0) + 1

        child.game_id = new_id
        child.metadata = {
            "parents": [game.game_id],
            "generation": generation,
            "mutation_types": mutation_types,
        }
        return child

    # ------------------------------------------------------------------
    # Individual mutation methods
    # ------------------------------------------------------------------

    def _mutate_placement(self, game: GameDefV2) -> None:
        """Randomly change placement target or constraint."""
        if self.rng.random() < 0.5:
            game.placement_rule.target = str(
                self.rng.choice(PLACEMENT_TARGETS)
            )
        else:
            game.placement_rule.constraint = str(
                self.rng.choice(PLACEMENT_CONSTRAINTS)
            )

    def _mutate_capture(self, game: GameDefV2) -> None:
        """Change capture_type and fix dependent parameters."""
        old_type = game.capture_rule.capture_type
        new_type = str(self.rng.choice(CAPTURE_TYPES))
        game.capture_rule.capture_type = new_type

        # If the new type is outnumber, set a random threshold
        if new_type == "outnumber":
            game.capture_rule.threshold = int(self.rng.integers(2, 4))  # [2, 3]

        # Cascade only works with custodian; demote if capture changed away
        if (
            old_type == "custodian"
            and game.propagation_rule.prop_type == "cascade"
            and new_type != "custodian"
        ):
            game.propagation_rule.prop_type = "none"

    def _mutate_propagation(self, game: GameDefV2) -> None:
        """Change propagation type and fix dependent parameters."""
        new_type = str(self.rng.choice(PROPAGATION_TYPES))

        # Cascade only works with custodian capture
        if new_type == "cascade" and game.capture_rule.capture_type != "custodian":
            new_type = "none"

        # Influence is vestigial unless win=threshold
        if new_type == "influence" and game.win_condition.condition_type != "threshold":
            new_type = "none"

        game.propagation_rule.prop_type = new_type

        if new_type == "influence":
            # Perturb radius: +-1, clamp to [1, axis_size]
            delta_r = int(self.rng.choice([-1, 1]))
            game.propagation_rule.radius = int(np.clip(
                game.propagation_rule.radius + delta_r,
                1,
                game.axis_size,
            ))

            # Perturb strength: gaussian noise with param_mutation_std * 2
            noise_s = float(
                self.rng.normal(0.0, self.config.param_mutation_std * 2)
            )
            game.propagation_rule.strength = float(
                game.propagation_rule.strength + noise_s
            )

            # Perturb decay: gaussian noise with param_mutation_std, clamp [0.1, 0.9]
            noise_d = float(
                self.rng.normal(0.0, self.config.param_mutation_std)
            )
            game.propagation_rule.decay = float(np.clip(
                game.propagation_rule.decay + noise_d,
                0.1,
                0.9,
            ))

    def _mutate_win_condition(self, game: GameDefV2) -> None:
        """Change win condition type and perturb parameters."""
        new_type = str(self.rng.choice(WIN_CONDITION_TYPES))

        # Connection needs axis_size >= 3
        if new_type == "connection" and game.axis_size < 3:
            # Pick another type that isn't connection
            alternatives = [t for t in WIN_CONDITION_TYPES if t != "connection"]
            new_type = str(self.rng.choice(alternatives))

        game.win_condition.condition_type = new_type

        # If switching away from threshold, demote vestigial influence
        if new_type != "threshold" and game.propagation_rule.prop_type == "influence":
            game.propagation_rule.prop_type = "none"

        # Connection-specific: set target_dimension per player (Hex-style)
        if new_type == "connection":
            dim_p1 = int(self.rng.integers(0, game.num_dimensions))
            remaining = [d for d in range(game.num_dimensions) if d != dim_p1]
            dim_p2 = int(self.rng.choice(remaining))
            game.win_condition.target_dimension = dim_p1
            game.win_condition.target_dimension_p2 = dim_p2

        # Perturb threshold depending on type
        noise_t = float(self.rng.normal(0.0, self.config.param_mutation_std))
        if new_type == "territory":
            game.win_condition.threshold = float(np.clip(
                game.win_condition.threshold + noise_t,
                0.2,
                0.8,
            ))
        elif new_type == "threshold":
            # Larger range for absolute threshold
            noise_t_big = float(
                self.rng.normal(0.0, self.config.param_mutation_std * 10)
            )
            # Floor: threshold must require multiple pieces to achieve.
            # A single piece radiates strength*(1+radius), so require 10x.
            strength = game.propagation_rule.strength
            radius = game.propagation_rule.radius
            min_threshold = 10.0 * strength * (1.0 + radius)
            # R17 parity-shift: perturb by ±0.5 × stone-contribution on
            # top of the Gaussian drift so fitness can't pull thresholds
            # back to P1's tempo-favored crossing position. See
            # generator_v2.py for the full rationale.
            stone_contribution = strength * (1.0 + radius)
            parity_shift = (
                float(self.rng.uniform(-0.5, 0.5)) * stone_contribution
            )
            game.win_condition.threshold = float(np.clip(
                game.win_condition.threshold + noise_t_big + parity_shift,
                min_threshold,
                max(50.0, min_threshold + 15.0),
            ))

        # Perturb max_turns: +/- 10-20%, clamp [10, 200]
        pct = float(self.rng.uniform(0.10, 0.20))
        if self.rng.random() < 0.5:
            pct = -pct
        new_max_turns = int(round(game.win_condition.max_turns * (1.0 + pct)))
        game.win_condition.max_turns = int(np.clip(new_max_turns, 10, 200))

    def _mutate_topology(self, game: GameDefV2) -> None:
        """Change number of dimensions and recompute axis_size."""
        if game.topology_type in EXPERIMENTAL_TOPOLOGIES:
            # Experimental topologies (sierpinski) have fixed dimension/axis
            # invariants — never mutate them away.
            return
        delta = int(self.rng.choice([-1, 1]))
        new_dims = int(np.clip(game.num_dimensions + delta, 2, _MAX_DIMENSIONS))
        new_axis = TopologicalSpace.compute_axis_size(new_dims, _MAX_TOTAL_CELLS)

        # Enforce minimum axis_size: 4 for 2D/3D, 3 for 4D+
        min_axis = 4 if new_dims <= 3 else 3
        new_axis = max(new_axis, min_axis)

        game.num_dimensions = new_dims
        game.axis_size = new_axis

        # Fix win condition for new topology
        if game.win_condition.condition_type == "connection":
            game.win_condition.target_dimension = min(
                game.win_condition.target_dimension, new_dims - 1
            )
            # Also fix P2 dimension
            dim_p2 = game.win_condition.target_dimension_p2
            if dim_p2 >= 0:
                dim_p2 = min(dim_p2, new_dims - 1)
                if dim_p2 == game.win_condition.target_dimension:
                    dim_p2 = (game.win_condition.target_dimension + 1) % new_dims
                game.win_condition.target_dimension_p2 = dim_p2
            if new_axis < 3:
                game.win_condition.condition_type = "territory"

    def _mutate_topology_type(self, game: GameDefV2) -> None:
        """Change topology type (grid, torus, hex, moore).

        Experimental topologies (sierpinski) are excluded from the mutation
        pool — they require explicit opt-in via hand-crafted seed games and
        have invariants (axis_size, dimensions) that mutation would break.
        Games already on an experimental topology stay there: we don't
        mutate INTO it, but we also don't mutate OUT of it via this op.
        """
        if game.topology_type in EXPERIMENTAL_TOPOLOGIES:
            return
        candidates = [t for t in TOPOLOGY_TYPES if t not in EXPERIMENTAL_TOPOLOGIES]
        new_topology = str(self.rng.choice(candidates))

        # Hex requires 2D; force dimensions if needed
        if new_topology == "hex" and game.num_dimensions != 2:
            game.num_dimensions = 2
            game.axis_size = TopologicalSpace.compute_axis_size(2, _MAX_TOTAL_CELLS)
            game.axis_size = max(game.axis_size, 4)

        # Custodian is incompatible with hex/moore
        if (
            game.capture_rule.capture_type == "custodian"
            and new_topology in ("hex", "moore")
        ):
            game.capture_rule.capture_type = "surround"

        game.topology_type = new_topology

    def _mutate_action_types(self, game: GameDefV2) -> None:
        """Toggle place/move action types and mutate move_constraint."""
        current = set(game.action_rule.action_types)

        # Randomly toggle each action type
        for at in ACTION_TYPES:
            if self.rng.random() < 0.4:
                if at in current:
                    current.discard(at)
                else:
                    current.add(at)

        # Ensure at least one remains
        if not current:
            current.add("place")

        game.action_rule.action_types = tuple(sorted(current))

        # Randomly mutate move_constraint
        if game.action_rule.has_move() and self.rng.random() < 0.5:
            game.action_rule.move_constraint = str(
                self.rng.choice(MOVE_CONSTRAINTS)
            )

    def _mutate_turn_structure(self, game: GameDefV2) -> None:
        """Change turn type and adjust pieces_per_turn."""
        new_type = str(self.rng.choice(TURN_TYPES))
        total_cells = game.axis_size ** game.num_dimensions

        if new_type == "multi_place" and total_cells >= 100:
            game.turn_structure.turn_type = new_type
            game.turn_structure.pieces_per_turn = int(self.rng.integers(2, 4))  # [2, 3]
        else:
            # Force alternating on small boards (< 100 cells)
            game.turn_structure.turn_type = "alternating"
            game.turn_structure.pieces_per_turn = 1

    def _mutate_ca_rule(self, game: GameDefV2) -> None:
        """Flip 1-3 random entries in the CA transition table.

        Biased toward identity to preserve the sparsity that makes CA
        rules playable.  Run 12 showed unbiased mutation gradually makes
        CA rules denser and more chaotic, destroying learnability.

        Each mutation is applied symmetrically: flipping (s, f, e) also
        flips its swap-mirror (see _generate_ca_rule for the invariant).
        Without this, mutation erodes player-swap symmetry over generations.
        """
        if game.ca_rule is None:
            return
        table = game.ca_rule.transition_table
        if not table:
            return
        keys = list(table.keys())
        # Fewer flips per mutation (1-3 instead of 1-5) for finer-grained search
        num_flips = int(self.rng.integers(1, min(4, len(keys) + 1)))
        flip_keys = self.rng.choice(len(keys), size=num_flips, replace=False)
        for idx in flip_keys:
            key = keys[int(idx)]
            state, f, e = key
            roll = float(self.rng.random())
            if roll < 0.35:
                new_value = state  # identity
            else:
                new_value = int(self.rng.integers(0, 3))
            table[key] = new_value
            # Apply the symmetric mirror so invariant is preserved.
            if state == 0:
                table[(0, e, f)] = new_value
            else:
                mirror_state = 3 - state  # 1 -> 2, 2 -> 1
                table[(mirror_state, e, f)] = _CA_SWAP[new_value]

    def _mutate_ca_steps(self, game: GameDefV2) -> None:
        """Change steps_per_turn by +-1 (clamp to 1-3)."""
        if game.ca_rule is None:
            return
        delta = int(self.rng.choice([-1, 1]))
        game.ca_rule.steps_per_turn = int(np.clip(
            game.ca_rule.steps_per_turn + delta, 1, 3
        ))


# ======================================================================
# CrossoverOperatorV2
# ======================================================================

class CrossoverOperatorV2:
    """Crossover operators for combining two V2/V3 games."""

    def __init__(
        self,
        config: EvolutionConfig,
        rng: np.random.Generator,
        audit_soft_rules: bool = False,
    ) -> None:
        self.config = config
        self.rng = rng
        self.audit_soft_rules = audit_soft_rules

    def crossover_games(
        self, game_a: GameDefV2, game_b: GameDefV2,
    ) -> GameDefV2:
        """Combine rule components from two parent games.

        Randomly selects one of three strategies:
          1. Component swap  -- topology from A, each rule from A or B.
          2. Blend topology  -- dimensions from one parent, rules mixed.
          3. Parameter blend -- types from A, parameters from B.

        Returns a new ``GameDefV2`` with both parents tracked in metadata.
        """
        strategy = int(self.rng.integers(0, 3))

        if strategy == 0:
            child, cross_type = self._component_swap(game_a, game_b)
        elif strategy == 1:
            child, cross_type = self._blend_topology(game_a, game_b)
        else:
            child, cross_type = self._parameter_blend(game_a, game_b)

        # Fix inconsistencies
        _fix_consistency(child, audit_soft_rules=self.audit_soft_rules)

        # Assign identity and parentage
        new_id = uuid.uuid4().hex[:12]
        generation = max(
            game_a.metadata.get("generation", 0),
            game_b.metadata.get("generation", 0),
        ) + 1

        child.game_id = new_id
        child.metadata = {
            "parents": [game_a.game_id, game_b.game_id],
            "generation": generation,
            "crossover_type": cross_type,
        }
        return child

    # ------------------------------------------------------------------
    # Strategy 1: Component swap
    # ------------------------------------------------------------------

    def _component_swap(
        self, game_a: GameDefV2, game_b: GameDefV2,
    ) -> tuple[GameDefV2, str]:
        """Topology from parent A; each rule randomly from A or B."""
        a = copy.deepcopy(game_a)
        b = copy.deepcopy(game_b)

        # CA crossover: if either parent has CA, child gets CA with 50% chance
        ca_rule = _crossover_ca_rules(a.ca_rule, b.ca_rule, self.rng)

        child = GameDefV2(
            game_id="",  # will be set later
            num_dimensions=a.num_dimensions,
            axis_size=a.axis_size,
            topology_type=(
                a.topology_type if self.rng.random() < 0.5
                else b.topology_type
            ),
            placement_rule=(
                a.placement_rule if self.rng.random() < 0.5
                else b.placement_rule
            ),
            capture_rule=(
                a.capture_rule if self.rng.random() < 0.5
                else b.capture_rule
            ),
            propagation_rule=(
                a.propagation_rule if self.rng.random() < 0.5
                else b.propagation_rule
            ),
            win_condition=(
                a.win_condition if self.rng.random() < 0.5
                else b.win_condition
            ),
            turn_structure=(
                a.turn_structure if self.rng.random() < 0.5
                else b.turn_structure
            ),
            action_rule=(
                a.action_rule if self.rng.random() < 0.5
                else b.action_rule
            ),
            ca_rule=ca_rule,
        )
        return child, "component_swap"

    # ------------------------------------------------------------------
    # Strategy 2: Blend topology
    # ------------------------------------------------------------------

    def _blend_topology(
        self, game_a: GameDefV2, game_b: GameDefV2,
    ) -> tuple[GameDefV2, str]:
        """num_dimensions from one parent; rules from both, mixed."""
        a = copy.deepcopy(game_a)
        b = copy.deepcopy(game_b)

        # Choose topology (dimensions + type) from one parent
        if self.rng.random() < 0.5:
            num_dims = a.num_dimensions
            topology_type = a.topology_type
        else:
            num_dims = b.num_dimensions
            topology_type = b.topology_type

        axis_size = TopologicalSpace.compute_axis_size(num_dims, _MAX_TOTAL_CELLS)

        # Pick action_rule from a random parent
        action_rule = a.action_rule if self.rng.random() < 0.5 else b.action_rule

        # CA crossover
        ca_rule = _crossover_ca_rules(a.ca_rule, b.ca_rule, self.rng)

        # Randomly decide which parent donates rules vs win_condition
        if self.rng.random() < 0.5:
            # Rules from A, win_condition from B
            child = GameDefV2(
                game_id="",
                num_dimensions=num_dims,
                axis_size=axis_size,
                topology_type=topology_type,
                placement_rule=a.placement_rule,
                capture_rule=a.capture_rule,
                propagation_rule=a.propagation_rule,
                win_condition=b.win_condition,
                turn_structure=a.turn_structure,
                action_rule=action_rule,
                ca_rule=ca_rule,
            )
        else:
            # Rules from B, win_condition from A
            child = GameDefV2(
                game_id="",
                num_dimensions=num_dims,
                axis_size=axis_size,
                topology_type=topology_type,
                placement_rule=b.placement_rule,
                capture_rule=b.capture_rule,
                propagation_rule=b.propagation_rule,
                win_condition=a.win_condition,
                turn_structure=b.turn_structure,
                action_rule=action_rule,
                ca_rule=ca_rule,
            )

        # Fix target_dimension for connection type
        if child.win_condition.condition_type == "connection":
            child.win_condition.target_dimension = min(
                child.win_condition.target_dimension, num_dims - 1,
            )

        return child, "blend_topology"

    # ------------------------------------------------------------------
    # Strategy 3: Parameter blend
    # ------------------------------------------------------------------

    def _parameter_blend(
        self, game_a: GameDefV2, game_b: GameDefV2,
    ) -> tuple[GameDefV2, str]:
        """Types from parent A, parameters from parent B."""
        a = copy.deepcopy(game_a)
        b = copy.deepcopy(game_b)

        # CA crossover
        ca_rule = _crossover_ca_rules(a.ca_rule, b.ca_rule, self.rng)

        # Topology from A
        child = GameDefV2(
            game_id="",
            num_dimensions=a.num_dimensions,
            axis_size=a.axis_size,
            topology_type=a.topology_type,
            # Placement: type from A, first_move_anywhere from B
            placement_rule=PlacementRule(
                target=a.placement_rule.target,
                constraint=a.placement_rule.constraint,
                first_move_anywhere=b.placement_rule.first_move_anywhere,
            ),
            # Capture: type from A, threshold from B
            capture_rule=CaptureRule(
                capture_type=a.capture_rule.capture_type,
                threshold=b.capture_rule.threshold,
            ),
            # Propagation: type from A, numeric params from B
            propagation_rule=PropagationRule(
                prop_type=a.propagation_rule.prop_type,
                radius=b.propagation_rule.radius,
                strength=b.propagation_rule.strength,
                decay=b.propagation_rule.decay,
            ),
            # Win condition: type from A, parameters from B
            win_condition=WinCondition(
                condition_type=a.win_condition.condition_type,
                threshold=b.win_condition.threshold,
                target_dimension=b.win_condition.target_dimension,
                max_turns=b.win_condition.max_turns,
            ),
            # Turn structure: type from A, pieces_per_turn from B
            turn_structure=TurnStructure(
                turn_type=a.turn_structure.turn_type,
                pieces_per_turn=b.turn_structure.pieces_per_turn,
            ),
            # Action rule: types from A, move_constraint from B
            action_rule=ActionRule(
                action_types=a.action_rule.action_types,
                move_constraint=b.action_rule.move_constraint,
            ),
            ca_rule=ca_rule,
        )
        return child, "parameter_blend"
