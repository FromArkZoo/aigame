# CAL-G — RUSH/TILT guard revalidation at n=24  [C2]

RC2 §0 lock obligation. 12 mirrored TacticalAgent pairs -> n=24, pair_seeds(0..11); guards + harness reused from the locked descriptor-v2 runner. RUSH: >=25% decisive in <=6 plies. TILT: P1 >=80% of decisive.

| game | role | n | decisive | RUSH (share) | TILT (P1 share) | flip-prob RUSH | flip-prob TILT |
|---|---|---:|---:|---|---|---:|---:|
| S1 | RUSH target | 24 | 18 | FIRES (1.00) | — (0.78) | 0.000 | 0.409 |
| S4 | TILT target | 24 | 24 | — (0.00) | — (0.79) | 0.000 | 0.420 |
| S5 | TILT target | 24 | 24 | — (0.00) | — (0.79) | 0.000 | 0.420 |
| d4015a646ae3 | control | 24 | 24 | — (0.00) | — (0.46) | 0.000 | 0.000 |
| e1453dac5445 | control | 24 | 24 | — (0.00) | — (0.04) | 0.000 | 0.000 |
| s_flip_r2 | control (field) | 24 | 24 | — (0.00) | — (0.17) | 0.000 | 0.000 |
| a1_field_connect | control (field) | 24 | 24 | — (0.00) | — (0.17) | 0.000 | 0.000 |

## Verdict: **FAIL**

B-RUSH: PASS (S1 fires=True, controls silent=True); B-TILT: FAIL (S4|S5 fires=False, field controls silent=True)

flip-prob = P an independent n=24 re-run flips the guard flag (observed share as point estimate); reported, not binding — the resolution cost of n=24. Low on silent controls = robustly silent.

Wall time: 2642.7s. COMPLETE
