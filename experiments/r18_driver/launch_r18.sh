#!/bin/bash
# launch_r18.sh — kick off all 5 R18 per-substrate evolutions in parallel.
#
# Each substrate runs in its own Python process. OMP_NUM_THREADS=1 keeps
# PyTorch single-threaded per process so the 5 processes can use distinct
# cores instead of thrashing.
#
# Usage:
#     ./experiments/r18_driver/launch_r18.sh                  # full R18 run
#     GENS=1 POP=5 BUDGET=200 ./experiments/r18_driver/launch_r18.sh   # tiny validation
#
# The script writes per-substrate logs to logs/run18/<sub>.log and exits
# immediately; processes continue in background. Track:
#     tail -f logs/run18/*.log
#     jobs -l       # list still-running PIDs (in same shell)
#     ps aux | grep run_r18_substrate     # cross-shell

set -e
cd "$(dirname "$0")/../.."

GENS=${GENS:-7}
POP=${POP:-30}
BUDGET=${BUDGET:-5000}
DB_SUFFIX=${DB_SUFFIX:-}

mkdir -p logs/run18

SUBSTRATES=(vicsek triangle carpet grid menger)

echo "=== R18 launch ==="
echo "  generations=$GENS  population=$POP  training_budget=$BUDGET"
echo "  db_suffix='${DB_SUFFIX}'"
echo "  logs: logs/run18/<substrate>.log"
echo

PIDS=()
for sub in "${SUBSTRATES[@]}"; do
    log="logs/run18/${sub}${DB_SUFFIX}.log"
    OMP_NUM_THREADS=1 .venv/bin/python experiments/r18_driver/run_r18_substrate.py \
        --substrate "$sub" \
        --generations "$GENS" \
        --population "$POP" \
        --training-budget "$BUDGET" \
        --db-suffix "$DB_SUFFIX" \
        > "$log" 2>&1 &
    pid=$!
    PIDS+=("$pid")
    echo "  $sub  pid=$pid  log=$log"
done

echo
echo "All 5 processes started. PIDs: ${PIDS[*]}"
echo "Check progress: tail -f logs/run18/*.log"
echo "Wait for all: wait ${PIDS[*]}"
