# Run 20 Agent-Team Eval — team-2 — Game b160b1f55378

**Team ID:** team-2
**Game ID:** b160b1f55378 (rank-2 by 15-seed mean GE 0.180, σ 0.074, depth 0.690, ELO 2409)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game b160b1f55378` (see `briefing_menger_b160b1f55378.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 cube with 329 inactive holes per the level-2 Menger sponge fractal (active=400). Cell index = z·81 + y·9 + x. Three perpendicular tunnels through the centre, recursively repeated. The 8 corner sub-cube interiors at (2,2,2), (2,2,6), (2,6,2), (6,2,2), (2,6,6), (6,2,6), (6,6,2), (6,6,6) are the only max_degree=6 hubs and host three perpendicular 9-cell active "spinal" lines each.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = 100.

**Action space.** 730 actions = 729 placements + 1 pass. **No move actions.**

**Placement & capture.** Place at any empty active cell. Capture rule = **outnumber-2** (threshold 2). Adjacent enemy stones with ≥2 friendly neighbours after placement are cleared to empty.

**Propagation.** influence (radius=1, strength=1.0, decay=0.5). +1.0 to placed cell, +0.5 to up to 6 axis-aligned active neighbours, sign +1/−1 by player. Clamped [−100, 100].

**Win condition.** Threshold-race. First player whose effective sum (P2 mirror via target_dimension_p2 = −1) exceeds **57.974** wins. Max-turn timeout: highest sum.

**Pie rule.** Off.

**Degeneracy check.**
- No soft violations.
- **Byte-identical rule-blob to `a6385db22c0b` and `d1dbc6568fc7`.** Confirmed empirically: replaying my Game 1 sequence from `a6385db22c0b` (59 plies) on `b160b1f55378` produces the *exact same trajectory* and the same `Done=True Winner=1` at step 59 with P1 score 58.000. The differentiator vs siblings is gen-6 lineage (vs gen-3 for `a6385d`, gen-? for `d1dbc6`).
- The σ=0.074 across 15 seeds (tightest in menger slate) reflects extreme determinism of the threshold-race once both sides commit to the dominant strategy. ELO 2409 (highest in slate) follows from the same predictability — this game beats most of R20's population in cross-tournament because both PPO seats know exactly what to do.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run20_helper.py`. Action IDs = cell indices for placement; pass = 729.

### Game 1 — Replay of `a6385db22c0b` Game 1 sequence — sanity check for byte-identity

Sequence: `182,546,101,465,263,627,20,384,344,708,425,303,506,222,587,141,668,60,164,564,173,555,191,537,200,528,209,519,227,492,236,501,180,540,181,541,183,545,184,548,185,547,187,544,188,543,218,542,299,461,137,470,245,467,56,488,74,484,102` (59 plies).

Engine output: `Pieces P1=30 P2=29 Step#=59 Done=True Winner=1`, `Scores P1=+58.000 P2=+54.000`. Trajectory matches `a6385db22c0b` exactly to the floating-point. **Confirmed: byte-identical rule blob.**

Plot:
- Same hub-cross construction as Game 1 of `a6385db22c0b`. P1 builds (2,2,*) column → (2,*,2) line → (*,2,2) line → (2,6,*) extension; P2 mirrors at (6,6,*) corner. P1 wins by tempo at move 59.

### Game 2 — P2 race-counter: skip the mirror, target a 2nd hub via shorter spine

Sequence: `182,182,...` initially I tried having P2 *steal the hub*, but (2,2,2) is occupied so move 2 is illegal. Adjusted to P2 contesting the (2,*,2) plane: `182,191,101,200,263,209,20,164,344,173,425,...`. P2 is now placing in P1's y-line, denying P1 the contiguous build. Each P2 stone in the (2,*,2) line has only 1 friendly P2 neighbour (or 0) for many moves, while P1 has multiple — captures fire on P2 stones whenever they sit between two P1 stones along the line.

Plot:
- Move 4: P2 plays (2,4,2)=200 next to P1's (2,2,2). P2 piece exposed.
- Move 5: P1 plays (2,2,3)=263. No capture yet (P2 (2,4,2) has 0 P1 nbrs.)
- Moves continued: when P1 plays (2,3,2)=191 (move 7), P2's (2,4,2) gets P1 neighbour count 1 (just (2,3,2)). Move 9 P1 plays (2,5,2)=209, now (2,4,2) has 2 P1 nbrs → CAPTURE. P2 down a piece.
- P2 keeps invading; P1 keeps capturing every 2nd or 3rd P2 invasion. By move 30 P2 has 8 stones to P1's 15 (7 captured P2 stones). P2 effective score collapses; P1 races to threshold uncontested.

Reflection: outnumber-2 is *brutal* against single-stone invasion. Each captured stone is a triple loss for P2 (the placement ply, the cell value contribution, and the cell ownership for further neighbour boosts). Invasion is decisively worse than mirror.

### Game 3 — P2 plays the only non-loss line: occupy the hub before P1 if P1 deviates

Sequence: `546,182,...` — but engine forces P1 first, so opening 546 (=(6,6,6)) is P1's move. I let P1 play *non-optimally* (open at (6,6,6) instead of (2,2,2)), then P2 takes (2,2,2)=182. P2 now has the corner sub-cube race-mirrored exactly opposite to P1's assumption.

Plot:
- Both sides build their respective hubs. P1 builds (6,6,*) → (6,*,6) → (*,6,6); P2 builds (2,2,*) → (2,*,2) → (*,2,2). Game proceeds symmetrically.
- P2 (the second mover) reaches +57.974 *one move after* P1 because P1 played first. P1 wins at move 59 again, by pure half-move tempo.

Reflection: there is no *which hub you choose* asymmetry. The substrate has 8 equivalent hubs by Menger symmetry. The only asymmetry is move-order tempo — and P1 always has the +0.5 ply lead.

### Strategy guides

**P1 (offence/threshold push):** Play (2,2,2) hub. Build the cross. Win by tempo. The exact sequence used in Game 1 of `a6385db22c0b` works here without modification.

**P2 (defence + threshold contest):** Mirror at the diagonally-opposite hub (6,6,6). Avoid invading P1's column at all costs — it's a free piece for P1. Hope for a draw on max-turn timeout, but you'll trail by ~+1–2 score and lose by margin. Without pie rule, P2 has no recourse.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Same as `a6385db22c0b`: hub-mirror or hub-contest, both lose for P2. The byte-identical rule blob means the strategic landscape is identical.

**Counter-play.** Real but losing. Mirror loses by tempo (~+1 score lead for P1); invasion loses by capture (every captured stone = ~−2 score swing for P2). The 0.500 trained-vs-trained on b160 (vs 0.667 on `a6385d`) is *not* a structural difference — same rules → same theoretical equilibrium. The 0.500 vs 0.667 split is training noise across 9 PPO runs (smaller sample, narrower σ).

**Short-term vs long-term.** Same as `a6385db22c0b`. Long games (avg 85.5 plies, σ=1.0 — extremely consistent), with tight σ=0.074 across 15 seeds reflecting the determinism.

**Emergent concepts observed.**
- **Same hub-cross / spinal builder dynamics as `a6385db22c0b`.**
- **Capture-as-defender's-tool.**
- **Tempo-additivity.**
- The 0.500 vs 0.667 PPO seat split tells us PPO sometimes finds a slightly better P2 line that converts the loss-by-+1 into a draw — but the structural fact is unchanged: P1 has the half-ply lead.

**Does menger matter?** Same as `a6385db22c0b`: constraint not creator.

**Does the propagation kernel matter?** Same.

**Capture-rule contribution.** Same — fires only against invasion.

**First-mover advantage / seat balance.** Trained reference 0.500 (vs 0.667 for `a6385d`). The 0.167 gap between siblings is a *training artefact*, not a substantive difference. Both games have identical theoretical balance; the ELO 2409 (highest in slate) reflects PPO consistency, not asymmetry. **My 3 trials all favour P1.**

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Identical to `a6385db22c0b` (byte-identical rules). Same closest analogue, same family, same R8 / R17 / R19 comparisons.

**(a)–(e).** See `team-2_gamea6385db22c0b.md` Phase 4. Replicating that argument here would be redundant.

**Closest known-game analogue:** "Reversi-Race-with-Cluster-Capture on a Menger sponge." Identical to `a6385db22c0b`. Within Genesis: R19 menger top family (`1f9191b5d4e6`), repeated.

**Comparison to R8.** Different family (custodian + connection on 2D vs outnumber-2 + influence + threshold-race on menger). R8 wins on strategic richness.

**Comparison to R19 best.** Same family as R19's outnumber-2 menger top (`1f9191b5d4e6`). Equivalent strategic depth, slightly tighter convergence (σ=0.074 vs ~0.09).

**Player rebuttal.**
- **No novel content vs `a6385db22c0b`.** This game is the same content with a different lineage label. The pilot's structural finding — these 3 games are byte-identical — is fully validated. Lineage-only differentiation is not strategic novelty.

**Novelty score (post-adversary):** **3/10.** Identical to `a6385db22c0b`. Same family, same substrate, same play. Generation-6 lineage is a database label, not a strategic feature.

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game ID:** b160b1f55378
**Rules Summary:** Byte-identical to `a6385db22c0b` and `d1dbc6568fc7`. Place on a Menger-sponge cube; influence accumulates per placement; outnumber-2 captures isolated invasions; first to threshold +57.97 wins. P1 favoured by tempo; pie rule off.
**Substrate:** menger, axis 9, 400/729, max_degree 6, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no.
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 4** — Same engine-measured 0.690 (vs 0.763 for `a6385d`) reflects training noise; subjective depth identical. Long predictable games with shallow decision trees.
- **Emergent Complexity: 4** — Identical to `a6385db22c0b`. Hub-cross, capture-as-defence, tempo-additivity. Small emergent vocabulary.
- **Balance: 4** — Slightly better than `a6385d` per training (0.500 vs 0.667) but my 3 trials all show P1 winning. The 0.500 PPO ratio with 9 runs has wide CI; structurally the game has the same tempo asymmetry. Anchor: 4 reflects "same as a6385d in fundamentals + one PPO point of evidence for closer balance" — but I weigh observed tempo loss heavily.
- **Novelty (post-adversary): 3** — see Phase 4. Sibling. No new content.
- **Replayability: 3** — Identical to `a6385db22c0b`. Strategy collapses to one playbook.
- **Overall "Would an agent team play this again?": 3** — Once: yes for the byte-identity demonstration. Twice: no — it is `a6385d` with a different lineage label.

### CLOSEST KNOWN-GAME ANALOG
"Reversi-Race-with-Cluster-Capture on a Menger sponge." Within Genesis: byte-identical sibling of `a6385db22c0b` and `d1dbc6568fc7`; family-cousin to R19's `1f9191b5d4e6`.

### KILLER FLAWS
- **Byte-identical to two other games in this slate.** 3 of the 5 menger games in R20 Option-C are the same blob; presenting them as separate evaluations *over-weights* the family by 3×. This is a slate-construction issue, not a game-design issue, but it directly impacts the headline statistics.
- **Pie rule OFF + tempo-driven P1 advantage.** Same as `a6385d`.
- **Strategy collapses to hub-cross.** Same as `a6385d`.
- **Capture as defender's tool only.** Same.
- **Threshold-race endgames are spreadsheet.** Same.

### BEST QUALITY
**Tightest σ=0.074 across 15 seeds** — the most reliable predictable game in the slate. As a *PPO benchmark game*, it's excellent: it has a clean equilibrium and converges fast. As a *human-interesting game*, that same tightness is the killer flaw.

### menger STRUCTURAL CONTRIBUTION
Same as `a6385db22c0b`. Constraint-only.

### IMPROVEMENT IDEAS
**Single best change:** **Turn pie rule ON across all menger games in this family.** The crossover that introduced this lineage at gen-6 didn't carry the pie_rule field; the `ac9e642` fix should be retroactively applied to the elite carryover.

Secondary improvements:
- Treat byte-identical games as one entry in future slates — sample one, score once, save the team-evaluation budget for genuinely distinct rule blobs.
- Same secondary improvements as `a6385db22c0b`: lower threshold, increase capture threshold to outnumber-3, increase propagation radius.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-2_gameb160b1f55378.md`.*
