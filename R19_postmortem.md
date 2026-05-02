# R19 Postmortem — smoke gate over-rejection on borderline seeds

**Trigger**: R19 menger missed goal #2 (top-1 ≥ 0.35) by 0.022, landing at 0.3293. Reviewing the pre-launch smoke gate in light of R19 results shows the gap was plausibly self-inflicted.

**Scope of this postmortem**: B2 PPO smoke gate calibration only. Evolution itself ran cleanly; this is about which seeds we *let into* evolution.

See: `evaluation_report_run19.md` § "Smoke gate retrospective" for the headline finding. This document expands it into a calibration proposal for R20+ champion runs.

---

## What happened

The pre-launch smoke gate (3000-ep PPO, 19 seeds) dropped 9 seeds. Five of those drops were **m1–m5** — every menger in-family capture variant (`{custodian-1, custodian-2, surround, outnumber-2, none} + influence(r=1) + threshold-race`).

All five dropped on essentially identical numerics:

| seed | sampled_avg_len | greedy_p1_wr | seat_bias | floors |
|---|---:|---:|---:|---|
| m1 custodian-2 | 39.7 | 0.86 | 0.36 | length floor 40.0; seat bias floor 0.30 |
| m2 custodian-1 | 39.7 | 0.86 | 0.36 | same |
| m3 surround    | 39.4 | 0.86 | 0.36 | same |
| m4 outnumber-2 | 40.2 | 0.86 | 0.36 | seat bias only |
| m5 none        | 39.7 | 0.86 | 0.36 | same |

Length came in 0.3–0.6 moves below the 40.0 floor. Seat bias came in 0.06 above the 0.30 threshold. **Marginal misses on both axes, with five seeds clustered identically** — a strong signal that we were measuring the substrate, not the seeds.

R19 evolution then went on to put **every one of those capture rules** (custodian, surround, outnumber) into the menger top-7, all under the same `+ influence(r=1) + threshold-race` family. The eventual top-1 (`1f9191b5d4e6`, 0.3293) is exactly the m4 combo (outnumber-2 + influence(r=1) + threshold-race), reached by crossover at gen 7.

The smoke gate said "PPO can't train this family." Evolution proved otherwise — at a higher budget.

---

## Smoke gate scorecard

Out of 9 R19 drops, scoring against R19's actual results:

| Drop | Substrate | Smoke verdict | R19 evolution verdict | Right call? |
|---|---|---|---|---|
| m1 custodian-2 + inf(r=1) + threshold | menger | unplayable | top-10 family present (custodian variant: #2 carry-over) | ❌ wrong |
| m2 custodian-1 + inf(r=1) + threshold | menger | unplayable | top-10 family | ❌ wrong |
| m3 surround + inf(r=1) + threshold | menger | unplayable | **top-3** (`5048f71b62fd`, 0.3158) | ❌ wrong |
| m4 outnumber-2 + inf(r=1) + threshold | menger | unplayable | **top-1** (`1f9191b5d4e6`, 0.3293) | ❌ wrong |
| m5 none + inf(r=1) + threshold | menger | unplayable | top-10 family | ❌ wrong |
| c6 outnumber-2 + territory | carpet | seat bias 0.50 | no descendant in top-10 | ✅ right |
| c8 outnumber-2 + inf(r=3) + threshold | carpet | seat bias 0.38 (r=3 over-amplifies) | no descendant in top-10 | ✅ right |
| g1 custodian-1 + connection | grid | seat bias 0.50 | (R18 reproduction; grid was control only) | ✅ right |
| g3 hybrid validator | grid | seat bias 0.50 | hybrid penalty D1 verified separately | ✅ right (but D1 already covered it) |

**Score: 4 right, 5 wrong.** The five wrong calls are all the m1–m5 cluster.

---

## Root cause: smoke and evolution run at different budgets

Smoke runs at **3000 PPO episodes** per seed; full evolution runs at **10000 episodes** with **C2 multi-seed averaging across 3 runs**. The smoke verdict is therefore a budget-relative measurement, not a fixed property of the game.

For the m1–m5 cluster, the binding constraint at 3000 ep was: PPO couldn't train P2 to disrupt P1's influence accumulation on a 400-cell 3D substrate. With 4000 more episodes plus averaging across 3 runs, P2 picks up enough policy quality to balance the seat bias and push average length above 40.

This isn't a new pattern. R18 smoke dropped `c2 outnumber + threshold` on every fractal substrate except grid for the same reason. R18's eventual menger top (`0f5e931fa3e1`) was that exact family — it just took mutation/crossover at higher PPO budgets to reach it. **R18 and R19 are now both confirmed cases** of smoke over-rejecting the family that wins.

---

## Cost estimate

The eval report's estimate: ~4–5 generations of evolutionary work to rediscover what direct seeds would have provided in gen 0. Concretely:

- Carpet seeds (c1–c5) survived smoke. Carpet's top-2 and top-3 are direct seeds. Evolution refined from a strong starting point.
- Menger seeds (m1–m5) were all dropped. Menger's gen-0 peak was 0.00; gen 7–8 peaks were 0.33. The path was: convergent mutation/crossover from out-of-family seeds (m6 territory, m7 connection, m8 r=2 inf) into the in-family combos that smoke had filtered out.

**If m1–m5 had been kept**, gen 0 would have started with the dominant family present. The 0.022 gap on goal #2 was plausibly closeable.

This is a calibration cost, not a methodology failure: the gate did its job (dropping unplayable games) for 4 of 9 drops. The other 5 misclassified borderline-but-trainable seeds as unplayable.

---

## Proposal: two-tier smoke for R20+ champion runs

The current gate is binary: pass or drop, single 3000-ep budget. The proposed change is to add a cheap second-chance tier for borderline drops. Cost is bounded and predictable.

### Tier 1 (unchanged): 3000-ep PPO, 1 run per seed

Hard-drop only on catastrophic failures:
- `seat_bias ≥ 0.45` (P1 or P2 wins ≥ 95% of seats — game is structurally lopsided, no PPO budget will fix it)
- `sampled_avg_len < 15` (degenerate quick-end)
- `greedy_p1_wr ≥ 0.95` AND `seat_bias ≥ 0.40` (greedy player dominates)

Everything else is **borderline**, not dropped.

### Tier 2 (new): 6000-ep PPO retry on borderline seeds only

Borderline = passed Tier 1 hard-drop checks but failed the soft floors (length floor or seat bias 0.30–0.45 zone).

For each borderline seed:
- Re-run PPO at 6000 episodes (2× the smoke budget; 60% of the evolution budget).
- Re-measure length and seat bias on the longer-trained policy.
- **Pass if either** the longer-trained metrics clear the soft floors **or** seat bias drops by ≥ 0.05 between Tier 1 and Tier 2 (showing PPO is making progress, just not finished).

The "showing progress" rule is the key calibration. If 4000 extra episodes can move the seat bias even partially toward balance, the full 10000-ep evolution budget plus C2 averaging will close the rest. If the metric is flat between 3000 and 6000 ep, the seed is genuinely structurally biased and should drop.

### Cost of Tier 2

Borderline seeds in R19 would have been: **m1–m5** (length and seat bias both marginal). That's 5 retries × 6000 ep = 30000 extra PPO ep before launch.

For comparison, R19 used **1041 PPO runs total across the three substrates** (525 + 420 + 96), each at 10000 ep ≈ ~10M ep total. Tier 2 retries are a 0.3% surcharge on total compute. Wall clock is bounded by the slowest substrate: ~2 hours of extra smoke time, run in parallel with launch prep.

### What stays the same

- Hybrid action games still drop (g3-style). D1 covers the case post-hoc anyway.
- R8 Connection Go on grid still drops (g1-style — clean catastrophic seat bias 0.50).
- Carpet r=3 influence still drops (c8-style — out-of-family probe with seat bias > 0.30 floor and PPO already converged at 3000 ep).

The two-tier rule changes only the borderline cases. It does not loosen the gate against genuinely broken games.

---

## Decision for R20

R20 scope is undecided as of this writing (see eval report § "What's next"). Whichever direction is chosen, **two-tier smoke should be in scope** if the run includes any in-family menger seeds or anything structurally similar to the m1–m5 cluster.

If R20 is "re-run menger only with a more lenient smoke gate" (one of the listed options), that *is* this proposal. The test would be: does a Tier-2-rescued m4 (outnumber-2 + inf(r=1) + threshold) seed at gen 0 clear 0.35 by gen 5–6 instead of gen 8?

If R20 is a different direction (hexaflake, pie rule, vicsek/triangle revival), Tier 2 still applies — fractal substrates with influence-based win conditions are exactly the regime where smoke at 3000 ep under-measures trainability.

---

## What this postmortem does NOT change

- The smoke gate's existence. Dropping the 4 catastrophic seeds (g1, g3, c6, c8) prevented compute waste on genuinely broken games.
- The evaluation methodology. R19's C1+C2+D1 scoring stack is solid; the issue is upstream.
- The R19 results. Goals #1 and #3 cleared; #2 missed by a measurement-noise-scale gap; #4 pending. The headline carpet + menger findings stand.

The change is narrow: **don't equate "PPO can't beat the seat-bias floor in 3000 episodes" with "this game is unplayable."** Give borderline cases a 6000-ep second look before excluding them from evolution.
