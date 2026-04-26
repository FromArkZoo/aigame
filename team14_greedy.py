"""Greedy player: pick the legal move that maximizes effective score swing."""
import sys
sys.path.insert(0, '/Users/jamesbrowne/aigame')
from play_helper import load_game
from game_engine.factory import create_engine
import copy


def score_diff(e, player):
    p1 = sum(e.board_values[c] for c in range(64) if e.board_owners[c] == 1)
    p2 = -sum(e.board_values[c] for c in range(64) if e.board_owners[c] == 2)
    return (p1 - p2) if player == 1 else (p2 - p1)


def greedy_move(e):
    player = e.current_player
    legal = [a for a in e.get_legal_actions() if a != 64]  # avoid pass unless forced
    if not legal:
        return 64
    best = None
    best_swing = -1e9
    cur_swing = score_diff(e, player)
    for a in legal:
        # Save state via the engine save/restore (mimicking ko rule)
        saved_owners = e.board_owners.copy()
        saved_values = e.board_values.copy()
        saved_pc = list(e.piece_counts)
        saved_cp = e.current_player
        saved_done = e.done
        saved_step = e.step_count
        saved_winner = e._winner
        saved_passes = e.consecutive_passes
        saved_history = set(e._position_history) if hasattr(e, '_position_history') else None
        try:
            e.step(a)
            new_swing = score_diff(e, player)
            d = new_swing - cur_swing
            if d > best_swing:
                best_swing = d
                best = a
        finally:
            e.board_owners[:] = saved_owners
            e.board_values[:] = saved_values
            e.piece_counts = list(saved_pc)
            e.current_player = saved_cp
            e.done = saved_done
            e.step_count = saved_step
            e._winner = saved_winner
            e.consecutive_passes = saved_passes
            if saved_history is not None:
                e._position_history = saved_history
    return best


def play_game(opening_p1, opening_p2, max_moves=80, verbose=False):
    g = load_game('genesis_v2_run16.db', 'c6bb58075520')
    e = create_engine(g)
    moves = []
    if opening_p1 is not None:
        e.step(opening_p1)
        moves.append(('P1', opening_p1))
        if verbose: print(f"M{len(moves)} P1 forced -> {opening_p1}")
    if opening_p2 is not None:
        e.step(opening_p2)
        moves.append(('P2', opening_p2))
        if verbose: print(f"M{len(moves)} P2 forced -> {opening_p2}")
    while not e.done and len(moves) < max_moves:
        cur = e.current_player
        a = greedy_move(e)
        e.step(a)
        moves.append((f'P{cur}', a))
        if verbose:
            x = a % 8; y = a // 8
            print(f"M{len(moves)} P{cur} -> ({x},{y}) action={a}, p1={sum(e.board_values[c] for c in range(64) if e.board_owners[c]==1):.2f}, p2={-sum(e.board_values[c] for c in range(64) if e.board_owners[c]==2):.2f}")
    p1 = sum(e.board_values[c] for c in range(64) if e.board_owners[c] == 1)
    p2 = -sum(e.board_values[c] for c in range(64) if e.board_owners[c] == 2)
    print(f"\nFinal: P1={p1:.2f}, P2={p2:.2f}, winner={getattr(e, '_winner', None)}, moves={len(moves)}, pieces P1={e.piece_counts[0]} P2={e.piece_counts[1]}")
    return moves, e


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--p1", type=int, default=None)
    p.add_argument("--p2", type=int, default=None)
    p.add_argument("-v", action="store_true")
    args = p.parse_args()
    play_game(args.p1, args.p2, verbose=args.v)
