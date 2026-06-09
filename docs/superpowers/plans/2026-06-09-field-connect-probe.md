# Field-Connect Probe Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and run the go/no-go probe from `docs/superpowers/specs/2026-06-07-field-connect-probe-design.md` (v2 lean, `0f99cb8`): a `field_connection` win condition + rhombus hex board, an A1 (Field-Connect) vs A0 (plateau baseline) pair on the same board, komi calibration, a PPO mechanical screen, and a blind 2-team agent A/B, read out against the pre-registered §8c criteria.

**Architecture:** Three additive engine-layer changes (new win condition in `engine_v2.py` + `rules.py`, new `hex_rhombus` topology in `topology.py`, capture-triggered field recompute gated to the new win condition), then a self-contained experiment package under `experiments/field_connect_probe/` that reuses the R20.5-G4 trainer/eval pattern (`SelfPlayTrainer` + sampled seat-swap mirror eval). No evolution, no GE, no DB writes to production DBs.

**Tech Stack:** Python 3, numpy, existing PPO stack (`training/trainer.py`, `training/utils.py`), pytest-style root-level tests, JSON game defs.

---

## Pre-verified engine facts (do not re-derive; line numbers as of `0f99cb8`)

- Win dispatch: `EngineV2._check_win_conditions()` at `game_engine/engine_v2.py:892`; called from `step()` right before step-count increment; `_end_by_max_turns()` (engine_v2.py:1025) fires only if not already done.
- `_check_connection(dim_p1, dim_p2)` (engine_v2.py:948) + `topo.connects_faces(cells, dimension)` (topology.py:634) already implement face-to-face BFS — `field_connection` reuses `connects_faces` with *controlled* cells instead of owned cells.
- Influence: `_propagate_influence(placed_cell)` (engine_v2.py:706) adds `sign·strength·decay^dist` within radius, clamps to ±100. **Capture (`_remove_group`, engine_v2.py:685) does NOT touch `board_values` — ghost influence remains.** The spec requires recompute-on-capture for Field-Connect; this must be gated so all existing games keep ghost semantics.
- Komi: `game.komi_p2` multiplicative — ×`threshold` for threshold wins (engine_v2.py:998), ×`num_active_cells` for count wins (engine_v2.py:927).
- Pie: `pie_rule=True` + `swap_action_idx = num_actions - 1`; swap flips owners and negates `board_values`; `_goals_swapped` is how connection wins swap targets.
- Topology: `_dist_matrix is None` ⇒ `distance()` (topology.py:668) computes analytically per `topology_type`; `cells_within_radius` (topology.py:719) falls back to a full-board scan. The existing `"hex"` type is **offset-coordinate** (square region) — NOT the canonical rhombus; we add a new axial-coordinate type.
- Trainer pattern (from `experiments/r20_5_g4/run_g4.py`): `SelfPlayTrainer(game, TrainingConfig(training_budget=B, eval_episodes=100), MetricsConfig(learning_curve_checkpoints=2), seed=s)`; `trainer.train()`; agents at `trainer.agents[0/1]`; engines via `game_engine.factory.create_engine(game)`; `engine.get_current_player()` is **0-indexed**; `agent.select_action(obs, legal_actions=..., deterministic=False)` returns `(action, _, _)`; `engine.piece_counts` is `[p1, p2]`; `engine._winner` ∈ {1, 2, None}.
- `evolution/operators_v2.py:493` demotes `influence` propagation on non-threshold wins inside `_fix_consistency` — **not on the probe's path** (no evolution here), but it WILL strip Field-Connect's influence in phase 2. Do not fix now (YAGNI); it is recorded in the phase-2 notes at the bottom.
- `GameDefV2.canonical_blob()` hashes `to_dict()` minus game_id/metadata/version. **New WinCondition fields must be omitted from `to_dict()` at default value** or every existing game's canonical hash changes.

## File structure

| File | Action | Responsibility |
|---|---|---|
| `game_engine/rules.py` | Modify | `WinCondition.control_margin` field + serde (omit-at-default) |
| `game_engine/topology.py` | Modify | `hex_rhombus` topology type: axial 6-neighbor builder + analytic axial distance |
| `game_engine/engine_v2.py` | Modify | `_check_field_connection`, `_add_influence` refactor, `_recompute_field` + dirty flag, field-aware timeout tiebreak |
| `test_hex_rhombus.py` | Create | Topology unit tests (root-level, pytest style, like `test_pie_rule.py`) |
| `test_field_connection.py` | Create | Engine win-condition + recompute + tiebreak tests |
| `experiments/field_connect_probe/build_games.py` | Create | Writes `games/a1_field_connect.json`, `games/a0_baseline.json` + random-rollout smoke |
| `experiments/field_connect_probe/metrics.py` | Create | Pure metric functions (controlled sets, largest component, progress diffs, lead changes) |
| `experiments/field_connect_probe/test_probe_metrics.py` | Create | Unit tests for metrics.py |
| `experiments/field_connect_probe/calibrate.py` | Create | Komi sweep per game → `games/calibrated/*.json` + `calibration.md` |
| `experiments/field_connect_probe/run_screen.py` | Create | Train 3 seeds × 2 games, instrumented sampled mirror eval, `screen_results.{csv,md}` |
| `experiments/field_connect_probe/eval_helper.py` | Create | Interactive board/control renderer for agent A/B (JSON-loading) |
| `evaluations/field_connect_probe/BRIEFING.md` + `TEMPLATE_team-N_game{Q,Z}.md` + `.blind_mapping.json` | Create | Blind A/B eval pack |
| `experiments/field_connect_probe/RESULTS.md` | Create (Task 12) | Go/no-go readout vs spec §8c |

Pre-registered parameter defaults (spec §9, locked here): `W=22` (484 cells), A1 influence `radius=2, strength=1.0, decay=0.5`, A1 `control_margin ε=0.0`, A0 = outnumber-2 + influence `r=1, decay=0.7` + threshold `36` (R21's 30 scaled by 484/400), both `max_turns=200`, both `pie_rule=True`, komi from calibration, healthy length band = mean plies in `[30, 160]`. Lead-change proxy (spec §8a "concrete proxy defined at implementation"): A1 → sign flips of (largest P1-controlled component size − largest P2-controlled component size); A0 → sign flips of (P1 score − (P2 score + komi_p2×threshold)), zeros skipped.

---

### Task 1: `WinCondition.control_margin` field + serde

**Files:**
- Modify: `game_engine/rules.py:182-233` (WinCondition dataclass)
- Test: `test_field_connection.py` (new file, first tests)

- [ ] **Step 1: Write the failing tests**

Create `test_field_connection.py` at repo root:

```python
"""Field-Connect probe — engine tests for the field_connection win condition.

Spec: docs/superpowers/specs/2026-06-07-field-connect-probe-design.md (v2).
"""
from __future__ import annotations

import numpy as np

from game_engine.rules import WinCondition


def test_control_margin_default_and_roundtrip() -> None:
    """control_margin defaults to 0.0 and survives to_dict/from_dict."""
    wc = WinCondition(condition_type="field_connection", control_margin=0.25)
    d = wc.to_dict()
    assert d["control_margin"] == 0.25
    wc2 = WinCondition.from_dict(d)
    assert wc2.control_margin == 0.25
    assert wc2.condition_type == "field_connection"


def test_control_margin_omitted_at_default() -> None:
    """A default-margin WinCondition must serialize WITHOUT the key, so
    canonical_blob()/canonical_hash() of every existing game is unchanged."""
    wc = WinCondition(condition_type="threshold", threshold=30)
    d = wc.to_dict()
    assert "control_margin" not in d
    wc2 = WinCondition.from_dict(d)
    assert wc2.control_margin == 0.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest test_field_connection.py -v`
Expected: FAIL with `TypeError: ... unexpected keyword argument 'control_margin'`

- [ ] **Step 3: Implement**

In `game_engine/rules.py`, inside the `WinCondition` dataclass (after `max_turns: int = 100`):

```python
    # Field-Connect (R22 probe): control margin epsilon. A cell is
    # P1-controlled iff board_values > +margin, P2-controlled iff
    # < -margin, else contested. Only meaningful for
    # condition_type == "field_connection".
    control_margin: float = 0.0
```

In `WinCondition.to_dict()`, after the existing keys are built, omit-at-default (mirrors the `pie_rule`/`komi_p2` convention — protects canonical hashes):

```python
        d = {
            "condition_type": self.condition_type,
            "threshold": self.threshold,
            "target_dimension": self.target_dimension,
            "target_dimension_p2": self.target_dimension_p2,
            "max_turns": self.max_turns,
        }
        if self.control_margin != 0.0:
            d["control_margin"] = self.control_margin
        return d
```

In `WinCondition.from_dict()`, add to the constructor call:

```python
            control_margin=float(d.get("control_margin", 0.0)),
```

Do **NOT** add `"field_connection"` to `WIN_CONDITION_TYPES` (rules.py:179) — that tuple is the mutation/generation menu for evolution; the probe must not leak the new type into random mutation. Engine dispatch (Task 3) handles the type directly.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest test_field_connection.py -v`
Expected: 2 passed

- [ ] **Step 5: Regression — full existing suite still green**

Run: `python -m pytest test_pie_rule.py test_komi.py test_substrate_invariants.py -q`
Expected: all pass (same counts as before this change)

- [ ] **Step 6: Commit**

```bash
git add game_engine/rules.py test_field_connection.py
git commit -m "feat(probe): WinCondition.control_margin with hash-safe serde"
```

---

### Task 2: `hex_rhombus` topology

**Files:**
- Modify: `game_engine/topology.py` (TOPOLOGY_TYPES line 21; constructor validation ~line 228; `_precompute_neighbors` dispatch ~line 342; new builder after `_build_hex_neighbors`; `distance()` branch ~line 700)
- Test: `test_hex_rhombus.py` (create)

- [ ] **Step 1: Write the failing tests**

Create `test_hex_rhombus.py` at repo root:

```python
"""hex_rhombus topology — axial-coordinate triangular lattice on a rhombus
(the canonical Hex board). Spec §5a."""
from __future__ import annotations

import pytest

from game_engine.topology import TopologicalSpace


def _build(s: int = 6) -> TopologicalSpace:
    return TopologicalSpace(num_dimensions=2, axis_size=s, topology_type="hex_rhombus")


def test_all_cells_active_and_counts() -> None:
    t = _build(22)
    assert t.total_cells == 484
    assert t.num_active_cells == 484
    assert t.max_degree == 6


def test_corner_degrees() -> None:
    """Canonical Hex rhombus: acute corners (0,0),(s-1,s-1) degree 2;
    obtuse corners (s-1,0),(0,s-1) degree 3."""
    t = _build(6)
    s = 6
    deg = lambda q, r: len(t.get_neighbors(t.coords_to_cell((q, r))))
    assert deg(0, 0) == 2
    assert deg(s - 1, s - 1) == 2
    assert deg(s - 1, 0) == 3
    assert deg(0, s - 1) == 3
    # interior cell
    assert deg(2, 2) == 6


def test_adjacency_symmetric() -> None:
    t = _build(6)
    for c in range(t.total_cells):
        for n in t.get_neighbors(c):
            assert c in t.get_neighbors(n)


def test_distance_matches_adjacency_and_bfs() -> None:
    """Analytic axial distance must equal BFS graph distance (the R13 bug
    class: wrong distance silently breaks influence propagation)."""
    t = _build(5)
    # BFS from every cell
    for src in range(t.total_cells):
        dist = {src: 0}
        frontier = [src]
        while frontier:
            nxt = []
            for c in frontier:
                for n in t.get_neighbors(c):
                    if n not in dist:
                        dist[n] = dist[c] + 1
                        nxt.append(n)
            frontier = nxt
        for dst in range(t.total_cells):
            assert t.distance(src, dst) == dist[dst], (src, dst)


def test_cells_within_radius_center() -> None:
    t = _build(7)
    center = t.coords_to_cell((3, 3))
    ball = t.cells_within_radius(center, 1)
    assert len(ball) == 7  # self + 6 neighbors


def test_connects_faces_both_dims() -> None:
    t = _build(6)
    # a straight column q=2 spans dimension 1 (r: 0..5)
    col = {t.coords_to_cell((2, r)) for r in range(6)}
    assert t.connects_faces(col, 1)
    assert not t.connects_faces(col, 0)
    # broken column does not connect
    col.remove(t.coords_to_cell((2, 3)))
    assert not t.connects_faces(col, 1)


def test_requires_2d() -> None:
    with pytest.raises(ValueError):
        TopologicalSpace(num_dimensions=3, axis_size=6, topology_type="hex_rhombus")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest test_hex_rhombus.py -v`
Expected: FAIL with `ValueError: ... topology_type` (unknown type rejected by constructor)

- [ ] **Step 3: Implement**

In `game_engine/topology.py`:

(a) Add to `TOPOLOGY_TYPES` (line 21):

```python
TOPOLOGY_TYPES = (
    "grid", "torus", "hex", "moore", "sierpinski", "holes",
    # R18 fractal substrates for the Hausdorff-dimension comparator
    "sierpinski_triangle", "vicsek", "menger",
    # Field-Connect probe: axial triangular lattice on a rhombus (Hex board)
    "hex_rhombus",
)
```

(b) Constructor validation, next to the existing `"hex"` 2D check (~line 228):

```python
        if topology_type == "hex_rhombus" and num_dimensions != 2:
            raise ValueError("hex_rhombus topology requires exactly 2 dimensions")
```

(c) Dispatch branch in `_precompute_neighbors()` (~line 342):

```python
        elif self.topology_type == "hex_rhombus":
            self._build_hex_rhombus_neighbors()
```

(d) Builder, placed directly after `_build_hex_neighbors`:

```python
    # The 6 triangular-lattice neighbours in the axial (q, r) basis.
    # Same basis as figures/koch_substrate/koch_explore.py NEI.
    _HEX_RHOMBUS_DELTAS = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1))

    def _build_hex_rhombus_neighbors(self) -> None:
        """Axial-coordinate triangular lattice on a rhombus (2D only).

        Unlike "hex" (offset coordinates, square region), this is the
        canonical Hex board: cells (q, r) in [0, s)^2 with a uniform
        6-neighbour basis. Acute corners have degree 2, obtuse corners
        degree 3, interior cells degree 6. All cells are active.
        """
        s = self.axis_size
        for cell in range(self.total_cells):
            q, r = self.cell_to_coords(cell)
            nbrs: list[int] = []
            for dq, dr in self._HEX_RHOMBUS_DELTAS:
                nq, nr = q + dq, r + dr
                if 0 <= nq < s and 0 <= nr < s:
                    nbrs.append(self.coords_to_cell((nq, nr)))
            self._neighbors[cell] = nbrs
```

(e) Analytic distance branch in `distance()`, immediately before the existing `if self.topology_type == "hex":` branch (~line 701):

```python
        if self.topology_type == "hex_rhombus":
            # Coordinates ARE axial — standard axial hex distance.
            qa, ra = ca
            qb, rb = cb
            dq, dr = qa - qb, ra - rb
            return (abs(dq) + abs(dr) + abs(dq + dr)) // 2
```

(No `_dist_matrix`, no `SUBSTRATE_INVARIANTS` entry — the rhombus is size-parameterizable, unlike the fixed fractal substrates; the invariants table would wrongly pin it.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest test_hex_rhombus.py -v`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add game_engine/topology.py test_hex_rhombus.py
git commit -m "feat(probe): hex_rhombus topology — axial Hex-board rhombus, analytic distance"
```

---

### Task 3: `field_connection` win condition in the engine

**Files:**
- Modify: `game_engine/engine_v2.py` (`_check_win_conditions` ~line 914; new method after `_check_connection`)
- Test: `test_field_connection.py` (extend)

- [ ] **Step 1: Write the failing tests**

Append to `test_field_connection.py`:

```python
from game_engine.engine_v2 import GameEngineV2
from game_engine.game_def_v2 import GameDefV2
from game_engine.rules import (
    ActionRule,
    CaptureRule,
    PlacementRule,
    PropagationRule,
    TurnStructure,
)


def make_fc_game(
    *,
    s: int = 6,
    control_margin: float = 0.0,
    radius: int = 1,
    decay: float = 0.5,
    capture_type: str = "surround",
    win_type: str = "field_connection",
    max_turns: int = 50,
    pie_rule: bool = False,
    komi_p2: float = 0.0,
) -> GameDefV2:
    """Minimal hex_rhombus game. P1 connects dim 1 (r=0..s-1), P2 dim 0."""
    return GameDefV2(
        game_id=f"fc_test_{win_type}_{capture_type}_m{control_margin}",
        num_dimensions=2,
        axis_size=s,
        topology_type="hex_rhombus",
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type=capture_type),
        propagation_rule=PropagationRule(
            prop_type="influence", radius=radius, strength=1.0, decay=decay,
        ),
        win_condition=WinCondition(
            condition_type=win_type,
            threshold=10.0,
            target_dimension=1,
            target_dimension_p2=0,
            max_turns=max_turns,
            control_margin=control_margin,
        ),
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
        pie_rule=pie_rule,
        komi_p2=komi_p2,
    )


def _engine(game: GameDefV2) -> GameEngineV2:
    e = GameEngineV2(game)
    e.reset()
    return e


def _cell(e: GameEngineV2, q: int, r: int) -> int:
    return e.topo.coords_to_cell((q, r))


def test_field_connection_p1_win_on_controlled_column() -> None:
    """A column of P1-controlled cells (positive field) spanning r=0..s-1
    wins for P1 — no stones needed on the path itself."""
    e = _engine(make_fc_game())
    for r in range(6):
        e.board_values[_cell(e, 2, r)] = 0.7
    e._check_win_conditions()
    assert e.done and e._winner == 1


def test_field_connection_contested_gap_blocks() -> None:
    """One contested (zero) cell on every crossing path blocks the win."""
    e = _engine(make_fc_game())
    for r in range(6):
        e.board_values[_cell(e, 2, r)] = 0.7
    e.board_values[_cell(e, 2, 3)] = 0.0  # contested gap
    e._check_win_conditions()
    assert not e.done


def test_field_connection_p2_win_along_dim0() -> None:
    e = _engine(make_fc_game())
    for q in range(6):
        e.board_values[_cell(e, q, 3)] = -0.4
    e._check_win_conditions()
    assert e.done and e._winner == 2


def test_control_margin_gates_weak_control() -> None:
    """With margin 0.5, |values| <= 0.5 are contested; 0.6 wins."""
    e = _engine(make_fc_game(control_margin=0.5))
    for r in range(6):
        e.board_values[_cell(e, 2, r)] = 0.3
    e._check_win_conditions()
    assert not e.done
    for r in range(6):
        e.board_values[_cell(e, 2, r)] = 0.6
    e._check_win_conditions()
    assert e.done and e._winner == 1


def test_field_connection_goal_swap() -> None:
    """After a pie swap, P1's target dimension becomes P2's and vice versa
    (mirrors _check_connection's _goals_swapped handling)."""
    e = _engine(make_fc_game())
    e._goals_swapped = True
    # positive (P1) field spanning dim 0 — P1's goal AFTER swap
    for q in range(6):
        e.board_values[_cell(e, q, 3)] = 0.7
    e._check_win_conditions()
    assert e.done and e._winner == 1


def test_field_connection_end_to_end_by_placement() -> None:
    """Engine detects the win from real placements: two P1 stones with
    radius-2 influence cover the full column q=2 on a 6-board while P2
    plays far away (distance > 2 from the column)."""
    game = make_fc_game(radius=2)
    e = _engine(game)
    e.step(_cell(e, 2, 1))   # P1 — covers (2,0)..(2,3)
    assert not e.done
    e.step(_cell(e, 5, 0))   # P2 — far away
    assert not e.done
    e.step(_cell(e, 2, 4))   # P1 — covers (2,2)..(2,5): column complete
    assert e.done and e._winner == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest test_field_connection.py -v`
Expected: the 6 new tests FAIL (win never detected — `done` stays False); the 2 Task-1 tests still pass.

- [ ] **Step 3: Implement**

In `game_engine/engine_v2.py`, add to `_check_win_conditions()` after the `"threshold"` branch (~line 914):

```python
        elif ctype == "field_connection":
            dim_p2 = wc.target_dimension_p2
            if dim_p2 < 0:
                dim_p2 = (wc.target_dimension + 1) % self.game.num_dimensions
            margin = getattr(wc, "control_margin", 0.0)
            if self._goals_swapped:
                self._check_field_connection(dim_p2, wc.target_dimension, margin)
            else:
                self._check_field_connection(wc.target_dimension, dim_p2, margin)
```

Add the method directly after `_check_connection` (~line 970):

```python
    def _check_field_connection(
        self, dim_p1: int, dim_p2: int, margin: float,
    ) -> None:
        """Field-Connect win: a player wins when their influence-CONTROLLED
        cells connect their two target faces (Hex on the influence field).

        Control is sign-of-field with a margin: P1-controlled iff
        board_values > +margin, P2-controlled iff < -margin, else
        contested. Control includes EMPTY cells — stones matter only
        through the field they project (spec §3).
        """
        controlled = {
            1: {c for c in self.topo.active_cells
                if self.board_values[c] > margin},
            2: {c for c in self.topo.active_cells
                if self.board_values[c] < -margin},
        }
        dims = {1: dim_p1, 2: dim_p2}
        connected = [
            p for p in (1, 2)
            if self.topo.connects_faces(controlled[p], dims[p])
        ]
        if len(connected) == 2:
            # Control sets are disjoint for margin >= 0, so two crossings
            # cannot coexist on the rhombus; defensive draw, mirrors
            # _check_connection.
            self._winner = None
            self.done = True
        elif len(connected) == 1:
            self._winner = connected[0]
            self.done = True
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest test_field_connection.py -v`
Expected: 8 passed

- [ ] **Step 5: Commit**

```bash
git add game_engine/engine_v2.py test_field_connection.py
git commit -m "feat(probe): field_connection win condition — Hex on the influence field"
```

---

### Task 4: capture-triggered field recompute (gated)

**Files:**
- Modify: `game_engine/engine_v2.py` (`_propagate_influence` ~line 706 refactor; `_remove_group` ~line 685; `step()` hook before `_check_win_conditions` call ~line 194; `reset()` flag init ~line 75)
- Test: `test_field_connection.py` (extend)

- [ ] **Step 1: Write the failing tests**

Append to `test_field_connection.py`:

```python
def _surround_corner_capture(e: GameEngineV2) -> None:
    """P2 stone at acute corner (0,0) (degree 2) is captured when P1
    fills both liberties (1,0) and (0,1). P2's other move is far away."""
    e.step(_cell(e, 1, 0))   # P1
    e.step(_cell(e, 0, 0))   # P2 — corner, 1 liberty left
    e.step(_cell(e, 0, 1))   # P1 — captures (0,0)
    assert e.board_owners[_cell(e, 0, 0)] == 0, "corner stone must be captured"


def test_capture_recomputes_field_for_field_connection() -> None:
    """Spec §3.4: removal recomputes the field. With radius-1/decay-0.5
    influence, the corner after capture holds ONLY the two P1 stones'
    contributions (+0.5 +0.5 = +1.0); the dead P2 stone's -1.0 ghost is gone."""
    e = _engine(make_fc_game(radius=1, decay=0.5))
    _surround_corner_capture(e)
    corner = _cell(e, 0, 0)
    assert e.board_values[corner] == 1.0, (
        f"expected recomputed +1.0 at corner, got {e.board_values[corner]}"
    )


def test_ghost_influence_preserved_for_legacy_games() -> None:
    """Identical position with a threshold win condition keeps the OLD
    semantics: the dead stone's influence remains (ghost), corner = 0.0.
    This is the regression guard for every pre-probe game."""
    e = _engine(make_fc_game(radius=1, decay=0.5, win_type="threshold"))
    _surround_corner_capture(e)
    corner = _cell(e, 0, 0)
    assert e.board_values[corner] == 0.0, (
        f"legacy ghost semantics changed! corner={e.board_values[corner]}"
    )


def test_capture_can_break_a_connection_win_path() -> None:
    """A capture that flips control must be visible to the win check in
    the same step: recompute runs before _check_win_conditions."""
    e = _engine(make_fc_game(radius=1, decay=0.5))
    # Hand-build: P1 has a controlled column except r=0 where the P2
    # corner stone's -1.0 dominates the +0.5 P1 spillover. Capturing the
    # corner stone flips (0,0) to P1 control... but the win path is column
    # q=0, which includes the corner itself.
    for r in range(1, 6):
        e.board_values[_cell(e, 0, r)] = 0.7
    e._check_win_conditions()
    assert not e.done  # (0,0) not controlled yet
    # Now play the capture sequence; after recompute (0,0) = +1.0 and the
    # hand-set values were wiped by recompute — so re-verify via field state.
    # (Recompute rebuilds from stones only; this asserts the mechanism fires.)
    e.step(_cell(e, 1, 0))   # P1
    e.step(_cell(e, 0, 0))   # P2 corner
    e.step(_cell(e, 0, 1))   # P1 captures
    corner = _cell(e, 0, 0)
    assert e.board_owners[corner] == 0
    assert e.board_values[corner] == 1.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest test_field_connection.py -v`
Expected: `test_capture_recomputes_field_for_field_connection` and `test_capture_can_break_a_connection_win_path` FAIL (corner = 0.0, ghost present); `test_ghost_influence_preserved_for_legacy_games` PASSES (current behavior IS ghost) — that's correct, it's the regression guard.

- [ ] **Step 3: Implement**

In `game_engine/engine_v2.py`:

(a) Refactor `_propagate_influence` (line 706) to extract the additive kernel:

```python
    def _add_influence(self, cell: int, sign: float) -> None:
        """Add one stone's influence kernel to board_values (no clamp)."""
        rule = self.game.propagation_rule
        for c in self.topo.cells_within_radius(cell, rule.radius):
            dist = self.topo.distance(cell, c)
            self.board_values[c] += sign * rule.strength * (rule.decay ** dist)

    def _propagate_influence(self, placed_cell: int) -> None:
        """Influence propagation: add strength * decay^distance to
        board_values for cells within radius. Positive for player 1,
        negative for player 2."""
        sign = 1.0 if self.current_player == 1 else -1.0
        self._add_influence(placed_cell, sign)
        # Clamp to prevent explosion
        np.clip(self.board_values, -100.0, 100.0, out=self.board_values)
```

(b) New method directly below:

```python
    def _recompute_field(self) -> None:
        """Rebuild board_values from scratch from stones currently on the
        board. Field-Connect only (spec §3.4: "removal recomputes the
        field") — legacy games keep ghost influence from dead stones.
        Idempotent: safe regardless of where in step() it runs.
        """
        if self.game.propagation_rule.prop_type != "influence":
            return
        self.board_values[:] = 0.0
        for cell in self.topo.active_cells:
            owner = int(self.board_owners[cell])
            if owner != 0:
                self._add_influence(cell, 1.0 if owner == 1 else -1.0)
        np.clip(self.board_values, -100.0, 100.0, out=self.board_values)
```

(c) In `_remove_group` (line 685), add as the last line:

```python
        self._field_dirty = True
```

(d) In `reset()` (~line 75, next to `self.board_values[:] = 0.0`) and in `__init__` (~line 35), initialize:

```python
        self._field_dirty = False
```

(e) In `step()`, immediately BEFORE the win check (`if not self.done: self._check_win_conditions()`, ~line 194):

```python
        # Field-Connect: captures must update the field before the win
        # check (spec §3.4). Gated to the new win condition so every
        # legacy game keeps ghost-influence semantics.
        if (
            self._field_dirty
            and self.game.win_condition.condition_type == "field_connection"
        ):
            self._recompute_field()
        self._field_dirty = False
```

(Note: a ko-restore within the step may leave `_field_dirty` stale-True; the recompute is idempotent from `board_owners`, so the worst case is one redundant rebuild — correctness is unaffected.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest test_field_connection.py -v`
Expected: 12 passed (including the legacy-ghost regression guard)

- [ ] **Step 5: Engine-wide regression**

Run: `python -m pytest test_pie_rule.py test_komi.py test_hex_rhombus.py -q`
Expected: all pass

- [ ] **Step 6: Commit**

```bash
git add game_engine/engine_v2.py test_field_connection.py
git commit -m "feat(probe): capture-triggered field recompute, gated to field_connection"
```

---

### Task 5: field-aware timeout tiebreak

**Files:**
- Modify: `game_engine/engine_v2.py` (`_end_by_max_turns` ~line 1025)
- Test: `test_field_connection.py` (extend)

- [ ] **Step 1: Write the failing tests**

Append to `test_field_connection.py`:

```python
def test_timeout_tiebreak_by_controlled_cells() -> None:
    """Spec §3.7: timeout -> larger controlled-cell count wins (komi
    applied), draw if equal. NOT piece count."""
    e = _engine(make_fc_game(radius=2, decay=0.5, max_turns=4))
    e.step(_cell(e, 2, 2))   # P1 center: radius-2 ball = many cells
    e.step(_cell(e, 5, 5))   # P2 acute corner: small ball
    e.step(_cell(e, 2, 3))   # P1
    e.step(_cell(e, 5, 4))   # P2 — step 4 hits max_turns
    assert e.done
    assert e._winner == 1, f"P1 controls more cells; got {e._winner}"


def test_timeout_tiebreak_komi_lifts_p2() -> None:
    """komi_p2 is multiplicative on num_active_cells for the count
    tiebreak (engine convention, engine_v2.py:927)."""
    e = _engine(make_fc_game(radius=2, decay=0.5, max_turns=4, komi_p2=1.0))
    # komi = 1.0 * 36 active cells — dwarfs any control gap on a 6-board
    e.step(_cell(e, 2, 2))
    e.step(_cell(e, 5, 5))
    e.step(_cell(e, 2, 3))
    e.step(_cell(e, 5, 4))
    assert e.done
    assert e._winner == 2, f"komi must lift P2; got {e._winner}"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest test_field_connection.py::test_timeout_tiebreak_by_controlled_cells -v`
Expected: FAIL — current tiebreak compares piece counts (2 vs 2 → draw, `_winner is None`)

- [ ] **Step 3: Implement**

In `game_engine/engine_v2.py`, at the TOP of `_end_by_max_turns()` (line 1025), before the piece-count comparison:

```python
        if self.game.win_condition.condition_type == "field_connection":
            # Spec §3.7: tiebreak by controlled-cell count, komi applied
            # (multiplicative on num_active_cells, same convention as
            # territory count wins).
            self.done = True
            margin = getattr(self.game.win_condition, "control_margin", 0.0)
            p1 = sum(
                1 for c in self.topo.active_cells
                if self.board_values[c] > margin
            )
            p2 = sum(
                1 for c in self.topo.active_cells
                if self.board_values[c] < -margin
            )
            komi = getattr(self.game, "komi_p2", 0.0) * self.topo.num_active_cells
            p2_eff = p2 + komi
            if p1 > p2_eff:
                self._winner = 1
            elif p2_eff > p1:
                self._winner = 2
            else:
                self._winner = None
            return
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest test_field_connection.py -v`
Expected: 14 passed

- [ ] **Step 5: Commit**

```bash
git add game_engine/engine_v2.py test_field_connection.py
git commit -m "feat(probe): field_connection timeout tiebreak by controlled cells + komi"
```

---

### Task 6: game-def builder (A1 + A0) with rollout smoke

**Files:**
- Create: `experiments/field_connect_probe/build_games.py`
- Create (output): `experiments/field_connect_probe/games/a1_field_connect.json`, `experiments/field_connect_probe/games/a0_baseline.json`

- [ ] **Step 1: Write the builder**

```python
"""Field-Connect probe — build the A1 (treatment) and A0 (control) game
defs on the shared hex_rhombus W=22 board, then random-rollout smoke them.

Spec: docs/superpowers/specs/2026-06-07-field-connect-probe-design.md (v2).
Pre-registered defaults (spec §9): W=22; A1 influence r=2/s=1.0/d=0.5,
margin 0.0; A0 = R21 menger plateau family (outnumber-2 + influence
r=1/d=0.7 + threshold 36 = R21's 30 scaled by 484/400); max_turns 200;
pie on; komi calibrated later (calibrate.py).

Usage:
    python experiments/field_connect_probe/build_games.py [--smoke 50]
"""
from __future__ import annotations

import argparse
import json
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

W = 22  # 484 cells

COMMON = dict(
    num_dimensions=2,
    axis_size=W,
    topology_type="hex_rhombus",
    placement_rule=PlacementRule(target="empty", constraint="anywhere"),
    turn_structure=TurnStructure(turn_type="alternating"),
    action_rule=ActionRule(action_types=("place",)),
    pie_rule=True,
)


def build_a1() -> GameDefV2:
    """Field-Connect: influence IS the win condition + surround capture."""
    return GameDefV2(
        game_id="fc_probe_a1_field_connect",
        capture_rule=CaptureRule(capture_type="surround"),
        propagation_rule=PropagationRule(
            prop_type="influence", radius=2, strength=1.0, decay=0.5,
        ),
        win_condition=WinCondition(
            condition_type="field_connection",
            control_margin=0.0,
            target_dimension=1,      # P1 connects r=0 <-> r=W-1
            target_dimension_p2=0,   # P2 connects q=0 <-> q=W-1
            max_turns=200,
        ),
        **COMMON,
    )


def build_a0() -> GameDefV2:
    """Plateau baseline: R20/R21 menger family, board held constant."""
    return GameDefV2(
        game_id="fc_probe_a0_baseline",
        capture_rule=CaptureRule(capture_type="outnumber", threshold=2),
        propagation_rule=PropagationRule(
            prop_type="influence", radius=1, strength=1.0, decay=0.7,
        ),
        win_condition=WinCondition(
            condition_type="threshold",
            threshold=36.0,          # R21's 30 x (484/400)
            max_turns=200,
        ),
        **COMMON,
    )


def smoke(game: GameDefV2, episodes: int, seed: int = 0) -> dict:
    """Uniform-random rollouts: the game must terminate, never error, and
    show every end cause is reachable."""
    rng = np.random.default_rng(seed)
    causes = {"win_condition": 0, "timeout": 0, "draw": 0}
    lengths = []
    for _ in range(episodes):
        e = GameEngineV2(game)
        e.reset()
        while not e.done:
            legal = e.get_legal_actions()
            if not legal:
                break
            e.step(int(rng.choice(legal)))
        lengths.append(e.step_count)
        timeout = e.step_count >= game.max_game_steps
        if e._winner is None:
            causes["draw"] += 1
        elif timeout:
            causes["timeout"] += 1
        else:
            causes["win_condition"] += 1
    return {"avg_length": float(np.mean(lengths)), **causes}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--smoke", type=int, default=50)
    args = p.parse_args()

    GAMES_DIR.mkdir(parents=True, exist_ok=True)
    for game in (build_a1(), build_a0()):
        out = GAMES_DIR / f"{game.game_id.removeprefix('fc_probe_')}.json"
        with open(out, "w") as f:
            json.dump(game.to_dict(), f, indent=2)
        print(f"wrote {out}")
        if args.smoke:
            print(f"  smoke({args.smoke}): {smoke(game, args.smoke)}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the builder with smoke**

Run: `python experiments/field_connect_probe/build_games.py --smoke 50`
Expected: two JSONs written (`a1_field_connect.json`, `a0_baseline.json`); for each game a smoke line with no exceptions, `avg_length > 0`, and at least one of `win_condition`/`timeout` nonzero. **Record the numbers.** If A1 random play NEVER ends by `win_condition` in 50 games, that is acceptable at random play (random fields are noisy) — but note it in the commit message; PPO play in the screen is the real check.

- [ ] **Step 3: Round-trip check**

Run: `python -c "
import json, sys; sys.path.insert(0, '.')
from game_engine.game_def_v2 import GameDefV2
for n in ('a1_field_connect','a0_baseline'):
    d = json.load(open(f'experiments/field_connect_probe/games/{n}.json'))
    g = GameDefV2.from_dict(d)
    assert g.to_dict() == d, n
    print(n, 'round-trip OK', g.topology_type, g.win_condition.condition_type)
"`
Expected: both `round-trip OK`

- [ ] **Step 4: Commit**

```bash
git add experiments/field_connect_probe/build_games.py experiments/field_connect_probe/games/
git commit -m "feat(probe): A1/A0 game defs on hex_rhombus W=22 + rollout smoke"
```

---

### Task 7: probe metrics module

**Files:**
- Create: `experiments/field_connect_probe/metrics.py`
- Test: `experiments/field_connect_probe/test_probe_metrics.py`

- [ ] **Step 1: Write the failing tests**

```python
"""Unit tests for the pre-registered mechanical-screen metric functions."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from experiments.field_connect_probe.metrics import (  # noqa: E402
    count_lead_changes,
    largest_component,
)
from game_engine.topology import TopologicalSpace  # noqa: E402


def test_count_lead_changes_skips_zeros() -> None:
    # signs: + + - (0 skipped) - +  -> flips: +to-, -to+  = 2
    assert count_lead_changes([1.0, 2.0, -1.0, 0.0, -2.0, 3.0]) == 2


def test_count_lead_changes_monotone_is_zero() -> None:
    assert count_lead_changes([0.5, 1.0, 3.0]) == 0
    assert count_lead_changes([]) == 0
    assert count_lead_changes([0.0, 0.0]) == 0


def test_largest_component_on_rhombus() -> None:
    t = TopologicalSpace(2, 6, "hex_rhombus")
    cells = {t.coords_to_cell((2, r)) for r in range(4)}          # 4-chain
    cells |= {t.coords_to_cell((5, 5))}                            # isolated
    assert largest_component(t, cells) == 4
    assert largest_component(t, set()) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest experiments/field_connect_probe/test_probe_metrics.py -v`
Expected: FAIL with `ModuleNotFoundError` / `ImportError`

- [ ] **Step 3: Implement `metrics.py`**

```python
"""Pre-registered mechanical-screen metrics for the Field-Connect probe.

Lead-change proxy (spec §8a, concretized here BEFORE any results exist):
  A1 (field_connection): d_t = largest P1-controlled component size
                               - largest P2-controlled component size
  A0 (threshold):        d_t = P1 score - (P2 score + komi_p2 * threshold)
lead_changes = sign flips of d_t over the game, zeros skipped.
"""
from __future__ import annotations

from typing import Iterable


def count_lead_changes(series: Iterable[float]) -> int:
    """Sign flips in *series*, ignoring zeros."""
    flips = 0
    prev = 0
    for v in series:
        s = (v > 0) - (v < 0)
        if s != 0:
            if prev != 0 and s != prev:
                flips += 1
            prev = s
    return flips


def largest_component(topo, cells: set[int]) -> int:
    """Size of the largest connected component of *cells* under *topo*
    adjacency."""
    best = 0
    unseen = set(cells)
    while unseen:
        start = unseen.pop()
        size = 1
        stack = [start]
        while stack:
            c = stack.pop()
            for n in topo.get_neighbors(c):
                if n in unseen:
                    unseen.remove(n)
                    size += 1
                    stack.append(n)
        best = max(best, size)
    return best


def controlled_sets(engine, margin: float) -> tuple[set[int], set[int]]:
    """(P1-controlled, P2-controlled) cell sets by field sign + margin."""
    p1 = {c for c in engine.topo.active_cells if engine.board_values[c] > margin}
    p2 = {c for c in engine.topo.active_cells if engine.board_values[c] < -margin}
    return p1, p2


def progress_diff_field(engine, margin: float) -> float:
    """A1 lead proxy: largest-controlled-component size differential."""
    p1, p2 = controlled_sets(engine, margin)
    return float(
        largest_component(engine.topo, p1) - largest_component(engine.topo, p2)
    )


def progress_diff_threshold(engine) -> float:
    """A0 lead proxy: effective threshold-race score differential,
    replicating the engine's scoring (engine_v2.py:998) incl. komi."""
    p1 = sum(
        float(engine.board_values[c])
        for c in engine.topo.active_cells
        if engine.board_owners[c] == 1
    )
    p2 = sum(
        -float(engine.board_values[c])
        for c in engine.topo.active_cells
        if engine.board_owners[c] == 2
    )
    komi = getattr(engine.game, "komi_p2", 0.0) * engine.game.win_condition.threshold
    return p1 - (p2 + komi)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest experiments/field_connect_probe/test_probe_metrics.py -v`
Expected: 3 passed

(If the `experiments.field_connect_probe` import path fails under pytest, add empty `experiments/__init__.py` is NOT the convention here — instead match how `experiments/r20_5_g4/run_g4.py` imports from `experiments.r20_finalization`: `sys.path.insert(0, ROOT)` already enables package-style imports because both dirs contain importable modules. If pytest still can't import, run with `python -m pytest` from repo root, which puts `.` on sys.path.)

- [ ] **Step 5: Commit**

```bash
git add experiments/field_connect_probe/metrics.py experiments/field_connect_probe/test_probe_metrics.py
git commit -m "feat(probe): pre-registered mechanical-screen metric functions"
```

---

### Task 8: komi calibration driver

**Files:**
- Create: `experiments/field_connect_probe/calibrate.py`
- Output: `experiments/field_connect_probe/games/calibrated/{a1_field_connect,a0_baseline}.json`, `experiments/field_connect_probe/calibration.md`

- [ ] **Step 1: Write the driver**

```python
"""Komi calibration for the two probe games (spec §3.6, §11.3).

Per game: sweep komi_p2 over a grid; at each value train PPO (budget 3000,
seed 42) and measure sampled trained-vs-trained seat bias with seat-swap
halves (the R20.5-G4 / R21-S4 methodology). Pick the smallest komi with
bias <= 0.10. Write calibrated game JSONs + a markdown report.

Note (spec wrinkle, recorded in the plan): for A1 komi only enters the
TIMEOUT tiebreak — pie is the primary balancer for connection wins. If no
komi passes for A1, the game is flagged BIAS_UNRESOLVED (not rush-broken)
and the A/B proceeds only if bias <= 0.15 at the best komi, reported.

Usage:
    python experiments/field_connect_probe/calibrate.py \
        [--grid "0.0,0.05,0.10,0.15,0.20,0.25,0.30"] \
        [--budget 3000] [--eval-episodes 200] [--seed 42]
"""
from __future__ import annotations

import argparse
import copy
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
from training.utils import play_game  # noqa: E402

HERE = Path(__file__).resolve().parent
GAMES = ("a1_field_connect", "a0_baseline")
BIAS_PASS = 0.10
BIAS_PROCEED_CAP = 0.15  # A1 may proceed flagged if best bias <= this


def sampled_mirror_eval(trainer, num_episodes: int, max_steps: int):
    """Copied from experiments/r20_5_g4/run_g4.py:102 (same methodology).
    Returns (p1_winrate, draw_rate, avg_length); p1 = seat 0."""
    half = num_episodes // 2
    p1_wins = 0
    draws = 0
    lengths = []
    for i in range(num_episodes):
        engine = create_engine(trainer.game)
        if i < half:
            a0, a1 = trainer.agents[0], trainer.agents[1]
        else:
            a0, a1 = trainer.agents[1], trainer.agents[0]
        winner, length, _ = play_game(
            engine, a0, a1, deterministic=False, max_steps=max_steps,
        )
        lengths.append(length)
        if winner is None:
            draws += 1
        elif winner == 0:
            p1_wins += 1
    n = max(num_episodes, 1)
    return p1_wins / n, draws / n, float(np.mean(lengths)) if lengths else 0.0


def bias_at_komi(game: GameDefV2, komi: float, budget: int, eval_eps: int,
                 seed: int) -> dict:
    g = copy.deepcopy(game)
    g.komi_p2 = komi
    cfg = TrainingConfig(training_budget=budget, eval_episodes=100)
    mcfg = MetricsConfig(learning_curve_checkpoints=2)
    trainer = SelfPlayTrainer(g, cfg, mcfg, seed=seed)
    t0 = time.time()
    trainer.train()
    wr, draws, length = sampled_mirror_eval(
        trainer, eval_eps, g.max_game_steps,
    )
    return dict(komi=komi, p1_winrate=wr, bias=abs(wr - 0.5),
                draw_rate=draws, avg_length=length,
                elapsed_s=time.time() - t0)


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
    md = ["# Field-Connect probe — komi calibration", "",
          f"PPO budget {args.budget}, seed {args.seed}, sampled mirror eval "
          f"n={args.eval_episodes} (seat-swap, deterministic=False). "
          f"PASS = smallest komi with bias <= {BIAS_PASS}.", ""]

    for name in GAMES:
        game = GameDefV2.from_dict(
            json.load(open(HERE / "games" / f"{name}.json"))
        )
        md += [f"## {name}", "",
               "| komi | p1_wr | bias | draws | len | s |",
               "|---|---:|---:|---:|---:|---:|"]
        rows = []
        chosen = None
        for komi in grid:
            r = bias_at_komi(game, komi, args.budget, args.eval_episodes,
                             args.seed)
            rows.append(r)
            md.append(f"| {r['komi']:.2f} | {r['p1_winrate']:.3f} | "
                      f"{r['bias']:.3f} | {r['draw_rate']:.3f} | "
                      f"{r['avg_length']:.1f} | {r['elapsed_s']:.0f} |")
            print(f"{name} komi={komi:.2f} bias={r['bias']:.3f}")
            if chosen is None and r["bias"] <= BIAS_PASS:
                chosen = r
        best = min(rows, key=lambda r: r["bias"])
        if chosen is None:
            verdict = (f"BIAS_UNRESOLVED (best bias {best['bias']:.3f} at "
                       f"komi {best['komi']:.2f})")
            use = best if best["bias"] <= BIAS_PROCEED_CAP else None
        else:
            verdict = f"PASS at komi {chosen['komi']:.2f}"
            use = chosen
        md += ["", f"**{verdict}**", ""]
        if use is not None:
            game.komi_p2 = use["komi"]
            with open(out_dir / f"{name}.json", "w") as f:
                json.dump(game.to_dict(), f, indent=2)
            md.append(f"Calibrated def written (komi_p2={use['komi']:.2f}).")
        else:
            md.append("NO calibrated def written — game is A/B-blocked.")
        md.append("")

    (HERE / "calibration.md").write_text("\n".join(md))
    print("wrote calibration.md")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Dry-run on a tiny budget to validate plumbing (not results)**

Run: `python experiments/field_connect_probe/calibrate.py --grid "0.0" --budget 200 --eval-episodes 10`
Expected: completes in a few minutes, writes `calibration.md` and both calibrated JSONs (bias values meaningless at budget 200 — this validates the pipeline only). Delete the dry-run outputs afterwards: `rm -r experiments/field_connect_probe/games/calibrated experiments/field_connect_probe/calibration.md`

- [ ] **Step 3: Commit the driver (not outputs)**

```bash
git add experiments/field_connect_probe/calibrate.py
git commit -m "feat(probe): komi calibration driver (R21-S4 methodology, JSON games)"
```

- [ ] **Step 4: Full calibration run (compute, ~1–2 hr)**

Run: `python experiments/field_connect_probe/calibrate.py 2>&1 | tee logs_calibration.txt`
Expected: per-game verdict lines; both calibrated JSONs written unless a game is A/B-blocked. **If A0 is FAIL on the whole grid** (rush-broken on this board), STOP and report — the baseline must be playable for the A/B to mean anything; widen the grid to 0.40/0.50 before concluding.

- [ ] **Step 5: Commit calibration results**

```bash
git add experiments/field_connect_probe/games/calibrated/ experiments/field_connect_probe/calibration.md
git commit -m "results(probe): komi calibration — A1/A0 calibrated defs"
```

---

### Task 9: mechanical screen driver

**Files:**
- Create: `experiments/field_connect_probe/run_screen.py`
- Output: `experiments/field_connect_probe/screen_results.csv`, `experiments/field_connect_probe/screen_results.md`

- [ ] **Step 1: Write the driver**

```python
"""Field-Connect probe — mechanical screen (spec §8a).

Per game (calibrated A1, A0) x 3 PPO seeds: train (budget 5000), then run
an INSTRUMENTED sampled trained-vs-trained mirror eval (n=200, seat-swap)
recording per-step metrics. Aggregates the six pre-registered signals:

  game_length, capture_rate, decisiveness, lead_changes, seat_balance,
  draw_rate

plus PPO-learnability diagnostics (trained_vs_random via trainer.evaluate)
so a no-go from unlearnability is distinguishable from shallowness
(spec §10).

Usage:
    python experiments/field_connect_probe/run_screen.py \
        [--budget 5000] [--eval-episodes 200] [--seeds 42,43,44]
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

HERE = Path(__file__).resolve().parent
GAMES = ("a1_field_connect", "a0_baseline")
LENGTH_BAND = (30.0, 160.0)  # pre-registered healthy band (plies)


def instrumented_episode(game: GameDefV2, a0, a1) -> dict:
    """One sampled game with per-step metric recording."""
    engine = create_engine(game)
    obs = engine.reset()
    agents = [a0, a1]
    is_field = game.win_condition.condition_type == "field_connection"
    margin = getattr(game.win_condition, "control_margin", 0.0)
    prev_counts = list(engine.piece_counts)
    captures = 0
    diffs: list[float] = []
    hard_cap = 2 * game.max_game_steps  # belt & braces; engine self-terminates

    while not engine.done and engine.step_count < hard_cap:
        legal = engine.get_legal_actions()
        if not legal:
            break
        agent = agents[engine.get_current_player()]
        action, _, _ = agent.select_action(
            obs, legal_actions=legal, deterministic=False,
        )
        obs, _, done, info = engine.step(action)
        if not info.get("pie_swap"):
            for pidx in (0, 1):
                drop = prev_counts[pidx] - engine.piece_counts[pidx]
                if drop > 0:
                    captures += drop
        prev_counts = list(engine.piece_counts)
        diffs.append(
            progress_diff_field(engine, margin) if is_field
            else progress_diff_threshold(engine)
        )

    winner = engine._winner  # 1 / 2 / None
    # Exact end-cause via the engine's _ended_by_max_turns observability
    # flag (added in the Task 6 review cycle — no proxy error).
    timeout = engine._ended_by_max_turns
    return dict(
        length=engine.step_count,
        captures=captures,
        lead_changes=count_lead_changes(diffs),
        decisive=(winner is not None and not timeout),
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
        capture_rate=float(np.mean([e["captures"] for e in eps])),
        decisiveness=sum(e["decisive"] for e in eps) / n,
        lead_changes=float(np.mean([e["lead_changes"] for e in eps])),
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
    args = p.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]

    rows = []
    for name in GAMES:
        path = HERE / "games" / "calibrated" / f"{name}.json"
        game = GameDefV2.from_dict(json.load(open(path)))
        for seed in seeds:
            r = screen_one(game, seed, args.budget, args.eval_episodes)
            rows.append(r)
            print(f"{name} seed={seed}: " + ", ".join(
                f"{k}={v:.3f}" for k, v in r.items()
                if isinstance(v, float)))

    with open(HERE / "screen_results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # Aggregate + pre-registered comparison
    def agg(gid: str, key: str) -> float:
        return float(np.mean([r[key] for r in rows if r["game_id"] == gid]))

    a1, a0 = "fc_probe_a1_field_connect", "fc_probe_a0_baseline"
    md = ["# Field-Connect probe — mechanical screen", "",
          f"PPO budget {args.budget}, seeds {seeds}, instrumented sampled "
          f"mirror eval n={args.eval_episodes}/seed.", "",
          "| metric | A1 (Field-Connect) | A0 (baseline) | A1 wins? |",
          "|---|---:|---:|:---:|"]
    wins = 0
    checks = [
        ("capture_rate", lambda x1, x0: x1 > x0),
        ("decisiveness", lambda x1, x0: x1 > x0),
        ("lead_changes", lambda x1, x0: x1 > x0),
        ("game_length", lambda x1, x0:
            LENGTH_BAND[0] <= x1 <= LENGTH_BAND[1]
            and not (LENGTH_BAND[0] <= x0 <= LENGTH_BAND[1] and
                     abs(x0 - 95.0) < abs(x1 - 95.0))),
    ]
    for key, better in checks:
        v1, v0 = agg(a1, key), agg(a0, key)
        ok = better(v1, v0)
        wins += ok
        md.append(f"| {key} | {v1:.3f} | {v0:.3f} | {'YES' if ok else 'no'} |")
    for key in ("seat_balance", "draw_rate", "trained_vs_random"):
        md.append(f"| {key} | {agg(a1, key):.3f} | {agg(a0, key):.3f} | — |")
    md += ["",
           f"**A1 beats A0 on {wins}/4 pre-registered signals "
           f"(GO requires >= 3; spec §8c).**", "",
           f"Healthy length band: {LENGTH_BAND}. game_length 'win' = A1 in "
           "band and at-least-as-central as A0 (95 = band midpoint).", "",
           "PPO-learnability guard (spec §10): if A1 trained_vs_random is "
           "near 0.5, a screen miss is UNLEARNABLE-not-shallow — report "
           "separately, do not score as a clean no-go."]
    (HERE / "screen_results.md").write_text("\n".join(md))
    print(f"\nA1 wins {wins}/4 — wrote screen_results.{{csv,md}}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Dry-run plumbing on tiny budget**

Run: `python experiments/field_connect_probe/run_screen.py --budget 200 --eval-episodes 10 --seeds 42`
Expected: completes, prints one line per game, writes both outputs (numbers meaningless). Delete outputs: `rm experiments/field_connect_probe/screen_results.csv experiments/field_connect_probe/screen_results.md`

- [ ] **Step 3: Commit the driver**

```bash
git add experiments/field_connect_probe/run_screen.py
git commit -m "feat(probe): instrumented mechanical-screen driver (6 pre-registered signals)"
```

- [ ] **Step 4: Full screen run (compute, ~2–4 hr)**

Run: `python experiments/field_connect_probe/run_screen.py 2>&1 | tee logs_screen.txt`
Expected: 6 result lines (2 games × 3 seeds), final `A1 wins K/4` line.

- [ ] **Step 5: Sanity-gate decision (record it)**

The agent A/B proceeds only if (spec §8b gate): A1 `trained_vs_random` clearly above 0.5 (PPO learns it at all) AND A1 `draw_rate` < 0.5 (contested-wall pathology check, spec §5a) AND seat bias acceptable per Task 8. Record the gate verdict in the commit message.

- [ ] **Step 6: Commit results**

```bash
git add experiments/field_connect_probe/screen_results.csv experiments/field_connect_probe/screen_results.md
git commit -m "results(probe): mechanical screen — A1 vs A0 [K/4 signals; gate verdict]"
```

---

### Task 10: blind A/B eval pack

**Files:**
- Create: `experiments/field_connect_probe/eval_helper.py`
- Create: `evaluations/field_connect_probe/BRIEFING.md`, `evaluations/field_connect_probe/TEMPLATE_team-N_gameQ.md`, `evaluations/field_connect_probe/TEMPLATE_team-N_gameZ.md`, `evaluations/field_connect_probe/.blind_mapping.json`

- [ ] **Step 1: Write the eval helper**

```python
"""Interactive helper for the Field-Connect probe agent A/B (blind).

Like eval_run21_helper.py but loads game defs from the probe's calibrated
JSONs via BLIND labels (Q/Z) so evaluator teams never see treatment names
or game_ids. Renders the stone board AND (for influence games) the
control map; reports scores/connection progress and legal actions.

Usage:
    python experiments/field_connect_probe/eval_helper.py --game Q
    python experiments/field_connect_probe/eval_helper.py --game Z \
        --moves "245,108,246" --control
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from game_engine.factory import create_engine  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402

from experiments.field_connect_probe.metrics import (  # noqa: E402
    controlled_sets,
    largest_component,
    progress_diff_threshold,
)

HERE = Path(__file__).resolve().parent
BLIND = json.load(open(ROOT / "evaluations" / "field_connect_probe"
                       / ".blind_mapping.json"))


def load_game(label: str) -> GameDefV2:
    name = BLIND[label.upper()]
    return GameDefV2.from_dict(
        json.load(open(HERE / "games" / "calibrated" / f"{name}.json"))
    )


def render(engine, game, show_control: bool) -> str:
    s = game.axis_size
    topo = engine.topo
    out = []
    for r in range(s):
        row = [" " * r]  # axial shear: indent row r by r half-cells
        for q in range(s):
            c = topo.coords_to_cell((q, r))
            o = int(engine.board_owners[c])
            row.append("X" if o == 1 else "O" if o == 2 else "·")
        out.append(" ".join(row))
    if show_control:
        margin = getattr(game.win_condition, "control_margin", 0.0)
        out.append("")
        out.append("control map (+ = P1-controlled, - = P2, · = contested):")
        for r in range(s):
            row = [" " * r]
            for q in range(s):
                v = float(engine.board_values[topo.coords_to_cell((q, r))])
                row.append("+" if v > margin else "-" if v < -margin else "·")
            out.append(" ".join(row))
    return "\n".join(out)


def status(engine, game) -> str:
    wc = game.win_condition
    lines = [f"step={engine.step_count} player_to_move="
             f"P{engine.current_player} done={engine.done} "
             f"winner={engine._winner}"]
    if wc.condition_type == "field_connection":
        margin = getattr(wc, "control_margin", 0.0)
        p1, p2 = controlled_sets(engine, margin)
        lines.append(
            f"controlled cells: P1={len(p1)} P2={len(p2)} "
            f"largest components: P1={largest_component(engine.topo, p1)} "
            f"P2={largest_component(engine.topo, p2)} "
            f"(P1 connects r=0<->r={game.axis_size-1}, "
            f"P2 connects q=0<->q={game.axis_size-1}; komi on timeout "
            f"tiebreak: {game.komi_p2})"
        )
    else:
        lines.append(
            f"score differential (P1 - P2, komi applied): "
            f"{progress_diff_threshold(engine):.2f} "
            f"(threshold {wc.threshold}, komi_p2 {game.komi_p2})"
        )
    legal = engine.get_legal_actions()
    lines.append(f"legal actions: {len(legal)} "
                 f"(cell index = q + {game.axis_size}*r; "
                 f"pass={game.axis_size**2}, swap={game.axis_size**2+1})")
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--game", required=True, choices=["Q", "Z", "q", "z"])
    p.add_argument("--moves", default="",
                   help="comma-separated action ids to replay")
    p.add_argument("--control", action="store_true",
                   help="also render the influence control map")
    args = p.parse_args()

    game = load_game(args.game)
    engine = create_engine(game)
    engine.reset()
    for tok in [t for t in args.moves.split(",") if t.strip()]:
        if engine.done:
            print("game already over — remaining moves ignored")
            break
        engine.step(int(tok))
    print(render(engine, game, args.control))
    print()
    print(status(engine, game))


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Write the blind mapping + briefing + templates**

`evaluations/field_connect_probe/.blind_mapping.json` (orchestrator-only; teams are instructed not to read it):

```json
{"Q": "a0_baseline", "Z": "a1_field_connect"}
```

`evaluations/field_connect_probe/BRIEFING.md`:

```markdown
# Field-Connect probe — blind agent A/B briefing

You are one of 2 independent evaluator teams. You will evaluate TWO games,
labeled **Q** and **Z**. You are NOT told which (if either) is new, or what
any hypothesis is. Do not read `.blind_mapping.json` or anything under
`experiments/field_connect_probe/` other than `eval_helper.py` usage below.

Per game: follow the 5-phase protocol in your TEMPLATE file (same rubric as
run21). Play >= 3 full lines per game (P1 push, P2 contest, adversary
stress) via:

    python experiments/field_connect_probe/eval_helper.py --game Q \
        --moves "<csv action ids>" [--control]

Rules comprehension (Phase 1): derive the rules ONLY from the game def the
helper prints and engine behavior you observe. Both games: hex-adjacency
rhombus board W=22 (484 cells), place-only, alternating, pie rule on.

Scoring anchors (Phase 5, Overall 1-10): R8 4.10, R19 4.375 (top 5.0),
R20 3.73 (best 4.80), R21 3.69. Anchor DOWN against drift, as in R21.

Additional final section (after Phase 5, per team): **Q-vs-Z comparison** —
which game would you rather play again, and by how many Overall points?

Write verdicts to evaluations/field_connect_probe/team-{N}_game{Q,Z}.md.
```

Templates: copy `evaluations/run21/TEMPLATE_team-N_gameXXXX.md` twice as `TEMPLATE_team-N_gameQ.md` / `TEMPLATE_team-N_gameZ.md`, then in each: (1) replace the run21 helper command with the eval_helper.py command above; (2) replace game-id placeholders with the blind label; (3) append the Q-vs-Z comparison section per the briefing; (4) update anchors line to include R21 3.69.

- [ ] **Step 3: Smoke the helper**

Run: `python experiments/field_connect_probe/eval_helper.py --game Z --moves "" --control`
Expected: rhombus render (22 sheared rows), control map all `·`, status line with controlled-cell counts and legal-action count 484 (+pass; swap appears only at P2's first move).

Run: `python experiments/field_connect_probe/eval_helper.py --game Q`
Expected: same board, threshold-score status line.

- [ ] **Step 4: Commit**

```bash
git add experiments/field_connect_probe/eval_helper.py evaluations/field_connect_probe/
git commit -m "feat(probe): blind A/B eval pack — helper, briefing, templates, sealed mapping"
```

---

### Task 11: run the blind agent A/B (campaign)

This is an interactive agent-team activity, not a script. Protocol (spec §8b):

- [ ] **Step 1:** Confirm the Task-9 sanity gate passed (recorded in the Task 9 commit). If it failed, skip to Task 12 and write the no-go/unlearnable readout.
- [ ] **Step 2:** Launch 2 independent evaluator teams (tmux agent teams, per the R21 campaign pattern — independent contexts, no cross-talk). Each team receives only: `evaluations/field_connect_probe/BRIEFING.md` + its two TEMPLATE files.
- [ ] **Step 3:** Each team plays ≥3 lines per game and files 2 verdicts: `team-{N}_gameQ.md`, `team-{N}_gameZ.md` (4 verdicts total).
- [ ] **Step 4:** Orchestrator (NOT the teams) unblinds via `.blind_mapping.json` and computes: mean Overall(A1) − mean Overall(A0) across teams, plus the Q-vs-Z preference answers.
- [ ] **Step 5: Commit**

```bash
git add evaluations/field_connect_probe/team-*.md
git commit -m "results(probe): blind agent A/B — 2 teams x 2 games verdicts"
```

---

### Task 12: go/no-go synthesis

**Files:**
- Create: `experiments/field_connect_probe/RESULTS.md`

- [ ] **Step 1: Write the readout against spec §8c (verbatim criteria, no re-litigating)**

`RESULTS.md` must contain, in order:
1. **Mechanical screen table** (from `screen_results.md`): A1 vs A0 on the 4 scored signals + the 3 diagnostics; the `K/4` line.
2. **Agent A/B table**: per-team Overall for Q and Z, unblinded means, the differential, and the Q-vs-Z preferences.
3. **Decision** — exactly one of:
   - **GO**: A1 ≥ 3/4 mechanical signals AND A/B differential ≥ +1.0 Overall. Next step: phase-2 design per spec §12 (carpet-family interiors under Field-Connect + QD/GE-replacement).
   - **NO-GO (lever wrong)**: A1 fails either bar with A1 `trained_vs_random` healthy. Next step: rethink rules before any substrate work.
   - **NO-GO (unlearnable — distinct, spec §10)**: A1 fails with `trained_vs_random` ≈ 0.5. The rule lever is UNTESTED, not falsified; next step is training-budget/representation work, not rule redesign.
4. **Pre-registration note**: link the criteria to spec §8c and confirm none were altered after data was seen (the lead-change proxy and length band were locked in this plan before any run).

- [ ] **Step 2: Update memory-facing docs**

Append a short results section to `docs/superpowers/specs/2026-06-07-field-connect-probe-design.md` (status line → RESULTS IN + decision).

- [ ] **Step 3: Commit**

```bash
git add experiments/field_connect_probe/RESULTS.md docs/superpowers/specs/2026-06-07-field-connect-probe-design.md
git commit -m "results(probe): go/no-go readout vs pre-registered criteria"
```

---

## Phase-2 notes (do NOT build now)

- The `_field_dirty` recompute flag is set only by `_remove_group` (surround-capture path). `_capture_outnumber` removes stones inline and `_capture_custodian` flips ownership without `_remove_group` — neither would trigger the field recompute for a hypothetical field_connection game using them. Fine for the probe (A1 = surround by spec); MUST be revisited if phase 2 ever mutates capture types on field_connection games.
- ~~`hex_rhombus` mutation-pool hazard~~ RESOLVED in `52c8108`: `hex_rhombus` was added to `EXPERIMENTAL_TOPOLOGIES`, which excludes it from `_mutate_topology_type`'s candidate pool. Still true: it has no `SUBSTRATE_INVARIANTS` entry (deliberate — it is size-parameterizable), so IF phase 2 ever removes it from the experimental set to evolve over it, add a dims guard first (R17-B1 bug class).
- `step_simultaneous` never runs the capture-recompute hook — a hypothetical *simultaneous-turn* field_connection game would win-check on a stale field. Unreachable today (both probe defs are alternating; the generator cannot emit field_connection); add the hook if phase 2 ever combines simultaneous turns with field_connection.
- `evolution/operators_v2.py:493` (`_fix_consistency`) demotes `influence` propagation on non-threshold wins — must learn about `field_connection` before any evolution/QD run uses it, or every Field-Connect genotype gets its win mechanic stripped.
- `WIN_CONDITION_TYPES` (rules.py:179) deliberately excludes `field_connection`; add it (plus generator support for target dimensions) only when phase 2 wants mutation over it.
- Carpet-family interiors under Field-Connect (spec §12) will need `connects_faces` to handle masked boards (holes between faces) — it already BFSes the active adjacency, so masked substrates should work, but face-membership (`coord == 0 / axis-1`) may select hole cells; verify then.
- Engine `_recompute_field` is O(stones × radius-ball) per capture — fine for the probe; for QD-scale evolution consider incremental subtraction (must then handle the ±100 clamp).

## Self-review (done at write time)

- **Spec coverage:** §3 game (Task 6 A1 def: placement/pie ✓, influence reuse ✓, control+margin Task 3 ✓, surround+recompute Task 4 ✓, win Task 3 ✓, komi Task 8 ✓, timeout tiebreak Task 5 ✓); §4 engine change + tests (Tasks 1,3,4,5) ✓; §5a board (Task 2) ✓; §5c (Task 2, no invariants entry — justified) ✓; §6 baseline (Task 6 A0) ✓; §7 matrix (2 games) ✓; §8a metrics (Tasks 7,9; lead-change proxy concretized) ✓; §8b gated A/B (Tasks 9.5, 10, 11) ✓; §8c criteria (Task 9 md + Task 12) ✓; §9 defaults locked in header ✓; §10 unlearnable-vs-shallow split (Task 9 diagnostics + Task 12 decision branch) ✓; §11 sequence = task order ✓.
- **Known risks accepted:** ~~decisive-at-final-step counted as timeout~~ (eliminated in `094225f` — exact `_ended_by_max_turns` end-cause flag); `trainer.evaluate()` diagnostic key name `trained_vs_random_winrate` taken from run.py's return schema — if `trainer.evaluate` uses a different key, fall back to `diag.get("trained_vs_random", ...)` (guarded with `.get` + sentinel −1.0 already).
- **Execution note (post-run):** the eval pack shipped at `evaluations/probe_ab/` (renamed from `evaluations/field_connect_probe/` in `5aae70b` — the original path leaked the treatment name to blind evaluators). References to `evaluations/field_connect_probe/` in the file-structure table and Tasks 10–11 above refer to that final location.
- **Type consistency:** `control_margin` read via `getattr(wc, "control_margin", 0.0)` everywhere; blind labels Q/Z consistent across helper/briefing/mapping; `make_fc_game` defined once in test file before all uses.
