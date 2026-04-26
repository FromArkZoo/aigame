# Pattern-vs-Random Probe

**Question.** The 2026-04-26 fractal-spike concluded the Sierpiński carpet adds genuine strategic depth on Pair-C-like rule families (alt + surround + connection): mean Δ Overall +0.60 vs grid, σ 0.49 across 5 teams. R17 will integrate Sierpiński on that basis.

But two hypotheses remain entangled in that result:
- **H1 (self-similarity load-bearing)** — the recursive hole structure creates the strategic depth.
- **H2 (any 17 holes do)** — hole *count* matters; hole *arrangement* is decorative.

This probe differentiates them.

## Design

**Within-team 4-condition comparison**, all using the locked Pair-C ruleset (alt + surround + connection), all with 64 active cells:

| Condition         | Substrate                                  | Holes |
|-------------------|--------------------------------------------|-------|
| `pat_grid`        | pure 8×8 grid (shared control)             | 0     |
| `pat_fractal`     | Sierpiński level-2 carpet 9×9              | 17    |
| `pat_random`      | random 17 holes 9×9 (locked seed 20260426) | 17    |
| `pat_structured`  | stride-2 lattice + centre 9×9              | 17    |

All three 9×9 hole-conditions are validated face-connected (all four faces reachable from a single component, so connection-win is feasible).

See `substrates.png` for the visual side-by-side.

**Eval protocol.** 7 teams, each plays all 4 games in a randomised order, fresh Claude session per team. Each team produces 4 condition scores + 3 within-team Δs (each condition − grid).

**Sample size rationale.** The fractal spike used 5 teams per pair and Pair A came back with σ_Δ = 1.10, borderline at n=5. Within-team paired comparison reduces team-personality noise, but n=7 gives more headroom than the original n=5 between-team design.

## Decision rule

| Outcome                                    | R17 implication                                                              |
|--------------------------------------------|------------------------------------------------------------------------------|
| `fractal ≫ random ≈ structured`            | Self-similarity load-bearing → keep Sierpiński generator path as scoped     |
| `fractal ≈ structured ≫ random`            | "Any structure helps" → swap to cheaper structured-hole operator             |
| `fractal ≈ random ≈ structured ≫ grid`     | Hole count alone matters → use generic random-hole-perturbation operator     |
| `all ≈ grid`                               | Re-examine fractal-spike conclusion before R17                                |

## Files

```
hole_patterns.py              hole-set generators + face-connectivity guard
build_games.py                builds the four candidate JSONs from hole_patterns
validate.py                   loads each game, plays a random self-play, sanity checks
visualize.py                  renders substrates.png (4-panel side-by-side)
v2-evaluation-prompt-pattern.txt   the team eval prompt
candidates/                   pat_{grid,fractal,random,structured}.json
evaluations/                  team-N.md goes here as teams report verdicts
substrates.png                visual reference for the four substrates
```

## Engine changes that landed for this probe

- `topology.py`: factored `_build_sierpinski_neighbors` into a generic `_build_holes_neighbors(holes_set)`; added a `"holes"` topology type that takes an explicit hole-set. `EXPERIMENTAL_TOPOLOGIES` now includes `"holes"` so evolution can't mutate into it.
- `game_def_v2.py`: added optional `holes: list[int] | None` field, round-trips through `to_dict`/`from_dict`, plumbed into the `TopologicalSpace` constructor.
- `engine_v2.py`: custodian-capture gate extended to accept `"holes"` topology.

All 26 existing sierpinski tests still pass after the refactor.

## Reproducing

```bash
.venv/bin/python experiments/pattern_vs_random/build_games.py
.venv/bin/python experiments/pattern_vs_random/validate.py
.venv/bin/python experiments/pattern_vs_random/visualize.py
```
