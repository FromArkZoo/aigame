# R8 Replay Eval Briefing — Connection Go — `d4015a646ae3`

**Purpose.** Recalibrate the project's load-bearing quality anchor. R8's `d4015a646ae3` (top-1 by ELO, 8/10 in the February 2026 agent eval) ranks 6/12 by current GE on the R20+R8 calibration slate. Before redesigning the fitness function we must verify the February rating is still valid under the **current R20-protocol rubric and model version**. This is a single-game absolute-rating campaign (no comparison games).

**Substrate**: Flat 2D 8×8 grid (64 active cells, max_degree 4, no holes, no pie rule).
**Run**: R8 (commit era ≈ Feb 2026). Generation 10. Mutation lineage from parent `14be6193ffc7`.
**DB**: `genesis_v2_run8.db` (passed explicitly to the helper via `--db`).

## Engine scores (R8 era)

| Metric | Value |
|---|---|
| Go Essence | **0.386** |
| Strategic depth | 0.545 |
| Non-triviality | 0.825 |
| Strategic diversity | 1.000 |
| Rule simplicity | 0.270 |
| ELO | **2304.6** (top-1 in R8) |
| Pie rule | False |

R8-era 2-seed PPO reference:
- `trained_vs_random`: 0.84 / 0.56
- avg game length: 72.5 / 69.5 turns
- training_steps: ~1.44M each

## Rules — verbatim from `rule_representation`

```json
{
  "num_dimensions": 2, "axis_size": 8,
  "placement_rule": {"target": "empty", "constraint": "anywhere", "first_move_anywhere": true},
  "capture_rule": {"capture_type": "surround", "threshold": 3},
  "propagation_rule": {"prop_type": "influence", "radius": 3, "strength": 0.7149717563606287, "decay": 0.7510267575649336},
  "win_condition": {"condition_type": "connection", "threshold": 0.5, "target_dimension": 1, "max_turns": 100},
  "turn_structure": {"turn_type": "alternating", "pieces_per_turn": 1}
}
```

### Plain-English

**Board.** 8×8 flat grid. Cell index = `y*8 + x`. Max degree 4 (no diagonals; interior cells have 4 neighbours, edges 3, corners 2).

**Turn structure.** Alternating, 1 piece/turn. P1 first. Max_turns = 100.

**Action space.** 65 actions = 64 placement + 1 pass. Place-only.

**Placement.** Any empty cell, anywhere, no first-move restriction.

**Capture — `surround` threshold=3.** Go-style surround. An enemy stone is captured (cleared) when **≥3 of the placer's stones are adjacent to it** (post-placement). The placer's *own* stones can become captured by symmetric application. Captures cascade — a single move can clear a multi-stone enemy chain. Verify on the board before relying on this; the engine's surround implementation may differ slightly from textbook Go (see `engine_v2.py` `_apply_surround_capture` if precision matters).

**Propagation — `influence` r=3, strength≈0.715, decay≈0.751.** On placement at cell `c`, the engine adds `sign * strength * decay^d` to `board_values[cell]` for every cell within graph distance ≤3 of `c`. `sign = +1` for P1, `-1` for P2. Values clamp to [−100, 100]. With strength 0.715 and decay 0.751:
- d=0 (cell itself): ±0.715
- d=1: ±0.537
- d=2: ±0.403
- d=3: ±0.303

The placed stone deposits influence on itself plus a 3-step neighbourhood. **Influence is a positional asset but is NOT the win condition** — see below.

**Win — `connection` (Hex-style asymmetric goals).** First player to form a contiguous chain of their own stones connecting the two opposing faces along their assigned dimension wins. `target_dimension = 1` for P1; P2 gets `(target_dimension + 1) % num_dimensions = 0` by the engine's auto-assign rule (`engine_v2.py:902-904`).

In x/y coordinates:
- **P1 connects top↔bottom** (`y=0` to `y=7` via a chain of P1 stones).
- **P2 connects left↔right** (`x=0` to `x=7` via a chain of P2 stones).

These goals **cross**. On any single cell P1 and P2 contend for the same square but for orthogonal reasons. This is exactly Hex's asymmetric-goal structure with Go stones layered on top.

The `threshold: 0.5` field is **vestigial under connection-win** — `_check_connection` ignores it; it just BFSes the player's owned cells and checks face-to-face reachability (`topology.py:634` `connects_faces`).

Max-turn timeout (100 plies): if neither side connects in time, **no fallback decision rule fires for connection-wins** — game ends without winner (draw). PPO will time out frequently early in training.

**Pie rule.** Off. R8 predates pie.

### Helper invocation

```
.venv/bin/python eval_run20_helper.py --game d4015a646ae3 --db genesis_v2_run8.db --moves "<csv>" [--values]
```

**Helper warning.** The header line `Win: threshold-race > 0.500` is **hardcoded** in `eval_run20_helper.py:header()` — ignore it. The actual win condition is connection, as described above. The engine still correctly applies connection-win semantics; `Done=True Winner=N` in the per-move output is accurate.

Also note: helper's `compute_scores()` and `P1/P2 effective score` lines reflect threshold-race accounting and are **irrelevant for win detection here**. Use them only as a proxy for influence-pressure (it is still a useful number — bigger influence often means more strategic momentum even when not the win condition).

To check whether a connection has formed visually: render the board, mentally BFS the X cells along the y-axis (P1) or the O cells along the x-axis (P2). The engine renders `Done=True Winner=N` on the winning move.

## Verification: a sanity-play

A trivial demonstration sequence (P1 walls x=0, P2 walls x=7):

```
.venv/bin/python eval_run20_helper.py --game d4015a646ae3 --db genesis_v2_run8.db \
  --moves "0,7,8,15,16,23,24,31,32,39,40,47,48,55,56"
```

Result: P1 wins at move 15 by completing the x=0 column (y=0..y=7) — a vertical wall = top↔bottom connection. P2's parallel x=7 column does NOT win (P2 needs horizontal wall, not vertical). No captures fire.

This shows the asymmetric-goal property concretely. Real play will be much messier: both sides race to complete their own axis while blocking the opponent's, with influence accumulation, surround captures, and territory pressure all in play.

## Strategic notes for evaluators (do not over-anchor on these — discover for yourself)

1. **Hex backbone.** The connection-win is structurally identical to Hex (a known to be deeply strategic game with proven theoretical depth). The substrate adds Go-style surround capture + influence accumulation on top.

2. **Influence as pressure, not goal.** The `influence` field accumulates positional value but does not directly win. Why include it? Because PPO sees `board_values` as part of the observation, so it shapes learned policy. Possible interpretation: influence is a "soft territory" signal that biases PPO's evaluation of contested cells.

3. **Surround capture interacts with connection paths.** A P1 chain connecting top-bottom can be **severed mid-build** by a 3-neighbour P2 surround. This is the key novel mechanic: in regular Hex, stones are permanent; here, an exposed stone with 3 enemy neighbours dies. **Are connection chains stable enough to ever win?** That's the central tactical question.

4. **8×8 axis** is unusual — narrower than R17+'s axis-9 or axis-16 standards. Diameter is small; connections are reachable in 8 stones minimum.

5. **Surround threshold=3 on flat grid.** Interior cells have 4 neighbours. So a single P2 cell at an interior P1 chain is captured only when 3 of its 4 neighbours are P1 (one neighbour direction left as an escape). Edge cells (3 neighbours) need all 3 P1; corner cells (2 neighbours) cannot be captured by surround-3 (only 2 neighbours available).

6. **No pie rule.** First-mover advantage is uncompensated. R20+ corpus universally requires pie; R8 era did not. Score balance accordingly.

## Eval style

**This is a single-game absolute-rating campaign.** Use the R20 protocol (Phase 1–5, six scoring dimensions) exactly. **Anchor against published R20 means and R8's own February 8/10 rating.** Do *not* try to "preserve" the historical 8/10 — if the game looks weaker under current protocol, score it as you see it. The point of the exercise is to detect calibration drift.

**Anchors to keep in mind:**
- R8 (this game, Feb 2026 rating): **8/10** "Would an agent team play this again?"
- R17 mean: 3.50
- R19 production mean: 4.375 / R19 menger top: 4.80
- R20 production mean: 3.73 / R20 top: 4.80 (depth record), 4.70 (carpet pie)

**Three branch outcomes the campaign will surface** (do not optimise for any of these — score honestly):
1. **Mean ≥ 7.0, range ≤ 3**: anchor is stable. GE-bottleneck diagnosis stands. Proceed to fitness redesign.
2. **Mean 4–5/10**: February rating was inflated; calibration drifted up. R21 launch with `w_planning=0` is correct.
3. **Range > 4 across 5 teams**: agent-eval is itself unstable. Project validator needs rework before fitness redesign.

## Files

- This briefing: `evaluations/r8_replay/briefing_r8_d4015a646ae3.md`
- Verdicts (one per team): `evaluations/r8_replay/team-{1..5}_game_d4015a646ae3.md`
- Summary: `evaluations/r8_replay/SUMMARY.md`
- Helper (with --db override): `eval_run20_helper.py`
- DB: `genesis_v2_run8.db`
