# Fractal Topology Spike — Findings

Status: **probe complete, awaiting human eval (4 teams)**.
Last updated: 2026-04-25.

## Hypothesis

The threshold-win + signed-influence + target-aligned scoring family hit a 4–5/10 ceiling across R13–R16 (memory: `aigame project state`). The phase-spike experiment closed 2026-04-25 with a structural negative: any "extra stone parameter" not coupled to scoring is opportunity-cost-negative under that scoring. The only remaining axis for adding strategic depth without changing the rules is to change the **substrate**.

A Sierpiński-carpet substrate (level-2 carpet on 9×9 → 64 active cells, 17 holes) introduces emergent geography:
- Choke points and district walls
- Variable per-cell connectivity (cells next to holes have degree 2–3 instead of 4)
- Influence shadows around holes (no propagation through holes)
- Self-similar motifs at multiple scales
- Forced path routing for connection-win games

If the hypothesis holds, the same rule set should play measurably differently on the fractal vs. a matched rectangular control.

## What was built

| Component | Path |
|---|---|
| Topology type `"sierpinski"` | `game_engine/topology.py` (TOPOLOGY_TYPES, helper `_sierpinski_carpet_holes`, `_build_sierpinski_neighbors`, BFS distance matrix, override of `cells_within_radius`) |
| Engine readiness (active-cell awareness, custodian-as-wall) | `game_engine/engine_v2.py` (5 surgical edits: lines 328, 643, 703, 782, 508/518); `game_engine/topology.py` (active_cells / active_mask / num_active_cells defaults); `game_engine/game_def_v2.py` (`decode_action` raises on hole) |
| Mutation gate | `evolution/operators_v2.py` — `EXPERIMENTAL_TOPOLOGIES` set; `_mutate_topology_type` skips it; `_mutate_topology` skips when game is already on it |
| Unit + integration tests | `experiments/fractal_spike/test_sierpinski_topology.py` — 26 tests, all passing |
| Hand-crafted candidate games | `experiments/fractal_spike/build_games.py` → `candidates/frac_{A,B,C}_{fractal,control}.json` |
| Greedy probe | `experiments/fractal_spike/probe.py` |
| Visualization | `experiments/fractal_spike/visualize.py` (ASCII carpet + replay PNG with influence heatmap) |
| Eval prompt | `experiments/fractal_spike/v2-evaluation-prompt-fractal.txt` |

Regressions: `test_ca_integration.py` (11 passed) and `test_simultaneous_integration.py` (all passing) unchanged after engine edits.

## Probe results (greedy-vs-greedy, 200 games per candidate)

See `probe_results.json` and `probe_results.md` for full numbers. Highlights:

| Pair | Topology | P0 winrate | Mean length | Decisive |
|---|---|---|---|---|
| A | torus (control) | 0.98 | 21.0 | 0.99 |
| A | sierpinski (fractal) | 0.94 | 22.9 | 1.00 |
| B | torus (control) | 1.00 | 21.0 | 1.00 |
| B | sierpinski (fractal) | 0.92 | 21.2 | 1.00 |
| C | grid (control) | 0.49 | 52.6 | 1.00 |
| C | sierpinski (fractal) | 0.47 | 50.7 | 1.00 |

**Reading**:
- Pairs A and B both show severe P0 dominance — this is the **known R16 threshold-parity bug** (memory: thresholds tend to land where P1 crosses first by tempo). Greedy play makes the bias deterministic. Note: this affects threshold games on every topology, so the fractal is not creating new bias.
- **Pair B has the largest substrate-induced shift**: P0 winrate drops from 1.00 to 0.92 (Δ −0.08) when moved to the fractal. Custodian capture's hole-as-wall semantics break the threshold-tempo determinism — captures fire less reliably when a walk hits a hole. **This is a real substrate effect.**
- Pair A shows a smaller but consistent shift (P0: 0.98 → 0.94, Δ −0.04); the fractal adds 1.9 turns of length. The detour around the central hole gives P2 marginal tempo room.
- Pair C is essentially balanced on both substrates under greedy. Mean length ~52 turns. Greedy doesn't differentiate connection-win on this resolution; humans likely will.

## Visualization observations

`replay_frac_B_fractal.png` vs. `replay_frac_B_control.png` (24-move greedy replays):

- **Control (torus 8×8)**: P1 builds a tight 3×4 cluster in the bottom rows; P2 mirrors at the top. Torus wrap visible — P2 influence appears at the bottom-right corner.
- **Fractal (sierpinski 9×9)**: P1's cluster gets pinned against the (1,7) and (4,7) holes. Stones can't expand into a clean rectangle; they thread between holes. P2 in the top-right is bounded by (4,1) and (7,1). The central 3×3 hole is a permanent influence wall.

The substrate is doing what we predicted: forcing strategic geography under identical rules.

## What the human eval needs to determine

The probe's greedy signal can't distinguish "fractal makes the game subtly different" from "fractal makes the game genuinely deeper." That's what 4 human teams across the three pairs are for. The eval prompt explicitly asks teams to:
1. Play matched fractal + control sessions for their assigned pair.
2. Score each candidate independently.
3. Record a delta and an explicit "did the substrate add strategic depth?" verdict with concrete Phase-2 evidence.

Eval prompt: `experiments/fractal_spike/v2-evaluation-prompt-fractal.txt`.

## Decision table (filled in 2026-04-25 after 15-team eval)

Per-pair, aggregated across 5 teams (n=5 per pair). Δ = fractal − control. Substrate-novelty is fractal-only (control = 0 by definition).

| Pair | Mean Fractal Overall | Mean Control Overall | Δ Overall | Δ Strategic Depth | Δ Balance | Δ Novelty (post-critic) | Substrate-novelty (frac-only) | σ Overall (fractal scores) | σ of Δ across teams |
|---|---|---|---|---|---|---|---|---|---|
| A — R16-clone (outnumber+influence+threshold) | 5.00 | 5.00 | **0.00** | −0.20 | −0.20 | +0.20 | 4.20 | 0.63 | 1.10 |
| B — R14-clone (custodian+influence+threshold) | 4.00 | 4.00 | **0.00** | +0.20 | +0.20 | +0.60 | 3.60 | 0.63 | 0.00 |
| C — hand-crafted (surround+connection)         | 5.20 | 4.60 | **+0.60** | +0.60 | −0.20 | +1.40 | 5.60 | 0.98 | 0.49 |

**Best pair: C.** Mean Δ Overall = +0.60 (≥ +0.5 threshold). Strongest substrate-novelty (5.60). Strongest novelty lift (+1.40). Slight balance regression (−0.20) noted as a caveat.

**Verdict per decision rule: INTEGRATE.** Add `"sierpinski"` to R17 generator, gated to connection-family rulesets. Full reasoning, qualitative themes, and R17 follow-ups in `synthesis.md`.

**Decision rule** (from spike plan):
- **Best fractal Δ Overall ≥ +0.5** → integrate `"sierpinski"` to R17 generator.   ← **MET (Pair C, +0.60)**
- **Best fractal Δ Overall in [−0.3, +0.5]** → ambiguous; if σ > 1.0, second-probe; else drop.
- **Best fractal Δ Overall ≤ −0.3** → drop. Ship R17 along established line.

## Cleanup notes for R17 integration (if positive)

- Add `"sierpinski"` to `config.GameConfig.topology_types` default (or behind a flag).
- Add quick-rejects in `generator_v2.py:430-550` analogous to existing topology-rule incompatibility filters. Top candidate: verify which capture/win combinations are not pathological on the punctured 9×9.
- Convert remaining `range(self.total_cells)` loops in `engine_v2.py` (cascade at 610, connection-set comprehension at 815, threshold sum at 838, observation at 920) to use `self.topo.active_cells`. They are currently hole-safe by accident; making the safety explicit reduces future-bug surface.
- Decide whether to expose `axis_size > 9` (level-3 carpet on 27×27 — 729 cells, expensive but more terrain) or keep level-2 as the canonical baseline.

## Cleanup notes if dropped

- Topology code stays in place (zero ongoing cost: `"sierpinski"` is gated out of default config and excluded from mutation). Re-enable later by adding it to `config.topology_types` and removing from `EXPERIMENTAL_TOPOLOGIES`.
- Test file `experiments/fractal_spike/test_sierpinski_topology.py` continues to verify the topology functions as documented; useful as a guard against future engine refactors that might silently break sparse-topology support.
