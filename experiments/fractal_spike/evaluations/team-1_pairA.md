# Team-1 Verdict — Pair A (Fractal vs Control)

Team ID: team-1
Pair: A
Fractal candidate: frac_A_fractal (9×9 Sierpiński carpet, 64 active cells, 17 holes)
Control candidate: frac_A_control (8×8 torus, 64 cells)
Shared rules: alt + place + outnumber-2 + influence (r=1, s=0.932, d=0.510) + threshold-22.65 + max_turns=100
Source: clone of R16 winner c6bb58075520

---

## Phase 1 — Rule Comprehension

The two candidates are byte-identical apart from `topology_type` (sierpinski vs torus) and `axis_size` (9 vs 8). Players alternate placements on empty cells; placing adjacent to an enemy with ≥2 of the placer's stones around it removes the enemy (outnumber-2). Each placement spreads influence at strength 0.932 to its own cell and 0.475 (=0.932·0.510) to each neighbor; first player to reach total influence > 22.65 on cells they own wins, otherwise majority-pieces at turn 100.

**Substrate-only degeneracy flags**

* **Fractal cell-degree distribution (verified empirically):** 20 cells of degree 2, 40 of degree 3, only 4 of degree 4. Compare torus: every cell is degree 4. Outnumber-2 capture has the same numerator threshold (=2) on both substrates, but the fractal denominator is far smaller — 20 cells become "2-of-2 sandwich traps" where occupying both neighbour slots auto-captures any future enemy stone placed there.
* **Per-stone influence is ~14% lower on fractal** (measured 1.96 effective/stone vs 2.23 on torus in matched mirror games — see Phase 2). Same threshold value 22.65 therefore takes ~2 extra stones (≈4 extra plies) on the fractal. Threshold remains reachable — no degeneracy — but the games run longer.
* **Hole-shadow defensive corridors:** cells like (4,2), (4,6), (2,4), (6,4) sit one move away from the central 3×3 hole. The hole acts as a one-sided wall — those cells cannot be attacked from the central-block side because no enemy stone can ever sit there. This creates a small but real asymmetric defensive bonus that has no analog on torus.

No degeneracy makes either game unplayable.

---

## Phase 2 — Strategic Play

### Game F (Fractal, P1 first)

I played a mirror-cluster race, prioritising degree-3+ cells and using the column-2 / column-6 corridors that flank the central hole (so each cluster gets one side guaranteed safe). Move log (engine-verified, every move):

| Ply | Player | Action | Cell | Notes |
|----:|:------:|:------:|:-----|:------|
| 1 | P1 | 20 | (2,2) | degree-4 anchor (one of only 4 on the board) |
| 2 | P2 | 60 | (6,6) | mirror, also a degree-4 anchor |
| 3 | P1 | 24 | (6,2) | second degree-4 anchor, top-right |
| 4 | P2 | 56 | (2,6) | mirror |
| 5 | P1 | 11 | (2,1) | extend left column, hole at (1,1) shields one side |
| 6 | P2 | 69 | (6,7) | mirror |
| 7 | P1 | 15 | (6,1) | extend right column |
| 8 | P2 | 53 | (8,5) | start fallback cluster (axis (2,5) was blocked by routing) |
| 9 | P1 | 2 | (2,0) | top of column 2 |
| 10 | P2 | 72 | (0,8) | corner anchor |
| 11 | P1 | 6 | (6,0) | top of column 6 |
| 12 | P2 | 78 | (6,8) | bottom anchor |
| 13 | P1 | 29 | (2,3) | extend column 2 down — hole at (3,3) prevents east attack |
| 14 | P2 | 51 | (6,5) | extend P2 cluster |
| 15 | P1 | 33 | (6,3) | extend column 6 down — hole at (5,3) shields east |
| 16 | P2 | 47 | (2,5) | extend |
| 17 | P1 | 28 | (1,3) | bridge into row 3 |
| 18 | P2 | 73 | (1,8) | extend |
| 19 | P1 | 19 | (1,2) | tighten cluster |
| 20 | P2 | 65 | (2,7) | extend |
| 21 | P1 | 21 | (3,2) | high-value bridge, owns hole-shielded triple |
| 22 | P2 | 59 | (5,6) | extend |
| 23 | P1 | 12 | (3,1) | clinch — P1 effective rises to 22.59, just below threshold |
| 24 | P2 | 68 | (5,7) | last gasp |
| 25 | P1 | 3 | (3,0) | **P1 wins, 25.43 vs 19.74**, threshold crossed |

Endgame reached the stated threshold win condition — no double-pass, no max_turns. P1 stones=13, P2 stones=12. No captures occurred during the game; clusters were spaced so neither side had a 2-of-2 sandwich opportunity that didn't cost more tempo than it gained.

**Substrate-specific decisions noted in play:**

* Move 13/15 (P1 plays (2,3) and (6,3)) — these placements were chosen *because* the central hole at (3,3)/(5,3) blocks east-side attack. On torus those rows would have been equally exposed on both sides, so I would have spread instead of tightening.
* Move 21 (P1 plays (3,2)) — (3,2) has degree 3 on fractal (loses (3,3) hole). Knowing only 3 cells matter for outnumber resistance, the move is safer than it looks: P2 cannot capture (3,2) without owning both (2,2) and (3,1), but I already own (2,2) so the capture is impossible by occupation alone.
* I deliberately avoided degree-2 sandwich cells like (2,4), (4,2), (4,6), (6,4) for non-anchor stones — placing there gives an enemy a 1-stone capture setup against you.

### Game C (Control / Torus, seats swapped — P2 plays "my" race strategy this time)

I separated the two clusters by torus-half so wraparound wouldn't merge them prematurely.

| Ply | Player | Action | Cell | Notes |
|----:|:------:|:------:|:-----|:------|
| 1 | P1 | 0 | (0,0) | corner anchor |
| 2 | P2 | 28 | (4,3) | far-side anchor |
| 3 | P1 | 8 | (0,1) | extend |
| 4 | P2 | 36 | (4,4) | extend |
| 5 | P1 | 1 | (1,0) | tighten 2x2 |
| 6 | P2 | 29 | (5,3) | extend |
| 7 | P1 | 9 | (1,1) | full 2x2 P1 cluster |
| 8 | P2 | 37 | (5,4) | full 2x2 P2 cluster |
| 9 | P1 | 16 | (0,2) | extend down |
| 10 | P2 | 44 | (4,5) | extend |
| 11 | P1 | 17 | (1,2) | extend |
| 12 | P2 | 45 | (5,5) | extend |
| 13 | P1 | 24 | (0,3) | extend |
| 14 | P2 | 52 | (4,6) | extend |
| 15 | P1 | 25 | (1,3) | tighten |
| 16 | P2 | 53 | (5,6) | tighten |
| 17 | P1 | 2 | (2,0) | extend top |
| 18 | P2 | 30 | (6,3) | extend right |
| 19 | P1 | 10 | (2,1) | tighten |
| 20 | P2 | 38 | (6,4) | tighten |
| 21 | P1 | 18 | (2,2) | **P1 wins, 24.51 vs 21.68**, threshold crossed |

Endgame reached threshold. P1 stones=11, P2 stones=10. No captures triggered — the two clusters never approached each other, and torus wraparound was not exploited because each side was already winning the race in its own half.

**Substrate-specific observation:** I noticed that on torus, the corner cell (0,0) has neighbours (7,0), (1,0), (0,7), (0,1) — four neighbours, every cell is degree-4 — so the corner is just as strong as the centre. On fractal the same logical position would have been degree-2 with only two neighbours, and would have been the worst possible anchor instead of one of the best.

---

## Phase 3 — Strategic Analysis

**Did the fractal play differently?** Modestly. Concrete differences:

1. **Anchor selection.** On fractal there are exactly 4 degree-4 cells: (2,2), (6,2), (2,6), (6,6). I opened on two of them. On torus, every cell is degree-4 — opening anywhere is equivalent.
2. **Defensive hugging.** On fractal I preferred cells one step from the central hole, gaining a free defensive flank. There is no torus analog.
3. **Tempo / game length.** Fractal game took 25 plies, torus took 21 plies. Fractal needed ~13 stones to threshold vs ~11 on torus. Same threshold value, different effective difficulty.
4. **Per-stone efficiency**: fractal 1.96/stone, torus 2.23/stone (14% lower on fractal). This is the threshold-rescaling artifact the Substrate Critic will weaponise.

**Choke points / districts.** Fractal cell (4,2) sits in a one-cell corridor between two holes; capturing it requires only 2 stones (at (3,2) and (5,2)). It's a literal forced corridor. Torus has no equivalent.

**Influence shadows.** Influence does not propagate across holes (the engine uses BFS over active cells via `cells_within_radius`). Stones placed against the central block have their influence cleanly truncated on the hole side, which means clusters near the centre are slightly *less* efficient than clusters far from holes. Combined with the 14% per-stone efficiency hit, this nudges play toward edge clusters on fractal — opposite of the torus where centre vs edge is symmetric.

**First-mover advantage.** Both games: P1 won by crossing threshold first, by a margin of one ply. Consistent with R16 winner c6bb58075520's known imbalance. The fractal does not fix it; the substrate is orthogonal to first-mover dynamics in a pure race game.

**Capture verification (engine-tested side-line).** I ran a separate sequence to verify outnumber-2 capture works on fractal: P1@22, P2@21, P1@23, P2@14, P1@24 (defends), P2@20, P1@12 — placing at (3,1) triggers capture of P2's (3,2), because (3,2) on the fractal has only 3 neighbours (the (3,3) hole removes one) and 2 of them are now P1. Captures function identically to torus arithmetically, but fractal cells with fewer neighbours have proportionally less "headroom" to stay safe.

---

## Phase 4 — Substrate Critic (rebuttal)

**Critic argues:**

(a) The fractal is just "8×8 grid with extra dead cells". Every move I made could be reframed as a torus move with some squares marked off-limits.

(b) The threshold (22.65) was kept constant despite the fractal's lower per-stone efficiency — so the apparent depth is just "the same race, made longer by a 14% nerf." Rescale the threshold to ~19.6 and the fractal game is structurally identical to control.

(c) An expert torus-Pair-A player transfers immediately. The opening principle (occupy degree-4 anchors → tile outward) is identical. The only learnable patch is "don't place on degree-2 cells unless you must." That's a footnote, not a new game.

**Player rebuttals:**

* **Hole-shadow corridors are not degenerate dead cells — they are *terrain*.** My moves at (2,3) and (6,3) were chosen specifically because the (3,3)/(5,3) hole shields the east face. That's a positional asymmetry that exists nowhere on the torus, and it is worth choosing different opening cells for. (Strength of rebuttal: moderate — the effect *exists*, but it's a small bonus, not a new mechanic.)
* **Degree-2 trap cells genuinely change move-vetting.** On torus I never have to ask "is this cell capturable on a 1-stone setup?" On fractal I do. That's a fresh tactical question, even if the underlying rule is unchanged. (Strength: weak — it's a tactical filter, not a strategic concept.)
* **Routing matters more on fractal.** Maximum graph distance is 16 on fractal vs 8 on torus. Battles localize because reinforcements take longer to arrive. Torus is global; fractal is regional. (Strength: real but modest in *this* ruleset, which doesn't reward long-range coordination — Pair C with connection wins would magnify this.)

**Substrate-novelty score:** 4/10. The substrate adds a tactical filter (avoid degree-2 traps) and a small positional bonus (hole shadows). It does not introduce a new strategic concept that an expert torus player would have to learn from scratch. An expert transfers ~85% of their skill immediately and patches the rest in 5 games.

---

## Phase 5 — Verdict

### Fractal (frac_A_fractal)
* **Strategic Depth: 5/10** — race-to-threshold dominates; degree-2 traps and hole-shadow corridors add real but minor positional texture above pure torus play.
* **Balance: 4/10** — pure first-mover race; P1 won by ~5.7 effective points, no seat-swap evidence the fractal corrects the underlying R16 winner's known imbalance.
* **Novelty (post-critic): 4/10** — outnumber+influence+threshold is the R16 winner family; substrate change isn't a new mechanic.
* **Substrate-novelty: 4/10** — genuine but small (hole-wall defensive bonus, degree-2 trap cells, regional vs global geometry). Most torus skills transfer.
* **Overall ("would I play this again?"): 4/10**

### Control (frac_A_control)
* **Strategic Depth: 5/10** — same family; uniform degree-4 board, slightly faster, marginally less interesting positionally.
* **Balance: 4/10** — same P1 first-mover advantage (P1 24.51 vs P2 21.68).
* **Novelty (post-critic): 4/10** — known torus + influence threshold game.
* **Overall: 4/10**

### Delta (fractal − control)
* Strategic Depth: **0**
* Balance: **0**
* Overall: **0**

### Critical Assessment

* "The fractal substrate genuinely added strategic depth" — **N** (only marginally; novel terrain effects exist but don't change the dominant strategy).
* **Phenomena observed only on fractal:**
  * Hole-shadow defensive corridors (column 2 / column 6 cluster invulnerable from central side).
  * Degree-2 sandwich cells acting as 1-stone capture traps for any stone placed there.
  * Anchor-cell scarcity (only 4 degree-4 cells vs 64 on torus) — opening principles are sharper.
  * Longer games (25 vs 21 plies, 13 vs 11 stones to threshold) due to ~14% lower per-stone influence efficiency.
* **Phenomena observed only on control (things the substrate took away):**
  * Toroidal wraparound — corner-to-corner threats and globally-reaching influence (not exploited in this game but available).
  * Symmetric anchor selection — every cell equally good, no opening theory needed.
  * Faster, denser games (might play more tournament rounds in same time).
* **Recommendation for R17: drop** for this ruleset; **second-probe** as a substrate option in the next generation only if Pair B (custodian, where capture-walks may genuinely interact with hole geometry) or Pair C (connection wins, where forced central-block routing creates real tempo asymmetry) shows substrate-novelty ≥6. The Pair-A rule family is a pure influence-threshold race, and the fractal's hole geometry doesn't engage with that mechanic deeply enough to justify the added board complexity, the threshold-rescaling artifact, and the +4 plies of game length.
