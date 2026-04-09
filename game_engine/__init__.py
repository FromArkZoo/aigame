"""game_engine -- Abstract game generation, representation, and execution.

This package provides:
- ``ExprTree`` / ``GameDef``: expression-tree-based game representation.
- ``GameGenerator``: random game synthesis with validation.
- ``GameEngine``: step-by-step game execution engine.
"""

from game_engine.representation import ExprTree, GameDef
from game_engine.generator import GameGenerator
from game_engine.engine import GameEngine

__all__ = [
    "ExprTree",
    "GameDef",
    "GameGenerator",
    "GameEngine",
]
