# Team 1 — Game B verdict

> Copy this template to `team-1_gameB.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game B` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  8×8 grid, von Neumann adjacency, free placement, Go-style surround capture (adjacent enemy groups at zero liberties are removed after your action), plus a MOVE action: relocate one of your stones to an adjacent empty cell (ids encode from-cell and a [W,E,N,S] neighbor slot). Win by stone-count: first to own 41+ of 64 cells; at 100 plies the higher count wins; two consecutive passes end it as a literal DRAW regardless of count; positional super-ko rolls repeating actions back into passes. Since 41 > 32 = half the board, an outright win REQUIRES large-scale captures — peaceful division cannot reach the threshold. Critical engine behaviors established in play: suicide placements that capture nothing are legal and the stone STAYS (creating permanently uncapturable zero-liberty stones/groups), and MOVE actions do trigger capture checks.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Threshold win twice (line 1: P1 hits exactly 41 at ply 81; line 2: P2 hits 41 at ply 90); double-pass draw once (line 3, ply 28, immediately after a super-ko rollback had already converted P1's move into the first pass). I never reached the ply-100 tiebreak, and my endgame analysis suggests it is nearly unreachable between competent players: the board fills before ply 100, a full board leaves only passes, and double-pass draws the game even at lopsided counts — the leader must deliberately burn plies with non-repeating MOVEs to reach 100, and super-ko caps how long that clock can run.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: Three major surprises. (1) Suicide-stays: X filled one eye of O's two-eyed group with a zero-liberty stone that persisted (line 1, ply 35) — then filling the second eye killed the whole "unconditionally alive" group. Two eyes provide NO life in this engine; no group is ever safe. (2) The whole-board capture: in line 2 the board filled to 63 stones with X's entire 32-stone force forming one giant group whose last liberty was the last empty point — my placement there captured all 32 stones at once. (3) MOVE actions trigger captures (line 3 ply 23: a relocation completed a surround and removed the victim), and a move-shuffle that recreates a position is rolled into a PASS (flagged at ply 27), which directly enables forced-draw traps.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `27,36,28,35,34,37,43,44,45,29,21,30,22,31,23,39,52,38,46,9,47,1,2,8,10,17,18,24,26,25,33,32,40,64,0,64,16,64,1,64,3,64,4,64,5,64,6,64,7,64,8,64,9,64,11,64,12,64,13,64,14,64,15,64,17,64,19,64,20,64,24,64,25,64,29,64,30,64,31,64,35`
- Plan and what happened: From a center crosscut I chased O's wall with a closing net — O kept extending a group that always had 3-4 liberties until the squeeze at (4,6)/(6,5) left the whole nine-stone chain in atari; (7,5) captured all nine at ply 21. O then built a textbook two-eyed corner fortress (eyes at (0,0) and (0,2)); I walled it, filled eye one with a legal suicide stone that persisted, filled eye two, and removed the entire seven-stone "living" group. From there I filled to the threshold against passes.
- Result (winner, end cause, plies): P1 (me) win, territory threshold (41/64), ply 81, final 41-0. Two mass captures (9 and 7 stones) plus the eye-fill demonstration.

### Line 2 — you as P2
- Moves: `27,36,28,35,19,44,37,45,29,38,30,46,39,47,31,34,33,42,41,49,50,51,58,57,18,60,48,59,20,53,62,54,63,55,12,61,4,62,26,9,10,17,25,8,24,16,32,43,1,0,40,56,50,52,58,63,49,14,56,15,57,6,13,7,5,22,21,23,2,11,3,11,27,24,28,25,4,26,12,29,5,30,13,31,21,18,1,19,2,20`
- Plan and what happened: A long, swingy fight. I won two local races early (capturing X's two-stone cutter at (3,7) and a two-stone corner invasion at (5,7)), X counter-captured three of my stones in the northwest, my invading north group ran out of liberties and I deliberately filled its own last liberty to convert it into a five-cell IMMORTAL zero-liberty pocket, and I repeated the trick with a six-cell pocket in the southeast corner. Then the game's most extraordinary event: with (3,1) the only empty point left on the board, X's entire 32-stone army had fused into one group with that single liberty — my placement there captured all 32 stones at once (engine delta: 32 removals). I rebuilt over the ruins to 41.
- Result: P2 (me) win, territory threshold (41/64), ply 90. (I note honestly: my first scripted ending passed twice right after the mega-capture, producing a 32-0 double-pass DRAW — the draw rule really does ignore the count — so I re-drove the tail with correct play; both endings are engine-verified.)

### Line 3 — adversarial / novelty-stress
- Moves: `1,9,8,33,10,34,25,104,18,133,17,131,16,163,3,5,4,21,14,29,13,37,123,216,91,247,123,64`
- What you tried to break / stress, and what happened: Full MOVE-mechanic workout. (1) Escape-by-move: my O stone in atari at (1,1) relocated to (1,2), then fled along the edge for three more moves while X chased with placements — vacated cells correctly became liberties for the mover. (2) Move-triggers-capture: X's MOVE (6,1)→(6,0) completed a surround and captured O(5,0) — relocations are full capture events. (3) Shuffle super-ko: after both sides shuttled a stone back and forth, X's attempt to repeat the earlier position was rolled back into a PASS with an explicit SUPER-KO flag; O then passed, ending the game as a double-pass draw. Also confirmed the id encoding (64+1+from*4+neighbor-slot in [W,E,N,S] order, compacted at edges) matches --legal's decoding.
- Result: DRAW, double pass, ply 28. Every probe behaved consistently; the super-ko-into-pass interaction is exactly the mechanism that bounds endgame clock-burning.

### Additional lines (optional)
None — but the aborted first ending of line 2 (`...,11,64,64` instead of the rebuild) is itself a documented finding: a 32-0 position ended as DRAW by double pass, proving the draw rule is count-blind.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Fight to kill, not to live — since two eyes confer nothing, every group is permanently attackable, so good moves either grow a group's liberty count faster than the opponent can fill, or close a net that wins a whole chase. The second loop is liberty bookkeeping at board scale: as the board fills, connected masses share fewer liberties, and the player who forces the opponent's mass to absorb its own last outside liberty wins everything at once (my 32-stone capture was this, taken to the theoretical limit).
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Yes, richly: extending a chased group was punished by the closing net (line 1); my careless northwest shape was punished by a three-stone counter-capture (line 2); X's corner invasion was punished by sealing its last liberty. The endgame rewards a different kind of response: racing to fill your own single-point holes before the opponent squats them with immortal suicide stones, and converting doomed groups into zero-liberty immortal pockets before the opponent takes their last liberty — a completely non-Go form of counterplay that both sides used.
- Topology/board effects on strategy: Plain 8×8 with 4-adjacency: edges accelerate kills (chases die at the rim), corners are where immortal pockets are cheapest to build (fewest liberties to self-fill), and the small board means one connected mass can absorb everything — which is precisely what makes the whole-army capture possible.
- Emergent concepts you'd name (or "none observed"): "Eye-fill kill" (suicide-stays deletes the concept of life); "immortal pocket" (self-filling your group's last liberty locks its cells forever — defense by voluntary petrification); "suicide squat" (stealing an enemy single-point hole with an unkillable stone); "whole-army liberty collapse" (one empty point = one shared liberty for a 32-stone mass); "count-blind draw trap" (double pass draws even at 32-0, so the leader must always have a non-pass, non-repeating action available); "shuffle clock" (burning plies with MOVEs, bounded by super-ko).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Choices dominated: both decisive lines turned on found tactics (nets, eye-fills, pocket petrification, the last-liberty count). But the endgame layer has a scripted-feeling attractor — full board → forced passes → draw — that punishes ignorance of the meta-rules more than bad fighting; a player who doesn't know the draw is count-blind can "win" the board and draw the game, which is agency of a strange kind.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  This is stone-scoring Go ("all-stones-count" Go, cf. ancient/stone-scoring rules) on 8×8: surround capture, super-ko, count-based winning. The MOVE action echoes hybrid Go variants and the placement/movement split of games like Conhex-era hybrids; the 41-cell supermajority threshold is just a scoring dial. An evaluator could say: Go with a house rule about moving stones and a broken suicide rule.
- Honest novelty assessment after arguing that case: The reduction captures the surface but inverts the soul. Suicide-stays abolishes life-and-death — the single deepest structure of Go — and replaces it with a genuinely different endgame calculus (immortal pockets, eye squats, whole-board liberty collapse) that I have not seen in any Go variant; the count-blind double-pass draw plus MOVE-plus-super-ko creates a clock/zugzwang layer that is also not Go. Whether these are DESIGNED novelties or artifacts is unknowable from the rules text alone, but they are load-bearing and produce coherent, learnable strategy. Moderate novelty: derivative core, genuinely novel (if accident-flavored) end structure.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — the core is recognizably Go-family (stone-scoring Go being the nearest prior), but I don't recognize this specific variant or any prior score.
- P1-role experience sub-score (1-10): 4.5 — the chase-net capture and the eye-fill discovery made line 1 a strong experience with a clean conversion.
- P2-role experience sub-score (1-10): 4.5 — line 2 had the single most dramatic engine-verified moment of my entire slate (the 32-stone whole-army capture) plus the immortal-pocket tech, though the endgame bookkeeping got fiddly.
- Role-averaged sub-score: 4.5
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 3 — each role won its competitive line and drew nothing structural; P1's tempo matters less than fighting skill because free placement lets either side pick every fight, and the draw-attractor endgame is symmetric.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.0**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  Game B produced spectacular play — a 9-stone net kill and an eye-fill execution in line 1, and in line 2 a 32-stone whole-army capture that is the most memorable single move of my slate — and its capture-or-nothing scoring (41 > half the board) correctly forces fighting games. But the same engine behaviors that create its novel endgame also read as design damage: suicide-stays deletes life-and-death entirely (a fortress with two eyes is worth nothing, which most players would experience as a rules betrayal), the double-pass draw is count-blind (my 32-0 position drew — verified), and equilibrium play seems to funnel toward full-board forced draws unless someone wins a total war. High drama, real depth, but with degenerate corners a strong player can and must exploit; that puts it a notch below R8's 4.10. Overall 4.0.
