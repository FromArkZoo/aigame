"""RC2 pre-campaign gate — CAL-C: cost projection [§5(b)].

Pre-data cost measurement (no search spend). Before any campaign search
spend, this obligation times ~20 fresh genomes end-to-end through the FULL
per-genome pipeline — descriptor batch + T1 eval + guard stage + one
full-conv re-eval — and projects the campaign wall (Stage-0 240 evals +
2 arms x 600 + 4 full-conv checkpoints) over 7 workers against the 8h
search-phase cap (run_campaign.WALL_CAP_S). Projection over the cap ->
this file flags RE-SCOPE REQUIRED (re-registration of B, never a silent
change) — an OWNER-level decision. The runner (run_campaign.py) does not
read cal_c.json; it only informs the launch decision (contrast cal_i.json,
which the runner refuses to start a real campaign without).

Reuse (BUILD_LOG #9 pooled path, not a re-implementation): descriptor batch
via run_campaign.compute_descriptor_batch (module-level, Phase C verbatim);
T1 and full-conv batches both via a minimally-instantiated
run_campaign.Campaign's bound method pg_batch_pooled (the exact pooled
fan-out the runner uses for both ledgers — it pools the module-level
_pg_game_worker via pg_eval.pg_seeds/pg_summarise); guard stage via the same
Campaign instance's guard_stage_pooled (pools the module-level
_tactical_worker via guard_stage.guard_pair_seeds/_verdict_from_shares — the
exact path the runner's insertion pipeline calls, NOT the sequential
guard_stage.run_guard_stage, since the runner itself uses the pooled
variant and wall-time fidelity requires timing the real thing). Per Task 9's
dispatch, the guard stage is run for EVERY CAL genome regardless of
would-enter status (offer(); prereg §4 step 4 normally gates it on "would
enter" — CAL-C is timing the guard's cost in isolation, not exercising
archive logic; the offer_rate assumption in the projection model accounts
for the gate).

CAL genome slot (comment carries the rationale — no new seeds.py entry
needed, see below): fresh genomes are drawn from
seeds.GEN_SEED_BASE + 500_000 + attempt, i.e. offset 500_000 inside
GEN_SEED_BASE's own registered SPAN (1_000_000, seeds.py). This keeps CAL-C's
draws disjoint from:
  - Stage-0's own attempts, base + [0, STAGE0_MAX_ATTEMPTS=3000)
  - the smoke seed range, 999_000_000+ (seeds.RECORDED_STREAMS["smoke"])
while staying entirely inside GEN_SEED_BASE + SPAN, a range
seeds.assert_disjoint() already validates as a whole against every other
recorded stream — so no additional RECORDED_STREAMS entry is required.
(test_cal_c.py asserts the disjointness claim directly.)

Projection model (§5(b), documented again in the rendered MD):
    search_phase_work =
        [Stage0: STAGE0_MAX_EVALS x (descriptor_n100 + T1
                                     + stage0_offer_rate x guard)]
      + [arms:   2*B_ARM x (descriptor_n50 + T1 + offer_rate x guard)]
      + [full-conv: len(REEVAL_AT) x 2 arms x archive_size_estimate x
                    full_conv]
    wall_hours = search_phase_work / WORKERS / 3600
Three assumptions (marked, not measured): offer_rate ~= 0.3 (share of arm
evals that trigger the guard stage at insertion time); stage0_offer_rate ~=
0.8 (in the real runner, init_archives() offers every valid Stage-0 genome
to BOTH archives — archives start empty so the would-enter rate is high;
the runner's per-canon guard cache means the guard runs ONCE per genome
even though it's offered to both archives, so this is not doubled); and
archive_size_estimate ~= 50/arm/checkpoint (elites re-priced by
reeval_full_conv at each checkpoint). descriptor_n50 is derived (not
hardcoded) as N_STAGE1/N_STAGE0 (50/100 = x0.5, a linear-in-rollout-count
scaling assumption, not separately measured) — all three are documented,
not hardcoded past the module constants below. Optimistic = measured
per-stage mean; pessimistic = mean + 1 SD per stage. The verdict
(within_cap/rescope_required) gates on the PESSIMISTIC projection — a
pre-launch cost gate should not clear on the optimistic case alone.

File contract (belt-and-braces, owner-gated real spend — mirrors cal_i.py)
---------------------------------------------------------------------------
  --real      Runs the REAL measurement (~20 fresh genomes through the FULL
              pipeline at production sims/n — expensive, expect tens of
              minutes). Writes cal_c.json + CAL_C.md next to this file.
  --dry-run   Tiny wiring check (3 genomes, sims 32v8, T1 n=8, guard
              n_pairs=4, full-conv 64v8 n=8); writes cal_c_dryrun.json +
              CAL_C_DRYRUN.md. NEVER writes cal_c.json/CAL_C.md.
  (neither)   Refuses to run anything (real spend is owner-gated) and prints
              how to invoke either mode.
  --from-cache  Re-derives the projection + MD from the existing JSON for
              the selected mode without re-running genomes.

Output: cal_c.json + CAL_C.md (real) or cal_c_dryrun.json + CAL_C_DRYRUN.md
(dry run), next to this file.
Run:    .venv/bin/python experiments/rc2_campaign/cal_c.py --real
        .venv/bin/python experiments/rc2_campaign/cal_c.py --dry-run
        .venv/bin/python experiments/rc2_campaign/cal_c.py --real --from-cache
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.rc2_campaign import seeds  # noqa: E402
from experiments.rc2_campaign.guard_stage import N_PAIRS  # noqa: E402
from experiments.rc2_campaign.pg_eval import (  # noqa: E402
    FULL_DEEP,
    FULL_N,
    FULL_SHALLOW,
    T1_DEEP,
    T1_N,
    T1_SHALLOW,
)
from experiments.rc2_campaign.run_campaign import (  # noqa: E402
    B_ARM,
    N_STAGE0,
    N_STAGE1,
    REEVAL_AT,
    STAGE0_MAX_EVALS,
    WALL_CAP_S,
    WORKERS,
    Campaign,
    EvalTimeout,
    compute_descriptor_batch,
)

HERE = Path(__file__).resolve().parent
OUT_JSON = HERE / "cal_c.json"           # REAL artifact
OUT_MD = HERE / "CAL_C.md"
DRYRUN_JSON = HERE / "cal_c_dryrun.json"  # dry-run artifact — never real
DRYRUN_MD = HERE / "CAL_C_DRYRUN.md"

# --- CAL genome slot (see module docstring for the disjointness rationale) -
CAL_SEED_OFFSET = 500_000
CAL_SEED_BASE = seeds.GEN_SEED_BASE + CAL_SEED_OFFSET

N_GENOMES = 20              # §5(b): "~20 fresh genomes"
MAX_ATTEMPTS = 2000         # cap on draw attempts (report if hit)

CAP_HOURS = WALL_CAP_S / 3600.0     # 8.0h — single source of truth (run_campaign)
ARCHIVE_SIZE_ESTIMATE = 50          # ASSUMPTION: elites/arm re-priced per checkpoint
OFFER_RATE = 0.3                    # ASSUMPTION: share of arm evals triggering guard
STAGE0_OFFER_RATE = 0.8             # ASSUMPTION: init_archives() offers every valid
                                     # Stage-0 genome to BOTH archives; archives start
                                     # empty so the would-enter rate is high — and the
                                     # runner's per-canon guard cache means the guard
                                     # runs ONCE per genome even though it's offered to
                                     # both archives, so this is not doubled.
N_ARMS = 2
DESCRIPTOR_N50_SCALE = N_STAGE1 / N_STAGE0  # derived (not hardcoded): n50/n100 rollout
                                             # count ratio (50/100 = x0.5)

# real (production instrument) sizing — imported constants, not re-hardcoded
DESCRIPTOR_N100 = N_STAGE0   # 100, matches Stage 0
GUARD_PAIRS = N_PAIRS        # 12

# --dry-run wiring-check sizing — tiny, non-binding, never touches OUT_JSON
DRY_N_GENOMES = 3
DRY_MAX_ATTEMPTS = 200
DRY_DESCRIPTOR_N100 = 10
DRY_T1_DEEP, DRY_T1_SHALLOW, DRY_T1_N = 32, 8, 8
DRY_GUARD_PAIRS = 4
DRY_FULL_DEEP, DRY_FULL_SHALLOW, DRY_FULL_N = 64, 8, 8


# ---------------------------------------------------------------------------
# Genome draw (mirrors run_campaign.Campaign.run_stage0's filter order:
# simultaneous-move exclusion -> quick_reject -> canonical-hash dedup).
# `gen` needs only generate_game(seed=...)/quick_reject(game)
# (GameGeneratorV2's interface) so the cap-detection logic here is testable
# with a stub, no engine required (test_cal_c.py).
# ---------------------------------------------------------------------------

def draw_cal_genomes(gen, *, seed_base: int = CAL_SEED_BASE,
                     n_target: int = N_GENOMES,
                     max_attempts: int = MAX_ATTEMPTS
                     ) -> tuple[list[tuple], dict]:
    seen: set[str] = set()
    accepted: list[tuple] = []
    attempts = 0
    while len(accepted) < n_target and attempts < max_attempts:
        game = gen.generate_game(seed=seed_base + attempts)
        attempts += 1
        if game.turn_structure.turn_type == "simultaneous":
            continue
        if not gen.quick_reject(game):
            continue
        canon = game.canonical_hash()
        if canon in seen:
            continue
        seen.add(canon)
        accepted.append((game, canon))
    report = dict(seed_base=seed_base, n_target=n_target,
                  max_attempts=max_attempts, attempts=attempts,
                  accepted=len(accepted),
                  attempt_cap_hit=len(accepted) < n_target)
    return accepted, report


# ---------------------------------------------------------------------------
# Per-genome timing — reuses run_campaign's own pieces directly (see module
# docstring "Reuse" paragraph for exactly what is reused vs wrapped).
# ---------------------------------------------------------------------------

def time_genome(campaign: Campaign, game, canon: str, full_batch_index: int, *,
                descriptor_n: int, t1_deep: int, t1_shallow: int, t1_n: int,
                full_deep: int, full_shallow: int, full_n: int) -> dict:
    family = game.win_condition.condition_type

    t0 = time.monotonic()
    compute_descriptor_batch(game, canon, 0, descriptor_n)
    descriptor_s = time.monotonic() - t0

    t0 = time.monotonic()
    t1 = campaign.pg_batch_pooled(game, canon, 0, t1_deep, t1_shallow, t1_n)
    t1_s = time.monotonic() - t0

    t0 = time.monotonic()
    guard = campaign.guard_stage_pooled(game, canon, family,
                                        reach_draw_count=t1["draws"],
                                        reach_n=t1["n"])
    guard_s = time.monotonic() - t0

    t0 = time.monotonic()
    full = campaign.pg_batch_pooled(game, canon, full_batch_index,
                                    full_deep, full_shallow, full_n)
    full_conv_s = time.monotonic() - t0

    total_s = descriptor_s + t1_s + guard_s + full_conv_s
    return dict(canon=canon, family=family,
               descriptor_s=descriptor_s, t1_s=t1_s, guard_s=guard_s,
               full_conv_s=full_conv_s, total_s=total_s,
               t1_raw_pg=t1["raw_pg"], guard_passed=guard["passed"],
               full_conv_raw_pg=full["raw_pg"])


# ---------------------------------------------------------------------------
# Pure helpers: stage summary + projection arithmetic + verdict
# ---------------------------------------------------------------------------

STAGES = ("descriptor_s", "t1_s", "guard_s", "full_conv_s", "total_s")


def min_successes_required(n_requested: int) -> int:
    """§5(b) real-loop failure tolerance floor: the real measurement loop
    (`run_measurement`) tolerates per-genome timeouts/errors, but refuses to
    write a projection off too small a surviving sample. Pure arithmetic —
    floor of 3, else half the requested genome count."""
    return max(3, n_requested // 2)


def has_sufficient_sample(n_success: int, n_requested: int) -> bool:
    """Whether `n_success` successfully-timed genomes (out of `n_requested`
    requested) clears `min_successes_required`. Pure."""
    return n_success >= min_successes_required(n_requested)


def summarise_stage_timings(records: list[dict]) -> dict:
    """Per-stage mean/SD across CAL genomes. Pure — operates on already-
    measured timing dicts, no engine call."""
    out = {}
    for stage in STAGES:
        vals = [r[stage] for r in records]
        n = len(vals)
        mean = float(np.mean(vals)) if n else float("nan")
        sd = float(np.std(vals, ddof=1)) if n > 1 else 0.0
        out[stage] = dict(mean=mean, sd=sd, n=n)
    return out


def project_campaign_hours(stage_stats: dict, *, spread: float = 0.0,
                           descriptor_n50_scale: float = DESCRIPTOR_N50_SCALE,
                           stage0_evals: int = STAGE0_MAX_EVALS,
                           stage0_offer_rate: float = STAGE0_OFFER_RATE,
                           arm_evals_total: int = N_ARMS * B_ARM,
                           n_checkpoints: int = len(REEVAL_AT),
                           archive_size_estimate: int = ARCHIVE_SIZE_ESTIMATE,
                           n_arms: int = N_ARMS, offer_rate: float = OFFER_RATE,
                           workers: int = WORKERS) -> dict:
    """Pure §5(b) projection arithmetic.

    `spread` is the number of per-stage standard deviations added to each
    measured mean before the arithmetic below (0.0 = optimistic, 1.0 =
    pessimistic — a conservative per-stage upper bound, NOT a rigorously
    propagated uncertainty interval).

    The Stage-0 term includes a guard cost (`stage0_offer_rate x guard`),
    mirroring the arms term's `offer_rate x guard` shape: in the real
    runner, `init_archives()` offers every valid Stage-0 genome to both
    archives, and with archives starting empty the would-enter (and hence
    guard-triggering) rate is high — but the runner's per-canon guard cache
    means the guard only runs ONCE per genome even though it's offered to
    both archives, so `stage0_offer_rate` is not doubled for two archives.
    """
    def s(stage: str) -> float:
        st = stage_stats[stage]
        return st["mean"] + spread * st["sd"]

    descriptor_n100 = s("descriptor_s")
    descriptor_n50 = descriptor_n100 * descriptor_n50_scale
    t1 = s("t1_s")
    guard = s("guard_s")
    full_conv = s("full_conv_s")

    stage0_work_s = stage0_evals * (descriptor_n100 + t1
                                    + stage0_offer_rate * guard)
    arms_work_s = arm_evals_total * (descriptor_n50 + t1 + offer_rate * guard)
    fullconv_work_s = n_checkpoints * n_arms * archive_size_estimate * full_conv
    total_work_s = stage0_work_s + arms_work_s + fullconv_work_s
    wall_s = total_work_s / workers
    return dict(
        spread=spread,
        descriptor_n100_s=descriptor_n100, descriptor_n50_s=descriptor_n50,
        t1_s=t1, guard_s=guard, full_conv_s=full_conv,
        stage0_work_s=stage0_work_s, arms_work_s=arms_work_s,
        fullconv_work_s=fullconv_work_s, total_work_s=total_work_s,
        wall_s=wall_s, wall_hours=wall_s / 3600.0,
    )


def build_verdict(stage_stats: dict, *, cap_hours: float = CAP_HOURS,
                  **projection_kwargs) -> dict:
    """optimistic (measured mean) + pessimistic (mean + 1 SD) projections;
    the verdict gates on the pessimistic one (conservative by design)."""
    optimistic = project_campaign_hours(stage_stats, spread=0.0,
                                        **projection_kwargs)
    pessimistic = project_campaign_hours(stage_stats, spread=1.0,
                                         **projection_kwargs)
    within_cap = pessimistic["wall_hours"] <= cap_hours
    return dict(
        projection_hours=dict(optimistic=optimistic["wall_hours"],
                              pessimistic=pessimistic["wall_hours"]),
        projection_detail=dict(optimistic=optimistic, pessimistic=pessimistic),
        cap_hours=cap_hours,
        within_cap=within_cap,
        rescope_required=not within_cap,
    )


# ---------------------------------------------------------------------------
# File contract (route_paths / build_state / render_md / finalize) — mirrors
# cal_i.py's belt-and-braces mode-gating pattern.
# ---------------------------------------------------------------------------

def route_paths(dry_run: bool) -> tuple[Path, Path]:
    return (DRYRUN_JSON, DRYRUN_MD) if dry_run else (OUT_JSON, OUT_MD)


def build_state(records: list[dict], draw_report: dict, *, elapsed: float,
                descriptor_n100: int, descriptor_n50_scale: float,
                t1_deep: int, t1_shallow: int, t1_n: int, guard_pairs: int,
                full_deep: int, full_shallow: int, full_n: int,
                dry_run: bool, from_cache: bool,
                failures: list[dict] | None = None) -> dict:
    failures = failures or []
    stage_stats = summarise_stage_timings(records)
    verdict = build_verdict(stage_stats, descriptor_n50_scale=descriptor_n50_scale)
    return dict(
        obligation="cal_c",
        dry_run=dry_run,
        from_cache=from_cache,
        failures=failures,
        n_failures=len(failures),
        protocol=dict(
            cal_seed_base=CAL_SEED_BASE, cal_seed_offset=CAL_SEED_OFFSET,
            n_genomes_target=(DRY_N_GENOMES if dry_run else N_GENOMES),
            n_genomes_measured=len(records),
            descriptor_n100=descriptor_n100,
            descriptor_n50_scale=descriptor_n50_scale,
            t1_deep=t1_deep, t1_shallow=t1_shallow, t1_n=t1_n,
            guard_pairs=guard_pairs,
            full_deep=full_deep, full_shallow=full_shallow, full_n=full_n,
            stage0_evals=STAGE0_MAX_EVALS, arm_evals_total=N_ARMS * B_ARM,
            n_checkpoints=len(REEVAL_AT), n_arms=N_ARMS,
            archive_size_estimate=ARCHIVE_SIZE_ESTIMATE, offer_rate=OFFER_RATE,
            stage0_offer_rate=STAGE0_OFFER_RATE,
            workers=WORKERS,
        ),
        draw_report=draw_report,
        records=records,
        stage_stats=stage_stats,
        **verdict,
        elapsed_s=round(elapsed, 1),
    )


def render_md(state: dict) -> str:
    p = state["protocol"]
    lines = [
        "# CAL-C — pre-campaign cost projection  [§5(b)]"
        + (" (DRY RUN — wiring check only, NOT a binding projection)"
           if state["dry_run"] else ""),
        "",
        f"RC2 §5(b) pre-campaign gate. {p['n_genomes_measured']} fresh CAL "
        f"genomes (seed base {p['cal_seed_base']} = GEN_SEED_BASE + "
        f"{p['cal_seed_offset']}) timed end-to-end through the FULL "
        f"per-genome pipeline (descriptor batch + T1 + guard stage + "
        f"full-conv re-eval), projected over the registered campaign shape "
        f"(Stage-0 {p['stage0_evals']} evals + {p['n_arms']} arms x "
        f"{p['arm_evals_total'] // p['n_arms']} + {p['n_checkpoints']} "
        f"full-conv checkpoints) across {p['workers']} workers vs the "
        f"{state['cap_hours']:.1f}h search-phase cap.",
        "",
        f"Draw: {state['draw_report']['attempts']} attempts -> "
        f"{state['draw_report']['accepted']} accepted"
        + (" (ATTEMPT CAP HIT)" if state["draw_report"]["attempt_cap_hit"]
           else "") + ".",
        "",
        f"Timed: {p['n_genomes_measured']} of "
        f"{p['n_genomes_measured'] + state['n_failures']} genomes attempted; "
        f"{state['n_failures']} failed.",
        "",
        "## Per-genome timings (s)\n",
        "| # | canon | family | descriptor | T1 | guard | full-conv | total |",
        "|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for i, r in enumerate(state["records"], 1):
        lines.append(
            f"| {i} | {r['canon'][:16]} | {r['family']} | "
            f"{r['descriptor_s']:.2f} | {r['t1_s']:.2f} | {r['guard_s']:.2f} "
            f"| {r['full_conv_s']:.2f} | {r['total_s']:.2f} |")
    lines += ["", "## Per-stage summary (s)\n",
             "| stage | mean | sd | n |", "|---|---:|---:|---:|"]
    for stage, st in state["stage_stats"].items():
        lines.append(f"| {stage} | {st['mean']:.3f} | {st['sd']:.3f} | "
                     f"{st['n']} |")
    lines += [
        "",
        "## Projection (§5(b) model)\n",
        "search_phase_work = [Stage0: stage0_evals x (descriptor_n100 + T1 "
        "+ stage0_offer_rate x guard)] + [arms: arm_evals_total x "
        "(descriptor_n50 + T1 + offer_rate x guard)] + [full-conv: "
        "n_checkpoints x n_arms x archive_size_estimate x full_conv]; "
        "wall = work / workers.",
        "",
        f"Assumptions (marked, not measured): offer_rate={p['offer_rate']} "
        "(share of arm evals triggering the guard stage — guard was timed "
        "for EVERY CAL genome per Task 9's dispatch, not gated on "
        "would-enter status, so this discounts it back down); "
        f"stage0_offer_rate={p['stage0_offer_rate']} (init_archives() "
        "offers every valid Stage-0 genome to BOTH archives; archives start "
        "empty so the would-enter rate is high, and the runner's per-canon "
        "guard cache means the guard runs ONCE per genome even though it's "
        "offered to both archives, so this is not doubled); "
        f"archive_size_estimate={p['archive_size_estimate']}/arm/checkpoint; "
        f"descriptor_n50 derived as descriptor_n100 x "
        f"{p['descriptor_n50_scale']} (= N_STAGE1/N_STAGE0, not "
        "hardcoded).",
        "",
        "| | optimistic (measured mean) | pessimistic (mean + 1 SD) |",
        "|---|---:|---:|",
        f"| projected wall | {state['projection_hours']['optimistic']:.2f}h "
        f"| {state['projection_hours']['pessimistic']:.2f}h |",
        "",
        f"Cap: {state['cap_hours']:.1f}h. Verdict gates on the PESSIMISTIC "
        "projection (mean + 1 SD per stage) — a pre-launch cost gate should "
        "not clear on the optimistic case alone.",
        "",
        f"## Verdict: **{'RE-SCOPE REQUIRED' if state['rescope_required'] else 'WITHIN CAP'}**",
        "",
        f"within_cap={state['within_cap']}, "
        f"rescope_required={state['rescope_required']}. Over-cap -> "
        "RE-SCOPE REQUIRED (re-registration of B, never a silent change; "
        "OWNER-level decision — the runner does not read this file, it "
        "only informs the launch decision).",
        "",
        ("(verdict re-derived from cached records; no genomes re-run)"
         if state["from_cache"] else ""),
        f"Wall time: {state['elapsed_s']}s. "
        f"{'DRY RUN — non-binding' if state['dry_run'] else 'COMPLETE'}",
        "",
    ]
    return "\n".join(lines)


def finalize(records: list[dict], draw_report: dict, *, elapsed: float,
            descriptor_n100: int, descriptor_n50_scale: float,
            t1_deep: int, t1_shallow: int, t1_n: int, guard_pairs: int,
            full_deep: int, full_shallow: int, full_n: int,
            dry_run: bool, from_cache: bool,
            failures: list[dict] | None = None) -> dict:
    state = build_state(records, draw_report, elapsed=elapsed,
                        descriptor_n100=descriptor_n100,
                        descriptor_n50_scale=descriptor_n50_scale,
                        t1_deep=t1_deep, t1_shallow=t1_shallow, t1_n=t1_n,
                        guard_pairs=guard_pairs, full_deep=full_deep,
                        full_shallow=full_shallow, full_n=full_n,
                        dry_run=dry_run, from_cache=from_cache,
                        failures=failures)
    out_json, out_md = route_paths(dry_run)
    out_json.write_text(json.dumps(state, indent=2))
    out_md.write_text(render_md(state))
    v = "RE-SCOPE REQUIRED" if state["rescope_required"] else "WITHIN CAP"
    ph = state["projection_hours"]
    print(f"\nVERDICT: {v} — optimistic {ph['optimistic']:.2f}h, "
         f"pessimistic {ph['pessimistic']:.2f}h vs cap "
         f"{state['cap_hours']:.1f}h", flush=True)
    print(f"wrote {out_json.name}, {out_md.name} in {state['elapsed_s']}s",
          flush=True)
    return state


def run_measurement(*, real: bool, from_cache: bool, workers: int) -> dict:
    dry_run = not real
    out_json, _ = route_paths(dry_run)

    if from_cache:
        cached = json.loads(out_json.read_text())
        p = cached["protocol"]
        return finalize(cached["records"], cached["draw_report"], elapsed=0.0,
                        descriptor_n100=p["descriptor_n100"],
                        descriptor_n50_scale=p["descriptor_n50_scale"],
                        t1_deep=p["t1_deep"], t1_shallow=p["t1_shallow"],
                        t1_n=p["t1_n"], guard_pairs=p["guard_pairs"],
                        full_deep=p["full_deep"], full_shallow=p["full_shallow"],
                        full_n=p["full_n"], dry_run=dry_run, from_cache=True,
                        failures=cached.get("failures", []))

    if dry_run:
        n_genomes, max_attempts = DRY_N_GENOMES, DRY_MAX_ATTEMPTS
        descriptor_n100 = DRY_DESCRIPTOR_N100
        t1_deep, t1_shallow, t1_n = DRY_T1_DEEP, DRY_T1_SHALLOW, DRY_T1_N
        guard_pairs = DRY_GUARD_PAIRS
        full_deep, full_shallow, full_n = (DRY_FULL_DEEP, DRY_FULL_SHALLOW,
                                           DRY_FULL_N)
    else:
        n_genomes, max_attempts = N_GENOMES, MAX_ATTEMPTS
        descriptor_n100 = DESCRIPTOR_N100
        t1_deep, t1_shallow, t1_n = T1_DEEP, T1_SHALLOW, T1_N
        guard_pairs = GUARD_PAIRS
        full_deep, full_shallow, full_n = FULL_DEEP, FULL_SHALLOW, FULL_N

    t0 = time.monotonic()
    # Minimal instantiation (Task 9's dispatch: "instantiate minimally"):
    # Campaign.__init__ touches no disk; smoke=False gives production
    # instrument shape (self.gen == GameGeneratorV2(GameConfig(), seed=0),
    # exactly the brief's genome source). Sims/n are passed explicitly per
    # call below, so only guard_pairs/workers need overriding for dry-run.
    campaign = Campaign(HERE, smoke=False)
    campaign.workers = workers
    campaign.guard_pairs = guard_pairs
    try:
        accepted, draw_report = draw_cal_genomes(
            campaign.gen, seed_base=CAL_SEED_BASE, n_target=n_genomes,
            max_attempts=max_attempts)
        print(f"  drew {len(accepted)}/{n_genomes} CAL genomes "
             f"({draw_report['attempts']} attempts)"
             + (" — ATTEMPT CAP HIT" if draw_report["attempt_cap_hit"]
                else ""), flush=True)
        records = []
        failures = []
        for i, (game, canon) in enumerate(accepted):
            try:
                r = time_genome(campaign, game, canon,
                                full_batch_index=9000 + i,
                                descriptor_n=descriptor_n100,
                                t1_deep=t1_deep, t1_shallow=t1_shallow,
                                t1_n=t1_n, full_deep=full_deep,
                                full_shallow=full_shallow, full_n=full_n)
            except (EvalTimeout, Exception) as exc:
                failures.append(dict(genome_index=i, canon=canon,
                                     error=repr(exc)))
                print(f"  [{i + 1}/{len(accepted)}] {canon[:16]} FAILED: "
                     f"{repr(exc)}", flush=True)
                continue
            records.append(r)
            print(f"  [{i + 1}/{len(accepted)}] {r['canon'][:16]} "
                 f"({r['family']}): descriptor {r['descriptor_s']:.1f}s, "
                 f"T1 {r['t1_s']:.1f}s, guard {r['guard_s']:.1f}s, "
                 f"full-conv {r['full_conv_s']:.1f}s, "
                 f"total {r['total_s']:.1f}s", flush=True)
    finally:
        campaign.shutdown()

    if not has_sufficient_sample(len(records), n_genomes):
        raise SystemExit(
            f"CAL-C: refusing to write a projection — insufficient sample "
            f"({len(records)} succeeded of {n_genomes} requested, "
            f"{len(failures)} failed; need >= "
            f"{min_successes_required(n_genomes)} successes). Re-run "
            f"--{'dry-run' if dry_run else 'real'}.")

    return finalize(records, draw_report, elapsed=time.monotonic() - t0,
                    descriptor_n100=descriptor_n100,
                    descriptor_n50_scale=DESCRIPTOR_N50_SCALE,
                    t1_deep=t1_deep, t1_shallow=t1_shallow, t1_n=t1_n,
                    guard_pairs=guard_pairs, full_deep=full_deep,
                    full_shallow=full_shallow, full_n=full_n,
                    dry_run=dry_run, from_cache=False, failures=failures)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--real", action="store_true",
                      help="Run the REAL CAL-C measurement (~20 fresh "
                           "genomes through the FULL pipeline at production "
                           "sims/n, owner-gated real spend — expect tens of "
                           "minutes). Writes cal_c.json.")
    mode.add_argument("--dry-run", action="store_true",
                      help="Tiny wiring check (3 genomes, sims 32v8, T1 "
                           "n=8, guard n_pairs=4, full-conv 64v8 n=8). "
                           "Writes cal_c_dryrun.json — NEVER cal_c.json.")
    parser.add_argument("--from-cache", action="store_true",
                        help="Re-derive the projection + MD from the "
                             "existing JSON for the selected mode; no "
                             "genomes re-run.")
    parser.add_argument("--workers", type=int, default=WORKERS)
    args = parser.parse_args(argv)

    if not args.real and not args.dry_run:
        print(
            "CAL-C: refusing to run without an explicit mode.\n"
            "This is the prereg §5(b) pre-campaign cost-projection gate — "
            "real spend is owner-gated (a run writes cal_c.json, which "
            "records whether the projected campaign wall clears the 8h "
            "cap).\n"
            "  Wiring check (tiny, non-binding): --dry-run\n"
            "  Real measurement (~20 fresh genomes, owner-gated, expect "
            "tens of minutes): --real",
            flush=True)
        return

    run_measurement(real=args.real, from_cache=args.from_cache,
                    workers=args.workers)


if __name__ == "__main__":
    main()
