"""Phase-1.5 rules-rethink — engine tests for field_flip / field_replace
captures and the not_enemy_controlled placement constraint.

Spec: docs/superpowers/specs/2026-06-10-field-connect-phase15-design.md.
"""
from __future__ import annotations

import numpy as np  # noqa: F401

from game_engine.engine_v2 import GameEngineV2
from game_engine.game_def_v2 import GameDefV2
from game_engine.rules import (
    CAPTURE_TYPES,
    PLACEMENT_CONSTRAINTS,
    ActionRule,
    CaptureRule,
    PlacementRule,
    PropagationRule,
    TurnStructure,
    WinCondition,
)


def make_p15_game(
    *,
    s: int = 6,
    control_margin: float = 0.25,
    radius: int = 1,
    decay: float = 0.5,
    capture_type: str = "none",
    placement_constraint: str = "anywhere",
    max_turns: int = 60,
) -> GameDefV2:
    """Minimal hex_rhombus phase-1.5 game. P1 connects dim 1, P2 dim 0."""
    return GameDefV2(
        game_id=f"p15_test_{capture_type}_{placement_constraint}",
        num_dimensions=2,
        axis_size=s,
        topology_type="hex_rhombus",
        placement_rule=PlacementRule(
            target="empty", constraint=placement_constraint,
        ),
        capture_rule=CaptureRule(capture_type=capture_type),
        propagation_rule=PropagationRule(
            prop_type="influence", radius=radius, strength=1.0, decay=decay,
        ),
        win_condition=WinCondition(
            condition_type="field_connection",
            target_dimension=1,
            target_dimension_p2=0,
            max_turns=max_turns,
            control_margin=control_margin,
        ),
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
        pie_rule=False,
    )


def _engine(game: GameDefV2) -> GameEngineV2:  # noqa: F401
    e = GameEngineV2(game)
    e.reset()
    return e


def test_new_rule_types_registered() -> None:
    assert "field_flip" in CAPTURE_TYPES
    assert "field_replace" in CAPTURE_TYPES
    assert "not_enemy_controlled" in PLACEMENT_CONSTRAINTS


def test_new_rule_types_roundtrip() -> None:
    g = make_p15_game(capture_type="field_flip")
    g2 = GameDefV2.from_dict(g.to_dict())
    assert g2.capture_rule.capture_type == "field_flip"
    g = make_p15_game(placement_constraint="not_enemy_controlled")
    g2 = GameDefV2.from_dict(g.to_dict())
    assert g2.placement_rule.constraint == "not_enemy_controlled"
