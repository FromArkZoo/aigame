"""R20.5 G4 — measure trained-vs-trained mirror seat bias on pie-clean menger top-N.

R20's G4 (mirror seat bias < 0.10) was unmeasurable because of the pie_rule
propagation bug fixed in `ac9e642`. R20.5 re-ran menger with pie clean across
all 130 games. This driver computes G4 the right way for pie-rule games.

**Why a custom eval, not the harness's `seat_bias`.** harness.smoke_test computes
`seat_bias = abs(greedy_p1_winrate - 0.5)`. GreedyAgent always-swaps under pie
(commit `d25590d`: "the upper-bound assumption — if pie can't structurally
balance the game even when P2 always swaps, the game is rush-broken"). That's
useful as a rush-broken filter but it is *not* a measurement of equilibrium
seat balance — under greedy-always-swap on a pie game, P2 trivially wins.
Deterministic trained-vs-trained also fails (per harness module docstring:
"deterministic argmax collapses to identical 2-step games regardless of game
quality"). Only **sampled trained-vs-trained with seat-swap** preserves the
equilibrium where pie usage is rational, which is what G4 actually wants.

Per game:
  - Train PPO at training_budget (default 3000 ep), seed=42.
  - Run sampled trained-vs-trained eval over eval_episodes (default 200) with
    seat-swap halves; record P1 (seat-0) winrate.
  - Also record greedy + deterministic-trained numbers as diagnostics.

G4 metric: ``g4_seat_bias = abs(sampled_p1_winrate - 0.5)``.
G4 PASS: ``g4_seat_bias < 0.10`` for every game in the slate.

Output:
  - <out-db> SQLite g4_results table (per-game)
  - <out-md> markdown table + verdict line + methodology note
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from config import MetricsConfig, TrainingConfig  # noqa: E402
from experiments.r20_finalization.finalize_champions import load_game  # noqa: E402
from game_engine.factory import create_engine  # noqa: E402
from training.trainer import SelfPlayTrainer  # noqa: E402
from training.utils import play_game  # noqa: E402


G4_THRESHOLD = 0.10
DEFAULT_BUDGET = 3000
DEFAULT_EVAL_EPISODES = 200
DEFAULT_SEED = 42
DEFAULT_DB = HERE / "g4_smoke.db"
DEFAULT_MD = HERE / "g4_smoke.md"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db", required=True,
                   help="Source DB containing the games (R20.5 menger DB).")
    p.add_argument("--game-ids", nargs="+", required=True,
                   help="Game IDs to evaluate.")
    p.add_argument("--budget", type=int, default=DEFAULT_BUDGET,
                   help=f"PPO training budget per game (default {DEFAULT_BUDGET}).")
    p.add_argument("--eval-episodes", type=int, default=DEFAULT_EVAL_EPISODES,
                   help=f"Sampled mirror eval episodes (default {DEFAULT_EVAL_EPISODES}).")
    p.add_argument("--seed", type=int, default=DEFAULT_SEED)
    p.add_argument("--out-db", type=Path, default=DEFAULT_DB)
    p.add_argument("--out-md", type=Path, default=DEFAULT_MD)
    return p.parse_args()


def init_db(path: Path) -> sqlite3.Connection:
    if path.exists():
        path.unlink()
    con = sqlite3.connect(str(path))
    con.execute(
        """
        CREATE TABLE g4_results (
            game_id TEXT PRIMARY KEY,
            sampled_p1_winrate REAL,
            g4_seat_bias REAL,
            sampled_avg_length REAL,
            sampled_draw_rate REAL,
            greedy_p1_winrate REAL,
            greedy_seat_bias REAL,
            deterministic_p0_winrate REAL,
            passed_g4 INTEGER,
            elapsed_s REAL,
            ts TEXT
        )
        """
    )
    con.commit()
    return con


def sampled_mirror_eval(
    trainer: SelfPlayTrainer,
    num_episodes: int,
    max_steps: int,
) -> tuple[float, float, float]:
    """Sampled trained-vs-trained with seat-swap halves.

    Returns (p1_winrate, draw_rate, avg_length). p1_winrate = fraction of games
    won by seat 0 (first player), regardless of which trained agent occupied
    that seat.
    """
    half = num_episodes // 2
    p1_wins = 0
    draws = 0
    lengths: list[int] = []
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


def evaluate_one_game(game, *, budget: int, eval_eps: int, seed: int) -> dict:
    """Train PPO, then run sampled-mirror G4 eval + harness-style diagnostics."""
    cfg = TrainingConfig(training_budget=budget, eval_episodes=100)
    mcfg = MetricsConfig(learning_curve_checkpoints=2)
    trainer = SelfPlayTrainer(game, cfg, mcfg, seed=seed)
    max_steps = getattr(game, "max_game_steps", 200)

    t0 = time.time()
    trainer.train()
    diag = trainer.evaluate(num_episodes=100)  # deterministic + greedy diagnostics
    sampled_p1_wr, sampled_draws, sampled_len = sampled_mirror_eval(
        trainer, num_episodes=eval_eps, max_steps=max_steps,
    )
    elapsed = time.time() - t0

    g4_seat_bias = abs(sampled_p1_wr - 0.5)
    greedy_p1_wr = float(diag["greedy_p1_winrate"])
    return dict(
        sampled_p1_winrate=sampled_p1_wr,
        g4_seat_bias=g4_seat_bias,
        sampled_avg_length=sampled_len,
        sampled_draw_rate=sampled_draws,
        greedy_p1_winrate=greedy_p1_wr,
        greedy_seat_bias=abs(greedy_p1_wr - 0.5),
        deterministic_p0_winrate=float(diag["p0_winrate"]),
        elapsed_s=elapsed,
    )


def write_md(rows: list[dict], path: Path, budget: int, eval_eps: int, seed: int) -> None:
    n = len(rows)
    pass_cnt = sum(1 for r in rows if r["passed_g4"])
    lines = [
        "# R20.5 G4 — mirror seat bias < 0.10",
        "",
        f"PPO {budget} ep, seed {seed}, then sampled trained-vs-trained eval "
        f"(seat-swap, deterministic=False, n={eval_eps}). G4 metric = "
        f"`abs(sampled_p1_winrate - 0.5)`; threshold = {G4_THRESHOLD}.",
        "",
        "| Game | sampled_p1_wr | **G4 seat bias** | sampled_len | greedy_p1_wr | det_p0_wr | G4 | elapsed |",
        "|---|---:|---:|---:|---:|---:|:---:|---:|",
    ]
    for r in rows:
        verdict = "PASS" if r["passed_g4"] else "FAIL"
        lines.append(
            f"| `{r['game_id']}` | {r['sampled_p1_winrate']:.3f} | "
            f"**{r['g4_seat_bias']:.3f}** | "
            f"{r['sampled_avg_length']:.1f} | "
            f"{r['greedy_p1_winrate']:.3f} | "
            f"{r['deterministic_p0_winrate']:.3f} | "
            f"{verdict} | {r['elapsed_s']:.0f}s |"
        )
    lines.append("")
    if pass_cnt == n:
        lines.append(f"**G4: PASS ({n}/{n} < {G4_THRESHOLD})**")
    else:
        fails = ", ".join(f"`{r['game_id']}`" for r in rows if not r["passed_g4"])
        lines.append(f"**G4: FAIL ({pass_cnt}/{n} < {G4_THRESHOLD}) — failing: {fails}**")
    lines += [
        "",
        "## Methodology",
        "",
        "**G4 metric is sampled trained-vs-trained mirror seat-bias.** Greedy and "
        "deterministic-trained metrics are reported as diagnostics, NOT for the G4 "
        "verdict, because both are misleading on pie-rule games:",
        "",
        "- `greedy_p1_winrate`: GreedyAgent always-swaps under pie "
        "(commit `d25590d`). On a pie-rule game P2 trivially wins under "
        "greedy-vs-greedy regardless of equilibrium balance. Use as upper-bound "
        "rush-broken filter only — see harness.py:50.",
        "- `det_p0_wr` (deterministic trained): per harness module docstring, "
        "deterministic argmax collapses to identical 2-step games regardless of "
        "game quality. Not a real signal.",
        "- `sampled_p1_winrate` (the G4 metric): trained-vs-trained sampled play "
        "with seat-swap halves preserves the equilibrium where pie usage is "
        "rational. Deviation from 0.500 = real structural seat bias.",
        "",
    ]
    path.write_text("\n".join(lines))


def main() -> int:
    args = parse_args()
    con = init_db(args.out_db)
    rows: list[dict] = []

    for gid in args.game_ids:
        print(f"=== {gid} (budget={args.budget}, eval_eps={args.eval_episodes}, "
              f"seed={args.seed}) ===", flush=True)
        game = load_game(args.db, gid)
        result = evaluate_one_game(
            game, budget=args.budget, eval_eps=args.eval_episodes, seed=args.seed,
        )
        passed_g4 = bool(result["g4_seat_bias"] < G4_THRESHOLD)
        result["game_id"] = gid
        result["passed_g4"] = passed_g4
        rows.append(result)
        print(
            f"  sampled_p1_wr={result['sampled_p1_winrate']:.3f} "
            f"G4_bias={result['g4_seat_bias']:.3f} "
            f"sampled_len={result['sampled_avg_length']:.1f} "
            f"greedy_p1_wr={result['greedy_p1_winrate']:.3f} "
            f"det_p0_wr={result['deterministic_p0_winrate']:.3f} "
            f"G4={'PASS' if passed_g4 else 'FAIL'} ({result['elapsed_s']:.0f}s)",
            flush=True,
        )
        con.execute(
            """
            INSERT INTO g4_results VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now')
            )
            """,
            (
                gid,
                result["sampled_p1_winrate"], result["g4_seat_bias"],
                result["sampled_avg_length"], result["sampled_draw_rate"],
                result["greedy_p1_winrate"], result["greedy_seat_bias"],
                result["deterministic_p0_winrate"],
                int(passed_g4), result["elapsed_s"],
            ),
        )
        con.commit()

    con.close()
    write_md(rows, args.out_md, args.budget, args.eval_episodes, args.seed)
    print(f"DONE — DB: {args.out_db}, MD: {args.out_md}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
