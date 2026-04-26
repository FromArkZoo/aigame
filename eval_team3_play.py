"""Helper for team-3 evaluation of game 8d12c8b92b71."""
import sys
sys.path.insert(0, '/Users/jamesbrowne/aigame')
from play_helper import load_game
from game_engine import factory


def make_engine():
    game = load_game('genesis_v2_run16.db', '8d12c8b92b71')
    return factory.create_engine(game), game


def show_state(engine):
    print(f'Step {engine.step_count}, Current player: {engine.current_player}, Done: {engine.done}, Winner: {engine._winner}')
    print(f'Pieces: P1={engine.piece_counts[0]}, P2={engine.piece_counts[1]}')
    p1_eff = sum(engine.board_values[c] for c in range(64) if engine.board_owners[c] == 1)
    p2_eff = -sum(engine.board_values[c] for c in range(64) if engine.board_owners[c] == 2)
    print(f'P1 effective: {p1_eff:.3f}, P2 effective: {p2_eff:.3f}, Threshold: 34.129')
    print('Owners:')
    for y in range(8):
        row = []
        for x in range(8):
            o = engine.board_owners[y * 8 + x]
            if o == 0:
                row.append('.')
            elif o == 1:
                row.append('X')
            else:
                row.append('O')
        print(' '.join(row))
    print('Values:')
    for y in range(8):
        print(' '.join(f'{engine.board_values[y*8+x]:+.2f}' for x in range(8)))
    print()


def play_seq(moves):
    engine, game = make_engine()
    for i, m in enumerate(moves):
        legal = engine.get_legal_actions()
        if m not in legal:
            print(f'ILLEGAL move {i}: action {m} not in legal {legal[:10]}...')
            return engine
        engine.step(m)
        if engine.done:
            print(f'Game ended after move {i+1} (action {m})')
            break
    show_state(engine)
    return engine


def candidate_eval(engine, candidate_action):
    """Return resulting board values delta if engine.current_player plays candidate_action."""
    import copy
    eng2 = copy.deepcopy(engine)
    eng2.step(candidate_action)
    p1 = sum(eng2.board_values[c] for c in range(64) if eng2.board_owners[c] == 1)
    p2 = -sum(eng2.board_values[c] for c in range(64) if eng2.board_owners[c] == 2)
    return p1, p2, eng2.done, eng2._winner


if __name__ == '__main__':
    moves = [int(x) for x in sys.argv[1:]]
    play_seq(moves)
