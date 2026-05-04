"""R18 noise-floor experiment — measure post-C2 GE std on stable-top games.

Why: Phase A's pge_std is a lower bound on real noise; Phase B's rescue
gives one corrected mean per game but no distribution. To say "the chart's
±0.014 menger error bar is real and the ±0.155 carpet bar collapses under
C2," we need fresh-train distributions, not re-derivations.

Method
------
For each of the 5 R18 stable-top games, do 5 outer reruns. Each rerun
fresh-trains 3 PPO agents (matching production num_independent_runs=3),
applies C2 multi-seed averaging on the inputs, and runs the full Go-Essence
scorer including cross-play diversity. Outer-rerun seeds are derived from
md5(game_id + ":noisefloor:" + rerun_idx + ":" + run_within), so all 15
seeds per game are unique.

Result: per game (mean, std, min, max) over 5 fresh-train GEs. The std is
the post-C2 noise floor — the bar all R18/R19 GE comparisons must clear.

Sidecar DB: r18_noise_floor.db. Original substrate DBs are NEVER written
to — we read game genotypes from them and write a temp in-memory DB during
each train_and_evaluate call to avoid polluting them.
"""
from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from config import GenesisConfig  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from metrics.scoring import GoEssenceScorer  # noqa: E402
from tracking.database import GenesisDB  # noqa: E402
import run as run_module  # noqa: E402  -- lets us monkey-patch deterministic_run_seed

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("noise_floor")

# Stable tops per substrate, as identified in memory and confirmed by extract_data.py.
STABLE_TOPS = [
    {"substrate": "vicsek",   "dim": 1.465, "db": "genesis_v2_run18_vicsek.db",   "game_id": "1e11adebcc35"},
    {"substrate": "triangle", "dim": 1.585, "db": "genesis_v2_run18_triangle.db", "game_id": "558be82199a8"},
    {"substrate": "carpet",   "dim": 1.893, "db": "genesis_v2_run18_carpet.db",   "game_id": "8776b2026957"},
    {"substrate": "grid",     "dim": 2.000, "db": "genesis_v2_run18_grid.db",     "game_id": "ab7270a81cd6"},
    {"substrate": "menger",   "dim": 2.727, "db": "genesis_v2_run18_menger.db",   "game_id": "0f5e931fa3e1"},
]

NUM_RERUNS = 5                     # outer reruns per game; std measured across these
TRAINING_BUDGET = 5000             # match R18 (was 5000 across all substrates)
SIDECAR_DB = HERE / "r18_noise_floor.db"
RESULTS_CSV = HERE / "noise_floor_per_run.csv"
SUMMARY_MD = HERE / "noise_floor_summary.md"


def parse_args():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true", help="1 game × 1 rerun × 200 ep — pipeline check")
    p.add_argument("--substrates", nargs="*", help="restrict to these substrate keys")
    p.add_argument("--reruns", type=int, default=NUM_RERUNS)
    p.add_argument("--budget", type=int, default=TRAINING_BUDGET)
    p.add_argument(
        "--only-rerun-idx", nargs="*", type=int,
        help="if set, run only these specific rerun indices (e.g. --only-rerun-idx 1 3 4)",
    )
    p.add_argument(
        "--bypass-validation", action="store_true",
        help="set game.metadata.seeded_from so train_and_evaluate skips validate_game. "
             "These games already passed validation in R18 — random PPO seeds occasionally "
             "fail the 5-rollout sanity check, contaminating fresh-train noise with validation noise.",
    )
    p.add_argument(
        "--upsert", action="store_true",
        help="instead of recreating the sidecar DB, upsert into the existing one (useful for redoing specific reruns)",
    )
    return p.parse_args()


def load_game(db_path: str, game_id: str) -> GameDefV2:
    con = sqlite3.connect(str(ROOT / db_path))
    con.row_factory = sqlite3.Row
    row = con.execute(
        "SELECT rule_representation FROM games WHERE game_id = ?", (game_id,)
    ).fetchone()
    con.close()
    if row is None:
        raise SystemExit(f"game {game_id} not found in {db_path}")
    return GameDefV2.from_dict(json.loads(row["rule_representation"]))


def patched_seed_for_rerun(rerun_idx: int):
    """Return a `deterministic_run_seed` replacement that namespaces seeds
    by `:noisefloor:<rerun_idx>` so each outer rerun's 3 internal PPO seeds
    are disjoint from every other rerun and from production R18 seeds.
    """
    def patched(game_id: str, run_idx: int = 0) -> int:
        s = f"{game_id}:noisefloor:{rerun_idx}:{run_idx}".encode("utf-8")
        return int(hashlib.md5(s).hexdigest()[:8], 16)
    return patched


def init_sidecar_db(path: Path, fresh: bool = True) -> sqlite3.Connection:
    if fresh and path.exists():
        path.unlink()
    con = sqlite3.connect(str(path))
    con.execute("""
        CREATE TABLE IF NOT EXISTS rerun_scores (
            substrate TEXT, dim REAL, game_id TEXT, rerun_idx INTEGER,
            go_essence REAL, strategic_depth REAL, non_triviality REAL,
            strategic_diversity REAL, rule_simplicity REAL,
            wallclock_seconds REAL, ts TEXT,
            PRIMARY KEY (game_id, rerun_idx)
        )
    """)
    con.commit()
    return con


def make_config() -> GenesisConfig:
    cfg = GenesisConfig()
    cfg.training.training_budget = TRAINING_BUDGET
    # num_independent_runs default = 3, matches production C2.
    return cfg


def main():
    args = parse_args()

    games = STABLE_TOPS
    reruns = args.reruns
    budget = args.budget
    if args.smoke:
        games = [STABLE_TOPS[3]]  # grid (smallest substrate, fastest train)
        reruns = 1
        budget = 200
        logger.info("SMOKE MODE — 1 game × 1 rerun × 200 ep")
    if args.substrates:
        games = [g for g in games if g["substrate"] in args.substrates]

    sidecar = init_sidecar_db(SIDECAR_DB, fresh=not args.upsert)

    cfg = make_config()
    cfg.training.training_budget = budget
    scorer = GoEssenceScorer(cfg.metrics)

    rerun_indices = args.only_rerun_idx if args.only_rerun_idx else list(range(reruns))

    for game_meta in games:
        substrate = game_meta["substrate"]
        gid = game_meta["game_id"]
        logger.info("=== %s top game %s (dim %.3f) ===", substrate, gid, game_meta["dim"])
        game = load_game(game_meta["db"], gid)

        if args.bypass_validation:
            # Mark as seeded so train_and_evaluate_game's quick-validate gate is skipped.
            # These games already passed validation in R18 — re-validating with random
            # PPO seeds is not what we're trying to measure.
            game.metadata["seeded_from"] = "noise_floor_bypass_validation"

        for k in rerun_indices:
            t0 = time.time()
            # Monkey-patch deterministic_run_seed for the duration of this call so
            # all 3 internal PPO seeds get a fresh namespace.
            original = run_module.deterministic_run_seed
            run_module.deterministic_run_seed = patched_seed_for_rerun(k)
            try:
                primary_seed = run_module.deterministic_run_seed(gid, run_idx=0)
                # Fresh in-memory DB per call: train_and_evaluate writes training_runs
                # and scores rows; we don't want them in any persistent DB.
                cfg.tracking.db_path = ":memory:"
                tmp_db = GenesisDB(cfg.tracking)
                # Insert the game so insert_training_run's FK is satisfied.
                tmp_db.insert_game(
                    game_id=game.game_id,
                    generation=0,
                    parent_ids=[],
                    state_dim=game.state_dim,
                    num_actions=game.num_actions,
                    num_players=game.num_players,
                    observation_type=getattr(game, "observation_type", "full"),
                    rule_representation=game.to_dict(),
                    rule_complexity=game.total_complexity(),
                )
                scores = run_module.train_and_evaluate_game(
                    game, cfg, scorer, tmp_db, primary_seed,
                    population_fingerprints=None,  # no diversity-against-other-games
                )
            finally:
                run_module.deterministic_run_seed = original
            wall = time.time() - t0

            ge = scores["go_essence"]
            depth = scores["strategic_depth"]
            ntriv = scores["non_triviality"]
            div = scores["strategic_diversity"]
            simp = scores["rule_simplicity"]
            logger.info(
                "  rerun %d: GE=%.4f depth=%.3f non_triv=%.3f div=%.3f simp=%.3f (%.1fs)",
                k, ge, depth, ntriv, div, simp, wall,
            )
            sidecar.execute(
                "INSERT OR REPLACE INTO rerun_scores VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))",
                (substrate, game_meta["dim"], gid, k, ge, depth, ntriv, div, simp, wall),
            )
            sidecar.commit()

    sidecar.close()
    write_csv_and_summary()
    logger.info("DONE — results at %s", SIDECAR_DB)


def write_csv_and_summary():
    """Re-emit the CSV and markdown summary from the sidecar DB."""
    con = sqlite3.connect(str(SIDECAR_DB))
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT * FROM rerun_scores ORDER BY dim, game_id, rerun_idx"
    ).fetchall()
    con.close()
    csv_lines = ["substrate,dim,game_id,rerun_idx,go_essence,strategic_depth,non_triviality,strategic_diversity,rule_simplicity,wallclock_seconds"]
    for r in rows:
        csv_lines.append(
            f"{r['substrate']},{r['dim']},{r['game_id']},{r['rerun_idx']},"
            f"{r['go_essence']:.6f},{r['strategic_depth']:.6f},{r['non_triviality']:.6f},"
            f"{r['strategic_diversity']:.6f},{r['rule_simplicity']:.6f},{r['wallclock_seconds']:.1f}"
        )
    RESULTS_CSV.write_text("\n".join(csv_lines) + "\n")
    write_summary()


def write_summary():
    """Compute per-game (mean, std, min, max) and emit summary.md."""
    con = sqlite3.connect(str(SIDECAR_DB))
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT substrate, dim, game_id, rerun_idx, go_essence "
        "FROM rerun_scores ORDER BY dim, game_id, rerun_idx"
    ).fetchall()
    con.close()

    by_game = {}
    for r in rows:
        key = (r["substrate"], r["dim"], r["game_id"])
        by_game.setdefault(key, []).append(r["go_essence"])

    lines = [
        "# R18 noise-floor results",
        "",
        f"Per-game GE distribution from {NUM_RERUNS} fresh PPO retrains "
        f"(each retrain = num_independent_runs={3}, training_budget={TRAINING_BUDGET}).",
        "",
        "Comparing against the substrate-comparison figure's reported error bars:",
        "",
        "| Substrate | Dim | Game | Phase A σ (chart) | n | mean GE | std GE | min | max | range |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    chart_sigma = {"vicsek": 0.171, "triangle": 0.018, "carpet": 0.155, "grid": 0.102, "menger": 0.014}
    for (substrate, dim, gid), ges in sorted(by_game.items(), key=lambda x: x[0][1]):
        n = len(ges)
        m = sum(ges) / n
        v = sum((g - m) ** 2 for g in ges) / max(n - 1, 1)
        s = v ** 0.5
        lines.append(
            f"| {substrate} | {dim} | `{gid}` | {chart_sigma[substrate]:.3f} "
            f"| {n} | {m:.4f} | {s:.4f} | {min(ges):.4f} | {max(ges):.4f} | {max(ges) - min(ges):.4f} |"
        )
    lines += [
        "",
        "**Read:** if `std GE` is materially lower than `Phase A σ (chart)` for the noisy "
        "substrates (carpet/grid/vicsek), C2 multi-seed averaging is doing its job and the "
        "chart's worst error bars over-state real noise. If `std GE` ≈ `Phase A σ (chart)`, "
        "the chart's bars are honest and most rankings are noise.",
        "",
        "**Decision criteria:**",
        "- carpet std > 0.10 → carpet's rescued 0.347 is single-rescue noise, drops out",
        "- carpet std < 0.05 AND mean > 0.20 → thesis breaks (carpet at dim 1.893 outperforms menger at 2.727)",
        "- menger std stays ~0.014: chart's reliability tags hold",
    ]
    SUMMARY_MD.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
