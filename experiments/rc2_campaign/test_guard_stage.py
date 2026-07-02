import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from experiments.rc2_campaign import guard_stage as gs


def test_pair_seeds_content_derived_and_mirrored():
    p = gs.guard_pair_seeds("a" * 64, n_pairs=12)
    assert len(p) == 12
    (a, b), (c, d) = p[0]
    assert (c, d) == (b, a)                    # mirrored
    assert gs.guard_pair_seeds("a" * 64) != gs.guard_pair_seeds("b" * 64)  # content


def test_reach_only_binds_threshold():
    # Non-threshold family: REACH never vetoes regardless of draw count.
    r = gs._verdict_from_shares(rush=0.30, tilt=0.50, reach_count=0,
                                reach_n=24, family="connection")
    assert "reach" not in r["vetoes"]
    # Threshold family with too few draws -> reach veto.
    r2 = gs._verdict_from_shares(rush=0.30, tilt=0.50, reach_count=4,
                                 reach_n=24, family="threshold")
    assert "reach" in r2["vetoes"] and r2["passed"] is False


def test_thresholds_applied():
    # rush >= 0.25 -> rush veto; tilt >= 0.625 -> tilt veto (fires on HIGH
    # share, confirmed against CAL-G / guard_rush / guard_tilt polarity).
    r = gs._verdict_from_shares(rush=0.30, tilt=0.70, reach_count=10,
                                reach_n=24, family="threshold")
    assert set(r["vetoes"]) == {"rush", "tilt"}
    r_ok = gs._verdict_from_shares(rush=0.10, tilt=0.40, reach_count=6,
                                   reach_n=24, family="threshold")
    assert r_ok["passed"] is True and r_ok["vetoes"] == []
