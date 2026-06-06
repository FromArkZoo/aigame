# Run 21 Agent-Team Eval — team-5 — Game d995cf010504

**Team ID:** team-5
**Game ID:** d995cf010504 (carpet slate TOP by 20-seed mean GE 0.103, σ 0.071, calibrated komi_p2 0.05; re-injected R20 anchor `625bfc1f3f49`)
**Substrate:** sierpinski/carpet (axis 9, 64 active cells / 81 grid positions, max_degree 4, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game d995cf010504` (see `briefing_carpet_d995cf010504.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9 Sierpinski carpet, level-2 holes. 64 active / 81, `c=y*9+x`, max_degree 4. The 17 holes are the centre of each 3×3 block (fractally): the central 3×3 (x,y∈{3,4,5}) is entirely a hole, and each of the 8 surrounding 3×3 blocks has its own centre hole. Net geometry: **8 solid-but-for-centre 3×3 blocks arranged in a ring around an empty core.** Verified live.

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = **100**.

**Action space.** 83 = 81 cells + pass(81) + pie(82). Anywhere-empty (`adjacent_empty` vestigial — verified). Holes rejected (e.g. cell 10=(1,1), 40=(4,4)).

**Placement & capture.** **outnumber, threshold 2.** Verified: contested contact drops the opponent's accumulator and a bracketed stone flips/clears.

**Propagation.** influence, **radius 2**, strength 1.0, decay 0.7 → self +1.0, dist-1 +0.70, dist-2 +0.49 over a Chebyshev-r2 disc. **Verified field:** a stone at (2,2) deposits +0.49 out to (4,2) and (2,4) — i.e. influence **spills across block boundaries along the continuous outer ring**; only diagonal crossing through the central void is blocked. Bigger footprint than the menger r=1 games.

**Win condition.** **threshold-race**, target **25.0**, `target_dimension_p2=-1` (mirror). **Komi = 0.05 × 25 = 1.25** (engine multiplicative; helper shows flat +0.05). Timeout → piece-count majority.

**Pie rule.** True (id 82).

**Degeneracy check.** Helper komi display flat (real 1.25); `adjacent_empty` vestigial; central void structures geometry (no diagonal crossing) but the outer ring is connected.

---

## Phase 2 — Strategic Play

### Game 1 — Block-fill race (P1 top-left block vs P2 bottom-right)
Sequence: `0,60,1,61,2,62,9,69,11,71,18,78,19,79,20,80` (P1 wins ply 15).
Plot: P1 fills the 8-cell top-left block, P2 mirrors bottom-right. r=2 compounding is strong: the **block-completing 8th stone jumped P1 +21.28 → +27.04 (+5.76!)** by claiming pre-existing influence from ~7 friendly stones at dist 1–2. **Engine: P1 crosses 25 first at ply 15, Winner=1.** A single 3×3 block (8 cells) is enough to win — block-completion is the pivotal high-value move, and P1 gets there first by tempo (komi 1.25 < the 5.76 completion swing).
Reflection: the binding decision is *which* block to complete and *when* — completing yours one tempo before the opponent is the whole game.

### Game 2 — P2 contest (invade P1's block)
Sequence: `0,1,9,2,18,11,19,20` — P2 plays into P1's block. At ply 7 P1 +7.99 vs P2 +4.66 — P2's invaders are sapped by P1's denser surround. r=2 means contact fights are even more mutually destructive than r=1 (more overlapping negative deposits). Building your own block uncontested dominates invading.

### Game 3 — Pie swap + field inspection
Sequence (pie): `20,82,11` — P2 swaps P1's opening stone; clean tempo transfer, position symmetric with P2 +1.
Sequence (field): `20` with `--values` — confirmed the r=2 disc and cross-boundary spill described above.

### Strategy guides
**P1:** Pick a solid 3×3 corner block and fill it compactly; the completing stone is a +5.76 swing and you reach 25 first by tempo. Use the continuous outer ring to let two adjacent blocks reinforce.
**P2:** Mirror in a different block and let komi 1.25 close the one-tempo gap; or swap. Do **not** invade — r=2 contact is mutually destructive and you fall behind.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** A bit more than the menger pod: there are 8 blocks and you choose which to develop and whether to chain two adjacent blocks via the ring. Within a block, packing is forced. So genuine *positional* choice (which blocks), shallow *tactical* choice (packing order).
**Counter-play.** Limited — invading is sapped; the leader completes their block first. Pie/komi balance the tempo. Captures fire in contact but are tempo-costly.
**Short-term vs long-term.** ~15-ply horizon; the medium-term consideration is "which two blocks do I chain via the ring before the opponent completes theirs."
**Emergent concepts.** **Block-completion swing** (the crown jewel — claiming accumulated r=2 influence in one move), cross-ring reinforcement, contested-boundary sapping.
**Does carpet matter?** Yes, more than menger's holes matter: the fractal void genuinely **partitions the board into quasi-independent battlegrounds** (no diagonal crossing through the core), so block selection is a real decision the substrate creates.
**Does the kernel matter?** Yes — r=2 (vs the menger r=1) makes block-completion a large discrete swing and lets adjacent blocks reinforce across the ring. The bigger footprint is the most field-like of the slate.
**Capture contribution.** Real but tempo-costly; r=2 makes contact fights more punishing, discouraging invasion.
**Seat balance.** **Cleanest in the slate** (calibration bias +0.005). In a pure mirror P1's tempo wins by the completion swing, but komi 1.25 + pie close it to ~even per calibration. Known-good R20 anchor.

---

## Phase 4 — Novelty Adversary

**Adversary case.** An r=2 influence-area race on a fractal board carved into 8 blocks.
(a) threshold-race ≈ area/territory race. (b) outnumber-2 ≈ Ataxx/Tafl. (c) the combination is the R20 carpet champion (this *is* the re-injected R20 anchor `625bfc1f3f49`) — explicitly **not** a novel mutant. (d) Sierpinski substrate with block-partitioning is the most substrate-distinctive feature, but it is inherited from R20. (e) expert-transfer ~5–10 min.
**Closest analogue:** R20 carpet area-race champion; broadly an Ataxx/area game on a fractal board.
**Comparison to R8 (4.10):** different family; comparable absolute level, cleaner balance.
**Comparison to R19/R20:** ≈ R20 production-to-best for carpet (R19 carpet top was 4.4; this is a notch below that). The block-partitioning is its strongest asset.

**Novelty score (post-adversary):** 3.0/10. Known-good but known — the briefing itself frames it as a reference point, not a discovery. The block-partitioning substrate is its most distinctive (inherited) trait.

---

## Phase 5 — Verdict

**Team ID:** team-5
**Game ID:** d995cf010504
**Rules Summary:** An r=2 influence-area race to +25 on a Sierpinski carpet whose fractal void splits the board into 8 quasi-independent 3×3 blocks; completing a block is a large discrete swing (+5.76) and the first mover completes theirs first. Clean balance, polished — the re-injected R20 anchor.
**Substrate:** carpet, axis 9, 64/81 cells, max_degree 4, pie_rule=True, komi_p2=0.05 (real ×25 = 1.25).
**Turn Structure:** alternating. **Hybrid actions:** no.
**Soft violations flagged:** helper komi display flat (real 1.25); `adjacent_empty` vestigial.

### Scores (1–10)
- **Strategic Depth: 3.6** — block selection + cross-ring chaining add a positional layer over the menger races; within-block packing is forced. Slightly above the menger pod.
- **Emergent Complexity: 3.5** — the block-completion swing and cross-ring reinforcement are genuine emergent patterns from the r=2 field + fractal geometry.
- **Balance: 4.0** — cleanest in the slate (bias +0.005); komi 1.25 + pie close the tempo gap to ~even.
- **Novelty (post-adversary): 3.0** — known-good R20 anchor, not a discovery.
- **Replayability: 3.5** — 8 blocks give real opening variety; plans still converge to "complete a block first."
- **Overall: 3.6** — polished, well-balanced, with a satisfying completion-swing mechanic and a substrate that actually shapes play. ≈ R20 production (3.73)–; below the R19 ceiling.

### CLOSEST KNOWN-GAME ANALOG
R20 carpet area-race champion (`625bfc1f3f49`); broadly an Ataxx/area game on a fractal board.

### KILLER FLAWS
- It is the R20 anchor re-served — low marginal novelty for R21.
- Still an influence-race at heart; invasion/captures are tempo-costly, so the contest is mostly "who completes a block first."

### BEST QUALITY
The **block-completion swing**: r=2 influence lets a single closing stone claim ~+5.76 of accumulated field, and the fractal void turns block selection into a real positional decision. This is the most field-like, most substrate-shaped game in the slate.

### CARPET STRUCTURAL CONTRIBUTION
**Positive and real** — the central void partitions the board into 8 quasi-independent blocks (no diagonal crossing), creating genuine block-selection decisions that a flat grid would not. The most substrate-load-bearing game I evaluated.

### IMPROVEMENT IDEAS
**Single best change:** make the inter-block ring connections strategically pivotal — e.g. reward (or require) controlling the connecting edge cells — so the 8 blocks form a contested network rather than parallel fills. That would convert "complete a block first" into "win the network," adding the depth the race currently lacks.
Secondary: since this is the R20 anchor, its role in R21 is calibration, not novelty — treat its score as a fixed reference point against which the genuinely-new games (e.g. `e1453`) are measured.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-5_gamed995cf010504.md`.*
