# Team 1 — Game D verdict

> Copy this template to `team-1_gameD.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game D` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  4×4×4 grid, von Neumann adjacency. The signature rule: every placement must be adjacent to at least one ENEMY stone (first stone anywhere; re-arms if you're wiped) — your opponent's stones are the only soil you can grow on, so your mobility is largely your opponent's choice. Othello-style custodian capture along the three axis lines flips runs of enemy stones bracketed by the placed stone and an existing own stone. Win by connection: P1 joins the y=0 and y=3 faces, P2 the z=0 and z=3 faces. 100-ply limit with stone-count tiebreak; two consecutive passes draw the game regardless of count; super-ko.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  One connection win (line 2: P2 at ply 10), two double-pass draws of structurally different kinds: line 1 ended as a "starved draw" at ply 18 with P2 holding 12 stones to my 1 (P2 dominated the flip war but could not legally descend below z=2 because I had no stones there to serve as soil, and I had no useful placements left — the count-blind draw rule ended a 12-1 game as a tie); line 3 ended at ply 5 as a "spite-pass draw" (see below). No turn-limit tiebreak.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: The rules read cleanly and the engine matched them, but the CONSEQUENCES kept surprising me: (1) a placement I read as a simple block flipped my stone because the blocker's own earlier stone silently anchored the line (line 2, ply 3 — I was wiped to zero and re-armed); (2) after you custodian-wipe your opponent to zero stones, YOU have no legal placements (no enemy stones to be adjacent to) — engine-verified: my legal list was exactly {PASS} — so the wiped player can pass and FORCE a draw (line 3: 3 stones vs 0, winner DRAW). A wipe is anti-winning unless you've already connected. (3) Flip-defense cells are often only attacker-accessible: twice in line 2 the defender could not legally occupy the cell that would parry a flip, because that cell was adjacent only to the defender's own stones.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `0,63,59,58,54,50,55,51,53,52,64,1,64,4,64,16,64,64`
- Plan and what happened: I opened corner (0,0,0) planning the flip-proof y-column (0,·,0); scripted P2 opened the opposite corner and anchored the z=3 plane with (3,3,3)+(2,2,3). Everything I placed near their wall sat on a line into one of their anchors and was custodian-flipped within a ply ((2,1,3) eaten via (2,0,3); my (3,1,3)+(3,2,3) eaten in one double-flip via (3,0,3); my (1,1,3) eaten via (0,1,3)). Down to one stone, I switched to the starvation defense: I refused to place (passing), P2 exhausted the three soil cells around my (0,0,0), and then had no legal placements either.
- Result (winner, end cause, plies): DRAW, double pass at ply 18, P2 ahead 12-1 on material but unable to convert: with no P1 stones below z=2, P2's z-connection was unreachable, and the draw rule is count-blind. My corner column never got built — P2 simply never placed a stone near it, and my own placements legally required contact with P2.

### Line 2 — you as P2
- Moves: `21,37,53,5,1,22,6,7,38,54`
- Plan and what happened: Scripted P1 opened the center; I capped his stack plan — and immediately ate the counterpart lesson: his (1,1,3) flipped my (1,1,2) through his (1,1,1) anchor, wiping me to zero (first_move_anywhere re-armed, engine-flagged). I rebuilt from underneath at (1,1,0) — z-flip-proof against the board edge — then raced a fresh column at (2,1,·): his z=0 block at (2,1,0) was flipped back by my (3,1,0) through my (1,1,0) anchor (a flip he could not pre-empt: the cell (3,1,0) was adjacent only to HIS stone, so only I could ever place there); his close-block at (2,1,2) was flipped by my (2,1,3), whose placement simultaneously completed the column.
- Result: P2 (me) win by connection at ply 10 — path (2,1,0)-(2,1,1)-(2,1,2)-(2,1,3), the last two cells acquired by custodian flips. I note honestly that P1 had a stronger ply-9 defense (blocking (2,1,3) rather than (2,1,2), which my analysis shows survives the immediate flip and forces me into a longer starvation fight); the block-the-nearer-cell move my script chose is natural but loses to two-ply custodian reading.

### Line 3 — adversarial / novelty-stress
- Moves: `0,1,2,64,64`
- What you tried to break / stress, and what happened: The wipe endgame. X anchored (0,0,0), O (cooperatively scripted) placed adjacent at (1,0,0), and X's (2,0,0) custodian-flipped O's only stone — O wiped to zero. Probes: (1) O's re-arm confirmed (legal = all empty cells); (2) O instead passed — and X's legal list collapsed to exactly {PASS}, because with zero enemy stones on the board X has no legal placement targets; (3) X's forced pass completed the double pass: winner DRAW at 3-0. This is the "spite-pass" degenerate: any player wiped below one stone can immediately force a draw, so total capture is self-defeating unless your connection is already complete. Illegal-move handling (non-enemy-adjacent placements) was verified repeatedly and organically in lines 1-2 (engine rejected them with decoded messages and legal samples).
- Result: DRAW, double pass, ply 5, 3 stones to 0.

### Additional lines (optional)
None — but note that line 2's plies 3-4 double as an organic wipe/re-arm verification (I was flipped to zero and legally re-placed anywhere), so all three re-arm paths in the rules text are engine-confirmed across my lines.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Anchor-first custodian play: a stone is only safe if, on every axis line through it, the far side is board edge, your own stone, or unreachable to the enemy; a good placement simultaneously extends your path AND sits anchored. The deeper loop is soil control: every move you make is also a gift of adjacency to the opponent, so strong moves give soil that is useless to the opponent's face-pair while taking soil that serves yours. The strongest single pattern I found: place the bait so that the opponent's natural block is on a line into your anchor, then flip the block — twice in line 2 the flip also completed my path.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? The game is ALL response — you literally cannot move except where the opponent is. Punishments were sharp: my line-1 approaches were each eaten within one ply by pre-set anchors; P1's blocks in line 2 were each flipped because the geometry let me anchor first. And the meta-counterplay is refusal: in line 1 I stopped feeding the flip engine entirely, and P2's 12-stone attack starved.
- Topology/board effects on strategy: Corners and edges are custodian sanctuaries (lines ending off-board can never be flipped), which makes corner columns the natural path plans; the 4×4×4 scale means minimal paths are only 4 cells, so a single flip often swings a whole connection; and the third dimension enables quarantine — a player can keep an entire z-band empty of their stones, making the opponent's crossing legally impossible rather than merely blocked.
- Emergent concepts you'd name (or "none observed"): "Soil control" (the opponent's placements are your mobility budget); "anchor warfare" (corner stones project flip-threat down three lines); "attacker-only defense cells" (the parry square is often adjacent only to the defender's stones, hence unplayable by the defender — a lovely structural asymmetry); "quarantine/starvation" (win-denial by refusing presence in the opponent's needed band); "spite-pass draw button" (wiping the enemy disarms yourself); "count-blind draw" (12-1 ends as a tie).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? High agency move-to-move — every result in my lines traces to identifiable decisions (my line-1 opening fed their anchors; my line-2 rebuild exploited the attacker-only-defense asymmetry). But the OUTCOME SPACE is compressed by the draw attractors: between two players who both understand quarantine and spite-pass, most games likely end drawn, and that's a structural property, not a skill failure.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  Othello/Reversi in 3D with a Hex win condition: custodian capture is Othello's exact mechanic (including the flip-on-placement-only rule), "must place adjacent to enemy" is reminiscent of Reversi's own placement flavor (in Othello you must place adjacent to enemy stones too — every legal Othello move touches an enemy line!), and connection goals are Hex boilerplate. Under this reading D is "3D Othello where you win by connection instead of majority."
- Honest novelty assessment after arguing that case: The Othello comparison is the strongest re-skin case in my slate and deserves respect — the placement rule really is Othello's DNA (though Othello requires the placement to FLIP something, which this game does not, and that difference is load-bearing: non-flipping contact placements are the game's positional vocabulary). What Othello has no analogue for: connection goals orthogonal per player, the soil/quarantine dynamic (impossible in Othello where the board fills), starvation draws, and the wipe-disarms-you property. The composite plays like nothing I know: the closest experience is Othello endgame parity logic stretched into a Hex race. Real novelty above the parts, tempered by the strong single-mechanic precedent.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — custodian capture is obviously Othello-derived (disclosed as a mechanic recognition, not a game identification), and I recall no prior score.
- P1-role experience sub-score (1-10): 3.5 — being out-anchored in line 1 was instructive but bleak: once behind in the flip war, my best move was literally to stop playing, and the "reward" was a 12-1 draw.
- P2-role experience sub-score (1-10): 4.5 — line 2 was the best tactical sequence of my D experience: wiped at ply 3, re-armed, and won at ply 10 with two anchor-flips the defender structurally could not parry.
- Role-averaged sub-score: 4.0
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 3.5 — the second player picks the contact geometry (their free stone dictates where P1 may legally play next, as my line-1 opening demonstrated painfully), and P2 won or draw-dominated all three lines, but the sample also shows the first mover getting strong early flips (line 2 ply 3), so I read it as mildly P2-leaning rather than structural.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.2**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  Game D contains the most original non-CA rule of my slate — enemy-adjacent placement — and it generates genuinely new strategy: soil control, quarantine, and the attacker-only-defense asymmetry that decided line 2 are concepts I've never needed in any prior game, and every tactical claim I make is engine-verified (the double-flip, the wipe/re-arm, the forced spite-pass). It also has the slate's most serious structural problem: three independent draw attractors (starved draw at 12-1 in line 1, count-blind double pass, and the spite-pass button in line 3) sit not in corner cases but at the heart of competent play, and my analysis suggests careful players converge on mutual starvation. Depth and originality argue for more; the hollow equilibrium argues down. 4.2 — above R8, below R19.
