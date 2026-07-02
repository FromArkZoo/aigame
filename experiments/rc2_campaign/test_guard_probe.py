import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from metrics.guard_probe import (
    rollout_tactical, rush_share, tilt_p1_share,
    RUSH_PLY_CAP, RUSH_SHARE, TILT_SHARE_REPRICED,
)
from experiments.rc2_descriptor_v2.run_probe import load_roster_game


def test_constants():
    assert RUSH_PLY_CAP == 6 and RUSH_SHARE == 0.25 and TILT_SHARE_REPRICED == 0.625


def test_rollout_tactical_deterministic():
    game = load_roster_game("d4015a646ae3")
    a = rollout_tactical(game, 11, 22)
    b = rollout_tactical(game, 11, 22)
    assert a["winner"] == b["winner"] and a["plies"] == b["plies"]


def test_share_helpers_ignore_draws():
    recs = [
        {"winner": 1, "plies": 4}, {"winner": 2, "plies": 10},
        {"winner": None, "plies": 400}, {"winner": 1, "plies": 6},
    ]
    dec, s6 = rush_share(recs)
    assert dec == 3 and abs(s6 - 2/3) < 1e-9      # 2 of 3 decisive end <=6 plies
    dec2, p1 = tilt_p1_share(recs)
    assert dec2 == 3 and abs(p1 - 2/3) < 1e-9      # 2 of 3 decisive won by P1


def test_backcompat_reexport():
    from experiments.rc2_descriptor_v2.run_probe import rollout_tactical as rt
    assert rt is rollout_tactical
