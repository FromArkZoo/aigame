# Run 21 Agent-Team Eval — team-2 — Game bfd1bb7ced76

**Team ID:** team-2
**Game ID:** bfd1bb7ced76 (menger rank 5, 20-seed mean GE 0.126, σ 0.070, calibrated komi_p2 0.00)
**Substrate:** menger (axis 9, 400 active / 729 grid, max_degree 6, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game bfd1bb7ced76` (see `briefing_menger_bfd1bb7ced76.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Menger sponge, 400/729 active, max_degree 6 (identical substrate to the rest of the menger pod). Cell = z·81 + y·9 + x.

**Turn structure.** Alternating, 1 piece/turn, P1 first. **Max_turns = 200.**

**Action space.** 731 = 729 place + pass + pie(730). `first_move_anywhere`; `adjacent_empty` overridden by `constraint=anywhere` → placement is anywhere-empty (verified in family).

**Placement & capture.** **outnumber, threshold 2** — stone cleared when enemy neighbours exceed friendly by ≥2 (radius-1, ≤6). Family-verified: 2 adjacent enemies clear a lone stone; cluster cells safe.

**Propagation.** `influence`, radius 1, strength 1.0, **decay 0.7**. Self +1.0, neighbour +0.7. Verified live in family: two adjacent friendlies → 3.40 = 2·1.0 + 2·0.7.

**Win condition.** **threshold-race**, exceed **30.0**. `target_dimension_p2 = -1` ⇒ P2 mirrors P1's accumulator. komi_p2 = **0.00**. max_turns 200 — but the 30-race finishes ~25 plies, so the 200 cap is **never approached** (functionally identical to e52e's 100 cap).

**Pie rule.** On (action 730).

**Degeneracy check.**
- `adjacent_empty` vestigial.
- `target_dimension_p2 = -1` = mirror flag, not a 2nd objective.
- max_turns 200 is inert (race ends ~25 plies) — the only field separating this from e52e besides komi.
- Captures real but marginal in dense play.

**Reliability note under test:** this is flagged as the **most reliable learner** in the slate (no zero-failure rerun mode; S5 elite Δ only −0.064). The eval question is whether "reliably learnable" correlates with "deep." DB single-seed sub-scores are maxed (non_triviality 1.0, strategic_diversity 1.0) — I test whether that survives play.

---

## Phase 2 — Strategic Play

Place id = cell; pass = 729; pie = 730. All engine-verified.

### Game 1 — Symmetric mirror race (tempo test, komi 0)
Sequence: `0,80,9,71,1,79,18,62,2,78,11,69,19,61,20,60,81,141,83,143,99,159,101,161`.
Plot: Same packing dynamics as e52e (decay 0.7). **Game ended at ply 25 with Winner = P1.** With komi=0, P1's first-move tempo carries the mirror (the mirror image of e52e, where komi 0.05 tipped it to P2). So the *only* play-relevant difference from e52e is the komi value deciding the mirror.
Reflection: 200-turn cap irrelevant; the race is a ~25-ply sprint identical in character to the 30/100 sibling.

### Game 2 — Reliability vs depth probe
I played the dense-packing line repeatedly with small opening variations (different corner, different face layer). Outcomes were consistent and the strategic content invariant — "reliable" here means the single optimal plan (pack densest) is easy and stable to find, **not** that there are many deep plans. Reliability ↔ low-variance-of-a-shallow-optimum, not depth.

### Game 3 — Capture / pie
Family-verified: outnumber-2 clears only isolated stones; pie (730) swaps the opening. With komi=0, P2 *should* swap to neutralize P1's mirror-tempo edge (residual bias ≈0.060).

### Strategy guides
**P1:** pack densest contiguous region, race to 30; komi=0 means your tempo wins clean mirrors — keep it simple.
**P2:** **swap** on a strong opening (komi=0 leaves you a tempo down otherwise), then mirror-pack.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** One — densest-blob packing. The maxed single-seed diversity/non-triviality (1.0/1.0) does **not** manifest as multiple deep plans in play; it reflects the GE scorer's view, not the agent's experience.
**Counter-play.** Out-race or swap.
**Short-term vs long-term.** ~25-ply sprint, 3–4-move horizon.
**Emergent concepts observed.** Clustering compounding, z-stacking, capture-on-isolated.
**Does menger matter?** Routing puzzle only.
**Does the kernel matter?** decay 0.7 gives the same mild gradient as e52e.
**Capture contribution.** Marginal.
**First-mover / seat balance.** komi=0 → P1 wins the clean mirror (residual bias 0.060); pie is the balancer. Slightly worse default balance than e52e (which has komi 0.05).

**Reliability ↔ quality verdict:** reliability does **NOT** track depth here. bfd1 is the cleanest learner because its single optimum (pack tight) is trivial and stable to converge on — exactly why it is also among the *shallowest*. Stability of a shallow optimum, not richness.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Menger threshold-race family, decay 0.7, threshold 30, inert 200-cap.
(a)–(e) identical to the menger pod: numeric-territory race + near-inert outnumber capture on a fractal lattice; ~5 min expert transfer; not a named published game.

**Closest known-game analogue:** numeric-territory race on a fractal lattice.
**Comparison to R8 (4.10):** thinner.
**Comparison to R19/R20 best:** same family; the intra-family differentiator here is **reliability**, which I find does not buy depth.

**Novelty score (post-adversary):** **3.0/10.**

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game ID:** bfd1bb7ced76
**Rules Summary:** The most reliably-learnable menger threshold-race: pack influence to +30 (decay 0.7), komi=0 so P1's tempo wins clean mirrors. Plays identically to e52e bar komi and an inert 200-turn cap.
**Substrate:** menger, axis 9, 400/729, max_degree 6, pie_rule=True, komi_p2=0.00.
**Turn Structure:** alternating.
**Hybrid actions:** no.
**Soft violations flagged:** vestigial `adjacent_empty`; inert max_turns 200; mirror-flag `target_dimension_p2=-1`.

### Scores (1–10)
- **Strategic Depth: 3.5** — Same packing race; reliable convergence reflects a shallow stable optimum, not depth. ~25-ply, 3–4-move horizon.
- **Emergent Complexity: 3.2** — Clustering + z-stacking; captures inert.
- **Balance: 3.5** — komi=0 leaves P1 a tempo up in clean mirrors; pie is the balancer (slightly behind e52e's komi-0.05 default).
- **Novelty (post-adversary): 3.0** — Menger threshold-race family.
- **Replayability: 3.4** — Stable single optimum → low replay incentive once known.
- **Overall "Would an agent team play this again?": 3.5** — Cleanest learner in the pod, but reliability ≠ depth: it is reliable *because* its optimum is shallow. Around R17/R20 production level, below R8 (4.10); does not clear 5.0.

### CLOSEST KNOWN-GAME ANALOG
Numeric-territory race on a fractal lattice; in-corpus the menger threshold-race pod (reliable-learner variant).

### KILLER FLAWS
- "Most reliable learner" = most reliably-shallow: one trivial optimum (pack densest).
- Functionally a duplicate of e52e (only komi + an inert turn-cap differ) — G2 dedup pressure.
- Captures inert.

### BEST QUALITY
Rock-solid trainability (no zero-failure mode). Useful as a control/baseline, not as a deep game — the explicit answer to "does stability imply quality?" is **no**.

### menger STRUCTURAL CONTRIBUTION
Routing-puzzle floor only; identical to the rest of the pod. No strategic ceiling lift.

### IMPROVEMENT IDEAS
**Single best change:** to make reliability *meaningful*, the win condition must reward more than one plan (region-control or connection) — otherwise reliable training just certifies a shallow optimum.
Secondary:
- Drop either bfd1 or e52e from the slate (near-identical play).
- Give komi 0.05 (match e52e) for cleaner default balance.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-2_gamebfd1bb7ced76.md`.*
