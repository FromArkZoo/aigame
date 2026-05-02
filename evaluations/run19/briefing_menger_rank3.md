# R19 Eval Briefing — Menger Rank 3 — `5048f71b62fd`

**Substrate**: Menger sponge (3D, axis 9, 400 active cells of 729 grid positions, Hausdorff dim 2.727, max_degree 6)
**Rank**: Menger #3 / 3
**Generation**: 8 (final). Crossover.
**Parents**: `ebf0a3e1c424`, `d21ef16c4945`

## Engine scores
| Metric | Value |
|---|---|
| Go Essence (GE) | **0.3158** |
| ELO | 2354.6 |
| Strategic depth | 0.640 |
| Non-triviality | 1.000 |
| Strategic diversity | 1.000 |

## Rules

**Capture**: surround-2 — Go-style. An enemy group with no liberties (≥2 friendly neighbours blocking) is removed entirely.
**Propagation**: influence, radius=1, strength=1.0, decay=0.5 (same kernel as rank-1).
**Win**: threshold-race — first player whose total influence on cells they own exceeds **21.212** wins. Lowest threshold of the 6 games. Max turns = 71.
**Actions**: place-only (D1 hybrid ban active). 730 actions = 729 cells + pass.
**Turn structure**: alternating, P1 first.

## PPO training reference
- Trained-vs-random WR (3 unique seeds): **1.000** all three.
- Avg game length: **27.2 moves** (range 23.5–30.5) — the shortest of the 3 menger games.
- Final winrate (trained vs trained): 0.500 (balanced).

## Notes
- Surround capture (Go-style) instead of outnumber. The eval report flags this game as the one whose gen-6 leadership was dethroned by outnumber-based crossovers in gen 7-8.
- Lowest threshold (21.2) and shortest games (27 moves) — expect tactical, racing-style play with fast resolution.
- Surround capture in 3D is geometry-dependent (R17 finding) — interior cells have 6 neighbours, edge/corner cells fewer. Watch whether captures actually fire on the menger's irregular topology.
- No soft-rule violations flagged.

## Helper invocation
```
.venv/bin/python eval_run19_helper.py --game 5048f71b62fd --moves "<csv>" [--values]
```
