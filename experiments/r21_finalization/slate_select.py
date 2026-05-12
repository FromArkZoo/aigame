"""R21 S1b — equilibrium-fingerprint slate dedup at slate-build.

S1a (canonical-blob dedup) catches R20's byte-identical trio — three games
with the same rule_representation under different game_ids — but cannot
see R20.5's functional-equivalence trio: three games whose rule blobs are
distinct (different bytes) but whose trained-policy behaviour is
*identical* under a single PPO seed (sampled_p1_wr, sampled_len,
greedy_p1_wr all matched to 1 decimal). S1b is the second-stage dedup
that closes this gap before the slate goes to the agent-team verdict
campaign.

Protocol per candidate (matches the R20.5 G4 driver at
`experiments/r20_5_g4/run_g4.py`):
  - Train PPO at training_budget=3000 ep, seed=42 (single seed — cheap).
  - Run sampled trained-vs-trained mirror eval with seat-swap halves,
    n=200 (`deterministic=False`, the equilibrium-preserving protocol).
  - Greedy diagnostic from `trainer.evaluate(num_episodes=100)`.

Fingerprint tuple: `(round(sampled_p1_wr, p), round(sampled_len, p),
round(greedy_p1_wr, p))` where `p` defaults to 1 decimal (the plan's
choice). Greedy candidates are walked in input rank order; the first
fingerprint instance is kept, subsequent collisions drop.

Cost: ~4 min per candidate (3000 ep PPO + 200-ep mirror + 100-ep diag).
Top-10 candidates → ~40 min serial. R21 slate target is 6 unique
kernels; over-pull by 4 to give the dedup room.

Inputs:
  --candidates-json   JSON list of {substrate, db, game_id, original_ge?}.
                      Sorted in priority order (best first).
  --target-size       Stop after this many uniques (default 6).
  --budget            PPO training budget (default 3000).
  --eval-episodes     Sampled mirror eval episodes (default 200).
  --seed              PPO seed (default 42).
  --fingerprint-precision
                      Decimal places to round to (default 1).
  --out-json          Pruned slate output.
  --out-md            Per-candidate verdict markdown.
  --dry-run           Print plan without running PPO.

Output JSON shape:
  [
    {"substrate": "menger", "db": "...", "game_id": "...",
     "fingerprint": [0.6, 57.1, 0.1],
     "sampled_p1_wr": 0.624, "sampled_avg_length": 57.0,
     "greedy_p1_wr": 0.10, "decision": "ACCEPT"},
    {"substrate": "menger", ..., "decision": "DROP_DUP",
     "duplicate_of": "..."}
  ]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("r21_slate_select")


DEFAULT_BUDGET = 3000
DEFAULT_EVAL_EPISODES = 200
DEFAULT_SEED = 42
DEFAULT_TARGET = 6
DEFAULT_PRECISION = 1


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--candidates-json", type=Path, required=True,
        help="JSON list of candidates: [{substrate, db, game_id, original_ge?}, ...]. "
             "Sorted best-first; dedup walks in order.",
    )
    p.add_argument("--target-size", type=int, default=DEFAULT_TARGET)
    p.add_argument("--budget", type=int, default=DEFAULT_BUDGET)
    p.add_argument("--eval-episodes", type=int, default=DEFAULT_EVAL_EPISODES)
    p.add_argument("--seed", type=int, default=DEFAULT_SEED)
    p.add_argument("--fingerprint-precision", type=int, default=DEFAULT_PRECISION)
    p.add_argument(
        "--out-json", type=Path, default=HERE / "r21_slate_pruned.json",
    )
    p.add_argument(
        "--out-md", type=Path, default=HERE / "r21_slate_pruned.md",
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Print which candidates would be evaluated; skip PPO.",
    )
    return p.parse_args()


def make_fingerprint(
    sampled_p1_wr: float,
    sampled_len: float,
    greedy_p1_wr: float,
    precision: int = 1,
) -> tuple[float, float, float]:
    """Round trained-policy stats to `precision` decimals. R20.5 confirmed
    the functional-equivalence trio matches to 1 decimal; tighter
    rounding (2+ decimals) would let PPO noise re-introduce false
    distinctions. Looser (0 decimals) collapses too many real
    differences."""
    return (
        round(float(sampled_p1_wr), precision),
        round(float(sampled_len), precision),
        round(float(greedy_p1_wr), precision),
    )


def dedup_slate(
    candidates: list[dict],
    evaluate_fn: Callable[[dict], dict],
    target_size: int,
    precision: int,
) -> list[dict]:
    """Walk candidates in order, evaluate each, fingerprint, accept the
    first instance per fingerprint and drop subsequent collisions.

    Returns the full per-candidate record list (including DROP_DUP rows
    for traceability) — the caller picks the ACCEPT subset for the
    output slate JSON.
    """
    seen: dict[tuple, str] = {}  # fingerprint -> first-seen game_id
    accepted = 0
    records: list[dict] = []

    for c in candidates:
        if accepted >= target_size:
            records.append({**c, "decision": "SKIP_TARGET_MET"})
            continue

        eval_result = evaluate_fn(c)
        fp = make_fingerprint(
            eval_result["sampled_p1_wr"],
            eval_result["sampled_avg_length"],
            eval_result["greedy_p1_wr"],
            precision=precision,
        )
        rec = {
            **c,
            "fingerprint": list(fp),
            "sampled_p1_wr": float(eval_result["sampled_p1_wr"]),
            "sampled_avg_length": float(eval_result["sampled_avg_length"]),
            "greedy_p1_wr": float(eval_result["greedy_p1_wr"]),
        }
        if fp in seen:
            rec["decision"] = "DROP_DUP"
            rec["duplicate_of"] = seen[fp]
            logger.info(
                "[%s] %s DROP — fingerprint %s duplicates %s",
                c.get("substrate", "?"), c["game_id"], fp, seen[fp],
            )
        else:
            seen[fp] = c["game_id"]
            rec["decision"] = "ACCEPT"
            accepted += 1
            logger.info(
                "[%s] %s ACCEPT — fingerprint %s (slot %d/%d)",
                c.get("substrate", "?"), c["game_id"], fp,
                accepted, target_size,
            )
        records.append(rec)

    return records


def write_summary_md(records: list[dict], path: Path, precision: int) -> None:
    lines = [
        "# R21 S1b — slate dedup verdict",
        "",
        f"Fingerprint precision: {precision} decimal places.",
        "",
        "| # | substrate | game_id | sampled_p1_wr | sampled_len | greedy_p1_wr | fingerprint | decision | note |",
        "|---|---|---|---:|---:|---:|---|---|---|",
    ]
    def _fmt(value, digits: int) -> str:
        if isinstance(value, float):
            return f"{value:.{digits}f}"
        return "n/a"

    for i, r in enumerate(records, 1):
        fp = r.get("fingerprint", [None, None, None])
        fp_str = (
            "—"
            if r.get("decision") == "SKIP_TARGET_MET"
            else f"({fp[0]}, {fp[1]}, {fp[2]})"
        )
        note = ""
        if r.get("decision") == "DROP_DUP":
            note = f"duplicate of `{r['duplicate_of']}`"
        elif r.get("decision") == "SKIP_TARGET_MET":
            note = "target size reached"
        lines.append(
            f"| {i} | {r.get('substrate', '?')} | `{r['game_id']}` | "
            f"{_fmt(r.get('sampled_p1_wr'), 3)} | "
            f"{_fmt(r.get('sampled_avg_length'), 1)} | "
            f"{_fmt(r.get('greedy_p1_wr'), 3)} | "
            f"{fp_str} | {r['decision']} | {note} |"
        )
    accepted = sum(1 for r in records if r["decision"] == "ACCEPT")
    dropped = sum(1 for r in records if r["decision"] == "DROP_DUP")
    skipped = sum(1 for r in records if r["decision"] == "SKIP_TARGET_MET")
    lines += [
        "",
        f"**Accepted**: {accepted}. **Dropped (duplicate)**: {dropped}. "
        f"**Skipped (target met)**: {skipped}.",
    ]
    path.write_text("\n".join(lines))


def main() -> int:
    args = parse_args()

    if not args.candidates_json.exists():
        logger.error("candidates JSON not found: %s", args.candidates_json)
        return 2
    candidates = json.loads(args.candidates_json.read_text())
    if not isinstance(candidates, list):
        logger.error("candidates JSON must be a top-level list")
        return 2

    if args.dry_run:
        logger.info(
            "DRY RUN: would evaluate %d candidates at budget=%d, eval_eps=%d, seed=%d",
            len(candidates), args.budget, args.eval_episodes, args.seed,
        )
        for i, c in enumerate(candidates, 1):
            logger.info("  %2d. [%s] %s (db=%s)", i, c.get("substrate", "?"),
                        c["game_id"], c.get("db", "?"))
        return 0

    # Import the heavy machinery only when actually running.
    from experiments.r20_5_g4.run_g4 import evaluate_one_game
    from experiments.r20_finalization.finalize_champions import load_game

    def evaluate_fn(candidate: dict) -> dict:
        game = load_game(candidate["db"], candidate["game_id"])
        result = evaluate_one_game(
            game,
            budget=args.budget,
            eval_eps=args.eval_episodes,
            seed=args.seed,
        )
        return {
            "sampled_p1_wr": result["sampled_p1_winrate"],
            "sampled_avg_length": result["sampled_avg_length"],
            "greedy_p1_wr": result["greedy_p1_winrate"],
        }

    t0 = time.time()
    records = dedup_slate(
        candidates,
        evaluate_fn=evaluate_fn,
        target_size=args.target_size,
        precision=args.fingerprint_precision,
    )
    elapsed = time.time() - t0
    logger.info("Slate dedup complete in %.1f min wall.", elapsed / 60.0)

    args.out_json.write_text(json.dumps(records, indent=2))
    write_summary_md(records, args.out_md, args.fingerprint_precision)
    logger.info("Pruned slate → %s", args.out_json)
    logger.info("Summary → %s", args.out_md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
