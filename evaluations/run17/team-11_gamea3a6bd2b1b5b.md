# Team-11 Evaluation — Game `a3a6bd2b1b5b` (R17 rank 2)

**Team ID:** team-11
**Game ID:** `a3a6bd2b1b5b` (R17 rank 2 by GE; GE 0.2933, ELO 2611.9)
**DB:** `/Users/jamesbrowne/aigame/genesis_v2_run17.db`
**Generation:** 11 (parent `8f36d001577d`, GE=0.0008 → big single-mutation jump on `win_condition`)
**Headline:** 3D 4³ grid, **surround capture**, **place-only** (NOT a place+move hybrid), connection win on orthogonal axes (P1=x, P2=y).

---

## Phase 1 — Rule Comprehension

### Board structure
- 3 dimensions, axis_size = 4 → **4×4×4 = 64 cells**
- Topology: **grid** (Manhattan/6-neighbour). Max_degree = 6.
- Cell index: `c = z·16 + y·4 + x`. Verified via `play_helper`.

### Action space
- 64 placement actions + action 64 = pass → 65 total.
- `action_types: ['place']` only. The `move_constraint` field is metadata; **no move actions are emitted**. (Confirmed by inspecting legal-action set: max ID = 64, never any 65+ move actions.) **Hybrid place+move = NO.**

### Turn structure
- **Alternating** (`turn_type: alternating`, `pieces_per_turn: 1`).

### Placement / movement
- Place on any empty cell. `first_move_anywhere: true`. No suicide rule explicitly listed; surround removes 0-liberty enemy groups after placement.

### Capture
- **Surround** (Go-style group capture). The stored `threshold: 1` is irrelevant for surround — only `outnumber` reads it. After each placement, all enemy groups adjacent to the placed cell with 0 liberties are removed.
- In all three Phase-2 games, **zero captures fired**. Surround is a *latent* mechanic in this game's natural openings: stones spread fast enough across the 64-cell volume that 6-neighbour groups rarely run out of liberties before a connection completes the game.

### Propagation
- `prop_type: none`. Influence rule is a dead field.

### Win condition
- Connection (`condition_type: connection`).
- `target_dimension = 0` → **P1 connects x = 0 face to x = 3 face**.
- `target_dimension_p2 = 1` → **P2 connects y = 0 face to y = 3 face**.
- `threshold: 42.08` is **dead text** — `_check_connection` ignores `wc.threshold`; only `connects_faces(cells, dim)` BFS matters.
- `max_turns: 87`.

### Degeneracy flags
- ❌ `propagation_rule.strength=1.4` & `decay=0.47` are inert (`prop_type: none`).
- ❌ Connection threshold 42.08 is inert.
- ⚠️ Surround capture rarely fires in observed play (0/3 games). Not "broken" — just structurally dormant given the connection-race tempo.
- ✅ Connection objective is reachable on a 4³ board (minimum win path = 4 collinear stones).

---

## Phase 2 — Strategic Play

All three games engine-verified via `/tmp/game11_helper.py` (custom replay/render of `a3a6bd2b1b5b`). Each move below was checked against `engine.get_legal_actions()` before commit.

### Game 1 — "P1 fix-y, sweep-z wall" (Player-1 perspective first)

**Idea (P1):** plant the entire x=0 face one z-line at a time so that every row attempt has a fresh x=0 anchor, regardless of P2's blocks at x=1.

Moves: `0,1,16,17,32,33,48,49,4,5,20,21,36,37,52,53,8,9,24,25,40,41,56,57,12,13`

| # | P | Action | Cell | Note |
|---|---|--------|------|------|
| 1 | 1 | 0 | (0,0,0) | P1 corner — anchors x=0 face |
| 2 | 2 | 1 | (1,0,0) | P2 block + start column at (x=1, z=0) |
| 3-8 | — | 16,17,32,33,48,49 | z-sweep at y=0 | P1 walls x=0 col, P2 walls x=1 col |
| 9-16 | — | 4,5,20,21,36,37,52,53 | z-sweep at y=1 | same pattern, y=1 |
| 17-24 | — | 8,9,24,25,40,41,56,57 | z-sweep at y=2 | same pattern, y=2 |
| 25-26 | — | 12,**13** | y=3 step | **P2 plays 13 → completes y-column at (x=1, z=0): {1,5,9,13}, y=0..3 → P2 WINS** |

**Result: P2 wins on move 26.** P1 ended with 13 stones forming a perfect (0, 0..3, 0..3) wall at x=0 — but with no breakthrough at x=1 (P2 mirrored at x=1) the row never crossed.

**P1 reflection:** the wall was "right" structurally (every potential P2 column at x=0 broken by P1) but **the mirrored x=1 P2 wall is itself a 4×4 grid of column-completion candidates**. As soon as I exhausted y=0,1,2 sweeps and reached for y=3, P2 closed *any* column on demand. I needed to either (a) commit to fewer z-layers and bridge through y=2/3 *before* y-3 was the only x=1 cell P2 needed, or (b) force a capture by leaving 17 with no liberties.

**P2 reflection:** simply mirroring P1 at x=1 is a winning strategy against this "wall" plan. The P2 column win triggers automatically the moment P1's y-3 sweep starts — *every* y-3 P1 move forces a P2 y-3 reply on the column line, which is the column's missing 4th stone.

**Endgame mode:** connection win, no double-pass, no max-turn timeout.

### Game 2 — "P1 central, P2 races x=3 column" (Player-2 perspective first)

Moves: `21,22,17,18,16,19,20,3,1,2,4,7,5,6,8,11,9,10,12,15`

| # | P | Cell | Note |
|---|---|------|------|
| 1 | 1 | (1,1,1) | P1 takes central interior |
| 2 | 2 | (2,1,1) | P2 mirror-block + threat |
| 3-7 | — | (1,0,1), (2,0,1), (0,0,1), (3,0,1), (0,1,1) | P1 fills z=1 partially |
| 8 | 2 | **(3,0,0)** | P2 quietly opens column at (x=3, z=0) |
| 9-19 | — | … | P1 sweeps z=0 corners; each P1 move forces P2 to "block" — but every P2 block at x=3 row is a column-filler |
| 20 | 2 | **(3,3,0)** | P2 closes column {3,7,11,15} → **P2 WINS** |

**Result: P2 wins on move 20.** P1 occupied 10 cells of the z=0 plane but never crossed x=2 in a connected component, while P2 quietly accumulated all four (x=3, y=0..3, z=0) stones.

**P1 reflection:** central-first opening is *worse* than corner-first because the central stone (1,1,1) doesn't anchor *either* face. By move 8 I had no x=3-face stone and had given P2 an undefended column line at x=3.

**P2 reflection:** Even when P2's "blocks" don't visibly threaten, the act of sealing P1's row at x=3 builds a column line for free. The right way to play P2 is *don't block in the interior* — block on whichever face is opposite to your own win-axis face.

**Endgame mode:** connection win, no double-pass.

### Game 3 — "P1 column-deny + row-bridge" (seats swapped reasoning frame)

I deliberately swapped seat-identity bias: now I argue *from P2's perspective first* on each P1 move, then commit P1.

Moves: `5,6,9,10,13,14,2,17,1,0,3,21,4`

| # | P | Cell | Note |
|---|---|------|------|
| 1 | 1 | (1,1,0) | P1 plants x=1 stone in y=1 row — kills two columns: x=1,z=0 (P2's natural prime) AND threatens row at (y=1,z=0) |
| 2 | 2 | (2,1,0) | P2 blocks P1's row at x=2,y=1 |
| 3 | 1 | (1,2,0) | P1 climbs y in same x=1 strip — keeps killing column x=1,z=0 |
| 4 | 2 | (2,2,0) | mirror block |
| 5 | 1 | (1,3,0) | column x=1,z=0 fully dead at y=1,2,3 (only y=0 left, but only 1 cell) |
| 6 | 2 | (2,3,0) | P2 row-block; P2 column at (x=2,z=0) now has y=1,2,3 |
| 7 | 1 | **(2,0,0)** | P1 grabs y=0 of P2's would-be column {2,6,10,14} → kills it |
| 8 | 2 | (1,0,1) | P2 starts a fresh column line at (x=1,z=1) |
| 9 | 1 | (1,0,0) | P1 connects: (2,0,0)–(1,0,0)–(1,1,0)–(1,2,0)–(1,3,0) is now one chain spanning x=1,2 with options at y for the bridge |
| 10 | 2 | (0,0,0) | P2 blocks the obvious x=0 corner |
| 11 | 1 | (3,0,0) | P1 grabs the x=3 face stone, adjacent to (2,0,0) — **chain now spans x=1..3** |
| 12 | 2 | (1,1,1) | P2 ignores triple-threat, continues column line |
| 13 | 1 | **(0,1,0)** | (0,1,0)→(1,1,0) bridges x=0 to chain. **Path: (0,1,0)–(1,1,0)–(1,0,0)–(2,0,0)–(3,0,0). x=0,1,1,2,3 ✓ connected by grid-adjacency. P1 WINS.** |

**Result: P1 wins on move 13** (7 P1 stones, 6 P2 stones, no captures).

**Critical Phase-2 finding:** at move 11, P1's chain `{1, 2, 3, 5, 9, 13}` simultaneously threatens **three** x=0 entry cells — (0,1,0)=4 via 5, (0,2,0)=8 via 9, (0,3,0)=12 via 13. P2 had only one stone on M12; **a single block cannot stop three threats**. This is the 3D analogue of a Hex *triple-edge* — and it's the strongest tactical motif we found in the game.

**P2 reflection:** the moment P2 saw a P1 chain at (1,y,0) for y=1,2,3 and (2,0,0), P2 had to abandon column-building immediately and convert all remaining moves to x=0 face defense. M2's row-block was already a mistake — P2 should have played on the x=0 face (e.g. (0,1,0)) at move 2 to deny P1's eventual bridge.

**Endgame mode:** connection win.

### Strategy guide for each side

**P1 strategy guide.** (i) Don't build symmetric walls — they let P2 win on tempo. (ii) Plant stones at a fixed `(x=k, z=k')` strip across multiple y values *first* — this kills the entire P2 column at that strip with a single 4-stone investment. (iii) Then convert the strip stones into x-row bridges using y-axis adjacency. (iv) The "triple-edge" pattern: a chain of stones at `(x=1, y=0..3, z=0) ∪ {(2,0,0), (3,0,0)}` threatens 3 simultaneous x=0 entries and is unstoppable. Aim for it.

**P2 strategy guide.** (i) Mirror P1 on the *opposite* face at the same y. Every face-mirror move advances both blocking and column-building. (ii) If P1 commits to a y-sweep at fixed z, the column at (x = P1's row index, z = sweep z) wins automatically when P1's last y move forces P2's reply. (iii) Beware "column-deny" P1 plays at x=1 across y — that's the strongest counter and you must shift to a non-mirrored column quickly.

---

## Phase 3 — Strategic Analysis (joint)

- **Distinct viable strategies?** Yes, at least three played-out kinds: *wall-builder* (Game 1), *interior-anchor* (Game 2), *column-deny + bridge* (Game 3). They're not equivalent — the column-deny strategy beats the wall strategy in head-to-head on small board.
- **Counter-play.** Yes — Game 3 shows P1 can break a P2 column-build by populating the column with their own stone (M7 `(2,0,0)` killed P2's primary threat). And P2 can break P1's row by blocking adjacent x=1 cells, but at the cost of building their own column elsewhere.
- **Short vs long-term tension.** Real. Each P2 block-of-P1 also advances P2's column. Each P1 stone in the strip kills a P2 column AND eventually contributes to an x-row. There is genuine *each-move-does-two-things* duality.
- **Emergent concepts.**
  - **3D path-routing:** real and used (Game 1 and 2 both had escape attempts to z>0).
  - **Sub-volume control:** real — controlling a (y=k, z=k') plane is a unit of strategic value.
  - **Tempo / triple-edge:** the unblockable triple-x=0 fork in Game 3 is exactly Hex's "edge-template" theory exported to 3D.
  - **Capture-as-tactic:** ABSENT. Surround capture didn't fire even once. The mechanic exists but the tempo of connection-races doesn't reward enclosing groups.
- **Does 3D matter?** **Yes.** A 2D 4×4 reduction would let P2 always win by mirroring (no z-escape). The third dimension lets P1 shift z-layers when blocked, and lets P2 multiply column candidates from 4 (in 2D) to 16 (in 3D). Both effects deepen play. The flat-to-2D test would *lose* depth.
- **Topology choice.** Grid is right for this game — moore would push max_degree to 26 (action space 27× larger, surround near-impossible), torus would let P2 wrap a column infinitely (broken). Hex would change the connection geometry entirely. So grid is structurally bound to the rule set.
- **Movement.** N/A (place-only). The R17 prompt warned of vestigial moves, but this game has *zero* move actions in its action space — not vestigial, just absent.
- **First-mover advantage.** P1 won 1/3, P2 won 2/3. With deliberate play (Game 3) P1 wins comfortably. The 2/3 P2 wins were against suboptimal P1 strategies. We estimate optimal play favors P1 modestly (Hex-theorem-style), but the **structural "blocks-line-up-as-columns" trap means *any* P1 misplay swings strongly to P2** — i.e., the game is *unforgiving*, but not biased once both sides play correctly.

---

## Phase 4 — Novelty Adversary

**Adversary's case (game is NOT novel):**

(a) **3D Hex / Hex-3D.** The game IS structurally a 3D Hex variant: two players race to connect opposing faces, axes orthogonal. 3D Hex has been studied (Yamaguchi, Kishimoto et al). The face-vs-face goal is *exactly* Hex's win definition. Surround capture is the only thing added — **so this is "3D Hex + Go capture."**

(b) **3D Connection Go (R8 family).** The R17 champion (`44f6630277b3`) is "3D + custodian + connection + place+move." This game is *very nearly* the same family — same dimension, same topology, same connection win, same alternating turns. The only differences are (i) **surround instead of custodian** capture, (ii) **place-only instead of place+move** action set. So at the family level this is "R8/R17-family Connection Go in 3D" — and the family is what justifies R17 to begin with. Within the family, this game is not the most novel member; the place+move hybrid champion is.

(c) **Qubic / 3D Tic-Tac-Toe.** Both 3D 4³ board, both connection-style. But Qubic wants 4-in-a-row across diagonals; this game wants face-to-face *graph* connection. The connection geometry is genuinely different — Qubic doesn't allow zigzag paths, this game does. Adversary concedes: not Qubic.

(d) **Go on a 4³ board.** Standard Go's win is territory; this is connection. Capture rule matches (group surround), action set matches (place + pass). Is this "Go with a connection score-out"? Closer than expected — connection is a *terminating* condition not a scoring condition, but a Go expert *would* recognize the surround capture immediately. The transfer is mostly mechanical.

(e) **Reskin test.** Could a Hex-3D + Go hybrid expert pick this up immediately? **Yes,** with one exception: the orthogonal-axis assignment (P1=x, P2=y) means the *opposing-face* heuristic from Hex transfers but the *blocking-as-column* trap is sharp enough that a Hex player without 3D Connection Go experience would likely lose to a player who has internalized "every block in your own win-line is a free column move."

**P1/P2 rebuttal:**

- **Rebut (a): not pure 3D Hex.** Surround capture is non-trivial in principle (we never triggered it, but a longer game with cluster-fights *would*) — and standard 3D Hex has no capture. The presence of the capture rule changes legal-move evaluation: a stone with no liberties dies. This shows up only under aggressive tempo deviation, which neither of our 3 games reached.
- **Rebut (b): R17 champion is the more novel sibling.** The champion has place+move; this game is the place-only "stripped-down" sibling. Within the family, this game is *less* novel than the champion — exactly because it hews closer to plain 3D Hex.
- **Rebut (d): Go expert wouldn't recognize the connection objective.** A Go expert opening this game would assume territory or majority and miss the face-to-face goal. The capture rule transfers but the *win* doesn't, so the strategic transfer is partial.

**Novelty score: 5/10.** It's a Hex-3D + Go-capture composite. The composite is real, novel-ish, and makes a different game than either parent — but neither component is new and the family this game lives in (3D Connection Go) was *already* identified by R8 in 2D.

---

## Phase 5 — Verdict

**Team ID:** team-11
**Game ID:** `a3a6bd2b1b5b`
**Rules summary:** 4³ grid, Go-style surround capture, alternating place-only, P1 connects x-faces / P2 connects y-faces. Connection BFS, max 87 moves.
**Topology:** 3D grid 4×4×4, max_degree=6.
**Turn structure:** alternating.
**Hybrid actions:** **NO** (place-only despite R17's general trend).

**SCORES (1-10):**

- **Strategic Depth: 5/10** — real triple-threat tactics, real column-vs-row duality, but small board (4³) caps deep planning at ~5-move horizon. Surround capture never engaged in our games, so a whole tactical layer was dormant.
- **Emergent Complexity: 5/10** — the "blocks-line-up-as-columns" structural property is genuinely emergent and creates an interesting forced-tradeoff; sub-volume control patterns appear; capture would deepen this further if it ever fired.
- **Balance: 4/10** — *with seat-swap evidence:* P1 lost games 1-2 (wall strategy, central strategy) and won game 3 (column-deny strategy). Default/naive P1 loses to mirroring P2 — the structural trap is real. Optimal P1 likely wins by Hex-theorem analogue, but the gap between optimal and naive is too sharp; for a human-rated game this would feel "P1-must-know-the-trick" rather than "balanced."
- **Novelty (post-adversary): 5/10** — 3D Hex × Go capture composite; not new at the component level, mildly novel at the composite level, less novel than the R17 place+move champion (`44f6630277b3`) within the same family.
- **Replayability: 5/10** — 16 P1 row-planes × 16 P2 column-planes × multiple opening choices ≈ rich opening tree, but mid-game converges on the same column-deny vs wall-build motifs quickly. Reasonable session-to-session variety.
- **Overall "Would I play this again?": 5/10** — solid, comprehensible, has real tactical bite, but feels like an austere stripped-down 3D Hex more than a lush new game.

**CLOSEST KNOWN-GAME ANALOG:** 3D Hex with Go-style group capture (a/k/a "3D Connection Go, place-only"). Not identical because (i) surround capture *is* a real-but-dormant rule and (ii) the R8 2D family found this is a publishable design space — but this 3D place-only specimen is the most stripped-down member of the family.

**KILLER FLAWS:**
- Propagation rule fields (`strength`, `decay`, `radius`) are present but completely inert (`prop_type: none`). Bookkeeping noise.
- Connection threshold (42.08) is inert text.
- Surround capture never fires in connection-race play. Latent rule.
- "Blocks-line-up-as-columns" structural property gives default-naive P2 a winning strategy against default-naive P1, even though optimal P1 should win.
- Place-only on a 64-cell board with connection win means many games end before any deep tactical position arises.

**BEST QUALITY:** The orthogonal-axis assignment creates a real tempo duality where every P2 blocking move *also* advances P2's column (and symmetrically for P1). This is the cleanest "every move means two things" structure I observed in this game — and it's the structural reason GE selected for it.

**3D STRUCTURAL CONTRIBUTION:** Real and significant. Flattening to 2D 4×4 would let mirror-blocking trivially win for the second player (no z-escape). The third dimension is *load-bearing* for the game's depth — but only modestly so, because the same 3D dimension that lets P1 escape blocks also gives P2 4× more column candidates. Net: 3D adds depth but also enlarges the trap.

**IMPROVEMENT IDEAS:** Switch the capture rule to **custodian**. Custodian capture fires on axis-aligned walks and would interact directly with the connection-race tactics — a partially-built P1 row of 3 stones with a P2 stone at the end could be flipped, dramatically changing the tempo calculus. This is exactly the rule used by the R17 champion (`44f6630277b3`), and it's likely why the champion ranks higher: custodian + connection + 3D activates the latent capture layer that surround leaves dormant. (Alternative: lift `axis_size` to 5 — gives more interior cells for surround groups to actually form.)

---

*Phase-2 evidence files:* `/tmp/game11_helper.py` (engine-verified replay tool for this game), three game traces verified via that helper. No moves were committed without legality check.
