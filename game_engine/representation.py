"""Game representation as abstract state machines with expression trees.

Games are defined by expression trees that govern transitions, termination,
and rewards. This provides a compact, evolvable, and interpretable
representation suitable for automated game generation.
"""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from typing import Any, Optional, Union

import numpy as np


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

ARITHMETIC_OPS = {"+", "-", "*", "/safe"}
COMPARISON_OPS = {">", "<", "=="}
LOGICAL_OPS = {"and", "or", "not"}
CONDITIONAL_OPS = {"if_then_else"}
UNARY_MATH_OPS = {"abs", "neg"}
OTHER_OPS = {"mod", "clamp"}

LEAF_OPS = {"const", "state_var", "action_var", "player_id", "step"}

# How many children each operator expects
ARITY: dict[str, int] = {
    # arithmetic (binary)
    "+": 2,
    "-": 2,
    "*": 2,
    "/safe": 2,
    # comparison (binary)
    ">": 2,
    "<": 2,
    "==": 2,
    # logical
    "and": 2,
    "or": 2,
    "not": 1,
    # conditional
    "if_then_else": 3,
    # unary math
    "abs": 1,
    "neg": 1,
    # other
    "mod": 2,
    "clamp": 3,  # clamp(value, lo, hi)
    # leaves
    "const": 0,
    "state_var": 0,
    "action_var": 0,
    "player_id": 0,
    "step": 0,
}

ALL_OPS = set(ARITY.keys())
INTERNAL_OPS = ALL_OPS - LEAF_OPS


def safe_div(a: float, b: float) -> float:
    """Division that returns 0.0 when the denominator is zero or result is non-finite."""
    if b == 0.0:
        return 0.0
    result = a / b
    if not math.isfinite(result):
        return 0.0
    return result


def _sanitize(value: float) -> float:
    """Clamp a scalar to a sane range and replace NaN/inf with 0."""
    if not math.isfinite(value):
        return 0.0
    return max(-1e6, min(1e6, value))


# ---------------------------------------------------------------------------
# ExprTree
# ---------------------------------------------------------------------------

@dataclass
class ExprTree:
    """A single node in an expression tree.

    Leaves hold a constant value or reference a context variable by index.
    Internal nodes hold an operator and a list of child sub-trees.
    """

    op: str
    children: list["ExprTree"] = field(default_factory=list)
    value: Union[float, int, None] = None  # for const / state_var / action_var indices

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def evaluate(
        self,
        state: np.ndarray,
        action: int,
        player_id: int,
        step: int,
    ) -> float:
        """Recursively evaluate the tree given the current game context.

        Parameters
        ----------
        state : np.ndarray
            Current game state vector.
        action : int
            The action taken (integer index).
        player_id : int
            The current player (0-indexed).
        step : int
            The current step / turn number.

        Returns
        -------
        float
            Scalar result of the evaluation.
        """
        op = self.op

        # --- leaves ---
        if op == "const":
            return float(self.value) if self.value is not None else 0.0

        if op == "state_var":
            idx = int(self.value) if self.value is not None else 0
            idx = idx % len(state) if len(state) > 0 else 0
            return float(state[idx])

        if op == "action_var":
            return float(action)

        if op == "player_id":
            return float(player_id)

        if op == "step":
            return float(step)

        # --- internal: evaluate children first ---
        child_vals = [
            _sanitize(c.evaluate(state, action, player_id, step))
            for c in self.children
        ]

        # arithmetic
        if op == "+":
            return _sanitize(child_vals[0] + child_vals[1])
        if op == "-":
            return _sanitize(child_vals[0] - child_vals[1])
        if op == "*":
            return _sanitize(child_vals[0] * child_vals[1])
        if op == "/safe":
            return _sanitize(safe_div(child_vals[0], child_vals[1]))

        # comparison  (return 1.0 for true, 0.0 for false)
        if op == ">":
            return 1.0 if child_vals[0] > child_vals[1] else 0.0
        if op == "<":
            return 1.0 if child_vals[0] < child_vals[1] else 0.0
        if op == "==":
            return 1.0 if abs(child_vals[0] - child_vals[1]) < 1e-9 else 0.0

        # logical  (>0.5 is truthy)
        if op == "and":
            return 1.0 if (child_vals[0] > 0.5 and child_vals[1] > 0.5) else 0.0
        if op == "or":
            return 1.0 if (child_vals[0] > 0.5 or child_vals[1] > 0.5) else 0.0
        if op == "not":
            return 0.0 if child_vals[0] > 0.5 else 1.0

        # conditional
        if op == "if_then_else":
            return child_vals[1] if child_vals[0] > 0.5 else child_vals[2]

        # unary math
        if op == "abs":
            return abs(child_vals[0])
        if op == "neg":
            return _sanitize(-child_vals[0])

        # other
        if op == "mod":
            if child_vals[1] == 0.0:
                return 0.0
            return _sanitize(math.fmod(child_vals[0], child_vals[1]))
        if op == "clamp":
            lo = min(child_vals[1], child_vals[2])
            hi = max(child_vals[1], child_vals[2])
            return _sanitize(max(lo, min(hi, child_vals[0])))

        raise ValueError(f"Unknown op: {op}")

    # ------------------------------------------------------------------
    # Complexity
    # ------------------------------------------------------------------

    def complexity(self) -> int:
        """Return the total number of AST nodes in this tree."""
        return 1 + sum(c.complexity() for c in self.children)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize the tree to a plain dict (JSON-safe)."""
        d: dict[str, Any] = {"op": self.op}
        if self.value is not None:
            # Convert numpy types to native Python for JSON compatibility
            if isinstance(self.value, (np.integer,)):
                d["value"] = int(self.value)
            elif isinstance(self.value, (np.floating,)):
                d["value"] = float(self.value)
            else:
                d["value"] = self.value
        if self.children:
            d["children"] = [c.to_dict() for c in self.children]
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ExprTree":
        """Reconstruct an ExprTree from a dict produced by ``to_dict``."""
        children = [cls.from_dict(c) for c in d.get("children", [])]
        return cls(op=d["op"], children=children, value=d.get("value"))

    # ------------------------------------------------------------------
    # Copy
    # ------------------------------------------------------------------

    def copy(self) -> "ExprTree":
        """Return a deep copy of this tree."""
        return copy.deepcopy(self)

    # ------------------------------------------------------------------
    # Repr
    # ------------------------------------------------------------------

    def __repr__(self) -> str:  # pragma: no cover
        if self.op in LEAF_OPS:
            if self.value is not None:
                return f"{self.op}({self.value})"
            return self.op
        child_strs = ", ".join(repr(c) for c in self.children)
        return f"{self.op}({child_strs})"


# ---------------------------------------------------------------------------
# GameDef
# ---------------------------------------------------------------------------

@dataclass
class GameDef:
    """Complete definition of a generated game.

    A game is an abstract state machine whose dynamics are defined
    entirely by expression trees.
    """

    game_id: str
    state_dim: int
    num_actions: int
    num_players: int
    transition_trees: list[list[ExprTree]]
    # Outer list indexed by action, inner list indexed by state dimension.
    # transition_trees[a][d] gives the state-delta ExprTree for action *a*,
    # state dimension *d*.
    termination_tree: ExprTree
    reward_tree: ExprTree  # evaluated per player (player_id is a context var)
    observation_type: str  # "full", "partial", "asymmetric"
    observation_mask: Optional[np.ndarray] = None  # shape varies by obs type
    metadata: dict = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize the full game definition to a JSON-safe dict."""
        return {
            "game_id": self.game_id,
            "state_dim": self.state_dim,
            "num_actions": self.num_actions,
            "num_players": self.num_players,
            "transition_trees": [
                [t.to_dict() for t in action_trees]
                for action_trees in self.transition_trees
            ],
            "termination_tree": self.termination_tree.to_dict(),
            "reward_tree": self.reward_tree.to_dict(),
            "observation_type": self.observation_type,
            "observation_mask": (
                self.observation_mask.tolist()
                if self.observation_mask is not None
                else None
            ),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "GameDef":
        """Reconstruct a GameDef from a dict."""
        transition_trees = [
            [ExprTree.from_dict(t) for t in action_trees]
            for action_trees in d["transition_trees"]
        ]
        obs_mask = (
            np.array(d["observation_mask"])
            if d.get("observation_mask") is not None
            else None
        )
        return cls(
            game_id=d["game_id"],
            state_dim=d["state_dim"],
            num_actions=d["num_actions"],
            num_players=d["num_players"],
            transition_trees=transition_trees,
            termination_tree=ExprTree.from_dict(d["termination_tree"]),
            reward_tree=ExprTree.from_dict(d["reward_tree"]),
            observation_type=d["observation_type"],
            observation_mask=obs_mask,
            metadata=d.get("metadata", {}),
        )

    def copy(self) -> "GameDef":
        """Deep copy of the entire game definition."""
        return copy.deepcopy(self)

    def total_complexity(self) -> int:
        """Sum of AST-node counts across every tree in the game."""
        total = 0
        for action_trees in self.transition_trees:
            for tree in action_trees:
                total += tree.complexity()
        total += self.termination_tree.complexity()
        total += self.reward_tree.complexity()
        return total
