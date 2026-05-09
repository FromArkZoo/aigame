# R20 champion-finalization results

Per-game GE distribution from 5 outer reruns × `num_independent_runs=3` C2 averaging = 15 unique PPO seeds per game.

| Substrate | Game | original_GE | n | mean GE | std GE | min | max | range | Δ vs original |
|---|---|---|---|---|---|---|---|---|---|
| carpet | `625bfc1f3f49` | 0.1183 | 5 | 0.0602 | 0.0754 | 0.0033 | 0.1620 | 0.1586 | -0.0581 |
| grid_control | `fcedbc14043d` | 0.2142 | 5 | 0.1292 | 0.0459 | 0.0687 | 0.1911 | 0.1224 | -0.0850 |
| menger | `a6385db22c0b` | 0.2621 | 5 | 0.2410 | 0.1199 | 0.1444 | 0.4167 | 0.2723 | -0.0211 |
| menger | `b160b1f55378` | 0.2738 | 5 | 0.1801 | 0.0737 | 0.0946 | 0.2915 | 0.1969 | -0.0937 |
| menger | `5f5c72e15220` | 0.1728 | 5 | 0.1705 | 0.1288 | 0.0188 | 0.3092 | 0.2904 | -0.0023 |
| menger | `d1dbc6568fc7` | 0.2091 | 5 | 0.1419 | 0.1045 | 0.0369 | 0.2560 | 0.2190 | -0.0672 |
| menger | `f98b9414f638` | 0.2879 | 5 | 0.1287 | 0.0886 | 0.0689 | 0.2852 | 0.2163 | -0.1592 |
| menger | `c850f91a55b4` | 0.3399 | 5 | 0.1059 | 0.0970 | 0.0336 | 0.2406 | 0.2070 | -0.2340 |
| menger | `49a2e33895f4` | 0.2689 | 5 | 0.0899 | 0.0303 | 0.0510 | 0.1252 | 0.0742 | -0.1790 |

## Read
- `std GE` is the post-15-seed measurement noise. Goal: < 0.04 on menger, < 0.03 on carpet (vs Phase A under-estimates of 0.014/0.155).
- `Δ vs original` shows where the production-stack 3-seed scoring was over- or under-estimating. Large positive Δ = the original was an unlucky-seed underestimate (carpet's Phase B finding).
- Cross-substrate comparisons are honest only when |Δmean| > max(σ_a, σ_b). Annotate substrate-vs-substrate claims accordingly.
