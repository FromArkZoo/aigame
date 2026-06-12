# RC2 planning-gap — cost/noise tiering

Which cheap tier preserves the full-convention screening properties? Bars pre-committed in `cost_tiering.py` (A1 sign separation of the positive set over the non-positive set, S5 free; A2 leader in {S3, d4015}); cheapest passing tier adopted for in-loop screening, full convention reserved for survivors.

| tier | config | A1 | A2 | Spearman vs full | CPU total | CPU/game range |
|---|---|---|---|---:|---:|---|
| T1 | 128v16, n=24 | PASS | PASS | +0.99 | 2211s | 131–543s |
| T2 | 64v8, n=24 | FAIL | PASS | +0.81 | 1400s | 76–280s |
| T3 | 64v8, n=12 | FAIL | PASS | +0.64 | 812s | 46–155s |

## Per-game PG by tier

| game | full | T1 | T2 | T3 |
|---|---:|---:|---:|---:|
| S1 | +0.000 | -0.021 | -0.083 | -0.167 |
| S2 | +0.198 | +0.042 | -0.125 | -0.208 |
| S3 | +0.479 | +0.458 | +0.229 | +0.167 |
| S4 | -0.323 | -0.417 | -0.500 | -0.500 |
| S5 | +0.052 | +0.042 | -0.021 | +0.000 |
| d4015a646ae3 | +0.438 | +0.417 | +0.458 | +0.500 |
| e1453dac5445 | -0.229 | -0.125 | -0.125 | +0.083 |

## Verdict: **ADOPT_T1**

T1: A1=True A2=True rho=+0.99 cpu=2211s; T2: A1=False A2=True rho=+0.81 cpu=1400s; T3: A1=False A2=True rho=+0.64 cpu=812s

Wall time: 1111.3s. COMPLETE

## Reading (post-verdict, non-binding)

1. **T1 adopted: ~5.3 CPU-min/game average** (range 2.2–9.1), vs ~20 for the
   full convention — a screening call is ~45 s wall on 7 workers. Full
   convention stays reserved for survivors.
2. **Why the cheaper tiers die: search depth IS the signal.** At 64 sims the
   deep side can no longer realize its advantage on the draw-prone/threshold
   boards — S2 collapses from +0.198 (full) through +0.042 (T1) to −0.125
   (T2); e1453 even drifts positive at T3. Degrading the instrument degrades
   exactly the games where planning is hardest to detect. 128 sims is the
   floor, not a budget choice.
3. **T1's A1 margin is thin precisely on S2** (+0.042 vs S1's −0.021) — the
   draw-prone game is the screening tier's weakest separation. This is the
   gap REACH-v3 covers from the same game records at zero extra cost: S2
   gets flagged on draw share regardless of where its PG lands.
