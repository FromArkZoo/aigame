"""Genome-based net-free UCT planning-gap evaluator (RC2 campaign).

Reuses anchor_calibration's UCT instrument (same one CAL-I validates) but
seeds each genome's games from the content-derived eval_seed_for formula
(prereg §2) instead of the fixed anchor streams. See BUILD_LOG decisions 3/6.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game_engine.factory import create_engine  # noqa: E402
from training.utils import play_game  # noqa: E402
from experiments.rc2_planning_gap.anchor_calibration import UCTAgent, MAX_STEPS  # noqa: E402
from experiments.rc2_archive.run_probe import eval_seed_for  # noqa: E402

T1_DEEP, T1_SHALLOW, T1_N = 128, 16, 24
FULL_DEEP, FULL_SHALLOW, FULL_N = 256, 16, 48


def pg_seeds(canon: str, batch_index: int, n: int = T1_N) -> list[tuple[int, int, int]]:
    rng = np.random.default_rng(eval_seed_for(canon, batch_index))
    out = []
    for j in range(n):
        deep_seed, shallow_seed = (int(x) for x in rng.integers(0, 2**31 - 1, size=2))
        out.append((deep_seed, shallow_seed, 0 if j < n // 2 else 1))
    return out


def pg_game(game, deep_seed, shallow_seed, deep_seat, deep_sims, shallow_sims) -> dict:
    engine = create_engine(game)
    deep = UCTAgent(engine, deep_sims, deep_seed)
    shallow = UCTAgent(engine, shallow_sims, shallow_seed)
    agents = (deep, shallow) if deep_seat == 0 else (shallow, deep)
    winner, length, _ = play_game(engine, agents[0], agents[1],
                                  deterministic=True, max_steps=MAX_STEPS)
    score = 0.5 if winner is None else float(winner == deep_seat)
    return dict(score=score, winner=winner, length=length)


def pg_batch(game, canon: str, batch_index: int = 0,
             deep_sims: int = T1_DEEP, shallow_sims: int = T1_SHALLOW,
             n: int = T1_N) -> dict:
    cells = [pg_game(game, ds, ss, seat, deep_sims, shallow_sims)
             for (ds, ss, seat) in pg_seeds(canon, batch_index, n)]
    scores = [c["score"] for c in cells]
    wins = sum(1 for c in cells if c["score"] == 1.0)
    draws = sum(1 for c in cells if c["score"] == 0.5)
    losses = sum(1 for c in cells if c["score"] == 0.0)
    raw = float(np.mean(scores)) - 0.5
    return dict(raw_pg=raw, floored_pg=max(raw, 0.0), wins=wins, draws=draws,
                losses=losses, n=n, non_draw_share=(wins + losses) / n,
                mean_length=float(np.mean([c["length"] for c in cells])),
                scores=scores)
