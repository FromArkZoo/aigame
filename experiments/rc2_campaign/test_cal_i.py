import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from experiments.rc2_campaign import bars as B
from experiments.rc2_campaign import cal_i as CI
from experiments.rc2_campaign import run_campaign as RC


def _fake_result(key: str, pg: float, n: int = 24) -> dict:
    return dict(key=key, family="x", blind_mean=3.0, n=n,
                planning_gap=pg, per_stream={"46": pg, "47": pg},
                wins=n // 2, draws=0, losses=n // 2, mean_length=12.0)


# ---------------------------------------------------------------------------
# Verdict logic (pure) — separation >=/< CAL_I_THRESHOLD -> PASS/FAIL
# ---------------------------------------------------------------------------

def test_verdict_from_pg_pass_above_threshold():
    verdict, sep, detail = CI.verdict_from_pg(0.30, -0.20)  # separation 0.50
    assert sep == pytest.approx(0.50)
    assert sep >= B.CAL_I_THRESHOLD
    assert verdict == "PASS"
    assert "PASS" in detail


def test_verdict_from_pg_fail_below_threshold():
    verdict, sep, detail = CI.verdict_from_pg(0.10, 0.00)  # separation 0.10
    assert sep == pytest.approx(0.10)
    assert sep < B.CAL_I_THRESHOLD
    assert verdict == "FAIL"
    assert "FAIL" in detail


def test_verdict_from_pg_boundary_is_inclusive_pass():
    """separation == CAL_I_THRESHOLD exactly -> PASS (bar is >=, not >)."""
    pg_s4 = 0.0
    pg_d4015 = pg_s4 + B.CAL_I_THRESHOLD
    verdict, sep, _ = CI.verdict_from_pg(pg_d4015, pg_s4)
    assert sep == pytest.approx(B.CAL_I_THRESHOLD)
    assert verdict == "PASS"


def test_verdict_from_pg_never_hardcodes_threshold():
    """The comparison must track bars.CAL_I_THRESHOLD, not a local literal."""
    assert CI.CAL_I_THRESHOLD is B.CAL_I_THRESHOLD


# ---------------------------------------------------------------------------
# File-routing rule — dry run must NEVER return the real cal_i.json path
# ---------------------------------------------------------------------------

def test_route_paths_dry_run_never_targets_real_file():
    dry_json, dry_md = CI.route_paths(dry_run=True)
    real_json, real_md = CI.route_paths(dry_run=False)
    assert dry_json != real_json
    assert dry_md != real_md
    assert dry_json.name == "cal_i_dryrun.json"
    assert dry_md.name == "CAL_I_DRYRUN.md"
    assert real_json.name == "cal_i.json"
    assert real_md.name == "CAL_I.md"
    # the real path is exactly the one run_campaign.load_cal_i reads
    assert real_json == RC.CAL_I_JSON


def test_main_refuses_without_explicit_mode_and_writes_nothing(
        monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(CI, "OUT_JSON", tmp_path / "cal_i.json")
    monkeypatch.setattr(CI, "OUT_MD", tmp_path / "CAL_I.md")
    monkeypatch.setattr(CI, "DRYRUN_JSON", tmp_path / "cal_i_dryrun.json")
    monkeypatch.setattr(CI, "DRYRUN_MD", tmp_path / "CAL_I_DRYRUN.md")

    CI.main([])

    out = capsys.readouterr().out
    assert "refusing to run" in out
    assert "--real" in out and "--dry-run" in out
    assert not (tmp_path / "cal_i.json").exists()
    assert not (tmp_path / "cal_i_dryrun.json").exists()


# ---------------------------------------------------------------------------
# JSON shape pins the contract run_campaign.py::load_cal_i expects
# ---------------------------------------------------------------------------

def test_writer_output_satisfies_load_cal_i_contract_pass(monkeypatch, tmp_path):
    results = {
        "d4015a646ae3": _fake_result("d4015a646ae3", 0.30),
        "S4": _fake_result("S4", -0.20),
    }
    state = CI.build_state(results, elapsed=12.3, streams=(46, 47),
                           games_per_stream=12, deep_sims=128,
                           shallow_sims=16, dry_run=False, from_cache=False)
    assert state["verdict"] == "PASS"

    p = tmp_path / "cal_i.json"
    p.write_text(json.dumps(state))
    monkeypatch.setattr(RC, "CAL_I_JSON", p)

    loaded = RC.load_cal_i(smoke=False)
    assert loaded["verdict"] == "PASS"
    # audit-trail fields load_cal_i's callers (write_reports, cal_i_pass)
    # and the report/audit trail actually read
    assert "verdict_detail" in loaded
    assert loaded["separation"] == pytest.approx(0.50)
    assert loaded["protocol"]["threshold"] == B.CAL_I_THRESHOLD
    assert loaded["protocol"]["streams"] == [46, 47]
    assert loaded["protocol"]["n"] == 24
    assert set(loaded["results"]) == {"d4015a646ae3", "S4"}


def test_writer_output_satisfies_load_cal_i_contract_fail(monkeypatch, tmp_path):
    results = {
        "d4015a646ae3": _fake_result("d4015a646ae3", 0.05),
        "S4": _fake_result("S4", 0.00),
    }
    state = CI.build_state(results, elapsed=1.0, streams=(46, 47),
                           games_per_stream=12, deep_sims=128,
                           shallow_sims=16, dry_run=False, from_cache=False)
    assert state["verdict"] == "FAIL"

    p = tmp_path / "cal_i.json"
    p.write_text(json.dumps(state))
    monkeypatch.setattr(RC, "CAL_I_JSON", p)

    loaded = RC.load_cal_i(smoke=False)
    assert loaded["verdict"] == "FAIL"

    # a Campaign wired to this artifact must NOT treat FAIL as a pass
    camp = RC.Campaign.__new__(RC.Campaign)
    camp.smoke = False
    camp.cal_i = loaded
    assert camp.cal_i_pass() is False


def test_load_cal_i_missing_file_refuses(monkeypatch, tmp_path):
    monkeypatch.setattr(RC, "CAL_I_JSON", tmp_path / "does_not_exist.json")
    with pytest.raises(SystemExit):
        RC.load_cal_i(smoke=False)


def test_load_cal_i_smoke_never_reads_the_file(monkeypatch, tmp_path):
    monkeypatch.setattr(RC, "CAL_I_JSON", tmp_path / "does_not_exist.json")
    assert RC.load_cal_i(smoke=True) == {"verdict": "SKIPPED_SMOKE"}


# ---------------------------------------------------------------------------
# Dry-run sizing stays tiny and distinct from the real (binding) instrument
# ---------------------------------------------------------------------------

def test_dry_run_sizing_is_tiny_and_distinct_from_real():
    assert CI.DRY_GAMES_PER_STREAM < CI.GAMES_PER_STREAM
    assert CI.DRY_DEEP_SIMS < CI.DEEP_SIMS
    assert CI.DRY_SHALLOW_SIMS < CI.SHALLOW_SIMS


def test_render_md_labels_dry_run_distinctly():
    results = {
        "d4015a646ae3": _fake_result("d4015a646ae3", 0.30, n=4),
        "S4": _fake_result("S4", -0.20, n=4),
    }
    dry_state = CI.build_state(results, elapsed=1.0, streams=(46, 47),
                               games_per_stream=2, deep_sims=32,
                               shallow_sims=8, dry_run=True, from_cache=False)
    real_state = CI.build_state(results, elapsed=1.0, streams=(46, 47),
                                games_per_stream=2, deep_sims=32,
                                shallow_sims=8, dry_run=False, from_cache=False)
    assert "DRY RUN" in CI.render_md(dry_state)
    assert "DRY RUN" not in CI.render_md(real_state)
