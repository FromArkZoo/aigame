# Team 2 — Game B verdict

> Copy this template to `team-2_gameB.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game B` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  8×8 orthogonal grid. Free placement (no spatial constraint), Go-style surround capture (adjacent enemy groups at zero liberties are removed after your action), plus MOVE actions: relocate one of your stones to an adjacent empty cell (ids 65-320, encoded per-neighbor; engine-verified that moves ALSO trigger captures). Win: territory race — first to own 41+ of the 64 cells (63.26%); 100-step limit with most-stones tiebreak; double pass = draw; super-ko rollback rule.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Both competitive lines ended by the 41-stone win condition (Line 1: me/P1 at ply 85, 41-10; Line 2: scripted P1 at ply 93, 41-20). The stress line ended in a double-pass draw. The tiebreak never fired but shapes strategy (small life loses the count race, so passive play is punished).
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: The headline discovery: TWO-EYE LIFE DOES NOT EXIST. The liberty check is placement-local and enemy-only, so (a) a 0-liberty "suicide" stone placed into an opponent's eye is never removed (verified: my (0,7) stone and his eye-fill sacs persisted indefinitely — they cannot even be captured later, since no adjacent empty cell remains to place into); (b) the attacker can sack one such stone into each eye and then remove the entire group when its last real liberty fills. Go instincts about alive groups are systematically wrong here. Also verified: eye-fill placements that DO capture are legal (my 14-stone kill at (0,2) in Line 1); capture-by-MOVE works (Line 3: moving (2,1)→(2,0) removed the surrounded stone); and a 0-liberty stone of your own can also persist if your own placement fills your group's last liberty (removal only fires on the opponent's subsequent adjacent action).

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `27,36,28,35,43,34,44,37,45,38,46,30,29,33,42,31,22,47,26,63,54,62,55,25,40,24,41,17,23,18,32,8,1,58,19,50,10,49,61,57,39,48,51,9,2,59,0,47,16,60,39,4,38,5,56,6,3,7,11,15,12,14,13,52,53,48,4,49,5,50,6,58,7,57,20,59,21,60,24,62,25,63,33,56,34`
- Plan and what happened: A genuine full Go-style game. Center crosscut; P2's stones merged into an eyeless snake along y=4 which I chased between two walls (attack-for-profit). I denied eyes systematically: corner cross-blocks at (6,6)/(7,6), west eye denial at (0,5)/(1,0), then filled outside liberties and killed the 14-stone mega-group by playing INSIDE its last eye at (0,2) — legal because it captured. Additional harvests: his 2-stone corner pair, the (7,4)/(7,5) exchange, and a 6-stone top-edge chain that died when my (5,1) filled its last liberty. After his wipeout and re-arm rebuild (I conceded him the SW corner), I filled methodically to exactly 41 stones.
- Result (winner, end cause, plies): P1 (me) win, territory (41 vs 10), ply 85.

### Line 2 — you as P2
- Moves: `27,36,28,35,44,37,43,34,29,38,30,39,31,46,53,13,21,14,22,15,12,5,4,6,23,33,7,41,25,40,24,49,56,48,57,58,47,57,56,50,26,51,32,52,61,60,59,54,42,55,45,63,62,1,47,2,33,8,34,9,35,0,36,16,37,10,38,17,39,18,40,3,41,11,46,19,48,20,49,5,50,6,52,13,54,14,55,12,51,15,57,4,58`
- Plan and what happened: Mirrored the crosscut with colors swapped — instructively, this loses: as P2 my snake was always one tempo behind the line-1 pattern. My top-side invasion died against his pre-built walls (too narrow, one eye). My main group secured what classical Go would call life — and then P1 demonstrated the game's signature: he sacked 0-liberty stones into my eyespace ((0,7) and (3,7) persist on the final board), sealed the outside, and when my group's last real liberty filled, his (7,5) placement removed all 19 stones at once. My re-arm rebuild in the northwest lived (and even captured 3 of his stones) but the count was unreachable; he filled to 41.
- Result: P1 win, territory (41 vs 20), ply 93. My P2 improvements delayed but could not change the outcome.

### Line 3 — adversarial / novelty-stress
- Moves: `10,1,0,63,9,62,107,1,64,64` (with a `--legal` probe to decode MOVE ids)
- What you tried to break / stress, and what happened: (a) MOVE mechanics: `--legal` decodes each move id (from-cell, neighbor index); action 107 moved my stone (2,1)→(2,0) into the last liberty of his (1,0) stone and the capture FIRED — moves trigger the surround check, so movement is a real tactical resource (capture without adding a stone). (b) Suicide persistence: his reply placed a stone back at (1,0) with zero liberties among three X stones — it captured nothing, was not removed, and can never be removed (no empty cell adjacent for any capturing placement): a permanent squatter, confirming the mechanism behind eye-destruction. (c) Double pass → draw, confirmed.
- Result: DRAW (double pass), ply 10, engineered.

### Additional lines (optional)
None — the two competitive lines are long (85 and 93 plies) and cover both roles' full arcs, including one large-group kill BY each side's technique (eye-fill capture in Line 1, suicide-sac strangulation in Line 2).

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Superficially Go: build walls, chase eyeless groups, count liberties, deny eyespace, win semeai. But the life-impossibility theorem rewrites the goal: since no group is ever permanently alive, good moves maximize ATTACK TEMPO and material efficiency rather than settledness — you want your opponent's stones dead before your own liberties run out, and every capture is doubly profitable because the vacated area plus your surviving sacs become your filling ground. The 41-stone bar then converts won positions into a mechanical march.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Highly interactive: every eye attempt has a cross-block (Line 1's corner sequence), every snake gets chased, and the suicide-sac makes even "settled" groups attackable — the defender's only real answers are outside liberties and counter-attack speed. My Line 2 improvements (earlier eyespace, wider invasion) each met concrete refutations rather than generic ones. One asymmetric wart: against the suicide-sac itself there is NO counterplay — the squatter can never be removed, so eye-destruction is unanswerable by design.
- Topology/board effects on strategy: Plain 8×8 with 4-adjacency: edges and corners reduce liberties exactly as in Go, and both my decisive kills drove groups against edges. The small board plus the 63% occupation bar means there is no room for two large living positions — the geometry itself forces total war.
- Emergent concepts you'd name (or "none observed"): (1) "Life-impossibility" — two eyes protect nothing; safety is a liberty-count lease, not a deed. (2) "Suicide squatters" — permanent 0-liberty stones as unanswerable eye-killers. (3) "Kill-recoup cycle" — sacs spent on a kill become live stones in the vacated zone, making captures hyper-profitable. (4) "Count-race discipline" — passive life loses the tiebreak arithmetic, so territory instinct must be replaced by occupation instinct. (5) Capture-by-move as a stone-neutral tactic.
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Fully choice-driven and — unlike the CA games in this set — fully human-legible: every kill and defense in both lines was planned, and my mistakes (the mirrored opening as P2, an early miscounted liberty) had identifiable better alternatives. The engine contributed no randomness; the closest thing to structural determinism is the first-mover initiative, which both lines suggest is large.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  "This is Go" — surround capture, liberties, eyes, ko, semeai, even my game transcripts read like Go records; the deltas are a stone-count winning threshold (arguably just area scoring with a supermajority bar), a movement action (seen in Go variants and general abstracts), and a missing suicide-removal rule that a Go engine would call a bug. Under this reading B is 8×8 Go with komi 0 and sloppy rules.
- Honest novelty assessment after arguing that case: The case is strong for the components but misses that the "sloppy rule" inverts the game's strategic foundation: Go IS the game of making unconditionally alive shapes, and B abolishes them — eyespace becomes a delaying tactic, aggression strictly dominates territory, and the correct instincts are anti-Go in exactly the places a Go player would feel most confident. Whether intended or emergent, that inversion produces a genuinely different (and coherent!) strategic experience I can't map to a published variant. Novelty: modest at the rule level, real at the strategy level.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — it is transparently Go-derived (disclosed), but I do not recognize this specific variant or recall any prior score.
- P1-role experience sub-score (1-10): 4.4
- P2-role experience sub-score (1-10): 3.9
- Role-averaged sub-score: 4.15
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 2 — P1 won both competitive lines decisively, there is no komi (explicitly komi_p2 = 0.00) in a symmetric total-war race where the first mover sets every fight's tempo, and my improved P2 play in Line 2 changed the margin (41-20 vs 41-10) but never the direction.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.2**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  This was the most strategically legible and sustained game of my seven: Line 1 is an honest 85-ply campaign of chase, eye denial, a 14-stone eye-fill kill and three smaller harvests, and Line 2's suicide-sac strangulation of my "alive" 19-stone group is a genuinely novel strategic experience wearing Go's clothes. Depth is real, human-plannable, and decisive — no oracle needed. I hold it below R19's 4.375 for three defects: the unanswerable suicide-squatter mechanic (elegant in effect, degenerate in texture — permanent 0-liberty stones and no counterplay against eye-destruction), the evident first-mover tilt with zero komi (fairness 2), and game length pushing against the step budget (93 of 100 in Line 2 — a slightly slower P1 would have hit the ceiling). 4.2, just above the R8 anchor, anchored down from an initial 4.35 impression.
