# Team-9 Evaluation — Game d8f2ae54f399

Team ID: team-9
Game ID: d8f2ae54f399
Run: 15
Date: 2026-04-22

## Phase 1 — Rule Comprehension

**Board structure.** 2-dimensional grid (standard grid topology, no torus wrap). Axis size 8, so the board is 8x8 = 64 cells. Cells are addressed linearly as `y * 8 + x`; action N-1 (action 64) is PASS, and actions 0..63 are placements.

**Turn structure.** ALTERNATING — `turn_structure = {"turn_type": "alternating", "pieces_per_turn": 1}`. P1 moves first, then P2, alternating. No simultaneous resolution, so the R15 pilot's "P1 wins simultaneous ties" caveat does NOT apply here. P1 does, however, have the natural alternating-game tempo advantage.

**Action types.** Place only. Each turn a player places a single stone on an empty cell. `first_move_anywhere = True` and `constraint = "anywhere"`, so no placement restrictions beyond "cell must be empty".

**Capture / CA dynamics.** `capture_rule = {"capture_type": "surround", "threshold": 1}`. This is classical Go-style surround: after each placement the engine walks every enemy group adjacent to the placed stone; any group with zero liberties is removed. No cellular automaton (`Cellular Automaton: No (classic)`), so CA-specific R15 concerns (1↔2 symmetry of transition table, dead CA rules) are not applicable.

**Propagation / influence.** `propagation_rule = {"prop_type": "influence", "radius": 1, "strength": 0.9322817703212022, "decay": 0.5097131432079061}`. Each placed stone writes value `+strength` (for P1) or `-strength` (for P2) onto its own cell and contributes `±strength * decay ≈ ±0.475` to each of the 4 orthogonal neighbors. Influences **sum linearly and are signed** — verified empirically: an isolated P1 stone at (3,3) gives `+0.93` on (3,3) and `+0.475` on each of (2,3)/(4,3)/(3,2)/(3,4); adding a P2 stone at (3,4) overwrites (3,4) with `-0.93` and the P1 fringe at (3,3) drops to `0.46` because the P2 influence `-0.475` is additive. No radius-2 component.

**Win condition.** `win_condition = {"condition_type": "threshold", "threshold": 22.645, "target_dimension": 0, "target_dimension_p2": -1, "max_turns": 100}`. After each move the engine iterates `for player in (1,2)` summing `board_values[c]` over cells owned by that player. For P1 that sum is compared directly to 22.645; for P2 the same sum is negated (P2 values are negative in the raw field) and compared. First player whose effective-value sum exceeds 22.645 wins. Ties broken by check-order (P1 first), but ties in alternating games are rarer than in simultaneous.

**Degeneracy flags.**
- Threshold 22.645 is **reachable** but requires a well-clustered group. An isolated 8-stone cluster is worth roughly 14–16 effective points; reaching 22.6 requires ~12–15 dense stones or ~20 scattered ones. Our Phase-2 games resolved between moves 25 and 31, so the threshold is neither trivial nor unreachable.
- Surround capture with `threshold=1` is alive but **very rare in practice** — in 3 full playthroughs we saw 0 captures. Interior stones have 4 liberties; surrounding a single interior stone costs 4 moves, and in a threshold race spending 4 moves to remove 1 enemy stone (net –1 for you, –0.93 for opponent) is a losing trade. Capture is essentially inert in optimal play.
- No double-pass concern: threshold is reachable quickly and no equilibrium gives both players an incentive to pass.
- No CA, so CA-rule-dead concerns don't apply.
- First-move anywhere → no opening asymmetry beyond standard tempo.

## Phase 2 — Strategic Play

Engine-verified every move using `play_helper.py` (wrapped in `team9_play.py` to print effective-value sums after each step). All three games ran to a natural threshold termination; none hit `max_turns=100` and none ended by double-pass.

### Game 1 — P1 "scatter + influence coverage" vs P2 "mirror then densify"

**P1 strategy.** Central seed at (3,3), then try to claim both a center cluster and four corners to maximize territorial coverage. Hypothesis: influence radius 1 means spreading stones gives broader coverage than densifying.

**P2 strategy.** Mirror-adjacent — place alongside P1's stones so P2's own cluster runs parallel to P1's. Once P1 abandons the center (move 13), P2 pivots to pure densification of its own column.

**Move log (abbreviated, all moves engine-verified).**
| Mv | P | Cell | P1_eff | P2_eff | Note |
|---|---|---|---|---|---|
| 1 | P1 | (3,3) | 0.93 | 0.00 | center seed |
| 2 | P2 | (4,3) | 0.46 | 0.46 | adjacent mirror — influences cancel |
| 3 | P1 | (3,2) | 2.34 | 0.46 | extend N |
| 4 | P2 | (4,2) | 1.86 | 1.86 | mirror |
| 5 | P1 | (3,4) | 3.75 | 1.86 | extend S |
| 6 | P2 | (4,4) | 3.27 | 3.27 | mirror |
| 7 | P1 | (3,1) | 5.15 | 3.27 | extend |
| 8 | P2 | (4,1) | 4.68 | 4.68 | mirror |
| 9 | P1 | (3,5) | 6.55 | 4.68 | extend |
| 10 | P2 | (4,5) | 6.08 | 6.08 | mirror |
| 11 | P1 | (3,6) | 7.49 | 6.08 | extend |
| 12 | P2 | (4,6) | 7.49 | 7.49 | mirror |
| 13 | P1 | **(0,0)** | 8.43 | 7.49 | scatter to corner |
| 14 | P2 | (5,3) | 8.43 | 9.38 | **P2 pivots to densify** |
| 15 | P1 | (7,0) | 9.36 | 9.38 | scatter corner |
| 16 | P2 | (6,3) | 9.36 | 11.26 | densify |
| 17 | P1 | (0,7) | 10.29 | 11.26 | scatter |
| 18 | P2 | (5,4) | 10.29 | 14.09 | densify |
| 19 | P1 | (7,7) | 11.22 | 14.09 | scatter |
| 20 | P2 | (5,5) | 11.22 | 16.93 | densify |
| 21 | P1 | (3,0) | 14.99 (correction: 13.11 at mv 22) | … | belated densify |
| 24 | P2 | (5,2) | 14.99 | 22.59 | one short of threshold |
| 26 | P2 | (6,4) | 16.40 | **24.95** | **P2 wins** |

**Result.** P2 wins by threshold at move 26 (P2_eff = 24.95 > 22.645). P1 reached only 16.4.

**P1 reflection (pre-P2-read, finalized in writing before switching).** The scatter strategy was wrong. Corner stones produce only ~1.88 effective mass (corner = self 0.93 + 2 neighbors 0.48 each, minus any adjacent enemy cancellation). A corner stone is equivalent to roughly half an interior stone. By move 13 I had 7 stones delivering 7.49 — by spreading I locked that rate down to ~0.93/move while P2, freed from mirroring, accelerated to ~1.88–2.83/move through densification. Surprising: my intuition that "influence = spread wide" was wrong. With radius 1 and strength*decay being a non-trivial fraction, the **interior bonus from friendly neighbors dominates** — each neighbor-pair adds 2 × 0.475 ≈ 0.95 to both stones' combined effective value, so dense clusters snowball.

**P2 reflection.** Mirror strategy held me even through move 12. The pivot at move 14 when P1 scattered was the winning decision — P2 had a ready-made seed at (5,3) and just needed to thicken it. Nothing surprising; P1 self-sabotaged.

### Game 2 — P1 "dense left cluster + interior extension" vs P2 "mirror densify"

**P1 strategy.** Build the densest possible cluster in the left-center region (x ∈ {1..3}) to maximize interior neighbor-bonus. Key moves pick cells with the most already-friendly neighbors.

**P2 strategy.** Mirror on the right (x ∈ {4..6}). Both players are densifying in parallel — this is the "race" case.

**Move log (abbreviated).**
| Mv | P | Cell | P1_eff | P2_eff |
|---|---|---|---|---|
| 1 | P1 | (3,3) | 0.93 | 0.00 |
| 2 | P2 | (4,4) | 0.46 | 0.46 |
| 3 | P1 | (2,3) | 2.83 | 0.46 |
| 4 | P2 | (3,4) | 1.88 | 1.88 |
| 5 | P1 | (3,2) | 3.75 | 1.88 |
| 6 | P2 | (4,3) | 2.36 | 2.36 |
| 7 | P1 | (2,2) | 4.69 | 2.36 |
| 8 | P2 | (4,2) | 3.75 | 4.21 |
| 9 | P1 | (1,2) | 5.61 | 4.21 |
| 10 | P2 | (3,1) | 5.61 | 5.15 |
| 11 | P1 | (2,1) | 8.92 | 5.14 | [interior bonus — (2,1) touches 3 own stones] |
| 12 | P2 | (4,1) | 8.92 | 7.97 |
| 15 | P1 | (1,5) | 12.69 | 9.85 |
| 21 | P1 | (2,4) | 18.81 | 15.03 |
| 24 | P2 | (5,6) | 21.64 | 20.69 |
| 25 | P1 | (1,3) | **25.43** | 20.69 | **P1 wins** |

**Result.** P1 wins by threshold at move 25 (P1_eff = 25.43 > 22.645).

**P1 reflection.** The densify race is straightforwardly won by whoever has the tempo. With +1 stone at parity density, P1 always reaches threshold ~1 move sooner. Move 11 at (2,1) was the pivotal move — (2,1) touched (1,1-not mine), (3,1), (2,2) — three own stones — adding ~2.35 in a single move where P2's mirror had to settle for a 2-own-neighbor cell. Selecting the *highest-neighbor-bonus* empty cell each turn is the optimal greedy heuristic.

**P2 reflection.** Pure mirror is a losing race given P1's tempo. Next time I would either (a) try asymmetric placement to force capture threat, (b) play deliberately adjacent to P1 to cancel influence rather than mirror in parallel, or (c) deny P1's highest-bonus cells by pre-occupying them. See Game 3.

### Game 3 — Seat swap: counter-adjacent P2 strategist is now P1; densifier is now P2

**Setup.** We swap the agent that was P1 in Games 1–2 to play P2, and vice versa. The new P1 plays counter-adjacent: place next to P2's stones to cancel P2's influence. The new P2 plays densify.

**Move log (abbreviated).**
| Mv | P | Cell | P1_eff | P2_eff |
|---|---|---|---|---|
| 1 | P1 | (3,3) | 0.93 | 0.00 |
| 2 | P2 | (2,3) | 0.46 | 0.46 |
| 3 | P1 | (4,3) | 2.36 | -0.00 | [P1 cancels P2 (2,3) influence and gets +self] |
| 4 | P2 | (3,4) | 1.88 | 1.88 |
| 5 | P1 | (3,2) | 3.75 | 0.91 |
| 6 | P2 | (4,2) | 2.80 | 0.90 |
| 7 | P1 | (4,4) | 4.20 | 0.42 | [continued cancellation] |
| 8 | P2 | (3,1) | 3.73 | 0.88 |
| 9 | P1 | (2,2) | 5.14 | 0.40 |
| 10 | P2 | (2,1) | 4.66 | 1.81 |
| 11 | P1 | (4,1) | 4.64 | 0.86 |
| 12 | P2 | (2,4) | 4.64 | 3.69 |
| (... game continues, both expand into free territory ...) |
| 25 | P1 | (4,0) | 17.36 | 13.60 |
| 26 | P2 | (2,5) | 18.77 | 18.79 |
| 27 | P1 | (6,0) | 20.66 | 18.79 |
| 28 | P2 | (2,7) | 20.66 | 20.67 |
| 29 | P1 | (2,0) | 22.06 | 20.20 |
| 30 | P2 | (1,7) | 22.06 | 22.08 |
| 31 | P1 | (6,1) | **24.90** | 22.08 | **P1 wins** |

**Result.** P1 wins by threshold at move 31 (P1_eff = 24.90 > 22.645). Closest game of the three — P2 was 0.57 points short when P1 sealed it.

**P1 (counter-adjacent) reflection.** Adjacency cancellation depresses *both* players' effective values but not symmetrically — the player whose stone is surrounded by more enemy neighbors loses more. Initially this worked (P2 held to ~0.4 through move 9). But stones can only be adjacent to 4 things, so cancellation saturates. After move 12 both players were in free territory again and the race resumed, with P1 still holding tempo. The counter-adjacent phase **narrowed the race** (final gap was 2.8 points instead of Game 2's 4.7) but could not overturn it.

**P2 (densifier) reflection.** In Game 3 I (as P2) was the seat-swapped agent. I could not prevent P1's inevitable tempo-win but came closer than a pure mirror would have. Nothing genuinely surprising — the tight finish confirms that P1 has ~+1-stone-worth of threshold advantage under best play.

### P1 Strategy Guide (for this game)

1. **Seed the center**, not a corner. (3,3), (3,4), (4,3), (4,4) are all equivalent; choose (3,3) or (4,4).
2. **Greedy densify.** Each turn, place on the empty cell with the most friendly-occupied 4-neighbors. Two own neighbors = +0.95 bonus versus an isolated spot; three = +1.41; four = +1.88.
3. **Do not scatter to corners** — they're effectively half-stones.
4. **Do not chase opponent.** Your tempo advantage wins the race if both players densify. Only interfere if opponent is building faster than you (rare).
5. **Expect the win by moves 23–27** under optimal play.

### P2 Strategy Guide (for this game)

1. **Mirror only while it's costless.** As soon as P1 makes a suboptimal move (scatters, plays an edge cell), switch to densifying your own shadow cluster.
2. **Counter-adjacency** depresses both totals but costs P2 tempo-equivalent value; use only when P1's cluster geometry concentrates value (e.g. P1 has just played a 3-neighbor cell you can now cancel).
3. **Do not try to capture.** Surround capture requires 4 moves per interior stone; those same 4 moves added to your own cluster gain ~6–8 effective points versus the capture's 0.93 swing.
4. **Accept that best-play P2 loses by ~0.5–3 effective-point margin** on 8x8 with threshold 22.645. P2 is hoping for P1 mistakes.

## Phase 3 — Joint Strategic Analysis

(P1-agent and P2-agent hat exchange, both now in strategist mode.)

**Are there distinct viable strategies or does one dominate?** Three distinct strategic families were tested:
- Scatter / territorial (Game 1 P1) — **dominated; loses badly**
- Densify (Game 1 P2, Game 2 P1, Game 3 P2) — **dominant family**; within it, greedy-neighbor-bonus selection is the clean heuristic
- Counter-adjacency cancellation (Game 3 P1) — **playable, narrows margin by ~2 points, does not overturn tempo**

Density clearly dominates scatter. Within density-play, tempo decides. This is a modest strategic landscape — not a single-strategy game, but close to one.

**Is there meaningful counter-play?** Yes but limited. The cancellation strategy is a real counter that changes the evaluation function (from "sum of own cluster" to "sum of own cluster minus enemy interference"). Choosing whether to cancel vs densify at each move is a genuine decision. However, counter-play does not overturn the tempo advantage; it only narrows it.

**Short-term vs long-term tension?** Very little. Every move's effective-value contribution is *local and immediate* (the stone you place plus the 4 neighbors). There are no delayed-payoff moves — the only slightly subtle choice is cancellation (accept –0.5 now for –1.5 to opponent later), and even that resolves over 1–2 moves. No ko-like cycles observed.

**Emergent concepts.**
- **Tempo** is the single most important concept. Alternating + threshold = P1 wins the race by default.
- **Cluster density** (interior neighbor bonus) drives the race.
- **Adjacency cancellation** is the only non-trivial interactive mechanic we found.
- **Territory** in the Go sense does NOT emerge — the threshold is a piece-count proxy weighted by clustering.
- **Capture** is mechanically present but strategically absent; a 4-move capture cost dwarfs the ~0.93 swing from removing one enemy stone.
- **Mutual-annihilation tactics** (relevant for simultaneous games) do not apply — this is alternating.

**Does topology matter?** Minimally. The grid edges cost stones ~0.48 (edge) or ~0.96 (corner) of potential bonus, so center-play dominates. This is weaker spatial strategy than e.g. Go (where edges affect life/death of groups) or Hex (where edges define the win condition). The topology is a plain 8x8 grid with no wrap; the only spatial insight is "play interior". Torus or hex would matter more; here the mutation from a parent (4af27911b0f5 was probably torus) to grid removed whatever topological drama the parent had.

**First-mover advantage.** Substantial. Seat-swap evidence from Phase 2:
- Games 1+2: same agent as P1; record 1–1 (lost Game 1 only because of scatter; won Game 2 on densify).
- Game 3 (seat swapped): the *other* agent plays P1 (counter-adjacent strategy); wins.
- Across all three games: the agent playing P1 won 2/3. The one P2 win came against a player making a strategic blunder (scatter).
- Under best-play-vs-best-play (Games 2 and 3), **P1 wins both**. Tempo advantage is worth roughly 0.5–3 effective-value points, equivalent to ~1 tempo-move at threshold.

This is a meaningful P1 bias, consistent with most alternating threshold-race games lacking a komi/tie-breaking mechanism. The R15 seat-balance metric would probably flag this.

## Phase 4 — Novelty Adversary

### The Adversary's case

**(a) Comparison to known abstract games.**

- **Go.** Board 8x8 grid, surround-capture with threshold 1 — this *is* the Go capture rule on a smaller board. Winning condition is the primary difference (threshold-on-influence-field instead of territory + prisoners). But the "capture" mechanic is cosmetic (never fires in our playthroughs), so the Go-ness collapses to "8x8 grid, place stones, can't occupy same cell". That's every placement game ever.
- **Reversi/Othello.** Reversi uses flip-on-flank on 8x8. This game has no flips. Eliminated except for board shape.
- **Hex / Y / Havannah.** Those are connection-based win conditions on triangular/hexagonal lattices. Different topology, different win conditions. Eliminated.
- **Gomoku / Pente / Connect6.** N-in-a-row. Different win condition. Eliminated except "place stones on a grid".
- **Amazons.** Move-and-shoot mechanic. No movement here. Eliminated.
- **Lines of Action / Chameleon / Mancala.** Move-based, not placement-based. Eliminated.
- **Tumbleweed.** This is the real near-match. Tumbleweed is played on a hex with influence fields (stack size = number of friendly stones with line-of-sight). The adversary argues: **this game is Tumbleweed with radius-1 orthogonal influence instead of line-of-sight influence, on a grid instead of hex, with a scalar threshold instead of majority-cells-captured.**
- **Slither.** Slither has snake-style piece movement. No movement here. Eliminated.
- **Life-like CA games** (Immigration, Day & Night). No CA here. Eliminated.

**(b) CA literature.** Not applicable — no CA.

**(c) Simultaneous-game analogs.** Not applicable — alternating.

**(d) Topology re-skin argument.** The adversary's strongest claim: "This is Tumbleweed on a grid with orthogonal-radius-1 influence and a scalar threshold win condition." Specific correspondence:
- Both: place stones, stones emit influence fields, opposing fields cancel, player with more influence wins.
- Both: first-move is free-placement.
- Tumbleweed uses hex + line-of-sight; this game uses grid + radius-1 orthogonal — a geometric re-parameterization.
- Tumbleweed's win condition is "majority of hexes settled by majority own influence"; this game's is "total effective value on own cells > 22.6". These are *different aggregation functions* but share the "influence field" framework.

**(e) Would a Tumbleweed expert have an advantage?** Partially. They would correctly intuit:
- "Play dense near existing friendly stones for influence stacking." (+1)
- "Opposing fields cancel at overlap; contest key squares." (+1)
- "Corners/edges are weaker than interior." (+1)

But they would mis-apply:
- **No line-of-sight**: Tumbleweed influence is long-range along rays. This game is strictly local (radius 1). A Tumbleweed expert might over-value placing stones "looking down a corridor" — that does nothing here.
- **Tempo race vs territory**: Tumbleweed doesn't have a scalar threshold; it has a territory-count win. A Tumbleweed expert might play for broad influence majorities across the whole board; here you just want to hit 22.6 fastest. Optimal play in this game would be the *opposite* of optimal Tumbleweed play in some positions.
- **Capture mechanic**: Tumbleweed has no capture. Here surround-capture exists (even if strategically inert). A Tumbleweed expert would not think about liberties.

### Players' rebuttal

Concrete Phase-2 moments where a known-game analogy would fail:

1. **Game 1 move 13** (P1 scatters to (0,0)). A Go player would approve of corner-first opening ("sente, secure corner"). A Tumbleweed player would approve of corner influence. **Both analogies fail here** — corner placement is strictly weaker than densifying because this game's *local* influence radius gives corners only 2 neighbors. Result: immediate loss of tempo, eventual loss of game.

2. **Game 3 move 3** (P1 plays (4,3) directly adjacent to P2 (2,3)). A Go player would call this "pushing into the opponent — bad shape, strengthens the opponent". A Gomoku player would never play this. But here it is the *correct* counter-adjacency move: it cancels P2's (2,3) influence on (3,3) and reclaims fringe value. The cancellation-cancels-value dynamic has **no analog** in Go, Hex, Reversi, or Tumbleweed (Tumbleweed has cell-majority override, not signed sum cancellation).

3. **Universal failure of the capture analog.** In Go, the threat of capture drives move choice even when no capture happens — you shape around liberties. In this game, the math says capturing an interior stone costs –3.7 effective value (your four moves at avg +0.93 each that instead could have gone into your cluster) versus gaining +0.93 (removing enemy stone). A Go player's instincts about "don't leave weak groups" produce strategically worthless plays here.

4. **Threshold race is unique to this game family.** No classical abstract game resolves by "first to N summed points". Go, Othello, Hex, Tumbleweed all resolve at a fixed game-end by comparison. Here the *race to threshold* forces greedy-tempo play, which is why counter-adjacency (Game 3) is viable even though it would be nonsense in any end-comparison game.

### Resolution

The adversary's strongest argument is **Tumbleweed-on-a-grid**. It is a legitimate high-level frame: "stones emit influence, cancel, player with more wins." But at the *move level*, the radius-1 orthogonal local field plus threshold-race produces a different strategic texture — counter-adjacency as a real strategy, corners as real losers, capture as truly inert. The game is not a simple re-skin.

It is also not wildly novel: "place stones, influence radius 1, surround capture, scalar threshold" is a compact parametrization of ideas that individually exist in the literature. The novelty is in the *combination and calibration* (particularly the threshold value that makes races of 25–31 moves), not in any genuinely new mechanic.

**Novelty score: 4 / 10.** Better than "X on a hex board" (2–3) because of the threshold-race and counter-adjacency texture, but well below a game with emergent dynamics that have no direct analog. Best one-line characterization: **a compact, tempo-dominated variant of influence-field placement — closest to Tumbleweed but with Go-shaped capture and a scalar threshold race**.

## Phase 5 — Verdict

**Team ID:** team-9
**Game ID:** d8f2ae54f399
**Rules Summary:** 8x8 grid, alternating placement, Go-style surround capture (surround-threshold 1, practically inert), radius-1 orthogonal signed influence propagation (strength 0.93, decay 0.51), first player whose summed-effective-value on own cells exceeds 22.645 wins.
**Topology:** 2D 8x8 grid, no wrap
**Turn Structure:** Alternating

### SCORES (1–10)

- **Strategic Depth: 4** — One dominant family (densify), one real counter (adjacency cancellation), tempo-decided. Meaningful within-move decisions (which empty cell has most own-neighbors) but no deep long-term planning. No ko, no sacrifice tactics, no emergent capture patterns.
- **Emergent Complexity: 3** — Influence summation and cancellation is a real emergent property, but the strategy-space collapses quickly to "greedy neighbor-bonus" under best play. Capture mechanic is effectively unused, representing unused rule-space.
- **Balance: 4** — Clear P1 tempo advantage. Seat-swap evidence: under best-play-vs-best-play (Games 2 and 3), P1 wins both — agent identity does not matter when strategy is fixed. The lone P2 win (Game 1) required a P1 blunder. R15's new seat-balance metric would almost certainly penalize this game; the training `final_win_rate=0.5` likely reflects mixed-skill opponents rather than balanced best-play. Threshold 22.645 with no komi or P2 bonus is the structural cause.
- **Novelty (post-adversary): 4** — Survives the Tumbleweed-re-skin claim because of the threshold-race tempo dynamic and counter-adjacency tactic, both absent from Tumbleweed and most influence games. But the fundamental "place stones, radius-1 influence, threshold win" architecture is a compact recombination of existing ideas. Strongest adversary argument: Tumbleweed-on-grid with different aggregation. Strongest rebuttal: counter-adjacency as a real competing strategy has no analog in Tumbleweed, Go, or Othello.
- **Replayability: 3** — After 2–3 games the optimal strategy is apparent (greedy densification by P1, mirror-then-densify by P2, occasionally counter-adjacency). Games run 25–31 moves with highly predictable trajectories. Variance comes mainly from opening cell choice among the four equivalent central cells.
- **Overall "Would I play this again?": 3** — Pedagogically interesting as a minimal example of influence-field games. Not fun for more than a few rounds because tempo dictates outcome and the decision space is narrow.

### CLOSEST KNOWN-GAME ANALOG

**Tumbleweed.** Both are influence-field placement games where opposing fields cancel and majority influence wins. It is not identical because (i) Tumbleweed uses line-of-sight influence on a hex board vs this game's orthogonal radius-1 on grid, (ii) Tumbleweed ends at a fixed terminal state and compares cell-majorities; this game races to a scalar threshold, and (iii) Tumbleweed has no capture mechanic (this game has surround capture — even if strategically inert).

### KILLER FLAWS

1. **Surround capture is inert.** In 3 full games no captures occurred. The capture_rule line is dead in practice — a 4-move investment for a 0.93 swing loses the race.
2. **P1 tempo dominance.** Under best play P1 wins essentially every time. No komi, no P2 bonus, no simultaneous mechanic to mitigate.
3. **Narrow strategic landscape.** "Greedy densify" is near-optimal, reducing the game to a counting exercise.

### BEST QUALITY

The **counter-adjacency cancellation** dynamic is the most interesting emergent feature. Placing your stone directly next to an enemy stone reduces both players' effective totals — creating a genuine tension between "density for yourself" and "denial to opponent" that rarely appears in conventional abstract games. In Game 3 it narrowed a natural 5-point P1 lead to 2.8 points, showing that it's a real strategy. If the game had a genuine P2 equalizer, this cancellation mechanic would be the game's signature.

### IMPROVEMENT IDEAS

**Give P2 a meaningful handicap.** The cleanest fix: a standard Go-style komi equivalent. Either (a) subtract ~2 effective-value points from P1's total before threshold check, or (b) give P2 an initial free stone at the center before P1 plays. This turns the tempo race into a genuine contest and unlocks the cancellation dynamic as a real P1 choice (accept value loss vs risk P2 pulling ahead).

A runner-up improvement: **make surround-capture strategically relevant** by lowering the influence decay so each stone contributes less, thereby making the +0.93 from capture worth more relative to a placement move. Or raise capture reward by giving captured cells a lasting negative influence. Currently the capture rule is vestigial.
