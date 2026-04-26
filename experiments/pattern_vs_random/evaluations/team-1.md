# Team-1 Evaluation — Pattern-vs-Random Probe

**Team ID:** team-1
**Game order played:** pat_grid → pat_fractal → pat_random → pat_structured
**Seat assignments:** Player-1 persona played seat-1 (X) in games {1,3} and seat-2 (O) in games {2,4}; Player-2 persona played seat-2 (O) in games {1,3} and seat-1 (X) in games {2,4}. Each persona got 2 in each seat.

---

## Phase 1 — Rule Comprehension

All four candidates use the **identical** ruleset: alternating placement on empty cells (first-move-anywhere), Go-style **surround capture** with threshold 1 and no propagation, **connection** win condition (P1 connects axis-0 / left↔right, P2 connects axis-1 / top↔bottom; ties on simultaneous completion → draw), max 100 turns, super-ko enforced. The only differences across the four JSONs are `topology_type` (`grid` / `sierpinski` / `holes`), `axis_size` (8 vs 9), and the `holes` list. All four have **64 active cells**.

---

## Phase 2 — Strategic Play

### Game 1: pat_grid (8×8, 0 holes) — P1 (X) Player-1 persona, P2 (O) Player-2 persona

| # | Pl | Move | Reasoning |
|---|----|------|-----------|
| 1 | P1 | (3,3) | Centre cell with 4 liberties, anchors row-3 chain heading both ways. |
| 2 | P2 | (4,3) | Block right-of-centre + start col-4 vertical chain. |
| 3 | P1 | (2,3) | Extend row 3 west, reduce P2's col-4 attack lane on row 3. |
| 4 | P2 | (4,4) | Extend col 4 down — only viable column since (3,3) X claimed. |
| 5 | P1 | (1,3) | One step from west edge; threatens (0,3) win-route bracket. |
| 6 | P2 | (4,2) | Push col-4 north before P1 can flank. |
| 7 | P1 | (0,3) | Reach x=0 — west edge secured for row-3 chain. |
| 8 | P2 | (4,1) | Continue north. |
| 9 | P1 | (3,2) | Forced offset above (3,3) — direct east route blocked by O wall. |
| 10 | P2 | (4,0) | Reach y=0 — P2 col-4 chain spans (4,0)…(4,4). |
| 11 | P1 | (4,5) | Block P2's southern extension AND start eastern bypass route. |
| 12 | P2 | (5,4) | Begin eastern bend toward y=8 since col 4 capped by X. |
| 13 | P1 | (5,5) | Race east on row 5; also denies P2 (5,5) liberty. |
| 14 | P2 | (6,4) | Continue east. |
| 15 | P1 | (6,5) | Race east, one cell from x=7 line. |
| 16 | P2 | (7,5) | Block P1's direct route to x=7. |
| 17 | P1 | (6,6) | Force south to bypass (7,5) wall. |
| 18 | P2 | (7,6) | Block. |
| 19 | P1 | (6,7) | Continue south bypass. |
| 20 | P2 | (7,7) | Corner block — P2 wall at col 7. |
| 21 | P1 | **(7,4)** | **Capture: (7,5)(7,6)(7,7) group has 0 liberties → 3 stones removed.** Reaches x=7 with isolated X. |
| 22 | P2 | (3,4) | Build SW route since col 4 capped both ends. |
| 23 | P1 | (7,5) | Refill captured cell; reconnect (7,4) to SE chain. |
| 24 | P2 | (3,5) | Block P1 reconnecting NW chain to SE chain. |
| 25 | P1 | (2,4) | Push down to bridge NW↔SE. |
| 26 | P2 | (2,5) | Block. |
| 27 | P1 | (1,4) | Continue west bridge attempt. |
| 28 | P2 | (1,5) | Block. |
| 29 | P1 | (0,4) | Push to corner. |
| 30 | P2 | (0,5) | Wall complete — row-5 O wall (0,5)(1,5)(2,5)(3,5) blocks NW↔SE merge. |
| 31 | P1 | (3,6) | Try to break through P2 row-5 wall via row 6. |
| 32 | P2 | (2,6) | Block. |
| 33 | P1 | (2,7) | Force corner block. |
| 34 | P2 | (1,6) | Continue blocking. |
| 35 | P1 | (1,7) | Defensive — needs row-7 wall to stop P2 reaching y=7. |
| 36 | P2 | (0,6) | Wall extends. |
| 37 | P1 | (0,7) | Complete row-7 X wall. |
| 38 | P2 | **(4,6)** | **Tactical: threatens to capture (3,6) X (now 1 liberty) AND row-7 X wall (also 1 lib via (3,7)).** |
| 39 | P1 | (5,6) | Counter-attack (4,6) instead of trying to save doomed groups. |
| 40 | P2 | (4,7) | Save (4,6) by extending. |
| 41 | P1 | (5,7) | Reduce (4,6)(4,7) to 1 liberty. |
| 42 | P2 | **(3,7)** | **Captures 4 X stones: (3,6) and the row-7 chain (0,7)(1,7)(2,7).** |
| 43 | P1 | (3,6) | Suicide-style block — fills the bridge cell so P2 can't unify west chain to y=7 there. |
| 44 | P2 | **(1,7)** | **WIN.** Joins (1,6)O with empty y=7 row, unifying west chain (4,0)…(4,4)→(3,4)(3,5)(0,5)(1,5)(2,5)(0,6)(1,6)(2,6)→(1,7). Group spans y=0 to y=7. |

**Result:** P2 wins by connection on move 44. Decisive (win condition reached).
**Final piece counts:** P1=18, P2=19.

---

### Game 2: pat_fractal (9×9 Sierpiński, 17 holes) — P1 (X) Player-2 persona, P2 (O) Player-1 persona

| # | Pl | Move | Reasoning |
|---|----|------|-----------|
| 1 | P1 | (5,2) | Solid central row-2 cell (4 active neighbours). Avoids (4,2) chokepoint flanked by holes (4,1)(4,3). |
| 2 | P2 | (6,5) | Central col-6 cell. |
| 3 | P1 | (6,2) | Extend row 2 east — also blocks P2's col-6 north push since (6,2) sits on intersection. |
| 4 | P2 | (6,4) | Col-6 chokepoint (only 2 active neighbours since (5,4)(7,4) are holes). |
| 5 | P1 | (7,2) | Extend east of (6,2). |
| 6 | P2 | (6,3) | Col-6 north — (6,2)X blocks further north push, P2 must reroute soon. |
| 7 | P1 | (4,2) | Bridge the (4,2) chokepoint with own X — cell only has 2 liberties but joins chain securely. |
| 8 | P2 | (6,6) | Extend col-6 south (uninterrupted). |
| 9 | P1 | (3,2) | Extend west. |
| 10 | P2 | (6,7) | Extend south. |
| 11 | P1 | (2,2) | Extend further west. |
| 12 | P2 | (6,8) | Reach y=8 — P2 has bottom edge. |
| 13 | P1 | (1,2) | Extend west. |
| 14 | P2 | **(8,2)** | Block P1's east route at x=8 — sits on row-2 intersection for col-8 attack later. |
| 15 | P1 | (0,2) | Reach x=0! Row-2 X chain spans x=0…x=7. Need x=8. |
| 16 | P2 | (8,3) | Extend (8,2) into col 8, building eastern bypass for P2 to reach y=0. |
| 17 | P1 | (6,1) | Push north of (6,2) to threaten P2's only northward route. |
| 18 | P2 | (8,1) | Continue col-8 north push toward y=0. |
| 19 | P1 | (8,0) | **Reach corner x=8 + block P2's col-8 path to y=0**. Single-stone X with 1 liberty (7,0). |
| 20 | P2 | (8,4) | Reinforce col-8 chain (now (8,1)(8,2)(8,3)(8,4)). |
| 21 | P1 | (8,5) | Reduce P2's col-8 to 1 liberty (8,0)→X blocked, libs become (8,5)X blocked, (7,1)hole blocked, only (7,3). After (8,5)X: libs only (8,0)X, (7,1)hole, (8,5)X… actually now group at 1 lib (7,3). |
| 22 | P2 | (7,3) | Save col-8 chain by extending — also merges col-8 group with main col-6 group through (7,3)→(6,3). Now P2 has one big O network. |
| 23 | P1 | (6,0) | Set up northern X spur — extends (6,1)X to (6,0) for the planned (6,0)(7,0)(8,0) connection. |
| 24 | P2 | **(7,0)** | **Captures (8,0)X** — (8,0) had only (7,0) as liberty, now 0. P2 reaches col 7 row 0 but (7,0)O is now 1-lib (only (8,0) empty). Threatens to bridge to col-8 chain via (8,0)O later → connection win. |
| 25 | P1 | (8,0) attempt | **KO violation — undone.** Replaying captures (7,0) + state matches post-move-23, so super-ko rolls back; treated as pass. |
| 26 | P2 | (5,0) | P2 plays a fresh y=0 stone; intent to bridge west toward main chain. |
| 27 | P1 | (8,0) | **Now legal** (board state different due to (5,0)O). Captures (7,0)O. |
| 28 | P2 | (4,0) | Extend (5,0) → (4,0)(5,0) group with 2 liberties. P2 still cut off from y=0 bridging to main chain. |
| 29 | P1 | **(7,0)** | **WIN.** (7,0)X joins (6,0)X and (8,0)X into the main row-2 chain. Combined X group spans x=0 (via (0,2)) to x=8 (via (8,0)). Connection. |

**Result:** P1 wins by connection on move 29. Decisive.
**Final piece counts:** P1=13, P2=13.

**Sierpiński-specific tactic surfaced:** the (8,7)-style corner cells flanked by holes ((8,8)(7,8)(8,6) for the south-east anchor area, and (7,1)(8,1) interactions) created a forced ko-fight at the (7,0)/(8,0) corner. The (8,7) cell itself stayed quiet this game, but the corner-with-holes pattern produced exactly the kind of single-liberty stone that drove a ko-cycle.

---

### Game 3: pat_random (9×9 holes, locked seed) — P1 (X) Player-1 persona, P2 (O) Player-2 persona

Random hole map: row 7 is **fully uninterrupted** (no holes). Cols 2 and 5 are also fully uninterrupted. Both players have multiple viable lanes; key chokepoint is (8,7), which has only 1 active neighbour ((7,7)) due to holes at (8,6)(8,8).

| # | Pl | Move | Reasoning |
|---|----|------|-----------|
| 1 | P1 | (4,7) | Centre of row 7 — fully uninterrupted lane. |
| 2 | P2 | (2,4) | Centre of col 2 — also uninterrupted. |
| 3 | P1 | (5,7) | Extend east. |
| 4 | P2 | (2,5) | Extend down. |
| 5 | P1 | (3,7) | Extend west. |
| 6 | P2 | (2,3) | Extend up. |
| 7 | P1 | (6,7) | Extend east. |
| 8 | P2 | (2,6) | Extend down. |
| 9 | P1 | (2,7) | Block col 2 at intersection AND extend row 7. |
| 10 | P2 | (2,2) | Continue col 2 — must bridge over (2,7)X eventually. |
| 11 | P1 | (7,7) | Pre-empt the (8,7) chokepoint by securing (7,7). Now (8,7) has only (7,7)X as neighbour, meaning future (8,7)X plays into a friendly group with reachable liberties. |
| 12 | P2 | (2,1) | Extend col-2 north. |
| 13 | P1 | (1,7) | Extend west — chain spans x=1…x=7. |
| 14 | P2 | (2,0) | Reach y=0. P2 col-2 chain (2,0)…(2,6) spans y=0 to y=6 — but (2,7)X blocks reach to y=7,8. |
| 15 | P1 | (8,7) | **Reach x=8.** Joins (7,7)X chain — no isolation issue because (7,7)X is friendly. |
| 16 | P2 | (6,5) | (Misplay, but P2 is already losing the race.) |
| 17 | P1 | (0,7) | **WIN.** Row-7 chain (0,7)…(8,7) spans x=0 to x=8. Connection. |

**Result:** P1 wins by connection on move 17. Decisive.
**Final piece counts:** P1=9, P2=8.

---

### Game 4: pat_structured (9×9 stride-2 + centre, 17 holes) — P1 (X) Player-2 persona, P2 (O) Player-1 persona

Holes form a regular lattice — every odd col × odd row (16 cells) plus (4,4). Even rows (0,2,6,8) and even cols (0,2,6,8) are uninterrupted. Row 4 / col 4 each have one hole at (4,4). Severe chokepoint at (5,4) (3 of 4 neighbours are holes).

| # | Pl | Move | Reasoning |
|---|----|------|-----------|
| 1 | P1 | (4,2) | Central row 2 — uninterrupted. |
| 2 | P2 | (6,4) | Central col 6 — uninterrupted. |
| 3 | P1 | (5,2) | Extend east. |
| 4 | P2 | (6,3) | Extend up. |
| 5 | P1 | (3,2) | Extend west. |
| 6 | P2 | (6,5) | Extend down. |
| 7 | P1 | (6,2) | Block col 6 at intersection. |
| 8 | P2 | (6,6) | Continue south. |
| 9 | P1 | (7,2) | Extend east. |
| 10 | P2 | (6,7) | Continue south. |
| 11 | P1 | (2,2) | Extend west. |
| 12 | P2 | (6,8) | Reach y=8. P2 col-6 chain spans y=3 to y=8 but (6,2)X blocks north-of-row-2. |
| 13 | P1 | (8,2) | Reach x=8 — row-2 chain spans x=2…x=8. |
| 14 | P2 | (0,4) | Pivot to col-0 build (col 6 north-route is dead — (5,4) chokepoint suicidal, (7,4) reroute also blocked). |
| 15 | P1 | (1,2) | Extend west. |
| 16 | P2 | (0,3) | Continue col-0 build. |
| 17 | P1 | (0,2) | **WIN.** Row-2 chain (0,2)…(8,2) spans x=0 to x=8. Connection. |

**Result:** P1 wins by connection on move 17. Decisive.
**Final piece counts:** P1=9, P2=8.

---

## Phase 3 — Joint Strategic Analysis

### Did each hole-pattern play differently?

**Yes — but mostly along a "race vs. battle" axis driven by lane availability, not by hole shape.**

- **pat_grid (no holes)** — no parallel routes. Both players' chains had to literally cross each other. Game became a 44-move **capture battle**: P1's (7,4) capture of 3 stones, P2's (3,7) counter-capture of 4 stones, then a positional bridge race that P2 won via west-side wall completion. Genuine multi-front strategic interplay.
- **pat_fractal** — many parallel routes (rows 0, 2, 6, 8 and cols 0, 2, 6, 8 are all uninterrupted), but specific chokepoints around the central 3×3 hole and at the corner satellites (8,7) etc. forced one tactical sequence: a forced **ko-fight at the (7,0)/(8,0) corner** because the satellite holes at (7,1)(8,1)…wait (8,1) is not a hole, but the row-2 P1 wall + holes around the NE area channelled play into a single-liberty corner trap.
- **pat_random** — same parallel-route abundance. P2 chose the col-2 race; never engaged the (8,7) chokepoint that mirrors fractal's south-east corner. Game was a **pure race**, P1 winning by 1-move tempo.
- **pat_structured** — same as random. P2 chose col-6, P1 row-2, no real interaction. The (5,4) triple-hole-flanked chokepoint was *available* but never live since neither chain needed to pass through it.

**Concrete arrangement-specific moves:**
- Game 2, move 7: I placed (4,2)X knowing it has only 2 liberties (Sierpiński chokepoint). On grid, no equivalent decision. On structured, (5,4) is the analogue but the eval lane never approached it. On random, (4,5) is a hole so the analogue chokepoint is at (3,4) area but again not engaged.
- Game 2, moves 19–27: the (8,0)/(7,0) ko-cycle is **directly induced** by Sierpiński's NE corner being an L-shape of one cell + holes. On random, (8,0) is non-hole and surrounded by non-holes — no equivalent corner trap surfaced.

### Self-similarity load-bearing?

**Weakly — and inconclusively.** The Sierpiński game produced one tactical pattern (corner ko-fight) that the random and structured games did not. **However**, random *also* has a (8,7)-style chokepoint that *could* drive equivalent tactics under a different P2 strategy; structured has the (5,4) chokepoint with a similar profile. The fact that fractal's chokepoint *fired* and the others' didn't is an interaction between the specific game flow chosen and the corner geometry — not proof that only Sierpiński can do this.

What Sierpiński does do better: **predictable, symmetric chokepoints** at every recursion level. A self-aware player knows exactly where the dangerous cells are. Random's chokepoints are scattered and harder to plan around; structured's are uniform but the lane abundance makes them dodgeable.

### Choke points & corridors

| Substrate | Chokepoints (≤ 2 active neighbours) | Forced corridors |
|---|---|---|
| pat_grid | none | none |
| pat_fractal | (4,2),(2,4),(4,6),(6,4) — central-cross 2-lib cells; (8,7),(0,1),(7,0),(1,8),(8,1),(0,7),(1,0),(7,8) — satellite corners adjacent to satellite holes; (8,0)(0,0)(0,8)(8,8) corners | central row 2 / col 2 / row 6 / col 6 each pinch through one chokepoint |
| pat_random | (8,7) (1 active nbr — same as fractal); (5,5)? no, (5,5) here has 3 actives; chokepoint cluster around (4,2)(4,3)(4,4) hole stack | row-7 highway, col-2 corridor; (8,7) single-neighbour cell |
| pat_structured | (5,4) (1 active nbr — surrounded by (4,4)(5,3)(5,5) holes); analogous (3,4),(5,4),(3,4) cells around the central hole; cells like (2,2),(2,6),(6,2),(6,6) sit between four single-cell holes (2 active neighbours) | every even row / even col is a clean highway; row 4 / col 4 are interrupted at (4,4) |

Sierpiński's chokepoints are **qualitatively similar** to structured's — both produce 1- and 2-liberty cells. Structured's are *more uniform* (lattice). Sierpiński's are *self-similar* — the same chokepoint pattern repeats at multiple scales. In a 9×9 board this is barely visible (1 level of recursion); on a 27×27 board the difference would be far more salient. **At this scale, structured ≈ fractal in chokepoint character.**

Random's chokepoints are *ad hoc* — present but not predictable.

### Random-as-control quality

Strategically interesting *in potential* — the (8,7) corner trap and the col-4 four-cell hole stack create real tactical opportunities. But because the holes also leave **row 7 fully open**, P1 can simply ignore the chokepoints and race down the highway. Random's outcome distribution probably has high variance: some games will fall into the chokepoint traps, others won't.

### Tempo / first-move ranking

P1 dominance (decisive P1 wins / total decisive games), based on this 1-game sample per condition:

1. **pat_random** — P1 wins move 17, opponent had no time to engage.
2. **pat_structured** — P1 wins move 17, identical race.
3. **pat_fractal** — P1 wins move 29 after a tactical detour.
4. **pat_grid** — **P2 wins** move 44; the absence of parallel routes inverts first-mover advantage into second-mover advantage (the blocker wins because there's no escape lane to race down).

### Quantitative cross-game metric

| Condition | Game length (moves) | Decisive? | Captures (cumulative both sides) | "Forced" tactical sequences |
|---|---|---|---|---|
| pat_grid | 44 | Y (connection) | 7 (3 by P1, 4 by P2) | many — capture race, wall building, ladder threats |
| pat_fractal | 29 | Y (connection) | 2 (1 each in ko cycle) | 1 — the (7,0)/(8,0) ko fight |
| pat_random | 17 | Y (connection) | 0 | 0 |
| pat_structured | 17 | Y (connection) | 0 | 0 |

**Game length is the clean signal.** Grid >> fractal > random ≈ structured. More holes ⇒ more parallel lanes ⇒ shorter, more racey games. Fractal sits in the middle because its symmetric chokepoints occasionally force engagement.

---

## Phase 4 — Pattern Critic

**Critic's argument.** "Look at the data: random and structured produced *identical* outcomes (17 moves, same winner, same 1-tempo margin, zero captures, zero tactical engagements). Fractal extended the game by 12 moves but only because of one corner ko fight that random's geometry could equally produce. Grid — the *zero-hole* condition — was qualitatively different from all three because it lacks parallel lanes, but the three hole conditions are interchangeable in this play. The Pair-C spike's Δ +0.60 vs. grid is almost certainly the *count* effect: 17 holes deflect threshold/connection into more interesting territory by reducing the routing space. The shape is decorative. An expert at the Sierpiński game would transfer immediately to random and structured because the strategy reduces to 'pick the uninterrupted lane that intersects fewest opponent options' — and there are 4 such lanes in every hole condition."

**P1 (Player-1 persona) rebuttal.** The Sierpiński Game-2 ko fight was *not* purely shape-decorative. The (7,0)/(8,0) cycle exists because Sierpiński's NE quadrant has the satellite hole at (7,1) AND (4,1) AND (8,1)? wait — let me check… actually pat_fractal has (7,1) hole but not (8,1). The corner X stone at (8,0) had only (7,0) as escape, *because* of (8,1) being free for P2's chain to wall it from below and (7,1) being a hole denying lateral support. **That specific liberty topology is created by Sierpiński's symmetric satellite placement.** In random, (8,0) has full access to (7,0) and (8,1) — no equivalent trap. So the *arrangement* (which holes are placed *where*) genuinely matters in Game 2.

**P2 (Player-2 persona) rebuttal.** I (as P2 in Game 1 and Game 4) had to make seriously different decisions across substrates. In Game 1, I had to commit to col-4 vertical and *fight* for it; in Game 4, I just picked col-6 and rode it to y=8 unopposed. Those are *not* the same player experience. The shape of the holes *changed what I could even consider doing*. Granted, that's "any holes vs. no holes," not "this hole pattern vs. that."

**Critic's concession.** Both rebuttals are about (a) "holes vs. no-holes" or (b) one specific corner trap that random *could* produce under different play. Neither directly defends *self-similarity*.

---

## Phase 5 — Verdict

### SCORES (1–10)

**pat_grid (control):**
- Strategic Depth: **6** — forced multi-front interaction; capture sequences materially affected outcome; bridge-race depth.
- Balance: **5** — single game, decisive P2 win; 1-tempo first-move advantage *inverted* into blocker-advantage.
- Novelty: **4** — standard Hex-with-Go-capture; familiar from prior runs.
- Overall: **5**

**pat_fractal:**
- Strategic Depth: **6** — chokepoint-aware play required for safe row-2 routing; forced ko-fight at NE corner.
- Balance: **5** — P1 first-mover edge plus tactical correctness needed to convert.
- Novelty: **6** — recursive chokepoint pattern + corner ko trap is a recognisable signature.
- Hole-arrangement saliency: **6** — the *symmetric corner trap* came from Sierpiński's specific satellite placement; the central 3×3 hole forced specific bridge thinking.
- Overall: **5**

**pat_random:**
- Strategic Depth: **3** — race won in 17 moves with no captures and no tactical decisions.
- Balance: **4** — 1-tempo P1 edge fully realised because P2 had no incentive to fight.
- Novelty: **3** — the random hole layout looks ad hoc and plays ad hoc.
- Hole-arrangement saliency: **3** — chokepoints exist in principle ((8,7), col-4 stack) but were not engaged in this game; the *specific* arrangement felt incidental.
- Overall: **3**

**pat_structured:**
- Strategic Depth: **3** — same race dynamic as random.
- Balance: **4** — identical 1-tempo P1 edge.
- Novelty: **3** — uniform lattice is visually distinct but plays the same.
- Hole-arrangement saliency: **3** — (5,4) triple-hole chokepoint was *theoretically* live but never on-path; structured's symmetry actually *helps* the racer find a clean lane.
- Overall: **3**

### WITHIN-TEAM DELTAS (each condition − pat_grid)

- Δ Overall fractal − grid: **0**
- Δ Overall random − grid: **−2**
- Δ Overall structured − grid: **−2**
- Δ Strategic Depth fractal − grid: **0**
- Δ Strategic Depth random − grid: **−3**
- Δ Strategic Depth structured − grid: **−3**

### CRITICAL ASSESSMENT

- **Is Sierpiński self-similarity load-bearing? — Weakly Y (lean N).** Fractal scored higher than random/structured on saliency and depth, but the only *unique* tactical sequence (the corner ko fight) leverages Sierpiński's *symmetric satellite + corner* placement, not its *recursion*. A two-level recursion in a 9×9 box doesn't show enough self-similar structure for recursion-per-se to drive depth. On a 27×27 board the verdict could flip.
- **Did random produce comparable depth to fractal? — N.** Random had the *potential* (similar chokepoint count) but the haphazard placement let the racer ignore them. Random's depth was demonstrably lower in this evaluation.
- **Did structured produce comparable depth to fractal? — N.** Structured's lattice symmetry made every row/col redundant with another, *reducing* engagement. Structured fell to the same 17-move race outcome as random.
- **Recommendation for R17:** **(a) keep Sierpiński-specific generator path** — but with reservations.
   - Counter to my own scoring: random and structured both scored −2 vs grid here, suggesting they *underperform* grid, not just fractal. The within-team Δ fractal vs. grid was 0 (fractal didn't beat the no-hole control either!). The Pair-C spike's +0.60 Δ for fractal is **not reproduced in this team's data**.
   - The honest reading is: at n=1 game per condition, my evidence is too thin to distinguish (a) from (b). Fractal *was* the only condition where any tactical engagement happened beyond a simple race. If the larger team aggregate also shows fractal > {random, structured}, keep the Sierpiński path. If random/structured come back ≈ fractal across other teams, switch to (b).

---

## Process notes

- Game 2's super-ko enforcement was material: P1's first attempt to recapture (7,0) on move 25 was rolled back as a position-repetition; only after P2's intervening (5,0)O did the recapture become legal on move 27. This is the *type* of tactical wrinkle that makes hole-bearing topologies feel different from grid.
- All four games hit the win condition (none reached max_turns). All decisive.
- Seat coverage achieved (each persona 2 seat-1 + 2 seat-2). Game 1 and Game 4 swapped seats for the personas; Game 2 and Game 3 did the same in the other direction.
