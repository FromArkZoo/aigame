"""Play a full game with per-player heuristics."""
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


def evaluate_candidate(eng, a, me, style):
    """Evaluate candidate move a for player me with a given style."""
    state = eng._save_state()
    saved_step = eng.step_count
    saved_done = eng.done
    saved_winner = eng._winner
    saved_hist = set(eng._position_history) if hasattr(eng, '_position_history') else None
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

    if style == "greedy":
        score = eff - 0.5 * oeff
    elif style == "aggressive":
        # Prioritize captures (piece diff)
        score = eff - 0.5 * oeff + 1.0 * (my_count - opp_count)
    elif style == "defensive":
        # Prioritize own threshold progress
        score = eff * 1.5 - 0.3 * oeff
    elif style == "mixed":
        score = eff - 0.7 * oeff + 0.5 * (my_count - opp_count)
    else:
        score = eff - 0.5 * oeff + 0.3 * (my_count - opp_count)

    eng._restore_state(state)
    eng.step_count = saved_step
    eng.done = saved_done
    eng._winner = saved_winner
    if saved_hist is not None:
        eng._position_history = set(saved_hist)
    return score


def best_move(eng, game, style):
    legal = [a for a in eng.get_legal_actions() if a != 64]
    if not legal:
        return 64
    me = eng.current_player
    best_score = -1e9
    best = legal[0]
    for a in legal:
        s = evaluate_candidate(eng, a, me, style)
        if s > best_score:
            best_score = s
            best = a
    return best


if __name__ == "__main__":
    game_id = sys.argv[1]
    p1_style = sys.argv[2] if len(sys.argv) > 2 else "greedy"
    p2_style = sys.argv[3] if len(sys.argv) > 3 else "greedy"
    prior_moves = [int(x) for x in sys.argv[4].split(",") if x.strip()] if len(sys.argv) > 4 and sys.argv[4] else []
    max_more = int(sys.argv[5]) if len(sys.argv) > 5 else 102

    game = load_game(game_id)
    eng = create_engine(game)
    for mv in prior_moves:
        eng.step(mv)
        if eng.done:
            break

    all_moves = list(prior_moves)
    while not eng.done and eng.step_count < max_more:
        style = p1_style if eng.current_player == 1 else p2_style
        mv = best_move(eng, game, style)
        eng.step(mv)
        all_moves.append(mv)

    print(f"Total moves: {len(all_moves)}")
    print(f"Moves: {all_moves}")
    print(f"Pieces: P1={eng.piece_counts[0]}, P2={eng.piece_counts[1]}")
    t1 = sum(eng.board_values[c] for c in range(eng.total_cells) if eng.board_owners[c] == 1)
    t2 = -sum(eng.board_values[c] for c in range(eng.total_cells) if eng.board_owners[c] == 2)
    print(f"P1 eff: {t1:.2f}, P2 eff: {t2:.2f}")
    print(f"Threshold: {game.win_condition.threshold:.2f}")
    print(f"Step: {eng.step_count}, Done: {eng.done}, Winner: {eng._winner}")
