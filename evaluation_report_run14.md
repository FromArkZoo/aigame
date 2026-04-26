# Run 14 Evaluation Report

**Database**: `genesis_v2_run14.db`
**Config**: 11 generations (0-10), pop 50, 10k training budget, 2D-only, simultaneous prob 0.5, CA prob 0.3, 25% immigration, seeded from Run 13 top games
**Seed games**: `531634cee158` (R13 human winner), `06bab8a32425` (R13 CA champion)
**Duration**: run completed 2026-04-14; human evaluation 2026-04-22
**Evaluation protocol**: Tiered agent-team evaluation with mandatory Novelty Adversary, following `v2-evaluation-prompt-run14.txt` (adapted from Run 13 protocol plus pilot-surfaced caveats)
- 1 pilot on champion
- 6 production teams on rank 1 (champion) → 7 total
- 5 teams on rank 2
- 5 teams on rank 3
- 7 teams on rank 5 (sim×CA — R15 premise candidate, extra-weighted)
- **Total: 24 independent team evaluations**

---

## Executive Summary

**Run 14 produced no champion that beats its predecessors.** All four tier-1 games scored 3–5/10 in human evaluation, well below Run 8's "Connection Go" (8/10) which remains the project's strongest output. The Go Essence metric again failed to track human judgment — every GE ranking was compressed or inverted relative to human verdict.

The run's most important outcome is **not a game** but a diagnostic finding: **7 independent teams converged on an engine bug that invalidates the R14 simultaneous×CA signal**. The simultaneous+CA hybrid at rank 5 (`992bf7dfc9f4`, GE 0.420) was the strategic premise for planning Run 15 around sim×CA coupling. That premise is corrupted — the "signal" was a P1-asymmetric CA execution, not a strategic mechanic.

**Three simultaneous discoveries:**
1. The `step_simultaneous` CA loop (`engine_v2.py:252-254`) only runs from P1's perspective when `steps_per_turn=1`
2. The CA rule-table generator produces asymmetric tables (not invariant under 1↔2 swap)
3. The double-pass majority exploit from R13 fired in ~30% of sim×CA games, confirming its continued priority for R15

**Highest-scoring game in R14 human evaluation**: the GE champion `deb4dfe0382d` at mean 4.57/10 — notable for a novel "capture-as-poison" / value-retention mechanic, but with decisive P1 first-mover advantage.

---

## Final Leaderboard — GE vs Human

| GE Rank | Game ID | GE | ELO | Human Mean | Human Stdev | Teams | Human Rank | Δ |
|------|---------|------|------|-----------|-----|-----|-----|---|
| 1 | `deb4dfe0382d` | 0.517 | 997 | **4.57** | 1.3 | 7 | **1** | 0 |
| 2 | `1ca924cc3062` | 0.500 | 993 | **3.40** | 1.1 | 5 | 2= | 0 |
| 3 | `931c58ae59b4` | 0.482 | 3035 | **3.40** | 0.9 | 5 | 2= | +1 |
| 5 | `992bf7dfc9f4` | 0.420 | 2953 | **2.86** | 0.35 | 7 | **4** | +1 |

**Observations:**
- GE correctly identifies the champion (rank 1 in both orderings)
- Ranks 2 and 3 tie on human score at 3.40 — GE's 0.018 GE-point gap is not distinguishable by humans
- Sim×CA (GE rank 5, human rank 4) had the **tightest inter-team agreement** (stdev 0.35) — the reason is that 7 teams all independently identified the same engine bug, yielding near-unanimous "broken" verdicts
- The highest-ELO game (`931c58ae59b4`, 3035) did not win the human evaluation — consistent with R13's finding that arena ELO and strategic quality are only weakly correlated

---

## Per-Game Findings

### Game 1 — `deb4dfe0382d` "Torus Custodian Threshold" (GE rank 1, human rank 1)

**Format**: 2D 8×8 torus, alternating placement on any empty cell, Othello-style custodian capture (threshold 1, **does not wrap on torus**), radius-1 influence propagation (strength 1.874, decay 0.402, **does wrap**), win at effective influence sum > 38.62, max_turns=102.

**Team-by-team overall scores**: pilot 5, team-1 3, team-2 6, team-3 5, team-4 3, team-5 6, team-6 4 (mean 4.57, stdev 1.3).

**Aggregate sub-scores** (mean):
- Strategic Depth: 5.3
- Emergent Complexity: 5.4
- Balance: 3.6
- Novelty (post-adversary): 4.5
- Replayability: 4.4

**Consensus findings**:
- **P1 won 3/3 games in every team's playthroughs** — structural first-mover advantage
- Team-5 (48-game matrix) found P1 wins drop from 100% (mirror play) to ~65% (mixed heuristics), suggesting the balance problem is real but not absolute
- Novel mechanic: **captured cells retain their pre-capture influence values**. Capturing an enemy cell with negative stored influence *subtracts* from the captor's threshold sum, producing "capture-as-poison" / "value-flip paradox" dynamics
- Team-4 derived exact value formula: `total = 1.874·N + 1.506·E` (N=pieces, E=friendly edges)
- **Torus topology asymmetry**: influence wraps, custodian walks do not. Creates "edge fortress" dynamic (team-2) where edge stones are partially invulnerable to walks but still contribute influence
- Teams observed 3-6-capture chain cascades via simultaneous multi-directional custodian triggers (team-2 saw a 6-capture placement)

**Disagreement**: team-1/team-4/team-6 (scores 3–4) emphasized the decisive P1 advantage under equal play; team-2/team-5 (score 6) gave more weight to the capture-as-poison mechanic and tactical depth they uncovered in extended play. Team-5's 48-game matrix is the most rigorous evidence for the score spread.

**Closest analog**: Toroidal Othello with a Tumbleweed-like influence-threshold scoring layer — but the value-retention quirk has no direct analog in either parent game.

**Killer flaws**:
1. P1 first-mover dominance without pie/swap
2. Custodian capture is typically strictly weaker than simple extension due to value-retention
3. Torus influence/capture asymmetry is undocumented and potentially confusing

**Best quality**: The value-flip paradox — most games reward aggression; this punishes it. Multiple teams flagged this as the most genuinely novel element of Run 14.

---

### Game 2 — `1ca924cc3062` "Torus Influence Race" (GE rank 2, human rank 2=)

**Format**: 2D 8×8 torus, alternating placement with `adjacent_to_own` constraint, no capture, radius-2 Manhattan influence propagation (strength 0.874, decay 0.425), win at own-cell influence sum > 46.41, max_turns=83.

**Team-by-team overall scores**: team-7 4, team-8 3, team-9 5, team-10 3, team-11 2 (mean 3.4, stdev 1.1).

**Consensus findings**:
- **P1 dominance near-universal**: team-9 found P2 can win via "invasion for denial" in specific configurations, but teams 7, 8, 10, 11 could not construct a P2 win. Team-10's 14-opening battery: P1 wins 14/14
- Adjacent-to-own constraint forces monolithic blob growth — no meaningful tempo/sacrifice dynamics
- Zero double-pass endings across any team's games — threshold is reachable (0 of 3 for most teams)
- **Closest analog universally identified**: Tumbleweed (Zapawa 2021) — hex/torus influence-majority territory game

**Killer flaws**:
1. Severe first-mover advantage with no counter-mechanic (no capture, no ko, no disruption)
2. Greedy local hill-climb defeats any long-term strategy — no tactical layer
3. No reversibility; monotonic accumulation

**Best quality**: Clean interpretable influence-potential surface; torus wrap-adjacency creates some corner-vs-center strategic parity

**Verdict**: A weaker, cleaner variant of the Tumbleweed family. Not a breakthrough.

---

### Game 3 — `931c58ae59b4` "Moore Influence Tempo" (GE rank 3, ELO rank 1, human rank 2=)

**Format**: 2D 8×8 Moore (8-neighbor Chebyshev) grid, alternating placement `adjacent_to_own`, surround-capture (threshold 1), radius-2 influence (strength 1.615, decay 0.462), win at sum > 63.46, max_turns=100. Seeded from R13 parent, v3 representation.

**Team-by-team overall scores**: team-12 5, team-13 3, team-14 3, team-15 3, team-16 3 (mean 3.4, stdev 0.9).

**Consensus findings**:
- **P1 won 3/3 in every team's playthroughs** — absolute consensus on first-mover dominance
- **Capture rule is dead on Moore** — 0 captures fired across all 5 teams × 3 games. 8-way surround is structurally unreachable in dense cluster play
- Games converge in ~21–23 plies; 0 double-pass endings observed
- Strategic Depth averages 4.0, Emergent Complexity averages 4.0 — moderate but shallow
- Team-12 (the outlier at 5/10) found a "contamination" / inverted-incentive mechanic when influence crosses cluster boundaries

**Closest analog**: Influence-scored Go on Chebyshev-adjacency board, with capture neutered by topology. Teams also cited Tumbleweed for the scoring aesthetic.

**Killer flaws**:
1. Vestigial capture rule (rule complexity inflation — rule is present but inert)
2. One dominant strategy: greedy cluster densification
3. P1 tempo advantage worth ~7–10 effective points under symmetric play

**Best quality**: The contamination dynamic (team-12) — hostile influence on own cells subtracts from score — is the one emergent property worth noting.

**Note on ELO**: This game's ELO of 3035 is the highest on the R14 leaderboard, yet human evaluation ranks it tied with rank-2 and below the champion. ELO reflects consistent wins against the arena population, not absolute strategic quality — and in this case the arena converges on an easy-to-exploit greedy strategy.

---

### Game 4 — `992bf7dfc9f4` "Simultaneous-CA Hybrid" (GE rank 5, human rank 4) — THE R15 PREMISE GAME

**Format**: 2D 8×8 grid, **simultaneous turn structure** (`pieces_per_turn=1`), `adjacent_to_own` placement, threshold territory win at ~41/64 cells, **active CA** with 16/75 non-trivial transitions (9 reachable on 4-neighbor grid: 3 births, 4 deaths, 2 conversions), `ca_rule.steps_per_turn=1`, v4 representation. Seed game, no parent.

**Team-by-team overall scores**: team-17 3, team-18 3, team-19 3, team-20 3, team-21 3, team-22 3, team-23 2 (mean 2.86, **stdev 0.35 — tightest consensus of any game in the run**).

**Aggregate sub-scores** (mean):
- Strategic Depth: 3.4
- Emergent Complexity: 4.3
- Balance: **1.7** (lowest of any tier-1 game)
- Novelty (post-adversary): 4.4
- Replayability: 2.9

**THE CRITICAL FINDING — independently reached by 7 teams:**

The simultaneous turn structure does **not** eliminate first-mover advantage for this game. The cause is an engine wiring issue in `engine_v2.py:252-254`:

```python
# --- CA steps: alternate perspective each step ---
if uses_ca:
    for i in range(self.game.ca_rule.steps_per_turn):
        acting_player = 1 if i % 2 == 0 else 2
        self._run_ca_step(acting_player)
```

With `steps_per_turn=1`, the loop only runs `i=0`, so `acting_player = 1` every single round. The "alternate perspective" comment is aspirational — the alternation never fires. **The CA always evaluates from P1's perspective.** As a consequence:
- All CA birth rules produce P1 stones (6 births in the rule table, all P1-favouring)
- Capture/conversion rules (e.g. `(enemy, 2 friendly, 0 enemy) → friendly`) only convert P2→P1, never the reverse
- P2 can only grow by placement; P1 grows by placement AND by CA births every round

This is compounded by a **secondary finding** (team-22): the CA rule-table generator produces tables that are not symmetric under 1↔2 swap. Team-22 counted 16 asymmetric entries in this game's table. So even if the step-loop were fixed, the rule table itself would still favour P1.

**Empirical consequences across teams**:
- P1 won 3/3 games for every team
- Team-23: 20/20 random games won by P1
- Team-21: 98/100 random games won by P1
- Team-17: 41–14, 41–18, and 43–11 / 35–29 score margins
- **Simultaneous-cell collisions never fired in any game** by any team — the simultaneous mechanic is decorative with this bug
- Team-22: double-pass exploit fired 3/3
- Team-23: double-pass exploit fired 2/2
- Team-21: confirmed super-ko does not terminate collision-ko stalemates (88-turn deadlock in one game)
- Team-18: found a P2 round-1 counter (`(1,0,1)→2` flips P1's lone opener) — this is the ONE P2-favouring interaction in the rule table, and it's confined to round 1

**Novelty verdict (team-average 4.4/10)**: Closest analog is Gungo (simultaneous Go) crossed with the Immigration Game (two-color Conway's Life). The combination is not documented in published abstract games. But the *observed* novelty — dramatic P1 dominance via "asymmetric CA" — is an engine artefact, not a design property. Teams uniformly recommend the fix: set `steps_per_turn >= 2` to force perspective alternation, or rewrite the step loop to always run both perspectives.

**Killer flaws** (ranked by frequency across 7 teams):
1. CA step-loop P1 asymmetry (7/7 teams) — the primary issue
2. Double-pass majority exploit (5/7 teams saw it fire) — R13 failure mode recurring
3. CA rule-table player-swap asymmetry (team-22)
4. "Collision fixation" endgame — ~35% of random games have both players repeatedly targeting the same cell until max_turns (team-23)
5. Super-ko doesn't terminate collision-ko stalemates (team-21)
6. Territory threshold (~41/64) is essentially unreachable — 37% of random games hit max_turns (team-21)

**Best quality** (what remains after the bugs): CA birth cascades — one placement can trigger 2-3 simultaneous births (team-17, team-22 both independently witnessed triple-birth events). Also: the trap-play mechanic (team-19, Game 2 round 6) where P2's simultaneous placement killed P1's placed stone via CA — a genuinely simultaneous-only dynamic that IS in the rule table but depends on the collision mechanic actually firing.

**Verdict**: Not the R15 frontier candidate its GE rank (inflation from 16 non-trivial CA entries + simultaneous turn type) suggests. Unless both the step-loop bug and the rule-table symmetry issue are fixed, no meaningful sim×CA evaluation is possible.

---

## Cross-Cutting Discoveries

### 1. Engine bug: CA step-loop player asymmetry in simultaneous play

**Reporters**: teams 17, 18, 19, 20, 21, 22, 23 (all 7 sim×CA teams, independently)
**Severity**: CRITICAL — invalidates the R14 sim×CA signal that was driving R15 planning

**Details**: `engine_v2.py:252-254` in `step_simultaneous`:
```python
for i in range(self.game.ca_rule.steps_per_turn):
    acting_player = 1 if i % 2 == 0 else 2
    self._run_ca_step(acting_player)
```

Comment claims "alternate perspective each step" but this only holds when `steps_per_turn >= 2`. Every sim×CA game generated by R14 has `steps_per_turn=1`, so the intended alternation never fires. The CA runs exclusively from P1's perspective.

**Impact**: Every simultaneous+CA game in R14 is structurally P1-biased in a way that has nothing to do with the mechanics. GE and ELO rankings for these games are inflated by the artificial P1-win rate.

**Fix directions** (equivalent outcomes):
1. Rewrite loop to always run both perspectives regardless of `steps_per_turn`:
   ```python
   for i in range(self.game.ca_rule.steps_per_turn * 2):
       acting_player = 1 if i % 2 == 0 else 2
       self._run_ca_step(acting_player)
   ```
2. Or force generator to set `steps_per_turn >= 2` for sim×CA games
3. Or run CA twice (once per player) in a single logical step, summing effects

Teams unanimously recommended option (1) as the minimal fix.

### 2. Generator issue: CA rule tables not 1↔2 symmetric

**Reporter**: team-22 (primary diagnosis), corroborated by teams 17, 20, 23 via rule-table inspection
**Severity**: HIGH — even fixing the step-loop alone leaves a residual asymmetry

**Details**: The CA rule generator mutates individual transition entries without enforcing the invariant that the rule table should be symmetric under player swap `{0 ↔ 0, 1 ↔ 2}`. Team-22 counted 16 asymmetric entries in `992bf7dfc9f4`'s table. Concrete example: the conversion rule `(P2 neighbors=2, P1 neighbors=2, self=empty) → P1` exists; the mirror `(P1 neighbors=2, P2 neighbors=2, self=empty) → P2` does not.

**Impact**: Even with the step-loop fixed, sim+CA games can still be structurally biased by their rule tables. This compounds with the step-loop bug but is an independent issue.

**Fix direction**: In the CA rule generator/mutator, enforce symmetry. When mutating an entry `T(a, b, c) = out`, simultaneously set `T(b, a, c_swap) = out_swap` where swap maps P1↔P2.

### 3. Double-pass majority exploit — R13 failure mode recurred

**Reporters**: pilot (2/3 games), team-18 (1/3), team-19 (1/3), team-17 (1/3), team-22 (3/3), team-23 (2/2)
**Severity**: HIGH — continues to corrupt win-condition evaluation across the run

**Details**: Same as R13: when both players pass consecutively, the game ends by majority piece count regardless of whether the stated win condition (threshold, connection, territory) has been met. In R14, the exploit was especially common in simultaneous+CA games where the CA bug made territory threshold unreachable for P2 and P2 would pass to end the game.

**Status**: Fix was planned for R15 in the prior-session scope decision. R14 data confirms the priority.

### 4. GE metric continues to mis-rank relative to human judgment

| GE Rank | Game | GE | Human Mean | Δ to GE rank |
|---|---|---|---|---|
| 1 | `deb4dfe0382d` | 0.517 | 4.57 | 0 ✓ |
| 2 | `1ca924cc3062` | 0.500 | 3.40 | 0 ✓ |
| 3 | `931c58ae59b4` | 0.482 | 3.40 | +1 (tied) |
| 5 | `992bf7dfc9f4` | 0.420 | 2.86 | +1 |

Champion rank holds. But:
- Ranks 2 and 3 are indistinguishable to humans (same mean)
- The sim×CA hybrid is ranked well above nothing — its GE (0.420) is high relative to humans (2.86/10, lowest of the four) — strongly suggesting the `non_triviality` signal in GE is being inflated by the P1-only CA producing decisive outcomes

The **balance sub-metric** planned for R15 would specifically target this: an asymmetric-but-decisive game (like the sim×CA bug game) currently looks "good" to GE because its non-triviality is ~0.9. A balance term would penalize the observed >95% P1-win rate.

### 5. Secondary engine/UI issues surfaced

Found during play, not blocking but should be swept before R15:
- `play_helper.py` prints "von Neumann (face-adjacent only, no diagonals)" for Moore topology (team-13). Engine actually uses 8-neighbor Chebyshev (confirmed in `game_engine/topology.py::_build_moore_neighbors`). UI string mismatch.
- `play_helper.py show` does not expose `board_values` field — teams had to drop into Python to see effective influence/threshold state. Multiple teams (5, 6, 14) built their own helper scripts.
- `_save_state` / `_restore_state` do not preserve `step_count`, `done`, `_winner`, `_position_history` (team-5) — corrupts simulation-based scoring for agents that speculate forward.
- Custodian capture walks do not wrap on torus, but influence propagation does — real asymmetry in the engine, potentially intentional but undocumented. Affects strategic reasoning on all torus games.
- Super-ko checks don't terminate collision-ko stalemates in simultaneous play (team-21) — `consecutive_passes` resets on collisions.

---

## Failure Modes Observed

| Failure | Games affected | Team-evaluations observing |
|---|---|---|
| P1 first-move advantage (alternating games) | Champion, Rank 2, Rank 3 | 17/17 alternating evaluations |
| CA runs only from P1 perspective (sim×CA) | `992bf7dfc9f4` | 7/7 sim×CA evaluations |
| CA rule table not symmetric under player swap | `992bf7dfc9f4` | team-22 primary + 3 corroborating |
| Double-pass majority ends game without win condition | `992bf7dfc9f4` (≥5/7), pilot champ | ≥7 team-evals total |
| Capture rule inert | `931c58ae59b4` (0 captures across 15 games) | 5/5 rank-3 evaluations |
| Simultaneous collisions never fire | `992bf7dfc9f4` | 7/7 sim×CA evaluations |
| Greedy-solvable (no tactical layer) | Rank 2, Rank 3 | 6/10 evaluations |

---

## Recommendations for Run 15

The R15 scope decided before this evaluation (sim×CA coupling + balance sub-metric + double-pass fix) **remains directionally correct but requires expansion** based on these findings.

### Prerequisite engine fixes (new — not in original R15 scope)

1. **Fix CA step-loop perspective symmetry** (`engine_v2.py:252-254`) — REQUIRED before any sim×CA evaluation is meaningful. Recommended minimal patch: run both perspectives regardless of `steps_per_turn`.
2. **Enforce CA rule-table symmetry in generator** — mutation/crossover operators should maintain the invariant `T(a,b,c) swap-equivalent T(b,a,swap(c))`.

### Originally planned R15 changes (unchanged)

3. **Simultaneous × CA hybrid generator bias** — but this is now conditional on (1) and (2) landing first. Without the engine fix, the hybrid cannot be validated.
4. **Balance sub-metric in Go Essence** — this evaluation produces concrete calibration data: the sim×CA game scored Balance 1.7 in human eval but has GE non_triviality 0.894. A balance term trained on the R13 + R14 human balance scores would penalize asymmetric-but-decisive games and improve GE/human correlation.
5. **Double-pass exploit fix** — confirmed priority. Recommended: treat double-pass as draw OR require the stated win condition to fire.

### Secondary cleanups (nice-to-have)

6. Fix `play_helper.py` Moore labelling
7. Extend `play_helper.py show` to print `board_values` for influence-based games
8. Fix `_save_state` / `_restore_state` to preserve step/done/winner/position history
9. Handle collision-ko stalemates in simultaneous super-ko

### Evolutionary changes

10. **Seed R15 with `deb4dfe0382d`** — R14 human winner, the capture-as-poison mechanic is the one genuinely novel finding of the run and worth preserving in the gene pool
11. **Keep seeding `531634cee158`** (R13 human winner) — still the strongest human-validated game
12. **Do NOT seed with `992bf7dfc9f4`** — the apparent quality is bug-inflated

---

## Proposed Run 15 Configuration

```bash
# BEFORE running R15:
# 1. Patch engine_v2.py:252-254 for CA step-loop symmetry
# 2. Patch CA rule-table generator for player-swap symmetry
# 3. Patch double-pass endgame to draw or require win-condition
# 4. Add balance sub-metric to metrics/scoring.py and weight into Go Essence
# 5. Verify with test_simultaneous_integration.py + new symmetry test

.venv/bin/python run.py \
  --generations 10 \
  --population 50 \
  --training-budget 10000 \
  --num-runs 2 \
  --immigration-rate 0.25 \
  --max-dimensions 2 \
  --ca-probability 0.3 \
  --simultaneous-probability 0.5 \
  --db-path genesis_v2_run15.db \
  --seed-db genesis_v2_run14.db \
  --seed-games deb4dfe0382d 531634cee158
```

**Rationale**:
- Engine/metric fixes happen BEFORE run starts (one-time prerequisites, ~1-2 days of engineering)
- Config is the same shape as R14 except seeded with the human winner rather than the GE/bug-inflated rank 5
- Seed games enforce diversity: `deb4dfe0382d` (R14 capture-as-poison, alternating torus) + `531634cee158` (R13 human winner, hex outnumber)
- Neither seed is a sim×CA game — we rely on the generator's simultaneous-probability and CA-probability knobs to produce new hybrids under the fixed engine

---

## Files

- **Database**: `genesis_v2_run14.db` (500 games, 380+ scored)
- **Training log**: `run14_output.log`
- **Team evaluation reports**: `evaluations/run14/team-{1-23,pilot}_game{deb4dfe0382d,1ca924cc3062,931c58ae59b4,992bf7dfc9f4}.md` (24 files)
- **Team helper scripts** (side artifacts): `evaluations/run14/team-16_game{1,2,3}.py`, `team-16_driver.py`, `team14_eval_tool.py`, `team6_inspect.py`, `team4_play.py`, `team5_helper.py`, `team5_autoplay.py`, `team5_game_v2.py`, `team-23_workspace/`, plus a few others
- **Evaluation protocol**: `v2-evaluation-prompt-run14.txt` (includes pilot-surfaced caveats about pass action, torus custodian non-wrap, seat-swap limitations, and 25-min budget)

---

## Verdict

Run 14's evolutionary output is a mild disappointment — no game reaches the 7-8/10 bar and the run's "novel mechanic" (sim×CA) turns out to be an engine artefact rather than a design property. The champion (`deb4dfe0382d`) is a competent-but-imbalanced torus Othello variant with one genuinely interesting emergent feature (capture-as-poison via value-retention).

The run's **lasting value is diagnostic**:
1. **The CA step-loop bug was silently corrupting every sim+CA game in R14**. Running R15 without fixing it would have compounded the error and produced more apparently-promising-but-actually-biased champions.
2. **The CA rule-table symmetry issue is independent and equally critical** — a full fix needs both.
3. **GE continues to mis-rank games**, and specifically to reward asymmetry disguised as non-triviality. The balance sub-metric planned for R15 is now strongly motivated by empirical data (the sim×CA Balance 1.7 vs non_triv 0.89 inversion).
4. **Double-pass endings recurred in ~30% of sim×CA evaluations** — the fix remains a cheap correctness win for R15.
5. **The original R15 scope (sim×CA coupling + balance metric + double-pass fix) is still correct in direction** but needs two engine fixes added as prerequisites. None of the fixes are large; all are well-specified by this evaluation.

The project's lesson from this round mirrors R13's: **metrics lie, humans are ground truth, and the most important outputs of a run are often the bugs it surfaces rather than the games it produces**.
