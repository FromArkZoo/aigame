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
    # Non-threshold family: REACH never vetoes regardless of draw count
    # (even draw-heavy).
    r = gs._verdict_from_shares(rush=0.30, tilt=0.50, reach_count=10,
                                reach_n=24, family="connection")
    assert "reach" not in r["vetoes"]
    # Draw-heavy threshold genome (>= 5/24 winner-None) -> REACH FIRES ->
    # veto (S2-style draw pathology; CAL-R: S2 fires 10/24).
    r2 = gs._verdict_from_shares(rush=0.30, tilt=0.50, reach_count=6,
                                 reach_n=24, family="threshold")
    assert "reach" in r2["vetoes"] and r2["passed"] is False
    # Decisive threshold genome (low draws, e1453-style 1/24) -> no reach
    # veto (CAL-R B2: silent on e1453).
    r3 = gs._verdict_from_shares(rush=0.10, tilt=0.50, reach_count=1,
                                 reach_n=24, family="threshold")
    assert r3["passed"] is True and r3["vetoes"] == []


def test_thresholds_applied():
    # rush >= 0.25 -> rush veto; tilt >= 0.625 -> tilt veto (fires on HIGH
    # share, confirmed against CAL-G / guard_rush / guard_tilt polarity).
    r = gs._verdict_from_shares(rush=0.30, tilt=0.70, reach_count=2,
                                reach_n=24, family="threshold")
    assert set(r["vetoes"]) == {"rush", "tilt"}
    r_ok = gs._verdict_from_shares(rush=0.10, tilt=0.40, reach_count=3,
                                   reach_n=24, family="threshold")
    assert r_ok["passed"] is True and r_ok["vetoes"] == []


def _stub_tactical_rollout():
    """Canned decisive, long, seat-balanced tactical records — rush share 0
    (plies >> RUSH_PLY_CAP), tilt P1 share 0.5 — so neither RUSH nor TILT
    fires and only the REACH input varies."""
    state = {"i": 0}

    def fake_rollout(game, seed_p1, seed_p2):
        state["i"] += 1
        return {"winner": 1 if state["i"] % 2 else 2, "plies": 40}

    return fake_rollout


def test_run_guard_stage_reach_polarity_each_side_of_fire_count(monkeypatch):
    # Direct run_guard_stage coverage of the CAL-R-registered polarity — the
    # gap that let the inversion through. Stubbed rollout_tactical, no
    # engine; a threshold genome each side of the 5/24 fire count.
    monkeypatch.setattr(gs, "rollout_tactical", _stub_tactical_rollout())
    fired = gs.run_guard_stage(game=None, canon="a" * 64, family="threshold",
                               reach_draw_count=6)
    assert "reach" in fired["vetoes"] and fired["passed"] is False

    monkeypatch.setattr(gs, "rollout_tactical", _stub_tactical_rollout())
    silent = gs.run_guard_stage(game=None, canon="a" * 64, family="threshold",
                                reach_draw_count=3)
    assert silent["passed"] is True and silent["vetoes"] == []


def test_reach_fire_count_pinned_to_cal_r():
    # cal_r is a script but import-safe (main() is __main__-guarded; its
    # imports are the same ROSTER/play_cell modules the suite already loads).
    from experiments.rc2_campaign import cal_r
    assert gs.REACH_FIRE_COUNT == cal_r.FIRE_COUNT
