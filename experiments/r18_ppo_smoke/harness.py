"""R18 B2 — 3000-episode PPO smoke harness.

R17's mechanical balance probe (random + greedy at 300 ep) cleared
`frac_C_fractal`, which then collapsed under PPO to 2-step games. The
mechanical probe measured "is this game balanced under non-learning
agents" — but it didn't measure "does PPO converge to non-degenerate
play." This harness adds the second check.

Each seed runs full self-play PPO for ``training_budget`` episodes
(default 3000) and is then evaluated by playing trained-vs-trained
games with **sampled** action selection (not deterministic argmax).
Sampled play matters: with deterministic=True the policy collapses to
identical 2-step games regardless of game quality — argmax over the
softmax tail is a numerical artifact, not a behavior signal. Sampling
preserves the trained distribution, which is what the evolution loop's
GE metrics measure during the actual run.

Two gates:

  * Length floor:   sampled_avg_length >= max(8, 0.10 * active_cells)
                    Catches policies that converge to truncated
                    openings — the R17 fractal failure mode.
  * Forced-win:     |greedy_p1_winrate - 0.5| <= 0.30
                    Catches structural seat bias surviving training
                    (greedy-vs-greedy seat-swap measures bias that's
                    a property of the game, not the trained policy).

Seeds that fail either gate are dropped before the R18 evolution kicks
off, so a substrate's per-substrate evolution doesn't waste compute on
seeds the engine has already shown will collapse.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np

from config import MetricsConfig, TrainingConfig
from game_engine.factory import create_engine
from game_engine.game_def_v2 import GameDefV2
from game_engine.topology import TopologicalSpace
from training.trainer import SelfPlayTrainer
from training.utils import play_game


SEAT_BIAS_THRESHOLD = 0.30  # |p1_wr - 0.5| above this -> forced-win drop
LENGTH_FLOOR_FRACTION = 0.10  # avg length must be >= 10% of active cells
LENGTH_FLOOR_MIN = 8  # ...but never below 8 (small-board floor)


@dataclass
class SmokeVerdict:
    """Result of one PPO smoke run on one seed game.

    ``passed`` is False iff at least one gate fired (see ``drop_reasons``).
    Numeric fields are kept on the verdict so the dim->fitness writeup can
    plot them without re-running the smoke pass.
    """

    game_id: str
    topology_type: str
    axis_size: int
    num_dimensions: int

    passed: bool
    drop_reasons: list[str]

    # Length gate (sampled trained-vs-trained play with seat-swap)
    sampled_avg_length: float
    length_floor: float
    active_cells: int

    # Forced-win gate
    greedy_p1_winrate: float
    seat_bias: float
    seat_bias_threshold: float

    # Auxiliary numbers from trainer.evaluate() — recorded for the writeup,
    # not gated. avg_game_length here is the deterministic-argmax measurement,
    # known to collapse to ~2 regardless of game quality (see module docstring).
    deterministic_avg_length: float
    trained_p0_winrate: float
    trained_vs_random_winrate: float
    heuristic_p1_winrate: float

    # Provenance
    training_budget: int
    eval_episodes: int
    seed: int
    elapsed_seconds: float

    extras: dict = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


def _active_cells(game: GameDefV2) -> int:
    """Count active (non-hole) cells. Falls back to total_cells when the
    topology isn't substrate-aware (grid, torus, hex, moore — no holes)."""
    holes = list(game.holes) if game.holes else None
    topo = TopologicalSpace(
        num_dimensions=game.num_dimensions,
        axis_size=game.axis_size,
        topology_type=game.topology_type,
        holes=holes,
    )
    return int(topo.num_active_cells)


def _sampled_trained_play_avg_length(
    trainer: SelfPlayTrainer,
    num_episodes: int,
    max_steps: int,
) -> float:
    """Trained-vs-trained sampled play with seat-swap. Returns avg game length.

    Deterministic argmax collapses to identical 2-step games on this engine
    regardless of training quality — see module docstring. Sampling preserves
    the trained policy distribution, which is what the GE metrics observe.
    """
    half = num_episodes // 2
    lengths: list[int] = []
    for i in range(num_episodes):
        engine = create_engine(trainer.game)
        if i < half:
            a0, a1 = trainer.agents[0], trainer.agents[1]
        else:
            a0, a1 = trainer.agents[1], trainer.agents[0]
        _, length, _ = play_game(
            engine, a0, a1, deterministic=False, max_steps=max_steps,
        )
        lengths.append(length)
    return float(np.mean(lengths)) if lengths else 0.0


def smoke_test(
    game: GameDefV2,
    *,
    training_budget: int = 3000,
    eval_episodes: int = 100,
    seed: int = 42,
) -> SmokeVerdict:
    """Run a 3000-ep PPO smoke on ``game``; return the verdict.

    Does not write to disk — callers persist the verdict if they want a
    record. ``run_smoke.py`` is the CLI wrapper that does.
    """
    cells = _active_cells(game)
    length_floor = max(float(LENGTH_FLOOR_MIN), LENGTH_FLOOR_FRACTION * cells)

    cfg = TrainingConfig(
        training_budget=training_budget,
        eval_episodes=eval_episodes,
    )
    mcfg = MetricsConfig(learning_curve_checkpoints=2)  # we don't need a fine curve

    trainer = SelfPlayTrainer(game, cfg, mcfg, seed=seed)
    max_steps = getattr(game, "max_game_steps", 200)

    t0 = time.time()
    trainer.train()
    eval_stats = trainer.evaluate(num_episodes=eval_episodes)
    sampled_len = _sampled_trained_play_avg_length(
        trainer, num_episodes=eval_episodes, max_steps=max_steps,
    )
    elapsed = time.time() - t0

    greedy_wr = float(eval_stats["greedy_p1_winrate"])
    seat_bias = abs(greedy_wr - 0.5)

    reasons: list[str] = []
    if sampled_len < length_floor:
        reasons.append(
            f"sampled_avg_length {sampled_len:.1f} < floor {length_floor:.1f} "
            f"(cells={cells})"
        )
    if seat_bias > SEAT_BIAS_THRESHOLD:
        reasons.append(
            f"seat bias |{greedy_wr:.2f} - 0.5| = {seat_bias:.2f} "
            f"> {SEAT_BIAS_THRESHOLD:.2f} (forced-win)"
        )

    return SmokeVerdict(
        game_id=game.game_id,
        topology_type=game.topology_type,
        axis_size=game.axis_size,
        num_dimensions=game.num_dimensions,
        passed=len(reasons) == 0,
        drop_reasons=reasons,
        sampled_avg_length=sampled_len,
        length_floor=length_floor,
        active_cells=cells,
        greedy_p1_winrate=greedy_wr,
        seat_bias=seat_bias,
        seat_bias_threshold=SEAT_BIAS_THRESHOLD,
        deterministic_avg_length=float(eval_stats["avg_game_length"]),
        trained_p0_winrate=float(eval_stats["p0_winrate"]),
        trained_vs_random_winrate=float(eval_stats["trained_vs_random_winrate"]),
        heuristic_p1_winrate=float(eval_stats["heuristic_p1_winrate"]),
        training_budget=training_budget,
        eval_episodes=eval_episodes,
        seed=seed,
        elapsed_seconds=elapsed,
    )


def load_game(path: str | Path) -> GameDefV2:
    """Load a GameDefV2 from a JSON file written by from_dict-compatible code."""
    p = Path(path)
    with open(p) as f:
        return GameDefV2.from_dict(json.load(f))
