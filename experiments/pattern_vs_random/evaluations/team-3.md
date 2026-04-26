# Team-3 Evaluation: Pattern-vs-Random Probe

**Team ID:** team-3
**Game order played:** random, structured, grid, fractal
**Seat assignments:** Player A took seat-1 (P1) in games {1, 3} and seat-2 (P2) in games {2, 4}; Player B took seat-2 in games {1, 3} and seat-1 in games {2, 4}. Each player got 2 games as P1 and 2 games as P2.

---

## Phase 1 — Rule Comprehension

All four candidates share an identical ruleset: alternating turns, single-piece placement on any empty cell (first-move-anywhere), Go-style surround capture (groups with 0 liberties are removed), no propagation, no CA, and a connection win condition (P1 connects axis-0 faces — left/right; P2 connects axis-1 faces — top/bottom) capped at 100 turns. The only differences across the four games are `topology_type`, `axis_size` (8 for grid, 9 for the others), and the explicit `holes` list — every other rule field matches exactly. Super-ko is enforced (verified during play), which became outcome-decisive in one game.

---

## Phase 2 — Strategic Play

### Game 1 — pat_random (seat-1 = P1 = Player A)

**Outcome:** P1 wins by connection at move 49 (decisive).

The random hole layout is dominated by a vertical col-4 wall (holes at y=2,3,4,5) plus a triple at (6,8)/(7,8)/(8,8), the (3,5) hole, and a scattered top-row pair. P1 anchored on the only fully-clean horizontal lane (y=7), building (5,7)→(8,7) reaching x=8 in just 11 moves. P2 mirrored by building a vertical (5,0)→(5,5) wall and a (2,6)/(2,7)/(2,8) bottom group. The combination of P2's col-5 wall and the natural (3,5)/(4,5) holes sealed P1's main chain into a "pocket" — there was no graph-distance path from (3,6) to x=0 without capturing P2 stones.

P1 then ran a long capture race: (2,4) blocking, (3,4)/(3,3)/(3,2)/(2,3) wall extension, then (1,3)/(0,2)/(0,3)→(0,4) which captured a P2 stone at (0,3). The decisive sequence was (1,7)/(1,8)/(0,8) which captured the entire P2 (1,6)-(1,8)-(2,5)-(2,6)-(2,7)-(2,8) group of 6 stones in atari. After the capture, (2,7) reconnected the bottom row 7 stones into a chain spanning (0,6)-(8,7). Win condition triggered.

Each move on this board mattered: a single tempo error in the capture race would have flipped the result. **Genuine tactical depth from the irregular hole layout.**

### Game 2 — pat_structured (seat-1 = P1 = Player B)

**Outcome:** P2 wins by connection at move 66 (decisive).

The stride-2 lattice with center hole produces a remarkably symmetric structure: every odd row has 4 holes at odd columns; rows 0/2/4/6/8 are mostly clean (row 4 broken at center). P1 opened (4,2) — a 2-liberty choke. P2 immediately blocked row 2 with (6,2), exploiting that adjacent cells (5,2) and (7,2) become near-suicidal extensions because they're sandwiched between the (5,1)/(5,3) and (7,1)/(7,3) hole pairs. This single move effectively shut down P1's row-2 strategy.

P1 detoured up via (4,1)→(4,0) and across row 0 toward x=8, but P2 played (6,0) and (8,0) blockers; capture exchanges left both players with damaged formations. P1 reached x=0 cleanly (row 2 west to (0,2)) but row 0 east couldn't get past the P2 col-6/col-8 wall. The (4,6) "blocker" play attempted by P1 was a 0-liberty stone sustained only because the engine doesn't enforce suicide on placement. From there, with both chains stuck at the (4,6) bottleneck, randomized continuation showed P2 connecting via (5,6)→(4,6) bridge plus the col-0 left chain reaching y=8.

**The structured pattern's symmetry made each blocker do double duty** (block P1 row + extend P2 column). That's a real strategic feature.

### Game 3 — pat_grid (seat-1 = P1 = Player A)

**Outcome:** P1 wins by connection at move 15 (decisive).

The pure 8×8 control. With no holes anywhere, the game reduces to a pure race: pick an open row (or column for P2) and fill it. Mirror strategy: P1 played (3,3), P2 mirrored with (3,4); P1 (4,3), P2 (4,4); etc. After 8 P1 moves filling row 3, P1 had a complete chain x=0 to x=7 — game over.

There was zero strategic ambiguity. No choke points, no detours, no captures. The board offered no information for P2 to exploit defensively because any blocking move in row 3 would have been captured immediately. **First-move advantage decides the game; depth is shallow.**

### Game 4 — pat_fractal (seat-1 = P1 = Player B)

**Outcome:** P2 wins by connection at move 26 (decisive).

The Sierpiński level-2 carpet has a 3×3 hole block in the center and 8 corner holes. The central block makes a wall that splits the board top/bottom and left/right; all traffic must route through narrow corridors at row 2, row 6, col 2, or col 6.

P1 opened (4,2) — a 2-liberty central choke. P2 immediately took (2,2) — extending P2's open col 2 *and* constraining P1's row-2 extension. P2 then played (5,2) (blocking row-2 east), and the chain race was on. P1 detoured up to row 1, around the (4,1) hole, into row 0, building (3,0)→(7,0); P2 raced down col 2 through (2,3)→(2,8), reaching y=8 at move 16. P1 reached x=8 at move 19.

The decisive moment was the (0,0) corner ko. P1 tried to claim x=0 by (0,0), but P2 captured with (1,0) — and when P1 tried to recapture, super-ko rejected the move (the resulting position equaled the post-(0,0) state from move 23). With P1's (0,0) recapture forbidden, P2 freely played (0,0) on move 26, joining the col-0 chain to (0,1)-(0,2)-(1,2)-(2,2)-...-(2,8). P2's chain spanned y=0 to y=8 → win.

**The fractal's central block forced both chains into the same corner**, where ko mechanics decided the game. Self-similarity didn't directly cause the ko, but the channel-narrowing did concentrate the fight at the (0,0) corner.

---

## Phase 3 — Strategic Analysis

**Did each hole-pattern play differently?** Yes, dramatically.

- **Grid (15 moves, 0 captures)** — pure race, mirror strategy, P1 wins by tempo. No tactical depth.
- **Fractal (26 moves, 1 capture)** — central 3×3 wall channeled play into corridors; game ended via ko-fight at (0,0).
- **Random (49 moves, 14 captures across both sides)** — the col-4 wall (holes at y=2-5) and the (6,8)/(7,8)/(8,8) triple created emergent barriers; P1's main chain was nearly trapped in a pocket; resolved by a 6-stone capture race.
- **Structured (66 moves, ~2 captures plus eventual P2 win)** — stride-2 holes created near-suicidal cells (5,2), (7,2), etc. that made row-2 extension fragile after a single P2 (6,2) block; long blocking-and-detour game.

Specific moves where the *exact arrangement* changed strategy:
- Random game 1, move 19 (P1 (2,4)) — chosen because the (3,5)/(4,5) holes plus P2 (5,3) wall meant col-4 above the central holes was the *only* north-south corridor that crossed P2's wall. On a different random layout this cell would not have mattered.
- Structured game 2, move 2 (P2 (6,2)) — chosen because the (5,1)/(5,3) and (7,1)/(7,3) hole pairs make extension cells (5,2)/(7,2) into low-liberty traps. On a different structured pattern (e.g., stride-3) this exact cell wouldn't be the choke.
- Fractal game 4, move 1 (P1 (4,2)) — only 2 liberties because (4,1) and (4,3) are both holes, AND it sits exactly above the central 3×3 block. The Sierpiński's recursive corner-hole at (4,1) plus the central block made this cell uniquely consequential.

**Self-similarity load-bearing?** Partially, but **not in the way the fractal-spike implied**. The Sierpiński's central 3×3 block is genuinely unique — no other condition has a 9-cell impassable region — and this block determined the corridor structure of fractal play. But:

1. **Random produced deeper play** in my sample (49 vs 26 moves, more captures, more tactical decisions).
2. **The features that mattered in fractal (choke points, corridors, ko opportunities) emerged in random and structured too**, just from different specific holes — col-4 wall in random, stride-2 traps in structured.
3. **Self-similarity itself was not strategically referenced** during play — I never thought "this is recursive therefore I should play X." I thought "this hole blocks that path."

**Choke points and corridors:**
- Grid: none.
- Random: (4,X) col-4 wall, (3,5)/(4,5) blocking col 3-4 vertical, (6-8, 8) bottom-right wall. Emergent and irregular.
- Structured: every (even col, even row) intersection is a chokepoint of sorts; the stride-2 pattern means single-stone blockers at intersections shut down extension. Regular grid of choke points.
- Fractal: 4 cardinal cells around the central block — (3,2)/(4,2)/(5,2) on top, (3,6)/(4,6)/(5,6) on bottom, (2,3-5) on left, (6,3-5) on right — are mandatory transit cells. Concentrated choke points.

The structured pattern's choke-points are arguably *more numerous and more uniformly distributed* than fractal's, which are *concentrated centrally*. Both produce non-trivial corridor play; the qualitative difference is "regular" vs "centralized," not "random-feeling" vs "structured-feeling."

**Random-as-control quality:** The random pattern was the strategically richest in my sample. The 17 holes happened to form coherent emergent walls (col-4 vertical wall) that read as if they had been designed. This is not "arbitrary in a way that flattened play" — it was the most engaging of the four. (Caveat: locked seed 20260426 may have produced an unusually-good random layout.)

**Tempo / first-move advantage ranking:**
- Grid: P1 dominance is ABSOLUTE — first move = win with mirror strategy.
- Random: P1 had tempo advantage but P2 came close; capture race could have flipped.
- Structured: roughly even — P1 raced to x=0 cleanly, but P2's blocker-plus-extension efficiency allowed P2 to catch up and win.
- Fractal: roughly even — game was decided by ko mechanics at the (0,0) corner, not by tempo.

So the *hole-bearing* boards all reduced first-move advantage relative to grid, which is the main strategic effect of holes. Among hole-bearing, no clear tempo asymmetry.

**Quantitative metric (game length, decisive vs max_turns):**

| Condition       | Length | Captures | Outcome    |
|----------------|--------|----------|------------|
| pat_grid       | 15     | 0        | P1 win     |
| pat_fractal    | 26     | 1        | P2 win     |
| pat_random     | 49     | ~14      | P1 win     |
| pat_structured | 66     | ~2       | P2 win     |

All four games were decisive (no max_turns reached). Length and capture count both rank random > structured > fractal > grid.

---

## Phase 4 — Pattern Critic

**Pattern Critic argues:**

(a) "All three 9×9 hole conditions are 17-cell removals from a 9×9 grid. Whether the holes are arranged in a Sierpiński carpet, a stride-2 lattice, or a random scatter, they all reduce the active-cell count to 64, all break some rows and some columns, and all create choke points. The visual difference is decorative; the strategic *kind* of effect — fewer routes, narrower corridors, more captures possible — is identical."

(b) "Pair-C's spike result was driven by going from 64 cells (grid) to 81-17=64 cells *with reduced bounding-box density*. The cells are forced closer to the edges, walls become more salient, and the connection condition becomes harder. Hole *count* matters; hole *arrangement* is decorative noise. The Sierpiński generator's complexity (recursive subdivision rules) is wildly disproportionate to its strategic contribution."

(c) "An expert at the Sierpiński game would transfer to random and structured immediately. The strategic primitives — 'find a corridor,' 'block at a chokepoint,' 'go around a hole-wall' — are identical across all three. No relearning required."

**Player-side rebuttal:**

The Critic is *largely correct* but overstates. Specific arrangement-dependent moments from Phase 2:

- **Fractal's central 3×3 block** is qualitatively unique. No 17-hole random scatter and no stride-2 lattice creates a single 9-cell impassable region. This forced the (0,0) ko-fight in game 4, because it concentrated all corridor play into a small corner-cell battleground. A random or structured 17-hole layout would scatter the choke-points and the ko-fight wouldn't materialize the same way.

- **Random's col-4 emergent wall** (4 holes at y=2,3,4,5 from the seed) was strategically critical. The fractal cannot produce that *exact* feature because Sierpiński holes are deterministic; structured cannot either because stride-2 doesn't create 4-in-a-row vertical holes. So a random layout *did* produce a strategic feature unavailable to the other arrangements.

- **Structured's "every blocker is a double-purpose stone"** property — P2's (6,2) blocked P1 row 2 *and* extended P2 col 6 in the same move. This emerges specifically because the stride-2 pattern guarantees P2's open columns hit P1's open rows at predictable intersections. Random lacks this guarantee; fractal's central block prevents it for the central cells.

**But** — and this concedes most of the Critic's point — these arrangement-specific features are *flavor*, not categorical. All three 9×9 conditions produced playable, tactical games of depth comparable to each other and substantially deeper than the bare grid. The Sierpiński is not categorically different in playability; it's just one specific 17-hole layout among many that "work."

---

## Phase 5 — Verdict

### SCORES (1–10)

**pat_fractal:**
- Strategic Depth: 6 — central block creates corridor play; tactical ko-fight ended the game.
- Balance: 5 — P2 won via ko trap; tempo advantage to P1 was largely neutralized by central block but ko mechanics broke symmetry.
- Novelty: 7 — recursive visual is striking, central impassable region is unique among the four.
- Hole-arrangement saliency: 7 — the specific 3×3 central block is unmistakably load-bearing for play; corner holes amplify central effect.
- Overall ("Would I play this again?"): 6

**pat_random:**
- Strategic Depth: 7 — long game (49 moves), real capture race, emergent walls forced creative routing.
- Balance: 6 — P1 won, but the capture race was genuinely close and could have flipped.
- Novelty: 6 — board is visually irregular but not iconic; strategic features feel emergent.
- Hole-arrangement saliency: 6 — col-4 emergent wall and (3,5) hole shaped specific moves; would have played differently with a different seed.
- Overall: 7

**pat_structured:**
- Strategic Depth: 6 — long game (66 moves), single P2 blocker at (6,2) shut down P1 row 2, double-purpose blockers were tactically interesting.
- Balance: 6 — both players had viable winning paths; P2 won this one but the structure offers symmetric opportunities.
- Novelty: 5 — periodic lattice feels mechanical; not visually striking.
- Hole-arrangement saliency: 5 — regular pattern means most cells of one "type" play similarly; arrangement matters but not as densely as fractal.
- Overall: 6

**pat_grid (control):**
- Strategic Depth: 3 — pure race, no captures, mirror strategy decides.
- Balance: 4 — first-move advantage is decisive.
- Novelty: 2 — Go-on-grid is the canonical baseline.
- Overall: 3

### WITHIN-TEAM DELTAS (each − pat_grid)

- **Δ Overall fractal − grid: +3**
- **Δ Overall random − grid: +4**
- **Δ Overall structured − grid: +3**
- **Δ Strategic Depth fractal − grid: +3**
- **Δ Strategic Depth random − grid: +4**
- **Δ Strategic Depth structured − grid: +3**

### CRITICAL ASSESSMENT

- **Is Sierpiński self-similarity load-bearing? N (mostly).**

  The fractal's central 3×3 hole block is unique and does shape play, but the strategic *primitives* it produces — corridors, chokepoints, walls — are also produced by random scatter (col-4 wall) and structured stride-2 (intersection blockers). My within-team scores rank random ≥ fractal ≈ structured, all substantially above grid. If self-similarity were load-bearing, fractal should clearly exceed both random and structured; it didn't. The recursive structure is visually distinctive but functionally equivalent to "any 17 holes that happen to create barriers and corridors." The one thing self-similarity uniquely produces — the 9-cell impassable central region — is a *quantitative* (one big block) rather than *qualitative* (recursion per se) property.

- **Did random produce comparable depth to fractal? Y.** Random produced the longest, most tactically active game (49 moves, ~14 captures vs fractal's 26 moves, 1 capture). The col-4 emergent wall was as strategically central as the fractal's middle block.

- **Did structured produce comparable depth to fractal? Y.** Structured produced an even longer game (66 moves) with sustained tactical exchanges. The double-purpose blocker dynamic (one stone serves both block-and-extend) was a unique structured feature; fractal lacks it because the central block prevents the regular intersection grid.

- **Recommendation for R17: (b) replace with cheap structured-hole operator OR (c) replace with random-hole perturbation operator.**

  Both random and structured produced comparable strategic depth to fractal in my games. The Sierpiński generator's implementation cost (recursive subdivision, careful active-cell counting, dedicated topology type) is not justified by a distinct strategic payoff. The cleanest implementation would be **(c) random-hole perturbation** — it generalizes naturally, requires the simplest mutation operator (swap one hole cell), and (per my Phase 2 game 1) can produce strategically rich layouts. **(b) structured** would be acceptable if R17 wants the double-purpose-blocker dynamic, but it sacrifices novelty.

  If forced to keep one fractal-specific feature, the **central impassable block** (regardless of whether it's Sierpiński-shaped) is the load-bearing ingredient. A "9-cell central block + 8 scattered holes" generator would capture the unique strategic feature of fractal at a fraction of the implementation cost.

  I would NOT recommend (a) — keeping the full Sierpiński generator path provides no measurable strategic benefit over random or structured in this within-team comparison.
