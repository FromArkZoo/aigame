# Run 9 Evaluation Report — Team 5

**Evaluator:** Agent Team 5
**Games Evaluated:** `6009cf66eb3a`, `fc4e82bd061b`

---

## Game 1: `6009cf66eb3a` — 3D Majority Go

### Phase 1 — Rule Comprehension

**Board:** 3D grid, 4×4×4 (64 cells), von Neumann adjacency (face-adjacent only, 6 neighbors max per interior cell).

**Placement:** Players alternate placing one stone per turn on **any** cell (empty or occupied), but must place **adjacent to their own stones** (except the first move, which is anywhere). Placing on an occupied cell wastes the move.

**Capture:** Go-style surround capture with threshold 1. Groups with zero liberties (no adjacent empty cells) are removed from the board.

**Win Condition:** Majority — whoever has the most stones on the board after 100 turns (or when no moves remain) wins.

**Key Observations:**
- The `target: any` placement rule means players CAN place on occupied cells, wasting their turn. Random agents frequently do this, producing many no-ops.
- The `adjacent_to_own` constraint creates organic blob growth from the starting position. Players must grow outward from their first stone.
- The 3D topology creates complex liberty counting — interior cells have 6 neighbors, making surround capture hard to execute.

### Phase 2 — Strategic Play

**Game 1 (seed 1, random):** P2 wins 11-9 after 29 moves. Both players grew organically in different parts of the board. P2's corner-based growth (column x=3 across z-layers) outpaced P1's interior growth. Many wasted moves placing on occupied cells.

**Game 2 (seed 2, random):** P1 wins 8-6 after 22 moves. Again, organic blob growth with wasted moves. Short game due to early majority achieved through efficient expansion.

**Game 3 (seed 3, random):** P1 wins 18-17 after 50 moves. Longer, more contested game with both players' blobs expanding across multiple z-layers.

**Strategic Game (center vs corner):** P1 started centrally at (1,1,1) and expanded a solid 3D block through z=1 and z=2. P2 started at corner (0,0,0) and grew along the x=0 column. After 22 moves, P2 led 11-10 by exploiting the wider surface area of corner/edge growth. The central strategy has more liberties to defend but is surrounded on all sides; the corner strategy has fewer neighbors to worry about and can expand efficiently along edges.

**Capture testing:** Surround capture in 3D is extremely difficult to execute. Interior cells have 6 neighbors, and groups share liberties. In no game (random or strategic) did I observe a meaningful capture that swung the game. The threat of capture is minimal when groups are large, since cutting off all 6 directions simultaneously requires massive investment.

### Phase 3 — Strategic Analysis

**Viable strategies:** Two main approaches — (1) central expansion for maximum adjacency options, (2) corner/edge expansion for efficient growth with fewer vulnerable liberties. Neither clearly dominates; it depends on how players interact.

**Counter-play:** Limited. The `adjacent_to_own` constraint means you can only grow your blob, not place disruptive stones in the opponent's territory. Two separate blobs rarely interact until late game when they collide. The game often reduces to a territory-claiming race.

**Short vs long term tension:** Minimal. There's little incentive to play defensively vs aggressively — just expand as efficiently as possible. No sacrifice or delayed gratification.

**Emergent concepts:** Blob growth, surface area management, and liberty counting exist but rarely matter. Capture is almost never achievable in 3D. No territory concepts beyond "grow my blob bigger."

**Topology impact:** The 3D topology makes captures nearly impossible (too many liberties) and makes the board hard to visualize/reason about. It arguably hurts the game compared to 2D.

**Comparison to known games:** A greatly simplified Go variant where capture is vestigial and the game reduces to a blob-growing race. Far less strategic depth than Go, Hex, or even Othello.

### Phase 4 — Verdict

```
Game ID: 6009cf66eb3a
Rules Summary: Place stones adjacent to your own group on a 3D 4×4×4 grid with Go-style capture; most stones at end wins.
Topology: 3D 4×4×4 (64 cells), von Neumann adjacency

SCORES (1-10):
  Strategic Depth: 3 — Adjacent-to-own constraint limits all play to blob expansion; capture is nearly impossible in 3D
  Emergent Complexity: 3 — Blob growth patterns emerge but no deeper concepts like sacrifice, ko, or territory
  Balance: 6 — Training shows 50/50 win rate; no obvious P1/P2 advantage
  Novelty: 4 — 3D Go-like game with majority scoring is moderately novel but not groundbreaking
  Replayability: 3 — Games feel similar; grow blob, count stones, limited interaction between players
  Overall "Would I play this again?": 3

KILLER FLAWS:
- Surround capture is nearly impossible in 3D (6 neighbors per cell), making it vestigial
- `target: any` allows placing on occupied cells (wasted moves), reducing effective decision space
- `adjacent_to_own` constraint means players can't interact until blobs collide, creating two parallel solitaire games
- No interesting mid-game decisions — just expand as efficiently as possible

BEST QUALITY:
- The adjacent_to_own constraint creates a natural, organic growth pattern that is visually interesting
- Well-balanced (50/50 win rates)
- Games end in reasonable time (22-50 moves)

IMPROVEMENT IDEAS:
- Switch to 2D (8×8) to make surround capture viable and increase player interaction
- Change placement from `adjacent_to_own` to `anywhere` so players can place disruptive stones
- Or add a connection win condition instead of majority to create directional tension
```

---

## Game 2: `fc4e82bd061b` — 2D Connection Go (Go × Hex)

### Phase 1 — Rule Comprehension

**Board:** 2D 8×8 grid (64 cells), von Neumann adjacency (4 neighbors max).

**Placement:** Players alternate placing one stone per turn on **empty** cells, anywhere on the board (no adjacency constraint). First move anywhere.

**Capture:** Go-style surround capture with threshold 1. Groups with zero liberties are removed.

**Win Condition:** Connection — P1 wins by connecting opposite faces of dimension 0 (left edge x=0 to right edge x=7). P2 wins by connecting opposite faces of dimension 1 (top edge y=0 to bottom edge y=7). Max 100 turns.

**Key Observations:**
- This is essentially **Go capture rules + Hex-style connection win conditions** on a standard 8×8 grid with orthogonal adjacency.
- P1 connects horizontally (left-to-right), P2 connects vertically (top-to-bottom). Both axes have the same length (8), creating symmetric connection distances.
- Unlike Hex, adjacency is only orthogonal (4-connected, not 6-connected), and captures can break opponent chains.
- The `target: empty` rule (unlike game 1) means no wasted moves on occupied cells.

### Phase 2 — Strategic Play

**Random games (seeds 1-4):** Games last 65-78 moves and fill most of the board. P2 won 3 of 4 random games, likely due to random variance. Massive captures occur late-game when surrounded groups lose all liberties, dramatically swinging piece counts (e.g., P1 went from 29 pieces to 9 in one capture event in seed 1).

**Strategic Game 1 — Racing:** P1 built horizontal chain across row 0, P2 built vertical chain down column 4. P1 completed 7 of 8 cells but P2's stone at (4,0) blocked the chain. The critical cell was the intersection point where both chains cross. First to claim it wins.

**Strategic Game 2 — Wall blocking:** P2 built a vertical wall at x=3 from y=0 to y=7. P1 had to navigate around it, going up through rows 2, 1, 0 before trying to cross. P2 completed their connection before P1 could route around. Blocking walls are very effective.

**Strategic Game 3 — The decisive intersection:** Both players built their chains leaving a gap at the intersection (3,3). P1, having first-move advantage, filled (3,3) on move 15 and simultaneously completed their connection while permanently blocking P2. This demonstrates the core strategic tension: the intersection cell is a dual-purpose move worth fighting over.

**Capture dynamics:** Successfully tested surround capture — P1 surrounded P2's stone at (3,3) by placing at (2,3), (4,3), (3,2), (3,4). Unlike the 3D game, captures are achievable on 2D since cells have only 4 neighbors. However, capturing large connected groups is still very difficult due to shared liberties. Captures are most impactful for removing isolated blocking stones.

### Phase 3 — Strategic Analysis

**Viable strategies:**
1. **Racing:** Build your connection as fast as possible, hoping the opponent doesn't block
2. **Blocking:** Build walls perpendicular to the opponent's connection axis
3. **Intersection control:** Fight for cells where both players' optimal paths cross
4. **Capture-assisted connection:** Surround and remove opponent blocking stones to restore broken chains

All four strategies are viable and create rich interactions.

**Counter-play:** Excellent. Every offensive move (extending your chain) can be met with a defensive move (blocking or wall-building). Captures can break chains, creating dynamic back-and-forth. Placing a stone at the intersection of both players' paths serves dual offensive/defensive purposes.

**Short vs long term tension:** Present. Building a thick, hard-to-capture chain (Go influence) vs racing to connect quickly (Hex tempo). Investing in capture setup now vs extending your chain. Deciding between multiple connection paths.

**Emergent concepts:**
- **Connection paths** (Hex-like): Multiple potential routes to connect, creating reading depth
- **Walls and barriers** (Hex blocking): Vertical/horizontal walls that force detours
- **Liberties** (Go-like): Groups need breathing room; isolated stones are vulnerable
- **Intersection control**: Critical cells where both players' paths cross
- **Capture threats**: Threatening to capture a blocking stone to restore a chain
- **Thickness vs speed**: Building a robust chain vs racing to connect

**Topology impact:** The 8×8 2D board with orthogonal adjacency works well. Enough space for multiple connection paths, routing around blocks, and capture setups. The orthogonal-only adjacency (vs Hex's 6-connectivity) makes blocking slightly easier and connection slightly harder, emphasizing the importance of multiple paths.

**Comparison to known games:** A genuine **Go × Hex hybrid**. Has Go's capture mechanics and liberty concepts combined with Hex's connection win condition and blocking dynamics. More interesting than either pure Go on 8×8 or pure Hex on 8×8 because capture adds a way to break through walls. Not as deep as full-sized Go or Hex, but the combination creates something distinctly novel.

**Training notes:** Two of three training runs learned well (0.72, 0.74 vs random), but one collapsed completely (0.04 vs random), suggesting the game has sufficient complexity to challenge RL training. The non-collapsed runs achieved reasonable game lengths (67-78 moves), indicating games don't end trivially fast.

### Phase 4 — Verdict

```
Game ID: fc4e82bd061b
Rules Summary: Place stones on an 8×8 grid with Go-style surround capture; P1 wins by connecting left-to-right, P2 wins by connecting top-to-bottom.
Topology: 2D 8×8 (64 cells), von Neumann adjacency (orthogonal only)

SCORES (1-10):
  Strategic Depth: 6 — Multiple viable strategies (racing, blocking, capture, intersection control) with genuine reading depth
  Emergent Complexity: 7 — Connection paths, walls, liberty management, capture threats, and intersection control all emerge naturally
  Balance: 6 — Both axes are symmetric (length 8). Training shows 50/50 win rate. P1 has first-mover advantage at intersection points (Hex-like), but P2 can compensate with good blocking
  Novelty: 7 — Genuine Go × Hex hybrid that isn't just "Go with different win condition" — the capture mechanics meaningfully interact with connection strategy
  Replayability: 6 — Multiple connection paths and blocking strategies create varied games; captures add dynamic swings
  Overall "Would I play this again?": 6

KILLER FLAWS:
- One training run completely collapsed (0.04 vs random), suggesting potential degeneracy in some strategy profiles
- Orthogonal-only adjacency makes connections somewhat fragile — a single blocking stone can cut a chain, and rerouting requires many moves
- On an 8×8 board, complete games can be long (65-78 moves) with endgame board fill becoming tedious
- First-mover advantage at intersection points may give P1 a structural edge (classic Hex problem without a swap rule)

BEST QUALITY:
- The combination of Go capture with Hex connection creates genuinely novel strategic tension
- Captures can break opponent chains, adding a dynamic that pure Hex lacks
- Multiple connection paths with blocking creates rich positional play
- The intersection control mechanic (a cell that serves both offense and defense) creates critical decision points

IMPROVEMENT IDEAS:
- Add a swap rule (P2 can choose to take P1's first move) to address first-mover advantage
- Consider Moore adjacency (8-connected) instead of von Neumann (4-connected) to make connections more robust and reduce fragility
- Alternatively, reduce board to 6×6 to tighten games and make captures more impactful
```

---

## Summary Comparison

| Metric | `6009cf66eb3a` (3D Majority) | `fc4e82bd061b` (2D Connection) |
|--------|-----|-----|
| Strategic Depth | 3 | 6 |
| Emergent Complexity | 3 | 7 |
| Balance | 6 | 6 |
| Novelty | 4 | 7 |
| Replayability | 3 | 6 |
| Overall | **3** | **6** |

**Recommendation:** `fc4e82bd061b` is clearly the stronger game. The Go × Hex hybrid creates meaningful strategic interactions that neither mechanic produces alone. `6009cf66eb3a` suffers from the 3D topology making captures impossible and the `adjacent_to_own` constraint creating parallel solitaire rather than interactive gameplay.
