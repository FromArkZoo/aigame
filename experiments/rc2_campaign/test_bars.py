import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pytest
from experiments.rc2_campaign import bars as B


def test_decide_verdict_precedence_all_branches():
    d = B.decide_verdict
    assert d(cal_i_pass=False, incomplete=None, bar_w_verdict="PASS",
             bar_h_verdict="PASS", slate_verdict="GO") == "PROBE_INVALID"
    assert d(cal_i_pass=True, incomplete="wall_cap", bar_w_verdict="PASS",
             bar_h_verdict="PASS", slate_verdict="GO") == "PROBE_INCOMPLETE"
    assert d(cal_i_pass=True, incomplete=None, bar_w_verdict="ARCHIVE_KILL",
             bar_h_verdict="PASS", slate_verdict="GO") == "ARCHIVE_KILL"
    assert d(cal_i_pass=True, incomplete=None, bar_w_verdict="ARCHIVE_KILL",
             bar_h_verdict="PROBE_INCOMPLETE", slate_verdict=None) == "ARCHIVE_KILL"
    assert d(cal_i_pass=True, incomplete=None, bar_w_verdict="PROBE_INCOMPLETE",
             bar_h_verdict="PASS", slate_verdict="GO") == "PROBE_INCOMPLETE"
    assert d(cal_i_pass=True, incomplete=None, bar_w_verdict="PASS",
             bar_h_verdict="SEARCH_NEUTRAL", slate_verdict=None) == "SEARCH_NEUTRAL"
    assert d(cal_i_pass=True, incomplete=None, bar_w_verdict="PASS",
             bar_h_verdict="PROBE_INCOMPLETE", slate_verdict=None) == "PROBE_INCOMPLETE"
    for sv in ("GO", "GO-PARTIAL", "NO-GO", "CAMPAIGN_UNRESOLVED", "SLATE_INCOMPLETE"):
        assert d(cal_i_pass=True, incomplete=None, bar_w_verdict="PASS",
                 bar_h_verdict="PASS", slate_verdict=sv) == sv
    with pytest.raises(ValueError):
        d(cal_i_pass=True, incomplete=None, bar_w_verdict="PASS",
          bar_h_verdict="PASS", slate_verdict="BOGUS")


def test_bar_w_quantifier():
    live = {f"F{i}": [0.0, 0.30] for i in range(2)}    # spread 0.30 >= floor -> LIVE
    dead = {"D": [0.10, 0.12]}                          # spread ~0 -> DEAD
    small = {"S": [0.0] * 5}                            # < 20 -> not qualifying
    fams = {**{k: v * 15 for k, v in live.items()}, "D": dead["D"] * 20, "S": small["S"]}
    r = B.bar_w(fams)
    assert r["n_qualifying"] == 3 and r["n_live"] == 2 and r["verdict"] == "PASS"
    r2 = B.bar_w({"D": dead["D"] * 20})
    assert r2["verdict"] == "PROBE_INCOMPLETE"          # <2 qualifying
    r3 = B.bar_w({"D": dead["D"] * 20, "E": dead["D"] * 20})
    assert r3["verdict"] == "ARCHIVE_KILL"              # 2 qualifying, 0 live


def test_bar_h_normal_and_saturation():
    assert B.bar_h(0.30, 0.20, 12, 12)["verdict"] == "PASS"        # gap 0.10 >= 0.05
    assert B.bar_h(0.22, 0.20, 12, 12)["verdict"] == "SEARCH_NEUTRAL"  # gap 0.02
    assert B.bar_h(0.30, 0.20, 8, 12)["verdict"] == "PROBE_INCOMPLETE" # <10 elites
    # saturation: R_top10 >= 0.40 -> switch to per-cell wins
    sat = B.bar_h(0.55, 0.45, 12, 12, joint_cells=[True] * 13 + [False] * 8)
    assert sat["metric"] == "per_cell_wins"
    assert sat["verdict"] == "PASS"                                # 13/21 ~= 0.619 >= 0.60
    sat_neutral = B.bar_h(0.55, 0.45, 12, 12, joint_cells=[True] * 11 + [False] * 10)
    assert sat_neutral["metric"] == "per_cell_wins"
    assert sat_neutral["verdict"] == "SEARCH_NEUTRAL"              # 11/21 ~= 0.524 < 0.60
    assert B.bar_h(0.55, 0.45, 12, 12, joint_cells=[True] * 10)["verdict"] == "PROBE_INCOMPLETE"


def test_slate_bars():
    # top-3 mean high, contrast low, separation clear, d4015 in band -> GO
    ts = {"m1": [4.2, 4.1, 4.3], "m2": [3.9]*3, "m3": [3.8]*3,
          "c1": [3.4]*3, "c2": [3.3]*3}
    full = {"m1": 0.4, "m2": 0.35, "m3": 0.3, "c1": 0.1, "c2": 0.05}
    r = B.slate_bars(ts, ["m1", "m2", "m3"], ["c1", "c2"], full, d4015_score=3.9)
    assert r["verdict"] == "GO"
    # min-contrast too small -> SEPARATION_UNDERDETERMINED -> GO-PARTIAL if sgo1 & band
    full2 = {"m1": 0.4, "m2": 0.35, "m3": 0.3, "c1": 0.28, "c2": 0.27}  # min-max < 0.15
    r2 = B.slate_bars(ts, ["m1", "m2", "m3"], ["c1", "c2"], full2, d4015_score=3.9)
    assert r2["separation_state"] == "SEPARATION_UNDERDETERMINED"
    assert r2["verdict"] == "GO-PARTIAL"
    # d4015 out of band -> CAMPAIGN_UNRESOLVED regardless
    r3 = B.slate_bars(ts, ["m1", "m2", "m3"], ["c1", "c2"], full, d4015_score=4.9)
    assert r3["verdict"] == "CAMPAIGN_UNRESOLVED"
    # sgo1 fails (no top-3 reaches 4.10) -> NO-GO
    ts_low = {k: [3.5]*3 for k in ts}
    r4 = B.slate_bars(ts_low, ["m1", "m2", "m3"], ["c1", "c2"], full, d4015_score=3.9)
    assert r4["verdict"] == "NO-GO"
    # sgo1 passes, band ok, min-contrast ok, but pooled separation < 0.4 -> NO-GO
    ts5 = {"m1": [4.2]*3, "m2": [4.0]*3, "m3": [3.9]*3,
           "c1": [3.9]*3, "c2": [3.8]*3}
    full5 = {"m1": 0.4, "m2": 0.35, "m3": 0.3, "c1": 0.1, "c2": 0.05}
    r5 = B.slate_bars(ts5, ["m1", "m2", "m3"], ["c1", "c2"], full5, d4015_score=3.9)
    assert r5["separation_state"] == "OK"
    assert r5["verdict"] == "NO-GO"
