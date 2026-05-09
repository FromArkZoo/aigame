# R20 Eval Briefing — Carpet — `625bfc1f3f49` ⭐ **ONLY PIE-RULE GAME IN SLATE**

**Substrate**: Sierpinski carpet (2D, axis 9, 64 active cells of 81 grid positions, Hausdorff dim 1.893, max_degree 4)
**Slate position**: Carpet top-1 (and only carpet game). Survived gen 0→8 unchanged because it never went through crossover (which would have stripped pie before the `ac9e642` fix).
**Generation**: 8 (final). **SEED**, born gen 0.
**Parents**: `[]` (seed, no parents)

## Engine scores

| Metric | Value | Notes |
|---|---|---|
| Original GE (3-seed) | 0.118 | |
| **15-seed mean GE** | **0.060** | σ = 0.075 — fails the < 0.03 carpet noise target |
| Strategic depth | 0.645 | Highest carpet depth in R20 |
| Non-triviality | 0.721 | |
| Strategic diversity | 0.667 | |
| ELO | 2125 | Lowest in slate |
| **Pie rule** | **True** | **Only game in slate with pie active** |

## Rules

**Capture**: outnumber-2 — when a stone is placed, any adjacent enemy stone with ≥2 friendly neighbours is captured.
**Propagation**: influence, **radius=2** (vs r=1 for menger games), strength=1.0, decay=0.5 — placement at cell c adds ±1.0 to `board_values[c]`, ±0.5 to its neighbours, ±0.25 to its second-neighbours. Larger footprint than menger.
**Win**: threshold-race — first player whose total influence on cells they own exceeds **30.0** wins. `target_dimension_p2 = -1`. Max turns = 100.
**Actions**: place-only. **83 actions = 81 cells + 1 pass + 1 pie**. Action 82 = PIE (P2 invokes after P1's first move to swap seats).
**Turn structure**: alternating, P1 first. Pie available only on P2's first turn.

## Pie rule mechanics (this game only)

After P1's first move, P2's first decision is whether to invoke pie (action 82). If invoked, the seats swap: the stone P1 placed is now P2's, and the originally-P2 player continues as P1 (and plays next). If not invoked, P2 places normally on their own first turn.

R19 30/30 verdict: "add pie rule" — this is the carpet game where it's actually present. **Verify empirically**: does pie correct the P1 seat advantage that was structural across all R19 games?

## PPO training reference (n=27 runs)
- Trained-vs-random WR: **0.760** (lowest in slate — game is hard to dominate even with random)
- Trained-vs-trained final winrate: **0.500** (balanced — pie may be doing its job)
- Avg game length: **36.5 moves** (range 32.5–38.5)

## Notes
- **Carpet's R20 result was uncomfortable**: 71 of 74 carpet games scored < 0.002. This is the only competitive carpet game, and it survived purely because it was a gen-0 seed that never went through the (broken) crossover.
- Larger influence footprint (r=2 → 13-cell 2D footprint vs 7-cell 3D for menger r=1) on a smaller board (64 cells active) — propagation density is much higher per move. This may explain the shorter games (37 vs 85 plies).
- **Pie rule is the unique mechanic to test.** R19 carpet rank-1 (`ce3a09e05cef`) didn't have pie and scored 4.4. Did pie buy this game anything?
- 0.760 trained-vs-random is unusual — suggests the game has strategic depth that random play doesn't accidentally find (vs menger games where any non-degenerate placement wins vs random).
- 27 PPO runs accumulated as elite — most-tested in slate.
- This is a SEED game (gen 0). The genotype was hand-designed (or randomly initialised by the seed generator), not evolved. Compare against `fcedbc14043d` (gen-4 grid mutation) to test the "seed vs evolved" axis.

## Helper invocation
```
.venv/bin/python eval_run20_helper.py --game 625bfc1f3f49 --moves "<csv>" [--values]
```

To test pie: P1 plays move 1 (e.g., center=`40`), then P2 invokes pie via action `82`. Engine should swap. Use `--values` to confirm the placed stone is now scored for the new P1 seat.
