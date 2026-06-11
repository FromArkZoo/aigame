# RC2 anchor probe — results

n=200 rollouts/game (n/2 random-pair + n/2 greedy-pair, anchor_drama seeding), base_seed=11, games=all 10 anchors.
Protocol + bars per experiments/rc2_anchor/PREREGISTRATION.md (locked): observer defaults r=2/strength=1.0/decay=0.5; threshold-family progress traces at the game's own propagation params (registered dual parameterization; observer measures current-stone influence — ghost-influence divergence documented in the prereg). Draws skipped from obs_drama and counted. Bootstrap: 1000 resamples, 95% percentile CIs.

## Per-game table

| game | pod | family | n_used | draws | obs_drama [95% CI] | obs_lead_changes [95% CI] | blend [95% CI] | blend_nan_resamples | interaction_rate [95% CI] | go_essence |
|---|---|---|---:|---:|---|---|---|---:|---|---:|
| d4015a646ae3 | ABOVE | connection | 181 | 19 | 0.1236 [0.1028, 0.1440] | 3.1250 [2.7799, 3.4850] | 0.4992 [0.3751, 0.6023] | 0 | 0.3030 [0.2761, 0.3298] | — |
| s_flip_r2 | ABOVE | field_connection | 200 | 0 | 0.1284 [0.1132, 0.1454] | 3.3650 [3.0050, 3.7350] | 0.5654 [0.4656, 0.6161] | 0 | 0.1187 [0.1035, 0.1336] | — |
| a1_field_connect | ABOVE | field_connection | 200 | 0 | 0.1322 [0.1157, 0.1498] | 3.3800 [3.0649, 3.7350] | 0.5806 [0.4864, 0.6352] | 0 | 0.1127 [0.0987, 0.1279] | — |
| d995cf010504 | BUFFER | threshold | 194 | 6 | 0.0820 [0.0697, 0.0948] | 2.4750 [2.1350, 2.8402] | 0.2279 [0.1220, 0.3175] | 0 | 0.2028 [0.1782, 0.2260] | 0.0936 |
| 573562833174 | BUFFER | connection | 194 | 6 | 0.3041 [0.2806, 0.3279] | 3.4050 [2.9599, 3.8053] | 1.0000 [0.8353, 1.0000] | 0 | 0.3015 [0.2724, 0.3322] | 0.0027 |
| b12ff78f1c1d | BUFFER | threshold | 188 | 12 | 0.0861 [0.0721, 0.1018] | 2.4650 [2.1200, 2.8102] | 0.2371 [0.1115, 0.3356] | 0 | 0.2462 [0.2165, 0.2756] | 0.1503 |
| e52e8889517a | BELOW | threshold | 200 | 0 | 0.0433 [0.0363, 0.0510] | 2.0200 [1.7650, 2.2850] | 0.0087 [0.0000, 0.0540] | 0 | 0.0856 [0.0744, 0.0966] | 0.2031 |
| bfd1bb7ced76 | BELOW | threshold | 200 | 0 | 0.0433 [0.0364, 0.0504] | 2.0200 [1.7699, 2.2650] | 0.0087 [0.0000, 0.0568] | 0 | 0.0856 [0.0761, 0.0958] | 0.1904 |
| e1453dac5445 | BELOW | threshold | 200 | 0 | 0.0480 [0.0402, 0.0568] | 1.9900 [1.7397, 2.2650] | 0.0000 [0.0000, 0.0680] | 0 | 0.0838 [0.0730, 0.0942] | 0.1810 |
| 1fea3357dca4 | BELOW | threshold | 200 | 0 | 0.0423 [0.0361, 0.0485] | 2.3350 [2.0596, 2.6150] | 0.0000 [0.0000, 0.0812] | 0 | 0.1238 [0.1083, 0.1392] | 0.2107 |

BUFFER games (d995cf010504, 573562833174, b12ff78f1c1d) are reported above but excluded from the binary separation bars (prereg pod rule). 573562833174 enters only via the binding secondary check.

## Bars per candidate column (point estimates; PASS iff ALL four hold)

### obs_drama — PASS

| bar | detail | pass | fragile |
|---|---|:---:|---|
| 1. mean(ABOVE) > mean(BELOW) | mean(ABOVE)=0.1281 vs mean(BELOW)=0.0442 | YES | no (100.0%) |
| 2. boundary inversions: count of BELOW games above min(ABOVE) <= 1 | inversions=0 (min ABOVE=0.1236) | YES | no (100.0%) |
| 3. e1453dac5445 does not score above any ABOVE-pod game | e1453dac5445=0.0480 vs min(ABOVE)=0.1236 | YES | no (100.0%) |
| 4. secondary (binding): signal(573562833174) > signal(e1453dac5445) | 573562833174=0.3041 vs e1453dac5445=0.0480 | YES | no (100.0%) |

### blend — PASS

| bar | detail | pass | fragile |
|---|---|:---:|---|
| 1. mean(ABOVE) > mean(BELOW) | mean(ABOVE)=0.5484 vs mean(BELOW)=0.0044 | YES | no (100.0%) |
| 2. boundary inversions: count of BELOW games above min(ABOVE) <= 1 | inversions=0 (min ABOVE=0.4992) | YES | no (100.0%) |
| 3. e1453dac5445 does not score above any ABOVE-pod game | e1453dac5445=0.0000 vs min(ABOVE)=0.4992 | YES | no (100.0%) |
| 4. secondary (binding): signal(573562833174) > signal(e1453dac5445) | 573562833174=1.0000 vs e1453dac5445=0.0000 | YES | no (100.0%) |

### interaction_rate — PASS

| bar | detail | pass | fragile |
|---|---|:---:|---|
| 1. mean(ABOVE) > mean(BELOW) | mean(ABOVE)=0.1781 vs mean(BELOW)=0.0947 | YES | no (100.0%) |
| 2. boundary inversions: count of BELOW games above min(ABOVE) <= 1 | inversions=1 (min ABOVE=0.1127) | YES | no (99.5%) |
| 3. e1453dac5445 does not score above any ABOVE-pod game | e1453dac5445=0.0838 vs min(ABOVE)=0.1127 | YES | no (99.8%) |
| 4. secondary (binding): signal(573562833174) > signal(e1453dac5445) | 573562833174=0.3015 vs e1453dac5445=0.0838 | YES | no (100.0%) |

### go_essence — FAIL

| bar | detail | pass | fragile |
|---|---|:---:|---|
| 1. mean(ABOVE) > mean(BELOW) | not evaluable (missing column values) | no | — |
| 2. boundary inversions: count of BELOW games above min(ABOVE) <= 1 | not evaluable (missing column values) | no | — |
| 3. e1453dac5445 does not score above any ABOVE-pod game | not evaluable (missing column values) | no | — |
| 4. secondary (binding): signal(573562833174) > signal(e1453dac5445) | 573562833174=0.0027 vs e1453dac5445=0.1810 | no | — |

GE control note: bars 1–3 are not evaluable — the prereg registers go_essence for the R21 games only ('—' for all three ABOVE-pod games), so the expected-FAIL control column cannot pass them. (genesis_v2_run8.db does hold a run8-era go_essence for d4015a646ae3, 0.3858, but the registered column definition excludes it: R8-era GE is not comparable to R21 GE.)

## Verdict

```
PHASE_C_GO
```

Candidate 1 (obs_drama) or 2 (blend) PASS -> register the archive-integration probe; obs_drama or blend is the primary archive-axis descriptor.

## Notes

- blend = sqrt(norm(obs_drama) x norm(obs_lead_changes)); min-max norms over the full anchor-set point estimates (degenerate-flat guard: max==min -> norm 0.5 for all). Blend CIs: drama/lead resampled jointly per game, re-normalized per resample against the OTHER games' fixed point estimates (isolates that game's sampling noise); resamples with all-draw drama yield nan and are dropped from the CI (count reported as blend_nan_resamples).
- FRAGILE flag (not a gate): bar passes by point estimate but its defining inequality fails in > 2.5% of bootstrap resamples — the operationalization of the prereg's CI-overlap clause.
- go_essence read from each R21 game's source DB scores table (the registered column source). Informational GE values quoted in the prereg pod tables came from the R21 report and differ materially for some games (e.g. 1fea 0.211 vs 0.118 quoted in the pod table; under the registered DB source e1453 is the LOWEST GE of the BELOW pod, not GE-top) — bar outcomes verified identical under either set.
- Anchor-set property: e52e8889517a and bfd1bb7ced76 differ only in max_turns (100 vs 200); their columns are expected to be heavily correlated.
- metrics/descriptors.py and metrics/rollout_traces.py are locked; per-rollout values were assembled from their public functions and cross-checked against descriptor_row (exact-equality assert) on the first game processed.
