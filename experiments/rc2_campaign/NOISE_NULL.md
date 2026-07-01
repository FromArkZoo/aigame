# RC2 §0 — NOISE-NULL (BAR W-PG floor)  [C4]

95th-percentile noise-only floor for P90-P10 of **floored** T1-PG, per family N. A Stage-0 family is LIVE (§6) iff its observed P90-P10 of floored T1-PG meets/exceeds the floor at its N.

- Model: discrete T1-PG estimator (24 games in {0,0.5,1.0}), true PG=0, FLOORED (max(PG,0)); floor = 95th pct of P90-P10 over MC draws.
- MC: reps=100,000, seed=95,000,000 (registered instrument stream, §2), n_games=24.
- **Binding sigma = sigma_max = 0.1016** (from sigma-FILE, max-over-roster) -> draw-rate d=0.009.

| N | floor (binding, floored, sigma_max) |
|---:|---:|
| 20 | **0.1708** |
| 24 | **0.1667** |
| 30 | **0.1687** |
| 40 | **0.1667** |
| 50 | **0.1667** |
| 75 | **0.1667** |
| 100 | **0.1667** |
| 150 | **0.1667** |

## Reconciliation with the draft's provisional reference

Draft §0 registered 'approx 0.28 at N=20, sigma=0.087'. That number reproduces on **raw** (unfloored) T1-PG: raw floor = 0.2729 (matches approx 0.28). The **floored** floor at the same N/sigma is 0.1479. Because §3/§6 define the bar on FLOORED T1-PG, the floored floor is binding and the draft's raw-based 0.28 is superseded — the §0 reference text needs a one-line correction at lock. Floored is also LESS conservative (lower floor), so BAR W is easier to pass than the raw 0.28 would have made it (guards against false ARCHIVE_KILL of a valid archive).

The binding floor uses sigma_max (conservative across roster). The per-family floor is looked up at the family's actual N at Stage-0 close using this locked model/seed; intermediate N are linearly interpolated on this grid.

COMPLETE
