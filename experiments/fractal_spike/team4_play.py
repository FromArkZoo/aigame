#!/usr/bin/env python3
"""Helper for team-4 evaluation of Pair A.

Usage:
    .venv/bin/python experiments/fractal_spike/team4_play.py <fractal|control> <comma-separated-actions>

Example:
    .venv/bin/python experiments/fractal_spike/team4_play.py fractal 0,18,2,20,4,22
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from game_engine.game_def_v2 import GameDefV2
from game_engine import factory


def load_game(role: str):
    path = ROOT / "experiments" / "fractal_spike" / "candidates" / f"frac_A_{role}.json"
    g = GameDefV2.from_dict(json.load(open(path)))
    engine = factory.create_engine(g)
    engine.reset()
    return g, engine


def render(engine, game):
    topo = game.get_topology()
    size = game.axis_size
    has_holes = topo.num_active_cells < topo.total_cells
    rows = []
    rows.append("   " + " ".join(f"{c:>5}" for c in range(size)))
    for row in range(size):
        cells = []
        for col in range(size):
            idx = topo.coords_to_cell((col, row))
            if has_holes and not bool(topo.active_mask[idx]):
                cells.append("  #  ")
                continue
            owner = engine.board_owners[idx]
            val = engine.board_values[idx]
            if owner == 1:
                cells.append(f" X{val:+.2f}"[:5])
            elif owner == 2:
                cells.append(f" O{val:+.2f}"[:5])
            else:
                if abs(val) > 0.005:
                    cells.append(f"{val:+.2f}")
                else:
                    cells.append("  .  ")
        rows.append(f"{row:>2} " + " ".join(c.rjust(5) for c in cells))
    return "\n".join(rows)


def scores(engine):
    p1 = sum(engine.board_values[c] for c in range(engine.total_cells)
             if engine.board_owners[c] == 1)
    p2 = -sum(engine.board_values[c] for c in range(engine.total_cells)
              if engine.board_owners[c] == 2)
    return p1, p2


def main():
    role = sys.argv[1]
    moves = []
    if len(sys.argv) > 2 and sys.argv[2].strip():
        moves = [int(m) for m in sys.argv[2].split(",")]

    game, engine = load_game(role)
    print(f"=== {game.game_id} ===")
    print(f"Threshold: {game.win_condition.threshold:.3f}")
    print(f"Topology: {game.topology_type}, axis={game.axis_size}, active={game.get_topology().num_active_cells}")
    print()

    for i, mv in enumerate(moves):
        player = engine.current_player
        legal = engine.get_legal_actions()
        legal_set = set(legal)
        if mv not in legal_set:
            print(f"!! Move {i+1} action {mv} ILLEGAL for player {player}")
            print(f"   Legal: {sorted(legal_set)[:20]}...")
            return
        _, _, done, _ = engine.step(mv)
        size = game.axis_size
        coord = (mv % size, mv // size) if mv != size * size else "PASS"
        p1s, p2s = scores(engine)
        print(f"[{i+1:2d}] P{player} -> {mv} {coord}   P1_score={p1s:.2f}  P2_score={p2s:.2f}  done={done}  pieces P1={engine.piece_counts[0]} P2={engine.piece_counts[1]}")
        if done:
            print(f"  WINNER: {engine.winner}")
            break

    print()
    print("Board (cell = '.X.' for player; 'X' or 'O' indicates owner; influence shown as +/-):")
    print(render(engine, game))
    p1s, p2s = scores(engine)
    print(f"\nFinal: P1 effective = {p1s:.3f}, P2 effective = {p2s:.3f} (threshold {game.win_condition.threshold:.3f})")
    print(f"Pieces P1={engine.piece_counts[0]} P2={engine.piece_counts[1]}")
    print(f"Done={engine.done}, winner={engine.winner if engine.done else '-'}")
    print(f"Current player: {engine.current_player if not engine.done else '-'}")
    if not engine.done:
        legal = engine.get_legal_actions()
        # Only show non-pass actions count
        size = game.axis_size
        non_pass = [a for a in legal if a != size * size]
        print(f"Legal actions remaining: {len(legal)} ({len(non_pass)} placement)")


if __name__ == "__main__":
    main()
