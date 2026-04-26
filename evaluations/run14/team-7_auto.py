"""Team-7 auto-play: greedy lookahead-1 for both players.

Greedy: each player maximizes (own_influence_total) after their move.
Optionally with spoiler bias (weight to minimize opponent too).
"""
import json, sqlite3, sys, os
sys.path.insert(0, '/Users/jamesbrowne/aigame')
os.chdir('/Users/jamesbrowne/aigame')
from game_engine.game_def_v2 import GameDefV2
from game_engine.factory import create_engine


def load():
    conn = sqlite3.connect('/Users/jamesbrowne/aigame/genesis_v2_run14.db')
    row = conn.execute("SELECT rule_representation FROM games WHERE game_id = ?", ('1ca924cc3062',)).fetchone()
    conn.close()
    return GameDefV2.from_dict(json.loads(row[0]))


def snap(engine):
    return {
        'bo': engine.board_owners.copy(),
        'bv': engine.board_values.copy(),
        'pc': engine.piece_counts[:],
        'cp': engine.current_player,
        'done': engine.done,
        'win': engine._winner,
        'cpass': engine.consecutive_passes,
        'placements': getattr(engine, 'placements_this_turn', 0),
        'step_count': engine.step_count,
        'pos_hist': engine._position_history.copy() if hasattr(engine, '_position_history') else set(),
    }


def rest(engine, s):
    engine.board_owners[:] = s['bo']
    engine.board_values[:] = s['bv']
    engine.piece_counts = s['pc']
    engine.current_player = s['cp']
    engine.done = s['done']
    engine._winner = s['win']
    engine.consecutive_passes = s['cpass']
    if hasattr(engine, 'placements_this_turn'):
        engine.placements_this_turn = s['placements']
    engine.step_count = s['step_count']
    if hasattr(engine, '_position_history'):
        engine._position_history = s['pos_hist']


def best_move(engine, player, spoiler_weight=0.0):
    """Return (action, score) of best greedy move for `player`.

    score = own_total - spoiler_weight * opponent_total (after move).
    Immediate-win moves always preferred.
    """
    legal = engine.get_legal_actions()
    best = None
    best_score = -1e18
    for c in legal:
        if c == 64:  # never consider pass in greedy
            continue
        s = snap(engine)
        try:
            engine.step(c)
        except Exception:
            rest(engine, s)
            continue
        if engine.done and engine._winner == player:
            rest(engine, s)
            return c, 1e9
        p1 = sum(engine.board_values[cc] for cc in range(64) if engine.board_owners[cc] == 1)
        p2 = -sum(engine.board_values[cc] for cc in range(64) if engine.board_owners[cc] == 2)
        own, opp = (p1, p2) if player == 1 else (p2, p1)
        score = own - spoiler_weight * opp
        if score > best_score:
            best_score = score
            best = c
        rest(engine, s)
    return best, best_score


def run(initial_moves, p1_spoiler=0.0, p2_spoiler=0.0, max_moves=200, verbose=True):
    game = load()
    engine = create_engine(game)
    moves_taken = list(initial_moves)
    for m in initial_moves:
        engine.step(m)
    while not engine.done and len(moves_taken) < max_moves:
        player = engine.current_player
        sw = p1_spoiler if player == 1 else p2_spoiler
        m, score = best_move(engine, player, sw)
        if m is None:
            break
        engine.step(m)
        moves_taken.append(m)
        if verbose:
            p1 = sum(engine.board_values[cc] for cc in range(64) if engine.board_owners[cc] == 1)
            p2 = -sum(engine.board_values[cc] for cc in range(64) if engine.board_owners[cc] == 2)
            print(f"Move {len(moves_taken)} P{player} plays {m} ({m%8},{m//8}) | P1={p1:.2f} P2={p2:.2f} | done={engine.done} win={engine._winner}")
    p1 = sum(engine.board_values[cc] for cc in range(64) if engine.board_owners[cc] == 1)
    p2 = -sum(engine.board_values[cc] for cc in range(64) if engine.board_owners[cc] == 2)
    print(f"\n=== FINAL: moves={len(moves_taken)}, P1={p1:.3f}, P2={p2:.3f}, done={engine.done}, winner={engine._winner} ===")
    print(f"move_list = {moves_taken}")
    return moves_taken, engine


if __name__ == '__main__':
    # args: init_moves | p1_spoiler | p2_spoiler
    init = [int(x) for x in sys.argv[1].split(',') if x.strip()] if len(sys.argv) > 1 and sys.argv[1] else []
    p1_sw = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    p2_sw = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    run(init, p1_sw, p2_sw)
