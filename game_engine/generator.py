"""Random game generator using expression-tree synthesis.

Generates complete, playable game definitions by randomly constructing
expression trees for transitions, termination, and rewards. Includes
validation to filter out degenerate games.
"""

from __future__ import annotations

import uuid
from typing import Optional

import numpy as np

from config import GameConfig
from game_engine.representation import (
    ARITY,
    INTERNAL_OPS,
    LEAF_OPS,
    ExprTree,
    GameDef,
)


# Operators suitable for transition / reward trees (numeric output)
_NUMERIC_INTERNAL_OPS: list[str] = [
    "+", "-", "*", "/safe",
    "abs", "neg",
    "mod", "clamp",
    "if_then_else",
]

# Operators suitable for termination trees (boolean-ish output)
_BOOLEAN_INTERNAL_OPS: list[str] = [
    ">", "<", "==",
    "and", "or", "not",
    "if_then_else",
]

# Small set of "nice" constants to embed in leaves
_CONST_POOL: list[float] = [
    -2.0, -1.0, -0.5, 0.0, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0,
]


class GameGenerator:
    """Generates random game definitions driven by ``GameConfig``."""

    def __init__(self, config: GameConfig, seed: int = 42) -> None:
        self.config = config
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    # ------------------------------------------------------------------
    # Random tree generation
    # ------------------------------------------------------------------

    def generate_random_tree(
        self,
        max_depth: int,
        available_state_dims: int,
        *,
        prefer_boolean: bool = False,
    ) -> ExprTree:
        """Build a random expression tree via the *grow* method.

        Parameters
        ----------
        max_depth : int
            Maximum depth of the generated tree.
        available_state_dims : int
            Number of state dimensions (so ``state_var`` indices stay in range).
        prefer_boolean : bool
            If True, bias toward comparison / logical operators (useful for
            termination trees).

        Returns
        -------
        ExprTree
        """
        return self._grow(max_depth, available_state_dims, prefer_boolean)

    def _grow(
        self,
        depth_remaining: int,
        state_dim: int,
        prefer_boolean: bool,
    ) -> ExprTree:
        """Recursive grow method for tree generation."""
        # At depth 0 (or probabilistically), generate a leaf
        if depth_remaining <= 0 or (depth_remaining < 2 and self.rng.random() < 0.3):
            return self._random_leaf(state_dim)

        # Pick an internal operator
        ops_pool = _BOOLEAN_INTERNAL_OPS if prefer_boolean else _NUMERIC_INTERNAL_OPS
        op = self.rng.choice(ops_pool)
        arity = ARITY[op]
        children = [
            self._grow(depth_remaining - 1, state_dim, prefer_boolean=False)
            for _ in range(arity)
        ]
        return ExprTree(op=op, children=children)

    def _random_leaf(self, state_dim: int) -> ExprTree:
        """Generate a random leaf node."""
        leaf_type = self.rng.choice(list(LEAF_OPS))

        if leaf_type == "const":
            val = float(self.rng.choice(_CONST_POOL))
            return ExprTree(op="const", value=val)
        if leaf_type == "state_var":
            idx = int(self.rng.integers(0, max(state_dim, 1)))
            return ExprTree(op="state_var", value=idx)
        if leaf_type == "action_var":
            return ExprTree(op="action_var")
        if leaf_type == "player_id":
            return ExprTree(op="player_id")
        # step
        return ExprTree(op="step")

    # ------------------------------------------------------------------
    # Game generation
    # ------------------------------------------------------------------

    def generate_game(self, seed: Optional[int] = None) -> GameDef:
        """Generate a complete random game definition.

        Parameters
        ----------
        seed : int, optional
            If provided, re-seeds the internal RNG for reproducibility.

        Returns
        -------
        GameDef
        """
        if seed is not None:
            self.rng = np.random.default_rng(seed)

        cfg = self.config

        # Random structural parameters
        state_dim = int(self.rng.integers(cfg.min_state_dim, cfg.max_state_dim + 1))
        num_actions = int(self.rng.integers(cfg.min_actions, cfg.max_actions + 1))
        num_players = cfg.num_players

        # Transition trees: one per (action, state_dim)
        transition_trees: list[list[ExprTree]] = []
        for _a in range(num_actions):
            action_trees: list[ExprTree] = []
            for _d in range(state_dim):
                depth = int(self.rng.integers(cfg.min_tree_depth, cfg.max_tree_depth + 1))
                tree = self.generate_random_tree(depth, state_dim)
                action_trees.append(tree)
            transition_trees.append(action_trees)

        # Termination tree (boolean-ish)
        term_depth = int(self.rng.integers(cfg.min_tree_depth, cfg.max_tree_depth + 1))
        termination_tree = self._build_termination_tree(state_dim, term_depth)

        # Reward tree (should depend on player_id to allow asymmetric rewards)
        reward_depth = int(self.rng.integers(cfg.min_tree_depth, cfg.max_tree_depth + 1))
        reward_tree = self._build_reward_tree(state_dim, reward_depth)

        # Observation type and mask
        obs_type: str = str(self.rng.choice(cfg.observation_types))
        obs_mask: np.ndarray | None = None
        if obs_type == "partial":
            # Each player sees the same random subset of state dims
            obs_mask = (self.rng.random(state_dim) > 0.3).astype(np.float64)
            # Ensure at least one dim is visible
            if obs_mask.sum() == 0:
                obs_mask[0] = 1.0
        elif obs_type == "asymmetric":
            # Different mask per player: shape (num_players, state_dim)
            obs_mask = (self.rng.random((num_players, state_dim)) > 0.3).astype(np.float64)
            for p in range(num_players):
                if obs_mask[p].sum() == 0:
                    obs_mask[p, 0] = 1.0

        game_id = uuid.uuid4().hex[:12]

        return GameDef(
            game_id=game_id,
            state_dim=state_dim,
            num_actions=num_actions,
            num_players=num_players,
            transition_trees=transition_trees,
            termination_tree=termination_tree,
            reward_tree=reward_tree,
            observation_type=obs_type,
            observation_mask=obs_mask,
            metadata={
                "generation": 0,
                "parent_ids": [],
                "seed": seed if seed is not None else self.seed,
            },
        )

    # ------------------------------------------------------------------
    # Specialised tree builders
    # ------------------------------------------------------------------

    def _build_termination_tree(self, state_dim: int, depth: int) -> ExprTree:
        """Build a termination tree that fires (>0) based on step count *and*
        state conditions so games are guaranteed to eventually end.

        Structure:  or( step > max_steps, <random boolean tree> )
        """
        step_limit = ExprTree(
            op=">",
            children=[
                ExprTree(op="step"),
                ExprTree(op="const", value=float(self.config.max_game_steps)),
            ],
        )
        state_condition = self.generate_random_tree(
            depth, state_dim, prefer_boolean=True,
        )
        return ExprTree(op="or", children=[step_limit, state_condition])

    def _build_reward_tree(self, state_dim: int, depth: int) -> ExprTree:
        """Build a reward tree that naturally depends on ``player_id``.

        Structure:  if_then_else(player_id == 0, <tree_a>, neg(<tree_a>))
        This gives a zero-sum flavour; the random sub-tree decides *which*
        player is winning.
        """
        sub_tree = self.generate_random_tree(depth, state_dim)
        return ExprTree(
            op="if_then_else",
            children=[
                ExprTree(
                    op="==",
                    children=[
                        ExprTree(op="player_id"),
                        ExprTree(op="const", value=0.0),
                    ],
                ),
                sub_tree,
                ExprTree(op="neg", children=[sub_tree.copy()]),
            ],
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_game(
        self,
        game: GameDef,
        *,
        max_rollout_steps: int = 300,
        num_rollouts: int = 5,
    ) -> bool:
        """Run sanity checks on a generated game.

        Checks:
        1. The game terminates within *max_rollout_steps* in random play.
        2. Not all actions produce the same next state (i.e. actions matter).
        3. Both players can potentially receive positive reward.

        Returns
        -------
        bool
            True if the game passes all checks.
        """
        # Lazy import to avoid circular dependency
        from game_engine.engine import GameEngine

        rng = np.random.default_rng(self.seed + 9999)

        # --- Check 1: terminates ---
        terminated_at_least_once = False
        for _ in range(num_rollouts):
            eng = GameEngine(game)
            eng.reset()
            done = False
            for _s in range(max_rollout_steps):
                action = int(rng.integers(0, game.num_actions))
                _obs, _rew, done, _info = eng.step(action)
                if done:
                    terminated_at_least_once = True
                    break
            if not terminated_at_least_once:
                # If even one rollout doesn't terminate, that's a problem
                # (but we keep trying other rollouts)
                pass
        if not terminated_at_least_once:
            return False

        # --- Check 2: actions are not all equivalent ---
        eng = GameEngine(game)
        eng.reset()
        base_state = eng.state.copy()
        states_after_action: list[np.ndarray] = []
        for a in range(game.num_actions):
            eng2 = eng.clone()
            eng2.state = base_state.copy()
            eng2.step(a)
            states_after_action.append(eng2.state.copy())

        all_same = True
        for i in range(1, len(states_after_action)):
            if not np.allclose(states_after_action[0], states_after_action[i], atol=1e-9):
                all_same = False
                break
        if all_same:
            return False

        # --- Check 3: both players can get positive reward ---
        player_got_positive = [False] * game.num_players
        for _ in range(num_rollouts * 2):
            eng = GameEngine(game)
            eng.reset()
            done = False
            for _s in range(max_rollout_steps):
                action = int(rng.integers(0, game.num_actions))
                _obs, rewards, done, _info = eng.step(action)
                if done:
                    for p in range(game.num_players):
                        if rewards[p] > 1e-9:
                            player_got_positive[p] = True
                    break
        if not all(player_got_positive):
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
    ) -> list[GameDef]:
        """Generate *count* validated games, discarding invalid ones.

        Parameters
        ----------
        count : int
            Number of valid games desired.
        seed : int
            Base seed; each attempt uses ``seed + i``.
        max_attempts_factor : int
            Try at most ``count * max_attempts_factor`` candidates before
            giving up.

        Returns
        -------
        list[GameDef]
        """
        valid: list[GameDef] = []
        max_attempts = count * max_attempts_factor
        for i in range(max_attempts):
            game = self.generate_game(seed=seed + i)
            if self.validate_game(game):
                valid.append(game)
                if len(valid) >= count:
                    break
        return valid
