"""Unit tests for the pre-registered mechanical-screen metric functions."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from experiments.field_connect_probe.metrics import (  # noqa: E402
    count_lead_changes,
    largest_component,
)
from game_engine.topology import TopologicalSpace  # noqa: E402


def test_count_lead_changes_skips_zeros() -> None:
    # signs: + + - (0 skipped) - +  -> flips: +to-, -to+  = 2
    assert count_lead_changes([1.0, 2.0, -1.0, 0.0, -2.0, 3.0]) == 2


def test_count_lead_changes_monotone_is_zero() -> None:
    assert count_lead_changes([0.5, 1.0, 3.0]) == 0
    assert count_lead_changes([]) == 0
    assert count_lead_changes([0.0, 0.0]) == 0


def test_largest_component_on_rhombus() -> None:
    t = TopologicalSpace(2, 6, "hex_rhombus")
    cells = {t.coords_to_cell((2, r)) for r in range(4)}          # 4-chain
    cells |= {t.coords_to_cell((5, 5))}                            # isolated
    assert largest_component(t, cells) == 4
    assert largest_component(t, set()) == 0
