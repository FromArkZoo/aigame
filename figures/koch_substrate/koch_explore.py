"""Exploration: what would a Koch-snowflake aigame substrate look like?

NOT an engine change. Builds the candidate board the way aigame substrates work
(a lattice masked to an active region) and measures it, so we can assess fit
before deciding whether to build it.

Candidate board = triangular lattice (degree-6, like the existing `hex` type)
masked to the interior of an iteration-n Koch snowflake. The snowflake is the
*outline*; the playable area is a filled degree-6 region. We measure: #active
cells, degree distribution, and the boundary (low-degree) fraction vs a plain
hexagon of the same lattice — the only thing the fractal edge actually buys.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from pathlib import Path as FPath

HERE = FPath(__file__).resolve().parent


def koch_polygon(n_iter):
    """Vertices of the Koch snowflake after n_iter, CCW, outward bumps."""
    # initial equilateral triangle (CCW)
    ang = np.deg2rad([90, 210, 330])
    pts = [np.array([np.cos(a), np.sin(a)]) for a in ang]
    pts.append(pts[0])
    rot = lambda t: np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
    R = rot(-np.pi / 3)  # outward peak for CCW polygon
    for _ in range(n_iter):
        new = []
        for p1, p2 in zip(pts[:-1], pts[1:]):
            d = (p2 - p1) / 3.0
            a = p1 + d
            b = p1 + 2 * d
            peak = a + R @ d
            new += [p1, a, peak, b]
        new.append(pts[-1])
        pts = new
    return np.array(pts)


def tri_lattice(spacing, bbox):
    """Triangular lattice points + index map; 6-neighbour basis."""
    e1 = np.array([1.0, 0.0]) * spacing
    e2 = np.array([0.5, np.sqrt(3) / 2]) * spacing
    (xmin, xmax, ymin, ymax) = bbox
    # generous index ranges
    pad = 4
    imax = int((xmax - xmin) / spacing) + pad
    jmax = int((ymax - ymin) / (spacing * np.sqrt(3) / 2)) + pad
    pts, idx = {}, {}
    k = 0
    for j in range(-pad, jmax + pad):
        for i in range(-imax - pad, imax + pad):
            p = np.array([xmin, ymin]) + i * e1 + j * e2
            if xmin - spacing <= p[0] <= xmax + spacing and ymin - spacing <= p[1] <= ymax + spacing:
                idx[(i, j)] = k
                pts[(i, j)] = p
                k += 1
    return pts, idx


# the 6 triangular-lattice neighbours in (i,j) basis
NEI = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]


def build_board(n_iter, spacing):
    poly = koch_polygon(n_iter)
    path = Path(poly)
    bbox = (poly[:, 0].min(), poly[:, 0].max(), poly[:, 1].min(), poly[:, 1].max())
    pts, idx = tri_lattice(spacing, bbox)
    coords = np.array(list(pts.values()))
    keys = list(pts.keys())
    inside = path.contains_points(coords)
    active = set(keys[m] for m in range(len(keys)) if inside[m])
    deg = {}
    for (i, j) in active:
        deg[(i, j)] = sum(((i + di, j + dj) in active) for (di, dj) in NEI)
    return poly, pts, active, deg


def hexagon_board(radius_cells, spacing):
    """Plain hexagon of the same lattice (control) — same family as `hex`."""
    pts, idx = tri_lattice(spacing, (-radius_cells * spacing, radius_cells * spacing,
                                     -radius_cells * spacing, radius_cells * spacing))
    # hexagonal region in axial coords: |i|,|j|,|i+j| <= R
    active = set()
    for (i, j) in pts:
        if abs(i) <= radius_cells and abs(j) <= radius_cells and abs(i + j) <= radius_cells:
            active.add((i, j))
    deg = {(i, j): sum(((i + di, j + dj) in active) for (di, dj) in NEI) for (i, j) in active}
    return pts, active, deg


def stats(active, deg):
    n = len(active)
    from collections import Counter
    h = Counter(deg.values())
    bdry = sum(v for d, v in h.items() if d < 6)
    return n, dict(sorted(h.items())), bdry, (bdry / n if n else 0)


# ---- measure a few configurations ----
print("KOCH SNOWFLAKE BOARD (triangular lattice, degree-6, masked to interior)")
print(f"{'iter':>4} {'spacing':>8} {'#active':>8} {'deg<6 (boundary)':>18} {'bdry frac':>10}  degree histogram")
configs = [(1, 0.18), (2, 0.10), (2, 0.06), (3, 0.06)]
koch_results = {}
for n_iter, sp in configs:
    poly, pts, active, deg = build_board(n_iter, sp)
    n, hist, bdry, frac = stats(active, deg)
    koch_results[(n_iter, sp)] = (poly, pts, active, deg, n, hist, frac)
    print(f"{n_iter:>4} {sp:>8.2f} {n:>8} {bdry:>18} {frac:>10.3f}  {hist}")

print("\nPLAIN HEXAGON CONTROL (same lattice) — what the fractal edge is compared against")
print(f"{'R':>4} {'spacing':>8} {'#active':>8} {'deg<6 (boundary)':>18} {'bdry frac':>10}  degree histogram")
for R, sp in [(6, 0.10), (10, 0.06), (14, 0.06)]:
    pts, active, deg = hexagon_board(R, sp)
    n, hist, bdry, frac = stats(active, deg)
    print(f"{R:>4} {sp:>8.2f} {n:>8} {bdry:>18} {frac:>10.3f}  {hist}")

# ---- visualize ----
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# panel 1: snowflake outlines iter 1-3
ax = axes[0]
for n_iter, c in [(1, "#bbb"), (2, "#77a"), (3, "#225")]:
    poly = koch_polygon(n_iter)
    ax.plot(poly[:, 0], poly[:, 1], color=c, lw=1.2, label=f"iteration {n_iter}")
ax.set_aspect("equal"); ax.axis("off"); ax.legend(loc="lower right", fontsize=9)
ax.set_title("Koch snowflake outline (the fractal is the BOUNDARY)", fontsize=11)

# panel 2: candidate board (iter 2, spacing .06) colored by degree
poly, pts, active, deg, n, hist, frac = koch_results[(2, 0.06)]
ax = axes[1]
xs = [pts[k][0] for k in active]; ys = [pts[k][1] for k in active]
cs = [deg[k] for k in active]
sc = ax.scatter(xs, ys, c=cs, s=10, cmap="viridis", vmin=2, vmax=6)
ax.plot(poly[:, 0], poly[:, 1], color="k", lw=0.6, alpha=0.5)
ax.set_aspect("equal"); ax.axis("off")
ax.set_title(f"Candidate board: degree-6 lattice masked to snowflake\n(iter 2, {n} cells, {frac:.0%} boundary)", fontsize=11)
plt.colorbar(sc, ax=ax, shrink=0.7, label="cell degree (6=interior)")

# panel 3: degree histogram, koch vs hexagon at similar cell count
ax = axes[2]
_, _, _, _, nk, hk, _ = koch_results[(2, 0.06)]
pts_h, active_h, deg_h = hexagon_board(10, 0.06)
nh, hh, _, _ = stats(active_h, deg_h)
ks = sorted(set(hk) | set(hh))
w = 0.38
ax.bar([k - w / 2 for k in ks], [hk.get(k, 0) for k in ks], w, label=f"Koch snowflake (n={nk})", color="#3a7")
ax.bar([k + w / 2 for k in ks], [hh.get(k, 0) for k in ks], w, label=f"plain hexagon (n={nh})", color="#a73")
ax.set_xlabel("cell degree"); ax.set_ylabel("# cells")
ax.set_title("Degree distribution: snowflake vs plain hexagon\n(same lattice & ~same size)", fontsize=11)
ax.legend(fontsize=9)

plt.tight_layout()
out = HERE / "koch_substrate.png"
plt.savefig(out, dpi=110, bbox_inches="tight")
print(f"\n[written] {out}")
