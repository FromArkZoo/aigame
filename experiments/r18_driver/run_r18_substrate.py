#!/usr/bin/env python3
"""R18 driver — runs the evolution for ONE substrate.

R18 is "5 INDEPENDENT per-substrate evolutions" (Plan A, hexaflake dropped).
Each substrate gets its own DB, its own surviving seed set (filtered by B2
Phase 2), and its own audit_soft_rules flag (carpet only, so threshold-race
mutations don't get demoted by R17's sierpinski_threshold_inert rule).

Invoke once per substrate, in parallel with one process each:

    OMP_NUM_THREADS=1 .venv/bin/python experiments/r18_driver/run_r18_substrate.py \\
        --substrate vicsek

The launch_r18.sh wrapper kicks off all 5 in parallel for the overnight run.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Make repo importable when run directly.
_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from config import GenesisConfig  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from run import run_pipeline  # noqa: E402


# ----------------------------------------------------------------------
# Per-substrate config — derived from B2 Phase 2 verdicts in
# experiments/r18_seeds/SMOKE_RESULTS.md
# ----------------------------------------------------------------------

# Each entry — surviving seeds (relative to experiments/r18_seeds/seeds/),
# the engine topology_type string, the substrate's required dimensions,
# and whether to run with audit_soft_rules.
SUBSTRATE_CONFIG: dict[str, dict] = {
    "vicsek": {
        "topology_type": "vicsek",
        "dims": 2,
        "seeds": [
            "c1_custodian_connection__vicsek",
            "c3_surround_territory__vicsek",
        ],
        "audit_soft_rules": False,
    },
    "triangle": {
        "topology_type": "sierpinski_triangle",
        "dims": 2,
        "seeds": [
            "c1_custodian_connection__triangle",
            "c3_surround_territory__triangle",
        ],
        "audit_soft_rules": False,
    },
    "carpet": {
        "topology_type": "sierpinski",
        "dims": 2,
        "seeds": [
            "c1_custodian_connection__carpet",
        ],
        # Soft-rule audit on so threshold-race mutations don't auto-demote
        # to connection — gives carpet evolution a wider exploration cone
        # despite starting from only one seed (R17 sierpinski_threshold_inert).
        "audit_soft_rules": True,
    },
    "grid": {
        "topology_type": "grid",
        "dims": 2,
        "seeds": [
            "c2_outnumber_threshold__grid",
            "c3_surround_territory__grid",
        ],
        "audit_soft_rules": False,
    },
    "menger": {
        "topology_type": "menger",
        "dims": 3,
        "seeds": [
            "c1_custodian_connection__menger",
            "c3_surround_territory__menger",
        ],
        "audit_soft_rules": False,
    },
}


SEEDS_DIR = _REPO / "experiments" / "r18_seeds" / "seeds"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--substrate", required=True,
        choices=sorted(SUBSTRATE_CONFIG.keys()),
        help="Which substrate to evolve.",
    )
    p.add_argument("--generations", type=int, default=7,
                   help="R18 default 7 (set lower for validation runs).")
    p.add_argument("--population", type=int, default=30,
                   help="R18 default 30.")
    p.add_argument("--training-budget", type=int, default=5000,
                   help="Episodes per game; R18 default 5000.")
    p.add_argument("--seed", type=int, default=42,
                   help="Global RNG seed.")
    p.add_argument("--db-suffix", type=str, default="",
                   help="Append to db filename, e.g. '_validation' so test "
                        "runs don't collide with the real R18 db.")
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

    # Build config
    config = GenesisConfig()
    config.evolution.num_generations = args.generations
    config.evolution.population_size = args.population
    config.training.training_budget = args.training_budget
    config.seed = args.seed

    # Restrict to a single substrate. SUBSTRATE_INVARIANTS in topology.py
    # will force axis_size + dims at construction time — but pinning min/max
    # dimensions matches what the substrate actually uses, so the random-
    # generation path doesn't waste rolls on dims that get overridden anyway.
    config.game.topology_types = [sub_cfg["topology_type"]]
    config.game.min_dimensions = sub_cfg["dims"]
    config.game.max_dimensions = sub_cfg["dims"]

    db_path = f"genesis_v2_run18_{args.substrate}{args.db_suffix}.db"
    config.tracking.db_path = db_path

    # Load surviving seeds
    seed_games = []
    for sid in sub_cfg["seeds"]:
        path = SEEDS_DIR / f"{sid}.json"
        with open(path) as f:
            seed_games.append(GameDefV2.from_dict(json.load(f)))
        logger.info("Loaded seed: %s", sid)

    logger.info(
        "R18 %s — topo=%s dims=%d seeds=%d audit_soft_rules=%s "
        "(gens=%d pop=%d budget=%d)",
        args.substrate, sub_cfg["topology_type"], sub_cfg["dims"],
        len(seed_games), sub_cfg["audit_soft_rules"],
        args.generations, args.population, args.training_budget,
    )
    logger.info("Output DB: %s", db_path)

    run_pipeline(
        config,
        use_v2=True,
        resume=args.resume,
        seed_games=seed_games,
        audit_soft_rules=sub_cfg["audit_soft_rules"],
    )
    logger.info("R18 %s — DONE", args.substrate)
    return 0


if __name__ == "__main__":
    sys.exit(main())
