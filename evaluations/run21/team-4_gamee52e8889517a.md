# Run 21 Agent-Team Eval — team-4 — Game e52e8889517a

**Team ID:** team-4
**Game ID:** e52e8889517a (menger rank 3, 20-seed mean GE 0.138, σ 0.090, calibrated komi_p2 0.05)
**Substrate:** menger (axis 9, 400 active / 729 grid positions, max_degree 6, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game e52e8889517a` (see `briefing_menger_e52e8889517a.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Identical menger sponge to the rest of the menger pod: 9×9×9, 400 active / 729, max_degree 6, level-1 corner subcubes (20 active each), hollow interior.

**Turn structure.** Alternating, 1 piece/turn, P1 first. **Max_turns = 100.**

**Action space.** 731 = 729 place + pass + pie (730). Place-only; `adjacent_empty` vestigial (397 legal after 4 moves).

**Placement & capture.** outnumber, **threshold 2** — stone cleared when outnumbered by ≥2. Same anti-synergistic clearing as the pod (verified in e1453: capturing leaves stale negative influence).

**Propagation.** influence, radius 1, strength 1.0, **decay 0.7** (≠ e1453's 1.0). Neighbor deposit = 0.7, so contiguous clustering compounds at ~+2.5–3/stone — slightly slower than e1453.

**Win condition.** threshold-race, **> 30.0**, `target_dimension_p2=-1` (P2 mirrors P1's accumulator). komi_p2 = 0.05 (bias +0.015).

**Pie rule.** True (action 730).

**Degeneracy check.** Same as pod: capture anti-synergistic; `adjacent_empty` vestigial; `target_dimension_p2=-1` is a mirror flag, not a second objective. Threshold-race dispatch correct.

**Sibling note (the job here).** This is the deliberate parameter-sibling of `1fea3357dca4`. Structural diff is exactly two fields: **threshold 30 (this) vs 50 (sibling)** and **max_turns 100 (this) vs 200 (sibling)**. Capture, decay 0.7, topology, pie, komi are identical. I score the **shorter-race** differentiator only.

---

## Phase 2 — Strategic Play

All moves engine-verified. Place ids = cell indices; pass = 729; pie = 730.

### Game 1 — Symmetric corner race (decay-0.7 calibration)
Sequence: `0,60,1,61,2,62,9,69,11,71,18,78,19,79,20,80,81,141,83,143,99,159,101,161,...`
Plot: P2 (mirroring in the far corner) **wins at step 24 (12 stones each)**. With komi 0.05 added, the second mover edges ahead — the komi slightly *overcorrects* the one-tempo P1 lead.
Reflection: ~24 plies / 12 stones to reach 30 at decay 0.7 — three plies slower than e1453's decay-1.0 sprint (21 plies). The race is marginally longer but the plan is identical: pack a corner subcube.

### Game 2 — Contest line (co-occupation)
Sequence: `0,1,2,9,18,11,20,19,...` (both into origin subcube).
Plot: Same family behavior as e1453 — outnumber captures fire, both accumulators collapse toward zero.
Reflection: Contesting remains mutually destructive; the longer decay-0.7 race does not change that interaction is self-harming.

### Game 3 — Pie / opening-balance
Sequence: `0,730`.
Plot: Swap transfers P1's opening to P2. As in the pod, the opening is non-committal (any corner equivalent), so pie has little to bite; here the small komi 0.05 already over-balances toward P2.
Reflection: Between komi 0.05 and pie, P2 is actually slightly favored in the pure symmetric race (Game 1) — the cleanest-balanced of the menger pod, but balance is achieved by overcorrection, not by depth.

### Strategy guides
**P1:** Pack a corner subcube contiguously; do not interact. Accept that komi 0.05 nearly erases the tempo edge.
**P2:** Build your own corner; the komi + mirror makes a pure copy slightly winning. Swap only if P1 opens unusually strong (rare given interchangeable corners).

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** No — single dominant plan (corner pack), as in the whole menger pod.
**Counter-play.** Absent/self-harming (co-occupation craters both scores).
**Short-term vs long-term.** ~24-ply game; no medium-term plan develops. Slightly more room than e1453's 21 plies but the extra plies are identical packing.
**Emergent concepts observed.** Capture-poisoning (negative); clustering-compounds (rule restatement). Nothing new vs e1453.
**Does menger matter?** No more than the pod — play uses one corner subcube.
**Does the propagation kernel matter?** decay 0.7 vs e1453's 1.0 only changes *speed* (24 vs 21 plies). It does not add structure. This is the core sibling/family finding: tuning decay/threshold rescales the sprint length, not its depth.
**Capture-rule contribution.** Net negative, as pod.
**First-mover advantage / seat balance.** Best-balanced of the pod: komi 0.05 over-corrects so P2 narrowly won my symmetric race. "Balanced" here = a lucky cancellation of two flaws (P1 tempo vs komi), not robustness.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Identical to e1453: influence-area accumulation to a fixed target with an anti-synergistic outnumber bolt-on, on a decorative fractal.
(a) Threshold-race = area/influence scoring to a target (Tumbleweed-like).
(b) outnumber-2 → custodial-by-count (Ataxx/Tafl) but a liability here.
(c) The shorter-race tuning (30/100) vs the sibling's (50/200) is a *parameter*, not a new mechanic — no published-game distinction.
(d) Fractal substrate decorative.
(e) Expert-transfer <3 min.

**Closest known-game analogue:** influence-area race; within corpus, a decay-0.7 R20-style menger threshold-race (the "standard" form, vs e1453's decay-1.0 variant).
**Comparison to R8 Connection Go (4.10):** far thinner (no global topology, no interaction).
**Comparison to R19/R20 best:** at/below R20 production 3.73; thinner than R19 menger top 4.8.

**Novelty score (post-adversary):** **3.0/10.** The 30/100 tuning is not a novelty axis; same family verdict as e1453.

---

## Phase 5 — Verdict

**Team ID:** team-4
**Game ID:** e52e8889517a
**Rules Summary:** The decay-0.7 / short-race (threshold 30, 100-turn) member of the menger pack-a-corner family; identical play to its siblings, a few plies longer than the decay-1.0 top game, and the best-balanced by accidental komi overcorrection.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=True, komi_p2=0.05.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** capture anti-synergistic; `adjacent_empty` vestigial; balance via komi overcorrection not depth; ~395 active cells unused.

### Scores (1–10)
- **Strategic Depth: 3.3** — Single dominant plan, ~24-ply game; the extra plies vs e1453 are identical packing, not added depth.
- **Emergent Complexity: 3.0** — Same negative capture-poisoning emergent property; nothing the family doesn't already have.
- **Balance: 4.2** — Best of the menger pod: komi 0.05 over-corrects so P2 won my symmetric race. But it is a cancellation of two flaws, not robust balance.
- **Novelty (post-adversary): 3.0** — Influence-area re-skin; the 30/100 tuning is a parameter, not a new mechanic.
- **Replayability: 3.2** — Converges to corner-pack; interchangeable openings.
- **Overall "Would an agent team play this again?": 3.3** — At/under R20 production (3.73), below R8 (4.10). The shorter race is marginally more seed-robust than its 50/200 sibling but no deeper.

### CLOSEST KNOWN-GAME ANALOG
Influence-area race to a fixed target; within corpus, the "standard" decay-0.7 menger threshold-race (vs e1453's decay-1.0 variant and 1fea's longer-race variant).

### KILLER FLAWS
- Same anti-synergistic capture as the pod (capturing zeroes your accumulator).
- No counterplay; play collapses to two non-interacting corner builds.
- The only differentiator vs siblings is race length — a parameter, not depth.

### BEST QUALITY
Cleanest seat balance in the menger pod (komi 0.05 ≈ cancels the P1 tempo edge) — but achieved by coincidence, not design.

### MENGER STRUCTURAL CONTRIBUTION
Decorative, identical to the pod: one corner subcube carries the whole game.

### IMPROVEMENT IDEAS
**Single best change:** Same as e1453 — make captures remove deposited influence so interaction becomes a real lever. Without it the 30/100 vs 50/200 sibling axis is just sprint-length tuning.
Secondary:
- If kept, prefer this 30/100 tuning over the 50/200 sibling — shorter race = less degenerate grinding and lower seed variance.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-4_gamee52e8889517a.md`.*
