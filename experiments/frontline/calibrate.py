"""FRONTLINE Stage-1 calibration driver (prereg Stage 1 — the locked authority).

F grid: E {0.75, 1.00, 1.25} x M_end {8, 12} = 6 cells, seeds 42/43/44.
Per cell, gate ORDER is pre-registered and STRUCTURAL (a cell that fails
gate N never computes gate N+1 — the siege early-return pattern; see
apply_gates()):
  (1) skill: tvr mean >= 0.75 AND no seed < 0.65. Collapsed seed
      (tvr < 0.20) -> ONE replace-in-slot rerun, reserves 45 then 46
      consumed in order ACROSS THE GRID, at most one rerun per original
      seed; the rerun REPLACES the collapsed seed in all aggregates; a
      third collapse (reserves exhausted, or a rerun that collapses
      again) -> cell INVALID.
  (2) seat bias <= 0.10 with pie ON at komi_cells 0 first; fallback
      ladder komi_cells {+-1, +-2} — smallest |komi| passing, direction
      by the measured bias SIGN at komi 0 (P1-favored -> POSITIVE komi:
      komi_cells is ADDED to P2's score in every engine comparison, so
      positive komi helps P2 — engine_v2 lead = s1 - (s2 + komi_cells)).
  (3) end-cause health: timeout share <= 0.25 of ALL games (denominator
      pinned); draw <= 0.05; score_margin share >= 0.25. Double-pass
      share LOGGED with yellow flag > 0.50 (diagnostic, not a gate).
  (4) engaged_share (final-ply mean over ALL games, all end-causes) in
      [0.02, 0.60].
Tie-break among passing cells (prereg verbatim): game_length centrality
closest to 95, then max score_margin share, then min |bias|. Runner-up
recorded in calibration.json (the registered PARTIAL knob). Winner ->
games/calibrated/f_frontline.json with the winning komi_cells baked in
(asserting |komi| < end_margin — the registered harness invariant).
NO passing cell -> loud F_GRID_UNRESOLVED, no calibrated file written,
exit 0 (siege convention; run_screen loud-skips the missing file).

Komi semantics (registered policy-reuse rationale — same as siege's S
komi sweep): komi is applied at EVAL time by setting
trainer.game.win_condition.komi_cells before the eval games (engines are
created per game via create_engine(trainer.game)); komi only enters
score comparisons, never placement legality, so the komi-0-trained
policies are re-evaluated unchanged. After each cell's ladder the
mutation is reset to the WINNING rung (or 0 if none passed) so no stale
mutation leaks.

bias = |p1_share + draw_rate/2 - 0.5| — draws count half to each side
(a draw-heavy meta must not masquerade as balance). p1_share is seat-0's
win share over seat-swapped halves.

All statistics are computed over EVERY eval game — no game- or
seed-level filtering (R21 Probe B survivorship lesson).

The comparators arm is a provenance STUB in this build: it verifies the
probe-calibrated S/A1 artifacts exist on disk and records their
registered calibration provenance. The full re-assert (retrain + bias
drift > 0.10 -> recalibration -> comparator rule) happens at screen time.

Report: calibration.md regenerated whole from calibration.json each run
(per-cell sections, every gate decision visible; rerunning a --cells
subset replaces only those cells' sources — siege convention).

Usage:
    .venv/bin/python experiments/frontline/calibrate.py \\
        [--arm {f,comparators,all}] [--budget 3000] [--eval-episodes 200] \\
        [--seeds 42,43,44] [--cells E1p00_M8,...] [--allow-partial]
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

from config import MetricsConfig, TrainingConfig  # noqa: E402
from game_engine.factory import create_engine  # noqa: E402
from training.trainer import SelfPlayTrainer  # noqa: E402

# Shared eval helpers — methodology of record since the FC probe.
# play_game lives in training/utils.py and is re-exported through the FC
# probe's calibrate module (the same import path siege uses for
# sampled_mirror_eval). sampled_mirror_eval itself is unused by the F
# grid (eval_cell_games supersedes it: end-causes + engaged_share need
# the engine post-game) but stays importable here for the Stage-2 S/A1
# re-assert.
from experiments.field_connect_probe.calibrate import (  # noqa: E402
    play_game,
    sampled_mirror_eval,  # noqa: F401  (screen-time re-assert helper)
)
from training.utils import RandomAgent  # noqa: E402
from experiments.frontline.build_games import build_f  # noqa: E402

HERE = Path(__file__).resolve().parent
GAMES_DIR = HERE / "games"
OUT_DIR = GAMES_DIR / "calibrated"
CAL_JSON = HERE / "calibration.json"
CAL_MD = HERE / "calibration.md"

# ---------------------------------------------------------------------------
# Pre-registered Stage-1 gate constants — experiments/frontline/
# PREREGISTRATION.md ("Stage 1 calibration"). Not altered after data.
# ---------------------------------------------------------------------------
TVR_MEAN_MIN = 0.75
TVR_SEED_MIN = 0.65
COLLAPSE_TVR = 0.20
BIAS_PASS = 0.10
KOMI_LADDER = (1, 2)            # tried as +k or -k by measured bias sign
TIMEOUT_SHARE_MAX = 0.25
DRAW_RATE_MAX = 0.05
SCORE_MARGIN_SHARE_MIN = 0.25
DOUBLE_PASS_YELLOW = 0.50       # diagnostic flag, NOT a gate
ENGAGED_BAND = (0.02, 0.60)
LENGTH_CENTER = 95.0
RESERVE_SEEDS = (45, 46)
GRID_E = (0.75, 1.00, 1.25)
GRID_M = (8, 12)


def cell_name(e: float, m: int) -> str:
    """Grid cell key, e.g. cell_name(1.0, 8) == 'E1p00_M8'."""
    return f"E{e:.2f}_M{m}".replace(".", "p")


ALL_CELLS: dict[str, tuple[float, int]] = {
    cell_name(e, m): (e, m) for e in GRID_E for m in GRID_M
}

# On-disk calibration provenance for the comparator re-assert stub
# (verified against the source calibration.md files before pinning).
COMPARATOR_PROVENANCE = {
    "s_flip_r2.json": (
        "SIEGE Stage-1 arm s: komi 0.00 PASS (p1_wr 0.550, bias 0.050, "
        "draws 0.000) — experiments/siege/calibration.md"),
    "a1_field_connect.json": (
        "FC probe calibration: komi 0.00 PASS (p1_wr 0.450, bias 0.050, "
        "draws 0.000) — experiments/field_connect_probe/calibration.md "
        "(passed through fc_phase15 unchanged)"),
}


# ---------------------------------------------------------------------------
# Pure gate logic (testable without training — test_frontline_calibrate.py)
# ---------------------------------------------------------------------------

def signed_bias(p1_share: float, draw_rate: float) -> float:
    """Seat-signed bias: p1_share + draw_rate/2 - 0.5.

    Draws count half to each side, so a draw-heavy meta cannot masquerade
    as balance. Positive = P1-favored. The SIGN at komi 0 directs the
    komi ladder (prereg: 'direction by the measured bias sign at komi 0').
    """
    return p1_share + 0.5 * draw_rate - 0.5


def bias_value(p1_share: float, draw_rate: float) -> float:
    """Registered bias statistic: |p1_share + draw_rate/2 - 0.5|."""
    return abs(signed_bias(p1_share, draw_rate))


def signed_komi(k: int, p1_favored: bool) -> int:
    """Ladder direction rule (prereg): P1-favored -> +k (positive komi is
    added to P2's score in every engine comparison, i.e. it helps P2);
    P2-favored -> -k."""
    return k if p1_favored else -k


def skill_ok(tvrs: list[float]) -> tuple[bool, str]:
    """Gate-1 thresholds over the FINAL seeds (post replace-in-slot)."""
    mean_tvr = sum(tvrs) / len(tvrs)
    ok = mean_tvr >= TVR_MEAN_MIN and min(tvrs) >= TVR_SEED_MIN
    detail = (f"mean {mean_tvr:.3f} (floor {TVR_MEAN_MIN}), "
              f"min {min(tvrs):.3f} (floor {TVR_SEED_MIN})")
    return ok, detail


def apply_gates(stats: dict) -> tuple[str, str]:
    """Pure prereg gate ladder over a stats dict. No training, no eval.

    Gate ORDER is structural: this function returns at the FIRST failing
    gate without reading any later gate's keys, so a stats dict truncated
    at a failure (e.g. a skill-fail dict with no 'bias'/'agg' keys) must
    never raise. calibrate_cell builds stats up in gate order and stops
    spending compute as soon as a gate fails.

    Keys, in gate order:
      invalid : str | None — gate-1 training invalidity (reserve
                exhaustion / rerun still collapsed)
      tvrs    : list[float] — per-seed tvr, post any replace-in-slot rerun
      bias    : float — mean per-seed bias at the LAST ladder rung evaluated
      komi    : int — that rung's signed komi (reporting only)
      agg     : dict — draw_rate / timeout_share / score_margin_share /
                double_pass_share / engaged_mean / mean_length
                (present only when gate 2 passed — plan/prereg structure)
    """
    # ---- Gate (1): skill ----
    if stats.get("invalid"):
        return "INVALID", stats["invalid"]
    ok, detail = skill_ok(stats["tvrs"])
    if not ok:
        return "FAIL", f"skill: {detail}"
    # ---- Gate (2): seat bias (ladder resolved by caller) ----
    if stats["bias"] > BIAS_PASS:
        return "FAIL", (
            f"bias {stats['bias']:.3f} > {BIAS_PASS} at komi 0 and the "
            f"sign-directed ladder +-{KOMI_LADDER} "
            f"(last rung {stats['komi']:+d})")
    # ---- Gate (3): end-cause health ----
    agg = stats["agg"]
    if agg["timeout_share"] > TIMEOUT_SHARE_MAX:
        return "FAIL", (f"timeout_share {agg['timeout_share']:.3f} > "
                        f"{TIMEOUT_SHARE_MAX}")
    if agg["draw_rate"] > DRAW_RATE_MAX:
        return "FAIL", f"draw_rate {agg['draw_rate']:.3f} > {DRAW_RATE_MAX}"
    if agg["score_margin_share"] < SCORE_MARGIN_SHARE_MIN:
        return "FAIL", (f"score_margin_share {agg['score_margin_share']:.3f}"
                        f" < {SCORE_MARGIN_SHARE_MIN}")
    # ---- Gate (4): engaged band (final-ply mean over ALL games) ----
    if not (ENGAGED_BAND[0] <= agg["engaged_mean"] <= ENGAGED_BAND[1]):
        return "FAIL", (f"engaged {agg['engaged_mean']:.3f} outside "
                        f"[{ENGAGED_BAND[0]}, {ENGAGED_BAND[1]}]")
    # ---- Yellow flag (diagnostic, never a gate) ----
    if agg["double_pass_share"] > DOUBLE_PASS_YELLOW:
        return "PASS DOUBLE_PASS_YELLOW", (
            f"all gates clear (double_pass {agg['double_pass_share']:.3f} "
            f"> {DOUBLE_PASS_YELLOW} — yellow flag, diagnostic)")
    return "PASS", "all gates clear"


def rank_passing(passing: list[dict]) -> list[dict]:
    """Prereg tie-break, verbatim: game_length centrality closest to 95,
    then max score_margin share, then min |bias|."""
    return sorted(passing, key=lambda r: (
        abs(r["agg"]["mean_length"] - LENGTH_CENTER),
        -r["agg"]["score_margin_share"],
        r["bias"],
    ))


# ---------------------------------------------------------------------------
# Eval helpers (compute)
# ---------------------------------------------------------------------------

def trained_vs_random(trainer, n: int = 100, max_steps: int = 400) -> float:
    """Symmetric tvr: trained agent vs RandomAgent, both seat orders."""
    wins = 0
    half = n // 2
    for i in range(n):
        engine = create_engine(trainer.game)
        if i < half:
            a0, a1, seat = trainer.agents[0], RandomAgent(seed=9000 + i), 0
        else:
            a0, a1, seat = RandomAgent(seed=9000 + i), trainer.agents[1], 1
        winner, _, _ = play_game(engine, a0, a1, deterministic=False,
                                 max_steps=max_steps)
        wins += int(winner == seat)
    return wins / n


def eval_cell_games(trainer, n: int = 200, max_steps: int = 400) -> dict:
    """Mirrored-seat self-play eval collecting Stage-1 gate inputs.
    ALL games enter every statistic (prereg survivorship pin)."""
    half = n // 2
    rec = dict(p1_wins=0, draws=0, lengths=[], causes=[], engaged=[])
    for i in range(n):
        engine = create_engine(trainer.game)
        order = (0, 1) if i < half else (1, 0)
        a0, a1 = trainer.agents[order[0]], trainer.agents[order[1]]
        winner, length, _ = play_game(engine, a0, a1, deterministic=False,
                                      max_steps=max_steps)
        seat_of_p1 = 0  # seat 0 is always engine P1
        if winner is None:
            rec["draws"] += 1
        elif winner == seat_of_p1:
            rec["p1_wins"] += 1
        rec["lengths"].append(length)
        cause = ("score_margin" if engine._ended_by_score_margin
                 else "double_pass" if engine._ended_by_double_pass
                 else "timeout" if engine._ended_by_max_turns else "other")
        rec["causes"].append(cause)
        _, _, engaged = engine.contested_scores()
        rec["engaged"].append(engaged / engine.topo.num_active_cells)
    n_f = float(n)
    causes = rec["causes"]
    p1_share = rec["p1_wins"] / n_f
    draw_rate = rec["draws"] / n_f
    return dict(
        bias=bias_value(p1_share, draw_rate),
        p1_share=p1_share,
        draw_rate=draw_rate,
        timeout_share=causes.count("timeout") / n_f,
        score_margin_share=causes.count("score_margin") / n_f,
        double_pass_share=causes.count("double_pass") / n_f,
        engaged_mean=float(np.mean(rec["engaged"])),
        mean_length=float(np.mean(rec["lengths"])),
    )


def train_one(game, budget: int, seed: int) -> SelfPlayTrainer:
    """Train one PPO self-play run (siege calibrate.py train_one, copied
    EXACTLY — the fc_phase15 config shape)."""
    cfg = TrainingConfig(training_budget=budget, eval_episodes=100)
    trainer = SelfPlayTrainer(
        game, cfg, MetricsConfig(learning_curve_checkpoints=2), seed=seed,
    )
    trainer.train()
    return trainer


# ---------------------------------------------------------------------------
# Per-cell ladder
# ---------------------------------------------------------------------------

def resolve_skill_gate(game, seeds, budget, used_reserves, tvr_n, cell):
    """Gate (1) TRAINING mechanics: collapse (tvr < COLLAPSE_TVR) -> ONE
    replace-in-slot rerun. Reserves (45 then 46) are consumed in order
    ACROSS THE GRID via the shared used_reserves dict, at most one rerun
    per original seed; a third collapse (reserves exhausted, or a rerun
    that collapses again) -> cell INVALID. The mean/min skill THRESHOLDS
    live in apply_gates (the gate-1 decision).

    Returns (trainers | None, tvrs, records, invalid_reason | None).
    trainers is None iff invalid — bias is structurally unreachable.
    """
    trainers, tvrs, records = [], [], []
    for s in seeds:
        trainer = train_one(game, budget, s)
        tvr = trained_vs_random(trainer, n=tvr_n)
        rec = dict(orig_seed=s, final_seed=s, tvr=tvr, rerun=False)
        if tvr < COLLAPSE_TVR:
            if not used_reserves["available"]:
                records.append(rec)
                return None, tvrs, records, (
                    f"seed {s} collapsed (tvr {tvr:.3f} < {COLLAPSE_TVR}) "
                    f"and reserves {RESERVE_SEEDS} exhausted "
                    "(third collapse across the grid)")
            reserve = used_reserves["available"].pop(0)
            used_reserves["used"].append(
                dict(cell=cell, orig_seed=s, reserve=reserve))
            print(f"    seed {s} COLLAPSED (tvr {tvr:.3f}) -> ONE "
                  f"replace-in-slot rerun with reserve seed {reserve}",
                  flush=True)
            trainer = train_one(game, budget, reserve)
            tvr2 = trained_vs_random(trainer, n=tvr_n)
            rec = dict(orig_seed=s, final_seed=reserve, tvr=tvr2,
                       rerun=True, orig_tvr=tvr)
            if tvr2 < COLLAPSE_TVR:
                records.append(rec)
                return None, tvrs, records, (
                    f"seed {s}->{reserve} rerun still collapsed "
                    f"(tvr {tvr2:.3f} < {COLLAPSE_TVR})")
            tvr = tvr2
        records.append(rec)
        trainers.append(trainer)
        tvrs.append(tvr)
    return trainers, tvrs, records, None


def calibrate_cell(name, e, m, seeds, budget, eval_n, tvr_n,
                   used_reserves) -> dict:
    """Run one (E, M) cell through the prereg gate ORDER. Gate N+1 compute
    is structurally unreachable when gate N fails (early returns below +
    apply_gates' first-failure short-circuit)."""
    t0 = time.time()
    game = build_f(e, m)
    print(f"  cell {name}: training seeds {seeds} "
          f"(budget {budget}, tvr n={tvr_n}, eval n={eval_n})", flush=True)

    trainers, tvrs, records, invalid = resolve_skill_gate(
        game, seeds, budget, used_reserves, tvr_n, name)
    stats: dict = dict(invalid=invalid, tvrs=tvrs)
    base = dict(cell=name, e=e, m=m, records=records, tvrs=tvrs,
                budget=budget, eval_n=eval_n, seeds=list(seeds),
                ladder=[], bias=None, komi=0, agg=None)

    if trainers is None:
        verdict, reason = apply_gates(stats)  # INVALID — bias never computed
        print(f"  cell {name}: {verdict} ({reason})", flush=True)
        return dict(base, verdict=verdict, reason=reason,
                    elapsed_s=time.time() - t0)
    ok, _ = skill_ok(tvrs)
    if not ok:
        verdict, reason = apply_gates(stats)  # FAIL skill — bias never computed
        print(f"  cell {name}: {verdict} ({reason})", flush=True)
        return dict(base, verdict=verdict, reason=reason,
                    elapsed_s=time.time() - t0)

    # ---- Gate (2): bias at komi 0, then the sign-directed ladder.
    # Komi is applied at EVAL time only (policy reuse — module docstring);
    # the three trainers share one game object, but we set every trainer
    # explicitly so the hygiene survives any future per-trainer copies.
    komi_signed = 0  # at komi 0 the eval runs with komi_cells = 0
    p1_favored = None
    ladder: list[dict] = []
    bias = None
    evals: list[dict] = []
    passed_bias = False
    for komi in (0, *KOMI_LADDER):
        komi_signed = 0 if komi == 0 else signed_komi(komi, p1_favored)
        evals = []
        for tr in trainers:
            tr.game.win_condition.komi_cells = komi_signed
            evals.append(eval_cell_games(tr, n=eval_n))
        p1_share = float(np.mean([ev["p1_share"] for ev in evals]))
        draw_rate = float(np.mean([ev["draw_rate"] for ev in evals]))
        bias = float(np.mean([ev["bias"] for ev in evals]))
        if komi == 0:
            # Direction by the measured bias SIGN at komi 0 (prereg):
            # signed bias > 0 = P1-favored -> positive komi (helps P2).
            p1_favored = signed_bias(p1_share, draw_rate) > 0
        ladder.append(dict(komi=komi_signed, p1_share=p1_share,
                           draw_rate=draw_rate, bias=bias))
        print(f"    komi {komi_signed:+d}: p1_share {p1_share:.3f} "
              f"draws {draw_rate:.3f} bias {bias:.3f}", flush=True)
        if bias <= BIAS_PASS:
            passed_bias = True
            break

    # Hygiene (registered): after the ladder, set every trainer's komi to
    # the WINNING rung (or 0 if none passed) — no stale mutation leaks.
    final_komi = komi_signed if passed_bias else 0
    for tr in trainers:
        tr.game.win_condition.komi_cells = final_komi

    stats.update(bias=bias, komi=komi_signed)  # komi = last rung evaluated
    if passed_bias:
        # Gates (3)/(4) inputs come from the PASSING rung's evals (plan
        # structure: a bias-failing cell never computes gate-3 aggregates).
        stats["agg"] = {
            k: float(np.mean([ev[k] for ev in evals]))
            for k in ("draw_rate", "timeout_share", "score_margin_share",
                      "double_pass_share", "engaged_mean", "mean_length")}
    verdict, reason = apply_gates(stats)
    print(f"  cell {name}: {verdict} ({reason})", flush=True)
    return dict(base, verdict=verdict, reason=reason, ladder=ladder,
                bias=bias, komi=final_komi, agg=stats.get("agg"),
                elapsed_s=time.time() - t0)


# ---------------------------------------------------------------------------
# Grid decision + calibrated write
# ---------------------------------------------------------------------------

def write_calibrated(winner: dict) -> Path:
    """Bake the winning komi into the winner cell's game and write it."""
    game = build_f(winner["e"], winner["m"])
    game.win_condition.komi_cells = int(winner["komi"])
    # Registered harness invariant (build_games Task-5 review): komi must
    # never reach the early-end margin.
    assert abs(game.win_condition.komi_cells) < game.win_condition.end_margin, (
        f"komi/end_margin invariant violated at write time: "
        f"komi {game.win_condition.komi_cells} vs end_margin "
        f"{game.win_condition.end_margin}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "f_frontline.json"
    path.write_text(json.dumps(game.to_dict(), indent=2))
    return path


def decide_grid(state: dict, allow_partial: bool) -> dict:
    """Winner selection over the cells present in calibration.json.

    Full-grid only (siege PARTIAL_WRITE_BLOCKED convention): with cells
    missing, the prereg tie-break has no meaning — block the write unless
    --allow-partial explicitly overrides.
    """
    cells = state["cells"]
    missing = [c for c in ALL_CELLS if c not in cells]
    passing = rank_passing(
        [r for r in cells.values() if r["verdict"].startswith("PASS")])
    decision: dict = dict(
        ranked_passing=[r["cell"] for r in passing],
        winner=None, runner_up=None, status=None)

    if missing and not allow_partial:
        decision["status"] = (
            f"F_GRID_PARTIAL — {len(missing)}/6 cells not yet run "
            f"({', '.join(missing)}); the prereg winner selection is "
            "full-grid only. games/calibrated/f_frontline.json NOT "
            "written (run the missing cells, or --allow-partial).")
        print(decision["status"], flush=True)
        return decision

    if not passing:
        decision["status"] = (
            "F_GRID_UNRESOLVED — no passing cell; campaign NO-GO at "
            "Stage 1 (subject to the prereg KILL_INVALID inspection "
            "branch). games/calibrated/f_frontline.json NOT written.")
        print(decision["status"], flush=True)
        return decision

    winner = passing[0]
    runner_up = passing[1] if len(passing) > 1 else None
    path = write_calibrated(winner)
    decision["winner"] = winner["cell"]
    decision["winner_komi"] = winner["komi"]
    # Runner-up = the registered PARTIAL re-parameterization knob.
    decision["runner_up"] = runner_up["cell"] if runner_up else None
    decision["status"] = (
        f"WINNER {winner['cell']} (komi {winner['komi']:+d}, bias "
        f"{winner['bias']:.3f}, mean_length "
        f"{winner['agg']['mean_length']:.1f}, score_margin_share "
        f"{winner['agg']['score_margin_share']:.3f}) -> {path.name}. "
        f"Runner-up (PARTIAL knob): "
        f"{decision['runner_up'] or 'NONE — PARTIAL would be VOID'}."
        + (" [PARTIAL GRID — --allow-partial override]" if missing else ""))
    print(f"F GRID {decision['status']}", flush=True)
    return decision


# ---------------------------------------------------------------------------
# Comparators arm (provenance stub — full re-assert happens at screen time)
# ---------------------------------------------------------------------------

def run_arm_comparators() -> dict:
    """Verify the probe-calibrated S/A1 artifacts exist and record their
    on-disk calibration provenance. NO retraining in this arm: the prereg
    re-assert ('full recalibration only if retraining drifts bias > 0.10')
    is exercised by the Stage-2 screen, where the retraining happens."""
    out: dict = {}
    for fname, prov in COMPARATOR_PROVENANCE.items():
        path = GAMES_DIR / fname
        if not path.exists():
            out[fname] = dict(present=False, provenance=prov)
            print(f"  comparator {fname}: MISSING from {GAMES_DIR} — run "
                  "build_games.py first", flush=True)
            continue
        d = json.loads(path.read_text())
        out[fname] = dict(
            present=True,
            game_id=d.get("game_id"),
            komi_p2=float(d.get("komi_p2") or 0.0),
            pie_rule=bool(d.get("pie_rule")),
            provenance=prov,
        )
        print(f"  comparator {fname}: present (game_id {out[fname]['game_id']},"
              f" komi_p2 {out[fname]['komi_p2']:.2f}, pie "
              f"{out[fname]['pie_rule']}) — {prov}", flush=True)
    return out


# ---------------------------------------------------------------------------
# Report assembly (calibration.json -> calibration.md, regenerated whole)
# ---------------------------------------------------------------------------

def _cell_section(r: dict) -> list[str]:
    lines = [f"## Cell {r['cell']} — **{r['verdict']}**", "",
             f"E={r['e']:.2f}, M_end={r['m']}; budget {r['budget']}, "
             f"eval n={r['eval_n']}, seeds {r['seeds']} "
             f"({r.get('elapsed_s', 0):.0f}s). Reason: {r['reason']}", ""]
    # Gate 1
    lines += ["Gate 1 (skill — tvr mean >= 0.75, min >= 0.65, "
              "collapse < 0.20 -> replace-in-slot):", "",
              "| orig seed | final seed | tvr | rerun |", "|---|---|---:|---|"]
    for rec in r["records"]:
        rerun = (f"yes (orig tvr {rec['orig_tvr']:.3f})"
                 if rec.get("rerun") else "no")
        lines.append(f"| {rec['orig_seed']} | {rec['final_seed']} "
                     f"| {rec['tvr']:.3f} | {rerun} |")
    if r["tvrs"]:
        mean_tvr = sum(r["tvrs"]) / len(r["tvrs"])
        lines += ["", f"tvr mean {mean_tvr:.3f}, min {min(r['tvrs']):.3f}."]
    # Gate 2
    if r["ladder"]:
        lines += ["", "Gate 2 (seat bias <= 0.10; komi 0 first, then the "
                  "sign-directed ladder — smallest |komi| passing):", "",
                  "| komi_cells | p1_share | draws | bias | <= 0.10? |",
                  "|---:|---:|---:|---:|:---:|"]
        for row in r["ladder"]:
            lines.append(f"| {row['komi']:+d} | {row['p1_share']:.3f} "
                         f"| {row['draw_rate']:.3f} | {row['bias']:.3f} "
                         f"| {'PASS' if row['bias'] <= BIAS_PASS else 'no'} |")
    else:
        lines += ["", "Gate 2 (bias): NOT COMPUTED — gate 1 failed "
                  "(prereg structural order)."]
    # Gates 3-4
    if r["agg"]:
        agg = r["agg"]
        eng_lo, eng_hi = ENGAGED_BAND
        lines += [
            "", "Gates 3-4 (end-cause health; engaged band) at komi "
            f"{r['komi']:+d}:", "",
            f"- timeout_share {agg['timeout_share']:.3f} "
            f"(gate <= {TIMEOUT_SHARE_MAX})",
            f"- draw_rate {agg['draw_rate']:.3f} (gate <= {DRAW_RATE_MAX})",
            f"- score_margin_share {agg['score_margin_share']:.3f} "
            f"(gate >= {SCORE_MARGIN_SHARE_MIN})",
            f"- double_pass_share {agg['double_pass_share']:.3f} "
            f"(LOGGED; yellow flag > {DOUBLE_PASS_YELLOW} — diagnostic, "
            "not a gate)",
            f"- engaged_mean {agg['engaged_mean']:.3f} "
            f"(gate in [{eng_lo}, {eng_hi}]; final-ply mean over ALL games)",
            f"- mean_length {agg['mean_length']:.1f} "
            f"(tie-break centrality vs {LENGTH_CENTER:.0f})",
        ]
    elif r["ladder"]:
        lines += ["", "Gates 3-4: NOT COMPUTED — gate 2 (bias) failed "
                  "(prereg structural order)."]
    return lines + [""]


def write_report(state: dict) -> None:
    CAL_JSON.write_text(json.dumps(state, indent=2))
    out = [
        "# FRONTLINE Stage-1 calibration", "",
        "Pre-registered gates: experiments/frontline/PREREGISTRATION.md "
        "(Stage 1 — the locked authority). Gate ORDER is structural: "
        "skill -> bias -> end-cause -> engaged; a cell that fails gate N "
        "never computes gate N+1. Rerunning a --cells subset replaces "
        "only those cells (sources persist in calibration.json; this "
        "file is regenerated whole each run).", "",
        "**bias** = |p1_share + draw_rate/2 - 0.5| — draws count half to "
        "each side, so a draw-heavy meta cannot masquerade as balance "
        "(p1_share = seat-0 win share over seat-swapped halves; all "
        "statistics over EVERY eval game — no filtering, the R21 "
        "survivorship lesson). Cell bias = mean over seeds of per-seed "
        "|draw-adjusted bias| — conservative when seed signs differ "
        "(opposite-signed per-seed seat advantages do not cancel).", "",
        "**Komi semantics**: komi is applied at EVAL time by setting "
        "trainer.game.win_condition.komi_cells before the eval games "
        "(engines are created per game via create_engine(trainer.game)); "
        "komi only enters score comparisons, never placement legality, "
        "so the komi-0-trained policies are reused unchanged — the same "
        "policy-reuse rationale as siege's S komi sweep. After each "
        "cell's ladder the mutation is reset to the winning rung (or 0), "
        "and the winning komi is baked into "
        "games/calibrated/f_frontline.json at write time (asserting "
        "|komi| < end_margin — the registered harness invariant). "
        "Ladder direction: P1-favored at komi 0 -> POSITIVE komi "
        "(komi_cells is added to P2's score in every engine comparison).",
        "",
    ]
    for name in ALL_CELLS:
        if name in state.get("cells", {}):
            out += _cell_section(state["cells"][name])
    if state.get("reserves_used"):
        out += ["## Reserve seeds consumed (across the grid, in order)", ""]
        for u in state["reserves_used"]:
            out.append(f"- {u['cell']}: seed {u['orig_seed']} -> reserve "
                       f"{u['reserve']}")
        out.append("")
    if state.get("decision"):
        d = state["decision"]
        out += ["## Grid decision (prereg tie-break: length centrality "
                f"closest to {LENGTH_CENTER:.0f} -> max score_margin share "
                "-> min |bias|)", "",
                f"Ranked passing cells: "
                f"{', '.join(d['ranked_passing']) or 'NONE'}", "",
                f"**{d['status']}**", ""]
    if state.get("comparators"):
        out += ["## Comparators (S/A1 re-assert stub — provenance check "
                "only; full re-assert at screen time)", ""]
        for fname, c in state["comparators"].items():
            if c.get("present"):
                out.append(f"- `{fname}`: present (game_id {c['game_id']}, "
                           f"komi_p2 {c['komi_p2']:.2f}, "
                           f"pie {c['pie_rule']}). {c['provenance']}")
            else:
                out.append(f"- `{fname}`: **MISSING** — run build_games.py. "
                           f"Registered provenance: {c['provenance']}")
        out.append("")
    CAL_MD.write_text("\n".join(out))
    print(f"wrote {CAL_MD.name}", flush=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def load_state() -> dict:
    """calibration.json sources; fail loudly on corruption (siege rule)."""
    if CAL_JSON.exists():
        try:
            return json.loads(CAL_JSON.read_text())
        except json.JSONDecodeError as e:
            raise SystemExit(
                f"corrupt {CAL_JSON}: {e}\n"
                "Rename or delete it to start fresh.") from e
    return {}


def main() -> None:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--arm", default="f", choices=("f", "comparators", "all"))
    p.add_argument("--budget", type=int, default=3000)
    p.add_argument("--eval-episodes", type=int, default=200,
                   help="per-trainer eval n per komi rung; "
                        "tvr n = max(10, n // 2) (siege convention)")
    p.add_argument("--seeds", default="42,43,44")
    p.add_argument("--cells", default=None,
                   help="comma-separated cell subset, e.g. "
                        f"'E1p00_M8'; valid: {', '.join(ALL_CELLS)}")
    p.add_argument("--allow-partial", action="store_true",
                   help="permit the winner selection/write over a partial "
                        "grid (default: blocked — the prereg tie-break is "
                        "full-grid only)")
    args = p.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]
    tvr_n = max(10, args.eval_episodes // 2)

    state = load_state()
    state.setdefault("cells", {})
    state.setdefault("reserves_used", [])

    t0 = time.time()
    if args.arm in ("f", "all"):
        if args.cells:
            wanted = [c.strip() for c in args.cells.split(",")]
            unknown = [c for c in wanted if c not in ALL_CELLS]
            if unknown:
                raise SystemExit(f"unknown --cells {unknown}; "
                                 f"valid: {list(ALL_CELLS)}")
            cells = wanted
        else:
            cells = list(ALL_CELLS)
        # Reserves are consumed in order ACROSS THE GRID — including
        # across subset reruns (consumption persists in calibration.json).
        consumed = {u["reserve"] for u in state["reserves_used"]}
        used_reserves = {
            "available": [s for s in RESERVE_SEEDS if s not in consumed],
            "used": state["reserves_used"],
        }
        print(f"=== arm f: cells {cells} ===", flush=True)
        for name in cells:
            e, m = ALL_CELLS[name]
            state["cells"][name] = calibrate_cell(
                name, e, m, seeds, args.budget, args.eval_episodes,
                tvr_n, used_reserves)
            write_report(state)  # checkpoint after each cell (crash safety)
        state["decision"] = decide_grid(state, args.allow_partial)

    if args.arm in ("comparators", "all"):
        print("=== arm comparators (provenance stub) ===", flush=True)
        state["comparators"] = run_arm_comparators()

    write_report(state)
    print(f"done in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
