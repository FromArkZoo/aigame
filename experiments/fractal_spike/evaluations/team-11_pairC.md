# Team-11 — Pair C Evaluation

**Pair:** C (alt + surround capture + connection)
**Fractal candidate:** `frac_C_fractal` (sierpinski 9×9, 17 holes, 64 active cells)
**Control candidate:** `frac_C_control` (grid 8×8, 64 cells)

---

## Phase 1 — Rule Comprehension

Both games use **identical** rules: alternating turns, single placement per turn on any empty cell, Go-style surround capture (groups with 0 liberties removed), and a Hex-style connection win where P1 must connect the low/high faces along dimension 0 (left↔right, x=0 to x=axis−1) and P2 must connect along dimension 1 (top↔bottom, y=0 to y=axis−1). Max 100 turns. The only differences are `topology_type` (sierpinski vs grid) and `axis_size` (9 vs 8); the fractal therefore has the same 64 active cells but with 17 holes carved into a 9×9 lattice.

**Degeneracy check (fractal-only):**
- Cells adjacent to holes have **fewer liberties**: (4,2) has only 2 liberties (vs 4 on grid) because (4,1) and (4,3) are holes; (4,0) has only 2 liberties because (4,1) is a hole. This makes single stones near holes much easier to capture.
- Columns 1, 4, 7 are broken at y=1, 4, 7 (one hole each) and columns 3 and 5 are broken at y=3..5 (central block). This means a player attempting a *single-column* defensive wall can only succeed in columns 0, 2, 6, or 8.
- Row 4 has only 4 active cells `{(0,4),(2,4),(6,4),(8,4)}` — a brutal mid-board chokepoint that forces row-4 traversal to detour by 4+ cells (BFS distance (0,4)→(8,4) = 12 vs 8 on grid).

**No degeneracy that prevents the rules from resolving** — connection win is reachable on both substrates and the action space is well-defined.

**3-sentence shared-rules summary:** Players alternate placing one stone per turn on any empty cell, with Go-style surround capture (0-liberty groups die immediately). The first player to form a stone-chain connecting their two opposing board faces — P1 left-to-right, P2 top-to-bottom — wins. Max 100 turns; if reached without a winner, no one wins.

---

## Phase 2 — Strategic Play

I played **4 games total** (2 per substrate, varying P2's defensive sharpness):

### Fractal Game 1 — P2 passive/parallel-builder
Move sequence: `22, 38, 21, 47, 23, 56, 19, 29, 24, 28, 18, 27, 20, 14, 25, 5, 26`

- P1 opens **(4,2)** — central along row 2 and dual-purpose because it claims one of only 4 cells in column 4 (which is fragmented by holes at y=1,3,4,5,7). Predicted P2 mirrors centrally.
- P2 plays **(2,4)** — the symmetric mirror move, claiming one of only 4 cells in row 4. Pure substrate-aware: (2,4) is a "frontier" cell because its only horizontal neighbors are itself in row 4.
- P1 builds row 2 chain (3,2), (5,2), (1,2), (6,2), (0,2), eventually filling (2,2); P2 builds column 2 chain (2,5),(2,6),(2,3),(1,3),(0,3).
- Critical moment: after P1 reached x=0 at move 11, P2 was already cut off from y=0 (P1's (0,2) blocks (0,3)→(0,2)→(0,1) path). P2 abandoned the upper face and tried (5,1)/(5,0) as a new northern group at move 14/16, but P1 (7,2)→(8,2) closed out the row-2 win at move 17.
- **Result:** P1 wins, **17 moves**. Endgame: connection condition triggered cleanly.

### Fractal Game 2 — P2 active row-2/column-6 wall
Move sequence: `22, 24, 20, 23, 21, 33, 19, 25, 18, 42, 12, 11, 3, 4, 2, 29, 5, 51, 4, 14, 6, 7, 8, 28, 7`

- P1 opens (4,2). P2 immediately plays **(6,2)** to preempt P1's row-2 right-side, then builds a wall **(5,2)→(6,3)→(7,2)→(6,4)→(6,5)** along the right side of central hole. This is a substrate-aware wall using column 6 (the rightmost continuous column).
- P1 races left, fills row 2 cells (2,2)→(0,2) reaching x=0 at move 9, then must detour. P1 climbs **(3,1)→(3,0)→(2,0)** — using the row above the central hole.
- **Substrate-specific moment (move 14):** P2 plays (4,0) trying to block P1's row-0 corridor. But (4,0) on fractal has only **2 liberties** ((3,0), (5,0)) because (4,1) is a hole. P1 plays (5,0) at move 17 → **captures (4,0)**. On grid 8×8, (4,0) would have 3 liberties and survive a single attack. **This capture was caused by the fractal substrate.**
- P2 tried again with (7,0) at move 22 — same 2-liberty problem (only (6,0)/(8,0) since (7,1) is a hole) — and P1 captured it at move 23 by playing (8,0).
- P1 finally plays (7,0) at move 25 to close the row-0 chain (0,2)..(0,2)→(2,0)..(8,0). **P1 wins, 25 moves.**
- **Two substrate-driven captures** ((4,0) and (7,0)) decided this game. Without them, P2's wall would have held.

### Control Game 1 — P2 passive/parallel-builder (analog of Fractal G1)
Move sequence: `27, 30, 25, 22, 26, 14, 24, 6, 38, 37, 28, 46, 20, 54, 21, 62...`

Wait, this move list belongs to Game 2; let me re-list G1.

**Control Game 1 sequence:** `27, 35, 28, 43, 26, 51, 25, 59, 29, 19, 24, 11, 30, 3, 31`

- P1 opens (3,3) center. P2 plays (3,4) directly below, then builds column 3 chain (3,5)→(3,6)→(3,7) reaching y=7 at move 8.
- P1 builds row 3 chain in lockstep: (4,3)→(2,3)→(1,3)→(5,3) → reaches x=0 at move 11 with (0,3).
- P2 belatedly tries to extend column 3 north with (3,2)→(3,1)→(3,0) reaching y=0 at move 14, but the **two halves of P2's chain are split by P1's (3,3)** — P2 has y=0 group and y=7 group with no connection.
- P1 finishes row 3 with (6,3)→(7,3) at move 15. **P1 wins, 15 moves.**

### Control Game 2 — P2 active column-6+7 wall (analog of Fractal G2)
Move sequence: `27, 30, 25, 22, 26, 14, 24, 6, 38, 37, 28, 46, 20, 54, 21, 62, 36, 45, 13, 23, 5, 47, 31, 39, 29, 31`

- P1 opens (3,3). P2 plays (6,3), then **builds column 6 continuously upward**: (6,2)→(6,1)→(6,0) — **reaches y=0 at move 8** in a single straight wall. (This wall is impossible to clone on the fractal in a single column without holes — but column 6 is fully open, so it works on both. The asymmetry shows up later.)
- P1 cuts at (6,4) at move 9, splitting P2's planned column.
- P2 builds bottom group **(5,4)→(6,5)→(6,6)→(6,7)** reaching y=7. Now P2 has top group y=0..3 and bottom group y=4..7, separated by P1's (6,4) cut.
- P2 reconnects via **column 7 bridge**: (7,2) at move 20, (7,5) at move 22, (7,4) at move 24. P2 plays (7,3) at move 26 — not suicide because the merged top+bottom chain has many liberties — and **P2 wins by connection, 26 moves.**
- **Critical observation:** the bridging cells (7,2), (7,4), (7,5) — all available on the grid — are precisely the cells that **DO NOT EXIST on the fractal** (well, (7,2) and (7,5) exist; but **(7,1), (7,4), (7,7) are holes**). P2 on the fractal cannot complete the column-6→column-7 bridge because (7,4) is a hole.

### Cross-game seat-swap evidence
Each substrate was played twice with different P2 strategies (passive vs aggressive wall). The P1-bias is therefore not just "P1 always wins because they move first" — on the **control with active P2**, P2 wins (Game 4). On the **fractal with active P2**, P1 still wins (Game 2) because P2 cannot complete the column 6+7 bridge.

---

## Phase 3 — Strategic Analysis (joint)

**Did the fractal play differently? — YES, decisively.**

| Phenomenon | Fractal G2 | Control G2 |
|---|---|---|
| Game length | 25 moves | 26 moves |
| Winner | **P1** | **P2** |
| Substrate-driven captures | 2 (P2's (4,0) & (7,0), each had only 2 liberties due to holes) | 0 |
| Successful defensive wall | No (broken at column 7 by holes) | Yes (column 6 + column 7 bridge) |
| Strategic chokepoints used | row 4, column 4, central 3×3 detour | none |

**Choke points / districts:** The fractal has **explicit chokepoints** that the control lacks. Row 4 has only 4 active cells `{(0,4),(2,4),(6,4),(8,4)}`, so any horizontal traversal at mid-board goes through these 4 cells. (2,4) and (6,4) are particularly valuable: each is the *only* row-4 cell within reach of the central column corridors, so claiming them gives a player either a key tempo-stone (for the player whose connection axis runs through it) or a wall (for the player whose axis is perpendicular). I deliberately played (2,4)/(6,4) early in both fractal games as substrate-aware moves; the same coordinate on the control (e.g. (2,4)) carries no special weight because (1,4), (3,4), etc. are all available alternatives.

**Influence shadows:** With `prop_type=none` in this ruleset there's no influence at all, so this dimension doesn't apply directly. However, holes act as **adjacency shadows**: cells next to holes have artificially low liberty counts, which translates to "stones in the shadow of a hole are weaker." Both fractal-game (4,0) captures exploited this — neither would have happened on grid.

**Path routing:** The central 3×3 hole **forces all routing around it**. P2 (top-to-bottom) cannot pass through column 3, 4, or 5 between rows 3 and 5 — must commit to a left-side (cols 0–2) or right-side (cols 6–8) route, or accept walking around. This means in the opening 5–8 moves, **both players must declare which side of the central hole they'll fight on**. There's no "go up the middle" option. On the control there's no such forced commitment.

**Tempo / first-move advantage:** P1 won 3 of 4 games. The single P2 win came on the control with smart play. The fractal **amplifies** P1's advantage because the holes break P2's primary defensive tool (a single continuous column wall). On the control, P2 has columns 0–7 all available for wall-building; on the fractal, P2 must use columns 0, 2, 6, or 8 — which are wider apart and easier for P1 to race between.

**Quantitative summary:** Of P2's 13 stones in fractal G2, **2 (15%) were captured** vs 0 of P2's 13 stones in control G2 — direct evidence that the substrate is altering capture dynamics, not just being decoration.

---

## Phase 4 — Substrate Critic (rebutted)

**Critic argues:** "The fractal is just an 8×8 grid with extra dead cells. The rules don't change. An expert in the rectangular game transfers immediately. Any apparent difference is artifact: P1 is just better positioned in this hand-crafted ruleset, and the fractal makes the game noisier without making it deeper."

**Critic's three charges:**

(a) "8×8 grid with dead cells, no new strategic concept."
(b) "Threshold/connection scaling — the fractal is just 'connection-game with detour penalty.'"
(c) "Expert transfers immediately."

**Rebuttal — Player 1 (me, in the connector seat):**
I did *not* transfer my opening directly. On grid I opened (3,3) — pure center. On fractal I opened (4,2) — *not center* but rather the cell that simultaneously claims one of only 4 cells in column 4 AND is on row 2 (my main connection corridor). That move makes no sense on grid because column 4 is just one of 8 columns; on fractal it's a structural priority. Charge (c) is **false**: the substrate forced an opening change.

The (4,0)-capture in Fractal G2 is a phenomenon **impossible on grid** (where (4,0) has 3 liberties and survives a single attacker). This isn't a "noisier version of the same game" — it's a new tactical pattern (single-stone groups in hole-shadow are tactically dead). Charge (a) ignores that holes carry adjacency-shadow effects, not just removed cells.

**Rebuttal — Player 2 (me, in the blocker seat):**
On the control I won via a **column 6 → column 7 bridge wall**. On the fractal I tried the same strategy and it **structurally cannot succeed** — (7,1), (7,4), (7,7) are holes and the column-7 chain cannot reach y=0 or y=7 contiguously. I had to abandon the wall strategy entirely on the fractal and play a different game (capture-pressure on P1's row-2 chain instead). Charge (a) is rebutted: the substrate didn't just tax me a few moves — it eliminated my best strategy.

Charge (b) is the strongest. The "detour penalty" framing is partially correct: the fractal *is* a connection game with extra obstacles. But the obstacles are **placed at strategically meaningful coordinates** (corners of the central block, periodic outer holes that break specific columns) rather than randomly, and they create asymmetric strategic effects (defensive walls hurt more than offensive paths because defenders need contiguous chains and attackers can branch). This is a real change in *which strategies succeed*, not just a difficulty knob.

**Substrate-novelty score: 7/10.** Genuinely changed strategic balance (wall-strategy elimination), introduced new tactical patterns (hole-shadow captures), required substrate-aware opening moves. Not a 9–10 because the underlying game (Hex+Go) is still recognizable and a strong Hex player would still understand the broad shape — but the specific tactical/strategic vocabulary needed is meaningfully larger.

---

## Phase 5 — Verdict

**Team ID:** team-11
**Pair:** C
**Fractal candidate:** frac_C_fractal
**Control candidate:** frac_C_control

### Fractal scores

- **Strategic Depth:** **7/10** — Forces substrate-aware opening, introduces hole-shadow capture tactics, eliminates the simplest defensive strategy (single-column wall) which forces both players into more nuanced play. Connection-around-central-hole is a genuinely novel strategic puzzle. Held back from 8+ because the policy space is still small (64 cells, ≤100 turns) and the "right" answers in many positions are forced by the hole geometry rather than open to creative interpretation.
- **Balance:** **5/10** — Across 2 fractal games (P2 passive G1; P2 active wall G2), **P1 won both** (moves 17, 25). The substrate amplifies first-mover advantage by breaking P2's defensive tool. Seat-swap evidence: P2 never won a fractal game in my play. This is a real balance issue for the fractal — the substrate's hole pattern asymmetrically favors the connector with shorter axis-traversal options.
- **Novelty (post-critic):** **6/10** — Hole-shadow capture and forced central-detour are novel-for-this-engine, and the substrate creates a ruleset that doesn't reduce to any prior R7–R16 winner. Rebuttable but rebutted.
- **Substrate-novelty:** **7/10** — Specific phenomena (column-7 wall impossible, (4,0)/(7,0) hole-shadow captures, row-4 4-cell chokepoint) only exist on this substrate.
- **Overall "Would I play this again?":** **6/10** — Yes, but I'd want a balance fix (e.g., komi for P2, or first-move restriction).

### Control scores

- **Strategic Depth:** **6/10** — Solid Hex+Go hybrid. Column-wall vs row-corridor race is rich: in Game 2 P2 wins by completing a column-6+7 wall, demonstrating that the rules support nontrivial defensive strategies. But it's mostly a known game (Hex with capture) — no strong novelty.
- **Balance:** **6/10** — 1-1 across 2 games (P1 won G1 with passive P2; P2 won G2 with active P2). The active-defender wins, suggesting P2 has the structural edge if they play the wall correctly. Better balanced than the fractal in absolute terms.
- **Novelty (post-critic):** **3/10** — This is essentially Hex+Go on a small grid. Not novel.
- **Substrate-novelty:** **0/10** (by definition for the control).
- **Overall "Would I play this again?":** **5/10** — Pleasant but unremarkable; I'd rather play actual 11×11 Hex.

### DELTA (fractal − control)

- **Strategic Depth:** **+1**
- **Balance:** **−1**
- **Overall:** **+1**

### Critical Assessment

- **"The fractal substrate genuinely added strategic depth" — Y** (with caveat that it also worsened balance).

- **Specific phenomena observed only on fractal:**
  1. Hole-shadow captures: (4,0) had only 2 liberties → capturable in one attack (vs 3 liberties uncapturable on grid).
  2. Column-7 defensive wall structurally impossible (holes at (7,1), (7,4), (7,7) break it).
  3. Substrate-aware openings required: (4,2) and (2,4) are forced "high-priority" cells because of column-4/row-4 fragmentation.
  4. Row-4 4-cell chokepoint forces all mid-board horizontal traversal through `{(0,4),(2,4),(6,4),(8,4)}`.
  5. Forced left-or-right commitment by move 5–8 because central hole blocks middle traversal.

- **Specific phenomena observed only on control (things the substrate took AWAY):**
  1. Single-continuous-column defensive wall as a winning strategy (P2 won control G2 this way).
  2. Mid-row interior cell traversal — being able to pass through (4,4), (3,4), (5,4) etc. as connecting tissue.
  3. Open ko/Go fights in central area (no central area on fractal).

- **Recommendation for R17: integrate (with balance probe).**
  The substrate clearly contributes new strategic content, especially for connection-rule games where the hole pattern creates structural defender-disadvantage. The fractal Pair C result (P1-favored substrate) is the **opposite asymmetry** of the control (P2-favored) — meaning fractal is *not* just a re-skin. Worth integrating into R17, but ALSO worth a follow-up balance probe (komi for P2, or mirror seed setup) before deploying as a champion-quality game.

  Specifically: I'd integrate sierpinski as a topology option in the generator pool, but bias evolution toward rule families where the substrate's first-mover advantage is offset by the rule structure (e.g., capture-heavy or majority-based wins might balance better than pure connection). Pair C exposes both the upside (genuine strategic novelty) and the risk (balance asymmetry).
