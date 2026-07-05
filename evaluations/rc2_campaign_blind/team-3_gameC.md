# Team 3 — Game C verdict

> Copy this template to `team-3_gameC.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game C` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  4×4×4 grid (64 cells, orthogonal adjacency, 3–6 neighbors). Placements must be adjacent
  to at least one ENEMY stone (anywhere while you have zero stones; re-arms on
  extinction) — so both players are forced to build inside each other's networks.
  Custodian capture on all three axes: after a placement, consecutive enemy stones in a
  line ending on one of your stones flip to you (engine-verified including double-axis
  flips from a single placement). Win by connection: P1 must link the d1=0 face to d1=3,
  P2 must link d2=0 to d2=3 (minimum path: 4 stones). 100-step limit → most stones;
  double pass → draw; super-ko → forced pass.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Connection win twice (Line 1: P1 at ply 7; Line 2: P1 at ply 21). Double-pass draw
  once, at ply 3, in the stress line — see the degeneracy below. No turn-limit games,
  though Line 2 was headed there before my blunder.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules:
  (1) THE BIG ONE: after P1's first placement, P2 can simply PASS — P1 then has zero
  legal placements (no enemy stone to be adjacent to, and first-move-anywhere no longer
  applies since P1 has a stone), so P1 is forced to pass and the game is an immediate
  double-pass DRAW. Engine-verified: `--legal` after `21,64` shows "1 total: PASS".
  Either player can steer any game of C into a draw almost immediately; competitive play
  exists only by mutual consent. (2) Flips chain along multiple axes simultaneously (one
  placement flipped two stones on two different lines). (3) Flip wars are deeply
  non-obvious: in Line 2 a single quiet stone (P1's 4 at (0,1,0)) later enabled a
  two-stone flip along a row (his 7 recaptured two cells at once at ply 19). (4) Flipped
  stones count fully for connection — Line 1's win ran through a re-flipped stone.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `21,37,41,25,29,5,17`
- Plan and what happened: I rushed a straight d1-column at (1,*,1). P2 tried the two most
  natural defenses and both were refuted by custodian tactics: when P2 stole my connector
  at (1,2,1), my placement at (1,3,1) flipped it back (bracketed against my (1,1,1)) —
  gaining the cell AND the tempo; when P2 counter-flipped my (1,1,1) by bracketing it on
  the d2-axis (making a 3-stone P2 column in one move), my reply at (1,0,1) flipped it
  back again along d1 and simultaneously completed the d1=0..3 column.
- Result (winner, end cause, plies): P1 (me) won by connection at ply 7, 5 stones to 2.
  My pre-play analysis found no P2 defense: the enemy-adjacency rule even makes some
  blocking cells ILLEGAL for the defender (they're not adjacent to any P1 stone), while
  flip-backs punish every steal. P1's rush looks close to forced.

### Line 2 — you as P2
- Moves: `21,22,18,5,23,19,9,20,4,0,3,13,6,1,14,10,12,2,7,15,8` (P1 won at ply 21; my scripted 22–24 were ignored)
- Plan and what happened: I tested whether P2 can survive by refusing the race: my early
  (2,1,1) starved P1's column (his extensions weren't enemy-adjacent), and the game became
  a "fortress war": both sides bank flip-immune cells (corners and edge-flanked cells are
  immortal against custodian brackets), avoid any cell with an enemy stone at distance 2
  on a shared axis (instant flip), and snipe: my (1,3,0) flipped his (1,2,0); his (2,1,0)
  flipped my (1,1,0); my (2,0,0) flipped his (2,1,0); then his (3,1,0) flipped BOTH back
  along the d0-row his quiet (0,1,0) had anchored ten plies earlier. Material see-sawed
  from 5–2 him to 6–6 to 12–7 him.
- Result: P1 won by connection at ply 21: his (0,2,0) completed a d1-path through block
  d2=0 that I failed to see — the very cell I had marked as MY next snipe (it flips his
  (0,1,0) and blocks the path) was available to me at ply 20 and I banked a corner
  instead. A traceable, instructive blunder in a genuinely deep position — but P2 was
  behind the whole game even before it.

### Line 3 — adversarial / novelty-stress
- Moves: `21,64,64` and `21,37,33,25,9,20,41`
- What you tried to break / stress, and what happened: (a) Pass-starvation: P2 passed on
  move 2; `--legal` confirmed P1's ONLY action was PASS, and the forced double pass drew
  the game at ply 3 — a guaranteed anti-loss button for P2 (and symmetric options exist
  for P1 by passing first). (b) Multi-axis custodian: I constructed X terminators at
  (1,0,2) and (1,2,0) against O stones at (1,1,2) and (1,2,1); placing (1,2,2) flipped
  both simultaneously along d1 and d2 (engine delta shows both O->X in one action).
- Result: Draw by double pass at ply 3 in (a); double-flip verified in (b), P1 up 6–1.

### Additional lines (optional)
Multiple `--legal` probes during Line 2 corrected my safety analysis twice — the legal
list is essential because placement legality (enemy adjacency) is easy to mis-compute.
The asymmetry that MY placements legalize cells for HIM (and vice versa) creates a
"feeding war": most of Line 2's middlegame was choosing the move that gives the opponent
the least useful new legal cells.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Three interlocking rules govern every move: (1) the tether — you can only place next to
  enemy stones, so every move feeds the opponent new legal cells; good moves feed only
  duplicate-value cells. (2) The E-me-E flip rule — never leave your new stone with an
  enemy stone at distance 2 on any axis, because the flank cell is adjacent to YOUR stone
  and therefore always legal for the enemy: instant flip. Corners and edge-flanked cells
  are flip-immortal and become the currency of the long game. (3) Snipe lines — a quiet
  stone placed two cells from the action (like P1's (0,1,0) in Line 2) turns every later
  friendly placement on that line into a multi-stone flip.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all?
  Intensely — this is the most response-driven game in my set. Every steal in Line 1 was
  punished by a flip-back within one ply; every unsafe placement in Line 2 was sniped;
  and P1's win came from my one unpunished-looking move (banking (3,3,0) instead of
  taking the dual-purpose (0,2,0)). Nothing can be played on autopilot.
- Topology/board effects on strategy: 3D at size 4 means paths are only 4 cells and
  walls are useless (cutting the board needs a 16-cell surface), so all defense is
  flip-based or legality-starvation. Corners (3 neighbors) are absolutely safe;
  face/edge cells partially safe; the 8 interior cells are permanently volatile.
- Emergent concepts you'd name (or "none observed"): "the tether" (enemy-adjacent
  placement), "feeding war" (minimizing the value of cells your move legalizes for the
  opponent), "E-me-E poison cells", "snipe anchors" (distance-2 stones that pre-load
  multi-flips), "flip-back tempo" (steals refunded with interest), "pass-starvation"
  (the degenerate forced draw).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Choices decide everything, at very high
  resolution — Line 2's loss is attributable to one identified wrong move at ply 20.
  But agency is undermined at the meta-level: a rational P2 would always press the
  ply-2 draw button rather than play a losing game, which collapses the whole contest.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  It is 3D Othello mechanics (custodian flips, even the classic flip-back tactics)
  grafted onto a Hex-goal race, i.e., "Othello meets 3D TwixT". Custodian capture is the
  most textbook mechanic in the pack, and 3D connection races are known to collapse into
  first-player rushes precisely because 3D cuts are impossible — which Line 1 reproduced.
- Honest novelty assessment after arguing that case: The ENEMY-adjacency placement
  constraint is the genuinely novel core — I know no published game where every
  placement must touch an opponent's stone, and it single-handedly generates the tether/
  feeding/starvation dynamics that dominated Line 2. That one rule also produces the
  game-breaking pass-draw, so the novelty is real but unfinished: the most original
  mechanic is also the source of the worst degeneracy.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — Othello/3D-connection resemblances are structural
  arguments, not recognition of a specific prior game or score.
- P1-role experience sub-score (1-10): 4.2
- P2-role experience sub-score (1-10): 3.4
- Role-averaged sub-score: 3.8
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 2 — P1 won both competitive
  lines (one in a near-forced 7 plies where every P2 defense was refuted by flip-backs),
  and P2's best practical asset is the degenerate draw button rather than any winning
  plan.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 3.8**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  Per-move, this was the most tactically demanding game I evaluated — Line 2's fortress
  war (immortal corners, E-me-E poison cells, pre-loaded snipe anchors, a two-stone
  recapture ten plies after its anchor was laid) is real depth, and Line 1's
  flip-refuted defenses are elegant. But the game fails at the level of the contest
  itself: P1's rush looks near-forced (Line 1, 7 plies), P2's rational best is the
  guaranteed ply-3 pass-draw (Line 3), and the tether rule that creates all the good
  dynamics also creates that hole. A brilliant tactical kernel inside a broken
  competitive frame: below R20's 3.73 would be too harsh given the depth I actually
  experienced; level with my Game-C-internal weighting at 3.8, just above R21.
