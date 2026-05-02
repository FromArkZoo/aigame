# Run 19 Evaluation — team-2 — Game c3427a8ae42b

**Team ID:** team-2
**Game ID:** `c3427a8ae42b` (Carpet rank-3, GE 0.2783, ELO 2232.9)
**Substrate:** Sierpinski carpet (axis 9, 64 active cells / 81 grid positions, max_degree 4)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game c3427a8ae42b` (see `briefing_carpet_rank3.md`).
**Note:** Direct seed (c1 family) with non-default propagation params (s=0.84, d=0.68).

---

## Phase 1 — Rule Comprehension

**Board.** Identical to carpet rank-1 and rank-2: 9×9, 64 active cells, 17 holes. Same 4 max-degree-4 anchor cells at (2,2)=20, (2,6)=56, (6,2)=24, (6,6)=60.

**Turn structure.** Alternating, P1 first. **Max 116 turns** (longest of the 6 R19 games — 16% more than rank-1's 100).

**Action space.** 82 actions = 81 placements + 1 pass. Place-only.

**Capture (outnumber-2).** Identical to carpet rank-1.

**Propagation.** Influence, **r=2, strength=0.8371, decay=0.6759** — non-default. Effective kernel:
- own: +0.8371
- dist-1: +0.5658 (vs rank-1's +0.5)
- dist-2: +0.3825 (vs rank-1's +0.25)

**The slower decay makes distance-2 contributions worth ~68% as much as distance-1**, vs rank-1's 50%. Combined with the lower per-placement strength (0.84 vs 1.0), the kernel is "flatter and wider" — same total influence integral but spread over a larger area.

**Win condition.** Threshold-race > **25.112** — 16% lower than rank-1's 30.0. Combined with wider kernel, threshold is reached with fewer stones.

**Verified per-stone yield at 4-degree interior anchor (Game 1):**
- 5-stone plus cluster: **+13.30** (vs rank-1's +12.0). Per-stone avg +2.66.
- 4-corner spread (no adjacency): **+5.04** at 6 stones placed at (0,0)/(8,0)/(0,8)/(8,8) + 2 mid-edge cells. Per-stone avg +1.35 — **50% less than cluster**.

**The wider kernel modestly increases cluster yield but does NOT make spread strategically equivalent.** Cluster still strictly dominates by ~70% per stone.

**Degeneracy check.**
- No soft violations.
- The strength=0.84 + decay=0.68 combination produces non-integer scores; the threshold value 25.112 is a precision-floored value reflecting kernel-dependent calibration. Not a degeneracy.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run19_helper.py`.

### Game 1 — Mirror at the 4-degree interior anchor (full play-through)

Sequence: `20,60,11,69,21,51,19,61,29,59,12,52,28,68,2,58,18` (17 plies).

Plot:
- Plies 1-10: 5-stone plus clusters at (2,2) and (6,6). Both at +13.30 by ply 10.
- Plies 11-16: shell-2 expansion. Both at +24.53 by ply 16.
- **Ply 17 P1 plays (0,2)=18.** P1 score = +28.03 > 25.112 → **P1 wins.** P2 has 8 stones at +24.53; never gets a 9th turn.

**Mirror = P1 wins by 1 ply at 9-vs-8 stones** — at **ply 17, the fastest mirror end of any of the 6 R19 games I've evaluated.** Compare:
- carpet rank-1: ply 23
- carpet rank-2: ply 23
- carpet rank-3 (this game): **ply 17**
- menger rank-1: ply 25
- menger rank-2: ply 39
- menger rank-3: ply 19

The lower threshold (25.1) + wider kernel (+10% per cluster stone) compress the game most aggressively.

### Game 2 — P1 counter-sandwich at the 4-degree interior anchor

Sequence: `20,19,18` (3 plies).

Plot:
- P1 (2,2)=20 — interior anchor.
- P2 (1,2)=19 — sandwich attack.
- **P1 (0,2)=18 — counter-sandwich.** Outnumber-2 fires on (1,2): 2 P1 neighbours → captured. P2 = 0 stones.

**Counter-sandwich works identically to carpet rank-1.** Same mechanic; the kernel difference doesn't change capture economics.

### Game 3 — Novelty adversary: 4-corner spread strategy (does wider kernel pay off?)

Sequence: `0,8,72,80,2,6,74,78,18,26,54,62` (12 plies — pure spread, no clustering).

Plot:
- P1 plays 6 stones at distance ≥2 from each other: (0,0), (0,8), (2,0), (2,8), (0,2), (0,6) — all left half.
- P2 mirrors right half: (8,0), (8,8), (6,0), (6,8), (8,2), (8,6).
- After ply 12: P1 = +8.08 (6 stones), P2 = +8.08 (6 stones).

**Per-stone average +1.35** — vs cluster's +2.66 = **50% less efficient**. The pilot's claim that "the wider kernel makes spread viable" is misleading: spread is *less suboptimal* on rank-3 than rank-1 (where spread would yield ~+1.0/stone), but cluster still strictly dominates. P1 spreading would still lose to P1 clustering by a factor of 2 in stone-efficiency.

The wider kernel doesn't open new strategies; it just slightly softens the cluster-bonus penalty for suboptimal play.

### Strategy guides

**P1 (offence/threshold push):** Same as rank-1 — anchor at one of the 4 max-degree-4 cells, build the 5-stone plus cluster (yields +13.30 here vs +12.0 in rank-1), expand to shell-2 cells. Threshold reached at just 9 stones / 17 plies — the fastest of all R19 games.

**P2 (defence + threshold contest):** Mirror loses by 1 ply (Game 1, faster than rank-1). Sandwich is a losing line via counter-sandwich (Game 2). Spread is a losing line vs cluster (Game 3). **No winning P2 strategy under perfect P1 play.**

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** **Fewer than rank-1.** The wider kernel reduces the cluster-vs-spread differentiation slightly, but the strategic skeleton is otherwise identical to rank-1. Two strategies, both for P1:
1. Interior 4-degree anchor cluster (best).
2. Corner anchor cluster (slightly worse but still wins under mirror).

P2 has no winning strategy under best P1 play.

**Counter-play.** Same as rank-1 — counter-sandwich is universal, sandwich attack is a losing line.

**Short-term vs long-term.** **Shortest game horizon of any R19 carpet game.** Mirror ends at ply 17; threshold reached at 9 stones. Tactical horizon ~5 plies, strategic horizon ~3 plies (anchor selection). Less depth than rank-1 by ~1 point.

**Emergent concepts observed.**
- Same primitives as rank-1: cluster + sandwich + counter-sandwich + threshold race.
- **Reduced cluster-spread differentiation** due to wider kernel.
- **No new emergent concepts** beyond rank-1.

**Does the carpet substrate matter?** Same as rank-1: ~0.5 point of substrate-driven novelty over a flattened 9×9 grid. The faster game length means substrate effects play out less.

**Does the propagation kernel matter?** **Differently than in rank-1.** The wider, flatter kernel:
- Slightly reduces the cluster bonus (cluster is +10% better, vs rank-1 where cluster is ~50% better than spread).
- Softens the hole-bottleneck penalty (distance-2 reach across a hole-vicinity costs less).
- Compresses the game length by ~30%.

**Capture-rule contribution.** Same as rank-1. Captures fire only in early plies during sandwich exchanges.

**First-mover advantage / seat balance.** Same structural P1-by-1-ply advantage. **Per-seed final winrate distribution {0.0, 0.5, 1.0} across 3 PPO seeds** — concerning. The high variance suggests PPO didn't converge to a stable equilibrium. Two readings: (a) the strategic surface is genuinely volatile; (b) the wider kernel introduces noise that destabilises learned policies. **Either way, this is the WORST-trained game of the 6 R19 games** despite its top-3 placement.

The pilot's note about "seed-dependent seat bias" is real and worth flagging.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a **parameter variant** of carpet rank-1 with non-default kernel params. The structural family (outnumber + influence + threshold) is identical.

(a) **Threshold-race influence games** — same family.

(b) **Outnumber-2 capture** — identical mechanic to rank-1.

(c) **The combination "outnumber + influence + threshold"** — identical to rank-1, with parameter variation.

(d) **Sierpinski carpet substrate** — identical to rank-1.

(e) **Wider kernel (s=0.84, d=0.68)** — a tuning variant. Kernel parameters are within the same generator's parameter space; this is not a structural innovation, just a different point in parameter space.

(f) **Comparison to R8's Connection Go (8/10).** Same as rank-1: different family, different strategic mechanism.

(g) **Expert-transfer test.** Identical to rank-1 — Go + Othello + Hex player understands rules in 5-10 minutes.

**Closest known-game analogue:** **A faster, more diffuse parameter variant of carpet rank-1.** Within the project corpus, **carpet rank-1 (`ce3a09e05cef`) is the same game with default kernel parameters.** The two differ only in s/d/threshold values.

**Player rebuttal (P1 + P2).**
- The non-default kernel does change the per-stone yield economics, but the strategic skeleton (cluster + counter-sandwich) is unchanged.
- The wider kernel doesn't open new strategies — just slightly softens existing differentials.
- Subtracting from novelty: this is a parameter sibling of carpet rank-1, not a structurally new game. Evolution produced 3 carpet games that are: rank-1 (crossover, default kernel), rank-2 (custodian, same kernel), rank-3 (outnumber, non-default kernel). Only rank-2 is structurally distinct (custodian instead of outnumber). Rank-3 is a tuning variant.

**Novelty score (post-adversary):** **3/10.** Below rank-1 (4) by 1 because: (a) this is explicitly a parameter variant of rank-1 with no structural novelty, (b) the wider kernel doesn't produce new strategic patterns, (c) the per-seed PPO instability suggests the parameter tuning is on a noisy ridge of the fitness surface, not a stable improvement. **The lowest novelty score I've assigned across the 6 R19 games.**

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game ID:** c3427a8ae42b
**Rules Summary:** Place stones on a 9×9 Sierpinski carpet (64 of 81 cells active) to accumulate influence on cells you own. Each placement adds ±0.84 to itself, ±0.57 to active 1-neighbours, ±0.38 to active 2-neighbours; an enemy stone is removed if it has ≥2 of your stones among its active neighbours when you place. First to >25.1 effective influence wins.
**Substrate:** Sierpinski carpet, axis 9, 64/81 active, max_degree 4.
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no.
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 3** — **Below rank-1 (4)** because the faster game (17-ply mirror end) and the slightly-softer cluster bonus reduce the strategic surface. Same primitives as rank-1, less expressed. Equal to pilot's 4 minus 1 for my finding that the spread is still suboptimal (no real new strategy from wider kernel).

- **Emergent Complexity: 4** — Same primitives as rank-1 with reduced amplitude. Same as pilot's 4.

- **Balance: 3** — Mirror = P1 wins by 1 ply (verified Game 1, the fastest mirror end across R19). Counter-sandwich universal (Game 2). **Per-seed PPO winrate volatility {0.0, 0.5, 1.0}** — most volatile training of the 6 games. Same as pilot's 4 minus 1 because the volatility suggests structural balance issues, not just learned counter-strategies.

- **Novelty (post-adversary): 3** — **Below rank-1 (4) by 1** because this is explicitly a parameter variant of rank-1 with no structural innovation. Lowest novelty score I've assigned across R19.

- **Replayability: 3** — Faster game = openings collapse faster = less position variety. Same as pilot's 3.

- **Overall "Would I play this again?": 3** — **The lowest overall score I've assigned across R19.** The game is a less-interesting parameter variant of rank-1 with shorter games and PPO training instability. Anchored against R17 mean (3.50): at floor. Same as pilot's 4 minus 1 because I find the parameter-variant nature less novel than the pilot did.

### CLOSEST KNOWN-GAME ANALOG
**A faster, more diffuse parameter variant of carpet rank-1.** Within the project corpus, this is essentially the same rule set as `ce3a09e05cef` with non-default kernel parameters. Outside the corpus, similar to a fast Tumbleweed variant.

### KILLER FLAWS
- **Mirror = P1 wins by 1 ply at ply 17** — the fastest mirror end of any R19 game. Less time for strategy to develop.
- **Per-seed PPO winrate volatility {0.0, 0.5, 1.0}** — concerning. Either the strategic surface is genuinely volatile, or the wider kernel introduces noise that destabilises learned policies. Worst-trained of the 6 R19 games.
- **Parameter variant of rank-1, not structurally new.** Evolution produced this as a kernel-parameter exploration of the same family rank-1 explores. The R19 carpet top-3 contains 1 distinct family (custodian, rank-2) and 2 parameter variants (rank-1 and rank-3, both outnumber).
- **Wider kernel softens cluster-bonus without opening new strategies.** Spread is still 50% less efficient than cluster; the kernel change just reduces the penalty for suboptimal play.

### BEST QUALITY
**The fastest game of any R19 evaluated** (mirror ends at ply 17). This is a feature for accessibility and a bug for depth. A new player can play and finish in ~30 seconds; a veteran will find it shallow because the game ends before complex tactics develop.

### CARPET STRUCTURAL CONTRIBUTION
**Same as rank-1, slightly reduced.** The wider kernel makes the carpet's hole-bottleneck effect smaller (distance-2 routing across holes is partially compensated by wider reach). Estimated contribution: ~0.4 point of depth, ~0.7 point of novelty over a flattened 9×9 grid. **Below rank-1's contribution by ~0.1.**

### IMPROVEMENT IDEAS
**Single best change:** **Restore default kernel (s=1.0, d=0.5)** — would revert to carpet rank-1's parameter regime and remove the redundancy of having two outnumber-based carpet games in the top-3. The non-default kernel doesn't add anything that justifies its presence in the top-3.

Secondary improvements:
- **Pie rule** (universal R19 recommendation).
- **Increase threshold to 30** to extend the game length and let strategic surface develop more.
- **Investigate the PPO winrate volatility** — the {0.0, 0.5, 1.0} per-seed distribution is a real signal. Either this game has actual strategic instability that the others don't, or the kernel-parameter combination is in a noisy region of the GE fitness landscape. **The R19 evolution may have rewarded the lucky-seed GE over the structurally better game** — a fitness-metric weakness worth flagging for R20.

### Notes on the gen-8 ranking
The pilot's note about "seed-dependent seat bias possibly inflating fitness" is worth amplifying. **The R19 evolution may have promoted this game to top-3 for the wrong reasons** — high GE on lucky seeds rather than genuine strategic improvement over rank-1. R20 should consider:
- Higher per-game seed counts (5-7 instead of 3).
- Robust fitness (median rather than mean across seeds).
- Penalising games with high per-seed winrate variance.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-2_gamec3427a8ae42b.md`.*
