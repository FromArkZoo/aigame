# R8 Replay Agent-Team Eval — team-2 — Game d4015a646ae3 (Connection Go)

**Team ID:** team-2
**Game ID:** d4015a646ae3 (R8 all-time-best, top-1 by ELO 2304.6, GE 0.386, depth 0.545, Feb-2026 agent-eval rating 8/10)
**Substrate:** flat 8×8 grid (64 active cells, max_degree=4, no holes, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game d4015a646ae3 --db genesis_v2_run8.db` (see `briefing_r8_d4015a646ae3.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Flat 2D 8×8 grid. Cell index = `y*8 + x`. Max degree 4 (no diagonals; interior cells have 4 neighbours, edges 3, corners 2). 64 active cells, no holes.

**Turn structure.** Alternating, 1 piece/turn. P1 first. Max_turns = 100.

**Action space.** 65 actions = 64 placements + 1 pass. No move actions. **No pie action.**

**Placement & capture.** Place at any empty cell, no first-move restriction. Capture rule = **surround (Go-style liberty capture)**.

**Critical clarification on capture.** The briefing's plain-English description says "≥3 of the placer's stones adjacent to an enemy stone captures it." **This is incorrect.** I verified empirically in `game_engine/engine_v2.py:_capture_surround` (lines 606–620) that this rule is **classic Go capture by removal of liberties**: an enemy group adjacent to the placed stone is captured iff it has zero empty neighbours after placement. The `threshold=3` parameter is **completely ignored** by surround capture.

This matters: a single P2 stone with 2 or 3 P1 neighbours is NOT captured if it still has at least one empty adjacent cell. To kill an interior P2 stone (4 neighbours), P1 must occupy all 4 of its neighbours. To kill an edge P2 stone, P1 must occupy all 3 of its neighbours. Corner stones (2 neighbours) can be captured with 2 P1 stones — these are the only "easy" kills.

I confirmed: placing 3 P1 stones around an edge P2 stone (4,1) at (3,1),(4,2),(5,1) did NOT trigger capture. Capture fired only when P1 also played (4,0), closing the last liberty.

**Propagation.** `influence` (radius=3, strength≈0.715, decay≈0.751). On placement, the engine adds `sign * 0.715 * 0.751^d` to `board_values[cell]` for every cell within graph distance ≤3 (so 0.715, 0.537, 0.403, 0.303 at d=0,1,2,3). Sign +1 for P1, −1 for P2. Clamped to [−100,100]. **Important: influence does not affect win detection at all.** It accumulates a "soft territory" signal that PPO can read as a heuristic — but the win condition is purely topological.

**Win condition.** **Connection (Hex-style asymmetric goals).** P1 wins by forming a contiguous chain of P1 stones connecting `y=0` face to `y=7` face (top↔bottom). P2 wins by forming a contiguous chain connecting `x=0` face to `x=7` face (left↔right). The `threshold: 0.5` field in the rule JSON is **vestigial** for connection-win — `_check_connection` BFSes owned cells and tests face reachability.

If neither side connects in 100 plies → draw (no fallback decision rule).

**Pie rule.** Off. R8 predates pie.

**Degeneracy check.**
- **Helper output header says `Win: threshold-race > 0.500` — this is HARDCODED and WRONG.** Real win is connection. The per-move `Done=True Winner=N` is correct, but the threshold-race "effective score" and "top-K greedy moves" displays are evaluating the wrong objective.
- The `threshold=0.5` field in `win_condition` is vestigial under connection-win.
- The `surround threshold=3` parameter is vestigial — engine uses Go liberty capture, not the outnumber-style described in the briefing.
- No pie rule, so first-mover advantage is uncompensated. P1 has substantial tempo edge.

---

## Phase 2 — Strategic Play

All moves engine-verified through the helper. Cell index = `y*8+x`; pass = 64.

### Game 1 — Sanity play (wall-race, asymmetric goal demo)

Sequence: `0,7,8,15,16,23,24,31,32,39,40,47,48,55,56` (15 plies).

Plot: P1 races column x=0 from top to bottom. P2 mirrors with column x=7. P1 wins at move 15 by completing the y=0..y=7 chain at x=0. P2's parallel column doesn't win — P2 needs LEFT-RIGHT, not TOP-BOTTOM. Demonstrates that the goals are genuinely asymmetric: a P2 vertical wall is wasted; P2 must build horizontally.

Reflection: P1 demonstrates the *fastest possible win*: 8 P1 moves uncontested. P2 also reaches 7 stones in their parallel wall but accomplishes nothing toward their own goal. Confirms the Hex-like topology and asymmetric goals are real.

### Game 2 — P2 plays "cut + build" through P1's column (the only real P2 strategy)

Sequence: `0,32,8,33,16,34,24,35,28,36,40,37,48,38,56,39` (16 plies).

Plot:
- P1 plays (0,0). P2 plays (0,4) — already a stone *inside* P1's intended column AND on P2's row=4 line.
- P1 continues (0,1),(0,2),(0,3) — building x=0 from top. P2 continues (1,4),(2,4),(3,4) — building y=4 east.
- Critical position at move 6: P2's stone at (0,4) sits on P1's column line. P1 cannot use (0,4) as a column cell.
- P1 jumps over P2's cut: (4,3) at move 9 — but this is now off the column line. **P1's column strategy is broken from move 2.** P1 should have abandoned x=0 immediately.
- P1 continues (0,5),(0,6),(0,7) along x=0 — but now x=0 is in two disconnected pieces ({(0,0)..(0,3)} and {(0,5)..(0,7)}) because (0,4) is P2.
- Move 16: P2 plays (7,4). P2's full row y=4 from x=0 to x=7 is now complete: connection from left face to right face. **P2 wins.**

Reflection (P2): P2's row=4 strategy was *strictly dominant* against P1's column-race. P2's stones simultaneously (i) block P1's column at (0,4) and (ii) build P2's own win. This is the classic Hex "blocker is also builder" property. Without pie rule, **P2 can always cut P1's intended column with one row-4 stone, then build their own row uncontested while P1 wastes moves on a dead column.**

Reflection (P1): P1's only counter was to *recognise the cut at move 2* and switch lines immediately. P1 should aim to make their column intent invisible at move 1 — e.g., start in the middle and not declare an axis. But on an 8×8 board, "hiding intent" while needing 8 connected stones is essentially impossible.

### Game 3 — P1 races inner column x=3, P2 races perpendicular row y=4 from x=0

Sequence: `3,32,11,33,19,34,27,35,44,36,52,37,60,38,4,39` (16 plies).

Plot:
- P1 builds column x=3 top-down: (3,0),(3,1),(3,2),(3,3). P2 builds row y=4 left-right: (0,4),(1,4),(2,4),(3,4).
- At move 8 P2's stone at (3,4) sits in P1's column — same "cut + build" pattern as Game 2.
- P1 attempts to reroute around (3,4): plays (4,5),(4,6),(4,7),(4,0) — a U-shape detour. Each detour move costs 1 ply but does NOT reconnect the broken column because the chain {(3,0)..(3,3)} and the detour {(4,5),(4,6),(4,7)} are separated by P2's row.
- Move 16: P2 completes y=4 row with (7,4). **P2 wins.**

Reflection: The "reroute around a single P2 cut" doesn't work because P2's row IS a continuous wall that fully separates the y=0 face from the y=7 face once it spans x=0 to x=7. P1's only hope is to **prevent P2 from completing the row** — which means P1 must spend a move on a cut-stone in P2's row instead of building the column. But every P1 cut-stone is one ply lost off P1's own race.

### Game 4 — P1 abandons column, plays for cut+build (mirror P2's Game 2 strategy)

Sequence: `27,11,28,12,29,13,26,10,30,14,25,9,31,15,24,8` (16 plies).

Plot:
- P1 plays (3,3). Then P1 races *horizontally* through row y=3 east: (3,3),(4,3),(5,3),(2,3),(6,3),(1,3),(7,3),(0,3).
- P2 mirrors: races row y=1 east: (3,1),(4,1),(5,1),(2,1),(6,1),(1,1),(7,1),(0,1).
- P1's row y=3 does NOT win for P1 — P1 needs *vertical* connection (top↔bottom). P1's row is a horizontal wall that goes left-to-right, which is P2's win condition, not P1's.
- P2's row y=1 DOES win for P2 — P2's win is x=0 to x=7. At move 16, P2 completes (0,1) and connects their entire row from left face to right face.
- **P2 wins on move 16 with a structural error by P1 (P1 chose the wrong axis).**

Reflection: This game confirmed that I had the goal-direction wrong in my early planning. **P1 needs columns (vertical), P2 needs rows (horizontal).** This is the asymmetric-goal property — and importantly, building the "wrong" axis is a wasted strategy.

### Game 5 — Capture probe: can P2 capture P1 chain stones mid-build?

Probe sequence: `27,18,19,26,20,28,11,21` (8 plies).

Position after move 8:
```
y=2:  . . O X X O . .
y=3:  . . O X O . . .
```

P1 has chain {(3,1),(3,2),(3,3),(4,2)}. P2 has stones at (2,2),(2,3),(4,3),(5,2) — pressing the P1 chain hard. Group liberties for P1's chain: {(2,1),(4,1),(3,0),(3,4)} = 4 liberties. Even with 4 P2 stones flanking, the chain still has 4 liberties because it spans multiple ranks.

To capture this 4-stone P1 chain, P2 would need to fill (2,1),(4,1),(3,0),(3,4) AND ensure no internal liberties remain. That's 4 more P2 moves — and P1 gets to extend or counter in between each. **Capturing a multi-stone connection chain mid-build is nearly impossible** under Go liberty rules on an 8×8 grid with 4-neighbour topology.

The verified capture earlier (Game probe with `11,12,20,30,13,29,4`) killed only an *isolated* single P2 stone at (4,1) — and P1 spent 4 moves to do it. **Captures matter for blocker stones (isolated invasions), not for winning chains.**

### Game 6 — P1 builds column with P2's row half-built east of column

Sequence: `27,28,11,29,3,30,19,31,35,32,43,33,51,34,59` (15 plies).

Plot:
- P1 builds column x=3 from middle: (3,3),(3,1),(3,0),(3,2),(3,4),(3,5),(3,6),(3,7).
- P2 builds row y=3 east: (4,3),(5,3),(6,3),(7,3) — completes the east half.
- Then P2 starts the west half: (0,4),(1,4),(2,4). But these are on row 4, NOT row 3. P2's east-half row-3 chain {(4,3),(5,3),(6,3),(7,3)} and west-half row-4 chain {(0,4),(1,4),(2,4)} are NOT connected (different rows).
- P1 completes column at move 15: (3,7). **P1 wins.**

Reflection: P2 played a *split* row strategy (east of P1's column on row 3, west of P1's column on row 4). These two chains never connect because they're on different rows. **P2's row must be on a single y-coordinate** to win, and that single row must intersect P1's column. If P2 splits the row, P1 wins on tempo.

### Strategy guides

**P1 (offence: race to top-bottom connection):**
1. Pick a column line (any x). Start in the *middle* of the column (e.g., (3,3)) so P2 can't predict the column edges yet.
2. Build down and up alternately — but recognize that P2's row strategy will cut your column at whatever y-row P2 commits to.
3. Once P2 plays a stone *inside your column*, your column line is broken. You must either (a) start a new column line or (b) spend a ply on a cut-stone in P2's row.
4. **Without pie rule, P1's tempo advantage means P1 wins if P2 plays sub-optimally** (e.g., mirrors with the wrong axis, or splits their row).
5. **Against optimal P2 (one-stone cut + build), P1 needs a "cut to block P2's row" move, which costs tempo.** This is the central tactical decision.

**P2 (defence + counter-build, hard-mode without pie):**
1. **Move 2 must cut P1's intended column AND seed P2's own row.** Pick a stone on row 4 (or 3, or 5) inside the column P1 is building.
2. Continue extending row 4 east or west — every P2 stone on row 4 is simultaneously a column-cut for any P1 column AND a row-build for P2.
3. The strategy is dominant in equilibrium because every P2 row stone double-counts.
4. **P2's row must be on a single y-value.** Don't split.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Two genuine strategy archetypes:
1. **P1 racing column** — straightforward Hex-builder.
2. **P2 cut+build row** — every P2 stone serves dual purpose.

Within these archetypes, the *column choice* (which x?) and *row choice* (which y?) introduce sub-strategies. But the meta-structure is two-strategy: race vs counter-race.

**Counter-play.** Real and bidirectional but **structurally favours P2** in the no-pie regime. P1 can break P2's row only by spending a move on the row line, which slows P1's column. P2 can break P1's column by playing a single row stone, which simultaneously builds P2's win. Asymmetric efficiency: **one P2 stone disrupts P1 + builds P2; one P1 disrupting stone slows P1 without contributing to P1's win.**

**Short-term vs long-term.** Games end in 15–20 plies if played sharply. This is *short*. The horizon for non-trivial planning is ~5–8 moves ahead (recognize opponent's axis, choose cut location, plan reroute). It is shorter than the 30–80 ply games of R20 menger threshold-race siblings.

**Emergent concepts observed.**
- **Cut-and-build dual-purpose stones** (P2's signature) — every row stone is simultaneously a blocker and a builder.
- **Axis lock-in.** Once a player has 3 stones along an axis, they're committed; switching axes costs all tempo accumulated.
- **The "broken column" reroute.** When P2 cuts at (k,4), P1 must reroute around the cut via (k+1,5),(k+1,6),(k+1,7) below and (k+1,3),(k+1,2),(k+1,1),(k+1,0) above — costing 4+ moves to reconnect.
- **Isolated stone captures.** P1 (or P2) can kill an isolated invading stone by closing all its liberties — but this requires 3–4 moves and chains of stones have so many liberties that they're effectively immortal.
- **Influence as a vestigial heuristic.** Influence accumulates and looks impressive in `effective_score` printouts, but never decides the game. Pure spreadsheet noise relative to win condition.

**Does the substrate matter?** 8×8 flat grid is a small Hex-like board. Diameter 8 means the minimum chain is 8 stones, the maximum game length under sharp play is ~16–20 plies. **The substrate is constraint-only — the same rules on a 9×9 grid would behave nearly identically, just with one extra cell per axis.** The 4-neighbour topology is what makes the asymmetric-goals work (diagonally adjacent stones not connected, so two parallel chains can cross-block).

**Does the propagation kernel matter?** No, for win detection. Influence is decorative. The kernel parameters (r=3, strength 0.715, decay 0.751) produce nice-looking accumulators in the score printout but never alter who connects first.

**Capture-rule contribution.** **Marginal in practice.** Captures fire only against isolated invading stones; multi-stone chains are essentially safe. In my 6 played games, only one capture fired (in a deliberate setup probe). In none of the natural-play games did a capture affect the connection race. The Go-liberty rule on 8×8 with 4-neighbour grid is **too weak to threaten the connection chain.** Compared to actual Hex (where stones are permanent), this game's captures add **only a small tactical sub-layer for invading-stone management** — meaningful for blocker placement, not for winning.

**First-mover advantage / seat balance.** Strong P1 edge against suboptimal P2. **Under optimal P2 play (cut+build row at y=4), P2 wins because their row stones serve dual purposes.** PPO data: `trained_vs_random` 0.84 / 0.56 suggests trained players outperform random badly, but `0.84 vs 0.56` (P1 winrate higher than P2 vs random) doesn't necessarily mean P1 favoured in trained-vs-trained — actually probably means *random P1 still wins 0.56 of the time*, which suggests P1 tempo is real. Without pie rule, this imbalance is structural.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a re-skin of **Hex**, with two minor decorations layered on top.

(a) **Connection-win on asymmetric goals** is **Hex** verbatim. Hex on a square grid with 4-neighbour adjacency is well-studied; published as "Bridg-It" (1958, David Gale) and other variants. The Hex theorem (one player must win, no draws on a hex board) does NOT apply on a 4-neighbour square grid — here draws are possible if both sides block each other (and indeed the briefing notes max-turn timeouts yield draws, not fallback winners).

(b) **Go-style liberty capture** added on top: a known mechanic from Go (3000+ years old). Adding Go capture to a connection game is **not novel** — published games like "Cross" (1953) and "Y" have similar mechanics, and TwixT layers capture-like blocking on Hex-style topology.

(c) **Influence accumulation** as a non-decisive side-field: **purely decorative.** Influence does not enter win logic, capture logic, or legal-move logic. PPO can read it as a heuristic, but a human player would simply ignore it. Calling this "influence-driven Go" overstates the novelty — it's just a debug stat that happens to be in the observation tensor.

(d) **Flat 8×8 grid substrate.** Standard. The smaller-than-typical (axis 8 vs Hex's 11–13) reduces strategic horizon. **Substrate is constraint-only — no fractal/topological contribution.**

(e) **Expert-transfer test.** A Hex player would understand this game in 90 seconds. The Go-capture addition is a 5-minute tactical sub-lesson. The influence field would take 30 seconds to dismiss as irrelevant. **Total transfer time: 5 minutes.** This is below the 10–15-minute threshold I'd expect for a "genuinely novel" combination.

**Closest known-game analogue:** **Hex on a square grid + minor Go-capture overlay.** Specifically resembles **"Hex with capture"** variants discussed in the Hex literature (Browne 2000, Hayward 2019). The published TwixT family also has connection + blocker mechanics but with different piece types.

**Comparison to the broader Genesis R8 corpus.** This was R8's top-1 game by ELO and the agent eval gave it 8/10 in February 2026. From the play I did:
- **The depth that 8/10 implies is NOT present in the natural game.** Games end in 15–20 plies. Decision space is small. The "two viable strategies" decompose to one dominant P2 strategy (cut+build) and a handful of P1 variations that all lose to it.
- The strategic richness comes almost entirely from **Hex's structure** — which is borrowed, not novel.
- The Go-capture overlay is **theoretically interesting but practically inert** on this substrate (too weak to threaten chains).
- The influence field is **vestigial**.

**Comparison to R19/R20 corpus.** R19 menger top (`1f9191b5d4e6`, 4.8/10) and R20 best (`5f5c72e15220`, 5.0/10) are threshold-race games on menger substrates. They are *quantitatively different* from this game — they have spreadsheet endgames and 70+ ply game lengths, but they have genuine multi-strategy depth (hub-cross + column-invasion + capture-cycles).

**This R8 game is shorter, more elegant, and more transparent** than R19/R20 winners — but the elegance is **Hex's elegance, not Connection Go's elegance.** The novelty is in the *combination* of (i) connection + (ii) capture + (iii) influence on (iv) a 2D grid — and that combination is mostly inert because (ii) is weak and (iii) is decorative.

**Player rebuttal (P1 + P2):**
- The **Hex backbone is brilliant and proven deep** — Hex has 60+ years of theoretical study and remains a strong AI benchmark. This game inherits Hex's depth structurally.
- The **Go-capture sub-mechanic adds a small tactical layer** that distinguishes it from pure Hex — invading stones become vulnerable, which slightly changes blocker calculus.
- But **on 8×8 with 4-neighbours, captures are too rare to add meaningful depth.** The chains are too well-protected.
- **The influence field is wholly inert in play** — it does not change winning logic, capture logic, or move legality. PPO may use it as a feature, but a strategic player cannot.
- **No pie rule** means the first-mover advantage is uncompensated. P2's "cut+build" is the only counter — and it's overpowered.

**Novelty score (post-adversary):** **3/10.** Above 2 (pure re-skin) because (i) the Hex+Go+influence combination is not a published game I can name, (ii) the cut+build asymmetry is a fresh tactical primitive, (iii) the captures *do* fire occasionally and affect invasion economics. Below 5 because (a) Hex is the load-bearing structure, (b) captures are largely inert, (c) influence is decorative, (d) no pie rule means the asymmetry is unbalanced.

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game ID:** d4015a646ae3
**Rules Summary:** Place stones on an 8×8 grid; P1 wins by connecting top to bottom, P2 by connecting left to right (Hex-style asymmetric goals). Stones can be captured Go-style if their group runs out of liberties. An influence field accumulates but does not affect winning.
**Substrate:** flat 2D grid, axis 8, 64 active cells, max_degree=4, pie_rule=False.
**Turn Structure:** alternating, 1 piece per turn, P1 first, max 100 plies.
**Hybrid actions:** no (place-only).
**Soft violations flagged:**
- Helper hardcodes a threshold-race header that doesn't match the connection-win rule.
- `threshold=3` in capture rule is ignored — engine uses Go liberty capture.
- `threshold=0.5` in win condition is vestigial under connection-win.
- Influence field accumulates but does not enter win/capture logic — pure decoration.
- No pie rule — first-mover advantage uncompensated.

### Scores (1–10)

- **Strategic Depth: 4** — Hex's depth is borrowed, not earned. Game ends in 15–20 plies under sharp play. Decision horizon is 5–8 moves. The "two viable strategy archetypes" decompose to one dominant P2 strategy (cut+build) and a few P1 variations. The engine-measured depth 0.545 is consistent with a Hex-like game on a small board — but anchoring against R8 8/10 (which implies Go-or-Hex-tier depth), this is **substantially below** the implied claim. Anchor: above R17 mean (3.5), above R20 production mean (3.73), but well below R8 Feb-2026 rating (8/10), well below true Hex on 11×11 (which I'd score 8+).

- **Emergent Complexity: 4** — Cut+build dual-purpose stones, axis lock-in, broken-column reroute, isolated-stone captures. These are real emergent patterns but they are **mostly inherited from Hex** plus a single small Go-capture decoration. The influence field generates no emergent strategy because it is inert to win logic. Anchor: above R17 mean, comparable to R20 menger threshold-race siblings (which score 4 on emergence), well below the 8/10 implied claim.

- **Balance: 3** — Without pie rule, P2 has a structural advantage via the cut+build strategy. PPO trained-vs-trained data is not directly reported but the trained_vs_random asymmetry (P1 winrate 0.84, P2 0.56) suggests P1 dominates against random play (where P2 doesn't know to cut+build) but optimal P2 should win in equilibrium. The lack of pie rule is the single biggest balance flaw and it is uncorrectable in the R8 era. Anchor: low — comparable to R20 menger games without pie (4) but worse because the asymmetry is sharper and harder to counter.

- **Novelty (post-adversary): 3** — see Phase 4. Hex + small Go-capture overlay + inert influence field. Above pure re-skin because the cut+build dual-purpose tactic is fresh, below "genuinely new" because Hex is doing nearly all the load-bearing strategic work and the two additions are weak/decorative.

- **Replayability: 4** — Two main strategies, both well-defined. After 2–3 games a player has fully mapped the strategy space. Subsequent games would explore (i) which row/column P2 picks for the cut and (ii) capture-tactics in fringe positions — but the meta-structure is fixed. **Less replayable than full Hex** because Hex's larger board (11×11) supports a richer opening theory; 8×8 is too small. Anchor: comparable to R19/R20 production games (4), below true Hex (8).

- **Overall "Would an agent team play this again?": 4** — Once: yes, to verify the Hex-like dynamics and confirm asymmetric goals. Twice: yes, to play both seats and feel the asymmetry. Three times: no — the strategy space is fully mapped. The game is competently constructed (real Hex backbone, clean rule set, no broken mechanics) but **NOT a 8/10 game by the R20-protocol rubric.** The R20-protocol rubric appears to penalise inert mechanics, decorative fields, and small substrates more than the Feb-2026 R8 rubric did. **My score of 4/10 is well below the Feb-2026 8/10 and indicates substantial calibration drift.** Anchor against R8 (8 — historical), R17 mean (3.5), R20 production mean (3.73), R20 top (4.80). My 4 places this game **just above R20 production mean and just below R20 top** — competently above floor but not exceptional.

### CLOSEST KNOWN-GAME ANALOG
**Hex on a square 4-neighbour grid, with Go-style liberty capture and a decorative influence field.** Within the project corpus, it is the canonical "connection game" — no R17–R20 ancestors use connection-win. Outside the corpus, the closest published analog is **Hex** (Piet Hein 1942 / John Nash 1947), with the Go-capture overlay reminiscent of **TwixT** (1962) or **Cross** (1953) but lighter. Influence accumulation is purely a debug stat.

### KILLER FLAWS
- **Influence field is wholly inert to win logic.** The strength=0.715, decay=0.751, radius=3 propagation field never affects who wins. It's an observable in the PPO observation tensor and a number in the score printout, but a strategic player cannot use it for anything. This is the kind of "vestigial mechanic" R20-protocol rubric heavily penalises.
- **`threshold=3` in capture rule is ignored.** Engine uses Go liberty capture; the rule JSON's threshold parameter does nothing. This is a documentation/rule-representation bug, not a play-time bug — but it inflates the game's apparent novelty.
- **No pie rule + measurable first-mover advantage.** P1's tempo edge is uncompensated. P2's only counter is cut+build, which is dominant once recognized but means the game has a forced winning strategy for P2 against any P1 column commitment — which is structurally unbalanced.
- **8×8 is too small.** Connection chains take 8 stones; games end in 15–20 plies under sharp play. Strategic horizon is short. Real Hex uses 11×11 or 13×13 for this reason.
- **Captures rarely fire in actual play.** In 6 played games, captures only fired in a deliberate setup probe. Multi-stone chains have too many liberties to die. The capture overlay is **theoretically interesting but practically inert**, similar to the influence field.
- **Helper output is misleading.** The `Win: threshold-race > 0.500` header and "top-K greedy moves by Δscore" displays are evaluating threshold-race (the wrong objective). The PPO training itself uses the correct connection-win — but the eval scaffolding leads to wrong intuitions.

### BEST QUALITY
**The connection-win on asymmetric goals with 4-neighbour grid topology.** This is Hex-on-a-square-grid, which is a proven deep strategic frame. It produces genuine emergent strategy: the cut+build dual-purpose stone, the broken-column reroute, the axis lock-in. **The structural choice to layer Hex semantics onto the Go-engine substrate is the most interesting design decision in the entire R8 corpus.** That deserves credit. But the credit is for *recognising* Hex's depth, not for *creating* novel depth — and the additional rules (capture, influence) are largely decorative.

### grid STRUCTURAL CONTRIBUTION
**8×8 flat grid is a constraint-only substrate.** The 4-neighbour topology is essential (it's what makes the asymmetric-goal-with-cross-blocking work), but the small axis means the game has a short strategic horizon and the same rules on 11×11 would be substantially deeper. Compared to R19/R20 menger (where the substrate is also constraint-only but provides 8 corner sub-cubes for hub-cross strategies), 8×8 grid gives *no* such structural scaffolding — the strategy is essentially independent of the cell index. **No fractal contribution, no Hausdorff-dim play, no substrate emergence.**

### IMPROVEMENT IDEAS
**Single best change: TURN ON THE PIE RULE.** P1's uncompensated tempo edge and P2's dominant cut+build counter are both directly addressed by pie. Pie would let P2 take P1's first move if it's a strong opening, forcing P1 to play sub-optimal openings, which would in turn give P2's cut+build less to work against. This is the canonical Hex fix and it would push balance from 3 to 6+ and add real opening theory.

Secondary improvements:
- **Replace the inert influence field with an active mechanic.** Either (i) make influence affect legal moves (e.g., illegal to place at cells with very negative influence), or (ii) drop the field entirely. Currently it consumes observation-tensor budget for no strategic gain.
- **Expand the board to 11×11 or 13×13.** Hex's strategic depth scales superlinearly with board size; 8×8 caps the depth. The R8 era's "axis 8" constraint is the bottleneck.
- **Replace Go-liberty capture with outnumber-N capture** (matching the briefing's plain-English description). Outnumber-2 or outnumber-3 captures would fire more frequently against winning chains and add real tactical depth.
- **Fix the helper's threshold-race display** to show connection-status instead. The current "effective_score" and "top-K greedy moves" outputs evaluate the wrong objective and lead to confused intuitions.
- **For project-level calibration:** treat the Feb-2026 8/10 rating with substantial skepticism. The R20-protocol rubric appears to score this game ~4/10, suggesting calibration drift of ~4 points on the GE-bottleneck branch. Before redesigning the fitness function around connection-win games, **verify that other R8 high-rated games show the same drift** — if they do, the GE-bottleneck diagnosis stands but R8 production estimates are inflated by ~50%.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/r8_replay/team-2_game_d4015a646ae3.md`.*
