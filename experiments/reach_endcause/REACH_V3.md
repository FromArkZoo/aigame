# REACH-v3 — end-cause guard under UCT play

Successor to REACH-v2 (FAIL: threshold-unreachability is policy-relative; tactical play crosses S2's threshold 100/100). Same end-cause question under the PG convention's UCT games on FRESH seed streams (44/45). Protocol pre-committed in `reach_v3.py`; bars mirror the original G-REACH wording.

| game | blind mean | n | draw share | per-stream | fires | mean plies |
|---|---:|---:|---:|---|---|---:|
| S2 (binding) | 3.2 | 48 | **0.417** | 0.417, 0.417 | FIRES | 51.2 |
| e1453dac5445 (binding) | 3.9 | 48 | **0.000** | 0.000, 0.000 | — | 38.4 |
| 1fea3357dca4 | None | 24 | **0.208** | 0.250, 0.167 | — | 77.1 |
| b12ff78f1c1d | None | 24 | **0.083** | 0.167, 0.000 | — | 40.8 |
| bfd1bb7ced76 | None | 24 | **0.042** | 0.083, 0.000 | — | 47.2 |
| d995cf010504 | None | 24 | **0.000** | 0.000, 0.000 | — | 36.5 |
| e52e8889517a | None | 24 | **0.042** | 0.083, 0.000 | — | 47.2 |

## Verdict: **PASS**

B1 fires-on-S2: PASS (draw_share 0.417); B2 silent-on-e1453: PASS (draw_share 0.000)

In-loop cost: zero — a PG-based search already plays these games; draw_share falls out of the screening records.

Wall time: 2215.9s. COMPLETE
