"""Team-5 evaluation helper: simulate sequences, display board values and piece totals."""
import sys
import sqlite3
import json
from game_engine.game_def_v2 import GameDefV2
from game_engine.factory import create_engine


def load_game(game_id, db="genesis_v2_run14.db"):
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT rule_representation FROM games WHERE game_id = ?", (game_id,)).fetchone()
    conn.close()
    rules = json.loads(row["rule_representation"])
    return GameDefV2.from_dict(rules)


def fmt_board(eng, game):
    topo = game.get_topology()
    axis = game.axis_size
    lines = []
    header = "       " + " ".join(f"{x:>7d}" for x in range(axis))
    lines.append(header)
    for y in range(axis):
        row = [f"y={y:2d}  "]
        for x in range(axis):
            cell = topo.coords_to_cell((x, y))
            owner = int(eng.board_owners[cell])
            val = float(eng.board_values[cell])
            mark = "." if owner == 0 else ("X" if owner == 1 else "O")
            row.append(f"{mark}{val:+5.2f}")
        lines.append(" ".join(row))
    return "\n".join(lines)


def run(game_id, moves):
    game = load_game(game_id)
    eng = create_engine(game)
    for mv in moves:
        legal = eng.get_legal_actions()
        if mv not in legal:
            print(f"ILLEGAL MOVE {mv}; current_player={eng.current_player}")
            print(fmt_board(eng, game))
            return eng, game
        eng.step(mv)
        if eng.done:
            break
    return eng, game


def summarize(eng, game):
    topo = game.get_topology()
    print(fmt_board(eng, game))
    print(f"\nPieces: P1={eng.piece_counts[0]}, P2={eng.piece_counts[1]}")
    for p in (1, 2):
        total = sum(eng.board_values[c] for c in range(eng.total_cells) if eng.board_owners[c] == p)
        eff = total if p == 1 else -total
        print(f"P{p} effective threshold value: {eff:.3f}")
    print(f"Threshold: {game.win_condition.threshold:.3f}")
    print(f"Turn: {eng.current_player}, Steps played: {eng.step_count}")
    print(f"Done: {eng.done}, Winner: {eng._winner}")
    print(f"Consecutive passes: {eng.consecutive_passes}")


if __name__ == "__main__":
    game_id = sys.argv[1]
    moves = [int(x) for x in sys.argv[2].split(",") if x.strip()] if len(sys.argv) > 2 and sys.argv[2] else []
    eng, game = run(game_id, moves)
    summarize(eng, game)
