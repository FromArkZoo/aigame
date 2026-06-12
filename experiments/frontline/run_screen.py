"""FRONTLINE Stage-2 — 4-arm mechanical screen (PREREGISTRATION.md "Stage 2 screen").

Per arm (f_frontline, s_flip_r2, a1_field_connect, a0_baseline) x 3 PPO
seeds: train (budget 5000), then an instrumented sampled trained-vs-trained
mirror eval (n=200/seed, seat-swap halves — all four arms are symmetric)
recording the pre-registered signals. f_frontline loads from
games/calibrated/ (the Stage-1 winner with its komi baked in); s/a1/a0
retrain from games/ (verbatim probe-calibrated copies, per prereg).

All statistics are computed over EVERY eval game of the 3 final seeds; no
game- or seed-level filtering of any comparative or band (R21 Probe B
survivorship lesson).

Comparatives (DIRECTIONAL, f_frontline vs s_flip_r2, arm means — GO = 2/2):
  1. control_flip_rate: F - S >= +0.5 absolute (identical r=2
     instrumentation — the registered cross-arm comparable).
  2. game_length centrality, band [30,160] center 95: F >= 10 turns more
     central than S (F must itself sit in the band — siege template
     semantics, matching the prereg's band citation).
NO drama comparative: drama is DIAGNOSTIC-ONLY by registration (closeness
Goodhart — prereg Stage 1.5). It is computed and REPORTED per arm
(clearly labeled DIAGNOSTIC): F via score_share_progress traces over
engine.contested_scores(); S/A1/A0 via the siege-style component-span /
threshold traces, which the ported instrumentation provides at no extra
rollout cost. F's score-share drama is incommensurable with the
component-span values — report-only, never compared.

Band-only sanity, scored on F: flip events/game in [1,20] AND
distinct-stones-flipped >= 0.5 x events; engaged_share in [0.02, 0.60];
timeout <= 0.25, draw <= 0.05, score_margin share >= 0.25 (re-asserted at
5000); tvr gates as Stage 1 (mean >= 0.75, no seed < 0.65) with mandatory
per-seed inspection; seat bias <= 0.10; packing-scores-zero re-assert
(MutualPacker mirror on the calibrated F config, mean total score <= 2);
exploiter bands (trained F beats PassBot >= 0.90 and MirrorAgent >= 0.70,
EACH seat, win share pooled across seeds as a ratio of totals).

Comparator health (S/A1/A0 owe only this): bias <= 0.10, no collapsed
seed (tvr < 0.20), tvr mean >= 0.75. Failure -> CAMPAIGN_UNRESOLVED —
comparator failure (<arm>) -> one retrain; NEVER a family verdict
(prereg "Comparator-failure rule"). A collapsed F screen seed is likewise
CAMPAIGN_UNRESOLVED (the Stage-1 reserve/rerun ladder is calibration
machinery and does not apply at screen time).

Instrumentation-reproduction check (A0's registered job): a1 - a0
control_flip_rate >= 3.0 (on-disk 10.6 vs 5.3); failure ->
instrumentation INVALID -> CAMPAIGN_UNRESOLVED, never a family verdict.

Verdict: SCREEN_GO (2/2 comparatives + ALL F bands + comparator health +
reproduction check) / SCREEN_NOGO (no blind, campaign NO-GO) /
CAMPAIGN_UNRESOLVED. Exit codes: GO 0, NOGO 1, UNRESOLVED 2.
Outputs: screen_results.csv (per-seed rows) + screen_results.md (every
bar decision visible).

Adaptations vs the siege template (documented, instrumentation-level):
  - All four arms are symmetric (pie ON): the asym Maker/Breaker branches,
    per_role_tvr, role matrix, and the z_flip_r2 stop rule are removed —
    frontline has NO F-absent screen (F fails -> campaign NO-GO).
  - tvr comes from calibrate.trained_vs_random (the Stage-1 statistic the
    prereg re-asserts), not trainer.evaluate's diagnostic.
  - flip_events are counted by board-diff (enemy -> mover ownership change
    on the mover's ply; build_games._run_rollout pattern) for ALL arms —
    the same event class as siege's symmetric piece-count drops, and it
    yields the distinct-cells set the F band needs directly.
    distinct_flip_ratio aggregates as sum(distinct)/max(1, sum(events))
    (ratio of totals — siege convention).
  - F lead proxy (reference rows only, no bar): engine lead semantics
    s1 - (s2 + komi_cells), sign flips zeros-skipped.
  - Seat bias uses the registered Stage-1 statistic
    |p1_share + draw_rate/2 - 0.5|, arm bias = mean over seeds of per-seed
    |draw-adjusted bias| (conservative when seed signs differ).

Usage:
    .venv/bin/python experiments/frontline/run_screen.py \
        [--budget 5000] [--eval-episodes 200] [--seeds 42,43,44] \
        [--calibrated-dir experiments/frontline/games/calibrated] \
        [--game-override PATH]   # plumbing tests ONLY — marks the run
                                 # NON-REGISTERED in every output
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

from game_engine.factory import create_engine  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402

from experiments.field_connect_probe.calibrate import play_game  # noqa: E402
from experiments.field_connect_probe.metrics import (  # noqa: E402
    count_lead_changes,
    progress_diff_field,
    progress_diff_threshold,
)
from experiments.fc_phase15.metrics import (  # noqa: E402
    controller_signs,
    count_controller_changes,
)
from experiments.siege.anchor_drama import (  # noqa: E402
    threshold_progress_p1,
    threshold_progress_p2,
)
from experiments.siege.metrics import maker_progress_span  # noqa: E402
from experiments.frontline.calibrate import (  # noqa: E402
    COLLAPSE_TVR,
    bias_value,
    train_one,
    trained_vs_random,
)
from experiments.frontline.metrics import (  # noqa: E402
    score_share_progress,
    winner_behindness,
)
from experiments.frontline.scripted_agents import (  # noqa: E402
    MirrorAgent,
    MutualPacker,
    PassBot,
)

HERE = Path(__file__).resolve().parent
GAMES_DIR = HERE / "games"

# ---------------------------------------------------------------------------
# Pre-registered Stage-2 constants — experiments/frontline/PREREGISTRATION.md
# ("Stage 2 screen"). Not altered after data.
# ---------------------------------------------------------------------------
ARMS = ("f_frontline", "s_flip_r2", "a1_field_connect", "a0_baseline")
LENGTH_BAND = (30.0, 160.0)
LENGTH_CENTER = 95.0
FLIP_DELTA_FLOOR = 0.5        # comparative 1: F - S >= +0.5 (DIRECTIONAL)
CENTRALITY_FLOOR = 10.0       # comparative 2: F >= 10 turns more central
COMPARATIVE_GO_MIN = 2        # GO = 2/2 (drama demoted by registration)
FLIP_EVENTS_BAND = (1.0, 20.0)
DISTINCT_FLIP_RATIO_MIN = 0.5
TIMEOUT_SHARE_MAX = 0.25
DRAW_RATE_MAX = 0.05
SCORE_MARGIN_SHARE_MIN = 0.25
ENGAGED_BAND = (0.02, 0.60)
BIAS_PASS = 0.10
TVR_MEAN_MIN, TVR_SEED_MIN = 0.75, 0.65
PASSBOT_BEAT_MIN = 0.90       # exploiter bands, each seat
MIRROR_BEAT_MIN = 0.70
A1_A0_FLIP_REPRO_MIN = 3.0    # instrumentation-reproduction check
PACKER_SCORE_MAX = 2.0

EXPLOITER_GAMES = 50          # games per (opponent, seat) per seed
PACKER_GAMES = 100            # MutualPacker-vs-MutualPacker re-assert games

F, S, A1, A0 = ARMS
COMPARATOR_ARMS = (S, A1, A0)


def arm_kind(game: GameDefV2) -> str:
    """'contested' (FRONTLINE F), 'field' (S/A1), or 'threshold' (A0)."""
    wc = game.win_condition
    if wc.condition_type == "contested_majority":
        return "contested"
    if wc.condition_type == "field_connection":
        return "field"
    if wc.condition_type == "threshold":
        return "threshold"
    raise ValueError(f"unsupported win condition for screen: "
                     f"{wc.condition_type} ({game.game_id})")


def resolve_axes(game: GameDefV2, engine) -> tuple[int, int]:
    """(p1_axis, p2_axis) for field arms, mirroring engine_v2._check_win
    field_connection dispatch: P2 axis = target_dimension_p2 if >= 0 else
    (target+1) % dims; after a pie swap (_goals_swapped) the axes swap
    with the goals. (siege run_screen verbatim.)"""
    wc = game.win_condition
    p1_axis = wc.target_dimension
    p2_axis = wc.target_dimension_p2
    if p2_axis < 0:
        p2_axis = (p1_axis + 1) % game.num_dimensions
    if engine._goals_swapped:
        p1_axis, p2_axis = p2_axis, p1_axis
    return p1_axis, p2_axis


# ---------------------------------------------------------------------------
# Instrumented episode (siege flip/control instrumentation + F traces)
# ---------------------------------------------------------------------------

def instrumented_episode(game: GameDefV2, a0, a1, kind: str) -> dict:
    """One sampled game with per-step metric + per-player progress traces."""
    engine = create_engine(game)
    obs = engine.reset()
    agents = [a0, a1]
    wc = game.win_condition
    margin = getattr(wc, "control_margin", 0.0)
    komi = float(getattr(wc, "komi_cells", 0) or 0)
    board = engine.board_owners  # live array (build_games._run_rollout pattern)
    prev_signs = controller_signs(engine, margin)
    flip_events = 0
    flipped_cells: set[int] = set()
    diffs: list[float] = []
    flips: list[int] = []
    p1_trace: list[float] = []
    p2_trace: list[float] = []
    hard_cap = 2 * game.max_game_steps

    while not engine.done and engine.step_count < hard_cap:
        legal = engine.get_legal_actions()
        if not legal:
            raise RuntimeError(
                f"no legal actions with done=False at step "
                f"{engine.step_count} ({game.game_id})"
            )
        mover = engine.get_current_player()  # seat index, read BEFORE step
        agent = agents[mover]
        prev_owners = board.copy()
        action, _, _ = agent.select_action(
            obs, legal_actions=legal, deterministic=False,
        )
        obs, _, done, info = engine.step(action)
        cur_signs = controller_signs(engine, margin)
        if not info.get("pie_swap"):
            # Flip events: cells that changed owner enemy -> mover across
            # the ply (board-diff; placements fill empty cells and are
            # excluded by construction).
            mover_owner = mover + 1
            enemy_owner = 3 - mover_owner
            ply_flips = np.nonzero(
                (prev_owners == enemy_owner) & (board == mover_owner))[0]
            if ply_flips.size:
                flip_events += int(ply_flips.size)
                flipped_cells.update(int(c) for c in ply_flips)
            if kind == "contested":
                s1, s2, _ = engine.contested_scores()
                p1_trace.append(score_share_progress(s1, s2))
                p2_trace.append(score_share_progress(s2, s1))
                # F lead proxy (reference only): engine lead semantics.
                diffs.append(s1 - (s2 + komi))
            elif kind == "field":
                ax1, ax2 = resolve_axes(game, engine)
                p1_trace.append(maker_progress_span(engine, 1, ax1, margin))
                p2_trace.append(maker_progress_span(engine, 2, ax2, margin))
                diffs.append(progress_diff_field(engine, margin))
            else:  # threshold (a0) — per-player split per anchor_drama.py
                p1_trace.append(threshold_progress_p1(engine))
                p2_trace.append(threshold_progress_p2(engine))
                diffs.append(progress_diff_threshold(engine))
            flips.append(count_controller_changes(prev_signs, cur_signs))
        prev_signs = cur_signs

    winner = engine._winner
    timeout = engine._ended_by_max_turns
    if not engine.done:
        # Hard-cap exit — should never fire (engine timeout < cap); labeled
        # "hard_cap" to match stage15_drama.py, not folded into "other".
        end_cause = "hard_cap"
    else:
        # End-cause classification (same expression as calibrate.py).
        end_cause = ("score_margin" if engine._ended_by_score_margin
                     else "double_pass" if engine._ended_by_double_pass
                     else "timeout" if timeout else "other")
    if winner == 1:
        drama = winner_behindness(p1_trace, p2_trace)
    elif winner == 2:
        drama = winner_behindness(p2_trace, p1_trace)
    else:
        drama = None  # draws skipped from drama (diagnostic convention)
    engaged_final = None
    if kind == "contested":
        _, _, engaged = engine.contested_scores()
        engaged_final = engaged / engine.topo.num_active_cells
    return dict(
        length=engine.step_count,
        flip_events=flip_events,
        distinct_flips=len(flipped_cells),
        lead_changes=count_lead_changes(diffs),
        control_flips=float(np.mean(flips)) if flips else 0.0,
        end_cause=end_cause,
        timeout=bool(timeout),
        draw=(winner is None),
        p1_win=(winner == 1),
        p2_win=(winner == 2),
        drama=drama,
        engaged_final=engaged_final,
    )


# ---------------------------------------------------------------------------
# Per-(arm, seed) screen unit
# ---------------------------------------------------------------------------

def screen_one(game: GameDefV2, arm: str, kind: str, seed: int,
               budget: int, eval_eps: int) -> tuple[dict, object]:
    """Train one seed, then the instrumented seat-swapped mirror eval.
    ALL games enter every statistic (prereg survivorship pin)."""
    t0 = time.time()
    trainer = train_one(game, budget, seed)
    tvr = trained_vs_random(trainer, n=max(10, eval_eps // 2))

    eps = []
    half = eval_eps // 2
    for i in range(eval_eps):
        if i < half:
            a, b = trainer.agents[0], trainer.agents[1]
        else:
            a, b = trainer.agents[1], trainer.agents[0]
        eps.append(instrumented_episode(game, a, b, kind))

    n = max(len(eps), 1)
    p1_share = sum(e["p1_win"] for e in eps) / n
    draw_rate = sum(e["draw"] for e in eps) / n
    dramas = [e["drama"] for e in eps if e["drama"] is not None]
    engaged = [e["engaged_final"] for e in eps
               if e["engaged_final"] is not None]
    row = dict(
        arm=arm,
        game_id=game.game_id,
        seed=seed,
        game_length=float(np.mean([e["length"] for e in eps])),
        lead_changes=float(np.mean([e["lead_changes"] for e in eps])),
        control_flip_rate=float(np.mean([e["control_flips"] for e in eps])),
        drama=(float(np.mean(dramas)) if dramas else None),
        flip_events=float(np.mean([e["flip_events"] for e in eps])),
        flip_events_total=int(sum(e["flip_events"] for e in eps)),
        distinct_flips_total=int(sum(e["distinct_flips"] for e in eps)),
        timeout_share=sum(e["timeout"] for e in eps) / n,
        draw_rate=draw_rate,
        score_margin_share=sum(
            e["end_cause"] == "score_margin" for e in eps) / n,
        double_pass_share=sum(
            e["end_cause"] == "double_pass" for e in eps) / n,
        engaged_mean=(float(np.mean(engaged)) if engaged else None),
        p1_share=p1_share,
        bias=bias_value(p1_share, draw_rate),
        tvr=tvr,
        collapsed=(tvr < COLLAPSE_TVR),
        elapsed_s=time.time() - t0,
    )
    return row, trainer


# ---------------------------------------------------------------------------
# Exploiter bands + packer re-assert (prereg Stage 2, F only)
# ---------------------------------------------------------------------------

def pool_shares(blocks: list[tuple[int, int]]) -> float:
    """Pooled win share over (wins, n) blocks — ratio of totals
    (the registered pooling: win share per seat pooled over seeds)."""
    wins = sum(w for w, _ in blocks)
    n = sum(n for _, n in blocks)
    return wins / max(1, n)


def exploiter_bands(game: GameDefV2, trainers: list,
                    n_games: int = EXPLOITER_GAMES) -> dict:
    """For each seed's trained F pair: n_games vs PassBot and n_games vs
    MirrorAgent, EACH seat. Returns pooled-per-(opponent, seat) win shares
    {'passbot': {'p1': x, 'p2': y}, 'mirror': {...}} — BOTH seats must
    clear the floor (checked in f_band_checks)."""
    opponents = {"passbot": PassBot, "mirror": MirrorAgent}
    blocks: dict[str, dict[str, list[tuple[int, int]]]] = {
        opp: {"p1": [], "p2": []} for opp in opponents}
    max_steps = 2 * game.max_game_steps
    for trainer in trainers:
        engine = create_engine(game)
        for opp_name, opp_cls in opponents.items():
            # Trained pair seat-faithful: agents[0] plays seat 0 (P1),
            # agents[1] plays seat 1 (P2) — fresh bound opponent per game.
            wins = 0
            for _ in range(n_games):
                opp = opp_cls(player=2).bind(engine)
                winner, _, _ = play_game(
                    engine, trainer.agents[0], opp,
                    deterministic=False, max_steps=max_steps)
                wins += int(winner == 0)
            blocks[opp_name]["p1"].append((wins, n_games))
            wins = 0
            for _ in range(n_games):
                opp = opp_cls(player=1).bind(engine)
                winner, _, _ = play_game(
                    engine, opp, trainer.agents[1],
                    deterministic=False, max_steps=max_steps)
                wins += int(winner == 1)
            blocks[opp_name]["p2"].append((wins, n_games))
    return {opp: {seat: pool_shares(blocks[opp][seat])
                  for seat in ("p1", "p2")}
            for opp in opponents}


def packer_reassert(game: GameDefV2, n_games: int = PACKER_GAMES) -> float:
    """Packing-scores-zero re-assert on the calibrated F config:
    MutualPacker vs MutualPacker, mean(s1 + s2 final). The pairing is
    deterministic (n identical games — run as registered)."""
    engine = create_engine(game)
    max_steps = 2 * game.max_game_steps
    totals = []
    for _ in range(n_games):
        a = MutualPacker(player=1).bind(engine)
        b = MutualPacker(player=2).bind(engine)
        play_game(engine, a, b, deterministic=False, max_steps=max_steps)
        s1, s2, _ = engine.contested_scores()
        totals.append(s1 + s2)
    return float(np.mean(totals))


# ---------------------------------------------------------------------------
# Pure aggregation + bar logic (testable without training —
# test_frontline_screen.py; same pattern as calibrate.py's apply_gates)
# ---------------------------------------------------------------------------

def arm_agg(rows: list[dict], arm: str) -> dict:
    """Arm-level aggregates over per-seed rows (means over seeds; the
    distinct-flip ratio is a ratio of totals — siege convention)."""
    sub = [r for r in rows if r["arm"] == arm]

    def mean(key: str) -> float:
        vals = [r[key] for r in sub if r[key] is not None]
        return float(np.mean(vals)) if vals else float("nan")

    events_total = sum(r["flip_events_total"] for r in sub)
    return dict(
        control_flip_rate=mean("control_flip_rate"),
        game_length=mean("game_length"),
        lead_changes=mean("lead_changes"),
        drama=mean("drama"),
        flip_events=mean("flip_events"),
        distinct_flip_ratio=(
            sum(r["distinct_flips_total"] for r in sub)
            / max(1, events_total)),
        engaged_mean=mean("engaged_mean"),
        timeout_share=mean("timeout_share"),
        draw_rate=mean("draw_rate"),
        score_margin_share=mean("score_margin_share"),
        double_pass_share=mean("double_pass_share"),
        bias=mean("bias"),
        tvr_mean=mean("tvr"),
        tvr_min=(min(r["tvr"] for r in sub) if sub else float("nan")),
        tvr_by_seed={r["seed"]: r["tvr"] for r in sub},
        collapsed_seeds=[r["seed"] for r in sub if r["collapsed"]],
    )


def build_aggs(rows: list[dict], exploiter: dict,
               packer_mean_total: float) -> dict:
    return dict(
        arms={arm: arm_agg(rows, arm) for arm in ARMS},
        exploiter=exploiter,
        packer_mean_total=packer_mean_total,
    )


def in_band(x: float) -> bool:
    return LENGTH_BAND[0] <= x <= LENGTH_BAND[1]


def comparative_checks(f: dict, s: dict) -> list[tuple[str, float, str, bool]]:
    """The two DIRECTIONAL comparatives (prereg-verbatim floors).
    Returns (name, value, floor description, win?) rows."""
    flip_delta = f["control_flip_rate"] - s["control_flip_rate"]
    centrality_gain = (abs(s["game_length"] - LENGTH_CENTER)
                       - abs(f["game_length"] - LENGTH_CENTER))
    return [
        ("control_flip_rate delta (F - S)", flip_delta,
         f">= +{FLIP_DELTA_FLOOR} absolute",
         flip_delta >= FLIP_DELTA_FLOOR),
        ("game_length centrality gain", centrality_gain,
         f">= {CENTRALITY_FLOOR:.0f} turns more central (center "
         f"{LENGTH_CENTER:.0f}, F in [{LENGTH_BAND[0]:.0f},"
         f"{LENGTH_BAND[1]:.0f}])",
         in_band(f["game_length"]) and centrality_gain >= CENTRALITY_FLOOR),
    ]


def f_band_checks(f: dict, exploiter: dict,
                  packer_mean_total: float) -> list[tuple[str, float, bool]]:
    """ALL must hold for GO. Returns (name, value, pass?) rows — every bar
    decision visible in the report."""
    return [
        (f"flip_events/game in [{FLIP_EVENTS_BAND[0]:.0f},"
         f"{FLIP_EVENTS_BAND[1]:.0f}]", f["flip_events"],
         FLIP_EVENTS_BAND[0] <= f["flip_events"] <= FLIP_EVENTS_BAND[1]),
        (f"distinct_flip_ratio >= {DISTINCT_FLIP_RATIO_MIN}",
         f["distinct_flip_ratio"],
         f["distinct_flip_ratio"] >= DISTINCT_FLIP_RATIO_MIN),
        (f"engaged_share in [{ENGAGED_BAND[0]}, {ENGAGED_BAND[1]}]",
         f["engaged_mean"],
         ENGAGED_BAND[0] <= f["engaged_mean"] <= ENGAGED_BAND[1]),
        (f"timeout_share <= {TIMEOUT_SHARE_MAX} (re-asserted)",
         f["timeout_share"], f["timeout_share"] <= TIMEOUT_SHARE_MAX),
        (f"draw_rate <= {DRAW_RATE_MAX} (re-asserted)",
         f["draw_rate"], f["draw_rate"] <= DRAW_RATE_MAX),
        (f"score_margin_share >= {SCORE_MARGIN_SHARE_MIN} (re-asserted)",
         f["score_margin_share"],
         f["score_margin_share"] >= SCORE_MARGIN_SHARE_MIN),
        (f"tvr mean >= {TVR_MEAN_MIN} AND no seed < {TVR_SEED_MIN} "
         f"(Stage-1 gates; per-seed inspection below)", f["tvr_mean"],
         f["tvr_mean"] >= TVR_MEAN_MIN and f["tvr_min"] >= TVR_SEED_MIN),
        (f"seat bias <= {BIAS_PASS}", f["bias"], f["bias"] <= BIAS_PASS),
        (f"packer re-assert: mean total score <= {PACKER_SCORE_MAX}",
         packer_mean_total, packer_mean_total <= PACKER_SCORE_MAX),
        (f"exploiter: beats PassBot >= {PASSBOT_BEAT_MIN} (seat P1)",
         exploiter["passbot"]["p1"],
         exploiter["passbot"]["p1"] >= PASSBOT_BEAT_MIN),
        (f"exploiter: beats PassBot >= {PASSBOT_BEAT_MIN} (seat P2)",
         exploiter["passbot"]["p2"],
         exploiter["passbot"]["p2"] >= PASSBOT_BEAT_MIN),
        (f"exploiter: beats Mirror >= {MIRROR_BEAT_MIN} (seat P1)",
         exploiter["mirror"]["p1"],
         exploiter["mirror"]["p1"] >= MIRROR_BEAT_MIN),
        (f"exploiter: beats Mirror >= {MIRROR_BEAT_MIN} (seat P2)",
         exploiter["mirror"]["p2"],
         exploiter["mirror"]["p2"] >= MIRROR_BEAT_MIN),
    ]


def comparator_health(arm: str, a: dict) -> tuple[bool, str]:
    """Prereg comparator-failure rule inputs: collapsed seed, bias, tvr."""
    problems = []
    if a["collapsed_seeds"]:
        problems.append(f"collapsed seed(s) {a['collapsed_seeds']} "
                        f"(tvr < {COLLAPSE_TVR})")
    if not (a["bias"] <= BIAS_PASS):
        problems.append(f"bias {a['bias']:.3f} > {BIAS_PASS}")
    if not (a["tvr_mean"] >= TVR_MEAN_MIN):
        problems.append(f"tvr mean {a['tvr_mean']:.3f} < {TVR_MEAN_MIN}")
    if problems:
        return False, "; ".join(problems)
    return True, (f"bias {a['bias']:.3f}, tvr mean {a['tvr_mean']:.3f}, "
                  f"no collapsed seed")


def repro_check(aggs: dict) -> tuple[float, bool]:
    """A0's registered job: a1 - a0 control_flip_rate >= 3.0."""
    delta = (aggs["arms"][A1]["control_flip_rate"]
             - aggs["arms"][A0]["control_flip_rate"])
    return delta, delta >= A1_A0_FLIP_REPRO_MIN


def screen_verdict(aggs: dict) -> tuple[str, list[str]]:
    """Pure prereg verdict over the aggregate dict.

    Precedence: validity failures (comparator health, collapsed F screen
    seed, instrumentation reproduction) -> CAMPAIGN_UNRESOLVED, NEVER a
    family verdict — they invalidate the comparison, so they dominate any
    GO/NOGO reading. Then GO = 2/2 comparatives + ALL F bands.
    """
    unresolved: list[str] = []
    for arm in COMPARATOR_ARMS:
        ok, detail = comparator_health(arm, aggs["arms"][arm])
        if not ok:
            unresolved.append(f"comparator failure ({arm}): {detail} — "
                              f"one retrain (prereg comparator-failure "
                              f"rule), never a family verdict")
    f = aggs["arms"][F]
    if f["collapsed_seeds"]:
        unresolved.append(
            f"collapsed screen seed ({F}): seed(s) {f['collapsed_seeds']} "
            f"tvr < {COLLAPSE_TVR} — the Stage-1 rerun ladder does not "
            f"apply at screen time; not a family verdict")
    delta, ok = repro_check(aggs)
    if not ok:
        unresolved.append(
            f"instrumentation reproduction FAILED: a1 - a0 "
            f"control_flip_rate {delta:.3f} < {A1_A0_FLIP_REPRO_MIN} "
            f"(on-disk 10.6 vs 5.3) — instrumentation INVALID, never a "
            f"family verdict")
    if unresolved:
        return "CAMPAIGN_UNRESOLVED", unresolved

    comps = comparative_checks(f, aggs["arms"][S])
    comp_wins = sum(ok for *_, ok in comps)
    bands = f_band_checks(f, aggs["exploiter"], aggs["packer_mean_total"])
    bands_ok = all(ok for *_, ok in bands)
    if comp_wins >= COMPARATIVE_GO_MIN and bands_ok:
        return "SCREEN_GO", [
            f"{comp_wins}/{len(comps)} comparatives + ALL F bands + "
            f"comparator health + instrumentation-reproduction check — "
            f"blind campaign runs F vs S vs A1 (PREREGISTRATION.md "
            f"Stage 3)"]
    reasons = [f"{comp_wins}/{len(comps)} comparatives "
               f"(GO needs {COMPARATIVE_GO_MIN}/{len(comps)})"]
    reasons += [f"comparative FAIL: {name} = {val:.3f} (floor {floor})"
                for name, val, floor, ok in comps if not ok]
    reasons += [f"band FAIL: {name} = {val:.3f}"
                for name, val, ok in bands if not ok]
    return "SCREEN_NOGO", reasons


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------

def _fmt(v) -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    return f"{v:.3f}"


def build_md(aggs: dict, rows: list[dict], verdict: str,
             reasons: list[str], run_info: str,
             override_note: str | None) -> str:
    f = aggs["arms"][F]
    md = ["# FRONTLINE Stage-2 — 4-arm mechanical screen", "",
          run_info, "",
          "All statistics computed over EVERY eval game of the 3 final "
          "seeds; no game- or seed-level filtering of any comparative or "
          "band (R21 Probe B survivorship lesson). Bars per "
          "experiments/frontline/PREREGISTRATION.md Stage 2.", ""]
    if override_note:
        md += [f"**{override_note}**", ""]

    # --- Comparatives (DIRECTIONAL, GO = 2/2; NO drama comparative) ----
    comps = comparative_checks(f, aggs["arms"][S])
    comp_wins = sum(ok for *_, ok in comps)
    md += [f"## Comparatives — {F} vs {S} (arm means, DIRECTIONAL "
           f"effect-size floors; GO = {COMPARATIVE_GO_MIN}/{len(comps)})",
           "", "| signal | f | s | delta/gain | floor | win? |",
           "|---|---:|---:|---:|---|:---:|"]
    comp_cols = {"control_flip_rate delta (F - S)": "control_flip_rate",
                 "game_length centrality gain": "game_length"}
    for name, val, floor, ok in comps:
        key = comp_cols[name]
        md.append(f"| {name} | {_fmt(f[key])} "
                  f"| {_fmt(aggs['arms'][S][key])} | {val:.3f} | {floor} "
                  f"| {'YES' if ok else 'no'} |")
    md += ["", f"**{comp_wins}/{len(comps)} comparatives.** Drama is NOT "
           "a comparative — DIAGNOSTIC-ONLY by registration (closeness "
           "Goodhart, prereg Stage 1.5); see the diagnostic section "
           "below.", ""]

    # --- F bands (ALL must hold) ---------------------------------------
    bands = f_band_checks(f, aggs["exploiter"], aggs["packer_mean_total"])
    md += [f"## {F} bands (ALL must hold)", "",
           "| band | value | pass? |", "|---|---:|:---:|"]
    for name, val, ok in bands:
        md.append(f"| {name} | {_fmt(val)} | {'YES' if ok else 'no'} |")
    md += ["", f"Bands: "
           f"{'ALL PASS' if all(ok for *_, ok in bands) else 'FAIL'}. "
           f"double_pass_share {_fmt(f['double_pass_share'])} (logged, "
           f"not a screen gate).", "",
           "Per-seed skill inspection (mandatory; tvr floors "
           f"mean >= {TVR_MEAN_MIN}, seed >= {TVR_SEED_MIN}, collapse "
           f"< {COLLAPSE_TVR}):", ""]
    for seed, tvr in sorted(f["tvr_by_seed"].items()):
        md.append(f"- {F} seed {seed}: tvr {tvr:.3f}"
                  f"{' — COLLAPSED' if tvr < COLLAPSE_TVR else ''}")
    md += ["", f"Exploiter pooling: win share per (opponent, seat) pooled "
           f"over seeds as a ratio of totals ({EXPLOITER_GAMES} games per "
           f"(opponent, seat) per seed); BOTH seats must clear. Packer "
           f"re-assert: {PACKER_GAMES} MutualPacker-vs-MutualPacker games "
           f"on the calibrated F config (deterministic pairing).", ""]

    # --- Comparator health (S/A1/A0) -----------------------------------
    md += ["## Comparator health (prereg comparator-failure rule: "
           "failure -> CAMPAIGN_UNRESOLVED, one retrain — never a family "
           "verdict)", "",
           f"| arm | bias (<= {BIAS_PASS}) | tvr mean (>= {TVR_MEAN_MIN}) "
           f"| collapsed seeds (tvr < {COLLAPSE_TVR}) | pass? |",
           "|---|---:|---:|---|:---:|"]
    for arm in COMPARATOR_ARMS:
        a = aggs["arms"][arm]
        ok, _ = comparator_health(arm, a)
        md.append(f"| {arm} | {_fmt(a['bias'])} | {_fmt(a['tvr_mean'])} "
                  f"| {a['collapsed_seeds'] or 'none'} "
                  f"| {'YES' if ok else 'no'} |")
    md += [""]

    # --- Instrumentation-reproduction check ----------------------------
    delta, ok = repro_check(aggs)
    md += ["## Instrumentation-reproduction check (A0's registered job)",
           "",
           f"a1 - a0 control_flip_rate = {_fmt(delta)} (floor "
           f">= {A1_A0_FLIP_REPRO_MIN}; on-disk ordering 10.6 vs 5.3): "
           f"{'PASS' if ok else 'FAIL -> instrumentation INVALID -> CAMPAIGN_UNRESOLVED'}",
           ""]

    # --- Drama (DIAGNOSTIC-ONLY) ----------------------------------------
    md += ["## Drama — DIAGNOSTIC-ONLY (no licensing role, prereg "
           "Stage 1.5)", "",
           "Demoted by registration (closeness Goodhart). F's drama uses "
           "score_share_progress traces (S_p / max(1, S_p + S_opp)); "
           "S/A1/A0 use the siege-style component-span / threshold "
           "traces — the two trace families are INCOMMENSURABLE and are "
           "reported per arm, never compared. Draws excluded per game.",
           ""]
    for arm in ARMS:
        md.append(f"- {arm}: per-game winner_behindness mean "
                  f"{_fmt(aggs['arms'][arm]['drama'])}"
                  + (" (score-share trace)" if arm == F
                     else " (siege-style trace)"))
    md += [""]

    # --- Reference rows --------------------------------------------------
    md += ["## Reference rows (arm means, identical instrumentation)", ""]
    for arm in ARMS:
        a = aggs["arms"][arm]
        md.append(f"- {arm}: " + ", ".join(
            f"{k}={_fmt(a[k])}" for k in
            ("lead_changes", "game_length", "control_flip_rate",
             "flip_events", "timeout_share", "draw_rate", "bias",
             "tvr_mean")))
    md += [""]

    # --- Verdict ---------------------------------------------------------
    md += ["## Verdict", "", f"**{verdict}**", ""]
    md += [f"- {r}" for r in reasons]
    md += [""]
    return "\n".join(md)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--budget", type=int, default=5000)
    p.add_argument("--eval-episodes", type=int, default=200)
    p.add_argument("--seeds", default="42,43,44")
    p.add_argument("--calibrated-dir", type=Path,
                   default=GAMES_DIR / "calibrated")
    p.add_argument("--game-override", type=Path, default=None,
                   help="F-arm game json used IN PLACE OF the Stage-1 "
                        "calibrated artifact — PLUMBING TESTS ONLY; the "
                        "run is marked NON-REGISTERED in every output")
    p.add_argument("--exploiter-games", type=int, default=EXPLOITER_GAMES,
                   help=f"games per (opponent, seat) per seed (registered "
                        f"value {EXPLOITER_GAMES}; lower only for "
                        f"plumbing tests)")
    p.add_argument("--packer-games", type=int, default=PACKER_GAMES,
                   help=f"packer re-assert games (registered value "
                        f"{PACKER_GAMES}; lower only for plumbing tests)")
    args = p.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]

    # ------------------------------------------------------------------
    # Arm sources. f_frontline comes from Stage-1 calibration output; a
    # missing file is a calibration verdict, handled loudly (siege
    # convention), never silently. There is NO F-absent screen: frontline
    # has no siege-style s-only stop rule (prereg: F fails -> NO-GO).
    # ------------------------------------------------------------------
    if args.game_override is not None:
        f_path = args.game_override
        if not f_path.exists():
            print(f"FATAL: --game-override {f_path} does not exist",
                  flush=True)
            sys.exit(1)
    else:
        f_path = args.calibrated_dir / "f_frontline.json"
        if not f_path.exists():
            print(f"FATAL: {F} missing from {args.calibrated_dir} — "
                  f"Stage-1 calibration has not produced a winner "
                  f"(F_GRID_UNRESOLVED, or Stage 1 unrun; "
                  f"PREREGISTRATION.md Stage 1). Registered outcome: "
                  f"campaign NO-GO at Stage 1 — there is no F-absent "
                  f"screen. For plumbing tests only, use "
                  f"--game-override.", flush=True)
            sys.exit(1)
    sources = {
        F: f_path,
        S: GAMES_DIR / "s_flip_r2.json",
        A1: GAMES_DIR / "a1_field_connect.json",
        A0: GAMES_DIR / "a0_baseline.json",
    }
    for arm in COMPARATOR_ARMS:
        if not sources[arm].exists():
            print(f"FATAL: {arm} missing from {GAMES_DIR} — run "
                  f"build_games.py first.", flush=True)
            sys.exit(1)

    t0 = time.time()
    rows: list[dict] = []
    f_trainers: list = []
    f_game: GameDefV2 | None = None
    for arm in ARMS:
        game = GameDefV2.from_dict(json.loads(sources[arm].read_text()))
        kind = arm_kind(game)
        for seed in seeds:
            row, trainer = screen_one(
                game, arm, kind, seed, args.budget, args.eval_episodes)
            rows.append(row)
            if arm == F:
                f_trainers.append(trainer)
                f_game = game
            print(f"{arm} seed={seed}: " + ", ".join(
                f"{k}={v:.3f}" for k, v in row.items()
                if isinstance(v, float)), flush=True)

    print(f"exploiter bands: {args.exploiter_games} games per "
          f"(opponent, seat) per seed...", flush=True)
    exploiter = exploiter_bands(f_game, f_trainers,
                                n_games=args.exploiter_games)
    print(f"  pooled shares: {exploiter}", flush=True)
    packer_mean = packer_reassert(f_game, n_games=args.packer_games)
    print(f"packer re-assert: mean total score {packer_mean:.3f} "
          f"(<= {PACKER_SCORE_MAX})", flush=True)

    aggs = build_aggs(rows, exploiter, packer_mean)
    verdict, reasons = screen_verdict(aggs)

    with open(HERE / "screen_results.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    override_note = None
    if args.game_override is not None:
        override_note = (f"NON-REGISTERED RUN — --game-override "
                         f"{args.game_override} stands in for "
                         f"games/calibrated/f_frontline.json (plumbing "
                         f"test only; no campaign decision attaches)")
    run_info = (f"PPO budget {args.budget}, seeds {seeds}, instrumented "
                f"sampled mirror eval n={args.eval_episodes}/seed "
                f"(seat-swap halves, all arms symmetric); exploiter "
                f"n={args.exploiter_games}/(opponent, seat)/seed; packer "
                f"n={args.packer_games}. Elapsed {time.time() - t0:.0f}s.")
    (HERE / "screen_results.md").write_text(
        build_md(aggs, rows, verdict, reasons, run_info, override_note))

    print(f"{verdict} — " + "; ".join(reasons), flush=True)
    print("wrote screen_results.csv + screen_results.md", flush=True)
    sys.exit({"SCREEN_GO": 0, "SCREEN_NOGO": 1,
              "CAMPAIGN_UNRESOLVED": 2}[verdict])


if __name__ == "__main__":
    main()
