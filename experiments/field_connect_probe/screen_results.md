# Field-Connect probe — mechanical screen

PPO budget 5000, seeds [42, 43, 44], instrumented sampled mirror eval n=200/seed.

| metric | A1 (Field-Connect) | A0 (baseline) | A1 wins? |
|---|---:|---:|:---:|
| capture_rate | 0.000 | 3.225 | no |
| decisiveness | 0.990 | 1.000 | no |
| lead_changes | 6.285 | 5.285 | YES |
| game_length | 70.395 | 61.892 | YES |
| seat_balance | 0.060 | 0.065 | — |
| draw_rate | 0.002 | 0.000 | — |
| trained_vs_random | 0.863 | 0.993 | — |

**A1 beats A0 on 2/4 pre-registered signals (GO requires >= 3; spec §8c).**

Healthy length band: (30.0, 160.0). game_length 'win' = A1 in band and at-least-as-central as A0 (95 = band midpoint).

PPO-learnability guard (spec §10): if A1 trained_vs_random is near 0.5, a screen miss is UNLEARNABLE-not-shallow — report separately, do not score as a clean no-go.