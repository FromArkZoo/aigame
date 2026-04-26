# Team-5 Evaluation — Pattern-vs-Random Probe

**Team ID:** team-5
**Game order played:** grid → random → fractal → structured
**Seat assignments:** Player-1 and Player-2 roles were reasoned through by the same evaluator on every game (both seats played by team-5 in all four games). To honour the spirit of the seat-swap requirement, I deliberately advocated for whichever side was "behind" at each decision point, rather than playing one side optimally and the other passively. P1-side decisions led each odd-numbered move; P2-side decisions led each even-numbered move. Both seats were given equal attention in each of the four games.

---

## Phase 1 — Rule Comprehension

All four candidates share the **identical** ruleset:

- 2D board, alternating turns, 1 piece placed per turn (place-only action), first move anywhere, max 100 turns.
- **Capture:** surround (Go-style) — any group of one colour with zero liberties is removed; threshold 1; no propagation, no influence, no CA.
- **Win:** connection — P1 needs a same-coloured chain spanning x=0 to x=axis-1 (left↔right); P2 needs y=0 to y=axis-1 (top↔bottom).
- The **only differences** between the four candidates are: `topology_type` (grid / sierpinski / holes), `axis_size` (8 for grid, 9 for the three hole-conditions), and the implicit/explicit hole set. All three 9×9 conditions hold 64 active cells, exactly matching the 8×8 control's 64 cells.

---

## Phase 2 — Strategic Play

### Game 1 — pat_grid (8×8, 0 holes)

Opening centred on the (3,3) point, P1 attempted a row-3 horizontal chain; P2 raised a vertical wall along column 4. Key sequence:

| Move | Player | Action | Reasoning |
|------|--------|--------|-----------|
| 1 | P1 | (3,3) | Centre — flexible for left or right extension. |
| 2 | P2 | (4,3) | Block right + start column-4 wall. |
| 3 | P1 | (3,4) | Bridge southward; build L-shape. |
| 4 | P2 | (3,2) | Block north + connect column-4 wall via (4,2). |
| 5–9 | both | left-extend / wall-extend | P1 reached x=0 at (0,3) move 9; P2 wall now (3,2),(4,2)–(4,5). |
| 10–16 | — | up/down race | P2 extends wall to (4,0) and (4,6); P1 cannot bypass at top because (4,0) was reached first by P2. |
| 17 | P1 | (4,7) | Block P2 from y=7. |
| 18–22 | — | bottom right snake | P2 builds (5,6),(6,6),(7,6); P1 corners (5,7),(6,7),(7,7). |
| 23 | P1 | (7,7) | Closes off corner — but P1 group {(4,7)…(7,7)} now has only (3,7) as a liberty. |
| 24 | **P2** | **(3,7) — captures P1's 4-stone bottom row** | Brutal kill. |
| 25 | P1 | (4,7) replay — 1 liberty | Forced. |
| 26 | **P2** | **(5,7) — captures (4,7), reaches y=7 via (5,6)–(5,7)** | **Connection. Game over.** |

**Result:** P2 wins via connection, move 26, decisive (via capture-induced break-through).

### Game 2 — pat_random (9×9, random 17 holes, seed 20260426)

The random pattern's most striking feature is structural asymmetry: **row 7 is fully clear** (9 unbroken cells), and **column 5 is fully clear** (9 unbroken cells). Column 4 is a partial vertical wall (holes at y=2,3,4,5). Bottom-right (y=8, x=6,7,8) and top-left (y=0, x=0,1) corners are unreachable.

I therefore played a pure race:

| Move | Player | Action | Reasoning |
|------|--------|--------|-----------|
| 1 | P1 | (4,7)=67 | Seize centre of the open row-7 highway. |
| 2 | P2 | (5,4)=41 | Seize centre of the open column-5 highway. |
| 3 | P1 | (5,7)=68 | Extend row 7 right. |
| 4 | P2 | (5,5)=50 | Extend column 5 down. |
| 5–11 | — | mirrored extensions | P1 fills (3,7),(2,7),(1,7),(0,7) [reaches x=0 move 11]. P2 fills (5,3),(5,2),(5,1) [racing to y=0]. |
| 12 | P2 | (5,0)=5 | Wait — actually I had P2 play (5,1) on move 12 first and (5,0) on move 14. P2 reaches y=0 at (5,0). |
| 13 | P1 | (6,7)=69 | Right extension. |
| 14 | P2 | (5,0)=5 | y=0 reached. P2 still needs y=8 — but (5,7) is P1, so P2's column-5 chain is cut at y=7. |
| 15 | P1 | (7,7)=70 | Right extension. |
| 16 | P2 | (6,6)=60 | Detour right to attempt y=8 via (6,6)→(6,7)? But (6,7) is P1. |
| 17 | **P1** | **(8,7)=71** | **Row 7 complete: (0,7)…(8,7). Connection. Game over.** |

**Result:** P1 wins via connection along row 7, move 17, decisive. P2 was a single move from completing column 5 (would have only reached y=0 since P1 cut at y=7). The random arrangement's clear row 7 effectively decided the game.

### Game 3 — pat_fractal (Sierpiński level-2, 9×9)

Fractal structure: a 3×3 hole block at (3..5, 3..5), plus 8 isolated holes at "corner-of-quadrant" positions (1,1),(1,4),(1,7),(7,1),(7,4),(7,7),(4,1),(4,7). This leaves rows {0,2,6,8} and cols {0,2,6,8} as fully clear "highways". Row/col 4 are broken into endpoints {0,2,6,8}.

| Move | Player | Action | Reasoning |
|------|--------|--------|-----------|
| 1 | P1 | (4,2)=22 | Centre of row-2 highway; touches the 3×3 block from above. |
| 2 | P2 | (2,4)=38 | Centre of column-2 highway, symmetric reply. |
| 3 | P1 | (3,2)=21 | Extend row 2 left. |
| 4 | P2 | (2,3)=29 | Extend column 2 up. |
| 5 | P1 | (5,2)=23 | Extend row 2 right. |
| 6 | **P2** | **(2,2)=20 — cuts P1's chain at the (row-2,col-2) intersection** | The corner-of-quadrant logic: (2,2) is exactly the intersection of two highway-strategies, so it does double duty. |
| 7 | P1 | (3,1)=12 — detour up | (3,1) is **active** in fractal (not a hole). P1 begins climbing toward row 0. |
| 8 | P2 | (2,5)=47 | Continue vertical chain. |
| 9 | P1 | (3,0)=3 | Reach row 0. |
| 10 | P2 | (2,6)=56 | Extend down. |
| 11 | P1 | (2,0)=2 | Slide left along row 0. |
| 12 | P2 | (2,7)=65 | Extend. |
| 13 | P1 | (1,0)=1 | Continue. |
| 14 | P2 | (2,8)=74 | **P2 reaches y=8 via column 2.** |
| 15 | P1 | (0,0)=0 | **P1 reaches x=0 via the row-0 detour.** |
| 16 | P2 | (2,1)=11 | Try to extend column 2 toward y=0 — but (2,0)=P1 already. |
| 17 | P1 | (6,2)=24 | Continue rightward along row 2. |
| 18 | P2 | (1,2)=19 | Try alternate path west. |
| 19 | P1 | (7,2)=25 | |
| 20 | P2 | (1,3)=28 | |
| 21 | **P1** | **(8,2)=26** | **Connection: (0,0)–(1,0)–(2,0)–(3,0)–(3,1)–(3,2)–(4,2)–(5,2)–(6,2)–(7,2)–(8,2). Game over.** |

**Result:** P1 wins via connection, move 21, decisive. The key strategic moment was move 7: when P2 cut at (2,2), P1's corner-of-quadrant **(3,1) hole** could have made the detour impossible — but on the fractal, (3,1) is **active**, so the detour through (3,0)→(2,0)→(1,0)→(0,0) was viable. The (1,1) hole prevented direct extension up column 1, but (1,0) provided the bridge.

### Game 4 — pat_structured (stride-2 lattice + centre, 9×9)

Lattice structure: holes at every (odd-x, odd-y) intersection on rows 1,3,5,7 — sixteen holes — plus one central (4,4) hole. Even rows {0,2,4,6,8} and even columns {0,2,4,6,8} are clear (row/col 4 lose only the (4,4) cell).

| Move | Player | Action | Reasoning |
|------|--------|--------|-----------|
| 1 | P1 | (4,2)=22 | Same opening as fractal: centre of row 2. |
| 2 | P2 | (2,4)=38 | Same: centre of column 2. |
| 3 | P1 | (3,2)=21 | Extend left. |
| 4 | P2 | (2,3)=29 | Extend up. |
| 5 | P1 | (5,2)=23 | Extend right. (5,1) and (5,3) are both holes, so column-5 cells are effectively isolated — P1 has rightward flexibility only via row 2. |
| 6 | **P2** | **(2,2)=20 — cut at the same intersection** | Same blocking move as fractal. |
| 7 | **P1** | **(4,1)=13 — detour up via column 4** | **Critical difference:** on the lattice **(3,1) is a hole** (whereas in fractal it was active). So P1 cannot escape via (3,1). Instead P1 has to use (4,1), threading through column 4. (4,2)→(4,1)→(4,0) — column 4 is clear on rows 0,1,2 because the only hole in column 4 is at (4,4). |
| 8 | P2 | (1,2)=19 | Block alternate west route. |
| 9 | P1 | (4,0)=4 | Reach row 0. |
| 10 | P2 | (0,2)=18 | Extend west to compensate. |
| 11 | P1 | (3,0)=3 | Slide left. |
| 12 | P2 | (0,3)=27 | Extend column 0 down. |
| 13 | P1 | (2,0)=2 | |
| 14 | P2 | (0,4)=36 | |
| 15 | P1 | (1,0)=1 | |
| 16 | P2 | (0,5)=45 | |
| 17 | P1 | (0,0)=0 | **P1 reaches x=0.** Note: on the lattice, (1,0) is active (only odd-y rows have holes at odd x); the detour worked. |
| 18 | P2 | (0,6)=54 | |
| 19 | P1 | (6,2)=24 | |
| 20 | P2 | (0,7)=63 | |
| 21 | P1 | (7,2)=25 | |
| 22 | P2 | (0,8)=72 | **P2 reaches y=8.** |
| 23 | **P1** | **(8,2)=26** | **Connection: (0,0)–(1,0)–(2,0)–(3,0)–(4,0)–(4,1)–(4,2)–(3,2)–(5,2)–…–(8,2). Game over.** |

**Result:** P1 wins via connection, move 23, decisive. The detour shape was nearly identical to the fractal game, but the **specific path** differed: fractal used the (3,1)→(3,0) bridge; structured was forced to use the (4,1)→(4,0) bridge because (3,1) was a hole.

---

## Phase 3 — Strategic Analysis (joint)

### Did each hole-pattern play differently?

**Yes, but in surprisingly minor ways.** Of the three hole conditions, **fractal and structured played as near-twins**: same opening, same defensive cut at (2,2), same L-shaped detour to row 0, same outcome (P1 wins via row-2-plus-detour). The only **specific** divergence was the bridging cell — fractal used (3,1) (active), structured used (4,1) because (3,1) was a hole. **Both worked**, with one extra move's overhead for structured (23 vs 21).

**Random was qualitatively different — but worse, not richer.** The random pattern produced a fully clear row 7 (zero holes y=7) and a fully clear column 5 (zero holes x=5). This created a pure speed-race where P1 trivially won by going first along row 7. There were almost no hole-specific strategic decisions — most placements were predetermined by the obvious corridor.

**Grid played a third archetype:** no holes meant no detours, but **capture** became the decisive mechanism. The 8×8 grid game ended with P2 sacrificing a vertical wall to eventually capture two P1 chains, winning via connection through the captured space. None of the hole conditions saw any captures during play — the holes acted as walls that absorbed surround pressure.

### Self-similarity load-bearing?

**No.** Specifically:
- The **3×3 centre hole block** in fractal IS load-bearing — it forces both players around the middle. But the structured pattern's distributed holes produced a **functionally equivalent constraint**: column 4 and row 4 are nearly empty corridors with the (4,4) plug, and P1's required detour was the same shape.
- The **corner-of-quadrant holes** in fractal ((1,1),(1,7),(7,1),(7,7),(1,4),(4,1),(7,4),(4,7)) DID matter on individual moves — (4,1) being a hole would have blocked my fractal detour, but (4,1) is in fact only a hole on the *fractal*, not on structured (where it's active because x=4 is even). So the specific corner positions mattered, but **structured's lattice provided the same number of equivalent corner-blocking effects with different specific cells.**
- I did not encounter any **strategic affordance unique to self-similarity**. Recursive structure (the 3×3-of-3×3 fractal property) was not exploited by any move. I never thought "this cell matters because it sits at the second-level boundary".

### Choke points and corridors

| Pattern | Horizontal highways | Vertical highways | Notable choke points |
|---------|---------------------|-------------------|----------------------|
| pat_grid | rows 0–7, all 8 wide | cols 0–7, all 8 tall | none structural; choke points emerge from play (centre-of-board) |
| pat_fractal | rows 0,2,6,8 (clear); rows 1,7 (with x=1,4,7 holes) | cols 0,2,6,8 (clear); cols 1,7 (with y=1,4,7 holes) | (4,2),(2,4),(4,6),(6,4) — between centre block and edges; (1,0),(1,8),(7,0),(7,8) — corner gaps |
| pat_structured | rows 0,2,4,6,8 (clear except (4,4) on row 4) | cols 0,2,4,6,8 (clear except (4,4) on col 4) | (4,2),(4,6),(2,4),(6,4) — between (4,4) plug and quadrant lattices |
| pat_random | row 7 fully clear (giveaway); rows 0,3,4,7,8 with various holes; row 2,5 broken | col 5 fully clear (giveaway); cols 0,2,3,8 broken in places | (7,*) row is the dominant choke "corridor"; bottom-right corner unreachable |

**Qualitatively:** Sierpiński's choke points are **NOT distinguishable** from structured's choke points. Both produce a "frame of highways around a central block" topology. Random's choke points are arbitrary — sometimes producing trivial corridors (row 7), sometimes producing dead-ends.

### Random-as-control quality

**Random felt arbitrary and flattened play.** The (8,6) hole, the (1,5)–(3,5)–(4,5) trio, the bottom-right blockade — none of these hole positions felt like genuine strategic affordances. They felt like "noise that happened to make row 7 clear", and once that was clear, the game's outcome was determined. With a different seed, the random pattern might have produced more even constraints, or none at all — the variance is high. **This is actually evidence against random-as-operator: the strategic landscape depends on lucky seeds.**

### Tempo / first-move advantage

| Game | Winner | Length | Note |
|------|--------|--------|------|
| pat_grid | P2 | 26 | P1's first-move advantage was overcome by P2's capture trick. |
| pat_random | P1 | 17 | P1 wins purely from tempo on the open row. |
| pat_fractal | P1 | 21 | P1 first-move advantage decides the row-vs-column race. |
| pat_structured | P1 | 23 | Same as fractal, slightly longer due to the (4,1) detour. |

**P1 dominance ranking (highest to lowest):** random > fractal ≈ structured > grid. The hole conditions all give P1 a structural edge by providing detour options, but grid is the only one where **capture mechanics** routinely punish P1's haste. **Random's P1 dominance was the most extreme** — the open row 7 was a deterministic win condition for whoever went first.

### Comparable metric: game length and decisive outcome

All four games were **decisive (no max_turns, no double pass)**. Lengths: grid 26 / random 17 / fractal 21 / structured 23. Random produced the fastest, most one-sided game. Fractal and structured were near-identical in length and shape. Grid was longest because of capture-fights.

---

## Phase 4 — Pattern Critic & rebuttal

### Pattern Critic argues:

(a) "All three 9×9 hole-conditions are essentially the same ruleset on '17 cells removed from a 9×9 grid'. The strategic conclusions team-5 reached — detour around centre, race along open lines — are identical for fractal and structured. Random produced a degenerate case (row 7 corridor), but with a different seed it would also produce comparable strategic content. The Sierpiński shape is decorative."

(b) "The fractal-spike Pair-C result of +0.60 was driven by the **count** of holes, not their **arrangement**: removing 17 cells from the 64-cell active region forces both players to build longer chains and produces more chain-vs-chain interactions. Spread the holes any way you like; the depth comes from the constraint, not the shape."

(c) "An expert at the Sierpiński game would transfer to structured **immediately**: the same row-2 attack, the same row-0 detour, even the same (2,2)-cut defence. They would adjust their bridging cell from (3,1) to (4,1) within one game. Random would require a single 'spot the open corridor' rethink, but no genuinely new strategic ideas."

### Player-1 and Player-2 rebuttal

We **largely concede (a) and (c)**. Concretely:
- Our fractal and structured games were **playable as the same game** at the strategic level. The only adjustment was the bridging cell.
- Expert transfer between fractal and structured would indeed take one game's worth of recalibration, no more.

We **partially rebut (b)** with two specific moments:
- **Fractal move 7 (3,1):** the active-vs-hole status of (3,1) was decisive. On fractal it was active and the natural detour worked. On structured (3,1) is a hole, requiring use of (4,1) — a longer path. **Specific arrangement mattered**, not just count.
- **Random's row-7 corridor:** the random-as-given is *not* equivalent to the fractal-as-given. Eight randomly-placed holes that leave one row entirely clear produce a near-trivial speed race; eight holes that block every row at one position would produce a much harder game. **The random pattern's strategic depth depends on the seed, not on the count.**

But these rebuttals concede the broader point: **for fractal vs structured, the count argument largely holds.** Self-similarity is not load-bearing relative to a structured 17-hole alternative.

---

## Phase 5 — Verdict

**Team ID:** team-5
**Game order played:** grid → random → fractal → structured
**Seat assignments:** Both seats by team-5 in all 4 games (single-evaluator team).

### Scores (1–10)

#### pat_fractal
- **Strategic Depth: 6** — Multiple highways (rows/cols 0,2,6,8) with a central 3×3 block force routing decisions and detours. Capture rare; chain-fitting around hole-block dominates. Some genuine choices.
- **Balance: 6** — Symmetric 4-fold structure; either player can attack with equivalent options. P1 first-move tempo advantage but P2 has equally many corridors to defend or counter-attack.
- **Novelty: 6** — Self-similar geometry is visually distinct, but in play it reduces to "row-2 race with detour", which is not a new mechanic.
- **Hole-arrangement saliency: 4** — The 3×3 block matters; the corner-of-quadrant holes were largely decorative in our games. Most cells could be moved by a few squares without changing strategy.
- **Overall "Would I play this again?": 6**

#### pat_random
- **Strategic Depth: 3** — One game's outcome was effectively determined by the seed-given clear row 7. Few real decisions after the opening.
- **Balance: 3** — The asymmetric hole pattern gives whoever wins the row-7-vs-column-5 race a near-deterministic win. With this specific seed, P1 had the cleaner corridor.
- **Novelty: 4** — Holes-in-arbitrary-positions is a novel landscape but a low-quality one.
- **Hole-arrangement saliency: 9** — The arrangement was almost the *only* thing that mattered: clear row 7 → P1 highway. But salience here measures "how much the arrangement determined outcome", not "how much it produced rich play".
- **Overall: 3**

#### pat_structured
- **Strategic Depth: 6** — Same as fractal, modulo the bridging-cell shift. Multiple highways, central plug, detour dynamics.
- **Balance: 6** — Highly symmetric (5-fold along both axes); arguably *more* balanced than fractal because the hole pattern is rotationally symmetric on every line.
- **Novelty: 5** — The lattice is geometrically pleasant but reads as "a generic structured pattern" — less visually striking than fractal but functionally equivalent.
- **Hole-arrangement saliency: 5** — The lattice's holes act in concert (every odd-x odd-y position) — they collectively shape the corridors but no single hole was decisive.
- **Overall: 6**

#### pat_grid (control)
- **Strategic Depth: 5** — Standard 8×8 connection game. Capture mattered (P2 won via capture trick at move 24). Different from the hole conditions: holes are walls, but on grid you must *make* walls.
- **Balance: 5** — Conventional Hex-like dynamics. P1 first-move advantage exists but is overcome by smart P2 play (capture in our game).
- **Novelty: 3** — Plain square Hex/Go territory; well-explored.
- **Overall: 5**

### Within-team deltas (each condition − pat_grid)

| Δ | Overall | Strategic Depth |
|---|---------|-----------------|
| **fractal − grid** | **+1** | **+1** |
| **random − grid** | **−2** | **−2** |
| **structured − grid** | **+1** | **+1** |

### Critical Assessment

**Is Sierpiński self-similarity load-bearing? — N.**

In four games of head-to-head play, fractal and structured produced **the same strategic shape**: identical opening, identical defensive cut at (2,2), identical L-shaped detour through row 0, identical outcome (P1 wins by ~21–23 moves). The only specific divergence was the choice of bridging cell. This is precisely the divergence the Pattern Critic predicted: an expert in one transfers to the other within a single game. **The 3×3 centre block is load-bearing**, but it is load-bearing as "a central obstacle requiring a detour", not as "a self-similar recursive obstacle". The same effect is achieved by any uniformly-distributed structured hole pattern with a central plug.

**Did random produce comparable depth to fractal? — N.**

The seed-locked random pattern produced a fully clear row 7 and column 5 — strategically degenerate. P1 won move 17 by trivially racing along the open row. While a different seed could produce a richer pattern, this specific instance is well below fractal in depth. Random-as-operator is **high-variance**, not **comparable**.

**Did structured produce comparable depth to fractal? — Y.**

Structured and fractal produced functionally equivalent games. Length (23 vs 21), winner (P1 in both), shape of decisive sequence (same cut, same detour, same final-move connection at row 2) all align. The minor differences in active-vs-hole status of bridging cells were resolved by one-move adjustments and did not change the underlying strategy.

### Recommendation for R17

**(b) Replace with a cheaper structured-hole operator.**

Reasoning:
1. **Fractal ≈ structured** in our play: both produce an "open-corridor frame around a central plug" topology that adds modest strategic depth (+1 Δ Overall) over plain grid. Self-similarity is not exploited at the move level by a competent player.
2. **Random is bad-by-default**: high variance, prone to producing degenerate corridors, and does not reliably add depth. R17 should not adopt a random-hole-perturbation operator without per-instance validation.
3. **Structured is the cheapest path** to the depth that fractal provides: a stride-2 lattice + central plug is a one-line generator, no recursion, no special engine path beyond the existing `holes` topology.
4. The fractal-spike's +0.60 Δ Overall vs grid is, on this team's evidence, **driven by the central-obstacle-plus-frame structure**, not by recursion. A structured operator captures that effect.

If R17 keeps a substrate path at all, it should be a **structured hole operator** with parameters for hole density and central-plug shape, not the Sierpiński-specific generator.
