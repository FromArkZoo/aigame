"""Deterministic scripted exploiter policies (prereg Stage 0b / Stage-2 bands).

MutualPacker: builds toward its own corner, never within graph distance 5
of any enemy stone (prereg pin: cross-player distance >= 5 so r=2 kernels
cannot overlap -> packing-scores-zero check). PassBot: always passes
(inaction-floor probe). MirrorAgent: answers the opponent's last placement
with its point reflection c -> W*W-1-c (even-board mirror probe, spec §4.4).
ChainBuilder (front-builder) is imported from experiments.siege unchanged.

select_action signature matches RandomAgent: (obs, legal_actions,
deterministic) -> (action, log_prob, value).
"""
from __future__ import annotations

import numpy as np

from experiments.siege.scripted_agents import ChainBuilder  # noqa: F401  (re-export)

W = 22


class PassBot:
    """Always passes. Pass action index == engine.total_cells."""

    def __init__(self, player: int):
        self.player = player
        self.engine = None

    def bind(self, engine) -> "PassBot":
        self.engine = engine
        return self

    def select_action(self, obs, legal_actions=None, deterministic=False):
        return self.engine.total_cells, 0.0, 0.0


class MutualPacker:
    """Packs compactly toward its own corner, avoiding all enemy kernels.

    Corner: P1 -> cell 0, P2 -> cell W*W-1. Among legal placements at
    graph distance >= 5 from EVERY enemy stone, picks the cell closest to
    its corner (tie: lowest index). No qualifying cell -> pass.
    """

    def __init__(self, player: int):
        self.player = player
        self.corner = 0 if player == 1 else W * W - 1
        self.engine = None

    def bind(self, engine) -> "MutualPacker":
        self.engine = engine
        return self

    def select_action(self, obs, legal_actions=None, deterministic=False):
        engine = self.engine
        board, topo = engine.board_owners, engine.topo
        enemy = 3 - self.player
        enemy_cells = [c for c in topo.active_cells if int(board[c]) == enemy]
        placement = [a for a in legal_actions if a < engine.total_cells]
        ok = [a for a in placement
              if all(topo.distance(a, ec) >= 5 for ec in enemy_cells)]
        if not ok:
            return engine.total_cells, 0.0, 0.0
        best = min(ok, key=lambda a: (topo.distance(a, self.corner), a))
        return best, 0.0, 0.0


class MirrorAgent:
    """Plays the point reflection of the opponent's last placement.

    Detection: cells empty at the previous snapshot and now enemy-owned
    (flips recolor occupied cells, placements fill empty ones — so this
    isolates the placement). Mirror cell occupied/illegal, or no new
    enemy placement -> pass. Snapshot updates every select_action call.
    """

    def __init__(self, player: int):
        self.player = player
        self.engine = None
        self._prev = None

    def bind(self, engine) -> "MirrorAgent":
        self.engine = engine
        self._prev = None
        return self

    def select_action(self, obs, legal_actions=None, deterministic=False):
        engine = self.engine
        board = engine.board_owners
        enemy = 3 - self.player
        action = engine.total_cells  # default: pass
        if self._prev is not None:
            placed = [c for c in engine.topo.active_cells
                      if self._prev[c] == 0 and int(board[c]) == enemy]
            if len(placed) == 1:
                target = W * W - 1 - placed[0]
                if legal_actions and target in legal_actions:
                    action = target
        self._prev = board.copy()
        return action, 0.0, 0.0
