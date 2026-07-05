"""BAR H v2 reanalysis of the concluded RC2 campaign (BUILD_LOG #15).

Registered by PREREGISTRATION_BARH_V2.md (ratified 2026-07-05). Re-runs the
§9 pre-slate chain over the TERMINAL checkpoint's final archives with the
v2 saturation-contingency semantics. Per the spec's §0 firewall the output
is routing-only: the verdict is tagged BARH-V2-REANALYSIS everywhere it is
written, and a PASS routes to the §7 slate (blind, fresh, bars untouched)
— it is not evidence of search value by itself.

Runs no simulations, mutates no run artifacts; reads checkpoint.json and
cal_i.json, writes REANALYSIS_BARH_V2.md. Refuses non-terminal checkpoints
(a live campaign's bars are the runner's job, not this script's).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from experiments.rc2_campaign import bars as B  # noqa: E402
from experiments.rc2_campaign.campaign_archive import CampaignArchive  # noqa: E402
from experiments.rc2_campaign.run_campaign import (  # noqa: E402
    bar_h_inputs,
    pre_slate_token,
)

HERE = Path(__file__).resolve().parent
TAG = "BARH-V2-REANALYSIS"


def main() -> int:
    ck = json.loads((HERE / "checkpoint.json").read_text())
    if ck.get("stage") != "terminal":
        print(f"refusing: checkpoint stage {ck.get('stage')!r} != 'terminal'")
        return 2
    cal_i = json.loads((HERE / "cal_i.json").read_text())
    cal_i_pass = cal_i["verdict"] == "PASS"

    arch_r = CampaignArchive.from_dict(ck["archives"]["R"], GameDefV2.from_dict)
    arch_m = CampaignArchive.from_dict(ck["archives"]["M"], GameDefV2.from_dict)
    inputs = bar_h_inputs(arch_r, arch_m)
    res = B.bar_h(inputs["top10_m"], inputs["top10_r"],
                  inputs["m_rated"], inputs["r_rated"],
                  contested_cells=inputs["contested_wins"])
    token = pre_slate_token(
        cal_i_pass=cal_i_pass,
        incomplete=ck["incomplete"],
        bar_w_verdict=ck["bar_w_result"]["verdict"],
        bar_h_verdict=res["verdict"],
    )

    m_wins = sum(inputs["contested_wins"])
    lines = [
        f"# RC2 campaign — BAR H v2 reanalysis [{TAG}]",
        "",
        "Registered by `PREREGISTRATION_BARH_V2.md` (ratified 2026-07-05, "
        "BUILD_LOG #15). POST-DATA re-registration — routing-only per its §0 "
        "firewall: a PASS routes to the §7 slate; it is NOT evidence of "
        "search value. v1 artifact `campaign_results.md` (PROBE_INCOMPLETE) "
        "stands as the registered v1 record.",
        "",
        f"Inputs: terminal checkpoint (bar mode {ck['bar_mode']}, "
        f"B_effective={ck['b_effective']}, elapsed "
        f"{ck['elapsed'] / 3600:.2f}h), cal_i.json verdict "
        f"{cal_i['verdict']}, BAR W {ck['bar_w_result']['verdict']} "
        "(Stage-0 close, unchanged).",
        "",
        "## BAR H-PG v2 (saturation metric: contested-cell record)",
        "",
        f"- R_top10 {inputs['top10_r']:.4f} >= 0.40 -> saturation switch "
        "fires (unchanged from v1)",
        f"- jointly filled cells: {inputs['joint_n']}; same-canon shared-init "
        f"residue EXCLUDED: {inputs['same_elite_ties']}; contested: "
        f"{inputs['contested_n']}",
        f"- M strict wins {m_wins}/{inputs['contested_n']} = "
        f"{m_wins / inputs['contested_n']:.3f} vs bar 0.60, "
        f"min contested {B.SATURATION_MIN_JOINT}",
        f"- bar_h: {res['metric']} {res['detail']} -> **{res['verdict']}**",
        "",
        f"## Chain token [{TAG}]",
        "",
        f"PRE-SLATE TOKEN: **{token}** [{TAG}]",
        "",
        "Registered consequence of SLATE_PENDING (spec §4): §7 slate runs "
        "manually on these archives, composition and bars unchanged. "
        "Disclosed pre-ratification: expected S-GO-2 minimum-contrast gap "
        "~0.052 < 0.15 -> SEPARATION_UNDERDETERMINED -> maximum slate "
        "outcome GO-PARTIAL, contingent on S-GO-1 and d4015 in [3.48, 4.18].",
        "",
    ]
    (HERE / "REANALYSIS_BARH_V2.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
