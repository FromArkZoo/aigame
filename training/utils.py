"""Training utilities: random agent, game-playing helpers, and evaluation."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from game_engine.engine import GameEngine
    from game_engine.representation import GameDef
    from training.agent import PolicyNetwork


# ======================================================================
# Random agent
# ======================================================================

class RandomAgent:
    """Agent that selects uniformly at random among legal actions."""

    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)

    def select_action(
        self,
        obs: np.ndarray,
        legal_actions: list[int] | None = None,
        deterministic: bool = False,
    ) -> tuple[int, float, float]:
        """Pick a random legal action.

        Returns the same ``(action, log_prob, value)`` signature as
        :class:`PolicyNetwork.select_action` so callers can treat both
        interchangeably.

        ``log_prob`` is the true log-probability under the uniform
        distribution; ``value`` is always 0.
        """
        if legal_actions is None or len(legal_actions) == 0:
            raise ValueError("RandomAgent requires at least one legal action.")
        action = self.rng.choice(legal_actions)
        log_prob = -np.log(len(legal_actions))
        value = 0.0
        return action, log_prob, value


# ======================================================================
# Single-game helper
# ======================================================================

def play_game(
    engine: "GameEngine",
    agent0,
    agent1,
    deterministic: bool = True,
    max_steps: int | None = None,
) -> tuple[int | None, int, dict]:
    """Play a full game between two agents.

    Args:
        engine: a ``GameEngine`` instance (already constructed with its
                ``GameDef``).
        agent0: agent for player 0 (any object exposing ``select_action``).
        agent1: agent for player 1.
        deterministic: forwarded to ``select_action``.
        max_steps: hard cap on the number of steps.  ``None`` means use the
                   engine default (``GameDef.max_steps`` or similar).

    Returns:
        winner: ``0``, ``1``, or ``None`` (draw / max-steps hit).
        game_length: number of environment steps taken.
        rewards: ``{0: total_reward_p0, 1: total_reward_p1}``
    """
    agents = [agent0, agent1]
    obs = engine.reset()
    done = False
    total_rewards = {0: 0.0, 1: 0.0}
    step_count = 0

    while not done:
        if max_steps is not None and step_count >= max_steps:
            # Game did not terminate within budget.
            break

        current_player = engine.get_current_player()
        legal_actions = engine.get_legal_actions()

        if len(legal_actions) == 0:
            # No legal actions: treat as draw.
            break

        action, _, _ = agents[current_player].select_action(
            obs, legal_actions=legal_actions, deterministic=deterministic
        )

        obs, reward, done, info = engine.step(action)
        step_count += 1

        # ``reward`` may be a scalar, dict, or numpy array.
        if isinstance(reward, dict):
            for pid, r in reward.items():
                total_rewards[pid] += r
        elif isinstance(reward, np.ndarray):
            for pid in range(len(reward)):
                total_rewards[pid] = total_rewards.get(pid, 0.0) + float(reward[pid])
        else:
            total_rewards[current_player] += float(reward)

    # Determine winner: highest cumulative reward.
    winner = _determine_winner(total_rewards)
    return winner, step_count, total_rewards


def _determine_winner(total_rewards: dict) -> int | None:
    """Return the player index with highest reward, or ``None`` on a draw."""
    r0 = total_rewards.get(0, 0.0)
    r1 = total_rewards.get(1, 0.0)
    if r0 > r1:
        return 0
    elif r1 > r0:
        return 1
    return None


# ======================================================================
# Evaluation helper
# ======================================================================

def evaluate_agents(
    game: "GameDef",
    agent0,
    agent1,
    num_episodes: int = 100,
    max_steps: int | None = None,
) -> dict:
    """Evaluate two agents over many games with seat swapping.

    Plays half the episodes with normal seating and half with swapped
    seats so that ``p0_winrate`` measures first-player advantage rather
    than agent identity.

    Returns a dict with:
        p0_winrate, p1_winrate, draw_rate, avg_game_length
    """
    from game_engine.factory import create_engine

    engine = create_engine(game)
    p1_wins = 0  # seat 0 (first player) wins
    p2_wins = 0
    draws = 0
    total_length = 0
    half = num_episodes // 2

    for i in range(num_episodes):
        if i < half:
            a0, a1 = agent0, agent1
        else:
            a0, a1 = agent1, agent0

        winner, length, _ = play_game(
            engine, a0, a1, deterministic=True, max_steps=max_steps
        )
        total_length += length
        if winner is None:
            draws += 1
        elif winner == 0:
            p1_wins += 1
        else:
            p2_wins += 1

    n = max(num_episodes, 1)
    return {
        "p0_winrate": p1_wins / n,
        "p1_winrate": p2_wins / n,
        "draw_rate": draws / n,
        "avg_game_length": total_length / n,
    }
