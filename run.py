#!/usr/bin/env python3
"""Genesis Creativity Engine — Main Pipeline (V2).

Usage:
    python run.py --generations 10 --population 50 --training-budget 10000

Runs the full generate -> train -> score -> rank -> evolve -> repeat loop.

V2 uses topological spaces with structured rules instead of expression trees.
"""

import argparse
import hashlib
import json
import logging
import os
import signal
import sys
import time

import numpy as np

from config import GenesisConfig
from training.trainer import SelfPlayTrainer
from training.utils import evaluate_agents, RandomAgent
from metrics.scoring import GoEssenceScorer
from arena.ranking import Arena
from evolution.loop import EvolutionaryLoop
from tracking.database import GenesisDB
from tracking.visualisation import GenesisVisualiser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("genesis")


def parse_args():
    p = argparse.ArgumentParser(description="Genesis Creativity Engine")
    p.add_argument("--generations", type=int, default=None,
                   help="Number of evolutionary generations (default: from config)")
    p.add_argument("--population", type=int, default=None,
                   help="Population size per generation (default: from config)")
    p.add_argument("--training-budget", type=int, default=None,
                   help="Training episodes per game (default: from config)")
    p.add_argument("--seed", type=int, default=None,
                   help="Global random seed (default: from config)")
    p.add_argument("--db-path", type=str, default=None,
                   help="Path to SQLite database (default: from config)")
    p.add_argument("--num-runs", type=int, default=None,
                   help="Independent training runs per game for diversity "
                        "(default: from config)")
    p.add_argument("--immigration-rate", type=float, default=None,
                   help="Fraction of each generation that are random immigrants "
                        "(default: from config)")
    p.add_argument("--resume", action="store_true",
                   help="Resume from the last checkpoint saved in the DB directory")
    p.add_argument("--v1", action="store_true",
                   help="Use V1 expression-tree representation instead of V2")
    p.add_argument("--seed-db", type=str, default=None,
                   help="Path to a previous run's SQLite DB to load seed games from")
    p.add_argument("--seed-games", type=str, nargs="+", default=None,
                   help="Game IDs to seed into the initial population (requires --seed-db)")
    p.add_argument("--seed-json", type=str, nargs="+", default=None,
                   help="Paths to .json game definitions to seed into the initial "
                        "population (independent of --seed-db). Combine with "
                        "--seed-games to mix DB-loaded and hand-crafted seeds.")
    p.add_argument("--max-dimensions", type=int, default=None,
                   help="Maximum number of dimensions for generated games (default: 6)")
    p.add_argument("--ca-probability", type=float, default=None,
                   help="Probability of generating CA games (default: 0.3)")
    p.add_argument("--simultaneous-probability", type=float, default=None,
                   help="Probability of generating simultaneous-turn games (default: 0.30)")
    p.add_argument("--topology-types", type=str, nargs="+", default=None,
                   help="Restrict generated games to these topology_type values "
                        "(default: from config). Used by R18 per-substrate runs "
                        "to confine each evolution to a single substrate.")
    p.add_argument("--audit-soft-rules", action="store_true",
                   help="Run with soft quick_reject rules in audit mode: violations "
                        "tag game.metadata['soft_violations'] but do NOT reject the "
                        "game. Lets unvalidated rule combos (e.g. sierpinski + "
                        "threshold, sierpinski + CA) train so post-run analysis can "
                        "compare their GE distribution to non-violating games. "
                        "Costs ~5-10% extra compute. See scripts/audit_soft_rules.py "
                        "for the post-run analysis.")
    return p.parse_args()


class _GameTimeout(Exception):
    """Raised when a game exceeds the training time limit."""


_GAME_TIMEOUT_SECONDS = 3 * 3600  # 3 hours


def _timeout_handler(signum, frame):
    raise _GameTimeout(
        f"Game training exceeded {_GAME_TIMEOUT_SECONDS // 3600}h time limit"
    )


def _game_description(game) -> str:
    """Return a human-readable description of a game for logging."""
    from game_engine.game_def_v2 import GameDefV2
    if isinstance(game, GameDefV2):
        parts = [
            f"{game.game_id} ({game.num_dimensions}D",
            f"{game.axis_size}^{game.num_dimensions}={game.total_cells} cells",
            f"topo={game.topology_type}",
            f"capture={game.capture_rule.capture_type}",
            f"win={game.win_condition.condition_type}",
        ]
        if game.action_rule.has_move():
            parts.append(f"actions={'+'.join(game.action_rule.action_types)}")
        return ", ".join(parts) + ")"
    return (
        f"{game.game_id} (dim={game.state_dim}, actions={game.num_actions})"
    )


def deterministic_run_seed(game_id: str, run_idx: int = 0) -> int:
    """Derive a deterministic PPO seed from game_id + run index.

    R18 followup (Phase A volatility analysis 2026-04-30): the previous scheme
    `config.seed + gen * 10000 + idx` made the PPO seed depend on the
    generation, so the same game scored in two different generations got two
    different seeds. Phase A confirmed this drives 50-80% GE swings on
    PPO-marginal substrates (carpet, vicsek, grid). With a deterministic seed
    keyed on game_id, the same game scored twice gives the same answer.

    The 32-bit prefix of an MD5 hash gives a uniformly distributed seed space
    that's stable across Python runs (unlike `hash(...)` which is salted).

    Use this for new games (mutants, crossovers, immigrants) and for the
    initial scoring of seed games. For carry-over elites (R21 S5),
    `carryover_run_seed` deliberately re-introduces generation dependence
    so each re-evaluation is a fresh sample.
    """
    h = hashlib.md5(f"{game_id}:{run_idx}".encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def carryover_run_seed(game_id: str, generation: int, run_idx: int = 0) -> int:
    """R21 S5: gen-dependent PPO seed for elite re-evaluation.

    Deliberate inversion of `deterministic_run_seed` for elites that have
    carried over from an earlier generation. R20+R20.5 finalization
    confirmed a +0.11 upward bias in production GE driven by the
    selection effect of R18's per-game stable seed: games that happened
    to land on the high end of the PPO-noise distribution at their first
    scoring stayed lucky forever (the same seed was re-used every
    generation, so their score never re-rolled).

    For carry-over elites we want a fresh sample each generation. Pure
    replace (no EMA blending) — the variance is handled by S6's
    20-rerun finalization at the slate stage.

    The 32-bit MD5 prefix gives a uniformly distributed, cross-process
    stable seed space.
    """
    h = hashlib.md5(
        f"{game_id}:gen{generation}:{run_idx}".encode("utf-8")
    ).hexdigest()
    return int(h[:8], 16)


def _average_run_inputs(
    per_run_curves: list[list[tuple[int, float]]],
    per_run_trained_vs_random: list[float],
    per_run_p0_winrate: list[float],
    per_run_avg_game_length: list[float],
) -> tuple[list[tuple[int, float]], float, float, float]:
    """C2 multi-seed averaging — collapse N parallel PPO runs into one
    headline-GE input bundle.

    The four quantities below are the only `evaluate_game` inputs that are
    re-rolled per PPO seed. Heuristic / greedy probes don't depend on the
    trained agent; cross-play uses all runs already; max_turns is a game
    property. Averaging only those four removes the noise we can remove
    while leaving everything else untouched.

    The learning curves all share checkpoints (config.metrics.learning_curve_
    checkpoints), so the average is a point-wise mean of winrates aligned
    by episode.
    """
    n_runs = len(per_run_curves)
    if n_runs == 0:
        return [], 0.0, 0.5, 0.0
    if n_runs == 1:
        return (
            list(per_run_curves[0]),
            float(per_run_trained_vs_random[0]),
            float(per_run_p0_winrate[0]),
            float(per_run_avg_game_length[0]),
        )

    # All curves should share the same checkpoint episodes; assert and average.
    base_eps = [ep for ep, _wr in per_run_curves[0]]
    n_pts = len(base_eps)
    summed = [0.0] * n_pts
    counted = [0] * n_pts
    for curve in per_run_curves:
        if len(curve) != n_pts:
            # Different curve length — fall back to using the primary curve only.
            return (
                list(per_run_curves[0]),
                sum(per_run_trained_vs_random) / n_runs,
                sum(per_run_p0_winrate) / n_runs,
                sum(per_run_avg_game_length) / n_runs,
            )
        for i, (_ep, wr) in enumerate(curve):
            summed[i] += float(wr)
            counted[i] += 1
    avg_curve = [(base_eps[i], summed[i] / counted[i]) for i in range(n_pts)]
    return (
        avg_curve,
        sum(per_run_trained_vs_random) / n_runs,
        sum(per_run_p0_winrate) / n_runs,
        sum(per_run_avg_game_length) / n_runs,
    )


def train_and_evaluate_game(
    game,
    config: GenesisConfig,
    scorer: GoEssenceScorer,
    db: GenesisDB,
    run_seed: int,
    population_fingerprints: list[tuple] | None = None,
    generation: int | None = None,
) -> dict:
    """Train agents on a game, evaluate all metrics, return scores.

    R21 S5: when `generation` is provided, the C2 extra-runs path uses
    `carryover_run_seed(game_id, generation, run_idx=i+1)` so all
    `num_independent_runs` seeds are gen-dependent (the elite re-eval
    case). When `generation` is None (default), extras use the legacy
    `deterministic_run_seed(game_id, run_idx=i+1)` — preserving R18's
    stability for new games.
    """

    # Set per-game timeout (SIGALRM, Unix only)
    old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(_GAME_TIMEOUT_SECONDS)

    try:
        return _train_and_evaluate_game_inner(
            game, config, scorer, db, run_seed, population_fingerprints, generation,
        )
    finally:
        signal.alarm(0)  # cancel alarm
        signal.signal(signal.SIGALRM, old_handler)


def _train_and_evaluate_game_inner(
    game,
    config: GenesisConfig,
    scorer: GoEssenceScorer,
    db: GenesisDB,
    run_seed: int,
    population_fingerprints: list[tuple] | None = None,
    generation: int | None = None,
) -> dict:
    """Train agents on a game, evaluate all metrics, return scores."""

    # --- Quick validation for V2 ---
    from game_engine.game_def_v2 import GameDefV2
    if isinstance(game, GameDefV2):
        from game_engine.generator_v2 import GameGeneratorV2
        # Hand-crafted seeded games bypass validate_game: random rollouts
        # often can't terminate connection-style wins on complex substrates
        # (e.g. frac_C_fractal: sierpinski + connection rarely terminates
        # in 200 random plies though PPO finds decisive play). Seeds were
        # already vetted upstream — usually by direct play in fractal-spike
        # or by past evolutionary scoring.
        is_seeded = bool(game.metadata.get("seeded_from"))
        if not is_seeded:
            validator = GameGeneratorV2(config.game, seed=run_seed)
            if not validator.validate_game(game, num_rollouts=5, max_rollout_steps=200):
                logger.info("    -> Quick-rejected (failed validation)")
                return {
                    "rule_simplicity": 0.0,
                    "strategic_depth": 0.0,
                    "non_triviality": 0.0,
                    "strategic_diversity": 0.0,
                    "go_essence": 0.0,
                }

    # --- Primary training run ---
    trainer = SelfPlayTrainer(
        game=game,
        config=config.training,
        metrics_config=config.metrics,
        seed=run_seed,
    )
    train_result = trainer.train()

    learning_curve = train_result["learning_curve"]
    eval_stats = trainer.evaluate(num_episodes=config.training.eval_episodes)

    # Log training run
    curve_for_db = [[ep, wr_rand] for ep, _wr_opp, wr_rand in learning_curve]
    db.insert_training_run(
        game_id=game.game_id,
        run_seed=run_seed,
        learning_curve=curve_for_db,
        final_winrate=eval_stats["p0_winrate"],
        trained_vs_random=eval_stats["trained_vs_random_winrate"],
        avg_game_length=eval_stats["avg_game_length"],
        training_steps=train_result["training_steps"],
    )

    # --- Additional independent runs for strategic diversity ---
    cross_play_results = []
    num_extra_runs = config.training.num_independent_runs - 1
    all_agents = [train_result["final_agents"]]
    # Collect per-run series for C2 multi-seed averaging.
    per_run_trained_vs_random = [eval_stats["trained_vs_random_winrate"]]
    per_run_p0_winrate = [eval_stats["p0_winrate"]]
    per_run_avg_game_length = [eval_stats["avg_game_length"]]
    primary_curve_pairs = [(ep, wr) for ep, _wo, wr in learning_curve]
    per_run_curves = [primary_curve_pairs]

    for i in range(num_extra_runs):
        # Deterministic per-(game, run_idx) seed — matches the primary run's
        # scheme so all num_independent_runs are reproducible from game_id.
        # R21 S5: for carry-over elites (caller passes `generation`), the
        # extras seeds also become gen-dependent so the whole C2 bundle is
        # a fresh sample. New games (generation=None) keep R18 stability.
        if generation is not None:
            extra_seed = carryover_run_seed(game.game_id, generation, run_idx=i + 1)
        else:
            extra_seed = deterministic_run_seed(game.game_id, run_idx=i + 1)
        extra_trainer = SelfPlayTrainer(
            game=game,
            config=config.training,
            metrics_config=config.metrics,
            seed=extra_seed,
        )
        extra_result = extra_trainer.train()
        all_agents.append(extra_result["final_agents"])

        extra_eval = extra_trainer.evaluate(
            num_episodes=config.training.eval_episodes
        )
        per_run_trained_vs_random.append(extra_eval["trained_vs_random_winrate"])
        per_run_p0_winrate.append(extra_eval["p0_winrate"])
        per_run_avg_game_length.append(extra_eval["avg_game_length"])
        extra_curve = [[ep, wr] for ep, _wo, wr in extra_result["learning_curve"]]
        per_run_curves.append([(ep, wr) for ep, wr in extra_curve])
        db.insert_training_run(
            game_id=game.game_id,
            run_seed=extra_seed,
            learning_curve=extra_curve,
            final_winrate=extra_eval["p0_winrate"],
            trained_vs_random=extra_eval["trained_vs_random_winrate"],
            avg_game_length=extra_eval["avg_game_length"],
            training_steps=extra_result["training_steps"],
        )

    # --- C2 multi-seed averaging ---
    # When num_independent_runs > 1 the headline GE inputs are averaged
    # across all runs. Phase A noise-floor analysis showed per-game GE std
    # of 0.10-0.17 on carpet/vicsek/grid driven by PPO inconsistency; the
    # 1/sqrt(N) reduction takes the carpet champion's std from 0.155 -> ~0.09.
    # Quantities not driven by the trained agent (heuristic/greedy probes,
    # cross-play, max_turns) keep their primary-run / aggregate values.
    avg_curve, avg_tvr, avg_p0, avg_alen = _average_run_inputs(
        per_run_curves,
        per_run_trained_vs_random,
        per_run_p0_winrate,
        per_run_avg_game_length,
    )

    # Cross-play: pit agent[0] from each independent run against each other
    if len(all_agents) > 1:
        for i in range(len(all_agents)):
            for j in range(i + 1, len(all_agents)):
                cp_stats = evaluate_agents(
                    game, all_agents[i][0], all_agents[j][0],
                    num_episodes=config.training.eval_episodes,
                )
                cross_play_results.append(cp_stats["p0_winrate"])

    # --- Compute Go Essence metrics ---
    training_results = {
        "learning_curve": avg_curve,
        "training_budget": config.training.training_budget,
        "trained_vs_random_winrate": avg_tvr,
        "p1_winrate": avg_p0,  # legacy key: P1-seat winrate
        "p0_winrate": avg_p0,  # correctly-named alias
        "heuristic_p1_winrate": eval_stats.get("heuristic_p1_winrate", 0.5),
        "heuristic_decisive_rate": eval_stats.get("heuristic_decisive_rate", 0.0),
        "greedy_p1_winrate": eval_stats.get("greedy_p1_winrate", 0.5),
        "greedy_decisive_rate": eval_stats.get("greedy_decisive_rate", 0.0),
        "avg_game_length": avg_alen,
        "max_turns": getattr(game, "max_game_steps", None),
        "per_run_trained_vs_random": per_run_trained_vs_random,
    }
    scores = scorer.evaluate_game(
        game, training_results, cross_play_results or None,
        population_fingerprints=population_fingerprints,
    )

    # Persist scores
    db.insert_scores(game.game_id, scores)

    return scores


def _checkpoint_path(db_path: str) -> str:
    """Return the checkpoint file path derived from the DB path."""
    base = os.path.splitext(db_path)[0]
    return base + ".checkpoint.json"


def _save_checkpoint(
    checkpoint_path: str,
    gen: int,
    population: list,
    scores_map: dict,
    arena: Arena,
    use_v2: bool,
) -> None:
    """Save pipeline state after a completed generation."""
    data = {
        "generation": gen,
        "scores_map": scores_map,
        "use_v2": use_v2,
        "population": [g.to_dict() for g in population],
        "arena": arena.to_dict(),
    }
    tmp_path = checkpoint_path + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump(data, f)
    os.replace(tmp_path, checkpoint_path)
    logger.info("Checkpoint saved: generation %d -> %s", gen, checkpoint_path)


def _load_checkpoint(
    checkpoint_path: str,
    config: GenesisConfig,
) -> dict:
    """Load checkpoint and return restored state."""
    with open(checkpoint_path) as f:
        data = json.load(f)

    use_v2 = data.get("use_v2", True)

    # Restore population
    if use_v2:
        from game_engine.game_def_v2 import GameDefV2
        population = [GameDefV2.from_dict(d) for d in data["population"]]
    else:
        from game_engine.representation import GameDef
        population = [GameDef.from_dict(d) for d in data["population"]]

    # Restore arena
    arena = Arena.from_dict(data["arena"], config.arena)

    return {
        "generation": data["generation"],
        "scores_map": data["scores_map"],
        "population": population,
        "arena": arena,
        "use_v2": use_v2,
    }


def run_pipeline(
    config: GenesisConfig,
    use_v2: bool = True,
    resume: bool = False,
    seed_games: list | None = None,
    audit_soft_rules: bool = False,
):
    """Execute the full Genesis pipeline."""

    db = GenesisDB(config.tracking)
    scorer = GoEssenceScorer(config.metrics)
    checkpoint_path = _checkpoint_path(config.tracking.db_path)

    num_generations = config.evolution.num_generations
    pop_size = config.evolution.population_size

    # --- Resume from checkpoint if requested ---
    resume_gen = -1
    if resume and os.path.exists(checkpoint_path):
        logger.info("Resuming from checkpoint: %s", checkpoint_path)
        ckpt = _load_checkpoint(checkpoint_path, config)
        resume_gen = ckpt["generation"]
        scores_map = ckpt["scores_map"]
        arena = ckpt["arena"]
        use_v2 = ckpt["use_v2"]

        evo = EvolutionaryLoop(
            config, seed=config.seed, use_v2=use_v2,
            audit_soft_rules=audit_soft_rules,
        )
        # Restore evo state
        evo.population = ckpt["population"]
        evo.generation = resume_gen
        for g in evo.population:
            evo._archive[g.game_id] = g

        population = evo.population
        logger.info(
            "Resumed at generation %d with %d games. Continuing from generation %d.",
            resume_gen, len(population), resume_gen + 1,
        )
    else:
        arena = Arena(config.arena)
        evo = EvolutionaryLoop(
            config, seed=config.seed, use_v2=use_v2,
            audit_soft_rules=audit_soft_rules,
        )
        scores_map = {}

    version_str = "V2 (topological)" if use_v2 else "V1 (expression-tree)"
    logger.info(
        "Starting Genesis Engine %s: %d generations, population %d, "
        "training budget %d episodes/game",
        version_str, num_generations, pop_size, config.training.training_budget,
    )
    start_time = time.time()

    if resume_gen < 0:
        # === Generation 0: Random population (with optional seed games) ===
        logger.info("=== Generation 0: Initializing random population ===")
        population = evo.initialize_population(
            seed=config.seed, seed_games=seed_games,
        )
        logger.info("Generated %d games.", len(population))

    start_gen = 0 if resume_gen < 0 else resume_gen + 1

    for gen in range(start_gen, num_generations + 1):
        gen_start = time.time()
        if gen > 0:
            logger.info("=== Generation %d: Evolving ===", gen)
            population = evo.evolve_generation(scores_map)

        scores_map = {}  # game_id -> go_essence
        gen_scores = []   # list of go_essence values

        # Compute structural fingerprints for novelty scoring
        pop_fingerprints = [scorer.structural_fingerprint(g) for g in population]

        for idx, game in enumerate(population):
            logger.info(
                "  [Gen %d] Training game %d/%d: %s",
                gen, idx + 1, len(population), _game_description(game),
            )

            # Register game in DB
            db.insert_game(
                game_id=game.game_id,
                generation=gen,
                parent_ids=game.metadata.get("parent_ids",
                            game.metadata.get("parents", [])),
                state_dim=game.state_dim,
                num_actions=game.num_actions,
                num_players=game.num_players,
                observation_type=getattr(game, "observation_type", "full"),
                rule_representation=game.to_dict(),
                rule_complexity=game.total_complexity(),
            )

            try:
                # R18 followup: deterministic seed keyed on game_id so the
                # same game scored twice gives the same answer. See
                # deterministic_run_seed() docstring for context.
                #
                # R21 S5: detect carry-over elites (games whose recorded
                # birth gen is < the current scoring gen) and switch to a
                # gen-dependent seed so each re-eval is a fresh sample.
                # R20+R20.5 confirmed R18's stable seed locked lucky
                # elites in (+0.11 upward bias on the leaderboard).
                born_gen = game.metadata.get("generation", gen)
                is_carryover_elite = born_gen < gen
                if is_carryover_elite:
                    run_seed = carryover_run_seed(game.game_id, gen, run_idx=0)
                    extras_generation = gen
                else:
                    run_seed = deterministic_run_seed(game.game_id, run_idx=0)
                    extras_generation = None
                scores = train_and_evaluate_game(
                    game, config, scorer, db, run_seed,
                    population_fingerprints=pop_fingerprints,
                    generation=extras_generation,
                )
                scores_map[game.game_id] = scores["go_essence"]
                gen_scores.append(scores["go_essence"])

                logger.info(
                    "    -> Go Essence: %.4f (depth=%.3f, diversity=%.3f, "
                    "simplicity=%.3f, non-triv=%.3f)",
                    scores["go_essence"],
                    scores["strategic_depth"],
                    scores["strategic_diversity"],
                    scores["rule_simplicity"],
                    scores["non_triviality"],
                )
            except _GameTimeout:
                logger.warning(
                    "    -> TIMEOUT after %dh (skipping game %s)",
                    _GAME_TIMEOUT_SECONDS // 3600, game.game_id,
                )
                scores_map[game.game_id] = 0.0
                gen_scores.append(0.0)
            except Exception as e:
                logger.warning(
                    "    -> FAILED: %s (skipping game %s)", e, game.game_id
                )
                scores_map[game.game_id] = 0.0
                gen_scores.append(0.0)

        # --- Arena tournament ---
        for gid, score in scores_map.items():
            arena.add_game(gid, {"go_essence": score}, generation=gen)
        arena.run_tournament()

        # Log match history to DB
        for match in arena.match_history:
            db.insert_match(
                match["game_a"], match["game_b"],
                match["score_a"], match["score_b"],
                match["elo_a"], match["elo_b"],
            )

        # Update ELO in DB
        for gid, entry in arena.games.items():
            db.update_elo(gid, entry.elo)

        # Log generation stats
        db.insert_generation(gen, len(population), gen_scores)

        gen_elapsed = time.time() - gen_start
        stats = evo.population_stats(scores_map)
        logger.info(
            "  Generation %d complete in %.1fs — "
            "Best: %.4f, Mean: %.4f, Pop: %d",
            gen, gen_elapsed,
            stats["best_score"], stats["mean_score"], stats["pop_size"],
        )

        # Print leaderboard
        print("\n" + arena.format_leaderboard(10))
        print()

        # === Save checkpoint after each completed generation ===
        _save_checkpoint(checkpoint_path, gen, population, scores_map, arena, use_v2)

    # === Final summary ===
    total_elapsed = time.time() - start_time
    logger.info("Genesis Engine complete. Total time: %.1fs", total_elapsed)
    logger.info("Database saved to: %s", config.tracking.db_path)

    # Generate plots
    try:
        vis = GenesisVisualiser(config.tracking, db)
        vis.generate_all_plots()
        logger.info("Plots saved to: %s/", config.tracking.plot_dir)
    except Exception as e:
        logger.warning("Plot generation failed: %s", e)

    # Print final leaderboard
    print("\n" + "=" * 66)
    print("FINAL LEADERBOARD")
    print("=" * 66)
    print(arena.format_leaderboard(20))

    # Clean up checkpoint on successful completion
    if os.path.exists(checkpoint_path):
        os.remove(checkpoint_path)
        logger.info("Checkpoint removed (run completed successfully).")

    db.close()


def main():
    args = parse_args()
    config = GenesisConfig()

    # Override config from CLI args
    if args.generations is not None:
        config.evolution.num_generations = args.generations
    if args.population is not None:
        config.evolution.population_size = args.population
    if args.training_budget is not None:
        config.training.training_budget = args.training_budget
    if args.seed is not None:
        config.seed = args.seed
    if args.db_path is not None:
        config.tracking.db_path = args.db_path
    if args.num_runs is not None:
        config.training.num_independent_runs = args.num_runs
    if args.immigration_rate is not None:
        config.evolution.immigration_rate = args.immigration_rate
    if args.max_dimensions is not None:
        config.game.max_dimensions = args.max_dimensions
    if args.ca_probability is not None:
        config.game.ca_probability = args.ca_probability
    if args.simultaneous_probability is not None:
        config.game.simultaneous_probability = args.simultaneous_probability
    if args.topology_types is not None:
        config.game.topology_types = list(args.topology_types)

    # Load seed games from a previous run's database and/or hand-crafted JSON files
    loaded_seed_games = None
    if (args.seed_db and args.seed_games) or args.seed_json:
        from game_engine.game_def_v2 import GameDefV2
        loaded_seed_games = []

        if args.seed_db and args.seed_games:
            import sqlite3
            logger.info(
                "Loading %d seed games from %s",
                len(args.seed_games), args.seed_db,
            )
            conn = sqlite3.connect(args.seed_db)
            conn.row_factory = sqlite3.Row
            for gid in args.seed_games:
                row = conn.execute(
                    "SELECT rule_representation FROM games WHERE game_id = ?",
                    (gid,),
                ).fetchone()
                if row:
                    game = GameDefV2.from_dict(json.loads(row["rule_representation"]))
                    loaded_seed_games.append(game)
                    logger.info("  Loaded seed game: %s", gid)
                else:
                    logger.warning("  Seed game %s not found in %s", gid, args.seed_db)
            conn.close()

        if args.seed_json:
            logger.info(
                "Loading %d seed games from JSON files", len(args.seed_json),
            )
            for path in args.seed_json:
                with open(path) as f:
                    game = GameDefV2.from_dict(json.load(f))
                loaded_seed_games.append(game)
                logger.info("  Loaded seed game from %s: %s", path, game.game_id)

    use_v2 = not args.v1
    run_pipeline(
        config, use_v2=use_v2, resume=args.resume, seed_games=loaded_seed_games,
        audit_soft_rules=args.audit_soft_rules,
    )


if __name__ == "__main__":
    main()
