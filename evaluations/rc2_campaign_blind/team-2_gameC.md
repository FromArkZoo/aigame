# Team 2 — Game C verdict

> Copy this template to `team-2_gameC.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game C` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  4×4×4 grid (no wrap), orthogonal adjacency in three axes. Placement is PARASITIC: every stone must be placed adjacent to an ENEMY stone (anywhere while you have zero stones; re-arms if wiped out). Custodian (Othello) capture along all three axis lines: enemy runs from your placed stone that end on your own stone flip to you. Asymmetric Hex goals: P1 connects the y=0 face to y=3, P2 connects z=0 to z=3. Two passes = draw; 100 steps → stone majority; super-ko (provably vestigial here — stones are only added or recolored, never removed, so positions cannot repeat).
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Connection win ×1 (my Line 1, ply 21). Double-pass draws ×2: the ply-3 camping exploit (Line 3) and Line 2's exhaustion draw at ply 34 — with the final material 24 to 0. Turn-limit tiebreak never reached.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: (1) The parasitic constraint is savage in practice: at ply 3 of a probe, P1's legal set was 5 cells, all dictated by P2's single stone — your opponent's stones ARE your mobility. (2) Edge-anchored lines are unflippable (custodian walks need a terminator, and the board edge is not one), which makes face-hugging columns permanently safe. (3) A player at zero stones is offered every empty cell (engine-verified, 40 options) — and can still rationally refuse and pass. (4) Whole-run flips fire through multiple stones at once ((1,0,3) flipped a 2-run to win Line 1... and my Line 2 opponent's stones were flipped to literal extinction).

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `21,25,29,17,18,19,22,37,53,26,23,24,41,57,45,30,34,50,51,28,49` (plus 2 ignored post-win moves)
- Plan and what happened: I opened center (1,1,1); P2 sat under me and my (1,3,1) custodian-flip wiped its only stone (re-arming P2). The game became "flip-tennis": my z-probes ((2,0,2)) were counter-flipped by his z=3 replies, my column was cut by his (0,2,1) flip and reconnected via the (1,2,2)/(1,3,2) exchange sacrifice. The winning idea was edge-anchoring: I took (3,0,3), let him grab (1,0,3)'s neighborhood, and at ply 21 placed (1,0,3) — custodian-flipping (2,0,3) and, decisively, landing a y=0 face stone directly adjacent to my (1,1,3) arm: path (1,0,3)-(1,1,3)-(1,1,2)-(1,2,2)-(1,3,2) spans y=0 to y=3. I won while BEHIND on material 10-11 — connection beats counting.
- Result (winner, end cause, plies): P1 win, connection, 21 plies.

### Line 2 — you as P2
- Moves: `21,5,9,13,25,29,30,31,1,41,28,24,20,8,4,12,64,37,64,2,64,17,64,36,64,40,64,44,64,16,64,0,64,64`
- Plan and what happened: I played the parasitic-starvation strategy: my ply-4 (1,3,0) custodian-flip built an edge-anchored, unflippable z=0 column, and I then answered every P1 flip-attack with the winning side of flip-tennis ((3,3,1) re-flip, (1,2,2) flip taking his column stone) while never placing near the y=0 cells he needed — his y-goal requires MY stones' shadows for legality, and I starved him of them. By ply 16 he was strategically dead (every y=0 approach cell permanently illegal for him). Then the flaw: he camped (passed every turn). I harvested flips until his stones were EXTINCT — final material 24 to 0 — at which point my own placement rule (adjacent to enemy stones, of which there were none) left me passing after his pass. DRAW, at twenty-four stones to zero.
- Result: DRAW, double pass (legality exhaustion), 34 plies, material 24-0 in my favor.

### Line 3 — adversarial / novelty-stress
- Moves: `21,64,64` and legality inspections
- What you tried to break / stress, and what happened: (1) The camping exploit at its purest: P1 places, P2 passes — P1 now has NO legal placement (no enemy stones to attach to; engine shows "Legal actions for P1: 1 total — PASS") and the forced double pass draws the game at ply 3. P2 can veto the entire game unilaterally. (2) Verified P1's ply-33 re-arm options in Line 2 (40 placements offered) — the extinct player's pass is a choice, i.e., the 24-0 draw is a deliberate, rational exploit, not an engine bug. (3) Super-ko: I attempted to design a repetition and proved it impossible — placements strictly add stones and flips only recolor, so board positions can never recur; the rule is dead code in this game. (4) Same-tick double-connection draw: unreachable — your action can only remove opponent path stones, never add them.
- Result: camping line: DRAW at ply 3; all mechanics behaved exactly as documented.

### Additional lines (optional)
Probe `21,25,29,17,18,19,22` + legality dumps — established the flip-tennis motifs (probe → counter-flip → re-flip), that P2 cannot even OCCUPY key blocking cells like (2,0,0) (never enemy-adjacent for him), and that (0,0,1)-style "sneak terminators" can flip entire two-stone runs at once, which nearly punished my Line 2 blocking plan before I saw it.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Every placement is triple-purpose: it must exploit the enemy-adjacency you're given, watch every axis line for custodian flips in both directions (the 4-cell lines make combinations short and sharp), and — most distinctively — manage the LEGALITY SHADOW you cast: each of your stones opens its empty neighbors to the opponent. Good moves are edge-anchored (unflippable), deny the opponent's face-approach shadows, and force him to approach yours. A brilliant local move that hands the opponent a needed shadow is a losing move.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Extremely — this is the most response-dense game of my seven. Every probe near an enemy terminator got counter-flipped one ply later (flip-tennis); my Line-1 column cut at (0,2,1) was answered by a two-ply reconnection combination; his y=3 grab (2,3,1) was refuted by an immediate re-flip. And at the strategic level, the opponent's stone placement IS your option set — you respond to it by construction.
- Topology/board effects on strategy: The 4-length lines make custodian capture razor-sharp (single placements flip 1-2 stones; whole-column flips win games), and the six faces make edge-anchoring the core defensive resource: my winning structures in both lines were face-hugging columns that no walk can terminate against. The 3D-ness gives each player three approach planes, so cuts must be answered in two other dimensions.
- Emergent concepts you'd name (or "none observed"): "parasitic starvation" (deny the opponent legality near their goal face by never placing there), "legality shadows" (stones as mobility grants to the enemy), "flip-tennis" (probe/counter-flip cycles that the better-anchored player wins on material), "edge-anchoring" (unflippable face columns), "camping" (the pass-based draw veto — the game's fatal flaw).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? In engaged play, agency is enormous — my Line 1 win was a 10-ply combinational plan that survived contact, and Line 2's strategic starvation worked exactly as designed. But the final layer of agency belongs to whoever chooses to stop playing: any player can convert imminent defeat into a draw by camping, which retroactively hollows out the agency of everything before it.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  "3D Othello with a Hex win condition": custodian capture is Othello's; enemy-adjacent placement is a relaxation of Othello's must-flank placement rule; asymmetric face-connection goals are Hex's; and my campaign set already contains this exact template (Game A: custodian + Hex goals + adjacency-constrained placement on an exotic board), so C can be framed as a parameter sibling — board swapped, adjacency polarity inverted.
- Honest novelty assessment after arguing that case: The polarity inversion (grow from the ENEMY, not yourself) turns out to be transformative, not cosmetic: it creates the legality-shadow economy, parasitic starvation, and steering — strategic ideas I have not met in any published game, and which dominated both of my competitive lines. The 3D short-line custodian tactics are also far sharper than Game A's (where growth constraints neutered the flips). This is the most genuinely novel-FEELING design of my seven — undermined by the camping degeneracy, which is itself a direct consequence of the novel placement rule and clearly unpatched.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — component genres recognized (Othello custodian, Hex goals); the parasitic placement rule and this specific game are unknown to me; no prior score recalled.
- P1-role experience sub-score (1-10): 5.0
- P2-role experience sub-score (1-10): 4.0
- Role-averaged sub-score: 4.5
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 3 — P1 won my engaged Line 1 while P2 strategically crushed Line 2, and the decisive structural lever (the camping draw-veto) is available to both sides from ply 2 onward, so neither seat is favored; the game is instead tilted toward the player willing to settle for a draw.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 3.9**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  When both players engage, this is the best pure-tactics experience of my seven games: Line 1 is a 21-ply connection win built from flip-tennis exchanges, an exchange sacrifice, and an edge-anchored finishing combination that won from behind on material; Line 2's parasitic-starvation plan (never feed the opponent legality near their goal face) is a genuinely original strategic idea that worked perfectly. But the same placement rule that creates all this also breaks the game: P2 can force a draw at ply 3 by passing (engine-verified), any losing player can camp to a draw, and my Line 2 ended 24-0 — total annihilation — as a DRAW because the extinct player rationally refused to re-arm. A design where dominance that complete cannot be converted must be scored on both truths: R19-caliber engaged play, F-caliber game-theoretic soundness. Net: just below the R8 anchor at 3.9.
