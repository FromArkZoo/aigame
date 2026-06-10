"""Blind agent eval helper — games D, V, X.

Loads game definitions via blind labels (D/V/X). Renders the stone board and
influence control map; reports game progress and legal actions. Run --rules
first to obtain a mechanical rules summary for each game.

Usage (evaluator entry point):
    python evaluations/stage3_ab/play.py --game D --rules
    python evaluations/stage3_ab/play.py --game V --rules
    python evaluations/stage3_ab/play.py --game X --rules
    python evaluations/stage3_ab/play.py --game X
    python evaluations/stage3_ab/play.py --game X \\
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
)

HERE = Path(__file__).resolve().parent
_MAPPING = json.load(
    open(ROOT / "evaluations" / "stage3_ab" / ".blind_mapping.json",
         encoding="utf-8")
)

# Resolve each label to an absolute path.
# D/V → experiments/siege/games/calibrated/{name}.json  (produced by Stage 1)
# X   → experiments/siege/games/{name}.json             (comparator, always present)
def _resolve_path(label: str) -> Path:
    name = _MAPPING[label.upper()]
    if label.upper() == "X":
        path = HERE / "games" / f"{name}.json"
    else:
        path = HERE / "games" / "calibrated" / f"{name}.json"
    return path


def load_game(label: str) -> GameDefV2:
    path = _resolve_path(label.upper())
    if not path.exists():
        # NOTE: never include the resolved path in this message — it contains
        # the unblinded arm name and evaluators may trigger this error.
        raise FileNotFoundError(
            f"Game file not found for label {label.upper()!r}. "
            f"Calibration has not produced this arm yet — ask the orchestrator."
        )
    return GameDefV2.from_dict(json.load(open(path, encoding="utf-8")))


def render(engine, game, show_control: bool) -> str:
    s = game.axis_size
    topo = engine.topo
    out = []
    for r in range(s):
        row = [" " * r]
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
    turns_remaining = wc.max_turns - engine.step_count
    lines = [
        f"step={engine.step_count} player_to_move=P{engine.current_player} "
        f"done={engine.done} winner={engine._winner} "
        f"turns_remaining={turns_remaining}"
    ]

    margin = getattr(wc, "control_margin", 0.0)
    p1_cells, p2_cells = controlled_sets(engine, margin)

    # Progress for the influence-connection role (P1 in asymmetric, both in symmetric)
    lc_p1 = largest_component(engine.topo, p1_cells)
    lc_p2 = largest_component(engine.topo, p2_cells)
    lines.append(
        f"controlled cells: P1={len(p1_cells)} P2={len(p2_cells)} "
        f"largest components: P1={lc_p1} P2={lc_p2} "
        f"(P1 connects r=0<->r={game.axis_size - 1}, "
        f"P2 connects q=0<->q={game.axis_size - 1}; components are "
        f"progress info only — timeout is decided by total controlled-cell count)"
    )

    # If there is a secondary win path with a conversion count, report it neutrally
    quota = getattr(wc, "capture_quota", 0)
    if quota > 0:
        ticks = getattr(engine, "_quota_ticks", 0)
        lines.append(f"conversion count: {ticks}/{quota}")

    legal = engine.get_legal_actions()
    lines.append(
        f"legal actions: {len(legal)} "
        f"(cell index = q + {game.axis_size}*r; "
        f"pass={game.axis_size ** 2}, swap={game.axis_size ** 2 + 1})"
    )
    return "\n".join(lines)


def rules_summary(game: GameDefV2) -> str:
    """Print a mechanical, neutral rules summary derived from the game definition.

    The text describes rules in the same neutral register for all three games
    without revealing experimental identities, arm roles, or variant names.
    """
    topo = game.get_topology()
    wc = game.win_condition
    cap = game.capture_rule
    prop = game.propagation_rule

    lines = []
    lines.append("=== GAME RULES SUMMARY ===")
    lines.append("")

    # --- Board ---
    s = game.axis_size
    total = game.total_cells
    active = topo.num_active_cells
    max_deg = topo.max_degree
    lines.append(f"Board: {s}×{s} rhombus ({total} cells total, {active} active).")
    lines.append(f"Adjacency: triangular lattice (hex), max degree {max_deg}.")
    lines.append(f"  Cell indexing: cell = q + {s}*r  where q is column (0..{s - 1}),")
    lines.append(f"  r is row (0..{s - 1}). Rows are sheared — each row r shifts right by r.")
    lines.append("")

    # --- Placement ---
    lines.append("Placement: one stone per turn, any empty cell.")
    lines.append("")

    # --- Capture ---
    ctype = cap.capture_type
    cthresh = cap.threshold
    if ctype == "field_flip":
        lines.append(
            "Capture (influence-flip): after each placement, all enemy stones "
            "that stand on cells where the influence field is dominated by the "
            "active player are immediately converted to that player's colour. "
            "Conversions are checked after the influence field is updated and "
            "can cascade: each conversion shifts the field further, potentially "
            "triggering additional conversions in the same turn. "
            "The influence field uses the same radius/strength/decay as the "
            "propagation rule."
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
    elif ctype == "outnumber":
        lines.append(
            f"Capture (outnumber-{cthresh}): after placing, any enemy stone "
            f"that has >= {cthresh} friendly neighbours is immediately removed. "
            f"Captures are single stones; checked after each placement."
        )
    elif ctype == "none":
        lines.append("Capture: none.")
    else:
        lines.append(f"Capture: {ctype}, threshold={cthresh}.")
    lines.append("")

    # --- Influence / propagation ---
    ptype = prop.prop_type
    if ptype == "influence":
        r = prop.radius
        s_val = prop.strength
        d_val = prop.decay
        lines.append(
            f"Influence field: each placed stone adds ±strength·decay^dist to "
            f"board_values within radius {r}. Placing a P1 stone: +{s_val}·{d_val}^dist; "
            f"P2: -{s_val}·{d_val}^dist. Values clamped [-100, 100]. "
            f"Radius={r}, strength={s_val}, decay={d_val}."
        )
    else:
        lines.append(f"Influence/propagation: {ptype}.")
    lines.append("")

    # --- Win condition ---
    cond = wc.condition_type
    max_turns = wc.max_turns
    margin = getattr(wc, "control_margin", 0.0)

    # Check whether there is a secondary win path (conversion count)
    quota = getattr(wc, "capture_quota", 0)
    timeout_winner_side = getattr(wc, "timeout_winner", 0)

    if cond == "field_connection" and quota > 0:
        # Asymmetric: two distinct win conditions, one per side
        p1_dim = wc.target_dimension
        p1_axis = "r" if p1_dim == 1 else "q"
        lines.append(
            f"Win conditions (two independent paths — one per side):"
        )
        lines.append("")
        lines.append(
            f"  Player 1 wins by connecting {p1_axis}=0 to {p1_axis}={s - 1} "
            f"with cells their influence controls. A cell is controlled by P1 "
            f"if board_values > +{margin}."
        )
        lines.append("")
        p2_clause = (
            f"  Player 2 wins by converting {quota} opposing stones "
            f"(each stone counts once toward the total; a stone that flips back "
            f"and forth is not counted again)"
        )
        if timeout_winner_side == 2:
            p2_clause += (
                f" or when the turn limit of {max_turns} turns is reached "
                f"(whichever comes first)."
            )
        else:
            p2_clause += "."
        lines.append(p2_clause)
        lines.append("")
        lines.append(
            f"Both players' placements can convert opposing stones where their "
            f"influence dominates — only Player 2's conversions count toward "
            f"the {quota}-stone total."
        )
        lines.append("")
        if timeout_winner_side == 2:
            lines.append(
                f"Turn limit: {max_turns} turns. If the turn limit is reached "
                f"before either side has won, Player 2 wins."
            )
        elif timeout_winner_side == 1:
            lines.append(
                f"Turn limit: {max_turns} turns. If the turn limit is reached "
                f"before either side has won, Player 1 wins."
            )
        else:
            lines.append(
                f"Turn limit ({max_turns} turns): if no player has satisfied "
                f"their win condition, the side that reaches the limit wins."
            )
    elif cond == "field_connection":
        # Symmetric: both sides use influence-field connection
        p1_dim = wc.target_dimension
        p2_dim = wc.target_dimension_p2
        p1_axis = "r" if p1_dim == 1 else "q"
        p2_axis = "q" if p2_dim == 0 else "r"
        lines.append(
            f"Win condition (influence-field connection): a player wins when "
            f"their controlled cells form a connected path across the board. "
            f"A cell is controlled by P1 if board_values > +{margin}; "
            f"by P2 if board_values < -{margin}; otherwise contested."
        )
        lines.append(
            f"P1 must connect {p1_axis}=0 to {p1_axis}={s - 1} "
            f"(top-to-bottom in the sheared display)."
        )
        lines.append(
            f"P2 must connect {p2_axis}=0 to {p2_axis}={s - 1} "
            f"(left-to-right in the sheared display)."
        )
        lines.append(
            f"Komi_p2={game.komi_p2} applies at timeout tiebreak only."
        )
        lines.append(
            f"Timeout ({max_turns} turns): player with the higher TOTAL "
            f"controlled-cell count wins (NOT largest component); P2's count "
            f"gains komi_p2 * {topo.num_active_cells} virtual cells; equal is a draw."
        )
    elif cond == "threshold":
        lines.append(
            f"Win condition (score race): the first player whose sum of "
            f"board_values over their owned cells exceeds {wc.threshold} wins. "
            f"P1 accumulates positive values; P2 accumulates negative values "
            f"(negated for comparison). P2 komi bonus = komi_p2 * threshold "
            f"(komi_p2={game.komi_p2})."
        )
        lines.append(
            f"Timeout ({max_turns} turns): player with MORE STONES on the "
            f"board wins (piece-count majority — NOT the score); equal is a draw."
        )
    else:
        lines.append(f"Win condition: {cond}, threshold={wc.threshold}.")
    lines.append("")

    # --- Pie rule ---
    if game.pie_rule:
        swap_idx = game.swap_action_idx
        lines.append(
            f"Pie rule: ON. After P1's first stone, P2 may swap seats (inherit P1's "
            f"stone as their own and become the first mover). Swap action index = {swap_idx}."
        )
    else:
        lines.append("Pie rule: OFF.")
    lines.append("")

    # --- Komi ---
    lines.append(
        f"Komi_p2: {game.komi_p2} (fractional advantage added to P2's effective score)."
    )
    lines.append("")

    # --- Action space ---
    pass_idx = game.total_cells
    lines.append(f"Action space: {game.num_actions} total actions.")
    lines.append(
        f"  Placement: actions 0..{game.total_cells - 1} (cell index = q + {game.axis_size}*r)."
    )
    lines.append(f"  Pass: action {pass_idx}.")
    if game.pie_rule:
        lines.append(f"  Swap (pie): action {game.swap_action_idx}.")
    lines.append("")

    lines.append("=== END RULES ===")
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(prog="play.py", description=__doc__)
    p.add_argument("--game", required=True, choices=["D", "V", "X", "d", "v", "x"])
    p.add_argument("--moves", default="",
                   help="comma-separated action ids to replay")
    p.add_argument("--control", action="store_true",
                   help="also render the influence control map")
    p.add_argument("--rules", action="store_true",
                   help="print a neutral mechanical rules summary then exit")
    args = p.parse_args()

    label = args.game.upper()

    if args.rules:
        try:
            game = load_game(label)
        except FileNotFoundError as exc:
            print(str(exc))
            sys.exit(1)
        print(rules_summary(game))
        return

    try:
        game = load_game(label)
    except FileNotFoundError as exc:
        print(str(exc))
        sys.exit(1)

    engine = create_engine(game)
    engine.reset()
    tokens = [t.strip() for t in args.moves.split(",") if t.strip()]
    for n, tok in enumerate(tokens, start=1):
        if engine.done:
            print("game already over — remaining moves ignored")
            break
        try:
            a = int(tok)
        except ValueError:
            print(f"error: ValueError: invalid move token {tok!r} "
                  f"(must be an integer action id)")
            sys.exit(1)
        legal = engine.get_legal_actions()
        if a not in legal:
            print(f"error: illegal action {a} at step {n} — "
                  f"legal count {len(legal)}")
            sys.exit(1)
        engine.step(a)
    print(render(engine, game, args.control))
    print()
    print(status(engine, game))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"error: {type(exc).__name__}: invalid input or internal error")
        sys.exit(1)
