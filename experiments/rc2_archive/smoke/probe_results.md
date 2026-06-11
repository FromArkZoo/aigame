# RC2 Phase C archive probe — results (SMOKE RUN — disjoint seed streams, NOT a verdict)

Protocol per experiments/rc2_archive/PREREGISTRATION.md (locked): base_seed 13, Stage-0 n=10, Stage-1 n=10, B=10/arm, re-eval at (5, 10).

## CAL

- drama(573562833174) = 0.2764
- drama(e1453dac5445) = 0.0488
- gap = 0.2276 (floor 0.15) -> PASS

## Stage 0 — BAR W (within-family separation)

Attempts 28, evaluated 24, valid 14.

| family | n_valid | p10 | p90 | p90-p10 | LIVE (floor 0.064) |
|---|---:|---:|---:|---:|---|
| territory | UNSAMPLED (1) | | | | |
| elimination | UNSAMPLED (0) | | | | |
| connection | 6 | 0.0562 | 0.1639 | 0.1077 | YES |
| threshold | 7 | 0.0132 | 0.1030 | 0.0899 | YES |

BAR W: 2 LIVE of 2 sampled -> PASS

## Stage 1 — BAR H (matched-budget search value)

| arm | evals | coverage | QD-score | top-10 mean drama [95% CI] | skips |
|---|---:|---:|---:|---|---:|
| R | 10 | 13 | 1.353 | 0.1230 [0.1044, 0.1420] | 0 |
| M | 10 | 11 | 1.283 | 0.1247 [0.1066, 0.1440] | 0 |

BAR H: top10(M) - top10(R) = 0.0017 (floor 0.03) -> FAIL

Jointly filled cells: 10; arm M wins 0, same-elite ties 9, losses 1.

Arm R top-10 family composition: {'connection': 6, 'territory': 2, 'threshold': 2}.
Arm M top-10 family composition: {'connection': 5, 'territory': 2, 'threshold': 3}.

Parent-child drama heritability (arm M): r = 0.726 over 10 pairs.

## Re-eval re-pricing (phantom diagnostic)

- arm R: 24 re-evals, max |repricing| 0.0494, mean 0.0186
- arm M: 21 re-evals, max |repricing| 0.0482, mean 0.0160

## Counters

- M_dedup: 3
- R_quick_reject: 8
- stage0_invalid_draw_majority: 7
- stage0_invalid_too_short: 3
- stage0_quick_reject: 4
- arm M archive: filled_empty_cell=11, invalid_draw_majority=1, invalid_too_short=1, lost_first_batch=10, offered=24, reeval_rollouts=210, replaced=1
- arm R archive: filled_empty_cell=13, invalid_draw_majority=2, invalid_too_short=2, lost_first_batch=5, offered=24, reeval_rollouts=240, replaced=2
- wall time: 0.2 min

## Verdict

SMOKE RUN — would-be token (not registered): ARCHIVE_NEUTRAL
