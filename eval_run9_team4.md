# Run 9 Evaluation Report — Team 4

**Evaluator**: Team 4 Agent
**Games Evaluated**: f9eba2b4bf19, cce37f4762c4
**Database**: genesis_v2_run9.db

---

## Game 1: f9eba2b4bf19 — "3D Contact Go"

### Phase 1 — Rule Comprehension

**Board**: 3D grid, 4x4x4 (64 cells), von Neumann adjacency (face-adjacent only — up to 6 neighbors per cell, fewer at edges/corners).

**Turns**: Players alternate placing 1 stone per turn.

**Placement constraint**: Must place on an empty cell adjacent to at least one enemy stone. Exception: the very first move of the game can be placed anywhere. Pass is always available.

**Capture**: Go-style surround capture. After placing, any adjacent enemy group with 0 liberties (no empty face-adjacent cells) is removed from the board.

**Win condition**: Majority — whichever player has more stones on the board when the game ends wins. The game ends after 100 turns OR when both players pass consecutively (double-pass triggers immediate majority count).

**Degenerate flags**:
- The double-pass + majority combination creates a perverse incentive: get a slight piece advantage, then pass repeatedly
- The adjacent_to_enemy constraint means P2's legal moves on turn 2 are extremely limited (only cells adjacent to P1's first stone)

### Phase 2 — Strategic Play

**Self-play game 1 — Central opening fight**:
P1 at (1,1,1), P2 at (2,1,1), P1 at (3,1,1) creating X-O-X line. P2 extends to (0,1,1) making O-X-O-X. The fight spirals through z-layers as both players must place adjacent to each other. Contact is forced at all times — this plays like a permanent Go "fight" with no ability to tenuki (play elsewhere). After ~10 moves, both players have ~5 stones each in a dense cluster.

**Self-play game 2 — Corner exploitation**:
P1 at corner (0,0,0), P2 adjacent at (1,0,0). P1 starts surrounding: (1,1,0), then (1,0,1). P2's stone at (1,0,0) has only 4 neighbors in this border position. After P1 fills 3 of them, only 1 liberty remains at (2,0,0). A few more moves could capture P2's stone with relatively low investment.

**Random game observations** (seeds 1-3, 5):
- Games always go to 100 turns with random agents (they don't learn to pass)
- Random games show wild piece-count swings — in seed 5, P2 ended with 35 vs P1's 3 due to massive surround captures
- Dense 3D formations create cascading capture opportunities
- The 3D topology makes group liberty counting extremely complex and hard to visualize
- Surround capture is very powerful in dense positions: a single placement can capture entire groups

**Critical training data insight**: Average game length of 3.5 moves in trained agents (vs 100 in random). Trained agents learned to exploit double-pass: P1 places, P2 places, P1 places (2-1 lead), then both pass → P1 wins. One training run showed P1 100% winrate. The game's theoretical depth is completely bypassed by optimal play.

### Phase 3 — Strategic Analysis

**In theory (if double-pass were removed)**:
- The 3D topology creates rich group dynamics — 6-neighbor adjacency makes liberty counting deeply complex
- Adjacent-to-enemy forces constant contact, creating tight tactical fights across z-layers
- Surround capture in 3D is harder than in 2D Go (more neighbors = more liberties) but more devastating when it happens
- The 3D space creates emergent concepts: "layers" as territory, multi-dimensional ladders
- Multiple fronts could develop as the contact zone expands through all three dimensions

**In practice (as actually played)**:
- No strategic depth — trained agents play 3-4 moves and double-pass
- No counter-play — first player gets +1 piece advantage and forces the end
- No short/long term tension — everything is immediate
- No emergent concepts develop in 3.5 moves
- The 3D topology is entirely irrelevant to actual gameplay
- One training run (seed=92084) showed 100% P1 winrate — broken balance

**Comparison to known games**: Resembles a degenerate Go variant where the fuseki/joseki/endgame structure is replaced by a 2-move opening theory. The forced-contact mechanic (adjacent_to_enemy) is interesting and novel but wasted on this win condition.

### Phase 4 — Verdict

```
Game ID: f9eba2b4bf19
Rules Summary: 3D Go with forced contact — place adjacent to enemies, surround capture, win by majority at game end.
Topology: 3D 4x4x4 grid, von Neumann adjacency (64 cells)

SCORES (1-10):
  Strategic Depth: 2 — Trained agents solve the game in 3-4 moves via double-pass exploitation
  Emergent Complexity: 3 — Surround capture in 3D creates interesting cascades in random play, but trained play shows none
  Balance: 3 — Two of three training runs were balanced (50%), but one showed 100% P1 winrate
  Novelty: 5 — 3D Go with forced-contact is a genuinely novel concept, just poorly executed
  Replayability: 2 — Every competent game follows the same 3-move pattern
  Overall "Would I play this again?": 2

KILLER FLAWS:
- Double-pass + majority = games end in 3-4 moves; optimal play bypasses all game mechanics
- First-mover advantage: P1 can always get a +1 lead and force double-pass (shown in training)
- The adjacent_to_enemy constraint makes it impossible to open new fronts or escape local fights

BEST QUALITY:
- The concept of forced-contact Go in 3D is genuinely interesting. Surround capture across
  z-layers creates complex group dynamics in random/casual play. The 3D liberty counting is
  harder than 2D Go and could produce deep reading if the win condition supported longer games.

IMPROVEMENT IDEAS:
- Replace majority win with territory or connection win to force engagement. Alternatively,
  add a minimum game length (e.g., 30 turns) before double-pass can end the game, or
  require the board to be >50% full before majority is counted. The forced-contact mechanic
  deserves a win condition that rewards long-term play.
```

---

## Game 2: cce37f4762c4 — "Outnumber Hex"

### Phase 1 — Rule Comprehension

**Board**: 2D grid, 8x8 (64 cells), von Neumann adjacency (face-adjacent only — up to 4 neighbors per interior cell).

**Turns**: Players alternate placing 1 stone per turn.

**Placement**: Place on any empty cell. No constraints beyond emptiness.

**Capture**: Outnumber with threshold 3. After placing, each adjacent enemy stone is removed if it has ≥3 neighbors belonging to the placing player. In practice: an interior stone (4 neighbors) is captured if 3 of its 4 neighbors are the enemy; edge stones (3 neighbors) need all 3 to be enemy; corner stones (2 neighbors) can never be outnumber-captured.

**Win condition**: Connection. P1 wins by creating a connected path (von Neumann adjacency) from x=0 to x=7 (left column to right column). P2 wins by connecting y=0 to y=7 (top row to bottom row). Cross-cutting goals like Hex. Max 100 turns, double-pass ends by majority.

### Phase 2 — Strategic Play

**Self-play game 1 — Hex-style racing**:
P1 builds along row 0: (0,0)→(1,0)→(2,0)→...→(7,0). P2 builds down column 0: (0,1)→(0,2)→...→(0,7). P1 completes the horizontal connection at move 15 and wins immediately. This confirms the Hex-like race dynamic — the game is fundamentally about who completes their spanning path first.

**Self-play game 2 — Blocking and capture testing**:
P1 builds central path, P2 blocks. Tested outnumber capture: P1 places at (3,3), (1,3), and (2,2) around P2's stone at (2,3). With 3 of P2's 4 neighbors being P1, the capture triggers — P2's stone is removed. This creates a "break" in any path P2 was building through that cell.

**Self-play game 3 — Parallel paths**:
Both players build parallel advance along their winning dimensions. When P1 extends rightward, P2 drops blocking stones in P1's path. P1 must route around blocks. The staircase routing is essential because von Neumann adjacency doesn't allow diagonal connections.

**Random game observations** (seeds 1-3):
- Seed 1: P1 wins at move 59 (connection), balanced game with captures occurring mid-game
- Seed 2: P2 wins at move 68 (connection), close game
- Seed 3: P2 wins at move 72 (connection), came down to the wire
- All three games ended by connection, not timeout — the win condition works
- Games fill ~50-60% of the board before someone connects
- Outnumber captures are infrequent (maybe 2-5 per game) but impactful when they happen

**Training data**: Average game length 62-73 moves. Trained vs random 64-70% (modest). All three training runs showed 50% P1 vs P2 winrate (well balanced). The lower trained-vs-random suggests either high variance or the game is strategically deep enough that PPO struggles to learn strong play.

### Phase 3 — Strategic Analysis

**Distinct strategies**:
- *Direct push*: Build a straight path along your winning dimension (fast but predictable, easy to block)
- *Wide spread*: Place stones across the whole board creating multiple partial paths, then connect them (slower but harder to block completely)
- *Capture disruption*: Cluster 3 stones around an enemy's key path stone to remove it, breaking their connection
- *Corner anchoring*: Corner stones can never be captured, making them safe connection anchors

**Counter-play**: Blocking the opponent's path forces routing around obstacles. Since connections must be von-Neumann-adjacent (no diagonals), a single blocking stone in a column/row forces a detour of at least 2 extra moves. This creates meaningful blocking decisions.

**Short/long term tension**: Immediate connection threats require defensive responses, but spreading too thin leaves stones vulnerable to outnumber capture. Building wide for future connection vs. pushing a narrow path creates strategic tension.

**Emergent concepts**:
- *Bridging*: Placing stones with a gap that can be connected in one move (borrowed from Hex)
- *Ladders*: Forcing sequences where the attacker pushes and the defender must respond
- *Path multiplicity*: Having multiple independent connection threats at once (like Hex's "double connection")
- *Capture zones*: Avoiding placing stones where 3 enemies already surround them

**Topology**: The 2D grid with cross-directional connection goals perfectly creates the Hex intersection property — P1's horizontal advance physically crosses P2's vertical advance, guaranteeing conflict.

**Comparison to known games**: This is essentially Hex played on a square grid with outnumber captures. The von Neumann adjacency (no diagonals) makes connections harder to build than in standard Hex (which uses hexagonal adjacency). The outnumber(3) capture adds a modest tactical layer not present in standard Hex. The game is competent but not highly original — the core mechanic is directly borrowed from Hex.

### Phase 4 — Verdict

```
Game ID: cce37f4762c4
Rules Summary: Hex-like connection race on 8x8 grid with outnumber captures — connect your edges while blocking the opponent's.
Topology: 2D 8x8 grid, von Neumann adjacency (64 cells)

SCORES (1-10):
  Strategic Depth: 5 — Hex-like connection dynamics create genuine reading depth; outnumber captures add tactical wrinkles
  Emergent Complexity: 5 — Bridging, ladders, path multiplicity, and capture zones all emerge naturally
  Balance: 7 — All three training runs showed exactly 50% winrate; random games won by both sides
  Novelty: 3 — Essentially Hex on a square grid with a capture mechanic; the core concept is well-known
  Replayability: 5 — Hex-like games have proven replay value; each game requires different routing
  Overall "Would I play this again?": 5

KILLER FLAWS:
- Low novelty — the game is a competent Hex variant but doesn't bring a fundamentally new idea
- Outnumber(3) captures are rare enough (need 3 of 4 neighbors) that they barely affect play;
  most games play out as pure connection races
- Trained-vs-random of only 64-70% suggests either high variance or that the game doesn't reward
  skill as clearly as it should (for comparison, Go PPO agents easily reach >90% vs random)

BEST QUALITY:
- The cross-directional connection goals create the proven Hex dynamic of inherent path
  intersection. Games are well-balanced, go to reasonable length (60-70 moves), and end
  decisively by connection rather than timeout. The basic gameplay loop works.

IMPROVEMENT IDEAS:
- Lower the outnumber threshold to 2 so captures happen more frequently and become a central
  strategic element rather than a rare edge case. This would differentiate the game further
  from standard Hex and create more meaningful tactical decisions about stone density.
```

---

## Summary Comparison

| Category | f9eba2b4bf19 (3D Contact Go) | cce37f4762c4 (Outnumber Hex) |
|----------|------------------------------|-------------------------------|
| Strategic Depth | 2 | 5 |
| Emergent Complexity | 3 | 5 |
| Balance | 3 | 7 |
| Novelty | 5 | 3 |
| Replayability | 2 | 5 |
| Overall | **2** | **5** |

**f9eba2b4bf19** has genuinely novel mechanics (3D forced-contact Go) but is completely broken by the majority + double-pass interaction. The game that *could* be played is interesting; the game that *is* played by trained agents lasts 3.5 moves.

**cce37f4762c4** is a solid, balanced Hex variant with working connection goals and decent game length. It doesn't bring much novelty (Hex on a grid + rare captures), but it functions as a competent abstract strategy game.
