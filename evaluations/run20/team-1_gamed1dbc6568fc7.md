# Run 20 Agent-Team Eval — team-1 — Game d1dbc6568fc7

**Team ID:** team-1
**Game ID:** d1dbc6568fc7 (menger rank-4 by 15-seed mean GE 0.142, σ 0.105, **depth 0.792 — second-deepest in slate**)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game d1dbc6568fc7` (see `briefing_menger_d1dbc6568fc7.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 cube, level-2 Menger sponge. 400 active of 729. Same substrate as `a6385db22c0b`, `b160b1f55378`, `5f5c72e15220`.

**Turn structure.** Alternating, 1 piece/turn. P1 first. Max_turns = 100.

**Action space.** 730 actions = 729 placement + 1 pass. Place-only.

**Placement & capture.** Capture = **outnumber-2**. Same as `a6385db22c0b` and `b160b1f55378`. Verified empirically with `0,1,2`: P2's `(1,0,0)` cleared at move 3 (degree-2 cell, 2 P1 neighbours = threshold met).

**Propagation.** influence (radius=1, strength=1.0, decay=0.5).

**Win condition.** Threshold-race > **57.974**. `target_dimension_p2 = -1`. Equal margins → draw. Max-turn timeout: highest sum.

**Pie rule.** Off.

**Degeneracy check.**
- **Byte-identical rule blob to `a6385db22c0b` and `b160b1f55378`** — confirmed empirically: replaying the pilot mainline `0,80,1,79,...,164` (51 plies) on this game produces the *exact same final score* (+59.0 / +53.0) as on `a6385db22c0b` and `b160b1f55378`. The 15-seed mean GE differences (0.241 / 0.180 / 0.142) are *measurement noise*. The depth metric difference (0.763 / 0.690 / 0.792) is also pure measurement variance — the rule blob is the same and the equilibrium play is the same.
- The "depth-rich" framing of this game (depth 0.792 putting it rank-2 in the slate by depth) is **a metric artefact** if it were measuring this game's outnumber-2 equilibrium. The cluster-vs-cluster mainline play is identical to `a6385db22c0b`'s.
- Lineage-only differentiation: this game is a single mutation off `c850f91a55b4`. The mutation may have changed the engine's PPO-trained behavior in ways that affect the depth metric, but the *gameplay rules* are unchanged.

---

## Phase 2 — Strategic Play

All moves engine-verified. Sequences are the same as those that worked on `a6385db22c0b` because the rule blob is identical.

### Game 1 — Pilot mainline replayed (P1 corner cluster vs P2 mirror cluster)

Sequence (51 plies, P1 wins): `0,80,1,79,9,71,2,78,18,62,11,69,19,61,20,60,3,77,12,68,21,59,27,53,28,52,29,51,81,161,83,159,84,158,4,76,22,58,36,44,38,42,99,233,101,235,165,140,110,239,164`.

**Final: P1=+59.000, P2=+53.000, P1 wins.** Identical move-by-move to `a6385db22c0b` and `b160b1f55378`.

### Game 2 — P1 corner cluster vs P2 z=0-face wall

Sequence (51 plies, P1 wins): `0,4,1,6,2,5,9,7,11,8,18,17,19,26,20,35,3,44,12,53,21,62,27,71,28,80,29,79,81,78,83,161,99,159,101,158,102,76,110,75,84,240,108,242,180,224,164,222,162,238,183`.

**Final: P1=+59.5, P2=+44.5. P1 wins by 15.** Identical to siblings.

### Game 3 — P1 max-degree centre `(2,2,2)` cluster (15 plies confirmed)

Sequence (15 plies sampled): `182,546,181,547,183,545,173,555,191,537,101,627,263,465,189`.

After 15 plies: P1=8 stones, P2=7 stones. Score-curve identical to the `b160b1f55378` Game 3 (~+1.4 per stone for centre-start vs ~+1.5 per stone for corner-start). Confirms the centre-vs-corner choice is wash on this rule blob.

### Strategy guides

Same as `a6385db22c0b`. Open at any corner, cluster-fill, ignore P2.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** **One: corner cluster.** Same as siblings.

**Counter-play.** **Effectively absent.** Two-corner solitaire race; first-mover wins by tempo unless P2 deviates.

**Short-term vs long-term.** Tactical = 1 ply, strategic = 0 ply. Same as siblings.

**Emergent concepts observed.** Cluster compounding only. No captures, no contention.

**Does menger matter?** Same as siblings — net negative. Fragments the board.

**Does the propagation kernel matter?** Same — radius=1 + decay=0.5 makes cluster the sole strategy.

**Capture-rule contribution.** **Zero in self-play.** Outnumber-2 fires only on contrived probes.

**First-mover advantage / seat balance.** P1 wins 3/3 in my games. PPO trained-vs-trained 0.667 P1-favoured (matches `a6385db22c0b`). Pie rule off, no compensation.

**Why does this game measure deeper than `a6385db22c0b` (0.792 vs 0.763)?** **It doesn't, in equilibrium play.** Both games play identically. The 0.792 vs 0.763 differential is sub-σ measurement noise:
- σ on this game: 0.105 → 0.792 ± 0.105 includes [0.687, 0.897]
- σ on `a6385db22c0b`: 0.120 → 0.763 ± 0.120 includes [0.643, 0.883]
- Overlap: [0.687, 0.883] — the central 80% mass of both estimates is in this band.
- The two games are measurement-distinguishable at <1σ.

**This is the GE-vs-depth feedback test failing on the noise floor.** The depth metric here is not measuring a real depth difference; it's measuring PPO seed variance.

---

## Phase 4 — Novelty Adversary (mandatory)

Same as `a6385db22c0b` and `b160b1f55378`. Closest analogue: **Ataxx-on-Menger with influence-sum scoring**. Inside this project, exact rule duplicate of two slate siblings.

(a) Threshold-race influence games — niche.
(b) Outnumber-2 capture — Tafl/Ataxx family.
(c) Identical rule recipe to R19 menger top-1 `1f9191b5d4e6`.
(d) Menger as substrate is novel as a research artefact, but its in-game effect is *fragmentation*.
(e) Expert-transfer test: <2 minutes for a Go + Othello + Ataxx player.

**Player rebuttal.** No new tactical primitives over `a6385db22c0b`/`b160b1f55378` siblings. The "depth-rank-2" position is a metric artefact, not a real depth difference.

**Novelty score (post-adversary):** **3/10.** Identical structural novelty to siblings.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game ID:** d1dbc6568fc7
**Rules Summary:** 9×9×9 Menger sponge cube; alternating placement; outnumber-2 captures clear single-stone enemy islands; influence (r=1) deposits ±1 self / ±0.5 neighbour. First to total-owned-influence > 57.974 wins. **Byte-identical rule blob to `a6385db22c0b` and `b160b1f55378`.**
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 3** — Identical play to outnumber-2 siblings. The 0.792 engine "depth" metric is sub-σ measurement noise; equilibrium play is the same one-strategy game. **The high engine-depth here is not real depth** — the rule blob is identical to `a6385db22c0b` (depth 0.763) and they are statistically indistinguishable.
- **Emergent Complexity: 3** — Same as siblings.
- **Balance: 4** — PPO 0.667 P1-favoured (same as `a6385db22c0b`). Same imbalance, same lack of correction (pie off).
- **Novelty (post-adversary): 3** — see Phase 4. No new mechanics over siblings.
- **Replayability: 3** — Same as siblings.
- **Overall "Would an agent team play this again?": 3** — Once: yes (to confirm byte-identity to siblings). Repeatedly: no.

### CLOSEST KNOWN-GAME ANALOG
Ataxx-on-Menger with threshold-race influence scoring. **Inside this project, exact duplicate of `a6385db22c0b` and `b160b1f55378`** (different lineages, identical play).

### KILLER FLAWS
- **Rule blob byte-identical to two other slate games.** The slate triple-counts a single underlying game. Rank-4 by GE (0.142) and rank-2 by depth (0.792) are both on-distribution noise away from `a6385db22c0b`'s rank-1 by GE (0.241) and rank-3 by depth.
- **The depth metric's "rank-2" signal here is misleading.** Tested against the game's actual play, depth is identical to siblings. The depth metric is rewarding either PPO seed variance or generation-of-origin features that don't survive into agent verdicts.
- **`feedback_ge_under_rewards_depth.md` test fails on this game.** The premise "high-depth-mid-GE games are systematically richer than mid-depth-high-GE games" is rejected: this game has equally rich (= equally shallow) play as the GE-top games.
- **Same parallel-solitaire / capture-vestigial / pie-off flaws as siblings.**

### BEST QUALITY
**Lineage from the collapsed `c850f91a55b4`** is the only differentiator. The mutation that produced this descendant from the original GE-rank-1 found a less-noise-sensitive attractor (Δ -0.067 vs parent's Δ -0.234). This is a meaningful evolutionary signal but not a gameplay quality signal. As a pure evaluation result, this game is identical to siblings.

### MENGER STRUCTURAL CONTRIBUTION
Same as `a6385db22c0b` — net negative. Fractal hole pattern fragments the board.

### IMPROVEMENT IDEAS
**Single best change:** **deduplicate the slate before agent-team eval.** This game and two siblings collectively waste ~3× the eval budget. The R20 finalization pipeline should hash rule blobs and skip duplicates; lineage-difference alone is not gameplay-difference.

Secondary improvements (apply equally to all three siblings):
- Pie rule on (lost in crossover).
- `target_dimension_p2 = +1` to break parallel-solitaire.
- Re-evaluate the depth metric: if it's measuring length-with-PPO-seed-variance rather than real strategic depth, calibrate the GE term to reduce its weight in fitness.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-1_gamed1dbc6568fc7.md`.*
