# SIEGE Stage-2 — 4-arm mechanical screen

PPO budget 5000, seeds [42, 43, 44], instrumented sampled mirror eval n=200/seed (m_siege: roles fixed, NO seat swap; symmetric arms: seat-swap halves). --anchor-result pass. Bars per experiments/siege/PREREGISTRATION.md Stage 2.

## m_siege

**SKIPPED — invalidated at calibration (M_GRID_UNRESOLVED / role-pie retry exhausted; PREREGISTRATION.md Stage 1). Registered outcome: campaign continues s-only.**

## Symmetric-arm bands (s/a1/a0)

| arm | draw_rate (<= 0.05) | seat_balance (<= 0.1) | trained_vs_random (>= 0.8) | pass? |
|---|---:|---:|---:|:---:|
| s_flip_r2 | 0.002 | 0.062 | 0.780 | no |
| a1_field_connect | 0.002 | 0.060 | 0.863 | YES |
| a0_baseline | 0.000 | 0.065 | 0.993 | YES |

## Reference rows (arm means, identical instrumentation)

- s_flip_r2: lead_changes=6.125, game_length=72.163, control_flip_rate=10.584, per_role_drama=0.143, connection_win_fraction=0.987, flip_events=7.838, timeout_share=0.013
- a1_field_connect: lead_changes=6.285, game_length=70.395, control_flip_rate=10.606, per_role_drama=0.151, connection_win_fraction=0.990, flip_events=0.000, timeout_share=0.008
- a0_baseline: lead_changes=5.285, game_length=61.892, control_flip_rate=5.298, per_role_drama=0.054, connection_win_fraction=1.000, flip_events=3.225, timeout_share=0.000

## Stop rule — z_flip_r2 template: s_flip_r2 vs a0_baseline (m_siege failed: missing from calibration)

| signal | s | a0 | win? |
|---|---:|---:|:---:|
| lead_changes > a0 | 6.125 | 5.285 | YES |
| game_length more central in [30,160] than a0 | 72.163 | 61.892 | YES |
| control_flip_rate > a0 | 10.584 | 5.298 | YES |
| connection_win_fraction >= 0.8 | 0.987 | 1.000 | YES |

**4/4 (threshold 3/4).**

## Verdict

**S-ONLY BLIND — m_siege fails the screen (missing from calibration) but s_flip_r2 clears the z_flip_r2 template 4/4 vs a0; blind runs s_flip_r2 vs a1_field_connect only.** NOTE: s_flip_r2 sanity bands FAIL — flagged for the record; the registered stop rule is the 3/4 template only.
