#!/usr/bin/env python3
"""Team 21 helper for simultaneous game 992bf7dfc9f4 (R14)."""
import argparse
import sys
sys.path.insert(0, '.')
from play_helper import load_game, render_board, cell_to_coords_str
from game_engine.factory import create_engine


def render_with_legals(engine, game):
    topo = game.get_topology()
    out = [render_board(engine, game)]
    out.append(f"  Pieces: P1={engine.piece_counts[0]}, P2={engine.piece_counts[1]}")
    lp1 = engine.get_legal_actions(player=1)
    lp2 = engine.get_legal_actions(player=2)
    out.append(f"  Legal(P1)[{len(lp1)}]: {lp1[:25]}{'...' if len(lp1)>25 else ''}")
    out.append(f"  Legal(P2)[{len(lp2)}]: {lp2[:25]}{'...' if len(lp2)>25 else ''}")
    out.append(f"  Step count: {engine.step_count}  Done: {engine.done}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db-path", default="genesis_v2_run14.db")
    ap.add_argument("--game-id", required=True)
    ap.add_argument(
        "--moves", default="",
        help="Semicolon-separated pairs p1_action,p2_action  e.g. '27,36;28,35'"
    )
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    game = load_game(args.db_path, args.game_id)
    engine = create_engine(game)
    engine.reset()

    print(f"=== Game {args.game_id} (simultaneous) ===")
    print(render_with_legals(engine, game))

    if not args.moves.strip():
        return

    pairs = [p.strip() for p in args.moves.split(";") if p.strip()]
    for i, pair in enumerate(pairs):
        a, b = pair.split(",")
        a = int(a); b = int(b)

        lp1 = engine.get_legal_actions(player=1)
        lp2 = engine.get_legal_actions(player=2)
        if a not in lp1:
            print(f"\n!!! Turn {i+1}: P1 action {a} ILLEGAL. Legal(P1)={lp1}")
            return
        if b not in lp2:
            print(f"\n!!! Turn {i+1}: P2 action {b} ILLEGAL. Legal(P2)={lp2}")
            return
        obs, rewards, done, info = engine.step_simultaneous(a, b)
        topo = game.get_topology()
        da = "PASS" if a == game.total_cells else f"cell {a} {cell_to_coords_str(topo, a)}"
        db_ = "PASS" if b == game.total_cells else f"cell {b} {cell_to_coords_str(topo, b)}"
        collision = info.get("collision", False)
        print(f"\n--- Turn {i+1}: P1 {da}  |  P2 {db_}  (collision={collision}) ---")
        print(render_board(engine, game))
        print(f"  Pieces: P1={engine.piece_counts[0]}, P2={engine.piece_counts[1]}")
        print(f"  Step count: {engine.step_count}  Done: {done}")
        if done:
            w = info.get("winner")
            if w is not None:
                print(f"*** GAME OVER: Player {w+1} wins (rewards P1={rewards[0]}, P2={rewards[1]}) ***")
            else:
                print(f"*** GAME OVER: Draw (rewards P1={rewards[0]}, P2={rewards[1]}) ***")
            return

    print("\n--- Position after all turns ---")
    print(render_with_legals(engine, game))


if __name__ == "__main__":
    main()
