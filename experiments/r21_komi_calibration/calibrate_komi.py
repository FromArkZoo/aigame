"""R21 S4 — komi auto-calibration driver (post-evolution slate stage).

R20.5 G4 showed pie corrects 60–80% of structural P1 rush advantage but
2/5 of the menger top games still fail mirror-balance by 0.03–0.04 even
with pie active. Pie is a one-move correction; on games where the
structural P1 advantage is large, one swap can't cancel it.

S4 introduces a second balancing mechanism: komi_p2, a fractional bonus
added to P2's effective score at win-condition check time
(`game_engine/engine_v2.py:_check_threshold/_check_territory`). This
driver finds the smallest komi value that brings a candidate's G4
mirror seat bias into the < 0.10 window with sufficient confidence.

Protocol per candidate (matches R20.5 G4 / S1b's evaluate machinery):
  - For each komi in the grid (default {0.05, 0.10, 0.15, 0.20, 0.25, 0.30}):
    - Clone the candidate game, set its komi_p2 to the grid value.
    - Train PPO at budget=3000, seed=42 (same as G4 / S1b — single seed
      because the goal is finding "is this komi sufficient?", not a
      precise per-game estimate).
    - Run sampled trained-vs-trained mirror eval with seat-swap halves,
      n=200, deterministic=False (the equilibrium-preserving setting
      validated by R20.5 G4).
    - Record g4_seat_bias = |sampled_p1_winrate - 0.5|.
  - Pick the smallest komi whose bias passes the 2σ-margin condition.

Decision rule (`passes_with_margin`): a measured bias estimate at n=200
has σ ≈ sqrt(0.25 / 200) ≈ 0.0354. To be 95% confident the *true* bias
is < 0.10, the *measured* bias must be ≤ 0.10 - 2σ ≈ 0.03. This is
deliberately strict — komi is a structural intervention, so we want
high confidence before locking in the value. The strict reading
matches R21_plan.md § S4 ("with ≥ 2σ margin").

If no komi value passes: the game is structurally rush-broken; marked
FAIL_RUSH_BROKEN and surfaced for the agent-eval campaign as a G3
miss (R21 success criterion).

Cost per candidate: 6 PPO trains × ~4 min/train ≈ 24 min. For a
top-K=10 slate that's ~4 hr serial (plan estimate was ~5 hr). The
driver is single-threaded by default; parallelising across candidates
would lift this further, but R21 launch can afford the serial wall.

Inputs:
  --candidates-json   list of {substrate, db, game_id, baseline_g4_bias?}.
                      Typically the post-S1b slate's accepted entries.
  --grid              komi grid (comma-separated floats, default
                      "0.05,0.10,0.15,0.20,0.25,0.30").
  --sigma             stdev of the bias estimator (default 0.0354 for n=200).
  --threshold         target bias upper bound (default 0.10).
  --budget            PPO training budget (default 3000).
  --eval-episodes     sampled mirror eval episodes (default 200).
  --seed              PPO seed (default 42).
  --skip-baseline     skip candidates whose baseline_g4_bias < threshold
                      (already passing — no komi needed). Default: don't
                      skip; calibrate every candidate so the output is
                      self-contained.
  --out-json          per-candidate calibrated-komi output.
  --out-md            human-readable summary.
  --dry-run           print the plan without launching PPO.

Output JSON shape (per-candidate record):
  {
    "substrate": "menger", "game_id": "...", "db": "...",
    "decision": "PASS_komi_0.10",        # or "PASS_komi_0.0" if baseline passes
                                          # or "FAIL_RUSH_BROKEN"
    "calibrated_komi": 0.10,              # null on FAIL
    "evaluations": [
      {"komi": 0.0,  "g4_seat_bias": 0.13, "passed": false},
      {"komi": 0.05, "g4_seat_bias": 0.08, "passed": false},
      {"komi": 0.10, "g4_seat_bias": 0.02, "passed": true},
      ...
    ]
  }
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import sys
import time
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("r21_komi_calibration")


DEFAULT_GRID = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30)
DEFAULT_SIGMA = 0.0354     # sqrt(0.25 / 200) for n=200 worst-case σ
DEFAULT_THRESHOLD = 0.10   # G3 target: bias < 0.10
DEFAULT_BUDGET = 3000
DEFAULT_EVAL_EPISODES = 200
DEFAULT_SEED = 42
MARGIN_MULTIPLE = 2.0      # 2σ for 95% confidence


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--candidates-json", type=Path, required=True)
    p.add_argument(
        "--grid", type=str,
        default=",".join(str(v) for v in DEFAULT_GRID),
        help=f"Komi grid as comma-separated floats. Default: {DEFAULT_GRID}",
    )
    p.add_argument("--sigma", type=float, default=DEFAULT_SIGMA)
    p.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    p.add_argument("--budget", type=int, default=DEFAULT_BUDGET)
    p.add_argument("--eval-episodes", type=int, default=DEFAULT_EVAL_EPISODES)
    p.add_argument("--seed", type=int, default=DEFAULT_SEED)
    p.add_argument(
        "--skip-baseline", action="store_true",
        help="Skip candidates whose pre-supplied baseline_g4_bias is "
             "already < --threshold (with margin).",
    )
    p.add_argument("--out-json", type=Path, default=HERE / "r21_komi_calibrated.json")
    p.add_argument("--out-md", type=Path, default=HERE / "r21_komi_calibrated.md")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


# ----------------------------------------------------------------------
# Pure decision logic (testable without PPO / sqlite)
# ----------------------------------------------------------------------

def passes_with_margin(
    bias: float,
    threshold: float = DEFAULT_THRESHOLD,
    sigma: float = DEFAULT_SIGMA,
    margin_multiple: float = MARGIN_MULTIPLE,
) -> bool:
    """Pass iff measured bias is far enough below threshold to be
    confident the true bias is also below it.

    margin = margin_multiple × sigma  (default 2σ ≈ 95% one-sided CI).
    Pass condition: bias <= threshold - margin.

    Example with defaults: bias <= 0.10 - 0.0708 = 0.0292.
    """
    margin = margin_multiple * sigma
    return bias <= threshold - margin


def pick_smallest_passing(
    evaluations: list[dict],
) -> tuple[str, float | None]:
    """Walk evaluations in komi-ascending order; return the first passing.

    Returns (decision_str, calibrated_komi). decision_str is one of:
      - "PASS_komi_0.0" if the baseline (komi=0) already passes
      - "PASS_komi_X.YZ" for the first grid value that passes
      - "FAIL_RUSH_BROKEN" if none pass.
    """
    for ev in sorted(evaluations, key=lambda e: e["komi"]):
        if ev["passed"]:
            komi = ev["komi"]
            return (f"PASS_komi_{komi:g}", float(komi))
    return ("FAIL_RUSH_BROKEN", None)


def calibrate_one(
    candidate: dict,
    grid: list[float],
    evaluate_fn: Callable[[dict, float], dict],
    threshold: float = DEFAULT_THRESHOLD,
    sigma: float = DEFAULT_SIGMA,
    include_baseline: bool = True,
) -> dict:
    """Run the full per-candidate calibration loop.

    `evaluate_fn(candidate, komi) -> {"g4_seat_bias": float, ...}` is the
    injection point for PPO + mirror eval. Tests pass a stub; production
    passes a closure over `evaluate_one_game` with the cloned game.

    If `include_baseline`, evaluates komi=0.0 first — useful when the
    caller didn't pre-supply baseline_g4_bias. The smallest-passing pick
    then includes 0.0 as the candidate's first option.
    """
    evaluations: list[dict] = []
    if include_baseline:
        result = evaluate_fn(candidate, 0.0)
        passed = passes_with_margin(
            result["g4_seat_bias"], threshold=threshold, sigma=sigma,
        )
        evaluations.append({
            "komi": 0.0,
            "g4_seat_bias": float(result["g4_seat_bias"]),
            "passed": bool(passed),
            **{k: v for k, v in result.items() if k != "g4_seat_bias"},
        })
        if passed:
            decision, calibrated = pick_smallest_passing(evaluations)
            return {
                **candidate,
                "decision": decision,
                "calibrated_komi": calibrated,
                "evaluations": evaluations,
            }

    for komi in grid:
        result = evaluate_fn(candidate, komi)
        passed = passes_with_margin(
            result["g4_seat_bias"], threshold=threshold, sigma=sigma,
        )
        evaluations.append({
            "komi": float(komi),
            "g4_seat_bias": float(result["g4_seat_bias"]),
            "passed": bool(passed),
            **{k: v for k, v in result.items() if k != "g4_seat_bias"},
        })
        if passed:
            break  # smallest-passing — stop walking the grid

    decision, calibrated = pick_smallest_passing(evaluations)
    return {
        **candidate,
        "decision": decision,
        "calibrated_komi": calibrated,
        "evaluations": evaluations,
    }


# ----------------------------------------------------------------------
# Output helpers
# ----------------------------------------------------------------------

def write_summary_md(
    records: list[dict],
    path: Path,
    *,
    threshold: float,
    sigma: float,
    margin_multiple: float,
) -> None:
    margin = margin_multiple * sigma
    lines = [
        "# R21 S4 — komi auto-calibration verdict",
        "",
        f"Pass condition: measured g4_seat_bias ≤ {threshold} − "
        f"{margin_multiple}σ ({margin_multiple}×{sigma:.4f} = {margin:.4f}) "
        f"≈ {threshold - margin:.4f}.",
        "",
        "| # | substrate | game_id | decision | calibrated_komi | smallest passing |",
        "|---|---|---|---|---:|---|",
    ]
    for i, r in enumerate(records, 1):
        k = r.get("calibrated_komi")
        k_str = "—" if k is None else f"{k:.2f}"
        lines.append(
            f"| {i} | {r.get('substrate', '?')} | `{r['game_id']}` | "
            f"{r['decision']} | {k_str} | "
            f"{'✓' if r['decision'].startswith('PASS') else '✗ (rush-broken)'} |"
        )
    passes = sum(1 for r in records if r["decision"].startswith("PASS"))
    fails = sum(1 for r in records if r["decision"] == "FAIL_RUSH_BROKEN")
    lines += [
        "",
        f"**Calibrated**: {passes}. **Rush-broken (FAIL G3)**: {fails}.",
        "",
        "## Per-candidate grid evaluations",
        "",
    ]
    for r in records:
        lines.append(f"### `{r['game_id']}` ({r.get('substrate', '?')})")
        lines.append("")
        lines.append("| komi | g4_seat_bias | passed |")
        lines.append("|---:|---:|---|")
        for ev in r["evaluations"]:
            lines.append(
                f"| {ev['komi']:.2f} | {ev['g4_seat_bias']:.4f} | "
                f"{'✓' if ev['passed'] else '✗'} |"
            )
        lines.append("")
    path.write_text("\n".join(lines))


# ----------------------------------------------------------------------
# Production evaluator (closes over evaluate_one_game)
# ----------------------------------------------------------------------

def make_production_evaluate_fn(
    *,
    budget: int,
    eval_eps: int,
    seed: int,
):
    """Build the closure injected as evaluate_fn for live PPO runs.

    Imports the heavy machinery lazily so the module loads quickly
    (tests stub evaluate_fn and never hit this path)."""
    from experiments.r20_5_g4.run_g4 import evaluate_one_game
    from experiments.r20_finalization.finalize_champions import load_game

    def evaluate_fn(candidate: dict, komi: float) -> dict:
        game = load_game(candidate["db"], candidate["game_id"])
        # Clone the game and apply komi_p2. game.copy() is deepcopy.
        cloned = game.copy()
        cloned.komi_p2 = float(komi)
        return evaluate_one_game(
            cloned, budget=budget, eval_eps=eval_eps, seed=seed,
        )

    return evaluate_fn


# ----------------------------------------------------------------------
# CLI entry
# ----------------------------------------------------------------------

def main() -> int:
    args = parse_args()
    grid = [float(v) for v in args.grid.split(",")]

    if not args.candidates_json.exists():
        logger.error("candidates JSON not found: %s", args.candidates_json)
        return 2
    candidates = json.loads(args.candidates_json.read_text())
    if not isinstance(candidates, list):
        logger.error("candidates JSON must be a top-level list")
        return 2

    logger.info(
        "S4 komi calibration: %d candidates, grid=%s, threshold=%.3f, "
        "sigma=%.4f (margin %.1fσ = %.4f).",
        len(candidates), grid, args.threshold,
        args.sigma, MARGIN_MULTIPLE, MARGIN_MULTIPLE * args.sigma,
    )

    if args.dry_run:
        for i, c in enumerate(candidates, 1):
            logger.info(
                "  %2d. [%s] %s (db=%s)",
                i, c.get("substrate", "?"), c["game_id"], c.get("db", "?"),
            )
        logger.info("DRY RUN — exiting before PPO.")
        return 0

    evaluate_fn = make_production_evaluate_fn(
        budget=args.budget, eval_eps=args.eval_episodes, seed=args.seed,
    )

    t0 = time.time()
    records: list[dict] = []
    for i, candidate in enumerate(candidates, 1):
        logger.info(
            "[%d/%d] calibrating %s (%s)",
            i, len(candidates), candidate["game_id"],
            candidate.get("substrate", "?"),
        )

        skip = (
            args.skip_baseline
            and "baseline_g4_bias" in candidate
            and passes_with_margin(
                candidate["baseline_g4_bias"],
                threshold=args.threshold, sigma=args.sigma,
            )
        )
        if skip:
            logger.info(
                "  baseline_g4_bias=%.4f passes already; skipping calibration",
                candidate["baseline_g4_bias"],
            )
            records.append({
                **candidate,
                "decision": "PASS_komi_0.0",
                "calibrated_komi": 0.0,
                "evaluations": [],
            })
            continue

        record = calibrate_one(
            candidate, grid, evaluate_fn=evaluate_fn,
            threshold=args.threshold, sigma=args.sigma,
            include_baseline=("baseline_g4_bias" not in candidate),
        )
        records.append(record)
        logger.info(
            "  → %s (calibrated_komi=%s)",
            record["decision"], record.get("calibrated_komi"),
        )

    elapsed = time.time() - t0
    logger.info("Calibration complete in %.1f min.", elapsed / 60.0)

    args.out_json.write_text(json.dumps(records, indent=2))
    write_summary_md(
        records, args.out_md,
        threshold=args.threshold, sigma=args.sigma,
        margin_multiple=MARGIN_MULTIPLE,
    )
    logger.info("Calibrated slate → %s", args.out_json)
    logger.info("Summary → %s", args.out_md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
