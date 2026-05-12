# R21 plan v1 — focusing run on R20+R20.5 lessons

**Status**: drafted 2026-05-11, post-R20.5 close-out. R20+R20.5 head `a30e71a` pushed. Refined 2026-05-11 (same day) after a Plan-agent second-opinion pass surfaced 12 issues; user-decided judgment calls applied (S5 α=1.0, NUM_RERUNS=20, substrate set held, G2 threshold >5.0 held). Pre-launch blockers below.

**Verified 2026-05-11**: codebase claims fact-checked — `evolution/loop.py` elite carry-over at lines 204–206 (S5 target); `game_engine/game_def_v2.py:62` has `pie_rule: bool = False`; `game_engine/engine_v2.py:967` is `_check_threshold` (Z1 briefing fix premise holds); `metrics/scoring.py` has `GoEssenceScorer` with rule_simplicity / strategic_depth / strategic_diversity / composite_score — S2 will add planning-horizon alongside via a new `metrics/inference_probe.py`; `training/trainer.py:427` produces logits transiently in the PPO update minibatch and does not persist them (S2 implementation premise — fresh inference pass required, not a free read); `experiments/r20_finalization/finalize_champions.py:61` has `NUM_RERUNS = 5` (S6 bumps to 20); commit `ac9e642` touches operators_v2.py + generator_v2.py + loop.py + test_pie_rule.py (S3 premise holds). No `canonical_blob` / `canonical_hash` exists in the codebase yet — S1a is a new addition with spec under § S1a. `experiments/r21_seeds/` and `experiments/r21_finalization/` don't exist yet — Z2/Z3/S1b/S6 will create them.

**Hypothesis (load-bearing)**: R20+R20.5 generated four reusable signals (depth-vs-GE disagreement, byte-identical / functional-equivalence triples, elite-carryover bias, residual mirror seat bias after pie). R21 is a **focusing run, not a breadth run**: tighten the scoring stack and the slate-selection stack so a smaller, dedup-cleaned eval can produce a defensible G2-clearance (> 5.0 agent-team eval) rather than R20's tied-at-4.80 ceiling.

R21 is a **stack-tuning round**, not a substrate-comparator round. Substrate set is held to R20's three; the differentiators are S1–S6 below.

---

## What changed since R20_plan.md

| Signal | R20 / R20.5 evidence | R21 response |
|---|---|---|
| Byte-identical triple in slate | R20 menger: 3 of 5 slate games share SHA-256 rule blob | S1a — semantic canonical-blob dedup before slate-build |
| Functional-equivalence triple | R20.5 G4: 3 distinct rule blobs → identical (sampled_p1_wr, sampled_len) | S1b — equilibrium-fingerprint dedup at slate-build |
| GE-rank vs eval-rank disagreement | R20 agent eval: depth-record game +5 ranks vs GE; pie-only game +5 ranks | S2 — planning-horizon term added to GE composite |
| Mirror seat bias not fully neutralised | R20.5 G4: 3/5 PASS, 2/5 FAIL by 0.03–0.04 even with pie | S4 — komi (asymmetric scoring) as secondary balancing mechanism |
| Production GE biased upward ~0.11 | R20 S3 Δ −0.119; R20.5 Δ −0.110 confirms | S5 — elite re-evaluation with held-out PPO seeds per gen |
| σ < 0.04 target missed | R20 S3: 1/9 clear; R20.5: 1/3 clear | S6 — NUM_RERUNS 5 → 12 |
| R8-revival failed by GE; team-1 reframed | R20 grid `fcedbc14043d` = "R8 minus connection-win"; 4-pt gap is in win condition | S7 — restore connection-win for grid + custodian seeds (with pie active) |
| Calibration converged tighter than R19 | R20 production teams 3.71 ± 0.04 across 4 indep campaigns | S8 — keep R17 + R19 anchor reads at session start (no change) |
| Briefing inaccuracy | team-1: briefing_grid_fcedbc14043d.md target_dimension_p2 claim wrong; engine_v2.py:967 mirror-sum unconditional | Z1 — briefing fix (15 min) |

---

## Substrate set

Held to R20's three. No new substrates in R21.

| # | substrate | dim | active cells | role |
|---|-----------|----:|-------------:|------|
| 1 | menger | 2.727 | 400 | **tune-not-search**: fix `outnumber-2 + influence(r=1) + threshold-race` family; sweep within (threshold, propagation-decay, max-turns) |
| 2 | carpet | 1.893 | 64 | **retain-not-explore**: anchor on `625bfc1f3f49` (R20's only above-R19 result, 4.70) + explore variations within pie + r=2 + outnumber-2 family |
| 3 | grid (axis 9) | 2.000 | 81 | **restore-connection**: re-seed R8 family `custodian-1/2 + connection + pie` (team-1's "R8 minus connection-win" finding — 4-pt gap is in win condition, not substrate/capture) |

**Deferred to R22+** (no R21 hypothesis): hexaflake, higher-axis 3D (menger axis=27, dim 2.5–2.9 scan), vicsek/triangle revival, OpenSpiel migration, hybrid-action restoration.

---

## Seed pool design

3 substrates, each with a tight purpose-built pool (not the 4-rule-family matrix R20 used).

### Menger — tune-not-search

Fix family to `outnumber-2 + influence(r=1) + threshold-race + pie`. Sweep within:

| dim | values |
|---|---|
| threshold | {30, 40, 50, 60} (R20 winners clustered around 57.97 — sweep both sides) |
| propagation_decay | {0.5, 0.7, 1.0} |
| max_turns | {100, 150, 200} |

Cartesian product = 36 seeds → smoke filter → ~15–20 surviving seeds. Pop 15, gens 4.

Carry-over anchor: `a6385db22c0b` (R20 S3 top, 15-seed mean 0.241) and `5f5c72e15220` (depth record, eval mean 4.80) — re-evaluated under R21 stack (S5 elite re-eval, S2 planning-horizon scoring) before they count as fitness anchors.

### Carpet — retain-not-explore

Anchor seed: `625bfc1f3f49` exact (the only R20 above-R19 result). Add 6 sibling seeds varying parameters within the `outnumber-2 + influence(r=2) + threshold-race + pie` family — vary threshold ∈ {25, 30, 35}, propagation_decay ∈ {0.5, 0.7}. Pop 15, gens 5.

No connection-win seeds on carpet. R20's negative finding holds: connection on 64 active cells doesn't get off the ground regardless of stack.

### Grid — restore-connection (R8-revival v2)

Per team-1's "R8 minus connection-win" finding — the 4-pt R8→R20-grid gap is in the win condition. R21 grid restores connection-win with pie now active (which R8 didn't have and the R20 pie-bug prevented from testing).

| ID | Family | Rationale |
|----|--------|-----------|
| G1 | custodian-1 + connection + pie | R8 exact + pie (which R20 attempted but bug-zeroed on grid) |
| G2 | custodian-2 + connection + pie | Heavier capture × R8 win condition |
| G3 | outnumber-2 + connection + pie | R20's working capture × R8's win condition |
| G4 | custodian-1 + threshold-race + pie | R20 grid winner (`fcedbc14043d`-style) — head-to-head anchor |

Pop 15, gens 5. G1 is the load-bearing seed for R21's R8-revival v2 verdict; G4 is the head-to-head anchor.

---

## Stack additions (R21)

### S1 — Functional rule-blob dedup (load-bearing, NEW)

Two-stage. **Stage A is cheap and runs during evolution; Stage B is moderate and runs at slate-build time.** Distribution-fingerprint dedup (multi-seed, ~21 hr) is rejected — that's what S3 already produces; using it as a dedup gate would double-count compute.

**S1a — Semantic canonical-blob dedup (during evolution)**

- New: `game_engine/game_def_v2.py:canonical_blob()` — produces a normalized byte string per the canonical-form spec below.
- Hash the canonical blob; reject any candidate in `evolution/loop.py` whose canonical hash matches an existing scored game in the run DB.
- Catches R20's byte-identical-trio AND structurally-equivalent reorderings.
- Cost: O(1) hash lookup per candidate. No measurable wall-clock overhead.

**Canonical-form spec** (precise enough to implement):
- (a) sort rule list by `(rule_type, parameter_tuple_lex_order)`;
- (b) round all float parameters to 6 decimals — keeps `57.97` distinct from `57.99` but collapses ±1e-7 crossover blend-drift;
- (c) emit JSON with `sort_keys=True`;
- (d) **include**: capture rule + params, win condition + params, topology, axis_size, max_turns, propagation_decay, `pie_rule`, `komi_p2` (post-S4);
- (e) **exclude**: `game_id`, `parent_ids`, `generation`, `score_history`, ELO, any per-run scoring artefact.

**Test fixture** (`tests/test_canonical_blob.py`): 3 hand-crafted near-duplicate cases must yield identical canonical hashes — (i) same content, different rule-order; (ii) same content, float drift ±1e-7; (iii) same content, dict-key reordering. Plus one R20 byte-identical-trio member as positive control. Without this fixture S1a is unverified beyond the trivial byte-identical case.

**S1b — Equilibrium-fingerprint dedup (at slate-build)**

- New: `experiments/r21_finalization/slate_select.py` — for each top-K candidate, run a single PPO smoke (3000 ep, seed 42) + sampled-trained mirror eval (n=200, same protocol as R20.5 G4 driver). Hash `(round(sampled_p1_wr, 1), round(sampled_len, 1), round(greedy_p1_wr, 1))`. Drop duplicates; pull the next-ranked unique fingerprint.
- Catches R20.5's functional-equivalence trio (3 rule blobs → identical trained-policy stats).
- Cost: one PPO smoke per slate candidate ≈ 4 min/game × top-10 = ~40 min serial.

**Decision: Stage A + Stage B both required.** Stage A alone misses R20.5's case; Stage B alone wastes evolution compute on near-duplicates. Distribution-fingerprint dedup deferred (overlaps S3 output).

### S2 — Planning-horizon term in GE (NEW component)

team-3 + team-4 finding: depth metric over-rewards game length and strategic-diversity; under-rewards genuine planning depth. Proposed metric: per-ply equity gap between 1st-best and 2nd-best legal moves, averaged across PPO mainline self-play games.

- New: `metrics/inference_probe.py:planning_horizon_from_rollouts(game, trained_agent, n_rollouts=20)`. Loads the trained agent, replays N self-play rollouts, computes softmax over legal moves per ply (legal-move-mask applied before softmax), returns top1 − top2 gap averaged across plies and rollouts. **Logits are not persisted by `training/trainer.py` (verified at `trainer.py:427` — transient inside the PPO update minibatch; only `log_probs` for the selected action plus learning curves are stored).** This is a fresh inference pass, not a free read of trainer state. Wire the result into `metrics/scoring.py:GoEssenceScorer` as a new component alongside `strategic_depth` / `strategic_diversity` / `rule_simplicity`.
- Cost: ~1 min/game × 7 for the R20 A/B re-score; ~1 min/game × pop 15 × 4 gens × 3 substrates ≈ 3 hr added across the run, integrated into the per-game scoring path.
- Add `planning_horizon_weight` to `config.py` (alongside existing `depth_weight`, `diversity_weight`, `simplicity_weight`).
- **Initial weighting: `w_planning = w_depth / 2`.** Rationale: depth is the better-understood signal; planning-horizon is auxiliary discrimination. Refine after A/B.
- **A/B calibration step (pre-launch)**: re-score R20 slate (7 games) under planning-horizon-augmented GE. Goals:
  - Byte-identical trio (`a6385db22c0b` / `b160b1f55378` / `d1dbc6568fc7`) compress to within Δ < 0.05 of each other on new GE.
  - Depth record `5f5c72e15220` (agent rank 1) and pie game `625bfc1f3f49` (agent rank 2) remain top-2 on new GE.
  - If both pass: lock weighting. If not: bisect `w_planning` and retry.

### S3 — Pie rule universal (NO CODE CHANGE)

Commit `ac9e642` (R20 mid-run fix) already propagates `pie_rule` through all 4 crossover operators + immigrant generator. R21 seed builder defaults `pie_rule=True` for all 12+ seeds. No fallback path; no "pie=False" seeds.

### S4 — Komi-style asymmetric scoring (NEW, FAIL-case rescue)

R20.5 G4: pie corrects 60–80% of P1 rush advantage but 2/5 games (top GE + lone custodian) still fail < 0.10 by 0.03–0.04. Pie is a one-move correction at the start; on games where structural P1 advantage is large, one swap can't cancel it.

**Decision: komi (asymmetric scoring), not handicap moves or ko-style restriction.**

- Komi is cheapest: single config field on game definition, applied at win-condition check time.
- Handicap moves and ko-style restriction touch engine action-generation logic — significant scope; defer to R22 if komi alone proves insufficient.

Implementation:
- New: `game_engine/game_def_v2.py` field `komi_p2: float = 0.0` — bonus added to P2's effective threshold-score / territory count in `_check_threshold` and `_check_territory`.
- Auto-calibration: post-evolution, for each top-K candidate whose post-pie G4 bias > 0.10, train fresh PPO at each of `komi ∈ {0.05, 0.10, 0.15, 0.20, 0.25, 0.30}` and pick the smallest komi whose sampled G4 bias < 0.10 with ≥ 2σ margin (eval n=200 has σ ≈ 0.035, so margin ≥ 0.07). If no value passes → game is structurally rush-broken, marked FAIL on G3. **Fixed grid, not binary search** — binary search oscillates under noisy bias estimates and each komi requires a fresh PPO training run anyway (otherwise the eval is misspecified, since komi changes the equilibrium).
- Cost: 6 komi × ~5 min PPO × top-K=10 candidates ≈ **~5 hr post-evolution** (the original "30 min binary search" estimate was 8× under-budget).
- Stored in DB alongside the rule blob; treated as part of the game definition for slate selection (and included in the S1a canonical blob).

### S5 — Elite re-evaluation with held-out PPO seeds (NEW algorithmic fix)

Root-cause fix for R20+R20.5's confirmed ~0.11 upward bias in production GE. R20 implications item 7 suggested either fix-algorithm-or-discount; we pick fix.

**Shipped design (revised from plan-as-written):** the surgical site is `run.py`, not `evolution/loop.py`. Under the current architecture, elites are already re-scored every generation by run.py's `for game in population: train_and_evaluate_game(...)` loop — the bug is that R18's `deterministic_run_seed(game_id, run_idx)` is gen-independent, so re-scoring reproduces the same lucky-elite GE on every pass. Selection then locks in lucky elites. The fix is a seed-swap at scoring time:

- New `run.py:carryover_run_seed(game_id, generation, run_idx)` — MD5(`f"{game_id}:gen{generation}:{run_idx}"`) — deliberately gen-dependent. Inverse of R18's per-game stable seed.
- run.py's main scoring loop detects carry-over elites via `is_carryover = game.metadata.get("generation", gen) < gen` and switches to `carryover_run_seed` for both the primary PPO run and the C2 extras (`num_independent_runs=3`). New games (mutants / crossovers / immigrants / seed games at gen 0) keep R18's stable `deterministic_run_seed`.
- `train_and_evaluate_game` gains an optional `generation` parameter that threads through to `_train_and_evaluate_game_inner` for the extras-run seed selection. Default `None` preserves R18 behaviour.
- **Pure replace** (α=1.0): the fresh score overwrites `scores_map[game_id]` outright. No EMA blending. EMA α=0.5 only attenuates the +0.11 bias by 50% (residual ~+0.055 competes with S6's σ≈0.045); pure replace is the root-cause fix and S6's 20-rerun finalization handles the variance increase.

**ThreadPool concurrency descoped.** The plan's claim that wrapping the elite re-eval in `concurrent.futures.ThreadPoolExecutor(max_workers=5)` would save ~5 hr/substrate assumed elite re-eval is *extra* work on top of population scoring. Under the current architecture, it isn't — every game (including elites) is already scored once per gen. The seed-swap adds zero PPO runs vs the no-fix baseline; it only changes which seed is used. If population scoring is parallelised later, elites get the benefit automatically. No race conditions to guard.

Cost: zero extra PPO runs (pure substitution of seed function). Compared to the plan's "180–225 extra PPO runs" estimate, this is a strict simplification.

Tests: `test_elite_reeval.py` (8 cases, all PASS) — `deterministic_run_seed` is gen-independent (R18 regression); `carryover_run_seed` is gen-dependent + deterministic + varies across run_idx and game_id; the two schemes diverge at gen ≥ 1; the carry-over detection predicate handles seed-game / mutant / surviving-elite / missing-metadata layouts; all run_idx slots (C2 multi-seed) vary by gen.

### S6 — Rerun budget: 5 → 20 (S3 finalization)

R20 S3 + R20.5 both confirmed 5 reruns produce σ too wide to rank top games (1/9 and 1/3 clear σ < 0.04).

- `experiments/r21_finalization/finalize_champions.py:NUM_RERUNS = 20` (was 5). With σ ∝ 1/√n, 5→20 reruns brings expected σ from 0.09 to **~0.045** — within sight of the 0.04 target. Reaching σ < 0.04 strictly would require ~25 reruns; 20 is the marginal compute / credibility sweet spot.
- Compute: 20 reruns × 9 games = 26.7 hr serial at R20's ~9 min/rerun pace. **Add parallelization** — 3 concurrent rerun processes (one per substrate) brings to **~9 hr wall**.
- Driver carry-over: structure is otherwise R20's `finalize_champions.py` — only constant + concurrency wrapper change.

### S7 — Substrate handling: tune / retain / restore-connection

Per § Seed pool design above. R21 doesn't change `evolution/loop.py` substrate handling — just the seed builder per substrate.

### S8 — Calibration anchors (NO CHANGE)

R20 production teams converged 3.71 ± 0.04 across 4 independent campaigns — tightest of any aigame run. The R17-verdict-read-at-session-start countermeasure works. R21 keeps it verbatim. Anchors:
- R8 Connection Go: 8.0
- R17 champion (`44f6630277b3`): 4.14
- R19 menger top (`1f9191b5d4e6`): 4.8
- R20 menger top (`5f5c72e15220`): 4.80 (depth record)
- R20 carpet top (`625bfc1f3f49`): 4.70 (only pie)

---

## Pre-launch blockers — STATUS

| ID | Blocker | Status | Owner-session(s) |
|----|---------|--------|------------------|
| S1a | Semantic canonical-blob dedup | **DONE** 2026-05-11 (commit `86b1a22`) — 11 tests | — |
| S1b | Equilibrium-fingerprint slate dedup | **DONE** 2026-05-12 — `experiments/r21_finalization/slate_select.py`; 10 tests; auto-calibration deferred (per-candidate PPO ~40 min at launch) | — / ~40 min compute at launch |
| S2 | Planning-horizon scoring component + A/B on R20 slate | **DONE (impl)** 2026-05-11 (commit `50fa235`) — 8 tests; A/B re-score on R20 slate **DEFERRED** to pre-launch (user decision) | — / 1.5–2 hr compute at launch |
| S4 | Komi field + auto-calibration logic | **DONE (field+engine)** 2026-05-11 (commit `f8541f9`) — 9 tests; auto-calibration driver **DEFERRED** to pre-launch (user decision) | — / 1 session + ~5 hr compute at launch |
| S5 | Elite re-eval logic + tests | **DONE** 2026-05-12 (commit `c622c05`) — shipped as `run.py` seed-swap, not loop.py ThreadPool; 8 tests | — |
| S6 | NUM_RERUNS=20 + parallel finalization driver | NOT STARTED | 0.5 session |
| Z1 | Briefing fix (`briefing_grid_fcedbc14043d.md`) | **DONE** 2026-05-12 (commit `f295279`) | — |
| Z2 | R21 seed builder (3 substrates) | **DONE** 2026-05-12 (commit pending) — `experiments/r21_seeds/build_seeds.py` emits 46 seeds (36 menger sweep + 6 carpet siblings + 4 grid families); 15 tests; smoke filter re-uses existing harness at launch | — |
| Z3 | R21 driver + launch script | **DONE** 2026-05-12 (commit pending) — `experiments/r21_driver/{run_r21_substrate.py, launch_r21.sh}`; per-substrate config matches § Run config; 13 tests | — |
| Z4 | Half-run smoke check — `launch_r21.sh` gen-2 GE-floor gate per substrate; abort if peak GE < 0.05 at end of gen 2 (catches S5 / S1a regressions before 24+ hr is sunk) | **DONE** 2026-05-12 (commit pending) — `experiments/r21_driver/gen2_smoke_gate.py` monitor + launch_r21.sh wiring; 13 tests incl. 2 end-to-end | — |

**All blockers shipped 2026-05-11/12.** R21 is ready to launch. Remaining work is pre-launch compute (S2 A/B re-score ~2 hr, S4 komi auto-cal driver build + ~5 hr, optional smoke filter on the 36 menger seeds) and the actual evolution run.

---

## Run config (per substrate)

| Substrate | pop | gens | budget/ep | est. wall-clock |
|-----------|----:|-----:|----------:|----------------:|
| menger | 15 | 4 | 10000 | ~15 hr |
| carpet | 15 | 5 | 15000 | ~13 hr |
| grid | 15 | 5 | 10000 | ~3 hr |

Total R21 evolution: **~31 hr wall-clock** (menger longest, parallel via `launch_r21.sh`). S5 ships as a seed-swap with zero extra PPO runs (vs the plan-as-written's ~5-7 hr for ThreadPool elite re-eval), so each substrate's evolution wall is back to the no-elite-reeval baseline.

Post-evolution:
- S1b equilibrium-fingerprint dedup: ~40 min
- S4 komi grid auto-calibration on slate FAIL-case games: ~5 hr
- S3 finalization at 20 reruns × parallel 3: ~9 hr
- Total post-evolution: ~15 hr

**Grand total: ~46 hr wall-clock.** Comfortably below R20's 65 hr — R21 remains a focusing run, not a breadth run, and the S5 simplification reclaims ~10 hr from the plan-as-written.

---

## Eval style — agent-team verdict campaign

Same 5-team protocol as R20 (1 pilot + 4 production teams). Slate size depends on S1b dedup output — target **6 unique kernels** after dedup. If R21 generates fewer than 6 distinct top games, drop the slate to match (don't pad with near-duplicates).

Slate selection rule (under S1 enforcement):
- 2 menger (post-S1 dedup top-2 by augmented GE)
- 1 menger (top-1 by planning-horizon component alone — surfaces S2 disagreement signal)
- 1 carpet (top-1; expected `625bfc1f3f49` variant or `625bfc1f3f49` itself)
- 1 grid × R8 family (G1 connection + custodian-1 + pie if it survived evolution; else best surviving connection-win)
- 1 grid × R20-family anchor (top threshold-race grid, for head-to-head with the connection-win seed)

Calibration anchors per S8 mandated at session start for every team.

---

## R21 success criteria

| Goal | Metric | Threshold | Falsifies if missed |
|------|--------|-----------|---------------------|
| **G1** Beat R19 ceiling | Best R21 game agent-eval mean | **> 5.0** | R20 G2 missed by 0.2; if R21 also misses, menger ceiling at ~5.0 is a real plateau under current rule families and R22 must shift framing (direct/MCTS search per `feedback_check_external_methods.md`) |
| **G2** Slate dedup | Fraction of slate that is structurally unique kernels | **≥ 5/6 unique** (vs R20's 4/7) | Tests S1 effectiveness; if FAILS, S1b's equilibrium-fingerprint check needs a tighter precision (e.g. 2-decimal vs 1-decimal) |
| **G3** Mirror balance under R21 stack | All R21 slate games clear G4 mirror seat bias < 0.10 (post-komi) | **all PASS** | Tests S4 effectiveness; if FAILS on top game, structural P1 rush is beyond komi's reach and ko/handicap moves move up to R22 |
| **G4** Planning-horizon discriminates pseudo-distinct games | On R20 slate A/B: byte-identical trio compresses to Δ < 0.05 of each other on augmented GE | **PASS** | Tests S2 calibration; if FAILS, planning-horizon weighting needs increase or the metric is mis-specified |
| **G5** Honest σ on top games | 12-rerun σ < 0.05 on top-3 per substrate | **all PASS** | Tests S5 + S6 jointly; if FAILS, either rerun budget still too small (rare — would need ~25) or elite re-eval not fully fixing carryover bias |
| **G6** R8-revival v2 (R21-specific) | Grid G1 seed (custodian-1 + connection + pie) agent-eval | **≥ 5.0** | team-1's "R8 minus connection-win = 4pt gap" hypothesis. If FAILS, the R8 ceiling is unreachable via evolutionary search and R22 must shift to direct/MCTS search per `feedback_check_external_methods.md` |
| **G7** Falsification pre-commitment | If G1, G2, and G6 all FAIL | **R22 framing is locked** to direct/MCTS search (per `feedback_check_external_methods.md`); not another evolutionary iteration with the current framing | Consulted before any R22 scoping. Pre-commitment, not a guideline — makes R21 a real test rather than an open-ended pursuit |

**G1 and G6 are load-bearing.** G1 is the cross-run improvement test (R20 G2 retry); G6 is the final test of team-1's reframed R8-revival hypothesis. Failing both signals that evolutionary search has saturated and R22 needs an architectural shift, not another iteration. **G7 makes that pre-commitment explicit.**

---

## Decisions resolved 2026-05-11

1. **Functional dedup: two-stage (semantic + equilibrium-fingerprint), not distribution-fingerprint.** Distribution-fingerprint duplicates S3 compute; semantic alone misses R20.5; equilibrium alone wastes evolution compute on near-duplicates. Stage A during evolution + Stage B at slate-build is the right pipeline placement.
2. **Planning-horizon weight = w_depth / 2 starting.** Refine after A/B on R20 slate. Don't replace depth; augment it.
3. **Komi (asymmetric scoring), not handicap moves or ko-style restriction.** Cheapest implementation, single-field game-def change. Handicap and ko deferred to R22 if komi proves insufficient.
4. **Elite re-evaluation as algorithmic fix (S5), not "accept and discount".** Fixes the root cause; accept-and-discount carries the bias forward indefinitely.
5. **NUM_RERUNS = 20.** See decision #10 below for the refined value; the earlier "12 not 15" framing under-committed relative to parallelization headroom.
6. **R21 substrate set = R20 substrate set.** Focused run; no new substrates. Hexaflake / higher-axis 3D / vicsek-triangle revival deferred to R22.
7. **Grid restores connection-win (R8-revival v2).** team-1's "R8 minus connection-win" finding overrides R20's blanket "R8 family doesn't generalize" — the failure was win-condition-specific on grid + custodian, not family-wide.
8. **Carpet does NOT restore connection-win.** R20's negative finding (3 of 74 games nonzero, none connection-win) holds — connection on 64 active cells fails structurally.
9. **S5 elite re-eval: pure replace (α=1.0), not EMA blending.** EMA α=0.5 only attenuates the +0.11 carryover bias by 50% (steady-state residual ~+0.055, which competes with S6's σ ≈ 0.045 target). Pure replace eliminates the bias as a root-cause fix; the variance increase is handled by S6's 20-rerun finalization.
10. **NUM_RERUNS = 20 (not 12 or 15).** 3.6 hr extra wall-clock over the 12-rerun option buys σ ≈ 0.045 vs σ ≈ 0.058 — within sight of the 0.04 G5 target. Lower budgets under-commit relative to the parallelization headroom.
11. **S4 komi via fixed grid, not binary search.** Avoids oscillation under noisy bias estimates (eval σ ≈ 0.035 is on the order of the search target). Cost rises from a quoted 30 min to a real ~5 hr but is bounded, predictable, and convergent.
12. **G7 falsification clause is pre-committed.** If G1 + G2 + G6 all fail, R22 framing is locked to direct/MCTS search — no further evolutionary iterations with the current framing. Forces R21 to be a real test rather than an open-ended pursuit.

---

## Explicitly deferred to R22+

- Hexaflake substrate
- Higher-axis 3D substrates (menger axis=27, dim 2.5–2.9 scan)
- Vicsek / triangle revival (still need training-budget probe)
- Direct/MCTS-augmented search as canonical answer to R8-revival ceiling (per `feedback_check_external_methods.md` — surface as R22 option **if and only if G1+G6 both fail** in R21; don't pre-commit)
- Handicap moves / ko-style restriction (only if S4 komi proves insufficient on G3)
- Hybrid action restoration. R17/R18/R19/R20 all confirmed under the prior penalty calibration that hybrid actions go unused. R20's depth-vs-planning agent-team disagreement (team-3 + team-4: outnumber-3 captures are vestigial; action-space narrowness suppresses planning) suggests hybrid action may still be a live hypothesis under a different penalty calibration — but R21 is a focusing run, not a substrate / action-space breadth run. Revisit in R22 if S2 planning-horizon scoring shows action-space variety correlates with the new metric.
- OpenSpiel migration (R20 plan confirmed: no stability win over current stack)
- Distribution-fingerprint dedup as a slate gate (overlaps S3; revisit if S1b fingerprint precision proves wrong)

---

## What R21 does NOT change

- C1 deterministic seeds, C2 multi-seed averaging, D1 hybrid penalty — unchanged.
- B1 substrate invariants — unchanged.
- S1/S2/S3/S4 from R20 plan numbering: **note R21 reuses S-prefix differently**. R20's S1 (pie) is shipped as `ac9e642`; R20's S2 (two-tier smoke) is unchanged; R20's S3 (finalization) is rebuilt as R21's S6 with bigger budget.
- 5-team agent-eval campaign protocol — unchanged. Only slate selection rule and seed pool design are new.
- Calibration anchors and session-start R17 read — unchanged.

---

## Sequencing summary

1. **Z1** briefing fix (15 min, can land anytime)
2. **S1a** semantic canonical-blob dedup + tests (1 session)
3. **S2** planning-horizon scoring component + A/B re-score of R20 slate (1–2 sessions, parallel with S1a)
4. **S4** komi field on game def + auto-calibration (1 session)
5. **S5** elite re-eval in `evolution/loop.py` + tests (1 session)
6. **S6** NUM_RERUNS bump + parallel finalization driver (1 session)
7. **S1b** equilibrium-fingerprint slate dedup (1 session, post-S1a)
8. **Z2** R21 seed builder — menger sweep + carpet variants + grid R8-revival v2 (1 session, post-S1a + S4)
9. **Z3** R21 driver + launch script (1 session, post-Z2)
10. R21 evolution launch (~41 hr parallel wall)
11. S1b slate dedup + S4 komi calibration (~70 min)
12. R21 S3 finalization at 12 reruns × 3 parallel (~6 hr)
13. R21 agent-team eval campaign (~1 session)
14. R21 evaluation report + R21_postmortem

Critical path: S1a → Z2 → Z3 → evolution → finalization → eval. **~8–9 implementation sessions before launch** (S1a + S2 + S4 + S5 have shipped 2026-05-11/12; remaining sessions are S1b + S6 + Z1/Z2/Z3/Z4), accounting for:
- S1a 1.5 sessions (canonical-form spec + impl + test fixture per § S1a)
- S2 2 sessions (inference probe + scoring component + A/B re-score)
- S5 1 session (run.py seed-swap + tests — ThreadPool descoped, see § S5)
- S6 0.5 session (constant + parallelization wrapper)
- S4 1 session (komi field + fixed-grid auto-calibration)
- S1b 1 session
- Z1 + Z4 30 min combined
- Z2 1 session
- Z3 1 session

The earlier "~7 session" estimate assumed everything landed on the first try, ignored the S2 inference-probe code path, and didn't price in S5 thread-pool work.
