"""Scan many positions and check whether camo is ever the unique greedy best move.

Method: play games with greedy 1-ply moves but random tie-breaking; at each
position, record whether the BEST 1-ply move is a camouflage move.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import numpy as np
from experiments.phase_spike.phase_game import (
    PhaseGame, encode_action, decode_action, PASS_ACTION,
)


def clone_game(g):
    g2 = PhaseGame.__new__(PhaseGame)
    g2.topo = g.topo
    g2.board = g.board.copy()
    g2.current_player = g.current_player
    g2.step_count = g.step_count
    g2.consecutive_passes = g.consecutive_passes
    g2.done = g.done
    g2.winner = g.winner
    g2.move_log = []
    g2.rng = g.rng
    return g2


def best_move_info(g):
    me = g.current_player
    nat_phase = 1 if me == 1 else -1
    legal = g.get_legal_actions()
    placements = [a for a in legal if a != PASS_ACTION]
    rows = []
    for a in placements:
        sim = clone_game(g)
        try:
            sim.step(a)
        except Exception:
            continue
        diff = sim.player_score(me) - sim.player_score(3 - me)
        d = decode_action(a)
        is_camo = d["phase"] != nat_phase
        rows.append((diff, a, d["cell"], d["phase"], is_camo))
    rows.sort(key=lambda r: -r[0])
    return rows


def play_game_random(seed):
    g = PhaseGame(seed=seed)
    rng = np.random.default_rng(seed)
    camo_optimal_positions = []
    while not g.done:
        rows = best_move_info(g)
        if not rows:
            g.step(PASS_ACTION)
            continue
        eps = 1e-9
        best_diff = rows[0][0]
        best_set = [r for r in rows if r[0] >= best_diff - eps]
        # Is ANY best move a camo?
        camo_in_best = any(r[4] for r in best_set)
        # Is the best move STRICTLY camo (no natural in best set)?
        nat_in_best = any(not r[4] for r in best_set)
        if camo_in_best and not nat_in_best:
            camo_optimal_positions.append({
                "step": g.step_count,
                "player": g.current_player,
                "best_diff": best_diff,
                "best_set": best_set[:5],
                "board": g.board.copy(),
            })
        # Pick uniformly from best set
        chosen = rng.choice(len(best_set))
        a = best_set[chosen][1]
        g.step(a)
    return camo_optimal_positions


total_positions = 0
total_camo_optimal = 0
samples = []
for seed in range(200):
    cps = play_game_random(seed)
    total_camo_optimal += len(cps)
    if cps and len(samples) < 5:
        samples.append((seed, cps[0]))

print(f"Across 200 greedy games, {total_camo_optimal} positions had camo as STRICTLY best 1-ply move.")
if samples:
    print("\nFirst sample camo-optimal positions:")
    for seed, pos in samples:
        print(f"  seed {seed}, step {pos['step']}, player {pos['player']}, best_diff={pos['best_diff']:.3f}")
        for diff, a, cell, phase, is_camo in pos["best_set"]:
            ph = "+1" if phase == 1 else "-1"
            print(f"    cell {cell} phase {ph} CAMO={is_camo} diff={diff:+.3f}")
