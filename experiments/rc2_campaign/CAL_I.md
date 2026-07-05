# CAL-I — pre-campaign instrument check  [§5]

RC2 §5 pre-campaign gate. T1 instrument (UCT@128 vs UCT@16, net-free, play_cell), fresh streams [46, 47], n=24, threshold CAL_I_THRESHOLD=0.431 (bars.py, imported).

| game | blind mean | family | n | PG (mean) | per-stream PG | W/D/L (deep) | mean plies |
|---|---:|---|---:|---:|---|---|---:|
| d4015a646ae3 | 3.83 | connection | 24 | **+0.292** | +0.417, +0.167 | 19/0/5 | 55.7 |
| S4 | 3.0 | territory | 24 | **-0.458** | -0.500, -0.417 | 1/0/23 | 57.5 |

## Verdict: **PASS**

PG(d4015a646ae3) +0.2917 - PG(S4) -0.4583 = separation +0.7500 vs bar >= 0.431 -> PASS

Bar: PG(d4015a646ae3) - PG(S4) >= CAL_I_THRESHOLD. FAIL -> PROBE_INVALID (prereg §9); no campaign.


Wall time: 124.7s. COMPLETE
