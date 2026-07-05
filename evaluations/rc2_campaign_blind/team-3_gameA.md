# Team 3 — Game A verdict

> Copy this template to `team-3_gameA.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game A` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  9×9 grid shaped as a level-2 Sierpinski carpet: 17 hole cells (the 3×3 center and each
  sub-block's center) are never playable and block both adjacency and capture lines.
  Players alternate placing stones; a placement must be adjacent to one of YOUR stones
  (first stone anywhere; the constraint re-arms on extinction). Capture is custodian
  (Othello-like): after a placement, along each axis-aligned line, consecutive enemy
  stones ending on one of your stones flip to your colour — holes and empty cells
  terminate the walk without flipping (engine-verified). Win is connection with crosswise
  goals: P1 connects the x=0 face to x=8, P2 connects y=0 to y=8. 100-step limit with
  most-stones tiebreak; double pass draws; super-ko converts repeats to a pass.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  All three lines ended by the connection win condition: ply 18 (P2, Line 1), ply 18
  (P2 = me, Line 2), ply 27 (P1 = me, Line 3). No turn-limit tiebreaks or draws.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules:
  (1) In both competitive lines, ZERO custodian flips fired — the own-stone adjacency
  constraint means you can almost never reach the far side of an enemy run to bracket
  it, so the headline capture mechanic is nearly inert in normal play. (2) Holes block
  flip lines cleanly (placing (3,1) over an enemy at (3,2) with the (3,3) hole below
  produced no flip). (3) Edge-anchored runs are permanently flip-proof (no cell beyond
  the edge to bracket from), so corridor walls anchored to a face are absolute. (4)
  Flipped stones immediately serve the flipper's connection path and grant placement
  adjacency — my Line 3 winning path ran straight through four freshly flipped stones.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `22,38,21,29,23,20,12,11,3,2,24,47,25,56,26,65,33,74`
- Plan and what happened: I seeded the double-fortress cell (4,2) (holes above and below
  make it vertically unbracketable) and grew along the row-2 corridor. Scripted P2
  counter-seeded (2,4) in column 2 — whose middle cells (2,3),(2,4),(2,5) are all
  flip-proof thanks to flanking holes — cut my corridor at the (2,2) crossing, and won
  the pinch fight at (2,1)/(2,0): the (1,1) hole means my only western detour ran
  through exactly the cells P2 needed anyway. Once (2,0) was P2's, my west was
  unreachable (rows 3–5 are hole-blocked, row 0/1 sealed), and P2's column, anchored to
  the top edge, was unflippable. I completed my eastern half and made waiting moves.
- Result (winner, end cause, plies): P2 won by connection at ply 18 with a complete
  column 2 (y=0..y=8). Piece count 9–9; the game was decided by corridor geometry around
  ply 8, not material.

### Line 2 — you as P2
- Moves: `58,42,57,51,59,60,68,69,77,78,56,33,55,24,54,15,47,6`
- Plan and what happened: Scripted P1 seeded (4,6) and rushed the row-6 corridor. I
  played the exact transpose of Line 1's winning pattern: counter-seeded (6,4), cut the
  crossing at (6,6) first (P1's central seed wastes tempo growing both directions), then
  used the (7,7) hole pinch to seal P1's southeastern detour — my (6,7) both blocked
  P1's only bypass and advanced my column. After my (6,8) anchor, P1's route to x=8 was
  provably unreachable (its organism could never grow past my full column-6 wall, and
  every potential flip of my wall cells was blocked by holes, my own flanking stones, or
  the edge anchor), so P1 pivoted west while I filled in column 6.
- Result: P2 (me) won by connection at ply 18 — mirror image of Line 1, confirming the
  counter-seeder's structural edge.

### Line 3 — adversarial / novelty-stress
- Moves: `20,21,11,22,12,23,3,24,4,15,5,33,6,42,7,51,8,60,17,69,26,78,25,59,19,68,18`
- What you tried to break / stress, and what happened: A scripted probe of the capture
  engine (P2 played demo-cooperative moves; noted as such). (a) Hole-blocking: at ply 5
  I placed (3,1) directly above an enemy stone whose far side is the (3,3) hole — no
  flip, confirming holes terminate custodian walks. (b) Mega-flip: I grew a ring via
  row 0 and column 8 around P2's row-2 run and at ply 23 placed (7,2), bracketing four
  consecutive enemy stones against my (2,2) — all four flipped in one action (engine
  delta: O->X at (3,2),(4,2),(5,2),(6,2)). (c) Flip-as-connection: at ply 27 I completed
  x=0..x=8 along row 2 THROUGH the four flipped stones — flips instantly count for the
  flipper's path. Also confirmed a placement adjacent only to enemy stones is illegal
  (adjacency is to YOUR stones, unlike Game-family variants where any stone works).
- Result: P1 (me) won by connection at ply 27, 18 stones to 9 after the 4-stone swing.

### Additional lines (optional)
Short `--legal` probes confirmed the initial anywhere-placement (65 actions) and that
growth cells are strictly own-adjacent thereafter.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Pick a corridor (rows 0/2/6/8 for P1, columns 0/2/6/8 for P2 — the only hole-free
  lines), seed near its fortress cells (cells flanked by holes can never be flipped or
  bypassed), and race: every move should either extend your corridor, take a crossing
  cell that doubles as a block, or anchor a run to a board edge where it becomes
  flip-proof. The best moves are the pinch cells next to holes — one stone there blocks
  the opponent's only detour AND advances your line.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all?
  The crossing fight is genuine: P2's (2,2) cut in Line 1 had to be answered instantly,
  and my failure to contest (2,1)/(2,0) early was the loss. But once one player wins the
  single contested crossing, the loser has no second theater: rows 3–5/columns 3–5 are
  hole-blocked, flips are unreachable under the adjacency constraint, and the game plays
  out as a foregone race. Counterplay is front-loaded into roughly plies 4–10.
- Topology/board effects on strategy: The Sierpinski carpet is the star: it reduces each
  player to four viable corridors, creates flip-proof fortress cells and one-cell
  pinches (the (1,1)-type holes), and makes the center totally dead. It also strangles
  the capture mechanic — most bracket cells either don't exist (holes) or can't be
  reached (adjacency).
- Emergent concepts you'd name (or "none observed"): "fortress cells" (hole-flanked,
  unflippable), "pinch points" (hole-adjacent cells whose occupation kills the only
  detour), "edge anchoring" (runs touching a face are flip-immune), "corridor race",
  "flip-through" (Line 3's rebuilt corridor through flipped enemy stones — spectacular
  but requires an encircling ring that competent opponents never allow).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Choices decide it, but early: seed placement and
  the first crossing skirmish determine the winner around ply 8–10 of an 18-ply game;
  after that both sides execute forced fills. High agency, short decision horizon.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  It is a Hex-goal connection race (crosswise faces, exactly as in Gale/Bridg-It) bolted
  onto Othello's custodian capture, played on a Sierpinski-carpet maze. Each element is
  textbook; the corridor race resembles maze-racing abstracts, and since flips almost
  never fire in real play, the "novel" capture layer effectively evaporates, leaving a
  known connection race on an unusual board mask.
- Honest novelty assessment after arguing that case: The fractal board genuinely
  reshapes strategy (fortresses, pinches, four-corridor structure) in a way I haven't
  seen in a published connection game, and the own-stone growth constraint gives it an
  organism-growing feel distinct from free-placement Hex. But the three mechanics
  under-interact: the marquee capture rule is structurally suppressed by the other two
  rules, which reads as an unintended near-vestigial combination rather than design
  synergy. Moderate novelty of setting; low novelty of experienced play.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — resemblances argued in Phase 4 are structural; I do not
  recognize this specific game or any prior score for it.
- P1-role experience sub-score (1-10): 3.8
- P2-role experience sub-score (1-10): 4.3
- Role-averaged sub-score: 4.05
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 4 — the counter-seeder (P2)
  won both competitive lines by choosing its corridor after seeing P1's seed and winning
  the single crossing fight with the tempo that choice buys; P1's only line win came in
  the scripted stress demo.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.0**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  The Sierpinski terrain produces one genuinely good idea — corridor races through
  fortress cells and hole pinches — and Lines 1/2 show a real, learnable opening fight
  (my Line 1 loss traces exactly to conceding (2,1)/(2,0); my Line 2 win to taking the
  crossing first). But the game is effectively over by ply ~10 of an 18-ply race, the
  custodian capture mechanic almost never fires under the adjacency constraint (0 flips
  across both competitive lines — Line 3 needed a cooperative script to show a 4-stone
  flip), and the second player's counter-seed advantage looked decisive. Shorter
  decision horizon and weaker mechanic synergy than the pack's stronger entries; anchors
  just below R8's 4.10 at 4.0.
