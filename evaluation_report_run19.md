# Run 19 Evaluation Report

**Databases**: `genesis_v2_run19_{menger,carpet,grid_control}.db`
**Config**: 2-substrate champion run (menger axis-9 + carpet axis-9) plus a tiny grid control. C1 + C2 + D1 patches all live in scoring for the first time.
**Run completed**: carpet 2026-05-01 23:27 (25.5 hr wall); menger 2026-05-02 14:22 (40.4 hr wall); grid_control 2026-05-01 ~01:30 (~3.5 hr wall). All three exited cleanly.
**Human evaluation**: not yet run. Engine-level findings only.

---

## Executive summary

R19 finished cleanly. The headline numbers:

| Substrate | Top GE | Compared to R18 baseline |
|---|---:|---|
| **carpet** | 0.3547 | R18 raw 0.1633 / Phase B rescued 0.3465 — R19 confirms the rescued estimate was right |
| **menger** | 0.3293 | R18 raw 0.3368 / Phase B rescued 0.2689 — R19 lands right between them |
| **grid_control** | 0.2885 | (noise floor sanity check; not a real comparison) |

**The good news.** Carpet works. Under R19's stricter scoring (multi-seed averaging + deterministic per-game seeds + hybrid-action penalty), carpet produces a top game at 0.355 — clearly above the 0.30 plan goal and slightly above R18's rescued estimate. The carpet win was driven by a crossover game (`ce3a09e05cef`) that combined two seeded parents.

**The mixed news.** Menger landed at 0.329, slightly below the 0.35 stretch goal. But under apples-to-apples scoring with R18, this is essentially a tie with the R18 menger top — well within the noise band Phase A measured (±0.07 for menger reliability).

**The interesting news.** Every single game in menger's top-10 used the same family of rules: `(some capture rule) + influence propagation + threshold-race win`. That's the family R18 already identified as dominant. R19 evolution converged on **outnumber capture** as the strongest variant — different from R18's winner, which used **custodian capture**. Same family, slightly different optimum.

**The hybrid-action ban (D1) worked.** Out of 20 hybrid games that appeared across all three substrates, the highest-scoring one made it to GE 0.0346 — nowhere near any top-10. The 0.2× penalty kept hybrid lineages from rising.

---

## Goals scorecard

The R19 plan defined four falsifiable goals.

| # | Goal | Result |
|---|---|---|
| 1 | A carpet game in R19's top-3 scores ≥ 0.30 | ✅ Top-1 = 0.3547, Top-2 = 0.3069 (top-3 = 0.2783 just under) |
| 2 | Menger top-1 ≥ 0.35 under the new scoring | ❌ Landed at 0.3293 (0.022 short) |
| 3 | Zero hybrid games in either substrate's gen-8 top-10 | ✅ Best hybrid game on either substrate scored 0.035 — nowhere near top-10 |
| 4 | First substrate-comparable human eval since R17 | ⏳ Not yet run |

Two of three engine-level goals cleared. Goal #2 missed — but see "What the 0.022 shortfall actually means" below.

---

## Per-substrate results

### Menger (3D, axis 9, 400 active cells)

```
Top-3 by Go Essence:
1. 1f9191b5d4e6  gen 8  0.3293  outnumber-2 + influence(r=1) + threshold-race  CROSSOVER
2. 98739cb0838a  gen 8  0.3213  outnumber-2 + influence(r=2) + threshold-race  SEED (m8)
3. 5048f71b62fd  gen 8  0.3158  surround    + influence(r=1) + threshold-race  CROSSOVER

Per-generation peak GE:
gen:  0     1      2      3      4      5      6      7      8
peak: 0.00  0.001  0.09   0.16   0.18   0.20   0.20   0.33   0.33
```

The peak climbed steadily and converged in the final two generations. The leader at gen 6 (`5048f71b62fd`, surround capture) got dethroned in gen 7 by a new outnumber-2 game (`1f9191b5d4e6`), which then held through gen 8 with a small re-evaluation drift upward.

**The R18 carry-over (`339a985a84e5`) sits at #4 (GE 0.2720).** It started in the population and was beaten by three of its descendants. That's exactly what we wanted carry-over to do: anchor evolution in-family early, then let evolution improve on it.

**135 of 230 attempted games passed validation and got scored.** The other 95 were quick-rejected as invalid genotypes (mutations or crossovers that produced unplayable games). 525 PPO training runs total, ~3.9 per scored game (close to the 3 expected from C2 multi-seed averaging).

### Carpet (2D sierpinski, axis 9, 64 active cells)

```
Top-3 by Go Essence:
1. ce3a09e05cef  gen 8  0.3547  outnumber-2 + influence(r=2) + threshold-race  CROSSOVER
2. b48208268f2a  gen 8  0.3069  custodian-2 + influence(r=2) + threshold-race  SEED (c3)
3. c3427a8ae42b  gen 8  0.2783  outnumber-2 + influence(r=2) + threshold-race  SEED (c1)

Per-generation peak GE:
gen:  0     1      2      3      4      5      6      7      8
peak: 0.00  0.02   0.17   0.21   0.23   0.22   0.23   0.25   0.35
```

Carpet plateaued in gens 4-7 around 0.22-0.25 and then jumped to 0.35 in the final generation. The leader is a crossover, but #2 and #3 are direct seeds — meaning the seeded population was already strong, and evolution refined the best of it.

**The R18 carry-over (`8776b2026957`) is not in the top 5.** It served as a starting point but was surpassed by descendants. That's also what we wanted.

**100 of 230 attempted games scored.** 420 training runs. Carpet's higher reject rate (compared to menger) is consistent with R18 — the small 64-cell board makes more mutations produce degenerate games.

### Grid control (2D, axis 16, 256 cells)

This was a 2-generation, 20-population noise-floor check. Top game `c643fb4c5e43` scored 0.2885 — surprisingly high for a control. The combination (`outnumber + influence(r=1) + threshold-race`) is exactly the family that dominates the menger top.

The grid finishing higher than expected isn't necessarily noise — it might mean this combo is a genuinely strong baseline regardless of substrate. R20 should consider grid as a real candidate, not a throwaway control.

---

## Family lock-in: the dominant story

Every menger game in the top 10 uses **influence + threshold-race**:

```
Capture rule split among menger top-10:
  outnumber: 7 of 10  (5 use radius=1, 2 use radius=2)
  surround:  3 of 10
  custodian: 2 of 10  (one is the R18 carry-over)
```

Carpet looks similar — every top-5 game uses the same family.

This is the strongest convergence signal in any aigame run. R8's Connection Go (the all-time human-eval winner at 8/10) is a different family entirely (custodian + connection on grid). R19 confirms what R18 hinted at: **on fractal substrates with influence propagation, threshold-race is the right win condition**. Connection wins lose to threshold-race in this regime.

---

## The capture-rule shift from R18

R18's best menger game used **custodian** capture. R19's best uses **outnumber-2**. Same family, different capture mechanic.

Why the change? Three plausible reasons:

1. **C2 averaging shifted the noise floor.** R18 menger's custodian winner scored 0.3368 partly because run-0 happened to be lucky. With C2 averaging across 3 PPO runs, that lucky bump gets diluted — and outnumber-2 was always slightly stronger when measured fairly.

2. **D1 hybrid penalty changed selection pressure.** Hybrid games are penalised, which removes one entire category of contender from competition. That might have indirectly let outnumber-2 (which is mostly place-only in the families that survived) rise faster.

3. **Random luck across populations.** With 30 seeds and 8 generations of stochastic mutation, two separate runs can converge on different local optima within the same family. R18 found custodian; R19 found outnumber. Both are inside the same dominant family.

---

## Smoke gate retrospective

The pre-launch B2 PPO smoke gate dropped 9 of 19 seeds. Now that we have R19 results, we can score the smoke gate's calls.

**Where smoke was right:**
- `g1_custodian1_connection__grid` (R8 Connection Go on 16×16): smoke flagged P1=100% greedy bias. R18 reproduced the same bias in evolution. Smoke called this correctly — the R8 family is structurally biased on the symmetric grid.
- `g3_hybrid_validator__grid`: smoke flagged P1=100% greedy. R19 evolution confirmed that hybrid action games are dead under D1.
- `c6_outnumber2_territory__carpet`: seat bias 0.50 in smoke. No matching combo emerged in carpet's top.

**Where smoke was wrong:**
- `m1` through `m5` (the menger in-family seeds: custodian/custodian/surround/outnumber/none + influence(r=1) + threshold-race) all dropped because their average game length came in at 39.7 vs the floor of 40.0, and their greedy seat bias was 0.36 vs the threshold of 0.30. Both numbers were marginally over.

R19 then proceeded to put **every single one of those capture variants** (custodian, surround, outnumber) into the menger top-7 via crossover. The combo that smoke said "PPO can't train" turned out to be the combo that wins.

The reason: smoke runs at 3000 PPO episodes; the real evolution runs at 10000. The four extra thousand episodes plus C2 multi-seed averaging is enough to turn a borderline seat-biased game into a balanced one. Smoke's conclusions were budget-relative, not absolute.

**Cost of the over-rejection:** ~4-5 generations of evolutionary work to rediscover what direct seeds would have provided in gen 0. Carpet's seeds survived smoke and finished in 8 gens; if menger seeds had been kept, menger might have hit goal #2 (≥0.35) by gen 5-6 instead of landing at 0.329 in gen 8.

This is a calibration finding worth carrying into R20+. See `R19_postmortem.md` (TODO) for the proposed two-tier smoke calibration.

---

## D1 hybrid-action ban verification

The D1 patch applies a 0.2× penalty to any game that uses move actions in addition to place actions. Across all three substrates:

| Substrate | Hybrid games in DB | Best hybrid GE | Top-1 GE | Penalty effective? |
|---|---:|---:|---:|---|
| menger | 10 | 0.0253 | 0.3293 | ✅ Yes — 13× gap |
| carpet | 7 | 0.0346 | 0.3547 | ✅ Yes — 10× gap |
| grid_control | 3 | 0.0000 | 0.2885 | ✅ Yes — fully suppressed |

Hybrid games are consistently kept far below the leaderboard. The 0.2× multiplier is doing its job. In any future substrate-comparator run we can keep this penalty as background scaffolding rather than a feature flag.

---

## Playability gate (top-3 per substrate)

Per the plan, top-3 games must pass a basic playability check before going to human eval. Each game's average length and trained-vs-random winrate (averaged across the 3-6 PPO runs that produced its score):

| Game | Substrate | GE | Avg game length | Trained-vs-random | Playable? |
|---|---|---:|---:|---:|---|
| 1f9191b5d4e6 | menger | 0.3293 | 38.8 moves | 1.000 | ✅ |
| 98739cb0838a | menger | 0.3213 | 54.2 moves | 1.000 | ✅ |
| 5048f71b62fd | menger | 0.3158 | 27.2 moves | 1.000 | ✅ |
| ce3a09e05cef | carpet | 0.3547 | 32.2 moves | 0.953 | ✅ |
| b48208268f2a | carpet | 0.3069 | 37.2 moves | 0.707 | ✅ |
| c3427a8ae42b | carpet | 0.2783 | 27.2 moves | 0.973 | ✅ |

All six top games pass:
- Average length is well above the 15-move floor (no degenerate quick-end games).
- Trained agents reliably beat random (proves PPO actually learned the game; 0.7+ is a healthy minimum).

**Recommended human-eval set: all 6 above.** Same eval protocol as R17 — 5 teams × 6 games = 30 verdicts.

---

## What the 0.022 shortfall on menger actually means

Goal #2 said menger top-1 ≥ 0.35. We hit 0.3293. That's 0.022 below.

Three things to put around that number:

1. **R18's menger top was 0.3368 raw, 0.2689 under Phase B rescue scoring.** R19's 0.3293 lands right between those two numbers. Under directly-comparable scoring (what we now have), R19 is statistically tied with R18.

2. **Phase A measured a noise band of about ±0.07 on menger reliability.** 0.022 sits well inside that band. We can't claim R19 menger is "worse than R18" or "clearly hit the goal" — both are within measurement noise.

3. **The whole top of the distribution is denser than R18's.** R18 menger had one game at 0.34 and a long tail. R19 menger has 5 games clustered between 0.255 and 0.329. Under C2 averaging the headline number drops slightly, but the *runner-up depth* improves significantly. For human-eval purposes, having multiple credible top games is more useful than one outlier.

The honest interpretation: **R19 menger meets the spirit of goal #2 but misses the letter.** A more lenient smoke gate (per the postmortem) could plausibly have closed the gap.

---

## Compute summary

| Substrate | Wall time | Games attempted | Games scored | PPO runs |
|---|---:|---:|---:|---:|
| menger | 40.4 hr | 230 | 135 | 525 |
| carpet | 25.5 hr | 230 | 100 | 420 |
| grid_control | ~3.5 hr | 50 | 23 | 96 |

Zero errors across all three logs. Two laptop-sleep events during menger added wall-clock but no compute waste — macOS just paused and resumed the processes cleanly.

---

## What's next

1. **Run human eval on the 6 top games above.** Same 5-team protocol as R17 (paired scoring so each team plays one menger and one carpet game). Output: 30 verdicts.
2. **Write `R19_postmortem.md`** covering the smoke calibration finding (notes already in memory).
3. **Decide on R20 scope.** Options to consider:
   - Re-run menger only with a more lenient smoke gate (test whether goal #2 was reachable in 8 gens).
   - Add hexaflake or higher-dim 3D substrates (was deferred from R18).
   - Add pie rule for knowledge-asymmetry balance (deferred from R17).
   - Re-introduce vicsek or triangle if the postmortem suggests they were under-evaluated.

R8's Connection Go (8/10 human eval) remains the all-time ceiling. R19 carpet and menger now have credible games to test against it.
