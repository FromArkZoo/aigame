# Run 8 — Agent Evaluation Report

## Executive Summary

Five Claude agent teams evaluated the top 10 games from Genesis Engine Run 8 (10 generations, population 20, 20k training budget, seeded with Run 7 champion). Run 8 incorporated critical fixes: parameter bounds (influence thresholds, outnumber floors), softened fitness penalties, super-ko rule, and **seat-swapping evaluation** — the single biggest improvement, which fixed the P1-dominance artifact that plagued Run 7.

**Result: One standout game, one solid game, the rest are broken or shallow.**

Go Essence scores improved 17x over Run 7 (0.39 vs 0.023 max), but the evaluation reveals that high Go Essence scores don't always correlate with good gameplay. The #1 game by ELO (`d4015a646ae3`) is genuinely excellent — an 8/10 "Connection Go" hybrid. Most other games are crippled by tiny boards (axis_size=2 hypercubes), dead win conditions, or non-functional mechanics.

---

## Final Rankings

| Rank | Game ID | Type | Score | Key Finding |
|------|---------|------|-------|-------------|
| **1** | `d4015a646ae3` | 2D 8×8 surround/connection | **8/10** | Go×Hex hybrid — publishable quality abstract strategy game |
| **2** | `ccb36d37cf83` | 3D 4×4×4 custodian/majority | **6/10** | Solid territory game with wall-building; impressive for gen-0 seed |
| **3** | `7a2b68223c1b` | 2D 8×8 outnumber/connection | **5/10** | Wall-breaking captures are engaging; training instability |
| 4 | `1a415ff78ab4` | 5D 2^5 surround-cascade/majority | 4/10 | Cascade creates drama but total-wipeout endgame is degenerate |
| 5 | `494f36e90cc2` | 6D 2^6 surround/threshold | 4/10 | Novel 6D topology; dead win condition (cascade doesn't update board_values) |
| 6 | `119d7331627d` | 4D 2^4 outnumber/threshold | 4/10 | Dead threshold (~2.5× above theoretical max); tiny board |
| 7 | `da709f43104e` | 4D 2^4 outnumber/majority | 3/10 | 16 cells too small; 60% P1 winrate; training collapse |
| 8 | `48d54427c94d` | 4D 2^4 outnumber/majority | 3/10 | 16 cells too small; outnumber-3 captures near-impossible |
| 9 | `20149a6d72b0` | 2D 8×8 outnumber/connection | 3/10 | Both players race same axis; P1 structural advantage |
| 10 | `2b0af61726d6` | 2D 8×8 surround-cascade/connection | 2/10 | Cascade provably inert (removing stones = adding liberties) |

---

## Individual Game Evaluations

### 1. `d4015a646ae3` — "Connection Go" — 8/10

**Board**: 2D 8×8 grid (64 cells)
**Capture**: Go-style surround
**Win**: Connect bottom to top edge (y=0 to y=7)
**Propagation**: Influence (vestigial — doesn't affect win condition)

**SCORES**: Strategic Depth 8, Emergent Complexity 8, Balance 9, Novelty 8, Replayability 7

**Why it works**: The synthesis of Go capture and Hex-style connection creates strategic depth that neither mechanic produces alone. Players race to connect edges while using surround captures to remove blocking stones. This creates a "capture or go around?" dilemma that is genuinely novel. Go-like life/death reading combines with Hex-like connection analysis. Near-perfect 50/50 balance in both random and trained play. 92% of games end by connection (not timeout).

**KILLER FLAWS**: Influence propagation adds 4 parameters for zero gameplay effect — should be removed.
**BEST QUALITY**: Novel Go×Hex hybrid creating layered decision-making.
**IMPROVEMENT**: Remove vestigial influence; consider pie rule for formal first-player balance; try 10×10 or 12×12.

---

### 2. `ccb36d37cf83` — "3D Custodian Expansion" — 6/10

**Board**: 3D 4×4×4 cube (64 cells)
**Capture**: Custodian (Othello-style flanking along axes, flips enemy to your color)
**Win**: Majority at game end
**Constraint**: Must place adjacent to own pieces (first move anywhere)

**SCORES**: Strategic Depth 6, Emergent Complexity 7, Balance 7, Novelty 5, Replayability 6

**Why it works**: The adjacent-to-own constraint creates territorial growth — players expand connected blobs that collide. Custodian captures along 6 axes in 3D create wall-building and flanking as emergent strategic concepts. Territorial squeeze (expanding faster to limit opponent's options) is a viable strategy. Impressively coherent for a generation-0 seed game.

**KILLER FLAWS**: Custodian captures are rare in random play; 50% training collapse rate; no decisive ending.
**BEST QUALITY**: Genuine territory game with wall-building and 3D flanking dynamics.
**IMPROVEMENT**: Add territory win condition (>60% control); increase to 5×5×5 (125 cells); consider diagonal custodian captures.

---

### 3. `7a2b68223c1b` — "Outnumber Connection" — 5/10

**Board**: 2D 8×8 grid (64 cells)
**Capture**: Outnumber (threshold=2 — adjacent enemy removed if ≥2 of its neighbors are yours)
**Win**: Connect top to bottom edge
**Propagation**: Influence (vestigial)

**SCORES**: Strategic Depth 6, Emergent Complexity 5, Balance 6, Novelty 5, Replayability 5

**Why it works**: Outnumber-2 capture creates a genuine tactical layer — coordinating 2 stones to break through a wall is a real decision balancing tempo cost against positional gain. Games average 62 turns with some ending by connection. Thick-vs-thin path building creates meaningful choices.

**KILLER FLAWS**: Catastrophic training instability (70% vs random in one run, 0% in the other); vestigial influence.
**BEST QUALITY**: Wall-breaking with coordinated capture is an engaging novel mechanic.
**IMPROVEMENT**: Remove influence propagation; investigate training instability; possibly try outnumber threshold 3.

---

### 4. `1a415ff78ab4` — "5D Surround-Cascade" — 4/10

**Board**: 5D 2^5 hypercube (32 cells)
**Capture**: Go-style surround with cascade (chain-reaction removal up to 10 iterations)
**Win**: Majority

**SCORES**: Strategic Depth 4, Emergent Complexity 5, Balance 8, Novelty 6, Replayability 4

**Why it's interesting**: Cascade creates dramatic total-wipeout events — a single placement on a nearly-full board can remove ALL opponent pieces. This forces "group fragmentation" as emergent defense and creates an "endgame chicken" dynamic.

**KILLER FLAWS**: Total wipeout cascade reduces endgame to who places last; "anywhere" placement eliminates territory.
**BEST QUALITY**: Remarkably consistent training (68-90% vs random across 4 runs); cascade as emergent drama.
**IMPROVEMENT**: Increase axis_size to 3 (243 cells); add adjacency constraint; cap cascade radius.

---

### 5. `494f36e90cc2` — "6D Hypercube Go" — 4/10

**Board**: 6D 2^6 hypercube (64 cells, 6 neighbors each)
**Capture**: Go-style surround with cascade
**Win**: Threshold (board_values > 22.6) — **DEAD: cascade doesn't update board_values**

**SCORES**: Strategic Depth 4, Emergent Complexity 5, Balance 7, Novelty 7, Replayability 4

**KILLER FLAW**: Win condition unreachable. Every game runs to 100 turns → majority.
**BEST QUALITY**: Go on a 6D hypercube is genuinely novel; cascade captures in 6D create unique chain dynamics.
**IMPROVEMENT**: Switch to influence propagation so threshold fires; or change win to territory.

---

### 6. `119d7331627d` — "4D Hypercube Influence" — 4/10

**Board**: 4D 2^4 hypercube (16 cells)
**Capture**: Outnumber (threshold=3)
**Win**: Threshold (>45.07) — **DEAD: ~2.5× above theoretical maximum**

**SCORES**: Strategic Depth 4, Emergent Complexity 3, Balance 9, Novelty 5, Replayability 3

**KILLER FLAW**: Threshold unreachable; 16 cells too small; outnumber-3 on 4-neighbor cells makes captures near-impossible.
**BEST QUALITY**: Perfect 50/50 balance across 8 training runs.
**IMPROVEMENT**: Lower threshold to ~12-15; increase to 3^4=81 cells; lower outnumber threshold to 2.

---

### 7. `da709f43104e` — "4D Hypercube Majority" — 3/10

**Board**: 4D 2^4 hypercube (16 cells)
**Capture**: Outnumber (threshold=3)
**Win**: Majority

**SCORES**: Strategic Depth 3, Emergent Complexity 3, Balance 3, Novelty 5, Replayability 2

**KILLER FLAW**: 16 cells = too small; 60% P1 winrate; one training run scored 0% vs random.
**IMPROVEMENT**: Scale to 3^4=81 cells; lower capture threshold to 2.

---

### 8. `48d54427c94d` — "4D Outnumber Majority" — 3/10

**Board**: 4D 2^4 hypercube (16 cells)
**Capture**: Outnumber (threshold=3)
**Win**: Majority

**SCORES**: Strategic Depth 3, Emergent Complexity 3, Balance 7, Novelty 5, Replayability 3

**KILLER FLAW**: 16 cells too small; outnumber-3 on 4-neighbor cells = 75% neighbor control required; captures near-impossible.
**IMPROVEMENT**: Increase axis_size to 3; lower outnumber threshold to 2.

---

### 9. `20149a6d72b0` — "8×8 Connection Race" — 3/10

**Board**: 2D 8×8 grid (64 cells)
**Capture**: Outnumber (threshold=2)
**Win**: Connect top to bottom (both players same axis)

**SCORES**: Strategic Depth 3, Emergent Complexity 3, Balance 3, Novelty 4, Replayability 3

**KILLER FLAW**: Both players connect the SAME axis → pure race → P1 structural advantage. Outnumber-2 kills all defensive play (blocking stones immediately captured).
**IMPROVEMENT**: Different connection axes per player (Hex-style); increase outnumber threshold to 3.

---

### 10. `2b0af61726d6` — "Cascade Go-Connection" — 2/10

**Board**: 2D 8×8 grid (64 cells)
**Capture**: Go-style surround with cascade
**Win**: Connect left to right edge

**SCORES**: Strategic Depth 3, Emergent Complexity 2, Balance 8, Novelty 3, Replayability 2

**KILLER FLAW**: Cascade is **provably non-functional** with surround capture — removing stones creates liberties (empty cells), never destroys them. The game's signature mechanic literally does nothing. Connection almost never achieved; games are 100-turn majority grinds.
**IMPROVEMENT**: Replace cascade with influence propagation; use custodian capture instead of surround; shrink board.

---

## Cross-Cutting Analysis

### What the best games share

1. **2D grids at 8×8** — The top 3 games by evaluation score are all on 2D grids. This size provides enough cells (64) for genuine strategy while keeping the topology comprehensible.
2. **Connection win conditions** — The top game uses connection-to-edges, creating directional goals and blocking incentives that majority/threshold lack.
3. **Working capture mechanics** — The champion's Go-style surround captures fire regularly (~5.9/game) and create meaningful tactical decisions.
4. **Games that end before timeout** — The champion ends by connection 92% of the time at ~73 turns. Lower-rated games almost always hit the 100-turn cap.

### What the worst games share

1. **axis_size=2 hypercubes** — 6 of the bottom 7 games use binary hypercubes (16-64 cells). The resulting boards are too small and too symmetric for strategic depth. All vertices are structurally equivalent (vertex-transitive), eliminating positional advantages.
2. **Dead win conditions** — 3 games have threshold win conditions that are mathematically unreachable due to mismatched propagation mechanics or impossibly high thresholds.
3. **Non-functional mechanics** — Cascade propagation is inert with surround capture (a fundamental incompatibility the engine doesn't check for). Influence propagation is vestigial in 4 games (doesn't affect any win condition).
4. **Training instability** — 6 of 10 games had at least one training run collapse to 0% vs random, suggesting degenerate local optima in the strategy landscape.

### Comparison with Run 7

| | Run 7 Champion | Run 8 Champion |
|--|--|--|
| Game | `edad1954a233` | `d4015a646ae3` |
| Score | 8/10 | 8/10 |
| Board | 3D 4×4×4 | 2D 8×8 |
| Capture | Surround (forced by adjacency constraint) | Surround (Go-style) |
| Win | Threshold | Connection |
| Key mechanic | Forced-capture from adjacent-to-enemy | Go capture + Hex connection hybrid |
| Novel? | Yes — forced capture is unique | Yes — Go×Hex synthesis is unique |

Both champions scored 8/10 — comparable quality. Run 8's champion is arguably more elegant (simpler rules, cleaner mechanics) while Run 7's had a more surprising novel mechanic (forced captures).

---

## Recommendations for Run 9

### Critical Fixes

1. **Ban axis_size=2 for all dimensions** — Binary hypercubes consistently produce tiny, shallow games. Minimum axis_size should be 3 (or 4 for 2D/3D).

2. **Validate win condition reachability** — Add a pre-training check that the win condition can theoretically fire given the propagation type. Specifically:
   - Threshold win + cascade propagation = INVALID (cascade doesn't update board_values)
   - Threshold win should check that the threshold is achievable given board size × strength × propagation
   - Connection win should ensure different connection axes exist (or assign different axes per player)

3. **Remove or fix cascade propagation** — Cascade is provably non-functional with surround capture (removing stones adds liberties). Either: (a) only pair cascade with custodian capture, or (b) redesign cascade semantics, or (c) remove it entirely.

4. **Remove vestigial influence** — 4 of 10 games have influence propagation that affects nothing. If influence doesn't feed into the win condition, don't generate it — it adds rule complexity without gameplay.

### Evolution Improvements

5. **Favor 2D grids and connection wins** — The top games all use 2D boards with connection. Seed Run 9 with `d4015a646ae3` and bias generation toward 2D grids (8×8 to 13×13) with connection win conditions.

6. **Add training stability to fitness** — 6/10 games had catastrophic training collapse in at least one run. Add a penalty for high variance across training runs (e.g., if min(vs_random) < 0.2 × max(vs_random), penalize).

7. **Add "games end before timeout" metric** — Games where >50% hit max_turns are generally low-quality. Penalize high average game length relative to max_turns.

8. **Custodian capture deserves more exploration** — The #2 game (3D custodian) showed genuine strategic depth. Custodian capture + territory/majority win + adjacency constraints could be a rich design space.

9. **Increase training budget for promising games** — 20k steps may not be enough to reveal deep strategies. Consider a two-phase approach: quick 10k screening, then 50k for top candidates.
