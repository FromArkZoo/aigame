# R21 Eval Briefing — Menger — `e52e8889517a`

**Substrate**: menger 3D axis-9 400/729 active Hausdorff 2.727 max_degree 6 (orthogonal 6-neighbour topology, sponge holes punched at center-cross cells — many low indices are inactive)
**Slate position**: rank 3 of menger slate by 20-seed mean GE (top is `e1453dac5445` @ 0.177; this game @ 0.138)
**Calibrated komi_p2**: 0.05 (G3 mirror-bias gate; auto-applies in the helper; → bias term 0.015)

## Engine scores
| Metric | Value | Notes |
|---|---|---|
| 20-seed mean GE | 0.138 | from R21 finalization (`evaluation_report_run21.md`); σ 0.090 |
| σ (20-seed) | 0.090 | sibling-comparable; not σ<0.04 target |
| go_essence (1-seed) | 0.203 | original `scores` table value — single-seed, inflated vs 20-seed mean |
| strategic_depth | 0.592 | from `scores` table |
| non_triviality | 0.667 | from `scores` table |
| strategic_diversity | 0.667 | from `scores` table |
| rule_simplicity | 0.254 | rule_complexity = 19 |
| elo | 2172.5 | original eval pool |
| pie_rule | True | swap action enabled |
| komi_p2 | 0.05 | calibrated |
| failure modes | 5% zero / 20% ceiling | per-rerun GE distribution (report §menger), bimodal |

## Rules
- **Capture**: `outnumber`, threshold 2. A stone is cleared to empty when it has ≥2 enemy orthogonal neighbours. **Verified live**: a P1 stone at (0,1,0) flanked by P2 at (0,0,0) and (0,2,0) was captured and removed.
- **Propagation**: `influence`, radius 1, strength 1.0, decay 0.7. Each placed stone radiates influence to active neighbours within 1 step, falling off by ×0.7 per step. Score = sum of owned-cell influence.
- **Win condition**: **threshold-race** (NOT connection). P-effective owned-influence > **30.0** wins; `max_turns` = **100** (draw/score-out otherwise). `target_dimension` = 0 for P1; `target_dimension_p2` = −1, meaning **P2 mirrors P1's accumulator** (both race the same owned-influence sum, P2 with +komi).
- **Actions**: `place` only. `first_move_anywhere=true`; thereafter `move_constraint=adjacent_empty` in the blob, though the live legal set is broad (397 legal after 4 moves). num_actions = 731.
- **Turn structure**: `alternating`, 1 piece per turn.
- **Balancing**: `pie_rule=True` (P2 may swap seats on move 2) + komi_p2 0.05 added to P2's effective score at every win-check (bias term 0.015).

## How to play it (helper)
```
.venv/bin/python eval_run21_helper.py --game e52e8889517a --moves "0,2,18,20" --values
```
(komi auto-applies; total_cells = 729 → place ids 0–728, pass = 729, **pie/swap action id = 730**; greedy top-K is influence-delta only and ignores captures.)

## Notes for evaluators
- **Sibling comparison is the job here.** This game is the deliberate parameter-sibling of `1fea3357dca4`. Their rule blobs are **NOT byte-identical**, but the structural diff is exactly two fields: `win_condition.threshold` 30 (this) vs 50 (sibling) and `max_turns` 100 (this) vs 200 (sibling). Capture, propagation (decay 0.7), topology, pie, komi are all identical. **Score the lineage/parameter difference only** — do not re-hunt for structural differences. The shorter race (30/100) vs the longer race (50/200) is the entire experimental contrast.
- This game's sibling `1fea3357dca4` was original-rank-1 and deflated −0.093 to rank 6 under 20-seed finalization (the largest deflation in the slate — "GE optimizer found cheaters" signature). This game (the 30/100 variant) held rank 3, so the shorter race appears more robust to seed variance.
- **Bimodal noise**: 5% of reruns score ~0 (PPO failed to converge) and 20% hit the ceiling — the 0.090 σ is partly structural PPO-failure, not Gaussian. Weight a clean converged playthrough over the mean.
- **Captures are real and tactical** — the greedy top-K influence-delta hint ignores them, so do not trust greedy to defend; flanking (2 orthogonal enemies) removes stones.
- Holes: many low cell indices are inactive (the z=1/3/4/5/7 layers are heavily punched). Pick cell ids from the helper's printed Legal list, not by guessing.
- No known rush-broken seat bias at komi 0.05 (G3 calibration passed for this game). Vestigial fields: `target_dimension_p2=-1` is a mirror flag, not a second objective — both seats race the same accumulator.
