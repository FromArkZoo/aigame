# Team 3 — Game B verdict

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  Fractal **Menger-sponge** board (9×9×9 grid, 400 active cells, holes block
  adjacency; degree 2–6). Place on any empty cell (no spatial constraint).
  **PIE-SWAP** is legal as P2's first action (steal P1's opening: colours flip,
  goals swap, original P1 then plays second). Each placement adds **+1.0
  influence** (P1) / −1.0 (P2) to the placed cell and every neighbour
  (decay=1, radius 1), permanently. **Win = influence threshold**: a player wins
  when the influence summed over the cells they OWN exceeds **30** (P2 sign-
  corrected); a stone sitting on net-enemy influence *subtracts*. **Capture =
  outnumber**: after you place, any adjacent enemy stone with ≥2 of your
  neighbours is removed. **Ghost influence**: a captured stone's negative
  influence stays on the board forever. Double pass = draw; super-ko;
  100-step stone-count tiebreak.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw): Threshold win
  in both decisive lines (Line 1 P1 31-26 @ ply21; Line 2 P2 31-26 @ ply22 after
  a pie-swap). Confirmed double-pass DRAW in the adversarial probe. No
  turn-limit games.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: The **ghost-influence tension is severe and real**: after P1
  captured a P2 stone wedged between two P1 stones, P1's score *stayed at 0*
  (its two cells read +0.00 each) — the captured stone's −1 ghost exactly
  cancelled P1's own +1. So capturing inside your own cluster craters your own
  scoring, and a sacrificed invader damages enemy territory permanently.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `0,728,1,727,2,726,3,725,4,724,5,723,6,722,7,721,8,720,9,710,18,709,27,708,36,707,45,706,54,705,63,704,72,703,11,702`
- Plan and what happened: I drove P1 to build an efficient connected cluster
  along the two fully-active edges of the d2=0 face (row y=0 + column x=0),
  maximising friendly-neighbour reinforcement so each stone sits on rising
  influence. P2 raced an equivalent cluster in the far (8,8,8) corner. Both grew
  ~+2.5–3 score/stone; my move-1 tempo lead carried me across 30 first
  (P1=+28 at ply20, +31 at ply21).
- Result (winner, end cause, plies): **P1 win**, threshold, ply 21, 31-26.

### Line 2 — you as P2
- Moves: `0,730,728,1,727,2,726,3,725,4,724,5,723,6,722,7,721,8,720,9,710,18`
- Plan and what happened: P1 opened with a normal corner stone; I (P2)
  **pie-swapped (730)** to steal it — the stone flipped to mine and the goals
  swapped, putting me one tempo ahead with P1 to move. I then built the same
  efficient edge-cluster from the stolen stone while P1 raced the far corner.
  The swapped tempo carried me over 30 one ply before P1.
- Result: **P2 win**, threshold, ply 22, 31-26 — a clean mirror of Line 1,
  proving the pie rule transfers the first-player edge.

### Line 3 — adversarial / novelty-stress
- Moves: `0,728,2` (baseline) vs `0,1,2` (sacrificial crater); `0,1,2,729,729`
- What you tried to break / stress, and what happened: I isolated the
  ghost-capture tension. **Baseline** (P1 at (0,0,0)+(2,0,0), no invader):
  P1=+2.0. **With a P2 sacrifice** at (1,0,0) — which P1 is *forced* to capture
  because the geometry leaves no other adjacency — P1's two cells both crater to
  net 0 and P1=+0.0. So **one sacrificed P2 stone permanently cost P1 two points
  even though P2 lost the stone**: a genuine suppression-by-sacrifice tactic.
  Confirmed double-pass DRAW as the only forced non-decisive end.
- Result: clean −2 swing from a single ghost crater; demonstrates real
  counterplay that the pure-race games lack.

### Additional lines (optional)
The pie-swap probe (`0,730`) verified seat-swap mechanics (stone recolours,
scores/goals swap, P1 moves next); the capture probe verified outnumber removal
(2 friendly neighbours clears the enemy stone).

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why): Grow a dense
  connected cluster so each new stone lands on cells already lifted by friendly
  neighbours — score per stone rises with internal edges. Avoid capturing inside
  your own cluster (it craters you). Consider sacrificing an invader into the
  enemy cluster to plant a permanent −crater.
- Counterplay: Real and varied. P2 can race (Line 1), steal via pie-swap
  (Line 2), or suppress by sacrificing invaders that crater the leader's
  territory (Line 3). This is the first game in the batch where the trailing side
  has genuine tools beyond "place faster."
- Topology/board effects on strategy: The Menger holes break up adjacency, so
  you cannot make an arbitrarily dense blob — you must route clusters along the
  fully-active edges/planes, which gives the board positional character and caps
  score-per-stone.
- Emergent concepts you'd name (or "none observed"): **Ghost-crater sacrifice**
  (damage enemy territory by feeding a capture), **self-crater avoidance** (don't
  capture in your core), and **pie-balanced opening tempo**. These are emergent
  from the rule interactions, not stated.
- Player agency: Higher than any other game here — your cluster shape, your
  capture decisions, the swap decision, and suppression sacrifices all move the
  score. Still, the *decisive* lines were tempo races; I did not prove
  suppression overturns best-play racing, so agency is real but not dominant.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior: At core it's an
  **influence/territory race** (à la Go-influence scoring): build the bigger
  cluster, cross a threshold, first mover edge. A cynic says the capture and
  ghost mechanics are avoidable flavour and the winner is just whoever races
  more efficiently with the tempo (or the swap).
- Honest novelty assessment after arguing that case: The novel parts are *not*
  vestigial here, which separates B from the others. The pie-swap actually
  decided Line 2, and the ghost-influence rule makes capture a double-edged,
  score-relevant decision (Line 3's −2 swing). The fractal board genuinely
  shapes cluster routing. Net: a real, moderately novel influence game — derivative
  in its skeleton but with two mechanics (ghost-crater capture, pie balance) that
  add live strategic content.

## Phase 5 — Verdict

- P1-role experience sub-score (1-10): 3.9 — a real positional build with
  tempo pressure and capture decisions.
- P2-role experience sub-score (1-10): 3.7 — meaningful counterplay (swap,
  suppress), though still chasing the tempo leader.
- Role-averaged sub-score: 3.8
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** **3** — P1 wins the raw
  race by one tempo (Line 1), but the pie-swap lets P2 neutralise exactly that
  edge and win symmetrically (Line 2), so the opening is balanced by design.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 3.8**
- One-paragraph justification of the Overall, citing your Phase 2 lines: This is
  clearly the strongest game I evaluated. It is a coherent influence-threshold
  game on a fractal board where the headline mechanics earn their keep: the
  pie-swap actually flipped the winner (Line 2, P2 31-26), and the
  ghost-influence rule makes capture a genuine double-edged choice that swung P1's
  score by two points off a single enemy sacrifice (Line 3, +2.0 → +0.0). That
  gives the trailing player real counterplay — racing, swapping, or suppressing —
  which the trivial parity/connection games entirely lack. I anchor it below the
  R19/5.0 ceiling because the *decisive* lines were still tempo races and I did
  not demonstrate suppression overturning best-play racing; but its balance (pie)
  and live novelty (ghost-crater) place it at the top of the batch, around the R8
  anchor and clearly above R20/R21 drift. **Overall 3.8.**
