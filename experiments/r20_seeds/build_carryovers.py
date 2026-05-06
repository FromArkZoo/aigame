#!/usr/bin/env python3
"""R20 carry-over builder — extract R19 top-1 games + augment with pie_rule.

Per R20_plan.md § Carry-over anchors:

  menger: 1f9191b5d4e6  (R19 top-1, GE 0.3293, human 4.8 — outnumber-2 +
                         influence(r=1) + threshold-race)
          5048f71b62fd  (R19 top-3, human 5.0 — surround variant; the only
                         R19 game where humans rated above GE)
  carpet: ce3a09e05cef  (R19 top-1, GE 0.3547, human 4.4)
  grid_control: SKIP    (R8 carry-over extraction deferred — F1 seed
                         covers G1 methodology check)

Each extracted game has pie_rule=True forced on it, matching R20's
mandatory pie balance. This means head-to-head comparison vs the R20
F1-F4 families is "R19 rule-family running with R20's fixes" — exactly
what R20 G3 measures.

The metadata records the original R19 GE and human-eval mean for
post-evolution leaderboard cross-referencing.

Usage:
    .venv/bin/python experiments/r20_seeds/build_carryovers.py
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from game_engine.factory import create_engine  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402


# Per R20_plan.md § Carry-over anchors. R19 human-eval means from the
# evaluation_report_run19.md § Per-game scores table.
CARRY_OVERS: list[dict] = [
    {
        "substrate": "menger",
        "label": "menger_r19_top1",
        "db": REPO / "genesis_v2_run19_menger.db",
        "game_id": "1f9191b5d4e6",
        "r19_human_mean": 4.8,
        "r19_family": "outnumber-2 + influence(r=1) + threshold-race",
    },
    {
        "substrate": "menger",
        "label": "menger_r19_top3_surround",
        "db": REPO / "genesis_v2_run19_menger.db",
        "game_id": "5048f71b62fd",
        "r19_human_mean": 5.0,
        "r19_family": "surround + influence(r=1) + threshold-race",
    },
    {
        "substrate": "carpet",
        "label": "carpet_r19_top1",
        "db": REPO / "genesis_v2_run19_carpet.db",
        "game_id": "ce3a09e05cef",
        "r19_human_mean": 4.4,
        "r19_family": "outnumber-2 + influence(r=2) + threshold-race",
    },
]


def fetch_game(db_path: Path, game_id: str) -> tuple[GameDefV2, float | None]:
    if not db_path.exists():
        raise SystemExit(f"FATAL: DB not found: {db_path}")
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
    ge = float(row["go_essence"]) if row["go_essence"] is not None else None
    return GameDefV2.from_dict(rep), ge


def main() -> int:
    out_dir = Path(__file__).parent / "carryover"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nBuilding {len(CARRY_OVERS)} R20 carry-overs → {out_dir}\n")

    for entry in CARRY_OVERS:
        game, r19_ge = fetch_game(entry["db"], entry["game_id"])

        # R20 stack: pie_rule mandatory. The R19 games predate S1 so this
        # always flips False -> True; warn if a future R19 re-export
        # already had it.
        if game.pie_rule:
            print(
                f"  NOTE  {entry['label']}: pie_rule already True in source"
            )
        game.pie_rule = True

        # Tag metadata so train_and_evaluate_game skips quick-validation,
        # and the leaderboard can cross-reference back to R19.
        game.metadata = dict(game.metadata or {})
        game.metadata.update({
            "seeded_from": f"R19 {entry['label']}",
            "r19_go_essence": r19_ge,
            "r19_human_mean": entry["r19_human_mean"],
            "r19_family": entry["r19_family"],
            "source": "R20 carry-over (pie_rule augmented)",
            "carryover_label": entry["label"],
        })

        # Sanity: game must construct under R20 (with pie_rule=True the
        # action space gains the swap idx; engine should still build).
        engine = create_engine(game)
        cells = engine.topo.num_active_cells
        assert game.swap_action_idx == game.num_actions - 1, (
            f"{entry['label']}: swap_action_idx mismatch after pie augmentation"
        )

        out_path = out_dir / f"{entry['label']}.json"
        with open(out_path, "w") as f:
            json.dump(game.to_dict(), f, indent=2)

        print(
            f"  OK  {entry['label']:<32s}  game_id={game.game_id}  "
            f"R19 GE={r19_ge:.4f}  human={entry['r19_human_mean']}  "
            f"cells={cells}  swap_idx={game.swap_action_idx}"
        )
        print(
            f"        family: {entry['r19_family']}"
        )
        print(
            f"        -> {out_path.relative_to(REPO)}"
        )

    # Convenience symlinks for the launch script's CARRY_OVER_DIR pattern:
    # the launcher looks for <substrate>.json. Default to top-1 per substrate.
    # Multiple-anchor carry-overs (menger has 2) are accessible by label.
    for sub_default in [
        ("menger", "menger_r19_top1.json"),
        ("carpet", "carpet_r19_top1.json"),
    ]:
        sub, fname = sub_default
        target = out_dir / fname
        link = out_dir / f"{sub}.json"
        if link.exists() or link.is_symlink():
            link.unlink()
        link.symlink_to(fname)
        print(f"  symlink {sub}.json -> {fname}")

    print(f"\n=== {len(CARRY_OVERS)} carry-overs written ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
