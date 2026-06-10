"""SIEGE Stage-1 calibration driver (prereg Stage 1).

Arm m — (N,T) grid {3,5,8}x{80,120,160}, seeds 42/43/44. Per cell, gate
ORDER is pre-registered (PREREGISTRATION.md "Stage 1 calibration"):
  (1) per-role skill gates FIRST — role tvr >= 0.80 AND >= +0.15 over that
      role's random-vs-random baseline; a collapsed seed (role tvr < 0.20)
      triggers ONE fresh-seed rerun (45 then 46), never exclusion. The
      cross-seed matrix (and therefore bias) is structurally unreachable
      until every seed's skill gates resolve — see calibrate_cell().
  (2) role bias = |mean Maker win rate - 0.5| <= 0.10 over the k x k
      cross-seed role matrix (3x3 x 22 = 198 games at --eval-episodes 200);
  (3) quota share of Breaker wins >= 0.20; timeout share <= 0.25 of ALL games.
Tie-break among passing cells: max quota share, then min |bias|. Winner is
written verbatim to games/calibrated/m_siege.json (komi_p2 stays 0.0, pie
stays False). NO passing cell -> loud M_GRID_UNRESOLVED, no file written,
exit 0 (registered outcome — run_screen loud-skips the missing file; the
role-pie fallback is a registered retry that returns via a plan update).

Arm s — komi sweep adapted nearly verbatim from experiments/fc_phase15/
calibrate.py onto games/s_flip_r2.json: pie ON at komi 0.00 first, then
grid 0.05..0.30 step 0.05; sampled mirror eval n=--eval-episodes; PASS =
smallest komi with bias <= 0.10 -> games/calibrated/s_flip_r2.json.

Arm eps — one eps=0.25 @ r=2 sensitivity cell on s_flip_r2
(control_margin=0.25, game_id s_flip_r2_eps025), 1 seed, DIAGNOSTIC ONLY:
no gate, no calibrated output.

Report: calibration.md (sections per arm, every gate decision visible).
Rerunning an arm replaces only its section — section sources persist in
calibration.json and the whole .md is regenerated from it each run.

Usage:
    .venv/bin/python experiments/siege/calibrate.py --arm {m,s,eps,all} \\
        [--budget 3000] [--eval-episodes 200] [--seeds 42,43,44] \\
        [--grid-cells N5_T120,N3_T80]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from config import MetricsConfig, TrainingConfig  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from training.trainer import SelfPlayTrainer  # noqa: E402

# Shared seat-swap stochastic eval — same function fc_phase15 imports
# (methodology of record for symmetric-arm bias since the FC probe).
from experiments.field_connect_probe.calibrate import (  # noqa: E402
    sampled_mirror_eval,
)
from experiments.siege.eval_roles import (  # noqa: E402
    per_role_tvr,
    role_bias_from_matrix,
    role_matrix,
)

HERE = Path(__file__).resolve().parent
GAMES_DIR = HERE / "games"
OUT_DIR = GAMES_DIR / "calibrated"
CAL_JSON = HERE / "calibration.json"
CAL_MD = HERE / "calibration.md"

# ---------------------------------------------------------------------------
# Pre-registered Stage-1 gate constants — experiments/siege/PREREGISTRATION.md
# ("Stage 1 calibration"). Not altered after data. Skill-gate constants
# (TVR_PASS/TVR_MARGIN/COLLAPSE_TVR/GAMES_PER_PAIR) live in eval_roles.py.
# ---------------------------------------------------------------------------
BIAS_PASS = 0.10           # gate (2): role/seat bias
QUOTA_SHARE_MIN = 0.20     # gate (3): quota share of Breaker wins
TIMEOUT_SHARE_MAX = 0.25   # gate (3): timeout share of ALL games
RESERVE_SEEDS = (45, 46)   # collapsed-seed rerun seeds, consumed in order
KOMI_GRID = (0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30)  # s arm: 0.00 first
GRID_N = (3, 5, 8)
GRID_T = (80, 120, 160)
EPS_CONTROL_MARGIN = 0.25  # the single licensed re-parameterization knob


def next_reserve(used: list[int]) -> int | None:
    """First reserve seed in RESERVE_SEEDS not yet consumed, else None.

    Pure bookkeeping for the collapsed-seed rerun rule: reserves are
    consumed in order (45 then 46), at most one rerun per original seed.
    """
    for s in RESERVE_SEEDS:
        if s not in used:
            return s
    return None


def train_one(game: GameDefV2, budget: int, seed: int) -> SelfPlayTrainer:
    """Train one PPO self-play run (fc_phase15 config shape)."""
    cfg = TrainingConfig(training_budget=budget, eval_episodes=100)
    trainer = SelfPlayTrainer(
        game, cfg, MetricsConfig(learning_curve_checkpoints=2), seed=seed,
    )
    trainer.train()
    return trainer


def _fmt_tvr(rec: dict) -> str:
    """Per-seed tvr summary token, e.g. '42:M0.85/B0.62' or, after a
    collapsed-seed rerun, '42(M0.05/B0.10)→45:M.../B...'."""
    t = rec["tvr"]
    if rec["rerun"]:
        o = rec["orig_tvr"]
        seed_part = (f"{rec['orig_seed']}"
                     f"(M{o['maker_tvr']:.2f}/B{o['breaker_tvr']:.2f})"
                     f"→{rec['final_seed']}")
    else:
        seed_part = f"{rec['orig_seed']}"
    flags = ""
    if t["collapsed"]:
        flags = "!COLLAPSED"
    elif not (t["maker_pass"] and t["breaker_pass"]):
        flags = "!skill"
    return (f"{seed_part}:M{t['maker_tvr']:.2f}/B{t['breaker_tvr']:.2f}"
            f"(base {t['maker_baseline']:.2f}/{t['breaker_baseline']:.2f})"
            f"{flags}")


def resolve_skill_gates(game, seeds, budget, tvr_n):
    """Gate (1): per-role skill gates, with collapsed-seed reruns.

    Returns (trainers | None, seed_records, failure_reason | None).
    trainers is None whenever the cell's skill gates did not resolve —
    callers cannot reach the role matrix (gate 2) in that case.
    """
    trainers: list[SelfPlayTrainer] = []
    records: list[dict] = []
    used_reserves: list[int] = []

    for s in seeds:
        trainer = train_one(game, budget, s)
        tvr = per_role_tvr(game, trainer, n=tvr_n)
        rec = dict(orig_seed=s, final_seed=s, tvr=tvr, rerun=False)

        if tvr["collapsed"]:
            reserve = next_reserve(used_reserves)
            if reserve is None:
                records.append(rec)
                return None, records, (
                    f"INVALID: seed {s} collapsed "
                    f"(M{tvr['maker_tvr']:.2f}/B{tvr['breaker_tvr']:.2f}) "
                    f"and reserve seeds {RESERVE_SEEDS} exhausted")
            used_reserves.append(reserve)
            print(f"    seed {s} COLLAPSED "
                  f"(M{tvr['maker_tvr']:.2f}/B{tvr['breaker_tvr']:.2f}) "
                  f"-> ONE rerun with reserve seed {reserve}", flush=True)
            orig_tvr = tvr
            trainer = train_one(game, budget, reserve)
            tvr = per_role_tvr(game, trainer, n=tvr_n)
            rec = dict(orig_seed=s, final_seed=reserve, tvr=tvr,
                       rerun=True, orig_tvr=orig_tvr)
            if tvr["collapsed"] or not (tvr["maker_pass"]
                                        and tvr["breaker_pass"]):
                records.append(rec)
                return None, records, (
                    f"INVALID: seed {s}→{reserve} rerun still fails skill "
                    f"gates (M{tvr['maker_tvr']:.2f}/B{tvr['breaker_tvr']:.2f}"
                    f", base {tvr['maker_baseline']:.2f}/"
                    f"{tvr['breaker_baseline']:.2f})")

        records.append(rec)
        trainers.append(trainer)

    # All seeds non-collapsed (post any reruns): plain skill-gate check.
    failing = [r for r in records
               if not (r["tvr"]["maker_pass"] and r["tvr"]["breaker_pass"])]
    if failing:
        detail = "; ".join(_fmt_tvr(r) for r in failing)
        return None, records, f"FAIL skill-gates: {detail}"
    return trainers, records, None


def calibrate_cell(game, cell, seeds, budget, tvr_n, games_per_pair) -> dict:
    """Run one (N,T) cell through the pre-registered gate ORDER.

    Bias (gate 2) is computed ONLY after gate (1) resolves: the early
    return below is the structural guarantee.
    """
    t0 = time.time()
    print(f"  cell {cell}: training seeds {seeds} "
          f"(budget {budget}, tvr n={tvr_n})", flush=True)
    trainers, records, fail = resolve_skill_gates(game, seeds, budget, tvr_n)
    seeds_summary = " ".join(_fmt_tvr(r) for r in records)

    if trainers is None:
        # Gate (1) unresolved/failed -> bias is never computed for this cell.
        verdict = "INVALID" if fail.startswith("INVALID") else "FAIL"
        print(f"  cell {cell}: {fail}", flush=True)
        reason = fail.removeprefix("INVALID: ")  # verdict already says it
        return dict(cell=cell, verdict=verdict, reason=reason,
                    seeds_summary=seeds_summary, bias=None,
                    quota_share=None, timeout_share=None,
                    elapsed_s=time.time() - t0)

    matrix, agg = role_matrix(game, trainers, games_per_pair=games_per_pair)
    bias = role_bias_from_matrix(matrix)
    quota_share = agg["quota_wins"] / max(1, agg["breaker_wins"])
    timeout_share = agg["timeout_games"] / max(1, agg["n"])
    for row in matrix:
        print(f"    matrix row: {['%.3f' % v for v in row]}", flush=True)
    print(f"    tallies: {agg}", flush=True)

    failures = []
    if bias > BIAS_PASS:
        failures.append(f"bias {bias:.3f} > {BIAS_PASS}")
    if quota_share < QUOTA_SHARE_MIN:
        failures.append(f"quota_share {quota_share:.3f} < {QUOTA_SHARE_MIN}")
    if timeout_share > TIMEOUT_SHARE_MAX:
        failures.append(
            f"timeout_share {timeout_share:.3f} > {TIMEOUT_SHARE_MAX}")

    verdict = "PASS" if not failures else "FAIL"
    reason = "all gates clear" if not failures else "; ".join(failures)
    print(f"  cell {cell}: {verdict} ({reason})", flush=True)
    return dict(cell=cell, verdict=verdict, reason=reason,
                seeds_summary=seeds_summary, bias=bias,
                quota_share=quota_share, timeout_share=timeout_share,
                elapsed_s=time.time() - t0)


# ---------------------------------------------------------------------------
# Arms
# ---------------------------------------------------------------------------

def run_arm_m(args, seeds) -> list[str]:
    games_per_pair = max(1, args.eval_episodes // 9)
    tvr_n = max(10, args.eval_episodes // 2)  # 100 at the registered n=200
    all_cells = [f"N{n}_T{t}" for n in GRID_N for t in GRID_T]
    if args.grid_cells:
        wanted = [c.strip() for c in args.grid_cells.split(",")]
        unknown = [c for c in wanted if c not in all_cells]
        if unknown:
            raise SystemExit(f"unknown --grid-cells {unknown}; "
                             f"valid: {all_cells}")
        cells = wanted
    else:
        cells = all_cells

    lines = [
        "## Arm m — m_siege (N,T) grid",
        "",
        f"Seeds {seeds}, PPO budget {args.budget}, tvr n={tvr_n}/role, "
        f"matrix {len(seeds)}x{len(seeds)} x {games_per_pair} games/pair. "
        f"Gate ORDER: skill (tvr >= 0.80, >= +0.15 over baseline, "
        f"collapse < 0.20 -> one reserve rerun {RESERVE_SEEDS}) -> "
        f"bias <= {BIAS_PASS} -> quota_share >= {QUOTA_SHARE_MIN}, "
        f"timeout_share <= {TIMEOUT_SHARE_MAX}. "
        f"Cells run: {', '.join(cells)}"
        + (" (FILTERED subset — not a full-grid decision)"
           if args.grid_cells else "") + ".",
        "",
        "| cell | per-seed tvr (M/B, baselines) | bias | quota_share "
        "| timeout_share | verdict |",
        "|---|---|---:|---:|---:|:---|",
    ]

    results = []
    for cell in cells:
        path = GAMES_DIR / f"m_siege_{cell}.json"
        game = GameDefV2.from_dict(json.loads(path.read_text()))
        res = calibrate_cell(game, cell, seeds, args.budget,
                             tvr_n, games_per_pair)
        results.append(res)
        bias_s = f"{res['bias']:.3f}" if res["bias"] is not None else "—"
        qs = (f"{res['quota_share']:.3f}"
              if res["quota_share"] is not None else "—")
        ts = (f"{res['timeout_share']:.3f}"
              if res["timeout_share"] is not None else "—")
        lines.append(f"| {cell} | {res['seeds_summary']} | {bias_s} | {qs} "
                     f"| {ts} | **{res['verdict']}** — {res['reason']} |")

    passing = [r for r in results if r["verdict"] == "PASS"]
    if passing:
        # Tie-break (pre-registered): max quota share, then min |bias|.
        winner = sorted(passing,
                        key=lambda r: (-r["quota_share"], r["bias"]))[0]
        if args.grid_cells and not args.allow_partial:
            # Partial-write hazard: a calibrated file from a FILTERED run
            # is indistinguishable on disk from a full-grid decision, but
            # the prereg winner selection only has meaning over the
            # COMPLETE grid. Block the write unless explicitly overridden.
            lines += ["", f"**PARTIAL_WRITE_BLOCKED** — best filtered cell "
                          f"was {winner['cell']} "
                          f"(quota_share {winner['quota_share']:.3f}, "
                          f"bias {winner['bias']:.3f}), but this was a "
                          f"--grid-cells run and the prereg tie-break is "
                          f"full-grid only. games/calibrated/m_siege.json "
                          f"NOT written (use --allow-partial to override)."]
            print("PARTIAL_WRITE_BLOCKED: filtered run; use --allow-partial "
                  "to override", flush=True)
        else:
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            src = GAMES_DIR / f"m_siege_{winner['cell']}.json"
            shutil.copy(src, OUT_DIR / "m_siege.json")  # verbatim copy
            lines += ["", f"**WINNER: {winner['cell']}** "
                          f"(quota_share {winner['quota_share']:.3f}, "
                          f"bias {winner['bias']:.3f}) -> "
                          f"games/calibrated/m_siege.json (verbatim copy; "
                          f"komi_p2 0.0, pie False)."]
            print(f"ARM M WINNER: {winner['cell']} -> "
                  f"calibrated/m_siege.json", flush=True)
    else:
        lines += ["", "**M_GRID_UNRESOLVED** — no (N,T) cell passed all "
                      "gates. games/calibrated/m_siege.json NOT written; "
                      "run_screen will loud-skip the M arm. Registered "
                      "outcome (role-pie fallback returns via plan update), "
                      "not an error."]
        print("M_GRID_UNRESOLVED: no passing cell — calibrated/m_siege.json "
              "NOT written (registered outcome)", flush=True)
    return lines


def run_arm_s(args, seeds) -> list[str]:
    """Komi sweep — adapted nearly verbatim from fc_phase15/calibrate.py."""
    seed = seeds[0]
    base = json.loads((GAMES_DIR / "s_flip_r2.json").read_text())
    game = GameDefV2.from_dict(base)
    lines = [
        "## Arm s — s_flip_r2 komi calibration",
        "",
        f"PPO budget {args.budget}, seed {seed}, sampled mirror eval "
        f"n={args.eval_episodes} (seat-swap, deterministic=False). "
        f"Pie ON at komi 0.00 first; grid fallback "
        f"{KOMI_GRID[1]:.2f}..{KOMI_GRID[-1]:.2f}. "
        f"PASS = smallest komi with bias <= {BIAS_PASS}.",
        "",
        "| arm | komi | p1_winrate | bias | draws | verdict |",
        "|---|---:|---:|---:|---:|:---:|",
    ]
    chosen = None
    for komi in KOMI_GRID:
        game.komi_p2 = komi
        trainer = train_one(game, args.budget, seed)
        # sampled_mirror_eval returns (p1_winrate, draw_rate, avg_length)
        p1_wr, draws, _ = sampled_mirror_eval(
            trainer, args.eval_episodes, game.max_game_steps,
        )
        bias = abs(p1_wr - 0.5)
        ok = bias <= BIAS_PASS
        row = (f"| s_flip_r2 | {komi:.2f} | {p1_wr:.3f} | {bias:.3f} "
               f"| {draws:.3f} | {'PASS' if ok else 'no'} |")
        lines.append(row)
        print(row, flush=True)
        if ok and chosen is None:
            chosen = komi
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            # Serialise via to_dict() so computed fields round-trip
            # (fc_phase15 convention).
            with open(OUT_DIR / "s_flip_r2.json", "w") as f:
                json.dump(game.to_dict(), f, indent=2)
            break  # smallest passing komi found — stop sweeping
    if chosen is None:
        lines.append("| s_flip_r2 | — | — | — | — | **BIAS_UNRESOLVED** |")
        print("WARNING: s_flip_r2 BIAS_UNRESOLVED — calibrated/s_flip_r2.json"
              " NOT written (run_screen will loud-skip)", flush=True)
    return lines


def run_arm_eps(args, seeds) -> list[str]:
    """eps=0.25 @ r=2 sensitivity cell — DIAGNOSTIC ONLY (prereg Stage 1)."""
    seed = seeds[0]
    base = json.loads((GAMES_DIR / "s_flip_r2.json").read_text())
    game = GameDefV2.from_dict(base)
    game.win_condition.control_margin = EPS_CONTROL_MARGIN
    game.game_id = "s_flip_r2_eps025"
    trainer = train_one(game, args.budget, seed)
    p1_wr, draws, length = sampled_mirror_eval(
        trainer, args.eval_episodes, game.max_game_steps,
    )
    bias = abs(p1_wr - 0.5)
    row = (f"| s_flip_r2_eps025 | {p1_wr:.3f} | {bias:.3f} | {draws:.3f} "
           f"| {length:.1f} | DIAGNOSTIC ONLY |")
    print(row, flush=True)
    return [
        "## Arm eps — eps=0.25 @ r=2 sensitivity cell (DIAGNOSTIC ONLY)",
        "",
        f"control_margin={EPS_CONTROL_MARGIN} on s_flip_r2 (as loaded, "
        f"komi_p2={base.get('komi_p2', 0.0)}), seed {seed}, budget "
        f"{args.budget}, sampled mirror eval n={args.eval_episodes}. "
        "NO gate, NO calibrated output — pre-bound as the single licensed "
        "PARTIAL re-parameterization knob.",
        "",
        "| arm | p1_winrate | bias | draws | avg_length | verdict |",
        "|---|---:|---:|---:|---:|:---:|",
        row,
    ]


# ---------------------------------------------------------------------------
# Report assembly (calibration.json -> calibration.md, section per arm)
# ---------------------------------------------------------------------------

def write_report(state: dict) -> None:
    CAL_JSON.write_text(json.dumps(state, indent=2))
    out = ["# SIEGE Stage-1 calibration",
           "",
           "Pre-registered gates: experiments/siege/PREREGISTRATION.md "
           "(Stage 1). Rerunning an arm replaces its section "
           "(sources persist in calibration.json).",
           ""]
    for arm in ("m", "s", "eps"):
        if arm in state:
            out += state[arm] + [""]
    CAL_MD.write_text("\n".join(out))
    print(f"wrote {CAL_MD.name}", flush=True)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--arm", required=True, choices=("m", "s", "eps", "all"))
    p.add_argument("--budget", type=int, default=3000)
    p.add_argument("--eval-episodes", type=int, default=200,
                   help="matrix n (games_per_pair = max(1, n // 9)) and "
                        "mirror-eval n; tvr n = max(10, n // 2)")
    p.add_argument("--seeds", default="42,43,44")
    p.add_argument("--grid-cells", default=None,
                   help='M-grid ONLY (arms s/eps never consult it): '
                        'comma-separated cell filter, e.g. "N5_T120"')
    p.add_argument("--allow-partial", action="store_true",
                   help="permit writing games/calibrated/m_siege.json from "
                        "a --grid-cells FILTERED run (default: blocked — "
                        "the prereg winner selection is full-grid only)")
    args = p.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]

    # calibration.json shape: {"m": [md lines], "s": [...], "eps": [...]}
    # Likeliest corruption mode on the multi-hour run: truncated write from
    # a Ctrl-C mid-write_report. Fail loudly rather than silently resetting.
    if CAL_JSON.exists():
        try:
            state = json.loads(CAL_JSON.read_text())
        except json.JSONDecodeError as e:
            raise SystemExit(
                f"corrupt {CAL_JSON}: {e}\n"
                "Rename or delete it to start fresh.") from e
    else:
        state = {}
    arms = ("m", "s", "eps") if args.arm == "all" else (args.arm,)
    t0 = time.time()
    for arm in arms:
        print(f"=== arm {arm} ===", flush=True)
        if arm == "m":
            state["m"] = run_arm_m(args, seeds)
        elif arm == "s":
            state["s"] = run_arm_s(args, seeds)
        else:
            state["eps"] = run_arm_eps(args, seeds)
    write_report(state)
    print(f"done in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
