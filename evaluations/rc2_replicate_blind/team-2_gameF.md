# Team 2 — Game F verdict

> Copy this template to `team-2_gameF.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game F` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  9×9 board in a Sierpinski-carpet pattern: 64 active cells, 17 holes (the central 3×3 plus each sub-block's center) that are unplayable and block adjacency. Orthogonal adjacency only. Players alternate placements; a placement must be adjacent to one of YOUR OWN stones (waived at zero stones, re-arming if wiped out) — so each side grows a connected "snake" from a freely chosen seed. Custodian (Othello) capture runs along both axes from each placement. Win by connection: P1 joins the x=0 face to the x=8 face, P2 joins y=0 to y=8. PASS always legal; two consecutive passes = draw; 100-step limit with most-stones tiebreak; super-ko rollback rule present.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  All three lines ended by the connection win condition (Line 1: P1 at ply 17; Line 2: P2 at ply 18; Line 3: P1 at ply 27). No turn-limit tiebreaks or draws occurred; competitive games finish in ~18 of the 100 allotted steps. As in the other custodian game I evaluated, stone count is monotone non-decreasing, so the super-ko rule is unreachable dead code.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: (1) The custodian capture — nominally a headline mechanic — fired ZERO times across both competitive lines; the hole walls and board edges kill almost every bracket line, so competent play is nearly flip-free. I had to construct Line 3 deliberately to see a flip at all. (2) The board's degree structure dominates: my first probe opener (4,0) turned out to have only two neighbors (holes), leaving P1 with exactly 2 legal moves at ply 3 — the engine's tiny legal lists made the corridor geometry vivid. (3) A flip that cuts a snake can leave the victim alive but with zero legal placements: in Line 3 the engine showed "Legal actions for P2: 1 total: PASS" while P2 still had a stone — permanent paralysis with no re-arm. (4) Flips fire only on placement: a bracket formed BY a flip does not itself flip (P2's (1,2) sat between two X stones, immortal).

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `24,56,23,47,22,38,21,29,20,28,19,27,18,65,25,74,26`
- Plan and what happened: I opened at the degree-4 cell (6,2) aiming at row y=2 (one of only four rows that pass the x=4 chokepoint). Scripted P2 played the transpose-mirror plan (seed (2,6), column x=2). The plans collide at (2,2) — on my row and his column. Racing west, I reached (2,2) at ply 9, exactly one tempo before his snake (his stone (2,3) arrived ply 8; mine won the cell). His column was then dead northward: my completed row (with hole-protected cells — (x,1)/(x,3) bracket pairs mostly blocked by holes) is an unbreakable wall, and I verified he could reach neither (0,1) nor any bracket anchor. His rerouting via (1,3),(0,3) was walled by my (1,2),(0,2). I completed the full y=2 row at ply 17.
- Result (winner, end cause, plies): P1 (me) win, connection, ply 17. Zero flips occurred.

### Line 2 — you as P2
- Moves: `24,20,23,11,22,2,21,29,25,38,26,47,33,56,42,65,51,74`
- Plan and what happened: Same P1 opener (6,2), but as P2 I played the refutation my Line 1 analysis suggested: the cross-block (2,2) — seeding MY column x=2 directly on P1's key row, far from his seed. Own-adjacency makes the local defender faster: I won (2,1) and (2,0) trivially (adjacent to my seed) while his snake crawled west; his bracket resources were dead — (1,0) and (1,2) are unreachable for a blob east of my column, and my mid-column corridor (2,3),(2,4),(2,5) is walled by holes on both sides, unflippable and unapproachable. P1 salvaged his east face (8,2 at ply 11) but could never cross column x=2; I marched the column down and completed y=0→y=8 at ply 18.
- Result: P2 (me) win, connection, ply 18. Zero flips occurred.

### Line 3 — adversarial / novelty-stress
- Moves: `0,9,1,18,2,19,11,81,20,81,29,81,28,81,27,81,3,81,4,81,5,81,6,81,7,81,8`
- What you tried to break / stress, and what happened: I forced the dormant capture mechanic to fire and probed its consequences. P2 seeded adjacent to P1's corner and built a 2-stone column run (0,1),(0,2) plus (1,2); I snaked around through (2,1),(2,2),(2,3),(1,3) and placed (0,3): the engine flipped the whole run ("O->X@(0,1) O->X@(0,2)") — custodian works and multi-stone runs flip. The flip cut P2's snake to a single stone at (1,2) whose remaining neighbors were all X or hole: the engine then reported P2's only legal action as PASS — permanent paralysis without re-arm (re-arm needs ZERO stones, and (1,2) is immortal since its bracket lines end in holes/occupied cells and flips only fire on placement). I also confirmed the hole-blocking of capture walks (no flip ever crossed a hole) and then walked P1 along y=0 to a connection win while P2 passed. One trap noted: had P1 passed at any point, the forced P2 pass plus mine would have ended a totally won game as a double-pass draw.
- Result: P1 win, connection, ply 27 (P2 paralyzed from ply 16 onward).

### Additional lines (optional)
Two aborted probes worth recording. (a) Opening probe `4,36`: P1's seed (4,0) — the chokepoint itself — has degree 2 (holes at (4,1) flank it), leaving P1 exactly two legal moves; analysis showed a P2 reply at (2,0) refutes it outright (P1's west becomes unreachable: (1,0) can never be legally placed). (b) Pre-Line-1 analysis, engine-checked cell by cell for legality: P2's transpose-mirror race loses every collision by one tempo, which is why Line 2's cross-block deviates from the mirror.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  A good move extends your snake along a path that (a) passes through one of your four chokepoint triples (P1 needs {(3,y),(4,y),(5,y)} for some y in {0,2,6,8}; P2 the transpose), (b) arrives at contested cells before the opponent's snake — distance-to-collision is everything, and (c) claims cells whose bracket lines are killed by holes or edges so they can never be flipped. The deepest recurring calculation is pure tempo arithmetic: count both snakes' distances to the collision cell; the loser of that count must reroute, which usually costs 4+ moves and the game.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? The game is almost entirely responsive — but at the STRATEGIC level, not tactically. The mirror strategy (Line 1) was punished by pure tempo; the correct response to a committed seed is the cross-block (Line 2), which annexes the far column the opponent cannot reach in time. Single-stone blocks sitting on an open line get custodian-flipped through (the mechanic's one real job), but blocks tucked behind holes are absolute. Once both seeds are committed, however, the outcome felt nearly computable — counterplay is front-loaded into the first few placements.
- Topology/board effects on strategy: The fractal holes are the whole game. They quantize both players' options into four crossing corridors each, make mid-corridor cells (e.g. (2,3),(2,4),(2,5)) simultaneously unflippable AND unapproachable from one side, and reduce key cells like (4,0) to degree 2. Edge rows are immune to perpendicular brackets. Every strategic judgment I made reduced to reading this hole geometry.
- Emergent concepts you'd name (or "none observed"): (1) "Seed commitment" — your single free placement decides your whole game; there is no re-seeding. (2) "Adjacency defender advantage" — the player whose stones already border a contested cell wins it against any distant snake. (3) "Corridor immunity" — hole-walled column/row segments are fortress territory. (4) "Snake paralysis" — a well-aimed flip amputates the opponent's only growth front (Line 3's pass-locked P2). (5) "One-tempo race law" — symmetric strategies lose for P2 by exactly the first-move tempo, forcing asymmetric play.
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Choices decided results, but most of the agency is concentrated in plies 1–8: seed placement and the block/race decision. After commitment, both Line 1 and Line 2 played out as forced tempo marches I could compute many plies ahead. High agency, but front-loaded; the middle game is execution rather than decision.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  "This is Hex with extra steps": asymmetric face-to-face connection goals are exactly Hex/Gale's, the square-grid orthogonal version is the classic game Gale (Bridg-It), and the additions — grow-from-your-own-stones and an Othello capture that competent play never triggers — just slow the race down. Even the fractal board only prunes the graph; Hex on an arbitrary graph is still Hex. Under this reading the game is Bridg-It on a punctured board, with a vestigial capture rule bolted on for flavor.
- Honest novelty assessment after arguing that case: Mostly sustained, with one genuine exception. The connection-race experience IS recognizably Hex/Bridg-It, and the capture mechanic is nearly dead weight (zero flips in competitive lines — a mechanic that only matters when someone blunders a single stone onto an open line). But the own-adjacency growth rule is a real innovation with a striking theoretical consequence: it breaks the strategy-stealing argument (you cannot "play elsewhere" — your blob is committed), which makes a second-player-favored connection game conceivable, something classical Hex cannot be. My Line 2 evidence (the cross-block's strength, reacting to a committed seed) suggests this is not just theory. Novelty: modest overall — one clever rule on a familiar chassis.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — the family resemblance to Hex/Bridg-It and Othello is generic; I do not recognize this specific game or recall a prior score.
- P1-role experience sub-score (1-10): 4.2
- P2-role experience sub-score (1-10): 4.3
- Role-averaged sub-score: 4.25
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 4 — my competitive lines split 1–1, but the second player's informational edge felt structural: P2 reacts to a committed, unmovable seed, and the cross-block reply (Line 2) refuted two P1 openers in engine-checked analysis while P1's win required P2 to mirror; the broken strategy-stealing argument means this perception is at least theoretically coherent.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.1**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  The fractal-corridor geometry produces genuinely sharp, fast, decisive races — Line 1's one-tempo collision win and Line 2's cross-block refutation were both satisfying to find and verify, and the opening-theory layer (seed commitment, corridor annexation) has real depth. But the game loses points for a headline mechanic that does not participate: custodian capture fired zero times in competitive play (Line 3 had to be lab-constructed to observe it), which makes the design feel like Bridg-It wearing an Othello costume. Agency is heavily front-loaded (after ply ~8 both my lines were computable forced marches), and the suspicion of a structural second-player edge (Line 2) plus the paralysis/forced-pass edge cases (Line 3) suggest rough balance edges at depth. That places it clearly above R20/R21's level but below the best: 4.1, just at the R8 anchor, anchoring down per instructions.
