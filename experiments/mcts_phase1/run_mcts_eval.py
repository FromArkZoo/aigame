"""Phase-1 MCTS evaluator driver — empirical σ + scaling-curve preview.

For each of the 5 R18 stable-top games:
  - Fresh-train ``--reruns`` PPO seat-pairs (default 5).
  - For each trained pair, evaluate MCTS@N vs RandomAgent at sim counts
    {16, 64, 256} via seat-balanced paired games (default 8 per N).

Outputs:
  - mcts_eval.db (sidecar SQLite, one row per (game, rerun_idx, N))
  - per_run.csv
  - summary.md (per-game σ across reruns at each N, scaling slope σ,
    side-by-side with the 0.05–0.09 GE noise floor from
    ``experiments/r18_noise_floor/noise_floor_summary.md``)

The "scaling slope" is the candidate replacement-fitness preview asked
for in R19_postmortem.md § noise-floor — strength gain per doubling of
sims, computed per game from the {16, 64, 256} measurements:

    slope = (winrate@256 - winrate@16) / log2(256/16)
          = (winrate@256 - winrate@16) / 4

If the across-reruns σ of this slope sits below the existing 0.05–0.09
GE noise floor, the metric beats GE on stability and Phase 2 (OpenSpiel
or expanded sim ladder) becomes worthwhile. If not, this experiment is
the cheap negative result that says "don't adopt OpenSpiel yet".

Usage
-----
    python -m experiments.mcts_phase1.run_mcts_eval --smoke
    python -m experiments.mcts_phase1.run_mcts_eval --reruns 5 --eval-games 8
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import random
import sqlite3
import sys
import time
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from config import GenesisConfig  # noqa: E402
from game_engine.factory import create_engine  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from training.trainer import SelfPlayTrainer  # noqa: E402
from training.utils import GreedyAgent, RandomAgent, play_game  # noqa: E402

from experiments.mcts_phase1.mcts import MCTSAgent  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("mcts_eval")

# Same 5 R18 stable-top games used by the noise-floor experiment.
STABLE_TOPS = [
    {"substrate": "vicsek",   "dim": 1.465, "db": "genesis_v2_run18_vicsek.db",   "game_id": "1e11adebcc35"},
    {"substrate": "triangle", "dim": 1.585, "db": "genesis_v2_run18_triangle.db", "game_id": "558be82199a8"},
    {"substrate": "carpet",   "dim": 1.893, "db": "genesis_v2_run18_carpet.db",   "game_id": "8776b2026957"},
    {"substrate": "grid",     "dim": 2.000, "db": "genesis_v2_run18_grid.db",     "game_id": "ab7270a81cd6"},
    {"substrate": "menger",   "dim": 2.727, "db": "genesis_v2_run18_menger.db",   "game_id": "0f5e931fa3e1"},
]

DEFAULT_SIM_COUNTS = (16, 64, 256)
DEFAULT_RERUNS = 5
DEFAULT_EVAL_GAMES = 8        # seat-balanced; must be even
DEFAULT_TRAINING_BUDGET = 5000  # match noise-floor experiment


# ----------------------------------------------------------------------
# Args
# ----------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--mcts-eval", action="store_true", default=True,
                   help="enabled by default; flag exists so this script is "
                        "discoverable as 'the MCTS eval' and to mirror the "
                        "design language in R19_postmortem.md")
    p.add_argument("--smoke", action="store_true",
                   help="1 game × 1 rerun × {8, 16} sims × 2 eval games × 200 ep")
    p.add_argument("--substrates", nargs="*",
                   help="restrict to these substrate keys (vicsek/triangle/carpet/grid/menger)")
    p.add_argument("--reruns", type=int, default=DEFAULT_RERUNS)
    p.add_argument("--eval-games", type=int, default=DEFAULT_EVAL_GAMES,
                   help="paired (seat-balanced) games per (rerun, sim_count). Must be even.")
    p.add_argument("--budget", type=int, default=DEFAULT_TRAINING_BUDGET,
                   help="PPO training budget per fresh train")
    p.add_argument("--sim-counts", type=int, nargs="*", default=list(DEFAULT_SIM_COUNTS))
    p.add_argument("--opponent", choices=["random", "greedy", "ladder"],
                   default="random",
                   help="opponent strategy. 'random'/'greedy' = fixed baseline; "
                        "'ladder' = MCTS@(N/ladder_ratio) using the same nets, "
                        "which is saturation-proof and gives a structurally "
                        "scaling-curve-shaped metric. Ladder mode auto-enables "
                        "Dirichlet root noise so per-game variance is meaningful.")
    p.add_argument("--ladder-ratio", type=int, default=4,
                   help="ratio between MCTS@N and the ladder opponent's sims "
                        "(opponent = MCTS@(N // ladder_ratio), floored at 1).")
    p.add_argument("--dirichlet-eps", type=float, default=0.25,
                   help="Dirichlet root-noise epsilon for ladder mode "
                        "(ignored unless --opponent=ladder)")
    p.add_argument("--dirichlet-alpha", type=float, default=0.3,
                   help="Dirichlet root-noise alpha. AlphaZero default "
                        "0.3 is for ~361-action Go; for sparser action "
                        "spaces (e.g. triangle/vicsek), 10/n_actions ≈ "
                        "0.04 is more standard.")
    p.add_argument("--leaf-eval", choices=["value", "rollout"], default="value",
                   help="leaf evaluation: 'value' = net's value head "
                        "(AlphaZero); 'rollout' = random playout to "
                        "terminal (classic MCTS). Use 'rollout' to "
                        "diagnose value-head miscalibration.")
    p.add_argument("--bypass-validation", action="store_true",
                   help="set seeded_from to skip validate_game (matches noise-floor harness)")
    return p.parse_args()


# ----------------------------------------------------------------------
# IO helpers
# ----------------------------------------------------------------------

def load_game(db_path: str, game_id: str) -> GameDefV2:
    con = sqlite3.connect(str(ROOT / db_path))
    con.row_factory = sqlite3.Row
    row = con.execute(
        "SELECT rule_representation FROM games WHERE game_id = ?", (game_id,)
    ).fetchone()
    con.close()
    if row is None:
        raise SystemExit(f"game {game_id} not found in {db_path}")
    return GameDefV2.from_dict(json.loads(row["rule_representation"]))


def deterministic_seed(game_id: str, rerun_idx: int) -> int:
    """Namespace seeds under 'mcts_phase1' so they're disjoint from the
    R18 production seeds and the noise-floor experiment's seeds."""
    s = f"{game_id}:mcts_phase1:{rerun_idx}".encode("utf-8")
    return int(hashlib.md5(s).hexdigest()[:8], 16)


def init_db(path: Path) -> sqlite3.Connection:
    if path.exists():
        path.unlink()
    con = sqlite3.connect(str(path))
    con.execute("""
        CREATE TABLE IF NOT EXISTS rerun_eval (
            substrate TEXT, dim REAL, game_id TEXT,
            rerun_idx INTEGER, sim_count INTEGER,
            wins INTEGER, losses INTEGER, draws INTEGER,
            n_games INTEGER, winrate REAL,
            wallclock_seconds REAL, ts TEXT,
            PRIMARY KEY (game_id, rerun_idx, sim_count)
        )
    """)
    con.commit()
    return con


# ----------------------------------------------------------------------
# Train + evaluate one seat-pair
# ----------------------------------------------------------------------

def train_pair(game: GameDefV2, cfg: GenesisConfig, seed: int) -> SelfPlayTrainer:
    """Run SelfPlayTrainer.train() and return the trainer (for its agents)."""
    trainer = SelfPlayTrainer(game, cfg.training, cfg.metrics, seed=seed)
    trainer.train()
    return trainer


def play_mcts_vs_baseline(
    game: GameDefV2, nets, num_sims: int, n_games: int, rng_seed: int,
    opponent: str = "random", ladder_ratio: int = 4,
    dirichlet_eps: float = 0.25, dirichlet_alpha: float = 0.3,
    leaf_eval: str = "value",
) -> tuple[int, int, int]:
    """Play ``n_games`` seat-balanced games of MCTS@num_sims vs a baseline.

    Half the games MCTS plays seat 0 (P1), half seat 1 (P2). Returns
    (wins, losses, draws) from the strong MCTS's perspective.

    Opponent options:
      - 'random'  : RandomAgent (re-seeded per game)
      - 'greedy'  : GreedyAgent (re-seeded per game)
      - 'ladder'  : MCTSAgent at num_sims // ladder_ratio (floor 1) using
                    the same nets. Both sides get Dirichlet root noise so
                    paired games actually vary; without it both MCTSs are
                    deterministic and 8 paired games collapse to 2 unique
                    outcomes.
    """
    if n_games % 2 != 0:
        raise ValueError("n_games must be even (seat-balanced).")
    half = n_games // 2

    wins = losses = draws = 0
    max_steps = getattr(game, "max_game_steps", 200)
    is_ladder = opponent == "ladder"
    opp_sims = max(num_sims // ladder_ratio, 1) if is_ladder else 0

    for game_idx in range(n_games):
        engine = create_engine(game)
        opp_seed = (rng_seed * 1000003 + game_idx) & 0x7FFFFFFF

        if is_ladder:
            # Two distinct seeds so the strong and weak MCTS sample
            # independent Dirichlet draws at root.
            mcts_noise_seed = (rng_seed * 1000033 + game_idx * 7 + 1) & 0x7FFFFFFF
            mcts = MCTSAgent(
                engine, nets, num_sims=num_sims,
                dirichlet_eps=dirichlet_eps, dirichlet_alpha=dirichlet_alpha,
                leaf_eval=leaf_eval, rng_seed=mcts_noise_seed,
            )
            opp = MCTSAgent(
                engine, nets, num_sims=opp_sims,
                dirichlet_eps=dirichlet_eps, dirichlet_alpha=dirichlet_alpha,
                leaf_eval=leaf_eval, rng_seed=opp_seed,
            )
        else:
            mcts = MCTSAgent(engine, nets, num_sims=num_sims, leaf_eval=leaf_eval)
            if opponent == "greedy":
                opp_player_num = 2 if game_idx < half else 1
                opp = GreedyAgent(engine, player_num=opp_player_num, seed=opp_seed)
            else:
                opp = RandomAgent(seed=opp_seed)

        if game_idx < half:
            mcts_seat = 0
            agent0, agent1 = mcts, opp
        else:
            mcts_seat = 1
            agent0, agent1 = opp, mcts

        winner, _len, _r = play_game(
            engine, agent0, agent1, deterministic=True, max_steps=max_steps,
        )
        if winner is None:
            draws += 1
        elif winner == mcts_seat:
            wins += 1
        else:
            losses += 1

    return wins, losses, draws


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main() -> None:
    args = parse_args()

    games = STABLE_TOPS
    sim_counts = list(args.sim_counts)
    reruns = args.reruns
    n_eval = args.eval_games
    budget = args.budget

    if args.smoke:
        games = [STABLE_TOPS[3]]  # grid — smallest substrate, fastest train
        sim_counts = [8, 16]
        reruns = 1
        n_eval = 2
        budget = 200
        logger.info("SMOKE — 1 game × 1 rerun × sims %s × %d eval games × %d ep",
                    sim_counts, n_eval, budget)
    if args.substrates:
        games = [g for g in games if g["substrate"] in args.substrates]

    db_path = HERE / "mcts_eval.db"
    sidecar = init_db(db_path)

    cfg = GenesisConfig()
    cfg.training.training_budget = budget
    # num_independent_runs is ignored by SelfPlayTrainer.train() directly
    # (it's used by run_module's outer loop). One trainer.train() call =
    # one fresh seat-pair, which is what we want for σ measurement.

    for game_meta in games:
        substrate = game_meta["substrate"]
        gid = game_meta["game_id"]
        logger.info("=== %s top game %s (dim %.3f) ===",
                    substrate, gid, game_meta["dim"])
        game = load_game(game_meta["db"], gid)
        if args.bypass_validation:
            game.metadata["seeded_from"] = "mcts_phase1_bypass_validation"
        if game.turn_structure.turn_type == "simultaneous":
            logger.warning("  skipping — simultaneous turn type unsupported by Phase 1 MCTS")
            continue

        for k in range(reruns):
            seed = deterministic_seed(gid, k)
            logger.info("  rerun %d (seed %d) — training %d ep", k, seed, budget)

            t0 = time.time()
            random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
            trainer = train_pair(game, cfg, seed=seed)
            train_wall = time.time() - t0
            logger.info("    train wall: %.1fs", train_wall)

            nets = trainer.agents

            for N in sim_counts:
                t1 = time.time()
                wins, losses, draws = play_mcts_vs_baseline(
                    game, nets, num_sims=N, n_games=n_eval,
                    rng_seed=(seed + N), opponent=args.opponent,
                    ladder_ratio=args.ladder_ratio,
                    dirichlet_eps=args.dirichlet_eps,
                    dirichlet_alpha=args.dirichlet_alpha,
                    leaf_eval=args.leaf_eval,
                )
                wall = time.time() - t1
                wr = (wins + 0.5 * draws) / n_eval
                logger.info(
                    "    sims=%4d  W/L/D=%d/%d/%d  winrate=%.3f  (%.1fs)",
                    N, wins, losses, draws, wr, wall,
                )
                sidecar.execute(
                    "INSERT OR REPLACE INTO rerun_eval VALUES "
                    "(?,?,?,?,?,?,?,?,?,?,?,datetime('now'))",
                    (substrate, game_meta["dim"], gid, k, N,
                     wins, losses, draws, n_eval, wr, wall),
                )
                sidecar.commit()

    sidecar.close()
    write_csv_and_summary(db_path, sim_counts, opponent=args.opponent)
    logger.info("DONE — results at %s", db_path)


# ----------------------------------------------------------------------
# Reporting
# ----------------------------------------------------------------------

def write_csv_and_summary(
    db_path: Path, sim_counts: list[int], opponent: str = "random",
) -> None:
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT * FROM rerun_eval ORDER BY dim, game_id, rerun_idx, sim_count"
    ).fetchall()
    con.close()

    csv_lines = ["substrate,dim,game_id,rerun_idx,sim_count,wins,losses,draws,n_games,winrate,wallclock_seconds"]
    for r in rows:
        csv_lines.append(
            f"{r['substrate']},{r['dim']},{r['game_id']},{r['rerun_idx']},"
            f"{r['sim_count']},{r['wins']},{r['losses']},{r['draws']},"
            f"{r['n_games']},{r['winrate']:.4f},{r['wallclock_seconds']:.1f}"
        )
    (HERE / "per_run.csv").write_text("\n".join(csv_lines) + "\n")

    # Group by (game, sim_count) for σ; by game for slope.
    by_game_sim: dict[tuple, list[float]] = {}
    by_game: dict[tuple, dict[int, list[float]]] = {}
    for r in rows:
        key = (r["substrate"], r["dim"], r["game_id"])
        by_game_sim.setdefault((*key, r["sim_count"]), []).append(r["winrate"])
        by_game.setdefault(key, {}).setdefault(r["rerun_idx"], {})[r["sim_count"]] = r["winrate"]

    def mstd(xs: list[float]) -> tuple[float, float]:
        n = len(xs)
        if n == 0:
            return 0.0, 0.0
        m = sum(xs) / n
        v = sum((x - m) ** 2 for x in xs) / max(n - 1, 1)
        return m, v ** 0.5

    sim_counts_sorted = sorted(set(sim_counts))
    lines = [
        "# Phase-1 MCTS evaluator — results",
        "",
        f"Per-game empirical σ across reruns of MCTS@N-vs-{opponent} winrate, "
        f"at sim counts {sim_counts_sorted}.",
        "",
        "## Per-(game, sim_count) winrate",
        "",
        "| Substrate | Dim | Game | Sims | n_reruns | mean WR | σ WR | min | max |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for (substrate, dim, gid, N), wrs in sorted(by_game_sim.items(),
                                                key=lambda x: (x[0][1], x[0][3])):
        m, s = mstd(wrs)
        lines.append(
            f"| {substrate} | {dim} | `{gid}` | {N} | {len(wrs)} "
            f"| {m:.3f} | {s:.3f} | {min(wrs):.3f} | {max(wrs):.3f} |"
        )

    # Scaling-slope: per rerun, slope = (WR@max - WR@min) / log2(max/min).
    # Then σ across reruns.
    if len(sim_counts_sorted) >= 2:
        n_lo, n_hi = sim_counts_sorted[0], sim_counts_sorted[-1]
        doublings = float(np.log2(n_hi / n_lo))
        lines += [
            "",
            f"## Scaling-slope per game (N={n_lo} → N={n_hi}, {doublings:.1f} doublings)",
            "",
            "Slope = (WR@max − WR@min) / log2(max/min). σ across reruns is the "
            "noise floor of this candidate fitness metric.",
            "",
            "| Substrate | Dim | Game | n_reruns | mean slope | σ slope | mean Δ WR |",
            "|---|---|---|---:|---:|---:|---:|",
        ]
        for (substrate, dim, gid), per_rerun in sorted(by_game.items(),
                                                       key=lambda x: x[0][1]):
            slopes: list[float] = []
            deltas: list[float] = []
            for k, wrs_by_N in per_rerun.items():
                if n_lo in wrs_by_N and n_hi in wrs_by_N:
                    delta = wrs_by_N[n_hi] - wrs_by_N[n_lo]
                    slopes.append(delta / doublings)
                    deltas.append(delta)
            sm, ss = mstd(slopes)
            dm, _ = mstd(deltas)
            lines.append(
                f"| {substrate} | {dim} | `{gid}` | {len(slopes)} "
                f"| {sm:+.4f} | {ss:.4f} | {dm:+.3f} |"
            )

    lines += [
        "",
        "## Comparison against GE noise floor",
        "",
        "From `experiments/r18_noise_floor/noise_floor_summary.md`, the "
        "production-stack GE σ floor is **0.05–0.09** on top games "
        "(menger 0.091, carpet 0.072, triangle 0.056). The Phase-1 σ "
        "columns above measure noise on a *different* metric: winrate "
        "in [0, 1] and slope in [-0.25, 0.25] (max), vs GE in roughly "
        "[0, 0.4]. Direct numeric comparison is approximate; the "
        "meaningful signal is whether **slope σ < 0.03** (roughly a "
        "third of GE σ on its own scale).",
        "",
        "**Decision criteria for Phase 2 (OpenSpiel / expanded ladder):**",
        "- slope σ ≤ 0.02 on all 5 substrates: scaling slope is a viable "
        "  GE replacement → Phase 2 worth doing.",
        "- slope σ in 0.02–0.05: marginal → Phase 2 only on substrates "
        "  that look promising.",
        "- slope σ > 0.05 broadly: Phase 1 MCTS doesn't beat GE → hold "
        "  off on OpenSpiel and revisit metric design instead.",
        "",
        f"**Opponent.** Configured as `{opponent}`. For `ladder` mode the "
        "weak side is MCTS@(N/ladder_ratio) using the same nets, with "
        "Dirichlet root noise on both sides for per-game variance. "
        "Ladder is saturation-proof — winrate stays around 0.5–0.8 "
        "regardless of overall policy strength, so the slope reflects "
        "true sim-budget value rather than baseline weakness.",
    ]
    (HERE / "summary.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
