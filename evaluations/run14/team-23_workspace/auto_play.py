"""Auto-play game 992bf7dfc9f4 simultaneous to resolution.

Uses a heuristic policy:
- P1: pick the move that maximizes (future P1 stones) one step ahead.
- P2: pick the move that minimizes (future P1 stones) one step ahead;
       break ties by maximizing P2 stones.

This approximates optimal play for this game given the CA asymmetry.
Pass is available if no placements exist.
"""
import sys, os, copy, argparse
sys.path.insert(0, "/Users/jamesbrowne/aigame")

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


def simulate(engine, game, p1_seed, p2_seed, max_rounds=150, verbose=False, p1_opener=None, p2_opener=None, swap=False):
    """Play out a full game with heuristic policies.

    p1_opener, p2_opener: override first-round action.
    swap: if True, swap the policies (seat swap).
    """
    collisions = 0
    history = []
    round_num = 0

    while not engine.done and round_num < max_rounds:
        round_num += 1

        legal_p1 = engine.get_legal_actions(1)
        legal_p2 = engine.get_legal_actions(2)

        # First-round openers
        if round_num == 1:
            if p1_opener is not None and p1_opener in legal_p1:
                ap1 = p1_opener
            else:
                ap1 = pick_best_action(engine, game, 1, legal_p1, legal_p2, maximize_p1=True)
            if p2_opener is not None and p2_opener in legal_p2:
                ap2 = p2_opener
            else:
                ap2 = pick_best_action(engine, game, 2, legal_p2, legal_p1, maximize_p1=False)
        else:
            if swap:
                ap1 = pick_best_action(engine, game, 1, legal_p1, legal_p2, maximize_p1=False)
                ap2 = pick_best_action(engine, game, 2, legal_p2, legal_p1, maximize_p1=True)
            else:
                ap1 = pick_best_action(engine, game, 1, legal_p1, legal_p2, maximize_p1=True)
                ap2 = pick_best_action(engine, game, 2, legal_p2, legal_p1, maximize_p1=False)

        obs, rewards, done, info = engine.step_simultaneous(ap1, ap2)
        if info.get("collision"):
            collisions += 1

        history.append((round_num, ap1, ap2, info.get("collision", False),
                       engine.piece_counts[0], engine.piece_counts[1]))

        if verbose:
            print(f"R{round_num}: P1={ap1} P2={ap2} collision={info.get('collision')} | P1={engine.piece_counts[0]} P2={engine.piece_counts[1]}")

    return collisions, history, engine


def pick_best_action(engine, game, player, own_legal, opp_legal, maximize_p1=True):
    """Greedy 1-ply: for each of player's legal actions, simulate against opponent's
    counter-best-response and pick highest P1-count (or lowest if maximize_p1=False).

    Simplification: assume opponent picks a policy that maximizes opposite of our goal.
    We do 1-ply search (for our move) and assume opponent picks their greedy move
    simultaneously. This is not true minimax but reasonable for small games.
    """
    # Guess opponent move: their greedy move in current state assuming we pass.
    # Then evaluate each of our moves against that guess.
    pass_action = game.total_cells

    # Step 1: opponent's best response if we pass.
    best_opp_action = pass_action
    best_opp_eval = None
    for opp_act in opp_legal:
        e2 = engine.clone()
        # Simulate with our=pass, opp=opp_act
        if player == 1:
            e2.step_simultaneous(pass_action, opp_act)
        else:
            e2.step_simultaneous(opp_act, pass_action)
        p1_count = e2.piece_counts[0]
        p2_count = e2.piece_counts[1]
        # Opponent's evaluation: opponent wants to push in their favor
        if player == 1:  # opp is P2
            if maximize_p1:  # we're P1, opp is P2 trying to minimize P1
                eval_val = -p1_count + 0.1 * p2_count
            else:  # we're P1 trying to help P2; opp P2 tries to... same as maximize_p2
                eval_val = p2_count - 0.1 * p1_count
        else:  # opp is P1
            if maximize_p1:  # we're P2 helping P1 — opp P1 also maximizes P1
                eval_val = p1_count - 0.1 * p2_count
            else:  # we're P2, opp P1 maximizes P1
                eval_val = p1_count - 0.1 * p2_count
        if best_opp_eval is None or eval_val > best_opp_eval:
            best_opp_eval = eval_val
            best_opp_action = opp_act

    # Step 2: our best action given opp plays best_opp_action.
    best_act = pass_action
    best_eval = None
    for act in own_legal:
        e2 = engine.clone()
        if player == 1:
            e2.step_simultaneous(act, best_opp_action)
        else:
            e2.step_simultaneous(best_opp_action, act)
        p1_count = e2.piece_counts[0]
        p2_count = e2.piece_counts[1]
        if maximize_p1:
            eval_val = p1_count - 0.1 * p2_count
        else:
            eval_val = p2_count - 0.5 * p1_count  # P2 heavily penalizes P1's growth
        if best_eval is None or eval_val > best_eval:
            best_eval = eval_val
            best_act = act

    return best_act


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p1", type=int, default=None)
    ap.add_argument("--p2", type=int, default=None)
    ap.add_argument("--swap", action="store_true")
    ap.add_argument("--max-rounds", type=int, default=150)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    game = load()
    engine = create_engine(game)
    engine.reset()

    collisions, history, eng = simulate(engine, game, None, None,
                                         max_rounds=args.max_rounds,
                                         verbose=args.verbose,
                                         p1_opener=args.p1,
                                         p2_opener=args.p2,
                                         swap=args.swap)

    print(f"\n=== FINAL: P1={eng.piece_counts[0]} P2={eng.piece_counts[1]}  step={eng.step_count}  done={eng.done}  winner={eng._winner}  collisions={collisions} ===")
    size = game.axis_size
    topo = game.get_topology()
    for row in range(size):
        line = ""
        for col in range(size):
            idx = topo.coords_to_cell((col, row))
            o = eng.board_owners[idx]
            line += " X" if o == 1 else (" O" if o == 2 else " .")
        print(f" {row}: {line}")


if __name__ == "__main__":
    main()
