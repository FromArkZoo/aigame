# Post-R21 Deep Analysis & Next Steps

**Written:** 2026-06-06. **Method:** whole-repo knowledge graph (`graphify-out/`, 8,526 nodes / 23 named subsystems) + the full R21 report + a 7-agent analysis pass, with the key claims **ground-truthed against the actual code and the on-disk per-run CSVs** (Probe B, below). This document supersedes the "R22 implications" section of `evaluation_report_run21.md` where they conflict.

---

## 1. What aigame is

A system that tries to **invent good board games automatically**. It mutates and crossbreeds the *rules* of abstract 2-player games on odd boards (3D Menger sponge, 2D Sierpinski carpet, flat grid). Each candidate is graded by a fitness number, **GE ("Go Essence")** — it trains a PPO self-play agent and measures emergent "strategic depth." But the *real* goal isn't GE; it is producing a game that a panel of **Claude agent-teams rates strategically deep, Overall > 5.0**. GE, PPO and the fractal boards are all instruments pointed at that one judged number.

## 2. Where it stands after R21

**A plateau the project has gotten very good at measuring but cannot break.**

- **Ceiling flat and statistically tied R20→R21.** 20-rerun top GE: menger **0.177**, carpet **0.103**, grid **0.099** (`experiments/r21_finalization/*_summary.md`). By the project's own honesty test (Δ must exceed the larger σ), R21 ties R20 on all three. No substrate has moved beyond its own noise in four runs (R18→R21).
- **The experiment that actually decides R21 has never been run.** There is no `evaluations/run21/` directory. Every R21 quality number is a PPO proxy. Goals G1 (Overall>5.0) and G2 are PENDING; the pre-committed G7 pivot trigger cannot fire because two of its three inputs don't exist yet.
- **No game has ever cleared 5.0 in the agent-team era.** Best modern-protocol score is R20's depth-record game at **4.80** (ties R19, misses 5.0). The R8 game that framed this quest as a "lost 8/10 peak" replayed at **4.10** (`evaluations/r8_replay/SUMMARY.md`) — today's games already sit in the same band as the all-time best. *There was never a lost peak to recover.*
- **The genuine R21 win is honesty, not capability.** S5 elite re-eval caught a phantom champion live (read 0.417, really 0.095); 20-rerun S6 finalization exposed how unreliable single-seed scores are. Durable, trustworthy instrumentation — but it does not move the ceiling.

## 3. Three corrections to the R21 report (verified against code/data)

1. **The "R20 carpet carryover bug" is a false alarm — drop the planned `always_preserve` fix.** Seed injection (`evolution/loop.py:121-133`) appends carryover seeds with **no dedup call**; dedup runs only on the random-fill loop. The anchor `625bfc1f3f49` *survived*, re-injected as `aa6299e181a9` (blob metadata reads `seeded_from: '625bfc1f3f49'`), and it is the **+0.044 carpet success the report celebrates** (orig 0.0142 → 20-seed 0.0585). One wrinkle to note so a reader doesn't re-trip on it: its DB `generation` column reads 5 even though its in-blob metadata says gen 0 / `parent_ids=[]` (likely re-archived by S5). Substance unchanged: the champion was never dropped; the "silent drop" was a query artifact.
2. **Evolution *did* compound on grid.** The R21 exec summary says "zero mutation/crossover children entered any final top-5." False for grid: its top two (`b12ff78f1c1d`, `e7c85d3409e6`) are gen-5 children with verified parent lineage. (Caveat: grid's gen-0 connection seeds all scored ~0, so beating them is a low bar — the lineage, not the margin, is the point.)
3. **The "bimodal PPO-failure" diagnosis is wrong about the cause** (see Probe B). PPO depth on menger is stable; the noise is small-sample evaluation-estimator noise. The proposed PPO-convergence filter is therefore misaimed *and* survivorship-biased.

## 4. Probe B — variance decomposition (verified, on-disk data)

Script: `experiments/r21_variance_probe/probe_b.py`. Full output: `experiments/r21_variance_probe/PROBE_B_RESULTS.md`. Reads the finalization per-run CSVs only — no training, no DB writes.

GE composite (`metrics/scoring.py:458-479`, with `w_d=w_div=w_s=1`, planning term inert at `w_p=0`):

```
raw = depth · (0.2 + 0.8·diversity) · (0.1 + 0.9·non_triviality) / (1 − simplicity)
GE  = raw / (raw + 1)
```

So `diversity` and `non_triviality` multiply directly into GE. Findings:

| Metric | menger (180 reruns) | carpet (100) | grid (100) |
|---|---|---|---|
| `strategic_depth` spread (CV; range) | **0.12; 0.444–0.820** (stable) | 0.33; 0.074–0.864 | 0.53; 0.074–0.781 |
| `strategic_diversity` distinct values | **{0, .333, .667, 1.0}** | same | same |
| GE≈0 reruns | 9/180 | 39/100 | 59/100 |
| …depth on those reruns | **healthy 0.56–0.76** | drops (mean 0.38) | low (mean 0.27) |
| …`non_triviality==0` on those | 8/9 | 35/39 | 58/59 |
| **within-game GE variance share — depth** | **0.024** | 0.265 | 0.008 |
| **— non_triviality** | **0.450** | 0.552 | 0.236 |
| **— diversity** | 0.136 | 0.004 | 0.082 |
| Survivorship: top game mean, full → filtered | **0.1775 → 0.1868 (+0.009)** | 0.1031 → 0.1085 (+0.005) | 0.0985 → 0.0985 |

Formula sanity: reconstructed-vs-stored GE corr **0.837**, mean\|Δ\| 0.116 (offset because stored GE is the C2 average of per-internal-seed GE — Jensen gap — but the structure is right).

**Reading:** On **menger** — the exact substrate the report's bimodal claim was made on — PPO learns reliably (depth stable, never near zero). The GE noise lives in the coarse **3-sample `non_triviality`** and **4-valued `strategic_diversity`** estimators. The report's stated cause ("PPO fails to converge ~15%") is wrong on its own evidence base. Filtering on a competence/non_triviality signal — which *feeds* GE (`competence_factor`, `scoring.py:307-310`) — biases the surviving mean **up** and breaks the cross-run comparability the project worked hard to earn. The bias is modest (+0.009 on the headline game) but **directional**. *Honest nuance:* on carpet/grid PPO depth does fluctuate, but those substrates are largely dead, so quality decisions aren't made there anyway; even there `non_triviality` is the top variance driver.

**Therefore: scrap the PPO-convergence filter. The honest denoiser is to raise `num_independent_runs` (currently 3, `config.py:46`) and `eval_episodes` (currently 50, `config.py:47`)** — that directly de-coarsens the two estimators that *are* the noise floor, with no censoring.

## 5. The core tension

**The project keeps sharpening the ruler instead of testing whether what it's building is any good.** R22-as-planned is a week of code that all improves GE or the evolution loop — but GE is a proxy the README itself says doesn't track agent verdicts and inverts rank order every run since R13, and the R8-replay teams independently found the real ceiling is **structural**: 8×8-class boards are too small for ladders/medium-term planning, and the influence field is observation-tensor decoration that never enters win logic. R22 keeps both the substrates *and* GE fixed, so it cannot move the ceiling its own evidence blames on the substrate.

## 6. Recommendations (prioritized)

The sharpest conflict was **"run the eval first" vs "do R22 GE code first."** Decision: **eval first** — it's the only step touching the objective, it's well-rehearsed (runs 13–20 all did it), and the R22 code sharpens a proxy known not to predict the goal.

| When | Action | Why | Effort |
|---|---|---|---|
| **NOW** | Run the S4 komi/seat-bias calibration (G3, built but never run) as a pre-eval gate | A high agent Overall on a seat-biased game is a first-player artifact, not depth | <1 hr |
| **NOW** | Run the R21 agent-team eval on the 7-game slate | Only action touching the real goal; resolves G1/G2/G6, arms/stands-down G7 | hours |
| **NOW** | ✅ Probe B done — **scrap the PPO-convergence filter**; record finding | Verified: noise is estimator-side; filter is survivorship-biased (overrides R21 report's #1 R22 item) | done |
| **NOW** | Correct the report: drop carryover "bug"/`always_preserve`; fix the grid-evolution claim | Both are verified factual errors that would misdirect R22 | hours |
| **NOW** | Pre-commit the decision rule (§7) *before* reading the eval | Turns the pivot into a falsification test, not an open-ended pursuit | hours |
| **NEXT** | If eval misses 5.0: raise `num_independent_runs` (3→5+) and `eval_episodes` (50→150+); re-validate σ on R21 tops | The honest denoiser — attacks the real noise source, no censoring; likely cheaper than 4× reruns | days |
| **NEXT** | Re-examine `planning_horizon` reinstatement — **only after verifying the S2 A/B kill wasn't a single-seed result** (`w_planning=0` is verified at `scoring.py:444`; the n=1 claim is not) | If the kill was a one-seed artifact it contradicts the project's "calibrate against the anchor" discipline | days |
| **NEXT** | Add an `_is_duplicate` guard + a "seeds surviving to gen-0" log to seed injection | The real latent risk (opposite of the reported one): duplicate seeds waste scarce gen-0 budget; the log would've made the carryover check a 2-minute job | hours |
| **LATER** | If GE stays uncorrelated with agent depth: pilot **MAP-Elites / Quality-Diversity** (behavioral descriptors + GE per-cell). Single-objective GE-greedy + hash-dedup is the textbook recipe for collapse onto a local optimum | Known failure mode, known fix; directly targets "evolution barely compounds" | weeks |
| **LATER** | Pilot a **bigger / connection-relevant board** (larger grid axis, hex/degree-6) and make the influence field enter win logic; check whether GE can even exceed 0.20 there | R8-replay teams' core finding: depth is gated by board size + decorative influence. Tightening the ruler can't raise a substrate-limited ceiling | weeks |
| **LATER** | Tidy repo root (78 root `.py`, 19 root `test_*.py`, 34 root DBs ≈1.2 GB) into `helpers/ tests/ dbs/` | Pure hygiene; lowers the cost of every R22 edit and search | hours |

## 7. Pre-committed decision rule (lock before reading the eval)

- **KEEP ITERATING (launch R22 evolution)** — only if the R21 eval produces **≥1 game Overall > 5.0**, *or* the cross-run agent mean rises **>1 rubric-SD above R19's 4.375**. Then R22 uses the *denoising* fix (more eval samples), **not** the convergence filter; reinstate `planning_horizon` only if its A/B artifact verifies the one-seed-kill claim.
- **PIVOT (change substrate/representation + Quality-Diversity)** — if the eval top game is **< 5.0 AND G6 (R8-revival) fails**. The pivot is **bigger/connection-relevant boards + influence-in-win-logic + MAP-Elites**, **not** MCTS-over-the-same-GE. (The R8 replay already retired the original G7 "MCTS pivot": MCTS was only justified if the agent-eval validator were suspect — it isn't; range 2.5 across 5 teams is the project's tightest convergence. MCTS over the same misaligned GE is the same loss with a different optimizer.) The half-built `experiments/mcts_phase1/` spike already showed no stability win (slope σ 0.04–0.09, same as GE) — don't rebuild it.
- **DECLARE SATURATION (stop iterating this grammar)** — if **two consecutive** eval campaigns under the stable R20+ rubric produce **no game > 5.0 AND no >1-SD rise**. At that point the rule-grammar + GE-evolution regime is empirically saturated; the open question becomes "change the substrate/metric or stop," not "tune it more."

**Throughline:** aigame has earned the right to trust its own measurements. The next honest move is to *use* that trust — run the one experiment that touches the goal — rather than spend another week making an already-trusted, non-predictive proxy slightly sharper.

---

### Appendix — key files
- This analysis: `analysis_post_r21.md`
- Probe B: `experiments/r21_variance_probe/probe_b.py` + `PROBE_B_RESULTS.md`
- R21 report (superseded re: R22 implications): `evaluation_report_run21.md`
- Finalization data: `experiments/r21_finalization/{menger,carpet,grid}_{per_run.csv,summary.md}`
- GE composite: `metrics/scoring.py:440-481`; competence factor: `scoring.py:301-311`
- Seed injection / dedup: `evolution/loop.py:121-160`
- Config knobs: `config.py:46` (`num_independent_runs=3`), `config.py:47` (`eval_episodes=50`), `config.py:59` (`planning_horizon_weight=0.0`)
- R8 replay (substrate-limit evidence): `evaluations/r8_replay/SUMMARY.md`
