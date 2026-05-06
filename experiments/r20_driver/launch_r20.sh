#!/bin/bash
# launch_r20.sh — kick off all 3 R20 per-substrate evolutions in parallel.
#
# Each substrate runs in its own Python process. OMP_NUM_THREADS=1 keeps
# PyTorch single-threaded per process so the 3 processes can use distinct
# cores instead of thrashing.
#
# Per-substrate defaults (overridable via env vars):
#   menger        gens=8 pop=30 budget=10000   (~30hr — bottleneck)
#   carpet        gens=8 pop=30 budget=15000   (~25hr)
#   grid_control  gens=4 pop=20 budget=10000   (~3hr — methodology check;
#                                               R20 G1 success criterion)
#
# Carry-over (optional): if experiments/r20_seeds/carryover/<sub>.json
# exists, it's injected as an additional gen-0 seed (R19 top-1 re-evaluated
# under R20 stack per Z3). Skipped silently if file not present.
#
# Usage:
#     ./experiments/r20_driver/launch_r20.sh                         # full R20
#     GENS=1 POP=5 BUDGET=200 SUBSTRATES=carpet \
#         ./experiments/r20_driver/launch_r20.sh                     # mini-evolution
#     DB_SUFFIX=_validation ./experiments/r20_driver/launch_r20.sh   # test run

set -e
cd "$(dirname "$0")/../.."

GENS=${GENS:-}
POP=${POP:-}
BUDGET=${BUDGET:-}
DB_SUFFIX=${DB_SUFFIX:-}

SUBSTRATES_STR=${SUBSTRATES:-"menger carpet grid_control"}
read -ra SUBSTRATES <<< "$SUBSTRATES_STR"

CARRYOVER_DIR="experiments/r20_seeds/carryover"

mkdir -p logs/run20

echo "=== R20 launch ==="
echo "  substrates=${SUBSTRATES[*]}"
echo "  per-substrate defaults from driver SUBSTRATE_CONFIG"
[[ -n "$GENS" ]]      && echo "  GENS override   = $GENS"
[[ -n "$POP" ]]       && echo "  POP override    = $POP"
[[ -n "$BUDGET" ]]    && echo "  BUDGET override = $BUDGET"
[[ -n "$DB_SUFFIX" ]] && echo "  db_suffix='${DB_SUFFIX}'"
echo "  logs: logs/run20/<substrate>.log"
echo

PIDS=()
for sub in "${SUBSTRATES[@]}"; do
    log="logs/run20/${sub}${DB_SUFFIX}.log"

    cmd=(env OMP_NUM_THREADS=1 .venv/bin/python
         experiments/r20_driver/run_r20_substrate.py
         --substrate "$sub")

    [[ -n "$GENS" ]]      && cmd+=(--generations "$GENS")
    [[ -n "$POP" ]]       && cmd+=(--population "$POP")
    [[ -n "$BUDGET" ]]    && cmd+=(--training-budget "$BUDGET")
    [[ -n "$DB_SUFFIX" ]] && cmd+=(--db-suffix "$DB_SUFFIX")

    carry="${CARRYOVER_DIR}/${sub}.json"
    if [[ -f "$carry" ]]; then
        cmd+=(--carryover-json "$carry")
        echo "  $sub  carry-over=$carry"
    fi

    "${cmd[@]}" > "$log" 2>&1 &
    pid=$!
    PIDS+=("$pid")
    echo "  $sub  pid=$pid  log=$log"
done

echo
echo "All ${#SUBSTRATES[@]} processes started. PIDs: ${PIDS[*]}"
echo "Check progress: tail -f logs/run20/*.log"
echo "Wait for all:   wait ${PIDS[*]}"
