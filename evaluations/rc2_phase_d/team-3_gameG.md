# Team 3 — Game G verdict

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  8×8 hex board, no capture, no influence. Alternating turns. Three action
  types: **PLACE** a stone on an empty cell adjacent to an enemy stone (first
  move anywhere); **PASS**; **MOVE** one of your stones to an adjacent empty
  cell. **Win = first to own ≥28 stones.** Crucially, MOVE does **not** change
  your stone count, so only PLACE advances you toward the 28-stone target.
  Super-ko: any action recreating a prior position is rolled back to a pass.
  100-step tiebreak by stone count; double pass = draw. This is **Game-C's
  territory race with a MOVE action and super-ko bolted on.**
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw): 28-stone win
  condition every real game — Line 1 (P1 @ ply55, 28-27), Line 2 (P1 @ ply55,
  28-26 after P2 wasted a MOVE). Super-ko rollback observed in Line 3. No
  turn-limit or draw outcomes in racing play.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: The MOVE action looked like it might add depth, but observation
  confirmed it is **strictly dominated** — because moving keeps your count flat
  while the opponent places, every MOVE you make loses you exactly one stone in
  the final tally (Line 2: 28-26 instead of 28-27). Super-ko fired exactly as
  described on a move-shuffle cycle.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `27,28,20,11,3,2,1,0,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19,21,22,23,24,25,26,29,30,31,33,32,34,35,36,37,38,39,40,41,42,43,44,45,46,47,49,48,50,51,52,53,54`
- Plan and what happened: I drove P1 to PLACE every turn (the only count-
  advancing action); P2 responded competently, also placing every turn. Both
  grew one stone/ply and I reached 28 first on my move-1 tempo lead — exactly as
  in Game C.
- Result (winner, end cause, plies): **P1 win**, win condition, ply 55, 28-27.

### Line 2 — you as P2
- Moves: `27,28,20,233,21,11,3,2,1,0,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19,22,23,24,25,26,28,30,31,33,32,34,35,36,37,38,39,40,41,42,43,44,45,46,47,49,48,50,51,52,53`
- Plan and what happened: I drove P2 and deliberately exercised the new toy —
  one **MOVE** (id 233, relocating my stone) on ply 4 — to test whether
  repositioning could buy anything. It cannot: the move spent a turn without
  adding a stone, so I finished one stone further behind than a pure racer.
- Result: **P1 win**, win condition, ply 55, **28-26** (one worse than the
  28-27 of pure racing — direct evidence MOVE is dominated).

### Line 3 — adversarial / novelty-stress
- Moves: `27,28,230,233,181,240`
- What you tried to break / stress, and what happened: I attempted to weaponize
  MOVE for repetition — P1 shifted (3,3)→(3,2) and back, P2 shifted (4,3)→(5,3)
  and tried to return. The return move (240) would have recreated the
  post-ply-2 position, and the engine printed **"SUPER-KO: this action
  recreated a previous position — rolled back and treated as a PASS"**, leaving
  P2's stone at (5,3) and the turn passing to P1. So move-cycling cannot
  manufacture a tempo or a stalemate; it just burns your turn.
- Result: super-ko rollback confirmed; no exploit found. MOVE remains useless
  for anything but (theoretically) un-sticking a stuck stone, which never arises
  before the 28-race ends.

### Additional lines (optional)
The greedy race (Line 1) plus the MOVE-penalty line (Line 2) plus the super-ko
cycle (Line 3) cover every distinct mechanic; further placement orders
reproduce the identical 28-stone race.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why): PLACE every turn;
  never MOVE or PASS. Location is irrelevant to your count or the opponent's
  options. The MOVE action is a trap — it only ever loses you a stone in the
  race (Line 2).
- Counterplay: None that works. As in Game C, the second player has no way to
  overtake; the added MOVE gives P2 no new resource because it cannot raise P2's
  count, and super-ko blocks any repetition trick (Line 3).
- Topology/board effects on strategy: Hex adjacency and the enemy-adjacency
  placement rule keep the colours interlocked but, with frontier cells always
  abundant before ply 55, never gate the result. Cosmetic.
- Emergent concepts you'd name (or "none observed"): None observed. The
  MOVE+super-ko machinery is dead weight that adds rule complexity without
  adding a single useful decision.
- Player agency: Effectively zero, and the MOVE option is a strictly worse
  choice — so the "extra agency" it appears to offer is negative value.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior: It is Game C —
  the degenerate place-adjacent-to-enemy majority/parity race — with a MOVE
  action and super-ko grafted on. Since MOVE is dominated and never used by a
  rational player, the playable game is **identical** to the banned
  majority-win fill: both add one stone per turn, first player wins by one.
- Honest novelty assessment after arguing that case: Very low — arguably lower
  in *design* terms than C, because the extra MOVE/super-ko rules expand the
  action space (449 ids) and the rulebook without producing any new strategy.
  Adding a strictly-dominated action is anti-novelty: more complexity, no depth.

## Phase 5 — Verdict

- P1-role experience sub-score (1-10): 2.9 — win by tempo fiat, plus a tempting
  but useless extra action.
- P2-role experience sub-score (1-10): 2.1 — no counterplay; the one new tool
  (MOVE) actively loses (Line 2).
- Role-averaged sub-score: 2.5
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** **1** — P1 won every
  race by structural first-move tempo, and the MOVE action gave P2 no path to
  parity (Line 2 lost by two).
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 2.5**
- One-paragraph justification of the Overall, citing your Phase 2 lines: The
  playable game is the same trivial first-player-by-one race as Game C (Line 1:
  P1 28-27), and the headline addition — the MOVE action — is strictly
  dominated (Line 2: wasting one move dropped P2 to 28-26), with super-ko
  closing the only repetition loophole (Line 3). So the new mechanics add
  rulebook weight and a 449-id action space while contributing zero strategic
  depth or counterplay; if anything that hurts the rule-economy dimension. It
  sits at or just below Game C and well under every anchor. **Overall 2.5.**
