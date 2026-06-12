"""Fast tests for experiments/frontline/run_screen.py — NO training.

Covers the pure Stage-2 bar logic (screen_verdict and friends operate on
synthetic aggregate dicts — the calibrate.apply_gates pattern):
  (a) verdict logic: GO / NOGO / CAMPAIGN_UNRESOLVED for every failure
      class (comparative, band, comparator health, collapsed seeds,
      reproduction check) + UNRESOLVED precedence over family verdicts;
  (b) directional comparative floors at their exact boundaries;
  (c) exploiter pooling (ratio of totals, per (opponent, seat), BOTH
      seats must clear).

Run via:
    .venv/bin/python -m pytest experiments/frontline/test_frontline_screen.py -q
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from experiments.frontline.run_screen import (
    A1_A0_FLIP_REPRO_MIN,
    CENTRALITY_FLOOR,
    FLIP_DELTA_FLOOR,
    MIRROR_BEAT_MIN,
    PASSBOT_BEAT_MIN,
    arm_agg,
    comparative_checks,
    comparator_health,
    f_band_checks,
    pool_shares,
    repro_check,
    screen_verdict,
)


# ---------------------------------------------------------------------------
# Synthetic aggregates (all-passing defaults; tests override one knob)
# ---------------------------------------------------------------------------

def _arm(**over):
    a = dict(control_flip_rate=6.0, game_length=95.0, lead_changes=3.0,
             drama=0.05, flip_events=5.0, distinct_flip_ratio=0.8,
             engaged_mean=0.15, timeout_share=0.10, draw_rate=0.00,
             score_margin_share=0.60, double_pass_share=0.20, bias=0.05,
             tvr_mean=0.85, tvr_min=0.80,
             tvr_by_seed={42: 0.85, 43: 0.80, 44: 0.90},
             collapsed_seeds=[])
    a.update(over)
    return a


def _aggs(f=None, s=None, a1=None, a0=None, exploiter=None, packer=None):
    return dict(
        arms={
            # Defaults clear everything: flip delta 7-5 = 2 >= 0.5;
            # centrality |120-95|=25 vs |95-95|=0 -> gain 25 >= 10.
            "f_frontline": _arm(**(f or {})),
            "s_flip_r2": _arm(**{"control_flip_rate": 5.0,
                                 "game_length": 120.0, **(s or {})}),
            "a1_field_connect": _arm(**{"control_flip_rate": 10.6,
                                        **(a1 or {})}),
            "a0_baseline": _arm(**{"control_flip_rate": 5.3,
                                   **(a0 or {})}),
        },
        exploiter=exploiter or {"passbot": {"p1": 0.95, "p2": 0.95},
                                "mirror": {"p1": 0.80, "p2": 0.75}},
        packer_mean_total=1.0 if packer is None else packer,
    )


# ---------------------------------------------------------------------------
# (a) Verdict logic
# ---------------------------------------------------------------------------

def test_all_pass_is_screen_go():
    verdict, reasons = screen_verdict(_aggs(f=dict(control_flip_rate=7.0)))
    assert verdict == "SCREEN_GO"
    assert "2/2 comparatives" in reasons[0]


def test_one_comparative_fail_is_nogo():
    # flip delta 5.4 - 5.0 = +0.4 < +0.5 -> 1/2 comparatives -> NOGO.
    verdict, reasons = screen_verdict(_aggs(f=dict(control_flip_rate=5.4)))
    assert verdict == "SCREEN_NOGO"
    assert reasons[0].startswith("1/2 comparatives")
    assert any("control_flip_rate" in r for r in reasons)


def test_band_fail_is_nogo():
    verdict, reasons = screen_verdict(_aggs(f=dict(draw_rate=0.10)))
    assert verdict == "SCREEN_NOGO"
    assert any(r.startswith("band FAIL: draw_rate") for r in reasons)


def test_comparator_health_fail_is_unresolved_never_family_verdict():
    verdict, reasons = screen_verdict(_aggs(a1=dict(bias=0.20)))
    assert verdict == "CAMPAIGN_UNRESOLVED"
    assert any("comparator failure (a1_field_connect)" in r
               for r in reasons)
    # Even when F's bands ALSO fail, comparator failure dominates: the
    # verdict must never be a family NOGO on an invalid comparison.
    verdict, _ = screen_verdict(_aggs(f=dict(draw_rate=0.50),
                                      a1=dict(bias=0.20)))
    assert verdict == "CAMPAIGN_UNRESOLVED"


def test_collapsed_comparator_seed_is_unresolved():
    verdict, reasons = screen_verdict(_aggs(s=dict(collapsed_seeds=[43])))
    assert verdict == "CAMPAIGN_UNRESOLVED"
    assert any("comparator failure (s_flip_r2)" in r and "collapsed" in r
               for r in reasons)


def test_comparator_tvr_floor_fail_is_unresolved():
    verdict, reasons = screen_verdict(_aggs(a0=dict(tvr_mean=0.70)))
    assert verdict == "CAMPAIGN_UNRESOLVED"
    assert any("comparator failure (a0_baseline)" in r for r in reasons)


def test_collapsed_f_screen_seed_is_unresolved_not_nogo():
    # The Stage-1 rerun ladder does not apply at screen time; a collapsed
    # F seed is CAMPAIGN_UNRESOLVED, never a family verdict — even with
    # F bands failing too.
    verdict, reasons = screen_verdict(
        _aggs(f=dict(collapsed_seeds=[44], draw_rate=0.50)))
    assert verdict == "CAMPAIGN_UNRESOLVED"
    assert any("collapsed screen seed (f_frontline)" in r for r in reasons)


def test_repro_fail_is_unresolved_and_dominates_comparative_fail():
    # a1 - a0 = 7.0 - 5.3 = 1.7 < 3.0 -> instrumentation INVALID.
    verdict, reasons = screen_verdict(_aggs(a1=dict(control_flip_rate=7.0)))
    assert verdict == "CAMPAIGN_UNRESOLVED"
    assert any("instrumentation reproduction FAILED" in r for r in reasons)
    # Dominates a would-be NOGO (comparative also failing).
    verdict, _ = screen_verdict(_aggs(f=dict(control_flip_rate=5.0),
                                      a1=dict(control_flip_rate=7.0)))
    assert verdict == "CAMPAIGN_UNRESOLVED"


def test_repro_boundary_exactly_3_passes():
    aggs = _aggs(a1=dict(control_flip_rate=8.3),
                 a0=dict(control_flip_rate=5.3))
    delta, ok = repro_check(aggs)
    assert delta == pytest.approx(A1_A0_FLIP_REPRO_MIN)
    assert ok
    verdict, _ = screen_verdict(aggs)
    assert verdict == "SCREEN_GO"


# ---------------------------------------------------------------------------
# (b) Directional comparative floors at the boundary
# ---------------------------------------------------------------------------

def test_flip_delta_directional_floor_boundary():
    # F - S = +0.4 -> comparative 1 FAILS; = +0.5 -> passes.
    s = _arm(control_flip_rate=5.0, game_length=120.0)
    name, val, _, ok = comparative_checks(
        _arm(control_flip_rate=5.4), s)[0]
    assert val == pytest.approx(0.4) and not ok
    name, val, _, ok = comparative_checks(
        _arm(control_flip_rate=5.5), s)[0]
    assert val == pytest.approx(FLIP_DELTA_FLOOR) and ok


def test_flip_delta_is_directional_not_absolute_difference():
    # S ahead by 0.5 must NOT pass: the comparative is F - S, directional.
    s = _arm(control_flip_rate=6.5, game_length=120.0)
    _, val, _, ok = comparative_checks(_arm(control_flip_rate=6.0), s)[0]
    assert val == pytest.approx(-0.5) and not ok


def test_centrality_gain_floor_boundary():
    # |s-95| - |f-95| gain: 9.9 fails, 10.0 passes (F at the center).
    f = _arm(game_length=95.0)
    _, val, _, ok = comparative_checks(f, _arm(game_length=104.9))[1]
    assert val == pytest.approx(9.9) and not ok
    _, val, _, ok = comparative_checks(f, _arm(game_length=105.0))[1]
    assert val == pytest.approx(CENTRALITY_FLOOR) and ok


def test_centrality_requires_f_inside_length_band():
    # Huge gain but F outside [30,160] -> comparative 2 fails.
    _, val, _, ok = comparative_checks(
        _arm(game_length=20.0), _arm(game_length=200.0))[1]
    assert val > CENTRALITY_FLOOR and not ok


# ---------------------------------------------------------------------------
# (c) Exploiter pooling logic
# ---------------------------------------------------------------------------

def test_pool_shares_is_ratio_of_totals_not_mean_of_shares():
    # Unequal blocks separate the two definitions: ratio of totals
    # 59/110 ~ 0.536; mean of per-block shares would be 0.7.
    assert pool_shares([(9, 10), (50, 100)]) == pytest.approx(59 / 110)
    assert pool_shares([(45, 50), (50, 50), (40, 50)]) == pytest.approx(0.9)
    assert pool_shares([]) == 0.0  # max(1, n) guard


def test_exploiter_band_each_seat_must_clear():
    # One seat below the Mirror floor -> band FAIL -> NOGO.
    verdict, reasons = screen_verdict(_aggs(
        exploiter={"passbot": {"p1": 0.95, "p2": 0.95},
                   "mirror": {"p1": 0.80, "p2": 0.69}}))
    assert verdict == "SCREEN_NOGO"
    assert any("Mirror" in r and "P2" in r for r in reasons)
    # One seat below the PassBot floor likewise.
    verdict, reasons = screen_verdict(_aggs(
        exploiter={"passbot": {"p1": 0.89, "p2": 0.95},
                   "mirror": {"p1": 0.80, "p2": 0.75}}))
    assert verdict == "SCREEN_NOGO"
    assert any("PassBot" in r and "P1" in r for r in reasons)


def test_exploiter_floors_are_inclusive():
    verdict, _ = screen_verdict(_aggs(
        exploiter={"passbot": {"p1": PASSBOT_BEAT_MIN,
                               "p2": PASSBOT_BEAT_MIN},
                   "mirror": {"p1": MIRROR_BEAT_MIN,
                              "p2": MIRROR_BEAT_MIN}}))
    assert verdict == "SCREEN_GO"


def test_packer_band():
    verdict, reasons = screen_verdict(_aggs(packer=2.5))
    assert verdict == "SCREEN_NOGO"
    assert any("packer" in r for r in reasons)
    verdict, _ = screen_verdict(_aggs(packer=2.0))  # inclusive floor
    assert verdict == "SCREEN_GO"


# ---------------------------------------------------------------------------
# Aggregation helpers (pure, row-level)
# ---------------------------------------------------------------------------

def _row(arm, seed, **over):
    r = dict(arm=arm, game_id="g", seed=seed, game_length=95.0,
             lead_changes=3.0, control_flip_rate=6.0, drama=0.05,
             flip_events=5.0, flip_events_total=500,
             distinct_flips_total=400, timeout_share=0.10, draw_rate=0.0,
             score_margin_share=0.6, double_pass_share=0.2,
             engaged_mean=0.15, p1_share=0.5, bias=0.05, tvr=0.85,
             collapsed=False, elapsed_s=1.0)
    r.update(over)
    return r


def test_arm_agg_distinct_flip_ratio_is_ratio_of_totals():
    rows = [_row("f_frontline", 42, flip_events_total=100,
                 distinct_flips_total=100),
            _row("f_frontline", 43, flip_events_total=300,
                 distinct_flips_total=60)]
    a = arm_agg(rows, "f_frontline")
    # ratio of totals 160/400 = 0.4; mean of per-seed ratios would be 0.6.
    assert a["distinct_flip_ratio"] == pytest.approx(0.4)


def test_arm_agg_collapsed_seeds_and_tvr_floors():
    rows = [_row("s_flip_r2", 42, tvr=0.85),
            _row("s_flip_r2", 43, tvr=0.10, collapsed=True),
            _row("s_flip_r2", 44, tvr=0.90)]
    a = arm_agg(rows, "s_flip_r2")
    assert a["collapsed_seeds"] == [43]
    assert a["tvr_min"] == pytest.approx(0.10)
    ok, detail = comparator_health("s_flip_r2", a)
    assert not ok and "collapsed" in detail


def test_f_band_checks_every_bar_visible():
    # 13 rows: 8 F stats + packer + 4 exploiter seats — every bar decision
    # is rendered in the report.
    bands = f_band_checks(
        _arm(), {"passbot": {"p1": 0.95, "p2": 0.95},
                 "mirror": {"p1": 0.8, "p2": 0.75}}, 1.0)
    assert len(bands) == 13
    assert all(ok for *_, ok in bands)
