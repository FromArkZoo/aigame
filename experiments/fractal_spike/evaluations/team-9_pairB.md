# Fractal Topology Spike — Team 9, Pair B Evaluation

**Pair**: B (alt + custodian + influence + threshold; clone of R14 winner `deb4dfe0382d`)
**Fractal candidate**: `frac_B_fractal` (sierpinski 9×9, 17 holes, 64 active)
**Control candidate**: `frac_B_control` (torus 8×8, 64 active)
**Engine**: R16 build (margin-based threshold resolution)

---

## PHASE 1 — Rule Comprehension

The two candidates share an identical ruleset: alternating turns, single placement per turn anywhere on an empty active cell (first-move-anywhere); custodian (Othello-style) capture flips enemy runs bracketed along an axis on placement; influence propagation radius=1, strength=1.874, decay=0.402 stamps a permanent positive (P1) or negative (P2) board-value on the placed cell and each neighbor; the first player whose summed board-value over their owned cells exceeds the threshold 38.616 wins (margin tie-break), or the higher piece-count wins at max_turns=102.

The only declarative difference is `topology_type` (sierpinski vs torus) and `axis_size` (9 vs 8). The 17 holes (central 3×3 + eight outer-sub-block centers) are walls: not legal placements; influence does not propagate across them; custodian walks terminate at them.

**Possible degeneracy flagged**: the threshold (38.616) is held constant despite the fractal's lower mean cell-degree (cells adjacent to holes have only 2 active neighbors instead of 4). This makes per-piece neighbor-influence accumulation slower for some "fortress" cells on the fractal — but our play below shows the effective rate to threshold is essentially unchanged in practice because clusters self-organize around interior cells. Threshold is reachable on both substrates within max_turns; no degeneracy.

---

## PHASE 2 — Strategic Play

Both games employed the same role assignment: Player 1 = aggressive cluster-builder (NW); Player 2 = symmetric mirror (SE). Seats were swapped between games (I played P1's plan in Game 1, P2's plan in Game 2).

### Game 1 — Fractal (P1 perspective)

P1 (X) opened at **(2,2)** — the NW sub-block corner, with all 4 von-Neumann neighbors active (high-influence cell). P2 mirrored at **(6,6)**.

P1 then occupied **(2,4)** — a "fortress" cell whose row-4 neighbors (1,4) and (3,4) are both holes; this cell can NEVER be custodian-captured along row 4. Substrate-aware choice. P2 mirrored (6,4) — the analogous fortress cell on the SE side.

P1 took **(2,6)** to complete a vertical wall in column 2 spanning rows 2–6 with the central holes splitting it into two pairs. The hole-induced split forced P1 to invest a stone bridging each gap (eventually (2,3) and (2,5)) that on a torus would have been optional.

Subsequent P1 moves: (1,2), (1,3), (2,3), (2,5), (1,6), (1,5), (3,2), (2,1) — a tightly packed, hole-shaped cluster wrapping around the (1,1) and (1,4) holes. P2 built a mirror-image cluster in cols 6–7.

**Endgame**: P1 crossed threshold (38.69 vs 35.31) on move 21 by placing (2,1). Margin = 3.38 (≈ one stone's self+neighbor stack). Reached the stated win condition; no double-pass; no captures occurred.

**Did either player adopt fractal-only strategy?** Yes — P1's choice of (2,4) as a fortress cell explicitly traded influence-radiation (only 2 active neighbors → less neighbor-stack) for capture-immunity along row 4. P1's column-2 cluster is hole-shaped: the (1,4) hole inserted an unavoidable break that had to be patched by stones at (1,3) and (1,5), neither of which would be necessary on a torus.

### Game 2 — Control (P2 perspective; seat swap)

Same opening intent on the 8×8 torus. Action IDs are y·8+x. P1 opened (2,2) = action 18; P2 mirrored at (5,5) = action 45 (180° rotation across torus center).

P1 cluster grew through (1,2), (2,3), (1,3), (2,4), (1,4), (2,1), (1,1), (3,2), (3,1) — a clean 3×3 + extensions. **No forced bridge moves**: the cluster could be any contiguous shape because no walls obstructed it. P2 built the symmetric SE cluster.

**Endgame**: P1 crossed threshold (41.71 vs 38.32) on move 21 placing (2,0). Margin = 3.38. Identical to fractal in ply count and margin.

**Did either player adopt substrate-only strategy?** Effectively no. The torus has perfect translation/rotation symmetry, so any placement choice is equivalent up to relabeling. The cluster shape was a free design parameter; on the fractal it was constrained.

---

## PHASE 3 — Strategic Analysis (joint)

**Did the fractal play differently?** *Mechanically*, no: same 21 plies, same 11-vs-10 piece counts, same 3.4 effective-margin victory for P1, zero captures in both. *Strategically*, yes in two narrow ways:

1. **Fortress cells**: (2,4), (6,4), (4,2), (4,6) etc. are flanked by holes on one axis and are therefore custodian-immune along that axis. We verified mechanically: in the control, an X stone at (2,4) is captured by O placing at (1,4) then (3,4); on the fractal those are holes and capture is impossible along row 4.
2. **Forced cluster bridging**: the (1,4) and (1,1) holes split P1's optimal NW cluster, forcing the *order and identity* of bridging moves (must take (1,3) and (1,5) to keep the cluster connected). On the torus, the cluster shape is a free choice.

**Choke points / districts**: Yes. The 3-wide corridor between sub-blocks (e.g. row 2 columns 3–5 connecting NW and NE sub-blocks) is genuinely forced terrain; control of (3,2)/(4,2)/(5,2) determines whether NE is reachable from NW influence.

**Influence shadows**: Confirmed — cell (4,2) only receives influence from (3,2) and (5,2) because (4,1) and (4,3) are holes. So (4,2)'s board-value depends entirely on whoever stacks (3,2) and (5,2). On the control, (4,2) gets influence from all four neighbors; no equivalent dependency.

**Tempo / first-move advantage**: Identical (3.38 margin in both games). The fractal does not redistribute first-move advantage.

**Quantified comparison**:

| Metric | Fractal | Control | Δ |
|---|---|---|---|
| Plies to win | 21 | 21 | 0 |
| Winner | P1 | P1 | — |
| Final P1 effective | 38.69 | 41.71 | −3.02 |
| Final P2 effective | 35.31 | 38.32 | −3.01 |
| Margin (P1−P2) | 3.38 | 3.39 | ≈0 |
| Captures | 0 | 0 | 0 |
| P1 stones | 11 | 11 | 0 |
| P2 stones | 10 | 10 | 0 |

The lower absolute totals on the fractal reflect that some of P1's stones (notably (2,4), (1,5), (1,3)) sit on cells with only 2–3 active neighbors and therefore accumulate less neighbor-stack; on the torus all 11 stones had 4-neighbor sites available. The MARGIN, however, is preserved because both players suffer equally.

---

## PHASE 4 — Substrate Critic

**Critic's claim (a)**: "Fractal is just 8×8 grid with extra dead cells. No new strategic concept. The clusters look the same, the game length is the same, the margin is the same, the winner is the same."

**Critic's claim (b)**: "Threshold-scaling artifact. The threshold is held constant, so the fractal is just 'harder threshold game on fewer high-value cells'. If you scaled threshold by mean-cell-degree, fractal and torus would be indistinguishable."

**Critic's claim (c)**: "An expert in the rectangular custodian-influence game transfers immediately. Cluster build, dense placement, defend the column wall — all carry over verbatim. Any fortress cells are a footnote, not a strategy."

**Player rebuttal**:

- (a) Half-conceded: in QUICK threshold games (≤ 21 plies) where no captures occur, the fractal is decoration. But the substrate creates fortress cells that ARE strategically distinct under a more aggressive play style (verified: (2,4) is uncapturable along row 4 on the fractal but capturable on torus). The 21-ply cluster-race didn't exercise this, but it's a real ruleset-level asymmetry, not a cosmetic one.

- (b) Mostly correct. The threshold was inherited from R14's torus tuning and not rescaled. With matched threshold scaling, P1 and P2 stones near holes would have ~equal effective contribution and the substrate would look even more decorative. However, the SHAPE of optimal clusters is still constrained — the (1,4) hole forces (1,3)+(1,5) bridging that adds a specific structural pattern.

- (c) Correct for the cluster-build playstyle. An R14 expert transfers immediately because the dominant strategy (place adjacent to own stones, race to threshold) is substrate-blind.

**Substrate-novelty score (Pair B)**: **3/10**. The fractal does change the geometry of optimal placement (forced cluster shapes, fortress cells, influence shadows), but the dominant ruleset (custodian + influence-threshold race) is not exercised in a substrate-distinguishing way. The same R14 winner ruleset on the fractal produces a strategically near-identical game — just on a more visually constrained board.

---

## PHASE 5 — Verdict

```
Team ID: team-9
Pair: B
Fractal candidate: frac_B_fractal
Control candidate: frac_B_control
```

### Fractal scores

- **Strategic Depth**: 5/10 — Cluster-race game with two minor hole-induced wrinkles (fortress cells, forced bridges). No new mechanic emerges.
- **Balance**: 5/10 — P1 wins by exactly 3.38 (one move's worth) at move 21. First-move advantage is real but small. Seat-swap evidence: identical margin in both seats (the seat-2 mirror in game 1 and seat-1 in game 2 both produced the same 3.4 P1 lead).
- **Novelty (post-critic)**: 4/10 — The substrate-induced fortress cells are a genuine new feature, but they're not exploited in cluster-race play.
- **Substrate-novelty**: 3/10 — Holes act as walls (placement, influence, custodian termination). Real but minor under this ruleset.
- **Overall "Would I play this again?"**: 4/10 — Same race-to-threshold outcome as the torus; the fractal aesthetic is more interesting than the play.

### Control scores

- **Strategic Depth**: 5/10 — Same cluster-race game; clean 3×3 cluster build dominates. No surprises.
- **Balance**: 5/10 — Same 3.38 margin; same P1 advantage.
- **Novelty (post-critic)**: 4/10 — Standard influence/threshold ruleset, well-explored from R14.
- **Overall "Would I play this again?"**: 4/10 — Reproducible but unexciting.

### Delta (fractal − control)

- Strategic Depth: **0** (5 − 5)
- Balance: **0** (5 − 5)
- Overall: **0** (4 − 4)

### Critical assessment

- **"The fractal substrate genuinely added strategic depth"**: **N**. Same game, same outcome, same margin, same ply count, same dominant strategy.

- **Phenomena observed only on fractal**:
  - Fortress cells: stones at (2,4)/(6,4)/(4,2)/(4,6) are custodian-immune along the hole-flanked axis (verified mechanically).
  - Forced cluster topology: the (1,4) and (1,1) holes split P1's column-1/2 wall, forcing the order of bridging moves.
  - Influence shadows: cells like (4,2) get neighbor-influence from only 2 sources, so their board-value is highly dependent on a small set of nearby placements.

- **Phenomena observed only on control**:
  - Free cluster-shape choice (no holes constraining the cluster topology).
  - All cells equally capture-vulnerable along all axes (no fortress sanctuaries).
  - Wraparound: a torus 8×8 has no edge effects either, so the cluster can be placed anywhere with full symmetry — different from a 9×9 grid but indistinguishable from the fractal in our actual cluster-race play.

- **Recommendation for R17**: **drop** for the Pair-B ruleset specifically. The custodian + influence + threshold rule family is not stressed by the fractal substrate — captures are rare and the threshold-race dominates. If fractal substrate is integrated into R17 at all, prefer Pair C (surround + connection), where forced detours around holes should genuinely change path-routing strategy. For Pair B, the spike data shows substrate change → ~zero behavioral change. **second-probe** would be acceptable only with: (a) threshold rescaled by mean-cell-degree to remove the artifact in the critic's claim (b), and (b) a ruleset where capture is incentivized so fortress cells matter.

---

### Appendix: full move sequences

**Game 1 (fractal)** — P1 move IDs (9×9 indexing): 20, 38, 56, 19, 28, 29, 47, 55, 46, 21, 11. P2: 60, 42, 24, 61, 52, 51, 33, 25, 34, 59. Final: P1=38.69, P2=35.31, P1 wins move 21.

**Game 2 (control)** — P1 (8×8 indexing): 18, 17, 26, 25, 34, 33, 10, 9, 19, 11, 2. P2: 45, 46, 37, 38, 29, 30, 53, 54, 44, 52. Final: P1=41.71, P2=38.32, P1 wins move 21.
