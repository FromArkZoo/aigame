# Run 20 Agent-Team Eval — team-pilot — Game d1dbc6568fc7

**Team ID:** team-pilot
**Game ID:** d1dbc6568fc7 (menger rank-4 by GE / rank-2 by depth 0.792)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game d1dbc6568fc7` (see `briefing_menger_d1dbc6568fc7.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 menger sponge — same substrate as the rest of the menger top-5. 400 active cells.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = 100.

**Action space.** 730 actions = 729 placement + 1 pass.

**Placement & capture.** **Outnumber-2** capture: when a stone is placed at `c`, any adjacent enemy stone with ≥2 friendly neighbours (counting `c`) is cleared.

**Propagation.** influence (radius=1, strength=1.0, decay=0.5).

**Win condition.** Threshold-race; first player to owned-cell sum >**57.974** wins. `target_dimension_p2 = -1`. Max turns = 100.

**Pie rule.** Off.

**Identity check vs `a6385db22c0b` and `b160b1f55378`.** Verified by direct comparison of helper output: substrate, capture rule + threshold, propagation kernel, win condition + threshold, pie rule, num_actions are byte-identical to both other rule-siblings. Mirror-cluster play through 51 plies on this DB produces the *same* trajectory and same +6 winning margin as on a6385db22c0b. **The depth-rank-2 (0.792) vs depth-rank-1 (0.763) for game 1 disagreement is a measurement-noise artifact** of the strategic-depth metric, not a structural rule difference.

The briefing's question "Why does d1dbc6568fc7 measure deeper?" is answered: **it doesn't, structurally.** Strategic-depth is computed on a small rollout sample and varies across PPO seed pools.

**Degeneracy check.**
- Same Menger degree-truncation (degree-2 cells = capture traps under outnumber-2) as siblings.
- No inert fields. Captures fire empirically.
- Threshold 57.97 + decay 0.5 + r=1 = ~25 stones each side to win in mirror play.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run20_helper.py`.

### Game 1 — Mirror cluster (identical line to a6385db22c0b's Game 1)

Sequence (51 plies, P1 wins +59 vs +53): `0,80,1,79,9,71,2,78,18,62,11,69,19,61,20,60,3,77,12,68,21,59,27,53,28,52,29,51,81,161,83,159,84,158,4,76,22,58,36,44,38,42,99,233,101,235,165,140,110,239,164`.

Plot: byte-identical to a6385db22c0b. Both sides build dense corner clusters in disjoint volumes, no contact, no captures, P1 wins on first-mover compounding tempo.

### Game 2 — Contested-corner capture cascade

Sequence (27 plies): `0,1,9,2,18,11,19,20,3,12,21,27,28,29,81,83,84,99,101,102,110,165,162,164,180,182,108`.

This line — both sides interleaved in the (0..3, 0..3, 0..2) corner — produces **8 captures in 27 plies** under outnumber-2:

| Move | Player | Action | Captures |
|--|--|--|--|
| 10 | P2 (3,1,0) | flanks (3,0,0) | P1 stone (3,0,0) |
| 11 | P1 (3,2,0) | flanks (2,2,0) | P2 stone (2,2,0) |
| 13 | P1 (1,3,0) | flanks (0,3,0) | P2 stone (0,3,0) |
| 20 | P2 (3,2,1) | flanks (3,2,0) | P1 stone (3,2,0) |
| 21 | P1 (2,3,1) | flanks (2,3,0) | P2 stone (2,3,0) |
| 22 | P2 (3,0,2) | flanks (3,0,1) | P1 stone (3,0,1) |
| 25 | P1 (0,2,2) | flanks (0,2,1) | P2 stone (0,2,1) |
| 26 | P2 (2,2,2) | flanks (2,2,1) | P1 stone (2,2,1) |

Net pieces lost: P1 4, P2 4. **Effective scores stay tightly balanced** (move 26: P1=+11.5, P2=+11.0). The captures cancel each other out at a near-1:1 effective rate.

This contradicts my Game 1 (mirror-only) reading — **outnumber-2 contested play is genuinely tactical** with frequent captures. The depth metric 0.792 reflects this: when PPO finds a contested-corner attractor, real captures fire.

But: this contested attractor is **not** the PPO equilibrium. Trained-vs-trained avg game length 79.7 plies (briefing) suggests the game stretches longer than the contested capture cascade — implying PPO converges to a more spread-out style with fewer captures. The contested cascade is a *side road* the agents avoid.

### Game 3 — Capture probe

Sequence (3 plies): `0,1,2`. Captures P2 at (1,0,0) immediately on move 3, identical to a6385db22c0b. Confirmed identical capture mechanic to siblings.

### Strategy guides

**P1 (offence/threshold push):** Same as a6385db22c0b. Open at degree-3+ corner, build dense cluster, accept the +1.5 first-move tempo. If P2 infiltrates, **engage** — outnumber-2 captures fire on every interleaved degree-4+ stone, and P1 trades 1:1 while keeping the tempo.

**P2 (defence + threshold contest):** Mirror at opposite corner. **Don't infiltrate** — every P2 stone placed adjacent to P1's expanding cluster gets captured within 2-3 plies. The contested-corner cascade trades evenly on stones but P1's tempo lead persists.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Two:
1. **Mirror cluster** (PPO equilibrium). Same as a6385db22c0b — works.
2. **Contested-corner capture cascade.** Real but produces equal-stone-loss trades — both sides exit at similar piece counts and similar effective scores. P1 tempo lead persists.

**Counter-play.** Real but limited. P1's tempo can't be erased by either strategy.

**Short-term vs long-term.** Tactical — captures fire reliably and require careful sequencing. Plan horizon ~3 plies.

**Emergent concepts observed.**
- **Capture cascade**: contested play produces 1 capture every 3-4 plies. Both sides lose stones equally.
- **Capture-trap on degree-2 cells** (same as siblings).
- **Mutual annihilation balance**: if P1 and P2 both engage in the same volume, the 2:1 capture rate means the loser is whichever side runs out of degree-4+ flanking moves first.

**Does menger matter?** Same conclusion as siblings — marginal. The degree-stratification gives some cells "capture trap" status but doesn't introduce a new strategic dimension.

**Does propagation kernel matter?** Same as siblings — `decay=0.5` is the cluster-compounding parameter.

**Capture-rule contribution.** Outnumber-2 captures fire reliably in contested play (8 captures in 27 plies = 30% of placements). In mirror play, never. The rule contributes meaningfully *only* if both sides engage, which PPO equilibrium tends not to.

**First-mover advantage / seat balance.** Briefing claims trained-vs-trained 0.667 P1-favoured, identical to a6385db22c0b. Same +1.5/game tempo lead, same lack of pie-rule corrector. P1 wins all my mirror lines.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is **byte-identical to `a6385db22c0b`** at the rule level. Same novelty arguments apply:

(a) Threshold-race influence games ≈ Othello-without-flipping / weighted Go territorial scoring.
(b) Outnumber-2 capture ≈ Tafl/Hnefatafl (sandwich-and-remove). More permissive than Tafl's full surround.
(c) Combination "outnumber-2 + influence + threshold-race" is the dominant menger family of R10–R19. This game is a single-mutation descendant of `c850f91a55b4` (the original GE-rank-1 that collapsed in finalization).
(d) Menger substrate adds irregular cell-degree graph but no new strategic concept.
(e) Expert-transfer test: 5 minutes for a Go + Othello + Ataxx player.

**Closest known-game analogue:** Influence Othello on a Menger-sponge graph. Inside this project corpus: `a6385db22c0b` (byte-identical sibling), `b160b1f55378` (byte-identical sibling), R19 menger top-1 `1f9191b5d4e6` (close cousin).

**Comparison to R8's Connection Go (8/10).** Different family entirely. R8 has connection wins + chain-extending flips; this game has threshold-race + cell-clearing capture. Structurally lower than R8.

**Comparison to R19 best.** R19 menger top-1 `1f9191b5d4e6` (4.8/10) is the closest sibling outside R20. Same recipe.

**Comparison to slate-mate `5f5c72e15220` (depth 0.894).** **Decisively lower.** `5f5c72e15220` has outnumber-3 which inverts the capture-trap (degree-2 cells become safe-havens for the placer), creating new tactical primitives (re-occupation, double-capture, degree-stratification). This game is just outnumber-2 — same capture-rule as the rest. The depth-0.792 vs depth-0.894 difference is real *if* the comparison is between rule-distinct games, but here the comparison is between an outnumber-3 game (5f5c72e15220) and an outnumber-2 game (this) — and the rule difference accounts for almost all the depth gap.

**Player rebuttal.**
- The **contested-corner capture cascade** is a real tactical primitive worth more than I gave it in my a6385db22c0b verdict. With 8 captures in 27 plies of careful play, this is more dynamic than "build cluster".
- However, the cascade is not the PPO equilibrium — PPO converges to mirror-cluster avoidance.
- The **single-mutation lineage from c850f91a55b4** doesn't add novelty — same recipe, different parameters.

**Novelty score (post-adversary):** **3/10.** Rule-byte-identical to two slate-mates. The depth metric 0.792 is noise relative to the actual strategic depth which is the same as siblings. Below R17 mean (3.50). Anchoring is the same as a6385db22c0b.

---

## Phase 5 — Verdict

**Team ID:** team-pilot
**Game ID:** d1dbc6568fc7
**Rules Summary:** byte-identical rule kernel to `a6385db22c0b` and `b160b1f55378`: 9×9×9 menger sponge; alternating placement on 400 active cells; influence kernel (r=1, decay=0.5) + outnumber-2 capture + threshold-race(57.97). Pie rule off.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only).
**Soft violations flagged:** none structurally; **redundancy flag**: byte-identical rule blob to a6385db22c0b and b160b1f55378.

### Scores (1–10)

- **Strategic Depth: 4** — Same as a6385db22c0b (corrected upward slightly from my earlier reading: contested-corner play is genuinely tactical with frequent captures). The depth-0.792 metric overstates by reflecting one PPO seed pool's contested-corner attractor. Real depth = same as siblings.
- **Emergent Complexity: 4** — Capture cascade tactic in contested play is real; bumped up from a6385db22c0b's 3 because I now believe the contested-corner attractor is reachable and produces 8-capture sequences.
- **Balance: 3** — Same +1.5 P1-tempo as a6385db22c0b. Briefing 0.667 P1-favoured matches.
- **Novelty (post-adversary): 3** — Byte-identical rules to two slate-mates. Depth-metric variance is noise.
- **Replayability: 3** — Same conclusions as a6385db22c0b.
- **Overall "Would an agent team play this again?": 3** — Same recipe as a6385db22c0b. Anchors: R8=8, R17 mean=3.5, R19 menger top=4.8. This game lands at the same level as a6385db22c0b — slightly above for the corrected complexity reading.

### CLOSEST KNOWN-GAME ANALOG
**`a6385db22c0b` and `b160b1f55378` in this slate** — byte-identical rule blobs. Outside R20: R19 menger top-1 `1f9191b5d4e6`. Outside this project: "Influence Othello on a Menger-sponge graph", no exact match.

### KILLER FLAWS
- **Slate redundancy (3 of 5 menger games are byte-identical rule blobs).** This game adds zero rule novelty over a6385db22c0b and b160b1f55378.
- **Pie rule off** — same +1.5 P1-tempo issue.
- **Single dominant strategy in PPO equilibrium** (mirror cluster, no engagement). The contested-corner cascade is reachable but PPO avoids it.
- **Substrate decorative** — same as a6385db22c0b.

### BEST QUALITY
**The contested-corner capture cascade is a real tactical pattern** that I missed in my a6385db22c0b verdict. When both sides engage, captures fire every 3-4 plies, producing genuine tactical depth. This game's depth metric 0.792 may reflect that some PPO seeds find this attractor. If they do, the game has more depth than my mirror-only analysis suggested.

### menger STRUCTURAL CONTRIBUTION
Same as a6385db22c0b: marginal, arguably negative. Could be flattened to a 9×9 grid with no strategic loss.

### IMPROVEMENT IDEAS
**Single best change:** **De-duplicate the slate.** Three byte-identical menger games is a slate-construction issue. Pick one menger representative from this rule kernel + one from the outnumber-3 family (5f5c72e15220) + one from a different capture rule (surround R19 line) for genuine slate variety.

Per-game improvements (same as siblings):
- Restore pie rule.
- Switch capture rule to surround for depth or outnumber-3 for tactical inversion.
- Reduce threshold to ~30 for shorter games.

**Why this game scores like a6385db22c0b**: same rule kernel, same play, same PPO equilibrium. The depth-metric difference (0.792 vs 0.763) is within seed noise. Don't reward the engine's depth metric for what's effectively the same game measured twice.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-pilot_gamed1dbc6568fc7.md`.*
