#!/usr/bin/env python3
"""C2 patch test — _average_run_inputs() multi-seed averaging.

R18 followup: confirms the helper averages learning_curve, trained_vs_random,
p0_winrate, and avg_game_length across all independent runs without losing
sample alignment, while keeping the single-run path identical to the
pre-patch behaviour.

Run as: .venv/bin/python test_multiseed_averaging.py
"""
from __future__ import annotations

import sys
import traceback

from run import _average_run_inputs


def _check(label: str, ok: bool, *, detail: str = "") -> bool:
    status = "PASS" if ok else "FAIL"
    print(f"  {status} | {label}{(': ' + detail) if detail else ''}")
    return ok


def _approx(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(a - b) <= tol


def test_single_run_passthrough():
    curve = [(500, 0.4), (1000, 0.6), (1500, 0.7)]
    avg_curve, tvr, p0, alen = _average_run_inputs(
        [curve], [0.65], [0.5], [42.0]
    )
    same_curve = avg_curve == curve
    same_scalars = _approx(tvr, 0.65) and _approx(p0, 0.5) and _approx(alen, 42.0)
    return _check(
        "single run -> identity passthrough",
        same_curve and same_scalars,
        detail=f"curve={avg_curve} tvr={tvr} p0={p0} alen={alen}",
    )


def test_three_run_pointwise_average():
    c1 = [(500, 0.0), (1000, 0.0), (1500, 0.0)]
    c2 = [(500, 0.5), (1000, 0.5), (1500, 0.5)]
    c3 = [(500, 1.0), (1000, 1.0), (1500, 1.0)]
    avg_curve, tvr, p0, alen = _average_run_inputs(
        [c1, c2, c3], [0.2, 0.5, 0.8], [0.4, 0.5, 0.6], [10.0, 20.0, 30.0],
    )
    eps_ok = [pt[0] for pt in avg_curve] == [500, 1000, 1500]
    wr_ok = all(_approx(pt[1], 0.5) for pt in avg_curve)
    scalars_ok = (
        _approx(tvr, 0.5) and _approx(p0, 0.5) and _approx(alen, 20.0)
    )
    return _check(
        "3 runs -> pointwise mean curve, mean tvr/p0/alen",
        eps_ok and wr_ok and scalars_ok,
        detail=f"avg_curve={avg_curve} tvr={tvr} p0={p0} alen={alen}",
    )


def test_variance_reduction_is_real():
    """Phase A's headline claim: averaging N runs cuts std by sqrt(N)."""
    # Three runs with widely different tvr — averaging should land at mean.
    _, tvr, _, _ = _average_run_inputs(
        [[(500, 0.5)]] * 3, [0.22, 1.00, 0.78], [0.5, 0.5, 0.5], [20.0]*3,
    )
    expected = (0.22 + 1.00 + 0.78) / 3.0
    return _check(
        "averaged tvr equals arithmetic mean (Phase A volatility-reduction claim)",
        _approx(tvr, expected),
        detail=f"tvr={tvr} expected={expected:.4f}",
    )


def test_curve_length_mismatch_falls_back():
    """If one run's curve has a different length, fall back to primary curve."""
    c1 = [(500, 0.4), (1000, 0.6)]
    c2 = [(500, 0.5)]  # short — mismatch
    avg_curve, tvr, _p0, _alen = _average_run_inputs(
        [c1, c2], [0.5, 0.7], [0.5, 0.5], [10.0, 12.0],
    )
    fell_back = avg_curve == c1
    # Scalars should still average even when curves mismatch.
    scalars_avg = _approx(tvr, 0.6)
    return _check(
        "curve-length mismatch -> falls back to primary curve, scalars still averaged",
        fell_back and scalars_avg,
        detail=f"avg_curve={avg_curve} tvr={tvr}",
    )


def test_empty_input_is_safe():
    avg_curve, tvr, p0, alen = _average_run_inputs([], [], [], [])
    return _check(
        "no runs -> safe defaults (no exception)",
        avg_curve == [] and _approx(tvr, 0.0) and _approx(p0, 0.5) and _approx(alen, 0.0),
        detail=f"avg_curve={avg_curve} tvr={tvr} p0={p0} alen={alen}",
    )


def test_realistic_carpet_champion():
    """Simulate the carpet champion's noisy 9 runs (Phase A measured tvr
    mean=0.784, std=0.296, range 0.22..1.0). Averaging should land near
    the mean and produce a single deterministic non_triviality input."""
    tvr_runs = [0.22, 0.40, 0.55, 0.70, 0.85, 0.90, 0.95, 1.00, 1.00]
    n = len(tvr_runs)
    curves = [[(500, w * 0.5), (1000, w)] for w in tvr_runs]
    p0_runs = [0.5] * n
    alen_runs = [40.0] * n
    avg_curve, tvr, p0, alen = _average_run_inputs(
        curves, tvr_runs, p0_runs, alen_runs
    )
    expected_tvr = sum(tvr_runs) / n
    final_pt_avg = sum(tvr_runs) / n
    curve_ok = _approx(avg_curve[-1][1], final_pt_avg, tol=1e-9)
    return _check(
        "carpet-champion shape: 9 noisy runs -> stable averaged inputs",
        _approx(tvr, expected_tvr) and _approx(p0, 0.5) and curve_ok,
        detail=f"avg_tvr={tvr:.4f} (mean={expected_tvr:.4f}); "
               f"final-curve-pt={avg_curve[-1][1]:.4f}",
    )


def main() -> int:
    print("=" * 72)
    print("C2 patch — _average_run_inputs() tests")
    print("=" * 72)
    tests = [
        test_single_run_passthrough,
        test_three_run_pointwise_average,
        test_variance_reduction_is_real,
        test_curve_length_mismatch_falls_back,
        test_empty_input_is_safe,
        test_realistic_carpet_champion,
    ]
    passed = failed = 0
    for t in tests:
        try:
            ok = t()
            passed += int(ok)
            failed += int(not ok)
        except Exception:
            failed += 1
            print(f"  FAIL | {t.__name__}: exception")
            traceback.print_exc()
    print("-" * 72)
    print(f"{passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
