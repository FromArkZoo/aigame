# R20 Eval Briefing — Menger — `b160b1f55378`

**Substrate**: Menger sponge (3D, axis 9, 400 active cells of 729 grid positions, Hausdorff dim 2.727, max_degree 6)
**Slate position**: Rank-2 by 15-seed mean GE (0.180). Was rank-3 by original 3-seed GE.
**Generation**: 8 (final). Crossover (blend_topology), born gen 6.
**Parents**: `f8acede1c192`, `63725e2b1ad0`

## Engine scores

| Metric | Value | Notes |
|---|---|---|
| Original GE (3-seed) | 0.274 | |
| **15-seed mean GE** | **0.180** | σ = 0.074 (tightest band among the menger top-5) |
| Strategic depth | 0.690 | |
| Non-triviality | 1.000 | |
| Strategic diversity | 0.667 | |
| ELO | 2409 | Highest ELO in slate |
| Pie rule | False | |

## Rules

**Capture**: outnumber-2 — when a stone is placed, any adjacent enemy stone with ≥2 friendly neighbours is captured (cleared).
**Propagation**: influence, radius=1, strength=1.0, decay=0.5 — same kernel as `a6385db22c0b`.
**Win**: threshold-race — first player whose total influence on cells they own exceeds **57.974** wins. `target_dimension_p2 = -1` (mirror).  Max turns = 100.
**Actions**: place-only. 730 actions = 729 cells + pass.
**Turn structure**: alternating, P1 first.

## PPO training reference (n=9 runs)
- Trained-vs-random WR: **1.000** (deterministic)
- Trained-vs-trained final winrate: **0.500** (balanced)
- Avg game length: **85.5 moves** (range 84.5–86.5) — extremely consistent length

## Notes
- **Parameter sibling of `a6385db22c0b` and `d1dbc6568fc7`** — same capture-threshold-prop kernel, just different gen lineage. R19 lesson 5 ("don't repeat menger rank-1+rank-2 pairing — they're parameter siblings") applies in spades to R20: 4 of 5 menger games here are siblings.
- Tightest noise band (σ=0.074) of the menger top-5. Most reliable score in the menger slate.
- Balanced trained-vs-trained (0.500) — closest to seat-balanced of the menger group. Don't expect a P1 dominance in this one.
- High ELO (2409) reflects strong PPO-vs-PPO separation across seeds.
- gen-6 lineage (vs gen-3 for `a6385db22c0b`) — younger generation, presumably more refined under selection.

## Helper invocation
```
.venv/bin/python eval_run20_helper.py --game b160b1f55378 --moves "<csv>" [--values]
```
