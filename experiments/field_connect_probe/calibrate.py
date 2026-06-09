"""Komi calibration for the two probe games (spec §3.6, §11.3).

Per game: sweep komi_p2 over a grid; at each value train PPO (budget 3000,
seed 42) and measure sampled trained-vs-trained seat bias with seat-swap
halves (the R20.5-G4 / R21-S4 methodology). Pick the smallest komi with
bias <= 0.10. Write calibrated game JSONs + a markdown report.

Note (spec wrinkle, recorded in the plan): for A1 komi only enters the
TIMEOUT tiebreak — pie is the primary balancer for connection wins. If no
komi passes for A1, the game is flagged BIAS_UNRESOLVED (not rush-broken)
and the A/B proceeds only if bias <= 0.15 at the best komi, reported.

Usage:
    python experiments/field_connect_probe/calibrate.py \\
        [--grid "0.0,0.05,0.10,0.15,0.20,0.25,0.30"] \\
        [--budget 3000] [--eval-episodes 200] [--seed 42]
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from config import MetricsConfig, TrainingConfig  # noqa: E402
from game_engine.factory import create_engine  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from training.trainer import SelfPlayTrainer  # noqa: E402
from training.utils import play_game  # noqa: E402

HERE = Path(__file__).resolve().parent
GAMES = ("a1_field_connect", "a0_baseline")
BIAS_PASS = 0.10
BIAS_PROCEED_CAP = 0.15  # A1 may proceed flagged if best bias <= this


def sampled_mirror_eval(trainer, num_episodes: int, max_steps: int):
    """Copied from experiments/r20_5_g4/run_g4.py:102 (same methodology).
    Returns (p1_winrate, draw_rate, avg_length); p1 = seat 0."""
    half = num_episodes // 2
    p1_wins = 0
    draws = 0
    lengths = []
    for i in range(num_episodes):
        engine = create_engine(trainer.game)
        if i < half:
            a0, a1 = trainer.agents[0], trainer.agents[1]
        else:
            a0, a1 = trainer.agents[1], trainer.agents[0]
        winner, length, _ = play_game(
            engine, a0, a1, deterministic=False, max_steps=max_steps,
        )
        lengths.append(length)
        if winner is None:
            draws += 1
        elif winner == 0:
            p1_wins += 1
    n = max(num_episodes, 1)
    return p1_wins / n, draws / n, float(np.mean(lengths)) if lengths else 0.0


def bias_at_komi(game: GameDefV2, komi: float, budget: int, eval_eps: int,
                 seed: int) -> dict:
    g = copy.deepcopy(game)
    g.komi_p2 = komi
    cfg = TrainingConfig(training_budget=budget, eval_episodes=100)
    mcfg = MetricsConfig(learning_curve_checkpoints=2)
    trainer = SelfPlayTrainer(g, cfg, mcfg, seed=seed)
    t0 = time.time()
    trainer.train()
    wr, draws, length = sampled_mirror_eval(
        trainer, eval_eps, g.max_game_steps,
    )
    return dict(komi=komi, p1_winrate=wr, bias=abs(wr - 0.5),
                draw_rate=draws, avg_length=length,
                elapsed_s=time.time() - t0)


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
    md = ["# Field-Connect probe — komi calibration", "",
          f"PPO budget {args.budget}, seed {args.seed}, sampled mirror eval "
          f"n={args.eval_episodes} (seat-swap, deterministic=False). "
          f"PASS = smallest komi with bias <= {BIAS_PASS}.", ""]

    for name in GAMES:
        game = GameDefV2.from_dict(
            json.load(open(HERE / "games" / f"{name}.json"))
        )
        md += [f"## {name}", "",
               "| komi | p1_wr | bias | draws | len | s |",
               "|---|---:|---:|---:|---:|---:|"]
        rows = []
        chosen = None
        for komi in grid:
            r = bias_at_komi(game, komi, args.budget, args.eval_episodes,
                             args.seed)
            rows.append(r)
            md.append(f"| {r['komi']:.2f} | {r['p1_winrate']:.3f} | "
                      f"{r['bias']:.3f} | {r['draw_rate']:.3f} | "
                      f"{r['avg_length']:.1f} | {r['elapsed_s']:.0f} |")
            print(f"{name} komi={komi:.2f} bias={r['bias']:.3f}", flush=True)
            if chosen is None and r["bias"] <= BIAS_PASS:
                chosen = r
        best = min(rows, key=lambda r: r["bias"])
        if chosen is None:
            verdict = (f"BIAS_UNRESOLVED (best bias {best['bias']:.3f} at "
                       f"komi {best['komi']:.2f})")
            use = best if best["bias"] <= BIAS_PROCEED_CAP else None
        else:
            verdict = f"PASS at komi {chosen['komi']:.2f}"
            use = chosen
        md += ["", f"**{verdict}**", ""]
        if use is not None:
            game.komi_p2 = use["komi"]
            with open(out_dir / f"{name}.json", "w") as f:
                json.dump(game.to_dict(), f, indent=2)
            md.append(f"Calibrated def written (komi_p2={use['komi']:.2f}).")
        else:
            md.append("NO calibrated def written — game is A/B-blocked.")
        md.append("")

    (HERE / "calibration.md").write_text("\n".join(md))
    print("wrote calibration.md", flush=True)


if __name__ == "__main__":
    main()
