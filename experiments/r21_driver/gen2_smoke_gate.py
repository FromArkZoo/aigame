#!/usr/bin/env python3
"""R21 Z4 — half-run smoke gate.

R20 ran for 24+ hours before the pie_rule propagation bug surfaced. That
class of regression is cheap to catch early: if a substrate's
end-of-gen-2 peak GE is below a floor (~0.05), something has gone wrong
with either the S1a canonical-blob dedup (rejecting all real diversity),
S5 elite re-eval (mis-seeded RNG), the seed pool (smoke filter missed a
catastrophic family), or the engine itself. Killing the substrate's
process at gen 2 saves the remaining ~12-14 hours of wall-clock per
substrate.

This monitor polls a substrate's SQLite DB and triggers a SIGTERM when
the gate fails. Read-only on the DB; SIGTERM, not SIGKILL, so the
substrate process gets a chance to flush its own shutdown handlers.

Decision logic (pure function `evaluate_gate`):
  - If the `generations` table has no row for generation=2 yet → WAITING.
    Continue polling.
  - If the row exists and `best_go_essence >= threshold` → PASS. Gate
    exits cleanly; substrate keeps running.
  - If the row exists and `best_go_essence < threshold` → FAIL. Send
    SIGTERM to the substrate PID and exit non-zero.

Usage (typically wired from launch_r21.sh — one gate per substrate):

    .venv/bin/python experiments/r21_driver/gen2_smoke_gate.py \\
        --substrate menger --db genesis_v2_run21_menger.db \\
        --pid 12345 --threshold 0.05 --poll-interval 120

Exit codes:
  0  PASS — gate cleared; substrate process kept alive.
  1  FAIL — gate failed; SIGTERM sent.
  2  TIMEOUT — `--max-wait-seconds` reached without gen 2 completing.
"""
from __future__ import annotations

import argparse
import logging
import os
import signal
import sqlite3
import sys
import time
from pathlib import Path

DEFAULT_THRESHOLD = 0.05
DEFAULT_POLL_INTERVAL = 120  # 2 minutes
DEFAULT_MAX_WAIT_HOURS = 24  # safety stop: longest a substrate's gen 0+1+2 should take


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [Z4] %(message)s",
)
logger = logging.getLogger("z4_gate")


# ----------------------------------------------------------------------
# Decision logic (pure — testable without sqlite, files, or signals)
# ----------------------------------------------------------------------

def evaluate_gate(
    gen2_peak_ge: float | None,
    threshold: float,
) -> str:
    """Map a measured gen-2 peak GE to one of WAITING / PASS / FAIL.

    None peak (no gen-2 row yet) → WAITING. Caller polls again.
    peak >= threshold → PASS. The gate exits cleanly.
    peak < threshold → FAIL. The caller should SIGTERM the substrate.
    """
    if gen2_peak_ge is None:
        return "WAITING"
    if gen2_peak_ge >= threshold:
        return "PASS"
    return "FAIL"


def read_gen2_peak_ge(db_path: str) -> float | None:
    """Return the `best_go_essence` for generation=2, or None if the
    `generations` row hasn't been inserted yet. Returns None on missing
    DB / table too (the run hasn't started writing yet)."""
    if not Path(db_path).exists():
        return None
    try:
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.execute(
                "SELECT best_go_essence FROM generations WHERE generation = ?",
                (2,),
            )
            row = cur.fetchone()
            return None if row is None else float(row[0])
        finally:
            conn.close()
    except sqlite3.OperationalError:
        # Table may not exist yet on a freshly-created DB.
        return None


# ----------------------------------------------------------------------
# Process control
# ----------------------------------------------------------------------

def send_sigterm(pid: int) -> None:
    """Send SIGTERM to `pid`. Raises ProcessLookupError if pid is gone."""
    os.kill(pid, signal.SIGTERM)


def pid_is_alive(pid: int) -> bool:
    """Cheap liveness check via kill(0)."""
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--substrate", required=True,
                   help="Label for log lines (menger/carpet/grid).")
    p.add_argument("--db", required=True, type=Path,
                   help="Path to the substrate's SQLite DB.")
    p.add_argument("--pid", required=True, type=int,
                   help="Substrate process PID to SIGTERM on FAIL.")
    p.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                   help=f"GE floor at gen 2 (default {DEFAULT_THRESHOLD}).")
    p.add_argument("--poll-interval", type=int, default=DEFAULT_POLL_INTERVAL,
                   help=f"Seconds between DB polls (default {DEFAULT_POLL_INTERVAL}).")
    p.add_argument(
        "--max-wait-hours", type=float, default=DEFAULT_MAX_WAIT_HOURS,
        help=f"Give up after this many hours (default {DEFAULT_MAX_WAIT_HOURS}).",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    sub = args.substrate
    db_path = str(args.db)
    pid = args.pid
    threshold = args.threshold
    poll = args.poll_interval
    deadline = time.time() + args.max_wait_hours * 3600

    logger.info(
        "[%s] gate started: db=%s pid=%d threshold=%.3f poll=%ds",
        sub, db_path, pid, threshold, poll,
    )

    while True:
        if not pid_is_alive(pid):
            # Substrate finished or died on its own — nothing to gate.
            logger.info(
                "[%s] substrate pid=%d no longer alive; gate exits cleanly", sub, pid,
            )
            return 0

        peak = read_gen2_peak_ge(db_path)
        decision = evaluate_gate(peak, threshold)

        if decision == "PASS":
            logger.info(
                "[%s] gate PASS — gen-2 peak GE %.4f >= %.3f. Exiting cleanly.",
                sub, peak, threshold,
            )
            return 0
        if decision == "FAIL":
            logger.warning(
                "[%s] gate FAIL — gen-2 peak GE %.4f < %.3f. Sending SIGTERM to pid=%d.",
                sub, peak, threshold, pid,
            )
            try:
                send_sigterm(pid)
            except ProcessLookupError:
                logger.warning("[%s] pid=%d already gone before SIGTERM", sub, pid)
            return 1
        # WAITING
        if time.time() > deadline:
            logger.warning(
                "[%s] gate TIMEOUT — gen 2 didn't complete in %.1f hours. "
                "Leaving substrate alive; exit code 2.",
                sub, args.max_wait_hours,
            )
            return 2
        logger.info("[%s] gate waiting — gen 2 not yet complete; sleeping %ds", sub, poll)
        time.sleep(poll)


if __name__ == "__main__":
    sys.exit(main())
