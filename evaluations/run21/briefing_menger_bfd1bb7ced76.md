# R21 Eval Briefing — Menger — `bfd1bb7ced76`

**Substrate**: menger 3D axis-9 400/729 active Hausdorff 2.727 max_degree 6
**Slate position**: rank 5 by 20-seed mean GE (0.126); 3rd of 4 menger games behind `e1453dac5445` (top) and `e52e8889517a`
**Calibrated komi_p2**: 0 (G3 gate: post-pie mirror seat bias already < 0.10, so the smallest balancing komi is 0; residual bias ≈ 0.060)

## Engine scores
| Metric | Value | Notes |
|---|---:|---|
| 20-seed mean GE | 0.126 | slate value; σ = 0.070 |
| GE (single-run, scores table) | 0.190 | raw `go_essence` in `genesis_v2_run21_menger.db` — higher than the 20-seed mean, hence the mean is the slate number |
| strategic_depth | 0.605 | verified from scores table |
| non_triviality | 1.000 | verified |
| strategic_diversity | 1.000 | verified |
| rule_simplicity | 0.254 | verified (rule_complexity = 19) |
| elo | 1917.4 | verified |
| pie_rule | True | verified in rule blob |
| komi_p2 | 0 | verified; helper auto-applies |

## Rules
- **Capture**: `outnumber`, **threshold = 2**. A stone is captured when the count of enemy stones in its radius-1 neighborhood meets/exceeds your own friendly neighbors by the threshold. Verified live: P1 on cells 9 + 1 (both adjacent to P2's cell 0) removed the lone P2 stone — P2 piece count dropped 1 → 0 on the move that completed the 2-neighbor surround.
- **Propagation**: `influence`, **radius = 1, strength = 1.0, decay = 0.7**. Each stone scores 1.0 on its own cell and projects 1.0 × 0.7 = 0.7 onto every neighbor. Verified live: two adjacent friendly stones scored 3.400 = 2×1.0 (self) + 2×0.7 (mutual radiation). Decay is per-step over a single ring (radius 1), so there is no second-ring spillover.
- **Win condition**: **threshold-race** (`condition_type = threshold`). First player whose effective owned-influence accumulator exceeds **30.0** wins; cap **max_turns = 200**. `target_dimension = 0` for P1; **`target_dimension_p2 = -1` ⇒ P2 mirrors P1's accumulator** (both race the same scalar owned-influence total — not orthogonal axes). Helper prints `P-to-threshold` for both seats.
- **Actions**: single action type `place`; `num_actions = 731` (729 cells + first-move + pie). `move_constraint` is `adjacent_empty` in the blob, but `placement_rule` is `target=empty, constraint=anywhere, first_move_anywhere=true` — placement is effectively anywhere on an empty active cell (holes are not placeable).
- **Turn structure**: `alternating`, **1 piece/turn**. **Pie rule on**: P2 may swap seats after P1's first move (swap/pie action id = total_cells + 1).

## How to play it (helper)
```
.venv/bin/python eval_run21_helper.py --game bfd1bb7ced76 --moves "<csv>" [--values]
```
(komi auto-applies = 0; pie/swap action id = total_cells+1 = 730; greedy top-K is influence-delta only and ignores captures. Pick cell ids from active cells only — holes `#` are inactive; many low/center indices are dead. z=0 row y=0 cells 0–8 and z=0 row y=2 cells 18–26 are reliable active starters.)

## Notes for evaluators
- **Most reliable learner in the slate.** Slate note: the only menger game flagged with **no zero-failure rerun mode** (0% of its 20 seeds scored GE = 0). It tests whether "reliably learnable" correlates with "deep." Treat clean, repeatable PPO convergence here as the expected baseline, not a surprise — that reliability is exactly what is under test.
- **Caveat on the 0% figure**: the 180-rerun distribution table in `evaluation_report_run21.md` (line 156) lists 5% at 0.0 for this game; the "0%" is the 20-seed mean rerun set. Either way it is the cleanest menger learner — the S5 elite Δ was only −0.064 (small), i.e. robust, not lucky-seed.
- **Komi = 0 is real, not vestigial.** The mirror-P2 win rule (`target_dimension_p2 = -1`) plus the pie rule already drive post-pie seat bias under the 0.10 gate, so no komi is needed. Residual bias ≈ 0.060 favors the mover slightly; pie is the actual balancer here.
- **3D depth matters.** max_degree 6 means interior active cells have full 6-neighbor coordination, so outnumber captures and influence stacking are genuinely 3D — a stone can be surrounded across z-layers, not just within one plane. Strategic_depth 0.605 is the second-highest signal in this menger pod.
- **Degeneracy flags**: `move_constraint = adjacent_empty` in the blob is overridden by `first_move_anywhere`/`constraint=anywhere` — placement is anywhere-empty, so the adjacency field is effectively vestigial. The win threshold (30.0) and decay (0.7) are live and load-bearing (verified). No rush-broken seat bias observed; threshold-race dispatch is correct (this is genuinely threshold, not connection).
