# R19 Eval Briefing — Menger Rank 1 — `1f9191b5d4e6`

**Substrate**: Menger sponge (3D, axis 9, 400 active cells of 729 grid positions, Hausdorff dim 2.727, max_degree 6)
**Rank**: Menger #1 / 3 (R19 top-1 overall)
**Generation**: 8 (final). Crossover.
**Parents**: `5d77199915e0` (R19 menger lineage)

## Engine scores
| Metric | Value |
|---|---|
| Go Essence (GE) | **0.3293** |
| ELO | 2402.4 |
| Strategic depth | 0.561 |
| Non-triviality | 1.000 |
| Strategic diversity | 1.000 |

## Rules

**Capture**: outnumber-2 — placing a stone clears any adjacent enemy stone that has ≥2 friendly neighbours.
**Propagation**: influence, radius=1, strength=1.0, decay=0.5 — placement at cell c adds ±1.0 to board_values[c] and ±0.5 to its 6 axis-aligned neighbours (sign = +1 for P1, −1 for P2). Clamped to [−100, 100].
**Win**: threshold-race — first player whose total influence on cells they own exceeds **29.709** wins. Margin tie → draw. Max turns = 89.
**Actions**: place-only (D1 hybrid ban active). 730 actions = 729 cells + pass. Legal at any empty active cell.
**Turn structure**: alternating, P1 first.

## PPO training reference
- Trained-vs-random WR (3 unique seeds × C2 averaging): **1.000** all three (deterministic dominance over random).
- Avg game length: **38.8 moves** (range 36.0–42.5).
- Final winrate (trained vs trained): 0.500 (balanced).

## Notes
- This is the menger top-1 game, slightly under R19's 0.35 stretch goal but inside the ±0.07 noise band.
- Family is: outnumber capture + radius-1 influence + threshold-race — the dominant family across menger top-10.
- No soft-rule violations flagged.

## Helper invocation
```
.venv/bin/python eval_run19_helper.py --game 1f9191b5d4e6 --moves "<csv>" [--values]
```
The `--values` flag adds an influence-field render. Initial state: `--moves ""`.
