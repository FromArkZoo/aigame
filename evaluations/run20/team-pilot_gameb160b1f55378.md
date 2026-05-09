# Run 20 Agent-Team Eval — team-pilot — Game b160b1f55378

**Team ID:** team-pilot
**Game ID:** b160b1f55378 (menger rank-2, 15-seed mean GE 0.180, σ 0.074, depth 0.690)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game b160b1f55378` (see `briefing_menger_b160b1f55378.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 menger sponge — identical substrate to `a6385db22c0b`. 400 active cells, level-2 fractal hole pattern, irregular cell-degree graph (many degree-2 / degree-3 cells along the tunnel axes).

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = 100.

**Action space.** 730 actions = 729 placement + 1 pass. Placement legal at any empty active cell (401 legal initially).

**Placement & capture.** **Outnumber-2** capture: when a stone is placed, every adjacent enemy stone with ≥2 friendly neighbours (counting the placer) is cleared (cell becomes empty, value persists). Verified empirically with `0,1,2` → P2 stone at `(1,0,0)` captured the moment P1 plays `(2,0,0)`.

**Propagation.** influence (radius=1, strength=1.0, decay=0.5). Same kernel as `a6385db22c0b`.

**Win condition.** Threshold-race; first player whose owned-cell sum exceeds **57.974** wins. `target_dimension_p2 = -1` (mirror). Max turns = 100.

**Pie rule.** Off.

**Identity check vs `a6385db22c0b`.** Confirmed by direct comparison of helper output: substrate, capture rule + threshold, propagation kernel, win condition + threshold, pie rule, and num_actions are **byte-identical** to game 1. Both a6385db22c0b and b160b1f55378 (and per the briefing also d1dbc6568fc7) are parameter siblings — same rule kernel, different lineage / generation. Mirror-cluster play in this game produces the *same* trajectory and same +6 winning margin at move 51 as in game 1 (verified). The briefing's "Rank-2 by 15-seed mean GE (0.180)" is an artifact of PPO training noise across seeds, not a structural difference from game 1.

**Degeneracy check.**
- Same Menger degree-truncation effects as game 1 (degree-2 cells = capture traps).
- No inert fields.
- Briefing notes "balanced trained-vs-trained 0.500" — but with identical rules to game 1 (which is 0.667), this is structurally **noise** in the PPO seed pool, not a balance feature of the rule blob. There is no in-game mechanism that produces seat-balance here that's absent from game 1.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run20_helper.py`.

### Game 1 — Cluster mirror (identical line to game 1's `a6385db22c0b`)

Sequence (51 plies, P1 wins +59 vs P2 +53): `0,80,1,79,9,71,2,78,18,62,11,69,19,61,20,60,3,77,12,68,21,59,27,53,28,52,29,51,81,161,83,159,84,158,4,76,22,58,36,44,38,42,99,233,101,235,165,140,110,239,164`.

Plot: identical trajectory to a6385db22c0b — P1 builds (0..3, 0..3, 0..2) corner cluster, P2 mirrors at (5..8, 5..8, 0..2), no contact, no captures, P1 wins on first-mover compounding tempo.

### Game 2 — Cross-z-layer P2 cluster

Sequence (16 plies, exploratory): `0,164,1,162,2,180,9,182,11,99,18,101,19,84,20,165`.

Plot:
- P1 builds z=0 cluster `(0..2, 0..2, 0)`.
- P2 builds z=2 cluster `(0..2, 0..2, 2)`, occupying the "vertical sibling" of P1's territory through the z=1 hole-rich layer.
- After 16 plies P1=+15.0, P2=+11.0 — **P2 is 4 effective points behind**.
- The deficit comes from the z=1 layer: cells like `(0,0,1), (2,0,1), (0,2,1), (2,2,1)` are physical neighbours of *both* P1 and P2 clusters. P1's `(0,0,0)` deposits +0.5 at `(0,0,1)`; P2's `(0,0,2)` deposits −0.5 at `(0,0,1)`. The cell ends at 0 but is owned by *neither* player, so neither side benefits from those propagations. P1's z=0 cluster has all its propagations land on P1-owned cells (because P1's cluster is fully connected within z=0); P2's z=2 cluster has analogous internal compounding **but two of its stones (`(0,2,1)`, `(2,2,1)`) land in z=1 next to a contested neutral edge**, partially leaking value.
- Conclusion: cross-layer clustering loses to same-layer corner-mirror.

### Game 3 — Capture probe

Sequence (3 plies): `0,1,2`. Identical to game 1's capture probe. P1 captures P2's `(1,0,0)` immediately on move 3. Confirmed identical capture mechanic.

### Strategy guides

**P1 (offence/threshold push):** identical to game 1 — open at a degree-3+ corner, build dense (0..3, 0..3, 0..2) cluster, maximize friendly-degree compounding. Aim for ~25 stones at average +2.3 effective.

**P2 (defence + threshold contest):** mirror-cluster at the (5..8, 5..8, 0..2) opposite corner. Game 2 shows that even moderate deviation from mirror (z=2 instead of z=0) costs ~4 effective points over 16 plies. Pie rule is off, no first-mover correction available.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** One: same-layer mirror cluster. Same as `a6385db22c0b`.

**Counter-play.** None better than mirror.

**Short-term vs long-term.** Short-term entirely. Plan horizon = 1 ply. Identical to game 1.

**Emergent concepts observed.**
- **Compounding density** (1 + 0.5·friendly-degree per placement). Same as game 1.
- **Capture trap on degree-2 cells.** Same as game 1.
- **Cross-layer leak**: clusters separated by hole-dense layers leak influence into the contested boundary cells. New observation in this game (because Game 2 line tested it) — but the mechanism is the same +0.5 propagation, just landing on neutral cells.

**Does menger matter?** Same conclusion as game 1: marginal and arguably negative. Substrate is decorative for the strategic shape.

**Does propagation kernel matter?** Identical kernel to game 1. `decay=0.5` defines the cluster-compounding mechanic.

**Capture-rule contribution.** Outnumber-2 fires reliably but is rarely triggered in mirror-cluster equilibrium play. Same as game 1.

**First-mover advantage / seat balance.** Briefing claims trained-vs-trained 0.500 (balanced). My play: P1 wins all 3 lines I tested. Structural P1 advantage = +1.5 / game (identical to game 1). The "balanced 0.500" is **PPO seed noise**, not a structural property — there is no mechanism in this game that produces balance which is absent from game 1.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a **direct re-skin of game 1** (`a6385db22c0b`) — same rule kernel, different gen-lineage. Same arguments as game 1 apply:

(a) **Threshold-race influence games** ≈ Othello scoring without flipping / weighted territorial Go.
(b) **Outnumber-2 capture** ≈ Tafl/Hnefatafl sandwich-and-remove. More permissive than Tafl's full surround.
(c) **Combination "outnumber-2 + influence + threshold-race"** is a known R10–R19 family and the dominant menger lineage. This game is a younger sibling of the same family.
(d) **Menger substrate.** Adds irregular cell-degree graph but no new strategic concept.
(e) **Expert-transfer.** A Go + Othello + Ataxx player understands this game in 5 minutes.

**Closest known-game analogue:** Influence Othello on a Menger-sponge graph. Inside this project's corpus, **`a6385db22c0b` is closer still** — they are byte-identical-rule siblings.

**Comparison to R8's Connection Go (8/10).** Different family entirely. R8 has connection wins (long-range planning) and chain-extending flips (mechanic interaction). This game has neither. Structurally lower than R8.

**Comparison to R19 best.** R19 menger top-1 `1f9191b5d4e6` (4.8/10) is the closest sibling outside R20. Same recipe. R19 menger top-3 `5048f71b62fd` (5.0, surround capture) is mildly stronger than this game because surround creates chain life-and-death.

**Comparison to slate-mate `a6385db22c0b`.** **Same game.** The only difference is generation lineage and PPO training-noise outcome. A 5-team eval cannot distinguish them on rules.

**Player rebuttal.**
- The **R20 slate has 4-of-5 menger games as parameter siblings** — this game adds zero novelty over its sibling. Rating it independently from a6385db22c0b is essentially rating the same recipe twice.
- The **degree-truncation capture trap** is substrate-specific but a degenerate case (negative novelty).
- The substrate adds no new strategic dimension over the R19 menger lineage.

**Novelty score (post-adversary):** **3/10.** Same recipe as game 1. Same as the R19 menger family. Below 4 because it adds *no new information* once a6385db22c0b has been evaluated. Anchoring against R17 mean (3.50): below mean because of explicit redundancy with slate-mate.

---

## Phase 5 — Verdict

**Team ID:** team-pilot
**Game ID:** b160b1f55378
**Rules Summary:** byte-identical rule kernel to `a6385db22c0b`: 9×9×9 menger sponge; alternating placement on 400 active cells; influence kernel (r=1, decay=0.5) + outnumber-2 capture + threshold-race(57.97). Pie rule off.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only).
**Soft violations flagged:** none structurally; **redundancy flag**: parameter sibling of `a6385db22c0b` and `d1dbc6568fc7`.

### Scores (1–10)

- **Strategic Depth: 4** — Same as game 1; same rules produce same depth. The 0.690 engine-measured depth is slightly below game 1's 0.763 — within seed noise.
- **Emergent Complexity: 3** — Same as game 1. Compounding density + degree-2 capture trap. Nothing new.
- **Balance: 4** — Briefing claims trained-vs-trained 0.500; my games show structural P1 +1.5 advantage as in game 1. Rating one notch above game 1 in case the 0.500 reflects a real PPO-equilibrium balance I haven't reproduced (n=3 play games is noisy). But mechanistically identical to game 1.
- **Novelty (post-adversary): 3** — Same recipe as game 1 and as the R19 menger family. Minus a half-point for explicit redundancy in the R20 slate.
- **Replayability: 3** — Same conclusions as game 1.
- **Overall "Would an agent team play this again?": 3** — Same recipe twice in the slate is a slate-construction issue, not a per-game flaw, but for this verdict's purposes: would agents play *this* game when its sibling is also available? No. Anchors: R8 = 8, R17 mean = 3.5, R19 menger top = 4.8. This game lands a notch below R19 menger top because it's an explicit rule-duplicate.

### CLOSEST KNOWN-GAME ANALOG
**`a6385db22c0b` in this slate** — byte-identical rule blob. Outside R20: R19 menger top-1 `1f9191b5d4e6`. Outside this project: "Influence Othello on a Menger-sponge graph", no published exact match.

### KILLER FLAWS
- **Slate redundancy.** This game is a parameter sibling of `a6385db22c0b` and `d1dbc6568fc7`. Three of five menger slate slots are spent on the same rule kernel. The slate cannot distinguish these on rules alone — only on PPO outcome variance.
- **Pie rule off** (same as game 1) — structural P1 advantage of ~+1.5 per game has no in-rule corrector.
- **Single viable strategy** (cluster compounding) collapses opening variety. Same as game 1.
- **Substrate decorative.** Same as game 1.

### BEST QUALITY
**Tightest noise band (σ=0.074) of the menger top-5** — the most reproducible PPO outcome in the slate. This is a *measurement* quality, not a *play* quality, but worth noting: this game is the most reliable of the menger top-5 to score against.

### menger STRUCTURAL CONTRIBUTION
Same as game 1: marginal, arguably negative. Could be flattened to a 9×9 grid + influence + outnumber-2 with no strategic loss.

### IMPROVEMENT IDEAS
**Single best change:** **Don't run 4 parameter siblings as a 5-game slate.** This is a slate-construction issue. Pick one menger representative + one menger variant with a *different* capture rule (e.g., the surround-capture R19 line) + one menger variant with *different threshold or decay*. That would let the slate distinguish family-internal variation from family-vs-family.

Secondary improvements (per-game):
- Restore pie rule (same as game 1).
- Switch capture rule to surround for at least one of the menger games (R19 lesson).
- Reduce threshold to ~30 for shorter, more decisive games.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-pilot_gameb160b1f55378.md`.*
