# Run 20 Agent-Team Eval — team-3 — Game a6385db22c0b

**Team ID:** team-3
**Game ID:** a6385db22c0b (menger top-1 by 15-seed mean GE 0.241, σ 0.120, depth 0.763)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game a6385db22c0b` (see `briefing_menger_a6385db22c0b.md` for full rules and engine internals).

---

## Phase 1 — Rule Comprehension

**Board.** Level-2 Menger sponge embedded in a 9×9×9 cube — 400 active cells out of 729 grid positions (329 holes). Cell index `c = z*81 + y*9 + x`. The hole pattern leaves 8 deg-6 "hub" cells at the centers of the 8 outer level-1 sub-cubes — coordinates `(x,y,z) ∈ {2,6}³` — plus 24 deg-5 cells one axis-step from each hub face. Most other active cells are deg-3 or deg-4. Hubs are pairwise non-adjacent (distance ≥ 4 axis-steps).

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = 100.

**Action space.** 730 actions = 729 placement + 1 pass. **No move actions** (D1 hybrid ban active). Placement legal at any empty active cell.

**Placement & capture.** Placement: empty active cell, no first-move restriction. Capture rule = **outnumber-2**. On placement at A: every enemy stone N adjacent to A is checked; if N has ≥ 2 friendly stones (counting just-placed) among its active neighbours, N is **cleared to empty** (ownership → 0; influence stays on the board but is unowned, so contributes nothing to either score).

**Propagation.** influence (radius=1, strength=1.0, decay=0.5). Every placement adds ±1.0 to `board_values[A]` and ±0.5 to each active axis-neighbour. P1 sign +, P2 sign −. Clamped to [−100,100]. Empirically, an unobstructed deg-6 hub claim contributes +1.0 self + 0.5 × (number of own neighbour placements built up to 6) → up to +4.0 final value once fully fortified.

**Win condition.** Threshold-race. After every move, P1 = Σ values on P1-owned cells; P2 = −Σ values on P2-owned cells. First to **> 57.974** wins. `target_dimension_p2 = -1` means P2 mirrors P1's accumulator (negation). Equal → draw. Max-turn timeout: highest effective sum.

**Pie rule.** False — pie was lost in crossover before `ac9e642`. P1 keeps its first-mover advantage uncorrected.

**Degeneracy check.**
- The Menger hole pattern reduces 729 → 400 active cells but leaves a clear deg-6 / deg-5 / deg-3 hierarchy. The 8 hubs are the dominant scoring loci.
- No dead rules; all of capture, propagation, threshold-race fire.
- Capture window is narrow: a hub becomes capture-immune once its placer has 5/6 neighbour cells filled with own stones (P2 cannot reach 2 adjacent placements).

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run20_helper.py`. Action IDs = cell indices for placement; pass = 729.

### Game 1 — P1 hub-rush, P2 mirrors

Sequence: `182,506,186,510,218,542,222,546,183,507,181,505,191,515,173,497,263,587,101,425,187,511,185,509,195,519,177,501,267,591,105,429,219,543,217,541,227,551,209,533,299,623,137,461,223,547,221,545,231,555,213,537,303,627,141,465,102,416,104` (59 plies).

Plot:
- Plies 1–8: each side claims 4 deg-6 hubs. P1 takes z=2 hubs `(2,2,2)(6,2,2)(2,6,2)(6,6,2)`; P2 takes z=6 hubs symmetrically. Score after ply 8: P1 +4 / P2 +4.
- Plies 9–56: each player walks through their 24 hub-neighbours in order. Every neighbour placement scores +2.0 effective (+1.5 from self cell now sitting at +1.5 = +1.0 self + +0.5 spillover from hub; +0.5 added back to the hub which is already owned).
- Score progression is mechanical: each side gains exactly +2 per ply, +4 per round-trip. Ply 56: P1 +52 / P2 +52.
- Plies 57–59: hub-neighbours exhausted; each player picks the highest-overlap deg-3/4 cells. P1 plays `(3,2,1)` which sits adjacent to two own stones (the (2,2,1) hub-neighbour and (3,2,2) hub-neighbour) → +2.5. P2 picks `(2,5,5)` adjacent to two own. Ply 59 P1 places `(5,2,1)` to break +57.974.

P1 reflection: First-mover advantage compounds exactly as predicted. The 4-hub split is forced — P2 cannot deny without giving up a symmetric hub.

P2 reflection: With pie OFF, mirror strategy loses to tempo. P2 needs +57.974 after at most 28 P2 plies; achievable by ply 56 = +52 + 6 plies of double-overlap = +56-58. P1 reaches it ~3 plies sooner.

### Game 2 — P2 hub denial (cross-layer contest)

Sequence: `182,222,218,186,506,542,510,546,…` (53 plies, P1 wins).

Plot:
- P1 opens `(2,2,2)`. P2 immediately takes a P1-layer hub `(6,6,2)` — denying P1 a 4-hub z=2 set.
- P1 grabs `(2,6,2)` to keep 2 z=2 hubs. P2 grabs `(6,2,2)` — now hubs split 2 z=2 each.
- Plies 5–8: each side claims its 2 z=6 hubs without contest.
- Plies 9 onward: greedy continuation finds non-hub-neighbour deg-5 cells around the upper layer (z=0,1) where P1's own stones already sit. P1 reaches +58 at ply 53.

Reflection: P2 gains nothing from cross-layer denial — both players still end with 4 hubs and same neighbour count. The placement order shifts but the threshold-race is symmetric in hub geometry. P1 still wins by tempo.

### Game 3 — Adversarial capture / fortification race

Sequence (greedy capture-aware): `0,1,9,2,18,3,19,4,20,5,11,12,11,6,21,12,11,7,11,12,12,8,84,3,83,2,22,14,23,15,24,104,23,105,24,25,24,33,24,34,27,114,28,17,29,26,36,35,38,42,45,44,46,51,47,52,54,53,55,60,56,61,57,62,58,59,63,68,140,59,65` (71 plies, P1 wins +58 / P2 +54.5).

Plot:
- Greedy with capture-bonus drives both players into tight clusters at the (0,0,0) corner. P2 captures P1 stone at `(2,1,0)` (cell 11) twice; P1 re-places, P2 re-captures. **Capture loops emerge**: same cell flips empty → P1 → empty → P1 because P2's two flanking stones make any P1 replacement immediately re-capturable.
- This is a stable ko-like fight, but the engine has no ko-rule and the cell is genuinely losable each cycle. P1 burns moves on captured stones — net `+0` per replacement — while P2 nets `+1` per capture (the surrounding pair of P2 stones each contribute +0.5–1.0).
- Despite this drag, P1 wins by ply 71. The capture-loop only delays the threshold-race by ~12 plies because P1 has a tempo lead from move 1 and the deg-3 corner cells P1 keeps re-placing are low-value (~+0.5 net) — P2's net gain per capture cycle is only ~+0.5–1.0, vs +2 from clean hub-neighbour play. Capture is a **drag**, not a kill.

Reflection: The outnumber-2 capture creates a real fortification dilemma — when you place a deg-6 hub you must immediately start filling its neighbours before P2 can put 2 stones around it. But in the menger geometry the 6 neighbours are pairwise non-adjacent and a single P2 placement only threatens capture if a second is added; P1 can fortify by placing 1 own neighbour after P2's first flank, blocking the sandwich for that hub. Capture rarely fires in clean play because building outpaces capturing.

### Strategy guides

**P1 (offence/threshold push):** Open at any deg-6 hub. After P2's response, immediately fortify by placing one neighbour of your hub *before* extending to a new hub if P2 has placed adjacent — denial of capture-flank takes priority. Then walk through the 6 neighbours of each owned hub. With 4 hubs × 6 neighbours = 24 hub-neighbour moves at +2 each, you reach +52 by ply ~56; +6 more from any deg-5 cells with own-cell overlap finishes at ~+58.

**P2 (defence + threshold contest):** Without pie rule, accept ~3-ply tempo deficit. Mirror P1's hub claims at z=6 (or contest z=2 hubs and accept symmetric trade). DO NOT pursue captures unless P1 has placed a hub but failed to fortify — capture costs 2 plies for ~+1 net P2 gain, vs +4 from 2 clean hub-neighbour plies. Capture is a tactical option for late-game when own hub-neighbour space is exhausted.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Two near-equivalent plans for P1 (z=2 hubs vs cross-layer hub mix) and two for P2 (mirror vs contest); the choice affects opening 8 plies but not the long run. **Capture-driven defence** is a third style that emerges under adversarial play but loses to clean accumulation.

**Counter-play.** Limited. Hub-rush has no real counter when pie is off — P2's tempo deficit is structural. Contested-hub denies symmetry but doesn't change the outcome, only the move order. Capture is a drag, not a kill (Game 3).

**Short-term vs long-term.** Long. Threshold 57.97 with each move worth +2 means ~28 plies per side of high-value play, then ~3–6 plies of overlap-mining. Total game length 53–71 plies. The "decision" each ply is mechanical: pick best-overlap empty cell. **Strategic horizon is shallow — one move ahead suffices for ~95% of choices.**

**Emergent concepts observed.**
- **Hub topology.** The 8 deg-6 cells at `(x,y,z) ∈ {2,6}³` are the dominant scoring scaffold. The substrate's defining contribution.
- **Hub-neighbour walk.** The 24 (per player) deg-5 cells one step from a hub each give +2 effective per placement. Routine.
- **Fortification dilemma.** Place hub, then race to fill ≥1 of 6 neighbours before opponent can sandwich. Real but rarely contested in clean play.
- **Capture loop / engine ko.** Greedy capture-aware play produces same-cell flip cycles. Engine has no ko rule but the cycles self-terminate when one side runs out of fortifying neighbours. Mildly novel as an emergent pattern.
- **Overlap mining.** End-game search for cells with 2+ own neighbours (+2.5 placements). Tactical but minor.

**Does menger matter?** Substantially for *opening structure* — the 8-hub scaffold gives the game its identity. Replace menger with flat 9×9×1 grid: the game collapses into a 2-D influence-race with no hub hierarchy (every cell is deg-3/4). Replace with 4³ cubic: smaller hub set, shorter game, more overlap. The **fractal hole pattern is doing real structural work** by isolating the 8 hubs at distance ≥4 — they cannot share propagation. This is the substrate's positive contribution.

**Does the propagation kernel matter?** Yes. r=1, decay=0.5 produces ±0.5 spillover per placement. If r=0 (self only): hub-neighbour walk drops from +2 to +1 per ply, hubs lose value, game length doubles. If decay=1.0: too much spillover, propagation saturates and score becomes "count own cells × ~3". The current parameters are well-tuned for ~60-ply games.

**Capture-rule contribution.** Outnumber-2 fires ~3–8 times per adversarial game (Game 3) but **0–1 times in clean play**. Its existence shapes opening (you must fortify) but it rarely actually fires when both sides play accumulatively. Comparable to en-passant in chess: structural deterrent more than active mechanic.

**First-mover advantage / seat balance.** Trained-vs-trained 0.667 P1-favoured (training reference). My games: P1 won 3/3 (Games 1, 2, 3 all P1 wins). With pie OFF and a 28-ply per side accumulation race, P1 has a ~3-ply tempo lead which is decisive when the threshold is tight. **The game is not balanced.** Pie rule (had it survived crossover) would have largely fixed this — P2 could swap when P1 opens at a hub.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a re-skin of well-known mechanics. Argument:

(a) **Threshold-race influence games** are closely analogous to Othello's disc-counting end-game *without the flipping*, or Halma-style territorial accumulation. The "pile up score until you cross a number" structure is unusual but not unprecedented (cf. Tantrix scoring, Carcassonne's meeple-cluster scoring).
(b) **Outnumber-2 capture** is essentially Ataxx/Tafl ("if 2+ friendlies adjacent, enemy gone"), or close to Go's surround capture but with a fixed numeric threshold instead of liberty-based logic. Distinctive in that captured cells *clear* (lose ownership) rather than flip.
(c) **The combination "outnumber-2 + influence + threshold-race"** does not exist as a published game in my knowledge. Inside Genesis, R19 menger top games had similar shape but with surround capture (`5048f71b62fd`, 5.0/10) or outnumber-2 (`1f9191b5d4e6`, 4.8/10) — this is essentially R19 menger top-1 rediscovered in R20 with a slightly different threshold and decay. Family-level redundancy.
(d) **Menger substrate.** The level-2 sponge as a board has been gestured at in puzzle/recreational geometry but I'm not aware of a serious 2-player game using it. The hole pattern is doing real work here (isolating 8 hubs at distance 4+) but the resulting strategy reduces to "claim hub, fortify, accumulate" — the same plan would work on any sparse high-degree graph.
(e) **Expert-transfer test.** A Go + Othello + Tantrix player would understand this in 5–10 minutes. The irreducible new piece is the 8-hub menger scaffold; the rules layered on top are familiar.

**Closest known-game analogue:** "Othello-counting on a sparse 3-D fractal graph with Ataxx capture" — equivalently, R19 menger outnumber-2 winners on a different RNG seed. No clean published analogue.

**Comparison to R8's Connection Go (8/10 ceiling).** R8 was custodian + connection on a 2-D grid; the *connection* win condition created strategic depth via geometric goal-seeking (you must build a path). R20 a6385db22c0b is *threshold-race*, which has no goal-shape — only "more is better" — so depth is shallower. R8 has a clear "place this stone, complete the chain" decision; here every decision is "+2 vs +1.5". **Different family. Significantly thinner than R8.**

**Comparison to R19 best.** R19 menger top-1 `1f9191b5d4e6` was outnumber-2 + threshold-race (4.8/10). This game has the same recipe with different parameters. The hub-rush + fortification dilemma is essentially identical. **R20 is parameter-tuned R19, not a novel exploration.**

**Player rebuttal (P1 + P2).**
- The capture-loop pattern (Game 3) is genuinely emergent — neither pure Othello nor pure Ataxx produces same-cell flip-cycles in this way. But it only appears under adversarial play and self-terminates.
- The 8-hub scaffold is substrate-specific — the game's geometry literally does not exist on a flat grid. This adds maybe 1 point of structural novelty.
- What subtracts: the threshold race replaces strategic goal-seeking with arithmetic; pie OFF leaves seat imbalance; capture is rarely live; depth ceiling is hit at ~5 plies of horizon.

**Novelty score (post-adversary):** **3/10.** Above pure re-skin (2) because the menger scaffold + outnumber-2 + threshold-race combination, while present in R19, has no published external analogue. Below "genuinely new" (8–9) because R19 already produced this family and the depth ceiling is shallow. Anchor: R17 mean 3.50, this is fractionally below.

---

## Phase 5 — Verdict

**Team ID:** team-3
**Game ID:** a6385db22c0b
**Rules Summary:** On a 9³ Menger-sponge graph (400 active cells, 8 deg-6 hubs), each player alternately drops a stone; placement adds ±1 to self and ±0.5 to neighbours, and any enemy stone with 2+ friendly neighbours is captured (cleared). First player whose owned-cell influence sum exceeds 57.97 wins.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 4** — Hub-claim opening is real structure (~8 plies of meaningful choice). Mid-game collapses into mechanical hub-neighbour walk where each ply has a clear +2 best move. Engine-measured 0.763 is borderline overstated — depth is more "long game" than "deep game". Fortification dilemma adds nuance but rarely activates.
- **Emergent Complexity: 4** — Capture-loops (Game 3) and overlap-mining endgame are genuine emergents. But the rule set is small and most plies are forced. No territory shape, no goal-seeking, no medium-term planning.
- **Balance: 3** — P1 won 3/3 my games. Trained 0.667 P1-favoured. With pie OFF the ~3-ply tempo lead is decisive in a 56-ply accumulation race. Not balanced.
- **Novelty (post-adversary): 3** — see Phase 4. Re-skin of R19 menger outnumber-2 with menger scaffold doing modest structural work.
- **Replayability: 3** — Once hub-rush is known, openings collapse to a 2–3-line family (z=2 split, mixed-layer split, contested hubs). Mid- and end-game are mechanical. Low replayability — the optimal line is too clear.
- **Overall "Would an agent team play this again?": 3** — Once: yes, to feel the menger geometry. Repeatedly: no — the game is a long arithmetic race with shallow horizon. Slightly below R17 mean (3.5).

### CLOSEST KNOWN-GAME ANALOG
"Ataxx-on-a-Menger-sponge with Othello-style influence scoring." Inside Genesis: R19 menger top-1 `1f9191b5d4e6` (4.8/10) — same recipe, different parameters. Outside Genesis: no clean analogue.

### KILLER FLAWS
- **Pie rule OFF + ~3-ply tempo lead → P1 wins** in clean play. Single largest flaw; the `ac9e642` fix would have addressed this but the game predates the patch.
- **Mechanical mid-game.** Plies 9–56 reduce to "find best +2 move" with one obvious answer. ~80% of the game is bookkeeping.
- **Capture rarely fires** in clean play (0–1× per game). The presence of the rule shapes opening fortification but the rule itself is mostly inert tactically.
- **Family-level redundancy.** Effectively R19's `1f9191b5d4e6` rediscovered with modest parameter retuning.

### BEST QUALITY
The **menger 8-hub scaffold + outnumber-2 fortification dilemma**: opening play has 5–8 plies of genuine decision-making where you must trade off claiming a new hub vs fortifying an existing one before P2 can sandwich it. This is the only stretch of the game with > 1-ply horizon, and it is a real interaction between the substrate (hub isolation), the rule (outnumber-2), and the tempo race.

### MENGER STRUCTURAL CONTRIBUTION
**Real but circumscribed.** The fractal hole pattern isolates the 8 deg-6 hubs at axis distance ≥ 4, preventing propagation overlap between hubs and creating a discrete scaffold. Strategy of "claim 4 hubs, fortify, walk neighbours" is substrate-specific — flatten to 9×9 and the hub hierarchy disappears entirely; the game becomes a 2-D influence sprawl. Compared to R19 (menger > carpet > grid), this game does sit on the menger end of that quality gradient — the substrate matters more here than at the carpet scale. But the menger contribution caps out at the opening; mid-game and end-game would play similarly on any sparse high-degree graph (e.g., random 400-cell graph with 8 hubs).

### IMPROVEMENT IDEAS
**Single best change:** **Restore pie rule.** Trained-vs-trained 0.667 P1-favoured shows the structural imbalance; pie at action 730 (or 731 if pass+pie) lets P2 swap after P1's first hub claim and roughly balances the game. The `ac9e642` fix exists in code; this game just lost it in crossover.

Secondary improvements:
- **Lower threshold to ~40** — currently the game runs into max-turn timeout pressure (85.0 avg from training) and clean play barely makes 58. Lower threshold = sharper endgame, more decision-pressure.
- **Capture also clears value** (currently only ownership is cleared). Would make capture more impactful and worth pursuing tactically.
- **Outnumber-3** (one more friendly required) would close the capture window further and push play toward pure accumulation — but depth would drop. Outnumber-2 is correctly tuned for the hub-fortification dilemma.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-3_gamea6385db22c0b.md`.*
