# R18 B2 Phase 2 — PPO smoke results on the 15 seed games

Run 2026-04-28. 3000-ep PPO per seed, 100 eval episodes, sampled-eval gate.

## Aggregate

**9 pass, 6 drop.** All drops are seat-bias ("forced-win"), none are
length-floor. PPO trained on every seed without crashing; the new
substrates (vicsek, triangle, menger) show no engine bugs under load.

| Combo | Pass rate | Notes |
|-------|-----------|-------|
| c1 custodian + connection         | 4/5 | grid drops (P1 100% greedy) |
| c2 outnumber-2 + threshold-race   | 1/5 | only grid passes; threshold-race amplifies P1 tempo on every fractal substrate (R17 finding reproduces) |
| c3 surround + territory           | 4/5 | carpet drops (P2 98% greedy) |

| Substrate | Pass rate | Surviving combos |
|-----------|-----------|------------------|
| vicsek               | 2/3 | c1, c3 |
| sierpinski_triangle  | 2/3 | c1, c3 |
| sierpinski (carpet)  | 1/3 | c1 only |
| 2D grid (control)    | 2/3 | c2, c3 |
| menger               | 2/3 | c1, c3 |

## Full table

| seed | status | sampled_avg_len | greedy_p1_wr | seat_bias |
|------|--------|----------------:|-------------:|----------:|
| c1_custodian_connection__vicsek    | PASS |  99.4 | 0.50 | 0.00 |
| c1_custodian_connection__triangle  | PASS | 100.0 | 0.50 | 0.00 |
| c1_custodian_connection__carpet    | PASS |  17.7 | 0.46 | 0.04 |
| c1_custodian_connection__grid      | DROP | 100.0 | 1.00 | 0.50 |
| c1_custodian_connection__menger    | PASS | 100.0 | 0.33 | 0.17 |
| c2_outnumber_threshold__vicsek     | DROP |  36.5 | 1.00 | 0.50 |
| c2_outnumber_threshold__triangle   | DROP |  38.8 | 1.00 | 0.50 |
| c2_outnumber_threshold__carpet     | DROP |  36.9 | 0.86 | 0.36 |
| c2_outnumber_threshold__grid       | PASS |  38.6 | 0.62 | 0.12 |
| c2_outnumber_threshold__menger     | DROP |  40.2 | 0.86 | 0.36 |
| c3_surround_territory__vicsek      | PASS |  27.6 | 0.67 | 0.17 |
| c3_surround_territory__triangle    | PASS | 100.0 | 0.50 | 0.00 |
| c3_surround_territory__carpet      | DROP |  16.3 | 0.02 | 0.48 |
| c3_surround_territory__grid        | PASS | 100.0 | 0.50 | 0.00 |
| c3_surround_territory__menger      | PASS | 100.0 | 0.50 | 0.00 |

## Patterns

1. **Threshold-race is broken on every fractal substrate.** Same root
   cause R17 saw with frac_C_fractal: influence-based threshold races
   amplify P1 tempo, and irregular topology doesn't help P2 disrupt
   the accumulating gradient. Only the symmetric grid is balanced
   enough for c2 to be playable.

2. **c1+grid fails** because connection on a 16×16 grid lets P1 rush
   a straight connecting line before P2 can block. The fractal holes
   that disqualify the threshold-race actually rescue connection by
   forcing routing.

3. **c3+carpet fails in the OPPOSITE direction** — P2 wins 98% under
   greedy. The carpet's 17 holes create asymmetric surround
   opportunities that favor whoever responds rather than initiates.
   Not seen on the larger 243-cell triangle, suggesting board size
   matters here.

## Implications for R18

Every substrate has at least one valid combo. The reduced seed set
per substrate:

- **vicsek, triangle, menger:** c1 + c3 (2 seeds each)
- **grid:** c2 + c3 (2 seeds each)
- **carpet:** c1 only (1 seed)

R18 evolution proceeds from these reduced seed sets. Mutation +
crossover within each per-substrate evolution will explore neighboring
rule-space; we don't need broad initial coverage to get a useful
dim→fitness curve.

**No replacement seeds generated.** The drops are real structural
biases, not measurement noise — relaxing the gate or hand-crafting
"adjusted" versions would either bias the comparator (forcing
P1-favored games into the pool) or change the rule combo enough that
cross-substrate comparison loses meaning.

**Open question for next session:** does the carpet-only-has-c1
asymmetry need addressing? Options: (a) accept and let evolution
explore, (b) add a 4th rule combo specifically for carpet, (c) run
carpet's evolution with `audit_soft_rules=True` so threshold-race can
be tried despite the demote rule. Decision deferred.
