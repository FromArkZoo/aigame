#!/usr/bin/env python3
"""S4 komi auto-calibration tests (R21).

The driver in `experiments/r21_komi_calibration/calibrate_komi.py` has
three pure pieces: `passes_with_margin`, `pick_smallest_passing`, and
`calibrate_one(candidate, grid, evaluate_fn, ...)`. The PPO-driven
production path is `make_production_evaluate_fn` — tests stub
`evaluate_fn` and never launch PPO.

Run as: .venv/bin/python test_calibrate_komi.py
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent / "experiments" / "r21_komi_calibration"),
)
import calibrate_komi as ck  # noqa: E402


passed: list[str] = []
failed: list[tuple[str, str]] = []


def case(name: str, fn) -> None:
    try:
        fn()
        passed.append(name)
        print(f"  PASS  {name}")
    except Exception as e:  # noqa: BLE001
        failed.append((name, traceback.format_exc()))
        print(f"  FAIL  {name}: {e}")


# ----------------------------------------------------------------------
# passes_with_margin
# ----------------------------------------------------------------------


def test_passes_with_margin_strict_under_default_sigma() -> None:
    """Defaults: threshold=0.10, sigma≈0.0354, 2σ margin ≈ 0.0708.
    Pass requires bias ≤ 0.10 − 0.0708 = 0.0292. So:
      bias=0.025  → PASS
      bias=0.030  → FAIL (0.030 > 0.0292)
      bias=0.029  → PASS"""
    assert ck.passes_with_margin(0.025) is True
    assert ck.passes_with_margin(0.029) is True
    assert ck.passes_with_margin(0.030) is False
    assert ck.passes_with_margin(0.060) is False  # R20.5 PASSing games don't pass under 2σ margin
    assert ck.passes_with_margin(0.100) is False


def test_passes_with_margin_threshold_override() -> None:
    """Looser threshold = more lenient. threshold=0.15, default sigma:
    margin=0.0708 → pass if bias ≤ 0.0792."""
    assert ck.passes_with_margin(0.07, threshold=0.15) is True
    assert ck.passes_with_margin(0.08, threshold=0.15) is False


def test_passes_with_margin_sigma_override() -> None:
    """Tighter sigma = less margin needed. sigma=0.01 → 2σ=0.02 → pass if
    bias ≤ 0.08 at default threshold 0.10."""
    assert ck.passes_with_margin(0.08, sigma=0.01) is True
    assert ck.passes_with_margin(0.09, sigma=0.01) is False


def test_passes_with_margin_multiple_override() -> None:
    """1σ margin (less strict) lets bias=0.06 pass at default sigma."""
    assert ck.passes_with_margin(0.06, margin_multiple=1.0) is True
    # 3σ (more strict): margin≈0.106 — even bias=0.0 fails because
    # 0.10 - 0.106 = -0.006 < 0.
    assert ck.passes_with_margin(0.0, margin_multiple=3.0) is False


# ----------------------------------------------------------------------
# pick_smallest_passing
# ----------------------------------------------------------------------


def test_pick_smallest_baseline_passes() -> None:
    """If komi=0 already passes, decision is PASS_komi_0."""
    evs = [
        {"komi": 0.0, "g4_seat_bias": 0.02, "passed": True},
        {"komi": 0.05, "g4_seat_bias": 0.01, "passed": True},
    ]
    decision, k = ck.pick_smallest_passing(evs)
    assert decision == "PASS_komi_0"
    assert k == 0.0


def test_pick_smallest_first_grid_value_passes() -> None:
    """Smallest grid value 0.05 passes; baseline didn't."""
    evs = [
        {"komi": 0.0, "g4_seat_bias": 0.13, "passed": False},
        {"komi": 0.05, "g4_seat_bias": 0.02, "passed": True},
        {"komi": 0.10, "g4_seat_bias": 0.01, "passed": True},
    ]
    decision, k = ck.pick_smallest_passing(evs)
    assert decision == "PASS_komi_0.05"
    assert k == 0.05


def test_pick_smallest_partway_through_grid() -> None:
    """The first passing entry mid-grid wins; later ones ignored."""
    evs = [
        {"komi": 0.0, "g4_seat_bias": 0.14, "passed": False},
        {"komi": 0.05, "g4_seat_bias": 0.10, "passed": False},
        {"komi": 0.10, "g4_seat_bias": 0.08, "passed": False},
        {"komi": 0.15, "g4_seat_bias": 0.02, "passed": True},
        {"komi": 0.20, "g4_seat_bias": 0.01, "passed": True},
    ]
    decision, k = ck.pick_smallest_passing(evs)
    assert decision == "PASS_komi_0.15"
    assert k == 0.15


def test_pick_smallest_none_pass() -> None:
    """No grid value passes → FAIL_RUSH_BROKEN, calibrated_komi=None."""
    evs = [
        {"komi": 0.0, "g4_seat_bias": 0.20, "passed": False},
        {"komi": 0.30, "g4_seat_bias": 0.18, "passed": False},
    ]
    decision, k = ck.pick_smallest_passing(evs)
    assert decision == "FAIL_RUSH_BROKEN"
    assert k is None


def test_pick_smallest_walks_in_komi_order_not_input_order() -> None:
    """Robustness: even if evaluations were appended out of order, the
    pick still respects komi ordering."""
    evs = [
        {"komi": 0.20, "g4_seat_bias": 0.01, "passed": True},
        {"komi": 0.05, "g4_seat_bias": 0.02, "passed": True},
        {"komi": 0.10, "g4_seat_bias": 0.01, "passed": True},
    ]
    decision, k = ck.pick_smallest_passing(evs)
    assert decision == "PASS_komi_0.05"
    assert k == 0.05


# ----------------------------------------------------------------------
# calibrate_one (full per-candidate flow with stubbed evaluate_fn)
# ----------------------------------------------------------------------


def make_stub(biases: dict[float, float]):
    """Return an evaluate_fn that maps a komi value to a canned bias."""
    calls: list[tuple[dict, float]] = []

    def stub(candidate: dict, komi: float) -> dict:
        calls.append((candidate, komi))
        if komi not in biases:
            raise KeyError(f"stub has no bias for komi={komi}")
        return {"g4_seat_bias": biases[komi]}
    stub.calls = calls  # type: ignore[attr-defined]
    return stub


def test_calibrate_one_baseline_passes_short_circuits() -> None:
    """If baseline (komi=0) passes, no grid values are evaluated."""
    stub = make_stub({0.0: 0.02})
    candidate = {"substrate": "menger", "game_id": "g1", "db": "x"}
    record = ck.calibrate_one(
        candidate,
        grid=[0.05, 0.10, 0.15, 0.20],
        evaluate_fn=stub,
        include_baseline=True,
    )
    assert record["decision"] == "PASS_komi_0"
    assert record["calibrated_komi"] == 0.0
    # Only the baseline was evaluated.
    assert len(stub.calls) == 1
    assert stub.calls[0][1] == 0.0


def test_calibrate_one_walks_grid_until_first_pass() -> None:
    """Baseline fails; grid evaluated until first PASS, then stops."""
    stub = make_stub({
        0.0: 0.14, 0.05: 0.10, 0.10: 0.02, 0.15: 0.01, 0.20: 0.01,
    })
    candidate = {"substrate": "menger", "game_id": "g1", "db": "x"}
    record = ck.calibrate_one(
        candidate, grid=[0.05, 0.10, 0.15, 0.20],
        evaluate_fn=stub, include_baseline=True,
    )
    assert record["decision"] == "PASS_komi_0.1"
    assert record["calibrated_komi"] == 0.10
    # 4 calls: baseline + 3 grid values (0.05, 0.10), stopped after 0.10 passed.
    komis_evaluated = [c[1] for c in stub.calls]
    assert komis_evaluated == [0.0, 0.05, 0.10]


def test_calibrate_one_evaluates_all_grid_on_full_fail() -> None:
    """Every grid value fails — all get evaluated, decision is FAIL_RUSH_BROKEN."""
    stub = make_stub({
        0.0: 0.20, 0.05: 0.18, 0.10: 0.16, 0.15: 0.14, 0.20: 0.12, 0.25: 0.11, 0.30: 0.11,
    })
    candidate = {"substrate": "menger", "game_id": "g1", "db": "x"}
    record = ck.calibrate_one(
        candidate, grid=[0.05, 0.10, 0.15, 0.20, 0.25, 0.30],
        evaluate_fn=stub, include_baseline=True,
    )
    assert record["decision"] == "FAIL_RUSH_BROKEN"
    assert record["calibrated_komi"] is None
    # All 7 evaluated (baseline + 6 grid values).
    assert len(stub.calls) == 7


def test_calibrate_one_records_carry_decisions() -> None:
    """The per-komi evaluations are preserved in the record so the user
    can audit which grid values were tried and why each failed."""
    stub = make_stub({0.0: 0.14, 0.05: 0.10, 0.10: 0.02})
    candidate = {"substrate": "menger", "game_id": "g1", "db": "x"}
    record = ck.calibrate_one(
        candidate, grid=[0.05, 0.10],
        evaluate_fn=stub, include_baseline=True,
    )
    evs = record["evaluations"]
    assert [e["komi"] for e in evs] == [0.0, 0.05, 0.10]
    assert [e["g4_seat_bias"] for e in evs] == [0.14, 0.10, 0.02]
    assert [e["passed"] for e in evs] == [False, False, True]


def test_calibrate_one_skips_baseline_when_disabled() -> None:
    """When the caller pre-supplied baseline_g4_bias (or simply wants
    to skip the komi=0 retrain), include_baseline=False starts from
    the first grid value."""
    stub = make_stub({0.05: 0.02, 0.10: 0.01})
    candidate = {"substrate": "menger", "game_id": "g1", "db": "x"}
    record = ck.calibrate_one(
        candidate, grid=[0.05, 0.10],
        evaluate_fn=stub, include_baseline=False,
    )
    komis_evaluated = [c[1] for c in stub.calls]
    assert komis_evaluated == [0.05]  # stopped after first pass
    assert record["decision"] == "PASS_komi_0.05"


def test_calibrate_one_preserves_candidate_fields() -> None:
    """Input fields (substrate, db, game_id, etc.) survive into the output record."""
    stub = make_stub({0.0: 0.02})
    candidate = {
        "substrate": "menger", "game_id": "g1", "db": "x.db",
        "baseline_g4_bias": 0.13, "extra_field": "should-survive",
    }
    record = ck.calibrate_one(
        candidate, grid=[0.05], evaluate_fn=stub, include_baseline=True,
    )
    assert record["substrate"] == "menger"
    assert record["db"] == "x.db"
    assert record["baseline_g4_bias"] == 0.13
    assert record["extra_field"] == "should-survive"


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("Komi auto-calibration tests (R21 S4)")
    print("-" * 50)
    case("passes_with_margin_strict_under_default_sigma", test_passes_with_margin_strict_under_default_sigma)
    case("passes_with_margin_threshold_override", test_passes_with_margin_threshold_override)
    case("passes_with_margin_sigma_override", test_passes_with_margin_sigma_override)
    case("passes_with_margin_multiple_override", test_passes_with_margin_multiple_override)
    case("pick_smallest_baseline_passes", test_pick_smallest_baseline_passes)
    case("pick_smallest_first_grid_value_passes", test_pick_smallest_first_grid_value_passes)
    case("pick_smallest_partway_through_grid", test_pick_smallest_partway_through_grid)
    case("pick_smallest_none_pass", test_pick_smallest_none_pass)
    case("pick_smallest_walks_in_komi_order_not_input_order", test_pick_smallest_walks_in_komi_order_not_input_order)
    case("calibrate_one_baseline_passes_short_circuits", test_calibrate_one_baseline_passes_short_circuits)
    case("calibrate_one_walks_grid_until_first_pass", test_calibrate_one_walks_grid_until_first_pass)
    case("calibrate_one_evaluates_all_grid_on_full_fail", test_calibrate_one_evaluates_all_grid_on_full_fail)
    case("calibrate_one_records_carry_decisions", test_calibrate_one_records_carry_decisions)
    case("calibrate_one_skips_baseline_when_disabled", test_calibrate_one_skips_baseline_when_disabled)
    case("calibrate_one_preserves_candidate_fields", test_calibrate_one_preserves_candidate_fields)
    print("-" * 50)
    print(f"{len(passed)} passed, {len(failed)} failed")
    if failed:
        for name, tb in failed:
            print(f"\n--- {name} ---\n{tb}")
        sys.exit(1)
