"""Pins for the BAR H v2 re-registration (PREREGISTRATION_BARH_V2.md,
ratified 2026-07-05; BUILD_LOG #15). Two kinds of pin:

1. Semantics pins (data-free): contested-cell construction in
   bar_h_inputs — same-canon cells excluded from numerator AND
   denominator; distinct-genome equal-value cells stay as non-wins.
2. Reanalysis pins (against the committed terminal checkpoint): the §0
   disclosure table of the spec, transcribed as assertions — joint 15,
   same-canon 5, contested 10 (7 M / 2 R / 1 equal-value), frac 0.700,
   bar_h PASS, pre-slate token SLATE_PENDING. If the checkpoint and
   these pins ever disagree, the spec's disclosed basis is wrong and
   the reanalysis must NOT run.
"""
import json
import pathlib
import statistics

import pytest

from experiments.rc2_campaign import bars as B
from experiments.rc2_campaign.campaign_archive import CampaignArchive
from experiments.rc2_campaign.run_campaign import bar_h_inputs, pre_slate_token
from game_engine.game_def_v2 import GameDefV2

HERE = pathlib.Path(__file__).resolve().parent
CHECKPOINT = HERE / "checkpoint.json"


class _Elite:
    def __init__(self, canon, fc):
        self.canon = canon
        self.full_conv = fc
        self.full_conv_mean_floored = (
            max(statistics.mean(fc), 0.0) if fc else float("nan"))


class _Arch:
    def __init__(self, cells):
        self.cells = cells

    def top_elites_by_full_conv(self, k):
        return sorted(self.cells.values(),
                      key=lambda e: e.full_conv_mean_floored,
                      reverse=True)[:k]


def _arch(spec):
    return _Arch({cell: _Elite(canon, fc) for cell, (canon, fc) in spec.items()})


def test_bar_h_inputs_contested_semantics_v2():
    r = _arch({
        "a": ("X", [0.40]),   # same-canon -> excluded entirely (v2 §2)
        "b": ("r1", [0.30]),  # M strictly better -> contested win
        "c": ("r2", [0.50]),  # distinct genomes, equal value -> contested non-win
        "d": ("r3", [0.45]),  # R strictly better -> contested non-win
        "e": ("r4", [0.20]),  # R-only cell -> not joint
        "g": ("r5", []),      # joint but R unrated -> excluded (v2 §6.5)
    })
    m = _arch({
        "a": ("X", [0.40]),
        "b": ("m1", [0.35]),
        "c": ("m2", [0.50]),
        "d": ("m3", [0.40]),
        "f": ("m4", [0.10]),  # M-only cell -> not joint
        "g": ("m5", [0.45]),
    })
    out = bar_h_inputs(r, m, top_k=1)
    assert out["joint_n"] == 5
    assert out["same_elite_ties"] == 1
    assert out["unrated_joint"] == 1
    assert out["contested_n"] == 3
    assert out["contested_wins"] == [True, False, False]
    assert "joint_wins" not in out  # v1 field retired; no silent dual-report


@pytest.mark.skipif(not CHECKPOINT.exists(), reason="terminal checkpoint absent")
def test_reanalysis_pins_match_spec_disclosure():
    ck = json.loads(CHECKPOINT.read_text())
    assert ck["stage"] == "terminal", "reanalysis pins only bind the terminal checkpoint"
    arch_r = CampaignArchive.from_dict(ck["archives"]["R"], GameDefV2.from_dict)
    arch_m = CampaignArchive.from_dict(ck["archives"]["M"], GameDefV2.from_dict)
    inputs = bar_h_inputs(arch_r, arch_m)

    # §0 disclosure table, transcribed
    assert inputs["joint_n"] == 15
    assert inputs["same_elite_ties"] == 5
    assert inputs["unrated_joint"] == 0
    assert inputs["contested_n"] == 10
    assert sum(inputs["contested_wins"]) == 7
    assert inputs["r_rated"] == 17 and inputs["m_rated"] == 26
    assert inputs["top10_r"] == pytest.approx(0.4823, abs=5e-4)
    assert inputs["top10_m"] == pytest.approx(0.4974, abs=5e-4)
    assert inputs["top10_r"] >= B.SATURATION_R_TOP10  # switch fires

    res = B.bar_h(inputs["top10_m"], inputs["top10_r"],
                  inputs["m_rated"], inputs["r_rated"],
                  contested_cells=inputs["contested_wins"])
    assert res["metric"] == "per_cell_wins"
    assert res["verdict"] == "PASS"  # 7/10 = 0.700 >= 0.60

    # chain inputs pinned to the RECORDED artifacts, not assumptions
    # (review finding: the pin must disagree loudly if the artifacts do)
    cal_i = json.loads((HERE / "cal_i.json").read_text())
    assert cal_i["verdict"] == "PASS"
    assert ck["incomplete"] is None          # wall 19.0h < 36h cap
    token = pre_slate_token(
        cal_i_pass=cal_i["verdict"] == "PASS",
        incomplete=ck["incomplete"],
        bar_w_verdict=ck["bar_w_result"]["verdict"],   # PASS, Stage-0 close
        bar_h_verdict=res["verdict"],
    )
    assert token == "SLATE_PENDING"


def test_v1_counterfactual_and_phase_c_consistency():
    # spec §0: v1 tie-in-denominator on the known data fails theta even at n>=20
    assert 7 / 15 < B.SATURATION_M_WIN_FRAC
    # spec §2: contested-only on the known data passes
    assert 7 / 10 >= B.SATURATION_M_WIN_FRAC
    # spec §3: v2 applied to Phase C R2 (20W/6L distinct-genome) still passes
    assert 20 / 26 >= B.SATURATION_M_WIN_FRAC
