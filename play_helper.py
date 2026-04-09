#!/usr/bin/env python3
"""Helper for Claude agents to play and evaluate Genesis V2 games.

Usage examples:
    # Show game rules summary
    python play_helper.py --game-id edad1954a233 --action rules

    # Show current board state (after reset)
    python play_helper.py --game-id edad1954a233 --action show

    # Play a sequence of moves and show result
    python play_helper.py --game-id edad1954a233 --action play --moves "10,25,11,26,12"

    # Show legal actions with coordinates
    python play_helper.py --game-id edad1954a233 --action legal --moves "10,25"

    # Play a full random game to see game flow
    python play_helper.py --game-id edad1954a233 --action random-game
"""

import argparse
import json
import sqlite3
import sys
import numpy as np

from game_engine.game_def_v2 import GameDefV2
from game_engine.factory import create_engine


def load_game(db_path: str, game_id: str) -> GameDefV2:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT rule_representation FROM games WHERE game_id = ?", (game_id,)).fetchone()
    conn.close()
    if row is None:
        raise ValueError(f"Game {game_id} not found")
    rules = json.loads(row["rule_representation"])
    return GameDefV2.from_dict(rules)


def cell_to_coords_str(topo, cell_idx):
    """Convert cell index to human-readable coordinate string."""
    coords = topo.cell_to_coords(cell_idx)
    if len(coords) == 2:
        return f"({coords[0]},{coords[1]})"
    elif len(coords) == 3:
        return f"({coords[0]},{coords[1]},{coords[2]})"
    else:
        return f"({','.join(str(c) for c in coords)})"


def render_board_2d(engine, game):
    """Render a 2D board as ASCII grid."""
    topo = game.get_topology()
    size = game.axis_size
    lines = []
    lines.append(f"  Board ({size}x{size})  Player 1=X  Player 2=O  Empty=.")
    lines.append("  " + " ".join(f"{c:>2}" for c in range(size)))
    for row in range(size):
        cells = []
        for col in range(size):
            idx = topo.coords_to_cell((col, row))
            owner = engine.board_owners[idx]
            if owner == 1:
                cells.append(" X")
            elif owner == 2:
                cells.append(" O")
            else:
                cells.append(" .")
        lines.append(f"{row:>2}" + "".join(cells))
    return "\n".join(lines)


def render_board_3d(engine, game):
    """Render a 3D board as multiple 2D slices."""
    topo = game.get_topology()
    size = game.axis_size
    lines = []
    lines.append(f"  Board ({size}x{size}x{size})  Player 1=X  Player 2=O  Empty=.")
    for z in range(size):
        lines.append(f"\n  Layer z={z}:")
        lines.append("    " + " ".join(f"{c:>2}" for c in range(size)))
        for y in range(size):
            cells = []
            for x in range(size):
                idx = topo.coords_to_cell((x, y, z))
                owner = engine.board_owners[idx]
                if owner == 1:
                    cells.append(" X")
                elif owner == 2:
                    cells.append(" O")
                else:
                    cells.append(" .")
            lines.append(f"  {y:>2}" + "".join(cells))
    return "\n".join(lines)


def render_board(engine, game):
    """Render board based on dimensionality."""
    if game.num_dimensions == 2:
        return render_board_2d(engine, game)
    elif game.num_dimensions == 3:
        return render_board_3d(engine, game)
    else:
        # For higher dimensions, show flat representation
        topo = game.get_topology()
        lines = [f"  Board: {game.num_dimensions}D, axis_size={game.axis_size}, total_cells={game.total_cells}"]
        lines.append(f"  Player 1=X  Player 2=O  Empty=.")
        p1_cells = []
        p2_cells = []
        for i in range(game.total_cells):
            if engine.board_owners[i] == 1:
                p1_cells.append(f"{i}{cell_to_coords_str(topo, i)}")
            elif engine.board_owners[i] == 2:
                p2_cells.append(f"{i}{cell_to_coords_str(topo, i)}")
        lines.append(f"  Player 1 pieces: {', '.join(p1_cells) if p1_cells else 'none'}")
        lines.append(f"  Player 2 pieces: {', '.join(p2_cells) if p2_cells else 'none'}")
        lines.append(f"  Empty cells: {game.total_cells - len(p1_cells) - len(p2_cells)}")
        return "\n".join(lines)


def format_rules(game):
    """Format game rules as human-readable text."""
    rules = game.to_dict()
    lines = []
    lines.append(f"=== Game {game.game_id} Rules ===")
    lines.append(f"")
    topology_type = getattr(game, 'topology_type', 'grid')
    lines.append(f"BOARD: {game.num_dimensions}D {topology_type}, axis_size={game.axis_size}")
    lines.append(f"  Topology: {topology_type}")
    lines.append(f"  Total cells: {game.total_cells}")
    lines.append(f"  Adjacency: von Neumann (face-adjacent only, no diagonals)")
    lines.append(f"")

    pr = rules["placement_rule"]
    lines.append(f"PLACEMENT:")
    lines.append(f"  Target: {pr['target']} cells")
    lines.append(f"  Constraint: {pr['constraint']}")
    lines.append(f"  First move anywhere: {pr.get('first_move_anywhere', False)}")
    lines.append(f"")

    cr = rules["capture_rule"]
    lines.append(f"CAPTURE: {cr['capture_type']}")
    if cr["capture_type"] == "surround":
        lines.append(f"  Go-style: groups with 0 liberties are removed")
        lines.append(f"  Threshold: {cr.get('threshold', 1)}")
    elif cr["capture_type"] == "custodian":
        lines.append(f"  Othello-style: enemy pieces bracketed along axis lines are flipped")
    elif cr["capture_type"] == "outnumber":
        lines.append(f"  Adjacent enemies removed if they have >= {cr.get('threshold', 2)} friendly neighbors")
    lines.append(f"")

    prop = rules["propagation_rule"]
    lines.append(f"PROPAGATION: {prop['prop_type']}")
    if prop["prop_type"] == "influence":
        lines.append(f"  Radius: {prop['radius']}, Strength: {prop['strength']:.3f}, Decay: {prop['decay']:.3f}")
    elif prop["prop_type"] == "cascade":
        lines.append(f"  Captures can chain (up to 10 iterations)")
    lines.append(f"")

    wc = rules["win_condition"]
    lines.append(f"WIN CONDITION: {wc['condition_type']}")
    if wc["condition_type"] == "threshold":
        lines.append(f"  Win when total influence on own cells > {wc['threshold']:.3f}")
    elif wc["condition_type"] == "territory":
        lines.append(f"  Win when owning > {wc['threshold']:.1%} of cells")
    elif wc["condition_type"] == "connection":
        lines.append(f"  Win by connecting opposite faces along dimension {wc.get('target_dimension', 0)}")
    elif wc["condition_type"] == "majority":
        lines.append(f"  Most pieces at game end wins")
    elif wc["condition_type"] == "elimination":
        lines.append(f"  Win by removing all enemy pieces")
    lines.append(f"  Max turns: {wc.get('max_turns', 100)}")
    lines.append(f"")

    ts = rules["turn_structure"]
    lines.append(f"TURNS: {ts['turn_type']}")
    if ts["turn_type"] == "multi_place":
        lines.append(f"  Pieces per turn: {ts.get('pieces_per_turn', 1)}")
    lines.append(f"")

    action_rule = getattr(game, 'action_rule', None)
    action_types = ', '.join(action_rule.action_types) if action_rule else 'place'
    lines.append(f"ACTION TYPES: {action_types}")
    if action_rule and action_rule.has_move():
        lines.append(f"  Move constraint: {action_rule.move_constraint}")
    lines.append(f"")

    if game.uses_ca:
        ca = game.ca_rule
        birth = sum(1 for (s, f, e), ns in ca.transition_table.items() if s == 0 and ns != 0)
        death = sum(1 for (s, f, e), ns in ca.transition_table.items() if s == 1 and ns == 0)
        convert = sum(1 for (s, f, e), ns in ca.transition_table.items() if s != 0 and ns != 0 and ns != s)
        lines.append(f"CELLULAR AUTOMATON: Yes")
        lines.append(f"  Steps per turn: {ca.steps_per_turn}")
        lines.append(f"  CA: {birth} birth rules, {death} death rules, {convert} conversion rules")
        lines.append(f"  Max neighbors: {ca.max_neighbors}")
    else:
        lines.append(f"CELLULAR AUTOMATON: No (classic mechanics)")
    lines.append(f"")

    lines.append(f"ACTION SPACE: {game.num_actions} actions")
    lines.append(f"  Actions 0-{game.total_cells-1}: place at cell index")
    lines.append(f"  Action {game.total_cells}: pass")

    return "\n".join(lines)


def show_legal_actions(engine, game, max_show=30):
    """Show legal actions with coordinates."""
    topo = game.get_topology()
    legal = engine.get_legal_actions()
    player = engine.get_current_player()

    lines = []
    lines.append(f"Current player: {player + 1} ({'X' if player == 0 else 'O'})")
    lines.append(f"Legal actions ({len(legal)} total):")

    placement_actions = [a for a in legal if a < game.total_cells]
    has_pass = game.total_cells in legal

    shown = 0
    for a in placement_actions[:max_show]:
        coords = cell_to_coords_str(topo, a)
        lines.append(f"  Action {a:>3} -> cell {coords}")
        shown += 1

    if len(placement_actions) > max_show:
        lines.append(f"  ... and {len(placement_actions) - max_show} more placement actions")

    if has_pass:
        lines.append(f"  Action {game.total_cells:>3} -> PASS")

    return "\n".join(lines)


def play_moves(engine, game, moves):
    """Play a sequence of moves, showing state after each."""
    topo = game.get_topology()
    output = []

    for i, move in enumerate(moves):
        player = engine.get_current_player()
        legal = engine.get_legal_actions()

        if move not in legal:
            output.append(f"\n!!! Move {move} is ILLEGAL for player {player + 1}")
            output.append(f"    Legal actions: {legal[:20]}{'...' if len(legal) > 20 else ''}")
            break

        if move == game.total_cells:
            move_desc = "PASS"
        else:
            move_desc = f"cell {move} {cell_to_coords_str(topo, move)}"

        obs, rewards, done, info = engine.step(move)

        ca_note = f" (after {game.ca_rule.steps_per_turn} CA step{'s' if game.ca_rule.steps_per_turn > 1 else ''})" if game.uses_ca else ""
        output.append(f"\n--- Move {i+1}: Player {player + 1} plays {move_desc}{ca_note} ---")
        output.append(render_board(engine, game))
        output.append(f"  Pieces: P1={engine.piece_counts[0]}, P2={engine.piece_counts[1]}")

        if done:
            winner = info.get("winner")
            if winner is not None:
                output.append(f"\n*** GAME OVER: Player {winner + 1} wins! ***")
            else:
                output.append(f"\n*** GAME OVER: Draw! ***")
            output.append(f"  Final rewards: P1={rewards[0]:.1f}, P2={rewards[1]:.1f}")
            break

    if not done:
        output.append(f"\n--- After {len(moves)} moves ---")
        player = engine.get_current_player()
        output.append(f"  Next to play: Player {player + 1} ({'X' if player == 0 else 'O'})")
        output.append(show_legal_actions(engine, game))

    return "\n".join(output)


def random_game(engine, game, seed=42):
    """Play a full random game to demonstrate game flow."""
    rng = np.random.RandomState(seed)
    topo = game.get_topology()
    output = []

    output.append(f"=== Random Game (seed={seed}) ===")
    output.append(render_board(engine, game))

    move_num = 0
    done = False
    while not done:
        player = engine.get_current_player()
        legal = engine.get_legal_actions()

        # Prefer placement over pass
        placements = [a for a in legal if a < game.total_cells]
        if placements:
            action = rng.choice(placements)
        else:
            action = game.total_cells  # pass

        if action == game.total_cells:
            move_desc = "PASS"
        else:
            move_desc = f"cell {action} {cell_to_coords_str(topo, action)}"

        obs, rewards, done, info = engine.step(action)
        move_num += 1

        output.append(f"\nMove {move_num}: Player {player + 1} -> {move_desc}")

        if done or move_num <= 10 or move_num % 10 == 0:
            output.append(render_board(engine, game))
            output.append(f"  Pieces: P1={engine.piece_counts[0]}, P2={engine.piece_counts[1]}")

    winner = info.get("winner")
    if winner is not None:
        output.append(f"\n*** GAME OVER after {move_num} moves: Player {winner + 1} wins! ***")
    else:
        output.append(f"\n*** GAME OVER after {move_num} moves: Draw! ***")
    output.append(f"  Final rewards: P1={rewards[0]:.1f}, P2={rewards[1]:.1f}")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Play helper for Genesis V2 games")
    parser.add_argument("--db-path", default="genesis_v2_run7.db")
    parser.add_argument("--game-id", required=True)
    parser.add_argument("--action", required=True,
                       choices=["rules", "show", "play", "legal", "random-game"])
    parser.add_argument("--moves", default="",
                       help="Comma-separated list of action indices")
    parser.add_argument("--seed", type=int, default=42,
                       help="Random seed for random-game")
    args = parser.parse_args()

    game = load_game(args.db_path, args.game_id)
    engine = create_engine(game)
    obs = engine.reset()

    if args.action == "rules":
        print(format_rules(game))

    elif args.action == "show":
        if args.moves:
            moves = [int(m.strip()) for m in args.moves.split(",") if m.strip()]
            for m in moves:
                engine.step(m)
        print(render_board(engine, game))
        print(f"  Pieces: P1={engine.piece_counts[0]}, P2={engine.piece_counts[1]}")
        print()
        print(show_legal_actions(engine, game))

    elif args.action == "play":
        moves = [int(m.strip()) for m in args.moves.split(",") if m.strip()]
        print(render_board(engine, game))
        print(play_moves(engine, game, moves))

    elif args.action == "legal":
        if args.moves:
            moves = [int(m.strip()) for m in args.moves.split(",") if m.strip()]
            for m in moves:
                engine.step(m)
        print(show_legal_actions(engine, game))

    elif args.action == "random-game":
        print(random_game(engine, game, seed=args.seed))


if __name__ == "__main__":
    main()
