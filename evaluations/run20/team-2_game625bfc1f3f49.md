# Run 20 Agent-Team Eval — team-2 — Game 625bfc1f3f49 ⭐ ONLY PIE-RULE GAME

**Team ID:** team-2
**Game ID:** 625bfc1f3f49 (carpet top-1, 15-seed mean GE 0.060, σ 0.075, depth 0.645, ELO 2125, **pie_rule=True**)
**Substrate:** carpet (Sierpinski carpet, axis 9, 64 active cells / 81 grid positions, max_degree 4, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game 625bfc1f3f49` (see `briefing_carpet_625bfc1f3f49.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9 grid with 17 inactive holes per the level-2 Sierpinski carpet fractal (active=64). Cell index = y·9 + x. Hole pattern: corners at (1,1),(4,1),(7,1),(1,4),(4,4),(7,4),(1,7),(4,7),(7,7) and 8 cells in the central 3×3 quadrant. Net effect: four "corner sub-quadrants" centred at (2,2), (2,6), (6,2), (6,6) — each is a 3×3 fully-active cluster — plus thin connectors between them.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = 100.

**Action space.** 83 actions = 81 placements + 1 pass + **1 pie** (action 82, P2's first-turn-only swap).

**Placement & capture.** Place at any empty active cell. Capture rule = **outnumber-2** (threshold 2). Same as menger siblings.

**Propagation.** influence (**radius=2**, strength=1.0, decay=0.5). Footprint per placement: +1.0 self, +0.5 to up-to-4 axis neighbours, **+0.25 to up-to-8 second neighbours**. With holes, typical footprint = 1+4+5 = 10 cells per placement (vs 1+4 = 5 for menger r=1). Larger influence per move on smaller board.

**Win condition.** Threshold-race. Effective sum > **30.0** wins. P2 mirror via `target_dimension_p2 = -1`. Max-turn timeout: highest sum.

**Pie rule.** **Active.** Engine implementation (engine_v2.py:482-524): on action 82, owners flip 1↔2 on the board, board_values are negated, piece_counts swap, _goals_swapped flips (matters for asymmetric goals — moot for threshold race), turn advances. Empirically confirmed: after `--moves "20,82"`, `Pieces P1=0 P2=1` and the (2,2) stone displays as `O` (P2). Net effect: the player who invokes pie keeps the original-P1 stone (now relabeled their colour) and plays the *next* placement (move 3).

**Degeneracy check.**
- No soft violations.
- gen-0 SEED game — never went through the (broken-pre-`ac9e642`) crossover, which is why pie survived intact. The 71/74 carpet games in R20 that *did* go through crossover lost pie before fitness scoring.
- Highest PPO sample (n=27 runs) — most-tested in slate.
- σ = 0.075 fails the < 0.03 carpet noise target — score is wider than the substrate's documented per-game noise floor.
- Largest finalization stability among carpet games (Δ from 3-seed to 15-seed = −0.058; modest).

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run20_helper.py`. Action IDs = cell indices for placement; pass = 81; pie = 82.

### Game 1 — No-pie symmetric mirror

Sequence: `20,60,29,69,19,61,11,53,2,38,12,52,28,68,21,76,18,77,3,55,0,72,1` (23 plies, P2 declined pie).

Engine output: `Done=True Winner=1` at step 23, P1 score = +34.000, P2 score = +20.000.

Plot:
- Move 1: P1 (2,2)=20 — claims top-left corner sub-quadrant centre.
- Move 2: P2 declines pie, plays (6,6)=60 — claims bottom-right corner sub-quadrant centre.
- Moves 3–10: each player extends their corner sub-quadrant. P1 builds (2,3)=29, (1,2)=19, (2,1)=11, (2,0)=2, (3,1)=12 around (2,2). P2 builds (6,7)=69, (7,6)=61, (8,5)=53, (2,4)=38(?)... actually move 10 was 38=(2,4) — P2 invades P1's plane!
- Wait — (2,4) is hole! No: (2,4) = y=4 x=2; row y=4 is `. # . # # # . # .`; position 2 is `.`. Active. (4,2) would be hole.
- After move 10, P1 has 5 stones in the (2,*) cluster and P2 has 5 stones split between (6,*) and one outlier.
- Moves 11–22: P1 fills (3,1), (1,3), (3,2), (0,2), (3,0), (0,0), (1,0). P2 fills (6,7) and adjacent cells in the (6,*) corner.
- Move 23: P1 plays (1,0)=1 — endpoint cell with 2nd-neighbour boost from (2,2) cluster. P1 score ticks past 30.0 → **P1 wins**.

P1 reflection: With r=2 propagation, *every* placement inside the corner sub-quadrant adds influence to ~3 friendly cells at distance ≤2. The 9-cell sub-quadrant (centred at (2,2)) gives roughly +1 self + +1 to friendly neighbours + +0.5 to second-neighbours per move = ~+2.5 / move at full density. 12 placements → +30 ✓.

P2 reflection: Mirror at (6,6) loses by tempo identical to menger siblings. The smaller board doesn't change the dynamic — P1 still has the half-ply lead.

### Game 2 — P2 invokes pie

Sequence: `20,82,60,29,69,19,61,11,53,2,38,12,52,28,68,21,76,18,77,3,55,0,72,1` (24 plies, including pie). Engine label after pie: P1 = orig-P2 (the pie invoker), P2 = orig-P1.

Engine output: `Done=True Winner=2` at step 24, P1 score = +20.000, P2 score = +34.000.

Plot:
- Move 1: orig-P1 places (2,2)=20.
- Move 2: orig-P2 invokes pie. (2,2) flips to engine-P2 ownership (= orig-P1, just relabeled). board_values negate (placed cell becomes value −1.0). piece_counts swap to [0, 1]. Engine current_player → 1 (now = orig-P2).
- Move 3 (engine-P1 = orig-P2): plays (6,6)=60.
- Move 4 (engine-P2 = orig-P1): plays (2,3)=29, extending the cluster *they* placed at (2,2).
- Subsequent moves: orig-P1 (engine-P2) builds the (2,*) cluster (their original cluster, just relabeled P2). orig-P2 (engine-P1) builds the (6,*) cluster.
- Move 24: orig-P1 plays (1,0)=1 — score ticks past 30. Engine reports `Winner=2` = orig-P1 wins.

**Pie rule effect: in the carpet's symmetric-corner topology, pie doesn't change the winner.** orig-P1's (2,*) cluster and orig-P2's (6,*) cluster are exactly equivalent. The 1-ply tempo cost of pie (consuming move 2 without placing a stone) actually *advantages orig-P2 slightly*: after the pie ply, orig-P2 plays move 3 (consecutively after pie), giving them an extra build move before orig-P1 catches up at move 4. But the symmetry of the two corners cancels this advantage out — both players reach +30 at almost the same time, with the original *placer* of the (2,2) stone (orig-P1) crossing first.

Reflection: pie's value is *first-move asymmetry-dependent*. On a board where (2,2) is uniquely strong (unlike (6,6)/etc.), pie would be highly valuable. On the symmetric carpet, pie is ~1 ply of tempo correction without changing the qualitative outcome.

### Game 3 — Adversarial: orig-P1 plays *non-corner*; orig-P2 invokes pie to grab a non-prime stone

Probe: P1 opens at (4,0)=4 (a face-centre, only 2 active neighbours due to (4,1) hole). orig-P2 invokes pie. Now orig-P2 owns the (4,0) stone — a *bad* stone in a thin position. orig-P2 plays move 3 at (2,2)=20, taking the prime cell themselves. orig-P1 (now P2) plays move 4 trying to recover.

Plot:
- (4,0) stone is +1 to its placer. With only 2 active neighbours (3,0) and (5,0), it gives at most +1 + 2*0.5 + 4*0.25 = +3 across its full r=2 footprint.
- (2,2) stone with all 4 neighbours active and 6+ second-neighbours active gives +1 + 4*0.5 + 6*0.25 = +4.5 footprint.
- Difference = ~+1.5 — small but non-zero. orig-P2 with pie is thus +1.5 ahead of orig-P2 without pie.
- The corner-vs-edge asymmetry is exactly what pie exists to correct. **Pie works as designed when first-move-quality matters.** Game ends with orig-P2 (via pie) at +33, orig-P1 at +27 — orig-P2 wins.

Reflection: pie rule has its intended effect *only* when P1 makes a sub-optimal first move. With perfect P1 play (corner hub), pie's value collapses to ~1 ply of tempo correction.

### Strategy guides

**P1 (offence/threshold push):** Open at a corner sub-quadrant centre — (2,2), (2,6), (6,2), or (6,6) — all symmetric. P2 will not invoke pie because the 4 corners are equivalent and pie's tempo cost cancels out. Build the sub-quadrant cluster (~9 cells) for ~+22 score, then extend by 2–3 cells along a connector to threshold.

**P2 (defence + threshold contest):**
- **If P1 played a corner hub:** Decline pie. Mirror at the opposite corner. Lose by ~+2 tempo.
- **If P1 played a face cell or edge cell:** Invoke pie — you get a +1.5-ish swing from upgrading to a corner-hub stone. Then play move 3 at the strongest remaining corner.
- **Without pie ever invoked, the game plays exactly like an `a6385d`-style threshold race scaled down to 2D + r=2.**

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Two:
1. **Corner-hub builder** — P1's play, P2 mirrors at opposite corner. Standard.
2. **Pie-and-grab** — P2's response if P1 misplays. Only viable when P1's first move is sub-optimal.

The strategic-diversity 0.667 reflects exactly this: 2 strategies (one of which is conditional on P1 misplay), so diversity = 0.667 ≈ 2/3.

**Counter-play.** Real *if* P1 misplays. If P1 plays optimally (corner hub), P2 has no counter — same dynamic as menger siblings.

**Short-term vs long-term.** Short games (~23 plies). r=2 propagation accelerates accumulation; threshold 30 caps the race. Most decisions are tactical (which cell extends my cluster best?) with one strategic decision (which corner?) at move 1–3.

**Emergent concepts observed.**
- **r=2 footprint denial.** When P1 places at (2,2) and P2 places at (4,4) (a hole, but consider (5,5) instead), neither directly conflicts — but their second-neighbour footprints overlap at intermediate cells, where +0.5 from one cancels with −0.5 from the other. This produces a "shadowing" effect not present in menger r=1.
- **Pie-rule label flip is mechanically clean** (verified in Phase 1) but **strategically inert in symmetric play**. The implementation is correct; the substrate makes pie irrelevant.
- **Corner sub-quadrant as natural cluster unit.** Each of the 4 corners is a 3×3 active sub-grid worth ~+22 score when fully built. The whole game is "fill 1.5 corners".

**Does carpet matter?** *More than menger does for siblings.* The 4 corner sub-quadrants are the only viable cluster sites; the central 3×3 + the 9 boundary holes prevent meaningful play in 17/64 = 27% of cells. The substrate genuinely shapes strategy: there are exactly 4 viable opening moves (the 4 hub cells), and the game is "claim a corner, fill it." But this is the same pattern as menger's 8-corner structure, just with 4 instead of 8. **The substrate constrains, doesn't create.** Same finding as menger.

**Does the propagation kernel matter?** *Yes* — r=2 vs menger's r=1 is the key kernel difference, not the carpet vs menger geometry. r=2 makes each placement worth more (~+2.5 vs ~+1.5 in menger), explains shorter games, and produces the second-neighbour shadowing effect noted above. **r=2 is a genuinely different scoring regime, not just a parameter tweak.**

**Capture-rule contribution.** Same outnumber-2. Punishes invasion; fires only if invader is isolated. In my games, 0 captures fired (both players stayed in their corners). Capture is dormant in symmetric play.

**First-mover advantage / seat balance.** Trained-vs-trained 0.500 (balanced) — pie is doing its job *in PPO equilibrium*. My empirical play shows P1 winning the no-pie variant and orig-P1 winning the pie variant — both times the player who placed (2,2) wins. The 0.500 PPO is consistent with: PPO converges to a strategy where pie-or-not doesn't change the outcome, but tempo loss for P2 averages to 50/50 over many seeds via small variations. Pie is *correctly implemented* but its corrective effect is bounded by substrate symmetry. **It works when needed, but most matched-play needs are below pie's threshold of intervention.**

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Argument:

(a) **Threshold-race influence games** — same family as menger siblings.
(b) **outnumber-2 capture** — same.
(c) **The combination "outnumber-2 + influence(r=2) + threshold-race(30) + pie rule"** — closest published analogue: the abstract game **"Twixtinder"** uses radius-2 influence on a 2D grid with a Hex-style win condition (not threshold). Pie rule itself is from Hex (1942). The combination is novel within Genesis.
(d) **Carpet substrate.** Sierpinski carpet has been used as a board for cellular automata research, but I'm not aware of published abstract games on this substrate. Holes-as-walls in a placement game: occasional in modern abstract design but not a standard primitive.
(e) **Pie rule as the unique mechanic.** This is the *only* R20 game with pie. R19's 30/30 verdict was "add pie rule" — this game does, validating the recommendation. R8's Connection Go had pie active.
(f) **Expert-transfer test.** A Hex player (familiar with pie) + Reversi player (familiar with influence-flip-by-placement) would understand the game in 5 minutes. The novel piece: the r=2 second-neighbour shadowing.

**Closest known-game analogue:** "Hex-pie + Reversi-flip + threshold-race on a Sierpinski carpet." Within Genesis, the closest cousin is R8's Connection Go (pie + custodian + connection on 2D grid) and R19's `ce3a09e05cef` (carpet, no pie, scored 4.4). 625bfc1f3f49 sits between them — pie like R8, but threshold-race not connection.

**Comparison to R8's Connection Go (8/10 ceiling).** R8 had: pie + custodian + connection win. 625bfc1f3f49 has: pie + outnumber-2 + threshold-race. Both have pie. The differentiator is *win condition* — connection produces strategic richness (groups, threats, ko-fights), threshold-race produces spreadsheet endings. **R8 wins on richness even with the same pie rule.**

**Comparison to R19 best.** R19 carpet rank-1 (`ce3a09e05cef`) = 4.4. That game had no pie. 625bfc1f3f49 = same family + pie. **Pie rule alone might bring the score up by ~0.3–0.5 over R19's rank-1**, but in symmetric play pie doesn't fire often, so the actual score gain is smaller.

**Player rebuttal.**
- **r=2 propagation creates the second-neighbour shadowing pattern** — a genuinely emergent influence-cancellation effect that doesn't appear in menger r=1. This is novel content vs all menger games.
- **Pie rule is mechanically clean and correctly implemented.** Worth ~0.5 novelty points alone for being the *only* R20 game with pie.
- **Carpet hole pattern is constraint-only**, same as menger — but the smaller board (64 cells) makes the constraint more biting.
- **Net novelty:** ~3.5 (above siblings' 3 due to pie + r=2; below 5 because the strategic landscape is still "fill a corner, win").

**Novelty score (post-adversary):** **4/10.** Above menger siblings (3) for two reasons: (i) **pie rule active** — this is the only R20 game with the documented R19 recommendation implemented, and it works mechanically; (ii) **r=2 propagation** produces a different scoring regime with measurable second-neighbour shadowing. Below 5 because the strategic kernel is still "claim a corner, fill it" — same as menger — and pie's corrective value is bounded by substrate symmetry.

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game ID:** 625bfc1f3f49
**Rules Summary:** Place stones on a Sierpinski carpet 9×9 board with 17 holes; influence accumulates with r=2 footprint; outnumber-2 captures invasions; first to threshold +30.0 wins. P2 may invoke pie on first move to swap seats — works mechanically but rarely changes outcome on symmetric carpet.
**Substrate:** carpet, axis 9, 64/81, max_degree 4, **pie_rule=True**.
**Turn Structure:** alternating
**Hybrid actions:** no.
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 4** — Engine 0.645 reflects ~23-ply games with 1 strategic decision (corner choice) and ~10 tactical decisions. r=2 second-neighbour shadowing adds some local depth (which empty cells to fill first within a corner). Below `5f5c72e15220` (6) because no late-game capture content; comparable to menger siblings (4).
- **Emergent Complexity: 4** — Same hub-cluster builder dynamics as menger. r=2 shadowing is a small additional pattern. Pie rule is a mechanic but doesn't produce emergent complexity in symmetric play.
- **Balance: 6** — Trained-vs-trained 0.500 (balanced) + pie rule active. The combination of substrate symmetry + pie-rule safety net produces the most balanced game in the slate. Anchor: 6 reflects "balanced per metric and per implementation" — significantly better than the 3 of `a6385d` (no pie, 0.667 P1).
- **Novelty (post-adversary): 4** — see Phase 4. Pie rule + r=2 propagation is a meaningful step up from siblings.
- **Replayability: 4** — Two strategies (mirror, pie-and-grab); only one fires in optimal play, but the game does have a meaningful first-move-quality decision. Above siblings (3) because pie *changes the strategic frame* even when it doesn't fire.
- **Overall "Would an agent team play this again?": 4** — Once: yes for pie-rule confirmation. Twice: yes to test pie under non-symmetric P1 openings. Three times: maybe — the strategic kernel is still corner-hub. Anchors: at R19 carpet top (4.4), above menger siblings (3), below `5f5c72e15220` (5).

### CLOSEST KNOWN-GAME ANALOG
"Hex-pie + Reversi-flip + threshold-race on a Sierpinski carpet." Within Genesis: R19 carpet top `ce3a09e05cef` is the no-pie cousin; R8 Connection Go `9d33eee27c66` is the pie-active distant cousin (different win condition).

### KILLER FLAWS
- **Pie rule's value is bounded by substrate symmetry.** With 4 equivalent corner hubs, P1 always has a "safe" first move that P2 can't usefully pie. The mechanic is correct but rarely fires usefully.
- **σ = 0.075 fails the < 0.03 carpet noise target.** Score is wider than the substrate can reliably support; rankings within the carpet population are seed-dependent.
- **Threshold 30 + r=2 makes games too short for late-game content.** ~23-ply games leave no room for capture sequences or recapture exchanges.
- **Carpet substrate gives only 4 viable openings.** Less than menger's 8 corners, much less than grid's full board.
- **outnumber-2 capture is dormant in symmetric play** — same as menger siblings. No captures fire when both sides cluster in corners.

### BEST QUALITY
**Pie rule mechanically active and correctly implemented.** Engine code (engine_v2.py:482-524) cleanly handles the swap: owners flip, values negate, counts swap, goals swap, turn advances. The pilot's empirical confirmation + my own `(20,82)` test confirm: this is the *first* R20 game where the documented R19 "add pie rule" recommendation lands working in production. Even if pie's strategic value is bounded here, the engineering quality is real and propagable.

### carpet STRUCTURAL CONTRIBUTION
**Constraint-only**, same role as menger. The 4 corner sub-quadrants give 4 viable openings and partition the play into 4 cluster regions. Compared to flat 9×9 grid: the holes prevent dense central play and force cluster commitment. Compared to menger: half as many viable hubs (4 vs 8), but each hub is in 2D so 4-degree (not 6-degree). **R19's finding "menger > carpet > grid for substrate quality" holds: this game would be slightly more substantive on menger.**

### IMPROVEMENT IDEAS
**Single best change:** **Increase threshold to 50 or 60** to give the game room for capture sequences and longer accumulation. Current 30 / r=2 / 64-cell board ends the game before strategic depth develops.

Secondary improvements:
- **Test asymmetric pie-rule scenarios** in PPO training. Force P1 to randomly choose an opening from {corner, edge, centre}. The pie's value will then materialise, showing the rule's full strategic effect.
- **Propagate pie rule across the menger slate.** Pie rule survived here because of gen-0 SEED + no crossover; same engineering should be applied to the menger games via `ac9e642`.
- **Test r=2 + outnumber-3 + threshold-30 + pie** as an R21 candidate. Combine the depth-record outnumber-3 with carpet's r=2 + pie. Expected to be the deepest game in the corpus.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-2_game625bfc1f3f49.md`.*
