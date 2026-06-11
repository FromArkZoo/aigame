# RC2 anchor probe — readout

**Decision criteria:** pre-registered in `PREREGISTRATION.md` (locked `65b3292`; pre-data amendments `d5852eb`, `7c91381`, `3e3a800` — all committed before any probe data). None altered after data. Probe run: n=200, seed 11, all 10 anchors, zero PPO, ~9 min wall.

## Decision: **PHASE_C_GO — observer-based drama separates agent-judged quality pods where GE cannot; the archive-integration probe is registered as next**

All three observer candidates passed all four bars; the two registered primaries passed with **zero fragile bars (100% of 1000 bootstrap resamples)**. The GE control column failed, as registered.

| candidate | bar 1 (pods) | bar 2 (inversions) | bar 3 (e1453) | bar 4 (573>e1453) | verdict |
|---|---|---|---|---|---|
| obs_drama (primary) | 0.1281 vs 0.0442 ✓ | 0 ✓ | 0.048 < 0.124 ✓ | 0.304 > 0.048 ✓ | **PASS** (all 100%) |
| blend | 0.5484 vs 0.0044 ✓ | 0 ✓ | 0.000 < 0.499 ✓ | 1.000 > 0.000 ✓ | **PASS** (all 100%) |
| interaction_rate | 0.1781 vs 0.0947 ✓ | 1 (≤1) ✓ | ✓ | ✓ | PASS (weakest margin 99.5%) |
| go_essence (control) | not evaluable | not evaluable | not evaluable | 0.0027 > 0.181 ✗ | **FAIL** (as registered) |

## Headline numbers

- **The pods do not touch.** ABOVE drama 0.1236–0.1322 vs BELOW 0.0423–0.0480 — ~3× separation, non-overlapping 95% CIs on every pairing, zero boundary inversions.
- **The GE-inversion pair separates 6.3×:** 573 (agents tied-1st, GE 0.003) scores 0.304 — the highest drama in the entire anchor set; e1453 (the R21 GE-favorite agents ranked 6/7) scores 0.048, near-bottom. The observer signal ranks them exactly as the agents did and exactly opposite to GE.
- **Cross-harness reproducibility:** a1's drama here (0.1322) matches the SIEGE Stage-1.5 anchor harness value (0.1324) to 3 decimals — two independently built pipelines (engine-field-based vs observer-field-based, different rollout code paths) agree on a field_connection game whose params equal the observer defaults. s_flip_r2 lands at 0.1284, consistent with its blind +0.2 preference over a1 being small.
- **The three ABOVE games cluster tightly** (0.124–0.132) across three different rule families (legacy connection+surround, field+flip, field+surround) — the signal tracks the judged quality, not the family.

## Honest synthesis

1. **The registered question is answered cleanly.** A training-free signal computable for EVERY genome (the observer field removes the prop_type='none' descriptor blackout) reproduces the agent-team quality ordering on all 10 games with verdicts. This was the blocker that killed both QD pivot candidates at the panel screen; it is now removed with evidence.
2. **interaction_rate also passing means drama is not just contact in disguise — but contact alone nearly suffices.** The cheap-skeptic column passed with 1 permitted inversion (1fea above a1). Drama's margins are categorically stronger (100% vs 99.5% worst-bar robustness, 0 vs 1 inversions). Phase C should carry interaction_rate as an archive AXIS (diversity descriptor), drama as the QUALITY signal — exactly the MAP-Elites division of labor.
3. **Known anchor-set weaknesses, stated:** the BELOW pod is all-threshold and contains near-twin genomes (e52e/bfd1 differ only in max_turns; identical columns to 4 d.p.), so the effective BELOW pod is ~3 distinct games; the ABOVE pod is only 3 games, one of which (a1, 3.90) sits at the validity boundary. The pods also differ by family (ABOVE has no threshold game), so family is a confound for this anchor set — drama within-family separation IS demonstrated on the BUFFER (573 at 0.304 vs d995/b12f at 0.082/0.086, all non-ABOVE-family games), which mitigates but does not eliminate it. Phase C's bars should include a within-family separation check on a broader genome sample.
4. **GE provenance discrepancy recorded:** the DB scores (registered column source) differ materially from the 20-seed slate means quoted in the pod table (e.g. 1fea 0.211 vs 0.118); under the DB source e1453 is the lowest GE of the BELOW pod. Bar outcomes are identical under either set (verified); the control column's failure is robust to the choice.
5. **Ghost-influence caveat held in practice:** threshold-progress traces measure current-stone influence (observer recompute), diverging from the engine's ghost-influence accumulation only on capture events (~0.035 max per-rollout drama delta observed pre-registration on e1453). Registered pre-data; no bar was within an order of magnitude of being sensitive to it.

## Pre-registration audit

- PREREGISTRATION locked before any data; four pre-data amendments (PROBE_INCOMPLETE clause, dual observer parameterization, ghost-influence honesty, pod pinning) all committed before the n=200 run; nothing altered after.
- Bars applied verbatim by `run_probe.py` (bar-transcription table verified line-by-line in review; all four verdict branches synthetically tested before the run; GE control structurally unable to pass via unevaluable bars).
- Protocol: anchor_drama's exact seeding scheme (cross-harness comparability proven by the a1 3-decimal match); family-drift guards passed on all 10 loads; R8 loaded from genesis_v2_run8.db (no fallback needed).
- Cost: build ~3.5 h wall (5 tasks, two-stage review each) + probe 9 min. Zero PPO, zero training.

## Registered next (per the locked grammar)

**Phase C — archive-integration probe:** MAP-Elites archive over the generator's genome space with obs_drama as the quality signal (GE diagnostic-only), interaction_rate + game_length as candidate axes; inherits from the panel's MAP-Elites seats: challenger eval-count matching, cross-cell blind slates, periodic full-archive re-eval. Pre-register before building: within-family separation bar on a fresh genome sample; honest-noise sample sizes from this probe's CIs (drama CI half-width ≈ ±0.015 at n=200). Inputs-not-commitments: the hex_rhombus win-graph fix; the Frontline rebuild remains registered in parallel (SIEGE RESULTS §7).
