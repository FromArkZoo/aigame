# R20 Eval Briefing — Menger — `d1dbc6568fc7`

**Substrate**: Menger sponge (3D, axis 9, 400 active cells of 729 grid positions, Hausdorff dim 2.727, max_degree 6)
**Slate position**: Rank-4 by 15-seed mean GE (0.142), but **rank-2 by strategic depth (0.792)** — the second depth-rich game in the slate. Together with `5f5c72e15220` it tests whether high-depth-mid-GE games are systematically richer than mid-depth-high-GE games.
**Generation**: 8 (final). Mutation, born gen 6.
**Parents**: `c850f91a55b4` (the original GE-rank-1 game that collapsed under finalization)

## Engine scores

| Metric | Value | Notes |
|---|---|---|
| Original GE (3-seed) | 0.209 | |
| **15-seed mean GE** | **0.142** | σ = 0.105 |
| **Strategic depth** | **0.792** | Second-highest in slate |
| Non-triviality | 0.667 | |
| Strategic diversity | 0.667 | |
| ELO | 2310 | |
| Pie rule | False | |

## Rules

**Capture**: outnumber-2.
**Propagation**: influence, radius=1, strength=1.0, decay=0.5.
**Win**: threshold-race — first player whose total influence on cells they own exceeds **57.974** wins. `target_dimension_p2 = -1`. Max turns = 100.
**Actions**: place-only. 730 actions = 729 cells + pass.
**Turn structure**: alternating, P1 first.

## PPO training reference (n=3 runs)
- Trained-vs-random WR: **1.000**
- Trained-vs-trained final winrate: **0.667** (P1-favoured)
- Avg game length: **79.7 moves** (range 77.5–82.5) — tight range

## Notes
- **Parameter sibling of `a6385db22c0b` and `b160b1f55378`** at the rule level. The differentiator is the lineage: this game is a single mutation off `c850f91a55b4` — the original GE-rank-1 that fell to seventh after honest re-scoring. The mutation found a deeper but lower-GE attractor.
- Pairs with `5f5c72e15220` (depth 0.894) as the slate's depth-rich pair. Score these two together: do they share a structural property the GE-top-3 don't?
- `c850f91a55b4` lineage: parent collapsed in finalization (Δ -0.234). This descendant landed at -0.067 — much more stable. Suggests the mutation found a less-luck-sensitive attractor.
- gen-6 origin (mid-evolution).
- Compare carefully against `a6385db22c0b` (rank-1 by GE, depth 0.763) — both are gen-6/3 outnumber-2 + r=1 + thresh-57.97. Why does `d1dbc6568fc7` measure deeper?

## Helper invocation
```
.venv/bin/python eval_run20_helper.py --game d1dbc6568fc7 --moves "<csv>" [--values]
```
