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

## Pilot results & lessons (committed `9fda4dd`, 2026-05-02)

All 6 pilots ran clean. Pilot mean **4.83**; per-game scores 4–6. Headline: **menger rank-3 (`5048f71b62fd`, surround capture) topped the pilot at 6/10** despite being only #3 by GE. Suggests the eval report's "gen-7/8 dethroning by outnumber crossovers" was a fitness-metric artifact — surround's strategic depth is harder for PPO to learn fully in 10000 episodes than outnumber's local-capture pattern.

**Lessons for the 24 production evals:**

1. **Anchor scoring against R17 explicitly.** Pilot mean 4.83 is above R17 mean 3.50; this might be calibration drift rather than a genuinely better R19. Production evaluators should re-read at least one R17 verdict (e.g., `evaluations/run17/team-1_game44f6630277b3.md`, scored 5/10) before scoring to keep the scale honest.

2. **Use `--values` aggressively.** The influence-field render is essential for threshold-race games. Briefings now suggest enabling it during play, not only at end-of-game.

3. **Carpet rank-2 custodian threshold quirk.** The rule blob says `threshold=2` but empirically a 1-stone bracket DOES flip — meaning the threshold field is a misnamed knob. Verify behaviour empirically rather than trust the briefing's literal interpretation.

4. **The greedy top-K heuristic doesn't account for capture potential.** It uses pure influence-delta. Useful for surfacing salient candidates but don't treat it as a ranking; check capture opportunities manually.

5. **Mirror = P1 win is structural across all 6 games.** Production evaluators don't need to re-derive this. Phase 2 should focus on asymmetric play (P2's actual counter-strategies) — mirror games are quick to play out, but the strategic content is in the asymmetric counter.

6. **Pie rule is the unanimous "single best change".** Production evaluators should still surface their own recommendation but be aware this is the cross-cutting verdict.

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
