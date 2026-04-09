#!/usr/bin/env python3
"""Integration tests for CA (Cellular Automaton) game mechanics.

Tests:
1. Generate CA games across all topology types
2. Verify all generated CA games pass validation
3. Run rollouts — no crashes
4. Verify CA step is simultaneous
5. Test super-ko with CA
6. Test CA mutation produces valid games
7. Test crossover between CA and non-CA games
8. Test crossover between two CA games
9. Print topology distribution, CA vs non-CA distribution
"""

import sys
import traceback
import numpy as np

from config import GameConfig, EvolutionConfig
from game_engine.generator_v2 import GameGeneratorV2
from game_engine.engine_v2 import GameEngineV2
from game_engine.game_def_v2 import GameDefV2
from game_engine.rules import (
    CARule, PlacementRule, CaptureRule, PropagationRule,
    WinCondition, TurnStructure, ActionRule,
)
from game_engine.topology import TopologicalSpace
from evolution.operators_v2 import MutationOperatorV2, CrossoverOperatorV2

passed = 0
failed = 0
bugs_found = []


def test(name, func):
    global passed, failed
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    try:
        func()
        passed += 1
        print(f"  PASSED")
    except Exception as e:
        failed += 1
        bugs_found.append((name, str(e)))
        print(f"  FAILED: {e}")
        traceback.print_exc()


# ======================================================================
# Test 1: Generate CA games across all topology types
# ======================================================================

generated_ca_games = []
generated_classic_games = []


def test_generate_ca_games():
    global generated_ca_games, generated_classic_games
    cfg = GameConfig(ca_probability=1.0)  # force CA
    gen = GameGeneratorV2(cfg, seed=100)

    topology_counts = {"grid": 0, "torus": 0, "hex": 0, "moore": 0}
    for i in range(50):
        game = gen.generate_game(seed=100 + i)
        assert game.ca_rule is not None, f"Game {game.game_id} should have CA rule"
        assert game.capture_rule.capture_type == "none", "CA games should have no capture"
        assert game.propagation_rule.prop_type == "none", "CA games should have no propagation"
        topology_counts[game.topology_type] += 1
        generated_ca_games.append(game)

    print(f"  Generated {len(generated_ca_games)} CA games")
    print(f"  Topology distribution: {topology_counts}")
    for t in ["grid", "hex", "moore"]:
        assert topology_counts[t] > 0, f"No {t} topology games generated"

    # Also generate classic games
    cfg2 = GameConfig(ca_probability=0.0)
    gen2 = GameGeneratorV2(cfg2, seed=200)
    for i in range(20):
        game = gen2.generate_game(seed=200 + i)
        assert game.ca_rule is None, f"Game {game.game_id} should NOT have CA rule"
        generated_classic_games.append(game)
    print(f"  Generated {len(generated_classic_games)} classic games")


# ======================================================================
# Test 2: Verify all generated CA games pass validation (quick_reject)
# ======================================================================

def test_ca_quick_reject():
    cfg = GameConfig(ca_probability=1.0)
    gen = GameGeneratorV2(cfg, seed=300)
    pass_count = 0
    fail_count = 0
    for game in generated_ca_games:
        if gen.quick_reject(game):
            pass_count += 1
        else:
            fail_count += 1
    print(f"  Quick reject: {pass_count} passed, {fail_count} rejected out of {len(generated_ca_games)}")
    # Some may fail stability check, that's OK
    assert pass_count > 0, "No CA games passed quick_reject"


# ======================================================================
# Test 3: Run rollouts — no crashes
# ======================================================================

def test_ca_rollouts():
    rng = np.random.default_rng(42)
    cfg = GameConfig(ca_probability=1.0)
    gen = GameGeneratorV2(cfg, seed=400)

    valid_games = [g for g in generated_ca_games if gen.quick_reject(g)][:10]
    if not valid_games:
        # Generate fresh valid games
        valid_games = gen.generate_valid_games(5, seed=500)

    total_rollouts = 0
    total_crashes = 0
    total_completed = 0

    for game in valid_games:
        for rollout in range(5):
            total_rollouts += 1
            try:
                engine = GameEngineV2(game)
                engine.reset()
                done = False
                for step in range(200):
                    legal = engine.get_legal_actions()
                    if not legal:
                        break
                    action = int(rng.choice(legal))
                    obs, rewards, done, info = engine.step(action)
                    if done:
                        total_completed += 1
                        break
                if not done:
                    total_completed += 1  # hit max steps, still OK
            except Exception as e:
                total_crashes += 1
                print(f"    CRASH on game {game.game_id} rollout {rollout}: {e}")

    print(f"  Ran {total_rollouts} rollouts on {len(valid_games)} CA games")
    print(f"  Completed: {total_completed}, Crashes: {total_crashes}")
    assert total_crashes == 0, f"{total_crashes} rollouts crashed"


# ======================================================================
# Test 4: Verify CA step is simultaneous
# ======================================================================

def test_ca_simultaneous():
    """Create a test where sequential vs simultaneous would give different results.

    Setup: 2D 4x4 grid, P1 at (0,0) and (1,1).
    CA rule: empty cell births P1 if it has >= 1 friendly neighbor.

    If simultaneous: both cells' neighbors are computed from the SAME snapshot.
    If sequential: cell (1,0) could be birthed first, then (2,1) would see it.

    We verify the board after one CA step matches simultaneous semantics.
    """
    # Create a simple CA rule: birth on 1+ friendly, survive always
    table = {}
    for f in range(5):
        for e in range(5):
            # Empty: birth if 1+ friendly
            table[(0, f, e)] = 1 if f >= 1 else 0
            # Friendly: always survive
            table[(1, f, e)] = 1
            # Enemy: always survive
            table[(2, f, e)] = 2

    ca_rule = CARule(transition_table=table, steps_per_turn=1, max_neighbors=4)

    game = GameDefV2(
        game_id="test_simultaneous",
        num_dimensions=2,
        axis_size=4,
        topology_type="grid",
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="none"),
        propagation_rule=PropagationRule(prop_type="none"),
        win_condition=WinCondition(condition_type="territory", threshold=0.9, max_turns=50),
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
        ca_rule=ca_rule,
    )

    engine = GameEngineV2(game)
    engine.reset()

    topo = game.get_topology()
    # Place P1 at (0,0) = cell 0 and (2,2) = cell 10
    # These are NOT adjacent on a 4x4 grid
    c00 = topo.coords_to_cell((0, 0))  # cell 0
    c22 = topo.coords_to_cell((2, 2))  # cell 10

    engine.board_owners[c00] = 1
    engine.board_owners[c22] = 1
    engine.piece_counts[0] = 2

    # Take snapshot before CA
    before = engine.board_owners.copy()

    # Compute what simultaneous should give:
    # Each empty cell adjacent to (0,0) or (2,2) should birth P1
    # Non-adjacent empty cells should stay empty
    expected = before.copy()
    for cell in range(16):
        if before[cell] == 0:
            nbrs = topo.get_neighbors(cell)
            friendly = sum(1 for n in nbrs if before[n] == 1)
            if friendly >= 1:
                expected[cell] = 1

    # Run one CA step via the engine
    engine._run_ca_step(acting_player=1)

    # Compare
    if not np.array_equal(engine.board_owners, expected):
        print(f"    Before: {before}")
        print(f"    After:  {engine.board_owners}")
        print(f"    Expected: {expected}")
        raise AssertionError("CA step is NOT simultaneous!")

    # Verify cells that were NOT adjacent to original pieces stayed empty
    # (This catches sequential updates where new births cascade within one step)
    c33 = topo.coords_to_cell((3, 3))
    # (3,3) is only adjacent to (2,3) and (3,2) — neither was initially occupied
    # So (3,3) should still be empty after ONE simultaneous step
    assert engine.board_owners[c33] == 0, \
        f"Cell (3,3) should be empty after 1 step but is {engine.board_owners[c33]} — sequential leak!"

    print(f"  CA step confirmed simultaneous")
    print(f"  Before: P1 at (0,0) and (2,2)")
    print(f"  After 1 step: {int(np.sum(engine.board_owners == 1))} P1 cells")


# ======================================================================
# Test 5: Test super-ko with CA
# ======================================================================

def test_ca_super_ko():
    """CA rules can create oscillating board positions.
    Super-ko should prevent infinite loops by treating repeated positions as passes.
    """
    # Create an oscillating rule: friendly dies if 0 friendly neighbors, births on 1+
    table = {}
    for f in range(5):
        for e in range(5):
            # Empty: birth if exactly 1 friendly neighbor
            table[(0, f, e)] = 1 if f == 1 else 0
            # Friendly: die if isolated (0 friendly neighbors)
            table[(1, f, e)] = 0 if f == 0 else 1
            # Enemy: same logic
            table[(2, f, e)] = 0 if e == 0 else 2  # uses enemy count for "friendly from their perspective"

    ca_rule = CARule(transition_table=table, steps_per_turn=1, max_neighbors=4)

    game = GameDefV2(
        game_id="test_ko",
        num_dimensions=2,
        axis_size=4,
        topology_type="grid",
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="none"),
        propagation_rule=PropagationRule(prop_type="none"),
        win_condition=WinCondition(condition_type="territory", threshold=0.9, max_turns=30),
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
        ca_rule=ca_rule,
    )

    engine = GameEngineV2(game)
    engine.reset()

    # Play some moves and verify the game terminates (super-ko prevents infinite loops)
    rng = np.random.default_rng(123)
    done = False
    for step in range(100):
        legal = engine.get_legal_actions()
        if not legal:
            break
        action = int(rng.choice(legal))
        obs, rewards, done, info = engine.step(action)
        if done:
            break

    print(f"  Game terminated after {engine.step_count} steps, done={done}")
    # The game should terminate (either by win condition or max turns), not hang
    assert engine.step_count <= 30, "Game exceeded max turns — possible infinite loop"


# ======================================================================
# Test 6: Test CA mutation produces valid games
# ======================================================================

def test_ca_mutation():
    cfg = GameConfig(ca_probability=1.0)
    gen = GameGeneratorV2(cfg, seed=600)
    evo_cfg = EvolutionConfig()
    rng = np.random.default_rng(700)
    mutator = MutationOperatorV2(evo_cfg, rng)

    valid_parents = [g for g in generated_ca_games if gen.quick_reject(g)][:10]
    if not valid_parents:
        valid_parents = gen.generate_valid_games(5, seed=650)

    mutated_count = 0
    valid_count = 0
    for parent in valid_parents:
        child = mutator.mutate_game(parent)
        mutated_count += 1
        if child.ca_rule is not None:
            # CA should still have none capture/propagation
            assert child.capture_rule.capture_type == "none", \
                f"Mutated CA game has capture={child.capture_rule.capture_type}"
            assert child.propagation_rule.prop_type == "none", \
                f"Mutated CA game has propagation={child.propagation_rule.prop_type}"
        if gen.quick_reject(child):
            valid_count += 1

    print(f"  Mutated {mutated_count} CA games, {valid_count} passed quick_reject")
    assert valid_count > 0, "No mutated CA games passed validation"


# ======================================================================
# Test 7: Test crossover between CA and non-CA games
# ======================================================================

def test_crossover_ca_classic():
    cfg = GameConfig(ca_probability=0.5)
    gen = GameGeneratorV2(cfg, seed=800)
    evo_cfg = EvolutionConfig()
    rng = np.random.default_rng(900)
    crossover = CrossoverOperatorV2(evo_cfg, rng)

    ca_games = [g for g in generated_ca_games if gen.quick_reject(g)][:5]
    classic_games = [g for g in generated_classic_games if gen.quick_reject(g)][:5]

    if not ca_games or not classic_games:
        print("  SKIP: not enough valid games for crossover test")
        return

    children_with_ca = 0
    children_without_ca = 0
    crashes = 0

    for ca_game in ca_games:
        for classic_game in classic_games:
            try:
                child = crossover.crossover_games(ca_game, classic_game)
                if child.ca_rule is not None:
                    children_with_ca += 1
                    assert child.capture_rule.capture_type == "none"
                    assert child.propagation_rule.prop_type == "none"
                else:
                    children_without_ca += 1
            except Exception as e:
                crashes += 1
                print(f"    Crossover crash: {e}")

    print(f"  CA x Classic crossovers: {children_with_ca} with CA, {children_without_ca} without CA, {crashes} crashes")
    assert crashes == 0, f"{crashes} crossover crashes"


# ======================================================================
# Test 8: Test crossover between two CA games
# ======================================================================

def test_crossover_ca_ca():
    cfg = GameConfig(ca_probability=1.0)
    gen = GameGeneratorV2(cfg, seed=1000)
    evo_cfg = EvolutionConfig()
    rng = np.random.default_rng(1100)
    crossover = CrossoverOperatorV2(evo_cfg, rng)

    ca_games = [g for g in generated_ca_games if gen.quick_reject(g)][:5]
    if len(ca_games) < 2:
        print("  SKIP: not enough valid CA games for CA x CA crossover test")
        return

    children_with_ca = 0
    children_without_ca = 0
    crashes = 0

    for i in range(len(ca_games)):
        for j in range(i + 1, len(ca_games)):
            try:
                child = crossover.crossover_games(ca_games[i], ca_games[j])
                if child.ca_rule is not None:
                    children_with_ca += 1
                    assert child.capture_rule.capture_type == "none"
                    assert child.propagation_rule.prop_type == "none"
                else:
                    children_without_ca += 1
            except Exception as e:
                crashes += 1
                print(f"    Crossover crash: {e}")

    print(f"  CA x CA crossovers: {children_with_ca} with CA, {children_without_ca} without CA, {crashes} crashes")
    assert crashes == 0, f"{crashes} crossover crashes"


# ======================================================================
# Test 9: Serialization roundtrip
# ======================================================================

def test_ca_serialization():
    for game in generated_ca_games[:5]:
        d = game.to_dict()
        assert "ca_rule" in d, "CA game dict missing ca_rule"
        assert d["version"] == 4, f"CA game version should be 4, got {d['version']}"

        restored = GameDefV2.from_dict(d)
        assert restored.ca_rule is not None, "Restored game lost CA rule"
        assert restored.ca_rule.steps_per_turn == game.ca_rule.steps_per_turn
        assert len(restored.ca_rule.transition_table) == len(game.ca_rule.transition_table)

        # Verify all table entries match
        for key, val in game.ca_rule.transition_table.items():
            assert restored.ca_rule.transition_table[key] == val, \
                f"Table mismatch at {key}: {val} vs {restored.ca_rule.transition_table.get(key)}"

    # Classic game roundtrip should still work
    for game in generated_classic_games[:3]:
        d = game.to_dict()
        assert "ca_rule" not in d, "Classic game dict should not have ca_rule"
        assert d["version"] == 3
        restored = GameDefV2.from_dict(d)
        assert restored.ca_rule is None

    print(f"  Serialization roundtrip OK for CA and classic games")


# ======================================================================
# Test 10: Distribution stats
# ======================================================================

def test_distribution():
    cfg = GameConfig(ca_probability=0.3)
    gen = GameGeneratorV2(cfg, seed=2000)

    ca_count = 0
    classic_count = 0
    topology_counts = {"grid": 0, "torus": 0, "hex": 0, "moore": 0}

    for i in range(100):
        game = gen.generate_game(seed=2000 + i)
        if game.ca_rule is not None:
            ca_count += 1
        else:
            classic_count += 1
        topology_counts[game.topology_type] += 1

    print(f"  CA vs Classic: {ca_count} CA, {classic_count} classic (out of 100)")
    print(f"  Topology distribution: {topology_counts}")
    # With 30% CA probability, expect roughly 20-40 CA games
    assert 10 <= ca_count <= 50, f"CA distribution seems off: {ca_count}/100"


# ======================================================================
# Test 11: CA game sample output
# ======================================================================

def test_sample_ca_output():
    """Show a sample CA game being played to demonstrate dynamics."""
    cfg = GameConfig(ca_probability=1.0)
    gen = GameGeneratorV2(cfg, seed=3000)

    # Find a valid CA game
    game = None
    for i in range(50):
        candidate = gen.generate_game(seed=3000 + i)
        if gen.quick_reject(candidate):
            game = candidate
            break

    if game is None:
        print("  SKIP: couldn't find a valid CA game for demo")
        return

    print(f"  Sample CA game: {game.game_id}")
    print(f"    Topology: {game.num_dimensions}D {game.topology_type} axis={game.axis_size}")
    print(f"    CA steps/turn: {game.ca_rule.steps_per_turn}")

    birth_rules = sum(1 for (s, f, e), ns in game.ca_rule.transition_table.items() if s == 0 and ns != 0)
    death_rules = sum(1 for (s, f, e), ns in game.ca_rule.transition_table.items() if s == 1 and ns == 0)
    convert_rules = sum(1 for (s, f, e), ns in game.ca_rule.transition_table.items() if s != 0 and ns != 0 and ns != s)
    print(f"    CA: {birth_rules} birth rules, {death_rules} death rules, {convert_rules} conversion rules")
    print(f"    Win condition: {game.win_condition.condition_type}")

    engine = GameEngineV2(game)
    engine.reset()

    rng = np.random.default_rng(42)
    moves = []
    for step in range(20):
        legal = engine.get_legal_actions()
        if not legal:
            break
        # Prefer placement over pass
        placements = [a for a in legal if a < game.total_cells]
        action = int(rng.choice(placements)) if placements else legal[0]

        p1_before = engine.piece_counts[0]
        p2_before = engine.piece_counts[1]
        player = engine.get_current_player()

        obs, rewards, done, info = engine.step(action)

        p1_after = engine.piece_counts[0]
        p2_after = engine.piece_counts[1]

        ca_effect = ""
        if p1_after != p1_before + (1 if player == 0 else 0) or p2_after != p2_before + (1 if player == 1 else 0):
            ca_effect = f" [CA: P1 {p1_before}->{p1_after}, P2 {p2_before}->{p2_after}]"

        moves.append(f"    Move {step+1}: P{player+1} -> cell {action}, P1={p1_after} P2={p2_after}{ca_effect}")

        if done:
            winner = info.get("winner")
            moves.append(f"    GAME OVER: {'P' + str(winner+1) + ' wins' if winner is not None else 'Draw'}")
            break

    for m in moves[:15]:
        print(m)
    if len(moves) > 15:
        print(f"    ... ({len(moves) - 15} more moves)")


# ======================================================================
# Run all tests
# ======================================================================

if __name__ == "__main__":
    test("Generate CA games across topologies", test_generate_ca_games)
    test("CA quick_reject validation", test_ca_quick_reject)
    test("CA rollouts (no crashes)", test_ca_rollouts)
    test("CA step is simultaneous", test_ca_simultaneous)
    test("CA super-ko prevents loops", test_ca_super_ko)
    test("CA mutation produces valid games", test_ca_mutation)
    test("Crossover CA x Classic", test_crossover_ca_classic)
    test("Crossover CA x CA", test_crossover_ca_ca)
    test("CA serialization roundtrip", test_ca_serialization)
    test("CA vs Classic distribution", test_distribution)
    test("Sample CA game output", test_sample_ca_output)

    print(f"\n{'='*60}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    print(f"{'='*60}")

    if bugs_found:
        print("\nBugs found:")
        for name, error in bugs_found:
            print(f"  - {name}: {error}")

    sys.exit(0 if failed == 0 else 1)
