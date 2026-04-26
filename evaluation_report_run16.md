# Run 16 Evaluation Report

**Database**: `genesis_v2_run16.db`
**Config**: 11 generations (0-10), pop 50, 10k training budget, 2 runs, 25% immigration, 2D-only, ca-prob 0.2, sim-prob 0.5, sim×CA bias 0.4
**Run duration**: ~20h (launched 2026-04-24 20:08, completed 2026-04-25 ~16:05)
**Seeds**: `deb4dfe0382d` (R14 GE champion) and `531634cee158` (R13 human winner) from genesis_v2_run14.db
**R16 engine/scoring changes shipped**:
1. Margin-based resolution in `_check_threshold` and `_check_connection` (replaces R15 P1-iteration-bias)
2. CA step from shared snapshot, conflicts→no-op (`_run_ca_step_symmetric`)
3. Generator quick-rejects torus + connection
4. Generator downgrades moore → grid when surround capture present (at fresh-game creation)
5. Greedy-vs-greedy seat-balance probe added to trainer; worst-of-three in `seat_balance` metric
6. `ca_probability` default 0.3 → 0.2

**Human evaluation**: 22 team evaluations (1 pilot + 6 production on rank 1; 5 each on ranks 2, 3, and 5)

---

## Executive Summary

R16 produced its **best human-evaluated game since R14**: rank-3 `c6bb58075520` (torus + alt + outnumber capture + influence threshold) at **mean 4.40/10**, the highest non-R8 score in three runs. Still well below R8's 8/10 bar, but a meaningful step up from R15's champion (2.43).

**The GE ranking inverted again**, this time at the top: GE rank-3 is the human winner; GE rank-1 is human rank-2; GE ranks 2 and 5 tie at the bottom.

**Engine fixes worked partially**:
- ✅ **Margin-based threshold/connection** — multiple teams independently demonstrated the fix firing correctly. Sim games show clean Balance 8-9/10 (R15 had Balance 1.7).
- ✅ **CA from shared snapshot** — sim+CA games dropped from R15's GE 0.145 (top tier) to R16's GE 0.0026 (bottom) and showed non-triv 0.00. Mechanic correctly identified as adding no value.
- ✅ **Generator quick-reject torus+connection** — no torus+connection games appeared in R16.
- ⚠️ **Moore + surround capture downgrade** — works at fresh-game creation but **mutation/crossover bypass it**. Team-17 traced this to `evolution/operators_v2.py:_fix_consistency` not applying the same downgrade. Rank-5 game is gen-10 evidence the fix has a hole.
- ⚠️ **Worst-of-three seat-balance probe** — caught some bias but missed others. The 0.2 floor on the seat_balance penalty caps how much imbalance can hurt the composite, allowing the alternating threshold-race champion to retain rank 1 despite Balance 2-3 from human eval.

**Three new engine issues surfaced** (in addition to R15's three already-fixed ones):
1. **Floating-point ordering bias in simultaneous propagation** — when both players cross threshold with margins differing by ~3.5e-15, the FP ordering of P1's vs P2's `_apply_propagation` calls determines the winner. Multiple teams reproduced this (team-7, team-9, team-10, team-11). Effectively a residual P1 bias at the precision boundary.
2. **`_fix_consistency` skips topology-capture compatibility checks** — the moore+surround downgrade exists in `_generate_game` but not in mutation/crossover consistency. Team-17 located the exact gap at `evolution/operators_v2.py`.
3. **Threshold tuning produces parity bias** — multiple teams (team-12, team-13) noted threshold values are calibrated such that whoever places stone N+1 in a symmetric race crosses first. P1 always plays odd plies, so P1 always gets stone N+1 first when threshold is between stones N and N+1's contributions. This is a coupling of fitness-driven threshold selection to alternating-game seat order.

---

## Final Leaderboard — GE vs Human

| GE Rank | Game ID | GE | Mechanics | Human Mean | Stdev | Teams | Human Rank | Δ |
|------|---------|------|------|-----------|-----|-----|-----|---|
| 1 | `8d12c8b92b71` | 0.160 | Hex alt no-cap threshold | 3.57 | 0.8 | 7 | **2** | −1 |
| 2 | `f8dbeb3079a5` | 0.120 | Moore SIM no-cap threshold | 2.60 | 0.9 | 5 | 3-4= | −1 to −2 |
| 3 | `c6bb58075520` | 0.102 | Torus alt outnumber threshold | **4.40** | 0.9 | 5 | **1** | **+2** |
| 5 | `4d9c5796dd18` | 0.088 | Moore alt surround threshold | 2.60 | 0.9 | 5 | 3-4= | −2 |

**Run-over-run trend (champion human score):**
- R8: 8.0 (still the high water mark)
- R13: 5.0
- R14: 4.57
- R15: 2.43
- R16: **3.57** (recovery from R15 floor; best human game in R16 is 4.40)

---

## Per-Game Findings

### Game 1 — `8d12c8b92b71` "Hex Alt Influence Threshold" (GE rank 1, human rank 2)

**Format**: 2D 8×8 hex (6-neighbor), alternating, place-anywhere, no capture, no CA, radius-2 signed influence (strength 0.984, decay 0.695), threshold win at effective own-cell sum > 34.13. Gen 7. Non-triv 1.00, diversity 1.00.

**Team-by-team Overall scores**: pilot 3, team-1 3, team-2 4, team-3 3, team-4 5, team-5 3, team-6 4 → **mean 3.57, stdev 0.79**.

**Consensus findings**:
- **First-mover advantage is severe under skilled play**: pilot saw 20/20 P1 in greedy probe; team-1 saw 7/8 P1; team-3 saw P1 14/14 with center opening; team-6 saw mostly P1 with non-mirror P2 wins; team-2 saw greedy 100% favor whoever opens center.
- **Center-grab is the real first-mover advantage**: hex topology gives center cells 19-cell radius-2 footprint vs ~6 for corners. Whoever claims center races to threshold first.
- **Some P2 counter-strategies exist**: team-4 found "disrupt-then-build" beats greedy P1 in non-mirror configurations. Team-3 found P2 beats greedy P1 when P1 plays corner. Team-5 found P2 wins greedy-vs-greedy 5/5 via the R16 margin tiebreak (when P2 lands a slightly better cluster).
- **Margin-based threshold fix verified**: team-5 explicitly demonstrated R16 margin tiebreaker awarding P2 (36.64 vs 33.37 same tick). Fix works.
- **Closest analog universally**: Tumbleweed (hex influence projection), with ~70-80% skill transfer for a Tumbleweed expert. Genuine novelty: signed influence + own-cell negative-influence drag.

**Aggregate sub-scores** (mean):
- Strategic Depth: 4.4
- Emergent Complexity: 4.3
- Balance: 3.0
- Novelty: 4.1
- Replayability: 3.6

**Killer flaws**:
1. Severe P1 tempo advantage under symmetric/greedy play
2. Center-grab dominant strategy resolves most games quickly
3. No capture/CA means no recovery dynamics
4. The R16 worst-of-three seat-balance probe did not down-rank this game enough to drop it from rank 1

**Best quality**: Negative own-cell influence drag — a genuine emergent property where overlapping signed influence creates self-poisoning regions. Multiple teams (4, 5, 6, pilot) flagged this as the most interesting feature.

---

### Game 2 — `f8dbeb3079a5` "Moore Sim Influence Threshold" (GE rank 2, human rank 3-4)

**Format**: 2D 8×8 moore (8-connected Chebyshev), **simultaneous**, place-anywhere, no capture, no CA, radius-1 influence (strength 1.04, decay 0.37), threshold win at 30.75. Gen 8.

**Team-by-team Overall scores**: team-7 2, team-8 3, team-9 2, team-10 2, team-11 4 → **mean 2.60, stdev 0.89**.

**Consensus findings**:
- **R16 fixes deliver genuine seat balance**: team-8 awarded **Balance 8/10**, team-9 Balance 9/10, team-11 Balance 8/10 — the highest balance scores in any R16 evaluation. Margin-based threshold fix lets symmetric play resolve as draws or strategy-determined wins, regardless of seat. **This is direct empirical evidence the engine fix delivers what it was designed to.**
- **But strategic depth is shallow**: aggregate Strategic Depth 2.6, Emergent Complexity 2.4. Mutual annihilation never fires in optimal play. Game decomposes to "two parallel solitaire games of cluster-fill in opposite corners". One dominant strategy.
- **Floating-point ordering artifact**: when both players' margins differ by ~1e-15, FP ordering of `_apply_propagation` for P1 vs P2 in `step_simultaneous` determines winner. Reproduced by teams 7, 9, 10, 11. Non-deterministic at the precision boundary; effectively a coin-flip but not a true draw.
- **Closest analog**: Tumbleweed family with simultaneous + collision; or Blotto with spatial coupling. Not a 1:1 reskin but inside established design space.

**Killer flaws**:
1. Strategic surface flat — no emergent dynamics
2. Mutual annihilation collision strategically inert
3. FP-precision residual P1 bias

**Best quality**: First clean human-eval demonstration that R16's engine fixes correctly eliminate seat advantage in simultaneous play. The mechanism works; the game just isn't deep.

---

### Game 3 — `c6bb58075520` "Torus Alt Outnumber Threshold" (GE rank 3, human rank 1) — HUMAN WINNER

**Format**: 2D 8×8 torus, alternating, place-anywhere, **outnumber capture (threshold 2)**, radius-1 influence (strength 0.93, decay 0.51), threshold win at 22.65. Gen 10.

**Team-by-team Overall scores**: team-12 3, team-13 4, team-14 5, team-15 5, team-16 5 → **mean 4.40, stdev 0.89**.

**Consensus findings**:
- **Active capture mechanic produces emergent dynamics**: team-14 documented "poisoned cells" (captured stones leave residual influence), capture-recapture cycles at contact lines, super-ko rollback creating "fortress cells" (cells with all non-empty neighbors are permanently invulnerable to outnumber capture).
- **Game responsive to skill**: team-16 — "smarter player wins 100%". Team-14 — P2 wins 2/6 in seat-cross greedy probe (not deterministic P1).
- **Tempo/parity bias is real**: P1 wins 67-87% in symmetric greedy probes (lower than the alternating champion's 87%, but still meaningful). Threshold appears tuned to give P1 a 1-move lead in symmetric races.
- **Three viable strategic motifs**: cluster-build, capture-trade, denial-placement. Distinct decision space, unlike the dominant-strategy collapse seen in other R16 top games.
- **Capture is mechanically active**: outnumber-2 threshold means P2 stone surrounded by 2 P1 stones dies on placement. Team-12, 13, 14, 15, 16 all observed captures firing.

**Aggregate sub-scores** (mean):
- Strategic Depth: 5.0
- Emergent Complexity: 5.2
- Balance: 4.0
- Novelty: 4.0
- Replayability: 4.6

**Killer flaws**:
1. P1 tempo bias (~67-87% greedy)
2. Torus radius-1 means wraparound rarely fires (radius too short to reach the other side)
3. Threshold appears parity-tuned

**Best quality**: The combination of outnumber capture + persistent influence + super-ko produces *emergent* dynamics — captures change ownership but leave influence; "fortress cells" emerge from being completely surrounded; ko-rollbacks favor whoever captures first. This is the design pattern that tested best across all R13/R14/R15/R16 evaluations: classical alternating + active capture + influence + threshold.

**Why human winner over GE rank-1**: simply has *more game in it*. Capture mechanics give counter-play; cluster-build is one of three viable strategies; emergent ko/fortress dynamics surprised multiple teams. The R16 GE metric ranked it 3rd because non-triv 1.00 + ELO 2665 don't capture "richness of decision space".

---

### Game 5 — `4d9c5796dd18` "Moore Alt Surround Threshold" (GE rank 5, human rank 3-4)

**Format**: 2D 8×8 **moore**, alternating, place-anywhere, **surround capture (threshold 1)**, radius-2 influence (strength 1.68, decay 0.72), threshold win at 50.5. Gen 10. Non-triv 0.85.

**Team-by-team Overall scores**: team-17 2, team-18 3, team-19 4, team-20 2, team-21 2 → **mean 2.60, stdev 0.89**.

**Consensus findings (5/5 teams converge)**:
- **Capture rule is dead** — 0 captures observed across 15 games (3 each × 5 teams). 8-neighbor adjacency makes interior stones structurally ungappable. Same pattern as R13/R14/R15 Moore games.
- **My R16 fix has a hole**: team-17 traced it precisely: `_generate_game` applies the moore→grid downgrade for surround capture, but `evolution/operators_v2.py:_fix_consistency` does not. Mutations and crossovers can produce moore+surround games that bypass the fix. This is a gen-10 game whose `capture` field was mutated to surround at some point in its lineage without the topology being downgraded.
- **Severe P1 first-mover advantage**: 3/3 P1 in every team's playthroughs; team-18 saw greedy 5/5 P1; team-19's 26-opening sweep showed ~73% P1.
- **Strategic depth is shallow**: dominant strategy is compact-cluster fill-in, capture rule is decorative, no emergent dynamics besides influence overlap.

**Killer flaws**:
1. Capture rule inert (Moore makes surround impossible)
2. Severe P1 tempo bias
3. Single dominant strategy

**Best quality**: Continuous radial influence kernel produces the only emergent property (overlapping influence regions). Same kind of novelty as the champion but with worse balance.

---

## Cross-Cutting Discoveries

### 1. NEW engine issue: floating-point ordering bias in `step_simultaneous`

**Severity**: LOW — only fires at FP precision boundary, but is reproducible
**Reporters**: team-7, team-9, team-10, team-11 on sim moore (`f8dbeb3079a5`)

**Details**: When both players' effective values cross the threshold on the same tick with margins differing by ~1e-15, the order in which `_apply_propagation` is called for P1 vs P2 in `step_simultaneous` introduces measurable FP rounding differences. Whoever's propagation runs second sees a slightly different cell value and crosses by a femto-margin. Reproduces:
- Team-9 Game 1: both ostensibly 31.48; P1 wins by ~1e-15
- Team-10 Game 1: both 33.67 → draw; symmetric variant produces ~3.5e-15 P1 win
- Team-11 Game 2/3: same geometry seat-swapped, FP outcome flips

**Impact**: In strictly-symmetric play this surfaces as a residual FP-level P1 bias. In normal asymmetric play, irrelevant. Margin-based threshold logic is correct in spirit; the artifact is downstream.

**Fix direction**: Either (a) compute both players' effective values from a single shared pre-step snapshot before applying any propagation (purely simultaneous semantics), or (b) snap margins to a deterministic precision before comparing.

### 2. NEW engine issue: `_fix_consistency` skips moore+surround downgrade

**Severity**: HIGH — directly bypasses an R16 fix
**Reporter**: team-17 (precise diagnosis), corroborated by teams 18-21 finding moore+surround games in R16 top tier

**Details**: In `_generate_game` (game_engine/generator_v2.py), when capture_type is "surround" and topology is "moore", the topology is downgraded to "grid". This is correct. However, `evolution/operators_v2.py:_fix_consistency` (called after mutation/crossover) does not apply this same rule. So a mutation that flips a non-surround game's capture to surround, or flips a non-moore game's topology to moore, creates an invalid moore+surround combination that survives.

**Impact**: rank-5 game `4d9c5796dd18` is a gen-10 descendant produced by mutation. Capture is dead. Game is in top 20 because evolutionary fitness can't see the dead-rule problem.

**Fix direction**: Add the moore→grid downgrade rule to `_fix_consistency` (and ideally factor the rule into a shared helper that both `_generate_game` and `_fix_consistency` call).

### 3. NEW engine issue: threshold parity bias in alternating games

**Severity**: MEDIUM — affects fitness-vs-human-perception calibration
**Reporters**: team-12, team-13 (explicit), and implicit in champion teams

**Details**: Generated thresholds appear to be calibrated such that whoever places stone N+1 in a symmetric race crosses first. P1 always plays odd plies (1, 3, 5, ...); P2 always plays even plies. For threshold values that fall between stone-N and stone-N+1's contribution, P1 always crosses first.

This isn't a "bug" so much as a consequence of how threshold values are mutated against the trained-vs-trained ELO signal — thresholds that produce decisive non-trivial games tend to land at the parity-favored value.

**Impact**: Compounds the alternating-game first-mover advantage. The R16 worst-of-three probe samples greedy and random play but doesn't specifically test "what if P2 had played one extra move?".

**Fix direction**: Generator could pin threshold to a multiple of stone-contribution (or shift it by 0.5 stones to favor neither parity). Alternatively, evaluation could include a "P2 gets +1 free stone" tie-break test.

### 4. R16 metric calibration: the 0.2 seat_balance floor masks severe imbalance

**Severity**: MEDIUM — directly affects rankings
**Reporters**: pilot, team-1, team-2, team-3, team-4, team-6 (all champion teams)

**Details**: In `metrics/scoring.py`, when seat_balance < 0.8, the composite is multiplied by `max(0.2, seat_balance)`. The 0.2 floor was added in R15 to give evolution differentiating signal even on imbalanced games. But for R16's champion (greedy probe ~100% P1 → seat_balance ≈ 0.0), this floor caps the penalty at 0.2× — letting a Balance 3/10 game retain GE 0.16 and rank 1.

**Fix direction**: Two options:
1. Lower the floor to 0.1 and apply only when seat_balance > 0.05 (hard-zero severe cases).
2. Keep the floor but increase the threshold for the penalty to fire (e.g., apply when seat_balance < 0.7 instead of 0.8) and steepen the slope.

Recommend option 1 — it preserves evolutionary signal on marginal imbalance while harder-killing severe imbalance.

### 5. Engine fixes that worked

These verified empirically across multiple teams:

- **Margin-based `_check_threshold`**: team-5 explicitly demonstrated P2 winning by margin (36.64 > 33.37) under R16's tiebreaker.
- **Margin-based `_check_connection`**: no torus+connection games appeared (generator filter), but the test in `test_simultaneous_integration.py` exercises the same logic.
- **CA from shared snapshot**: sim+CA games scored near zero across the entire R16 population (top sim+CA at GE 0.0026, non-triv 0.00). Compared to R15 where sim×CA had a top-tier candidate at GE 0.145, this is a striking change.
- **Sim seat balance**: teams 8, 9, 11 all awarded Balance 8-9/10 to the sim moore game. R15's sim×CA was Balance 1.7. Direct empirical evidence the engine fixes work.
- **Generator quick-reject torus+connection**: no such games in R16 top 20 (R15 had one at rank 5).

---

## Failure Modes Observed

| Failure | Games affected | Teams documenting |
|---|---|---|
| First-mover advantage (alternating) | All 3 alternating games | 17/17 alternating teams |
| Capture rule inert (Moore + surround) | Rank 5 | 5/5 |
| Floating-point ordering at margin boundary | Rank 2 (sim) | 4/5 |
| `_fix_consistency` skips moore+surround downgrade | Rank 5 | team-17 primary |
| 0.2 seat-balance floor preserves rank for severe imbalance | Champion | 6/7 |
| Threshold parity bias | Rank 1, Rank 3 | 3+ teams |

---

## Recommendations for Run 17

R16 was a meaningful step forward — engine fixes verified, balance metric extended, sim×CA conclusively dead. R17's goal is to (a) close the remaining holes in seat-balance handling, (b) push toward designs that beat R14's 4.57 / R8's 8.0.

### Engine fixes (must land before R17)

1. **Add moore+surround downgrade to `_fix_consistency`** (`evolution/operators_v2.py`). One line; team-17 specified it. Refactor into a shared `_normalize_topology_capture(game)` helper used by both `_generate_game` and `_fix_consistency`.

2. **Fix FP-ordering in `step_simultaneous`** (`engine_v2.py`). Compute both players' effective values from a single pre-step snapshot, then apply propagation outcomes in a deterministic order (e.g., resolve final values first, then update board atomically).

3. **Tighten seat_balance floor in scoring.py**. Drop from 0.2 to 0.1, with hard-zero (× 0.05 or × 0.0) when seat_balance < 0.1.

### Generator changes

4. **Threshold parity-shift**: when generating a threshold, perturb by ±0.5 × (stone-contribution) so the "first-to-cross-by-tempo" effect doesn't lock to P1.

5. **Extend the greedy probe**: in addition to the trainer's greedy-vs-greedy, add a "greedy P1 vs greedy P2 with +1 free move" probe to detect parity-tuned thresholds.

### Evolutionary strategy

6. **Reseed with R16's human winner** (`c6bb58075520`) plus the prior winners. The torus+outnumber+influence+threshold combination is the most strategically interesting design across all four runs.

7. **Reduce sim-probability to 0.3** (from 0.5). R15 and R16 evals show sim-only games are now correctly balanced but mechanically thin. Don't invest 50% of population in shallow games; let evolution focus on alternating with capture.

8. **Keep ca-probability at 0.2** — CA is dead post-fix and we don't need to over-invest, but a small population maintains genetic diversity.

---

## Proposed Run 17 Configuration

```bash
# BEFORE running R17:
# 1. Patch _fix_consistency for moore+surround
# 2. Fix FP ordering in step_simultaneous
# 3. Tighten seat_balance floor (0.2 → 0.1, hard-zero severe)
# 4. Add threshold parity-shift to generator
# 5. Optional: greedy-with-extra-move probe

.venv/bin/python run.py \
  --generations 10 \
  --population 50 \
  --training-budget 10000 \
  --num-runs 2 \
  --immigration-rate 0.25 \
  --max-dimensions 2 \
  --ca-probability 0.2 \
  --simultaneous-probability 0.3 \
  --db-path genesis_v2_run17.db \
  --seed-db genesis_v2_run16.db \
  --seed-games c6bb58075520 8d12c8b92b71
```

Rationale:
- **Seeds**: R16 human winner (`c6bb58075520`) + R16 GE champion (`8d12c8b92b71`). Both have legitimate features worth preserving — outnumber-capture + torus + influence in the winner; signed-influence drag in the GE champion.
- **sim-prob 0.5 → 0.3**: shift evolutionary budget toward classical alternating with capture (the design family that has produced the best games across runs).
- **ca-prob 0.2 unchanged**: CA is decorative now; small probability for genetic diversity.

---

## Files

- **Database**: `genesis_v2_run16.db` (500 games, 310 scored, 115 MB)
- **Training log**: `run16_output.log`
- **Team evaluations**: `evaluations/run16/team-{1-21,pilot}_game{id}.md` (22 files)
- **Evaluation protocol**: `v2-evaluation-prompt-run16.txt`

---

## Verdict

R16 is the most successful run since R14 by human evaluation, with a clear winner (`c6bb58075520`, 4.40/10) and an honest second-place GE champion (3.57/10). The engine fixes verifiably work — margin-based threshold delivers seat balance for sim games, CA-from-snapshot kills the bug-driven sim+CA inflation, and torus+connection is correctly filtered. The seat-balance metric improvement (worst-of-three with greedy probe) catches more bias than R15's metric, but the 0.2 floor in scoring still lets imbalanced games rank too high.

Three new engine issues surfaced (FP ordering, `_fix_consistency` gap, threshold parity), all actionable for R17. The mutation/crossover gap in particular is mechanically clear: team-17 traced it to a single missing topology-capture compatibility check.

The strongest design family across R13-R14-R15-R16 evals is now apparent: **classical alternating placement + active capture (custodian or outnumber) + radius-1-or-2 signed influence + threshold win on a non-Moore topology (grid / hex / torus)**. R8's "Connection Go" was outside this family (connection win, no influence) but matched the pattern of "active rule that creates emergent dynamics + simple but non-trivial primitive". R17 should bias evolutionary search toward this family explicitly.

The **sim×CA premise stays dead**. R16 confirmed conclusively: post-fix, sim+CA games are at the bottom of GE *and* the bottom of human eval. The R14/R15 "signal" was bug-driven. Don't reorganize R17 around it.

Pure simultaneous games are **balanced but shallow**. R16's lone simultaneous top-tier game scored Balance 8-9/10 (R15 was 1.7) — proof the engine fixes work — but Strategic Depth 2.5. The mechanic *can* be made fair, but doesn't generate emergent dynamics on its own. Reduce evolutionary investment.
