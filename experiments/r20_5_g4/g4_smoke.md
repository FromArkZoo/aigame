# R20.5 G4 — mirror seat bias < 0.10

PPO 3000 ep, seed 42, then sampled trained-vs-trained eval (seat-swap, deterministic=False, n=200). G4 metric = `abs(sampled_p1_winrate - 0.5)`; threshold = 0.1.

| Game | sampled_p1_wr | **G4 seat bias** | sampled_len | greedy_p1_wr | det_p0_wr | G4 | elapsed |
|---|---:|---:|---:|---:|---:|:---:|---:|
| `2f378e8c18b5` | 0.630 | **0.130** | 57.1 | 0.120 | 0.500 | FAIL | 120s |
| `66c7c98d3745` | 0.560 | **0.060** | 57.1 | 0.100 | 0.500 | PASS | 117s |
| `77f8288387d9` | 0.560 | **0.060** | 57.1 | 0.100 | 0.500 | PASS | 119s |
| `c9fd0350fdf7` | 0.560 | **0.060** | 57.1 | 0.100 | 0.500 | PASS | 113s |
| `faebc7094d51` | 0.640 | **0.140** | 74.9 | 0.220 | 0.500 | FAIL | 154s |

**G4: FAIL (3/5 < 0.1) — failing: `2f378e8c18b5`, `faebc7094d51`**

## Methodology

**G4 metric is sampled trained-vs-trained mirror seat-bias.** Greedy and deterministic-trained metrics are reported as diagnostics, NOT for the G4 verdict, because both are misleading on pie-rule games:

- `greedy_p1_winrate`: GreedyAgent always-swaps under pie (commit `d25590d`). On a pie-rule game P2 trivially wins under greedy-vs-greedy regardless of equilibrium balance. Use as upper-bound rush-broken filter only — see harness.py:50.
- `det_p0_wr` (deterministic trained): per harness module docstring, deterministic argmax collapses to identical 2-step games regardless of game quality. Not a real signal.
- `sampled_p1_winrate` (the G4 metric): trained-vs-trained sampled play with seat-swap halves preserves the equilibrium where pie usage is rational. Deviation from 0.500 = real structural seat bias.
