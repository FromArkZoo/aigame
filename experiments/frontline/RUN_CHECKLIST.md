# FRONTLINE campaign — execution runbook (prereg `3a378dd`; spec §6–§8)

Run stages strictly in order. **STOP at any registered KILL — kills are outcomes, not bugs.**
Before classifying any Stage-0/1 kill, apply the prereg **KILL_INVALID inspection branch**:
a kill attributable on inspection to implementation error (not design arithmetic) → fix and
rerun that stage ONCE; only a clean kill, or the rerun's kill, maps to RETIRED.

Interpreter: ALWAYS `.venv/bin/python` (bare `python`/`python3` lack pytest/torch).
Contract: `experiments/frontline/PREREGISTRATION.md` (locked `3a378dd`, before any engine code).
Plan: `docs/superpowers/plans/2026-06-11-frontline-build.md`.

## Stage 0 — pre-training kills (DONE at build time)

- [x] **0a kernel memo** — `.venv/bin/python experiments/frontline/stage0_memo.py` → `STAGE0_MEMO.md`.
      **KILL-0a1: mean front margin swing = +1.14 → PASS** (conservative all-rows mean; front-only
      chain rows 1.33; bar: < −2 kills). **KILL-0a2: analytic engaged@20% fill, E=1.0 = 0.107 → PASS**
      (bar: > 0.60 kills). Committed (`baa8a9d`, `ee7d531`).
- [x] **0b pinned smoke** — `.venv/bin/python experiments/frontline/build_games.py`
      (pinned: E=1.00, M_end=8, komi_cells=0, seed 7; 1000 random + 200/scripted matchup).
      **KILL-0b1: flips/game 29.242 ≥ 1.0 → PASS** · **KILL-0b2: mutual-packer total score 0.000 ≤ 2.0
      → PASS** · **KILL-0b3: random engaged@min(80, end) = 0.024 ∈ (0.01, 0.60) → PASS**.
      Committed (`6c285f8`).
- [x] **⚠ MIRROR_CONTINGENCY FIRED at 100%** — mirror secured ≥ draw in **100%** of games vs
      front-builder (threshold ≥ 30%). NOT a kill; build continued. **OWNER DECISION RESOLVED
      2026-06-12: STAY AT W=22** (owner-directed; the one licensed W=21 switch is hereby
      forfeited — no W edits, no Stage-0 rerun). Mirror-resistance now rests on the Stage-2
      exploiter band (beats mirror ≥ 0.70 per seat), as registered.
      Original alternative (NOT taken): switch to **W=21 + Stage-0a
      rerun** (S/A1 stay W=22 — comparability cost recorded, prereg Stage 0).
      **If W=21 is chosen, FIRST fix the W constant in all FOUR locations**:
      `experiments/frontline/scripted_agents.py` (W=22, line ~19),
      `experiments/siege/scripted_agents.py` (W=22, line ~14 — frontline imports `ChainBuilder`
      from it), `experiments/frontline/build_games.py` (W=22, line ~63), and
      `experiments/frontline/stage0_memo.py` (W=22, line ~34 — LOAD-BEARING: the memo's pinned
      margin-swing coordinates are W-indexed (`cell = r*W + q`), so a stale constant would
      silently re-validate W=22 geometry on the rerun). Then rerun 0a → 0b.

## Stage 1 — calibration (F grid 6 cells + comparator re-assert)

**RUN 2026-06-12 (7,653 s): F_GRID_UNRESOLVED — all 6 cells FAIL gate 1 (skill), tvr means
0.500–0.587 vs floor 0.75, minima 0.430–0.550 vs 0.65; no collapsed seed, reserves unconsumed,
komi ladder never reached. KILL_INVALID inspection (kill_inspection.py/.log): CLEAN KILL —
harness/reward/obs/anchor all verified sound; PPO learning curve degrades below random
(0.08 @ ep 2250), deterministic policy collapses to passive timeout-losing play (tvr 0.28,
83% timeout). Campaign NO-GO; contested_majority RETIRED. See RESULTS.md. Stages 1.5/2/3
NOT RUN (registered: no screen/blind spend after a Stage-1 kill).**

```
.venv/bin/python experiments/frontline/calibrate.py --arm all --budget 3000 --eval-episodes 200 --seeds 42,43,44
```

- **Wall clock (honest):** registered estimate ~1.5 h; build-time toy runs suggest **2.5–3.5 h** —
  frontline games run ~2.3× longer than s_flip. Schedule accordingly (estimate drift recorded
  here; the locked prereg is unchanged).
- Outputs: `calibration.md` + `calibration.json` + `games/calibrated/f_frontline.json` (winner
  cell). **Record the RUNNER-UP cell from the decision block** — it is the only licensed Stage-3
  PARTIAL knob (no runner-up ⇒ PARTIAL is VOID ⇒ NO-GO).
- Gate ORDER per cell (structural): (1) skill — tvr mean ≥ 0.75 AND no seed < 0.65; collapsed
  seed (tvr < 0.20) → ONE fresh-seed rerun (reserves 45 then 46, replace-in-slot); third collapse
  → cell INVALID; (2) seat bias ≤ 0.10 with pie ON at komi_cells 0; fallback ladder
  komi_cells {±1, ±2}, sign-directed, one pass; (3) end-cause health — timeout ≤ 0.25,
  draw ≤ 0.05, score_margin share ≥ 0.25; double-pass > 0.50 = yellow flag (diagnostic);
  (4) engaged_share final-ply mean ∈ [0.02, 0.60].
  Tie-break: length centrality closest to 95 → max score_margin share → min |bias|.
- **F_GRID_UNRESOLVED** (no passing cell incl. komi ladder) → family dead → **campaign NO-GO**,
  no screen/blind spend — subject to the KILL_INVALID inspection branch above.
- Comparators: s_flip_r2 / a1 re-assert their SIEGE/fc_phase15 artifacts (komi 0 PASS on disk);
  recalibration only if retraining drifts bias > 0.10; comparator failure →
  **CAMPAIGN_UNRESOLVED** → one retrain — never a family verdict.

## Stage 1.5 — drama (DIAGNOSTIC ONLY — never a comparative or bar)

```
.venv/bin/python experiments/frontline/stage15_drama.py --budget 3000 --n 200
```

(~10 min; defaults: seed 42, game `games/calibrated/f_frontline.json`.) Logs score-share-trace
drama on the winning cell's seed-42 policy pair; yellow flag: < 30% of games with per-game
drama > 0.01. Reported alongside the anchored S/A1 values in the writeup. **No licensing role** —
Stage-2 GO is 2/2 comparatives regardless of this number (drama demoted by registration).

## Stage 2 — mechanical screen

```
.venv/bin/python experiments/frontline/run_screen.py --budget 5000 --eval-episodes 200
```

(seeds default 42,43,44; registered ~2 h — expect longer per the Stage-1 wall-clock note.)

- Comparatives (DIRECTIONAL, F vs S — GO requires **2/2**): control_flip_rate F − S ≥ +0.5;
  game-length centrality (band [30,160], center 95) F ≥ 10 turns more central than S.
- Bands on F only: flip events/game ∈ [1,20] AND distinct-stones ≥ 0.5×events; engaged_share
  ∈ [0.02,0.60]; timeout ≤ 0.25; draw ≤ 0.05; score_margin ≥ 0.25 re-asserted at 5000; tvr gates
  as Stage 1 with mandatory per-seed inspection; bias ≤ 0.10; packing-scores-zero ≤ 2 cells/game;
  exploiter bands — beats pass-bot ≥ 0.90 and mirror ≥ 0.70 per seat. No game- or seed-level
  filtering of any statistic (R21 Probe B survivorship lesson).
- Instrumentation-reproduction (A0's registered job): a1 − a0 control_flip_rate ≥ +3.0
  (on-disk 10.6 vs 5.3); failure → instrumentation INVALID → CAMPAIGN_UNRESOLVED, never a
  family verdict.
- Verdicts (exit codes 0/1/2): **SCREEN_GO** → proceed to blind; **SCREEN_NOGO** → campaign
  NO-GO, no blind spend; **CAMPAIGN_UNRESOLVED** → comparator-failure rule: ONE retrain of the
  failing comparator (S or A1 health: collapsed seed, bias > 0.10, tvr floor), then re-run the
  screen. A crashed arm hard-fails the screen — re-run it (crash ≠ registered failure path).

## Stage 3 — blind agent-team campaign (~1 h)

1. Build the pack — AFTER SCREEN_GO, at campaign time:

   ```
   .venv/bin/python experiments/frontline/build_blind_pack.py --seed <runner-chosen>
   ```

   `--seed` is REQUIRED with no default — pick it now, at campaign time (the sealed label↔game
   mapping is a pure function of the seed; a default in the script would let anyone reconstruct
   it). Pack: labels **G/J/P**, anonymized `g/j/p.json` (game_id rewritten to label; canonical
   files untouched), `.blind_mapping.json` **SEALED**.
   **At pack-build time, exercise the plan's licensed rename: build into
   `evaluations/stage3_ab2/` (pack name must not evoke the treatment mechanic).** Mechanical via
   `--out-dir evaluations/stage3_ab2` — every pack-internal path reference follows the directory
   name (default `evaluations/frontline_ab` is for dry-run plumbing checks only).
2. **2 INDEPENDENT agent teams** — REAL tmux teammates (user's standing agent-team setup), no
   cross-reads. **OPPOSITE evaluation orders:** team 1 G→J→P; team 2 P→J→G. Seat-swapped
   matches, role-averaged verdicts; fairness-perception probe mandatory per game (in BRIEFING).
   **Evaluator team briefs must NOT load aigame project memory (it names the arms); spawn
   evaluators with clean context — SIEGE precedent.**
3. Verdict instrument: the pack `BRIEFING.md` (= the stage3_ab template adapted ONLY by label
   substitution; Overall 1–10, same anchors).
4. **Unblind ONLY after all 6 verdicts are filed.** Log the three label means first, then open
   `.blind_mapping.json`. **A1 validity band [3.7, 4.4]**; outside → CAMPAIGN_UNRESOLVED → one
   cheap blind replicate (its numbers adjudicate alone); a second consecutive validity failure →
   CAMPAIGN_INVALID. S sanity flag [3.7, 4.5] → verdicts provisional → one replicate.
5. Decision grammar: apply `PREREGISTRATION.md` **Stage 3 VERBATIM** (GO / PARTIAL / NO-GO live
   there; PARTIAL's only knob = the recorded Stage-1 runner-up cell, second blind adjudicated
   GO-else-NO-GO, no further knobs).

## After the campaign

- Write `experiments/frontline/RESULTS.md` (decision first, stages, honest synthesis,
  pre-registration audit — fc_phase15/siege format).
- Commit results; merge `frontline-rebuild` per finishing-a-development-branch.

---

Pre-registration locked at commit `3a378dd` (before any engine code or training run) and
**not altered after data**. This runbook transcribes it for execution convenience; on any
discrepancy the prereg text wins.
