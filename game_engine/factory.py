"""Engine factory — picks the right engine for a game definition."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


def create_engine(game):
    """Create the appropriate engine for a game definition.

    Returns a GameEngine (V1) or GameEngineV2 depending on the game type.
    Both share the same public interface: reset(), step(), get_legal_actions(),
    get_current_player(), clone().
    """
    from game_engine.game_def_v2 import GameDefV2

    if isinstance(game, GameDefV2):
        from game_engine.engine_v2 import GameEngineV2
        return GameEngineV2(game)
    else:
        from game_engine.engine import GameEngine
        return GameEngine(game)
