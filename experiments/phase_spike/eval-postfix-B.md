# Evaluator-B Post-Fix Re-Evaluation: Phase-Extended `c6bb58075520`

**Role**: independent post-fix evaluator B for the phase-extended c6bb58075520 spike.
**Question**: does the FIXED design (P2 unwinnable sign-bug now corrected) produce a strategically deeper game than the source `c6bb58075520` (mean 4.40/10)?
**Date**: 2026-04-22.
**Budget used**: ~45 min.

---

## Summary verdict

**Score: 4/10** vs source 4.40/10 — the fix restores a playable, two-sided game (no longer broken), but the camouflage primitive remains **strategically dominated** under any greedy or 2-ply analysis I could find. The post-fix game plays essentially identically to the source `c6bb58075520`: greedy agents and hand play both ignore camo entirely.

**Recommendation**: do not promote. The fix is correct and necessary for the spike to be evaluable, but the underlying mechanic does not earn its keep. Camouflage as a primitive needs a different incentive structure (e.g., camo as score-neutral, or capture gives camo a points reward) before this design becomes interesting.

---

## 1. 50-game greedy-vs-greedy probe results

**Heuristic**: at each turn, pick the (cell, phase) action maximizing
`player_score(me) - player_score(other)` after a 1-ply simulation. Random
tie-breaking with seed (otherwise all 50 games are identical and P1 wins
every one — the ruleset is highly deterministic in the absence of randomization).

Script: `experiments/phase_spike/eval_postfix_B_work/greedy_probe.py`
Log: `experiments/phase_spike/eval_postfix_B_work/greedy_probe_output.log`

| Metric | Value |
|---|---|
| P1 wins | 45 / 50 (90%) |
| P2 wins | 5 / 50 (10%) |
| Draws | 0 |
| Decisive rate | 100% |
| Mean game length | 21.5 steps |
| End reasons | `P1_threshold` × 45, `P2_threshold` × 5 |
| Total placements | 1077 |
| **Camo placements** | **0 / 1077 (0.00%)** |
| P1 camo rate | 0.00% |
| P2 camo rate | 0.00% |

**Key finding 1 — fix works**: P2 now wins 5/50, confirming the post-fix engine is no longer P2-unwinnable. Pre-fix this number was zero by mathematical force.

**Key finding 2 — strong P1 advantage**: P1 still wins 90% under greedy, vs the source `c6bb58075520`'s ~50/50 split. The first-mover lead at the threshold race compounds (each P1 stone radiates to its neighbors, P1 is +1 first by tempo and the threshold favors who-cluster-faster). The 4.40/10 source score reflects exactly this kind of first-mover problem; phase-extension does NOT mitigate it.

**Key finding 3 — camo is never selected**: 0 / 1077 placements were camouflage. This held across all 50 seeds and all 200 seeds in a follow-up scan (see Section 4 below).

---

## 2. Hand-played games

### Game 1: natural-only

Script: `experiments/phase_spike/eval_postfix_B_work/hand_game1_natural.py`
Log: `experiments/phase_spike/eval_postfix_B_work/hand_game1_output.log`

Both players built mirrored clusters in the upper/lower halves of the board:
- P1 builds a 3x3 minus 1 cluster around cells 18–28
- P2 builds a 3x3 cluster around cells 35–53

Score progression was symmetric: each P1 move added ~2.83 to P1, each P2 move added the same. P1 hit threshold (23.56) on move 21 (cell 13+), one move before P2 could (P2 was at 20.73). **No captures occurred**; the game played exactly like the source `c6bb58075520`. The 23-step duration matches greedy probe averages.

**Verdict**: with both players natural-only, the post-fix game is *indistinguishable* from the source.

### Game 2: camo allowed

Script: `experiments/phase_spike/eval_postfix_B_work/hand_game2_play.py`
Log: `experiments/phase_spike/eval_postfix_B_work/hand_game2_play.log`

I deliberately tried a camo move on move 9 (P1 plays `37-` — camouflage at the boundary between P1 and P2's clusters, hoping the wrong-phase stone would survive in P2's territory and seed future P1 -1 territory).

**Result**: the camo move was demonstrably worse than the best alternative.
- Best alt (cell `11+` natural): diff `+1.883`
- Camo `37-`: diff `-1.883` — a swing of **3.77 points** lost in one move.

After move 9, P1 was permanently behind P2 (P2: 7.06, P1: 5.17). At every subsequent move, the engine confirmed the natural choice was greedy-optimal. Final after move 19: P1 = 16.01, P2 = 18.85, P1 trailing.

**I could not find a single camo move that I, the player, believed was the BEST move available.** I tried multiple constructed positions:

1. **Threshold-denial at corner of P1's cluster** (`hand_game2_camo_critical.py`): tried to deny P1 a winning cell by occupying it with P2 camo. Result: camo cost P2 2.83 points; if camo radiated +1 into P1's surrounding cluster the radiation pushed P1 over threshold IMMEDIATELY (game ended before P2 could benefit from the denial). Camo was strictly worse than any natural alternative.

2. **Natural-captured threshold deny** (`hand_game2_camo_uniqueness.py`): position where P2 natural at the deny-cell would be auto-captured (4 P1+1 nbrs → outnumbered by 4, captured). Camo +1 there is NOT captured (it's same-phase as the surrounding P1+1's, so 4 same nbrs, 0 opp). Camo correctly denied the cell — but the score cost (2.83) plus the +1 radiation into adjacent P1 cells made it rank 99/100 actions by 2-ply, dead-last among non-trivial moves. P2 lost regardless.

3. **Tactical mid-game camo** (Game 2 at move 9): camo as a "fence" at the cluster boundary. Result: cost the placing player 3.77 over the natural alternative. Never recovered.

**Conclusion on camo**: under both 1-ply greedy and 2-ply (opponent best-responds) analysis, camouflage is dominated in every position I tested. Even when camo successfully achieves its theoretical purpose (denying a cell that natural-phase would lose to capture), the score cost exceeds the strategic value.

---

## 3. Does camouflage actually change optimal play?

**Empirical answer: NO.**

### Brute-force scan across 200 games

Script: `experiments/phase_spike/eval_postfix_B_work/scan_for_camo_optimal.py`

I played 200 greedy self-play games (random tie-breaking by seed) and at every position checked whether the strict 1-ply best move set was camo-only (no natural placement was tied or better).

> **0 / ~4000 positions had camo as strictly the best 1-ply move.**

### Why is camo dominated?

A camouflage stone (e.g. P1@-1) contributes to its owner's score as `cell_value × +1`, but its `cell_value` is computed against its own phase (-1). At the moment of placement, the stone radiates `-0.93` self-contribution into its own cell — vs a natural stone's `+0.93`. That's a **1.86-point swing per placement** before any neighborhood effect.

The only escape: have the camo neighbor a strong enemy cluster so the cell value's environmental sign flips. But the camo also radiates -1 into 4 neighbors, which:
- If those neighbors are EMPTY: no effect on score, but the camo's own `cell_value` is heavily negative → big self-cost.
- If those neighbors are P1+1 (own team's natural stones): adds **negative** influence to P1's score (because cell_value(P1+1 nbr) drops by 0.475). Net: **camo HURTS the P1 cluster**.
- If neighbors are P2-1 (enemy natural stones): adds **negative** influence to P2's cells (because P2 owns them). But P2's score = sum over P2 cells of cell_value × -1, so a more-negative cell_value for P2 INCREASES P2's score. So **placing P1@-1 next to P2-1's actively boosts P2's score**.

The math forces camo to be self-harming in every realistic configuration. The claimed "invade enemy territory without capture" benefit doesn't exist because the camo gives the enemy a free score boost as a side effect.

### Eval-4's "concrete moment" doesn't survive scrutiny

Eval-4 (pre-fix) cited a hypothetical where camo denial at a winning cell extends the game past P1's threshold. I tested this directly in Section 2's puzzle 2: camo successfully denies the cell, but the radiated +1 boost to surrounding P1 cells crosses threshold for P1 anyway. The denial fails because the camo's own influence betrays the placer.

---

## 4. Comparison to source `c6bb58075520` on emergent dynamics

| Dimension | Source | Post-fix phase-extended |
|---|---|---|
| Decisive rate | high | 100% (50/50) |
| First-mover advantage | strong | strong (90% P1) |
| Distinct strategic primitives | 1 (territory cluster) | 1 (territory cluster) — camo never used |
| Capture frequency in greedy play | low | 0 (zero captures across 50 games) |
| Action space size | 65 (cells + pass) | 129 (cells × 2 phases + pass) |
| Game length (greedy) | ~22 steps | 21.5 steps |
| Source human mean rating | 4.40/10 | — |

The phase extension **doubles the action space** but adds **zero new emergent dynamics** in greedy or hand play. Game length is identical. Capture frequency is the same (essentially zero in both). The first-mover advantage is identical or slightly worse. The win condition (threshold race) is the same.

**The only thing the extension adds is computational cost** (twice the action space to search) and **rule complexity** (decoupled owner/phase). Neither produces strategic value at the depth I could probe.

---

## 5. Score: 4/10 vs source 4.40/10

I rate the post-fix design **4/10**, marginally below the source's 4.40/10.

Rationale:
- (-) Post-fix retains all source weaknesses: strong P1 advantage, threshold-race monoculture, no captures in greedy play.
- (-) Adds doubled action space with NO strategic payoff. Camo rate is 0% in 250 greedy games.
- (-) Hand play with deliberate camo confirms camo is strictly worse than natural in every position I constructed.
- (-) The stated camo "use cases" (deny enemy threshold, fence territory) do not work because camo radiates score-boosting influence into the enemy's cluster.
- (+) The fix correctly restores P2's ability to win.
- (+) The phase-capture rule (friendly-fire possible via camo) is genuinely novel as a *rule*, even if no greedy/2-ply player ever exercises it.
- (+) Move-space expansion does increase the *threat space* (opponent must consider camo lines, even if they don't pay off).

Net: half a point worse than source for adding cost without value. Not 0/10 because the rules are coherent and the fix works — but the spike's hypothesis (phase adds depth) is **not supported** by post-fix evidence.

---

## 6. Recommendation

**Do not promote** the phase-extended design as-is.

**Possible future directions** if camo is to earn its keep:
1. Make camo SCORE-NEUTRAL: count camo stones as `cell_value × +1` regardless of stone phase. Then camo becomes a pure occupation primitive (still vulnerable to neighborhood effects but not penalized at the cell itself).
2. Reward CAPTURE explicitly: when capturing, the capturer scores points, making capture-bait via camo a coherent strategy.
3. Reduce action space: only allow camo when adjacent to at least one same-team natural stone. Discourages the dominant "phase-flip anywhere" no-op.
4. Redesign the win condition: threshold-race rewards homogeneous clusters; camo only matters in *interleaved* board topologies. A different win condition (e.g., longest-connected-component, or majority-by-cell-value) would force camo to be a real lever.

Any of these would produce a more interesting game. The current design is a strict superset of the source's action space with no compensating strategic depth.

---

## Files

- `experiments/phase_spike/eval_postfix_B_work/greedy_probe.py` — 50-game probe.
- `experiments/phase_spike/eval_postfix_B_work/greedy_probe_output.log` — full per-game log.
- `experiments/phase_spike/eval_postfix_B_work/hand_game1_natural.py` — natural-only hand game.
- `experiments/phase_spike/eval_postfix_B_work/hand_game2_play.py` — camo-allowed hand game.
- `experiments/phase_spike/eval_postfix_B_work/hand_game2_camo_critical.py` — threshold-denial puzzle.
- `experiments/phase_spike/eval_postfix_B_work/hand_game2_camo_uniqueness.py` — camo-vs-captured-natural puzzle.
- `experiments/phase_spike/eval_postfix_B_work/scan_for_camo_optimal.py` — 200-game scan for camo-optimal positions.
