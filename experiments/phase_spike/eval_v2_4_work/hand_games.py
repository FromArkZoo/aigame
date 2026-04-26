"""Three hand games for the 4-phase complex (v2) game.

Game 1: greedy mirror — both players play N/S only with similar density.
Game 2: P1 plays N+E (mixed primary + blocker). P2 plays S-only.
Game 3: free play (greedy, full 4-phase mix).
"""

from __future__ import annotations

import copy
import os
import sys

_THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(_THIS))))

from experiments.phase_spike.phase_game_v2 import (
    PhaseGameV2, encode_action, decode_action, PASS_ACTION, PHASE_NAMES,
)


def play_moves(moves: list[tuple[int, int]], label: str = "game"):
    """Play a list of (cell, phase_idx) moves and print scores after each."""
    g = PhaseGameV2()
    print(f"=== {label} ===")
    for i, (c, p) in enumerate(moves):
        if g.done:
            print(f"  Game ended early at move {i}")
            break
        info = g.step(encode_action(c, p))
        captured = info.get("captured", [])
        cap = f" CAPTURED={captured}" if captured else ""
        end = info.get("end_reason", "")
        endstr = f" END={end}" if end else ""
        ptag = "P1" if info["player"] == 1 else "P2"
        cellname = f"{c}{PHASE_NAMES[p]}"
        print(f"  m{i+1:2d}: {ptag} {cellname:>4s}  P1={g.player_score(1):+7.3f}  "
              f"P2={g.player_score(2):+7.3f}{cap}{endstr}")
    print()
    print(g.render())
    print()
    return g


# ---------------------------------------------------------------------------
# Game 1: greedy mirror — both players play N/S only with similar density
# ---------------------------------------------------------------------------
# P1 builds a +x cluster, P2 mirrors with -x. Both stick to primary axis.

def game1_greedy_mirror():
    moves = [
        (27, 0),   # P1@N at (3,3)
        (36, 2),   # P2@S at (4,4)
        (28, 0),   # P1@N at (3,4)
        (35, 2),   # P2@S at (4,3)
        (19, 0),   # P1@N at (2,3)
        (44, 2),   # P2@S at (5,4)
        (20, 0),   # P1@N at (2,4)
        (43, 2),   # P2@S at (5,3)
        (18, 0),   # P1@N at (2,2)
        (45, 2),   # P2@S at (5,5)
        (29, 0),   # P1@N at (3,5)
        (34, 2),   # P2@S at (4,2)
        (11, 0),   # P1@N at (1,3)
        (52, 2),   # P2@S at (6,4)
        (12, 0),   # P1@N at (1,4)
        (51, 2),   # P2@S at (6,3)
        (10, 0),   # P1@N at (1,2)
        (53, 2),   # P2@S at (6,5)
        (13, 0),   # P1@N at (1,5)
        (50, 2),   # P2@S at (6,2)
        (4, 0),    # P1@N at (0,4) -- might trigger threshold
    ]
    return play_moves(moves, "GAME 1: greedy mirror (N+S only)")


# ---------------------------------------------------------------------------
# Game 2: P1 plays N+E (mixed primary + blocker). P2 plays S-only.
# ---------------------------------------------------------------------------
# P1 mixes N (primary scoring) with E (orthogonal blocker — capture-immune
# from S attackers). P2 plays pure S attack. Question: does the blocker help
# P1 vs lose to pure attack?

def game2_blocker_vs_attack():
    moves = [
        (27, 0),   # P1@N
        (36, 2),   # P2@S
        (28, 1),   # P1@E (blocker -- doesn't score but immune to S capture)
        (35, 2),   # P2@S
        (19, 0),   # P1@N
        (44, 2),   # P2@S
        (20, 1),   # P1@E (blocker)
        (43, 2),   # P2@S
        (11, 0),   # P1@N
        (52, 2),   # P2@S
        (12, 1),   # P1@E
        (51, 2),   # P2@S
        (3, 0),    # P1@N
        (60, 2),   # P2@S
        (4, 1),    # P1@E
        (59, 2),   # P2@S
        (10, 0),   # P1@N
        (53, 2),   # P2@S
        (18, 0),   # P1@N
        (45, 2),   # P2@S
        (26, 0),   # P1@N
        (37, 2),   # P2@S
    ]
    return play_moves(moves, "GAME 2: P1 N+E mix vs P2 S-only")


# ---------------------------------------------------------------------------
# Game 3: free play (1-ply greedy, full 4-phase mix)
# ---------------------------------------------------------------------------

def greedy_action(game: PhaseGameV2) -> int:
    actions = game.get_legal_actions()
    best_score = -float("inf")
    best_action = PASS_ACTION
    me = game.current_player
    other = 3 - me
    for a in actions:
        sim = copy.deepcopy(game)
        try:
            sim.step(a)
        except Exception:
            continue
        own = sim.player_score(me)
        opp = sim.player_score(other)
        diff = own - opp
        if a == PASS_ACTION:
            diff -= 1e-6
        if diff > best_score:
            best_score = diff
            best_action = a
    return best_action


def game3_free_greedy():
    print("=== GAME 3: free play (1-ply greedy, full 4-phase mix) ===")
    g = PhaseGameV2()
    while not g.done:
        a = greedy_action(g)
        d = decode_action(a)
        ptag = f"P{g.current_player}"
        if d["type"] == "pass":
            mtag = "pass"
        else:
            mtag = f"{d['cell']}{d['phase_name']}"
        info = g.step(a)
        captured = info.get("captured", [])
        cap = f" CAP={captured}" if captured else ""
        end = info.get("end_reason", "")
        endstr = f" END={end}" if end else ""
        print(f"  m{g.step_count:3d}: {ptag} {mtag:>4s}  P1={g.player_score(1):+7.3f}  "
              f"P2={g.player_score(2):+7.3f}{cap}{endstr}")
        if g.step_count > 110:
            break
    print()
    print(g.render())
    print()
    # Tally phase usage
    from collections import Counter
    pcount = {1: Counter(), 2: Counter()}
    for m in g.move_log:
        if m.get("type") == "place":
            pcount[m["player"]][m["phase_name"]] += 1
    for p in (1, 2):
        total = sum(pcount[p].values())
        if total:
            bits = " ".join(f"{ph}={pcount[p][ph]}({100*pcount[p][ph]/total:.0f}%)"
                            for ph in PHASE_NAMES)
            print(f"  P{p} phase usage (total={total}): {bits}")
    return g


def main():
    g1 = game1_greedy_mirror()
    print()
    print()
    g2 = game2_blocker_vs_attack()
    print()
    print()
    g3 = game3_free_greedy()


if __name__ == "__main__":
    main()
