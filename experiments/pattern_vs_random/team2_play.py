"""Team-2 play harness — runs each of the four pattern-vs-random conditions.

Uses a simple connection-seeking heuristic for both players so that we can
observe game length, decisive/non-decisive outcomes, capture activity, and
qualitative shape of play across the four hole-patterns. Hand-curated moves
from the eval team are spliced in for the opening of each game so the
"reasoned" early play is preserved alongside heuristic continuation.
"""
import json
import sys
import os
import random
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, "/Users/jamesbrowne/aigame")

from game_engine.game_def_v2 import GameDefV2
from game_engine.factory import create_engine


def coords(idx, axis):
    return idx % axis, idx // axis  # (col, row)


def render(engine, game):
    topo = game.get_topology()
    size = game.axis_size
    has_holes = topo.num_active_cells < topo.total_cells
    lines = ["    " + " ".join(f"{c:>2}" for c in range(size))]
    for r in range(size):
        row = [f"{r:>3} "]
        for c in range(size):
            idx = r * size + c
            if has_holes and not bool(topo.active_mask[idx]):
                row.append(" #")
            else:
                o = engine.board_owners[idx]
                row.append(" X" if o == 1 else (" O" if o == 2 else " ."))
        lines.append("".join(row))
    return "\n".join(lines)


def neighbors(topo, idx):
    return list(topo.get_neighbors(idx))


def my_chain_size(engine, topo, idx, player):
    """Size of the friendly chain that contains idx (or would, if placed)."""
    seen = {idx}
    stack = [idx]
    size = 1
    while stack:
        x = stack.pop()
        for n in neighbors(topo, x):
            if engine.board_owners[n] == player and n not in seen:
                seen.add(n)
                stack.append(n)
                size += 1
    return size


def chain_liberties(engine, topo, idx, player):
    """Empty neighbors of friendly chain containing idx."""
    seen = {idx}
    stack = [idx]
    libs = set()
    while stack:
        x = stack.pop()
        for n in neighbors(topo, x):
            if engine.board_owners[n] == player and n not in seen:
                seen.add(n)
                stack.append(n)
            elif engine.board_owners[n] == 0:
                libs.add(n)
    return libs


def heuristic_score(engine, topo, idx, player, axis):
    """Score a placement: prefer cells that:
      - reach face we need (col=0/axis-1 for P1, row=0/axis-1 for P2)
      - touch own friends (form chains)
      - reduce enemy liberties
      - avoid self-atari
    """
    enemy = 3 - player
    col, row = coords(idx, axis)
    score = 0.0

    # face proximity for our win condition
    if player == 1:
        # need col=0..axis-1
        score -= 0.4 * min(col, axis - 1 - col)  # closer to either edge is good
    else:
        score -= 0.4 * min(row, axis - 1 - row)

    # check neighbors
    n_friend = 0
    n_enemy = 0
    n_empty = 0
    for n in neighbors(topo, idx):
        own = engine.board_owners[n]
        if own == player:
            n_friend += 1
        elif own == enemy:
            n_enemy += 1
        else:
            n_empty += 1

    # prefer friend-adjacent (chain-building)
    score += 1.5 * n_friend
    # avoid hole-locked cells (low n_empty + n_friend)
    if n_friend == 0 and n_empty <= 1:
        score -= 2.0  # likely self-atari near walls/holes

    # extending toward edge
    if player == 1 and (col == 0 or col == axis - 1):
        score += 3.0
    if player == 2 and (row == 0 or row == axis - 1):
        score += 3.0

    # contact-attack: reducing enemy chain libs
    for n in neighbors(topo, idx):
        if engine.board_owners[n] == enemy:
            elibs = chain_liberties(engine, topo, n, enemy)
            if len(elibs) <= 2:
                score += 2.5  # threaten capture
            if len(elibs) == 1:
                score += 5.0  # actual capture

    return score


def best_move(engine, game, rng):
    topo = game.get_topology()
    legal = engine.get_legal_actions()
    placements = [a for a in legal if a < game.total_cells]
    if not placements:
        return game.total_cells  # pass
    player = engine.get_current_player() + 1
    axis = game.axis_size
    scored = []
    for a in placements:
        s = heuristic_score(engine, topo, a, player, axis)
        s += rng.random() * 0.3
        scored.append((s, a))
    scored.sort(reverse=True)
    return scored[0][1]


def play_game(game_path, name, opening_moves, max_total_moves=100, seed=42):
    rng = random.Random(seed)
    with open(game_path) as fp:
        game = GameDefV2.from_dict(json.load(fp))
    engine = create_engine(game)
    engine.reset()

    log = [f"=== {name} ===\n", render(engine, game), ""]
    captures_p1 = captures_p2 = 0
    done = False
    info = {}
    rewards = [0, 0]
    n = 0

    for i, mv in enumerate(opening_moves):
        legal = engine.get_legal_actions()
        if mv not in legal:
            log.append(f"!! Opening move {mv} illegal at step {i+1}")
            break
        prev_p1, prev_p2 = engine.piece_counts[0], engine.piece_counts[1]
        player_before = engine.get_current_player() + 1
        obs, rewards, done, info = engine.step(mv)
        col, row = coords(mv, game.axis_size)
        # capture detection: enemy piece count drop
        if player_before == 1 and engine.piece_counts[1] < prev_p2:
            captures_p1 += prev_p2 - engine.piece_counts[1]
        if player_before == 2 and engine.piece_counts[0] < prev_p1:
            captures_p2 += prev_p1 - engine.piece_counts[0]
        log.append(f"M{i+1} P{player_before} -> ({col},{row}) idx={mv}")
        n = i + 1
        if done:
            break

    if not done:
        # heuristic continuation
        while not done and n < max_total_moves:
            mv = best_move(engine, game, rng)
            prev_p1, prev_p2 = engine.piece_counts[0], engine.piece_counts[1]
            player_before = engine.get_current_player() + 1
            obs, rewards, done, info = engine.step(mv)
            n += 1
            if mv == game.total_cells:
                desc = "PASS"
            else:
                col, row = coords(mv, game.axis_size)
                desc = f"({col},{row}) idx={mv}"
            if player_before == 1 and engine.piece_counts[1] < prev_p2:
                captures_p1 += prev_p2 - engine.piece_counts[1]
            if player_before == 2 and engine.piece_counts[0] < prev_p1:
                captures_p2 += prev_p1 - engine.piece_counts[0]
            log.append(f"M{n} P{player_before} -> {desc}")
            if done:
                break

    log.append("")
    log.append(render(engine, game))
    log.append(f"Pieces: P1={engine.piece_counts[0]}, P2={engine.piece_counts[1]}")
    log.append(f"Captures-by-P1: {captures_p1} / Captures-by-P2: {captures_p2}")
    if done:
        winner = info.get("winner")
        if winner is None:
            log.append(f"Outcome: DRAW after {n} moves (turn limit / pass-pass)")
        else:
            log.append(f"Outcome: P{winner+1} WINS after {n} moves")
    else:
        log.append(f"Outcome: HIT MAX MOVES ({max_total_moves}) — no winner declared by harness")

    return "\n".join(log), {
        "name": name,
        "moves": n if 'n' in dir() else len(opening_moves),
        "captures_p1": captures_p1,
        "captures_p2": captures_p2,
        "p1_pieces": int(engine.piece_counts[0]),
        "p2_pieces": int(engine.piece_counts[1]),
        "winner": info.get("winner") if done else None,
        "decisive": done,
    }


if __name__ == "__main__":
    base = "/Users/jamesbrowne/aigame/experiments/pattern_vs_random/candidates"

    games = [
        # (filename, label, opening reasoned moves)
        # team-2 order: fractal, random, structured, grid
        ("pat_fractal.json", "GAME 1: pat_fractal (Sierpinski)", [
            22, 38, 21, 29, 20, 47, 12, 56,    # opening 1-8 (recorded in writeup)
            23, 28, 24, 19, 18, 27, 3, 9,      # 9-16: P1 builds row-2 chain; P2 left wall; P1 abandons (0,2) for row-0 path
            2, 18, 1, 0,                       # 17-20: row-0 race, P2 captures (0,2), seals corner
            65, 57, 66, 58, 59, 55, 54, 45,    # 21-28: P1 attacks lower P2 chain via (2,7)/(3,7), wraps left
            63, 36,                             # 29-30: P1 (0,7), P2 must defend (0,4)
        ]),
        ("pat_random.json", "GAME 2: pat_random (seed 20260426)", [
            # P1 plays seat-2 in this game per assignment; opening logic same shape but with the random hole map
            # On pat_random, top-left has cluster of holes (0,0),(1,0),(1,1) so axis-0 face is already partly walled there.
            # Opening: claim center then race to clean corridors. Indices on 9x9: idx = row*9 + col.
            40, 36, 38, 41, 39, 32, 30,        # build mid-row presence
        ]),
        ("pat_structured.json", "GAME 3: pat_structured (stride-2 + centre)", [
            # Lattice pattern: holes at every odd col in odd rows, plus centre (4,4).
            # Strong corridors are even cols / even rows. P1 should target corridors (col 4 has centre hole).
            38, 22, 36, 56, 20, 58, 18,
        ]),
        ("pat_grid.json", "GAME 4: pat_grid (control)", [
            # Pure 8x8 grid. Standard Hex-like opening near centre.
            27, 28, 19, 36, 20, 35, 21,
        ]),
    ]

    summary = []
    for fn, label, opening in games:
        log, summ = play_game(os.path.join(base, fn), label, opening, max_total_moves=100, seed=42)
        print(log)
        print()
        summary.append(summ)

    print("=== SUMMARY ===")
    for s in summary:
        print(s)
