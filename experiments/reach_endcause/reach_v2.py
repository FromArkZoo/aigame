"""REACH-v2 — end-CAUSE redesign of the REACH guard (descriptor-v2 binding input (b)).

The original G-REACH ("fires iff < 20% of tactical rollouts end decisively
BEFORE max_turns") FAILED its bar: S2 is 100% decisive under tactical play,
but by custodian-capture attrition — the threshold the blind teams called
unreachable ("threshold 36.9 unreachable; peaks ~+10") is indeed never
crossed. The rc2_descriptor_v2 verdict required the redesign to key on
end-CAUSE (decided BY the win condition vs by attrition/timeout), not
end-RATE. Protocol committed before the run; bars applied verbatim.

Mechanism (engine ground truth)
-------------------------------
GameEngineV2 sets an explicit flag for every NON-win-condition end:
_ended_by_max_turns, _ended_by_no_moves, _ended_by_double_pass,
_ended_by_score_margin. The win-condition check itself (_check_threshold
for this family) ends the game with NO flag set. Therefore:

  end_via_win_condition := engine.done AND no _ended_by_* flag set

(A both-players-cross FP-tied draw counts as a win-condition end — the
threshold was reached; that is what REACH asks.) Rollouts that hit the
2*max_game_steps hard cap without engine.done are timeouts.

Guard (pre-committed)
---------------------
  REACH-v2 (threshold-family only): fires iff
      wc_share = share of tactical rollouts ending via win condition < 0.20
  Rollouts: TacticalAgent-vs-TacticalAgent, n=100/game as 50 mirrored seed
  pairs, the descriptor-v2 convention verbatim (pair_seeds scheme,
  hard cap 2*max_game_steps).

PASS bars (binding — mirrors the original G-REACH bar wording)
--------------------------------------------------------------
  B1: REACH-v2 FIRES on S2 (the motivating game).
  B2: REACH-v2 does NOT fire on e1453dac5445.
  Other threshold-family roster games reported, not binding.

Diagnostics: v1 end-rate share alongside v2 wc_share per game (the S2 row
should show the mechanism: ~1.00 decisive vs ~0.00 via threshold), end-cause
breakdown, mean plies.

Output: reach_v2.json + REACH_V2.md next to this file.
Run:    .venv/bin/python experiments/reach_endcause/reach_v2.py [--workers N]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game_engine.factory import create_engine  # noqa: E402
from metrics.tactical_agent import TacticalAgent  # noqa: E402
from experiments.rc2_descriptor_v2.run_probe import (  # noqa: E402
    ROSTER,
    load_roster_game,
    pair_seeds,
)

HERE = Path(__file__).resolve().parent
OUT_JSON = HERE / "reach_v2.json"
OUT_MD = HERE / "REACH_V2.md"

N_PAIRS = 50            # 100 rollouts/game, descriptor-v2 convention
REACH_SHARE = 0.20      # retained verbatim from v1
END_FLAGS = ("_ended_by_max_turns", "_ended_by_no_moves",
             "_ended_by_double_pass", "_ended_by_score_margin")


def rollout_endcause(game, seed_p1: int, seed_p2: int) -> dict:
    """One tactical-vs-tactical rollout, recording the end cause.

    Loop shape mirrors rc2_descriptor_v2.run_probe.rollout_tactical
    (deterministic given seeds); only the end-state capture differs.
    """
    engine = create_engine(game)
    obs = engine.reset()
    agents = [
        TacticalAgent(engine, player_num=1, seed=seed_p1),
        TacticalAgent(engine, player_num=2, seed=seed_p2),
    ]
    hard_cap = 2 * engine.game.max_game_steps
    plies = 0
    while not engine.done and engine.step_count < hard_cap:
        legal = engine.get_legal_actions()
        agent = agents[engine.get_current_player()]
        action, _, _ = agent.select_action(obs, legal_actions=legal,
                                           deterministic=False)
        obs, _, _, _ = engine.step(action)
        plies += 1
    flags = {f: bool(getattr(engine, f)) for f in END_FLAGS}
    timeout = not engine.done
    via_wc = engine.done and not any(flags.values())
    winner = engine._winner  # 1-based or None
    decisive_pre_max = winner is not None and not flags["_ended_by_max_turns"] \
        and not timeout
    return dict(plies=plies, timeout=timeout, winner=winner,
                via_win_condition=via_wc, decisive_pre_max=decisive_pre_max,
                flags=flags)


def measure(key: str) -> dict:
    game = load_roster_game(key)
    t0 = time.time()
    records = []
    for i in range(N_PAIRS):
        (a, b), (c, d) = pair_seeds(i)
        records.append(rollout_endcause(game, a, b))
        records.append(rollout_endcause(game, c, d))
    n = len(records)
    wc_share = sum(r["via_win_condition"] for r in records) / n
    v1_share = sum(r["decisive_pre_max"] for r in records) / n
    causes = dict(
        win_condition=sum(r["via_win_condition"] for r in records),
        max_turns=sum(r["flags"]["_ended_by_max_turns"] for r in records),
        no_moves=sum(r["flags"]["_ended_by_no_moves"] for r in records),
        double_pass=sum(r["flags"]["_ended_by_double_pass"] for r in records),
        score_margin=sum(r["flags"]["_ended_by_score_margin"] for r in records),
        timeout=sum(r["timeout"] for r in records),
    )
    return dict(
        key=key,
        blind_mean=ROSTER[key].get("blind_mean"),
        n=n,
        wc_share=wc_share,
        fires=wc_share < REACH_SHARE,
        v1_decisive_share=v1_share,
        causes=causes,
        mean_plies=float(np.mean([r["plies"] for r in records])),
        elapsed_s=round(time.time() - t0, 1),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()

    keys = [k for k in ROSTER if ROSTER[k]["family"] == "threshold"]
    assert "S2" in keys and "e1453dac5445" in keys
    t0 = time.time()
    results: dict[str, dict] = {}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(measure, k): k for k in keys}
        for fut in as_completed(futs):
            r = fut.result()
            results[r["key"]] = r
            print(f"  {r['key']}: wc_share {r['wc_share']:.2f} "
                  f"(v1 {r['v1_decisive_share']:.2f}) "
                  f"fires={r['fires']} ({r['elapsed_s']}s)", flush=True)

    b1 = results["S2"]["fires"]
    b2 = not results["e1453dac5445"]["fires"]
    verdict = "PASS" if (b1 and b2) else "FAIL"
    detail = (f"B1 fires-on-S2: {'PASS' if b1 else 'FAIL'} "
              f"(wc_share {results['S2']['wc_share']:.2f}); "
              f"B2 silent-on-e1453: {'PASS' if b2 else 'FAIL'} "
              f"(wc_share {results['e1453dac5445']['wc_share']:.2f})")

    state = dict(
        protocol=dict(n_pairs=N_PAIRS, reach_share=REACH_SHARE,
                      definition="fires iff share of tactical rollouts "
                                 "ending via win condition < 0.20",
                      bars="B1 fires on S2; B2 silent on e1453; others "
                           "reported, not binding"),
        results=results,
        verdict=verdict,
        verdict_detail=detail,
        elapsed_s=round(time.time() - t0, 1),
    )
    OUT_JSON.write_text(json.dumps(state, indent=2))

    lines = [
        "# REACH-v2 — end-cause guard redesign", "",
        "Descriptor-v2 binding input (b): REACH redesigned on end-CAUSE "
        "(decided BY the win condition vs by attrition/timeout). Protocol "
        "pre-committed in `reach_v2.py`; bars mirror the original G-REACH "
        "wording verbatim (fires on S2; silent on e1453; other threshold "
        "games reported, not binding). Tactical rollouts: descriptor-v2 "
        "convention (100/game, 50 mirrored seed pairs).", "",
        "| game | blind mean | wc_share (v2) | v1 decisive share | fires "
        "| end causes (wc/maxT/noMv/dblP/margin/timeout) | mean plies |",
        "|---|---:|---:|---:|---|---|---:|",
    ]
    order = ["S2", "e1453dac5445"] + sorted(
        k for k in results if k not in ("S2", "e1453dac5445"))
    for k in order:
        r = results[k]
        c = r["causes"]
        lines.append(
            f"| {k}{' (binding)' if k in ('S2', 'e1453dac5445') else ''} "
            f"| {r['blind_mean']} | **{r['wc_share']:.2f}** "
            f"| {r['v1_decisive_share']:.2f} "
            f"| {'FIRES' if r['fires'] else '—'} "
            f"| {c['win_condition']}/{c['max_turns']}/{c['no_moves']}"
            f"/{c['double_pass']}/{c['score_margin']}/{c['timeout']} "
            f"| {r['mean_plies']:.1f} |")
    lines += ["", f"## Verdict: **{verdict}**", "", detail, "",
              f"Wall time: {state['elapsed_s']}s. COMPLETE", ""]
    OUT_MD.write_text("\n".join(lines))
    print(f"\nVERDICT: {verdict} — {detail}")
    print(f"wrote {OUT_JSON.name}, {OUT_MD.name} in {state['elapsed_s']}s",
          flush=True)


if __name__ == "__main__":
    main()
