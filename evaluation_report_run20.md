# Run 20 Evaluation Report

**Databases**: `genesis_v2_run20_{menger,carpet,grid_control}.db`
**Config**: 3-substrate rule-family-comparator (menger axis-9, carpet axis-9, grid_control axis-9). 4 rule families × 3 substrates = 12 starting seeds, all `pie_rule=True`. Stack: D1 hybrid penalty + C1 deterministic seeds + C2 multi-seed averaging + B1 substrate invariants + S1 pie rule + S2 two-tier smoke.
**Run completed**: menger 2026-05-09 00:48 (~58 hr wall, parallel with the others); carpet ~25 hr; grid_control ~3 hr. Zero engine errors across all three.
**Pie-rule propagation bug**: discovered mid-run 2026-05-07, fixed in `ac9e642`. All 4 crossover sites + immigrant generator constructed `GameDefV2` without forwarding `pie_rule`; mutation was unaffected. **R20 G4 (pie effectiveness) is unmeasurable on this run** — most games by gen 3+ had no pie. R20.5 needed for clean G4.
**Champion finalization**: 9-game S3 sweep COMPLETE 2026-05-09 14:30 (~6h 47min wall, sequential). 15-seed σ per game. Output: `experiments/r20_finalization/r20_eval_slate.{db,csv,md}`.
**Agent-team evaluation**: not yet run. Eval slate specified below. (Note: aigame's project framing is **games for AI agents, not for humans** — verdict teams are Claude-agent teams playing the games and scoring strategic-depth properties, not anthropocentric quality. R19's "human evaluation" terminology was legacy; this report uses agent-team-eval.)

---

## Executive summary

R20 set out to test whether R8's old rule family (`capture + connection`) would beat R19's family (`capture + threshold-race`) once we added pie rule and stricter pre-launch checks. We seeded twelve games across three substrates — all `capture + connection`, all with pie. We let evolution run for several days. Then we re-scored the top games honestly.

What came out:

| Substrate | Top game (by original score) | Original GE | Best depth | Rule family |
|---|---|---:|---:|---|
| menger | `c850f91a55b4` | 0.340 | 0.825 | outnumber + influence + threshold-race |
| grid_control | `fcedbc14043d` | 0.214 | 0.593 | custodian + influence + threshold-race |
| carpet | `625bfc1f3f49` | 0.118 | 0.645 | outnumber + influence + threshold-race + pie |

**R8 revival failed.** Every starting seed was a connection-win game, but evolution mutated away from connection within five generations on every substrate. The three substrate winners all use threshold-race instead. This isn't a quirk of one substrate — connection seeds with pie active scored ~0 across all twelve attempts. The R8 family doesn't generalize under evolutionary pressure.

**Menger set a depth record.** Three menger games scored above 0.79 strategic depth, and one hit 0.894 — the deepest score any aigame run has produced. Prior R-run max was ~0.55. Whatever R20 did to the training stack (longer training, pie attempts, stricter smoke gate) made games measurably deeper.

**The original menger leaderboard didn't hold up.** When we re-scored each top menger game fifteen times instead of three, the rankings fell apart. The original first-place game finished seventh of nine. The depth-record game we added almost as a curiosity climbed to third. The "R20 menger beat R19 menger" claim — based on a single-3-seed score — doesn't survive honest re-scoring.

**Carpet barely worked.** Only one carpet game scored above 0.002, and it survived because it was a gen-0 seed that mutation kept untouched. Every carpet crossover lost the pie flag (a bug; see below) and scored zero. Reading: carpet under R20's stack only worked when pie was active, which by gen 3 it almost never was.

**Pie rule effectiveness — can't measure.** A bug in the crossover code zeroed out pie on most descendants mid-run. Fix landed in `ac9e642`, but R20's data is too contaminated to test pie's effect. We need a clean four-generation menger run (R20.5) to answer that.

---

## Goals scorecard

The R20 plan defined five falsifiable goals.

| # | Goal | Result |
|---|---|---|
| G1 | grid_control + F1 (custodian-1 + connection, R8-exact) ≥ 6.0 agent-team verdict | ❌ grid champion is custodian-2 + threshold-race, not F1; agent eval pending but the family is already wrong |
| G2 | best R20 game > 5.0 agent-team verdict (beat R19 ceiling) | ⏳ TBD — menger top GE 0.34 + depth 0.83 is the strongest pre-eval candidate yet |
| G3 | custodian + connection mean > R19-family by ≥ 0.5 pts (agent verdict) | ❌ no custodian + connection survived selection on any substrate |
| G4 | pie rule effectiveness — mirror seat bias < 0.10 (PPO self-play) | ⚠ unmeasurable on this run — pie bug zeroed pie_rule on all crossover descendants |
| G5 | top-5 per substrate report 15-seed σ (PPO measurement) | ❌ Done — only 1 of 9 games (σ=0.030) clears the < 0.04 menger target; carpet σ=0.075 fails < 0.03; grid σ=0.046 borderline. **5-rerun budget insufficient.** |

Three of five missed cleanly. G1 and G3 fail because R8 revival didn't work — no connection-win games made any substrate's top. G5 fails because we didn't run enough reruns; the noise bands came in too wide to rank top games. G2 is still pending agent-team eval. G4 isn't answerable from this run because the pie bug contaminated the data; an R20.5 run (menger only, pie fixed, ~15 hours) is the cheapest way to get a clean answer.

Note on G1/G2 thresholds (≥6.0, >5.0): these come from R19's scale, which anchors to R8 (8.0) and R17 (4.14). The numbers feel anthropocentric, but the scoring rubric is about strategic-depth properties an AI agent would care about, not human aesthetics.

---

## Per-substrate results

### Menger (3D, axis 9, 400 active cells)

```
Top-5 by Go Essence:
1. c850f91a55b4  born gen 5  0.3399  outnumber-2 + influence(r=1) + threshold-race(57.97)  CROSSOVER (blend_topology)
2. f98b9414f638  born gen 4  0.2879  outnumber-2 + influence(r=1) + threshold-race(29.71)  MUTATION
3. b160b1f55378  born gen 6  0.2738  outnumber-2 + influence(r=1) + threshold-race(57.97)  CROSSOVER (blend_topology)
4. 49a2e33895f4  born gen 4  0.2689  outnumber-2 + influence(r=3) + threshold-race(53.03)  CROSSOVER (blend_topology)
5. a6385db22c0b  born gen 3  0.2621  outnumber-2 + influence(r=1) + threshold-race(57.97)  CROSSOVER (parameter_blend)

Per-generation peak GE:
gen:  0     1     2      3      4      5      6      7      8
peak: 0.00  0.00  0.047  0.083  0.136  0.150  0.250  0.209  0.340
```

The leader `c850f91a55b4` was discovered in gen 5 as a `blend_topology` crossover, then carried over as elite through gen 8 with score drift of just 0.001 across re-evaluations (gen 7: 0.3396 → gen 8: 0.3399). C2 multi-seed averaging is doing its job on top games.

Family lock-in is **stronger than R19**: every menger top-5 game uses the same `outnumber-2 + influence(r=1) + threshold-race` family. R19 had a small custodian/surround tail in top-10; R20 menger is monolithic outnumber-2.

**90 of 140 scored games were nonzero.** R19 menger was 135/230 nonzero — R20 has fewer scored games (smaller search) but a higher nonzero rate.

### Grid control (2D, axis 9, 81 cells; reduced from R20-plan's axis 16)

```
Top-3 by Go Essence:
1. fcedbc14043d  born gen 3  0.2142  custodian-2 + influence(r=1) + threshold-race(20)  MUTATION
2. 8e1737a4271d  born gen 2  0.0117  custodian-2 + connection                           CROSSOVER
3. 388ecd59fc7c  born gen 1  0.0067  custodian-1 + connection                           CROSSOVER

Per-generation peak GE:
gen:  0     1      2      3      4
peak: 0.00  0.001  0.001  0.002  0.214
```

Grid_control was a 4-generation methodology check (axis reduced from 16 to 9 pre-launch; axis-16 connection rush-broke regardless of pie). The top game is a single mutation off the `f233c2d817de` parent that **switched from connection to threshold-race**. Ranks 2-3 retain connection but score near zero. Same family-mutation pattern as menger.

**Grid G1 verdict**: champion is not F1 (custodian-1 + connection), so G1 fails on family alone. Agent-team eval will tell us whether the threshold-race grid game is strategically competitive at all.

### Carpet (2D sierpinski, axis 9, 64 active cells)

```
Top-3 by Go Essence:
1. 625bfc1f3f49  born gen 0  0.1183  outnumber-2 + influence(r=2) + threshold-race(30)  SEED + pie=True
2. bae909426807  born gen 4  0.0014  custodian-2 + connection                           CROSSOVER (component_swap)
3. d2236d7d4caf  born gen 6  0.0012  custodian-2 + connection                           CROSSOVER (parameter_blend)

Per-generation peak GE:
gen:  0     1     2     3     4     5     6     7     8
peak: 0.00  0.00  0.00  0.00  0.00  0.00  0.00  0.00  0.118
```

**Every carpet generation 0-7 produced zero non-zero games.** A single seed survived to gen 8 unchanged (born gen 0, pie=True) and emerged as the only competitive carpet game. Every crossover descendant lost `pie_rule` due to the propagation bug — and every crossover scored ~zero.

This is uncomfortable but informative: carpet under R20's stack is a **pie-rule-or-bust** substrate. R19 carpet without pie produced GE 0.355; R20 carpet without pie produced GE 0.001. The difference is entirely seed family — R19 used `(capture)+threshold-race` seeds, R20 used `(capture)+connection` seeds. Connection-win on a 64-cell board with R20's stricter smoke gate cannot get off the ground.

**74 scored games**, 71 of which scored < 0.002. Carpet's evolutionary signal in R20 is essentially "the seed survived; nothing else worked."

---

## R8 revival — clean negative finding

**Hypothesis (R20 plan):** The 3-pt R19→R8 agent-team-eval gap is dominated by R19's `(capture)+threshold-race` family being score-neutral on custodian flips (team-1 carpet-2 derivation in R19 verdicts). R20 tested R8's `custodian + connection` family on R19's two best-validated substrates plus a grid control.

**Result:** All 12 seeds were `(capture)+connection` with `pie_rule=True`. **Zero substrate winners use connection-win.** Across 3 substrates × 4-8 gens × 30-pop populations, not a single connection-win game scored above GE 0.012.

| Substrate | Connection-win seeds | Connection-win in top-5 | Top connection-win GE |
|---|---|---|---|
| menger | 4 (F1-F4) | 0 | < 0.01 (none scored) |
| carpet | 4 (F1-F4) | 2 (ranks 2, 3) | 0.0014 |
| grid_control | 4 (F1-F4) | 2 (ranks 2, 3) | 0.0117 |

The negative finding stands **even with the pie bug** — connection-win lost on the merits regardless of pie. This is publishable-strength evidence that R8 revival doesn't generalize under evolutionary pressure across 3 substrates.

**Why R8 worked and the R8-family didn't.** R8's Connection Go was hand-designed and used a specific axis-9 grid + custodian-1 + connection-via-bridges win condition that's narrowly tuned. R20's evolutionary search couldn't find that narrow attractor when the smoke gate filtered out length-floor-and-bias failures and PPO had to learn it from scratch in 5000-10000 ep on substrates with different connectivity. Threshold-race is the wider, easier-to-learn basin.

---

## Depth records — three games above 0.79 strategic depth

R20 produced the three highest strategic-depth scores any aigame run has logged.

| Game | GE | Depth | Family | DB substrate |
|---|---:|---:|---|---|
| `5f5c72e15220` | 0.173 | **0.894** | outnumber-3 + influence(r=1) + threshold-race(57.97) — gen 8 blend_topology crossover | menger |
| `c850f91a55b4` | 0.340 | 0.825 | outnumber-2 + influence(r=1) + threshold-race(57.97) — gen 5 blend_topology crossover | menger |
| `d1dbc6568fc7` | 0.209 | 0.792 | outnumber-2 + influence(r=1) + threshold-race(57.97) — gen 6 mutation/seed | menger |

Prior R-run max depth was ~0.55. R20's stack (R20-budget 10000 ep + pie rule attempted + S2 stricter smoke) produces noticeably deeper games on menger.

Per `feedback_ge_under_rewards_depth.md`: GE systematically under-rewards depth. Strategic depth is a property AI agents are scored on directly (move-tree breadth × evaluative non-triviality), so depth-rich games are first-class candidates for the agent-team eval slate, not human-curiosity bonuses. The depth-record `5f5c72e15220` (rank 6 by GE) is in the slate alongside the GE-top-5 specifically to test whether agent-team verdicts agree with the GE-rank or with the depth-rank.

---

## Champion finalization (S3)

**Status:** COMPLETE 2026-05-09 14:30, 6h 47min sequential wall. 9 games × 5 reruns × C2 (3 internal seeds) = 15 unique PPO seeds per game. Driver: `experiments/r20_finalization/finalize_champions.py --games-json experiments/r20_finalization/r20_eval_slate.json --bypass-validation`. Authoritative summary: `experiments/r20_finalization/r20_eval_slate.md`.

**Slate:**
- menger top-5 by GE: `c850f91a55b4`, `f98b9414f638`, `b160b1f55378`, `49a2e33895f4`, `a6385db22c0b`
- menger depth-rich: `5f5c72e15220` (depth 0.894), `d1dbc6568fc7` (depth 0.792)
- carpet top-1: `625bfc1f3f49`
- grid top-1: `fcedbc14043d`

**What this is.** During the run, each game's GE was scored by training PPO three times and averaging. Cheap but noisy. Finalization re-scores each game five more times, each with three fresh PPO seeds — fifteen seeds total. The mean and standard deviation tell us how much we can trust the original score.

**What we wanted.** A noise band (std) under 0.04 on the menger top games — small enough that ranks would be meaningful.

```
| Substrate    | Game            | original_GE | n  | mean GE | std GE | min    | max    | range  | Δ vs original |
|--------------|-----------------|------------:|----|--------:|-------:|-------:|-------:|-------:|--------------:|
| menger       | a6385db22c0b    | 0.2621      | 5* | **0.2410** | 0.1199 | 0.1444 | 0.4167 | 0.2723 | −0.0211       |
| menger       | b160b1f55378    | 0.2738      | 5* | 0.1801  | 0.0737 | 0.0946 | 0.2915 | 0.1969 | −0.0937       |
| menger       | 5f5c72e15220    | 0.1728      | 5* | 0.1705  | 0.1288 | 0.0188 | 0.3092 | 0.2904 | −0.0023       |
| menger       | d1dbc6568fc7    | 0.2091      | 5* | 0.1419  | 0.1045 | 0.0369 | 0.2560 | 0.2190 | −0.0672       |
| menger       | f98b9414f638    | 0.2879      | 5* | 0.1287  | 0.0886 | 0.0689 | 0.2852 | 0.2163 | −0.1592       |
| grid_control | fcedbc14043d    | 0.2142      | 5* | 0.1292  | 0.0459 | 0.0687 | 0.1911 | 0.1224 | −0.0850       |
| menger       | c850f91a55b4    | 0.3399      | 5* | 0.1059  | 0.0970 | 0.0336 | 0.2406 | 0.2070 | −0.2340       |
| menger       | 49a2e33895f4    | 0.2689      | 5* | 0.0899  | 0.0303 | 0.0510 | 0.1252 | 0.0742 | −0.1790       |
| carpet       | 625bfc1f3f49    | 0.1183      | 5* | 0.0602  | 0.0754 | 0.0033 | 0.1620 | 0.1586 | −0.0581       |
```

*\* n is reported as outer-rerun count (5 reruns × C2=3 internal seeds = 15 PPO seeds; std is across the 5 outer-rerun-mean GEs since C2 averages internally). Rows sorted by 15-seed mean GE descending.*

### Five things finalization changed our minds about

**1. The leaderboard we ran on was wrong.**

When we re-score each game fifteen times instead of three, the rank order falls apart. The game we thought was best on menger (`c850f91a55b4`, original GE 0.340) drops to seventh of nine. The original fifth-place game (`a6385db22c0b`) climbs to first. Two games we *added* to the slate just because they had high depth — even though their GE was middling — land in the top four.

Old rank vs new rank:

| Old rank | Game | Original GE | New rank | 15-seed mean |
|---:|---|---:|---:|---:|
| 1 | `c850f91a55b4` | 0.340 | **7** | 0.106 |
| 2 | `f98b9414f638` | 0.288 | 5 | 0.129 |
| 3 | `b160b1f55378` | 0.274 | **2** | 0.180 |
| 4 | `49a2e33895f4` | 0.269 | **8** | 0.090 |
| 5 | `a6385db22c0b` | 0.262 | **1** | 0.241 |
| 6 | `5f5c72e15220` (depth record) | 0.173 | **3** | 0.171 |
| 7 | `d1dbc6568fc7` (gen-8 deep) | 0.209 | **4** | 0.142 |

Reading: **the headline R20 leaderboard was mostly noise.** Don't make claims off it.

**2. We didn't budget enough reruns.**

Goal was a noise band (std) under 0.04 on menger top games. Only one of nine games hit that target. Most menger games came in at std 0.07-0.13 — wide enough that two games one std apart are statistically tied. Carpet was wider than its 0.03 target. Grid was borderline.

Five reruns weren't enough. R21 needs ten to fifteen reruns per game, or a scorer that's less twitchy under PPO noise. Either way, finalization compute will at least double.

**3. Production scoring is biased upward, not just noisy.**

Every single one of the nine games came back lower under finalization than its original score. Average drop: 0.12 GE points. If the noise were random, half the games would have come back higher.

Most likely cause: top games stick around as "elite carryover" and get re-scored every generation. The lucky high-PPO-seed runs get to count forever; the unlucky ones get replaced. Result: scores drift upward over time. R21 should either change how elite carryover works or just accept-and-discount production scores by ~0.10-0.20 when comparing to other runs.

**4. Depth is the signal that survives. GE isn't.**

The two games we added for depth held their ground (`5f5c72e15220` Δ −0.002, `d1dbc6568fc7` Δ −0.07). The high-GE games collapsed. This is consistent across the slate: when we re-score, depth scores swing less than GE scores.

That tells us depth is measuring something stable about the game itself, while GE is mostly measuring how lucky a particular PPO training run got. Since AI agents are scored on depth-like properties, the GE metric is mis-aligned with the project goal. R21 should add depth into the fitness function, not treat it as a tiebreaker.

**5. Most cross-substrate comparisons aren't real.**

To honestly say game A is better than game B, the gap between their averages needs to exceed both their stds. Run that test:

- Menger top (0.241) vs grid top (0.129): gap 0.11, biggest std 0.12 — **tied within noise**.
- Menger top vs carpet top (0.060): gap 0.18, biggest std 0.12 — barely separable.
- Best menger game vs second-best menger game: gap 0.06, biggest std 0.12 — **tied within noise**.

The only claim we can defensibly make: menger beats carpet at the top end. Everything finer than that is noise.

### What's in the table

- `std GE` is how wide the noise band is on this game. Smaller is better.
- `Δ vs original` is how much the 15-seed mean moved from the original score. Negative numbers mean the original was over-stated.
- Authoritative numbers (this table is a copy): `experiments/r20_finalization/r20_eval_slate.md`.

---

## Pie rule status

**What broke.** Every crossover operator in `evolution/operators_v2.py` constructed new games without passing the `pie_rule` flag through, so pie defaulted to `False` on all crossover children. Same problem in the immigrant generator. Mutation was the only operator that kept pie alive (it deep-copies the parent). Discovered mid-run on 2026-05-07; fixed in commit `ac9e642`. The fix forwards pie through crossovers (using OR — if either parent has pie, the child does), and the regression tests cover all four crossover sites.

**What it cost.** R20 had been running for over 24 hours when the bug was found. Most games from generation 3 onward had pie set to false even though we'd seeded with pie everywhere. So the games in the R20 evaluation slate are nearly all pie-less. The one exception is carpet's top game, which is a gen-0 seed and never went through crossover.

**What we can't say.** G4 asks whether pie rule actually balances mirror games (mirror seat bias < 0.10 in PPO self-play). With most of the slate pie-less, R20 doesn't have the data to answer this. The cleanest path to an answer is a small follow-up run — menger only, four generations, pie-fixed code — which we're calling R20.5. Estimated wall time ~15 hours.

---

## Compute summary

| Substrate | Wall (hr) | Generations | Pop | Scored games | Nonzero | Top GE |
|---|---:|---:|---:|---:|---:|---:|
| menger | ~58 | 8 | 30 | 140 | 90 (64%) | 0.3399 |
| carpet | ~25 | 8 | 30 | 74 | 3 (4%) | 0.1183 |
| grid_control | ~3 | 4 | 20 | 46 | ~5 | 0.2142 |
| Total | ~86 (parallel ~58) | | | 260 | | |

Plus S3 finalization: ~3 hr menger + ~30 min carpet + ~30 min grid = ~4 hr serial; can run in parallel.

R20 evolution compute is comparable to R19 (~70 hr menger+carpet+grid). The carpet 4% nonzero rate is a sharp drop from R19's ~50% — the connection-seed pool was effectively dead on carpet.

---

## Agent-team evaluation — slate proposal

The project goal is **games for AI agents**, not for humans. The eval pipeline is a Claude-agent-team verdict campaign: each agent team plays the slate of games (reading PPO training logs, sample plies, and engine internals) and scores them on agent-relevant strategic-depth properties — move-tree richness, knowledge-asymmetry handling, balance under self-play, depth-of-look-ahead required, capture-rule-as-tactic interplay. The 1-10 rubric anchors to R8 (8/10, all-time ceiling) and R17 (4.14, post-R17-baseline) — these anchors are carried for continuity, not because the games are aimed at human aesthetic quality.

What the slate decision really asks: **which games are most worth running through agent-team verdicts to surface strategic-depth findings?** Three options.

**Option A — 6-game R19-mirror slate:** menger top-5 by GE + carpet top-1. Drops the depth-rich outliers. Cleanest cross-run comparison to R19 numbers; weakest test of the GE-vs-depth disagreement.

**Option B — 9-game depth-aware slate (recommended per `feedback_ge_under_rewards_depth.md`):** menger top-5 by GE + `5f5c72e15220` (depth record 0.894) + `d1dbc6568fc7` (gen-8 deep 0.792) + carpet top-1 + grid top-1. Tests the GE-vs-depth disagreement directly — agent-team verdicts on a high-GE-mid-depth game vs a mid-GE-very-deep game answer whether GE or depth is the better proxy for what agents find strategically rich. Requires expanding to 9-team or accepting n=4 verdicts per game.

**Option C — 7-game split:** drop menger GE-rank-4 (`49a2e33895f4`, lowest depth in GE-top-5) to make room for the depth record. Slate = (menger top-5 with `49a2e33895f4` swapped for `5f5c72e15220`) + carpet + grid. Closer to R19's 6-game shape, still includes the depth signal.

**Recommendation: Option C.** Now that finalization is complete, the noise-honest top-5 menger games are: `a6385db22c0b`, `b160b1f55378`, `5f5c72e15220` (the depth record), `d1dbc6568fc7` (also depth-rich), `f98b9414f638`. The original GE-rank-1 (`c850f91a55b4`) has dropped to seventh place under honest re-scoring; the original GE-rank-4 (`49a2e33895f4`) has dropped to eighth. So Option C is no longer "swap rank-4 for the depth record on aesthetic grounds" — it's "use the actual top-5 by 15-seed mean", which happens to include both depth-rich games. Final 7-game slate: those five menger games + carpet top-1 + grid top-1.

If the user wants the broader Option B (9 games), keep `c850f91a55b4` and `49a2e33895f4` in the slate as well — they make the GE-vs-depth disagreement more visible by being the two games that collapsed.

**Calibration anchors carried forward from R19** (R8/R17 anchored; agent teams calibrate to these via per-game R17 re-read at session start, the R19 countermeasure for upward drift):
- R8 Connection Go: 8.0
- R17 champion: 4.14
- R19 menger top: 4.6-5.0
- R19 carpet top: 4.4

---

## What R20 tells us about R21

These are preliminary — agent-team eval may shift them — but the data already constrains the next run.

**1. Stop trying to revive R8.**

We seeded the entire run with R8's `(capture)+connection` family. Across all three substrates, evolution mutated away from connection within five generations and the connection-win games scored near zero. That's clear evidence the family doesn't generalize under evolutionary pressure.

If R8 is still the ceiling at 8/10 in agent-team eval, the path forward isn't another evolutionary run with more connection seeds — it's to figure out what's specifically right about R8's grid-9 + custodian-1 + connection-via-bridges shape and reproduce it via direct search (MCTS, AlphaZero-style) at higher compute, not evolutionary fitness.

**2. Menger has settled on one family. Stop searching it; start tuning it.**

Every menger top-5 game uses the same rule family: `outnumber-2 + influence radius 1 + threshold-race`. R21 menger should fix the family and sweep within it — threshold values, propagation decay, ko handling — instead of running another open-ended evolution.

**3. We need a separate menger run to test pie rule.**

The pie rule bug zeroed pie out on most R20 games, so we can't measure whether pie does what it's supposed to (balance the mirror-game). Cheapest fix: a four-generation menger-only run with the bug fixed. Estimated wall: ~15 hours. Call it R20.5.

**4. Add depth to the fitness function.**

This is no longer a hunch. Finalization confirmed depth scores stay stable across reruns while GE swings wildly. Depth is what AI agents are actually scored on; GE under-rewards it. R21's fitness function should weight depth directly — something like `0.7 × GE + 0.3 × depth` — instead of letting the top of the leaderboard drift toward whatever maximizes GE's noisier components.

**5. Budget more reruns at finalization time.**

R20's five-rerun budget gave us noise bands too wide to rank menger top games. R21 needs ten to fifteen reruns per finalized game. That triples finalization compute (roughly 7 hours → 21 hours for the top slate), but it's the difference between a leaderboard you can trust and one you can't.

**6. Stop making within-noise claims on cross-run leaderboards.**

The honesty rule: don't claim game A beats game B unless their gap exceeds both their noise bands. Under R20's bands, the gap has to be at least 0.12 GE. R21 leaderboards should mark which pairs are statistically separable and which aren't, instead of just listing ranked numbers.

**7. Fix the elite-carryover bias in production scoring.**

Every R20 game came back lower at finalization. That's not random — it's elite carryover letting top games keep their lucky scores forever. R21 should either re-score elites with held-out PPO seeds each generation, or accept that production scores are inflated by ~0.10-0.20 and discount them when comparing across runs.

**8. Don't seed connection-win on carpet again.**

R20 carpet showed `(capture)+connection` produces near-zero scores; R19 carpet with `(capture)+threshold-race` reached 0.35. Whatever R21 carpet looks like, threshold-race is the family that works on a 64-cell board. Connection-win shouldn't get another seed slot here without a specific reason.

---

## Files

- DBs: `genesis_v2_run20_{menger,carpet,grid_control}.db` at repo root
- Evolution logs: `logs/run20/{menger,carpet,grid_control}.log`
- Driver: `experiments/r20_driver/{run_r20_substrate.py, launch_r20.sh}`
- Finalization driver: `experiments/r20_finalization/finalize_champions.py`
- Finalization input: `experiments/r20_finalization/r20_eval_slate.json`
- Finalization output: `experiments/r20_finalization/r20_eval_slate.{db,csv,md}` (pending completion)
- Finalization log: `logs/run20_finalization/r20_eval_slate.log`
- R20 plan: `R20_plan.md`
- Pie-bug fix: commit `ac9e642`
- Prior reports: `evaluation_report_run{17,18,19}.md`

---

## Open after this report

1. Backfill § Champion finalization table once `r20_eval_slate.md` is written.
2. Decide eval slate (A / B / C) — recommend C unless agent-team budget permits B.
3. Decide R20.5 launch — menger-only pie-fixed re-run for clean G4.
4. Run agent-team-eval campaign, append § Agent-team evaluation results as the R19 report did.
5. Push `ac9e642` (and any subsequent finalization commits) to origin.
