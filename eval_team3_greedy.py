"""Greedy player for team-3 eval: maximize (own_eff - opponent_eff) after move."""
import sys
sys.path.insert(0, '/Users/jamesbrowne/aigame')
import copy
from play_helper import load_game
from game_engine import factory


def make_engine():
    game = load_game('genesis_v2_run16.db', '8d12c8b92b71')
    return factory.create_engine(game), game


def eff(engine):
    p1 = sum(engine.board_values[c] for c in range(64) if engine.board_owners[c] == 1)
    p2 = -sum(engine.board_values[c] for c in range(64) if engine.board_owners[c] == 2)
    return p1, p2


def best_greedy(engine, mode='max_diff'):
    """Pick action that maximizes own_eff - opp_eff."""
    me = engine.current_player
    legal = engine.get_legal_actions()
    best_a = None
    best_score = -1e9
    for a in legal:
        if a == 64:  # pass — only consider if forced
            continue
        e2 = copy.deepcopy(engine)
        e2.step(a)
        # Win check
        if e2.done and e2._winner == me:
            return a, 1e9
        if e2.done and e2._winner == (3 - me):
            score = -1e8
        else:
            p1, p2 = eff(e2)
            if me == 1:
                score = p1 - p2
            else:
                score = p2 - p1
        if score > best_score:
            best_score = score
            best_a = a
    return best_a, best_score


def play_greedy_game(verbose=True, p1_strategy='greedy', p2_strategy='greedy'):
    engine, game = make_engine()
    moves = []
    while not engine.done and engine.step_count < 200:
        me = engine.current_player
        strat = p1_strategy if me == 1 else p2_strategy
        if strat == 'greedy':
            a, s = best_greedy(engine)
        elif strat == 'cluster':
            a, s = best_greedy(engine)  # same for now
        engine.step(a)
        moves.append(a)
        if verbose:
            p1, p2 = eff(engine)
            print(f'  Turn {engine.step_count}: P{me} plays {a} (cell {a%8},{a//8}); P1eff={p1:.2f} P2eff={p2:.2f}')
    p1, p2 = eff(engine)
    print(f'\nGame ended. Winner: {engine._winner}, turns: {engine.step_count}')
    print(f'Final: P1eff={p1:.3f}, P2eff={p2:.3f}')
    print(f'Moves: {moves}')
    return moves, engine


if __name__ == '__main__':
    play_greedy_game()
