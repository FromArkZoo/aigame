# R21 S2 A/B re-score — R20 slate under planning-horizon-augmented GE

Budget 10000 ep, seed 42, rollouts 20, `w_planning = depth_weight * 0.5 = 0.5`.

**Columns:**

- `original GE` — stored value from `scores.go_essence`. Includes the full `evaluate_game()` pipeline (seat-balance, length, hybrid, stability, timeout, novelty penalties).
- `baseline GE` — `composite_score` on the same stored signals (simplicity / depth / non-triv / diversity) with `w_planning = 0`. **Pre-penalty.** This is the apples-to-apples reference for new GE.
- `new GE` — `composite_score` on the same signals plus fresh `planning_horizon` from a 20-rollout PPO inference probe, with `w_planning = 0.5`. **Pre-penalty.**
- `Delta` — `new GE − baseline GE`. Isolates the metric change.

## Ranking on augmented GE

| Rank | Game | substrate | original GE | baseline GE | planning_horizon | **new GE** | Delta |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | `c850f91a55b4` | menger | 0.3399 | 0.4472 | 0.1812 | **0.3458** | -0.1014 |
| 2 | `a6385db22c0b` | menger | 0.2621 | 0.4139 | 0.1812 | **0.3157** | -0.0982 |
| 3 | `b160b1f55378` | menger | 0.2738 | 0.4053 | 0.1812 | **0.3081** | -0.0972 |
| 4 | `49a2e33895f4` | menger | 0.2689 | 0.3980 | 0.0916 | **0.2852** | -0.1128 |
| 5 | `d1dbc6568fc7` | menger | 0.2091 | 0.3537 | 0.1812 | **0.2634** | -0.0903 |
| 6 | `5f5c72e15220` | menger | 0.1728 | 0.3819 | 0.0406 | **0.2615** | -0.1204 |
| 7 | `fcedbc14043d` | grid_control | 0.2142 | 0.3702 | 0.0570 | **0.2553** | -0.1150 |
| 8 | `625bfc1f3f49` | carpet | 0.1183 | 0.3220 | 0.1367 | **0.2300** | -0.0920 |
| 9 | `f98b9414f638` | menger | 0.2879 | 0.2727 | 0.0501 | **0.1783** | -0.0944 |

## Pass criteria

- G4.1 FAIL — trio spread 0.0523 >= 0.05 (GEs: {'a6385db22c0b': 0.3157, 'b160b1f55378': 0.3081, 'd1dbc6568fc7': 0.2634})
- G4.2 (depth rec 5f5c72e15220) FAIL — rank 6 (need <= 2)
- G4.3 (pie game 625bfc1f3f49) FAIL — rank 8 (need <= 2)

**Overall: FAIL — bisect w_planning**

## On FAIL — bisection guide

Re-run with `--use-cache --w-planning-ratio <new>`. Cached probes make this near-instant. Try doubling and halving the current ratio. If neither range passes, planning-horizon weighting can't satisfy the three criteria simultaneously — escalate to user before launch.
