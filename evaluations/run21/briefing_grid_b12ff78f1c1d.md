# R21 Eval Briefing — Grid — `b12ff78f1c1d`

**Substrate**: grid 2D axis-8 64/64 active flat (max_degree 4, no holes) — NOTE: live game is grid-8/64-cell, not the grid-9/81 in the slate notes; verify-against-live wins.
**Slate position**: grid top by 20-seed mean GE. The single place R21 evolution compounded — a gen-5 crossover child with verified parent lineage `[07d19636abaa, 09150071c8cb]` (parameter_blend). MOST STABLE game in the project (sigma 0.0517). Tests whether stability correlates with quality.
**Calibrated komi_p2**: 0.05 (helper auto-applies). CAVEAT: G3 finalization verdict was `FAIL_RUSH_BROKEN` and `calibrated_komi=null` — 0.05 is the least-bad point (G4 seat bias 0.030, lowest of the sweep), not a passing calibration. See Notes.

## Engine scores
| Metric | Value | Notes |
|---|---|---|
| 20-seed mean GE | 0.0985 | finalization rerun (20 outer × C2 n=3 = 60 seeds); original single-shot GE was 0.1503 |
| GE sigma | 0.0517 | min 0.0239 / max 0.2064; tightest distribution in the project |
| strategic_depth | 0.6065 | from `scores` table |
| non_triviality | 0.6667 | from `scores` table |
| strategic_diversity | 1.0000 | from `scores` table (maxed) |
| rule_simplicity | 0.2570 | rule_complexity 18 |
| elo | 1854 | from `scores` table |
| pie_rule | True | swap available to P2 on move 2 |
| komi_p2 | 0.05 | applied to P2 effective score every step |

## Rules
**Capture** — Custodian, threshold=1. A stone is flipped to the mover's colour when it becomes sandwiched: placing such that an opponent stone has the mover's stones on opposite orthogonal sides. Verified live: P1 at (3,3) then (5,3) flipped the P2 stone at (4,3) (the move 5 line showed `Captures (flipped owner): ['(4,3)']`, P2 piece count dropped 2→1).
**Propagation** — Influence, radius=1, strength=1.0, decay=0.5. Each stone deposits +1.0 (own colour) on its own cell and +0.5 (=strength×decay) on each orthogonal neighbour; opponent influence is negative on the field. Verified live: a lone stone shows +1.00 on-cell, +0.50 on each of 4 neighbours; overlapping fields sum (a contested neighbour reached −1.00).
**Win condition** — Threshold-RACE (dispatch: race, NOT connection). First player whose effective owned-influence accumulator exceeds 20.0 wins. `target_dimension_p2 = -1` ⇒ P2 mirrors P1's accumulator (both race the same owned-influence sum, not a per-player axis). `max_turns = 72`; if neither crosses 20.0 by then the game ends (decided by accumulator, draws possible — finalization saw ~0–3% draw rate).
**Actions** — `place` only (num_actions=66 = 64 cells + slot 64 unused + 65=PIE). `placement_rule.target=empty`, `first_move_anywhere=true`. NOTE: the rule blob's `move_constraint=adjacent_empty` is VESTIGIAL — live legal lists show all empty cells are playable from any state (65 legal on move 1, full board open), so placement is effectively anywhere-empty, not adjacency-gated.
**Turn structure** — Alternating, 1 piece/turn, 2 players.
**Pie/komi balancing** — pie_rule=True: P2 may SWAP seats on move 2 (action id 65 = total_cells+1; illegal for P1, confirmed live). Komi_p2=+0.05 is added to P2's effective accumulator every step to offset P1's first-move tempo.

## How to play it (helper)
```
.venv/bin/python eval_run21_helper.py --game b12ff78f1c1d --moves "27,28,35,36,29" --values
```
(komi auto-applies; pie/swap action id = total_cells+1 = 65, P2-only on move 2; greedy top-K is influence-delta only and ignores captures — do not trust it for capture tactics.)

## Notes for evaluators
- **Stability ≠ passing.** This is the lowest-sigma game in the project, but G3 still graded it `FAIL_RUSH_BROKEN`. At the chosen komi 0.05: sampled P1 winrate 0.47 (balanced) BUT greedy P1 winrate = 0.00 with greedy seat bias 0.50 — i.e. against a greedy opponent the seats are fully determined. The race is solvable by rushing; the eval question is whether agent-team play surfaces depth beyond the rush, or confirms the FAIL.
- **Komi is a least-bad pick, not a clean fix.** Across the sweep, raising komi monotonically pushes sampled P1 winrate down (0.63 @ 0 → 0.095 @ 0.30) while greedy bias stays pinned at 0.50 for all komi ≥ 0.05. 0.05 is where sampled seat bias is minimised (0.030); treat seat results with suspicion.
- **Greedy heuristic is influence-only.** The helper's top-K ignores custodian captures entirely. Captures (which flip both ownership AND the influence field) are the real tactical lever — play them by hand and inspect with `--values`.
- **target_dimension_p2 = -1 mirror.** Both players race the same owned-influence accumulator; there is no separate per-player goal axis. Confirm both `P1_to_threshold` and `P2_to_threshold` move off the shared 20.0 target as you play.
- **Vestigial `adjacent_empty`.** The action_rule advertises an adjacency constraint that the engine does not enforce here (first_move_anywhere + grid topology → all empties legal). Do not assume moves must touch existing stones.
- **No holes.** Unlike menger/carpet, grid-8 is fully active (64/64), so any in-range cell id 0–63 is a candidate; pick from the printed "Legal" list each turn.
