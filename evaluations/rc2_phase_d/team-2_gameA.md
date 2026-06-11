# Team 2 — Game A verdict

## Phase 1 — Rule comprehension

- Mechanics in your own words:
  A 5D **Moore** board, axis_size 3 (243 cells), where Chebyshev-distance-1
  adjacency means the centre cell touches **all 242 others** and even a corner
  has 31 neighbours. Each turn a player makes **3 consecutive placements**
  (multi-place); placements may target empty, enemy (replace), or own (no-op)
  cells, and must be adjacent to one of your stones except while you have none
  (first-move-anywhere). After **every** action a 3-step **cellular automaton**
  runs over the whole board, born/killing/flipping stones by a totalistic table
  keyed to the actor's friendly/enemy neighbour counts — but the table only
  covers counts 0..4, so any cell with >4 friendly or enemy occupied neighbours
  is frozen. Classic capture/influence are disabled. **Win = connection**
  (Hex-style, asymmetric): P1 links the d0=0 face to d0=2; P2 links d1=0 to
  d1=2. Turn-limit tiebreak = more stones; double-pass = draw.
- What actually ends the game / frequency: all 3 of my decisive lines ended by
  **connection win** on the FIRST turn the leader chose to connect. P1 won when
  P1 tried (1 line, 3 plies); P2 won only when P1 deliberately declined (1 line,
  6 plies). No game reached the CA-driven midgame, none drew.
- Surprises: the connection goal needs only **3 collinear stones** along a
  length-3 axis, and a turn grants exactly **3 placements** — so the first
  player connects on turn 1 against an empty board, where the CA is dormant
  (no enemy neighbours to trigger it). The CA itself is wildly destructive once
  stones are adjacent (Line 3), but optimal play ends before it ever matters.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `121,120,122`  (centre, then the two d0 faces through it)
- Plan and what happened: first move anywhere → centre (1,1,1,1,1); the next
  two placements (0,1,1,1,1) and (2,1,1,1,1) are each adjacent to it and put a
  P1 stone on d0=0, d0=1, d0=2 sharing the other four coords → an instant
  connected path. The CA did nothing (no enemy stones exist yet).
- Result: **P1 win, connection, 3 plies — P2 never moved.**

### Line 2 — you as P2
- Moves: `0,9,18,239,236,242`
- Plan and what happened: to even get a P2 turn I had P1 play a deliberately
  non-connecting cluster (three stones all at d0=0). I (P2) then built three
  collinear stones along d1 in the **opposite corner** (d0=2,d2=2,d3=2,d4=2),
  far from P1 so the CA had no enemy neighbours to fire on. P2 connected
  d1=0→1→2. (The CA still spawned P2 stones — P2 ended with 7 from 3 placed.)
- Result: **P2 win, connection, 6 plies — but only because P1 chose not to win
  on turn 1.**

### Line 3 — adversarial / novelty-stress
- Moves: `121,112,130,239,236,242`
- What I tried to break / stress: I had P1 occupy the centre (which is adjacent
  to everything) plus two neighbours, then had P2 attempt its d1 connection near
  that mass. The CA detonated: on P2's second placement the delta wiped all
  three P1 stones AND flipped P2's own freshly-placed stone to P1
  (`O->X@(2,1,2,2,2)`), leaving P2 with 0 stones; P2's connection never formed.
- Result: **no winner / chaos** — demonstrates the CA makes connection near
  enemy/central stones nearly impossible, which is precisely why the clean
  empty-board turn-1 win (Line 1) is the only sane strategy.

### Additional lines (optional)
none needed — the turn-1 forced win settles the game's character.

## Phase 3 — Joint strategic analysis

- Core tactical loop: there isn't one. The "optimal" move is to place 3
  collinear stones along your goal axis on turn 1 and win. Nothing else is a
  decision.
- Counterplay: **none exists** for the second player against correct first-
  player play — P2 does not get a turn before P1 wins (Line 1). The CA, far
  from enabling counterplay, actively sabotages the trailing player who must
  build amid the leader's stones (Line 3).
- Topology effects: the 5D Moore centre-touches-everything property + axis
  length 3 is exactly what makes a 3-stone line a full face-to-face connection,
  collapsing the game.
- Emergent concepts: the CA produces genuinely chaotic birth/death/flip
  cascades — interesting to watch, but causally irrelevant to who wins.
- Player agency: essentially zero. The engine/structure decides (first mover
  wins in 3 plies); my "choices" never mattered beyond choosing to win or not.

## Phase 4 — Novelty adversary

- Strongest re-skin case: it is a Hex-family connection race bolted onto a
  Conway-style cellular automaton on an exotic 5D Moore lattice — the CA layer
  is novel relative to the other games here.
- Honest novelty assessment: the CA + 5D-Moore substrate is genuinely unusual,
  but novelty of *mechanism* cannot rescue a game with a **forced 3-ply first-
  player win and no opponent interaction**. The one length-3 axis plus 3
  placements per turn is a fatal balance break; the elaborate CA never enters
  optimal play. Novel wrapper, broken core.

## Phase 5 — Verdict

- P1-role experience sub-score (1-10): 2.0 (you win instantly, but it's hollow)
- P2-role experience sub-score (1-10): 1.0 (no agency; you lose before moving)
- Role-averaged sub-score: 1.5
- **Fairness perception (1-5):** 1 — Strongly P1-favored: P1 has a forced
  connection on turn 1 (Line 1, 3 plies) and P2 never gets to respond.
- **Overall (1-10, anchored): 1.5**
- One-paragraph justification: Game A is broken in the most decisive way — Line
  1 shows P1 forcing a connection win in three plies on the empty board with no
  possible P2 counterplay, because the connection axis is only length-3 and a
  turn grants exactly three placements. Line 2 only produced a P2 win by having
  P1 voluntarily skip its instant win, and Line 3 shows the much-touted CA is
  either dormant (sparse) or destructively anti-strategic (dense), never a
  source of genuine play. The 5D-Moore-plus-CA machinery is novel to look at but
  irrelevant to the outcome. With zero agency, zero interaction, and a forced
  first-mover win, this sits far below every anchor (R20 3.73, R21 3.69); I
  score it 1.5.
