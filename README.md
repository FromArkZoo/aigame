# Genesis Engine

**A systematic study of whether evolutionary search combined with LLM-as-judge evaluation can discover novel abstract strategy games with genuine strategic depth.**

This project evolves original two-player games on n-dimensional topological boards, scored by a metric — **Go Essence** — that balances strategic richness against rule complexity:

```
GoEssence = (strategic_depth × strategic_diversity) / rule_complexity
```

The hypothesis: can unguided search on a constrained rule grammar rediscover the depth-from-simplicity property that makes Go, Chess and Hex interesting — and ideally find something new that didn't come from human intuition?

After 21 evolution runs the GE-evolution regime saturated (two consecutive sub-5.0 agent-eval campaigns, with GE anti-correlating with agent-judged depth at the extremes). The project now tests rule levers directly with **pre-registered probes** — calibration gate → mechanical screen → blind agent A/B with sealed labels — and reports the NO-GOs as faithfully as the wins.

## What the pipeline does

Each generation runs four stages:

1. **Generate** (`evolution/operators_v2.py`) — mutate + crossover game definitions drawn from a structured grammar of topologies, placement rules, capture mechanics, propagation rules, and win conditions
2. **Validate** (`game_engine/generator_v2.py`) — reject degenerate games via short rollouts: no guaranteed early dominance, reachable wins, both players must interact
3. **Train** (`training/trainer.py`) — PPO self-play on each candidate, returning win-rate balance, ELO, and game-length statistics
4. **Score** (`metrics/scoring.py`) — compute Go Essence from training outputs plus a rule-complexity estimate

Top candidates are then evaluated by **independent Claude agent teams** (typically 5–7 teams across the top 3–4 games per run) that each play full head-to-head games, produce strategy guides, and score across five axes (strategic depth, emergent complexity, balance, novelty, replayability). Every run is checkpointed to SQLite; every evaluation report lives in the repo.

## The research progression

The search has gone through several architectural generations, each prompted by the failure mode of the last:

| Gen | Approach | Outcome |
|---|---|---|
| **V1** | Unconstrained rule expression trees | Grammar too loose → degenerate games, no theoretical binding |
| **V2** | Structured rules on n-dim boards (placement, capture, propagation, win) | Games are playable, but the search converges to a **Go × Hex local optimum** |
| **V3** | **Cellular automata as rule substrate** — evolve the state-transition rule itself | Expanded grammar; CA games can compete (R13) but didn't deliver the breakthrough on a 64-cell grid |
| **V3.5** | **Fractal substrates** — vary the *board topology's* Hausdorff dimension as a search axis | R18 showed menger sponge (dim 2.727) lifts above flat-grid champions; R19 was the first end-to-end run under deterministic, multi-seed scoring + hybrid-action ban; R20 stress-tested rankings with 15-seed σ and produced the project's deepest single game (depth 0.894) |
| **V4 (current)** | **Pre-registered rule probes** — after R21 fired the pivot rule, stop evolving against GE and test rule levers directly: influence-field win conditions, blind agent A/Bs, locked decision criteria | Field-Connect probe: 2/2 blind teams prefer the interaction-forcing win condition at 4.15 ≈ R8 parity on its first build (lever validated; parameterization NO-GO). Phase-1.5 slate screened out — and inverted its own premise: radius-2 field overlap is what makes control contestable. Next: new win-condition family or Quality-Diversity selection |

The CA direction is laid out in [`cellular_automata_proposal.txt`](cellular_automata_proposal.txt). The fractal-substrate pivot (R17 → R18) holds the rule grammar fixed but lets evolution search across boards with non-integer dimension — vicsek (1.465), triangle (1.585), carpet (1.893), grid (2.000), menger (2.727).

## Run history

Each run is a deliberate response to what the previous one revealed.

| Run | Focus | Key finding |
|---|---|---|
| 7–8 | V2 baseline | Go × Hex hybrid emerges as a strong local optimum (R8 "Connection Go" — 8/10 LLM eval, project's strongest game to date) |
| 9 | Larger populations | Confirmed Go × Hex isn't novel — it's just Go on a different topology |
| 10 | Added validation rules | **Ko fights emerged from a non-Go mechanism** (overwrite + outnumber) — a genuinely new discovery |
| 11 | Tightened constraints | Hex-focused, torus banned, R10 failure modes folded into the validator |
| 12 | First CA run | Evolving the rule substrate itself — no CA games competitive yet |
| 13 | CA + larger pop | First competitive CA games (9 of top-20). **Engine bug discovered**: `topology.distance()` used Manhattan on all topologies, breaking influence propagation on hex/moore/torus since V3 |
| 14 | Sim×CA push | No champion beats predecessors; GE metric again fails to track human judgment; sim×CA "signal" looks promising |
| 15 | Sim×CA + symmetry fixes | Three new iteration-order biases surfaced (`_check_threshold`, `_check_connection`, CA step-ordering); once fixed, the sim×CA signal disappears |
| 16 | Margin-based resolution + CA snapshot fix | Engine biases closed; mechanics stable but games still ≤ R8 quality |
| 17 | Soft-rule audit + seat-balance hard-zero + fractal seed | First clean engineering run with regressed games; champion 4.14/10. Seeded fractal substrate collapsed under PPO |
| 18 | **6-substrate Hausdorff-dim scan** (vicsek / triangle / carpet / grid / menger) | Menger lifts above other substrates on peak-GE; **GE volatility finding** — per-generation peaks drop 50–80 % when re-trained, because PPO seeds were generation-indexed |
| 19 | Champion run on menger + carpet under C1 (deterministic per-game seeds), C2 (multi-seed-averaged GE), D1 (hybrid-action ban) | Engine done: **carpet 0.355** (above plan goal), **menger 0.329** (inside ±0.07 noise band of R18). Smoke gate over-rejected 5 menger seeds that evolution rediscovered — postmortem proposes two-tier smoke. Agent-team eval done: 30 verdicts (pilot 6 + production 24), production mean 4.375/10 |
| 20 | 3-substrate rule-family-comparator (menger / carpet / grid) with pie rule + S2 two-tier smoke + R8 family revival attempt | **Depth record:** menger `5f5c72e15220` hits 0.894 strategic depth (prior max ~0.55). **R8 family didn't generalise** — every connection-win seed mutated to threshold-race within 5 generations. **15-seed σ destabilises rankings** — original top menger game fell to 7th of 9 under honest re-scoring. **Pie effectiveness unmeasurable** — crossover bug zeroed pie on most descendants. Agent-team eval: 35 verdicts (5 teams × 7 games) |
| 8 replay | Re-evaluate R8 "Connection Go" anchor under R20's rubric to test the GE-bottleneck hypothesis | Anchor recalibrated: R8 scored 4.10 ± 1.14 / 10 (range 2.5), sitting **mid-R20 corpus, not above it**. The February 8/10 anchor inflated by ~3.9 pts of rubric drift. The GE-bottleneck-on-pole-vault diagnosis collapses |
| 20.5 | Pie-effectiveness smoke (G4) with the crossover fix | 3/5 menger games pass seat-bias < 0.10 with pie; established the sampled seat-swap mirror-eval methodology all later probes reuse |
| 21 | Champion run under the full R20 stack + S5 elite re-eval | Top menger 0.177, tied with R20 within noise — no ceiling progress in 4 runs. S5 caught a 0.417→0.095 phantom elite. Agent-team eval (5 independent teams, 35 verdicts): **no game cleared 5.0**, campaign mean 3.69; **GE rank inverts at the extremes** (GE-top game ranked 6/7 by agents). **Decision rule fires: PIVOT + SATURATION** |
| 21 probe | Variance probe — is GE noise PPO instability? | No: menger PPO depth is stable (CV 0.12); the noise lives in GE's coarse estimators (3-sample non-triviality, 4-valued diversity). The planned "PPO-convergence filter" was misaimed *and* survivorship-biased — scrapped before any compute was spent on it |
| FC probe | **Field-Connect**: influence *is* the win condition (connect your sides through field-controlled cells), blind A/B vs the plateau baseline on hex W=22 | **NO-GO per pre-registered bars** (screen 2/4, blind +0.70 < +1.0) — but 2/2 blind teams prefer it at **4.15 ≈ R8 parity on its first build**, unanimously naming the interaction-forcing win condition. Lever validated; the r=2 blur + dead surround capture parameterization is what failed |
| Phase-1.5 | Rules-rethink slate on a sharpened r=1, ε=0.25 field: C1 flip-capture, C2 contested-terrain gate, C3 control-capture | **NO-GO at the mechanical screen.** C2 died at calibration (60%+ draws, komi immovable); C1/C3 1/4 signals + sanity FAIL. The inversion: **r=2 overlap is what makes control contestable** (control-flip rate 10.6 vs ~4.2 at r=1) — while C1's flip-capture itself fires exactly as designed (7.1 events/game vs surround's structural 0.000) |

Each run's SQLite database (~100 MB) is regenerable and not committed. Per-run evaluation reports are in `evaluation_report_run*.md`; R21's campaign report is [`evaluations/run21/SUMMARY.md`](evaluations/run21/SUMMARY.md), and the two probes publish go/no-go readouts at [`experiments/field_connect_probe/RESULTS.md`](experiments/field_connect_probe/RESULTS.md) and [`experiments/fc_phase15/RESULTS.md`](experiments/fc_phase15/RESULTS.md). The R8 replay (2026-05-14) is in [`evaluations/r8_replay/SUMMARY.md`](evaluations/r8_replay/SUMMARY.md).

For a plain-English narrative across runs 7–16, see [`SUMMARY.md`](SUMMARY.md). R17–R21 and the probe era are documented in their per-run reports and readouts rather than in SUMMARY (which has not been updated since R16).

A note on terminology: aigame's project framing is **games for AI agents, not for humans**. Verdict campaigns are written by **Claude-agent teams** playing the games and scoring agent-relevant strategic-depth properties — not anthropocentric quality. Earlier reports (R17, R19) used "human evaluation" as legacy wording; R20 and the R8 replay use "agent-team eval".

## R20 + R8 replay in summary

What R20 added or changed:

- **Depth record.** Menger `5f5c72e15220` hit 0.894 strategic depth — the deepest single game any aigame run has produced (prior R-run max ~0.55). Two more menger games cleared 0.79.
- **R8 revival failed.** All 12 starting seeds were `capture + connection` (the R8 family). Within 5 generations, every substrate had mutated away from connection toward threshold-race. Connection-win seeds with pie active scored ~0 across all substrates.
- **Ranking instability under honest re-scoring.** When the top games were re-evaluated under 15-seed σ instead of 3-seed σ, the original first-place menger game fell to 7th of 9. The "R20 menger beat R19 menger" claim from the initial leaderboard didn't survive.
- **Pie rule effectiveness — unmeasurable.** A crossover bug zeroed the `pie_rule` flag on most descendants mid-run. Fix landed in `ac9e642`. An R20.5 menger-only run is the cheapest path to a clean answer.
- **Agent-team eval.** 35 verdicts (5 evaluator-teams × 7 games, Option-C slate, 2026-05-09).

Then the R8 anchor itself was re-checked:

- **R8 replay (2026-05-14).** Re-evaluated "Connection Go" (`d4015a646ae3`, R8 top-1) under R20's rubric with 5 production teams. Mean **4.10 ± 1.14 / 10**, range 2.5 — sitting mid-R20 corpus, not above it. The February 8/10 anchor inflated by ~3.9 pts of rubric drift between scoring regimes.
- **The GE-bottleneck-on-pole-vault diagnosis collapses.** R19's "GE under-rewards depth" finding stands (depth-rich games rank low on GE), but the framing where R8 was a genuine ceiling the metric couldn't reach is gone. R21 will resume without redesigning GE on the original bottleneck basis.

## The pivot era (R21 → probes)

R21 ended the GE-evolution regime: two consecutive campaigns under 5.0, GE anti-correlating with agent-judged depth, and a variance probe showing the noise lives in GE's own estimators, not in PPO. The pre-committed decision rule fired (PIVOT + SATURATION), and the project switched from *evolving against a metric* to *testing rule levers directly* with pre-registered experiments:

- **The Field-Connect probe** (2026-06-09) asked the smallest decisive version of the pivot's rule question: does putting influence *inside the win condition* — you win by connecting your sides through cells your field controls — force the interaction the plateau games lack? Registered answer: NO-GO on the bars, but the strongest positive signal since R8 — both blind teams independently preferred it (4.15 ≈ R8 parity on a first build) and named the interaction-forcing win condition unprompted ([readout](experiments/field_connect_probe/RESULTS.md)).
- **Phase-1.5** (2026-06-10) rebuilt the rules per the probe's critique — sharper field (r=1, ε=0.25) and three capture/terrain mechanics anchored in published games (Sygo, Tumbleweed, Gonnect). Registered answer: NO-GO at the mechanical screen, with the experiment refuting its own premise: the r=2 "blur" the critique targeted is precisely what makes control contestable. The flip-capture mechanic itself works — 7.1 capture events/game where surround managed 0.000 ([readout](experiments/fc_phase15/RESULTS.md)).

Net state: a validated lever (influence-in-the-win-condition), a working capture mechanic (field-flip), a proven-deterministic comparison harness, and one sharply-posed open combination (flip-capture on the r=2 field) — with the registered next step being a new win-condition family or QD selection.

## Tech stack

- **Python 3.12+**, SQLite for run state and genealogy
- **PyTorch** for PPO self-play agents
- **Claude API** for multi-team evaluation
- Single-machine runs (M2 Mac). Wall-clock varies by substrate complexity: ~30 hr for menger, ~4.5 hr for carpet, <1 hr for the grid control. From R18 onwards, substrates run **in parallel** as independent processes.

## Honest state

**Working**
- V2 architecture, evolution loop, validation filter, LLM evaluation pipeline
- Engine bias issues (R13–R16) all closed; symmetry holds across CA, threshold, connection, and step-ordering
- Scoring is deterministic per game (C1) and multi-seed-averaged (C2); D1 hybrid-action penalty is in scoring
- Multi-substrate parallel runs (R18+) — substrates run as independent processes with independent DBs
- **Pre-registered probe harness** — komi calibration gate → mechanical screen with signals every arm can move → blind agent A/B with sealed labels and locked decision rules; determinism validated by bit-identical A0/A1 retraining across experiments
- **Field mechanics in the engine** (field-connection win, flip/replace captures, control-gated placement) — all additive, init-guarded, and legacy-bit-identical, with a memoized influence-kernel cache giving a ~100–500× field-recompute speedup

**In progress**
- **The pivot menu.** Phase-1.5's registered NO-GO escalates past the Field-Connect family: the next move is either a different win-condition family or the Quality-Diversity (MAP-Elites) selection work — replacing GE as the selection signal entirely (R21 showed GE *anti-correlating* with agent-judged depth at the extremes).
- **Recorded but unregistered candidate:** flip-capture on the r=2 field — the one combination both probes individually validated but never tested together (phase-1.5 RESULTS §3.5). Running it would be a deliberate, logged exception to the registered consequence.
- **Kernel-cache memory cap** before any evolution-scale run: the new influence-kernel cache is unbounded and would retain ~100–250 MB over an R21-scale population.

**Known limits**
- Agents use flat MLP policies — no spatial inductive bias, which caps strategic depth on larger boards and likely contributes to the fractal-substrate PPO collapse seen in R17
- Evaluation is the rate limiter (30–60 min per game via Claude-agent teams; only top 3–6 candidates per run get fully scored)
- The Go Essence metric does not fully track agent-team verdicts. Every run since R13 has produced cases where GE rank order inverts under eval; R19+R20 showed GE under-rewards strategic depth, and R21 showed the inversion at both extremes (GE-top ranked 6/7 by agents; a GE-last game tied 1st on design). GE is being retired as the selection signal in the pivot.
- The R8 "Connection Go" champion was the project's nominal anchor at 8/10. The R8 replay under R20's rubric (2026-05-14) re-scored it at 4.10 — meaning the 8/10 was inflated by rubric drift, not that subsequent runs failed to match a real ceiling. The genuine question is no longer "why hasn't anything beaten R8" but "what does the corpus look like once the anchor is honestly normalised."

## Running it

```bash
pip install -r requirements.txt
python run.py
```

See `config.py` for population size, generation count, training budget, dimensionality, and CA / substrate probability knobs. R18+ uses per-substrate driver scripts in `experiments/` for parallel launches.

## Minimum reading list

If you want to understand the project end-to-end, open these in order:

1. [`SUMMARY.md`](SUMMARY.md) — plain-English narrative covering runs 7–16. **Stale beyond R16**; later work is in the per-run reports and probe readouts.
2. [`analysis_post_r21.md`](analysis_post_r21.md) — why the GE-evolution regime was declared saturated, and the pivot's reasoning. The single best current-state document.
3. [`experiments/field_connect_probe/RESULTS.md`](experiments/field_connect_probe/RESULTS.md) and [`experiments/fc_phase15/RESULTS.md`](experiments/fc_phase15/RESULTS.md) — the two pre-registered probe readouts; together they define where the project stands.
4. [`dimensionality_and_go_essence_analysis.txt`](dimensionality_and_go_essence_analysis.txt) — why V2 converged to Go × Hex, and what the search grammar was missing. Sets up the dimension-as-axis pivot that became R18.
5. [`cellular_automata_proposal.txt`](cellular_automata_proposal.txt) — why CA was the V3 generative substrate.
6. [`evaluation_report_run19.md`](evaluation_report_run19.md) — representative end-to-end evolution-run report (carpet + menger under C1 + C2 + D1 scoring); R21's campaign report is [`evaluations/run21/SUMMARY.md`](evaluations/run21/SUMMARY.md).
7. [`run.py`](run.py) — the orchestration: config → generation → training → evaluation → next gen.
8. [`game_engine/engine_v2.py`](game_engine/engine_v2.py) — how games actually execute. `step()` is where all rule application happens.
