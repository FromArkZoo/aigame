"""Team-12 helper — play a move sequence and show board values, owner, influence totals."""
import sys
import argparse
import numpy as np

sys.path.insert(0, '/Users/jamesbrowne/aigame')

from play_helper import load_game
from game_engine.factory import create_engine


def fmt_val(v):
    if abs(v) < 1e-9:
        return "  .   "
    return f"{v:+5.2f}"


def show(engine, game, last_move=None):
    axis = game.axis_size
    print(f"\nStep {engine.step_count}, next to play: P{engine.get_current_player()+1}")
    print(f"Pieces: P1={engine.piece_counts[0]}, P2={engine.piece_counts[1]}, consecutive_passes={engine.consecutive_passes}")
    if last_move is not None:
        if last_move == game.total_cells:
            print(f"Last move: PASS")
        else:
            x = last_move % axis
            y = last_move // axis
            print(f"Last move: action {last_move} = ({x},{y})")
    # Board with owners
    print("\nOwners:")
    print("    " + " ".join(f"{x:>2}" for x in range(axis)))
    for y in range(axis):
        row = []
        for x in range(axis):
            idx = y * axis + x
            o = engine.board_owners[idx]
            row.append("X" if o == 1 else ("O" if o == 2 else "."))
        print(f" {y}  " + "  ".join(row))
    # Board values
    print("\nBoard values (X=P1 positive, O=P2 negative):")
    print("       " + " ".join(f"{x:>6}" for x in range(axis)))
    for y in range(axis):
        row_vals = []
        for x in range(axis):
            idx = y * axis + x
            row_vals.append(fmt_val(engine.board_values[idx]))
        print(f" {y}   " + " ".join(row_vals))
    # Thresholds
    p1_val = sum(engine.board_values[c] for c in range(game.total_cells) if engine.board_owners[c] == 1)
    p2_val = -sum(engine.board_values[c] for c in range(game.total_cells) if engine.board_owners[c] == 2)
    thr = game.win_condition.threshold
    print(f"\nP1 sum on own cells: {p1_val:+.3f}  (threshold {thr:.3f})")
    print(f"P2 sum on own cells: {p2_val:+.3f}  (threshold {thr:.3f})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--moves", default="")
    ap.add_argument("--show-each", action="store_true")
    ap.add_argument("--final-only", action="store_true")
    args = ap.parse_args()
    g = load_game('genesis_v2_run14.db', '931c58ae59b4')
    e = create_engine(g)
    moves = []
    if args.moves.strip():
        moves = [int(x) for x in args.moves.split(",") if x.strip()]
    for i, m in enumerate(moves):
        legal = e.get_legal_actions()
        if m not in legal:
            print(f"ILLEGAL move {i+1}: action {m} not in legal list ({len(legal)} legal)")
            print("Legal (first 30):", legal[:30])
            sys.exit(1)
        obs, rew, done, info = e.step(m)
        if args.show_each and not args.final_only:
            show(e, g, last_move=m)
        if done:
            winner = info.get("winner")
            print(f"\n*** GAME OVER at move {i+1}: winner={'P'+str(winner+1) if winner is not None else 'Draw'} ***")
            break
    show(e, g, last_move=moves[-1] if moves else None)
    # Legal actions
    if not e.done:
        legal = e.get_legal_actions()
        placements = [a for a in legal if a < g.total_cells]
        print(f"\nLegal placements ({len(placements)}): {placements}")
        print(f"Pass action: {g.total_cells}")


if __name__ == "__main__":
    main()
