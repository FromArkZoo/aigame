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


def test_legacy_canonical_hash_unchanged():
    # A legacy game's canonical hash must be identical before/after this change.
    g = GameDefV2(
        game_id="legacy_probe", num_dimensions=2, axis_size=9,
        placement_rule=PlacementRule(), capture_rule=CaptureRule(),
        propagation_rule=PropagationRule(), win_condition=WinCondition(),
        turn_structure=TurnStructure(),
    )
    assert g.canonical_hash() == GOLDEN_LEGACY_HASH
