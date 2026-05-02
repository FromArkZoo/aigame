# Run 19 Evaluation — team-4 — Game c3427a8ae42b

**Team ID:** team-4
**Game ID:** `c3427a8ae42b` (Carpet rank-3, GE 0.2783, ELO 2232.9)
**Substrate:** Sierpinski carpet, axis 9, 64 active cells / 81 grid positions, max_degree 4 (effective 2–4).
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game c3427a8ae42b` (see `briefing_carpet_rank3.md`).

---

## Phase 1 — Rule Comprehension

**Board / Turn / Action.** Same 9×9 sierpinski carpet as carpet rank-1 and rank-2.

**Capture (outnumber-2).** Same mechanic as carpet rank-1. Engine ignores the threshold parameter? No — for outnumber, threshold *is* used (`friendly_count >= threshold` in engine_v2.py:558). Threshold=2 means the standard outnumber-2 capture.

**Propagation.** Influence, r=2, **strength=0.8371, decay=0.6759** — non-default. Effective per-placement contributions:
- own cell: +0.84 (vs +1.0 in rank-1)
- distance-1: +0.57 (= 0.84 × 0.68; vs +0.50 in rank-1, **+13% stronger**)
- distance-2: +0.38 (= 0.84 × 0.68²; vs +0.25 in rank-1, **+52% stronger**)

**Net effect:** stones reinforce each other more strongly at distance, less at the placed cell. The kernel is "flatter and wider" — clustering still helps but spreading is also viable.

**Win.** Threshold-race > **25.112** (16% lower than rank-1's 30.0). Max turns = 116.

**Other rules.** `needs_ko_rule = True`. Super-ko active.

**Degeneracy check.**
- No soft-rule violations flagged.
- The non-default kernel (strength<1, decay>0.5) is the most distinctive parameter combo of the 6 R19 games. Its strategic effect is "slightly more diffuse, slightly faster" — kernel tuning, not a new mechanic.
- The high variance in PPO trained-vs-trained final winrate (0.000, 0.500, 1.000 across seeds) is concerning — suggests the strategic surface has multiple local optima that different training seeds find. Not necessarily a balance flaw, but a stability flaw.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run19_helper.py`.

### Game 1 — Interior cluster mirror (kernel-pace calibration)

Sequence: `20,60,11,69,2,78,18,62,29,51` (10 plies).

Plot:
- Same opening line as my carpet rank-1 Game 1: P1 at (2,2), (2,1), (2,0), (0,2), (2,3); P2 mirrors at (6,6) etc.
- After 10 plies (5 stones each): both at +9.87. **Per-stone gain ~+1.97** (vs rank-1's ~+2.0). Slightly *less* per-stone than rank-1 because the lower strength (0.84) reduces own-cell contribution more than the higher decay (0.68) restores distance-2 reach.
- Threshold 25.1 / per-stone 1.97 → ~13 stones each → game ends ~ply 25.

Reflection: **The kernel tuning makes rank-3 marginally slower per stone but the lower threshold compensates.** Net game length is similar to rank-1 (~25–30 plies) — the briefing's "faster" framing is approximately correct in moves-to-threshold terms. The strategic surface is *very similar* to rank-1's; the differentiation is in cluster-vs-spread payoffs at distance 2 (here +0.38 mutual reinforcement vs rank-1's +0.25).

### Game 2 — P2 sandwich + multi-corner attack + P1 counter-sandwich

Sequence: `0,9,38,1,46,18,2,11,20,3,2` (11 plies).

Plot:
- Plies 1–4: P1 (0,0); P2 (0,1); P1 (2,4); P2 (1,0) — captures (0,0). Identical to carpet rank-1 Game 2.
- Plies 5–8: P1 (1,5); P2 (0,2) — extends P2 cluster; P1 (2,0) builds own; P2 (2,1) — captures (2,0). P1=2, P2=4 after 8 plies. P2 leads +3.36 vs P1 +2.44.
- Ply 9–10: P1 (2,2) builds adjacent to (2,1)=P2 — but (2,1) only has 1 P1 neighbour ((2,2)=just placed), so no capture. P2 (3,0) extends.
- **Ply 11: P1 plays (2,0)** — replays the captured cell. (2,0)'s neighbours: (1,0)=P2, (3,0)=P2, (2,1)=P2 — 3 enemy neighbours. Outnumber check fires: for (2,1), its P1 neighbours are (2,0)=just placed and (2,2)=P1 = **2**. ≥2 → **(2,1) captured!**
- After ply 11: P1 has 4 stones (regained (2,0), captured (2,1)), P2 has 4 stones (lost (2,1)). Score P1 +4.60, P2 +2.62. **P1 has reversed the deficit via counter-sandwich.**

Reflection: **Counter-sandwich works on carpet rank-3, identical to my menger rank-1 finding.** The pilot didn't test counter-sandwich on this game — it works whenever the placer has a nearby supporting stone (here (2,2)). This is a real strategic resource that the pilot's "faster and shallower" framing under-credits.

### Game 3 — Spread-vs-cluster comparison (sketched + 8-ply demo)

Sketch + partial demo. Under rank-3's flatter kernel:
- 4-stone tight cluster (e.g., (2,2), (2,1), (2,3), (3,2)): own contributions = 4×0.84 = 3.35. Mutual reinforcement = 6 distance-1 pairs × 0.57 = 3.42. Plus distance-2 reinforcement among the L-shape = small extra. Total ~+7.5–8.0.
- 4-stone spread (e.g., (0,0), (8,0), (0,8), (8,8) — all corners): own contributions = 4×0.84 = 3.35. Distance-2 reinforcement: corners are far apart (distance >> 2), no inter-stone reinforcement. Total ~+3.35.

Cluster still pays off ~2× over spread. **The pilot's framing of "spread becomes viable" is partial** — the spread is *less penalised* than rank-1, but cluster is still strictly better. Strategic differentiation is reduced but not erased.

### Strategy guides

**P1 (offence/threshold push):** Same playbook as carpet rank-1. Anchor + chain + race. The wider kernel lets you tolerate slightly looser cluster shapes if needed (e.g., one hole in your chain costs less here than in rank-1).

**P2 (sandwich-and-pivot):** Same as carpet rank-1. The sandwich-as-cluster-builder works identically. Counter-sandwich threats from P1 require the same liberty arithmetic.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Same two as carpet rank-1, with slightly reduced cluster-vs-spread differentiation. Counter-sandwich is available identically.

**Counter-play.** Real, same as carpet rank-1. **Counter-sandwich works** (verified Game 2 ply 11). Pilot's analysis didn't probe this.

**Short-term vs long-term.** Same horizon as rank-1. Slightly faster game in moves-to-threshold but similar 4–6 ply tactical horizon and ~10-ply strategic horizon.

**Emergent concepts observed.**
- All carpet rank-1 emergents (sandwich-as-cluster, replay-as-recovery, hole-edge resistance, counter-sandwich).
- **Reduced cluster-vs-spread differentiation.** The +52% stronger distance-2 reinforcement makes spread play more viable (but still inferior to cluster). Strategic palette is slightly narrower because the optimal play range is narrower.

**Does the carpet substrate matter?** Same modest contribution as rank-1.

**Does the propagation kernel matter?** **More than rank-1, in the wrong direction.** The flatter kernel reduces strategic differentiation between cluster shapes, narrowing the decision space. This is a kernel choice that *reduces* depth, contradicting the rank-1 kernel's optimal tuning.

**Capture-rule contribution.** Same as rank-1. Outnumber-2 + super-ko + counter-sandwich. The Pyrrhic-flip dynamic from custodian (rank-2) is *absent* here because outnumber clears stones, not flips them.

**First-mover advantage / seat balance.** Same structural P1 favour. **PPO trained-vs-trained per-seed final winrate (0.000, 0.500, 1.000) is alarming** — indicates strong seed-dependent local optima. Pilot read this as instability; I agree this is a real concern. The game's strategic surface may have multiple "basins" that PPO sometimes escapes from, sometimes doesn't.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Influence + outnumber + threshold-race + super-ko on a 2D Sierpinski carpet, with non-default flatter kernel.

(a) **Influence + outnumber + threshold** — same family as carpet rank-1 and menger ranks 1–2.
(b) **Flatter-kernel parameters** are a tuning, not a new mechanic. The strategic feel is the same as rank-1 with slightly different per-shape payoffs.
(c) **Sierpinski carpet substrate** — same as rank-1.
(d) **Super-ko on outnumber** — same as all R19 games.

**Closest known-game analogue:** **A flatter-kernel parameter variant of carpet rank-1.** Within R19, this game is essentially the rank-1 family with parameters tuned for less cluster-discipline. No structural differentiation.

**Comparison to R8's Connection Go (8/10).** Same family-distance as carpet rank-1. R8 has connection win + custodian; this has threshold + outnumber. Different families.

**Player rebuttal.**
- **Counter-sandwich works** (verified Game 2 ply 11) — adds a recovery primitive that pilot didn't credit.
- **Substrate + super-ko + counter-sandwich** is consistent with all R19 outnumber games — same family-shared depth.
- Subtracts: the flatter kernel reduces strategic differentiation (less cluster-vs-spread tension); the seed-dependent winrate volatility suggests strategic instability.

**Novelty score (post-adversary):** **5/10.** Same as pilot. Family-shared with carpet rank-1; kernel tuning isn't a structural innovation.

---

## Phase 5 — Verdict

**Team ID:** team-4
**Game ID:** c3427a8ae42b
**Rules Summary:** Place stones on a 9×9 Sierpinski carpet to accumulate r=2 influence (flat kernel: s=0.84, d=0.68) on owned cells. Outnumber-2 captures + super-ko. First to >25.1 effective influence wins. Faster, more diffuse variant of carpet rank-1.
**Substrate:** Sierpinski carpet, axis 9, 64/81 active, max_degree 4.
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no.
**Soft violations flagged:** none.
**Quirks discovered:** super-ko active; counter-sandwich works (pilot didn't probe); seed-dependent strategic-surface volatility (PPO winrate variance 0/0.5/1.0).

### Scores (1–10)

- **Strategic Depth: 5** — Same family as carpet rank-1 (5). Counter-sandwich works (pilot missed). Flatter kernel reduces cluster-vs-spread differentiation slightly. Net same depth as rank-1, marginally less crisp.
- **Emergent Complexity: 5** — Same primitives as rank-1 (sandwich, counter-sandwich, replay, hole-edge resistance). No new emergent vocabulary from the kernel tuning.
- **Balance: 4** — Same structural P1 favour as all R19 games. **Seed-volatility flag** (PPO 0/0.5/1.0 final winrate) is a real concern but doesn't degrade balance below 4.
- **Novelty (post-adversary): 5** — Same band as rank-1. Parameter variant.
- **Replayability: 4** — Faster game + flatter kernel reduces variety vs rank-1's 4. Same score, marginal difference.
- **Overall "Would I play this again?": 5** — **Same as carpet rank-1, above pilot's 4.** The kernel tuning doesn't fundamentally change the game; counter-sandwich + super-ko + sandwich-as-cluster-builder are all preserved. Pilot scored this 1 below rank-1; I think they're on par because counter-sandwich (which pilot didn't test) restores most of the depth. Anchor: above R17 mean (3.5), above R17 best (4.14), well below R8 (8).

### CLOSEST KNOWN-GAME ANALOG
**A flatter-kernel parameter variant of carpet rank-1** (`ce3a09e05cef`). No published exact analogue.

### KILLER FLAWS
- **Same as carpet rank-1** (mirror = P1 win, knowledge-asymmetric balance, undocumented super-ko, 64-cell board limits variety).
- **Seed-dependent strategic-surface volatility.** PPO trained-vs-trained final winrate ranges 0.000–1.000 across seeds. Indicates multiple strategic local optima that PPO sometimes escapes from. May reflect a noisier strategic surface, not a bug, but a stability concern worth flagging.
- **Flatter kernel reduces strategic differentiation.** The cluster-vs-spread payoff gap is narrower than rank-1's, so opening choices are less differentiated. **This is a fitness-tuning artifact** — the parameters that survived evolution might have done so partly because the flatter kernel is *easier for PPO to learn*, not because the resulting game is *better*.

### BEST QUALITY
**Same as carpet rank-1: the sandwich-as-cluster-builder + counter-sandwich pair.** Plus, here, slightly more tolerance for loose cluster shapes due to the flatter kernel. The kernel tuning doesn't add new strategic primitives but does soften the cluster-discipline penalty, making the game slightly more forgiving of suboptimal play.

### CARPET STRUCTURAL CONTRIBUTION
**Same modest contribution as carpet rank-1.** ~+0.5 depth via hole-edge geometry. The kernel tuning is independent of substrate. Flatten to 9×9 grid: lose ~0.5 depth and most substrate flavour.

### IMPROVEMENT IDEAS
**Single best change: pie rule.** Cross-cutting recommendation. Same as all R19 games.

Secondary improvements:
- **Restore default kernel (s=1.0, d=0.5) and threshold=30** — would converge this game to carpet rank-1. Probably a strict improvement: rank-1's parameters seem better-tuned for strategic differentiation.
- **Document super-ko in briefing.** Same gap as all R19 games.
- **Investigate the seed-dependent winrate volatility.** If this is a reproducible strategic-surface multimodality, it's interesting (multiple local optima). If it's a training-noise artifact, it's a stability concern. **Worth a dedicated analysis run.**
- **Strip the inert custodian-style threshold from ANY rules** that don't use it (custodian is the prominent case but worth auditing all R19 rule blobs).

### What evolution did or didn't add (vs other carpet games)
**This game is the c1 seed (outnumber + influence + threshold) with hand-tuned non-default propagation parameters.** It survived 8 generations untouched, similar to menger rank-2's m8 seed. The non-default kernel parameters are the distinguishing feature — likely chosen at seed-design time rather than discovered by evolution. Compared to carpet rank-1 (default kernel) and carpet rank-2 (custodian + Pyrrhic-flip):
- Rank-1 wins on strategic clarity (default kernel is well-tuned).
- Rank-2 wins on novelty (Pyrrhic-flip dynamic).
- **Rank-3 has neither advantage** — flatter kernel is a tuning regression; outnumber capture lacks Pyrrhic-flip depth.
- **Net read: rank-3 is the weakest carpet game**, agreeing with the pilot.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-4_gamec3427a8ae42b.md`.*
