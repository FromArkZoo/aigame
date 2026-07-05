# Team 2 — Game A verdict

> Copy this template to `team-2_gameA.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game A` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  8×8 orthogonal grid. Placement must be adjacent to ANY stone (either colour; waived at zero stones). MOVE actions relocate one of your stones to an adjacent cell and may OVERWRITE an enemy stone there. After every action (including passes) a one-iteration totalistic CA runs from the actor's perspective. Only five transitions are reachable on this board: empty cells at (1 friendly, 2 enemy) or (2,1) birth to the ACTOR; the actor's own stone with zero neighbors of either colour flips to the OPPONENT; the actor's stone at (1F,3E) flips to the opponent; and an opponent's stone at (3F,1E) — or isolated — flips to the actor. Win: territory race, first to 30 of 64 stones; 100-step limit with count tiebreak; double pass = draw; super-ko rollback.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Win condition in both competitive lines (Line 1: P2 at ply 44, 31-26; Line 2: P1 at ply 39, 31-18 — in each case the winner's final action triggered births crossing 30). Double-pass draw at ply 2 in the stress line — and that draw is not a curiosity but the game's apparent rational equilibrium (below).
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: (1) The isolated-stone rule makes the FIRST PLACEMENT OF THE GAME a forced gift: a lone stone has (0F,0E), so the opening placement flips to the opponent on its own tick (verified: my 27 became O instantly). (2) Passes are substantive actions: in the stress line, P2's PASS flipped an isolated O stone to X — from the passer's perspective it was their own isolated stone, so it flipped away. Isolated stones ping-pong ownership on every action until someone attaches to them. (3) A MOVE that overwrites an enemy stone can show a net-zero board delta in its origin cell: my (3,2)→(4,2) overwrite converted his stone AND the vacated (3,2) was re-birthed to me by the same CA tick — engine-verified as a single O->X delta. (4) Moving a stone into isolation self-gifts it (my ply-11 move landed and flipped to O in one tick).

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `27,28,19,20,12,21,11,13,14,5,15,4,23,18,7,3,2,1,17,0,26,16,30,37,35,44,24,25,31,34,33,39,42,32,46,53,51,60,40,41,47,54,62,63`
- Plan and what happened: I deliberately paid the gift tax (27 flipped to P2) to test whether contact play recovers it. The early middlegame was genuinely positional: I fought for birth cells (my (7,2) placement birthed (6,2) via the 2F+1E rule), set steal threats (two of my stones flanking his (5,1) would have flipped it), and he punished my thin shape with the mirror steal — his (4,0) placement flipped my (4,1) via (3F',1E'). From ply 13 I drove both sides with a greedy one-ply sweep (maximize post-action stone differential, candidates from the legal list — every move engine-evaluated); the deficit from the gift plus the lost steal exchange never closed, and his ply-44 action birthed him over the 30-stone bar.
- Result (winner, end cause, plies): P2 win, territory (31 vs 26), ply 44.

### Line 2 — you as P2
- Moves: `64,27,19,11,3,2,18,9,12,28,21,1,0,4,5,6,7,8,16,25,34,36,29,13,43,15,14,23,30,38,44,39,45,47,24,32,40,41,50`
- Plan and what happened: Scripted-competent P1 opens with the correct move — PASS (Line 1 established that placing first is a gift). As P2 I refused the mutual-pass draw and gifted at 27 to fight for a win, then both sides continued under the same greedy sweep. The result was even more lopsided than Line 1: P1 absorbed the gift, out-stole and out-birthed me all game, and crossed 30 at ply 39 (31-18). Combined with Line 1, this is a role-swapped replication: THE GIFTER LOSES FROM EITHER SEAT, by 5 and by 13 stones — strong evidence that the opening has no compensation and the game's rational value is a ply-2 draw.
- Result: P1 win, territory (31 vs 18), ply 39.

### Line 3 — adversarial / novelty-stress
- Moves: `64,64` and `27,28,19,20,12,21,11,13,142,64,141,64` (+ `--legal` MOVE decoding)
- What you tried to break / stress, and what happened: (a) The equilibrium draw: pass-pass ends the game 0-0 at step 2 ("double pass -> draw") — two rational players never play at all. (b) Overwrite MOVE: action 142 moved my (3,2) stone onto his (4,2), converting it, while the CA re-birthed my vacated origin cell in the same tick — a startlingly efficient double-purpose action (net +1 me, -1 him, no placement spent). (c) Isolation dynamics: moving that stone to an empty flank isolated it and it flipped to P2 on my own tick; P2's subsequent PASS flipped it back to me (the passer counts as actor). (d) My attempted shuffle repetition for a super-ko test was pre-empted by these flips — positions mutate too much for casual repetition; super-ko remained untriggerable in my A play (consistent with flips constantly changing the board).
- Result: draw (by design) and mechanics findings; no conventional contest.

### Additional lines (optional)
Candidate sweeps at plies 4-13 of Line 1 (engine-evaluated, 5-8 candidates each) are part of the record above; they establish that early moves produce no CA events until contact shapes mature — Game A is the slowest-burning of the three CA games in this set.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Once past the (broken) opening: fight for birth cells and steal patterns. A good placement (i) sits where it turns an empty cell into a (2F,1E) birth for you next tick, (ii) denies the mirror-image cell to the opponent (occupy his birth cells before they trigger), and (iii) avoids leaving your own stones at (3 enemy, 1 friendly) or reachable isolation, since those flip on schedule. The MOVE-overwrite is the strongest single action when available: it converts an enemy stone AND can re-birth its origin. All of this is fully human-readable — one CA iteration, four neighbors, five live rules — the most legible of the three CA siblings in this set.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Yes, concretely: my steal threat on (5,1) forced his defensive (5,0); his (4,0) steal of my (4,1) punished my thin flank shape; birth-cell pre-emption (his 22 blocking my (6,2) birth) was a recurring duel. The one place counterplay fails is the meta-level: the correct response to the opening is to not play, and no in-game cleverness I found compensates the gifter.
- Topology/board effects on strategy: Plain 8×8 with 4-adjacency caps neighbor counts at 4, which prunes the rule table to five live transitions and makes the CA tractable; edges reduce steal and birth geometry (corner stones can never suffer (1F,3E)); and the adjacent-to-ANY-stone placement rule keeps all action in one connected theater — no second fronts, unlike the own-adjacency games in this set.
- Emergent concepts you'd name (or "none observed"): (1) "The gift tax" — the first substantive placement of the game is a forced donation; (2) "isolation ping-pong" — unattached stones flip to whoever acts, every action, passes included; (3) "birth-cell pre-emption" — occupying cells before they trigger for the opponent; (4) "steal geometry" — engineering 3-vs-1 flanks; (5) "overwrite-rebirth" — the move action's double profit.
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Mid-game agency is real and readable (I planned steals and births by hand and they fired as calculated — unlike its CA siblings, no oracle needed). But the OUTCOME of both competitive lines was substantially decided at ply 1-2 by who paid the gift tax, and the meta-game reduces to "don't play first," which caps how much any later choice matters. High local agency, broken global agency.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  Third member of this set's actor-perspective-CA family (with C and E): same skeleton — totalistic table from the actor's viewpoint, births at (1,2)/(2,1), territory-threshold win — on the tamest board, with the MOVE action recycled from the non-CA movement games. As an external matter, two-player Life-like territory games are a known genre; nothing in the component list is new.
- Honest novelty assessment after arguing that case: Fair, with one genuinely distinctive wrinkle: the isolated-stone flip rule, which produces both the game's most original texture (ownership ping-pong, passes as weapons) and its fatal flaw (the forced-gift opening and the resulting ply-2 draw equilibrium). The overwrite-move + same-tick-rebirth interaction is also a neat, novel micro-mechanic. Novelty: modest — and the most novel rule is the one that breaks the game.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — no external prior recognized, no prior score recalled (kinship to blind-set siblings C and E noted, not a recognition).
- P1-role experience sub-score (1-10): 3.3
- P2-role experience sub-score (1-10): 3.5
- Role-averaged sub-score: 3.4
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 3 — the asymmetry is not between seats but between roles-in-the-opening: the gifter lost from both seats (31-26 as P1's gift, 31-18 as P2's gift) while the passer profits, and since P1 can simply pass, the equilibrium is a balanced (and empty) draw.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 3.3**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  The middlegame layer deserves real credit: birth-cell duels, steal geometry, and the overwrite-rebirth move are readable, plannable, and fun — the best agency-to-chaos ratio of this set's three CA games, and my Line 1 steal exchanges were genuine tactics. But a competitive game must survive its own opening, and this one doesn't: the isolated-stone rule makes the first placement a verified gift, my role-swapped Lines 1 and 2 show the gifter losing decisively from either seat, and the stress line confirms that two players who both understand this draw at step 2 without placing a stone. Everything good in the game is gated behind an irrational act. That is a deeper defect than R20/R21-level dullness — it is a broken equilibrium — so I score below both: 3.3.
