#!/usr/bin/env python3
"""R21 driver — runs the evolution for ONE substrate.

R21 is a stack-tuning round (per R21_plan.md): purpose-built seed pool
per substrate, S1a canonical-blob dedup + S5 elite re-eval seed-swap
both active inside the loop, S2 planning-horizon scoring threaded in
via training_results (default w_planning=0.0 unless config flips it).

Per-substrate config (matches R21_plan.md § Run config):
    menger  pop=15 gens=4 budget=10000   (~15 hr wall)
    carpet  pop=15 gens=5 budget=15000   (~13 hr wall)
    grid    pop=15 gens=5 budget=10000   (~3 hr wall)

Seeds loaded from experiments/r21_seeds/seeds/<substrate>/ — the
build_seeds.py output. R21 ships 36 menger / 6 carpet / 4 grid seeds
pre-smoke. The smoke filter (experiments/r18_ppo_smoke/run_smoke.py)
should run BETWEEN seed building and this driver in the typical
pipeline, pruning menger from 36 to ~15-20. For development /
mini-runs, --max-seeds caps the loaded count.

R21 stack inside the loop:
- S1a canonical-blob dedup automatically rejects equivalent kernels
  during mutation/crossover/immigrant generation (evolution/loop.py).
- S5 elite re-eval applies in run.py's scoring loop — carry-over
  elites use carryover_run_seed(id, gen, idx) so re-eval is a fresh
  sample. Pure replace, no EMA.
- pie_rule=True on every seed (post-ac9e642).
- komi_p2=0.0 default; auto-calibration is post-evolution (S4 driver
  is pre-launch deferred work).

Carry-over: R20 carpet anchor `625bfc1f3f49` (4.70 — only above-R19
result) should be added as a gen-0 seed on carpet via
--carryover-json (path to a JSON dump of the game from R20 carpet DB).
Other substrates: no carry-overs (per R21_plan.md § Seed pool design).

Invoke once per substrate:

    OMP_NUM_THREADS=1 .venv/bin/python \\
        experiments/r21_driver/run_r21_substrate.py \\
        --substrate menger

The launch_r21.sh wrapper kicks off all three in parallel.
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

SUBSTRATE_CONFIG: dict[str, dict] = {
    "menger": {
        "topology_type": "menger",
        "dims": 3,
        "default_generations": 4,
        "default_population": 15,
        "default_training_budget": 10000,
        "seeds_subdir": "menger",
        # Smoke filter expected to prune 36 → ~15-20. If running pre-smoke,
        # --max-seeds will cap.
    },
    "carpet": {
        "topology_type": "sierpinski",
        "dims": 2,
        "default_generations": 5,
        "default_population": 15,
        "default_training_budget": 15000,
        "seeds_subdir": "carpet",
    },
    "grid": {
        "topology_type": "grid",
        "dims": 2,
        "default_generations": 5,
        "default_population": 15,
        "default_training_budget": 10000,
        "seeds_subdir": "grid",
    },
}


SEEDS_DIR = _REPO / "experiments" / "r21_seeds" / "seeds"


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
    p.add_argument("--seed", type=int, default=42, help="Global RNG seed.")
    p.add_argument(
        "--db-suffix", type=str, default="",
        help="Append to db filename, e.g. '_validation'.",
    )
    p.add_argument(
        "--max-seeds", type=int, default=None,
        help="Cap the number of seeds loaded (default: all in seeds_subdir). "
             "Useful for development: pre-smoke menger has 36 candidates which "
             "would inflate gen-0 compute by 2-3x.",
    )
    p.add_argument(
        "--smoke-passed-json", type=Path, default=None,
        help="JSON list of seed game_ids that survived smoke. If set, only "
             "these seeds are loaded; others are skipped.",
    )
    p.add_argument(
        "--carryover-json", type=Path, default=None,
        help="GameDefV2 JSON to inject as an extra gen-0 seed. R21 carpet: "
             "load 625bfc1f3f49 from R20 carpet DB.",
    )
    p.add_argument(
        "--resume", action="store_true",
        help="Resume from the substrate's checkpoint if present.",
    )
    return p.parse_args()


def load_substrate_seeds(
    substrate: str,
    *,
    max_seeds: int | None = None,
    smoke_passed: set[str] | None = None,
) -> list[GameDefV2]:
    """Load all JSON seed files under `seeds_subdir`, optionally filtered
    to a smoke-passed subset and/or capped at `max_seeds` items. Files
    are loaded in lexicographic order — deterministic across runs."""
    sub_cfg = SUBSTRATE_CONFIG[substrate]
    seed_dir = SEEDS_DIR / sub_cfg["seeds_subdir"]
    paths = sorted(seed_dir.glob("*.json"))
    games: list[GameDefV2] = []
    for p in paths:
        with open(p) as f:
            game = GameDefV2.from_dict(json.load(f))
        if smoke_passed is not None and game.game_id not in smoke_passed:
            continue
        games.append(game)
    if max_seeds is not None and len(games) > max_seeds:
        games = games[:max_seeds]
    return games


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

    db_path = f"genesis_v2_run21_{args.substrate}{args.db_suffix}.db"
    config.tracking.db_path = db_path

    smoke_passed: set[str] | None = None
    if args.smoke_passed_json is not None:
        with open(args.smoke_passed_json) as f:
            smoke_passed = set(json.load(f))
        logger.info(
            "Filtering to %d smoke-passed seeds from %s",
            len(smoke_passed), args.smoke_passed_json,
        )

    seed_games = load_substrate_seeds(
        args.substrate,
        max_seeds=args.max_seeds,
        smoke_passed=smoke_passed,
    )
    logger.info(
        "Loaded %d seeds from %s",
        len(seed_games), SEEDS_DIR / sub_cfg["seeds_subdir"],
    )

    if args.carryover_json is not None:
        with open(args.carryover_json) as f:
            carry = GameDefV2.from_dict(json.load(f))
        seed_games.append(carry)
        logger.info(
            "Loaded CARRY-OVER seed: %s (from %s)",
            carry.game_id, args.carryover_json,
        )

    # Pie rule sanity: every R21 seed must have pie_rule=True. Carry-overs
    # from R20 should also have it (R20 carpet anchor was a gen-0 pie seed).
    for g in seed_games:
        if not g.pie_rule:
            logger.warning(
                "seed %s has pie_rule=False — R21 mandates pie_rule=True; "
                "the loop's pie-detection will still skip pie propagation "
                "for this seed's descendants",
                g.game_id,
            )

    # If seed count exceeds population, the loop will train all seeds at
    # gen 0 then trim to population_size from gen 1. Log for awareness.
    if len(seed_games) > pop:
        logger.warning(
            "Seed count %d > population_size %d. Gen 0 trains all seeds "
            "(extra compute); gen 1+ trims to %d. Consider running the smoke "
            "filter first or passing --smoke-passed-json / --max-seeds.",
            len(seed_games), pop, pop,
        )

    logger.info(
        "R21 %s — topo=%s dims=%d seeds=%d (gens=%d pop=%d budget=%d)",
        args.substrate, sub_cfg["topology_type"], sub_cfg["dims"],
        len(seed_games), gens, pop, budget,
    )
    logger.info("Output DB: %s", db_path)

    run_pipeline(
        config,
        use_v2=True,
        resume=args.resume,
        seed_games=seed_games,
        audit_soft_rules=False,
    )
    logger.info("R21 %s — DONE", args.substrate)
    return 0


if __name__ == "__main__":
    sys.exit(main())
