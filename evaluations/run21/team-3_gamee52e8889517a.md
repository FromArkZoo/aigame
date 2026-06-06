# Run 21 Agent-Team Eval — team-3 — Game e52e8889517a

**Team ID:** team-3
**Game ID:** e52e8889517a (menger slate rank-3, 20-seed mean GE 0.138, σ 0.090, calibrated komi_p2 0.05)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game e52e8889517a` (see `briefing_menger_e52e8889517a.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Same Menger sponge as the slate (400/729, max_degree 6, holes break neighbourhoods). Cell index `c = z*81 + y*9 + x`.

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = **100**.

**Action space.** 731 = 729 place + pass + pie(730). Placement anywhere-empty (adjacency vestigial; 397 legal after 4 moves).

**Placement & capture.** outnumber-2 → enemy stone with (enemy − friendly) ≥ 2 cleared to empty. Verified live: P1 at (0,1,0) flanked by P2 at (0,0,0)+(0,2,0) was captured. Fires only against exposed stones.

**Propagation.** influence, r=1, strength 1.0, **decay 0.7**. Self +1.0, each neighbour +0.7. **Derived packing law (verified):** adding a stone with *k* friendly contacts gains **1 + 1.4k** to the accumulator — line tip (k=1) ≈ +2.4, inner corner (k=2) ≈ +3.8. Less flat than the decay-1.0 top game; spacing matters slightly more.

**Win condition.** threshold-race > **30.0**; `target_dimension_p2 = -1` (P2 mirrors P1's accumulator). **Engine komi = komi_p2 × threshold = 0.05 × 30 = 1.5** (NOT 0.05 — see soft violation). max_turns 100.

**Pie rule.** True (action 730).

**Degeneracy check.**
- **Helper display bug (soft violation):** the per-move "Scores" line shows P2's komi as +0.05, but the engine win-check uses **+1.5**. Agents reading the helper near threshold will mis-judge who wins.
- `target_dimension_p2 = -1` is a mirror flag, not a second objective.
- `move_constraint=adjacent_empty` vestigial.

---

## Phase 2 — Strategic Play

All moves engine-verified.

### Game 1 — P1 corner-block pack vs P2 mirror (the komi flip)
Sequence: `0,162,1,163,2,164,9,171,11,173,18,180,19,181,20,182,27,189,28,190,29,191` (22 plies, **P2 wins (Winner=2)**).
Plot: both build identical clusters (P1 top-left z=0 block, P2 mirror on z=2). At ply 21 P1 reaches **+29.2** — just *under* 30. At ply 22 P2 places its mirror stone, reaching the same +29.2 in owned influence **plus the real +1.5 komi = +30.7 > 30 → P2 wins.** The threshold (30) lands exactly in the gap where P1's 11-stone build (+29.2) fails to cross but P2's mirror+komi does.
Reflection: **balance here is a knife-edge komi-tuning artifact.** With threshold 30 and ~+3.8/stone, P1 stalls at +29.2 and the 1.5-point komi flips the symmetric game to P2.

### Game 2 — P2 out-packs (density beats tempo)
P2 abandoned the mirror, packed the dense top-left corner block while P1 spread along a row → P2 +20.9 vs P1 +19.5 by ply ~18, despite being a tempo down. Confirms the menger family's one real lever: choose the highest-coordination region.

### Game 3 — Capture / pie probes
Capture fires only against lone stones (verified). Pie swap (730) transfers tempo; with komi already favouring P2 by +1.5, P2 is unlikely to need it.

### Strategy guides
**P1:** pack the densest hole-free block; aim to *overshoot* 30 on a high-contact move rather than stall at +29 (the komi punishes stalling exactly at threshold).
**P2:** mirror is sufficient given the +1.5 komi — you win symmetric races. Otherwise out-pack a denser region.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Moderate — diversity 0.667 (higher than the decay-1.0 top game). Decay 0.7 leaves a little spacing nuance, so a few packing families compete.
**Counter-play.** Out-pack or rely on komi (P2). Captures not a real counter.
**Short-term vs long-term.** ~1-ply lookahead; games end ~ply 22 (shorter race than the 50/200 sibling).
**Emergent concepts.** Packing law (1+1.4k); density-beats-tempo; **komi knife-edge** (a brittle balance emergent from threshold/build-rate alignment).
**Does menger matter?** Yes — region density reading is the skill.
**Does the kernel matter?** decay 0.7 is the better setting than the top game's 1.0 (slightly more nuance), but still arithmetic.
**Capture contribution.** Inert in competent play.
**First-mover / seat balance.** This is the **sibling differentiator** (per README): the *shorter* race (30/100) vs game 1fea3357dca4's longer race (50/200). The short race makes balance hyper-sensitive — komi 0.05 *over*-corrects and hands symmetric games to P2. Briefing says G3 passed (bias 0.015), but my play shows the balance is tuned-to-the-threshold, not robust.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Identical kernel to its sibling 1fea3357dca4 and to the R20 menger family; only `threshold` (30 vs 50) and `max_turns` (100 vs 200) differ.
(a)(b)(c) Threshold-race influence + outnumber capture on a sponge = R20 menger family; closest external analogue is a disc-counting territory race.
(d) Fractal substrate = geometric novelty only.
(e) Expert transfer ~5 min.

**Closest known-game analogue:** R20 menger threshold-race family (short-race variant). The only intra-family differentiator is the faster threshold.
**Comparison to R8 (4.10).** Thinner in structure (no goal-shape), but better balanced via pie+komi.
**Comparison to R19/R20.** Same family as R20 5f5c (my team 4.0); the short race is sharper but adds no depth.

**Novelty score (post-adversary):** **3/10.** A parameter-sibling of the menger family; the 30/100 tuning is the entire differentiator, which is balance-tuning, not new strategy. Anchor: R8 4.10, R19 top 4.8.

---

## Phase 5 — Verdict

**Team ID:** team-3
**Game ID:** e52e8889517a
**Rules Summary:** Menger packing race to 30 with decay-0.7 influence (inner corners +3.8, line tips +2.4); a real +1.5 komi flips symmetric mirror games to P2. The shorter-race sibling of 1fea3357dca4.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=True, komi_p2=0.05.
**Turn Structure:** alternating
**Hybrid actions:** no.
**Soft violations flagged:** helper "Scores" line under-displays komi (engine uses komi_p2×threshold = 1.5, helper shows 0.05); outnumber-2 inert vs packed play; balance is knife-edge (threshold-tuned, not robust).

### Scores (1–10)
- **Strategic Depth: 4** — Same packing-region puzzle as the family; decay 0.7 gives marginally more spacing nuance than the decay-1.0 top game. ~1-ply horizon.
- **Emergent Complexity: 4** — Packing law + density-beats-tempo + the brittle komi-flip balance.
- **Balance: 5** — Pie + komi are two real balancers, but the short race makes komi *over*-correct (symmetric games → P2). Tuned, not robust.
- **Novelty (post-adversary): 3** — Parameter-sibling of the menger family; differentiator is threshold tuning.
- **Replayability: 4** — Diversity 0.667; a few packing families compete in the opening.
- **Overall "Would an agent team play this again?": 4.0** — A competent, slightly-better-balanced menger race; the shorter threshold makes it sharper than its 50/200 sibling but no deeper. Between R20 production (3.73) and R8 replay (4.10); below the R19 ceiling.

### CLOSEST KNOWN-GAME ANALOG
R20 menger threshold-race (short-race variant); externally a disc-counting territory race with no flips.

### KILLER FLAWS
- Captures inert; ~1-ply horizon.
- Balance is threshold-tuned (komi over-corrects to P2 in symmetric play) — fragile, not robust.

### BEST QUALITY
The **density-beats-tempo** packing lever and a genuinely contested-to-the-last-stone race (the komi-flip ending is a real, if brittle, source of tension).

### MENGER STRUCTURAL CONTRIBUTION
Region-density reading is the skill; the substrate matters more than a flat grid would. Still geometric, not deep.

### IMPROVEMENT IDEAS
**Single best change:** retune threshold so the symmetric race resolves on a *clean overshoot* by whoever is ahead on packing, rather than on a komi knife-edge at +29.2 — i.e. decouple balance from exact threshold/build-rate alignment.
Secondary:
- Fix the helper to display the scaled komi (komi_p2 × threshold).
- Make captures relevant or drop them.
