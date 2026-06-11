"""FRONTLINE campaign — arm configs + Stage-0b smoke (pre-registered).

Builds the F arm E x M grid (6 variants: E in {0.75, 1.00, 1.25} x
M_end in {8, 12}), copies the three probe-calibrated comparators
(s_flip_r2 from SIEGE, a1_field_connect / a0_baseline from fc_phase15),
then runs the prereg-pinned Stage-0b smoke on the pinned cell
(E=1.00, M=8, komi 0, seed 7):

  1000 random rollouts (seed-7 master rng, fresh RandomAgent pair/episode)
   200 ChainBuilder(P1, axis=0) vs ChainBuilder(P2, axis=1)
   200 MutualPacker(P1)        vs MutualPacker(P2)
   200 ChainBuilder(P1, axis=0) vs MirrorAgent(P2)
   200 ChainBuilder(P1, axis=0) vs PassBot(P2)

KILL gates (pre-registered, asserted in this order):
  KILL-0b1 (build-regression): max(random, chain) flips/game >= 1.0
  KILL-0b2 (packing-scores-zero): mutual-packer mean total score <= 2.0
  KILL-0b3 (design-model validation): random engaged_share at
           min(ply 80, final ply) inside (0.01, 0.60)
MIRROR CONTINGENCY (decision, never an assert): mirror secures >= draw
in >= 30% of games vs front-builder -> print loudly, owner decides W=21.

Usage:
    .venv/bin/python experiments/frontline/build_games.py
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from game_engine.factory import create_engine  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from game_engine.rules import (  # noqa: E402
    ActionRule,
    CaptureRule,
    PlacementRule,
    PropagationRule,
    TurnStructure,
    WinCondition,
)
from training.utils import RandomAgent  # noqa: E402
from experiments.frontline.scripted_agents import (  # noqa: E402
    ChainBuilder,
    MirrorAgent,
    MutualPacker,
    PassBot,
)

HERE = Path(__file__).resolve().parent
GAMES_DIR = HERE / "games"
SIEGE_CAL = ROOT / "experiments" / "siege" / "games" / "calibrated"
FC15_CAL = ROOT / "experiments" / "fc_phase15" / "games" / "calibrated"
MEMO = HERE / "STAGE0_MEMO.md"

W = 22  # hex_rhombus board width (prereg: W=22; W=21 only via mirror contingency)

# -----------------------------------------------------------------------
# COMMON base — mirrors siege COMMON but with pie_rule=True
# (prereg §Arms: pie ON, komi_cells 0 first; ladder is Stage 1's job)
# -----------------------------------------------------------------------
COMMON = dict(
    num_dimensions=2,
    axis_size=W,
    topology_type="hex_rhombus",
    turn_structure=TurnStructure(turn_type="alternating"),
    action_rule=ActionRule(action_types=("place",)),
    placement_rule=PlacementRule(target="empty", constraint="anywhere"),
    pie_rule=True,  # prereg: pie ON, komi 0 first
)
FIELD = dict(prop_type="influence", radius=2, strength=1.0, decay=0.5)
GRID_E = (0.75, 1.00, 1.25)
GRID_M = (8, 12)
SMOKE = dict(E=1.00, M=8, komi=0, seed=7)  # prereg-pinned

N_RANDOM = 1000
N_SCRIPTED = 200


def build_f(e: float, m: int) -> GameDefV2:
    """Build one F-arm FRONTLINE game (contested_majority on the flip substrate)."""
    return GameDefV2(
        game_id=f"f_frontline_E{e:.2f}_M{m}".replace(".", "p"),
        capture_rule=CaptureRule(capture_type="field_flip"),
        propagation_rule=PropagationRule(**FIELD),
        win_condition=WinCondition(
            condition_type="contested_majority",
            engage_threshold=e,
            end_margin=m,
            min_turns_score_end=20,
            komi_cells=0,
            control_margin=0.0,
            max_turns=200,
        ),
        **COMMON,
    )


# -----------------------------------------------------------------------
# Stage-0b smoke helpers
# -----------------------------------------------------------------------

def _run_rollout(engine, agents: list) -> dict:
    """Run one episode; record flips (board-diff), contested-score
    trajectory, mover-signed margin swing per flip-ply, end cause."""
    obs = engine.reset()
    board = engine.board_owners
    num_active = len(engine.topo.active_cells)

    flips = 0
    flip_swings: list[int] = []  # mover-signed Delta(s_mover - s_opp) per flip-ply
    engaged_traj: list[float] = []  # engaged_frac per recorded (non-pie) ply
    prev_s1, prev_s2, _ = engine.contested_scores()  # (0, 0, 0) at reset

    while not engine.done:
        player_idx = engine.get_current_player()  # 0-indexed
        agent = agents[player_idx]
        legal = engine.get_legal_actions()

        # Snapshot board_owners before step for flip detection (siege pattern)
        prev_owners = board.copy()

        action, _, _ = agent.select_action(obs, legal_actions=legal, deterministic=False)
        obs, _, done, info = engine.step(action)

        s1, s2, engaged = engine.contested_scores()

        # Skip pie-swap steps for flip/trajectory accounting (no placement;
        # ownership recolouring is the swap itself, not a field flip)
        if info.get("pie_swap"):
            prev_s1, prev_s2 = s1, s2
            continue

        # Detect flips: cells that changed owner enemy -> mover across the ply
        mover_owner = player_idx + 1  # 1 or 2
        enemy_owner = 3 - mover_owner
        ply_flips = int(np.count_nonzero(
            (prev_owners == enemy_owner) & (board == mover_owner)))
        if ply_flips:
            flips += ply_flips
            if mover_owner == 1:
                swing = (s1 - s2) - (prev_s1 - prev_s2)
            else:
                swing = (s2 - s1) - (prev_s2 - prev_s1)
            flip_swings.append(swing)

        engaged_traj.append(engaged / num_active)
        prev_s1, prev_s2 = s1, s2

    # End cause via the three flags (+ "other" fallback)
    if engine._ended_by_score_margin:
        end_cause = "score_margin"
    elif engine._ended_by_double_pass:
        end_cause = "double_pass"
    elif engine._ended_by_max_turns:
        end_cause = "timeout"
    else:
        end_cause = "other"

    final_s1, final_s2, final_engaged = engine.contested_scores()

    def _at(ply: int) -> float:
        if not engaged_traj:
            return 0.0
        return engaged_traj[min(ply, len(engaged_traj)) - 1]

    return dict(
        flips=flips,
        flip_swings=flip_swings,
        end_cause=end_cause,
        s1=final_s1,
        s2=final_s2,
        engaged_final=final_engaged / num_active,
        engaged_at_20=_at(20),
        engaged_at_40=_at(40),
        engaged_at_80=_at(80),  # engaged_frac at ply min(80, final)
        length=engine.step_count,
        winner=engine._winner,  # 1, 2, or None
    )


END_CAUSES = ("score_margin", "double_pass", "timeout", "other")


def _aggregate(results: list[dict]) -> dict:
    n = len(results)
    all_swings = [s for r in results for s in r["flip_swings"]]
    out = dict(
        n=n,
        flips_per_game=float(np.mean([r["flips"] for r in results])),
        mean_len=float(np.mean([r["length"] for r in results])),
        mean_s1=float(np.mean([r["s1"] for r in results])),
        mean_s2=float(np.mean([r["s2"] for r in results])),
        mean_total_score=float(np.mean([r["s1"] + r["s2"] for r in results])),
        engaged_at_20=float(np.mean([r["engaged_at_20"] for r in results])),
        engaged_at_40=float(np.mean([r["engaged_at_40"] for r in results])),
        engaged_at_80=float(np.mean([r["engaged_at_80"] for r in results])),
        engaged_final=float(np.mean([r["engaged_final"] for r in results])),
        mean_flip_swing=(float(np.mean(all_swings)) if all_swings else float("nan")),
        n_flip_plies=len(all_swings),
        p1_win_share=sum(r["winner"] == 1 for r in results) / n,
        p2_win_share=sum(r["winner"] == 2 for r in results) / n,
        draw_share=sum(r["winner"] is None for r in results) / n,
    )
    for cause in END_CAUSES:
        out[f"{cause}_share"] = sum(r["end_cause"] == cause for r in results) / n
    # Mirror probe stat (mirror seats P2): draw-or-win share for P2
    out["mirror_draw_or_win_share"] = out["p2_win_share"] + out["draw_share"]
    return out


def _run_matchup(engine, n_games: int, make_agents, label: str) -> dict:
    t0 = time.time()
    results = []
    for _ in range(n_games):
        agents = make_agents()
        for a in agents:
            if hasattr(a, "bind"):
                a.bind(engine)
        results.append(_run_rollout(engine, agents))
    agg = _aggregate(results)
    agg["runtime_s"] = time.time() - t0
    agg["label"] = label
    return agg


def _fmt_row(agg: dict) -> str:
    return (
        f"{agg['label']:<18} {agg['n']:>5} {agg['flips_per_game']:>8.3f} "
        f"{agg['mean_len']:>7.1f} "
        f"{100 * agg['score_margin_share']:>8.1f} {100 * agg['double_pass_share']:>8.1f} "
        f"{100 * agg['timeout_share']:>8.1f} {100 * agg['other_share']:>6.1f} "
        f"{agg['mean_s1']:>7.2f} {agg['mean_s2']:>7.2f} "
        f"{agg['engaged_at_80']:>8.3f} {agg['engaged_final']:>8.3f} "
        f"{100 * agg['p1_win_share']:>6.1f} {100 * agg['p2_win_share']:>6.1f} "
        f"{100 * agg['draw_share']:>6.1f}"
    )


HEADER = (
    f"{'matchup':<18} {'n':>5} {'flips/g':>8} {'len':>7} "
    f"{'scrmrg%':>8} {'dblpas%':>8} {'timeout%':>8} {'oth%':>6} "
    f"{'s1':>7} {'s2':>7} {'eng@80':>8} {'engEnd':>8} "
    f"{'P1w%':>6} {'P2w%':>6} {'drw%':>6}"
)


def smoke(game: GameDefV2) -> dict:
    """Run the prereg-pinned Stage-0b smoke on the pinned F cell."""
    engine = create_engine(game)
    aggs: dict[str, dict] = {}

    # ---- 1000 random rollouts (seed=7 master rng; siege pattern verbatim) ----
    rng = np.random.default_rng(SMOKE["seed"])

    def make_random():
        # Fresh RandomAgent pair per episode, seeded from the master rng for
        # independence + reproducibility
        return [
            RandomAgent(seed=int(rng.integers(0, 2**31))),
            RandomAgent(seed=int(rng.integers(0, 2**31))),
        ]

    aggs["random"] = _run_matchup(engine, N_RANDOM, make_random, "random")
    print(f"random done in {aggs['random']['runtime_s']:.1f}s")

    # ---- Scripted matchups (fresh instances bound per episode) ----
    scripted = [
        ("chain_vs_chain",
         lambda: [ChainBuilder(player=1, axis=0), ChainBuilder(player=2, axis=1)]),
        ("packer_vs_packer",
         lambda: [MutualPacker(player=1), MutualPacker(player=2)]),
        ("chain_vs_mirror",
         lambda: [ChainBuilder(player=1, axis=0), MirrorAgent(player=2)]),
        ("chain_vs_passbot",
         lambda: [ChainBuilder(player=1, axis=0), PassBot(player=2)]),
    ]
    for label, maker in scripted:
        aggs[label] = _run_matchup(engine, N_SCRIPTED, maker, label)
        print(f"{label} done in {aggs[label]['runtime_s']:.1f}s "
              f"(deterministic pairing: {N_SCRIPTED} identical games)")

    # ---- Print summary table ----
    print(f"\n{'=' * len(HEADER)}")
    print(f"STAGE-0b SMOKE — {game.game_id} (pinned: E={SMOKE['E']:.2f}, "
          f"M={SMOKE['M']}, komi={SMOKE['komi']}, seed={SMOKE['seed']})")
    print(f"{'=' * len(HEADER)}")
    print(HEADER)
    print("-" * len(HEADER))
    for agg in aggs.values():
        print(_fmt_row(agg))
    print(f"\nmean mover-signed margin swing per flip-ply: "
          + ", ".join(f"{k}={v['mean_flip_swing']:.2f} (n={v['n_flip_plies']})"
                      for k, v in aggs.items()))

    rand_agg = aggs["random"]
    chain_agg = aggs["chain_vs_chain"]
    packer_agg = aggs["packer_vs_packer"]
    mirror_agg = aggs["chain_vs_mirror"]
    pass_agg = aggs["chain_vs_passbot"]

    # ---- KILL gates (pre-registered, in this order) ----
    print(f"\nKILL-0b1: max(random={rand_agg['flips_per_game']:.3f}, "
          f"chain={chain_agg['flips_per_game']:.3f}) flips/game")
    # KILL-0b1 (build-regression): flips alive under random OR front-builder
    assert max(rand_agg["flips_per_game"], chain_agg["flips_per_game"]) >= 1.0, \
        "KILL-0b1 FIRED: flip mechanic dead"
    print("KILL-0b1: PASS (>= 1.0)")

    print(f"KILL-0b2: mutual-packer mean total score = "
          f"{packer_agg['mean_total_score']:.3f} cells/game")
    # KILL-0b2: packing scores zero
    assert packer_agg["mean_total_score"] <= 2.0, \
        "KILL-0b2 FIRED: mutual packers scored > 2 cells/game"
    print("KILL-0b2: PASS (<= 2.0)")

    print(f"KILL-0b3: random engaged_share at min(80, end) = "
          f"{rand_agg['engaged_at_80']:.3f}")
    # KILL-0b3 (design-model validation): random engaged_share at min(80, end)
    assert 0.01 < rand_agg["engaged_at_80"] < 0.60, \
        f"KILL-0b3 FIRED: engaged_share {rand_agg['engaged_at_80']:.3f}"
    print("KILL-0b3: PASS (inside (0.01, 0.60))")

    # ---- MIRROR CONTINGENCY (decision, never an assert) ----
    mirror_nonloss = mirror_agg["mirror_draw_or_win_share"]
    if mirror_nonloss >= 0.30:
        print(f"\n*** MIRROR_CONTINGENCY: mirror secured >= draw in "
              f"{mirror_nonloss:.0%} of games — prereg licenses ONE switch "
              f"to W=21 + Stage-0a rerun. Owner decision required before "
              f"Stage 1. ***")
    else:
        print(f"\nmirror non-loss share {mirror_nonloss:.0%} < 30% — no contingency")

    # ---- PassBot outcome (diagnostic) ----
    print(f"PassBot probe: P1(front-builder) win {pass_agg['p1_win_share']:.0%}, "
          f"end-cause timeout {pass_agg['timeout_share']:.0%}, "
          f"final scores {pass_agg['mean_s1']:.1f}-{pass_agg['mean_s2']:.1f}")

    return aggs


def _append_memo(game: GameDefV2, aggs: dict[str, dict]) -> None:
    mirror_nonloss = aggs["chain_vs_mirror"]["mirror_draw_or_win_share"]
    pass_agg = aggs["chain_vs_passbot"]

    lines = [
        "",
        "## 4. Stage 0b smoke",
        "",
        f"Pinned cell: `{game.game_id}` (E={SMOKE['E']:.2f}, M_end={SMOKE['M']}, "
        f"komi_cells={SMOKE['komi']}, seed={SMOKE['seed']}). "
        f"{N_RANDOM} random rollouts + {N_SCRIPTED} per scripted matchup. "
        "All scripted pairings are deterministic: each row is "
        f"{N_SCRIPTED} identical games (run as registered).",
        "",
        "| matchup | n | flips/g | mean len | score_margin% | double_pass% "
        "| timeout% | other% | mean s1 | mean s2 | eng@80 | eng final "
        "| P1 win% | P2 win% | draw% |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for agg in aggs.values():
        lines.append(
            f"| {agg['label']} | {agg['n']} | {agg['flips_per_game']:.3f} "
            f"| {agg['mean_len']:.1f} "
            f"| {100 * agg['score_margin_share']:.1f} "
            f"| {100 * agg['double_pass_share']:.1f} "
            f"| {100 * agg['timeout_share']:.1f} | {100 * agg['other_share']:.1f} "
            f"| {agg['mean_s1']:.2f} | {agg['mean_s2']:.2f} "
            f"| {agg['engaged_at_80']:.3f} | {agg['engaged_final']:.3f} "
            f"| {100 * agg['p1_win_share']:.1f} | {100 * agg['p2_win_share']:.1f} "
            f"| {100 * agg['draw_share']:.1f} |"
        )
    lines += [
        "",
        "Engaged-share trajectory (mean engaged_frac at ply 20 / 40 / 80 / final):",
        "",
        "| matchup | @20 | @40 | @80 | final |",
        "|---|---|---|---|---|",
    ]
    for agg in aggs.values():
        lines.append(
            f"| {agg['label']} | {agg['engaged_at_20']:.3f} "
            f"| {agg['engaged_at_40']:.3f} | {agg['engaged_at_80']:.3f} "
            f"| {agg['engaged_final']:.3f} |"
        )
    lines += [
        "",
        "Mover-signed margin swing per flip-ply (mean, n flip-plies): "
        + ", ".join(
            f"{k} {v['mean_flip_swing']:.2f} (n={v['n_flip_plies']})"
            if v["n_flip_plies"] else f"{k} n/a (n=0)"
            for k, v in aggs.items()
        ),
        "",
        f"**KILL-0b1: max(random, chain) flips/game = "
        f"{max(aggs['random']['flips_per_game'], aggs['chain_vs_chain']['flips_per_game']):.3f} "
        f">= 1.0 (PASS)**",
        f"**KILL-0b2: mutual-packer mean total score = "
        f"{aggs['packer_vs_packer']['mean_total_score']:.3f} <= 2.0 (PASS)**",
        f"**KILL-0b3: random engaged_share at min(80, end) = "
        f"{aggs['random']['engaged_at_80']:.3f} in (0.01, 0.60) (PASS)**",
        "",
    ]
    if mirror_nonloss >= 0.30:
        lines.append(
            f"**MIRROR_CONTINGENCY FIRED: mirror secured >= draw in "
            f"{mirror_nonloss:.0%} of games vs front-builder (threshold 30%). "
            "Registered contingency: ONE licensed switch to W=21 + Stage-0a "
            "rerun — owner decision required before Stage 1. Not a kill; "
            "build continues.**"
        )
    else:
        lines.append(
            f"Mirror non-loss share {mirror_nonloss:.0%} < 30% — no contingency."
        )
    lines += [
        "",
        f"PassBot probe: P1 (front-builder) win share "
        f"{pass_agg['p1_win_share']:.0%}, timeout share "
        f"{pass_agg['timeout_share']:.0%}, mean final scores "
        f"{pass_agg['mean_s1']:.1f}-{pass_agg['mean_s2']:.1f} "
        "(stones tiebreak; pass-bot placed zero stones and can never win "
        "per the participation clause).",
        "",
    ]
    with MEMO.open("a") as f:
        f.write("\n".join(lines))
    print(f"\nappended Stage-0b smoke section to {MEMO.name}")


def main() -> None:
    GAMES_DIR.mkdir(exist_ok=True)

    # ---- Build F arm (E, M) grid: 6 variants ----
    f_games = [build_f(e, m) for e in GRID_E for m in GRID_M]
    for g in f_games:
        # Harness-level invariant (registered at Task 5 review): komi must
        # never reach the early-end margin
        assert abs(g.win_condition.komi_cells) < g.win_condition.end_margin, (
            f"komi/end_margin invariant violated on {g.game_id}"
        )
        path = GAMES_DIR / f"{g.game_id}.json"
        path.write_text(json.dumps(g.to_dict(), indent=2))
        # Round-trip sanity check
        g2 = GameDefV2.from_dict(json.loads(path.read_text()))
        assert g2.canonical_hash() == g.canonical_hash(), (
            f"canonical_hash mismatch on round-trip: {g.game_id}"
        )
        print(f"wrote + verified {path.name}")

    # ---- Copy probe-calibrated comparators (S, A1, A0) ----
    for src_dir, name in (
        (SIEGE_CAL, "s_flip_r2.json"),
        (FC15_CAL, "a1_field_connect.json"),
        (FC15_CAL, "a0_baseline.json"),
    ):
        shutil.copy(src_dir / name, GAMES_DIR / name)
        print(f"copied probe-calibrated {name}")

    # ---- Stage-0b smoke on the pinned cell ----
    pinned_id = f"f_frontline_E{SMOKE['E']:.2f}_M{SMOKE['M']}".replace(".", "p")
    pinned = next(g for g in f_games if g.game_id == pinned_id)
    print(f"\nRunning Stage-0b smoke on: {pinned.game_id}")

    aggs = smoke(pinned)
    _append_memo(pinned, aggs)

    print("\n\nSMOKE OK — Stage-0b KILL gates cleared.")


if __name__ == "__main__":
    main()
