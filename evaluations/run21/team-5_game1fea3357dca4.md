# Run 21 Agent-Team Eval — team-5 — Game 1fea3357dca4

**Team ID:** team-5
**Game ID:** 1fea3357dca4 (menger original rank 1 → rank 6 under 20-seed; mean GE 0.118, σ 0.085, Δ −0.093 = largest deflation; calibrated komi_p2 0.05)
**Substrate:** menger (axis 9, 400 active / 729, max_degree 6, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game 1fea3357dca4` (see `briefing_menger_1fea3357dca4.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Same Menger sponge: 400/729 active, `c=z*81+y*9+x`, max_degree 6.

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = **200**.

**Action space.** 731 (729 + pass + pie 730). Anywhere-empty (`adjacent_empty` vestigial — verified 401 legal after P1's first move).

**Placement & capture.** **outnumber, threshold 2** (same as pod). Clears to empty.

**Propagation.** influence, radius 1, strength 1.0, **decay 0.7** (self +1.0, neighbour +0.7) — identical to `e52e`/`bfd1`.

**Win condition.** **threshold-race**, target **50.0** (vs the pod's 30) — a long grind. `target_dimension_p2=-1` (mirror). **Komi = 0.05 × 50 = 2.5** (engine multiplicative). Helper shows flat "+0.05" — **real P2 bonus is 2.5.** Timeout → piece-count majority.

**Pie rule.** True (id 730).

**Sibling note.** This ↔ `e52e8889517a` are the parameter-sibling pair: identical except **threshold 50/max_turns 200 (this) vs 30/100 (sibling)**. **I score the longer-race differentiator only.** I confirmed by play: this resolves ~36 plies vs the sibling's ~22.

**Degeneracy check.** `adjacent_empty` vestigial; helper komi display flat (real 2.5); high σ/mean ratio (0.72) is the lucky-seed-inflation signature flagged in the briefing.

---

## Phase 2 — Strategic Play

### Game 1 — Mirror slab race to 50 (the grind)
Sequence: `0,6,1,7,2,8,9,15,11,17,18,24,19,25,20,26,27,33,28,34,29,35,36,42,38,44,45,51,46,52,47,53,54,60,55,61` (36 plies).
Plot: P1 packs the left x0–2 slab, P2 the right x6–8 slab. decay-0.7 compounding over a much larger region. At ply 36, P1 raw ≈ 48.8; **P2 raw 48.8 + komi 2.5 = 51.3 → P2 crosses 50 first. Engine: Done, Winner=2 at ply 36** (the next P1 move was rejected as illegal — game already over). The larger komi 2.5 again flips the clean mirror to P2.
Reflection: doubling the target from 30 to 50 just **adds ~14 plies of the same packing** — no new decisions emerge in the back half. This is the "longer ≠ deeper" signature. The original rank-1 GE did not survive 20-seed re-evaluation precisely because the long grind is swingy/seed-sensitive, not rich.

### Game 2 — Pie swap
Sequence: `20,730,11` — P2 swaps; with komi 2.5 ALSO favouring P2, the swap+komi together over-reward P2 unless P1 opens carefully. Since all opening stones are worth +1, P1's opening is balance-neutral and komi does the heavy lifting.

### Game 3 — Capture / contest (shared family probe)
Confirmed (via the pod's verified mechanics on identical rules): outnumber-2 clears a stone for 2 plies of cost; sapping into the enemy slab drops their accumulator ~1/contact but is mutually destructive. In a 36-ply grind there is *more* opportunity to contest than in the 22-ply sibling, but contesting still trades tempo unfavourably for the leader.

### Strategy guides
**P1:** Pack a large contiguous slab; you must out-grind komi 2.5, so you need more than a one-tempo margin — harder than the sibling. Avoid contact.
**P2:** Mirror and ride komi 2.5 over the line first; or swap. The longer race gives komi more room to decide.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** No more than the pod — DB strategic_depth 0.485 is the **lowest** in the menger pod, consistent with the deflation. The longer race does not open new plans.
**Counter-play.** Captures/sapping fire and there is more time to use them, but they remain tempo-costly; komi is P2's real lever.
**Short-term vs long-term.** ~36-ply horizon, but the extra length is repetition, not deeper planning. max_turns 200 still unused.
**Emergent concepts.** Same palette (compounding, captures, komi-finishing); the long grind adds variance, not concepts.
**Does menger matter?** Same navigation/z-stacking; no new axis.
**Does the kernel matter?** decay 0.7 = same gradient as the sibling.
**Capture contribution.** Slightly higher salience than the short sibling purely because the game lasts longer; still situational.
**Seat balance.** komi 2.5 flips the clean mirror to P2 (as in `e52e`), but the briefing flags this game as the **swingiest** (σ 0.085, lucky-seed signature) — balance is "corrected on average" but high-variance.

**Inflation diagnosis (the eval question).** **Confirmed.** Played head-to-head with its short sibling, this game feels *shallower per ply*, not deeper — the rank-1 GE was a lucky-seed artifact, and the −0.093 deflation is the truth. The longer target is grind, not depth.

---

## Phase 4 — Novelty Adversary

**Adversary case.** Decay-0.7 influence-race to a high target on a sponge with outnumber-2 capture — same family as `e52e`/`bfd1`.
(a) area/score race. (b) Ataxx/Tafl capture. (c) standard family combination, just a longer finish. (d) sponge = navigation. (e) expert-transfer ~5 min.
**Closest analogue:** `e52e` with a doubled target — a longer R20-style menger race.
**Intra-family differentiator:** the **long race (50/200)** is more seed-sensitive and shallower-per-ply than the short sibling; it is the inflation case-study, not a distinct game.
**Comparison to R8 (4.10):** different family, slightly *below* comparable level once deflation is accounted for.
**Comparison to R19/R20:** at/below R20 production; thinner than R19 menger 4.8.

**Novelty score (post-adversary):** 3.0/10. Standard family member; the "longer race" is a parameter, not a novelty, and it reads as a regression (grind).

---

## Phase 5 — Verdict

**Team ID:** team-5
**Game ID:** 1fea3357dca4
**Rules Summary:** A decay-0.7 influence-packing race to a *high* +50 target on a Menger sponge; doubling the finish line over its sibling adds ~14 plies of the same packing without new decisions — the inflated original rank-1 that deflated hardest under honest re-evaluation.
**Substrate:** menger, axis 9, 400/729, max_degree 6, pie_rule=True, komi_p2=0.05 (real ×50 = 2.5).
**Turn Structure:** alternating. **Hybrid actions:** no.
**Soft violations flagged:** helper komi display flat (real 2.5); `adjacent_empty` vestigial; high σ/mean (lucky-seed inflation signature).

### Scores (1–10)
- **Strategic Depth: 3.3** — lowest DB strategic_depth in the pod (0.485); the long grind is repetition, not depth. Confirmed shallower-per-ply than the short sibling.
- **Emergent Complexity: 3.0** — same palette as the pod; length adds variance, not concepts.
- **Balance: 3.5** — komi 2.5 corrects the mirror to P2 on average, but swingiest in the pod (high σ).
- **Novelty (post-adversary): 3.0** — a parameter variant; reads as a regression.
- **Replayability: 3.0** — long, repetitive; openings converge.
- **Overall: 3.4** — the inflation case-study confirmed: shallower than its rank-1 GE implied, and a grind to play. Lowest of the menger pod; at R17 mean (3.5)–. Below the R19 ceiling.

### CLOSEST KNOWN-GAME ANALOG
`e52e` with a doubled target — a long decay-0.7 Ataxx-style area race on menger.

### KILLER FLAWS
- **Longer ≠ deeper** — the 50/200 race is ~14 extra plies of identical packing with no new decisions.
- **Swingiest balance in the pod** (lucky-seed inflation signature); the rank-1 GE did not survive honest re-evaluation.

### BEST QUALITY
Mostly a diagnostic: it cleanly demonstrates the GE-inflation failure mode (rank-1 single-seed → rank-6 at 20 seeds). The decay-0.7 compounding is fine; the target is just set too high.

### MENGER STRUCTURAL CONTRIBUTION
Same as the pod: navigation + z-stacking, no new strategic axis.

### IMPROVEMENT IDEAS
**Single best change:** lower the target to its sibling's 30 (and max_turns to 100) — i.e. *become* the sibling, which is strictly better-behaved. The slate should keep `e52e` over this one (dedup).
Secondary: this game's deflation is the strongest argument in the slate for 20-seed (not single-seed) GE as the fitness signal; treat its rank-1 history as a cautionary artifact, not a quality claim.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-5_game1fea3357dca4.md`.*
