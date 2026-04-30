# R19 Plan v3 — drafted 2026-04-30

Supersedes R18-plan-v2 (in `project_aigame_run15_plan.md` memory). Builds
on the 4 patches that landed between R18 and R19 (C1, C2, D1, eval-report
addendum) and the substrate evidence from Phase B rescue.

## TL;DR

1. **R19 is a champion run on two substrates, not a comparator** — menger
   axis-9 + carpet axis-9, with grid as a tiny noise-floor control.
2. **Status-quo R18 shape, with one cheap free bump**: pop=30, 8 gens,
   10k eps on menger; **15k eps on carpet** (where Phase A showed PPO
   was undertrained). Grid control: pop=20, 2 gens, 10k eps.
3. **C1+C2+D1 are now live in `evaluate_game`** — scoring is deterministic
   per game, multi-seed averaged, hybrid-action penalised. R19 is the
   first end-to-end test that those three landed correctly.
4. **Wall-clock estimate**: ~30 hr (parallel substrate launch; menger is
   the bottleneck, same as R18). Carpet finishes in ~4.5hr; grid in <1hr.
5. **Eval**: 5-team human eval × 6 games (3 menger top + 3 carpet top),
   playability-gated.

## What changed since R18 plan v2

| Change | When | Commit | What it does for R19 |
|--------|------|--------|----------------------|
| C1 deterministic `run_seed = md5(game_id)` | 2026-04-30 | `addda54` | Same game scored twice gives the same number. Removes generation-indexed PPO seed noise. |
| C2 multi-seed averaging in primary GE | 2026-04-30 | `a843d0a` | All `num_independent_runs=3` PPO runs feed the headline GE. Cuts per-game variance ~√3. |
| Phase A volatility analysis | 2026-04-30 | `a6ab867` | Established noise floor: menger top games std=0.014 (RELIABLE), carpet/vicsek/grid 0.10-0.17 (NOISY). |
| Phase B rescue (no retraining) | 2026-04-30 | `a843d0a` | Carpet champion underestimated 2.1× (0.1633→0.3465); menger holds (0.3368→0.2689). Promoted carpet to R19 candidate. |
| Eval report Phase B addendum | 2026-04-30 | `2d3b584` | Annotated stale claims; renumbered blockers (C1/C2 = scoring; D1/D2 = evolution-design); revised R19 candidate set. |
| D1 hybrid-action ban | 2026-04-30 | `50baabc` | 0.2× soft-ban on `has_move()` games. R17 22-team + R18 5-substrate evidence: 0% move usage. |

## Goals (testable)

R19 is designed to answer four questions. Each has a falsifiable success
criterion that the eval report should be able to address.

1. **Does the carpet champion's rescued GE survive end-to-end re-evolution?**
   The Phase B 0.3465 number is a math-only re-derivation on R18 data. R19
   is the first chance to see the same composite under live evolution
   with C1+C2 active. Success: a carpet game in R19's final top-3 scores
   ≥ 0.30 on the new pipeline.
2. **Does menger lift above R17's GE rank-1 (0.3773) under the new scoring?**
   R18's stable menger top was 0.3368, rescued to 0.2689. C2 averaging
   means R19 numbers are directly comparable to R17's rank-1. Success:
   R19 menger top-1 ≥ 0.35.
3. **Does D1 actually evict hybrid-action lineages?**
   Hybrid games still appear in random-init populations (~10% of R18
   pop). Under D1 they should disappear by gen 3-4. Success: 0 hybrid
   games in either substrate's gen-7 top-10 by GE.
4. **First substrate-comparable human eval since R17.**
   Get 5-team verdicts on menger top-3 + carpet top-3 = 6 games. Success:
   either substrate produces a game ≥ R17 winner (4.14 mean), OR we
   confirm the GE-vs-human gap noted in R17 still holds.

## Substrate set

| Substrate | Dim | Active cells | Why |
|-----------|-----|--------------|-----|
| Menger axis-9 (3D) | 2.727 | 400 | R18 stable champion (`0f5e931fa3e1`); Phase A reliable; carry over the gen-7 elite as seed |
| Carpet axis-9 (2D) | 1.893 | 64 | Phase B rescue's headline finding (`8776b2026957`, rescued 0.3465); cheap to evolve; benefits most from C2 |
| Grid 16×16 (2D, control) | 2.000 | 256 | Sets noise floor for R19. Phase B grid top-1 was 0.0105 — that's the bar any R19 result must clear to count as signal |

**Dropped from v2**:
- **Vicsek axis-27** — Phase B rescued top-1 0.0238 (still in noise band; substrate-level low-GE verdict unchanged)
- **Triangle axis-32** — Phase B rescued top-1 0.0596; mostly tied at ~10⁻³ across the rest of top-10
- **Menger axis-27** — too expensive (8000 active cells); deferred to R20-track

## Run config (per substrate)

| Substrate | Pop | Gens | Eps/game | Indep runs | Estimated wall-clock |
|-----------|-----|------|----------|------------|----------------------|
| Menger | 30 | 8 | 10000 | 3 | ~30 hr (R18 baseline) |
| Carpet | 30 | 8 | 15000 | 3 | ~4.5 hr (R18 carpet × 1.5) |
| Grid (control) | 20 | 2 | 10000 | 3 | ~30 min |

**Why these numbers:**

- **Menger 10k stays unchanged.** Phase A showed menger top games at
  std=0.014 — already reliable at 10k. C1+C2 will lift the noise floor
  for the rest of the population without needing more compute.
- **Carpet bumped to 15k.** Phase A showed carpet champion's tvr swings
  0.22→1.0 across runs at 10k — clear undertraining signal. 15k is the
  free bump (carpet is 10× faster per game than menger; bump is
  invisible against the menger bottleneck).
- **Pop=30 carried from R18** — actual R18 setting per `launch_r18.sh`
  default. Plan v2's "pop=50" was a memory error. Pop=30 produced
  meaningful evolution; bumping to 50 for R19 would extend menger
  wall-clock to ~50 hr — not justified.
- **Grid control deliberately small** — its job is to confirm the noise
  floor, not to evolve a champion. Pop=20 × 2 gens = 40 game-evals total,
  finishes in <1hr.

## Seed design

R18 used 3 rule combos × 5 substrates = 15 seeds. R19 narrows to 2 evolution
substrates with **8 seeds each** (richer per-substrate diversity), plus
control seeds.

### Menger seeds (8 + 1 carry-over)

5 in dominant family (`* + influence(r=1) + threshold-race`):

| # | Capture | Influence | Win | Notes |
|---|---------|-----------|-----|-------|
| 1 | custodian-2 | r=1 | threshold | match for R18 winner `0f5e931fa3e1` |
| 2 | custodian-1 | r=1 | threshold | thresh-2 ablation |
| 3 | surround | r=1 | threshold | match for R18 peak `f87428258916` |
| 4 | outnumber-2 | r=1 | threshold | cross-substrate (R18 carpet champ family) |
| 5 | none | r=1 | threshold | influence-only ablation |

3 off-family probes:

| # | Combo | Notes |
|---|-------|-------|
| 6 | custodian-2 + territory | Tests "only threshold-race works" claim |
| 7 | surround + connection | R8 Connection Go family |
| 8 | outnumber-2 + threshold(r=2) | Probe radius-2 (R18 vicsek peak used r=3) |

**Carry-over (B-list, not a seed but a gen-0 elite injection)**: copy R18
winner `0f5e931fa3e1` into the gen-0 population so evolution starts at
the known peak, not below it.

### Carpet seeds (8 + 1 carry-over)

5 in dominant family (`* + influence(r=2) + threshold-race`):

| # | Capture | Influence | Win | Notes |
|---|---------|-----------|-----|-------|
| 1 | outnumber-2 | r=2 | threshold | match for R18 winner `8776b2026957` |
| 2 | outnumber-3 | r=2 | threshold | thresh ablation |
| 3 | custodian-2 | r=2 | threshold | cross-substrate (R18 menger family) |
| 4 | surround | r=2 | threshold | tests R18 menger-peak family on 2D |
| 5 | none | r=2 | threshold | influence-only ablation |

3 off-family probes:

| # | Combo | Notes |
|---|-------|-------|
| 6 | outnumber-2 + territory | Tests territory on dense fractal |
| 7 | custodian + connection | R8 family on fractal |
| 8 | outnumber-2 + threshold(r=3) | Probe larger influence radius |

**Carry-over**: R18 winner `8776b2026957` into gen-0 population.

### Grid control seeds (3)

| # | Combo | Notes |
|---|-------|-------|
| 1 | custodian-1 + connection | R8 Connection Go (the all-time human-eval ceiling) |
| 2 | outnumber-2 + influence(r=1) + threshold | Cross-substrate from carpet/menger family |
| 3 | **HYBRID validator**: custodian-1 + connection + place+move | Verifies D1 fires correctly; should score ~0 in DB; never wins selection |

The hybrid validator is the cheapest end-to-end D1 verification we can
build. After grid control finishes, check that:
- Game 3's stored GE has `hybrid_action_penalty=0.2` in the result dict
- Game 3 doesn't appear in any gen-2 top-10
- Phase A-style analysis: 0 hybrid games in final population

## Pre-launch validation checklist

Before launching the ~30hr menger run, verify all 4 patches work
end-to-end. Each item is ~5-30min of work; total ~2hr.

1. **Build R19 seeds** — `experiments/r19_seeds/build_seeds.py` (modify
   from r18 builder; output `experiments/r19_seeds/seeds/<game_id>.json`).
2. **B2 PPO smoke gate on all 19 seeds** — reuse
   `experiments/r18_ppo_smoke/harness.py` with new seed dir. Expected:
   menger c1+c3, carpet c1, grid c1 PASS (consistent with R18's smoke
   filter); the hybrid validator will pass smoke (smoke doesn't see D1)
   but get penalty 0.2 in scoring.
3. **C1 verification** — pick any seed, score it twice via
   `train_and_evaluate_game` in a Python REPL, confirm both scores are
   bit-identical. Catches regression risk.
4. **C2 verification** — score a seed once with `num_independent_runs=3`,
   inspect the DB. `training_runs` should have 3 rows; `scores.go_essence`
   should match the multi-seed averaged composite, not run-0 alone.
5. **D1 verification** — score a hybrid-action game (the grid validator
   seed); inspect: `hybrid_action_penalty=0.2` in scoring's result dict;
   stored GE should be 0.2× what the place-only equivalent scores.
6. **Tiny end-to-end mini-evolution** — `GENS=1 POP=5 BUDGET=200` on
   carpet (cheapest substrate); ~5min. Confirms driver + DB writes +
   logging all clean. Then nuke the test DB before the real run.

Only launch after all 6 items pass.

## Eval protocol

Same shape as R17's 22-team eval but narrower (R17 was over-coverage at
4 games × 22 teams = 88 verdicts; R19 needs depth on the 2 surviving
substrates).

- **Playability gate** (run before eval): forced-win <10 moves OR
  avg_game_length <8 → mark broken; replace with rank+1 from the same
  substrate.
- **Eval set**: top-3 by R19 final-gen GE per substrate = 6 games total.
- **Teams**: 5 per game = 30 verdicts total. Same 1-5 rubric as R17.
- **Cross-substrate balance**: each team plays one menger and one carpet
  game (paired) so substrate effects don't entangle with team effects.
- **Output**: `evaluation_report_run19.md` with per-game mean ± SD,
  per-substrate aggregate, R8/R17/R19 mean comparison, and an explicit
  GE-vs-human disagreement section (R17 found GE over-rewards complexity;
  R19 should test whether that gap narrows under C2).

## Risk register

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| C2 averaging blunts the lucky-run signal that produced R18 menger 0.3368 | Medium — Phase B saw menger drop to 0.2689 already | Acceptable — 0.2689 is still the highest stable end-of-run GE; no action needed |
| Carpet 15k still undertrained (Phase A floor was 10k) | Low | If carpet end-of-run top GE < 0.20, run a one-shot 25k re-eval on the carpet top-3 to disambiguate |
| D1 over-penalises and a genuinely good hybrid game is missed | Very low — R17 evidence is unanimous (0% move use) | If post-eval analysis suggests a hybrid pattern was viable, we have the per-game `hybrid_action_penalty` field to retrospectively un-multiply |
| 30hr menger run interrupted by lid-close (as in R18) | High — happened 2× in R18 | Driver supports checkpointing (`run.py:_save_checkpoint`); resume from latest checkpoint if needed |
| Hybrid validator in grid control accidentally wins (D1 broken) | Very low — D1 has 6 unit tests | Pre-launch checklist item 5 catches this before commit |
| Rule-mutation pulls a place-only game into hybrid mid-evolution and never recovers | Low | D1 is multiplicative not additive; once mutated to place-only, penalty is removed. Lineage doesn't go extinct |

## Wall-clock estimate (corrected)

R18 actual numbers from `logs/run18/{menger,carpet}.log`:

- Menger 8 gens at pop=30, 10k eps: **30.8 hr** (per-gen range 8.4-22.5k sec)
- Carpet 8 gens at pop=30, 10k eps: **3.0 hr** (per-gen range 0.5-2.9k sec)

R19 estimate (parallel substrate launch via `OMP_NUM_THREADS=1`):

| Component | Wall-clock |
|-----------|------------|
| Menger 8 gens × 30 pop × 10k eps (status quo) | ~30 hr |
| Carpet 8 gens × 30 pop × **15k eps** (1.5× bump) | ~4.5 hr |
| Grid control 2 gens × 20 pop × 10k eps | ~0.5 hr |
| **Parallel total (menger bottleneck)** | **~30 hr** |

The carpet budget bump is invisible at the parallel run-level — it costs
~1.5hr of carpet's 4.5hr but menger keeps running anyway. Free quality
upgrade.

**Skipped optimisation footnote**: elite-score caching (deferred per your
call). With C1 deterministic scoring it would be pure waste-saver — 5
elites × 7 carry-over generations = 35 retrain-skipped games out of 240
total per substrate ≈ **15% wall-clock savings** (~4.5 hr off menger).
Adding it later if R19 timing pinches is a 1-2 hr code change to
`run.py:_train_and_evaluate_game_inner`.

## File checklist

Code to land before launch:

- [ ] `experiments/r19_driver/run_r19_substrate.py` — copy from
  `experiments/r18_driver/run_r18_substrate.py`, swap seed dir,
  swap DB suffix, swap default args
- [ ] `experiments/r19_driver/launch_r19.sh` — copy from r18; substrate
  list = `(menger carpet grid_control)`; carpet override BUDGET=15000;
  grid override GENS=2 POP=20
- [ ] `experiments/r19_seeds/build_seeds.py` — generate 19 seeds (8
  menger + 8 carpet + 3 grid), based on `experiments/r18_seeds/
  build_seeds.py` template
- [ ] `experiments/r19_seeds/seeds/*.json` — generated by `build_seeds.py`
- [ ] B2 smoke results documented at
  `experiments/r19_seeds/SMOKE_RESULTS.md`

After-run artifacts:

- [ ] DBs: `genesis_v2_run19_{menger,carpet,grid}.db`
- [ ] Logs: `logs/run19/{menger,carpet,grid}.log`
- [ ] Eval verdicts: `evaluations/run19/`
- [ ] Eval report: `evaluation_report_run19.md`
- [ ] Plot: `plots/run19_top_games_by_substrate.png`

## Decision log (settled)

- ✅ **Substrate set**: menger axis-9 + carpet axis-9 + tiny grid control
  (decided 2026-04-30 from Phase B rescue findings)
- ✅ **Pop / gens**: 30 / 8 (status quo from R18; not bumping to 50)
- ✅ **Budget**: 10k menger / 15k carpet / 10k grid (free carpet bump)
- ✅ **Seed mix**: 5 in-family + 3 off-family per substrate, with R18
  winner carried over as gen-0 elite injection
- ✅ **C1, C2, D1 all shipped** — pre-launch checklist verifies they
  work end-to-end
- ✅ **D2 (triangle 30k probe)**: dropped (no triangle in R19)
- ✅ **Elite-score cache**: skipped (not load-bearing for correctness;
  ~15% compute saver if reconsidered later)
- ✅ **Pie rule**: deferred to R20

## Open decisions (need your call before launch)

1. **Sequential or parallel substrate launch?** R18 ran parallel and the
   menger bottleneck dominated. Parallel is the obvious default — but
   needs a brief CPU benchmark first (one menger gen + one carpet gen
   simultaneously, measure throughput vs sequential) to confirm PPO
   contention isn't worse than expected on this Mac. ~1 hr benchmark.
2. **Hybrid validator seed in grid control?** Recommended (cheapest
   end-to-end D1 verification) but adds 1 of the 3 grid seeds. Skip if
   you want a tighter grid control.
3. **Eval team count**: 5 teams × 6 games = 30 verdicts feels right for
   the carpet+menger comparison without R17's overkill. Confirm.

## Files & references

- This plan: `R19_plan_v3.md` (this file)
- R18 eval report (with Phase B addendum): `evaluation_report_run18.md`
- Phase A: `experiments/r18_volatility/phase_a_results.md`
- Phase B: `experiments/r18_volatility/phase_b_rescue_results.md`
- C1/C2/D1 commits: `addda54`, `a843d0a`, `50baabc`
- Tests: `test_deterministic_run_seed.py`, `test_multiseed_averaging.py`,
  `test_hybrid_action_ban.py`
- R17 reference report: `evaluation_report_run17.md`
- R8 ceiling reference (Connection Go, 8/10 humans): see `SUMMARY.md`
- Project memory: `~/.claude/projects/-Users-jamesbrowne/memory/project_aigame_run15_plan.md`
