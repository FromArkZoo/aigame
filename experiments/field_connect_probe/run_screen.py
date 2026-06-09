"""Field-Connect probe — mechanical screen (spec §8a).

Per game (calibrated A1, A0) x 3 PPO seeds: train (budget 5000), then run
an INSTRUMENTED sampled trained-vs-trained mirror eval (n=200, seat-swap)
recording per-step metrics. Aggregates the six pre-registered signals:

  game_length, capture_rate, decisiveness, lead_changes, seat_balance,
  draw_rate

plus PPO-learnability diagnostics (trained_vs_random via trainer.evaluate)
so a no-go from unlearnability is distinguishable from shallowness
(spec §10).

Usage:
    python experiments/field_connect_probe/run_screen.py \
        [--budget 5000] [--eval-episodes 200] [--seeds 42,43,44] \
        [--games-dir experiments/field_connect_probe/games/calibrated]
"""
from __future__ import annotations

import argparse
import csv
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

from experiments.field_connect_probe.metrics import (  # noqa: E402
    count_lead_changes,
    progress_diff_field,
    progress_diff_threshold,
)

HERE = Path(__file__).resolve().parent
GAMES = ("a1_field_connect", "a0_baseline")
LENGTH_BAND = (30.0, 160.0)  # pre-registered healthy band (plies)


def instrumented_episode(game: GameDefV2, a0, a1) -> dict:
    """One sampled game with per-step metric recording."""
    engine = create_engine(game)
    obs = engine.reset()
    agents = [a0, a1]
    is_field = game.win_condition.condition_type == "field_connection"
    margin = getattr(game.win_condition, "control_margin", 0.0)
    prev_counts = list(engine.piece_counts)
    captures = 0
    diffs: list[float] = []
    hard_cap = 2 * game.max_game_steps  # belt & braces; engine self-terminates

    while not engine.done and engine.step_count < hard_cap:
        legal = engine.get_legal_actions()
        if not legal:
            # Expected unreachable for place-only games: get_legal_actions
            # returns [] only when done. If it fires, surface it loudly
            # rather than polluting the draw statistics.
            raise RuntimeError(
                f"no legal actions with done=False at step {engine.step_count} "
                f"({game.game_id})"
            )
        agent = agents[engine.get_current_player()]
        action, _, _ = agent.select_action(
            obs, legal_actions=legal, deterministic=False,
        )
        obs, _, done, info = engine.step(action)
        if not info.get("pie_swap"):
            for pidx in (0, 1):
                drop = prev_counts[pidx] - engine.piece_counts[pidx]
                if drop > 0:
                    captures += drop
            # Pie-swap steps are excluded from the differential series too:
            # the swap relabels the players (negates the field), which would
            # register one spurious sign flip per swapped episode.
            diffs.append(
                progress_diff_field(engine, margin) if is_field
                else progress_diff_threshold(engine)
            )
        prev_counts = list(engine.piece_counts)

    winner = engine._winner  # 1 / 2 / None
    # Exact end-cause via the engine's _ended_by_max_turns observability
    # flag (added in the Task 6 review cycle — no proxy error).
    timeout = engine._ended_by_max_turns
    return dict(
        length=engine.step_count,
        captures=captures,
        lead_changes=count_lead_changes(diffs),
        decisive=(winner is not None and not timeout),
        draw=(winner is None),
        p1_win=(winner == 1),
    )


def screen_one(game: GameDefV2, seed: int, budget: int, eval_eps: int) -> dict:
    cfg = TrainingConfig(training_budget=budget, eval_episodes=100)
    mcfg = MetricsConfig(learning_curve_checkpoints=2)
    trainer = SelfPlayTrainer(game, cfg, mcfg, seed=seed)
    t0 = time.time()
    trainer.train()
    diag = trainer.evaluate(num_episodes=100)

    half = eval_eps // 2
    eps = []
    for i in range(eval_eps):
        if i < half:
            a, b = trainer.agents[0], trainer.agents[1]
        else:
            a, b = trainer.agents[1], trainer.agents[0]
        eps.append(instrumented_episode(game, a, b))

    n = max(len(eps), 1)
    p1_wr = sum(e["p1_win"] for e in eps) / n
    return dict(
        game_id=game.game_id,
        seed=seed,
        game_length=float(np.mean([e["length"] for e in eps])),
        capture_rate=float(np.mean([e["captures"] for e in eps])),
        decisiveness=sum(e["decisive"] for e in eps) / n,
        lead_changes=float(np.mean([e["lead_changes"] for e in eps])),
        seat_balance=abs(p1_wr - 0.5),
        draw_rate=sum(e["draw"] for e in eps) / n,
        trained_vs_random=float(diag.get("trained_vs_random_winrate", -1.0)),
        elapsed_s=time.time() - t0,
    )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--budget", type=int, default=5000)
    p.add_argument("--eval-episodes", type=int, default=200)
    p.add_argument("--seeds", default="42,43,44")
    p.add_argument("--games-dir", type=Path,
                   default=HERE / "games" / "calibrated",
                   help="directory holding the two game JSONs (default: "
                        "the komi-calibrated defs)")
    args = p.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]

    rows = []
    for name in GAMES:
        path = args.games_dir / f"{name}.json"
        game = GameDefV2.from_dict(json.load(open(path)))
        for seed in seeds:
            r = screen_one(game, seed, args.budget, args.eval_episodes)
            rows.append(r)
            print(f"{name} seed={seed}: " + ", ".join(
                f"{k}={v:.3f}" for k, v in r.items()
                if isinstance(v, float)), flush=True)

    with open(HERE / "screen_results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # Aggregate + pre-registered comparison
    def agg(gid: str, key: str) -> float:
        return float(np.mean([r[key] for r in rows if r["game_id"] == gid]))

    a1, a0 = "fc_probe_a1_field_connect", "fc_probe_a0_baseline"
    md = ["# Field-Connect probe — mechanical screen", "",
          f"PPO budget {args.budget}, seeds {seeds}, instrumented sampled "
          f"mirror eval n={args.eval_episodes}/seed.", "",
          "| metric | A1 (Field-Connect) | A0 (baseline) | A1 wins? |",
          "|---|---:|---:|:---:|"]
    wins = 0
    BAND_MID = (LENGTH_BAND[0] + LENGTH_BAND[1]) / 2.0
    checks = [
        ("capture_rate", lambda x1, x0: x1 > x0),
        ("decisiveness", lambda x1, x0: x1 > x0),
        ("lead_changes", lambda x1, x0: x1 > x0),
        ("game_length", lambda x1, x0:
            LENGTH_BAND[0] <= x1 <= LENGTH_BAND[1]
            and not (LENGTH_BAND[0] <= x0 <= LENGTH_BAND[1] and
                     abs(x0 - BAND_MID) < abs(x1 - BAND_MID))),
    ]
    for key, better in checks:
        v1, v0 = agg(a1, key), agg(a0, key)
        ok = better(v1, v0)
        wins += ok
        md.append(f"| {key} | {v1:.3f} | {v0:.3f} | {'YES' if ok else 'no'} |")
    for key in ("seat_balance", "draw_rate", "trained_vs_random"):
        md.append(f"| {key} | {agg(a1, key):.3f} | {agg(a0, key):.3f} | — |")
    md += ["",
           f"**A1 beats A0 on {wins}/4 pre-registered signals "
           f"(GO requires >= 3; spec §8c).**", "",
           f"Healthy length band: {LENGTH_BAND}. game_length 'win' = A1 in "
           f"band and at-least-as-central as A0 ({BAND_MID:.0f} = band midpoint).", "",
           "PPO-learnability guard (spec §10): if A1 trained_vs_random is "
           "near 0.5, a screen miss is UNLEARNABLE-not-shallow — report "
           "separately, do not score as a clean no-go."]
    (HERE / "screen_results.md").write_text("\n".join(md))
    print(f"\nA1 wins {wins}/4 — wrote screen_results.{{csv,md}}", flush=True)


if __name__ == "__main__":
    main()
