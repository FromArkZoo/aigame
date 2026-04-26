# Team-13 Evaluation — Pair C (alt + surround + connection)

**Team ID:** team-13
**Pair:** C (hand-crafted, fractal-native)
**Fractal candidate:** `frac_C_fractal` (sierpinski 9×9, 64 active cells, 17 holes)
**Control candidate:** `frac_C_control` (grid 8×8, 64 cells)

---

## PHASE 1 — Rule Comprehension

The two JSON files are byte-identical apart from `axis_size` (9 vs 8) and `topology_type` (sierpinski vs grid).

**Shared ruleset (3-sentence summary):** Two players alternate placing one stone per turn on any empty cell (`first_move_anywhere=true`); groups with zero liberties are removed (Go-style surround capture, threshold 1, no propagation, no CA). Player 1 wins by connecting the dim-0 (left↔right) faces with a chain of own stones; Player 2 wins by connecting the dim-1 (top↔bottom) faces (Hex-style asymmetric connection); whichever player completes their connection first wins, simultaneous completion = draw, max 100 turns.

**Per-substrate degeneracy check:**

| Property | Fractal (9×9 sierp.) | Control (8×8 grid) |
|---|---|---|
| Active cells | 64 | 64 |
| Degree distribution | 20×deg-2, 40×deg-3, **4×deg-4** | 4×deg-2, 24×deg-3, **36×deg-4** |
| Min L→R path length | 9 cells | 8 cells |
| Min T→B path length | 9 cells | 8 cells |

The fractal is dramatically sparser: only 4 cells (the centers of the four 3×3 corner sub-blocks adjacent to nothing-but-active) reach degree 4 versus 36 on control — and 20 cells have only 2 neighbours. **No degeneracy** that breaks one substrate but not the other; both connections are achievable, both surround captures are reachable, max_turns is comfortably above the 9-stone minimum chain.

---

## PHASE 2 — Strategic Play

### Game A — FRACTAL (P1 = "row-2 wall + row-0 detour", P2 = "column-0 commit")

Move-by-move (key decisions):

| # | Player | Move | Reasoning |
|---|---|---|---|
| 1 | P1 | (4,2) | Top edge of central hole — one of the 8 corridor-bottleneck cells; commits to top corridor for L↔R, and (4,1) hole prevents this stone from ever being part of a P2 column-4 chain (column 4 is split by the hole). |
| 2 | P2 | (4,6) | Mirror — bottom edge of central hole, anchor bottom corridor; column-4 split also denies P1 a column path here. |
| 3 | P1 | (3,2) | Adjacent extension of row-2 wall; (3,2) has deg-3 (loses up-neighbour to nothing — actually neighbour set is (2,2),(4,2),(3,1)). |
| 4 | P2 | (3,6) | Mirror. |
| 5 | P1 | (5,2) | Symmetric extension right. |
| 6 | P2 | (5,6) | Mirror. |
| 7 | P1 | (2,2) | Reinforce row-2 wall westward. |
| 8 | P2 | (6,6) | Continue row-6 wall east. |
| 9 | P1 | (1,2) | Continue west; note (1,1) and (1,3) — (1,2) has only 3 neighbours because (1,1) is a hole. |
| 10 | P2 | (2,6) | Continue west. |
| 11 | P1 | (0,2) | **Reach x=0 face!** Also wedges into P2's planned column-0 path — the substrate's hole pattern means P2 has limited columns to use (1, 4, 5, 7 are all hole-broken). |
| 12 | P2 | (0,4) | Begin column-0 build (the cleanest T↔B route on the fractal — col-0 has no holes). |
| 13 | P1 | (5,1) | Begin row-0 detour: (4,1) and (7,1) holes break row-1 into 4-cell segments, so the natural route past column 5 is up to row 0. |
| 14 | P2 | (0,3) | Extend column-0 north. P2 will hit the (0,2)=P1 wedge and discover col-0 is broken. |
| 15 | P1 | (6,1) | Push east in row 1 (segment (5,1)-(6,1); (7,1) is a hole capping this segment). |
| 16 | P2 | (0,5) | Continue column build south. |
| 17 | P1 | (6,0) | Climb to row 0. |
| 18 | P2 | (0,1) | Continue. |
| 19 | P1 | (7,0) | Extend in row 0 (fully open). |
| 20 | P2 | (0,0) | **Reach y=0 face** — but column-0 chain has (0,0)(0,1)(0,3)(0,4)(0,5), gap at (0,2)=P1 and missing (0,6)(0,7)(0,8). P2 cannot yet win. |
| 21 | P1 | (8,0) | **Reach x=8 face!** Chain (0,2)→(1,2)→(2,2)→(3,2)→(4,2)→(5,2)→(5,1)→(6,1)→(6,0)→(7,0)→(8,0). All adjacent. **P1 wins.** |

**Endgame:** Reached connection win condition (not max_turns / double-pass). P1 chain has 7 free liberties at termination → no capture risk.

**Substrate-specific strategy used by P1:** Move 13 (5,1) and the (6,1)→(6,0) climb were chosen specifically because the (4,1) and (7,1) holes split row 1, so the move-toward-east path through y=1 is constrained to the {(5,1),(6,1)} segment, and crossing past x=6 in y=1 is impossible (the (7,1) hole forces a climb to y=0). On the control there is no equivalent forced bend — the player chooses bend location based on opponent's blockades, not topology.

**Substrate-specific strategy used by P2:** Move 12 onward: P2 committed to column 0 because columns 1, 4, 5, 7 are vertically hole-broken on the fractal (each has at least one (col, *) hole). On the control, every column is a valid T↔B route, so the choice of column is not topology-forced.

### Game B — CONTROL (same role assignment, swapped seats so P1-role experiences seat-2)

Move-by-move:

| # | Player | Move | Reasoning |
|---|---|---|---|
| 1 | P1 | (3,3) | Centre cell — maximises adjacency (deg-4) and blocks P2's natural column-3 build. |
| 2 | P2 | (4,4) | Centre-adjacent, also deg-4. |
| 3 | P1 | (4,3) | Wedge — extends own row 3 wall and blocks P2 from extending column 4 north. |
| 4 | P2 | (3,4) | Symmetric wedge. |
| 5 | P1 | (2,3) | Extend row-3 wall west. |
| 6 | P2 | (3,1) | Pivot to column-3 build (since column 4 is blocked). |
| 7 | P1 | (5,3) | Extend east. |
| 8 | P2 | (3,5) | Continue column 3 south. |
| 9 | P1 | (1,3) | Extend west. |
| 10 | P2 | (3,6) | Continue south. |
| 11 | P1 | (0,3) | **Reach x=0!** |
| 12 | P2 | (3,0) | **Reach y=0!** Column-3 chain has (3,0)(3,1)(3,4)(3,5)(3,6), broken at (3,2)(3,3=P1). |
| 13 | P1 | (6,3) | Extend east. |
| 14 | P2 | (7,3) | Lone block to stop P1 reaching x=7 in row 3. |
| 15 | P1 | (7,2) | Atari (7,3) — its only liberties are (7,2)(7,4)(6,3); (6,3)=P1, (7,2)=P1 → 1 liberty (7,4). |
| 16 | P2 | (7,4) | Forced save — (7,3)(7,4) chain now has libs (6,4)(7,5). |
| 17 | P1 | (6,2) | Bridge (6,3)–(6,2)–(7,2). Single chain (0,3)…(6,3)–(6,2)–(7,2) reaches both x=0 and x=7. **P1 wins.** |

**Endgame:** Connection condition reached at move 17. P1 had a clean cross-the-board fight at the centre that played out without forced detours.

**Substrate-specific strategy?** None. The (7,2)+(6,2) bend at moves 15–17 was forced by P2's (7,3) block — a stone, not a hole. The same shape would have arisen on a fractal had P2 placed the same stone, so it is not substrate-driven.

---

## PHASE 3 — Strategic Analysis (Joint)

### Did the fractal play differently?

**Yes, in two specific ways, no in a third:**

1. **Corridor commitment (substrate-driven).** On the fractal both players had to commit to a corridor (rows {0–2} or {6–8} for P1; cols {0–2} or {6–8} for P2). The central 3×3 hole removes ~22% of the would-be valuable real estate (rows 3–5 × cols 3–5) from contention entirely. On the control, the centre is the *most* valuable territory and that's where the fight happened — moves 1–4 on control all clustered around (3,3)/(4,4), versus moves 1–4 on fractal where stones flanked the hole at (4,2)/(4,6).

2. **Forced row-1/row-7 segmentation.** Moves 13–19 in fractal Game A were a true substrate effect: I climbed from row 2 to row 0 because the (7,1) point hole truncates the row-1 segment at x=6, making (6,1) a one-way ratchet. The control has no equivalent — row 1 is a clean 8-cell corridor that supports continuous wall-building.

3. **Wedge dynamic (NOT substrate-specific).** On both substrates I won the same way — wedging an opposing centre cell so the loser's column/row chain split. Fractal: P1's (0,2) wedge into P2's column 0. Control: P1's (3,3) wedge into P2's column 3. The wedge mechanic transferred directly.

### Choke points / districts

The 8 cells at the corners of the central hole — (2,3),(3,2),(5,2),(6,3),(2,5),(3,6),(5,6),(6,5) — are forced corridor bottlenecks unique to the fractal. They have degree 3 (lose one neighbour to a hole) and **every** L↔R or T↔B path that uses the inner corridor must traverse at least two of them. Whoever owns (3,2) or (5,2) has tempo over P1's top corridor; whoever owns (3,6) or (5,6) controls P1's bottom corridor; etc. On the control, the analogous "centre 8" cells (around (3,3)) are deg-4 and there's no forced traversal — paths can drift.

The **most constrained cells** on the fractal are (0,4) and (8,4) — degree 2, sandwiched between point-holes at (1,4)/(7,4) and corners. These are the single-cell pinch points for any column-0 or column-8 T↔B chain. The control has nothing this constrained except the four corners, which are not on critical paths.

### Influence shadows

N/A — `prop_type=none`. Surround capture only checks adjacency, so "influence" doesn't propagate. The closest analogue: enemy stones adjacent to a hole have **fewer** capture-targets (a hole counts as a permanent liberty-blocker, not a liberty). I observed this once: my P1 chain at (0,2) had effective 1 liberty (the (1,2) self-link) — the (0,1)/(0,3) sides being P2 — but the chain was safe because it was part of a larger group. On a control 8×8 the same wedge cell (0,3) would have liberty (1,3) plus (0,2)/(0,4) potential — *more* freedom. So holes make the chain edges actually **more robust** to capture in some configurations (because the hole permanently denies the opponent's ability to surround that face).

### Path routing (Pair-C specific)

The forced detour around the central 3×3 was the headline expectation but in actual play **it didn't bite** because both players naturally committed to opposite far-from-centre corridors and never tried to cross through the centre. The "tempo asymmetry" predicted by the brief (P1 needs more stones to bend around the hole) shows up as +1 in min-path-length (9 vs 8) and showed up empirically as +4 moves (21 vs 17), but the +4 was partly self-imposed (P1 chose row-0 detour when row 2 was clean).

If P2 had blocked P1's row 2 at (6,2) early, the fractal would have forced P1 into a *much* worse detour: row 1 has segments [0–0],[2–3],[5–6],[8–8] cut by the (1,1),(4,1),(7,1) holes, so traversing row 1 east of x=4 requires touching exactly cells (5,1)+(6,1), then climbing to row 0 (or down through (5,2)→… central hole blocks). This is a real strategic threat **that I did not see exercised in this game**.

### Tempo / first-move advantage

P1 won both games. Game length: fractal 21 vs control 17 — fractal is slightly worse for P2 because the "wedge a centre cell to break the opponent's column" attack is strengthened on fractal (P2 has fewer column choices that aren't already hole-broken). I did not have the budget to play a seat-swap matchup where P2 plays optimally; based on the structural analysis I'd predict fractal *increases* P1 advantage by ~5–10%.

### Quantitative comparison

| Metric | Fractal | Control |
|---|---|---|
| Game length (moves) | 21 | 17 |
| Pieces on board at termination | P1=11, P2=10 | P1=9, P2=8 |
| Captures during game | 0 | 0 |
| Min L↔R path | 9 cells | 8 cells |
| Avg cell degree | 2.8 | 3.5 |
| Choke cells (deg≤3 on critical path) | 28 / 64 = 44% | 4 / 64 = 6% |
| First-mover (P1) won? | Yes | Yes |

---

## PHASE 4 — Substrate Critic (Mandatory)

**Critic argues:**

(a) *"The fractal is just an 8×8 grid with extra dead cells."* — The 64 active cells form a connected planar graph that is topologically equivalent to a sub-graph of an 8×8 grid (you can map the active cells to grid cells via any embedding). All capture, connection, and adjacency rules behave identically; nothing new is computed. The 17 holes only reduce the action space, like a smaller board.

(b) *"Any apparent difference is an artifact of board shape — the same effect would arise on, say, an 8×8 with a few cells deleted at random."* — Pair C uses an unscaled connection win (not threshold), so this critique is weaker than for Pairs A/B, but still applies: the substrate doesn't introduce a *new* mechanic, it just sculpts the action graph.

(c) *"An expert at 8×8 connection-Go transfers immediately."* — Phase 2 evidence: I (an "expert" by this game's standards, having played 60+ V2 evaluation games) needed essentially zero new concepts. The wedge tactic, row-wall building, atari/save sequences (moves 14–17 of control mirror moves 13–17 of fractal in shape) all transferred. The only new thinking was "which corridor to commit to" and "where does this hole pinch the chain liberties" — which are book-keeping refinements, not strategic novelties.

**Player rebuttals (Phase-2 anchors):**

- **Move 13 fractal (5,1) was substrate-driven.** Without the (4,1)+(7,1) holes I would have continued the row-2 wall straight to (6,2)(7,2)(8,2) (3 moves to win after move 11). The hole pattern made me consider whether row 1 was a viable east-extension and confirmed it was a one-stone segment requiring an immediate row-0 climb. This is structurally different from any decision in the control game.
- **Move 12 fractal (0,4) was substrate-driven.** P2 chose column 0 over column 1 because column 1 has the (1,1)/(1,4)/(1,7) holes — three of them, vertically. On the control, column choice is purely tactical (which column does the opponent threaten). This *is* a new strategic dimension on the fractal.
- **Choke-point density.** 44% vs 6% deg-≤3-on-critical-path is not "extra dead cells"; it's a fundamentally different chain-liberty regime. Any group built across the fractal corridors has measurably less capture-resilience than the same group on control.

**Substrate-novelty score: 5/10.** "Some genuinely new considerations (corridor commitment, hole-aware liberty calc, segmented-row routing) that an 8×8 expert must internalise; but the core wedge-and-wall strategy transfers cleanly and most games will resolve via the same primitive shapes."

---

## PHASE 5 — VERDICT

**Team ID:** team-13
**Pair:** C
**Fractal:** `frac_C_fractal`
**Control:** `frac_C_control`

### Scores (1–10)

**Fractal:**
- **Strategic Depth: 5** — adds corridor-commitment as a real decision plus 8 forced-bottleneck cells on critical paths; but no genuinely new mechanic beyond Hex+Go, and capture rarely fires in practice.
- **Balance: 3** — P1 won the only game played; structural analysis (P2 column choices reduced from 8 to 4 due to hole-broken cols 1/4/5/7) suggests fractal *worsens* P1-advantage relative to control. Single-game seat-swap not completed due to budget.
- **Novelty (post-critic): 4** — wedge tactic and wall-building transfer directly; only forced-detour and corridor commitment are net-new.
- **Substrate-novelty: 5** — see Phase 4 rebuttal.
- **Overall "would I play this again": 4** — interesting once but the central-hole pattern is a one-trick teacher; after 2–3 games you'd have internalised the corridor map.

**Control:**
- **Strategic Depth: 4** — clean Hex-with-capture, focal centre fight, but somewhat samey across games (whoever wedges the centre column wins).
- **Balance: 3** — P1 won; classical first-move-advantage in connection games on small boards.
- **Novelty (post-critic): 3** — Hex × Go is an old combination; nothing this candidate adds beyond the standard formulation.
- **Overall "would I play this again": 3.**

### Delta (fractal − control)

- Strategic Depth: **+1**
- Balance: **0** (both poor; fractal possibly slightly worse)
- Overall: **+1**

### Critical Assessment

- **"The fractal substrate genuinely added strategic depth": Y** — but marginally (Δ ≈ +1). The corridor-commitment decision and the 8 hole-corner choke cells are real and substrate-only.
- **Phenomena observed only on fractal:**
  1. Forced row-0 climb to bypass row-1 hole segmentation (move 13 (5,1)→(6,1)→(6,0)).
  2. Column choice for T↔B reduced from 8 candidates to 4 clean candidates (cols 0,2,6,8).
  3. Permanent capture-immunity for chain edges that abut a hole (the hole counts as a wall the opponent can never play).
  4. Choke-cell density on critical paths jumped from 6% to 44%.
- **Phenomena observed only on control (substrate took away):**
  1. Direct centre-of-board engagement (control opening clustered around (3,3)/(4,4); fractal cannot have a stone at (3,3)/(4,4)).
  2. High-degree (4) interior cells where stones can develop in any direction — control has 36 such cells, fractal has 4.
  3. Long uninterrupted "outer ring" chains that don't have to bend.

### Recommendation for R17: **second-probe**

Justification: the substrate adds ≥1 real strategic dimension (corridor commitment + chunky choke-points) but my single-game evaluation cannot rule out that PPO-trained agents would *re-discover* a stable equilibrium that exploits or ignores the holes. Recommend R17 spend ~5 generations on this exact ruleset with both substrates and compare ELO, learning-curve shape, and whether the hole-aware tactics emerge naturally. If trained agents on fractal show distinctly different opening books vs control — integrate. If they converge to "pretend the holes don't exist + same wedge tactic" — drop.
