# RC2 planning-gap — closeness-confound anchor calibration

Registered obligation: rc2_descriptor_v2/RESULTS.md binding input (c) — quality signal demonstrated on the S4/S5 vs d4015 pair BEFORE any search spend. Protocol pre-committed in `anchor_calibration.py`; bar applied verbatim.

Signal: PG = seat-balanced score of net-free UCT@256 vs UCT@16 − 0.5 (uniform prior, random-rollout leaf, c_puct 1.5); n=48 per game (streams [42, 43], draws = 0.5). Net-free is required: rc2_learnability recorded PPO pass-collapse on 3/4 anchors, so net-guided search would inherit poisoned priors.

| game | blind mean | family | PG (mean) | per-stream PG | W/D/L (deep) | mean plies |
|---|---:|---|---:|---|---|---:|
| S4 | 3.0 | territory | **-0.323** | -0.312, -0.333 | 8/1/39 | 58.6 |
| S5 | 3.07 | territory | **+0.052** | +0.021, +0.083 | 26/1/21 | 54.0 |
| d4015a646ae3 | 3.83 | connection | **+0.438** | +0.417, +0.458 | 45/0/3 | 60.6 |
| e1453dac5445 (diagnostic) | 3.9 | threshold | **-0.229** | -0.333, -0.125 | 13/0/35 | 36.9 |

## Verdict: **PASS**

PG(d4015) +0.438 vs PG(S4) -0.323, PG(S5) +0.052 — bar: PG(d4015) strictly above both

Reading: PG ≈ 0 — deep search buys nothing (parity race / greedy-sufficient play); PG >> 0 — lookahead wins (live tactics). The closeness confound predicts S4/S5 near 0, d4015 above.

Wall time: 781.4s. COMPLETE
