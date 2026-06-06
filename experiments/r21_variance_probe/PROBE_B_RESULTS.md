# Probe B — GE variance decomposition

```

========================================================================
MENGER  —  180 reruns across 9 games
========================================================================

[1] Component spread across all reruns (low CV = stable, high = noisy):
    component                  min     max    mean      sd      CV
    strategic_depth          0.444   0.820   0.669   0.077    0.12
    non_triviality           0.000   1.000   0.645   0.284    0.44
    strategic_diversity      0.000   1.000   0.544   0.308    0.57
    rule_simplicity          0.254   0.254   0.254   0.000    0.00

[2] strategic_diversity distinct values: [0.0, 0.333, 0.667, 1.0]
    counts: 0.0:21, 0.333:59, 0.667:65, 1.0:35

[3] reruns with go_essence < 0.01: 9 / 180
    of those: depth range 0.558-0.760 (mean 0.661)  → PPO learning signal HEALTHY
    non_triviality == 0 in 8/9;  diversity == 0 in 2/9

[4] within-game GE variance decomposition (single-predictor R^2 of GE swings):
    strategic_depth        R^2 =  0.024   (corr +0.154)
    non_triviality         R^2 =  0.450   (corr +0.671)
    strategic_diversity    R^2 =  0.136   (corr +0.369)
    rule_simplicity        R^2 =  0.000   (corr +nan)
    total within-game GE variance = 0.00645

[5] survivorship demo on top menger game e1453dac5445:
    full 20-rerun mean         = 0.1775
    after dropping 1 non_triviality==0 reruns = 0.1868   (Δ +0.0093; mean moves UP = upward bias)

========================================================================
CARPET  —  100 reruns across 5 games
========================================================================

[1] Component spread across all reruns (low CV = stable, high = noisy):
    component                  min     max    mean      sd      CV
    strategic_depth          0.074   0.864   0.525   0.174    0.33
    non_triviality           0.000   1.000   0.337   0.321    0.95
    strategic_diversity      0.000   1.000   0.720   0.270    0.37
    rule_simplicity          0.254   0.254   0.254   0.000    0.00

[2] strategic_diversity distinct values: [0.0, 0.333, 0.667, 1.0]
    counts: 0.0:6, 0.333:8, 0.667:50, 1.0:36

[3] reruns with go_essence < 0.01: 39 / 100
    of those: depth range 0.074-0.564 (mean 0.377)  → PPO learning signal COLLAPSED
    non_triviality == 0 in 35/39;  diversity == 0 in 3/39

[4] within-game GE variance decomposition (single-predictor R^2 of GE swings):
    strategic_depth        R^2 =  0.265   (corr +0.515)
    non_triviality         R^2 =  0.552   (corr +0.743)
    strategic_diversity    R^2 =  0.004   (corr +0.067)
    rule_simplicity        R^2 =  0.000   (corr +nan)
    total within-game GE variance = 0.00389

[5] survivorship demo on top carpet game d995cf010504:
    full 20-rerun mean         = 0.1031
    after dropping 1 non_triviality==0 reruns = 0.1085   (Δ +0.0054; mean moves UP = upward bias)

========================================================================
GRID  —  100 reruns across 5 games
========================================================================

[1] Component spread across all reruns (low CV = stable, high = noisy):
    component                  min     max    mean      sd      CV
    strategic_depth          0.074   0.781   0.407   0.216    0.53
    non_triviality           0.000   1.000   0.266   0.350    1.32
    strategic_diversity      0.000   1.000   0.487   0.331    0.68
    rule_simplicity          0.257   0.265   0.260   0.004    0.02

[2] strategic_diversity distinct values: [0.0, 0.333, 0.667, 1.0]
    counts: 0.0:26, 0.333:13, 0.667:50, 1.0:11

[3] reruns with go_essence < 0.01: 59 / 100
    of those: depth range 0.074-0.552 (mean 0.271)  → PPO learning signal COLLAPSED
    non_triviality == 0 in 58/59;  diversity == 0 in 23/59

[4] within-game GE variance decomposition (single-predictor R^2 of GE swings):
    strategic_depth        R^2 =  0.008   (corr +0.090)
    non_triviality         R^2 =  0.236   (corr +0.485)
    strategic_diversity    R^2 =  0.082   (corr +0.287)
    rule_simplicity        R^2 =  0.000   (corr +nan)
    total within-game GE variance = 0.00127

[5] survivorship demo on top grid game b12ff78f1c1d:
    full 20-rerun mean         = 0.0985
    after dropping 0 non_triviality==0 reruns = 0.0985   (Δ +0.0000; mean moves UP = upward bias)

========================================================================
FORMULA SANITY (reconstructed vs stored go_essence)
========================================================================
    n=380  corr(reconstructed, stored) = 0.837  mean|Δ| = 0.116
    (high corr + nonzero |Δ| = formula is structurally right; stored GE is the
     C2 average of per-internal-seed GE, so it differs from GE(avg components).)
```
