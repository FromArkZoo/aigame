# Team 1 — Game E verdict

> Copy this template to `team-1_gameE.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game E` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  4×4×4 board with 3D Moore adjacency (up to 26 neighbors). Placement must touch your own stones (first stone anywhere, re-arms at zero), and the target can be ANY cell — placing on an enemy stone REPLACES it, placing on your own is a legal no-op. After EVERY action (including passes) a cellular automaton runs THREE times from the acting player's perspective. The table is savage: your own stone with exactly 3 friendly and 0 enemy neighbors dies (density suicide); a stone with 1 friendly + 2 enemy contacts flips to the enemy — on your own tick; enemy stones with 2-of-yours + 1-their support convert to you; lone stones touching the enemy annihilate. The single birth rule needs an empty cell with exactly 3 friendly + 3 enemy neighbors. Win by connection: P1 joins the z=0 and z=3 faces, P2 the x=0 and x=3 faces; 141-ply limit with stone-count tiebreak; double-pass draw; super-ko on the post-CA position rolls repeats back into passes.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Connection win twice (line 1: P1 at ply 13; line 2: P2 at ply 8); double-pass draw twice — one deliberate (line 3, ply 11) and one ACCIDENTAL (additional line, ply 6): two consecutive futile actions were each super-ko-rolled into passes and the engine declared a draw that neither player ever chose. No tiebreak reached.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: This game generated more engine surprises than the rest of my slate combined, all traceable to the table afterwards: (1) my first "winning" link placement gave two of my own cells 3 friendly neighbors and the 3-iteration cascade executed them before the win check — my connection disintegrated as I completed it; (2) a single landing of mine converted an enemy stone, starved a second, and wiped P2 to zero (re-arming their first-move-anywhere) twice in one line; (3) naked contact stones die on their own placement tick, so the engine rolls such placements back as super-ko repeats — producing the accidental double-pass draw; (4) P1's completion move in line 2 triggered four (3F,3E) births and a cascade that flipped three of P1's own path cells to me; (5) a replace-attack stuck for exactly one iteration before the CA flipped the replacing stone back to its victim and killed both its supporters.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `45,52,29,57,60,50,13,37,42,54,42,35,57`
- Plan and what happened: I raced a z-column while scripted P2 shadowed my z=3 landing zone with its own x-chain (its stones there double as chain and flip-threats). My ply-5 landing at (0,3,3) triggered a cascade that converted P2's (1,2,3), starved its other stone (P2 wiped to zero, re-armed), and killed my own (1,3,2) by density. My first re-link attempt at (2,2,2) then self-destructed the same way — completing a path in a compact region gives interior cells 3 friendly neighbors, which is death. I learned the geometry (stretched chains: consecutive stones adjacent, non-consecutive NOT), rebuilt through (2,2,2) a second time after P2's harassment killed my orphaned z=2 stone, and landed at (1,2,3), which arrived with exactly 2 own neighbors — the immortal interior count.
- Result (winner, end cause, plies): P1 (me) win, connection z=0→z=3 at ply 13, having wiped P2 to zero twice along the way.

### Line 2 — you as P2
- Moves: `13,58,29,42,40,57,60,59`
- Plan and what happened: Against a scripted P1 straight z-column, I planted a SUPPORTED pair ((2,2,3),(2,2,2)) beside P1's landing fan — any cell adjacent to both is poisoned (a stone landing there with one own support flips on its owner's own tick via (1F,2E)). P1 rerouted through (0,2,2) toward the one clean corner and played the "winning" (0,3,3)... which detonated: the placement created four (3F,3E) birth cells (births to P1), but the ensuing iterations flipped (1,3,1), (0,2,2) and the landing itself to ME and killed (1,3,0). P1's win check found no path; I inherited a 6-4 material lead with x=0 and x=2 already held, and placed (3,2,3) — landing with 2 own supports, immortal — to complete x=0→x=3.
- Result: P2 (me) win, connection at ply 8, final count 10-4 after the cascade's bonus births. The reactive player harvested the leader's explosion — this game's completion moves into contested space are landmines for the mover.

### Line 3 — adversarial / novelty-stress
- Moves: `13,58,29,42,40,57,42,64,29,64,64` (plus the failed-pincer exhibit below)
- What you tried to break / stress, and what happened: (1) REPLACE: P1 replaced my (2,2,2) directly — legal, and the stone stuck through iteration 1, but the cascade then killed both of P1's adjacent supporters (3-friendly suicide) and flipped the replacing stone BACK to me via (1F,2E): the attack converted P1's 4-stone position into a single survivor. Replace-attacks into supported enemy clusters are self-destructive. (2) Pass-runs-CA: my pass at ply 8 executed a CA step with "board delta: none" — consistent, no ripe cells. (3) Deliberate double-pass ending confirmed at ply 11.
- Result: DRAW, double pass, ply 11. Combined with the accidental-draw exhibit, every exotic action type (replace, self-place, pass, rolled-back futile placement) is now engine-verified.

### Additional lines (optional)
Failed-pincer exhibit (moves `21,20,42,17,21,5,31,2,43,3`, ends at ply 6): my attempt to pincer P1's core with naked contact stones failed in the most instructive way possible. Ply 2: my lone stone adjacent to P1's lone stone would have mutually annihilated back to the empty board — the engine detected the position repeat and rolled my placement back to a PASS. Ply 4: my next try was placed and died in the same tick (delta: none). Ply 5: P1's scripted no-op self-placement was likewise rolled to a pass; ply 6: my second futile contact placement became a pass — and the two consecutive rolled-back "passes" ended the game as an OFFICIAL DRAW at ply 6, 2 stones to 0, with neither player ever choosing to pass. An accidental-draw landmine baked into the rules interaction.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Build stretched chains — consecutive stones adjacent, non-consecutive stones NOT adjacent — because 3 friendly neighbors is death and 2 is immortality; land path endpoints so they arrive with exactly 2 own supports; and never place a stone whose (own, enemy) contact count sits on a flip row of the table. Offensively, approach with supported pairs: two connected stones adjacent to an enemy stone with exactly one own support convert it on your tick.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Response is everything, but through the CA: shadowing the opponent's landing fan poisons their completion cells; their "winning" move then either detours (losing tempo) or detonates (line 2, where I won directly from P1's explosion). Naked aggression is punished instantly (the pincer exhibit); over-supported aggression is punished by density suicide; the rewarded style is a narrow band between them.
- Topology/board effects on strategy: Moore-26 adjacency makes everything close — a 4-chain spans the board, single stones shadow nine-cell landing fans, and the two players' diagonals interpenetrate. The (3F,0E) death rule interacts with this brutally: in Moore geometry almost any compact cluster crosses the 3-neighbor threshold, so viable structures are strings and staircases, never blobs. The replace rule means even "immortal" 2-support interiors are only CA-immortal, not placement-immortal.
- Emergent concepts you'd name (or "none observed"): "Stretched chain" (the only viable path geometry); "immortal interior" (exactly-2-own-support); "poisoned landing" (cells adjacent to two enemy supported stones flip the lander on its own tick); "detonating completion" (win-completing moves into contested zones trigger cascades that can flip the path to the defender); "futility rollback" (doomed placements become passes — and two in a row end the game); "wipe-and-re-arm cycle" (zero-stone players re-enter anywhere, which happened three times across my lines).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Mixed — the lowest of my slate so far. Strategic choices (stretched geometry, shadow pairs, supported approaches) demonstrably mattered and I won both competitive lines with them, but the 3-iteration cascades outran my analysis repeatedly: several results (including my line-2 win) arrived via chains of consequences I only partly foresaw. Playing well feels like probing a reactive system rather than out-thinking an opponent.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  It is the same actor-perspective-CA game framework as another game in this slate (C) with different dials: swap the 4D torus for a 3D Moore cube, swap territory for Hex-style connection goals, crank the CA to 3 iterations, and add replace-placement. As a FAMILY, two-player Life-like CA combat exists in prior art, and connection wins are Hex boilerplate; one could argue E is "game C's chassis with a different tuning file," making it a re-skin within its own campaign, not just of external priors.
- Honest novelty assessment after arguing that case: The within-slate chassis-sharing is real and reduces marginal novelty — but the tuning IS the game, and E's table produces a completely different play experience from C's: C rewards fortress-building and birth-farming; E forbids density outright, makes your own completion moves dangerous, and turns futile actions into game-ending passes. The replace mechanic and the 3-iteration cascades have no counterpart in C or in any prior game I know. Substantial novelty in absolute terms; moderate marginal novelty if evaluated alongside its sibling.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — no external prior recognized; I do note its evident mechanical kinship to slate-game C (same CA framework, different parameters), which I have factored into novelty, not identity.
- P1-role experience sub-score (1-10): 4 — the line-1 win required genuine learning (two disasters before the stretched-chain insight), which was satisfying but bruising; the role feels like defusing your own bombs.
- P2-role experience sub-score (1-10): 4.5 — poisoning P1's landing fan and then winning directly out of P1's detonation (line 2) was the most dramatic reactive win of my slate.
- Role-averaged sub-score: 4.25
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 3 — P1 won line 1 and P2 won line 2, and while P1 nominally has the tempo (a clean 4-chain completes on ply 7), completion moves into contested space detonate so reliably that the reactive player's harvest roughly cancels the first-mover edge in my observed play.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.2**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  Game E is the most volatile and in some ways most fascinating game of my slate: the stretched-chain geometry, poisoned landings, and detonating completions (all engine-verified across lines 1-2) are genuinely novel strategic content, and every one of its many surprises reconciled exactly with the printed CA table afterwards. It scores below its sibling C because the experience is less governable: three CA iterations per action outran even careful analysis (line 1 needed two full rebuilds; line 2 was won by an explosion I triggered but didn't fully predict), the accidental double-pass draw (additional line — a real game ended at ply 6 by two rolled-back futile moves) is a genuine design landmine, and marginal novelty is discounted for sharing its chassis with C. High-novelty, high-chaos, medium-agency: 4.2, between R8 and R19.
