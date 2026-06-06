# R21 Eval Briefing — Carpet — `d995cf010504`

**Substrate**: carpet (Sierpinski) 2D axis-9 64/81 active, Hausdorff 1.893, max_degree 4
**Slate position**: carpet slate TOP by 20-seed mean (GE 0.103)
**Calibrated komi_p2**: 0.05 (G3 gate; bias +0.005 — cleanest balance in the slate)

## Engine scores
| Metric | Value | Notes |
|---|---|---|
| 20-seed mean GE | 0.103 | from slate facts; cannot recompute from blob |
| sigma | 0.071 | from slate facts |
| strategic_depth | — | not stored in rule blob; could not verify |
| non_triviality | — | not in blob; could not verify |
| strategic_diversity | — | not in blob; could not verify |
| pie_rule | True | verified in blob (`pie_rule: true`) |
| komi_p2 | 0.05 | verified via helper header + live P2 start score +0.050 |
| capture threshold | 2 | verified (`outnumber`, threshold 2) |
| influence r / strength / decay | 2 / 1.0 / 0.7 | verified in blob |
| win threshold | 25 | verified; `target_dimension_p2 = -1` (P2 mirrors P1's accumulator) |
| max_turns | 100 | verified |

Note: this is gen-5 immigrant, the one carpet game whose original GE UNDERESTIMATED its 20-seed mean (Delta +0.009). Blob `seeded_from: r21_carpet_t25_d07`; per slate notes this is the re-injected R20 carpet anchor `625bfc1f3f49` — the R21 report's "lost carryover champion" was never lost.

## Rules
- **Capture**: `outnumber`, threshold 2. A stone flips owner when the opponent outnumbers the placing side by ≥2 in the relevant neighborhood. Verified live: P2's (2,5) next to P1's x=2 column dropped P1 score 6.29→5.10 via contested propagation; pie-flip captured the placed stone (owner toggled).
- **Propagation**: `influence`, radius 2, strength 1.0, decay 0.7. Each stone radiates ±influence over a Chebyshev-r2 disc, decaying 0.7^distance, signed by owner (P1 +, P2 −). Holes (#) carry no influence. Clustering compounds: the verified x=2 P1 column peaked at +1.70/+1.91, far above the +1.0 of an isolated stone.
- **Win condition**: threshold-RACE (not connection). First player whose **net signed owned-influence** exceeds **+25** (P-effective) wins; P2's target mirrors P1's accumulator (`target_dimension_p2 = -1`). With per-stone influence ~1–2 and only 64 active cells, the +25 bar is steep — expect `max_turns=100` to be the practical terminator and the result to hinge on who holds the larger net field at the cap.
- **Actions**: `place` only. `num_actions=83` (cells 0–81 + pie id 82). Placement is effectively **anywhere empty** — `first_move_anywhere: true`, and verified live that a non-adjacent second placement is legal, so the blob's `move_constraint: adjacent_empty` is **vestigial / dead**.
- **Turn structure**: alternating, 1 piece per turn. Pie rule active: P2's first action may swap seats (flips ownership of all placed stones); komi +0.05 compensates P2 for moving second.

## How to play it (helper)
```
.venv/bin/python eval_run21_helper.py --game d995cf010504 --moves "<csv>" [--values]
```
(komi auto-applies; pie/swap action id = total_cells+1 = **82**; greedy top-K is influence-delta only and ignores captures.)

Pick cell ids from the helper's **Legal** list — the carpet has 17 holes (centers of each 3×3 block, fractally), so ids like 40 (4,4) and 10,13,16,31,... are inactive and rejected. The center 3×3 (x,y ∈ {3,4,5}) is entirely a hole.

## Notes for evaluators
- **Slate-specific**: top carpet game; lowest-bias balance (komi 0.05 → +0.005). It's the re-injected R20 anchor `625bfc1f3f49` — treat it as a known-good reference point, not a novel mutant. GE under-estimated its true mean, so don't anchor your verdict on the headline 0.103; play it.
- **Race not connection**: dispatch as a threshold race on net influence. There is NO connectivity goal — captures and field dominance are the only levers. Reaching +25 outright is unlikely; judge play as territory/field accumulation toward the turn cap.
- **Clustering dominates**: r=2 decay=0.7 means adjacent stones reinforce (column peaked ~+1.9). Strong play builds compact connected masses on the solid corner/edge 3×3 blocks; isolated stones are worth only +1.0 and are exposed to outnumber-2 flips.
- **Holes structure the geometry**: max_degree 4, and the fractal holes cut the board into eight solid 3×3 corner/edge blocks around an empty core. Influence cannot cross the central void, so the four corner blocks are quasi-independent battlegrounds.
- **Degeneracies flagged**: (1) `move_constraint: adjacent_empty` is dead — placement is anywhere-empty (verified). (2) `target_dimension: 0` / `target_dimension_p2: -1` are scalar-accumulator artifacts; only the net-influence threshold matters for a threshold-race game. (3) Watch for rush-broken seat bias: with pie active + komi 0.05 the balance is the slate's cleanest (bias +0.005), so seat advantage should be minimal — confirm in play.
