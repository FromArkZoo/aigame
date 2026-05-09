# R20 Eval Briefing — Grid Control — `fcedbc14043d`

**Substrate**: Flat 2D grid (axis 9, 81 active cells of 81 grid positions — no fractal holes, max_degree 4)
**Slate position**: Grid_control top-1 (and only grid game). 4-generation methodology check (axis was reduced from 16 → 9 pre-launch because axis-16 connection rush-broke regardless of pie).
**Generation**: 4 (final). Mutation, born gen 3.
**Parents**: `f233c2d817de`

## Engine scores

| Metric | Value | Notes |
|---|---|---|
| Original GE (3-seed) | 0.214 | |
| **15-seed mean GE** | **0.129** | σ = 0.046 — borderline meets the 0.04 noise target |
| Strategic depth | 0.593 | Lowest of slate |
| Non-triviality | 1.000 | |
| Strategic diversity | 0.667 | |
| ELO | 1942 | Lowest in slate |
| Pie rule | False | |

## Rules

**Capture**: **custodian-2** — only game in slate using custodian rule. Place at cell c such that an enemy run along an axis is bracketed by friendly stones (one being c, one being at least 2 steps away with friendly stones in between forming a closed bracket); the entire enemy run flips owner to placer. Threshold parameter = 2.
**Propagation**: influence, radius=1, strength=1.0, decay=0.5.
**Win**: threshold-race — first player whose total influence on cells they own exceeds **20.0** wins. `target_dimension_p2 = +1` (**different** from the menger/carpet games that use −1; +1 means P2 has a separate accumulator that's not just the negation of P1's). Max turns = 72.
**Actions**: place-only. 82 actions = 81 cells + 1 pass.
**Turn structure**: alternating, P1 first.

## PPO training reference (n=3 runs)
- Trained-vs-random WR: **1.000**
- Trained-vs-trained final winrate: **0.500** (balanced)
- Avg game length: **22.2 moves** (range 20.5–24.5) — **shortest games in slate**

## Notes
- **The mutation that defined the game**: the parent `f233c2d817de` was a connection-win game (R20's seeded R8-revival family). This mutation switched the win condition from connection to threshold-race — and immediately scored 0.214 in production while every other connection-seed scored ~0. The R8-revival negative finding hinges on this fact: even on the most R8-friendly substrate (flat grid, custodian capture), evolution dropped connection within the first generations.
- **Custodian + influence + threshold-race on flat grid** is the closest geometric analog to R8 Connection Go (8/10) we have. R8 was custodian + connection on flat grid. This game shares 2 of 3 axes with R8; the win condition is the only difference. **Use this game to test directly: is connection-win or threshold-race the missing piece between R20-family and R8?**
- **Custodian threshold = 2** has been flagged in R19 carpet rank-2 as "single-stone bracket DOES flip" (briefing → empirical verification). Verify empirically here.
- **target_dimension_p2 = +1** is a different win mechanic than menger/carpet (which use -1, mirror score). Reading the engine's win-check is the first verification step.
- 22-ply average is short — race ends fast, decision density is high per move.
- Only 4 gens of evolution (vs 8 for menger/carpet) — this is a pre-launch axis-reduction control, not a fully-evolved champion.

## Helper invocation
```
.venv/bin/python eval_run20_helper.py --game fcedbc14043d --moves "<csv>" [--values]
```

To compare against R8 directly: ask whether a Go + Othello player would call this game "Othello with influence and a race-clock". If yes, this game is closest to R8's family; if no, the influence/threshold-race shifts it materially.
