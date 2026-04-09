"""Game execution engine.

Runs a game defined by a ``GameDef`` as an interactive step-by-step
environment (similar to an OpenAI Gym interface).  All computation is
backed by numpy; expression-tree evaluation uses the ``ExprTree.evaluate``
method from ``representation.py``.
"""

from __future__ import annotations

import copy
from typing import Any

import numpy as np

from game_engine.representation import GameDef

# Bounds used to clamp state values and prevent numeric explosion
_STATE_CLAMP_LO = -10.0
_STATE_CLAMP_HI = 10.0


class GameEngine:
    """Step-by-step execution engine for a ``GameDef``-defined game.

    Usage::

        engine = GameEngine(game_def)
        obs = engine.reset()
        done = False
        while not done:
            action = pick_action(obs, engine.get_legal_actions())
            obs, reward, done, info = engine.step(action)
    """

    def __init__(self, game: GameDef) -> None:
        self.game = game

        # Mutable state -- initialised by reset()
        self.state: np.ndarray = np.zeros(game.state_dim, dtype=np.float64)
        self.current_player: int = 0
        self.step_count: int = 0
        self.done: bool = False
        self._last_rewards: np.ndarray = np.zeros(game.num_players, dtype=np.float64)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reset(self, *, rng: np.random.Generator | None = None) -> np.ndarray:
        """Reset the game to its initial state.

        Parameters
        ----------
        rng : np.random.Generator, optional
            If provided, initialise state with small random values drawn
            from U(-0.1, 0.1).  Otherwise state is all zeros.

        Returns
        -------
        np.ndarray
            Initial observation for the first player.
        """
        if rng is not None:
            self.state = rng.uniform(-0.1, 0.1, size=self.game.state_dim).astype(
                np.float64
            )
        else:
            self.state = np.zeros(self.game.state_dim, dtype=np.float64)

        self.current_player = 0
        self.step_count = 0
        self.done = False
        self._last_rewards = np.zeros(self.game.num_players, dtype=np.float64)

        return self._observe(self.current_player)

    def step(self, action: int) -> tuple[np.ndarray, np.ndarray, bool, dict[str, Any]]:
        """Execute one game step.

        Parameters
        ----------
        action : int
            Index of the action to take (must be in ``[0, num_actions)``).

        Returns
        -------
        observation : np.ndarray
            Observation for the *next* player after this step.
        reward : np.ndarray
            Reward vector of shape ``(num_players,)``.  Non-zero only when
            the game is done (terminal reward).
        done : bool
            Whether the game has ended.
        info : dict
            Auxiliary information (step count, acting player, raw state).
        """
        if self.done:
            return (
                self._observe(self.current_player),
                self._last_rewards.copy(),
                True,
                {"step": self.step_count, "player": self.current_player},
            )

        # Clamp action to valid range
        action = max(0, min(action, self.game.num_actions - 1))

        acting_player = self.current_player

        # --- Apply transition ---
        delta = np.zeros(self.game.state_dim, dtype=np.float64)
        action_trees = self.game.transition_trees[action]
        for d in range(self.game.state_dim):
            delta[d] = action_trees[d].evaluate(
                self.state, action, acting_player, self.step_count
            )

        # Sanitize delta (replace NaN/inf with 0)
        delta = np.nan_to_num(delta, nan=0.0, posinf=0.0, neginf=0.0)

        self.state = self.state + delta
        # Clamp state
        np.clip(self.state, _STATE_CLAMP_LO, _STATE_CLAMP_HI, out=self.state)
        # Final NaN guard on state
        self.state = np.nan_to_num(self.state, nan=0.0, posinf=_STATE_CLAMP_HI, neginf=_STATE_CLAMP_LO)

        self.step_count += 1

        # --- Check termination ---
        term_val = self.game.termination_tree.evaluate(
            self.state, action, acting_player, self.step_count
        )
        self.done = term_val > 0.5

        # --- Compute rewards (only on termination) ---
        rewards = np.zeros(self.game.num_players, dtype=np.float64)
        if self.done:
            for p in range(self.game.num_players):
                r = self.game.reward_tree.evaluate(
                    self.state, action, p, self.step_count
                )
                # Sanitize reward
                if not np.isfinite(r):
                    r = 0.0
                rewards[p] = r
            self._last_rewards = rewards.copy()

        # --- Advance player turn ---
        self.current_player = (self.current_player + 1) % self.game.num_players

        info: dict[str, Any] = {
            "step": self.step_count,
            "player": acting_player,
            "raw_state": self.state.copy(),
        }

        return self._observe(self.current_player), rewards, self.done, info

    def get_legal_actions(self) -> list[int]:
        """Return list of legal action indices (all actions are always legal)."""
        return list(range(self.game.num_actions))

    def get_current_player(self) -> int:
        """Return the index of the player whose turn it is."""
        return self.current_player

    def clone(self) -> "GameEngine":
        """Return a deep copy of this engine (useful for search / MCTS)."""
        return copy.deepcopy(self)

    # ------------------------------------------------------------------
    # Observation helpers
    # ------------------------------------------------------------------

    def _observe(self, player_id: int) -> np.ndarray:
        """Return the observation for *player_id* given the current state.

        Applies the observation mask according to ``game.observation_type``.
        """
        state = self.state.copy()

        obs_type = self.game.observation_type
        mask = self.game.observation_mask

        if obs_type == "full" or mask is None:
            return state

        if obs_type == "partial":
            # mask is 1-d, same length as state
            return state * mask

        if obs_type == "asymmetric":
            # mask is (num_players, state_dim)
            player_mask = mask[player_id % mask.shape[0]]
            return state * player_mask

        # Fallback: full observation
        return state
