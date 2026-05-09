# R20 Agent-Team Eval — Protocol & Index

**Goal**: Produce 35 verdicts (5 evaluator-teams × 7 games) on R20 Option-C slate to settle goal #2 (best R20 game beats R19 ceiling) and surface strategic-depth findings on R20's depth-record menger games. Output: append § Agent-team evaluation results to `evaluation_report_run20.md`.

**Source eval report**: `evaluation_report_run20.md` § "Agent-team evaluation — slate proposal" (Option C). § "Champion finalization (S3)" gives 15-seed mean GE / σ for each game. **NOTE**: this is **agent-team eval**, not human eval. Verdicts are written by Claude-agent teams playing the games and scoring agent-relevant strategic-depth properties; the 1-10 anchor is carried from R19 only for continuity (R8 ceiling 8/10, R17 mean 3.50, R19 production mean 4.375).

**`feedback_ge_under_rewards_depth.md`**: GE systematically under-rewards depth. Two depth-rich games (`5f5c72e15220` depth 0.894, `d1dbc6568fc7` depth 0.792) sit in the slate alongside the 15-seed-mean top-5 specifically to test whether agent verdicts agree with GE rank or with depth rank.

## The 7 games (Option-C slate)

| File | Substrate | Game ID | 15-seed GE | σ | Depth | Family |
|---|---|---|---:|---:|---:|---|
| `briefing_menger_a6385db22c0b.md` | menger | `a6385db22c0b` | 0.241 | 0.120 | 0.763 | outnumber-2 + inf(r=1) + thresh-race |
| `briefing_menger_b160b1f55378.md` | menger | `b160b1f55378` | 0.180 | 0.074 | 0.690 | outnumber-2 + inf(r=1) + thresh-race |
| `briefing_menger_5f5c72e15220.md` | menger | `5f5c72e15220` | 0.171 | 0.129 | **0.894** | outnumber-3 + inf(r=1) + thresh-race |
| `briefing_menger_d1dbc6568fc7.md` | menger | `d1dbc6568fc7` | 0.142 | 0.105 | 0.792 | outnumber-2 + inf(r=1) + thresh-race |
| `briefing_menger_f98b9414f638.md` | menger | `f98b9414f638` | 0.129 | 0.089 | 0.597 | outnumber-2 + inf(r=1) + thresh-race(29.7) |
| `briefing_carpet_625bfc1f3f49.md` | carpet | `625bfc1f3f49` | 0.060 | 0.075 | 0.645 | outnumber-2 + inf(r=2) + thresh-race **+ pie** |
| `briefing_grid_fcedbc14043d.md` | grid | `fcedbc14043d` | 0.129 | 0.046 | 0.593 | custodian-2 + inf(r=1) + thresh-race |

Five of seven menger games + carpet top-1 + grid top-1. **Only `625bfc1f3f49` has pie_rule=True** (it's a gen-0 seed; the rest lost pie in crossover before the bug was fixed in `ac9e642`).

## Protocol

Each evaluator-team plays **all 7 games sequentially** (mirrors R19's per-team-runs-all-games structure):

1. Read the briefing for the game (`briefing_<substrate>_<gameid>.md`).
2. Open the template `TEMPLATE_team-N_gameXXXX.md` for that team's verdict.
3. Play **at minimum 3 games** (P1 line, P2 line, novelty/adversary line) using `eval_run20_helper.py`.
4. Run the 5-phase analysis: rule comprehension → strategic play → joint analysis → novelty adversary → structured verdict.
5. Save output as `evaluations/run20/team-{N}_game{GAME_ID}.md`.

5 teams × 7 games = **35 verdicts total**.

## Helper invocation

```
.venv/bin/python eval_run20_helper.py --game <GAME_ID> --moves "<csv>" [--values]
```

Auto-routes to the correct DB. `--values` adds the influence-field render — **enable it during play**, not just at end-of-game (R19 lesson 2). The greedy top-K is influence-delta only and ignores capture potential (R19 lesson 4) — verify capture lines manually.

## Calibration anchors (R19 carry-forward)

- **R8 Connection Go**: 8.0 (all-time ceiling)
- **R17 mean**: 3.50; R17 best (`44f6630277b3`): 4.14
- **R19 menger top-1** (`1f9191b5d4e6`): 4.8; R19 menger top-3 (`5048f71b62fd` surround): 5.0
- **R19 carpet top-1** (`ce3a09e05cef`): 4.4
- **R19 production-only mean**: 4.375

Production teams should re-read at least one R17 verdict (e.g., `evaluations/run17/team-1_game44f6630277b3.md`) before scoring to keep the scale honest. R19 pilot drifted upward (4.83) and was pulled back to 4.375 by 4 production teams; R20 expects a similar pattern.

## R20-specific calibration notes

- **All R20 menger games are the same family** (`outnumber-2 + influence(r=1) + threshold-race(57.97)`). Don't double-count "novelty of the family" — score each game's *intra-family* differentiator (capture threshold, threshold target, gen-of-origin).
- **`5f5c72e15220` is the depth record (0.894).** This is the GE-vs-depth disagreement game: rank-3 by 15-seed mean GE but rank-1 by depth. Agent-team verdicts here are the project's primary signal for whether GE or depth is the better proxy.
- **`625bfc1f3f49` is the only pie-rule game in the slate.** The carpet 30/30 R19 verdict was "add pie rule"; this game has it. Test whether pie does what it's supposed to do (mirror balance) or sits inert.
- **`fcedbc14043d` uses custodian capture on a flat 9×9 grid.** Closest to R8 Connection Go's geometry. Closest to a "control" check on whether grid-9 + custodian can deliver depth without fractal substrate or 3D.

## Pilot first

Run **1 pilot per game (7 evals)** before the production teams to catch helper/briefing bugs. Output `team-pilot_game{GAME_ID}.md`. Review pilots for:
- Helper-script issues (illegal-action handling, render bugs, pie-action handling on `625bfc1f3f49`)
- Missing reference data the briefing should have included
- Scoring scale drift vs R19 production mean 4.375
- Family lock-in collapse (4 of 5 menger games are parameter siblings — pilot may notice they read the same)

Once pilots are clean, the 4 production teams run their 7 games each (28 verdicts).

### Pilot results (campaign 2026-05-09)

team-pilot mean **3.86** across 7 games. Calibration honest (between R17 mean 3.50 and R19 production 4.375). Per-game pilot scores: 3/3/**6**/3/3/5/4 (a6385db22c0b/b160b1f55378/5f5c72e15220/d1dbc6568fc7/f98b9414f638/625bfc1f3f49/fcedbc14043d).

**Helper**: clean. Pie action 82 works on `625bfc1f3f49`; captures render correctly (cleared vs flipped); illegal-action handling clean.

**Critical structural finding for production teams**: pilot empirically verified that **`a6385db22c0b`, `b160b1f55378`, and `d1dbc6568fc7` have BYTE-IDENTICAL rule blobs** (same capture rule + threshold + propagation kernel + win condition + pie + max_turns). The 0.763 / 0.690 / 0.792 depth differences are pure measurement noise. Production teams: **don't waste effort searching for structural differentiators among the menger outnumber-2 trio** — the briefings ask "why does X measure deeper?" but the answer is "it doesn't structurally." The differentiator is lineage-only.

**The structural odd-ones-out within the menger group**:
- `5f5c72e15220` — outnumber-**3** (vs -2 in siblings); genuinely different game with double-capture, residual-value harvest, cluster-deepening tactics. Pilot rated **6/10** (highest in slate). Confirms `feedback_ge_under_rewards_depth.md` — depth wins as a fitness signal *when rule kernels differ*.
- `f98b9414f638` — threshold=29.71 (vs 57.97); racier, shorter games, balance-preserving.

**GE-vs-depth headline**: depth was right where the rules genuinely differed (`5f5c72e15220`), but depth scores within the byte-identical trio are noise. R21 implication: weight depth in fitness only after enforcing rule-kernel diversity in selection.

**Pie rule** (only in `625bfc1f3f49`): empirically works. Pilot read: pie is structurally a no-op for tempo balance — transfers first-stone advantage to whichever side claims it; trained-vs-trained 0.500 reflects equilibrium where pie usage is rational, not where pie equalizes seats.

## Output (final § Agent-team evaluation results)

After 35 verdicts, append a § Agent-team evaluation results section to `evaluation_report_run20.md` with:
- Per-game mean ± SD across 5 teams
- Per-team mean (calibration anchors)
- Cross-substrate comparison (menger vs carpet vs grid) — annotated for noise overlap per finalization rules (gap > max σ to claim separation)
- GE-vs-eval rank disagreement table (especially: does `5f5c72e15220`'s depth advantage show up in agent verdicts?)
- Comparison vs R19 (4.8 menger top, 4.4 carpet top), R17 (4.14 best), R8 (8.0 ceiling)
- Cross-cutting themes per substrate
- R21 implications

## File index

```
evaluations/run20/
├── README.md                                ← this file
├── TEMPLATE_team-N_gameXXXX.md              ← reusable verdict skeleton
├── briefing_menger_a6385db22c0b.md          ← per-game briefings (×7)
├── briefing_menger_b160b1f55378.md
├── briefing_menger_5f5c72e15220.md          ← depth record 0.894
├── briefing_menger_d1dbc6568fc7.md
├── briefing_menger_f98b9414f638.md
├── briefing_carpet_625bfc1f3f49.md          ← only pie-rule game
├── briefing_grid_fcedbc14043d.md            ← grid control
└── team-{N}_game{GAME_ID}.md                ← evaluator outputs (×35)
```
