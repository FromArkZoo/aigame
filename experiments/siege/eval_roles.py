"""Cross-seed role-matrix evaluation for asymmetric arms (prereg Stage 1).

m_siege roles are seat-locked (pie OFF): P1 = Maker (field_connection),
P2 = Breaker (capture_quota / timeout). So "role-aware" evaluation means
seat-aware with NO seat swapping — the Maker policy is trainer.agents[0]
and the Breaker policy is trainer.agents[1], always played in their own
seats.

End-cause attribution reads the engine's own authoritative state after
each game (engine._winner in {1, 2, None}, engine._quota_ticks,
engine._ended_by_max_turns) rather than play_game's reward-derived winner
— the Stage-1 gates (quota share, timeout share) key off exactly these
engine flags (see engine_v2.py SIEGE quota accounting / _end_by_max_turns).

Reproducibility note: PolicyNetwork.select_action(deterministic=False)
samples from torch.distributions.Categorical, which draws from torch's
GLOBAL rng. play_pair therefore accepts an optional ``seed`` and calls
torch.manual_seed(seed) at the top; role_matrix passes a per-pairing seed
derived from the two trainers' seeds so the matrix is reproducible
independent of call order. RandomAgent carries its own random.Random and
ignores the deterministic flag, so trained-deterministic-vs-random games
need no torch seeding (argmax draws nothing from the global rng).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from game_engine.factory import create_engine  # noqa: E402
from training.utils import RandomAgent, play_game  # noqa: E402

# ---------------------------------------------------------------------------
# Pre-registered Stage-1 constants — experiments/siege/PREREGISTRATION.md
# ("Stage 1 calibration", gate (1) per-role skill gates). Not altered after data.
# ---------------------------------------------------------------------------
GAMES_PER_PAIR = 22  # 3x3 x 22 = 198 ~= 200 (prereg n≈200/cell)
TVR_PASS = 0.80      # role tvr must be >= this ...
TVR_MARGIN = 0.15    # ... AND >= that role's random-vs-random baseline + this
COLLAPSE_TVR = 0.20  # role tvr below this = collapsed seed -> fresh-seed rerun


def role_bias_from_matrix(matrix) -> float:
    """|mean Maker win rate - 0.5| over the cross-seed matrix."""
    return float(abs(np.mean(np.asarray(matrix, dtype=np.float64)) - 0.5))


def play_pair(game, maker_agent, breaker_agent, n: int = GAMES_PER_PAIR,
              seed: int | None = None) -> tuple[float, dict]:
    """Maker win rate over n games (maker = P1 seat, breaker = P2 seat).

    Stochastic play (deterministic=False) — calibration measures the policy
    DISTRIBUTION, mirroring sampled_mirror_eval (field_connect_probe
    calibrate.py). ``seed`` (optional) is fed to torch.manual_seed for
    reproducible Categorical sampling; see module docstring.

    Returns (maker_win_rate, tallies) where tallies = dict(
        quota_wins=, timeout_games=, breaker_wins=, maker_wins=, draws=, n=).
    Quota win  = engine winner == 2 AND quota reached
                 (engine._quota_ticks >= wc.capture_quota).
    Timeout    = engine._ended_by_max_turns (timeout_winner routes the win).
    """
    if seed is not None:
        torch.manual_seed(seed)
    engine = create_engine(game)
    wc = game.win_condition
    quota = getattr(wc, "capture_quota", 0)
    tallies = dict(quota_wins=0, timeout_games=0, breaker_wins=0,
                   maker_wins=0, draws=0, n=n)

    for _ in range(n):
        play_game(engine, maker_agent, breaker_agent,
                  deterministic=False, max_steps=game.max_game_steps)
        w = engine._winner  # 1, 2, or None — engine-authoritative
        if w == 1:
            tallies["maker_wins"] += 1
        elif w == 2:
            tallies["breaker_wins"] += 1
            if quota > 0 and engine._quota_ticks >= quota:
                tallies["quota_wins"] += 1
        else:
            tallies["draws"] += 1
        if engine._ended_by_max_turns:
            tallies["timeout_games"] += 1

    return tallies["maker_wins"] / max(n, 1), tallies


def role_matrix(game, trainers,
                games_per_pair: int = GAMES_PER_PAIR,
                ) -> tuple[list[list[float]], dict]:
    """k x k Maker-win-rate matrix over trainers (Maker policy from trainer
    i = trainers[i].agents[0]; Breaker policy from trainer j =
    trainers[j].agents[1]) + end-cause tallies aggregated across all
    pairings. Prereg: k=3 seeds, 3x3 x 22 = 198 games per cell.
    """
    k = len(trainers)
    matrix = [[0.0] * k for _ in range(k)]
    agg = dict(quota_wins=0, timeout_games=0, breaker_wins=0,
               maker_wins=0, draws=0, n=0)
    for i, ti in enumerate(trainers):
        for j, tj in enumerate(trainers):
            # Per-pairing torch seed from the trainers' own seeds: stable
            # under reserve-seed replacement (a replaced seed changes the
            # stream — it is a different policy pair).
            pair_seed = 100_000 + ti.seed * 1_000 + tj.seed
            wr, tallies = play_pair(
                game, ti.agents[0], tj.agents[1],
                n=games_per_pair, seed=pair_seed,
            )
            matrix[i][j] = wr
            for key in agg:
                agg[key] += tallies[key]
    return matrix, agg


def per_role_tvr(game, trainer, n: int = 100) -> dict:
    """Role-aware trained-vs-random win rates + random-vs-random baselines.

    Trained sides play deterministic=True (mirrors trainer.evaluate's tvr
    convention — play_game forwards the flag to both agents but RandomAgent
    ignores it, so the random opponent stays stochastic). Baselines use two
    distinct RandomAgents (mirrors trainer.evaluate's heuristic probe).

    Returns dict(maker_tvr=, breaker_tvr=, maker_baseline=, breaker_baseline=,
                 maker_pass=, breaker_pass=, collapsed=, n=).
    Gates (PREREGISTRATION.md Stage 1, gate (1)):
      role pass  = tvr >= TVR_PASS and tvr >= baseline + TVR_MARGIN
      collapsed  = either role tvr < COLLAPSE_TVR
    """
    engine = create_engine(game)
    max_steps = game.max_game_steps
    # Seed derivation mirrors trainer.evaluate (trainer.py:646-647).
    # rand_a is DELIBERATELY reused across the maker-eval, breaker-eval and
    # baseline loops below (its random.Random stream just continues), the
    # same way trainer.evaluate reuses its probe agents — not an oversight.
    # rand_b exists so the random-vs-random baseline pits two DISTINCT
    # agents, mirroring trainer.evaluate's heuristic seat-balance probe.
    rand_a = RandomAgent(seed=trainer.seed * 7 + 11)
    rand_b = RandomAgent(seed=trainer.seed * 7 + 23)

    maker_wins = 0
    for _ in range(n):
        w, _, _ = play_game(engine, trainer.agents[0], rand_a,
                            deterministic=True, max_steps=max_steps)
        maker_wins += int(w == 0)  # play_game winner is seat-indexed (0 = P1)

    breaker_wins = 0
    for _ in range(n):
        w, _, _ = play_game(engine, rand_a, trainer.agents[1],
                            deterministic=True, max_steps=max_steps)
        breaker_wins += int(w == 1)

    base_maker = 0
    base_breaker = 0
    for _ in range(n):
        w, _, _ = play_game(engine, rand_a, rand_b,
                            deterministic=False, max_steps=max_steps)
        base_maker += int(w == 0)
        base_breaker += int(w == 1)

    nn = max(n, 1)
    maker_tvr = maker_wins / nn
    breaker_tvr = breaker_wins / nn
    maker_baseline = base_maker / nn
    breaker_baseline = base_breaker / nn
    return dict(
        maker_tvr=maker_tvr,
        breaker_tvr=breaker_tvr,
        maker_baseline=maker_baseline,
        breaker_baseline=breaker_baseline,
        maker_pass=(maker_tvr >= TVR_PASS
                    and maker_tvr >= maker_baseline + TVR_MARGIN),
        breaker_pass=(breaker_tvr >= TVR_PASS
                      and breaker_tvr >= breaker_baseline + TVR_MARGIN),
        collapsed=(maker_tvr < COLLAPSE_TVR or breaker_tvr < COLLAPSE_TVR),
        n=n,
    )
