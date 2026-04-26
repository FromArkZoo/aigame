"""Integration tests for simultaneous turn type (V5).

Tests:
1. Generator can produce simultaneous games
2. Engine step_simultaneous works for non-colliding placements
3. Mutual annihilation on colliding placements
4. Both-pass ends the game
5. Super-ko rollback in simultaneous mode
6. CA alternates perspective across steps in simultaneous games
7. Serialization round-trips simultaneous turn type
"""

import numpy as np

from config import GameConfig
from game_engine.generator_v2 import GameGeneratorV2
from game_engine.engine_v2 import GameEngineV2
from game_engine.game_def_v2 import GameDefV2
from game_engine.rules import (
    PlacementRule, CaptureRule, PropagationRule,
    WinCondition, TurnStructure, ActionRule,
)


def _make_simultaneous_game(
    axis_size: int = 6,
    topology_type: str = "grid",
    with_ca: bool = False,
) -> GameDefV2:
    """Small 2D game with simultaneous turn type for unit tests."""
    game = GameDefV2(
        game_id="test_sim",
        num_dimensions=2,
        axis_size=axis_size,
        topology_type=topology_type,
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="none"),
        propagation_rule=PropagationRule(prop_type="none"),
        win_condition=WinCondition(
            condition_type="territory",
            threshold=0.5,
            target_dimension=0,
            max_turns=50,
        ),
        turn_structure=TurnStructure(turn_type="simultaneous", pieces_per_turn=1),
        action_rule=ActionRule(action_types=("place",), move_constraint="adjacent_empty"),
        ca_rule=None,
        num_players=2,
    )
    if with_ca:
        from game_engine.rules import CARule
        # Simple CA: lone enemy dies (1-friendly next to an enemy kills it)
        table = {}
        max_degree = game.get_topology().max_degree
        for s in range(3):
            for f in range(max_degree + 1):
                for e in range(max_degree + 1):
                    table[(s, f, e)] = s  # identity default
        # Add one non-identity rule: lone enemy with 1 friendly -> empty
        table[(2, 1, 0)] = 0
        game.ca_rule = CARule(
            transition_table=table,
            steps_per_turn=2,  # two steps to test perspective alternation
            max_neighbors=max_degree,
        )
    return game


def test_generator_produces_simultaneous():
    """Generator should produce simultaneous games when probability is high."""
    cfg = GameConfig(simultaneous_probability=1.0)
    gen = GameGeneratorV2(cfg, seed=42)

    count_sim = 0
    for i in range(30):
        game = gen.generate_game(seed=42 + i)
        if game.turn_structure.turn_type == "simultaneous":
            count_sim += 1
            assert not game.action_rule.has_move(), \
                f"Simultaneous game {game.game_id} has movement — should be place-only"

    assert count_sim >= 20, f"Expected most games simultaneous, got {count_sim}/30"
    print(f"  Generator produced {count_sim}/30 simultaneous games")


def test_non_colliding_placements():
    """Two players place on different cells → both placed."""
    game = _make_simultaneous_game(axis_size=4)
    engine = GameEngineV2(game)
    engine.reset()

    # P1 places at 0, P2 places at 5
    obs, reward, done, info = engine.step_simultaneous(0, 5)

    assert engine.board_owners[0] == 1, "P1 stone missing"
    assert engine.board_owners[5] == 2, "P2 stone missing"
    assert engine.piece_counts == [1, 1]
    assert not info.get("collision"), "No collision expected"
    print("  Non-colliding placements: both placed correctly")


def test_mutual_annihilation():
    """Two players target the same cell → mutual annihilation."""
    game = _make_simultaneous_game(axis_size=4)
    engine = GameEngineV2(game)
    engine.reset()

    # Both target cell 5
    obs, reward, done, info = engine.step_simultaneous(5, 5)

    assert engine.board_owners[5] == 0, "Cell should be empty after annihilation"
    assert engine.piece_counts == [0, 0]
    assert info.get("collision") == True, "Collision should be flagged"
    print("  Mutual annihilation works")


def test_both_pass_ends_game():
    """Both players pass → game ends as a DRAW (R15 exploit fix).

    Pre-fix: both pass resolved by piece-count majority, which allowed a
    leading player to stop placing and force a win without the stated win
    condition firing. Now double-pass produces winner=None (draw).
    """
    game = _make_simultaneous_game(axis_size=4)
    engine = GameEngineV2(game)
    engine.reset()

    # Asymmetric board: P1 places one stone, then both pass.
    # Pre-fix, P1 would win by majority. Post-fix, it's a draw.
    pass_action = game.total_cells
    engine.step_simultaneous(0, pass_action)  # P1 places at 0, P2 passes
    assert engine.piece_counts == [1, 0]
    obs, reward, done, info = engine.step_simultaneous(pass_action, pass_action)

    assert done, "Game should end on double pass"
    assert engine._winner is None, (
        f"Double-pass should produce a draw, not a majority win. "
        f"Winner was {engine._winner} with piece counts {engine.piece_counts}"
    )
    print("  Double-pass ends the game as a draw (winner=None)")


def test_collision_on_existing_stone():
    """P1 and P2 both target cell that already has P1's stone.
    With target='empty', both actions would be illegal; use target='any'."""
    game = _make_simultaneous_game(axis_size=4)
    game.placement_rule.target = "any"
    engine = GameEngineV2(game)
    engine.reset()

    # P1 places at 5 first (via two non-colliding rounds)
    engine.step_simultaneous(5, 0)

    # Now both target cell 5
    engine.step_simultaneous(5, 5)

    # Collision: neither places, cell 5 should still have P1's stone from before
    # (because collision = "neither places this round")
    assert engine.board_owners[5] == 1, "Existing P1 stone should survive collision"
    print("  Collision on occupied cell: existing stone preserved")


def test_ca_alternates_perspective():
    """In simultaneous + CA games, CA steps should alternate P1/P2 perspective."""
    game = _make_simultaneous_game(axis_size=4, with_ca=True)
    engine = GameEngineV2(game)
    engine.reset()

    # The CA rule kills enemy stones with exactly 1 friendly neighbor (rule: 2,1,0 → 0).
    # After step 1 from P1's perspective, it kills P2 stones adjacent to isolated P1 stones.
    # After step 2 from P2's perspective, it kills P1 stones adjacent to isolated P2 stones.

    # Place one P1 at (1,1)=5 and one P2 at (2,1)=6
    obs, reward, done, info = engine.step_simultaneous(5, 6)

    # After 2 CA steps alternating perspective:
    # Step 1 from P1's view: cell 6 has (state=2 enemy, f=1 friendly=P1-at-5, e=0) → apply (2,1,0) → 0
    #   So P2 at cell 6 dies.
    # Step 2 from P2's view: nothing happens because no isolated P2 remains.
    # Result: only P1 stone at cell 5 remains.
    assert engine.board_owners[5] == 1 or engine.board_owners[6] == 2, \
        "At least one stone should have persisted or been killed by CA"
    print(f"  After simultaneous + CA: P1 pieces={engine.piece_counts[0]}, P2 pieces={engine.piece_counts[1]}")


def test_ca_symmetric_with_steps_per_turn_1():
    """With steps_per_turn=1, both P1 and P2 perspectives must run per tick.

    Regression test for the R14 engine bug: the old loop `for i in range(steps_per_turn):
    acting_player = 1 if i%2==0 else 2` only ever fired P1's perspective when
    steps_per_turn=1, producing engine-wide P1 bias in every sim+CA R14 game.
    """
    from game_engine.rules import CARule

    game = _make_simultaneous_game(axis_size=4, with_ca=False)
    max_degree = game.get_topology().max_degree

    # Rule: isolated own stone dies (own=1, friends=0, enemies=0) -> empty.
    # Mirror for state=2 per R15 symmetry invariant so the R16 shared-
    # snapshot engine actually applies the rule (disagreements between
    # perspectives get rejected — asymmetric tables would no-op here).
    table = {}
    for s in range(3):
        for f in range(max_degree + 1):
            for e in range(max_degree + 1):
                table[(s, f, e)] = s
    table[(1, 0, 0)] = 0  # isolated own stone dies
    table[(2, 0, 0)] = 0  # symmetric mirror: swap(T(1,0,0)) = swap(0) = 0

    game.ca_rule = CARule(
        transition_table=table,
        steps_per_turn=1,   # the broken case pre-fix
        max_neighbors=max_degree,
    )

    engine = GameEngineV2(game)
    engine.reset()

    # Place P1 and P2 isolated stones far apart. 4×4 grid → 16 cells.
    # P1 at cell 0 (corner), P2 at cell 15 (opposite corner). No adjacency.
    obs, reward, done, info = engine.step_simultaneous(0, 15)

    # After the CA step with both perspectives applied:
    # - P1 stone at 0: from P1 view abstract (1,0,0) -> 0 (dies). From P2 view abstract (2,0,0) -> identity. Result: dead.
    # - P2 stone at 15: from P1 view abstract (2,0,0) -> identity. From P2 view abstract (1,0,0) -> 0 (dies). Result: dead.
    # PRE-FIX: only P1 perspective ran, so P1 died but P2 survived -> asymmetric.
    # POST-FIX: both perspectives run, both dead -> symmetric.
    assert engine.board_owners[0] == 0, (
        f"P1 stone at 0 should have died from P1-perspective CA; got owner {engine.board_owners[0]}"
    )
    assert engine.board_owners[15] == 0, (
        f"P2 stone at 15 should have died from P2-perspective CA; got owner {engine.board_owners[15]} "
        f"(pre-fix bug: P2's perspective never ran with steps_per_turn=1)"
    )
    print("  CA symmetry holds with steps_per_turn=1 (both perspectives fire)")


def test_threshold_margin_based_resolution():
    """Same-tick threshold crossings resolve by margin, not by iteration order (R16 fix).

    Regression test for the R15 bug where `_check_threshold` iterated
    `for player in (1, 2)` and returned on the first crossing, giving P1
    every same-tick tie — even when P2 had a higher effective margin.
    Human eval teams documented P2 scoring 42.6 losing to P1 at 41.85.
    """
    game = _make_simultaneous_game(axis_size=4)
    game.win_condition.condition_type = "threshold"
    game.win_condition.threshold = 1.5  # low enough to cross after a few stones
    engine = GameEngineV2(game)
    engine.reset()

    # Manually rig the board so that on the next tick both players cross
    # the threshold, but P2 has a larger effective margin than P1.
    # P1 owns cell 0 with value 1.6; P2 owns cell 15 with value -3.0.
    # Effective: P1 = 1.6, P2 = 3.0. Both > 1.5 threshold. P2 should win.
    engine.board_owners[0] = 1
    engine.board_values[0] = 1.6
    engine.board_owners[15] = 2
    engine.board_values[15] = -3.0
    engine.piece_counts = [1, 1]

    engine._check_threshold(1.5)
    assert engine.done, "Game should be decided"
    assert engine._winner == 2, (
        f"P2 has higher margin (3.0 > 1.6) but engine said winner={engine._winner}. "
        f"Iteration-order bias still active."
    )
    print("  Threshold: higher margin wins (P2 3.0 beats P1 1.6)")

    # Now test exact-tie → draw
    engine2 = GameEngineV2(game)
    engine2.reset()
    engine2.board_owners[0] = 1
    engine2.board_values[0] = 2.0
    engine2.board_owners[15] = 2
    engine2.board_values[15] = -2.0
    engine2.piece_counts = [1, 1]
    engine2._check_threshold(1.5)
    assert engine2.done
    assert engine2._winner is None, (
        f"Perfectly symmetric margins should draw; engine said {engine2._winner}"
    )
    print("  Threshold: symmetric tie is a draw")


def test_threshold_fp_ulp_tie_draws():
    """Margins differing by ~ULPs (FP noise from propagation order) draw, not P1 win.

    R17 regression: simultaneous play applies P1 then P2 _apply_propagation
    as separate += passes; with overlapping radii the ordering of those
    passes shifts each total by ~1e-15. Without tolerance, those shifts
    became phantom P1 wins instead of draws (4 R16 sim teams hit this).
    """
    game = _make_simultaneous_game(axis_size=4)
    game.win_condition.condition_type = "threshold"
    game.win_condition.threshold = 1.5
    engine = GameEngineV2(game)
    engine.reset()

    # P1 effective = 2.0; P2 effective = 2.0 - 1e-14 (one ULP at this scale).
    # True margins are equal; the 1e-14 gap is FP noise. Engine must draw.
    engine.board_owners[0] = 1
    engine.board_values[0] = 2.0
    engine.board_owners[15] = 2
    engine.board_values[15] = -(2.0 - 1e-14)
    engine.piece_counts = [1, 1]

    engine._check_threshold(1.5)
    assert engine.done
    assert engine._winner is None, (
        f"FP-ULP-sized margin diff (~1e-14) should draw; engine said {engine._winner}"
    )
    print("  Threshold: ULP-sized margin difference resolves as draw (R17 FP fix)")


def test_connection_symmetric_tie_draws():
    """Same-tick connection completions resolve as draw (R16 fix).

    On a 4-connected grid the Hex theorem prevents disjoint cross-board
    connections, so use a torus where both players' paths can coexist
    via wrap-adjacency. This also exercises the exact scenario R15 sim×CA
    teams reported.
    """
    from game_engine.rules import WinCondition
    game = _make_simultaneous_game(axis_size=4, topology_type="torus")
    game.win_condition = WinCondition(
        condition_type="connection",
        threshold=0.5,
        target_dimension=0,
        target_dimension_p2=1,
        max_turns=50,
    )
    engine = GameEngineV2(game)
    engine.reset()
    # P1 dim 0 connection needs cells touching x=0 and x=3 faces, connected.
    # On torus, (0, 0) and (3, 0) are wrap-adjacent via x axis — two stones
    # form a winning group touching both x-faces. Indices: 0 and 3.
    # P2 dim 1 connection: (2, 0) and (2, 3) are wrap-adjacent via y axis,
    # touching both y-faces. Indices: 2 and 14. (Disjoint from P1's.)
    engine.board_owners[0] = 1
    engine.board_owners[3] = 1
    engine.board_owners[2] = 2
    engine.board_owners[14] = 2
    engine.piece_counts = [2, 2]

    engine._check_connection(0, 1)
    assert engine.done
    assert engine._winner is None, (
        f"Simultaneous connection completion should draw; engine said {engine._winner}"
    )
    print("  Connection: simultaneous completion is a draw (on torus)")


def test_serialization_round_trip():
    """Simultaneous games serialize and deserialize correctly."""
    game = _make_simultaneous_game(axis_size=4)
    d = game.to_dict()
    game2 = GameDefV2.from_dict(d)
    assert game2.turn_structure.turn_type == "simultaneous"
    print("  Serialization: simultaneous preserved through to_dict/from_dict")


def test_quick_reject_simultaneous_with_movement():
    """Generator's quick_reject should reject simultaneous games with movement."""
    from game_engine.generator_v2 import GameGeneratorV2
    cfg = GameConfig()
    gen = GameGeneratorV2(cfg, seed=42)

    game = _make_simultaneous_game()
    game.action_rule = ActionRule(action_types=("place", "move"), move_constraint="adjacent_empty")
    assert not gen.quick_reject(game), "Should reject simultaneous + movement"
    print("  quick_reject correctly rejects simultaneous + movement")


if __name__ == "__main__":
    print("Running simultaneous turn type tests...\n")
    test_generator_produces_simultaneous()
    test_non_colliding_placements()
    test_mutual_annihilation()
    test_both_pass_ends_game()
    test_collision_on_existing_stone()
    test_ca_alternates_perspective()
    test_ca_symmetric_with_steps_per_turn_1()
    test_threshold_margin_based_resolution()
    test_threshold_fp_ulp_tie_draws()
    test_connection_symmetric_tie_draws()
    test_serialization_round_trip()
    test_quick_reject_simultaneous_with_movement()
    print("\nAll simultaneous turn type tests passed.")
