# R20 Eval Briefing — Menger — `f98b9414f638`

**Substrate**: Menger sponge (3D, axis 9, 400 active cells of 729 grid positions, Hausdorff dim 2.727, max_degree 6)
**Slate position**: Rank-5 by 15-seed mean GE (0.129), originally ranked #2. Largest finalization Δ in slate (-0.159) — collapsed hardest of the 5 menger games.
**Generation**: 8 (final). Mutation, born gen 4.
**Parents**: `4afa58f6b157`

## Engine scores

| Metric | Value | Notes |
|---|---|---|
| Original GE (3-seed) | 0.288 | Was rank-2 originally |
| **15-seed mean GE** | **0.129** | σ = 0.089, **Δ = −0.159** (biggest collapse in menger top-5) |
| Strategic depth | 0.597 | Lowest of menger top-5 |
| Non-triviality | 1.000 | |
| Strategic diversity | 0.333 | Lowest in slate |
| ELO | 2407 | |
| Pie rule | False | |

## Rules

**Capture**: outnumber-2.
**Propagation**: influence, radius=1, strength=1.0, decay=0.5.
**Win**: threshold-race — first player whose total influence on cells they own exceeds **29.709** wins. `target_dimension_p2 = -1`. **Max turns = 89** (vs 100 for the others). **Threshold = 29.7 vs 57.97 for siblings — half the target.**
**Actions**: place-only. 730 actions = 729 cells + pass.
**Turn structure**: alternating, P1 first.

## PPO training reference (n=12 runs)
- Trained-vs-random WR: **1.000**
- Trained-vs-trained final winrate: **0.500** (balanced)
- Avg game length: **38.8 moves** (range 37.0–40.0) — **less than half the length of siblings**, consistent with the lower threshold target

## Notes
- **The structural odd-one-out in the menger group.** All 4 other menger games target threshold 57.97 over up to 100 turns. This one targets 29.71 over 89 turns. Lower threshold → race ends roughly twice as fast.
- This is the strategic-diversity-0.333 game (lowest in slate) — fewer distinct viable strategies. Consistent with: shorter race favours faster, more local strategies.
- Largest finalization collapse (−0.159) — flagged as the production score most inflated by elite-carryover bias in the report's "5 things finalization changed our minds about" §3.
- gen-4 origin via mutation from `4afa58f6b157`. Lineage older than `b160b1f55378` (gen-6) but younger than `a6385db22c0b` (gen-3).
- Use this game to test the "racier-threshold" axis vs the "longer-grind" axis on the same substrate / family.

## Helper invocation
```
.venv/bin/python eval_run20_helper.py --game f98b9414f638 --moves "<csv>" [--values]
```
