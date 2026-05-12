#!/bin/bash
# launch_r21.sh — kick off all 3 R21 per-substrate evolutions in parallel.
#
# Each substrate runs in its own Python process. OMP_NUM_THREADS=1 keeps
# PyTorch single-threaded per process so the 3 processes can use distinct
# cores instead of thrashing.
#
# Per-substrate defaults (overridable via env vars):
#   menger  pop=15 gens=4 budget=10000   (~15 hr — bottleneck)
#   carpet  pop=15 gens=5 budget=15000   (~13 hr)
#   grid    pop=15 gens=5 budget=10000   (~3 hr)
#
# Smoke filter: by convention the smoke filter has already been run before
# this script — see experiments/r18_ppo_smoke/run_smoke.py and pass the
# survivors via SMOKE_PASSED env (one path per substrate, glob if needed).
# Without it, the driver loads all pre-smoke seeds (36 menger candidates
# inflates gen-0 compute by ~2-3x; carpet and grid are unaffected).
#
# Carry-over (optional): if experiments/r21_seeds/carryover/<sub>.json
# exists, it's injected as an additional gen-0 seed. The intended R21
# carry-over is the R20 carpet anchor `625bfc1f3f49` (only above-R19
# result, 4.70). Dump it from R20 carpet DB before launch.
#
# Usage:
#     ./experiments/r21_driver/launch_r21.sh                            # full R21
#     GENS=1 POP=5 BUDGET=200 SUBSTRATES=carpet \
#         ./experiments/r21_driver/launch_r21.sh                        # mini-evolution
#     DB_SUFFIX=_validation ./experiments/r21_driver/launch_r21.sh      # test run
#     MAX_SEEDS=15 ./experiments/r21_driver/launch_r21.sh               # cap pre-smoke menger

set -e
cd "$(dirname "$0")/../.."

GENS=${GENS:-}
POP=${POP:-}
BUDGET=${BUDGET:-}
DB_SUFFIX=${DB_SUFFIX:-}
MAX_SEEDS=${MAX_SEEDS:-}
# Z4 half-run smoke gate. Set GATE=0 to disable (e.g., on mini-runs that
# don't actually reach gen 2). GATE_THRESHOLD overrides the GE floor.
GATE=${GATE:-1}
GATE_THRESHOLD=${GATE_THRESHOLD:-0.05}
GATE_POLL=${GATE_POLL:-120}

SUBSTRATES_STR=${SUBSTRATES:-"menger carpet grid"}
read -ra SUBSTRATES <<< "$SUBSTRATES_STR"

CARRYOVER_DIR="experiments/r21_seeds/carryover"
SMOKE_PASSED_DIR="experiments/r21_seeds/smoke_passed"

mkdir -p logs/run21

echo "=== R21 launch ==="
echo "  substrates=${SUBSTRATES[*]}"
echo "  per-substrate defaults from driver SUBSTRATE_CONFIG"
[[ -n "$GENS" ]]       && echo "  GENS override     = $GENS"
[[ -n "$POP" ]]        && echo "  POP override      = $POP"
[[ -n "$BUDGET" ]]     && echo "  BUDGET override   = $BUDGET"
[[ -n "$MAX_SEEDS" ]]  && echo "  MAX_SEEDS         = $MAX_SEEDS"
[[ -n "$DB_SUFFIX" ]]  && echo "  db_suffix='${DB_SUFFIX}'"
echo "  logs: logs/run21/<substrate>.log"
echo

PIDS=()
GATE_PIDS=()
for sub in "${SUBSTRATES[@]}"; do
    log="logs/run21/${sub}${DB_SUFFIX}.log"

    cmd=(env OMP_NUM_THREADS=1 .venv/bin/python
         experiments/r21_driver/run_r21_substrate.py
         --substrate "$sub")

    [[ -n "$GENS" ]]       && cmd+=(--generations "$GENS")
    [[ -n "$POP" ]]        && cmd+=(--population "$POP")
    [[ -n "$BUDGET" ]]     && cmd+=(--training-budget "$BUDGET")
    [[ -n "$DB_SUFFIX" ]]  && cmd+=(--db-suffix "$DB_SUFFIX")
    [[ -n "$MAX_SEEDS" ]]  && cmd+=(--max-seeds "$MAX_SEEDS")

    smoke="${SMOKE_PASSED_DIR}/${sub}.json"
    if [[ -f "$smoke" ]]; then
        cmd+=(--smoke-passed-json "$smoke")
        echo "  $sub  smoke-passed=$smoke"
    fi

    carry="${CARRYOVER_DIR}/${sub}.json"
    if [[ -f "$carry" ]]; then
        cmd+=(--carryover-json "$carry")
        echo "  $sub  carry-over=$carry"
    fi

    "${cmd[@]}" > "$log" 2>&1 &
    pid=$!
    PIDS+=("$pid")
    echo "  $sub  pid=$pid  log=$log"

    # Z4: spawn half-run smoke gate alongside the substrate. Exits 0 on
    # PASS, sends SIGTERM to the substrate's pid on FAIL. DB path
    # matches run_r21_substrate.py's output convention.
    if [[ "$GATE" != "0" ]]; then
        gate_log="logs/run21/${sub}${DB_SUFFIX}_gate.log"
        db_path="genesis_v2_run21_${sub}${DB_SUFFIX}.db"
        env .venv/bin/python experiments/r21_driver/gen2_smoke_gate.py \
            --substrate "$sub" --db "$db_path" --pid "$pid" \
            --threshold "$GATE_THRESHOLD" --poll-interval "$GATE_POLL" \
            > "$gate_log" 2>&1 &
        gate_pid=$!
        GATE_PIDS+=("$gate_pid")
        echo "  $sub  gate-pid=$gate_pid  gate-log=$gate_log  threshold=$GATE_THRESHOLD"
    fi
done

echo
echo "All ${#SUBSTRATES[@]} processes started. PIDs: ${PIDS[*]}"
[[ "$GATE" != "0" ]] && echo "Gate PIDs: ${GATE_PIDS[*]}"
echo "Check progress: tail -f logs/run21/*.log"
echo "Wait for all:   wait ${PIDS[*]}"
