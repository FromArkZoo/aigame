#!/usr/bin/env python3
"""Tests for the R21 S6 parallel finalization wrapper.

Exercises `build_child_cmd` (the only logic-bearing piece — subprocess
launch is delegated to `subprocess.Popen` which has its own tests
upstream).

Run as: .venv/bin/python test_parallel_finalize.py
"""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path

# parallel_finalize lives in experiments/r21_finalization/; import via path.
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent / "experiments" / "r21_finalization"),
)
import parallel_finalize  # noqa: E402


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
# Tests
# ----------------------------------------------------------------------


def test_build_child_cmd_basic_shape() -> None:
    """Three substrates → three distinct commands with substrate-tagged output paths."""
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        labels = []
        cmds = []
        for spec in (
            "menger:r21_menger.db:9",
            "carpet:r21_carpet.db:5",
            "grid:r21_grid.db:5",
        ):
            label, cmd = parallel_finalize.build_child_cmd(
                spec,
                python="/usr/bin/python",
                reruns=None, budget=None,
                output_dir=out, bypass_validation=False,
            )
            labels.append(label)
            cmds.append(cmd)
        assert labels == ["menger", "carpet", "grid"], (
            f"substrate labels must round-trip: got {labels}"
        )
        # Each cmd's sidecar / csv / summary paths must be substrate-tagged
        # and in the requested output dir.
        for label, cmd in zip(labels, cmds):
            joined = " ".join(cmd)
            assert f"{label}_finalization.db" in joined
            assert f"{label}_per_run.csv" in joined
            assert f"{label}_summary.md" in joined
            assert str(out) in joined


def test_build_child_cmd_forwards_auto_verbatim() -> None:
    """The --auto value is forwarded byte-for-byte (finalize_champions parses it)."""
    with tempfile.TemporaryDirectory() as td:
        spec = "menger:/abs/path/db.db:7"
        _, cmd = parallel_finalize.build_child_cmd(
            spec,
            python="x", reruns=None, budget=None,
            output_dir=Path(td), bypass_validation=False,
        )
        i = cmd.index("--auto")
        assert cmd[i + 1] == spec, f"expected {spec}, got {cmd[i + 1]}"


def test_build_child_cmd_reruns_and_budget_overrides() -> None:
    """--reruns and --budget appear only when overridden."""
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        # Defaults: no --reruns / --budget flags forwarded.
        _, cmd_default = parallel_finalize.build_child_cmd(
            "menger:db:5",
            python="x", reruns=None, budget=None,
            output_dir=out, bypass_validation=False,
        )
        assert "--reruns" not in cmd_default
        assert "--budget" not in cmd_default
        # Overrides: both flags present with the overridden values.
        _, cmd_over = parallel_finalize.build_child_cmd(
            "menger:db:5",
            python="x", reruns=25, budget=8000,
            output_dir=out, bypass_validation=False,
        )
        i_r = cmd_over.index("--reruns")
        assert cmd_over[i_r + 1] == "25"
        i_b = cmd_over.index("--budget")
        assert cmd_over[i_b + 1] == "8000"


def test_build_child_cmd_bypass_validation_flag() -> None:
    """--bypass-validation is a boolean — absent or present, never with a value."""
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        _, cmd_no = parallel_finalize.build_child_cmd(
            "menger:db:5",
            python="x", reruns=None, budget=None,
            output_dir=out, bypass_validation=False,
        )
        assert "--bypass-validation" not in cmd_no
        _, cmd_yes = parallel_finalize.build_child_cmd(
            "menger:db:5",
            python="x", reruns=None, budget=None,
            output_dir=out, bypass_validation=True,
        )
        assert "--bypass-validation" in cmd_yes


def test_build_child_cmd_rejects_malformed_spec() -> None:
    """Specs missing the substrate:db:K shape must raise."""
    with tempfile.TemporaryDirectory() as td:
        try:
            parallel_finalize.build_child_cmd(
                "menger:db",  # missing K
                python="x", reruns=None, budget=None,
                output_dir=Path(td), bypass_validation=False,
            )
            raise AssertionError("expected ValueError for short spec")
        except ValueError:
            pass


def test_finalize_champions_default_reruns_is_20() -> None:
    """R21 S6: bumped default. Loaded via import — must read as 20."""
    sys.path.insert(
        0,
        str(Path(__file__).resolve().parent / "experiments" / "r20_finalization"),
    )
    import finalize_champions  # noqa: E402

    assert finalize_champions.NUM_RERUNS == 20, (
        f"R21 S6 expected NUM_RERUNS=20, got {finalize_champions.NUM_RERUNS}"
    )


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("Parallel finalization wrapper tests (R21 S6)")
    print("-" * 50)
    case("build_child_cmd_basic_shape", test_build_child_cmd_basic_shape)
    case("build_child_cmd_forwards_auto_verbatim", test_build_child_cmd_forwards_auto_verbatim)
    case("build_child_cmd_reruns_and_budget_overrides", test_build_child_cmd_reruns_and_budget_overrides)
    case("build_child_cmd_bypass_validation_flag", test_build_child_cmd_bypass_validation_flag)
    case("build_child_cmd_rejects_malformed_spec", test_build_child_cmd_rejects_malformed_spec)
    case("finalize_champions_default_reruns_is_20", test_finalize_champions_default_reruns_is_20)
    print("-" * 50)
    print(f"{len(passed)} passed, {len(failed)} failed")
    if failed:
        for name, tb in failed:
            print(f"\n--- {name} ---\n{tb}")
        sys.exit(1)
