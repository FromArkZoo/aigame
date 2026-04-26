"""Quick helper for team-20 to step through a game and print status."""
from game_engine.game_def_v2 import GameDefV2
from game_engine.factory import create_engine
import sqlite3, json, sys

GAME_ID = "4d9c5796dd18"
DB = "genesis_v2_run16.db"

def load():
    conn = sqlite3.connect(DB)
    row = conn.execute("SELECT rule_representation FROM games WHERE game_id = ?", (GAME_ID,)).fetchone()
    return GameDefV2.from_dict(json.loads(row[0]))

def play_moves(moves):
    game = load()
    engine = create_engine(game)
    engine.reset()
    topo = game.get_topology()
    rows = []
    for i, m in enumerate(moves):
        if engine.done:
            print(f"  [game already over before move {i}]")
            break
        if isinstance(m, tuple):
            a = topo.coords_to_cell(m)
        else:
            a = m
        legal = engine.get_legal_actions()
        if a not in legal:
            print(f"  ILLEGAL move {m} (action {a}); legal={legal[:10]}...")
            return engine
        cur = engine.current_player
        engine.step(a)
        p1s = sum(engine.board_values[c] for c in range(64) if engine.board_owners[c]==1)
        p2s = -sum(engine.board_values[c] for c in range(64) if engine.board_owners[c]==2)
        coord = topo.cell_to_coords(a) if a != 64 else "PASS"
        print(f"  Move {i+1} P{cur}: {coord} (a={a})  P1score={p1s:.2f}  P2score={p2s:.2f}  pieces=({engine.piece_counts[0]},{engine.piece_counts[1]})  done={engine.done} winner={engine._winner}")
    return engine

def show(engine):
    game = engine.game
    topo = game.get_topology()
    size = game.axis_size
    print("   " + " ".join(f"{c:>2}" for c in range(size)))
    for r in range(size):
        s = f"{r:>2} "
        for c in range(size):
            o = engine.board_owners[topo.coords_to_cell((c,r))]
            s += " X" if o==1 else (" O" if o==2 else " .")
        print(s)
    print("Influence:")
    for r in range(size):
        s = f"{r:>2} "
        for c in range(size):
            v = engine.board_values[topo.coords_to_cell((c,r))]
            s += f"{v:6.2f}"
        print(s)
    p1s = sum(engine.board_values[c] for c in range(64) if engine.board_owners[c]==1)
    p2s = -sum(engine.board_values[c] for c in range(64) if engine.board_owners[c]==2)
    print(f"P1 own-cell sum: {p1s:.3f}   P2 own-cell sum: {p2s:.3f}   threshold=50.508")

if __name__ == "__main__":
    # parse moves from CLI: as comma-sep "x,y;x,y;..." or action ids
    moves = []
    for tok in sys.argv[1:]:
        if "," in tok:
            x,y = tok.split(",")
            moves.append((int(x), int(y)))
        else:
            moves.append(int(tok))
    e = play_moves(moves)
    print()
    show(e)
