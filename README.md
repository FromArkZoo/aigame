# Genesis Engine

**A systematic study of whether evolutionary search combined with LLM-as-judge evaluation can discover novel abstract strategy games with genuine strategic depth.**

This project evolves original two-player games on n-dimensional topological boards, scored by a metric — **Go Essence** — that balances strategic richness against rule complexity:

```
GoEssence = (strategic_depth × strategic_diversity) / rule_complexity
```

The hypothesis: can unguided search on a constrained rule grammar rediscover the depth-from-simplicity property that makes Go, Chess and Hex interesting — and ideally find something new that didn't come from human intuition?

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
| **V3.5 (current)** | **Fractal substrates** — vary the *board topology's* Hausdorff dimension as a search axis | R18 showed menger sponge (dim 2.727) lifts above flat-grid champions; R19 first end-to-end test under deterministic, multi-seed scoring + hybrid-action ban |

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
| 19 | Champion run on menger + carpet under C1 (deterministic per-game seeds), C2 (multi-seed-averaged GE), D1 (hybrid-action ban) | Engine done: **carpet 0.355** (above plan goal), **menger 0.329** (inside ±0.07 noise band of R18). Smoke gate over-rejected 5 menger seeds that evolution rediscovered — postmortem proposes two-tier smoke. Pilot human eval done (6 verdicts, mean 4.83); 24 production verdicts pending |

Each run's SQLite database (~100 MB) is regenerable and not committed. Per-run evaluation reports are in `evaluation_report_run*.md`; the most recent is [`evaluation_report_run19.md`](evaluation_report_run19.md).

For a plain-English narrative across runs 7–16, see [`SUMMARY.md`](SUMMARY.md). R17–R19 are documented in their per-run evaluation reports rather than in SUMMARY (which has not been updated since R16).

## R19 in summary

What this run added or changed:

- **Carpet works.** R19 carpet's top game (`ce3a09e05cef`) reaches GE 0.355 under the new stricter scoring — above the 0.30 plan goal and slightly above R18's rescued estimate.
- **Menger lands inside R18's noise band.** Top game (`1f9191b5d4e6`) at 0.329, within ±0.07 of R18 menger top under directly-comparable scoring. The R19 plan's stretch goal of 0.35 was missed by 0.022 — explained in [`R19_postmortem.md`](R19_postmortem.md) (smoke gate over-rejected the family that wins).
- **Smoke calibration finding.** The pre-launch PPO smoke gate dropped 9 of 19 seeds; 5 of those drops were the menger in-family seeds that R19 evolution then rediscovered via crossover at an estimated ~4–5 generations of extra cost. R19_postmortem.md proposes a two-tier smoke for R20+ champion runs.
- **Hybrid actions confirmed dead.** D1 ban (0.2× fitness penalty) kept all 20 hybrid-action games across the run far below the leaderboard. No top-10 games on either substrate use move actions.
- **Preliminary human-eval signal.** 6 pilot verdicts (1 per game), pilot mean 4.83/10 — in R17-best range (4.14). **Surprise: menger rank-3 (`5048f71b62fd`, surround capture, GE rank #3) topped the pilot at 6/10.** If the GE metric ranks this game #3 but humans rank it #1, the metric is under-weighting Go-family strategic depth. **Preliminary — confirmation depends on the 24 production verdicts still to run.**

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

**In progress**
- R19 human eval — pilot done (6 verdicts), production 24 verdicts pending. R20 scope decision waits on full eval.
- Open question from the pilot: does Go-style surround capture create richer human-judged play than outnumber-2? If yes, the GE metric needs a Go-family weighting term.

**Known limits**
- Agents use flat MLP policies — no spatial inductive bias, which caps strategic depth on larger boards and likely contributes to the fractal-substrate PPO collapse seen in R17
- Evaluation is the rate limiter (30–60 min per game via LLM teams; only top 3–6 candidates per run get fully scored)
- The Go Essence metric still does not reliably track human judgment. Every run since R13 has produced cases where rank order inverts under human eval. R19 is the first run where C1+C2 ought to make GE comparable across runs at all — the pilot menger-rank-3 finding suggests further calibration work is needed.
- The R8 "Connection Go" champion (8/10) has not been matched by any subsequent run. Whether this means R8 was a lucky early hit, a genuine ceiling on the current grammar+architecture, or recoverable with a Go-family-weighted metric is unresolved.

## Running it

```bash
pip install -r requirements.txt
python run.py
```

See `config.py` for population size, generation count, training budget, dimensionality, and CA / substrate probability knobs. R18+ uses per-substrate driver scripts in `experiments/` for parallel launches.

## Minimum reading list

If you want to understand the project end-to-end, open these in order:

1. [`SUMMARY.md`](SUMMARY.md) — plain-English narrative covering runs 7–16. **Stale beyond R16**; R17–R19 are in their per-run reports below.
2. [`cellular_automata_proposal.txt`](cellular_automata_proposal.txt) — why CA was the V3 generative substrate.
3. [`dimensionality_and_go_essence_analysis.txt`](dimensionality_and_go_essence_analysis.txt) — why V2 converged to Go × Hex, and what the search grammar was missing. Sets up the dimension-as-axis pivot that became R18.
4. [`evaluation_report_run19.md`](evaluation_report_run19.md) — most recent end-to-end run report. Carpet + menger under C1 + C2 + D1 scoring. Includes the smoke-gate retrospective that motivated R19_postmortem.
5. [`R19_postmortem.md`](R19_postmortem.md) — proposed two-tier smoke calibration for R20+. Reads in 5 minutes.
6. [`run.py`](run.py) — the orchestration: config → generation → training → evaluation → next gen.
7. [`game_engine/engine_v2.py`](game_engine/engine_v2.py) — how games actually execute. `step()` is where all rule application happens.
