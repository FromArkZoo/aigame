"""FC phase-1.5 — komi calibration for the three C arms (spec §6a).

Methodology identical to the probe (sampled_mirror_eval imported from it):
sweep komi_p2; train PPO (budget 3000, seed 42); pick the smallest komi
with seat bias <= 0.10. Komi only enters the timeout tiebreak — pie is the
primary balancer for connection wins (probe: both arms passed at 0.00).
A0/A1 are copied through with their probe komi untouched.

Adaptations from probe:
- sampled_mirror_eval return order is (p1_winrate, draw_rate, avg_length);
  the probe's bias_at_komi unpacks it identically.
- game.komi_p2 is set directly then game.to_dict() used for serialisation
  (matches probe line 141-143; avoids stale raw-dict round-trip).
- No --full-sweep flag: C arms have no BIAS_PROCEED_CAP special case
  (unlike A1); if all komis fail, BIAS_UNRESOLVED is logged and calibrate
  continues to the next arm.

Usage:
    python experiments/fc_phase15/calibrate.py \\
        [--grid "0.0,0.05,0.10,0.15,0.20,0.25,0.30"] \\
        [--budget 3000] [--eval-episodes 200] [--seed 42]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from config import MetricsConfig, TrainingConfig  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from training.trainer import SelfPlayTrainer  # noqa: E402

from experiments.field_connect_probe.calibrate import (  # noqa: E402
    sampled_mirror_eval,
)

HERE = Path(__file__).resolve().parent
GAMES = ("c1_field_flip", "c2_contested_terrain", "c3_control_capture")
PASSTHROUGH = ("a0_baseline.json", "a1_field_connect.json")
BIAS_PASS = 0.10


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--grid", default="0.0,0.05,0.10,0.15,0.20,0.25,0.30")
    p.add_argument("--budget", type=int, default=3000)
    p.add_argument("--eval-episodes", type=int, default=200)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    grid = [float(x) for x in args.grid.split(",")]

    out_dir = HERE / "games" / "calibrated"
    out_dir.mkdir(parents=True, exist_ok=True)
    report = [
        "# FC phase-1.5 — komi calibration",
        "",
        f"PPO budget {args.budget}, seed {args.seed}, sampled mirror eval "
        f"n={args.eval_episodes} (seat-swap, deterministic=False). "
        f"PASS = smallest komi with bias <= {BIAS_PASS}. "
        "A0/A1 passed through from probe calibration unchanged.",
        "",
        "| arm | komi | p1_winrate | bias | draws | verdict |",
        "|---|---:|---:|---:|---:|:---:|",
    ]

    for name in GAMES:
        base = json.load(open(HERE / "games" / f"{name}.json"))
        game = GameDefV2.from_dict(base)
        chosen = None

        for komi in grid:
            game.komi_p2 = komi
            cfg = TrainingConfig(training_budget=args.budget,
                                 eval_episodes=100)
            trainer = SelfPlayTrainer(
                game, cfg,
                MetricsConfig(learning_curve_checkpoints=2),
                seed=args.seed,
            )
            trainer.train()
            # sampled_mirror_eval returns (p1_winrate, draw_rate, avg_length)
            p1_wr, draws, _ = sampled_mirror_eval(
                trainer, args.eval_episodes, game.max_game_steps,
            )
            bias = abs(p1_wr - 0.5)
            ok = bias <= BIAS_PASS
            row = (f"| {name} | {komi:.2f} | {p1_wr:.3f} "
                   f"| {bias:.3f} | {draws:.3f} "
                   f"| {'PASS' if ok else 'no'} |")
            report.append(row)
            print(row, flush=True)

            if ok and chosen is None:
                chosen = komi
                # Serialise via to_dict() so all computed fields round-trip
                # correctly (matches probe lines 141-143).
                with open(out_dir / f"{name}.json", "w") as f:
                    json.dump(game.to_dict(), f, indent=2)
                break  # smallest passing komi found — stop sweeping

        if chosen is None:
            unresolved = (f"| {name} | — | — | — | — "
                          "| **BIAS_UNRESOLVED** |")
            report.append(unresolved)
            print(f"WARNING: {name} BIAS_UNRESOLVED", flush=True)

    # A0/A1: copy through from probe calibration untouched
    for src in PASSTHROUGH:
        shutil.copy(HERE / "games" / src, out_dir / src)
        print(f"passthrough: {src}", flush=True)

    (HERE / "calibration.md").write_text("\n".join(report) + "\n")
    print("wrote calibration.md", flush=True)


if __name__ == "__main__":
    main()
