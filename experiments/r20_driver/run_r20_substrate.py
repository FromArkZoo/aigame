#!/usr/bin/env python3
"""R20 driver — runs the evolution for ONE substrate.

R20 is a rule-family-comparator round (custodian/surround/outnumber +
connection). Each substrate runs its own evolution; per-substrate config
below carries the population, generations, and training budget per
R20_plan.md § Run config.

Per-substrate config:
    menger        pop=30 gens=8 budget=10000  (~30hr wall-clock)
    carpet        pop=30 gens=8 budget=15000  (~25hr; carpet trains faster)
    grid_control  pop=20 gens=4 budget=10000  (~3hr — methodology check,
                                               more gens than R19's 2)

Invoke once per substrate:

    OMP_NUM_THREADS=1 .venv/bin/python experiments/r20_driver/run_r20_substrate.py \\
        --substrate menger

The launch_r20.sh wrapper kicks off all three in parallel.

R20 stack:
- pie_rule=True on every seed (R19 30/30 verdicts unanimous)
- D1 hybrid penalty (already in scoring stack)
- C1 deterministic seeds, C2 multi-seed averaging (already in run.py)
- Two-tier smoke (run BEFORE this driver — see r20_smoke_two_tier/)
- Champion finalization (run AFTER this driver — see r20_finalization/)

The "seeds" lists below are populated AFTER two-tier smoke completes; the
PRE-SMOKE seed list is all 12 (4 families × 3 substrates from
experiments/r20_seeds/seeds/). G1 success criterion requires F1
(custodian-1 + connection) on grid_control to clear human 6.0 — keep F1
in grid_control regardless of smoke verdict.

Carry-over (optional, gated on a flag): R20 carry-overs are R19 top-1s
re-evaluated under the R20 stack (see Z3 / R20_plan.md § carry-over
re-evaluation). Pass via --carryover-json PATH.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from config import GenesisConfig  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from run import run_pipeline  # noqa: E402


# ----------------------------------------------------------------------
# Per-substrate config
# ----------------------------------------------------------------------

# Seeds lists below default to ALL 4 families per substrate (pre-smoke).
# After two-tier smoke runs, prune to PASS-only EXCEPT keep F1 on
# grid_control regardless (G1 methodology check is load-bearing).
SUBSTRATE_CONFIG: dict[str, dict] = {
    "menger": {
        "topology_type": "menger",
        "dims": 3,
        "seeds": [
            "F1_custodian1_conn__menger",
            "F2_custodian2_conn__menger",
            "F3_surround_conn__menger",
            "F4_outnumber2_conn__menger",
        ],
        "default_generations": 8,
        "default_population": 30,
        "default_training_budget": 10000,
        "audit_soft_rules": False,
    },
    "carpet": {
        "topology_type": "sierpinski",
        "dims": 2,
        "seeds": [
            "F1_custodian1_conn__carpet",
            "F2_custodian2_conn__carpet",
            "F3_surround_conn__carpet",
            "F4_outnumber2_conn__carpet",
        ],
        "default_generations": 8,
        "default_population": 30,
        "default_training_budget": 15000,
        # R20 carpet uses connection win across all 4 families — no
        # threshold-race / inert-rule audit issue. Keep audit OFF unless
        # post-smoke evidence says otherwise.
        "audit_soft_rules": False,
    },
    "grid_control": {
        "topology_type": "grid",
        "dims": 2,
        "seeds": [
            # F1 is the G1 methodology check — keep regardless of smoke verdict.
            "F1_custodian1_conn__grid_control",
            "F2_custodian2_conn__grid_control",
            "F3_surround_conn__grid_control",
            "F4_outnumber2_conn__grid_control",
        ],
        "default_generations": 4,
        "default_population": 20,
        "default_training_budget": 10000,
        "audit_soft_rules": False,
    },
}


SEEDS_DIR = _REPO / "experiments" / "r20_seeds" / "seeds"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--substrate", required=True,
        choices=sorted(SUBSTRATE_CONFIG.keys()),
        help="Which substrate to evolve.",
    )
    p.add_argument("--generations", type=int, default=None,
                   help="Override per-substrate default.")
    p.add_argument("--population", type=int, default=None,
                   help="Override per-substrate default.")
    p.add_argument("--training-budget", type=int, default=None,
                   help="Override per-substrate default.")
    p.add_argument("--seed", type=int, default=42,
                   help="Global RNG seed.")
    p.add_argument("--db-suffix", type=str, default="",
                   help="Append to db filename, e.g. '_validation'.")
    p.add_argument(
        "--carryover-json", type=Path, default=None,
        help="GameDefV2 JSON to inject as an extra gen-0 seed (R19 top-1 "
             "re-evaluated under R20 stack — see Z3).",
    )
    p.add_argument("--resume", action="store_true",
                   help="Resume from the substrate's checkpoint if present.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    sub_cfg = SUBSTRATE_CONFIG[args.substrate]

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger(__name__)

    gens = args.generations if args.generations is not None else sub_cfg["default_generations"]
    pop = args.population if args.population is not None else sub_cfg["default_population"]
    budget = args.training_budget if args.training_budget is not None else sub_cfg["default_training_budget"]

    config = GenesisConfig()
    config.evolution.num_generations = gens
    config.evolution.population_size = pop
    config.training.training_budget = budget
    config.seed = args.seed

    config.game.topology_types = [sub_cfg["topology_type"]]
    config.game.min_dimensions = sub_cfg["dims"]
    config.game.max_dimensions = sub_cfg["dims"]

    db_path = f"genesis_v2_run20_{args.substrate}{args.db_suffix}.db"
    config.tracking.db_path = db_path

    seed_games: list[GameDefV2] = []
    for sid in sub_cfg["seeds"]:
        path = SEEDS_DIR / f"{sid}.json"
        with open(path) as f:
            seed_games.append(GameDefV2.from_dict(json.load(f)))
        logger.info("Loaded seed: %s", sid)

    if args.carryover_json is not None:
        with open(args.carryover_json) as f:
            carry = GameDefV2.from_dict(json.load(f))
        seed_games.append(carry)
        logger.info(
            "Loaded CARRY-OVER seed: %s (from %s)",
            carry.game_id, args.carryover_json,
        )

    # Pie rule sanity: every R20 seed should have pie_rule=True. Carry-overs
    # may not — if a carry-over predates S1, we still load it but log a
    # warning so the eval-time pie_rule bookkeeping is honest.
    for g in seed_games:
        if not g.pie_rule:
            logger.warning(
                "seed %s has pie_rule=False — R20 mandates pie_rule=True; "
                "this seed will play without pie balance",
                g.game_id,
            )

    logger.info(
        "R20 %s — topo=%s dims=%d seeds=%d audit_soft_rules=%s "
        "(gens=%d pop=%d budget=%d)",
        args.substrate, sub_cfg["topology_type"], sub_cfg["dims"],
        len(seed_games), sub_cfg["audit_soft_rules"],
        gens, pop, budget,
    )
    logger.info("Output DB: %s", db_path)

    run_pipeline(
        config,
        use_v2=True,
        resume=args.resume,
        seed_games=seed_games,
        audit_soft_rules=sub_cfg["audit_soft_rules"],
    )
    logger.info("R20 %s — DONE", args.substrate)
    return 0


if __name__ == "__main__":
    sys.exit(main())
