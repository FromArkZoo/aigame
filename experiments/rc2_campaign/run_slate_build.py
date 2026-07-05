"""Slate-build orchestrator step (README_BUILD run order #5).

On SLATE_PENDING — reached 2026-07-05 via the BAR H v2 reanalysis
(REANALYSIS_BARH_V2.md, BUILD_LOG #15) — compose the §7 slate from the
terminal checkpoint's M archive and write the --slate-json input for
build_blind_pack.py. Prints the substitution log (§7: every substitution
reported) and the family composition; refuses non-terminal checkpoints.

Usage:
  .venv/bin/python experiments/rc2_campaign/run_slate_build.py \
      [--out slate_entries.json]
Then:
  .venv/bin/python experiments/rc2_campaign/build_blind_pack.py \
      --seed <sealed> --slate-json experiments/rc2_campaign/slate_entries.json \
      --out-dir evaluations/rc2_campaign_blind
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from experiments.rc2_campaign.campaign_archive import CampaignArchive  # noqa: E402
from experiments.rc2_campaign.slate import build_slate, slate_to_pack_entries  # noqa: E402
from experiments.rc2_descriptor_v2.run_probe import load_roster_game  # noqa: E402

HERE = Path(__file__).resolve().parent


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--out", default=str(HERE / "slate_entries.json"))
    args = p.parse_args()

    ck = json.loads((HERE / "checkpoint.json").read_text())
    if ck.get("stage") != "terminal":
        print(f"refusing: checkpoint stage {ck.get('stage')!r} != 'terminal'")
        return 2

    arch_m = CampaignArchive.from_dict(ck["archives"]["M"], GameDefV2.from_dict)
    d4015 = {"game": load_roster_game("d4015a646ae3"), "label": "d4015a646ae3"}
    s3 = {"game": load_roster_game("S3"), "label": "S3"}

    result = build_slate(arch_m.cells.values(), d4015, s3)
    entries = slate_to_pack_entries(result, fixture_meta={
        "validity_anchor": {"game_id": "d4015a646ae3",
                            "source": "rc2_descriptor_v2 roster (§7 validity anchor)"},
        "carry_in": {"game_id": "S3",
                     "source": "rc2_descriptor_v2 roster (§7 registered carry-in; "
                               "reported, not binding)"},
    })
    Path(args.out).write_text(json.dumps(entries, indent=1))

    print(f"slate written: {args.out} ({len(entries)} entries)")
    print(f"family composition (top-3): {result['family_composition']}")
    for g in result["games"]:
        pg = g["full_conv_mean_floored"]
        pg_s = "fixture" if pg is None else f"{pg:.4f}"
        print(f"  {g['role']:16s} {str(g['canon'])[:12]:12s} "
              f"family={g['family']} full_conv={pg_s}")
    print("substitution log (§7, every substitution reported):")
    for s in result["substitutions"] or ["  (none)"]:
        print(f"  {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
