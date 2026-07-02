"""Task 9 tests — CAL-C pre-campaign cost projection (`cal_c.py`).

Pure-only (no engine): projection arithmetic, mode routing, attempt-cap
reporting (via a stub generator satisfying only the generate_game/
quick_reject interface — no GameGeneratorV2/engine involved), and the
seed-offset disjointness claim (CAL_SEED_BASE's draw range vs Stage-0's
attempt range and the smoke range).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from experiments.rc2_campaign import cal_c as CC
from experiments.rc2_campaign import seeds
from experiments.rc2_campaign.run_campaign import (
    B_ARM,
    REEVAL_AT,
    STAGE0_MAX_ATTEMPTS,
    STAGE0_MAX_EVALS,
    WORKERS,
)


# ---------------------------------------------------------------------------
# Projection arithmetic (pure)
# ---------------------------------------------------------------------------

def _stage_stats(descriptor=1.0, t1=1.0, guard=1.0, full_conv=1.0, sd=0.0,
                 n=20):
    def st(mean):
        return dict(mean=mean, sd=sd, n=n)
    return {"descriptor_s": st(descriptor), "t1_s": st(t1),
           "guard_s": st(guard), "full_conv_s": st(full_conv),
           "total_s": st(descriptor + t1 + guard + full_conv)}


def test_project_campaign_hours_arithmetic_optimistic():
    stats = _stage_stats(descriptor=2.0, t1=3.0, guard=4.0, full_conv=5.0)
    proj = CC.project_campaign_hours(
        stats, spread=0.0, descriptor_n50_scale=0.5,
        stage0_evals=10, stage0_offer_rate=0.5, arm_evals_total=20,
        n_checkpoints=2, archive_size_estimate=5, n_arms=2, offer_rate=0.5,
        workers=1)
    stage0 = 10 * (2.0 + 3.0 + 0.5 * 4.0)   # descriptor_n100 + T1 + stage0_offer_rate*guard
    arms = 20 * (1.0 + 3.0 + 0.5 * 4.0)     # descriptor_n50(1.0) + T1 + offer_rate*guard
    fullconv = 2 * 2 * 5 * 5.0              # checkpoints * arms * archive * full_conv
    total = stage0 + arms + fullconv
    assert proj["descriptor_n100_s"] == pytest.approx(2.0)
    assert proj["descriptor_n50_s"] == pytest.approx(1.0)
    assert proj["stage0_work_s"] == pytest.approx(stage0)
    assert proj["arms_work_s"] == pytest.approx(arms)
    assert proj["fullconv_work_s"] == pytest.approx(fullconv)
    assert proj["total_work_s"] == pytest.approx(total)
    assert proj["wall_s"] == pytest.approx(total / 1)
    assert proj["wall_hours"] == pytest.approx(total / 3600)


def test_project_campaign_hours_pessimistic_adds_one_sd_per_stage():
    stats = _stage_stats(descriptor=2.0, t1=3.0, guard=4.0, full_conv=5.0,
                         sd=1.0)
    kw = dict(workers=1, stage0_evals=1, stage0_offer_rate=1.0,
             arm_evals_total=1, n_checkpoints=1, archive_size_estimate=1,
             n_arms=1, offer_rate=1.0)
    opt = CC.project_campaign_hours(stats, spread=0.0, **kw)
    pess = CC.project_campaign_hours(stats, spread=1.0, **kw)
    assert pess["wall_hours"] > opt["wall_hours"]
    assert pess["descriptor_n100_s"] == pytest.approx(3.0)   # mean+sd
    assert pess["t1_s"] == pytest.approx(4.0)
    assert pess["guard_s"] == pytest.approx(5.0)
    assert pess["full_conv_s"] == pytest.approx(6.0)


def test_project_campaign_hours_stage0_includes_guard_term():
    """Important-1 fix: stage0_work_s must include a stage0_offer_rate x
    guard term, mirroring the arms term's offer_rate x guard shape — not
    just descriptor_n100 + T1."""
    stats = _stage_stats(descriptor=2.0, t1=3.0, guard=4.0, full_conv=5.0)
    proj = CC.project_campaign_hours(
        stats, spread=0.0, descriptor_n50_scale=0.5,
        stage0_evals=10, stage0_offer_rate=0.8, arm_evals_total=20,
        n_checkpoints=2, archive_size_estimate=5, n_arms=2, offer_rate=0.5,
        workers=1)
    stage0_without_guard = 10 * (2.0 + 3.0)
    assert proj["stage0_work_s"] == pytest.approx(10 * (2.0 + 3.0 + 0.8 * 4.0))
    assert proj["stage0_work_s"] > stage0_without_guard


def test_project_campaign_hours_stage0_offer_rate_defaults_to_module_constant():
    stats = _stage_stats(descriptor=2.0, t1=3.0, guard=4.0, full_conv=5.0)
    proj = CC.project_campaign_hours(
        stats, spread=0.0, stage0_evals=10, arm_evals_total=20,
        n_checkpoints=2, archive_size_estimate=5, n_arms=2, workers=1)
    expected = 10 * (2.0 + 3.0 + CC.STAGE0_OFFER_RATE * 4.0)
    assert proj["stage0_work_s"] == pytest.approx(expected)


def test_build_verdict_within_cap():
    stats = _stage_stats(descriptor=0.001, t1=0.001, guard=0.001,
                         full_conv=0.001, sd=0.0)
    v = CC.build_verdict(stats, cap_hours=8.0)
    assert v["within_cap"] is True
    assert v["rescope_required"] is False
    assert v["cap_hours"] == 8.0
    assert v["projection_hours"]["optimistic"] <= v["projection_hours"]["pessimistic"]


def test_build_verdict_over_cap_flags_rescope():
    stats = _stage_stats(descriptor=1000.0, t1=1000.0, guard=1000.0,
                         full_conv=1000.0, sd=0.0)
    v = CC.build_verdict(stats, cap_hours=8.0)
    assert v["within_cap"] is False
    assert v["rescope_required"] is True


def test_build_verdict_gates_on_pessimistic_not_optimistic():
    """A projection that clears the cap optimistically but NOT pessimistically
    must still flag rescope — the verdict is conservative by design (mean +
    1 SD), never the optimistic mean alone."""
    stats = _stage_stats(descriptor=0.01, t1=0.01, guard=0.01, full_conv=0.01,
                         sd=100.0)
    v = CC.build_verdict(stats, cap_hours=8.0,
                         stage0_evals=STAGE0_MAX_EVALS,
                         arm_evals_total=2 * B_ARM,
                         n_checkpoints=len(REEVAL_AT),
                         archive_size_estimate=50, n_arms=2, offer_rate=0.3,
                         workers=WORKERS)
    assert v["projection_hours"]["optimistic"] < 8.0
    assert v["projection_hours"]["pessimistic"] > 8.0
    assert v["within_cap"] is False
    assert v["rescope_required"] is True


def test_summarise_stage_timings_pure():
    records = [
        dict(descriptor_s=1.0, t1_s=2.0, guard_s=3.0, full_conv_s=4.0,
            total_s=10.0),
        dict(descriptor_s=3.0, t1_s=4.0, guard_s=5.0, full_conv_s=6.0,
            total_s=18.0),
    ]
    out = CC.summarise_stage_timings(records)
    assert out["descriptor_s"]["mean"] == pytest.approx(2.0)
    assert out["descriptor_s"]["n"] == 2
    assert out["descriptor_s"]["sd"] == pytest.approx(1.4142135, abs=1e-5)


# ---------------------------------------------------------------------------
# Minor fix — DESCRIPTOR_N50_SCALE derived (not hardcoded)
# ---------------------------------------------------------------------------

def test_descriptor_n50_scale_derived_from_registered_constants():
    from experiments.rc2_campaign.run_campaign import N_STAGE0, N_STAGE1
    assert CC.DESCRIPTOR_N50_SCALE == pytest.approx(N_STAGE1 / N_STAGE0)
    assert CC.DESCRIPTOR_N50_SCALE == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# Important-2 fix — real-loop failure tolerance (pure)
# ---------------------------------------------------------------------------

def test_min_successes_required_floor_of_three():
    assert CC.min_successes_required(0) == 3
    assert CC.min_successes_required(3) == 3
    assert CC.min_successes_required(4) == 3
    assert CC.min_successes_required(6) == 3


def test_min_successes_required_half_of_requested_above_floor():
    assert CC.min_successes_required(10) == 5
    assert CC.min_successes_required(20) == 10


def test_has_sufficient_sample_insufficient_rule():
    assert CC.has_sufficient_sample(10, 20) is True
    assert CC.has_sufficient_sample(9, 20) is False
    assert CC.has_sufficient_sample(3, 4) is True
    assert CC.has_sufficient_sample(2, 4) is False


def test_build_state_includes_failures():
    records = [dict(canon="abc123def456ghi7", family="territory",
                    descriptor_s=1.0, t1_s=1.0, guard_s=1.0, full_conv_s=1.0,
                    total_s=4.0, t1_raw_pg=0.1, guard_passed=True,
                    full_conv_raw_pg=0.1)]
    draw_report = dict(seed_base=1, n_target=2, max_attempts=10, attempts=2,
                       accepted=2, attempt_cap_hit=False)
    failures = [dict(genome_index=1, canon="deadbeef00000000",
                     error="EvalTimeout()")]
    state = CC.build_state(records, draw_report, elapsed=1.0,
                           descriptor_n100=10, descriptor_n50_scale=0.5,
                           t1_deep=32, t1_shallow=8, t1_n=8,
                           guard_pairs=4, full_deep=64, full_shallow=8,
                           full_n=8, dry_run=True, from_cache=False,
                           failures=failures)
    assert state["failures"] == failures
    assert state["n_failures"] == 1


def test_build_state_defaults_failures_to_empty_list():
    draw_report = dict(seed_base=1, n_target=1, max_attempts=10, attempts=1,
                       accepted=1, attempt_cap_hit=False)
    state = CC.build_state([], draw_report, elapsed=1.0, descriptor_n100=10,
                           descriptor_n50_scale=0.5, t1_deep=32, t1_shallow=8,
                           t1_n=8, guard_pairs=4, full_deep=64,
                           full_shallow=8, full_n=8, dry_run=True,
                           from_cache=False)
    assert state["failures"] == []
    assert state["n_failures"] == 0


# ---------------------------------------------------------------------------
# Mode routing — dry paths must NEVER equal real paths
# ---------------------------------------------------------------------------

def test_route_paths_dry_run_never_targets_real_file():
    dry_json, dry_md = CC.route_paths(dry_run=True)
    real_json, real_md = CC.route_paths(dry_run=False)
    assert dry_json != real_json
    assert dry_md != real_md
    assert dry_json.name == "cal_c_dryrun.json"
    assert dry_md.name == "CAL_C_DRYRUN.md"
    assert real_json.name == "cal_c.json"
    assert real_md.name == "CAL_C.md"


def test_main_refuses_without_explicit_mode_and_writes_nothing(
        monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(CC, "OUT_JSON", tmp_path / "cal_c.json")
    monkeypatch.setattr(CC, "OUT_MD", tmp_path / "CAL_C.md")
    monkeypatch.setattr(CC, "DRYRUN_JSON", tmp_path / "cal_c_dryrun.json")
    monkeypatch.setattr(CC, "DRYRUN_MD", tmp_path / "CAL_C_DRYRUN.md")

    CC.main([])

    out = capsys.readouterr().out
    assert "refusing to run" in out
    assert "--real" in out and "--dry-run" in out
    assert not (tmp_path / "cal_c.json").exists()
    assert not (tmp_path / "cal_c_dryrun.json").exists()


def test_render_md_labels_dry_run_distinctly():
    records = [dict(canon="abc123def456ghi7", family="territory",
                    descriptor_s=1.0, t1_s=1.0, guard_s=1.0, full_conv_s=1.0,
                    total_s=4.0, t1_raw_pg=0.1, guard_passed=True,
                    full_conv_raw_pg=0.1)]
    draw_report = dict(seed_base=1, n_target=1, max_attempts=10, attempts=1,
                       accepted=1, attempt_cap_hit=False)
    dry_state = CC.build_state(records, draw_report, elapsed=1.0,
                               descriptor_n100=10, descriptor_n50_scale=0.5,
                               t1_deep=32, t1_shallow=8, t1_n=8,
                               guard_pairs=4, full_deep=64, full_shallow=8,
                               full_n=8, dry_run=True, from_cache=False)
    real_state = CC.build_state(records, draw_report, elapsed=1.0,
                                descriptor_n100=10, descriptor_n50_scale=0.5,
                                t1_deep=32, t1_shallow=8, t1_n=8,
                                guard_pairs=4, full_deep=64, full_shallow=8,
                                full_n=8, dry_run=False, from_cache=False)
    assert "DRY RUN" in CC.render_md(dry_state)
    assert "DRY RUN" not in CC.render_md(real_state)


# ---------------------------------------------------------------------------
# Attempt-cap reporting (pure — stub generator, no engine)
# ---------------------------------------------------------------------------

class _StubTurn:
    turn_type = "sequential"


class _StubGame:
    def __init__(self, seed, dup_after):
        self.turn_structure = _StubTurn()
        self._seed = seed
        self._dup_after = dup_after

    def canonical_hash(self):
        if self._dup_after is not None and self._seed >= self._dup_after:
            return "dup"
        return f"canon-{self._seed}"


class _StubGen:
    """Minimal GameGeneratorV2-shaped stub (generate_game/quick_reject
    only) — no engine, deterministic accept/reject for cap-detection tests."""
    def __init__(self, *, always_reject=False, dup_after=None):
        self.always_reject = always_reject
        self.dup_after = dup_after

    def generate_game(self, seed):
        return _StubGame(seed, self.dup_after)

    def quick_reject(self, game):
        return not self.always_reject


def test_draw_cal_genomes_reaches_target_without_hitting_cap():
    gen = _StubGen()
    accepted, report = CC.draw_cal_genomes(gen, seed_base=1000, n_target=5,
                                           max_attempts=100)
    assert len(accepted) == 5
    assert report["accepted"] == 5
    assert report["attempt_cap_hit"] is False
    assert report["attempts"] == 5


def test_draw_cal_genomes_reports_attempt_cap_hit():
    gen = _StubGen(always_reject=True)
    accepted, report = CC.draw_cal_genomes(gen, seed_base=1000, n_target=5,
                                           max_attempts=20)
    assert len(accepted) == 0
    assert report["attempts"] == 20
    assert report["attempt_cap_hit"] is True


def test_draw_cal_genomes_dedup_counts_toward_attempts_not_accepted():
    # seeds 1000,1001,1002 unique canons; 1003 is the FIRST "dup"-hash genome
    # (accepted, since "dup" isn't seen yet) and every seed after 1003 also
    # hashes to "dup" and is rejected -> accepted stalls at 4 well before the
    # n_target=5 while attempts keep consuming the cap.
    gen = _StubGen(dup_after=1003)
    accepted, report = CC.draw_cal_genomes(gen, seed_base=1000, n_target=5,
                                           max_attempts=10)
    assert report["attempts"] == 10
    assert len(accepted) == 4
    assert report["attempt_cap_hit"] is True


# ---------------------------------------------------------------------------
# Seed-offset disjointness claim
# ---------------------------------------------------------------------------

def test_cal_seed_base_transcription():
    assert CC.CAL_SEED_OFFSET == 500_000
    assert CC.CAL_SEED_BASE == seeds.GEN_SEED_BASE + 500_000


def test_cal_seed_base_disjoint_from_stage0_attempt_range():
    stage0_lo = seeds.GEN_SEED_BASE
    stage0_hi = seeds.GEN_SEED_BASE + STAGE0_MAX_ATTEMPTS
    cal_lo = CC.CAL_SEED_BASE
    cal_hi = CC.CAL_SEED_BASE + CC.MAX_ATTEMPTS
    assert cal_lo >= stage0_hi
    assert not (cal_lo < stage0_hi and stage0_lo < cal_hi)


def test_cal_seed_base_disjoint_from_smoke_range():
    lo, hi = seeds.RECORDED_STREAMS["smoke"]
    cal_lo = CC.CAL_SEED_BASE
    cal_hi = CC.CAL_SEED_BASE + CC.MAX_ATTEMPTS
    assert not (cal_lo < hi and lo < cal_hi)


def test_cal_seed_base_stays_within_gen_seed_base_span():
    """The CAL slot lives inside GEN_SEED_BASE's own registered SPAN, so no
    new seeds.RECORDED_STREAMS entry is needed — assert_disjoint() already
    validates GEN_SEED_BASE as a whole against every other recorded
    stream."""
    assert seeds.GEN_SEED_BASE <= CC.CAL_SEED_BASE
    assert CC.CAL_SEED_BASE + CC.MAX_ATTEMPTS <= seeds.GEN_SEED_BASE + seeds.SPAN


def test_assert_disjoint_still_passes():
    seeds.assert_disjoint()
