# R21 Agent-Team Evaluation — Summary

**Campaign**: 5 independent evaluator teams (team-1…team-5), each played all 7 Option-C slate games (komi-calibrated) via `eval_run21_helper.py` and scored them against the Phase 1–5 rubric. 35 verdicts total (`team-{N}_game{ID}.md`). Run 2026-06-06; spawned as a tmux agent team, fully independent (no team read another's verdicts).

## Headline

**No game cleared Overall 5.0. G1 (beat the R19 ceiling) FAILS — unanimously, across all 5 teams.** The campaign mean is **3.69**, statistically tied with R20 production (3.73), **below** R19 (4.375) and below the R8 replay anchor (4.10). R21 did not move the agent-judged ceiling; if anything it sits a touch lower than R20.

## Score matrix (Overall, 1–10)

| Game (GE) | t1 | t2 | t3 | t4 | t5 | **mean** | **SD** |
|---|--|--|--|--|--|--|--|
| menger `e1453` (GE-top, 0.177) | 4.0 | 3.5 | 3.9 | 3.4 | 3.5 | **3.66** | 0.27 |
| menger `e52e` (0.138) | 4.0 | 3.5 | 4.0 | 3.3 | 3.6 | **3.68** | 0.31 |
| menger `bfd1` (0.126) | 3.9 | 3.5 | 4.1 | 3.4 | 3.5 | **3.68** | 0.30 |
| menger `1fea` (0.118) | 3.7 | 3.3 | 3.9 | 3.2 | 3.4 | **3.50** | 0.29 |
| carpet `d995` (0.103) | 4.2 | 3.7 | 4.0 | 3.4 | 3.6 | **3.78** | 0.32 |
| grid `b12` (0.099) | 3.8 | 3.4 | 4.2 | 3.7 | 3.5 | **3.72** | 0.31 |
| grid `573` (connection, 0.002) | 3.3 | 3.8 | 3.8 | 4.3 | 3.7 | **3.78** | 0.36 |
| **team mean (calibration)** | 3.84 | 3.53 | 3.99 | 3.53 | 3.54 | **3.69** | — |

Top game by mean: a tie at **3.78** between carpet `d995` and the connection game `573`. Highest single score anywhere: **4.3**. Team means span 3.53–3.99 — tight calibration, honestly anchored between R17 (3.50) and R20 (3.73).

## GE vs agent-eval: the ranking is inverted at the extremes

GE order (high→low): `e1453` > `e52e` > `bfd1` > `1fea` > `d995` > `b12` > `573`.
Eval-mean order (high→low): `d995` ≈ `573` > `b12` > `e52e` ≈ `bfd1` > `e1453` > `1fea`.

**The GE-#1 game (`e1453`, 0.177) is second-from-bottom by agents; the GE-last game (`573`, 0.002) is tied for first.** This is the cleanest, most direct confirmation yet that **GE does not track agent-judged depth** — and it now has a *mechanistic* explanation from the play (below), not just a rank correlation.

## Goals readout

| Goal | Result |
|---|---|
| **G1** — best game Overall > 5.0 | **❌ FAIL** (top game-mean 3.78; top single score 4.3) |
| **G2** — slate ≥ 5/6 unique kernels | ⚠️ **nominal PASS / functional FAIL** — S1b says 7 distinct kernels, but in play the 4 menger games are near-identical (`e52e`≈`bfd1`≈`1fea` differ only by komi and an *inert* max_turns cap; `e1453` differs only by decay=1.0). The menger pod is effectively 1–2 games. |
| **G3** — mirror seat bias < 0.10 post-komi | ⚠️ **mixed** — 6/7 balanced via komi; `573` rush-broken (0.50, komi can't fix). Several still felt P1-favored in play. |
| **G6** — R8-revival connection ≥ 5.0 | **❌ FAIL** (3.78) — but the *design* is promising; see below. |
| **G7** — pre-commitment | **FIRES** (G1 + G6 fail). See decision. |

## Why the games are shallow (mechanistic findings, convergent across teams)

- **The menger/carpet pod is a non-interactive packing race.** outnumber-2 capture is *anti-synergistic*: capturing leaves stale negative influence and zeroes your own accumulator, so engaging is mutually destructive → play collapses to both players packing the densest fractal region in their own corner, no contact. Decay=1.0 on the GE-top game (`e1453`) flattens the influence gradient further → an even purer, shallower sprint. The 3D substrate is barely used (play stays on 2D faces).
- **The only live capture lever is custodian flip on the grid games** (`b12`, `573`) — an Othello-in-a-race double-swing. That's why `b12` is the menger/grid family's most tactical game and why the connection game's design has teeth.
- **The connection game `573` has the most interactive design in the slate** — custodian capture actually *fires* and *cuts* connection paths (unlike R8 Connection Go's surround, which never fired in equilibrium), and a cut simultaneously breaks the opponent's path and advances the cutter's perpendicular goal. 3 of 5 teams rated it top-tier *on design*. **team-1 dissented (3.3)**: custodian lets the attacker *reclaim* a cut (one stone flips a whole run back), which can erase the defender's counter — strictly worse than surround on that axis. Either way it can't score ≥5.0 because it is rush-broken (0.50 seat bias, pie/komi can't fix), its influence layer is dead, the 9×9 board is too small for ladders, and it is PPO-unlearnable (sparse connection reward → GE≈0).

## Engine finding (verified in code, not just play)

3 teams independently flagged it: **komi is multiplicative** — `engine_v2.py:998` applies `komi_p2 × threshold` for threshold-race (e.g. komi_p2=0.05, threshold=30 → +1.5 to P2), and `:927` applies `komi_p2 × num_active_cells` for count-based wins. The original `eval_run21_helper.py` displayed the flat fraction (0.05). **This was a display bug only — the engine (and thus every game's win determination, which teams read off `Done/Winner`) used the correct multiplicative komi, so the verdicts stand. The helper display is now fixed.**

## Decision (pre-committed rule, `analysis_post_r21.md` §7)

- KEEP ITERATING — requires ≥1 game > 5.0 *or* cross-run mean > 1 SD above R19's 4.375. **Neither holds** (3.69 < 4.375; no game > 5.0).
- **PIVOT — fires: top game < 5.0 AND G6 fails.** ✅
- **DECLARE SATURATION — also fires:** R20 (top 4.80) and R21 (top 3.78) are **two consecutive campaigns with no game > 5.0 and no > 1-SD rise.** ✅

**Verdict: the rule-grammar + GE-evolution regime is empirically saturated.** Twenty-one runs of evolving rule-blobs scored by PPO-GE have not produced a game an agent rates ≥ 5.0, and GE now demonstrably anti-correlates with agent depth at the top of the slate. Another GE-tuning run (the R22-as-planned scope) is not warranted.

**Constructive pivot (what the evidence points to), NOT another GE run and NOT MCTS-over-the-same-GE:**
1. **Bigger / connection-relevant boards** — 9×9-class is too small for ladders/medium-term planning (R8-replay + this campaign agree). Try a larger axis and/or hex (degree-6) geometry with diagonal bridges.
2. **Connection win + a capture that creates *permanent* cuts** — connection is the most interactive win condition in the corpus, but pair it with **surround** (permanent) rather than **custodian** (reclaimable) capture (team-1's finding).
3. **Make the influence field enter win logic** — today it is decorative observation-tensor padding; it never determines a winner.
4. **Quality-Diversity selection (MAP-Elites / novelty search)** instead of single-objective GE-greedy + hash-dedup, which is the textbook recipe for the local-optimum collapse this corpus shows (evolution barely compounds; dedup kills children).
5. **Replace/augment GE** with a depth proxy that agents validate — GE's anti-correlation here means it can no longer be the selection signal.

## Files
- 35 verdicts: `evaluations/run21/team-{1..5}_game{ID}.md`
- Briefings: `evaluations/run21/briefing_*.md`; protocol: `README.md`; rubric: `TEMPLATE_team-N_gameXXXX.md`
- Komi gate: `experiments/r21_komi_calibration/r21_komi_calibrated.md`
- Analysis + decision rule: `analysis_post_r21.md`
