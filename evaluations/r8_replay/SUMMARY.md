# R8 Replay — Summary

**Date.** 2026-05-14.
**Game.** `d4015a646ae3` — "Connection Go", R8 top-1 by ELO (2304.6). The project's nominal quality anchor (8/10 in February 2026 agent eval).
**Campaign.** 5 production teams, parallel independent agents. Each team: read briefing only, played ≥3 distinct strategy games via `eval_run20_helper.py --db genesis_v2_run8.db`, scored on the R20 Phase 1–5 rubric.
**Files.** `team-{1..5}_game_d4015a646ae3.md` + `briefing_r8_d4015a646ae3.md` in this directory.

## Scores

| Team | Depth | Complexity | Balance | Novelty | Replayability | **Overall** |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5 | 5 | 4 | 4 | 5 | **5.0** |
| 2 | 4 | 4 | 3 | 3 | 4 | **4.0** |
| 3 | 3 | 3 | 2 | 3 | 3 | **3.0** |
| 4 | 6 | 6 | 5 | 5 | 5 | **5.5** |
| 5 | 3 | 2 | 2 | 2 | 2 | **3.0** |
| **mean** | 4.20 | 4.00 | 3.20 | 3.40 | 3.80 | **4.10** |
| **σ** | 1.30 | 1.58 | 1.30 | 1.14 | 1.30 | **1.14** |
| **range** | 3 | 4 | 3 | 3 | 3 | **2.5** |

## Headline

**Mean 4.10 ± 1.14, range 2.5.** The February 2026 rating of 8/10 does not survive replay under the R20 protocol. Drift = **−3.9 points**.

The range (2.5) is **well within branch-(1)'s ≤3 stability bound and far below branch-(3)'s wild-spread threshold of >4**. Agent-eval as an instrument is stable; the 5 teams converged tightly given how different their playthroughs were.

## Branch classification

Per the briefing's pre-registered decision criteria:

| Outcome | Criterion | Hit? |
|---|---|---|
| (1) Anchor stable — proceed to fitness redesign | mean ≥ 7.0, range ≤ 3 | NO (mean 4.10) |
| (2) February rating inflated — resume R21 with `w_planning=0` | mean 4–5/10 | **YES** (mean 4.10) |
| (3) Agent-eval unstable — validator crisis | range > 4 | NO (range 2.5) |

**Branch (2). Resume R21 with `w_planning=0`.**

## What this means for the project

### The GE-bottleneck diagnosis collapses

The R21 pause on 2026-05-13 rested on a single observation: R8 champion ranks 6 of 12 by GE on the R20+R8 calibration slate, with R20 menger games outranking it. That observation **assumed the R8 champion was an 8/10 game** — i.e., that the comparison was meaningful in the first place.

Under the current rubric, the R8 champion is a **4.10/10 game**. R20 production mean is 3.73. R20 top is 4.80. **R8 sits in the middle of the R20 corpus, not above it.**

The "5-rank GE miss" was not a metric failure. It was the metric correctly ranking a 4.10/10 game in the middle of a slate of 3.7–4.8/10 games. GE may still under-reward depth in specific ways (the existing `feedback_ge_under_rewards_depth.md` finding holds for R19 surround variants), but **the project does not have a load-bearing anchor that GE is missing**. The optimizer is not optimizing a phantom.

### What the teams actually saw

Independent observations that converged across multiple teams:

1. **Connection Go is Hex on a too-small square grid with decorative Go captures.** The asymmetric face-connection objective is the only genuinely good mechanic. The 8×8 axis caps games at ~15–20 plies — too short for ladders, no room for medium-term planning.

2. **No pie rule → uncompensated first-mover advantage.** R8 predates the pie rule; modern rubric penalises this heavily. Teams 3 and 5 specifically score balance at 2/10 on this basis.

3. **4-connected grid has no diagonal bridges.** Unlike hex Hex (degree 6), a square-grid connection chain is fragile against a single P2 cut. Teams 1 and 2 found a dominant P2 "cut+build" counter — row stones simultaneously block P1's column and build P2's row.

4. **Surround captures effectively never fire in equilibrium play.** Across ~15 games of natural play (3 per team), captures fired only on contrived adversarial probes. Connection chains have abundant liberties.

5. **The influence field is observation-tensor decoration** — it never enters connection-win logic.

These are the same kinds of structural-flaw observations that R17–R20 teams made about subsequent champions. **R8 is not categorically better than R20 by team analysis. It just had less competition in February and was rated more generously.**

### Bugs surfaced (multi-team independent confirmation)

All 5 teams independently flagged:

1. **Briefing-error.** The briefing described `surround threshold=3` as outnumber-3 semantics ("≥3 placer's stones adjacent"). The engine at `engine_v2.py:606-620` `_capture_surround` actually implements **Go-style liberty-zero group capture**; the `threshold=3` field is vestigial. Teams 1, 2, 3, 4, 5 all verified empirically and corrected.

2. **Helper-error.** `eval_run20_helper.py:header()` prints `Win: threshold-race > 0.500` unconditionally — wrong for connection-win games. Should dispatch on `win_condition.condition_type`.

3. **`win_condition.threshold=0.5`** is vestigial under connection-win — `_check_connection` ignores it.

These don't change the calibration verdict but should be fixed before any future R8-era replays.

## Recommended next steps

In priority order:

**1. Resume R21 with `w_planning=0`.** All R21 blockers shipped + pushed (`673383f` on origin/main). The S2 A/B re-score showed planning_horizon doesn't help at any weight. Drop it; launch evolution as paused.

**2. Don't redesign GE on this basis.** The bottleneck framing was wrong. The `feedback_ge_under_rewards_depth.md` finding for surround-capture variants is narrower than a project-wide fitness redesign; keep that observation, but don't escalate it into a generalized "GE is broken" conclusion.

**3. Fix the documentation bugs.** Helper header dispatch on win-condition type. Update R8 briefing for any future replays.

**4. Audit other historical "anchors" similarly.** The fact that R8 dropped 3.9 points under modern rubric suggests R17/R19 anchors may have similar drift. If R19 menger top (4.80) is replayed and drops to ~3.5, the entire run-vs-run comparison structure needs recalibration. Out of scope for this session but flagged for the next opportunity.

**5. Don't lose the campaign mechanism.** Five agents independently played the same game, converged on the same structural critiques, and produced a tight ±1.14 distribution. **This worked.** The agent-eval validator is functioning as a research instrument — that's the most important durable finding here. The G7 MCTS pre-commit can be retired with this evidence.

## Note on the original R8 evaluation report

The R8 report (2026-02) said, verbatim: *"Go Essence scores improved 17× over Run 7, but the evaluation reveals that high Go Essence scores don't always correlate with good gameplay. The #1 game by ELO (`d4015a646ae3`) is genuinely excellent."*

The 2026-02 team rated this 8/10 in good faith. The drift to 4.10 isn't a failure of that team; it's a measurement-instrument result. **Three months of Claude versions and rubric refinement = roughly 4 points of anchor drift** is the most useful single number this campaign produced. Any future cross-run comparisons should bake in a ±0.5/month drift assumption until a stable rubric is locked.

---

**Decision logged.** Branch (2). Resume R21. Update project memory.
