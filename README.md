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

Top candidates are then evaluated by **five independent Claude agent teams** that each play three full head-to-head games, produce strategy guides, and score across five axes (strategic depth, emergent complexity, balance, novelty, replayability). Every run is checkpointed to SQLite; every evaluation report lives in the repo.

## The research progression

The search has gone through three architectural generations, each prompted by the failure mode of the last:

| Gen | Approach | Outcome |
|---|---|---|
| **V1** | Unconstrained rule expression trees | Grammar too loose → degenerate games, no theoretical binding |
| **V2** | Structured rules on n-dim boards (placement, capture, propagation, win) | Games are playable, but the search converges to a **Go × Hex local optimum** |
| **V3 (current)** | **Cellular automata as rule substrate** — evolve the state-transition rule itself | Expands the grammar beyond human-designed mechanics |

The CA direction is laid out in [`cellular_automata_proposal.txt`](cellular_automata_proposal.txt). For a 3-state, hex-neighbourhood totalistic rule, the search space is `3^147` — a strict superset of everything the V2 grammar can express, because surround capture, outnumber capture, and propagation are all special cases of CA rules. Ko fights, gliders, propagation frontlines and self-replicating patterns all become possible as evolved behaviours rather than hand-coded components.

## Run history

Runs 7–12 form a clear iteration trail. Each row is a deliberate response to what the previous run revealed:

| Run | Focus | Discovery |
|---|---|---|
| 7–8 | V2 baseline | Go × Hex hybrid emerges as a strong local optimum (8/10 on LLM eval) |
| 9 | Larger populations | Confirmed Go × Hex isn't novel — it's just Go on a different topology |
| 10 | Added validation rules | **Ko fights emerged from a non-Go mechanism** (overwrite + outnumber) — a genuinely new discovery |
| 11 | Tightened constraints | Hex-focused, torus banned, run-10 failure modes folded into the validator |
| 12 | **First CA run** | Evolving the rule substrate itself (first results pending analysis) |

Each run's SQLite database (~100 MB) is regenerable and not committed. Evaluation reports live in [`evaluation_report_run10.md`](evaluation_report_run10.md) and per-team reports in `eval_run9_team*.md`.

## Tech stack

- **Python 3.12+**, SQLite for run state and genealogy
- **PyTorch** for PPO self-play agents
- **Claude API** for multi-team evaluation
- Single-machine runs (M2 Mac, ~18–36 h per run); a scaling plan for an island-model cloud setup is sketched in [`scaling_recommendations.txt`](scaling_recommendations.txt)

## Honest state

**Working**
- V2 architecture, evolution loop, validation filter, LLM evaluation pipeline, run-to-run iteration with lessons fed back into constraints

**In progress**
- Cellular automata substrate (Run 12, first results pending analysis)

**Known limits**
- Agents use flat MLP policies — no spatial inductive bias, which caps strategic depth on larger boards
- Evaluation is the rate limiter (30–60 minutes per game via LLM teams, so only top candidates are fully scored)
- The search has a clear Go × Hex attractor basin that CA is specifically designed to escape; if it doesn't, the 64-cell grid paradigm itself may be the limiting factor, not the grammar

## Running it

```bash
pip install -r requirements.txt
python run.py
```

See `config.py` for population size, generation count, training budget, dimensionality, and CA probability knobs.

## Minimum reading list

If you want to understand the project end-to-end, open these five files in order:

1. [`cellular_automata_proposal.txt`](cellular_automata_proposal.txt) — the current research direction, in prose. Explains *why* CA is the right generative substrate.
2. [`dimensionality_and_go_essence_analysis.txt`](dimensionality_and_go_essence_analysis.txt) — why V2 converged to Go × Hex, and what the search grammar was missing.
3. [`evaluation_report_run10.md`](evaluation_report_run10.md) — a concrete example of what the LLM evaluation pipeline produces (ko fights, failure modes, validation rules inferred from losses).
4. [`run.py`](run.py) — the orchestration: config → generation → training → evaluation → next gen.
5. [`game_engine/engine_v2.py`](game_engine/engine_v2.py) — how games actually execute. `step()` is where all rule application happens.
