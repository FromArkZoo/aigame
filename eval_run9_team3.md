# Run 9 Evaluation Report — Team 3

## Games Evaluated
1. **404ace5c1863** — 3D 4x4x4, surround capture (thresh=1), connection win, ELO 2439.2, Go Essence 0.200
2. **dcd36397091e** — 2D 8x8, surround capture (thresh=2), majority win, ELO 2407.1, Go Essence 0.202

---

## Game 1: 404ace5c1863 — "3D Forced-Proximity Connection"

### Phase 1 — Rule Comprehension

**Board**: 3D grid of 4x4x4 = 64 cells. Von Neumann adjacency (face-adjacent only, no diagonals). Each cell has up to 6 neighbors (up/down/left/right/forward/back).

**Placement**: Players alternate placing one stone per turn on empty cells. After each player's first move (which can be placed anywhere), all subsequent placements must be **adjacent to an enemy stone**. This creates forced engagement — you can never retreat or build independently.

**Capture**: Go-style surround capture (threshold 1). A group of connected same-color stones with zero liberties (empty adjacent cells) is removed from the board.

**Win condition**: Connection game. Player 1 wins by connecting opposite faces along dimension 2 (z-axis: z=0 face to z=3 face). Player 2 wins by connecting opposite faces along dimension 0 (x-axis: x=0 face to x=3 face). This is a Hex-like asymmetric connection objective in 3D. Maximum 100 turns; if no connection is made, the player with a connection advantage wins.

**Key mechanic**: The adjacent_to_enemy constraint is the defining feature. After the opening moves, every stone MUST be placed next to an opponent's stone. This creates tight, interleaved play where both colors are woven together — very different from traditional connection games where you build your own chain.

### Phase 2 — Strategic Play

**Self-play Game 1**: P1 opens at (1,1,0) on z=0 face, P2 opens at (1,1,2). P1 immediately jumps to (1,1,3) — now having stones on z=0 and z=3 but disconnected. P2 responds by taking (1,1,1), blocking P1's direct column. The game becomes a complex routing problem as P1 tries to find a winding path from z=0 to z=3 while P2 both blocks and pursues its own x-axis connection. After 55 moves, P1 wins with a winding path through z-layers.

**Self-play Game 2**: P1 opens center (1,1,1), P2 opens at (0,1,0) on x=0 face. The forced-proximity constraint means both players build dense clusters. P2 attempts an x-axis connection but P1's forced adjacency to P2's stones naturally creates blocking positions. The interleaving of colors makes connection extremely difficult. Game reaches 100 moves without clean connection.

**Self-play Game 3**: P1 opens at edge, P2 takes opposite corner. The 3D topology allows routing around 2D blockades — this is where the game becomes interesting. A wall in one z-layer can be bypassed by going to an adjacent layer. This gives the 3D version genuine depth over 2D Hex.

**Random game observations** (5 games watched): Games ranged from 54 to 100 moves. P1 won 3, P2 won 2. Captures occurred but were relatively infrequent — the spread-out nature of forced-enemy-adjacency play means groups rarely get fully surrounded. In late game, one player often dominates materially (30+ stones vs 10-15) due to cascading captures creating vulnerability chains.

**Critical observation**: Training data shows average game length of only **3.5 moves** across all 8 training runs. This is extremely suspicious — a minimum connection path requires 4 stones (one per z-layer). Trained agents learned a near-instant winning strategy, likely exploiting the opponent's forced proximity to rapidly complete connections. The trained vs random win rate (86-94%) and perfect 50/50 balance between P1/P2 suggest this is a legitimate tactical shortcut rather than a bug, but it means the game's depth for skilled play may be very shallow.

### Phase 3 — Strategic Analysis

**Viable strategies**: In casual play, two main approaches emerge:
1. **Direct punch-through**: Open on your target face, extend across layers as fast as possible
2. **Blocking + opportunistic connecting**: Focus on disrupting the opponent's path while building your own gradually

The adjacent_to_enemy constraint means both strategies are interleaved — you can't purely block or purely extend.

**Counterplay**: Yes, meaningful counterplay exists. Since you must play next to the opponent, every move is both offensive and defensive. Placing a stone to extend your own connection simultaneously creates a mandatory adjacency point for your opponent.

**Tension**: There's genuine short-term vs long-term tension. Placing a stone to immediately threaten connection can leave your other groups vulnerable to capture. The 3D routing creates interesting read-ahead.

**Emergent concepts**:
- **Threading**: Finding a path through enemy stones in 3D
- **Layer bridging**: Using adjacency across z-layers to bypass blockades
- **Capture threats**: Stones forced into proximity can form capture-ready configurations
- **Tempo**: Being forced to play near the enemy creates a "tempo ladder" where initiative alternates

**Topology impact**: The 3D topology is genuinely important. A 4x4 2D Hex game would be trivially small. The third dimension provides exactly enough room for meaningful routing decisions. A minimum path is 4 stones but actual games require 8-15 stones due to detours around blocks.

**Comparison**: This is most similar to 3D Hex, but the forced-proximity placement is a genuinely novel mechanic. In standard Hex, you can place anywhere; here, engagement is mandatory. The result is more combative and tactical, less territorial.

**Degenerate concern**: The 3.5 avg game length in training is a serious red flag. It suggests that for sufficiently strong players, the game resolves almost immediately — likely one player opens on their target face, and through the forced-proximity mechanism, can establish a winning connection in 2 moves. This would make the game a trivial first-mover puzzle at high skill levels, despite appearing complex to casual players.

### Phase 4 — Verdict

```
Game ID: 404ace5c1863
Rules Summary: 3D 4x4x4 connection game where you must place adjacent to enemy stones, with Go-style captures.
Topology: 3D 4x4x4 cube, von Neumann adjacency (6-connected)

SCORES (1-10):
  Strategic Depth: 5 — Interesting for casual play but the 3.5 avg game length suggests shallow depth at high skill. The forced-proximity creates tactical richness that may be illusory.
  Emergent Complexity: 7 — 3D routing, capture threats, and forced engagement create genuine emergent patterns. Threading through enemy stones in 3D is conceptually interesting.
  Balance: 8 — Perfect 50/50 P1/P2 balance in training. Asymmetric connection axes (z vs x) work well.
  Novelty: 8 — The forced-proximity placement in a 3D connection game is genuinely novel. Not seen in any established game.
  Replayability: 4 — If the 3.5-move solution is real, high-skill games would be repetitive. Casual play offers more variety.
  Overall "Would I play this again?": 5

KILLER FLAWS: The 3.5 avg game length in training strongly suggests a degenerate shortcut exists where skilled players can win almost immediately. This undermines the apparent strategic depth. The game may be "solved" at a shallow search depth.

BEST QUALITY: The forced-proximity placement mechanic is brilliant and genuinely novel. Being forced to engage with the enemy on every move creates a unique feel — combative, interleaved play unlike any standard connection game. The 3D routing adds meaningful spatial reasoning.

IMPROVEMENT IDEAS: Increase the board to 5x5x5 or 6x6x6 to make instant connections much harder. The forced-proximity mechanic is strong; it just needs more space to breathe. Alternatively, require connections along the longest dimension to increase minimum path length.
```

---

## Game 2: dcd36397091e — "Territorial Blob Race"

### Phase 1 — Rule Comprehension

**Board**: 2D grid of 8x8 = 64 cells. Von Neumann adjacency (4-connected: up/down/left/right, no diagonals).

**Placement**: Players alternate placing one stone per turn on empty cells. After each player's first move (placed anywhere), all subsequent placements must be **adjacent to one of your own stones**. This creates organic blob growth — each player expands outward from their initial stone.

**Capture**: Go-style surround capture with threshold 2. This means a connected group is captured and removed if it has **fewer than 2 liberties** (i.e., 0 or 1 liberty). This is stricter than standard Go (where groups need 0 liberties to die). Groups must maintain at least 2 empty adjacent cells to survive.

**Win condition**: Majority — the player with the most stones on the board at game end wins. Maximum 159 turns (enough to nearly fill the 64-cell board multiple times with captures and replacements).

**Key mechanic**: The adjacent_to_own constraint creates two opposing blobs that grow organically from their starting positions and eventually collide at a frontier. The capture threshold of 2 makes frontier stones more vulnerable than in Go, since a stone with only 1 liberty dies.

### Phase 2 — Strategic Play

**Self-play Game 1**: P1 opens at (3,3), P2 at (4,4). Both grow outward. P1 extends toward upper-left, P2 toward lower-right. The blobs meet along a diagonal frontier. I tried pushing aggressively into P2's territory but the adjacent_to_own constraint limits how quickly you can extend thin fingers. The frontline becomes a solid wall. Final: 33-31, P1 wins by 2 pieces due to slightly better initial positioning.

**Self-play Game 2**: P1 opens center (3,3), P2 opens corner (7,7). P2 has a disadvantage — growing from a corner limits expansion directions. P1's central start captures more territory. The game becomes a straightforward territorial race with the border settling around column 5. P1 wins handily with more cells on its side.

**Self-play Game 3**: Both players open near center (3,3) and (4,4). Growth is symmetric. The frontier forms a clean diagonal line. I tried a capture strategy — extending a thin tendril into enemy territory hoping to cut off a section. The threshold-2 capture rule killed my thin extension (1 liberty = death). This punishes aggressive play. Result: near-draw, 32-32.

**Random game observations** (5 games, seeds 1,2,10,42): Extremely consistent pattern across all games:
- Both players start from different areas
- Blobs grow organically
- They meet at a clean frontier (usually a vertical or diagonal line)
- Board fills nearly completely
- Result depends primarily on first-move positions
- 2 draws, 3 wins (varying sides)
- Games last 66-67 moves

The game is remarkably predictable in random play. Every random game looked essentially the same — two blobs growing, meeting, filling the board, counting pieces.

### Phase 3 — Strategic Analysis

**Viable strategies**: Only one approach dominates — grow your blob as fast as possible to claim more territory. There's no meaningful alternative. Opening near the center gives maximum expansion room.

**Counterplay**: Minimal. You can't invade the opponent's territory (adjacent_to_own prevents jumping) and you can't aggressively extend without dying to threshold-2 captures. The only "counterplay" is choosing which direction to expand, which is barely a decision.

**Short-term vs long-term tension**: Almost none. Every move is equivalent — extend your blob in the best available direction. There's no sacrifice play, no tempo, no trading material for position.

**Emergent concepts**:
- **Territory**: Yes, in the simplest possible form — your blob IS your territory
- **Frontier optimization**: Choosing which edge to extend is the only real decision
- **First-move advantage**: Opening position is by far the most important decision

**Topology impact**: The 2D 8x8 grid is adequate. The von Neumann adjacency (no diagonals) creates cleaner frontiers than Moore adjacency would. The board size is appropriate for the mechanics.

**Capture threshold 2 impact**: In practice, captures almost never happen. Both blobs maintain healthy liberties along their frontiers because they grow as solid masses. The threshold-2 rule only matters if someone extends a thin finger (which immediately dies), effectively punishing the only interesting tactical option. The capture mechanic is vestigial.

**Comparison**: This is essentially a simplified territory-claiming game, somewhere between Othello (without flipping) and a "flood fill" race. It has far less depth than Go, Othello, or even basic area-control games because there are almost no meaningful decisions.

**Training signal**: The weak 52-68% vs random win rate confirms that strategy barely matters. Random play is nearly as effective as trained play — the game's outcome is mostly determined by initial placement geometry.

### Phase 4 — Verdict

```
Game ID: dcd36397091e
Rules Summary: 2D 8x8 majority game where you grow from your starting stone, with surround capture requiring 2+ liberties.
Topology: 2D 8x8 grid, von Neumann adjacency (4-connected)

SCORES (1-10):
  Strategic Depth: 2 — Almost no meaningful decisions beyond the opening move. Grow your blob; whoever started closer to center wins.
  Emergent Complexity: 2 — No emergent concepts beyond trivial territory. Capture mechanic is vestigial. No tactics, no combinations, no surprises.
  Balance: 7 — Reasonably balanced (50/50 P1/P2 in training). Draws are common. But balance comes from symmetry, not from deep equilibrium.
  Novelty: 3 — Adjacent-to-own blob growth has some novelty but the overall game is just a territory race with almost no interaction between players.
  Replayability: 2 — Every game plays out the same way: grow blob, meet frontier, count pieces. Outcome determined by opening placement. No reason to play more than twice.
  Overall "Would I play this again?": 2

KILLER FLAWS:
1. **No meaningful interaction**: The adjacent_to_own constraint means players grow independently until frontiers meet. There's no combat, no invasion, no disruption — just parallel solitaire.
2. **Vestigial capture**: Threshold-2 surround capture almost never triggers because solid blobs have plenty of liberties. The one situation it does trigger (thin extensions) punishes the only interesting tactical option.
3. **Deterministic feel**: Games are essentially decided by opening placement. 52-68% trained-vs-random confirms strategy barely matters.

BEST QUALITY: The adjacent_to_own constraint creates aesthetically pleasing organic growth patterns. Watching two blobs expand and meet is visually satisfying, even if strategically empty.

IMPROVEMENT IDEAS: Add a mechanic that forces interaction — perhaps allow "jumping" to place a stone 2 spaces away from your blob (creating a separate group that must survive on its own), or change the win condition to connection (which would create directional goals and blocking incentives). The adjacent_to_own growth model could work well in a connection game where you need to reach the opposite side.
```

---

## Comparative Summary

| Dimension | 404ace5c1863 (3D Connection) | dcd36397091e (2D Majority) |
|-----------|------------------------------|---------------------------|
| Strategic Depth | 5 | 2 |
| Emergent Complexity | 7 | 2 |
| Balance | 8 | 7 |
| Novelty | 8 | 3 |
| Replayability | 4 | 2 |
| Overall | **5** | **2** |

**404ace5c1863** is the stronger game by a significant margin. Its forced-proximity placement mechanic is genuinely novel and creates rich tactical interplay in 3D. The main concern is the ultra-short trained game length suggesting a shallow solution exists. If the board were larger, this could be an excellent game.

**dcd36397091e** is functional but strategically empty. Both players grow blobs independently with minimal interaction. The capture mechanic is vestigial and the majority win condition creates no directional goals. It's a territory race with nearly no decisions.
