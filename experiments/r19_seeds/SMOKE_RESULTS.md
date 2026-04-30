# R19 B2 PPO smoke results — 19 seeds, 3000-ep budget

Run 2026-04-30. 3000-ep PPO per seed, 100 eval episodes, sampled-eval gate.
Identical harness as R18 (`experiments/r18_ppo_smoke/harness.py`).

## Aggregate

**10 pass, 9 drop.** Drops concentrated in two patterns:

1. **All 5 menger in-family seeds (m1–m5) drop** — `* + influence(r=1) + threshold-race`.
   Every drop is the same failure mode: avg game length stays just at/below the
   400-cell floor of 40 moves while greedy P1 wins 86 %. PPO at 3000 ep does not
   accumulate enough influence on the menger interior for P2 to disrupt.
2. **2 carpet probes drop** (c6 territory, c8 r=3 influence), **2 grid drop**
   (g1 R8 Connection Go, g3 hybrid validator).

| Substrate | Pass | Drop | Surviving combos |
|-----------|-----:|-----:|------------------|
| menger    | 3 / 8 | 5 | m6 territory, m7 connection, m8 r=2 inf |
| carpet    | 6 / 8 | 2 | c1, c2, c3, c4, c5 (in-family) + c7 connection |
| grid      | 1 / 3 | 2 | g2 (outnumber + influence + threshold) |

## Full table

| seed | status | sampled_avg_len | greedy_p1_wr | seat_bias | drop reason |
|------|--------|----------------:|-------------:|----------:|-------------|
| c1_outnumber2_inf2_threshold__carpet  | PASS |  45.1 | 0.74 | 0.24 | – |
| c2_outnumber3_inf2_threshold__carpet  | PASS |  43.9 | 0.74 | 0.24 | – |
| c3_custodian2_inf2_threshold__carpet  | PASS |  43.6 | 0.74 | 0.24 | – |
| c4_surround_inf2_threshold__carpet    | PASS |  44.0 | 0.74 | 0.24 | – |
| c5_none_inf2_threshold__carpet        | PASS |  44.7 | 0.74 | 0.24 | – |
| c6_outnumber2_territory__carpet       | DROP |  18.2 | 1.00 | 0.50 | seat bias 0.50 (P1 100% greedy) |
| c7_custodian_connection__carpet       | PASS |  17.7 | 0.46 | 0.04 | – |
| c8_outnumber2_inf3_threshold__carpet  | DROP |  49.1 | 0.88 | 0.38 | seat bias 0.38 (r=3 over-amplifies P1 tempo) |
| g1_custodian1_connection__grid        | DROP | 100.0 | 1.00 | 0.50 | seat bias 0.50 (R18 reproduced — P1 connects 16-row before P2 blocks) |
| g2_outnumber2_inf1_threshold__grid    | PASS |  38.6 | 0.62 | 0.12 | – |
| g3_hybrid_validator__grid             | DROP | 100.0 | 1.00 | 0.50 | seat bias 0.50 (move-action search blows P2's tempo) |
| m1_custodian2_inf1_threshold__menger  | DROP |  39.7 | 0.86 | 0.36 | length 39.7 < floor 40.0; seat bias 0.36 |
| m2_custodian1_inf1_threshold__menger  | DROP |  39.7 | 0.86 | 0.36 | length 39.7 < floor 40.0; seat bias 0.36 |
| m3_surround_inf1_threshold__menger    | DROP |  39.4 | 0.86 | 0.36 | length 39.4 < floor 40.0; seat bias 0.36 |
| m4_outnumber2_inf1_threshold__menger  | DROP |  40.2 | 0.86 | 0.36 | seat bias 0.36 |
| m5_none_inf1_threshold__menger        | DROP |  39.7 | 0.86 | 0.36 | length 39.7 < floor 40.0; seat bias 0.36 |
| m6_custodian2_territory__menger       | PASS | 100.0 | 0.50 | 0.00 | – |
| m7_surround_connection__menger        | PASS | 100.0 | 0.33 | 0.17 | – |
| m8_outnumber2_inf2_threshold__menger  | PASS |  57.7 | 0.70 | 0.20 | – |

## Patterns

1. **Menger in-family family is unreachable from a cold start.** All 5
   m1–m5 seeds drop with identical numerics (length ≈ 39.7, P1 greedy
   86 %). The capture rule barely matters — the binding constraint is
   that PPO can't make P2 disrupt P1's influence accumulation in 3000
   episodes on a 400-cell 3D substrate. R18's stable menger top
   `0f5e931fa3e1` (which IS this combo) was reached from a different
   seed via mutation/crossover at 5000+ ep, not from a cold seed.

2. **Influence radius matters on carpet.** r=2 in-family (c1–c5) all
   pass; r=3 (c8) drops on seat bias. The R18 carpet champion family
   was r=2 — c1 is a direct seed of it.

3. **R8 Connection Go (g1) reproduces its R18 drop.** Same pattern as
   R18: `c1_custodian_connection__grid` dropped because P1 rushes a
   straight 16-row connection. The fractal substrates rescue connection
   by forcing routing; the symmetric grid doesn't.

4. **Hybrid validator (g3) drops on smoke** — doubled action space lets
   P1 reach the connection win before P2 can react. D1 was already
   verified by `verify_d1.py` (`hybrid_action_penalty=0.2` fires
   correctly on the same game). The validator is therefore not needed
   to confirm D1 end-to-end; we have a separate verification path.

## Implications for SUBSTRATE_CONFIG

If we follow the R18 precedent of "drop smoke-DROP seeds before
launch", SUBSTRATE_CONFIG would shrink to:

- **menger**: m6, m7, m8  (loses entire in-family — see "Open
  decisions" in the surface-for-review notes)
- **carpet**: c1, c2, c3, c4, c5, c7  (loses 2 probes; in-family intact)
- **grid_control**: g2 only  (loses R8 reference and hybrid validator)

This is a **non-trivial reduction in menger seed coverage** — the R19
plan's primary research goal #2 ("Does menger lift above R17 GE
rank-1?") loses its strongest seeded prior. See the surfaced findings
for the open decisions before R19 launches.
