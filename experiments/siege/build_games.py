"""SIEGE campaign — arm configs + Stage-0b smoke (pre-registered).

Builds the M arm (N,T) grid (9 variants) and S arm (s_flip_r2), copies
probe-calibrated A0/A1 comparators, then runs Stage-0b: 1000 random rollouts
+ 200 scripted chain-builder rollouts per arm (m_siege mid-grid N5_T120 and
s_flip_r2) with flip-locus (frontier vs straggler) logged at flip time.

KILL gate (pre-registered):
  assert max(flips_random, flips_scripted) >= 1.0   (per arm)

Usage:
    .venv/bin/python experiments/siege/build_games.py
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
from experiments.siege.scripted_agents import ChainBuilder, FlipHunter  # noqa: E402

HERE = Path(__file__).resolve().parent
GAMES_DIR = HERE / "games"
FC15_CAL = ROOT / "experiments" / "fc_phase15" / "games" / "calibrated"

W = 22  # hex_rhombus board width

# -----------------------------------------------------------------------
# COMMON base — mirrors fc_phase15 COMMON but with:
#   • pie_rule=False (roles seat-fixed per SIEGE pre-registration)
#   • FIELD r=2 (SIEGE; fc_phase15 used r=1)
#   • control_margin=0.0 (SIEGE; fc_phase15 used 0.25)
# -----------------------------------------------------------------------
COMMON = dict(
    num_dimensions=2,
    axis_size=W,
    topology_type="hex_rhombus",
    turn_structure=TurnStructure(turn_type="alternating"),
    action_rule=ActionRule(action_types=("place",)),
    placement_rule=PlacementRule(target="empty", constraint="anywhere"),
    pie_rule=False,  # seat-fixed; pre-registration §Arms
)

# SIEGE win condition dict (shared across M variants; max_turns set per call)
WIN_M = dict(
    condition_type="field_connection",
    condition_type_p2="capture_quota",
    timeout_winner=2,
    target_dimension=0,
    control_margin=0.0,
)

# SIEGE propagation — r=2 (vs fc_phase15's r=1)
FIELD = dict(prop_type="influence", radius=2, strength=1.0, decay=0.5)

GRID_N = (3, 5, 8)
GRID_T = (80, 120, 160)


def _quota_for_n(n: int) -> int:
    """Capture quota = N.  Breaker must flip N distinct Maker-stone cells."""
    return n


def build_m(n: int, t: int) -> GameDefV2:
    """Build one M-arm SIEGE game.

    game_id: m_siege_N{n}_T{t}
    P1 Maker wins via field_connection across target_dimension=0.
    P2 Breaker wins via capture_quota=N distinct Maker-cell flips, capped 2/move.
    At timeout (max_turns=t), P2/Breaker wins (timeout_winner=2).
    Both players use field_flip capture (symmetric capture rule).
    """
    return GameDefV2(
        game_id=f"m_siege_N{n}_T{t}",
        capture_rule=CaptureRule(capture_type="field_flip"),
        propagation_rule=PropagationRule(**FIELD),
        win_condition=WinCondition(
            **WIN_M,
            capture_quota=_quota_for_n(n),
            max_turns=t,
        ),
        **COMMON,
    )


def build_s() -> GameDefV2:
    """Build the S arm: s_flip_r2.

    Base: fc_phase15 calibrated a1_field_connect.json (loaded + patched).
    Manipulated variable vs m_siege: symmetric win-structure (both players
    field_connection) vs SIEGE asymmetry.  Pie ON (as A1 had it).

    Patches applied:
      - game_id = "s_flip_r2"
      - capture_rule = field_flip  (C1 variant on A1's substrate)
      - komi_p2 = 0.0  (calibration will set it later)
    """
    src = FC15_CAL / "a1_field_connect.json"
    d = json.loads(src.read_text())
    game = GameDefV2.from_dict(d)
    game.game_id = "s_flip_r2"
    game.capture_rule = CaptureRule(capture_type="field_flip")
    game.komi_p2 = 0.0
    # pie_rule stays True as A1 had it (documented: pie + calibration policy
    # difference is the residual variance vs m_siege beyond win-structure asymmetry).
    return game


# -----------------------------------------------------------------------
# Stage-0b smoke helpers
# -----------------------------------------------------------------------

def _run_rollout(engine, agents: list) -> dict:
    """Run one episode and return flip metrics.

    Flip classification at flip time:
      frontier: the flipped cell has >= 2 neighbors owned by the current mover
                (the cell is being absorbed into the mover's cluster)
      straggler: otherwise

    Returns:
        flips (int), frontier (int), straggler (int),
        quota_ticks (int|None), distinct_quota (int|None),
        timeout (bool), length (int)
    """
    obs = engine.reset()
    topo = engine.topo
    board = engine.board_owners
    total_cells = engine.total_cells

    flips = 0
    frontier_flips = 0
    straggler_flips = 0

    game = engine.game
    is_siege = game.win_condition.condition_type_p2 == "capture_quota"

    while not engine.done:
        player_idx = engine.get_current_player()  # 0-indexed
        agent = agents[player_idx]
        legal = engine.get_legal_actions()

        # Snapshot board_owners before step for flip classification
        prev_owners = board.copy()

        action, _, _ = agent.select_action(obs, legal_actions=legal, deterministic=False)
        obs, _, done, info = engine.step(action)

        # Skip pie-swap steps (no placement, no flips)
        if info.get("pie_swap"):
            continue

        # Detect flips: cells that changed owner from 1→2 or 2→1
        # Mover is the player who just placed (0-indexed player_idx → owner = player_idx+1)
        mover_owner = player_idx + 1  # 1 or 2
        enemy_owner = 3 - mover_owner

        # A flip by the current mover: a cell that was enemy_owner before and is
        # now mover_owner. (Mover can also flip back their own previously-flipped
        # cells that were in enemy control.)
        for c in range(total_cells):
            if prev_owners[c] == enemy_owner and board[c] == mover_owner:
                flips += 1
                # Classify: frontier if >= 2 neighbors owned by mover BEFORE step
                # (but after capture: use current board state is wrong; use prev_owners
                # for "before" — the mover's own stones that surrounded the cell)
                mover_nbr_count = sum(
                    1 for nbr in topo.get_neighbors(c)
                    if prev_owners[nbr] == mover_owner
                )
                if mover_nbr_count >= 2:
                    frontier_flips += 1
                else:
                    straggler_flips += 1

    return dict(
        flips=flips,
        frontier=frontier_flips,
        straggler=straggler_flips,
        quota_ticks=engine._quota_ticks if is_siege else None,
        distinct_quota=len(engine._quota_cells) if is_siege else None,
        timeout=engine._ended_by_max_turns,
        length=engine.step_count,
    )


def _aggregate(results: list[dict]) -> dict:
    n = len(results)
    flips = [r["flips"] for r in results]
    timeouts = [r["timeout"] for r in results]
    lengths = [r["length"] for r in results]
    frontiers = [r["frontier"] for r in results]
    total_flips = sum(flips)
    frontier_pct = (100.0 * sum(frontiers) / total_flips
                    if total_flips > 0 else float("nan"))
    out = dict(
        n=n,
        flips_per_game=float(np.mean(flips)),
        distinct_per_game=float(np.mean([r["distinct_quota"] or 0 for r in results])),
        timeout_pct=100.0 * sum(timeouts) / n,
        mean_len=float(np.mean(lengths)),
        frontier_pct=frontier_pct,
    )
    quota_vals = [r["quota_ticks"] for r in results if r["quota_ticks"] is not None]
    if quota_vals:
        out["quota_ticks_per_game"] = float(np.mean(quota_vals))
    return out


def smoke_arm(game: GameDefV2, arm_name: str) -> None:
    """Run Stage-0b smoke on one arm: 1000 random + 200 scripted rollouts."""
    N_RANDOM = 1000
    N_SCRIPTED = 200

    engine = create_engine(game)
    is_siege = game.win_condition.condition_type_p2 == "capture_quota"

    # ---- Random rollouts (seed=7 per pre-registration) ----
    t0 = time.time()
    rng = np.random.default_rng(7)
    # Fresh RandomAgent pair per episode, seeded from the master rng for
    # independence + reproducibility
    random_results = []
    for _ in range(N_RANDOM):
        ra = [
            RandomAgent(seed=int(rng.integers(0, 2**31))),
            RandomAgent(seed=int(rng.integers(0, 2**31))),
        ]
        random_results.append(_run_rollout(engine, ra))
    t_random = time.time() - t0

    # ---- Scripted rollouts ----
    # M arm: ChainBuilder(1) vs FlipHunter(2) — 200 games
    # S arm (symmetric): both pairings 100+100 since S has no role asymmetry
    t1 = time.time()
    scripted_results = []

    def run_scripted_game(player1_agent, player2_agent):
        player1_agent.bind(engine)
        player2_agent.bind(engine)
        agents = [player1_agent, player2_agent]  # 0-indexed: agent[0]=P1, agent[1]=P2
        return _run_rollout(engine, agents)

    if is_siege:
        # M arm: Maker=ChainBuilder(1) vs Breaker=FlipHunter(2), 200 games
        for _ in range(N_SCRIPTED):
            r = run_scripted_game(ChainBuilder(player=1, axis=0), FlipHunter(player=2))
            scripted_results.append(r)
    else:
        # S arm is symmetric: 100 games each pairing
        half = N_SCRIPTED // 2
        for _ in range(half):
            r = run_scripted_game(ChainBuilder(player=1, axis=0), FlipHunter(player=2))
            scripted_results.append(r)
        for _ in range(half):
            # Reverse pairing: FlipHunter as P1, ChainBuilder as P2
            r = run_scripted_game(FlipHunter(player=1), ChainBuilder(player=2, axis=1))
            scripted_results.append(r)
    t_scripted = time.time() - t1

    # ---- Aggregate ----
    rand_agg = _aggregate(random_results)
    scr_agg = _aggregate(scripted_results)

    # ---- Print table ----
    print(f"\n{'='*60}")
    print(f"ARM: {arm_name}  (is_siege={is_siege})")
    print(f"{'='*60}")
    header = f"{'policy':<14} {'flips/g':>8} {'distinct/g':>11}"
    if is_siege:
        header += f" {'quota_t/g':>10}"
    header += f" {'timeout%':>9} {'len':>7} {'frontier%':>10}"
    print(header)
    print("-" * len(header))

    def row(label, agg):
        s = f"{label:<14} {agg['flips_per_game']:>8.3f} {agg['distinct_per_game']:>11.3f}"
        if is_siege:
            s += f" {agg.get('quota_ticks_per_game', float('nan')):>10.3f}"
        s += f" {agg['timeout_pct']:>9.1f} {agg['mean_len']:>7.1f} {agg['frontier_pct']:>10.1f}"
        return s

    print(row("random", rand_agg))
    print(row("scripted", scr_agg))
    print(f"\nRuntime: random={t_random:.1f}s  scripted={t_scripted:.1f}s")

    # ---- KILL gate (pre-registered) ----
    flips_random = rand_agg["flips_per_game"]
    flips_scripted = scr_agg["flips_per_game"]
    max_flips = max(flips_random, flips_scripted)
    print(f"\nKILL gate: max(random={flips_random:.3f}, scripted={flips_scripted:.3f}) = {max_flips:.3f}")
    assert max_flips >= 1.0, (
        f"KILL FIRED on {arm_name}: max flips/game = {max_flips:.3f} < 1.0 "
        f"under BOTH random and scripted policy — arm is mechanically dead"
    )
    print(f"KILL gate: PASS (>= 1.0)")


def main() -> None:
    GAMES_DIR.mkdir(exist_ok=True)

    # ---- Build M arm (N,T) grid: 9 variants ----
    m_games = [build_m(n, t) for n in GRID_N for t in GRID_T]
    for g in m_games:
        path = GAMES_DIR / f"{g.game_id}.json"
        d = g.to_dict()
        path.write_text(json.dumps(d, indent=2))
        # Round-trip sanity check
        g2 = GameDefV2.from_dict(json.loads(path.read_text()))
        assert g2.canonical_hash() == g.canonical_hash(), (
            f"canonical_hash mismatch on round-trip: {g.game_id}"
        )
        print(f"wrote + verified {path.name}")

    # ---- Build S arm ----
    s_game = build_s()
    s_path = GAMES_DIR / "s_flip_r2.json"
    s_path.write_text(json.dumps(s_game.to_dict(), indent=2))
    s2 = GameDefV2.from_dict(json.loads(s_path.read_text()))
    assert s2.canonical_hash() == s_game.canonical_hash(), "canonical_hash mismatch on s_flip_r2"
    print(f"wrote + verified s_flip_r2.json")

    # ---- Copy probe-calibrated comparators (A0/A1) ----
    for name in ("a0_baseline.json", "a1_field_connect.json"):
        shutil.copy(FC15_CAL / name, GAMES_DIR / name)
        print(f"copied probe-calibrated {name}")

    # ---- Stage-0b smoke: mid-grid M + S ----
    mid_game = next(g for g in m_games if g.game_id == "m_siege_N5_T120")
    print(f"\nRunning Stage-0b smoke on: {mid_game.game_id} + s_flip_r2")

    smoke_arm(mid_game, mid_game.game_id)
    smoke_arm(s_game, "s_flip_r2")

    print("\n\nSMOKE OK — Stage-0b gates cleared.")


if __name__ == "__main__":
    main()
