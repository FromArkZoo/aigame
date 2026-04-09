"""Evolutionary selection and generation loop.

Manages the population of games across generations, applying selection,
mutation, crossover, and immigration to discover high-quality games
according to their *Go Essence* score.

Supports both V1 (expression-tree) and V2 (topological/structured-rule)
game representations.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

import numpy as np

from config import EvolutionConfig, GenesisConfig

logger = logging.getLogger(__name__)


class EvolutionaryLoop:
    """Manages the evolutionary process across generations.

    Parameters
    ----------
    config : GenesisConfig
        Master configuration (provides both game-generation and evolution
        parameters).
    seed : int, optional
        Random seed.  Defaults to ``config.seed``.
    use_v2 : bool
        If True (default), use V2 topological game representation.
    """

    def __init__(
        self,
        config: GenesisConfig,
        seed: Optional[int] = None,
        use_v2: bool = True,
    ) -> None:
        self.config = config
        self.evo_config: EvolutionConfig = config.evolution
        self.use_v2 = use_v2

        effective_seed = seed if seed is not None else config.seed
        self.rng = np.random.default_rng(effective_seed)

        if use_v2:
            from game_engine.generator_v2 import GameGeneratorV2
            from evolution.operators_v2 import MutationOperatorV2, CrossoverOperatorV2

            self.generator = GameGeneratorV2(config.game, seed=effective_seed)
            self.mutation_op = MutationOperatorV2(self.evo_config, self.rng)
            self.crossover_op = CrossoverOperatorV2(self.evo_config, self.rng)

            # Propagate dimension bounds to operators module
            import evolution.operators_v2 as _ops
            _ops._MAX_DIMENSIONS = config.game.max_dimensions
        else:
            from game_engine.generator import GameGenerator
            from evolution.operators import MutationOperator, CrossoverOperator

            self.generator = GameGenerator(config.game, seed=effective_seed)
            self.mutation_op = MutationOperator(self.evo_config, self.rng)
            self.crossover_op = CrossoverOperator(self.evo_config, self.rng)

        self.population: list = []
        self.generation: int = 0

        # Historical archive: every game that ever existed, keyed by game_id.
        self._archive: Dict[str, object] = {}

    # ------------------------------------------------------------------
    # Population initialisation
    # ------------------------------------------------------------------

    def initialize_population(
        self,
        seed: Optional[int] = None,
        seed_games: Optional[List] = None,
    ) -> list:
        """Generate the initial random population.

        For V2, uses quick_reject to filter out structurally degenerate
        games before they consume training budget.

        Parameters
        ----------
        seed : int, optional
            Base seed for random generation.
        seed_games : list, optional
            Pre-existing game definitions to include in the initial
            population.  These are added first (with fresh game_ids),
            and the remaining slots are filled with random games.
        """
        base_seed = seed if seed is not None else self.config.seed
        pop: list = []

        # --- Inject seed games first ---
        if seed_games:
            import copy, uuid
            for game in seed_games:
                clone = copy.deepcopy(game)
                clone.game_id = uuid.uuid4().hex[:12]
                clone.metadata = {
                    "generation": 0,
                    "parent_ids": [],
                    "seeded_from": game.game_id,
                }
                pop.append(clone)
                self._archive[clone.game_id] = clone
            logger.info(
                "Seeded %d games into initial population.", len(seed_games),
            )

        # --- Fill remaining slots with random games ---
        remaining = self.evo_config.population_size - len(pop)
        if self.use_v2:
            attempts = 0
            max_attempts = remaining * 10
            while len(pop) < self.evo_config.population_size and attempts < max_attempts:
                game = self.generator.generate_game(seed=base_seed + attempts)
                attempts += 1
                # Quick-reject degenerate games before validation
                if hasattr(self.generator, "quick_reject"):
                    if not self.generator.quick_reject(game):
                        continue
                pop.append(game)
                self._archive[game.game_id] = game
        else:
            for i in range(remaining):
                game = self.generator.generate_game(seed=base_seed + i)
                pop.append(game)
                self._archive[game.game_id] = game

        self.population = pop
        self.generation = 0
        logger.info(
            "Initialized population of %d games (generation 0).",
            len(pop),
        )
        return pop

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def tournament_select(self, scores: Dict[str, float], k: int):
        """Tournament selection: pick *k* random games, return the best one."""
        eligible = [g for g in self.population if g.game_id in scores]
        if not eligible:
            return self.population[int(self.rng.integers(0, len(self.population)))]

        k = min(k, len(eligible))
        indices = self.rng.choice(len(eligible), size=k, replace=False)
        tournament = [eligible[int(i)] for i in indices]
        best = max(tournament, key=lambda g: scores.get(g.game_id, 0.0))
        return best

    # ------------------------------------------------------------------
    # Generation step
    # ------------------------------------------------------------------

    def evolve_generation(self, scores: Dict[str, float]) -> list:
        """Create the next generation from the current population and scores.

        Steps:
          1. **Elitism** -- keep the top ``elite_count`` games unchanged.
          2. **Mutation** -- select parents via tournament, mutate.
          3. **Crossover** -- select two parents, crossover.
          4. **Immigration** -- fill remaining slots with new random games.
        """
        new_pop: list = []

        # --- 1. Elitism -----------------------------------------------
        scored_pop = sorted(
            self.population,
            key=lambda g: scores.get(g.game_id, 0.0),
            reverse=True,
        )
        elite_count = min(self.evo_config.elite_count, len(scored_pop))
        for game in scored_pop[:elite_count]:
            new_pop.append(game)

        # --- Compute slot allocation -----------------------------------
        remaining = self.evo_config.population_size - len(new_pop)
        immigration_rate = getattr(self.evo_config, "immigration_rate", 0.15)
        total_rate = (
            self.evo_config.mutation_rate
            + self.evo_config.crossover_rate
            + immigration_rate
        )
        num_mutants = int(remaining * self.evo_config.mutation_rate / total_rate)
        num_crossovers = int(remaining * self.evo_config.crossover_rate / total_rate)
        num_random = remaining - num_mutants - num_crossovers
        num_random = max(num_random, 0)

        # --- 2. Mutants -----------------------------------------------
        for _ in range(num_mutants):
            parent = self.tournament_select(scores, self.evo_config.tournament_size)
            child = self.mutation_op.mutate_game(parent)
            new_pop.append(child)
            self._archive[child.game_id] = child

        # --- 3. Crossovers --------------------------------------------
        for _ in range(num_crossovers):
            p1 = self.tournament_select(scores, self.evo_config.tournament_size)
            p2 = self.tournament_select(scores, self.evo_config.tournament_size)
            attempts = 0
            while p2.game_id == p1.game_id and attempts < 5:
                p2 = self.tournament_select(scores, self.evo_config.tournament_size)
                attempts += 1
            child = self.crossover_op.crossover_games(p1, p2)
            new_pop.append(child)
            self._archive[child.game_id] = child

        # --- 4. Random immigrants --------------------------------------
        for i in range(num_random):
            immigrant_seed = (self.generation + 1) * 10_000 + i
            game = self.generator.generate_game(seed=immigrant_seed)
            # Quick-reject for V2 immigrants
            if self.use_v2 and hasattr(self.generator, "quick_reject"):
                if not self.generator.quick_reject(game):
                    # Try a few more seeds
                    for retry in range(5):
                        game = self.generator.generate_game(
                            seed=immigrant_seed + 100 + retry
                        )
                        if self.generator.quick_reject(game):
                            break
            new_pop.append(game)
            self._archive[game.game_id] = game

        self.population = new_pop
        self.generation += 1
        logger.info(
            "Generation %d: %d elite, %d mutants, %d crossovers, %d immigrants "
            "(pop=%d).",
            self.generation,
            elite_count,
            num_mutants,
            num_crossovers,
            num_random,
            len(new_pop),
        )
        return new_pop

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def _get_game_by_id(self, game_id: str):
        if game_id in self._archive:
            return self._archive[game_id]
        for game in self.population:
            if game.game_id == game_id:
                return game
        return None

    def get_best(self, scores: Dict[str, float], n: int = 1) -> list:
        ranked = sorted(
            self.population,
            key=lambda g: scores.get(g.game_id, 0.0),
            reverse=True,
        )
        return ranked[:n]

    def population_stats(self, scores: Dict[str, float]) -> dict:
        pop_scores = [scores.get(g.game_id, 0.0) for g in self.population]
        complexities = [g.total_complexity() for g in self.population]
        return {
            "generation": self.generation,
            "pop_size": len(self.population),
            "best_score": max(pop_scores) if pop_scores else 0.0,
            "mean_score": float(np.mean(pop_scores)) if pop_scores else 0.0,
            "worst_score": min(pop_scores) if pop_scores else 0.0,
            "mean_complexity": float(np.mean(complexities)) if complexities else 0.0,
        }
