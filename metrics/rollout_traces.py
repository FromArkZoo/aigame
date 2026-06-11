"""Seeded rollout harness producing per-ply ownership traces (RC2 Phase A).

Protocol mirrors experiments/siege/anchor_drama.py's validated random+greedy
scheme, factored for reuse. First half of n rollouts use a random-pair, second
half use a greedy-pair. Seed constants are IDENTICAL to anchor_drama.py so
results remain directly comparable:
  random  pair: seed = base_seed * 10_000 + i  (second agent: +1)
  greedy  pair: seed = base_seed * 29 + 31 * i  (second agent: +7)

Returns OWNERSHIP SNAPSHOTS per ply (one copy of board_owners after each
non-pie-swap ply), plus end info and capture counts attributed by piece-count
drops. Descriptors in metrics/descriptors.py derive everything else via the
observer field.

Hard cap: 2 * max_game_steps (mirrors the instrumented_episode idiom used
elsewhere in the codebase).
"""
from __future__ import annotations

import numpy as np

from game_engine.factory import create_engine
from training.utils import GreedyAgent, RandomAgent


def rollout_with_traces(game, policy: str, seed: int) -> dict:
    """Run one seeded rollout, returning per-ply ownership snapshots + end info.

    Args:
        game: GameDefV2 instance.
        policy: "random" or "greedy".
        seed: Seed for the first agent; second agent gets seed+1 (random) or
              seed+7 (greedy), exactly as in anchor_drama.py.

    Returns dict with keys:
        policy          : str, echoes the policy arg.
        plies           : int, number of non-pie-swap plies recorded.
        owner_snapshots : list[np.ndarray], one copy of board_owners per ply.
        winner          : int | None, engine._winner (1, 2, or None = draw).
        timeout         : bool, whether game ended via max-turns.
        captures_total  : int, total piece-count drops attributed to captures.
        game_length     : int, engine.step_count (includes pie-swap steps).
    """
    engine = create_engine(game)
    obs = engine.reset()

    if policy == "random":
        agent0 = RandomAgent(seed=seed)
        agent1 = RandomAgent(seed=seed + 1)
    elif policy == "greedy":
        # GreedyAgent takes (engine, player_num, seed) — positional engine,
        # then keyword player_num and seed. Same signature as anchor_drama.py
        # lines 358-359.
        agent0 = GreedyAgent(engine, player_num=1, seed=seed)
        agent1 = GreedyAgent(engine, player_num=2, seed=seed + 7)
    else:
        raise ValueError(f"Unknown policy: {policy!r}; must be 'random' or 'greedy'")

    agents = [agent0, agent1]
    snapshots: list[np.ndarray] = []
    captures = 0
    prev_counts = list(engine.piece_counts)  # [p1_count, p2_count]
    hard_cap = 2 * engine.game.max_game_steps

    while not engine.done and engine.step_count < hard_cap:
        legal = engine.get_legal_actions()
        agent = agents[engine.get_current_player()]  # get_current_player() is 0-indexed
        action, _, _ = agent.select_action(obs, legal_actions=legal,
                                           deterministic=False)
        obs, _, _, info = engine.step(action)
        if not info.get("pie_swap"):
            # Attribute captures by piece-count drops before updating prev_counts
            for pidx in (0, 1):
                drop = prev_counts[pidx] - engine.piece_counts[pidx]
                if drop > 0:
                    captures += drop
            snapshots.append(engine.board_owners.copy())
        prev_counts = list(engine.piece_counts)

    return dict(
        policy=policy,
        plies=len(snapshots),
        owner_snapshots=snapshots,
        winner=engine._winner,
        timeout=bool(getattr(engine, "_ended_by_max_turns", False)),
        captures_total=captures,
        game_length=engine.step_count,
    )


def run_protocol(game, n: int, base_seed: int) -> list[dict]:
    """Run n rollouts: first half random-pair, second half greedy-pair.

    Seed formulas are identical to anchor_drama.py so results are comparable:
      random rollout i: seed = base_seed * 10_000 + i
      greedy rollout i: seed = base_seed * 29 + 31 * i

    Args:
        game:      GameDefV2 instance.
        n:         Total number of rollouts (split evenly; odd n gives greedy
                   the extra rollout, matching anchor_drama.py's n_greedy = n - n//2).
        base_seed: Base seed; combined with the per-rollout index formula above.

    Returns list of dicts from rollout_with_traces.
    """
    half = n // 2
    out: list[dict] = []
    for i in range(half):
        out.append(rollout_with_traces(game, "random",
                                       seed=base_seed * 10_000 + i))
    for i in range(n - half):
        out.append(rollout_with_traces(game, "greedy",
                                       seed=base_seed * 29 + 31 * i))
    return out
