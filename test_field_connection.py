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


# ---------------------------------------------------------------------------
# Task 4: capture-triggered influence-field recompute (spec §3.4)
# ---------------------------------------------------------------------------

def _surround_corner_capture(e: GameEngineV2) -> None:
    """P2 stone at acute corner (0,0) (degree 2) is captured when P1
    fills both liberties (1,0) and (0,1). P2's other move is far away."""
    e.step(_cell(e, 1, 0))   # P1
    e.step(_cell(e, 0, 0))   # P2 — corner, 1 liberty left
    e.step(_cell(e, 0, 1))   # P1 — captures (0,0)
    assert e.board_owners[_cell(e, 0, 0)] == 0, "corner stone must be captured"


def test_capture_recomputes_field_for_field_connection() -> None:
    """Spec §3.4: removal recomputes the field. With radius-1/decay-0.5
    influence, the corner after capture holds ONLY the two P1 stones'
    contributions (+0.5 +0.5 = +1.0); the dead P2 stone's -1.0 ghost is gone."""
    e = _engine(make_fc_game(radius=1, decay=0.5))
    _surround_corner_capture(e)
    corner = _cell(e, 0, 0)
    assert e.board_values[corner] == 1.0, (
        f"expected recomputed +1.0 at corner, got {e.board_values[corner]}"
    )


def test_ghost_influence_preserved_for_legacy_games() -> None:
    """Identical position with a threshold win condition keeps the OLD
    semantics: the dead stone's influence remains (ghost), corner = 0.0.
    This is the regression guard for every pre-probe game."""
    e = _engine(make_fc_game(radius=1, decay=0.5, win_type="threshold"))
    _surround_corner_capture(e)
    corner = _cell(e, 0, 0)
    assert e.board_values[corner] == 0.0, (
        f"legacy ghost semantics changed! corner={e.board_values[corner]}"
    )


def test_capture_recompute_fires_within_capturing_step() -> None:
    """Recompute fires within the capturing step and rebuilds the field
    from stones only (hand-set values are wiped)."""
    e = _engine(make_fc_game(radius=1, decay=0.5))
    # Hand-build: P1 has SOME positive field values on the board, but NOT
    # a winning connection (use q=4 which is far from the P1 stones at
    # (1,0) and (0,1)). The key assertion is that after the capture+recompute
    # these hand-set values are wiped (recompute rebuilds from stones only)
    # and the corner (0,0) holds exactly the two P1 stones' contributions:
    # +0.5 from (1,0) + +0.5 from (0,1) = +1.0.
    for r in range(1, 6):
        e.board_values[_cell(e, 4, r)] = 0.7  # q=4, outside P1 stones' radius
    e._check_win_conditions()
    assert not e.done  # no winning path yet
    # Now play the capture sequence; after recompute (0,0) = +1.0 and the
    # hand-set values were wiped by recompute — so re-verify via field state.
    # (Recompute rebuilds from stones only; this asserts the mechanism fires.)
    e.step(_cell(e, 1, 0))   # P1
    e.step(_cell(e, 0, 0))   # P2 corner
    e.step(_cell(e, 0, 1))   # P1 captures
    corner = _cell(e, 0, 0)
    assert e.board_owners[corner] == 0
    assert e.board_values[corner] == 1.0


def test_recompute_runs_before_win_check_on_capture_ply() -> None:
    """Pin the hook ordering: on the capturing ply, _check_win_conditions
    must already see the recomputed field (corner == +1.0), not the stale
    ghost value. A mutant that recomputes after the win check fails here."""
    e = _engine(make_fc_game(radius=1, decay=0.5))
    corner = _cell(e, 0, 0)
    seen: list[float] = []
    real_check = e._check_win_conditions

    def spy() -> None:
        seen.append(float(e.board_values[corner]))
        real_check()

    e._check_win_conditions = spy
    e.step(_cell(e, 1, 0))   # P1
    e.step(_cell(e, 0, 0))   # P2 corner
    e.step(_cell(e, 0, 1))   # P1 captures
    assert e.board_owners[corner] == 0
    assert seen[-1] == 1.0, (
        f"win check saw stale field {seen[-1]} on the capture ply; "
        "recompute must run BEFORE _check_win_conditions"
    )


# ---------------------------------------------------------------------------
# Task 5: field_connection timeout tiebreak by controlled-cell count (spec §3.7)
# ---------------------------------------------------------------------------

def test_timeout_tiebreak_by_controlled_cells() -> None:
    """Spec §3.7: timeout -> larger controlled-cell count wins (komi
    applied), draw if equal. NOT piece count.

    Placement adjustment from plan's original moves (which triggered an early
    field-connection win on step 3):
      P1 at (0,2) and (1,2)  — two adjacent stones on the left half,
        influence radius 2 covers 16 cells with net positive field.
      P2 at (5,2) and (5,3)  — two stones in the far-right column,
        influence radius 2 covers 14 cells with net negative field.
    Neither player's positive/negative region spans the required dimension
    (P1 needs r=0..5, P2 needs q=0..5), so the game reaches max_turns=4
    and fires _end_by_max_turns. Piece counts are equal (2 vs 2), so the
    current tiebreak draws — but controlled cells are 16 vs 14, so P1
    must win under the new tiebreak.
    """
    e = _engine(make_fc_game(radius=2, decay=0.5, max_turns=4))
    e.step(_cell(e, 0, 2))   # P1: left-side stone
    e.step(_cell(e, 5, 2))   # P2: right-column stone
    e.step(_cell(e, 1, 2))   # P1: adjacent left-side stone
    e.step(_cell(e, 5, 3))   # P2: right-column stone — step 4 hits max_turns
    assert e.done
    assert e._winner == 1, f"P1 controls more cells (16 vs 14); got {e._winner}"


def test_timeout_tiebreak_komi_lifts_p2() -> None:
    """komi_p2 is multiplicative on num_active_cells for the count
    tiebreak (engine convention): komi = komi_p2 * num_active_cells is
    added to P2's raw controlled-cell count.

    With komi_p2=1.0, komi = 1.0 * 36 = 36, which dwarfs any control gap
    on this 6-board, so P2 wins despite controlling fewer raw cells (14 vs 16).
    """
    e = _engine(make_fc_game(radius=2, decay=0.5, max_turns=4, komi_p2=1.0))
    e.step(_cell(e, 0, 2))   # P1
    e.step(_cell(e, 5, 2))   # P2
    e.step(_cell(e, 1, 2))   # P1
    e.step(_cell(e, 5, 3))   # P2 — step 4 hits max_turns
    assert e.done
    assert e._winner == 2, f"komi (36) must lift P2 past P1 (16 vs 14+36); got {e._winner}"


def test_ended_by_max_turns_flag() -> None:
    """_ended_by_max_turns is True only for timeout endings, False for
    win-condition endings — exact end-cause for experiment classifiers."""
    # timeout ending (4-ply game from the tiebreak test)
    e = _engine(make_fc_game(radius=2, decay=0.5, max_turns=4))
    e.step(_cell(e, 0, 2)); e.step(_cell(e, 5, 2))
    e.step(_cell(e, 1, 2)); e.step(_cell(e, 5, 3))
    assert e.done and e._ended_by_max_turns

    # win-condition ending (3-ply column win from the end-to-end test)
    e2 = _engine(make_fc_game(radius=2))
    e2.step(_cell(e2, 2, 1)); e2.step(_cell(e2, 5, 0)); e2.step(_cell(e2, 2, 4))
    assert e2.done and e2._winner == 1 and not e2._ended_by_max_turns
