# RC2 descriptor-v2 probe — readout

**Decision criteria:** PREREGISTRATION.md locked `42f8403`; build committed `0633c4e`
pre-data (73 tests green incl. all verdict branches). Full run: 15 games × 100
tactical-vs-tactical mirrored rollouts, 72 min wall, zero PPO. Bars applied verbatim
(probe_results.md).

## Verdict: **DESCRIPTOR_V2_KILL** (G-REACH failed; V2-RANK also failed)

| bar | result | operative numbers |
|---|---|---|
| G-RUSH | **PASS** | fires on S1 (1.00 of decisive wins in ≤6 plies; mean 4.0); silent on all four protected anchors |
| G-REACH | **FAIL** | S2 is 100% decisive under tactical play (35.5 mean plies) — the guard never fires |
| G-TILT | **PASS** | fires on S4 and S5 (P1 share exactly 0.80); silent on s_flip_r2/a1 (0.22) |
| V2-RANK | **FAIL** | guarded elites S1/S4/S5 (0.146/0.312/0.312) and guard-clean S2/S3 (0.372/0.327) ALL outrank both controls (d4015 0.108, e1453 0.032) |
| V2-NONREG | **PASS** | all four Phase B pod bars reproduce under drama_v2 (ABOVE 0.117 vs BELOW 0.036; 0 inversions; 573 0.216 > e1453 0.032) |

Spearman(drama_v2, blind mean) over the Phase D seven: **−0.31** (random-rollout drama
was −0.68 on the same games — better policy, still inverted).

## Honest synthesis

1. **Two of three guards are validated and adopted-able.** RUSH and TILT fire exactly on
   the elites that motivated them, at clean margins, and spare every protected anchor.
   These survive this KILL as standalone instruments.
2. **REACH's operationalization missed the mechanism.** S2 ends decisively under
   tactical play (custodian-capture dynamics produce winners without threshold-crossing
   saturation), so "decisive before max_turns" does not capture what the blind teams
   experienced ("threshold 36.9 unreachable; peaks ~+10; draw-prone"). The guard needs an
   end-CAUSE condition (decided BY the win condition vs by attrition/timeout), not an
   end-RATE condition.
3. **The core negative result: winner-behindness is range-valid but not a maximand —
   under ANY trace policy tried.** Tactical-play drama reproduces the Phase B pod
   separation perfectly (V2-NONREG, second independent confirmation of Phase B) yet
   still ranks every Goodharted elite above both controls. The mechanism is structural:
   winner-behindness rewards CLOSENESS, and the degenerate games are maximally close by
   construction (28–27 parity races; capture see-saws). Close ≠ deep, and no rollout
   policy fixes that, because the signal definition itself is the problem above the
   anchor range.
4. **Cumulative RC2 picture:** GE failed as a maximand (R19–R21); random-rollout drama
   failed as a maximand (Phase D); competent-trace drama failed as a maximand (here);
   drama remains an excellent within-range DISCRIMINATOR (Phase B, twice). The next
   quality signal must either measure something closeness cannot fake (e.g.,
   planning-gap: score delta between deep and shallow search on the same position
   set; learnability curves) or use agent judgment directly in the loop at low
   frequency (cross-cell slates as periodic ground truth, drama only as a cheap
   band-pass between slates).

## Registered next (per the locked KILL branch + accumulated evidence)

Per the grammar, no archive re-registration. The KILL branch requires the failed designs
to return to analysis with a report of which and why (above). For any successor
registration, this probe binds three inputs: (a) RUSH + TILT as insertion guards
(validated here); (b) REACH redesigned on end-cause; (c) the quality signal must be
demonstrated on a closeness-confound pair (S4/S5 vs d4015) BEFORE any search spend —
a 15-minute calibration that this probe makes mechanical. The Frontline rebuild remains
the registered parallel thread.
