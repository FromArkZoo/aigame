# RC2 Phase C archive probe — results

Protocol per experiments/rc2_archive/PREREGISTRATION.md (locked): base_seed 17, Stage-0 n=100, Stage-1 n=50, B=600/arm, re-eval at (100, 200, 300, 400, 500, 600).

## CAL

- drama(573562833174) = 0.3057
- drama(e1453dac5445) = 0.0649
- gap = 0.2408 (floor 0.15) -> PASS

## Stage 0 — BAR W (within-family separation)

Attempts 252, evaluated 160, valid 97.

| family | n_valid | p10 | p90 | p90-p10 | LIVE (floor 0.064) |
|---|---:|---:|---:|---:|---|
| territory | 26 | 0.0667 | 0.2161 | 0.1494 | YES |
| elimination | UNSAMPLED (0) | | | | |
| connection | 48 | 0.0548 | 0.1288 | 0.0739 | YES |
| threshold | 23 | 0.0416 | 0.0976 | 0.0560 | no |

BAR W: 2 LIVE of 3 sampled -> PASS

## Stage 1 — BAR H (matched-budget search value)

| arm | evals | coverage | QD-score | top-10 mean drama [95% CI] | skips |
|---|---:|---:|---:|---|---:|
| R | 600 | 31 | 4.682 | 0.2331 [0.2243, 0.2422] | 0 |
| M | 600 | 42 | 7.028 | 0.2905 [0.2807, 0.3004] | 0 |

BAR H: top10(M) - top10(R) = 0.0574 (floor 0.03) -> PASS

Jointly filled cells: 30; arm M wins 20, same-elite ties 4, losses 6.

Arm R top-10 family composition: {'territory': 9, 'threshold': 1}.
Arm M top-10 family composition: {'connection': 4, 'territory': 5, 'threshold': 1}.

Parent-child drama heritability (arm M): r = 0.444 over 533 pairs.

## Re-eval re-pricing (phantom diagnostic)

- arm R: 168 re-evals, max |repricing| 0.0305, mean 0.0048
- arm M: 222 re-evals, max |repricing| 0.0447, mean 0.0057

## Counters

- M_dedup: 387
- M_quick_reject: 32
- R_quick_reject: 325
- stage0_invalid_draw_majority: 36
- stage0_invalid_too_short: 27
- stage0_quick_reject: 92
- arm M archive: filled_empty_cell=42, invalid_draw_majority=153, invalid_too_short=74, lost_after_matching=34, lost_first_batch=304, offered=697, reeval_rollouts=11100, replaced=90, topup_rollouts=12100
- arm R archive: filled_empty_cell=31, invalid_draw_majority=178, invalid_too_short=91, lost_after_matching=12, lost_first_batch=333, offered=697, reeval_rollouts=8400, replaced=52, topup_rollouts=5650
- wall time: 24.7 min

## Verdict

```
ARCHIVE_GO
```
