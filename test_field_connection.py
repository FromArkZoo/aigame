"""Field-Connect probe — engine tests for the field_connection win condition.

Spec: docs/superpowers/specs/2026-06-07-field-connect-probe-design.md (v2).
"""
from __future__ import annotations

import numpy as np

from game_engine.rules import WinCondition


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
