"""Field-Connect probe — engine tests for the field_connection win condition.

Spec: docs/superpowers/specs/2026-06-07-field-connect-probe-design.md (v2).
"""
from __future__ import annotations

from game_engine.engine_v2 import GameEngineV2
from game_engine.game_def_v2 import GameDefV2
from game_engine.rules import (
    ActionRule,
    CaptureRule,
    PlacementRule,
    PropagationRule,
    TurnStructure,
    WinCondition,
)


def make_fc_game(
    *,
    s: int = 6,
    control_margin: float = 0.0,
    radius: int = 1,
    decay: float = 0.5,
    capture_type: str = "surround",
    win_type: str = "field_connection",
    max_turns: int = 50,
    pie_rule: bool = False,
    komi_p2: float = 0.0,
) -> GameDefV2:
    """Minimal hex_rhombus game. P1 connects dim 1 (r=0..s-1), P2 dim 0."""
    return GameDefV2(
        game_id=f"fc_test_{win_type}_{capture_type}_m{control_margin}",
        num_dimensions=2,
        axis_size=s,
        topology_type="hex_rhombus",
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type=capture_type),
        propagation_rule=PropagationRule(
            prop_type="influence", radius=radius, strength=1.0, decay=decay,
        ),
        win_condition=WinCondition(
            condition_type=win_type,
            threshold=10.0,
            target_dimension=1,
            target_dimension_p2=0,
            max_turns=max_turns,
            control_margin=control_margin,
        ),
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
        pie_rule=pie_rule,
        komi_p2=komi_p2,
    )


def _engine(game: GameDefV2) -> GameEngineV2:
    e = GameEngineV2(game)
    e.reset()
    return e


def _cell(e: GameEngineV2, q: int, r: int) -> int:
    return e.topo.coords_to_cell((q, r))


def test_field_connection_p1_win_on_controlled_column() -> None:
    """A column of P1-controlled cells (positive field) spanning r=0..s-1
    wins for P1 — no stones needed on the path itself."""
    e = _engine(make_fc_game())
    for r in range(6):
        e.board_values[_cell(e, 2, r)] = 0.7
    e._check_win_conditions()
    assert e.done and e._winner == 1


def test_field_connection_contested_gap_blocks() -> None:
    """One contested (zero) cell on every crossing path blocks the win."""
    e = _engine(make_fc_game())
    for r in range(6):
        e.board_values[_cell(e, 2, r)] = 0.7
    e.board_values[_cell(e, 2, 3)] = 0.0  # contested gap
    e._check_win_conditions()
    assert not e.done


def test_field_connection_p2_win_along_dim0() -> None:
    e = _engine(make_fc_game())
    for q in range(6):
        e.board_values[_cell(e, q, 3)] = -0.4
    e._check_win_conditions()
    assert e.done and e._winner == 2


def test_control_margin_gates_weak_control() -> None:
    """With margin 0.5, |values| <= 0.5 are contested; 0.6 wins."""
    e = _engine(make_fc_game(control_margin=0.5))
    for r in range(6):
        e.board_values[_cell(e, 2, r)] = 0.3
    e._check_win_conditions()
    assert not e.done
    for r in range(6):
        e.board_values[_cell(e, 2, r)] = 0.6
    e._check_win_conditions()
    assert e.done and e._winner == 1


def test_field_connection_goal_swap() -> None:
    """After a pie swap, P1's target dimension becomes P2's and vice versa
    (mirrors _check_connection's _goals_swapped handling)."""
    e = _engine(make_fc_game())
    e._goals_swapped = True
    # positive (P1) field spanning dim 0 — P1's goal AFTER swap
    for q in range(6):
        e.board_values[_cell(e, q, 3)] = 0.7
    e._check_win_conditions()
    assert e.done and e._winner == 1


def test_field_connection_end_to_end_by_placement() -> None:
    """Engine detects the win from real placements: two P1 stones with
    radius-2 influence cover the full column q=2 on a 6-board while P2
    plays far away (distance > 2 from the column)."""
    game = make_fc_game(radius=2)
    e = _engine(game)
    e.step(_cell(e, 2, 1))   # P1 — covers (2,0)..(2,3)
    assert not e.done
    e.step(_cell(e, 5, 0))   # P2 — far away
    assert not e.done
    e.step(_cell(e, 2, 4))   # P1 — covers (2,2)..(2,5): column complete
    assert e.done and e._winner == 1


def test_control_margin_default_and_roundtrip() -> None:
    """control_margin defaults to 0.0 and survives to_dict/from_dict."""
    wc = WinCondition(condition_type="field_connection", control_margin=0.25)
    d = wc.to_dict()
    assert d["control_margin"] == 0.25
    wc2 = WinCondition.from_dict(d)
    assert wc2.control_margin == 0.25
    assert wc2.condition_type == "field_connection"


def test_control_margin_omitted_at_default() -> None:
    """A default-margin WinCondition must serialize WITHOUT the key, so
    canonical_blob()/canonical_hash() of every existing game is unchanged."""
    wc = WinCondition(condition_type="threshold", threshold=30)
    d = wc.to_dict()
    assert "control_margin" not in d
    wc2 = WinCondition.from_dict(d)
    assert wc2.control_margin == 0.0
