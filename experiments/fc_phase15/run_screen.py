"""FC phase-1.5 — 5-arm mechanical screen (spec §6b, PREREGISTRATION.md).

Per arm (c1, c2, c3, a0, a1) x 3 PPO seeds: train (budget 5000), then an
instrumented sampled trained-vs-trained mirror eval (n=200, seat-swap)
recording the four pre-registered signals:

  lead_changes, game_length, control_flip_rate, connection_win_fraction

plus sanity columns (seat_balance, draw_rate, trained_vs_random,
capture_events and stranded_rate as diagnostics). A0/A1 are retrained from
their probe-calibrated defs — no probe checkpoints exist — so every number
in the comparison table comes from identical instrumentation.

Usage:
    python experiments/fc_phase15/run_screen.py \
        [--budget 5000] [--eval-episodes 200] [--seeds 42,43,44] \
        [--games-dir experiments/fc_phase15/games/calibrated]
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
from experiments.fc_phase15.metrics import (  # noqa: E402
    controller_signs,
    count_controller_changes,
)

HERE = Path(__file__).resolve().parent
ARMS = ("c1_field_flip", "c2_contested_terrain", "c3_control_capture",
        "a0_baseline", "a1_field_connect")
C_ARMS = ("c1_field_flip", "c2_contested_terrain", "c3_control_capture")
A0 = "a0_baseline"
LENGTH_BAND = (30.0, 160.0)
CONNECTION_WIN_FLOOR = 0.80
SCREEN_GO_MIN = 3


def instrumented_episode(game: GameDefV2, a0, a1) -> dict:
    """One sampled game with per-step metric recording."""
    engine = create_engine(game)
    obs = engine.reset()
    agents = [a0, a1]
    is_field = game.win_condition.condition_type == "field_connection"
    margin = getattr(game.win_condition, "control_margin", 0.0)
    prev_counts = list(engine.piece_counts)
    prev_signs = controller_signs(engine, margin)
    captures = 0
    diffs: list[float] = []
    flips: list[int] = []
    hard_cap = 2 * game.max_game_steps

    while not engine.done and engine.step_count < hard_cap:
        legal = engine.get_legal_actions()
        if not legal:
            raise RuntimeError(
                f"no legal actions with done=False at step "
                f"{engine.step_count} ({game.game_id})"
            )
        agent = agents[engine.get_current_player()]
        action, _, _ = agent.select_action(
            obs, legal_actions=legal, deterministic=False,
        )
        obs, _, done, info = engine.step(action)
        cur_signs = controller_signs(engine, margin)
        if not info.get("pie_swap"):
            for pidx in (0, 1):
                drop = prev_counts[pidx] - engine.piece_counts[pidx]
                if drop > 0:
                    captures += drop
            diffs.append(
                progress_diff_field(engine, margin) if is_field
                else progress_diff_threshold(engine)
            )
            flips.append(count_controller_changes(prev_signs, cur_signs))
        prev_counts = list(engine.piece_counts)
        prev_signs = cur_signs

    winner = engine._winner
    timeout = engine._ended_by_max_turns
    return dict(
        length=engine.step_count,
        captures=captures,
        lead_changes=count_lead_changes(diffs),
        control_flips=float(np.mean(flips)) if flips else 0.0,
        connection_win=(winner is not None and not timeout),
        draw=(winner is None),
        p1_win=(winner == 1),
        stranded=bool(getattr(engine, "_ended_by_no_moves", False)),
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
        lead_changes=float(np.mean([e["lead_changes"] for e in eps])),
        control_flip_rate=float(np.mean([e["control_flips"] for e in eps])),
        connection_win_fraction=sum(e["connection_win"] for e in eps) / n,
        capture_events=float(np.mean([e["captures"] for e in eps])),
        stranded_rate=sum(e["stranded"] for e in eps) / n,
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
                   default=HERE / "games" / "calibrated")
    args = p.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]

    rows = []
    for name in ARMS:
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

    def agg(gid_suffix: str, key: str) -> float:
        vals = [r[key] for r in rows if r["game_id"].endswith(gid_suffix)]
        return float(np.mean(vals))

    BAND_MID = (LENGTH_BAND[0] + LENGTH_BAND[1]) / 2.0

    def length_win(x_c: float, x_0: float) -> bool:
        return (LENGTH_BAND[0] <= x_c <= LENGTH_BAND[1]
                and not (LENGTH_BAND[0] <= x_0 <= LENGTH_BAND[1]
                         and abs(x_0 - BAND_MID) < abs(x_c - BAND_MID)))

    md = ["# FC phase-1.5 — mechanical screen", "",
          f"PPO budget {args.budget}, seeds {seeds}, instrumented sampled "
          f"mirror eval n={args.eval_episodes}/seed. Bars per "
          f"PREREGISTRATION.md.", ""]
    ranking = []
    for arm in C_ARMS:
        wins = 0
        md += [f"## {arm} vs {A0}", "",
               "| signal | arm | A0 | win? |", "|---|---:|---:|:---:|"]
        checks = [
            ("lead_changes", agg(arm, "lead_changes") > agg(A0, "lead_changes")),
            ("game_length", length_win(agg(arm, "game_length"),
                                       agg(A0, "game_length"))),
            ("control_flip_rate", agg(arm, "control_flip_rate")
                                  > agg(A0, "control_flip_rate")),
            ("connection_win_fraction", agg(arm, "connection_win_fraction")
                                        >= CONNECTION_WIN_FLOOR),
        ]
        for key, ok in checks:
            wins += ok
            md.append(f"| {key} | {agg(arm, key):.3f} | {agg(A0, key):.3f} "
                      f"| {'YES' if ok else 'no'} |")
        sane = (agg(arm, "trained_vs_random") >= 0.80
                and agg(arm, "draw_rate") <= 0.05
                and agg(arm, "seat_balance") <= 0.10)
        md += ["", f"**{wins}/4 signals; sanity "
                   f"{'PASS' if sane else 'FAIL'}.**", ""]
        if wins >= SCREEN_GO_MIN and sane:
            ranking.append((agg(arm, "control_flip_rate"), arm, wins))

    md += ["## Reference rows (A0/A1, new instrumentation)", ""]
    for ref in (A0, "a1_field_connect"):
        md.append(f"- {ref}: " + ", ".join(
            f"{k}={agg(ref, k):.3f}" for k in
            ("lead_changes", "game_length", "control_flip_rate",
             "connection_win_fraction", "trained_vs_random")))
    if ranking:
        ranking.sort(reverse=True)
        md += ["", f"**WINNER (advances to blind A/B): {ranking[0][1]}** "
                   f"(ranked by control_flip_rate among >=3/4 arms; "
                   f"PREREGISTRATION.md).", ""]
    else:
        md += ["", "**NO ARM CLEARED 3/4 + sanity — screen NO-GO; "
                   "stop before the blind campaign (spec §6b).**", ""]
    (HERE / "screen_results.md").write_text("\n".join(md))
    print("\n".join(md[-4:]))


if __name__ == "__main__":
    main()
