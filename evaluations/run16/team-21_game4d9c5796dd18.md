# Team-21 Evaluation — Game `4d9c5796dd18` (Run 16, Rank 5)

## PHASE 1 — RULE COMPREHENSION

**Board.** 8×8 grid (64 cells), 2D, **moore** topology (8-neighbor adjacency, Chebyshev distance). 65 actions: 64 placement actions (`y * 8 + x`) plus action 64 = PASS.

**Turn structure.** **ALTERNATING** (1 piece per turn), `pieces_per_turn=1`. Two consecutive passes end the game as a draw (R16 fix; previously resolved by piece majority).

**Action types.** Place only — no movement.

**Placement constraints.** Place on any empty cell. `first_move_anywhere=True` (no center-restriction). No suicide rule mentioned, but suicide doesn't matter much because of the propagation/win mechanic.

**Capture rule.** `surround` (Go-style "0 liberties → group removed"), `threshold=2` field is unused for surround (only outnumber consults it). On a moore topology this means a friendly stone is captured only when **all 8 neighbors are enemy** (or board-edge). In practice: degenerate / inert — no realistic game arrives at a single-stone enclosure before someone wins on threshold. (Cluster captures even harder: a 2-stone group needs ~10 surrounding enemies.) Note: the R16 generator was supposed to "downgrade moore → grid when surround capture is present," but this game (gen 9–10) escaped that filter.

**Influence propagation.** Type `influence`, **radius=2**, **strength≈1.6836**, **decay≈0.7205**. On placement, the placed cell adds `+strength * decay^d` (P1) or `-strength * decay^d` (P2) to `board_values[c]` for every cell `c` within Chebyshev distance 2. So the deltas are: d=0 → ±1.68, d=1 → ±1.21, d=2 → ±0.87. A 5×5 footprint per stone; the field is clipped to [-100, +100].

**Win condition.** `threshold` type, threshold ≈ **50.508**. The check sums `board_values[c]` over each player's owned cells: `effective_P1 = Σ values[c] for c where owner=P1`; `effective_P2 = -Σ values[c] for c where owner=P2`. First to exceed 50.508 wins; same-tick double-cross resolves by margin (R16 fix), equal margins → draw. Max turns = 100.

**Degeneracy flags.**
- **Capture rule effectively inert** on moore + 8-neighbor; the generator was specifically supposed to filter these out — this game slipped through.
- **Threshold reachable** by an isolated 7–8-stone cluster — confirmed in Phase 2. A solo stone in the open contributes ~25 to its own cell, plus large field, but the score sums *only on owned cells*, so clustering is what compounds.
- **First-mover tempo** is structurally large: in three games the threshold-cross arrives on P1's 8th stone (move 15) when both sides cluster. P2 is in a deficit because the marginal stone always raises the placer's effective by enough to push past the line.
- **No double-pass / max-turns issue** in real play — games end at ~move 13–17 by threshold.
- The CA is not engaged (`Cellular Automaton: No (classic)`).

## PHASE 2 — STRATEGIC PLAY

All moves verified against `engine.step()` via `/tmp/team21_play.py` (loads `factory.create_engine`). Influence field read from `engine.board_values`; effective scores recomputed each move.

### Game 1 — P1 cluster vs P2 mirror cluster (P1 in NW, P2 in SE)

| Move | Player | Cell | P1 eff | P2 eff |
|----:|:------|:----|------:|------:|
| 1 | P1 | (3,3) | 1.68 | 0.00 |
| 2 | P2 | (4,4) | 0.47 | 0.47 |
| 3 | P1 | (2,2) | 3.71 | -0.40 |
| 4 | P2 | (5,5) | 2.83 | 2.83 |
| 5 | P1 | (3,2) | 8.49 | 1.96 |
| 6 | P2 | (4,5) | 7.62 | 7.62 |
| 7 | P1 | (2,3) | 14.83 | 5.87 |
| 8 | P2 | (5,4) | 13.09 | 13.09 |
| 9 | P1 | (4,2) | 21.37 | 11.34 |
| 10 | P2 | (3,5) | 19.62 | 19.62 |
| 11 | P1 | (2,1) | 31.40 | 19.62 |
| 12 | P2 | (5,6) | 31.40 | 31.40 |
| 13 | P1 | (3,1) | 46.29 | 31.40 |
| 14 | P2 | (4,6) | 46.29 | 46.29 |
| **15** | **P1** | **(1,2)** | **60.49** | 46.29 → **WIN P1** |

**P1 reasoning per move:** open in the highest-value cell (3,3); diagonally extend out from P2 to keep maximum cluster overlap; build a 2×2 → 3×3 footprint. Predicted P2 mirror response (correct, almost always).

**P2 reasoning per move:** match P1 step-for-step, diagonally opposite, hoping symmetry breaks P1's tempo lead via the R16 margin tiebreak. It does not — same-tick crossings only resolve by margin if BOTH cross in the same call to `_check_threshold`; alternating moves give P1 the cross alone.

**Reflections.**
- *P1:* "Strategy: tight cluster, every stone goes in a cell already inside my radius-2 footprint of two others. Would not change. P2 didn't surprise me — perfect mirror was unwinnable for them. Endgame reached the stated 50.5 threshold cleanly on move 15."
- *P2:* "I thought mirroring would force the R16 same-tick margin tiebreak. It doesn't, because alternating placement means I cross on **my** move (move 16), but P1 already won on move 15. To win I'd need to either disrupt P1's cluster or cluster more efficiently — neither is geometrically possible against an equal opponent."

### Game 2 — P1 cluster vs P2 disrupt (P2 plays at distance 2 inside P1's radius)

P2 abandons mirror and plants at (3,5) on move 2 (distance 2 from P1's (3,3)) to drain P1's effective via negative field on the P1-owned cell.

| Move | Player | Cell | P1 eff | P2 eff |
|----:|:------|:----|------:|------:|
| 1 | P1 | (3,3) | 1.68 | 0.00 |
| 2 | P2 | (3,5) | 0.81 | 0.81 |
| 3 | P1 | (2,3) | 4.05 | -0.06 |
| 4 | P2 | (4,5) | 2.30 | 2.30 |
| 5 | P1 | (3,2) | 8.83 | 2.30 |
| 6 | P2 | (3,6) | 8.83 | 8.83 |
| 7 | P1 | (2,2) | 17.79 | 8.83 |
| 8 | P2 | (4,6) | 17.79 | 17.79 |
| 9 | P1 | (4,2) | 27.83 | 17.79 |
| 10 | P2 | (4,7) | 27.83 | 27.83 |
| 11 | P1 | (4,3) | 38.54 | 26.08 |
| 12 | P2 | (3,7) | 38.54 | 38.54 |
| **13** | **P1** | **(2,1)** | **52.06** | 38.54 → **WIN P1** |

P1 wins one move *earlier* here (move 13, only 7 stones). P2's "disrupt" actually conceded the front edge of P1's cluster more efficiently. The disruption stone at (3,5) drained P1 by 0.87 once but locked P2 into a non-overlapping cluster region — and P2 fell behind on cluster size.

**Reflections.**
- *P1:* "Same plan, faster win because P2 split between disruption and own cluster. P2 disrupted exactly one stone of mine and committed to the same column 3 axis — the disruption gave P2 only marginal value while costing P2 a cluster-anchoring move."
- *P2:* "Disrupt-and-cluster is strictly worse than parallel-cluster. The single-square drain on P1 is not enough to offset the lost tempo on my own footprint. I should have just mirrored — at least it loses by the same margin."

### Game 3 — Seat swap: I play P2, opponent plays P1 with cluster strategy

P2 (me) plays AT distance 1 from P1's center, then builds own cluster aggressively.

| Move | Player | Cell | P1 eff | P2 eff |
|----:|:------|:----|------:|------:|
| 1 | P1 | (3,3) | 1.68 | 0.00 |
| 2 | P2 | (4,3) | 0.47 | 0.47 |
| 3 | P1 | (2,2) | 3.71 | -0.40 |
| 4 | P2 | (4,4) | 1.62 | 1.62 |
| 5 | P1 | (1,2) | 7.48 | 1.62 |
| 6 | P2 | (5,4) | 6.60 | 7.28 |
| 7 | P1 | (2,1) | 14.01 | 6.41 |
| 8 | P2 | (5,3) | 13.14 | 14.49 |
| 9 | P1 | (1,1) | 23.85 | 14.49 |
| 10 | P2 | (5,5) | 22.97 | 23.65 |
| 11 | P1 | (1,3) | 34.75 | 23.65 |
| 12 | P2 | (4,5) | 33.88 | 35.24 |
| 13 | P1 | (3,1) | 45.66 | 33.49 |
| 14 | P2 | (6,4) | 45.66 | **47.69** |
| **15** | **P1** | **(3,2)** | **58.46** | 43.86 → **WIN P1** |

**Critical observation:** at move 14, P2 was AHEAD of P1 (47.69 vs 45.66). But the game-ending crossing happens on the next move, and that next move is P1's. P2 cannot interpose. Even when P2 has the lead in effective score, **alternating tempo ensures P1 always crosses the line first** when both players are equally proficient at clustering.

**Reflections.**
- *P2 (me):* "Adjacent disruption is geometrically more useful than mirror — I actually got ahead by move 14. But it doesn't matter: tempo wins. The tiebreak only fires when *both* cross in the same `_check_threshold` call, and that requires a simultaneous move structure, which this game does not have."
- *P1:* "I just clustered. The seat advantage is decisive."

### Bonus: bad-P1 sanity test

P1 scatters (corners (0,0),(7,7),(0,7),(7,0),(4,0),(4,7),(0,4),(7,4)), P2 clusters at (3,3) center. P2 wins on move 14, P2 effective = 55.4, P1 effective = 9.2. Confirms the game is NOT a forced P1 win — only an equal-skill P1 win. A P1 who fails to cluster loses.

### Strategy guides

**P1 strategy guide.** Open (3,3) or (4,4). Every subsequent stone must lie within Chebyshev distance ≤ 2 of at least two existing P1 stones, and inside the convex footprint of the existing cluster. Build a 3×3 → 4×3 footprint. Ignore P2 unless P2 enters your cluster — then fill the radius-1 ring. You will cross threshold on your 7th–8th stone (~move 13–15).

**P2 strategy guide.** No winning line against an equal-skill P1. Best practical play: cluster equally hard at a diagonally-opposite quadrant, hoping P1 mis-steps or scatters. If P1 plays a single non-clustering move, **immediately** punish by tightening your own cluster — the tempo deficit shrinks to nothing. Disruption (placing inside P1's footprint) is *worse* than parallel clustering because it splits your own placement budget.

## PHASE 3 — STRATEGIC ANALYSIS (joint)

**Distinct viable strategies?** One dominant strategy: tight clustering. Disruption, mirror, and territory-spread are all strictly worse. The only "axis" of choice is *where* on the board to anchor the cluster (any 4×4 sub-region works, edge cells slightly worse since they can't reach 5×5 of dist-2 neighbors).

**Counter-play?** Effectively none. P2 can punish P1's mistakes (Bonus run) but cannot punish optimal P1 play.

**Short-term vs long-term tension?** None. Every move is short-term (immediate +Δ to your effective score). There is no setup → payoff structure, no sacrifice, no positional vs material trade-off. The game is purely greedy-additive.

**Emergent concepts?** *Influence territory* exists — but the relevant scoring rule (sum on **owned** cells) collapses it back to "place stones in your own influence zone," which is just clustering. There is no tempo, initiative, ko, mutual-annihilation, or sacrificial play. Capture exists in the rules but cannot fire in real play. Topology (moore) matters only insofar as the radius-2 Chebyshev footprint = 5×5 (vs 3×3 for von Neumann radius 2). It does **not** add geometric depth.

**First-mover advantage (alternating).** Decisive. Across three games with equal-skill players, P1 won 3/3, all by reaching threshold on the 13th–15th move (P1's 7th–8th stone). The seat-swap (Game 3) confirmed: even a P2 strategy that puts P2 *ahead* in effective score by move 14 still loses, because P1's move 15 crosses first. The R16 margin-based threshold fix is irrelevant here — same-tick crossings cannot occur in alternating play. The only way to expose seat asymmetry would be simultaneous placement, which this game does not have. **Quantified: 3/3 P1 wins; seat-swap result identical → first-move advantage is not a probabilistic edge but a structural certainty.**

**Acknowledged seat-identity bias:** since one agent played all roles, both "players" are the same skill. The seat advantage we measure is the upper bound (equal-skill); a weaker P1 would lose to a stronger P2 (Bonus run). But generator-fitness measurements use uniformly-trained agents on both sides, so equal-skill is the relevant regime.

## PHASE 4 — NOVELTY ADVERSARY

**Adversary's case.** This game is "Reversi/Othello with a Gaussian splat instead of flips."
- It is on a 8×8 board (Othello).
- Each placement has a radius-of-effect (like an aura, like Risk-of-Reign or Tumbleweed's pile-strength rules).
- The win condition is a numeric majority threshold (like Tumbleweed's piece-count, like Reversi's count-the-pieces).
- The capture rule (Go-style surround) is **inert** — it functions as decoration. So topologically the game is "place pieces, accumulate radius-2 score on your own cells, first to N wins" — essentially **Tumbleweed lite** or **a degenerate Risk**: just clustering your own stones to compound a local field.
- An expert at Tumbleweed (Mark Steere) or at influence-area Go variants would transfer immediately: the dominant strategy ("build the densest radius-r ball") is identical.
- The moore topology is window-dressing: any topology with a notion of distance and a self-overlapping kernel produces the same dynamic.
- Conclusion: not novel; it is "**Tumbleweed-on-an-8×8 grid with a fixed 5×5 Gaussian kernel and a numeric threshold instead of LoS-based stack-count**."

**Rebuttal (P1 + P2 jointly).**
- The **scoring on owned cells** (rather than on field-controlled cells) is genuinely different from Tumbleweed and from any standard influence-area game we know. Tumbleweed's score is "cells where you have line-of-sight majority"; Reversi's is "cells you own"; this game's is "field value summed on cells you own" — a hybrid that doesn't appear in the canonical catalog. (Whether this hybrid is *interesting* is a separate question — see Killer Flaws.)
- However, this difference does **not** produce different play. Phase 2 confirmed the dominant strategy is "cluster densely so your own stones sit on high field value," which is equivalent in practice to standard influence-area games. The mathematical novelty is real; the strategic novelty is not.
- The capture rule, while inert in equilibrium, is *technically* a Go-style rule the strategy must respect. But in three games it never fired, even when one side scattered.
- The R16 generator's intent — find emergent dynamics from rule combinations — is not realized here: the surround capture is dead code, the influence rule is greedy-additive, and the threshold is reachable by a single cluster. There are no rule **interactions** that produce surprise.

**Novelty score (post-adversary): 3/10.** Mathematical hybrid of Tumbleweed + Reversi-style ownership + Go-style (inert) capture. Plays as a degenerate Tumbleweed-clone with no emergent dynamics. An expert at Tumbleweed transfers immediately and dominates.

## PHASE 5 — VERDICT

```
Team ID:        team-21
Game ID:        4d9c5796dd18
Rules Summary:  8x8 moore-topology placement game; each stone radiates Gaussian-decay influence (radius 2, strength 1.68, decay 0.72) onto board_values; first player whose owned-cell influence sum exceeds 50.5 wins; surround capture rule is technically active but unreachable in practice.
Topology:       8x8 grid, moore (8-neighbor / Chebyshev-distance) — radius-2 footprint = 5x5
Turn Structure: ALTERNATING (1 piece per turn)
```

### SCORES (1–10)

- **Strategic Depth: 3** — Single dominant strategy (tight clustering). No tempo, sacrifice, or trade-off structure. Every move is greedy-local. The optimal placement is computed by a 1-ply lookahead on Σboard_values delta. No long-term planning required beyond "stay inside your existing cluster's radius-2 hull."
- **Emergent Complexity: 2** — No emergent concepts. Influence + ownership + capture combine to *exactly* "make your cluster bigger." The surround capture rule is dead. The threshold is hit cleanly on move ~15. No CA. No interaction effects between rules.
- **Balance: 2** — Severe first-mover advantage on equal-skill play. 3/3 games went to P1 by reaching threshold on move 13–15. Even when P2 led in effective score (Game 3, move 14), P2 still lost because P1's next move crossed first. The R16 same-tick margin tiebreak is irrelevant in alternating play. **No seat-swap robustness.** Training data confirms it: of the 4 training runs, two settled at 0.5 final winrate (probably a copy-symmetry artifact / coin-flip from non-converged self-play) and two at 1.0 — a wide bimodal spread that strongly suggests strategy collapse.
- **Novelty (post-adversary): 3** — Mathematical hybrid is technically not on the catalog, but plays exactly like Tumbleweed / Reversi-influence variants. An expert transfers in one game. The "moore + radius-2 + decay" combination is window-dressing on greedy clustering.
- **Replayability: 2** — After 1–2 games you have the dominant strategy. There is no role-asymmetry to explore. There are no traps, ko-fights, sacrifices, or tempo plays. Anchor cluster, fill cluster, win.
- **Overall "Would I play this again?": 2** — No.

### CLOSEST KNOWN-GAME ANALOG
**Tumbleweed** (Mark Steere, 2020) crossed with **Reversi/Othello**'s ownership-count win condition. Not identical: Tumbleweed scores LoS majority, this scores summed-influence on owned cells; Tumbleweed has stack-strength placement constraints, this is anywhere-empty. But the strategic core ("build the densest pile in one place; threshold wins") is the same. An expert would transfer immediately.

### KILLER FLAWS
1. **First-mover wins all equal-skill games.** Three games, three P1 wins on moves 13–15. The R16 margin-based threshold tiebreak is structurally inapplicable to alternating play. The R16 worst-of-three seat-balance probe should have caught this — if it didn't, this game ranking 5th in R16 is calibration evidence the probe is still mis-tuned for alternating threshold games.
2. **Surround capture is inert** on moore + 8-neighbor — needs all 8 cells around a single P1 stone (or 10+ for a 2-stone group), but P1 wins on cluster size 7–8 long before. The R16 generator was supposed to downgrade moore→grid when capture is present, but this generation-10 game escaped the filter (parents were already moore + capture).
3. **No rule interactions.** Influence and capture do not interact in real play because capture never fires. The threshold rule cleanly resolves before any other rule can engage.
4. **Single dominant strategy.** Tight cluster anywhere on the board. No counter-play exists for an equal-skill opponent.
5. **The "pieces_per_turn=1" + alternating + threshold combination structurally guarantees P1 wins** when both players have access to the same dominant strategy. The marginal stone always crosses the line for the player who places it; P1 places one more stone per cycle.

### BEST QUALITY
The **scoring formulation** (sum field on owned cells, where field is colored by placer) is a genuinely interesting hybrid: stones contribute negatively to the *opposing* player's effective score by drainage, not just positively to your own. That creates the non-trivial geometry where placing INSIDE your opponent's cluster is more valuable per-stone than placing in the open. It almost rescues the design — but the alternating-tempo issue dominates so completely that the subtlety never matters in practice.

### IMPROVEMENT IDEAS
**Make this a simultaneous game.** Switching `turn_type` from `alternating` to `simultaneous` (with the R16 mutual-annihilation collision rule) eliminates the structural first-mover certainty, makes the R16 margin-tiebreak relevant, and re-introduces meaningful counter-play (you'd have to predict whether your opponent is clustering-or-disrupting on each step). The same field/threshold mechanic on a simultaneous engine would be a much more interesting design — the very change R16 is putatively trying to validate as bug-free, applied here, would transform a degenerate alternating game into a contested one.

A second-best fix that keeps alternating: **make P2's threshold lower than P1's** (e.g. 50.5 for P1, 47.5 for P2) to compensate the half-tempo gap. Crude but effective.

A third option: **restrict placement to cells within Chebyshev distance ≤ 1 of an existing own stone after move 1** — turns the game into a Hex-like connection puzzle and forces strategic territory carving rather than greedy stacking.
