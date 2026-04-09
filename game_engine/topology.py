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

import numpy as np


# Supported topology types
TOPOLOGY_TYPES = ("grid", "torus", "hex", "moore")


class TopologicalSpace:
    """An n-dimensional grid with precomputed adjacency."""

    __slots__ = (
        "num_dimensions", "axis_size", "total_cells",
        "topology_type", "max_degree", "_neighbors",
    )

    def __init__(
        self,
        num_dimensions: int,
        axis_size: int,
        topology_type: str = "grid",
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

        self.num_dimensions = num_dimensions
        self.axis_size = axis_size
        self.topology_type = topology_type
        self.total_cells = axis_size ** num_dimensions

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
        """Manhattan distance between two cells."""
        ca = self.cell_to_coords(cell_a)
        cb = self.cell_to_coords(cell_b)
        return sum(abs(a - b) for a, b in zip(ca, cb))

    def cells_within_radius(self, cell_idx: int, radius: int) -> list[int]:
        """Return all cells within Manhattan distance *radius* of *cell_idx*."""
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
