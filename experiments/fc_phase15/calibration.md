# FC phase-1.5 — komi calibration

PPO budget 3000, seed 42, sampled mirror eval n=200 (seat-swap, deterministic=False). PASS = smallest komi with bias <= 0.1. A0/A1 passed through from probe calibration unchanged.

| arm | komi | p1_winrate | bias | draws | verdict |
|---|---:|---:|---:|---:|:---:|
| c1_field_flip | 0.00 | 0.410 | 0.090 | 0.325 | PASS |
| c2_contested_terrain | 0.00 | 0.215 | 0.285 | 0.635 | no |
| c2_contested_terrain | 0.05 | 0.195 | 0.305 | 0.655 | no |
| c2_contested_terrain | 0.10 | 0.185 | 0.315 | 0.605 | no |
| c2_contested_terrain | 0.15 | 0.185 | 0.315 | 0.605 | no |
| c2_contested_terrain | 0.20 | 0.185 | 0.315 | 0.605 | no |
| c2_contested_terrain | 0.25 | 0.185 | 0.315 | 0.605 | no |
| c2_contested_terrain | 0.30 | 0.185 | 0.315 | 0.605 | no |
| c2_contested_terrain | — | — | — | — | **BIAS_UNRESOLVED** |
| c3_control_capture | 0.00 | 0.695 | 0.195 | 0.035 | no |
| c3_control_capture | 0.05 | 0.625 | 0.125 | 0.005 | no |
| c3_control_capture | 0.10 | 0.585 | 0.085 | 0.000 | PASS |
