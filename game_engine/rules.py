"""Structured rule components for V2/V3 games.

Instead of arbitrary expression trees, games are built from
compositions of well-understood game mechanics.  Each rule component
is a small dataclass with a type selector and a handful of parameters.
This makes the search space much more constrained while still allowing
a rich variety of games.

V3 additions:
  - ActionRule: defines which action types are available (place, move)
  - Movement support: pieces can relocate, not just appear

All rule types are designed to be serialisable (to_dict / from_dict)
and deep-copyable.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any


# ======================================================================
# Placement — where can a player place a piece?
# ======================================================================

PLACEMENT_TARGETS = ("empty", "any")
PLACEMENT_CONSTRAINTS = (
    "anywhere",
    "adjacent_to_own",
    "adjacent_to_enemy",
    "adjacent_to_any",
)


@dataclass
class PlacementRule:
    """Defines legal placement locations.

    Attributes:
        target: Which cells can be targeted.
            - ``"empty"``: only unoccupied cells.
            - ``"any"``: any cell (allows overwriting).
        constraint: Spatial constraint relative to existing pieces.
            - ``"anywhere"``: no constraint.
            - ``"adjacent_to_own"``: must be adjacent to a friendly piece.
            - ``"adjacent_to_enemy"``: must be adjacent to an enemy piece.
            - ``"adjacent_to_any"``: must be adjacent to any occupied cell.
        first_move_anywhere: If True the constraint is waived when the
            player has no pieces on the board yet.
    """

    target: str = "empty"
    constraint: str = "anywhere"
    first_move_anywhere: bool = True

    def complexity(self) -> int:
        score = 2  # target + constraint
        if self.first_move_anywhere:
            score += 1
        return score

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "constraint": self.constraint,
            "first_move_anywhere": self.first_move_anywhere,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> PlacementRule:
        return cls(
            target=d["target"],
            constraint=d["constraint"],
            first_move_anywhere=d.get("first_move_anywhere", True),
        )


# ======================================================================
# Capture — what happens to enemy pieces after placement?
# ======================================================================

CAPTURE_TYPES = ("none", "surround", "custodian", "outnumber")


@dataclass
class CaptureRule:
    """Defines how enemy pieces are captured.

    Attributes:
        capture_type: The capture mechanic.
            - ``"none"``: no captures.
            - ``"surround"``: Go-style; groups with no liberties are removed.
            - ``"custodian"``: Othello-style; lines of enemies bracketed by
              friendly pieces are flipped.
            - ``"outnumber"``: each adjacent enemy cell with fewer friendly
              neighbours than *threshold* is captured.
        threshold: Parameter for ``"outnumber"`` (minimum friendly
            neighbour advantage required to capture).
    """

    capture_type: str = "none"
    threshold: int = 1

    def complexity(self) -> int:
        if self.capture_type == "none":
            return 1
        if self.capture_type == "outnumber":
            return 3  # type + comparison + threshold
        return 2  # type + mechanic

    def to_dict(self) -> dict[str, Any]:
        return {"capture_type": self.capture_type, "threshold": self.threshold}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> CaptureRule:
        return cls(capture_type=d["capture_type"], threshold=d.get("threshold", 1))


# ======================================================================
# Propagation — how do effects spread after placement?
# ======================================================================

PROPAGATION_TYPES = ("none", "influence", "cascade")


@dataclass
class PropagationRule:
    """Defines how effects propagate across the board.

    Attributes:
        prop_type: The propagation mechanic.
            - ``"none"``: no propagation.
            - ``"influence"``: each piece exerts influence on nearby cells.
              ``board_values`` for cells within *radius* are updated.
            - ``"cascade"``: captures can chain — after a capture, newly
              exposed groups are re-checked for capture.
        radius: For ``"influence"``, how far the effect reaches.
        strength: For ``"influence"``, the initial strength at distance 0.
        decay: For ``"influence"``, multiplicative decay per step of
            distance.
    """

    prop_type: str = "none"
    radius: int = 1
    strength: float = 1.0
    decay: float = 0.5

    def complexity(self) -> int:
        if self.prop_type == "none":
            return 1
        if self.prop_type == "influence":
            return 4  # type + radius + strength + decay
        return 2  # cascade: type + recurrence

    def to_dict(self) -> dict[str, Any]:
        return {
            "prop_type": self.prop_type,
            "radius": self.radius,
            "strength": self.strength,
            "decay": self.decay,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> PropagationRule:
        return cls(
            prop_type=d["prop_type"],
            radius=d.get("radius", 1),
            strength=d.get("strength", 1.0),
            decay=d.get("decay", 0.5),
        )


# ======================================================================
# Win condition — how does the game end and who wins?
# ======================================================================

WIN_CONDITION_TYPES = ("territory", "elimination", "connection", "threshold")


@dataclass
class WinCondition:
    """Defines how the game ends and who wins.

    Attributes:
        condition_type: The win mechanic.
            - ``"territory"``: win by owning > *threshold* fraction of cells.
            - ``"elimination"``: win by reducing enemy to 0 pieces.
            - ``"connection"``: win by connecting opposite faces along
              *target_dimension* (Hex-style).
            - ``"threshold"``: win when total ``board_values`` across own
              cells exceeds *threshold*.
        threshold: Fraction (for territory) or absolute value (for
            threshold-type).
        target_dimension: For ``"connection"``, which dimension's faces
            to connect.
        max_turns: Hard turn limit.  If the game reaches this without a
            winner, the player with more pieces wins (or draw if equal).
    """

    condition_type: str = "connection"
    threshold: float = 0.5
    target_dimension: int = 0
    target_dimension_p2: int = -1  # For connection: P2's axis (-1 = auto)
    max_turns: int = 100

    def complexity(self) -> int:
        score = 2  # type + max_turns
        if self.condition_type in ("territory", "threshold"):
            score += 1  # threshold parameter
        if self.condition_type == "connection":
            score += 2  # target_dimension per player
        return score

    def to_dict(self) -> dict[str, Any]:
        return {
            "condition_type": self.condition_type,
            "threshold": self.threshold,
            "target_dimension": self.target_dimension,
            "target_dimension_p2": self.target_dimension_p2,
            "max_turns": self.max_turns,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> WinCondition:
        return cls(
            condition_type=d["condition_type"],
            threshold=d.get("threshold", 0.5),
            target_dimension=d.get("target_dimension", 0),
            target_dimension_p2=d.get("target_dimension_p2", -1),
            max_turns=d.get("max_turns", 100),
        )


# ======================================================================
# Action types — what actions can players take? (V3)
# ======================================================================

ACTION_TYPES = ("place", "move")


@dataclass
class ActionRule:
    """Defines which action types are available in a game.

    Attributes:
        action_types: Tuple of enabled action types.
            - ``"place"``: place a new piece on a cell (classic)
            - ``"move"``: move an existing piece to an adjacent cell
        move_constraint: For ``"move"``, where pieces can move to.
            - ``"adjacent_empty"``: can only move to adjacent empty cells
            - ``"adjacent_any"``: can move to any adjacent cell (captures by overwrite)
    """

    action_types: tuple[str, ...] = ("place",)
    move_constraint: str = "adjacent_empty"

    def has_place(self) -> bool:
        return "place" in self.action_types

    def has_move(self) -> bool:
        return "move" in self.action_types

    def complexity(self) -> int:
        score = len(self.action_types)
        if self.has_move():
            score += 1  # move_constraint
        return score

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_types": list(self.action_types),
            "move_constraint": self.move_constraint,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ActionRule:
        return cls(
            action_types=tuple(d.get("action_types", ["place"])),
            move_constraint=d.get("move_constraint", "adjacent_empty"),
        )


# ======================================================================
# Turn structure — how do turns work?
# ======================================================================

TURN_TYPES = ("alternating", "multi_place", "simultaneous")


@dataclass
class TurnStructure:
    """Defines how turns are structured.

    Attributes:
        turn_type: How turns progress.
            - ``"alternating"``: players alternate, one placement per turn.
            - ``"multi_place"``: each player places *pieces_per_turn*
              pieces before the turn passes.
            - ``"simultaneous"``: both players submit actions per round and
              resolve together.  Same-cell placements mutually annihilate.
        pieces_per_turn: For ``"multi_place"``, how many placements
            per turn.  Ignored for simultaneous.
    """

    turn_type: str = "alternating"
    pieces_per_turn: int = 1

    def complexity(self) -> int:
        if self.turn_type == "alternating":
            return 1
        return 2  # type + pieces_per_turn

    def to_dict(self) -> dict[str, Any]:
        return {
            "turn_type": self.turn_type,
            "pieces_per_turn": self.pieces_per_turn,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TurnStructure:
        return cls(
            turn_type=d["turn_type"],
            pieces_per_turn=d.get("pieces_per_turn", 1),
        )


# ======================================================================
# Move constraint types
# ======================================================================

MOVE_CONSTRAINTS = ("adjacent_empty", "adjacent_any")


# ======================================================================
# Cellular automaton rule — simultaneous board update
# ======================================================================


@dataclass
class CARule:
    """Player-symmetric totalistic cellular automaton rule.

    Maps (cell_state, friendly_neighbor_count, enemy_neighbor_count) -> new_state.
    States: 0=empty, 1=friendly (acting player), 2=enemy (opponent).
    Applied simultaneously from a board snapshot after each player action.

    Attributes:
        transition_table: Dict mapping (state, friendly, enemy) -> new_state.
            Missing entries default to identity (no change).
        steps_per_turn: Number of CA iterations per player turn.
        max_neighbors: Maximum neighbor count (varies by topology).
    """

    transition_table: dict[tuple[int, int, int], int] = field(default_factory=dict)
    steps_per_turn: int = 1
    max_neighbors: int = 4

    def apply(self, cell_state: int, friendly_count: int, enemy_count: int) -> int:
        """Look up the new state for a cell. Returns cell_state if no entry."""
        return self.transition_table.get(
            (cell_state, friendly_count, enemy_count), cell_state
        )

    def complexity(self) -> int:
        """Number of entries that differ from identity (no change).

        Discounted by 0.5x because each CA entry is a trivial state
        transition, not a structured rule.  Without this discount, CA
        games have ~2x the complexity of classic games (avg 32 vs 16),
        creating an unfair simplicity penalty.  Run 12 analysis showed
        this is the secondary cause (after non-triviality) of CA
        underperformance.
        """
        count = 0
        for (state, _f, _e), new_state in self.transition_table.items():
            if new_state != state:
                count += 1
        # Half-weight: each CA entry is simpler than a structured rule parameter
        return max(1, count // 2)

    def to_dict(self) -> dict[str, Any]:
        table: dict[str, int] = {}
        for (s, f, e), v in self.transition_table.items():
            table[f"{s},{f},{e}"] = v
        return {
            "transition_table": table,
            "steps_per_turn": self.steps_per_turn,
            "max_neighbors": self.max_neighbors,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> CARule:
        raw = d["transition_table"]
        table: dict[tuple[int, int, int], int] = {}
        for key_str, value in raw.items():
            parts = key_str.split(",")
            table[(int(parts[0]), int(parts[1]), int(parts[2]))] = int(value)
        return cls(
            transition_table=table,
            steps_per_turn=d.get("steps_per_turn", 1),
            max_neighbors=d.get("max_neighbors", 4),
        )


# ======================================================================
# Convenience: copy any rule
# ======================================================================

def copy_rule(rule):
    """Deep-copy any rule dataclass."""
    return copy.deepcopy(rule)
