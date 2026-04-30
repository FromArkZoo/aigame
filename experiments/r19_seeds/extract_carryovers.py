#!/usr/bin/env python3
"""Extract R18 winners as gen-0 carry-over seeds for R19.

Per R19 plan v3 "Seed design" — inject the R18 stable champions into
gen-0 so evolution starts at the known peak rather than below it.

  menger: 0f5e931fa3e1  (R18 stable top, GE 0.3368, custodian-2 + inf r=1 + threshold)
  carpet: 8776b2026957  (R18 stable top, GE 0.1633 raw / 0.3465 Phase B rescued,
                         outnumber-2 + inf r=2 + threshold)

The R18 game records store the full GameDefV2 dict in
games.rule_representation. We pull that out and write it to
experiments/r19_seeds/carryover/<substrate>.json.

The metadata gets a ``seeded_from`` flag so train_and_evaluate_game's
quick-validation pass is skipped (run.py:236 — same path R18 used for
its own seeded games).

Usage:
    .venv/bin/python experiments/r19_seeds/extract_carryovers.py
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from game_engine.factory import create_engine  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402


REPO = Path(__file__).resolve().parents[2]

CARRY_OVERS = [
    {
        "substrate": "menger",
        "db": REPO / "genesis_v2_run18_menger.db",
        "game_id": "0f5e931fa3e1",
    },
    {
        "substrate": "carpet",
        "db": REPO / "genesis_v2_run18_carpet.db",
        "game_id": "8776b2026957",
    },
]


def fetch_game(db_path: Path, game_id: str) -> tuple[GameDefV2, float]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT g.rule_representation, s.go_essence "
        "FROM games g LEFT JOIN scores s USING(game_id) "
        "WHERE g.game_id = ?",
        (game_id,),
    ).fetchone()
    conn.close()
    if row is None:
        raise SystemExit(f"FATAL: game_id={game_id} not found in {db_path}")
    rep = json.loads(row["rule_representation"])
    return GameDefV2.from_dict(rep), float(row["go_essence"] or 0.0)


def main() -> int:
    out_dir = Path(__file__).parent / "carryover"
    out_dir.mkdir(parents=True, exist_ok=True)

    for entry in CARRY_OVERS:
        game, ge = fetch_game(entry["db"], entry["game_id"])

        # Tag so quick-validation in train_and_evaluate_game skips this game.
        game.metadata = dict(game.metadata or {})
        game.metadata["seeded_from"] = f"R18 {entry['substrate']} stable top"
        game.metadata["r18_go_essence"] = ge
        game.metadata["source"] = "R19 carry-over from R18 DB"

        # Sanity: game must construct without error
        engine = create_engine(game)
        cells = engine.topo.num_active_cells

        out_path = out_dir / f"{entry['substrate']}.json"
        with open(out_path, "w") as f:
            json.dump(game.to_dict(), f, indent=2)

        print(
            f"  OK  {entry['substrate']:<8s}  game_id={game.game_id}  "
            f"R18 GE={ge:.4f}  cells={cells}  -> {out_path.relative_to(REPO)}"
        )

    print(f"\n=== {len(CARRY_OVERS)} carry-overs written ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
