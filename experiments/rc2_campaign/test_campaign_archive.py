import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from evolution.qd_archive import BatchResult
from experiments.rc2_campaign.campaign_archive import CampaignArchive, CampaignElite


class StubWin:
    def __init__(self, ct="connection", mt=100):
        self.condition_type, self.max_turns = ct, mt

class StubGame:
    def __init__(self, ct="connection"):
        self.win_condition = StubWin(ct)
    def to_dict(self):
        return {"ct": self.win_condition.condition_type}

def desc_batch(interaction=0.1, length=40.0, n=20):
    # non-draw majority, length ok -> descriptor-valid
    return BatchResult(batch_n=n, dramas=[0.3] * n, draws=0,
                       interactions=[interaction] * n, lengths=[length] * n)

PASS_GUARD = lambda g, c, fam: {"passed": True, "vetoes": []}
VETO_GUARD = lambda g, c, fam: {"passed": False, "vetoes": ["rush"]}
FULL = lambda g, c: 0.2


def test_empty_cell_fills_when_guard_passes():
    a = CampaignArchive()
    out = a.offer(StubGame(), "c1", ("connection", 2, 2), desc_batch(), 0.30, PASS_GUARD)
    assert out == "filled_empty_cell" and a.coverage == 1


def test_guard_vetoes_first_occupancy():
    a = CampaignArchive()
    out = a.offer(StubGame(), "c1", ("connection", 2, 2), desc_batch(), 0.30, VETO_GUARD)
    assert out == "guard_vetoed_rush" and a.coverage == 0


def test_strict_improvement_only_and_floor():
    a = CampaignArchive()
    cell = ("connection", 2, 2)
    a.offer(StubGame(), "c1", cell, desc_batch(), 0.30, PASS_GUARD)
    # equal floored PG never displaces
    assert a.offer(StubGame(), "c2", cell, desc_batch(), 0.30, PASS_GUARD) == "lost_first_batch"
    # 0-vs-0 never displaces (both floor to 0)
    b = CampaignArchive()
    b.offer(StubGame(), "z1", cell, desc_batch(), -0.1, PASS_GUARD)   # floored 0 -> fills empty
    assert b.offer(StubGame(), "z2", cell, desc_batch(), -0.2, PASS_GUARD) == "lost_first_batch"
    # strictly better displaces (guard runs because it would enter)
    assert a.offer(StubGame(), "c3", cell, desc_batch(), 0.45, PASS_GUARD) == "replaced"


def test_descriptor_invalid_rejected_before_guard():
    a = CampaignArchive()
    bad = BatchResult(batch_n=20, dramas=[0.3] * 5, draws=15,  # draw majority
                      interactions=[0.1] * 20, lengths=[40.0] * 20)
    out = a.offer(StubGame(), "c1", ("connection", 2, 2), bad, 0.9, PASS_GUARD)
    assert out.startswith("invalid_")


def test_reeval_full_conv_ledger():
    a = CampaignArchive()
    a.offer(StubGame(), "c1", ("connection", 2, 2), desc_batch(), 0.30, PASS_GUARD)
    a.reeval_full_conv(FULL)
    a.reeval_full_conv(lambda g, c: -0.1)   # raw ledger; floor AFTER pooling
    elite = next(iter(a.cells.values()))
    assert elite.full_conv == [0.2, -0.1]
    # floor-of-POOLED (§6 "post-final-checkpoint pooled", BUILD_LOG #12):
    # mean(0.2, -0.1) = 0.05 -> floored 0.05 (NOT mean(0.2, 0) = 0.1)
    assert abs(elite.full_conv_mean_floored - 0.05) < 1e-12


def test_full_conv_mean_floored_floors_negative_pool_to_zero():
    a = CampaignArchive()
    a.offer(StubGame(), "c1", ("connection", 2, 2), desc_batch(), 0.30, PASS_GUARD)
    a.reeval_full_conv(lambda g, c: -0.3)
    a.reeval_full_conv(lambda g, c: 0.1)
    elite = next(iter(a.cells.values()))
    assert elite.full_conv_mean_floored == 0.0   # pooled -0.1 -> floored 0.0


def test_reeval_full_conv_none_is_counted_and_skipped():
    # EVAL_TIMEOUT/EVAL_ERROR during a re-eval (§2): elite keeps its ledger.
    a = CampaignArchive()
    a.offer(StubGame(), "c1", ("connection", 2, 2), desc_batch(), 0.30, PASS_GUARD)
    a.reeval_full_conv(FULL)
    a.reeval_full_conv(lambda g, c: None)   # failed batch
    elite = next(iter(a.cells.values()))
    assert elite.full_conv == [0.2]
    assert a.counters["reeval_failed"] == 1


def test_archive_serialization_round_trip_via_json():
    # Full to_dict -> json.dumps -> json.loads -> from_dict equality:
    # cells (tuple keys), canon, t1 values, full_conv ledger, counters,
    # seen; game via the stub's to_dict/from_dict.
    a = CampaignArchive()
    a.mark_seen("spent_but_never_inserted")
    a.offer(StubGame("connection"), "c1", ("connection", 2, 2),
            desc_batch(), 0.30, PASS_GUARD)
    a.offer(StubGame("territory"), "t1", ("territory", 1, 3),
            desc_batch(interaction=0.4, length=22.0), -0.05, PASS_GUARD)
    a.offer(StubGame("connection"), "c2", ("connection", 2, 2),
            desc_batch(), 0.10, PASS_GUARD)          # lost_first_batch counter
    a.reeval_full_conv(FULL)
    a.reeval_full_conv(lambda g, c: -0.1)

    d = json.loads(json.dumps(a.to_dict()))
    b = CampaignArchive.from_dict(d, lambda gd: StubGame(gd["ct"]))

    assert b.to_dict() == a.to_dict()
    assert b.seen == a.seen
    assert b.counters == a.counters
    assert set(b.cells) == set(a.cells)              # tuple keys restored
    for cell in a.cells:
        ea, eb = a.cells[cell], b.cells[cell]
        assert (eb.canon, eb.cell, eb.t1_raw, eb.t1_floored, eb.full_conv) \
            == (ea.canon, ea.cell, ea.t1_raw, ea.t1_floored, ea.full_conv)
        assert eb.full_conv_mean_floored == ea.full_conv_mean_floored
        assert eb.descriptor_batch.to_dict() == ea.descriptor_batch.to_dict()
        assert eb.game.to_dict() == ea.game.to_dict()
