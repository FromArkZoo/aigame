# Team 2 — Game D verdict

> Copy this template to `team-2_gameD.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game D` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  81-cell 4D torus (3×3×3×3; every cell has exactly 8 neighbors, and each axis line of 3 cells is a mutually-adjacent triangle). Players alternately place stones (must touch own stones; first stone anywhere, re-arming at zero). After EVERY action — including passes — a totalistic CA step runs over the whole board from the ACTOR's perspective: empty cells with (friendly,enemy) neighbor counts in {(1,2),(2,1),(2,5),(5,2),(6,6)} become the actor's; (3,6),(6,3) become the opponent's; the actor's stones die at (0,3),(1,5),(1,6),(3,4),(3,5); opponent stones die at (3,0),(4,3),(5,1),(5,3),(6,1). Classic capture/propagation are disabled. First to own 17+ cells (>0.2×81) wins; 98-step limit falls back to stone majority; double pass = draw; super-ko checked on the post-CA position.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Territory threshold in 3 lines (P1 18 stones at ply 15; P2 17 at ply 14; P1 18 at ply 21 in the policy-baseline line); one deliberate double-pass draw (Line 3, leader at 16-14 passed and the trailer accepted). Turn-limit tiebreak never approached — games are fast.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: (1) My own placement killed my own stone: playing 34 pushed my stone at (1,0,0,1) from (2 friendly,4 enemy) to the (3,4) death entry — overcrowding suicide, engine delta `X->.@(1,0,0,1)`. (2) A PASS really does run the CA for the passer: engine-verified pass at ply 11 of a Line-1 variant birthed 3 stones for the passing player (flagged "3 of these were CA mutations"). (3) Births/deaths are computed simultaneously on the post-placement state, so a placement can instantly convert an adjacent enemy pair-gap (my ply 11 fired 5 births in one action). (4) Super-ko never fired in any line; placements always net-changed the board.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `40,0,41,1,39,2,30,27,31,45,42,32,4,46,13`
- Plan and what happened: I built the immortal "triangle" shape (all 3 cells of an axis line — every stone keeps 2 friendly neighbors, which is outside every death entry, and the shape leaks no birth cells), then probed toward P2's cluster. The game became a cascade race: my ply 9 (cell 31) spawned an extra stone in P2's pair-gap (+2); scripted P2's ply 10 (cell 45) answered with a +4 sweep; my ply 11 (cell 42) fired FIVE simultaneous births (+6, engine-verified: 33,37,38,49,51); ply 13 (cell 4) fired three more (+4, including a birth inside P2's zone). My first attempt at the winning move (34) backfired by overcrowd-killing my own stone (net 0); the corrected move 13 birthed (1,0,1,0) for +2 and crossed the 17-stone threshold.
- Result (winner, end cause, plies): P1 win, territory threshold (18 vs 14), 15 plies.

### Line 2 — you as P2
- Moves: `0,13,27,40,54,67,2,4,28,10,46,9,5,7`
- Plan and what happened: P1 was scripted with the strongest policy I had (a depth-2 search over a rules-derived CA calculator, which as P1 beats the same policy playing P2 by 18-14 — see additional lines). Driving P2, I used deeper (rollout) analysis: I made early contact at 13 to poison P1's triangle line, matched P1's cascades ((1,2)-conversions at plies 8-10), landed a +6 sweep at ply 12 (placement 9 fired 5 births, engine delta confirms), and at ply 14 played cell 7 — a move that deliberately SACRIFICED my own stone at (1,0,0,0) to the CA (`O->.`) while birthing 4: net +3 to exactly 17 stones. All plies engine-verified.
- Result: P2 win, territory threshold (17 vs 14), 14 plies.

### Line 3 — adversarial / novelty-stress
- Moves: `40,0,41,1,39,2,30,27,31,45,42,32,4,46,81,81` (pass-trap); `40,0,41,1,39,2,30,27,31,45,81` (pass-sweep)
- What you tried to break / stress, and what happened: Three stress tests. (a) Pass-trap: with P1 LEADING 16-14, P1 passed; P2, losing on the board, simply passed back — engine declared DRAW. The double-pass rule converts any pass by the leader into a free draw offer to the loser, so passing while ahead is structurally forbidden. (b) Pass-sweep: at ply 11 of the Line-1 position, P1 passed and the CA still birthed 3 stones for the passer (engine: "3 of these were CA mutations") — passing is a real harvesting move, not a null move. (c) I attempted to construct a super-ko repetition and failed: every placement nets a board change and suicide-placements aren't reachable (placement requires a friendly neighbor, so a placed stone never has 0 friendly), so I observed no rollback; the rule looks near-vestigial here, though deaths make repetition possible in principle.
- Result: pass-trap line: DRAW by double pass at ply 16 (despite 16-14); pass-sweep line: verified +3 births on a pass, game in progress (probe).

### Additional lines (optional)
Policy baseline: both sides driven by the same depth-2 calculator policy → P1 wins 18-14 at ply 21 (moves `0,1,2,4,6,5,8,10,15,19,24,12,20,14,17,22,18,81,27,28,30`, engine-verified, including P2 rationally passing at ply 18). Under symmetric strength the first mover wins the harvest race; my Line-2 P2 win required strictly deeper search. Note on method: CA arithmetic in 4D is beyond reliable hand-calculation, so I built a neighbor-count calculator strictly from the printed `--rules` table and validated it against engine deltas (it reproduced the ply-11 five-birth cascade and full games exactly; one early mismatch was my own stale bookkeeping, not the engine).

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Every action is a global CA sweep for the actor: all cells at (2 friendly,1 enemy) or (1 friendly,2 enemy) become yours. So a good move (i) harvests all standing mixed cells (they always go to whoever acts next), (ii) uses the placement itself to tip more cells into birth counts — the best moves fire 3-5 births at once, (iii) avoids leaving (2,1)/(1,2) counts behind for the opponent's reply, and (iv) respects the overcrowding entries — adding a friendly neighbor to your own (2,4)/(2,5)-count stone kills it. The triangle (a full axis line) is the key defensive shape: immortal and birth-sterile.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Constantly. When P2 blocked my birth cell at 27 (Line 1 ply 8), the block was correct and cost me the cell; when P2 armed a cell adjacent to my pair-gaps (45), it harvested my structure for +4; when I left cell 29 armed, P2's next action took it. Every stone you place near the enemy is simultaneously fuel for their sweeps — the whole game is reciprocal arming/denial, and unanswered moves are punished within one ply.
- Topology/board effects on strategy: The 3-torus means axis lines are triangles: adjacent pairs share exactly 1 common neighbor, 2-axis diagonal pairs share exactly 2, and 3+-axis pairs share none — this dictates the entire birth geometry. No edges exist, so there are no safe walls; density is the only defense. The 8-neighbor uniformity plus the 17-cell threshold (~21% of the board) keeps games short and explosive.
- Emergent concepts you'd name (or "none observed"): "actor-harvest" (mixed cells belong to whoever moves next — tempo IS territory), "immortal triangle" (2-friendly-neighbor closed shapes that cannot die under any table entry), "arming/poisoning" (creating (2,0) pair-gaps is giving the opponent instant-birth fuel), "overcrowd suicide" ((3,4)/(3,5) deaths from your own reinforcement), "sacrifice finishers" (Line 2's winning move traded one of my stones for 4 births), "pass-harvest" and the "pass-trap" (leader can never pass safely because of the double-pass draw).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Choices decided everything, but through a computational veil: the deterministic CA punishes miscounting brutally (my ply-15 self-kill), and finding the multi-birth moves is the whole game. Between equal players the first-mover tempo probably decides it (policy baseline: P1 won); between unequal players, search depth dominated (my P2 win).

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  Two-player cellular-automaton games are established prior art: Immigration Game / p2life (two-color Life variants), and "place a stone then step the CA" is the core of several Life-based board games; the placement-adjacency rule is stock Go-variant fare, and territory-threshold wins are ordinary. One can argue this is "two-color Life on a torus with a stone-count victory," i.e., a parameter re-skin of p2life.
- Honest novelty assessment after arguing that case: The actor-perspective CA is a genuine departure from p2life-style symmetric updates: the SAME configuration resolves differently depending on who acts, which creates the actor-harvest/tempo economy, pass-as-harvest, and the pass-trap — none of which exist in symmetric two-color Life. The 4D 3-torus (all-lines-are-triangles) adjacency is structurally unlike any standard CA neighborhood I know, and the immortal-triangle/overcrowd-suicide table is bespoke. The asymmetric-by-actor totalistic table is the most novel single mechanic I've seen in this campaign's two games so far. Real novelty, with the caveat that the genre (CA-driven placement race) is known.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — I know the two-player-Life genre (p2life, Immigration) but not this specific rule table, board, or game, and I recall no prior score.
- P1-role experience sub-score (1-10): 4.5
- P2-role experience sub-score (1-10): 4.5
- Role-averaged sub-score: 4.5
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 2 — with both sides playing the identical depth-2 policy P1 won the harvest race 18-14 (ply 21), and my P2 win in Line 2 required strictly deeper search than the scripted P1, so equal-strength play tilts toward the first mover's tempo.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.3**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  This is the richest game of my set so far: Line 1's five-birth cascade (ply 11), the overcrowd suicide that punished my first finishing attempt, Line 2's sacrifice-to-win finisher (giving up a stone to net +3 and hit exactly 17), and Line 3's pass-trap/pass-harvest pair are all genuinely emergent, engine-verified phenomena arising from a compact rule table. Both roles are winnable and the arming/denial economy makes every ply interactive. It stays below the ceiling for two structural reasons: equal-strength play shows a real first-mover tempo edge (policy baseline 18-14), and the game is humanly illegible — I could not play it competently without building a calculator, which for a game evaluated as a game is a serious accessibility flaw; the threshold ending also cuts games off just as the board gets interesting. Above R8 and just below the R19 top anchor: 4.3.
