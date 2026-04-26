"""Hole-set generators for the pattern-vs-random probe.

Three hole patterns, all on a 9x9 grid, all 17 holes (matching the level-2
Sierpinski carpet's hole budget; 64 active cells in each).

Cell index convention: cell = y * axis_size + x  (matches TopologicalSpace).

  - sierpinski : level-2 Sierpinski carpet (the existing experimental
                 substrate; included here for symmetry)
  - random     : 17 holes drawn uniformly without replacement from the 81
                 cells, fixed seed for reproducibility. Re-rolls if the
                 active region is disconnected or doesn't connect both
                 faces along x or y (connection-win must be feasible).
  - structured : 17 holes on a regular lattice with stride 2 (16 holes at
                 (1+2i, 1+2j)) plus the centre cell (4,4). Diffuse small-
                 scale regularity, contrasting with sierpinski's clustered
                 medium-scale fractal pattern.

All three patterns are validated to leave the active region connected and
both axis-faces reachable from one another.
"""

from __future__ import annotations

import os
import random
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from game_engine.topology import _sierpinski_carpet_holes


AXIS_SIZE = 9
NUM_HOLES = 17
RANDOM_SEED = 20260426  # locked for reproducibility


def _xy(x: int, y: int) -> int:
    return y * AXIS_SIZE + x


def sierpinski_holes() -> list[int]:
    """Level-2 Sierpinski carpet pattern (17 holes)."""
    return sorted(_sierpinski_carpet_holes(AXIS_SIZE))


def _is_face_connected(holes: set[int]) -> bool:
    """True iff the active region is one component AND both x-faces and
    both y-faces are mutually reachable. Guarantees connection-win games
    are well-posed on this hole-set.
    """
    active = [c for c in range(AXIS_SIZE * AXIS_SIZE) if c not in holes]
    if not active:
        return False
    active_set = set(active)
    # BFS from active[0]
    visited = {active[0]}
    stack = [active[0]]
    while stack:
        cell = stack.pop()
        x, y = cell % AXIS_SIZE, cell // AXIS_SIZE
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < AXIS_SIZE and 0 <= ny < AXIS_SIZE:
                n = ny * AXIS_SIZE + nx
                if n in active_set and n not in visited:
                    visited.add(n)
                    stack.append(n)
    if visited != active_set:
        return False
    # Check both face-pairs are present in the single component
    has_x0 = any(c % AXIS_SIZE == 0 for c in visited)
    has_xN = any(c % AXIS_SIZE == AXIS_SIZE - 1 for c in visited)
    has_y0 = any(c // AXIS_SIZE == 0 for c in visited)
    has_yN = any(c // AXIS_SIZE == AXIS_SIZE - 1 for c in visited)
    return has_x0 and has_xN and has_y0 and has_yN


def random_holes(seed: int = RANDOM_SEED) -> list[int]:
    """Uniform random 17 holes on a 9x9 grid; rerolls until face-connected.

    Uses the locked seed by default; if the first draw fails the connectivity
    guard, advances the seed deterministically and retries.
    """
    cells = list(range(AXIS_SIZE * AXIS_SIZE))
    attempt = 0
    while True:
        rng = random.Random(seed + attempt)
        candidate = set(rng.sample(cells, NUM_HOLES))
        if _is_face_connected(candidate):
            return sorted(candidate)
        attempt += 1
        if attempt > 1000:
            raise RuntimeError(
                f"random_holes could not find a face-connected layout "
                f"after 1000 attempts from seed {seed}"
            )


def structured_holes() -> list[int]:
    """Diffuse regular pattern — stride-2 lattice + centre.

    Pattern (X = hole):
        . . . . . . . . .
        . X . X . X . X .
        . . . . . . . . .
        . X . X . X . X .
        . . . . X . . . .
        . X . X . X . X .
        . . . . . . . . .
        . X . X . X . X .
        . . . . . . . . .

    16 holes on a 4x4 stride-2 lattice at (1+2i, 1+2j) plus the centre (4,4).
    All all-empty rows (y=0,2,4,6,8) are active corridors connecting both
    x-faces; row y=2/6 are fully clear so connection-win is well-posed.
    """
    holes: set[int] = set()
    for j in range(4):
        for i in range(4):
            holes.add(_xy(1 + 2 * i, 1 + 2 * j))
    holes.add(_xy(4, 4))
    assert len(holes) == NUM_HOLES, (
        f"structured pattern has {len(holes)} holes, expected {NUM_HOLES}"
    )
    return sorted(holes)


PATTERNS = {
    "sierpinski": sierpinski_holes,
    "random": random_holes,
    "structured": structured_holes,
}


def render(holes: list[int]) -> str:
    """Render a hole-set as ASCII art (X = hole, . = active)."""
    hole_set = set(holes)
    rows = []
    for y in range(AXIS_SIZE):
        row = []
        for x in range(AXIS_SIZE):
            row.append("X" if _xy(x, y) in hole_set else ".")
        rows.append(" ".join(row))
    return "\n".join(rows)


if __name__ == "__main__":
    for name, fn in PATTERNS.items():
        holes = fn()
        connected = _is_face_connected(set(holes))
        print(f"\n{name}: {len(holes)} holes, face-connected={connected}")
        print(render(holes))
