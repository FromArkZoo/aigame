# R19 Eval Briefing — Carpet Rank 2 — `b48208268f2a`

**Substrate**: Sierpinski carpet (2D, axis 9, 64 active cells of 81 grid positions, Hausdorff dim 1.893, max_degree 4)
**Rank**: Carpet #2 / 3
**Generation**: 8 (final). Direct seed (c3 — `custodian-2 + influence(r=2) + threshold-race`).
**Parents**: none.

## Engine scores
| Metric | Value |
|---|---|
| Go Essence (GE) | **0.3069** |
| ELO | 2255.7 |
| Strategic depth | 0.599 |
| Non-triviality | 0.643 |
| Strategic diversity | 0.667 |

## Rules

**Capture**: custodian-2 — Othello-style sandwich. A contiguous run of enemy stones bracketed by friendly stones flips to the placer (along axis-aligned directions, no boundary wrap).
**Propagation**: influence, radius=2, strength=1.0, decay=0.5 (same kernel as rank-1).
**Win**: threshold-race — first player whose total influence on cells they own exceeds **30.000** wins. Max turns = 100.
**Actions**: place-only (D1 hybrid ban active). 82 actions = 81 cells + pass.
**Turn structure**: alternating, P1 first.

## PPO training reference
- Trained-vs-random WR (3 unique seeds): **0.707** mean (range 0.520–0.840) — lower than the other 5 games.
- Avg game length: **37.2 moves** (range 34.5–39.5).
- Final winrate (trained vs trained): 0.500 (balanced).

## Notes
- Custodian capture instead of outnumber — sandwich-and-flip mechanic, not stone-removal. Captured stones change colour and contribute to the captor's threshold race (because their owner flipped, not their position cleared).
- Lower trained-vs-random WR (0.707) than the other 5 games (which sit ≥0.95). Means PPO's learned policy is less dominant over random — could indicate either harder-to-learn strategy or a noisier strategic surface.
- Lower non-triviality (0.643) and strategic diversity (0.667) than the others — fewer distinct strong strategies surfaced during training.
- This is the parent of carpet rank-1 (the crossover champion). Comparing the two should reveal what the crossover added.
- No soft-rule violations flagged.

## Helper invocation
```
.venv/bin/python eval_run19_helper.py --game b48208268f2a --moves "<csv>" [--values]
```
