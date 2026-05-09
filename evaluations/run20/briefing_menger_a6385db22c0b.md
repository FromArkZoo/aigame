# R20 Eval Briefing — Menger — `a6385db22c0b`

**Substrate**: Menger sponge (3D, axis 9, 400 active cells of 729 grid positions, Hausdorff dim 2.727, max_degree 6)
**Slate position**: Rank-1 by 15-seed mean GE (0.241) — was rank-5 by original 3-seed GE before finalization. Original GE-rank-1 (`c850f91a55b4`) collapsed under re-scoring; this game climbed.
**Generation**: 8 (final). Crossover (parameter_blend), born gen 3.
**Parents**: `baf9ba3ae935`, `aa509e54dbf9`

## Engine scores

| Metric | Value | Notes |
|---|---|---|
| Original GE (3-seed) | 0.262 | Production noisy estimate |
| **15-seed mean GE** | **0.241** | σ = 0.120, range 0.144–0.417 |
| Strategic depth | 0.763 | Top quartile of R20 menger |
| Non-triviality | 0.653 | |
| Strategic diversity | 1.000 | |
| ELO | 2336 | |
| Pie rule | False | (lost in crossover before `ac9e642` fix) |

## Rules

**Capture**: outnumber-2 — when a stone is placed, any adjacent enemy stone with ≥2 friendly neighbours (counting the just-placed stone) is captured (cleared to empty).
**Propagation**: influence, radius=1, strength=1.0, decay=0.5 — placement at cell c adds ±1.0 to `board_values[c]` and ±0.5 to its ≤6 axis-aligned neighbours. Sign = +1 for P1, −1 for P2. Clamped to [−100, 100].
**Win**: threshold-race — first player whose total influence on cells they own exceeds **57.974** wins. `target_dimension_p2 = -1` means P2's accumulator is the negation of P1's (mirror score). Margin tie → draw. Max turns = 100.
**Actions**: place-only (D1 hybrid ban active). 730 actions = 729 cells + 1 pass. Legal at any empty active cell.
**Turn structure**: alternating, P1 first.

## PPO training reference (n=18 runs, accumulated as elite)
- Trained-vs-random WR avg: **0.980** (range close to 1.0, robust dominance)
- Trained-vs-trained final winrate avg: **0.667** (P1-favoured)
- Avg game length: **85.0 moves** (range 80.0–92.0) — long games, threshold-race grinds out
- 18 runs because elite carryover re-scored this game multiple generations

## Notes
- Top-1 by 15-seed honest re-scoring; the headline slate game.
- Long games (85 plies / max 100) suggest threshold-race plays out near max-turn timeout — depth is in the protracted accumulation, not a sharp endgame.
- Family = `outnumber-2 + influence(r=1) + threshold-race(57.97)` is the dominant menger family. Compare against `b160b1f55378`, `d1dbc6568fc7` which share it exactly (parameter siblings). This game's distinguisher: gen-3 origin via parameter_blend (older lineage than the gen-6+ siblings).
- No soft-rule violations.
- 0.667 trained-vs-trained suggests measurable P1-favoured imbalance even after PPO. Pie rule is OFF here — predict mirror = P1 wins and look for asymmetric P2 counters.

## Helper invocation
```
.venv/bin/python eval_run20_helper.py --game a6385db22c0b --moves "<csv>" [--values]
```
Initial state: `--moves ""`. Use `--values` during play to track influence buildup — threshold target 57.97 is large and accumulation is the whole game.
