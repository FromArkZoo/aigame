# Run 21 Agent-Team Eval — team-2 — Game 1fea3357dca4

**Team ID:** team-2
**Game ID:** 1fea3357dca4 (menger original rank-1 → rank 6 under 20-seed finalization; 20-seed mean GE 0.118, σ 0.085, calibrated komi_p2 0.05)
**Substrate:** menger (axis 9, 400 active / 729 grid, max_degree 6, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game 1fea3357dca4` (see `briefing_menger_1fea3357dca4.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Menger sponge, 400/729 active, max_degree 6 (same substrate as the menger pod). Cell = z·81 + y·9 + x.

**Turn structure.** Alternating, 1 piece/turn, P1 first. **Max_turns = 200.**

**Action space.** 731 = 729 place + pass + pie(730). `first_move_anywhere` + `constraint=anywhere` (verified: 401 legal after P1's first move) → `adjacent_empty` is vestigial.

**Placement & capture.** **outnumber, threshold 2** — capture incidental to the influence race; clears isolated stones only in dense play.

**Propagation.** `influence`, radius 1, strength 1.0, **decay 0.7**. Self +1.0, neighbour +0.7.

**Win condition.** **threshold-race**, exceed **50.0** (NOT connection). `target_dimension_p2 = -1` ⇒ P2 mirrors P1's accumulator. komi_p2 = **0.05** (bias 0.065 per slate). max_turns 200. **50 on 400 active cells with decay 0.7 is a long grind** — most games run ~40+ plies toward the cap.

**Pie rule.** On (action 730).

**Degeneracy check.**
- `adjacent_empty` vestigial (verified).
- High GE variance (σ 0.085 ≈ 72% of mean 0.118) — the classic **lucky-seed inflation signature**; this game suffered the slate's largest deflation (−0.093) from its original single-seed rank-1.
- Komi 0.05 is tiny relative to a 50.0 target — verify whether pie/komi actually neutralizes seat bias.

**This is the explicit parameter-sibling of `e52e8889517a`.** Diff = two fields only: `threshold` 50 (here) vs 30, `max_turns` 200 (here) vs 100. Everything else identical. The contrast under test = **long race (50/200) vs short race (30/100)**, and whether the original rank-1 GE was real depth or inflation.

---

## Phase 2 — Strategic Play

Place id = cell; pass = 729; pie = 730. All engine-verified.

### Game 1 — Symmetric mirror race, long clock
Sequence: `0,80,9,71,1,79,18,62,2,78,11,69,19,61,20,60,81,141,83,143,99,159,101,161,162,242,164,233,180,240,182,224` (32 plies, 16 stones each).
Plot: At ply 32 P1 = +38.4, P2 = +39.85 (incl komi) — **neither has reached 50; the game grinds on.** This is the *identical* densest-blob packing as e52e, just continued for ~2× the moves to clear the higher bar. The extra length is more of the same packing, not a new strategic phase.
Reflection: The 50/200 parameterization adds **tedium, not depth** — the decision content per move is unchanged from the 30/100 sibling; there are simply more of the same decisions.

### Game 2 — Inflation probe (does it feel rank-1?)
I looked specifically for any medium-term structure the longer game might unlock (capture cycles, contested mid-board fronts, a second strategic gear). None appeared — the long race is decided on accumulator margin at the cap, and the margin is set by who packed more efficiently, exactly as in the short sibling. The original rank-1 GE was **inflation**, not depth: removing the lucky seed (the −0.093 deflation) matches the subjective experience of a shallow, swingy grind.

### Game 3 — Capture / pie / swinginess
Family-verified: outnumber-2 clears isolated stones only; pie swaps the opening. Because the race is long and decided on thin accumulator margins, small opening/seed differences swing the result — consistent with the high relative σ. komi 0.05 is too small to reliably balance a 50-target; pie does the real work, but the swinginess persists.

### Strategy guides
**P1:** pack densest contiguous region; settle in for a long grind to 50; protect your accumulator margin near the cap.
**P2:** swap a strong opening; otherwise mirror-pack and rely on komi + margin at the cap. Expect variance.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** One — densest-blob packing (single-seed strategic_diversity 1.0 does not survive as multiple deep plans in play).
**Counter-play.** Out-race or swap; none structural.
**Short-term vs long-term.** Horizon still ~3–4 moves; the long clock multiplies move count, not planning depth. Game ~40+ plies.
**Emergent concepts observed.** Clustering compounding, z-stacking, capture-on-isolated — same set as the pod.
**Does menger matter?** Routing puzzle only.
**Does the kernel matter?** decay 0.7 + threshold 50 = a slow grind; the high bar just delays resolution.
**Capture contribution.** Marginal.
**First-mover / seat balance.** Swingy. komi 0.05 is small relative to the 50 target; pie balances tempo but thin margins at the cap make outcomes variance-dominated — the deflation/inflation finding made tactile.

**Sibling verdict (vs e52e):** identical strategy; the long race is *worse* — more tedium, more variance, and it was the inflated rank-1 that did not survive 20-seed re-evaluation. The short-clock sibling (e52e) is the better-calibrated, more robust member of the pair.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Menger threshold-race family, decay 0.7, high bar (50), long clock.
(a)–(e) identical to the pod: numeric-territory race + near-inert outnumber capture on a fractal lattice; ~5 min expert transfer; not a named published game.

**Closest known-game analogue:** numeric-territory race on a fractal lattice (long-grind variant).
**Comparison to R8 (4.10):** thinner, and swingier.
**Comparison to R19/R20 best:** same family; the intra-family differentiator (50/200 vs 30/100) makes this the *weaker* sibling — the longer race exposes the inflation that its original rank-1 GE hid.

**Novelty score (post-adversary):** **2.8/10.** Re-parameterization of the menger threshold-race family, and a worse one (length ≠ novelty).

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game ID:** 1fea3357dca4
**Rules Summary:** The long-grind menger threshold-race: pack influence to +50 (decay 0.7) over ~40 plies. Identical strategy to its 30/100 sibling, stretched 2× — the slate's deflation poster child.
**Substrate:** menger, axis 9, 400/729, max_degree 6, pie_rule=True, komi_p2=0.05.
**Turn Structure:** alternating.
**Hybrid actions:** no.
**Soft violations flagged:** vestigial `adjacent_empty`; mirror-flag `target_dimension_p2=-1`; lucky-seed inflation signature (σ ≈ 72% of mean); komi 0.05 small vs a 50-target.

### Scores (1–10)
- **Strategic Depth: 3.3** — Same packing race as e52e but longer; the extra plies add tedium, not a strategic phase. 3–4-move horizon throughout.
- **Emergent Complexity: 3.0** — Identical to the pod; the long clock surfaces no new patterns.
- **Balance: 3.4** — Swingy: komi 0.05 too small for a 50-target, thin cap-margins make results variance-dominated; pie helps but doesn't tame the variance.
- **Novelty (post-adversary): 2.8** — A worse re-parameterization of the family.
- **Replayability: 3.0** — One optimum, long execution; replay value is low and the variance is noise, not depth.
- **Overall "Would an agent team play this again?": 3.3** — The inflation diagnosis is confirmed: it plays shallower (and longer, and swingier) than its original rank-1 GE implied. The weakest of the four menger games. Below R17 mean territory after accounting for tedium; well below R8 (4.10); does not clear 5.0.

### CLOSEST KNOWN-GAME ANALOG
Numeric-territory race on a fractal lattice; in-corpus the menger threshold-race pod (long-grind variant).

### KILLER FLAWS
- Length without depth — 50/200 is the same game as 30/100, just slower.
- Lucky-seed inflation: original rank-1 GE did not survive 20-seed re-evaluation (−0.093).
- Variance-dominated outcomes on thin cap-margins; komi too small to balance a 50-target.

### BEST QUALITY
As a *diagnostic* it is valuable — it cleanly demonstrates that GE rank can be inflated by seed luck and that raising the threshold buys move-count, not strategy. As a game, nothing distinguishes it favourably from its shorter sibling.

### menger STRUCTURAL CONTRIBUTION
Routing-puzzle floor only; the high threshold merely prolongs the same packing on the same shell.

### IMPROVEMENT IDEAS
**Single best change:** delete it in favour of the 30/100 sibling (e52e) — a longer race on identical rules adds no design value and reintroduces inflation/variance.
Secondary:
- If kept, raise komi materially (≈0.3–0.5) to match the 50-target and reduce variance-dominated finishes.
- As with the family, only a non-additive win condition would justify a longer game.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-2_game1fea3357dca4.md`.*
