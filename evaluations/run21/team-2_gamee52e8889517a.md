# Run 21 Agent-Team Eval — team-2 — Game e52e8889517a

**Team ID:** team-2
**Game ID:** e52e8889517a (menger rank 3, 20-seed mean GE 0.138, σ 0.090, calibrated komi_p2 0.05)
**Substrate:** menger (axis 9, 400 active / 729 grid, max_degree 6, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game e52e8889517a` (see `briefing_menger_e52e8889517a.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Menger sponge, 400/729 active, max_degree 6 (identical substrate to the other 3 menger slate games). Cell = z·81 + y·9 + x.

**Turn structure.** Alternating, 1 piece/turn, P1 first. **Max_turns = 100.**

**Action space.** 731 = 729 place + pass + pie(730). `first_move_anywhere`, then broad legal set (397 legal after 4 stones); `adjacent_empty` effectively non-binding.

**Placement & capture.** **outnumber, threshold 2** — a stone is cleared when enemy neighbours exceed friendly by ≥2 (radius-1). Verified live in the family: 2 adjacent enemies clear a lone stone; cluster-interior cells are safe.

**Propagation.** `influence`, radius 1, strength 1.0, **decay 0.7**. Self +1.0, each neighbour +0.7. Score(P1 cell) = 1 + 0.7·(#P1 nbrs) − 0.7·(#P2 nbrs). The gradient (vs e1453's flat 1.0) gives slightly more positional texture.

**Win condition.** **threshold-race**, exceed **30.0**. `target_dimension_p2 = -1` ⇒ P2 mirrors P1's accumulator. komi_p2 = **0.05** (bias term 0.015). max_turns 100.

**Pie rule.** On (action 730), P2 may swap after P1's first move.

**Degeneracy check.**
- `target_dimension_p2 = -1` is a mirror flag, not a second objective (both seats race the same scalar).
- `adjacent_empty` vestigial.
- Captures real but tactically marginal in dense play (and conflict with the score objective).
- Bimodal training: ~5% zero / ~20% ceiling reruns — weight a clean converged playthrough over the mean.

**This game is the deliberate parameter-sibling of `1fea3357dca4`.** Structural diff is exactly two fields: `threshold` 30 (here) vs 50, and `max_turns` 100 (here) vs 200. Capture, decay 0.7, topology, pie, komi identical. The contrast under test = **short race (30/100) vs long race (50/200)**.

---

## Phase 2 — Strategic Play

Place id = cell; pass = 729; pie = 730. All moves engine-verified.

### Game 1 — Symmetric mirror race (tempo + komi test)
Sequence: `0,80,9,71,1,79,18,62,2,78,11,69,19,61,20,60,81,141,83,143,99,159,101,161` (P1 (0,0,0) corner+z-stack; P2 mirrors (8,8,0)).
Plot: ~+2.6/stone in dense corners (a touch below e1453's +2.7 — decay 0.7 < 1.0). **Game ended at ply 24 with Winner = P2.** Here komi 0.05 tipped the mirror to the second player: P1's tempo edge was just slightly overcome by P2's +0.05 + one extra equalizing stone at the finish.
Reflection: The shorter 30-threshold race is decided within ~24 plies, well inside max_turns 100 — so the 100-cap is never reached and is irrelevant to play.

### Game 2 — P2 swap line
Sequence: `0,730,...` — P2 swaps P1's opening (confirmed in the family: 730 flips the opening stone and tempo to P2). With komi already nudging P2 ahead, the swap makes P2's seat clearly fine — arguably P1 should NOT open too strong here, lest P2 swap into komi+tempo.
Reflection: With komi 0.05 + pie, P2's seat is healthy; the family's first-mover edge is well-compensated for this variant (G3 passed for e52e).

### Game 3 — Capture / spoiler stress
Family-verified: outnumber-2 clears only isolated stones; spoiling adjacent to an opponent cluster is net-negative for the spoiler (it earns ~2.1/stone vs ~2.6 for a clean own-corner and risks capture). No viable disruption strategy beyond the race.

### Strategy guides
**P1:** pack a contiguous corner block on a face layer, z-stack into hollow layers, race to 30. Don't over-commit the opening (P2 can swap into komi+tempo).
**P2:** swap a strong opening, else mirror-pack; komi 0.05 already gives you the finish-line edge in a clean mirror.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** One — pack densest contiguous region. (DB single-seed strategic_diversity 0.667 is higher than e1453's 0.181; in practice the decay-0.7 gradient permits marginally more line variety, but the meta is still "race your own blob.")
**Counter-play.** Out-race, or swap. No structural counter.
**Short-term vs long-term.** Horizon ~3–4 moves; game ~24 plies. Shallow.
**Emergent concepts observed.** Clustering compounding, z-stacking, capture-only-on-isolated.
**Does menger matter?** Same as the family — routing puzzle through holes; not a strategic generator.
**Does the kernel matter?** decay 0.7 gives a mild positional gradient absent in e1453 (1.0); slightly more texture, same skeleton.
**Capture contribution.** Marginal.
**First-mover / seat balance.** With komi 0.05 + pie, the mirror actually tips to **P2** (Winner=2 in my run) — G3 calibration looks genuinely passed for this variant, the cleanest-balanced of the menger pod alongside the threshold being short enough to avoid drift.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Threshold-race influence-packing on a Menger sponge — the R19/R20 menger family, decay 0.7, short clock.
(a) Threshold race ≈ numeric area/territory scoring.
(b) Outnumber-2 ≈ Ataxx/Tafl flanking, near-inert here.
(c) Not a named published game; internally a re-skin of the menger threshold-race pod.
(d) Fractal substrate is uncommon but constraint-only.
(e) ~5 min expert transfer.

**Closest known-game analogue:** numeric-territory race on a fractal lattice.
**Comparison to R8 (4.10).** Thinner (no cut+build).
**Comparison to R19/R20 best.** Same family as R19 menger top (4.8) / R20 (4.80); judged down under the anchored rubric. The intra-family differentiator here (short 30/100 race) is the *robust* sibling — it held rank 3 while the 50/200 sibling deflated to rank 6.

**Novelty score (post-adversary):** **3.0/10.** Re-parameterization of the menger threshold-race family.

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game ID:** e52e8889517a
**Rules Summary:** Menger threshold-race: pack influence to +30, decay-0.7 gradient, komi 0.05 + pie balance the seats. The short-clock sibling of 1fea.
**Substrate:** menger, axis 9, 400/729, max_degree 6, pie_rule=True, komi_p2=0.05.
**Turn Structure:** alternating.
**Hybrid actions:** no.
**Soft violations flagged:** vestigial `adjacent_empty`; mirror-flag `target_dimension_p2=-1`; bimodal training (5% zero / 20% ceiling).

### Scores (1–10)
- **Strategic Depth: 3.6** — Same packing race as e1453 but the decay-0.7 gradient adds a sliver of positional choice; ~24-ply game, 3–4-move horizon.
- **Emergent Complexity: 3.2** — Clustering + z-stacking + mild gradient; captures inert.
- **Balance: 3.7** — Best-balanced of the menger pod: komi 0.05 + pie + short clock; mirror actually tipped to P2 (G3 genuinely passed).
- **Novelty (post-adversary): 3.0** — Menger threshold-race re-parameterization.
- **Replayability: 3.3** — A little more line variety than e1453 (diversity 0.667 single-seed), but the meta is fixed.
- **Overall "Would an agent team play this again?": 3.5** — Competent, the best-calibrated menger variant, but strategically the same packing race. Around R17/R20 production level, below R8 (4.10); does not clear 5.0.

### CLOSEST KNOWN-GAME ANALOG
Numeric-territory race on a fractal lattice; in-corpus the menger threshold-race pod (short-clock variant).

### KILLER FLAWS
- Strategy collapses to densest-blob packing; captures inert.
- The two-field diff vs its 50/200 sibling is pure pacing, not depth.

### BEST QUALITY
Cleanest seat balance in the menger pod (komi 0.05 + pie + short clock) — the one menger game where the second player is demonstrably fine.

### menger STRUCTURAL CONTRIBUTION
Routing-puzzle floor from the holes; no strategic ceiling lift. Decay 0.7 preserves a faint positional gradient that e1453's flat 1.0 destroys — a point in this sibling's favour.

### IMPROVEMENT IDEAS
**Single best change:** as with the family — replace pure additive-threshold scoring with a win condition the influence field actually shapes (regions/connection), to break the single-blob optimum.
Secondary:
- It is near-indistinguishable from `bfd1` (30/200) in play; the slate could drop one of them (G2 dedup pressure).
- Strengthen capture so defence becomes a real decision.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-2_gamee52e8889517a.md`.*
