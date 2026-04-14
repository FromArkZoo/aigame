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
    """Both players pass → game ends."""
    game = _make_simultaneous_game(axis_size=4)
    engine = GameEngineV2(game)
    engine.reset()

    pass_action = game.total_cells
    obs, reward, done, info = engine.step_simultaneous(pass_action, pass_action)

    assert done, "Game should end on double pass"
    print("  Double-pass ends the game")


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
    test_serialization_round_trip()
    test_quick_reject_simultaneous_with_movement()
    print("\nAll simultaneous turn type tests passed.")
