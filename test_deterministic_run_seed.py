#!/usr/bin/env python3
"""C1 patch test — deterministic_run_seed() reproducibility.

R18 followup: confirms the seed keyed on game_id is stable across Python
runs (no PYTHONHASHSEED contamination), differs per run_idx, and produces
distinct seeds for distinct game_ids.

Run as: .venv/bin/python test_deterministic_run_seed.py
"""
from __future__ import annotations

import os
import subprocess
import sys
import traceback

from run import deterministic_run_seed


def _check(label: str, ok: bool, *, detail: str = "") -> bool:
    status = "PASS" if ok else "FAIL"
    print(f"  {status} | {label}{(': ' + detail) if detail else ''}")
    return ok


def test_same_input_same_output():
    a = deterministic_run_seed("abc123def456", 0)
    b = deterministic_run_seed("abc123def456", 0)
    return _check("same (game_id, run_idx) -> same seed", a == b, detail=f"{a} == {b}")


def test_different_run_idx_different_seed():
    s0 = deterministic_run_seed("abc123def456", 0)
    s1 = deterministic_run_seed("abc123def456", 1)
    s2 = deterministic_run_seed("abc123def456", 2)
    distinct = len({s0, s1, s2}) == 3
    return _check(
        "(same game_id, different run_idx) -> distinct seeds",
        distinct,
        detail=f"run_idx 0/1/2 -> {s0}/{s1}/{s2}",
    )


def test_different_game_id_different_seed():
    s_a = deterministic_run_seed("aaaaaaaaaaaa", 0)
    s_b = deterministic_run_seed("bbbbbbbbbbbb", 0)
    return _check(
        "different game_id -> different seed",
        s_a != s_b,
        detail=f"a={s_a} b={s_b}",
    )


def test_seed_in_uint32_range():
    s = deterministic_run_seed("abc123def456", 0)
    in_range = 0 <= s < 2 ** 32
    return _check(
        "seed fits in [0, 2^32)",
        in_range,
        detail=f"seed={s}",
    )


def test_stable_across_python_invocations():
    """Different Python processes must produce the same seed.

    Guards against accidentally using `hash(...)` (which is salted with
    PYTHONHASHSEED and changes per process) instead of a stable hash.
    """
    script = (
        "from run import deterministic_run_seed; "
        "print(deterministic_run_seed('abc123def456', 0))"
    )
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"
    out_a = subprocess.run(
        [sys.executable, "-c", script], cwd="/Users/jamesbrowne/aigame",
        capture_output=True, text=True, env=env,
    ).stdout.strip()
    env["PYTHONHASHSEED"] = "12345"
    out_b = subprocess.run(
        [sys.executable, "-c", script], cwd="/Users/jamesbrowne/aigame",
        capture_output=True, text=True, env=env,
    ).stdout.strip()
    return _check(
        "seed is stable across Python processes (different PYTHONHASHSEED)",
        out_a == out_b and out_a != "",
        detail=f"{out_a!r} == {out_b!r}",
    )


def test_realistic_r18_game_ids():
    """Spot-check on actual R18 game_ids — same id -> same seed, different ids differ."""
    real_ids = [
        "f87428258916", "1e11adebcc35", "c8f1927d1bea",
        "8776b2026957", "0f5e931fa3e1",
    ]
    seeds = {gid: deterministic_run_seed(gid, 0) for gid in real_ids}
    all_distinct = len(set(seeds.values())) == len(real_ids)
    return _check(
        "5 real R18 game_ids -> 5 distinct seeds",
        all_distinct,
        detail=str(seeds),
    )


def main() -> int:
    print("=" * 72)
    print("C1 patch — deterministic_run_seed() tests")
    print("=" * 72)
    tests = [
        test_same_input_same_output,
        test_different_run_idx_different_seed,
        test_different_game_id_different_seed,
        test_seed_in_uint32_range,
        test_stable_across_python_invocations,
        test_realistic_r18_game_ids,
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
