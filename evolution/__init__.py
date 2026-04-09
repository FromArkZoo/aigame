"""Evolution module for the Genesis Creativity Engine.

Provides mutation/crossover operators and the main evolutionary loop
that discovers high-quality games via population-based search.
"""

from evolution.operators import CrossoverOperator, MutationOperator
from evolution.loop import EvolutionaryLoop

__all__ = [
    "MutationOperator",
    "CrossoverOperator",
    "EvolutionaryLoop",
]
