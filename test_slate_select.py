#!/usr/bin/env python3
"""Slate dedup tests (R21 S1b).

S1b is the equilibrium-fingerprint dedup at slate-build. Catches games
with distinct rule blobs but identical trained-policy stats — what R20.5
called the functional-equivalence trio (66c7c98d / 77f82883 / c9fd0350
all showed sampled_p1_wr=0.560, sampled_len=57.1, greedy_p1_wr=0.100
under the same PPO seed).

These tests exercise the pure dedup logic with a stubbed evaluate_fn
that returns canned fingerprints. The full PPO-driven path is exercised
at launch time.

Run as: .venv/bin/python test_slate_select.py
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

# slate_select lives in experiments/r21_finalization/; import via path.
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent / "experiments" / "r21_finalization"),
)
from slate_select import dedup_slate, make_fingerprint  # noqa: E402


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
# Helpers
# ----------------------------------------------------------------------


def make_eval_stub(stats: dict[str, dict[str, float]]):
    """Return an evaluate_fn that looks up each candidate's game_id in
    `stats` and returns the canned (sampled_p1_wr, sampled_avg_length,
    greedy_p1_wr) dict."""
    calls: list[str] = []

    def stub(candidate: dict) -> dict:
        gid = candidate["game_id"]
        calls.append(gid)
        return stats[gid]
    stub.calls = calls  # type: ignore[attr-defined]
    return stub


# ----------------------------------------------------------------------
# make_fingerprint tests
# ----------------------------------------------------------------------


def test_fingerprint_rounds_to_one_decimal_by_default() -> None:
    """R20.5 functional-equivalence trio matched to 1 decimal."""
    fp = make_fingerprint(
        sampled_p1_wr=0.560, sampled_len=57.13, greedy_p1_wr=0.100,
    )
    assert fp == (0.6, 57.1, 0.1), f"unexpected fingerprint: {fp}"


def test_fingerprint_collapses_r20_5_trio() -> None:
    """The actual R20.5 functional-equivalence trio inputs must collapse
    to a single fingerprint at 1-decimal precision."""
    fps = {
        make_fingerprint(0.560, 57.1, 0.100),
        make_fingerprint(0.560, 57.1, 0.100),  # 77f8288387d9
        make_fingerprint(0.560, 57.1, 0.100),  # c9fd0350fdf7
    }
    assert len(fps) == 1, (
        f"R20.5 functional-equivalence trio must collapse to 1 fingerprint, got {fps}"
    )


def test_fingerprint_distinguishes_real_differences() -> None:
    """sampled_p1_wr 0.560 vs 0.630 → distinct (1-decimal: 0.6 vs 0.6 — collapses)
    but 0.560 vs 0.700 → distinct (0.6 vs 0.7)."""
    # Within rounding (intended collapse — pie correction at the same rate)
    fp_a = make_fingerprint(0.560, 57.1, 0.100)
    fp_b = make_fingerprint(0.630, 57.1, 0.100)
    assert fp_a == fp_b  # 0.6 == 0.6 at 1-decimal — by design
    # Across rounding (real diff)
    fp_c = make_fingerprint(0.700, 57.1, 0.100)
    assert fp_a != fp_c, f"0.6 vs 0.7 must differ, got {fp_a} vs {fp_c}"


def test_fingerprint_precision_parameter() -> None:
    """At precision=2, finer differences survive that 1-decimal collapses."""
    # 0.560 vs 0.580 — same at precision=1 (both 0.6), distinct at precision=2.
    fp1_a = make_fingerprint(0.560, 57.1, 0.100, precision=1)
    fp1_b = make_fingerprint(0.580, 57.1, 0.100, precision=1)
    assert fp1_a == fp1_b, f"precision=1 should collapse 0.56 vs 0.58, got {fp1_a} {fp1_b}"
    fp2_a = make_fingerprint(0.560, 57.1, 0.100, precision=2)
    fp2_b = make_fingerprint(0.580, 57.1, 0.100, precision=2)
    assert fp2_a != fp2_b, (
        f"precision=2 should keep 0.56 vs 0.58 distinct, got {fp2_a} {fp2_b}"
    )


# ----------------------------------------------------------------------
# dedup_slate tests
# ----------------------------------------------------------------------


def test_dedup_drops_r20_5_trio() -> None:
    """3 candidates with identical fingerprints → 1 ACCEPT + 2 DROP_DUP."""
    stats = {
        "66c7c98d": dict(sampled_p1_wr=0.560, sampled_avg_length=57.1, greedy_p1_wr=0.100),
        "77f82883": dict(sampled_p1_wr=0.560, sampled_avg_length=57.1, greedy_p1_wr=0.100),
        "c9fd0350": dict(sampled_p1_wr=0.560, sampled_avg_length=57.1, greedy_p1_wr=0.100),
    }
    stub = make_eval_stub(stats)
    candidates = [
        {"substrate": "menger", "game_id": gid, "db": "x.db"}
        for gid in stats
    ]
    records = dedup_slate(candidates, evaluate_fn=stub, target_size=6, precision=1)
    accepted = [r for r in records if r["decision"] == "ACCEPT"]
    dropped = [r for r in records if r["decision"] == "DROP_DUP"]
    assert len(accepted) == 1, f"expected 1 ACCEPT, got {len(accepted)}"
    assert len(dropped) == 2, f"expected 2 DROP_DUP, got {len(dropped)}"
    # The 2 DROP_DUP rows must point at the first-accepted game_id.
    assert all(r["duplicate_of"] == "66c7c98d" for r in dropped)


def test_dedup_keeps_distinct_candidates() -> None:
    """3 distinct-fingerprint candidates → 3 ACCEPTs, no drops."""
    stats = {
        "g1": dict(sampled_p1_wr=0.500, sampled_avg_length=50.0, greedy_p1_wr=0.500),
        "g2": dict(sampled_p1_wr=0.600, sampled_avg_length=55.0, greedy_p1_wr=0.300),
        "g3": dict(sampled_p1_wr=0.700, sampled_avg_length=60.0, greedy_p1_wr=0.100),
    }
    stub = make_eval_stub(stats)
    candidates = [
        {"substrate": "menger", "game_id": gid, "db": "x.db"}
        for gid in stats
    ]
    records = dedup_slate(candidates, evaluate_fn=stub, target_size=6, precision=1)
    accepted = [r for r in records if r["decision"] == "ACCEPT"]
    assert len(accepted) == 3
    assert all(r["decision"] != "DROP_DUP" for r in records)


def test_dedup_respects_target_size() -> None:
    """target_size=3 + 5 distinct candidates → first 3 ACCEPT, next 2 SKIP."""
    stats = {
        f"g{i}": dict(
            sampled_p1_wr=0.5 + 0.05 * i,
            sampled_avg_length=50.0 + i,
            greedy_p1_wr=0.5,
        )
        for i in range(5)
    }
    stub = make_eval_stub(stats)
    candidates = [
        {"substrate": "menger", "game_id": gid, "db": "x.db"}
        for gid in stats
    ]
    records = dedup_slate(candidates, evaluate_fn=stub, target_size=3, precision=1)
    accepted = [r for r in records if r["decision"] == "ACCEPT"]
    skipped = [r for r in records if r["decision"] == "SKIP_TARGET_MET"]
    assert len(accepted) == 3
    assert len(skipped) == 2


def test_dedup_skip_does_not_evaluate() -> None:
    """SKIP_TARGET_MET candidates must not consume an evaluate_fn call —
    PPO is expensive; we only run it on candidates we might keep."""
    stats = {
        "g1": dict(sampled_p1_wr=0.5, sampled_avg_length=50.0, greedy_p1_wr=0.5),
        "g2": dict(sampled_p1_wr=0.6, sampled_avg_length=55.0, greedy_p1_wr=0.3),
        "g3": dict(sampled_p1_wr=0.7, sampled_avg_length=60.0, greedy_p1_wr=0.1),
    }
    stub = make_eval_stub(stats)
    candidates = [
        {"substrate": "menger", "game_id": gid, "db": "x.db"}
        for gid in stats
    ]
    records = dedup_slate(candidates, evaluate_fn=stub, target_size=1, precision=1)
    # Only one evaluate_fn call: the first candidate, which gets ACCEPTed.
    assert stub.calls == ["g1"], f"expected only g1 evaluated, got {stub.calls}"
    assert records[0]["decision"] == "ACCEPT"
    assert records[1]["decision"] == "SKIP_TARGET_MET"
    assert records[2]["decision"] == "SKIP_TARGET_MET"


def test_dedup_processes_in_input_order() -> None:
    """The accept-vs-drop decision must depend on rank order. Reversing
    the input changes WHICH game gets ACCEPTed for a shared fingerprint."""
    stats = {
        "A": dict(sampled_p1_wr=0.6, sampled_avg_length=57.1, greedy_p1_wr=0.1),
        "B": dict(sampled_p1_wr=0.6, sampled_avg_length=57.1, greedy_p1_wr=0.1),
    }
    stub_ab = make_eval_stub(stats)
    rec_ab = dedup_slate(
        [{"substrate": "m", "game_id": "A", "db": "x"},
         {"substrate": "m", "game_id": "B", "db": "x"}],
        evaluate_fn=stub_ab, target_size=6, precision=1,
    )
    assert rec_ab[0]["decision"] == "ACCEPT" and rec_ab[1]["decision"] == "DROP_DUP"
    assert rec_ab[1]["duplicate_of"] == "A"

    stub_ba = make_eval_stub(stats)
    rec_ba = dedup_slate(
        [{"substrate": "m", "game_id": "B", "db": "x"},
         {"substrate": "m", "game_id": "A", "db": "x"}],
        evaluate_fn=stub_ba, target_size=6, precision=1,
    )
    assert rec_ba[0]["decision"] == "ACCEPT" and rec_ba[1]["decision"] == "DROP_DUP"
    assert rec_ba[1]["duplicate_of"] == "B"


def test_dedup_records_carry_fingerprint_data() -> None:
    """Each per-candidate record must include the raw stats + fingerprint
    so downstream analysis can audit the dedup decision."""
    stats = {
        "g1": dict(sampled_p1_wr=0.560, sampled_avg_length=57.1, greedy_p1_wr=0.100),
    }
    stub = make_eval_stub(stats)
    records = dedup_slate(
        [{"substrate": "m", "game_id": "g1", "db": "x"}],
        evaluate_fn=stub, target_size=6, precision=1,
    )
    r = records[0]
    assert r["fingerprint"] == [0.6, 57.1, 0.1]
    assert r["sampled_p1_wr"] == 0.560
    assert r["sampled_avg_length"] == 57.1
    assert r["greedy_p1_wr"] == 0.100


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("Slate dedup tests (R21 S1b)")
    print("-" * 50)
    case("fingerprint_rounds_to_one_decimal_by_default", test_fingerprint_rounds_to_one_decimal_by_default)
    case("fingerprint_collapses_r20_5_trio", test_fingerprint_collapses_r20_5_trio)
    case("fingerprint_distinguishes_real_differences", test_fingerprint_distinguishes_real_differences)
    case("fingerprint_precision_parameter", test_fingerprint_precision_parameter)
    case("dedup_drops_r20_5_trio", test_dedup_drops_r20_5_trio)
    case("dedup_keeps_distinct_candidates", test_dedup_keeps_distinct_candidates)
    case("dedup_respects_target_size", test_dedup_respects_target_size)
    case("dedup_skip_does_not_evaluate", test_dedup_skip_does_not_evaluate)
    case("dedup_processes_in_input_order", test_dedup_processes_in_input_order)
    case("dedup_records_carry_fingerprint_data", test_dedup_records_carry_fingerprint_data)
    print("-" * 50)
    print(f"{len(passed)} passed, {len(failed)} failed")
    if failed:
        for name, tb in failed:
            print(f"\n--- {name} ---\n{tb}")
        sys.exit(1)
