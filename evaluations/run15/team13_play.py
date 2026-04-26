"""team-13 play harness for 3bde3258978e.
Uses heuristic agents; dumps full move history and final field summary."""
import sqlite3, json, sys, os
sys.path.insert(0, '/Users/jamesbrowne/aigame')
os.chdir('/Users/jamesbrowne/aigame')
from game_engine.game_def_v2 import GameDefV2
from game_engine.factory import create_engine
import numpy as np

AXIS = 8
THRESH = 22.645289471714786
DB = 'genesis_v2_run15.db'
GID = '3bde3258978e'

def load():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('SELECT rule_representation FROM games WHERE game_id=?', (GID,))
    rules = json.loads(cur.fetchone()[0])
    return GameDefV2.from_dict(rules)

def fresh():
    e = create_engine(load())
    e.reset()
    return e

def yx(a):
    return a // AXIS, a % AXIS  # y, x

def a_of(y,x):
    return y*AXIS + x

def effective(engine, player):
    total = 0.0
    for c in range(64):
        if engine.board_owners[c] == player:
            total += engine.board_values[c]
    return total if player==1 else -total

def simulate_and_score(engine, move, player):
    """Clone, apply move, return (eff_self, eff_opp, legal?) — None if illegal."""
    legal = engine.get_legal_actions()
    if move not in legal:
        return None
    clone = engine.clone()
    clone.step(move)
    return effective(clone, player), effective(clone, 3-player)

def choose_greedy(engine, player, avoid_pass=True):
    legal = engine.get_legal_actions()
    if avoid_pass and len(legal) > 1 and 64 in legal:
        legal = [a for a in legal if a != 64]
    best = None
    best_score = -1e9
    for a in legal:
        res = simulate_and_score(engine, a, player)
        if res is None: continue
        eff_self, eff_opp = res
        # Score: prioritize own threshold progress, secondarily reduce opponent
        score = eff_self - 0.4 * eff_opp
        # Slight central bias tiebreaker
        if a != 64:
            y,x = yx(a)
            center_bonus = -(abs(y-3.5)+abs(x-3.5))*0.01
            score += center_bonus
        if score > best_score:
            best_score = score
            best = a
    return best

def choose_defensive(engine, player):
    """Aggressively block opponent threshold growth (heavy opp-penalty)."""
    legal = engine.get_legal_actions()
    if len(legal)>1 and 64 in legal: legal = [a for a in legal if a!=64]
    best = None; best_score=-1e9
    for a in legal:
        res = simulate_and_score(engine, a, player)
        if res is None: continue
        eff_self, eff_opp = res
        score = eff_self*0.3 - eff_opp*1.5
        if a != 64:
            y,x = yx(a)
            score += -(abs(y-3.5)+abs(x-3.5))*0.01
        if score > best_score:
            best_score = score; best=a
    return best

def choose_cluster_region(engine, player, cy, cx):
    """Prefer moves clustered around (cy,cx), tiebroken by influence gain."""
    legal = engine.get_legal_actions()
    if len(legal)>1 and 64 in legal: legal = [a for a in legal if a!=64]
    best = None; best_score=-1e9
    for a in legal:
        res = simulate_and_score(engine, a, player)
        if res is None: continue
        eff_self, eff_opp = res
        y,x = yx(a) if a != 64 else (0,0)
        dist_bonus = -(abs(y-cy)+abs(x-cx))*0.5
        score = eff_self*1.0 - eff_opp*0.3 + dist_bonus
        if score > best_score:
            best_score = score; best=a
    return best

def p2_cluster_opposite(engine, player):
    # P2 clusters in bottom-right quadrant (5,5) to avoid P1's center dominance
    return choose_cluster_region(engine, player, 5, 5)

def p1_cluster_center(engine, player):
    return choose_cluster_region(engine, player, 3, 3)

def play_game(p1_fn, p2_fn, max_moves=200, label='game', verbose=True):
    engine = fresh()
    hist = []
    for t in range(max_moves):
        if engine.done: break
        seat = engine.current_player  # 1 or 2
        fn = p1_fn if seat==1 else p2_fn
        move = fn(engine, seat)
        eff1 = effective(engine, 1)
        eff2 = effective(engine, 2)
        if verbose:
            y,x = yx(move) if move != 64 else ('-','-')
            print(f'  t{t} seat{seat} -> act {move} (y={y},x={x}) | pre-move eff P1={eff1:.2f} P2={eff2:.2f} | legal={len(engine.get_legal_actions())}')
        engine.step(move)
        hist.append((seat, move))
    eff1 = effective(engine, 1); eff2 = effective(engine, 2)
    print(f'\n{label} RESULT: winner={engine._winner}, moves={len(hist)}, P1 pieces={engine.piece_counts[0]}, P2 pieces={engine.piece_counts[1]}, final eff P1={eff1:.2f} P2={eff2:.2f}')
    print('Final board:')
    b = engine.board_owners.reshape(8,8)
    for row in b:
        print(' '.join('X' if v==1 else 'O' if v==2 else '.' for v in row))
    print('Final values:')
    v = engine.board_values.reshape(8,8)
    for row in v:
        print(' '.join(f'{x:+.2f}' for x in row))
    return engine, hist

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv)>1 else 'g1'
    if mode == 'g1':
        print('=== GAME 1: P1=greedy, P2=greedy ===')
        play_game(choose_greedy, choose_greedy, label='G1')
    elif mode == 'g2':
        print('=== GAME 2: P1=cluster-center, P2=cluster-opposite ===')
        play_game(p1_cluster_center, p2_cluster_opposite, label='G2')
    elif mode == 'g3':
        print('=== GAME 3 (seat swap): P1=cluster-opposite, P2=cluster-center (was P1 strategy) ===')
        play_game(p2_cluster_opposite, p1_cluster_center, label='G3')
    elif mode == 'g4':
        print('=== GAME 4: P1=defensive, P2=greedy ===')
        play_game(choose_defensive, choose_greedy, label='G4')
    elif mode == 'g5':
        print('=== GAME 5: P1=cluster-center, P2=defensive (blocks P1) ===')
        play_game(p1_cluster_center, choose_defensive, label='G5')
    elif mode == 'g6':
        print('=== GAME 6: P1=cluster-center(3,3), P2=adjacent-block (clusters at 3,4 to touch P1) ===')
        play_game(p1_cluster_center, lambda e,p: choose_cluster_region(e,p,3,4), label='G6')
    elif mode == 'g7':
        # Perfect-race: both attempt greedy-cluster, neither touches the other
        print('=== GAME 7: P1=cluster-center(2,2), P2=cluster-far(5,5), no interference ===')
        play_game(lambda e,p: choose_cluster_region(e,p,2,2),
                  lambda e,p: choose_cluster_region(e,p,5,5), label='G7')
    elif mode == 'p1bias':
        # Seat-balance probe: 20 greedy vs greedy, count P1 wins
        wins={1:0,2:0,None:0}
        for i in range(20):
            e = fresh()
            for t in range(300):
                if e.done: break
                cp = e.get_current_player()
                mv = choose_greedy(e, cp)
                e.step(mv)
            wins[e._winner] = wins.get(e._winner,0)+1
        print('greedy vs greedy:', wins)
