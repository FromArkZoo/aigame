"""Render the four substrate hole-patterns to a single side-by-side PNG.

Output: experiments/pattern_vs_random/substrates.png

Run as: .venv/bin/python experiments/pattern_vs_random/visualize.py
"""

from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.pattern_vs_random.hole_patterns import (
    AXIS_SIZE, sierpinski_holes, random_holes, structured_holes,
)


def _grid(holes: list[int], axis: int) -> np.ndarray:
    """Return an axis x axis array, 1 = hole, 0 = active."""
    arr = np.zeros((axis, axis), dtype=int)
    for h in holes:
        x, y = h % axis, h // axis
        arr[y, x] = 1
    return arr


def main() -> None:
    panels = [
        ("pat_grid (8x8, 0 holes)", _grid([], 8), 8),
        ("pat_fractal (Sierpinski L2)", _grid(sierpinski_holes(), AXIS_SIZE), AXIS_SIZE),
        ("pat_random (seed 20260426)", _grid(random_holes(), AXIS_SIZE), AXIS_SIZE),
        ("pat_structured (stride-2 + ctr)", _grid(structured_holes(), AXIS_SIZE), AXIS_SIZE),
    ]

    fig, axes = plt.subplots(1, 4, figsize=(16, 4.4))
    for ax, (title, arr, n) in zip(axes, panels):
        ax.imshow(arr, cmap="Greys", vmin=0, vmax=1)
        ax.set_title(title, fontsize=10)
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.tick_params(axis="both", which="both", length=0, labelsize=7)
        ax.set_xlim(-0.5, n - 0.5)
        ax.set_ylim(n - 0.5, -0.5)
        for i in range(n + 1):
            ax.axhline(i - 0.5, color="lightgray", linewidth=0.4)
            ax.axvline(i - 0.5, color="lightgray", linewidth=0.4)
        active_count = int((arr == 0).sum())
        hole_count = int((arr == 1).sum())
        ax.set_xlabel(f"{active_count} active, {hole_count} holes", fontsize=9)

    fig.suptitle(
        "Pattern-vs-random probe: 4 substrates "
        "(all 64 active cells, Pair-C ruleset)",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out_path = os.path.join(_HERE, "substrates.png")
    fig.savefig(out_path, dpi=150)
    print(f"  wrote {os.path.relpath(out_path, _REPO)}")


if __name__ == "__main__":
    main()
