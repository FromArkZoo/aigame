"""Deterministic scripted policies for Stage-0b smoke (pre-registered).

ChainBuilder (Maker-shaped): always extends own largest stone group toward the
far face of the target axis. FlipHunter (Breaker-shaped): plays the empty cell
with maximum kernel pressure onto enemy stones. Both break ties by lowest cell
index. These test flip-firing against connection-shaped play, not random
stragglers (synthesis graft 6).
"""
from __future__ import annotations

import numpy as np


W = 22  # hex_rhombus axis_size; coords: q = cell % W, r = cell // W


class ChainBuilder:
    """Maker-shaped agent: extends own largest stone group toward the far face.

    Plays cells adjacent to own stones, biasing toward increasing axis_coord.
    axis=0 → drives across q dimension (col 0→W-1).
    axis=1 → drives across r dimension (row 0→W-1).

    select_action signature matches RandomAgent exactly:
        (obs, legal_actions, deterministic) -> (action, log_prob, value)
    """

    def __init__(self, player: int, axis: int = 0):
        """
        Parameters
        ----------
        player : 1 or 2 (concrete owner id)
        axis : 0 = q-axis (cell % W), 1 = r-axis (cell // W)
        """
        self.player = player
        self.axis = axis
        self.engine = None

    def bind(self, engine) -> "ChainBuilder":
        self.engine = engine
        return self

    def _axis_coord(self, cell: int) -> int:
        if self.axis == 0:
            return cell % W
        return cell // W

    def select_action(
        self,
        obs: np.ndarray,
        legal_actions: list[int] | None = None,
        deterministic: bool = False,
    ) -> tuple[int, float, float]:
        engine = self.engine
        assert engine is not None, "ChainBuilder.bind(engine) must be called first"
        assert legal_actions is not None and len(legal_actions) > 0, \
            "ChainBuilder requires at least one legal action"

        board = engine.board_owners
        topo = engine.topo
        total_cells = engine.total_cells

        # Placement actions only (exclude pass / pie_swap which are >= total_cells)
        placement = [a for a in legal_actions if a < total_cells]
        if not placement:
            # No placement legal; fall back to lowest non-placement action
            return min(legal_actions), 0.0, 0.0

        # Own stone coordinates on axis
        own_axis_coords = [
            self._axis_coord(c)
            for c in topo.active_cells
            if int(board[c]) == self.player
        ]
        # next_target = one step beyond the furthest own stone, or 0 if none
        if own_axis_coords:
            next_target = max(own_axis_coords) + 1
        else:
            next_target = 0

        # Cells adjacent (graph distance 1) to own stones
        own_cells = {
            c for c in topo.active_cells if int(board[c]) == self.player
        }
        adjacent_to_own: set[int] = set()
        for c in own_cells:
            for nbr in topo.get_neighbors(c):
                if int(board[nbr]) == 0:
                    adjacent_to_own.add(nbr)

        candidates = [a for a in placement if a in adjacent_to_own]
        if not candidates:
            # No adjacent empties: fall back to all placements
            candidates = placement

        # Among candidates, minimise |axis_coord(cell) - next_target|,
        # tie-break by lowest cell index
        best_action = min(
            candidates,
            key=lambda a: (abs(self._axis_coord(a) - next_target), a),
        )
        return best_action, 0.0, 0.0


class FlipHunter:
    """Breaker-shaped agent: maximises kernel pressure onto enemy stones.

    For each legal placement cell, computes the sum of decay^distance over
    all enemy-occupied cells within the propagation radius (r=2, decay=0.5).
    Picks the cell with maximum pressure; tie-breaks by lowest cell index.

    select_action signature matches RandomAgent exactly:
        (obs, legal_actions, deterministic) -> (action, log_prob, value)
    """

    def __init__(self, player: int, radius: int = 2, decay: float = 0.5):
        self.player = player
        self.radius = radius
        self.decay = decay
        self.engine = None

    def bind(self, engine) -> "FlipHunter":
        self.engine = engine
        return self

    def select_action(
        self,
        obs: np.ndarray,
        legal_actions: list[int] | None = None,
        deterministic: bool = False,
    ) -> tuple[int, float, float]:
        engine = self.engine
        assert engine is not None, "FlipHunter.bind(engine) must be called first"
        assert legal_actions is not None and len(legal_actions) > 0, \
            "FlipHunter requires at least one legal action"

        board = engine.board_owners
        topo = engine.topo
        total_cells = engine.total_cells
        enemy = 3 - self.player  # 1↔2

        placement = [a for a in legal_actions if a < total_cells]
        if not placement:
            return min(legal_actions), 0.0, 0.0

        enemy_cells = [
            c for c in topo.active_cells if int(board[c]) == enemy
        ]

        def pressure(action: int) -> float:
            if not enemy_cells:
                return 0.0
            total = 0.0
            for ec in enemy_cells:
                d = topo.distance(action, ec)
                if d <= self.radius:
                    total += self.decay ** d
            return total

        best_action = min(
            placement,
            key=lambda a: (-pressure(a), a),
        )
        return best_action, 0.0, 0.0
