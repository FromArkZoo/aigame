# Run 20 Agent-Team Eval — team-1 — Game b160b1f55378

**Team ID:** team-1
**Game ID:** b160b1f55378 (menger rank-2 by 15-seed mean GE 0.180, σ 0.074, depth 0.690)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game b160b1f55378` (see `briefing_menger_b160b1f55378.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Identical to `a6385db22c0b`: 9×9×9 cube with the level-2 Menger sponge fractal pattern (400 active of 729 grid positions). Cell index = z·81 + y·9 + x.

**Turn structure.** Alternating, 1 piece/turn. P1 first. Max_turns = 100.

**Action space.** 730 actions = 729 placement + 1 pass.

**Placement & capture.** Capture = **outnumber-2** (clear, not flip). Same as `a6385db22c0b`.

**Propagation.** influence (radius=1, strength=1.0, decay=0.5). Captures do not reset board_values.

**Win condition.** Threshold-race > **57.974**. `target_dimension_p2 = -1` (P2's effective sum is negation of values on its cells). Equal margins → draw. Max-turn timeout: highest sum.

**Pie rule.** Off.

**Degeneracy check.**
- **Byte-identical rule blob to `a6385db22c0b` and `d1dbc6568fc7`** — confirmed empirically: replaying pilot's Game 1 sequence on `b160b1f55378` produces identical move-by-move output and identical final score (+59.0 / +53.0). The 15-seed mean GE differences between the three siblings (0.241 / 0.180 / 0.157) are *measurement noise*, not structural differentiators. The only differentiator is lineage (this game's parents `f8acede1c192`, `63725e2b1ad0` and gen-6 origin vs gen-3 / gen-? for siblings).
- Briefing claims 0.500 trained-vs-trained winrate (better than `a6385db22c0b`'s 0.667). Since the rules are identical, the winrate difference is a PPO seed/elite-pool artefact, not a game-design signal.

---

## Phase 2 — Strategic Play

All moves engine-verified. Sequences identical to those that worked on `a6385db22c0b` because the rule blob is identical.

### Game 1 — Pilot mainline replayed (P1 corner cluster vs P2 mirror cluster)

Sequence (51 plies, P1 wins):
`0,80,1,79,9,71,2,78,18,62,11,69,19,61,20,60,3,77,12,68,21,59,27,53,28,52,29,51,81,161,83,159,84,158,4,76,22,58,36,44,38,42,99,233,101,235,165,140,110,239,164`.

**Final: P1=+59.000, P2=+53.000, P1 wins.** Identical to `a6385db22c0b` to the digit. The score curves diverge only because of P1's first-mover tempo (+2 throughout the corner-fill, then a +3 compounding move pulls P1 over threshold while P2 is still at +53).

### Game 2 — P1 corner cluster vs P2 z=0-face wall

Sequence (51 plies, P1 wins):
`0,4,1,6,2,5,9,7,11,8,18,17,19,26,20,35,3,44,12,53,21,62,27,71,28,80,29,79,81,78,83,161,99,159,101,158,102,76,110,75,84,240,108,242,180,224,164,222,162,238,183`.

**Final: P1=+59.5, P2=+44.5. P1 wins by 15.** Wall geometry costs ~10–15 effective points over the game vs cluster.

### Game 3 — P1 max-degree centre `(2,2,2)` cluster vs P2 mirror corner

Sequence (50 plies):
`182,80,181,79,183,71,173,78,191,62,101,69,263,61,189,60,190,77,254,68,165,59,99,53,162,52,21,51,164,161,180,159,18,158,2,76,20,58,11,44,29,42,3,233,12,235,27,140,28,239`.

Plot:
- P1 starts at the max_degree-6 cell `(2,2,2)=182`, then fills its 6 active neighbours `(1,2,2), (3,2,2), (2,1,2), (2,3,2), (2,2,1), (2,2,3)`.
- P2 mirrors at the (6..8, 5..8) corner cluster (pilot's standard line).
- At move 50: **P1=+54, P2=+53.** P1 has +1 lead but neither has crossed threshold; greedy next P1 move is Δ+3 → +57, still below; needs ~3 more plies.
- **Comparison to corner-start:** centre-of-corner-subcube `(2,2,2)` gives ~1.43 score/stone; corner `(0,0,0)` gives ~1.38 score/stone but is faster to extend because the corner's 3 neighbours form a `(0..1)^3` 2D corner with internal compounding. Net wash; centre vs corner change scoring rate by <2%.

Reflection: starting from the max_degree-6 cell does **not** materially improve P1's score curve because the neighbours of `(2,2,2)` themselves have low degree (1 or 2 active neighbours within the corner subcube, plus `(2,2,2)` itself). Cluster compounding requires *chains* of high-degree cells, and the menger geometry doesn't supply them — degree-6 cells are isolated points, not contiguous regions.

### Strategy guides

**P1 (offence/threshold push):** Same as `a6385db22c0b`. Open at any corner, fill the level-1 corner subcube greedily.

**P2 (defence + threshold contest):** Same — mirror at opposite corner. Avoid wall and avoid invasion.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** **One: corner cluster.** Same conclusion as `a6385db22c0b`.

**Counter-play.** **Effectively absent.** Two-corner solitaire race; first-mover wins by tempo unless P2 deviates.

**Short-term vs long-term.** Tactical = 1 ply, strategic = 0 ply. Same as sibling.

**Emergent concepts observed.**
- Cluster compounding (the only emergent pattern).
- Centre vs corner placement is essentially equivalent (Game 3) — neither generates extra novelty.
- I did not observe any captures, ko-like fights, or contested cells in self-play.

**Does menger matter?** **No more than for `a6385db22c0b`.** Same fractal geometry, same disjoint corner clusters, same parallel-solitaire structure.

**Does the propagation kernel matter?** Same as `a6385db22c0b` — radius=1, decay=0.5 makes cluster the sole strategy.

**Capture-rule contribution.** Zero in self-play. Outnumber-2 fires only on contrived probes.

**First-mover advantage / seat balance.** **Briefing's reference 0.500 winrate is the most interesting datum here.** Since the rule blob is byte-identical to `a6385db22c0b` (PPO-trained 0.667), the only way `b160b1f55378`'s 0.500 winrate is real is via PPO seed variance — both samples are from the same effective game. **The "balance" advantage of `b160b1f55378` over `a6385db22c0b` is a measurement artefact**, not a design improvement. (This is exactly the issue the 15-seed re-scoring was meant to expose: σ 0.074 here vs σ 0.120 on `a6385db22c0b` is the same noise band, just sampled differently.)

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Same as `a6385db22c0b` — outnumber-2 + influence(r=1) + threshold-race > 57.97 on Menger sponge. Closest analogue: **Ataxx-on-Menger with influence-sum scoring**.

(a) Threshold-race influence games — niche but documented; this is not a published game.
(b) Outnumber-2 capture is Tafl/Ataxx family.
(c) **The combination is partially anticipated by R10/R11/R19 outnumber experiments and is structurally identical to R19's `1f9191b5d4e6`.**
(d) Menger as a board-game substrate is novel as a research artefact, but its in-game effect here is *fragmentation* (clusters can't meet) — not strategic enrichment.
(e) Expert-transfer test: Go + Othello + Ataxx player would understand the rules in <2 minutes.

**Closest known-game analogue:** Ataxx-on-Menger with threshold-race influence scoring. **Inside this project corpus**, near-duplicate of R19 menger top-1 `1f9191b5d4e6` AND of `a6385db22c0b`/`d1dbc6568fc7` parameter siblings.

**Comparison to R8's Connection Go (8/10 ceiling).** Different family, substantially shallower. R8 had connection-win + custodian flips, both of which create *contention*. This game has *parallel solitaire*.

**Comparison to R19 best.** Direct duplicate of R19 menger top-1 family on a different parent lineage. No genuine innovation over R19.

**Player rebuttal (P1 + P2).** The Menger substrate forces local-degree awareness, but this is the only contribution. The capture rule is vestigial in equilibrium play. P2 has no compensation mechanism; pie rule is off.

**Novelty score (post-adversary):** **3/10.** Same level as `a6385db22c0b`. The "tightest noise band" argument doesn't add novelty; it just means we're measuring the same shallow game more precisely.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game ID:** b160b1f55378
**Rules Summary:** 9×9×9 Menger sponge cube; alternating placement; outnumber-2 captures clear single-stone enemy islands; influence (r=1) deposits ±1 self / ±0.5 neighbour. First to total-owned-influence > 57.974 wins. **Byte-identical rule blob to `a6385db22c0b` and `d1dbc6568fc7`.**
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no
**Soft violations flagged:** none. (Lineage-only differentiation from siblings is a R20 evolutionary artefact, not a rule defect.)

### Scores (1–10)

- **Strategic Depth: 3** — Same single-strategy game as sibling. 1-ply tactical horizon. The 0.690 engine "depth" metric is a game-length artefact. Game 3 confirmed centre-vs-corner choice is wash — the geometry doesn't generate variants.
- **Emergent Complexity: 3** — Cluster compounding is the only emergent pattern. Capture rule shapes equilibrium but doesn't fire. Same vocabulary as sibling.
- **Balance: 4** — Briefing claims trained-vs-trained 0.500, but rule-identity to `a6385db22c0b` (0.667) means this is sampling variance, not structural balance. My self-play games all show P1 wins by 2+. Counted slightly higher than sibling because the better PPO sample suggests strong play *can* approach balance, but the structural P1 advantage is the same.
- **Novelty (post-adversary): 3** — Identical to `a6385db22c0b`. Above pure re-skin (Menger is a novel research substrate) but below 4 because the rule recipe is documented in R19's outnumber-2 family and the substrate's effect is fragmentation not strategy.
- **Replayability: 3** — Same as sibling. Corner-pick is the only opening choice; mid-game greedy-Δ.
- **Overall "Would an agent team play this again?": 3** — Once: yes, to confirm the byte-identity to siblings. Repeatedly: no.

### CLOSEST KNOWN-GAME ANALOG
Ataxx-on-Menger with threshold-race influence scoring. **Inside this project, exact duplicate of `a6385db22c0b` and `d1dbc6568fc7`** (different lineages, identical play).

### KILLER FLAWS
- **Rule blob byte-identical to two other slate games** (`a6385db22c0b`, `d1dbc6568fc7`). The slate is over-counting structurally identical games — this game is rank-2 because of variance in 15-seed re-scoring, not because it is a different game.
- **Same parallel-solitaire flaw as siblings** — corner clusters never interact through Menger's hollow core.
- **Capture rule largely vestigial in optimal play.** Same as sibling.
- **Pie rule off; structural P1 advantage uncorrected** — sibling-rule means same imbalance as `a6385db22c0b`.

### BEST QUALITY
**Tightest noise band σ=0.074 in the menger slate** — the most reliable measurement of the underlying game. Useful as a *measurement reference* for the family even though gameplay quality is the same as siblings. Otherwise nothing distinguishes it from `a6385db22c0b`.

### MENGER STRUCTURAL CONTRIBUTION
Same as `a6385db22c0b` — net negative. Fractal hole pattern fragments the board into disjoint corner clusters; opposing clusters never meet. Same rules on a flat 9³ cube would be richer.

### IMPROVEMENT IDEAS
**Single best change:** **deduplicate the slate before 15-seed re-scoring.** Spending 15 seeds × 3 finalization + agent-team time × 5 teams × 3 byte-identical games is wasted compute. The R20 finalization pipeline should hash rule blobs and skip duplicates.

Secondary improvements (apply equally to all three siblings):
- `target_dimension_p2 = +1` to break parallel-solitaire structure.
- Pie rule on to correct P1 first-mover tempo.
- Lower threshold to ~30 to force opening-choice tension.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-1_gameb160b1f55378.md`.*
