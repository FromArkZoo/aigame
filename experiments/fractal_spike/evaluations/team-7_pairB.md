# team-7 — Pair B Evaluation (Fractal Spike)

Team ID: team-7
Pair: B
Fractal candidate: `frac_B_fractal` (9×9 Sierpiński carpet, 64 active cells)
Control candidate: `frac_B_control` (8×8 torus)

Shared ruleset: alternating placement on empty cells, custodian (Othello-style) capture at threshold 1, radius-1 influence propagation (strength 1.874, decay 0.402), win at total influence on own cells > 38.616, max 102 turns. Cloned from R14 winner `deb4dfe0382d`. Custodian walks treat fractal holes as walls (per `engine_v2.py:_capture_custodian`).

---

## Phase 1 — Rule Comprehension

The two JSON files are byte-equivalent except `topology_type` (`sierpinski` vs `torus`), `axis_size` (9 vs 8), and metadata. The threshold (38.616) is **unchanged across substrates** despite the average node degree dropping from 4.0 (torus) to 2.75 (fractal — measured: 20 cells deg-2, 40 cells deg-3, 4 cells deg-4). This is the critic's biggest target: a piece on the fractal contributes ~25% less self-influence on average because it has fewer friendly neighbors to amplify, yet the win bar is identical.

Substrate-only degeneracy flags:
- **Influence threshold harder on fractal in expectation** (lower mean degree). Empirically still reachable, but only along the high-degree outer ring; an interior-hugging strategy is dominated.
- **Custodian on fractal is geometrically truncated**: any axis line passing through the central 3×3 (rows 3–5 / cols 3–5) is severed at the hole, halving line lengths in the most contested middle rows/cols.
- **Torus retains wrap-around custodian** in principle (e.g. column-line bracketing across the y=0/y=7 boundary), which the fractal cannot offer.

No game-breaking degeneracy. The threshold is reachable on both substrates.

---

## Phase 2 — Strategic Play

Both games played from P1 perspective primary; seat-swap interpreted as Game 2 prioritising P2's perspective (control), and the buildup mirrored.

### Game 1 — Fractal

P1 strategy: claim the highest-degree corner cell (2,2) (one of only four deg-4 cells), then expand within the upper-left sub-block of the carpet, routing **around** the (1,1) hole. P2 mirrors in the lower-right sub-block.

Key decision points:

- **Move 1 (P1 → (2,2), action 20)**: The four deg-4 cells of the carpet are exactly (2,2),(2,6),(6,2),(6,6) — the centroids of the four corner sub-blocks. On the fractal, fertility is non-uniform: this cell choice is FORCED, not arbitrary. On torus, all 64 cells are equivalent.
- **Move 5 (P1 → (2,1))**: Want to extend along row 1. On torus this would naturally chain (0,1)–(1,1)–(2,1)–(3,1). On the fractal, **(1,1) is a hole** — the row-1 corridor is fragmented at column 1. I had to skip it.
- **Move 9 (P1 → (1,2))**: To reach a cell that adds 2+ friendlies, I had to route via column 2 instead of column 1, because column 1 is fragmented by holes at (1,1) and (1,4). On torus this routing question doesn't exist.
- **Move 11 (P1 → (1,3))**: Continued the "outer ring" L-shape. The natural compact 3×3 fill around (2,2) is impossible on the fractal because (1,1) AND (3,3) are both holes.
- **Move 13 (P1 → (0,3)) and Move 17 (P1 → (3,1))**: Both moves stretch the cluster onto the outer edge of the board to compensate for cells lost inside. This is a substrate-driven shape adaptation: cluster becomes an **L** wrapping around the carpet's top-left sub-block, NOT a 3×3 square.
- **Move 21 (P1 → (3,0))**: P1 hits threshold with **11 pieces in an L-shape**. P2 has 10 pieces and is ~4 influence behind.

Endgame: hit threshold (decisive, not max_turns). Custodian capture **never triggered** the entire game — clusters were segregated to opposite sub-blocks by the central 3×3 hole, so no axis line ever connected an enemy run.

Substrate-only strategy used: **explicit L-shape buildup** dictated by the hole pattern. On torus the same opening would yield a 3×3.

### Game 2 — Control (torus)

P1 plays the same opening intent: cluster around (2,2). On torus, the "natural" compact buildup around the start cell gives a perfect **3×3 cluster** at (1..3, 1..3) by move 17 — exactly the configuration the fractal forbids. P2 mirrors with 3×3 at (4..6, 4..6).

Key decision points:

- **Moves 9, 11, 17 (P1 → (2,1), (1,3), (3,1))**: All three of these cells are on the fractal in the same column/row corridors as their fractal counterparts, but **none of the diagonal-blocking holes exist**, so I just fill the 3×3 in any order.
- **Move 18**: Both clusters are perfect 3×3 squares (9 pieces each, ~34.94 influence). Neither has crossed threshold yet.
- **Move 19 (P1 → (2,4))**: Extend by one cell adjacent to (2,3). Adds 1 friend → +3.381 influence → P1 at ~38.32, just under threshold (38.616).
- **Move 20 (P2 → (4,7))**: Symmetric P2 extension. P2 now ~38.3.
- **Move 21 (P1 → (1,4))**: This cell is adjacent to BOTH (1,3) AND (2,4) — 2 friendly neighbors. The "+2 friend" extension yields +4.888 influence (vs +3.381 for the 1-friend cells). P1 ends at ~43.2 → wins.

Endgame: hit threshold at move 21 with **11 P1 pieces** (3×3 + (2,4) + (1,4)). Custodian also never triggered — same reason: clusters built into opposite quadrants of the torus.

**Identical move-count outcome (21) and identical piece-count to win (11), with different cluster shapes.**

---

## Phase 3 — Strategic Analysis (joint)

| Metric | Fractal | Control |
|---|---|---|
| Move count to win | 21 | 21 |
| Winning player | P1 | P1 |
| Pieces placed by winner | 11 | 11 |
| Cluster shape | L (outer ring + col 0/row 0) | 3×3 + 2 fingers |
| Custodian captures triggered | 0 | 0 |
| Avg own-cell influence per winning piece | ~3.51 | ~3.93 |
| Inter-cluster axis-line interaction | impossible (central hole) | possible but unused |

Where the fractal genuinely changed decisions:

1. **Opening cell choice was forced, not arbitrary.** On torus all 64 cells are equivalent; on fractal, only (2,2)/(2,6)/(6,2)/(6,6) are deg-4, so the fractal pre-commits a player to a sub-block.
2. **Cluster shape adapted to hole pattern.** The fractal cluster wraps around the (1,1) hole in an L, the torus cluster fills a square. This required active substrate awareness — at moves 5, 9, 11, 13 I had to consult the hole map before choosing a cell.
3. **Influence shadows are real but were not exploited.** The central 3×3 hole creates a no-influence corridor; both players just built away from it. The latent strategic phenomenon — using the hole as a wall to deny opponent influence-leakage into your zone — would require asymmetric play (one player invades the other's sub-block) that neither player attempted.
4. **Cross-board distance is doubled.** Graph distance (4,2)↔(4,6) is 8 hops on fractal vs 4 on torus. This means a player who wanted to invade the opposite sub-block would pay a ~2× tempo penalty. Latent but unused.
5. **Custodian was inert on both substrates** in the symmetric corner-builder line we played. Pair B's capture rule did not differentiate the substrates in this evaluation.

P1 dominance on fractal vs control: **identical** — both ended at move 21 with the first-mover hitting threshold ~1 move ahead of the second. Tempo asymmetry from the substrate (e.g. P1 having an easier corner because of asymmetric hole placement) was not observed; the carpet is symmetric under the four-fold rotation that maps sub-block to sub-block.

---

## Phase 4 — Substrate Critic (mandatory)

**Critic's argument:**

(a) The fractal is "8×8 grid with 17 dead cells inserted in a pretty pattern." The strategic concept on offer — *build a compact cluster, reach influence threshold* — is identical. Players don't think about the carpet's self-similarity; they think "this cell is blocked, route around it." That is the same cognitive operation as "this cell is occupied by an opponent stone." The Sierpiński structure adds zero game-theoretic content — only board art.

(b) The threshold (38.616) is **kept constant** despite the cell-degree drop from 4.0→2.75. So the fractal is just a "harder threshold game" — players need 1–2 extra pieces on the outer ring to compensate for the lower mutual-influence density. This is not a new strategic concept; it is a numerical scaling artefact. If the spike author had scaled the threshold by 2.75/4.0 = 0.69 to match expected influence density, the fractal game would play out almost identically to the torus, removing any apparent depth.

(c) **Transfer test:** an expert in the rectangular control transfers immediately to the fractal. They learn one new sub-rule ("cells (1,1),(4,1),...,(7,7) and the central 3×3 are walls") in under 30 seconds, then play the same opening (claim a deg-4 cell), build a cluster around it, hit threshold. They do not need to learn a new strategic concept. **My own play in Phase 2 confirms this**: I used the same opening, the same buildup, the same victory condition, with only minor tactical re-routing around blocked cells. Expert transfer is essentially instant.

**Conclusion (critic):** The fractal substrate is **decoration**. Substrate-novelty score: 2/10.

---

**Player rebuttals (focused, post-Phase-2):**

- **The forced-fertility-sites observation is real.** On torus, opening cell choice is genuinely arbitrary (translation-symmetric), so there is no "opening theory." On the fractal, only 4 of 64 cells are deg-4, and they're spaced exactly two sub-blocks apart. This pre-commits both players to building in sub-block centres, which **eliminates a degree of freedom** that the torus has. I'd argue this is not "decoration" — it's a topological fact that constrains the game's opening tree.
- **Cluster-shape adaptation IS a new tactical layer**, even if the strategic objective is unchanged. On fractal, choosing between an L-shape and a corridor extension required reasoning about cell-degree-after-occupation, which never came up on torus. The depth is small but non-zero.
- **Influence shadows were latent but not theoretical.** Had we played a more aggressive variant where one player invaded the opponent's sub-block, the central 3×3 hole would force a long detour — the 8-hop distance vs 4-hop on torus is a hard fact, not a vibe. We did not exploit it because Pair B's ruleset (custodian + threshold + symmetric corner builds) doesn't reward invasion.
- **The threshold-scaling critique (b) lands hardest.** If the spike author had renormalised threshold against degree, the fractal game would indeed look like the torus game. As shipped, the substrate-novelty observed is partially driven by "harder game" rather than "differently shaped game."

**Net substrate-novelty score (post-rebuttal): 4/10.** The carpet introduces real but minor structural constraints (forced opening cells, shape adaptation, doubled cross-board distance) that the torus lacks, but the strategic concepts remain those of the rectangular game. Pair B's specific ruleset (custodian + threshold + radius-1 influence) does not exercise the substrate's unique features (it never forces axis-line crossings of holes, never forces cross-board connection, never punishes lower mutual degree decisively).

---

## Phase 5 — Verdict

Team ID: team-7
Pair: B
Fractal candidate: `frac_B_fractal`
Control candidate: `frac_B_control`

### SCORES

**Fractal:**
- Strategic Depth: **5** — same cluster-builder strategy as control with a minor shape constraint; custodian inactive (clusters segregated by central hole); influence shadows latent but unused.
- Balance: **4** — P1 won by exactly 1 tempo (move 21). Symmetric corner-build is too dominant; second-mover cannot catch up without aggressive interference, and Pair B's rules don't reward interference. Seat-swap evidence: identical 21-move outcome on both substrates suggests P1 advantage is rule-driven, not substrate-driven.
- Novelty (post-critic): **3** — R14 clone (already evaluated), substrate adds modest tactical re-routing only.
- Substrate-novelty: **4** — forced fertility sites, cluster-shape adaptation, doubled cross-board distance — all present but weakly exercised by this ruleset.
- Overall "Would I play again?": **4** — symmetric corner-builder is mechanical; the carpet is interesting to look at but doesn't sing under this rule set.

**Control:**
- Strategic Depth: **5** — same cluster-builder, slightly cleaner.
- Balance: **4** — same P1 +1 tempo dominance.
- Novelty (post-critic): **3** — direct R14 clone with substrate-only renaming.
- Overall: **4**.

### DELTA (fractal − control)

- Strategic Depth: **0**
- Balance: **0**
- Overall: **0**

### CRITICAL ASSESSMENT

- **"The fractal substrate genuinely added strategic depth": N (with qualifications).** It added structural constraints but not strategic concepts. The 21-move winner-and-piece-count outcome is identical on both substrates.
- **Phenomena observed only on fractal:**
  - Forced opening at one of the four deg-4 cells (no translation symmetry to break)
  - L-shaped cluster around the (1,1) hole (vs torus's 3×3 square)
  - Latent influence shadow across the central 3×3 hole (8-hop detour, not exploited)
  - Custodian walks truncated at hole boundaries (never triggered → unobserved)
  - Lower mean degree (2.75 vs 4.0) → ~25% less mutual amplification per piece, partially compensated by outer-ring extension
- **Phenomena observed only on control:**
  - Toroidal axis-line wrap-around for custodian (not triggered → latent)
  - Translation-symmetric opening (any cell equivalent — no opening theory)
  - Compact 3×3 cluster as the natural buildup shape
- **Recommendation for R17: SECOND-PROBE.** Pair B's symmetric corner-builder line never stressed the substrate's unique features — custodian was inert, no cross-hole invasion, no boundary interaction. Before integrating, re-test with a ruleset that *forces* cross-board interaction (e.g. capture-driven aggression, larger influence radius that bridges the central hole, or connection-style win condition). If the substrate features remain inert under more interactive rulesets, **drop**. As measured here, the carpet is functionally equivalent to "8×8 with a slightly higher threshold," and the cleaner choice for R17 is to integrate the carpet only paired with rulesets that reward path-routing or boundary play (i.e. Pair C's territory) rather than pure threshold-density rulesets like Pair B.
