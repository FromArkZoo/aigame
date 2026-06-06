# R21 Agent-Team Eval — Protocol & Index

**Goal**: Produce 35 verdicts (5 evaluator-teams × 7 games) on the R21 Option-C slate to settle the pending R21 goals — **G1** (best R21 game Overall > 5.0, beats the R19 ceiling), **G2** (slate dedup ≥ 5/6 unique kernels), **G6** (R8-revival-v2 grid game ≥ 5.0) — and to fire or stand down the **G7** pre-commitment. This is the only step that touches R21's *real* objective; every GE number to date is a PPO proxy. Output: a `SUMMARY.md` + append § Agent-team evaluation results to `evaluation_report_run21.md`.

**This is agent-team eval** (Claude-agent teams play the games and score agent-relevant strategic-depth properties), **not human eval**. The 1–10 scale is carried forward only for continuity with prior runs.

## Pre-eval gate — komi calibration (G3)

Before play, each slate game's residual post-pie mirror seat bias is calibrated via `experiments/r21_komi_calibration/calibrate_komi.py` (output: `r21_komi_calibrated.{json,md}`). The teams play the **komi-adjusted** versions of the games (served from `evaluations/run21/r21_eval_slate.db`), so a high Overall reflects real depth, not first-player advantage. Any game marked `FAIL_RUSH_BROKEN` (no komi balances it) is a G3 miss and is flagged in its briefing — it is still evaluated.

## The 7 games (Option-C slate)

| File | Substrate | Game ID | 20-seed GE | σ | Rationale |
|---|---|---|---:|---:|---|
| `briefing_menger_e1453dac5445.md` | menger | `e1453dac5445` | **0.177** | 0.101 | R21 top by mean; decay=1.0 / shorter-game structure, distinct from R20 champions |
| `briefing_menger_e52e8889517a.md` | menger | `e52e8889517a` | 0.138 | 0.090 | rank 3; parameter-sibling to game 4 — comparison pair |
| `briefing_menger_bfd1bb7ced76.md` | menger | `bfd1bb7ced76` | 0.126 | 0.070 | rank 5; the only menger game with no zero-failure rerun mode |
| `briefing_menger_1fea3357dca4.md` | menger | `1fea3357dca4` | 0.118 | 0.085 | original rank-1, deflated most under 20-seed — tests the inflation diagnosis |
| `briefing_carpet_d995cf010504.md` | carpet | `d995cf010504` | **0.103** | 0.071 | carpet top; only carpet game whose original GE *underestimated* its 20-seed mean |
| `briefing_grid_b12ff78f1c1d.md` | grid | `b12ff78f1c1d` | **0.099** | **0.050** | grid top; **most stable game in the project**; a gen-5 crossover **child** (evolution *did* compound on grid) |
| `briefing_grid_573562833174.md` | grid | `573562833174` | **0.002** | 0.002 | R8-revival v2 (custodian-1 + connection + pie) — tests **G6** directly; expected weak |

**Dedup (G2)**: 7 games, 7 distinct canonical kernels (verified via S1b equilibrium-fingerprint). **G2 PASS at proposal time.**

## Protocol

Each evaluator-team plays **all 7 games sequentially** (mirrors R19/R20 per-team structure):

1. Read the briefing (`briefing_<substrate>_<gameid>.md`) — includes calibrated komi.
2. Copy the template `TEMPLATE_team-N_gameXXXX.md`.
3. Play **at least 3 lines** (P1 push, P2 contest, novelty/adversary) using `eval_run21_helper.py`.
4. Run the 5-phase analysis: rule comprehension → strategic play → joint analysis → novelty adversary → structured verdict.
5. Save as `evaluations/run21/team-{N}_game{GAME_ID}.md`.

5 teams × 7 games = **35 verdicts**.

## Helper invocation

```
.venv/bin/python eval_run21_helper.py --game <GAME_ID> --moves "<csv>" [--values]
```

Serves the komi-adjusted slate from `evaluations/run21/r21_eval_slate.db`. `--values` renders the influence field — **enable it during play** (R19 lesson 2). The greedy top-K is influence-delta only and ignores capture potential (R19 lesson 4) — verify capture lines manually. On the pie game (`573562833174`), the pie/swap action is the last action id.

## Calibration anchors

- **R8 Connection Go (replayed 2026-05-14, modern rubric)**: **4.10** ± 1.14 — the all-time best under the *current* rubric (the 2026-02 "8/10" was ~3.9 pts of rubric drift; there is no lost peak to recover).
- **R20 production mean**: 3.73; R20 best (`5f5c72e15220` depth-record): 4.80.
- **R19 production mean**: 4.375; R19 menger top 4.8, surround top-3 **5.0**; R19 carpet top 4.4.
- **R17 mean**: 3.50; R17 best 4.14.

Re-read at least one prior verdict (e.g. `evaluations/r8_replay/team-1_game_d4015a646ae3.md` or `evaluations/run20/team-1_game5f5c72e15220.md`) before scoring to hold the scale honest. Pilot drift has historically been small (+0.13 in R20) but real — anchor down toward R17/R20, not up.

## R21-specific calibration notes

- **The 4 menger games include a parameter-sibling pair** (`e52e8889517a` ↔ `1fea3357dca4`). Score each game's *intra-family* differentiator (capture threshold, decay, generation/lineage), not "novelty of the family" repeatedly. Verify byte-identity via the rule blobs before assuming siblings are distinct (R20 wasted ~40% of its budget triple-counting a byte-identical trio).
- **`e1453dac5445` (R21 top) is structurally distinct** — decay=1.0 and a shorter game than R20's decay-0.5–0.7 champions. This is the headline "did R21 find something new?" game.
- **`b12ff78f1c1d` (grid top) is a gen-5 crossover child with verified lineage** — the one place R21 evolution actually compounded. It is also the most stable game in the project (σ 0.050). Test whether stability ↔ quality.
- **`573562833174` is the R8-revival v2 test (G6).** custodian-1 + connection + pie on flat grid-9 — the "restore connection-win" hypothesis. Its GE is ~0 (connection-win trained unreliably). Evaluate honestly whether the *game design* has depth even though PPO couldn't learn it — this is the G6 question and the substrate/representation-limit question the R8-replay teams raised (8×8-class boards too small for ladders; influence field never enters win logic).

## Output

After 35 verdicts, write `evaluations/run21/SUMMARY.md` and append § Agent-team evaluation results to `evaluation_report_run21.md` with:
- Per-game mean ± SD across 5 teams; per-team mean (calibration check).
- Cross-substrate comparison annotated for noise overlap (claim separation only if gap > max σ).
- **GE-vs-eval rank disagreement** (does the GE order survive agent judgment?).
- Comparison vs R8 replay (4.10), R19 (4.375 / 5.0 top), R20 (3.73 / 4.80).
- **Decision-rule readout** (per `analysis_post_r21.md` §7): does any game clear Overall > 5.0, or the cross-run mean rise > 1 SD over R19's 4.375? → KEEP ITERATING. Else if top < 5.0 and G6 fails → PIVOT (bigger/connection-relevant boards + influence-in-win-logic + MAP-Elites; **not** MCTS-over-the-same-GE). Two consecutive sub-5.0 campaigns → DECLARE SATURATION.

## File index

```
evaluations/run21/
├── README.md                                ← this file
├── TEMPLATE_team-N_gameXXXX.md              ← reusable verdict skeleton
├── r21_eval_slate.db                        ← komi-adjusted slate games (built post-calibration)
├── briefing_menger_e1453dac5445.md          ← per-game briefings (×7)
├── briefing_menger_e52e8889517a.md
├── briefing_menger_bfd1bb7ced76.md
├── briefing_menger_1fea3357dca4.md
├── briefing_carpet_d995cf010504.md
├── briefing_grid_b12ff78f1c1d.md            ← grid top; gen-5 child
├── briefing_grid_573562833174.md            ← R8-revival v2 (G6 test)
└── team-{N}_game{GAME_ID}.md                ← evaluator outputs (×35)
```
