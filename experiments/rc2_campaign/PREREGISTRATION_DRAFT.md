# RC2 Campaign — PREREGISTRATION (DRAFT — NOT LOCKED)

Status: **DRAFT for ultracode panel review.** This document locks (renamed
PREREGISTRATION.md, committed pre-data) only after panel grafts are applied.
Design authority: `docs/superpowers/specs/2026-06-12-rc2-campaign-design.md`
(owner decisions recorded there). Lineage: Phase C ARCHIVE_GO machinery
(`experiments/rc2_archive/`, locked `986ef53`/R2), planning-gap validations
(`experiments/rc2_planning_gap/`), guards (`rc2_descriptor_v2` RUSH/TILT,
`reach_endcause` REACH-v3).

## 1. Question

Does PG-driven QD search produce games that escape the 3.5–4.0 agent-eval
plateau? One variable changes from ARCHIVE_GO: quality = planning-gap, not
drama.

## 2. Search space and arms

- GameGeneratorV2 DEFAULT GameConfig, MutationOperatorV2 DEFAULT
  EvolutionConfig (Phase C verbatim), strict quick_reject everywhere, PLUS
  one registered exclusion: genomes with simultaneous moves are
  quick-rejected (UCT instrument constraint; ~30% of generator space;
  counted and reported).
- Arms: R = fresh generator genomes; M = uniform-random filled cell → mutate
  elite once → pre-filter → evaluate → offer. **B = 600 evaluated genomes
  per arm** (owner decision; the validated replicate scale).
- Seed streams (fresh, never used by any recorded probe): Stage-0/CAL
  generation seed base 17_000_000; arm R 34_000_000; arm M mutation rng
  51_000_000; arm M cell-selection rng 68_000_000. Eval seeds
  content-derived per the Phase C formula:
  eval_seed = (int(canonical_hash()[:16], 16) + 7919 × batch_index) mod 2^31.
- Per-eval wall timeout 180 s → EVAL_TIMEOUT; engine exception → EVAL_ERROR;
  both consume the budget slot, are excluded from archives/bars, counted.

## 3. Quality signal

- **Screening (every genome): T1-PG** = seat-balanced score of net-free
  UCT@128 vs UCT@16 − 0.5; n=24 (12 per stream, 2 streams per genome derived
  from the eval seed), draws 0.5, max_steps=400, anchor_calibration.py
  conventions. Per-game noise σ ≈ 0.07 at n=24 (cost_tiering per-stream).
- **Quality for insertion/QD = max(PG, 0)** (informative-region rule; raw
  PG always recorded). Insertion requires STRICT improvement on floored PG;
  a 0-vs-0 challenger never displaces (coverage still counts first
  occupancy).
- **Elite re-evals: full-convention PG** (UCT@256 vs UCT@16, n=48) at eval
  counts 200/400/600 per arm (Phase C checkpoints ×2), with challenger
  eval-count matching inherited from Phase C.

## 4. Insertion guards (veto on archive entry; never deletion of incumbents)

- RUSH: ≥ 25% of decisive tactical rollouts end in ≤ 6 plies
  (descriptor-rollout records; descriptor-v2 validated constant).
- TILT: P1 wins ≥ 80% of decisive tactical rollouts (mirrored pairs; same
  source).
- REACH-v3 (threshold family only): ≥ 25% of the genome's own T1 games end
  with winner None (validated on fresh streams 44/45; zero extra cost).
- Guard-vetoed genomes are counted and logged with which guard fired.

## 5. Pre-campaign CAL (before any search spend)

- CAL-I (instrument): T1-PG on fresh streams (46, 47) must give
  PG(d4015a646ae3) − PG(S4) ≥ **0.30** (= 3× σ_diff, where σ_diff =
  σ(T1,n=24)·√2 ≈ 0.10 for a difference of two measurements; observed
  separation 0.834 at streams 42/43). Fail → **PROBE_INVALID**, no campaign.
- CAL-C (cost): 20 fresh genomes (CAL seed stream) timed end-to-end through
  the full per-genome pipeline → projected campaign wall. If projection
  exceeds the cap, the campaign is re-scoped BEFORE launch (re-registration
  of B, not a silent change).

## 6. Bars (binding; constants final at lock)

- **BAR W-PG** (within-family validity): in every family with ≥ 20 valid
  evaluated genomes, P90 − P10 of T1-PG ≥ **0.21** (3 × σ(T1, n=24) ≈
  3 × 0.07). Fail in any sampled family → **ARCHIVE_KILL** (descriptor/
  signal interaction redesign precedes any campaign).
- **BAR H-PG** (search value): mean floored full-conv PG of the top-10
  elites per arm (global across cells, post-final-re-eval pooled),
  top10(M) − top10(R) ≥ **0.05**. Either archive < 10 elites → not
  evaluable → PROBE_INCOMPLETE.
- **Slate trigger**: slate runs only on BAR W-PG pass ∧ BAR H-PG pass.
  BAR H-PG fail → **SEARCH_NEUTRAL**; registered next step: parent-child
  T1-PG heritability r from the M-log (no new compute); r ≥ 0.3 → one
  2×-budget replicate is registered, launched on owner confirmation;
  r < 0.3 → mutation/signal interaction analysis precedes any replicate.
- **SLATE bars** (3 independent blind tmux teams, 21 verdicts):
  - S-GO-1: ≥ 1 M-elite blind team mean ≥ **4.10** (R8-parity, owner
    decision).
  - S-GO-2 (PG validation, graft-10 binary separation): pooled team mean of
    the top-2-by-full-PG slate elites exceeds the bottom-2-by-full-PG by
    ≥ **+0.5**.
  - GO requires BOTH; either fails → **NO-GO** (PG returns to analysis
    with which/why; periodic-agent-slates-only becomes the registered
    selection fallback).
  - Campaign validity: in-slate d4015 team mean within **[3.48, 4.18]**
    (3.83 ± 0.35); outside → **CAMPAIGN_UNRESOLVED** → one cheap 2-team
    replicate slate; never permanent closure (z_flip_r2 graft).
- **PROBE_INCOMPLETE**: wall cap **8 h** hit; either archive < 10 elites;
  < 2 families sampled; anchor games unloadable.

## 7. Slate composition and blinding

Top-5 M-arm elites by full-convention PG, cross-cell (max 1 per cell;
next-best cell substitutes on collision), + d4015a646ae3 (validity anchor)
+ S3 (registered carry-in; reported, not binding — the open
PG-vs-agent-depth question from the blind-seven validation). Blind-packed
per evaluations/stage3_ab convention; teams see no provenance, scores, or
signal values.

## 8. Reported, not binding

Per-arm coverage and QD-score (sum of floored elite PG), per-cell paired
wins, family composition of top-10s, guard-veto counts by guard,
simultaneous-quick-reject count, raw (unfloored) PG distributions,
re-eval re-pricing magnitudes, heritability r, S3 slate read, all counters.

## 9. Verdict consequences

- **GO** → register loop integration at run.py:593 scores_map.
- **NO-GO** (valid instrument) → PG to analysis; agent-slates-only fallback.
- ARCHIVE_KILL / SEARCH_NEUTRAL / CAMPAIGN_UNRESOLVED / PROBE_INCOMPLETE /
  PROBE_INVALID per §5–6. No archive re-registration (house grammar).

## 10. Build and audit obligations

Runner applies bars via a pure `decide_verdict` with all branches
synthetically tested pre-run; bars transcribed as constants; prereg locked
pre-data; any post-lock code change must be pre-data and review-logged
(Phase C audit pattern). Checkpointing + unbuffered logs (Phase C
run-integrity disclosure applied as a requirement).

## DRAFT marks for the panel

Constants the panel should attack hardest: CAL-I floor 0.30; BAR W-PG floor
0.21 and its ≥20-genome family threshold; BAR H-PG floor 0.05 (top-10 mean
difference σ ≈ 0.032 under measured T1 noise — is 1.5σ enough?); S-GO-2
margin +0.5; d4015 band ±0.35; the 8 h cap vs CAL-C projection; whether
flooring at 0 creates an insertion pathology (0-PG carpets occupying cells
that guards should have vetoed); whether T1 n=24 screening lets noisy
near-zero genomes churn elites (strict-improvement + eval-count matching is
the intended brake); REACH-v3 scoped threshold-only (draw-prone
non-threshold genomes have no draw guard).
