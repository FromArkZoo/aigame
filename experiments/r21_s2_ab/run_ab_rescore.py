"""R21 S2 A/B re-score — validate planning-horizon-augmented GE on the R20 slate.

R21 plan § S2 (R21_plan.md:120-123) calls for an A/B calibration step before
launching R21 evolution: re-score the R20 finalization slate (9 games) under
planning-horizon-augmented GE and check three criteria.

Pipeline per game:

  1. Load game definition from the per-substrate R20 DB.
  2. Read stored component scores (simplicity, depth, non-trivality, diversity)
     and the original ``go_essence`` from the ``scores`` table.
  3. Train a fresh PPO policy at ``--budget`` episodes, seed 42.
  4. Run ``metrics.inference_probe.planning_horizon_from_rollouts(game,
     [agents[0], agents[1]], n_rollouts=20)``.
  5. Recompute ``composite_score(...)`` with ``MetricsConfig.planning_horizon_weight
     = depth_weight * --w-planning-ratio`` (default 0.5 per the plan).
  6. Write per-game record to the sidecar DB + the markdown A/B table.

Pass criteria (R21_plan.md § S2):
  G4.1 -- Byte-identical trio (``a6385db22c0b`` / ``b160b1f55378`` /
          ``d1dbc6568fc7``) compress to within Delta < 0.05 on augmented GE.
  G4.2 -- Depth record ``5f5c72e15220`` reaches top-2 by augmented GE.
  G4.3 -- Pie game  ``625bfc1f3f49`` reaches top-2 by augmented GE.

Caching: per-game ``planning_horizon`` values are cached in the sidecar DB
keyed by (game_id, budget, seed). With ``--use-cache`` the harness skips
training and reuses cached probes, which makes bisecting ``w_planning``
cheap (~seconds rather than ~hour).
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from config import MetricsConfig, TrainingConfig  # noqa: E402
from experiments.r20_finalization.finalize_champions import load_game  # noqa: E402
from metrics.inference_probe import planning_horizon_from_rollouts  # noqa: E402
from metrics.scoring import GoEssenceScorer  # noqa: E402
from training.trainer import SelfPlayTrainer  # noqa: E402


DEFAULT_SLATE = ROOT / "experiments/r20_finalization/r20_eval_slate.json"
DEFAULT_DB = HERE / "r20_ab_rescore.db"
DEFAULT_MD = HERE / "r20_ab_rescore.md"
DEFAULT_BUDGET = 10000  # matches R20 menger/grid budget; carpet R20 used 15000 but
                        # for an internal A/B the consistent budget across games is
                        # the right tradeoff.
DEFAULT_SEED = 42
DEFAULT_ROLLOUTS = 20
DEFAULT_W_PLANNING_RATIO = 0.5  # w_planning = depth_weight * ratio; plan starts at 0.5.


# Identifiers used by the pass criteria.
BYTE_IDENTICAL_TRIO = ("a6385db22c0b", "b160b1f55378", "d1dbc6568fc7")
TRIO_DELTA_MAX = 0.05
TOP2_GAMES = ("5f5c72e15220", "625bfc1f3f49")


@dataclass
class GameRecord:
    substrate: str
    db: str
    game_id: str
    original_ge: float       # from DB scores.go_essence (incl. evaluate_game penalties)
    baseline_ge: float       # composite_score with w_planning=0 (no penalties)
    simplicity: float
    depth: float
    non_triv: float
    diversity: float
    planning_horizon: float
    new_ge: float            # composite_score with w_planning=ratio*depth (no penalties)
    elapsed_s: float


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--slate", type=Path, default=DEFAULT_SLATE,
                   help=f"Slate JSON (default: {DEFAULT_SLATE.relative_to(ROOT)})")
    p.add_argument("--budget", type=int, default=DEFAULT_BUDGET,
                   help=f"PPO training budget (default {DEFAULT_BUDGET})")
    p.add_argument("--seed", type=int, default=DEFAULT_SEED)
    p.add_argument("--rollouts", type=int, default=DEFAULT_ROLLOUTS,
                   help=f"Self-play rollouts for planning_horizon (default {DEFAULT_ROLLOUTS})")
    p.add_argument("--w-planning-ratio", type=float, default=DEFAULT_W_PLANNING_RATIO,
                   help="planning_horizon_weight = depth_weight * ratio "
                        f"(default {DEFAULT_W_PLANNING_RATIO} per the plan)")
    p.add_argument("--out-db", type=Path, default=DEFAULT_DB)
    p.add_argument("--out-md", type=Path, default=DEFAULT_MD)
    p.add_argument("--use-cache", action="store_true",
                   help="Reuse cached planning_horizon values (skips training).")
    return p.parse_args()


def init_db(path: Path, *, fresh: bool) -> sqlite3.Connection:
    if fresh and path.exists():
        path.unlink()
    con = sqlite3.connect(str(path))
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS probe_cache (
            game_id TEXT,
            budget INTEGER,
            seed INTEGER,
            planning_horizon REAL,
            elapsed_s REAL,
            ts TEXT,
            PRIMARY KEY (game_id, budget, seed)
        )
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS ab_results (
            game_id TEXT PRIMARY KEY,
            substrate TEXT,
            original_ge REAL,
            baseline_ge REAL,
            simplicity REAL,
            depth REAL,
            non_triv REAL,
            diversity REAL,
            planning_horizon REAL,
            new_ge REAL,
            delta_ge REAL,
            elapsed_s REAL,
            w_planning REAL,
            budget INTEGER,
            seed INTEGER,
            ts TEXT
        )
        """
    )
    con.commit()
    return con


def load_stored_scores(db_path: str, game_id: str) -> dict:
    full = ROOT / db_path if not Path(db_path).is_absolute() else Path(db_path)
    con = sqlite3.connect(str(full))
    con.row_factory = sqlite3.Row
    row = con.execute(
        """
        SELECT rule_simplicity, strategic_depth, non_triviality,
               strategic_diversity, go_essence
        FROM scores WHERE game_id = ?
        """,
        (game_id,),
    ).fetchone()
    con.close()
    if row is None:
        raise SystemExit(f"no scored row for {game_id} in {db_path}")
    return {
        "simplicity": float(row["rule_simplicity"]),
        "depth": float(row["strategic_depth"]),
        "non_triv": float(row["non_triviality"]),
        "diversity": float(row["strategic_diversity"]),
        "original_ge": float(row["go_essence"]),
    }


def fetch_cached_probe(con: sqlite3.Connection, game_id: str,
                       budget: int, seed: int) -> tuple[float, float] | None:
    row = con.execute(
        "SELECT planning_horizon, elapsed_s FROM probe_cache "
        "WHERE game_id = ? AND budget = ? AND seed = ?",
        (game_id, budget, seed),
    ).fetchone()
    return (float(row[0]), float(row[1])) if row else None


def cache_probe(con: sqlite3.Connection, game_id: str, budget: int, seed: int,
                ph: float, elapsed_s: float) -> None:
    con.execute(
        "INSERT OR REPLACE INTO probe_cache "
        "(game_id, budget, seed, planning_horizon, elapsed_s, ts) "
        "VALUES (?, ?, ?, ?, ?, datetime('now'))",
        (game_id, budget, seed, ph, elapsed_s),
    )
    con.commit()


def probe_game(game, budget: int, seed: int, rollouts: int) -> tuple[float, float]:
    """Train PPO and return (planning_horizon, elapsed_s)."""
    cfg = TrainingConfig(training_budget=budget)
    mcfg = MetricsConfig(learning_curve_checkpoints=2)
    trainer = SelfPlayTrainer(game, cfg, mcfg, seed=seed)
    t0 = time.time()
    trainer.train()
    ph = planning_horizon_from_rollouts(
        game, [trainer.agents[0], trainer.agents[1]],
        n_rollouts=rollouts, seed=seed,
    )
    return float(ph), time.time() - t0


def evaluate_one(entry: dict, con: sqlite3.Connection, args: argparse.Namespace,
                 scorer_aug: GoEssenceScorer,
                 scorer_baseline: GoEssenceScorer) -> GameRecord:
    stored = load_stored_scores(entry["db"], entry["game_id"])

    cached = fetch_cached_probe(con, entry["game_id"], args.budget, args.seed)
    if cached is not None and args.use_cache:
        ph, elapsed = cached
        print(f"  [cache] planning_horizon={ph:.4f}")
    else:
        game = load_game(entry["db"], entry["game_id"])
        print(f"  training PPO ({args.budget} ep, seed {args.seed})...")
        ph, elapsed = probe_game(
            game, budget=args.budget, seed=args.seed, rollouts=args.rollouts,
        )
        cache_probe(con, entry["game_id"], args.budget, args.seed, ph, elapsed)
        print(f"  planning_horizon={ph:.4f} ({elapsed:.0f}s)")

    # Baseline GE: composite_score with w_planning=0 (planning_factor**0 = 1, inert).
    # This is the apples-to-apples comparison against new_ge — both pre-penalty.
    baseline_ge = scorer_baseline.composite_score(
        simplicity=stored["simplicity"],
        depth=stored["depth"],
        non_triviality=stored["non_triv"],
        diversity=stored["diversity"],
        planning_horizon=ph,  # value doesn't matter when w_p=0
    )
    new_ge = scorer_aug.composite_score(
        simplicity=stored["simplicity"],
        depth=stored["depth"],
        non_triviality=stored["non_triv"],
        diversity=stored["diversity"],
        planning_horizon=ph,
    )

    return GameRecord(
        substrate=entry["substrate"],
        db=entry["db"],
        game_id=entry["game_id"],
        original_ge=stored["original_ge"],
        baseline_ge=baseline_ge,
        simplicity=stored["simplicity"],
        depth=stored["depth"],
        non_triv=stored["non_triv"],
        diversity=stored["diversity"],
        planning_horizon=ph,
        new_ge=new_ge,
        elapsed_s=elapsed,
    )


def persist_ab_result(con: sqlite3.Connection, rec: GameRecord,
                      w_planning: float, budget: int, seed: int) -> None:
    con.execute(
        """
        INSERT OR REPLACE INTO ab_results
        (game_id, substrate, original_ge, baseline_ge, simplicity, depth,
         non_triv, diversity, planning_horizon, new_ge, delta_ge, elapsed_s,
         w_planning, budget, seed, ts)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """,
        (rec.game_id, rec.substrate, rec.original_ge, rec.baseline_ge,
         rec.simplicity, rec.depth, rec.non_triv, rec.diversity,
         rec.planning_horizon, rec.new_ge, rec.new_ge - rec.baseline_ge,
         rec.elapsed_s, w_planning, budget, seed),
    )
    con.commit()


def check_pass(records_sorted_by_new_ge: list[GameRecord]) -> tuple[bool, list[str]]:
    """Apply the three R21 § S2 pass criteria. Returns (overall_pass, reasons)."""
    reasons: list[str] = []

    by_id = {r.game_id: r for r in records_sorted_by_new_ge}
    top_ids = [r.game_id for r in records_sorted_by_new_ge[:2]]

    # G4.1 byte-identical trio compresses to delta < 0.05
    trio_present = [g for g in BYTE_IDENTICAL_TRIO if g in by_id]
    if len(trio_present) == 3:
        trio_ges = [by_id[g].new_ge for g in trio_present]
        spread = max(trio_ges) - min(trio_ges)
        if spread < TRIO_DELTA_MAX:
            reasons.append(f"G4.1 PASS — trio spread {spread:.4f} < {TRIO_DELTA_MAX}")
        else:
            reasons.append(
                f"G4.1 FAIL — trio spread {spread:.4f} >= {TRIO_DELTA_MAX} "
                f"(GEs: {dict(zip(trio_present, [round(g, 4) for g in trio_ges]))})"
            )
    else:
        reasons.append(f"G4.1 SKIP — trio not all present (have {trio_present})")

    # G4.2 + G4.3 — depth record and pie game reach top-2.
    for label, gid in (("G4.2 (depth rec 5f5c72e15220)", "5f5c72e15220"),
                       ("G4.3 (pie game 625bfc1f3f49)", "625bfc1f3f49")):
        if gid in top_ids:
            rank = top_ids.index(gid) + 1
            reasons.append(f"{label} PASS — rank {rank}")
        elif gid in by_id:
            actual_rank = next(
                i + 1 for i, r in enumerate(records_sorted_by_new_ge) if r.game_id == gid
            )
            reasons.append(f"{label} FAIL — rank {actual_rank} (need <= 2)")
        else:
            reasons.append(f"{label} SKIP — game not in slate")

    overall = all(r.startswith(("G4.1 PASS", "G4.2", "G4.3")) and "FAIL" not in r
                  for r in reasons)
    # Simpler: any FAIL anywhere -> overall fail.
    overall = not any("FAIL" in r for r in reasons)
    return overall, reasons


def write_md(records: list[GameRecord], reasons: list[str], overall: bool,
             args: argparse.Namespace, w_planning: float, path: Path) -> None:
    records_sorted = sorted(records, key=lambda r: r.new_ge, reverse=True)
    lines = [
        "# R21 S2 A/B re-score — R20 slate under planning-horizon-augmented GE",
        "",
        f"Budget {args.budget} ep, seed {args.seed}, rollouts {args.rollouts}, "
        f"`w_planning = depth_weight * {args.w_planning_ratio} = {w_planning}`.",
        "",
        "**Columns:**",
        "",
        "- `original GE` — stored value from `scores.go_essence`. Includes the "
        "full `evaluate_game()` pipeline (seat-balance, length, hybrid, stability, "
        "timeout, novelty penalties).",
        "- `baseline GE` — `composite_score` on the same stored signals "
        "(simplicity / depth / non-triv / diversity) with `w_planning = 0`. "
        "**Pre-penalty.** This is the apples-to-apples reference for new GE.",
        "- `new GE` — `composite_score` on the same signals plus fresh "
        f"`planning_horizon` from a {args.rollouts}-rollout PPO inference probe, "
        f"with `w_planning = {w_planning}`. **Pre-penalty.**",
        "- `Delta` — `new GE − baseline GE`. Isolates the metric change.",
        "",
        "## Ranking on augmented GE",
        "",
        "| Rank | Game | substrate | original GE | baseline GE | planning_horizon | **new GE** | Delta |",
        "|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for i, r in enumerate(records_sorted):
        lines.append(
            f"| {i + 1} | `{r.game_id}` | {r.substrate} | "
            f"{r.original_ge:.4f} | {r.baseline_ge:.4f} | {r.planning_horizon:.4f} | "
            f"**{r.new_ge:.4f}** | {r.new_ge - r.baseline_ge:+.4f} |"
        )
    lines += ["", "## Pass criteria", ""]
    for reason in reasons:
        lines.append(f"- {reason}")
    lines += [
        "",
        f"**Overall: {'PASS — lock w_planning' if overall else 'FAIL — bisect w_planning'}**",
        "",
    ]
    if not overall:
        lines += [
            "## On FAIL — bisection guide",
            "",
            "Re-run with `--use-cache --w-planning-ratio <new>`. Cached probes "
            "make this near-instant. Try doubling and halving the current ratio. "
            "If neither range passes, planning-horizon weighting can't satisfy "
            "the three criteria simultaneously — escalate to user before launch.",
            "",
        ]
    path.write_text("\n".join(lines))


def main() -> int:
    args = parse_args()
    args.out_db.parent.mkdir(parents=True, exist_ok=True)

    with open(args.slate) as f:
        slate = json.load(f)
    if not slate:
        raise SystemExit(f"empty slate: {args.slate}")

    # Cache-only mode keeps existing DB; fresh-train mode wipes ab_results
    # (probe_cache is preserved across runs anyway via INSERT OR REPLACE).
    con = init_db(args.out_db, fresh=False)

    # Compute augmented w_planning from MetricsConfig defaults.
    base_mcfg = MetricsConfig()
    w_planning = float(base_mcfg.depth_weight) * float(args.w_planning_ratio)
    aug_mcfg = MetricsConfig(
        depth_weight=base_mcfg.depth_weight,
        diversity_weight=base_mcfg.diversity_weight,
        simplicity_weight=base_mcfg.simplicity_weight,
        planning_horizon_weight=w_planning,
        planning_horizon_rollouts=args.rollouts,
    )
    scorer_aug = GoEssenceScorer(aug_mcfg)
    # Baseline scorer keeps the same weights as MetricsConfig() defaults except
    # planning_horizon_weight = 0 (the default itself). Using the default
    # explicitly keeps the comparison transparent.
    scorer_baseline = GoEssenceScorer(MetricsConfig())

    print(f"R21 S2 A/B — {len(slate)} games, budget {args.budget}, "
          f"seed {args.seed}, w_planning={w_planning}")
    records: list[GameRecord] = []
    t_all = time.time()
    for i, entry in enumerate(slate):
        print(f"[{i + 1}/{len(slate)}] {entry['substrate']} {entry['game_id']}")
        rec = evaluate_one(entry, con, args, scorer_aug, scorer_baseline)
        persist_ab_result(con, rec, w_planning, args.budget, args.seed)
        records.append(rec)
        print(f"  baseline_ge={rec.baseline_ge:.4f}  new_ge={rec.new_ge:.4f}  "
              f"delta={rec.new_ge - rec.baseline_ge:+.4f}")

    records_sorted = sorted(records, key=lambda r: r.new_ge, reverse=True)
    overall, reasons = check_pass(records_sorted)
    write_md(records, reasons, overall, args, w_planning, args.out_md)
    elapsed_total = time.time() - t_all

    print(f"\nTotal elapsed: {elapsed_total:.0f}s")
    print(f"DB: {args.out_db}")
    print(f"MD: {args.out_md}")
    for reason in reasons:
        print(f"  {reason}")
    print(f"\nOverall: {'PASS' if overall else 'FAIL'}")
    con.close()
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
