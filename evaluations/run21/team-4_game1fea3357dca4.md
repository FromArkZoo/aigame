# Run 21 Agent-Team Eval — team-4 — Game 1fea3357dca4

**Team ID:** team-4
**Game ID:** 1fea3357dca4 (menger original rank 1 → fell to rank 6 under 20-seed, 20-seed mean GE 0.118, σ 0.085, calibrated komi_p2 0.05)
**Substrate:** menger (axis 9, 400 active / 729 grid positions, max_degree 6, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game 1fea3357dca4` (see `briefing_menger_1fea3357dca4.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Standard menger pod board: 9×9×9, 400 active / 729, max_degree 6, level-1 corner subcubes, hollow interior.

**Turn structure.** Alternating, 1 piece/turn, P1 first. **Max_turns = 200.**

**Action space.** 731 = 729 place + pass + pie (730). Place-only; `adjacent_empty` vestigial (401 legal after P1's first move — verified anywhere-empty).

**Placement & capture.** outnumber, **threshold 2**; cleared to empty; anti-synergistic (pod-wide).

**Propagation.** influence, radius 1, strength 1.0, **decay 0.7**.

**Win condition.** threshold-race, **> 50.0** (≠ siblings' 30), `target_dimension_p2=-1` (P2 mirrors P1). komi_p2 = 0.05.

**Pie rule.** True (action 730).

**Degeneracy check.** Pod-standard. The distinguishing facts: highest threshold (50) ⇒ longest grind; **largest deflation in the slate (−0.093)** under 20-seed re-eval, σ ≈ 72% of mean — the classic "GE optimizer found a lucky seed" signature. The eval question: does it feel as deep as its original rank-1 GE, or shallow once the lucky seed is removed?

**Sibling note.** Parameter-sibling of `e52e8889517a`: identical except **threshold 50 / max_turns 200 (this)** vs **30 / 100 (sibling)**. I score the **longer-race** differentiator only.

---

## Phase 2 — Strategic Play

All moves engine-verified. Place ids = cell indices; pass = 729; pie = 730.

### Game 1 — Symmetric corner race (long grind)
Sequence: `0,60,1,61,2,62,9,69,11,71,18,78,19,79,20,80,81,141,83,143,99,159,101,161,162,222,163,223,164,224,171,231,173,233,180,240,181,241`
Plot: **P2 wins at step 38 (19 stones each).** Threshold 50 takes ~19 stones/side — nearly double the sibling's 12. komi 0.05 over-corrects, P2 edges it.
Reflection: The entire difference from e52e is *more of the same packing*. ~38 plies of identical corner-fill. The longer grind gives PPO more room to overfit a lucky packing line — consistent with the −0.093 deflation and high relative σ.

### Game 2 — Contest line
Sequence: `0,1,2,9,18,11,20,19,...`
Plot: Pod behavior — captures fire, both accumulators collapse.
Reflection: The longer race means MORE opportunity for capture interaction, but since interaction is self-harming, that "opportunity" is never taken in rational play.

### Game 3 — Pie / opening
Sequence: `0,730`.
Plot: Swap transfers the opening; non-committal as in the pod; komi 0.05 over-balances toward P2.
Reflection: Over a 38-ply grind the one-tempo edge is even less decisive; balance rests on komi overcorrection.

### Strategy guides
**P1:** Corner-pack; commit to nothing early; out-pack on tempo (here komi cancels it).
**P2:** Mirror; komi 0.05 makes a pure copy slightly winning.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** No — single corner-pack plan, stretched to 38 plies.
**Counter-play.** Absent/self-harming.
**Short-term vs long-term.** Long (38 plies) but *flat* — every ply is the same packing decision; no medium-term plan emerges. Length without depth.
**Emergent concepts observed.** Capture-poisoning (negative); clustering-compounds (rule restatement).
**Does menger matter?** No — one corner subcube; though the higher threshold (50) forces packing a *second* region after a corner fills (~20 active cells), the second region is just another corner — same decision repeated.
**Does the propagation kernel matter?** decay 0.7 + threshold 50 only lengthens the sprint; no structural role.
**Capture-rule contribution.** Net negative.
**First-mover advantage / seat balance.** komi 0.05 over-corrects (P2 won my symmetric race); balance by overcorrection.
**Deflation diagnosis confirmed.** Subjectively this is the shallowest-*feeling* menger game — a long, monotone fill. Its original rank-1 GE was a lucky-seed inflation; agent play does NOT find rank-1 depth. **Strong GE-vs-eval disagreement in the deflation direction.**

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Same as the pod: influence-area accumulation to a (higher) target, anti-synergistic outnumber, decorative fractal.
(a) Threshold-race = area/influence scoring (Tumbleweed-like), longer target.
(b) outnumber-2 → custodial-by-count, a liability.
(c) Threshold 50/200 is a parameter, not a new mechanic.
(d) Substrate decorative.
(e) Expert-transfer <3 min.

**Closest known-game analogue:** influence-area race to a high target; within corpus, the long-grind decay-0.7 menger threshold-race (sibling to e52e).
**Comparison to R8 (4.10):** far thinner.
**Comparison to R19/R20 best:** below R20 production 3.73 in felt depth.

**Novelty score (post-adversary):** **2.8/10.** Lowest in the menger pod — a higher threshold adds grind, not novelty.

---

## Phase 5 — Verdict

**Team ID:** team-4
**Game ID:** 1fea3357dca4
**Rules Summary:** The long-grind (threshold 50, 200-turn) sibling of the menger pack-a-corner family — twice the plies, identical decisions, and the slate's clearest case of lucky-seed GE inflation deflating under honest play.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=True, komi_p2=0.05.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** anti-synergistic capture; vestigial adjacency; balance by komi overcorrection; lucky-seed GE inflation (−0.093 deflation) confirmed in play.

### Scores (1–10)
- **Strategic Depth: 3.2** — Single corner-pack plan stretched to ~38 plies; length without branching. Original single-seed depth 0.485 overstates felt depth.
- **Emergent Complexity: 3.0** — Same negative capture-poisoning; nothing the higher threshold adds.
- **Balance: 4.0** — komi 0.05 over-corrects (P2 won my symmetric race); balance by coincidence.
- **Novelty (post-adversary): 2.8** — Higher threshold = grind, not novelty; lowest in pod.
- **Replayability: 3.0** — Long, monotone, converges to corner-pack; the grind discourages replay.
- **Overall "Would an agent team play this again?": 3.2** — Lowest of the menger pod, below R20 production (3.73) and R8 (4.10). **Confirms the inflation diagnosis: the original rank-1 GE was lucky-seed; agent judgment ranks it last.**

### CLOSEST KNOWN-GAME ANALOG
Influence-area race to a high target; within corpus, the long-grind decay-0.7 menger threshold-race (sibling of e52e).

### KILLER FLAWS
- Length without depth — 38 plies of the identical packing decision.
- Anti-synergistic capture; no counterplay.
- Lucky-seed GE inflation (the −0.093 deflation is real; agent play sees through it).

### BEST QUALITY
None distinctive — it is the sibling pair's "more grind" arm; the shorter sibling (e52e) is strictly preferable.

### MENGER STRUCTURAL CONTRIBUTION
Decorative; the higher threshold forces packing a second corner, but a second corner is the same decision repeated.

### IMPROVEMENT IDEAS
**Single best change:** Drop the threshold/cap to the sibling's 30/100 (or fix capture, pod-wide). The 50/200 tuning strictly adds grind and seed variance with no depth payoff.
Secondary:
- Retire this arm of the sibling pair; keep e52e (G2 dedup gives the family a single representative anyway).

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-4_game1fea3357dca4.md`.*
