# Team 3 — Game A verdict

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  5D Moore board, axis_size 3 (243 cells); Moore adjacency means two cells are
  neighbours iff they differ by ≤1 in every coordinate (up to 242 neighbours).
  **Multi-place: 3 actions per turn.** PLACE must be adjacent to one of YOUR
  stones (first move anywhere); placing on an enemy cell replaces it. A
  **cellular automaton fires 3× after every action**, but its table only covers
  friendly/enemy neighbour counts 0..4, so dense cells (the norm in 5D Moore)
  are inert; it only bites in sparse regions. **Win = Hex-style connection**: P1
  connects the d0=0 face to the d0=2 face, P2 connects d1=0 to d1=2. Because
  Moore adjacency lets a single step change one coordinate by 1, **three
  collinear stones spanning d0=0,1,2 already connect P1's faces** — and P1 can
  place all three on turn 1.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw): Connection win
  in 3 plies (P1, Line 1) or 6 plies (P2, Line 2 — only because P1 declined its
  turn-1 win). I also produced a **double-pass DRAW** (Line 3) when CA-nullified
  placements were rolled back to passes. No game reached the turn limit.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: Two surprises. (1) **P1 wins on turn 1, ply 3, before P2 ever
  acts** — the CA does nothing because with no enemy stones present none of its
  destructive transitions match. (2) When P2 places adjacent to a 3-stone P1
  cluster, the CA rule "actor's cell, 0 friendly + 3 enemy → empties" **wipes
  P2's stone the instant it lands**; the resulting no-change is treated as a
  super-ko pass, and two such non-moves ended the game in an accidental DRAW.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `0,1,2`
- Plan and what happened: I placed three collinear stones along d0 —
  (0,0,0,0,0), (1,0,0,0,0), (2,0,0,0,0) — using my 3-action turn. First stone is
  free; second and third are each adjacent to the previous (Moore distance 1).
  The third stone completed the d0=0→d0=2 path and the engine fired the win
  immediately. P2 never moved.
- Result (winner, end cause, plies): **P1 win**, connection, ply 3 — the
  minimum possible. This is a forced first-player win.

### Line 2 — you as P2
- Moves: `0,9,3,236,239,242`
- Plan and what happened: To get a P2 turn at all I had P1 play three
  *non*-collinear stones at d0=0 (cells 0,9,3 — no d0 span, no win). I then drove
  P2 to its symmetric instant win: a d1-line in the far corner — (2,0,2,2,2),
  (2,1,2,2,2), (2,2,2,2,2) — placed away from P1's cluster so the CA wouldn't
  wipe it. P2 connected d1=0→d1=2 on its first turn.
- Result: **P2 win**, connection, ply 6 — but *only* available because P1
  declined its turn-1 win. Against a competent P1 this line never occurs.

### Line 3 — adversarial / novelty-stress
- Moves: `0,9,3,1,10,4`
- What you tried to break / stress, and what happened: I stress-tested the CA by
  placing P2 stones directly adjacent to P1's 3-cluster. Each P2 placement
  (cell 1, then cell 10) was instantly emptied by the CA (0 friendly + 3 enemy →
  empties), reported as "board delta: none," and rolled back as a super-ko pass;
  two consecutive non-moves triggered "double pass → DRAW." So the CA can
  **forbid a player from playing in contested space and even force a draw**, but
  it is a side-effect, not a strategic system anyone engages with — the game is
  already decided on turn 1.
- Result: accidental DRAW at ply 5 — demonstrates the CA/super-ko interaction
  but no genuine contest.

### Additional lines (optional)
The 3-ply P1 win, the symmetric 6-ply P2 win, and the CA-kill draw exhaust the
distinct behaviours; the game cannot produce a contested mid-game under optimal
first-player play.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why): "Place three
  collinear stones along your connection axis on turn 1." There is no second
  idea. Moore adjacency makes a straight 3-line a complete face-to-face
  connection, and 3 actions/turn lets the first player complete it before the
  opponent acts.
- Counterplay: None. P2 cannot respond to a turn-1 win (Line 1). Even given a
  turn, P2's only resource is its own symmetric line (Line 2), and placing near
  the opponent gets CA-wiped (Line 3) — so there is not even a blocking option.
- Topology/board effects on strategy: The 5D Moore topology is the whole
  problem: it makes connection so cheap (3 stones) that the multi-place turn
  hands the first player an immediate win. The dense adjacency also neuters the
  CA almost everywhere.
- Emergent concepts you'd name (or "none observed"): The CA kill-on-contact /
  super-ko-pass interaction is a genuine emergent oddity, but it produces draws
  and non-moves, not play. No strategic emergence.
- Player agency: Essentially none. P1's win is forced and immediate; P2 has no
  turn under optimal play. Outcome is decided by move order, not decisions.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior: It's **Hex/
  connection** with the dimensionality cranked so high that the connection is
  trivial — closer to "first to place 3 in a row on your axis," i.e. a
  degenerate race won outright by the first mover. The CA, multi-place, and 5D
  dressing don't change the playable game: form your line first and win.
- Honest novelty assessment after arguing that case: The *mechanics listed* are
  novel (5D Moore + per-action CA + multi-place + connection), but the *playable
  game* is a forced 3-ply first-player win with zero contest, so the novelty is
  inert — it never manifests as new strategy. Novel parts list, degenerate game.

## Phase 5 — Verdict

- P1-role experience sub-score (1-10): 2.2 — you win instantly, which is hollow.
- P2-role experience sub-score (1-10): 1.4 — under optimal opposition you do not
  get to move at all.
- Role-averaged sub-score: 1.8
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** **1** — P1 wins on
  turn 1 (ply 3) before P2 has any action (Line 1); P2 can only win if P1
  deliberately throws its turn-1 win (Line 2).
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 1.9**
- One-paragraph justification of the Overall, citing your Phase 2 lines: This is
  the most degenerate game I evaluated. Line 1 is a forced first-player win in
  the minimum 3 plies — P2 never moves — because 5D Moore adjacency makes a
  3-stone straight line a complete face-to-face connection and the 3-action turn
  lets P1 finish it first. Line 2 only manufactures a P2 win by having P1 throw,
  and Line 3 shows the CA can outright forbid contested placement and force a
  draw rather than create play. The headline machinery (per-action CA, 5D Moore,
  multi-place) is real but completely unengaged in actual games. With no
  counterplay, no contest, and an instant first-player win, it sits well below
  every anchor and below the parity-race games. **Overall 1.9.**
