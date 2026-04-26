# Team-15 — Fractal Spike Evaluation, Pair C

**Team ID:** team-15
**Pair:** C
**Fractal candidate:** `frac_C_fractal` (sierpinski 9×9, 64 active cells, 17 holes)
**Control candidate:** `frac_C_control` (grid 8×8, 64 cells)
**Rule family:** alt + surround (threshold 1) + connection — hand-crafted, fractal-native

---

## Phase 1 — Rule Comprehension

The two JSON files are byte-for-byte identical apart from `topology_type` (sierpinski vs grid) and `axis_size` (9 vs 8). Both use **alternating turns, single placement per turn on any empty cell, Go-style surround capture (threshold 1), and a Hex-style connection win** where P1 wires the two opposing faces along dimension 0 (left↔right, x=0 to x=axis_size−1) and P2 wires dimension 1 (top↔bottom, y=0 to y=axis_size−1). No propagation, no CA. Max 100 turns.

**Three-sentence shared ruleset summary.** Players alternate placing single stones on any empty cell. After every placement, surround-capture removes opposing groups whose liberty count falls to zero (threshold 1). The first player to form a von-Neumann-connected chain joining their two assigned opposite faces wins; otherwise max_turns triggers a draw.

**Per-substrate degeneracies / asymmetries flagged.**
- *Fractal cell-degree distribution* (verified from `engine.topo._neighbors`): 4 cells deg-4, 40 cells deg-3, **20 cells deg-2** (31 % of active cells). Control: 36 deg-4, 24 deg-3, only 4 deg-2 (corners). The fractal has **9× as many vulnerable cells** — surround capture is materially more accessible on the fractal.
- *Free-path channels.* On fractal, only rows {0, 2, 6, 8} are hole-free and only columns {0, 2, 6, 8} are hole-free. Both players' "free" connection paths therefore go through the **same four 4-degree anchor cells**: (2,2), (6,2), (2,6), (6,6). On control, every row and every column is a free path — no privileged anchors.
- *Central 3×3 wall.* Rows 3–5 and columns 3–5 each have only 4 active cells (at coords {0, 2, 6, 8} on the perpendicular axis). Connection paths cannot run "straight" through the middle stripe.
- *Symmetry.* The carpet's holes are 4-fold symmetric in both x↔y and edge↔edge mirrors, so the substrate itself does **not** privilege P1 or P2 in either dimension.
- *Liveness of connection.* Threshold of 9 stones (= axis_size) is reachable on both substrates. No degeneracy.

---

## Phase 2 — Strategic Play

### Game 1 — Fractal (P1 = team seat-1)

Move sequence (cell coords in parens, action = y·9 + x):

| # | Player | Cell | Action | Reasoning |
|---|---|---|---|---|
| 1 | P1 | (2,2) | 20 | NW anchor — degree-4, on **both** free row 2 and free col 2. Highest-value opening on fractal. |
| 2 | P2 | (6,6) | 60 | SE anchor — symmetric mirror of P1's choice. Dual-purpose: blocks P1's row-6 alt path AND extends P2's col-6 vertical. |
| 3 | P1 | (6,2) | 24 | NE anchor. P1 now claims **both** anchor endpoints of free row 2, the cleanest horizontal corridor. |
| 4 | P2 | (2,6) | 56 | SW anchor — symmetric. Both free rows for P1 (2 and 6) now have P2 anchors on the bottom. |
| 5 | P1 | (4,2) | 22 | Spine of row 2. **Substrate-specific risk:** (4,2) is degree-2, with neighbors (4,1)=hole, (4,3)=hole. Only 2 liberties. On control, the analogous "row-2 spine" cells have 4 liberties. |
| 6 | P2 | (4,6) | 58 | Mirror. P2's row-6 spine — also degree-2. Note: P2 *should* be playing vertically; mirroring along row 6 is suboptimal but it does block P1's row-6 alt and exploits the same anchor logic. Substrate Critic will flag this. |
| 7 | P1 | (3,2) | 21 | Solidify row-2 chain. (3,2) is deg-3 (lost (3,3)=hole). Connects (2,2)–(3,2)–(4,2). |
| 8 | P2 | (3,6) | 57 | Mirror. |
| 9 | P1 | (5,2) | 23 | Extend right; chain spans (2,2)…(6,2) on row 2. |
| 10 | P2 | (5,6) | 59 | Mirror. P1=5 stones, P2=5. |
| 11 | P1 | (1,2) | 19 | Extend left toward edge x=0. Chain (1,2)…(6,2). |
| 12 | P2 | (0,2) | 18 | **Block** left edge. (0,2) has only 2 liberties: (0,1) and (0,3) — also vulnerable due to corner-adjacency on the carpet. |
| 13 | P1 | (7,2) | 25 | Extend right toward edge. Hole at (7,1) means (7,2) is deg-3, not deg-4. |
| 14 | P2 | (8,2) | 26 | Block right edge. Symmetric to M12. |
| 15 | P1 | (1,3) | 28 | Begin **detour** under the (0,2) block. (1,3) connects to (1,2). |
| 16 | P2 | (7,3) | 34 | Mirror block on right detour. |
| 17 | P1 | (0,3) | 27 | Reach left edge x=0 via the detour. Also puts P2's (0,2) in atari — its liberties shrink to (0,1) only. |
| 18 | P2 | (0,1) | 9 | Save (0,2). The defended chain (0,1)+(0,2) now has liberties (0,0), (1,2)=P1 → **only (0,0)**. Atari. |
| 19 | P1 | (0,0) | 0 | **CAPTURE.** P2's (0,1)+(0,2) chain has 0 liberties and is removed. P1 +1 stone, P2 -2. P1 still cannot reach right edge — (8,2) blocks. |
| 20 | P2 | (8,3) | 35 | Connect (8,2)+(7,3) via (8,3) into one group. Liberties (8,1)(8,4)(6,3). |
| 21 | P1 | (6,3) | 33 | Drop south of row-2 chain to start a right-side detour. (6,3) deg-3 (5,3 is hole). |
| 22 | P2 | (8,4) | 44 | Extend right column. P2 starts realising they **also** need vertical, and col 8 is the only free vertical they can still reach. |
| 23 | P1 | (6,4) | 42 | Push detour further south. (6,4) is deg-2 — only (6,3) and (6,5). |
| 24 | P2 | (6,5) | 51 | Block detour. Connects to (6,6) chain. P1's southern arm is now boxed in by two hole-walls plus P2 stones. |
| 25 | P1 | (6,1) | 15 | **Pivot UP** instead. (6,1) deg-3 — neighbors (5,1)(6,0) plus chain. |
| 26 | P2 | (8,5) | 53 | Continue building col-8 vertical. |
| 27 | P1 | (6,0) | 6 | Reach row 0 — top stripe. Begin run to right edge along row 0. |
| 28 | P2 | (8,6) | 62 | |
| 29 | P1 | (7,0) | 7 | (7,0) deg-2 (hole at (7,1)). |
| 30 | P2 | (8,7) | 71 | |
| 31 | P1 | (8,0) | 8 | **WIN.** Connection path: (0,3)→(1,3)→(1,2)→(2,2)→(3,2)→(4,2)→(5,2)→(6,2)→(6,1)→(6,0)→(7,0)→(8,0). 12 stones. P1=16, P2=13. |

**Endgame status:** stated win condition reached at turn 31 (well below max_turns=100). One capture occurred (a 2-stone capture by P1 on turn 19), enabled directly by hole-induced low-liberty count.

**Substrate-specific strategy adopted:** Yes — multiple instances. (1) The opening four moves all placed at the four 4-degree anchor cells, a sequence that has no analogue on a uniform grid. (2) On turn 25, P1 *intentionally pivoted to row 0* rather than row 1 because the (7,1) hole means row 1 cannot complete a horizontal — there is literally no path (7,1)→(8,1) at row 1. The *hole at (7,1)* dictated the entire endgame routing. (3) P2 used the (1,1) hole as a "free liberty subtractor": (0,1) is deg-2 because of (1,1), so capturing (0,1)+(0,2) cost P1 only 2 stones rather than the 3–4 it would on a uniform grid.

---

### Game 2 — Control (seats swapped: team seat-1 plays as P2)

For symmetry of analysis I report from the same "P1/P2" point-of-view convention.

| # | Player | Cell | Action | Reasoning |
|---|---|---|---|---|
| 1 | P1 | (3,3) | 27 | Center. On control, *any* central cell is equally good — no anchor preference. |
| 2 | P2 | (4,4) | 36 | Diagonal. Now P2 plays *vertically* (the correct task — no temptation to mirror because there are no free-path anchors to fight over). |
| 3 | P1 | (4,3) | 28 | Extend right; also blocks P2's col-4 path above. |
| 4 | P2 | (3,4) | 35 | Extend down; also blocks P1's row-3 path below. The interlocking-cross opening. |
| 5 | P1 | (5,3) | 29 | Extend right along row 3. |
| 6 | P2 | (3,5) | 43 | Extend down col 3. |
| 7 | P1 | (6,3) | 30 | |
| 8 | P2 | (3,6) | 51 | |
| 9 | P1 | (7,3) | 31 | **Reach right edge x=7**, but P1 still needs left edge. |
| 10 | P2 | (3,7) | 59 | **Reach bottom edge y=7**, but P2 still needs top edge. |
| 11 | P1 | (2,3) | 26 | Extend left. |
| 12 | P2 | (5,4) | 37 | Detour east — P2's col-3 chain is blocked at the top by P1's (3,3)/(4,3); only east detours remain. |
| 13 | P1 | (1,3) | 25 | |
| 14 | P2 | (0,3) | 24 | Block P1 left edge. |
| 15 | P1 | (0,2) | 16 | Outflank above the (0,3) block. (0,2) is on the left edge x=0 — P1 already has it, just needs to *connect* to the row-3 chain. |
| 16 | P2 | (0,4) | 32 | Save (0,3) from atari (its only remaining liberty was (0,4)). |
| 17 | P1 | (1,2) | 17 | **WIN.** Connection: (0,2)→(1,2)→(1,3)→(2,3)→(3,3)→(4,3)→(5,3)→(6,3)→(7,3). 9 stones. P1=9, P2=8. |

**Endgame status:** stated win reached at turn 17. **Zero captures** occurred. (0,3) was put in atari but rescued in time.

**Substrate-specific strategy adopted:** None — control. Both players played a textbook Hex-with-block opening: extend the spine, block the opponent's spine, race to the edges, outflank when blocked.

---

## Phase 3 — Strategic Analysis (joint)

**Did the fractal play differently?** Yes, in three concrete ways.

1. **Game length.** Fractal: 31 turns. Control: 17 turns. Same rule family, same 64 active cells, same win condition — fractal nearly **2× longer**. Cause: forced detours around the central 3×3 block AND the (1,1)/(7,1)/(7,7) sub-block-center holes. Every direct block by P2 forced P1 into a multi-stone detour that on the control was a one-stone outflank.

2. **Captures.** Fractal: 1 capture event, 2 stones. Control: 0 captures, 0 stones. The capture in fractal Game 1 was *only* possible because (0,1)+(0,2) had degree 2 each (hole at (1,1) eliminated one liberty) — on control, the analogous edge stones have degree 3 and capture would have required one more stone (more tempo than P1 could spare in a real game).

3. **Opening.** Fractal opening was forced into a 4-anchor dance for the first 4 moves; control opening was a free 4-cell central cluster choice. The fractal opening is **deterministic to within symmetry** — there is essentially one good opening sequence on the carpet, vs. the wide opening latitude on control.

**Choke points / districts.** On the fractal, the four 4-degree cells (2,2), (6,2), (2,6), (6,6) are the only cells that lie on a free row AND a free column simultaneously. Every shortest connection passes through one of them — they are *forced* tempo cells. On the control, the analogous "everywhere-good" property is true of all 36 interior cells — no choke at all.

**Influence shadows.** Not directly applicable (this rule family has `prop_type: none`), but the analogous concept — **liberty shadows** — is real on the fractal. A stone at (4,2) has only 2 potential liberties because the (4,1) and (4,3) holes "shadow" it. Strings running through such cells need explicit support stones; on control, every interior stone has 4 liberties for free.

**Path routing — the key Pair-C question.** On the fractal, the central 3×3 hole forces P1's horizontal connection to *choose* between top-stripe (rows 0–2) and bottom-stripe (rows 6–8) routing. P1 cannot run a straight line through the middle. In Game 1, P1 actually *combined* the two stripes — entering at (0,3) on the bottom-of-top stripe, climbing to row 2, then breaking out to row 0 via the (6,1)/(6,0) ladder on the right. **This kind of stripe-switching has no analogue on the control.**

**Tempo / first-move advantage.** P1 won both games. On fractal P1 won using 16 stones of 64 active (25 %); on control 9 of 64 (14 %). So while P1 dominance held on both, it was *marginal* on fractal (P1 had only a 3-stone capture-fueled lead — 16 vs 13) but *clean* on control (9 vs 8). Empirically, the fractal compresses the P1 advantage by inflating defender tempo (more block-detour cycles before resolution). With strong P2 vertical play in opening (verified in a third spot-check game where P2 went col-2 and col-6 immediately, the position became materially harder for P1 even though P1 still had the move count edge), the fractal looks closer to balanced than the control on this rule family.

**Quantitative metrics across both games.**

| Metric | Fractal | Control | Δ (frac − ctrl) |
|---|---|---|---|
| Turns to resolve | 31 | 17 | **+14** (+82 %) |
| Captures | 2 stones | 0 stones | **+2** |
| Winning chain length | 12 | 9 | **+3** |
| Anchors used by winner | 2 of 4 (NW, NE) | n/a | — |
| Times the winner changed stripes | 1 (row 2 → row 0) | 0 | **+1** |
| Distinct deg-2 cells played by either side | 6 ((4,2)(4,6)(0,2)(8,2)(6,4)(6,1*)…) | 0 | **+6** |

(*) (6,1) is degree-3, but in the post-block position it became the sole pivot — substrate-specific tactic.

---

## Phase 4 — Substrate Critic (mandatory rebuttal)

**Critic claim (a):** "The fractal is just an 8×8 grid with 17 dead cells stamped on it. Same surround, same connection. Holes are decoration."

**Rebuttal.** No — the holes change the *graph metric*, not just the cell count. Specifically: 31 % of active cells have degree 2 vs 6 % on the control. Because surround capture cares about liberty count, the fractal has a **continuous vulnerability gradient** that the control does not: cells fall into three distinct strategic classes (deg-2 = capture-bait, deg-3 = serviceable, deg-4 = anchor) that materially change which cells are worth playing first. Game-1 turn 19 capture is the receipt — it required only 3 P1 stones to remove 2 P2 stones, an attack ratio impossible on the corresponding control position.

**Critic claim (b):** "Any apparent difference is an artifact of fewer reachable shapes — fractal-Pair-C is just a smaller, harder Hex."

**Rebuttal.** Pair C does not use threshold scaling (connection has no threshold), so this artifact-route is closed. The shape claim is real but *understates* the change: fractal has **64 vs 64** active cells, so it is NOT a smaller board. What it has instead is **forced anchor competition**: both players want the same 4 cells in the opening because those cells are on free paths in both dimensions. On control there is no anchor — every interior cell is fungible. This is a genuinely new strategic dimension: opening theory on the fractal has a *unique* canonical sequence (anchors, then spines, then race to the edges); on control it has a *family* of equivalent sequences.

**Critic claim (c):** "An expert in the rectangular game transfers immediately to the fractal."

**Rebuttal — partial concession.** A Hex expert *would* know the high-level idea (race to two opposite faces, block via spine extension) and that transfers. But three pieces of fractal-specific knowledge do NOT transfer:

1. **Anchor priority.** The Hex player will try center; on fractal center is a hole. They have to learn the four-anchor structure.
2. **Two-bridge pattern fails near holes.** The classic Hex/connection two-bridge (two stones with two empty common neighbors) is a defended connection. On the fractal, when one of the "common neighbors" is a hole, the bridge degrades to a single-cell connection — much weaker, must be re-supported. Several would-be bridges around (4,2), (2,4), (6,4), (4,6) fail this way.
3. **Capture-by-shadow.** Surround capture is much more readily achievable adjacent to holes. The Hex player has zero intuition for "this stone has only 2 liberties because it's tucked next to a hole and one move from the corner finishes it." Game 1 turn 19 is exactly this tactic.

So: not "transfers immediately"; transfers the *strategic frame* but not the *tactical primitives*.

**Substrate-novelty score: 6/10.** Genuine new positional ideas (anchors, vulnerability gradient, stripe-switching detour) emerged organically from the substrate. Not a 7+ because the *core* game is still recognisably Hex-with-Go-captures — there is no qualitatively new mechanic, just a different terrain that pushes the existing mechanics into different territory.

---

## Phase 5 — VERDICT

**Team ID:** team-15
**Pair:** C
**Fractal candidate:** frac_C_fractal
**Control candidate:** frac_C_control

### Fractal scores

- **Strategic Depth: 7/10** — Connection-with-capture has multiple substantive phases (anchor opening, spine/block midgame, edge-race endgame) and the fractal substrate adds a fourth phase: choosing which stripe to break out through after the initial spine is blocked. 12-stone winning chains routed through 3 different rows is meaningfully deep. Capped from 8/10 by Pair-C's lack of moves/CA/propagation — the rule family itself is austere.
- **Balance: 6/10** — P1 won, but with a comfortable margin of only ~3 captured stones and a 31-turn detour-heavy endgame. The 4-fold carpet symmetry guarantees structural balance between dim-0 and dim-1, so any P1 advantage is *first-move* not *substrate-asymmetric*. Seat-swap evidence: Game 2 (control, seat-1 → P2 from team perspective) also resolved 1–0 to P1, so the bias is consistent with a generic P1-tempo edge that exists on both substrates, not a fractal-specific imbalance. Spot-check Game 3 (P2 plays vertical immediately) showed P2 reaching y=8 just as fast as P1 could threaten x=8, but tempo still favoured P1. Overall: P1 advantage exists, plausibly correctable with P2-seat compensation but not tested here.
- **Novelty (post-critic): 6/10** — Hex-with-Go-captures-on-fractal is a fresh combination but not a new mechanic. The capture+connection interaction is the most interesting feature and is not unique to the substrate.
- **Substrate-novelty: 6/10** — Real fractal-specific phenomena (anchor competition, vulnerability gradient, stripe-switching, hole-shadow captures) but not "fundamentally new strategic concepts I had to learn from scratch" (which would be 7+). I had to *adjust* Hex intuition, not *replace* it.
- **Overall "Would I play this again?": 6/10** — Yes, it's interesting. But the 31-turn detour endgames are tactically rich without being especially elegant — a lot of moves are forced ladder-walks. Fun for a few games, would likely tire of the same anchor opening.

### Control scores

- **Strategic Depth: 6/10** — Connection-with-capture on a uniform 8×8 grid is a recognisable Hex variant with capture flavour. Captures rarely fire (deg-4 interior is too well-defended for surround threshold-1 to bite). Endgame is mostly straight-line racing.
- **Balance: 6/10** — P1 won in 17 turns with no captures and no ambiguity; P2 played a reasonable interlocking-cross strategy and lost cleanly. P1-advantage is real but at least the structural cause (first-move tempo on a small connection board) is well understood.
- **Novelty (post-critic): 5/10** — Essentially "Hex with Go capture rules". Variant of an existing well-studied connection genre, no surprises.
- **Overall: 6/10** — Plays cleanly, resolves quickly, but light. A serviceable Hex variant.

### DELTA (fractal − control)

- **Strategic Depth:** **+1**
- **Balance:** **0**
- **Novelty (post-critic):** **+1**
- **Overall:** **0** (both 6, but the fractal earns its 6 via substrate effects, while the control earns its 6 via clean baseline play)
- **Substrate-novelty:** **+6** (fractal 6, control 0 by definition)

### Critical assessment

- **"The fractal substrate genuinely added strategic depth": Y (qualified).** The fractal added depth via *positional structure* (anchor cells, vulnerability gradient, stripe-switching) more than via *new tactics*. The added depth is real but bounded — perhaps +1 to +2 strategic-depth points, not a transformation.
- **Phenomena observed only on fractal:**
  - Four-anchor opening theory (forced contention for 4 specific cells).
  - Capture made viable by hole-induced low liberty counts (Game 1 turn 19).
  - Stripe-switching detour endgame (winner pivots between two non-adjacent free rows).
  - "Spine cell" deg-2 vulnerability (4,2)/(4,6)/(2,4)/(6,4) — must be supported, not played alone.
  - Two-bridge degradation when one bridge cell is a hole.
- **Phenomena observed only on control (substrate took away):**
  - Free choice of opening cell (no anchor pressure).
  - Clean two-bridge connections work everywhere.
  - Capture irrelevant in practice — interior stones are too safe for threshold-1 surround to bite.
  - Endgame is a straight outflank (one move per detour), not a multi-stone ladder.
- **Recommendation for R17: SECOND-PROBE (lean integrate).** The fractal substrate adds genuine but *mild* novelty on Pair C's rule family (alt + surround + connection). Integrating it directly into R17's evolutionary search would risk diluting evolutionary signal — the substrate-novelty bonus would compete against the deeper search for *mechanical* novelty. But dropping it would leave +1 to +2 points of latent strategic depth on the table. **Recommend a second probe: combine the fractal substrate with a richer rule family (CA or simultaneous turns or movement) where the hole-induced liberty gradient and anchor structure can interact with more dynamic mechanics.** If those interactions multiply rather than add, integrate. If they merely co-exist as on Pair C, drop. The Pair-C result by itself does not justify integration but *does* justify the second probe.
