# R21 menger champion-finalization results

Per-game GE distribution from 20 outer reruns × `num_independent_runs=3` C2 averaging = 60 unique PPO seeds per game.

Header line "R20" and "15 unique PPO seeds" in the auto-generated output are stale strings in `experiments/r20_finalization/finalize_champions.py:329-332` — corrected here at commit time; upstream fix queued for R22.

| Substrate | Game | original_GE | n | mean GE | std GE | min | max | range | Δ vs original |
|---|---|---|---|---|---|---|---|---|---|
| menger | `e1453dac5445` | 0.1810 | 20 | 0.1775 | 0.1038 | 0.0000 | 0.4340 | 0.4340 | -0.0035 |
| menger | `d970e5bd7c48` | 0.1651 | 20 | 0.1441 | 0.0951 | 0.0000 | 0.3716 | 0.3716 | -0.0210 |
| menger | `e52e8889517a` | 0.2031 | 20 | 0.1376 | 0.0923 | 0.0000 | 0.3454 | 0.3454 | -0.0656 |
| menger | `d182cfb9e65e` | 0.1673 | 20 | 0.1320 | 0.0848 | 0.0216 | 0.2946 | 0.2731 | -0.0353 |
| menger | `bfd1bb7ced76` | 0.1904 | 20 | 0.1258 | 0.0716 | 0.0000 | 0.2636 | 0.2636 | -0.0645 |
| menger | `1fea3357dca4` | 0.2107 | 20 | 0.1175 | 0.0869 | 0.0000 | 0.3028 | 0.3028 | -0.0932 |
| menger | `d0d549703688` | 0.1883 | 20 | 0.1141 | 0.0800 | 0.0000 | 0.2515 | 0.2515 | -0.0742 |
| menger | `4933727afb0b` | 0.2029 | 20 | 0.1058 | 0.0670 | 0.0000 | 0.2412 | 0.2412 | -0.0971 |
| menger | `579c865452cd` | 0.1661 | 20 | 0.0825 | 0.0447 | 0.0262 | 0.1951 | 0.1689 | -0.0836 |

## Read
- `std GE` is the post-15-seed measurement noise. Goal: < 0.04 on menger, < 0.03 on carpet (vs Phase A under-estimates of 0.014/0.155).
- `Δ vs original` shows where the production-stack 3-seed scoring was over- or under-estimating. Large positive Δ = the original was an unlucky-seed underestimate (carpet's Phase B finding).
- Cross-substrate comparisons are honest only when |Δmean| > max(σ_a, σ_b). Annotate substrate-vs-substrate claims accordingly.
