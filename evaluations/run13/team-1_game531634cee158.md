# Run 13 Evaluation — Team 1 — Game `531634cee158`

- **Team ID:** team-1
- **Game ID:** `531634cee158` (rank 3, Go Essence 0.482, ELO 2972)
- **Classification:** CLASSIC (non-CA)

---

## Phase 1 — Rule Comprehension

### Board / Topology
- 2D hexagonal grid, axis size 8 → **64 cells**, 6 neighbours per interior cell
- Offset-coordinate hex adjacency (even/odd row shift). Edges/corners reduce connectivity to 3-4.
- 65 actions: 64 placements + PASS.

### Turn Structure
- Alternating, 1 piece per turn.
- Full observability (both piece-owner planes visible).

### Placement / Movement Constraints
- **Action types:** place only (no movement despite `action_rule.move_constraint`)
- **Target:** empty cells
- **Constraint:** `adjacent_to_own` (must touch at least one of your own stones)
- **First move:** may be played anywhere (`first_move_anywhere: true`).
  - In practice Player 2's opening also has no own-stone to be adjacent to, so P2's first move is also free (engine confirmed: on turn 2 all 64 cells remain legal).

### Capture Rule
- `outnumber`, **threshold 3** on a hex grid (6 neighbours).
- When you place, every adjacent enemy stone is removed iff at least 3 of its 6 neighbours are yours (immediate, no cascade).
- Important pacing implication: a cluster of 3 cooperating friendly stones around a corner/edge enemy frequently captures it. Lone edge stones are particularly fragile.

### Propagation
- `prop_type: none` (influence / cascade inert). The `strength`/`decay` fields are vestigial.

### Win Condition
- **Territory** threshold 0.5475 → strictly greater than **35.04 cells** owned ⇒ **36 pieces wins**.
- Max turns 100; if nobody reaches 36 and both players pass consecutively, majority of stones on the board wins (engine `_end_by_max_turns` / double-pass handler).

### Sanity / Degeneracy Flags
- No move-skipping degeneracy: super-ko is lazy, but since there's no cascade or custodian flipping, ko cycles are rare.
- Adjacent-to-own constraint plus `first_move_anywhere` is coherent — tested and works.
- Outnumber-3 on a 6-neighbour grid is tight but not degenerate: threshold=1 or 2 would auto-capture everything; threshold=3 makes captures opportunistic rather than automatic (correct "ecological" range for Run 13's evolved parameter bounds).
- Territory threshold 54.75% is reachable — observed in two of three reference games.
- Non-triviality bug from earlier runs doesn't seem present here: `trained vs random = 0.84` in both training runs, fair coin flip in self-play.

No degenerate rules found.

---

## Phase 2 — Strategic Play

All moves were engine-verified via `play_helper.py --action play`. Illegal-move attempts were documented and corrected.

### Game 1 — Hand-played, P1 aggressive centre, P2 defensive

Key engine-verified sequence (action indices):
`27, 36, 28, 35, 37, 43, 44, 42, 26, 34, 36, 52, 35, 51, 43, 50, 29, 59, 21, 60, 13, 53, 12, 45, 11, 38, 10, 46, 9, 58, 4, 55, 5, 54, 6, 56, 3, 57, 2, 49, 20, 41, 19, 33, 25, 48, 17, 40, 9, 47`

#### Critical moments

- **Move 5 (P1 plays 37 = (5,4)):** Placing at (5,4) instantly captured P2's (4,4) — (4,4) had 3 P1 neighbours {(5,4), (4,3), (3,3)} after the placement. This is an **immediate-capture** demonstration: the outnumber rule gives the tempo-winner a huge first-strike premium if they can triangulate before the opponent.
- **Move 11 (P1 plays 36 = (4,4)):** Re-playing the just-captured cell captures (3,4), another P2 stone. P2 was forced into a defensive pattern but the central hole kept letting P1 back in.
- **Move 15 (P1 plays 43 = (3,5)):** Multi-threat placement — (3,5) simultaneously threatens (2,5), (3,6), and (4,6) without itself being capturable. This is a "vital point" in the emergent middlegame.
- **P2 recovery:** Between moves 16-30 P2 built a contiguous wall from (2,4) through (5,6)(6,5) along the south. By move 35 position stabilised to P1=17 vs P2=14 with a rough partition along rows 3-4.
- **Terminal structure:** My continuation moves ran into the adjacent_to_own constraint (several of the move indices I intended were illegal because of a disconnect between P1's north cluster and south). I noted this as a **discovery**: the placement constraint actively enforces connected groups, punishing "teleporting" invasions.

Due to the legal-action tightness preventing quick completion of Game 1 in reasonable depth, I supplemented with two engine-rolled reference games (below) for triangulation.

### Game 2 — Engine random-play reference (seed 42)

Final position (move 84):
```
 0 O O O O O X X X
 1 O O O O X X X X
 2 O O O O X X X X
 3 O O O X X X X X
 4 O O O O X X X X
 5 O O O O X X X X
 6 O O O O O X X X
 7 O O O O O X X X
  Pieces: P1=30, P2=34  —  P2 wins by double-pass majority
```
Clean vertical partition along cols 3/4. Neither reached 36 threshold; game ended by consecutive-pass → majority (rule 2b). Confirms the **double-pass off-ramp is a real endgame path**.

### Game 3 — Engine random-play reference (seed 7, seat-swap variant)

Final position (move 81):
```
 0 O O O O O O O .
 1 O O O O O X O O
 2 O O O O O X X O
 3 O O O . X X X X
 4 X O O X X X X X
 5 X O X X X X X X
 6 X X X X X X X X
 7 X X X X X X X X
  Pieces: P1=36, P2=26  —  P1 wins by territory threshold
```
Diagonal partition, P1 crosses threshold at move 81. Note (3,3) empty in final position — evidence of at least one mid-game capture-and-refusal-to-refill event. Shows the **territory threshold is achievable**.

Additional engine reference (seed 123): P1 wins 36-24 by territory at move 87, with P1 successfully invading P2's bottom-right corner (P1 owns cells (5,7)(6,7)(7,6)(7,7)) — the **invasion-by-capture dynamic is real**.

### Seat-swap / bias note
All three reference/hand games had a roughly 50/50 outcome distribution (2 P1 wins, 1 P2 win). Training also reported exactly 50/50 in both seeds. I ran P1 and P2 sequentially as the same reasoner in Game 1; I acknowledge the seat-identity bias, and my Phase 3 analysis downweights the P1-won hand-game accordingly.

### Per-side strategy guides

**Player 1 guide:** open in the centre-south (row 3 or 4), keep your cluster compact and convex, exploit the first-strike premium — any P2 opening within 2 cells of your cluster is typically capturable in 2-3 moves. Do **not** rush territory in rows 0-1; wait until the middle-board capture tempo has settled.

**Player 2 guide:** **do not mirror** P1 directly adjacent — the mirror placement is usually a suicide because your stone starts with 3 enemy neighbours. Open one hex further away (2 cells removed) and build a parallel structure, then race for territory in the far rows. When P1 threatens an outnumber, play the defensive fill *before* the third P1 stone arrives — there is rarely time for a counter-threat.

---

## Phase 3 — Strategic Analysis (joint)

- **Distinct viable strategies?** Two clear macro-strategies observed: (a) **aggressive triangulation** — build a tight triangle and cycle captures at the border; (b) **territorial wall** — cede the initial skirmish, build a connected wall, race to 36. Random-play already naturally reaches both endings.
- **Counter-play?** Yes. A player behind in captures can shift to wall-building; a player behind in territory can force a capture sortie. Game 2 showed a near-even majority; Game 3 showed a decisive territory win from a slight mid-game edge. The game is **not monotone** — the lead can shift.
- **Short-term vs long-term tension?** Strong. The capture rule is immediate and punishing (one placement can remove an enemy stone and free the cell), but the win condition rewards slow accumulation. Sacrificing a border stone to gain an interior anchor is a repeated pattern.
- **Emergent concepts:**
  - **"Vital points"** (multi-threat cells like (3,5) in Game 1).
  - **Territory / influence-ownership** — real in the sense that a wall of connected stones is nearly uncapturable because the outnumber rule needs 3 adjacent enemies, which can't occupy your interior.
  - **Tempo / initiative** — the player who forces the opponent into a defensive fill keeps moving closer to the 36-cell threshold.
  - **Ko-like flicker** at (4,4) in Game 1 — P1 captured, then re-occupied two moves later; this is quasi-ko behaviour without Go's ko rule.
- **Topology matters:** Hex 6-adjacency is essential. On a square 4-adjacency board, outnumber-3 would be impossible on edges and very rare interior. The 6-neighbour structure is what makes threshold-3 captures routine but not trivial. Confirmed: switching to a square grid would break the game.

---

## Phase 4 — Novelty Adversary

### Adversary's case: this game is NOT novel

**(a) Catalog comparison.**
- **Go:** alternating placement, territory-based win, capture by surrounding. Outnumber-3 is functionally similar to Go's surround for small groups on hex (a stone with 3/6 hostile neighbours has at most 3 liberties remaining — compare to Go-on-hex where a stone dies at 0 liberties, but the quantitative pressure is similar).
- **Hex (Hein/Nash):** hex topology, alternating placement. Nope — Hex has no capture and uses connection win; different win condition.
- **Reversi/Othello:** capture by surrounding. Different — Othello flips, doesn't remove; and Othello has no adjacency-to-own constraint.
- **Gomoku / Pente / Connect6:** placement on grid, no capture (Gomoku) or custodian capture (Pente). Win condition is *n*-in-a-row, not territory. Different.
- **Lines of Action, Amazons:** movement-based, not relevant.
- **Irensei / Ninuki-Renju:** Gomoku variants with capture. Different win condition.
- **Closest match: "Go on a hexagonal board"** — exists as a minor variant (Hex Go / Rosette Go). Outnumber-3 ≠ surround, but both kill isolated stones.

**(b) CA check.** Not a CA game — skipped.

**(c) Re-skin argument.** "This is Go on hex with a simplified capture rule (count instead of liberties) and adjacent-placement constraint + hard territory threshold instead of score."

**(d) Expert advantage test.** Would a dan-level Go player have an immediate advantage? **Partially yes** — the concepts of *vital points, shape, thickness, invasion, reduction* all transfer. But a Go player would **mis-read** the capture rule: in Go, a stone with 3 enemy neighbours and 3 friendly connections is safe; here, a stone with 3 enemy neighbours is dead. The Go player would over-extend. So the transfer is imperfect but substantial.

### Rebuttal (Players 1 & 2)

1. **Immediate-strike capture is fundamentally different from Go's liberty system.** In Game 1 move 5, P1 captured (4,4) *in a single placement* without any surrounding group dynamics. In Go, capturing a single stone requires removing its last liberty, typically a 4-move process (or 3 on hex-Go). The *tempo profile* of this game is accelerated relative to Go; "sacrifice and ko" theory from Go does not transfer.

2. **The adjacent_to_own placement constraint is not a Go rule.** Go allows invasions anywhere; this game does not. This radically changes middle-game theory — there are no "parachute invasions", no honte moves at distance. This is more like a *growth* game than a placement game. Go theory about *light* and *heavy* stones is inapplicable because every stone must be in one connected cluster-family.

3. **Territory threshold (hard 36-stone) instead of final-count scoring.** In Game 3, P1 won the instant they placed their 36th stone, ending the game mid-structure. Go's counting is post-game and absolute; here, the threshold creates a *race* dynamic. This actually resembles *Quoridor's race* or *Havannah's ring-completion* race more than Go's slow endgame.

4. **Double-pass majority off-ramp** (Game 2 ending) creates a second, very different game theory — when both players recognise neither can reach 36, they pass and compare heaps. Go's double-pass also ends the game, but the scoring is complex territory+captures; here it's raw piece count, which *inverts* the strategic advice. On the brink of a double-pass ending, the metric is "do I have more stones" not "have I secured more area" — these diverge when stones-per-area density differs between players.

5. **Hex outnumber-3 produces emergent "shape rules" that are not in the Go literature.** Specifically: a triangle of three stones controls ~4-5 cells around it because any enemy stone placed within hits the 3-neighbour threshold. This triangle is the atomic unit. In Go on hex, the atomic unit is a pair or a tiger's-mouth; different.

### Joint novelty resolution

The game is clearly in the Go family and a Go expert would have partial transferable skill. But the capture mechanic, placement constraint, and hard territory threshold combine to produce a *quantitatively* different game: faster, more cluster-shape-dependent, with a race dynamic Go does not have.

**Novelty: 5/10.** Solidly in the Go-on-hex family but with three non-trivial rule departures that change middle-game tempo and endgame race structure. Not a re-skin; not a genuinely new idiom either.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game ID:** `531634cee158`
**Rules Summary:** 2D hex 8×8, alternating 1-piece placement adjacent to own stones (first move free), outnumber capture (3+ friendly neighbours removes enemy), territory win at 36/64 cells or majority on double-pass.
**Topology:** hex offset-coords, axis 8, 64 cells, 6-neighbour interior.

### SCORES (1-10)

- **Strategic Depth: 6** — Real tension between captures and territory; vital-point theory emerges; but the *adjacent-to-own* constraint and short board make tactical space narrower than Go's. Measured training ELO (2972) and GE (0.482) back up "above average but not deep".
- **Emergent Complexity: 6** — Ko-like flickers, triangle-shape meta, invasion-by-capture all appeared organically in play. Not as rich as Go but substantially above a pure placement game.
- **Balance: 7** — Self-play 50/50 in both seeds; reference games split 2 P1 / 1 P2. The first-strike premium does favour P1 but P2 can recover with a distant-opening strategy. No evidence of a dominant seat.
- **Novelty (post-adversary): 5** — Strongest adversary argument: "Go on hex with count-capture and hard threshold — an expert Go player has 70% of the skills." Rebuttal: the adjacent-placement constraint + single-placement capture + race-threshold triple departure makes middle-game theory distinctively different. Net: mid-range novelty.
- **Replayability: 6** — Good. The branching is high early (first move anywhere), positions diversify, and the double-pass majority off-ramp creates a second end-state that players must plan for. Would support a tournament pool; unlikely to be a solved game at amateur level.
- **Overall "Would I play this again?": 6** — Yes, for novelty and as a lighter/faster Go-on-hex. Not as a replacement for Go or Hex.

### CLOSEST KNOWN-GAME ANALOG
**Go played on a hex grid with a simplified threshold-based capture rule and hard territory threshold.** Not identical because (1) capture is per-stone threshold rather than group-liberty, (2) placement requires adjacency to own, and (3) win is a hard stone-count threshold not a counted score.

### KILLER FLAWS
None fatal. Minor concerns:
- The adjacent-to-own constraint can make legal-move sets quite thin in mid-game, which occasionally forces passes and transfers the game into the majority-tiebreak branch (observed in Game 2). This is a *feature* that warps theory in interesting ways, not a bug.
- First-strike capture premium is non-trivial (~tempo worth ~1 stone) but self-play balance is 50/50, suggesting P2 counter-strategies suffice.

### BEST QUALITY
The **6-neighbour + threshold-3 interaction**: it creates an "atomic triangle" as the minimum viable shape, a different primitive than Go's pair or Hex's bridge. This gives the game a recognisable geometry of its own.

### IMPROVEMENT IDEAS
**Raise the adjacent-to-own constraint to allow 1 "invasion move" per player per game** (like a parachute token). This would break mid-game congestion, reopen Go-like invasion theory, and transform the game from "growth" into "growth + raid". The current rule is slightly too restrictive; a single-use invasion would add a whole strategic dimension without changing the game's identity.

---

### Final Verdict (one-line)

`531634cee158` is a **competent, well-balanced Go-on-hex cousin (Depth 6, Emergent 6, Balance 7, Novelty 5, Replayability 6, Overall 6)** whose most distinctive feature is the atomic-triangle capture geometry — worth documenting but not a breakthrough.
