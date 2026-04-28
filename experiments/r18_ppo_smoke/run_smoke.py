#!/usr/bin/env python3
"""CLI wrapper for the R18 PPO smoke harness.

Usage:
    python experiments/r18_ppo_smoke/run_smoke.py <game.json> [<game.json> ...]
    python experiments/r18_ppo_smoke/run_smoke.py --budget 500 game.json   # quick probe
    python experiments/r18_ppo_smoke/run_smoke.py --out-dir verdicts/ *.json

Each game JSON is a serialized GameDefV2 (as written by GameDefV2.to_dict).
Verdicts go to stdout and, if --out-dir is set, also as <game_id>.verdict.json
files in that directory.

Exit code is the count of dropped seeds — 0 means every seed passed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make repo importable when running this file directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.r18_ppo_smoke.harness import (  # noqa: E402
    load_game,
    smoke_test,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "games",
        nargs="+",
        help="Path(s) to GameDefV2 JSON file(s).",
    )
    p.add_argument(
        "--budget",
        type=int,
        default=3000,
        help="PPO training episodes per seed (default 3000, R18 plan).",
    )
    p.add_argument(
        "--eval-episodes",
        type=int,
        default=100,
        help="Episodes for the post-train evaluation (default 100).",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Trainer seed.",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help=(
            "If set, writes one <game_id>.verdict.json per seed into this "
            "directory in addition to printing to stdout."
        ),
    )
    return p.parse_args()


def _print_verdict(v) -> None:
    status = "PASS" if v.passed else "DROP"
    print(
        f"\n{status}  {v.game_id}  ({v.topology_type} axis={v.axis_size} "
        f"dims={v.num_dimensions}, cells={v.active_cells})"
    )
    print(
        f"    sampled_avg_len = {v.sampled_avg_length:7.2f}  "
        f"(floor {v.length_floor:.1f}, det_avg {v.deterministic_avg_length:.1f})"
    )
    print(
        f"    greedy_p1_wr    = {v.greedy_p1_winrate:7.2%}  "
        f"(seat bias {v.seat_bias:.2f}, threshold {v.seat_bias_threshold:.2f})"
    )
    print(
        f"    trained_p0_wr   = {v.trained_p0_winrate:7.2%}  "
        f"vs_random {v.trained_vs_random_winrate:.2%}  "
        f"heuristic {v.heuristic_p1_winrate:.2%}"
    )
    print(
        f"    elapsed         = {v.elapsed_seconds:.1f}s  "
        f"(budget {v.training_budget} ep, eval {v.eval_episodes} ep)"
    )
    if not v.passed:
        for r in v.drop_reasons:
            print(f"    DROP: {r}")


def main() -> int:
    args = parse_args()

    if args.out_dir is not None:
        args.out_dir.mkdir(parents=True, exist_ok=True)

    drops = 0
    for path in args.games:
        game = load_game(path)
        verdict = smoke_test(
            game,
            training_budget=args.budget,
            eval_episodes=args.eval_episodes,
            seed=args.seed,
        )
        _print_verdict(verdict)

        if args.out_dir is not None:
            out_path = args.out_dir / f"{verdict.game_id}.verdict.json"
            out_path.write_text(verdict.to_json())

        if not verdict.passed:
            drops += 1

    print(f"\n=== {len(args.games) - drops} pass, {drops} drop ===")
    return drops


if __name__ == "__main__":
    sys.exit(main())
