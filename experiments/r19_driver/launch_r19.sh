#!/bin/bash
# launch_r19.sh — kick off all 3 R19 per-substrate evolutions in parallel.
#
# Each substrate runs in its own Python process. OMP_NUM_THREADS=1 keeps
# PyTorch single-threaded per process so the 3 processes can use distinct
# cores instead of thrashing.
#
# Per-substrate defaults (overridable via env vars):
#   menger        gens=8 pop=30 budget=10000   (~30hr — bottleneck)
#   carpet        gens=8 pop=30 budget=15000   (~4.5hr — free bump)
#   grid_control  gens=2 pop=20 budget=10000   (~30 min — noise floor)
#
# Carry-over (optional): if experiments/r19_seeds/carryover/<sub>.json
# exists, it's injected as an additional gen-0 seed (R19 plan v3 elite
# carry-over). Skipped silently if file not present (e.g. for the
# pre-launch mini-evolution).
#
# Usage:
#     ./experiments/r19_driver/launch_r19.sh                         # full R19
#     GENS=1 POP=5 BUDGET=200 SUBSTRATES=carpet \
#         ./experiments/r19_driver/launch_r19.sh                     # mini-evolution
#     DB_SUFFIX=_validation ./experiments/r19_driver/launch_r19.sh   # test run

set -e
cd "$(dirname "$0")/../.."

# Per-substrate budgets carried by the driver's defaults.
# Allow blanket overrides for validation runs.
GENS=${GENS:-}
POP=${POP:-}
BUDGET=${BUDGET:-}
DB_SUFFIX=${DB_SUFFIX:-}

# Default substrate set; overridable for mini-evolution.
SUBSTRATES_STR=${SUBSTRATES:-"menger carpet grid_control"}
read -ra SUBSTRATES <<< "$SUBSTRATES_STR"

CARRYOVER_DIR="experiments/r19_seeds/carryover"

mkdir -p logs/run19

echo "=== R19 launch ==="
echo "  substrates=${SUBSTRATES[*]}"
echo "  per-substrate defaults from driver SUBSTRATE_CONFIG"
[[ -n "$GENS" ]]   && echo "  GENS override   = $GENS"
[[ -n "$POP" ]]    && echo "  POP override    = $POP"
[[ -n "$BUDGET" ]] && echo "  BUDGET override = $BUDGET"
[[ -n "$DB_SUFFIX" ]] && echo "  db_suffix='${DB_SUFFIX}'"
echo "  logs: logs/run19/<substrate>.log"
echo

PIDS=()
for sub in "${SUBSTRATES[@]}"; do
    log="logs/run19/${sub}${DB_SUFFIX}.log"

    cmd=(env OMP_NUM_THREADS=1 .venv/bin/python
         experiments/r19_driver/run_r19_substrate.py
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
echo "Check progress: tail -f logs/run19/*.log"
echo "Wait for all:   wait ${PIDS[*]}"
