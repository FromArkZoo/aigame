"""Inference probes that read trained-agent behaviour for scoring.

The trainer produces logits transiently inside the PPO update minibatch
(`training/trainer.py:427`) but does not persist per-ply policy
distributions. To compute distribution-level statistics — e.g. the gap
between the top-ranked move and the second-ranked move per ply — we need
a fresh inference pass over self-play rollouts. This module is the home
for those probes.

Currently exposes:
  - `planning_horizon_from_rollouts(game, trained_agents, n_rollouts)`:
    R21 S2 metric. Mean of (top1_prob − top2_prob) across legal moves at
    every ply of `n_rollouts` self-play games between two trained
    policies. High values → top action dominates → confident lookahead.
    Low values → top moves are interchangeable → little planning signal.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import torch
import torch.nn.functional as F

from game_engine.engine_v2 import GameEngineV2

if TYPE_CHECKING:
    from game_engine.game_def_v2 import GameDefV2
    from training.agent import PolicyNetwork


def planning_horizon_from_rollouts(
    game: "GameDefV2",
    trained_agents: "list[PolicyNetwork]",
    n_rollouts: int = 20,
    seed: int = 0,
    max_steps_per_rollout: int | None = None,
) -> float:
    """Mean (top1 − top2) softmax gap over legal moves, averaged across plies.

    For each rollout, both agents play themselves (`trained_agents[0]` as
    P1, `trained_agents[1]` as P2 — the standard self-play seating). At
    every ply we:

    1. Build a legal-move boolean mask from `engine.get_legal_actions()`.
    2. Call `agent.forward(obs, legal_mask)` so illegal logits are −∞.
    3. Softmax → probability over legal actions only (illegals at ~0).
    4. Sort the legal probs descending. Take the top two. Record
       `top1 − top2`.
    5. Sample an action (non-deterministic) and step the engine.

    The returned scalar is the mean gap across every ply of every
    rollout — bounded in [0, 1].

    Interpretation:
      - **High (→ 1.0)**: trained policy strongly prefers a single move
        each ply. Decisions matter; the agent has learned distinguishing
        signal between move classes.
      - **Low (→ 0.0)**: the top moves are interchangeable. The R20
        agent-team verdict on `5f5c72e15220` (depth 0.894 but team-3 +
        team-4 dissent on planning) describes this regime: many opening
        families reach threshold in similar plies but each ply is 1-ply
        lookahead.

    Plies with fewer than 2 legal actions are skipped (no gap defined).

    Parameters
    ----------
    game : GameDefV2
        The game definition to score.
    trained_agents : list[PolicyNetwork]
        Length-2 list. Agent 0 plays P1; agent 1 plays P2.
    n_rollouts : int
        Number of self-play games to sample over.
    seed : int
        Seed for the per-ply action sampling RNG. Different seeds yield
        different rollouts (and slightly different gap means) but the
        statistic is a property of the policy, not the seed.
    max_steps_per_rollout : int, optional
        Override the engine's `max_game_steps`. Defaults to the engine's
        own ceiling.

    Returns
    -------
    float
        Mean gap in [0, 1].
    """
    if len(trained_agents) != 2:
        raise ValueError(
            f"planning_horizon_from_rollouts expects 2 agents, got {len(trained_agents)}"
        )

    engine = GameEngineV2(game)
    max_steps = max_steps_per_rollout or getattr(game, "max_game_steps", 200)

    rng = np.random.default_rng(seed)
    torch.manual_seed(int(seed))

    num_actions = game.num_actions
    gaps: list[float] = []

    for rollout_idx in range(n_rollouts):
        obs = engine.reset()
        step = 0
        done = False
        while not done and step < max_steps:
            legal = engine.get_legal_actions()
            if len(legal) == 0:
                break
            if len(legal) < 2:
                # No gap to measure — single forced move. Take it and continue.
                action = legal[0]
                obs, _r, done, _info = engine.step(action)
                step += 1
                continue

            current_player = engine.get_current_player()  # 0 or 1 (0-indexed)
            agent = trained_agents[current_player]

            x = torch.as_tensor(obs, dtype=torch.float32).unsqueeze(0)
            mask = torch.zeros(1, num_actions, dtype=torch.bool)
            mask[0, legal] = True

            logits, _value = agent.forward(x, legal_mask=mask)
            probs = F.softmax(logits.squeeze(0), dim=-1).detach().cpu().numpy()

            # Sort legal-action probs only; illegal entries are ~0 after
            # softmax-over-masked-logits but excluded explicitly for clarity.
            legal_probs = np.sort(probs[legal])[::-1]
            gap = float(legal_probs[0] - legal_probs[1])
            gaps.append(gap)

            # Sample next action from the same distribution so subsequent
            # plies reflect realistic self-play trajectories. Use numpy
            # RNG to keep determinism under the function-level seed.
            sampled_idx = int(rng.choice(len(legal), p=probs[legal] / probs[legal].sum()))
            action = int(legal[sampled_idx])
            obs, _r, done, _info = engine.step(action)
            step += 1

    if not gaps:
        return 0.0
    return float(np.mean(gaps))
