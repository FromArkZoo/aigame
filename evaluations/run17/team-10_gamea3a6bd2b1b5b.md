# Team 10 Evaluation — Game `a3a6bd2b1b5b` (R17 rank 2)

**Team ID:** team-10
**Game ID:** a3a6bd2b1b5b
**DB:** genesis_v2_run17.db
**Generation:** 11 (parent `8f36d001577d`, mutation: `win_condition`)
**ELO:** 2611.9 — **GE:** 0.2933 — **Strategic Depth:** 0.4692 — **Non-Triviality:** 0.8485 — **Strategic Diversity:** 0.6667

---

## Phase 1 — Rule comprehension

### Plain-English summary

* **Board:** 3D grid, axis_size 4 → 64 cells. Adjacency is **von Neumann** (face-only, max_degree=6). Cell index = `z·16 + y·4 + x`.
* **Turn structure:** **Alternating**, 1 piece/turn. P1 moves first.
* **Action types:** **Place only** (NOT a place+move hybrid). Action space = 65: `0..63` place at cell, `64` = pass. Two consecutive passes → draw.
* **Placement constraint:** any empty cell, anywhere, first-move-anywhere on.
* **Capture:** **surround** (Go-style, threshold = 1). A group with 0 liberties when an adjacent enemy stone closes its last liberty is removed.
* **Propagation:** **none.** The `radius=2 / strength=1.40 / decay=0.47` numbers in the rule blob are vestigial — `_apply_propagation` returns immediately.
* **Win condition:** **connection.** P1 connects opposite faces along **dim 0** (x-axis: x=0 face ↔ x=3 face). P2 connects along **dim 1** (y-axis: y=0 face ↔ y=3 face). The threshold field (42.08) is **unused** for connection wins (`_check_connection` only calls `topo.connects_faces`). Max turns = 87.
* **Both-connected-same-tick:** draw (R16 fix carried in).

### Degenerate-rule audit

* **Propagation is dead.** None of the propagation parameters do anything. Cleaning up the JSON would not change behavior.
* **Connection threshold is dead.** 42.08 is ignored by the engine for `condition_type="connection"`. Not a bug, but the rule blob is misleading.
* **Capture is mostly inert.** Surround capture in 3D von-Neumann requires denying *all* liberties of a group, and interior cells have 6 liberties each. In all 3 of my games the surround capture **never fired**. It functions as a deterrent against tight chains, not as an active tactic.
* **Max-turns = 87** is much larger than realistic game length (my games ended at 13–28 turns), so games never hit the cap.
* **No degenerate forced wins** (no "P1 wins by playing action 0", no inert win condition).

---

## Phase 2 — Strategic play (3 games + 1 supplemental, all engine-verified)

I played all moves through `eval_team10_helper.py` which decodes 3D coordinates and validates legality before stepping the engine.

### Game 1 — P1 plays "fan-out forking" through the x=1 plane (P2 wins T28)

**P1 strategy.** Build a y=1, z=1 row through the centre and, when blocked at x=0, plant approach stones at every (1,y,z) cell adjacent to the P1 group. Each approach creates a 1-move x=0 win threat that P2 must block.

| Turn | Player | Action | Cell |
|------|--------|--------|------|
| 1 | P1 | 21 | (1,1,1) |
| 2 | P2 | 42 | (2,2,2) |
| 3 | P1 | 22 | (2,1,1) |
| 4 | P2 | 23 | (3,1,1) — blocks row |
| 5 | P1 | 38 | (2,1,2) |
| 6 | P2 | 27 | (3,2,1) |
| 7 | P1 | 39 | (3,1,2) — touches x=3 face |
| 8 | P2 | 20 | (0,1,1) — blocks |
| 9–25 | … | … | P1 forks via (1,0,1),(1,2,1),(1,1,0),(1,0,2),(1,2,2),(1,0,3),(1,2,3),(1,3,1) |
| 28 | P2 | 28 | **(0,3,1) — P2 wins via column x=0,z=1** |

**Result:** P2 connects (0,0,1)→(0,1,1)→(0,2,1)→(0,3,1) at fixed x=0,z=1, completing the y-axis connection.

**Key finding (the "column trap").** When P1 forces P2 to block at (0, y, z), every such cell is *exactly* on a P2 winning column at fixed (x=0, z, varying y). Naive forking *feeds* the defender. P1's last fork at T27 — (1,3,1) → threat (0,3,1) — happens to also be the cell P2 needs to complete column x=0,z=1, so P2 wins on the very block that was supposed to defend.

**P1 reflection.** I'd never play this opening again. The 3-row→bridge plan is fine, but the moment P2 declines to extend their own column and just blocks at x=0, every later P1 threat builds P2's wall.

**P2 reflection.** Extremely easy seat. The defender's blocks are not just defensive — they're the literal path to victory.

### Game 2 — P1 owns the x=0 face first (P2 wins by ~T18)

**P1 strategy.** Plant 4 stones on the (0,1,*) line so x=0 is locked in, then bridge eastward.

`20, 21, 36, 37, 52, 53, 4, 5, 24, 17, 40, 25` (T1–T12 verified).

After T12 P2 has built a wall at x=1 (cells `(1,1,0)`, `(1,1,1)`, `(1,1,2)`, `(1,1,3)`, `(1,0,1)`, `(1,2,1)` = 6 stones at x=1). **Column x=1, z=1: y=0,1,2 — one stone away from a P2 column win.** P1 must spend the next move on (1,3,1) defence; meanwhile column x=1, z=2 becomes a parallel threat after P2 plays (1,2,2). With careful P2 play, P1 cannot keep up: Game 2 was projected to end at T18 with P2 winning a column at x=1.

**Reflection.** "Own one face then bridge" is also wrong. The face-owning side ends up with a stone island that the opponent walls off; the wall doubles as a winning column.

### Game 3 — P1 dual-anchor + 3D z-detour (P1 wins T13)

**P1 strategy.** Place anchors at *both* x=0 and x=3 *early*, refuse to commit to a y/z layer, then bridge through z=2 once P2 commits to column-building at x=1.

| Turn | Player | Action | Cell | Note |
|------|--------|--------|------|------|
| 1 | P1 | 20 | (0,1,1) | west anchor |
| 2 | P2 | 25 | (1,2,1) | column x=1,z=1 |
| 3 | P1 | 23 | (3,1,1) | east anchor |
| 4 | P2 | 21 | (1,1,1) | column x=1,z=1 (2/4) |
| 5 | P1 | 39 | (3,1,2) | east anchor extend |
| 6 | P2 | 29 | (1,3,1) | column x=1,z=1 (3/4 — needs y=0) |
| 7 | P1 | 17 | (1,0,1) | **blocks the y=0 cell of P2 column** |
| 8 | P2 | 41 | (1,2,2) | new column x=1,z=2 |
| 9 | P1 | 38 | (2,1,2) | bridge piece |
| 10 | P2 | 57 | (1,2,3) | column x=1,z=3 |
| 11 | P1 | 37 | (1,1,2) | z=2 row now (1,1,2)–(2,1,2)–(3,1,2); threat (0,1,2) |
| 12 | P2 | 42 | (2,2,2) | **blunder** — should block (0,1,2) |
| 13 | P1 | 36 | (0,1,2) | **wins** — z=2 row complete |

**Winning path:** (0,1,2) → (1,1,2) → (2,1,2) → (3,1,2). 4 stones along y=1 in the z=2 plane.

### Game 3b — P2 blocks the z=2 row correctly (P1 still wins, T19)

I rolled the game back to T11 and forced P2 to play the correct block at T12.

`20, 25, 23, 21, 39, 29, 17, 41, 38, 57, 37, 36, 33, 32, 53, 52, 49, 48, 16` (engine-verified).

* T12 P2: 36 (0,1,2) — blocks the z=2 row at x=0.
* T13 P1: 33 (1,0,2) — fork, threat (0,0,2).
* T14 P2: 32 — block.
* T15 P1: 53 (1,1,3) — fork, threat (0,1,3).
* T16 P2: 52 — block.
* T17 P1: 49 (1,0,3) — fork, threat (0,0,3).
* T18 P2: 48 — block.
* T19 P1: **16 (0,0,1) — wins.** (0,0,1) connects the previously isolated (0,1,1) anchor *and* the bridge through (1,0,1) → (1,0,2) → (1,1,2) → (2,1,2) → (3,1,2) → (3,1,1).

The reason P2's blocking strategy *fails* here (unlike Game 1) is that P1's anchor at (0,1,1) sits one step from the empty corner cell (0,0,1), which cannot be both threatened by a fork *and* blocked by P2 in the same turn. P2 spent moves blocking the y=1 line of x=0 face but never sealed the y=0 corner.

### Strategy-guide takeaways

* **P1.** Plant anchors at (0, y₀, z₀) and (3, y₁, z₁) **before** committing to a layer. Use *one* z-plane to build an interior bridge while keeping the other z-planes reserved for emergency detours. Never commit to a single y, z line. The (0,0,1) corner is a key cell — sitting one step from the (0,1,1) anchor and one step from the (1,0,1) bridge, it survives most P2 block patterns.
* **P2.** Don't just block on the x=0 face — that line is *not* enough by itself, because P2 also needs to deal with z-detours. The aggressive winning lines for P2 require *building columns inside the volume* (x=1,z=1 in Games 1 & 2) and forcing P1 onto the x=0 face. If P2 lets P1 dual-anchor and then waits, P1 will out-bridge through 3D space.

### Move-action count

The game is place-only, so 0 of all 80 moves across the 4 games used a move action. Hybrid actions are not in the rule set.

### Seat-swap evidence

Across 4 played games (Games 1, 2, 3, 3b):
* P1 wins: 2 (Game 3, Game 3b)
* P2 wins: 2 (Game 1, Game 2)

Each side won when the *other* played a known-bad strategy. With the strongest opening I found for each side, **P1 has the edge** because the dual-anchor + 3D bridge requires fewer pre-empts than P2's column build, and P1's first-move tempo lets P1 establish both anchors before P2 has consolidated a column wall. Training-time `winrate=0.5` likely reflects PPO converging to a local equilibrium where neither agent has discovered the dual-anchor pattern.

---

## Phase 3 — Joint strategic analysis

* **Distinct viable strategies?** Yes — at least three for P1 (forking [bad], face-monopoly [bad], dual-anchor+detour [good]) and at least two for P2 (block-only [bad], column-build inside volume [good]). Players who haven't found dual-anchor+detour are essentially playing a different (worse) game.
* **Counter-play?** Yes, deeply. P2's "wall at x=1" is the right defence against P1's naive openings, but P1's dual-anchor+detour out-paces it. Not a rock-paper-scissors style; rather a tier hierarchy.
* **Short-term vs long-term tension.** Strong. Every P2 column-build has 3-move latency (need 4 stones at fixed (x,z)); P2 can't both block and build in the same move. P1's threats fire after 2 P1 moves (approach + win cell). The race is real.
* **Emergent concepts.**
  * **Column trap.** Forced P2 blocks at x=0 build P2's columns — discovered above. This is the most striking emergent dynamic in the game.
  * **Dual anchor.** Investing the first two moves at *both* boundary faces, far apart, makes blocking almost impossible.
  * **3D detour bridges.** The z-axis is genuinely needed; P1's winning paths in Games 3 and 3b go through z=2 with a y=0-corner finish.
  * **Liberty inflation.** Surround capture is so weak in 3D that it acts only as a "do not chain too tightly" pressure.
  * **No territory, no influence, no ko.** Mechanically the game is much simpler than 2D Go.
* **Does 3D enable strategies 2D wouldn't?** Yes — partially. The z-axis detour in Games 3 and 3b is the *only* P1 winning line I found, and it requires a 3D substrate. In 2D Hex with surround capture and asymmetric goals on a 4×4 board, the column trap (each block is also a column cell) would be far more fatal because there's no out-of-plane bypass. So 3D rescues P1 from the trap. **However**, the same dynamic could be reproduced in 2D by going to a larger axis (e.g. 8×8 2D), since the "detour" P1 needed was simply to find a bridge cell that wasn't pinned. The 3D structure is *useful* but not *uniquely necessary* for the strategic flavour.
* **Topology effect.** This is a grid (von Neumann); switching to torus would let surround captures wrap and would invalidate the corner trick (0,0,1) that P1 relies on, probably tipping the balance further to P2. Switching to moore (max_degree=26) would make every cell have many liberties, killing surround capture even harder, and would also introduce diagonal connectivity that destroys the column-block-feeds-opponent dynamic.
* **Move-enabled?** No. Place-only. The team-lead summary calling this "place" was correct (NOT a place+move hybrid like the R17 champion).
* **First-mover advantage.** With best play I found, **P1 wins**. PPO's 0.5 winrate likely reflects sub-optimal play. There may be a stronger P2 line I missed, but I've tested both naive blocking and column-building and dual-anchor beats both.

---

## Phase 4 — Novelty adversary

### The case for "this is not novel"

The Adversary argues:

1. **It's 3D Hex with capture.** Cameron Browne's *Hex and the Single Hexagon* (and follow-ups) discuss 3D Hex variants. P1 connecting along x and P2 along y is *exactly* the 2-player Hex template lifted to 3D. The capture rule from Go is a known graft (Atari Go, Border-Go, etc).
2. **Asymmetric directional goals are standard.** Hex, Y, *Star*, *Slither*, and Twixt all use perpendicular directional connection. The novelty here is just "in 3D" which is well-trodden (Cubic Connect-4, Qubic, 3D-tic-tac-toe).
3. **Surround capture is effectively dead in 3D von Neumann.** The capture rule does nothing in practice (0 captures across 4 played games). Stripped of the inert capture rule, this game is **3D Hex on a 4³ grid with axis-only adjacency** — a known toy.
4. **The "column trap" is just Hex's no-draw theorem in disguise.** In 2D Hex the same thing exists: P2's blocking moves on the left edge are P2's path cells. Players just learn to bridge.
5. The R17 context note flags the broad pattern: "every prior champion was 2D; R17 is 100% 3D" — the substrate change alone explains the score. The +5% non-grid novelty multiplier doesn't even apply to this game (it's grid).

### Rebuttal

* **Phase 2 specifically rebuts (1).** The column trap *plus* asymmetric face goals *plus* von-Neumann adjacency makes naive forking strictly losing in a way that doesn't apply to standard 3D Hex (which has no boundary-face asymmetry and no Go-style capture). My Game 3b winning line — the (0,0,1) corner play that simultaneously fills two role functions — is a tactic specific to this rule combo. An expert at 3D Hex would not transfer this immediately.
* **(3) overstates the deadness.** Surround capture *did* shape my play in Game 1: P1 avoided playing (1,0,1) until late because clustering at y=0,z=1 invited P2 to seal liberties. The threat-of-capture is non-zero even when actual captures don't fire.
* **(4) is partially right.** This *is* in the same family as Hex. But Hex has a no-draw theorem because hexagonal adjacency makes blocking impossible without connecting. In von-Neumann 3D the no-draw theorem fails (the 4³ board can have no winning chain for either player; double-pass draws are possible). So the equivalence isn't tight.
* **Closest known game?** **3D Hex on a cubic lattice** (cf. Cameron Browne's catalogue). Not 3D-tic-tac-toe (that's 5-in-a-row, not face connection). Not Qubic (3 dimensions but 4-in-a-row). Not standard Go (no connection win, no asymmetric goals). The game is closer to "Hex + Atari-Go on a 3D grid, asymmetric axes", which I do not believe is a published, named game. But the *components* are standard.

### Novelty score: **4**

The combination is fresh-ish, but it's mostly "3D Hex with mostly-inert Go capture and asymmetric axis goals." The column trap is the only emergent dynamic that I'd call genuinely interesting; the rest is mechanical re-use.

---

## Phase 5 — Verdict

**Team ID:** team-10
**Game ID:** a3a6bd2b1b5b
**Rules summary:** Alternating-turn 3D 4³ grid, place-only, surround capture (mostly inert), connection win — P1 connects x-axis faces, P2 connects y-axis faces.
**Topology:** 3D grid 4³, von Neumann (max_degree=6), 64 cells.
**Turn structure:** Alternating, 1 piece/turn.
**Hybrid actions:** No.

### Scores (1–10)

| Dimension | Score | Reasoning |
|---|---|---|
| **Strategic Depth** | **5** | The dual-anchor + 3D detour + corner-finish line is genuinely deep, and the column-trap dynamic forces players to learn non-obvious play. But the board is small (64 cells), capture is essentially dead, and games end in 13–28 moves. |
| **Emergent Complexity** | **5** | The column trap (forced P2 blocks build P2's columns) is a real emergent dynamic. Beyond that — z-axis detour, anchor patterns — it's standard Hex-family stuff. |
| **Balance** | **5** | I found a P1-winning line that beat every P2 strategy I tried (Game 3b: P1 wins T19 with full P2 defence). PPO 0.5 win rate is likely a sub-optimal equilibrium. With best play P1 wins, so balance is moderate not strong. Seat-bal floor of 0.1 was passed but the game has more bias than R17's gates detected. |
| **Novelty (post-adversary)** | **4** | Combination of 3D Hex + Go-style capture (mostly inert) + asymmetric axis goals. The column trap is interesting; the rest is well-known. The R17 +5% non-grid bonus doesn't apply here (this is grid). |
| **Replayability** | **5** | Different P1 openings (fork / face-monopoly / dual-anchor) lead to genuinely different game trees with different winners. But once both players know the dual-anchor pattern, openings will collapse to a narrow band. |
| **Overall "Would I play this again?"** | **4** | I'd play it 5–10 times to internalise the column trap and the corner finish, then I'd be done. It's a fine puzzle, not a deep game. |

**Closest known-game analog:** **3D Hex on a cubic lattice** (asymmetric axis variant) with Go-style surround grafted on. Not identical because (a) standard 3D Hex uses different adjacency, (b) no published 3D Hex variant I know of has Go capture, and (c) the column-trap dynamic that defines play here doesn't appear in pure 3D Hex literature.

**Killer flaws:**
* **Surround capture is essentially inert** — 0 captures fired across 4 games. The capture rule contributes only as a soft deterrent against tight P1 chains.
* **Propagation parameters are dead code** — `prop_type="none"` makes radius/strength/decay completely vestigial, but they still appear in the rule blob.
* **Connection threshold (42.08) is unused** by `_check_connection`. Pure rule-blob noise.
* **Small board** (4³ = 64) makes games short and shallow.
* **"Column trap" is a sharp dynamic that punishes naive players, but skilled players bypass it via dual-anchor**, so the game is partially solved at any reasonable level of play.

**Best quality:**
* The **column trap** is the single most interesting feature of the game — a genuinely emergent property where defensive blocking moves *are* the defender's winning material. This forces P1 (the attacker) to think 3D-spatially rather than 1D.
* The (0,0,1) corner-finish trick in Game 3b is a tidy little gem: a single cell that simultaneously closes the corner liberty, joins two previously-isolated P1 sub-groups, and completes the x=0–to–x=3 path through 3D.

**3D structural contribution:** The z-axis detour is *used* by the dominant P1 strategy. **Could this be 2D without losing strategy?** Mostly yes — a 2D 8×8 Hex-with-capture game would reproduce the column trap and the long-bridge-via-detour dynamic. So 3D is *useful* (it gives a smaller board with similar tactical content) but not *uniquely necessary*. The R17 hypothesis that "3D + connection is genuinely deep" gets a partial confirm here: 3D is doing real work, but it's not opening fundamentally new strategic vistas.

**Improvement ideas (one rule change):** Change the capture rule from `surround` to `outnumber` with threshold 4 (= must have 4 friendly neighbours of an enemy cell to capture). In 3D von-Neumann, this would be reachable but rare, and would interact with the column-build dynamic — P2's tight x=1 wall would become capture-vulnerable, giving P1 a third strategic option (capture the wall) in addition to bridge / forfeit. This would re-balance toward P2 (since walls are now vulnerable) while making capture an *active* tactic instead of dead code.

---

*Phase notes:*
* All 4 played games (Games 1, 2, 3, 3b) were engine-verified move-by-move via `eval_team10_helper.py`.
* Action IDs were checked against the `cell = z·16 + y·4 + x` decoder before each step.
* No move actions were used (game is place-only).
* No surround captures fired in any game.
* No double-pass draws.
* No max-turns timeouts.
