# Run 21 Agent-Team Eval — team-5 — Game e52e8889517a

**Team ID:** team-5
**Game ID:** e52e8889517a (menger rank 3 by 20-seed mean GE 0.138, σ 0.090, calibrated komi_p2 0.05)
**Substrate:** menger (axis 9, 400 active / 729 grid, max_degree 6, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game e52e8889517a` (see `briefing_menger_e52e8889517a.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Identical Menger sponge to the other 3 menger games: 400/729 active, holes at center-cross cells, `c = z*81+y*9+x`, max_degree 6. Many low indices are dead.

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = **100**.

**Action space.** 731 = 729 cells + pass + pie(730). Placement anywhere-empty (`adjacent_empty` vestigial — verified 397 legal after 4 moves).

**Placement & capture.** **outnumber, threshold 2** — a stone is cleared when ≥2 enemy neighbours outnumber its owner by 2. **Verified live in a contact fight:** P2 captured P1's (1,2,0) mid-cluster, dropping P1's accumulator ~1.7.

**Propagation.** influence, radius 1, strength 1.0, **decay 0.7** (self +1.0, each neighbour +0.7). This is the R20-champion decay regime — a contiguous line scores less than under flat decay (line of 9 ≈ +20 vs +25 flat). Gradient is present.

**Win condition.** **threshold-race**, target **30.0**, `target_dimension_p2=-1` (P2 mirrors P1's accumulator). **Komi is multiplicative: 0.05 × 30 = 1.5** (engine `_check_threshold`). The helper displays a flat "+0.05" — **misleading; the real P2 bonus is 1.5.** Timeout → piece-count majority.

**Pie rule.** True (id 730). Swap takes P1's opening stone.

**Sibling note.** This game ↔ `1fea3357dca4` are the deliberate parameter-sibling pair. The structural diff is exactly **two fields**: threshold 30 (this) / 50 (sibling) and max_turns 100 (this) / 200 (sibling). Capture, decay 0.7, topology, pie are identical. **I score the shorter-race differentiator only.** I confirmed the diff by playing both: this game resolves ~22 plies, the sibling ~36.

**Degeneracy check.** Helper komi display flat (real = ×30); `adjacent_empty` vestigial; `target_dimension_p2=-1` is a mirror flag, not a second objective. Threshold/decay/pie all live.

---

## Phase 2 — Strategic Play

### Game 1 — Mirror compact-cluster race (the headline line)
Sequence: `0,6,1,7,2,8,9,15,11,17,18,24,19,25,20,26,27,33,28,34,29,35` (22 plies).
Plot: P1 packs (x0–2) corner, P2 mirrors (x6–8). Clusters compound at +2.4 to +3.8/stone (less than flat-decay game 1 because neighbours give 0.7 not 1.0). At ply 22, P1 raw +29.2, P2 raw +29.2 **+ komi 1.5 = 30.7 → P2 crosses first. Engine: Done, Winner=2.** The multiplicative komi flips the mirror to P2.
Reflection: with komi 1.5 ≈ a half-stone's worth of compounding, the one-tempo P1 lead is overturned — this is *why* the briefing reports calibration passed (bias 0.015). The shorter 30-target makes komi a larger fraction of the finish, so balance holds better than the sibling.

### Game 2 — P2 contest (sap + in-cluster capture)
Sequence: `0,1,9,11,18,2,19,20,27,28` — P2 invades P1's region. At ply 8 P2's bracket **captured P1's (1,2,0)** (outnumber-2), dropping P1 +9.2→+7.5. But P2's own invading stones are sapped; net P2 fell behind. Contact fighting is a real but tempo-costly lever.

### Game 3 — Pie swap
Sequence: `20,730,11,19` — P2 swaps P1's opening stone; position becomes P1-to-move, P2 +1 stone, +komi 1.5. With both swap-tempo AND komi favouring P2, P1 must open weakly; since all opening stones are worth +1, the swap is indifferent and the komi does the balancing.

### Strategy guides
**P1:** Pack the densest contiguous region; you lead the mirror by one tempo but **must out-pace komi 1.5** — i.e. you need slightly more than a one-tempo margin. Avoid contact fights.
**P2:** Mirror and let komi 1.5 carry you over first; or swap for tempo. Contact captures only when they remove a high-degree P1 cell cheaply.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Somewhat — DB strategic_diversity 0.667 (higher than the flat-decay game's 0.181), and decay 0.7 gives a mild gradient so cluster *shape* matters a little more. Still fundamentally a packing race.
**Counter-play.** Captures fire in contact (verified) and can swing ~1.7; combined with the komi this gives P2 a genuine path to win the mirror. More real counter-play than the flat-decay sibling-of-the-pod.
**Short-term vs long-term.** ~22-ply horizon; medium-term planning is shallow but the gradient adds a little shape consideration.
**Emergent concepts.** Compounding clusters, in-cluster captures (real here), komi-aware finishing (must beat the 1.5 buffer).
**Does menger matter?** Same as the pod: hole-navigation + z-stacking, no new strategic axis.
**Does the kernel matter?** Yes — decay 0.7 restores the gradient the flat-decay game throws away, making cluster shape (not just size) weakly relevant.
**Capture contribution.** Higher than the flat-decay game: captures fired in my contact line and the gradient makes contested boundaries worth fighting.
**Seat balance.** **Best in the menger pod.** Multiplicative komi 1.5 flips the clean mirror to P2; briefing calibration passed (bias 0.015). The shorter 30/100 race makes komi proportionally larger → robust.

---

## Phase 4 — Novelty Adversary

**Adversary case.** Influence-accumulation race (decay-0.7 regime) on a sponge with outnumber-2 capture.
(a) threshold-race ≈ area/score race. (b) outnumber-2 ≈ Ataxx/Tafl custodial-by-count, here occasionally firing. (c) the combination is the R20-champion family; this game is a faithful member, not a departure. (d) sponge = packing navigation. (e) expert-transfer ~5 min.
**Closest analogue:** R20 decay-0.7 influence-race champion on menger. **Intra-family differentiator vs sibling 1fea:** the shorter race (30/100) is more seed-robust (held rank 3 while the sibling deflated to rank 6) and better-balanced (komi a larger fraction of the target).
**Comparison to R8 (4.10):** different family; comparable absolute level.
**Comparison to R19/R20:** ≈ R20 production; thinner than R19 menger 4.8.

**Novelty score (post-adversary):** 3.0/10. This is the *standard* R21 menger race (decay 0.7) — the headline novelty (flat decay) lives in the sibling-pod's `e1453`, not here. Solid family member, low marginal novelty.

---

## Phase 5 — Verdict

**Team ID:** team-5
**Game ID:** e52e8889517a
**Rules Summary:** A decay-0.7 influence-packing race to +30 on a Menger sponge; the multiplicative komi (1.5) balances the first-mover tempo, and outnumber-2 captures give contact fights real (if costly) stakes. The shorter, better-balanced member of the menger sibling pair.
**Substrate:** menger, axis 9, 400/729, max_degree 6, pie_rule=True, komi_p2=0.05 (real ×30 = 1.5).
**Turn Structure:** alternating. **Hybrid actions:** no.
**Soft violations flagged:** helper komi display flat (real 1.5); `adjacent_empty` vestigial.

### Scores (1–10)
- **Strategic Depth: 3.5** — packing race with a mild gradient; diversity 0.667 and firing captures lift it slightly above the flat-decay game.
- **Emergent Complexity: 3.0** — compounding + in-cluster captures + komi-aware finishing; nothing multi-step.
- **Balance: 4.0** — best in the menger pod; multiplicative komi 1.5 flips the mirror to P2, calibration passed (bias 0.015).
- **Novelty (post-adversary): 3.0** — standard R21 menger race; differentiator is robustness, not novelty.
- **Replayability: 3.5** — diversity 0.667 and contact-fight texture give modest opening variety.
- **Overall: 3.6** — a clean, well-balanced family member. Between R17 (3.5) and R20 production (3.73); below the R19 ceiling.

### CLOSEST KNOWN-GAME ANALOG
R20 decay-0.7 influence-race champion, on menger — an Ataxx-flavoured area race with a finish line.

### KILLER FLAWS
- Marginal novelty — it is the family baseline (the flat-decay innovation is in its pod-mate).
- Still a packing race at heart; captures are tempo-costly.

### BEST QUALITY
Cleanest balance in the menger pod: the multiplicative komi genuinely converts a P1-tempo win into a fair contest, and the decay-0.7 gradient + firing captures make contested boundaries worth playing.

### MENGER STRUCTURAL CONTRIBUTION
Same as the pod: hole-navigation and z-stacking, no new strategic axis. Substrate ≈ neutral.

### IMPROVEMENT IDEAS
**Single best change:** widen the intra-family contrast deliberately — e.g. raise capture salience (outnumber-2 transfers influence) so the shorter race rewards aggression differently from the long sibling, giving the pair a real strategic dichotomy rather than a pace difference.
Secondary: this game is the better-calibrated sibling; if only one of the pair survives dedup, keep this one (30/100, robust).

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-5_gamee52e8889517a.md`.*
