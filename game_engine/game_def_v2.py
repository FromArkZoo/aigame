"""V2/V3 game definition using topological spaces and structured rules.

Replaces the expression-tree-based GameDef with a constrained
representation built from compositions of known game mechanics.
Provides the same public interface expected by the training,
metrics, and evolution infrastructure.

V3 additions:
  - topology_type: grid, torus, hex, moore
  - action_rule: ActionRule defining available action types (place, move)
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from game_engine.rules import (
    ActionRule,
    CARule,
    CaptureRule,
    PlacementRule,
    PropagationRule,
    TurnStructure,
    WinCondition,
)
from game_engine.topology import TopologicalSpace


@dataclass
class GameDefV2:
    """Complete definition of a V2/V3 generated game.

    A game is played on an n-dimensional topological grid.  Rules are
    structured components (placement, capture, propagation, win condition,
    turn structure, action types) rather than arbitrary expression trees.
    """

    game_id: str
    num_dimensions: int
    axis_size: int

    placement_rule: PlacementRule
    capture_rule: CaptureRule
    propagation_rule: PropagationRule
    win_condition: WinCondition
    turn_structure: TurnStructure

    # V3 fields
    topology_type: str = "grid"
    action_rule: ActionRule = field(default_factory=ActionRule)

    # V4 fields
    ca_rule: CARule | None = None

    # V5 fields (R20+): pie rule for knowledge-asymmetric balance.
    # When True, P2's first action may choose pie_swap (flip stone colours
    # and turn). See engine_v2.GameEngineV2._handle_pie_swap and R20_plan.md.
    pie_rule: bool = False

    num_players: int = 2
    metadata: dict = field(default_factory=dict)

    # Explicit hole-set for topology_type=="holes". List for JSON friendliness;
    # passed to TopologicalSpace as `holes`. None for non-holes topologies.
    holes: list[int] | None = None

    # ------------------------------------------------------------------
    # Derived properties (interface-compatible with V1 GameDef)
    # ------------------------------------------------------------------

    @property
    def total_cells(self) -> int:
        return self.axis_size ** self.num_dimensions

    @property
    def state_dim(self) -> int:
        """Observation vector length for the policy network.

        Per cell: owner_encoded (1 float) + value (1 float).
        Plus metadata: normalised turn number, own piece fraction,
        enemy piece fraction.
        """
        return self.total_cells * 2 + 3

    @property
    def num_actions(self) -> int:
        """Action space size.

        Layout:
          - Place actions: 0 .. total_cells-1  (if place enabled)
          - Pass action: total_cells
          - Move actions: total_cells+1 .. total_cells+total_cells*max_degree
            (if move enabled, encoded as from_cell * max_degree + neighbor_idx)
          - Pie swap action: trailing index (if pie_rule enabled)
        """
        n = self.total_cells + 1  # place actions + pass
        if self.action_rule.has_move():
            topo = self.get_topology()
            n += self.total_cells * topo.max_degree
        if self.pie_rule:
            n += 1  # pie_swap action
        return n

    @property
    def swap_action_idx(self) -> int:
        """Action index of the pie_swap action.

        Only meaningful when pie_rule is True. Always the trailing index in
        num_actions so its position is unambiguous regardless of whether
        move actions are enabled.
        """
        if not self.pie_rule:
            raise ValueError("pie_rule not enabled on this game")
        return self.num_actions - 1

    @property
    def max_game_steps(self) -> int:
        return self.win_condition.max_turns

    @property
    def observation_type(self) -> str:
        """V2/V3 always uses full observation (board is visible to both)."""
        return "full"

    @property
    def needs_ko_rule(self) -> bool:
        """Return True if this game has mechanics that can cause position repetition."""
        if self.ca_rule is not None:
            return True
        if self.placement_rule.target in ("any", "occupied"):
            return True
        if self.capture_rule.capture_type != "none":
            return True
        if self.action_rule.has_move():
            return True
        return False

    @property
    def uses_ca(self) -> bool:
        """Return True if this game uses a cellular automaton rule."""
        return self.ca_rule is not None

    # ------------------------------------------------------------------
    # Complexity
    # ------------------------------------------------------------------

    def total_complexity(self) -> int:
        """Total number of meaningful rule parameters.

        Used by the Go Essence simplicity metric.
        """
        c = 2  # num_dimensions + axis_size
        c += 1  # topology_type
        c += self.placement_rule.complexity()
        if self.ca_rule is not None:
            c += self.ca_rule.complexity()
        else:
            c += self.capture_rule.complexity()
            c += self.propagation_rule.complexity()
        c += self.win_condition.complexity()
        c += self.turn_structure.complexity()
        c += self.action_rule.complexity()
        if self.pie_rule:
            c += 1
        return c

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        # Version bump: 5 if pie_rule, else 4 if ca_rule, else 3.
        if self.pie_rule:
            version = 5
        elif self.ca_rule is not None:
            version = 4
        else:
            version = 3
        d = {
            "version": version,
            "game_id": self.game_id,
            "num_dimensions": self.num_dimensions,
            "axis_size": self.axis_size,
            "topology_type": self.topology_type,
            "placement_rule": self.placement_rule.to_dict(),
            "capture_rule": self.capture_rule.to_dict(),
            "propagation_rule": self.propagation_rule.to_dict(),
            "win_condition": self.win_condition.to_dict(),
            "turn_structure": self.turn_structure.to_dict(),
            "action_rule": self.action_rule.to_dict(),
            "num_players": self.num_players,
            "metadata": self.metadata,
        }
        if self.ca_rule is not None:
            d["ca_rule"] = self.ca_rule.to_dict()
        if self.holes is not None:
            d["holes"] = list(self.holes)
        if self.pie_rule:
            d["pie_rule"] = True
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> GameDefV2:
        # Handle V2 dicts that lack V3 fields
        action_rule_dict = d.get("action_rule")
        if action_rule_dict:
            action_rule = ActionRule.from_dict(action_rule_dict)
        else:
            action_rule = ActionRule()  # default: place only

        # Handle V4 CA rule
        ca_rule_dict = d.get("ca_rule")
        ca_rule = CARule.from_dict(ca_rule_dict) if ca_rule_dict else None

        holes_field = d.get("holes")
        return cls(
            game_id=d["game_id"],
            num_dimensions=d["num_dimensions"],
            axis_size=d["axis_size"],
            topology_type=d.get("topology_type", "grid"),
            placement_rule=PlacementRule.from_dict(d["placement_rule"]),
            capture_rule=CaptureRule.from_dict(d["capture_rule"]),
            propagation_rule=PropagationRule.from_dict(d["propagation_rule"]),
            win_condition=WinCondition.from_dict(d["win_condition"]),
            turn_structure=TurnStructure.from_dict(d["turn_structure"]),
            action_rule=action_rule,
            ca_rule=ca_rule,
            pie_rule=bool(d.get("pie_rule", False)),
            num_players=d.get("num_players", 2),
            metadata=d.get("metadata", {}),
            holes=list(holes_field) if holes_field is not None else None,
        )

    # ------------------------------------------------------------------
    # Copy
    # ------------------------------------------------------------------

    def copy(self) -> GameDefV2:
        return copy.deepcopy(self)

    # ------------------------------------------------------------------
    # Topology helper (lazy, not serialised)
    # ------------------------------------------------------------------

    _topology: TopologicalSpace | None = field(
        default=None, init=False, repr=False, compare=False,
    )

    def get_topology(self) -> TopologicalSpace:
        """Return (and cache) the TopologicalSpace for this game."""
        if self._topology is None or (
            self._topology.num_dimensions != self.num_dimensions
            or self._topology.axis_size != self.axis_size
            or self._topology.topology_type != self.topology_type
        ):
            self._topology = TopologicalSpace(
                self.num_dimensions,
                self.axis_size,
                self.topology_type,
                holes=self.holes,
            )
        return self._topology

    # ------------------------------------------------------------------
    # Action decoding helpers
    # ------------------------------------------------------------------

    def decode_action(self, action: int) -> dict[str, Any]:
        """Decode an action index into a structured description.

        Returns a dict with 'type' key:
          - {'type': 'place', 'cell': int}
          - {'type': 'pass'}
          - {'type': 'move', 'from_cell': int, 'to_cell': int}
          - {'type': 'pie_swap'} (if pie_rule enabled and action is the
            trailing swap index)
        """
        if self.pie_rule and action == self.swap_action_idx:
            return {"type": "pie_swap"}
        if action < self.total_cells:
            topo = self.get_topology()
            if not topo.active_mask[action]:
                raise ValueError(
                    f"action {action} decodes to hole cell {action} on "
                    f"topology {self.topology_type!r}"
                )
            return {"type": "place", "cell": action}
        if action == self.total_cells:
            return {"type": "pass"}
        # Move action
        move_idx = action - self.total_cells - 1
        topo = self.get_topology()
        from_cell = move_idx // topo.max_degree
        nbr_idx = move_idx % topo.max_degree
        neighbors = topo.get_neighbors(from_cell)
        if nbr_idx < len(neighbors):
            to_cell = neighbors[nbr_idx]
        else:
            to_cell = -1  # invalid (will be masked as illegal)
        return {"type": "move", "from_cell": from_cell, "to_cell": to_cell}

    def encode_move_action(self, from_cell: int, nbr_idx: int) -> int:
        """Encode a move action as an action index."""
        topo = self.get_topology()
        return self.total_cells + 1 + from_cell * topo.max_degree + nbr_idx
