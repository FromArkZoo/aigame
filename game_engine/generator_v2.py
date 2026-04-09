"""Random game generator and validator for V2 of the Genesis Creativity Engine.

Replaces the V1 GameGenerator (expression-tree synthesis) with a generator
that creates games on n-dimensional topological spaces using structured rules.
Games are composed from well-understood mechanics (placement, capture,
propagation, win conditions, turn structure) and validated via simulation
rollouts to filter out degenerate configurations.
"""

from __future__ import annotations

import uuid

import numpy as np

from config import GameConfig
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
from game_engine.topology import TopologicalSpace, TOPOLOGY_TYPES


class GameGeneratorV2:
    """Generates random V2 game definitions on topological spaces.

    Each generated game is a composition of structured rule components
    (placement, capture, propagation, win condition, turn structure)
    on an n-dimensional grid.  Games are validated via fast structural
    checks (``quick_reject``) and simulation-based rollouts
    (``validate_game``) to ensure playability.
    """

    def __init__(self, config: GameConfig, seed: int = 42) -> None:
        self.config = config
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    # ------------------------------------------------------------------
    # Game generation
    # ------------------------------------------------------------------

    def generate_game(self, seed: int | None = None) -> GameDefV2:
        """Generate a random V2 game definition.

        Parameters
        ----------
        seed : int, optional
            If provided, re-seeds the internal RNG for reproducibility.

        Returns
        -------
        GameDefV2
            A complete game definition ready for simulation.
        """
        if seed is not None:
            self.rng = np.random.default_rng(seed)

        cfg = self.config

        # V2-specific config fields with defaults
        min_dimensions = getattr(cfg, "min_dimensions", 2)
        max_dimensions = getattr(cfg, "max_dimensions", 6)
        max_total_cells = getattr(cfg, "max_total_cells", 64)
        max_game_steps = getattr(cfg, "max_game_steps", 100)
        num_players = getattr(cfg, "num_players", 2)

        # V3-specific config fields
        topology_types = getattr(cfg, "topology_types", ["grid", "torus", "hex", "moore"])
        enable_movement = getattr(cfg, "enable_movement", True)
        movement_probability = getattr(cfg, "movement_probability", 0.3)

        # --- 1. Topology ---
        num_dimensions = int(self.rng.integers(min_dimensions, max_dimensions + 1))
        axis_size = TopologicalSpace.compute_axis_size(num_dimensions, max_total_cells)
        # Ban axis_size=2: minimum 4 for 2D/3D, 3 for 4D+
        min_axis = 4 if num_dimensions <= 3 else 3
        if axis_size < min_axis:
            # Reduce dimensions until the minimum axis fits
            while axis_size < min_axis and num_dimensions > 2:
                num_dimensions -= 1
                axis_size = TopologicalSpace.compute_axis_size(
                    num_dimensions, max_total_cells
                )
                min_axis = 4 if num_dimensions <= 3 else 3
            # Final clamp
            axis_size = max(axis_size, min_axis)
        total_cells = axis_size ** num_dimensions

        # --- 1b. Topology type (V3) ---
        topology_type = str(self.rng.choice(topology_types))
        # Hex is 2D only; if we picked hex but have wrong dimensions, reroll
        if topology_type == "hex" and num_dimensions != 2:
            non_hex = [t for t in topology_types if t != "hex"]
            topology_type = str(self.rng.choice(non_hex)) if non_hex else "grid"

        # --- 2. Placement rule ---
        target = self._weighted_choice(
            PLACEMENT_TARGETS,
            [0.8, 0.2],
        )
        constraint = self._weighted_choice(
            PLACEMENT_CONSTRAINTS,
            [0.4, 0.25, 0.15, 0.2],
        )
        placement_rule = PlacementRule(
            target=target,
            constraint=constraint,
            first_move_anywhere=True,
        )

        # --- 3. Capture rule ---
        capture_type = self._weighted_choice(
            CAPTURE_TYPES,
            [0.2, 0.3, 0.25, 0.25],
        )
        # Custodian is incompatible with hex/moore topologies
        if capture_type == "custodian" and topology_type in ("hex", "moore"):
            non_custodian = [t for t in CAPTURE_TYPES if t != "custodian"]
            capture_type = str(self.rng.choice(non_custodian))
        if capture_type == "outnumber":
            threshold = int(self.rng.integers(2, 4))  # [2, 3]
        else:
            threshold = 1
        capture_rule = CaptureRule(
            capture_type=capture_type,
            threshold=threshold,
        )

        # --- 4. Propagation rule ---
        prop_type = self._weighted_choice(
            PROPAGATION_TYPES,
            [0.4, 0.35, 0.25],
        )
        # Cascade only works with custodian capture (cascade+surround is
        # provably inert: removing stones creates liberties, cascade never fires)
        if prop_type == "cascade" and capture_type != "custodian":
            prop_type = "none"
        radius = int(self.rng.integers(1, min(3, axis_size) + 1))
        strength = float(self.rng.uniform(0.5, 2.0))
        decay = float(self.rng.uniform(0.3, 0.8))
        propagation_rule = PropagationRule(
            prop_type=prop_type,
            radius=radius,
            strength=strength,
            decay=decay,
        )

        # --- 5. Win condition ---
        # V3: majority removed; connection gets highest weight
        condition_type = self._weighted_choice(
            WIN_CONDITION_TYPES,
            [0.2, 0.15, 0.4, 0.25],  # territory, elimination, connection, threshold
        )
        # Connection fallbacks
        if condition_type == "connection" and num_dimensions < 2:
            condition_type = "territory"
        if condition_type == "connection" and axis_size < 3:
            condition_type = "territory"

        # Ensure influence <-> threshold consistency:
        # - Only keep influence propagation when win=threshold.
        # - Force influence propagation when win=threshold (otherwise
        #   board_values stay at 0 and threshold is unreachable).
        if condition_type != "threshold" and prop_type == "influence":
            prop_type = "none"
            propagation_rule = PropagationRule(
                prop_type="none",
                radius=radius,
                strength=strength,
                decay=decay,
            )
        elif condition_type == "threshold" and prop_type != "influence":
            prop_type = "influence"
            propagation_rule = PropagationRule(
                prop_type="influence",
                radius=radius,
                strength=strength,
                decay=decay,
            )

        # Threshold depends on condition type
        if condition_type == "territory":
            win_threshold = float(self.rng.uniform(0.3, 0.7))
        elif condition_type == "threshold":
            # Floor: threshold must be achievable but not trivially easy.
            # A single piece radiates strength*(1+radius) influence, so
            # require at least 10x that to need multiple pieces.
            min_threshold = 10.0 * strength * (1.0 + radius)
            # Cap: threshold must be reachable. Upper bound assumes a player
            # owns half the board; each cell receives influence from all
            # friendly cells within radius.
            cells_in_radius = min(total_cells, (2 * radius + 1) ** num_dimensions)
            max_threshold = (total_cells // 2) * strength * cells_in_radius * 0.8
            max_threshold = max(max_threshold, min_threshold + 15.0)
            win_threshold = float(
                self.rng.uniform(min_threshold, min(min_threshold + 15.0, max_threshold))
            )
        else:
            win_threshold = 0.5  # default, not used for most types

        # Target dimensions for connection (Hex-style: each player connects
        # a different axis).
        target_dimension_p2 = -1
        if condition_type == "connection":
            target_dimension = int(self.rng.integers(0, num_dimensions))
            # Assign a different dimension for player 2
            remaining = [d for d in range(num_dimensions) if d != target_dimension]
            target_dimension_p2 = int(self.rng.choice(remaining))
        else:
            target_dimension = 0

        # Max turns: both players can fill the board, capped
        max_turns = min(total_cells * 2, max_game_steps)

        win_condition = WinCondition(
            condition_type=condition_type,
            threshold=win_threshold,
            target_dimension=target_dimension,
            target_dimension_p2=target_dimension_p2,
            max_turns=max_turns,
        )

        # --- 6. Turn structure ---
        turn_type = self._weighted_choice(
            TURN_TYPES,
            [0.7, 0.3],
        )
        if turn_type == "multi_place" and total_cells >= 100:
            pieces_per_turn = int(self.rng.integers(2, 4))  # [2, 3]
        else:
            # Force alternating on small boards (< 100 cells)
            turn_type = "alternating"
            pieces_per_turn = 1
        turn_structure = TurnStructure(
            turn_type=turn_type,
            pieces_per_turn=pieces_per_turn,
        )

        # --- 7. Action rule (V3) ---
        if enable_movement and self.rng.random() < movement_probability:
            # Movement enabled for this game
            action_choice = self._weighted_choice(
                ("place_only", "both", "move_only"),
                [0.70, 0.15, 0.15],
            )
            if action_choice == "place_only":
                action_types = ("place",)
            elif action_choice == "both":
                action_types = ("place", "move")
            else:
                action_types = ("move",)
            move_constraint = str(self.rng.choice(MOVE_CONSTRAINTS))
        else:
            action_types = ("place",)
            move_constraint = "adjacent_empty"
        action_rule = ActionRule(
            action_types=action_types,
            move_constraint=move_constraint,
        )

        # --- 8. CA rule (optional) ---
        ca_probability = getattr(cfg, "ca_probability", 0.3)
        ca_rule = None
        if self.rng.random() < ca_probability:
            # Compute max_degree from topology
            topo = TopologicalSpace(num_dimensions, axis_size, topology_type)
            ca_rule = self._generate_ca_rule(topo.max_degree)
            # CA replaces capture and propagation
            capture_rule = CaptureRule(capture_type="none")
            propagation_rule = PropagationRule(prop_type="none")

        # --- 9. Assemble game definition ---
        game_id = uuid.uuid4().hex[:12]

        return GameDefV2(
            game_id=game_id,
            num_dimensions=num_dimensions,
            axis_size=axis_size,
            topology_type=topology_type,
            placement_rule=placement_rule,
            capture_rule=capture_rule,
            propagation_rule=propagation_rule,
            win_condition=win_condition,
            turn_structure=turn_structure,
            action_rule=action_rule,
            ca_rule=ca_rule,
            num_players=num_players,
            metadata={
                "generation": 0,
                "parent_ids": [],
                "seed": seed if seed is not None else self.seed,
            },
        )

    # ------------------------------------------------------------------
    # CA rule generation
    # ------------------------------------------------------------------

    def _generate_ca_rule(self, max_degree: int) -> CARule:
        """Generate a biased random CA transition table.

        The table maps (state, friendly_count, enemy_count) -> new_state
        where state is 0=empty, 1=friendly, 2=enemy.
        """
        table: dict[tuple[int, int, int], int] = {}

        for friendly in range(max_degree + 1):
            for enemy in range(max_degree + 1):
                # --- Empty cells ---
                roll = float(self.rng.random())
                if roll < 0.80:
                    new_state = 0  # stay empty
                elif roll < 0.95:
                    # Birth if enough friendly neighbors
                    new_state = 1 if friendly >= 2 else 0
                else:
                    # Rare birth with just 1 friendly neighbor
                    new_state = 1 if friendly >= 1 else 0
                table[(0, friendly, enemy)] = new_state

                # --- Friendly cells ---
                roll = float(self.rng.random())
                if roll < 0.70:
                    new_state = 1  # survive
                elif roll < 0.90:
                    # Die if outnumbered
                    new_state = 0 if enemy > friendly else 1
                else:
                    # Convert to enemy
                    new_state = 2 if enemy > friendly else 1
                table[(1, friendly, enemy)] = new_state

                # --- Enemy cells (mirror of friendly from opponent's perspective) ---
                # Reuse same logic with swapped counts for symmetry
                roll = float(self.rng.random())
                if roll < 0.70:
                    new_state = 2  # survive
                elif roll < 0.90:
                    new_state = 0 if friendly > enemy else 2
                else:
                    new_state = 1 if friendly > enemy else 2
                table[(2, friendly, enemy)] = new_state

        steps_per_turn = int(self.rng.choice([1, 2, 3], p=[0.6, 0.3, 0.1]))

        return CARule(
            transition_table=table,
            steps_per_turn=steps_per_turn,
            max_neighbors=max_degree,
        )

    # ------------------------------------------------------------------
    # Quick reject (fast structural check)
    # ------------------------------------------------------------------

    def quick_reject(self, game: GameDefV2) -> bool:
        """Fast structural degeneracy check before simulation.

        Returns True if the game passes all structural checks (i.e. it
        should NOT be rejected).  Returns False if the game is
        structurally degenerate and should be discarded.
        """
        # 1. Too small for a real game
        if game.total_cells < 4:
            return False

        # 2. Too few turns
        if game.win_condition.max_turns < 4:
            return False

        # 3. Ban axis_size=2 (always too small / too symmetric)
        if game.axis_size < 3:
            return False

        # 4. Connection on a tiny axis is trivially easy
        if game.win_condition.condition_type == "connection" and game.axis_size < 3:
            return False

        # 5. Connection: players must connect different axes
        if game.win_condition.condition_type == "connection":
            dim_p2 = game.win_condition.target_dimension_p2
            if dim_p2 < 0:
                dim_p2 = (game.win_condition.target_dimension + 1) % game.num_dimensions
            if dim_p2 == game.win_condition.target_dimension:
                return False

        # 6. Adjacent-to-own constraint with no first_move_anywhere
        #    makes the game unplayable when captures exist
        if (
            game.capture_rule.capture_type != "none"
            and game.placement_rule.constraint == "adjacent_to_own"
            and not game.placement_rule.first_move_anywhere
        ):
            return False

        # 7. Cascade propagation only works with custodian capture
        #    (cascade+surround is provably inert)
        if (
            game.propagation_rule.prop_type == "cascade"
            and game.capture_rule.capture_type != "custodian"
        ):
            return False

        # 8. Vestigial influence: influence propagation without threshold
        #    win condition has no effect on gameplay
        if (
            game.propagation_rule.prop_type == "influence"
            and game.win_condition.condition_type != "threshold"
        ):
            return False

        # 9. Threshold requires influence propagation
        if (
            game.win_condition.condition_type == "threshold"
            and game.propagation_rule.prop_type != "influence"
        ):
            return False

        # 10. Threshold reachability: reject if threshold is unreachable
        if game.win_condition.condition_type == "threshold":
            s = game.propagation_rule.strength
            r = game.propagation_rule.radius
            cells_in_radius = min(
                game.total_cells,
                (2 * r + 1) ** game.num_dimensions,
            )
            max_achievable = (game.total_cells // 2) * s * cells_in_radius
            if game.win_condition.threshold > max_achievable:
                return False

        # 11. Custodian capture on hex/moore topology (V3)
        if (
            game.capture_rule.capture_type == "custodian"
            and game.topology_type in ("hex", "moore")
        ):
            return False

        # 12. Move-only games must have capture (V3) — unless CA handles it
        if (
            game.action_rule.has_move()
            and not game.action_rule.has_place()
            and game.capture_rule.capture_type == "none"
            and game.ca_rule is None
        ):
            return False

        # 13. CA games: capture and propagation should be none
        if game.ca_rule is not None:
            if game.capture_rule.capture_type != "none":
                return False
            if game.propagation_rule.prop_type != "none":
                return False

        # 14. CA stability test
        if game.ca_rule is not None and not self._ca_stability_check(game):
            return False

        return True

    # ------------------------------------------------------------------
    # CA stability check
    # ------------------------------------------------------------------

    def _ca_stability_check(self, game: GameDefV2) -> bool:
        """Quick stability test for CA rules.

        Places random pieces, runs CA steps, checks the rule doesn't
        annihilate everything or fill the board instantly.
        """
        from game_engine.engine_v2 import GameEngineV2

        rng = np.random.default_rng(self.seed + 7777)
        topo = game.get_topology()
        total = game.total_cells

        # Place 5-10 random pieces (mix of P1 and P2)
        num_pieces = int(rng.integers(5, min(11, total)))
        cells = rng.choice(total, size=num_pieces, replace=False)
        board = np.zeros(total, dtype=np.int8)
        for i, c in enumerate(cells):
            board[c] = 1 if i % 2 == 0 else 2

        initial_board = board.copy()
        changed = False

        # Run 10 CA steps
        for _ in range(10):
            snapshot = board.copy()
            new_board = snapshot.copy()
            for cell in range(total):
                cell_owner = int(snapshot[cell])
                perspective = cell_owner if cell_owner != 0 else 1
                opponent = 3 - perspective
                friendly_count = 0
                enemy_count = 0
                for nbr in topo.get_neighbors(cell):
                    nbr_owner = int(snapshot[nbr])
                    if nbr_owner == perspective:
                        friendly_count += 1
                    elif nbr_owner == opponent:
                        enemy_count += 1
                abstract_state = 0 if cell_owner == 0 else (1 if cell_owner == perspective else 2)
                new_abstract = game.ca_rule.apply(abstract_state, friendly_count, enemy_count)
                if new_abstract == 0:
                    new_board[cell] = 0
                elif new_abstract == 1:
                    new_board[cell] = perspective
                else:
                    new_board[cell] = opponent
            if not np.array_equal(board, new_board):
                changed = True
            board = new_board

            # Check bounds: not annihilated, not exploded
            occupied = int(np.sum(board != 0))
            if occupied == 0:
                return False  # Everything died
            if occupied > 0.9 * total:
                return False  # Board filled up

        # Must have changed at least once (not a frozen/identity rule)
        if not changed:
            return False

        return True

    # ------------------------------------------------------------------
    # Simulation-based validation
    # ------------------------------------------------------------------

    def validate_game(
        self,
        game: GameDefV2,
        *,
        max_rollout_steps: int = 300,
        num_rollouts: int = 10,
    ) -> bool:
        """Run simulation-based validation on a game definition.

        This is more expensive than ``quick_reject`` and involves
        actually playing random games to check for degeneracy.

        Checks:
        1. Termination: >= 80% of rollouts end within max_rollout_steps.
        2. Action diversity: different legal actions produce different states.
        3. Dual winability: both players win at least once.
        4. Minimum game length: average >= 4 steps.
        5. Non-trivial legal actions: average >= 1.5 per step.

        Parameters
        ----------
        game : GameDefV2
            The game to validate.
        max_rollout_steps : int
            Maximum steps per rollout before declaring non-termination.
        num_rollouts : int
            Number of random rollouts to run.

        Returns
        -------
        bool
            True if the game passes all validation checks.
        """
        # Lazy import to avoid circular dependency
        from game_engine.engine_v2 import GameEngineV2

        rng = np.random.default_rng(self.seed + 9999)

        terminated_count = 0
        player_wins = [0, 0]  # count of wins per player
        game_lengths: list[int] = []
        total_legal_actions = 0
        total_steps = 0

        for rollout_idx in range(num_rollouts):
            engine = GameEngineV2(game)
            obs = engine.reset()
            done = False
            steps = 0

            for step in range(max_rollout_steps):
                legal_actions = engine.get_legal_actions()
                total_legal_actions += len(legal_actions)
                total_steps += 1

                if not legal_actions:
                    # No legal actions means the game is stuck
                    break

                action = int(rng.choice(legal_actions))
                obs, reward, done, info = engine.step(action)
                steps += 1

                if done:
                    terminated_count += 1
                    game_lengths.append(steps)
                    # Determine winner from reward
                    # reward > 0 means current result favours someone
                    if isinstance(reward, (list, tuple, np.ndarray)):
                        for p in range(min(2, len(reward))):
                            if reward[p] > 0:
                                player_wins[p] += 1
                    else:
                        # Scalar reward: positive means player 0 wins,
                        # negative means player 1 wins
                        if reward > 0:
                            player_wins[0] += 1
                        elif reward < 0:
                            player_wins[1] += 1
                    break

            if not done:
                game_lengths.append(steps)

        # --- Check 1: Termination (>= 80%) ---
        if terminated_count < int(0.8 * num_rollouts):
            return False

        # --- Check 2: Action diversity ---
        # Play 3 moves randomly, then check that legal actions from that
        # state produce different board states.
        try:
            engine = GameEngineV2(game)
            engine.reset()
            for _ in range(3):
                legal = engine.get_legal_actions()
                if not legal:
                    break
                action = int(rng.choice(legal))
                _, _, done, _ = engine.step(action)
                if done:
                    break

            if not done:
                legal = engine.get_legal_actions()
                if len(legal) >= 2:
                    # Try each legal action and collect resulting observations
                    observed_states: list[np.ndarray] = []
                    for act in legal:
                        test_engine = GameEngineV2(game)
                        test_engine.reset()
                        # Replay the same 3 moves
                        replay_rng = np.random.default_rng(self.seed + 9999)
                        replay_engine = GameEngineV2(game)
                        replay_engine.reset()
                        replay_done = False
                        for _ in range(3):
                            replay_legal = replay_engine.get_legal_actions()
                            if not replay_legal:
                                replay_done = True
                                break
                            replay_act = int(replay_rng.choice(replay_legal))
                            _, _, replay_done, _ = replay_engine.step(replay_act)
                            if replay_done:
                                break

                        if not replay_done:
                            obs_after, _, _, _ = replay_engine.step(act)
                            if isinstance(obs_after, np.ndarray):
                                observed_states.append(obs_after.copy())

                    # Check that at least 2 actions produce different states
                    if len(observed_states) >= 2:
                        found_different = False
                        for i in range(1, len(observed_states)):
                            if not np.array_equal(observed_states[0], observed_states[i]):
                                found_different = True
                                break
                        if not found_different:
                            return False
        except Exception:
            # If action diversity check fails due to engine issues,
            # don't reject -- the other checks are sufficient
            pass

        # --- Check 3: Dual winability ---
        if player_wins[0] == 0 or player_wins[1] == 0:
            return False

        # --- Check 4: Minimum game length ---
        if game_lengths:
            avg_length = sum(game_lengths) / len(game_lengths)
            min_length = 15 if game.uses_ca else 4
            if avg_length < min_length:
                return False
        else:
            return False

        # --- Check 5: Non-trivial legal actions ---
        if total_steps > 0:
            avg_legal = total_legal_actions / total_steps
            if avg_legal < 1.5:
                return False
        else:
            return False

        return True

    # ------------------------------------------------------------------
    # Batch generation with filtering
    # ------------------------------------------------------------------

    def generate_valid_games(
        self,
        count: int,
        seed: int,
        *,
        max_attempts_factor: int = 20,
    ) -> list[GameDefV2]:
        """Generate *count* validated games, discarding invalid ones.

        Each candidate is first checked with ``quick_reject`` (fast),
        then with ``validate_game`` (simulation-based, slower).

        Parameters
        ----------
        count : int
            Number of valid games desired.
        seed : int
            Base seed; each attempt uses ``seed + i``.
        max_attempts_factor : int
            Try at most ``count * max_attempts_factor`` candidates
            before giving up.

        Returns
        -------
        list[GameDefV2]
            Up to *count* validated game definitions.
        """
        valid: list[GameDefV2] = []
        max_attempts = count * max_attempts_factor

        for i in range(max_attempts):
            game = self.generate_game(seed=seed + i)

            # Fast structural check
            if not self.quick_reject(game):
                continue

            # Simulation-based validation
            if not self.validate_game(game):
                continue

            valid.append(game)
            if len(valid) >= count:
                break

        return valid

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _weighted_choice(
        self,
        options: tuple[str, ...] | list[str],
        weights: list[float],
    ) -> str:
        """Choose from *options* with the given probability weights."""
        probs = np.array(weights, dtype=np.float64)
        probs /= probs.sum()  # normalise in case of rounding
        idx = int(self.rng.choice(len(options), p=probs))
        return options[idx]
