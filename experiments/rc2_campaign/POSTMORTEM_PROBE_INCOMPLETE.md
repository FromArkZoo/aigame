# RC2 campaign — PROBE_INCOMPLETE post-mortem

Status: ANALYSIS (2026-07-05). No new simulations were run; every number below is
recomputed from the concluded run's artifacts (`checkpoint.json`,
`checkpoint_archives` at 150/300, `arm_{R,M}_log.csv`, `campaign_results.md`)
or quoted from locked prior documents. Companion re-registration draft:
`PREREGISTRATION_BARH_V2.md` (owner ratification pending).

## 1. What happened

The campaign (erratum #14-S2 shape: B=300/arm, re-eval at 150/300, 36 h cap)
ran to completion in 1141.1 min (~19.0 h) with zero salvage events. The chain:

- CAL-I: PASS (+0.750 vs bar 0.431).
- BAR W-PG: PASS 3/3 LIVE (territory, connection, threshold; elimination UNSAMPLED).
- BAR H-PG: saturation contingency fired — R_top10 = 0.4823 ≥ 0.40 — switching
  the binding metric to paired per-cell wins (§6, C7). That metric requires
  ≥ 20 jointly filled cells; the final archives had **15**.
  `bars.decide_verdict` → **PROBE_INCOMPLETE** (bars.py:40-42). Correct per the
  locked prereg; the token is not disputed.

Final state: R coverage 17, QD 7.604, top-10 full-conv 0.4823 [0.4745, 0.4901];
M coverage 26, QD 11.458, top-10 0.4974 [0.4948, 0.4995]. Joint 15: M strict 7,
R strict 2, same-canon ties 5, equal-value distinct 1.

## 2. Proximate cause

Joint-cell feasibility is bounded above by min-arm coverage. R's archive
plateaued at 17 cells; 20 joint cells were therefore unreachable regardless of
M's behaviour. The arm logs sharpen this: R filled new cells at evals **11,
168, 187 only** (init 14 → 17) — zero fills in its final 113 evals. M filled
12 (last at eval 224; init 14 → 26).

## 3. Root causes, ranked

**RC1 — calibration constant transcribed across regimes.**
SATURATION_MIN_JOINT = 20 was sized from Phase C (rc2_archive): R1 (B=300/arm)
had 30 joint cells at coverage 39v32; R2 (B=600/arm) had 30 at 42v31. Phase C
had **no guard stage**. The campaign added the guard (TILT re-priced to 0.625
at lock), which vetoed 55/153 archive offers at Stage-0 init (36%) and 43 (R) /
13 (M) more in the arm phases. Archives ran 17v26 instead of ~31-42/arm; the
constant was never re-derived under the campaign's own occupancy regime. This
is the same class of error erratum #14 caught in CAL-C: a pinned number whose
generating conditions had changed.

**RC2 — no occupancy feasibility gate.**
The campaign gated the instrument (CAL-I) and the cost model (CAL-C) pre-flight,
but nothing gated the saturation contingency's evaluability. The miss was
projectable at the 150 checkpoint: joint was 14 (R 15, M 21, contested 6) with
R's fill rate at 3/150 — a linear tail projects final joint ≈ 15-16 vs bar 20.
That signal was available ~9 h of wall before conclusion. The §9 salvage rule
could not help: it re-evaluates the *same* bar at the last mutual checkpoint.

**RC3 — the plateau is structural, so budget was never the fix.**
R is the fresh-generation baseline; its cell discovery saturates by
construction (and the tilt guard removes a further band of legal fills:
R_sim_excluded 148, R_quick_reject 113 of 300 evals). The B=600 original design
would (a) still have missed — 0 R fills after eval 187 — and (b) have
wall-capped anyway under the pre-erratum-#14 8 h cap. There is no accessible
compute setting under this design in which the 20-joint bar is met.

**RC4 — tie semantics conflate init persistence with search parity.**
Both archives share the Stage-0 init (14 cells, identical counters). Joint
cells still holding the *identical* init elite in both archives (same canon)
are counted as M non-wins in the registered denominator. In Phase C R2 that
residue was 4/30 (13%); in the campaign's smaller archives it was **5/15
(33%)**. Those cells carry no information about search value — neither arm
ever replaced them. Registered rule: 7/15 = 46.7% (< 60%, i.e. would have
FAILED even at joint ≥ 20). Contested-only (same-canon excluded): 7/10 =
70.0% (> 60%). The verdict-relevant read flips on a semantics choice the
prereg fixed for a regime (large archives, thin init residue) that did not
obtain.

**RC5 — background: the full-conv instrument is out of top-end headroom.**
Seven of M's 26 elites sit at exactly 0.5000 (the cap); M_top10's CI upper
bound is 0.4995. The gap metric was already saturation-dead (observed gap
0.0151 vs bar 0.05 — this is precisely why C7's switch existed), but the
switch metric degrades at the ceiling too: one joint cell has *distinct*
genomes tied at exactly 0.5000, where a strict win is impossible. Any future
arm-pair design needs either headroom (harder opponent gap ⇒ new CAL-I) or a
top-end metric that does not read the capped scale.

## 4. What worked

- The verdict machinery emitted the registered token — no silent failure, no
  post-hoc bar-bending mid-run.
- Checkpointing + the errata discipline (#13, #14) caught the CAL-C /7 cost
  bug mid-flight and salvaged the campaign into a shape that finished at
  ~19.0 h against a 36 h cap.
- Direction-of-signal (NON-BINDING) is coherent across every reported metric:
  M over R on coverage 26v17, QD 11.458v7.604 (+51%), top-10 with
  non-overlapping CIs, contested cells 7-2. Nothing here contradicts the M
  hypothesis; the campaign failed to *measure* it at the registered bar, it
  did not measure its absence.
- Heritability r = 0.232 (raw, 299 pairs) was captured, so the SEARCH_NEUTRAL
  branch's next-step input already exists if that path is taken.

## 5. Counterfactual table

| Counterfactual | Outcome | Evidence |
|---|---|---|
| B=600 (original) | Still PROBE_INCOMPLETE, plus 8 h wall-cap breach | 0 R fills after eval 187; erratum #14 pricing (b600 pess 48-65 h) |
| Joint ≥ 20 somehow reached, v1 tie rule | BAR H FAIL → SEARCH_NEUTRAL | 7/15 = 46.7% < 60% |
| Gap metric (no saturation switch) | BAR H FAIL → SEARCH_NEUTRAL | gap 0.0151 < 0.05, ceiling-compressed |
| Contested-cell rule (v2 draft) | BAR H PASS → slate | 7/10 = 70% ≥ 60% |

Every registered path out of this run other than the v2 semantics leads to
"signal not demonstrated" for reasons that are artifacts of ceiling + init
residue + archive size, not of the M-vs-R comparison itself. That is the case
for a re-registration — and also exactly why the re-registration must not be
allowed to mint confirmatory evidence on its own (see the draft's §0 firewall).

## 6. Lessons (for any future arm-pair registration)

1. Constants inherited from a prior phase must be re-derived when any
   occupancy-shaping mechanism changes (guards, init size, B, cell grid) —
   "transcribed from §0 lock files" is not sufficient provenance across regimes.
2. Every contingency bar needs a pre-flight or first-checkpoint feasibility
   gate (CAL-O pattern), with re-scope-before-continue semantics like CAL-C's.
3. Tie/denominator semantics are bar constants and need the same calibration
   discipline as thresholds.
4. A checkpoint whose projection makes the bar unreachable should be allowed
   to end the run early — 9 h of the 19 were spent buying no additional
   verdict information.
