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


def _far_cells(e: GameEngineV2, exclude: set[int], n: int) -> list[int]:
    """n cells at graph distance >= 2 from everything in *exclude*."""
    halo = set(exclude)
    for c in exclude:
        halo.update(e.topo.get_neighbors(c))
    out = []
    for c in e.topo.active_cells:
        if c not in halo and not (set(e.topo.get_neighbors(c)) & exclude):
            out.append(c)
        if len(out) == n:
            return out
    raise AssertionError("board too small for test geometry")


def test_field_flip_three_attackers_flip_lone_stone() -> None:
    e = _engine(make_p15_game(capture_type="field_flip"))
    center = e.topo.coords_to_cell((3, 3))
    ring = list(e.topo.get_neighbors(center))
    attackers = ring[:3]
    far = _far_cells(e, {center, *ring}, 2)
    # P1 a0, P2 center, P1 a1, P2 far0, P1 a2 -> field at center
    # = -1.0 + 0.5*3 = +0.5 > eps(0.25) -> flips.
    e.step(attackers[0]); e.step(center)
    e.step(attackers[1]); e.step(far[0])
    assert e.board_owners[center] == 2  # not yet: -1.0 + 0.5*2 = 0.0 <= 0.25
    e.step(attackers[2])
    assert e.board_owners[center] == 1
    assert e.piece_counts == [4, 1]
    # field must be the exact recompute (no stale/double-added values)
    bv = e.board_values.copy()
    e._recompute_field()
    assert np.allclose(bv, e.board_values)


def test_field_flip_defender_blocks_until_fourth_attacker() -> None:
    e = _engine(make_p15_game(capture_type="field_flip"))
    center = e.topo.coords_to_cell((3, 3))
    ring = list(e.topo.get_neighbors(center))
    defender = ring[0]
    attackers = [c for c in ring if c != defender][:4]
    far = _far_cells(e, {center, *ring}, 2)
    e.step(attackers[0]); e.step(center)
    e.step(attackers[1]); e.step(defender)
    e.step(attackers[2]); e.step(far[0])
    # -1.0 + 0.5*(3-1) = 0.0 <= 0.25: defender holds.
    assert e.board_owners[center] == 2
    e.step(attackers[3])
    # -1.0 + 0.5*(4-1) = +0.5 > 0.25: flips despite defender.
    assert e.board_owners[center] == 1


def test_field_flip_cascades_through_flipped_stone() -> None:
    e = _engine(make_p15_game(capture_type="field_flip"))
    A = e.topo.coords_to_cell((3, 3))
    ring = list(e.topo.get_neighbors(A))
    B = ring[0]
    adj_B = set(e.topo.get_neighbors(B))
    non_adj = [c for c in ring if c != B and c not in adj_B]
    bridge = next(c for c in ring if c != B and c in adj_B)
    attackers = non_adj[:3] + [bridge]           # 4 attackers on A's ring
    outer = [c for c in adj_B if c != A and c not in ring][:2]
    far = _far_cells(e, {A, B, *ring, *adj_B}, 3)
    # P1: outer0, outer1, non_adj x3, bridge(last, trigger). P2: A, B, far x3.
    seq_p1 = [outer[0], outer[1], attackers[0], attackers[1], attackers[2],
              attackers[3]]
    seq_p2 = [A, B, far[0], far[1], far[2]]
    for i in range(5):
        e.step(seq_p1[i]); e.step(seq_p2[i])
        # A is placed at pair 0, B at pair 1 — assert neither ever flips
        # to P1 prematurely (owner is 0-or-2 until the trigger).
        assert e.board_owners[A] != 1 and e.board_owners[B] != 1
    e.step(seq_p1[5])  # trigger
    # A: -1.0 + 0.5*4 - 0.5(B) = +0.5 > 0.25 -> flips.
    # B after A flips: -1.0 + 0.5(A) + 0.5(bridge) + 0.5*2(outer) = +1.0 -> cascades.
    assert e.board_owners[A] == 1 and e.board_owners[B] == 1
    assert e.piece_counts == [8, 3]


def test_field_flip_can_complete_connection_same_step() -> None:
    """Flips update the field before the win check, so a flip-created
    connection wins on the move that caused it."""
    e = _engine(make_p15_game(capture_type="field_flip", s=4, max_turns=40))
    p1_col = [e.topo.coords_to_cell((1, r)) for r in range(4)]
    p2_cells = [e.topo.coords_to_cell((3, r)) for r in range(3)]
    moves = [p1_col[0], p2_cells[0], p1_col[1], p2_cells[1],
             p1_col[2], p2_cells[2], p1_col[3]]
    for m in moves:
        if e.done:
            break
        e.step(m)
    assert e.done and e._winner == 1 and not e._ended_by_max_turns
