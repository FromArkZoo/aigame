# Run 20 Agent-Team Eval — team-1 — Game a6385db22c0b

**Team ID:** team-1
**Game ID:** a6385db22c0b (menger top-1 by 15-seed mean GE 0.241, σ 0.120, depth 0.763)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game a6385db22c0b` (see `briefing_menger_a6385db22c0b.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 cube, 329 inactive holes per the level-2 Menger sponge fractal pattern (active=400 of 729). Cell index = z·81 + y·9 + x. A cell is inactive iff at least two of its (x,y,z) base-3 digits at the level-1 scale equal 1 — the central slabs (`y∈{3,4,5} ∧ z∈{3,4,5}` etc.) and 6 face-centre crosses are hollow. Net effect: 20 active cells per surviving level-1 3³ subcube (8 corners + 12 edges of the cube), and the bulk is hollow. Many cells have **degree 2 or 3** rather than the grid maximum 6, e.g. `(1,0,0)` has only `(0,0,0)` and `(2,0,0)` as active neighbours.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = 100.

**Action space.** 730 actions = 729 placement + 1 pass. Placement legal at any empty active cell (401 legal initially). **No move actions** (D1 hybrid ban active).

**Placement & capture.** Capture = **outnumber-2**. When a stone is placed at `c`, every adjacent enemy stone `d` is checked; if `d` has ≥2 placer-coloured stones among its active neighbours (counting `c`), `d` is **cleared** to empty (not flipped). Verified empirically with `0,1,2`: P2's `(1,0,0)` is degree-2; once `(0,0,0)` and `(2,0,0)` are both P1, the P2 stone is cleared — P2 piece count drops 1→0.

**Propagation.** influence (radius=1, strength=1.0, decay=0.5). On placement at `c`, engine adds ±1.0 to `board_values[c]` and ±0.5 to each of c's ≤6 active axis-neighbours. Sign +1 if P1, −1 if P2. Clamped [−100, 100]. **Captures do not reset board_values** — earlier deposits persist on the cleared cell, so a capture costs the placer ~0.5 net effective influence (the residual −0.5 deposit at the bracket cells stays).

**Win condition.** Threshold-race. Owned-sum exceeds **57.974**. `target_dimension_p2 = -1` ⇒ P2's effective sum is the negation of the values it owns, so P2 wants its cells to be very negative. Equal margins → draw. Max-turn timeout: highest effective sum wins.

**Pie rule.** Off (lost in crossover before the `ac9e642` fix).

**Degeneracy check.**
- No inert fields. Influence on, capture on, both fire empirically.
- The fractal hole pattern reduces local degree heavily — degree-2 cells are **easy capture traps for the placer**, but no rule path is dead.
- Threshold 57.97 with strength=1.0, decay=0.5 ⇒ a fully-clustered stone yields `1 + 0.5·deg_friendly` to its own owned-sum; corner clusters deliver ~2.0/stone, so crossover-win is ~28–30 stones each side. My 3 games all decided in 47–51 plies; engine's PPO 85-ply average reflects suboptimal play that wanders away from cluster.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run20_helper.py`. Action IDs = cell indices for placement; pass = 729.

### Game 1 — P1 corner cluster vs P2 mirror cluster (mainline self-play)

Sequence (51 plies, P1 wins):
`0,80,1,79,9,71,2,78,18,62,11,69,19,61,20,60,3,77,12,68,21,59,27,53,28,52,29,51,81,161,83,159,84,158,4,76,22,58,36,44,38,42,99,233,101,235,165,140,110,239,164`.

Plot:
- P1 builds the dense corner cluster at `(0..3, 0..3, 0..2)`; P2 mirrors at `(5..8, 5..8, 0..2)`. The two clusters are physically disjoint — Menger's hollow core blocks the z-axis interior, so the clusters never touch.
- Linear accumulation: at move 16 both at +16; at move 32 P1=+36, P2=+36; at move 48 P1=+53, P2=+51. P1 leads by 2 throughout — pure first-mover tempo.
- Move 49 P1 plays `(2,3,1)=110` — picks up two friendly +0.5 deposits (neighbours `(2,3,0)` and `(2,2,1)`). Δ score +3.0 → P1=+56.
- Move 50 P2 mirrors `(5,8,2)=239` Δ+3 → P2=+53.
- Move 51 P1 plays `(2,0,2)=164` Δ+3 (adj to `(2,0,1)=83`). **P1 score → +59 ≥ 57.97 → win.**

Reflection (P1): cluster compounding is the only knob. Menger's holes thin out the 3³ corner subcube to 20 active cells, so a corner cluster has fewer adjacencies than a flat 3³ cube — but enough to dominate.

Reflection (P2): mirroring is fine if you have first-equivalent tempo; here P1 starts with one stone of free advantage and never gives it back.

### Game 2 — P1 cluster vs P2 wall along z=0 face perimeter

Sequence (51 plies, P1 wins):
`0,4,1,6,2,5,9,7,11,8,18,17,19,26,20,35,3,44,12,53,21,62,27,71,28,80,29,79,81,78,83,161,99,159,101,158,102,76,110,75,84,240,108,242,180,224,164,222,162,238,183`.

Plot:
- P1 starts `(0,0,0)`. P2 plays `(4,0,0)`: degree-2 cell *between* P1's expansion zones, baiting capture.
- P1 ignores the bait and keeps building the corner. At move 5 P1 places `(2,0,0)`; outnumber-2 doesn't fire because `(4,0,0)`'s only 2 neighbours are `(3,0,0)` (still empty) and `(5,0,0)` (P2). Wall-link self-protects.
- P2 builds an L-wall along z=0 face perimeter: `(4..8, 0)` then `(8, 0..8)`. Wall-density ~1.5 per stone vs cluster 2.0/stone.
- By move 36 the gap is +5 (P1=+39.5, P2=+34.5). P1 spreads into z=1/z=2; the gap compounds.
- Final at move 51: **P1=+59.5 vs P2=+44.5 — P1 wins by 15.**

Reflection: the wall outscores nothing because (i) every wall stone hits a y=1 / z=1 hole row, capping its degree at 2; (ii) the asymmetric wall geometry stays at the periphery, missing the +0.5 compounding that interior corner cells get from triple-edge adjacencies.

### Game 3 — Symmetric corner-vs-corner on the same z-side, no mirror

Sequence (50 plies played, P1 winning by next move):
`0,8,1,7,9,17,2,6,18,26,20,24,3,5,11,15,27,35,29,33,81,89,83,87,99,107,101,105,162,170,164,168,180,188,182,186,12,14,19,25,28,34,84,86,108,116,110,195,21,114`.

Plot:
- P1 builds at `(0..3, 0..3, 0..2)`; P2 builds at `(5..8, 0..3, 0..2)` — same z-side, different x-corners. Both subcubes have ~14 active cells per layer.
- At move 36 both at +35. Move 48 both at +57.0. Pure parity until P1's next move (`(3,2,0)=21` Δ+3 → +60) wins.
- This is a **complete tempo race** — neither side ever gets to capture or interact. The game reduces to "fill your subcube faster" and "first mover wins by one tempo unit."

Reflection: the symmetric race shows the game's headline characteristic: the two clusters never touch. Menger's hollow core is wide enough that a corner cluster on x∈{0..3} and one on x∈{5..8} never contact — outnumber-2 never fires, board_values never overlap, and the only differentiator is who places first.

### Strategy guides

**P1 (offence/threshold push):** Open at `(0,0,0)` or any corner. Fill the (0..3, 0..3, 0..2) subcube greedily, prioritising cells with ≥2 already-owned neighbours (Δ+3 moves over Δ+2 moves over Δ+1 moves). Ignore P2 entirely; clusters never collide.

**P2 (defence + threshold contest):** Mirror at the opposite corner. Don't play wall (loses ~10–15 effective points over the game). Don't play sacrificial captures (each costs you ~0.5 net). Don't try to invade P1's cluster — the geometry blocks contact. The honest play is to take the second-best corner and accept losing by ~2 to first-mover tempo.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** **One viable strategy: corner cluster.** Wall and isolated-stone play both lose. Corner-cluster has minor variants (which corner; z=0 vs z=2 first; row-first vs column-first within the layer) but they all yield ~the same score curve.

**Counter-play.** **Effectively absent.** Cluster-vs-cluster on opposite corners never interact — the game is two parallel solitaires racing to threshold. P1 wins by tempo unless P2 deviates (and any deviation underperforms mirror).

**Short-term vs long-term.** Tactical horizon = 1 ply (pick the highest-Δ legal placement). Strategic horizon = 0 ply (the corner choice is made on move 1; nothing afterwards changes the plan). The 0.763 engine "strategic depth" metric is **almost entirely an artefact of game length** — long games + non-trivial winrate by-seat ≠ strategic depth.

**Emergent concepts observed.**
- **Cluster compounding** — the only emergent pattern. Each Δ+3 placement reflects two prior friendly neighbours.
- **Capture-bait inefficiency** — single-stone P2 invasions in degree-2 cells cost P2 -1 stone for ~ -1 P1 effective points. Below the cluster-build rate of +1.5–2.0 per stone, so always negative-EV.
- I did **not** observe ko-like fights, mutual annihilation, sub-volume territorial control, or cluster-vs-cluster contention. The Menger geometry **prevents** these by design — the two corner subcubes are physically disconnected through the hollow core.

**Does menger matter?** **Yes, but in a destructive way.** The fractal hole pattern fragments the board into ~20 disjoint level-1 subcubes (with thin tunnel connections), so a corner cluster builds inside one subcube and can't be contested. **Same game on a flat 9³ cube with custodian + influence + threshold-race would be richer** — the clusters would actually meet in the middle and the capture rule would fire. Menger ≈ "bigger 9³ playing field with most of the contact surface deleted."

**Does the propagation kernel matter?** Yes — radius=1, decay=0.5 is what makes cluster compounding the sole strategy. With radius=2 or stronger decay, isolated influence wells could compete with clusters; with radius=1 + decay=0.5, the only compound win is to cluster.

**Capture-rule contribution.** **Zero in self-play.** Outnumber-2 never fired in Games 1, 2, or 3. The only capture observed was the contrived 3-move probe `0,1,2`. PPO learns to avoid putting stones in degree-2 capture-traps and to avoid invading enemy clusters; the rule shapes the equilibrium but doesn't appear in the move sequence.

**First-mover advantage / seat balance.** P1 wins 3/3 in my games. Trained-vs-trained 0.667 P1 winrate confirms structural P1 advantage. **Pie rule is OFF**, so P2 has no compensation mechanism. Balance is meaningfully off-centre — not catastrophic (a strong P2 can lose by only 2 effective points), but a competitive game would need pie or `target_dimension_p2 = +1` rebalance.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a re-skin of well-known mechanics:

(a) **Threshold-race influence games** are a niche but established branch — closest analogues are *Octopus's Garden* (territorial sum-race), Othello scoring without flipping, or arcade-stratagem influence games (e.g., Risk-style territory-value summation). The "first to N" branch is mechanically simpler than majority-at-end-of-game.

(b) **Outnumber-2 capture** is **Tafl-family / Ataxx-family** — an enemy stone with too many adjacent friendlies dies. Specifically the "place-clear" variant (not flip) is closest to Ataxx's unilateral conversion or the historical *Phutball* contact-clear.

(c) **The combination "outnumber-2 + influence(r=1) + threshold-race"** is **not a published board game.** It is partially anticipated by R10/R11 outnumber experiments in this same project and most directly by R19's `1f9191b5d4e6` (outnumber-2 + influence + threshold) — this game is a near-duplicate of that R19 game on a different substrate.

(d) **Menger sponge substrate.** Fractal Hausdorff-dim play on this exact substrate has not (to my knowledge) been studied as a competitive board game. **What does it add?** Mostly *fragmentation* — it makes clusters disjoint by geometric necessity. **What does it subtract?** Almost everything that would generate strategic interaction, because the holes prevent the contact.

(e) **Expert-transfer test.** A Go + Othello + Ataxx player would understand this game in **<2 minutes**: "place stones, +0.5 to neighbours, captures clear single-stone islands, first to 58 owned-influence wins." The novel piece is the substrate, not the rules.

**Closest known-game analogue:** **Ataxx-on-Menger-with-influence-scoring** — Ataxx's outnumber-clear capture, cluster-build incentive, on a fractal 3D substrate, with threshold-race scoring instead of stone-count.

**Comparison to R8's Connection Go (8/10 ceiling).** R8 was custodian + connection on 2D. This game is outnumber + influence + threshold-race on Menger 3D. **Different family.** R8's depth came from the *connection* win condition forcing global plan, plus *custodian flips* enabling chain-completion in one move. This game has neither — it's two parallel solitaires. Substantially shallower than R8.

**Comparison to R19 best.** R19 menger top-3 `5048f71b62fd` was surround capture (5.0/10), R19 menger top-1 `1f9191b5d4e6` was outnumber-2 (4.8/10). **This R20 game is structurally identical to R19's `1f9191b5d4e6`** (same outnumber-2 + influence + threshold-race recipe). The 15-seed re-scoring mean GE 0.241 vs R19's similar GE region puts them in the same ballpark.

**Player rebuttal (P1 + P2).**
- The Menger substrate adds a **legitimate** novelty — fractal degree distribution per cell forces thinking about local degree before placing. But this only applies to the *boundary* between cluster and tunnel; deep inside a corner cluster, degree is fixed and the game reduces to greedy-Δ.
- The outnumber-2 capture rule fires in adversarial probes but not in equilibrium play. The rule **shapes** play (avoid degree-2 invasions) but doesn't appear in optimal sequences.
- Subtractors: the corner-cluster strategy is one-dimensional; pie rule off; clusters disconnected by geometry; capture rule largely vestigial in optimal play.

**Novelty score (post-adversary):** **3/10.** Above pure re-skin (1–2) because the Menger substrate is not previously studied as a board-game arena. Below 4 because (i) the rule recipe is identical to R19's `1f9191b5d4e6`, (ii) the substrate's primary effect is *fragmentation* not *new strategy*, (iii) outnumber + influence + threshold-race is a documented R10/R11/R19 family.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game ID:** a6385db22c0b
**Rules Summary:** 9×9×9 Menger sponge cube; alternating placement; each stone deposits +1 to its cell and +0.5 to neighbours (sign per player). Outnumber-2 captures clear single-stone enemy islands. First to total-owned-influence > 57.974 wins.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only, D1 active)
**Soft violations flagged:** none (pie rule loss noted by briefing — design-time issue, not in-game).

### Scores (1–10)

- **Strategic Depth: 3** — Single viable strategy (corner cluster). 1-ply tactical horizon. The 0.763 engine "depth" metric is mostly game-length artefact; subjectively the game is shallow. Each placement is a greedy Δ-pick; the planning horizon never exceeds "which adjacent cell has the most friendly neighbours."
- **Emergent Complexity: 3** — Cluster compounding is the only emergent pattern. Capture-rule shapes equilibrium but doesn't fire in optimal play. No territory, no influence wells, no ko, no chain-completion. The rule-set is small and the emergent vocabulary correspondingly small.
- **Balance: 4** — P1 wins 3/3 in my games; PPO trained-vs-trained 0.667 confirms structural P1 advantage; pie rule off so no compensation. By exact effective-score margin: P1 wins by 2 in mirror-play, by 15 in P2-suboptimal. Not catastrophic but uncorrected.
- **Novelty (post-adversary): 3** — see Phase 4. Above re-skin (Menger as substrate is novel) but the rule recipe is a near-duplicate of R19's outnumber-2 family game, and the substrate's primary effect is fragmentation not new strategy.
- **Replayability: 3** — Once the corner-cluster pattern is known, openings collapse to "pick a corner." The corner choice is symmetric, so 4-fold rotation in 3D gives 8 starting corners — no real opening variety. Mid-game pure greedy-Δ.
- **Overall "Would an agent team play this again?": 3** — Once: yes, to feel the Menger geometry. Repeatedly: no — the pure tempo race with no contention is a parallel-solitaire structure, not a competitive game.

### CLOSEST KNOWN-GAME ANALOG
Ataxx-on-Menger with threshold-race influence scoring instead of stone-count. Inside this project, near-duplicate of R19 menger top-1 `1f9191b5d4e6` (same outnumber-2 + influence + threshold recipe).

### KILLER FLAWS
- **Clusters never interact.** Menger's hollow core puts opposing corner clusters in physically disconnected subcubes. The capture rule never fires in self-play; the game reduces to two parallel scoring tracks.
- **Capture rule largely vestigial in optimal play.** Outnumber-2 fires only when one side deliberately invades degree-2 cells. PPO learns to avoid this. Net: ~85% of the rule blob's complexity contributes nothing to equilibrium play.
- **Pie rule lost in crossover.** Trained-vs-trained 0.667 P1 advantage with no compensation mechanism — game has measurable seat imbalance baked in.
- **Strategic depth metric is a game-length artefact.** 0.763 reads as "deep" but the game is just *long* (slow accumulation), not deep. Engine's GE depth term needs a recalibration to distinguish length from depth.

### BEST QUALITY
The **Menger substrate as a fractal-degree placement constraint** is the game's only genuinely novel element. Forcing a player to think about local degree before placing (since outnumber-2 only fires on low-degree cells) is a legitimate small twist on Ataxx — even if optimal play factors it out.

### MENGER STRUCTURAL CONTRIBUTION
**Net negative.** The fractal hole pattern fragments the board into ~20 disjoint level-1 subcubes; opposite-corner clusters never meet. **Same rules on a flat 9³ cube would be richer** — the clusters would actually contact in the middle, the capture rule would fire, and contention would emerge. Menger acts as a *strategy-killing geometry* here, not a strategy-enabling one. Anchored against R19's finding that "menger > carpet > grid" — for *this rule recipe*, the ordering reverses, because the rule needs cluster contact and Menger prevents it.

### IMPROVEMENT IDEAS
**Single best change:** **add `target_dimension_p2 = +1`** so both players use additive influence sums on their own cells (not mirror-negation). This breaks the parallel-solitaire structure: now P2's placements compete for the *same* cell-value sign, and contesting interior cells matters. Combined with a pie rule, this would force cluster contact and re-engage the capture mechanic.

Secondary improvements:
- Lower threshold to ~30 so games end before either player completes a full corner-cluster — forces opening-choice tension.
- Re-enable pie rule (lost in crossover); without it the 0.667 P1 advantage is uncorrected.
- Increase propagation radius to 2 so cluster boundaries actually overlap across the Menger holes — the fractal would then *connect* rather than *fragment*.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-1_gamea6385db22c0b.md`.*
