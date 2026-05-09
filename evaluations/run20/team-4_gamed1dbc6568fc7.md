# Run 20 Agent-Team Eval — team-4 — Game d1dbc6568fc7

**Team ID:** team-4
**Game ID:** d1dbc6568fc7 (menger rank-4 by 15-seed mean GE 0.142, σ 0.105; rank-2 by strategic depth 0.792)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game d1dbc6568fc7` (see `briefing_menger_d1dbc6568fc7.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 menger sponge — 400 active cells of 729 grid positions; identical fractal hole pattern to siblings. Cell index = `z*81 + y*9 + x`. **Byte-identical rule blob to `a6385db22c0b` and `b160b1f55378`** per the pilot's structural finding — depth differences are seed noise, lineage is the only differentiator.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = 100.

**Action space.** 730 actions = 729 placement + 1 pass. **No move actions** (D1 hybrid ban active).

**Placement & capture.** Capture rule = **outnumber-2** — same as `a6385db22c0b` and `b160b1f55378`. Placement at empty active cell; any adjacent enemy stone with ≥2 friendly neighbours (counting just-placed) is **cleared** (not flipped).

**Propagation.** influence (radius=1, strength=1.0, decay=0.5).

**Win condition.** Threshold-race — first to exceed **57.974** wins. `target_dimension_p2 = -1` (P2 mirror).

**Pie rule.** False.

**Degeneracy check.**
- No inert fields. No soft violations.
- Same menger geometry as siblings.
- **Lineage:** this game is a single mutation off `c850f91a55b4` (the original GE-rank-1 that collapsed in finalization). The mutation found a more stable attractor (Δ-0.067 vs parent's Δ-0.234), but the rule blob is the same as siblings.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run20_helper.py`. Same dynamics as siblings — verified by spot-check.

### Game 1 — Mirror cluster build (confirmation)

Sequence: `182,546,181,545,183,547,173,537,191,555,101,465,263,627` (14 plies).

Plot: Identical scoring to `a6385db22c0b` Game 1 — both at +13 after turn 14. Same +2/ply gradient.

### Game 2 — Capture verification

Sequence: `182,181,183,173` (4 plies).

Plot: Capture fires at turn 4 (P2's 2nd stone gives 2 P2-neighbours of (2,2,2), centre clears). P1 piece count 2→1. Identical to `a6385db22c0b` Game 2.

### Game 3 — P1 cluster + P2 parasitic shell-2

Sequence: `182,164,181,200,183,344,173,20,191,628,101,556` (12 plies — P1 builds (2,2,*) cluster; P2 walls shell-2 cells).

Plot:
- P1 builds cube near (2,2,2). P2 takes (2,0,2), (2,4,2), (2,2,4), (2,2,0), then face-corners.
- P1 cube at +11 after 7 own-plies. P2 at ~+8 after 6 own-plies (cells with 0 friendly neighbours initially, then shell-2 self-clusters as P2's nearby cells start having 1+ friendly).
- No captures — P2 not adjacent enough to P1.

After 12 plies: P1=+11, P2=+9.

This is the same parasitic strategy that worked for P2 in `b160b1f55378`, but here PPO converged to a P1-favoured equilibrium (0.667 trained WR) rather than the balanced one. Same rule blob, different attractor.

### Strategy guides

**P1 (offence/threshold push):** Same as siblings — pick a 6-degree menger hub, build the cube + axials. Ignore P2 denial unless they spend 2 stones adjacent to one of yours, in which case re-occupy (the residue may favour the side that placed last).

**P2 (defence + threshold contest):** Same as siblings — parasitic shell-2 wall is the candidate counter. PPO converged to P1-favoured 0.667 here, suggesting either the parasitic strategy was not found in this lineage's training or the seat-2-side benefit is conditional on starting position. Mirror = lose by tempo.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Same two as `b160b1f55378`:
1. **Symmetric far-hub cluster** (loses to tempo).
2. **Parasitic shell-2 wall** (cancels tempo at cost of cluster bonus).

**Counter-play.** Real, same as siblings.

**Short-term vs long-term.** **Engine reports 0.792 depth — second-highest in slate.** What does it mean subjectively? Same as `5f5c72e15220` — the higher depth comes from longer games and residue persistence, not deeper decision trees. My 14-ply mirror game ran identically to `a6385db22c0b`'s 14-ply mirror. The residue-persistence effect mildly differentiates from siblings, but does not show up as additional decision points.

**Emergent concepts observed.**
- Same as siblings: influence-cube cluster, +2/ply gradient, captures rare.
- **Lineage stability:** the briefing flags this lineage as more luck-stable (parent `c850f91a55b4` collapsed -0.234 while this child collapsed only -0.067). This is **a metric property**, not an in-play property — does not surface as a different play experience.

**Does menger matter?** Same as siblings — channels viable hubs.

**Does the propagation kernel matter?** Yes — same as siblings.

**Capture-rule contribution.** Marginal — same as outnumber-2 siblings.

**First-mover advantage / seat balance.** Training reports **0.667 P1-favoured** (same as `a6385db22c0b`, *unlike* the balanced `b160b1f55378`). With identical rules, this difference is **lineage-dependent**: PPO converged to a P1-favoured equilibrium in this lineage. Pie rule absent.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Identical rule blob to `a6385db22c0b` and `b160b1f55378`. Novelty argument is identical.

(a) Threshold-race influence games — Othello/Go-territorial without flips/captures.
(b) Outnumber-2 capture — Tafl/Ataxx family.
(c) The combination — R19's dominant menger family.
(d) Menger substrate — no published prior art.
(e) Expert-transfer test — 3–5 minutes for a Reversi+Ataxx+Go player.

**Closest known-game analogue:** Ataxx with influence scoring on a 3D fractal cube. Same as siblings.

**Comparison to R8.** Different family. Far below R8 ceiling.

**Comparison to R19 best.** R19 menger top family is the direct ancestor.

**The depth-metric finding (continued from `5f5c72e15220`).** This game is the second confirmation. Engine reports depth 0.792, but the rule blob is identical to `a6385db22c0b` (depth 0.763) — both reach +13 at turn 14 in the same arithmetic. The depth difference is seed-noise residual after 15-seed averaging. **This supports the conclusion that the depth metric is partially noise / partially game-length artifact.**

**Player rebuttal.**
- Influence-cube cluster is genuinely emergent (same as siblings).
- Lineage-stable scoring is a metric property, not a play feature.
- **Subtraction:** 3 byte-identical games dilute the slate's claim to 7 distinct entries.

**Novelty score (post-adversary):** **3.5/10.** Same as outnumber-2 siblings.

---

## Phase 5 — Verdict

**Team ID:** team-4
**Game ID:** d1dbc6568fc7
**Rules Summary:** Same as `a6385db22c0b` and `b160b1f55378` — outnumber-2 + influence(r=1, decay=0.5) + threshold-race(57.97) on 9×9×9 menger sponge. Distinguished only by lineage (gen 6, mutation off the original collapsed GE-rank-1) and a slightly higher engine-depth measurement (0.792 vs 0.763).
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 4** — Same +2/ply cluster gradient and same race dynamic as siblings. 0.792 engine-depth metric is +0.029 above `a6385db22c0b` (0.763) — within seed noise. My play experience is at parity with `a6385db22c0b`. Slight edge for residue persistence in tail (since captures rare). Below R19 menger top 4.8.
- **Emergent Complexity: 4** — Same vocabulary as siblings. No new patterns observed beyond cluster + capture-rare + residue.
- **Balance: 3** — Training reports 0.667 P1-favoured WR — **same as `a6385db22c0b`**, worse than `b160b1f55378`'s 0.500. Pie rule absent. Same structural imbalance.
- **Novelty (post-adversary): 3.5** — Same as siblings; identical rule blob.
- **Replayability: 3** — Same as `a6385db22c0b`. Slate redundancy with two byte-identical siblings further reduces overall replayability.
- **Overall "Would an agent team play this again?": 3.5** — Once: yes, mostly to verify the byte-identical claim. The lineage-stability claim is a metric property that doesn't surface in play. Anchored against R19 menger top (4.8 — this is below) and R17 mean (3.5 — at par). Slate-context: this and `a6385db22c0b` should score very close.

### CLOSEST KNOWN-GAME ANALOG
Ataxx + Reversi-style scoring on a fractal 3D cube with influence-radius cluster bonuses. Direct lineage to R19 menger top family. Identical to siblings `a6385db22c0b` and `b160b1f55378`.

### KILLER FLAWS
- **Byte-identical to two slate siblings.** R20's 7-game slate has 3 entries with the same rule blob — substantial redundancy.
- **Pie rule missing.** 0.667 P1 imbalance unmitigated.
- **Captures rarely fire** in optimal play.
- **The "stability" advantage over parent `c850f91a55b4` is a metric property, not a play feature.** Does not differentiate from `a6385db22c0b` in any agent-relevant way.

### BEST QUALITY
**Lineage stability** — this game's child-of-collapsed-parent lineage demonstrates that mutation can find a more luck-robust attractor without changing the rule blob. This is a **process insight** (R20's mutation operator works), not a play feature. The actual crown jewel (influence-cube +2/ply cluster) is shared with siblings.

### MENGER STRUCTURAL CONTRIBUTION
**Same as siblings — channels, doesn't transform.** Hole pattern restricts viable hubs; could flatten to 9×9 grid with ≈ −1 depth.

### IMPROVEMENT IDEAS
**Single best change:** **Drop two of the three byte-identical menger games from the slate**, keep the one with best PPO-discovered balance (`b160b1f55378`'s 0.500), and add 2 distinct rule-blob entries instead. The current slate's rank-1, rank-2, rank-4 are the same game.

Secondary improvements:
- Add the pie rule (would lock in `b160b1f55378`'s balance, partially correct this game's 0.667).
- Audit the depth metric — three siblings with 0.763, 0.690, 0.792 depth scores from the same rule blob shows the metric is seed-noise-sensitive.
- Diversify the menger slate by varying capture, propagation, or threshold values.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-4_gamed1dbc6568fc7.md`.*
