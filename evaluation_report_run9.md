# Run 9 -- Agent Evaluation Report

## Executive Summary

Five Claude agent teams evaluated the top 10 games from Genesis Engine Run 9 (10 generations, population 50, 10k training budget, 25% immigration). Run 9 used the same parameter bounds and fitness fixes from Run 8, with a larger population (50 vs 20) and lower training budget (10k vs 20k).

**Result: Two strong games, two solid games, three middling, three broken.**

The top games continue the Go x Hex hybrid pattern that dominated Run 8. The Run 9 champion (`4772ff161000`) is essentially small-board Go with a territory-counting win condition -- strategically deep but not novel. The best *novel* game is `bcd45c85f87d`, a Go x Hex connection hybrid nearly identical to Run 8's champion. The bottom three games are all broken by majority win conditions that either create parallel solitaire or enable pass exploits.

**Key finding: Majority win condition is consistently the worst performer.** All three games scoring 3/10 or below use majority wins. Connection and territory wins continue to produce the best games.

---

## Final Rankings

| Rank | Game ID | Type | Score | Key Finding |
|------|---------|------|-------|-------------|
| **1** | `4772ff161000` | 2D 8x8 surround/territory | **7/10** | Small-board Go with 59.4% threshold; deep strategy but limited novelty |
| **2** | `bcd45c85f87d` | 2D 8x8 surround/connection | **7/10** | Go x Hex hybrid; dual-purpose stones, rich tactical play |
| **3** | `fc4e82bd061b` | 2D 8x8 surround/connection | **6/10** | Go x Hex hybrid; captures break chains, intersection control emerges |
| **4** | `384b3e1af682` | 3D 4x4x4 surround/threshold | **5/10** | Novel 3D + influence; but "cluster and accumulate" dominates |
| **5** | `1ac8f19581ca` | 3D 4x4x4 surround/connection | **5/10** | 3D Hex-Go; novel spatial reasoning but board too small (4-step paths) |
| **6** | `404ace5c1863` | 3D 4x4x4 surround/connection | **5/10** | Forced-proximity placement is brilliant; but 3.5 avg game length in training |
| **7** | `cce37f4762c4` | 2D 8x8 outnumber/connection | **5/10** | Competent Hex variant; balanced but low novelty, rare captures |
| 8 | `6009cf66eb3a` | 3D 4x4x4 surround/majority | **3/10** | Adjacent-to-own + 3D = parallel solitaire; capture impossible |
| 9 | `dcd36397091e` | 2D 8x8 surround/majority | **2/10** | Blob growth race; vestigial capture; every game identical |
| 10 | `f9eba2b4bf19` | 3D 4x4x4 surround/majority | **2/10** | Double-pass exploit; trained agents end games in 3.5 moves |

---

## Individual Game Evaluations

### 1. `4772ff161000` -- "Small-Board Go" -- 7/10

**Board**: 2D 8x8 grid (64 cells)
**Capture**: Go-style surround
**Win**: Territory -- own >59.4% of cells (39+ stones on board)
**Propagation**: None

**SCORES**: Strategic Depth 7, Emergent Complexity 7, Balance 7, Novelty 4, Replayability 7

**Why it works**: This is essentially Go on a small board with a stone-counting win condition (not enclosed area). The 59.4% territory threshold creates dramatic endgame swings -- one large capture can completely reverse the position. All core Go concepts emerge naturally: liberties, life/death, influence, sente/gote, and thickness. Training shows perfect 50/50 balance. Games average ~90 moves with deep reading trees.

**KILLER FLAWS**: Limited novelty -- it's a Go variant, not a fundamentally new game. The capture threshold=3 parameter is vestigial (does nothing for surround capture). No ko rule means potential cycling (super-ko exists but adds complexity). The 59.4% threshold can lead to prolonged endgames in clearly decided positions.

**BEST QUALITY**: The territory-counting win condition (stones on board) combined with the high threshold creates endgame drama that's actually *more* exciting than Go's typically gentle endgame. Large capture swings are possible until the very end.

**IMPROVEMENT**: Add a connection bonus (largest group counts double) to differentiate from Go. Consider pie rule for formal first-player balance.

---

### 2. `bcd45c85f87d` -- "Hex-Go" -- 7/10

**Board**: 2D 8x8 grid (64 cells)
**Capture**: Go-style surround
**Win**: Connection -- P1 connects left-right (x=0 to x=7), P2 connects top-bottom (y=0 to y=7)
**Propagation**: None

**SCORES**: Strategic Depth 7, Emergent Complexity 7, Balance 7, Novelty 5, Replayability 7

**Why it works**: The marriage of Hex-style connection racing with Go-style capture creates a game where every stone serves dual purposes -- both advancing your connection and threatening/defending captures. The 8x8 board hits a sweet spot: large enough for deep strategy, small enough for decisive games. Rich emergent concepts: territory, influence, ladders, cutting points, fork threats, and large-scale captures. Very similar to Run 8's champion (`d4015a646ae3`) -- same evolutionary lineage.

**KILLER FLAWS**: Self-capture allowed (stones in 0-liberty positions survive), weakening capture as strategic tool. 4-connectivity blocking may be too strong (single stone blocks all orthogonal paths). Random play shows P2 bias (73%) suggesting subtle structural asymmetry.

**BEST QUALITY**: The interaction between building resilient (2-wide) paths and the opponent's ability to capture cutting points creates genuine strategic depth that neither Hex nor Go produces alone.

**IMPROVEMENT**: Switch to 6-connectivity (add diagonals) for more fluid Hex-like connection flow. Add pie/swap rule for first-player balance.

---

### 3. `fc4e82bd061b` -- "Connection Go" -- 6/10

**Board**: 2D 8x8 grid (64 cells)
**Capture**: Go-style surround
**Win**: Connection -- P1 left-right, P2 top-bottom
**Propagation**: None

**SCORES**: Strategic Depth 6, Emergent Complexity 7, Balance 6, Novelty 7, Replayability 6

**Why it works**: Another Go x Hex hybrid. Multiple viable strategies emerge: racing, wall-blocking, intersection control, and capture-assisted chain restoration. Captures can break opponent chains (unlike pure Hex), creating dynamic back-and-forth. The intersection control mechanic -- cells that serve both offense and defense -- creates critical decision points. Games go 65-78 moves and end by connection.

**KILLER FLAWS**: One training run collapsed completely (0.04 vs random), suggesting potential degeneracy. Orthogonal-only adjacency makes connections fragile. First-mover advantage at intersection points.

**BEST QUALITY**: Captures breaking opponent chains adds a dynamic that pure Hex lacks. Multiple connection paths with blocking creates rich positional play.

**IMPROVEMENT**: Add swap rule; consider Moore adjacency (8-connected) to reduce fragility; or reduce to 6x6 to tighten games.

---

### 4. `384b3e1af682` -- "3D Influence Go" -- 5/10

**Board**: 3D 4x4x4 grid (64 cells)
**Capture**: Go-style surround
**Win**: Threshold -- total influence across own cells exceeds 51.416
**Propagation**: Influence (strength 1.714, decay 0.471, radius 2)

**SCORES**: Strategic Depth 5, Emergent Complexity 5, Balance 6, Novelty 6, Replayability 5

**Why it works**: The 3D spatial reasoning is genuinely challenging. Understanding adjacency across layers, planning surrounding operations in 3D, and optimizing influence clusters creates a unique cognitive experience. This game has the highest raw Go Essence score (0.301) in Run 9.

**KILLER FLAWS**: The influence threshold (51.416) is trivially reachable with ~30 isolated stones (30 * 1.714 = 51.42), meaning the game often degenerates into "fill the board first." P1 advantage in random play (8/12 wins). "Cluster and accumulate" strategy dominates, reducing diversity. 4x4x4 too small for deep strategy.

**BEST QUALITY**: 3D spatial reasoning is genuinely novel and engaging.

**IMPROVEMENT**: Increase threshold to ~80+ to force denser clustering and more conflict. Consider making influence decay *between* friendly stones to create clustering-vs-spreading tension.

---

### 5. `1ac8f19581ca` -- "3D Hex-Go" -- 5/10

**Board**: 3D 4x4x4 grid (64 cells)
**Capture**: Go-style surround
**Win**: Connection -- P1 connects z=0 to z=3, P2 connects x=0 to x=3
**Propagation**: None

**SCORES**: Strategic Depth 5, Emergent Complexity 6, Balance 7, Novelty 7, Replayability 5

**Why it works**: 3D path-finding with Go capture is genuinely novel. The dimensional asymmetry (P1 crosses z, P2 crosses x) creates different spatial reasoning for each player. Fork threats and capture-for-tempo create meaningful emergent play. Perfect 50/50 balance in training.

**KILLER FLAWS**: Board too small -- minimum connection path is only 4 stones. Self-capture allowed. Captures rarely matter; most games end by connection before captures become decisive. The 4-step minimum crossing is too short for rich gameplay.

**BEST QUALITY**: 3D topology creates novel spatial reasoning challenges.

**IMPROVEMENT**: Increase to 5x5x5 or 6x6x6 to create longer minimum paths.

---

### 6. `404ace5c1863` -- "3D Forced-Proximity Connection" -- 5/10

**Board**: 3D 4x4x4 grid (64 cells)
**Capture**: Go-style surround
**Win**: Connection -- P1 connects z=0 to z=3, P2 connects x=0 to x=3
**Placement**: Must place adjacent to enemy stones (after opening)
**Propagation**: None

**SCORES**: Strategic Depth 5, Emergent Complexity 7, Balance 8, Novelty 8, Replayability 4

**Why it works**: The forced-proximity placement mechanic is the most genuinely novel concept in this run. Being forced to engage with the enemy on every move creates combative, interleaved play unlike any standard connection game. The 3D routing adds meaningful spatial reasoning. Perfect 50/50 balance.

**KILLER FLAWS**: Average game length of only 3.5 moves in training -- strongly suggests a degenerate shortcut where skilled players win almost immediately. The game may be "solved" at a shallow search depth.

**BEST QUALITY**: The forced-proximity mechanic is brilliant. Same mechanic that created Run 7's champion's novel forced-capture dynamic.

**IMPROVEMENT**: Increase to 5x5x5+ to make instant connections impossible. The mechanic deserves more space to breathe.

---

### 7. `cce37f4762c4` -- "Outnumber Hex" -- 5/10

**Board**: 2D 8x8 grid (64 cells)
**Capture**: Outnumber (threshold 3)
**Win**: Connection -- P1 left-right, P2 top-bottom
**Propagation**: None

**SCORES**: Strategic Depth 5, Emergent Complexity 5, Balance 7, Novelty 3, Replayability 5

**Why it works**: Competent Hex variant. Cross-directional connection goals work well. Games are balanced (50/50), go 60-70 moves, and end by connection rather than timeout. The basic gameplay loop works.

**KILLER FLAWS**: Low novelty -- essentially Hex on a square grid. Outnumber(3) captures are too rare (need 3 of 4 neighbors) to meaningfully differentiate from standard Hex. Trained-vs-random of only 64-70%.

**BEST QUALITY**: The proven Hex dynamic of inherent path intersection. Solid, functional gameplay.

**IMPROVEMENT**: Lower outnumber threshold to 2 for more frequent, impactful captures.

---

### 8. `6009cf66eb3a` -- "3D Blob Race" -- 3/10

**Board**: 3D 4x4x4 grid (64 cells)
**Capture**: Go-style surround
**Win**: Majority
**Placement**: Adjacent to own stones
**Propagation**: None

**SCORES**: Strategic Depth 3, Emergent Complexity 3, Balance 6, Novelty 4, Replayability 3

**Why it works**: It doesn't, strategically. Well-balanced but boring.

**KILLER FLAWS**: Adjacent-to-own + 3D = parallel solitaire. Surround capture is nearly impossible in 3D (6 neighbors per cell). Players can't interact until blobs collide. `target: any` allows placing on occupied cells (wasted moves). No interesting mid-game decisions.

**BEST QUALITY**: Organic blob growth patterns are visually interesting. Well-balanced.

**IMPROVEMENT**: Switch to connection win condition; allow placement anywhere; or move to 2D.

---

### 9. `dcd36397091e` -- "Territorial Blob Race" -- 2/10

**Board**: 2D 8x8 grid (64 cells)
**Capture**: Go-style surround (threshold 2 -- groups need 2+ liberties to survive)
**Win**: Majority
**Placement**: Adjacent to own stones
**Propagation**: None

**SCORES**: Strategic Depth 2, Emergent Complexity 2, Balance 7, Novelty 3, Replayability 2

**KILLER FLAWS**: No meaningful interaction -- parallel solitaire. Both players grow blobs independently until frontiers meet. Capture threshold-2 punishes the only interesting tactical option (thin extensions) and is otherwise vestigial. Games determined by opening placement. Trained-vs-random of only 52-68% confirms strategy barely matters. Every game looks identical: grow blob, meet frontier, count.

**BEST QUALITY**: Aesthetically pleasing organic growth patterns. Well-balanced.

**IMPROVEMENT**: Change win condition to connection; or replace adjacent_to_own with anywhere placement.

---

### 10. `f9eba2b4bf19` -- "3D Contact Go (Broken)" -- 2/10

**Board**: 3D 4x4x4 grid (64 cells)
**Capture**: Go-style surround
**Win**: Majority (double-pass ends game immediately)
**Placement**: Adjacent to enemy stones
**Propagation**: None

**SCORES**: Strategic Depth 2, Emergent Complexity 3, Balance 3, Novelty 5, Replayability 2

**KILLER FLAWS**: Double-pass + majority = games end in 3-4 moves. P1 places, P2 places, P1 places (2-1 lead), both pass -> P1 wins. One training run showed 100% P1 winrate. Optimal play completely bypasses all game mechanics. The 3D forced-contact concept has genuine potential but majority win condition kills it.

**BEST QUALITY**: The concept of forced-contact Go in 3D is genuinely interesting. Surround capture across z-layers creates complex group dynamics in casual play.

**IMPROVEMENT**: Replace majority with connection or territory win. Add minimum game length before pass-ending is allowed.

---

## Cross-Cutting Analysis

### What the Best Games Share
1. **2D 8x8 boards**: All three top games (7/10, 7/10, 6/10) are 2D 8x8. The board size provides enough space for strategic depth while keeping games finite.
2. **Connection or territory win conditions**: These create directional goals (connection) or accumulation pressure (territory) that force interaction.
3. **Surround capture**: Go-style capture is the most strategically productive mechanic -- it creates liberties, life/death, and group management.
4. **Unconstrained placement**: All three top games allow placing anywhere (no adjacency constraints), enabling invasion, disruption, and long-range planning.

### What the Worst Games Share
1. **Majority win condition**: All three bottom games (3/10, 2/10, 2/10) use majority. Majority creates no directional goals, rewards passive play, and enables pass exploits.
2. **Adjacent-to-own placement**: Two of three bottom games restrict placement to adjacent-to-own, creating parallel solitaire with no interaction until blobs collide.
3. **3D 4x4x4 boards**: Two of three bottom games are 3D. The 6-neighbor adjacency makes captures nearly impossible, removing the most strategically productive mechanic.

### Structural Patterns

| Property | Top 3 (avg 6.7/10) | Bottom 3 (avg 2.3/10) |
|----------|--------------------|-----------------------|
| Board | 2D 8x8 (all 3) | 3D 4x4x4 (2/3) |
| Win condition | Connection (2), Territory (1) | Majority (all 3) |
| Capture type | Surround (all 3) | Surround (all 3) |
| Placement | Anywhere (all 3) | Adjacent-to-own (2/3) |
| Avg game length (trained) | 60-90 moves | 3.5-67 moves |
| Trained vs random | 70-95% | 52-68% |

### Run 9 vs Run 8 Comparison
- **Run 8 champion** (`d4015a646ae3`): 8/10 -- 2D 8x8 surround/connection ("Connection Go")
- **Run 9 champion** (`4772ff161000`): 7/10 -- 2D 8x8 surround/territory ("Small-Board Go")
- **Run 9 runner-up** (`bcd45c85f87d`): 7/10 -- 2D 8x8 surround/connection (same lineage as Run 8 champion)

Run 9's best games are comparable to Run 8 but didn't clearly surpass the Run 8 champion. The Go x Hex connection pattern continues to be the most successful game archetype. The Run 9 champion's territory win condition is a genuine alternative but scored slightly lower due to limited novelty.

### Novel Mechanics Worth Preserving
1. **Forced-proximity placement** (`404ace5c1863`): Adjacent-to-enemy creates interleaved, combative play. Brilliant concept that needs a larger board.
2. **3D connection with Go capture** (`1ac8f19581ca`): The dimensional asymmetry creates novel spatial reasoning. Needs larger boards (5x5x5+).
3. **High territory threshold** (`4772ff161000`): The 59.4% threshold creates dramatic endgame swings unlike standard Go scoring.

---

## Recommendations for Run 10

1. **Ban majority win condition** (or heavily penalize it). 100% of majority games scored 3/10 or below across both Run 8 and Run 9 evaluations. It consistently produces either parallel solitaire or pass exploits.

2. **Enforce minimum board size for 3D**: 4x4x4 (64 cells) is consistently too small for 3D games. Connection paths are too short (4 steps), captures are too hard (6 neighbors), and strategy space is limited. Require 5x5x5 minimum (125 cells) for 3D games.

3. **Penalize double-pass exploits**: Add a fitness penalty for games where trained agents average <10 moves. This would catch the `f9eba2b4bf19` pattern where majority + pass = instant win.

4. **Seed with the Go x Hex archetype**: The 2D 8x8 surround/connection pattern has produced the best games in both Run 8 and Run 9. Seed Run 10 with `bcd45c85f87d` and `d4015a646ae3` to explore variations.

5. **Explore 6-connectivity on square grids**: Multiple evaluators noted that 4-connectivity makes blocking too powerful. Adding diagonal adjacency could create more fluid connection games.

6. **Fix adjacent-to-own for majority games**: If majority must exist, combine it with anywhere placement so players can disrupt each other. Adjacent-to-own + majority is always parallel solitaire.

7. **Investigate forced-proximity on larger boards**: The adjacent-to-enemy mechanic (`404ace5c1863`) is the most novel concept in this run. It deserves exploration on 5x5x5+ boards with connection win conditions.
