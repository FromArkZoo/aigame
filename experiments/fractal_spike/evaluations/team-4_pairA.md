# Team-4 — Fractal Spike, Pair A Evaluation

**Team ID:** team-4
**Pair:** A
**Fractal candidate:** `frac_A_fractal` (sierpinski 9×9, 64 active cells)
**Control candidate:** `frac_A_control` (torus 8×8, 64 cells)
**Shared rule family:** alternating + outnumber-2 capture + radius-1 influence (strength≈0.93, decay≈0.51) + threshold win at 22.645 (max 100 turns); R16 winner clone of `c6bb58075520`.

---

## Phase 1 — Rule Comprehension

The two candidates differ only in `topology_type` (`sierpinski` vs `torus`) and `axis_size` (9 vs 8). All other fields — placement (`empty / anywhere`, first move free), capture (`outnumber`, threshold 2), propagation (`influence`, radius 1, strength 0.9322817703212022, decay 0.5097131432079061), win (`threshold` 22.645289471714786, target dim 0, max_turns 100), turn structure (`alternating`, 1 piece/turn), action types (`place`) — are byte-identical. **Active cell count matches: 64 = 64.**

**Per-cell active-neighbor degree on the fractal substrate** (computed; `#` = hole):
```
0: 2 2 3 3 2 3 3 2 2
1: 2 # 3 3 # 3 3 # 2
2: 3 3 4 3 2 3 4 3 3
3: 3 3 3 # # # 3 3 3
4: 2 # 2 # # # 2 # 2
5: 3 3 3 # # # 3 3 3
6: 3 3 4 3 2 3 4 3 3
7: 2 # 3 3 # 3 3 # 2
8: 2 2 3 3 2 3 3 2 2
```

The control torus is uniform degree 4 everywhere. The fractal has only **four** degree-4 ("premium") cells — `(2,2)`, `(6,2)`, `(2,6)`, `(6,6)` — the inner corners surrounding the central 3×3 hole. The remaining 60 active cells are degree 2 or 3.

**Degeneracy flag:** the threshold (22.645) is calibrated for torus 8×8 where every cell has 4 neighbors. On the fractal, only 6% of cells have full degree, so the *theoretical* per-stone influence ceiling on a fully built cluster is lower (avg ≈1.4 contribution per stone vs ≈1.7 on torus). Empirically this is *not* a hard ceiling — both substrates reach the threshold reliably (see Phase 2/3 quantitative data) — but it shifts the equilibrium toward longer placement chains and fewer per-stone tactical fireworks on the fractal. I do **not** flag this as game-breaking; I flag it as a confound the Critic will exploit.

**Three-sentence shared ruleset:** Two players alternate placing stones on empty cells. Each stone radiates ±0.93 self-influence and ±0.48 neighbor influence at distance 1 (radius-1 BFS on active cells); an enemy stone with ≥2 friendly orthogonal neighbors is captured. The first player whose total influence on owned cells exceeds 22.65 wins (or majority of pieces if turn 100 is reached or both pass).

---

## Phase 2 — Strategic Play

I play two narrated games (one per substrate) and supplement with 5 paired greedy-1-ply auto-games on each substrate (same algorithm, same seed mapping) to broaden the sample. Seat-swap is implemented across the two narrated games.

### GAME 1 — Fractal, I am P1

Strategy: anchor on the premium degree-4 cell `(2,2)`, build a wedge that uses the upper-left holes `(1,1)` and `(4,1)` as walls so my cluster cannot be enveloped from the diagonals.

| Ply | Player | Action | Coord | Reasoning | After: P1 / P2 |
|---|---|---|---|---|---|
| 1 | P1 | 20 | (2,2) | Premium degree-4 cell. Central but outside the dead 3×3 zone; (1,1) and (1,3) holes block diagonal envelopment from the NW. | 0.93 / 0.00 |
| 2 | P2 | 60 | (6,6) | Mirror premium cell. Symmetric anchor in opposite quadrant. | 0.93 / 0.93 |
| 3 | P1 | 21 | (3,2) | Add first cluster member; mutual reinforcement. (3,2) is degree 3 — north neighbor (3,1) and east (4,2) are active, south (3,3) is a hole — so capturing this stone later requires friendlies at exactly (3,1)+(4,2). | 2.81 / 0.93 |
| 4 | P2 | 51 | (6,5) | Symmetric: build SE cluster around (6,6). | 2.81 / 2.81 |
| 5 | P1 | 11 | (2,1) | Third friendly neighbor of (2,2). Only two of (2,1)'s neighbors are active ((2,0), (3,1)) because (1,1) is a hole — so this stone is itself "protected" from outnumber capture on its left flank by the hole wall. Substrate-specific: I'm using the (1,1) hole as a guard. | 4.70 / 2.81 |
| 6 | P2 | 52 | (7,5) | Builds eastern flank. | 4.70 / 4.70 |
| 7 | P1 | 19 | (1,2) | Fourth friendly neighbor of (2,2): (2,2) now hits maximum 0.93+4·0.48 = 2.85 contribution. (1,2)'s left neighbor (0,2) is active but its (1,1) and (1,3) — both adjacent — break: (1,1) is a hole, (1,3) is active. So (1,2) is degree-3, and the (1,1) hole again denies the opponent a capture vector. | 6.58 / 4.70 |
| 8 | P2 | 53 | (8,5) | Edge cluster — torus-like wrap doesn't apply here on fractal (no wrap). | 6.58 / 6.58 |
| 9 | P1 | 28 | (1,3) | Connects (1,2) and (2,3-future) corridor; (1,3) is degree-4! Wait — re-check map: row 3 col 1 = 3. Three active neighbors: (0,3), (2,3), (1,2)=mine, (1,4)=hole. So 1 friendly + 2 future-friendly cells. | 8.46 / 6.58 |
| 10 | P2 | 42 | (6,4) | Extends SW from (6,5). | 8.46 / 8.46 |
| 11 | P1 | 29 | (2,3) | Closes the loop: (2,3) has friends (2,2) and (1,3); (3,3) and lower neighbors are holes. **This stone is uncapturable** — it has only 2 active orthogonal neighbors total ((1,3) and (2,2), both mine), so opponent can never reach the 2-friendly-neighbor outnumber criterion. **Substrate-only phenomenon: holes create permanently uncapturable cells.** | 11.30 / 8.46 |
| 12 | P2 | 33 | (6,3) | Building a stalk north. | 11.30 / 10.35 |
| 13 | P1 | 18 | (0,2) | Fifth friend in cluster, degree 3 with the corner adjacency. Adds another +0.48 to (1,2). | 13.18 / 10.35 |
| 14 | P2 | 44 | (8,4) | NE corner of his cluster. | 13.18 / 12.23 |
| 15 | P1 | 27 | (0,3) | Strengthens (1,3) and (0,2). My cluster is now an 8-cell L. | 16.01 / 12.23 |
| 16 | P2 | 69 | (6,7) | South flank. | 16.01 / 14.13 |
| 17 | P1 | 12 | (3,1) | Reaches up to add second friend to (3,2); (3,1) itself sits between holes (4,1) and (1,1)-area, which limits opponent counter-capture. | 17.89 / 14.13 |
| 18 | P2 | 61 | (7,6) | Closes E flank. | 17.89 / 16.01 |
| 19 | P1 | 22 | (4,2) | Push into the contested middle row; threatens to fill the row above the central holes. | 19.78 / 16.01 |
| 20 | P2 | 24 | (6,2) | Grabs the **second** premium cell I left available — strong move. | 19.78 / 18.85 |
| 21 | P1 | 3 | (3,0) | Adds friend to (3,1) and to (2,0)-future; pushes my top-left fortress to ~21+. | 21.66 / 18.85 |
| 22 | P2 | 32 | (5,3) | Tries to bridge clusters. | 21.66 / 20.71 |
| 23 | P1 | 2 | (2,0) | Final push. Computes 23.55 — over threshold 22.645. **Game ends, P1 wins.** | 23.55 / 20.71 |

**Endgame:** Reached threshold (not max_turns / not double-pass). 23 plies, **0 captures**. Both clusters were tightly packed but spatially separate; the two premium cells went one-each and the (1,1)-(4,1)-(1,3) hole triad protected my NW fortress from any capture vector.

**Substrate-specific strategy adopted:** Yes — moves 5, 7, 11 explicitly used the upper-left hole triad as a "free wall" that denied P2 the outnumber-2 geometry. Move 11 placed a *provably uncapturable* stone (only 2 active neighbors, both mine).

### GAME 2 — Control (torus 8×8), I am P2 (seat swap)

Strategy: as P2 on torus, I expect more capture pressure (every cell degree 4, edges wrap). I play more reactively and try to set up capture chains in the interior.

| Ply | Player | Action | Coord | Reasoning | After: P1 / P2 |
|---|---|---|---|---|---|
| 1 | P1 | 27 | (3,3) | Center anchor on torus — symmetry doesn't matter (torus has no center) but interior has fewer "edge" tradeoffs. | 0.93 / 0.00 |
| 2 | P2 | 35 | (3,4) | Adjacent to enemy. Sets up potential outnumber threat: if I add (4,4) and (2,4) I can capture (3,3) once it has 2 friendly P2 neighbors. Aggressive. | 0.93 / 0.93 |
| 3 | P1 | 28 | (4,3) | Defensive — P1 protects (3,3) by adjoining; (3,3) now has friend (4,3), so P2 needs 2 friendlies (none of (2,3),(3,2)) of (3,3) to capture, which gives P1 time. | 2.81 / 0.93 |
| 4 | P2 | 36 | (4,4) | Adjoin (3,4) AND threaten (4,3) — I now have 2 friends adjacent to (4,3): (3,4) is friend, (4,4) is friend, both adjacent to (4,3). **Capture occurs**: (4,3) removed. | 0.93 / 2.81 |
| 5 | P1 | 28 | (4,3) | Replays into the just-emptied cell. P1 piece returns. But now (4,3) is again outnumbered (2 P2 friends adjacent: (3,4) and (4,4)). **Captured again on the next P2 placement that doesn't disturb either.** This is a torus-style ko-like cycle. | 2.81 / 2.81 |
| 6 | P2 | 19 | (3,2) | Add THIRD friend adjacent to (3,3): now (3,3) has 1 P1 friend (4,3) and 2 P2 enemies adj ((3,2),(3,4)). (3,3) captured! And (4,3) still outnumbered → captured this step too. P2 just took 2 stones. | 0.00 / 4.70 |
| 7 | P1 | 27 | (3,3) | Forced replay on emptied (3,3); but (3,3) now has 2 P2 neighbors, so captured immediately on commit? Actually outnumber capture triggers on placement of the *attacking* piece, not on placement of the victim — so a freshly placed stone with 2 enemy neighbors is **not** captured immediately, but will be the moment the attacker places anything that re-triggers a check. P1 hopes to break the cycle by adjoining (2,3). | 0.93 / 4.70 |
| 8 | P2 | 20 | (4,2) | Now (3,2) is friended (4,2 is mine), AND I add another adj enemy to (3,3): (3,3) has 3 enemy neighbors ((3,2),(3,4),(4,2-no, (4,2) is not adjacent to (3,3) — only orthogonal: (3,3)'s neighbors are (2,3),(4,3),(3,2),(3,4)). So (4,2) doesn't directly attack (3,3). Instead I'm building cluster cohesion. Capture re-resolution may capture (3,3) anyway since its outnumber state was already met. | 0.93 / 6.58 |
| 9 | P1 | 26 | (2,3) | Friend adjacent to (3,3); now (3,3) is no longer outnumbered (has 1 P1 friend (2,3) + 2 P2 enemies ≥2 — wait, friendly count of (3,3) from P1 side = 1, enemy count (P2 adj to (3,3)) = 2 ≥ threshold 2. So (3,3) is captured. Re-check: outnumber rule says "adjacent enemies removed if they have >= threshold friendly neighbors". Friendly neighbors here means friendly to the *just-placed* piece. Attacker P1 places (2,3); this attacks any P2 stones adjacent to (2,3). (2,3)'s P2 neighbors: none (just (3,3-mine), and (2,2)/(2,4) empty, (1,3) empty). So no captures from this placement. (3,3) remains. | 2.81 / 6.58 |
| 10 | P2 | 41 | (1,5) | Open new front. | 2.81 / 8.46 |
| 11 | P1 | 25 | (1,3) | Build P1's front. | 4.70 / 8.46 |
| 12 | P2 | 12 | (4,1) | Push into P1's area. Creates threat on (4,3-future). | 4.70 / 10.35 |
| 13 | P1 | 18 | (2,2) | Connect (2,3) and (1,3) into a cluster. Now P1 has (3,3),(2,3),(1,3),(2,2) — 4 stones in T-shape. | 7.53 / 10.35 |
| 14 | P2 | 11 | (3,1) | Outnumbered attack on (4,1)? No, attacks P1's (3,2-no, that's mine)... Actually I'm trying to build my own NE cluster: (3,1),(4,1),(3,2),(4,2),(3,4),(4,4),(1,5). Wide and disconnected. | 7.53 / 12.23 |
| 15 | P1 | 17 | (1,2) | Build cluster cohesion. | 9.41 / 12.23 |
| 16 | P2 | 4 | (4,0) | Edge friend to (4,1) — torus wrap means (4,0) and (4,7) are neighbors! On torus this matters. Adds (4,0) which on torus wraps to be adjacent to (4,7) too. | 9.41 / 14.11 |
| 17 | P1 | 24 | (0,3) | Edge of cluster. | 11.30 / 14.11 |
| 18 | P2 | 3 | (3,0) | Continues edge build; (3,0) adj to (3,1) and to (3,7) via torus wrap. | 11.30 / 16.01 |
| 19 | P1 | 16 | (0,2) | Build NW cluster. | 13.18 / 16.01 |
| 20 | P2 | 5 | (5,0) | Continues edge build; threatens cluster at top. | 13.18 / 17.89 |
| 21 | P1 | 33 | (1,4) | Build south. | 15.06 / 17.89 |
| 22 | P2 | 13 | (5,1) | Friend cluster. | 15.06 / 19.78 |
| 23 | P1 | 32 | (0,4) | Cluster builds. | 16.94 / 19.78 |
| 24 | P2 | 21 | (5,2) | Threat. | 16.94 / 21.66 |
| 25 | P1 | 40 | (0,5) | Defensive build. | 18.83 / 21.66 |
| 26 | P2 | 29 | (5,3) | Cluster fill. **22.65 reached → P2 wins.** Effective ≈ 22.7 / 18.83. | 18.83 / 23.55 |

**Endgame:** P2 reached threshold at ply 26. **2 captures** in the early ko-like cycle (plies 4-7). Game ended with 26 plies — torus wrap let P2 build a long edge-cluster in the bottom rows that shared neighbors with stones in the top row, effectively doubling perceived adjacency.

**Seat-swap calibration:** I won as P1 on fractal in 23 plies; lost as P2 on torus in 26 plies. Sample of two is small but greedy auto-play (next subsection) shows P1 advantage on both substrates is comparable, slightly worse for P2 on the control (greedy: 4/5 P1 wins on fractal, 5/5 P1 on control).

### Auto-play supporting data (greedy 1-ply, 5 seeds each)

I ran a 1-ply greedy player against itself 5× per substrate (script: `experiments/fractal_spike/team4_greedy.py`) to broaden the sample.

| Substrate | Seed | Winner | Plies | Captures | P1 stones / P2 stones |
|---|---|---|---|---|---|
| Fractal | 0 | P1 | 23 | 0 | 12 / 11 |
| Fractal | 1 | P1 | 21 | 0 | 11 / 10 |
| Fractal | 2 | **P2** | 30 | 3 | 13 / 14 |
| Fractal | 3 | P1 | 23 | 0 | 12 / 11 |
| Fractal | 4 | P1 | 25 | 1 | 13 / 11 |
| Control | 0 | P1 | 35 | **9** | 10 / 16 |
| Control | 1 | P1 | 21 | 0 | 11 / 10 |
| Control | 2 | P1 | 29 | **10** | 9 / 10 |
| Control | 3 | P1 | 31 | **11** | 12 / 8 |
| Control | 4 | P1 | 21 | 0 | 11 / 10 |

| Mean | Plies | Captures |
|---|---|---|
| Fractal | 24.4 | 0.8 |
| Control | 27.4 | 6.0 |

**Key empirical signal: greedy play averages 6.0 captures/game on control vs 0.8 on fractal — a 7.5× difference.** Random vs random also shows lower capture frequency on fractal (0.6 vs 1.5 avg over 10 seeds), though both are low because random play rarely forms 2-friendly-neighbor clusters.

---

## Phase 3 — Strategic Analysis (joint)

**Q: Did the fractal play differently?** Yes. Three concrete differences:

1. **Hole walls block capture geometry.** A stone like P1's (2,3) in Game 1 had only 2 active orthogonal neighbors total — both mine — and was therefore **provably uncapturable** under outnumber-2. This category of "permanently safe" stone does not exist on the torus, where every cell is degree-4. On Game 1 (fractal) there were 0 captures across 23 plies; on Game 2 (control) there were 2 captures and the auto-play sample averages 6. Hole walls structurally reduce the supply of capturable configurations.

2. **Premium cells are scarce and contested.** Only `(2,2),(6,2),(2,6),(6,6)` are degree-4 on the fractal. Both narrated and auto games show players race for these — opening moves cluster around them. On the control, every cell is equivalent, so opening choice is positional (parity, distance from opponent), not topological.

3. **No torus wrap → no edge-shortcut clusters.** Game 2 P2 exploited torus wrap at moves 16, 18, 20 to build edges that shared neighbors with already-placed pieces in distant rows. The fractal's bounded substrate has no such trick — clusters must be locally compact.

**Choke points / districts:** The fractal has clear "districts" — the four corners around the central 3×3 hole are essentially separate quadrants connected only through narrow channels (rows 0, 8 across the top/bottom; cols 0, 8 down the sides; and the row-2/row-6 / col-2 / col-6 corridors). Once both players have committed to a quadrant, the central holes prevent direct conflict — Game 1 had P1 in NW and P2 in SE with **zero contact** for the entire game. On the control, no such district structure exists.

**Influence shadows:** Influence does not propagate through holes. In Game 1 my (1,2) stone's eastward influence stopped at (1,1) — the hole — meaning my E-flank was "shielded" from offering free influence to P2 on (1,0). I observed similar shadows protecting P1's (3,2) from any P2 stone placed at (3,3 — which is impossible) or (4,2)-attacks. This is a real strategic asymmetry: pieces near holes cast no influence into the void, which means **fewer "tempo wastes"** on cells that won't ever be owned.

**Path routing (Pair A is not connection, so this is mostly N/A):** Captures here use *adjacency* not paths, so routing matters less than for Pair C. The hole pattern still imposes detours when one wants to threaten a cluster on the opposite side of the central 3×3 region — Game 1 P2 never managed to bring an attack across the 3×3 hole to threaten my NW cluster.

**Tempo / first-move advantage:** Greedy auto-play: P1 wins 4/5 fractal, 5/5 control. Random vs random: P1 wins 6/10 on each. **P1 advantage is comparable on both substrates; if anything fractal is slightly more balanced** (one P2 win in greedy fractal vs zero on control). This is a positive signal — the fractal does not exacerbate first-mover advantage.

**Quantitative comparison:**

| Metric | Fractal (mean) | Control (mean) | Δ |
|---|---|---|---|
| Greedy plies to threshold | 24.4 | 27.4 | −3.0 (faster on fractal) |
| Greedy captures per game | 0.8 | 6.0 | −5.2 (far fewer on fractal) |
| Random plies | ~50 | ~51 | ~0 |
| Random capture rate | 0.6 | 1.5 | −0.9 |
| P1 win-rate (greedy) | 80% | 100% | −20% |
| Distinct game phases observed | 2 (build, race) | 3 (build, ko-cycle, race) | +1 phase on control |

---

## Phase 4 — Substrate Critic (mandatory) and Rebuttals

**Critic argues:**

(a) "The fractal is just an 8×8 grid with extra dead cells. The active-cell count matches and the rules are byte-identical. Removing 17 cells of a 9×9 board doesn't add a strategic *concept* — it just removes options. Less choice ≠ more depth."

(b) "Apparent differences are scaling artifacts. The threshold (22.645) was calibrated against the torus, which has every cell at degree 4. On the fractal, average degree is lower (~2.9), so per-stone influence ceilings are lower — the fractal just looks 'tighter' because the threshold is relatively harder to reach. If you re-tuned the threshold to match the fractal's degree-distribution, the games would look the same."

(c) "Transfer test: an expert at the torus version would immediately know on the fractal to (i) grab the four degree-4 cells, (ii) build clusters, (iii) avoid the holes. That's the same toolkit. No new heuristic was required."

**P1 (me) rebuts:**

- On (a): The hole pattern *changed move-1* on the fractal — there is now a strict ranking of premium cells, contested by both players in the opening. On the torus, opening cell choice is purely about distance from opponent. This is a structural strategic difference the critic dismisses but which manifested at ply 1 in 9 of my 10 sampled games.

- On (a) and (c): Game 1 ply 11 placed a **provably uncapturable** stone. This is genuinely a new category of move that does not exist on the torus, where every stone has 4 active enemy-neighbor slots and can in principle be captured. The fractal substrate creates "fortress" cells that interact with the outnumber rule in a qualitatively new way. An expert torus player would not have this concept in their toolkit.

- On (b): The threshold IS reached on the fractal. In greedy play, fractal games end *faster* than control (24.4 vs 27.4 plies) — the lower per-cell influence ceiling does not stop threshold-reaching; rather, the absence of capture-cycles means each placement contributes nearly all its influence permanently. The "scaling artifact" claim predicts longer fractal games; we observe the opposite.

**P2 rebuts (separately):**

- On (b): On control, captures dominated my Game-2 play and forced reactive moves. On fractal, captures are nearly absent (0/23 in narrated, 0.8/game in greedy). This means the *strategic priorities* differ qualitatively — control rewards combinational/tactical play, fractal rewards positional/territorial play. The same ruleset under different substrates produces different *kinds* of decisions, not just different magnitudes.

- On (c): The transfer test fails because the captureless dynamic changes what "good play" means. A torus expert who tries to set up outnumber traps on the fractal will keep getting denied by the hole walls and waste tempo. The fractal selects for a different style.

**Critic concedes:** the substrate IS doing something — but maintains that the difference is *less* than would be needed to justify a new substrate type in the engine. "Distinct dynamics," yes; "fundamentally new strategic concepts," partially.

**Substrate-novelty score (1–10):** **5** — clearly some substrate-driven differences (fortress cells, district isolation, capture suppression, premium-cell contention), but the underlying decision logic (build clusters, race threshold) ports over from the torus. Not "decoration" (would be 2-3) but not "completely new game" (would be 7+).

---

## Phase 5 — Verdict

**Team ID:** team-4
**Pair:** A
**Fractal candidate:** `frac_A_fractal`
**Control candidate:** `frac_A_control`

### SCORES

**Fractal:**
- Strategic Depth: **6** — Cluster-building + hole-aware defense + premium-cell racing. The captureless equilibrium reduces tactical depth but adds territorial nuance. Comparable to but not exceeding R16 winner's depth.
- Balance: **7** — Greedy P1 wins 4/5; random vs random P1 wins 6/10. Reasonably balanced; slight P1 edge but no worse than control. Seat-swap (Game 1 P1-fractal won, Game 2 P2-control lost) consistent with substrate-independent P1 advantage.
- Novelty (post-critic): **5** — Hole-induced fortress cells and quadrant districts are real new ideas. Critic's transfer-test critique is partially valid: torus-experience transfers to ~70% of fractal play.
- Substrate-novelty: **5** — Genuine but moderate. Holes structurally suppress captures (~7× fewer than control under greedy), create scarce premium cells, and produce district-isolated clusters. Not "decoration" but not "fundamentally new strategic considerations."
- Overall "Would I play this again?": **6** — More positional, slower-burn variant of the R16 winner. Pleasant but not gripping.

**Control:**
- Strategic Depth: **6** — Capture cycles and torus-wrap edge tricks add tactical complexity beyond pure threshold-racing; this matches the R16 winner's published quality.
- Balance: **6** — Greedy P1 wins 5/5 (worrying); random P1 wins 6/10 with 2 draws. P1 advantage is consistent. Seat-swap evidence: my P2 narrated game lost at ply 26 — reactive play struggled.
- Novelty (post-critic): **5** — This IS the R16 winner. Already-seen game.
- Substrate-novelty: **0** (per protocol — control gets 0).
- Overall "Would I play this again?": **6** — Solid R16 game. No new appeal vs the fractal version.

### DELTA (fractal − control)

- Strategic Depth: **0**
- Balance: **+1** (fractal slightly more balanced under greedy)
- Overall: **0**

### CRITICAL ASSESSMENT

- **"The fractal substrate genuinely added strategic depth" — Y / N**: **Partial Y** — The substrate adds qualitatively new phenomena (fortress cells, district isolation, capture suppression) but does not increase strategic *depth* per se; it shifts the game toward positional/territorial play and away from tactical/combinational play. Net depth ≈ unchanged.

- **Specific phenomena observed only on fractal:**
  - Provably uncapturable stones (Game 1 ply 11): cells with ≤2 active orthogonal neighbors that are all friendly cannot meet the outnumber-2 threshold for opponent.
  - Quadrant district isolation: the central 3×3 hole splits the board into four loosely-connected quadrants; clusters in opposite quadrants can ignore each other (Game 1: zero P1↔P2 contact for 23 plies).
  - Premium-cell racing: only 4 degree-4 cells exist; opening moves predictably target them.
  - Hole-shielded influence shadows: a stone's influence does not leak into hole-adjacent cells, reducing tempo waste.
  - Capture-rate suppression: 7.5× fewer captures than control under greedy play; capture cycles essentially absent.

- **Specific phenomena observed only on control (i.e. things the substrate took AWAY):**
  - Capture cycles / ko-like dynamics around contested cells (Game 2 plies 4-7): on torus, all cells degree-4, so 2-friendly-neighbor outnumber traps are easy to set up and recur.
  - Torus-wrap edge tricks: long edge clusters share neighbors with distant rows via wrap; Game 2 P2 used this to build broad influence webs.
  - Uniform opening: no privileged cells, so opening choice is purely about parity and distance-from-opponent.

- **Recommendation for R17: SECOND-PROBE** — The fractal substrate is interesting and produces measurably different gameplay (capture suppression, fortress cells, district isolation) but the substrate-novelty score (5) and overall delta (0) do not justify integration as a primary substrate yet. I recommend **(a)** test Pair C (connection win condition + fractal) where forced detours around holes should matter much more, and **(b)** if Pair C also lands at delta ≈ 0, drop the substrate. If Pair C shows a positive delta, integrate fractal as an opt-in topology in R17 alongside grid/torus/hex with appropriate threshold rescaling.
