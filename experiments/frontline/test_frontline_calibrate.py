"""Fast tests for experiments/frontline/calibrate.py — NO training.

Covers the pure prereg gate logic:
  (a) gate-order structure: a skill-failing cell never computes/reads bias
      (apply_gates short-circuits at the first failing gate; truncated
      stats dicts must never raise);
  (b) komi direction logic (P1-favored -> +1 first; P2-favored -> -1);
  (c) tie-break ordering on synthetic passing cells;
  (d) the bias formula (draws count half).

Run via:
    .venv/bin/python -m pytest experiments/frontline/test_frontline_calibrate.py -q
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import pytest

from experiments.frontline.calibrate import (
    BIAS_PASS,
    DOUBLE_PASS_YELLOW,
    KOMI_LADDER,
    apply_gates,
    bias_value,
    cell_name,
    rank_passing,
    signed_bias,
    signed_komi,
    skill_ok,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _Tripwire(dict):
    """Stats dict that fails the test if a forbidden key is ever read —
    the structural proof that gate N's failure prevents any gate-N+1
    access."""

    def __init__(self, base: dict, forbidden: set[str]):
        super().__init__(base)
        self._forbidden = forbidden

    def __getitem__(self, key):
        assert key not in self._forbidden, (
            f"gate ladder read forbidden later-gate key {key!r}")
        return super().__getitem__(key)

    def get(self, key, default=None):
        assert key not in self._forbidden, (
            f"gate ladder read forbidden later-gate key {key!r}")
        return super().get(key, default)


def _passing_agg(**over):
    agg = dict(timeout_share=0.10, draw_rate=0.00, score_margin_share=0.60,
               double_pass_share=0.20, engaged_mean=0.15, mean_length=95.0)
    agg.update(over)
    return agg


def _full_stats(**over):
    stats = dict(invalid=None, tvrs=[0.85, 0.80, 0.90], bias=0.05, komi=0,
                 agg=_passing_agg())
    stats.update(over)
    return stats


# ---------------------------------------------------------------------------
# (a) Gate-order structure
# ---------------------------------------------------------------------------

def test_invalid_cell_never_reads_skill_or_bias():
    stats = _Tripwire({"invalid": "seed 42 collapsed, reserves exhausted"},
                      forbidden={"tvrs", "bias", "komi", "agg"})
    verdict, reason = apply_gates(stats)
    assert verdict == "INVALID"
    assert "collapsed" in reason


def test_skill_failing_cell_never_computes_bias():
    # min tvr 0.50 < 0.65 floor -> FAIL at gate 1. The dict has NO
    # bias/komi/agg keys AND trips on any access to them: the only way
    # this passes is a structural early return at gate 1.
    stats = _Tripwire({"invalid": None, "tvrs": [0.50, 0.90, 0.90]},
                      forbidden={"bias", "komi", "agg"})
    verdict, reason = apply_gates(stats)
    assert verdict == "FAIL"
    assert reason.startswith("skill")


def test_skill_mean_floor_fires_independently_of_min_floor():
    # every seed >= 0.65 but mean 0.70 < 0.75 -> still FAIL skill
    stats = {"invalid": None, "tvrs": [0.70, 0.70, 0.70]}
    verdict, reason = apply_gates(stats)
    assert verdict == "FAIL" and reason.startswith("skill")
    ok, _ = skill_ok([0.70, 0.70, 0.70])
    assert not ok


def test_bias_failing_cell_never_reads_endcause_agg():
    stats = _Tripwire(
        {"invalid": None, "tvrs": [0.85, 0.80, 0.90], "bias": 0.20,
         "komi": -2},
        forbidden={"agg"})
    verdict, reason = apply_gates(stats)
    assert verdict == "FAIL"
    assert "bias 0.200" in reason
    assert str(BIAS_PASS) in reason


def test_gate3_order_timeout_before_draw_before_scoremargin():
    # all three gate-3 stats violated -> timeout (first check) is the reason
    stats = _full_stats(agg=_passing_agg(
        timeout_share=0.50, draw_rate=0.50, score_margin_share=0.0))
    verdict, reason = apply_gates(stats)
    assert verdict == "FAIL" and reason.startswith("timeout_share")
    # draw + score_margin violated -> draw fires before score_margin
    stats = _full_stats(agg=_passing_agg(
        draw_rate=0.50, score_margin_share=0.0))
    verdict, reason = apply_gates(stats)
    assert verdict == "FAIL" and reason.startswith("draw_rate")
    # only score_margin violated
    stats = _full_stats(agg=_passing_agg(score_margin_share=0.10))
    verdict, reason = apply_gates(stats)
    assert verdict == "FAIL" and reason.startswith("score_margin_share")


def test_gate3_failure_blocks_gate4_decision():
    # engaged ALSO out of band, but timeout fails first -> reason is timeout
    stats = _full_stats(agg=_passing_agg(timeout_share=0.90,
                                         engaged_mean=0.99))
    verdict, reason = apply_gates(stats)
    assert verdict == "FAIL"
    assert reason.startswith("timeout_share")
    assert "engaged" not in reason


def test_gate4_engaged_band_both_sides():
    verdict, reason = apply_gates(_full_stats(
        agg=_passing_agg(engaged_mean=0.01)))
    assert verdict == "FAIL" and reason.startswith("engaged")
    verdict, reason = apply_gates(_full_stats(
        agg=_passing_agg(engaged_mean=0.70)))
    assert verdict == "FAIL" and reason.startswith("engaged")


def test_all_gates_clear_passes():
    verdict, reason = apply_gates(_full_stats())
    assert verdict == "PASS"
    assert reason == "all gates clear"


def test_double_pass_yellow_is_flag_not_gate():
    stats = _full_stats(agg=_passing_agg(double_pass_share=0.60))
    verdict, reason = apply_gates(stats)
    assert verdict == "PASS DOUBLE_PASS_YELLOW"  # still a PASS
    assert verdict.startswith("PASS")
    assert str(DOUBLE_PASS_YELLOW) in reason


# ---------------------------------------------------------------------------
# (b) Komi direction logic
# ---------------------------------------------------------------------------

def test_komi_direction_p1_favored_positive_first():
    # P1-favored -> positive komi (komi_cells is added to P2's score)
    p1_favored = signed_bias(0.60, 0.00) > 0
    assert p1_favored
    assert signed_komi(KOMI_LADDER[0], p1_favored) == +1
    assert signed_komi(KOMI_LADDER[1], p1_favored) == +2


def test_komi_direction_p2_favored_negative_first():
    p1_favored = signed_bias(0.30, 0.10) > 0  # signed bias -0.15
    assert not p1_favored
    assert signed_komi(KOMI_LADDER[0], p1_favored) == -1
    assert signed_komi(KOMI_LADDER[1], p1_favored) == -2


def test_komi_direction_uses_draw_adjusted_sign():
    # p1_share 0.45 < 0.5 BUT draws 0.20 -> p2_share 0.35: P1 wins more
    # decided games. Prereg pins direction to the MEASURED bias sign
    # (draws count half): signed bias +0.05 -> P1-favored -> +komi.
    assert signed_bias(0.45, 0.20) == pytest.approx(0.05)
    assert signed_komi(1, signed_bias(0.45, 0.20) > 0) == +1


# ---------------------------------------------------------------------------
# (c) Tie-break ordering
# ---------------------------------------------------------------------------

def _cell(name, mean_length, score_margin_share, bias):
    return dict(cell=name, bias=bias,
                agg=dict(mean_length=mean_length,
                         score_margin_share=score_margin_share))


def test_tiebreak_centrality_then_scoremargin_then_bias():
    a = _cell("A", mean_length=100.0, score_margin_share=0.30, bias=0.05)
    b = _cell("B", mean_length=90.0, score_margin_share=0.50, bias=0.08)
    c = _cell("C", mean_length=94.0, score_margin_share=0.26, bias=0.10)
    ranked = rank_passing([a, b, c])
    # C wins on centrality (|94-95|=1 < 5); A/B tie centrality (5) ->
    # B wins on score_margin share; bias never consulted.
    assert [r["cell"] for r in ranked] == ["C", "B", "A"]


def test_tiebreak_bias_breaks_full_ties():
    d = _cell("D", mean_length=95.0, score_margin_share=0.40, bias=0.09)
    e = _cell("E", mean_length=95.0, score_margin_share=0.40, bias=0.02)
    assert [r["cell"] for r in rank_passing([d, e])] == ["E", "D"]


# ---------------------------------------------------------------------------
# (d) Bias formula
# ---------------------------------------------------------------------------

def test_bias_formula_draws_count_half():
    assert bias_value(0.50, 0.00) == 0.0
    assert bias_value(0.60, 0.00) == pytest.approx(0.10)
    assert bias_value(0.40, 0.00) == pytest.approx(0.10)
    # all draws = perfectly balanced
    assert bias_value(0.00, 1.00) == 0.0
    # draw-heavy meta cannot masquerade as balance: p1 wins every decided
    # game (p1 0.5, p2 0.0, draws 0.5) -> bias 0.25, NOT 0
    assert bias_value(0.50, 0.50) == pytest.approx(0.25)
    # symmetric: p2 wins every decided game
    assert bias_value(0.00, 0.50) == pytest.approx(0.25)


def test_cell_name_format():
    assert cell_name(1.0, 8) == "E1p00_M8"
    assert cell_name(0.75, 12) == "E0p75_M12"
    assert cell_name(1.25, 8) == "E1p25_M8"
