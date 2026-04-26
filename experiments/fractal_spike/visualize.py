"""Visualization for the fractal-topology spike.

Two outputs:
  1. ASCII rendering of the 9x9 Sierpinski carpet with hole pattern.
  2. PNG replay grid for a sample greedy-vs-greedy game on the highest-
     priority fractal candidate (Pair B by default — biggest substrate
     effect in probe). Stones overlaid on a heatmap of board_values
     (the influence shadow). Holes drawn as solid black blocks.

Run as: .venv/bin/python experiments/fractal_spike/visualize.py [--candidate frac_B_fractal]
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from game_engine.engine_v2 import GameEngineV2
from game_engine.game_def_v2 import GameDefV2
from game_engine.topology import _sierpinski_carpet_holes, SIERPINSKI_AXIS_SIZE
from training.utils import GreedyAgent


CANDIDATES_DIR = os.path.join(_HERE, "candidates")


def render_ascii_carpet() -> str:
    """ASCII render of the 9x9 carpet with holes as ·."""
    holes = _sierpinski_carpet_holes(SIERPINSKI_AXIS_SIZE)
    s = SIERPINSKI_AXIS_SIZE
    rows = []
    rows.append("Sierpinski level-2 carpet (9x9 → 64 active, 17 holes):")
    rows.append("    " + " ".join(str(x) for x in range(s)))
    rows.append("   +" + "--" * s + "+")
    for y in range(s):
        cells = []
        for x in range(s):
            idx = y * s + x
            cells.append("·" if idx in holes else "□")
        rows.append(f" {y} | " + " ".join(cells) + " |")
    rows.append("   +" + "--" * s + "+")
    rows.append("Active: 64, Holes: 17 (central 3x3 + 8 sub-block centers)")
    return "\n".join(rows)


def _capture_replay(game: GameDefV2, num_moves: int = 30, seed: int = 0):
    """Greedy-vs-greedy replay; returns list of (board_owners, board_values) snapshots."""
    eng = GameEngineV2(game)
    a0 = GreedyAgent(eng, player_num=1, seed=seed)
    a1 = GreedyAgent(eng, player_num=2, seed=seed + 1)
    eng.reset()
    snapshots = [(eng.board_owners.copy(), eng.board_values.copy())]
    step = 0
    done = False
    while not done and step < num_moves:
        legal = eng.get_legal_actions()
        if len(legal) == 0:
            break
        current = eng.get_current_player()
        agent = a0 if current == 0 else a1
        action, _, _ = agent.select_action(None, legal_actions=legal, deterministic=True)
        _, _, done, _ = eng.step(action)
        snapshots.append((eng.board_owners.copy(), eng.board_values.copy()))
        step += 1
    return snapshots


def _build_html(game: GameDefV2, snapshots, out_path: str) -> None:
    """Build a self-contained HTML page rendering each snapshot as a small grid."""
    s = game.axis_size
    holes = _sierpinski_carpet_holes(s) if game.topology_type == "sierpinski" else set()

    # Compute symmetric color range from board_values across all snapshots.
    max_abs_value = 0.0
    for _, vals in snapshots:
        v = float(abs(vals).max()) if vals.size else 0.0
        if v > max_abs_value:
            max_abs_value = v
    max_abs_value = max(max_abs_value, 1e-6)

    snap_data = []
    for owners, values in snapshots:
        snap_data.append({
            "owners": owners.tolist(),
            "values": values.tolist(),
        })

    title = f"{game.game_id} ({game.topology_type} {s}x{s})"
    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{title}</title>
<style>
  body {{ font-family: monospace; background: #1a1a1a; color: #ccc; padding: 16px; }}
  h1 {{ font-size: 16px; }}
  .grid-row {{ display: flex; flex-wrap: wrap; gap: 12px; }}
  .panel {{ display: flex; flex-direction: column; align-items: center; }}
  .panel small {{ color: #888; font-size: 10px; margin-bottom: 2px; }}
  table {{ border-collapse: collapse; }}
  td {{
    width: 16px; height: 16px; border: 1px solid #333;
    text-align: center; vertical-align: middle;
    font-size: 11px; font-weight: bold;
  }}
  .hole {{ background: #000 !important; color: #000; }}
  .p1 {{ color: #fff; }}
  .p2 {{ color: #fff; }}
</style>
</head><body>
<h1>{title} — greedy-vs-greedy first {len(snapshots)} snapshots</h1>
<p>P1 = ●  P2 = ○  Holes = solid black. Cell shading = board_values (red=P1 influence, blue=P2 influence).</p>
<div class="grid-row" id="grid"></div>
<script>
const HOLES = new Set({sorted(holes)!r});
const SNAPS = {json.dumps(snap_data)};
const S = {s};
const MAXV = {max_abs_value};
const root = document.getElementById('grid');
SNAPS.forEach((snap, idx) => {{
  const panel = document.createElement('div');
  panel.className = 'panel';
  const lbl = document.createElement('small');
  lbl.textContent = idx === 0 ? 'start' : `move ${{idx}}`;
  panel.appendChild(lbl);
  const tbl = document.createElement('table');
  for (let y = 0; y < S; y++) {{
    const tr = document.createElement('tr');
    for (let x = 0; x < S; x++) {{
      const i = y * S + x;
      const td = document.createElement('td');
      if (HOLES.has(i)) {{
        td.className = 'hole';
      }} else {{
        const v = snap.values[i];
        const intensity = Math.min(Math.abs(v) / MAXV, 1.0);
        const alpha = (0.15 + 0.85 * intensity).toFixed(3);
        const color = v >= 0 ? `rgba(220,60,60,${{alpha}})` : `rgba(60,120,220,${{alpha}})`;
        td.style.background = color;
        const owner = snap.owners[i];
        if (owner === 1) {{ td.className = 'p1'; td.textContent = '●'; }}
        else if (owner === 2) {{ td.className = 'p2'; td.textContent = '○'; }}
      }}
      tr.appendChild(td);
    }}
    tbl.appendChild(tr);
  }}
  panel.appendChild(tbl);
  root.appendChild(panel);
}});
</script>
</body></html>
"""
    with open(out_path, "w") as fp:
        fp.write(html)


def render_replay_png(candidate_name: str) -> str:
    """Build HTML + render to PNG via Playwright/Chromium. Returns PNG path."""
    with open(os.path.join(CANDIDATES_DIR, f"{candidate_name}.json")) as fp:
        game = GameDefV2.from_dict(json.load(fp))
    snapshots = _capture_replay(game, num_moves=24, seed=0)

    # Write HTML to a temp file we keep next to the PNG for traceability.
    html_path = os.path.join(_HERE, f"replay_{candidate_name}.html")
    _build_html(game, snapshots, html_path)

    png_path = os.path.join(_HERE, f"replay_{candidate_name}.png")
    cmd = [
        "npx", "playwright", "screenshot",
        "--browser", "chromium",
        "--full-page",
        "--wait-for-timeout=1000",
        f"file://{html_path}",
        png_path,
    ]
    print(f"  rendering: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  Playwright stderr:\n{res.stderr}")
        raise RuntimeError(f"playwright failed (rc={res.returncode})")
    return png_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", default="frac_B_fractal",
                        help="candidate name to render replay for")
    parser.add_argument("--ascii-only", action="store_true",
                        help="skip PNG render (no Playwright)")
    args = parser.parse_args()

    print(render_ascii_carpet())
    print()

    if args.ascii_only:
        return 0

    # Render replays for the highest-priority fractal candidate, plus its control.
    pair = args.candidate.split("_")[1]  # 'A' / 'B' / 'C'
    targets = [args.candidate]
    if args.candidate.endswith("fractal"):
        targets.append(f"frac_{pair}_control")

    for name in targets:
        png = render_replay_png(name)
        print(f"  wrote {os.path.relpath(png, _REPO)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
