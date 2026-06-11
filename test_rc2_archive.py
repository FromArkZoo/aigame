"""Unit tests for RC2 Phase C: qd_archive mechanics + probe verdict grammar.

Archive tests use stub games/batches (no engine); the verdict tests exercise
every branch of the registered decision grammar synthetically (the Phase B
pattern: all verdict branches tested before any probe data).
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from evolution.qd_archive import (
    INTERACTION_EDGES,
    LENGTH_EDGES,
    BatchResult,
    Elite,
    QDArchive,
    bin_index,
    cell_key,
    validity,
)


# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------

class StubWC:
    def __init__(self, condition_type="connection", max_turns=100):
        self.condition_type = condition_type
        self.max_turns = max_turns


class StubGame:
    def __init__(self, condition_type="connection", max_turns=100, tag="g"):
        self.win_condition = StubWC(condition_type, max_turns)
        self.tag = tag

    def to_dict(self):
        return {
            "tag": self.tag,
            "condition_type": self.win_condition.condition_type,
            "max_turns": self.win_condition.max_turns,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(d["condition_type"], d["max_turns"], d["tag"])


def batch(drama, n=50, draws=0, interaction=0.15, length=50.0):
    """Batch with uniform per-rollout values; n - draws non-draw rollouts."""
    k = n - draws
    return BatchResult(
        batch_n=n,
        dramas=[drama] * k,
        draws=draws,
        interactions=[interaction] * n,
        lengths=[length] * n,
    )


def no_evals(game, batch_index, batch_n):  # pragma: no cover - guard
    raise AssertionError("evaluate_batch must not be called here")


# ---------------------------------------------------------------------------
# Binning
# ---------------------------------------------------------------------------

def test_bin_edges_interaction():
    assert bin_index(0.0, INTERACTION_EDGES) == 0
    assert bin_index(0.049, INTERACTION_EDGES) == 0
    assert bin_index(0.05, INTERACTION_EDGES) == 1
    assert bin_index(0.12, INTERACTION_EDGES) == 2
    assert bin_index(0.20, INTERACTION_EDGES) == 3
    assert bin_index(0.30, INTERACTION_EDGES) == 4
    assert bin_index(0.999, INTERACTION_EDGES) == 4
    # registered: values > 1.0 clamp into the top bin
    assert bin_index(1.0, INTERACTION_EDGES) == 4
    assert bin_index(2.5, INTERACTION_EDGES) == 4


def test_bin_edges_length_last_bin_upper_inclusive():
    assert bin_index(0.0, LENGTH_EDGES) == 0
    assert bin_index(0.2, LENGTH_EDGES) == 1
    assert bin_index(0.799, LENGTH_EDGES) == 3
    assert bin_index(0.8, LENGTH_EDGES) == 4
    assert bin_index(1.0, LENGTH_EDGES) == 4


def test_cell_key_pins_family_and_normalizes_length():
    g = StubGame("threshold", max_turns=200)
    b = batch(0.1, interaction=0.13, length=90.0)
    fam, ibin, lbin = cell_key(g, b)
    assert fam == "threshold"
    assert ibin == 2                      # 0.13 in [0.12, 0.20)
    assert lbin == 2                      # 90/200 = 0.45 in [0.4, 0.6)


def test_cell_key_clips_length_frac():
    g = StubGame(max_turns=10)
    b = batch(0.1, length=40.0)           # 40/10 -> clipped to 1.0
    assert cell_key(g, b)[2] == len(LENGTH_EDGES) - 2


# ---------------------------------------------------------------------------
# Validity guard
# ---------------------------------------------------------------------------

def test_validity_passes_clean_batch():
    assert validity(batch(0.1)) is None


def test_validity_rejects_draw_majority():
    assert validity(batch(0.1, n=50, draws=26)) == "draw_majority"
    assert validity(batch(0.1, n=50, draws=25)) is None  # exactly 50% ok


def test_validity_rejects_short_games():
    assert validity(batch(0.1, length=5.9)) == "too_short"


def test_validity_rejects_all_draw():
    b = BatchResult(batch_n=50, dramas=[], draws=50,
                    interactions=[0.1] * 50, lengths=[50.0] * 50)
    assert validity(b) == "draw_majority"


# ---------------------------------------------------------------------------
# Pooled means
# ---------------------------------------------------------------------------

def test_pooled_drama_weights_by_nondraw_count():
    e = Elite(game=StubGame(), canon="c", cell=("connection", 0, 0))
    e.batches.append(batch(0.10, n=50, draws=0))    # 50 rollouts at 0.10
    e.batches.append(batch(0.40, n=50, draws=40))   # 10 rollouts at 0.40
    expected = (50 * 0.10 + 10 * 0.40) / 60
    assert math.isclose(e.pooled_drama, expected)
    assert e.pooled_n == 100


def test_pooled_drama_skips_all_draw_batches():
    e = Elite(game=StubGame(), canon="c", cell=("connection", 0, 0))
    e.batches.append(batch(0.10))
    e.batches.append(BatchResult(batch_n=50, dramas=[], draws=50,
                                 interactions=[], lengths=[]))
    assert math.isclose(e.pooled_drama, 0.10)
    assert e.pooled_n == 100


# ---------------------------------------------------------------------------
# Insertion + eval-count matching
# ---------------------------------------------------------------------------

def test_offer_fills_empty_cell():
    arch = QDArchive()
    out = arch.offer(StubGame(), "a", batch(0.1), no_evals)
    assert out == "filled_empty_cell"
    assert arch.coverage == 1


def test_offer_invalid_consumes_no_cell():
    arch = QDArchive()
    out = arch.offer(StubGame(), "a", batch(0.1, n=50, draws=30), no_evals)
    assert out == "invalid_draw_majority"
    assert arch.coverage == 0


def test_offer_loses_on_first_batch_without_topup():
    arch = QDArchive()
    arch.offer(StubGame(tag="inc"), "inc", batch(0.30), no_evals)
    out = arch.offer(StubGame(tag="ch"), "ch", batch(0.10), no_evals)
    assert out == "lost_first_batch"
    assert arch.cells[("connection", 2, 2)].canon == "inc"


def test_offer_equal_first_batch_loses():
    arch = QDArchive()
    arch.offer(StubGame(tag="inc"), "inc", batch(0.30), no_evals)
    out = arch.offer(StubGame(tag="ch"), "ch", batch(0.30), no_evals)
    assert out == "lost_first_batch"


def test_topup_matches_eval_counts_then_replaces():
    arch = QDArchive(batch_n=50)
    # Incumbent with 150 pooled rollouts at drama 0.10.
    inc = batch(0.10)
    arch.offer(StubGame(tag="inc"), "inc", inc, no_evals)
    elite = next(iter(arch.cells.values()))
    elite.batches.append(batch(0.10))
    elite.batches.append(batch(0.10))
    assert elite.pooled_n == 150

    topups = []

    def eval_fn(game, batch_index, batch_n):
        topups.append(batch_index)
        return batch(0.20, n=batch_n)

    out = arch.offer(StubGame(tag="ch"), "ch", batch(0.20), eval_fn)
    assert out == "replaced"
    # challenger had 50, incumbent 150 -> exactly two top-up batches,
    # with batch indices continuing the challenger's stream (1, 2)
    assert topups == [1, 2]
    assert arch.counters["topup_rollouts"] == 100
    winner = arch.cells[("connection", 2, 2)]
    assert winner.canon == "ch"
    assert winner.pooled_n == 150


def test_topup_can_demote_lucky_challenger():
    arch = QDArchive(batch_n=50)
    arch.offer(StubGame(tag="inc"), "inc", batch(0.20), no_evals)
    elite = next(iter(arch.cells.values()))
    elite.batches.append(batch(0.20))     # pooled_n=100 at 0.20

    def eval_fn(game, batch_index, batch_n):
        return batch(0.05, n=batch_n)     # truth comes out on top-up

    out = arch.offer(StubGame(tag="ch"), "ch", batch(0.25), eval_fn)
    assert out == "lost_after_matching"
    assert arch.cells[("connection", 2, 2)].canon == "inc"


def test_topup_failure_abandons_challenge():
    arch = QDArchive(batch_n=50)
    arch.offer(StubGame(tag="inc"), "inc", batch(0.10), no_evals)
    elite = next(iter(arch.cells.values()))
    elite.batches.append(batch(0.10))     # pooled_n=100

    out = arch.offer(StubGame(tag="ch"), "ch", batch(0.20),
                     lambda g, i, n: None)
    assert out == "lost_topup_error"
    assert arch.cells[("connection", 2, 2)].canon == "inc"
    assert arch.counters["topup_failed"] == 1


# ---------------------------------------------------------------------------
# Re-eval
# ---------------------------------------------------------------------------

def test_reeval_reprices_but_never_evicts():
    arch = QDArchive(batch_n=50)
    arch.offer(StubGame(tag="a"), "a", batch(0.30), no_evals)

    def eval_fn(game, batch_index, batch_n):
        assert batch_index == 1           # continues the elite's stream
        return batch(0.00, n=batch_n)     # phantom: fresh batch collapses

    records = arch.reeval_all(eval_fn)
    assert arch.coverage == 1             # never evicts
    elite = next(iter(arch.cells.values()))
    assert math.isclose(elite.pooled_drama, 0.15)   # re-priced pooled mean
    assert records[0]["pooled_before"] == pytest.approx(0.30)
    assert records[0]["fresh_batch"] == pytest.approx(0.00)
    assert records[0]["pooled_after"] == pytest.approx(0.15)
    assert arch.counters["reeval_rollouts"] == 50


def test_reeval_does_not_rebin():
    arch = QDArchive(batch_n=50)
    arch.offer(StubGame(tag="a"), "a", batch(0.30, interaction=0.13),
               no_evals)

    def eval_fn(game, batch_index, batch_n):
        # wildly different interaction would re-bin if cells weren't pinned
        return batch(0.30, n=batch_n, interaction=0.90)

    arch.reeval_all(eval_fn)
    assert list(arch.cells) == [("connection", 2, 2)]


def test_reeval_failure_skips_elite_without_repricing():
    arch = QDArchive(batch_n=50)
    arch.offer(StubGame(tag="a"), "a", batch(0.30), no_evals)
    records = arch.reeval_all(lambda g, i, n: None)
    elite = next(iter(arch.cells.values()))
    assert elite.pooled_drama == pytest.approx(0.30)
    assert elite.pooled_n == 50           # no batch appended
    assert records[0]["fresh_batch"] is None
    assert arch.counters["reeval_failed"] == 1


# ---------------------------------------------------------------------------
# Dedup + reporting + persistence
# ---------------------------------------------------------------------------

def test_seen_tracking():
    arch = QDArchive()
    assert not arch.is_seen("x")
    arch.mark_seen("x")
    assert arch.is_seen("x")


def test_top_elites_and_qd_score():
    arch = QDArchive()
    arch.offer(StubGame("territory"), "a", batch(0.10), no_evals)
    arch.offer(StubGame("connection"), "b", batch(0.30), no_evals)
    arch.offer(StubGame("threshold"), "c", batch(0.20), no_evals)
    tops = arch.top_elites(2)
    assert [e.canon for e in tops] == ["b", "c"]
    assert arch.qd_score == pytest.approx(0.60)


def test_identical_offer_sequences_give_identical_archives():
    """Determinism promise: same inputs -> identical archive state."""
    def feed(arch):
        arch.mark_seen("a")
        arch.offer(StubGame("territory", tag="t1"), "a", batch(0.10),
                   no_evals)
        arch.offer(StubGame("connection", tag="c1"), "b", batch(0.30),
                   no_evals)
        arch.offer(StubGame("connection", tag="c2"), "c",
                   batch(0.40), lambda g, i, n: batch(0.40, n=n))
        arch.reeval_all(lambda g, i, n: batch(0.20, n=n))
        return arch

    a = feed(QDArchive(batch_n=50))
    b = feed(QDArchive(batch_n=50))
    assert a.to_dict() == b.to_dict()


def test_eval_seed_is_pure_and_schedule_invariant():
    """Content-derived seeds: same (canon, batch_index) -> same seed,
    regardless of call order."""
    from experiments.rc2_archive.run_probe import eval_seed_for
    canon = "6b6a2ef593c2d2189d07e120c4c454e6d60812c33a412010c6dda805815766a6"
    forward = [eval_seed_for(canon, i) for i in range(5)]
    backward = [eval_seed_for(canon, i) for i in reversed(range(5))]
    assert forward == backward[::-1]
    assert eval_seed_for(canon, 0) == (int(canon[:16], 16)) % 2 ** 31
    assert eval_seed_for(canon, 3) == (int(canon[:16], 16) + 7919 * 3) % 2 ** 31
    assert all(0 <= s < 2 ** 31 for s in forward)


def test_roundtrip_persistence():
    arch = QDArchive(batch_n=50)
    arch.mark_seen("a")
    arch.offer(StubGame("territory", tag="t1"), "a", batch(0.10), no_evals)
    d = arch.to_dict()
    back = QDArchive.from_dict(d, StubGame.from_dict)
    assert back.coverage == 1
    assert back.is_seen("a")
    elite = next(iter(back.cells.values()))
    assert elite.pooled_drama == pytest.approx(0.10)
    assert elite.pooled_n == 50
    assert back.counters["filled_empty_cell"] == 1
    assert back.to_dict() == d


# ---------------------------------------------------------------------------
# Verdict grammar (synthetic, every branch — Phase B pattern)
# ---------------------------------------------------------------------------

from experiments.rc2_archive.run_probe import decide_verdict  # noqa: E402


def _w(live=2, sampled=4):
    """Family spread summary: `live` LIVE families out of `sampled`."""
    fams = {}
    for i in range(sampled):
        spread = 0.10 if i < live else 0.01
        fams[f"fam{i}"] = {"n_valid": 20, "p90_p10": spread,
                           "live": spread >= 0.064}
    return fams


def test_verdict_probe_invalid_on_cal_fail():
    v = decide_verdict(cal_gap=0.10, family_spreads=_w(),
                       top10_m=0.2, top10_r=0.1,
                       m_elites=20, r_elites=20, incomplete=None)
    assert v == "PROBE_INVALID"


def test_verdict_archive_kill_on_bar_w_fail():
    v = decide_verdict(cal_gap=0.25, family_spreads=_w(live=1),
                       top10_m=0.2, top10_r=0.1,
                       m_elites=20, r_elites=20, incomplete=None)
    assert v == "ARCHIVE_KILL"


def test_verdict_archive_go():
    v = decide_verdict(cal_gap=0.25, family_spreads=_w(live=2),
                       top10_m=0.16, top10_r=0.12,
                       m_elites=20, r_elites=20, incomplete=None)
    assert v == "ARCHIVE_GO"


def test_verdict_archive_neutral_on_bar_h_fail():
    # uplift below the 0.03 floor
    v = decide_verdict(cal_gap=0.25, family_spreads=_w(live=2),
                       top10_m=0.13, top10_r=0.12,
                       m_elites=20, r_elites=20, incomplete=None)
    assert v == "ARCHIVE_NEUTRAL"


def test_verdict_bar_h_floor_is_strict():
    # exactly 0.03 passes (>= floor)
    v = decide_verdict(cal_gap=0.25, family_spreads=_w(live=2),
                       top10_m=0.15, top10_r=0.12,
                       m_elites=20, r_elites=20, incomplete=None)
    assert v == "ARCHIVE_GO"


def test_verdict_incomplete_flag_dominates():
    v = decide_verdict(cal_gap=0.25, family_spreads=_w(),
                       top10_m=0.2, top10_r=0.1,
                       m_elites=20, r_elites=20, incomplete="wall_cap")
    assert v == "PROBE_INCOMPLETE"


def test_verdict_incomplete_on_thin_archives():
    v = decide_verdict(cal_gap=0.25, family_spreads=_w(),
                       top10_m=0.2, top10_r=0.1,
                       m_elites=9, r_elites=20, incomplete=None)
    assert v == "PROBE_INCOMPLETE"


def test_verdict_incomplete_on_too_few_sampled_families():
    v = decide_verdict(cal_gap=0.25, family_spreads=_w(live=1, sampled=1),
                       top10_m=0.2, top10_r=0.1,
                       m_elites=20, r_elites=20, incomplete=None)
    assert v == "PROBE_INCOMPLETE"


def test_verdict_cal_checked_before_bar_w():
    # CAL fail + BAR W fail -> PROBE_INVALID (CAL is the instrument gate)
    v = decide_verdict(cal_gap=0.0, family_spreads=_w(live=0),
                       top10_m=0.0, top10_r=0.0,
                       m_elites=20, r_elites=20, incomplete=None)
    assert v == "PROBE_INVALID"
