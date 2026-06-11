# Team 2 — Game E verdict

## Phase 1 — Rule comprehension

- Mechanics in your own words:
  A 3D **Moore** board, axis_size 4 (64 cells, degrees 7–26). Players
  **alternate single placements** (PLACE; may target empty / enemy-replace /
  own-noop, must be adjacent to one of your stones unless you have none). After
  **every** action a 3-step **cellular automaton** runs over the whole board:
  totalistic from the actor's perspective, it births/kills/flips stones by
  friendly/enemy neighbour counts (table covers 0..4; cells with >4 of a side
  freeze). Classic capture/influence are disabled. **Win = connection**
  (asymmetric): P1 links the d2=0 face to d2=3 (a length-4 axis); P2 links d0=0
  to d0=3. Turn-limit (141) tiebreak = more stones; double-pass = draw. The
  decisive CA entries I hit live: *0 friendly + 1 enemy → your own stone
  empties* (lone stones next to an enemy self-destruct); *3 friendly + 0 enemy
  → empties* (dense friendly blobs self-destruct); *2 friendly(actor) + 1 enemy
  on an enemy cell → flips to actor*; *3 friendly + 1 enemy on actor's cell →
  flips to opponent*.
- What actually ends the game / frequency: my decisive lines ended by
  **connection win** (P1 ply 7 in a clean race; P2 ply 8 when P1 declined). The
  adversarial line ended *no* decisive result at ply 7 — the leader's line was
  shattered mid-build. No draws/turn-limits observed but mutual disruption
  trends that way.
- Surprises: (1) A straight line is the ONLY CA-stable shape — each cell has
  ≤2 friendly neighbours and dodges the 3-friendly self-destruct. (2) You
  **cannot** place a lone disruptor next to an enemy line; it self-empties
  instantly. (3) A single enemy "poison" stone can make every natural bridge
  cell flip to the enemy (3 friendly + 1 enemy), durably denying a reconnect.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `0,60,16,61,32,62,48`
- Plan and what happened: I (P1) raced a straight d2-line in a corner
  (0,0,0)→(0,0,3) while P2 raced its own d0-line in the far corner. The
  straight line is CA-stable (≤2 friendly neighbours per cell), so it survived
  untouched and connected one tempo ahead.
- Result: **P1 win, connection, 7 plies** (P1 4 stones, P2 3).

### Line 2 — you as P2
- Moves: `21,60,22,61,25,62,26,63`
- Plan and what happened: I had P1 build a non-connecting d2=1 cluster (no
  d2=0/d2=3 stone) while I (P2) laid a clean straight d0-line
  (0,3,3)→(3,3,3). With P1 not racing, my line connected d0=0→3.
- Result: **P2 win, connection, 8 plies.** (Note: against a P1 that *does* race
  a corner line, P2 cannot win this way — first mover wins by one tempo; P2's
  realistic winning resource is disruption, Line 3.)

### Line 3 — adversarial / novelty-stress
- Moves: `0,2,16,1,32,4,48`
- What I tried to break / stress: I drove P2 to **sacrifice** stones to shatter
  P1's racing line via CA cascade. P2 placed a supported pair flanking the line
  ((2,0,0) then (1,0,0)) plus a poison stone at (0,1,0). The cascade **emptied
  P1's (0,0,1)** mid-build; even though P2 lost both flanking stones, P1
  reached ply 7 with 4 stones that **no longer connected** (gap at d2=1), and
  the surviving poison stone at (0,1,0) makes every reconnect cell either flip
  to P2 (3 friendly + 1 enemy) or self-empty (3 friendly + 0 enemy).
- Result: **P1's tempo win DENIED** (done=False at ply 7) — genuine counterplay,
  unlike a clean race.

### Additional lines (optional)
Probe `0,63,16,62,32,16`: confirmed P2 cannot reach into P1's corner to replace
a line cell — the constraint requires an adjacent P2 stone, and lone P2 stones
there self-destruct (catch-22).

## Phase 3 — Joint strategic analysis

- Core tactical loop: build a **straight** line toward your face-pair (the only
  CA-stable shape) as fast as possible; deviate only when forced. Every "good"
  move is one that advances the line without creating a 3-friendly cell.
- Counterplay: real but costly. The defender sacrifices stones near the
  leader's line to trigger cascades, and leaves a single **poison stone**
  positioned so the leader's bridge cells flip or self-empty. This genuinely
  delayed/denied P1 (Line 3). The cost is the defender's own tempo and stones.
- Topology effects: Moore adjacency + axis 4 means a connection is 4 collinear
  cells; the high degree makes the CA counts volatile, so contact between the
  two colours is unstable for both sides.
- Emergent concepts: CA-stable straight lines, lone-stone self-destruct, dense-
  blob self-destruct, poison-stone bridge denial, sacrificial cascade.
- Player agency: mixed. Building cleanly is reliably skillful (Line 1), but the
  disruptive midgame turns on intricate multi-step CA cascades that are hard to
  plan precisely — agency is real but murky.

## Phase 4 — Novelty adversary

- Strongest re-skin case: a Hex-family connection race with a Conway-style CA
  bolted on — connection goals are textbook, and the CA is a generic life-like
  rule.
- Honest novelty assessment: genuinely the most novel *mechanics* in this set.
  The CA isn't decorative here (contrast game A, where it never matters): it
  actively shapes strategy — straight-line stability, sacrificial disruption,
  and poison-stone denial are emergent dynamics I produced and exploited at the
  board. Docked because the novelty also brings chaos and a first-mover tempo
  edge with no balancing (pie) rule.

## Phase 5 — Verdict

- P1-role experience sub-score (1-10): 3.9 (reliable but tempo-gifted win)
- P2-role experience sub-score (1-10): 3.4 (interesting disruption, but uphill)
- Role-averaged sub-score: 3.65
- **Fairness perception (1-5):** 2 — Leaning P1-favored: first mover wins clean
  races by one tempo (Line 1, ply 7) with no pie rule; P2's only equaliser is
  costly disruption that doesn't always convert.
- **Overall (1-10, anchored): 3.7**
- One-paragraph justification: E is the mechanically richest game I've seen
  here — Line 3 proves the CA creates real sacrificial counterplay (P2 broke
  P1's racing line and left a poison stone denying every reconnect), which
  lifts it well above the broken sibling game where the CA never matters. But
  Line 1 shows the dominant strategy is still "race a CA-stable straight line,"
  first mover wins that race by a tempo, and there's no pie rule to fix it; the
  disruptive midgame, while genuine, is chaotic and hard to steer deliberately.
  Interesting and contested but imbalanced and noisy — I anchor it right at the
  R20/R21 band, 3.7.
