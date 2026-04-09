# Run 9 Evaluation Report — Team 1

**Evaluator:** Team 1 Agent
**Games Evaluated:** `4772ff161000` (Run 9 Champion), `384b3e1af682` (Highest Go Essence)

---

## Game 1: `4772ff161000`

### Phase 1 — Rule Comprehension

**Rules Summary:** Players alternate placing stones on an 8x8 grid (von Neumann adjacency, no diagonals). Go-style surround capture removes groups with zero liberties. First player to own >59.4% of cells (39+ stones on board) wins. Max 114 turns. Pass is available.

**Board:** 2D 8x8 grid, 64 cells, orthogonal adjacency only.

**Key Mechanics:**
- **Placement:** One stone per turn on any empty cell. No placement restrictions.
- **Capture:** Standard Go surround — when a connected group has no empty adjacent cells (liberties), it is removed. The `threshold=3` parameter is unused for surround capture (only applies to outnumber capture type).
- **Win Condition:** Territory — own >59.4% of cells. This counts stones currently on the board, not enclosed area. 39 stones needed out of 64.
- **Propagation:** None (the propagation parameters exist but prop_type is "none").

**Degenerate Flags:** The 59.4% territory threshold is quite high — you need a substantial lead (39 vs max 25 for opponent). This means the game often goes deep, with many captures and recaptures before one side accumulates enough. Games that reach 114 turns without either side hitting 59.4% go to a draw by timeout, but in practice P1 (the side with more total turns) would often have a slight stone advantage.

### Phase 2 — Strategic Play

**Random Game Observations (12 games):**
- P1 wins: 4, P2 wins: 8 (from random play)
- Game length range: 79-114 moves, average ~90
- Games frequently feature massive late-game captures that swing the board
- The endgame is often decided by a single large capture chain

**Self-Play Game Analysis:**

*Game 1: Territory Building.* I played both sides building competing walls — P1 claiming center-right, P2 claiming left. The game developed a clear frontier. A critical moment came when P2 played at (6,7), capturing P1's stone at (6,6) which was surrounded by O stones on all 4 orthogonal sides. This single capture broke P1's wall and created a cascading territorial collapse.

*Game 2: Capture Mechanics Testing.* Confirmed that:
- Single stones are captured when all 4 orthogonal neighbors are enemy
- Groups of any size (2, 3, 4+) are captured when the entire group has 0 liberties
- The surround threshold=3 parameter has no effect — capture is pure Go-style

*Game 3: Wall vs. Spread Strategy.* Tried spreading stones widely (P1) vs. building connected walls (P2). Connected walls proved stronger because they create mutual liberties and are harder to surround. Isolated stones are vulnerable to being picked off one at a time.

**Key Strategic Observations:**
- **Connection is survival** — connected groups share liberties. An isolated stone in the center has 4 liberties; a 2-stone line has 6.
- **Edge and corner play is important** — edge stones have only 2-3 liberties, making them easier to capture, but also reducing the investment needed to surround them.
- **The 59.4% threshold creates endgame drama** — neither side can win early, so the game builds to a climactic late-game where large captures determine the winner.
- **Recapture cycles are common** — when a group is captured, the freed cells become available, and the opponent often places there, creating back-and-forth capture chains.

### Phase 3 — Strategic Analysis

**Distinct Strategies:**
1. *Solid framework building* — connect stones into large groups with many liberties
2. *Invasion/reduction* — play inside opponent's framework to deny territory
3. *Capture racing* — set up simultaneous threats to capture multiple groups
4. *Edge claiming* — secure edges first where stones are cheaper to defend

**Meaningful Counter-play:** Yes. Every move creates both offensive (threatening to surround) and defensive (adding liberties) value. There's genuine tension between expanding territory and protecting existing groups.

**Short-term vs. Long-term Tension:** Moderate. Playing aggressively to capture stones NOW risks leaving your own groups under-defended. But playing too passively lets the opponent build an uncatchable lead.

**Emergent Concepts:**
- *Liberties* (exactly as in Go) — the lifeblood of groups
- *Influence/thickness* — walls radiate control over nearby empty cells
- *Sente/Gote* — initiative matters when there are mutual threats
- *Life and death* — can this group survive? Classic Go concept applies

**Topology Impact:** The 8x8 size is appropriate — large enough for strategic play but small enough that the board fills up and creates capture pressure. Von Neumann adjacency (no diagonals) makes groups easier to surround than in Go, so the game feels more aggressive.

**Comparison to Known Games:** This is essentially **Go on a small board with a territory-count win condition**. The key difference from real Go is: (1) no ko rule (super-ko exists but wasn't tested), (2) territory counts stones on board rather than enclosed area, (3) the 59.4% threshold rather than komi. It's a competent Go variant that plays well on 8x8.

### Phase 4 — Verdict

```
Game ID: 4772ff161000
Rules Summary: Go-style surround capture on 8x8 grid; win by owning >59.4% of cells.
Topology: 2D 8x8 grid, von Neumann (orthogonal) adjacency

SCORES (1-10):
  Strategic Depth: 7 — Go-style liberties create deep reading trees; territory threshold adds endgame calculation
  Emergent Complexity: 7 — Life/death, influence, sente/gote all emerge naturally from simple rules
  Balance: 7 — Training shows perfect 50/50 P1/P2; random play slightly favors P2 (survives to endgame better)
  Novelty: 4 — Essentially small-board Go with a different scoring system; the 59.4% threshold is an interesting twist but not revolutionary
  Replayability: 7 — Large decision tree, multiple viable strategies, no two games play the same
  Overall "Would I play this again?": 7

KILLER FLAWS:
- The capture threshold=3 parameter is completely unused — it does nothing for surround capture
- No traditional ko rule means some positions could cycle (super-ko exists but adds complexity)
- The 59.4% threshold means games must go deep; there's no way to "resign" a position early, leading to prolonged endgames in clearly decided positions
- Novelty is limited — this is a Go variant, not a fundamentally new game

BEST QUALITY: The territory-counting win condition (stones on board, not enclosed area) combined with the 59.4% threshold creates dramatic endgame swings where one large capture can completely reverse the position. This makes the game more exciting than Go's typically gentle endgame.

IMPROVEMENT IDEAS: Add a connection-based bonus — e.g., your largest connected group counts double for territory purposes. This would add a novel strategic dimension beyond pure Go and reward building cohesive positions over scattered stones.
```

---

## Game 2: `384b3e1af682`

### Phase 1 — Rule Comprehension

**Rules Summary:** Players alternate placing stones on a 3D 4x4x4 grid (von Neumann adjacency). Go-style surround capture (threshold=1, same as standard). Each stone radiates influence (strength 1.714, decay 0.471, radius 2). Win when your total influence on your own cells exceeds 51.416.

**Board:** 3D 4x4x4 grid, 64 cells, face-adjacent only (each cell has up to 6 neighbors: +/-x, +/-y, +/-z).

**Key Mechanics:**
- **Placement:** One stone per turn on any empty cell.
- **Capture:** Standard Go surround (threshold=1 = standard). Groups with 0 liberties are removed.
- **Propagation:** Influence type. Each stone radiates influence to nearby friendly cells. Self-influence on own cell: 1.714. Distance-1 neighbors: 1.714 * 0.471 = 0.808. Distance-2: 1.714 * 0.471^2 = 0.380.
- **Win Condition:** Threshold — total influence across all your cells must exceed 51.416.

**Influence Math:**
- A lone stone contributes 1.714 to its own cell
- 30 isolated stones: 30 * 1.714 = 51.42 (just barely wins!)
- But clustered stones boost each other. A stone with 2 friendly neighbors at dist-1 gets: 1.714 + 2*0.808 = 3.33 per cell
- Clustering is mathematically rewarded — a compact group of 20 stones could easily exceed 51.416

**Degenerate Flags:**
- The threshold of 51.416 is *exactly* achievable with 30 isolated stones (30 * 1.714 = 51.42). This means the game is essentially "get 30 stones on the board" if you spread out, or fewer if you cluster.
- Since there are only 64 cells and games are short (~31 moves), most games end when one player accumulates enough stones — often just by filling up the board.

### Phase 2 — Strategic Play

**Random Game Observations (12 games):**
- P1 wins: 8, P2 wins: 4 (noticeable first-player advantage with random play)
- Game length range: 35-94 moves, average ~50
- Games end faster than game 1 — often by move 35-55
- Shorter games tend to be P1 wins (first-mover accumulates influence faster)

**Self-Play Analysis:**

*Seed 1 random game:* P1 won at move 41 with 21 stones vs P2's 20 stones. P1's stones were more clustered (z=0 and z=2 layers), boosting total influence above threshold.

*Seed 42 random game:* P1 won at move 51 with 25 stones each. Despite equal stone counts, P1's clustering gave higher total influence.

*Seed 7 random game:* P2 won at move 36 — P2 managed to capture several P1 groups in the mid-game, accumulating stones while P1 lost them.

**Key Strategic Observations:**
- **Clustering is king** — placing stones near your existing stones increases influence per-stone dramatically
- **Captures are devastating** — losing stones reduces your influence count, AND opponent gains board control
- **3D makes surrounding hard** — each cell has up to 6 neighbors, requiring much more investment to surround
- **Edge/corner cells have fewer liberties** — in 3D, a corner cell (0,0,0) has only 3 neighbors, making corner groups vulnerable
- **The game feels like a race** — whoever accumulates stones faster wins, so tempo matters more than position

### Phase 3 — Strategic Analysis

**Distinct Strategies:**
1. *Cluster building* — place stones adjacent to existing ones to maximize influence
2. *Spread and race* — scatter stones across the board to avoid being captured
3. *Capture-focused* — surround opponent groups in 3D to remove their stones

**Meaningful Counter-play:** Limited. The influence threshold creates a simple race — whoever gets enough stones clustered together wins. There's little reason to play defensively because every stone you play adds ~1.7 influence minimum.

**Short-term vs. Long-term Tension:** Weak. The optimal strategy is almost always to place near your existing stones. There's rarely a reason to invest in a long-term plan when immediate influence accumulation wins.

**Emergent Concepts:**
- *Cluster efficiency* — dense clusters amplify influence
- *3D surrounding* — requires 6 stones to fully surround a cell, creating interesting spatial puzzles
- *Layer control* — controlling a full z-layer is powerful
- *Capture prevention* — keeping liberties open in 3D

**Topology Impact:** The 3D aspect is the game's strongest feature. Navigating 4x4x4 space creates genuine spatial complexity. Understanding which cells are adjacent across layers adds a unique cognitive challenge. However, the 4x4x4 size limits strategic depth — the board is small enough that there's not much room for deep plans.

**Comparison to Known Games:** A 3D Go variant with influence-based scoring. Similar to 3D Tic-Tac-Toe in spatial challenge but with Go's capture mechanics. The influence scoring is reminiscent of area scoring in Go but with a mathematical boost for clustering.

### Phase 4 — Verdict

```
Game ID: 384b3e1af682
Rules Summary: 3D Go with influence propagation; win when your stones' total influence exceeds 51.4.
Topology: 3D 4x4x4 grid, von Neumann (face-adjacent) adjacency

SCORES (1-10):
  Strategic Depth: 5 — Clustering strategy dominates; capture threats add some depth but the game is fundamentally a race
  Emergent Complexity: 5 — 3D spatial reasoning is interesting; influence clustering creates optimization puzzles; but few truly surprising emergent behaviors
  Balance: 6 — Training shows 50/50 balance; random play shows P1 advantage (8 wins vs 4); first-mover advantage exists
  Novelty: 6 — 3D topology + influence threshold is a genuinely novel combination not seen in traditional games
  Replayability: 5 — 3D board creates variety in positions but the "cluster and accumulate" strategy limits strategic diversity
  Overall "Would I play this again?": 5

KILLER FLAWS:
- The influence threshold (51.416) is trivially reachable with ~30 stones — the game often degenerates into "fill the board first"
- First-player advantage is noticeable — P1 always has one more stone placed, which translates directly to influence advantage
- 4x4x4 is too small for deep strategy — with only 64 cells and ~50 moves, there's limited room for long-term planning
- Clustering is almost always correct, reducing strategic diversity

BEST QUALITY: The 3D spatial reasoning is genuinely challenging and fun. Understanding adjacency across layers, planning surrounding operations in 3D, and optimizing influence clusters across three dimensions creates a unique cognitive experience that 2D games can't replicate.

IMPROVEMENT IDEAS: Increase the influence threshold to ~80+ (requiring much denser clustering or ~47 stones) to force more conflict over territory. Alternatively, make influence decay between friendly stones — stones too close to each other contribute less — to encourage spreading and create tension between clustering (for survival) and spreading (for influence efficiency).
```

---

## Comparative Summary

| Dimension | 4772ff161000 (2D Territory) | 384b3e1af682 (3D Threshold) |
|-----------|----------------------------|----------------------------|
| Strategic Depth | 7 | 5 |
| Emergent Complexity | 7 | 5 |
| Balance | 7 | 6 |
| Novelty | 4 | 6 |
| Replayability | 7 | 5 |
| Overall | **7** | **5** |

**Ranking:** `4772ff161000` > `384b3e1af682`

**Analysis:** The 2D territory game is the stronger game overall. While it lacks novelty (being essentially small-board Go), it inherits Go's deep strategic properties — liberty management, life/death, influence, and initiative. The 59.4% territory threshold adds genuine endgame drama with large swing captures. The 3D threshold game has more novel design but suffers from a dominant "cluster and accumulate" strategy that reduces strategic diversity. Its saving grace is the genuine spatial complexity of 3D play.

The Run 9 champion (`4772ff161000`) earned its position — it's the most strategically complete game of the two, with the most replayability and deepest decision-making. The highest-GE game (`384b3e1af682`) has interesting mechanics but its win condition is too easily achievable, making the game feel more like a race than a battle.
