# Run 20 Agent-Team Eval — team-1 — Game 625bfc1f3f49

**Team ID:** team-1
**Game ID:** 625bfc1f3f49 (carpet top-1, **only pie-rule game in slate**, 15-seed mean GE 0.060, σ 0.075, depth 0.645)
**Substrate:** sierpinski carpet (axis 9, 64 active cells / 81 grid positions, max_degree 4, **pie_rule=True**)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game 625bfc1f3f49` (see `briefing_carpet_625bfc1f3f49.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9 grid with 17 inactive holes per the level-2 Sierpinski carpet pattern (active=64). Cell index = y·9 + x. Holes form an "L_2 carpet" pattern: (1,1), (4,1), (7,1), (1,4), (4,4), (7,4) (row-3 and row-5 from x=3..5), and (1,7), (4,7), (7,7). Center (4,4)=40 is a hole. Most cells are degree-4 (max).

**Turn structure.** Alternating, 1 piece/turn. P1 first. Max_turns = 100.

**Action space.** **83 actions = 81 cells + 1 pass + 1 pie**. Action 82 = PIE (P2 invokes after P1's first move to swap seats). Pie is legal only on P2's first turn.

**Placement & capture.** Capture = **outnumber-2**. When a stone is placed at `c`, every adjacent enemy stone with ≥2 placer-coloured neighbours is cleared.

**Propagation.** influence (radius=2, strength=1.0, decay=0.5) — **wider than menger games (r=1)**. On placement at `c`, engine adds ±1.0 to `c`, ±0.5 to ≤4 axis-neighbours, ±0.25 to distance-2 cells (8 cells in 2D minus holes). 13-cell footprint per move, vs 7-cell for menger r=1.

**Win condition.** Threshold-race > **30.0**. `target_dimension_p2 = -1`. Equal margins → draw. Max-turn timeout: highest sum.

**Pie rule.** **TRUE**. Mechanic verified empirically:
- After P1 plays (2,2)=20, board_values[(2,2)]=+1, P1 effective +1.
- P2 invokes action 82. Engine flips all stone colours, negates all values, swaps piece counts, advances turn.
- After pie: (2,2) is owned by colour-2 with value −1. P2 effective = −(−1) = +1. P1 (= colour-1, the original-P2 player who took the seat) is now to move with 0 stones.
- The pie thus transfers the +1-stone advantage from colour-1 to colour-2 *and* gives the move-tempo back to colour-1. Net: ~+2 swing in P2's favour relative to no-pie.

**Degeneracy check.**
- The pie rule is **functional and balance-active**, not a vestigial bit. Game 2 below (P1 plays max-degree (2,2), P2 invokes pie) has P2 winning — pie *over-corrects* against strong P1 openings.
- Capture rule fires only on contrived probes; equilibrium play is cluster-vs-cluster with no contention (same as menger siblings).
- Larger r=2 propagation footprint creates faster score accumulation: ~1.5–2.0 effective per stone vs menger's ~1.5/stone.

---

## Phase 2 — Strategic Play

All moves engine-verified.

### Game 1 — P1 weak corner opening, P2 declines pie, both cluster

Sequence (21 plies, P1 wins):
`0,80,1,79,9,71,2,78,18,62,11,69,19,61,20,60,3,77,12,68,21`.

Plot:
- P1 plays `(0,0)=0` — degree-2 corner cell. Weak first move.
- P2 considers pie but declines (corner stone is too weak to "steal"). Plays `(8,8)=80` mirror cluster.
- Both fill (0..3, 0..3) and (5..8, 5..8) corner subcubes.
- At move 20: P1=+27, P2=+27. Tied.
- **Move 21 P1 plays `(3,2)=21`** — Δ+4.5 (compounds with `(2,2), (3,3)hole, (3,1)`, plus distance-2 deposits). **P1 score → +31.5 ≥ 30 → win.**

Final: P1=+31.5, P2=+27. P1 wins by +4.5.

### Game 2 — P1 max-degree opening, P2 invokes pie

Sequence (26 plies, **P2 WINS**):
`20,82,21,59,11,69,19,61,2,78,18,62,1,79,9,71,0,80,12,68,28,76,29,75,3,77`.

Plot:
- Move 1: P1 plays `(2,2)=20` (max-degree-4 cell). Effective +1.
- Move 2: P2 invokes action **82 = PIE**. Engine flips. (2,2) is now P2's stone, P2 effective +1, P1 to move.
- Moves 3–26: P1 (= original-P2, now to move from "behind") builds (0..3, 0..3) cluster, P2 (= original-P1, now holding (2,2) + builds (5..8, 5..8) cluster).
- Through move 20: both at +20.
- Move 21 P1 plays `(1,3)=28`, P2 mirrors `(7,5)=76`.
- **Move 26 P2 plays `(7,8)=77`** Δ+4 (compounds with mirror cluster + `(2,2)` distance-2 contribution). **P2 score → +31.5 ≥ 30 → P2 wins by +2.5.**

Reflection: **Pie over-corrects against strong P1 openings.** The +1 stone advantage from (2,2) plus the move-tempo P2 gains by pie-ing is greater than what P1 can recover from a "second-best" reply. Pie is *too strong* to invoke against (2,2). This is real strategic depth — P1 must deliberately under-play their first move to keep pie from being free.

### Game 3 — P1 medium opening, P2 declines pie

Sequence (21 plies, P1 wins):
`11,69,12,68,2,78,20,60,21,59,3,77,19,61,28,52,29,51,22,58,4`.

Plot:
- P1 plays `(1,2)=11` — degree-3 cell (active neighbours: `(0,2), (2,2), (1,3)`). Edge of cluster, not as strong as `(2,2)` but better than corner.
- P2 considers pie. Trade-off:
  - If pie: P2 inherits (1,2), P1 (= original-P2) plays (2,2) next. P1 has the strong centre cell. P2 would be ahead +1 (from (1,2)) but P1 would dominate the centre for the next ~15 moves.
  - If no pie: P2 plays own corner cluster. P1 has +1 tempo + (1,2) which is moderate.
- P2 declines pie (judgment call: (1,2) is "fair" enough that pie isn't worth the risk of P1 taking (2,2)).
- Both cluster; P1 leads by +1–2 throughout.
- **Move 21 P1 plays `(4,0)=4`** Δ+3 (compounds with `(3,0), (5,0), (4,1)hole`). **P1 score → +32 ≥ 30 → P1 wins by +3.**

Reflection: **(1,2) is a "fair" first move** — strong enough to give P1 a small edge but not so strong that pie is mandatory. This is the equilibrium: P1 picks a fair move, P2 declines pie, P1 wins by ~+3 (smaller than menger-style first-mover dominance).

### Strategy guides

**P1:** Play a degree-3 cell adjacent to a max-degree-4 cell — `(1,2)`, `(2,1)`, `(2,3)`, `(3,2)` etc. NOT `(2,2)` (P2 pies). NOT `(0,0)` (too weak). Then build cluster; keep tempo +1–2 throughout.

**P2:** Pie if P1 plays max-degree-4 cell. Decline pie if P1 plays edge or corner. Mirror cluster from opposite (5..8, 5..8) corner.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** **Yes, three:**
1. **P1 weak opening + corner cluster** — guaranteed +1–2 effective lead.
2. **P1 strong opening + lose-by-pie** — P1 sacrifices tempo for the (2,2) location, but P2 invokes pie and steals the win (Game 2).
3. **P1 fair opening + decline-pie** — P1 picks a degree-3 cell that's strong enough to be useful but weak enough that P2 declines pie. Game 3.

**Counter-play.** **Real for the first time in this slate.** P1 must choose first move with awareness of pie threshold. P2 must judge whether to pie. This decision is the only meta-strategic content of the slate.

**Short-term vs long-term.** **Tactical horizon = 3 plies, strategic horizon = ~5 plies (the pie decision sets up the entire game).** Better than menger games' 1-ply tactical horizon. The remaining ~20 plies after move 1–2 are mechanical cluster-fill, but the move-1 choice has 2-point game impact.

**Emergent concepts observed.**
- **Pie threshold** — the first-move choice is a discrete-valued game-theoretic problem. The threshold cell-strength at which P2's pie-EV crosses zero is the equilibrium first move. This is *real* strategic content.
- **Cluster compounding** — same as menger siblings.
- **Distance-2 propagation deposits** create a 13-cell influence footprint per stone, much larger than menger r=1's 7-cell footprint. This makes each placement worth more raw influence (~1.5–2.0/stone vs ~1.5 in menger).

**Does carpet matter?** The Sierpinski carpet's holes do shape the cluster structure — corner subcubes have ~14 active cells minus internal holes, giving ~12 cells per cluster. The center hole at (4,4) prevents the two clusters from meeting in the centre, but the carpet's smaller scale (64 active vs 400 in menger) makes contact more likely on a flat 9×9 grid. **Net effect:** carpet's holes are less destructive than menger's. The clusters here can almost touch (clearance of ~3 cells across the central hole strip).

**Does the propagation kernel matter?** **Yes — r=2 is a meaningful difference from menger's r=1.** The 13-cell footprint covers ~20% of the active board per stone (vs ~3% in menger). This means each placement has near-global influence-deposit, which makes opening-cell choice more sensitive (a centre stone affects 13 cells, a corner stone affects ~5).

**Capture-rule contribution.** Zero in self-play (same as menger siblings).

**First-mover advantage / seat balance.** **Pie rule corrects the balance.** PPO trained-vs-trained 0.500 over 27 runs is the most reliable balance datum in the slate. My games confirm: with optimal pie-invocation strategy, the game is roughly seat-balanced.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is closer to a published game than the menger siblings:

(a) **Threshold-race influence games with pie** are an established branch — most influence games (e.g., Hex, Y, Havannah, TwixT) have pie. This is the standard pie-rule equilibrium analysis on a fractal substrate.

(b) **Outnumber-2 capture** — Tafl/Ataxx family.

(c) **The combination "outnumber-2 + influence(r=2) + threshold-race + pie"** with pie producing real meta-strategic content **is novel within Genesis**. R8's Connection Go (the project's 8/10 ceiling) had pie via the seat-swap rule; this game has pie via action 82, which is the modern convention.

(d) **Sierpinski carpet substrate.** Fractal Hausdorff-dim play has been studied in physics but rarely as a competitive board game. The carpet's pattern of holes resembles a Go board with structured forbidden zones.

(e) **Expert-transfer test.** A Hex + Othello + Ataxx player familiar with pie would understand this game in **3–5 minutes**. The pie threshold analysis is exactly the standard Hex problem; the rest is "first to threshold via influence accumulation."

**Closest known-game analogue:** **"Threshold-race Ataxx with Hex pie on a Sierpinski carpet"** — Hex's pie-rule first-move equilibrium grafted onto a threshold-race influence game.

**Comparison to R8's Connection Go (8/10 ceiling).** R8 was custodian + connection on 2D grid with pie. This game is outnumber + influence + threshold-race on Sierpinski carpet 2D with pie. **Closer to R8's family than the menger games are**, because both have pie and both are 2D-with-holes substrates. R8's depth came from connection-win forcing global plan. This game's depth comes from pie-threshold analysis. R8 wins on the depth axis (connection > threshold), but pie+r=2 here adds something R8 didn't have.

**Comparison to R19 best.** R19 carpet top-1 `ce3a09e05cef` was 4.4/10 *without pie*. **This game has pie**. The R19 30/30 verdict was "add pie rule." This is the result. So is this game richer than R19's `ce3a09e05cef`? **Yes, but only via the pie meta-game**, which adds 1–2 strategic plies of depth.

**Player rebuttal (P1 + P2).**
- The pie meta-game (move 1 choice + P2 pie decision) is real strategic content not present in menger siblings or R19's pie-less carpet games.
- The carpet substrate is mid-tier: less destructive than menger but doesn't add new strategic content beyond fragmentation.
- r=2 propagation is a non-trivial change from r=1 and rewards different cell choices.
- Subtractor: post-pie-decision play is mechanical cluster-fill — the depth is concentrated in moves 1–2.
- Subtractor: capture rule still vestigial.

**Novelty score (post-adversary):** **5/10.** Above menger siblings (3/10) because:
- Pie produces real meta-strategy (Game 2 demonstrates pie inverts the win).
- r=2 propagation is a meaningful kernel change.
- The substrate-rule fit is better (carpet's scale makes clusters near-touch).

Below 7 because:
- Pie + threshold-race is documented (Hex + Octopus's Garden).
- Post-pie play is mechanical cluster-fill.
- Capture rule still vestigial.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game ID:** 625bfc1f3f49
**Rules Summary:** 9×9 Sierpinski carpet (64 active cells); alternating placement + **pie option for P2**; outnumber-2 captures; influence (r=2) deposits ±1 self / ±0.5 nbr / ±0.25 dist-2. First to total-owned-influence > 30.0 wins. Pie verified to invert outcomes when P1 plays max-degree first move.
**Substrate:** sierpinski carpet, axis 9, 64/81 cells, max_degree 4, **pie_rule=True**.
**Turn Structure:** alternating
**Hybrid actions:** no
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 5** — Pie creates a discrete game-theoretic move-1 problem with real consequences (Game 2: P2 wins via pie; Game 3: P2 declines pie and loses by +3). 3-ply strategic horizon for the pie decision. Post-pie play is mechanical (1-ply tactical), but the pie decision adds 2 effective points of depth over menger siblings.
- **Emergent Complexity: 5** — Pie threshold + cluster compounding + r=2 distance-2 deposits. Three real concepts vs menger's one.
- **Balance: 7** — **Highest in slate.** PPO 0.500 over 27 runs is the most reliable balance datum in R20. My games show pie successfully transfers the win between seats based on first-move choice — exactly what pie is supposed to do.
- **Novelty (post-adversary): 5** — see Phase 4. Pie + r=2 + carpet is a real combination, slightly above the R19 carpet without-pie family.
- **Replayability: 5** — Two viable first-move classes (fair vs strong-with-pie). Move-1 choice generates opening variety. Mid-game cluster-fill remains mechanical, but variety in first move = enough to play multiple times.
- **Overall "Would an agent team play this again?": 5** — **Best of slate.** Anchored against R19 carpet top (4.4) — this is slightly above because of the working pie rule. Anchored against R8 (8.0) — far below because R8 has connection-win on top of pie. This game is between R17 best (4.14) and R19 menger top (4.8); 5 is appropriate.

### CLOSEST KNOWN-GAME ANALOG
"Threshold-race Ataxx with Hex pie on a Sierpinski carpet." Inside this project corpus, **the closest cousin is R8's Connection Go (`9d33eee27c66`)**, which had pie + custodian + connection on a 2D grid. This game replaces connection with threshold-race and shifts to a fractal substrate. Compared to R19 carpet top-1 (without pie), this game has the pie rule R19's 30/30 verdict explicitly called for.

### KILLER FLAWS
- **Pie over-corrects on (2,2).** Game 2 shows P2 wins by +2.5 after invoking pie against a max-degree first move. This means P1 cannot play optimally — must deliberately play a sub-optimal first move. While this *is* the standard pie-rule equilibrium, the over-correction is sharp enough that the strategic-depth signal is "memorise the fair move," not "exploit position-by-position depth."
- **Post-pie play is mechanical cluster-fill.** The pie meta-game adds 2 strategic plies; the remaining ~20 plies are 1-ply tactical (greedy Δ).
- **Capture rule still vestigial.** Outnumber-2 doesn't fire in equilibrium play.
- **Lowest 15-seed mean GE (0.060) in slate** — the metric undervalues this game relative to menger siblings, which is a finalization-pipeline bug given that pie produces actual depth here.
- **Carpet's structural contribution is mid-tier.** The center-hole strip prevents centre cluster contact but doesn't add real strategic content beyond fragmentation.

### BEST QUALITY
**The pie rule producing a real first-move equilibrium problem.** Game 2 demonstrates that pie inverts the game outcome when P1 plays the strongest cell — this is a genuine meta-strategic decision that exists in published board games (Hex, Y, etc.) but is rare in this project's R-runs. The pie rule's effect on balance (PPO 0.500 over 27 runs) is the most reliable balance datum in R20.

### CARPET STRUCTURAL CONTRIBUTION
**Mid-tier — better than menger, worse than flat grid.** The Sierpinski carpet's holes shape clusters into ~12-cell corners, with the central hole strip preventing direct cluster contact. The 64 active cells make clusters near-touch (clearance of ~3 cells) — closer to interaction than menger's 400-cell sprawl. **Same rules on a flat 9×9 grid** would be similarly competitive but possibly more interactive (clusters could meet directly). Anchored against R19's "menger > carpet > grid" — for *this rule recipe with pie*, the order is approximately "carpet ≈ grid > menger" because the substrate-rule fit favours interaction.

### IMPROVEMENT IDEAS
**Single best change:** **enable pie rule on the menger games too.** This game shows pie is the slate's only working balance-correction mechanism. Three of the menger games have PPO P1 win-rates 0.667 — pie would close that gap. The crossover bug that stripped pie pre-`ac9e642` should be fixed and re-finalized.

Secondary improvements:
- Reduce r=2 to r=1 for tighter cluster control (currently each placement affects 20% of the board).
- Lower threshold to ~20 to make pie-decision sharper (shorter game = pie-correction more decisive).
- Add `target_dimension_p2 = +1` to break parallel-solitaire when both sides decline pie.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-1_game625bfc1f3f49.md`.*
