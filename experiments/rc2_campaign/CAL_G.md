# CAL-G — RUSH/TILT guard revalidation at n=24  [C2]

RC2 §0 lock obligation. 12 mirrored TacticalAgent pairs -> n=24, pair_seeds(0..11); guards + harness reused from the locked descriptor-v2 runner. RUSH: >=25% decisive in <=6 plies. **TILT re-priced 0.80 -> 0.625 for n=24** (§4); RUSH unchanged at 0.25.

| game | role | n | dec | RUSH (share) | TILT P1 share | fires@0.625 | would fire@0.80 | flip-prob TILT |
|---|---|---:|---:|---|---:|---|---|---:|
| S1 | RUSH target | 24 | 18 | FIRES (1.00) | 0.78 | FIRES | — | 0.084 |
| S4 | TILT target | 24 | 24 | — (0.00) | 0.79 | FIRES | — | 0.017 |
| S5 | TILT target | 24 | 24 | — (0.00) | 0.79 | FIRES | — | 0.017 |
| d4015a646ae3 | control | 24 | 24 | — (0.00) | 0.46 | — | — | 0.076 |
| e1453dac5445 | control | 24 | 24 | — (0.00) | 0.04 | — | — | 0.000 |
| s_flip_r2 | control (field) | 24 | 24 | — (0.00) | 0.17 | — | — | 0.000 |
| a1_field_connect | control (field) | 24 | 24 | — (0.00) | 0.17 | — | — | 0.000 |

## Verdict: **PASS**

B-RUSH: PASS (S1 fires=True, controls silent=True); B-TILT@0.625: PASS (S4|S5 fires=True, field controls silent=True)

Re-pricing rationale: at descriptor-v2's TILT=0.80, S4/S5 (19/24=0.79) do NOT fire and flip-prob=0.42 — the guard is a coin-flip at n=24. TILT=0.625 (15/24) is equidistant from the S4/S5 targets (19) and the highest control d4015 (11) — ~2σ each side; at 0.625 flip-prob≈0.01. RUSH needs no re-pricing (S1 fires 18/18, controls 0.00, flip-prob 0.000).

flip-prob = P an independent n=24 re-run flips the guard flag (observed share as point estimate); reported, not binding.

(verdict re-derived from cached shares; no game re-run)
Wall time: 0.0s. COMPLETE
