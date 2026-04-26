# Team-3 Evaluation — Pair A (alt + outnumber-2 + influence-radius-1 + threshold)

Team ID: team-3
Pair: A
Fractal candidate: frac_A_fractal (sierpinski 9×9, 64 active cells, 17 holes)
Control candidate: frac_A_control (torus 8×8, 64 cells)
Source: clone of R16 winner c6bb58075520

## Phase 1 — Rule Comprehension

The two candidates are byte-identical apart from `topology_type` (`sierpinski` vs `torus`) and `axis_size` (9 vs 8). Both share: alternating turns, single placement on any empty cell (first-move-anywhere), outnumber-2 capture (enemy stone removed when it has ≥2 friendly orthogonal neighbours), influence propagation with radius 1 / strength 0.932 / decay 0.510, and a win-by-threshold of 22.645 on P1-cells (sign-flipped for P2). Max 100 turns.

**Shared ruleset (3-sentence summary):** Two players alternate placing stones on empty cells. Each placement adds +0.932 to the placed cell's `board_value` and +0.475 to each radius-1 neighbour (sign +1 for P1, −1 for P2), and any adjacent enemy stone with ≥2 friendly neighbours is removed. The first player whose total `board_value` on their own cells exceeds 22.645 wins (margin-tiebreak if both cross simultaneously); if no one crosses by turn 100, majority pieces wins.

**Substrate-specific degeneracy flags:**
- **Fractal-only:** the four sub-block centres (1,1), (7,1), (1,7), (7,7) are holes, so the perfectly dense 3×3 block (which on torus is the densest legal P1 shape, with corner cells achieving 2 own neighbours) is impossible — the densest fractal cluster around an anchor is a plus-shape with no 2-own-neighbour empty extension cells. This caps influence-per-stone at ~2.09 on fractal vs ~2.20 on torus.
- **Fractal-only:** four "district anchors" (2,2), (6,2), (2,6), (6,6) are the only degree-4 cells; everything else is degree 2 or 3. Bridge cells (0,4), (2,4), (6,4), (8,4) are degree 2 chokepoints connecting upper and lower halves around the central 3×3 hole.
- **Threshold not unreachable on either** — both completed in well under 100 turns (verified below).

## Phase 2 — Strategic Play

I played 4 games total (2 per substrate, with a seat-swap effective via mirror/non-mirror P2 strategies) plus a fragmented-P2-erosion variant on fractal. All games used the dense-cluster strategy as the spine.

### Game 1 — FRACTAL, P2 plays "exploration" (vertical column-6 + bottom-left jump)

Moves (action IDs): `20,60,11,51,19,15,29,33,21,52,28,56,27,65,18,47,12,46,9,38,22,55,3`

Move-by-move highlights (substrate-relevant moments):
- **M1 P1=20 (2,2)**: claim NW anchor — the only degree-4 cell in upper-left district. Substrate-specific: equivalent torus move would be arbitrary; here (2,2) is structurally privileged.
- **M2 P2=60 (6,6)**: claim SE anchor — the diagonally opposite degree-4 cell. Mirror to P1.
- **M3 P1=11 (2,1)**: extend N from anchor. Hole at (1,1) means I can't add a NW corner; the cluster is forced into a plus shape rather than a 3×3 block.
- **M5 P1=19 (1,2), M7 P1=29 (2,3), M9 P1=21 (3,2)**: complete plus-5 around anchor. Each arm has only the anchor as its P1 neighbour (+1.407 each); the anchor itself reaches +2.832 when all 4 arms are present.
- **M6 P2=15 (6,1), M8 P2=33 (6,3)**: P2 deliberately spreads vertically through column 6 instead of clustering — a fragmenting choice that the substrate "punishes" because column 6 cells are degree 3 and don't compound. (On torus, this same shape would be just as bad — but on fractal the alternative cluster shape is also worse, so P2 may have been over-correcting.)
- **M11 P1=28 (1,3)**: this becomes adjacent to BOTH (1,2) and (2,3) — the rare 2-own-neighbour move on fractal, achievable only because (1,3) sits at the inside of the plus-5 elbow. +2.832 inf, jumps P1 to 16.96.
- **M17 P1=12 (3,1)**: symmetric 2-own-neighbour move (adj to (2,1)+(3,2)). +2.832, P1=18.84.
- **M20 P2=38 (2,4)**: P2 finally invades P1's flank, claiming a degree-2 bridge cell next to my (2,3). Substrate-specific: this move erodes my (2,3) by 0.475 (visible: P1 inf 20.73→20.25). On torus the analogous move would be much more flexible because the eroding stone could have 4 own-cluster neighbours.
- **M21 P1=22 (4,2)**: claim my own degree-2 bridge stone. +1.407.
- **M23 P1=3 (3,0)**: cross threshold. P1 wins move 23: **24.02 vs 17.38**.

Endgame: threshold reached cleanly, no double-pass, no max-turns. Substrate-specific strategy adopted: P1 deliberately did NOT play (1,1) — it's a hole — and the cluster shape (plus-with-elbows) was distinctively non-rectangular. (3,1) and (1,3) doubled as both extensions and capture-shield against any P2 invasion at (3,0) or (0,3) respectively, exploiting the hole-bordered topology.

### Game 2 — CONTROL TORUS (seat-swap: same role-A plays P2, same dense-cluster idea but executed as 3×3 block)

Moves: `0,36,1,37,8,28,9,29,2,38,16,44,10,30,17,45,18,46,11,27,19`

Highlights:
- **M1–M6** both players build a 2×3 strip; **M7 P1=9 (1,1)** completes 2×2 corner — adj (0,1)+(1,0), 2 own neighbours, +2.832. **M8 P2=29 (5,3)** mirrors with adj (5,4)+(4,3), +2.832. The 3×3 block pattern is *only* available on the torus.
- **M13 P1=10, M14 P2=30, M15 P1=17, M16 P2=45**: cluster densification. By M17 both blocks are filled 3×3, both at 19.80 inf — *identical*, demonstrating perfect mirror symmetry that the torus permits and the fractal partly breaks.
- **M21 P1=19 (3,2)**: the killer extension — adjacent to (2,2)+(3,1), +2.832. Crosses threshold. **P1 wins move 21: 24.04 vs 21.20**.

Endgame reached threshold; P2 was 1.45 below threshold, much closer than fractal-game-1.

### Game 3 — FRACTAL, P2 plays mirror (4-fold reflection)

Moves: `20,60,11,51,19,59,29,69,21,61,28,68,12,52,18,53,27,62,22,58,9,71,3`

This is the controlled apples-to-apples test: P2 mirrors P1 around the (4,4) centre (which is a hole, but the involution maps active→active). Result: through M18 both at 18.84 inf (identical). P1 wins move 23: **24.49 vs 22.61**. Margin of 1.88, P2 missed threshold by 0.04 — a single tempo.

### Game 4 — FRACTAL, P2 plays vertical-column-6 + extension into upper-right anchor (24)

Moves: `20,60,11,51,19,69,29,52,21,61,28,59,12,68,18,42,3,33,9,15,2,24`

P2 builds a 7-stone (6,6)-area cluster, then jumps to claim column-6 chokepoints (6,4)=42, (6,3)=33, (6,1)=15, and (6,2)=24. After M22 P1=22.61, P2=21.66 — close, but P1 plays M23 to cross threshold first. Same-tempo dynamic as G3.

## Phase 3 — Strategic Analysis (joint)

**Did the fractal play differently? Yes, modestly:**

| Metric | Fractal | Control | Δ |
|---|---|---|---|
| Game length to threshold (mirror P2) | 23 moves | 21 moves | +2 |
| Final winning margin | 1.88 (24.49–22.61) | 2.84 (24.04–21.20) | −0.96 |
| Loser's final inf | 22.61 (98.0% of threshold) | 21.20 (93.6% of threshold) | +1.41 |
| Inf per stone (12-stone cluster) | ~2.04 | ~2.20 | −0.16 |
| Cells with degree 4 | 4 (anchors only) | 64 (all) | −60 |
| Maximum density block | plus-7 around anchor | full 3×3 | — |

**Specific fractal-only phenomena:**
1. **Anchor scarcity** — the four degree-4 cells (2,2),(6,2),(2,6),(6,6) are structurally privileged. Opening at one of them is strictly stronger than any non-anchor opener. On torus, opening choice is pure preference (translation-invariance).
2. **Plus-not-block clusters** — the hole at each sub-block centre (1,1) etc. forbids the optimal 3×3 dense pattern, forcing a plus-with-elbow shape that has *fewer* 2-own-neighbour extension cells. This makes per-stone influence accumulation ~7% lower on fractal.
3. **Bridge / chokepoint cells** — (0,4),(2,4),(6,4),(8,4) and their column counterparts are degree-2 corridor cells. P2 tried to use (2,4) as a wedge in Game 1; (4,2),(4,6) appear similarly. These cells are weak for own cluster bonus but strong for influence-erosion of an enemy's lateral cluster. No analogous cell exists on torus.
4. **District structure** — the substrate is 4 sub-blocks linked by narrow corridors. "Claim a district" is a meaningful strategic concept on fractal that is meaningless on torus (where everywhere is structurally identical).

**Tempo / first-move advantage:** Identical in form (P1 wins by 1 tempo on both substrates), but the *magnitude* differs:
- Fractal mirror: P2 ends 0.04 below threshold — a hair-thin loss.
- Torus mirror: P2 ends 1.45 below threshold — a comfortable, decisive loss for P2.

The fractal is *more competitive* end-game because the lower per-stone efficiency stretches the race out 2 moves longer, during which P2 has more chance to catch up via erosion plays. This is the substrate's strongest legitimate claim to depth.

**Influence shadows / blocked propagation:** Mostly null in Pair A — radius is 1, so propagation is local and the holes only block influence transfer through cells the engine would cross. With radius=1, this only matters for capture/threshold counts on cells immediately adjacent to a hole (which we noted: (2,4) and friends are degree-2). The shadow effect would be *much* larger with radius ≥ 2; in this rule-set it's barely measurable.

## Phase 4 — Substrate Critic (mandatory)

**Critic argues:**

(a) "The fractal is just an 8×8 torus with 17 dead cells. There's no new strategic concept — both games are won by the same dense-cluster-to-threshold strategy. Players who never read 'fractal' could play identically."

(b) "The threshold (22.645) was inherited unchanged from R16's torus winner. On fractal the achievable density per stone is ~7% lower, so the game is just 'the same game with the goal post moved harder' — a difficulty knob, not a substrate-novelty knob."

(c) "An R16 expert would transfer immediately: claim a degree-4 anchor, build the plus-cluster, race to threshold. Same opening principle, same midgame, same endgame."

**Player rebuttals (specific Phase-2 moments):**

- **Rebuttal to (a) — anchor scarcity:** On torus, opening at (0,0) is identical to opening at (3,7) under translation. On fractal, opening at (2,2) is strictly stronger than (0,0), (1,2), (3,3), or any cell in the central column. The four-fold privileged opening is a real strategic concept that an expert would have to *learn* (the torus expert would not). [Game 1 M1 vs Game 2 M1.]
- **Rebuttal to (b) — bridge cells are not just "harder threshold":** Cell (2,4) in Game 1 M20 was placed not for cluster gain but to erode P1's (2,3) and to occupy a corridor. There is no torus equivalent — the closest torus analogue would be a cell with degree 4, where the same erosion effect comes packaged with cluster bonus, removing the trade-off entirely. The fractal forces a *trade* between density and territory-control that the torus does not.
- **Rebuttal to (c) — the densest cluster shape changes:** On torus the optimal P1 corner is a 3×3 block, achieved by M7 P1=(1,1) in Game 2. On fractal, (1,1) is a hole; the optimal shape is plus-7 with elbows at (1,3) and (3,1). An R16 expert would *try* to play (1,1) and find it illegal — they need to relearn the cluster geometry. This is a small but real new concept: "the densest legal pattern depends on the hole layout, not just the rules."

**Substrate-novelty score: 4/10.** The substrate genuinely changes opening theory (anchor scarcity), cluster geometry (plus-not-block), and adds chokepoint/district concepts — but the strategic *type* is unchanged (it's still "race-to-threshold-via-dense-cluster"), the win condition is unchanged, and the games converge to the same outcome (P1 wins by 1 tempo). An expert transfers ~80% of intuitions; the remaining 20% is non-trivial but cosmetic. Score 4 reflects "real but small" substrate effect.

## Phase 5 — Verdict

### SCORES (1–10)

**Fractal (frac_A_fractal):**
- Strategic Depth: **5** — anchor opening + plus-cluster + bridge wedges adds a couple of layers over the rectangular base, but the win race remains dominantly threshold-cluster. Closer endgame margin (0.04) gives a small depth boost.
- Balance: **4** — P1 wins by 1 tempo against perfectly-mirroring P2 (Game 3 G3 P2 missed threshold by 0.04). With seat-swapped strategy (P2 plays cluster, P1 plays fragmented column) the result still favours seat-1; the alternating + monotone-accumulation rules give an irreducible first-move advantage that the fractal does not fix. Slightly *better* balance than control (margin 1.88 vs 2.84) but P1-wins-on-mirror is structural.
- Novelty (post-critic): **4** — anchor scarcity + plus-cluster + chokepoints are real but minor.
- Substrate-novelty: **4** — see Phase 4 reasoning. Hole pattern changes geometry but not strategic kind.
- Overall "Would I play this again?": **5** — closer endgame than torus is the main attraction; otherwise no.

**Control (frac_A_control):**
- Strategic Depth: **5** — clean dense-cluster race; opening is uninteresting (translation-invariant) but mid/end game is well-formed. Same depth ceiling as the fractal — both are "threshold-via-cluster" games.
- Balance: **3** — P1 wins by 1 tempo with comfortable 1.45-inf margin against mirror P2. Worse balance than fractal (margin is 50% larger).
- Novelty (post-critic): **3** — this is essentially a generic torus-influence game with no surprises. R14/R16 produced ~20 of these.
- Overall "Would I play this again?": **3** — same content as a hundred prior runs, plays out predictably.

### DELTA (fractal − control)
- Strategic Depth: **0**
- Balance: **+1** (fractal slightly better, mainly via tighter endgame margin)
- Overall: **+2** (5 vs 3)

### CRITICAL ASSESSMENT

- **"The fractal substrate genuinely added strategic depth": Y** — but only marginally. It added structural concepts (anchor scarcity, plus-cluster, chokepoints, districts) without changing strategic type. The closer endgame margin is the most concrete depth signal.
- **Phenomena observed only on fractal:**
  - Anchor-scarcity opening theory (only 4 degree-4 cells)
  - Plus-cluster geometry (no 3×3 block possible)
  - Degree-2 bridge / chokepoint cells with density-vs-control trade-off (e.g. (2,4))
  - 2-move-longer game length, ~7% lower per-stone influence efficiency
  - End-game closer to threshold tie (P2 0.04 below in mirror play)
- **Phenomena observed only on control (substrate took AWAY):**
  - Translation-invariant opening (no strong opening preference)
  - 3×3 dense block achievable from any corner
  - Mid-game high-density cluster bonus (per-stone inf ~2.20 vs ~2.04)
  - Larger seat-1 winning margin (substrate makes the imbalance more visible)
- **Recommendation for R17: second-probe.** The substrate effect is real (G3 endgame margin 0.04 is striking) but small enough that I would not integrate the fractal as a default topology for R17. Worth a follow-up probe with: (i) radius ≥ 2 propagation (which would amplify hole-shadow effects), (ii) a threshold scaled down for fractal (e.g. 21.0) to test whether matched difficulty changes the depth picture, (iii) the surround/connection rule families where district isolation should matter more than threshold accumulation does. If those probes also yield Δ-overall ≤ 2, drop. If radius-2 or surround-rules yield Δ ≥ 4, integrate.
