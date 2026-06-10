# SIEGE Pivot Campaign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and pre-register the SIEGE campaign — asymmetric Maker–Breaker win conditions on the validated r=2 field — with z_flip_r2 as control arm S, through a runnable mechanical screen and a ready blind pack.

**Architecture:** Three gated engine additions (asymmetric P2 win dispatch, capture_quota with distinct-stone accounting, timeout_winner), one gated observation float (quota_frac), then a four-arm experiment harness under `experiments/siege/` mirroring `experiments/fc_phase15/` conventions exactly (PREREGISTRATION → build+smoke → calibrate → screen → blind pack). All engine work is additive and keyed off new `WinCondition` fields that default to legacy-inert values, so every legacy game stays bit-identical (canonical hashes unchanged, observation dims unchanged).

**Tech Stack:** Python 3, numpy, PyTorch (existing PPO trainer), pytest. No new dependencies.

**Spec of record:** `docs/pivot_menu_synthesis_2026-06-10.md` (the probe skeleton section). Decision grammar follows `docs/superpowers/specs/2026-06-10-field-connect-phase15-design.md` §7 shape.

---

## Pre-verified engine facts (read before coding; all verified 2026-06-10)

- Win dispatch: `game_engine/engine_v2.py:1188` `_check_win_conditions()`, branches on `wc.condition_type` string. `field_connection` branch at ≈1211–1220 calls `_check_field_connection(dim_p1, dim_p2, margin)` (≈1280–1311), which checks BOTH players' controlled-set face connection.
- Turn cap: `engine_v2.py:368-371` — `step_count >= self.game.max_game_steps` → `_end_by_max_turns()` (≈1364–1402). That method already special-cases `field_connection` (controlled-cell tiebreak with komi). End-cause flags `_ended_by_max_turns` / `_ended_by_no_moves` exist (≈158–167).
- Flip capture: `_capture_field_flip(placed_cell)` at `engine_v2.py:905-933`. Cascading while-loop; flips recorded only via `piece_counts` deltas — **no event counter exists yet**. `mover = self.current_player` (win check runs before player advance — verify in `step()` when editing).
- Control: `_control_mask(player)` at ≈897–903, margin from `wc.control_margin` via getattr.
- Observation: `engine_v2.py:1463-1491` `_observe()` → `[owner_encoded(total_cells), board_values(total_cells), step_frac, own_frac, enemy_frac]`. `state_dim` = `total_cells * 2 + 3` at `game_engine/game_def_v2.py:92-99`. **`step_frac` ≡ the skeleton's clock_frac — already present; do NOT add a duplicate. Only quota_frac is new.**
- Config: `GameDefV2` in `game_def_v2.py:35-82` (`pie_rule`, `komi_p2` fields exist). `WinCondition` in `game_engine/rules.py:210-240` (`condition_type, threshold, target_dimension, target_dimension_p2, max_turns, control_margin`). Serde omits defaults — mirror the `control_margin` pattern at `rules.py:257-258`. Canonical-hash stability via `canonical_blob()` at `game_def_v2.py:273-295`.
- Trainer: per-seat `PolicyNetwork`s at `training/trainer.py:99-107` (list indexed by player — asymmetric roles need NO trainer changes; `obs_dim` flows from `game.state_dim`). `evaluate()` at 553–698 (tvr is agents[0]-both-seats — NOT role-aware; SIEGE needs its own per-role tvr in the harness, not in trainer.py).
- Harness conventions: copy the anatomy of `experiments/fc_phase15/` — `PREREGISTRATION.md`, `build_games.py` (COMMON/WIN/FIELD dicts at lines 41–58), `calibrate.py` (BIAS_PASS=0.10, smallest-passing, BIAS_UNRESOLVED loud-skip), `run_screen.py` (`instrumented_episode` at 58–109, screen bars applied verbatim at 182–243, CSV+MD outputs), `metrics.py`, root-level engine tests (`test_field_capture_phase15.py` style). Blind packs live in `evaluations/<name>/` with sealed `.blind_mapping.json` + `play.py` runpy shim + `BRIEFING.md` + templates (see `evaluations/probe_ab/`).
- Comparator sources: `experiments/fc_phase15/games/calibrated/a0_baseline.json` and `a1_field_connect.json` (exist, verified).
- Test suite: 242 tests, `python -m pytest test_*.py -q` from repo root (also run `experiments/fc_phase15/test_phase15_metrics.py` separately if needed).

## Locked constants (judgment calls — owner may adjust ONLY before the prereg commit in Task 1)

| Constant | Value | Rationale |
|---|---|---|
| `QUOTA_TICK_CAP_PER_MOVE` | 2 | distinct-cell accounting kills flip-tennis; cap guards single-cascade quota bursts |
| (N, T) calibration grid | {3,5,8} × {80,120,160} | skeleton verbatim |
| Per-role skill gate | role tvr ≥ 0.80 AND ≥ +0.15 over that role's random-vs-random baseline | fixes the vacuous Breaker gate |
| Collapsed-seed rerun reserve | seeds 45 then 46, max one rerun per grid cell | rerun-not-exclude graft |
| Role-matrix size | 3×3 seed pairings × 22 games = 198 | cross-seed decorrelation |
| Comparative floors | flips Δ≥0.5 abs; length Δ≥10 toward center 95; drama Δ≥0.05 | honest-denoiser effect-size floors |
| Blind labels | D / V / X (fresh; Q,Z,K,M,T burned) | sealed-mapping convention |
| A1 validity band | blind A1 ∈ [3.9, 4.4] | campaign-validity graft |

---

### Task 1: PREREGISTRATION.md (locked before any training)

**Files:**
- Create: `experiments/siege/PREREGISTRATION.md`

- [ ] **Step 1: Write the pre-registration document**

Transcribe the probe skeleton from `docs/pivot_menu_synthesis_2026-06-10.md` into the fc_phase15 PREREGISTRATION format, with the locked constants above substituted in. Full content:

```markdown
# SIEGE campaign — pre-registration (locked before any training run)

Spec of record: docs/pivot_menu_synthesis_2026-06-10.md (probe skeleton).
Decision grammar shape: docs/superpowers/specs/2026-06-10-field-connect-phase15-design.md §7.

## Arms (4 in screen, 3 in blind)
- m_siege (treatment): P1 Maker wins field_connection; P2 Breaker wins capture_quota
  (N distinct-Maker-stone flip ticks, per-move tick cap 2) OR timeout (timeout_winner=2 at T).
  Both players field_flip. hex_rhombus W=22, influence r=2/s=1.0/d=0.5, control_margin 0.0,
  pie OFF (roles fixed; role-pie is the registered lever of last resort, one retry max).
  Observation adds quota_frac; clock_frac ≡ existing step_frac (verified present, not duplicated).
- s_flip_r2 (control): symmetric field_flip + field_connection on the identical substrate
  (= a1_field_connect + field_flip capture). Fresh pre-registration of the phase-1.5
  post-hoc candidate. Single manipulated variable vs m_siege = win-structure asymmetry.
- a1_field_connect (comparator): retrained in-campaign from
  experiments/fc_phase15/games/calibrated/a1_field_connect.json.
- a0_baseline (comparator, screen only): retrained in-campaign from
  experiments/fc_phase15/games/calibrated/a0_baseline.json.

## Stage 0 (pre-training kills)
- 0a flip-threshold memo on CHAINS at r=2/d=0.5/eps=0, computed from the engine's own kernels.
  KILL: lone-stone flip needs > 4 coordinated attackers.
- 0b 1000 random rollouts + 200 scripted chain-builder rollouts per arm (m_siege, s_flip_r2),
  flip-locus (frontier vs straggler) logged.
  KILL: < 1 flip/game in m_siege or s_flip_r2 under EITHER policy.

## Stage 1 calibration (PPO 3000, n≈200/cell)
- m_siege: (N,T) grid {3,5,8}x{80,120,160}, seeds 42/43/44. Per cell, gate ORDER:
  (1) per-role skill gates FIRST: role tvr >= 0.80 AND >= +0.15 over that role's
      random-vs-random baseline; a collapsed seed (role tvr < 0.20) triggers ONE
      fresh-seed rerun (45 then 46), never exclusion;
  (2) role bias = |mean Maker win rate - 0.5| <= 0.10 over the 3x3 cross-seed
      role matrix (198 games);
  (3) quota share of Breaker wins >= 0.20; timeout share <= 0.25 of ALL games.
  Tie-break among passing cells: max quota share, then min |bias|.
  Fallback (one registered retry): role-pie (P2 chooses role after move 1).
  KILL: grid + role-pie retry all leave bias > 0.10 -> m_siege dead; campaign CONTINUES
  as s_flip_r2 vs a1 vs a0 under the z_flip_r2 bars below.
- s_flip_r2: pie ON at komi 0.00 first; komi grid 0.05..0.30 step 0.05 fallback; bias <= 0.10.
- One eps=0.25 @ r=2 sensitivity cell on s_flip_r2, DIAGNOSTIC ONLY; pre-bound as the single
  licensed PARTIAL re-parameterization knob.

## Stage 1.5 signal anchor-calibration (before drama becomes a bar)
Per-role drama = mean over plies of sqrt(max(0, loser_progress - winner_progress)) on each
player's OWN normalized progress trace (connection roles: largest-controlled-component span
fraction along own axis; Breaker: max(quota_frac, step_frac)).
Retro-compute on fresh a0/a1 rollout traces + R21 extremes (e1453, 573).
BAR: drama(a1) > drama(a0) AND e1453 not ranked top. FAIL: drama demoted to diagnostic;
screen GO becomes 2/2 of the remaining comparatives.

## Stage 2 screen (PPO 5000, seeds 42/43/44, mirror eval n=200/seed)
Comparative signals, m_siege vs s_flip_r2, with effect-size floors:
1. control_flip_rate (identical r=2 instrumentation all field arms) — floor delta >= 0.5 absolute.
2. game_length centrality in [30,160], center 95 — floor >= 10 turns more central.
3. per-role drama (if anchor-calibrated) — floor delta >= 0.05.
Band-only sanity (NOT comparative): m_siege flip events/game in [1,20] AND
distinct-stones-flipped >= 0.5 x flip events; quota share >= 0.20 and timeout share <= 0.25
RE-ASSERTED at 5000; draw rate <= 0.05 (s/a1/a0 only; m_siege structurally drawless — stated,
not credited); per-role skill gates as Stage 1 with mandatory per-seed inspection;
role/seat bias <= 0.10.
GO: m_siege >= 2/3 comparatives + all bands. STOP RULES: m_siege fails but s_flip_r2 clears
the z_flip_r2 template (>= 3/4 vs a0: lead_changes, game_length, control_flip_rate,
connection_win_fraction >= 0.80) -> blind runs s vs a1 only. Both fail -> NO blind, NO-GO.

## Stage 3 blind (2 independent teams, fresh labels D/V/X, sealed mapping, role-swapped
matches, role-averaged verdicts; fairness-perception probe question in protocol; role win
split logged, flag > 80/20)
- CAMPAIGN VALIDITY: a1 blind mean in [3.9, 4.4]; outside -> CAMPAIGN_UNRESOLVED -> one cheap
  blind replicate, no permanent classification.
- GO: M - A1 >= +1.0 AND M > S with |M - S| >= 0.3.
- PARTIAL: |M - S| < 0.3, or M > S but M - A1 < +1.0 -> exactly one licensed
  re-parameterization: the eps=0.25@r2 cell. Nothing else.
- M <= S: asymmetric-objectives direction RETIRED. S adjudicated under z_flip_r2 grammar:
  S - A1 >= +1.0 reopens the FC family; S <= A1 closes it permanently (validity band guards
  the closure).
- Both NO-GO: registered escalation -> Frontline rebuilt (margin ~1.0, decoupled flip_margin,
  score-margin early-end, double-pass resolves by main score) as the next family.

## Registered follow-on (fires on ANY outcome)
RC2 selection-layer workstream: build measurement-only observer influence field
(generator_v2.py:213-224 zeroes descriptors off-threshold), then QD anchor probe with
within-R21 binary separation bars. GE stays diagnostic-only meanwhile.

Locked constants table: see docs/superpowers/plans/2026-06-10-siege-campaign.md.
Not altered after data.
```

- [ ] **Step 2: Commit**

```bash
git add experiments/siege/PREREGISTRATION.md
git commit -m "prereg(siege): lock arms, gates, signals, floors, decision rule before any training"
```

---

### Task 2: Stage-0a flip-threshold memo on chains

**Files:**
- Create: `experiments/siege/stage0_memo.py`
- Create: `experiments/siege/STAGE0_MEMO.md` (generated by the script + hand-written conclusions)

- [ ] **Step 1: Write the threshold computation script**

Computes flip thresholds from the engine's real kernels (not hand arithmetic — the phase-1.5 memo had a published arithmetic error; this script is the fix).

```python
"""Stage 0a: flip-threshold memo at r=2/d=0.5/eps=0, from the engine's own kernels.

A stone at cell c flips when net opposing field at c exceeds own-side field at c
(control margin 0). Own stone contributes strength*decay^0 = 1.0 at its own cell.
This script measures, on the real W=22 hex_rhombus topology:
  - lone stone: minimum attacker sets (adjacent vs distance-2 mixes)
  - chain-end and chain-interior stones (own-chain support raises the bar)
Writes a markdown table to STAGE0_MEMO.md.

KILL (pre-registered): lone-stone flip needs > 4 coordinated attackers.
"""
from __future__ import annotations
import itertools, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from game_engine.rules import (  # noqa: E402
    PlacementRule, CaptureRule, PropagationRule, WinCondition, TurnStructure,
)
from game_engine.engine_v2 import create_engine  # noqa: E402

W = 22
RADIUS, STRENGTH, DECAY = 2, 1.0, 0.5


def make_game() -> GameDefV2:
    return GameDefV2(
        game_id="stage0_probe", num_dimensions=2, axis_size=W,
        topology_type="hex_rhombus",
        placement_rule=PlacementRule(),
        capture_rule=CaptureRule(capture_type="field_flip"),
        propagation_rule=PropagationRule(
            prop_type="influence", radius=RADIUS, strength=STRENGTH, decay=DECAY),
        win_condition=WinCondition(
            condition_type="field_connection", control_margin=0.0, max_turns=200),
        turn_structure=TurnStructure(),
    )


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

    Searches subsets of cells within radius 2 of the victim, smallest first.
    Returns (count, description-of-distances)."""
    topo = engine.topo
    candidates = [c for c in topo.cells_within_radius(victim, RADIUS)
                  if c != victim and c not in support]
    stones_base = {victim: 1, **support}
    for k in range(1, 8):
        for combo in itertools.combinations(candidates, k):
            stones = dict(stones_base)
            for c in combo:
                stones[c] = 2
            if field_at(engine, victim, stones) < 0.0:
                dists = sorted(topo.distance(victim, c) for c in combo)
                return k, "+".join(f"d{d}" for d in dists)
    return 99, "none<=7"


def main() -> None:
    game = make_game()
    engine = create_engine(game)
    topo = engine.topo
    center = topo.active_cells[len(topo.active_cells) // 2]
    nbrs = [c for c in topo.cells_within_radius(center, 1) if c != center]

    rows = []
    k, desc = min_attackers(engine, center, {})
    rows.append(("lone stone", k, desc))
    k, desc = min_attackers(engine, center, {nbrs[0]: 1})
    rows.append(("chain end (1 own neighbour)", k, desc))
    k, desc = min_attackers(engine, center, {nbrs[0]: 1, nbrs[1]: 1})
    rows.append(("chain interior (2 own neighbours)", k, desc))
    k, desc = min_attackers(engine, center, {nbrs[0]: 1, nbrs[1]: 1, nbrs[2]: 1})
    rows.append(("dense interior (3 own neighbours)", k, desc))

    out = ["# Stage 0a — flip thresholds at r=2/d=0.5/eps=0 (computed from engine kernels)",
           "", "| position | min attackers | distances |", "|---|---|---|"]
    for name, k, desc in rows:
        out.append(f"| {name} | {k} | {desc} |")
    lone = rows[0][1]
    verdict = "PASS" if lone <= 4 else "KILL (lone-stone flip needs > 4 attackers)"
    out += ["", f"**Pre-registered kill check: lone stone needs {lone} attackers -> {verdict}**", ""]
    Path(__file__).with_name("STAGE0_MEMO.md").write_text("\n".join(out))
    print("\n".join(out))
    assert lone <= 4, "STAGE 0a KILL fired"


if __name__ == "__main__":
    main()
```

Note: `PlacementRule()`/`TurnStructure()` defaults — verify the COMMON dict at `experiments/fc_phase15/build_games.py:41-48` and copy its exact placement/turn arguments if defaults differ (place-only, etc.).

- [ ] **Step 2: Run it**

Run: `python experiments/siege/stage0_memo.py`
Expected: table printed, `STAGE0_MEMO.md` written, PASS (analytic expectation: lone stone = 3 attackers with ≥2 adjacent; if KILL fires, STOP THE PLAN and report).

- [ ] **Step 3: Commit**

```bash
git add experiments/siege/stage0_memo.py experiments/siege/STAGE0_MEMO.md
git commit -m "feat(siege): stage-0a flip-threshold memo computed from engine kernels (chains, not lone stones)"
```

---

### Task 3: Engine — new WinCondition fields + serde + hash stability

**Files:**
- Modify: `game_engine/rules.py:210-270` (WinCondition dataclass + serde)
- Test: `test_siege_engine.py` (new, repo root)

- [ ] **Step 1: Write failing tests**

```python
"""SIEGE engine mechanics: asymmetric win fields, quota accounting, timeout_winner."""
import numpy as np

from game_engine.game_def_v2 import GameDefV2
from game_engine.rules import (
    PlacementRule, CaptureRule, PropagationRule, WinCondition, TurnStructure,
)


def _wc_roundtrip(wc: WinCondition) -> WinCondition:
    return WinCondition.from_dict(wc.to_dict())


def test_asym_fields_default_inert_and_roundtrip():
    wc = WinCondition()
    assert wc.condition_type_p2 == ""
    assert wc.capture_quota == 0
    assert wc.timeout_winner == 0
    d = wc.to_dict()
    # defaults omitted from serialized form (legacy-hash stability)
    assert "condition_type_p2" not in d
    assert "capture_quota" not in d
    assert "timeout_winner" not in d
    wc2 = WinCondition(condition_type="field_connection",
                       condition_type_p2="capture_quota",
                       capture_quota=5, timeout_winner=2)
    back = _wc_roundtrip(wc2)
    assert back.condition_type_p2 == "capture_quota"
    assert back.capture_quota == 5
    assert back.timeout_winner == 2


def test_legacy_canonical_hash_unchanged():
    # A legacy game's canonical hash must be identical before/after this change.
    # Golden hash captured on main (pre-SIEGE) — see Step 2 for capture command.
    g = GameDefV2(
        game_id="legacy_probe", num_dimensions=2, axis_size=9,
        placement_rule=PlacementRule(), capture_rule=CaptureRule(),
        propagation_rule=PropagationRule(), win_condition=WinCondition(),
        turn_structure=TurnStructure(),
    )
    assert g.canonical_hash() == GOLDEN_LEGACY_HASH
```

- [ ] **Step 2: Capture the golden hash on main, then run tests to verify failure**

```bash
git stash && git checkout main
python -c "
from game_engine.game_def_v2 import GameDefV2
from game_engine.rules import *
g = GameDefV2(game_id='legacy_probe', num_dimensions=2, axis_size=9,
    placement_rule=PlacementRule(), capture_rule=CaptureRule(),
    propagation_rule=PropagationRule(), win_condition=WinCondition(),
    turn_structure=TurnStructure())
print(g.canonical_hash())
"
git checkout siege-campaign && git stash pop
```

Paste the printed hash as `GOLDEN_LEGACY_HASH = "..."` at the top of `test_siege_engine.py`.

Run: `python -m pytest test_siege_engine.py -v`
Expected: FAIL — `WinCondition` has no attribute `condition_type_p2`.

- [ ] **Step 3: Implement**

In `game_engine/rules.py`, add to the `WinCondition` dataclass (after `control_margin`):

```python
    # SIEGE (pivot campaign): asymmetric P2 win condition. "" = symmetric/legacy.
    # Only "capture_quota" is valid; NOT in WIN_CONDITION_TYPES (never generated).
    condition_type_p2: str = ""
    capture_quota: int = 0    # distinct-flip ticks Breaker needs (capture_quota only)
    timeout_winner: int = 0   # 0 = legacy tiebreak at max turns; 1/2 = that player wins
```

In `WinCondition.to_dict()`, mirror the `control_margin` omit-default pattern (rules.py:257-258):

```python
        if self.condition_type_p2:
            d["condition_type_p2"] = self.condition_type_p2
        if self.capture_quota:
            d["capture_quota"] = self.capture_quota
        if self.timeout_winner:
            d["timeout_winner"] = self.timeout_winner
```

In `from_dict()`, read with defaults: `condition_type_p2=d.get("condition_type_p2", "")`, `capture_quota=int(d.get("capture_quota", 0))`, `timeout_winner=int(d.get("timeout_winner", 0))`. If `WinCondition` has a `__post_init__`/validator, add: `condition_type_p2 in ("", "capture_quota")` else raise `ValueError`.

- [ ] **Step 4: Run tests**

Run: `python -m pytest test_siege_engine.py -v` → PASS.
Run: `python -m pytest test_canonical_blob.py test_*.py -q` → all 242 legacy tests PASS.

- [ ] **Step 5: Commit**

```bash
git add game_engine/rules.py test_siege_engine.py
git commit -m "feat(engine): asymmetric win fields condition_type_p2/capture_quota/timeout_winner — default-inert, hash-stable"
```

---

### Task 4: Engine — timeout_winner

**Files:**
- Modify: `game_engine/engine_v2.py:1364` (`_end_by_max_turns`)
- Test: `test_siege_engine.py`

- [ ] **Step 1: Write failing test**

Append to `test_siege_engine.py` (helper used by later tasks too):

```python
from game_engine.engine_v2 import create_engine


def make_siege(quota: int = 3, max_turns: int = 12, axis: int = 7) -> GameDefV2:
    return GameDefV2(
        game_id="m_siege_test", num_dimensions=2, axis_size=axis,
        topology_type="hex_rhombus",
        placement_rule=PlacementRule(),
        capture_rule=CaptureRule(capture_type="field_flip"),
        propagation_rule=PropagationRule(prop_type="influence",
                                         radius=2, strength=1.0, decay=0.5),
        win_condition=WinCondition(condition_type="field_connection",
                                   condition_type_p2="capture_quota",
                                   capture_quota=quota, timeout_winner=2,
                                   target_dimension=0, control_margin=0.0,
                                   max_turns=max_turns),
        turn_structure=TurnStructure(),
    )


def test_timeout_winner_awards_breaker():
    game = make_siege(quota=99, max_turns=6)
    engine = create_engine(game)
    engine.reset()
    rng = np.random.default_rng(0)
    while not engine.done:
        legal = engine.get_legal_actions()
        engine.step(int(rng.choice(legal)))
    assert engine._ended_by_max_turns
    assert engine._winner == 2  # Breaker wins at the cap, not majority tiebreak


def test_timeout_winner_zero_keeps_legacy_tiebreak():
    game = make_siege(quota=99, max_turns=6)
    game.win_condition.timeout_winner = 0
    game.win_condition.condition_type_p2 = ""  # fully legacy field_connection
    engine = create_engine(game)
    engine.reset()
    rng = np.random.default_rng(0)
    while not engine.done:
        engine.step(int(rng.choice(engine.get_legal_actions())))
    # legacy path: controlled-cell tiebreak (winner may be 1, 2, or None — just
    # assert the new branch did not fire by checking the game is decided by counts)
    assert engine._ended_by_max_turns
```

Note: `make_siege` exercises the not-yet-built asymmetric dispatch; if `_check_win_conditions` raises on the unknown combination before Task 5, set quota=99 (unreachable) so only the timeout path runs — if it still raises, mark `test_timeout_winner_awards_breaker` with `pytest.mark.xfail(strict=False)` until Task 5 lands, then remove the mark.

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest test_siege_engine.py::test_timeout_winner_awards_breaker -v`
Expected: FAIL (winner from majority tiebreak / dispatch error, not 2).

- [ ] **Step 3: Implement**

At the top of `_end_by_max_turns()` (engine_v2.py:1364), immediately after `self._ended_by_max_turns = True`:

```python
        tw = getattr(self.game.win_condition, "timeout_winner", 0)
        if tw:
            self.done = True
            self._winner = tw
            return
```

- [ ] **Step 4: Run tests** — siege tests PASS, full suite `python -m pytest test_*.py -q` PASS (242 + new).

- [ ] **Step 5: Commit**

```bash
git add game_engine/engine_v2.py test_siege_engine.py
git commit -m "feat(engine): timeout_winner — designated player wins at turn cap (gated, legacy tiebreak untouched)"
```

---

### Task 5: Engine — quota accounting (distinct stones, per-move tick cap)

**Files:**
- Modify: `game_engine/engine_v2.py:905-933` (`_capture_field_flip`), engine `__init__`/`reset`
- Test: `test_siege_engine.py`

- [ ] **Step 1: Write failing tests**

```python
def _place_stones(engine, stones: dict[int, int]) -> None:
    """Test helper: paint stones directly and recompute the field."""
    for c, owner in stones.items():
        engine.board_owners[c] = owner
        engine.piece_counts[owner - 1] += 1
    engine._recompute_field()


def test_quota_ticks_on_breaker_flip_distinct_and_capped():
    game = make_siege(quota=10, max_turns=200, axis=9)
    engine = create_engine(game)
    engine.reset()
    assert engine._quota_ticks == 0 and engine._quota_cells == set()
    topo = engine.topo
    center = topo.active_cells[len(topo.active_cells) // 2]
    nbrs = [c for c in topo.cells_within_radius(center, 1) if c != center]
    # Maker lone stone at center; Breaker has 2 adjacent attackers; Breaker to move.
    _place_stones(engine, {center: 1, nbrs[0]: 2, nbrs[1]: 2})
    engine.current_player = 2
    third = nbrs[2]
    engine._handle_placement_for_test = None  # marker: use engine.step if available
    # Drive the third attacker through the real step path:
    engine.step(third)
    assert engine.board_owners[center] == 2          # flipped
    assert engine._quota_cells == {center}
    assert engine._quota_ticks == 1


def test_quota_no_tick_for_maker_flips_or_repeat_cells():
    game = make_siege(quota=10, max_turns=200, axis=9)
    engine = create_engine(game)
    engine.reset()
    topo = engine.topo
    center = topo.active_cells[len(topo.active_cells) // 2]
    nbrs = [c for c in topo.cells_within_radius(center, 1) if c != center]
    # Breaker stone surrounded by Maker attackers; Maker to move -> Maker flip, no tick.
    _place_stones(engine, {center: 2, nbrs[0]: 1, nbrs[1]: 1})
    engine.current_player = 1
    engine.step(nbrs[2])
    assert engine.board_owners[center] == 1
    assert engine._quota_ticks == 0
    # Now Breaker re-flips the SAME cell: ticks once; a later re-flip of the
    # same cell after another Maker reflip must NOT tick again (distinct cells).
```

(If `engine.step(cell)` is not the raw placement API — check `get_legal_actions()` mapping; phase-1.5 tests in `test_field_capture_phase15.py` show the exact pattern for driving placements in tests. Mirror that pattern verbatim; the assertions above are the contract.)

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest test_siege_engine.py -k quota -v`
Expected: FAIL — engine has no `_quota_ticks`.

- [ ] **Step 3: Implement**

Module-level constant near the top of engine_v2.py:

```python
QUOTA_TICK_CAP_PER_MOVE = 2  # SIEGE anti-cascade-burst cap (prereg-locked)
```

In engine `__init__` (next to the end-cause flags at ≈158–167) and in `reset()`:

```python
        # SIEGE quota accounting (inert unless condition_type_p2 == "capture_quota")
        self._quota_ticks: int = 0
        self._quota_cells: set[int] = set()
```

In `_capture_field_flip` (905–933): accumulate every flipped cell across cascade iterations into a local `flipped_all: list[int]`, then after the while-loop, before `self._field_dirty = True`:

```python
        if (
            mover == 2
            and getattr(self.game.win_condition, "condition_type_p2", "")
            == "capture_quota"
        ):
            new_cells = [c for c in flipped_all if c not in self._quota_cells]
            self._quota_cells.update(new_cells)
            self._quota_ticks += min(len(new_cells), QUOTA_TICK_CAP_PER_MOVE)
```

(`mover` already exists in the function. The branch is string-gated → legacy flips untouched.)

- [ ] **Step 4: Run tests** — quota tests PASS; `python -m pytest test_field_capture_phase15.py test_*.py -q` all PASS (phase-1.5 C1 flip semantics must be bit-identical).

- [ ] **Step 5: Commit**

```bash
git add game_engine/engine_v2.py test_siege_engine.py
git commit -m "feat(engine): capture_quota accounting — distinct-cell ticks, per-move cap 2, Breaker-only, string-gated"
```

---

### Task 6: Engine — asymmetric win dispatch

**Files:**
- Modify: `game_engine/engine_v2.py:1188` (`_check_win_conditions`) + new `_check_win_asymmetric`
- Test: `test_siege_engine.py`

- [ ] **Step 1: Write failing tests**

```python
def test_maker_wins_by_connection_quota_incomplete():
    game = make_siege(quota=99, max_turns=200, axis=5)
    engine = create_engine(game)
    engine.reset()
    topo = engine.topo
    # Maker stones spanning axis 0 (a full column of the 5x5 rhombus):
    col = [c for c in topo.active_cells][:0]  # replaced below by real span cells
    # Build the span by placement through step(): alternate Maker placements along
    # one axis-0 line with Breaker placements far away. Mirror the span-construction
    # helper used in test_field_connection.py (existing field_connection win tests)
    # — reuse its cell-selection code verbatim.
    ...
    assert engine.done and engine._winner == 1


def test_breaker_wins_at_quota():
    game = make_siege(quota=1, max_turns=200, axis=9)
    engine = create_engine(game)
    engine.reset()
    topo = engine.topo
    center = topo.active_cells[len(topo.active_cells) // 2]
    nbrs = [c for c in topo.cells_within_radius(center, 1) if c != center]
    _place_stones(engine, {center: 1, nbrs[0]: 2, nbrs[1]: 2})
    engine.current_player = 2
    engine.step(nbrs[2])  # third attacker -> flip -> tick 1 >= quota 1
    assert engine.done and engine._winner == 2


def test_breaker_connection_is_irrelevant():
    # Breaker spanning their axis must NOT win (P2's only wins are quota/timeout).
    game = make_siege(quota=99, max_turns=200, axis=5)
    # build a Breaker span via _place_stones, then trigger a win check via a
    # neutral Maker placement; assert engine not done.
```

For `test_maker_wins_by_connection_quota_incomplete` and `test_breaker_connection_is_irrelevant`: open `test_field_connection.py` (repo root) and copy its span-construction approach exactly — it already solves "place a connected controlled span across faces" for field_connection games. Do not invent a new construction.

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest test_siege_engine.py -k "maker or breaker" -v`
Expected: FAIL — symmetric `_check_field_connection` awards Breaker connection wins / quota never checked.

- [ ] **Step 3: Implement**

In `_check_win_conditions()` (1188), insert before `ctype = wc.condition_type` branching:

```python
        if getattr(wc, "condition_type_p2", ""):
            self._check_win_asymmetric(wc)
            return
```

New method (place next to `_check_field_connection`):

```python
    def _check_win_asymmetric(self, wc) -> None:
        """SIEGE dispatch: P1's win is wc.condition_type checked for P1 ONLY
        (field_connection); P2's win is wc.condition_type_p2 (capture_quota).
        The mover's condition is checked first so one step never awards both.
        Timeout is handled separately by _end_by_max_turns/timeout_winner."""
        margin = getattr(wc, "control_margin", 0.0)
        controlled_p1 = {
            c for c in self.topo.active_cells if self.board_values[c] > margin
        }
        p1_win = self.topo.connects_faces(controlled_p1, wc.target_dimension)
        p2_win = (
            wc.condition_type_p2 == "capture_quota"
            and wc.capture_quota > 0
            and self._quota_ticks >= wc.capture_quota
        )
        order = (1, 2) if self.current_player == 1 else (2, 1)
        for p in order:
            if (p == 1 and p1_win) or (p == 2 and p2_win):
                self._winner = p
                self.done = True
                return
```

(No `_goals_swapped` handling: m_siege is pie-OFF by prereg; role-pie fallback, if ever licensed, is a separate registered change.)

- [ ] **Step 4: Run tests** — all siege tests PASS; full suite PASS.

- [ ] **Step 5: Commit**

```bash
git add game_engine/engine_v2.py test_siege_engine.py
git commit -m "feat(engine): asymmetric win dispatch — P1-only field_connection + P2 capture_quota, mover-first precedence"
```

---

### Task 7: Engine — gated quota_frac observation

**Files:**
- Modify: `game_engine/engine_v2.py:1463-1491` (`_observe`), `game_engine/game_def_v2.py:92-99` (`state_dim`)
- Test: `test_siege_engine.py`

- [ ] **Step 1: Write failing tests**

```python
def test_state_dim_and_obs_gated():
    legacy = GameDefV2(
        game_id="legacy_dim", num_dimensions=2, axis_size=9,
        placement_rule=PlacementRule(), capture_rule=CaptureRule(),
        propagation_rule=PropagationRule(), win_condition=WinCondition(),
        turn_structure=TurnStructure(),
    )
    assert legacy.state_dim == legacy.total_cells * 2 + 3  # unchanged
    siege = make_siege(quota=4)
    assert siege.state_dim == siege.total_cells * 2 + 4   # +1 quota_frac only
    engine = create_engine(siege)
    obs = engine.reset()
    assert obs.shape == (siege.state_dim,)
    assert obs[-1] == 0.0  # quota_frac starts at 0
    engine._quota_ticks = 2
    obs2 = engine._observe()
    assert abs(obs2[-1] - 0.5) < 1e-12  # 2/4
```

- [ ] **Step 2: Run to verify failure** — `python -m pytest test_siege_engine.py -k state_dim -v` → FAIL.

- [ ] **Step 3: Implement**

`game_def_v2.py` `state_dim` property:

```python
        extra = (
            1
            if getattr(self.win_condition, "condition_type_p2", "") == "capture_quota"
            else 0
        )
        return self.total_cells * 2 + 3 + extra
```

`engine_v2.py` `_observe()` — build metadata as a list, append conditionally before the concatenate at 1490:

```python
        metadata = [step_frac, own_frac, enemy_frac]
        wc = self.game.win_condition
        if getattr(wc, "condition_type_p2", "") == "capture_quota":
            q = wc.capture_quota
            metadata.append(self._quota_ticks / q if q > 0 else 0.0)
        metadata = np.array(metadata, dtype=np.float64)
```

(clock_frac is NOT added: `step_frac` at metadata[0] is already exactly `step_count / max_game_steps` — the skeleton's clock. Recorded in PREREGISTRATION.)

- [ ] **Step 4: Run tests** — PASS; full suite PASS (legacy dims untouched → all training/eval regression green).

- [ ] **Step 5: Commit**

```bash
git add game_engine/engine_v2.py game_engine/game_def_v2.py test_siege_engine.py
git commit -m "feat(engine): gated quota_frac observation float (+1 state_dim for capture_quota games only)"
```

---

### Task 8: Legacy regression sweep

**Files:** none new.

- [ ] **Step 1: Full suite**

Run: `python -m pytest test_*.py -q`
Expected: 242 legacy + ~10 new siege tests, ALL PASS (the known `test_ca_integration` collection artifact excepted, as on main).

- [ ] **Step 2: Hash spot-check against main**

```bash
python - <<'EOF'
import json, glob
from game_engine.game_def_v2 import GameDefV2
for p in sorted(glob.glob("experiments/fc_phase15/games/calibrated/*.json")):
    g = GameDefV2.from_dict(json.load(open(p)))
    print(p, g.canonical_hash()[:16])
EOF
```

Compare the four hashes against the same command run on `main` (git stash / checkout main / run / return). Expected: identical.

- [ ] **Step 3: Commit (only if any fix was needed); otherwise proceed**

---

### Task 9: build_games.py + scripted chain-builder + Stage-0b smoke

**Files:**
- Create: `experiments/siege/build_games.py`
- Create: `experiments/siege/scripted_agents.py`
- Create: `experiments/siege/games/` (output dir)

- [ ] **Step 1: Write scripted_agents.py**

```python
"""Deterministic scripted policies for Stage-0b smoke (pre-registered).

ChainBuilder (Maker-shaped): always extends own largest controlled component
toward the far face of the target axis. FlipHunter (Breaker-shaped): plays the
empty cell with maximum kernel pressure onto enemy stones. Both break ties by
lowest cell index. These test flip-firing against connection-shaped play, not
random stragglers (graft 6)."""
from __future__ import annotations
import numpy as np


class ChainBuilder:
    def __init__(self, player: int, axis: int = 0):
        self.player, self.axis = player, axis

    def select_action(self, obs, legal_actions, deterministic=True):
        return self._pick(self.engine, legal_actions), None, None

    def bind(self, engine):
        self.engine = engine
        return self

    def _pick(self, engine, legal):
        topo, W = engine.topo, engine.game.axis_size
        own = [c for c in topo.active_cells
               if engine.board_owners[c] == self.player]
        def axis_coord(cell):  # hex_rhombus is a W x W rhombus, row-major
            return cell // W if self.axis == 0 else cell % W
        target = max((axis_coord(c) for c in own), default=-1) + 1
        best, best_key = None, None
        for a in legal:
            adj = any(topo.distance(a, c) == 1 for c in own) if own else True
            key = (0 if adj else 1, abs(axis_coord(a) - target), a)
            if best_key is None or key < best_key:
                best, best_key = a, key
        return best


class FlipHunter:
    def __init__(self, player: int):
        self.player = player

    def bind(self, engine):
        self.engine = engine
        return self

    def select_action(self, obs, legal_actions, deterministic=True):
        engine, enemy = self.engine, 3 - self.player
        topo = engine.topo
        decay = engine.game.propagation_rule.decay
        radius = engine.game.propagation_rule.radius
        best, best_p = None, -1.0
        for a in legal_actions:
            p = sum(
                decay ** topo.distance(a, c)
                for c in topo.cells_within_radius(a, radius)
                if engine.board_owners[c] == enemy
            )
            if p > best_p or (p == best_p and (best is None or a < best)):
                best, best_p = a, p
        return best, None, None
```

(Verify the agent interface — `select_action(obs, legal_actions=..., deterministic=...)` returning a 3-tuple — against `RandomAgent` in `training/` and the `instrumented_episode` call at `experiments/fc_phase15/run_screen.py:84-87`; adjust signatures to match exactly.)

- [ ] **Step 2: Write build_games.py**

Copy the structure of `experiments/fc_phase15/build_games.py` (COMMON at 41–48, smoke at the bottom) and define:

```python
GRID_N = (3, 5, 8)
GRID_T = (80, 120, 160)

def build_m(n: int, t: int) -> GameDefV2:
    return GameDefV2(
        game_id=f"m_siege_N{n}_T{t}", **COMMON,           # hex_rhombus W=22, place-only
        capture_rule=CaptureRule(capture_type="field_flip"),
        propagation_rule=PropagationRule(prop_type="influence",
                                         radius=2, strength=1.0, decay=0.5),
        win_condition=WinCondition(condition_type="field_connection",
                                   condition_type_p2="capture_quota",
                                   capture_quota=n, timeout_winner=2,
                                   target_dimension=0, control_margin=0.0,
                                   max_turns=t),
        pie_rule=False, komi_p2=0.0,
    )

def build_s() -> GameDefV2:
    # a1_field_connect + field_flip capture; pie ON, komi 0 (calibration adjusts)
    a1 = load(CAL_DIR / "a1_field_connect.json")
    a1.game_id = "s_flip_r2"
    a1.capture_rule = CaptureRule(capture_type="field_flip")
    a1.komi_p2 = 0.0
    return a1
```

COMMON: lift verbatim from `experiments/fc_phase15/build_games.py:41-48` minus the fields overridden above (note their FIELD dict is r=1 and WIN margin=0.25 — ours are r=2 and margin 0.0; the COMMON board/placement/turn parts carry over unchanged). A0/A1: copy the two JSONs from `experiments/fc_phase15/games/calibrated/` into `experiments/siege/games/` unmodified.

`main()` writes one mid-grid M smoke config (`m_siege_N5_T120`) plus all 9 grid variants to `games/`, then runs Stage-0b smoke:

```python
def smoke(game, n_random=1000, n_scripted=200, seed=7):
    """Random + scripted rollouts; counts flips (piece-count drops attributed to
    the mover), distinct quota cells, end causes, flip locus. Asserts the
    pre-registered Stage-0b kill: >= 1 flip/game under EITHER policy."""
```

— mirror `smoke()` in fc_phase15/build_games.py for the counting loop (prev_counts pattern from run_screen.py:58-109), add `engine._quota_cells` readout for M, and scripted games as `ChainBuilder(player=1).bind(engine)` vs `FlipHunter(player=2).bind(engine)` (and the reverse pairing for S). Print a table; `assert flips_per_game >= 1.0` for m_siege_N5_T120 and s_flip_r2 under at least one policy each (the pre-registered kill is "< 1 under EITHER" → assert max(random, scripted) ≥ 1.0).

- [ ] **Step 3: Run it**

Run: `python experiments/siege/build_games.py`
Expected: 9 M JSONs + s_flip_r2.json + a0/a1 copies in `experiments/siege/games/`; smoke table printed; kill assertions pass. If a kill fires: STOP, report (this is a registered NO-GO, not a bug to fix).

- [ ] **Step 4: Commit**

```bash
git add experiments/siege/build_games.py experiments/siege/scripted_agents.py experiments/siege/games/
git commit -m "feat(siege): M (N,T) grid + S/A1/A0 arm configs + stage-0b smoke (random + chain-builder rollouts, flip-locus logged)"
```

---

### Task 10: metrics.py — per-role progress traces + drama

**Files:**
- Create: `experiments/siege/metrics.py`
- Test: `experiments/siege/test_siege_metrics.py`

- [ ] **Step 1: Write failing tests**

```python
import numpy as np
from experiments.siege.metrics import winner_behindness, maker_progress_span

def test_winner_behindness_basic():
    # winner always ahead -> 0 drama
    assert winner_behindness([0.5, 0.8], [0.1, 0.2]) == 0.0
    # winner behind by 0.25 then 0.0 -> mean(sqrt(0.25), 0) = 0.25
    assert abs(winner_behindness([0.25, 0.6], [0.5, 0.5]) - 0.25) < 1e-12

def test_winner_behindness_empty():
    assert winner_behindness([], []) == 0.0
```

(`maker_progress_span` is tested via an engine fixture: paint a 3-cell axis-0 chain on a 5×5 rhombus, assert span fraction == 3/5.)

- [ ] **Step 2: Run to verify failure** — `python -m pytest experiments/siege/test_siege_metrics.py -v` → FAIL (module missing).

- [ ] **Step 3: Implement**

```python
"""SIEGE screen metrics (pre-registered Stage 1.5/2 definitions).

Per-role progress traces, both normalized to [0,1]:
  - connection roles: span fraction along own target axis of the largest
    connected controlled component (control at the game's margin);
  - Breaker: max(quota_frac, step_frac) — quota and clock are both win paths.
Per-role drama = mean over plies of sqrt(max(0, loser_prog - winner_prog)).
"""
from __future__ import annotations
import numpy as np


def winner_behindness(winner_trace, loser_trace) -> float:
    if not len(winner_trace):
        return 0.0
    w = np.asarray(winner_trace, dtype=np.float64)
    l = np.asarray(loser_trace, dtype=np.float64)
    return float(np.mean(np.sqrt(np.maximum(0.0, l - w))))


def _controlled_cells(engine, player: int, margin: float) -> set[int]:
    sign = 1.0 if player == 1 else -1.0
    return {c for c in engine.topo.active_cells
            if sign * engine.board_values[c] > margin}


def _components(topo, cells: set[int]) -> list[set[int]]:
    seen, comps = set(), []
    for start in cells:
        if start in seen:
            continue
        comp, stack = set(), [start]
        while stack:
            c = stack.pop()
            if c in comp:
                continue
            comp.add(c)
            stack.extend(n for n in topo.cells_within_radius(c, 1)
                         if n in cells and n not in comp)
        seen |= comp
        comps.append(comp)
    return comps


def maker_progress_span(engine, player: int, axis: int, margin: float) -> float:
    """Span fraction along `axis` of the largest controlled component."""
    W = engine.game.axis_size
    cells = _controlled_cells(engine, player, margin)
    if not cells:
        return 0.0
    comps = _components(engine.topo, cells)
    big = max(comps, key=len)
    coords = {(c // W) if axis == 0 else (c % W) for c in big}
    return len(coords) / W


def breaker_progress(engine) -> float:
    wc = engine.game.win_condition
    q = wc.capture_quota
    quota_frac = engine._quota_ticks / q if q > 0 else 0.0
    step_frac = engine.step_count / engine.game.max_game_steps
    return max(quota_frac, step_frac)
```

Before finalizing `_components`/`maker_progress_span`, read `experiments/field_connect_probe/metrics.py` (92 lines — has `largest_component`, `controlled_sets`, `progress_diff_field`): if its component/progress internals match this contract, import and reuse them instead of duplicating; keep `winner_behindness` and `breaker_progress` here either way. Verify the cell→coordinate arithmetic (`c // W`, `c % W`) against `game_engine/topology.py`'s hex_rhombus indexing; if the topology exposes a coordinate accessor, use it.

- [ ] **Step 4: Run tests** — PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/siege/metrics.py experiments/siege/test_siege_metrics.py
git commit -m "feat(siege): per-role progress traces + sqrt-deficit winner-behindness drama + tests"
```

---

### Task 11: Role-matrix eval + calibrate.py

**Files:**
- Create: `experiments/siege/eval_roles.py`
- Create: `experiments/siege/calibrate.py`
- Test: `experiments/siege/test_siege_metrics.py` (bias math only)

- [ ] **Step 1: Write the failing bias-math test**

```python
from experiments.siege.eval_roles import role_bias_from_matrix

def test_role_bias_from_matrix():
    # 3x3 matrix of Maker win rates; bias = |mean - 0.5|
    m = [[0.6, 0.5, 0.55], [0.45, 0.5, 0.5], [0.5, 0.55, 0.4]]
    assert abs(role_bias_from_matrix(m) - abs(np.mean(m) - 0.5)) < 1e-12
```

- [ ] **Step 2: Run to verify failure**, then **Step 3: Implement eval_roles.py**

```python
"""Cross-seed role-matrix evaluation for asymmetric arms (prereg Stage 1).

Trains are done by the caller; this module plays Maker(seed_i) vs
Breaker(seed_j) for all (i,j) pairs and reports the matrix plus per-role
baseline-adjusted skill gates.
"""
from __future__ import annotations
import numpy as np

GAMES_PER_PAIR = 22  # 3x3 x 22 = 198 ~= 200 (prereg)


def role_bias_from_matrix(matrix) -> float:
    return float(abs(np.mean(np.asarray(matrix, dtype=np.float64)) - 0.5))


def play_pair(game, maker_agent, breaker_agent, n=GAMES_PER_PAIR) -> float:
    """Maker win rate over n games (roles are seats: maker=P1, breaker=P2)."""
    from game_engine.engine_v2 import create_engine
    wins = 0
    engine = create_engine(game)
    for _ in range(n):
        obs = engine.reset()
        agents = [maker_agent, breaker_agent]
        while not engine.done:
            legal = engine.get_legal_actions()
            a = agents[engine.get_current_player()]
            action, _, _ = a.select_action(obs, legal_actions=legal,
                                           deterministic=False)
            obs, _, _, _ = engine.step(action)
        if engine._winner == 1:
            wins += 1
    return wins / n


def role_matrix(game, trainers) -> list[list[float]]:
    """trainers: list of 3 trained SelfPlayTrainer (one per seed)."""
    return [
        [play_pair(game, ti.agents[0], tj.agents[1]) for tj in trainers]
        for ti in trainers
    ]


def per_role_tvr(game, trainer, random_agent, n=100) -> dict:
    """Role-aware tvr + random-vs-random baseline (fixes the vacuous gate)."""
    from game_engine.engine_v2 import create_engine
    def wr(p1_agent, p2_agent, want):
        engine = create_engine(game)
        w = 0
        for _ in range(n):
            obs = engine.reset()
            agents = [p1_agent, p2_agent]
            while not engine.done:
                legal = engine.get_legal_actions()
                a = agents[engine.get_current_player()]
                action, _, _ = a.select_action(obs, legal_actions=legal,
                                               deterministic=True)
                obs, _, _, _ = engine.step(action)
            if engine._winner == want:
                w += 1
        return w / n
    base_maker = wr(random_agent, random_agent, 1)
    base_breaker = wr(random_agent, random_agent, 2)
    maker = wr(trainer.agents[0], random_agent, 1)
    breaker = wr(random_agent, trainer.agents[1], 2)
    return dict(
        maker_tvr=maker, breaker_tvr=breaker,
        maker_baseline=base_maker, breaker_baseline=base_breaker,
        maker_pass=(maker >= 0.80 and maker - base_maker >= 0.15),
        breaker_pass=(breaker >= 0.80 and breaker - base_breaker >= 0.15),
        collapsed=(maker < 0.20 or breaker < 0.20),
    )
```

(RandomAgent import: same one trainer.py uses — find it via `rg "class RandomAgent" training/`.)

- [ ] **Step 4: Write calibrate.py**

Structure copied from `experiments/fc_phase15/calibrate.py` (argparse, BIAS_PASS=0.10, report writing), with the M-grid logic:

```python
# Per (N, T) cell, prereg gate ORDER:
# 1. train seeds (42,43,44) at --budget 3000; per_role_tvr each; if collapsed:
#    retrain ONCE with reserve seed (45 then 46) replacing the collapsed one.
#    Any seed still failing skill gates after rerun -> cell INVALID (loud skip).
# 2. role_matrix(...) over the 3 trainers -> bias; PASS iff bias <= 0.10.
# 3. quota_share = quota_wins / max(1, breaker_wins) >= 0.20 over matrix games;
#    timeout_share = timeout_games / all_games <= 0.25.
#    (instrument play_pair to also return end-cause tallies — extend its return
#    to (maker_wr, dict(quota_wins=, timeout_games=, n=)) and aggregate.)
# Winner cell: max quota_share, then min bias. Writes:
#   games/calibrated/m_siege.json  (the winning (N,T) config)
#   calibration.md                 (full grid table + verdicts)
# S arm: pie ON komi 0.0 first; komi grid 0.05..0.30 fallback (copy the
# fc_phase15 komi loop verbatim, BIAS_PASS 0.10, smallest passing komi).
# Plus one eps=0.25 sensitivity cell on S: train 1 seed, report metrics,
# DIAGNOSTIC ONLY (markdown section, no gate).
# Role-pie fallback is NOT implemented here — it is a registered retry that
# would come back through the plan if the grid fails (YAGNI now).
```

Write it fully (≈150 lines), following fc_phase15/calibrate.py's arg/report conventions: `--budget 3000 --eval-episodes 200 --seeds 42,43,44 --arm m|s|all`.

- [ ] **Step 5: Run unit tests + a 1-cell dry run**

Run: `python -m pytest experiments/siege/test_siege_metrics.py -v` → PASS.
Dry run: `python experiments/siege/calibrate.py --arm m --grid-cells N5_T120 --budget 200 --eval-episodes 20` (add `--grid-cells` filter + tiny budget for smoke; NOT a real calibration) → completes, writes a grid-table row, no crash.

- [ ] **Step 6: Commit**

```bash
git add experiments/siege/eval_roles.py experiments/siege/calibrate.py experiments/siege/test_siege_metrics.py
git commit -m "feat(siege): role-matrix eval + (N,T) calibration grid with tvr-before-bias ordering and collapsed-seed rerun"
```

---

### Task 12: Stage-1.5 drama anchor-calibration

**Files:**
- Create: `experiments/siege/anchor_drama.py`

- [ ] **Step 1: Locate the R21 extreme game configs**

Run: `rg -l "e1453" --glob "*.json" evaluations/ experiments/ games/ 2>/dev/null; rg -l "573562833174" --glob "*.json" evaluations/ experiments/ games/ 2>/dev/null`
Expected: JSON config paths for both R21 games (check `evaluations/run21/` first). Record the two paths as constants in the script. If configs are not on disk as JSON, extract them from wherever run21 eval loaded games (check `evaluations/run21/` helpers) — this is a hard prerequisite, surface loudly if missing.

- [ ] **Step 2: Write anchor_drama.py**

```python
"""Stage 1.5: anchor-calibrate per-role drama BEFORE it becomes a screen bar.

Retro-computes drama on fresh rollout traces (random + greedy, n=200 each) for:
a0_baseline, a1_field_connect, e1453 (R21 GE-top), 573... (R21 GE-bottom).
BAR (prereg): drama(a1) > drama(a0) AND e1453 NOT ranked top of the four.
FAIL -> print DEMOTED: drama becomes diagnostic; screen GO = 2/2 remaining.
"""
```

Per game: roll n games (RandomAgent pairs, then the greedy agent pair used by trainer.evaluate — see `training/trainer.py:661-686` GreedyAgent usage), record per-ply progress traces using `metrics.py` (`maker_progress_span` for connection/field games on both players; threshold-race progress for a0/legacy: effective score / threshold — lift `progress_diff_threshold`'s internals from `experiments/field_connect_probe/metrics.py` and split per player). Compute `winner_behindness` per game (skip draws), report mean drama per game config, apply the BAR, write `anchor_drama.md`.

- [ ] **Step 3: Run on a0/a1 only as a smoke** (n=20): `python experiments/siege/anchor_drama.py --n 20 --games a0,a1` → table prints, no crash. (Full run with the R21 extremes is an execution-stage step.)

- [ ] **Step 4: Commit**

```bash
git add experiments/siege/anchor_drama.py
git commit -m "feat(siege): stage-1.5 drama anchor-calibration harness (a0/a1 + R21 extremes, demote-on-fail)"
```

---

### Task 13: run_screen.py — 4-arm mechanical screen

**Files:**
- Create: `experiments/siege/run_screen.py`

- [ ] **Step 1: Write it**

Copy `experiments/fc_phase15/run_screen.py` wholesale and modify:

1. Arms: `["m_siege", "s_flip_r2", "a1_field_connect", "a0_baseline"]`, loaded from `experiments/siege/games/calibrated/` (m_siege, s_flip_r2) and `games/` (a0/a1 copies); loud-skip any missing calibration file (BIAS_UNRESOLVED pattern, lines 159–168 of the original).
2. `instrumented_episode`: keep the existing per-ply loop (58–109) and add:
   - attribute piece-count drops to the mover (`engine.get_current_player()` read BEFORE `step`) → `breaker_flip_events` (P1 drops on Breaker moves) for m_siege;
   - per-ply per-role progress traces (`maker_progress_span` both players for symmetric arms; maker span + `breaker_progress` for m_siege);
   - end-cause tallies: quota win (`engine._winner == 2 and engine._quota_ticks >= quota`), timeout (`engine._ended_by_max_turns`), connection win;
   - `distinct_flips = len(engine._quota_cells)` for m_siege;
   - for m_siege there is NO seat swap (roles are fixed) — eval all 200 episodes with agents[0]=Maker, agents[1]=Breaker; symmetric arms keep the existing seat-swap halves.
3. Aggregation adds: `per_role_drama` (mean winner_behindness), `quota_share`, `timeout_share`, `flip_events`, `distinct_flip_ratio = distinct_flips / max(1, flip_events)`.
4. Bars section (replace 182–243) — apply PREREGISTRATION verbatim:

```python
COMPARATIVE = [  # m_siege vs s_flip_r2, with effect-size floors
    ("control_flip_rate", lambda m, s: m - s >= 0.5),
    ("game_length", lambda m, s: centrality_gain(m, s) >= 10),  # toward center 95 in [30,160]
    ("per_role_drama", lambda m, s: m - s >= 0.05),             # only if anchor PASS
]
BANDS_M = [
    ("flip_events", lambda v: 1.0 <= v <= 20.0),
    ("distinct_flip_ratio", lambda v: v >= 0.5),
    ("quota_share", lambda v: v >= 0.20),
    ("timeout_share", lambda v: v <= 0.25),
    ("role_bias", lambda v: v <= 0.10),
    # per-role skill gates re-checked per seed via eval_roles.per_role_tvr
]
BANDS_SYM = [("draw_rate", lambda v: v <= 0.05), ("seat_balance", lambda v: v <= 0.10),
             ("trained_vs_random", lambda v: v >= 0.80)]
# GO: m_siege wins >= 2/3 COMPARATIVE (or 2/2 if drama demoted) AND all BANDS_M pass.
# STOP RULE: if m_siege fails, evaluate s_flip_r2 vs a0 under the z_flip_r2 template:
#   lead_changes > a0, game_length more central, control_flip_rate > a0,
#   connection_win_fraction >= 0.80  -> >= 3/4 sends S alone to blind.
# Both fail -> print "SCREEN NO-GO — no blind campaign" and exit nonzero.
```

`--anchor-result pass|demoted` CLI flag selects 2/3 vs 2/2 mode (read Stage-1.5 outcome; no silent default — required arg).
5. Outputs: `screen_results.csv` (4 arms × 3 seeds), `screen_results.md` (comparative table M vs S with floors, bands table, verdict + stop-rule branch taken).

- [ ] **Step 2: Smoke run**

Run: `python experiments/siege/run_screen.py --budget 100 --eval-episodes 10 --seeds 42 --anchor-result pass` (after a Task-11 dry calibration produced `games/calibrated/m_siege.json` + `s_flip_r2.json`; if not present, the loud-skip path must print and exit cleanly — test BOTH behaviors).
Expected: CSV+MD written, verdict line printed, no crash.

- [ ] **Step 3: Commit**

```bash
git add experiments/siege/run_screen.py
git commit -m "feat(siege): 4-arm mechanical screen — M-vs-S comparatives with floors, M bands, z_flip_r2 stop-rule branch"
```

---

### Task 14: Blind pack

**Files:**
- Create: `evaluations/siege_ab/.blind_mapping.json`
- Create: `evaluations/siege_ab/play.py`
- Create: `evaluations/siege_ab/BRIEFING.md`
- Create: `evaluations/siege_ab/TEMPLATE_team-N_game{D,V,X}.md`

- [ ] **Step 1: Build the pack**

Copy `evaluations/probe_ab/` structure (play.py runpy shim pointing at an eval_helper; BRIEFING 5-phase protocol; templates). Changes:

- `.blind_mapping.json`: `{"D": "m_siege", "V": "s_flip_r2", "X": "a1_field_connect"}` — labels D/V/X are fresh (Q,Z,K,M,T burned). Sealed: evaluators never read this file; only the orchestrator unblinds after all verdicts are filed.
- Create `experiments/siege/eval_helper.py` (copied from `experiments/field_connect_probe/eval_helper.py`, BLIND dict loading the new mapping; `rules_summary()` must describe m_siege's asymmetric rules NEUTRALLY — "Player 1 wins by connecting...; Player 2 wins by converting N opposing stones or when the turn limit is reached" — no Maker/Breaker/SIEGE words, no quality adjectives).
- BRIEFING.md additions (prereg Stage 3): each team plays BOTH roles of every game (role-swapped matches), verdicts are role-averaged; add the fairness-perception probe question ("Did either side feel structurally favored? 1–5 + one sentence"); log role win split, flag > 80/20.
- Templates: per game D/V/X, the 5-phase rubric + per-role sub-scores + the fairness question.

- [ ] **Step 2: Verify the shim**

Run: `python evaluations/siege_ab/play.py --game D --rules` (after arm configs exist)
Expected: neutral rules text for the sealed game behind D, no identity leak (grep output for "siege|maker|breaker|m_siege": zero matches).

- [ ] **Step 3: Commit**

```bash
git add evaluations/siege_ab/ experiments/siege/eval_helper.py
git commit -m "feat(siege): blind pack — fresh D/V/X labels, sealed mapping, role-swap protocol + fairness probe"
```

---

### Task 15: Execution checklist (run stages in order; STOP at any kill)

**Files:**
- Create: `experiments/siege/RUN_CHECKLIST.md` (this content)

- [ ] **Step 1: Stage 0** — `python experiments/siege/stage0_memo.py` (done in Task 2) and Task 9 smoke (done). Both kills already evaluated at build time; re-confirm PASS lines in STAGE0_MEMO.md and build output.
- [ ] **Step 2: Stage 1** — `python experiments/siege/calibrate.py --arm all --budget 3000 --eval-episodes 200` (~4–5 h). Outputs `calibration.md` + `games/calibrated/{m_siege,s_flip_r2}.json`. STOP RULE: grid-wide M failure → campaign continues S-only (note in calibration.md; do NOT improvise role-pie — it returns through a plan update as the one registered retry).
- [ ] **Step 3: Stage 1.5** — `python experiments/siege/anchor_drama.py --n 200 --games a0,a1,e1453,573` → PASS keeps drama as bar 3; DEMOTED → screen runs `--anchor-result demoted`.
- [ ] **Step 4: Stage 2** — `python experiments/siege/run_screen.py --budget 5000 --eval-episodes 200 --seeds 42,43,44 --anchor-result <pass|demoted>` (~2.5 h). Read screen_results.md verdict: GO-to-blind (M+S+A1), S-only, or SCREEN NO-GO.
- [ ] **Step 5: Stage 3** — blind campaign via agent teams (tmux teammates, NOT background subagents — user's standing setup), 2 independent teams × 3 games, templates in `evaluations/siege_ab/`. Unblind only after all 6 verdicts filed. Apply the Stage-3 decision grammar from PREREGISTRATION verbatim; write `experiments/siege/RESULTS.md` in the fc_phase15 format (decision first, stages, honest synthesis, pre-registration audit).
- [ ] **Step 6: Commit results + propose merge** (finishing-a-development-branch skill).

---

## Self-review notes (spec coverage check, done at plan-writing time)

- Skeleton arms M/S/A1/A0 → Tasks 9 (build), 11 (calibrate), 13 (screen). ✓
- Stage 0a/0b kills → Tasks 2, 9. ✓  Stage 1 gate order + collapsed-seed rerun + (N,T) grid → Task 11. ✓
- Stage 1.5 anchor bar → Task 12; demote path wired into Task 13 via `--anchor-result`. ✓
- Stage 2 comparatives with floors + bands + stop rules → Task 13. ✓
- Stage 3 validity band, role-swap, fairness probe, sealed D/V/X → Task 14 + PREREGISTRATION. ✓
- Grafts: tick cap (T5), clock_frac≡step_frac documented (T1/T7), per-role baseline-adjusted tvr (T11), tvr-before-bias (T11), de-Goodhart bands (T13), chains-not-lone-stones memo (T2), eps sensitivity cell (T11), timeout-share re-assert (T13), RC2 follow-on registered (T1). ✓
- Role-pie fallback intentionally NOT built (YAGNI; registered retry only). clock_frac intentionally NOT added (exists as step_frac). Engine ko: field_flip cycles are bounded by T ≤ 160; flip-tennis is unscored by distinct-cell accounting and surfaced by the distinct_flip_ratio band — no new ko machinery. ✓
