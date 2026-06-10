"""Phase-1.5 rules-rethink — engine tests for field_flip / field_replace
captures and the not_enemy_controlled placement constraint.

Spec: docs/superpowers/specs/2026-06-10-field-connect-phase15-design.md.
"""
from __future__ import annotations

import numpy as np  # noqa: F401
import pytest

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
    cell = e.topo.coords_to_cell
    blocker = cell((1, 1))   # P2 stone holding P1's q=1 column shut
    trigger = cell((2, 0))   # P1's third attacker adjacent to the blocker
    assert trigger in e.topo.get_neighbors(blocker)
    # P1 builds the q=1 column around the blocker; P2's spare stones sit
    # in the q=3 column, out of radius-1 range of every q=1 cell (their
    # neighbors are all q=2/q=3), so they never contest the column.
    moves = [
        cell((1, 0)), blocker,
        cell((1, 2)), cell((3, 1)),
        cell((1, 3)), cell((3, 2)),
    ]
    for m in moves:
        e.step(m)
    # Blocker holds: field at (1,1) = -1.0 + 0.5*((1,0)+(1,2)) = 0.0
    # <= 0.25, so row r=1 has no P1-controlled cell and the column is cut.
    assert not e.done
    assert e.board_owners[blocker] == 2
    e.step(trigger)
    # Field at (1,1): -1.0 + 0.5*3 = +0.5 > 0.25 -> flips to P1. The
    # flipped stone makes (1,1) strongly P1-controlled (+2.5), completing
    # the controlled column q=1 across r=0..3 on the same step.
    assert e.board_owners[blocker] == 1
    assert e.piece_counts == [5, 2]  # P2 lost a stone to the flip
    assert e.done and e._winner == 1 and not e._ended_by_max_turns


def test_kernel_cache_bit_identical_to_naive_field() -> None:
    """The memoized vectorized kernels must reproduce the historical
    naive per-cell influence loop bit-for-bit on a LEGACY game (probe A1
    shape: hex_rhombus s=6, surround captures, influence radius 2).

    The reference mirrors the engine's incremental legacy semantics: one
    naive kernel add per placement, then clip — ghost influence from any
    captured stones is kept, exactly as legacy games behave.
    """
    game = GameDefV2(
        game_id="p15_kernel_cache_legacy",
        num_dimensions=2,
        axis_size=6,
        topology_type="hex_rhombus",
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="surround"),
        propagation_rule=PropagationRule(
            prop_type="influence", radius=2, strength=1.0, decay=0.5,
        ),
        win_condition=WinCondition(
            condition_type="connection",
            target_dimension=1,
            target_dimension_p2=0,
            max_turns=80,
        ),
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
        pie_rule=False,
    )
    e = _engine(game)
    rule = game.propagation_rule
    ref = np.zeros(e.total_cells, dtype=np.float64)
    # Seed 5: 30 full steps, 2 surround-capture events, no ko rollbacks —
    # exercises both the kernel path and legacy ghost influence.
    rng = np.random.default_rng(5)
    steps = 0
    capture_steps = 0
    for _ in range(30):
        if e.done:
            break
        legal = [a for a in e.get_legal_actions() if a < e.total_cells]
        if not legal:
            break
        target = int(rng.choice(legal))
        mover = e.current_player
        sign = 1.0 if mover == 1 else -1.0
        pieces_before = sum(e.piece_counts)
        e.step(target)
        # The mirror assumes the move landed (no super-ko rollback turned
        # it into a pass with this seed).
        assert e.board_owners[target] == mover, "ko rollback; change seed"
        if sum(e.piece_counts) != pieces_before + 1:
            capture_steps += 1
        # Naive double loop — the pre-cache implementation, verbatim.
        for c in e.topo.cells_within_radius(target, rule.radius):
            dist = e.topo.distance(target, c)
            ref[c] += sign * rule.strength * (rule.decay ** dist)
        np.clip(ref, -100.0, 100.0, out=ref)
        assert np.array_equal(e.board_values, ref)
        steps += 1
    assert steps >= 20  # the game must run long enough to exercise the field
    assert capture_steps >= 1, "seed must exercise ghost influence; change seed"


def test_simultaneous_field_games_rejected() -> None:
    """step_simultaneous never honors _field_dirty, so field-coupled games
    (field_connection win or field captures) must never reach a running
    simultaneous engine."""
    # Prong 1: field_connection win condition (capture_type "none").
    g = make_p15_game()
    g.turn_structure = TurnStructure(turn_type="simultaneous")
    with pytest.raises(ValueError, match="simultaneous"):
        GameEngineV2(g)
    # Prong 2: field capture type with a LEGACY win condition — the
    # capture arm of the guard must fire on its own.
    g2 = make_p15_game(capture_type="field_flip")
    g2.win_condition = WinCondition(
        condition_type="connection",
        target_dimension=1,
        target_dimension_p2=0,
        max_turns=60,
    )
    g2.turn_structure = TurnStructure(turn_type="simultaneous")
    with pytest.raises(ValueError, match="simultaneous"):
        GameEngineV2(g2)
    # Alternating field games still construct fine.
    GameEngineV2(make_p15_game(capture_type="field_flip"))


def test_experimental_types_not_generatable() -> None:
    """Phase-1.5 types are registered but excluded from generation/mutation
    sampling spaces (legacy generation must stay bit-identical)."""
    from game_engine.rules import (
        GENERATABLE_CAPTURE_TYPES,
        GENERATABLE_PLACEMENT_CONSTRAINTS,
    )
    assert "field_flip" not in GENERATABLE_CAPTURE_TYPES
    assert "field_replace" not in GENERATABLE_CAPTURE_TYPES
    assert "not_enemy_controlled" not in GENERATABLE_PLACEMENT_CONSTRAINTS
    assert set(GENERATABLE_CAPTURE_TYPES) | {"field_flip", "field_replace"} \
        == set(CAPTURE_TYPES)
    assert (set(GENERATABLE_PLACEMENT_CONSTRAINTS)
            | {"not_enemy_controlled"} == set(PLACEMENT_CONSTRAINTS))


def _reference_field(owners, topo, rule) -> np.ndarray:
    bv = np.zeros(len(owners), dtype=np.float64)
    for cell in topo.active_cells:
        o = int(owners[cell])
        if o == 0:
            continue
        s = 1.0 if o == 1 else -1.0
        for c in topo.cells_within_radius(cell, rule.radius):
            bv[c] += s * rule.strength * (rule.decay ** topo.distance(cell, c))
    return np.clip(bv, -100.0, 100.0)


def _reference_flip_fixpoint(owners, mover, topo, rule, margin):
    owners = owners.copy()
    enemy = 3 - mover
    sign = 1.0 if mover == 1 else -1.0
    while True:
        bv = _reference_field(owners, topo, rule)
        flips = [c for c in topo.active_cells
                 if owners[c] == enemy and sign * bv[c] > margin]
        if not flips:
            return owners
        for c in flips:
            owners[c] = mover


def test_field_flip_matches_reference_on_random_games() -> None:
    rng = np.random.default_rng(7)
    for trial in range(3):
        g = make_p15_game(capture_type="field_flip", s=5, max_turns=40)
        e = _engine(g)
        for _ in range(40):
            if e.done:
                break
            legal = [a for a in e.get_legal_actions() if a < e.total_cells]
            if not legal:
                break
            mover = e.current_player
            pre = e.board_owners.copy()
            cell = int(rng.choice(legal))
            pre[cell] = mover  # the placement itself
            expected = _reference_flip_fixpoint(
                pre, mover, e.topo, g.propagation_rule,
                g.win_condition.control_margin,
            )
            e.step(cell)
            assert np.array_equal(e.board_owners, expected), (
                f"trial {trial}: engine diverged from reference fixpoint"
            )
            assert np.allclose(
                e.board_values,
                _reference_field(e.board_owners, e.topo, g.propagation_rule),
            )


def _setup_three_attackers(capture_type: str):
    """P2 stone at center with exactly 3 P1 attackers; P1 to move."""
    e = _engine(make_p15_game(capture_type=capture_type))
    center = e.topo.coords_to_cell((3, 3))
    ring = list(e.topo.get_neighbors(center))
    attackers = ring[:3]
    far = _far_cells(e, {center, *ring}, 3)
    e.step(attackers[0]); e.step(center)
    e.step(attackers[1]); e.step(far[0])
    e.step(attackers[2]); e.step(far[1])
    return e, center


def test_field_replace_legality_tracks_control() -> None:
    e, center = _setup_three_attackers("field_replace")
    # P1 to move; field at center = -1.0 + 0.5*3 = +0.5 > 0.25 -> replaceable.
    legal = e.get_legal_actions()
    assert center in legal
    # The ONLY occupied legal target is the controlled enemy stone — own
    # stones and uncontrolled enemy stones are never replace targets.
    occupied_targets = [a for a in legal
                        if a < e.total_cells and e.board_owners[a] != 0]
    assert occupied_targets == [center]


def test_field_replace_two_attackers_not_legal() -> None:
    e = _engine(make_p15_game(capture_type="field_replace"))
    center = e.topo.coords_to_cell((3, 3))
    ring = list(e.topo.get_neighbors(center))
    far = _far_cells(e, {center, *ring}, 2)
    e.step(ring[0]); e.step(center)
    e.step(ring[1]); e.step(far[0])
    # P1 to move; field at center = -1.0 + 0.5*2 = 0.0 <= 0.25 -> NOT legal.
    assert center not in e.get_legal_actions()


def test_field_replace_executes_and_sets_lockout() -> None:
    e, center = _setup_three_attackers("field_replace")
    k = e.step_count
    e.step(center)
    assert e.board_owners[center] == 1
    assert e.piece_counts == [4, 2]  # P1: 3 placed + replacement; P2: 3 - 1
    assert e._replace_lockout_cell == center
    assert e._replace_lockout_step == k


def test_field_replace_lockout_excludes_then_expires() -> None:
    """White-box: the locked cell is excluded exactly on the following turn."""
    e = _engine(make_p15_game(capture_type="field_replace"))
    center = e.topo.coords_to_cell((3, 3))
    ring = list(e.topo.get_neighbors(center))
    # Manufacture: P1 stone at center, P2 controls it (4 P2 ring stones).
    e.board_owners[center] = 1
    for c in ring[:4]:
        e.board_owners[c] = 2
    e.piece_counts = [1, 4]
    e._recompute_field()
    e.current_player = 2
    e.step_count = 10
    # field at center = +1.0 - 0.5*4 = -1.0; sign(P2)*bv = +1.0 > 0.25.
    assert center in e.get_legal_actions()
    e._replace_lockout_cell = center
    e._replace_lockout_step = 9   # "replaced last turn"
    assert center not in e.get_legal_actions()
    e._replace_lockout_step = 8   # one turn older -> expired
    assert center in e.get_legal_actions()


def test_field_replace_state_save_restore() -> None:
    e = _engine(make_p15_game(capture_type="field_replace"))
    e._replace_lockout_cell = 7
    e._replace_lockout_step = 3
    saved = e._save_state()
    e._replace_lockout_cell = -1
    e._replace_lockout_step = -1
    e._restore_state(saved)
    assert e._replace_lockout_cell == 7
    assert e._replace_lockout_step == 3
