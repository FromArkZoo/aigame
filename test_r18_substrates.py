#!/usr/bin/env python3
"""Topology tests for R18 fractal substrates: sierpinski_triangle, vicsek, menger.

The level-2 sierpinski carpet has its own dedicated test in
experiments/fractal_spike/test_sierpinski_topology.py (26 cases) — this file
covers the three R18 additions to the same depth that B1 validation needs:
active-cell counts, hole isolation, neighbor invariants, connectivity, and
round-trip serialisation.

Run as: .venv/bin/python test_r18_substrates.py
"""
from __future__ import annotations

import json
import sys
import traceback

import numpy as np

from game_engine.game_def_v2 import GameDefV2
from game_engine.rules import (
    ActionRule,
    CaptureRule,
    PlacementRule,
    PropagationRule,
    TurnStructure,
    WinCondition,
)
from game_engine.topology import (
    EXPERIMENTAL_TOPOLOGIES,
    MENGER_AXIS_SIZE,
    SIERPINSKI_TRIANGLE_AXIS_SIZE,
    SUBSTRATE_INVARIANTS,
    TOPOLOGY_TYPES,
    TopologicalSpace,
    VICSEK_AXIS_SIZE,
    _menger_holes,
    _sierpinski_triangle_holes,
    _vicsek_holes,
)


_PASS: list[str] = []
_FAIL: list[tuple[str, str]] = []


def case(name: str):
    def deco(fn):
        try:
            fn()
            _PASS.append(name)
            print(f"  PASS  {name}")
        except Exception as e:
            _FAIL.append((name, traceback.format_exc()))
            print(f"  FAIL  {name}: {e}")
        return fn
    return deco


# ---- Active-cell counts (the fractal-recursion invariant) ----

@case("triangle: 243 active cells (3^5) on 32x32 grid")
def _():
    holes = _sierpinski_triangle_holes()
    assert len(holes) == 32 * 32 - 243


@case("vicsek: 125 active cells (5^3) on 27x27 grid")
def _():
    holes = _vicsek_holes()
    assert len(holes) == 27 * 27 - 125


@case("menger: 400 active cells (20^2) on 9x9x9 cube")
def _():
    holes = _menger_holes()
    assert len(holes) == 9 ** 3 - 400


# ---- Registration ----

@case("all R18 substrates registered in TOPOLOGY_TYPES + EXPERIMENTAL")
def _():
    for topo in ("sierpinski_triangle", "vicsek", "menger"):
        assert topo in TOPOLOGY_TYPES, f"{topo} not in TOPOLOGY_TYPES"
        assert topo in EXPERIMENTAL_TOPOLOGIES, f"{topo} not experimental"
        assert topo in SUBSTRATE_INVARIANTS, f"{topo} missing invariants"


# ---- Constructor validation ----

@case("each substrate rejects wrong axis_size")
def _():
    for topo, (axis, dims) in SUBSTRATE_INVARIANTS.items():
        if topo == "sierpinski":
            continue  # covered by the carpet test
        try:
            TopologicalSpace(num_dimensions=dims, axis_size=axis - 1, topology_type=topo)
        except ValueError:
            continue
        raise AssertionError(f"{topo} should reject axis={axis-1}")


@case("each substrate rejects wrong num_dimensions")
def _():
    for topo, (axis, dims) in SUBSTRATE_INVARIANTS.items():
        if topo == "sierpinski":
            continue
        wrong_dims = 3 if dims == 2 else 2
        try:
            TopologicalSpace(num_dimensions=wrong_dims, axis_size=axis, topology_type=topo)
        except ValueError:
            continue
        raise AssertionError(f"{topo} should reject dims={wrong_dims}")


# ---- Adjacency invariants ----

def _build(topo: str) -> TopologicalSpace:
    axis, dims = SUBSTRATE_INVARIANTS[topo]
    return TopologicalSpace(num_dimensions=dims, axis_size=axis, topology_type=topo)


@case("triangle: holes have empty neighbor lists")
def _():
    t = _build("sierpinski_triangle")
    holes = set(range(t.total_cells)) - set(t.active_cells)
    for h in holes:
        assert t.get_neighbors(h) == [], f"hole {h} has neighbors"


@case("vicsek: holes have empty neighbor lists")
def _():
    t = _build("vicsek")
    holes = set(range(t.total_cells)) - set(t.active_cells)
    for h in holes:
        assert t.get_neighbors(h) == [], f"hole {h} has neighbors"


@case("menger: holes have empty neighbor lists")
def _():
    t = _build("menger")
    holes = set(range(t.total_cells)) - set(t.active_cells)
    for h in holes:
        assert t.get_neighbors(h) == [], f"hole {h} has neighbors"


@case("active cells never have hole neighbors (all 3 substrates)")
def _():
    for topo in ("sierpinski_triangle", "vicsek", "menger"):
        t = _build(topo)
        active = set(t.active_cells)
        for c in active:
            for n in t.get_neighbors(c):
                assert n in active, f"{topo}: cell {c} -> hole {n}"


@case("triangle/vicsek max_degree is 4 (2D von Neumann)")
def _():
    for topo in ("sierpinski_triangle", "vicsek"):
        t = _build(topo)
        assert t.max_degree <= 4, f"{topo}: max_degree {t.max_degree} > 4"


@case("menger max_degree is 6 (3D von Neumann)")
def _():
    t = _build("menger")
    assert t.max_degree <= 6, f"menger max_degree {t.max_degree} > 6"


# ---- Connectivity (substrate is reachable end-to-end) ----

@case("vicsek is connected: distance(corner_active, opposite_corner_active) > 0")
def _():
    t = _build("vicsek")
    # corner cell (0,0) is active for vicsek? digits all 0 → not on cross → hole.
    # Pick first and last active cells.
    src, dst = t.active_cells[0], t.active_cells[-1]
    d = t._dist_matrix[src, dst]
    assert d > 0, f"vicsek disconnected: dist({src},{dst})={d}"


@case("triangle is connected (all active cells reachable from cell 0)")
def _():
    t = _build("sierpinski_triangle")
    # cell (0,0) is active under (x AND y)==0
    src = 0
    assert src in t.active_cells
    for dst in t.active_cells:
        d = t._dist_matrix[src, dst]
        assert d >= 0, f"triangle: cell {dst} unreachable from 0"


@case("menger is connected (all active cells reachable from cell 0)")
def _():
    t = _build("menger")
    src = 0  # (0,0,0) corner: digits all 0, no 1s -> active
    assert src in t.active_cells
    for dst in t.active_cells:
        d = t._dist_matrix[src, dst]
        assert d >= 0, f"menger: cell {dst} unreachable from 0"


# ---- Round-trip serialisation ----

def _make_game(topo: str) -> GameDefV2:
    axis, dims = SUBSTRATE_INVARIANTS[topo]
    return GameDefV2(
        game_id=f"rt_{topo}",
        num_dimensions=dims,
        axis_size=axis,
        topology_type=topo,
        placement_rule=PlacementRule(),
        capture_rule=CaptureRule(capture_type="surround"),
        propagation_rule=PropagationRule(),
        win_condition=WinCondition(
            condition_type="territory", threshold=0.5, max_turns=50
        ),
        turn_structure=TurnStructure(),
        action_rule=ActionRule(),
    )


@case("round-trip: GameDefV2 to_dict/from_dict preserves all 3 substrates")
def _():
    for topo in ("sierpinski_triangle", "vicsek", "menger"):
        g1 = _make_game(topo)
        g2 = GameDefV2.from_dict(json.loads(json.dumps(g1.to_dict())))
        assert g2.topology_type == topo
        assert g2.axis_size == g1.axis_size
        assert g2.num_dimensions == g1.num_dimensions


# ---- Entry ----

if __name__ == "__main__":
    print("\n=== R18 substrate topology tests ===\n")
    print(f"\n{len(_PASS)} passed, {len(_FAIL)} failed")
    if _FAIL:
        print("\n--- failures ---")
        for name, tb in _FAIL:
            print(f"\n{name}:\n{tb}")
        sys.exit(1)
    sys.exit(0)
