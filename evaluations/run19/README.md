# R19 Human Eval — Protocol & Index

**Goal**: Produce 30 verdicts (5 evaluator-teams × 6 games) on R19's top games to satisfy goal #4 (first substrate-comparable human eval since R17) and unblock R20 scope decisions.

**Source eval report**: `evaluation_report_run19.md` § "Playability gate" lists the 6 games. § "What's next" defines the protocol. See `R19_postmortem.md` for the smoke-calibration finding that frames R20.

## The 6 games

| File | Substrate | Rank | Game ID | GE | Mechanics |
|---|---|---|---|---:|---|
| `briefing_menger_rank1.md` | Menger | 1 | `1f9191b5d4e6` | 0.3293 | outnumber-2 + inf(r=1) + threshold |
| `briefing_menger_rank2.md` | Menger | 2 | `98739cb0838a` | 0.3213 | outnumber-2 + inf(r=2) + threshold |
| `briefing_menger_rank3.md` | Menger | 3 | `5048f71b62fd` | 0.3158 | surround + inf(r=1) + threshold |
| `briefing_carpet_rank1.md` | Carpet | 1 | `ce3a09e05cef` | 0.3547 | outnumber-2 + inf(r=2) + threshold |
| `briefing_carpet_rank2.md` | Carpet | 2 | `b48208268f2a` | 0.3069 | custodian-2 + inf(r=2) + threshold |
| `briefing_carpet_rank3.md` | Carpet | 3 | `c3427a8ae42b` | 0.2783 | outnumber-2 + inf(r=2,s=0.84,d=0.68) + threshold |

## Protocol

Each evaluator-team:
1. Reads the relevant `briefing_*.md` for the assigned game.
2. Loads `TEMPLATE_team-N_gameXXXX.md` as a starting structure.
3. Plays at minimum 3 games (P1, P2, novelty adversary) using `eval_run19_helper.py`.
4. Runs the 5-phase analysis: rule comprehension → strategic play → joint analysis → novelty adversary → structured verdict.
5. Saves output as `team-{N}_game{GAME_ID}.md`.

5 teams per game × 6 games = 30 verdicts total.

## Helper invocation

```
.venv/bin/python eval_run19_helper.py --game <GAME_ID> --moves "<csv>" [--values]
```

The helper auto-routes to the correct DB. `--values` adds an influence-field render (helpful for threshold-race games where influence shape is the strategy).

## Pilot first

Before running all 30, run **1 pilot per game (6 evals total)** to catch helper/briefing bugs and calibration drift. Output named `team-pilot_game{GAME_ID}.md`. Review pilots for:
- Helper-script issues (illegal action handling, render bugs)
- Missing reference data the briefing should have included
- Scoring scale drift vs. R17 (anchor against R17 mean 3.50, R17 best 4.14, R8 8/10)

Once pilots are clean, run the remaining 24.

## Output

After 30 verdicts, append a "Human evaluation" section to `evaluation_report_run19.md` with:
- Per-game mean ± SD
- Cross-substrate comparison (carpet GE 0.355 vs menger GE 0.329 — does that gap show up in human verdicts?)
- Comparison vs R17 best (4.14) and R8 ceiling (8/10)
- GE-vs-human disagreement table
- Cross-cutting themes per substrate

## File index

```
evaluations/run19/
├── README.md                           ← this file
├── TEMPLATE_team-N_gameXXXX.md         ← reusable verdict skeleton
├── briefing_menger_rank1.md            ← per-game briefings (×6)
├── briefing_menger_rank2.md
├── briefing_menger_rank3.md
├── briefing_carpet_rank1.md
├── briefing_carpet_rank2.md
├── briefing_carpet_rank3.md
└── team-{N}_game{GAME_ID}.md           ← evaluator outputs (×30, populated as runs complete)
```
