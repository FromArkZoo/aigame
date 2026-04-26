# Team-15 Evaluation — Game `3bde3258978e`

Run 15 Genesis Creativity Engine human evaluation.
Team: `team-15`
Date: 2026-04-22

---

## PHASE 1 — RULE COMPREHENSION

### Board and Topology
- **8x8 grid, 2D, Moore topology** (no wraparound).
- Moore adjacency = 8 neighbours per interior cell (4 orthogonal + 4 diagonal). Note: `play_helper.py` wrongly prints "von Neumann" in its rules summary — the engine's actual `_build_moore_neighbors` uses Chebyshev-distance-1 (all 8 surrounding cells), verified at `game_engine/topology.py:159-188`. All analysis here uses true 8-neighbour Moore.

### Turn Structure
- **Alternating**, 1 placement per turn. `turn_type: alternating`, `pieces_per_turn: 1`. NOT simultaneous.

### Actions
- `action_types: ["place"]`. No movement. 65 actions: 0-63 place at `y*8+x`, action 64 = PASS.

### Placement Constraint
- Target empty cells, `constraint: anywhere`, `first_move_anywhere: true`. No placement restrictions.

### Capture — `surround`, threshold 1 (Go-style group removal)
- After each placement, enemy groups that are Moore-adjacent to the placed cell and have zero liberties are removed.
- **In practice, never fires.** Moore topology gives single stones up to 8 liberties. Surrounding a group requires occupying every empty Moore neighbour of every stone in the group — on an 8x8 board with two players adding stones at equal rate, this essentially never happens in normal play. I verified by stress-testing (3 real games + one manual "strangulation" attempt): no captures occurred in any sequence. The capture rule is effectively **inert**.

### Propagation — `influence`, radius 1
- `strength = 0.9323`, `decay = 0.5097`.
- On placement, P1 adds +0.9323 to the placed cell and +0.9323 × 0.5097 = +0.4754 to each of its 8 Moore neighbours. P2 subtracts the same values (negative influence).
- Values are clamped to ±100.

### Win Condition — `threshold`, 22.6453
- `_check_threshold` sums `board_values` on cells owned by each player. P1's effective score is the sum (positive). P2's effective score is the negation of the sum on its own cells (so both players measure their "own accumulated influence"). First player to cross **22.6453** wins.
- `max_turns = 100`. Double-pass ends the game as a draw (R15 rule). Max-turns fallback is piece-count majority (engine_v2.py:763-773).
- Threshold-check iteration is `for player in (1,2)`; since this is alternating, only one player can cross per tick, so the R15 "P1-wins-ties-by-iteration-order" issue is not triggered here. Relevant only to simultaneous variants.

### Degenerate behaviour flags
- **Capture rule is effectively dead** on this 8x8 Moore configuration.
- **Threshold is reachable easily** — a compact 3x3 own-cluster gives ≈ 30 score before any enemy interference; the game resolves in ~17 moves in all three of my playouts.
- **First-move advantage is very large** — see Phase 3.

---

## PHASE 2 — STRATEGIC PLAY

All moves engine-verified via `play_helper.py` / custom `team15_eval.py`. Every cited board state is the engine's output.

### Game 1 — Standard opening
- Sequence: `27,36,18,45,19,44,26,37,35,28,34,29,25,38,33,30,10`
- P1 at (3,3) centre. P2 mirrors at (4,4). Both players build diagonal 2x2 Moore blocks, then extend aggressively. Score stayed exactly symmetric (to 4 decimal places) through move 8 at 8.96-8.96.
- P1 broke symmetry on move 9 by playing (3,4) — a frontier-disruption move adjacent to both clusters. After move 9, P1 led 10.84 to 8.01.
- P2 re-matched on move 10 with (4,3). Scores became 9.41-9.41 again.
- From move 11 onwards both players extended their own cluster with "3-adjacent" moves (new stone Moore-adjacent to three existing own stones) worth +3.78 each turn. P1 stayed exactly 1 turn ahead because of tempo.
- **P1 wins on move 17** by placing (2,1). Final P1 = 23.60, P2 = 20.76.
- No captures, no passes. Threshold win.

### Game 2 — Early disruption try
- Sequence: `27,36,35,45,26,44,34,37,18,43,25,52,19,53,17,28,33`
- Same opening, but P1 (me) tries move 3 = (3,4) (frontier disruption) instead of passive (2,2). Jumps to 1.86 vs -0.02.
- P2 retreats to (5,5) to build own cluster. Symmetry is restored by move 6 at 4.22 each.
- From then on it replays Game 1's endgame with P1 one tempo ahead. On move 16 P2 tries the defensive disruption (4,3) which lowers P1 from 21.24 → 19.81 and puts P2 at 18.86, but P1 still has at least one 3-adj move that gains > 2.83.
- **P1 wins on move 17** placing (1,4). Final P1 = 23.60, P2 = 18.86.
- No captures, no passes. Threshold win.

### Game 3 — Seat swap + offset opening
- Sequence: `18,27,9,36,10,28,17,37,19,29,26,45,11,38,2,44,12`
- P1 plays (2,2) (not centre) to test whether centre is special. P2 takes (3,3) (Moore-adjacent to P1, asymmetric counter). P1 builds a 2x2 block at (1,1)-(2,1)-(1,2)-(2,2) while P2 builds a 3-stone L at (3,3)-(4,3)-(4,4) then (5,4).
- **Asymmetry in block shape favoured P1** because a 2x2 Moore block has more internal density (each corner has 3 own Moore neighbours) than an L (only 2-3).
- P2 played (3,3) adjacent to P1 instead of mirroring to (5,5); this is a reasonable "contact" opening but turned out slightly worse. Score split 8.96-8.01 by move 8 (vs perfect symmetry in games 1 & 2).
- **P1 wins on move 17** placing (4,1). Final P1 = 24.55, P2 = 20.76.
- No captures, no passes. Threshold win.

Note on role-switch: I ran P1 and P2 as the same agent sequentially for all three games. I attempted different strategies on different moves and acknowledge the seat-identity bias. Game 3 deliberately tested a non-central P1 opening and non-mirroring P2 reply; P1 still won.

### Player reflections

**Player 1 strategy guide.**
- Open in or near the centre (3,3) or (4,4). Avoid corners — the boundary truncates the Moore neighbourhood and loses influence.
- Grow the densest possible Moore block. A 2x2 block is the smallest maximally-dense shape (each corner has 3 own Moore neighbours, so placing the 4th corner gains +3.78).
- Prefer moves with 3-adj Moore density over disruption moves of equal nominal swing — pure own-growth compounds because each future own placement also benefits from the 3-adj cell.
- Late game, play an explicit +2.83 or +3.78 move to cross the threshold; don't play disruption unless you're one tempo behind.

**Player 2 strategy guide.**
- P2 has no winning strategy I could find. Mirror-building ties each turn, but P1 is always one tempo ahead, so P1 wins on some move between 13 and 17.
- Your only realistic hope is to **break P1's plan** by forcing a disruption exchange early — e.g. play on a cell that's Moore-adjacent to all three stones in a P1 3-cell cluster. That forces P1 to defend or accept a 1.4-1.9 tempo loss, shifting the critical turn by one.
- The "adjacent-disruption" opening (play next to P1's stone instead of mirroring far away) does not help on its own — it just relocates the symmetric exchange.

**Endgame resolution note.** All three games resolved by threshold, not by double-pass draw or max-turns. R15's double-pass-draw rule did not fire. No captures occurred.

---

## PHASE 3 — STRATEGIC ANALYSIS (joint)

### Dominant approach
There is effectively one viable strategy: build the densest Moore cluster you can, as fast as possible. Capture is inert. Movement doesn't exist. Propagation is the only interaction. So the game reduces to **parallel cluster-density races with mild cross-turn disruption**.

### Counter-play
Counter-play exists only as an "exchange of tempo" — when your opponent plays a frontier disruption move at -1.425, you can reply in kind. But the game doesn't reward true strategic diversity: every player's best move in ~85 % of positions is the 3-adj own-extension. I found exactly one recurring decision point: "disrupt the opponent for +0.95 swing or extend for +2.83 own-growth?" — and extension was almost always better.

### Short-term vs long-term tension
Minimal. Every turn you almost always play the locally greedy +max move, and that also happens to be globally correct because each own stone becomes a future +0.475 for all your later adjacent placements. There is no sacrifice-for-later dynamic and no committed plan you can be punished for.

### Emergent concepts
- **Influence density** is the main emergent concept (= "how many own Moore neighbours does each own stone have"). Compact 2x2 / 3x3 blocks maximise this.
- **Tempo / initiative** exists in the trivial form: P1 is always exactly one move ahead because alternating + identical valuations for each seat.
- **Territory** exists weakly. The "shadow of negative influence" around the opponent's cluster is a soft boundary.
- **No mutual-annihilation** (this is alternating, not simultaneous). **No ko**. **No ladders, no life-and-death, no eyes**. Surround capture is present mechanically but dead in practice.

### Does topology matter?
Moore vs grid/von-Neumann matters significantly for cluster valuation: a 2x2 block on Moore = 4 stones with 3 own Moore neighbours each (+3.78 per new corner). On a von-Neumann grid that same block would be only +1.88 per corner (1 own orthogonal neighbour). So Moore makes dense clusters much more valuable and makes the game resolve much faster than a grid version would.

Torus would remove boundary penalties and let P2 catch up in edge cases, but since games finish in 17 moves centred on (3,3)-(5,5), the boundary barely matters for games as played.

### First-mover advantage
**Extremely high.** P1 won all 3/3 of my games, always on move 17, with a score margin of 2.8-5.5 at the end. The seat-swap in Game 3 did not change the outcome — even with a non-central P1 opening and a non-mirroring P2 reply, P1 won.

This is a strongly P1-biased alternating game. R15's seat-balance heuristic should flag it: the training ELO of 2596 and non-triviality 1.00 hide the fact that a rational P1 wins deterministically against a rational P2. The R15 training winrate of "0.5 / 1.0" (one seed 50 %, the other 100 %) is consistent: one seed discovered the P1 strategy, the other learned both seats at the 50 % fixed point of self-play cycling.

---

## PHASE 4 — NOVELTY ADVERSARY

### Adversary case (argued forcefully)

This game is **not novel**. It is a thin reskin of several well-known abstract games, and its emergent behaviour would be immediately familiar to any experienced Go / Reversi / Pente player.

**(a) Catalog comparison.**
- **Reversi/Othello.** The "influence field" with positive-for-me, negative-for-you values is exactly the "piece count" aspect of Othello mapped to a continuous shadow. In Othello, placing a stone flips contiguous opponent lines; here, placing a stone adds influence to a radius-1 neighbourhood. Same "I spread my colour, you spread yours" dynamic, just with soft values instead of binary flips.
- **Go.** Placement-only board, surround capture, threshold goal. Strip the influence layer and this is just a territory-counting Go variant on an 8x8 Moore board. The evolutionary ancestor notation (`parents`, `mutation_types: action_types`) even suggests this was derived from a Go-like starting point.
- **Pente / Gomoku / Connect6.** All are "place and build a cluster" games on a grid with Moore/orthogonal adjacency. The winning criterion differs (line vs threshold) but the core motor — compact placement building value — is the same.
- **Tumbleweed.** Tumbleweed uses a decaying "influence cone" metaphor explicitly. This game's `radius=1`, `decay=0.51` propagation is a degenerate 1-step Tumbleweed where the cone has only two rings.
- **Lines of Action.** Cluster-density goal (all your stones connected). Different mechanism, same "compact your own pieces" strategic theme.
- **Hex/Y/Havannah/Connect6.** Not relevant — those are connection games and this is a density/threshold game.
- **Life-like CA, Day & Night, HighLife.** Not relevant — this game has no CA step, `ca_rule=None`.

**(b) CA literature.** N/A — classic mechanics, no CA.

**(c) Simultaneous-game comparison.** N/A — this is alternating.

**(d) Re-skin hypothesis.** This is **"Weighted Reversi on an 8x8 Moore board with Go-style capture disabled in practice."** The specific transformation: replace Othello's flip-on-bracketing rule with "every placement adds ±strength·decay^dist to each cell in Moore-radius 1, and you win when the sum over your own cells exceeds threshold." This is exactly the Tumbleweed-style influence accumulator with the flip/bracket rule replaced by a threshold gate.

**(e) Expert transfer test.** An experienced Reversi player would dominate here. They already understand: "play on cells that will still be mine at the end", "contest the centre", "build compact mutual-support structures". A competent Go 15-kyu would also play this correctly at first sight — they would recognise the Moore-cluster density goal as the "good shape" heuristic from Go.

### Rebuttal (P1 + P2 joint)

The adversary conflates thematic similarity with strategic equivalence. Three specific points from Phase 2 playthroughs show where known-game intuition **fails**.

1. **Othello's bracketing rule vs this game's influence accumulator are strategically different.** In Reversi, you must capture at least one opponent stone each move (there is a pass only when no capture is possible). Here, the placement rule is `anywhere`, and no placement can flip opponent stones. In Game 1 move 3 (P1 at (3,4)), P1 played a move that would have been impossible in Reversi (no brackets). The correct move in this game is often the move that maximises own-density, not the one that flips maximum enemy pieces. A Reversi expert would systematically overweight disruption.

2. **The threshold win is different from Go's territorial count and from Reversi's majority count.** Game 2 ended with P1=23.60 and P2=18.86 — both players still had large unclaimed regions. A Go player would try to secure territory boundaries; an Othello player would try to control corners. Neither intuition is right here: you just want a compact cluster anywhere. Game 3 confirmed this — P1's 2x2 block at (1,1) corner (the WORST corner in Othello because it's near the edge) won comfortably.

3. **Capture being dead makes this unlike Go.** In Go, the whole game is about the tension between extension and capture threat. Here, in three games and one stress-test, no capture occurred. The "surround" rule in the rule-record is inert. A Go expert would spend moves on cutting and atari threats that have zero effect on the outcome.

4. **Tumbleweed is the closest analog, but Tumbleweed uses a "line-of-sight" stack-count with visibility along rows/columns, not a Chebyshev-radius-1 influence.** The mechanic here is simpler and denser — a single radius-1 pulse, no line-of-sight tracing, no stack heights.

So: the game is NOT a re-skin. It's closer to **"static-radius Tumbleweed with a sum-threshold win, no ranged visibility, dead capture rule."** That's a real variant, not a new game.

### Joint Novelty score: **3/10**

The game is a mild modification of existing influence-accumulation abstract games (Tumbleweed-like). It has no emergent property that's absent from those ancestors. The dead capture rule and the lack of a plan-committing mechanic (no ko, no life-death, no sacrificial structure) mean its strategic surface is much shallower than Go. A single obvious strategy (build dense Moore blocks) dominates. The one defensible novelty point is that I am not aware of a published abstract game that is specifically "radius-1 influence + Go-moore-capture + threshold on own-cells", but novelty-by-combination is weak novelty.

---

## PHASE 5 — VERDICT

**Team ID:** team-15
**Game ID:** 3bde3258978e
**Rules Summary:** Alternating placement on an 8x8 Moore grid; each stone adds ±0.932 to its cell and ±0.475 to each Moore neighbour; first player whose total own-cell influence exceeds 22.645 wins; Go-style surround capture exists mechanically but is unreachable in practice.
**Topology:** 8x8, Moore (8-neighbour), no wraparound
**Turn Structure:** Alternating, 1 piece per turn

### SCORES (1-10)

- **Strategic Depth: 3** — One dominant strategy (build the densest Moore cluster). Disruption is occasionally correct but by a small margin. Very few strategic decision points per game — most moves are forced by the local +3.78 > +2.83 > +1.88 ordering. I could compute optimal moves with a ~1-line heuristic.

- **Emergent Complexity: 3** — The influence field produces a smooth positional score that encodes cluster density. That's a mild emergent property. But no long-range patterns, no local tactics (ladders, eyes, ko), no initiative handoff. Symmetric play produces exactly-matching scores to 4 decimal places for ~8 moves in a row.

- **Balance: 2** — First-mover advantage is severe. P1 won 3/3 of my games, always on move 17, with final margins of +2.83, +4.73, +3.78. Even a non-mirroring P2 reply and a seat-swapped opening (Game 3) did not change the result. Training data confirms: seed 100061 had 50 % P1 winrate but seed 101061 had 100 % P1 winrate — i.e., once a policy learns the P1 strategy, P2 cannot win. Game should be penalised heavily by R15's new seat-balance heuristic if applied rigorously.

- **Novelty (post-adversary): 3** — Closest to Tumbleweed with a sum-threshold victory condition. The adversary's Reversi/Go/Tumbleweed comparisons land; the rebuttal only establishes that this is a new combination of existing ideas, not a new idea.

- **Replayability: 3** — Games are short (17 moves), deterministic under optimal play, and the strategic choices are narrow. After 3 games I could predict every move class. Playing this a 5th time would feel like playing the same game.

- **Overall "Would I play this again?": 3**

### CLOSEST KNOWN-GAME ANALOG
**Tumbleweed** (influence-based placement game) with simplified radius-1 influence, plus a Go-style capture rule that is effectively dead on 8x8 Moore.

### KILLER FLAWS
1. **Severe P1 advantage** (3/3 wins in my trials, confirmed by the 100 % P1 winrate in one of the training seeds). Alternating + symmetric valuations + no ko-like mechanism means P1's one-tempo lead is decisive.
2. **Capture rule is dead.** Surround capture on 8x8 Moore never triggers in normal play. Listed as `capture_type: surround, threshold: 1` but has zero gameplay impact. This is a rule-representation artefact, not a real mechanic.
3. **Dominant single strategy.** Dense Moore cluster. Every position has a clearly best move computable from local arithmetic.
4. **No pass-draw issue** (R15's new draw rule didn't fire) — but this is because the threshold is very reachable, not because the game is well-balanced.

### BEST QUALITY
The smooth scalar-valued influence field is a genuinely clean mechanic — it replaces Go's "is this group alive" with a continuous density score, which is conceptually elegant and would be pedagogically useful as a stepping-stone between Tic-Tac-Toe and Go for teaching positional evaluation. Moore adjacency amplifies this (2x2 blocks are the smallest maximally-dense structures, easy to visualise).

### IMPROVEMENT IDEAS
The single best rule change: **add a komi of ~3.0 to P2's effective score**, or **raise the threshold for P1 by ~3.0 while holding P2's threshold constant**. This would offset the first-mover tempo advantage (one "3-adj" move ≈ +3.78) and produce a genuine contest. Alternative: make the game **simultaneous** (both players submit a move, collisions annihilate both stones) — this would actually make the Moore-cluster race interesting because both players could target the same cell for different reasons, and it would test the R15 engine's sim+CA fix directly. Alternative #3: **shrink the board to 6x6** — would force earlier contact and likely produce more decisive tempo swings.
