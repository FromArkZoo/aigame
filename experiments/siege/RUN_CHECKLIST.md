# SIEGE campaign — execution checklist

Run stages strictly in order. STOP at any registered kill — kills are outcomes, not bugs.
Interpreter: ALWAYS `.venv/bin/python` (bare `python`/`python3` lack pytest/torch).
Contract: `PREREGISTRATION.md` (locked `0e51297`, before any training). Plan: `docs/superpowers/plans/2026-06-10-siege-campaign.md`.

## Stage 0 — pre-training kills (DONE at build time)
- [x] 0a flip-threshold memo: `STAGE0_MEMO.md` — lone 3 / chain-end 4 / interior 5 / dense 8, engine cross-check PASS → **kill check PASS** (lone ≤ 4).
- [x] 0b smoke (build_games.py run, seed 7): m_siege random 5.20 flips/g (quota ticks 2.50/g), scripted 21.0; s_flip_r2 random 3.59, scripted 70.5 → **both kill gates PASS** (≥ 1 flip/game).

## Stage 1 — calibration (~4–5 h)
```
.venv/bin/python experiments/siege/calibrate.py --arm all --budget 3000 --eval-episodes 200 --seeds 42,43,44
```
- Outputs: `calibration.md` + `games/calibrated/{m_siege,s_flip_r2}.json`.
- Gate order is structural: per-role skill gates (tvr ≥ 0.80 AND +0.15 over baseline; collapse < 0.20 → ONE reserve rerun 45→46) BEFORE role-matrix bias (≤ 0.10) BEFORE quota-share (≥ 0.20) / timeout-share (≤ 0.25).
- `M_GRID_UNRESOLVED` → m_siege dead; campaign CONTINUES S-only. Role-pie is a registered retry that comes back through a plan update — do NOT improvise it.
- `--grid-cells` runs never write calibrated files without `--allow-partial` (prereg winner selection is full-grid only).
- A crash mid-run: fix the cause and re-run the arm (calibration.md sections regenerate per arm; corrupt calibration.json fails loudly with instructions).

## Stage 1.5 — drama anchor-calibration (minutes)
```
.venv/bin/python experiments/siege/anchor_drama.py --n 200 --games a0,a1,e1453,573 --seed 11
```
- BAR: drama(a1) > drama(a0) AND e1453 not top (tie-for-top = FAIL, conservative).
- `DRAMA_ANCHORED` → screen runs `--anchor-result pass` (GO = 2/3 comparatives).
- `DRAMA_DEMOTED` → screen runs `--anchor-result demoted` (drama excluded; GO = 2/2).

## Stage 2 — mechanical screen (~2.5 h)
```
.venv/bin/python experiments/siege/run_screen.py --budget 5000 --eval-episodes 200 --seeds 42,43,44 --anchor-result <pass|demoted>
```
- Outputs: `screen_results.csv` + `screen_results.md` with the verdict and stop-rule branch.
- Verdicts: **GO-to-blind** (M+S+A1) / **S-ONLY BLIND** (m fails, s clears z_flip_r2 template ≥ 3/4 vs a0) / **SCREEN NO-GO** (both fail → no blind, exit 1).
- A crashed arm hard-fails the screen — deliberate: an infrastructure crash must stay distinguishable from the registered M-invalidated path. Re-run the screen.

## Stage 3 — blind agent-team campaign (~1 h)
- Pack: `evaluations/stage3_ab/` (sealed D/V/X mapping; BRIEFING has the role-swap protocol + fairness probe; orchestrator section below the STOP divider).
- Teams are REAL tmux teammates (agent teams), NOT background subagents — user's standing setup.
- 2 independent teams × assigned games; role-swapped matches, role-averaged verdicts; unblind ONLY after all verdicts filed.
- Apply the Stage-3 decision grammar from PREREGISTRATION.md verbatim (A1 validity band [3.9,4.4] → CAMPAIGN_UNRESOLVED + one cheap replicate; GO: M−A1 ≥ +1.0 AND M>S by ≥ 0.3; PARTIAL → only the ε=0.25@r2 knob; M≤S retires asymmetric objectives; S≤A1 closes the FC family).
- Write `experiments/siege/RESULTS.md` in the fc_phase15 format (decision first, stages, honest synthesis, pre-registration audit). Stage-0b smoke used seed 7 (recorded here since PREREGISTRATION was already locked when the seed was chosen).

## After the campaign
- Commit results; merge `siege-campaign` per finishing-a-development-branch.
- REGISTERED FOLLOW-ON (fires on ANY outcome): RC2 selection-layer workstream — observer influence field build first (generator_v2.py:213-224 zeroes descriptors off-threshold), then the QD anchor probe. GE stays diagnostic-only.

## Known notes (build-time decisions)
- clock_frac ≡ existing step_frac observation — not duplicated; only quota_frac added (+1 state_dim, capture-quota games only; legacy obs bit-identical, verified vs main).
- Screen centrality bar requires m's mean length in [30,160] AND gain ≥ 10 (in-band requirement is an interpretive extension matching fc_phase15 precedent; documented in run_screen.py's docstring).
- Pre-existing on main, NOT ours: `test_parallel_finalize::test_finalize_champions_default_reruns_is_20` failure + `test_ca_integration` collection error.
- Deferred cosmetics: a comment on `state_dim`'s `extra` accumulation pattern; a comment on the `_quota_ticks` injection in the obs test.
