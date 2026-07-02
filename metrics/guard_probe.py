"""Tactical-rollout guard primitives (RC2). Lifted from rc2_descriptor_v2 so
the campaign guard stage and CAL-G share one implementation (prereg §4 [C2])."""
from __future__ import annotations

import numpy as np

from game_engine.factory import create_engine
from game_engine.game_def_v2 import GameDefV2
from metrics.tactical_agent import TacticalAgent

RUSH_PLY_CAP = 6          # "winner in <= 6 plies"
RUSH_SHARE = 0.25         # ">= 25% of decisive tactical games"
TILT_SHARE_REPRICED = 0.625   # CAL-G re-price (15/24); prereg §4


def rollout_tactical(game: GameDefV2, seed_p1: int, seed_p2: int) -> dict:
    """One tactical-vs-tactical rollout; same trace dict shape as
    metrics.rollout_traces.rollout_with_traces."""
    engine = create_engine(game)
    obs = engine.reset()
    agents = [
        TacticalAgent(engine, player_num=1, seed=seed_p1),
        TacticalAgent(engine, player_num=2, seed=seed_p2),
    ]
    snapshots: list[np.ndarray] = []
    captures = 0
    prev_counts = list(engine.piece_counts)
    hard_cap = 2 * engine.game.max_game_steps

    while not engine.done and engine.step_count < hard_cap:
        legal = engine.get_legal_actions()
        agent = agents[engine.get_current_player()]  # 0-indexed
        action, _, _ = agent.select_action(obs, legal_actions=legal,
                                           deterministic=False)
        obs, _, _, info = engine.step(action)
        if not info.get("pie_swap"):
            for pidx in (0, 1):
                drop = prev_counts[pidx] - engine.piece_counts[pidx]
                if drop > 0:
                    captures += drop
            snapshots.append(engine.board_owners.copy())
        prev_counts = list(engine.piece_counts)

    return dict(
        policy="tactical",
        plies=len(snapshots),
        owner_snapshots=snapshots,
        winner=engine._winner,
        timeout=bool(getattr(engine, "_ended_by_max_turns", False)),
        captures_total=captures,
        game_length=engine.step_count,
    )


def rush_share(records: list[dict]) -> tuple[int, float]:
    """(decisive_count, share of decisive games ending in <= RUSH_PLY_CAP plies)."""
    decisive = [r for r in records if r["winner"] is not None]
    if not decisive:
        return 0, float("nan")
    return len(decisive), sum(1 for r in decisive if r["plies"] <= RUSH_PLY_CAP) / len(decisive)


def tilt_p1_share(records: list[dict]) -> tuple[int, float]:
    """(decisive_count, share of decisive games won by P1)."""
    decisive = [r for r in records if r["winner"] is not None]
    if not decisive:
        return 0, float("nan")
    return len(decisive), sum(1 for r in decisive if r["winner"] == 1) / len(decisive)
