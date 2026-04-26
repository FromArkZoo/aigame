# Team-5 — Fractal Spike Evaluation, Pair A

**Team ID:** team-5
**Pair:** A
**Fractal candidate:** `frac_A_fractal` (sierpinski 9×9, 17 holes, 64 active cells)
**Control candidate:** `frac_A_control` (torus 8×8, 64 cells)
**Source game:** R16 winner `c6bb58075520` — alt + outnumber-2 + radius-1 influence (s=0.932, d=0.510) + threshold-22.645

---

## Phase 1 — Rule Comprehension

The two JSONs are byte-identical apart from `topology_type` (sierpinski vs torus) and `axis_size` (9 vs 8); all other rule blocks (placement, capture, propagation, win condition, turn structure) match exactly.

**Shared ruleset (3 sentences):** Players alternate placing a single stone on an empty cell; after each placement, every adjacent enemy stone with ≥2 friendly neighbours of the placer is removed (outnumber-2 capture). Each placed stone propagates influence of strength 0.932 to its own cell and 0.475 to each radius-1 neighbour, accumulating into a per-cell `board_value` (positive for P1, negative for P2). The first player whose total `board_value` summed over their owned cells crosses 22.645 (margin-based per the R16 fix) wins; otherwise the game ends in piece-majority at turn 100.

**Substrate-specific degeneracy flagged:**
- **Lower max-degree on fractal.** A 3×3 block in the corner (e.g. NW) has only 8 cells (the centre is a hole), so the densest *fully-clean* block accessible without crossing a hole is 2×3 (6 cells) or 3×2. The torus, by contrast, allows 4×4 contiguous clusters everywhere with uniform degree 4.
- The threshold (22.645) is held constant despite the fractal's reduced clustering ceiling — Critic point (b) is *prima facie* valid and must be tested in play.
- No reachability dead zone: every active cell on the Sierpiński carpet remains connected, so the win condition is not unreachable, just costlier per stone.
- Engine sanity: `play_helper.py` correctly filters hole cells out of `legal_actions` (65 actions on initial board: 64 placements + 1 pass).

---

## Phase 2 — Strategic Play

I played both games through to a decisive threshold-crossing. The same pattern was used for both: P1 attempts to grow a tight cluster in one corner; P2 mirrors in the opposite corner, then tries one disruption when P1 reaches striking distance. **Seats were swapped between games:** in game 1 the "NW-builder" plays P1; in game 2 the "SE-builder" plays P1.

### Game 1 — Fractal (NW-builder is P1)

Move-by-move (effective scores reported by harness; full transcript captured by `eval_helper.py`):

| # | Player | Move | P1_eff | P2_eff | Reasoning |
|---|---|---|---|---|---|
| 1 | P1 | (3,0) | 0.93 | 0.00 | Top of N sub-block; hole-bordered (degree 3). Anchor for column-3 chain. |
| 2 | P2 | (5,8) | 0.93 | 0.93 | Mirror in S sub-block. |
| 3 | P1 | (3,1) | 2.82 | 0.93 | Chain south; (3,1) sits next to hole (4,1) — using it as a structural wall. |
| 4 | P2 | (5,7) | 2.82 | 2.82 | Mirror. |
| 5 | P1 | (3,2) | 4.70 | 2.82 | Complete column 3 of N sub-block (south boundary is the central hole — natural stop). |
| 6 | P2 | (5,6) | 4.70 | 4.70 | Mirror. |
| 7 | P1 | (4,0) | 6.58 | 4.70 | Branch east along row 0; (4,0) sits between active row-0 cells with hole below. |
| 8 | P2 | (4,8) | 6.58 | 6.58 | Mirror. |
| 9 | P1 | (2,2) | 8.46 | 6.58 | Hop into NW sub-block; will route around hole (1,1). |
| 10 | P2 | (3,8) | 8.46 | 8.46 | Mirror. |
| 11 | P1 | (2,0) | 10.35 | 8.46 | Top-anchor column 2 in NW sub-block. |
| 12 | P2 | (6,8) | 10.35 | 10.35 | Mirror. |
| 13 | P1 | (2,1) | 14.13 | 10.35 | **Substrate-specific:** (2,1) has 3 active neighbours (hole at (1,1) removes one) — placing here yields 3 friendly bonds at once → +3.78 instead of the normal +2.83 for an interior cell. The hole *concentrates* my friendly bonds. |
| 14 | P2 | (6,7) | 14.13 | 13.18 | Mirror, 3 friends. |
| 15 | P1 | (5,0) | 16.01 | 13.18 | Bridge into N sub-block right column. |
| 16 | P2 | (1,8) | 16.01 | 14.11 | P2 hits a low-degree fork (its cluster bumps the (1,7) hole). |
| 17 | P1 | (5,1) | 17.89 | 14.11 | Pillars (3,*) and (5,*) sandwich hole (4,1) — a P2 stone *cannot* be inserted between them. Free defensive geometry. |
| 18 | P2 | (0,8) | 17.89 | 15.99 | P2 still mirroring on bottom row. |
| 19 | P1 | (5,2) | 19.78 | 15.99 | Three-stone column sealed; cluster now spans 10 stones bridging N + NW. |
| 20 | P2 | (8,7) | 19.78 | 16.93 | P2 routes around hole (7,7). |
| 21 | P1 | (6,0) | 21.66 | 16.93 | One stone from threshold. |
| 22 | P2 | (6,1) | 20.71 | 16.91 | **Disruption attempt — substrate-specific.** (6,0) has only 3 active neighbours: (5,0), (7,0), (6,1) — because (7,1) is a hole. If P2 follows up with (7,0) next turn, (6,0) is captured (outnumber-2 satisfied). On the torus, (6,0)-equivalent has 4 neighbours so P2 would need 2 stones placed before capture, taking 4 plies. Fractal accelerates capture by 1 ply. |
| 23 | P1 | (6,2) | 22.12 | 16.93 | **Counter-capture.** Placing (6,2) makes the threatening P2 stone at (6,1) have 3 P1 neighbours — (5,1), (6,0), (6,2) — and (7,1) hole isn't counted: 3≥2 → (6,1) removed. P1 now at threshold-distance 0.5; P2 lost a piece. |
| 24 | P2 | (7,0) | 21.64 | 17.38 | P2 still tries the corner, but with no (6,1) seed the threat is gone. The placement also propagates -0.475 onto P1's (6,0), nudging P1 back below threshold. |
| 25 | P1 | (7,2) | **23.52** | 17.38 | One quiet move (1 friendly neighbour) crosses the line. **P1 wins.** |

**Endgame:** Decisive threshold cross at move 25 (P1=23.52 vs P2=17.38; margin 6.14). Did NOT hit max_turns. One capture (P1 captures the lone P2 disruption stone at (6,1)). Final piece counts: P1=13, P2=11.

**Substrate-specific strategy adopted:**
1. **Sandwich-the-hole defence (M17).** P1 built two parallel columns (3,*) and (5,*) around the (4,1) hole. Result: P2 *cannot ever* play in between; P1 enjoys a free wall. There is no equivalent on the torus.
2. **Low-degree leverage (M13).** Placing on (2,1) — degree 3 because of hole (1,1) — yielded 3 immediate friendly bonds for one stone (+3.78), the highest single-move gain in the game. Holes adjacent to my own cluster *amplify* my own move's value.
3. **Hole-accelerated capture exchange (M22–M23).** Played out a tactical sequence that's only available because (7,1) hole reduced (6,0) to degree 3, putting it within 2-stone capture range. This is the cleanest substrate-only tactic of the game.

### Game 2 — Control / Torus 8×8 (SE-builder is P1, seats swapped)

Same opening logic, mirrored across the torus.

| # | Player | Move | P1_eff | P2_eff | Note |
|---|---|---|---|---|---|
| 1 | P1 | (5,7) | 0.93 | 0.00 | Anchor SE. |
| 2 | P2 | (3,0) | 0.93 | 0.93 | Anchor N — but on torus, (3,0)↔(3,7) is *adjacent* via wraparound. |
| 3 | P1 | (5,6) | 2.82 | 0.93 | |
| 4 | P2 | (3,1) | 2.82 | 2.82 | |
| 5 | P1 | (5,5) | 4.70 | 2.82 | |
| 6 | P2 | (3,2) | 4.70 | 4.70 | |
| 7 | P1 | (4,7) | 6.58 | 4.70 | |
| 8 | P2 | (4,0) | **6.10** | 6.10 | **Wraparound conflict** — (4,0) is torus-adjacent to (4,7), so P2's stone propagates -0.475 onto P1's stone. P1 *loses* 0.475 just from P2 placing in their own corner. Cannot happen on fractal (the central 3×3 hole separates the two builds). |
| 9 | P1 | (5,4) | 7.99 | 6.10 | |
| 10 | P2 | (3,3) | 7.99 | 7.99 | |
| 11 | P1 | (6,7) | 9.87 | 7.99 | |
| 12 | P2 | (2,0) | 9.87 | 9.87 | |
| 13 | P1 | (6,6) | 12.70 | 9.87 | |
| 14 | P2 | (2,1) | 12.70 | 12.70 | |
| 15 | P1 | (4,6) | 15.54 | 12.70 | |
| 16 | P2 | (4,1) | 15.54 | 15.54 | Tied — wraparound has fully neutralised P1's first-move lead. |
| 17 | P1 | (3,7) | 16.94 | 15.06 | Reaching toward P2 — but (3,7) is wrap-adjacent to P2's (3,0), so the P1 stone *also* gets -0.475 from P2 propagation. |
| 18 | P2 | (5,0) | 16.47 | 16.47 | Same wrap suppression. |
| 19 | P1 | (3,6) | 19.30 | 16.47 | |
| 20 | P2 | (5,1) | 19.30 | 19.30 | Tied again at 19.30. |
| 21 | P1 | (4,4) | 21.19 | 19.30 | |
| 22 | P2 | (4,2) | 21.19 | **22.14** | **P2 reaches striking distance** — torus tempo allows P2 to keep pace. P2 now needs +0.51 to win; P1 needs +1.46. |
| 23 | P1 | (4,5) | **24.97** | 22.14 | P1 has the move and 4 friendly neighbours of (4,5) — pushes safely over. **P1 wins.** |

**Endgame:** Decisive threshold cross at move 23 (P1=24.97 vs P2=22.14; margin 2.83). Did NOT hit max_turns. **Zero captures.** Final piece counts: P1=12, P2=11.

**Substrate-specific strategy adopted:** None — pure cluster-building both sides; wraparound constantly subtracted from leading player's score, keeping the game tense but offering no tactical fork.

---

## Phase 3 — Strategic Analysis

### Did the fractal play differently?

Yes, in three concrete ways, and one larger structural way:

1. **Capture geometry was substrate-dependent.** The only capture in either game (Game 1, M23) hinged on (7,1) being a hole: it dropped (6,0)'s degree from 4 to 3 and put it within 2-stone outnumber range. The control torus has uniform degree 4 — the equivalent capture would require 2 dedicated P2 stones placed *before* the corner stone is occupied, costing 2 plies of tempo P2 doesn't have.
2. **Hole-amplified moves.** Move 13 on fractal (2,1) yielded +3.78 (3 friends of a degree-3 cell) — the highest single-move gain of either game. On torus, any cell has 4 neighbour slots so a single move can in theory yield +4.73 (4 friends), but in practice early game has no isolated cell with 4 friends pre-placed. The fractal bunches friends into low-degree cells, making 3-friend moves *easier to set up*.
3. **Wraparound vs central wall.** Torus had every move on opposite-corner P2 *subtracting* from P1's score (M8: P1 dropped 0.475 from a P2 placement on the wraparound edge). Fractal's central 3×3 hole acts as a perfect insulator: through the entire game, *no* P2 move on the S sub-block ever subtracted a single milli-point from P1's N-block stones. Distance-via-graph through the carpet is large.
4. **Sub-block districting (latent).** The 8 sub-blocks form natural strategic regions. In our games, each player took one corner sub-block and bridged through one neighbour, never contesting the same sub-block. A more adversarial line could exploit this, but it didn't surface naturally.

### Choke points

Yes. On fractal, cells like **(4,0), (4,2), (4,6), (4,8), (0,4), (2,4), (6,4), (8,4)** are corridor cells: they sit on the only edge connecting two sub-blocks. (4,0) connects N to NW and NE via row 0. Capturing or holding such a cell denies the opponent route options for a connection-style win (irrelevant in Pair A's threshold rule, but the *geometry* exists). On torus, no cell has elevated routing significance.

### Influence shadows

Confirmed. Through the central hole there is **zero influence cross-talk** between N and S clusters. On torus, every move is within ≤4 graph-distance of every other move, so propagation cross-talk is constant background noise (and in fact it's exactly what kept the torus game balanced — the trailing player was slowly poisoning the leader's own cells via wrap).

### Path routing / tempo asymmetry

For the P2 disruption on fractal (M22–M24), the path from P2's S-cluster to P1's N-cluster requires routing through one of the four "side corridors" (cols 0–2, 6–8 in rows 3–5). P2 spent the entire game far from P1's cluster and had to *manufacture* a threat from a fresh stone at (6,1), with no support. On torus, P2's column-5 stones at (5,0)/(5,1) were already directly poking P1 via the wrap. **Net tempo:** torus benefits the trailing player (constant wrap interference); fractal benefits the leader (the central hole shields their cluster).

### Tempo / first-move advantage

**Fractal: stronger first-move advantage.** P1 won by margin 6.14, with P2 nowhere near threshold (17.38 / 22.65 = 77%). **Torus: weaker first-move advantage.** P1 won by margin 2.83, with P2 at 22.14 / 22.65 = 97% — one extra ply for P2 and the game is a draw or P2 win.

### Quantitative metric (game-length + decisiveness)

| metric | fractal | control |
|---|---|---|
| game length (moves) | 25 | 23 |
| stones placed | 24 | 23 |
| captures | 1 | 0 |
| winning margin (eff) | 6.14 | 2.83 |
| loser-fraction-of-threshold | 0.77 | 0.98 |

The control was 22 percentage points more competitive on the loser-fraction metric.

---

## Phase 4 — Substrate Critic (mandatory)

### Critic argues:

(a) **"Fractal = grid with extra dead cells."** The 17 holes don't add any new mechanics — they just reduce cell count. The placement rule, capture rule, propagation rule, and win condition are all *cell-local*; they don't reference holes specially. Whatever a stone does on cell `c`, it does identically on fractal and grid. So no new mechanics, just a different cell graph.

(b) **"Threshold scaling artefact."** Threshold is held at 22.645 across both substrates. But the fractal's max cluster density is lower (every contiguous 3×3 block has a hole). So the fractal is just "the same game with a harder threshold" — the apparent difference (P1 needed 13 stones vs 12 on torus) is just threshold-tightness, not new strategy. If we'd scaled threshold to 22.645 × 8/9 ≈ 20.13 on the fractal to compensate, the games would feel identical.

(c) **"Expert transfer test."** A player who mastered torus 8×8 with this ruleset would transfer ~95% of their strategy to fractal: open in a corner-ish cell, build a tight cluster, fork a friendly cell with three friends to maximise per-move gain, defend cluster perimeter against outnumber capture. The only adjustment is "don't place where a hole is and avoid stones whose only escape route runs into a hole." That's avoidance, not new strategy.

### Player rebuttal (P1 + P2):

**Specific Phase-2 moments where the substrate genuinely changed strategy:**

1. **Move 17 (sandwich defence).** I deliberately placed (5,1) so that my columns (3,*) and (5,*) flanked the (4,1) hole. This created an *inviolable wall* at (4,1) that no opponent stone can ever enter. There is no equivalent on the torus — *no torus cell is unenterable.* Critic point (a) — "grid with dead cells" — *concedes* this: the dead cells *are* the new feature. Calling them "just dead" is dismissive; *strategically using* the dead cells as walls is a non-trivial tactic.

2. **Move 22–23 (hole-accelerated capture).** This was a substrate-only tactic: the (7,1) hole reduced (6,0) to degree 3, putting it in 2-stone capture range. I had to read this 3 plies deep to defend correctly. On torus, no cell is in 2-stone capture range from move 21, ever. Critic (b) — "harder threshold" — would predict the fractal game is *slower*, not that *new* tactical sequences emerge. We saw exactly such a sequence.

3. **Move 13 (3-friend bonus).** A degree-3 cell that I have 3 stones already adjacent to gives +3.78 in one move. On torus a degree-4 cell with 3 friends gives +3.78 too (same arithmetic), but to *get* 3 friends adjacent to a single cell takes more setup on torus because cells are more spread out. The fractal *concentrates* friends because the hole-bordered cells have small adjacency sets — 3-of-3 is reachable in fewer plies than 3-of-4 in torus play. This is a real tempo difference; not just threshold-scaling.

**However**, the rebuttal is not overwhelming. Three local tactical wrinkles do not amount to *fundamentally new strategic considerations I had to learn from scratch*. Most of the game was identical: build a cluster, push to threshold. The sub-block district structure (potentially the deepest substrate-specific feature) didn't surface in adversarial play because both players had no incentive to contest the same sub-block. We'd need a different ruleset (connection win, or area control) to elicit it.

**Substrate-novelty score (1–10): 4** — Real, specific, replicable tactical effects exist (sandwich-walls, hole-accelerated capture, friend-concentration on low-degree cells) but they sit on top of a strategic backbone unchanged from the rectangular game. The Pair-A ruleset (threshold-on-influence) doesn't pull on the deepest fractal features (sub-block districting / forced detours) — those would need a connection or routing-based win condition to matter.

---

## Phase 5 — Verdict

**Team ID:** team-5
**Pair:** A
**Fractal candidate:** frac_A_fractal
**Control candidate:** frac_A_control

### Fractal scores

- **Strategic Depth: 6** — Same fundamentals as the R16 source game (build cluster → threshold). Substrate-specific tactics (sandwich-defence, hole-accelerated capture) add a genuine tactical layer worth ~+0.5 over the source, but no new strategic concept.
- **Balance: 4** — Single-game seat-swap evidence: P1 (NW-builder) won by margin 6.14, with P2 stuck at 77% of threshold. The central hole shielded the leader, which compounds first-move advantage. Worse than control on this dimension. (Acknowledged: only 1 game per seat; full balance verdict needs 2× this.)
- **Novelty (post-critic): 5** — Hole-as-wall and hole-degree-amplification are genuine novelties but scoped to local tactics. Substrate critic's "harder threshold" framing partially holds. Sub-block districting unexplored under this ruleset.
- **Substrate-novelty: 4** — See Phase 4. Real but local; doesn't dominate gameplay.
- **Overall "Would I play this again?": 5** — Slight curiosity bonus over pure-grid version, but also more decisive (less interesting outcome).

### Control scores

- **Strategic Depth: 6** — Identical backbone. Wraparound creates constant cross-cluster pressure that keeps the game competitive without adding new mechanics.
- **Balance: 7** — P1 won by margin 2.83; P2 was at 97% of threshold. Wraparound is naturally balancing because the leader's stones are always within ≤4 graph-distance of the trailing player's pressure stones.
- **Novelty (post-critic): 5** — R16 well-trodden territory; no new ground.
- **Overall "Would I play this again?": 6** — More competitive, more tactical pressure throughout, no decisive moment until move 22–23.

### Delta (fractal − control)

- **Strategic Depth: 0**
- **Balance: −3**
- **Overall: −1**

### Critical assessment

- **"The fractal substrate genuinely added strategic depth": NO** — for Pair A specifically. It added local *tactical* depth (≥3 concrete examples). Strategic depth (long-horizon planning, novel objectives) was unchanged. The Pair A ruleset (threshold on influence) doesn't load on the substrate's distinctive features.

- **Phenomena observed only on fractal:**
  - Sandwich-the-hole defensive structure (move 17).
  - Hole-accelerated outnumber capture: degree-3 corner cell capturable from a single 1-stone seed (moves 22–23).
  - Concentrated-friends bonus: degree-3 cell hits 3-of-3 friends in fewer plies than degree-4 (move 13).
  - Insulated clusters: 0 cross-influence between opposite sub-blocks separated by central hole.
  - Sub-block districting (latent — never adversarially contested in our game; would emerge with different rules).

- **Phenomena observed only on control:**
  - Wraparound cross-cluster propagation: every opponent placement on the wrap-edge subtracts from the leader's effective (move 8 onward).
  - Balanced tempo: trailing player can stay within striking distance throughout.
  - No "natural walls" — every cell is contestable.

- **Recommendation for R17: SECOND-PROBE.**
  Pair A's ruleset under-uses the fractal's structural features. Before deciding integrate vs drop, we should test whether the fractal pays off under a *connection* or *district-control* win condition (cf. Pair C). If those experiments show ≥2-point Strategic-Depth deltas, integrate the substrate but pair it specifically with routing/connection rules. If not, drop. For this Pair A specifically (alt+outnumber+influence+threshold), I lean DROP — but the experiment should be re-run with at least one game where both players contest the *same* sub-block, which our cooperative-corner opening did not test.
