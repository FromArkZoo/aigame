# Run 9 Evaluation — Team 2

## Game 1: `1ac8f19581ca` — "3D Hex-Go"

### Phase 1 — Rule Comprehension

**Board**: 3D grid, 4×4×4 (64 cells), von Neumann adjacency (6 face-neighbors per interior cell).

**Placement**: Players alternate placing one stone per turn on any empty cell. Pass is allowed (action 64).

**Capture**: Go-style surround capture. A group of connected same-color stones with 0 liberties (no adjacent empty cells) is removed from the board. Threshold=1 means standard Go capture rules. Self-capture appears to be allowed (stones can be placed in positions with 0 liberties and remain).

**Win Condition**: Connection game — P1 wins by connecting z=0 face to z=3 face (4 layers); P2 wins by connecting x=0 face to x=3 face (4 columns). Both players must cross exactly 4 cells, making the win condition geometrically symmetric despite targeting different dimensions. Max 114 turns.

**Propagation**: None (vestigial parameter, no effect).

**Summary**: This is essentially **3D Hex with Go capture** on a 4×4×4 cube. Each player tries to build a connected path across the cube along their assigned axis while using Go-style captures to disrupt the opponent's connections.

**Degenerate Rules**: The self-capture mechanic (stones surviving in 0-liberty positions) is unusual and somewhat counterintuitive. In practice, it mainly wastes tempo for the placing player, weakening the impact of captures since a captured stone can be immediately replayed.

### Phase 2 — Strategic Play

**Self-Play Game 1** (P1 builds direct z-column):
P1 placed stones at (1,1,z) for z=0,1,2,3 — a direct vertical column. P2 tried building horizontally but was too slow. **P1 wins in 7 moves** (4 stones for P1). The minimum-length vertical path wins trivially if uncontested.

**Self-Play Game 2** (P2 blocks z=3 layer):
P2 mirrored P1's placement by blocking z=3 at the same x,y coordinates. P1 adapted by building a broader base at z=0 and jogging through x=2→x=3 at z=2 and z=3, flanking around P2's blocks. **P1 wins in 15 moves.** Even with dedicated blocking, P1 found a path by using lateral movement within layers.

**Self-Play Game 3** (P2 directly blocks every column):
P2 placed blocking stones directly above each of P1's z=0 placements. P1 responded by building through the x=3 edge: z=0 base → (3,1,1) → (3,1,2) → (3,1,3). **P1 wins in 17 moves.** P2 cannot block all 16 cells of z=3 simultaneously; P1 always finds a gap.

**Random Games** (15 games, seeds 1-10, 42, 100-400):
- P1 wins: 9/15 (60%), P2 wins: 6/15 (40%)
- Average game length: ~37 moves (range 28-54)
- Slight P1 advantage from first-move, but P2 wins are frequent
- Training data shows perfect 50/50 balance with trained agents (all 3 runs)

### Phase 3 — Strategic Analysis

**Viable Strategies**: The 3D connection goal creates rich path-finding. Multiple strategies emerge:
1. **Direct column**: Build a straight z-column (fastest but easiest to block)
2. **Broad base**: Secure multiple z=0 cells, then extend upward through whichever path is open
3. **Lateral jog**: Build through one x-column for 2-3 layers, then hop to an adjacent column to bypass blocks
4. **Edge exploitation**: Use cube edges (where cells have fewer neighbors) to build hard-to-surround chains

**Counter-play**: Blocking is meaningful but requires predicting the opponent's path. The 4×4 face gives 16 possible entry points per layer, but only 4 layers to cross. This creates a favorable attack-defense ratio for the connector: the blocker can't cover all paths. This is analogous to Hex's proof that the first player always has a winning strategy.

**Short-term vs Long-term Tension**: Players face choices between extending their own path (offensive) vs blocking opponent paths (defensive). Building a broad z=0 base costs tempo but creates options. There's genuine tension about when to attack vs defend.

**Emergent Concepts**:
- **Path flexibility**: The 3D lattice provides many redundant paths, creating strategic depth around which path to develop
- **Captures as tempo**: Surrounding and capturing an enemy group breaks their connection while gaining tempo. But the self-capture mechanic weakens this (opponent can replay)
- **Layer control**: Securing multiple footholds in middle layers (z=1, z=2) is critical infrastructure
- **Fork threats**: Threatening connection through two different paths simultaneously forces the opponent to choose which to block

**Topology**: The 3D structure is the game's most distinctive feature. While 2D Hex has only one shortest path length (N steps across an N-wide board), 3D Hex has many more routing options. The cube's 6-connectivity creates a richer adjacency graph than a hex grid. However, the small 4×4×4 size limits the depth: paths are short (minimum 4 steps) and the game often ends before the board is half-full.

**Comparison to Known Games**: Strong Hex influence (connection goal on symmetric board). The Go-style capture adds a tactical layer absent from pure Hex. The 3D topology is reminiscent of 3D Connect Four but with much more strategic freedom (any cell placement, not gravity-constrained). Less deep than Go due to small board and simple win condition.

### Phase 4 — Verdict

```
Game ID: 1ac8f19581ca
Rules Summary: 3D connection game with Go-style captures on a 4×4×4 cube; each player connects opposite faces along different axes.
Topology: 3D 4×4×4 grid, von Neumann adjacency (6 neighbors per interior cell)

SCORES (1-10):
  Strategic Depth: 5 — Multiple viable path strategies and blocking tactics, but 4-layer crossing distance limits depth; minimum wins possible in 4 moves
  Emergent Complexity: 6 — 3D path-finding, fork threats, and capture-for-tempo create meaningful emergent play
  Balance: 7 — Training shows perfect 50/50; asymmetric axes create different spatial reasoning for each player
  Novelty: 7 — 3D Hex-with-Go-capture is genuinely novel; the dimensional asymmetry (P1 crosses z, P2 crosses x) is clever
  Replayability: 5 — The 4×4×4 board is small enough that strong players would exhaust strategic space relatively quickly
  Overall "Would I play this again?": 5

KILLER FLAWS:
- Board is too small: 4 layers means minimum connection path is only 4 stones. Games can end very quickly with inexperienced blocking.
- Self-capture allowed: stones placed in 0-liberty positions survive, weakening the capture mechanic. Captured stones can be immediately replayed.
- Captures rarely matter: most games in testing ended via connection before captures became strategically decisive. The Go capture feels underutilized.

BEST QUALITY: The 3D topology creates genuinely novel spatial reasoning challenges. Visualizing connection paths through a cube and blocking them requires thinking in three dimensions — something few board games demand. The asymmetric axis assignment (P1 crosses z, P2 crosses x) means the two players face subtly different spatial problems.

IMPROVEMENT IDEAS: Increase board to 6×6×6 or 5×5×5 to create longer minimum paths and more strategic depth. The current 4-step minimum is too short for rich gameplay. Alternatively, add a mandatory "adjacent to existing stone" placement constraint to slow connection and force territorial development.
```

---

## Game 2: `bcd45c85f87d` — "Hex-Go"

### Phase 1 — Rule Comprehension

**Board**: 2D grid, 8×8 (64 cells), von Neumann adjacency (4 orthogonal neighbors per interior cell).

**Placement**: Players alternate placing one stone per turn on any empty cell. Pass is allowed.

**Capture**: Go-style surround capture. Groups with 0 liberties are removed. Threshold=1 (standard). Self-capture appears to be allowed.

**Win Condition**: Connection game — P1 wins by connecting x=0 to x=7 (left edge to right edge); P2 wins by connecting y=0 to y=7 (top edge to bottom edge). Both players must cross 8 cells. Max 100 turns.

**Propagation**: None.

**Summary**: This is **Hex played on a square grid with Go capture rules**. Two players race to connect opposite edges of an 8×8 board while using Go-style liberties and capture to disrupt each other. Unlike actual Hex (which uses a hexagonal grid with 6-connectivity), this uses orthogonal 4-connectivity on a square grid.

**Degenerate Rules**: Same self-capture issue as Game 1. Additionally, the von Neumann (4-neighbor) adjacency on a square grid creates a potentially significant difference from Hex: in Hex, the hexagonal grid ensures that a path can always be found without being "cut" by the opponent. On a square grid with 4-connectivity, a single enemy stone at (x,y) blocks orthogonal passage, which may make blocking too powerful.

### Phase 2 — Strategic Play

**Self-Play Game 1** (naive edge-to-edge):
P1 and P2 both built straight lines along their respective edges. P2 won because P1 was building vertically (connecting rows) while P2 built vertically too — demonstrating I initially misunderstood the coordinate system. After correction: P1 needs horizontal paths, P2 needs vertical paths.

**Self-Play Game 2** (P1 horizontal + diagonal bridge):
P1 built row 0 from x=0 to x=3, then used a diagonal bridge (stepping down through column x=3 from y=0 to y=4), then completed horizontally to x=7 at row 4. **P1 wins in 23 moves.** P2 built a strong vertical wall at x=4-5 but P1 went around below it. This demonstrated the classic Hex strategy of "going around" a wall.

**Self-Play Game 3** (P1 builds complete row with P2 chasing):
P1 extended row 3 from left to right while P2 tried to build a parallel blocking wall at row 2. P2 couldn't keep up because P1 had first-move advantage. **P1 wins in 17 moves** by completing a straight horizontal line from x=0 to x=7.

**Capture Test**: Confirmed Go-style capture works. P1 surrounded a P2 stone at (3,3) with stones at (3,2), (3,4), (2,3), (4,3) — the P2 stone was removed. P2 could immediately replay at (3,3), with the stone surviving despite having 0 liberties.

**Random Games** (15 games):
- P1 wins: 4/15 (27%), P2 wins: 11/15 (73%)
- Average game length: ~79 moves (range 60-100)
- Significant P2 advantage in random play (surprising — first player usually advantaged)
- Training data shows 50/50 balance with trained agents (all 3 runs)
- Much longer games than the 3D variant

### Phase 3 — Strategic Analysis

**Viable Strategies**:
1. **Direct bridging**: Build a straight row/column across the board (fastest but easiest to block)
2. **Diagonal approach**: Build diagonally, creating a path that advances toward both edges simultaneously; requires stepping through adjacent rows/columns
3. **Fork strategy**: Build two partial connections that share a middle segment, forcing opponent to block both
4. **Capture-based connection breaking**: Surround and capture a key enemy stone to break their connection chain
5. **Wall defense**: Build a wall perpendicular to opponent's direction to force them around

**Counter-play**: The 4-connectivity of the square grid makes blocking more impactful than in Hex (6-connectivity). A single stone can block 4 directions. This means wall-building is powerful: a vertical wall completely stops horizontal passage through that column. The attacker must go *around* the wall by stepping to a different row. This creates deep tactical play around wall gaps and end-runs.

**Short-term vs Long-term Tension**: Strong tension exists between:
- Extending your own connection vs blocking opponent
- Building a direct path (fast but predictable) vs a meandering path (resilient but slow)
- Investing in captures (disrupting enemy) vs building connections (advancing your goal)
- Securing the center (flexible but not directly progressing) vs edges (progressing but cornered)

**Emergent Concepts**:
- **Influence/territory**: Clusters of same-color stones create zones of influence; a dense group is harder to cut through
- **Tempo**: Each stone placed is both offense (extending path) and defense (denying cell to opponent). The tempo battle drives the game.
- **Ladders**: As in Go, chasing a group's liberties creates "ladder" patterns along the board. These interact with the connection goal — a ladder chase toward your target edge is excellent offense
- **Bridge structure**: Building broad (2-cell-wide) paths creates resilient connections that require multiple captures to break
- **Cutting points**: Single-stone connections are vulnerable to capture; identifying and attacking cutting points is a key tactic
- **Large-scale captures**: Late-game mass captures (as seen in random game seed=1 where P2 went from 9 to 33 pieces in one sequence) can dramatically shift board control

**Topology**: The 8×8 square grid with 4-connectivity is simpler than Hex's hexagonal grid but creates different strategic properties. The lower connectivity makes blocking easier but also makes capturing more powerful (fewer liberties to fill). The 8-cell crossing distance creates games of meaningful length (avg 79 moves vs 37 for 3D). The board size is appropriate — large enough for strategic depth, small enough to finish.

**Comparison to Known Games**:
- **Hex**: Same connection goal, but square grid with Go captures adds significant tactical depth. Hex has no capture mechanic; here, captures can break connections.
- **Go**: Same capture mechanic, but the connection win condition replaces territory scoring. This simplifies endgame while maintaining Go's tactical richness around groups and liberties.
- **Run 8 champion `d4015a646ae3`**: Very similar — also 2D 8×8 surround capture with connection win. These games are siblings from the same evolutionary lineage.

### Phase 4 — Verdict

```
Game ID: bcd45c85f87d
Rules Summary: Connection game with Go-style captures on an 8×8 square grid; P1 connects left-right, P2 connects top-bottom.
Topology: 2D 8×8 grid, von Neumann adjacency (4 orthogonal neighbors)

SCORES (1-10):
  Strategic Depth: 7 — Rich interaction between connection paths, blocking walls, Go captures, and tempo management; 8-cell crossing distance allows deep strategic development
  Emergent Complexity: 7 — Territory, influence, ladders, cutting points, fork threats, and large-scale captures all emerge naturally from simple rules
  Balance: 7 — Perfect 50/50 in training; random play shows P2 bias (73%) suggesting subtle structural asymmetry, but trained agents overcome it
  Novelty: 5 — Hex + Go hybrid is interesting but not unprecedented; very similar to Run 8 champion and other top games in evolutionary lineage
  Replayability: 7 — 64 cells with two competing connection paths and tactical captures create high game-tree complexity; many distinct game trajectories
  Overall "Would I play this again?": 7

KILLER FLAWS:
- Self-capture allowed: as with Game 1, stones in 0-liberty positions survive, which is counterintuitive and weakens capture as a strategic tool
- 4-connectivity blocking may be too strong: a single stone blocks all 4 orthogonal paths, potentially making first-blocker advantages too decisive in skilled play
- Random play P2 bias (73%) suggests a subtle structural advantage that training barely compensates for; may become exploitable at expert level

BEST QUALITY: The marriage of Hex-style connection racing with Go-style capture creates a game where every stone serves dual purposes — both advancing your connection and threatening/defending captures. The 8×8 board hits a sweet spot: large enough for deep strategy, small enough for decisive games. The interaction between building resilient (2-wide) paths and the opponent's ability to capture cutting points creates genuine strategic depth.

IMPROVEMENT IDEAS: Switch to 6-connectivity (add diagonal neighbors) to create a more Hex-like connection flow and reduce the "single stone blocks everything" problem. This would make the game feel more fluid while preserving the Go capture mechanics that give it strategic identity.
```

---

## Comparative Summary

| Criterion | `1ac8f19581ca` (3D 4×4×4) | `bcd45c85f87d` (2D 8×8) |
|-----------|---------------------------|--------------------------|
| Strategic Depth | 5 | 7 |
| Emergent Complexity | 6 | 7 |
| Balance | 7 | 7 |
| Novelty | 7 | 5 |
| Replayability | 5 | 7 |
| Overall | **5** | **7** |

**The 2D game (`bcd45c85f87d`) is the stronger game overall.** It has more strategic depth, longer and more varied games, and richer emergent tactical play. The 3D game is more novel conceptually but the 4×4×4 board is too small for the connection mechanic to develop strategic richness.

Both games share the same evolutionary lineage (common ancestor `fc4e82bd061b`) and the same core mechanics (surround capture + connection win). The key difference is dimensionality: the 2D 8×8 version provides better strategic depth because the longer crossing distance (8 vs 4) gives more room for blocking, counter-play, and complex tactical sequences.
