"""Task 7 tests — campaign runner (`run_campaign.py`).

Two layers:
  1. Pure-helper unit tests (no engine): constants-as-data transcription
     guards, T1 validity guard, family grouping, salvage/checkpoint
     selection, pre-slate token mapping, heritability.
  2. The end-to-end --smoke run: tiny budgets baked into the SMOKE_*
     module constants (monkeypatch-able), seed bases INSIDE the registered
     smoke range (seeds.RECORDED_STREAMS["smoke"] = 999_000_000+), writes
     smoke/campaign_results.md, emits NO verdict token, archives get >= 1
     elite.
"""
import json
import math
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from experiments.rc2_campaign import run_campaign as rc
from experiments.rc2_campaign import seeds


# ---------------------------------------------------------------------------
# Constants transcription (prereg drift guard — constants are data)
# ---------------------------------------------------------------------------

def test_registered_constants_transcription():
    assert rc.B_ARM == 600
    # §3 as amended pre-data by BUILD_LOG erratum #13 (was 150/300/450/600):
    # CAL-C measured full-conv as 52% of projected wall; cadence 4->2 clears
    # the 8h cap (6.88h pessimistic) without touching search dynamics.
    assert rc.REEVAL_STEP == 300
    assert rc.REEVAL_AT == (300, 600)
    assert rc.BAR_W_MIN_VALID == 20
    assert rc.STAGE0_MIN_TOTAL_VALID == 150
    assert rc.STAGE0_MAX_EVALS == 240
    assert rc.STAGE0_MAX_ATTEMPTS == 3000
    assert rc.REDRAW_CAP == 50
    assert rc.N_STAGE0 == 100 and rc.N_STAGE1 == 50
    assert rc.EVAL_TIMEOUT_S == 180
    assert rc.WALL_CAP_S == 8 * 3600           # §6/§9 search-phase cap
    assert rc.WORKERS == 7                     # BUILD_LOG #9
    assert rc.T1_MIN_NONDRAW_SHARE == 0.5      # §4 step 3 [C13]
    assert rc.T1_MIN_MEAN_LENGTH == 6.0
    assert rc.FULL_CONV_BATCH_BASE == 1000     # never collides with T1's 0


def test_campaign_derives_registered_instrument(tmp_path):
    c = rc.Campaign(tmp_path, smoke=False)
    assert c.reeval_at == rc.REEVAL_AT
    assert (c.t1_n, c.t1_deep, c.t1_shallow) == (24, 128, 16)
    assert (c.full_n, c.full_deep, c.full_shallow) == (48, 256, 16)
    assert c.guard_pairs == 12
    assert c.gen_seed_base == seeds.GEN_SEED_BASE
    assert c.arm_r_seed_base == seeds.ARM_R_SEED_BASE
    assert c.b_arm == 600 and c.workers == 7


def test_b_arm_override_must_keep_registered_reeval_cadence(tmp_path):
    # --b-arm (re-registered scopes only) must stay a positive multiple of
    # REEVAL_STEP or the reeval_at derivation drops the terminal checkpoint.
    with pytest.raises(SystemExit, match="cadence"):
        rc.Campaign(tmp_path, smoke=False, b_arm=500)
    # 450 was a legal multiple at the superseded step of 150; under
    # erratum #13's step of 300 it must now be rejected too.
    with pytest.raises(SystemExit, match="cadence"):
        rc.Campaign(tmp_path, smoke=False, b_arm=450)
    c = rc.Campaign(tmp_path, smoke=False, b_arm=600)
    assert c.reeval_at == (300, 600)
    c2 = rc.Campaign(tmp_path, smoke=False, b_arm=300)
    assert c2.reeval_at == (300,)
    # smoke keeps its own tiny cadence, untouched by the guard
    s = rc.Campaign(tmp_path, smoke=True, b_arm=500)
    assert s.b_arm == rc.SMOKE_B_ARM and s.reeval_at == rc.SMOKE_REEVAL_AT


def test_smoke_seed_bases_inside_registered_smoke_range(tmp_path):
    lo, hi = seeds.RECORDED_STREAMS["smoke"]
    for base in (rc.SMOKE_GEN_SEED_BASE, rc.SMOKE_ARM_R_SEED_BASE,
                 rc.SMOKE_ARM_M_MUT_SEED, rc.SMOKE_ARM_M_SEL_SEED,
                 rc.SMOKE_BOOT_SEED):
        assert lo <= base < hi
    # attempt offsets stay inside the recorded range too
    assert rc.SMOKE_GEN_SEED_BASE + rc.SMOKE_STAGE0_MAX_ATTEMPTS < hi
    assert rc.SMOKE_ARM_R_SEED_BASE + 10_000 < hi
    c = rc.Campaign(tmp_path, smoke=True)
    assert c.b_arm == rc.SMOKE_B_ARM
    assert c.reeval_at == rc.SMOKE_REEVAL_AT
    assert c.workers == rc.SMOKE_WORKERS


# ---------------------------------------------------------------------------
# T1 validity guard (§4 step 3, BUILD_LOG #2)
# ---------------------------------------------------------------------------

def _t1(raw=0.2, non_draw=0.8, length=30.0):
    return {"raw_pg": raw, "floored_pg": max(raw, 0.0), "draws": 2, "n": 24,
            "non_draw_share": non_draw, "mean_length": length}


def test_t1_validity_passes_good_batch():
    assert rc.t1_validity(_t1()) is None


def test_t1_validity_draw_majority():
    assert rc.t1_validity(_t1(non_draw=0.49)) == "draw_majority"


def test_t1_validity_too_short():
    assert rc.t1_validity(_t1(length=5.9)) == "too_short"


def test_t1_validity_nan_pg():
    assert rc.t1_validity(_t1(raw=float("nan"))) == "pg_nan"


# ---------------------------------------------------------------------------
# Family grouping for BAR W (floored T1-PG of Stage-0 VALID genomes)
# ---------------------------------------------------------------------------

def test_family_floored_pgs_groups_and_floors():
    recs = [
        {"valid": True, "family": "connection", "t1": _t1(raw=0.3)},
        {"valid": True, "family": "connection", "t1": _t1(raw=-0.2)},
        {"valid": True, "family": "territory", "t1": _t1(raw=0.1)},
        {"valid": False, "family": "territory", "t1": _t1(raw=0.9)},   # excluded
        {"valid": False, "family": "threshold", "t1": None},           # eval_failed
    ]
    out = rc.family_floored_pgs(recs)
    assert out == {"connection": [0.3, 0.0], "territory": [0.1]}


def test_family_table_agrees_with_bar_w():
    from experiments.rc2_campaign.bars import bar_w
    fpgs = {"connection": [0.0, 0.05, 0.3, 0.4], "territory": [0.1, 0.1],
            "threshold": [0.2]}
    table = rc.family_table(fpgs, min_valid=2)
    res = bar_w(fpgs, min_valid=2)
    for fam, row in table.items():
        assert row["qualifying"] == (fam in res["qualifying"])
        if row["qualifying"]:
            assert row["live"] == res["live"][fam]
    assert table["elimination"]["n_valid"] == 0
    assert not table["elimination"]["qualifying"]


# ---------------------------------------------------------------------------
# Salvage / bar-checkpoint selection (§9 rule 2)
# ---------------------------------------------------------------------------

REEVAL = (300, 600)  # §3 registered cadence as amended by erratum #13


def test_select_final_when_both_complete_and_no_wall():
    assert rc.select_bar_checkpoint([300, 600], [300, 600],
                                    REEVAL, wall_hit=False) == ("final", 600)


def test_select_salvage_at_last_mutual_when_wall_after_penultimate():
    # R finished all checkpoints; M reached the penultimate (300 at the
    # registered cadence, erratum #13) then the cap hit
    assert rc.select_bar_checkpoint([300, 600], [300],
                                    REEVAL, wall_hit=True) == ("salvage", 300)


def test_select_salvage_at_600_when_wall_trips_after_completion():
    assert rc.select_bar_checkpoint([300, 600], [300, 600],
                                    REEVAL, wall_hit=True) == ("salvage", 600)


def test_select_incomplete_when_no_mutual_checkpoint():
    assert rc.select_bar_checkpoint([300, 600], [],
                                    REEVAL, wall_hit=True) == ("incomplete", "wall_cap")


def test_select_incomplete_under_budget_without_wall():
    assert rc.select_bar_checkpoint([300], [],
                                    REEVAL, wall_hit=False) == \
        ("incomplete", "arms_under_budget")


def test_select_penultimate_rule_is_cadence_generic():
    # The salvage floor is reeval_at[-2] whatever the cadence — pinned on a
    # 4-point tuple so the rule survives any future re-registration.
    generic = (150, 300, 450, 600)
    assert rc.select_bar_checkpoint([150, 300, 450, 600], [150, 300, 450],
                                    generic, wall_hit=True) == ("salvage", 450)
    assert rc.select_bar_checkpoint([150, 300, 450, 600], [150, 300],
                                    generic, wall_hit=True) == \
        ("incomplete", "wall_cap")


# ---------------------------------------------------------------------------
# Pre-slate token (§9 chain via bars.decide_verdict; SLATE_PENDING is NOT
# a §9 token — the slate stage runs later, manually)
# ---------------------------------------------------------------------------

def test_pre_slate_token_cal_fail():
    assert rc.pre_slate_token(cal_i_pass=False, incomplete=None,
                              bar_w_verdict="PASS", bar_h_verdict="PASS") \
        == "PROBE_INVALID"


def test_pre_slate_token_incomplete():
    assert rc.pre_slate_token(cal_i_pass=True, incomplete="wall_cap",
                              bar_w_verdict="PASS", bar_h_verdict="PASS") \
        == "PROBE_INCOMPLETE"


def test_pre_slate_token_archive_kill():
    assert rc.pre_slate_token(cal_i_pass=True, incomplete=None,
                              bar_w_verdict="ARCHIVE_KILL",
                              bar_h_verdict="PROBE_INCOMPLETE") \
        == "ARCHIVE_KILL"


def test_pre_slate_token_search_neutral():
    assert rc.pre_slate_token(cal_i_pass=True, incomplete=None,
                              bar_w_verdict="PASS",
                              bar_h_verdict="SEARCH_NEUTRAL") \
        == "SEARCH_NEUTRAL"


def test_pre_slate_token_slate_pending_when_bars_pass():
    assert rc.pre_slate_token(cal_i_pass=True, incomplete=None,
                              bar_w_verdict="PASS", bar_h_verdict="PASS") \
        == "SLATE_PENDING"


# ---------------------------------------------------------------------------
# Heritability (§6 registered next-step inputs [C14]; reported only)
# ---------------------------------------------------------------------------

def test_heritability_restricts_to_positive_floored_parents():
    log = [
        {"parent_t1_raw": 0.1, "child_t1_raw": 0.11},
        {"parent_t1_raw": 0.2, "child_t1_raw": 0.19},
        {"parent_t1_raw": 0.3, "child_t1_raw": 0.32},
        {"parent_t1_raw": -0.2, "child_t1_raw": 0.9},    # floored parent 0 -> excluded
        {"parent_t1_raw": 0.4, "child_t1_raw": None},    # failed child -> excluded
        {"child_t1_raw": 0.5},                           # arm-R style entry -> excluded
    ]
    h = rc.heritability(log)
    assert h["n_pairs"] == 3
    assert h["raw_r"] == pytest.approx(1.0, abs=0.05)
    assert h["floored_r"] is not None


def test_heritability_too_few_pairs():
    h = rc.heritability([{"parent_t1_raw": 0.3, "child_t1_raw": 0.2}])
    assert h == {"raw_r": None, "floored_r": None, "n_pairs": 1}


# ---------------------------------------------------------------------------
# End-to-end smoke run (registered smoke semantics: disjoint seed range,
# early-exit gates ignored, NO verdict token, tiny budgets)
# ---------------------------------------------------------------------------

def test_smoke_end_to_end():
    smoke_dir = rc.HERE / "smoke"
    if smoke_dir.exists():
        shutil.rmtree(smoke_dir)

    rc.main(["--smoke"])

    md = (smoke_dir / "campaign_results.md").read_text()
    assert "SMOKE RUN" in md
    assert "would-be pre-slate token" in md
    assert "```" not in md          # never a registered/fenced verdict token

    ck = json.loads((smoke_dir / "checkpoint.json").read_text())
    assert ck["stage"] == "terminal"
    assert ck["smoke"] is True
    # both archives initialize from the same Stage-0 valid set -> >= 1 elite
    for arm in ("R", "M"):
        assert len(ck["archives"][arm]["cells"]) >= 1, f"arm {arm} has no elite"
        # arm ran its full smoke budget
        assert ck["arm_state"][arm]["evals"] == rc.SMOKE_B_ARM

    assert (smoke_dir / "campaign_results.csv").exists()
    assert (smoke_dir / "arm_R_log.csv").exists()
    assert (smoke_dir / "arm_M_log.csv").exists()


def test_checkpoint_resume_round_trip(tmp_path):
    # Real save_checkpoint/load_checkpoint round-trip on the smoke config:
    # run Stage 0 + archive init (real engine evals, smoke budgets), save,
    # load into a FRESH Campaign, assert stage + stage0 records + archive
    # contents + rng state survive.
    p = rc.Campaign(tmp_path, smoke=True)
    try:
        p.run_stage0()
        p.init_archives()
        # advance the arm-M rngs so a non-fresh rng state is exercised
        p.sel_rng.integers(0, 100, size=3)
        p.mut_rng.integers(0, 100, size=3)
        rc.save_checkpoint(p, "arms_init")
    finally:
        p.shutdown()

    q = rc.Campaign(tmp_path, smoke=True)
    try:
        stage = rc.load_checkpoint(q)
    finally:
        q.shutdown()

    assert stage == "arms_init"
    assert q.stage0_progress == p.stage0_progress
    assert dict(q.eval_counters) == dict(p.eval_counters)
    assert [r["canon"] for r in q.stage0_records] \
        == [r["canon"] for r in p.stage0_records]
    assert [r["valid"] for r in q.stage0_records] \
        == [r["valid"] for r in p.stage0_records]
    assert set(q.archives) == {"R", "M"}
    for arm in ("R", "M"):
        assert q.archives[arm].to_dict() == p.archives[arm].to_dict()
    assert q.init_counters == p.init_counters
    assert q.sel_rng.bit_generator.state == p.sel_rng.bit_generator.state
    assert q.mut_rng.bit_generator.state == p.mut_rng.bit_generator.state
