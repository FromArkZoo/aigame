"""4-Phase complex extension of c6bb58075520 — Round 3 of the phase spike.

The Round 1+2 binary {+1, -1} design failed because phase -1 always radiated
enemy-aligned influence into the placer's own neighborhood. Mean post-fix
score: 3.5/10 vs source 4.40/10.

This v2 escalates to true complex / 4-phase mechanics. Phases are at the four
unit-circle quadrants {0°, 90°, 180°, 270°} (compass directions N, E, S, W).

KEY INSIGHT: phases 90° (E) and 270° (W) are orthogonal to both players'
score axes (P1 target = 0° = N, P2 target = 180° = S). Stones at E/W
contribute ZERO to both scores AND are capture-immune to N/S attackers
(cos(90°) = 0). They're true neutral occupiers — the strategic primitive
the binary design couldn't produce.

CELL STATES (9 values):
  0 = empty
  1 = P1@N (0°)    "A^"  — P1's primary attack
  2 = P1@E (90°)   "A>"  — P1 neutral occupier
  3 = P1@S (180°)  "Av"  — P1 anti-stone (helps enemy; rarely rational)
  4 = P1@W (270°)  "A<"  — P1 neutral occupier
  5 = P2@N (0°)    "B^"  — P2 anti-stone
  6 = P2@E (90°)   "B>"  — P2 neutral occupier
  7 = P2@S (180°)  "Bv"  — P2's primary attack
  8 = P2@W (270°)  "B<"  — P2 neutral occupier

INFLUENCE: each stone projects a 2D vector
    (cos(phase), sin(phase)) × strength × decay^distance
to itself and to radius-1 neighbors. Cell vec is the sum of all projections.

SCORE: player p's score = Σ over p-owned cells of dot(cell_vec, target_unit)
where target_unit = (1, 0) for P1 (0°) or (-1, 0) for P2 (180°).

CAPTURE: stone at phase P dies if
    Σ over occupied neighbors of (-cos(P - neighbor_phase)) > threshold
This generalizes outnumber-by-anti-aligned-phase. Self-aligned (same phase)
contributes -1 (protective); orthogonal contributes 0; anti-aligned (180°
apart) contributes +1 (lethal).

Phases 90° vs 0°/180° = orthogonal → no capture interaction → real blocker.
Phases 90° vs 270° = anti-aligned → mutual capture → secondary axis.

ACTION ENCODING: action = cell * 4 + phase_idx where phase_idx ∈ {0,1,2,3}
    representing N, E, S, W. Pass action = TOTAL_CELLS * 4.
"""

from __future__ import annotations

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import math
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
CAPTURE_THRESHOLD = 2  # stone dies if Σ -cos(P - N_phase) > this
WIN_THRESHOLD = 22.645289471714786
MAX_TURNS = 100

# Phase indexing: 0=N(0°), 1=E(90°), 2=S(180°), 3=W(270°)
PHASE_NAMES = ("N", "E", "S", "W")
PHASE_ANGLES = (0.0, math.pi / 2, math.pi, 3 * math.pi / 2)
# Precompute phase unit vectors
PHASE_VECS = tuple((math.cos(a), math.sin(a)) for a in PHASE_ANGLES)
# (1, 0), (0, 1), (-1, 0), (0, -1)

# Cell state codes
EMPTY = 0
# P1 phases at codes 1-4 (P1@N, P1@E, P1@S, P1@W)
# P2 phases at codes 5-8 (P2@N, P2@E, P2@S, P2@W)


def cell_owner(state: int) -> int:
    if state == EMPTY:
        return 0
    return 1 if 1 <= state <= 4 else 2


def cell_phase_idx(state: int) -> int:
    """Returns the phase index 0-3 (N, E, S, W) of an occupied cell. -1 for empty."""
    if state == EMPTY:
        return -1
    return (state - 1) % 4


def cell_phase_angle(state: int) -> float:
    return PHASE_ANGLES[cell_phase_idx(state)]


def encode_state(owner: int, phase_idx: int) -> int:
    if owner not in (1, 2) or phase_idx not in (0, 1, 2, 3):
        raise ValueError(f"invalid owner={owner} phase_idx={phase_idx}")
    return (owner - 1) * 4 + phase_idx + 1


PASS_ACTION = TOTAL_CELLS * 4  # 256


def decode_action(action: int) -> dict:
    if action == PASS_ACTION:
        return {"type": "pass"}
    if not 0 <= action < TOTAL_CELLS * 4:
        raise ValueError(f"action {action} out of range")
    cell = action // 4
    phase_idx = action % 4
    return {"type": "place", "cell": cell, "phase_idx": phase_idx,
            "phase_name": PHASE_NAMES[phase_idx]}


def encode_action(cell: int, phase_idx: int) -> int:
    if not 0 <= cell < TOTAL_CELLS:
        raise ValueError(f"cell {cell} out of range")
    if phase_idx not in (0, 1, 2, 3):
        raise ValueError(f"phase_idx must be 0-3, got {phase_idx}")
    return cell * 4 + phase_idx


def parse_phase_letter(letter: str) -> int:
    letter = letter.upper().strip()
    if letter not in PHASE_NAMES:
        raise ValueError(f"phase must be N/E/S/W, got {letter!r}")
    return PHASE_NAMES.index(letter)


# ---------------------------------------------------------------------------
# Game engine
# ---------------------------------------------------------------------------

class PhaseGameV2:
    """Standalone 4-phase complex game engine."""

    def __init__(self, seed: int | None = None):
        self.topo = TopologicalSpace(2, AXIS_SIZE, "torus")
        self.board = np.zeros(TOTAL_CELLS, dtype=np.int8)
        self.current_player = 1
        self.step_count = 0
        self.consecutive_passes = 0
        self.done = False
        self.winner: int | None = None
        self.move_log: list[dict] = []
        self.rng = np.random.default_rng(seed)

    # --- queries ---

    def get_legal_actions(self) -> list[int]:
        if self.done:
            return []
        actions = []
        for cell in range(TOTAL_CELLS):
            if self.board[cell] == EMPTY:
                for p in range(4):
                    actions.append(encode_action(cell, p))
        actions.append(PASS_ACTION)
        return actions

    def board_vectors(self) -> np.ndarray:
        """Vector-valued influence field. Returns shape (TOTAL_CELLS, 2)."""
        vecs = np.zeros((TOTAL_CELLS, 2), dtype=np.float64)
        for cell in range(TOTAL_CELLS):
            state = int(self.board[cell])
            if state == EMPTY:
                continue
            p_idx = cell_phase_idx(state)
            vec = PHASE_VECS[p_idx]
            # Self-contribution
            vecs[cell, 0] += vec[0] * INFLUENCE_STRENGTH
            vecs[cell, 1] += vec[1] * INFLUENCE_STRENGTH
            # Neighbor contributions (radius 1)
            for nbr in self.topo.get_neighbors(cell):
                vecs[nbr, 0] += vec[0] * INFLUENCE_STRENGTH * INFLUENCE_DECAY
                vecs[nbr, 1] += vec[1] * INFLUENCE_STRENGTH * INFLUENCE_DECAY
        return vecs

    def player_score(self, player: int) -> float:
        """Player score = sum over owned cells of dot(cell_vec, target_unit).

        P1 target = N (1, 0). P2 target = S (-1, 0).
        """
        target = np.array([1.0, 0.0]) if player == 1 else np.array([-1.0, 0.0])
        vecs = self.board_vectors()
        total = 0.0
        for cell in range(TOTAL_CELLS):
            state = int(self.board[cell])
            if cell_owner(state) != player:
                continue
            total += float(vecs[cell, 0] * target[0] + vecs[cell, 1] * target[1])
        return total

    # --- mutation ---

    def step(self, action: int) -> dict:
        if self.done:
            raise RuntimeError("game is over")

        decoded = decode_action(action)
        info = {"step": self.step_count, "player": self.current_player, **decoded}

        if decoded["type"] == "pass":
            self.consecutive_passes += 1
            self.move_log.append(info)
            if self.consecutive_passes >= 2:
                self.done = True
                self.winner = None
                info["end_reason"] = "double_pass_draw"
            else:
                self._advance_turn()
            self.step_count += 1
            return info

        cell = decoded["cell"]
        phase_idx = decoded["phase_idx"]
        if self.board[cell] != EMPTY:
            raise ValueError(f"cell {cell} not empty (state {int(self.board[cell])})")

        self.consecutive_passes = 0
        self.board[cell] = encode_state(self.current_player, phase_idx)
        self.move_log.append(info)

        captured = self._apply_captures()
        info["captured"] = captured

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

        if not self.done:
            self._advance_turn()
        self.step_count += 1
        if not self.done and self.step_count >= MAX_TURNS:
            p1_pieces = int(np.sum((self.board >= 1) & (self.board <= 4)))
            p2_pieces = int(np.sum((self.board >= 5) & (self.board <= 8)))
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
        """Phase-aware capture: stone at phase P dies if
            Σ over occupied neighbors of (-cos(P - N_phase)) > CAPTURE_THRESHOLD.
        Same phase neighbor: -1 (protective); orthogonal: 0; anti-aligned: +1.
        Owner is irrelevant — purely phase-based.
        """
        snapshot = self.board.copy()
        to_capture: list[int] = []
        for cell in range(TOTAL_CELLS):
            state = int(snapshot[cell])
            if state == EMPTY:
                continue
            p_angle = cell_phase_angle(state)
            score = 0.0
            for nbr in self.topo.get_neighbors(cell):
                nbr_state = int(snapshot[nbr])
                if nbr_state == EMPTY:
                    continue
                n_angle = cell_phase_angle(nbr_state)
                score += -math.cos(p_angle - n_angle)
            if score > CAPTURE_THRESHOLD:
                to_capture.append(cell)
        for cell in to_capture:
            self.board[cell] = EMPTY
        return to_capture

    # --- rendering ---

    def render(self) -> str:
        symbols = {
            EMPTY: " . ",
            1: " A^",  # P1@N
            2: " A>",  # P1@E
            3: " Av",  # P1@S
            4: " A<",  # P1@W
            5: " B^",  # P2@N
            6: " B>",  # P2@E
            7: " Bv",  # P2@S
            8: " B<",  # P2@W
        }
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
        lines.append(
            "Phases: N=0° (P1's target), E=90°, S=180° (P2's target), W=270°. "
            "E/W are orthogonal to score axis; N/S compete on score."
        )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Quick smoke test when run directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    g = PhaseGameV2(seed=0)
    # P1 places primary at (3,3)=27, N
    g.step(encode_action(27, 0))  # P1@N
    # P2 places primary at (4,4)=36, S
    g.step(encode_action(36, 2))  # P2@S
    # P1 places neutral at (3,4)=35, E
    g.step(encode_action(35, 1))  # P1@E
    # P2 places neutral at (4,3)=28, W
    g.step(encode_action(28, 3))  # P2@W
    print(g.render())
    print()
    print(f"Legal actions count: {len(g.get_legal_actions())}")

    # Quick 50-game random probe
    print()
    print("=== 50-game random probe ===")
    results = {1: 0, 2: 0, None: 0}
    avg_steps = 0
    for seed in range(50):
        g2 = PhaseGameV2(seed=seed)
        while not g2.done:
            actions = g2.get_legal_actions()
            a = int(g2.rng.choice(actions))
            g2.step(a)
        results[g2.winner] += 1
        avg_steps += g2.step_count
    print(f"P1={results[1]}, P2={results[2]}, draws={results[None]}, avg steps={avg_steps/50:.1f}")
