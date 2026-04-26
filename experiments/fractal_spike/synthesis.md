# Fractal Topology Spike — Synthesis (15-team verdict aggregation)

**Date:** 2026-04-25
**Aggregator:** team-lead (over 15 evaluator verdicts in `evaluations/`)
**Verdict:** **INTEGRATE** `"sierpinski"` into R17 generator, **gated to connection-family rule sets**. Pair C clears the +0.5 Δ-Overall threshold; Pairs A and B do not.

---

## Per-pair aggregate scores

5 teams per pair. Δ = fractal − control. All scores 1–10. Substrate-novelty is fractal-only (control scored 0 by protocol).

| Pair | Source | Frac Overall | Ctrl Overall | Δ Overall | Δ SD | Δ Bal | Δ Nov | Sub-Nov | σ(frac Overall) | σ(Δ Overall) |
|---|---|---|---|---|---|---|---|---|---|---|
| A | R16 winner clone (outnumber + influence + threshold) | 5.00 | 5.00 | **0.00** | −0.20 | −0.20 | +0.20 | 4.20 | 0.63 | 1.10 |
| B | R14 winner clone (custodian + influence + threshold) | 4.00 | 4.00 | **0.00** | +0.20 | +0.20 | +0.60 | 3.60 | 0.63 | 0.00 |
| C | hand-crafted (surround + connection)                | 5.20 | 4.60 | **+0.60** | +0.60 | −0.20 | +1.40 | 5.60 | 0.98 | 0.49 |

Pair C is the winner on every axis except balance (which it slightly worsens) and is the only pair where the substrate clears the integration threshold.

---

## Qualitative themes

### Theme 1: "The substrate is real, but threshold-race rules don't exercise it." (Pairs A & B)

Every Pair A and Pair B team independently arrived at the same conclusion: the carpet **does** create new tactical primitives — fortress cells (degree-2 corners that cannot be outnumber-captured), hole-shadow defensive corridors, walk-killers (custodian walks aborted at hole boundaries), forced four-anchor opening theory, and ~14 % lower per-stone influence efficiency. **None of these primitives fire under threshold-race play**, because both players race symmetric corner clusters to a fixed influence sum and never make capture contact. Quotes:

- team-1 (Pair A): "The substrate adds a tactical filter (avoid degree-2 traps) and a small positional bonus. It does not introduce a new strategic concept."
- team-9 (Pair B): "Same game, same outcome, same margin, same ply count, same dominant strategy."
- team-10 (Pair B): "Substrate effect is real but **inert** under threshold-race play."

The shared structural observation across all 10 A+B teams: the rule families they evaluated **don't reward path-routing or boundary play**, which is precisely what the carpet's geometry adds. Threshold + influence + radius-1 is the wrong rule family for this substrate.

### Theme 2: "Pair C's connection win **forces** the substrate to matter." (Pair C)

Connection wins make graph distance and graph cuts strategically central, which is what the holes attack. Specific phenomena observed only on the fractal in Pair C games:

- **Wall-strategy elimination** (team-11): "On control I won via column-7 bridge wall. On fractal that strategy structurally cannot succeed — (7,1)/(7,4)/(7,7) are holes and the chain cannot be contiguous. I had to abandon the strategy entirely." The substrate doesn't tax the strategy; it forbids it.
- **Hole-shadow capture** (team-11, team-15): single stones adjacent to holes have only 2 liberties and can be captured by a single attacker — a tactical primitive that **does not exist** on the grid.
- **Two-bridge degradation** (team-15): the classical Hex two-bridge connection collapses to a single-cell connection when one bridge cell is a hole; ~4 such failure points around (4,2)/(2,4)/(6,4)/(4,6).
- **Anchor competition** (teams 11, 13, 14, 15): only 4 cells are degree-4 — both players forced to contend for the same 4 anchors, eliminating the translation-invariant opening of the grid.
- **Forced corridor commitment** (team-12, team-13): central 3×3 hole forces an early left-or-right routing decision; column choice for top↔bottom traversal collapses from 8 candidates to 4 clean candidates.

Pair C teams uniformly scored substrate-novelty 4–7 (mean 5.6 vs Pair A's 4.2 and Pair B's 3.6). Two teams (11, 14) gave a clear "INTEGRATE" recommendation; two (13, 15) gave SECOND-PROBE; one (12) gave DROP. The aggregate Δ Overall +0.60 is consistent across teams (σ = 0.49) and not driven by a single outlier.

### Theme 3: Confounds and caveats teams flagged

- **Width confound (Pairs A & B):** the fractal is 9-wide vs the torus's 8-wide. Multiple teams flagged that "harder threshold on a slightly bigger board" partially explains the longer fractal games. Threshold rescaling against mean cell degree would close most of this gap. Not a fatal confound for Pair C (connection has no threshold).
- **Wraparound recovery (Pair B):** torus wrap-around aids the trailing player; the fractal removes this recovery channel. This is a real substrate effect but mostly invisible at radius-1 propagation.
- **P1 advantage on fractal-Pair-C:** team-11 and team-13 noted the fractal's reduced corridor count amplifies the first-mover edge for connection wins. Δ Balance −0.20 is small but worth a probe before R17 deployment.
- **Latent vs realized novelty (team-12):** corner-by-hole-adjacency captures and detour amplification are real but did not fire in this team's games. The aggregate is buoyed by teams whose games did exercise these tactics.

---

## Verdict and reasoning

**Decision rule applied to the BEST pair (C):**

- Mean Δ Overall = **+0.60 ≥ +0.5** → **integrate**.
- σ across teams (deltas) = 0.49, well below the 1.0 ambiguity threshold — teams agree the effect is real and positive.
- Δ Strategic Depth = +0.60, Δ Novelty = +1.40, Substrate-novelty = 5.6 — all consistent with a substrate that is doing real strategic work, not just adding decoration.
- Δ Balance = −0.20 is the one drag; small enough not to block integration but large enough to warrant a follow-up.

**Pairs A and B are tied at Δ Overall = 0.00** — confirming the spike's structural prediction: substrate effects only manifest when the rule family rewards path-routing/boundary play. Threshold-race families remain insensitive to the substrate. This is **a useful negative result**: it tells the R17 generator how to gate sierpinski mutation.

---

## R17 follow-ups (since integrating)

1. **Add `"sierpinski"` to `config.GameConfig.topology_types`**, but pair it with a generator filter that rejects sierpinski + threshold-win combinations (which Pairs A and B showed are inert). Acceptable rule-family combinations to allow: surround/custodian capture + connection win; surround + territory; outnumber + connection. Effectively: gate on win-condition family, not capture family.

2. **Engine cleanup (from existing findings):** convert remaining `range(self.total_cells)` loops in `engine_v2.py` (lines 610, 815, 838, 920) to use `self.topo.active_cells`. Currently hole-safe by accident; making the safety explicit reduces future-bug surface as new code paths land.

3. **Balance probe before R17 deployment:** Pair C teams independently flagged that the fractal's reduced corridor count amplifies P1's first-mover edge for connection wins. Run a small probe with seat-swapped self-play on Pair-C-style sierpinski games and decide whether to introduce a komi-equivalent (P2 +1 starting cell, or first-move restriction). If unfixable at the rule layer, adjust the fitness scoring to penalise P1-winrate skew on sierpinski more aggressively than on grid/torus.

4. **Pattern-vs-random control (team-14 suggestion):** before fully committing, run a one-generation A/B comparing (a) sierpinski 9×9 and (b) grid 8×8 with 17 randomly-placed holes, on a Pair-C-style ruleset. If (a) substantially outperforms (b), the Sierpinski self-similarity is doing real work; if (a) ≈ (b), the integration rationale collapses to "structured-hole grid" and the sierpinski-specific generator can be replaced by a cheaper hole-perturbation operator.

5. **Don't expose level-3 27×27 yet.** The level-2 9×9 baseline is what the eval validated. Level-3 (729 cells) would change training cost and observation tensor size enough that the Pair-C substrate effects might dilute or change character. Defer until R18 if R17 evolution converges on sierpinski-Pair-C-style champions.

6. **Track substrate-novelty separately in the fitness function.** Pair C's strongest signal was novelty (+1.40) and substrate-novelty (5.6), not strategic depth. Currently `GoEssenceScorer` does not directly reward substrate diversity — the current fitness will favour clean-grid champions. Add a small bonus for non-default topologies (e.g. +0.05 multiplier for sierpinski/hex over grid), or risk evolution rejecting the substrate even when individual games would benefit.

---

## What we learned beyond the integrate/drop decision

The cleanest operational insight is that **substrates and rule families have to co-evolve** — the carpet only earns its keep when paired with rules that load on path-routing, and the threshold-race family that has dominated R13–R16 is precisely the wrong partner for it. R17 should treat this as a **structural constraint on mutation**, not just an extra topology in the pool. Concretely: the generator should refuse to mutate a threshold-win game's topology to sierpinski, and refuse to mutate a sierpinski-connection game's win-condition to threshold. Without that coupling the substrate will score worse in evolution than it deserves.
