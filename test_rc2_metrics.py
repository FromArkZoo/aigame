"""RC2 Phase A: observer field + descriptor tests."""
import numpy as np

from game_engine.game_def_v2 import GameDefV2
from game_engine.rules import (
    PlacementRule, CaptureRule, PropagationRule, WinCondition, TurnStructure,
)
from game_engine.factory import create_engine
from metrics.observer_field import (
    OBSERVER_DECAY, OBSERVER_RADIUS, OBSERVER_STRENGTH, observer_field,
)


def _game(prop_type: str, condition_type: str = "connection",
          radius: int = 2, strength: float = 1.0, decay: float = 0.5,
          axis: int = 7) -> GameDefV2:
    return GameDefV2(
        game_id=f"rc2_{prop_type}_{condition_type}", num_dimensions=2,
        axis_size=axis, topology_type="grid",
        placement_rule=PlacementRule(), capture_rule=CaptureRule(),
        propagation_rule=PropagationRule(prop_type=prop_type, radius=radius,
                                         strength=strength, decay=decay),
        win_condition=WinCondition(condition_type=condition_type,
                                   max_turns=60),
        turn_structure=TurnStructure(),
    )


def test_observer_parity_with_engine_field():
    # influence game whose params == observer defaults: observer must equal
    # the engine's own recomputed field exactly.
    game = _game("influence", condition_type="threshold")
    # Confirm the game uses the same params as the observer defaults so parity
    # is a real guarantee and would catch a drift in either direction.
    assert game.propagation_rule.radius == OBSERVER_RADIUS
    assert game.propagation_rule.strength == OBSERVER_STRENGTH
    assert game.propagation_rule.decay == OBSERVER_DECAY
    engine = create_engine(game)
    engine.reset()
    rng = np.random.default_rng(3)
    for _ in range(12):
        if engine.done:
            break
        engine.step(int(rng.choice(engine.get_legal_actions())))
    engine._recompute_field()
    obs = observer_field(engine.topo, engine.board_owners)
    assert np.array_equal(obs, engine.board_values)


def test_observer_nonzero_for_prop_none_and_no_leak():
    game = _game("none")
    engine = create_engine(game)
    engine.reset()
    rng = np.random.default_rng(4)
    for _ in range(8):
        if engine.done:
            break
        engine.step(int(rng.choice(engine.get_legal_actions())))
    before = engine.board_values.copy()
    obs = observer_field(engine.topo, engine.board_owners)
    assert np.count_nonzero(obs) > 0            # field defined for prop-none
    assert np.array_equal(engine.board_values, before)  # no leak
    assert np.all(before == 0.0)                # engine field genuinely dead


def test_observer_empty_board_zero():
    game = _game("none")
    engine = create_engine(game)
    engine.reset()
    assert np.count_nonzero(
        observer_field(engine.topo, engine.board_owners)) == 0
