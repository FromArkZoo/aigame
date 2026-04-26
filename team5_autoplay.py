"""Simple heuristic autoplay to finish a game deterministically."""
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


def best_move(eng, game, seed_bias=0):
    """Heuristic: try every legal non-pass placement, pick highest threshold-gain for current player.
    seed_bias adds a tiny per-move random tie-breaker for variation across games."""
    import random
    legal = [a for a in eng.get_legal_actions() if a != 64]
    if not legal:
        return 64
    best_score = -1e9
    best = legal[0]
    me = eng.current_player
    saved_done_global = eng.done
    saved_winner_global = eng._winner
    saved_hist = set(eng._position_history) if hasattr(eng, '_position_history') else None
    for a in legal:
        state = eng._save_state()
        saved_step = eng.step_count
        eng.done = False
        eng._winner = None
        eng.step(a)
        total = sum(eng.board_values[c] for c in range(eng.total_cells) if eng.board_owners[c] == me)
        eff = total if me == 1 else -total
        opp = 3 - me
        otot = sum(eng.board_values[c] for c in range(eng.total_cells) if eng.board_owners[c] == opp)
        oeff = otot if opp == 1 else -otot
        my_count = eng.piece_counts[me - 1]
        opp_count = eng.piece_counts[opp - 1]
        score = eff - 0.5 * oeff + 0.3 * (my_count - opp_count)
        score += seed_bias * (hash((a, eng.step_count)) % 1000) / 1e6
        eng._restore_state(state)
        eng.step_count = saved_step
        if saved_hist is not None:
            eng._position_history = set(saved_hist)
        if score > best_score:
            best_score = score
            best = a
    eng.done = saved_done_global
    eng._winner = saved_winner_global
    return best


if __name__ == "__main__":
    game_id = sys.argv[1]
    prior_moves = [int(x) for x in sys.argv[2].split(",") if x.strip()] if len(sys.argv) > 2 and sys.argv[2] else []
    max_more = int(sys.argv[3]) if len(sys.argv) > 3 else 100

    game = load_game(game_id)
    eng = create_engine(game)
    for mv in prior_moves:
        eng.step(mv)
        if eng.done:
            break

    print(f"Resuming at step {eng.step_count}, turn={eng.current_player}, done={eng.done}")
    played = []
    for _ in range(max_more):
        if eng.done:
            break
        seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        mv = best_move(eng, game, seed_bias=seed)
        pre = (eng.piece_counts[0], eng.piece_counts[1], eng.step_count, int(eng.board_owners[mv]))
        eng.step(mv)
        played.append((mv, pre, (eng.piece_counts[0], eng.piece_counts[1], eng.step_count, eng.done, eng._winner)))
    print(f"Played {len(played)} more moves: {played}")
    print(f"Pieces: P1={eng.piece_counts[0]}, P2={eng.piece_counts[1]}")
    t1 = sum(eng.board_values[c] for c in range(eng.total_cells) if eng.board_owners[c] == 1)
    t2 = -sum(eng.board_values[c] for c in range(eng.total_cells) if eng.board_owners[c] == 2)
    print(f"P1 eff: {t1:.2f}, P2 eff: {t2:.2f}")
    print(f"Threshold: {game.win_condition.threshold:.2f}")
    print(f"Step: {eng.step_count}, Done: {eng.done}, Winner: {eng._winner}")
