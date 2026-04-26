"""Play a full game with per-player heuristics and optional randomness."""
import sys
import sqlite3
import json
import random
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
        score = eff - 0.3 * oeff + 2.5 * (my_count - opp_count)
    elif style == "defensive":
        score = eff * 1.2 - 0.8 * oeff
    elif style == "counter":
        score = -oeff + 0.5 * eff + 1.0 * (my_count - opp_count)
    elif style == "random":
        score = random.random()
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
    scored = [(evaluate_candidate(eng, a, me, style), a) for a in legal]
    if style == "random":
        return random.choice(legal)
    scored.sort(reverse=True)
    # Random tie-break within 0.01 of the top
    top = scored[0][0]
    near_top = [a for s, a in scored if top - s < 0.01]
    return random.choice(near_top)


if __name__ == "__main__":
    game_id = sys.argv[1]
    p1_style = sys.argv[2] if len(sys.argv) > 2 else "greedy"
    p2_style = sys.argv[3] if len(sys.argv) > 3 else "greedy"
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 42
    prior_moves = [int(x) for x in sys.argv[5].split(",") if x.strip()] if len(sys.argv) > 5 and sys.argv[5] else []
    max_more = int(sys.argv[6]) if len(sys.argv) > 6 else 102

    random.seed(seed)
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

    print(f"Total moves: {len(all_moves)}, steps: {eng.step_count}")
    print(f"Moves: {all_moves}")
    print(f"Pieces: P1={eng.piece_counts[0]}, P2={eng.piece_counts[1]}")
    t1 = sum(eng.board_values[c] for c in range(eng.total_cells) if eng.board_owners[c] == 1)
    t2 = -sum(eng.board_values[c] for c in range(eng.total_cells) if eng.board_owners[c] == 2)
    print(f"P1 eff: {t1:.2f}, P2 eff: {t2:.2f}")
    print(f"Threshold: {game.win_condition.threshold:.2f}")
    print(f"Done: {eng.done}, Winner: {eng._winner}")
