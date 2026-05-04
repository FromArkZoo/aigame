"""Extract per-substrate champion data for the substrate-comparison figure.

Output: data.json next to this script. Consumed by index.html.

Sources:
  - genesis_v2_run18_<substrate>.db    (stored GE per game)
  - experiments/r18_volatility/phase_a_per_game.csv  (pge_std per game = volatility lower bound)
  - experiments/r18_volatility/phase_b_rescue_per_game.csv  (rescued GE — corrects single-run noise spikes)
  - game_engine/topology.py SUBSTRATE_INVARIANTS + active-cell comments (axis, dim, active cells)
"""
import csv
import json
import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

# Authoritative substrate metadata (axis, dim, active cells) from game_engine/topology.py.
# Listed in Hausdorff-dim order — drives the x-axis of the headline chart.
SUBSTRATES = [
    {"key": "vicsek",   "label": "Vicsek",            "axis": 27, "spatial_dim": 2, "active_cells": 125, "haus_dim": 1.465},
    {"key": "triangle", "label": "Sierpinski tri.",   "axis": 32, "spatial_dim": 2, "active_cells": 243, "haus_dim": 1.585},
    {"key": "carpet",   "label": "Sierpinski carp.",  "axis": 9,  "spatial_dim": 2, "active_cells": 64,  "haus_dim": 1.893},
    {"key": "grid",     "label": "2D grid (control)", "axis": 16, "spatial_dim": 2, "active_cells": 256, "haus_dim": 2.000},
    {"key": "menger",   "label": "Menger",            "axis": 9,  "spatial_dim": 3, "active_cells": 400, "haus_dim": 2.727},
]


def champion_by_stored_ge(db_path):
    """Top-1 game by stored GE (the "stable end-of-run top-1" used in the eval report)."""
    con = sqlite3.connect(db_path)
    row = con.execute(
        "SELECT g.game_id, g.generation, s.go_essence, s.strategic_depth, s.rule_simplicity, "
        "       s.non_triviality, s.strategic_diversity "
        "FROM games g JOIN scores s ON s.game_id = g.game_id "
        "ORDER BY s.go_essence DESC LIMIT 1"
    ).fetchone()
    con.close()
    return {
        "game_id": row[0], "generation": row[1], "stored_ge": row[2],
        "depth": row[3], "simplicity": row[4], "non_triviality": row[5], "diversity": row[6],
    }


def load_csv_index(path, key):
    out = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            out[r[key]] = r
    return out


def load_noise_floor():
    """Per-game (n, mean, std, min, max) of GE across fresh-train reruns."""
    db = REPO / "experiments/r18_noise_floor/r18_noise_floor.db"
    if not db.exists():
        return {}
    con = sqlite3.connect(str(db))
    rows = con.execute(
        "SELECT game_id, go_essence FROM rerun_scores ORDER BY game_id, rerun_idx"
    ).fetchall()
    con.close()
    by_gid = {}
    for gid, ge in rows:
        by_gid.setdefault(gid, []).append(ge)
    out = {}
    for gid, ges in by_gid.items():
        n = len(ges)
        m = sum(ges) / n
        v = sum((g - m) ** 2 for g in ges) / max(n - 1, 1)
        out[gid] = {
            "n": n, "mean": m, "std": v ** 0.5,
            "min": min(ges), "max": max(ges),
        }
    return out


def main():
    phase_a = load_csv_index(REPO / "experiments/r18_volatility/phase_a_per_game.csv", "game_id")
    phase_b = load_csv_index(REPO / "experiments/r18_volatility/phase_b_rescue_per_game.csv", "game_id")
    noise_floor = load_noise_floor()

    rows = []
    for s in SUBSTRATES:
        db = REPO / f"genesis_v2_run18_{s['key']}.db"
        ch = champion_by_stored_ge(db)

        gid = ch["game_id"]
        a = phase_a.get(gid)
        b = phase_b.get(gid)
        nf = noise_floor.get(gid)

        pge_std = float(a["pge_std"]) if a else None
        n_runs_a = int(a["n_runs"]) if a else None
        rescued_ge = float(b["rescued_ge"]) if b else None

        rows.append({
            **s,
            "champion": {
                "game_id": gid,
                "generation": ch["generation"],
                "stored_ge": round(ch["stored_ge"], 4),
                "rescued_ge": round(rescued_ge, 4) if rescued_ge is not None else None,
                "pge_std": round(pge_std, 4) if pge_std is not None else None,
                "n_volatility_runs": n_runs_a,
                "depth": round(ch["depth"], 4),
                # Empirical noise floor — fresh-train n=5, the canonical numbers for the chart.
                "noise_floor": {
                    "n": nf["n"], "mean": round(nf["mean"], 4), "std": round(nf["std"], 4),
                    "min": round(nf["min"], 4), "max": round(nf["max"], 4),
                } if nf else None,
            },
        })

    out = {
        "generated_from": "experiments/{r18_volatility,r18_noise_floor}/* + genesis_v2_run18_*.db",
        "notes": (
            "noise_floor: empirical mean/std from 5 fresh PPO retrains (each at "
            "num_independent_runs=3, training_budget=5000 — matching R18). "
            "These are the canonical numbers; rescued_ge / pge_std are pre-experiment "
            "estimates that the noise-floor pass empirically corrects."
        ),
        "substrates": rows,
    }
    out_path = HERE / "data.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
