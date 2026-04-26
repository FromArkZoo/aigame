# Team-4 Evaluation — Pattern-vs-Random Probe

**Team ID:** team-4
**Game order played:** structured → grid → fractal → random
**Seat assignments:**
- Player A: P1 in games {1, 3} (structured, fractal); P2 in games {2, 4} (grid, random)
- Player B: P2 in games {1, 3} (structured, fractal); P1 in games {2, 4} (grid, random)
- Each player: 2 seats P1, 2 seats P2 (perfect 2–2 balance)

---

## Phase 1 — Rule Comprehension

All four candidates share the **identical** rule core: 2D, alternating turns, place-only (1 piece/turn), surround-capture (Go-style, threshold 1), no propagation, **connection win** — P1 must connect axis-0 faces (left↔right, x=0 to x=axis-1), P2 must connect axis-1 faces (top↔bottom, y=0 to y=axis-1), max 100 turns. The only differences are (i) `topology_type` (`grid` vs `holes` vs `sierpinski`), (ii) `axis_size` (8 for grid; 9 for the three hole-bearing variants), and (iii) the `holes` list (or implicit Sierpiński hole set). All four substrates are face-connected, all have 64 active cells, and all use von Neumann adjacency over the active subgraph.

---

## Phase 2 — Strategic Play

I drove the engine via `play_helper.py` / a minimal driver script (`/tmp/play_driver.py`) replaying move sequences against `GameDefV2.from_dict`. Action ID = `y * axis_size + x`. Both players reasoned move-by-move. Cell coordinates below are written `(x, y)`.

### Game 1 — pat_structured (Player A = P1, Player B = P2) — 17 moves, P1 wins by row-2 chain

Structured pattern: stride-2 lattice of holes on odd rows/odd cols, plus a single centre hole at (4, 4). Even rows {0, 2, 6, 8} are 9-cell open highways; even cols {0, 2, 6, 8} are 9-cell vertical highways. Odd-row even-col cells like (2, 1) are *pinch* cells — only N–S extensions remain because their col±1 neighbours are holes.

| # | Side | Move | Reasoning |
|---|------|------|-----------|
| 1 | P1 (A) | (4, 2) = 22 | Anchor on the central row-2 horizontal highway. Four active neighbours, max optionality. |
| 2 | P2 (B) | (2, 4) = 38 | Symmetric: anchor central col-2 vertical highway. |
| 3 | P1 (A) | (2, 2) = 20 | **Dual-purpose**: occupies col-2 above P2's anchor (kills P2's natural northbound chain) AND extends own row-2 stake westward. |
| 4 | P2 (B) | (6, 4) = 42 | Col-2 north is closed; pivot to a fresh vertical highway on col-6. |
| 5 | P1 (A) | (6, 2) = 24 | **Dual-purpose again**: cuts P2's col-6 *and* reserves row-2 east. The structured lattice rewards exactly these row-col intersection plays. |
| 6 | P2 (B) | (6, 3) = 33 | Tries to reach (6, 2) from below; (6, 3) joins the col-6 chain. Its row-3 lateral exits (5, 3)/(7, 3) are *both holes*, so the chain is permanently single-thick here. |
| 7 | P1 (A) | (5, 2) = 23 | Bridge between (4, 2) and (6, 2). (5, 1)/(5, 3) are both holes — once placed, the 3-stone group is fully *interior* with no own liberties at this stone. |
| 8 | P2 (B) | (6, 5) = 51 | Continue col-6 south; (5, 5)/(7, 5) are both holes — same single-thick pattern as move 6. |
| 9 | P1 (A) | (3, 2) = 21 | Bridges (2, 2) and (4, 2). Row-2 chain is now (2,2)–(3,2)–(4,2)–(5,2)–(6,2). |
| 10 | P2 (B) | (6, 6) = 60 | Col-6 reaches y=6 — first lateral exits since (5,6)/(7,6) are clear. |
| 11 | P1 (A) | (7, 2) = 25 | Extend east. (7, 1)/(7, 3) are holes → again a pinch cell. |
| 12 | P2 (B) | (6, 7) = 69 | Continue south. |
| 13 | P1 (A) | (8, 2) = 26 | Reach right edge (x=8). Row-2 chain now spans (2,2)–(8,2). Left edge still pending. |
| 14 | P2 (B) | (6, 8) = 78 | P2 col-6 chain spans y=3–8 (south done), but y=0,1,2 forever blocked by my (6,2). |
| 15 | P1 (A) | (1, 2) = 19 | Lateral pinch cell on west side. |
| 16 | P2 (B) | (4, 0) = 4 | Hail-mary new anchor at row 0; no path to current chain. |
| 17 | P1 (A) | (0, 2) = 18 | **Connection complete**: (0,2)–(8,2) spans x=0…8. P1 wins. |

Result: decisive, 17 moves, no captures, 9–8 piece count. Final P1 chain = full row 2.

### Game 2 — pat_grid (Player A = P2, Player B = P1) — 15 moves, P1 wins by row-3 chain

Pure 8×8 grid, zero holes. Standard alternating-turn connection race. Player B is now P1 and goes first.

| # | Side | Move | Reasoning |
|---|------|------|-----------|
| 1 | P1 (B) | (3, 3) = 27 | Centre-of-board anchor. |
| 2 | P2 (A) | (4, 4) = 36 | Adjacent diagonal centre — classic Hex-style mirror. |
| 3 | P1 (B) | (4, 3) = 28 | Push east on row-3, attacks (4,4) liberty. |
| 4 | P2 (A) | (3, 4) = 35 | Block south, anchor own col-3 plan. |
| 5 | P1 (B) | (5, 3) = 29 | Continue row-3 east. |
| 6 | P2 (A) | (3, 5) = 43 | Build col-3 south. |
| 7 | P1 (B) | (2, 3) = 26 | Extend west. |
| 8 | P2 (A) | (3, 6) = 51 | South. |
| 9 | P1 (B) | (1, 3) = 25 | Extend. |
| 10 | P2 (A) | (3, 7) = 59 | Reach bottom edge — P2 has y=4..7 in col-3 but (3,3)=P1 blocks y<4. Same trap as game 1. |
| 11 | P1 (B) | (0, 3) = 24 | Reach left edge. |
| 12 | P2 (A) | (3, 2) = 19 | Try to start a *second* col-3 piece north of P1's wall. Disconnected. |
| 13 | P1 (B) | (6, 3) = 30 | Extend east. |
| 14 | P2 (A) | (3, 1) = 11 | Continue north anchor. Still disconnected; P2 needs y=0 *and* a connection across (3,3)=P1. |
| 15 | P1 (B) | (7, 3) = 31 | **Connection complete**: row-3 spans x=0..7. P1 wins. |

Result: decisive, 15 moves, no captures, 8–7 pieces. Pure tempo race; first player wins by one move because they can always respond on their column ahead of P2's.

### Game 3 — pat_fractal (Player A = P1, Player B = P2) — 17 moves, P1 wins by row-2 chain

Sierpiński level-2: solid 3×3 block at the centre (rows 3–5, cols 3–5) plus eight isolated single-cell holes at (1,1),(4,1),(7,1),(1,4),(7,4),(1,7),(4,7),(7,7). Crucially, **rows 0, 2, 6, 8 are entirely hole-free** — any of them is a 9-cell highway. Same for cols 0, 2, 6, 8.

I deliberately ran the same template as game 1 to test whether the fractal arrangement makes any difference at all on the row-2 highway:

| # | Side | Move | Reasoning |
|---|------|------|-----------|
| 1 | P1 (A) | (4, 2) = 22 | Row-2 anchor. (4, 2) has 4 active neighbours — fully unblocked. |
| 2 | P2 (B) | (2, 4) = 38 | Col-2 anchor. (2, 4)'s east neighbour (3, 4) is a hole; west (1, 4) is a hole; on the *fractal*, this anchor is *more* isolated than its structured-pattern equivalent (which had clear E/W). |
| 3 | P1 (A) | (2, 2) = 20 | Dual-purpose, same as game 1. |
| 4 | P2 (B) | (2, 5) = 47 | Forced south because (2, 3) is OK but (2, 2)=P1 already blocks north — extend south of (2, 4). Note (3, 5) and (1, 5) are clear in fractal (only (3,5) is a hole — wait, (1,5) IS clear in fractal). |
| 5 | P1 (A) | (6, 2) = 24 | Block col-6 *and* reserve row-2 east. |
| 6 | P2 (B) | (2, 6) = 56 | Continue south. |
| 7 | P1 (A) | (3, 2) = 21 | Bridge. |
| 8 | P2 (B) | (2, 7) = 65 | Continue south. (1,7)=hole, (3,7) clear. |
| 9 | P1 (A) | (5, 2) = 23 | Bridge. |
| 10 | P2 (B) | (2, 8) = 74 | South edge reached. P2 has col-2 from y=4..8 — 5 cells; needs y=0..3 still, but (2,2)=P1 wall. |
| 11 | P1 (A) | (1, 2) = 19 | Extend west. |
| 12 | P2 (B) | (2, 3) = 29 | Try to push north of (2, 4); but (2,3) is then adjacent to (2,2)=P1 — interior to P1's pocket. |
| 13 | P1 (A) | (7, 2) = 25 | Extend east. |
| 14 | P2 (B) | (1, 3) = 28 | Try to break out laterally toward col-1/col-0. (1, 3) is adjacent to (1, 4)=hole and (1, 2)=P1. Limited routing. |
| 15 | P1 (A) | (0, 2) = 18 | Left edge. Chain (0,2)–(7,2), need x=8. |
| 16 | P2 (B) | (0, 3) = 27 | Try to wrap around west. |
| 17 | P1 (A) | (8, 2) = 26 | **Connection complete**. P1 wins. |

Result: decisive, 17 moves, no captures, 9–8 pieces — **identical move count to game 1 (structured)**. The fractal's central 3×3 block was *visible from row 2 but never touched*: my chain ran along y=2, the entire central block sits at y=3..5. The fractal's row-2 cells have *exactly the same* local neighbourhood as the structured pattern's row-2 cells (4 neighbours each, except none of row 2's cells are adjacent to the central block). Self-similarity was visually distinct but strategically *invisible*.

### Game 4 — pat_random (Player A = P2, Player B = P1) — 21 moves, P1 wins by row-7+row-6 detour

Random 17 holes (seed 20260426). The pattern has a **structural feature absent from the other three**: a 4-cell **vertical wall in column 4** at rows 2, 3, 4, 5. This makes every row in y∈{2..5} *broken at x=4*. There are also clusters at top-left (0,0)/(1,0)/(1,1), bottom-right (6,8)/(7,8)/(8,8), and isolated blockers at (6,1)/(8,1)/(6,2)/(7,2)/(1,5)/(3,5)/(8,6).

**Row 7 is the only fully-clean horizontal row** (no holes anywhere in row 7). Row 8 has a 3-cell hole cluster on the right; row 6 has one hole at (8,6). Row 0 has the (0,0)/(1,0) cluster; row 1 is heavily perforated. So P1's optimal horizontal highway is row 7. P2 (Player A) anticipated this and *broke row 7 directly*.

| # | Side | Move | Reasoning |
|---|------|------|-----------|
| 1 | P1 (B) | (4, 7) = 67 | Row-7 anchor — *the* clean horizontal highway. Crosses col-4 here because col-4 is impassable at y∈{2..5}. |
| 2 | P2 (A) | (5, 7) = 68 | **Direct row-7 break**: P2 reads my plan and inserts a stone east of my anchor. Row 7 is now bisected. |
| 3 | P1 (B) | (3, 7) = 66 | Commit west on row 7; will need to detour around (5,7) for east half. |
| 4 | P2 (A) | (2, 4) = 38 | Switch to col-2 anchor (col-2 is fully hole-free in random — best vertical highway). |
| 5 | P1 (B) | (2, 7) = 65 | Continue west. |
| 6 | P2 (A) | (2, 5) = 47 | Extend col-2 south. |
| 7 | P1 (B) | (1, 7) = 64 | (Note: (1, 7) is a hole in *fractal* but clear in *random* — the same action ID maps to a hole vs. an active cell across substrates, illustrating arrangement matters.) |
| 8 | P2 (A) | (2, 6) = 56 | South. |
| 9 | P1 (B) | (0, 7) = 63 | Left edge reached. West half of row 7 done. |
| 10 | P2 (A) | (2, 3) = 29 | North. |
| 11 | P1 (B) | (4, 6) = 58 | **Detour begin**: drop down from (4,7) to (4,6). My row-7 east route is blocked by (5,7)=P2; row 6 is the next-cleanest row (only (8,6) hole). |
| 12 | P2 (A) | (2, 2) = 20 | North. |
| 13 | P1 (B) | (5, 6) = 59 | Continue east on row 6. |
| 14 | P2 (A) | (2, 1) = 11 | North. |
| 15 | P1 (B) | (6, 6) = 60 | East. |
| 16 | P2 (A) | (2, 0) = 2 | Top edge. P2 col-2 chain spans y=0..6. Needs y=7..8 — but row 7 is *full of P1* and (2,7)=P1 blocks col-2 directly. |
| 17 | P1 (B) | (7, 6) = 61 | East — note (8, 6) is a hole, so I can't simply continue to (8, 6). Need to drop *up* to row 7 again. |
| 18 | P2 (A) | (5, 8) = 77 | Try to start a south-route. (5, 8)→(5, 7)=P2 — connects to the *isolated* (5,7) breaker stone. But P2 still has no path between this y=7..8 segment and the col-2 north chain. |
| 19 | P1 (B) | (7, 7) = 70 | Bridge from (7, 6) up to row 7, around (8, 6) hole. |
| 20 | P2 (A) | (4, 8) = 76 | Try to extend south chain west. Still disconnected from north. |
| 21 | P1 (B) | (8, 7) = 71 | **Connection complete** via (0,7)–(1,7)–(2,7)–(3,7)–(4,7)–(4,6)–(5,6)–(6,6)–(7,6)–(7,7)–(8,7). Note that (8, 6) is a hole and (8, 8) is a hole, so (8, 7) is *only* reachable via (7, 7). The hole-adjacency forced this exact tail. P1 wins. |

Result: decisive, 21 moves, no captures, 11–10 pieces. **Materially longer than the other three games (15, 17, 17).** P1's chain has a non-trivial shape — row 7 west half, then dives to row 6 to bypass P2's breaker, then rises back to row 7 for the right-edge tail because (8, 6) is a hole. This is the only one of the four games where the hole *arrangement* (specifically the col-4 wall + (8,6) corner hole) drove a non-straight winning chain.

---

## Phase 3 — Strategic Analysis

### Did each pattern play differently?

**Yes, but only one of them produced strategically distinct play.**

- **pat_grid (control):** Pure tempo race. Whoever controls the centre row/col wins. No structural decisions — every move is "extend".
- **pat_structured:** Identical macro-strategy to grid (race a horizontal highway), but the stride-2 lattice creates *pinch cells* at odd-row even-col positions — e.g., (5, 2) has neighbours {(4,2), (6,2), hole, hole}. Once placed, a pinch cell has zero own liberties and can be captured only via the chain. **In practice, this never mattered**, because whoever owns row 2 has so many group liberties from the highway that capture is impossible. The structured pattern's *appearance* of strategic features (regular lattice) does not translate to *strategic content*.
- **pat_fractal:** Visually striking (recursive self-similarity), but the row-2 chain literally never touches a fractal hole — the central 3×3 block sits at y=3..5, the perimeter rings of single-cell holes are at y=1, y=4, y=7 only. **Move-for-move identical to structured for my chosen template.** The fractal's central solid block is a *visual* feature that never enters the strategic calculation when an open row exists at distance 1 from the block.
- **pat_random:** **Genuinely different.** The col-4 wall (4 contiguous holes at y=2..5) closes off rows 2, 3, 4, 5 as horizontal options. The (8, 6)/(6, 8)/(7, 8)/(8, 8) corner cluster forces the right-edge tail to come through (7, 7) specifically. P2 had real defensive options because my "best" row (7) was *unique*, not one of four equivalents. The 21-move game vs. 17-move "templated" games is a 24% increase in length driven by hole arrangement.

### Self-similarity load-bearing?

**No.** The Sierpiński carpet's recursive structure was strategically inert in our games. Specifically:

1. **The peripheral ring is unaffected.** Rows 0, 2, 6, 8 and cols 0, 2, 6, 8 are 100% clear. A connection-game player who claims one of these rings wins exactly as on a pure grid. The recursive hole-structure sits *inside* the ring at y=3..5, x=3..5, and is invisible to the chain.
2. **The 3×3 centre block is a *single* obstruction**, no different from any 9-cell hole blob. The fact that it is recursively decomposable into a pattern of nested 3-cell holes is a *naming* property, not a *play* property. A 3×3 solid block of holes plays the same as a 3×3 random arrangement of 9 holes (modulo perimeter shape).
3. **The 8 single-cell holes at (1,1),(4,1),(7,1),(1,4),(7,4),(1,7),(4,7),(7,7)** are positioned at the corners of a 3x3 super-grid. They affect exactly *one* lateral-bridge motif each. None of them came into play in our games.

If self-similarity were truly load-bearing, I'd expect to see strategic affordances — e.g., recursive ladders, fractal ko-fights, scale-invariant corridors — that random/structured patterns can't replicate. **I saw none.** The fractal's strategic content reduces to "there is a big central wall and a few isolated holes near the edges", which structured and random both replicate (or improve on) with their own large walls.

### Choke points and corridors

- **pat_grid:** None. Every cell has 4 neighbours.
- **pat_structured:** ~16 pinch cells at (odd row, even col) and (even row, odd col) positions. Each pinch cell has exactly 2 active neighbours, but they are *paired symmetrically* across the lattice — a chain through one is mirrored by alternatives, so no individual pinch is a true choke.
- **pat_fractal:** Eight single-cell hole-bridges at the corner positions of the super-grid (e.g., (4,1) creates a 1-cell choke between (3,1) and (5,1)). The 3×3 block creates a no-go zone but **no narrow corridor** — you simply route around it via row 2 or row 6 (full highways).
- **pat_random:** **Multiple genuine chokes.** (a) The col-4 wall forces every horizontal chain to cross at y∈{0,1,6,7,8}. (b) The (8,6)+(8,8) hole pair makes (8,7) reachable *only* from (7,7). (c) The (6,8)/(7,8)/(8,8) bottom-right cluster cuts off bottom-right connectivity. (d) The (0,0)/(1,0)/(1,1) cluster does the same in top-left. **Random's chokes are qualitatively different from fractal's** — they are clustered (creating *deep* obstructions) rather than evenly-spaced (creating *shallow* ones).

### Random-as-control quality

**The "random control" was the *most* strategically interesting of the four**, contrary to what the name suggests. The col-4 wall is exactly the kind of large-scale asymmetric feature that creates real routing choices. The fact that this wall arose from random 17-hole sampling is a property of the seed, not of randomness per se — but in our seed (20260426), the random pattern out-performed both the regular (structured) and the recursive (fractal) patterns on hole-arrangement saliency.

### Tempo / first-move advantage

P1 won all 4 games. With n=1 per condition this is uninformative for balance, but the move counts to victory were:

| Condition | P1-win moves |
|-----------|-------------:|
| grid (8×8) | 15 |
| structured | 17 |
| fractal | 17 |
| random | **21** |

The 4-move gap between random and the rest is the strongest signal in this evaluation: **random produces non-trivial defensive opportunities for P2** (P2 actually broke my row-7 plan with (5,7), forcing a real detour), while structured and fractal collapsed to "P1 races a highway, P2 chases a highway, P1 wins by 2 moves." Grid is a 2-move-faster version of the same template.

### Quantitative metric: "moves where >1 plausible candidate existed"

Roughly counted from my own thinking-aloud:

| Condition | Moves with real choice |
|-----------|----------------------:|
| grid | 1 (move 1: which cell central) |
| structured | 2 (moves 1, 5 — which highway, which intersection) |
| fractal | 2 (same as structured) |
| random | **5** (moves 1 (which row to claim), 2 (whether to defend or build), 11 (which row to detour to), 17 (which side to bridge to row-7), 19 (going *up* to (7,7) before across)) |

---

## Phase 4 — Pattern Critic + Rebuttal

### Pattern Critic argues:

**(a)** All three 9×9 hole-conditions are essentially "remove 17 cells from a 9×9 grid." The play is identical across them: each player races a clear row/col, the first player wins by a 1–2 move tempo lead, no captures occur, the board fills to ~10–11 stones per side. Move counts (17, 17, 21) are within 25% of each other — within noise for a single-game-per-condition evaluation. The grid (15 moves) is faster only because there is one less row/col to traverse.

**(b)** The fractal-spike's Pair-C result (Δ +0.60) was driven by *cell count*, not arrangement. Removing 17 cells from a 64-cell board changes the *density* of legal moves and the *length* of viable chains. The Sierpiński shape is a coincidence of the generator path the spike used — any 17-hole pattern would produce the same Δ vs. an 8×8 grid.

**(c)** Prediction: an expert at the Sierpiński game transferring to random or structured will play *the exact same opening* — central row-2 anchor, then build out — and reach the same equilibrium (P1 wins on a perimeter highway), with **no relearning** required. The strategic vocabulary ("anchor, bridge, pinch cell, highway") is identical across all three.

### Player 1 / Player 2 rebut:

**Random's col-4 wall genuinely changed strategy in game 4.** Specifically, **move 11 ((4, 6) detour)** has no analogue in games 1 or 3. On structured and fractal, P1 never detoured — both row 0 and row 2 (and row 6, row 8) are equivalently clear, so P2's only useful break would be a mass blockade, which costs them more tempo than it costs P1. **On random, row 7 is uniquely clean.** When P2 broke it at (5, 7), P1 had to commit to a *specific* detour through row 6, plus a vertical jog at (7, 7) to circumvent the (8, 6) hole.

This is *not* a count effect: structured also has 17 holes but offers 4 equivalent-quality horizontal highways (rows 0, 2, 6, 8), so a row-break costs P2 nothing because P1 just shifts to the next highway. Fractal has the same 4 highways. **It is the *concentration* of holes (col-4 wall) that produces strategic content**, not the count.

The Pattern Critic's transfer prediction is **partially correct**: the *opening* on random is grid-like (central anchor). But the *middlegame* on random is qualitatively different. An expert at Sierpiński or structured would *not* anticipate a row-7 break being decisive (because it isn't on those substrates) and would lose tempo when they fail to build the (8, 6)-aware bridge.

So:
- Critic's claim (a) — "essentially the same" — **rejected**. Random produced a measurably longer, structurally different game.
- Critic's claim (b) — "count drives Δ" — **partially supported for fractal-vs-structured, rejected for random-vs-others**. The *count* of holes seems to be the dominant driver of fractal's Δ; the *arrangement* of holes is the dominant driver of random's Δ.
- Critic's claim (c) — "no relearning" — **rejected for random**. The detour-and-jog motif is not present on the other three.

---

## Phase 5 — Verdict

### SCORES (1–10) per condition

#### pat_grid (control)
- Strategic Depth: **4** — pure tempo race; once you take the centre row, you win. No real branching.
- Balance: **3** — P1 wins by tempo without contest; on a swap-rule version this would be 6.
- Novelty: **2** — vanilla Hex-with-Go-capture.
- Overall: **4**

#### pat_structured
- Strategic Depth: **5** — pinch cells exist, but four equivalent highways at rows {0,2,6,8} mean the play degenerates to "pick a highway, race, win". Hole-density-driven but not arrangement-driven.
- Balance: **3** — same race, same P1 win.
- Novelty: **4** — visually regular; strategically a +1 over grid because of pinch-cell theory but never relevant in practice.
- Hole-arrangement saliency: **3** — the lattice is symmetric enough that any of the 4 highways is fine; arrangement collapses to "is the cell on a highway or a pinch?"
- Overall: **5** (Δ +1 vs grid)

#### pat_fractal
- Strategic Depth: **5** — same as structured. The recursive 3×3 centre block is a visible obstacle but rows 0/2/6/8 (and cols 0/2/6/8) bypass it entirely.
- Balance: **3** — P1 wins; the central block doesn't break symmetry.
- Novelty: **5** — the *visual* novelty of recursive self-similarity is real, but I'm scoring strategic novelty too — and strategic novelty is roughly the same as structured.
- Hole-arrangement saliency: **3** — arrangement was visible but never load-bearing.
- Overall: **5** (Δ +1 vs grid)

#### pat_random
- Strategic Depth: **7** — col-4 wall forces a unique horizontal route; (8,6)/(8,8) corner cluster forces a unique east-tail bridge; P2 had a real defensive option at (5, 7). 5 moves with genuine candidate choice (vs ~1–2 for the other three).
- Balance: **4** — still P1, but the move count (21) shows P2's defence had teeth.
- Novelty: **6** — irregular wall-and-cluster geometry produces play patterns absent from fractal/structured.
- Hole-arrangement saliency: **7** — the col-4 wall is *the* strategic feature of the substrate; remove it and the game collapses to grid-like.
- Overall: **7** (Δ +3 vs grid)

### WITHIN-TEAM DELTAS

| Δ | Value |
|---|------:|
| Δ Overall fractal − grid | **+1** |
| Δ Overall random − grid | **+3** |
| Δ Overall structured − grid | **+1** |
| Δ Strategic Depth fractal − grid | +1 |
| Δ Strategic Depth random − grid | +3 |
| Δ Strategic Depth structured − grid | +1 |

### CRITICAL ASSESSMENT

- **Is Sierpiński self-similarity load-bearing? — No.**
  In my games the fractal's recursive structure produced **identical** play to the structured pattern (same 17-move row-2 victory, same opening, same closure). The fractal's "interesting" features (recursive 3×3 holes, perimeter ring) all sit at distance ≥1 from rows 0/2/6/8, so any chain on those rows is unaffected. Self-similarity is a *generator-side* property of the substrate, not a *strategic* property at game-time. The fractal-spike's Δ = +0.60 result is more parsimoniously explained by the generic effect of removing 17 cells (which raises chain-length-to-board ratio and tightens defensive options) than by the specific shape.

- **Did random produce comparable depth to fractal? — Yes, in fact greater.**
  Random's Δ Overall = +3 vs. fractal's +1. The col-4 wall in seed 20260426 happened to produce a single-cleanest-horizontal-row asymmetry that fractal/structured don't have (they each offer 4 equivalent highways). Random's longer game (21 vs 17 moves) and 5 candidate-choice moves (vs 2) are concrete evidence.

- **Did structured produce comparable depth to fractal? — Yes, almost exactly.**
  Both gave 17-move P1 wins on row-2 chains via the same template. The 4 perimeter highways exist on both. Structured's pinch cells and fractal's central block are aesthetically different, strategically equivalent.

- **Recommendation for R17:** **(c) replace with random-hole-perturbation operator.**

  Justification: my single-team result is **(random > fractal ≈ structured > grid)** which is the "hole-count alone matters" pattern from the README's decision rule, **with the additional finding that hole *concentration* (clusters / walls) produces meaningfully more depth than dispersed-but-regular arrangements.** A random-hole operator naturally produces such concentrations on some seeds (cf. the col-4 wall here) and disperses them on others, giving evolution stochastic access to high-saliency arrangements without paying for a Sierpiński-specific code path.

  A weaker form of this recommendation: keep a **random-hole operator with an additional "wall-concentration" mutation** that biases toward 3+ contiguous holes per axis. This would deliberately reproduce the col-4-wall property that drove random's lead in this evaluation.

  Caveat: n=1 within-team (and P1 winning all 4) is insufficient to over-determine. The cross-team aggregate (7 teams) is what should drive R17, not this single report.
