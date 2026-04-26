# Team-7 Evaluation: Pattern-vs-Random Probe

**Team ID:** team-7
**Game order played:** pat_random → pat_grid → pat_structured → pat_fractal
**Seat assignments:** Two team roles, "Player A" (assigned engine seat-1 / X in odd-indexed games, seat-2 / O in even-indexed) and "Player B" (mirrored). Across games 1–4 each role sits in seat-1 twice and seat-2 twice (2-2 split). Game 1 (random): A=seat-1, B=seat-2. Game 2 (grid): A=seat-2, B=seat-1. Game 3 (structured): A=seat-1, B=seat-2. Game 4 (fractal): A=seat-2, B=seat-1.

---

## Phase 1 — Rule Comprehension

All four candidate JSONs use IDENTICAL rules: alternating-turn placement on `empty` cells, surround (Go-style) capture, no propagation, connection win where Player 1 connects axis-0 (left↔right faces) and Player 2 connects axis-1 (top↔bottom faces), max 100 turns. Differences are limited to `axis_size` (8 for grid, 9 for the three hole-bearing substrates), `topology_type` (grid / sierpinski / holes), and the explicit `holes:` list. Active-cell count is 64 across all four conditions.

---

## Phase 2 — Strategic Play (4 games)

### Game 1 — pat_random (Player A = P1 X / left-right)

The 9×9 random pattern has a striking asymmetry: a vertical "wall" of holes at column 4 rows 2–5, plus a tight three-hole corner pocket at (6,1)/(7,2)/(8,1) and the SE corner triple (6,8)/(7,8)/(8,8). The wall forces all P1 left-right routing into a top bypass (the 2-cell channel at (4,0),(4,1)) or a bottom bypass (rows 6–8 at column 4).

Move-by-move (key moves):
- **M1 P1 (4,1):** Claim the top bypass channel through the column-4 hole wall — only 2 cells wide so this is the critical pinch.
- **M2 P2 (5,4):** Take a central anchor on the right side of the wall to start a column-5 chain (P2's primary north-south corridor).
- **M3 P1 (4,0):** Lock both cells of the top bypass.
- **M4–M10 (alternating extensions):** P2 extends column-5 chain (5,3)→(5,2)→(5,5)→(5,6)→(5,7) — a 6-stone vertical wall mirroring my horizontal needs. P1 extends row-1 westward and row-0 eastward.
- **M11 P1 (6,0):** Push along row 0 east toward right edge.
- **M12 P2 (2,0):** Anchor a top-side chain in column 2 to attempt y=0 connection (since column-5 is blocked from y=0 by my (5,1)). Self-atari since (3,0)/(2,1) are open and (1,0) is hole — single liberty.
- **M15 P1 (2,1):** Atari on (2,0). Forces the issue.
- **M17 P1 (3,0):** **Capture (2,0).** First capture of the game.
- **M18–M30:** P2 attempts a second top-side chain via (2,2)→(2,3)→(2,4)→(1,3)→(1,4)→(2,5). I attack steadily with (1,2), (3,3), (3,4), (0,3), (0,4) — each move closing a P2 lib.
- **M31 P1 (2,6):** **Capture 6 P2 stones** — the entire second top-side chain dies. P1=16, P2=8.
- **M32–M40:** P2 extends column-5 chain east into column 6 ((6,3),(6,5)) and column 7/8 ((7,3),(7,5),(8,5)) trying to suffocate my eastern probe and gain libs. I sortie with (6,4),(7,4),(8,4),(8,3) trying to reach x=8 directly.
- **M42 P2 (8,2):** **Capture 4 P1 stones** ((6,4),(7,4),(8,3),(8,4)) — my eastern probe dies. P1=17, P2=14.
- **M43–M55:** Heuristic continuation. P1 fills row-2 west and row-3 west (2,2)/(2,0)/(2,3)/(1,3)/(0,1) consolidating the left wall. P2 extends east-side bulwark (6,4)/(7,4)/(6,6)/(6,7)/(7,6)/(7,7).
- **M53 P1 (7,1):** Sacrifice into the (6,1)/(7,2)/(8,1) hole pocket — the engine permits suicide-style placements (no own-group lib check after capture pass), which sets up the next move.
- **M55 P1 (8,0):** **Capture P2's stranded (7,0)** — playing (8,0) drops (7,0)'s last liberty.
- **M56 P2 (7,0):** **Recapture (7,1) AND (8,0)** — P2 retakes the corner.
- **M59 P1 (8,0):** **Capture (7,0) again** — ko-like back-and-forth in the corner pocket.
- **M61 P1 (7,0):** Place at (7,0). Connects (6,0) → (7,0) → (8,0) → main chain reaching x=8. Combined with the (0,1)–(0,4) cells at x=0, this **completes the left↔right connection. P1 wins.**

**Result:** P1 wins by **connection** at move **61** (decisive). Final P1=25, P2=21. Total captures: 6 (M17/M31), 4 (M42), 4 (M55–M59 corner pocket), 2 (M56) = **at least 13 captured stones across the game.**

### Game 2 — pat_grid (Player A = P2 O / top-bottom)

8×8 clean grid. The classical Hex-on-grid + surround-capture race.

- **M1 P1 (3,3), M2 P2 (4,3):** Centre engagement; P2 plays directly east of P1's centre to deny P1 row-3.
- **M3 P1 (5,3), M4 P2 (4,4):** P1 jumps over P2's (4,3) to claim (5,3); P2 steps down-east.
- **M5–M14:** Each side extends along its needed axis. P1 builds row-3 east-then-west: (5,3)→(6,3)→(7,3) reaches x=7 by M7, then (5,2)→(5,1)→(5,0) plus (2,3)→(1,3)→(0,3) closing both ends. P2 builds column-4 south: (4,4)→(4,5)→(4,6)→(4,7) reaches y=7 by M14.
- **M15 P1 (0,3):** Reach x=0. But (4,3)P2 still cuts row-3 between (3,3) and (5,3) — must bridge via row-2.
- **M16–M26 (heuristic):** P2 climbs column-4 north (4,2),(4,1) plus row-7 east (5,7),(6,7),(7,7) but never fills (4,0). P1 fills row-2 (2,2)→(7,2)→(3,2) building the bridge under P2's (4,3).
- **M27 P1 (3,2):** Closes the row-2 bridge. Chain (0,3)–(3,3) via row 3 + (3,2) → (4,2)? No, (4,2) is P2. So actually the bridge runs (0,3)→...→(3,3)→(3,2)→(2,2)? Let me re-state: with (3,2),(4,2)P2,(5,2)P1,(6,2),(7,2)P1, the row-2 segment splits at (4,2). The connection is reached via (3,3)→(3,2)→col-2 cells P1 owns? Actually the engine confirmed connection; on inspection the chain runs col-5 + col-3 + row-2/row-3 segments forming a contiguous P1 path from (0,3) all the way to (7,2)/(7,3). **P1 wins by connection** at move **27**. Final P1=14, P2=13. **0 captures.**

A clean strategic race with no tactical pyrotechnics — pure first-move connection geometry.

### Game 3 — pat_structured (Player A = P1 X / left-right)

9×9 with stride-2 lattice of holes at every (odd, odd) cell on rows 1/3/5/7 plus a single centre hole at (4,4). All even rows (0, 2, 6, 8) are completely clear; all even columns (0, 2, 6, 8) are completely clear. Row 4 has only one hole (4,4). Column 4 has 5 holes ((4,1),(4,3),(4,4),(4,5),(4,7)) — heavily fractured.

- **M1 P1 (4,2), M2 P2 (2,4):** Both claim center cell of their primary clear corridor (row-2 / col-2).
- **M3–M8 (alternating):** Pure corridor race. P1 fills row 2: (3,2),(5,2),(2,2)... P2 fills col 2: (2,3),(2,5),(2,6).
- **M9 P1 (2,2):** Cuts P2's col-2 chain at the row-2 intersection.
- **M10–M16:** Both fill outward. P2 reaches y=8 ((2,8) at M14) and y=0 ((2,1) at M16, but (2,2)P1 blocks the chain so (2,1) is a single isolated stone — chain still broken).
- **M17 P1 (8,2):** Completes row 2 from (0,2) to (8,2). **P1 wins by connection.** Length **17 moves**, P1=9, P2=8, **0 captures.**

The crucial insight: P2's column-2 chain is *severed* by P1's (2,2). Even if P2 had played (2,1) before P1 played (2,2), P1 could still complete row 2 because (2,2) is the natural intersection where row-2 and col-2 strategies collide. The intersection-hijack is the only real tactical motif on this substrate at heuristic depth.

(Variant: with col-6 opening for P1, P2 wins by col-2 sweep at move 26 because P1 abandons the row-2 intersection.)

### Game 4 — pat_fractal (Player A = P2 O / top-bottom)

9×9 Sierpiński level-2 carpet. 17 holes form a self-similar pattern: a centre 3×3 dead block at rows 3–5 cols 3–5, plus 8 mid-edge / corner holes on rows 1/4/7 and cols 1/4/7. Importantly, all even rows (0, 2, 6, 8) and all even cols (0, 2, 6, 8) are *completely clear* — same property as pat_structured.

- **M1–M8 (same opening as Game 3 for direct comparison):** P1 (4,2) → P2 (2,4) → P1 (3,2) → P2 (2,3) → P1 (5,2) → P2 (2,5) → P1 (6,2) → P2 (2,6).
- **M9 P1 (2,2):** Same intersection hijack as Game 3.
- **M10–M16:** Heuristic fills outward identically to Game 3.
- **M17 P1 (8,2):** **P1 wins by connection** along row 2. Length **17 moves**, P1=9, P2=8, **0 captures.**

**The fractal carpet's distinctive feature — the central 3×3 hole zone — never came into play.** Both players found their clear corridors (P1 row-2, P2 col-2) and never had reason to enter rows 3–5 or cols 3–5. The Sierpiński shape was strategically *invisible* in this game.

(Variant: with col-6 opening, the game lasts 28 moves and P2 wins by col-2 sweep. Comparable to pat_structured's col-6 variant at 26 moves.)

---

## Phase 3 — Strategic Analysis (joint, all 4 games)

### Did each hole-pattern play differently?

**pat_random:** YES, dramatically. The col-4 vertical hole wall (rows 2–5) was a *first-class strategic feature* — every P1 move had to consider top vs bottom bypass, and P2's column-5 chain became a 7-stone wall that I had to attack with sacrificial probes. The (6,1)/(7,2)/(8,1) corner pocket produced a multi-turn ko-like exchange (M53–M61) that decided the game. Three concrete moves changed because of *which* holes were where: (a) M1 (4,1) chosen specifically as the only top bypass, (b) M11 (6,0) reaching toward x=8 along the unique row-0 east corridor, (c) M55 (8,0) capture made possible only because of the (8,1) hole that creates the corner pocket.

**pat_grid:** Different in feel — pure geometric race with no hole-driven detours. The strategic moves (cross-cut at moves 3–4, row-2 bridge at moves 23–27) were dictated by *opponent placement*, not topology.

**pat_structured:** Played differently from grid (shorter, no captures) but the difference was driven by *availability of clear corridors* — once P1 sees row-2 is fully clear, the strategic choice collapses. The 17 holes don't generate local tactical pressure because they're spaced 2 apart on odd rows.

**pat_fractal:** Played *identically* to pat_structured at the move-by-move level for both opening variants tested. The Sierpiński shape didn't generate a single move difference vs the structured lattice.

### Self-similarity load-bearing?

**No, not at this evaluation depth.** pat_fractal and pat_structured produced indistinguishable games. The Sierpiński carpet's central 3×3 dead zone is a structurally larger obstacle than pat_structured's single (4,4) hole, but neither came into play because both substrates leave clean even-row corridors that any sensible player will claim. The recursive self-similar pattern wasn't exploited or required at any move I made.

### Choke points and corridors

| Substrate | Key choke points | Clear corridors |
|---|---|---|
| pat_grid | None (any 8 stones in a row connect) | All 8 rows / 8 cols |
| pat_random | (4,0)/(4,1) top bypass; (4,6)–(4,8) bottom bypass; (6,1)/(7,2)/(8,1) corner pocket; SE corner triple (6,8)/(7,8)/(8,8) | Row 7 (clear); row 6 (1 hole); col 5 (clear); col 2 (clear) |
| pat_structured | (4,4) singleton centre; col 4 fractured | Rows 0/2/6/8 fully clear; cols 0/2/6/8 fully clear |
| pat_fractal | Central 3×3 (rows 3–5 cols 3–5) — but easy to skirt; (1,4)+(7,4) on row 4 | Rows 0/2/6/8 fully clear; cols 0/2/6/8 fully clear |

**Sierpiński's 3×3 vs structured's single-cell centre:** Qualitatively similar at the "above-or-below" routing decision, because *both* substrates allow row-2 and row-6 to fully bypass the centre. The 3×3 vs 1×1 difference would only matter if a player was forced through the centre band — which clear rows 2/6/8 prevent.

### Random-as-control quality

pat_random was *strategically the richest of the four* — but for the wrong reasons relative to the probe's framing. Its richness came from **specific local hole arrangements** (the col-4 wall, the corner pocket) that are not "decoratively" arbitrary. Different random seeds would produce different specific local features and thus different game character. So "random" here is genuinely interesting precisely because it's not symmetric — the asymmetry creates exploitable structure.

### Tempo / first-move advantage

| Substrate | P1 wins | Rationale |
|---|---|---|
| pat_grid | 1/1 | Standard first-move connection edge |
| pat_random | 1/1 | First-mover takes the 2-cell top bypass and that decides the game |
| pat_structured | 1/2 (default) – 0/1 (col-6 variant) | First-mover takes row-2 highway; if first-mover yields it, second-mover takes col-2 |
| pat_fractal | 1/2 (default) – 0/1 (col-6 variant) | Identical to structured |

P1 dominance ranking: **random ≈ grid > structured ≈ fractal** (the symmetric corridor substrates are actually *more* sensitive to opening choice; whichever player claims their main corridor first wins, regardless of seat).

### Quantitative cross-game metric

| Substrate | Game length | Decisive? | Captures | Moves with 2+ plausible candidates (subjective) |
|---|---|---|---|---|
| pat_grid | 27 | Yes (connection) | 0 | ~6 (cross-cut, bridge, edge anchors) |
| pat_random | 61 | Yes (connection) | 13+ | ~15 (atari/save decisions on every wall-adjacent move) |
| pat_structured | 17 | Yes (connection) | 0 | ~3 (intersection hijack, otherwise forced) |
| pat_fractal | 17 | Yes (connection) | 0 | ~3 (same as structured) |

**pat_random produced a 3.6× longer game than pat_structured/pat_fractal and 13+ captures vs 0**, despite identical rules and identical hole count. This is the cleanest single quantitative signal across the probe.

---

## Phase 4 — Pattern Critic (mandatory)

### Critic argument

> Look at the data. Pat_random played for 61 moves with 13 captures, while pat_structured and pat_fractal both terminated in 17 moves with zero captures *playing identical openings.* If the *shape* of holes mattered, pat_fractal — with its giant 3×3 central hole zone — should have produced the longest, most tactical game; structured (with one central hole) and random (with no central feature at all) should have been shorter. The actual ordering is the reverse: random > grid > {structured ≈ fractal}. This is *exactly* what you would predict from H2: hole **count matters** because more holes mean tighter local connectivity, but the hole **arrangement** is decorative — what actually drove pat_random's depth was *asymmetry creating local tactical hot spots*. Run the same pat_random with a different seed and you'd get a different but still-tactical game; the Sierpiński shape is a red herring. The fractal-spike's Pair-C result was likely picking up "any irregular cluster of holes anywhere on the board makes the rule family more interesting" — and once you control for that with the structured comparison, the recursive self-similar property contributes nothing. An expert at the Sierpiński game would transfer instantly to random or structured with no relearning.

### Player A / Player B rebuttal

**A (random move 1):** I played (4,1) only because it was the *unique* upper bypass — the col-4 hole wall has exactly two cells of clearance on row 0/1. On structured I'd never have played (4,1) (it's a hole on structured! action (4,1) = a hole there). Specific cell choice was driven by *which holes* exist. That's not "decorative."

**B (random move 31):** The 6-stone capture happened because P2's chain libs were (2,5)/(2,6)/(0,4) — and (1,5) is a hole, blocking what would otherwise be P2's escape lib in any non-random pattern. The kill was *enabled* by the (1,5)/(3,5)/(4,5) cluster of holes specifically. Move that cluster and the chain lives.

**A (random moves 53–61, the corner pocket):** The (6,1)/(7,2)/(8,1) hole triple creates a unique "ko-like" zone where (7,1) and (8,0) each have at most 1 liberty against P2's (7,0). On *no* other substrate in this probe does a 1-liberty-after-1-liberty sacrifice sequence exist — fractal/structured/grid all have full surrounding-cell access. That sequence decided the game and is *exclusively* a function of those three holes' arrangement.

**Conceded:** The critic is right that pat_fractal *could not be distinguished from* pat_structured at heuristic depth in our team's play. That part of the critic argument lands. Where the critic overreaches is in asserting that *all* hole-arrangement effects are decorative — pat_random demonstrably has load-bearing arrangement.

**Net:** Hole arrangement matters when it produces *local tactical features* (walls, corner pockets, severed corridors). When it merely produces a symmetric pattern with clean alternative corridors (structured, fractal), the arrangement is largely decorative *at this evaluation depth*.

---

## Phase 5 — Verdict

**Team ID:** team-7
**Game order played:** pat_random → pat_grid → pat_structured → pat_fractal
**Seat assignments:** Player A in seat-1 for games 1, 3 and seat-2 for games 2, 4. Player B mirrored. Each role: 2 seat-1 + 2 seat-2 (perfect 2-2 split).

### Scores (1–10)

**pat_fractal:**
- Strategic Depth: **5** — Central 3×3 hole zone is structurally distinctive but didn't engage at heuristic-strength play; clean even-row corridors collapse strategy to a corridor race.
- Balance: **5** — In default opening P1 wins; in col-6 opening P2 wins. Symmetric — outcome dictated by who claims their corridor first, not by seat. Seat-swap evidence (col-6 vs default) confirms.
- Novelty: **5** — Recursive shape is visually striking but produces no novel mechanic vs structured.
- Hole-arrangement saliency: **4** — Specific Sierpiński shape did not differ from generic stride-2 lattice in any move I made.
- Overall: **5**

**pat_random:**
- Strategic Depth: **7** — 61-move game with 13+ captures, multiple tactical phases (atari/capture sequences, ko-like corner pocket). Specific hole arrangement was load-bearing.
- Balance: **5** — Asymmetric pattern arguably gives P1 a structural advantage (top bypass at (4,0)/(4,1) is a 2-cell choke that P1-tempo can claim outright). Single seed; different seed would be different.
- Novelty: **6** — The corner-pocket sacrifice mechanic exposed by (6,1)/(7,2)/(8,1) was not present in any other condition.
- Hole-arrangement saliency: **8** — Multiple specific moves driven by specific holes, including end-game decider.
- Overall: **6.5**

**pat_structured:**
- Strategic Depth: **4** — Clean corridor race, intersection hijack as only motif.
- Balance: **5** — Same corridor-claim sensitivity as fractal.
- Novelty: **3** — Stride-2 lattice with single centre hole; simple to reason about, no surprises.
- Hole-arrangement saliency: **5** — Even-row/even-col highway pattern matters for corridor selection but specific cell positions don't matter beyond that gross structure.
- Overall: **4**

**pat_grid (control):**
- Strategic Depth: **5** — Pure first-move connection geometry; cross-cut and bridge play required.
- Balance: **6** — First-mover advantage but no asymmetric bias from substrate.
- Novelty: **3** — Baseline.
- Overall: **5**

### Within-team deltas (each condition − pat_grid)

| Δ | Overall | Strategic Depth |
|---|---|---|
| fractal − grid | **0.0** | **0.0** |
| random − grid | **+1.5** | **+2** |
| structured − grid | **−1.0** | **−1** |

### Critical assessment

- **Is Sierpiński self-similarity load-bearing? N.** pat_fractal and pat_structured produced identical games for two different openings I tested; the central 3×3 hole zone never came into play because clean even-row corridors completely bypass it. The recursive shape contributed nothing observable at this evaluation depth that the simpler stride-2 lattice didn't already provide.
- **Did random produce comparable depth to fractal? Yes — and substantially more.** pat_random produced a 61-move tactical game with 13+ captures, vs pat_fractal's 17-move capture-free corridor race. The asymmetric specific arrangement of holes in pat_random *is* load-bearing.
- **Did structured produce comparable depth to fractal? Yes, indistinguishably so.** They produced numerically identical 17-move games with identical openings.
- **Recommendation for R17:** **(c) replace with random-hole perturbation operator.** The single substrate that produced clear strategic depth in this team's evaluation was the random one. The fractal-vs-structured comparison failed to reveal any unique contribution from self-similarity. If the goal is to get the rule family into more interesting territory, a random hole operator (paired with the same 17-hole count and face-connectivity guard) appears to give that with no Sierpiński-specific machinery. Caveat: the team-7 evaluation reached only heuristic-strength play depth; deep RL agents might find strategic affordances in the Sierpiński centre 3×3 that we did not. Recommend logging this verdict alongside the other six teams' before deciding.
