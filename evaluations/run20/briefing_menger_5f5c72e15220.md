# R20 Eval Briefing — Menger — `5f5c72e15220` ⭐ **DEPTH RECORD 0.894**

**Substrate**: Menger sponge (3D, axis 9, 400 active cells of 729 grid positions, Hausdorff dim 2.727, max_degree 6)
**Slate position**: Rank-3 by 15-seed mean GE (0.171), but **rank-1 by strategic depth (0.894)** — the highest depth score in any aigame run. Prior R-run max was ~0.55. **This is the GE-vs-depth disagreement game.**
**Generation**: 8 (final). Crossover (blend_topology), born gen 8.
**Parents**: `7a4f4c257f00`, `be31be482a6a`

## Engine scores

| Metric | Value | Notes |
|---|---|---|
| Original GE (3-seed) | 0.173 | Mid-pack on GE |
| **15-seed mean GE** | **0.171** | σ = 0.129, range 0.019–0.309 (widest noise) |
| **Strategic depth** | **0.894** | Highest in any aigame run |
| Non-triviality | 0.667 | |
| Strategic diversity | 0.667 | |
| ELO | 2223 | Lowest of menger top-5 |
| Pie rule | False | |

## Rules

**Capture**: outnumber-**3** (note: stricter than the rest — needs ≥3 friendly neighbours adjacent to the enemy stone, vs 2 for siblings) — captures fire less often, board accumulates more.
**Propagation**: influence, radius=1, strength=1.0, decay=0.5.
**Win**: threshold-race — first player whose total influence on cells they own exceeds **57.974** wins. `target_dimension_p2 = -1`. Max turns = 100.
**Actions**: place-only. 730 actions = 729 cells + pass.
**Turn structure**: alternating, P1 first.

## PPO training reference (n=3 runs)
- Trained-vs-random WR: **1.000** (deterministic over random)
- Trained-vs-trained final winrate: **0.333** — **P2-favoured imbalance** (only menger game with P2 lead)
- Avg game length: **80.7 moves** (range 71.0–96.0) — wide variance suggests divergent-strategy seeds

## Notes
- **The big test of `feedback_ge_under_rewards_depth.md`.** GE places this rank-3, depth places it rank-1. If agent verdicts agree with the depth ranking, R21 should weight depth in the fitness function. If they agree with GE, the depth metric is the suspect.
- **outnumber-3** capture (vs outnumber-2 in siblings) is the structural differentiator. With stricter capture conditions, fewer cells clear, propagation accumulates longer, and games run deeper.
- **P2-favoured trained-vs-trained (0.333)** is the inverse of `a6385db22c0b` (0.667). Combined: this game might be the only menger candidate with a real P2 strategy worth the seat. Or it's an artifact of the 3-run sample.
- Variance in game length (71–96) suggests multiple lines exist — strategic-diversity 0.667 is consistent but the variance hint is bigger.
- gen-8 origin: youngest in the slate — selection just discovered this attractor at the very end.
- 3 runs only (no elite carryover yet — was added late).

## Helper invocation
```
.venv/bin/python eval_run20_helper.py --game 5f5c72e15220 --moves "<csv>" [--values]
```
**Recommended**: spend extra time on this game. Phase-3 strategic depth analysis is the headline evidence for whether R20's depth findings hold up to agent inspection.
