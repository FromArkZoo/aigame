"""FRONTLINE engine tests (contested_majority — spec §3/§5, prereg-locked).

Run: .venv/bin/python -m pytest test_frontline_engine.py -q
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from game_engine.factory import create_engine
from game_engine.game_def_v2 import GameDefV2
from game_engine.rules import (
    ActionRule, CaptureRule, PlacementRule, PropagationRule,
    TurnStructure, WinCondition, WIN_CONDITION_TYPES,
)

W = 22


def make_cm_game(
    engage_threshold: float = 1.0,
    end_margin: int = 8,
    min_turns: int = 20,
    komi_cells: int = 0,
    max_turns: int = 200,
    pie: bool = False,
) -> GameDefV2:
    """Frontline test fixture — prereg arm config, pie OFF by default so
    tests drive deterministic sequences (pie covered by its own test)."""
    return GameDefV2(
        game_id="f_test",
        num_dimensions=2,
        axis_size=W,
        topology_type="hex_rhombus",
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="field_flip"),
        propagation_rule=PropagationRule(
            prop_type="influence", radius=2, strength=1.0, decay=0.5),
        win_condition=WinCondition(
            condition_type="contested_majority",
            engage_threshold=engage_threshold,
            end_margin=end_margin,
            min_turns_score_end=min_turns,
            komi_cells=komi_cells,
            max_turns=max_turns,
            control_margin=0.0,
        ),
        pie_rule=pie,
    )


def test_wincondition_serde_roundtrip():
    wc = WinCondition(
        condition_type="contested_majority", engage_threshold=1.0,
        end_margin=8, min_turns_score_end=20, komi_cells=1, max_turns=200,
    )
    d = wc.to_dict()
    wc2 = WinCondition.from_dict(d)
    assert wc2.engage_threshold == 1.0
    assert wc2.end_margin == 8
    assert wc2.min_turns_score_end == 20
    assert wc2.komi_cells == 1


def test_legacy_serde_omits_frontline_keys():
    legacy = WinCondition(condition_type="connection")
    d = legacy.to_dict()
    for key in ("engage_threshold", "end_margin",
                "min_turns_score_end", "komi_cells"):
        assert key not in d, f"legacy to_dict leaked {key}"
    # back-compat: from_dict on a dict without the new keys
    wc = WinCondition.from_dict({"condition_type": "connection"})
    assert wc.engage_threshold == 0.0 and wc.komi_cells == 0


def test_contested_majority_not_generated():
    assert "contested_majority" not in WIN_CONDITION_TYPES


def test_legacy_canonical_hash_unchanged():
    src = Path("experiments/fc_phase15/games/calibrated/a1_field_connect.json")
    g = GameDefV2.from_dict(json.loads(src.read_text()))
    g2 = GameDefV2.from_dict(json.loads(json.dumps(g.to_dict())))
    assert g2.canonical_hash() == g.canonical_hash()
