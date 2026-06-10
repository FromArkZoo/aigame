"""Stage 0a: flip-threshold memo at r=2/d=0.5/eps=0, from the engine's own kernels.

A stone at cell c flips when net opposing field at c exceeds own-side field at c
(control margin 0). Own stone contributes strength*decay^0 = 1.0 at its own cell.
This script measures, on the real W=22 hex_rhombus topology:
  - lone stone: minimum attacker sets (adjacent vs distance-2 mixes)
  - chain-end and chain-interior stones (own-chain support raises the bar)
Writes a markdown table to STAGE0_MEMO.md.

KILL (pre-registered): lone-stone flip needs > 4 coordinated attackers.

Implementation note: because the field contribution at the victim cell from an
attacker depends only on decay**distance(attacker, victim), the search is done
over (n_d1, n_d2) attacker counts (adjacent vs distance-2) rather than full
subset enumeration. This is mathematically identical to the full subset search
and runs in microseconds.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from game_engine.rules import (  # noqa: E402
    PlacementRule, CaptureRule, PropagationRule, WinCondition, TurnStructure,
)
from game_engine.factory import create_engine  # noqa: E402 (not engine_v2 — factory dispatches)

W = 22
RADIUS, STRENGTH, DECAY = 2, 1.0, 0.5


def make_game() -> GameDefV2:
    return GameDefV2(
        game_id="stage0_probe", num_dimensions=2, axis_size=W,
        topology_type="hex_rhombus",
        placement_rule=PlacementRule(),
        capture_rule=CaptureRule(capture_type="field_flip"),
        propagation_rule=PropagationRule(
            prop_type="influence", radius=RADIUS, strength=STRENGTH, decay=DECAY),
        win_condition=WinCondition(
            condition_type="field_connection", control_margin=0.0, max_turns=200),
        turn_structure=TurnStructure(),
    )


def field_at(engine, cell: int, stones: dict[int, int]) -> float:
    """Net field at `cell` given {cell: owner} stones, via engine recompute."""
    engine.board_owners[:] = 0
    engine.board_values[:] = 0.0
    for c, owner in stones.items():
        engine.board_owners[c] = owner
    engine._recompute_field()
    return float(engine.board_values[cell])


def min_attackers(engine, victim: int, support: dict[int, int]) -> tuple[int, str]:
    """Smallest attacker set (P2 stones) making net field at victim negative.

    Uses a count-based search over (n_d1, n_d2) pairs — the field contribution
    from an attacker depends only on its distance to the victim, so only
    distance counts matter. Equivalent to full subset search but O(1).

    Returns (count, description-of-distances).
    """
    topo = engine.topo

    # Contribution weights at the victim cell from an attacker at each distance
    w_d1 = STRENGTH * (DECAY ** 1)   # 0.5
    w_d2 = STRENGTH * (DECAY ** 2)   # 0.25

    # How many attacker candidates are available at each distance from victim,
    # excluding the victim itself and any support stones already placed.
    excluded = set(support.keys()) | {victim}
    r1_cells = [c for c in topo.cells_within_radius(victim, 1) if c != victim and c not in excluded]
    r2_cells = [c for c in topo.cells_within_radius(victim, RADIUS) if topo.distance(victim, c) == 2 and c not in excluded]
    max_d1 = len(r1_cells)
    max_d2 = len(r2_cells)

    # Own-side field at victim from victim itself + support stones
    stones_own = {victim: 1, **support}
    own_field = field_at(engine, victim, stones_own)

    # Search (n_d1, n_d2) pairs for smallest total count that yields negative net field.
    # Attackers are P2 (sign -1): flip when own_field - n_d1*w_d1 - n_d2*w_d2 < 0.
    best_k = 99
    best_desc = "none<=7"
    for total_k in range(1, max_d1 + max_d2 + 1):
        found = False
        for n_d1 in range(min(total_k, max_d1) + 1):
            n_d2 = total_k - n_d1
            if n_d2 < 0 or n_d2 > max_d2:
                continue
            net = own_field - n_d1 * w_d1 - n_d2 * w_d2
            if net < 0.0:
                dists = ["d1"] * n_d1 + ["d2"] * n_d2
                desc = "+".join(dists)
                if total_k < best_k:
                    best_k = total_k
                    best_desc = desc
                found = True
                break  # smallest n_d1 for this total_k; can stop since total_k increases
        if found:
            break
    return best_k, best_desc


def pick_interior_cell(topo) -> int:
    """First cell with the full hex interior neighbourhood: 6 distance-1
    neighbours AND 12 distance-2 cells.

    Guards against edge/corner probe cells — len(active_cells)//2 lands on a
    LEFT-EDGE cell of the W=22 rhombus (only 4 d1 neighbours), which silently
    inflates the chain-interior/dense-interior thresholds."""
    for cell in topo.active_cells:
        n_d1 = len([c for c in topo.cells_within_radius(cell, 1) if c != cell])
        n_d2 = len([c for c in topo.cells_within_radius(cell, 2)
                    if topo.distance(cell, c) == 2])
        if n_d1 == 6 and n_d2 == 12:
            return cell
    raise RuntimeError("no fully-interior cell found on this topology")


def engine_cross_check(engine, victim: int) -> str:
    """Verify the lone-stone minimal set with REAL stones through the engine:
    2 adjacent attackers alone must NOT flip (net field >= 0); adding one
    distance-2 attacker must flip (net field < 0). This grounds the
    count-based search in the engine's own kernels, not just analytic
    weights."""
    topo = engine.topo
    d1 = [c for c in topo.cells_within_radius(victim, 1) if c != victim]
    d2 = [c for c in topo.cells_within_radius(victim, 2)
          if topo.distance(victim, c) == 2]
    net_two = field_at(engine, victim, {victim: 1, d1[0]: 2, d1[1]: 2})
    net_three = field_at(engine, victim, {victim: 1, d1[0]: 2, d1[1]: 2, d2[0]: 2})
    assert net_two >= 0.0, (
        f"engine cross-check FAILED: 2 adjacent attackers flipped (net={net_two})")
    assert net_three < 0.0, (
        f"engine cross-check FAILED: 2 adjacent + 1 d2 did not flip (net={net_three})")
    return (f"engine cross-check: PASS (2 adjacent: net={net_two:+.4f}, no flip; "
            f"2 adjacent + 1 distance-2: net={net_three:+.4f}, flip)")


def main() -> None:
    game = make_game()
    engine = create_engine(game)
    topo = engine.topo
    center = pick_interior_cell(topo)
    nbrs = [c for c in topo.cells_within_radius(center, 1) if c != center]

    rows = []
    k, desc = min_attackers(engine, center, {})
    rows.append(("lone stone", k, desc))
    k, desc = min_attackers(engine, center, {nbrs[0]: 1})
    rows.append(("chain end (1 own neighbour)", k, desc))
    k, desc = min_attackers(engine, center, {nbrs[0]: 1, nbrs[1]: 1})
    rows.append(("chain interior (2 own neighbours)", k, desc))
    k, desc = min_attackers(engine, center, {nbrs[0]: 1, nbrs[1]: 1, nbrs[2]: 1})
    rows.append(("dense interior (3 own neighbours)", k, desc))

    cross_check = engine_cross_check(engine, center)

    out = ["# Stage 0a — flip thresholds at r=2/d=0.5/eps=0 (computed from engine kernels)",
           "", "| position | min attackers | distances |", "|---|---|---|"]
    for name, k, desc in rows:
        out.append(f"| {name} | {k} | {desc} |")
    lone = rows[0][1]
    verdict = "PASS" if lone <= 4 else "KILL (lone-stone flip needs > 4 attackers)"
    out += ["", cross_check, "",
            f"**Pre-registered kill check: lone stone needs {lone} attackers -> {verdict}**", ""]
    Path(__file__).with_name("STAGE0_MEMO.md").write_text("\n".join(out))
    print("\n".join(out))
    assert lone <= 4, "STAGE 0a KILL fired"


if __name__ == "__main__":
    main()
