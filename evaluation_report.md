# Genesis V2 Run 7 — Game Evaluation Report

**Date**: 2026-02-26
**Evaluators**: 5 Claude agent teams
**Method**: Rule comprehension, 3 strategic games per game (played by reasoning agents), strategic analysis, structured scoring
**Database**: genesis_v2_run7.db

---

## Final Rankings

| Rank | Game ID | Score | Type | Board | Capture | Win Condition |
|------|---------|-------|------|-------|---------|---------------|
| **1** | **edad1954a233** | **8/10** | 3D Go variant | 4x4x4 | Surround | Threshold |
| 2 | e5e20fdf72af | 6/10 | 2D Othello variant | 8x8 | Custodian | Threshold |
| 3 | 394d4463f023 | 4.3/10 | Overwrite flipper | varies | Custodian | varies |
| 4 | 7c3b8c4665a9 | 4/10 | 3D territory game | 4x4x4 | Custodian | Majority |
| 5 | 7fac6c8e571a | 3/10 | 2D connection race | 8x8 | Outnumber | Connection |
| 6 | 38eff40b12c3 | 2/10 | 2D outnumber influence | 8x8 | Outnumber | Threshold |
| 7 | 3e0f0fa12959 | 1.4/10 | Outnumber influence | varies | Outnumber | Threshold |
| 8 | 0401c6aa8648 | 1/10 | 6D hypercube | 2^6 | Surround | Threshold |
| 9 | 8bad3b65af8c | 1/10 | 6D surround threshold | 2^6 | Surround | Threshold |
| 10 | 4dfe47c81b5f | 1/10 | 4D multi-place | 2^4 | Surround | Territory |

---

## Detailed Evaluations

### #1: edad1954a233 — "3D Forced-Capture Go" (8/10)

**Rules**: 3D 4x4x4 grid. Alternating single placement on empty cells, constrained to adjacent-to-enemy (first move anywhere). Go-style surround capture. Threshold win (influence > 12.633). Max 100 turns.

**What makes it special**: The adjacent-to-enemy placement constraint creates a *genuinely novel* mechanic not found in any known game: **forced captures**. Because you can only place next to enemy pieces, the defender literally cannot reinforce threatened liberties — the attacker dictates the engagement zone. This creates rich tactical reading sequences reminiscent of Go's life-and-death problems, but with a fundamentally different flavor.

**Strengths**:
- Well-balanced (~50/50 outcomes across test games)
- High capture frequency (~15 captures per game)
- Long, meaningful games (average 74 turns)
- Emergent concepts: territory, influence, sacrifice, reading
- 3D topology genuinely matters — vertical connections create surprising capture sequences

**Weaknesses**:
- Many games hit the 100-turn limit (threshold may be slightly too high for "no propagation" mode)
- 3D board is hard for humans to visualize (but strategically rich)
- Win condition is effectively "majority at turn limit" since propagation is set to "none" — threshold never triggers

**Scores**: Strategic Depth 8, Emergent Complexity 8, Balance 7, Novelty 9, Replayability 7

---

### #2: e5e20fdf72af — "2D Custodian Influence" (6/10)

**Rules**: 2D 8x8 grid. Alternating single placement on any cell (including overwrite!). Custodian (Othello-style) capture with influence propagation. Threshold win.

**What makes it good**: Chain custodian captures can flip 3+ pieces in a single move, creating dramatic reversals. Compact clusters beat extended lines. Perfectly balanced (50/50).

**Weaknesses**: Games are too short (~30 turns) for deep strategy to develop. Place-anywhere (including overwrite) reduces meaningful spatial choices. Strong resemblance to Othello limits novelty.

**Scores**: Strategic Depth 6, Emergent Complexity 7, Balance 8, Novelty 5, Replayability 6

---

### #3: 394d4463f023 — "Custodian Chain Flipper" (4.3/10)

**Rules**: Custodian capture with overwrite placement (place on any cell, including occupied).

**What makes it interesting**: The overwrite + custodian flip combination creates dramatic 3-5 piece swings and real tactical decisions about when to abandon contested areas.

**Fatal flaw**: Without a ko/super-ko rule, players can infinitely recapture the same positions, creating degenerate loops.

**Fix**: Add super-ko rule or restrict to empty-cell placement only.

**Scores**: Strategic Depth 4, Emergent Complexity 5, Balance 5, Novelty 6, Replayability 3

---

### #4: 7c3b8c4665a9 — "3D Custodian Territory" (4/10)

**Rules**: 3D 4x4x4 grid. Custodian capture, majority win, 3 pieces per turn, adjacent-to-own placement.

**What makes it interesting**: Adjacent-to-own constraint creates organic territorial expansion like ink spreading. Custodian captures at 3D territory boundaries create genuinely tense moments.

**Fatal flaw**: Strong P2 advantage (won all test games ~34-30). The last player to reach a boundary executes decisive captures. First 80% of moves are mechanical expansion.

**Fix**: Reduce to 1 piece/turn, add territory-weighted scoring instead of raw piece count.

**Scores**: Strategic Depth 4, Emergent Complexity 4, Balance 3, Novelty 5, Replayability 4

---

### #5: 7fac6c8e571a — "2D Connection Race" (3/10)

**Rules**: 2D 8x8 grid. 3 pieces per turn. Outnumber capture (threshold 1). Connection win (connect opposite faces on y-axis).

**What makes it interesting**: Within-turn placement order matters for capture chains — genuine tactical sequencing.

**Fatal flaw**: Severe P1 advantage. P1 needs 3 turns to span 8 cells, P2 starts 1 turn behind. Outnumber threshold of 1 means ANY adjacent enemy is auto-captured, making defensive blocking impossible.

**Fix**: Single placement per turn, raise outnumber threshold to 3+.

**Scores**: Strategic Depth 3, Emergent Complexity 4, Balance 2, Novelty 5, Replayability 2

---

### #6-10: Broken Games (1-2/10)

All remaining games are fundamentally broken, primarily by the same root cause:

| Game | Issue | Root Cause |
|------|-------|------------|
| 38eff40b12c3 | Games end in ~13 moves | Influence threshold (12.633) too low |
| 3e0f0fa12959 | Games end in 5-7 moves | Influence threshold (6.017) too low |
| 0401c6aa8648 | P1 wins in 3 moves | Influence threshold (6.017) too low on 6D grid |
| 8bad3b65af8c | P1 forced win turn 2 | Influence threshold (6.017) too low on 6D grid |
| 4dfe47c81b5f | Deterministic P1 win | Tiny board (2^4=16) + 3 pieces/turn + low territory threshold |

---

## Systemic Analysis

### What the best games share

The top 2 games (edad1954a233 at 8/10 and e5e20fdf72af at 6/10) share these structural properties:

1. **Single placement per turn** — Multi-placement (2-3 pieces/turn) almost always creates first-player-wins scenarios
2. **Sufficient board size** — The 4x4x4 (64 cells) and 8x8 (64 cells) boards give enough room for strategy to develop
3. **Active capture mechanics** — Both have captures that fire frequently and meaningfully reshape the board
4. **Games last 30+ turns** — Enough moves for strategic depth to emerge, counter-play to develop, and position evaluation to matter

### What kills games

1. **Low influence thresholds** (4 of 10 games broken by this) — Thresholds of 6-12 with influence propagation strength ~1.6 mean 3 clustered pieces instantly win. This is the #1 killer bug.
2. **Multi-placement on small boards** — 3 pieces/turn on a 16-cell board = deterministic first-player win
3. **Outnumber capture with threshold 1** — Auto-captures any adjacent enemy, making all blocking moves worthless
4. **Missing repetition rules** — Overwrite placement without ko/super-ko creates infinite loops

### Genuine strategic merit

Only **1 of 10 games** (edad1954a233) demonstrates genuine strategic merit comparable to established abstract games. Its forced-capture mechanic is a genuinely novel contribution to abstract game design. Game #2 (e5e20fdf72af) is a competent but derivative Othello variant. Games #3-4 have interesting kernels but need significant parameter tuning. Games #5-10 are broken.

---

## Recommendations for Next Evolution Run

### Critical Fitness Function Fixes

1. **Penalize short games hard**: Any game averaging under 20 moves should get a massive Go Essence penalty. Currently, 5-move forced wins score higher than they should because rule_simplicity and strategic_depth metrics don't catch this.

2. **Add a balance metric**: Track P1 vs P2 win rate across training seeds. Games outside 40-60% P1 winrate should be heavily penalized. 6 of 10 evaluated games had severe first/second player advantages.

3. **Fix non-triviality**: This metric was always 0 across all games, which is a known bug. Fixing it would help filter out deterministic/trivially-solved games.

4. **Add minimum game length**: Reject any game where average game length < 15 moves. This alone would have filtered out 5 of the 10 broken games.

### Parameter Space Fixes

5. **Floor influence thresholds**: If using influence propagation with the threshold win condition, enforce `threshold >= 10 * strength * (1 + radius)`. The current random sampling allows catastrophically low thresholds.

6. **Constrain multi-placement**: Either remove multi-placement entirely, or only allow it on boards with 100+ cells. On small boards it's always degenerate.

7. **Cap outnumber threshold**: Outnumber capture with threshold=1 is degenerate (auto-captures everything). Enforce threshold >= 2, ideally >= 3.

### Mechanic Recommendations

8. **Favor custodian capture**: The custodian mechanic produced the most interesting games (#2, #3, #4). It creates dramatic reversals and chain-capture sequences that surround capture rarely achieves on small boards.

9. **Favor adjacency constraints**: The adjacent-to-enemy constraint in game #1 created genuinely novel forced-capture mechanics. The adjacent-to-own constraint in game #4 created organic territorial growth. Both are more interesting than "place anywhere."

10. **Add ko/super-ko rules**: Any game with overwrite placement needs repetition prevention. This should be built into the engine.

11. **Explore larger boards**: 3D games at 5x5x5 (125 cells) or 6x6x6 (216 cells) with surround capture could unlock deeper Go-like strategy. The 4x4x4 champion already shows promise.

### What to evolve toward

The ideal Genesis game based on this evaluation would be:
- **3D board, 5x5x5 or larger**
- **Single alternating placement**
- **Adjacency constraint** (to-enemy or to-own)
- **Surround or custodian capture**
- **Majority or high-threshold territory win** (not influence-threshold)
- **100+ turn average game length**

The champion game (edad1954a233) already approximates this recipe and scored 8/10. Evolving from this direction with better parameter bounds would likely produce even stronger games.

---

## Summary

**1 genuinely interesting game** out of 10 evaluated. The champion (edad1954a233, "3D Forced-Capture Go") has a novel mechanic worthy of further development. The biggest finding is that the fitness function fails to penalize degenerate games — low influence thresholds, first-player-wins, and ultra-short games all slip through. Fixing the fitness function (balance metric, minimum game length, non-triviality) would likely double the proportion of interesting games in the next run.
