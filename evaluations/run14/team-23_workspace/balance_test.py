"""Test balance by running many auto-play games with different openers.

Both players use the SAME heuristic: maximize own piece count minus 0.5x opponent.
This is a symmetric objective; any imbalance comes from the game's structural asymmetry.
"""
import sys
sys.path.insert(0, "/Users/jamesbrowne/aigame")
sys.path.insert(0, "/Users/jamesbrowne/aigame/evaluations/run14/team-23_workspace")

import sqlite3, json
from game_engine.game_def_v2 import GameDefV2
from game_engine.factory import create_engine

DB = "/Users/jamesbrowne/aigame/genesis_v2_run14.db"
GID = "992bf7dfc9f4"


def load():
    conn = sqlite3.connect(DB)
    row = conn.execute("SELECT rule_representation FROM games WHERE game_id=?", (GID,)).fetchone()
    conn.close()
    return GameDefV2.from_dict(json.loads(row[0]))


def pick_greedy(engine, game, player):
    """Pick the move that maximizes our count minus half opponent count, 1-ply."""
    own_legal = engine.get_legal_actions(player)
    opp_legal = engine.get_legal_actions(3 - player)
    pass_action = game.total_cells

    # Opponent's predicted move: greedy one-step self-interest.
    best_opp_action = pass_action
    best_opp_eval = None
    for opp_act in opp_legal:
        e2 = engine.clone()
        try:
            if player == 1:
                e2.step_simultaneous(pass_action, opp_act)
            else:
                e2.step_simultaneous(opp_act, pass_action)
        except Exception:
            continue
        opp_pieces = e2.piece_counts[(3-player)-1]
        own_pieces = e2.piece_counts[player-1]
        eval_val = opp_pieces - 0.5 * own_pieces
        if best_opp_eval is None or eval_val > best_opp_eval:
            best_opp_eval = eval_val
            best_opp_action = opp_act

    # Our best: max own - 0.5 * opp.
    best_act = pass_action
    best_eval = None
    for act in own_legal:
        e2 = engine.clone()
        try:
            if player == 1:
                e2.step_simultaneous(act, best_opp_action)
            else:
                e2.step_simultaneous(best_opp_action, act)
        except Exception:
            continue
        own_pieces = e2.piece_counts[player-1]
        opp_pieces = e2.piece_counts[(3-player)-1]
        eval_val = own_pieces - 0.5 * opp_pieces
        if best_eval is None or eval_val > best_eval:
            best_eval = eval_val
            best_act = act

    return best_act


def run_one(p1_open, p2_open, max_rounds=150):
    game = load()
    engine = create_engine(game)
    engine.reset()
    collisions = 0
    round_num = 0

    while not engine.done and round_num < max_rounds:
        round_num += 1
        if round_num == 1:
            ap1 = p1_open
            ap2 = p2_open
        else:
            ap1 = pick_greedy(engine, game, 1)
            ap2 = pick_greedy(engine, game, 2)

        obs, rewards, done, info = engine.step_simultaneous(ap1, ap2)
        if info.get("collision"):
            collisions += 1

    return {
        "rounds": round_num,
        "p1": engine.piece_counts[0],
        "p2": engine.piece_counts[1],
        "winner": engine._winner,
        "done_by_threshold": engine.done and round_num < max_rounds and collisions < round_num - 5,
        "collisions": collisions,
        "max_turns_reached": round_num >= max_rounds or engine.step_count >= game.max_game_steps,
    }


# Test 8 openings
openings = [
    (27, 36),  # central diag
    (27, 28),  # adjacent (P2 aggressive)
    (18, 45),  # neutral opposite
    (0, 63),   # opposite corners
    (27, 0),   # P1 center, P2 corner
    (0, 27),   # swap: P1 corner, P2 center
    (36, 27),  # swap of first
    (63, 0),   # swap of opposite corners
]

print(f"{'P1_open':>8} {'P2_open':>8} {'P1':>4} {'P2':>4} {'winner':>6} {'rounds':>6} {'collis':>7} {'by':>8}")
p1_wins = 0
p2_wins = 0
draws = 0
for p1o, p2o in openings:
    r = run_one(p1o, p2o)
    winner_txt = "P1" if r["winner"] == 1 else ("P2" if r["winner"] == 2 else "draw")
    end_reason = "thresh" if r["p1"] > 40 or r["p2"] > 40 else ("maxturn" if r["max_turns_reached"] else "2pass")
    print(f"{p1o:>8} {p2o:>8} {r['p1']:>4} {r['p2']:>4} {winner_txt:>6} {r['rounds']:>6} {r['collisions']:>7} {end_reason:>8}")
    if r["winner"] == 1:
        p1_wins += 1
    elif r["winner"] == 2:
        p2_wins += 1
    else:
        draws += 1

print(f"\nTotal: P1={p1_wins} P2={p2_wins} draws={draws} of {len(openings)}")
