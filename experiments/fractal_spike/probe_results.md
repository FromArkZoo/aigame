# Fractal-spike probe results

Greedy-vs-greedy probe for each candidate. Greedy picks the placement with highest (friendly_neighbors − enemy_neighbors); ties broken randomly. Lopsided P0 winrate indicates seat bias in the rules+topology combination.

| Candidate | Topology | P0 win | P1 win | Draw | Mean len | Decisive | P0 pieces | P1 pieces |
|---|---|---|---|---|---|---|---|---|
| frac_A_control | torus | 0.98 | 0.01 | 0.00 | 21.0 | 1.00 | 11.0 | 10.0 |
| frac_A_fractal | sierpinski | 0.94 | 0.06 | 0.00 | 22.9 | 1.00 | 11.9 | 11.0 |
| frac_B_control | torus | 1.00 | 0.00 | 0.00 | 21.0 | 1.00 | 11.0 | 10.0 |
| frac_B_fractal | sierpinski | 0.92 | 0.08 | 0.00 | 21.2 | 1.00 | 11.1 | 10.2 |
| frac_C_control | grid | 0.49 | 0.51 | 0.00 | 52.6 | 1.00 | 25.2 | 26.0 |
| frac_C_fractal | sierpinski | 0.47 | 0.53 | 0.00 | 50.7 | 1.00 | 24.5 | 25.1 |

## Per-pair delta (fractal − control)

### Pair A
- P0 winrate: control 0.98 / fractal 0.94 (Δ -0.05)
- Decisive rate: control 1.00 / fractal 1.00 (Δ +0.00)
- Mean length: control 21.0 / fractal 22.9

### Pair B
- P0 winrate: control 1.00 / fractal 0.92 (Δ -0.08)
- Decisive rate: control 1.00 / fractal 1.00 (Δ +0.00)
- Mean length: control 21.0 / fractal 21.2

### Pair C
- P0 winrate: control 0.49 / fractal 0.47 (Δ -0.03)
- Decisive rate: control 1.00 / fractal 1.00 (Δ +0.00)
- Mean length: control 52.6 / fractal 50.7
