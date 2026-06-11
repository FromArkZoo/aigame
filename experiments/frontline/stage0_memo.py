"""Stage 0a — FRONTLINE kernel memo (prereg-locked geometries; run AFTER
prereg lock 3a378dd, BEFORE any training).

Sections:
  1. Corrected flip-threshold table incl. own-side d2 support — the SIEGE
     memo's chain rows assumed a 2-chain; a linear 3-chain end has
     I2 = 1.75 and the d1+d1+d1+d2 profile nets exactly 0.0 (no flip).
  2. Engagement-saturation table (analytic model, spec §4.1), E x fill.
  3. Flip margin-swing Delta(S_cap - S_opp) at E=1.0 on the PINNED
     canonical set (coordinates fixed below before computing), vacuum +
     second-rank variants, computed through the REAL engine (placement →
     cascade → contested_scores), not hand arithmetic.

KILL-0a1: mean margin swing across the pinned front set < -2.
KILL-0a2: analytic engaged_share at 20% fill, E=1.0 > 0.60.
Writes STAGE0_MEMO.md. Usage: .venv/bin/python experiments/frontline/stage0_memo.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from game_engine.factory import create_engine  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from game_engine.rules import (  # noqa: E402
    ActionRule, CaptureRule, PlacementRule, PropagationRule,
    TurnStructure, WinCondition,
)

W = 22
RADIUS, STRENGTH, DECAY = 2, 1.0, 0.5
E_GRID = (0.75, 1.0, 1.25)
FILL_GRID = (0.10, 0.20, 0.41)


def make_game() -> GameDefV2:
    return GameDefV2(
        game_id="f_stage0_probe", num_dimensions=2, axis_size=W,
        topology_type="hex_rhombus",
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="field_flip"),
        propagation_rule=PropagationRule(
            prop_type="influence", radius=RADIUS, strength=STRENGTH, decay=DECAY),
        win_condition=WinCondition(
            condition_type="contested_majority", engage_threshold=1.0,
            end_margin=8, min_turns_score_end=20, control_margin=0.0,
            max_turns=200),
        pie_rule=False,
    )


# ---------------------------------------------------------------------------
# Helpers copied VERBATIM from experiments/siege/stage0_memo.py:47-114
# (frozen campaign artifact — copied, not imported, so the siege memo never
# grows dependencies and frontline never depends on siege internals).
# ---------------------------------------------------------------------------

def field_at(engine, cell: int, stones: dict[int, int]) -> float:
    """Net field at `cell` given {cell: owner} stones, via engine recompute."""
    engine.board_owners[:] = 0
    engine.board_values[:] = 0.0
    for c, owner in stones.items():
        engine.board_owners[c] = owner
    engine._recompute_field()
    return float(engine.board_values[cell])


def min_attackers(engine, victim: int, support: dict[int, int]) -> tuple[int, str]:
    """Smallest attacker set (P2 stones) making net field at victim negative.

    Uses a count-based search over (n_d1, n_d2) pairs — the field contribution
    from an attacker depends only on its distance to the victim, so only
    distance counts matter. Equivalent to full subset search but O(1).

    Returns (count, description-of-distances).
    """
    topo = engine.topo

    # Contribution weights at the victim cell from an attacker at each distance
    w_d1 = STRENGTH * (DECAY ** 1)   # 0.5
    w_d2 = STRENGTH * (DECAY ** 2)   # 0.25

    # How many attacker candidates are available at each distance from victim,
    # excluding the victim itself and any support stones already placed.
    excluded = set(support.keys()) | {victim}
    r1_cells = [c for c in topo.cells_within_radius(victim, 1) if c != victim and c not in excluded]
    r2_cells = [c for c in topo.cells_within_radius(victim, RADIUS) if topo.distance(victim, c) == 2 and c not in excluded]
    max_d1 = len(r1_cells)
    max_d2 = len(r2_cells)

    # Own-side field at victim from victim itself + support stones
    stones_own = {victim: 1, **support}
    own_field = field_at(engine, victim, stones_own)

    # Search (n_d1, n_d2) pairs for smallest total count that yields negative net field.
    # Attackers are P2 (sign -1): flip when own_field - n_d1*w_d1 - n_d2*w_d2 < 0.
    for total_k in range(1, max_d1 + max_d2 + 1):
        for n_d1 in range(min(total_k, max_d1) + 1):
            n_d2 = total_k - n_d1
            if n_d2 > max_d2:
                continue
            net = own_field - n_d1 * w_d1 - n_d2 * w_d2
            if net < 0.0:
                # total_k is the global minimum: any (n_d1, n_d2) at this
                # level suffices; stop.
                dists = ["d1"] * n_d1 + ["d2"] * n_d2
                return total_k, "+".join(dists)
    # A pre-registration anchor must fail loudly, not emit a sentinel row.
    raise RuntimeError(f"no flip found within {max_d1 + max_d2} attackers")


def pick_interior_cell(topo) -> int:
    """First cell with the full hex interior neighbourhood: 6 distance-1
    neighbours AND 12 distance-2 cells.

    Guards against edge/corner probe cells — len(active_cells)//2 lands on a
    LEFT-EDGE cell of the W=22 rhombus (only 4 d1 neighbours), which silently
    inflates the chain-interior/dense-interior thresholds."""
    for cell in topo.active_cells:
        n_d1 = len([c for c in topo.cells_within_radius(cell, 1) if c != cell])
        n_d2 = len([c for c in topo.cells_within_radius(cell, 2)
                    if topo.distance(cell, c) == 2])
        if n_d1 == 6 and n_d2 == 12:
            return cell
    raise RuntimeError("no fully-interior cell found on this topology")


# ---------------------------------------------------------------------------
# Section 1 — corrected threshold table (own-side d2 support included)
# ---------------------------------------------------------------------------

def threshold_table(engine) -> list[tuple[str, int, str]]:
    topo = engine.topo
    c = pick_interior_cell(topo)
    east = c + 1            # same row: hex_rhombus axial +q
    east2 = c + 2           # distance 2, collinear
    rows = []
    k, d = min_attackers(engine, c, {})
    rows.append(("lone stone", k, d))
    k, d = min_attackers(engine, c, {east: 1})
    rows.append(("2-chain end", k, d))
    k, d = min_attackers(engine, c, {east: 1, east2: 1})
    rows.append(("3-chain end (linear; own d2 term)", k, d))
    k, d = min_attackers(engine, c, {c - 1: 1, east: 1, east2: 1})
    rows.append(("4-chain interior (linear)", k, d))
    return rows


# ---------------------------------------------------------------------------
# Section 2 — analytic engagement model (spec §4.1: Bernoulli d0 + Poisson rings)
# ---------------------------------------------------------------------------

def _pois_pmf(lam: float, k: int) -> float:
    return math.exp(-lam) * lam**k / math.factorial(k)


def _p_ring_sum_ge(lam1: float, lam2: float, target: float) -> float:
    """P(0.5*X1 + 0.25*X2 >= target), X1~Poi(lam1), X2~Poi(lam2)."""
    if target <= 0:
        return 1.0
    p = 0.0
    for k1 in range(0, 40):
        need = target - 0.5 * k1
        if need <= 0:
            p += _pois_pmf(lam1, k1)
            continue
        k2_min = math.ceil(need / 0.25 - 1e-12)
        p += _pois_pmf(lam1, k1) * (
            1.0 - sum(_pois_pmf(lam2, k2) for k2 in range(0, k2_min)))
    return p


def p_engaged_both(rho: float, e: float) -> float:
    """P(cell engaged) = P(I_p >= e)^2 under the interior-cell model."""
    p_side = rho * _p_ring_sum_ge(6 * rho, 12 * rho, e - 1.0) + \
        (1 - rho) * _p_ring_sum_ge(6 * rho, 12 * rho, e)
    return p_side ** 2


# ---------------------------------------------------------------------------
# Section 3 — margin-swing triad (PINNED geometries; engine-applied flips)
# ---------------------------------------------------------------------------

def margin_swing(engine, pre_stones: dict[int, int], place: int) -> dict:
    """Set board to pre_stones, P1 places `place` (flips cascade inside the
    engine), return before/after (s1 - s2) from the capturer (P1) view."""
    engine.reset()
    engine.board_owners[:] = 0
    for c, o in pre_stones.items():
        engine.board_owners[c] = o
    engine._recompute_field()
    # Sync stone bookkeeping with the direct board write: the win check
    # reads piece_counts (zero-stones clause) and the flip accounting in
    # step() updates it incrementally from whatever it currently holds.
    n1_pre = sum(1 for o in pre_stones.values() if o == 1)
    n2_pre = sum(1 for o in pre_stones.values() if o == 2)
    engine.piece_counts = [n1_pre, n2_pre]
    engine._placements_made = [n1_pre, n2_pre]
    s1_b, s2_b, _ = engine.contested_scores()
    engine.current_player = 1
    engine.step_count = 30          # past min_turns; parity irrelevant here
    engine._cm_streak = 0
    engine.step(place)
    # contested_scores stays callable even if the step ended the game.
    s1_a, s2_a, _ = engine.contested_scores()
    # Flipped count from the board itself (P1 stones after = pre + 1 placed
    # + flips), immune to any piece_counts bookkeeping drift.
    flipped = int((engine.board_owners == 1).sum()) - (n1_pre + 1)
    return dict(before=s1_b - s2_b, after=s1_a - s2_a,
                swing=(s1_a - s2_a) - (s1_b - s2_b), flipped=flipped)


def pinned_configs(topo) -> dict[str, tuple[dict[int, int], int]]:
    """The prereg-pinned canonical set. c = interior anchor; rows are
    (pre-placement stones, P1's triggering placement)."""
    c = pick_interior_cell(topo)
    d1 = sorted(x for x in topo.cells_within_radius(c, 1) if x != c)
    d2 = sorted(x for x in topo.cells_within_radius(c, 2)
                if topo.distance(c, x) == 2)
    east, east2 = c + 1, c + 2
    west = c - 1
    # west is itself at distance 2 from east and is listed separately in
    # every chain config below — exclude it from the far-d1 candidates so
    # the dict literals don't collapse a key and silently drop an attacker
    # (the prereg pins "2-chain end (memo profile)" = d1+d1+d1+d2 and
    # "3-chain end (4x d1)"; with the collision neither profile would
    # materialize).
    d1_far = [x for x in d1
              if topo.distance(x, east) >= 2 and x != west]  # far from chain
    d1_near = [x for x in d1 if topo.distance(x, east) == 1 and x != east]
    d2_west = [x for x in d2 if topo.distance(x, east) > 2]
    # Second rank at d2 behind the chain — prereg Stage 0a(3) literal: "a
    # second-rank enemy support row at d2 behind the chain". +2W = axial
    # (0, +2) = two rows behind; each support stone is distance 2 from its
    # chain stone (verified below). A d1-support variant (+W) suppresses
    # the trigger flip entirely; recorded during build review, excluded
    # from the registered set.
    behind = [east + 2 * W, east2 + 2 * W]
    assert topo.distance(east, east + 2 * W) == 2, "second rank not at d2"
    assert topo.distance(east2, east2 + 2 * W) == 2, "second rank not at d2"
    cfg = {}
    # straggler: victim c, P1 at two far d1, trigger = far d2
    cfg["straggler"] = ({c: 2, d1_far[0]: 1, d1_far[1]: 1}, d2_west[0])
    # 2-chain far: chain c-east; attackers on the west side
    cfg["2chain_far"] = (
        {c: 2, east: 2, d1_far[0]: 1, d1_far[1]: 1, west: 1}, d2_west[0])
    # 2-chain near: attackers adjacent to the chain neighbour
    cfg["2chain_near"] = (
        {c: 2, east: 2, d1_near[0]: 1, d1_far[0]: 1, west: 1}, d2_west[0])
    # 3-chain: corrected threshold — 4 attackers ALL at d1
    cfg["3chain_4d1"] = (
        {c: 2, east: 2, east2: 2, d1_far[0]: 1, d1_far[1]: 1, west: 1},
        d1_near[0] if d1_near else d1[0])
    # second-rank variants: enemy support row at d2 behind the chain —
    # prereg: "EACH in vacuum AND with a second-rank enemy support row",
    # so all three chain rows get a rank2 variant.
    for name in ("2chain_far", "2chain_near", "3chain_4d1"):
        stones, trig = cfg[name]
        stones2 = dict(stones)
        for b in behind:
            stones2[b] = 2
        cfg[name + "_rank2"] = (stones2, trig)
    return cfg


def _pinned_coordinates_block(topo) -> list[str]:
    """Exact axial coordinates of the pinned set (prereg Stage 0a: pinned
    BEFORE computing)."""
    out = ["Pinned cells (cell index, axial (q, r) with cell = r*W + q; "
           f"W = {W}; second-rank offset = +2W, axial (0, +2) = two rows "
           "behind, verified distance 2 from each chain stone):", ""]
    for name, (stones, trig) in pinned_configs(topo).items():
        parts = ", ".join(
            f"{cell}{topo.cell_to_coords(cell)}:P{owner}"
            for cell, owner in sorted(stones.items()))
        out.append(f"- {name}: {{{parts}}} -> P1 plays "
                   f"{trig}{topo.cell_to_coords(trig)}")
    out.append("")
    return out


def main() -> None:
    game = make_game()
    engine = create_engine(game)
    out = ["# Stage 0a — FRONTLINE kernel memo (prereg 3a378dd, pinned)", ""]

    out += ["## 1. Corrected flip thresholds (own-side d2 support included)",
            "", "| position | min attackers | distances |", "|---|---|---|"]
    for name, k, d in threshold_table(engine):
        out.append(f"| {name} | {k} | {d} |")

    out += ["", "## 2. Analytic engagement saturation (interior-cell model)",
            "", "| E \\ fill | " + " | ".join(f"{f:.0%}" for f in FILL_GRID) + " |",
            "|---|" + "---|" * len(FILL_GRID)]
    sat = {}
    for e in E_GRID:
        cells = [p_engaged_both(f / 2, e) for f in FILL_GRID]  # rho = per-side
        sat[e] = dict(zip(FILL_GRID, cells))
        out.append(f"| {e} | " + " | ".join(f"{v:.3f}" for v in cells) + " |")

    out += ["", "## 3. Margin swing at E=1.0 (engine-applied, pinned set)", ""]
    out += _pinned_coordinates_block(engine.topo)
    out += ["| config | before | after | swing | stones flipped |",
            "|---|---|---|---|---|"]
    all_swings = []
    front_swings = []
    for name, (stones, trig) in pinned_configs(engine.topo).items():
        r = margin_swing(engine, stones, trig)
        out.append(f"| {name} | {r['before']} | {r['after']} | "
                   f"{r['swing']} | {r['flipped']} |")
        all_swings.append(r["swing"])
        if name != "straggler":
            front_swings.append(r["swing"])

    out += ["", "A d1-support variant (second rank at +W) suppresses the "
            "flip (swing +1/+2, 0 flips); recorded during build review.", ""]

    # Prereg's "mean margin swing across the pinned canonical front set" is
    # ambiguous about the straggler row (lone stone — arguably not "front").
    # Resolution: compute BOTH readings and apply KILL-0a1 to the more
    # conservative (lower) mean, so no reading can rescue a failing set.
    mean_front = sum(front_swings) / len(front_swings)
    mean_all = sum(all_swings) / len(all_swings)
    mean_swing = min(mean_front, mean_all)
    k0a2 = sat[1.0][0.20]
    out += ["",
            f"Mean swing, front-only (chain rows, vacuum + rank2): "
            f"{mean_front:.2f}; all rows (incl. straggler): {mean_all:.2f}. "
            "KILL-0a1 applied to the lower of the two.",
            "",
            f"**KILL-0a1: mean front margin swing = {mean_swing:.2f} "
            f"({'KILL' if mean_swing < -2 else 'PASS'})**",
            f"**KILL-0a2: engaged@20% fill, E=1.0 = {k0a2:.3f} "
            f"({'KILL' if k0a2 > 0.60 else 'PASS'})**", ""]
    Path(__file__).with_name("STAGE0_MEMO.md").write_text("\n".join(out))
    print("\n".join(out))
    assert mean_swing >= -2, "STAGE 0a KILL-0a1 fired"
    assert k0a2 <= 0.60, "STAGE 0a KILL-0a2 fired"


if __name__ == "__main__":
    main()
