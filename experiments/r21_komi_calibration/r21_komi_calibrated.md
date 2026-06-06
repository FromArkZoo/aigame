# R21 S4 — komi auto-calibration verdict

Pass condition: measured g4_seat_bias ≤ 0.1 − 2.0σ (2.0×0.0354 = 0.0708) ≈ 0.0292.

| # | substrate | game_id | decision | calibrated_komi | smallest passing |
|---|---|---|---|---:|---|
| 1 | menger | `e1453dac5445` | FAIL_RUSH_BROKEN | — | ✗ (rush-broken) |
| 2 | menger | `e52e8889517a` | PASS_komi_0.05 | 0.05 | ✓ |
| 3 | menger | `bfd1bb7ced76` | FAIL_RUSH_BROKEN | — | ✗ (rush-broken) |
| 4 | menger | `1fea3357dca4` | FAIL_RUSH_BROKEN | — | ✗ (rush-broken) |
| 5 | carpet | `d995cf010504` | PASS_komi_0.05 | 0.05 | ✓ |
| 6 | grid | `b12ff78f1c1d` | FAIL_RUSH_BROKEN | — | ✗ (rush-broken) |
| 7 | grid | `573562833174` | FAIL_RUSH_BROKEN | — | ✗ (rush-broken) |

**Calibrated**: 2. **Rush-broken (FAIL G3)**: 5.

## Per-candidate grid evaluations

### `e1453dac5445` (menger)

| komi | g4_seat_bias | passed |
|---:|---:|---|
| 0.00 | 0.0600 | ✗ |
| 0.05 | 0.1150 | ✗ |
| 0.10 | 0.2000 | ✗ |
| 0.15 | 0.2800 | ✗ |
| 0.20 | 0.3600 | ✗ |
| 0.25 | 0.4400 | ✗ |
| 0.30 | 0.4100 | ✗ |

### `e52e8889517a` (menger)

| komi | g4_seat_bias | passed |
|---:|---:|---|
| 0.00 | 0.0800 | ✗ |
| 0.05 | 0.0150 | ✓ |

### `bfd1bb7ced76` (menger)

| komi | g4_seat_bias | passed |
|---:|---:|---|
| 0.00 | 0.0600 | ✗ |
| 0.05 | 0.1050 | ✗ |
| 0.10 | 0.2600 | ✗ |
| 0.15 | 0.3400 | ✗ |
| 0.20 | 0.4400 | ✗ |
| 0.25 | 0.4850 | ✗ |
| 0.30 | 0.5000 | ✗ |

### `1fea3357dca4` (menger)

| komi | g4_seat_bias | passed |
|---:|---:|---|
| 0.00 | 0.1150 | ✗ |
| 0.05 | 0.0650 | ✗ |
| 0.10 | 0.2950 | ✗ |
| 0.15 | 0.3950 | ✗ |
| 0.20 | 0.1350 | ✗ |
| 0.25 | 0.2550 | ✗ |
| 0.30 | 0.4950 | ✗ |

### `d995cf010504` (carpet)

| komi | g4_seat_bias | passed |
|---:|---:|---|
| 0.00 | 0.1600 | ✗ |
| 0.05 | 0.0050 | ✓ |

### `b12ff78f1c1d` (grid)

| komi | g4_seat_bias | passed |
|---:|---:|---|
| 0.00 | 0.1300 | ✗ |
| 0.05 | 0.0300 | ✗ |
| 0.10 | 0.1500 | ✗ |
| 0.15 | 0.2800 | ✗ |
| 0.20 | 0.3050 | ✗ |
| 0.25 | 0.3800 | ✗ |
| 0.30 | 0.4050 | ✗ |

### `573562833174` (grid)

| komi | g4_seat_bias | passed |
|---:|---:|---|
| 0.00 | 0.5000 | ✗ |
| 0.05 | 0.5000 | ✗ |
| 0.10 | 0.5000 | ✗ |
| 0.15 | 0.5000 | ✗ |
| 0.20 | 0.5000 | ✗ |
| 0.25 | 0.5000 | ✗ |
| 0.30 | 0.5000 | ✗ |
