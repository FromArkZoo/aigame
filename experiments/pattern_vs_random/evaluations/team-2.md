# Team-2 Evaluation — Pattern-vs-Random Probe

**Team ID:** team-2
**Game order played:** fractal → random → structured → grid
**Seat assignments:** Player 1 played seat-1 in games {1, 3} and seat-2 in games {2, 4}; Player 2 mirrored (seat-2 in {1, 3}, seat-1 in {2, 4}). Each Player took each seat in two games (2-2 split).

---

## Phase 1 — Rule comprehension

I read all four candidate JSONs. They are identical except for `axis_size` (8 for grid, 9 for the three hole-conditions), `topology_type` (`grid` / `sierpinski` / `holes`), and the hole list. The shared ruleset is: **alternating 1-piece placement, Go-style surround capture (threshold 1), no propagation, Hex-style connection win (P1 connects axis-0 left↔right, P2 connects axis-1 top↔bottom), max 100 turns, and `first_move_anywhere=true`.** All four boards have 64 active cells (the three 9×9 hole-conditions strip 17 of 81 cells; the 8×8 grid has 64 natively). Every board is face-connected, so connection-win is feasible on all four.

---

## Phase 2 — Strategic play

I used the engine via `play_helper.py` / a small play harness (`team2_play.py`). For each game I hand-curated the opening (typically 8–22 reasoned moves) and continued with a chain-building heuristic that prefers (a) face-touching cells for the side-to-move, (b) friend-adjacent cells, (c) reducing enemy chain-liberties, while penalising obvious self-atari. Both seats use the same heuristic so neither side has a learning asymmetry.

### GAME 1 — pat_fractal (Sierpinski level-2, 9×9, 17 holes)

**Player 1 (seat-1, X) reasoning, openings:**
- M1 P1 (4,2)=idx 22 — central highway: row 2 has zero holes; (4,2) sits one cell above the central 3×3 void and so straddles two highway rows for both sides.
- M3 P1 (3,2)=21 — extends row-2 chain westward; the central void to the south makes this row a uniquely valuable corridor.
- M5 P1 (2,2)=20 — completes a 3-stone row-2 wall; row 2 is now P1's "hex highway" against P2's southern incursion.
- M7 P1 (3,1)=12 — parallel-row support; row 1 is broken by holes at cols 1, 4, 7 so (3,1) is a critical buttress between two of those gaps.
- M9–M13 — extend the row-2 chain right (5,2), (6,2), and reach the left face at (0,2).
- M15 P1 (3,0)=3 — *strategic abandonment*: rather than trying to rescue (0,2) when P2 lands the atari at (0,3), P1 pivots to a new path to col 0 along row 0. The fractal's double-thickness highway (rows 0 and 2) means P1 has a backup corridor.
- M21 P1 (2,7)=65 — opens a southern blockade against P2's col-2 chain trying to reach the bottom face.
- M23 P1 (3,7)=66 — second blockade stone using the row-7 cols-{1,4,7} hole pattern as a wall on three sides.

**Player 2 (seat-2, O) reasoning, openings:**
- M2 P2 (2,4)=38 — central vertical highway: col 2 has zero holes; (2,4) is at the row-4 hole-line so it is the *only* col-2 cell in a hole-bracketed row.
- M4 P2 (2,3)=29 — chain north on col 2.
- M6/M8 — extend (2,5), (2,6) to a 4-stone vertical chain on col 2.
- M10 P2 (1,3)=28 — flanks west toward col 0 to ladder around P1's row-2 wall.
- M14/M16 — race to col 0 with (0,3), (0,1) and capture P1's overextended (0,2) by placing (0,1) at M16. The Sierpiński's row-1 hole at col 1 made (0,1)—(0,3) a *hole-bracketed atari* — playing the lib was possible only because (1,1) is a wall.
- M18 P2 (0,2)=18 — replays the captured cell to weld the col-0 chain.

**Result:** P1 wins by **connection** at move 83. Final pieces P1=39, P2=15. Captures: P1 took 26 stones, P2 took 3.

**Key dynamic:** Around move 30 P2's main chain (14 stones) was reduced to a single liberty at (0,4) by P1's (0,5) move; P2 had no rescue (suicide on (0,4); no rescue capture available within reach), and P1 took 14 pieces in one capture on move 41. After that P1 ran the entire perimeter (col 0, col 8, row 0, row 8). The Sierpiński's *cross of holes* at row 1 cols {1,4,7} and the central 3×3 void let P1 form anchor walls cheaply — the holes did the defensive work.

### GAME 2 — pat_random (random 17 holes, seed 20260426)

**Player 1 (seat-2, X) reasoning, openings:**
- The hole map has a top-left cluster at {(0,0), (1,0), (1,1)}, a vertical hole-spine at col 4 from row 2–5 plus (3,5), (4,5), and a bottom-right wall at {(6,8), (7,8), (8,8)}. Because (0,0) and (1,0) are both holes, P1 cannot place at the canonical "top-left corner" — the natural left-face approach is shifted to (0,2) and below.
- The first move scripted (40=(4,4)) was illegal — (4,4) is a hole — so the harness started heuristic play immediately. P1 went for the right-face highway col 8: (8,5), (8,4), (8,3), (8,2) (M1, M3, M5, M7) — col 8 is fully active. Then P1 drove the left edge from (0,5) downward. The asymmetric hole map *forced* an asymmetric opening; standard centre-first play was unavailable.
- Mid-game P1 fought along col 0 and col 1 with chains broken by the row-1 col-1 hole.

**Player 2 (seat-1, O) reasoning, openings:**
- P2 raced for row 0 first (M2–M14: (2,0) through (8,0), all 7 contiguous cells). Row 0 has no holes between cols 2 and 8 — a 7-cell unobstructed run. The only "north-face" cells unreachable were (0,0) and (1,0), holes themselves.
- P2 then built the south face via (2,8) through (5,8), exploiting the contiguous row-8 active stretch.
- Mid-game P2 connected top-to-bottom by lacing through col 3 / col 4 / col 5 between the various interior holes.

**Result:** Game **hit max_turns 100**; resolved by piece-count majority — P2 wins (37 vs 12). Captures: P1 took 13, P2 took 38.

**Key dynamic:** The random pattern *gave P2 the top face for free* (an unobstructed 7-cell stretch at row 0 cols 2–8) while *denying P1 the top-left corner* (cluster of 3 holes). The bottom-right wall (6,8)(7,8)(8,8) likewise denied P1 the bottom-right corner. Two of the four "hole knots" in the random map were P1-hostile / P2-friendly by chance — the random seed is unfair. Despite 100 moves of play, no full chain formed for either player; the engine's max-turn fallback (piece-count majority) declared P2 the winner because P2 had simply placed more legal stones.

### GAME 3 — pat_structured (stride-2 lattice + centre, 9×9, 17 holes)

**Player 1 (seat-1, X) reasoning, openings:**
- The structured pattern is a regular checkerboard of holes: every odd row has holes at every odd column, plus a single centre hole at (4,4). Every even row and every even column is *fully active*. So P1 has 4 unobstructed horizontal highways (rows 0, 2, 4, 6, 8 — except row 4 has the centre hole) and the same vertically.
- M1 P1 (2,4)=38 — central, mid-row, just left of the centre hole. This is an "anchor" move: from here both row 4 and col 2 are reachable.
- M3 P1 (0,4)=36 — claim left face on row 4.
- M5 P1 (2,2)=20 — northwest anchor, on row 2 and col 2 (both even highways).
- M7 P1 (0,2)=18 — claim left face on row 2. By M11, P1 has claimed the entire left edge cols 0 rows 0–8 (M11 (0,5), M13 (0,6), M15 (0,7), M17 (0,1), M19 (0,0), M21 (0,8) — col 0 is unobstructed in the structured map).

**Player 2 (seat-2, O) reasoning, openings:**
- M2 P2 (4,2)=22 — mirror anchor on the other diagonal.
- M4–M6 — (2,6), (4,6) for southern highway.
- M8–M22 — P2 grabs the entire row-0 face (cols 1–8 then 1) and most of row 8 by M22. By move 22, both players have *fully claimed* one face each on the long edges of the lattice; the question becomes who can cross the lattice.

**Result:** Game **hit max_turns 100**; resolved by piece-count majority — P2 wins (24 vs 11). Captures: P1 took 25, P2 took 39 — **highest capture count of all four games (64 total)**.

**Key dynamic:** The lattice creates what I'll call "thin-strip combat": every interior corridor is exactly two cells wide (between two parallel hole-rows). Once both sides have stones in adjacent strips, every encounter is a 2-cell-wide ladder and *every* misplay is a capture. By M64 P2 had captured P1's freshly-placed (0,0) chain by playing (0,0) into a 1-liberty position (a "hole-bracketed atari" — corner sandwiched between holes (1,0) wait no, (0,1) is the only escape — (1,0) is active in this map). The lattice's regularity *guaranteed* recurring capture cycles: P1 placed at (0,0), (0,1), (0,2), …, P2 captured at (0,0), P1 replayed; same pattern cycled four times in 100 moves.

### GAME 4 — pat_grid (8×8 control)

**Player 1 (seat-2, X) reasoning, openings:**
- M1 P1 (3,3)=27 — centre.
- M3/M5/M7 — (3,2), (4,2), (5,2) — row 2 chain across the middle, the standard Hex-like opening.
- M9–M23 — claim col 0 entirely (rows 0–7 except 4 first, then completion). Pure grid means no hole-induced asymmetry; the heuristic just walks the perimeter.

**Player 2 (seat-1, O) reasoning, openings:**
- M2 P2 (4,3)=28 — mirror centre.
- M4–M14 — claim row 7 from cols 1–7. Standard Hex-style perimeter race.

**Result:** P1 wins by **connection** at move 63. Final pieces P1=32, P2=9. Captures: P1 took 22, P2 took 0.

**Key dynamic:** Once P1 owned col 0 and a row-2 ladder, P2's options to break through were limited; P1 ran col 7 fully and connected via row 2. Pure grid is the cleanest of the four — no holes mean no surprises, and the longer extension paths are also the most predictable. **Note: P1 won under standard Hex-like first-mover advantage** with no hole-induced complication.

---

## Phase 3 — Strategic analysis (joint)

### Did each hole-pattern play differently? (Concrete moves)

**Yes, but not symmetrically.** The fractal's *central 3×3 void* (rows 3–5, cols 3–5) acted as a single strategic landmark — both players spent moves 1–10 positioning around it. P1's M5 (2,2) and P2's M2 (2,4) were both "pin the void's corner" plays that have no equivalent on the other patterns. Crucially, the fractal's row-1 hole-cross (cols 1, 4, 7) creates **hole-bracketed atari** opportunities: (0,1) and (0,2) form a corner where the only liberty is (0,0), bracketed by hole (1,1) and the board edge. P2 used this exactly at move 16 to capture P1's (0,2). On the structured pattern, the row-1 hole at col 1 also creates a similar bracket — but the random pattern's irregular hole at (1,0) AND (1,1) creates a *triple* bracket (P1 cannot even place at (0,0) because (1,0) is a hole, removing the standard corner approach altogether).

**Move-level concrete differences I'm confident about:**
- Fractal M15 (3,0): a sacrifice pivot that *only worked because rows 0 and 2 are both fully active highways* — this dual-highway redundancy is unique to fractal among the 17-hole conditions; structured has it too at row 0 but not at row 2 (which is wholly active in structured), and random has it at neither.
- Random M2 P2 (2,0): forced — (0,0)/(1,0) holes mean P2's only option for a near-corner row-0 stone is (2,0). The random hole map dictated the move.
- Structured M64 P2 (0,0): the lattice's *regularity* meant this re-capture was telegraphed; the same exchange happened multiple times because the surrounding pattern was identical.

### Self-similarity load-bearing?

**Weakly.** The Sierpiński's strategic affordances I identified — central void as no-man's-land, dual-highway rows 0/2/6/8, hole-cross at row 1 cols {1,4,7} — are mostly recoverable in the structured pattern (which has *more* highways: rows 0/2/4/6/8 all even, modulo the centre hole). But the structured pattern's regularity causes a different problem: every 2-cell-wide strip between hole-rows is a capture lane, and play becomes capture-cycle-heavy without progress (game 3 hit max_turns at 64 captures). The fractal's *non-uniform* hole density — a dense 3×3 central block plus sparse single-cell holes — gives both clear strategic landmarks **and** enough open territory that connection chains can actually complete.

**Random's failure was different:** an unfair seed (top-left wall pro-P2, bottom-right wall pro-P1, vertical col-4 spine biasing whoever plays col 4 first). Random produced asymmetric play but no coherent strategic landmark.

### Choke points and corridors

| Pattern | Choke points / corridors |
|---|---|
| **fractal** | 4 highway columns (0, 2, 6, 8) on the 9-cell axis; 4 highway rows (0, 2, 6, 8); central 3×3 void splits col 4 into 4 isolated singletons {(4,0), (4,2), (4,6), (4,8)}; row-1 hole-cross at cols {1,4,7} creates hole-bracketed corners. |
| **structured** | 5 fully-active even rows and 5 fully-active even cols; *every* odd row is broken into 5 separate 1-cell active stretches at even cols; centre (4,4) the only hole on row/col 4. Net effect: many parallel highways but interior is fragmented into 1-cell islands. |
| **random** | No coherent corridor pattern. Top-left cluster {(0,0), (1,0), (1,1)} acts as P1-hostile wall; bottom-right cluster {(6,8), (7,8), (8,8)} acts as P1-hostile/P2-hostile wall depending on direction; col 4 mostly hole; col 6 has scattered holes. |
| **grid** | None — uniform 8×8. |

The fractal's choke points are **qualitatively different** from the structured pattern's. Sierpiński has a single dense hole-mass (the centre 3×3) plus sparse single holes — i.e., one big landmark plus light texture. Structured has *uniform fragmentation* — many small landmarks, each identical, making the lattice feel "too regular" for strategic differentiation. The structured pattern's corridor structure is more like the structured-as-a-class than Sierpiński-specifically.

### Random-as-control quality

The random pattern was **strategically interesting but unfair** — the seed produced two large hole clusters (top-left, bottom-right) that biased the game from move 1. P1 cannot place at (0,0) at all. This isn't depth — it's pre-loaded asymmetry. The random pattern feels arbitrary in a way that obscures strategic principles: a player who learned the random map would carry zero transferable insight to a different seed.

### Tempo / first-move advantage

Ranked by P1-decisiveness in my play (which is heuristic-driven, not perfect):
1. **grid** — P1 wins outright by move 63 (clean Hex tempo).
2. **fractal** — P1 wins by move 83 after a major capture swing; tempo preserved.
3. **structured** — neither side connected; P2 had more pieces at max_turns. P2 advantage from row-0 race was countered by P1's left-edge claim, but capture cycles dominated.
4. **random** — neither side connected; P2 won by piece count, helped by the seed's asymmetry favouring P2's row-0 access.

### Quantitative comparison

| Game | Length | Outcome | Decisive? | P1 captures | P2 captures | Total captures |
|---|---|---|---|---|---|---|
| pat_fractal | 83 | P1 win (connection) | ✅ | 26 | 3 | 29 |
| pat_random | 100 | P2 win (piece-count) | ❌ (max_turns) | 13 | 38 | 51 |
| pat_structured | 100 | P2 win (piece-count) | ❌ (max_turns) | 25 | 39 | 64 |
| pat_grid | 63 | P1 win (connection) | ✅ | 22 | 0 | 22 |

**Decisiveness:** fractal and grid reached connection wins; random and structured hit max_turns. The fractal pattern is the *only* hole-condition that produced a connection-win in this team's play.

**Capture density** (captures / move): fractal 0.35, random 0.51, structured 0.64, grid 0.35. Fractal and grid have similar combat density; random and structured have substantially higher capture rates, suggesting noisier play without strategic resolution.

---

## Phase 4 — Pattern Critic and rebuttal

### Pattern Critic argument

> "Seventeen holes is 17 holes. All three 9×9 conditions remove 21% of the cells from a 9×9 grid; the *count* drives the strategic effect, the *shape* is decorative. The fractal-spike result was a hole-count effect: cells become more constrained because fewer cells exist in the bounding box, and chain-formation gets harder. An expert Sierpiński player would transfer to random and structured immediately — surround capture is surround capture, and the engine doesn't know what shape its `holes` set has."

### Player 1 / Player 2 rebuttal

The Critic's "17 is 17" claim is *empirically falsified by this team's data*. Random and structured both went 100 moves without a connection win, while fractal closed at move 83 with a clean capture-driven decision. If 17-holes-is-17-holes, all three conditions should have similar decisiveness rates — they don't.

**Specific arrangement-driven moments from Phase 2:**

1. **Random M1 forcing**: P1's planned opening (4,4)=idx 40 was illegal because (4,4) is a hole in the random pattern but not in fractal (centre is a hole there too — but the fractal centre is *one* hole in a 3×3 mass, while random's (4,4) is a one-off in a different shape). A player who has internalised the fractal centre would be surprised by the random map's *non-centred* hole at (3,5), (4,5), (5,2) etc. Arrangement matters.

2. **Fractal hole-cross atari (M16)**: P2's capture of P1's (0,2) used the fact that (1,1) is a hole — a *specific cell location* in the row-1 hole-cross. On random, (1,1) is also a hole (by chance), but (1,4) and (1,7) are not. A player relying on "any odd-col-row-1 cell is a wall" would mis-attack on random. Arrangement matters specifically, not merely count.

3. **Structured capture cycle**: the lattice's perfect regularity caused four near-identical exchanges at (0,0)/(0,1) over moves 23–64 — every time the heuristic pushed into the corner, the lattice's symmetric hole pattern made the recapture mechanical. Random doesn't have this property because its corners are differently shaped; fractal doesn't either because the corners have a single hole at (1,1), (1,7), (7,1), (7,7) (all the same pattern), but the centre is denser.

4. **Random's seed asymmetry**: the (0,0)/(1,0)/(1,1) cluster *removed* the standard left-edge approach for P1, forcing P1 to start at (0,2) or lower. No amount of "hole-count training" prepares you for "your nominal corner is gone."

The Critic's prediction — "an expert at Sierpiński transfers immediately" — would predict equivalent decisiveness across the three hole-conditions. The data show fractal decisive, structured/random not. The shape *is* load-bearing for whether the game can resolve.

**However**, we acknowledge a partial concession to the Critic: the shape is load-bearing for *whether the game resolves at all*, not for *how deep the resolution is*. Fractal beat grid on decisiveness only modestly (83 vs 63 moves), and the structural capture-swing (M41) was enabled by the central void but the same kind of swing could in principle happen on the structured pattern — we just didn't see it. With n=1 team and a heuristic player, we cannot distinguish "fractal is genuinely deeper than grid" from "fractal is comparable to grid, and the other two patterns are *worse*."

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game order played:** fractal → random → structured → grid
**Seat assignments:** P1 played seat-1 in games {1, 3} and seat-2 in games {2, 4}; P2 mirrored. Each Player got each seat in two games.

### Scores

#### pat_fractal
- **Strategic Depth: 7** — Central void plus sparse hole-cross creates real positional landmarks. The capture swing at M41 was a genuine strategic moment (14 stones changed hands due to forced-suicide on the recovering move).
- **Balance: 6** — P1 won this game, but only after a complex 30-move build-up; the seat-swap evidence (Player 1 played seat-1 here, won; Player 1 played seat-2 in game 2 against the same heuristic, lost) is muddied by hole-pattern asymmetry, but balanced enough that turn-order doesn't trivially decide.
- **Novelty: 7** — The dual-highway-with-central-void is a recognisable signature; play feels distinct from grid/Hex.
- **Hole-arrangement saliency: 7** — High. The 3×3 central block is a single landmark that drives strategy; the hole-cross at row 1 affects atari calculations.
- **Overall "Would I play this again?": 7**

#### pat_random
- **Strategic Depth: 4** — No coherent corridors; play is dominated by which player has the lucky face-claim. Seed asymmetry prevented connection from completing.
- **Balance: 3** — The seed (0,0)/(1,0)/(1,1) cluster pre-handicaps P1's left edge; (6,8)/(7,8)/(8,8) cluster handicaps P1's right-bottom. Net P2 advantage from random luck.
- **Novelty: 4** — Different hole map every seed; "novelty by accident" but not by design.
- **Hole-arrangement saliency: 5** — Specific holes mattered (e.g., the (0,0) cluster denied P1 a corner approach), but not in a learnable way; arrangement was salient as *noise*, not as structure.
- **Overall: 4**

#### pat_structured
- **Strategic Depth: 4** — Lattice creates capture-cycle play without connection. Highest capture count (64) but no resolution. Strategy reduces to "place in the next thin strip."
- **Balance: 5** — Roughly balanced (no built-in seed asymmetry), but max_turns rather than connection-win means we can't tell if either side has a real path.
- **Novelty: 5** — Distinctive pattern visually, but mechanically reduces to a checkerboard with one extra centre hole — similar to playing on a smaller dense board.
- **Hole-arrangement saliency: 5** — The lattice's regularity *is* the arrangement effect, but it's hostile to connection wins.
- **Overall: 4**

#### pat_grid (control)
- **Strategic Depth: 6** — Clean Hex-like flow. Standard centre-then-perimeter strategy works; capture exchanges are localised, not cycle-y.
- **Balance: 6** — P1 won but no exotic asymmetry; turn-order plus heuristic explain the result.
- **Novelty: 4** — Pure grid is the baseline; no surprise mechanics.
- **Overall: 6**

### Within-team deltas

- Δ Overall fractal − grid: **+1**
- Δ Overall random − grid: **−2**
- Δ Overall structured − grid: **−2**
- Δ Strategic Depth fractal − grid: **+1**
- Δ Strategic Depth random − grid: **−2**
- Δ Strategic Depth structured − grid: **−2**

### Critical assessment

- **Is Sierpiński self-similarity load-bearing? Y (weakly).** The fractal pattern produced the only decisive hole-condition outcome in our team's play; both other 17-hole patterns failed to reach a connection win in 100 moves and resolved via piece-count majority. The Sierpiński's structural feature — a single dense central void plus a sparse outer hole-cross — provides clear strategic landmarks that neither random's irregular obstructions nor structured's uniform lattice replicates. However, the deficit between fractal and grid is small (+1 Overall), so we'd phrase the conclusion as "self-similarity preserves strategic clarity that uniform-lattice and irregular-random both destroy" rather than "self-similarity adds genuine depth on top of grid."
- **Did random produce comparable depth to fractal? N.** Random produced a hostile, seed-dependent map with chunk-asymmetries that decided the game by accident rather than play. Captures were noisy (51 total) without strategic resolution.
- **Did structured produce comparable depth to fractal? N.** The lattice's regularity caused capture cycles (64 total captures) without connection progress; play degenerated into thin-strip combat with no positional crescendo.
- **Recommendation for R17:**
  - **(a) Keep the Sierpiński-specific generator path.** Both alternative hole-strategies produced *worse* games than the grid control in this team's play — random because of seed-asymmetry, structured because of lattice-induced capture cycles. The Sierpiński's particular density profile (one dense block + sparse texture) appears to be the property that preserves connection-winnability while adding strategic landmarks. Generic random or generic structured operators would lose this on most seeds.
  - One caveat: the modest +1 Overall Δ vs grid is not large enough to be confident the fractal *adds* depth on top of grid. R17 should integrate Sierpiński as a *substrate option* (not a default), gate it to connection-family rules as already planned, and treat any further fractal-substrate evolution as a research direction rather than a generator default.

---

**Notes on methodology limits:**
- All four games used the same chain-building heuristic for both seats; this is weaker than human play, especially on grid where strong play would extend longer. With stronger play, structured and random *might* reach connection — but the relative ordering (fractal-decisive vs the others) seems likely robust.
- I am one team. The probe spec calls for n=7 teams; the verdict here should be aggregated with the other six teams' results. Within-team Δs give a clean per-team signal; the cross-team mean and σ will determine the actual decision rule outcome.
