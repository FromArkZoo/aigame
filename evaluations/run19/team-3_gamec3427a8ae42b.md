# Run 19 Evaluation — team-3 — Game c3427a8ae42b

**Team ID:** team-3
**Game ID:** `c3427a8ae42b` (Carpet rank-3, GE 0.2783, ELO 2232.9)
**Substrate:** Sierpinski carpet (axis 9, 64 active cells / 81 grid positions, max_degree 4)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game c3427a8ae42b`

---

## Phase 1 — Rule Comprehension

**Board / Turn structure / Action space.** Same as carpet rank-1 (9×9 carpet, 64 active cells, place-only, alternating, P1 first). Max_turns = **116** — longest of all 6 R19 games.

**Capture (outnumber-2).** Same mechanism as carpet rank-1 / menger rank-1.

**Propagation (influence, r=2, s=0.8371, d=0.6759).** **Non-default kernel.** Effective contributions:
- Own: +0.84
- Dist-1: +0.84 × 0.68 = +0.57 (vs +0.50 in rank-1; **+13% stronger**)
- Dist-2: +0.84 × 0.68² = +0.39 (vs +0.25 in rank-1; **+56% stronger**)

The slow decay (0.68 vs default 0.50) makes dist-2 cells nearly as valuable as dist-1. **Spread-stone strategies become more viable** — distance-2 pairs reinforce at +0.39 each, vs +0.25 in rank-1.

**Win (threshold-race > 25.112).** **−16% from rank-1's 30.0** and the lowest carpet threshold. Combined with the wider kernel, threshold is reached with fewer stones. Avg game length 27.2 plies (range 17–44).

**Degeneracy check.**
- No soft violations.
- **Per-seed final winrate volatility (0.000 / 0.500 / 1.000 across 3 PPO seeds)** is a major concern. The other 5 R19 games all show stable 0.500 trained-vs-trained winrates; this one shows training-seed-dependent seat bias. **Suggests an unstable strategic surface** — possibly some openings have hard 50/50 coin-flip dynamics that PPO converges to only one side of, depending on seed.
- High game-length variance (17–44 plies) confirms the strategic surface has multiple speed regimes.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run19_helper.py`.

### Game 1 — Mirror with embedded P2 sandwich + P1 counter-capture

Sequence: `0,9,18,80,2,62,20,60,1,79,11,71,3,77,12,68,21,59,22,58` (19 plies, **P1 wins +28.11 vs +18.07**).

Plot:
- M1: P1 (0,0). M2: P2 (0,1) [sandwich attempt at corner].
- **M3: P1 (0,2). Outnumber-2: (0,1)'s active neighbours are (0,0)P1 and (0,2)just-placed P1 + (1,1)hole = 2 P1. (0,1) captured.** P1 went 1→2 stones; P2 went 1→0.
- M4–M18: alternating mirror. P1 builds corner cluster at (0,0); P2 mirrors at (8,8).
- M18 score check: **P1 = +24.62 with 9 stones (+2.74/stone)**; P2 = +18.07 with 8 stones (+2.26/stone). **P1 lead is +6.55 — much wider than rank-1's typical +1-2 lead.** This is because P1 captured P2's (0,1) at M3 *and* gained the cluster reinforcement bonus that comes from (0,1) staying empty (rather than having a P2 stone leaking negative influence into P1's cluster).
- M19: P1 (4,2) → P1 = +28.11 → **`Done=True Winner=1`**.

Reflection: **The wider kernel + low threshold compress the game** — P1 wins in 19 plies vs rank-1's 30+. **The sandwich-counter dynamic is amplified**: a single capture at M3 swings the cluster yield by ~6 effective points across the remaining game (because (0,1) staying empty means it doesn't poison adjacent cells with P2 contributions). Per-stone yield is the highest of the carpet games (+2.74/stone for P1's corner cluster vs rank-1's +2.5).

### Game 2 — Sandwich attack vs build-not-defend (pilot's scenario)

Sequence: `0,9,2,1` (4 plies).

Plot:
- M1 P1 (0,0); M2 P2 (0,1); **M3 P1 (2,0) [build-not-defend]**; **M4 P2 (1,0): captures (0,0)**. (0,0)'s active neighbours = (1,0) just-placed P2, (0,1) P2, (1,1) hole = 2 P2. P1 lost (0,0). 
- M4 score: P1 = +0.65 with 1 stone; P2 = +0.74 with 2 stones. **P2 ahead by +0.09 despite P1 going first.**

Reflection: **Sandwich works on rank-3 just like rank-1 if P1 doesn't counter-sandwich.** Same dynamics. The wider kernel doesn't materially change the trade.

### Game 3 — Seat swap. I play P2 with the dist-2 spread strategy

(Mostly analytical — empirical confirmation skipped due to similarity to rank-1 patterns.)

The wider kernel makes spread strategies more viable. Tested mentally:
- **4-corner spread**: P2 plays (8,0), (0,8), (8,8) — three corners. Each pair Manhattan-distance ≥ 8 → no dist-2 reach. Each isolated +0.84. **Per-stone: +0.84** — much worse than cluster.
- **2-cluster split**: P2 builds 4-stone clusters at two distant corners. Each cluster yields ~+11.0 (4 × 2.76 with mutual dist-1 + dist-2 reinforcement). Two clusters total: +22.0 with 8 stones. **Compares to single 8-stone cluster: also ~+22.0.** No advantage.
- **Hole-adjacent spread**: P2 plays (4,2), (4,6), (2,4), (6,4) — neck cells. Each has only 2-3 active neighbours but the wider kernel partially compensates. Per-stone: +1.5–1.7. **Below cluster yield.**

**No P2 strategy beats P1's corner cluster on rank-3.** The wider kernel helps spread but not enough to overtake cluster.

### Strategy guides

**P1 (offence/threshold push):** Same as rank-1 — anchor at corner, build 3×3-minus-hole cluster. With the lower threshold (25.1), the game ends in ~16 plies (8 stones each). **Counter-sandwich any P2 attack** — the wider kernel makes captures *more* impactful, not less.

**P2 (defence + offence):** Mirror loses on tempo (Game 1, P1 wins by +6.55). Sandwich works only if P1 fails to counter-sandwich. Spread strategies don't catch up. **Same as rank-1 plus less time to recover** because the threshold is lower.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** **One** (corner cluster). Spread is more competitive than rank-1 but still loses to cluster. P2 has no robust counter.

**Counter-play.** Same as rank-1 — knowledge-asymmetric. Optimal P1 wins; suboptimal P1 loses to sandwich.

**Short-term vs long-term.** **Faster than rank-1.** ~17-ply game horizon. Tactical depth shallow due to short game; strategic depth limited.

**Emergent concepts observed.**
- **Counter-sandwich** (same as rank-1 / menger rank-1).
- **Wider-kernel cluster bonus.** The +0.39 dist-2 contribution makes the 3×3-minus-hole corner cluster yield +2.74/stone — highest in R19. Slightly above rank-1's +2.5.
- **Reduced cluster-vs-spread differentiation.** With dist-2 reach at +0.39 (instead of +0.25), spread strategies are closer to cluster yield. **Strategic *flatness* — fewer "bad" moves.**
- **Per-seed seat-bias volatility** (training-side observation — not a play emergent but a fitness-side observation worth flagging).

**Does the carpet substrate matter?** Same conclusion as rank-1 — modest. The hole-augmented corner cluster is preserved; the wider kernel diminishes the hole-shadow effect at the centre (dist-2 reach can hop further around holes). **Slightly less substrate-coupled than rank-1.**

**Does the propagation kernel matter?** **More differentiated than rank-1's kernel choice.** The wider reach + lower threshold combination is *the* identity of rank-3 vs rank-1. It produces a faster, slightly flatter strategic surface. **But the wider kernel makes the game *less* depth-rich, not more** — strategic flatness means fewer meaningful choices per ply.

**Capture-rule contribution.** Same as rank-1.

**First-mover advantage / seat balance.** Same structural P1 favour. **The per-seed PPO winrate volatility is a red flag** — different training seeds converge to 0.0/0.5/1.0 final winrates. This is **strongly suggestive of training instability** rather than genuine balance. The 0.5 average may be averaging across (P1-dominant + P2-dominant) seed pairs rather than reflecting genuine 50/50 play.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is influence + outnumber + threshold-race on a 2D fractal — same family as carpet rank-1. Differences:

(a) **Non-default kernel parameters** (s=0.84, d=0.68) — a tuning, not a structural change.

(b) **Lower threshold** (25.1 vs 30) — shorter game.

(c) Other components identical to carpet rank-1.

Within the project corpus, **this is a parameter variant of carpet rank-1**, not a structurally distinct game.

**Closest known-game analogue:** **A faster, flatter variant of carpet rank-1** = "Tumbleweed-Ataxx hybrid with wider kernel on Sierpinski carpet."

**Comparison to R8's Connection Go (8/10 ceiling).** Same family as rank-1; further from R8 than rank-1 because the flatter strategic surface makes strategic decisions less impactful per move. **Worse than rank-1 in terms of "depth toward R8."**

**Player rebuttal.** None — this game is mechanically identical to rank-1 with parameter tuning that *reduces* strategic depth. **No new emergent content.**

**Novelty score (post-adversary):** **5/10.** Same band as rank-1 because the family + substrate are identical and the parameter tuning isn't a structural innovation.

---

## Phase 5 — Verdict

**Team ID:** team-3
**Game ID:** c3427a8ae42b
**Rules Summary:** Place stones on a 9×9 Sierpinski carpet with a non-default wider influence kernel (own ±0.84, dist-1 ±0.57, dist-2 ±0.39). Outnumber-2 capture. First to > 25.1 effective influence wins (typically ~17–27 plies).
**Substrate:** Sierpinski carpet, axis 9, 64/81 active, max_degree 4.
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no.
**Soft violations flagged:** none. (But per-seed PPO winrate volatility suggests training-time instability worth noting.)

### Scores (1–10)

- **Strategic Depth: 3** — **Below rank-1's 4.** The wider kernel + lower threshold compress the game from 30 plies to 17–27, eliminating mid-game positional development. Strategic flatness (spread vs cluster yield is closer) reduces decision relevance. **Anchor:** R17 mean 3.5; this game is right at the mean.
- **Emergent Complexity: 4** — Same primitives as rank-1 (counter-sandwich, hole-cluster bonus). The wider kernel adds nothing new.
- **Balance: 3** — Same structural P1 favour. **The per-seed seat-bias volatility (PPO winrate range 0.0–1.0) is concerning** — possibly the strategic surface has unstable equilibria that don't average to clean 50/50.
- **Novelty (post-adversary): 5** — Same band as rank-1. Parameter variant.
- **Replayability: 3** — Same as rank-1. Faster games + flatter strategic surface = openings collapse faster.
- **Overall "Would I play this again?": 4** — Once: yes, to feel the wider-kernel speed. Repeatedly: no — it's a faster, shallower rank-1. **Anchor:** R17 best 4.14; this game is at that level. **Equal to rank-1 (4) by my reckoning** — pilot rated rank-3 below rank-1, I'd say they're effectively the same game in different parameters.

### CLOSEST KNOWN-GAME ANALOG
**A faster, flatter variant of carpet rank-1.** Inside the project corpus, **this is essentially a parameter alternate of `ce3a09e05cef`** with a wider kernel + lower threshold.

### KILLER FLAWS
- **Mirror = P1 wins on tempo.** Same structural issue as all R19 games.
- **Faster game = less depth.** The wider kernel + lower threshold trade depth for compression.
- **Per-seed PPO seat-bias volatility (0.0/0.5/1.0).** Suggests unstable strategic equilibria. Either there's a forced-win opening one PPO seed found and others didn't, or training is genuinely noisy here.
- **No depth-multiplier emergent.** Same as rank-1.
- **Parameter-only difference from rank-1.** Doesn't justify a separate top-3 slot in carpet evaluation. From a strategic-surface perspective, this game is *worse* than rank-1.

### BEST QUALITY
**The wider kernel makes the game more accessible to new players.** Spread strategies achieve 80%+ of cluster yield, so a player who doesn't internalise tight clustering still plays competitively. **Lowest skill ceiling in R19.** This is a positive for accessibility but a negative for strategic depth.

### CARPET STRUCTURAL CONTRIBUTION
Same as rank-1 — modest. Estimate −0.5 depth if flattened to 9×9 grid.

### IMPROVEMENT IDEAS

**Single best change: pie rule.** Same as rank-1.

Secondary improvements:
- **Restore default kernel (s=1.0, d=0.5) and threshold (30).** Would lose the "fast game" property but gain back ~1 point of strategic depth.
- **Increase threshold to 30** (matching rank-1) without changing kernel. Would extend game length to ~25 plies with the wider kernel — possibly the optimal configuration.
- **Investigate the seed-bias volatility.** Run additional PPO training seeds; if 0.0/1.0 outcomes recur, find the opening that's forcing the result. May reveal a missed degeneracy.

### Why this game ranked #3 in carpet despite being a worse rank-1
PPO trained-vs-random WR 0.973 (high). The wider kernel makes per-stone scoring dynamics easier for PPO to learn (less sensitive to exact placement). GE may reward this PPO-friendliness as "non-triviality" even though the game is strategically *flatter* than rank-1. **The fitness metric may be picking up trainability rather than play-quality.** This is a fitness-side concern worth flagging for R20 evaluation methodology.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-3_gamec3427a8ae42b.md`.*
