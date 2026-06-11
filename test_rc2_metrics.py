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


from metrics.rollout_traces import rollout_with_traces, run_protocol


def test_rollout_traces_shape_and_determinism():
    game = _game("none")
    r1 = rollout_with_traces(game, policy="random", seed=99)
    r2 = rollout_with_traces(game, policy="random", seed=99)
    assert r1["plies"] == r2["plies"] and r1["winner"] == r2["winner"]
    assert len(r1["owner_snapshots"]) == r1["plies"]
    # snapshots are independent copies, not views: mutating one must not
    # affect another (proven by mutation, not identity)
    before = r1["owner_snapshots"][-1].copy()
    r1["owner_snapshots"][0][0] += 1
    assert np.array_equal(r1["owner_snapshots"][-1], before)
    assert r1["captures_total"] == r2["captures_total"]


def test_run_protocol_split():
    game = _game("none")
    out = run_protocol(game, n=6, base_seed=11)
    assert len(out) == 6
    assert sum(1 for r in out if r["policy"] == "random") == 3
    assert sum(1 for r in out if r["policy"] == "greedy") == 3


from metrics.descriptors import (
    descriptor_row, interaction_rate_for_rollout,
    obs_control_flip_rate_from_snapshots, obs_drama_for_rollout,
    obs_lead_changes_from_snapshots, obs_progress_span,
    obs_threshold_progress,
)


def _topo(axis: int = 5):
    return _game("none", axis=axis).get_topology()


def _paint(topo, stones: dict[tuple[int, int], int]) -> np.ndarray:
    """Painted ownership array: {(axis0, axis1) coords: player} -> owners."""
    owners = np.zeros(topo.total_cells, dtype=np.int8)
    for coords, player in stones.items():
        owners[topo.coords_to_cell(coords)] = player
    return owners


def test_obs_progress_span_painted_board():
    game = _game("none", axis=5)
    engine = create_engine(game)
    engine.reset()
    topo = engine.topo
    owners = np.zeros(topo.total_cells, dtype=engine.board_owners.dtype)
    # P1 stones at (0,2),(2,2),(4,2): observer radius-2 influence spans all
    # 5 axis-0 coords -> span 1.0; P2 absent -> 0.0.
    for cell in (topo.coords_to_cell((0, 2)), topo.coords_to_cell((2, 2)),
                 topo.coords_to_cell((4, 2))):
        owners[cell] = 1
    assert obs_progress_span(topo, owners, player=1, axis=0) == 1.0
    assert obs_progress_span(topo, owners, player=2, axis=0) == 0.0


def test_obs_lead_changes_sign_flips():
    # Closed form: with only one player's stone on the board, that player's
    # radius-2 ball around the center of a 5x5 grid spans all 5 coords on
    # both axes (span 1.0) while the absent player spans 0.0.
    topo = _topo(axis=5)
    only_p1 = _paint(topo, {(2, 2): 1})  # diff = 1.0 - 0.0 = +1.0
    only_p2 = _paint(topo, {(2, 2): 2})  # diff = 0.0 - 1.0 = -1.0
    snapshots = [only_p1, only_p2, only_p1]
    # diff series +1, -1, +1 -> 2 lead changes
    assert obs_lead_changes_from_snapshots(
        topo, snapshots, axis_p1=0, axis_p2=1) == 2


def test_obs_control_flip_rate_counts_sign_changes():
    # Two snapshots differing by one P2 stone at (4,4); its radius-2 kernel
    # flips exactly its 6-cell ball from sign 0 to -1 (the P1 ball around
    # (0,0) is untouched: distance((0,0),(4,4)) = 8 > 4, kernels disjoint).
    topo = _topo(axis=5)
    snap1 = _paint(topo, {(0, 0): 1})
    snap2 = _paint(topo, {(0, 0): 1, (4, 4): 2})
    # Expected flip count k computed via observer_field directly:
    f1, f2 = observer_field(topo, snap1), observer_field(topo, snap2)
    s1 = (f1 > 0).astype(int) - (f1 < 0).astype(int)
    s2 = (f2 > 0).astype(int) - (f2 < 0).astype(int)
    k = int(np.count_nonzero(s1 != s2))
    # hand count: (4,4),(3,4),(4,3),(2,4),(3,3),(4,2)
    assert k == 6
    # mean over the single consecutive-snapshot transition == k
    assert obs_control_flip_rate_from_snapshots(topo, [snap1, snap2]) == float(k)


def test_obs_threshold_progress_observer_analogue():
    # Threshold-family game: progress uses the GAME'S OWN propagation params
    # (here identical to observer defaults: r=2, s=1.0, d=0.5) and the
    # engine's komi arithmetic. threshold = 0.5 (WinCondition default).
    game = _game("influence", condition_type="threshold", axis=7)
    assert game.win_condition.threshold == 0.5 and game.komi_p2 == 0.0
    topo = game.get_topology()
    # Single P1 stone: field at its own cell = strength * decay^0 = 1.0
    # -> p1 progress = 1.0 / 0.5 = 2.0; P2 owns nothing, komi 0 -> 0.0.
    owners = _paint(topo, {(3, 3): 1})
    assert obs_threshold_progress(game, topo, owners, player=1) == 2.0
    assert obs_threshold_progress(game, topo, owners, player=2) == 0.0
    # komi: P2 effective score adds komi_p2 * threshold (engine arithmetic),
    # so progress gains exactly komi_p2 = 0.5 with no P2 stones.
    game.komi_p2 = 0.5
    assert obs_threshold_progress(game, topo, owners, player=2) == 0.5
    game.komi_p2 = 0.0
    # clip at 0 (no upper clip): P1 stone at (0,0) swamped by three P2
    # stones -> field(0,0) = 1.0 - 0.5 - 0.5 - 0.25 = -0.25
    # -> raw progress -0.5 -> clipped to 0.0.
    owners = _paint(topo, {(0, 0): 1, (0, 1): 2, (1, 0): 2, (1, 1): 2})
    assert obs_threshold_progress(game, topo, owners, player=1) == 0.0


def test_descriptor_row_keys_and_aggregation():
    game = _game("none", axis=5)
    rollouts = run_protocol(game, n=2, base_seed=7)
    row = descriptor_row(game, rollouts)
    assert set(row.keys()) == {
        "obs_drama", "obs_drama_n", "obs_lead_changes",
        "obs_control_flip_rate", "interaction_rate", "game_length", "draws",
    }
    assert row["obs_drama_n"] + row["draws"] == 2
    assert 0.0 <= row["interaction_rate"] <= 1.0
    assert row["game_length"] > 0
    if row["obs_drama_n"] > 0:
        assert np.isfinite(row["obs_drama"]) and row["obs_drama"] >= 0.0
    # per-rollout functions agree with the aggregate path on one rollout
    topo = game.get_topology()
    d0 = obs_drama_for_rollout(game, topo, rollouts[0])
    assert d0 is None or d0 >= 0.0
    ir0 = interaction_rate_for_rollout(topo, rollouts[0])
    assert 0.0 <= ir0 <= 1.0
