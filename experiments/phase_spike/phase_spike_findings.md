# Phase-Extended c6bb58075520 — Spike Findings

**Date:** 2026-04-25
**Goal:** Test whether phase-stones (complex-number-inspired stone state) add genuine strategic depth on top of the R16 human winner `c6bb58075520`. Validate before paying the cost of full evolutionary integration.

**Design:** Each stone has both an OWNER (P1 or P2) and a PHASE (+1 or -1), decoupled. P1's target alignment is +1, P2's is -1. P1 can place "camouflage" stones at phase -1 (and vice versa) — same owner but enemy phase, theoretically letting them survive in enemy territory at a score cost.

---

## Round 1 (pre-fix)

4 evaluators played 3 games each on the as-shipped design.

| Eval | Score (vs source 4.40) | Verdict |
|---|---|---|
| eval-1 | 3/10 | Bug found; camo is "free lunch for P1" (extracts positive from P2's incorrectly-negative cell-vals) |
| eval-2 | 2/10 | Camo strictly dominated even after bug fix in head; suggests redesign |
| eval-3 | 3/10 | 50-game probe: 50/0 P1; **but** identified genuine novel primitives (camo anchor in dense enemy territory + friendly-fire self-capture). Estimated 6-7/10 post-fix |
| eval-4 | 5/10 | Novelty adversary: formal novelty exists (owner-phase decoupling), practically inert under buggy scoring |

**Mean: 3.25/10**

### Critical bug surfaced

`PhaseGame.player_score(2)` used `cell_val * (-stone_phase)`, which made a P2 natural stone in a P2 cluster contribute *negatively* to P2's score. Consequence: P2 was structurally unwinnable through threshold; could only win via max_turns_majority. All 4 evaluators independently identified this.

**Fix applied 2026-04-25:** unified formulation using a per-player target phase (P1: +1, P2: -1), with `score += cell_val × target_phase`. P2 natural now contributes positively to P2's score.

### Post-fix smoke test

50 random games: P1=4, P2=5, draws=41. P1/P2 within noise of symmetric. High draw rate reflects random play not converging on threshold-crossing positions on the phase variant — phase choice adds friction (probably good).

### Genuine novel primitives identified

Even pre-fix, evaluators flagged two primitives that don't exist in known abstract games:

1. **Camouflage anchor**: a P1 stone at phase -1 placed inside a dense P2 cluster is *not captured* (same phase as neighbors) and contributes positively to its owner's score (eval-3 measured +1.88 from a single anchor placement). The strategic question becomes: when does the anchor's gain exceed the cost of mismatched-phase friendly-fire risk?

2. **Friendly-fire self-capture**: phase-based outnumber capture is owner-agnostic. A player's own camouflage stones can capture their own natural stones if positioned wrong. This is a structurally novel primitive — no known game has the property "your own stones can kill each other".

---

## Round 2 (post-fix)

| Eval | Score | Verdict |
|---|---|---|
| postfix-A | 4/10 | Camouflage anchor (eval-3's "novel primitive") was a bug artifact. Post-fix it's a -4.7 net swing for the placing player. Phase action axis collapses — natural-only dominates. |
| postfix-B | 4/10 | 50-game greedy probe: 45/5/0 P1; camo never picked once in 1077 placements. Across 200 hand-constructed positions: zero where camo was strictly best. The math forces self-harm: P1 camo radiates -0.475 to P1 neighbors AND its own contribution is -0.93 vs natural's +0.93. |

**Round 2 mean: 4.0/10. Combined mean (6 evals): 3.5/10.** Below source 4.40.

### Why binary phase doesn't work — the math

A P1 camo stone (P1@-1) at cell C:
- Self-contribution to cell C's value: -0.93 (radiates -1 phase)
- Contribution to each adjacent cell's value: -0.475 (radiates -1 × decay)
- P1's score for cell C: cell_val × +1 (P1 target). Self-contribution alone: -0.93.
- For each P1 neighbor: cell_val drops by 0.475 → P1's score drops by 0.475 per friendly neighbor.

So a P1 camo is a strict score loss for P1 *unless* the cell's environment provides enough positive cell_val to overcome the self-loss. But that environment requires P1 stones nearby — and P1 stones are best served by natural placement, not camo.

In enemy territory, camo is even worse: P2 stones make cell_val negative, P1's target +1 multiplies the negativity, and P1's own -0.475 radiation into P2 cells *boosts* P2's score (P2 target is -1, more negative cell_val = more positive P2 score). Triple loss.

There is no positive-EV camo move under these dynamics. The action space inflation from 65 → 129 is pure overhead.

### What would actually need to change

To make a phase-extended primitive work, *at least one* of these needs to hold:

1. **Camo radiates zero** (or attenuated). Make camo stones pure blockers with no influence radiation. Then P1 camo doesn't harm P1 neighbors' cell_vals, and the strategic question becomes: "is it worth the self-cost to occupy + survive?" For camo to break even, capture-immunity in enemy territory must outweigh the lost +0.93 of natural. Tractable but unclear if interesting.

2. **Score function decoupled from radiation field**. E.g., score by piece count or connectivity instead of influence sum. Then camo doesn't actively help the opponent. But this breaks the source game's signed-influence threshold — it's a different game.

3. **More phases** (4-phase or continuous). Use {0°, 90°, 180°, 270°} where 90°/270° are *orthogonal* to both players' targets — radiate vector-orthogonal influence that doesn't contribute to either score. This is the "true complex numbers" version. Cost: substantially more eval-cognitive load (humans now need to reason about 2D phase vectors), engine refactor for vector-valued board_values. ~5+ days of work.

4. **Phase as state, not annotation**. Add a phase-rotation action so phase becomes a dynamic property that changes during play, not a one-shot decision at placement. This makes phase a real strategic variable. Adds action class complexity but creates genuine novel decision space.

---

## Round 3 (4-phase complex redesign)

User picked path (C) — full 4-phase complex redesign with phases at compass directions {N=0°, E=90°, S=180°, W=270°}, vector-valued influence, target-aligned scoring.

The structural argument: phases 90° and 270° are *orthogonal* to both players' score axes (project ±y influence, contributing zero to either x-component score). They're true neutral occupiers. They're also capture-immune to N/S attackers (cos(90°) = 0). The math problem that killed binary phase is solved by construction.

| Eval | Score | Verdict |
|---|---|---|
| v2-1 | 4/10 | Math correct, all primitives verified. But denial-by-E dominated by N opportunity cost (~1.5-1.9 score gap). Random play 48/50 draws — half the action space "wasted". |
| v2-2 | 3/10 | 100 greedy games, 2,225 placements: **0 E/W placements**. H2 (E-vs-W secondary axis): "sterile — freezes at score 0.000". Recommend DROP. |
| v2-3 | 4/10 | 1-ply greedy: 20 games, P1 20/20. Phase distribution {N:240, S:220, E:0, W:0}. Found exactly *one* concrete strategic moment where E is best (capture-immune permanent denial in a contested-cell position). Real but rare primitive. |
| v2-4 | 5/10 (Balance 7) | Structural symmetry verified at numerical precision. Forced-pass-first inverts P1 87% → P2 87% — pure move-order asymmetry. Better balance than binary v1. But 0/690 E/W placements in greedy probes. |

**Round 3 mean: 4.0/10**. Equivalent to source 4.40 — marginally below.

### What 4-phase fixed vs. what stayed broken

✅ **Fixed**: structural seat balance (verified symmetric to numerical precision). The math now works correctly — E/W truly orthogonal, no active self-harm, no enemy-helping radiation.

❌ **Stayed broken**: the orthogonal primitives are **never the best 1-ply move**. Across 100+ greedy games and ~3,000 placements, E/W placement rate ≈ 0%. The new design space is invisible to forward-looking policies because:
1. N gives +1 to own score AND -1 to enemy (net swing +2 per move)
2. E gives 0 to own AND 0 to enemy (net swing 0)
3. The denial value of an E placement (preventing future +2.83 enemy cluster) is dominated by the +1.88 opportunity cost of *not* placing N elsewhere
4. The E-vs-W secondary axis is sterile — both pure-E and pure-W games freeze at score 0 forever

### The structural problem

**Threshold-win + signed-influence + target-alignment scoring is structurally hostile to phase-orthogonal strategic choice.** The math forces aligned (N/S) placements to dominate orthogonal (E/W) ones except in very narrow contested-cell positions where capture-immunity provides a specific tactical edge.

The same pathology hit binary post-fix and 4-phase complex: agents converge to "natural-only" play, the new action space is overhead.

To make phase mechanics genuinely productive, would need *at least one* of:
- **Different scoring**: piece-count or connectivity instead of influence-summed-target-alignment. But this is no longer the c6bb58075520 source family.
- **Phase as state, not annotation**: add a phase-rotation *action* so phase becomes dynamic. Would force engagement with the phase axis.
- **Asymmetric phase availability**: e.g., orthogonal phases only available under specific game conditions (post-capture? after a "trigger" move?). Adds emergent context.

---

## Final verdict: **DROP the phase-on-c6bb58075520 line entirely.**

Across **10 evaluators in 3 rounds** (binary pre-fix, binary post-fix, 4-phase complex), the empirical mean is:

| Round | Design | Evals | Mean |
|---|---|---|---|
| 1 | Binary {+1,-1} pre-fix | 4 | 3.25 |
| 2 | Binary {+1,-1} post-fix | 2 | 4.0 |
| 3 | 4-phase complex {N,E,S,W} | 4 | 4.0 |

**Combined: 3.7/10 across 10 independent evaluations** vs source 4.40. Phase mechanics on this game template do not produce strategic depth beyond the source.

This is a **clean negative result**, not a wasted experiment. The signal is unambiguous and well-documented. Three takeaways for the project:

1. **Threshold-win + influence-propagation + target-alignment scoring is fundamentally aligned-only.** Any phase that doesn't align with the player's target is opportunity-cost-negative. This insight applies beyond phase: any future "extra stone parameter" with this scoring function will hit the same wall.

2. **Adding action-space dimensions doesn't add strategic depth without coupling.** The 4-phase 4× action inflation produced 0 strategic content because the new dimensions are decoupled from the score function. Future substrate additions need explicit coupling to scoring.

3. **The cheap-spike protocol works.** Two design iterations + 10 evaluators in ~1 day of wall time gave a clean go/no-go. Cost-effective even on negative results — much cheaper than full evolutionary integration would have been.

### Forward path

Return to **R17 along the established line**: classical alt + active capture + signed influence + threshold on non-Moore topology, with the three R17 engine fixes (mutation-time moore+surround downgrade, FP ordering, seat_balance floor). The R16 human winner (`c6bb58075520`, 4.40/10) sits in this family. R17 has a real chance of producing a 5+/10 game by tightening the metric and closing the bug-leak — a more reliable bet than another substrate experiment.

If the user wants to revisit phase mechanics later, the cheapest viable path would be **phase-rotation as a separate action class** — making phase a dynamic state rather than a placement annotation. This forces engagement with the phase axis through gameplay, not just choice-at-placement. Estimated cost: similar to v2 spike (~1 day).

---

## Appendix: file inventory

- `phase_game.py` — standalone PhaseGame engine (~250 lines)
- `phase_play_helper.py` — CLI for engine-verified play
- `eval-1.md`, `eval-2.md`, `eval-3.md`, `eval-4.md` — Round 1 reports
- `eval-postfix-A.md`, `eval-postfix-B.md` — Round 2 reports (pending)
- `eval3_work/random_probe.py` + `p2_strategy_test.py` — eval-3's probe scripts
- `eval_postfix_B_work/` — eval-postfix-B's greedy probe (pending)
