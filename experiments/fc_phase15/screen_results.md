# FC phase-1.5 — mechanical screen

PPO budget 5000, seeds [42, 43, 44], instrumented sampled mirror eval n=200/seed. Bars per PREREGISTRATION.md.

## c2_contested_terrain

**SKIPPED — invalidated at calibration (BIAS_UNRESOLVED; sanity gate, PREREGISTRATION.md).**

## c1_field_flip vs a0_baseline

| signal | arm | A0 | win? |
|---|---:|---:|:---:|
| lead_changes | 5.713 | 5.285 | YES |
| game_length | 155.057 | 61.892 | no |
| control_flip_rate | 4.187 | 5.298 | no |
| connection_win_fraction | 0.697 | 1.000 | no |

**1/4 signals; sanity FAIL.**

## c3_control_capture vs a0_baseline

| signal | arm | A0 | win? |
|---|---:|---:|:---:|
| lead_changes | 5.355 | 5.285 | YES |
| game_length | 154.608 | 61.892 | no |
| control_flip_rate | 4.154 | 5.298 | no |
| connection_win_fraction | 0.712 | 1.000 | no |

**1/4 signals; sanity FAIL.**

## Reference rows (A0/A1, new instrumentation)

- a0_baseline: lead_changes=5.285, game_length=61.892, control_flip_rate=5.298, connection_win_fraction=1.000, trained_vs_random=0.993
- a1_field_connect: lead_changes=6.285, game_length=70.395, control_flip_rate=10.606, connection_win_fraction=0.990, trained_vs_random=0.863

**NO ARM CLEARED 3/4 + sanity — screen NO-GO; stop before the blind campaign (spec §6b).**
