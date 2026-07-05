"""Blind-eval helper — self-contained player for games A-G.

Loads anonymized game definitions from evaluations/rc2_campaign_blind/games/<LABEL>.json
and runs them through the project game engine. Evaluators interact with the
games ONLY through this CLI (see BRIEFING.md).

Usage:
    .venv/bin/python evaluations/rc2_campaign_blind/play.py --game A --rules
    .venv/bin/python evaluations/rc2_campaign_blind/play.py --game A --legal
    .venv/bin/python evaluations/rc2_campaign_blind/play.py --game A --moves "12,40,7" [--values] [--legal]

--rules   print the full mechanics of the game (derived from the game
          definition and engine semantics only — no provenance).
--moves   csv of action ids applied from the initial position; per-ply delta
          is printed, full board at the end.
--legal   after the moves (or at the start), print the legal action ids for
          the player to move, with human decode.
--values  also render the influence field (board_values); only meaningful
          for games with influence propagation.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game_engine.factory import create_engine          # noqa: E402
from game_engine.game_def_v2 import GameDefV2          # noqa: E402

LABELS = ("A", "B", "C", "D", "E", "F", "G")


def load_game(label: str) -> GameDefV2:
    if label not in LABELS:
        sys.exit(f"!! unknown game label {label!r}; valid labels: {', '.join(LABELS)}")
    path = HERE / "games" / f"{label}.json"
    if not path.exists():
        sys.exit(f"!! game file missing: {path}")
    return GameDefV2.from_dict(json.loads(path.read_text()))


# ----------------------------------------------------------------------
# Action decode
# ----------------------------------------------------------------------

def fmt_cell(topo, c: int) -> str:
    return "(" + ",".join(str(v) for v in topo.cell_to_coords(c)) + ")"


def decode(game, topo, a: int) -> str:
    if game.pie_rule and a == game.swap_action_idx:
        return f"PIE-SWAP [action {a}] (P2 takes over P1's position; goals swap too)"
    if a < game.total_cells:
        if not topo.active_mask[a]:
            return f"<cell {a} is a HOLE — never legal>"
        return f"PLACE @ {fmt_cell(topo, a)} [cell {a}]"
    if a == game.total_cells:
        return f"PASS [action {a}]"
    if game.action_rule.has_move():
        move_idx = a - game.total_cells - 1
        from_cell = move_idx // topo.max_degree
        nbr_idx = move_idx % topo.max_degree
        if from_cell < game.total_cells:
            nbrs = topo.get_neighbors(from_cell)
            if nbr_idx < len(nbrs):
                to_cell = nbrs[nbr_idx]
                return (f"MOVE {fmt_cell(topo, from_cell)} -> {fmt_cell(topo, to_cell)} "
                        f"[action {a}: from cell {from_cell}, neighbor #{nbr_idx} = cell {to_cell}]")
            return f"<invalid move action {a}: cell {from_cell} has no neighbor #{nbr_idx}>"
    return f"<unknown action {a}>"


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

def _blocks(engine, game, values: bool) -> list[tuple[str, list[str]]]:
    """Render the board as labeled (d0 x d1) blocks, one per combination of
    the remaining coordinates. Returns [(label, rows)]."""
    topo = game.get_topology()
    n = game.axis_size
    nd = game.num_dimensions

    def cell_str(c: int) -> str:
        if not topo.active_mask[c]:
            return "     #" if values else "#"
        if values:
            return f"{engine.board_values[c]:+6.2f}"
        v = int(engine.board_owners[c])
        return "X" if v == 1 else ("O" if v == 2 else ".")

    rest_dims = list(range(2, nd))
    combos = (list(itertools.product(range(n), repeat=len(rest_dims)))
              if rest_dims else [()])
    out = []
    for combo in combos:
        if rest_dims:
            label = ",".join(f"d{d}={v}" for d, v in zip(rest_dims, combo))
        else:
            label = ""
        rows = []
        for y in range(n):
            cells = []
            for x in range(n):
                coords = (x, y) + combo
                cells.append(cell_str(topo.coords_to_cell(coords)))
            rows.append(" ".join(cells))
        out.append((label, rows))
    return out


def render_board(engine, game, values: bool = False) -> str:
    n = game.axis_size
    blocks = _blocks(engine, game, values)
    cw = 6 if values else 1
    block_w = n * (cw + 1) - 1

    if len(blocks) == 1:
        # 2D: single grid with axis labels. rows = y (dim 1), cols = x (dim 0).
        _, rows = blocks[0]
        out = ["      x=" + " ".join(str(x).rjust(cw) for x in range(n))]
        for y, row in enumerate(rows):
            out.append(f"  y={y}  " + row)
        return "\n".join(out)

    # 3D+: bands of blocks side by side. Within each block cols = d0 (x),
    # left->right 0..n-1; rows = d1 (y), top->bottom 0..n-1.
    per_band = max(1, (110 + 4) // (block_w + 4))
    out = [f"  (within each block: columns = d0 = 0..{n-1} left->right, "
           f"rows = d1 = 0..{n-1} top->bottom)"]
    for i in range(0, len(blocks), per_band):
        band = blocks[i:i + per_band]
        out.append("  " + "    ".join(lbl.ljust(block_w) for lbl, _ in band))
        for y in range(n):
            out.append("  " + "    ".join(rows[y].ljust(block_w) for _, rows in band))
        out.append("")
    return "\n".join(out).rstrip()


# ----------------------------------------------------------------------
# Scores / status
# ----------------------------------------------------------------------

def score_lines(engine, game) -> list[str]:
    topo = game.get_topology()
    wc = game.win_condition
    ctype = wc.condition_type
    komi = float(getattr(game, "komi_p2", 0.0))
    if ctype == "threshold":
        p1 = sum(float(engine.board_values[c]) for c in topo.active_cells
                 if engine.board_owners[c] == 1)
        p2 = -sum(float(engine.board_values[c]) for c in topo.active_cells
                  if engine.board_owners[c] == 2)
        p2 += komi * wc.threshold
        return [f"scores (sum of influence on own stones): "
                f"P1={p1:+.3f}  P2={p2:+.3f}"
                + (f" (incl. P2 komi bonus {komi * wc.threshold:+.2f})" if komi else "")
                + f"  | win at > {wc.threshold:.3f}"]
    if ctype == "territory":
        target = wc.threshold * topo.num_active_cells
        p1 = engine.piece_counts[0]
        p2 = engine.piece_counts[1] + komi * topo.num_active_cells
        return [f"territory: P1 owns {engine.piece_counts[0]}/{topo.num_active_cells}"
                f"  P2 owns {engine.piece_counts[1]}/{topo.num_active_cells}"
                + (f" (+{komi * topo.num_active_cells:.1f} P2 komi cells)" if komi else "")
                + f"  | win at > {target:.2f} cells"
                + f"  (P1 to win: {max(0.0, target - p1):.2f} more; "
                  f"P2 to win: {max(0.0, target - p2):.2f} more)"]
    if ctype == "connection":
        dim_p2 = wc.target_dimension_p2
        if dim_p2 < 0:
            dim_p2 = (wc.target_dimension + 1) % game.num_dimensions
        d1, d2 = wc.target_dimension, dim_p2
        if engine._goals_swapped:
            d1, d2 = d2, d1
        return [f"connection goals: P1 must connect d{d1}=0 face to "
                f"d{d1}={game.axis_size-1} face; P2 must connect d{d2}=0 to "
                f"d{d2}={game.axis_size-1} (path of own stones, board adjacency)"]
    return []


def end_cause(engine) -> str:
    if not engine.done:
        return "in progress"
    if engine._ended_by_max_turns:
        return "max_turns reached -> piece-count majority tiebreak"
    if engine._winner is None and engine.consecutive_passes >= 2:
        return "double pass -> draw"
    return "win condition fired (incl. same-tick draws)"


def status_lines(engine, game) -> list[str]:
    out = [f"pieces: P1={engine.piece_counts[0]}  P2={engine.piece_counts[1]}"
           f"  | step={engine.step_count}/{game.max_game_steps}"
           f"  | done={engine.done}"
           f"  | winner={'P%d' % engine._winner if engine._winner else ('none' if not engine.done else 'DRAW')}"
           f"  | end cause: {end_cause(engine)}"]
    if not engine.done:
        line = f"to move: P{engine.current_player}"
        if game.turn_structure.turn_type == "multi_place":
            k = game.turn_structure.pieces_per_turn
            line += (f"  (multi-place: action {engine.placements_this_turn + 1}"
                     f" of {k} in P{engine.current_player}'s turn)")
        out.append(line)
    out.extend(score_lines(engine, game))
    return out


# ----------------------------------------------------------------------
# Legal actions
# ----------------------------------------------------------------------

def print_legal(engine, game) -> None:
    topo = game.get_topology()
    legal = engine.get_legal_actions()
    places = [a for a in legal if a < game.total_cells]
    moves = [a for a in legal
             if a > game.total_cells
             and not (game.pie_rule and a == game.swap_action_idx)]
    has_pass = game.total_cells in legal
    has_pie = game.pie_rule and game.swap_action_idx in legal

    print(f"Legal actions for P{engine.current_player}: {len(legal)} total")
    active_empty = [c for c in topo.active_cells if engine.board_owners[c] == 0]
    if places:
        if set(places) == set(active_empty):
            print(f"  PLACE: every empty active cell ({len(places)} cells, ids = cell index)")
        elif (game.placement_rule.target == "any"
                and set(places) == set(topo.active_cells)):
            print(f"  PLACE: every active cell ({len(places)} cells, ids = cell index;"
                  f" occupied cells may be overwritten in this game)")
        else:
            print(f"  PLACE ({len(places)} cells; id=(coords)):")
            line = "    "
            for a in places:
                tok = f"{a}={fmt_cell(topo, a)}"
                if len(line) + len(tok) > 100:
                    print(line)
                    line = "    "
                line += tok + "  "
            if line.strip():
                print(line)
    if moves:
        print(f"  MOVE ({len(moves)}):")
        for a in moves:
            print(f"    {a}: {decode(game, topo, a)}")
    if has_pass:
        print(f"  PASS: action {game.total_cells}")
    if has_pie:
        print(f"  PIE-SWAP: action {game.swap_action_idx} "
              f"(P2's first action only: swap into P1's position, goals swap too)")


# ----------------------------------------------------------------------
# Rules description (mechanics only — no provenance, no scores)
# ----------------------------------------------------------------------

def describe_rules(game, label: str) -> str:
    topo = game.get_topology()
    n = game.axis_size
    nd = game.num_dimensions
    wc = game.win_condition
    cap = game.capture_rule
    prop = game.propagation_rule
    ts = game.turn_structure
    ar = game.action_rule
    komi = float(getattr(game, "komi_p2", 0.0))
    out: list[str] = []

    # --- Topology ---
    degs = [len(topo.get_neighbors(c)) for c in topo.active_cells]
    out.append(f"=== Game {label} — rules (mechanics only) ===")
    out.append("")
    out.append(f"BOARD: topology={game.topology_type}, {nd}D, axis_size={n}, "
               f"{topo.num_active_cells} active cells / {topo.total_cells} grid cells"
               + (" (inactive cells are HOLES, rendered '#': never playable, "
                  "block adjacency)" if topo.num_active_cells < topo.total_cells else ""))
    if min(degs) == max(degs):
        out.append(f"  adjacency degree: {max(degs)} for every cell")
    else:
        out.append(f"  adjacency degree: min {min(degs)}, max {max(degs)} "
                   f"(varies by position; edge/corner/hole-adjacent cells have "
                   f"fewer neighbors)")
    if game.topology_type == "torus":
        out.append("  torus: every axis wraps around — opposite faces are adjacent; "
                   "no edges or corners (all cells degree "
                   f"{max(degs)}).")
    if game.topology_type == "moore":
        out.append("  moore adjacency: ALL cells within Chebyshev distance 1 are "
                   "neighbors (orthogonal + every diagonal, in every dimension).")
    if game.topology_type == "hex":
        out.append("  hex adjacency (offset rows): 6 neighbors interior — E, W, "
                   "N(y+1), S(y-1), plus (x-1,y±1) on even rows / (x+1,y±1) on odd rows.")
    if game.topology_type == "grid":
        out.append("  grid adjacency: orthogonal neighbors only (von Neumann), no wrap.")
    out.append(f"  coordinates: cell index = d0 + {n}*d1"
               + "".join(f" + {n**i}*d{i}" for i in range(2, nd))
               + "; coords printed as (d0,d1" + ",..." * (nd > 2) + ")"
               + ("; in 2D read d0=x (column), d1=y (row)" if nd == 2 else ""))

    # --- Actions ---
    out.append("")
    out.append(f"ACTIONS (total action-id space: {game.num_actions}):")
    out.append(f"  PLACE: ids 0..{game.total_cells - 1} = cell index (see formula above).")
    if game.placement_rule.target == "any":
        out.append("    placement target 'any': occupied cells are ALSO legal targets — "
                   "placing on an enemy stone REPLACES it; placing on your own stone "
                   "is a legal no-op placement (board unchanged).")
    else:
        out.append("    placement target 'empty': only unoccupied cells.")
    constraint = game.placement_rule.constraint
    ctext = {
        "anywhere": "no spatial constraint",
        "adjacent_to_own": "must be adjacent to at least one of YOUR stones",
        "adjacent_to_enemy": "must be adjacent to at least one ENEMY stone",
        "adjacent_to_any": "must be adjacent to any stone",
    }.get(constraint, constraint)
    out.append(f"    placement constraint: {ctext}.")
    if game.placement_rule.first_move_anywhere and constraint != "anywhere":
        out.append("    first_move_anywhere: while a player has ZERO stones on the "
                   "board the constraint is waived (anywhere legal) — this re-arms "
                   "if all your stones are ever removed.")
    out.append(f"  PASS: id {game.total_cells}. Two consecutive passes (by either "
               "sequence of actors) end the game as a DRAW.")
    if ar.has_move():
        out.append(f"  MOVE: ids {game.total_cells + 1}..{game.total_cells + game.total_cells * topo.max_degree}, "
                   f"encoded as {game.total_cells} + 1 + from_cell*{topo.max_degree} + neighbor_index.")
        out.append(f"    moves relocate one of YOUR stones to an adjacent "
                   f"{'EMPTY cell' if ar.move_constraint == 'adjacent_empty' else 'cell (overwriting enemy stones)'}.")
        out.append("    neighbor_index is positional in the cell's neighbor list — "
                   "use --legal to see each move id decoded as from->to coords.")
    if game.pie_rule:
        out.append(f"  PIE-SWAP: id {game.swap_action_idx}, legal ONLY as P2's first "
                   "action. Swaps seats: stone colours flip, influence negates, and "
                   "win goals swap, so P2 takes over P1's opening. After the swap the "
                   "original P1 moves next (now playing O).")
    else:
        out.append("  (no pie rule in this game)")

    # --- Turn structure ---
    out.append("")
    if ts.turn_type == "multi_place":
        out.append(f"TURNS: multi-place — each player takes {ts.pieces_per_turn} "
                   f"consecutive actions before the turn passes to the opponent "
                   f"(each action is a separate engine step; --legal shows whose "
                   f"action it is and which action of the turn).")
        out.append("  NOTE: a PASS consumes one of the turn's actions, and two "
                   "consecutive passes end the game in a draw EVEN inside one "
                   "player's multi-place turn.")
    else:
        out.append("TURNS: alternating — one action per player per turn.")

    # --- CA ---
    if game.uses_ca:
        ca = game.ca_rule
        out.append("")
        out.append(f"CELLULAR AUTOMATON — THE BOARD MUTATES BETWEEN TURNS:")
        out.append(f"  After EVERY action (each placement, each pass), the CA rule is "
                   f"applied {ca.steps_per_turn} time(s) to the whole board "
                   f"simultaneously. Stones can be born, die, or flip colour without "
                   f"either player touching them.")
        out.append("  The rule is totalistic from the ACTING player's perspective: "
                   "new_state = T(cell_state, #friendly_neighbors, #enemy_neighbors), "
                   "where 'friendly' = the player who just acted. Cells not matched "
                   "by the table are unchanged.")
        out.append(f"  The table only covers neighbor counts 0..{ca.max_neighbors} "
                   f"(per side). On this board cells can have up to {max(degs)} "
                   f"neighbors — any cell whose friendly or enemy count exceeds "
                   f"{ca.max_neighbors} is NOT in the table and therefore never "
                   f"changes that step.")
        nonid = sorted(
            (k, v) for k, v in ca.transition_table.items() if v != k[0]
        )
        state_name = {0: "empty", 1: "actor's", 2: "opponent's"}
        new_name = {0: "cell EMPTIES", 1: "becomes ACTOR's stone",
                    2: "becomes OPPONENT's stone"}
        out.append(f"  Non-identity transitions ({len(nonid)} of "
                   f"{len(ca.transition_table)} entries):")
        for (s, f, e), v in nonid:
            out.append(f"    {state_name[s]:>10s} cell, {f} friendly + {e} enemy "
                       f"neighbors -> {new_name[v]}")
        out.append("  In CA games the classic capture and propagation rules are "
                   "DISABLED by the engine (the CA is the only board-transformation "
                   "mechanic).")

    # --- Capture ---
    out.append("")
    if game.uses_ca:
        out.append(f"CAPTURE: rule field says '{cap.capture_type}' but it is "
                   f"VESTIGIAL — CA games skip classic captures entirely (see above).")
    elif cap.capture_type == "none":
        out.append("CAPTURE: none. (The capture 'threshold' field "
                   f"({cap.threshold}) is vestigial.)")
    elif cap.capture_type == "custodian":
        out.append("CAPTURE: custodian (Othello-like). After your placement, walk "
                   "each axis-aligned line from the placed cell in both directions: "
                   "consecutive enemy stones that end on one of YOUR stones are "
                   "FLIPPED to your colour.")
        if game.topology_type == "torus":
            out.append("  ENGINE QUIRK (verified): custodian line-walks CLAMP at the "
                   "coordinate bounds 0.." + str(n - 1) + " — they do NOT wrap "
                   "around the torus, even though adjacency does. No wrap-around "
                   "custodian captures exist.")
        out.append(f"  (capture threshold field ({cap.threshold}) is vestigial for "
                   "custodian.)")
    elif cap.capture_type == "surround":
        out.append("CAPTURE: surround (Go-like). After your placement, any adjacent "
                   "enemy GROUP (connected same-colour component) with zero "
                   "liberties (no empty adjacent cell) is REMOVED from the board.")
        out.append(f"  (capture threshold field ({cap.threshold}) is vestigial for "
                   "surround.)")
    elif cap.capture_type == "outnumber":
        out.append(f"CAPTURE: outnumber. After your placement, each enemy stone "
                   f"ADJACENT TO THE PLACED CELL that has >= {cap.threshold} "
                   f"friendly (your) neighbors is REMOVED (cleared, not flipped).")
    if (not game.uses_ca and cap.capture_type != "none"
            and prop.prop_type == "influence"):
        out.append("  GHOST INFLUENCE (verified engine behaviour): captures change "
                   "stone ownership but do NOT update the influence field — a "
                   "captured/flipped stone's influence stays on the board with its "
                   "ORIGINAL sign forever.")

    # --- Propagation ---
    out.append("")
    if game.uses_ca:
        out.append(f"PROPAGATION: rule field says '{prop.prop_type}' but CA games "
                   "skip propagation — vestigial (incl. radius/strength/decay "
                   "parameters).")
    elif prop.prop_type == "none":
        out.append("PROPAGATION: none — no influence field. (The radius/strength/"
                   "decay parameters in the rule blob are vestigial.)")
    elif prop.prop_type == "influence":
        out.append(f"PROPAGATION: influence. Each placement adds "
                   f"strength*decay^distance to board_values for all cells within "
                   f"topological distance {prop.radius} of the placed cell "
                   f"(strength={prop.strength:.4f}, decay={prop.decay:.4f}; "
                   f"positive = P1, negative = P2; values clamp at ±100). "
                   f"Influence is permanent once placed (see --values).")
        if prop.decay == 1.0:
            out.append("  decay=1.0: no fall-off — every cell within the radius "
                       "gets the FULL strength.")
        if ar.has_move():
            out.append("  NOTE: moves re-apply influence at the destination; the "
                       "influence left at the origin is NOT removed.")

    # --- Win condition ---
    out.append("")
    ctype = wc.condition_type
    if ctype == "connection":
        dim_p2 = wc.target_dimension_p2
        if dim_p2 < 0:
            dim_p2 = (wc.target_dimension + 1) % nd
        out.append(f"WIN — CONNECTION (Hex-style, asymmetric goals):")
        out.append(f"  P1 wins by connecting the d{wc.target_dimension}=0 face to the "
                   f"d{wc.target_dimension}={n-1} face with a path of P1 stones "
                   f"(path steps use board adjacency).")
        out.append(f"  P2 wins by connecting the d{dim_p2}=0 face to the "
                   f"d{dim_p2}={n-1} face with a path of P2 stones.")
        out.append("  If both players complete their connection on the same tick"
                   + (" (possible because the CA changes the board)" if game.uses_ca
                      else "") + ", the game is a DRAW.")
        out.append(f"  (The win_condition 'threshold' field ({wc.threshold:.3f}) is "
                   "VESTIGIAL under connection.)")
    elif ctype == "threshold":
        bonus = komi * wc.threshold
        out.append(f"WIN — THRESHOLD (influence race):")
        out.append(f"  A player wins when the sum of board_values over the cells "
                   f"they OWN exceeds {wc.threshold:.3f} (P1 sums +values; P2 sums "
                   f"-values, i.e. sign-corrected).")
        out.append(f"  komi_p2={komi:.2f}: P2's effective score gets "
                   f"{bonus:+.2f} added (komi_p2 x threshold)."
                   if komi else
                   "  komi_p2=0.00: no scoring bonus for either side.")
        out.append("  A stone you own standing on net-ENEMY influence SUBTRACTS "
                   "from your score. If both players cross on the same tick the "
                   "higher margin wins (exact tie -> draw).")
        out.append("  (target_dimension fields are vestigial under threshold.)")
    elif ctype == "territory":
        target = wc.threshold * topo.num_active_cells
        out.append(f"WIN — TERRITORY (stone-count race):")
        out.append(f"  A player wins the moment they OWN more than "
                   f"{wc.threshold:.4f} x {topo.num_active_cells} = {target:.2f} "
                   f"cells (i.e. at least {int(target) + 1} stones).")
        if komi:
            out.append(f"  komi_p2={komi:.2f}: P2 counts "
                       f"{komi * topo.num_active_cells:.1f} virtual extra cells.")
        else:
            out.append("  komi_p2=0.00: no virtual-cell bonus for either side.")
        out.append("  (target_dimension and the propagation params play no role.)")
    out.append(f"  max_turns={wc.max_turns}: if no one has won after "
               f"{wc.max_turns} engine steps, the player with MORE STONES on the "
               f"board wins (equal -> draw).")
    out.append("  Double pass at any point -> immediate DRAW (the win condition is "
               "the only path to a decisive result besides the turn-limit tiebreak).")

    # --- Repetition rule ---
    if game.needs_ko_rule:
        out.append("")
        out.append("REPETITION (super-ko): if an action would recreate a previous "
                   "board position (same stones + same player to move), the engine "
                   "ROLLS THE ACTION BACK and treats it as a PASS. The helper flags "
                   "this when it happens. (For CA games the check runs on the "
                   "post-CA position.)")

    return "\n".join(out)


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(
        description="Blind-eval game runner (games A-G).")
    p.add_argument("--game", required=True, help="blind label A..G")
    p.add_argument("--rules", action="store_true",
                   help="print the game's mechanics and exit")
    p.add_argument("--moves", default="",
                   help="csv of action ids to apply from the initial position")
    p.add_argument("--legal", action="store_true",
                   help="print legal action ids (decoded) for the player to move")
    p.add_argument("--values", action="store_true",
                   help="render the influence field too (influence games only)")
    args = p.parse_args()

    label = args.game.strip().upper()
    game = load_game(label)
    topo = game.get_topology()

    if args.rules:
        print(describe_rules(game, label))
        return

    engine = create_engine(game)
    engine.reset()

    print(f"=== Game {label} ===")
    moves = [int(x) for x in args.moves.split(",") if x.strip()]
    for i, a in enumerate(moves):
        actor = engine.current_player
        legal = engine.get_legal_actions()
        if a not in legal:
            print(f"\n!! Ply {i+1}: action {a} is ILLEGAL for P{actor}.")
            print(f"   decoded: {decode(game, topo, a)}")
            print(f"   {len(legal)} legal actions (sample: {legal[:10]}...). "
                  f"Use --legal to list them.")
            sys.exit(2)
        decoded = game.decode_action(a)
        pre_owners = engine.board_owners.copy()
        pre_passes = engine.consecutive_passes
        engine.step(a)

        print(f"\n--- Ply {i+1} (P{actor}): {decode(game, topo, a)}")
        # Super-ko rollback detection: a place/move that ends with the pass
        # counter incremented was rolled back and converted to a pass.
        if (decoded["type"] in ("place", "move")
                and engine.consecutive_passes == pre_passes + 1):
            print("    !! SUPER-KO: this action recreated a previous position — "
                  "rolled back and treated as a PASS.")
        # Board delta
        changes = []
        sym = {0: ".", 1: "X", 2: "O"}
        for c in topo.active_cells:
            before, after = int(pre_owners[c]), int(engine.board_owners[c])
            if before != after:
                changes.append(f"{sym[before]}->{sym[after]}@{fmt_cell(topo, c)}")
        if changes:
            action_cells = {decoded.get("cell"), decoded.get("from_cell"),
                            decoded.get("to_cell")} - {None}
            extra = [ch for ch, c in
                     [(f"{sym[int(pre_owners[c])]}->{sym[int(engine.board_owners[c])]}@{fmt_cell(topo, c)}", c)
                      for c in topo.active_cells
                      if int(pre_owners[c]) != int(engine.board_owners[c])]
                     if c not in action_cells]
            shown = changes[:14]
            print(f"    board delta ({len(changes)} cells): " + "  ".join(shown)
                  + ("  ..." if len(changes) > 14 else ""))
            if game.uses_ca and extra:
                print(f"    ^ {len(extra)} of these were CA mutations "
                      f"(cells neither placed on nor moved).")
        else:
            print("    board delta: none (no cell changed owner)")
        for line in status_lines(engine, game):
            print(f"    {line}")
        if engine.done:
            if i + 1 < len(moves):
                print(f"    (game over — remaining {len(moves) - i - 1} "
                      f"moves ignored)")
            break

    print(f"\n=== Board after {min(len(moves), engine.step_count)} "
          f"plies (X=P1, O=P2, .=empty, #=hole) ===")
    print(render_board(engine, game))
    if args.values:
        if game.propagation_rule.prop_type == "influence" and not game.uses_ca:
            print("\n=== Influence field (board_values; +:P1, -:P2) ===")
            print(render_board(engine, game, values=True))
        else:
            print("\n(--values: this game has no live influence field — nothing "
                  "to render)")
    print()
    for line in status_lines(engine, game):
        print(line)
    if args.legal and not engine.done:
        print()
        print_legal(engine, game)


if __name__ == "__main__":
    main()
