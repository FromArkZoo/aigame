#!/usr/bin/env python3
"""R19 driver — runs the evolution for ONE substrate.

R19 narrows R18's 5-substrate comparator to a 2-substrate champion run
(menger axis-9 + carpet axis-9) plus a tiny grid control. C1+C2+D1 are
live in the scoring path; this driver is the first end-to-end test that
they integrate cleanly under live evolution.

Per-substrate config:
    menger        pop=30 gens=8 budget=10000  (~30hr wall-clock)
    carpet        pop=30 gens=8 budget=15000  (~4.5hr; free quality bump)
    grid_control  pop=20 gens=2 budget=10000  (~30 min; noise-floor only)

Invoke once per substrate:

    OMP_NUM_THREADS=1 .venv/bin/python experiments/r19_driver/run_r19_substrate.py \\
        --substrate menger

The launch_r19.sh wrapper kicks off all three in parallel.

Carry-over (optional, gated on a flag): the R19 plan calls for injecting
R18 winners into gen-0 (menger 0f5e931fa3e1, carpet 8776b2026957). When
``--carryover-json PATH`` is supplied, the driver loads that JSON as an
additional gen-0 seed. The plan says this should be done for the real
launch but not for smoke / mini-evolution validation.

Seed lists below currently include ALL R19 seeds. After the B2 PPO smoke
gate runs (experiments/r19_seeds/SMOKE_RESULTS.md), the SUBSTRATE_CONFIG
"seeds" lists should be pruned to PASS-only (R18 precedent). The hybrid
validator on grid_control is expected to PASS smoke (smoke doesn't see D1)
but score with hybrid_action_penalty=0.2 in evolution proper.
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

# topology_type — engine string (NOT the substrate label)
# dims          — fixed by SUBSTRATE_INVARIANTS but pinned here so the
#                 random-generation path doesn't waste rolls
# seeds         — file stems under experiments/r19_seeds/seeds/
#                 (PRUNE THIS to smoke-PASS only after smoke gate runs)
# default_*     — overridable per-substrate from CLI
# audit_soft_rules — carpet only; lets threshold-race mutations train
#                 instead of being demoted to connection by the R17
#                 sierpinski_threshold_inert audit rule
SUBSTRATE_CONFIG: dict[str, dict] = {
    # SMOKE FILTER APPLIED 2026-04-30 (see SMOKE_RESULTS.md):
    #   menger m1-m5 dropped: in-family threshold-race undertrained at 3000 ep
    #     -- evolution will rediscover the family from m6/m7/m8 + carry-over,
    #     same path R18 took.
    #   carpet c6, c8 dropped: probe seeds with structural seat bias.
    #   grid g1 dropped: R8 Connection Go on 16x16 lets P1 rush a straight line
    #     (R18 reproduced same drop). g3 hybrid validator dropped: D1 already
    #     verified standalone via verify_d1.py; no need for in-evolution path.
    "menger": {
        "topology_type": "menger",
        "dims": 3,
        "seeds": [
            "m6_custodian2_territory__menger",
            "m7_surround_connection__menger",
            "m8_outnumber2_inf2_threshold__menger",
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
            "c1_outnumber2_inf2_threshold__carpet",
            "c2_outnumber3_inf2_threshold__carpet",
            "c3_custodian2_inf2_threshold__carpet",
            "c4_surround_inf2_threshold__carpet",
            "c5_none_inf2_threshold__carpet",
            "c7_custodian_connection__carpet",
        ],
        "default_generations": 8,
        "default_population": 30,
        "default_training_budget": 15000,
        # Carpet's in-family combo is influence(r=2) + threshold-race;
        # without audit-mode, _fix_consistency demotes threshold to
        # connection on sierpinski (R17 inert rule). Same call as R18 carpet.
        "audit_soft_rules": True,
    },
    "grid_control": {
        "topology_type": "grid",
        "dims": 2,
        "seeds": [
            "g2_outnumber2_inf1_threshold__grid",
        ],
        "default_generations": 2,
        "default_population": 20,
        "default_training_budget": 10000,
        "audit_soft_rules": False,
    },
}


SEEDS_DIR = _REPO / "experiments" / "r19_seeds" / "seeds"


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
                   help="Append to db filename, e.g. '_validation' so test "
                        "runs don't collide with the real R19 db.")
    p.add_argument("--carryover-json", type=Path, default=None,
                   help="Path to a GameDefV2 JSON to inject as an extra "
                        "gen-0 seed. R19 plan calls for menger/carpet R18 "
                        "winners as carry-overs; pass nothing for smoke or "
                        "mini-evolution.")
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

    db_path = f"genesis_v2_run19_{args.substrate}{args.db_suffix}.db"
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
        logger.info("Loaded CARRY-OVER seed: %s (from %s)",
                    carry.game_id, args.carryover_json)

    logger.info(
        "R19 %s — topo=%s dims=%d seeds=%d audit_soft_rules=%s "
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
    logger.info("R19 %s — DONE", args.substrate)
    return 0


if __name__ == "__main__":
    sys.exit(main())
