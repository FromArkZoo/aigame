# Fractal Spike — Pair B Evaluation (team-10)

Team ID: team-10
Pair: B
Fractal candidate: `frac_B_fractal` (sierpinski 9×9, 64 active)
Control candidate: `frac_B_control` (torus 8×8, 64 active)
Source game: R14 winner `deb4dfe0382d` — alt + custodian + radius-1 influence + threshold 38.616

---

## Phase 1 — Rule Comprehension

The two candidates are byte-identical apart from `topology_type`/`axis_size`. **Shared ruleset**: alternating placement on empty cells (first move anywhere); custodian capture (Othello-style axis-line bracketing); influence propagation radius=1, strength≈1.874, decay≈0.402; threshold win — first player whose total `board_value` on owned cells exceeds 38.616 wins (margin tie-break per R16 fix); max_turns=102.

**Substrate-only differences**:
- *Fractal*: 17 holes (central 3×3 + 8 sub-block centers). Holes are walls — no placement, no influence-propagation through them, custodian walks terminate at them.
- *Control*: torus 8×8, no holes, axis-line custodian walks are non-wrapping (engine restricts walks to `[0, axis_size)` on both topologies — torus does **not** wrap captures, only influence/distance).

**Degeneracy flag**: With strength 1.874 + decay 0.402, a stone alone contributes 1.874 to its own cell, +0.753 to each occupied friendly neighbor on either side. Threshold ≈ 38.6 is reachable by ~11 stones in a tight 4-degree-rich cluster (`(2,2)` plus arms). **The threshold is unchanged across substrates** (per `metadata.threshold_unchanged: true`), and 64 active cells × cluster scoring means it is comfortably reachable on both — game length is dominated by tempo, not by terrain.

---

## Phase 2 — Strategic Play (4 games, 2 per substrate, seat-symmetric)

### Game 1A — FRACTAL, mirror corner clusters
Plan: P1 builds 4-degree "+ cluster" centered at `(2,2)` (a fractal cell with all 4 neighbors active); P2 mirrors at `(6,6)`. Both clusters live against fractal walls — `(3,3)`/`(4,3)` shield P1's east flank; `(5,5)`/`(7,7)` shield P2's NW flank.

Move list (annotated):
1. P1 `(2,2)` — high-degree cluster anchor, 4 active neighbors despite hole curtain.
2. P2 `(6,6)` — symmetric mirror, identical degree profile.
3-9. Both extend "+ cluster" arms `(2,3)/(2,1)/(1,2)/(3,2)` for P1; `(6,5)/(6,7)/(5,6)/(7,6)` for P2. Each arm yields 1.874 + 0.753 ≈ 2.63 influence.
11. P1 `(1,3)` — corner-fill, two friendly neighbors.
12. P2 `(7,5)` — mirror.
13-17. Both densify into an "L"-shape; influence-per-stone ~3.4.
21. P1 `(0,3)` — **GAME ENDS**. P1 effective influence = **40.19** > 38.616. P1 wins.

P2 effective at game-end: 36.81 (one stone short). **No captures on either side. Game length = 21 moves (11+10).**

### Game 1B — CONTROL (torus), identical mirror plan
Same move sequence translated cell-for-cell to torus 8×8 (action remap `y*9+x → y*8+x`).

**Outcome**: P1 wins on move 21 with 11 stones in the same shape. **Identical termination point.** Influence values identical to the fractal stone-by-stone (verified by hand: `(2,2)` cluster center gets 4.886 in both; arms get 2.627; corner-fills get 3.380). No captures.

### Game 2A — FRACTAL, contested middle (seat-balanced — both contest near central hole)
P1 expands across the fractal "ring" around the central 3×3 hole (`(2,4),(4,2),(3,2),(5,2),(2,5),(2,6),(1,6)`), P2 mirrors on the opposite ring (`(6,4),(4,6),(5,6),(3,6),(7,6),(6,5),(2,7)`). Both players intentionally hug the central hole — testing whether the fractal wall creates exploitable defensive shape.

Move list highlights:
- M5 P1 `(2,4)` — only 2 active neighbors (hole `(1,4)` and `(3,4)`); influence-poor cell, but anchors a ring chain.
- M11 P1 `(5,2)` — reaches across to threaten an outnumber pattern with `(6,2)`. No bracket forms (no friendly to east).
- M14 P2 `(2,7)` — threatens column-2 capture of `(2,6)`. P1 defends M15 `(2,5)`.
- M25 P1 `(2,3)` — completes interlocked column 2 cluster. **GAME ENDS**. P1 wins with 13 stones; P2 has 12.

**No captures occurred.** Both sides repeatedly threatened custodian brackets but the threshold ended the game before any flip.

### Game 2B — CONTROL, identical contested-middle plan
Same sequence translated to torus. **GAME ENDS at move 25 with P1 at 13 stones**. Identical termination point, identical winner. The "fractal-isolated" cells like `(2,4)` had no leverage because their lonely-neighbor influence is the same on torus (the surrounding cells were also empty in this opening).

### Capture micro-experiment (forced demonstration)
Setup: P1 `(2,1)` → P2 `(3,1)` → P1 attempts `(4,1)` to bracket horizontally.
- **Control**: `(4,1)` is legal; P1 plays it; **P2's `(3,1)` is flipped immediately** (P1=3, P2=0 after 3 moves). Classic Othello bracket.
- **Fractal**: `(4,1)` is a HOLE — action ID 13 is rejected as illegal. P1 cannot bracket horizontally; the only path to capture `(3,1)` is the slower vertical route (X at `(3,0)` AND `(3,2)`) requiring two extra tempi.

This is a real, mechanical, fractal-only effect on custodian. **It exists but does not fire in race-to-threshold play.**

---

## Phase 3 — Strategic Analysis

| Metric | Fractal | Control | Δ |
|---|---|---|---|
| Game 1 length (moves) | 21 | 21 | **0** |
| Game 1 winner | P1 | P1 | same |
| Game 1 P1 influence at end | 40.19 | 40.19 | **0** |
| Game 2 length | 25 | 25 | **0** |
| Game 2 winner | P1 | P1 | same |
| Captures across all 4 games | 0 | 0 | 0 |

**Did the fractal play differently?** In our games — *no, identically*. Same move IDs (translated 1:1) produced same end state at same tempo. Influence math collapses across substrates because *empty and hole neighbors look identical to the influence accumulator*: only friendly stones contribute. Holes neither help nor hurt influence — they simply remove a cell from the eligible pool.

**Choke points / districts**: Cells like `(2,4),(4,2),(4,6),(6,4)` are 2-degree (sandwiched between two holes). They look strategic but in practice are *low influence yield* because they have at most 2 friendly cluster-mates ever. Players naturally avoid them — they're anti-choke-points.

**Influence shadows**: Radius=1 means propagation never has to "route around" anything — it stops at radius 1 anyway. Holes are functionally invisible to influence at this radius. (Higher radii would make the fractal matter.)

**Path routing**: N/A for Pair B (no connection win condition).

**Tempo / first-move advantage**: P1 won every game. With 11-13 stones for victory and alternating turns, P1 simply gets to the threshold first because they're one stone ahead at every parity check. **This is identical on both substrates** — the fractal doesn't restore P2 balance.

**Custodian asymmetry** (Phase 2 micro-experiment): Holes on rows {1, 4, 7} and cols {1, 4, 7} segment those axes; stones at the rim of the central 3×3 (e.g., `(2,3),(3,2),(2,5),(5,2),(3,6),(6,3),(5,6),(6,5)`) lose one custodian direction permanently. **Demonstrably real**, but produced ZERO captures in 4 full games because threshold games don't reach the fight phase.

---

## Phase 4 — Substrate Critic

**Critic argues**:
(a) The fractal is just an 8×8 grid (literally 64 active cells, same as control) with 17 cells removed in a recognizable pattern. Influence math is unchanged stone-for-stone. The "+ cluster" yields 15.39 influence on either substrate. The threshold gate fires identically. Where is the "new strategic concept"? *Nowhere observed*.
(b) Threshold scaling artifact: not applicable — threshold is unchanged AND active cell count is matched, so this is the cleanest possible A/B. The control performs identically without holes; the fractal therefore demonstrably adds nothing on this rule family.
(c) Transfer test: I (the player) wrote *literally the same opening sequence* and won the same way on both substrates with identical tempo and identical endgame influence values. An expert in the rectangular game transfers in zero seconds.

**Rebuttal (Player 1 + Player 2)**: One genuine, mechanical effect was demonstrated — the hole-blocked custodian (Phase 2 micro-experiment). On the fractal, P1 *cannot* play `(4,1)` to flip `(3,1)`, because the cell is a hole. Vertical capture remains available but costs an extra tempo. This restricts attackers and protects defenders sitting on rim cells.

**However**, in 4 actual played games, this asymmetry never *fired*. Threshold games race to ~12 stones in tight clusters; neither side voluntarily creates the bracket setup that would expose the asymmetry. The cluster-anchor cells `(2,2),(6,6)` are themselves NOT hole-adjacent (4-degree cells), so the asymmetry is invisible to optimal play.

**Substrate-novelty score: 3/10** — A real mechanical effect exists (custodian direction-dropping at hole boundaries; cluster-max-density cap at hole-adjacent cells) but it does not change strategic decisions in this rule family, because the threshold race resolves before captures matter.

---

## Phase 5 — Verdict

```
Team ID: team-10
Pair: B
Fractal candidate: frac_B_fractal
Control candidate: frac_B_control
```

### SCORES — Fractal
- **Strategic Depth: 5** — Identical to control. The "+cluster race to threshold" is the only strategy; ring-cells are deceptively low-yield. No new strategic concept emerges from the holes.
- **Balance: 3** — P1 wins both games (Game 1 by 1 stone tempo, Game 2 by 1 stone tempo). With 11-stone victory and alternating placement, P2 is structurally one tempo behind. Seat-swap (we tried both contested-middle and corner-cluster openings) produced no P2 win.
- **Novelty (post-critic): 4** — Custodian gets axis-segmentation around hole rows/cols. Demonstrated mechanically. Did not fire in any of 4 full games.
- **Substrate-novelty: 3** — Fractal effect is real but inert under threshold-race play. Would matter more with longer games (no threshold) or with capture-heavy mechanics (surround/outnumber).
- **Overall "Would I play this again?": 4** — A fast, decided, substrate-decorative game. The fractal aesthetic is the only differentiator from control.

### SCORES — Control
- **Strategic Depth: 5** — Same race-to-threshold, no captures, P1 tempo-wins. The torus wraparound on influence (distance metric) is invisible at radius=1 since edge cells still get 4 in-board neighbors via wrap, but no P1/P2 cluster touched the wrap zone in our games.
- **Balance: 3** — Same P1 dominance — built into the rule family, not the topology.
- **Novelty (post-critic): 3** — Standard threshold race; nothing distinguishing.
- **Overall "Would I play this again?": 4** — Same game, less visually distinctive.

### DELTA (fractal − control)
- Strategic Depth: **0**
- Balance: **0**
- Overall: **0**
- (Substrate-novelty is fractal-only by definition, so no Δ.)

### CRITICAL ASSESSMENT
- **"The fractal substrate genuinely added strategic depth"**: **N**.
- **Specific phenomena observed only on fractal**:
  - Hole-blocked custodian: action 13 (`(4,1)`) literally illegal, forcing detour to vertical capture. Verified with isolated 3-move setup.
  - Cluster-max-density cap at hole-adjacent cells (e.g., a "+" cluster at `(2,1)` cannot be filled into a 3×3 because `(1,1)` is a hole).
  - Anti-choke-points: 2-degree cells (`(2,4),(4,2)`, etc.) are visibly weak placements (low influence yield, no expansion); both players naturally avoided them.
- **Specific phenomena observed only on control**:
  - Easy 1-tempo horizontal custodian flips (any axis, any row, no segmentation).
  - Wraparound influence distance (engine BFS on torus) — *zero impact at radius=1*; would matter at radius ≥ 4.
  - Larger contiguous cluster ceiling (no cap from holes).
- **Recommendation for R17**: **DROP** for this rule family. The Pair B mechanics (radius-1 influence + custodian + low threshold) are insensitive to the hole pattern — the threshold race ends before the substrate effect can fire. If fractal is to be tested seriously, it must be paired with: (i) larger propagation radius (≥ 3) so influence-routing-around-holes matters; or (ii) a non-threshold win condition (territory or connection) that forces play to reach the contested middle and exposes the custodian asymmetry. The hand-crafted Pair C (surround + connection) is the most likely fractal-native ruleset; Pair B's reuse of the R14 winner reproduces R14 verbatim regardless of substrate.

---

### Methodology notes
- All four games played end-to-end via `play_helper.py --action play`.
- Action-ID translation between substrates: fractal `y*9+x` → control `y*8+x`, applied cell-for-cell to keep openings comparable.
- Influence values validated by hand against `engine_v2.py:_propagate_influence` (each placement adds `strength * decay^dist` to in-radius cells). The hand calculation `4*1.874*0.753 + 1.874 = 4.886` for 4-friendly-neighbor anchor matches the engine outcome.
- Time spent: ~1.5 hours. Hard stop comfortably under budget.
