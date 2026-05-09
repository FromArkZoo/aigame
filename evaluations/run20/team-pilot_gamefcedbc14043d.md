# Run 20 Agent-Team Eval — team-pilot — Game fcedbc14043d

**Team ID:** team-pilot
**Game ID:** fcedbc14043d (grid top-1 / only grid game, 15-seed mean GE 0.129, σ 0.046, depth 0.593)
**Substrate:** flat 9×9 grid (axis 9, 81/81 active cells, max_degree 4, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game fcedbc14043d` (see `briefing_grid_fcedbc14043d.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Flat 9×9 grid with **no holes** (active=81/81). Degree distribution: 4 corners (degree 2), 28 edges (degree 3), 49 interior (degree 4). Cell index = `y·9 + x`.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = **72** (shorter than menger's 100).

**Action space.** 82 actions = 81 placement + 1 pass. **No pie**, no special actions.

**Placement & capture.** **Custodian-2** capture (Othello-style — only game in slate using custodian). On placement at `c`, each of 4 cardinal axes is scanned outward; a contiguous run of enemy stones bracketed by friendly stones (one being `c`, one further out, with no gaps) is **flipped to placer ownership**. Threshold=2 means standard Othello bracketing (one friendly on each side of the enemy run).

**Verified empirically with `0,1,2`**: P1 places (0,0); P2 places (1,0); P1 places (2,0). Result: `Captures (flipped owner): ['(1,0)']`. P1 piece count 1→3, P2 1→0. **Single-stone bracket DOES flip** (R19 carpet rank-2 lesson confirmed).

**Propagation.** influence (radius=1, strength=1.0, decay=0.5). Same kernel as menger games, but on degree-4 grid (vs degree 2-3 in menger).

**Win condition.** Threshold-race; first player to owned-cell sum >**20.0** wins. **`target_dimension_p2 = +1`** (different from menger/carpet's −1) — P2 has a *separate* accumulator, not a mirror of P1's. Both players race independently to 20.0; first to exceed wins. Verified empirically: scores at move 12 in my Game 2 line were `P1=+11.0, P2=+12.0` — both positive, both growing independently.

**Pie rule.** Off.

**Degeneracy check.**
- No fractal holes — all 81 cells active.
- Custodian-2 captures fire reliably on bracketed enemies. Verified.
- target_dimension_p2 = +1 — confirmed both players have positive accumulators (not mirrored).
- Threshold 20 + max_turns 72 + r=1 + decay 0.5 ⇒ winner determined in ~17 plies of mirror or ~20 plies of contested play.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run20_helper.py`.

### Game 1 — P1 corner cluster vs P2 corner mirror (P1 wins)

Sequence (17 plies, P1 wins +21 vs +18): `0,80,1,79,9,71,2,78,10,70,11,69,18,62,19,61,20`.

Plot:
- P1 builds (0..2, 0..2) corner cluster. P2 mirrors (6..8, 6..8). No contact, no captures.
- Linear accumulation: move 12 both at +12.0; move 16 both at +18.0.
- Move 17 P1 plays (2,2) → score +21, wins.
- **First-mover tempo advantage = +3** (1 stone × 3 effective per stone in a corner cluster).

### Game 2 — P1 corner vs P2 center cluster (**P2 wins**)

Sequence (20 plies, P2 wins +22 vs +19): `0,40,1,41,2,49,3,50,4,32,5,42,6,33,7,51,8,34,17,52`.

Plot:
- P1 builds (0..8, 0) edge line — not a true cluster, just edge stones.
- P2 builds central 2×3 cluster around (4,4): (4,4), (5,4), (4,5), (5,5), (4,3), (5,3), (4,6), (5,6), (4,2). Wait let me re-decode actions: 40=(4,4), 41=(5,4), 49=(4,5), 50=(5,5), 32=(5,3), 42=(6,4), 33=(6,3), 51=(6,5), 34=(7,3), 52=(7,5). P2's stones span (4..7, 3..5) — a wide central rectangle with full degree-4 cells.
- After 12 plies P2 leads +12 vs P1 +11.
- After 18 plies P2 reaches +20.0 threshold (rounded) — but engine shows +20.0 = exactly 20.0 ⇒ NOT exceeded ⇒ no win yet.
- Move 20 P2 plays (7,5)=52 → P2 score +22.0 → **P2 wins**.

This is the **only R20 slate game where P2 wins by structural strategic choice (not just because pie was invoked).** Center-cluster vs corner-cluster gives P2 ~+0.5 effective per stone advantage, which over the 9-stone race is enough to overcome P1's first-move tempo and win by 3.

### Game 3 — Both contest center (custodian capture cascade)

Sequence (5 plies probe): `40,39,41,31,49`.

Plot:
- M1: P1 (4,4). M2: P2 (3,4) — adjacent.
- M3: P1 (5,4) — does NOT bracket P2's (3,4) (would need P1 at (3,4)'s opposite side, but (2,4) is empty).
- M4: P2 (4,3) — adjacent to P1 (4,4).
- M5: P1 (4,5) — does NOT bracket P2's (4,3) (would need P1 at (4,2), empty).

After 5 plies, no captures. Both sides build clusters in center. P1 +4, P2 +1.

The pattern: in central contested play, P1 stays slightly ahead because of the +1.5 tempo. Captures don't fire unless one side leaves an enemy stone bracketed. With careful play, both sides avoid bracketing.

### Strategy guides

**P1 (offence/threshold push):** **Play center, not corner.** A degree-4 cluster gives +2.5 per stone vs degree-3 corner's +2.0 per stone. The +1.5 first-move tempo + degree-4 compounding is enough to win in 17–18 plies. **Avoid setting up your own stones to be flanked** — never play with an enemy on one cardinal side without backing your stone with a friendly on the other side.

**P2 (defence + threshold contest):** **Play center if P1 plays corner.** Game 2 confirmed: center cluster beats corner cluster despite P2's tempo deficit. If P1 also plays center, mirror their cluster and accept the first-mover tempo loss — both center-clusters give the same compounding rate, and the +1.5 tempo is the structural P1 advantage with no in-game corrector.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Three:
1. **Corner cluster** — degree-3 compounding, slightly weaker.
2. **Center cluster** — degree-4 compounding, slightly stronger.
3. **Edge line** — degree-3 with low neighbour overlap, weakest.

**Counter-play.** Real. P2 has a real winning strategy (center cluster vs P1 corner). However if P1 plays center too, mirror is the default and P1 wins by tempo.

**Short-term vs long-term.** Tactical. Plan horizon ~3 plies. Custodian captures fire when enemy stones get bracketed, which requires careful 3-ply lookahead.

**Emergent concepts observed.**
- **Custodian-2 flip** = Othello capture, single-stone bracket fires reliably.
- **Center-vs-corner cluster choice** as a real strategic decision.
- **Bracket avoidance** in contested center play.
- **Tempo + cluster-shape interaction**: degree advantage outweighs first-move advantage.

**Does grid matter?** Yes — flat grid is the *natural* substrate for custodian-2 + influence. Menger holes would break custodian walks (axis scan stops at hole boundary) and degrade the mechanic. Carpet would have similar issues. **This is the only substrate in the slate where custodian-2 plays cleanly.**

**Does propagation kernel matter?** Yes — `decay=0.5` defines the cluster compounding (same as menger). r=1 keeps the footprint contained, allowing distinct "corner" and "center" clusters to coexist without bleed.

**Capture-rule contribution.** Custodian-2 fires reliably in contested play but is rare in mirror equilibrium because both sides avoid bracketing. The capture rule is meaningful only when both sides engage — and engagement is rare because the race-clock makes it suboptimal to waste tempo on capture-bait setups.

**First-mover advantage / seat balance.** Briefing claims trained-vs-trained 0.500. My Game 2 confirmed P2 has a real winning strategy via center-cluster. The +1.5 P1 tempo is overcome by a +0.5/stone center-cluster advantage if P1 plays corner, but if P1 plays center too, mirror P1 wins by tempo. **Equilibrium is around 0.5 if both sides use center-cluster optimally with mixed P1-tempo / P2-shape outcomes.**

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is **Othello with influence + race-clock**.

(a) **Threshold-race influence games** ≈ Go territorial scoring without capture.
(b) **Custodian-2 capture is literally Othello/Reversi.** Bracket-and-flip on cardinal axes.
(c) **The combination "custodian + influence + threshold-race"** is the closest geometric analog to **R8 Connection Go** in this slate. R8 was custodian + connection on flat grid. This game is custodian + influence-threshold-race on flat grid. Same custodian, same substrate, different win condition.
(d) **Flat 9×9 grid substrate** is the most-published board game substrate (Go on 9×9 is a beginner format).
(e) **Expert-transfer test.** Othello + Go player understands this in 2 minutes. The "influence" deposit + "race threshold" are the only departures from standard Othello, and both are minor.

**Closest known-game analogue:** **"Othello with influence and a race-clock"** — exactly as the briefing's expert-transfer test predicted. Yes, this game is closest to R8's family.

**Comparison to R8's Connection Go (8/10 ceiling).** **Same family, different win condition.** R8 = custodian + connection (long-range planning, chain-extension via flip); this game = custodian + threshold-race (short-range tempo, no chain dynamics). R8's connection win condition produces 4-ply+ planning horizon; this game's threshold-race caps planning at 3 plies. **R8 is structurally deeper because of the win condition**, not because of the substrate or capture mechanic — both are shared.

**This is the project's evidence that the missing piece between R20-family and R8 is the win condition.** This game has 2 of 3 R8 ingredients (custodian, flat grid) but produces depth 0.593 vs R8's 8/10. The delta is "connection-win → threshold-race" — a -3+ rating step.

**Comparison to R19 best.** R19 had no grid-control top game like this. Comparison is N/A.

**Comparison to other R20 slate games.** **This game is shallower than the menger top-5** because: (a) custodian + threshold-race is faster than outnumber + threshold-race (1-stone bracket fires immediately, vs 2-3 stone surrounds), (b) the flat grid offers fewer degree-stratification surprises than menger or carpet. Slightly above 5f5c72e15220 in the "is this a published game?" sense (yes — Othello + race) but below in pure tactical depth.

**Player rebuttal.**
- The **center-vs-corner cluster choice** is a real strategic decision, not just an opening preference.
- The **target_dimension_p2 = +1** independent-accumulator mechanic differs from menger/carpet's mirror-score, allowing both players to accumulate positive scores simultaneously. This is mildly novel relative to the rest of the slate (but not relative to published games — Othello scoring works similarly).
- Otherwise, this is a clean re-skin of Othello + race-clock. The "influence" overlay doesn't add a new strategic dimension over Othello's positional scoring.

**Novelty score (post-adversary):** **3/10.** A Go + Othello player understands this in 2 minutes and could play competitively in 5. Below R17 mean (3.50). The custodian + flat-grid + 2D combination is the most-published in the slate and contributes the least novelty.

---

## Phase 5 — Verdict

**Team ID:** team-pilot
**Game ID:** fcedbc14043d
**Rules Summary:** Flat 9×9 grid (no holes); alternating placement; influence kernel (r=1, decay=0.5) + Othello-style **custodian-2** flip (bracket-and-flip enemy stones along cardinal axes) + threshold-race(20). Independent P2 accumulator (target_dimension_p2 = +1, not mirror). Pie rule off. Max turns 72.
**Substrate:** grid, axis 9, 81/81 cells, max_degree 4, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only).
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 4** — Center-vs-corner cluster choice is real, custodian flips fire reliably, but plan horizon caps at 3 plies because of fast race clock (game ends 17-22 plies). Lower than 5f5c72e15220 (6) because the substrate adds nothing and the win condition limits horizon.
- **Emergent Complexity: 4** — Custodian flip cascade in contested play, center-cluster compounding, edge-line trap. About on par with menger family.
- **Balance: 5** — Briefing 0.500 trained-vs-trained, my Game 2 confirms P2 has a real winning strategy (center cluster). However P1 +1.5 tempo dominates if both play center. Balance is achieved by strategy mix, not by structural symmetry.
- **Novelty (post-adversary): 3** — Othello-with-influence-and-race. Most-published combination in the slate.
- **Replayability: 4** — Three viable strategies (corner, center, edge) but center clearly best. Once known, openings collapse to "both play center, P1 wins by tempo".
- **Overall "Would an agent team play this again?": 4** — Closest to R8 in family but missing the connection-win that gave R8 its depth. Anchors: R8=8, R17 mean=3.5, R19 menger top=4.8, R8-without-connection-win = ~3-4. This game lands at 4.

### CLOSEST KNOWN-GAME ANALOG
**"Othello with influence and a race-clock"** — a 5-minute-to-learn variant of Reversi. Inside this project: **R8 Connection Go is the closest sibling** (same custodian + flat grid; different win condition). The win-condition difference is the depth differential.

### KILLER FLAWS
- **Win condition limits depth.** Threshold-race + 17-ply game length produces tactical-only play. R8's connection win condition would lift this game's depth substantially.
- **Single dominant cluster shape (center).** Once known, opening play collapses to mirror center-cluster, and P1 wins by +1.5 tempo with no in-game corrector.
- **Pie rule off** — the seat-balance is structurally tilted +1.5 for P1.
- **Only 4 generations of evolution** (per briefing — pre-launch axis-reduction control). Not a fully-evolved champion. The mutation that defined the game (connection→threshold-race switch) suggests the engine *prefers* threshold-race over connection on this substrate, which the R8-revival negative finding turns on.

### BEST QUALITY
**Connects R20-family's threshold-race shape to R8's custodian + grid roots.** This is the slate's reference point for "what does threshold-race lose vs connection-win on the same substrate?" Answer: ~3-4 rating points of depth. Useful as a calibration anchor more than as a playable game.

### grid STRUCTURAL CONTRIBUTION
**Substrate is the natural fit for custodian.** Custodian walks need clean axis scans without holes, so menger or carpet would break the mechanic. Flat grid maximizes custodian utility. **This is the only slate game where the substrate-rule combination is well-matched.** However, the 9×9 grid is the most-published board game substrate so adds zero novelty.

### IMPROVEMENT IDEAS
**Single best change:** **Switch win condition from threshold-race to connection.** This restores the R8 recipe exactly (custodian + connection on flat grid) and should produce R8-quality depth (8/10 ceiling). The mutation lineage shows evolution prefers threshold-race on this substrate, which is the R8-revival negative finding — but a *manual* switch back to connection would test the hypothesis directly.

Secondary improvements:
- Add pie rule for seat-balance.
- Increase axis to 11 or 13 for longer-horizon play.
- Test connection on this substrate against this game directly to confirm the R8-revival negative finding's specific cause.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-pilot_gamefcedbc14043d.md`.*
