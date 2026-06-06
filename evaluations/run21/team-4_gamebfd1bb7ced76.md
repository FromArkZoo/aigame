# Run 21 Agent-Team Eval — team-4 — Game bfd1bb7ced76

**Team ID:** team-4
**Game ID:** bfd1bb7ced76 (menger rank 5, 20-seed mean GE 0.126, σ 0.070, calibrated komi_p2 0.00)
**Substrate:** menger (axis 9, 400 active / 729 grid positions, max_degree 6, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game bfd1bb7ced76` (see `briefing_menger_bfd1bb7ced76.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Standard menger pod board: 9×9×9, 400 active / 729, max_degree 6, level-1 corner subcubes (20 cells), hollow interior.

**Turn structure.** Alternating, 1 piece/turn, P1 first. **Max_turns = 200** (never reached — see Phase 2).

**Action space.** 731 = 729 place + pass + pie (730). Place-only; `adjacent_empty` overridden by `first_move_anywhere`/`anywhere` (vestigial).

**Placement & capture.** outnumber, **threshold 2**; cleared to empty; anti-synergistic (pod-wide finding).

**Propagation.** influence, radius 1, strength 1.0, **decay 0.7**. Neighbor deposit 0.7 (verified in briefing: two adjacent friendlies = 3.4).

**Win condition.** threshold-race, **> 30.0**, `target_dimension_p2=-1` (P2 mirrors P1). komi_p2 = 0 (residual bias ≈ 0.060; pie is the balancer).

**Pie rule.** True (action 730).

**Degeneracy check.** Pod-standard: anti-synergistic capture; vestigial adjacency; live threshold + decay. The distinguishing slate fact is *reliability*: this is the only menger game flagged with **no zero-failure rerun mode** (cleanest PPO learner). The eval question: does "reliably learnable" ⇒ "deep"?

---

## Phase 2 — Strategic Play

All moves engine-verified. Place ids = cell indices; pass = 729; pie = 730.

### Game 1 — Symmetric corner race
Sequence: `0,60,1,61,2,62,9,69,11,71,18,78,19,79,20,80,81,141,83,143,99,159,101,161,162,222,163,...`
Plot: **P1 wins at step 25 (13 stones).** komi 0 ⇒ the one-tempo P1 lead is uncorrected; P1 led the whole symmetric race.
Reflection: ~25 plies, decay-0.7 pace, threshold 30 — essentially identical to e52e (24 plies) but with komi 0 so the first mover wins outright. The max_turns 200 cap is irrelevant (game ends at ply 25).

### Game 2 — Contest line
Sequence: `0,1,2,9,18,11,20,19,...`
Plot: Pod behavior — outnumber captures fire under co-occupation, both accumulators collapse.
Reflection: No counterplay; interaction is self-harming, identical to the rest of the pod.

### Game 3 — Pie / opening
Sequence: `0,730`.
Plot: Swap transfers the opening; with komi 0 the pie is the only balancer, and because the opening is non-committal (interchangeable corners), the residual ~0.060 P1 bias largely persists.
Reflection: "Reliable learner" reflects training stability (low σ 0.070, no zero-mode), not a deeper game — PPO reliably converges to the same shallow corner-pack.

### Strategy guides
**P1:** Corner-pack contiguously; win on tempo (komi 0 helps P1).
**P2:** Mirror in a separate corner; swap to claw the tempo back, but expect a small residual P1 edge.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** No — single corner-pack plan.
**Counter-play.** Absent/self-harming.
**Short-term vs long-term.** ~25-ply game; max_turns 200 is dead weight. No medium-term planning.
**Emergent concepts observed.** Capture-poisoning (negative); clustering-compounds (rule restatement). Engine non_triviality/diversity = 1.0 here are single-eval metric artifacts — subjectively the play is as monotone as the rest of the pod.
**Does menger matter?** No — one corner subcube.
**Does the propagation kernel matter?** decay 0.7 sets pace; no structural role.
**Capture-rule contribution.** Net negative.
**First-mover advantage / seat balance.** komi 0 ⇒ P1 won my symmetric race; residual bias ≈ 0.060, pie weak. Slightly worse seat balance than e52e (which over-corrects to P2).
**Reliability ↔ quality?** **No.** Its crown stat (cleanest learner, lowest σ) means PPO reliably finds the same shallow optimum. Reliability is a property of the *training*, not the *game*.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Same as the pod: influence-area accumulation to a target, anti-synergistic outnumber, decorative fractal.
(a) Threshold-race = area/influence scoring (Tumbleweed-like).
(b) outnumber-2 → custodial-by-count, a liability here.
(c) Reliability is not a novelty axis — same mechanic set as e52e/1fea.
(d) Substrate decorative.
(e) Expert-transfer <3 min.

**Closest known-game analogue:** influence-area race; within corpus, the decay-0.7 menger threshold-race (sibling to e52e, longer-cap variant).
**Comparison to R8 (4.10):** far thinner.
**Comparison to R19/R20 best:** at/below R20 production 3.73.

**Novelty score (post-adversary):** **3.0/10.** Reliability does not lift novelty; same family.

---

## Phase 5 — Verdict

**Team ID:** team-4
**Game ID:** bfd1bb7ced76
**Rules Summary:** The most reliably-trainable member of the menger pack-a-corner family (lowest σ, no zero-mode) — but reliability buys a consistently shallow corner-pack sprint, not depth.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=True, komi_p2=0.00.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** anti-synergistic capture; vestigial adjacency; max_turns 200 dead (games end ~ply 25); residual P1 bias 0.060 at komi 0.

### Scores (1–10)
- **Strategic Depth: 3.4** — Single corner-pack plan, ~25-ply game. Reliable convergence to a shallow optimum.
- **Emergent Complexity: 3.2** — Same negative capture-poisoning; single-eval non_triviality/diversity 1.0 are metric artifacts, not felt.
- **Balance: 4.0** — komi 0 ⇒ P1 won my symmetric race; residual 0.060; pie weak. Slightly behind e52e on balance.
- **Novelty (post-adversary): 3.0** — Reliability ≠ novelty; same influence-area family.
- **Replayability: 3.3** — Converges identically every game (that is the point — and the problem).
- **Overall "Would an agent team play this again?": 3.4** — At/under R20 production (3.73), below R8 (4.10). The "stability ↔ quality" hypothesis fails here: it is the most stable *because* it is the most monotone.

### CLOSEST KNOWN-GAME ANALOG
Influence-area race; within corpus, a longer-cap decay-0.7 menger threshold-race, sibling-adjacent to e52e.

### KILLER FLAWS
- Reliability is training-side, not game-side — it reliably learns a shallow game.
- Anti-synergistic capture; no counterplay; one dominant plan.
- max_turns 200 is dead weight (games end by ply 25).

### BEST QUALITY
Lowest-variance learner in the pod — useful as an *experimental control*, not as a game.

### MENGER STRUCTURAL CONTRIBUTION
Decorative; one corner subcube carries play.

### IMPROVEMENT IDEAS
**Single best change:** Fix capture to remove deposited influence (pod-wide fix) so interaction matters — reliability would then reflect a deeper learned policy rather than a trivial optimum.
Secondary:
- Drop max_turns to ~60; the 200 cap is meaningless.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-4_gamebfd1bb7ced76.md`.*
