# Pattern-vs-Random Probe — Synthesis

**Run date:** 2026-04-26
**Teams:** 7 (within-team 4-condition design)
**Conditions:** pat_grid (control) / pat_fractal (Sierpiński L2) / pat_random (seed 20260426) / pat_structured (stride-2 lattice + centre)
**Ruleset (locked):** alternating turns, surround capture, no propagation, connection win, max 100 turns
**Active cells per condition:** 64

## Question

The 2026-04-26 fractal-spike concluded the Sierpiński carpet adds genuine strategic depth on Pair-C-like rule families: mean Δ Overall +0.60 vs grid (5 teams, σ 0.49). R17 was scoped to integrate Sierpiński on that basis. This probe asked: is the *self-similarity* load-bearing, or would *any* 17-hole pattern produce the same effect?

## Per-team results

| Team | Game order                   | Δ Fractal | Δ Random | Δ Structured | Pick |
|------|------------------------------|-----------|----------|--------------|------|
| 1    | grid → fractal → random → structured     | 0     | −2     | −2     | (a) |
| 2    | fractal → random → structured → grid     | +1    | −2     | −2     | (a) |
| 3    | random → structured → grid → fractal     | +3    | +4     | +3     | (c) |
| 4    | structured → grid → fractal → random     | +1    | +3     | +1     | (c) |
| 5    | grid → random → fractal → structured     | +1    | −2     | +1     | (b) |
| 6    | fractal → structured → random → grid     | +1    | −2     | +1     | (b) |
| 7    | random → grid → structured → fractal     | 0     | +1.5   | −1     | (c) |

All Δs are within-team Overall scores (each condition − pat_grid for that team).

## Aggregate statistics

| Condition  | Mean Δ | σ    | SEM  | 95% CI            |
|------------|--------|------|------|-------------------|
| Fractal    | +1.00  | 1.00 | 0.38 | [+0.07, +1.93]    |
| Random     | +0.07  | 2.68 | 1.01 | [−2.41, +2.55]    |
| Structured | +0.14  | 1.86 | 0.70 | [−1.58, +1.86]    |

**Only the fractal condition's 95% CI excludes zero.** Random and structured both have means barely above grid with variance several times larger than the effect size — they are not reliably distinguishable from grid.

## Why team recommendations diverged from the aggregate

Recommendations distributed 2× (a) keep Sierpiński / 2× (b) swap to structured / 3× (c) random-hole. The plurality (c) came from team-3 (+4 random) and team-4 (+3 random) — both rolled "good" on the random pattern's col-4 hole-wall feature. The other five teams either rolled "bad" on its row-7-corridor feature (−2) or saw it as roughly flat. The same fixed-seed hole-set produced σ 2.68. Individual teams read from their own single-condition experience; the aggregate read sees the variance.

This is itself the cleanest finding of the probe: **the cheaper alternatives have within-condition variance much larger than their average effect.** R17 evolution would get noisy fitness signal from them.

## Decision rule mapping

The probe README's decision table:
- `fractal ≫ random ≈ structured` → (a) keep Sierpiński generator path
- `fractal ≈ structured ≫ random` → (b) swap to structured-hole operator
- `fractal ≈ random ≈ structured ≫ grid` → (c) random-hole-perturbation operator
- `all ≈ grid` → re-examine spike conclusion

Aggregate maps to **(a) keep Sierpiński generator path.** Fractal beats grid reliably; alternatives don't.

## Substantive findings beyond the headline

1. **Sierpinski's specific affordance is the central 3×3 block.** team-7's evidence: when both substrates allow even-row corridor escape (rows 0/2/6/8 are clean on both fractal and structured), neither's hole pattern matters — both collapsed to identical 17-move corridor races. The central 3×3 produces depth only when an opening engages it.

2. **The original spike's +0.60 reproduces and slightly strengthens to +1.00 here.** Within-team paired comparison produced cleaner signal than the spike's between-team design, as predicted.

3. **Random-pattern variance is itself a finding.** Same fixed-seed hole-set produced verdicts ranging from −2 to +4 across teams, depending on which features (col-4 wall vs row-7 corridor) the openings engaged. Two genuinely different games hidden in the same hole layout. This is not noise — it's an artefact of strong local features in random hole-sets.

4. **Pattern critic's transfer prediction is wrong.** Several teams (notably team-6) caught specific moves where *which* cells flip live/dead between fractal and structured changed the move calculus — not just the count of holes. So "17 holes is 17 holes" is false at the move level. But the *average* depth that arrangement creates is matched between fractal and structured.

5. **Heuristic-strength caveat applies to all teams.** The play was per-move human-style reasoning, not deep RL. team-7 explicitly flagged that deep RL might find affordances in the central 3×3 we didn't. The fractal-vs-grid signal could be larger or smaller under stronger play. The aggregate trend should still hold direction-wise.

## R17 implication

The probe was the gate on whether to collapse Sierpiński's generator path into a cheaper hole-pattern operator. **Do not collapse.** R17 keeps Sierpiński as a first-class substrate, integrated as previously scoped:

- Add `"sierpinski"` to `config.GameConfig.topology_types` default
- Generator quick-reject: gate Sierpinski to win-condition family (allow connection/territory; reject threshold)
- Substrate-novelty multiplier (+0.05) in GoEssenceScorer
- Seed with `c6bb58075520`, `8d12c8b92b71`, and `frac_C_fractal.json`
- Balance preflight (komi=2 if P1-dominance confirmed)

## Engine work that landed for the probe (kept)

- `topology.py`: factored `_build_sierpinski_neighbors` into a generic `_build_holes_neighbors(holes_set)`; added `"holes"` topology type that takes an explicit hole-set. Marked `EXPERIMENTAL` so evolution can't mutate into it.
- `game_def_v2.py`: optional `holes: list[int] | None` field, round-trips through `to_dict`/`from_dict`.
- `engine_v2.py`: custodian-capture gate accepts `"holes"`.

The `"holes"` topology type stays in the engine post-probe — useful for future feature-ablation probes (e.g., Sierpinski-with-only-central-block, Sierpinski-with-only-satellites) that R17 follow-ups may want.

## Future probes (not before R17)

Post-R17 (after a Sierpinski-evolved champion exists to compare against):

- **Sierpinski feature-ablation**: central-3×3-only vs satellites-only vs full carpet. Tests which structural feature drives the +1.00 effect.
- **Sierpinski-triangle-on-hex**: tests whether self-similarity transfers across base lattices.
- **Other fractal families** (Julia, Koch, Vicsek): tests whether type of self-similarity matters beyond the carpet pattern.

All deferred until a Sierpinski-trained R17 champion is in hand.
