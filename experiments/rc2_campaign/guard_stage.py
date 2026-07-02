"""Insertion guard stage (prereg §4 steps 4). RUSH/TILT from 12 mirrored
TacticalAgent pairs (n=24, content-derived seeds); REACH-v3 from the genome's
own T1 draw count (threshold family only). Fired guard = veto."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
from metrics.guard_probe import (  # noqa: E402
    rollout_tactical, rush_share, tilt_p1_share,
    RUSH_SHARE, TILT_SHARE_REPRICED,
)
from experiments.rc2_archive.run_probe import eval_seed_for  # noqa: E402

N_PAIRS = 12
REACH_FIRE_COUNT = 5      # >= 5/24 winner-None keeps a threshold genome


def guard_pair_seeds(canon, n_pairs=N_PAIRS):
    rng = np.random.default_rng(eval_seed_for(canon, 0) ^ 0x6EAC)  # guard-stage stream
    out = []
    for _ in range(n_pairs):
        a, b = (int(x) for x in rng.integers(1, 2**31 - 1, size=2))
        out.append(((a, b), (b, a)))
    return out


def _verdict_from_shares(rush, tilt, reach_count, reach_n, family):
    vetoes = []
    if not np.isnan(rush) and rush >= RUSH_SHARE:
        vetoes.append("rush")
    if not np.isnan(tilt) and tilt >= TILT_SHARE_REPRICED:
        vetoes.append("tilt")
    if family == "threshold" and reach_count < REACH_FIRE_COUNT:
        vetoes.append("reach")
    return dict(passed=not vetoes, rush_share=rush, tilt_share=tilt,
                reach_count=reach_count, family=family, vetoes=vetoes)


def run_guard_stage(game, canon, family, reach_draw_count, reach_n=24, n_pairs=N_PAIRS):
    records = []
    for (s1, s2), (s3, s4) in guard_pair_seeds(canon, n_pairs):
        for (p1, p2) in ((s1, s2), (s3, s4)):
            r = rollout_tactical(game, p1, p2)
            records.append(dict(winner=r["winner"], plies=r["plies"]))
    dec_r, rush = rush_share(records)
    dec_t, tilt = tilt_p1_share(records)
    out = _verdict_from_shares(rush, tilt, reach_draw_count, reach_n, family)
    out["decisive"] = dec_r
    return out
