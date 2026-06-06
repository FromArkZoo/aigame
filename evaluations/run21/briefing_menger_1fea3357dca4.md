# R21 Eval Briefing — Menger — `1fea3357dca4`

**Substrate**: menger 3D axis-9 400/729 active Hausdorff 2.727 max_degree 6
**Slate position**: original rank 1 → fell to rank 6 under 20-seed finalization (largest deflation in the menger slate, Δ −0.093)
**Calibrated komi_p2**: 0.05 (G3 gate result; applied to P2's accumulator before the win test — see Notes)

## Engine scores
| Metric | Value | Notes |
|---|---|---|
| 20-seed mean GE | 0.118 | slate fact; original single-seed GE was 0.2107 (`scores` table) → −0.093 deflation |
| GE sigma (20-seed) | 0.085 | slate fact; ~72% of the mean — high relative variance, lucky-seed signature |
| strategic_depth | 0.485 | from `scores` table (original single-seed; not re-measured at 20 seeds) |
| non_triviality | 0.667 | from `scores` table (single-seed) |
| strategic_diversity | 1.000 | from `scores` table (single-seed) |
| pie_rule | True | enabled (rule blob) |
| komi_p2 | 0.05 | calibrated bias 0.065 per slate note; helper applies +0.05 to P2 |

(Original single-seed values verified from the DB `scores` row. The 20-seed mean/sigma are slate-provided and could not be recomputed here.)

## Rules
- **Capture** — `outnumber`, threshold = 2. A placed stone flips an opposing-owned cell only when the placing side outnumbers it by ≥ 2 in the relevant neighborhood. Capture is incidental to influence accumulation, not the win path.
- **Propagation** — `influence`, radius = 1, strength = 1.0, decay = 0.7. Each stone deposits 1.0 on its own cell and 1.0 × 0.7 = 0.7 to each active radius-1 neighbor (6-neighborhood max; many neighbors are holes, so effective fan-out is well below 6 across the fractal). Influence is the scored quantity.
- **Win condition** — **threshold-race** (NOT connection). First player whose effective owned-influence accumulator exceeds **50.0** wins; `max_turns = 200`. `target_dimension = 0` for P1; `target_dimension_p2 = -1`, meaning **P2 mirrors P1's accumulator dimension** (both race the same owned-influence total — symmetric race, not opposed axes). 50.0 on 400 active cells with decay 0.7 is a long grind; expect most games to run toward the turn cap.
- **Actions** — single action type `place`; `num_actions = 731` (729 cells + pass/terminal + 1 pie/swap). Placement is **`anywhere`** on any empty active cell (`placement_rule.constraint: anywhere`, `first_move_anywhere: true`). NOTE: the blob's `action_rule.move_constraint: adjacent_empty` is **vestigial** — verified live, 401 legal actions persist after P1's first move (= 400 remaining active empty cells + pie), so adjacency is not enforced.
- **Turn structure** — `alternating`, 1 piece per turn.
- **Balancing** — pie_rule enabled; P2 may swap on its first reply (pie/swap action id = total_cells + 1 = **730**). Komi of +0.05 is added to P2's accumulator (calibrated bias 0.065) to offset first-mover edge.

## How to play it (helper)
```
.venv/bin/python eval_run21_helper.py --game 1fea3357dca4 --moves "<csv>" [--values]
```
(komi auto-applies; pie/swap action id = total_cells+1 = 730; greedy top-K is influence-delta only and ignores captures. Pick cell ids from the "Legal" list — menger has holes, so many low indices are inactive `#`; e.g. cells 9 and 11 are active, but most of the central z=3..5 block is hollow.)

## Notes for evaluators
- **Test the inflation diagnosis directly.** This game was the menger slate's GE rank-1 entry and suffered the largest deflation (−0.093) on 20-seed re-evaluation. Sigma (0.085) is ~72% of the mean (0.118) — the classic "GE optimizer found a lucky-seed inflation" signature. The eval question: does this game feel as deep to an agent as its original rank-1 GE implied, or is it shallow once the lucky seed is removed? Expect it to play **shallower** than rank 1.
- **Parameter sibling to `e52e8889517a`** — if you also briefed that game, contrast directly; they share substrate/rule family, so divergent agent verdicts are informative.
- **Threshold race, not connection** — there is no territory/connection objective. Both seats accumulate owned-influence toward 50.0; P2 mirrors P1's accumulator (`target_dimension_p2 = -1`). Strategy is about maximizing your own influence growth (and denying opponent's via outnumber-2 captures), not building a path.
- **Sparse high-decay field** — influence radius 1 with decay 0.7 over a Menger sponge (only 400/729 active, fan-out throttled by holes) means stone value is highly local and the 50.0 threshold is far; many games likely hit `max_turns = 200`. Watch whether the race resolves before the cap or is decided on accumulator margin.
- **Degeneracies / flags**: (1) `move_constraint: adjacent_empty` is a dead field — placement is anywhere (verified live). (2) High GE variance suggests outcome can hinge on seed/opening luck; if agents report it feels "swingy" or first-mover-dominated despite komi, that supports the deflation finding. (3) Komi 0.05 is tiny relative to a 50.0 target — verify whether pie/swap or komi actually neutralizes seat bias, or whether P1 still wins most games.
