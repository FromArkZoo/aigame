"""R20 S3 — champion-finalization tier (15-seed re-evaluation).

Per R19_postmortem.md § Champion-finalization: at end-of-run, re-score the
top-K candidates per substrate with 5 fresh trains × num_independent_runs=3
C2 averaging = 15 unique PPO seeds total per game. Drives σ from ~0.09 to
~0.04 on menger; R20 leaderboard claims then have honest measurement bars.

Generalizes experiments/r18_noise_floor/run_noise_floor.py by accepting an
arbitrary list of (substrate, db_path, game_id) triples instead of the
hardcoded STABLE_TOPS list. Two ways to drive it:

    1. Auto-extract top-K from a single substrate DB:
       --auto <substrate>:<db_path>:<K>

    2. Explicit list via JSON config:
       --games-json finalization_input.json

       where the JSON is:
       [
         {"substrate": "menger", "db": "genesis_v2_run20_menger.db",
          "game_id": "abc123", "original_ge": 0.3293},
         ...
       ]

Output:
  - sidecar DB (default `r20_finalization.db`) with per-rerun rows
  - per-run CSV
  - markdown summary with mean/std/n=5 per game and original-vs-finalized
    rank comparison

Naming: outer-rerun seeds are namespaced as
`:finalization:<rerun_idx>:<run_within>` (distinct from `:noisefloor:` and
production R20 seeds).
"""

from __future__ import annotations

import argparse
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
import run as run_module  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("r20_finalization")


NUM_RERUNS = 5            # outer reruns per game; each does 3 internal C2 seeds
TRAINING_BUDGET = 5000    # match production R20; override per-call if needed
DEFAULT_SIDECAR_DB = HERE / "r20_finalization.db"
DEFAULT_RESULTS_CSV = HERE / "finalization_per_run.csv"
DEFAULT_SUMMARY_MD = HERE / "finalization_summary.md"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--games-json", type=Path,
        help="JSON config: list of {substrate, db, game_id, original_ge?, dim?}",
    )
    p.add_argument(
        "--auto", action="append", default=[],
        help=(
            "Auto-extract top-K from a single substrate DB. "
            "Format: <substrate>:<db_path>:<K>. May be repeated for multi-substrate runs."
        ),
    )
    p.add_argument("--reruns", type=int, default=NUM_RERUNS,
                   help=f"Outer reruns per game (default {NUM_RERUNS}).")
    p.add_argument("--budget", type=int, default=TRAINING_BUDGET,
                   help=f"Training budget per PPO seed (default {TRAINING_BUDGET}).")
    p.add_argument("--sidecar-db", type=Path, default=DEFAULT_SIDECAR_DB)
    p.add_argument("--results-csv", type=Path, default=DEFAULT_RESULTS_CSV)
    p.add_argument("--summary-md", type=Path, default=DEFAULT_SUMMARY_MD)
    p.add_argument(
        "--only-rerun-idx", nargs="*", type=int,
        help="If set, run only these specific rerun indices.",
    )
    p.add_argument(
        "--bypass-validation", action="store_true",
        help="Set game.metadata.seeded_from to skip validate_game's 5-rollout check. "
             "Champion games passed evolution-time validation; we don't want fresh "
             "PPO seeds to fail the sanity check and contaminate the noise estimate.",
    )
    p.add_argument(
        "--upsert", action="store_true",
        help="Upsert into the sidecar DB instead of recreating it.",
    )
    p.add_argument(
        "--smoke", action="store_true",
        help="Pipeline check: 1 game × 1 rerun × 200 ep. Requires --auto or --games-json.",
    )
    return p.parse_args()


def load_games_from_config(path: Path) -> list[dict]:
    with open(path) as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise SystemExit(f"{path}: expected a JSON list, got {type(data).__name__}")
    for entry in data:
        if "substrate" not in entry or "db" not in entry or "game_id" not in entry:
            raise SystemExit(
                f"{path}: each entry needs substrate/db/game_id keys; got {entry}"
            )
    return data


def auto_extract_top_k(spec: str) -> list[dict]:
    """Parse <substrate>:<db_path>:<K> and pull top-K games by go_essence."""
    parts = spec.split(":")
    if len(parts) != 3:
        raise SystemExit(
            f"--auto needs <substrate>:<db>:<K>, got {spec!r}"
        )
    substrate, db_path, k_str = parts
    k = int(k_str)
    full_db = ROOT / db_path if not Path(db_path).is_absolute() else Path(db_path)
    if not full_db.exists():
        raise SystemExit(f"DB not found: {full_db}")
    con = sqlite3.connect(str(full_db))
    con.row_factory = sqlite3.Row
    rows = con.execute(
        """
        SELECT game_id, go_essence
        FROM scores
        ORDER BY go_essence DESC
        LIMIT ?
        """,
        (k,),
    ).fetchall()
    con.close()
    if not rows:
        raise SystemExit(f"No scored games in {full_db}")
    return [
        {
            "substrate": substrate,
            "db": str(db_path),
            "game_id": r["game_id"],
            "original_ge": float(r["go_essence"]),
        }
        for r in rows
    ]


def load_game(db_path: str, game_id: str) -> GameDefV2:
    full_db = ROOT / db_path if not Path(db_path).is_absolute() else Path(db_path)
    con = sqlite3.connect(str(full_db))
    con.row_factory = sqlite3.Row
    row = con.execute(
        "SELECT rule_representation FROM games WHERE game_id = ?", (game_id,)
    ).fetchone()
    con.close()
    if row is None:
        raise SystemExit(f"game {game_id} not found in {db_path}")
    return GameDefV2.from_dict(json.loads(row["rule_representation"]))


def patched_seed_for_rerun(rerun_idx: int):
    """Replacement for `run.deterministic_run_seed` that namespaces seeds by
    `:finalization:<rerun_idx>` so the 3 internal PPO seeds across the 5
    outer reruns produce 15 disjoint values per game.
    """
    def patched(game_id: str, run_idx: int = 0) -> int:
        s = f"{game_id}:finalization:{rerun_idx}:{run_idx}".encode("utf-8")
        return int(hashlib.md5(s).hexdigest()[:8], 16)
    return patched


def init_sidecar_db(path: Path, fresh: bool = True) -> sqlite3.Connection:
    if fresh and path.exists():
        path.unlink()
    con = sqlite3.connect(str(path))
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS rerun_scores (
            substrate TEXT, game_id TEXT, rerun_idx INTEGER,
            go_essence REAL, strategic_depth REAL, non_triviality REAL,
            strategic_diversity REAL, rule_simplicity REAL,
            wallclock_seconds REAL, ts TEXT,
            original_ge REAL,
            PRIMARY KEY (game_id, rerun_idx)
        )
        """
    )
    con.commit()
    return con


def make_config(budget: int) -> GenesisConfig:
    cfg = GenesisConfig()
    cfg.training.training_budget = budget
    # num_independent_runs default = 3, matches production C2.
    return cfg


def run_finalization(
    games: list[dict],
    *,
    reruns: int,
    budget: int,
    sidecar_path: Path,
    only_rerun_idx: list[int] | None,
    bypass_validation: bool,
    upsert: bool,
) -> None:
    sidecar = init_sidecar_db(sidecar_path, fresh=not upsert)
    cfg = make_config(budget)
    scorer = GoEssenceScorer(cfg.metrics)
    rerun_indices = only_rerun_idx if only_rerun_idx else list(range(reruns))

    for entry in games:
        substrate = entry["substrate"]
        gid = entry["game_id"]
        original_ge = entry.get("original_ge")
        logger.info(
            "=== %s game %s (orig_GE=%s) ===",
            substrate, gid,
            f"{original_ge:.4f}" if original_ge is not None else "?",
        )
        game = load_game(entry["db"], gid)

        if bypass_validation:
            game.metadata["seeded_from"] = "finalization_bypass_validation"

        for k in rerun_indices:
            t0 = time.time()
            original_seed_fn = run_module.deterministic_run_seed
            run_module.deterministic_run_seed = patched_seed_for_rerun(k)
            try:
                primary_seed = run_module.deterministic_run_seed(gid, run_idx=0)
                cfg.tracking.db_path = ":memory:"
                tmp_db = GenesisDB(cfg.tracking)
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
                    population_fingerprints=None,
                )
            finally:
                run_module.deterministic_run_seed = original_seed_fn
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
                """
                INSERT OR REPLACE INTO rerun_scores
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?)
                """,
                (
                    substrate, gid, k, ge, depth, ntriv, div, simp,
                    wall, original_ge,
                ),
            )
            sidecar.commit()

    sidecar.close()


def write_csv_and_summary(
    sidecar_path: Path, csv_path: Path, summary_path: Path,
) -> None:
    con = sqlite3.connect(str(sidecar_path))
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT * FROM rerun_scores ORDER BY substrate, game_id, rerun_idx"
    ).fetchall()
    con.close()

    csv_lines = [
        "substrate,game_id,rerun_idx,go_essence,strategic_depth,non_triviality,"
        "strategic_diversity,rule_simplicity,wallclock_seconds,original_ge",
    ]
    for r in rows:
        original_ge_str = f"{r['original_ge']:.6f}" if r["original_ge"] is not None else ""
        csv_lines.append(
            f"{r['substrate']},{r['game_id']},{r['rerun_idx']},"
            f"{r['go_essence']:.6f},{r['strategic_depth']:.6f},"
            f"{r['non_triviality']:.6f},{r['strategic_diversity']:.6f},"
            f"{r['rule_simplicity']:.6f},{r['wallclock_seconds']:.1f},"
            f"{original_ge_str}"
        )
    csv_path.write_text("\n".join(csv_lines) + "\n")

    by_game: dict[tuple[str, str], list[float]] = {}
    original_by_game: dict[tuple[str, str], float | None] = {}
    for r in rows:
        key = (r["substrate"], r["game_id"])
        by_game.setdefault(key, []).append(r["go_essence"])
        original_by_game[key] = r["original_ge"]

    lines = [
        "# R20 champion-finalization results",
        "",
        f"Per-game GE distribution from {NUM_RERUNS} outer reruns × "
        f"`num_independent_runs=3` C2 averaging = 15 unique PPO seeds per game.",
        "",
        "| Substrate | Game | original_GE | n | mean GE | std GE | min | max | range | Δ vs original |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    rows_for_table = []
    for (substrate, gid), ges in by_game.items():
        n = len(ges)
        m = sum(ges) / n
        v = sum((g - m) ** 2 for g in ges) / max(n - 1, 1)
        s = v ** 0.5
        orig = original_by_game[(substrate, gid)]
        delta = (m - orig) if orig is not None else None
        rows_for_table.append(
            (substrate, gid, orig, n, m, s, min(ges), max(ges),
             max(ges) - min(ges), delta)
        )
    rows_for_table.sort(key=lambda x: (x[0], -x[4]))  # by substrate, then mean DESC
    for substrate, gid, orig, n, m, s, lo, hi, rng, delta in rows_for_table:
        orig_s = f"{orig:.4f}" if orig is not None else "—"
        delta_s = f"{delta:+.4f}" if delta is not None else "—"
        lines.append(
            f"| {substrate} | `{gid}` | {orig_s} | {n} "
            f"| {m:.4f} | {s:.4f} | {lo:.4f} | {hi:.4f} | {rng:.4f} | {delta_s} |"
        )

    lines += [
        "",
        "## Read",
        "- `std GE` is the post-15-seed measurement noise. Goal: < 0.04 on "
        "menger, < 0.03 on carpet (vs Phase A under-estimates of 0.014/0.155).",
        "- `Δ vs original` shows where the production-stack 3-seed scoring "
        "was over- or under-estimating. Large positive Δ = the original was "
        "an unlucky-seed underestimate (carpet's Phase B finding).",
        "- Cross-substrate comparisons are honest only when |Δmean| > "
        "max(σ_a, σ_b). Annotate substrate-vs-substrate claims accordingly.",
    ]
    summary_path.write_text("\n".join(lines) + "\n")


def main() -> int:
    args = parse_args()

    games: list[dict] = []
    if args.games_json:
        games.extend(load_games_from_config(args.games_json))
    for spec in args.auto:
        games.extend(auto_extract_top_k(spec))
    if not games:
        raise SystemExit("No games specified — pass --games-json or --auto.")

    reruns = args.reruns
    budget = args.budget
    if args.smoke:
        games = games[:1]
        reruns = 1
        budget = 200
        logger.info("SMOKE MODE — 1 game × 1 rerun × 200 ep")

    run_finalization(
        games,
        reruns=reruns,
        budget=budget,
        sidecar_path=args.sidecar_db,
        only_rerun_idx=args.only_rerun_idx,
        bypass_validation=args.bypass_validation,
        upsert=args.upsert,
    )
    write_csv_and_summary(args.sidecar_db, args.results_csv, args.summary_md)
    logger.info("DONE — results at %s", args.sidecar_db)
    return 0


if __name__ == "__main__":
    sys.exit(main())
