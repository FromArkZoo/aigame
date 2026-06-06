# Run 21 Agent-Team Eval — team-3 — Game b12ff78f1c1d

**Team ID:** team-3
**Game ID:** b12ff78f1c1d (grid slate TOP; gen-5 crossover child, verified parent lineage [07d19636abaa, 09150071c8cb]; MOST STABLE game in the project, σ 0.0517; 20-seed mean GE 0.0985, calibrated komi_p2 0.05)
**Substrate:** grid (axis 8, 64 active cells / 64 grid positions, max_degree 4, no holes, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game b12ff78f1c1d` (see `briefing_grid_b12ff78f1c1d.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Flat 8×8 grid, 64/64 active, no holes. Cell index `c = y*8 + x`. max_degree 4 (orthogonal). Interior cells 4 neighbours, edges 3, corners 2.

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = **72**.

**Action space.** 66 (64 place + slot 64 unused + pie 65). Placement anywhere-empty (adjacency vestigial, verified — full board legal from move 1).

**Placement & capture.** **Custodian, threshold=1** (the structural differentiator from the menger/carpet outnumber games). Placing such that an opponent stone (or contiguous run) is bracketed on opposite orthogonal sides **flips it to the mover**. Verified live: P1 at (3,3)=27 then (5,3)=29 flipped P2's (4,3)=28 → P1 jumped 1→3 pieces. **Flips swing both ownership and the influence field** — an Othello-like lever, far more active than the menger captures.

**Propagation.** influence, r=1, strength 1.0, **decay 0.5**. Self +1.0, each neighbour +0.5; opponent influence negative on the field. Packing law 1 + k (line tip +2, inner corner +3).

**Win condition.** threshold-race > **20.0**; mirror P2; **engine komi = 0.05 × 20 = 1.0** (helper shows 0.05 — soft violation). max_turns 72 (draws possible, ~0–3%).

**Pie rule.** True (action 65, P2-only on move 2).

**Degeneracy check.** `adjacent_empty` vestigial; helper under-displays komi (real +1.0). Threshold dispatch correct. **Greedy top-K ignores custodian captures entirely** — the helper hint is blind to the game's main tactical lever.

---

## Phase 2 — Strategic Play

### Game 1 — Custodian flip probe (the crown mechanic)
Sequence: `27,28,29` (3 plies). P1 27=(3,3), P2 28=(4,3), P1 29=(5,3) **brackets and flips (4,3)** → P1 1→3 pieces; score swung from P2-ahead (+0.55) to P1 +1.0 / P2 +0.05. A single move both denied P2 a stone and converted it to P1 — a ~2-point swing for the price of one placement. **This is a genuinely tactical lever, unlike the inert menger outnumber captures.**

### Game 2 — Race to 20 (mirror)
Sequence: `27,36,28,35,19,44,20,43,18,45,26,37,11,52,12,51,10,50` → P1 +20.0 (exactly, not > 20) / P2 +19.05. The symmetric race stays neck-and-neck; komi +1.0 ≈ one tempo, so the seats are near-balanced in mirror play and the race can hover at threshold.

### Game 3 — Contested / flip-aware play
With custodian-1, **placement safety matters**: a lone stone dropped between two enemies is immediately flippable next turn. Strong play builds compact blocks (whose interiors can't be bracketed) and looks for chances to flip the opponent's frontier stones for a double-duty swing (deny + gain). Flips require 2-stone bracket setups, so they don't fire every move, but the *threat* shapes where both sides place.

### Strategy guides
**P1:** build a compact central block (decay-0.5 packing, +contacts), keep stones un-bracketable, and flip P2's exposed frontier stones when a bracket is one move away. Don't over-extend into flippable positions.
**P2:** mirror + komi keeps you even; deviate to flip P1's frontier when profitable. Pie (65) if P1's opener is strong.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Yes (diversity 1.000): packing-race plans plus flip-tactics give real opening variety. The custodian layer adds a second axis of decision absent from the menger/carpet games.
**Counter-play.** Real: flip/re-flip battles, block-packing, pie. The flip mechanic means captures are a live counter (unlike every other slate game).
**Short-term vs long-term.** Mostly ~1-ply, but flip setups span 2 plies and create genuine tactical sequences (bracket threats, recaptures). Medium-term horizon is the best in the slate among the race games.
**Emergent concepts.** **Othello-style flips in service of an influence race** — the standout emergent. Placement-safety (don't get bracketed), frontier flipping, double-duty captures (deny + gain), field-swing on flip.
**Does grid matter?** The flat 8×8 is the *cleanest* substrate for the custodian mechanic (orthogonal brackets work uniformly, no holes to break lines). Substrate is a neutral stage here — the *rules* (custodian + decay 0.5) carry the game, not the topology. This is the R19 finding that grid < menger/carpet for substrate contribution, but here the rule-set compensates.
**Does the kernel matter?** decay 0.5 is load-bearing for the packing race; the flip swinging the field on top of it is what gives the game texture.
**Capture contribution.** **The highest of any slate game.** Custodian-1 flips actually fire and swing the race; they are the game's defining lever.
**First-mover / seat balance.** **G3 graded FAIL_RUSH_BROKEN** — greedy P1 winrate 0.00 with greedy seat bias 0.50 (seats fully determined vs a greedy opponent), though *sampled* P1 winrate 0.47 (balanced). My play: komi +1.0 ≈ one tempo, races hover at threshold → near-balanced for skilled, flip-aware play. The "rush-broken" verdict reflects the influence-only greedy heuristic (which ignores flips); capture-aware agents have more counterplay. Treat balance with suspicion but not as catastrophic.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.**
(a) Threshold-race influence ≈ territorial accumulation.
(b) **Custodian capture = Othello/Reversi flipping.** This is the irreducible new piece vs the menger/carpet games.
(c) "Othello-flip + influence field + threshold-race on a flat grid" has no clean single published analogue — it is Othello's capture grafted onto an influence-accumulation race. The closest is a Reversi/area-scoring hybrid.
(d) Flat 8×8 grid — the plain substrate; the novelty is the rule combination, not the board.
(e) Expert transfer: an Othello + territory-game player gets the core in ~10 min, but the flip-for-influence-swing interaction (flips change the *field*, not just stone count) is a genuinely new wrinkle to reason about.

**Closest known-game analogue:** an Othello/Reversi-flip mechanic driving an influence-accumulation race — a hybrid with no exact published match.
**Comparison to R8 Connection Go (4.10).** Different family (race vs connection), but **comparable or better tactical liveness**: R8's captures were inert; here custodian flips are the central lever and actually fire.
**Comparison to R19/R20.** The custodian-flip-in-a-race combination is *more* tactically alive than the R20 menger/carpet champions (whose captures were inert). It is the one R21 game where the capture rule genuinely matters in play.

**Novelty score (post-adversary):** **4/10.** Above the menger/carpet siblings (3) because the Othello-flip-driving-an-influence-race is a real, less-common combination with an irreducible new interaction (flips swing the field). Below genuinely-new (8) because both halves (Reversi flips, influence race) are individually well-known. Anchor: R8 4.10, R19 top 4.8.

---

## Phase 5 — Verdict

**Team ID:** team-3
**Game ID:** b12ff78f1c1d
**Rules Summary:** On a flat 8×8 grid, drop stones with a short influence field and race your owned-influence total to 20; bracket an opponent stone on opposite sides to flip it to your colour (Othello-style), swinging both ownership and the field. Custodian flips are the live tactical lever; pie + komi balance the seats.
**Substrate:** grid, axis 8, 64/64 cells, max_degree 4, pie_rule=True, komi_p2=0.05.
**Turn Structure:** alternating
**Hybrid actions:** no.
**Soft violations flagged:** G3 FAIL_RUSH_BROKEN (greedy bias 0.50, sampled 0.47); helper under-displays komi (real +1.0) and its greedy hint ignores custodian captures entirely; `adjacent_empty` vestigial.

### Scores (1–10)
- **Strategic Depth: 4** — The custodian flip adds a real second decision axis (bracket threats, placement-safety, recaptures) on top of the packing race — the most of any R21 race-game, though still modest (most moves ~1-ply, flips span 2).
- **Emergent Complexity: 5** — Othello-flips in service of an influence race: field-swinging captures, placement-safety, double-duty flips. The richest emergent texture in the slate.
- **Balance: 4** — G3 rush-broken on the greedy (capture-blind) heuristic, but komi +1.0 ≈ one tempo and flip-aware play hovers at parity. Real concern, not catastrophic.
- **Novelty (post-adversary): 4** — Reversi-flip driving an influence race; an uncommon, genuinely-interacting combination.
- **Replayability: 5** — Diversity 1.000; flip tactics + packing plans give the best opening variety in the slate.
- **Overall "Would an agent team play this again?": 4.2** — The most *playable* and tactically alive R21 game: the custodian flip is the one capture rule that actually matters, and it lifts the game above the inert-capture menger/carpet races. Stability **did** track quality here (most stable AND best-playing). At/above R8 replay (4.10); still below the R19 ceiling (no clear path past 5.0).

### CLOSEST KNOWN-GAME ANALOG
An Othello/Reversi flip mechanic grafted onto an influence-accumulation race — no exact published match; inside the corpus, the most tactically-alive R21 game.

### KILLER FLAWS
- G3 rush-broken seat bias (0.50 greedy) — balance leans on capture-aware play to recover.
- The race objective still caps depth; flips require setup and don't fire every move.

### BEST QUALITY
**Custodian flips that swing the influence field** — the only R21 capture rule that is a genuine, frequently-usable tactical lever. Bracket-and-flip a frontier stone to deny the opponent and gain field in one move; it makes placement-safety and recapture real considerations.

### GRID STRUCTURAL CONTRIBUTION
Neutral-to-positive: the flat grid is the cleanest stage for uniform orthogonal brackets (no holes to break custodian lines). Unlike R19's finding that grid < menger/carpet, here the *rule-set* (custodian + decay) carries the game and the plain substrate is an asset, not a liability.

### IMPROVEMENT IDEAS
**Single best change:** fix the seat balance properly (the rush-broken 0.50 greedy bias) — e.g. a swap/komi scheme tuned against *capture-aware* play, or a slightly larger board so the rush is slower — to convert "tactically alive but rush-broken" into "tactically alive and fair."
Secondary:
- Surface custodian captures in the helper's greedy hint (currently influence-only, blind to the main lever).
- Consider threshold/board tuning so flip battles, not the opening rush, decide games.
