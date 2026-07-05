# Team 2 — Game E verdict

> Copy this template to `team-2_gameE.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game E` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  4×4×4 board with Moore adjacency (all Chebyshev-distance-1 cells — up to 26 neighbors). Placement must touch your own stones (first stone free; re-arms at zero); placing onto an ENEMY stone replaces it (verified); the rules text also claims own-stone no-op placements are legal, but the engine rejects them (see surprises). After EVERY action — including passes — a totalistic CA runs THREE iterations from the actor's perspective; the table covers neighbor counts 0..4 per side only (denser cells are frozen), with one birth rule (empty at 3 friendly + 3 enemy) and a menagerie of deaths and ownership flips (e.g. an actor's stone at 1F+2E flips to the opponent; an opponent's stone at 2F+1E or 1F+4E flips to the actor; lone stones die at 1 enemy contact). Win: Hex-style connection, P1 joining the d2=0/d2=3 faces, P2 the d0 faces; same-tick double completion is an explicit draw. 141-step limit with stone-count tiebreak; double pass draws; super-ko checked post-CA.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Both competitive lines ended by connection win, absurdly early relative to the 141-step budget: Line 1 at ply 7 (P1), Line 2 at ply 12 (P2/me). The stress line produced super-ko rollbacks rather than a normal ending. Moore adjacency makes minimal winning paths only 4 stones, so the game is a knife fight.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: Plenty. (1) Rules/engine contradiction: "placing on your own stone is a legal no-op placement" is false in practice — the engine excludes own stones from the legal list (verified twice, including a no-super-ko position). (2) The opening annihilation-lock: any P2 reply adjacent to P1's lone first stone kills BOTH stones via the (1F,0E)/(0F,1E) rules, recreating the initial position — which the engine rolls back as SUPER-KO into a forced pass; since a central first stone's Moore neighborhood is 26 cells, P2's entire natural reply zone is illegal-in-effect. (3) The 3-iteration CA is genuinely beyond hand tracking: my ply-7 win in Line 1 came with an 11-cell delta in which two of my four chain stones flipped to the enemy yet freshly-born stones completed the connection anyway; and in the stress line my predicted pass-triggered flip did not occur — my neighborhood bookkeeping was simply wrong. (4) A defensive move by P1 in Line 2 would have completed MY connection on HIS tick (CA birth), an outcome class impossible in non-CA games.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `5,12,26,29,37,46,58`
- Plan and what happened: Diagonal-chain race: (1,1,0)→(2,2,1)→(1,1,2)→(2,2,3), designed so every stone kept ≤2 friendly neighbors (avoiding the actor's (3F,0E) self-destruct) and non-consecutive stones stayed non-adjacent. Scripted P2 raced his own d0-chain with one contact stone. My hand-analysis held for six plies (I verified P2's natural (2,2,2) would have self-flipped via the actor's (1F,2E) rule, so he detoured), but the final placement triggered an 11-cell CA storm across the 3 iterations: two of my chain stones flipped to O, several new X stones were born, and the born stones happened to preserve a d2=0→d2=3 path. Win — but partially by CA accident rather than by my design.
- Result (winner, end cause, plies): P1 (me) win, connection, ply 7.

### Line 2 — you as P2
- Moves: `5,19,26,2,37,1,22,1,21,7,0,4`
- Plan and what happened: Against the same racing P1, I played the disruption I derived from the table: seed at Chebyshev-2 from his stone (adjacent seeding is annihilation-locked), then bring TWO stones adjacent to his d2=0 anchor while avoiding his second stone — the opponent-cell (2F,1E) steal. The engine's version was even better than planned: his anchor DIED outright and the CA bore me a bonus stone at (2,1,1). He counter-attacked with the replacement rule (placing onto my CA-born stone — verified capture-by-replacement), then stole my chain stone 1 via his own (2F,1E); I answered at (3,1,0), carefully NOT adjacent to his thief so the (1F,4E) counter-flip would fire — and the 3-iteration cascade instead exploded into +8 births for me (13-5). From there I had multiple redundant d0=0 entry cells; his sweep-best block (0) couldn't cover them, one of his tries (8) would have completed my path FOR me on his own tick, and at ply 12 every single candidate I tested won.
- Result: P2 (me) win, connection, ply 12.

### Line 3 — adversarial / novelty-stress
- Moves: `21,22` and `21,2,21,64,64` and `21,63` (+ legality probe) and `5,19,26,2,37,1,22,1,21,64`
- What you tried to break / stress, and what happened: (a) Mutual annihilation: P2 placing adjacent to P1's lone (1,1,1) stone kills both stones → empty board = initial position → engine flags SUPER-KO and rolls the move back to a pass; confirmed for two different adjacent cells, including the deceptively "far" (2,0,0) (Moore adjacency!). P2 literally cannot engage P1's first stone — an opening-theory quirk unique to this game. (b) Self-overwrite: the engine rejects placing on your own stone as ILLEGAL despite the rules text calling it a legal no-op — documented rules/engine contradiction (verified in a position with no super-ko confound: 26 legal cells, own stone excluded). (c) Enemy replacement: verified working in Line 2 (his ply-7 move overwrote my stone). (d) Pass-triggered CA: a pass in a volatile Line-2 position produced NO delta where I had predicted a flip — passes do run the CA, but my hand-model of the neighborhood was wrong; the honest finding is that 26-neighbor × 3-iteration dynamics defeat human calculation.
- Result: stress findings as above; no conventional game result (rollbacks and probes).

### Additional lines (optional)
Candidate sweeps used as part of play (all engine-verified): P1's 14 options at Line-2 ply 11 (best kept him alive; one accidentally won the game for ME); my 6 options at ply 12 (all won). These sweeps are themselves data: the branching outcomes differ wildly between adjacent cells, confirming the evaluation-opacity noted below.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Two legible layers sit on top of an illegible one. Legible: (1) chain-building with safe self-counts — keep own stones at 1-2 friendly neighbors (the (3F,0E) suicide and (1F,2E)/(3F,1E) self-flip rules punish density between 3 and 4); (2) the theft calculus — two attackers adjacent to an enemy stone that has exactly one friend steals or kills it, and a stone drowning at (1F,4E) flips on your ANY action. Illegible: the 3-iteration cascade consequences of any placement in a mixed zone — there the practical loop degenerates to enumerate-and-test.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Constant response: every stone placed near the enemy is attackable by steal, replacement, or drowning, and both my lines were WON by responses (the anchor theft in Line 2; his replacement counter kept him in the game). The replacement rule is the purest counterplay tool — an unconditional local override, limited only by own-adjacency. But punishment is often mutual and delayed by CA chaos: my winning explosion at ply 10 was a response whose actual effect (+8 births) I did not and could not predict.
- Topology/board effects on strategy: Moore adjacency compresses the game: 4-stone winning paths, 26-cell neighborhoods, everything within distance 3 of everything. This makes tempo overwhelming (Line 1's ply-7 win), makes "keeping away" impossible, and via the counts-0..4-only table makes DENSITY a shield (cells with 5+ neighbors of a color freeze) — the only stable structures are either isolated pairs or thick blobs.
- Emergent concepts you'd name (or "none observed"): (1) "Annihilation lock" — lone-stone contact is mutual death, rolled back by super-ko at the opening. (2) "Safe-count chains" — 1-2 friendly neighbors as the only survivable marching formation. (3) "Theft war" — (2F,1E) steal vs replacement vs (1F,4E) drowning as a rock-paper-scissors of ownership. (4) "Density freezing" — packing past the table's 0..4 range as immunity. (5) "Accidental completion" — connections created or destroyed by CA births neither player placed (his move 8 would have won the game for me).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? The weakest agency of my seven games. The calm-phase mechanisms (chain safety, theft setups) are real decisions and mine worked, but every decisive moment ran through a 3-iteration Moore-3D cascade that neither I nor plausibly any human can evaluate unaided — I found winning moves by sweeping candidates through the engine, and Line 1's win survived by luck. The game rewards having a simulator more than having a plan.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  "Competitive Life with a Hex win": two-player cellular automata (Immigration/p2life family) plus a connection victory condition is a mashup of two known genres, and the sibling game in this evaluation set (my Game C) already established the actor-perspective CA formula — E is arguably C re-skinned onto a Moore 3D board with a connection goal instead of a territory count, plus a stock replacement-capture rule.
- Honest novelty assessment after arguing that case: Within this blind set, E and C are clearly siblings (same actor-perspective CA skeleton, different tables/boards/goals), so E's marginal novelty over C is the question. It does add genuinely new dynamics: the annihilation-lock opening, ownership FLIPS (C's table only births/kills — E's stones change color, enabling the theft war), density freezing, and replacement placement. Against the outside world the combination remains unprecedented in my knowledge. But novelty of experience is undercut by illegibility — three CA iterations per action pushes the game from "chaotic but readable" (C) to "oracle-required". Moderate novelty, most of it shared with its sibling.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — no specific prior recognized, no prior score recalled (its evident kinship to blind-set sibling Game C is noted above, not a recognition of an external game).
- P1-role experience sub-score (1-10): 3.6
- P2-role experience sub-score (1-10): 3.8
- Role-averaged sub-score: 3.7
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 3 — my competitive lines split 1-1 (P1's tempo race won Line 1 at ply 7; my P2 disruption won Line 2 at ply 12), and the two structural asymmetries I found cut in opposite directions (P1 gets the first-strike tempo; P2's annihilation-lock handicap is offset by the disruption toolkit), so I saw no consistent tilt in play.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 3.6**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  The learnable layer of this game is genuinely clever — the theft war I fought in Line 2 (steal his anchor, absorb his replacement counter, arm the (1F,4E) drowning) was real strategy derived from reading the table, and it produced my win. But the game undermines its own decisions: Line 1's win survived on CA accident (two path stones flipped enemy, strangers born to replace them), my stress-line flip prediction simply failed, and at the decisive ply of Line 2 all six candidates won — the 3-iteration Moore cascade makes outcomes locally decision-independent and globally human-incomputable, so play collapses into engine-sweeping precisely when it matters. Add the opening annihilation-lock oddity, a documented rules/engine contradiction (illegal "legal no-op"), and games that consume 5-9% of their step budget, and this sits below both R20 and R21 anchors for me despite its inventiveness: spectacular physics, weak game. 3.6.
