#!/usr/bin/env python3
"""CLI wrapper for the R20 two-tier PPO smoke harness.

Usage:
    python experiments/r20_smoke_two_tier/run_two_tier.py <game.json> [...]
    python experiments/r20_smoke_two_tier/run_two_tier.py --tier1 3000 --tier2 6000 game.json
    python experiments/r20_smoke_two_tier/run_two_tier.py --out-dir verdicts/ *.json

Each game JSON is a serialized GameDefV2 (GameDefV2.to_dict). Verdicts go
to stdout and, if --out-dir is set, also as <game_id>.tt_verdict.json files
in that directory.

Exit code = count of dropped seeds (0 = all pass).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.r20_smoke_two_tier.harness import (  # noqa: E402
    DEFAULT_TIER2_BUDGET,
    TwoTierVerdict,
    load_game,
    two_tier_smoke,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("games", nargs="+", help="GameDefV2 JSON file(s).")
    p.add_argument("--tier1", type=int, default=3000,
                   help="Tier 1 PPO budget (default 3000).")
    p.add_argument("--tier2", type=int, default=DEFAULT_TIER2_BUDGET,
                   help=f"Tier 2 PPO budget (default {DEFAULT_TIER2_BUDGET}).")
    p.add_argument("--eval-episodes", type=int, default=100,
                   help="Episodes per evaluation pass (default 100).")
    p.add_argument("--seed", type=int, default=42, help="Trainer seed.")
    p.add_argument("--out-dir", type=Path, default=None,
                   help="If set, writes <game_id>.tt_verdict.json per seed.")
    return p.parse_args()


def _print_verdict(tt: TwoTierVerdict) -> None:
    t1 = tt.tier1
    print(
        f"\n{tt.final_classification.upper():<19} {tt.game_id}  "
        f"({t1.topology_type} axis={t1.axis_size} dims={t1.num_dimensions}, "
        f"cells={t1.active_cells})"
    )
    print(
        f"    Tier 1 ({t1.training_budget}ep): len={t1.sampled_avg_length:.1f} "
        f"(floor {t1.length_floor:.1f})  "
        f"seat_bias={t1.seat_bias:.2f}  greedy_p1={t1.greedy_p1_winrate:.0%}  "
        f"({t1.elapsed_seconds:.1f}s)"
    )
    print(f"    Tier 1 verdict: {tt.tier1_classification}")
    if tt.tier2 is not None:
        t2 = tt.tier2
        progress = tt.tier2_seat_bias_progress or 0.0
        print(
            f"    Tier 2 ({t2.training_budget}ep): len={t2.sampled_avg_length:.1f} "
            f"(floor {t2.length_floor:.1f})  "
            f"seat_bias={t2.seat_bias:.2f}  greedy_p1={t2.greedy_p1_winrate:.0%}  "
            f"({t2.elapsed_seconds:.1f}s)"
        )
        print(
            f"    Seat-bias progress: {progress:+.3f} "
            f"(needs >= 0.05 OR soft floors clear)"
        )
    print(f"    Decision: {tt.rationale}")


def main() -> int:
    args = parse_args()
    if args.out_dir is not None:
        args.out_dir.mkdir(parents=True, exist_ok=True)

    drops = 0
    for path in args.games:
        game = load_game(path)
        tt = two_tier_smoke(
            game,
            tier1_budget=args.tier1,
            tier2_budget=args.tier2,
            eval_episodes=args.eval_episodes,
            seed=args.seed,
        )
        _print_verdict(tt)
        if args.out_dir is not None:
            out_path = args.out_dir / f"{tt.game_id}.tt_verdict.json"
            out_path.write_text(tt.to_json())
        if not tt.final_passed:
            drops += 1

    total = len(args.games)
    print(f"\n=== {total - drops} pass, {drops} drop ({total} total) ===")
    return drops


if __name__ == "__main__":
    sys.exit(main())
