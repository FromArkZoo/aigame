# Run 20 Evaluation Report

**Databases**: `genesis_v2_run20_{menger,carpet,grid_control}.db`
**Config**: 3-substrate rule-family-comparator (menger axis-9, carpet axis-9, grid_control axis-9). 4 rule families × 3 substrates = 12 starting seeds, all `pie_rule=True`. Stack: D1 hybrid penalty + C1 deterministic seeds + C2 multi-seed averaging + B1 substrate invariants + S1 pie rule + S2 two-tier smoke.
**Run completed**: menger 2026-05-09 00:48 (~58 hr wall, parallel with the others); carpet ~25 hr; grid_control ~3 hr. Zero engine errors across all three.
**Pie-rule propagation bug**: discovered mid-run 2026-05-07, fixed in `ac9e642`. All 4 crossover sites + immigrant generator constructed `GameDefV2` without forwarding `pie_rule`; mutation was unaffected. **R20 G4 (pie effectiveness) is unmeasurable on this run** — most games by gen 3+ had no pie. R20.5 needed for clean G4.
**Champion finalization**: 9-game S3 sweep COMPLETE 2026-05-09 14:30 (~6h 47min wall, sequential). 15-seed σ per game. Output: `experiments/r20_finalization/r20_eval_slate.{db,csv,md}`.
**Agent-team evaluation**: complete — 35 verdicts (5 teams × 7 games, Option-C slate, 2026-05-09). See § Agent-team evaluation results below. (aigame's project framing is **games for AI agents, not for humans** — verdict teams are Claude-agent teams playing the games and scoring agent-relevant strategic-depth properties, not anthropocentric quality. R19's "human evaluation" terminology was legacy; this report uses agent-team-eval.)

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
| G4 | pie rule effectiveness — mirror seat bias < 0.10 (PPO self-play) | ⚠ partial (measured in R20.5) — 3/5 PASS, 2/5 FAIL by 0.03–0.04 under sampled-trained mirror eval. Pie corrects ~70% of structural bias but doesn't fully neutralise on the strongest games. See § R20.5. |
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

## R20.5 — pie-fixed menger re-run (G4 measurement, 2026-05-10)

**Setup.** 4 evolution gens × 30 pop, menger axis-9 only, with the `ac9e642` pie-propagation fix in place. DB: `genesis_v2_run20_menger_pie_fix.db`. All 130 games in the run carry `pie_rule=True` — the fix works. Total wall: 19h 4min (2026-05-09 21:30 → 2026-05-10 16:34).

**Mean GE climbed steadily across generations** (0.008 → 0.015 → 0.033 → 0.056 → 0.085) — pie didn't kill fitness pressure. Best GE was flat at ~0.20 through gens 0–2 and broke out to 0.2383 in gen 3, carried as elite into gen 4.

### Top-5 menger games (single-seed production scoring)

| Game ID | GE | Depth | Family | Pie | Gen | Parents |
|---|---:|---:|---|:---:|:---:|---|
| `2f378e8c18b5` | 0.2383 | 0.579 | outnumber + threshold-race | ✓ | 4 | `e9414200632e`, `9efafa340361` |
| `66c7c98d3745` | 0.2152 | 0.549 | outnumber + threshold-race | ✓ | 4 | `7aeb96ff9a8f`, `e9414200632e` |
| `77f8288387d9` | 0.2150 | 0.548 | outnumber + threshold-race | ✓ | 4 | `8ad05b2db30f`, `e9414200632e` |
| `c9fd0350fdf7` | 0.2003 | 0.545 | outnumber + threshold-race | ✓ | 4 | (immigrant) |
| `faebc7094d51` | 0.1861 | 0.545 | custodian + threshold-race | ✓ | 4 | `8f238697666f`, `2f378e8c18b5` |

**Family hegemony persists.** 4 of 5 are `outnumber + threshold-race` (the same family that swept R20). 1 of 5 is `custodian + threshold-race`. Connection-win still doesn't survive even with pie clean — R8-revival negative finding holds under R20.5 conditions.

**No byte-identical duplicates** within R20.5 top-5 OR vs R20 menger top-7 (verified by SHA-256 over `rule_representation`). Distinct from R20's byte-identical trio; see § Functional-equivalence finding below.

### G4 — pie effectiveness (partial PASS)

**Methodology.** Driver: `experiments/r20_5_g4/run_g4.py`. Per game, train PPO 3000 ep at seed 42; then run **sampled trained-vs-trained mirror eval** with seat-swap halves (n=200, `deterministic=False`). G4 metric: `g4_seat_bias = abs(sampled_p1_winrate - 0.5)`.

**Why a custom eval, not the harness's `seat_bias`.** The harness's existing `seat_bias = abs(greedy_p1_winrate - 0.5)` is computed from greedy-vs-greedy. `GreedyAgent` always-swaps under pie (commit `d25590d`: "the upper-bound assumption — if pie can't structurally balance the game even when P2 always swaps, the game is rush-broken"). So on any pie-rule game, P2 trivially wins ~85–90% under greedy regardless of equilibrium. Deterministic-trained also fails (per harness module docstring: deterministic argmax collapses to identical 2-step games). Only sampled trained-vs-trained with seat-swap preserves the equilibrium where pie usage is rational — which is what G4 actually wants. The first G4 driver pass used the harness's greedy metric and produced uniform G4 FAIL across all 5 games (greedy_p1_wr = 0.10–0.22). The second pass — what's reported here — uses the principled metric.

| Game | sampled_p1_wr | **G4 seat bias** | sampled_len | greedy_p1_wr (diag.) | G4 verdict |
|---|---:|---:|---:|---:|:---:|
| `2f378e8c18b5` | 0.630 | **0.130** | 57.1 | 0.120 | FAIL |
| `66c7c98d3745` | 0.560 | **0.060** | 57.1 | 0.100 | PASS |
| `77f8288387d9` | 0.560 | **0.060** | 57.1 | 0.100 | PASS |
| `c9fd0350fdf7` | 0.560 | **0.060** | 57.1 | 0.100 | PASS |
| `faebc7094d51` | 0.640 | **0.140** | 74.9 | 0.220 | FAIL |

**G4: PARTIAL PASS — 3/5 < 0.10. Failing games miss by 0.03–0.04.**

**Reading the result.**
- **Pie does most of the work.** Greedy diagnostics (P2 wins 78–90%) show the underlying games have strong P1 rush advantage. After pie + sampled-trained equilibrium, P1 advantage is reduced to 0.06–0.14. Pie corrects ~60–80% of the structural bias.
- **Pie doesn't fully neutralise on the strongest games.** The two failing games are also the two stylistically-distinct ones: the top GE game (`2f378e8c18b5`, 0.130 over) and the lone custodian game (`faebc7094d51`, 0.140 over). The 3 outnumber+threshold games at the middle of the GE rankings all PASS at exactly 0.060.
- **The "all-PASS" framing of G4 was probably overoptimistic.** Pie is a one-move correction at the start of the game; on games where the structural P1 rush is large enough, a single swap can't fully cancel it. R21 may need to add a second balancing mechanism (e.g. ko-style restriction, asymmetric scoring) for games where pie alone leaves residual bias.

Output: `experiments/r20_5_g4/g4_smoke.{db,md}`. Log gitignored.

### Functional-equivalence finding

The 3 PASSing games (`66c7c98d3745`, `77f8288387d9`, `c9fd0350fdf7`) have **identical eval stats** to one-decimal precision: sampled_p1_wr = 0.560, sampled_len = 57.1, greedy_p1_wr = 0.100. Yet their `rule_representation` blobs are **NOT byte-identical** — distinct SHA-256 hashes, distinct blob lengths (802, 802, 770 bytes).

This is a different pattern from R20's byte-identical-trio (`a6385db22c0b` / `b160b1f55378` / `d1dbc6568fc7`). R20's trio had the SAME rule blob written under three different game IDs. R20.5's PASSing trio has DIFFERENT rule blobs that produce IDENTICAL trained-policy behaviour — **functionally equivalent** rather than literally identical.

**R21 implication: rule-blob deduplication must be functional, not just byte-hash.** R20's recommendation (item 1 in § R21 implications) was to hash genotypes and drop duplicates. That would catch R20's byte-identical trio but NOT R20.5's functional-equivalent trio. R21 needs either (a) trained-policy-fingerprint dedup (run a short PPO smoke per candidate, hash the resulting policy or eval stats), or (b) semantic rule-blob normalisation (canonicalise rule order, parameter encoding) before hashing. Option (b) is cheaper but may miss reorderings that produce equivalent dynamics.

### 15-seed finalization

Running in background as of 2026-05-10 (estimated ~21h sequential). Driver: `experiments/r20_finalization/finalize_champions.py --auto menger:genesis_v2_run20_menger_pie_fix.db:3`. Output (when complete): `experiments/r20_5_finalization/r20_5_eval_slate.{db,csv,md}`. Slate: top-3 by GE = `2f378e8c18b5`, `66c7c98d3745`, `77f8288387d9`. Section will be appended once the run completes.

Sanity-check expectation per S3 finding (mean Δ = −0.119 production-vs-15-seed): top game's honest mean GE should land near 0.12 ± 0.10, mid-table on R20's 15-seed leaderboard. Not a new champion candidate by GE alone.

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

## Agent-team evaluation results (35 verdicts, 2026-05-09)

5-team protocol: 1 pilot + 4 production teams × 7 games (Option-C slate). Pilot ran first to validate helper and surface briefing issues; production teams ran in parallel without seeing pilot scores. Verdicts in `evaluations/run20/team-{pilot,1..4}_game{ID}.md`. Helper: `eval_run20_helper.py`. Verdicts score on agent-relevant strategic-depth properties (move-tree richness, capture-rule-as-tactic interplay, knowledge-asymmetry handling, balance under self-play) — calibrated to R19's 1-10 scale for cross-run continuity, **not** to anthropocentric quality.

### Per-game scores (n=5)

| Substrate | Game ID | 15-seed GE | σ (GE) | Depth | pilot | t1 | t2 | t3 | t4 | **Mean** | **SD** |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| menger | `a6385db22c0b` | 0.241 | 0.120 | 0.763 | 3 | 3 | 3 | 3 | 3.5 | **3.10** | 0.20 |
| menger | `b160b1f55378` | 0.180 | 0.074 | 0.690 | 3 | 3 | 3 | 3 | 4 | **3.20** | 0.40 |
| menger | `5f5c72e15220` ⭐depth | 0.171 | 0.129 | **0.894** | 6 | 5 | 5 | 4 | 4 | **4.80** | 0.75 |
| menger | `d1dbc6568fc7` | 0.142 | 0.105 | 0.792 | 3 | 3 | 3 | 3 | 3.5 | **3.10** | 0.20 |
| menger | `f98b9414f638` | 0.129 | 0.089 | 0.597 | 3 | 4 | 3 | 4 | 3 | **3.40** | 0.49 |
| carpet | `625bfc1f3f49` ⭐pie | 0.060 | 0.075 | 0.645 | 5 | 5 | 4 | 5 | 4.5 | **4.70** | 0.40 |
| grid | `fcedbc14043d` | 0.129 | 0.046 | 0.593 | 4 | 3 | 5 | 4 | 4 | **4.00** | 0.63 |

**Per-team means (calibration anchors):** pilot 3.86, t1 3.71, t2 3.71, t3 3.71, t4 3.79. **Production-only mean 3.73**; **including pilot 3.76**. Pilot drift this campaign was small (+0.13 vs production) — much tighter than R19's pilot-vs-production gap of +0.45. Production teams converged to 3.71 ± 0.04 across the four independent campaigns; calibration-stability is the highest of any aigame run.

### GE-rank vs eval-rank disagreement

| Game | 15-seed GE | GE rank | Eval mean | Eval rank | Δ rank |
|---|---:|---:|---:|---:|---:|
| `a6385db22c0b` | 0.241 | 1 | 3.10 | 6 (tied) | **−5** |
| `b160b1f55378` | 0.180 | 2 | 3.20 | 5 | **−3** |
| `5f5c72e15220` ⭐ | 0.171 | 3 | **4.80** | **1** | **+2** |
| `d1dbc6568fc7` | 0.142 | 4 | 3.10 | 6 (tied) | **−2** |
| `fcedbc14043d` | 0.129 | 5 (tie) | 4.00 | 4 | +1 |
| `f98b9414f638` | 0.129 | 5 (tie) | 3.40 | 5 | 0 |
| `625bfc1f3f49` | 0.060 | 7 | **4.70** | **2** | **+5** |

The two largest rank disagreements are also the two structural anomalies in the slate. **Carpet `625bfc1f3f49` jumps from GE rank-7 to eval rank-2** — the only pie-rule game; pie does meaningful work. **Menger `5f5c72e15220` jumps from GE rank-3 to eval rank-1** — the only outnumber-3 game; depth metric and agent verdicts agree this is the deepest. Together they confirm the project goal: GE under-rewards depth-rich and structurally-distinct games, exactly per `feedback_ge_under_rewards_depth.md`.

### The byte-identical-trio finding (campaign headline)

**Three of the five menger games (`a6385db22c0b`, `b160b1f55378`, `d1dbc6568fc7`) have byte-identical rule blobs** — same capture rule (outnumber-2), same threshold, same propagation kernel, same win condition, same pie flag, same max_turns. The 15-seed mean GE differences (0.241/0.180/0.142) and depth differences (0.763/0.690/0.792) are pure measurement noise.

Three teams confirmed this empirically: pilot inferred from rule inspection; team-1 replayed pilot's 51-move mainline on all three games and got identical +59/+53 final scores; team-2 confirmed identical Winner=1 at step 59 across the trio. **The R20 slate triple-counts a single underlying game**, wasting ~40% of the eval budget.

This explains Goal G5's failure (5-rerun budget insufficient): the σ estimates were inflated by what looked like rule-distinct games' independent measurement noise but is actually the same game's PPO-seed noise repeated three times. **R21 must enforce rule-blob deduplication before slate finalization.**

### Cross-substrate comparison (under campaign noise)

| Substrate | Top game | Eval mean | Mean of subs (5-team) | n verdicts |
|---|---|---:|---:|---:|
| menger | `5f5c72e15220` (depth-record) | **4.80** | 3.52 | 25 |
| carpet | `625bfc1f3f49` (only pie) | **4.70** | 4.70 | 5 |
| grid | `fcedbc14043d` (closest R8 analog) | **4.00** | 4.00 | 5 |

Honesty rule (gap > both σs to claim separation):
- Menger top (4.80, σ=0.75) vs carpet top (4.70, σ=0.40): gap 0.10, σ_max 0.75 — **tied within noise.**
- Menger top vs grid top (4.00, σ=0.63): gap 0.80, σ_max 0.75 — **tied within noise.**
- Carpet top vs grid top: gap 0.70, σ_max 0.63 — **tied within noise.**

The only defensible cross-game claim: the slate's three top-of-substrate games are statistically indistinguishable. Within-substrate, menger has wide spread (3.10 → 4.80) but **the spread is almost entirely the depth-record game vs the byte-identical trio**.

### Anchored against R8 / R17 / R19

| Anchor | Score | R20 comparison |
|---|---:|---|
| R8 Connection Go (ceiling) | 8.0 | R20 ceiling is 4.80 — **3.2 points below R8**. No R20 game approaches the R8 family. |
| R17 mean | 3.50 | R20 mean 3.76 is +0.26 above. Modest improvement, smallest cross-run delta in the corpus. |
| R17 best (`44f6630277b3`) | 4.14 | R20 has 3 games clearing it: `5f5c72e15220` 4.80, `625bfc1f3f49` 4.70, `fcedbc14043d` exactly 4.00. |
| R19 menger top (`1f9191b5d4e6`) | 4.8 | R20 menger top (`5f5c72e15220`) ties exactly at 4.80. **G2 (>5.0) FAILS by 0.2 — does not beat R19's ceiling.** |
| R19 menger surround top-3 (`5048f71b62fd`) | 5.0 | R20 has no game above this — surround capture from R19 still outperforms outnumber-3 from R20. |
| R19 carpet top (`ce3a09e05cef`) | 4.4 | R20 carpet (`625bfc1f3f49`) at 4.70 — **+0.30 above R19 carpet ceiling**. The pie-rule game is the slate's only above-R19 result. |
| R19 production mean | 4.375 | R20 production mean 3.73 is **−0.65 below R19**. The byte-identical-trio dragging the menger floor explains most of the gap. |

**G2 verdict** (R20 plan: best R20 game > 5.0 agent-team verdict): ❌ **FAILS** by 0.2. The depth-record `5f5c72e15220` ties R19's menger top-1 exactly but does not clear R19 menger top-3.

### The depth-vs-GE disagreement: 5-team verdict

`5f5c72e15220` (depth metric 0.894 — highest in any aigame run) split the campaign:

| Team | Score | Read |
|---|---:|---|
| pilot | 6 | Depth genuine. Outnumber-3 enables double-capture, residual-value harvest, cluster-deepening. |
| team-1 | 5 | Depth genuine **but only on non-mainline P2 wrap-capture** (5 captures in 22 plies suppressing P1's cluster). Mainline play is identical to outnumber-2 siblings. |
| team-2 | 5 | Depth genuine via outnumber-3 + influence-r=1 + hub geometry **multi-rule synergy**. Move 18 captured the (2,2,2) hub via the (2,2,3)+(2,3,2)+(3,2,2) triangle. |
| team-3 | 4 | Depth metric is **strategic-diversity mistaken for planning-depth** — multiple opening families reach threshold in similar plies but each ply is 1-ply lookahead. |
| team-4 | 4 | Depth metric **over-rewards game length and residue accumulation**, not decision-tree complexity. Outnumber-3 makes captures *more* vestigial than outnumber-2. |

**Synthesis**: depth on `5f5c72e15220` is real (3 of 5 teams scoring ≥5) but **mechanism-specific** — concentrated in non-mainline P2 wrap-capture / hub-cluster strategies that PPO mainline doesn't reach. The 0.894 depth metric is partially valid (rewards distinct rule kernel) and partially confounded (rewards game length). **R21's fitness function should keep GE rank for parameter-sibling discrimination but add a planning-horizon proxy** (team-3's suggestion: gap between 1st- and 2nd-best equity moves per ply) for cross-rule comparisons.

### Pie rule effectiveness (G4 partial answer)

`625bfc1f3f49` is the only pie-rule game in the slate. G4 was nominally "unmeasurable on this run" because the pie bug zeroed pie on most descendants. Agent-team eval contributes a partial answer:

- **Pie verified mechanically** — pilot, t1, t2 all confirmed action 82 swaps seats correctly; trained-vs-trained 0.500 over 27 PPO runs is the most reliable balance datum in R20.
- **team-1 empirical proof** that pie does corrective work: P1 plays max-degree (2,2), P2 invokes pie, **P2 wins by +2.5**. Pie *over-corrects* against strong openings, forcing P1 to play a "fair" middle-strength move.
- **Pilot + team-4 dissent**: pie is structurally a no-op for tempo balance — it transfers first-stone advantage to whichever side claims it; 0.500 reflects equilibrium-where-pie-usage-is-rational, not equilibrium-where-pie-equalizes-seats.
- **3 teams agree pie is "the only meaningful meta-strategic content in the slate"** (t1, t3, pilot). The R19 30/30 carpet verdict ("add pie rule") is empirically validated here.

### `fcedbc14043d` as R8-revival proof: "R8 minus connection-win"

team-1 framed the cleanest R8-revival negative finding citation: **`fcedbc14043d` is R8's `9d33eee27c66` minus the connection-win** — same custodian capture, same flat axis-9 grid, same influence-r=1 propagation. The only differences are the win condition (threshold-race vs connection) and parameter values.

This game scores 4.00 (production mean 4.0). R8 scored 8.0. **The 4-point gap is in the win condition, not the substrate or the capture rule.** team-3 elaborated: custodian on `fcedbc14043d` produces real counter-flip cycles — the most-tactically-active capture in the slate — but threshold-race wastes its strategic potential because flips are tempo-only, not win-relevant.

This is sharper than R20's executive-summary "R8 revival failed" framing: it's not that connection-win + custodian doesn't generalize — it's that **threshold-race-without-connection-win is the wrong fitness attractor on flat-grid + custodian substrates**. R21 should restore connection-win as a candidate if grid + custodian are seeded.

### Briefing inaccuracy flagged for fix

team-1 flagged that briefing_grid_fcedbc14043d.md's claim "`target_dimension_p2 = +1` gives P2 a 'separate accumulator'" is incorrect. Engine `_check_threshold` (`engine_v2.py:967`) always uses the mirror-sum convention; `target_dimension_p2` is only consulted for connection-win games. All 5 teams scored fcedbc14043d on the correct (mirror) interpretation regardless. **Briefing fix to land before R21 grid eval.**

### Cross-cutting themes

**Universal (all 7 games):**
- **Pie rule should propagate to all R21 games**, especially with the `ac9e642` fix landed (4/5 teams).
- **Slate selection must enforce rule-blob deduplication** (3/5 teams confirmed empirically).
- **Depth metric needs a planning-horizon adjustment** (3/5 teams; team-3 proposes "1st-best vs 2nd-best equity gap per ply").
- **GE rank still beats depth rank for parameter-sibling discrimination** — within the byte-identical trio, depth ranks them as 0.690/0.763/0.792 (pure noise), GE ranks them as 0.180/0.241/0.142 (also noisy but smaller-scale, and closer to truth: they're tied).

**Menger-specific:**
- **Outnumber-3 is the structural differentiator** — outnumber-2 produces capture-vestigial games (cluster-build dominates); outnumber-3 enables hub-capture, double-capture, residual-value harvest, P2 wrap-encirclement.
- **Mainline PPO play in menger is cluster-vs-cluster non-engagement** — captures rarely fire, both sides build separate empires until threshold. Real depth requires non-mainline strategy commitment.
- **`f98b9414f638` (threshold=29.7) is the structural odd-one-out** — racier, balance-preserving, but reduced strategic-diversity (0.333) confirmed by lowest novelty score (2.80) in slate.

**Carpet-specific:**
- **Pie rule is decisive on small boards** with big propagation footprints (r=2 on 64 active cells = 13/64 = 20% of board affected per move). The mechanic *over*-corrects rather than equalizes — but the over-correction is itself strategic content.
- 0.760 trained-vs-random WR (lowest in slate) means random play accidentally finds non-degenerate games here — a substrate property worth replicating in R21 carpet.

**Grid-specific:**
- **Custodian + flat grid + threshold-race is structurally shallow** — 22-ply average game is the shortest in slate; tactical content is real but win condition wastes it.
- **R8 ancestor identification is direct**: this is the clearest "R8 minus a single rule axis" game in the corpus.

### Top independent findings beyond pilot

| Finding | Game | Team | Significance |
|---|---|---|---|
| Empirical byte-identity replay (51-move mainline → identical scores) | a6385db / b160 / d1dbc6 | t1 | Confirms slate triple-counting at engine level |
| outnumber-3 hub-capture via (2,2,3)+(2,3,2)+(3,2,2) cluster | `5f5c72e15220` | t2 | Citable mechanical primitive for outnumber-3 depth |
| Pie over-corrects: P1@(2,2) → P2 invokes → P2 wins +2.5 | `625bfc1f3f49` | t1 | Cleanest pie-effectiveness datum in campaign |
| Depth = strategic-diversity mistaken for planning-depth | `5f5c72e15220` | t3 | Suggests "1st-best vs 2nd-best equity gap" R21 fitness component |
| Outnumber-3 makes capture *more* vestigial than outnumber-2 | `5f5c72e15220` | t4 | Refines mechanism — depth ≠ tactical engagement on this game |
| `fcedbc14043d` = R8 minus connection-win | `fcedbc14043d` | t1 | Sharpens R8-revival negative finding to win-condition-specific |
| `target_dimension_p2 = +1` is inert under threshold-race | `fcedbc14043d` | t1 | Briefing fix; engine_v2.py:967 |
| Custodian counter-flip cycles wasted by threshold-race | `fcedbc14043d` | t3 | Argues for connection-win restoration on grid + custodian |
| P2 wrap-capture on outnumber-3 (5 captures in 22 plies) | `5f5c72e15220` | t1 | Reconciles depth-genuine vs depth-suspect cross-team split |

### R21 implications (preliminary)

These constrain R21 scope; R20.5's pie-fixed menger re-run will sharpen item 4.

**1. Enforce rule-blob deduplication in slate selection.** R20 wasted ~40% of the eval budget triple-counting one game. R21 should hash genotypes before adding to a slate; rank ties on hash → drop duplicates and pull from the next-ranked unique kernel. Implement at champion-finalization slate-build time (`experiments/r20_finalization/finalize_champions.py:slate_select`).

**2. Add a planning-horizon term to GE.** team-3's proposal: per-ply equity gap between 1st-best and 2nd-best legal moves, averaged across PPO games. High = decisions matter; low = moves are interchangeable (the menger byte-identical trio reads as "high" on raw depth but "low" on this proxy). Don't replace depth — augment it with a metric that distinguishes diversity from genuine lookahead. R21 should A/B test this.

**3. Pie rule for every R21 game** — the only meta-strategic content in the slate, validated empirically by the only game that has it. With `ac9e642` fixed, propagation works through crossover. Don't gate behind "pie effectiveness measurement"; ship it as scaffolding.

**4. Restore connection-win for grid + custodian seeds.** R20 wrote off connection-win as "doesn't generalize under evolutionary pressure" but agent-team verdicts say the actual signal is win-condition-specific: threshold-race wastes custodian's tactical content. R21 grid runs should seed connection-win + custodian with the new pie rule and let evolution explore. R8's 4-point lead is in the win condition, not the substrate or the capture.

**5. R20 menger ties R19 menger top-1; doesn't beat R19 menger top-3.** G2 fails by 0.2. The R20 stack (10000-ep training + pie attempted + S2 stricter smoke) didn't move the menger ceiling above R19. Either the menger ceiling is a real plateau at 4.8-5.0 with current rule families, or R21 needs a structurally distinct rule family (R8-style connection-win on menger, or move-action restoration with a different penalty calibration).

**6. Carpet's R20 result is structurally informative.** R20 carpet ceiling 4.70 > R19 carpet ceiling 4.40 — the only above-R19 result in the slate. The differentiator is pie. R21 carpet should keep this game as a seed and explore variations *within* the pie+r=2+outnumber-2 family rather than re-opening to other capture rules.

**7. Cross-substrate comparison verdict: tied within noise.** Don't claim menger > carpet > grid for R20 the way R19 humans did. Honest reading: with σ ≥ 0.40 on every substrate's top game and gaps ≤ 0.80, menger / carpet / grid are statistically indistinguishable at the slate's ceiling.

**8. Calibration is reproducible.** Production teams converged 3.71 ± 0.04 across 4 independent runs — tighter than any prior campaign. The R17/R19 calibration anchors hold; pilot drift can be small (+0.13 here) when briefings include explicit anchor reads. Continue mandating R17 verdict reads at session start.

---

## Files

(see § Files above; in addition for the agent-team eval campaign:)

- Agent-team verdicts: `evaluations/run20/team-{pilot,1..4}_game{ID}.md` (35 files)
- Eval helper: `eval_run20_helper.py`
- Briefings: `evaluations/run20/briefing_{menger,carpet,grid}_<ID>.md` (7 files)
- Protocol/index: `evaluations/run20/README.md`
- Verdict template: `evaluations/run20/TEMPLATE_team-N_gameXXXX.md`

---

## Open after this report

1. ~~Run agent-team-eval campaign, append § Agent-team evaluation results.~~ ✅ Complete.
2. ~~Backfill § Champion finalization table once `r20_eval_slate.md` is fully written.~~ ✅ Complete.
3. ~~Decide R20.5 launch — menger-only pie-fixed re-run for clean G4.~~ ✅ Complete (run + G4 measured 2026-05-10; see § R20.5).
4. Fix `briefing_grid_fcedbc14043d.md` `target_dimension_p2` claim (team-1 finding; engine_v2.py:967 is mirror-sum unconditional under threshold-race). **R21.**
5. Implement **functional** rule-blob deduplication in `experiments/r20_finalization/finalize_champions.py:slate_select` (R20.5 functional-equivalence finding raises the bar from byte-hash to trained-policy-fingerprint or semantic-blob-canonicalisation). **R21.**
6. ~~Push `ac9e642` (and any subsequent finalization commits) to origin.~~ ✅ Complete.
7. R20.5 15-seed finalization on top-3 (running ~21h in background); append § when complete.
