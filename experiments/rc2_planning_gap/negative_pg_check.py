"""Post-verdict mechanism inspection for the negative planning gaps.

Non-binding addendum (collapse_check.py precedent). The calibration bar
PASSED; this asks WHY deep UCT loses to shallow UCT on S4 (-0.323) and
e1453 (-0.229), since more search should not hurt under a healthy signal.

Two probes per game (S4, e1453 negative; d4015 healthy contrast):
  1. dvs  — replay 4 deep-vs-shallow games with action logging: per-side
            pass shares and game length. Hypothesis: deep search converges
            on pass-heavy lines that score well against the random-rollout
            leaf model but lose to a live opponent — the pass-collapse
            attractor in search form.
  2. vsr  — UCT@256 and UCT@16 vs RandomAgent, n=8 seat-balanced each:
            is deep search objectively weak on these games, or only
            non-transitively weak vs shallow?

Run: .venv/bin/python experiments/rc2_planning_gap/negative_pg_check.py
"""
from __future__ import annotations

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
from training.utils import RandomAgent, play_game  # noqa: E402
from experiments.rc2_descriptor_v2.run_probe import load_roster_game  # noqa: E402
from experiments.rc2_planning_gap.anchor_calibration import (  # noqa: E402
    DEEP_SIMS,
    MAX_STEPS,
    SHALLOW_SIMS,
    UCTAgent,
    WORKERS,
)

HERE = Path(__file__).resolve().parent
OUT = HERE / "negative_pg_check.json"

GAMES = ("S4", "e1453dac5445", "d4015a646ae3")
DVS_N = 4
VSR_N = 8


def dvs_logged(key: str, idx: int) -> dict:
    """One deep-vs-shallow game with per-side action logging."""
    game = load_roster_game(key)
    engine = create_engine(game)
    deep = UCTAgent(engine, DEEP_SIMS, 5000 + idx)
    shallow = UCTAgent(engine, SHALLOW_SIMS, 6000 + idx)
    deep_seat = 0 if idx < DVS_N // 2 else 1
    agents = (deep, shallow) if deep_seat == 0 else (shallow, deep)

    obs = engine.reset()
    moves = {0: 0, 1: 0}
    passes = {0: 0, 1: 0}
    steps = 0
    winner = None
    while not engine.done and steps < MAX_STEPS:
        player = engine.get_current_player()
        legal = engine.get_legal_actions()
        if not legal:
            break
        action, _, _ = agents[player].select_action(obs, legal_actions=legal,
                                                    deterministic=True)
        if game.decode_action(int(action))["type"] == "pass":
            passes[player] += 1
        moves[player] += 1
        obs, _, _, info = engine.step(action)
        steps += 1
        winner = info.get("winner")  # 0/1/None per engine_v2._info
    deep_p, shal_p = deep_seat, 1 - deep_seat
    return dict(probe="dvs", key=key, idx=idx, deep_seat=deep_seat,
                winner=winner, length=steps,
                deep_pass_share=passes[deep_p] / max(moves[deep_p], 1),
                shallow_pass_share=passes[shal_p] / max(moves[shal_p], 1),
                deep_won=(winner == deep_seat))


def vsr(key: str, sims: int, idx: int) -> dict:
    """One UCT@sims vs RandomAgent game, seat-balanced by idx."""
    game = load_roster_game(key)
    engine = create_engine(game)
    uct = UCTAgent(engine, sims, 7000 + sims * 37 + idx)
    opp = RandomAgent(seed=8000 + idx)
    uct_seat = 0 if idx < VSR_N // 2 else 1
    agents = (uct, opp) if uct_seat == 0 else (opp, uct)
    winner, length, _ = play_game(engine, agents[0], agents[1],
                                  deterministic=True, max_steps=MAX_STEPS)
    score = 0.5 if winner is None else float(winner == uct_seat)
    return dict(probe="vsr", key=key, sims=sims, idx=idx, score=score,
                length=length)


def main() -> None:
    t0 = time.time()
    tasks = []
    for key in GAMES:
        tasks += [("dvs", key, i) for i in range(DVS_N)]
        tasks += [("vsr", key, s, i) for s in (DEEP_SIMS, SHALLOW_SIMS)
                  for i in range(VSR_N)]
    rows = []
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futs = [pool.submit(dvs_logged, *t[1:]) if t[0] == "dvs"
                else pool.submit(vsr, *t[1:]) for t in tasks]
        for fut in as_completed(futs):
            rows.append(fut.result())
            print(f"  {len(rows)}/{len(tasks)} ({time.time()-t0:.0f}s)",
                  flush=True)

    summary = {}
    for key in GAMES:
        dvs_rows = [r for r in rows if r["probe"] == "dvs" and r["key"] == key]
        out = dict(
            deep_pass_share=float(np.mean([r["deep_pass_share"]
                                           for r in dvs_rows])),
            shallow_pass_share=float(np.mean([r["shallow_pass_share"]
                                              for r in dvs_rows])),
            dvs_deep_wins=sum(r["deep_won"] for r in dvs_rows),
            dvs_n=len(dvs_rows),
        )
        for sims in (DEEP_SIMS, SHALLOW_SIMS):
            ss = [r["score"] for r in rows
                  if r["probe"] == "vsr" and r["key"] == key
                  and r["sims"] == sims]
            out[f"vs_random@{sims}"] = float(np.mean(ss))
        summary[key] = out
        print(f"{key}: deep pass {out['deep_pass_share']:.2f} vs shallow "
              f"pass {out['shallow_pass_share']:.2f} | vs-random "
              f"@{DEEP_SIMS} {out[f'vs_random@{DEEP_SIMS}']:.3f} "
              f"@{SHALLOW_SIMS} {out[f'vs_random@{SHALLOW_SIMS}']:.3f}",
              flush=True)

    OUT.write_text(json.dumps(dict(summary=summary, rows=rows,
                                   elapsed_s=round(time.time() - t0, 1)),
                              indent=2))
    print(f"wrote {OUT.name} in {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
