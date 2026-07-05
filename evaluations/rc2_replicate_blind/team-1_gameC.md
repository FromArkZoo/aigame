# Team 1 — Game C verdict

> Copy this template to `team-1_gameC.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game C` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  81-cell board that is a 3×3×3×3 torus — every cell has exactly 8 neighbors (±1 in each of four dimensions, wrapping), so the entire board is within graph distance 4 of everywhere and complete lines of 3 are mutual-adjacency triangles. Placement must touch one of your own stones (first stone anywhere; re-arms at zero stones). The only board-transformation mechanic is a cellular automaton applied once after EVERY action (including passes), evaluated from the ACTING player's perspective: mixed-contact empty cells birth stones for the actor (notably 2 friendly+1 enemy AND 1 friendly+2 enemy both become the ACTOR's), and specific neighbor-count patterns kill stones (e.g. your own stone with 0 friendly+3 enemy dies on YOUR tick; an enemy stone with 3 of yours+0 of theirs dies on your tick; overextended stones die at 5F+1E against them). Win: first to own 17+ of 81 cells; 98-ply limit with stone-count tiebreak; double-pass draw; super-ko checked on the post-CA position.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Territory win twice (line 1: P1 reaches 20 cells at ply 21; line 2: P2 reaches 17 at ply 22); double-pass draw once (line 3, ply 10, after the engineered wipe/re-arm demo). Never near the 98-ply tiebreak — CA births make the race fast.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: The engine matched the printed CA table exactly, but the table's consequences kept outrunning my 4D bookkeeping in instructive ways: (1) a "bonus" birth at (1,1,2,1) in line 1 via the d2 wrap (2 friendly through the torus seam + 1 enemy) that I hadn't predicted; (2) in line 2 BOTH of X's stones planted inside my block were later killed by the (5F,1E) encirclement row as my births accumulated around them — deaths I only half-foresaw; (3) my own forward stone died on X's tick once X assembled 5 neighbors. Every surprise was deterministic and reconstructible afterwards from the table, which speaks well of the engine; the helper's "N of these were CA mutations" flag made verification possible.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `40,0,41,1,39,2,37,3,43,6,36,4,38,5,42,7,44,8,13,22,31`
- Plan and what happened: I built a 3×3 plane fortress in two dimensions at (·,·,1,1) — every plane stone has 4 friendly neighbors, which sits outside every death row in the table — while scripted P2 mirrored at (·,·,0,0). With both planes complete (9 v 9, zero CA events, as predicted: births need enemy contact), I discovered the "5-stone bomb": placing at the center of a contested inter-plane block creates four simultaneous (2F,1E) births. My ply-19 bomb at (1,1,1,0) went 9→14; O counter-bombed (1,1,2,0) to reach 14; my second bomb at (1,1,0,1) birthed five (including the wrap bonus) for 20 ≥ 17.
- Result (winner, end cause, plies): P1 (me) win, territory (20/81 ≥ 17), ply 21. My analysis of O's alternatives (blocking one bomb site, pre-poisoning a birth cell) found no defense — the two contested blocks can't both be denied and even a poisoned cell leaves +4.
- 
### Line 2 — you as P2
- Moves: `40,49,41,50,39,46,37,47,43,31,35,53,36,27,29,58,42,48,38,52,13,22`
- Plan and what happened: Against the same P1 plane-build (scripted), I played a "leech": my plane went in the block ADJACENT to X's (d2-neighbors), so X's own stones supply the enemy counts my births need. Cost: pending cells resolve to whoever acts, so X's plane-completion moves stole two cells inside my block (engine-confirmed at plies 5 and 9), and my (1F,2E) invader at (2,0,1,1) — born inside X's plane from my own placement — was eventually executed by X's (5F,1E) encirclement at ply 15. But the economics favored me decisively: my 4-placement plane finished as 7 stones via births, my (0,1)-block bomb fired all four cells (two via the aggressive 1F+2E rule even where X outnumbered me), and my accumulating births then KILLED both of X's stolen stones via (5F,1E). From 14 v 8 I walked in the last three stones.
- Result: P2 (me) win, territory (17/81), ply 22, final 17–13. Notably X's bombs were duds all game: bombs require an enemy neighbor, and the leech had placed all my stones where they fed MY births, not his.

### Line 3 — adversarial / novelty-stress
- Moves: `40,67,13,81,39,81,66,0,81,81` (plus probe `40,40`)
- What you tried to break / stress, and what happened: (1) CA kill and re-arm: P2's lone stone at (1,1,1,2), deliberately parked next to P1's cluster, was killed the moment P1 assembled 3 neighbors — the (3F,0E) opponent-cell row fired on P1's ply-7 tick, dropping P2 to zero stones; the engine then correctly re-armed first_move_anywhere (P2's legal set = all 77 empty cells). (2) Pass semantics: single passes interleaved with placements (plies 4, 6, 9) did not end the game; the first genuinely consecutive pair (plies 9-10) ended it as a draw. (3) Placement on an occupied cell rejected with a clean ILLEGAL message. I also note super-ko never fired in any line — unlike static games, stones here strictly accumulate or die via CA, and no oscillating configuration arose in my play.
- Result: DRAW, double pass, ply 10. All engine behaviors consistent with the rules text.

### Additional lines (optional)
None beyond the three — but line 1 plies 1-18 doubles as a control experiment: two non-contacting plane builds produced ZERO CA events across 18 plies, confirming that every birth/death row in the table requires enemy contact and that quiet building is CA-silent.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Maximize births-per-placement. A good move completes a 2:1 mixed count on as many adjacent empties as possible at once (the bomb: 1 placement → 4-5 births); a great move does it using the OPPONENT's stones as the enemy count (the leech), so their structure powers your growth. The other half of the loop is death engineering: build toward (5F,1E) around enemy stones embedded in your zone — they die on your tick without costing a move dedicated to "capture."
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Strongly. When I leeched X's plane, X's plane completions auto-stole my pending cells (the actor-takes-all rule cuts both ways); when I planted an invader in X's plane, X answered with a two-move encirclement that executed it; when X mirrored my build far away (line 1), the punishment was that pure racing loses to first-mover tempo. The actor-perspective CA makes every single action a global sweep for ripe cells, so timing — completing conditions on YOUR tick, never leaving them for the opponent's — is the entire tactical texture.
- Topology/board effects on strategy: The 4D 3-torus is load-bearing: axis lines are 3-cliques, so "planes" are dense fortresses (4 friendly neighbors each, immune to every death row); blocks have 4 block-neighbors, creating a metagame of contested blocks; and wrap adjacency (d=0 vs d=2) produces births through the seam that flat-board intuition misses — one decided a bonus stone in my line-1 win.
- Emergent concepts you'd name (or "none observed"): "Bomb" (center placement of a contested block, +4 births); "leech" (build adjacent to the enemy so their stones feed your birth counts); "pending poisoning" (never complete a 2:1 condition on the opponent's harvesting tick); "fortress plane" (the 4F-everywhere shape outside all death rows); "encirclement execution" ((5F,1E) and (3F,0E) as move-free kills); "actor-takes-all" (both 2F+1E and 1F+2E resolve to whoever moved — aggression is always rewarded on your own tick).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Choices decided both competitive lines — line 1 by finding the bomb before the mirror-opponent, line 2 by choosing leech over mirror — but agency is mediated through a CA that is genuinely hard to read in 4D: I made several local mispredictions (a stolen cell, an unforeseen death) that the engine adjudicated against me even while my overall plan won. High strategic agency, medium tactical legibility.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  Two-player cellular-automaton combat is a known genre (Immigration/two-color Life variants, CA-based war games), stone-count racing is Go/territory boilerplate, and "grow from your own stones" is a standard growth constraint. One could frame this as "two-color Life on a torus with a first-to-N stone count," and the 4D board as mere size disguise — 81 cells is just a 9×9 with exotic wiring.
- Honest novelty assessment after arguing that case: The reduction fails on the mechanic that actually runs the game: the CA is evaluated from the ACTING player's perspective after every half-move, with an asymmetric hand-built table (actor-takes-all births at 2:1, perspective-dependent deaths) — that is not Life-like symmetric evolution, it is a tempo mechanic I have not seen in any prior game, and every emergent concept I found (bombs, leeching, pending poisoning) flows specifically from it. The 4D 3-torus is also not disguise: line-cliques, block adjacency, and seam births all shaped strategy in observable ways. This is the most genuinely novel game of my slate; its closest priors are genre-level, not game-level.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — I recognize the genre ingredients (CA combat, territory race) but no specific prior game, and no prior score.
- P1-role experience sub-score (1-10): 4.5 — the build-then-bomb discovery arc in line 1 was excellent, and the win felt fully earned by analysis.
- P2-role experience sub-score (1-10): 4.5 — the leech strategy was the single best strategic find of my whole evaluation, and it produced a genuine comeback structure (behind 8-6 at ply 9, winning 17-13 at ply 22).
- Role-averaged sub-score: 4.5
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 3 — P1 won the symmetric-mirror line on pure tempo (ply 21 vs a would-be ply 22) but P2 won the asymmetric line by leeching, and my analysis suggests the reactive player's leech is at least as strong as the first player's tempo, leaving no clear structural favorite.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.4**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  Game C pairs the highest novelty of my slate (an actor-perspective CA with a hand-crafted asymmetric table on a 4D torus — no game-level prior I can name) with real, discoverable depth: line 1's bomb (engine-verified +5 in one action, including a torus-seam birth) and line 2's leech (winning by feeding on the opponent's structure, 17-13) are strategies I derived, tested, and in one case had refuted in detail by the engine's exact CA arithmetic. Both roles won a line with genuinely different plans, and the adversarial line confirmed even the exotic corners (actor-tick kills, zero-stone re-arm) work as written. It stays at 4.4 rather than pressing the ceiling because tactical legibility is poor — even careful analysis mispredicts individual births/deaths, which on a human table would read as chaos — and because the opening ~17 plies of quiet building are low-interaction. Slightly above R19's 4.375 on the strength of novelty-plus-depth, still well under the never-cleared 5.0.
