# FRONTLINE Stage-1 calibration

Pre-registered gates: experiments/frontline/PREREGISTRATION.md (Stage 1 — the locked authority). Gate ORDER is structural: skill -> bias -> end-cause -> engaged; a cell that fails gate N never computes gate N+1. Rerunning a --cells subset replaces only those cells (sources persist in calibration.json; this file is regenerated whole each run).

**bias** = |p1_share + draw_rate/2 - 0.5| — draws count half to each side, so a draw-heavy meta cannot masquerade as balance (p1_share = seat-0 win share over seat-swapped halves; all statistics over EVERY eval game — no filtering, the R21 survivorship lesson). Cell bias = mean over seeds of per-seed |draw-adjusted bias| — conservative when seed signs differ (opposite-signed per-seed seat advantages do not cancel).

**Komi semantics**: komi is applied at EVAL time by setting trainer.game.win_condition.komi_cells before the eval games (engines are created per game via create_engine(trainer.game)); komi only enters score comparisons, never placement legality, so the komi-0-trained policies are reused unchanged — the same policy-reuse rationale as siege's S komi sweep. After each cell's ladder the mutation is reset to the winning rung (or 0), and the winning komi is baked into games/calibrated/f_frontline.json at write time (asserting |komi| < end_margin — the registered harness invariant). Ladder direction: P1-favored at komi 0 -> POSITIVE komi (komi_cells is added to P2's score in every engine comparison).

## Cell E0p75_M8 — **FAIL**

E=0.75, M_end=8; budget 3000, eval n=200, seeds [42, 43, 44] (1159s). Reason: skill: mean 0.527 (floor 0.75), min 0.510 (floor 0.65)

Gate 1 (skill — tvr mean >= 0.75, min >= 0.65, collapse < 0.20 -> replace-in-slot):

| orig seed | final seed | tvr | rerun |
|---|---|---:|---|
| 42 | 42 | 0.530 | no |
| 43 | 43 | 0.540 | no |
| 44 | 44 | 0.510 | no |

tvr mean 0.527, min 0.510.

Gate 2 (bias): NOT COMPUTED — gate 1 failed (prereg structural order).

## Cell E0p75_M12 — **FAIL**

E=0.75, M_end=12; budget 3000, eval n=200, seeds [42, 43, 44] (1598s). Reason: skill: mean 0.577 (floor 0.75), min 0.550 (floor 0.65)

Gate 1 (skill — tvr mean >= 0.75, min >= 0.65, collapse < 0.20 -> replace-in-slot):

| orig seed | final seed | tvr | rerun |
|---|---|---:|---|
| 42 | 42 | 0.550 | no |
| 43 | 43 | 0.590 | no |
| 44 | 44 | 0.590 | no |

tvr mean 0.577, min 0.550.

Gate 2 (bias): NOT COMPUTED — gate 1 failed (prereg structural order).

## Cell E1p00_M8 — **FAIL**

E=1.00, M_end=8; budget 3000, eval n=200, seeds [42, 43, 44] (1181s). Reason: skill: mean 0.560 (floor 0.75), min 0.550 (floor 0.65)

Gate 1 (skill — tvr mean >= 0.75, min >= 0.65, collapse < 0.20 -> replace-in-slot):

| orig seed | final seed | tvr | rerun |
|---|---|---:|---|
| 42 | 42 | 0.550 | no |
| 43 | 43 | 0.550 | no |
| 44 | 44 | 0.580 | no |

tvr mean 0.560, min 0.550.

Gate 2 (bias): NOT COMPUTED — gate 1 failed (prereg structural order).

## Cell E1p00_M12 — **FAIL**

E=1.00, M_end=12; budget 3000, eval n=200, seeds [42, 43, 44] (1078s). Reason: skill: mean 0.587 (floor 0.75), min 0.550 (floor 0.65)

Gate 1 (skill — tvr mean >= 0.75, min >= 0.65, collapse < 0.20 -> replace-in-slot):

| orig seed | final seed | tvr | rerun |
|---|---|---:|---|
| 42 | 42 | 0.570 | no |
| 43 | 43 | 0.640 | no |
| 44 | 44 | 0.550 | no |

tvr mean 0.587, min 0.550.

Gate 2 (bias): NOT COMPUTED — gate 1 failed (prereg structural order).

## Cell E1p25_M8 — **FAIL**

E=1.25, M_end=8; budget 3000, eval n=200, seeds [42, 43, 44] (1354s). Reason: skill: mean 0.500 (floor 0.75), min 0.430 (floor 0.65)

Gate 1 (skill — tvr mean >= 0.75, min >= 0.65, collapse < 0.20 -> replace-in-slot):

| orig seed | final seed | tvr | rerun |
|---|---|---:|---|
| 42 | 42 | 0.570 | no |
| 43 | 43 | 0.430 | no |
| 44 | 44 | 0.500 | no |

tvr mean 0.500, min 0.430.

Gate 2 (bias): NOT COMPUTED — gate 1 failed (prereg structural order).

## Cell E1p25_M12 — **FAIL**

E=1.25, M_end=12; budget 3000, eval n=200, seeds [42, 43, 44] (1283s). Reason: skill: mean 0.557 (floor 0.75), min 0.510 (floor 0.65)

Gate 1 (skill — tvr mean >= 0.75, min >= 0.65, collapse < 0.20 -> replace-in-slot):

| orig seed | final seed | tvr | rerun |
|---|---|---:|---|
| 42 | 42 | 0.600 | no |
| 43 | 43 | 0.560 | no |
| 44 | 44 | 0.510 | no |

tvr mean 0.557, min 0.510.

Gate 2 (bias): NOT COMPUTED — gate 1 failed (prereg structural order).

## Grid decision (prereg tie-break: length centrality closest to 95 -> max score_margin share -> min |bias|)

Ranked passing cells: NONE

**F_GRID_UNRESOLVED — no passing cell; campaign NO-GO at Stage 1 (subject to the prereg KILL_INVALID inspection branch). games/calibrated/f_frontline.json NOT written.**

## Comparators (S/A1 re-assert stub — provenance check only; full re-assert at screen time)

- `s_flip_r2.json`: present (game_id s_flip_r2, komi_p2 0.00, pie True). SIEGE Stage-1 arm s: komi 0.00 PASS (p1_wr 0.550, bias 0.050, draws 0.000) — experiments/siege/calibration.md
- `a1_field_connect.json`: present (game_id fc_probe_a1_field_connect, komi_p2 0.00, pie True). FC probe calibration: komi 0.00 PASS (p1_wr 0.450, bias 0.050, draws 0.000) — experiments/field_connect_probe/calibration.md (passed through fc_phase15 unchanged)
