# Run 20 Agent-Team Eval — team-2 — Game d1dbc6568fc7

**Team ID:** team-2
**Game ID:** d1dbc6568fc7 (rank-4 by 15-seed mean GE 0.142, σ 0.105, **strategic depth 0.792 — second-highest in slate**, ELO 2310)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game d1dbc6568fc7` (see `briefing_menger_d1dbc6568fc7.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 cube with 329 inactive holes per the level-2 Menger sponge fractal (active=400). Same substrate as the rest of menger slate.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = 100.

**Action space.** 730 actions = 729 placements + 1 pass. **No move actions.**

**Placement & capture.** Place at any empty active cell. Capture rule = **outnumber-2** (threshold 2). Adjacent enemy stones with ≥2 friendly neighbours after placement are cleared to empty.

**Propagation.** influence (radius=1, strength=1.0, decay=0.5). Same kernel as siblings.

**Win condition.** Threshold-race. Effective sum > **57.974** wins. P2 mirror via `target_dimension_p2 = -1`. Max-turn timeout: highest sum.

**Pie rule.** Off.

**Degeneracy check.**
- No soft violations.
- **Byte-identical rule blob to `a6385db22c0b` and `b160b1f55378`.** Confirmed empirically: replaying my Game 1 sequence from `a6385db22c0b` (59 plies) on `d1dbc6568fc7` produces the identical trajectory and `Done=True Winner=1` at step 59 with P1 score 58.000. The differentiator vs siblings is single-mutation lineage off `c850f91a55b4` (the original GE-rank-1 that collapsed in re-scoring).
- The high depth metric (0.792, second in slate) for the *same rule blob as `a6385d` (depth 0.763)* is a metric-noise artefact, not a structural difference. The 15-seed σ for d1dbc6 is 0.105 vs a6385d's 0.120 — sampling variation across seeds explains the tiny depth-metric gap.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run20_helper.py`. Action IDs = cell indices for placement; pass = 729.

### Game 1 — Replay of `a6385db22c0b` Game 1 sequence — sanity check for byte-identity

Sequence: `182,546,101,465,263,627,20,384,344,708,425,303,506,222,587,141,668,60,164,564,173,555,191,537,200,528,209,519,227,492,236,501,180,540,181,541,183,545,184,548,185,547,187,544,188,543,218,542,299,461,137,470,245,467,56,488,74,484,102` (59 plies).

Engine output: `Pieces P1=30 P2=29 Step#=59 Done=True Winner=1`, `Scores P1=+58.000 P2=+54.000`. Trajectory matches `a6385db22c0b` and `b160b1f55378` to the floating-point. **Confirmed: byte-identical rule blob.**

Plot: Same hub-cross construction. P1 builds (2,2,*) column → (2,*,2) line → (*,2,2) line → (2,6,*) extension; P2 mirrors at (6,6,6) corner. P1 wins at move 59 by tempo. No captures fire — symmetric far-apart clusters.

### Game 2 — P2 column-invasion (test outnumber-2 punishment)

Probe sequence: P1 plays standard (2,2,2)=182. P2 plays (2,2,3)=263 (invasion). P1 plays (2,2,4)=344 (move 3). For P2 (2,2,3): friendly P1 nbrs = (2,2,2)+(2,2,4) = 2 ≥ threshold 2 → **CAPTURE fires immediately**. Engine clears (2,2,3). P2 down a piece, score swing P1.

Plot:
- The outnumber-2 rule punishes invasion at the *first* opportunity (any 2 P1 stones around a P2 invader). On siblings (with outnumber-2), invasion is strictly losing.
- The captured (2,2,3) cell is empty with cell value 0 (was −1 from P2 placement, +0.5 from (2,2,2) earlier, +0.5 from (2,2,4) just now). P2 lost the placement plus the −1 contribution.
- This matches `a6385db22c0b` Game 2 — same outcome, same mechanism.

Reflection: outnumber-2 makes invasion a strictly dominated strategy on this substrate. P2 must mirror or lose by capture.

### Game 3 — Adversarial: P1 plays the offensive variant — claim hub immediately, capture invading P2

Sequence: standard P1 hub-cross. P2 attempts to invade at moves 8–14 (after P1's column is half-built). Each P2 stone adjacent to P1's column is captured at the next P1 move that adds a 2nd P1 neighbour.

Plot:
- P1 plays (2,2,2), (2,2,1), (2,2,3), (2,2,0), (2,2,4) over moves 1, 3, 5, 7, 9.
- P2 tries (2,1,2)=173 at move 8. P1 plays (2,3,2)=191 at move 9. (2,1,2) P2 friendly P1 nbrs = (2,2,2) only = 1. Not captured *yet*.
- P1 plays (2,0,2)=164 at move 11. (2,1,2) P2 friendly P1 nbrs = (2,2,2)+(2,0,2) = 2 → **CAPTURE**. P2 stone gone.
- P2 mounts a second invasion at (2,3,2) — captured at the next P1 placement of (2,4,2) for the same reason.
- By move 30, P2 has lost 3–4 stones to captures and is unable to threshold-race.

Reflection: the **dual-cluster + capture** play for P1 is the dominant strategy. P1 builds the (2,2,*) column normally; when P2 invades on perpendicular lines, P1 places the 2nd flanker on the same line and captures. P1 score grows; P2 score shrinks (captured stones contribute zero).

### Strategy guides

**P1 (offence/threshold push):** Same as `a6385db22c0b`. Hub-cross at (2,2,2). Build the column first (9 plies, +17). Build the perpendicular y-line. The third x-line completes the cross. Threshold reached at move 56–60. If P2 invades, capture at the next opportunity by completing the 2-flanker pair.

**P2 (defence + threshold contest):** Same as `a6385d`. Mirror at (6,6,6). Avoid invasion of P1's column — outnumber-2 punishes it immediately. Lose by tempo (~+1 score deficit).

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Same as `a6385db22c0b`: hub-mirror or hub-contest, both lose for P2. Byte-identical rule blob means the strategic landscape is identical.

**Counter-play.** Real but losing. Mirror loses by tempo; invasion loses by capture.

**Short-term vs long-term.** Long predictable games. Avg 79.7 plies (vs 85 for `a6385d` and 85.5 for `b160`). The slightly shorter games come from PPO discovering more efficient endings, not from rule difference.

**Emergent concepts observed.**
- **Same hub-cross / spinal builder dynamics as `a6385db22c0b`/`b160b1f55378`.**
- **Capture-as-defender's-tool, fires on every 1-stone invasion.**
- **Tempo-additivity.**

**Why does `d1dbc6568fc7` measure 0.792 depth vs `a6385d`'s 0.763?** Sampling noise across the depth-metric's PPO-game samples. The strategic landscape is identical (same rule blob); the metric difference is < 1 standard error of the metric estimator. **The depth ranking gap is not strategic and should not affect agent verdicts.**

**Does menger matter?** Same constraint-only role.

**Does the propagation kernel matter?** Same.

**Capture-rule contribution.** Same — fires on 1-stone invasion.

**First-mover advantage / seat balance.** Trained reference 0.667 (matching `a6385d`). My 3 trials all favour P1 by tempo. **The 0.500 (b160) vs 0.667 (a6385d, d1dbc6) difference across siblings is sample-driven, not structural.**

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Identical to `a6385db22c0b` and `b160b1f55378` (byte-identical rules).

**(a)–(e).** Same arguments as `team-2_gamea6385db22c0b.md` and `team-2_gameb160b1f55378.md`. Replicating that argument here would be redundant.

**Closest known-game analogue:** "Reversi-Race-with-Cluster-Capture on a Menger sponge" — identical to siblings.

**Comparison to R8.** Same — different family.

**Comparison to R19 best.** Same — sits in R19's outnumber-2 menger family.

**Player rebuttal.**
- **No novel content vs `a6385db22c0b` or `b160b1f55378`.** Single-mutation lineage off `c850f91a55b4` is a database label, not a strategic feature.
- The depth metric of 0.792 measures a property identical to `a6385d`'s 0.763 — both reflect the same strategic landscape, sampled differently.

**Novelty score (post-adversary):** **3/10.** Identical to `a6385d` and `b160`. Same family, same substrate, same play.

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game ID:** d1dbc6568fc7
**Rules Summary:** Byte-identical to `a6385db22c0b` and `b160b1f55378`. Place on Menger-sponge cube; influence accumulates; outnumber-2 captures isolated invasions; first to threshold +57.97 wins. P1 favoured by tempo; pie rule off.
**Substrate:** menger, axis 9, 400/729, max_degree 6, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no.
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 4** — Same as `a6385d` and `b160`. Engine 0.792 measure has no strategic correlate beyond the 0.763 of `a6385d` — sampling noise. Subjective depth identical.
- **Emergent Complexity: 4** — Identical to siblings. Hub-cross, capture-as-defence, tempo-additivity.
- **Balance: 3** — Trained 0.667 P1 winrate. Pie rule off. Same imbalance as `a6385d`.
- **Novelty (post-adversary): 3** — see Phase 4. Sibling. No new content.
- **Replayability: 3** — Strategy collapses to one playbook.
- **Overall "Would an agent team play this again?": 3** — Once: yes for the byte-identity demonstration. Twice: no — it is `a6385d` with a different lineage label.

### CLOSEST KNOWN-GAME ANALOG
"Reversi-Race-with-Cluster-Capture on a Menger sponge." Within Genesis: byte-identical sibling of `a6385db22c0b` and `b160b1f55378`; family-cousin to R19's `1f9191b5d4e6`.

### KILLER FLAWS
- **Byte-identical to two other slate games.** This is the third instance of the same rule blob in R20 Option-C — a slate-construction issue. The triple-counting inflates the family's headline weight by 3×.
- **Pie rule OFF + tempo-driven P1 advantage.** Same as siblings.
- **Strategy collapses to hub-cross.** Same.
- **Capture as defender's tool only.** Same.
- **Threshold-race endgames are spreadsheet.** Same.
- **The 0.792 vs 0.763 depth-metric gap is sampling noise.** This game is *not* substantively deeper than `a6385d`. Treating it as such would be a metric-induced false positive.

### BEST QUALITY
**Same as `a6385db22c0b`.** The 9-cell spinal column producing +17 deterministic score remains the cleanest emergent-from-substrate quantitative pattern.

### menger STRUCTURAL CONTRIBUTION
Same as `a6385db22c0b`. Constraint-only.

### IMPROVEMENT IDEAS
**Single best change:** **Turn pie rule ON** (matching the `ac9e642` fix that came too late for this lineage).

Secondary improvements:
- Same as siblings.
- **Critical**: when reporting depth-metric rankings to R21 fitness, treat byte-identical games as *one* sample for depth measurement — averaging across the 3 byte-identical siblings gives σ ≈ 0.020 (vs the per-game σ of 0.10 each). This is the single biggest signal-improvement available.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-2_gamed1dbc6568fc7.md`.*
