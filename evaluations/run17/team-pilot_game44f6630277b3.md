# R17 Evaluation — `team-pilot` × game `44f6630277b3`

Pilot evaluation for Run 17 strategic-quality protocol.

- **Team ID**: `team-pilot`
- **Game ID**: `44f6630277b3`
- **GE**: 0.3773 / **ELO**: 2627.2 / **Generation**: 11
- **Headline R17 claim under test**: 3D + custodian + connection + place+move hybrid is a *genuinely novel* combination, not a topology-artifact.

---

## Phase 1 — Rule Comprehension

**Board structure.** 4×4×4 = 64 cells, 3D grid topology, 6-neighbor von Neumann adjacency (face-only; no diagonals). No wraparound (boundaries are hard walls — both for movement and for custodian-capture walks). Cell index encoding: `idx = z*16 + y*4 + x`. Action space: `64 (place) + 1 (pass) + 64*6 (move) = 449`.

**Turn structure.** Alternating, 1 piece per turn. P1 moves first. Two consecutive passes ⇒ draw.

**Action types: place + move (hybrid).**
- **Place**: drop a stone on any empty cell (`placement_rule.constraint = "anywhere"`, `target = "empty"`, `first_move_anywhere = True`).
- **Move**: relocate one of your stones to a face-adjacent **empty** cell (`move_constraint = "adjacent_empty"`). Target must be empty — no movement-based displacement of enemy stones. Movement *does* trigger custodian capture at the destination.

**Capture: custodian, threshold=1 (Othello-style; threshold field is inert for custodian).** When you place (or move-arrive at) a stone, the engine walks along each of the 6 axis directions; consecutive enemy stones encountered are queued; if the walk terminates on a friendly stone (before hitting the board edge or an empty cell), the queued enemies all flip to your color. Walks **do not** wrap (it's grid topology; documented quirk for torus only). In 3D this means a single placement can flip stones along the x-, y-, **or** z-axis, and a placement at the right cell can trigger captures on multiple axes simultaneously.

**Propagation: none.** `prop_type = "none"` — `radius`, `strength`, `decay` fields are stored but unused. `engine.board_values` plays no role.

**Win condition: connection (asymmetric).**
- **P1** must form a 6-connected path of own stones from the `z=0` face to the `z=3` face (`target_dimension = 2`).
- **P2** must form a 6-connected path of own stones from the `x=0` face to the `x=3` face (`target_dimension_p2 = 0`).
- The two players' goal axes are **perpendicular**, so their routes can intersect at most at one (x, y, z) cell on any given plane.
- `threshold = 0.5` is stored but `_check_connection` ignores it (BFS connectivity only; threshold is not used).
- `max_turns = 86`. Double-pass ⇒ draw; max-turns triggers piece-count majority.

**Cellular automaton: none** (classic mechanics, capture+propagation path).

**Degeneracy flags raised:**
1. **Movement is vestigial in early/midgame.** Movement requires existing stones, but the win is reachable in ≤9 moves with optimal placement-only play. None of the 3 games used a single move action.
2. **Boundary anchors are flank-immune along their boundary axis.** A P1 stone at z=0 (on the lower face) has no z=−1 cell, so it cannot be z-axis flanked — by symmetry the z=3 face is the same. This makes "anchor your column at both faces and only worry about middle" a structural invariant.
3. **Asymmetric win axes** (P1 z-axis, P2 x-axis) means P1 and P2 have *different* shortest-path geometries; it does not symmetrize via a coordinate relabel because the alternation order is fixed (P1 first).
4. **Capture threshold = 1 is inert** for custodian (engine never reads the threshold field in `_capture_custodian`). Threshold is a "rule complexity" generator artifact.

---

## Phase 2 — Strategic Play

All moves engine-verified via `eval_pilot_helper.py` (computes captures, piece counts, decoded coords). One Phase-2 indexing-typo error caught and corrected mid-game (see "Quality issue" at end of this section).

### Game 1 — P1 brain offensive, P2 brain "block-the-middle" defense

| # | Player | Action | Coord | Reasoning |
|---|--------|--------|-------|-----------|
| 1 | P1 | 5 | (1,1,0) | Anchor column at xy=(1,1) on z=0 face. Boundary makes flank-safe along z. |
| 2 | P2 | 37 | (1,1,2) | Bisect P1's column AND claim a y=1, z=2 row cell. Dual-purpose. |
| 3 | P1 | 21 | (1,1,1) | **Set up forced capture**: if I play (1,1,3) next, the line (1,1,1)P1—(1,1,2)P2—(1,1,3)P1 z-flanks → flips (1,1,2). |
| 4 | P2 | 53 | (1,1,3) | Forced defense (any other move loses to the (1,1,3) capture-and-win). |
| 5 | P1 | 36 | (0,1,2) | Multi-threat: occupies P2's row x=0 anchor, AND sets up x-flank capture of (1,1,2) via future (2,1,2). |
| 6 | P2 | 38 | (2,1,2) | Friendly-cap: blocks the x-flank attack and extends row to 2/4. |
| 7 | P1 | 39 | (3,1,2) | **DOUBLE CUSTODIAN CAPTURE.** Walk from (3,1,2) along −x: (2,1,2)P2 collected, (1,1,2)P2 collected, terminates at (0,1,2)P1 → both P2 stones flip. |
| 8 | P2 | 52 | (0,1,3) | Blocks one of three winning anchors at z=3. P2 has no winning move. |
| 9 | P1 | 55 | (3,1,3) | **WIN.** Chain (1,1,0)→(1,1,1)→(1,1,2)→(2,1,2)→(3,1,2)→(3,1,3) connects z=0 to z=3. |

**Result**: P1 win, 9 moves, 0 movement actions used.

**Reflections.**
- **P1**: The (3,1,2) double-capture was the strategic core. Custodian along x with two consecutive P2 stones (1,1,2)+(2,1,2) bracketed against my pre-placed (0,1,2) cleared two stones AND simultaneously placed me on the row at z=2 with three connected P1 cells. Surprised by how cheap the capture geometry was — once P2 plays a "self-bracketing" pair, a single P1 placement at the right boundary cell collapses the position.
- **P2**: I should not have played (2,1,2) at move 6 — that *cemented* the (1,1,2)+(2,1,2) capturable-pair. Better was to capture P1's (1,1,1) via x-flank setup (placing (0,1,1) and later (2,1,1)) — but that's two turns, and P1's threat is one-turn, so I was already losing tempo. Real lesson: do not play (1,1,2) at move 2; this handed P1 a capture target.

### Game 2 — P2 brain attempts "block z=3 boundary then y-flank attack"

| # | Player | Action | Coord | Reasoning |
|---|--------|--------|-------|-----------|
| 1 | P1 | 5 | (1,1,0) | Same opening. |
| 2 | P2 | 53 | (1,1,3) | Block z=3 boundary anchor instead of mid-column. Avoids the game-1 trap. |
| 3 | P1 | 21 | (1,1,1) | Continue column. |
| 4 | P2 | 41 | (1,2,2) | Y-flank setup on (1,1,2) — if I play (1,0,2) later AND P1 fills (1,1,2), P1 stone gets captured. Doubles as a y=2,z=2 row seed. |
| 5 | P1 | 20 | (0,1,1) | **Avoid the (1,1,2) trap.** Extend chain x-laterally: (1,1,1)–(0,1,1). Sets up alternate column at xy=(0,1). |
| 6 | P2 | 36 | (0,1,2) | Block P1's left-side z=3 route, plant x=0 row anchor. |
| 7 | P1 | 52 | (0,1,3) | **WIN via z-flank capture.** Walk from (0,1,3) along −z: (0,1,2)P2 collected, terminates at (0,1,1)P1 → (0,1,2) flips to P1. Chain (1,1,0)→(1,1,1)→(0,1,1)→(0,1,2)→(0,1,3) connects z=0 to z=3. |

**Result**: P1 win, 7 moves, 0 movement actions used.

**Reflections.**
- **P1**: Avoiding the central (1,1,2) trap and pivoting x-lateral via (0,1,1) found a much faster winning line. The z-flank capture at (0,1,3) is symmetric to the game-1 x-flank capture: any P2 stone bracketed between two P1 stones along an axis is single-move-flippable, and on the connection-completing move both happen at once.
- **P2**: My (1,2,2) flank-setup was a tempo waste. P1 simply went around it. I should have either (a) played pure defense at (0,1,1) immediately to seal the x=0 column, or (b) attempted to capture (1,1,1) via x-flank setup. Both still likely lose.

### Game 3 — Seat-swap discipline. P2 plays the "boundary-row trap" — place at x=0 and x=3 of the row to set up bracket-traps on any P1 mid-row placement.

| # | Player | Action | Coord | Reasoning |
|---|--------|--------|-------|-----------|
| 1 | P1 | 5 | (1,1,0) | Same anchor. |
| 2 | P2 | 36 | (0,1,2) | x=0 row anchor. **Trap setup**: if P1 plays (1,1,2) or (2,1,2), P2 places the other and brackets. |
| 3 | P1 | 21 | (1,1,1) | Continue column, avoiding row trap. |
| 4 | P2 | 39 | (3,1,2) | x=3 row anchor. Trap fully armed: any P1 stone at (1,1,2) or (2,1,2) gets bracket-flipped on P2's next turn. |
| 5 | P1 | 52 | (0,1,3) | **Counter-attack**: z-flank capture setup on (0,1,2). Anchors z=3 face on x=0 column. |
| 6 | P2 | 37 | (1,1,2) | Race to complete row (chooses speed over defense). Walk from (1,1,2) doesn't capture — needs (1,1,3) to bracket along z, but (1,1,3) is empty so walk just terminates at OOB. |
| 7 | P1 | 20 | (0,1,1) | **WIN via z-flank capture.** Walk from (0,1,1) along +z: (0,1,2)P2 collected, terminates at (0,1,3)P1 → (0,1,2) flips. Chain (1,1,0)→(1,1,1)→(0,1,1)→(0,1,2)→(0,1,3) connects z=0 to z=3. |

**Result**: P1 win, 7 moves, 0 movement actions used.

**Reflections.**
- **P1 (seat-swap)**: Even with P2 playing the strongest defensive idea found across all 3 games (boundary-row trap), P1 has a forced 7-move win via z-flank counter-capture at the column boundary. The (0,1,2) blocker that P2 *needs* on the x=0 face is also the cell P1 most wants to capture for column completion — giving the cell *to* P2 actively helps P1.
- **P2 (seat-swap)**: I considered defending with (0,1,1) at move 6 instead of racing with (1,1,2). That *prevents* the move-7 z-flank but loses by move 9 to a different sequence: P1 plays (3,1,3), P2 forced to cover (3,1,1), P1 plays (3,1,0) and the line (3,1,0)P1—(3,1,1)P2—(3,1,2)P2—(3,1,3)P1 produces a **double-capture column-completion** along z. So defending one boundary anchor merely shifts the capture sequence to the other end. Both routes converge to P1 winning by capture-completion; the only question is move-7 vs move-9.

### Strategy guides

**P1 strategy guide** (canonical winning recipe):
1. **Open at a boundary z=0 cell that's neighbor-rich**, e.g. (1,1,0). The face-anchored stone is z-flank-immune and has 4 friendlier neighbors than corners.
2. **On move 3, fork**: play (1,1,1) (the cell directly above the z=0 anchor) — this *threatens* a single-move z-flank capture-and-win at (1,1,3) if P2 hasn't blocked.
3. **On move 5, plant an x=0 row-blocker / capture-setup**, e.g. (0,1,2). One stone, three jobs: blocks P2's row, sets up x-flank capture of any P2 stone at (1,1,2), gives you an alt-column at xy=(0,1).
4. **Look for boundary-anchored capture sequences.** Any line of 1–3 P2 stones along an axis with empty boundary cells can be flipped by placing your own stone at the empty boundary and the inner-side flank cell. Pick the one that *completes* connection on the same move.
5. **Movement is unused.** Don't waste a turn on it; placement+capture wins faster than 9 moves.

**P2 strategy guide** (best-found defenses; all losing within 7–9 moves):
1. **Never play (1,1,2) (the canonical column-bisector).** It cements the (1,1,2)+anything pair into a custodian-flippable line.
2. **Block z=3 boundary anchor first** (e.g. (1,1,3)) — denies P1 the cheapest column route. But P1 simply x- or y-detours and finds a flank-capture win in 5–7 P1 placements.
3. **The boundary-row trap** (occupy x=0 and x=3 of your goal row, force P1 to walk into a bracket) is the most coherent attacking idea, but P1 counter-flanks faster than the trap fires.
4. **Building the row independent of P1's column is too slow** — P1 wins at move 7 in pure-race; P2 cannot complete 4 connected stones with x=0 and x=3 anchors before P1's column finishes (or before a flank capture lands).
5. **No defense found; structural P1 advantage holds across both seats.**

### Phase-2 quality issue (transparent disclosure)

On the first attempt at Game 1, I miscomputed a placement action ID: I intended to play (0,1,2) but used `action 20`, which decodes to (0,1,1). The error was caught after observing the next-state board render did not show a stone at the intended cell. The spec explicitly warned about this (`"for 3D it's z*axis^2 + y*axis + x. Typos are easy — double-check"`). **The warning is justified — this is a real prompt-quality risk for downstream teams.** Recommendation: future teams should adopt a discipline of computing the action ID explicitly via `z*16 + y*4 + x`, then immediately verifying the decoded coordinate from the engine output before committing the move. Game 1 was restarted from move 1 once the error was caught and the rest of the evaluation is clean.

---

## Phase 3 — Strategic Analysis (joint)

**Are there distinct viable strategies?** Substantively no for P2; somewhat yes for P1.
- For **P1**: there are 2–3 winning strategy families (corner-column, edge-column with x-flank counter-attack, edge-column with z-flank counter-attack). All converge in ≤9 moves on a 4³ board. Different opening cells (1,1,0), (2,2,0), (1,2,0) each have similar tempo.
- For **P2**: every defense we tried — middle-column block, top-boundary block, boundary-row trap, race-strategy, y-flank attack — loses in 7–9 moves. We did not find a viable winning strategy.

**Meaningful counter-play?** Tactically yes (P2 can choose *which* losing line they prefer, and the 7- vs 9-move difference is real). Strategically no — P2's goal axis (x) is *forced through cells P1 also wants* (any z=2 row crosses through cells P1 needs for column-routing detours), and the custodian rule punishes whichever side commits stones to the contested middle layer first. P1 commits second (P1's column has multiple z-layers to spread risk; P2's row is on a single z-layer and is therefore spatially compact and capture-vulnerable).

**Short-term vs long-term tension?** Mostly short-term. The 7–9 move horizon doesn't allow long-term planning to express itself. With max_turns=86 a longer game would be possible but would require both players to play much weaker openings.

**Emergent concepts.**
- **Capture-trap.** A P1 stone played as a "row-stopper" doubles as a flank pre-stone. The boundary cell + interior cell pattern creates 2-stone capture chains. This is a real emergent tactic (not a Go or Othello pattern, exactly — it's the **connection-driven custodian** combo).
- **Ko-like positions did not appear** in any game. The 7–9 move length is too short for repetition to matter.
- **3D path-routing**: did not contribute. All 3 winning paths used a single z-column (with at most one 1-cell x-detour). The 3rd dimension was exploited in only 1 game (the double-capture on move 7 in Game 1 used z, x adjacencies in close coordination, but the win still resolved on a near-2D structure).
- **Tempo / initiative**: dominant. P1's first-move advantage compounds with capture asymmetry.

**Does 3D actually contribute depth?** **Mostly no.** Empirically, all 3 winning paths used essentially a 2D structure (a single column at xy=(1,1) plus at most a 1-cell sideways branch). On a 2D 4×4 grid with the same rules and connection-axis assignments, the same patterns would play out — the third dimension was *available* but rarely *necessary*. The one exception is the move-7 double-capture in Game 1: the (3,1,2) placement chained through 3 cells along x, and that path was reachable because z=2 layer had enough open cells for stones to coexist. On a 2D 4×4 board, that 3-cell capture line would still work along a row. So even the most interesting move can be flattened.

**Topology change effect (counterfactual).** Replacing 3D grid with 2D 4×4 grid: P1's win-axis is reduced from 4 cells to 4 cells (same). Custodian flank patterns are simpler (4 axis directions instead of 6). The capture geometry tightens but the *winning recipe* survives. Replacing with hex topology: custodian capture is *skipped* on hex per the engine code (`_capture_custodian` exits early if topology not in {grid, torus, sierpinski, holes}), so the game would lose its core mechanic. Replacing with torus: custodian walks are still bounded by axis_size (no wrap during capture, per the engine quirk note), but propagation/connection wrap — this would change tactics significantly but in a way that probably *favors* P2 (eliminates boundary-anchor immunity). Replacing with moore: custodian is also skipped (only grid/torus/sierpinski/holes use it). The game's identity is "3D + grid + custodian" specifically; changing topology destroys it.

**Move actions: vestigial.** Across **3 games and 23 total turns, zero move actions were used**. The action space includes 384 move actions (>85% of the action space), all of which were either illegal (no source stone) or strictly dominated by a placement. Empirically, movement contributes nothing to the game's strategic surface in this game. The training stats from the database (3 PPO runs, agents reach 66–96% winrate vs random, learning curves rising 0.06→0.84) suggest the trained agents *do* discover meaningful play, but if they used moves, our 3 games at the human-strategic level did not need them.

**First-mover advantage**: severe. **P1 won 3/3 games**, including game 3 with deliberate P2 best-effort defense. With only 3 games we cannot say P1 wins always with statistical confidence, but the structural arguments (boundary-anchor immunity along the goal axis is asymmetrically available to whoever moves first; alternation tempo) plus the consistency of the result give a strong qualitative reading. **The R17 seat-balance gate (seat_bal ≥ 0.1, with hard zero below) cannot have detected this** — the 544/544 tournament wins of this game (from the run logs) suggest the trained agents found the same skew. The seat-balance gate evidently passed because P1 and P2 trained agents both had ~0.5 final winrate against each *other in the same game* (which is engine-symmetric by training), but at the strategic-quality level the seat asymmetry is severe.

---

## Phase 4 — Novelty Adversary

**Adversary's case (game is NOT novel):**

(a) **Re-skin of 3D Hex / Qubic.** The connection-win mechanic is straight 3D Hex (or 3D-Y on a degenerate substrate). 3D Hex / Qubic / 3D Tic-Tac-Toe / Connect-4-3D are all "connect opposite faces or rows in 3D" games. Just rebrand "3D Hex with capture" and the analogy is tight.

(b) **Re-skin of Reversi/Othello in 3D with a connection objective.** Custodian capture is *the* defining mechanic of Othello. Adding a 3D dimension and a "connect faces" win condition just gives "3D Othello where instead of disc-count majority you need a connected path." This composition is mechanical, not creative.

(c) **3D Go variants exist.** "3D Go" (occasionally proposed in academic papers and recreational design) extends Go to 3D with various topology choices. Custodian capture is the *natural* lift of Go's surround-capture to a different rule set; if you instead used surround capture in 3D you'd have 3D Go proper. This game is "3D Go with custodian instead of surround and connection instead of territory" — three rule swaps from a known game.

(d) **The hybrid place+move action is decorative.** In our 3 games, 0 move actions were used. The "novelty" of mobile stones doesn't materialize in actual play. An expert from 3D Hex or 3D Othello would transfer immediately and never even notice the move action exists.

(e) **The "3D-shift basin" (R17 hypothesis) is actually substrate-effect, not concept-effect.** The fitness function rewards *variability of play* and *non-trivial games*, both of which are easier in higher-dimensional spaces because there are more cells. A 3D Hex variant would score similarly. The "novel combination" is just the cross product of three known mechanics; the substrate did the heavy lifting.

(f) **Verdict from adversary**: novelty score 3 — "3D Hex with Othello capture" — direct analog from any 3D abstract-strategy fan.

---

**Rebuttal (P1 + P2 jointly):**

1. **The combination is genuinely uncommon.** Searching the abstract-game design literature, 3D Hex variants are documented (Cameron Browne and others have written about 3D connection games), but **3D Hex specifically with custodian capture as the perturbation rule** is not a published variant we could locate. The closest is *Connect6*, which is in 2D and has no capture. Reversi-with-connection-objective has been *proposed* (e.g., in papers on rule-induction for novel games) but not as a 3D variant with asymmetric goal axes. So the *exact* tuple (3D, grid, custodian, connection-with-asymmetric-goal-axes, alternating, hybrid actions) is not in any catalog we could confirm. Novelty score should sit above "obvious recombination" (3) but below "wholly emergent dynamics" (8).

2. **Phase-2 specific counter-evidence to (a)**: The double-capture move in Game 1 (move 7, the (3,1,2) placement that flips two stones in one shot AND completes a 3-cell P1 chain along x at z=2 toward the win condition) is a class of play that **3D Hex does not have** (Hex has no capture), **3D Tic-Tac-Toe does not have** (TTT has no capture), and **Othello does not have** (Othello has no connection objective; capture is the win condition itself). The specific tactical motif "use a custodian capture *as* the connection-completion move" is a real cross-mechanic property of *this combination*. An expert from any of those 3 ancestor games would transfer most of their intuition but would *miss* the capture-as-completion line in their first plays.

3. **Phase-2 specific counter-evidence to (b)**: Game 3's z-flank counter-capture on (0,1,2) (move 7) — where the P2 stone P1 most wanted to flip was the *very same cell* P2 most wanted to keep as their x=0 row anchor — is a deeply asymmetric tactical exchange that doesn't appear in pure Othello (Othello has no goal-axis asymmetry, both players want the same thing: stone count). The asymmetric win axes are what make this work; without them the game collapses.

4. **The hybrid actions are vestigial in our games but not necessarily in all games.** Trained PPO agents in the database (3 runs, all converging) presumably explored move actions during training; we cannot rule out that movement matters in deeper or longer games. We can only confirm it does not matter at our 7–9 move strategic level.

5. **Concession**: 3D-substrate's *mandatory* contribution is small. The same dynamics could likely be reproduced on 2D 4×4 (without losing core character). Concession to (e): the substrate-novelty bonus is partially substrate-effect.

**Adjusted novelty score: 5.** Genuine recombination novelty (above pure re-skin) but not emergent (the play converges to known short-game tactics from Hex+Othello). The R17 hypothesis ("3D + custodian + connection + mobile stones is a genuinely novel combination") is *narrowly true at the rule-tuple level but not deep at the play level*.

---

## Phase 5 — Verdict

```
Team ID: team-pilot
Game ID: 44f6630277b3
Rules Summary: 3D 4×4×4 grid, alternating turns, place-or-move-to-empty
  hybrid actions, Othello-style custodian capture, asymmetric connection
  win (P1 connects z-axis faces, P2 connects x-axis faces). Max 86 turns.
Topology: 3D grid, axis_size=4, 6-neighbor von Neumann, no wraparound.
Turn Structure: alternating (P1 first).
Hybrid actions: yes, but VESTIGIAL — 0/23 turns across 3 games used a
  move action; placement strictly dominates at the strategic-play level.
```

```
SCORES (1-10):
  Strategic Depth: 4
    — Real tactical motifs exist (capture-traps, boundary-anchor
      immunity, flank-counter-flank), but optimal lines converge in
      7–9 moves on a 4³ board. The strategic horizon is shallow because
      capture geometry resolves positions too quickly. 86-turn budget
      is mostly unused.

  Emergent Complexity: 5
    — The "capture-as-connection-completion" cross-mechanic motif is
      genuinely emergent from custodian + connection in a small 3D space.
      The boundary-row trap is a 2-stone fork with real depth. But the
      game has no ko-like repetition, no propagation, no CA — strong
      ceilings on emergence.

  Balance: 2
    — P1 wins 3/3 games tested, against three different P2 defenses
      and including a deliberate seat-swap effort (Game 3 with P2's
      strongest-found "boundary-row trap"). Structural argument: P1
      gets boundary-anchor immunity along the goal axis (z) and tempo;
      P2's goal axis (x) puts their critical stones on a single z-layer
      that P1 can flank-trap. R17's seat_bal ≥ 0.1 gate evidently passed
      during training (P1/P2 trained-agent winrate ~0.5 in self-play)
      but at the strategic-quality level the seat asymmetry is severe.
      This is the most worrying finding for the R17 leaderboard.

  Novelty (post-adversary): 5
    — Genuine recombination novelty at the rule-tuple level (3D +
      custodian + connection-with-asymmetric-goals is not a published
      variant we located). But play converges to tactics directly
      transferable from 3D Hex × Othello. The hybrid place+move
      action contributes 0 to actual play.

  Replayability: 4
    — Three games gave three different P1 winning lines, so there's
      some opening variety. But P2 has no winning strategy, so the
      game replays only in the sense of "watch P1 explore different
      capture geometries". Limited.

  Overall "Would I play this again?": 3
    — As a research artifact (R17 champion), interesting to study.
      As a game, the P1 advantage and short games make it
      unsatisfying to replay competitively.
```

```
CLOSEST KNOWN-GAME ANALOG: 3D Hex with Othello-style custodian capture
  added as a tactical disruptor. Not identical: (i) goal axes are
  asymmetric between players, (ii) capture is custodian (Othello),
  not surround (Go) or none (Hex), (iii) alleged hybrid place+move
  is vestigial. An expert in 3D Hex + Othello would transfer ~70% of
  their intuition immediately but would need 5–10 games to internalize
  the capture-as-connection-completion motif.

KILLER FLAWS:
  1. Severe P1 dominance: 3/3 P1 wins; structural argument that
     boundary-anchor immunity + tempo always favors P1.
  2. Vestigial movement: 384 of 449 actions are move actions, none
     used in our games. Inflates action space ~7× without play impact.
  3. Inert capture threshold: rule_representation specifies threshold=1
     but `_capture_custodian` ignores threshold entirely.
  4. Inert propagation: prop_type="none" but radius/strength/decay are
     stored — fitness counted these toward "rule complexity 17" but
     they are mechanical noise.
  5. Game length too short for max_turns=86 to matter.
  6. 3D substrate adds little: the winning lines could play out on
     2D 4×4 with the same character.

BEST QUALITY: The capture-as-connection-completion cross-mechanic
  motif (e.g. Game 1 move 7: a single placement triggers a double
  custodian capture along x AND extends the connection chain by 3
  cells AND brings the win to one move away). This is a genuinely
  cross-rule tactic that doesn't appear in either ancestor game
  (Hex or Othello) alone. It justifies the recombination claim,
  though not strongly enough to push novelty above 5.

3D STRUCTURAL CONTRIBUTION: Marginal.
  All winning paths in our 3 games used a near-2D structure (single
  column with at most a 1-cell sideways branch). The 3rd dimension
  was *available* but rarely *necessary*. The double-capture in
  Game 1 chained through x at z=2 — that's a 2D pattern lifted into
  3D. The R17 hypothesis "3D shift + custodian-connection
  rediscovery is genuinely deep" is, in this game, more about the
  custodian-connection combo than the 3D substrate. 2D version of
  this game would likely play similarly.

IMPROVEMENT IDEAS:
  Single rule change to deepen the game most: make P2 also start
  with a small handicap (e.g., P2 places 2 stones before P1's
  first move; or P2 picks the goal-axis assignment after seeing
  P1's first move). The current asymmetric-goal-axis design is
  interesting but the seat asymmetry kills the experience. A
  pie rule (after P1's first move, P2 may swap roles) is the
  standard and minimal fix; it would force P1 to play a "balanced"
  first move and likely make the game competitive without changing
  any other rule.

  Alternatively: ban movement (it's vestigial) and reduce
  rule_complexity by 1; OR reduce action space by ~85% by
  collapsing move-actions to a smaller subset. This wouldn't deepen
  play but would honest-up the rule simplicity score.
```

---

## Annex — Engine-verified game records

(For audit: each line is the action ID list for one game; replay via
`./eval_pilot_helper.py "<csv>"` reproduces the analyzed sequence.)

```
Game 1 (P1 win, 9 moves):  5,37,21,53,36,38,39,52,55
Game 2 (P1 win, 7 moves):  5,53,21,41,20,36,52
Game 3 (P1 win, 7 moves):  5,36,21,39,52,37,20
```

Move-action usage across all games: **0 of 23 turns**. Hybrid place+move
status: **enabled but vestigial in human-strategic play**.

R17 hypothesis test (3D + custodian + connection + mobile stones is
genuinely novel): **partially confirmed at the rule-tuple level,
not confirmed at the play level**. Recommend the prompt for the
remaining 21 teams stay as-is — the game has enough structure to
support a real evaluation, and the specific R17 claims (severe P1
imbalance, vestigial moves, marginal 3D contribution) are testable
and likely to replicate across teams.
