# Team 3 — Game E verdict

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  3D Moore board, axis 4 (64 cells, degree 7–26; neighbours = Chebyshev
  distance 1). **One placement per turn** (unlike Game A's triple). PLACE must
  be adjacent to one of YOUR stones (first move anywhere); may replace an enemy
  / no-op on own. **A CA fires 3× after every action**, totalistic from the
  acting player's view, with destructive/creative transitions (self-empty,
  flip-to-opponent, spawn, convert-opponent) but only for neighbour counts ≤4.
  Classic capture/influence disabled. **Win = Hex-style connection**: P1
  connects the d2=0 face to d2=3, P2 connects d0=0 to d0=3. Because Moore
  adjacency advances one coordinate per step, a **4-stone straight line** spans a
  face pair. No pie rule; super-ko; double-pass draw; 141-step stone tiebreak.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw): Connection win
  in both decisive lines — P1 @ ply7 (Line 1, clean race), **P2 @ ply8 (Line 2,
  via CA disruption)**. No draws or tiebreaks in my decisive lines. Games are
  decisive, unlike Game D.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: Two things. (1) A **lone stone placed adjacent to a single enemy
  self-empties** (CA "0 friendly + 1 enemy → empties"), so you can't just drop a
  stone next to the opponent. (2) The CA cascades are huge: one P2 placement at
  ply 6 produced a **6-cell delta** that flipped two P1 line-stones to P2 and
  spawned others, swinging the board from P1=3/P2=3 to P1=1/P2=6.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `0,63,16,62,32,61,48`
- Plan and what happened: I drove P1 to race a straight 4-stone line along d2 —
  (0,0,0),(0,0,1),(0,0,2),(0,0,3) — while keeping P2's cluster far away (its
  own d-line in the (3,3,3) corner) so no CA cascade could bridge the two
  groups. The line built undisturbed and completed the d2=0→d2=3 connection.
- Result (winner, end cause, plies): **P1 win**, connection, ply 7 — clean
  tempo race when the opponent can't reach.

### Line 2 — you as P2
- Moves: `0,40,16,41,32,42,17,43`
- Plan and what happened: P1 raced the same d2-line; I drove P2 to build a
  3-stone cluster ((0,2,2),(1,2,2),(2,2,2)) positioned to interact with P1's
  line. On my ply-6 placement the **CA cascaded**: it flipped P1's (0,0,0) and
  (0,0,2) to me and spawned (0,1,1),(1,1,1), leaving P1 with a single stone and
  me with six — including a ready-made d0=0→2 chain. P1 could no longer extend
  (ply-7 line move became illegal), I played (3,2,2) to reach d0=3, and won.
- Result: **P2 win**, connection, ply 8 — a come-from-behind built entirely on
  the CA's flips and spawns.

### Line 3 — adversarial / novelty-stress
- Moves: `0,1,16,21` and the ply-6 cascade from Line 2
- What you tried to break / stress, and what happened: I probed CA
  controllability. A P2 stone dropped next to a lone P1 stone (`...,1,...`)
  **vanished immediately** (self-empty), and the follow-up couldn't manufacture
  the "2 friendly + 1 enemy → flip" I was aiming for. Conversely the Line-2 ply-6
  placement caused a board-flipping 6-cell cascade. So the CA is exploitable
  (build near the enemy line to trigger disruption) but its exact results are
  hard to predict and easy to mis-fire.
- Result: confirmed the CA is both a real weapon and a chaotic one — powerful
  swings, loose control.

### Additional lines (optional)
The far-race (Line 1), the near-disruption (Line 2), and the self-empty/cascade
probes (Line 3) together map the two strategic poles: race when separated,
disrupt when adjacent.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why): If unobstructed,
  race a straight 4-line on your axis (fastest connection, Line 1). If the
  opponent is racing, build a cluster adjacent to their line to trigger a CA
  cascade that flips/breaks it — and harvest the flipped stones toward your own
  connection (Line 2).
- Counterplay: Strong and two-sided — the first player's tempo race (Line 1) is
  answered by the second player's CA disruption (Line 2). This is the only CA
  game in the batch where the CA actually produces contested play rather than
  ending the game before it engages.
- Topology/board effects on strategy: Moore axis-4 makes a 4-stone line a
  connection and gives every cluster many neighbours, which is what powers the
  cascades; the self-empty rule means stones must arrive in supported groups,
  shaping how fronts form.
- Emergent concepts you'd name (or "none observed"): **Proximity disruption**
  (build beside the enemy line to cascade it), **stone harvesting** (flipped
  enemy stones become yours), and **self-empty fronts**. These are genuine
  emergent dynamics, not stated in the rules.
- Player agency: Real but partly luck-laundered — your strategic *intent*
  (race vs disrupt) matters and decides games, but the precise cascade outcomes
  are hard to compute, so some results feel swingy rather than earned.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior: Skeleton is
  Hex/connection again (race a path between opposite faces, first-mover tempo).
  A cynic calls the CA a chaotic noise generator bolted on top of a connection
  race.
- Honest novelty assessment after arguing that case: Unlike Game A, the CA here
  is **load-bearing** — it engages every game and creates a real second strategy
  (disruption/harvest) that actually decided Line 2. That is genuinely novel
  emergent behaviour. The cost is comprehensibility: the rule table is large and
  the cascades are hard to predict, so the novelty comes with the classic CA
  learnability problem.

## Phase 5 — Verdict

- P1-role experience sub-score (1-10): 3.4 — a clean, satisfying race when you
  can stay clear of the opponent (Line 1).
- P2-role experience sub-score (1-10): 3.3 — a real, powerful comeback tool, but
  it fires through a chaotic cascade you can't fully steer (Line 2/3).
- Role-averaged sub-score: 3.35
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** **3** — P1 won the
  separated race (Line 1, ply7) and P2 won via CA disruption (Line 2, ply8), so
  both seats have a winning plan, balanced through chaotic swings rather than
  clean structure.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 3.3**
- One-paragraph justification of the Overall, citing your Phase 2 lines: E is
  the only CA game here where the automaton actually creates a game: P1 wins a
  clean 4-line race by tempo (Line 1, ply7), but P2 can build a cluster beside
  P1's line and trigger a cascade that flips P1's stones and hands P2 the
  material to win its own connection (Line 2, ply8). That two-sided,
  decisive contest puts it well above the trivial races and the draw-prone Game
  D. It falls short of the top because the CA's swings are hard to predict and
  easy to mis-fire (Line 3's self-empty and the 6-cell cascade), the rule table
  is complex (poor rule economy), and there's no pie rule to formalise the
  balance — so good results can feel swingy rather than earned. Novel and alive,
  but chaotic. **Overall 3.3.**

---

## Cross-game comparison (Team 3 — all 7 games)

Ranking by Overall score (high → low):

| Rank | Game | Overall | One-clause justification |
|------|------|---------|--------------------------|
| 1 | **B** | **3.8** | Influence-threshold game on a Menger board where the pie-swap and ghost-crater capture are *live* mechanics that decide games (P2 swap-win; −2 sacrifice swing). |
| 2 | **F** | **3.4** | Clean square-grid Hex with elegant block-equals-connect duality, but P1-imbalanced and its capture/influence extras are vestigial. |
| 3 | **E** | **3.3** | The one CA game where the automaton creates real two-sided play (race vs proximity-disruption + harvest), decisive both ways but chaotic and rules-heavy. |
| 4 | **D** | **2.9** | Torus influence race with genuine positional choice and custodian/ghost tactics, but a win threshold so high every reasonable game saturates into a draw. |
| 5 | **C** | **2.6** | Hex place-adjacent-to-enemy race to 28 stones — a parity/majority fill that P1 wins by one tempo with zero meaningful agency. |
| 6 | **G** | **2.5** | Identical to C plus a strictly-dominated MOVE action and super-ko — extra rules, no extra depth (wasting a move loses by two). |
| 7 | **A** | **1.9** | 5D-Moore CA connection that P1 wins on turn 1 (ply 3) before P2 ever moves; all the novel machinery is inert. |

- Which would you most want to play again, and by how many Overall points?
  **Game B**, by **+0.4** over the next game (F). It is the only game where the
  trailing player has multiple real tools — race more efficiently, pie-swap to
  steal the opening, or sacrifice an invader to crater enemy territory — and the
  opening is balanced by design rather than handed to the first mover.

- The single mechanic or dynamic that most differentiates the top-ranked game
  from the others: **The ghost-influence rule turning capture into a double-
  edged, score-relevant decision.** In B, capturing inside your own cluster
  craters your own influence (P1's two-stone value fell from +2.0 to 0.0 off a
  single sacrificed enemy stone), which—combined with the pie-swap—creates
  genuine give-and-take. Every other game collapses to a first-mover tempo race
  (A/C/G/F), a draw (D), or chaos (E); only B sustains a real positional
  negotiation between the two sides.
