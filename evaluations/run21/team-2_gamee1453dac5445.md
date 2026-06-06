# Run 21 Agent-Team Eval — team-2 — Game e1453dac5445

**Team ID:** team-2
**Game ID:** e1453dac5445 (menger slate TOP, 20-seed mean GE 0.177, σ 0.101, calibrated komi_p2 0.00)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game e1453dac5445` (see `briefing_menger_e1453dac5445.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 3D Menger sponge, 9×9×9. Level-2 holes punch out the central cross of every sub-cube; 400 of 729 cells are active. The active set is a thin fractal shell — z=0/2/6/8 layers carry the 2D carpet pattern, z=1/3/4/5/7 are heavily hollowed (entire y=1,4,7 rows are gone on the punched layers). Cell index = z·81 + y·9 + x. Verified live: 400 active, max_degree 6.

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = 100.

**Action space.** 731 actions = 729 placements + pass (729) + pie/swap (730). Place-only (D1 hybrid ban). `first_move_anywhere=True`, then `adjacent_empty` is advertised but the live legal set stays broad (389 legal after 12 stones) — adjacency is effectively non-binding.

**Placement & capture.** Capture = **outnumber, threshold 2**. A stone is **cleared to empty** when enemy neighbours exceed friendly neighbours by ≥2 in its radius-1 (≤6) neighbourhood. Verified live: lone P1 at (0,0,0) flanked by P2 at (1,0,0)+(0,1,0) (2 enemy, 0 friendly) → cleared. Capturing removes that stone's influence contribution too.

**Propagation.** `influence`, radius 1, strength 1.0, **decay 1.0** — *flat, no falloff*. Each placement adds ±1 to its own cell and ±1 to every active neighbour. Score(cell owned by P1) = 1 (self) + (#P1 neighbours) − (#P2 neighbours). Verified: greedy adjacency move = +3.000 (self +1, plus +1 to each of two existing friendly neighbours).

**Win condition.** **threshold-race** (NOT connection). First player whose effective owned-influence accumulator exceeds **30.0** wins. `target_dimension_p2 = -1` ⇒ P2 mirrors P1's accumulator (single shared scalar). komi_p2 = 0.00. max_turns 100; decay=1.0 makes the race fast (~21 plies in my games).

**Pie rule.** On. P2 may swap seats after P1's first move (action 730). Verified live: P2 playing 730 flipped P1's opening stone to P2 ownership and handed P2 the +1 and the tempo.

**Degeneracy check.**
- Komi gate did NOT lock in: residual P1 bias ≈0.060 at komi=0; positive komi overcorrects and flips P2 ahead, so 0 was served (below the G3 0.10 target). Balance rests entirely on the pie swap.
- `adjacent_empty` constraint is effectively vestigial (broad legal set live).
- Captures partly **conflict** with the win objective — clearing an enemy stone removes its negative contribution but also re-zeroes contested edges and exposes your own stones; the greedy hint ignores this.
- ~15% of training seeds collapse (bimodal σ, not Gaussian) — a training-fragility flag, not a play-time bug.

---

## Phase 2 — Strategic Play

All moves engine-verified. Place id = cell index; pass = 729; pie = 730.

### Game 1 — P1 push vs P2 symmetric mirror (tempo test)
Sequence: `0,80,9,71,1,79,18,62,2,78,11,69,19,61,20,60,81,141,83,143,99,159,101,161` (P1 builds the (0,0,0) corner block + z-stack; P2 mirrors the (8,8,0) corner).
Plot: Both accumulate ~+2.7/stone in their dense corners. At ply 12 both sat at +16.0. P1's first-move tempo carried through: **P1 crossed 30 first at ply 21 (+33.0) while P2 sat at exactly +30.0 (need > 30 — not a win).**
Reflection: Pure mirror is a one-tempo win for P1. Binding constraint = pack the densest contiguous active region; placement order just maximizes friendly adjacency. komi=0 leaves the tempo edge uncompensated → pie is mandatory for P2.

### Game 2 — P2 spoiler (capture/suppress instead of build)
Sequence: `0,3,1,12,2,21,9,5,18,14,11,23,19,84,20,86` (P1 builds corner; P2 plays stones *adjacent* to P1's cluster to drag down P1's cell values).
Plot: At ply 16 P1 = +21.0, P2 = +17.0. Spoiling shaved ~3 pts off P1 but cost P2 more — P2's adjacent stones earned only ~2.1/stone vs ~2.7 for a clean corner, and several risked outnumber capture. **P2 fell further behind by spoiling.**
Reflection: Suppression is net-negative for the spoiler. The dominant line for both seats is to race your own densest region; interference is a losing deviation. This is the engine's low strategic_diversity (0.181) made visible.

### Game 3 — Pie swap + capture mechanic (seat-balance / novelty stress)
Sequence: `0,730,9,80,1` (P1 opens (0,0,0); P2 swaps).
Plot: After 730, (0,0,0) became O (P2-owned), P2 holds +1 and the tempo. Capture sub-test (`0,1,80,9`): P2 cleared the lone P1 corner stone with 2 adjacent stones — but interior/edge cluster cells (≥2 friendly neighbours) are *uncapturable* because free neighbour slots are too few on the sparse shell. Captures only kill isolated stones.

### Strategy guides
**P1 (offence):** open in a dense corner of a face layer (z∈{0,2,6,8}), pack a contiguous 3×3-minus-hole block, then z-stack into the punched layers for cheap +1 neighbour bonuses. Race; ignore the opponent.
**P2 (defence):** **swap (730) on any strong P1 opening** — this is the whole defence. Then mirror-pack your own corner. Do not spoil; do not chase captures.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Essentially **one** — pack the densest contiguous active region. Diversity comes only from *which* corner/column you pick (all roughly equivalent). Spoiling and capture-hunting are dominated deviations.
**Counter-play.** Weak. There is no counter to "opponent packs faster" except packing faster yourself; the only real lever is the pie swap to equalize tempo.
**Short-term vs long-term.** Horizon ~3–4 moves (where is my next densest adjacency). Games end ~21 plies. Shallow planning depth.
**Emergent concepts observed.** Clustering compounding (each adjacency = +1 with flat decay); z-stacking across hollow layers; capture-only-kills-isolated. No higher-order structure.
**Does menger matter?** Partially — the holes force you to *find* contiguous active runs and reward z-stacking, which a flat 9×9 wouldn't. But the strategy reduces to the same "pack tightest" on any substrate; the sponge raises the routing-puzzle floor slightly, not the strategic ceiling.
**Does the propagation kernel matter?** decay=1.0 (flat) makes adjacency MORE rewarded than R20's decay-0.5–0.7 champions → the race is faster and MORE convergent (less positional gradient to exploit). This is the headline structural difference, and it makes the game *shallower*, not richer.
**Capture-rule contribution.** Marginal. Outnumber-2 only fires on isolated stones; in dense play it never triggered and actively conflicts with score-maximization.
**First-mover / seat balance.** Real P1 tempo edge at komi=0 (mirror → P1 wins by one tempo). Pie swap is the only balancer; with it, balance is acceptable. Residual bias 0.060 (below 0.10 but un-locked).

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This is a threshold-race influence-packing game on a Menger sponge — the **same family as the R19/R20 menger threshold-race champions**, with decay tweaked to 1.0.
(a) Threshold-race influence ≈ territorial/area scoring (Go-territory, Othello disc-count) with a numeric finish line.
(b) Outnumber-2 capture ≈ Ataxx/Tafl-style flanking, but here near-inert.
(c) "outnumber + flat-influence + threshold-race on menger" is not a named published game, but it is *internally* a re-skin of the R19/R20 menger pod with a faster clock.
(d) Fractal-substrate play on a Menger sponge is genuinely uncommon, but the substrate here is a routing constraint, not a strategic generator.
(e) Expert transfer: a Go/Othello player learns this in ~5 min ("pack tight, race to 30, swap if you're P2").

**Closest known-game analogue:** numeric-territory race (Go area-scoring with a finish line) on a fractal lattice.
**Comparison to R8 Connection Go (4.10).** Thinner. R8 had genuine cut+build dual-purpose tactics; this has none — it is a packing sprint.
**Comparison to R19/R20 best.** Same family as R19 menger top (4.8) and R20 depth-record (4.80) but **more convergent** (flat decay + diversity 0.181), and judged under an anchored-down rubric. Not richer than its ancestors; the decay=1.0 "novelty" reduces depth.

**Novelty score (post-adversary):** **3.0/10.** Above pure re-skin (the 3D fractal substrate + flat-decay clock is a fresh *parameterization*), below genuinely-new because the strategic content is identical to the menger threshold-race family.

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game ID:** e1453dac5445
**Rules Summary:** Drop stones on a Menger sponge; each stone radiates flat +1 influence to neighbours; first to a +30 owned-influence accumulator wins. Pack the densest contiguous region and race; P2 swaps to equalize.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=True, komi_p2=0.00.
**Turn Structure:** alternating.
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** un-locked komi gate (bias 0.060); vestigial `adjacent_empty`; captures conflict with win objective; bimodal training failure mode (~15%).

### Scores (1–10)
- **Strategic Depth: 3.5** — A ~21-ply packing race with a 3–4-move horizon. The 3D sponge adds a routing puzzle (contiguous-run finding, z-stacking) but no medium-term strategy. Engine strategic_depth 0.595 reads as a metric artifact of the fast race, not subjective depth.
- **Emergent Complexity: 3.0** — Clustering compounding and z-stacking are the only emergent patterns; flat decay kills positional gradient and captures are inert.
- **Balance: 3.5** — komi=0 un-locked (P1 wins the mirror by one tempo); pie swap is a working but sole balancer.
- **Novelty (post-adversary): 3.0** — See Phase 4: a faster, flatter re-parameterization of the menger threshold-race family.
- **Replayability: 3.0** — Diversity 0.181; once "pack densest + swap" is known there is little to explore.
- **Overall "Would an agent team play this again?": 3.5** — Competent and balanced-via-pie, but it is the most convergent packing race in the slate. The R21-headline "did we find something new?" answer is **no** — decay=1.0 made the family *shallower*, not deeper. Sits around R17/R20 production level, below R8 (4.10); does **not** clear the R19 5.0 ceiling (G1 not met by this game).

### CLOSEST KNOWN-GAME ANALOG
Numeric-territory race (Go area-scoring with a +30 finish line) on a fractal lattice. In-corpus: the R19/R20 menger threshold-race pod, faster clock.

### KILLER FLAWS
- Strategic diversity 0.181 — optimal play collapses to "fill the densest contiguous column/corner."
- Flat decay (1.0) removes the positional gradient that gave decay-0.7 siblings their (modest) extra texture.
- Captures are inert in dense play and actively conflict with the score objective.
- Komi gate un-locked; balance depends solely on the pie swap.

### BEST QUALITY
The 3D Menger shell genuinely complicates *where* to pack (contiguous active runs threading the holes; cheap z-layer stacking) — a real spatial-routing floor that a flat grid lacks. It raises the puzzle floor, not the strategic ceiling.

### menger STRUCTURAL CONTRIBUTION
Topology shapes *tactics* (which runs are contiguous through the holes) but not *strategy* (still "pack tight, race"). Consistent with R19's menger > carpet > grid ordering, but the flat-decay clock erodes the menger advantage. Could flatten to a regular grid with moderate (not minimal) loss.

### IMPROVEMENT IDEAS
**Single best change:** make the influence field *enter a non-additive win condition* (e.g., win by controlling N disjoint high-influence regions, or by a connection/territory-enclosure goal) so packing one blob is not strictly optimal — this is the only way to lift diversity above 0.18.
Secondary:
- Restore a decay < 1.0 to reintroduce positional gradient.
- Strengthen capture (outnumber-1, or a flip that steals influence) so it can threaten dense clusters and create real defensive decisions.
- Lock the komi gate (or accept pie-only and document it) so seat balance is principled.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-2_gamee1453dac5445.md`.*
