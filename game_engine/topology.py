"""N-dimensional topological spaces with configurable adjacency.

Provides the spatial substrate for V2/V3 games. A TopologicalSpace is an
n-dimensional grid where each axis has a fixed size.  The topology_type
controls how adjacency is computed:

  - "grid"  : von Neumann neighbourhood (face-adjacent only)
  - "torus" : von Neumann with wraparound edges (no corners/edges)
  - "hex"   : hexagonal adjacency (2D only, 6 neighbours per interior cell)
  - "moore" : Moore neighbourhood (face + diagonal adjacent, 8 neighbours in 2D)
"""

from __future__ import annotations

from typing import Iterable

import numpy as np


# Supported topology types
TOPOLOGY_TYPES = ("grid", "torus", "hex", "moore", "sierpinski", "holes")

# Topology types whose generated population uses must be opted-in via
# config.topology_types. Mutation skips these unless explicitly enabled.
# "holes" requires an explicit hole-set and is for hand-crafted experiments
# (e.g. pattern-vs-random probe); evolution should not mutate into it.
EXPERIMENTAL_TOPOLOGIES = frozenset({"sierpinski", "holes"})

# Sierpinski-carpet baseline: level-2 carpet on a 9x9 grid.
SIERPINSKI_AXIS_SIZE = 9


def _sierpinski_carpet_holes(axis_size: int = SIERPINSKI_AXIS_SIZE) -> set[int]:
    """Return the set of cell indices that are holes in a level-2 Sierpinski
    carpet on an axis_size x axis_size grid.

    Cell index encoding matches TopologicalSpace.coords_to_cell((x, y)) with
    coords[0] (== x) as the fast-varying dimension, i.e. cell = y * axis_size + x.
    Equivalent to row-major packing where x is column and y is row.

    Hole pattern:
      - The central 3x3 sub-block: rows 3-5 x cols 3-5 (9 cells)
      - The center cell of each of the 8 outer 3x3 sub-blocks:
        (col, row) = (1,1), (4,1), (7,1), (1,4), (7,4), (1,7), (4,7), (7,7)
        (8 cells; (4,4) is already inside the central block above)
    Total: 17 holes; 64 active cells.
    """
    if axis_size != SIERPINSKI_AXIS_SIZE:
        raise ValueError(
            f"Sierpinski carpet level-2 requires axis_size=={SIERPINSKI_AXIS_SIZE}, "
            f"got {axis_size}"
        )
    holes: set[int] = set()
    # Central 3x3 sub-block
    for y in range(3, 6):
        for x in range(3, 6):
            holes.add(y * axis_size + x)
    # Center cell of each outer 3x3 sub-block
    for sub_y in (0, 3, 6):
        for sub_x in (0, 3, 6):
            if sub_x == 3 and sub_y == 3:
                continue  # central block already covered
            cy = sub_y + 1
            cx = sub_x + 1
            holes.add(cy * axis_size + cx)
    return holes


class TopologicalSpace:
    """An n-dimensional grid with precomputed adjacency."""

    __slots__ = (
        "num_dimensions", "axis_size", "total_cells",
        "topology_type", "max_degree", "_neighbors",
        "active_cells", "active_mask", "num_active_cells",
        "_dist_matrix", "_holes",
    )

    def __init__(
        self,
        num_dimensions: int,
        axis_size: int,
        topology_type: str = "grid",
        holes: "Iterable[int] | None" = None,
    ) -> None:
        if num_dimensions < 1:
            raise ValueError(f"num_dimensions must be >= 1, got {num_dimensions}")
        if axis_size < 2:
            raise ValueError(f"axis_size must be >= 2, got {axis_size}")
        if topology_type not in TOPOLOGY_TYPES:
            raise ValueError(
                f"topology_type must be one of {TOPOLOGY_TYPES}, got {topology_type!r}"
            )
        if topology_type == "hex" and num_dimensions != 2:
            raise ValueError("hex topology is only supported for 2D (num_dimensions=2)")
        if topology_type == "sierpinski":
            if num_dimensions != 2:
                raise ValueError(
                    "sierpinski topology is only supported for 2D (num_dimensions=2)"
                )
            if axis_size != SIERPINSKI_AXIS_SIZE:
                raise ValueError(
                    f"sierpinski topology requires axis_size=={SIERPINSKI_AXIS_SIZE} "
                    f"(level-2 carpet baseline), got {axis_size}"
                )
        if topology_type == "holes":
            if num_dimensions != 2:
                raise ValueError(
                    "holes topology is only supported for 2D (num_dimensions=2)"
                )
            if holes is None:
                raise ValueError(
                    "holes topology requires an explicit `holes` argument"
                )

        self.num_dimensions = num_dimensions
        self.axis_size = axis_size
        self.topology_type = topology_type
        self.total_cells = axis_size ** num_dimensions

        # Frozen hole-set, populated for sierpinski and holes topologies.
        # For sierpinski, computed from the level-2 carpet pattern. For
        # "holes", taken from the explicit `holes` argument and validated.
        self._holes: frozenset[int] | None = None
        if topology_type == "holes":
            hole_set = frozenset(int(h) for h in holes)
            for h in hole_set:
                if not (0 <= h < self.total_cells):
                    raise ValueError(
                        f"hole index {h} out of range [0, {self.total_cells})"
                    )
            self._holes = hole_set

        # Active-cell awareness. Default: every cell is active. Non-rectangular
        # topologies (e.g. sierpinski) override these in their _build_*_neighbors.
        self.active_cells: list[int] = list(range(self.total_cells))
        self.active_mask: np.ndarray = np.ones(self.total_cells, dtype=bool)
        self.num_active_cells: int = self.total_cells

        # All-pairs distance matrix. Sentinel None for rectangular topologies
        # which compute distance() analytically; populated by topologies that
        # need graph distance over a sparse adjacency (sierpinski).
        self._dist_matrix: np.ndarray | None = None

        # Precompute neighbour lists for every cell.
        self._neighbors: list[list[int]] = [[] for _ in range(self.total_cells)]
        self._precompute_neighbors()

        # Max degree: maximum number of neighbours any cell has
        self.max_degree = max(
            (len(nbrs) for nbrs in self._neighbors), default=0
        )

    # ------------------------------------------------------------------
    # Coordinate conversion
    # ------------------------------------------------------------------

    def cell_to_coords(self, cell_idx: int) -> tuple[int, ...]:
        """Convert a flat cell index to n-dimensional coordinates.

        coords[0] is the least-significant (fastest-varying) dimension.
        """
        coords: list[int] = []
        remaining = cell_idx
        for _ in range(self.num_dimensions):
            coords.append(remaining % self.axis_size)
            remaining //= self.axis_size
        return tuple(coords)

    def coords_to_cell(self, coords: tuple[int, ...]) -> int:
        """Convert n-dimensional coordinates to a flat cell index."""
        cell = 0
        for i in range(self.num_dimensions - 1, -1, -1):
            cell = cell * self.axis_size + coords[i]
        return cell

    # ------------------------------------------------------------------
    # Adjacency computation
    # ------------------------------------------------------------------

    def _precompute_neighbors(self) -> None:
        """Build adjacency lists based on topology_type."""
        if self.topology_type == "grid":
            self._build_grid_neighbors(wrap=False)
        elif self.topology_type == "torus":
            self._build_grid_neighbors(wrap=True)
        elif self.topology_type == "hex":
            self._build_hex_neighbors()
        elif self.topology_type == "moore":
            self._build_moore_neighbors()
        elif self.topology_type == "sierpinski":
            self._build_sierpinski_neighbors()
        elif self.topology_type == "holes":
            assert self._holes is not None
            self._build_holes_neighbors(self._holes)

    def _build_grid_neighbors(self, wrap: bool) -> None:
        """Von Neumann neighbourhood (face-adjacent).

        If wrap=True, edges connect to the opposite side (torus).
        """
        for cell in range(self.total_cells):
            coords = list(self.cell_to_coords(cell))
            nbrs: list[int] = []
            for dim in range(self.num_dimensions):
                original = coords[dim]
                for delta in (-1, 1):
                    new_val = original + delta
                    if 0 <= new_val < self.axis_size:
                        coords[dim] = new_val
                        nbrs.append(self.coords_to_cell(tuple(coords)))
                        coords[dim] = original
                    elif wrap:
                        # Torus: wrap around
                        coords[dim] = new_val % self.axis_size
                        nbrs.append(self.coords_to_cell(tuple(coords)))
                        coords[dim] = original
            self._neighbors[cell] = nbrs

    def _build_hex_neighbors(self) -> None:
        """Hexagonal adjacency using offset coordinates (2D only).

        Even rows (y%2==0): neighbours are the 4 orthogonal plus
        (x-1, y-1) and (x-1, y+1) — "pointy-top" offset.
        Odd rows (y%2==1): neighbours are the 4 orthogonal plus
        (x+1, y-1) and (x+1, y+1).

        This gives 6 neighbours per interior cell.
        """
        s = self.axis_size
        for cell in range(self.total_cells):
            x, y = self.cell_to_coords(cell)
            nbrs: list[int] = []

            if y % 2 == 0:
                # Even row offsets
                hex_deltas = [
                    (1, 0), (-1, 0),   # east, west
                    (0, 1), (0, -1),   # north, south
                    (-1, 1), (-1, -1), # NW, SW
                ]
            else:
                # Odd row offsets
                hex_deltas = [
                    (1, 0), (-1, 0),   # east, west
                    (0, 1), (0, -1),   # north, south
                    (1, 1), (1, -1),   # NE, SE
                ]

            for dx, dy in hex_deltas:
                nx, ny = x + dx, y + dy
                if 0 <= nx < s and 0 <= ny < s:
                    nbrs.append(self.coords_to_cell((nx, ny)))

            self._neighbors[cell] = nbrs

    def _build_moore_neighbors(self) -> None:
        """Moore neighbourhood: all cells within Chebyshev distance 1.

        In 2D this gives 8 neighbours (orthogonal + diagonal).
        In nD this gives 3^n - 1 neighbours for interior cells.
        """
        for cell in range(self.total_cells):
            coords = list(self.cell_to_coords(cell))
            nbrs: list[int] = []
            self._moore_recurse(coords, 0, coords[:], nbrs)
            self._neighbors[cell] = nbrs

    def _moore_recurse(
        self,
        original: list[int],
        dim: int,
        current: list[int],
        nbrs: list[int],
    ) -> None:
        """Recursively enumerate all Moore neighbours."""
        if dim == self.num_dimensions:
            if current != original:
                nbrs.append(self.coords_to_cell(tuple(current)))
            return
        for delta in (-1, 0, 1):
            new_val = original[dim] + delta
            if 0 <= new_val < self.axis_size:
                current[dim] = new_val
                self._moore_recurse(original, dim + 1, current, nbrs)
        current[dim] = original[dim]

    def _build_sierpinski_neighbors(self) -> None:
        """Sierpinski carpet on a 9x9 grid (level-2 carpet, 64 active cells).

        Holes form the standard level-2 pattern:
          - The central 3x3 sub-block (rows 3-5, cols 3-5) = 9 cells
          - The center cell of each of the 8 surrounding 3x3 sub-blocks
            (excluding the central sub-block whose center is already a hole)
            = 8 cells
        Total holes = 17, active cells = 64.
        """
        holes = _sierpinski_carpet_holes(self.axis_size)
        self._holes = frozenset(holes)
        self._build_holes_neighbors(holes)

    def _build_holes_neighbors(self, holes: Iterable[int]) -> None:
        """Generic 2D grid with arbitrary `holes` removed.

        Adjacency is von Neumann (4-connected) on the bounding box, with
        every neighbour-of-an-active-cell that lands on a hole dropped, and
        holes themselves given empty neighbour lists. Holes are walls.

        Also precomputes an all-pairs BFS distance matrix (-1 sentinel for
        pairs touching a hole). Used by both sierpinski and "holes" types.
        """
        s = self.axis_size
        hole_set = set(holes)
        active_mask = np.ones(self.total_cells, dtype=bool)
        for h in hole_set:
            active_mask[h] = False

        for cell in range(self.total_cells):
            if not active_mask[cell]:
                self._neighbors[cell] = []
                continue
            x, y = self.cell_to_coords(cell)
            nbrs: list[int] = []
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < s and 0 <= ny < s:
                    nidx = self.coords_to_cell((nx, ny))
                    if active_mask[nidx]:
                        nbrs.append(nidx)
            self._neighbors[cell] = nbrs

        self.active_mask = active_mask
        self.active_cells = [c for c in range(self.total_cells) if active_mask[c]]
        self.num_active_cells = len(self.active_cells)

        dist = np.full((self.total_cells, self.total_cells), -1, dtype=np.int32)
        for src in self.active_cells:
            dist[src, src] = 0
            frontier = [src]
            d = 0
            while frontier:
                d += 1
                next_frontier: list[int] = []
                for c in frontier:
                    for n in self._neighbors[c]:
                        if dist[src, n] == -1:
                            dist[src, n] = d
                            next_frontier.append(n)
                frontier = next_frontier
        self._dist_matrix = dist

    def get_neighbors(self, cell_idx: int) -> list[int]:
        """Return neighbours of *cell_idx*."""
        return self._neighbors[cell_idx]

    # ------------------------------------------------------------------
    # Group / connectivity helpers
    # ------------------------------------------------------------------

    def get_group(self, cell_idx: int, board_owners: np.ndarray) -> set[int]:
        """Return the connected component of same-owner cells containing *cell_idx*.

        Returns an empty set if the cell is empty (owner == 0).
        """
        owner = int(board_owners[cell_idx])
        if owner == 0:
            return set()
        visited: set[int] = set()
        stack = [cell_idx]
        while stack:
            cell = stack.pop()
            if cell in visited:
                continue
            if int(board_owners[cell]) != owner:
                continue
            visited.add(cell)
            stack.extend(self._neighbors[cell])
        return visited

    def get_liberties(self, group: set[int], board_owners: np.ndarray) -> set[int]:
        """Return empty cells adjacent to *group*."""
        liberties: set[int] = set()
        for cell in group:
            for nbr in self._neighbors[cell]:
                if int(board_owners[nbr]) == 0:
                    liberties.add(nbr)
        return liberties

    def connects_faces(self, cells: set[int], dimension: int) -> bool:
        """Check whether *cells* form a path connecting the two opposing
        faces along *dimension* (coordinate 0 and coordinate axis_size-1).

        Uses BFS restricted to *cells*.
        """
        if not cells:
            return False
        if dimension >= self.num_dimensions:
            return False

        # Find all cells on the low face (coord[dim] == 0)
        start_cells: list[int] = []
        for c in cells:
            if self.cell_to_coords(c)[dimension] == 0:
                start_cells.append(c)
        if not start_cells:
            return False

        # BFS from low-face cells, restricted to *cells*
        visited: set[int] = set()
        queue = list(start_cells)
        while queue:
            cell = queue.pop()
            if cell in visited:
                continue
            visited.add(cell)
            if self.cell_to_coords(cell)[dimension] == self.axis_size - 1:
                return True
            for nbr in self._neighbors[cell]:
                if nbr in cells and nbr not in visited:
                    queue.append(nbr)
        return False

    def distance(self, cell_a: int, cell_b: int) -> int:
        """Topology-aware distance between two cells.

        Uses the graph distance appropriate for the topology:
          - grid:  Manhattan distance on raw coordinates
          - torus: Manhattan distance with wraparound
          - hex:   axial hex distance (consistent with 6-neighbor adjacency)
          - moore: Chebyshev distance (consistent with 8-neighbor adjacency)

        Run 13 discovered that using Manhattan everywhere was a bug:
        on hex, the two "hex diagonals" are adjacent cells but Manhattan-2,
        so influence propagation was broken on all non-grid topologies.
        """
        if self._dist_matrix is not None:
            # BFS graph distance, precomputed for holes-based topologies.
            # Returns -1 if either endpoint is a hole.
            return int(self._dist_matrix[cell_a, cell_b])

        ca = self.cell_to_coords(cell_a)
        cb = self.cell_to_coords(cell_b)

        if self.topology_type == "moore":
            # Chebyshev distance: max absolute difference
            return max(abs(a - b) for a, b in zip(ca, cb))

        if self.topology_type == "torus":
            # Wrapped Manhattan: take the shorter path around each axis
            total = 0
            for a, b in zip(ca, cb):
                d = abs(a - b)
                total += min(d, self.axis_size - d)
            return total

        if self.topology_type == "hex":
            # Hex distance on offset coordinates.  Convert to axial then
            # compute standard axial hex distance.
            x_a, y_a = ca
            x_b, y_b = cb
            # Convert offset coords to axial (q, r): q = x - (y // 2), r = y
            q_a = x_a - (y_a // 2)
            q_b = x_b - (y_b // 2)
            r_a = y_a
            r_b = y_b
            # Axial distance
            dq = q_a - q_b
            dr = r_a - r_b
            return (abs(dq) + abs(dr) + abs(dq + dr)) // 2

        # grid: plain Manhattan
        return sum(abs(a - b) for a, b in zip(ca, cb))

    def cells_within_radius(self, cell_idx: int, radius: int) -> list[int]:
        """Return all cells within topological distance *radius* of *cell_idx*."""
        if self._dist_matrix is not None:
            row = self._dist_matrix[cell_idx]
            mask = (row >= 0) & (row <= radius)
            return np.where(mask)[0].tolist()
        result: list[int] = []
        for c in range(self.total_cells):
            if self.distance(cell_idx, c) <= radius:
                result.append(c)
        return result

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def compute_axis_size(num_dimensions: int, max_total_cells: int) -> int:
        """Compute the largest axis_size such that axis_size^n <= max_total_cells."""
        if num_dimensions <= 0:
            return 2
        axis = int(max_total_cells ** (1.0 / num_dimensions))
        # Adjust upward if we can fit
        while (axis + 1) ** num_dimensions <= max_total_cells:
            axis += 1
        # Ensure minimum of 2
        return max(axis, 2)
