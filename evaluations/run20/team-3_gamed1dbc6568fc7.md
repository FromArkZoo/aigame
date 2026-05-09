# Run 20 Agent-Team Eval — team-3 — Game d1dbc6568fc7

**Team ID:** team-3
**Game ID:** d1dbc6568fc7 (menger rank-4 by 15-seed mean GE 0.142, σ 0.105; rank-2 by strategic depth 0.792)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game d1dbc6568fc7` (see `briefing_menger_d1dbc6568fc7.md` for full rules and engine internals).

---

## Phase 1 — Rule Comprehension

**Board.** Identical menger sponge — 400 active cells, 8 deg-6 hubs at `{2,6}³`. Cell index `c = z*81 + y*9 + x`.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = 100.

**Action space.** 730 actions = 729 placement + 1 pass.

**Placement & capture.** Capture rule = **outnumber-2** (threshold 2). On placement, any enemy stone with ≥2 friendly neighbours is cleared.

**Propagation.** influence, r=1, strength=1.0, decay=0.5.

**Win condition.** Threshold-race > 57.974. `target_dimension_p2 = -1` (mirror).

**Pie rule.** False.

**Degeneracy check.**
- **Byte-identical rule blob to `a6385db22c0b` and `b160b1f55378`.** Confirmed via engine output: substrate / capture / propagation / win headers all match. Hub-rush sequence `182,506,…,104` produces identical end-state P1 +58 / P2 +55 / 59 plies. Differences across the trio are **lineage-only** (this is a mutation off `c850f91a55b4`).
- All rules fire normally (capture in adversarial play, propagation, threshold-race).

---

## Phase 2 — Strategic Play

### Game 1 — Hub-rush

Sequence: `182,506,186,510,218,542,222,546,183,507,181,505,191,515,173,497,263,587,101,425,187,511,185,509,195,519,177,501,267,591,105,429,219,543,217,541,227,551,209,533,299,623,137,461,223,547,221,545,231,555,213,537,303,627,141,465,102,416,104` (59 plies, **P1 wins +58 / P2 +55**, engine output identical to `a6385db22c0b`).

### Game 2 — Cross-layer hub denial

Sequence: `182,222,218,186,506,542,510,546,…` ending P1 win at ply 53.

### Game 3 — Adversarial capture race

Greedy capture-aware play produces same corner-cluster + capture-loop pattern as `a6385db22c0b`, P1 wins ~71 plies.

### Strategy guides

**P1:** Hub-rush + 24-neighbour walk + overlap finish. Same as `a6385db22c0b`.

**P2:** Mirror, accept tempo deficit. Same as `a6385db22c0b`. Pie OFF.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Same as outnumber-2 siblings — hub-rush dominant, mirror or denial as P2 alternatives, capture-driven defence loses to clean accumulation.

**Counter-play.** Limited. Same as siblings.

**Short-term vs long-term.** Long game, shallow horizon. Same as siblings.

**Emergent concepts observed.** Same set as `a6385db22c0b`: 8-hub scaffold, hub-neighbour walk, fortification dilemma, capture-loop (rare), overlap mining.

**Does menger matter?** Same as siblings.

**Does the propagation kernel matter?** Same as siblings.

**Capture-rule contribution.** Same as siblings — fires 0–1× in clean play, shapes opening only.

**First-mover advantage / seat balance.** Trained-vs-trained 0.667 P1-favoured (same as `a6385db22c0b`), my games P1 won 3/3. Pie OFF, structural P1 lead.

**On the depth-record pairing.** Briefing asks whether `d1dbc6568fc7` (depth 0.792) and `5f5c72e15220` (depth 0.894) share a structural property the GE-top-3 don't. **My verdict: NO.** These two games are *not* structurally similar:
- `5f5c72e15220` is outnumber-3 (capture inert).
- `d1dbc6568fc7` is outnumber-2 (rule-identical to GE-top siblings).

So the depth signal across the slate is two distinct effects:
1. For outnumber-2 trio (depth 0.763 / 0.690 / 0.792) — **noise** in the depth metric across rule-identical games (max delta 0.102 across siblings is the noise floor).
2. For outnumber-3 (depth 0.894) — diversity signal mistaken for depth (Phase 4 of `5f5c72e15220` verdict).

**Therefore: depth metric is unreliable across this slate.** R21 fitness should not weight it without further validation.

---

## Phase 4 — Novelty Adversary (mandatory)

Same adversary case as `a6385db22c0b`:

(a–e) Same arguments as siblings. Threshold-race ≈ Othello scoring; outnumber-2 ≈ Ataxx; combination has no published external analogue but exists internally as R19 menger top-1 family.

**Closest known-game analogue:** Same as siblings — "Ataxx-on-Menger with influence scoring." Inside Genesis: parameter twin of `a6385db22c0b` and `b160b1f55378`.

**Comparison to R8 (8/10):** Different family — same as siblings.

**Comparison to R19 best:** Same — re-skin of R19's outnumber-2 menger.

**Player rebuttal.** Same emergents as siblings; substrate-specific 8-hub scaffold; threshold-race subtracts goal-shape; pie OFF imbalance; capture rare. Lineage from `c850f91a55b4` (collapsed-finalization parent) is curious but doesn't change the agent-experience.

**Novelty score (post-adversary):** **3/10.** Same as siblings.

---

## Phase 5 — Verdict

**Team ID:** team-3
**Game ID:** d1dbc6568fc7
**Rules Summary:** Byte-identical recipe to `a6385db22c0b`/`b160b1f55378`: alternating placement on 9³ Menger sponge with outnumber-2 capture, ±1.0/±0.5 propagation, threshold-race to >57.97. Lineage differs (mutation off the collapsed `c850f91a55b4`); rules do not.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no.
**Soft violations flagged:** **lineage redundancy** — third slate slot occupied by the same recipe as `a6385db22c0b` and `b160b1f55378`. R20's 5-menger slate effectively contains 3 distinct games.

### Scores (1–10)

- **Strategic Depth: 4** — Same recipe as siblings, same hub-claim opening + mechanical neighbour walk. Engine 0.792 depth is within noise of the sibling values (0.763, 0.690).
- **Emergent Complexity: 4** — Same emergents as siblings.
- **Balance: 3** — Trained 0.667 P1-favoured (same as `a6385db22c0b`), my play P1 3/3, pie OFF.
- **Novelty (post-adversary): 3** — Same as siblings.
- **Replayability: 3** — Same as siblings.
- **Overall "Would an agent team play this again?": 3** — Same as siblings. The slate-position-rank-4 and depth-rank-2 are noise artefacts; structurally this is the same game as `a6385db22c0b`.

### CLOSEST KNOWN-GAME ANALOG
"Ataxx-on-a-Menger-sponge with influence scoring." Inside Genesis: rule-identical to `a6385db22c0b` and `b160b1f55378`; family-relative to R19 `1f9191b5d4e6` (4.8/10).

### KILLER FLAWS
- **Lineage redundancy** (third copy of the same recipe in the slate).
- **Pie rule OFF** — structural P1 tempo lead.
- **Depth metric (0.792) is noise** within the rule-identical sibling trio.
- **Mechanical mid-game** (same as siblings).

### BEST QUALITY
The lineage detail is mildly interesting — `c850f91a55b4` collapsed in finalization (Δ -0.234) but this single-mutation descendant stabilized at Δ -0.067. The mutation found a less-luck-sensitive attractor in score-space. **But this is a property of the evolution, not of the game** — the agent-experience is identical to the parent recipe. The "best quality" is therefore really the same as `a6385db22c0b`: 5–8 plies of opening choice + fortification dilemma.

### MENGER STRUCTURAL CONTRIBUTION
Identical to `a6385db22c0b`. 8-hub scaffold, opening structure; mid- and end-game would play similarly on any sparse high-degree graph.

### IMPROVEMENT IDEAS
**Single best change:** **Restore pie rule** — same recommendation as siblings; same code path (`ac9e642`).

Secondary improvements:
- **Deduplicate sibling games at the slate level.** This is the third slot eaten by the same recipe.
- **Investigate why depth metric varies 0.690–0.894 across rule-identical games.** This is a metric-noise diagnostic, not a game-property finding.
- Lower threshold to ~40 for sharper endgame.
- Capture clears value as well as ownership.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-3_gamed1dbc6568fc7.md`.*
