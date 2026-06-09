"""hex_rhombus topology — axial-coordinate triangular lattice on a rhombus
(the canonical Hex board). Spec §5a."""
from __future__ import annotations

import pytest

from game_engine.topology import TopologicalSpace


def _build(s: int = 6) -> TopologicalSpace:
    return TopologicalSpace(num_dimensions=2, axis_size=s, topology_type="hex_rhombus")


def test_all_cells_active_and_counts() -> None:
    t = _build(22)
    assert t.total_cells == 484
    assert t.num_active_cells == 484
    assert t.max_degree == 6


def test_corner_degrees() -> None:
    """Canonical Hex rhombus: acute corners (0,0),(s-1,s-1) degree 2;
    obtuse corners (s-1,0),(0,s-1) degree 3."""
    t = _build(6)
    s = 6
    deg = lambda q, r: len(t.get_neighbors(t.coords_to_cell((q, r))))
    assert deg(0, 0) == 2
    assert deg(s - 1, s - 1) == 2
    assert deg(s - 1, 0) == 3
    assert deg(0, s - 1) == 3
    # interior cell
    assert deg(2, 2) == 6


def test_adjacency_symmetric() -> None:
    t = _build(6)
    for c in range(t.total_cells):
        for n in t.get_neighbors(c):
            assert c in t.get_neighbors(n)


def test_distance_matches_adjacency_and_bfs() -> None:
    """Analytic axial distance must equal BFS graph distance (the R13 bug
    class: wrong distance silently breaks influence propagation)."""
    t = _build(5)
    # BFS from every cell
    for src in range(t.total_cells):
        dist = {src: 0}
        frontier = [src]
        while frontier:
            nxt = []
            for c in frontier:
                for n in t.get_neighbors(c):
                    if n not in dist:
                        dist[n] = dist[c] + 1
                        nxt.append(n)
            frontier = nxt
        for dst in range(t.total_cells):
            assert t.distance(src, dst) == dist[dst], (src, dst)


def test_cells_within_radius_center() -> None:
    t = _build(7)
    center = t.coords_to_cell((3, 3))
    ball = t.cells_within_radius(center, 1)
    assert len(ball) == 7  # self + 6 neighbors


def test_connects_faces_both_dims() -> None:
    t = _build(6)
    # a straight column q=2 spans dimension 1 (r: 0..5)
    col = {t.coords_to_cell((2, r)) for r in range(6)}
    assert t.connects_faces(col, 1)
    assert not t.connects_faces(col, 0)
    # broken column does not connect
    col.remove(t.coords_to_cell((2, 3)))
    assert not t.connects_faces(col, 1)


def test_requires_2d() -> None:
    with pytest.raises(ValueError):
        TopologicalSpace(num_dimensions=3, axis_size=6, topology_type="hex_rhombus")
