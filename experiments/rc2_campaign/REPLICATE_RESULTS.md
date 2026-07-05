# RC2 campaign — 2-team replicate slate results (§6 registered consequence)

2026-07-05 evening. The registered consequence of the first
CAMPAIGN_UNRESOLVED (`SLATE_RESULTS.md`): one cheap 2-team replicate,
**instrument deliberately unchanged** so the replicate distinguishes
noise-breach from systematic cohort drift (decision tree pre-registered in
the lab notebook 17:15 record, before any replicate verdict existed).
Fresh pack `evaluations/rc2_replicate_blind` (new label seed 917204,
disclosed post-unblind; new pack dir because the original now contains
filed verdicts). Same blind mitigations (aigame project memory parked +
probe-verified + restored; pack-dir cwd; content-free prompts). 14
verdicts + 2 cross-game notes; DONE markers before unblind.

## Pre-unblind grep — 8 hits, all BENIGN

All 8 are `[R8]` scoring-anchor citations (briefing-mandated anchor
vocabulary). All 14 recognition-disclosure lines: "none" or generic
prior-art (Gonnect, Othello, Go-family, Hex/carpet) with explicit denial
of specific-game recognition and prior-score recall.

## Unblinded scores (Overall 1–10, 2 teams; mean)

| label | role | id | t1 | t2 | mean | (main-slate mean) |
|---|---|---|---:|---:|---:|---:|
| D | contrast | b461c5160c5e | 4.2 | 4.5 | **4.350** | 4.067 |
| G | **validity anchor** | d4015a646ae3 | 4.3 | 4.3 | **4.300** | 4.300 |
| C | **top** | 627eb70b77ed | 4.4 | 3.9 | 4.150 | 4.433 |
| B | contrast | 1c55e13164ae | 4.0 | 4.2 | 4.100 | 3.667 |
| F | **top** | 8f1f95ef38f6 | 4.1 | 4.1 | 4.100 | 4.067 |
| E | carry-in | S3 | 4.2 | 3.6 | 3.900 | 4.167 |
| A | **top** | 764ad3ae50ec | 4.3 | 3.3 | 3.800 | 3.850 |

## Bars → token

- d4015 = **4.300, OUTSIDE [3.48, 4.18] — again, at the identical value.**
- S-GO-1 TRUE (627eb 4.15, 8f1f 4.10); S-GO-2 sep **−0.208** (contrast
  pool beat the top pool); SEPARATION_UNDERDETERMINED (min-contrast gap
  0.0521 as before).
- **FINAL §9 TOKEN (replicate): `CAMPAIGN_UNRESOLVED` — second occurrence.**

The §6 chain is now exhausted (the one registered replicate has run).
Registered state of the campaign: CAMPAIGN_UNRESOLVED ×2, "never permanent
closure" — any continuation requires new registration.

## Hypothesis scorecard (vs the 17:15 pre-registered record)

**H-drift CONFIRMED, H-noise rejected**: five independent team-reads of
the anchor across two slates — 4.2, 4.2, 4.5, 4.3, 4.3 (pooled 4.32,
spread 0.3) vs band center 3.83. The cohort scores d4015 ≈ **+0.5 above
the band-calibration cohorts**, with high consistency. The replicate
answered exactly the question it was registered to answer.

## The finding that matters (non-binding, pooled across both slates, n=5/game)

- Top elite 627eb70b77ed pooled 4.32 — **exactly anchor parity** (4.32).
- Top pool ≈ 4.08 vs contrast pool ≈ 4.01 — **top-vs-contrast blind
  separation is flat** (and negative within the replicate alone). The
  archive's full-conv distinction (0.5000 vs 0.4479) does not reproduce
  in blind judgment — consistent with the pre-disclosed
  SEPARATION_UNDERDETERMINED: a 0.05 PG gap was never expected to be
  visible at this n.
- Under the two candidate future instruments the existing data reads
  oppositely — re-anchored absolute band (≈[3.95, 4.65], S-GO-1 4.10)
  → GO-PARTIAL; anchor-relative R8-parity (anchor + 0.27 ≈ 4.59) →
  NO-GO. **Choosing between them retroactively would be choosing the
  verdict; neither is applied here.** The registered token stands.

## Honest synthesis

The search found games that blind agent teams judge at **parity with a
blind-preferred control** (d4015) — real, but short of the campaign's
R8-parity-plus GO ambition once cohort drift is accounted for. Meanwhile
both the top-10 gap metric AND the blind slate agree the full-conv
instrument is out of top-end resolution (seven elites pinned at 0.5000;
flat blind separation). The binding constraint on this program is now
**instrument headroom, not search or selection**: PREREGISTRATION_BARH_V2
§5/§6.4 already flags the fix (harder opponent gap for full-conv ⇒ new
CAL-I; 25%-at-cap saturation rule). Recommended next registration, owner-
gated: instrument-headroom work FIRST; any future slate registers
anchor-relative bars pre-data (offset R8−d4015 = +0.27 on the historical
scale), never absolute anchors across evaluator generations.

## Role win split (reported, not binding; line-1 results)

A 1-1-0 · B 2-0-0 · C 1-1-0 · D 0-1-1 · E 2-0-0 · F 1-1-0 · G 2-0-0.
No 80/20 flag at the captured sample sizes.
