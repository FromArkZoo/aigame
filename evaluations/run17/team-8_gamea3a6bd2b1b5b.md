# Team-8 Evaluation — Game `a3a6bd2b1b5b` (R17)

**Team ID:** team-8
**Game ID:** a3a6bd2b1b5b (R17 rank 2 by GE / ELO 2611.9)
**Date:** 2026-04-28
**DB:** `genesis_v2_run17.db`

---

## Phase 1 — Rule comprehension

**Board structure.** 3D grid, axis_size = 4 → 4×4×4 = 64 cells. Topology = `grid` (no torus wrap, no hex/moore). Cell index = `z*16 + y*4 + x`. Each interior cell has 6 neighbours (±x, ±y, ±z); face cells have 5; edge cells 4; corner cells 3.

**Turn structure.** Alternating; one piece per turn. Engine flag confirmed.

**Action space.** 65 total. Cells 0–63 are PLACE actions; cell 64 = PASS. **No move actions** — `action_types=['place']`. The `move_constraint: 'adjacent_empty'` field in the rule dict is dormant (the action-list flag dominates). So this is **NOT** the place+move hybrid the R17 prompt warns about; the action space is the simple place-only ~65, not the ~1700 place+move space.

**Placement constraints.** Target = empty, constraint = anywhere, first-move-anywhere = true. No opening restriction.

**Capture.** `surround` (Go-style) with threshold = 1. After every placement the engine examines adjacent enemy groups; a group with 0 liberties is removed. Threshold 1 is the standard surround threshold.

**Propagation.** `prop_type: none`. The radius/strength/decay fields in the rule dict are inert — `_apply_propagation` early-returns. So `engine.board_values` is always 0 and the win threshold field (42.08) is unused for connection wins.

**Cellular automaton.** None.

**Win condition.** `connection`. P1 must connect the two opposite x-faces (`target_dimension = 0`: cells with x=0 to cells with x=3). P2 must connect the y-faces (`target_dimension_p2 = 1`: y=0 to y=3). The threshold value 42.08 is **ignored** — `_check_connection` only calls `topo.connects_faces(cells, dim)`, BFS over friendly stones, no threshold check. **`max_turns = 87`**, well above the 64-cell board capacity, so practically unreachable. Double-pass = draw.

**Degeneracy / quirk audit.**
- ✅ The `42.080…` threshold is decorative for connection wins. Confirmed by reading `_check_connection` (no threshold use) and `_apply_propagation` (none).
- ✅ Surround capture is **near-inert**: 200 random self-play games produced 127 captures total (0.64 / game) over an average of 41 placements. <1% of placements capture anything. The 6-connectivity in 3D + 4-cell axes gives groups too many liberties to ring efficiently in the time it takes a connection to form.
- ✅ Random self-play is balanced: P1 wins 104 / 200 = 52%, P2 wins 96 / 200 = 48%, no draws. Engine training also reported P1-vs-P2 winrate = 0.50.
- ⚠ Trivially fast wins exist if P2 plays passively. A P1 straight-line race (cells 0,1,2,3) ends at turn 7 if P2 plays anywhere not on x=2,z=0,y=0. Confirmed: with P2 building (1,*,1) y-line at x=1,z=1, P1 wins turn 7.
- ⚠ P2 has a strong block-build counter (see Phase 2/3): the block of P1's track is automatically a build of P2's own track because the two tracks intersect when they share a z-plane. Combined with first-move advantage, this creates real tension rather than a one-sided race.

**Plain-English summary.** "Connection Go in 3D" — Go-style placement with surround capture, on a 4×4×4 cube. P1 races to wire its x=0 face to its x=3 face through a connected chain of black stones; P2 races to wire y=0 to y=3 through a connected chain of white stones. No simultaneity, no movement, no propagation, no CA.

---

## Phase 2 — Strategic play (3 games)

### Game 1 — P1 races a straight x-line, P2 walls along x=2

Sequence (P1, P2 alternating):
`0, 2, 1, 17, 5, 6, 21, 22, 37, 38, 25, 26, 9, 10, 13, 14`

| T | Player | Move | Cell | Reasoning |
|---|--------|------|------|-----------|
| 1 | P1 | 0 | (0,0,0) | Anchor x=0, on row y=0/z=0 racing track. |
| 2 | P2 | 2 | (2,0,0) | Block-build: blocks P1's natural x-line midpoint AND on P2's column track at x=2,z=0. |
| 3 | P1 | 1 | (1,0,0) | Continue racing. (Group now (0,0,0)-(1,0,0).) |
| 4 | P2 | 17 | (1,0,1) | Block at z=1 in case P1 escapes upward. |
| 5 | P1 | 5 | (1,1,0) | Try to detour around (2,0,0) via y=1. |
| 6 | P2 | 6 | (2,1,0) | Block-build: blocks the y=1 detour AND extends the x=2,z=0 column. |
| 7 | P1 | 21 | (1,1,1) | Try z=1 detour. |
| 8 | P2 | 22 | (2,1,1) | Wall at (2,1,1). |
| 9 | P1 | 37 | (1,1,2) | Try z=2. |
| 10 | P2 | 38 | (2,1,2) | Wall at (2,1,2). |
| 11 | P1 | 25 | (1,2,1) | Spread laterally. |
| 12 | P2 | 26 | (2,2,1) | Wall at (2,2,1). |
| 13 | P1 | 9 | (1,2,0) | Y=2 push at z=0. |
| 14 | P2 | 10 | (2,2,0) | Wall at (2,2,0). P2 column now at x=2,z=0 covers y=0,1,2. |
| 15 | P1 | 13 | (1,3,0) | Push to y=3. |
| 16 | P2 | 14 | (2,3,0) | **Wins!** P2's stones at (2,0,0),(2,1,0),(2,2,0),(2,3,0) form a connected y=0→y=3 line at x=2,z=0. |

**Outcome: P2 wins, turn 16.** P1 placed 8 stones, all marooned at x=0,1 (no x=3 reach).

P1 reflection: I treated P2 as a passive blocker and didn't notice that every "block" P2 placed was simultaneously building P2's win-line. The duality is the central feature of this game; missing it = certain loss. I'd play the same opening cell 0 again, but on T5 I'd shift to z=1,2,3 immediately (cell 16, 32, 48) AND start placing at x=3 to anchor the far face.

P2 reflection: I never had to plan a y-connection separately — every reactive block was the y-line. I'd play exactly the same sequence again. The lesson is that P2 doesn't need to choose between blocking and building.

### Game 2 — P1 dodges by switching z-layers

Sequence: `0, 1, 16, 17, 32, 33, 48, 49, 4, 5, 8, 9, 12, 13`

P1's plan: Anchor (0,0,0), then jump to z=1,2,3 hoping P2 won't follow on every layer.
P2's plan: Mirror P1 at x=1 (block-build x=1 column) then pivot to a y-line as soon as P1 stops pushing forward.

| T | Player | Move | Cell | Note |
|---|--------|------|------|------|
| 1 | P1 | 0 | (0,0,0) | |
| 2 | P2 | 1 | (1,0,0) | Block-build x=1, z=0. |
| 3 | P1 | 16 | (0,0,1) | Try z=1 row. |
| 4 | P2 | 17 | (1,0,1) | Block-build x=1, z=1. |
| 5 | P1 | 32 | (0,0,2) | z=2 row. |
| 6 | P2 | 33 | (1,0,2) | Block-build x=1, z=2. |
| 7 | P1 | 48 | (0,0,3) | z=3 row. |
| 8 | P2 | 49 | (1,0,3) | Block-build x=1, z=3. |
| 9 | P1 | 4 | (0,1,0) | Pivot to y=1 at x=0. |
| 10 | P2 | 5 | (1,1,0) | Pivot — start building y-line at x=1,z=0. |
| 11 | P1 | 8 | (0,2,0) | y=2 at x=0. |
| 12 | P2 | 9 | (1,2,0) | y=2 at x=1,z=0. |
| 13 | P1 | 12 | (0,3,0) | y=3 at x=0. |
| 14 | P2 | 13 | (1,3,0) | **Wins!** P2's group `(1,0,0)-(1,1,0)-(1,2,0)-(1,3,0)` at z=0 spans y=0..3. |

**Outcome: P2 wins, turn 14.** P1 was 7 stones deep on the x=0 face with zero progress toward x=3; P2 built a 4-stone y-line at x=1,z=0 incidentally while shadowing P1.

P1 reflection: Z-layer dodge was useless — P2 just shadowed me at x=1, and the four shadow stones at z=0..3 each became "first stone of a y-line at x=1,z=k". I needed to push x-direction (forward), not y/z (sideways/up). Never anchored x=3.

P2 reflection: P1 gave me four free first-stones for four parallel y-lines. I just had to pick whichever z-plane finished first (z=0). Same lesson as Game 1.

### Game 3 — P1 plays the "central junction" with seat-aware blocking (seat-swap exercise)

For the seat-swap pass I assigned my "primary side" mentally to P2 (since the engine gives P1 the move-1 advantage; swapping = playing carefully from the disadvantaged seat). Play sequence:

`5, 6, 4, 2, 10, 9, 21, 13, 22, 23, 26, 11, 27`

| T | Player | Move | Cell | Note |
|---|--------|------|------|------|
| 1 | P1 | 5 | (1,1,0) | Central junction; on P1 track (y=1,z=0) AND P2 track (x=1,z=0). |
| 2 | P2 | 6 | (2,1,0) | Block-build: P1 track AND P2 track (x=2,z=0). |
| 3 | P1 | 4 | (0,1,0) | Anchor x=0. (0,1,0)-(1,1,0) connected. |
| 4 | P2 | 2 | (2,0,0) | Build x=2 column, anchor y=0. |
| 5 | P1 | 10 | (2,2,0) | **Block AND build**: blocks P2's x=2 line at y=2 AND anchors a P1 cell that's two bridge-steps from x=3. Isolated for now. |
| 6 | P2 | 9 | (1,2,0) | Block P1's natural (1,1,0)→(2,2,0) bridge AND build P2's alt y-line at x=1. |
| 7 | P1 | 21 | (1,1,1) | Open a z=1 bridge from (1,1,0). |
| 8 | P2 | 13 | (1,3,0) | Extend P2's (1,2,0) toward y=3. |
| 9 | P1 | 22 | (2,1,1) | Bridge: (1,1,1)→(2,1,1), and (2,1,1) is adjacent to (2,2,0)'s vertical neighbour (2,2,1). |
| 10 | P2 | 23 | (3,1,1) | Block P1's (2,1,1)→(3,1,1) jump to x=3. |
| 11 | P1 | 26 | (2,2,1) | Bridge: connects (2,1,1)-(2,2,1)-(2,2,0). P1 group now spans x=0,1,2 in one component. |
| 12 | P2 | 11 | (3,2,0) | Block P1 at (3,2,0). |
| 13 | P1 | 27 | (3,2,1) | **Wins!** (3,2,1) is adjacent to (2,2,1)=P1; the P1 path `(0,1,0)→(1,1,0)→(1,1,1)→(2,1,1)→(2,2,1)→(3,2,1)` connects x=0 face to x=3 face. |

**Outcome: P1 wins, turn 13.** Final P1 piece count = 7, P2 = 6. Game ended via stated win condition (connection), not double-pass or max_turns.

P1 strategy notes from G3:
- Opening the centre (1,1,0) instead of the corner (0,0,0) trades guaranteed x=0 anchorage for tactical optionality on T2.
- Cell 10 (2,2,0) on T5 was the critical move — it severed P2's z=0 y-line (the line that won Games 1 & 2) at y=2, forcing P2 to reroute through z=1 or x=1.
- Once P2 was forced into (1,2,0) / (1,3,0) / (3,1,1) / (3,2,0) blocks that *didn't* form their own y-line, the block-build duality flipped in P1's favour.

P2 strategy notes from G3:
- T6 (1,2,0) was a fork: it blocked P1 but cost P2 the (2,2,0)-anchored x=2 column. Once that column was severed, P2 had to start a *new* y-line from scratch (x=1,z=0), and P1's first-move advantage compounded.
- T12 (3,2,0) was the correct block but came too late — P1 already had the z=1 alternative bridge ready.

### Strategy guides (after 3 games)

**Player 1 guide.**
1. Open in the **interior of the y=1 or y=2 row, z=0 or z=1**, e.g., (1,1,0) or (1,2,1). This opening cell sits on a P2 track, so any P2 block-build forces P2 onto a *different* track.
2. By move 3, claim a **P2-track-severing cell at x=2** (e.g., (2,2,0) or (2,1,1)). This is the single highest-leverage move because it converts P2's "block = build" into "block = block-only".
3. Reserve a z=1 (or z=2) bridge to side-step late P2 walls; the 4×4 face has 16 entry cells per face so P1 always has more entry candidates than P2 has stones.
4. Don't bother chasing captures — surround capture is essentially decorative on this board.

**Player 2 guide.**
1. T2 must be a block-build cell on the same z-plane as P1's T1 stone, ideally one that gives P2 the longest possible interior subchain. Against (1,1,0): play (2,1,0) or (0,1,0). Against (0,0,0): play (1,0,0).
2. Continue the x-column (or y-row) you opened on T2 *unless* P1 severs it. If severed, immediately start a parallel y-line at a different x or z.
3. P2 has 16 candidate y-tracks; P1 can sever at most 1 per turn, so P2 only needs to be the first to commit a track P1 is unwilling to spend two stones to sever.
4. Avoid wasting moves on captures — this is a connection race.

---

## Phase 3 — Joint strategic analysis

**Distinct viable strategies?** Two: (a) the **track-race** (commit early to one (y,z) row for P1 / (x,z) column for P2 and play 4 moves on it), (b) the **junction-blocker** (open central, accumulate threats, force opponent to spend tempo on detours). Game 3 showed (b) beats naive (a) for P1.

**Counter-play?** Yes. P1 can sever P2's column with a single x-line cell at the right (x,z). P2 has the structural block-build duality. Both sides have legitimate tactics; neither is dominant from move 1 with skilled play.

**Short- vs long-term tension?** Real but compressed. With 4 stones to win, every move is both tactical and committal. There's almost no long game — the longest of my 3 evaluation games was 16 turns and the avg random-play game was 41 turns of a 87-turn cap. Endgames per se don't really exist; the connection completes mid-game.

**Emergent concepts.**
- **Block-build duality** — a stone at (x_2, y_1, z) blocks P1's (y_1, z) track AND builds P2's (x_2, z) track. This is the central structural feature; analogous to Hex's "you can't both win" but without the forced-cross theorem (because 3D paths don't have to cross).
- **Track-severance value** — a single stone at the right (x_2, *, z) can convert opponent's block-build cells into block-only cells.
- **Plane-switching** — paths can detour around blocks via z; in practice though both players play on shared z-planes, so this is a tactical option rather than a strategic frame.
- No territory, no influence, no ko fights, no mutual annihilation tactics. Capture too rare to matter.

**Does 3D add depth?**
*Modest*. The 3rd dimension provides additional tracks (16 each for P1 and P2 instead of 4 in 2D) and detour options, but most strategic content can be reduced to "4×4 Hex-ish on a single z-plane" because (a) random-play and skilled-play games concentrate on 1-2 z-planes, (b) the win is satisfied by a 4-stone path in any z-plane, (c) capture is too rare to motivate using the 3rd dimension defensively. Flattened to 2D 4×4 grid with the same rules, P1-connects-x and P2-connects-y, this is **literally 4×4 Hex with surround capture** and most of the strategic content survives. The 3D substrate adds optionality but very little qualitative novelty.

**Topology dependence.** Grid is essential — 6-connectivity gives the right liberty density. Torus (wrap) would change the connection geometry significantly and probably break it (any line wraps trivially). Moore (26-conn) would make capture even harder and turn the game into pure race. Sierpinski would deny most cells.

**Move-enabled?** No — place-only. The R17 caveat about hybrid action spaces does not apply.

**First-mover advantage quantified.** Random self-play: P1 = 52%, P2 = 48% (200 games, no draws). PPO training reported final P1 winrate = 0.50. My 3 evaluation games: 1 P1 win (game 3), 2 P2 wins (games 1 & 2). The P2 wins both came from naive P1 play that ignored block-build duality; smart P1 in game 3 won. Engineered 16-track race: in the 12 cases where the schedule completed, P1 won all 12 but those were exactly the cases where P2's first move didn't actually block; the other 36 cases ended in collision (= P2 successfully blocked, schedule undefined). Conclusion: **the seat balance is genuinely close to 50/50 under skilled play**, well within the R17 0.1 seat-balance floor.

---

## Phase 4 — Novelty Adversary

**Adversary opening.** "This is just 4×4 3D Hex with Go capture. Both pieces of that combination — 3D Hex and surround capture — are >40 years old. The only ‘novelty' is the substrate dimension, and the game's behaviour reduces to a 2D Hex-like race on whichever z-plane the players happen to share. The capture rule is decorative (0.64 captures / game). The connection threshold is decorative (unused). The propagation field is decorative (none). The move-action space is decorative (place-only). What's left to be novel?"

**Catalog comparison.**
- **Hex / Y / Havannah.** Hex on 4×4 is trivially P1-win; Hex on a 4×4 *square* grid (not rhombus) with x-vs-y connection is closer to "Bridg-it" / "Connections" (1960s, Gardner). Bridg-it has a known P1-win strategy. The 3D extension here (depth-4 cube) is a cosmetic generalisation; an experienced Bridg-it / Hex player would transfer strategy almost immediately — open a key bridge cell, respond with the dual-purpose cell.
- **3D Tic-Tac-Toe / Qubic / Score Four.** Different goal (n-in-a-row, not face-connect), different victory condition (line, not path). Not a close analog.
- **3D Hex / Cubic Hex.** Has been studied informally; the present game is essentially that with surround capture grafted on. Adding capture without making it bite (as here) is a no-op.
- **3D Go / Notakto-3D.** 3D Go has been explored as a curiosity; 3D Go without territory and with face-connection win is still a connection game, not Go proper. The R8 champion ("Connection Go", 2D, custodian + connection) was *the* publishable game in this project; this game is just R8's family in 3D minus custodian capture — **and surround capture in 3D is much weaker than custodian in 2D** because 6-connectivity gives groups too many liberties.
- **Reversi / Othello.** Different mechanic (flip-by-bracket); not close.
- **Lines of Action.** Movement-driven; not close.
- **Slither / Tumbleweed.** Very different goals.
- **Diplomacy / Blotto / RPS-scaled.** Simultaneous; this game is alternating, so n/a.

**Adversary's strongest line.** "An expert at 4×4 Bridg-it (or 4×4 Shannon switching games more generally) plays this on day one. The 3D substrate gives them a slightly bigger board, but the underlying duality is identical. The R17 hypothesis — that 3D + custodian + connection + mobile stones is novel — does *not* apply here, because this game has no custodian and no movement. So even the R17 hypothesis treats this as the boring corner of the 3D-connection family."

**P1 / P2 rebuttal.**
- *Not 4×4 Bridg-it because:* (i) Bridg-it has fixed connection points; here every face cell is a candidate endpoint, giving 16 entry cells per face and 16 tracks. (ii) Bridg-it has no captures at all; this game has surround capture which, while rare, can still threaten isolated stones (we saw zero captures in 3 played games but 0.64/game in random play, including occasional 1- or 2-stone captures that change tactical evaluations). (iii) The detour cost in 3D is materially different: a single block in 2D Bridg-it usually costs 1 detour stone; in 3D it can be free (different z-plane) OR can cost 2-3 stones if the relevant z-plane is already contested. Game 3 showed a 5-stone winning path that used 1 detour through z=1 — that geometry is unavailable on a 2D board.
- *Not 3D Hex because:* in classical 3D Hex / Qubic-style boards the two faces are typically opposite of the same cube and players share a goal axis. Here the goals are *orthogonal* axes — P1 connects x, P2 connects y — and the two paths can avoid each other entirely in z. That orthogonality is what gives rise to block-build duality without forced intersection.
- *Not just R8's family because:* R8 was 2D + custodian. The 3D + surround variant has fundamentally different liberty arithmetic (capture nearly never fires) and a much larger detour budget.

**Honest assessment of rebuttal strength.** The rebuttals are genuine but modest. The game is *recognisably* in the 3D-connection family, and a Hex / Bridg-it expert would be at home within ~10 minutes. The orthogonal-axis goal is the cleanest novel feature; the rest is incremental.

**Novelty score: 3 / 10.** "3D Bridg-it / 3D Hex with mostly-decorative Go capture." Sits near the "X on a different topology" end of the scale. The orthogonal-goal-axis dynamic is the single non-trivial twist.

---

## Phase 5 — Verdict

**Team ID:** team-8
**Game ID:** a3a6bd2b1b5b
**Rules summary:** Alternating place-only Go-style game on a 4×4×4 grid. Surround capture with threshold 1. Win = first to connect their assigned pair of opposite faces (P1: x-axes, P2: y-axes). Max 87 turns; double-pass = draw.
**Topology:** 3D grid 4×4×4, 6-connectivity, no wrap.
**Turn structure:** Alternating, 1 piece / turn.
**Hybrid actions:** No — place-only. The `move_constraint` field in the rule dict is dormant.

### Scores (1-10)

| Metric | Score | Rationale |
|---|---|---|
| **Strategic Depth** | **5** | Real tactical choices on every move via block-build duality; track-severance value is non-obvious; central-junction openings beat corner openings. But the game tree is shallow (most decisive games end in 7-16 turns) and capture is essentially inert. Game 3's 13-turn P1 win required exactly one non-trivial insight (sever x=2 column at y=2). After that, play is mostly forced. |
| **Emergent Complexity** | **4** | The block-build duality emerges naturally from the orthogonal-axis goal — a genuinely emergent property, not built into the rules. Beyond that, almost nothing: no territory, no influence (propagation = none), no ko (capture too rare), no influence cascades, no group dynamics worth speaking of. |
| **Balance** | **7** | Random self-play 52/48; PPO training 50/50; my 3 games gave 1 P1 / 2 P2 wins with a clear "smart-P1-beats-naive-P2" attribution for the P2 victories. Both seats have constructive winning strategies. Well above the R17 seat-balance floor of 0.1. |
| **Novelty (post-adversary)** | **3** | "3D Bridg-it / 3D Hex with vestigial Go capture." Orthogonal-goal-axes is the single non-trivial twist; everything else is in the 1960s connection-game literature or the R8 family. Surround capture doesn't fire often enough to differentiate. |
| **Replayability** | **3** | Short games (7-16 turns under skilled play, mean 41 random), small board (64 cells), small action space (65), only 4 stones needed to win, no opening restriction. Optimal play converges quickly. |
| **Overall — would I play this again?** | **4** | I'd play 5-10 games to learn the block-build pattern, then move on. There's a real tactical lesson here but it doesn't sustain a long study. Compared to R8's 2D Connection Go (8/10 human eval), this 3D variant is structurally weaker because surround capture is too diluted. |

### Closest known-game analog
**4×4 Bridg-it on a 3D substrate** (or equivalently "3D Hex with orthogonal goal axes and decorative Go capture"). Not identical because: (a) 16 entry cells per face vs Bridg-it's fixed endpoints, (b) the 3rd dimension supports z-plane detours that no 2D Bridg-it allows, (c) surround capture exists (rarely fires but does fire), (d) goal axes are orthogonal not aligned.

### Killer flaws
1. **Surround capture is essentially inert** (0.64 captures / random game; 0 in my 3 evaluation games). The capture rule contributes near-zero strategic content; the game would behave almost identically with `capture_type: none`.
2. **Threshold field (42.08) is unused** — it's a generator-mutation artifact for connection wins. Cosmetic, but indicates the GE composite is rewarding a parameter that does nothing here.
3. **Propagation rule is `none`** — radius/strength/decay fields are dormant. Same artifact.
4. **`max_turns = 87`** is unreachable on a 64-cell place-only board. Effectively a no-op.
5. **`move_constraint: 'adjacent_empty'`** on a place-only game is a generator artifact.
6. **Detour cost asymmetry** — when P1 plays a corner like (0,0,0), P2 has a guaranteed 1-detour block-build at (1,0,0), forcing P1 to 5+ stones while P2 finishes in 4 (P2 wins T8). Skilled P1 must open in the interior to neutralise this. This is *partly* a flaw and partly the source of strategic depth.

### Best quality
The **orthogonal-goal-axis block-build duality**: P2 blocks P1 by playing on a cell that's simultaneously on a P2 winning track. This duality emerges from the geometry (orthogonal connection axes share intersection cells in shared z-planes) and forces every move to carry both attacking and defensive value. It's the single feature that makes the game worth playing past 5 minutes.

### 3D structural contribution
**Modest.** Pros: the 3rd dimension provides 4× more candidate tracks per player and enables single-stone-detour-via-z that 2D Bridg-it forbids. Cons: most games concentrate on 1-2 z-planes, capture is weakened (more liberties), and the strategic content survives a 2D flattening. Counter-test: imagine the same game on a 2D 4×4 grid with the same rules. It would be tighter (no z-detours), capture would matter more, and it would be very close to "4×4 Bridg-it with Go capture" — a **better** game in my view, because every cell carries higher leverage. The 3D substrate dilutes intensity without adding qualitatively new strategy.

This contradicts the R17 headline hypothesis ("3D substrate is genuinely deep play, not a substrate artifact") *for this specific game.* The 3D substrate here is an artifact: it bumps the GE composite via the +5% non-grid-novelty multiplier (wait — this game IS grid, so it gets no multiplier; the 3D bump must come from elsewhere). Looking at the metric scores: NonTriviality 0.85, StrategicDiversity 0.67, StrategicDepth 0.47, RuleSimplicity 0.27 → GE 0.29. The high NonTriviality reflects "decisive games happen" and StrategicDiversity reflects "many move sequences possible", but neither captures whether the strategic content is *deep*. My human read says it's not particularly deep — I'd score it ~5 / 10 on depth alone.

### Improvement idea (single rule change)
**Replace surround capture with custodian capture.** Custodian on a 3D 4×4×4 grid would actually fire frequently: a single placed stone bracketing a 1-2 stone enemy line along an axis flips it. This would (a) make capture a real strategic factor, (b) reward central play (more brackets), (c) tie the game more tightly to R8's celebrated 2D Connection Go (8/10 human eval) family, and (d) probably push the strategic depth from 5 to 7. This is in fact what R17's actual GE-rank-1 champion (`44f6630277b3`) did differently — custodian + place+move hybrid. The current game's choice of surround was likely the wrong capture type for this substrate.

---

**Final headline:** A solid, balanced, but shallow 3D-Bridg-it variant in the R8 family. The orthogonal-goal-axis dynamic creates real block-build tactics, but surround capture is wasted on this substrate, the action space is small, and the game tree is short. Worth a few plays for the duality lesson; nothing publishable.
