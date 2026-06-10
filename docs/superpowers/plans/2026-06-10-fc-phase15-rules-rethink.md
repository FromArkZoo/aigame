# Field-Connect Phase-1.5 Rules Rethink Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and screen three redesigned Field-Connect rule-sets (C1 field-flip, C2 contested terrain, C3 control capture), then blind-A/B the screen winner against A0/A1 under the pre-registered §7 decision rule.

**Architecture:** Three small, gated, additive mechanics in the existing V2 engine (two new `capture_type`s, one new placement constraint), each keyed off the existing `control_margin`/`board_values` field machinery; a new `experiments/fc_phase15/` harness that mirrors `experiments/field_connect_probe/` (build → calibrate → screen → blind pack). Legacy games stay bit-identical: new code paths only fire for the new type strings.

**Tech Stack:** Python 3 / numpy, pytest (root-level `test_*.py` convention), existing `SelfPlayTrainer` PPO harness, agent-team blind eval protocol from `evaluations/probe_ab/`.

**Spec:** `docs/superpowers/specs/2026-06-10-field-connect-phase15-design.md` (committed `1cd2cf3`). Bars and decision rule are locked there; this plan concretizes proxies and must be committed before any training run.

---

## File structure

| File | Responsibility |
|---|---|
| `game_engine/rules.py` | Register `"field_flip"`, `"field_replace"` capture types and `"not_enemy_controlled"` placement constraint |
| `game_engine/engine_v2.py` | Implement the three mechanics + lockout state + recompute-gate extension + no-legal-move termination |
| `test_field_capture_phase15.py` (root) | Engine unit + property tests for all three mechanics |
| `experiments/fc_phase15/PREREGISTRATION.md` | Locked proxies/signals/bars/labels (committed before training) |
| `experiments/fc_phase15/build_games.py` | C1/C2/C3 game defs + A0/A1 copies + random-rollout smoke |
| `experiments/fc_phase15/metrics.py` | Control-flip-rate helpers (new signals) |
| `experiments/fc_phase15/test_phase15_metrics.py` | Metric unit tests |
| `experiments/fc_phase15/calibrate.py` | Komi calibration for the three C arms |
| `experiments/fc_phase15/run_screen.py` | 5-arm mechanical screen with the fixed 4-signal table |
| `experiments/fc_phase15/eval_helper.py` | Blind eval helper (labels K/M/T), adapted from probe |
| `evaluations/phase15_ab/` | Blind pack: play.py shim, BRIEFING.md, 6 verdict templates |
| `experiments/fc_phase15/RESULTS.md` | Go/no-go readout vs spec §7 |

Engine integration points (verified against current source):
- `_handle_placement` (engine_v2.py:554) places, then `_apply_captures` (611), then `_apply_propagation` (714). At capture time `board_owners` includes the placed stone but `board_values` does **not** yet — field-based capture handlers therefore call `_recompute_field()` (741) themselves, and set `_field_dirty = True` so the gated recompute in `step()` (engine_v2.py:200-208) rebuilds the field after `_apply_propagation`'s incremental add (which would otherwise double-count the placed stone). The final recompute runs before the win check, so the interim double-add is never observed.
- `needs_ko_rule` (game_def_v2.py:142) already returns True for any `capture_type != "none"` — C1/C3 get superko tracking for free; C2 (capture none, target empty, place-only) correctly gets none.
- `_end_by_max_turns` (engine_v2.py:1099) already implements the field_connection controlled-cell tiebreak — C2's no-legal-move termination reuses it.

Parameter note (recorded, not a spec change): at the locked defaults (r=1, d=0.5, ε=0.25) instant recapture in C3 is arithmetically impossible by a single enemy *placement* (post-replace field at the cell is ≥ +2.5 for the mover; one reply swings ≤ 0.5, or ≤ 2·d via a counter-replacement of an adjacent stone — still short). The lockout is implemented anyway per spec §4/§8: it is cheap, and the PARTIAL branch allows parameter re-iteration where the arithmetic no longer protects (e.g. d > 1).

---

### Task 1: Pre-registration document

**Files:**
- Create: `experiments/fc_phase15/PREREGISTRATION.md`

- [ ] **Step 1: Write the pre-registration doc**

```markdown
# FC phase-1.5 — pre-registration (locked before any training run)

Spec: docs/superpowers/specs/2026-06-10-field-connect-phase15-design.md (1cd2cf3).
This file concretizes measurement details; bars are quoted verbatim from spec §6b/§7.

## Arms
c1_field_flip, c2_contested_terrain, c3_control_capture (treatments);
a0_baseline, a1_field_connect (comparators, retrained — no probe checkpoints
exist — from the probe's komi-calibrated defs under identical new instrumentation).

## Screen signals (all movable by every arm; spec §6b)
1. lead_changes — proxy identical to probe metrics.py: field arms use
   largest-controlled-component differential at the arm's own control_margin
   (0.25 for C arms, 0.0 for A1); A0 uses the threshold-race score differential.
   Pie-swap plies excluded. Bar: arm mean > A0 mean.
2. game_length — bar: in [30,160] and at-least-as-central as A0
   (probe's exact lambda, band midpoint 95).
3. control_flip_rate (NEW) — per non-swap ply, count cells whose controller
   sign {-1,0,+1} (at the arm's margin) changed vs the previous ply; mean per
   ply, then mean over episodes/seeds. Bar: arm mean > A0 mean.
4. connection_win_fraction (NEW) — fraction of episodes ending by win-condition
   fire (engine._winner is not None and not engine._ended_by_max_turns).
   Bar: >= 0.80 (floor, not vs A0).

Screen GO per arm: >= 3/4. Ranking among GO arms: control_flip_rate, descending.
Only the top arm advances. If no arm clears 3/4: report NO-GO, stop before blind.

## Sanity gates (per arm; any failure invalidates the arm)
trained_vs_random >= 0.80; draw_rate <= 0.05; post-komi seat bias <= 0.10.

## Screen config
PPO budget 5000, seeds 42/43/44, sampled seat-swap mirror eval n=200/seed
(probe methodology). Komi: C arms calibrated by experiments/fc_phase15/calibrate.py
(grid 0.0..0.30 step 0.05, budget 3000, seed 42, bias <= 0.10 to pass);
A0/A1 keep their probe-calibrated komi.

## Blind campaign (spec §6c)
3 games x 2 independent agent teams = 6 verdicts. Fresh labels K/M/T
(mapping sealed in experiments/fc_phase15/eval_helper.py BLIND dict;
evaluators are instructed not to read harness internals — same protocol
that held in the probe). Unblinding only after all 6 verdicts are filed.

## Decision rule
Spec §7 verbatim (GO / PARTIAL / NO-GO / replicate-check). Not altered after data.
```

- [ ] **Step 2: Commit**

```bash
git add experiments/fc_phase15/PREREGISTRATION.md
git commit -m "prereg(phase-1.5): lock screen proxies, signals, labels, decision rule before any training"
```

---

### Task 2: Register the new rule types

**Files:**
- Modify: `game_engine/rules.py:28-34` (PLACEMENT_CONSTRAINTS), `game_engine/rules.py:84` (CAPTURE_TYPES), docstrings + complexity
- Test: `test_field_capture_phase15.py` (root — new file)

- [ ] **Step 1: Write the failing tests**

Create `test_field_capture_phase15.py`:

```python
"""Phase-1.5 rules-rethink — engine tests for field_flip / field_replace
captures and the not_enemy_controlled placement constraint.

Spec: docs/superpowers/specs/2026-06-10-field-connect-phase15-design.md.
"""
from __future__ import annotations

import numpy as np

from game_engine.engine_v2 import GameEngineV2
from game_engine.game_def_v2 import GameDefV2
from game_engine.rules import (
    CAPTURE_TYPES,
    PLACEMENT_CONSTRAINTS,
    ActionRule,
    CaptureRule,
    PlacementRule,
    PropagationRule,
    TurnStructure,
    WinCondition,
)


def make_p15_game(
    *,
    s: int = 6,
    control_margin: float = 0.25,
    radius: int = 1,
    decay: float = 0.5,
    capture_type: str = "none",
    placement_constraint: str = "anywhere",
    max_turns: int = 60,
) -> GameDefV2:
    """Minimal hex_rhombus phase-1.5 game. P1 connects dim 1, P2 dim 0."""
    return GameDefV2(
        game_id=f"p15_test_{capture_type}_{placement_constraint}",
        num_dimensions=2,
        axis_size=s,
        topology_type="hex_rhombus",
        placement_rule=PlacementRule(
            target="empty", constraint=placement_constraint,
        ),
        capture_rule=CaptureRule(capture_type=capture_type),
        propagation_rule=PropagationRule(
            prop_type="influence", radius=radius, strength=1.0, decay=decay,
        ),
        win_condition=WinCondition(
            condition_type="field_connection",
            target_dimension=1,
            target_dimension_p2=0,
            max_turns=max_turns,
            control_margin=control_margin,
        ),
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
        pie_rule=False,
    )


def _engine(game: GameDefV2) -> GameEngineV2:
    e = GameEngineV2(game)
    e.reset()
    return e


def test_new_rule_types_registered() -> None:
    assert "field_flip" in CAPTURE_TYPES
    assert "field_replace" in CAPTURE_TYPES
    assert "not_enemy_controlled" in PLACEMENT_CONSTRAINTS


def test_new_rule_types_roundtrip() -> None:
    g = make_p15_game(capture_type="field_flip")
    g2 = GameDefV2.from_dict(g.to_dict())
    assert g2.capture_rule.capture_type == "field_flip"
    g = make_p15_game(placement_constraint="not_enemy_controlled")
    g2 = GameDefV2.from_dict(g.to_dict())
    assert g2.placement_rule.constraint == "not_enemy_controlled"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest test_field_capture_phase15.py -v`
Expected: FAIL — `"field_flip" in CAPTURE_TYPES` is False.

- [ ] **Step 3: Register the types in rules.py**

In `game_engine/rules.py`:

```python
PLACEMENT_CONSTRAINTS = (
    "anywhere",
    "adjacent_to_own",
    "adjacent_to_enemy",
    "adjacent_to_any",
    "not_enemy_controlled",
)
```

```python
CAPTURE_TYPES = (
    "none", "surround", "custodian", "outnumber", "field_flip", "field_replace",
)
```

Extend the docstrings in place:
- `PlacementRule.constraint`: add `- ``"not_enemy_controlled"``: only cells the enemy does not control via the influence field (|board_values| margin from win_condition.control_margin). Phase-1.5 C2.`
- `CaptureRule.capture_type`: add `- ``"field_flip"``: enemy stones standing on mover-controlled cells (incl. own contribution) flip colour; cascades to a fixed point. Phase-1.5 C1.` and `- ``"field_replace"``: placement onto an enemy stone is legal when the mover controls that cell; the stone is replaced. One-turn recapture lockout. Phase-1.5 C3.`
- `CaptureRule.complexity()`: return 2 for both new types (type + mechanic — same bucket as surround/custodian; no free parameter).

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest test_field_capture_phase15.py -v`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add game_engine/rules.py test_field_capture_phase15.py
git commit -m "feat(engine): register field_flip/field_replace captures + not_enemy_controlled constraint"
```

---

### Task 3: C1 — field_flip capture mechanic

**Files:**
- Modify: `game_engine/engine_v2.py` (`_apply_captures` at 611; new `_capture_field_flip`; recompute gate at 200-208)
- Test: `test_field_capture_phase15.py`

- [ ] **Step 1: Write the failing tests**

Append to `test_field_capture_phase15.py`. All cell choices are computed from
the topology (no assumed coordinate offsets); the hand arithmetic in comments
uses: field at a stone's cell = (own ±1.0) + 0.5·(friendly nbrs − enemy nbrs).

```python
def _far_cells(e: GameEngineV2, exclude: set[int], n: int) -> list[int]:
    """n cells at graph distance >= 2 from everything in *exclude*."""
    halo = set(exclude)
    for c in exclude:
        halo.update(e.topo.get_neighbors(c))
    out = []
    for c in e.topo.active_cells:
        if c not in halo and not (set(e.topo.get_neighbors(c)) & exclude):
            out.append(c)
        if len(out) == n:
            return out
    raise AssertionError("board too small for test geometry")


def test_field_flip_three_attackers_flip_lone_stone() -> None:
    e = _engine(make_p15_game(capture_type="field_flip"))
    center = e.topo.coords_to_cell((3, 3))
    ring = list(e.topo.get_neighbors(center))
    attackers = ring[:3]
    far = _far_cells(e, {center, *ring}, 2)
    # P1 a0, P2 center, P1 a1, P2 far0, P1 a2 -> field at center
    # = -1.0 + 0.5*3 = +0.5 > eps(0.25) -> flips.
    e.step(attackers[0]); e.step(center)
    e.step(attackers[1]); e.step(far[0])
    assert e.board_owners[center] == 2  # not yet: -1.0 + 0.5*2 = 0.0 <= 0.25
    e.step(attackers[2])
    assert e.board_owners[center] == 1
    assert e.piece_counts == [4, 1]
    # field must be the exact recompute (no stale/double-added values)
    bv = e.board_values.copy()
    e._recompute_field()
    assert np.allclose(bv, e.board_values)


def test_field_flip_defender_blocks_until_fourth_attacker() -> None:
    e = _engine(make_p15_game(capture_type="field_flip"))
    center = e.topo.coords_to_cell((3, 3))
    ring = list(e.topo.get_neighbors(center))
    defender = ring[0]
    attackers = [c for c in ring if c != defender][:4]
    far = _far_cells(e, {center, *ring}, 2)
    e.step(attackers[0]); e.step(center)
    e.step(attackers[1]); e.step(defender)
    e.step(attackers[2]); e.step(far[0])
    # -1.0 + 0.5*(3-1) = 0.0 <= 0.25: defender holds.
    assert e.board_owners[center] == 2
    e.step(attackers[3])
    # -1.0 + 0.5*(4-1) = +0.5 > 0.25: flips despite defender.
    assert e.board_owners[center] == 1


def test_field_flip_cascades_through_flipped_stone() -> None:
    e = _engine(make_p15_game(capture_type="field_flip"))
    A = e.topo.coords_to_cell((3, 3))
    ring = list(e.topo.get_neighbors(A))
    B = ring[0]
    adj_B = set(e.topo.get_neighbors(B))
    non_adj = [c for c in ring if c != B and c not in adj_B]
    bridge = next(c for c in ring if c != B and c in adj_B)
    attackers = non_adj[:3] + [bridge]           # 4 attackers on A's ring
    outer = [c for c in adj_B if c != A and c not in ring][:2]
    far = _far_cells(e, {A, B, *ring, *adj_B}, 3)
    # P1: outer0, outer1, non_adj x3, bridge(last, trigger). P2: A, B, far x3.
    seq_p1 = [outer[0], outer[1], attackers[0], attackers[1], attackers[2],
              attackers[3]]
    seq_p2 = [A, B, far[0], far[1], far[2]]
    for i in range(5):
        e.step(seq_p1[i]); e.step(seq_p2[i])
        # A is placed at pair 0, B at pair 1 — assert neither ever flips
        # to P1 prematurely (owner is 0-or-2 until the trigger).
        assert e.board_owners[A] != 1 and e.board_owners[B] != 1
    e.step(seq_p1[5])  # trigger
    # A: -1.0 + 0.5*4 - 0.5(B) = +0.5 > 0.25 -> flips.
    # B after A flips: -1.0 + 0.5(A) + 0.5(bridge) + 0.5*2(outer) = +1.0 -> cascades.
    assert e.board_owners[A] == 1 and e.board_owners[B] == 1
    assert e.piece_counts == [8, 3]


def test_field_flip_can_complete_connection_same_step() -> None:
    """Flips update the field before the win check, so a flip-created
    connection wins on the move that caused it."""
    e = _engine(make_p15_game(capture_type="field_flip", s=4, max_turns=40))
    # Drive P1 toward a column connection; exact final assertion is on the
    # invariant: whenever done fires with a winner and not max-turns, the
    # field recompute confirms a crossing exists. Play scripted greedy fill
    # of column q=1 for P1, scattered P2 elsewhere.
    p1_col = [e.topo.coords_to_cell((1, r)) for r in range(4)]
    p2_cells = [e.topo.coords_to_cell((3, r)) for r in range(3)]
    moves = [p1_col[0], p2_cells[0], p1_col[1], p2_cells[1],
             p1_col[2], p2_cells[2], p1_col[3]]
    for m in moves:
        if e.done:
            break
        e.step(m)
    assert e.done and e._winner == 1 and not e._ended_by_max_turns
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest test_field_capture_phase15.py -v -k field_flip`
Expected: FAIL — flips never happen (`board_owners[center]` stays 2), because `_apply_captures` ignores `"field_flip"`.

- [ ] **Step 3: Implement field_flip in engine_v2.py**

In `_apply_captures` (engine_v2.py:611), extend the dispatch:

```python
        elif capture_type == "field_flip":
            self._capture_field_flip(placed_cell)
        elif capture_type == "field_replace":
            self._capture_field_replace(placed_cell)
```

(`_capture_field_replace` is a stub for now — added properly in Task 4; for this task define it as `pass`-equivalent only if needed to keep imports clean. Prefer adding both dispatch lines now and the real `_capture_field_replace` in Task 4.)

New method after `_capture_outnumber` (engine_v2.py:682):

```python
    def _capture_field_flip(self, placed_cell: int) -> None:
        """Phase-1.5 C1: enemy stones on mover-controlled cells flip colour.

        Control is measured INCLUDING the stone's own contribution, so a
        lone stone needs net opposing pressure > 1 + margin to flip
        (3 net adjacent attackers at r=1/d=0.5/eps=0.25). Flips cascade:
        each flip raises the mover's field monotonically, so resolution
        terminates in at most #enemy-stones iterations. board_values does
        not yet include the just-placed stone here (propagation runs after
        captures), so we recompute from board_owners first; the final
        gated recompute in step() corrects propagation's later double-add.
        """
        mover = self.current_player
        enemy = 3 - mover
        margin = getattr(self.game.win_condition, "control_margin", 0.0)
        sign = 1.0 if mover == 1 else -1.0
        self._recompute_field()
        while True:
            to_flip = [
                c for c in self.topo.active_cells
                if self.board_owners[c] == enemy
                and sign * self.board_values[c] > margin
            ]
            if not to_flip:
                break
            for c in to_flip:
                self.board_owners[c] = mover
            self.piece_counts[enemy - 1] -= len(to_flip)
            self.piece_counts[mover - 1] += len(to_flip)
            self._recompute_field()
        self._field_dirty = True
```

Extend the gated recompute in `step()` (engine_v2.py:200-208) so the new capture types always get the corrective recompute even if composed with a non-field win condition:

```python
        if self._field_dirty and (
            self.game.win_condition.condition_type == "field_connection"
            or self.game.capture_rule.capture_type
            in ("field_flip", "field_replace")
        ):
            self._recompute_field()
        self._field_dirty = False
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest test_field_capture_phase15.py -v -k field_flip`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add game_engine/engine_v2.py test_field_capture_phase15.py
git commit -m "feat(engine): C1 field_flip capture — monotone flip cascade on mover-controlled cells"
```

---

### Task 4: C1 property test — fixed-point reference implementation

**Files:**
- Test: `test_field_capture_phase15.py`

- [ ] **Step 1: Write the property test**

```python
def _reference_field(owners, topo, rule) -> np.ndarray:
    bv = np.zeros(len(owners), dtype=np.float64)
    for cell in topo.active_cells:
        o = int(owners[cell])
        if o == 0:
            continue
        s = 1.0 if o == 1 else -1.0
        for c in topo.cells_within_radius(cell, rule.radius):
            bv[c] += s * rule.strength * (rule.decay ** topo.distance(cell, c))
    return np.clip(bv, -100.0, 100.0)


def _reference_flip_fixpoint(owners, mover, topo, rule, margin):
    owners = owners.copy()
    enemy = 3 - mover
    sign = 1.0 if mover == 1 else -1.0
    while True:
        bv = _reference_field(owners, topo, rule)
        flips = [c for c in topo.active_cells
                 if owners[c] == enemy and sign * bv[c] > margin]
        if not flips:
            return owners
        for c in flips:
            owners[c] = mover


def test_field_flip_matches_reference_on_random_games() -> None:
    rng = np.random.default_rng(7)
    for trial in range(3):
        g = make_p15_game(capture_type="field_flip", s=5, max_turns=40)
        e = _engine(g)
        for _ in range(40):
            if e.done:
                break
            legal = [a for a in e.get_legal_actions() if a < e.total_cells]
            if not legal:
                break
            mover = e.current_player
            pre = e.board_owners.copy()
            cell = int(rng.choice(legal))
            pre[cell] = mover  # the placement itself
            expected = _reference_flip_fixpoint(
                pre, mover, e.topo, g.propagation_rule,
                g.win_condition.control_margin,
            )
            e.step(cell)
            assert np.array_equal(e.board_owners, expected), (
                f"trial {trial}: engine diverged from reference fixpoint"
            )
            assert np.allclose(
                e.board_values,
                _reference_field(e.board_owners, e.topo, g.propagation_rule),
            )
```

- [ ] **Step 2: Run the test**

Run: `python -m pytest test_field_capture_phase15.py -v -k reference`
Expected: PASS (this validates Task 3; if it fails, debug Task 3 — the reference is the spec).

- [ ] **Step 3: Commit**

```bash
git add test_field_capture_phase15.py
git commit -m "test(engine): C1 field_flip property test vs brute-force fixpoint reference"
```

---

### Task 5: C3 — field_replace capture mechanic

**Files:**
- Modify: `game_engine/engine_v2.py` (`__init__` at 28; `_handle_placement` at 554; `get_legal_actions` at 382; new `_capture_field_replace`; `_save_state`/`_restore_state` at 1164/1178)
- Test: `test_field_capture_phase15.py`

- [ ] **Step 1: Write the failing tests**

```python
def _setup_three_attackers(capture_type: str):
    """P2 stone at center with exactly 3 P1 attackers; P1 to move."""
    e = _engine(make_p15_game(capture_type=capture_type))
    center = e.topo.coords_to_cell((3, 3))
    ring = list(e.topo.get_neighbors(center))
    attackers = ring[:3]
    far = _far_cells(e, {center, *ring}, 3)
    e.step(attackers[0]); e.step(center)
    e.step(attackers[1]); e.step(far[0])
    e.step(attackers[2]); e.step(far[1])
    return e, center


def test_field_replace_legality_tracks_control() -> None:
    e, center = _setup_three_attackers("field_replace")
    # P1 to move; field at center = -1.0 + 0.5*3 = +0.5 > 0.25 -> replaceable.
    legal = e.get_legal_actions()
    assert center in legal
    # The ONLY occupied legal target is the controlled enemy stone — own
    # stones and uncontrolled enemy stones are never replace targets.
    occupied_targets = [a for a in legal
                        if a < e.total_cells and e.board_owners[a] != 0]
    assert occupied_targets == [center]


def test_field_replace_two_attackers_not_legal() -> None:
    e = _engine(make_p15_game(capture_type="field_replace"))
    center = e.topo.coords_to_cell((3, 3))
    ring = list(e.topo.get_neighbors(center))
    far = _far_cells(e, {center, *ring}, 2)
    e.step(ring[0]); e.step(center)
    e.step(ring[1]); e.step(far[0])
    # P1 to move; field at center = -1.0 + 0.5*2 = 0.0 <= 0.25 -> NOT legal.
    assert center not in e.get_legal_actions()


def test_field_replace_executes_and_sets_lockout() -> None:
    e, center = _setup_three_attackers("field_replace")
    k = e.step_count
    e.step(center)
    assert e.board_owners[center] == 1
    assert e.piece_counts == [4, 2]  # P1: 3 placed + replacement; P2: 3 - 1
    assert e._replace_lockout_cell == center
    assert e._replace_lockout_step == k


def test_field_replace_lockout_excludes_then_expires() -> None:
    """White-box: the locked cell is excluded exactly on the following turn."""
    e = _engine(make_p15_game(capture_type="field_replace"))
    center = e.topo.coords_to_cell((3, 3))
    ring = list(e.topo.get_neighbors(center))
    # Manufacture: P1 stone at center, P2 controls it (4 P2 ring stones).
    e.board_owners[center] = 1
    for c in ring[:4]:
        e.board_owners[c] = 2
    e.piece_counts = [1, 4]
    e._recompute_field()
    e.current_player = 2
    e.step_count = 10
    # field at center = +1.0 - 0.5*4 = -1.0; sign(P2)*bv = +1.0 > 0.25.
    assert center in e.get_legal_actions()
    e._replace_lockout_cell = center
    e._replace_lockout_step = 9   # "replaced last turn"
    assert center not in e.get_legal_actions()
    e._replace_lockout_step = 8   # one turn older -> expired
    assert center in e.get_legal_actions()


def test_field_replace_state_save_restore() -> None:
    e = _engine(make_p15_game(capture_type="field_replace"))
    e._replace_lockout_cell = 7
    e._replace_lockout_step = 3
    saved = e._save_state()
    e._replace_lockout_cell = -1
    e._replace_lockout_step = -1
    e._restore_state(saved)
    assert e._replace_lockout_cell == 7
    assert e._replace_lockout_step == 3
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest test_field_capture_phase15.py -v -k field_replace`
Expected: FAIL — `center not in legal actions` (replace targets never offered).

- [ ] **Step 3: Implement field_replace**

In `__init__` (engine_v2.py:28, near `_field_dirty`):

```python
        # Phase-1.5 C3 (field_replace): one-turn recapture lockout + the
        # previous owner of the last-placed cell (set by _handle_placement,
        # consumed by _capture_field_replace).
        self._replace_prev_owner: int = 0
        self._replace_lockout_cell: int = -1
        self._replace_lockout_step: int = -1
```

In `reset()` (engine_v2.py:78-104, wherever board state is zeroed), reset all three to the same defaults.

In `_handle_placement` (engine_v2.py:554), the method already computes `prev_owner`; stash it (one line, behavior-neutral for legacy games):

```python
        prev_owner = int(self.board_owners[cell])
        self._replace_prev_owner = prev_owner
```

New method after `_capture_field_flip`:

```python
    def _capture_field_replace(self, placed_cell: int) -> None:
        """Phase-1.5 C3: bookkeeping after a placement in a field_replace
        game. The replacement itself already happened in _handle_placement
        (overwrite path); here we set the one-turn recapture lockout when
        an enemy stone was displaced, and mark the field for recompute
        (the displaced stone's kernel must be rebuilt away).
        """
        if self._replace_prev_owner not in (0, self.current_player):
            self._replace_lockout_cell = placed_cell
            self._replace_lockout_step = self.step_count
        self._field_dirty = True
```

In `get_legal_actions` (engine_v2.py:382), after `actions.extend(candidates)` (line 440), add the replace targets:

```python
        # Phase-1.5 C3: enemy-occupied cells the mover controls (beyond the
        # control margin, with the stone's own contribution included) are
        # legal placement targets — except the cell replaced last turn.
        if (
            self.game.action_rule.has_place()
            and self.game.capture_rule.capture_type == "field_replace"
        ):
            margin = getattr(self.game.win_condition, "control_margin", 0.0)
            sign = 1.0 if player == 1 else -1.0
            lockout = (
                self._replace_lockout_cell
                if self.step_count == self._replace_lockout_step + 1
                else -1
            )
            actions.extend(
                c for c in self.topo.active_cells
                if self.board_owners[c] == enemy
                and sign * self.board_values[c] > margin
                and c != lockout
            )
```

In `_save_state` (engine_v2.py:1164) add to the returned dict:

```python
            "_replace_lockout_cell": self._replace_lockout_cell,
            "_replace_lockout_step": self._replace_lockout_step,
            "_replace_prev_owner": self._replace_prev_owner,
```

and in `_restore_state` (engine_v2.py:1178):

```python
        self._replace_lockout_cell = saved["_replace_lockout_cell"]
        self._replace_lockout_step = saved["_replace_lockout_step"]
        self._replace_prev_owner = saved["_replace_prev_owner"]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest test_field_capture_phase15.py -v -k field_replace`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add game_engine/engine_v2.py test_field_capture_phase15.py
git commit -m "feat(engine): C3 field_replace capture — control-gated replacement with one-turn recapture lockout"
```

---

### Task 6: C2 — not_enemy_controlled placement gate + no-legal-move termination

**Files:**
- Modify: `game_engine/engine_v2.py` (`get_legal_actions` constraint chain at 411-438; `step()` after win check at 210-217; new `_has_legal_placement`)
- Test: `test_field_capture_phase15.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_not_enemy_controlled_gates_placements_symmetrically() -> None:
    e = _engine(make_p15_game(
        placement_constraint="not_enemy_controlled", capture_type="none",
    ))
    a = e.topo.coords_to_cell((0, 0))
    b = e.topo.coords_to_cell((3, 3))
    e.step(a)   # P1
    e.step(b)   # P2
    # P1 to move: b's empty neighbors have bv = -0.5 < -0.25 -> illegal for P1.
    legal_p1 = set(e.get_legal_actions())
    for c in e.topo.get_neighbors(b):
        if e.board_owners[c] == 0:
            assert c not in legal_p1
    # a's empty neighbors (bv = +0.5) and far cells (bv = 0) stay legal.
    for c in e.topo.get_neighbors(a):
        if e.board_owners[c] == 0:
            assert c in legal_p1
    # Symmetric for P2 after P1 moves again somewhere neutral.
    far = _far_cells(e, {a, b, *e.topo.get_neighbors(a),
                         *e.topo.get_neighbors(b)}, 1)
    e.step(far[0])
    legal_p2 = set(e.get_legal_actions())
    for c in e.topo.get_neighbors(a):
        if e.board_owners[c] == 0:
            assert c not in legal_p2


def test_contested_tie_cells_placeable_by_both() -> None:
    e = _engine(make_p15_game(
        placement_constraint="not_enemy_controlled", capture_type="none",
    ))
    a = e.topo.coords_to_cell((2, 2))
    e.step(a)  # P1
    # Find an empty cell adjacent to a; P2 places adjacent to that cell so
    # its field becomes exactly 0.0 (tie) -> contested -> both may place.
    target = next(c for c in e.topo.get_neighbors(a)
                  if e.board_owners[c] == 0)
    p2_spot = next(c for c in e.topo.get_neighbors(target)
                   if e.board_owners[c] == 0 and c != a
                   and a not in e.topo.get_neighbors(c))
    e.step(p2_spot)  # P2: target now has bv = +0.5 - 0.5 = 0.0
    assert abs(e.board_values[target]) < 1e-9
    assert target in e.get_legal_actions()          # P1 may place
    e.step(_far_cells(e, {a, p2_spot, target}, 1)[0])
    assert target in e.get_legal_actions()          # P2 may place too


def test_no_legal_placement_ends_game_with_field_tiebreak() -> None:
    """White-box: when the mover's last legal cell disappears, the game
    ends immediately via the max-turns (controlled-cell) tiebreak."""
    g = make_p15_game(
        placement_constraint="not_enemy_controlled", capture_type="none", s=4,
    )
    e = _engine(g)
    # P2 owns a dominating position: all cells except two empties are P2's.
    empties = [e.topo.coords_to_cell((0, 0)), e.topo.coords_to_cell((3, 3))]
    n_p2 = 0
    for c in e.topo.active_cells:
        if c not in empties:
            e.board_owners[c] = 2
            n_p2 += 1
    e.piece_counts = [0, n_p2]
    e._recompute_field()
    e.current_player = 2
    e.step_count = 4
    e._pie_resolved = True
    # P2 fills one empty; the other is now enemy-controlled for P1 ->
    # P1 has no legal placement -> game ends, P2 wins on controlled cells.
    e.step(empties[0])
    assert e.done
    assert e._ended_by_max_turns
    assert e._winner == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest test_field_capture_phase15.py -v -k "not_enemy or contested_tie or no_legal"`
Expected: FAIL — enemy-controlled neighbors still legal (constraint not implemented).

- [ ] **Step 3: Implement the gate and termination**

In `get_legal_actions`, extend the constraint chain (engine_v2.py:411-438, after the `adjacent_to_any` branch):

```python
                elif constraint == "not_enemy_controlled":
                    # Phase-1.5 C2: the field gates moves. A cell is
                    # placeable unless the enemy controls it beyond the
                    # control margin (contested ties stay open to both).
                    margin = getattr(
                        self.game.win_condition, "control_margin", 0.0
                    )
                    sign = 1.0 if player == 1 else -1.0
                    candidates = [
                        c for c in candidates
                        if sign * self.board_values[c] >= -margin
                    ]
```

New helper next to `get_legal_actions`:

```python
    def _has_legal_placement(self, player: int) -> bool:
        """True if *player* has at least one legal place action (raw cell
        indices are < total_cells; pass and swap encode higher)."""
        return any(a < self.total_cells for a in self.get_legal_actions(player))
```

In `step()`, after the win check (engine_v2.py:210-212) and before the max-turns enforcement:

```python
        # Phase-1.5 C2: a mover with no legal placement ends the game
        # immediately under the timeout tiebreak (spec §4 C2). Gated on the
        # constraint so every other game skips the extra legality scan.
        if (
            not self.done
            and self.game.placement_rule.constraint == "not_enemy_controlled"
            and not self._has_legal_placement(self.current_player)
        ):
            self._end_by_max_turns()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest test_field_capture_phase15.py -v`
Expected: all phase-1.5 tests pass (14 total).

- [ ] **Step 5: Commit**

```bash
git add game_engine/engine_v2.py test_field_capture_phase15.py
git commit -m "feat(engine): C2 not_enemy_controlled placement gate + no-legal-move termination"
```

---

### Task 7: Legacy bit-identity regression

**Files:** none (verification only)

- [ ] **Step 1: Run the full suite**

Run: `python -m pytest -x -q`
Expected: everything passes, 0 failures. The new branches are all gated on the new type strings, so every existing test (including `test_field_connection.py`, `test_pie_rule.py`, `test_r21_seeds.py` determinism tests) must be untouched.

- [ ] **Step 2: If anything fails**

Use superpowers:systematic-debugging. The most likely regression sources: the recompute-gate edit in `step()` (Task 3) changing behavior for legacy `field_connection` games — the new disjunct must be additive (`or`), never replacing the original condition; and the `_replace_prev_owner` stash in `_handle_placement` — it must be a pure attribute assignment with no control-flow change.

- [ ] **Step 3: Commit (only if fixes were needed)**

```bash
git add -A && git commit -m "fix(engine): legacy regression fixes from phase-1.5 mechanics"
```

---

### Task 8: Build the three game defs + smoke

**Files:**
- Create: `experiments/fc_phase15/build_games.py`
- Create (generated): `experiments/fc_phase15/games/*.json`

- [ ] **Step 1: Write build_games.py**

```python
"""FC phase-1.5 — build C1/C2/C3 game defs on the probe's hex_rhombus W=22
board, copy the probe-calibrated A0/A1 comparators, random-rollout smoke all.

Spec: docs/superpowers/specs/2026-06-10-field-connect-phase15-design.md.
Shared base (spec §3): r=1/s=1.0/d=0.5, control_margin 0.25, pie on,
max_turns 200, komi 0.0 pre-calibration.

Usage:
    python experiments/fc_phase15/build_games.py [--smoke 50]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from game_engine.engine_v2 import GameEngineV2  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from game_engine.rules import (  # noqa: E402
    ActionRule,
    CaptureRule,
    PlacementRule,
    PropagationRule,
    TurnStructure,
    WinCondition,
)

HERE = Path(__file__).resolve().parent
GAMES_DIR = HERE / "games"
PROBE_CAL = ROOT / "experiments" / "field_connect_probe" / "games" / "calibrated"

W = 22

COMMON = dict(
    num_dimensions=2,
    axis_size=W,
    topology_type="hex_rhombus",
    turn_structure=TurnStructure(turn_type="alternating"),
    action_rule=ActionRule(action_types=("place",)),
    pie_rule=True,
)

WIN = dict(
    condition_type="field_connection",
    control_margin=0.25,
    target_dimension=1,
    target_dimension_p2=0,
    max_turns=200,
)

FIELD = dict(prop_type="influence", radius=1, strength=1.0, decay=0.5)


def build_c1() -> GameDefV2:
    return GameDefV2(
        game_id="p15_c1_field_flip",
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="field_flip"),
        propagation_rule=PropagationRule(**FIELD),
        win_condition=WinCondition(**WIN),
        **COMMON,
    )


def build_c2() -> GameDefV2:
    # first_move_anywhere=False: the default True would waive the gate on
    # each player's first stone (engine_v2.py:411), violating spec §4 C2.
    # On an empty board the gate excludes nothing anyway (field is 0).
    return GameDefV2(
        game_id="p15_c2_contested_terrain",
        placement_rule=PlacementRule(
            target="empty", constraint="not_enemy_controlled",
            first_move_anywhere=False,
        ),
        capture_rule=CaptureRule(capture_type="none"),
        propagation_rule=PropagationRule(**FIELD),
        win_condition=WinCondition(**WIN),
        **COMMON,
    )


def build_c3() -> GameDefV2:
    return GameDefV2(
        game_id="p15_c3_control_capture",
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="field_replace"),
        propagation_rule=PropagationRule(**FIELD),
        win_condition=WinCondition(**WIN),
        **COMMON,
    )


def smoke(game: GameDefV2, n: int, rng: np.random.Generator) -> dict:
    lengths, capture_events, draws, timeouts, gate_seen = [], 0, 0, 0, 0
    for _ in range(n):
        e = GameEngineV2(game)
        e.reset()
        prev_counts = list(e.piece_counts)
        while not e.done:
            legal = e.get_legal_actions()
            if game.placement_rule.constraint == "not_enemy_controlled":
                empties = sum(1 for c in e.topo.active_cells
                              if e.board_owners[c] == 0)
                if sum(1 for a in legal if a < e.total_cells) < empties:
                    gate_seen += 1
            e.step(int(rng.choice(legal)))
            for p in (0, 1):
                drop = prev_counts[p] - e.piece_counts[p]
                if drop > 0:
                    capture_events += drop
            prev_counts = list(e.piece_counts)
        lengths.append(e.step_count)
        draws += e._winner is None
        timeouts += e._ended_by_max_turns
    return dict(
        game_id=game.game_id, n=n, mean_len=float(np.mean(lengths)),
        capture_events=capture_events, draws=draws, timeouts=timeouts,
        gate_seen=gate_seen,
    )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--smoke", type=int, default=50)
    args = p.parse_args()

    GAMES_DIR.mkdir(exist_ok=True)
    games = [build_c1(), build_c2(), build_c3()]
    for g in games:
        path = GAMES_DIR / f"{g.game_id.removeprefix('p15_')}.json"
        json.dump(g.to_dict(), open(path, "w"), indent=2)
        print(f"wrote {path}")
    for src in ("a0_baseline.json", "a1_field_connect.json"):
        shutil.copy(PROBE_CAL / src, GAMES_DIR / src)
        print(f"copied probe-calibrated {src}")

    rng = np.random.default_rng(0)
    for g in games:
        r = smoke(g, args.smoke, rng)
        print(r)
        assert r["mean_len"] <= g.win_condition.max_turns + 1
        if g.game_id == "p15_c1_field_flip":
            assert r["capture_events"] > 0, "C1 smoke: no flips ever fired"
        if g.game_id == "p15_c3_control_capture":
            assert r["capture_events"] > 0, "C3 smoke: no replacements fired"
        if g.game_id == "p15_c2_contested_terrain":
            assert r["gate_seen"] > 0, "C2 smoke: gate never restricted moves"
    print("SMOKE OK")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run it**

Run: `python experiments/fc_phase15/build_games.py --smoke 50`
Expected: three `wrote ...` lines, two `copied ...` lines, three smoke dicts, `SMOKE OK`. If a smoke assert fires, that is a real design-mechanics bug — debug before proceeding (superpowers:systematic-debugging), do not weaken the assert.

- [ ] **Step 3: Commit**

```bash
git add experiments/fc_phase15/build_games.py experiments/fc_phase15/games/
git commit -m "feat(phase-1.5): C1/C2/C3 game defs + A0/A1 comparator copies + rollout smoke (flips/replacements/gate all fire)"
```

---

### Task 9: Screen metrics module

**Files:**
- Create: `experiments/fc_phase15/metrics.py`
- Test: `experiments/fc_phase15/test_phase15_metrics.py`

- [ ] **Step 1: Write the failing tests**

```python
"""Unit tests for the phase-1.5 control-flip metrics."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from experiments.fc_phase15.metrics import (  # noqa: E402
    controller_signs,
    count_controller_changes,
)


class _FakeEngine:
    def __init__(self, bv):
        self.board_values = np.asarray(bv, dtype=np.float64)


def test_controller_signs_trichotomy() -> None:
    e = _FakeEngine([0.5, -0.5, 0.25, -0.25, 0.0, 0.26])
    s = controller_signs(e, margin=0.25)
    assert s.tolist() == [1, -1, 0, 0, 0, 1]


def test_count_controller_changes() -> None:
    a = np.array([1, -1, 0, 0], dtype=np.int8)
    b = np.array([1, 0, -1, 0], dtype=np.int8)
    assert count_controller_changes(a, b) == 2
    assert count_controller_changes(a, a) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest experiments/fc_phase15/test_phase15_metrics.py -v`
Expected: FAIL — module does not exist.

- [ ] **Step 3: Write metrics.py**

```python
"""Phase-1.5 screen metrics (pre-registered in PREREGISTRATION.md).

control_flip_rate: per non-swap ply, the number of cells whose controller
sign (+1 P1 / -1 P2 / 0 contested, at the game's control margin) changed
vs the previous ply. Pie-swap plies are excluded by the caller — the swap
negates the whole field and would register ~half the board as flipped.
"""
from __future__ import annotations

import numpy as np


def controller_signs(engine, margin: float) -> np.ndarray:
    """Trichotomous controller array over all cells: {-1, 0, +1}."""
    bv = engine.board_values
    return (bv > margin).astype(np.int8) - (bv < -margin).astype(np.int8)


def count_controller_changes(prev: np.ndarray, cur: np.ndarray) -> int:
    """Cells whose controller sign differs between two snapshots."""
    return int(np.count_nonzero(prev != cur))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest experiments/fc_phase15/test_phase15_metrics.py -v`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add experiments/fc_phase15/metrics.py experiments/fc_phase15/test_phase15_metrics.py
git commit -m "feat(phase-1.5): control-flip-rate screen metrics + tests"
```

---

### Task 10: 5-arm mechanical screen script

**Files:**
- Create: `experiments/fc_phase15/run_screen.py`

- [ ] **Step 1: Write run_screen.py**

Mirror `experiments/field_connect_probe/run_screen.py` (same trainer config, seat-swap halves, hard cap, pie-swap exclusion), with these deltas — the full file:

```python
"""FC phase-1.5 — 5-arm mechanical screen (spec §6b, PREREGISTRATION.md).

Per arm (c1, c2, c3, a0, a1) x 3 PPO seeds: train (budget 5000), then an
instrumented sampled trained-vs-trained mirror eval (n=200, seat-swap)
recording the four pre-registered signals:

  lead_changes, game_length, control_flip_rate, connection_win_fraction

plus sanity columns (seat_balance, draw_rate, trained_vs_random,
capture_events as a diagnostic). A0/A1 are retrained from their
probe-calibrated defs — no probe checkpoints exist — so every number in the
comparison table comes from identical instrumentation.

Usage:
    python experiments/fc_phase15/run_screen.py \
        [--budget 5000] [--eval-episodes 200] [--seeds 42,43,44] \
        [--games-dir experiments/fc_phase15/games/calibrated]
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from config import MetricsConfig, TrainingConfig  # noqa: E402
from game_engine.factory import create_engine  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from training.trainer import SelfPlayTrainer  # noqa: E402

from experiments.field_connect_probe.metrics import (  # noqa: E402
    count_lead_changes,
    progress_diff_field,
    progress_diff_threshold,
)
from experiments.fc_phase15.metrics import (  # noqa: E402
    controller_signs,
    count_controller_changes,
)

HERE = Path(__file__).resolve().parent
ARMS = ("c1_field_flip", "c2_contested_terrain", "c3_control_capture",
        "a0_baseline", "a1_field_connect")
C_ARMS = ("c1_field_flip", "c2_contested_terrain", "c3_control_capture")
A0 = "a0_baseline"
LENGTH_BAND = (30.0, 160.0)
CONNECTION_WIN_FLOOR = 0.80
SCREEN_GO_MIN = 3


def instrumented_episode(game: GameDefV2, a0, a1) -> dict:
    engine = create_engine(game)
    obs = engine.reset()
    agents = [a0, a1]
    is_field = game.win_condition.condition_type == "field_connection"
    margin = getattr(game.win_condition, "control_margin", 0.0)
    prev_counts = list(engine.piece_counts)
    prev_signs = controller_signs(engine, margin)
    captures = 0
    diffs: list[float] = []
    flips: list[int] = []
    hard_cap = 2 * game.max_game_steps

    while not engine.done and engine.step_count < hard_cap:
        legal = engine.get_legal_actions()
        if not legal:
            raise RuntimeError(
                f"no legal actions with done=False at step "
                f"{engine.step_count} ({game.game_id})"
            )
        agent = agents[engine.get_current_player()]
        action, _, _ = agent.select_action(
            obs, legal_actions=legal, deterministic=False,
        )
        obs, _, done, info = engine.step(action)
        cur_signs = controller_signs(engine, margin)
        if not info.get("pie_swap"):
            for pidx in (0, 1):
                drop = prev_counts[pidx] - engine.piece_counts[pidx]
                if drop > 0:
                    captures += drop
            diffs.append(
                progress_diff_field(engine, margin) if is_field
                else progress_diff_threshold(engine)
            )
            flips.append(count_controller_changes(prev_signs, cur_signs))
        prev_counts = list(engine.piece_counts)
        prev_signs = cur_signs

    winner = engine._winner
    timeout = engine._ended_by_max_turns
    return dict(
        length=engine.step_count,
        captures=captures,
        lead_changes=count_lead_changes(diffs),
        control_flips=float(np.mean(flips)) if flips else 0.0,
        connection_win=(winner is not None and not timeout),
        draw=(winner is None),
        p1_win=(winner == 1),
    )


def screen_one(game: GameDefV2, seed: int, budget: int, eval_eps: int) -> dict:
    cfg = TrainingConfig(training_budget=budget, eval_episodes=100)
    mcfg = MetricsConfig(learning_curve_checkpoints=2)
    trainer = SelfPlayTrainer(game, cfg, mcfg, seed=seed)
    t0 = time.time()
    trainer.train()
    diag = trainer.evaluate(num_episodes=100)

    half = eval_eps // 2
    eps = []
    for i in range(eval_eps):
        if i < half:
            a, b = trainer.agents[0], trainer.agents[1]
        else:
            a, b = trainer.agents[1], trainer.agents[0]
        eps.append(instrumented_episode(game, a, b))

    n = max(len(eps), 1)
    p1_wr = sum(e["p1_win"] for e in eps) / n
    return dict(
        game_id=game.game_id,
        seed=seed,
        game_length=float(np.mean([e["length"] for e in eps])),
        lead_changes=float(np.mean([e["lead_changes"] for e in eps])),
        control_flip_rate=float(np.mean([e["control_flips"] for e in eps])),
        connection_win_fraction=sum(e["connection_win"] for e in eps) / n,
        capture_events=float(np.mean([e["captures"] for e in eps])),
        seat_balance=abs(p1_wr - 0.5),
        draw_rate=sum(e["draw"] for e in eps) / n,
        trained_vs_random=float(diag.get("trained_vs_random_winrate", -1.0)),
        elapsed_s=time.time() - t0,
    )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--budget", type=int, default=5000)
    p.add_argument("--eval-episodes", type=int, default=200)
    p.add_argument("--seeds", default="42,43,44")
    p.add_argument("--games-dir", type=Path,
                   default=HERE / "games" / "calibrated")
    args = p.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]

    rows = []
    for name in ARMS:
        path = args.games_dir / f"{name}.json"
        game = GameDefV2.from_dict(json.load(open(path)))
        for seed in seeds:
            r = screen_one(game, seed, args.budget, args.eval_episodes)
            rows.append(r)
            print(f"{name} seed={seed}: " + ", ".join(
                f"{k}={v:.3f}" for k, v in r.items()
                if isinstance(v, float)), flush=True)

    with open(HERE / "screen_results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    def agg(gid_suffix: str, key: str) -> float:
        vals = [r[key] for r in rows if r["game_id"].endswith(gid_suffix)]
        return float(np.mean(vals))

    BAND_MID = (LENGTH_BAND[0] + LENGTH_BAND[1]) / 2.0

    def length_win(x_c: float, x_0: float) -> bool:
        return (LENGTH_BAND[0] <= x_c <= LENGTH_BAND[1]
                and not (LENGTH_BAND[0] <= x_0 <= LENGTH_BAND[1]
                         and abs(x_0 - BAND_MID) < abs(x_c - BAND_MID)))

    md = ["# FC phase-1.5 — mechanical screen", "",
          f"PPO budget {args.budget}, seeds {seeds}, instrumented sampled "
          f"mirror eval n={args.eval_episodes}/seed. Bars per "
          f"PREREGISTRATION.md.", ""]
    ranking = []
    for arm in C_ARMS:
        wins = 0
        md += [f"## {arm} vs {A0}", "",
               "| signal | arm | A0 | win? |", "|---|---:|---:|:---:|"]
        checks = [
            ("lead_changes", agg(arm, "lead_changes") > agg(A0, "lead_changes")),
            ("game_length", length_win(agg(arm, "game_length"),
                                       agg(A0, "game_length"))),
            ("control_flip_rate", agg(arm, "control_flip_rate")
                                  > agg(A0, "control_flip_rate")),
            ("connection_win_fraction", agg(arm, "connection_win_fraction")
                                        >= CONNECTION_WIN_FLOOR),
        ]
        for key, ok in checks:
            wins += ok
            md.append(f"| {key} | {agg(arm, key):.3f} | {agg(A0, key):.3f} "
                      f"| {'YES' if ok else 'no'} |")
        sane = (agg(arm, "trained_vs_random") >= 0.80
                and agg(arm, "draw_rate") <= 0.05
                and agg(arm, "seat_balance") <= 0.10)
        md += ["", f"**{wins}/4 signals; sanity "
                   f"{'PASS' if sane else 'FAIL'}.**", ""]
        if wins >= SCREEN_GO_MIN and sane:
            ranking.append((agg(arm, "control_flip_rate"), arm, wins))

    md += ["## Reference rows (A0/A1, new instrumentation)", ""]
    for ref in (A0, "a1_field_connect"):
        md.append(f"- {ref}: " + ", ".join(
            f"{k}={agg(ref, k):.3f}" for k in
            ("lead_changes", "game_length", "control_flip_rate",
             "connection_win_fraction", "trained_vs_random")))
    if ranking:
        ranking.sort(reverse=True)
        md += ["", f"**WINNER (advances to blind A/B): {ranking[0][1]}** "
                   f"(ranked by control_flip_rate among >=3/4 arms; "
                   f"PREREGISTRATION.md).", ""]
    else:
        md += ["", "**NO ARM CLEARED 3/4 + sanity — screen NO-GO; "
                   "stop before the blind campaign (spec §6b).**", ""]
    (HERE / "screen_results.md").write_text("\n".join(md))
    print("\n".join(md[-4:]))


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Plumbing dry-run (tiny budget — NOT the registered run)**

Run: `python experiments/fc_phase15/run_screen.py --budget 200 --eval-episodes 6 --seeds 42 --games-dir experiments/fc_phase15/games`
Expected: completes in a few minutes, prints one row per arm, writes both output files. Numbers are meaningless at this budget — verify only that no exceptions occur and `screen_results.md` renders the three comparison tables plus the winner/NO-GO line.

- [ ] **Step 3: Discard dry-run outputs and commit the script only**

```bash
git checkout -- experiments/fc_phase15/screen_results.csv 2>/dev/null; rm -f experiments/fc_phase15/screen_results.csv experiments/fc_phase15/screen_results.md
git add experiments/fc_phase15/run_screen.py
git commit -m "feat(phase-1.5): 5-arm mechanical screen with pre-registered 4-signal table + ranking"
```

---

### Task 11: Komi calibration for the C arms

**Files:**
- Create: `experiments/fc_phase15/calibrate.py`
- Create (generated): `experiments/fc_phase15/games/calibrated/*.json`, `experiments/fc_phase15/calibration.md`

- [ ] **Step 1: Write calibrate.py**

Adapt `experiments/field_connect_probe/calibrate.py` — import its `sampled_mirror_eval` rather than copying it. Differences only: `GAMES = ("c1_field_flip", "c2_contested_terrain", "c3_control_capture")`, `HERE = Path(__file__).resolve().parent`, games loaded from `HERE / "games"`, calibrated JSONs written to `HERE / "games" / "calibrated"`, and A0/A1 copied through unchanged (already calibrated):

```python
"""FC phase-1.5 — komi calibration for the three C arms (spec §6a).

Methodology identical to the probe (sampled_mirror_eval imported from it):
sweep komi_p2; train PPO (budget 3000, seed 42); pick the smallest komi
with seat bias <= 0.10. Komi only enters the timeout tiebreak — pie is the
primary balancer for connection wins (probe: both arms passed at 0.00).
A0/A1 are copied through with their probe komi untouched.

Usage:
    python experiments/fc_phase15/calibrate.py \
        [--grid "0.0,0.05,0.10,0.15,0.20,0.25,0.30"] \
        [--budget 3000] [--eval-episodes 200] [--seed 42]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from config import MetricsConfig, TrainingConfig  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from training.trainer import SelfPlayTrainer  # noqa: E402

from experiments.field_connect_probe.calibrate import (  # noqa: E402
    sampled_mirror_eval,
)

HERE = Path(__file__).resolve().parent
GAMES = ("c1_field_flip", "c2_contested_terrain", "c3_control_capture")
PASSTHROUGH = ("a0_baseline.json", "a1_field_connect.json")
BIAS_PASS = 0.10


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--grid", default="0.0,0.05,0.10,0.15,0.20,0.25,0.30")
    p.add_argument("--budget", type=int, default=3000)
    p.add_argument("--eval-episodes", type=int, default=200)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    grid = [float(x) for x in args.grid.split(",")]

    out_dir = HERE / "games" / "calibrated"
    out_dir.mkdir(parents=True, exist_ok=True)
    report = ["# FC phase-1.5 — komi calibration", "",
              f"budget {args.budget}, seed {args.seed}, "
              f"n={args.eval_episodes}, pass bias <= {BIAS_PASS}", "",
              "| arm | komi | p1_winrate | bias | draws | verdict |",
              "|---|---:|---:|---:|---:|:---:|"]
    for name in GAMES:
        base = json.load(open(HERE / "games" / f"{name}.json"))
        chosen = None
        for komi in grid:
            d = dict(base)
            d["komi_p2"] = komi
            game = GameDefV2.from_dict(d)
            cfg = TrainingConfig(training_budget=args.budget,
                                 eval_episodes=100)
            trainer = SelfPlayTrainer(game, cfg,
                                      MetricsConfig(
                                          learning_curve_checkpoints=2),
                                      seed=args.seed)
            trainer.train()
            p1_wr, draws, _ = sampled_mirror_eval(
                trainer, args.eval_episodes, game.max_game_steps)
            bias = abs(p1_wr - 0.5)
            ok = bias <= BIAS_PASS
            report.append(f"| {name} | {komi:.2f} | {p1_wr:.3f} "
                          f"| {bias:.3f} | {draws:.3f} "
                          f"| {'PASS' if ok else 'no'} |")
            print(report[-1], flush=True)
            if ok and chosen is None:
                chosen = komi
                json.dump(d, open(out_dir / f"{name}.json", "w"), indent=2)
                break
        if chosen is None:
            report.append(f"| {name} | — | — | — | — | **BIAS_UNRESOLVED** |")
            print(f"WARNING: {name} BIAS_UNRESOLVED", flush=True)
    for src in PASSTHROUGH:
        shutil.copy(HERE / "games" / src, out_dir / src)
    (HERE / "calibration.md").write_text("\n".join(report) + "\n")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run calibration (~10-20 min: stops at the first passing komi per arm; probe precedent says 0.00 passes because pie balances)**

Run: `python experiments/fc_phase15/calibrate.py`
Expected: per-arm PASS rows (most likely at komi 0.00), five JSONs in `games/calibrated/`, `calibration.md` written. If any arm prints BIAS_UNRESOLVED, stop and surface it — that arm is invalidated by the sanity gate (PREREGISTRATION.md) and the screen proceeds with the remaining arms.

- [ ] **Step 3: Commit**

```bash
git add experiments/fc_phase15/calibrate.py experiments/fc_phase15/games/calibrated/ experiments/fc_phase15/calibration.md
git commit -m "results(phase-1.5): komi calibration for C1/C2/C3 + A0/A1 passthrough"
```

---

### Task 12: Run the registered mechanical screen

**Files:**
- Create (generated): `experiments/fc_phase15/screen_results.csv`, `experiments/fc_phase15/screen_results.md`

- [ ] **Step 1: Run the screen at the registered config (~60-90 min: 5 arms × 3 seeds; probe was ~25 min for 2 arms × 3 seeds)**

Run: `python experiments/fc_phase15/run_screen.py 2>&1 | tee /tmp/p15_screen.log`
Expected: 15 result rows, then either `WINNER (advances to blind A/B): <arm>` or the NO-GO line.

- [ ] **Step 2: Commit results verbatim (win or lose — registered output)**

```bash
git add experiments/fc_phase15/screen_results.csv experiments/fc_phase15/screen_results.md
git commit -m "results(phase-1.5): mechanical screen — <fill in: winner arm + signal counts, or screen NO-GO>"
```

- [ ] **Step 3: Branch on the outcome**

- **Winner exists** → continue to Task 13.
- **No arm cleared 3/4 + sanity** → skip Tasks 13–14's blind campaign; write `experiments/fc_phase15/RESULTS.md` recording the screen NO-GO per spec §6b ("stop before the blind"), update the spec's Status line, commit, and stop. The §7 decision rule is then applied with the screen as the deciding leg (this is the NO-GO branch: escalate past the Field-Connect family).

---

### Task 13: Blind eval pack (only after a screen winner exists)

**Files:**
- Create: `experiments/fc_phase15/eval_helper.py` (adapted copy of `experiments/field_connect_probe/eval_helper.py`)
- Create: `evaluations/phase15_ab/play.py`, `evaluations/phase15_ab/BRIEFING.md`, `evaluations/phase15_ab/TEMPLATE_team-N_game{K,M,T}.md`

- [ ] **Step 1: Adapt eval_helper.py**

Copy `experiments/field_connect_probe/eval_helper.py` to `experiments/fc_phase15/eval_helper.py` and change ONLY:
- The `BLIND` dict: three labels mapping to the calibrated JSONs, with the assignment of {K, M, T} → {a0_baseline, a1_field_connect, <winner>} drawn by the orchestrator (any fixed permutation chosen without looking at per-arm results beyond the winner's identity), e.g.:

```python
BLIND = {
    "K": "a1_field_connect",      # SEALED — evaluators must not read this file
    "M": "<winner-arm-json-name>",
    "T": "a0_baseline",
}
GAMES_DIR = Path(__file__).resolve().parent / "games" / "calibrated"
```

- The argparse choices: `choices=["K", "M", "T", "k", "m", "t"]`.
- The rules-summary renderer: verify it describes the new mechanics neutrally from the game def (capture_type/constraint names must NOT leak which arm is "new" — describe mechanics, never provenance). Audit every output string for the words "probe", "baseline", "new", "treatment", "A0", "A1", "C1/2/3" — none may appear in evaluator-visible output.

- [ ] **Step 2: Create the pack**

`evaluations/phase15_ab/play.py` (shim, mirrors probe):

```python
"""Phase-1.5 A/B — evaluator entry point. Usage:
    python evaluations/phase15_ab/play.py --game K [--moves "..."] [--rules] [--control]
"""
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
runpy.run_path(str(ROOT / "experiments" / "fc_phase15"
                   / "eval_helper.py"), run_name="__main__")
```

`BRIEFING.md`: copy `evaluations/probe_ab/BRIEFING.md`, change game labels Q/Z → K/M/T (three games per team, not two), and keep the standing instructions verbatim: evaluators read ONLY `evaluations/phase15_ab/` files; they must not read `experiments/`, git history, or specs; verdict files use the same rubric (Overall 1–10 plus the dimension scores used in run21/probe — copy the rubric block from the probe templates unchanged).

Six templates: `TEMPLATE_team-N_gameK.md`, `TEMPLATE_team-N_gameM.md`, `TEMPLATE_team-N_gameT.md` — copy a probe template per label, find/replace the label letter, keep everything else symmetric across the three.

- [ ] **Step 3: Verify blindness mechanically**

Run: `python evaluations/phase15_ab/play.py --game K --rules && python evaluations/phase15_ab/play.py --game M --rules && python evaluations/phase15_ab/play.py --game T --rules`
Expected: three rules summaries print; grep the combined output for leak words: `python evaluations/phase15_ab/play.py --game K --rules | grep -iE "probe|baseline|treatment|winner|a0|a1|c1|c2|c3|flip|replace|phase"` — adjust the renderer until only mechanic-neutral language remains (e.g. "stones standing on opponent-dominated cells change colour" is fine; "field_flip (C1, the new arm)" is a leak). Note: the mechanic itself may be described; its *novelty/provenance* may not.

- [ ] **Step 4: Commit**

```bash
git add experiments/fc_phase15/eval_helper.py evaluations/phase15_ab/
git commit -m "feat(phase-1.5): blind 3-game eval pack (labels K/M/T, sealed mapping, neutral renderer)"
```

---

### Task 14: Blind campaign + readout

**Files:**
- Create: `evaluations/phase15_ab/team-{1,2}_game{K,M,T}.md` (verdicts, filed by the teams)
- Create: `experiments/fc_phase15/RESULTS.md`
- Modify: `docs/superpowers/specs/2026-06-10-field-connect-phase15-design.md` (Status line)

- [ ] **Step 1: Run the blind campaign (agent teams — outside this coding loop)**

Protocol identical to the probe + R21 campaigns: 2 independent agent teams in tmux (user's agent-team mode), each plays all three games via `evaluations/phase15_ab/play.py`, reads only `evaluations/phase15_ab/`, files verdicts from the templates. Orchestrator (main session) does not discuss arm identities with teams and opens the `BLIND` mapping only after all 6 verdicts are filed. Budget: ~50 min (probe's 2-game campaign was ~35 min).

- [ ] **Step 2: Unblind and apply spec §7 verbatim**

Compute campaign means Z (winner arm), Y (a1), Q (a0) across both teams' Overall scores. Apply, in order: replicate-check corner case → GO → PARTIAL → NO-GO, quoting the rule text from the spec. No re-interpretation: if a result feels surprising, record it as surprising — the rule still decides.

- [ ] **Step 3: Write RESULTS.md**

Structure mirrors `experiments/field_connect_probe/RESULTS.md`: decision banner; screen table; blind table (per-team + means for all three games); honest synthesis (including convergent blind findings and anything the teams named unprompted); pre-registration audit (what was locked when, commit hashes; confirm bars unaltered).

- [ ] **Step 4: Update the spec Status line and commit**

```bash
git add experiments/fc_phase15/RESULTS.md evaluations/phase15_ab/team-*.md docs/superpowers/specs/2026-06-10-field-connect-phase15-design.md
git commit -m "results(phase-1.5): blind A/B readout + <GO|PARTIAL|NO-GO> per pre-registered §7"
```

- [ ] **Step 5: Surface the outcome + propose follow-ups**

Report the decision branch and its consequence (GO → spec §12 substrate work un-gates; PARTIAL → one parameterization iteration; NO-GO → escalate past Field-Connect). Propose a push to origin/main at this break point.
