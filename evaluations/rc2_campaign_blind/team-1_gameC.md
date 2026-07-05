# Team 1 — Game C verdict

> Copy this template to `team-1_gameC.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game C` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  4×4×4 orthogonal grid. Placement is free only while you have zero stones
  (re-arming if annihilated); otherwise every placement must be adjacent to
  an ENEMY stone — you can never reinforce your own structure, only engage
  the opponent's. After each placement, Othello-style custodian capture
  runs along the three axis lines: consecutive enemy stones ending on your
  stone flip to your colour (stones are never removed, only flipped).
  Hex-style asymmetric connection wins: P1 joins the d1=0 and d1=3 faces,
  P2 joins d2=0 and d2=3. 100-step limit (most stones), double pass draws.
  Super-ko exists in the rules but is provably dead here: occupancy grows
  monotonically (no removals), so no position can ever repeat — verified,
  it never fired in any line.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Connection wins in both main lines (P2 at step 20 in each), double-pass
  draw in the stress line (step 10). The turn-limit tiebreak is nearly
  unreachable: the board fills by ~ply 64 forcing a double-pass draw first.
  My analysis branches also found "gate-locked" dead positions where BOTH
  players' winning cells are permanently illegal (no enemy stone adjacent,
  and the opponent will never provide one) — one branch reached 26 stones
  vs 6 and was still a forced draw.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: (1) A player can be annihilated entirely by a single flip
  (lone stone flanked) — verified: P1 hit zero stones and re-armed with an
  anywhere placement. (2) Placing INTO an enemy sandwich is safe (flips
  only fire for the mover), which makes wedge blocks possible. (3) The
  engine checks connection after flips, so a placement can win by flipping
  distant stones — both my decisive lines ended this way. (4) Multi-stone
  runs flip together (his ply-12 move in Line 2 flipped two of my stones
  through a 2-run ending on his anchor), which repeatedly out-read me.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `0,63,62,61,60,44,28,29,45,46,13,41,30,25,9,10,26,27,22,42` (P2
  wins at step 20; the tail of my scripted continuation was never reached)
- Plan and what happened: I opened on an unflippable corner and applied
  edge-lane theory: corner and face-end stones are immune to flips along
  the axes that run off-board, so the four edge-lanes per player are the
  flip-safe express routes. I won several tactical exchanges (my 28 flipped
  his 44; my 13 flipped his 29) and sealed his obvious lanes. But in the
  central flip-war I lost track of his quiet z-column: his 25/10 plus a
  three-way flip fight over cell (2,2,1) ended with his ply-20 placement at
  (2,2,2) flipping the contested stone one final time and completing
  10–26–42–46–62, a z0→z3 column I had physically watched being assembled.
- Result (winner, end cause, plies): P2 wins by connection at step 20 of
  100; stones 10–10.

### Line 2 — you as P2
- Moves: `21,42,26,10,58,57,56,22,25,29,18,17,41,45,61,62,63,37,9,53`
- Plan and what happened: Mirroring Line 1's lesson, I built the same kind
  of protected z-trunk (10–26–42) — my ply-4 stone at 10 flipped his
  probing 26 into my column using my 42 as the anchor. Midgame highlights:
  his 17 flipped two of my stones with one placement (2-run to his 29
  anchor); my 62 threatened a winning flip of his 58; his only defense was
  the counter-flip 63 (I verified his direct block at 54 is ILLEGAL for
  him — no friendly-enemy adjacency — a beautiful "gate" moment); I pivoted
  to a second trunk: 37 (flipping his 41 off my 45 anchor), then 53, which
  connected 10–…–21–37–53 through cells his stones had been forced to
  ungate for me.
- Result: P2 (me) wins by connection at step 20 of 100; stones 10–10.

### Line 3 — adversarial / novelty-stress
- Moves: `21,22,64,20,63,62,61,46,64,64`
- What you tried to break / stress, and what happened: (1) Flip-to-zero:
  his 20 flanked my lone 21 and flipped it — P1 at ZERO stones (engine
  showed X→O with P1=0). (2) Re-arm: my next placement was legally made at
  the far corner 63, adjacent to nothing. (3) Own-anchor flip: my 61
  flipped his 62 back using my just-placed corner as the anchor. (4) Clean
  double-pass draw at step 10. (5) Confirmed across all games that
  super-ko never fires (no removals → monotone positions).
- Result: DRAW by double pass, step 10; every probe behaved per the rules
  text.

### Additional lines (optional)
Analysis branches (helper-verified, not all engine-run to terminal) found
the game's signature pathology: mutual gate-lock, where both sides'
completion cells are permanently illegal because placement requires enemy
adjacency and neither player will ever place next to the opponent's needed
cells. One such branch reached P1 26 stones vs P2 6 — a crushing material
lead that is still a dead draw. Blocking moves systematically UNGATE the
opponent (your new stone gives them placement rights beside it), which is
why several of my "obvious" defensive moves were refuted.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Build a face-to-face column whose cells are anchored by your own stones
  along the flip axes (so enemy wedges flip to YOU), while placing only
  moves that do not ungate the opponent's key cells. The best moves are
  triple-purpose: legal harassment (enemy-adjacent by rule), flip material,
  and quiet column progress. Corners and face-end cells are eternally
  yours — claim the relevant ones early.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? The whole game is response:
  placement legality REQUIRES touching the enemy. Wedges get flipped by
  anchor parity (my 28 punished his 44 instantly); blocks get flipped by
  ladder-anchors or refuted because they ungate; over-extension hands the
  opponent flip fodder. The deepest counterplay was Line 2's 63: the only
  defense to my 62-anchor threat was flipping the anchor itself.
- Topology/board effects on strategy: 4-cell lines mean flip runs are
  short (1–2 stones) and edge/corner immunity dominates — the geometry is
  really about which cells CAN'T be flipped. 3D means each cell sits on
  three lines, so anchor threats come from unexpected axes (this beat me
  twice). The enemy-adjacency rule glues both players into one crawling
  melee; empty quadrants are unreachable until someone is dragged there.
- Emergent concepts you'd name (or "none observed"): "gates" (cells
  legally unreachable until the enemy approaches — the game's core
  currency), "self-ungating blunder" (a block that legalizes the
  opponent's win), "anchor parity" (who owns the far end of a line decides
  every wedge war), "flip-to-zero annihilation", "edge-lane immunity",
  "gate-lock draw" (mutual frozen completions).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Choices decide everything, and the
  skill ceiling is real: every loss in my lines traces to a concrete
  readable error (missing a 2-run flip, missing that a block ungates a
  cell). Unlike the CA games, the causality is human-followable —
  Othello players would recognize the discipline — though 3D anchor
  geometry takes practice.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  It is Othello capture mechanics (custodian flips, threshold vestigial)
  bolted onto a Hex-style asymmetric connection win — both ancient
  mechanisms — on a 4×4×4 board. "Flip games" and "connection games" are
  both saturated genres, and 3D Othello variants exist.
- Honest novelty assessment after arguing that case: The synthesis plays
  like neither parent: connection-Othello with the enemy-adjacency
  placement constraint produces the gate economy (you can never develop
  privately, defense requires legal contact, blocks ungate the attacker),
  which I have not seen in any published game and which dominated every
  line I played. Custodian flips serving connection (not majority count)
  also invert Othello instincts — flips are路径 surgery, not material.
  Genuinely novel as a system despite familiar parts. Moderate-to-high
  novelty.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — components are recognizably Othello/Hex
  family, but I do not recognize this specific game or recall a score.
- P1-role experience sub-score (1-10): 4.2
- P2-role experience sub-score (1-10): 4.5
- Role-averaged sub-score: 4.35
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 3.5 — P2 won both
  decisive lines (once against me, once as me), and in both the winner was
  the responder profiting from the mover's forced contact, hinting at a
  mild second-player lean; but the axes are structurally symmetric and my
  Line-1 loss traces to identifiable misreads, so the evidence is weak.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.5**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  Game C is the strongest entry in my set: it combines Game B's human
  legibility with genuine mechanical novelty, and both decisive lines were
  taut, readable, 20-ply knife fights that ended with placements flipping
  the winning path into existence (his 10–26–42–46–62 column in Line 1;
  my 37/53 trunk in Line 2). The gate economy — placement requiring enemy
  contact — is a real design discovery: it manufactures constant contact,
  makes defense a privilege you must earn, and produced the most
  interesting refutations I saw all campaign (his 54-block being simply
  ILLEGAL in Line 2). Held below the ceiling by its draw pathology: gate-
  locked positions where even a 26–6 material lead is a dead draw, and a
  turn-limit tiebreak that fill-dynamics make almost unreachable. Above
  R19's 4.375: 4.5.
