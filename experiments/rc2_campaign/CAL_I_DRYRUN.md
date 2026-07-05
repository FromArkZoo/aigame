# CAL-I — pre-campaign instrument check  [§5] (DRY RUN — wiring check only, NOT the binding measurement)

RC2 §5 pre-campaign gate. T1 instrument (UCT@32 vs UCT@8, net-free, play_cell), fresh streams [46, 47], n=4, threshold CAL_I_THRESHOLD=0.431 (bars.py, imported).

| game | blind mean | family | n | PG (mean) | per-stream PG | W/D/L (deep) | mean plies |
|---|---:|---|---:|---:|---|---|---:|
| d4015a646ae3 | 3.83 | connection | 4 | **+0.500** | +0.500, +0.500 | 4/0/0 | 71.5 |
| S4 | 3.0 | territory | 4 | **-0.250** | -0.500, +0.000 | 1/0/3 | 56.2 |

## Verdict: **PASS**

PG(d4015a646ae3) +0.5000 - PG(S4) -0.2500 = separation +0.7500 vs bar >= 0.431 -> PASS

Bar: PG(d4015a646ae3) - PG(S4) >= CAL_I_THRESHOLD. FAIL -> PROBE_INVALID (prereg §9); no campaign.

(verdict re-derived from cached results; no game re-run)
Wall time: 0.0s. DRY RUN — non-binding
