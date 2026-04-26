"""CLI for engine-verified phase-game play.

Mirrors play_helper.py from the main project. Actions:
  rules        - print game rules
  show         - render initial empty board
  play         - apply a sequence of moves; format: "5+,12-,3+,..."
                 where digits are cell index and +/- is phase
  legal        - print legal actions count and a few examples
  random-game  - simulate a random game

Examples:
  .venv/bin/python experiments/phase_spike/phase_play_helper.py --action rules
  .venv/bin/python experiments/phase_spike/phase_play_helper.py --action play \\
      --moves "27+,36-,35+,43+,28+,44-,29+,45-,30+"
"""

from __future__ import annotations

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.phase_spike.phase_game import (
    PhaseGame,
    AXIS_SIZE, TOTAL_CELLS, INFLUENCE_RADIUS, INFLUENCE_STRENGTH,
    INFLUENCE_DECAY, OUTNUMBER_THRESHOLD, WIN_THRESHOLD, MAX_TURNS,
    PASS_ACTION, encode_action, decode_action,
)


def parse_move(token: str) -> int:
    """Parse a move token like '27+' or '36-' or 'pass' to an action int."""
    token = token.strip().lower()
    if token == "pass":
        return PASS_ACTION
    if not token:
        raise ValueError("empty move token")
    if token[-1] not in "+-":
        raise ValueError(f"move token must end in + or -, got {token!r}")
    cell_str = token[:-1]
    cell = int(cell_str)
    if not 0 <= cell < TOTAL_CELLS:
        raise ValueError(f"cell out of range: {cell}")
    phase = 1 if token[-1] == "+" else -1
    return encode_action(cell, phase)


def cmd_rules() -> None:
    print(f"""=== Phase-Extended c6bb58075520 ===

A research spike testing whether phase-stones (complex-number-inspired stone
state) add genuine strategic depth. The base game is the R16 human winner
`c6bb58075520` (torus 8x8, alternating, outnumber-2 capture, radius-1 signed
influence, threshold win). The extension: each placement specifies BOTH a
cell AND a phase (+1 or -1).

OWNERSHIP vs PHASE
  Each stone has an OWNER (P1 or P2) AND a PHASE (+1 or -1). They are
  decoupled. P1 can place a stone with EITHER phase; same for P2.

  P1@+1 ("A"): natural P1 stone. Contributes positively to P1's score.
  P1@-1 ("a"): P1 CAMOUFLAGE stone. Owned by P1 but reads as -1-aligned for
    capture and influence. Contributes NEGATIVELY to P1's score, but survives
    in enemy territory and blocks the cell.
  P2@-1 ("B"): natural P2 stone. P2's primary alignment is -1.
  P2@+1 ("b"): P2 CAMOUFLAGE stone.

INFLUENCE (radius {INFLUENCE_RADIUS}, strength {INFLUENCE_STRENGTH:.4f}, decay {INFLUENCE_DECAY:.4f})
  Each stone projects (stone_phase × strength × decay^distance) to neighbors.
  A +1 stone radiates positive value; a -1 stone radiates negative.

CAPTURE (phase-based outnumber, threshold {OUTNUMBER_THRESHOLD})
  A stone at phase P is captured if:
    (count of opposite-phase neighbors) > (count of same-phase neighbors) + {OUTNUMBER_THRESHOLD}
  Owner is irrelevant — captures are determined by phase alone. A P1 camouflage
  stone (P1@-1) is treated like any -1 stone for capture purposes.

WIN
  P1 score = sum over P1-owned cells of (cell_value × stone_phase).
  P2 score = sum over P2-owned cells of (cell_value × -stone_phase).
  First to score > {WIN_THRESHOLD:.4f} wins. If both cross same step, higher
  margin wins; equal margin = draw. Double pass = draw.

  Note: P1 camouflage stones have stone_phase = -1, so they contribute
  -cell_value to P1's score. Camouflage is a NET COST to your score; its
  benefit is occupying a cell in enemy territory without being captured.

ACTION ENCODING
  - Place: "<cell><phase>" e.g. "27+" places at cell 27 with phase +1.
  - Pass: "pass"
  - Cell index: y * 8 + x where (x, y) ∈ [0, 8)^2.

BOARD ({AXIS_SIZE}x{AXIS_SIZE} TORUS, max {MAX_TURNS} turns)
  Cells wrap on both axes. Cell (0, 0) is index 0; cell (7, 7) is index 63.
""")


def cmd_show() -> None:
    print(PhaseGame().render())


def cmd_play(moves_str: str) -> None:
    g = PhaseGame()
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
    g = PhaseGame()
    actions = g.get_legal_actions()
    print(f"Total legal actions on empty board: {len(actions)}")
    print(f"  - {(len(actions)-1)//2} placements per phase × 2 phases + 1 pass")
    examples = actions[:6] + [actions[-1]]
    print("Examples:")
    for a in examples:
        d = decode_action(a)
        if d["type"] == "pass":
            print(f"  action {a} -> pass")
        else:
            sign = "+" if d["phase"] == 1 else "-"
            print(f"  action {a} -> place at cell {d['cell']} phase {sign}1")


def cmd_random_game(seed: int) -> None:
    g = PhaseGame(seed=seed)
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
    p.add_argument("--moves", default="",
                   help="Comma-separated move tokens for --action play")
    p.add_argument("--seed", type=int, default=42,
                   help="Seed for random-game action selection")
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
