"""Blind agent A/B eval helper — games Q and Z.

Loads game defs from calibrated JSONs via blind labels (Q/Z). Renders
the stone board and (for influence games) the control map; reports
scores/connection progress and legal actions. Run --rules first to obtain
a mechanical rules summary for each game.

Usage:
    python experiments/field_connect_probe/eval_helper.py --game Q --rules
    python experiments/field_connect_probe/eval_helper.py --game Z --rules
    python experiments/field_connect_probe/eval_helper.py --game Q
    python experiments/field_connect_probe/eval_helper.py --game Z \
        --moves "245,108,246" --control
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from game_engine.factory import create_engine  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402

from experiments.field_connect_probe.metrics import (  # noqa: E402
    controlled_sets,
    largest_component,
    progress_diff_threshold,
)

HERE = Path(__file__).resolve().parent
BLIND = json.load(open(ROOT / "evaluations" / "field_connect_probe"
                       / ".blind_mapping.json"))


def load_game(label: str) -> GameDefV2:
    name = BLIND[label.upper()]
    return GameDefV2.from_dict(
        json.load(open(HERE / "games" / "calibrated" / f"{name}.json"))
    )


def render(engine, game, show_control: bool) -> str:
    s = game.axis_size
    topo = engine.topo
    out = []
    for r in range(s):
        row = [" " * r]  # axial shear: indent row r by r half-cells
        for q in range(s):
            c = topo.coords_to_cell((q, r))
            o = int(engine.board_owners[c])
            row.append("X" if o == 1 else "O" if o == 2 else "·")
        out.append(" ".join(row))
    if show_control:
        margin = getattr(game.win_condition, "control_margin", 0.0)
        out.append("")
        out.append("control map (+ = P1-controlled, - = P2, · = contested):")
        for r in range(s):
            row = [" " * r]
            for q in range(s):
                v = float(engine.board_values[topo.coords_to_cell((q, r))])
                row.append("+" if v > margin else "-" if v < -margin else "·")
            out.append(" ".join(row))
    return "\n".join(out)


def status(engine, game) -> str:
    wc = game.win_condition
    lines = [f"step={engine.step_count} player_to_move="
             f"P{engine.current_player} done={engine.done} "
             f"winner={engine._winner}"]
    if wc.condition_type == "field_connection":
        margin = getattr(wc, "control_margin", 0.0)
        p1, p2 = controlled_sets(engine, margin)
        lines.append(
            f"controlled cells: P1={len(p1)} P2={len(p2)} "
            f"largest components: P1={largest_component(engine.topo, p1)} "
            f"P2={largest_component(engine.topo, p2)} "
            f"(P1 connects r=0<->r={game.axis_size-1}, "
            f"P2 connects q=0<->q={game.axis_size-1}; komi on timeout "
            f"tiebreak: {game.komi_p2})"
        )
    else:
        lines.append(
            f"score differential (P1 - P2, komi applied): "
            f"{progress_diff_threshold(engine):.2f} "
            f"(threshold {wc.threshold}, komi_p2 {game.komi_p2})"
        )
    legal = engine.get_legal_actions()
    lines.append(f"legal actions: {len(legal)} "
                 f"(cell index = q + {game.axis_size}*r; "
                 f"pass={game.axis_size**2}, swap={game.axis_size**2+1})")
    return "\n".join(lines)


def rules_summary(game: GameDefV2) -> str:
    """Print a mechanical, neutral rules summary derived from the game def.

    The text is symmetric in tone for both games — it describes rules in the
    same neutral register without revealing which variant is which.
    """
    topo = game.get_topology()
    wc = game.win_condition
    cap = game.capture_rule
    prop = game.propagation_rule

    lines = []
    lines.append("=== GAME RULES SUMMARY ===")
    lines.append("")

    # Board
    s = game.axis_size
    total = game.total_cells
    active = topo.num_active_cells
    max_deg = topo.max_degree
    lines.append(f"Board: {s}×{s} rhombus ({total} cells total, {active} active).")
    lines.append(f"Adjacency: triangular lattice (hex), max degree {max_deg}.")
    lines.append(f"  Cell indexing: cell = q + {s}*r  where q is column (0..{s-1}),")
    lines.append(f"  r is row (0..{s-1}). Rows are sheared — each row r shifts right by r.")
    lines.append("")

    # Placement
    lines.append("Placement: one stone per turn, any empty cell.")
    lines.append("")

    # Capture
    ctype = cap.capture_type
    cthresh = cap.threshold
    if ctype == "outnumber":
        lines.append(
            f"Capture (outnumber-{cthresh}): after placing, any enemy stone that "
            f"has >= {cthresh} friendly neighbours is immediately removed (cleared to empty). "
            f"Captures are single stones; checked after each placement."
        )
    elif ctype == "surround":
        lines.append(
            f"Capture (surround): after placing, any enemy group with zero "
            f"empty-cell liberties is immediately removed (cleared to empty). "
            f"Groups = connected same-owner stones. Threshold field={cthresh} (vestigial for surround)."
        )
    elif ctype == "custodian":
        lines.append(
            f"Capture (custodian-{cthresh}): after placing, any enemy run "
            f"bracketed by {cthresh}+ friendly stones along an axis flips to friendly."
        )
    elif ctype == "none":
        lines.append("Capture: none.")
    else:
        lines.append(f"Capture: {ctype}, threshold={cthresh}.")
    lines.append("")

    # Influence / propagation
    ptype = prop.prop_type
    if ptype == "influence":
        r = prop.radius
        s_val = prop.strength
        d_val = prop.decay
        lines.append(
            f"Influence field: each placed stone adds ±strength·decay^dist to "
            f"board_values within radius {r}. Placing P1 stone: +{s_val}·{d_val}^dist; "
            f"P2: -{s_val}·{d_val}^dist. Values clamped [-100, 100]. "
            f"Radius={r}, strength={s_val}, decay={d_val}."
        )
    else:
        lines.append(f"Influence/propagation: {ptype}.")
    lines.append("")

    # Win condition
    cond = wc.condition_type
    if cond == "threshold":
        lines.append(
            f"Win condition (score race): the first player whose sum of "
            f"board_values over their owned cells exceeds {wc.threshold} wins. "
            f"P1 accumulates positive values; P2 accumulates negative values "
            f"(negated for comparison). P2 komi bonus = komi_p2 * threshold "
            f"(komi_p2={game.komi_p2})."
        )
        lines.append(
            f"Timeout ({wc.max_turns} turns): player with higher effective score wins; "
            f"equal is a draw."
        )
    elif cond == "field_connection":
        margin = getattr(wc, "control_margin", 0.0)
        p1_dim = wc.target_dimension
        p2_dim = wc.target_dimension_p2
        # Translate dimension indices to axis names
        p1_axis = "r" if p1_dim == 1 else "q"
        p2_axis = "q" if p2_dim == 0 else "r"
        lines.append(
            f"Win condition (influence-field connection): a player wins when "
            f"their controlled cells form a connected path across the board. "
            f"A cell is controlled by P1 if board_values > +{margin}; "
            f"by P2 if board_values < -{margin}; otherwise contested."
        )
        lines.append(
            f"P1 must connect {p1_axis}=0 to {p1_axis}={game.axis_size-1} "
            f"(top-to-bottom in the sheared display)."
        )
        lines.append(
            f"P2 must connect {p2_axis}=0 to {p2_axis}={game.axis_size-1} "
            f"(left-to-right in the sheared display)."
        )
        lines.append(
            f"Komi_p2={game.komi_p2} applies at timeout tiebreak only."
        )
        lines.append(
            f"Timeout ({wc.max_turns} turns): player with larger largest-controlled-component wins; "
            f"komi breaks tie."
        )
    elif cond == "connection":
        lines.append(
            f"Win condition (stone connection): a player wins by placing stones "
            f"that form a connected path across the board. "
            f"P1: dimension {wc.target_dimension}; P2: dimension {wc.target_dimension_p2}."
        )
    else:
        lines.append(f"Win condition: {cond}, threshold={wc.threshold}.")
    lines.append("")

    # Pie rule
    if game.pie_rule:
        swap_idx = game.swap_action_idx
        lines.append(
            f"Pie rule: ON. After P1's first stone, P2 may swap seats (inherit P1's "
            f"stone as their own and become the first mover). Swap action index = {swap_idx}."
        )
    else:
        lines.append("Pie rule: OFF.")
    lines.append("")

    # Komi
    lines.append(f"Komi_p2: {game.komi_p2} (fractional advantage added to P2's effective score).")
    lines.append("")

    # Action space
    pass_idx = game.total_cells
    lines.append(f"Action space: {game.num_actions} total actions.")
    lines.append(f"  Placement: actions 0..{game.total_cells - 1} (cell index = q + {game.axis_size}*r).")
    lines.append(f"  Pass: action {pass_idx}.")
    if game.pie_rule:
        lines.append(f"  Swap (pie): action {game.swap_action_idx}.")
    lines.append("")

    lines.append("=== END RULES ===")
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--game", required=True, choices=["Q", "Z", "q", "z"])
    p.add_argument("--moves", default="",
                   help="comma-separated action ids to replay")
    p.add_argument("--control", action="store_true",
                   help="also render the influence control map")
    p.add_argument("--rules", action="store_true",
                   help="print a neutral mechanical rules summary then exit")
    args = p.parse_args()

    game = load_game(args.game)

    if args.rules:
        print(rules_summary(game))
        return

    engine = create_engine(game)
    engine.reset()
    for tok in [t for t in args.moves.split(",") if t.strip()]:
        if engine.done:
            print("game already over — remaining moves ignored")
            break
        engine.step(int(tok))
    print(render(engine, game, args.control))
    print()
    print(status(engine, game))


if __name__ == "__main__":
    main()
