"""Phase B — R18 multi-seed rescue script.

For every R18 game with >=2 persisted training_runs we recompute the
headline GE using C2 (multi-seed averaging) on the inputs that the headline
GE depends on. NO retraining: this is purely a re-derivation from data
already in the DB.

Method (ratio approach, so unknown penalties cancel exactly)
------------------------------------------------------------

Original-run partial composite (uses run-0 inputs only):

    depth_orig    = strategic_depth(curve_0)
    non_triv_orig = non_triviality(tvr_0, p0_0)
    raw_orig      = composite_score(simplicity, depth_orig, non_triv_orig, diversity)
    partial_orig  = raw_orig * length_factor(alen_0)

Rescued partial composite (uses C2-averaged inputs across all N runs):

    curve_avg    = pointwise_mean(curves)
    tvr_avg      = mean(per_run_tvr)
    p0_avg       = mean(per_run_p0)
    alen_avg     = mean(per_run_alen)
    depth_resc   = strategic_depth(curve_avg)
    non_triv_resc = non_triviality(tvr_avg, p0_avg)
    raw_resc     = composite_score(simplicity, depth_resc, non_triv_resc, diversity)
    partial_resc = raw_resc * length_factor(alen_avg)

Then:

    rescued_go_essence = stored_go_essence * (partial_resc / partial_orig)

The seat_balance penalty, timeout penalty, novelty bonus, and stability
penalty all cancel in the ratio (stability uses the full per-run list in
both numerator and denominator; the others are PPO-seed-independent).
Rescued GE is therefore directly comparable to the stored value: it is
exactly what R18 would have written if C2 had been live during the run.

Caveats
-------
- Games with only 1 persisted run can't be rescued; they keep stored GE.
- Games where the stored GE is 0 (seat_balance hard-zeroed at < 0.1) stay
  at 0 — averaging across PPO seeds can't rescue structural seat bias.
- partial_orig == 0 from collapsed depth/non_triv falls back to stored GE
  with delta = 0 to keep the table well-defined.
"""

from __future__ import annotations

import json
import math
import sqlite3
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/Users/jamesbrowne/aigame")
sys.path.insert(0, str(ROOT))

from metrics.scoring import (  # noqa: E402
    _compute_auc,
    _estimate_plateau_fraction,
)

OUT = ROOT / "experiments" / "r18_volatility"

SUBSTRATES = [
    ("vicsek",   1.465, "genesis_v2_run18_vicsek.db"),
    ("triangle", 1.585, "genesis_v2_run18_triangle.db"),
    ("carpet",   1.893, "genesis_v2_run18_carpet.db"),
    ("grid",     2.000, "genesis_v2_run18_grid.db"),
    ("menger",   2.727, "genesis_v2_run18_menger.db"),
]

# Default weights from MetricsConfig (aigame/config.py).
W_DEPTH = 1.0
W_DIVERSITY = 0.5
W_SIMPLICITY = 1.0
EPS = 1e-8


# ----------------------------- scorer math -----------------------------
# Inlined to avoid instantiating GoEssenceScorer (and its tracked depth
# defaults) thousands of times. Identical math to metrics/scoring.py.

def strategic_depth(curve: list[tuple[int, float]]) -> float:
    if not curve or len(curve) < 2:
        return 0.0
    pts = sorted(curve, key=lambda p: p[0])
    eps = np.array([p[0] for p in pts], dtype=np.float64)
    wrs = np.clip(np.array([p[1] for p in pts], dtype=np.float64), 0.0, 1.0)
    auc = _compute_auc(eps, wrs)
    plat = _estimate_plateau_fraction(eps, wrs)
    mid = len(wrs) // 2
    if mid > 0:
        first = float(np.mean(wrs[:mid]))
        second = float(np.mean(wrs[mid:]))
        late = max(0.0, second - first)
        late = min(late / 0.5, 1.0)
    else:
        late = 0.0
    return float(np.clip((auc + plat + late) / 3.0, 0.0, 1.0))


def non_triviality(tvr: float, p0: float) -> float:
    if not math.isfinite(tvr):
        tvr = 0.0
    if not math.isfinite(p0):
        p0 = 0.5
    tvr = float(np.clip(tvr, 0.0, 1.0))
    p0 = float(np.clip(p0, 0.0, 1.0))
    balance_factor = 1.0 - 2.0 * abs(p0 - 0.5)
    edge = max(0.0, tvr - 0.5) * 2.0
    competence = float(edge ** 0.5)
    return float(np.clip(balance_factor * competence, 0.0, 1.0))


def composite_score(simplicity: float, depth: float, non_triv: float,
                    diversity: float) -> float:
    diversity_factor = 0.2 + 0.8 * float(np.clip(diversity, 0.0, 1.0))
    non_triv_factor = 0.1 + 0.9 * float(np.clip(non_triv, 0.0, 1.0))
    num = (
        max(depth, 0.0) ** W_DEPTH
        * (diversity_factor ** W_DIVERSITY)
        * non_triv_factor
    )
    denom = (1.0 - float(np.clip(simplicity, 0.0, 1.0))) ** W_SIMPLICITY + EPS
    raw = num / denom
    return float(np.clip(raw / (raw + 1.0), 0.0, 1.0))


def length_factor(avg_len: float) -> float:
    if avg_len is None or not math.isfinite(avg_len):
        return 1.0
    if avg_len >= 15.0:
        return 1.0
    return max(0.2, 0.2 + 0.8 * (avg_len / 15.0))


# --------------------------- DB extraction ----------------------------

def fetch_runs(db_path: Path) -> dict[str, dict]:
    """Return {game_id: {scores: {...}, runs: [{...}, ...]}} for all games
    with >=1 persisted training_run."""
    con = sqlite3.connect(db_path)
    by_gid: dict[str, dict] = {}
    rows = con.execute("""
        SELECT t.game_id, t.run_id, t.run_seed, t.learning_curve,
               t.trained_vs_random, t.final_winrate, t.avg_game_length,
               g.generation, g.rule_complexity,
               s.rule_simplicity, s.strategic_depth, s.non_triviality,
               s.strategic_diversity, s.go_essence
        FROM training_runs t
        JOIN games g ON g.game_id = t.game_id
        LEFT JOIN scores s ON s.game_id = t.game_id
        ORDER BY t.game_id, t.run_id
    """).fetchall()
    for (gid, run_id, seed, lc_json, tvr, p0, alen,
         gen, complexity, simp, dep, ntr, div, ge) in rows:
        try:
            curve = [(int(p[0]), float(p[1])) for p in json.loads(lc_json)]
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
        if gid not in by_gid:
            by_gid[gid] = {
                "scores": {
                    "rule_simplicity": float(simp) if simp is not None else 0.0,
                    "strategic_depth": float(dep) if dep is not None else 0.0,
                    "non_triviality": float(ntr) if ntr is not None else 0.0,
                    "strategic_diversity": float(div) if div is not None else 0.5,
                    "go_essence": float(ge) if ge is not None else 0.0,
                },
                "generation": int(gen) if gen is not None else -1,
                "rule_complexity": int(complexity) if complexity is not None else 0,
                "runs": [],
            }
        by_gid[gid]["runs"].append({
            "run_id": int(run_id),
            "seed": int(seed) if seed is not None else 0,
            "curve": curve,
            "tvr": float(tvr) if tvr is not None and math.isfinite(tvr) else 0.0,
            "p0": float(p0) if p0 is not None and math.isfinite(p0) else 0.5,
            "alen": float(alen) if alen is not None and math.isfinite(alen) else 0.0,
        })
    con.close()
    return by_gid


# ------------------------------- rescue -------------------------------

def average_curves(curves: list[list[tuple[int, float]]]) -> list[tuple[int, float]]:
    if not curves:
        return []
    base_eps = [ep for ep, _ in curves[0]]
    n_pts = len(base_eps)
    sums = [0.0] * n_pts
    n_used = 0
    for c in curves:
        if len(c) != n_pts:
            continue
        for i, (_ep, wr) in enumerate(c):
            sums[i] += float(wr)
        n_used += 1
    if n_used == 0:
        return list(curves[0])
    return [(base_eps[i], sums[i] / n_used) for i in range(n_pts)]


def rescue_one(game: dict) -> dict:
    """Compute rescued GE for a single game."""
    s = game["scores"]
    runs = game["runs"]
    n = len(runs)
    record = {
        "n_runs": n,
        "stored_ge": s["go_essence"],
        "rescued_ge": s["go_essence"],
        "delta": 0.0,
        "ratio": 1.0,
        "depth_orig": s["strategic_depth"],
        "depth_resc": s["strategic_depth"],
        "tvr_orig": runs[0]["tvr"] if runs else 0.0,
        "tvr_resc": runs[0]["tvr"] if runs else 0.0,
        "rescuable": False,
    }
    if n < 2 or s["go_essence"] <= 0.0:
        return record

    simplicity = s["rule_simplicity"]
    diversity = s["strategic_diversity"]

    # Original partial composite (run-0 inputs only).
    r0 = runs[0]
    depth_orig = strategic_depth(r0["curve"])
    nt_orig = non_triviality(r0["tvr"], r0["p0"])
    raw_orig = composite_score(simplicity, depth_orig, nt_orig, diversity)
    partial_orig = raw_orig * length_factor(r0["alen"])

    # Rescued partial composite (averaged across all N runs).
    avg_curve = average_curves([r["curve"] for r in runs])
    avg_tvr = sum(r["tvr"] for r in runs) / n
    avg_p0 = sum(r["p0"] for r in runs) / n
    avg_alen = sum(r["alen"] for r in runs) / n
    depth_resc = strategic_depth(avg_curve)
    nt_resc = non_triviality(avg_tvr, avg_p0)
    raw_resc = composite_score(simplicity, depth_resc, nt_resc, diversity)
    partial_resc = raw_resc * length_factor(avg_alen)

    if partial_orig <= EPS:
        return record

    ratio = partial_resc / partial_orig
    rescued_ge = float(np.clip(s["go_essence"] * ratio, 0.0, 1.0))
    record.update({
        "rescued_ge": rescued_ge,
        "delta": rescued_ge - s["go_essence"],
        "ratio": ratio,
        "depth_orig": depth_orig,
        "depth_resc": depth_resc,
        "tvr_orig": r0["tvr"],
        "tvr_resc": avg_tvr,
        "rescuable": True,
    })
    return record


def rescue_substrate(name: str, dim: float, db_filename: str) -> list[dict]:
    db_path = ROOT / db_filename
    if not db_path.exists():
        print(f"  WARN: {db_path} missing, skipping {name}", file=sys.stderr)
        return []
    games = fetch_runs(db_path)
    out = []
    for gid, g in games.items():
        rec = rescue_one(g)
        rec.update({
            "substrate": name,
            "dim": dim,
            "game_id": gid,
            "generation": g["generation"],
        })
        out.append(rec)
    return out


# -------------------------------- main --------------------------------

def main() -> int:
    all_records: list[dict] = []
    for name, dim, db_filename in SUBSTRATES:
        print(f"rescuing {name} ({db_filename})...")
        recs = rescue_substrate(name, dim, db_filename)
        rescuable = sum(1 for r in recs if r["rescuable"])
        nonzero_delta = sum(1 for r in recs if r["rescuable"] and abs(r["delta"]) > 1e-6)
        print(f"  {len(recs)} games | {rescuable} rescuable | "
              f"{nonzero_delta} with non-zero delta")
        all_records.extend(recs)

    # Write per-game CSV.
    csv_path = OUT / "phase_b_rescue_per_game.csv"
    with csv_path.open("w") as f:
        f.write("substrate,dim,game_id,generation,n_runs,stored_ge,rescued_ge,"
                "delta,ratio,depth_orig,depth_resc,tvr_orig,tvr_resc,rescuable\n")
        for r in all_records:
            f.write(f"{r['substrate']},{r['dim']:.3f},{r['game_id']},"
                    f"{r['generation']},{r['n_runs']},"
                    f"{r['stored_ge']:.6f},{r['rescued_ge']:.6f},"
                    f"{r['delta']:+.6f},{r['ratio']:.4f},"
                    f"{r['depth_orig']:.4f},{r['depth_resc']:.4f},"
                    f"{r['tvr_orig']:.4f},{r['tvr_resc']:.4f},"
                    f"{int(r['rescuable'])}\n")
    print(f"\nwrote {csv_path}")

    # Per-substrate top-10 comparison.
    print("\n" + "=" * 78)
    print("Per-substrate top-10: stored vs rescued")
    print("=" * 78)
    for name, _dim, _db in SUBSTRATES:
        sub = [r for r in all_records if r["substrate"] == name]
        if not sub:
            continue
        by_stored = sorted(sub, key=lambda x: -x["stored_ge"])[:10]
        by_rescued = sorted(sub, key=lambda x: -x["rescued_ge"])[:10]
        stored_ids = [r["game_id"] for r in by_stored]
        rescued_ids = [r["game_id"] for r in by_rescued]
        overlap = len(set(stored_ids) & set(rescued_ids))
        print(f"\n{name} (top-10 overlap: {overlap}/10)")
        print(f"  {'rank':>4} | {'stored top-10':>50} | {'rescued top-10':>50}")
        for i in range(10):
            so = by_stored[i] if i < len(by_stored) else None
            re = by_rescued[i] if i < len(by_rescued) else None
            sl = (f"{so['game_id']} ge={so['stored_ge']:.4f} "
                  f"n={so['n_runs']}") if so else ""
            rl = (f"{re['game_id']} ge={re['rescued_ge']:.4f} "
                  f"({re['delta']:+.4f})") if re else ""
            print(f"  {i+1:>4} | {sl:>50} | {rl:>50}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
