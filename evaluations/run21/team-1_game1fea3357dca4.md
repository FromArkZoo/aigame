# Run 21 Agent-Team Eval — team-1 — Game 1fea3357dca4

**Team ID:** team-1
**Game ID:** 1fea3357dca4 (menger **original rank 1 → rank 6** after 20-seed finalization, largest deflation Δ −0.093; 20-seed mean GE 0.118, σ 0.085, calibrated komi_p2 0.05)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game 1fea3357dca4` (see `briefing_menger_1fea3357dca4.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Same Menger sponge (9×9×9, 400/729 active, dense carpet faces). Cell = z·81 + y·9 + x.

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = **200**.

**Action space.** 731 actions (729 place + pass + pie 730). Place-only; `adjacent_empty` vestigial (401 legal after P1's first move — confirmed live in briefing).

**Placement & capture.** **outnumber-2** (identical to the rest of the pod). Isolated stones cleared at 2-to-0 enemy neighbors; interior cluster stones immune.

**Propagation.** influence, radius 1, strength 1.0, **decay 0.7**.

**Win condition.** threshold-race. Effective owned-influence > **50.0** (the high bar — the long-grind variant). `target_dimension_p2=-1` mirror. **Komi = komi_p2 × threshold = 0.05 × 50 = 2.5** (helper under-displays as 0.05).

**Pie rule.** True (action 730).

**Sibling identity (the scored differentiator).** This is the **longer-race sibling of e52e8889517a** — verified earlier by flattened-blob diff: the *only* differences are `threshold` 50 (vs 30) and `max_turns` 200 (vs 100). decay-0.7 propagation, outnumber-2, topology, pie, komi_p2=0.05 are identical. So the entire experimental contrast is **long grind (50/200) vs short race (30/100)**.

**Degeneracy check.** Helper komi under-display (true komi 2.5); `adjacent_empty` vestigial; mirror flag; high σ (0.085 ≈ 72% of mean) is the lucky-seed-inflation signature flagged in the briefing.

---

## Phase 2 — Strategic Play

All moves engine-verified. Place ids = cell indices; pass = 729; pie = 730.

### Game 1 — P1 packs left vs P2 packs right (uncontested mirror) — **komi flips it to P2**
Sequence: `0,6,1,7,2,8,9,15,11,17,18,24,19,25,20,26,27,33,28,34,29,35,36,42,38,44,45,51,46,52,47,53,54,60,55,61,56,62,63,69,65,71,72,78,73,79,74,80` (36 plies to resolution, **18 stones each**).
Plot: identical lockstep to e52 but stretched — P1 ~3.8 ahead the whole way. Ply 35 P1 raw 48.8 (< 50, no cross). Ply 36 P2 reaches raw 48.8; **+2.5 komi → 51.3 > 50 → Done, Winner=2.** Same komi-decides-the-mirror outcome as e52, just after twice as many stones.
Reflection: the higher threshold does nothing structural — it only makes the *same* packing race take ~36 plies instead of ~22. More stones, more board filled, no new decision type.

### Game 2 — Capture-contest
Sequence: `2,1,72,3`.
Plot: outnumber-2 clears P1's isolated (2,0,0) — same deterrent; two-for-one tempo cost; irrelevant against packing.

### Game 3 — Pie-swap balance
Sequence: `0,730,...`.
Plot: swap hands P1's opener and tempo to P2; combined with the 2.5 komi it over-balances the perfect mirror toward P2 (matching the calibration that this game still needs komi to balance).

### Strategy guides
**P1:** pack the densest face compactly and try to reach 50 before komi tips an equal-raw P2 over (you must out-tempo by > 2.5).
**P2:** mirror-pack — the 2.5 komi wins you the equal race; capture only if P1 scatters; swap only against a uniquely strong opener.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** One (compact packing) + binary swap — same as the whole pod. DB strategic_diversity 1.0 is single-seed and not seen in play.
**Counter-play.** Partial (komi/swap balance seats; capture can't beat packing).
**Short-term vs long-term.** The longest of the pod (~36 plies) but **not deeper** — the extra length is repetition, not horizon. ~4-ply lookahead still suffices at every step.
**Emergent concepts observed.** Contiguity-as-armor; komi-as-tiebreak. Same set, stretched out.
**Does menger matter?** No more than the pod.
**Does the propagation kernel matter?** It's the win metric (decay 0.7).
**Capture contribution.** Deterrent only.
**First-mover advantage / seat balance.** Komi 2.5 balances (and slightly over-balances) the mirror; the **longer race amplifies seed variance** — exactly why this game deflated most under 20-seed re-evaluation. The original rank-1 GE was a lucky-seed artifact; the deeper-feel that ranking implied is **not present** subjectively.

**Inflation diagnosis (the briefing's question), answered.** The game does **not** feel as deep as its original rank-1 GE implied. It is the same packing race as its short sibling, just longer and noisier. The −0.093 deflation is consistent with "GE optimizer found a lucky seed on a longer, higher-variance grind," not with genuine depth being averaged away.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Same family: influence packing race + flanking capture on a fractal (Go-area sprint + Ataxx capture; ~5-min expert transfer; substrate restricts not innovates).
**Intra-family differentiator (the job):** longer grind (50/200) vs e52's short race (30/100). The contrast yields *worse* properties — more tedium, higher variance, the largest deflation — with no added depth. Length is not a novelty.
**Closest known-game analogue:** Go-area packing race with Ataxx capture.
**Comparison to R8 (4.10):** thinner; no counter-strategy.
**Comparison to R19/R20:** same family as R19 menger top (4.8); the long-grind parameterization, which the data shows is the weakest of the menger pod once seed luck is removed.

**Novelty score (post-adversary): 3.5/10.** No new mechanic; the only intra-family difference (a longer race) makes it noisier, not novel.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game ID:** 1fea3357dca4
**Rules Summary:** The long-grind version of the Menger packing race — first to 50 own-influence points (decay 0.7), outnumber-2 deterrent capture, 2.5 komi balancing the mirror. Identical strategy to its 30/100 sibling but ~36 plies long and the highest-variance, most-deflated game in the menger pod.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=True, komi_p2=0.05 (effective 2.5).
**Turn Structure:** alternating, 1 piece/turn.
**Hybrid actions:** no.
**Soft violations flagged:** helper komi under-display (true 2.5); high-σ lucky-seed signature; vestigial `adjacent_empty`.

### Scores (1–10)
- **Strategic Depth: 3.5** — same one-plan packing race, just longer; the extra length is repetition. DB strategic_depth 0.485 is the lowest in the pod and matches the felt shallowness.
- **Emergent Complexity: 3.5** — contiguity-as-armor + komi tiebreak; nothing new.
- **Balance: 4.5** — the 2.5 komi balances/over-balances the mirror; seat balance is fine (this is the one dimension where it ties e52).
- **Novelty (post-adversary): 3.5** — same family; length is not novelty.
- **Replayability: 3** — converges to packing and the longer race makes each game more of the same; highest variance means *outcomes* differ by seed luck, not by interesting play.
- **Overall "Would an agent team play this again?": 3.7** — A long, balanced, but tedious packing race; the weakest menger entry once lucky-seed inflation is removed. Right at the R20 production mean (3.73), below R8 (4.10) and R19 menger top (4.8). The inflation diagnosis is confirmed: it is not as deep as its original rank-1 GE.

### CLOSEST KNOWN-GAME ANALOG
Go-area packing race + Ataxx flanking capture; inside the corpus, the long-grind sibling of e52e8889517a.

### KILLER FLAWS
- **Longer ≠ deeper** — the high threshold adds grind and variance, no new decisions.
- Highest-variance / most-deflated game in the slate (lucky-seed inflation confirmed).
- One dominant strategy; score-max and safety coincide.

### BEST QUALITY
Seat balance via the 2.5 komi is genuine; otherwise it inherits only the pod's contiguity-as-armor.

### MENGER STRUCTURAL CONTRIBUTION
Same as pod: restriction not enrichment; flattens to carpet.

### IMPROVEMENT IDEAS
**Single best change:** lower the threshold back to the short-race value (the long grind only adds variance) — i.e. prefer the e52 parameterization. Better still, break the score/safety coincidence so the extra stones create real contest instead of repetition.
Secondary:
- If a longer game is wanted, add a mechanic that *uses* the extra length (territory decay, recapture cycles) rather than just raising the bar.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-1_game1fea3357dca4.md`.*
