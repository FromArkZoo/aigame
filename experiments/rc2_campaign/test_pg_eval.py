import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.rc2_campaign.pg_eval import (
    pg_seeds, pg_batch, T1_DEEP, T1_SHALLOW, T1_N,
)
from experiments.rc2_descriptor_v2.run_probe import load_roster_game

CANON = "0" * 64  # 16 leading hex zeros -> deterministic seed base


def test_t1_sims_pinned_to_cal_i():
    # cal_i is a script but import-safe (main() is __main__-guarded;
    # test_cal_i.py already imports it directly) — pin the CAL-I instrument
    # sims to the campaign T1 instrument it validates.
    from experiments.rc2_campaign import cal_i
    assert (cal_i.DEEP_SIMS, cal_i.SHALLOW_SIMS) == (T1_DEEP, T1_SHALLOW)


def test_seat_balance_and_determinism():
    s = pg_seeds(CANON, 0, n=24)
    assert len(s) == 24
    assert [seat for *_ , seat in s][:12] == [0] * 12   # first half deep=P1
    assert [seat for *_ , seat in s][12:] == [1] * 12
    assert pg_seeds(CANON, 0) == pg_seeds(CANON, 0)      # deterministic
    assert pg_seeds(CANON, 0) != pg_seeds(CANON, 1)      # batch_index varies


def test_pg_batch_shape_and_reproducible():
    game = load_roster_game("d4015a646ae3")
    r1 = pg_batch(game, "d4015a646ae30000" + "0" * 48, deep_sims=32, shallow_sims=8, n=8)
    r2 = pg_batch(game, "d4015a646ae30000" + "0" * 48, deep_sims=32, shallow_sims=8, n=8)
    assert r1["raw_pg"] == r2["raw_pg"]                  # reproducible
    assert r1["wins"] + r1["draws"] + r1["losses"] == 8
    assert abs(r1["raw_pg"] - (sum(r1["scores"]) / 8 - 0.5)) < 1e-12
    assert r1["floored_pg"] == max(r1["raw_pg"], 0.0)
    assert 0.0 <= r1["non_draw_share"] <= 1.0
