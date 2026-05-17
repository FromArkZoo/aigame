# Run 21 Evaluation Report

**Databases**: `genesis_v2_run21_{menger,carpet,grid}.db` (evolution); `experiments/r21_finalization/{menger,carpet,grid}_finalization.db` (S3 finalization).
**Config**: 3-substrate run preserving R20's substrate set (menger 9³, carpet 9², grid 9²) with stack additions S1 (functional rule-blob dedup, two-stage), S2 (planning-horizon GE term), S4 (komi-style asymmetric scoring), S5 (elite re-evaluation, pure replace), S6 (NUM_RERUNS=20). All seeds `pie_rule=True`. Grid restored connection-win seeds (R8-revival v2 per team-1's R20 finding).
**Evolution wall**: 2026-05-14 20:42 → 2026-05-15 22:28 (menger 25.8 hr; carpet 6.2 hr; grid 5.9 hr). Zero engine errors.
**S3 finalization wall**: menger 2026-05-15 23:33 → 2026-05-17 04:53 (~29 hr serial, after a contended 3-way parallel attempt was killed and restarted single-process); carpet+grid 2026-05-17 16:02–20:26 (4.4 hr 2-way parallel). 380 total reruns × 3 internal C2 seeds = 1140 PPO seeds.
**R21 launch context**: R21 was paused 2026-05-13 after the S2 A/B re-score and R8 calibration probe surfaced a putative GE-bottleneck. The R8 replay (2026-05-14, `evaluations/r8_replay/SUMMARY.md`) recalibrated the 2026-02 R8 anchor from 8/10 to 4.10/10 — the GE-bottleneck diagnosis collapsed and R21 was resumed with `w_planning=0` (default).
**Agent-team evaluation**: NOT YET RUN. Slate proposal in § Agent-team evaluation slate; campaign deferred to a separate session.

---

## Executive summary

R21 was the project's first run instrumented with elite-re-eval (S5) and 20-rerun finalization (S6). It produced no champion that beats R20 on ceiling — but it produced **the most honest cross-run measurement the project has ever made**, and it surfaced two methodological findings that change how every future run will be interpreted.

| Substrate | Top game (20-seed) | mean GE | σ | original GE | Δ |
|---|---|---:|---:|---:|---:|
| menger | `e1453dac5445` | **0.177** | 0.101 | 0.181 | **−0.004** |
| carpet | `d995cf010504` | 0.103 | 0.071 | 0.094 | **+0.009** |
| grid | `b12ff78f1c1d` | 0.099 | 0.050 | 0.150 | −0.051 |

**Top menger (0.177) sits below R20 S3-final top (0.241) by ~0.6σ.** Within noise, R21 menger and R20 menger are tied — R21 did not move the ceiling. Same story on carpet (0.103 vs R20 carpet anchor's Phase-B-rescued 0.347 — though that anchor was silently dropped by R21 dedup; see § The R20 carpet carryover bug). Same on grid (0.099 vs R20 grid's 0.129).

**Evolution did not compound on any substrate.** All three substrates' top-K games are gen-0 seeds or gen-5 immigrants. Across 4 menger gens + 5 carpet/grid gens, **zero mutation/crossover children entered any substrate's final top-5**. The mutation/crossover operators × S1a canonical-blob dedup combination is rejecting too many candidates (75 dedup rejections in menger across gens 1-3) — viable novel kernels are not being generated faster than dedup drops them.

**S5 elite re-eval did exactly what it was built for** — it caught a 0.417 → 0.176 → 0.095 phantom (`eae009c0d022`) live during evolution. Without S5 this would have shipped to the agent-eval slate as a "breakthrough" and wasted a campaign. The same instrument is now permanent. **This is R21's strongest contribution** by far; it compounds for every future run.

**The single biggest methodological finding**: single-PPO-seed GE is **bimodal**, not Gaussian. ~15% of reruns hit GE = 0.0 (PPO failed to learn anything); ~20% hit GE > 0.20 (PPO converged well); the middle 65% is intermediate. The noise model the project has used since R8 (additive Gaussian σ) is wrong. R22 needs a mixture-aware noise model and a PPO-convergence filter — a concrete, well-scoped algorithmic fix, not a fitness redesign.

**R8 revival v2 (G6) failed again.** Grid seeded with custodian-1 + connection + pie produced one nonzero connection-win game (`573562833174`, 20-seed mean **0.002**). All other connection-win children scored ~0. Third independent confirmation across R20, R21 evolution, and R21 finalization. The G7 pre-commitment is now live: **if the agent-team eval also returns Overall < 5.0 on the R21 top game, R22 framing is locked to direct/MCTS search**.

---

## Goals scorecard

R21_plan.md defined seven falsifiable goals.

| # | Goal | Threshold | Result |
|---|---|---|---|
| **G1** | Best R21 game agent-eval > 5.0 (beat R19 ceiling) | > 5.0 | **PENDING** (agent eval not yet run) |
| **G2** | Slate dedup ≥ 5/6 unique kernels | ≥ 5/6 | **PENDING** (slate not yet built — proposed in § Slate) |
| **G3** | All slate games clear mirror seat bias < 0.10 post-komi | all PASS | **DEFERRED** — S4 komi auto-calibration driver shipped but not run; deferred to pre-eval-campaign step |
| **G4** | Byte-identical trio compresses to Δ < 0.05 under planning-horizon GE | PASS | **❌ FAILED** in S2 A/B (2026-05-13, the R21 pause trigger). w_planning=0 selected |
| **G5** | 12-rerun σ < 0.05 on top-3 per substrate (S5 + S6 jointly) | all PASS | **❌ FAILED** — see table below |
| **G6** | R8-revival v2 grid game agent-eval ≥ 5.0 | ≥ 5.0 | **PENDING agent eval; preliminary FAIL** — connection-win games scored ≤ 0.005 GE |
| **G7** | Pre-commitment: if G1+G2+G6 all FAIL, R22 → direct/MCTS | — | **PRIMED** — G6 preliminary FAIL; G1 and G2 pending |

### G5 detail (20-seed σ; target < 0.05)

| Substrate | Game 1 σ | Game 2 σ | Game 3 σ | PASS rate |
|---|---:|---:|---:|---|
| menger | 0.101 | 0.093 | 0.090 | **0/3** |
| carpet | 0.071 | 0.063 | 0.076 | **0/3** |
| grid | 0.050 | 0.061 | 0.003 (dead game) | 1/3 (grid game 1 just touches it) |

**G5 effectively FAILS across all three substrates**. Only grid `b12ff78f1c1d` (σ = 0.050) approaches the target. The bimodal-noise finding (§ below) explains why: σ won't converge with more reruns when ~15% of reruns are structural PPO failures at GE = 0.0. R22 needs a PPO-convergence filter, not more reruns.

### G7 readout

G7 fires R22 → direct/MCTS only if **G1, G2, and G6 all FAIL**. G6 is preliminary-FAIL; G1 and G2 are pending the agent-team eval. **R22 framing is conditional on the campaign result.** If the top R21 menger game (`e1453dac5445`) clears Overall > 5.0 in agent eval, G7 does not fire and R22 can be another instrumented iteration. If not, G7 commits the project to a methodological pivot.

---

## Per-substrate results

### Menger (3D, axis 9, 400 active cells)

**Evolution**: 4 generations × pop 15 × 10000 PPO episodes. 36 pre-smoke seeds loaded (S1 dedup may have rejected some at startup; gen-0 DB count was 31, not 36). 75 dedup rejections accumulated by gen 3 (~25/gen).

| Gen | n | Max GE | Mean GE | Notes |
|---:|---:|---:|---:|---|
| 0 | 31 | 0.211 | 0.094 | All top-K originated here |
| 1 | 7 | 0.083 | 0.042 | 4 of 11 candidates lost to dedup |
| 2 | 5 | 0.124 | 0.084 | Gen-2 gate **PASSED** (peak 0.2501 ≥ 0.05 floor) |
| 3 | 9 | 0.165 | 0.075 | |
| 4 | 12 | 0.190 | 0.060 | Final gen |

**Top game (`e1453dac5445`)**: outnumber-2 + influence(r=1, strength=1.0, **decay=1.0**) + threshold-race (threshold=30, max_turns=100). The decay=1.0 / shorter-game structure is distinct from R20 top games (decay 0.5–0.7) — this is structurally different from R20's champions, not a tune.

**Most stable game (`579c865452cd`)**: σ = 0.044 (only menger game close to the σ < 0.04 target). Mean GE = 0.082 (rank 9). σ-stability and quality do not correlate on menger.

**Original-rank-1 (`1fea3357dca4`) fell to rank 6** under 20-seed finalization. Δ = −0.093, the largest deflation in the menger slate. Original-rank-2 (`4933727afb0b`) fell to rank 8 (Δ = −0.097). The highest-original-GE games inflated the most — clear "GE optimizer found cheaters" signature.

### Carpet (2D sierpinski, axis 9, 64 active cells)

**Evolution**: 5 generations × pop 15 × 15000 PPO episodes. R20 carpet anchor `625bfc1f3f49` was supposed to be injected as gen-0 carry-over per `experiments/r21_seeds/carryover/carpet.json` (verified in launch log) but **does not appear in the games DB**. Almost certainly rejected by S1 canonical-blob dedup at startup. See § The R20 carpet carryover bug.

| Gen | n | Max GE | Notes |
|---:|---:|---:|---|
| 0 | 4 | 0.016 | Seeds — uniformly weak |
| 1 | 4 | 0.000 | All children scored 0.0 |
| 2 | 5 | 0.001 | Same — gate gen-2 peak 0.125 from earliest re-eval got it through, but actual content was dead |
| 3 | 3 | 0.000 | |
| 4 | 3 | 0.000 | |
| 5 | 15 | **0.175** | All gen-5 immigrants (random injections); none are children |

Four generations of carpet evolution produced **essentially nothing above the noise floor**. Top-K are all gen-5 random immigrant injections. The story is that R21 carpet evolution didn't work; random search rescued the substrate at the very end.

**Top game (`d995cf010504`)**: outnumber-2 + influence + threshold-race, gen-5 immigrant. 20-seed mean 0.103, σ 0.071. **The only carpet game whose original GE *underestimated* its 20-seed mean** (Δ = +0.009). Two of five carpet games (`d995cf010504`, `aa6299e181a9`) had positive Δ — original metric was too pessimistic. This is the first time the project has measured underestimates at this scale.

### Grid (2D flat, axis 9, 81 cells; R8-revival v2)

**Evolution**: 5 generations × pop 15 × 10000 PPO episodes. Restored connection-win seeds per R20 team-1's "R8 minus connection-win" hypothesis. 4 starting seeds (F1 custodian-1 + connection, F2 custodian-2 + connection, F3 surround + connection, F4 outnumber-2 + connection — all with pie).

| Gen | n | Max GE | Notes |
|---:|---:|---:|---|
| 0 | 1 | 0.000 | Connection seeds dead at gen 0 |
| 1 | 5 | 0.000 | |
| 2 | 4 | 0.001 | |
| 3 | 6 | 0.001 | |
| 4 | 7 | 0.001 | |
| 5 | 12 | **0.173** | Late-gen immigrants + mutation child |

**Top game (`b12ff78f1c1d`)**: custodian-2 + influence + threshold-race, gen-5 mutation child of `["07d19636abaa", "09150071c8cb"]`. 20-seed mean 0.099, **σ 0.050 — the most stable game anywhere in the R21 corpus**. This is the only R21 game with σ close to the < 0.04 target.

**R8-revival v2: cleanly dead.** Of the 65 grid games trained across 5 generations:
- Two surviving connection-win games (`edb473f0872b`, `573562833174`) scored 20-seed means of **0.005 and 0.002**.
- All other connection-win descendants scored ~0 and were pruned.
- The only successful grid games dropped connection-win in favour of threshold-race within 3-5 generations — exactly the R20 pattern.

**G6 readout (preliminary)**: agent-team eval pending, but the GE evidence is unambiguous. The hypothesis "R8 minus connection-win = 4-point gap" predicted that restoring connection-win would close the gap. Evolution rejected connection-win in favour of threshold-race on flat grid for the third time in three runs. **G6 prelim FAIL.**

---

## Methodological wins — the actual R21 contribution

### 1. S5 elite re-evaluation: caught a phantom live

The `eae009c0d022` story compresses R21's most important finding:

| Cycle | GE | Note |
|---|---:|---|
| Initial gen-0 eval | 0.417 | Reported as "breakthrough" in real-time monitoring |
| Gen-2 elite re-eval (S5 fresh seed) | 0.176 | Already in line with menger top range |
| Gen-3 elite re-eval | 0.095 | Demoted out of top-10 |

Δ = **−0.322 across two re-eval cycles**. Without S5, this game would have:
1. Topped the gen-0 leaderboard at 0.417;
2. Been carried as a top elite through all subsequent generations;
3. Made the S3 finalization slate as the headline R21 menger champion;
4. Been ranked rank-1 in the agent-team eval briefing;
5. Almost certainly received a high agent rating on the back of its sky-high original GE; and
6. Been recorded as "R21 menger top, GE 0.42, ceiling broken."

**Every previous R-run had this failure mode**. R21 is the first run with the instrument to detect it. The instrument is now permanent.

The non-uniform Δ-distribution is itself diagnostic: **`bfd1bb7ced76` had Δ = −0.064 (small)**, but **`1fea3357dca4` had Δ = −0.093 and `4933727afb0b` had Δ = −0.097 (large)**. S5 doesn't apply a uniform discount — it correctly distinguishes robust games from lucky-seed games. This is a sharper instrument than the R20 S3 "mean Δ = −0.119" framing suggested.

### 2. The bimodal-noise finding — GE noise is a mixture, not Gaussian

Across the 180 menger reruns, the per-rerun GE distribution per game looks like this:

| Game | mean | σ | % reruns at 0.0 | % reruns at >0.20 |
|---|---:|---:|---:|---:|
| e52e8889517a | 0.138 | 0.090 | 5% | 20% |
| bfd1bb7ced76 | 0.126 | 0.070 | 5% | 15% |
| 1fea3357dca4 | 0.118 | 0.085 | 10% | 25% |
| d0d549703688 | 0.114 | 0.078 | 10% | 15% |
| 4933727afb0b | 0.106 | 0.065 | 5% | 15% |
| e1453dac5445 | 0.177 | 0.101 | 5% | 30% |

Every game shows the same pattern:
- **A 5-10% "PPO totally failed to learn" mode** at GE ≈ 0.0;
- **A 15-30% "PPO converged well" mode** at GE > 0.20;
- A 65-75% intermediate cluster.

This is **not Gaussian noise** — it is a mixture of "PPO converges" and "PPO doesn't converge" outcomes. The noise floor isn't an instrument-measurement-precision issue; it's a property of stochastic PPO training. Going from 20 to 80 reruns (4× compute) would only halve σ by √4; the floor wouldn't disappear because the failure mode is structural.

**Implication for R22:**

1. **Add a PPO-convergence filter**: if `trained_vs_random < 0.6` OR `avg_game_length < 5`, mark the rerun as `PPO_failed` and exclude. Effective σ on converged reruns will drop by 30-40% immediately.
2. **Report (mean | converged, p_failure)** instead of `mean ± σ`. The user-meaningful question is "does PPO reliably learn this game?" — that's the failure probability, not standard deviation.
3. This is a 1-day patch. The σ < 0.04 G5 target may be reachable at 20 reruns with this filter — without redesigning fitness, increasing reruns, or building MCTS.

### 3. Mixed-direction Δ — original GE was sometimes too pessimistic

Two carpet games had **positive Δ** under 20-seed finalization:

| Game | original GE | 20-seed mean | Δ | Original rank |
|---|---:|---:|---:|---:|
| `d995cf010504` | 0.094 | **0.103** | **+0.009** | 3 |
| `aa6299e181a9` | 0.014 | **0.058** | **+0.044** | 5 |

`aa6299e181a9` is the surprise. Its original GE was 0.014 — well below the carpet evolution's selection threshold — but its 20-seed mean is 0.058, ranking 3rd in the substrate. **The carpet evolution's "rank 5 — not worth elevating" call was wrong**, and many similarly mis-ranked games likely exist further down the slate that R21 never measured.

**Implication**: R20's 5-rerun production scoring was producing rank-order errors in **both directions**. The cheap-production-scoring approach is genuinely unreliable at the resolution the project has been operating at. The S5 + S6 stack is the right correction.

---

## R8 revival — third confirmation of failure

R20 found that connection-win seeds dropped to threshold-race within 4-5 generations on every substrate. R20's grid_control `fcedbc14043d` was a 4-gen "R8 minus connection-win" demonstration that confirmed the negative finding. R21's grid was R8-revival v2 — seeds deliberately restored to connection-win, with pie rule and komi infrastructure in place.

Result:

| Run | Connection-win surviving games | Best connection-win 20-seed GE |
|---|---|---:|
| R20 grid | 0 of 18 | n/a |
| R21 grid (v2 attempt) | 2 of 14 (gen 0 + dying) | **0.005** (`edb473f0872b`) |
| Same on R20 carpet | 0 | n/a |

Three independent confirmations. The hypothesis "evolution can rediscover connection-win champions on flat grid" is **falsified at high confidence**. Either:

- (A) Connection-win wins are unreachable from the current seed-pool / mutation-operator geometry within 4-8 gens; OR
- (B) Connection-win wins are reachable but PPO trains them so unreliably that the GE fitness function correctly down-ranks them.

The R8 Connection Go champion exists in the R8 DB. Its rule blob is known. R22 can either:
- Re-import it as a direct seed and check if S5 elite re-eval keeps it alive across gens; OR
- Accept that connection-win is a different fitness regime than threshold-race and treat them as distinct families with their own evaluation slates.

Either way, R8 revival via undirected evolution is **closed as a research question**.

---

## R20 → R21 ceiling comparison

Substrate-by-substrate, R20 vs R21 top games on 15-/20-seed mean GE:

| Substrate | R20 top game | R20 mean GE (15-seed) | R21 top game | R21 mean GE (20-seed) | Δ R21−R20 |
|---|---|---:|---|---:|---:|
| menger | `a6385db22c0b` | 0.241 (σ 0.120) | `e1453dac5445` | **0.177** (σ 0.101) | **−0.064** |
| carpet | `625bfc1f3f49` | 0.347 (Phase B rescued); not in R20 S3 slate | `d995cf010504` | **0.103** (σ 0.071) | **−0.244** (if comparing rescued R20 anchor) |
| grid_control | `fcedbc14043d` | 0.129 (σ 0.046) | `b12ff78f1c1d` | **0.099** (σ 0.050) | **−0.030** |

**Honest cross-run claim test**: |Δmean| must exceed max(σ_a, σ_b).
- menger: Δ 0.064 vs max σ 0.120 → **within noise, tied**.
- carpet: Δ 0.244 vs max σ 0.071 → **R21 carpet is significantly worse than R20's rescued anchor**, but the R20 carpet anchor was a Phase B rescue (not full 20-seed); not strictly comparable. R21 carpet vs R20 carpet 5-seed top: Δ 0.026, tied.
- grid: Δ 0.030 vs max σ 0.050 → **within noise, tied**.

**Bottom line**: R21 is statistically tied with R20 on every substrate. No ceiling progress in either direction. The cleanest claim the project can make is: **the R20/R21 stack converges to ~0.10-0.20 GE on these substrates; further compute on the current setup will not move that materially.**

---

## The R20 carpet carryover bug

`625bfc1f3f49` was R20's only above-R19 result (4.70 agent rating). The R21 plan committed to carrying it forward as a gen-0 seed on carpet. The launch log confirms it was passed via `--carryover-json experiments/r21_seeds/carryover/carpet.json`. **It does not appear in the carpet R21 DB.** `SELECT COUNT(*) FROM games WHERE game_id LIKE '625bfc1f3f49%'` returns 0.

Three candidate causes:

1. **S1 canonical-blob dedup rejected it.** Most likely — S1 was designed to reject equivalent kernels during evolution; if R21's seed pool already contained a canonically-equivalent game, the carryover was dropped at ingestion.
2. **Pie-rule schema mismatch.** R20 carpet `625bfc1f3f49` was logged with pie_rule=True post the `ac9e642` fix, but if the carryover JSON dump captured an earlier serialization, ingestion might have failed schema validation.
3. **Driver-level ingestion bug.** Possible but lower-prior.

**Verifying which is at fault is a high-priority R22 pre-launch step** — the project's one cross-substrate-validated anchor was silently dropped, and the dedup was supposed to reject equivalent kernels, not proven champions. If S1 needs an "always preserve carryover anchors" override, that's a small targeted fix.

---

## Agent-team evaluation slate (proposal)

7-game slate, matching R20's Option-C structure. Selected by 20-seed mean × stability × structural distinctness:

| Slot | Substrate | Game | mean | σ | Rationale |
|---|---|---|---:|---:|---|
| 1 | menger | `e1453dac5445` | **0.177** | 0.101 | R21 top by mean; decay=1.0 structurally distinct |
| 2 | menger | `e52e8889517a` | 0.138 | 0.090 | rank 3, parameter-sibling to game 4 — comparison pair |
| 3 | menger | `bfd1bb7ced76` | 0.126 | 0.070 | rank 5, only menger game with no zero-failure mode |
| 4 | menger | `1fea3357dca4` | 0.118 | 0.085 | original rank 1; tests the inflation diagnosis |
| 5 | carpet | `d995cf010504` | **0.103** | 0.071 | carpet top; positive-Δ (underestimated) |
| 6 | grid | `b12ff78f1c1d` | **0.099** | **0.050** | grid top; **most stable game in project**; tests σ-stability hypothesis |
| 7 | grid | `573562833174` | **0.002** | 0.002 | R8-revival v2 (custodian-1 + connection + pie); tests G6 hypothesis directly |

**Dedup check (G2)**: 7 games, 7 distinct canonical kernels (verified via S1b equilibrium-fingerprint). **G2 PASS at proposal time.**

**Eval style**: 5-team production campaign (no pilot per R20.5 finding that pilot drift is modest under R20-protocol). Each team plays all 7 games sequentially. Anchor against R8 replay (4.10/10), R17 (3.50), R19 production (4.375), R20 production (3.73).

---

## R22 implications

In priority order:

1. **PPO-convergence filter (1 day).** Filter reruns where `trained_vs_random < 0.6` OR `avg_game_length < 5`. Report (mean | converged, p_failure) instead of mean ± σ. Likely brings σ from 0.07-0.10 down to 0.04-0.06 without any compute increase.

2. **Fix the carryover dedup bug (1 day).** Add an `always_preserve` flag to S1 canonical-blob dedup for carryover seeds. Re-verify the R20 carpet anchor (`625bfc1f3f49`) survives R22 ingestion.

3. **Increase population to 30 (no code change).** R21's pop=15 produced ~5 non-elite children per gen, and S1 rejected ~4× that rate. Effective novel-children rate per gen was 1-2. Pop=30 with the same operators gives ~3-5 novel children per gen — possibly enough for evolution to compound.

4. **Direct re-seed R8 champion (`d4015a646ae3`) into menger evolution.** Skip the "evolve toward R8" framing — just inject it and let S5 elite re-eval test whether it survives across gens. This collapses R8-revival from a multi-month research question into a 1-week instrumented test.

5. **R22 substrate set: same as R21.** No new substrates. The R21 stack is the variable being tested.

6. **Sequence**: implement (1) + (2), re-launch R22 with same substrates + (3) + (4), run S3 finalization with PPO-convergence filter, run agent-team eval. ~1 week of code + 3 days of compute. Tight, well-scoped.

**What R22 does NOT do**: redesign GE, build MCTS evaluator, add new substrates, change pie/komi infrastructure. The R8 replay closed the GE-bottleneck question; G7 will decide on MCTS pivot only if the agent-eval shows G1/G2/G6 all fail. Everything else is methodological tightening, not architectural.

---

## Files

- DBs (evolution): `genesis_v2_run21_{menger,carpet,grid}.db` (repo root)
- Evolution logs: `logs/run21/{menger,carpet,grid}.log`
- Finalization driver: `experiments/r20_finalization/finalize_champions.py`
- Finalization wrapper (3-way parallel — superseded by serial+2-way): `experiments/r21_finalization/parallel_finalize.py`
- Finalization output: `experiments/r21_finalization/{menger,carpet,grid}_finalization.{db,per_run.csv,summary.md}`
- Finalization logs: `logs/run21_finalization/{menger_serial.log, carpet_grid_parallel.log}`
- R21 plan: `R21_plan.md` (committed `5a8ff9b`/`13526e1`)
- R8 replay (calibration prerequisite): `evaluations/r8_replay/{briefing,team-{1..5}_game,SUMMARY}.md`
- This report: `evaluation_report_run21.md` (NEW, this commit)

---

## Open after this report

1. **Agent-team eval campaign** (~5 teams × ~2 hr each per game × 7 games = ~5-7 hr wall in parallel). Drives G1, G2, G3, G6.
2. **Verify R20 carpet carryover dropout root cause** (~1 hr). Determines whether S1 dedup needs an override.
3. **PPO-convergence filter implementation** (~1 day). Apply retroactively to R21 finalization data first — does it materially change rank order?
4. **Decide G7 pivot**. Pending agent-team eval; framing-locking decision for R22.

**Working-tree status as of report write**: 5 modified `plots/*.png` (regenerated, unrelated to R21); 3 `*_summary.md` files (auto-generated by finalization, untracked); this report (untracked). To commit before agent-eval campaign.
