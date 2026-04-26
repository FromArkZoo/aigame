"""Quick play-and-show helper for team-2 evaluation."""
import sys
sys.path.insert(0, '/Users/jamesbrowne/aigame')
from play_helper import load_game
from game_engine.factory import create_engine
import numpy as np

def run(moves, game_id='deb4dfe0382d', db='genesis_v2_run14.db'):
    game = load_game(db, game_id)
    engine = create_engine(game)
    engine.reset()
    for i, mv in enumerate(moves):
        legal = engine.get_legal_actions()
        if mv not in legal:
            print(f"Move {i+1} action {mv}: ILLEGAL (legal count={len(legal)})")
            return engine
        engine.step(mv)
        if engine.done:
            print(f"Move {i+1}: action {mv}; game ended, winner={getattr(engine,'_winner',None)}")
            break
    show(engine)
    return engine

def show(engine):
    size = 8
    print('  Board (8x8) + values (X=P1, O=P2)')
    print('   ' + ' '.join(f'{c:>6}' for c in range(size)))
    for row in range(size):
        syms = []
        vals = []
        for col in range(size):
            idx = col + row*size
            owner = engine.board_owners[idx]
            v = engine.board_values[idx]
            sym = 'X' if owner == 1 else ('O' if owner == 2 else '.')
            syms.append(f'{sym:>6}')
            vals.append(f'{v:+.2f}')
        print(f'{row:>2} ' + ' '.join(syms))
        print('   ' + ' '.join(f'{v:>6}' for v in vals))
    p1 = sum(engine.board_values[c] for c in range(64) if engine.board_owners[c]==1)
    p2 = -sum(engine.board_values[c] for c in range(64) if engine.board_owners[c]==2)
    print(f'P1 score: {p1:.3f}   P2 score: {p2:.3f}   (threshold=38.62)')
    print(f'P1 pieces: {engine.piece_counts[0]}   P2 pieces: {engine.piece_counts[1]}')
    winner = getattr(engine, '_winner', None)
    print(f'Current player: {engine.current_player}  done={engine.done}  winner={winner}')
    print(f'Consecutive passes: {engine.consecutive_passes}')

if __name__ == '__main__':
    moves = [int(x) for x in sys.argv[1].split(',')] if len(sys.argv) > 1 else []
    run(moves)
