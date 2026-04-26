"""Team-9 helper for game d8f2ae54f399 — runs a move sequence and prints
the effective-value sums after each move, plus final board."""
import sys, json, sqlite3
sys.path.insert(0, '.')
from game_engine.game_def_v2 import GameDefV2
from game_engine.factory import create_engine

def play(moves, verbose=False):
    conn = sqlite3.connect('genesis_v2_run15.db')
    row = conn.execute('SELECT rule_representation FROM games WHERE game_id = ?', ('d8f2ae54f399',)).fetchone()
    rules = json.loads(row[0])
    game = GameDefV2.from_dict(rules)
    engine = create_engine(game)
    engine.reset()
    thr = 22.6453
    for i, m in enumerate(moves):
        legal = engine.get_legal_actions()
        player = engine.get_current_player()
        if m not in legal:
            print(f'MOVE {i+1} player {player} action {m} ILLEGAL. Legal sample:', legal[:10])
            return
        engine.step(m)
        p1_eff = sum(engine.board_values[c] for c in range(64) if engine.board_owners[c] == 1)
        p2_eff = -sum(engine.board_values[c] for c in range(64) if engine.board_owners[c] == 2)
        x = m % 8; y = m // 8
        note = ''
        if m == 64: note = 'PASS'
        if verbose or i >= len(moves) - 3:
            print(f'Move {i+1}: P{player} -> action {m} ({x},{y}) {note}  P1_eff={p1_eff:.2f} P2_eff={p2_eff:.2f} pieces P1={engine.piece_counts[0]} P2={engine.piece_counts[1]}')
        if engine.done:
            print(f'*** GAME OVER after {i+1} moves. Winner: {engine._winner}')
            break
    # Final board render
    print()
    print('Final board (owners):')
    for y in range(8):
        row_str = ''
        for x in range(8):
            o = engine.board_owners[y*8+x]
            row_str += {0:'.',1:'X',2:'O'}[int(o)] + ' '
        print(f' {y} {row_str}')
    print()
    print('Final values:')
    for y in range(8):
        row_str = ''
        for x in range(8):
            v = engine.board_values[y*8+x]
            row_str += f'{v:+5.2f} '
        print(f' {y} {row_str}')
    p1_eff = sum(engine.board_values[c] for c in range(64) if engine.board_owners[c] == 1)
    p2_eff = -sum(engine.board_values[c] for c in range(64) if engine.board_owners[c] == 2)
    print(f'P1 effective: {p1_eff:.3f}  P2 effective: {p2_eff:.3f}  Threshold: {thr}')
    print(f'Done={engine.done} Winner={engine._winner}')
    return engine

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: team9_play.py "m1,m2,m3,..."')
        sys.exit(1)
    moves = [int(x) for x in sys.argv[1].split(',')]
    play(moves, verbose=True)
