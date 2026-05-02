# Run 19 Evaluation — team-1 — Game c3427a8ae42b

**Team ID:** team-1
**Game ID:** `c3427a8ae42b` (Carpet rank-3, GE 0.2783, ELO 2232.9)
**Substrate:** Sierpinski carpet (axis 9, 64/81 active, max_degree 4)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game c3427a8ae42b` (briefing: `briefing_carpet_rank3.md`).

---

## Phase 1 — Rule Comprehension

**Board / turn structure / actions.** Identical to carpet rank-1 and rank-2: 9×9 sierpinski carpet, 64 active cells, place-only, alternating, P1 first. Max 116 turns (longest of the 6 R19 games — broad time window).

**Capture (outnumber-2).** Identical to carpet rank-1. Same 2-for-1 sandwich economy.

**Propagation (influence, r=2, s=0.8371, d=0.6759).** **Non-default kernel.** Effective contributions:
- own: +0.84
- dist-1: +0.57 (vs +0.50 in rank-1; +13% stronger than default)
- dist-2: +0.39 (vs +0.25 in rank-1; +56% stronger than default)

The slow decay (0.68 vs 0.50) makes distance-2 cells nearly as strong as distance-1 cells. **The pilot's claim "clustering is much less critical" is partially correct but overstated** — see Phase 2 Game 3.

**Win (threshold-race > 25.112).** **16% lower than rank-1's 30.0**. Combined with wider-reach kernel, threshold reachable in fewer stones. Avg game length 27.2 plies vs rank-1's 32.2.

**Degeneracy check.**
- No soft violations.
- **Per-seed final-winrate volatility (0.0/0.5/1.0) is the concerning signal**: across 3 PPO training seeds, one converged to P1-wins-everything, one to balanced, one to P2-wins-everything. **Suggests the strategic surface has multiple local optima depending on training seed.** This is a balance instability the other 5 R19 games don't share.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run19_helper.py`.

### Game 1 — Mirror cluster baseline

Sequence: `0,8,2,6,18,26,20,24` (8 plies).

Plot:
- Standard 4-stone "diagonal cluster" mirror per rank-1.
- Move 8: both at +6.41 with 4 stones each. **Per-stone +1.60** (vs +1.50 in rank-1) — confirming the wider kernel pays off ~7% more for the symmetric-2-spaced cluster.
- Linear extrapolation: 13 stones × +1.60 = +20.8; 14 stones × +1.60 = +22.4. Threshold 25.1 reached at ~16 stones. **Mirror P1-wins at ply ~31** (P1's 16th stone).

Reflection: **Wider kernel makes mirror games modestly faster than rank-1 (+1.0 ply earlier on average) but doesn't change the structural P1-wins-mirror dynamic.** Per-stone gain is ~7% higher; threshold ~16% lower; net effect ~13% fewer plies to threshold.

### Game 2 — Sandwich attack (canonical outnumber-2)

The capture mechanic is identical to carpet rank-1, so I tested the canonical sequence (`0,9,2,1`) and verified P2 captures (0,0) at move 4. Trade economics match rank-1 exactly: 2-for-1 stone trade, ≈ 1-for-1 in influence (P2 attackers form a tight 2-stone cluster as side-effect).

### Game 3 — Cluster vs spread comparison (independent novelty test)

I designed an experiment to test the pilot's "spread-friendly" claim: P1 plays 4 stones at MAXIMUM spread (the 4 board corners (0,0), (8,0), (0,8), (8,8)) while P2 mirrors adjacent to each corner.

Sequence: `0,9,8,17,72,63,80,71` (8 plies).

Plot:
- P1 places at all 4 corners (cells 0, 8, 72, 80). P2 places adjacent to each corner ((0,1)=9, (8,1)=17, (0,7)=63, (8,7)=71).
- After ply 8: **P1 = 4 stones (corners) at +1.085; P2 = 4 stones (adjacent attackers) at +1.085.**
- **Per-stone P1: +0.27** (vs mirror cluster's +1.60).

Reflection: **Maximum spread is ~6× WORSE than mirror cluster, even with the wider kernel.** The pilot's framing "clustering is much less critical" is empirically overstated. The wider kernel pulls cluster vs spread closer (cluster bonus vs spread is ~7× in rank-1, ~6× here), but cluster still dominates dramatically.

**Independent finding**: the 4-corner spread configuration's per-stone score is +0.27 because each corner stone is 100% adjacent to a P2 attacker, so P1's own +0.84 contribution is reduced by P2's -0.57 dist-1 contribution. **The spread-friendly framing assumes no P2 interference; under P2 interference (which is the realistic case), spread is dominated by cluster regardless of kernel parameters.**

### Strategy guides

**P1 (offence/threshold push):** Cluster at corners, exactly as in carpet rank-1. The wider kernel + lower threshold means you need ~16 stones (vs ~14 in rank-1), reachable by ply ~31 under mirror. **Don't be fooled by the wider kernel's "spread-friendly" property** — under realistic P2 interference, cluster still beats spread by ~6×. The kernel parameters are a tuning, not a strategic shift.

**P2 (defence + offence):** Same as carpet rank-1. Sandwich war is the asymmetric counter. The wider kernel slightly increases the dist-2 contribution from P2's 2-stone cluster post-sandwich (+0.39 vs +0.25), making the post-sandwich cluster ~7% stronger. Net: sandwich war is marginally more favourable for P2 here than in rank-1. **But the per-seed seat-bias volatility (0.0/0.5/1.0 winrates) suggests this advantage may not be stably exploitable.**

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Same two as carpet rank-1 — cluster-and-race, sandwich-and-pivot. The wider kernel reduces but does NOT eliminate the cluster bonus. **Spread is still dominated by cluster under realistic P2 interference.** No new strategic branches.

**Counter-play.** Same family as rank-1.

**Short-term vs long-term.** Faster than rank-1 (~13-16 ply horizon vs ~14 in rank-1). Less long-term planning available.

**Emergent concepts observed.**
- Same primitives as carpet rank-1.
- **Reduced cluster-bonus penalty for spreading** is a real kernel-driven softening, but the magnitude (cluster ~6× better than far-spread) is still dominant.
- **Per-seed seat-bias volatility** as a balance signal — different PPO seeds learn different dominant strategies. Unique to this game among the 6.

**Does the carpet substrate matter?** Same conclusion as rank-1 — modest, not transformative.

**Does the propagation kernel matter?** **Less than in rank-1** because the wider kernel makes the kernel itself less differentiating: any 13-16-stone cluster reaches roughly the same +25 score. **The game converges to "place fast, race threshold" with reduced strategic variation.** This is what the pilot meant by "less differentiating", and it's roughly correct (modulo the "spread is still bad" finding from my Game 3).

**Capture-rule contribution.** Same as rank-1.

**First-mover advantage / seat balance.** Same P1 favour. **The PPO trained-vs-trained final winrate volatility (0.0, 0.5, 1.0 across 3 seeds) is concerning** — it suggests the game has multiple local optima where one seat dominates. **In a fair human competition, the seat bias might be 0.7/0.3 in either direction depending on opening choices.** This is a real balance defect not present in the other 5 R19 games (which all converged to ~0.500 across seeds).

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a **parameter variant** of carpet rank-1 — same family (outnumber + influence + threshold), different kernel parameters. Argument:

(a) Same family as rank-1: outnumber + influence + threshold-race on sierpinski carpet.
(b) **Non-default kernel (s=0.84, d=0.68)**. Slower decay creates "flatter, more diffuse" influence. Closer in feel to *Tumbleweed* (Mike Zapawa, 2020) which uses ranged influence on hex.
(c) **Lower threshold (25.1) and longer max-turns (116)** create a different speed regime. Faster mid-game tactics; broad time window for late-game maneuvers.
(d) Sierpinski carpet substrate — same novelty as rank-1.
(e) **Expert-transfer test**: same as rank-1 but the wider kernel makes the "cluster discipline" learning curve slightly easier — accessible to players unfamiliar with influence-game cluster geometry.

**Closest known-game analogue:** **A faster, more diffuse parameter variant of carpet rank-1.** Within the project corpus, this game is essentially a tuning of `ce3a09e05cef`'s rule blob.

**Comparison to R8's Connection Go (8/10 ceiling).** Same conclusion as rank-1. Different family. R19 carpet rank-3's wider kernel moves it slightly closer to the territorial "weight-everywhere" feel of Tumbleweed, but no closer to R8's connection-game family.

**Player rebuttal.**
- **Wider kernel + lower threshold is genuinely a different speed regime** (~30% faster than rank-1). This adds tactical accessibility but reduces strategic depth.
- **Per-seed seat-bias volatility is a genuine instability** that the other R19 games don't share. This is interesting from a fitness-metric perspective — possibly the game won evolution because lucky seeds gave it high GE, but the underlying balance is unstable.
- **What subtracts**: this is a parameter variant, not a structural innovation. Same family, slightly different kernel, same flaws.

**Novelty score (post-adversary):** **4/10.** Same band as rank-1, slightly lower because: (i) this is a kernel parameter variant, not a fresh combination, (ii) the "wider kernel" softening reduces strategic differentiation rather than adding it, (iii) the per-seed seat-bias volatility is a flaw, not a feature. Anchored against R17 mean 3.50.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game ID:** c3427a8ae42b
**Rules Summary:** Place stones on a 9×9 sierpinski carpet to accumulate wide-reach influence (s=0.84, d=0.68 — ±0.84/±0.57/±0.39 within graph-radius 2). Outnumber-2 captures fire when an enemy has ≥2 of your stones among its neighbours. First to >25.1 effective influence wins. Faster than rank-1 due to wider kernel + lower threshold.
**Substrate:** Sierpinski carpet, axis 9, 64/81 active, max_degree 4.
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no.
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 4** — Same depth-2 decision tree as carpet rank-1, with reduced cluster-discipline strictness due to wider kernel. Per-stone arithmetic still linear; tactical horizon shorter (~13-16 plies vs rank-1's ~14). **Below rank-1's 4** is identical because the kernel softening reduces strategic differentiation modestly. Below pilot's 4 is identical.

- **Emergent Complexity: 4** — Same primitives as rank-1 (sandwich, cluster reinforcement, hole-bottleneck). Wider kernel doesn't add new emergent vocabulary.

- **Balance: 3** — **Worse than rank-1's 4** because of per-seed seat-bias volatility. Mirror = P1 wins (same as rank-1). PPO trained-vs-trained final winrate distribution (0.0/0.5/1.0 across 3 seeds) suggests unstable balance. **Below pilot's 4** by 1, because I weight the seed-volatility more heavily.

- **Novelty (post-adversary): 4** — see Phase 4. Parameter variant of rank-1. Below pilot's 5 by 1.

- **Replayability: 3** — Faster games + reduced strategic differentiation = openings collapse faster than rank-1. Aligned with pilot's 3.

- **Overall "Would I play this again?": 3** — Once: yes, the wider-kernel speed regime is interesting to feel. Repeatedly: no — same strategic ceiling as rank-1 with sharper balance instability and shallower tactical surface. **Below pilot's 4** by 1, anchored against R17 mean 3.50.

### CLOSEST KNOWN-GAME ANALOG
**A faster, more diffuse parameter variant of carpet rank-1.** Within R19, this is the "low-strategic-discipline" carpet variant — accessible but shallow.

### KILLER FLAWS
- **Faster game = less depth** (intrinsic to wider kernel + lower threshold).
- **Per-seed seat-bias volatility** (final winrate range 0.0–1.0 across 3 PPO seeds) — unique to this game among the 6 R19 evaluated. **Suggests evolution may have selected this game for fitness-metric reasons (lucky-seed high GE) rather than structural quality.**
- **Mirror = P1 wins** (same as all R19 games).
- **Cluster still dominates spread by ~6×** under realistic P2 interference. The pilot's "spread-friendly" framing is partially overstated.
- **Parameter variant of rank-1** with no structural innovation. Same family, weaker version.

### BEST QUALITY
**The wider influence kernel makes the game more accessible.** A new player can place stones broadly (less strict cluster discipline) and still reach reasonable scores (+1.6/stone vs +1.5 in rank-1, modest improvement). **The lowest-skill-ceiling R19 game I've evaluated** — useful as a "training" game but not as an "exhibition" game.

### CARPET STRUCTURAL CONTRIBUTION
Same as rank-1 — modest. Estimate: −0.5 strategic-depth points if flattened to 9×9 grid.

### IMPROVEMENT IDEAS
**Single best change: pie rule** (same as cross-cutting verdict).

Secondary improvements:
- **Restore default kernel (s=1.0, d=0.5)** to match rank-1 — would lose the fast-pace property but gain strategic depth and possibly balance stability.
- **Increase threshold to 30** — matches rank-1, eliminates the speed-vs-depth tradeoff.
- **Investigate the per-seed volatility cause** — if the strategic surface has multiple local optima depending on seed, this is a fitness-metric weakness. R20 should consider: (i) testing balance with ≥10 PPO seeds before evolution to detect such instability, (ii) penalizing rule blobs with high per-seed winrate variance during fitness scoring.
- **Add a connection or territory secondary win condition** — purely additive — to add narrative tension. R8-family direction.

### Comparison to carpet rank-1 (parent family)

| Axis | Rank-1 (default kernel) | Rank-3 (wide kernel) | Delta |
|---|---|---|---|
| Strength | 1.00 | 0.84 | -16% |
| Decay | 0.50 | 0.68 | +36% |
| Threshold | 30.0 | 25.1 | -16% |
| Per-stone | +1.50 | +1.60 | +7% |
| Plies to threshold | ~28 | ~31 | +11% |
| Cluster vs far-spread bonus | ~6.5× | ~6× | -8% |
| Per-seed final WR variance | low | high (0.0/0.5/1.0) | concerning |
| Strategic Depth | 4 | 4 | tie |
| Overall | 4 | 3 | rank-1 better |

**Both rank-1 and rank-3 are in the same strategic family with different parameters.** Rank-3 is the faster, less-strict-cluster, more-balance-unstable variant. **Evolution kept the family alive in two parameter regimes**; rank-1 (crossover-derived from rank-2 + rank-3's neighbor seed) is the more refined version.

### Independent disagreement with pilot

| Score | Pilot | Team-1 | Delta |
|---|---|---|---|
| Strategic Depth | 4 | 4 | 0 |
| Emergent Complexity | 4 | 4 | 0 |
| Balance | 4 | 3 | -1 |
| Novelty | 5 | 4 | -1 |
| Replayability | 3 | 3 | 0 |
| Overall | 4 | 3 | -1 |

**Disagreements are on Balance and Novelty.** Balance: I weight the per-seed seat-bias volatility (0.0/0.5/1.0) more heavily than the pilot. Novelty: I treat this as a parameter variant of rank-1, not a meaningfully novel game. The "spread-friendly" claim from the pilot is partially overstated (spread is still dominated by cluster ~6×).

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-1_gamec3427a8ae42b.md`.*
