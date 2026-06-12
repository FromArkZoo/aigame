"""Fast tests for experiments/frontline/calibrate.py — NO training.

Covers the pure prereg gate logic:
  (a) gate-order structure: a skill-failing cell never computes/reads bias
      (apply_gates short-circuits at the first failing gate; truncated
      stats dicts must never raise);
  (b) komi direction logic (P1-favored -> +1 first; P2-favored -> -1);
  (c) tie-break ordering on synthetic passing cells;
  (d) the bias formula (draws count half);
  (e) the reserve/rerun machinery (resolve_skill_gate with train_one and
      trained_vs_random monkeypatched — no training): replace-in-slot
      rerun, reserves 45 then 46 consumed in order ACROSS the grid, third
      collapse -> INVALID, at most one rerun per original seed.

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


# ---------------------------------------------------------------------------
# (e) Reserve/rerun machinery — resolve_skill_gate with training mocked out
# ---------------------------------------------------------------------------

import experiments.frontline.calibrate as cal  # noqa: E402
from experiments.frontline.calibrate import (  # noqa: E402
    ALL_CELLS,
    COLLAPSE_TVR,
    RESERVE_SEEDS,
    calibrate_cell,
    resolve_skill_gate,
)


class _FakeTrainer:
    """Dummy trainer object: train_one is monkeypatched to return these;
    trained_vs_random is monkeypatched to look the canned tvr up by seed."""

    def __init__(self, seed: int):
        self.seed = seed


def _patch_training(monkeypatch, tvr_by_seed: dict[int, float]):
    monkeypatch.setattr(
        cal, "train_one", lambda game, budget, seed: _FakeTrainer(seed))
    monkeypatch.setattr(
        cal, "trained_vs_random",
        lambda trainer, n=100: tvr_by_seed[trainer.seed])
    return tvr_by_seed


def _fresh_reserves():
    return {"available": list(RESERVE_SEEDS), "used": []}


def test_collapse_triggers_replace_in_slot_rerun_with_45(monkeypatch):
    # Registered behavior 1: a collapsed seed (tvr < 0.20) gets ONE rerun
    # with reserve 45, and the rerun REPLACES the collapsed seed IN SLOT
    # (aggregates run over the 3 final seeds).
    _patch_training(monkeypatch,
                    {42: 0.85, 43: 0.10, 44: 0.88, 45: 0.90})
    used = _fresh_reserves()
    trainers, tvrs, records, invalid = resolve_skill_gate(
        None, [42, 43, 44], 0, used, 10, "cellA")
    assert invalid is None
    assert [t.seed for t in trainers] == [42, 45, 44]  # replace IN SLOT
    assert tvrs == [0.85, 0.90, 0.88]                  # rerun tvr in slot 2
    assert records[1] == dict(orig_seed=43, final_seed=45, tvr=0.90,
                              rerun=True, orig_tvr=0.10)
    assert records[0]["rerun"] is False and records[2]["rerun"] is False
    assert used["available"] == [46]
    assert used["used"] == [dict(cell="cellA", orig_seed=43, reserve=45)]


def test_second_collapse_consumes_46_in_order_across_grid(monkeypatch):
    # Registered behavior 2: reserves are consumed in order (45 then 46)
    # ACROSS the grid — the shared used_reserves dict carries over cells.
    used = _fresh_reserves()
    _patch_training(monkeypatch,
                    {42: 0.85, 43: 0.10, 44: 0.88, 45: 0.90})
    resolve_skill_gate(None, [42, 43, 44], 0, used, 10, "cellA")
    assert used["available"] == [46]

    # Second cell: a different original seed collapses -> consumes 46.
    _patch_training(monkeypatch,
                    {42: 0.05, 43: 0.90, 44: 0.88, 46: 0.82})
    trainers, tvrs, records, invalid = resolve_skill_gate(
        None, [42, 43, 44], 0, used, 10, "cellB")
    assert invalid is None
    assert [t.seed for t in trainers] == [46, 43, 44]
    assert tvrs == [0.82, 0.90, 0.88]
    assert used["available"] == []
    assert used["used"] == [
        dict(cell="cellA", orig_seed=43, reserve=45),
        dict(cell="cellB", orig_seed=42, reserve=46),
    ]


def test_third_collapse_with_reserves_exhausted_is_invalid(monkeypatch):
    # Registered behavior 3: a third collapse across the grid (reserves
    # exhausted) -> cell INVALID; trainers is None (bias unreachable).
    _patch_training(monkeypatch, {42: 0.90, 43: 0.85, 44: 0.10})
    used = {"available": [], "used": [
        dict(cell="cellA", orig_seed=43, reserve=45),
        dict(cell="cellB", orig_seed=42, reserve=46),
    ]}
    trainers, tvrs, records, invalid = resolve_skill_gate(
        None, [42, 43, 44], 0, used, 10, "cellC")
    assert trainers is None
    assert "exhausted" in invalid and "44" in invalid
    # Earlier healthy seeds' tvrs are retained for the report.
    assert tvrs == [0.90, 0.85]
    assert records[-1] == dict(orig_seed=44, final_seed=44, tvr=0.10,
                               rerun=False)
    # INVALID via apply_gates (the gate-1 decision path).
    verdict, reason = apply_gates(dict(invalid=invalid, tvrs=tvrs))
    assert verdict == "INVALID" and "exhausted" in reason


def test_callsite_reserve_wiring_across_grid_via_calibrate_cell(monkeypatch):
    # Across-grid reserve ordering at the CALL-SITE level: main() builds ONE
    # shared used_reserves dict from state["reserves_used"] and passes it to
    # calibrate_cell for every cell in the grid loop (calibrate.py main(),
    # the block under "Reserves are consumed in order ACROSS THE GRID").
    # Mirror that wiring EXACTLY through calibrate_cell (not just
    # resolve_skill_gate): each cell's seed 43 collapses; cell A must consume
    # reserve 45, cell B reserve 46, and both consumptions must land in
    # state["reserves_used"] (the same list object main persists to
    # calibration.json). Canned tvrs keep the post-rerun skill gate FAILING
    # (mean 0.70 < 0.75 floor), so calibrate_cell early-returns at gate 1 —
    # no training, no eval compute, as in every test in this file.
    _patch_training(monkeypatch,
                    {42: 0.70, 43: 0.10, 44: 0.70, 45: 0.70, 46: 0.70})
    state = {"cells": {}, "reserves_used": []}
    # --- main()'s wiring, verbatim ---
    consumed = {u["reserve"] for u in state["reserves_used"]}
    used_reserves = {
        "available": [s for s in RESERVE_SEEDS if s not in consumed],
        "used": state["reserves_used"],
    }
    cells = ("E1p00_M8", "E1p00_M12")
    for name in cells:
        e, m = ALL_CELLS[name]
        state["cells"][name] = calibrate_cell(
            name, e, m, [42, 43, 44], 10, 20, 10, used_reserves)
    # --- end main() wiring ---

    # Across-grid ordering: 45 consumed by cell A, then 46 by cell B —
    # recorded through the SHARED list, never a per-cell copy.
    assert used_reserves["used"] is state["reserves_used"]
    assert used_reserves["available"] == []
    assert state["reserves_used"] == [
        dict(cell="E1p00_M8", orig_seed=43, reserve=45),
        dict(cell="E1p00_M12", orig_seed=43, reserve=46),
    ]
    # Each cell's record shows ITS OWN reserve replacing seed 43 in slot,
    # and the rerun tvr reached the gates via calibrate_cell.
    for name, reserve in zip(cells, (45, 46)):
        res = state["cells"][name]
        assert res["records"][1] == dict(orig_seed=43, final_seed=reserve,
                                         tvr=0.70, rerun=True, orig_tvr=0.10)
        assert res["tvrs"] == [0.70, 0.70, 0.70]
        assert res["verdict"] == "FAIL"
        assert res["reason"].startswith("skill")


def test_rerun_collapsing_again_is_invalid_one_rerun_per_seed(monkeypatch):
    # Registered behavior 4: at most ONE rerun per original seed — a rerun
    # that collapses again -> cell INVALID immediately; the NEXT reserve
    # (46) is NOT consumed for the same original seed.
    _patch_training(monkeypatch, {42: 0.10, 45: 0.15})
    used = _fresh_reserves()
    trainers, tvrs, records, invalid = resolve_skill_gate(
        None, [42, 43, 44], 0, used, 10, "cellA")
    assert trainers is None
    assert "still collapsed" in invalid
    assert used["available"] == [46]  # 46 untouched: one rerun per seed
    assert used["used"] == [dict(cell="cellA", orig_seed=42, reserve=45)]
    assert records[-1] == dict(orig_seed=42, final_seed=45, tvr=0.15,
                               rerun=True, orig_tvr=0.10)
    # Sanity: both observed tvrs really are collapses.
    assert records[-1]["orig_tvr"] < COLLAPSE_TVR
    assert records[-1]["tvr"] < COLLAPSE_TVR
