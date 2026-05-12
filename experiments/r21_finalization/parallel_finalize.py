"""R21 S6 — parallel champion-finalization wrapper.

Launches `experiments/r20_finalization/finalize_champions.py` as one
subprocess per substrate, in parallel. Each substrate's reruns are
serialized within its own process; the wall-clock saving comes from
overlapping the 3 substrates.

The plan target for R21 (NUM_RERUNS=20 × 9 games at ~9 min/rerun):
- ~27 hr serial across all 3 substrates
- ~9 hr wall under 3-way parallel

Each substrate gets its own sidecar DB, per-run CSV, and markdown
summary in this directory so the runs don't trample each other's
outputs.

Usage:
    .venv/bin/python experiments/r21_finalization/parallel_finalize.py \\
        --auto menger:genesis_v2_run21_menger.db:9 \\
        --auto carpet:genesis_v2_run21_carpet.db:5 \\
        --auto grid:genesis_v2_run21_grid.db:5 \\
        --bypass-validation

Each --auto value is forwarded verbatim to finalize_champions.py.
Combined log lines are tagged with [<substrate>] so concurrent output
is readable.
"""

from __future__ import annotations

import argparse
import logging
import shlex
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FINALIZE = ROOT / "experiments" / "r20_finalization" / "finalize_champions.py"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("r21_parallel_finalize")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--auto", action="append", default=[],
        help=(
            "Forwarded to finalize_champions.py --auto. Format: "
            "<substrate>:<db_path>:<K>. Repeat once per substrate."
        ),
    )
    p.add_argument(
        "--reruns", type=int, default=None,
        help="Override NUM_RERUNS in the child finalize_champions.py. "
             "Defaults to the child's own default (20 for R21).",
    )
    p.add_argument(
        "--budget", type=int, default=None,
        help="Per-PPO training budget override (forwards to --budget).",
    )
    p.add_argument(
        "--output-dir", type=Path, default=HERE,
        help=f"Per-substrate sidecar DBs / CSVs / MDs land here (default: {HERE}).",
    )
    p.add_argument(
        "--bypass-validation", action="store_true",
        help="Pass --bypass-validation to each child invocation.",
    )
    p.add_argument(
        "--max-workers", type=int, default=3,
        help="Maximum concurrent finalization processes (default 3 — one per substrate).",
    )
    p.add_argument(
        "--python", default=str(ROOT / ".venv" / "bin" / "python"),
        help="Python interpreter for child processes.",
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Print the child commands and exit without launching.",
    )
    return p.parse_args()


def build_child_cmd(
    auto_spec: str,
    *,
    python: str,
    reruns: int | None,
    budget: int | None,
    output_dir: Path,
    bypass_validation: bool,
) -> tuple[str, list[str]]:
    """Return (substrate_label, argv) for one finalize_champions.py invocation."""
    parts = auto_spec.split(":")
    if len(parts) < 3:
        raise ValueError(f"--auto spec must be substrate:db:K, got {auto_spec!r}")
    substrate = parts[0]
    output_dir.mkdir(parents=True, exist_ok=True)
    sidecar = output_dir / f"{substrate}_finalization.db"
    csv = output_dir / f"{substrate}_per_run.csv"
    summary = output_dir / f"{substrate}_summary.md"
    cmd = [
        python, str(FINALIZE),
        "--auto", auto_spec,
        "--sidecar-db", str(sidecar),
        "--results-csv", str(csv),
        "--summary-md", str(summary),
    ]
    if reruns is not None:
        cmd += ["--reruns", str(reruns)]
    if budget is not None:
        cmd += ["--budget", str(budget)]
    if bypass_validation:
        cmd += ["--bypass-validation"]
    return substrate, cmd


def stream_with_prefix(stream, prefix: str, sink) -> None:
    """Read lines from `stream`, prefix them with `[<substrate>]`, write to `sink`."""
    for raw in iter(stream.readline, ""):
        line = raw.rstrip()
        sink.write(f"[{prefix}] {line}\n")
        sink.flush()
    stream.close()


def run_one(label: str, cmd: list[str]) -> int:
    logger.info("[%s] launching: %s", label, " ".join(shlex.quote(c) for c in cmd))
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    out_thread = threading.Thread(
        target=stream_with_prefix, args=(proc.stdout, label, sys.stdout),
        daemon=True,
    )
    out_thread.start()
    rc = proc.wait()
    out_thread.join(timeout=2.0)
    return rc


def main() -> int:
    args = parse_args()
    if not args.auto:
        logger.error("at least one --auto spec is required")
        return 2

    # Build all child commands first so we can validate before launching.
    children = []
    for spec in args.auto:
        label, cmd = build_child_cmd(
            spec,
            python=args.python,
            reruns=args.reruns,
            budget=args.budget,
            output_dir=args.output_dir,
            bypass_validation=args.bypass_validation,
        )
        children.append((label, cmd))

    if args.dry_run:
        for label, cmd in children:
            print(f"[{label}] {' '.join(shlex.quote(c) for c in cmd)}")
        return 0

    if len(children) > args.max_workers:
        logger.warning(
            "%d substrates exceed max_workers=%d — extra substrates will queue",
            len(children), args.max_workers,
        )

    start = time.time()
    results: dict[str, int] = {}

    # Bounded parallelism via thread pool; each thread owns one subprocess.
    from concurrent.futures import ThreadPoolExecutor, as_completed
    with ThreadPoolExecutor(max_workers=args.max_workers) as ex:
        futures = {ex.submit(run_one, label, cmd): label for label, cmd in children}
        for fut in as_completed(futures):
            label = futures[fut]
            try:
                rc = fut.result()
            except Exception as e:  # noqa: BLE001
                logger.error("[%s] crashed: %s", label, e)
                results[label] = 1
                continue
            results[label] = rc
            logger.info("[%s] finished with exit code %d", label, rc)

    elapsed = time.time() - start
    logger.info("All substrates done in %.1f min wall.", elapsed / 60.0)
    for label, rc in sorted(results.items()):
        logger.info("  %s: exit %d", label, rc)
    return 0 if all(rc == 0 for rc in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
