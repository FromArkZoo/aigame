# Team 2 — Game G verdict

> Copy this template to `team-2_gameG.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game G` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  8×8 grid, orthogonal adjacency, completely free placement (no spatial constraint). Go-style surround capture: after a placement, any adjacent enemy group with zero liberties is removed from the board. Win by connection with asymmetric goals: P1 joins y=0 to y=7, P2 joins x=0 to x=7. PASS is legal; double pass = draw; 100-step limit with most-stones tiebreak. Super-ko: an action recreating a prior position is rolled back to a pass. There is also an influence/propagation field (each placement deposits decaying values within distance 3) that the rules themselves flag as "ghost" — engine-verified to affect nothing.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Connection win in both competitive lines (Line 1: P1 ply 37; Line 2: P1 ply 43 — both preceded by a game-deciding capture). Line 3 ended by double-pass draw (deliberate). No turn-limit tiebreak reached, though my Line 2 analysis found mutually-blocked positions where it would be the only decisive path.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: Three findings from the stress line. (1) Super-ko actually fires here — unique among the custodian-family games I evaluated, because capture removes stones, making repetition constructible: my textbook ko recapture was rolled back with an explicit "!! SUPER-KO ... treated as a PASS" flag. (2) Suicide is legal and unpunished: P2 placed at (0,0) with zero liberties, captured nothing, and the dead-on-arrival stone persisted indefinitely — the liberty check is evidently placement-local and enemy-only. (3) The influence field renders and accumulates exactly as described (--values) and demonstrably influences neither legality, captures, nor scoring — true dead code in this ruleset.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `28,36,35,27,44,37,19,26,20,34,43,45,42,18,53,46,52,29,21,38,54,39,30,31,22,47,23,25,55,33,36,32,12,24,4,17,60`
- Plan and what happened: Center opening led to a four-group crosscut: my north/south column groups versus P2's east/west row groups, each pair mutually split (my (3,4) permanently severed his y=4 row; his (3,3),(4,4) severed my x=4 column). I verified a real Go ladder threat against my 2-liberty (4,3) stone and connected solidly at (4,2) — an unfixed ladder would have lost the game. The decisive campaign: I squeezed his east group with double-purpose moves ((5,2) and (6,6) each took a liberty while extending my own groups), and when he defended with (5,3) and ran east, I chased the liberty race into the edge: my ply-29 placement at (7,6) captured his entire nine-stone east army. With his x=7 access annihilated, I linked my groups through the vacated center at (4,4) and completed the straight x=4 column, (4,0)…(4,7).
- Result (winner, end cause, plies): P1 (me) win, connection, ply 37, after a 9-stone capture.

### Line 2 — you as P2
- Moves: `28,36,35,27,44,37,19,26,20,34,43,45,42,18,53,46,52,54,29,38,30,39,33,17,25,16,41,9,11,10,3,62,60,24,32,1,2,21,8,64,0,26,27`
- Plan and what happened: Same opening (it transposes with roles swapped), but as P2 I deviated at ply 18: instead of the (5,3) overextension that doomed Line 1's P2, I took (6,6) for corner eyespace, then blocked his link route with (6,4) and grabbed x=7 face contact with (7,4) — my east group lived this time. The game became a pure link war: his north and south complexes could only join by strangling my west group (his wrap (1,4),(1,3),(1,5) was simultaneously his link route and my group's death). I secured x=0 contact ((1,2),(0,2)) and contested the corner, but the life-and-death was lost on inspection: my eyespace was a bent-three poisoned at both ends by his (3,0) and (1,3) stones — (2,0) and (0,3) could never become eyes, leaving one real eye. He filled the outside liberties, captured my eleven-stone west group at ply 41, and replayed (3,3) into the vacated wall to complete (3,0)-(3,1)-(3,2)-(3,3)-(3,4)-(3,5)-(4,5)-(4,6)-(4,7).
- Result: P1 win, connection, ply 43, after an 11-stone capture. I (P2) lost despite materially better play than Line 1's P2.

### Line 3 — adversarial / novelty-stress
- Moves: `1,9,8,16,10,18,63,25,17,9,62,0,9,64,64` (plus a re-run to capture the ply-10 flag text, and `--values`)
- What you tried to break / stress, and what happened: Built a textbook ko: my (1,2) captured O(1,1); P2's immediate recapture at (1,1) was rolled back by the engine with the explicit SUPER-KO flag and treated as a pass — repetition handling verified live (the only game in my set where it is reachable). Then P2 placed (0,0) with zero liberties: the engine ACCEPTED it, captured nothing, and the dead stone persisted for the rest of the game — suicide is legal and permanent here, and since (0,0)'s neighbors were all X, no enemy placement could ever trigger its removal. I filled my own ko point (legal), then double-passed: draw confirmed. Finally `--values` showed the influence field faithfully accumulating (positive around X placements, negative around O) while affecting no observable rule — the "ghost influence" note is accurate.
- Result: DRAW, double pass, ply 15 (by design).

### Additional lines (optional)
None beyond the above; Line 2's middle-game contains an engine-verified sub-experiment worth flagging: between plies 30–33 the position became one where NEITHER player could ever connect (both link corridors walled) — a genuine mutual-blockage state, impossible in Hex but possible under 4-connectivity, where only captures or the step-100 stone count could decide.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Go tactics in service of Hex strategy. A good move does two jobs at once: takes a liberty from an enemy group WHILE extending your own connection (Line 1's (5,2),(6,6)), or blocks the opponent's inter-group link WHILE approaching your own face (Line 2's (6,4),(7,4)). Group safety is a precondition for everything — a 2-liberty stone on your critical path is a losing move if the ladder works (verified in Line 1), and eyespace determines whether a blocking wall is permanent or harvestable. The single most important read: captures reopen cells, so a wall is only as strong as the group's life status.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Extremely responsive — the most interactive game in my set. Every strategic plan ran through the opponent: chasing a doomed group (Line 1's P2 running east) converted a bad position into a catastrophic capture; conversely my Line 2 deviation ((6,6) eyespace instead of (5,3) overextension) kept the same group alive for 25 more plies and changed the whole game's shape. Blocks are answerable by capture (Line 2's finale: he KILLED my separating wall and connected straight through the vacated cells — counterplay of a kind D and F cannot express).
- Topology/board effects on strategy: The plain 8×8 grid with 4-connectivity makes perpendicular completed paths mutually exclusive (blocker = winner), but unlike Hex, BOTH players can end up blocked (verified mid-Line 2), making the stone-count tiebreak strategically live. Edges and corners double as liberty-shortage zones: both decisive captures happened by driving groups into an edge or corner, and corner eyespace (bent-three, poisoned points) decided Line 2 exactly as in Go.
- Emergent concepts you'd name (or "none observed"): (1) "Wall life-and-death" — a blocking wall is only permanent if the group achieves two eyes; the game's real currency is group life, not territory. (2) "Double-purpose moves" — liberty-taking that simultaneously link-builds. (3) "Capture-reopened corridors" — connection through cells vacated by a kill (both decisive lines ended this way). (4) "Mutual blockage" — 4-connectivity draws where neither path is completable. (5) "Immortal suicide stones" — the engine quirk allowing 0-liberty placements that can never be removed if their surroundings are full.
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Fully choice-driven. Both decisive games turned on identifiable, avoidable decisions (Line 1: P2's doomed-group chase; Line 2: my corner eyespace miscount — I can state the exact losing move and the better alternative). The engine contributes no randomness or drift; the influence field is inert. This had the highest ratio of decision-depth to rule-complexity of my seven games.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  This is Gonnect — João Pedro Neto's published 2000 game "Go + connection" (Go rules, win by connecting opposite sides) — with minor deltas: goals are fixed per player (P1 north-south, P2 east-west) rather than either-pair, passing is allowed (Gonnect forbids it), plus an inert influence field and a permissive suicide rule that reads more like an engine gap than a design choice. Even the strategy lexicon transfers wholesale: ladders, eyes, ko, walls, throw-ins. Of my seven games this is the one closest to a nameable prior.
- Honest novelty assessment after arguing that case: The case is strong and I largely accept it — the core experience is Gonnect-like to anyone who knows that game. The deltas do matter at the margin: fixed asymmetric goals remove Gonnect's "either pair of sides" flexibility and create genuinely different blocking geometry (my (3,4) stone splitting his row was valuable ONLY because his goal was fixed); legal passing plus the stone-count tiebreak changes mutually-blocked endgames from Gonnect's zugzwang-decided endings to counting races. Novelty: low-to-moderate — an excellent known formula, re-parameterized rather than re-invented.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (mandatory): I believe this game is essentially Gonnect (Neto, 2000) with asymmetric fixed goals — disclosed per protocol; I recall no prior score for it in this campaign context. Continuing with unbiased assessment.
- P1-role experience sub-score (1-10): 4.7
- P2-role experience sub-score (1-10): 4.0
- Role-averaged sub-score: 4.35
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 2 — P1 won both competitive lines from the same opening, and the initiative was visible mechanically: P1 was always one tempo ahead in every crosscut fight and liberty race (Line 2's P2 improvements bought 6 extra plies of survival, not a different result), with no pie rule to compensate.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.3**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  As a play experience this was the strongest of my seven: Line 1's nine-stone edge kill and Line 2's bent-three corner life-and-death are real, deep, teachable fights, and both games ended through the signature dynamic — connection through capture-vacated cells — that neither pure Hex nor pure Go produces. Agency is total and counterplay is constant. I cap it at 4.3 for three reasons: it is the least novel game in my set (recognizably Gonnect re-parameterized, disclosed above); the first-player tilt looked structural across both lines with no pie rule; and it carries dead or buggy freight (the ghost influence field affects nothing; legal immortal suicide stones are an exploit-shaped quirk). Against the anchors that lands just below R19's 4.375 — excellent play value discounted for derivative design — and I anchor down accordingly.
