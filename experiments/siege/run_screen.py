"""SIEGE Stage-2 — 4-arm mechanical screen (PREREGISTRATION.md "Stage 2 screen").

Per arm (m_siege, s_flip_r2, a1_field_connect, a0_baseline) x 3 PPO seeds:
train (budget 5000), then an instrumented sampled trained-vs-trained mirror
eval (n=200/seed) recording the pre-registered signals. m_siege and
s_flip_r2 load from games/calibrated/ (Stage-1 outputs); a0/a1 retrain from
games/ (verbatim copies of the fc_phase15 calibrated defs, per prereg).

Comparative bars (m_siege vs s_flip_r2, arm means, effect-size floors):
  1. control_flip_rate delta >= 0.5 absolute
  2. game_length centrality in [30,160], center 95 — >= 10 turns more central
  3. per-role drama delta >= 0.05 (ONLY if --anchor-result pass)
GO: m_siege >= 2/3 comparatives (2/2 when drama demoted) + ALL m bands.
STOP RULES: m fails but s clears the z_flip_r2 template vs a0 (>= 3/4:
lead_changes, game_length, control_flip_rate, connection_win_fraction
>= 0.80) -> S-ONLY BLIND. Both fail -> SCREEN NO-GO, exit nonzero.

Adaptations vs the fc_phase15 template (documented, instrumentation-level):
  - m_siege roles are seat-locked (pie OFF): NO seat swap in the mirror
    eval — agents[0] is always the Maker, agents[1] always the Breaker.
    Symmetric arms keep fc_phase15's seat-swap halves.
  - m_siege lead_changes: the symmetric progress_diff proxies don't apply
    to asymmetric objectives, so the differential is the per-role progress
    gap maker_progress_span - breaker_progress per non-swap ply; lead
    changes = sign flips of that series, zeros skipped (count_lead_changes,
    same flip-counting as all other arms).
  - m_siege flip_events: P1 (Maker) piece-count drops on Breaker plies —
    the quota-feeding event class. distinct_flip_ratio aggregates per seed
    as sum(distinct)/max(1, sum(events)) (ratio of totals; per-episode
    ratios would let 0-event episodes distort the band).
  - Symmetric field arms resolve per-player axes through the engine's
    _goals_swapped flag (pie swap swaps goals; engine_v2.py:1250-1257).
  - Stage-2 skill gates re-assert the Stage-1 per_role_tvr pass flags per
    seed (mandatory per-seed inspection); the reserve-seed rerun ladder is
    Stage-1 calibration machinery and does not apply here.
  - m_siege is structurally drawless (timeout_winner=2): the draw-rate
    band applies to s/a1/a0 only and is STATED, not credited, for m.

Usage:
    .venv/bin/python experiments/siege/run_screen.py \
        --anchor-result {pass,demoted} \
        [--budget 5000] [--eval-episodes 200] [--seeds 42,43,44] \
        [--calibrated-dir experiments/siege/games/calibrated]
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
from experiments.siege.metrics import (  # noqa: E402
    breaker_progress,
    maker_progress_span,
    winner_behindness,
)
from experiments.siege.anchor_drama import (  # noqa: E402
    threshold_progress_p1,
    threshold_progress_p2,
)
from experiments.siege.eval_roles import (  # noqa: E402
    per_role_tvr,
    role_bias_from_matrix,
    role_matrix,
)

HERE = Path(__file__).resolve().parent
GAMES_DIR = HERE / "games"

M, S, A1, A0 = ("m_siege", "s_flip_r2", "a1_field_connect", "a0_baseline")
ARMS = (M, S, A1, A0)
SYM_ARMS = (S, A1, A0)

# ---------------------------------------------------------------------------
# Pre-registered Stage-2 constants — experiments/siege/PREREGISTRATION.md
# ("Stage 2 screen"). Not altered after data.
# ---------------------------------------------------------------------------
LENGTH_BAND = (30.0, 160.0)      # game_length centrality band
LENGTH_CENTER = 95.0             # centrality center
FLIP_DELTA_FLOOR = 0.5           # comparative 1: control_flip_rate floor
CENTRALITY_FLOOR = 10.0          # comparative 2: turns-more-central floor
DRAMA_DELTA_FLOOR = 0.05         # comparative 3: per-role drama floor
COMPARATIVE_GO_MIN = 2           # pass: 2/3; demoted: 2/2 (drama excluded)
FLIP_EVENTS_BAND = (1.0, 20.0)   # m band: flip events/game
DISTINCT_FLIP_RATIO_MIN = 0.5    # m band: distinct-stones-flipped ratio
QUOTA_SHARE_MIN = 0.20           # m band: quota share of Breaker wins
TIMEOUT_SHARE_MAX = 0.25         # m band: timeout share of ALL games
BIAS_PASS = 0.10                 # role/seat bias band (all arms)
DRAW_RATE_MAX = 0.05             # symmetric-arm band (s/a1/a0 only)
TVR_FLOOR = 0.80                 # symmetric-arm band: trained_vs_random
CONNECTION_WIN_FLOOR = 0.80      # z_flip_r2 template (and fc_phase15 bar)
Z_GO_MIN = 3                     # z_flip_r2 stop rule: >= 3/4 vs a0


def arm_kind(game: GameDefV2) -> str:
    """'asym' (SIEGE Maker/Breaker), 'field', or 'threshold'."""
    wc = game.win_condition
    if getattr(wc, "condition_type_p2", "") == "capture_quota":
        return "asym"
    if wc.condition_type == "field_connection":
        return "field"
    if wc.condition_type == "threshold":
        return "threshold"
    raise ValueError(f"unsupported win condition for screen: "
                     f"{wc.condition_type} ({game.game_id})")


def resolve_axes(game: GameDefV2, engine) -> tuple[int, int]:
    """(p1_axis, p2_axis), mirroring engine_v2._check_win field_connection
    dispatch: P2 axis = target_dimension_p2 if >= 0 else (target+1) % dims;
    after a pie swap (_goals_swapped) the axes swap with the goals."""
    wc = game.win_condition
    p1_axis = wc.target_dimension
    p2_axis = wc.target_dimension_p2
    if p2_axis < 0:
        p2_axis = (p1_axis + 1) % game.num_dimensions
    if engine._goals_swapped:
        p1_axis, p2_axis = p2_axis, p1_axis
    return p1_axis, p2_axis


def instrumented_episode(game: GameDefV2, a0, a1, kind: str) -> dict:
    """One sampled game with per-step metric + per-role progress recording."""
    engine = create_engine(game)
    obs = engine.reset()
    agents = [a0, a1]
    wc = game.win_condition
    margin = getattr(wc, "control_margin", 0.0)
    prev_counts = list(engine.piece_counts)
    prev_signs = controller_signs(engine, margin)
    flip_events = 0
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
        action, _, _ = agent.select_action(
            obs, legal_actions=legal, deterministic=False,
        )
        obs, _, done, info = engine.step(action)
        cur_signs = controller_signs(engine, margin)
        if not info.get("pie_swap"):
            # Piece-count drops on this ply attribute to the mover.
            for pidx in (0, 1):
                drop = prev_counts[pidx] - engine.piece_counts[pidx]
                if drop > 0:
                    if kind == "asym":
                        # Breaker flip events: Maker (P1) stones flipped on
                        # Breaker (seat-1) plies — the quota-feeding class.
                        if pidx == 0 and mover == 1:
                            flip_events += drop
                    else:
                        flip_events += drop
            if kind == "asym":
                mk = maker_progress_span(
                    engine, 1, wc.target_dimension, margin)
                bk = breaker_progress(engine)
                p1_trace.append(mk)
                p2_trace.append(bk)
                # m_siege lead proxy (documented adaptation): per-role
                # progress differential; sign flips counted zeros-skipped.
                diffs.append(mk - bk)
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
        prev_counts = list(engine.piece_counts)
        prev_signs = cur_signs

    winner = engine._winner
    timeout = engine._ended_by_max_turns
    quota = getattr(wc, "capture_quota", 0)
    if winner == 1:
        drama = winner_behindness(p1_trace, p2_trace)
    elif winner == 2:
        drama = winner_behindness(p2_trace, p1_trace)
    else:
        drama = None  # draws skipped from per-role drama
    return dict(
        length=engine.step_count,
        flip_events=flip_events,
        distinct_flips=len(engine._quota_cells),
        lead_changes=count_lead_changes(diffs),
        control_flips=float(np.mean(flips)) if flips else 0.0,
        # asym: only the Maker's win is a connection win (Breaker quota
        # wins are not); symmetric arms: any decisive non-timeout end.
        connection_win=((winner == 1) if kind == "asym"
                        else (winner is not None and not timeout)),
        quota_win=(winner == 2 and quota > 0
                   and engine._quota_ticks >= quota),
        timeout=bool(timeout),
        draw=(winner is None),
        p1_win=(winner == 1),
        p2_win=(winner == 2),
        drama=drama,
    )


def screen_one(game: GameDefV2, arm: str, kind: str, seed: int,
               budget: int, eval_eps: int) -> tuple[dict, SelfPlayTrainer]:
    cfg = TrainingConfig(training_budget=budget, eval_episodes=100)
    mcfg = MetricsConfig(learning_curve_checkpoints=2)
    trainer = SelfPlayTrainer(game, cfg, mcfg, seed=seed)
    t0 = time.time()
    trainer.train()

    eps = []
    if kind == "asym":
        # Roles fixed (pie OFF): NO seat swap. agents[0]=Maker, [1]=Breaker.
        for _ in range(eval_eps):
            eps.append(instrumented_episode(
                game, trainer.agents[0], trainer.agents[1], kind))
        tvr = per_role_tvr(game, trainer, n=max(10, eval_eps // 2))
        diag_tvr = None
    else:
        diag = trainer.evaluate(num_episodes=100)
        diag_tvr = float(diag.get("trained_vs_random_winrate", -1.0))
        tvr = None
        half = eval_eps // 2
        for i in range(eval_eps):
            if i < half:
                a, b = trainer.agents[0], trainer.agents[1]
            else:
                a, b = trainer.agents[1], trainer.agents[0]
            eps.append(instrumented_episode(game, a, b, kind))

    n = max(len(eps), 1)
    p1_wr = sum(e["p1_win"] for e in eps) / n
    breaker_wins = sum(e["p2_win"] for e in eps)
    dramas = [e["drama"] for e in eps if e["drama"] is not None]
    sum_events = sum(e["flip_events"] for e in eps)
    row = dict(
        arm=arm,
        game_id=game.game_id,
        seed=seed,
        game_length=float(np.mean([e["length"] for e in eps])),
        lead_changes=float(np.mean([e["lead_changes"] for e in eps])),
        control_flip_rate=float(np.mean([e["control_flips"] for e in eps])),
        per_role_drama=(float(np.mean(dramas)) if dramas else None),
        flip_events=float(np.mean([e["flip_events"] for e in eps])),
        distinct_flip_ratio=(
            sum(e["distinct_flips"] for e in eps) / max(1, sum_events)
            if kind == "asym" else None),
        quota_share=(
            sum(e["quota_win"] for e in eps) / max(1, breaker_wins)
            if kind == "asym" else None),
        timeout_share=sum(e["timeout"] for e in eps) / n,
        draw_rate=sum(e["draw"] for e in eps) / n,
        seat_role_bias=abs(p1_wr - 0.5),
        connection_win_fraction=sum(e["connection_win"] for e in eps) / n,
        trained_vs_random=diag_tvr,
        maker_tvr=(tvr["maker_tvr"] if tvr else None),
        breaker_tvr=(tvr["breaker_tvr"] if tvr else None),
        maker_baseline=(tvr["maker_baseline"] if tvr else None),
        breaker_baseline=(tvr["breaker_baseline"] if tvr else None),
        maker_pass=(tvr["maker_pass"] if tvr else None),
        breaker_pass=(tvr["breaker_pass"] if tvr else None),
        collapsed=(tvr["collapsed"] if tvr else None),
        elapsed_s=time.time() - t0,
    )
    return row, trainer


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--budget", type=int, default=5000)
    p.add_argument("--eval-episodes", type=int, default=200)
    p.add_argument("--seeds", default="42,43,44")
    p.add_argument("--anchor-result", required=True,
                   choices=("pass", "demoted"),
                   help="Stage-1.5 anchor_drama verdict (REQUIRED, no "
                        "default): pass -> drama is comparative 3 (GO needs "
                        ">= 2/3); demoted -> drama excluded (GO needs 2/2)")
    p.add_argument("--calibrated-dir", type=Path,
                   default=GAMES_DIR / "calibrated")
    args = p.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]

    # ------------------------------------------------------------------
    # Arm sources. m_siege/s_flip_r2 come from Stage-1 calibration output;
    # missing files are calibration verdicts, handled loudly (fc_phase15
    # BIAS_UNRESOLVED-style), never silently.
    # ------------------------------------------------------------------
    sources = {
        M: args.calibrated_dir / "m_siege.json",
        S: args.calibrated_dir / "s_flip_r2.json",
        A1: GAMES_DIR / "a1_field_connect.json",
        A0: GAMES_DIR / "a0_baseline.json",
    }
    skipped: list[str] = []
    if not sources[M].exists():
        skipped.append(M)
        print(f"WARNING: {M} missing from {args.calibrated_dir} — arm "
              f"invalidated at calibration (M_GRID_UNRESOLVED / role-pie "
              f"retry exhausted, PREREGISTRATION.md Stage 1), skipped. "
              f"Registered outcome: campaign CONTINUES s-only; the screen "
              f"evaluates s_flip_r2 under the z_flip_r2 template vs "
              f"a0_baseline.", flush=True)
    if not sources[S].exists():
        print(f"FATAL: {S} missing from {args.calibrated_dir} — arm "
              f"invalidated at calibration (BIAS_UNRESOLVED; sanity gate, "
              f"PREREGISTRATION.md). The control arm is gone: no M-vs-S "
              f"comparatives AND no z_flip_r2 stop-rule arm exist. The "
              f"Stage-2 screen cannot run.", flush=True)
        sys.exit(1)

    rows: list[dict] = []
    m_trainers: list[SelfPlayTrainer] = []
    m_game: GameDefV2 | None = None
    for arm in ARMS:
        if arm in skipped:
            continue
        game = GameDefV2.from_dict(json.loads(sources[arm].read_text()))
        kind = arm_kind(game)
        for seed in seeds:
            row, trainer = screen_one(
                game, arm, kind, seed, args.budget, args.eval_episodes)
            rows.append(row)
            if kind == "asym":
                m_trainers.append(trainer)
                m_game = game
            print(f"{arm} seed={seed}: " + ", ".join(
                f"{k}={v:.3f}" for k, v in row.items()
                if isinstance(v, float)), flush=True)

    # m_siege role bias band: recomputed over the cross-seed role matrix
    # (eval_roles.role_matrix on the screen trainers; games_per_pair scaled
    # from --eval-episodes exactly as Stage-1 calibrate.py does).
    m_matrix_bias = None
    if m_trainers:
        gpp = max(1, args.eval_episodes // 9)
        matrix, agg_tallies = role_matrix(
            m_game, m_trainers, games_per_pair=gpp)
        m_matrix_bias = role_bias_from_matrix(matrix)
        for mrow in matrix:
            print(f"  m role-matrix row: {['%.3f' % v for v in mrow]}",
                  flush=True)
        print(f"  m role-matrix tallies: {agg_tallies} "
              f"(bias {m_matrix_bias:.3f})", flush=True)

    with open(HERE / "screen_results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # ------------------------------------------------------------------
    # Aggregation + bars (applied verbatim from PREREGISTRATION.md Stage 2)
    # ------------------------------------------------------------------
    def agg(arm: str, key: str) -> float:
        vals = [r[key] for r in rows if r["arm"] == arm
                and r[key] is not None]
        return float(np.mean(vals)) if vals else float("nan")

    def in_band(x: float) -> bool:
        return LENGTH_BAND[0] <= x <= LENGTH_BAND[1]

    def length_win(x_arm: float, x_0: float) -> bool:
        """z_flip_r2 template length bar — fc_phase15/run_screen.py
        verbatim: arm in [30,160] AND a0 not both in-band and closer to 95."""
        return (in_band(x_arm)
                and not (in_band(x_0)
                         and abs(x_0 - LENGTH_CENTER)
                         < abs(x_arm - LENGTH_CENTER)))

    m_present = M not in skipped
    fmt = lambda v: ("—" if v is None or (isinstance(v, float)
                     and np.isnan(v)) else f"{v:.3f}")

    md = ["# SIEGE Stage-2 — 4-arm mechanical screen", "",
          f"PPO budget {args.budget}, seeds {seeds}, instrumented sampled "
          f"mirror eval n={args.eval_episodes}/seed (m_siege: roles fixed, "
          f"NO seat swap; symmetric arms: seat-swap halves). "
          f"--anchor-result {args.anchor_result}. Bars per "
          f"experiments/siege/PREREGISTRATION.md Stage 2.", ""]
    for name in skipped:
        md += [f"## {name}", "",
               "**SKIPPED — invalidated at calibration (M_GRID_UNRESOLVED / "
               "role-pie retry exhausted; PREREGISTRATION.md Stage 1). "
               "Registered outcome: campaign continues s-only.**", ""]

    # --- Comparatives: m_siege vs s_flip_r2, arm means, floors ---------
    comp_wins = 0
    comp_total = 0
    if m_present:
        m_len, s_len = agg(M, "game_length"), agg(S, "game_length")
        flip_delta = (agg(M, "control_flip_rate")
                      - agg(S, "control_flip_rate"))
        centrality_gain = (abs(s_len - LENGTH_CENTER)
                           - abs(m_len - LENGTH_CENTER))
        comparatives = [
            ("control_flip_rate delta", flip_delta,
             f">= {FLIP_DELTA_FLOOR} absolute",
             flip_delta >= FLIP_DELTA_FLOOR),
            ("game_length centrality gain", centrality_gain,
             f">= {CENTRALITY_FLOOR} turns more central (center "
             f"{LENGTH_CENTER:.0f}, m in [{LENGTH_BAND[0]:.0f},"
             f"{LENGTH_BAND[1]:.0f}])",
             in_band(m_len) and centrality_gain >= CENTRALITY_FLOOR),
        ]
        if args.anchor_result == "pass":
            drama_delta = (agg(M, "per_role_drama")
                           - agg(S, "per_role_drama"))
            comparatives.append(
                ("per_role_drama delta", drama_delta,
                 f">= {DRAMA_DELTA_FLOOR}",
                 drama_delta >= DRAMA_DELTA_FLOOR))
        comp_total = len(comparatives)
        md += [f"## Comparatives — {M} vs {S} (arm means, effect-size "
               f"floors)", "",
               f"| signal | m | s | delta/gain | floor | win? |",
               "|---|---:|---:|---:|---|:---:|"]
        comp_cols = {"control_flip_rate delta": "control_flip_rate",
                     "game_length centrality gain": "game_length",
                     "per_role_drama delta": "per_role_drama"}
        for name, val, floor, ok in comparatives:
            comp_wins += ok
            key = comp_cols[name]
            md.append(f"| {name} | {fmt(agg(M, key))} | {fmt(agg(S, key))} "
                      f"| {val:.3f} | {floor} | {'YES' if ok else 'no'} |")
        if args.anchor_result == "demoted":
            md += ["", f"Drama DEMOTED to diagnostic (anchor calibration "
                   f"FAIL): m {fmt(agg(M, 'per_role_drama'))} vs s "
                   f"{fmt(agg(S, 'per_role_drama'))} — not a comparative. "
                   f"GO needs 2/2 of the remaining comparatives."]
        md += ["", f"**{comp_wins}/{comp_total} comparatives "
               f"(GO threshold {COMPARATIVE_GO_MIN}/{comp_total}).**", ""]

    # --- m_siege bands (all must hold) ---------------------------------
    m_bands_ok = False
    if m_present:
        m_rows = [r for r in rows if r["arm"] == M]
        skill_ok = all(r["maker_pass"] and r["breaker_pass"]
                       for r in m_rows)
        bands = [
            (f"flip_events/game in [{FLIP_EVENTS_BAND[0]:.0f},"
             f"{FLIP_EVENTS_BAND[1]:.0f}]", agg(M, "flip_events"),
             FLIP_EVENTS_BAND[0] <= agg(M, "flip_events")
             <= FLIP_EVENTS_BAND[1]),
            (f"distinct_flip_ratio >= {DISTINCT_FLIP_RATIO_MIN}",
             agg(M, "distinct_flip_ratio"),
             agg(M, "distinct_flip_ratio") >= DISTINCT_FLIP_RATIO_MIN),
            (f"quota_share >= {QUOTA_SHARE_MIN} (re-asserted at "
             f"{args.budget})", agg(M, "quota_share"),
             agg(M, "quota_share") >= QUOTA_SHARE_MIN),
            (f"timeout_share <= {TIMEOUT_SHARE_MAX} (re-asserted at "
             f"{args.budget})", agg(M, "timeout_share"),
             agg(M, "timeout_share") <= TIMEOUT_SHARE_MAX),
            (f"role bias <= {BIAS_PASS} (cross-seed role matrix)",
             m_matrix_bias, m_matrix_bias <= BIAS_PASS),
            ("per-role skill gates, every seed (Stage-1 gates)",
             None, skill_ok),
        ]
        m_bands_ok = all(ok for _, _, ok in bands)
        md += [f"## {M} bands (ALL must hold)", "",
               "| band | value | pass? |", "|---|---:|:---:|"]
        for name, val, ok in bands:
            md.append(f"| {name} | {fmt(val)} | "
                      f"{'YES' if ok else 'no'} |")
        md += ["", "Per-seed skill gates (mandatory per-seed inspection; "
               "tvr >= 0.80 AND >= baseline + 0.15, collapse < 0.20):", ""]
        for r in m_rows:
            line = (f"- seed {r['seed']}: maker_tvr {r['maker_tvr']:.3f} "
                    f"(base {r['maker_baseline']:.3f}) "
                    f"{'PASS' if r['maker_pass'] else 'FAIL'}; "
                    f"breaker_tvr {r['breaker_tvr']:.3f} "
                    f"(base {r['breaker_baseline']:.3f}) "
                    f"{'PASS' if r['breaker_pass'] else 'FAIL'}"
                    f"{'; COLLAPSED' if r['collapsed'] else ''}")
            md.append(line)
            print(line, flush=True)
        md += ["", f"m_siege is structurally drawless (timeout_winner=2): "
               f"draw-rate band NOT credited — stated only (observed "
               f"draw_rate {fmt(agg(M, 'draw_rate'))}).",
               "", f"**m bands: {'ALL PASS' if m_bands_ok else 'FAIL'}.**",
               ""]

    # --- Symmetric-arm bands (s / a1 / a0) ------------------------------
    sym_band_ok: dict[str, bool] = {}
    md += ["## Symmetric-arm bands (s/a1/a0)", "",
           f"| arm | draw_rate (<= {DRAW_RATE_MAX}) | seat_balance "
           f"(<= {BIAS_PASS}) | trained_vs_random (>= {TVR_FLOOR}) "
           f"| pass? |", "|---|---:|---:|---:|:---:|"]
    for arm in SYM_ARMS:
        ok = (agg(arm, "draw_rate") <= DRAW_RATE_MAX
              and agg(arm, "seat_role_bias") <= BIAS_PASS
              and agg(arm, "trained_vs_random") >= TVR_FLOOR)
        sym_band_ok[arm] = ok
        md.append(f"| {arm} | {fmt(agg(arm, 'draw_rate'))} "
                  f"| {fmt(agg(arm, 'seat_role_bias'))} "
                  f"| {fmt(agg(arm, 'trained_vs_random'))} "
                  f"| {'YES' if ok else 'no'} |")
    md += [""]

    # --- Reference rows --------------------------------------------------
    md += ["## Reference rows (arm means, identical instrumentation)", ""]
    for arm in ARMS:
        if arm in skipped:
            continue
        md.append(f"- {arm}: " + ", ".join(
            f"{k}={fmt(agg(arm, k))}" for k in
            ("lead_changes", "game_length", "control_flip_rate",
             "per_role_drama", "connection_win_fraction", "flip_events",
             "timeout_share")))
    md += [""]

    # --- Verdict ---------------------------------------------------------
    m_go = (m_present and comp_wins >= COMPARATIVE_GO_MIN and m_bands_ok)
    exit_code = 0
    if m_go:
        verdict = (f"**SCREEN GO — m_siege clears "
                   f"{comp_wins}/{comp_total} comparatives + all bands; "
                   f"blind campaign runs m_siege vs s_flip_r2 vs "
                   f"a1_field_connect (PREREGISTRATION.md Stage 3).**")
        md += ["## Verdict", "", verdict, "",
               "Stop rule not reached (m cleared).", ""]
    else:
        # STOP RULE: m failed (or was skipped) -> evaluate s under the
        # z_flip_r2 template vs a0 (>= 3/4).
        why = ("missing from calibration" if not m_present else
               f"{comp_wins}/{comp_total} comparatives"
               f"{'' if m_bands_ok else ' + band failure(s)'}")
        z_checks = [
            ("lead_changes > a0",
             agg(S, "lead_changes") > agg(A0, "lead_changes")),
            ("game_length more central in [30,160] than a0",
             length_win(agg(S, "game_length"), agg(A0, "game_length"))),
            ("control_flip_rate > a0",
             agg(S, "control_flip_rate") > agg(A0, "control_flip_rate")),
            (f"connection_win_fraction >= {CONNECTION_WIN_FLOOR}",
             agg(S, "connection_win_fraction") >= CONNECTION_WIN_FLOOR),
        ]
        z_wins = sum(ok for _, ok in z_checks)
        md += [f"## Stop rule — z_flip_r2 template: {S} vs {A0} "
               f"(m_siege failed: {why})", "",
               "| signal | s | a0 | win? |", "|---|---:|---:|:---:|"]
        z_cols = {"lead_changes > a0": "lead_changes",
                  "game_length more central in [30,160] than a0":
                      "game_length",
                  "control_flip_rate > a0": "control_flip_rate",
                  f"connection_win_fraction >= {CONNECTION_WIN_FLOOR}":
                      "connection_win_fraction"}
        for name, ok in z_checks:
            key = z_cols[name]
            md.append(f"| {name} | {fmt(agg(S, key))} "
                      f"| {fmt(agg(A0, key))} | {'YES' if ok else 'no'} |")
        md += ["", f"**{z_wins}/4 (threshold {Z_GO_MIN}/4).**", ""]
        if z_wins >= Z_GO_MIN:
            verdict = (f"**S-ONLY BLIND — m_siege fails the screen ({why}) "
                       f"but s_flip_r2 clears the z_flip_r2 template "
                       f"{z_wins}/4 vs a0; blind runs s_flip_r2 vs "
                       f"a1_field_connect only.**")
            if not sym_band_ok.get(S, False):
                verdict += (" NOTE: s_flip_r2 sanity bands FAIL — flagged "
                            "for the record; the registered stop rule is "
                            "the 3/4 template only.")
        else:
            verdict = (f"**SCREEN NO-GO — no blind campaign: m_siege fails "
                       f"({why}) AND s_flip_r2 clears only {z_wins}/4 of "
                       f"the z_flip_r2 template vs a0.**")
            exit_code = 1
        md += ["## Verdict", "", verdict, ""]

    (HERE / "screen_results.md").write_text("\n".join(md))
    print(verdict, flush=True)
    print(f"wrote screen_results.csv + screen_results.md", flush=True)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
