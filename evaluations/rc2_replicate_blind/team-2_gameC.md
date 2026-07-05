# Team 2 — Game C verdict

> Copy this template to `team-2_gameC.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game C` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  81-cell 4D torus (3×3×3×3): two cells are adjacent iff they differ in exactly one coordinate, and since each axis is a 3-cycle, all three cells of a line are mutually adjacent — every cell has degree 8, no edges or corners exist. Placement must touch your own stones (waived at zero stones, re-arming on wipeout). After EVERY action — placements AND passes — a totalistic cellular automaton fires once, interpreted from the ACTING player's perspective: specific (friendly, enemy) neighbor-count pairs cause empty cells to birth (mostly to the actor, e.g. 2F+1E, and strikingly 1F+2E — an "intrusion" birth inside enemy mass) and stones to die (e.g. an actor's stone at 0F+3E, an opponent's stone at 3F+0E). Classic capture/propagation are disabled. Win: territory race — first to own 17+ cells (>16.2 = 20% of 81). 98-step limit with count tiebreak; double pass = draw; super-ko checked on the post-CA position.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Both competitive lines ended by the 17-stone win condition at ply 14 (Line 1: P2 22-15; Line 2: me-as-P2 18-16) — remarkably fast for a 98-step budget, because the endgame is an exponential birth cascade. The stress line ended in a double-pass draw produced by a super-ko rollback (see below).
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: (1) The CA cascades are enormous: single placements produced up to 8 simultaneous births (ply 12 of Line 1), and my hand predictions of birth counts were wrong twice despite careful counting — 4D torus adjacency (81 cells, 8 neighbors, three-cliques per axis) defeats reliable human bookkeeping. (2) A placement can die on its own tick: my stress-line stone placed at (0F,3E) vanished in the same step, leaving "board delta: none" and my side still at zero stones with first-move-anywhere intact. (3) The super-ko/pass interaction: repeating that suicide recreated the post-CA position, the engine rolled it back to a PASS, and because the opponent had just passed, the rolled-back pass ended the game as a double-pass draw — a four-rule chain (death → re-arm → super-ko → draw) I did not foresee from the rules text.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `40,36,39,37,41,43,13,34,67,61,49,53,66,45`
- Plan and what happened: I opened center-block and built a line; engineered my first CA birth by hand (placing 41 created a 1F+2E cell at 38 — verified: the engine birthed it), but his reply's double birth taught the core lesson: my stones are the enemy-ingredient of HIS birth patterns. After a quiet development phase (the fully-saturated 3×3 plane went CA-inert — all its off-plane shell cells see exactly one stone), my ply-11 placement of 49 detonated a quadruple birth (11-8 lead). That explosion armed HIM: the frontier my births created gave his ply-12 reply (+7, to 16) and I could not reach 17 on my tick (best sweep result: 15) nor deny his final placement. His ply-14 move cascaded +5 more.
- Result (winner, end cause, plies): P2 win, territory (22 vs 15), ply 14.

### Line 2 — you as P2
- Moves: `40,0,41,1,39,2,37,3,43,10,31,13,67,19`
- Plan and what happened: As P2 I let scripted-P1 race compactly (correct for him: contactless play wins P1 the pure placement race by tempo, so P2 must manufacture volatility). I seeded a far cluster, then probed contact with 10 and hand-engineered a double birth with 13 — the engine delivered more than I calculated (+4, though it also revealed his cross had quietly harvested off my earlier stones: 4D feeding is treacherous). At 10-9 the explosion phase began: his best tested move (67, +7) took him to 16, mirroring Line 1's cliff — but this time the huge X mass was MY intrusion-birth fuel. I swept my 22 legal replies: four were outright wins, and 19=(1,0,2,0) birthed +7 for 18 stones.
- Result: P2 (me) win, territory (18 vs 16), ply 14 — the mirror-image of Line 1's finish, decided by the same explosion-parity.

### Line 3 — adversarial / novelty-stress
- Moves: `1,81,2,81,10,81,9,81,11,0,81,0`
- What you tried to break / stress, and what happened: I had P1 build three stones around cell 0 while I passed (interleaved passes are legal; only consecutive ones end the game), then placed my FIRST stone into the (0 friendly, 3 enemy) pocket: it died on its own CA tick — board delta "none", my count still zero, place-anywhere still armed. P1 passed; I repeated the suicide: the engine flagged SUPER-KO (post-CA position repeated), rolled my action back to a pass — and that rolled-back pass, following P1's real pass, ended the game as a double-pass draw. This verified: CA deaths exist (all competitive-line deltas had been births), same-tick self-death, zero-stone re-arm persistence, post-CA repetition detection, and that a super-ko rollback counts as a pass for the double-pass rule.
- Result: DRAW ("double pass -> draw"), ply 12, engineered.

### Additional lines (optional)
Candidate sweeps (engine-verified, part of my play process): at Line 1 ply 13 I tested 10 legal moves (best +4, none reaching 17, none killing O stones — confirming the loss); at Line 2 ply 14 I swept all 22 legal placements: outcomes ranged from +3 to +8 with four immediate wins — direct measurement of how much placement choice matters inside the cascade.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Early: build shapes that are CA-inert from the opponent's perspective (his cross was exemplary — a saturated plane whose shell cells each see only one stone) while arranging your pairs so that a single future contact creates (2F,1E) cells only YOU can harvest. Middle: the feeding calculus — every stone you place near his mass is the "1 enemy" ingredient of his births, so contact must be shaped to leave your patterns, not his. Late (explosion phase): pure harvest maximization; the position is so volatile that the practical loop becomes "enumerate legal moves, evaluate each cascade" — I could hand-design births in the calm phase (Line 2's move 13) but not reliably in the storm.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? The central irony: the BIGGER your harvest, the more intrusion-birth fuel (1F+2E cells thrive next to dense enemy mass) you hand the opponent's next tick. Line 1's quadruple birth directly enabled his +7; his +7 enabled my four winning replies in Line 2. So the game punishes premature explosions and rewards timing the cascade so YOUR tick crosses 17 first — response to the opponent is everything, but it is response-by-calculation rather than response-by-reading.
- Topology/board effects on strategy: The 3-cycle axes make the board terrifyingly connected (diameter 4, every line a triangle): "distant" development is only ever 2-3 steps from contact, saturated planes create temporary firewalls, and no edges exist to anchor anything — a fundamental contrast to every other board I evaluated. The torus also makes all openings equivalent, removing opening theory entirely.
- Emergent concepts you'd name (or "none observed"): (1) "Feeding" — your stones are ingredients of enemy births. (2) "Intrusion births" — dense masses spawn enemy stones at their own boundary (1F+2E). (3) "Saturation firewalls" — fully-filled planes are CA-inert. (4) "Explosion parity" — the cascade grows each tick, and whoever's tick lands when the cumulative crosses 17 wins; both my games ended on the same ply number (14) for this reason. (5) "Suicide probes" — same-tick self-death placements that preserve re-arm.
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Split verdict. In the calm phase agency is real and legible: I designed a double birth by hand and it worked as calculated. In the explosion phase, choices still matter enormously (my ply-14 sweep spanned +3 to +8 — losing vs winning), but the evaluation is beyond human reading: I found the winning move by enumeration, not understanding. Agency exists but degrades into oracle-consultation exactly when the game is decided; a human without an engine would be gambling from ply 11 on.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  "It's a competitive Life variant": two-color cellular automata games (Immigration Game, p2life, and the black/white competitive Life family) have existed for decades, and territory-threshold races are standard. Under this reading the designer took competitive Life, shrank it onto a 4D torus, bolted on Go-ish placement, and set a 20% territory bar — every ingredient has a documented ancestor.
- Honest novelty assessment after arguing that case: The case underestimates two things. First, the actor-perspective rule table — the SAME neighborhood configuration resolves differently depending on who just moved — is not a feature of any competitive-CA game I know; it converts a symmetric physics into an initiative mechanic (patterns are first-come-first-served, passes are meaningful actions, and "whose tick is it" becomes the game's central resource). Second, the 3^4 torus's everywhere-3-clique adjacency produces the saturation-firewall and intrusion-birth dynamics that don't exist on standard Life grids. This is the most genuinely novel game in my set — at the cost of near-illegible dynamics.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — competitive-CA games exist as a family, but I do not recognize this specific ruleset or recall any prior score.
- P1-role experience sub-score (1-10): 3.7
- P2-role experience sub-score (1-10): 4.2
- Role-averaged sub-score: 3.95
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 4 — both competitive lines were won by P2 at ply 14 via the same mechanism (the explosion's threshold-crossing landing on an even tick), and since contactless play favors P1 by tempo, the volatility P2 needs appears to come with a built-in parity advantage once it starts; two games is thin evidence, but the mechanism is structural, not incidental.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 3.9**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  The most novel and most spectacular game of my seven — Line 1's quadruple birth, the mutual-explosion finishes at ply 14 in both lines, and the stress line's suicide→super-ko→forced-pass→draw chain are mechanics I have never seen compose anywhere. But the same volatility that makes it spectacular corrodes the play experience: my hand-calculations failed twice in the calm phase (4D feeding is unreadable), and both games were ultimately decided by move-enumeration inside a cascade no human could evaluate unaided — agency becomes oracle-search precisely at the decisive moment, and the explosion-parity (both lines: P2 wins, same ply) suggests the winner may be substantially determined by timing structure rather than accumulated skill. Games lasting 14 plies of an allotted 98 also leave most of the design unvisited. High novelty, questionable game; slightly above R20's anchor on the strength of its genuinely original mechanics, below R8 because the strategic experience frays exactly where it matters: 3.9.
