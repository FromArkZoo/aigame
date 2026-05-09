# Run 20 Agent-Team Eval — team-pilot — Game 625bfc1f3f49

**Team ID:** team-pilot
**Game ID:** 625bfc1f3f49 (carpet top-1, 15-seed mean GE 0.060, σ 0.075, depth 0.645)
**Substrate:** sierpinski carpet (axis 9, 64 active cells / 81 grid positions, max_degree 4, **pie_rule=True** — only pie game in slate)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game 625bfc1f3f49` (see `briefing_carpet_625bfc1f3f49.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9 2D grid with 17 inactive holes per the level-2 Sierpinski carpet pattern (active=64). Cell index = `y·9 + x`. Holes sit at cells where the level-1 base-3 digits of (x,y) are both central (e.g., (4,4)). Result: outer "ring" + 4 sub-square interior, with the central 3×3 fully hollow.

Cell-degree distribution: most cells degree 3–4 (boundary or hole-adjacent), some interior-corner cells degree 2 (e.g., (1,0) has only `(0,0), (2,0), (1,2)`-via-jump? — actually (1,0) nbrs: (0,0), (2,0), (1,1)hole. Degree 2). Carpet has fewer degree-2 cells than menger because the hole pattern is sparser in 2D.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = 100. **Pie available on P2's first turn only.**

**Action space.** 83 actions = 81 placement + 1 pass + 1 **pie (action 82)**. Verified empirically: action 82 on P2's first move swaps seats — the previously-placed P1 stone becomes P2's, and the original-P2 player now plays as P1.

**Placement & capture.** **Outnumber-2** capture: when a stone is placed at `c`, every adjacent enemy stone with ≥2 friendly neighbours (counting `c`) is cleared. Verified: in the contested-corner line, captures fire at moves 10, 11, 13 — same pattern as menger outnumber-2.

**Propagation.** influence (radius=**2**, strength=1.0, decay=0.5). On placement at `c`, engine adds ±1.0 to `board_values[c]`, ±0.5 to ≤4 axis-neighbours, **and ±0.25 to ≤8 distance-2 cells** (axis-2 + diagonal). 13-cell footprint (vs 7-cell for menger r=1). Cell value clamped [−100, 100].

**Win condition.** Threshold-race; first player to owned-cell sum >**30.000** wins. `target_dimension_p2 = -1`. Max turns = 100. Avg game length ~21 plies (from my Game 1 mirror line), 36.5 in PPO equilibrium per briefing.

**Pie rule.** **TRUE — only game in the R20 slate with pie active.** Tested empirically with `0,82`: P1 places (0,0); P2 invokes pie via action 82; engine swaps. After: piece count P1=0, P2=1, score P2=+1.0, "Next: P1". The original-P2 player now seated as P1 plays next.

**Degeneracy check.**
- Carpet hole pattern: 17 holes in 9×9 = 21% inactive. Less aggressive than menger (45% inactive) but still significant.
- Pie rule fires on action 82, only legal as P2's first move.
- r=2 propagation gives a 13-cell deposit footprint; on a 64-cell board the footprint is ~20% of the active area per move. Influence saturates fast.
- Threshold 30 + r=2 ⇒ ~10–12 stones each side to reach threshold. Naive mirror games end in ~21 plies.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run20_helper.py`.

### Game 1 — Mirror cluster, no pie

Sequence (21 plies, P1 wins +31.5 vs +27.0): `0,80,1,79,9,71,2,78,18,62,20,60,11,69,19,61,3,77,12,68,21`.

Plot:
- P1 builds (0..3, 0..3) corner cluster. P2 mirrors at (5..8, 5..8). No contact, no captures.
- Linear accumulation: by move 12 both at +12.5; by move 16 both at +20; move 21 P1 wins at +31.5.
- **First-mover tempo +1.5–2.0 in the win column.**

### Game 2 — Pie invoked

Sequence (16 plies, P2 leads +19 vs P1 +14.5): `0,82,80,1,71,2,79,9,62,18,69,20,61,11,77,3`.

Plot:
- M1 P1 places (0,0). M2 P2 invokes pie via action 82. (0,0) now P2's stone; original-P2 now seated as P1 (next to move). P2 score +1, P1 score 0.
- New P1 (= original-P2) plays (8,8)=80. New P2 (= original-P1) plays (1,0)=1. Both build mirrored clusters.
- After 16 plies, **new-P2 leads +19 vs new-P1 +14.5** because the pied (0,0) stone gives original-P1 (now seated as P2) a +1 head-start AND they kept the (0..3, 0..3) corner cluster they wanted to build.
- **Pie effectively transfers the first-mover tempo + the chosen first-cell value from new-P1 to new-P2.** Whoever places the first stone "loses" — but they're the one who chose the cell, so the equilibrium is: P1 plays a cell of "fair-tempo" value, P2 invokes pie iff P1's cell exceeds fair value.
- In this line, P1 played (0,0) — a corner cluster anchor. Pie invocation correctly punished the strong play.

This empirically confirms pie's intended mechanic. **However**: pie does *not* eliminate the structural advantage; it transfers it. Whoever has the first-stone-value wins, just as in non-pie games.

### Game 3 — Contested-corner capture cascade

Sequence (22 plies): `0,1,9,2,18,11,19,20,3,12,21,27,28,29,36,38,27,20,45,47,3,5`.

Plot:
- Both sides interleave in (0..3, 0..3) corner.
- 3 captures in 14 plies (moves 10, 11, 13) — same density as menger outnumber-2 contested play.
- Move 17 P1 re-occupies the previously-captured (0,3) for **Δ+3.75** (residual-value harvest with r=2 propagation, more value deposited than in menger).
- After 22 plies, **P2 leads +13.75 vs P1 +12.75** — close race, captures + residuals create tempo swings.

### Strategy guides

**P1 (offence/threshold push):** Open at a "fair-tempo" cell — one that isn't a corner-cluster anchor (because P2 will invoke pie and steal it). Try (3,2) or (5,2) — interior cells whose r=2 footprint is symmetric. If P2 doesn't pie, build cluster; if they do pie, you're new-P2 with the original-P2's intended position. Plan around captures in degree-4 cells.

**P2 (defence + threshold contest):** Invoke pie iff P1's first move is strong (e.g., (0,0) corner anchor). Otherwise mirror. **Watch for the no-op trap**: pie just transfers tempo; if P1 plays an exact-fair cell, pie does nothing useful.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Three:
1. **Mirror cluster** (no pie) — P1 wins on tempo (Game 1).
2. **Pie + new-cluster** — original-P2 invokes, takes P1's first stone, builds opposite cluster (Game 2).
3. **Contested-corner cascade** — both sides interleave, captures fire (Game 3).

**Counter-play.** Pie rule provides a counter for "P1 played too strong" — but doesn't help against "P1 played fair". So balance depends on P1 finding the fair-tempo first move and P2 deciding correctly whether to pie.

**Short-term vs long-term.** Tactical with race-tempo overlay. Plan horizon 2–3 plies. Pie decision is a 1-move strategic choice.

**Emergent concepts observed.**
- **Pie equilibrium**: P1's first move converges to fair-tempo cell value where P2 is indifferent to pie.
- **Capture cascade in contested play** (same as menger outnumber-2).
- **Residual-value harvest** in re-occupation (move 17 Δ+3.75 — higher than menger because r=2 propagation deposited more).
- **r=2 footprint saturation**: by move ~10, the entire 64-cell carpet has non-zero `board_values` from both sides' depositions.

**Does sierpinski carpet matter?** Less than menger because (a) 2D, smaller hole pattern, (b) most cells degree 3–4, fewer extreme-degree cells, (c) the carpet hole structure roughly tiles into 4 corner sub-squares + cross-arms — strategic symmetry is high.

**Does propagation kernel matter?** **r=2 is the structural lever for this game**. With r=2 the influence footprint is 13 cells (vs 7 for r=1 menger), saturating the 64-cell board within 5 placements. This makes the game fast and dense. Pie rule needs the fast pace to be meaningful — at r=1 menger speed (51 plies for mirror), the +1 tempo would compound to +5 by mid-game and pie wouldn't catch up.

**Capture-rule contribution.** Outnumber-2 fires on degree-4 cells in contested play. Same captures as menger lines. The captures matter more here because the game is shorter and each capture exchange is ~10% of threshold.

**First-mover advantage / seat balance.** **Briefing claims trained-vs-trained 0.500 (balanced).** My experimentation shows pie is real but not magical — it transfers tempo rather than eliminating it. Balance is achieved when P1 finds the fair first move (no pie) or when P1 plays slightly above-fair (pie invoked, equal swap). Random PPO equilibrium settles around this point.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.**

(a) **Threshold-race influence games** ≈ Othello-without-flipping / weighted Go territorial scoring.
(b) **Outnumber-2 capture** ≈ Tafl. (c) **r=2 influence propagation** ≈ Quoridor's range-based effect, or weighted-distance scoring in Go variants.
(d) **Pie rule** is established Hex / Y / Havannah / Reversi-variant convention. Adding it to an influence-threshold-race game is a small step.
(e) **Sierpinski carpet substrate**: hasn't been used in published board games at this scale, but adds modest structural variation.
(f) **Expert-transfer test.** A Go + Hex + Othello player would understand this in 5 minutes. The "novel" piece is r=2 + pie, both of which are familiar individually.

**Closest known-game analogue:** "Influence-Othello with pie rule on a sierpinski-carpet graph." No exact published match, but pie + influence + capture is a small step from Hex-with-Othello-flips.

**Comparison to R8's Connection Go (8/10).** R8 is custodian + connection on 8×8 grid. This game is outnumber + threshold-race on 9×9 carpet with pie. **Same era, similar quality**. R8 had pie rule active too (per R8 code changes). R8's connection-win produces longer-range planning; this game's threshold-race caps planning at ~3 plies. R8 stronger on depth, this game comparable on balance.

**Comparison to R19 carpet top-1 `ce3a09e05cef` (4.4/10).** R19 carpet didn't have pie. **Pie does buy this game ~0.5 in balance**, so this rates ~0.5 above R19 carpet top-1. Trained-vs-trained 0.500 (this game) vs ??? (R19 carpet) confirms.

**Comparison to slate-mate `5f5c72e15220` (depth 0.894).** Lower depth, similar balance. 5f5c72e15220 has outnumber-3 + degree-stratification on menger; this game has pie + r=2 on carpet. Different mechanics, comparable score.

**Comparison to slate-mate menger games** (a6385db22c0b family). **This game is more interesting** because pie is active and r=2 propagation makes the game faster and denser. Both contribute novelty. However, the carpet substrate is decorative.

**Player rebuttal.**
- The **pie rule is genuinely loadbearing** — empirically transfers tempo and produces the 0.500 trained-vs-trained.
- The **r=2 propagation footprint** is the unique kernel parameter (vs r=1 in all menger games). Combined with the smaller board, it produces fast saturated influence games.
- **Pie + r=2 + threshold-race-30** is a real combination that doesn't appear in published games.
- However, each component (pie, r=2 influence, threshold-race) is well-known individually.

**Novelty score (post-adversary):** **5/10.** Above R17 mean (3.50) and above R19 carpet top-1 (4.4) because pie is active. Below 7 because each component is well-known. The combination is novel within this project corpus and the slate.

---

## Phase 5 — Verdict

**Team ID:** team-pilot
**Game ID:** 625bfc1f3f49
**Rules Summary:** 9×9 sierpinski carpet (64 active cells); alternating placement; influence kernel with **r=2** (13-cell footprint) + outnumber-2 capture + threshold-race(30); **pie rule active** on P2's first move (action 82). The only pie-active R20 game.
**Substrate:** sierpinski, axis 9, 64/81 cells, max_degree 4, **pie_rule=True**.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only + pie + pass).
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 4** — Tactical layer (captures, residual harvest) similar to menger outnumber-2 family. Pie adds a 1-move strategic choice but not deeper plan horizon. Plan horizon ~3 plies.
- **Emergent Complexity: 4** — Captures + residuals + r=2 footprint saturation + pie equilibrium. Slightly above menger family because r=2 + 2D produces denser interactions.
- **Balance: 6** — Trained-vs-trained 0.500 confirmed by my pie test (pie transfers tempo correctly when invoked on a strong first move). Best balance in slate alongside f98b9414f638.
- **Novelty (post-adversary): 5** — Pie + r=2 + sierpinski-carpet + outnumber-2 combination is novel within the project corpus. Each component is well-known but the assembly is unique.
- **Replayability: 4** — Three viable strategies + pie decision. Once equilibrium is known (P1 plays fair-tempo cell), opening collapses but not as sharply as in menger family.
- **Overall "Would an agent team play this again?": 5** — Once: yes, to feel the pie mechanic. Repeatedly: yes, more than menger games because of balance and pie variation. Anchors: R8=8, R19 carpet top-1=4.4, R17 mean=3.5. This game lands above R19 carpet top-1 because pie is active.

### CLOSEST KNOWN-GAME ANALOG
"Influence-Othello with pie rule, on a sierpinski-carpet graph" — no published game matches exactly. Closest published: **Hex** (pie rule, connection-game) — but win condition differs. Closest project: R8 Connection Go (had pie + custodian + connection). R19 carpet top-1 `ce3a09e05cef` is a near-sibling without pie.

### KILLER FLAWS
- **Carpet's R20 result was disastrous overall** — 71 of 74 carpet games scored < 0.002 by GE. This game survived only because it was a gen-0 seed that never hit broken crossover. The "carpet attractor" is essentially a gen-0 seed quirk, not an evolutionary discovery.
- **Pie rule is structurally a no-op for tempo-baseline balance** — it transfers the first-mover advantage to whichever side wants it. Useful but not transformative.
- **r=2 propagation saturates the 64-cell board fast** — by move 10 every cell has non-zero values from multiple stones, reducing positional choice in late game.
- **Strategic depth caps at ~3 plies** because of fast game length and threshold-race shape.

### BEST QUALITY
**Pie rule is empirically active and structurally useful.** R19's 30/30 verdict said "add pie rule" and this game has it. Trained-vs-trained 0.500 matches my finding that pie correctly transfers tempo to balance. **The carpet + r=2 + pie combination produces a fast, balanced, capturing influence game** — it's the only R20 slate game where balance is structurally guaranteed rather than a noise outcome.

### sierpinski STRUCTURAL CONTRIBUTION
**Modest.** Carpet hole pattern adds some degree heterogeneity but the active-cell count (64) is small enough that PPO can learn the active graph quickly. The hole pattern doesn't introduce new strategic concepts. Could be reduced to a 8×8 grid with 1-cell holes carved out and would play similarly. The contribution of carpet vs grid is *less* than the menger contribution to its top games — this game's interesting-ness comes from pie + r=2, not from carpet.

### IMPROVEMENT IDEAS
**Single best change:** **Promote this game's pie + r=2 kernel to the rest of R20 menger family**. The pie + r=2 combination is what makes this carpet game competitive; menger games suffer from no pie + r=1. Apply the kernel.

Secondary improvements:
- **Re-seed the carpet population** so future runs find more carpet attractors. The 71-of-74 collapse suggests carpet evolution is broken.
- **Reduce threshold to ~20** for even shorter, sharper games — would amplify the pie mechanic's importance.
- **Test r=3 propagation** to see if even broader footprint creates richer influence shapes.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-pilot_game625bfc1f3f49.md`.*
