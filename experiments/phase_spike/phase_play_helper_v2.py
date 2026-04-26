"""CLI for engine-verified 4-phase complex game play.

Move format: <cell><N|E|S|W> where N=0°, E=90°, S=180°, W=270°.
  Examples: "27N" places at cell 27 with phase 0° (P1's target axis).
            "36S" places at cell 36 with phase 180° (P2's target axis).
            "27E" places at cell 27 with phase 90° (orthogonal / neutral).
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.phase_spike.phase_game_v2 import (
    PhaseGameV2,
    AXIS_SIZE, TOTAL_CELLS, INFLUENCE_RADIUS, INFLUENCE_STRENGTH,
    INFLUENCE_DECAY, CAPTURE_THRESHOLD, WIN_THRESHOLD, MAX_TURNS,
    PASS_ACTION, encode_action, decode_action,
    PHASE_NAMES, parse_phase_letter,
)


def parse_move(token: str) -> int:
    token = token.strip().lower()
    if token == "pass":
        return PASS_ACTION
    if not token:
        raise ValueError("empty move token")
    if token[-1] not in "neswNESW":
        raise ValueError(f"move token must end in N/E/S/W, got {token!r}")
    cell = int(token[:-1])
    if not 0 <= cell < TOTAL_CELLS:
        raise ValueError(f"cell out of range: {cell}")
    phase_idx = parse_phase_letter(token[-1])
    return encode_action(cell, phase_idx)


def cmd_rules() -> None:
    print(f"""=== 4-Phase Complex Extended c6bb58075520 (v2) ===

Round 3 of the phase spike. The Round 1+2 binary {{+1, -1}} design failed
because phase -1 always radiated enemy-aligned influence. This v2 escalates
to 4-phase complex mechanics where two phases (E/W) are orthogonal to the
main score axis — true neutral occupiers.

PHASES (compass directions):
  N (0°)   = P1's primary attack direction (P1 target)
  S (180°) = P2's primary attack direction (P2 target)
  E (90°)  = orthogonal / neutral occupier
  W (270°) = orthogonal / neutral occupier (anti-aligned with E)

CELL STATES (occupied)
  P1 stones: A^ (P1@N), A> (P1@E), Av (P1@S), A< (P1@W)
  P2 stones: B^ (P2@N), B> (P2@E), Bv (P2@S), B< (P2@W)
  Owner is decoupled from phase. Each player can place any phase.

INFLUENCE
  Each stone projects a 2D vector (cos(phase), sin(phase)) × strength × decay^d
  to its own cell + radius-1 neighbors. Cell value is a 2-vector (sum).
  - N stones radiate +x: helps P1, hurts P2.
  - S stones radiate -x: helps P2, hurts P1.
  - E/W stones radiate ±y: contribute zero to both scores (orthogonal).

SCORE
  P1 score = Σ over P1-owned cells of (cell_vec · (+1, 0))   [x-component]
  P2 score = Σ over P2-owned cells of (cell_vec · (-1, 0))   [-x-component]
  E and W stones never affect either player's score.
  First to score > {WIN_THRESHOLD:.4f} wins. Both crossing same step:
  higher margin wins, equal = draw.

CAPTURE (phase-cosine outnumber, threshold {CAPTURE_THRESHOLD})
  A stone at phase P dies if Σ over occupied neighbors of (-cos(P - N_phase)) > {CAPTURE_THRESHOLD}.
  Phase-difference contributions per neighbor:
    same phase    : -1 (protective)
    90° away (E/W vs N/S): 0 (no interaction)
    180° away     : +1 (lethal)
  This means N-stones and S-stones can capture each other, E and W can capture
  each other, but N/S cannot capture E/W and vice versa. E/W stones are
  capture-immune from the main-axis (N/S) attackers.

STRATEGIC TENSIONS
  - N (P1 attack) vs S (P2 attack): main score race. Capturable by each other.
  - E vs W: secondary axis. Pure blocking conflict. No score implications.
  - Mixed defense: a player can place E or W to occupy a cell without
    contributing to score, but immune to capture by N/S. Strategic question:
    when does the cost of "wasted" zero-score moves outweigh capture-resistance
    or denial?

BOARD: {AXIS_SIZE}x{AXIS_SIZE} torus, max {MAX_TURNS} turns.

ACTION ENCODING: "<cell><N|E|S|W>" e.g. "27N", "36S", "12E", "18W". "pass" to pass.
""")


def cmd_show() -> None:
    print(PhaseGameV2().render())


def cmd_play(moves_str: str) -> None:
    g = PhaseGameV2()
    if not moves_str.strip():
        print(g.render())
        return
    tokens = [t.strip() for t in moves_str.split(",") if t.strip()]
    for i, tok in enumerate(tokens):
        action = parse_move(tok)
        try:
            info = g.step(action)
        except Exception as e:
            print(f"ERROR at move {i+1} ({tok!r}): {e}")
            print(g.render())
            sys.exit(1)
        captured = info.get("captured", [])
        cap_str = f"  captured={captured}" if captured else ""
        end = info.get("end_reason", "")
        end_str = f"  END={end}" if end else ""
        print(f"  move {i+1}: P{info['player']} {tok}{cap_str}{end_str}  "
              f"(scores P1={g.player_score(1):.3f}, P2={g.player_score(2):.3f})")
        if g.done:
            break
    print()
    print(g.render())


def cmd_legal() -> None:
    g = PhaseGameV2()
    actions = g.get_legal_actions()
    print(f"Total legal actions on empty board: {len(actions)}")
    print(f"  - {(len(actions)-1)//4} placements per phase × 4 phases + 1 pass")
    examples = actions[:8] + [actions[-1]]
    print("Examples:")
    for a in examples:
        d = decode_action(a)
        if d["type"] == "pass":
            print(f"  action {a} -> pass")
        else:
            print(f"  action {a} -> place at cell {d['cell']} phase {d['phase_name']}")


def cmd_random_game(seed: int) -> None:
    g = PhaseGameV2(seed=seed)
    while not g.done:
        actions = g.get_legal_actions()
        a = int(g.rng.choice(actions))
        g.step(a)
    print(g.render())
    print()
    print(f"Random game finished in {g.step_count} steps. Winner: {g.winner}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--action", required=True,
                   choices=["rules", "show", "play", "legal", "random-game"])
    p.add_argument("--moves", default="")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    if args.action == "rules":
        cmd_rules()
    elif args.action == "show":
        cmd_show()
    elif args.action == "play":
        cmd_play(args.moves)
    elif args.action == "legal":
        cmd_legal()
    elif args.action == "random-game":
        cmd_random_game(args.seed)


if __name__ == "__main__":
    main()
