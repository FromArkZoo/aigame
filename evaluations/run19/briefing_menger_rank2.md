# R19 Eval Briefing — Menger Rank 2 — `98739cb0838a`

**Substrate**: Menger sponge (3D, axis 9, 400 active cells of 729 grid positions, Hausdorff dim 2.727, max_degree 6)
**Rank**: Menger #2 / 3
**Generation**: 8 (final). Direct seed (m8 — `outnumber-2 + influence(r=2) + threshold-race`).
**Parents**: none (seed survived to final generation).

## Engine scores
| Metric | Value |
|---|---|
| Go Essence (GE) | **0.3213** |
| ELO | 2402.6 |
| Strategic depth | 0.538 |
| Non-triviality | 1.000 |
| Strategic diversity | 1.000 |

## Rules

**Capture**: outnumber-2 — placing a stone clears any adjacent enemy stone that has ≥2 friendly neighbours.
**Propagation**: influence, radius=2, strength=0.9895, decay=0.3037 — placement at cell c adds ±0.99 to c, ±0.30 to distance-1 neighbours, ±0.091 to distance-2 cells.
**Win**: threshold-race — first player whose total influence on cells they own exceeds **38.959** wins. Max turns = 100.
**Actions**: place-only (D1 hybrid ban active). 730 actions = 729 cells + pass.
**Turn structure**: alternating, P1 first.

## PPO training reference
- Trained-vs-random WR (3 unique seeds): **1.000** all three.
- Avg game length: **54.2 moves** (range 52.5–55.5).
- Final winrate (trained vs trained): 0.500 (balanced).

## Notes
- Direct seed that survived 8 generations of mutation/crossover untouched. The R19 evolution kept finding nothing better than this exact rule blob.
- Higher threshold (38.96 vs rank-1's 29.71) and bigger influence radius (r=2 vs r=1) → longer games (54 vs 39 moves) and more late-game tactical complexity expected.
- No soft-rule violations flagged.

## Helper invocation
```
.venv/bin/python eval_run19_helper.py --game 98739cb0838a --moves "<csv>" [--values]
```
