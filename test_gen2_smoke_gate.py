#!/usr/bin/env python3
"""Z4 half-run smoke gate tests.

The gate has three orthogonal pieces:
  - `evaluate_gate(peak, threshold)`: pure decision function (WAITING /
    PASS / FAIL) — directly testable.
  - `read_gen2_peak_ge(db_path)`: SQLite read — testable with a
    synthetic DB.
  - polling loop + SIGTERM: integration glue, kept thin so the failure
    modes that matter live in the two pieces above.

Run as: .venv/bin/python test_gen2_smoke_gate.py
"""
from __future__ import annotations

import sqlite3
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent / "experiments" / "r21_driver"),
)
import gen2_smoke_gate as gate  # noqa: E402


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
# evaluate_gate (pure logic)
# ----------------------------------------------------------------------


def test_evaluate_gate_waiting_when_peak_is_none() -> None:
    """No gen-2 row yet → WAITING regardless of threshold."""
    assert gate.evaluate_gate(None, threshold=0.05) == "WAITING"
    assert gate.evaluate_gate(None, threshold=0.5) == "WAITING"


def test_evaluate_gate_pass_when_peak_meets_threshold() -> None:
    """peak >= threshold → PASS."""
    assert gate.evaluate_gate(0.05, threshold=0.05) == "PASS"
    assert gate.evaluate_gate(0.30, threshold=0.05) == "PASS"


def test_evaluate_gate_fail_when_peak_below_threshold() -> None:
    """peak < threshold → FAIL."""
    assert gate.evaluate_gate(0.04, threshold=0.05) == "FAIL"
    assert gate.evaluate_gate(0.0, threshold=0.05) == "FAIL"


def test_evaluate_gate_threshold_boundary_is_inclusive() -> None:
    """Exactly equal to the threshold counts as PASS (>=). Documents the
    inclusion convention so future threshold tuning is unambiguous."""
    assert gate.evaluate_gate(0.05, threshold=0.05) == "PASS"


# ----------------------------------------------------------------------
# read_gen2_peak_ge (DB-backed read)
# ----------------------------------------------------------------------


def _make_db_with_gen_row(gen: int, peak_ge: float) -> Path:
    """Create a temp SQLite DB with a `generations` row matching the
    schema used by tracking/database.py."""
    fd = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    fd.close()
    path = Path(fd.name)
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE generations (
            generation INTEGER PRIMARY KEY,
            population_size INTEGER,
            best_go_essence REAL,
            mean_go_essence REAL,
            median_go_essence REAL,
            std_go_essence REAL,
            best_game_id TEXT,
            score_distribution TEXT
        )
    """)
    conn.execute(
        "INSERT INTO generations (generation, best_go_essence) VALUES (?, ?)",
        (gen, peak_ge),
    )
    conn.commit()
    conn.close()
    return path


def test_read_returns_none_when_db_missing() -> None:
    """Pre-evolution: DB file doesn't exist yet → None (WAITING upstream)."""
    assert gate.read_gen2_peak_ge("/nonexistent/path/missing.db") is None


def test_read_returns_none_when_generations_table_missing() -> None:
    """Fresh DB without the `generations` table → None (run hasn't reached gen 0 end)."""
    fd = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    fd.close()
    try:
        # Empty DB with no tables.
        sqlite3.connect(fd.name).close()
        assert gate.read_gen2_peak_ge(fd.name) is None
    finally:
        Path(fd.name).unlink(missing_ok=True)


def test_read_returns_none_when_gen2_row_missing() -> None:
    """generations table exists with rows 0/1 but no row 2 yet → None."""
    path = _make_db_with_gen_row(gen=1, peak_ge=0.03)
    try:
        assert gate.read_gen2_peak_ge(str(path)) is None
    finally:
        path.unlink(missing_ok=True)


def test_read_returns_peak_when_gen2_row_present() -> None:
    """Gen-2 row inserted → returns its best_go_essence as a float."""
    path = _make_db_with_gen_row(gen=2, peak_ge=0.087)
    try:
        peak = gate.read_gen2_peak_ge(str(path))
        assert peak is not None
        assert abs(peak - 0.087) < 1e-9
    finally:
        path.unlink(missing_ok=True)


def test_read_returns_zero_when_gen2_peak_is_zero() -> None:
    """An honest 0.0 gen-2 peak must read as 0.0, not None (the gate
    needs to FAIL on this, not WAIT forever)."""
    path = _make_db_with_gen_row(gen=2, peak_ge=0.0)
    try:
        peak = gate.read_gen2_peak_ge(str(path))
        assert peak == 0.0
    finally:
        path.unlink(missing_ok=True)


# ----------------------------------------------------------------------
# pid_is_alive
# ----------------------------------------------------------------------


def test_pid_is_alive_for_self_returns_true() -> None:
    """The test process's own pid must report alive."""
    import os
    assert gate.pid_is_alive(os.getpid()) is True


def test_pid_is_alive_returns_false_for_dead_pid() -> None:
    """A short-lived child that has already exited reports dead.
    Use a known-bad pid (a very high number unlikely to be in use)."""
    # Spawn `true` and wait — its pid is now a zombie / reaped.
    proc = subprocess.Popen(["true"])
    proc.wait()
    # On most kernels the pid becomes invalid quickly after wait().
    # We can't deterministically test this without race; instead use a
    # known-impossible pid space (very high).
    assert gate.pid_is_alive(2**30) is False


# ----------------------------------------------------------------------
# Integration: end-to-end fail path with a real subprocess
# ----------------------------------------------------------------------


def test_gate_kills_substrate_on_fail() -> None:
    """Full integration: launch a long-running placeholder process,
    seed a DB with gen-2 peak below threshold, run the gate against
    that PID, verify the placeholder gets SIGTERMed and the gate exits 1."""
    import os
    import time

    # Long-lived placeholder; we'll SIGTERM it via the gate.
    placeholder = subprocess.Popen(
        ["sleep", "60"],
    )
    try:
        path = _make_db_with_gen_row(gen=2, peak_ge=0.01)  # < 0.05 → FAIL
        try:
            gate_proc = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve().parent / "experiments" / "r21_driver" / "gen2_smoke_gate.py"),
                    "--substrate", "test_sub",
                    "--db", str(path),
                    "--pid", str(placeholder.pid),
                    "--threshold", "0.05",
                    "--poll-interval", "1",
                    "--max-wait-hours", "0.01",
                ],
                capture_output=True, text=True, timeout=30,
            )
            assert gate_proc.returncode == 1, (
                f"gate should exit 1 on FAIL, got {gate_proc.returncode}; "
                f"stderr={gate_proc.stderr}"
            )
            # Give the placeholder a moment to react to SIGTERM.
            for _ in range(20):
                if placeholder.poll() is not None:
                    break
                time.sleep(0.1)
            assert placeholder.poll() is not None, (
                "placeholder must be dead after gate SIGTERMs it"
            )
        finally:
            path.unlink(missing_ok=True)
    finally:
        if placeholder.poll() is None:
            placeholder.kill()
            placeholder.wait()


def test_gate_passes_when_peak_meets_threshold() -> None:
    """End-to-end PASS: placeholder survives, gate exits 0."""
    import os
    import time

    placeholder = subprocess.Popen(["sleep", "30"])
    try:
        path = _make_db_with_gen_row(gen=2, peak_ge=0.20)  # >= 0.05 → PASS
        try:
            gate_proc = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve().parent / "experiments" / "r21_driver" / "gen2_smoke_gate.py"),
                    "--substrate", "test_sub",
                    "--db", str(path),
                    "--pid", str(placeholder.pid),
                    "--threshold", "0.05",
                    "--poll-interval", "1",
                    "--max-wait-hours", "0.01",
                ],
                capture_output=True, text=True, timeout=30,
            )
            assert gate_proc.returncode == 0, (
                f"gate should exit 0 on PASS, got {gate_proc.returncode}; "
                f"stderr={gate_proc.stderr}"
            )
            # Placeholder must still be alive.
            assert placeholder.poll() is None, (
                "placeholder must survive when gate PASSes"
            )
        finally:
            path.unlink(missing_ok=True)
    finally:
        if placeholder.poll() is None:
            placeholder.terminate()
            placeholder.wait()


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("Gen-2 smoke gate tests (R21 Z4)")
    print("-" * 50)
    case("evaluate_gate_waiting_when_peak_is_none", test_evaluate_gate_waiting_when_peak_is_none)
    case("evaluate_gate_pass_when_peak_meets_threshold", test_evaluate_gate_pass_when_peak_meets_threshold)
    case("evaluate_gate_fail_when_peak_below_threshold", test_evaluate_gate_fail_when_peak_below_threshold)
    case("evaluate_gate_threshold_boundary_is_inclusive", test_evaluate_gate_threshold_boundary_is_inclusive)
    case("read_returns_none_when_db_missing", test_read_returns_none_when_db_missing)
    case("read_returns_none_when_generations_table_missing", test_read_returns_none_when_generations_table_missing)
    case("read_returns_none_when_gen2_row_missing", test_read_returns_none_when_gen2_row_missing)
    case("read_returns_peak_when_gen2_row_present", test_read_returns_peak_when_gen2_row_present)
    case("read_returns_zero_when_gen2_peak_is_zero", test_read_returns_zero_when_gen2_peak_is_zero)
    case("pid_is_alive_for_self_returns_true", test_pid_is_alive_for_self_returns_true)
    case("pid_is_alive_returns_false_for_dead_pid", test_pid_is_alive_returns_false_for_dead_pid)
    case("gate_kills_substrate_on_fail", test_gate_kills_substrate_on_fail)
    case("gate_passes_when_peak_meets_threshold", test_gate_passes_when_peak_meets_threshold)
    print("-" * 50)
    print(f"{len(passed)} passed, {len(failed)} failed")
    if failed:
        for name, tb in failed:
            print(f"\n--- {name} ---\n{tb}")
        sys.exit(1)
