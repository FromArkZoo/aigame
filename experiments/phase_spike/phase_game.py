"""Phase-Extended c6bb58075520: a Phase-1 spike for complex/phase stone mechanics.

Source game: 8x8 torus, alternating, place-anywhere on empty cells, outnumber-2
capture, radius-1 signed influence (strength 0.93, decay 0.51), threshold win
at 22.65 effective own-cell influence sum.

Extension: each placement specifies a stone PHASE in {+1, -1} in addition to
the implicit owner (P1 or P2). The mechanic decouples ownership from team
alignment:
  - Owner-matched phase (P1@+1, P2@-1): standard play, full score contribution,
    vulnerable to opposite-phase neighbors.
  - Owner-mismatched phase (P1@-1, P2@+1): "camouflage stones". Owned by P1
    but reads as P2-aligned for influence and capture. Contributes negatively
    to own score, but survives enemy territory and blocks enemy from claiming
    the cell.

Cell state encoding (5 values):
  0 = empty
  1 = P1@+1  (P1 owner, +1 phase) — natural P1 stone
  2 = P1@-1  (P1 owner, -1 phase) — P1 camouflage stone
  3 = P2@-1  (P2 owner, -1 phase) — natural P2 stone
  4 = P2@+1  (P2 owner, +1 phase) — P2 camouflage stone

Action encoding: action = cell * 2 + phase_bit, plus a pass action.
  cell ∈ [0, 64), phase_bit ∈ {0, 1} where 0 = +1 phase, 1 = -1 phase
  action ∈ [0, 128) for placements, action == 128 for pass.

This module is intentionally standalone — it does NOT modify the main engine
or generator. It reuses TopologicalSpace from the main project for neighbor
lookup but implements all phase-aware game logic from scratch.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np

from game_engine.topology import TopologicalSpace


# ---------------------------------------------------------------------------
# Constants — calibrated to match c6bb58075520
# ---------------------------------------------------------------------------

AXIS_SIZE = 8
TOTAL_CELLS = AXIS_SIZE * AXIS_SIZE
INFLUENCE_RADIUS = 1
INFLUENCE_STRENGTH = 0.9322817703212022
INFLUENCE_DECAY = 0.5097131432079061
OUTNUMBER_THRESHOLD = 2  # neighbors-of-opposite-phase must exceed neighbors-of-same-phase by this much for capture
WIN_THRESHOLD = 22.645289471714786
MAX_TURNS = 100

# Cell state codes
EMPTY = 0
P1_POS = 1   # P1 owner, +1 phase (natural)
P1_NEG = 2   # P1 owner, -1 phase (camouflage)
P2_NEG = 3   # P2 owner, -1 phase (natural)
P2_POS = 4   # P2 owner, +1 phase (camouflage)

# Helpers to extract owner / phase from cell state
def cell_owner(state: int) -> int:
    """Returns 0 (empty), 1 (P1), or 2 (P2)."""
    if state == EMPTY:
        return 0
    if state in (P1_POS, P1_NEG):
        return 1
    return 2

def cell_phase(state: int) -> int:
    """Returns 0 (empty), +1, or -1."""
    if state == EMPTY:
        return 0
    if state in (P1_POS, P2_POS):
        return 1
    return -1

def encode_state(owner: int, phase: int) -> int:
    """owner in {1, 2}, phase in {1, -1} -> cell state code."""
    if owner == 1 and phase == 1:
        return P1_POS
    if owner == 1 and phase == -1:
        return P1_NEG
    if owner == 2 and phase == -1:
        return P2_NEG
    if owner == 2 and phase == 1:
        return P2_POS
    raise ValueError(f"invalid owner={owner} phase={phase}")


# ---------------------------------------------------------------------------
# Game engine
# ---------------------------------------------------------------------------

PASS_ACTION = TOTAL_CELLS * 2  # actions [0, 128) are placements, 128 is pass


def decode_action(action: int) -> dict:
    """Decode an action into {type, cell, phase}."""
    if action == PASS_ACTION:
        return {"type": "pass"}
    if not 0 <= action < TOTAL_CELLS * 2:
        raise ValueError(f"action {action} out of range")
    cell = action // 2
    phase_bit = action % 2
    phase = 1 if phase_bit == 0 else -1
    return {"type": "place", "cell": cell, "phase": phase}


def encode_action(cell: int, phase: int) -> int:
    """Encode placement action."""
    if phase == 1:
        return cell * 2
    if phase == -1:
        return cell * 2 + 1
    raise ValueError(f"phase must be 1 or -1, got {phase}")


class PhaseGame:
    """Standalone phase-extended game engine."""

    def __init__(self, seed: int | None = None):
        self.topo = TopologicalSpace(2, AXIS_SIZE, "torus")
        self.board = np.zeros(TOTAL_CELLS, dtype=np.int8)  # cell state codes
        self.current_player = 1  # 1 or 2; alternates
        self.step_count = 0
        self.consecutive_passes = 0
        self.done = False
        self.winner: int | None = None
        self.move_log: list[dict] = []
        self.rng = np.random.default_rng(seed)

    # --- queries ---

    def get_legal_actions(self) -> list[int]:
        """All legal actions for the current player.

        Place at any empty cell with either phase. Pass is always legal.
        """
        if self.done:
            return []
        actions = []
        for cell in range(TOTAL_CELLS):
            if self.board[cell] == EMPTY:
                actions.append(encode_action(cell, 1))
                actions.append(encode_action(cell, -1))
        actions.append(PASS_ACTION)
        return actions

    def board_values(self) -> np.ndarray:
        """Compute the influence field: for each cell, sum of stone_phase × strength × decay^d
        over all occupied cells within radius INFLUENCE_RADIUS.
        """
        values = np.zeros(TOTAL_CELLS, dtype=np.float64)
        for cell in range(TOTAL_CELLS):
            if self.board[cell] == EMPTY:
                continue
            phase = cell_phase(int(self.board[cell]))
            # Self-contribution
            values[cell] += phase * INFLUENCE_STRENGTH
            # Radius-1 propagation to direct neighbors
            for nbr in self.topo.get_neighbors(cell):
                values[nbr] += phase * INFLUENCE_STRENGTH * INFLUENCE_DECAY
        return values

    def player_score(self, player: int) -> float:
        """Effective threshold sum for a player.

        Each player has a target phase: P1's target is +1, P2's target is -1.
        For each cell the player owns, contribution = cell_val × target_phase.
        - P1 natural (+1): in a P1 cluster, cell_val is positive → contributes positively.
        - P1 camo (-1): in a P2 cluster, cell_val is negative → contributes positively
          via target × negative = +1 × (negative-by-environment); also +1 × own-radiation -1
          subtracts. Net depends on environment.
        - P2 natural (-1): in P2 cluster, cell_val negative → -1 × negative = positive ✓
        - P2 camo (+1): in P1 cluster, cell_val positive → -1 × positive = negative ✗

        Earlier (pre-fix) version used cell_val × stone_phase for P1 and
        cell_val × -stone_phase for P2, which made P2's natural cluster
        accrue NEGATIVE score (P2 unwinnable). Fixed 2026-04-25 after spike eval.
        """
        target = 1 if player == 1 else -1
        values = self.board_values()
        total = 0.0
        for cell in range(TOTAL_CELLS):
            state = int(self.board[cell])
            if cell_owner(state) != player:
                continue
            cell_val = values[cell]
            total += cell_val * target
        return total

    # --- mutation ---

    def step(self, action: int) -> dict:
        """Apply an action for the current player. Returns info dict."""
        if self.done:
            raise RuntimeError("game is over")

        decoded = decode_action(action)
        info = {"step": self.step_count, "player": self.current_player, **decoded}

        if decoded["type"] == "pass":
            self.consecutive_passes += 1
            self.move_log.append(info)
            if self.consecutive_passes >= 2:
                # Both players passed consecutively → DRAW (R15+ convention).
                self.done = True
                self.winner = None
                info["end_reason"] = "double_pass_draw"
            else:
                self._advance_turn()
            self.step_count += 1
            return info

        # Placement
        cell = decoded["cell"]
        phase = decoded["phase"]
        if self.board[cell] != EMPTY:
            raise ValueError(f"cell {cell} not empty (state {int(self.board[cell])})")
        if phase not in (1, -1):
            raise ValueError(f"phase must be 1 or -1, got {phase}")

        self.consecutive_passes = 0
        self.board[cell] = encode_state(self.current_player, phase)
        self.move_log.append(info)

        # Apply phase-aware outnumber capture across the board.
        captured = self._apply_captures()
        info["captured"] = captured

        # Check threshold win (margin-based, both players checked simultaneously).
        score_p1 = self.player_score(1)
        score_p2 = self.player_score(2)
        info["score_p1"] = score_p1
        info["score_p2"] = score_p2
        crossings = {}
        if score_p1 > WIN_THRESHOLD:
            crossings[1] = score_p1
        if score_p2 > WIN_THRESHOLD:
            crossings[2] = score_p2
        if len(crossings) == 2:
            # Both crossed same step → margin-based resolution (higher wins, tied = draw).
            if crossings[1] > crossings[2]:
                self.winner = 1
            elif crossings[2] > crossings[1]:
                self.winner = 2
            else:
                self.winner = None
            self.done = True
            info["end_reason"] = "both_threshold_margin"
        elif len(crossings) == 1:
            self.winner = next(iter(crossings))
            self.done = True
            info["end_reason"] = f"P{self.winner}_threshold"

        # Advance turn / check max turns
        if not self.done:
            self._advance_turn()
        self.step_count += 1
        if not self.done and self.step_count >= MAX_TURNS:
            # Max turns: piece-count majority (this is _end_by_max_turns equivalent).
            p1_pieces = int(np.sum((self.board == P1_POS) | (self.board == P1_NEG)))
            p2_pieces = int(np.sum((self.board == P2_POS) | (self.board == P2_NEG)))
            self.done = True
            if p1_pieces > p2_pieces:
                self.winner = 1
            elif p2_pieces > p1_pieces:
                self.winner = 2
            else:
                self.winner = None
            info["end_reason"] = "max_turns_majority"

        return info

    def _advance_turn(self) -> None:
        self.current_player = 3 - self.current_player

    def _apply_captures(self) -> list[int]:
        """Phase-aware outnumber capture, applied simultaneously.

        A stone at phase P is captured if:
          (count of opposite-phase neighbors) > (count of same-phase neighbors) + OUTNUMBER_THRESHOLD

        Note: this is purely PHASE-based, not owner-based. A P1 camouflage stone
        (P1@-1) is captured by phase-+1 neighbors regardless of who owns those
        +1 stones. This is the key dynamic — owners and phases are decoupled.

        All captures computed from the pre-capture board snapshot; applied
        simultaneously.
        """
        snapshot = self.board.copy()
        to_capture: list[int] = []
        for cell in range(TOTAL_CELLS):
            state = int(snapshot[cell])
            if state == EMPTY:
                continue
            phase = cell_phase(state)
            same = 0
            opp = 0
            for nbr in self.topo.get_neighbors(cell):
                nbr_state = int(snapshot[nbr])
                if nbr_state == EMPTY:
                    continue
                nbr_phase = cell_phase(nbr_state)
                if nbr_phase == phase:
                    same += 1
                else:
                    opp += 1
            if opp > same + OUTNUMBER_THRESHOLD:
                to_capture.append(cell)
        for cell in to_capture:
            self.board[cell] = EMPTY
        return to_capture

    # --- rendering ---

    def render(self) -> str:
        """ASCII render of the board."""
        symbols = {EMPTY: " . ", P1_POS: " A ", P1_NEG: " a ", P2_NEG: " B ", P2_POS: " b "}
        rows = []
        for y in range(AXIS_SIZE):
            row = "".join(symbols[int(self.board[y * AXIS_SIZE + x])] for x in range(AXIS_SIZE))
            rows.append(f"{y} | {row}")
        header = "    " + " ".join(f" {x} " for x in range(AXIS_SIZE))
        lines = [header, "    " + "---" * AXIS_SIZE] + rows
        lines.append("")
        lines.append(
            f"P1 score: {self.player_score(1):.3f}   P2 score: {self.player_score(2):.3f}   "
            f"threshold: {WIN_THRESHOLD:.3f}"
        )
        lines.append(
            f"step {self.step_count}   to-move: P{self.current_player}   "
            f"done: {self.done}   winner: {self.winner}"
        )
        lines.append("Legend: A=P1@+1 (natural)  a=P1@-1 (camo)  B=P2@-1 (natural)  b=P2@+1 (camo)")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Quick smoke test when run directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    g = PhaseGame(seed=0)
    # P1 places natural at (3,3)=27, +1
    g.step(encode_action(27, 1))
    # P2 places natural at (4,4)=36, -1
    g.step(encode_action(36, -1))
    # P1 places at (3,4)=35, +1
    g.step(encode_action(35, 1))
    # P2 places camouflage at (3,5)=43, +1 (camo!)
    g.step(encode_action(43, 1))
    print(g.render())
    print()
    print(f"Legal actions count: {len(g.get_legal_actions())}")
