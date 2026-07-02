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
    a.reeval_full_conv(lambda g, c: -0.1)   # negative -> floors to 0 in mean
    elite = next(iter(a.cells.values()))
    assert elite.full_conv == [0.2, -0.1]
    assert abs(elite.full_conv_mean_floored - 0.1) < 1e-12   # mean(0.2, 0)


def test_reeval_full_conv_none_is_counted_and_skipped():
    # EVAL_TIMEOUT/EVAL_ERROR during a re-eval (§2): elite keeps its ledger.
    a = CampaignArchive()
    a.offer(StubGame(), "c1", ("connection", 2, 2), desc_batch(), 0.30, PASS_GUARD)
    a.reeval_full_conv(FULL)
    a.reeval_full_conv(lambda g, c: None)   # failed batch
    elite = next(iter(a.cells.values()))
    assert elite.full_conv == [0.2]
    assert a.counters["reeval_failed"] == 1
