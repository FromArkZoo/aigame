"""FRONTLINE Stage-1.5 drama diagnostic (prereg Stage 1.5 — the locked
authority). DIAGNOSTIC ONLY — never a comparative or bar.

DIAGNOSTIC-ONLY: no licensing role; Stage-2 GO is 2/2 comparatives.

Drama is demoted by registration: F's score-share trace
(progress_p = S_p / max(1, S_p + S_opp)) is closeness-by-construction —
the rc2_descriptor_v2 Goodhart relocated — and is incommensurable with
the component-span traces behind the on-disk DRAMA_ANCHORED result
(experiments/siege/RESULTS.md §3). This script therefore computes and
LOGS drama; it gates nothing.

Registered procedure (prereg Stage 1.5, verbatim semantics):
- Data: fresh --n 200 trace-instrumented self-play rollouts of the
  winning cell's seed-42 policy pair — retrained here at --budget 3000
  (deterministic, same policy as calibration; train_one is imported from
  calibrate.py unchanged). Seat orders mirrored (eval_cell_games
  convention: first half (0,1), second half (1,0); seat 0 = engine P1).
- Per game: progress_p(t) = S_p(t)/max(1, S_p+S_opp) recorded per ply
  (pie-swap plies skipped — the build_games/siege trace convention: a
  swap is ownership recolouring, not a placement);
  drama = winner_behindness(winner_trace, loser_trace).
- Draws are EXCLUDED from drama and counted in the report.
- Yellow flag: < 30% of games with per-game drama > 0.01 -> YELLOW
  (printed loudly; still not a gate).

The calibrated file games/calibrated/f_frontline.json exists only after
Stage 1 runs; --game overrides (loud error if the default is missing).

Usage:
    .venv/bin/python experiments/frontline/stage15_drama.py \\
        [--budget 3000] [--n 200] [--seed 42] [--game PATH]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from game_engine.factory import create_engine  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from experiments.frontline.calibrate import train_one  # noqa: E402
from experiments.frontline.metrics import (  # noqa: E402
    score_share_progress,
    winner_behindness,
)

HERE = Path(__file__).resolve().parent
DEFAULT_GAME = HERE / "games" / "calibrated" / "f_frontline.json"
OUT_MD = HERE / "stage15_drama.md"

DRAMA_EPS = 0.01      # per-game drama threshold for the share statistic
YELLOW_SHARE = 0.30   # yellow flag below this share (diagnostic, no gate)

DIAGNOSTIC_LINE = (
    "DIAGNOSTIC-ONLY: no licensing role; Stage-2 GO is 2/2 comparatives")
DEMOTION_LINE = (
    "Drama was demoted by registration (closeness Goodhart — "
    "rc2_descriptor_v2; F's score-share trace is "
    "closeness-by-construction).")

# On-disk anchored values, experiments/siege/RESULTS.md §3 (component-span
# traces — cross-family, printed for the writeup ONLY).
ANCHORED = (
    ("573 (R21 GE-bottom, agent-tied-1st)", "connection", 0.1765),
    ("a1_field_connect", "field_connection", 0.1324),
    ("a0_baseline", "threshold", 0.0536),
    ("e1453 (R21 GE-top, agent-ranked 6/7)", "threshold", 0.0458),
)
ANCHOR_CAVEAT = (
    "Caveat: the anchored values come from component-span progress "
    "traces; F's score-share trace is a different functional — "
    "cross-family traces are INCOMMENSURABLE. Printed for the "
    "post-campaign writeup only, never for comparison-as-evidence.")


def traced_selfplay_game(game: GameDefV2, a0, a1) -> dict:
    """One trace-instrumented self-play game (seat 0 = engine P1).

    Drives the loop directly (build_games._run_rollout pattern) so the
    per-ply contested scores are observable; play_game cannot expose
    them. Records progress_p per non-pie ply for both players, then
    computes per-game drama for the winner (None on draws — excluded
    from drama by registration).
    """
    engine = create_engine(game)
    obs = engine.reset()
    agents = [a0, a1]
    p1_trace: list[float] = []
    p2_trace: list[float] = []
    hard_cap = 2 * game.max_game_steps  # safety only; engine timeout < cap

    while not engine.done and engine.step_count < hard_cap:
        legal = engine.get_legal_actions()
        if not legal:
            raise RuntimeError(
                f"no legal actions with done=False at step "
                f"{engine.step_count} ({game.game_id})")
        mover = engine.get_current_player()  # 0-indexed, read BEFORE step
        action, _, _ = agents[mover].select_action(
            obs, legal_actions=legal, deterministic=False)
        obs, _, _, info = engine.step(action)
        if info.get("pie_swap"):
            # Swap plies place nothing; ownership recolouring is the swap
            # itself (build_games/siege trace convention) — skip.
            continue
        s1, s2, _ = engine.contested_scores()
        p1_trace.append(score_share_progress(s1, s2))
        p2_trace.append(score_share_progress(s2, s1))

    winner = engine._winner  # 1, 2, or None
    if not engine.done:
        end_cause = "hard_cap"   # should never fire (engine timeout first)
        winner = None
    elif engine._ended_by_score_margin:
        end_cause = "score_margin"
    elif engine._ended_by_double_pass:
        end_cause = "double_pass"
    elif engine._ended_by_max_turns:
        end_cause = "timeout"
    else:
        end_cause = "other"

    if winner == 1:
        drama = winner_behindness(p1_trace, p2_trace)
    elif winner == 2:
        drama = winner_behindness(p2_trace, p1_trace)
    else:
        drama = None  # draw — excluded from drama, counted in the report

    return dict(drama=drama, draw=(winner is None), end_cause=end_cause,
                length=engine.step_count)


def run_diagnostic(game: GameDefV2, trainer, n: int) -> dict:
    """n mirrored-seat trace-instrumented self-play games -> aggregates.

    ALL games enter every reported statistic (R21 survivorship pin);
    draws simply have no drama value, so the literal prereg share
    ('< 30% of GAMES with per-game drama > 0.01') keeps n as its
    denominator — a draw cannot satisfy the predicate.
    """
    half = n // 2
    results = []
    for i in range(n):
        order = (0, 1) if i < half else (1, 0)
        results.append(traced_selfplay_game(
            game, trainer.agents[order[0]], trainer.agents[order[1]]))
        if (i + 1) % 25 == 0:
            print(f"  game {i + 1}/{n}", flush=True)

    dramas = [r["drama"] for r in results if r["drama"] is not None]
    n_f = float(n)
    causes = [r["end_cause"] for r in results]
    high = sum(1 for d in dramas if d > DRAMA_EPS)
    share_all = high / n_f
    return dict(
        n=n,
        draws=sum(r["draw"] for r in results),
        decisive=len(dramas),
        mean_drama=(float(np.mean(dramas)) if dramas else float("nan")),
        high_count=high,
        share_all=share_all,
        share_decisive=(high / len(dramas) if dramas else float("nan")),
        yellow=share_all < YELLOW_SHARE,
        mean_length=float(np.mean([r["length"] for r in results])),
        end_cause_shares={
            c: causes.count(c) / n_f
            for c in ("score_margin", "double_pass", "timeout",
                      "hard_cap", "other")
            if causes.count(c)},
    )


def write_report(agg: dict, game_path: Path, budget: int, seed: int) -> str:
    flag = (f"**YELLOW** — share {agg['share_all']:.3f} < {YELLOW_SHARE} "
            "(diagnostic flag; still no gate)"
            if agg["yellow"] else
            f"clear (share {agg['share_all']:.3f} >= {YELLOW_SHARE})")
    causes = ", ".join(f"{c} {s:.3f}"
                       for c, s in agg["end_cause_shares"].items())
    lines = [
        "# FRONTLINE Stage-1.5 drama diagnostic",
        "",
        f"**{DIAGNOSTIC_LINE}**",
        "",
        DEMOTION_LINE,
        "",
        f"Game: `{game_path}`; policy pair retrained at seed {seed}, "
        f"budget {budget} (deterministic — same policy as calibration); "
        f"n={agg['n']} fresh trace-instrumented mirrored-seat self-play "
        "rollouts. progress_p(t) = S_p(t)/max(1, S_p+S_opp) per ply; "
        "drama = winner_behindness(winner_trace, loser_trace) "
        "(prereg formula, draws excluded from drama).",
        "",
        "## Results",
        "",
        f"- campaign mean drama (over {agg['decisive']} decisive games): "
        f"{agg['mean_drama']:.4f}",
        f"- games with per-game drama > {DRAMA_EPS}: {agg['high_count']}"
        f"/{agg['n']} = {agg['share_all']:.3f} of all games "
        f"({agg['share_decisive']:.3f} of decisive games)",
        f"- yellow flag (< {YELLOW_SHARE:.0%} of games with drama > "
        f"{DRAMA_EPS}): {flag}",
        f"- draws (EXCLUDED from drama, counted here): {agg['draws']}",
        f"- mean game length: {agg['mean_length']:.1f}",
        f"- end-cause shares: {causes}",
        "",
        "## Anchored values for the writeup (siege RESULTS.md §3)",
        "",
        "| game | family | DRAMA_ANCHORED |",
        "|---|---|---:|",
    ]
    lines += [f"| {name} | {fam} | {val:.4f} |" for name, fam, val in ANCHORED]
    lines += ["", ANCHOR_CAVEAT, ""]
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--budget", type=int, default=3000,
                   help="retrain budget (default 3000 — the calibration "
                        "budget, deterministic at --seed)")
    p.add_argument("--n", type=int, default=200,
                   help="fresh trace-instrumented self-play rollouts")
    p.add_argument("--seed", type=int, default=42,
                   help="winning cell's registered policy seed")
    p.add_argument("--game", default=str(DEFAULT_GAME),
                   help="game JSON (default: the Stage-1 calibrated file)")
    args = p.parse_args()

    game_path = Path(args.game)
    if not game_path.exists():
        raise SystemExit(
            f"MISSING GAME FILE: {game_path}\n"
            "games/calibrated/f_frontline.json is written by Stage 1 "
            "(calibrate.py) — run it first, or pass --game PATH "
            "explicitly.")
    game = GameDefV2.from_dict(json.loads(game_path.read_text()))

    print(f"=== Stage 1.5 drama — {DIAGNOSTIC_LINE} ===", flush=True)
    print(f"game {game_path} (game_id {game.game_id}, komi_cells "
          f"{game.win_condition.komi_cells:+d}); retraining seed "
          f"{args.seed} at budget {args.budget}", flush=True)
    t0 = time.time()
    trainer = train_one(game, args.budget, args.seed)
    print(f"trained in {time.time() - t0:.0f}s; playing {args.n} "
          "trace-instrumented self-play games", flush=True)

    agg = run_diagnostic(game, trainer, args.n)
    report = write_report(agg, game_path, args.budget, args.seed)
    OUT_MD.write_text(report)
    print(report, flush=True)
    if agg["yellow"]:
        print("YELLOW", flush=True)
    print(f"wrote {OUT_MD} ({time.time() - t0:.0f}s total)", flush=True)


if __name__ == "__main__":
    main()
