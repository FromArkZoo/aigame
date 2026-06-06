# Run 21 Agent-Team Eval — team-5 — Game bfd1bb7ced76

**Team ID:** team-5
**Game ID:** bfd1bb7ced76 (menger rank 5 by 20-seed mean GE 0.126, σ 0.070, calibrated komi_p2 0.00)
**Substrate:** menger (axis 9, 400 active / 729, max_degree 6, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game bfd1bb7ced76` (see `briefing_menger_bfd1bb7ced76.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Same Menger sponge as the pod: 400/729 active, `c=z*81+y*9+x`, max_degree 6, holes throughout.

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = **200**.

**Action space.** 731 (729 + pass + pie 730). Placement anywhere-empty (`adjacent_empty` vestigial).

**Placement & capture.** **outnumber, threshold 2.** Verified live: P1 on cells 1 + 9 (both adjacent to P2's cell 0) cleared the lone P2 stone (outnumber by 2). Captures clear to empty.

**Propagation.** influence, radius 1, strength 1.0, **decay 0.7** (self +1.0, neighbour +0.7). Verified: two adjacent friendly stones scored +3.4 = 2×1.0 + 2×0.7.

**Win condition.** **threshold-race**, target **30.0**, `target_dimension_p2=-1` (mirror). **Komi = 0.05? No — komi_p2 = 0.00 here**, so multiplicative komi = 0 × 30 = 0. No P2 bonus. Timeout (max_turns 200) → piece-count majority.

**Pie rule.** True (id 730).

**Pod placement.** Same decay/threshold as `e52e` (decay 0.7, threshold 30) but **max_turns 200 (vs 100) and komi 0 (vs 0.05)**. The flagged differentiator is **reliability**: this is the only menger game with no zero-failure rerun mode (the cleanest PPO learner). The eval question is whether "reliably learnable" ↔ "deep."

**Degeneracy check.** `adjacent_empty` vestigial; komi 0 is real (gate said post-pie bias already < 0.10, residual ≈ 0.060, so pie is the only balancer); threshold/decay live.

---

## Phase 2 — Strategic Play

### Game 1 — Mirror compact-cluster race
Sequence: `0,6,1,7,2,8,9,15,11,17,18,24,19,25,20,26,27,33,28,34,29,35,36` (P1 wins ply 23).
Plot: P1 packs (x0–2), P2 mirrors (x6–8). decay-0.7 compounding (+2.4 to +3.8/stone). **Engine: P1 crosses 30 first at ply 23 (raw +31.6 vs P2 +29.2), Winner=1.** With **komi 0, the one-tempo P1 lead is decisive** — unlike `e52e` where komi 1.5 flips it to P2. Slightly slower than `e52e` (23 vs 22 plies) — noise, same dynamics.
Reflection: this game is `e52e` minus the komi balancer. The shared accumulator + first-mover = P1 win.

### Game 2 — Capture probe
Sequence: `1,0,9,2` — P1 at (1,0,0) and (0,1,0) both border P2's (0,0,0); P1's second stone **captured P2's corner** (cleared). Symmetric to the e52e capture: outnumber-2 fires, cost 2 plies, removes 1 stone + its influence.

### Game 3 — Pie swap
Sequence: `20,730,11` — P2 swap takes P1's stone; with komi 0, the swap is the **only** balancing lever, and it cleanly transfers first-mover tempo. After swap the position is symmetric with P2 +1, P1 to move.

### Strategy guides
**P1:** Pack the densest contiguous region; with komi 0 your one-tempo lead wins the mirror outright (~23 plies). No need to fight.
**P2:** You cannot win a clean mirror (komi 0). **Swap (pie) to take the tempo**, then pack symmetrically — that is your only equaliser. Captures are tempo-negative.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** DB strategic_diversity 1.000 and non_triviality 1.000 are the highest in the pod, but subjectively play still converges on densest-packing; the "diversity" is among roughly-equivalent dense regions, not strategically distinct plans.
**Counter-play.** Captures fire; pie equalises tempo. But with komi 0, an even race favours the mover, so P2's real counter is the swap, not in-board play.
**Short-term vs long-term.** ~23-ply horizon; the longer max_turns (200) is almost never reached because the race resolves fast.
**Emergent concepts.** Compounding clusters, outnumber captures, pie-tempo equalisation. Same palette as the pod.
**Does menger matter?** Hole-navigation + z-stacking; no new axis.
**Does the kernel matter?** decay 0.7 gives the same mild gradient as `e52e`.
**Capture contribution.** Real (verified) but tempo-costly; situational.
**Seat balance.** **Weaker than `e52e`.** komi 0 means a clean mirror is a P1 win; balance rests entirely on the pie swap (residual bias 0.060). The "reliable learner" property is about PPO convergence, not seat fairness.

**Reliability ↔ depth?** My read: **no.** This game's reliability (no zero-failure mode, σ 0.070) comes from a *clean, low-variance dominant strategy* (pack densest blob) — exactly what makes it learnable also caps its depth. Stable because simple, not stable because rich.

---

## Phase 4 — Novelty Adversary

**Adversary case.** Decay-0.7 influence-race on a sponge with outnumber-2 capture — the R20-champion family, minus komi.
(a) area/score race. (b) Ataxx/Tafl capture. (c) standard family combination. (d) sponge = packing navigation. (e) expert-transfer ~5 min.
**Closest analogue:** the same R20 decay-0.7 menger race as `e52e`; this is essentially `e52e` with komi removed and a longer (unused) clock.
**Comparison to R8 (4.10):** different family, comparable level.
**Comparison to R19/R20:** ≈ R20 production; thinner than R19 menger 4.8.

**Novelty score (post-adversary):** 3.0/10. Standard family member; its distinguishing trait (learnability) is a *training* property, not a novelty.

---

## Phase 5 — Verdict

**Team ID:** team-5
**Game ID:** bfd1bb7ced76
**Rules Summary:** A decay-0.7 influence-packing race to +30 on a Menger sponge with no komi — the cleanest, most reliably-learnable menger game, but reliability comes from a simple dominant packing strategy, and with komi 0 the first mover wins the clean mirror.
**Substrate:** menger, axis 9, 400/729, max_degree 6, pie_rule=True, komi_p2=0.00.
**Turn Structure:** alternating. **Hybrid actions:** no.
**Soft violations flagged:** `adjacent_empty` vestigial; komi 0 (pie is the sole balancer); max_turns 200 effectively unused (race resolves ~23 plies).

### Scores (1–10)
- **Strategic Depth: 3.5** — packing race with mild gradient; DB diversity 1.0 overstates subjective variety (dense regions are near-equivalent).
- **Emergent Complexity: 3.0** — compounding + captures + pie-tempo; nothing multi-step.
- **Balance: 3.0** — komi 0 ⇒ clean mirror is a P1 win; balance hangs on the pie swap (residual bias 0.060). Weaker than `e52e`.
- **Novelty (post-adversary): 3.0** — standard family member; "reliable learner" is a training trait.
- **Replayability: 3.5** — diversity 1.0 gives some opening spread, but plans converge.
- **Overall: 3.5** — clean and learnable but shallow; its stability reflects a simple dominant strategy, not depth. Between R17 (3.5) and R20 (3.73); below the R19 ceiling.

### CLOSEST KNOWN-GAME ANALOG
`e52e` without komi — a decay-0.7 Ataxx-flavoured area race on menger.

### KILLER FLAWS
- **Stability is from simplicity, not depth** — the low-variance dominant packing line that makes it learnable also caps its ceiling.
- **komi 0 leaves the clean mirror a P1 win**; only the pie swap balances it.

### BEST QUALITY
The most *robust* member of the pod — PPO converges reliably and the game never collapses into a degenerate failure mode. As a controlled baseline it is valuable; as a game it is the pod's median.

### MENGER STRUCTURAL CONTRIBUTION
Same as the pod: navigation + z-stacking, no new strategic axis.

### IMPROVEMENT IDEAS
**Single best change:** add the multiplicative komi its sibling uses (≈1.5) to fix the komi-0 seat bias without changing the (reliable) core. The reliability is worth preserving; the balance is the fixable weakness.
Secondary: the answer to "does reliability ↔ depth" is no — fitness should not reward learnability as a proxy for quality; pair GE with an explicit balance/diversity gate.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-5_gamebfd1bb7ced76.md`.*
