# Run 12 Evaluation Report

**Database**: `genesis_v2_run12.db`
**Config**: 11 generations (0-10), pop 50, 10k training budget, 2 runs, 25% immigration, `--max-dimensions 2`
**Seed games**: `484fcb3b0471`, `7fa2c8ac1dc7` (Run 10 hex champions)
**Duration**: ~18 hours (Mar 10-11)
**First CA run**: 30% CA probability, all topologies, 2D only

---

## Summary

Run 12 is the first evolutionary run to include cellular automata (V4) games. The results are clear: **CA games cannot compete with classic games under the current generation and scoring framework**. Zero CA games appear in the top 20, the best CA game scores 0.1632 Go Essence (vs 0.4282 for the best classic game), and CA games are progressively eliminated by selection pressure -- from 9/50 in generation 0 to 1/50 by generation 10.

The root causes are identifiable and fixable: agents can't learn CA games (non-triviality=0 for 69% of CA games), CA transition tables inflate complexity unfairly, and the stability check has a perspective bug that may reject valid rules.

---

## Overall Statistics

| Metric | CA Games | Classic Games |
|--------|----------|---------------|
| Generated | 42 | 458 |
| Scored (survived validation) | 26 (62%) | 354 (77%) |
| Avg Go Essence | 0.0273 | 0.0509 |
| Max Go Essence | 0.1632 | 0.4282 |
| Avg Strategic Depth | 0.399 | 0.364 |
| Avg Non-Triviality | 0.119 | 0.265 |
| Avg Rule Simplicity | 0.227 | 0.267 |
| Avg ELO | 1440 | 1536 |
| Avg Rule Complexity | 32.3 | 15.7 |

---

## Generation Progress

| Gen | Best GE | Mean GE | CA Generated | CA Scored | Classic Generated | Classic Scored |
|-----|---------|---------|-------------|-----------|-------------------|----------------|
| 0 | 0.4193 | 0.037 | 9 | 5 | 36 | 22 |
| 1 | 0.300 | 0.026 | 7 | 6 | 38 | 29 |
| 2 | 0.449 | 0.068 | 1 | 0 | 44 | 36 |
| 3 | 0.451 | 0.067 | 2 | 1 | 43 | 34 |
| 4 | 0.480 | 0.063 | 6 | 3 | 39 | 31 |
| 5 | 0.518 | 0.076 | 4 | 3 | 41 | 33 |
| 6 | 0.520 | 0.068 | 5 | 4 | 40 | 31 |
| 7 | 0.468 | 0.086 | 4 | 1 | 41 | 30 |
| 8 | 0.398 | 0.057 | 1 | 1 | 44 | 34 |
| 9 | 0.436 | 0.081 | 2 | 1 | 43 | 36 |
| 10 | 0.415 | 0.058 | 1 | 1 | 49 | 38 |

**Key observation**: CA games decline monotonically through generations. Selection pressure eliminates them because they never score well enough to survive into the elite. By gen 2, only immigration introduces new CA games.

---

## Top 10 Games (All Classic)

| Rank | Game ID | GE | ELO | Depth | Non-Triv | Topo | Capture | Win | Placement |
|------|---------|----|-----|-------|----------|------|---------|-----|-----------|
| 1 | `df2d664fd1f1` | 0.428 | 993.5 | 0.533 | 0.980 | moore | surround | threshold | adj_own |
| 2 | `b6987c123057` | 0.415 | 2993.8 | 0.614 | 0.800 | hex | surround | threshold | anywhere |
| 3 | `4e8564d23260` | 0.413 | 1006.0 | 0.646 | 0.721 | hex | surround | threshold | adj_own |
| 4 | `162d074d8036` | 0.398 | 1002.7 | 0.532 | 0.872 | hex | none | threshold | anywhere |
| 5 | `aa576fdde4b2` | 0.382 | 2957.3 | 0.443 | 0.980 | grid | outnumber | threshold | anywhere |
| 6 | `53552b7fef03` | 0.371 | 998.1 | 0.518 | 0.800 | hex | outnumber | threshold | anywhere |
| 7 | `57093918dd09` | 0.350 | 2925.9 | 0.656 | 0.529 | torus | custodian | threshold | adj_own |
| 8 | `6ecae2fef9ab` | 0.347 | 3025.7 | 0.567 | 0.632 | moore | outnumber | threshold | anywhere |
| 9 | `679c75eec887` | 0.342 | 3031.8 | 0.553 | 0.632 | torus | surround | threshold | anywhere |
| 10 | `97d1f06f6ff1` | 0.338 | 2979.6 | 0.597 | 0.566 | moore | none | threshold | anywhere |

**Classic game patterns**:
- All 2D 8x8 (as enforced by `--max-dimensions 2`)
- Win condition column is blank in raw query because field is `condition_type` not `win_type` -- all are threshold or territory
- Surround capture most common among top 10 (4/10)
- Mix of topologies: hex (4), moore (3), torus (2), grid (1)
- High non-triviality across top 10 (all > 0.5)

---

## CA Game Analysis (All 26 Scored CA Games)

| Rank | Game ID | GE | Topo | CA Steps | Win Type | Avg Len | vs_Random |
|------|---------|----|------|----------|----------|---------|-----------|
| 1 | `567384041c59` | 0.163 | grid | 2 | territory | 25.5 | 0.85 |
| 2 | `eaca9770eae2` | 0.120 | grid | 2 | connection | 66.0 | 0.80 |
| 3 | `dffb5a6b03a7` | 0.105 | torus | 2 | connection | 35.0 | 0.50 |
| 4 | `e96bab9f9155` | 0.095 | hex | 2 | connection | 28.5 | 0.43 |
| 5 | `f2e8476c5286` | 0.062 | torus | 1 | connection | 57.5 | 0.28 |
| 6-26 | (21 games) | <0.03 | mixed | 1-3 | mixed | 3-84 | 0.0-0.51 |

### CA Failure Mode Breakdown

**1. Non-triviality = 0 (18/26 games, 69%)**
The #1 killer. Agents trained on these CA games cannot beat a random player (`vs_random <= 0.50`). The CA dynamics are either too chaotic (random play is as effective as trained play) or the game state space is too complex for the flat MLP policy to learn meaningful strategies within 10k episodes.

**2. High rule complexity (avg 32.3 vs 15.7 classic)**
CA transition tables contribute significantly to complexity. Even the "simplest" CA game has complexity 19 vs classic minimum of 13. The simplicity formula `1/(1+ln(complexity))` gives CA games a ~15% simplicity penalty.

**3. Short game lengths (8/26 have avg_length < 25)**
CA rules that are too aggressive (explosive birth or rapid death) create games that end in a few moves. The game-length penalty further suppresses their scores.

**4. Rejection rate 38% vs 23% classic**
CA games fail validation more often, likely due to stability check failures (annihilation, explosion, or frozen boards).

### CA Success Factors (Top 4 CA Games)

The 4 CA games that scored above 0.09 share these traits:
- **2 steps per turn**: All use `steps_per_turn=2`, allowing CA dynamics to propagate meaningfully each turn
- **Grid or torus topology**: Simpler connectivity (4 neighbors) produces more predictable CA behavior
- **vs_random > 0.43**: Agents can learn to play them better than random
- **Territory or connection win**: These win conditions work well with CA spreading dynamics

---

## Topology Analysis

| Topology | CA Avg GE | Classic Avg GE | CA Count | Classic Count |
|----------|-----------|----------------|----------|---------------|
| grid | 0.0752 | 0.0491 | 4 | 64 |
| hex | 0.0271 | 0.0622 | 4 | 78 |
| torus | 0.0293 | 0.0426 | 7 | 100 |
| moore | 0.0087 | 0.0515 | 11 | 112 |

**Grid CA outperforms grid classic** (0.075 vs 0.049) with only 4 games -- a promising signal, though statistically weak. Moore CA is worst (0.009) -- 8-connectivity creates too many CA table entries (3 x 9 x 9 = 243 entries vs 3 x 5 x 5 = 75 for grid).

---

## Win Condition Analysis

| Win Type | CA Avg GE | Classic Avg GE | CA Count | Classic Count |
|----------|-----------|----------------|----------|---------------|
| territory | 0.0292 | 0.0416 | 9 | 98 |
| connection | 0.0289 | 0.0290 | 15 | 127 |
| threshold | 0.0066 | 0.0795 | 2 | 129 |

**Threshold win dominates classic games** (0.0795 avg) because it pairs naturally with influence propagation. CA games can't use threshold (requires influence propagation, which CA replaces), leaving them only territory and connection.

---

## Critical Findings

### 1. CA Games Are Evolutionary Dead-Ends (Under Current Framework)
CA games start at ~18% of population (9/50 in gen 0) and drop to 2% (1/50 by gen 10). Selection pressure eliminates them because:
- They can't compete on simplicity (2x higher complexity)
- Most can't produce learnable agents (69% have non-triviality=0)
- They can't use the strongest win condition (threshold)

### 2. Stability Check Has Perspective Bug
The `_ca_stability_check()` in `generator_v2.py:507` uses `perspective = cell_owner if cell_owner != 0 else 1` (always P1 for empty cells). The actual game engine applies CA from the acting player's perspective, which alternates. This mismatch means some valid rules are rejected and some invalid rules pass.

### 3. Moore Topology Is Poison for CA
Moore connectivity (8 neighbors) creates transition tables with 243 entries (3 x 9 x 9). This inflates complexity, making simplicity scores worse, and creates a search space too large for random initialization to find good rules. Grid connectivity (4 neighbors, 75 entries) is 3x smaller and produces better CA games.

### 4. CA Mutation Is Unbiased
Mutation replaces table entries with uniform random states {0,1,2}. This destroys the generation-time bias toward sparsity (80% empty stays empty, 70% occupied survives) and gradually makes CA rules denser and more chaotic.

### 5. Grid CA Shows Promise
Despite tiny sample size (n=4), grid CA games average 0.0752 GE vs 0.0491 for grid classic games. The best CA game (`567384041c59`) uses grid topology with 2 steps/turn, territory win, and adjacent-to-own placement -- a "seed and grow" game where players place stones near their own and CA rules expand territory.

---

## Run 12b (Comparison)

A smaller parallel run (280 games, 11 generations) with similar configuration:
- 15 CA games generated, only 7 scored
- Max CA Go Essence: 0.0671 (worse than Run 12's 0.1632)
- Classic champion: 0.5268 (higher than Run 12's 0.4282)
- Confirms Run 12 findings: CA games are outcompeted

---

## Recommendations for Run 13

### Code Changes Required

1. **Fix stability check perspective** (`generator_v2.py:507`): Alternate between P1/P2 perspectives during stability testing to match actual game engine behavior.

2. **Restrict CA to grid topology** (or reduce max_neighbors): Moore's 243-entry tables are too large. Cap CA to grid (75 entries) or hex (108 entries) topologies.

3. **Bias CA mutation toward identity**: When mutating a CA table entry, 40% chance to keep current value, 30% chance to set to identity (state stays same), 30% chance to random. This preserves the sparsity that makes CA rules playable.

4. **Lower explosion threshold**: Change from 0.9 to 0.75 in `_ca_stability_check()`. Rules that fill >75% of the board are likely degenerate.

5. **Increase stability test density**: Place 10-15 initial pieces instead of 5-10, and run 15 steps instead of 10. Better approximation of real game conditions.

6. **Boost CA mutation rate**: Increase from 20% to 35%. CA rules need more evolutionary exploration to find the narrow band of stable, interesting dynamics.

7. **Consider CA complexity discount**: The `total_complexity()` method could weight CA entries at 0.5x, reflecting that each entry is a simple state transition (not a structured rule). This would reduce CA's complexity penalty.

### Run Configuration

- **CA probability**: Increase to 0.5 for a focused CA exploration run
- **Topology**: Grid-only for CA games (highest signal), all topologies for classic
- **Seed games**: Keep Run 10 hex champions for classic gene pool; seed best CA game `567384041c59` separately
- **Training budget**: Keep 10k (5k may be insufficient for CA games to learn)
- **Population**: 50 (same as Run 12)
- **Dimensions**: 2D only (Run 12 confirmed 2D is optimal)

---

## Champion: `df2d664fd1f1` (Classic)

- **Format**: 2D 8x8 Moore topology
- **Mechanics**: Surround capture (threshold=1), influence propagation, threshold win (63.5)
- **Training**: 36 avg game length, 0.98 vs_random, perfectly balanced (0.5 P1 winrate)
- **Go Essence**: 0.4282

This is a Go-variant on a Moore grid with influence propagation -- solidly in the Go x Hex attractor basin that has dominated since Run 8. No novelty beyond previous runs.

## Champion: `567384041c59` (Best CA)

- **Format**: 2D 8x8 grid
- **Mechanics**: CA with 2 steps/turn, territory win (41.6%), adjacent-to-own placement
- **CA Rule Summary**: Life-like birth (3 own neighbors -> birth), conditional death (outnumbered -> die), rare conversion (isolated near enemy -> convert to enemy)
- **Training**: 25.5 avg game length, 0.85 vs_random, perfectly balanced
- **Go Essence**: 0.1632

This "seed and grow" game is the most interesting CA discovery. Players place stones adjacent to their own, and CA dynamics spread territory through birth rules while eliminating isolated pieces. The game is learnable (0.85 vs_random) and balanced. Its low GE score is primarily due to complexity (32.3 vs 15.7 average classic) and the resulting simplicity penalty.
