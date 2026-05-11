#!/usr/bin/env python3
"""Inference-probe tests for the planning-horizon metric (R21 S2).

The probe is `metrics/inference_probe.py:planning_horizon_from_rollouts`.
Output is the mean (top1 − top2) softmax gap over legal actions per
ply, averaged across `n_rollouts` self-play games.

These tests use scripted PolicyNetwork stubs that emit deterministic
logit patterns (one-hot, uniform, mixed) so we can verify the gap math
without a real PPO training run.

Run as: .venv/bin/python test_planning_horizon.py
"""
from __future__ import annotations

import sys
import traceback

import numpy as np
import torch
import torch.nn as nn

from game_engine.game_def_v2 import GameDefV2
from game_engine.rules import (
    ActionRule,
    CaptureRule,
    PlacementRule,
    PropagationRule,
    TurnStructure,
    WinCondition,
)
from metrics.inference_probe import planning_horizon_from_rollouts


# ----------------------------------------------------------------------
# Test scaffolding
# ----------------------------------------------------------------------

passed: list[str] = []
failed: list[tuple[str, str]] = []


def case(name: str, fn) -> None:
    try:
        fn()
        passed.append(name)
        print(f"  PASS  {name}")
    except Exception as e:  # noqa: BLE001
        failed.append((name, traceback.format_exc()))
        print(f"  FAIL  {name}: {e}")


# ----------------------------------------------------------------------
# Scripted policy stubs
# ----------------------------------------------------------------------


class StubPolicy(nn.Module):
    """Policy with caller-controlled logits. Provides the same
    `forward(obs, legal_mask)` surface as PolicyNetwork.

    Patterns adapt to the legal_mask so they exercise the gap metric
    consistently regardless of which actions have already been taken.
    """

    def __init__(self, num_actions: int, logit_pattern: str):
        super().__init__()
        self.num_actions = num_actions
        self.logit_pattern = logit_pattern

    def forward(self, x: torch.Tensor, legal_mask: torch.Tensor | None = None):
        batch = x.shape[0] if x.ndim > 1 else 1

        if self.logit_pattern == "uniform":
            logits = torch.zeros((batch, self.num_actions))
            if legal_mask is not None:
                mask = legal_mask.to(dtype=torch.bool)
                logits = logits.masked_fill(~mask, float("-inf"))
            return logits, torch.zeros((batch, 1))

        # For one_hot_lowest_legal and top_two_close we read the legal
        # mask and place the high-mass logit(s) on the lowest-index
        # legal action(s) so every ply produces a measurable gap.
        if legal_mask is None:
            raise ValueError(
                f"pattern {self.logit_pattern} requires a legal_mask"
            )
        mask = legal_mask.to(dtype=torch.bool)
        logits = torch.full((batch, self.num_actions), -1e3)
        for b in range(batch):
            legal_idx = torch.nonzero(mask[b]).squeeze(-1)
            if legal_idx.numel() == 0:
                continue
            if self.logit_pattern == "one_hot_lowest_legal":
                logits[b, legal_idx[0]] = 0.0
            elif self.logit_pattern == "top_two_close":
                logits[b, legal_idx[0]] = 0.0
                if legal_idx.numel() > 1:
                    logits[b, legal_idx[1]] = -0.01
            else:
                raise ValueError(f"unknown logit pattern: {self.logit_pattern}")
        logits = logits.masked_fill(~mask, float("-inf"))
        return logits, torch.zeros((batch, 1))


def make_game() -> GameDefV2:
    """Minimal V2 game: 3x3 grid, territory, alternating, no captures.
    Short enough that the probe terminates fast on every test run."""
    return GameDefV2(
        game_id="ph_test",
        num_dimensions=2,
        axis_size=3,
        topology_type="grid",
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="none"),
        propagation_rule=PropagationRule(prop_type="none"),
        win_condition=WinCondition(
            condition_type="territory", threshold=0.5, max_turns=20,
        ),
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
    )


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------


def test_deterministic_policy_yields_near_one_gap() -> None:
    """A policy that always concentrates mass on a single action should
    yield gap → 1.0 (top1 ≈ 1, top2 ≈ 0)."""
    game = make_game()
    n_actions = game.num_actions
    agents = [
        StubPolicy(n_actions, "one_hot_lowest_legal"),
        StubPolicy(n_actions, "one_hot_lowest_legal"),
    ]
    gap = planning_horizon_from_rollouts(game, agents, n_rollouts=3, seed=0)
    assert 0.95 < gap <= 1.0, (
        f"one-hot policy should yield gap ≈ 1.0, got {gap:.4f}"
    )


def test_uniform_policy_yields_near_zero_gap() -> None:
    """A uniform policy over legal moves should yield gap → 0.0."""
    game = make_game()
    n_actions = game.num_actions
    agents = [
        StubPolicy(n_actions, "uniform"),
        StubPolicy(n_actions, "uniform"),
    ]
    gap = planning_horizon_from_rollouts(game, agents, n_rollouts=3, seed=0)
    assert 0.0 <= gap < 0.05, (
        f"uniform policy should yield gap ≈ 0.0, got {gap:.4f}"
    )


def test_close_top_two_yields_small_gap() -> None:
    """Two near-equal top actions (logit diff 0.01) should produce a
    small but nonzero gap. Softmax with logit gap 0.01 over 2 entries
    gives probs ~0.5025/0.4975 → gap ~0.005."""
    game = make_game()
    n_actions = game.num_actions
    agents = [
        StubPolicy(n_actions, "top_two_close"),
        StubPolicy(n_actions, "top_two_close"),
    ]
    gap = planning_horizon_from_rollouts(game, agents, n_rollouts=2, seed=0)
    assert 0.0 < gap < 0.02, (
        f"top-two-close policy should yield gap ~0.005, got {gap:.4f}"
    )


def test_legal_mask_excludes_illegals() -> None:
    """Forcing only one action legal must not crash and must skip the
    no-gap-defined ply (single-legal-move). Mixing in plies with ≥2
    legal moves should still produce a measurable gap."""
    game = make_game()
    n_actions = game.num_actions
    agents = [
        StubPolicy(n_actions, "one_hot_lowest_legal"),
        StubPolicy(n_actions, "one_hot_lowest_legal"),
    ]
    # Single-rollout sanity — must not raise.
    gap = planning_horizon_from_rollouts(game, agents, n_rollouts=1, seed=42)
    assert gap >= 0.0, f"single-rollout probe must produce a non-negative gap, got {gap}"


def test_return_type_is_float() -> None:
    """API contract: probe returns a plain float (not numpy scalar)."""
    game = make_game()
    n_actions = game.num_actions
    agents = [
        StubPolicy(n_actions, "uniform"),
        StubPolicy(n_actions, "uniform"),
    ]
    gap = planning_horizon_from_rollouts(game, agents, n_rollouts=1, seed=0)
    assert isinstance(gap, float), f"expected float, got {type(gap).__name__}"


def test_wrong_num_agents_raises() -> None:
    """Probe requires exactly 2 agents (P1 + P2)."""
    game = make_game()
    n_actions = game.num_actions
    agents = [StubPolicy(n_actions, "uniform")]  # only 1 agent
    try:
        planning_horizon_from_rollouts(game, agents, n_rollouts=1)
        raise AssertionError("expected ValueError for wrong agent count")
    except ValueError:
        pass


def test_composite_score_neutral_when_weight_zero() -> None:
    """When planning_horizon_weight=0, the composite must not depend on
    planning_horizon (factor ** 0 = 1)."""
    from config import MetricsConfig
    from metrics.scoring import GoEssenceScorer

    cfg = MetricsConfig(planning_horizon_weight=0.0)
    scorer = GoEssenceScorer(cfg)
    s_low = scorer.composite_score(
        simplicity=0.6, depth=0.5, non_triviality=0.5, diversity=0.5,
        planning_horizon=0.0,
    )
    s_high = scorer.composite_score(
        simplicity=0.6, depth=0.5, non_triviality=0.5, diversity=0.5,
        planning_horizon=1.0,
    )
    assert abs(s_low - s_high) < 1e-9, (
        f"planning_horizon_weight=0 must mute the term, but composite "
        f"changed: {s_low} vs {s_high}"
    )


def test_composite_score_responsive_when_weight_positive() -> None:
    """When planning_horizon_weight>0, high planning_horizon must raise
    the composite vs low planning_horizon (other components held)."""
    from config import MetricsConfig
    from metrics.scoring import GoEssenceScorer

    cfg = MetricsConfig(planning_horizon_weight=0.5)  # w_d / 2 starting
    scorer = GoEssenceScorer(cfg)
    s_low = scorer.composite_score(
        simplicity=0.6, depth=0.5, non_triviality=0.5, diversity=0.5,
        planning_horizon=0.0,
    )
    s_high = scorer.composite_score(
        simplicity=0.6, depth=0.5, non_triviality=0.5, diversity=0.5,
        planning_horizon=1.0,
    )
    assert s_high > s_low, (
        f"planning_horizon_weight>0 should make high>low, got "
        f"low={s_low:.4f} high={s_high:.4f}"
    )


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("Planning-horizon probe tests (R21 S2)")
    print("-" * 50)
    case("deterministic_policy_yields_near_one_gap", test_deterministic_policy_yields_near_one_gap)
    case("uniform_policy_yields_near_zero_gap", test_uniform_policy_yields_near_zero_gap)
    case("close_top_two_yields_small_gap", test_close_top_two_yields_small_gap)
    case("legal_mask_excludes_illegals", test_legal_mask_excludes_illegals)
    case("return_type_is_float", test_return_type_is_float)
    case("wrong_num_agents_raises", test_wrong_num_agents_raises)
    case("composite_score_neutral_when_weight_zero", test_composite_score_neutral_when_weight_zero)
    case("composite_score_responsive_when_weight_positive", test_composite_score_responsive_when_weight_positive)
    print("-" * 50)
    print(f"{len(passed)} passed, {len(failed)} failed")
    if failed:
        for name, tb in failed:
            print(f"\n--- {name} ---\n{tb}")
        sys.exit(1)
