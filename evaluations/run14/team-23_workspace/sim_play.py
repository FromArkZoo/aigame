"""Simultaneous play driver for game 992bf7dfc9f4.

Usage:
    .venv/bin/python sim_play.py --moves "p1a:p2a,p1b:p2b,..."

Each comma-separated pair is one simultaneous round; within a pair,
"p1:p2" are the action IDs for Player 1 and Player 2 respectively.
Use "P" for pass (action 64).

Prints board, legal actions, win state after each round.
"""
import argparse, sys, os
sys.path.insert(0, "/Users/jamesbrowne/aigame")

from game_engine.game_def_v2 import GameDefV2
from game_engine.factory import create_engine
import sqlite3, json
import numpy as np

DB = "/Users/jamesbrowne/aigame/genesis_v2_run14.db"
GID = "992bf7dfc9f4"


def load():
    conn = sqlite3.connect(DB)
    row = conn.execute("SELECT rule_representation FROM games WHERE game_id=?", (GID,)).fetchone()
    conn.close()
    return GameDefV2.from_dict(json.loads(row[0]))


def render(engine, game):
    size = game.axis_size
    topo = game.get_topology()
    lines = [f"  P1=X  P2=O  .=empty"]
    lines.append("    " + " ".join(f"{c:>2}" for c in range(size)))
    for row in range(size):
        cells = []
        for col in range(size):
            idx = topo.coords_to_cell((col, row))
            o = engine.board_owners[idx]
            cells.append(" X" if o == 1 else (" O" if o == 2 else " ."))
        lines.append(f"{row:>2}  " + "".join(cells))
    return "\n".join(lines)


def parse_action(s, game):
    s = s.strip().upper()
    if s == "P":
        return game.total_cells  # pass
    return int(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--moves", default="")
    ap.add_argument("--no-render-each", action="store_true")
    ap.add_argument("--final-only", action="store_true")
    args = ap.parse_args()

    game = load()
    engine = create_engine(game)
    engine.reset()
    print(f"Game {GID}: {game.axis_size}x{game.axis_size} grid, simultaneous, territory threshold {game.win_condition.threshold:.4f} ({game.win_condition.threshold * game.total_cells:.2f}/{game.total_cells} cells), max_turns={game.win_condition.max_turns}")
    print(render(engine, game))
    print(f"  P1={engine.piece_counts[0]} P2={engine.piece_counts[1]}")

    if not args.moves.strip():
        # Show legal for both
        legal_p1 = engine.get_legal_actions(1)
        legal_p2 = engine.get_legal_actions(2)
        print(f"\nP1 legal ({len(legal_p1)}): {legal_p1}")
        print(f"P2 legal ({len(legal_p2)}): {legal_p2}")
        return

    pairs = [p.strip() for p in args.moves.split(",") if p.strip()]
    collisions = 0
    for i, pair in enumerate(pairs):
        if ":" not in pair:
            print(f"Malformed pair {pair!r}; expected 'p1:p2'")
            sys.exit(1)
        a, b = pair.split(":")
        ap1 = parse_action(a, game)
        ap2 = parse_action(b, game)

        legal_p1 = engine.get_legal_actions(1)
        legal_p2 = engine.get_legal_actions(2)

        illegal = []
        if ap1 not in legal_p1:
            illegal.append(f"P1 action {ap1} illegal (legal: {legal_p1[:15]}{'...' if len(legal_p1)>15 else ''})")
        if ap2 not in legal_p2:
            illegal.append(f"P2 action {ap2} illegal (legal: {legal_p2[:15]}{'...' if len(legal_p2)>15 else ''})")
        if illegal:
            print(f"\n--- Round {i+1}: P1={ap1}, P2={ap2} ---")
            for e in illegal:
                print("  ", e)
            sys.exit(2)

        obs, rewards, done, info = engine.step_simultaneous(ap1, ap2)
        if info.get("collision"):
            collisions += 1
        if not args.final_only:
            print(f"\n--- Round {i+1}: P1={ap1}, P2={ap2}{'  COLLISION!' if info.get('collision') else ''} ---")
            print(render(engine, game))
            print(f"  P1={engine.piece_counts[0]} P2={engine.piece_counts[1]}  step={engine.step_count}  done={done}  winner={info.get('winner')}  collisions_so_far={collisions}")
        if done:
            print(f"\n*** GAME OVER after round {i+1}: winner={info.get('winner')} (0=P1,1=P2,None=draw)  rewards={rewards.tolist()}  total collisions: {collisions} ***")
            break
    else:
        # Loop finished without done
        print(f"\n--- After {len(pairs)} rounds, game continuing ---")
        print(render(engine, game))
        print(f"  P1={engine.piece_counts[0]} P2={engine.piece_counts[1]}  step={engine.step_count}  collisions: {collisions}")
        legal_p1 = engine.get_legal_actions(1)
        legal_p2 = engine.get_legal_actions(2)
        print(f"P1 legal ({len(legal_p1)}): {legal_p1}")
        print(f"P2 legal ({len(legal_p2)}): {legal_p2}")


if __name__ == "__main__":
    main()
