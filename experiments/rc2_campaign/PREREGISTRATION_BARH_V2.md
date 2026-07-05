# RC2 BAR H-PG saturation contingency — re-registration v2 (DRAFT)

Status: **DRAFT — OWNER RATIFICATION PENDING** (2026-07-05). Changes no code
and no data. On ratification: bars.py `SATURATION_MIN_JOINT` 20→10,
`run_campaign.bar_h_inputs` contested-cell computation, tests re-pinned,
change review-logged per §10 of the parent prereg.
Parent: `PREREGISTRATION.md` (locked 2026-07-01). Post-mortem basis:
`POSTMORTEM_PROBE_INCOMPLETE.md`.

## 0. Epistemic position — read first

This registration is written **after** the campaign concluded and **with full
knowledge of the outcome under every candidate rule**:

| Rule | Known outcome on the final archives |
|---|---|
| v1 (ties in denominator, joint ≥ 20) | PROBE_INCOMPLETE (joint 15) |
| v1 semantics, any n_min ≤ 15 | FAIL — 7/15 = 46.7% < 60% → SEARCH_NEUTRAL |
| v2 (contested-cell, n_min ≤ 10) | PASS — 7/10 = 70.0% ≥ 60% → slate |
| any n_min > 10 | PROBE_INCOMPLETE again |

Therefore this document **cannot create confirmatory evidence**. Its sole
registered consequence is a *routing* decision: whether the §7 slate — which
is blind, fresh, and whose bars are untouched by this document — runs on the
existing final archives. All inferential weight lives in the slate bars
(S-GO-1, S-GO-2, d4015 validity band). Ratifying v2 is exactly the decision
"run the slate on M's top-3"; it is presented in bar language only so the
constants bind identically on future runs, where they WILL be pre-data.

## 1. Scope

Replaces the saturation-contingency clause of parent §6 (C7) only. Untouched:
BAR W-PG, the primary gap metric and its 0.05 bar, the 0.40 saturation switch
trigger, slate composition/blinding (§7), slate bars, decision grammar (§9),
CAL-I/CAL-C gates. Applies to:

- **(a) Reanalysis (post-hoc, disclosed):** the concluded campaign's final
  archives (B_effective = 300).
- **(b) Pre-data (binding):** any future RC2 arm-pair run, where §6 below also
  binds.

## 2. Amended metric — contested-cell record

On saturation switch (R_top10 ≥ 0.40, unchanged):

- **Joint cells** = cells filled in both final archives.
- **Excluded from numerator AND denominator: same-canon cells** — joint cells
  whose two elites are the identical genome (equal `canon` hash). These are
  shared Stage-0 init residue neither arm ever replaced; they measure init
  persistence, not search value. (Registered v1 counted them as M non-wins;
  in small archives that residue dominates — 5/15 here vs 4/30 in Phase C R2 —
  and biases the read toward NEUTRAL mechanically.)
- **Contested cells** = joint − same-canon. M strict win iff M's elite
  full-conv floored mean > R's.
- **Distinct-genome equal-value cells stay in the denominator as non-wins.**
  They are real contests the ceiling flattened; excluding them would spend the
  ceiling twice in M's favour.
- **Bar: M strict wins ≥ 60% of contested cells (θ unchanged from v1), with
  contested n ≥ 10.** Contested < 10 → PROBE_INCOMPLETE for this bar
  (unchanged token semantics).

Known outcome under (a), stated plainly: contested = 10 (7 M / 2 R / 1
equal-value-at-0.5000) → 70.0% → **PASS**.

## 3. Constant derivation and disclosures

- **θ = 0.60 is retained, not re-chosen.** The only semantic change is the
  same-canon exclusion; a θ moved to sit at the known 70% would be maximally
  post-hoc and is rejected.
- **n_min = 10.** Derivation: n_min's function (v1 and v2) is to refuse
  verdicts on trivially small joint sets, and its size must come from the
  regime that produces the data. The campaign regime (guarded archives,
  14-cell shared init, B=300) produced contested counts of 6 (ckpt 150) and 10
  (final); the Phase-C-derived 20 belongs to a guard-free regime that no
  longer exists. n_min = 10 is the smallest evaluable count observed in-regime
  — and yes, it exactly admits the known data; that is disclosed, not hidden,
  and is why §0's firewall exists.
- **Type-I honesty (both versions are triage, not tests):** under a
  search-neutral null (per-cell win p = 0.5, cells independent), false-pass
  P(≥60% of n) = **0.377 at n=10** (v2) vs 0.252 at n=20 (v1). Neither
  controls error at evidential levels; BAR H has only ever routed to the
  slate, where GO is decided. The economics: a false trigger costs one slate
  (3 blind tmux teams × 7-game pack, ~agent-hours, bounded, no search
  compute); a false non-trigger kills a campaign that cost ~19 h. Given the
  run is otherwise a dead end, the permissive trigger is the correct trade.
- **Retroactive consistency check:** the v2 rule applied to Phase C data
  passes both replicates (R1: 74% of contested; R2: 20W/6L distinct-genome →
  76.9%), i.e. it does not reverse any previously validated read.

## 4. Registered consequence chain (reanalysis (a))

On ratification, `decide_verdict` re-runs over the final archives with v2
constants. All other §6/§9 conditions are already resolved (CAL-I PASS, wall
19.0 h < 36 h, archives ≥ 10 rated elites: 17/26, BAR W PASS 3/3): the chain
lands **BAR H-PG v2 PASS → SLATE_PENDING**, and the §7 slate runs manually,
unchanged, on the existing archives.

**Known-in-advance slate facts (disclosed so ratification prices them in):**

- Top-3 M elites will come from the seven cells at exactly full-conv 0.5000
  (family cap ≤ 2 applies; canon-lex tiebreak) — top-pool min = 0.5000.
- Contrast picks are best-first within the lowest tertile (slate.py §7
  semantics): expected contrast max ≈ 0.4479 → S-GO-2 minimum-contrast gap
  ≈ 0.052 < 0.15 → **SEPARATION_UNDERDETERMINED will be declared by
  construction**. The slate verdict then rests on S-GO-1 ∧ d4015 in
  [3.48, 4.18], i.e. **the maximum reachable outcome is GO-PARTIAL** (loop
  integration registered but gated on one confirmatory slate).
- S-GO-1 (≥ 1 of top-3 reaches game score ≥ 4.10, blind) is unaffected by any
  of the above and is the campaign's real question. It is fresh evidence
  regardless.

Ratifying v2 therefore buys: one blind test of "did M find an R8-parity game",
ceiling-capped at GO-PARTIAL. It cannot buy GO. If that ceiling is not worth a
slate, DECLINE (below) is the coherent choice.

**Not amended, considered and rejected:** flipping contrast selection to
worst-first would restore the S-GO-2 gap (0.5000 − 0.2760 = 0.224 ≥ 0.15) but
(i) is a second post-hoc change made knowing the values, and (ii) the lowest
elites (0.0729) risk being recognisably broken, threatening the blind. The
registered SEPARATION_UNDERDETERMINED path exists precisely for this case.

## 5. Decision grammar deltas

- (a) reanalysis verdicts are reported with the tag **BARH-V2-REANALYSIS** next
  to the token, permanently distinguishing them from pre-data verdicts.
- FAIL branch (not reachable on known data, binding for (b)): SEARCH_NEUTRAL →
  parent §6 heritability next-step. For the record, the campaign's r = 0.232
  (299 pairs) < 0.3 → mutation/signal interaction analysis is the registered
  follow-on if the owner declines this registration.
- No other token, bar, or consequence changes.

## 6. Pre-data bindings for any future RC2 arm-pair run

1. **CAL-O (occupancy feasibility gate):** at the first registered checkpoint,
   project final contested count from observed per-arm fill rates (linear
   tail). Projection < n_min → the run stops early with PROBE_INCOMPLETE and a
   re-scope decision (CAL-C re-scope pattern: re-registration, never a silent
   change). No further budget may be spent on a bar already known unreachable.
2. Same-canon exclusion (§2) binds from the start.
3. Occupancy-shaping changes (guard constants, init size, B, cell grid)
   invalidate all transferred occupancy constants; they must be re-derived
   from a same-regime source, with provenance named in the §0 lock.
4. Instrument headroom: if > 25% of an arm's elites sit at the full-conv cap
   at any checkpoint, the top-10 gap metric is declared saturated for the run
   regardless of R_top10, and the contested-cell record is the binding metric
   from that point (removes the single-threshold cliff at 0.40).

## 7. Ratification decision (owner)

- **RATIFY (recommended):** slate runs on existing archives; outcomes
  {GO-PARTIAL, NO-GO, CAMPAIGN_UNRESOLVED, SLATE_INCOMPLETE}; no search
  compute.
- **DECLINE:** campaign token remains PROBE_INCOMPLETE; registered analysis
  follow-on = mutation/signal interaction analysis (r = 0.232 branch); slate
  does not run.
- **SHELVE:** as DECLINE, and §6 bindings are still adopted for future runs.

Recommendation rationale: the direction-of-signal is uniform (coverage 26v17,
QD +51%, top-10 CIs non-overlapping, contested 7-2), the remaining
uncertainty is exactly what the blind slate measures, its cost is bounded, and
the GO-PARTIAL cap keeps the post-hoc origin of this registration from ever
converting directly into loop integration.
