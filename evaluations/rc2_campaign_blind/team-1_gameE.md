# Team 1 — Game E verdict

> Copy this template to `team-1_gameE.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game E` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  8×8 orthogonal grid. Each turn: place a stone on any empty cell, MOVE one
  of your stones to an adjacent empty cell, or pass. Go-style surround
  capture fires after placements AND after moves (engine-verified: my move
  into a liberty captured a stone). No self-capture check — suicide is
  legal and zero-liberty stones persist ("undead", as in the engine's other
  Go-capture game). Win by owning ≥41 of 64 cells, or by most stones when
  the 100-step limit hits; double pass draws; positional super-ko rolls
  repeating actions (including MOVE shuttles) back into passes.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Both decisive lines ended by the step-100 piece-count tiebreak (37–22 and
  29–22) — the first turn-limit terminals of my whole evaluation. The
  41-stone threshold is close to unreachable by my analysis: a maximal
  5-column territory holds 40 cells, eyes cost 2, and even stuffing the
  opponent's eyes with undead suicides caps out at 40; you would need to
  kill wall chunks outright. Line 3 ended in a double-pass draw at step 7
  via a super-ko'd move shuttle.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: (1) Moves trigger captures — the rules text says "after
  your placement", but the engine applies surround capture after MOVE
  relocations too (verified ply-5 probe: move-in kill). (2) Moving a stone
  back recreates the prior position and is rolled into a PASS, which can
  end the game (Line 3: my shuttle-return became pass #2 of a double pass).
  (3) The endgame demands "shuffle discipline": once territories are
  sealed, the leader must burn ~40 plies making non-repeating moves —
  passing even once lets the loser pass for the draw.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `3,2,11,10,19,18,27,26,35,34,43,42,51,50,59,58,4,29,21,30,28,22,37,14,38,13,12,5,6,15,7,23,39,1,222,16,20,24,36,32,44,40,52,48,60,56,5,9,13,17,29,25,45,33,53,41,61,49,14,57,22,69,30,65,46,69,54,65,15,69,23,65,39,69,55,65,223,69,191,65,159,69,127,65,94,69,90,65,86,69,82,65,78,69,111,65,113,69,117,65`
- Plan and what happened: I claimed the five right columns with a solid x=3
  wall against his x=2 wall (40 cells vs 24 — stone-scoring logic makes the
  bigger zone decisive). He invaded my zone with an 8-stone snake; I
  contained it patiently and delivered the killing liberty-fill with a MOVE
  (action 222, sliding (7,4)→(7,3)) — an 8-stone capture that placements
  alone could not have timed as well. Then ~30 plies of zone-filling
  (keeping three eye cells) and ~25 plies of non-repeating shuffle moves to
  reach the step-100 tiebreak without ever passing.
- Result (winner, end cause, plies): P1 wins by max-turns piece-count
  tiebreak at step 100; 37 stones v 22.

### Line 2 — you as P2
- Moves: `2,3,10,11,18,19,26,27,34,35,42,43,50,51,58,59,28,20,29,36,21,37,22,13,14,23,6,15,5,12,7,38,0,219,8,4,16,44,24,52,32,60,40,45,48,53,1,61,9,38,17,46,25,54,33,31,41,39,49,55,259,82,227,78,74,86,70,82,65,85,98,82,78,90,66,86,69,89,73,86,81,89,70,85,65,82,98,85,101,82,78,86,74,89,70,86,65,89,71,86`
- Plan and what happened: Mirror doctrine from the P2 seat: scripted P1
  took a greedy small base (x=2 wall) and launched a deep 8-stone invasion
  of my big zone; I built the containment net move by move (20, 36, 37, 13,
  23, 15, 12), tightened with a MOVE (219, (6,4)→(6,3)), and his whole
  group came off the board at ply 36 when my placement at (4,0) filled its
  last liberty. From there: fills with eye discipline and a 40-ply
  non-repeating shuffle to the horn.
- Result: P2 (me) wins by max-turns piece-count tiebreak at step 100;
  29 stones v 22.

### Line 3 — adversarial / novelty-stress
- Moves: `1,20,70,64,73,64,70`
- What you tried to break / stress, and what happened: Move-shuttle
  repetition: I moved a stone out (70), back (73 — legal, because the
  to-move player differed from the earlier occurrence), his pass, then out
  again (70) — which exactly recreated an earlier position and was flagged
  SUPER-KO, rolled back to a pass, and combined with his preceding pass to
  end the game. Also verified in probes: move-triggered captures (a MOVE
  into the last liberty removed the enemy stone) and legal suicide with a
  persistent zero-liberty stone.
- Result: DRAW by double pass at step 7, with the second "pass" being a
  super-ko rollback of a MOVE — the engine's repetition, movement, and
  pass-counting rules interlock exactly as documented.

### Additional lines (optional)
Endgame theory I derived and partially verified: the leader must keep
empty cells in PAIRS — a lone surrounded empty is an invitation for the
opponent to place an undead suicide stone there permanently (it can never
be captured, since capture requires an adjacent placement and no empty
ever borders it). Against eye invasions of paired empties, MOVE-captures
are the correct response because they preserve the empty count by
relocating it. A leader who runs out of safe non-repeating moves before
step 100 is forced to pass and concedes a draw — "time-wasting capacity"
is a real resource in this game.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Claim the bigger zone with a solid wall (stone-scoring: cells ARE
  points), contain invasions with liberty-counting, and prefer MOVEs over
  placements when reshaping — they deliver captures with tempo and manage
  your empty-cell topology without spending a stone. In the endgame, a
  good move is simply any legal move that doesn't repeat a position.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Invasions died to methodical
  containment in both lines (8 stones each time) — over-extension into a
  walled zone is unpunishable-by-him and fatal. The subtler counterplay is
  defensive: eye-stuffing undead invasions punish single-cell empties, and
  passing punishes nothing but yourself.
- Topology/board effects on strategy: Plain 8×8 orthogonal — the flattest
  topology in my set. Column arithmetic dominates (a one-column bigger
  zone = +8 stones at the horn); edges make containment cheap; the
  41-threshold at 63% of the board is calibrated so that walls alone
  cannot reach it, forcing captures for a threshold win.
- Emergent concepts you'd name (or "none observed"): "shuffle discipline"
  (burning turns without repetition or passes), "eye-pair maintenance",
  "undead eye-stuffing", "move-capture tempo", "zone arithmetic".
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Choices decide it, and they're
  readable Go-like choices (walls, liberties, containment). But a large
  fraction of a decisive game — 40 plies in my lines — is ritual: legal,
  content-free shuffling that neither player can skip. Agency is high in
  the first 60 plies and nearly zero (but mandatory) in the last 40.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  This is stone-scoring (ancient Chinese) Go on 8×8 with a majority
  threshold, plus a piece-relocation option found in many Go variants;
  surround capture, super-ko, and pass rules are Go verbatim. Every
  strategic concept I used (walls, liberties, containment, eyes) is Go
  theory applied without modification.
- Honest novelty assessment after arguing that case: Substantially a Go
  re-skin. The additions do generate new texture — move-captures, empty-
  region management via relocation, and the shuffle/repetition endgame are
  not Go — but the first two are minor variations and the third is closer
  to a rules artifact than a designed dynamic. Lowest novelty in my set.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none for the specific game; the family is
  transparently stone-scoring Go with movement, as argued in Phase 4.
- P1-role experience sub-score (1-10): 4.0
- P2-role experience sub-score (1-10): 4.0
- Role-averaged sub-score: 4.0
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 3 — I won from
  both seats using the same zone-arithmetic doctrine (37–22 as P1, 29–22
  as P2), the goals are fully symmetric, and the first-placement tempo
  edge never manifested as more than a marginal count difference.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 3.9**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  Game E plays soundly and rewards genuine skill — both my wins (Lines 1
  and 2) came from correct zone arithmetic and clean 8-stone containment
  kills, with the MOVE mechanic contributing real tactical content
  (move-captures at 222/219, the super-ko shuttle in Line 3). But it is
  the least novel game in my set (stone-scoring Go with relocation), its
  headline win condition (41 stones) is practically unreachable so games
  funnel into the step-100 tiebreak, and reaching that tiebreak obliges
  both players to perform ~40 plies of contentless, repetition-dodging
  shuffle moves while draw loopholes (eye-stuffing undead, pass baiting)
  lurk for the careless. Solid but derivative with a degenerate endgame:
  3.9, just under R8.
