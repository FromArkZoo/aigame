# R21 Eval Briefing — Menger — `e1453dac5445`

**Substrate**: menger 3D axis-9 400/729 active Hausdorff 2.727 max_degree 6 (verified live: total_cells 729, active 400, max_degree 6)
**Slate position**: R21 top — rank 1 of slate by 20-seed mean GE (0.177)
**Calibrated komi_p2**: 0 (G3 gate: bias 0.060 at komi=0; positive komi OVERCORRECTS and flips P2 ahead, so komi=0 is served — below the G3 0.10 target and did NOT clear the strict 2σ lock-in)

## Engine scores
| Metric | Value | Notes |
|---|---|---|
| 20-seed mean GE | 0.177 | slate headline (mean across 20 training seeds) |
| GE sigma | 0.101 | high relative dispersion; ~15% of seeds are a structural PPO-failure mode (bimodal, not Gaussian) |
| go_essence (DB, single eval) | 0.181 | from `scores` table this DB — consistent with the 20-seed mean |
| strategic_depth | 0.595 | DB-verified |
| non_triviality | 0.667 | DB-verified |
| strategic_diversity | 0.181 | DB-verified — LOW; play tends to collapse toward fill-the-densest-column |
| rule_simplicity | 0.254 | DB-verified |
| elo (internal) | 2055 | DB-verified |
| pie_rule | True | verified live |
| komi_p2 | 0 | calibrated; see gate note above |

## Rules
**Capture** — `outnumber`, threshold 2. A stone is removed when the opponent outnumbers its owner by ≥2 among its lattice neighbors (radius-1 adjacency). Captures CLEAR to empty (verified live: P2 at (2,0,0) flanked by P1 at (1,0,0) and (3,0,0) was cleared once P1 led by 2 neighbors — not flipped to P1). Capturing also removes that stone's influence contribution, so it can drop your own accumulator.

**Propagation** — `influence`, radius 1, strength 1.0, **decay 1.0**. Each placed stone deposits +1 (sign by player) on its own cell and +1 on every active neighbor within radius 1 — *flat, no distance falloff*. This decay=1.0 is the structural signature distinguishing R21 from the R20 champions (decay 0.5–0.7). Holes (`#`) carry no influence and break neighborhoods, so contiguous-active runs (e.g. a full edge column) compound much faster than scattered placements.

**Win condition** — `threshold-race` (dispatch: NOT connection). A player wins the instant their effective owned-influence accumulator exceeds **30.0**. Accumulator = sum over active cells of `board_values` signed by owner (P1 positive, P2 negative-then-flipped). `target_dimension_p2 = -1` ⇒ P2 mirrors P1's accumulator (no separate axis). `max_turns = 100` — a hard cap; if neither side clears 30 by then the game ends (shorter than the R20 100+ games in practice because decay=1.0 makes the race fast). Verified live: a 4-stone contiguous P1 column reached +10 accumulator.

**Actions** — `place` only, on empty cells, `adjacent_empty` constraint with `first_move_anywhere=True` (opening can go anywhere; subsequent placements must be adjacent-empty). num_actions = 731 = 729 cells + pass + swap.

**Turn structure** — alternating, 1 piece per turn. **Pie/swap balancing**: pie_rule=True; the swap action id = total_cells+1 = **730** (P2 may swap seats after P1's first move). komi_p2 is 0, so balancing rests on the pie swap alone.

## How to play it (helper)
```
.venv/bin/python eval_run21_helper.py --game e1453dac5445 --moves "<csv>" [--values]
```
(komi auto-applies at 0; pie/swap action id = total_cells+1 = 730; greedy top-K is influence-delta only and IGNORES captures — verify capture lines manually. Enable `--values` during play to see the influence field.)

## Notes for evaluators
- **The headline "did R21 find something new?" game.** It is structurally distinct from R20 champions: decay=1.0 (flat influence) plus a fast threshold-30 race. Judge whether that flatness produces genuinely different strategy or just a faster fill-the-board sprint.
- **Mean is real signal, not a lucky seed** (Probe B: ~50% of reruns score >0.20, depth stable). Treat the 0.177 mean as the true level.
- **Bimodal seed risk**: ~15% of training seeds collapse into a PPO-failure mode (the sigma 0.101 is not Gaussian dispersion — it is a mixture). Engine numbers are trustworthy; the *training* of any single agent on this game is the fragile part.
- **Komi gate did NOT fully lock in.** Residual P1 bias 0.060 at komi=0; the only available komi value overcorrects and hands P2 the lead, so komi=0 was chosen as the lesser bias. This is below the G3 0.10 target — watch for a mild first-mover edge in your games and lean on the pie swap (action 730) to balance.
- **Captures suppress your own score.** Because the accumulator sums live influence, clearing an opponent stone removes its (negative-to-you) contribution but can also expose your stones to recapture and re-zeroes contested edges (verified: P1 fell back to +0.000 after a capture). The greedy helper will not warn you — capture and influence-race objectives partly conflict here.
- **Low strategic_diversity (0.181).** Expect optimal lines to converge on packing the densest contiguous active region (full edge columns / face strips that avoid the central holes). Reward genuinely varied winning plans cautiously.
- **Holes dominate geometry.** 329 of 729 cells are dead; the central 3×3×3 (and recursive sub-cubes) are gone. The active set is a thin shell — neighborhoods are sparse and max_degree caps at 6, so a stone rarely touches its full 6 neighbors.
- No vestigial-field degeneracy detected: threshold is live (threshold-race, not connection), pie+komi both wired, propagation active. The only soft flag is the un-locked komi gate and the bimodal training risk above.
