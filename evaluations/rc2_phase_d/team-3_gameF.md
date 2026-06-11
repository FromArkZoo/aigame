# Team 3 — Game F verdict

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  8×8 grid, von Neumann (orthogonal) adjacency, no wrap. Players alternate
  placing one stone on any empty cell. **Asymmetric connection win**: P1 wins
  by connecting the top face (d1=0) to the bottom face (d1=7) with an
  orthogonally-connected path of its stones; P2 wins by connecting the left
  face (d0=0) to the right face (d0=7). Same-tick double connection = draw.
  Go-style **surround capture**: after a placement, any adjacent enemy group
  with zero liberties is removed. A permanent **influence field** is laid down
  by each placement (strength 0.715, decay 0.751, radius 3) but is irrelevant
  to the win. If no one connects by 100 steps, the player with more stones
  wins (equal = draw). Double pass = immediate draw. Super-ko: a move
  recreating a prior position is rolled back to a pass.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Connection-win in both decisive lines (Line 1 P1 @ ply15, Line 2 P1 @ ply17).
  Confirmed double-pass → DRAW (`27,64,64` ended DRAW at step 3). Did not reach
  the 100-step stone-count tiebreak in normal play.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: The **ghost-influence quirk is real and observable**: after
  P1 captured a P2 corner stone (`1,0,8`), cell (0,0) read **+0.36** in the
  influence field — the removed P2 stone's −0.715 contribution persists, only
  net-flipped positive by the two adjacent P1 stones. Since influence never
  feeds the win condition, this quirk is mechanically inert.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `27,32,35,33,19,34,11,36,3,37,43,38,51,39,59`
- Plan and what happened: I (P1) raced a straight vertical column at x=3
  (cells 3/11/19/27/35/43/51/59); P2 raced a straight horizontal row at y=4.
  Their lines must cross at exactly one cell, (3,4)=35; I grabbed it on ply 3.
  From then P2's row was permanently severed at the column while I filled the
  rest of the column.
- Result (winner, end cause, plies): **P1 win**, connection fired, ply 15.
  Final board shows P2's full y=4 row blocked by my x=3 column.

### Line 2 — you as P2
- Moves: `27,35,36,34,28,33,44,32,20,43,52,51,12,26,60,18,4`
- Plan and what happened: I drove P2 as an active **denier**: P1 opened (3,3),
  I immediately took the column crossing (3,4)=35 to break P1's x=3 column;
  P1 calmly re-committed one column right (x=4), grabbing the *new* crossing
  (4,4)=36 before me. I built a clean 4-stone run on row 4 (x=0..3) and probed
  detours (43,51,26,18), but P1's x=4 column is a solid wall I could never
  cross. Whack-a-mole denial failed because P1, moving first, always reaches
  the contested crossing of its chosen column first.
- Result: **P1 win**, connection fired, ply 17. P2 row 4 walled at x=4.

### Line 3 — adversarial / novelty-stress
- Moves: `1,0,8` (+ `--values`), plus `1,0,8,9`, `27,64,64`
- What you tried to break / stress, and what happened: (a) **Capture +
  ghost-influence**: P1 surrounded a P2 corner stone — it was removed, and the
  influence field retained the captured stone's sign (cell (0,0)=+0.36),
  confirming the documented ghost quirk. (b) **Double pass** → immediate DRAW.
  (c) Probed for a connection-breaking capture: surrounding a *single* isolated
  stone is feasible, but a stone inside a building column is part of a
  multi-liberty group and is effectively uncapturable during a race, so capture
  cannot realistically break a committed connection.
- Result: capture works as Go; ghost influence inert; draw reachable only by
  mutual passing (no decisive use of capture found).

### Additional lines (optional)
Line 2 already exercises the full denial fight across 17 plies; the capture
and pass probes above cover the remaining mechanics.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why): Commit to a single
  straight line in your own connection direction and **win the unique crossing
  cell** where your line meets the opponent's line. Because two straight lines
  (one vertical, one horizontal) intersect at exactly one cell, whoever owns
  that cell both completes their own wall and severs the opponent's. Filler
  stones are nearly forced; the whole game compresses to a fight over crossings.
- Counterplay: When I (as P2) pre-empted P1's crossing, P1 simply shifted its
  column one file over and seized the new crossing first. Denial buys a tempo
  but never the game, because the first player re-reaches the next crossing
  ahead of the denier. Capture exists as counterplay in principle but is
  impractical against a connected, multi-liberty column.
- Topology/board effects on strategy: Orthogonal (von Neumann) adjacency on a
  square board is what makes a *complete* straight column an impassable wall —
  there are no diagonal leaks through a filled file. This is the engine of the
  whole game and of the first-player edge.
- Emergent concepts you'd name (or "none observed"): Hex-style
  **block-equals-connect duality** (severing the opponent = completing your own
  wall). The "ghost influence" is a named quirk but produces no emergent play.
- Player agency: Your choices (which file to commit to, when to grab a crossing,
  when to deny) decide the *path*, but the **first-move structural advantage
  decides the result** in symmetric play — P1 won every decisive line I ran,
  including one where I actively denied as P2.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior: This is **Hex on
  a square grid** — two players with crossing connection goals, blocking =
  winning. With orthogonal adjacency it's essentially the classic square-board
  connection game (Bridg-it/Gale family rendered with stones). The Go capture
  and the influence field are bolt-ons that, in observed play, never changed an
  outcome: capture is impractical mid-race and influence is win-irrelevant.
  Strip those and you have a pure square-grid connection race.
- Honest novelty assessment after arguing that case: Low-to-moderate. The
  connection core is a well-known prior; the genuinely distinctive additions
  (surround capture, permanent influence with the ghost quirk) are present but
  vestigial — they decorate rather than transform. The one real character trait,
  the crossing-cell fight, is inherited from Hex, not novel here.

## Phase 5 — Verdict

- P1-role experience sub-score (1-10): 4.0 — clean, decisive, but the winning
  plan is mechanical (commit a column, take the crossing).
- P2-role experience sub-score (1-10): 2.8 — structurally on the back foot;
  my best denial play still lost, with little creative agency.
- Role-averaged sub-score: 3.4
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** **2** — P1 won both
  decisive lines including one where I actively denied as P2, because the first
  player always reaches the contested crossing of its chosen file first.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 3.4**
- One-paragraph justification of the Overall, citing your Phase 2 lines: The
  connection core is clean and the Hex-duality is genuinely elegant, but Line 1
  and Line 2 both show the game collapses to a single mechanical idea — commit
  to a straight file and win its crossing — with a robust first-player edge that
  my active P2 denial in Line 2 could not overcome (P1 won at ply 17). The
  ostensibly novel mechanics are inert: capture never broke a connection in
  Line 3, and the influence field (ghost quirk included) is decorative since it
  never feeds the win. That places it below the R8/R19 anchors and roughly at
  R20/R21 drift level: a competent but derivative square-grid Hex with an
  imbalance and two vestigial systems. **Overall 3.4.**
