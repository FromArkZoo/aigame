#!/usr/bin/env python3
"""Greedy player for fractal Pair A — both players play 1-ply lookahead.

Greedy: pick the legal move that maximizes (own_score - opp_score) after the move,
breaking ties randomly with a fixed seed.
"""
import json
import sys
import random
import copy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from game_engine.game_def_v2 import GameDefV2
from game_engine import factory


def scores(engine):
    p1 = sum(engine.board_values[c] for c in range(engine.total_cells)
             if engine.board_owners[c] == 1)
    p2 = -sum(engine.board_values[c] for c in range(engine.total_cells)
              if engine.board_owners[c] == 2)
    return p1, p2


def greedy_choice(game, engine, rng, lookahead=1):
    """Pick best move by 1-ply (score after move = own - opp from that player's view)."""
    legal = list(engine.get_legal_actions())
    me = engine.current_player
    best_val = -1e9
    best_actions = []
    for a in legal:
        e2 = copy.deepcopy(engine)
        e2.step(a)
        p1, p2 = scores(e2)
        if me == 1:
            val = p1 - p2
        else:
            val = p2 - p1
        if val > best_val + 1e-9:
            best_val = val
            best_actions = [a]
        elif val > best_val - 1e-9:
            best_actions.append(a)
    return rng.choice(best_actions)


def play(role: str, max_moves: int = 100, seed: int = 0, log_every: int = 1):
    path = ROOT / "experiments" / "fractal_spike" / "candidates" / f"frac_A_{role}.json"
    g = GameDefV2.from_dict(json.load(open(path)))
    e = factory.create_engine(g)
    e.reset()
    rng = random.Random(seed)
    moves_played = []
    for i in range(max_moves):
        if e.done:
            break
        a = greedy_choice(g, e, rng)
        player = e.current_player
        e.step(a)
        moves_played.append(a)
        if log_every and (i + 1) % log_every == 0:
            p1s, p2s = scores(e)
            size = g.axis_size
            coord = (a % size, a // size) if a != size * size else "PASS"
            print(f"[{i+1:3d}] P{player} -> {a} {coord}  P1={p1s:.2f} P2={p2s:.2f} pieces P1={e.piece_counts[0]} P2={e.piece_counts[1]} done={e.done}")
    p1s, p2s = scores(e)
    print()
    print(f"FINAL ({role}): P1={p1s:.3f} P2={p2s:.3f} threshold={g.win_condition.threshold:.3f}")
    print(f"Pieces P1={e.piece_counts[0]} P2={e.piece_counts[1]}  Done={e.done}  Winner={e._winner}")
    print(f"Moves played ({len(moves_played)}): {','.join(str(m) for m in moves_played)}")
    return moves_played, (p1s, p2s), e._winner, e.done


if __name__ == "__main__":
    role = sys.argv[1] if len(sys.argv) > 1 else "fractal"
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    play(role, seed=seed)
