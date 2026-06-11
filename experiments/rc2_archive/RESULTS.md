# RC2 Phase C archive-integration probe — readout

## FINAL: **ARCHIVE_GO** (run 1 ARCHIVE_NEUTRAL → registered 2× replicate → R2 ARCHIVE_GO per the locked R2 grammar)

---

# Run 1 (base_seed 13, B=300/arm)

**Decision criteria:** pre-registered in `PREREGISTRATION.md` (locked `986ef53`, before any
probe data; review-driven runner fixes `d288095` all pre-data). Bars applied verbatim by
`run_probe.py`; all five verdict branches synthetically tested before the run. Full run:
CAL n=100 + Stage 0 (160 genomes @ n=100) + two arms (B=300 @ n=50 each, re-eval at
100/200/300), base_seed 13, 10.5 min wall, zero PPO.

## Verdict: **ARCHIVE_NEUTRAL — and the registered heritability trigger FIRES the 2×-budget replicate (r = 0.344 ≥ 0.3)**

| bar | result | detail |
|---|---|---|
| CAL (instrument) | **PASS** | drama(573) − drama(e1453) = 0.2408 ≥ 0.15; values (0.306/0.065 at n=100) consistent with Phase B's n=200 (0.304/0.048) |
| BAR W (within-family) | **PASS** | 3 of 3 sampled families LIVE: territory 0.0943, connection 0.0868, threshold 0.0734 (floor 0.064); elimination UNSAMPLED (0 valid of 20) |
| BAR H (search value) | **FAIL** | top10(M) − top10(R) = 0.0194 < 0.03 floor |

## Headline numbers

- **The Phase B family-confound caveat is resolved for every sampleable family.** On 99
  valid fresh genomes, obs_drama's within-family P90−P10 spread exceeds 3× measurement
  noise in all three sampled families. Drama is not a family detector.
- **Every reported-not-binding Stage-1 signal favors the archive arm:** QD-score 5.469 vs
  4.221 (+30%), coverage 39 vs 32 cells, per-cell record on the 30 jointly filled cells
  20 wins / 3 same-elite ties / 7 losses, top elite 0.248 vs stage-0 max ≈ 0.21-class.
  The single BINDING metric — top-10 mean — missed its floor at +0.0194.
- **Why the binding metric saturated:** both arms' top-10 are 100% territory-family. The
  archive's top end sits against the territory drama ceiling, so top-10 mean compresses
  exactly where the two arms compete hardest; M's gains live in breadth (coverage, QD,
  per-cell wins), which BAR H was registered not to count. Declared as a metric
  limitation, not re-litigated: the token is NEUTRAL.
- **Drama is heritable under MutationOperatorV2:** parent-child r = 0.344 over 279
  evaluated pairs — above the registered 0.3 trigger, so the pre-registered next step is
  one 2×-budget replicate (not a redesign).
- **The noise machinery worked as designed:** 200 elite re-evals re-priced by mean 0.006
  (max 0.055 ≈ 1.8× hw(50)); no phantom regime; arm M survived all three re-evals with
  its QD intact (5.469 final, post-re-eval) — its lead is not challenger luck.

## Honest synthesis

1. **New generator finding: the elimination family is rollout-degenerate as generated.**
   All 20 elimination genomes evaluated in Stage 0 were invalid — 19 ended with mean
   game_length < 6 plies (elimination under random/greedy play ends almost immediately),
   1 was draw-majority. This is a quick_reject gap (structural checks pass; play is
   trivial) and the reason elimination is UNSAMPLED in BAR W. Logged for generator work;
   not a Phase C blocker.
2. **Stage-0 attrition was material and is fully counted:** 265 attempts → 105
   quick-rejects → 160 evaluated → 99 valid (42 draw-majority, 19 too-short). The
   validity guard is doing real work; archive integration inherits it for free.
3. **BAR H's verdict is honest but blunt at this budget.** M overtook R's *final* QD by
   eval 100 of 300 and won 74% of contested cells, yet NEUTRAL is correct under the
   locked floor. The 2× replicate (registered, fresh seeds, B=600) directly tests
   whether the top-10 gap reopens once mutation has budget to push past the territory
   ceiling — or whether top-K-on-drama is the wrong binding metric for archive value,
   which would be a Phase D design input, not a rules change now.
4. **Cost model was off 25×: the probe took 10.5 minutes, not ~4-5h.** Fresh generator
   genomes (≤64 cells) roll out far faster than the anchor games the estimate was
   calibrated on. Consequence: the 2× replicate is ~25 min, and budget is not a
   constraint for Phase D scoping.
5. **Run-integrity disclosure:** the first launch was killed ~3 min in (stdout
   buffering hid the log; no results were read) and relaunched unbuffered from scratch
   with identical registered seeds. Content-derived eval seeding makes the rerun
   bit-identical; checkpoint files were cleared before relaunch.

## Pre-registration audit

- PREREGISTRATION locked at `986ef53` before any probe data; the only post-lock code
  changes were the pre-run review fixes (`d288095`): removal of an UNREGISTERED stall
  guard (could have emitted PROBE_INCOMPLETE on runs the contract says must continue),
  wall-cap recheck at verdict, terminal checkpoint marker. Nothing changed after data.
- Bars transcribed as constants and applied by `decide_verdict` (pure function; all five
  branches synthetically tested in `test_rc2_archive.py`, 34 tests green pre-run).
- Reviewer (independent pass, pre-run) verified line-by-line prereg transcription,
  determinism (content-derived seeds; no wall-clock/scheduling dependence), checkpoint
  completeness, and arm fairness (identical init, identical mechanics, shared elites get
  identical content-seeded re-eval batches in both arms).
- Smoke ran on registered-disjoint seed streams (+777k offsets); its values informed no
  bar.

## Registered next (per the locked ARCHIVE_NEUTRAL branch)

Heritability r = 0.344 ≥ 0.3 → **one 2×-budget replicate**: fresh seed streams, B = 600
per arm, otherwise mechanics, bars, floors, and grammar unchanged. Pre-registered as
`PREREGISTRATION_R2.md` (locked `7cb818f`) before the replicate ran.

---

# R2 replicate (base_seed 17, B=600/arm, locked `PREREGISTRATION_R2.md`)

Run: fresh CAL + fresh Stage 0 + both arms at B=600, 24.7 min wall, zero PPO. Full
tables: `replicate2x/probe_results.md`.

## R2 verdict: **ARCHIVE_GO**

| bar | result | detail |
|---|---|---|
| CAL | **PASS** | gap 0.2408 — bit-identical to run 1 (content-derived seeds; deterministic by design) |
| BAR W | **PASS** | 2 of 3 sampled LIVE: territory 0.1494, connection 0.0739; threshold DEAD at 0.0560 (was 0.0734 in run 1) |
| BAR H | **PASS** | top10(M) − top10(R) = **0.0574 ≥ 0.03** (top10 M 0.2905 [0.2807, 0.3004] vs R 0.2331 [0.2243, 0.2422] — CIs do not touch) |

## R2 headline numbers

- **The run-1 saturation hypothesis was confirmed, not patched.** At 2× budget arm M's
  top-10 broke out of the all-territory ceiling into a family-diverse set (5 territory /
  4 connection / 1 threshold) while arm R's stayed 9/10 territory — the top-10 gap
  reopened exactly as run 1's honest synthesis predicted, under unchanged metrics.
- **Every secondary signal widened at 2×:** QD-score 7.028 vs 4.682 (+50%, was +30%),
  coverage 42 vs 31 (was 39 vs 32), jointly-filled record 20W/4T/6L, heritability
  r = 0.444 over 533 pairs (was 0.344/279).
- **Noise machinery stayed clean at double the exposure:** 390 elite re-evals, mean
  re-pricing ≈ 0.005, max 0.045 — no phantom regime; M's lead survives 6 full-archive
  re-evals.
- **Replication notes, stated:** threshold's within-family liveness did NOT replicate
  (0.0734 → 0.0560 around the 0.064 floor) — drama's within-family signal is robust for
  territory/connection and marginal for threshold; and elimination was again 0-valid
  (rollout-degenerate as generated) — both are Phase D / generator-work inputs.

## Phase C conclusion (per the locked R2 grammar)

**ARCHIVE_GO.** A training-free MAP-Elites archive (obs_drama quality; family ×
interaction × length cells; eval-count matching + periodic full-archive re-eval) adds
real search value over random generation at matched budget, and drama is heritable under
the existing mutation operators. Registered next:

1. **Phase D — cross-cell blind-slate agent-team eval** of arm M's top elites (the
   expensive validation stage deferred from the panel's MAP-Elites seats): do
   archive-discovered high-drama games clear agent judgment where GE-evolved games
   plateaued? Pre-register before building; R2's `replicate2x/probe_results.csv` is the
   elite source.
2. **Loop-integration spec** at `run.py:593` (scores_map swap point) — drafted only
   alongside Phase D, gated on its outcome.
3. Generator-work inputs logged: elimination rollout-degeneracy (quick_reject gap);
   threshold within-family marginality.
