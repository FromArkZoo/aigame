# Run 21 Agent-Team Eval — team-3 — Game 1fea3357dca4

**Team ID:** team-3
**Game ID:** 1fea3357dca4 (menger; original rank-1 → fell to rank-6 under 20-seed finalization, Δ −0.093 — largest deflation in slate; 20-seed mean GE 0.118, σ 0.085, calibrated komi_p2 0.05)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game 1fea3357dca4` (see `briefing_menger_1fea3357dca4.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Menger sponge, 400/729, max_degree 6. `c = z*81 + y*9 + x`.

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = **200**.

**Action space.** 731; placement anywhere-empty.

**Placement & capture.** outnumber-2 → clear to empty; inert vs packed play.

**Propagation.** influence, r=1, strength 1.0, **decay 0.7**. Packing law 1 + 1.4k (verified) — line tip +2.4, inner corner +3.8.

**Win condition.** threshold-race > **50.0**; mirror P2; **engine komi = 0.05 × 50 = 2.5** (helper displays only 0.05 — soft violation). max_turns 200. The 50-target on ~+3.8/stone is a long grind (~26 stones each).

**Pie rule.** True (action 730).

**Degeneracy check.** `adjacent_empty` vestigial (401 legal after move 1, verified). Helper under-displays komi (real +2.5). Threshold dispatch correct.

---

## Phase 2 — Strategic Play

### Game 1 — P1 corner pack vs P2 mirror (long race)
Sequence: `0,162,…,46,208` (36 plies shown; **race still open at +43.2 / +43.25**, resolving ~ply 42–44). Same symmetric packing as the short-race sibling e52e8889517a, just **twice as long** to reach 50. The +2.5 komi keeps P2 within a fraction at every step; the result again hinges on the knife-edge of who crosses 50 first.
Reflection: the longer threshold adds **length, not depth** — every ply is the same 1-ply contact-maximising packing decision, repeated ~26 times instead of ~11.

### Game 2 — P2 out-packs (density beats tempo)
The same density-beats-tempo lever from the pod applies: a denser non-mirror region overtakes a spread tempo-leader. The longer race gives more opportunity to express it, but the decision type is unchanged.

### Game 3 — Capture probe
outnumber-2 fires only against stranded stones; never against the packed blobs. Inert.

### Strategy guides
**P1:** pack the densest fractal block; the long race rewards relentless contact-maximising. Don't stall exactly at 50 (komi +2.5 punishes it).
**P2:** mirror + the +2.5 komi keeps you alive; out-pack for the win. Pie available.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Single-seed scores list diversity 1.0, but my play finds the *same* family as e52e8889517a — the longer race simply extends it. The README's task here is to **test the inflation diagnosis**: does it feel as deep as its original rank-1 GE? **It does not.** It plays as a longer, more tedious version of the menger packing race; the −0.093 deflation is justified — the original single-seed rank-1 was a lucky-seed inflation, not extra depth.
**Counter-play.** Out-pack; pie. Captures inert.
**Short-term vs long-term.** ~1-ply per move; the only added "horizon" is sustaining a packing plan over ~26 plies — endurance, not depth.
**Emergent concepts.** Packing law; density-beats-tempo; same komi knife-edge stretched over a longer race.
**Does menger matter?** Yes (region density), same as siblings.
**Does the kernel matter?** decay 0.7 as in siblings; the only real lever this game changes vs e52e is threshold 50/max_turns 200 — which is length.
**Capture contribution.** Inert.
**First-mover / seat balance.** komi 0.05 → +2.5 effective; sibling-comparable. With the longer race the komi has more room to over/under-shoot; balance remains tuned, not robust. (README: parameter-sibling of e52e8889517a — contrast: same kernel, longer race, *more* deflated and *more* grind-y, confirming the longer race is the worse variant.)

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Same kernel as e52e8889517a and the R20 menger family; the only diff is threshold 50 / max_turns 200.
(a)(b)(c) Threshold-race influence + outnumber on a sponge = R20 menger family; external = disc-counting territory race.
(d) Fractal = geometric novelty.
(e) ~5 min expert transfer.

**Closest known-game analogue:** R20 menger threshold-race family (long-race variant).
**Comparison to R8 (4.10).** No goal-shape; better balanced; captures equally inert; the long grind makes it *less* engaging than R8.
**Comparison to R19/R20.** Same family as R20 5f5c (my team 4.0); the deflation shows its original rank-1 GE was inflated, not deep.

**Novelty score (post-adversary):** **3/10.** Parameter-sibling; the long race is its only distinction and it subtracts engagement. Anchor R8 4.10.

---

## Phase 5 — Verdict

**Team ID:** team-3
**Game ID:** 1fea3357dca4
**Rules Summary:** The long-race (50/200) sibling of e52e8889517a — the same Menger decay-0.7 packing race, stretched to ~26 stones a side, with a +2.5 komi. Original GE rank-1 that deflated to rank-6: the inflation diagnosis is confirmed in play.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=True, komi_p2=0.05.
**Turn Structure:** alternating
**Hybrid actions:** no.
**Soft violations flagged:** helper under-displays komi (engine uses 2.5, helper shows 0.05); outnumber-2 inert; balance tuned not robust; long grind for no added depth.

### Scores (1–10)
- **Strategic Depth: 4** — Identical packing puzzle to its short-race sibling; the extra length adds endurance, not planning horizon. ~1-ply.
- **Emergent Complexity: 4** — Same emergents (packing law, density-beats-tempo); no new texture from the longer race.
- **Balance: 5** — Pie + komi (real +2.5); knife-edge over a longer race, tuned not robust.
- **Novelty (post-adversary): 3** — Parameter-sibling; the long race is the only differentiator and it subtracts engagement.
- **Replayability: 4** — Single-seed diversity 1.0, but the long grind makes repeated play tedious.
- **Overall "Would an agent team play this again?": 3.9** — A competent but *grindier* menger race; the deflation to rank-6 is justified — the original rank-1 GE was lucky-seed inflation, not depth. Slightly below its shorter sibling (the long race adds tedium). Just above R20 production (3.73), below R8 replay (4.10) and the R19 ceiling.

### CLOSEST KNOWN-GAME ANALOG
R20 menger threshold-race family (long-race variant); externally a disc-counting territory race.

### KILLER FLAWS
- Long race (threshold 50) adds tedium without depth — endurance over horizon.
- Captures inert; ~1-ply per move; balance tuned not robust.

### BEST QUALITY
The density-beats-tempo lever (shared with the pod) is the only real positional content; the longer race gives more chances to express it but does not deepen it.

### MENGER STRUCTURAL CONTRIBUTION
Same region-density reading as the siblings; substrate matters, but the longer threshold just prolongs the same arithmetic.

### IMPROVEMENT IDEAS
**Single best change:** shorten the race (threshold ~30, max_turns ~100, i.e. become its sibling) — the long variant is strictly the worse one; depth is identical and engagement drops. This game's existence mainly serves to confirm the GE-inflation diagnosis.
Secondary:
- Add a live tactical layer (captures that swing the race) to justify the length.
- Fix helper komi display.
