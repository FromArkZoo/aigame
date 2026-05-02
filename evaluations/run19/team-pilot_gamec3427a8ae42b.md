# Run 19 Evaluation — team-pilot — Game c3427a8ae42b

**Team ID:** team-pilot
**Game ID:** `c3427a8ae42b` (Carpet rank-3, GE 0.2783, ELO 2232.9)
**Substrate:** Sierpinski carpet (axis 9, 64/81 active, max_degree 4)
**Helper:** `eval_run19_helper.py --game c3427a8ae42b`

---

## Phase 1 — Rule Comprehension

**Board / Turn structure / Action space.** Same as carpet rank-1.

**Capture (outnumber-2).** Same as carpet rank-1.

**Propagation (influence, r=2, s=0.8371, d=0.6759).** Non-default. Effective kernel:
- own: +0.84
- dist-1: +0.57 (vs 0.50 in rank-1; **+13% stronger**)
- dist-2: +0.39 (vs 0.25 in rank-1; **+56% stronger**)

The slow decay (0.68 vs 0.50) makes distance-2 cells nearly as valuable as distance-1 cells. Clustering is much less critical — even spread stones reinforce strongly.

**Win (threshold-race > 25.112).** **16% lower than rank-1's 30.** Combined with the wider-reach kernel, threshold is reached with fewer stones. Avg game length 27.2 moves vs rank-1's 32.2.

**Degeneracy check.** No soft violations. The wider-reach kernel + lower threshold creates a faster, more diffuse-influence variant of the carpet family.

---

## Phase 2 — Strategic Play

### Game 1 — Symmetric corner-cluster mirror

Sequence: `0,8,2,6,18,26,20,24` (8 plies, partial).

Plot:
- Same opening as carpet rank-1.
- Move 8: both at +6.4 with 4 stones each. **Per-stone contribution +1.6** (vs +1.5 in rank-1) — confirming the wider kernel pays off slightly more for separated stones.

Reflection: **The wider kernel makes mirror games faster.** Fewer stones needed to reach threshold, so P1 wins by tempo even sooner than rank-1. Game length avg 27 moves means each side places ~13-14 stones — game over before late-game tactics matter much.

### Game 2 — Sandwich attack (same as rank-1)

Same dynamics as carpet rank-1: P2 sandwiches P1's corner stones via outnumber-2. Captured stones cleared, P2 builds 2-stone clusters as side-effect. Tested empirically with `0,9,2,1` — capture fires identically.

Reflection: **Capture mechanics unchanged from rank-1.** Same 2-for-1 trade with cluster-side-effect.

### Game 3 — Spread-and-race exploiting wide kernel

(Sketched analytically.)

The non-default kernel makes "spread" play viable for the first time among R19 carpet games. Placing stones at distance 2 still reinforces +0.39 per pair (vs +0.25 in rank-1). Strategy: occupy the 4 corners far apart; the resulting 4-stone spread already contributes ≈ 4×0.84 + small inter-stone terms ≈ +3.5, which would only be +4.0 if perfectly clustered. The penalty for spreading is smaller than rank-1's, so P1 has more opening flexibility.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Same two as rank-1, with **lower differentiation between cluster and spread** because the wider kernel reduces the cluster-bonus penalty for spreading.

**Counter-play.** Same family.

**Short-term vs long-term.** Faster game (27 moves avg). Less long-term planning available; ~13-14 ply horizon per side.

**Emergent concepts observed.**
- Same primitives as carpet rank-1.
- **Reduced cluster-bonus penalty** is a kernel-driven softening of the rank-1 strategic landscape.

**Does the carpet substrate matter?** Same conclusion as rank-1.

**Does the propagation kernel matter?** **Less than in rank-1.** The wider-reach kernel makes the kernel itself less differentiating: any 13-stone spread or cluster reaches roughly the same +25 score. **The game converges to "place fast, race threshold" with reduced strategic variation.**

**Capture-rule contribution.** Same. Captures are the only real balance mechanism.

**First-mover advantage / seat balance.** Same P1 favour. PPO trained-vs-random WR is 0.973 (high); but the per-seed final winrate distribution (0.0, 0.5, 1.0) suggests **seed-dependent seat bias** — some training seeds learn pro-P1 play, others pro-P2. Final-winrate volatility is concerning.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Largely the same as carpet rank-1: influence + outnumber + threshold-race on a fractal. The non-default kernel is a *parameter variant* of the same design family — not a structurally new game.

**Closest known-game analogue:** Same as rank-1. The kernel tuning makes this game closer in feel to *Tumbleweed* (which uses ranged influence on hex) than rank-1 (which is more cluster-focused).

**Comparison to R8's Connection Go (8/10 ceiling).** Same conclusion as rank-1. R8 is a different family (connection-driven). R19 carpet rank-3 is in the influence-threshold family with a wider kernel, which moves it closer in *feel* to broad territorial games but not closer to R8 specifically.

**Novelty score (post-adversary):** **5/10.** Same band as rank-1. The kernel parameters are a tuning, not a structural innovation.

---

## Phase 5 — Verdict

**Team ID:** team-pilot
**Game ID:** c3427a8ae42b
**Rules Summary:** Place stones on a 9×9 carpet to accumulate wide-reach influence. Captures fire by outnumber-2; first to >25.1 effective influence wins. Faster than rank-1 due to wider kernel + lower threshold.
**Substrate:** Sierpinski carpet, axis 9, 64/81 active, max_degree 4.
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no.
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 4** — **Below rank-1**. The wider kernel reduces strategic differentiation — cluster vs spread matters less. Faster game means less long-term planning. Tactical surface is narrower.
- **Emergent Complexity: 4** — Same primitives as rank-1, but less amplified due to faster pace.
- **Balance: 4** — Same mirror = P1 win. Concerning per-seed final winrate volatility (0.0/0.5/1.0) suggests seed-dependent seat bias not present in rank-1.
- **Novelty (post-adversary): 5** — Same as rank-1. Parameter variant.
- **Replayability: 3** — Faster games + reduced strategic differentiation = openings collapse faster than rank-1.
- **Overall "Would I play this again?": 4** — **Below rank-1 by 1 point.** The non-default kernel makes the game faster and shallower without adding novelty.

### CLOSEST KNOWN-GAME ANALOG
**A faster, more diffuse variant of carpet rank-1.** Within the project corpus, this game is essentially a parameter alternate of `ce3a09e05cef`.

### KILLER FLAWS
- **Faster game = less depth** (intrinsic to the kernel + threshold combination).
- **Per-seed seat-bias volatility** (final winrate range 0.0–1.0 across PPO seeds) suggests unstable balance.
- Same mirror = P1 win as the other carpet games.

### BEST QUALITY
**The wider kernel makes the game more accessible.** A new player can place stones broadly (less strict cluster discipline) and still build to threshold. This is the lowest-skill-ceiling R19 game I've evaluated.

### CARPET STRUCTURAL CONTRIBUTION
Same as rank-1: modest (~−0.5 depth if flattened).

### IMPROVEMENT IDEAS
**Single best change: pie rule** (same as all R19 games).

Secondary improvements:
- **Restore default kernel (s=1.0, d=0.5)** to match rank-1 — would lose the fast-pace property but gain strategic depth.
- **Increase threshold to 30** — matches rank-1, eliminates the speed-vs-depth tradeoff.
- **Examine why this kernel won at evolution** — likely the seed-bias volatility *helped* it pass C2 multi-seed averaging by sometimes giving high GE on lucky seeds. May indicate a fitness-metric weakness rather than a genuinely better game.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-pilot_gamec3427a8ae42b.md`.*
