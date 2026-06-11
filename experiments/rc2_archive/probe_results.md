# RC2 Phase C archive probe — results

Protocol per experiments/rc2_archive/PREREGISTRATION.md (locked): base_seed 13, Stage-0 n=100, Stage-1 n=50, B=300/arm, re-eval at (100, 200, 300).

## CAL

- drama(573562833174) = 0.3057
- drama(e1453dac5445) = 0.0649
- gap = 0.2408 (floor 0.15) -> PASS

## Stage 0 — BAR W (within-family separation)

Attempts 265, evaluated 160, valid 99.

| family | n_valid | p10 | p90 | p90-p10 | LIVE (floor 0.064) |
|---|---:|---:|---:|---:|---|
| territory | 27 | 0.0891 | 0.1834 | 0.0943 | YES |
| elimination | UNSAMPLED (0) | | | | |
| connection | 34 | 0.0466 | 0.1334 | 0.0868 | YES |
| threshold | 38 | 0.0276 | 0.1010 | 0.0734 | YES |

BAR W: 3 LIVE of 3 sampled -> PASS

## Stage 1 — BAR H (matched-budget search value)

| arm | evals | coverage | QD-score | top-10 mean drama [95% CI] | skips |
|---|---:|---:|---:|---|---:|
| R | 300 | 32 | 4.221 | 0.2054 [0.1957, 0.2155] | 0 |
| M | 300 | 39 | 5.469 | 0.2248 [0.2150, 0.2351] | 0 |

BAR H: top10(M) - top10(R) = 0.0194 (floor 0.03) -> FAIL

Jointly filled cells: 30; arm M wins 20, same-elite ties 3, losses 7.

Arm R top-10 family composition: {'territory': 10}.
Arm M top-10 family composition: {'territory': 10}.

Parent-child drama heritability (arm M): r = 0.344 over 279 pairs.

## Re-eval re-pricing (phantom diagnostic)

- arm R: 91 re-evals, max |repricing| 0.0547, mean 0.0057
- arm M: 109 re-evals, max |repricing| 0.0349, mean 0.0060

## Counters

- M_dedup: 124
- M_quick_reject: 3
- R_quick_reject: 146
- stage0_invalid_draw_majority: 42
- stage0_invalid_too_short: 19
- stage0_quick_reject: 105
- arm M archive: filled_empty_cell=39, invalid_draw_majority=67, invalid_too_short=24, lost_after_matching=17, lost_first_batch=192, offered=399, reeval_rollouts=5450, replaced=60, topup_rollouts=5100
- arm R archive: filled_empty_cell=32, invalid_draw_majority=82, invalid_too_short=58, lost_after_matching=10, lost_first_batch=177, offered=399, reeval_rollouts=4550, replaced=40, topup_rollouts=3000
- wall time: 10.5 min

## Verdict

```
ARCHIVE_NEUTRAL
```
