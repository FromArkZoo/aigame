# R20 plan v1 — R8-family revival on validated substrates

**Status**: scoped 2026-05-06, pre-launch blockers below.

**Hypothesis (load-bearing)**: The 3-point gap between R19's human-eval ceiling (5.0) and R8's (8/10) is dominated by **rule family**, not substrate. R19 family `(capture) + influence + threshold-race` produces a score-neutral custodian flip (team-1 derivation: P1 +0.5 + P2 −1.0 + P1 +0.5 = 0); R8's `custodian + connection` family makes the same flip win-relevant. R20 tests this directly by running R8's family on R19's two best-validated substrates plus a grid control.

R20 is a **rule-family-comparator** round, not a substrate-comparator round. Substrate is the secondary axis.

---

## Substrate set

| # | substrate | dim | active cells | role |
|---|-----------|----:|-------------:|------|
| 1 | menger    | 2.727 | 400 | R19 strongest validated, 3D depth |
| 2 | carpet    | 1.893 | 64  | R19 second, tests whether connection rescues 2D score-neutrality |
| 3 | grid_control (axis 9) | 2.000 | 81 | **methodology check** — R8 family native; if R8 family doesn't approach 8/10 here under current stack, **stop and debug before R21**. (Original spec said axis=16; pre-launch smoke showed 16x16 connection is rush-broken regardless of pie rule. Axis revised to 9 — 81 cells, matches the carpet/menger axis-9 pattern; 12/12 R20 seeds passed two-tier smoke at this size.) |

Vicsek/triangle deferred — MCTS Phase 1 (2026-05-06) showed their R18/R19 weakness is training quality, not substrate ceiling. That belongs in a scoped training-budget probe, not R20's main course. Hexaflake deferred to R21+ (engineering-heavy, no evidence-driven hypothesis after R18 noise-floor null result).

---

## Seed pool design

4 rule families × 3 substrates = **12 seeds pre-smoke**, plus per-substrate R19 carry-overs as anchors.

### Rule families (held constant across substrates)

| ID | Family | Rationale |
|----|--------|-----------|
| F1 | custodian-1 + connection | **R8 exact**. Establishes the methodology floor on grid_control. |
| F2 | custodian-2 + connection | Heavier capture × R8 win condition. |
| F3 | surround + connection | Tests team-3's depth hypothesis (surround needs more PPO for full strategic learning, but on a win-relevant scoring rule). |
| F4 | outnumber-2 + connection | R19's GE-strongest capture rule × R8's win condition. Cross-pollinates R19 lessons into R8 frame. |

All four families use **place-only** actions (D1 hybrid penalty enforces this; R17/R18/R19 unanimous: hybrid actions unused).

### Carry-over anchors (per substrate, post-finalization)

- menger: R19 top-1 `1f9191b5d4e6` (outnumber-2 + influence(r=1) + threshold-race; GE 0.3293, human 4.8) + top-3 `5048f71b62fd` (surround variant; human 5.0)
- carpet: R19 top-1 `ce3a09e05cef` (GE 0.3547, human 4.4)
- grid_control: R8 Connection Go genotype if extractable from older DBs; else skip carry-over and rely on F1 seed

These carry-overs let R20's evolution measure direct family-vs-family fitness on equal footing. **Must be re-evaluated under the R20 stack** (with pie rule + 15-seed finalization) before being treated as fitness anchors — their original GE numbers are pre-finalization and will move.

---

## Stack additions (all mandatory in R20)

### S1 — Pie rule (NEW, BLOCKING)

**30/30 R19 verdicts unanimous**: mirror = P1 wins is structural across all 6 R19 games. Pie rule (P2 may swap sides after P1's first move) is the canonical knowledge-asymmetric balance fix.

**Status**: **NOT YET IMPLEMENTED**. Grep across codebase returns zero hits for `pie_rule`. This is a real engine + training change, not a config flag.

**Implementation scope**:
- `game_engine/engine_v2.py`: add a pie-decision step after P1's first move. P2 chooses swap-or-play, swap relabels stones P1↔P2.
- `game_engine/game_def_v2.py`: add `pie_rule: bool` field on game definition.
- PPO: pie decision is a 2-action policy at exactly one ply. Either (a) train as a separate small head, or (b) cleanest: encode as "P2's first action chooses pie or normal-move" expanding action space at ply-2 only. Decision deferred to implementation session.
- Generator: default `pie_rule=True` for all R20 seeds.
- Tests: `test_pie_rule.py` covering swap-applied, swap-declined, swap-on-first-only, win-condition-after-swap.

**Cost estimate**: 1-2 sessions of focused work. The 2-action expansion approach has the cleanest training-stack interaction. This is **R20's largest pre-launch blocker** by far.

### S2 — Two-tier smoke gate (per R19_postmortem § Tier 2)

Spec already in `R19_postmortem.md` lines 76-112. Reproduced here for R20-implementation reference:

- **Tier 1** (existing 3000-ep PPO): hard-drop only on catastrophic — `seat_bias ≥ 0.45`, `sampled_avg_len < 15`, or `greedy_p1_wr ≥ 0.95 AND seat_bias ≥ 0.40`.
- **Tier 2** (new 6000-ep retry on borderline): pass if soft floors clear OR seat bias drops by ≥ 0.05 between Tier 1 and Tier 2.
- Wall-clock surcharge: ~2 hr parallel with launch prep. Compute surcharge: ~0.3% of total run.

**Implementation**: extend `experiments/r18_ppo_smoke/harness.py` with `--tier2-budget 6000` and a `--retry-borderline` flag. Wire into `experiments/r20_seeds/build_seeds.py` (new) following R19's smoke-driver pattern.

### S3 — Champion-finalization tier (per R19_postmortem § Champion-finalization)

Spec already in `R19_postmortem.md` lines 149-161. Reproduced for R20-implementation reference:

- For top-K = 5 candidates per substrate at end-of-run, re-score with **15 PPO seeds total** per game (5 reruns × `num_independent_runs=3`).
- Drives σ from ~0.09 → ~0.04 on menger; from ~0.07 → ~0.03 on carpet.
- Cost: ~1 hr wall-clock per substrate. **~3 hr total** for 3 substrates.

**Implementation**: new script `experiments/r20_finalization/finalize_champions.py`. Pattern from `experiments/r18_noise_floor/run_noise_floor.py` (5-rerun loop with `:finalization:<rerun_idx>:<run_within>` seed namespacing).

### S4 — Already in stack (no R20 change)

- D1 hybrid action penalty (R19 `bc858af`)
- C1 deterministic run seeds (R18 `addda54`)
- C2 multi-seed averaging across 3 runs (R18 `a843d0a`)
- B1 substrate invariants (R18 `a0e0ede`)

---

## Pre-launch blockers — STATUS

| ID | Blocker | Status | Owner-session |
|----|---------|--------|---------------|
| S1 | Pie rule (engine + training + tests) | NOT STARTED | next 1-2 sessions |
| S2 | Two-tier smoke harness | NOT STARTED | 1 session |
| S3 | Champion-finalization script | NOT STARTED | 1 session |
| Z1 | R20 seed builder + 12 seeds | NOT STARTED | post-S1 |
| Z2 | R20 driver + launch script | NOT STARTED | post-S1, S2 |
| Z3 | Carry-over re-evaluation (R19 anchors under R20 stack) | NOT STARTED | post-S1, S3 |

**S1 is the critical path.** S2 and S3 can be built in parallel, but seeds and driver depend on S1.

---

## Run config (per substrate)

Same shape as R19, with carry-overs:

| Substrate | pop | gens | budget/ep | est. wall-clock |
|-----------|----:|-----:|----------:|----------------:|
| menger | 30 | 8 | 10000 | ~30 hr |
| carpet | 30 | 8 | 15000 | ~25 hr |
| grid_control (axis 9) | 20 | 4 | 10000 | ~1 hr (faster than the original axis-16 estimate; 81 cells trains roughly at carpet speeds) |

Total R20 evolution: **~58 hr wall-clock**, parallel via `launch_r20.sh`.

Tier-2 smoke retries: ~2 hr.
Champion finalization: ~3 hr.
Carry-over re-evaluation: ~2 hr.

**Grand total: ~65 hr wall-clock**, within R19's order of magnitude.

---

## Eval style — DECISION

Same protocol as R19: **5-team campaign × 6 games = 30 verdicts**.

R20 produces 3 substrates × top-3 = 9 candidate games, but eval bandwidth is 6 games per campaign. Selection rule for the 6:
- 1 menger × custodian+connection (best F1/F2 by post-finalization GE)
- 1 menger × surround+connection (F3, tests depth hypothesis)
- 1 menger × R19 carry-over (head-to-head: R8 family vs R19 family, same substrate)
- 1 carpet × custodian+connection (cleanest carpet score-neutrality test)
- 1 carpet × R19 carry-over (head-to-head)
- 1 grid_control × F1 (R8 reproduction sanity check)

Briefing must explicitly anchor against R8 (8/10), R17 (3.50 mean / 4.14 best), and R19 (4.375 mean / 5.0 ceiling). R19 found Claude drifts ~+0.5–1.0 above R17 unless actively countered — same correction expected for R20.

---

## R20 success criteria

| Goal | Metric | Threshold |
|------|--------|-----------|
| **G1** Methodology check | Grid_control F1 (custodian + connection) human eval | **≥ 6.0** (gives 2-pt safety margin to R8's 8/10; if it doesn't clear 6.0, the stack is broken) |
| **G2** Beat R19 ceiling | Best R20 game human eval | **> 5.0** (R19 menger rank-3) |
| **G3** Family hypothesis | Custodian+connection mean > R19-family carry-over mean (head-to-head pairs) | **≥ 0.5 pts** on the 1-10 scale |
| **G4** Pie rule effectiveness | Mirror-game seat bias on R20 games | **< 0.10** (vs R19's universal mirror=P1-wins finding) |
| **G5** Noise-floor honesty | All R20 leaderboard claims report 15-seed σ | post-finalization stage executed for top-5 per substrate |

**G1 is load-bearing.** If grid_control + F1 doesn't clear 6.0, do not promote R20 conclusions on menger/carpet. The methodology stack has regressed since R8 and the priority shifts to root-causing the gap.

---

## Decisions resolved 2026-05-06

1. **Pie rule implementation approach**: **ply-2 action-space expansion**. P2's first action chooses pie-or-normal-move; cleaner training-stack interaction than a separate small head. Locked.
2. **R8 Connection Go carry-over**: **skip extraction**. Grid_control starts from F1 seed only. Rationale: grid_control is a methodology check (G1 success criterion), and F1 (custodian-1 + connection = R8 exact) clearing human 6.0 is the load-bearing test. Carry-over comparison adds engineering cost without changing the gate. If R8 DB is trivially accessible during S1 it can be added back, but it is not blocking.
3. **Carry-over re-evaluation scope**: **4 anchors only** — the exact carry-overs cited in § Eval style (3 R19 + R8-skip). Bounded by the 6-game eval pool. Wider scope deferred to R20_postmortem if cross-run noise-corrected delta becomes a question.
4. **F3 surround + connection on carpet**: **keep**. Lowest-confidence cell of the matrix, most likely to fail informatively. Drop only if smoke catastrophically rejects it on every retry.

---

## Explicitly deferred to R21+

- Hexaflake substrate (R18-deferred, no evidence-driven hypothesis as of R20 scoping)
- Higher-axis 3D substrates (menger axis=27, dim 2.5–2.9 scan)
- Vicsek/triangle revival (MCTS Phase 1 reframes this as a training-budget probe, not a substrate question)
- GE depth-aware adjustment for surround capture (R19 finding #6 — methodological work, separate scope)
- Threshold raise to 35-40 on surround games (R19 team-3 single-finding, can be a per-seed parameter variant if F3 underperforms but not a primary R20 axis)
- OpenSpiel migration (Phase 1 MCTS confirmed: no stability win, σ 0.04-0.09 same as GE)

---

## What R20 does NOT change

- C1 deterministic seeds, C2 multi-seed averaging, D1 hybrid penalty — unchanged.
- B1 substrate invariants — unchanged.
- Smoke gate's existence and Tier-1 hard-drop checks — unchanged. Tier 2 only adds a second-chance for borderline seeds.
- 30-verdict human eval campaign protocol — unchanged. Only the briefing anchors and the 6-game selection rule are new.

---

## Sequencing summary

1. S1 — pie rule implementation + tests (1-2 sessions)
2. S2, S3 — two-tier smoke + finalization scripts (1 session, parallelizable post-S1)
3. Z1 — seed builder + 12 seeds (1 session, post-S1)
4. Z2 — driver + launch script (post-S2)
5. Z3 — carry-over re-evaluation under R20 stack (post-S1, S3)
6. Tier-1 smoke + Tier-2 retries → final R20 seed set
7. R20 evolution launch (~3 days wall-clock)
8. Champion finalization (~3 hr)
9. R20 evaluation report draft + 30-verdict eval campaign (~1-2 sessions)
10. R20 evaluation report final + R20_postmortem.md
