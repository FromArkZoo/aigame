# Team 1 — Game F verdict

## Phase 1 — Rule comprehension

- Mechanics in your own words: 8×8 **grid** (orthogonal/von-Neumann adjacency,
  no wrap), pure PLACE (ids 0–63 = `d0+8·d1`; 64 = PASS; no pie). **Win =
  CONNECTION (Hex-style, asymmetric):** P1 connects the top face (d1=0) to the
  bottom face (d1=7) with an orthogonally-connected path of P1 stones; P2
  connects left (d0=0) to right (d0=7) with P2 stones. Same-tick double
  connection → DRAW. **Capture = surround (Go):** after you place, any adjacent
  enemy group with zero liberties is removed. Super-ko rolls a
  position-repeating move back to a pass. There is an influence field in the
  rule blob (radius 3, decay 0.751) **but it is vestigial** — the win is
  connection and the turn-limit tiebreak is stone count, so influence/ghost
  influence never affect the result.
- What actually ends the game: **connection firing** in every decisive line I
  played (P1 won by a vertical wall in Line 1, P2 by a horizontal wall in Line
  2). Double-pass draw verified (`27,64,64` → DRAW). Unopposed, a straight line
  connects in **8 stones** (verified: P1 column won at ply 15).
- Surprises: (1) **A completed wall both wins AND blocks the opponent** — the
  two goals are coupled, so you cannot "just block," you must out-build. (2)
  **Capture can break a blockade:** I surrounded a P2 stone occupying P1's path
  and removed it (`27,35,34,0,36,1,43` → `O->.@(3,4)`), reopening the column.

## Phase 2 — Strategic play (≥3 full lines, both roles)

### Line 1 — you as P1
- Moves: `3,43,11,51,19,36,27,37,35,38,34,39,42,32,50,40,58`
- Plan and what happened: I (P1) built column 3 top-down (3,0)→(3,4), and when
  P2 blocked the bottom of the column I **detoured into column 2** for the
  lower half, (2,4)→(2,7). P2 raced a right-side row-4 segment but my column
  split its row at x=2/3, so it could never join left-to-right. My vertical
  wall completed first.
- Result: **P1 wins by connection, ply 17 (P1=9 stones, P2=8).**

### Line 2 — you as P2
- Moves: `27,35,19,34,11,36,3,33,28,32,29,37,30,38,31,39`
- Plan and what happened: I (P2) made **every move dual-purpose** — each row-4
  stone simultaneously blocked P1's descent and extended my wall left/right
  (3,4)→ out to both edges. P1 (driven as opponent) tried to descend but each
  time I took the row-4 cell under it; P1 ended up crawling along row 3,
  parallel to my wall, and never punched through. My full row-4 wall completed.
- Result: **P2 wins by connection, ply 16 (full row 4).** (Note: P1's "crawl
  parallel to the wall" is the losing error this line exposes.)

### Line 3 — adversarial / novelty-stress
- Moves: `27,35,34,0,36,1,43` (capture probe) and `27,64,64` (draw probe)
- What you tried to break / stress: (a) **Capture as connection tool** — I let
  P2 plant a blocker at (3,4) astride P1's column, then surrounded it
  ((3,3),(2,4),(4,4),(3,5)) → the blocker was captured and the path reopened.
  (b) **Draw reachability** — double pass returned a clean DRAW. (c) I also
  confirmed the strong P2 counter of **grabbing the central crossing** (3,4)
  immediately after P1's (3,3), which forces P1 off its straight column.
- Result: capture successfully broke a blockade (P2 −1 stone); draw is a real
  outcome; crossing-grab is genuine counterplay.

### Additional lines (optional)
Verified unopposed straight-line connection fires at 8 stones (ply 15). Across
play, the decisive factor was always **execution of the wall fight** — contest
the crossing, and punch *through* the enemy wall rather than crawling beside
it — not a fixed scripted result.

## Phase 3 — Joint strategic analysis

- Core tactical loop: Build a straight wall in your direction; every stone
  ideally also blocks the opponent's wall. The key skill move is to **occupy
  the crossing cell** where your line and theirs must intersect, and to **punch
  a stone through the enemy's wall row/column** and continue past it, forcing
  them into a long detour.
- Counterplay: Strong and two-sided. When P2 grabbed my central crossing
  (Line 3), my straight column died and I had to reroute. When P1 crawled
  parallel to my wall (Line 2) it simply lost. Capture adds a second layer:
  a blockading stone can be surrounded and removed (Line 3), so blockades are
  not permanent.
- Topology/board effects: Orthogonal adjacency on a square grid means the two
  walls must cross at a shared cell, making crossing fights the heart of the
  game — but it also permits genuine **draws** (mutual block / same-tick),
  unlike Hex, which slightly dilutes the decisiveness.
- Emergent concepts I'd name: "crossing control," "punch-through vs.
  crawl-parallel," and "capture-to-reopen-a-blockade." All three appeared in
  actual play.
- Player agency: **High** for this set. My two decisive games went to opposite
  players based on who executed the wall fight better; the loser's blunder
  (crawling parallel) was a real, avoidable mistake. Choices clearly decided
  the result.

## Phase 4 — Novelty adversary

- Strongest re-skin case: This is **Hex re-skinned onto a square grid**, plus
  bolted-on Go surround capture — both well-known. The asymmetric
  top-bottom/left-right goals are exactly Hex/Y/Bridg-it territory, and the
  capture is vanilla Go. The influence field is dead weight (vestigial).
- Honest novelty assessment: **Low-to-moderate.** The *combination* —
  connection race where capture can reopen a blockade — is a real and
  enjoyable twist not present in pure Hex, and it produced emergent tactics in
  my games. But the skeleton is a familiar connection game, and the
  square-grid orthogonal version is strictly less elegant than Hex (it can
  draw). Good game, not a novel one.

## Phase 5 — Verdict

- P1-role experience sub-score (1-10): **4.2** — first-move initiative plus a
  satisfying wall/crossing fight; my Line-1 win felt earned.
- P2-role experience sub-score (1-10): **4.0** — fully competitive (I won
  Line 2 outright), with the same rich crossing tactics, slightly behind on
  initiative.
- Role-averaged sub-score: **4.1**
- **Fairness perception (1–5): 3** — Balanced in practice: both roles won
  decisively in my lines and the result hinged on execution, not seat; there
  is only a mild theoretical first-move (P1) edge typical of pie-less
  connection games.
- **Overall (1-10): 4.1**
- Justification: This is comfortably the strongest game I've evaluated. Lines
  1 and 2 are genuine, decisive games won by *opposite* players through skill
  (wall-building and crossing control), Line 3 shows capture meaningfully
  reopening a blockade and confirms draws exist, and the connection/blocking
  coupling forces real two-sided play rather than a parallel race. It anchors
  near the campaign-top band (R19 top 4.375) but not above it: the core is a
  familiar Hex-on-grid connection game with a vestigial influence field and a
  square topology that admits draws, so I anchor down to **4.1** — a legitimately
  good game, short of anything novel or ceiling-clearing.
