"""Unit + integration tests for Sierpinski-carpet topology.

Run as: .venv/bin/python experiments/fractal_spike/test_sierpinski_topology.py
"""

from __future__ import annotations

import json
import os
import sys
import traceback

import numpy as np

# Make repo root importable when running this file directly.
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from game_engine.topology import (
    TopologicalSpace,
    TOPOLOGY_TYPES,
    EXPERIMENTAL_TOPOLOGIES,
    SIERPINSKI_AXIS_SIZE,
    _sierpinski_carpet_holes,
)


_PASS: list[str] = []
_FAIL: list[tuple[str, str]] = []


def _xy(x: int, y: int) -> int:
    return y * SIERPINSKI_AXIS_SIZE + x


def case(name: str):
    def deco(fn):
        try:
            fn()
            _PASS.append(name)
            print(f"  PASS  {name}")
        except Exception as e:
            tb = traceback.format_exc()
            _FAIL.append((name, tb))
            print(f"  FAIL  {name}: {e}")
        return fn
    return deco


# ----------------------------------------------------------------------
# Hole pattern
# ----------------------------------------------------------------------

@case("holes: count is 17")
def _():
    assert len(_sierpinski_carpet_holes(9)) == 17

@case("holes: spot-check known holes")
def _():
    holes = _sierpinski_carpet_holes(9)
    for x, y in [(4, 4), (1, 1), (7, 7), (1, 7), (7, 1), (4, 1), (1, 4), (7, 4), (4, 7),
                 (3, 3), (5, 5), (4, 5), (5, 4)]:
        assert _xy(x, y) in holes, f"({x},{y}) should be a hole"

@case("holes: spot-check known active cells")
def _():
    holes = _sierpinski_carpet_holes(9)
    for x, y in [(0, 0), (2, 2), (0, 4), (8, 8), (0, 8), (8, 0), (2, 4), (6, 4),
                 (4, 0), (4, 8), (0, 4), (8, 4)]:
        assert _xy(x, y) not in holes, f"({x},{y}) should be active"

@case("holes: only valid axis_size==9 raises otherwise")
def _():
    try:
        _sierpinski_carpet_holes(8)
    except ValueError:
        return
    raise AssertionError("expected ValueError for non-9 axis_size")


# ----------------------------------------------------------------------
# TopologicalSpace construction
# ----------------------------------------------------------------------

@case("construct: requires axis_size==9")
def _():
    try:
        TopologicalSpace(2, 8, "sierpinski")
    except ValueError:
        return
    raise AssertionError("expected ValueError for axis_size != 9")

@case("construct: requires num_dimensions==2")
def _():
    try:
        TopologicalSpace(3, 9, "sierpinski")
    except ValueError:
        return
    raise AssertionError("expected ValueError for num_dimensions != 2")

@case("construct: rectangular topologies still default to all-active")
def _():
    for t in ("grid", "torus", "hex", "moore"):
        topo = TopologicalSpace(2, 8, t)
        assert topo.num_active_cells == 64
        assert len(topo.active_cells) == 64
        assert topo.active_mask.sum() == 64
        assert topo._dist_matrix is None


# ----------------------------------------------------------------------
# Sierpinski topology object
# ----------------------------------------------------------------------

def _topo() -> TopologicalSpace:
    return TopologicalSpace(2, 9, "sierpinski")

@case("sierpinski: 64 active cells, 17 holes")
def _():
    topo = _topo()
    assert topo.num_active_cells == 64
    assert len(topo.active_cells) == 64
    assert topo.active_mask.sum() == 64
    assert int((~topo.active_mask).sum()) == 17

@case("sierpinski: holes have empty neighbor lists")
def _():
    topo = _topo()
    holes = _sierpinski_carpet_holes(9)
    for h in holes:
        assert topo.get_neighbors(h) == [], f"hole {h} has neighbors"

@case("sierpinski: active cells never have hole neighbors")
def _():
    topo = _topo()
    holes = _sierpinski_carpet_holes(9)
    for a in topo.active_cells:
        for n in topo.get_neighbors(a):
            assert n not in holes

@case("sierpinski: max_degree is 4 (von Neumann)")
def _():
    topo = _topo()
    assert topo.max_degree == 4

@case("sierpinski: corner cells have 2 neighbors")
def _():
    topo = _topo()
    assert len(topo.get_neighbors(_xy(0, 0))) == 2
    assert len(topo.get_neighbors(_xy(8, 0))) == 2
    assert len(topo.get_neighbors(_xy(0, 8))) == 2
    assert len(topo.get_neighbors(_xy(8, 8))) == 2

@case("sierpinski: cell adjacent to hole has reduced degree")
def _():
    topo = _topo()
    # (2,4) is adjacent to (3,4) which is a hole, plus (1,4) which is also a hole.
    # So (2,4) has only (2,3) and (2,5) as neighbors — degree 2.
    nbrs = topo.get_neighbors(_xy(2, 4))
    assert _xy(3, 4) not in nbrs
    assert _xy(1, 4) not in nbrs
    assert _xy(2, 3) in nbrs
    assert _xy(2, 5) in nbrs


# ----------------------------------------------------------------------
# Distance and influence radius
# ----------------------------------------------------------------------

@case("distance: corner (0,0) to corner (8,8) = 16 (perimeter route)")
def _():
    topo = _topo()
    assert topo.distance(_xy(0, 0), _xy(8, 8)) == 16

@case("distance: opposite-of-central-hole detour > Manhattan")
def _():
    topo = _topo()
    # (2,4) to (6,4): Manhattan 4, must detour around 3-wide central hole.
    # Routes go up to row 2 or down to row 6 then across.
    d = topo.distance(_xy(2, 4), _xy(6, 4))
    assert d >= 8, f"expected detour >= 8, got {d}"

@case("distance: hole endpoints return -1 sentinel")
def _():
    topo = _topo()
    holes = sorted(_sierpinski_carpet_holes(9))
    for h in holes[:5]:
        assert topo.distance(h, _xy(0, 0)) == -1
        assert topo.distance(_xy(0, 0), h) == -1

@case("cells_within_radius: holes excluded from result")
def _():
    topo = _topo()
    holes = _sierpinski_carpet_holes(9)
    cells = topo.cells_within_radius(_xy(0, 0), 5)
    for h in holes:
        assert h not in cells

@case("cells_within_radius: hole blocks influence to far side")
def _():
    topo = _topo()
    # Cell (2,4) at radius 2: should NOT include (6,4) on the far side.
    cells = topo.cells_within_radius(_xy(2, 4), 2)
    assert _xy(6, 4) not in cells
    assert _xy(7, 4) not in cells
    # Should include immediate active neighbors and their neighbors.
    assert _xy(2, 3) in cells
    assert _xy(2, 5) in cells


# ----------------------------------------------------------------------
# Connection / face checks
# ----------------------------------------------------------------------

@case("connects_faces: all-active connects on both axes")
def _():
    topo = _topo()
    cells = set(topo.active_cells)
    assert topo.connects_faces(cells, 0)
    assert topo.connects_faces(cells, 1)


# ----------------------------------------------------------------------
# Engine integration
# ----------------------------------------------------------------------

@case("engine: legal placements exclude holes")
def _():
    from game_engine.engine_v2 import GameEngineV2
    from game_engine.game_def_v2 import GameDefV2
    from game_engine.rules import (
        PlacementRule, CaptureRule, PropagationRule,
        WinCondition, TurnStructure, ActionRule,
    )
    g = GameDefV2(
        game_id="test_sierpinski",
        num_dimensions=2,
        axis_size=9,
        topology_type="sierpinski",
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="none"),
        propagation_rule=PropagationRule(prop_type="none"),
        win_condition=WinCondition(condition_type="elimination", max_turns=50),
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
    )
    eng = GameEngineV2(g)
    actions = eng.get_legal_actions(player=1)
    place_actions = [a for a in actions if a < g.total_cells]
    assert len(place_actions) == 64, f"expected 64 placements, got {len(place_actions)}"
    holes = _sierpinski_carpet_holes(9)
    for a in place_actions:
        assert a not in holes

@case("engine: territory threshold uses active cell count")
def _():
    from game_engine.engine_v2 import GameEngineV2
    from game_engine.game_def_v2 import GameDefV2
    from game_engine.rules import (
        PlacementRule, CaptureRule, PropagationRule,
        WinCondition, TurnStructure, ActionRule,
    )
    g = GameDefV2(
        game_id="test_sierpinski_territory",
        num_dimensions=2,
        axis_size=9,
        topology_type="sierpinski",
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="none"),
        propagation_rule=PropagationRule(prop_type="none"),
        win_condition=WinCondition(
            condition_type="territory", threshold=0.5, max_turns=200
        ),
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
    )
    eng = GameEngineV2(g)
    # Manually fill 33 of 64 active cells with P1 to cross 0.5 * 64 = 32.
    for c in eng.topo.active_cells[:33]:
        eng.board_owners[c] = 1
    eng.piece_counts[0] = 33
    eng._check_win_conditions()
    assert eng.done is True
    assert eng._winner == 1, f"expected P1 win, got {eng._winner}"

    # Reset and confirm 32 stones is not enough (32 > 0.5 * 64 == 32 is False).
    eng2 = GameEngineV2(g)
    for c in eng2.topo.active_cells[:32]:
        eng2.board_owners[c] = 1
    eng2.piece_counts[0] = 32
    eng2._check_win_conditions()
    assert eng2.done is False, "32/64 should not trigger 0.5 threshold"

@case("engine: influence propagation skips holes")
def _():
    from game_engine.engine_v2 import GameEngineV2
    from game_engine.game_def_v2 import GameDefV2
    from game_engine.rules import (
        PlacementRule, CaptureRule, PropagationRule,
        WinCondition, TurnStructure, ActionRule,
    )
    g = GameDefV2(
        game_id="test_sierpinski_influence",
        num_dimensions=2,
        axis_size=9,
        topology_type="sierpinski",
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="none"),
        propagation_rule=PropagationRule(
            prop_type="influence", radius=2, strength=1.0, decay=0.5
        ),
        win_condition=WinCondition(
            condition_type="threshold", threshold=10.0, max_turns=200
        ),
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
    )
    eng = GameEngineV2(g)
    eng.step(_xy(2, 4))  # P1 places adjacent to central hole's left flank
    holes = _sierpinski_carpet_holes(9)
    for h in holes:
        assert eng.board_values[h] == 0.0, f"hole {h} got influence {eng.board_values[h]}"

@case("engine: custodian capture works on sierpinski (active corridor)")
def _():
    from game_engine.engine_v2 import GameEngineV2
    from game_engine.game_def_v2 import GameDefV2
    from game_engine.rules import (
        PlacementRule, CaptureRule, PropagationRule,
        WinCondition, TurnStructure, ActionRule,
    )
    g = GameDefV2(
        game_id="test_sierpinski_custodian_pos",
        num_dimensions=2,
        axis_size=9,
        topology_type="sierpinski",
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="custodian"),
        propagation_rule=PropagationRule(prop_type="none"),
        win_condition=WinCondition(
            condition_type="territory", threshold=0.5, max_turns=200
        ),
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
    )
    # Column x=2 is fully active (no holes). Row y=2 column x=2..4 active.
    # Setup: P2 at (1,0), P1 at (2,0) (already placed). P1 places at (0,0).
    # Walk +x from (0,0): (1,0)=enemy, (2,0)=friendly → capture (1,0).
    eng = GameEngineV2(g)
    eng.board_owners[_xy(1, 0)] = 2
    eng.piece_counts[1] = 1
    eng.board_owners[_xy(2, 0)] = 1
    eng.piece_counts[0] = 1
    eng.current_player = 1
    eng.step(_xy(0, 0))
    assert eng.board_owners[_xy(1, 0)] == 1, "P2 stone should have been flipped to P1"

@case("engine: custodian walk terminates at hole (no capture across)")
def _():
    from game_engine.engine_v2 import GameEngineV2
    from game_engine.game_def_v2 import GameDefV2
    from game_engine.rules import (
        PlacementRule, CaptureRule, PropagationRule,
        WinCondition, TurnStructure, ActionRule,
    )
    g = GameDefV2(
        game_id="test_sierpinski_custodian_hole",
        num_dimensions=2,
        axis_size=9,
        topology_type="sierpinski",
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="custodian"),
        propagation_rule=PropagationRule(prop_type="none"),
        win_condition=WinCondition(
            condition_type="territory", threshold=0.5, max_turns=200
        ),
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
    )
    # Row y=4: holes at x ∈ {1, 3, 4, 5, 7}; active at x ∈ {0, 2, 6, 8}.
    # Setup: P2 at (2,4), P1 at (6,4). P1 places at (0,4).
    # Walk +x from (0,4): (1,4)=hole → break. No capture even though P2 sits
    # downstream and a P1 sits beyond it.
    eng = GameEngineV2(g)
    eng.board_owners[_xy(2, 4)] = 2
    eng.piece_counts[1] = 1
    eng.board_owners[_xy(6, 4)] = 1
    eng.piece_counts[0] = 1
    eng.current_player = 1
    eng.step(_xy(0, 4))
    assert eng.board_owners[_xy(2, 4)] == 2, "hole should have prevented capture"


# ----------------------------------------------------------------------
# Round-trip serialization
# ----------------------------------------------------------------------

@case("round-trip: GameDefV2 to_dict/from_dict preserves sierpinski")
def _():
    from game_engine.game_def_v2 import GameDefV2
    from game_engine.rules import (
        PlacementRule, CaptureRule, PropagationRule,
        WinCondition, TurnStructure, ActionRule,
    )
    g = GameDefV2(
        game_id="rt_test",
        num_dimensions=2,
        axis_size=9,
        topology_type="sierpinski",
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="none"),
        propagation_rule=PropagationRule(prop_type="none"),
        win_condition=WinCondition(condition_type="elimination", max_turns=50),
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
    )
    d = g.to_dict()
    raw = json.dumps(d)
    g2 = GameDefV2.from_dict(json.loads(raw))
    assert g2.topology_type == "sierpinski"
    topo = g2.get_topology()
    assert topo.num_active_cells == 64
    assert topo._dist_matrix is not None


# ----------------------------------------------------------------------
# Mutation gating
# ----------------------------------------------------------------------

@case("mutation: sierpinski excluded from mutation pool")
def _():
    from evolution.operators_v2 import MutationOperatorV2
    from config import EvolutionConfig
    from game_engine.game_def_v2 import GameDefV2
    from game_engine.rules import (
        PlacementRule, CaptureRule, PropagationRule,
        WinCondition, TurnStructure, ActionRule,
    )
    rng = np.random.default_rng(0)
    op = MutationOperatorV2(EvolutionConfig(), rng)
    # Build a non-sierpinski game and mutate topology_type 100 times.
    base = GameDefV2(
        game_id="m_test",
        num_dimensions=2,
        axis_size=8,
        topology_type="grid",
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="none"),
        propagation_rule=PropagationRule(prop_type="none"),
        win_condition=WinCondition(condition_type="elimination", max_turns=50),
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
    )
    seen = set()
    for _ in range(200):
        clone = base.copy()
        op._mutate_topology_type(clone)
        seen.add(clone.topology_type)
    assert "sierpinski" not in seen, f"sierpinski leaked into mutation: {seen}"
    assert seen.issubset({"grid", "torus", "hex", "moore"}), f"unexpected topology(s): {seen}"


def main() -> int:
    if _FAIL:
        print("\n=== FAILURE DETAIL ===")
        for name, tb in _FAIL:
            print(f"--- {name} ---\n{tb}")
    print(f"\n{'PASS' if not _FAIL else 'FAIL'}: {len(_PASS)} passed, {len(_FAIL)} failed")
    return 0 if not _FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
