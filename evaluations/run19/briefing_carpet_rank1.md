# R19 Eval Briefing — Carpet Rank 1 — `ce3a09e05cef`

**Substrate**: Sierpinski carpet (2D, axis 9, 64 active cells of 81 grid positions, Hausdorff dim 1.893, max_degree 4)
**Rank**: Carpet #1 / 3 (R19 top-1 carpet, **highest GE in R19 overall**)
**Generation**: 8 (final). Crossover (`blend_topology`).
**Parents**: `eb301d1bf7f6`, `b48208268f2a` (rank-2 of this list — same family)

## Engine scores
| Metric | Value |
|---|---|
| Go Essence (GE) | **0.3547** |
| ELO | 2280.5 |
| Strategic depth | 0.676 |
| Non-triviality | 0.952 |
| Strategic diversity | 1.000 |

## Rules

**Capture**: outnumber-2 — placing a stone clears any adjacent enemy stone that has ≥2 friendly neighbours.
**Propagation**: influence, radius=2, strength=1.0, decay=0.5 — placement adds ±1.0 to c, ±0.5 to distance-1 cells, ±0.25 to distance-2 cells.
**Win**: threshold-race — first player whose total influence on cells they own exceeds **30.000** wins. Max turns = 100.
**Actions**: place-only (D1 hybrid ban active). 82 actions = 81 cells + pass.
**Turn structure**: alternating, P1 first.

## PPO training reference
- Trained-vs-random WR (3 unique seeds × C2 averaging across multiple gens): **0.953** mean (range 0.880–1.000).
- Avg game length: **32.2 moves** (range 28.5–34.5).
- Final winrate (trained vs trained): 0.500 (balanced).

## Notes
- **R19 headline game**: highest GE (0.3547) of all 6 evaluated games. Carpet's only crossover-derived top result.
- Inherits from a direct seed (rank-2 of this eval set) refined by crossover with `eb301d1bf7f6`.
- **Soft violation flagged**: `sierpinski_threshold_inert` (R17 audit found violating games score worse than clean ones, but still allowed). Worth flagging in your novelty / playability analysis.
- Carpet's holes pattern (4 corner 1×1 + 1 center 3×3) makes axis-aligned chains pass through irregular bottlenecks — quite different from menger's symmetric 3D holes.

## Helper invocation
```
.venv/bin/python eval_run19_helper.py --game ce3a09e05cef --moves "<csv>" [--values]
```
