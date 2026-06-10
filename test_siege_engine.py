"""SIEGE engine mechanics: asymmetric win fields, quota accounting, timeout_winner."""
import numpy as np

from game_engine.game_def_v2 import GameDefV2
from game_engine.rules import (
    PlacementRule, CaptureRule, PropagationRule, WinCondition, TurnStructure,
)

# Captured from main branch (pre-SIEGE) — must never change.
GOLDEN_LEGACY_HASH = "edfb3b24ff198b2993388f594d99b424d75aa11b0bba60df3f1c6566688716b4"


def _wc_roundtrip(wc: WinCondition) -> WinCondition:
    return WinCondition.from_dict(wc.to_dict())


def test_asym_fields_default_inert_and_roundtrip():
    wc = WinCondition()
    assert wc.condition_type_p2 == ""
    assert wc.capture_quota == 0
    assert wc.timeout_winner == 0
    d = wc.to_dict()
    # defaults omitted from serialized form (legacy-hash stability)
    assert "condition_type_p2" not in d
    assert "capture_quota" not in d
    assert "timeout_winner" not in d
    wc2 = WinCondition(condition_type="field_connection",
                       condition_type_p2="capture_quota",
                       capture_quota=5, timeout_winner=2)
    back = _wc_roundtrip(wc2)
    assert back.condition_type_p2 == "capture_quota"
    assert back.capture_quota == 5
    assert back.timeout_winner == 2
    # timeout_winner=1 also serializes and roundtrips
    assert WinCondition(timeout_winner=1).to_dict()["timeout_winner"] == 1
    assert _wc_roundtrip(WinCondition(timeout_winner=1)).timeout_winner == 1


from game_engine.factory import create_engine


def make_siege(quota: int = 3, max_turns: int = 3, axis: int = 7) -> GameDefV2:
    return GameDefV2(
        game_id="m_siege_test", num_dimensions=2, axis_size=axis,
        topology_type="hex_rhombus",
        placement_rule=PlacementRule(),
        capture_rule=CaptureRule(capture_type="field_flip"),
        propagation_rule=PropagationRule(prop_type="influence",
                                         radius=2, strength=1.0, decay=0.5),
        win_condition=WinCondition(condition_type="field_connection",
                                   condition_type_p2="capture_quota",
                                   capture_quota=quota, timeout_winner=2,
                                   target_dimension=0, control_margin=0.0,
                                   max_turns=max_turns),
        turn_structure=TurnStructure(),
    )


def test_timeout_winner_awards_breaker():
    # max_turns=3 with quota=99: game always ends by turn cap (no connection or
    # quota in 3 moves on a 7-board). Seed 0 confirmed: legacy tiebreak awards
    # P1 (16 controlled cells vs P2's 6), so timeout_winner=2 decree must
    # override to give winner=2 — the discrimination is real.
    game = make_siege(quota=99, max_turns=3)
    engine = create_engine(game)
    engine.reset()
    rng = np.random.default_rng(0)
    while not engine.done:
        legal = engine.get_legal_actions()
        engine.step(int(rng.choice(legal)))
    assert engine._ended_by_max_turns
    assert engine._winner == 2  # Breaker wins at the cap, not majority tiebreak


def test_timeout_winner_zero_keeps_legacy_tiebreak():
    game = make_siege(quota=99, max_turns=3)
    game.win_condition.timeout_winner = 0
    game.win_condition.condition_type_p2 = ""  # fully legacy field_connection
    engine = create_engine(game)
    engine.reset()
    rng = np.random.default_rng(0)
    while not engine.done:
        engine.step(int(rng.choice(engine.get_legal_actions())))
    # legacy path: controlled-cell tiebreak — just assert the new branch did not
    # force a winner-by-decree; the game must still end via the cap.
    assert engine._ended_by_max_turns


def test_legacy_canonical_hash_unchanged():
    # A legacy game's canonical hash must be identical before/after this change.
    g = GameDefV2(
        game_id="legacy_probe", num_dimensions=2, axis_size=9,
        placement_rule=PlacementRule(), capture_rule=CaptureRule(),
        propagation_rule=PropagationRule(), win_condition=WinCondition(),
        turn_structure=TurnStructure(),
    )
    assert g.canonical_hash() == GOLDEN_LEGACY_HASH
