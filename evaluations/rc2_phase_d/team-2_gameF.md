# Team 2 — Game F verdict

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  An 8×8 square grid, orthogonal (von Neumann) adjacency, no wrap. Players
  alternate placing one stone on any empty cell (PLACE 0..63) or PASS (64).
  It is a **connection race**: P1 wins by linking the top row (d1=0) to the
  bottom row (d1=7) with an orthogonally-connected chain of P1 stones; P2 wins
  by linking the left column (d0=0) to the right column (d0=7) with P2 stones.
  Because both must cross the board with orthogonal-only paths, a P1 vertical
  chain and a P2 horizontal chain must contest a shared crossing cell. Go-style
  surround capture is present (an enemy group with zero liberties is removed —
  verified by forcing a corner capture). An influence field is propagated by
  every placement but it is **vestigial**: the win is connection and the only
  tiebreak (turn limit) is by raw stone count, so influence never affects any
  outcome. "Ghost influence" (captured stones keep their original-sign
  influence) is therefore a quirk of a subsystem that cannot change results.
- What actually ends the game, and how often each end cause occurred:
  Every one of my decisive lines ended by **connection win** ("win condition
  fired"). Of 4 decisive games: P1 won 2 (uncontested column; crossing-timed
  column), P2 won 2 (uncontested row; crossing-steal race). No draws, no
  turn-limit tiebreaks, no double-pass draws occurred in my play.
- Anything that surprised you about how the engine behaved vs. your reading:
  Nothing contradicted the rules. Confirmed: capture fires immediately on
  liberty-fill; connection is detected on the completing ply; the influence
  field accumulates but is decorative. The crossing-cell arrival timing being
  outcome-decisive was the main emergent surprise.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `59,32,51,33,43,34,35,36,27,37,19,38,11,39,3`
- Plan and what happened: I (P1) built column x=3 **bottom-up** specifically
  to reach the crossing cell (3,4) before P2's row-4 wall could claim it. P1
  grabbed (3,4)=35 on ply 7; P2's row 4 (32,33,34,36,37,38,39) was then
  permanently severed at x=3. P1 then filled up the column.
- Result (winner, end cause, plies): **P1 win, connection, 15 plies.**

### Line 2 — you as P2
- Moves: `3,32,11,33,19,34,27,35,28,36,20,37,12,38,4,39`
- Plan and what happened: I (P2) let P1 commit to a top-down column 3, then
  stole the low crossing cell (3,4)=35 on ply 8 (P2's 4th stone arrives before
  P1's 5th). With column 3 capped at y=4, P1 could only build a 4×2 block above
  the wall; P2 completed row 4 across the board.
- Result: **P2 win, connection, 16 plies.**

### Line 3 — adversarial / novelty-stress
- Moves: `9,0,1,64,8` (capture probe) and `35,27,43,19,51,11,59,3` (block
  probe) and `0,32,1,33,2,34,3,35,4,36,5,37,6,38,7,39` (symmetry probe)
- What you tried to break / stress, and what happened: (a) Forced a Go-style
  corner capture — P2's (0,0) stone was removed once both liberties were filled;
  `--values` confirmed the captured stone's negative influence persists
  ("ghost"), but since influence is vestigial this changes nothing. (b) Drove
  P2 to block a single P1 column from the top: P1 was walled off and forced
  into a Hex-style ladder detour, confirming a lone column cannot brute-force
  through a committed blocker. (c) Verified the engine awards P2 a symmetric
  horizontal connection win.
- Result: capture fired as specified; block forced a ladder (no result reached
  in that fragment); symmetry probe **P2 win, connection, 16 plies.**

### Additional lines (optional)
Warm-up: `3,0,11,...,59` — P1 completes an uncontested column → P1 win, 15
plies, verifying connection detection.

## Phase 3 — Joint strategic analysis

- Core tactical loop: a strong move either (i) advances your own wall toward
  the two goal faces or (ii) seizes/holds the unique crossing cell where your
  chain must cut the opponent's. Because adjacency is orthogonal-only, a single
  gap in your wall is fatal and a single stone on the crossing both blocks the
  opponent and advances you — so the crossing cell is the pivot of every game.
- Counterplay: blocking is real and strong. When P2 stole the low crossing
  (Line 2), P1's column died and P1 had no recovery in a single file; the
  answer is to approach the crossing from the side that reaches it first (Line
  1, bottom-up) or to use diagonal **bridges** (two-carrier links P2 cannot cut
  in one move). The game clearly rewards responding to the opponent's chain.
- Topology/board effects: orthogonal-only adjacency makes walls "tight" (no
  diagonal leaks), so connection is harder and blocking is easier than on Hex's
  6-connectivity. Crossing timing (ply 2r+1 to reach row r top-down) is a
  direct artifact of the square lattice.
- Emergent concepts: crossing-cell tempo, mutual-wall race (your wall is the
  opponent's block), Hex-style bridges and ladders.
- Player agency: the result was decided by MY choices (which face to approach,
  when to grab the crossing), not by engine dynamics — every decisive game
  turned on a single contested cell I controlled.

## Phase 4 — Novelty adversary

- Strongest case that this is a re-skin: it is essentially **Hex/Bridg-it
  played on a square lattice with orthogonal connectivity** — two players race
  to connect opposite face-pairs, exactly the Hex/Gale family, just with
  von-Neumann adjacency instead of hex adjacency (which reintroduces draws and
  tight walls). The Go capture and the influence field are bolted-on systems
  that, for the connection win, are at best marginal (capture) and entirely
  vestigial (influence).
- Honest novelty assessment: low-to-moderate. The connection core is textbook
  prior art. The only genuinely non-standard wrinkle is that surround-capture
  *can* punch a gap in an opponent's completed wall — a real interaction with
  the connection goal — but it is expensive and I never found it worth the
  tempo versus simply racing. Net: a competent, decisive connection game with
  two largely inert subsystems.

## Phase 5 — Verdict

- P1-role experience sub-score (1-10): 4.1
- P2-role experience sub-score (1-10): 4.1
- Role-averaged sub-score: 4.1
- **Fairness perception (1-5):** 3 — Both roles won decisive games in my play;
  P1's one-tempo head start is offset by P2's ability to steal a low crossing
  cell, so it felt balanced.
- **Overall (1-10, anchored): 4.0**
- One-paragraph justification: F is a clean, fully-functional connection game
  with real, transparent strategy — Line 1 and Line 2 both turned on a single
  crossing cell whose ownership I could time and contest, and outcomes were
  decisive with no degenerate draws. That puts it above broken or noise-driven
  games. But it is also a near-textbook Hex/Bridg-it reskin on a square grid,
  its Go-capture rarely pays for itself against simply racing, and its entire
  influence subsystem is decorative (never touches the win or the stone-count
  tiebreak). Genuine but derivative, with two inert subsystems dragging
  coherence — anchored just below R19/above R21 noise, I land at 4.0.
