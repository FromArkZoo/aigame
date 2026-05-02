# R19 Eval Briefing — Carpet Rank 3 — `c3427a8ae42b`

**Substrate**: Sierpinski carpet (2D, axis 9, 64 active cells of 81 grid positions, Hausdorff dim 1.893, max_degree 4)
**Rank**: Carpet #3 / 3
**Generation**: 8 (final). Direct seed (c1 — `outnumber-2 + influence(r=2) + threshold-race` with custom strength/decay).
**Parents**: none.

## Engine scores
| Metric | Value |
|---|---|
| Go Essence (GE) | **0.2783** |
| ELO | 2232.9 |
| Strategic depth | 0.531 |
| Non-triviality | 0.973 |
| Strategic diversity | 1.000 |

## Rules

**Capture**: outnumber-2 — placing a stone clears any adjacent enemy stone that has ≥2 friendly neighbours.
**Propagation**: influence, radius=2, strength=**0.8371**, decay=**0.6759** — non-default. Slower decay (0.68 vs 0.50) means the influence field reaches farther; lower strength (0.84 vs 1.00) means each placement contributes less locally. Net effect: flatter, more diffuse influence field.
**Win**: threshold-race — first player whose total influence on cells they own exceeds **25.112** wins. Max turns = 116 (longest of the 6 games).
**Actions**: place-only (D1 hybrid ban active). 82 actions = 81 cells + pass.
**Turn structure**: alternating, P1 first.

## PPO training reference
- Trained-vs-random WR (3 unique seeds): **0.973** mean (range 0.920–1.000).
- Avg game length: **27.2 moves** (range 17.0–43.5) — high variance suggests the strategic surface has multiple speed regimes.
- Final winrate (trained vs trained): mixed (0.000, 0.500, 1.000 across seeds) — suggests possible seat-bias dependent on training seed.

## Notes
- Lowest threshold (25.1) of the 3 carpet games but longest max_turns (116) — broad time window.
- Non-default propagation params (strength=0.84, decay=0.68) make this a lower-tempo, more diffuse-influence variant of the carpet family.
- High variance in game length (17–44 moves) and final-winrate volatility — possibly less stable strategy convergence than the others. Worth probing whether seat balance is genuine or seed-dependent.
- No soft-rule violations flagged.

## Helper invocation
```
.venv/bin/python eval_run19_helper.py --game c3427a8ae42b --moves "<csv>" [--values]
```
