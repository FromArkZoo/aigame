# Frontline Rebuild Build Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the FRONTLINE campaign — the `contested_majority` game family plus its full experiment harness (Stage 0a memo → Stage 0b smoke → calibration → screen → Stage 1.5 diagnostic → blind pack) — exactly as locked in `experiments/frontline/PREREGISTRATION.md`.

**Architecture:** Gated, additive engine changes keyed off `WinCondition.condition_type == "contested_majority"` (new fields default legacy-inert, serde omits defaults, canonical hashes unchanged), then a harness under `experiments/frontline/` mirroring `experiments/siege/` anatomy file-for-file. All engine work lands before any harness work; the full 242+-test suite must stay green after every task.

**Tech Stack:** Python 3 (`.venv/bin/python`), numpy, PyTorch (existing `SelfPlayTrainer`), pytest. No new dependencies.

**Spec of record:** `docs/superpowers/specs/2026-06-11-frontline-rebuild-design.md` (§3 rules, §4 arithmetic, §5 build list, §8 locked constants). Prereg: `experiments/frontline/PREREGISTRATION.md` — locked at commit `3a378dd`; nothing in it may be altered by this build. Where this plan and the prereg disagree, the prereg wins.

---

## Pre-verified engine facts (verified on disk 2026-06-11 — re-verify line numbers before editing, code may have drifted)

- Win dispatch: `game_engine/engine_v2.py:1220` `_check_win_conditions()`, string-branches on `wc.condition_type`; `field_connection` branch at 1248-1257. The check runs at `engine_v2.py:367-369`, BEFORE `step_count += 1` (line 383) — so at the check site `step_count` is pre-increment: P1's plies check at even values, P2's at odd (alternating). Pie-swap plies (291-308) skip the win check entirely and preserve parity.
- Field recompute gating: `engine_v2.py:360-365` — recomputes when `capture_rule.capture_type in FIELD_CAPTURE_TYPES`; `field_flip` qualifies, so contested_majority games already get a fresh field every ply. Scoring reads `board_owners` directly (per-player recompute), so ghost-influence can never contaminate scores.
- Flip capture: `_capture_field_flip` at `engine_v2.py:919-965` (cascading; recomputes from owners first). Control: `_control_mask` at 911-917, strict `>` at `wc.control_margin`.
- Kernel cache: module-level `_influence_kernels(topo, radius, strength, decay)` at `engine_v2.py:45-78`, returns per-cell `(idx, w)` numpy pairs. Reuse it for per-player fields.
- Ends: `_end_by_double_pass` at 1474-1485 (hard draw — our gated override goes here); `_end_by_max_turns` at 1428-1472 (`timeout_winner` first, then `field_connection` count branch — our branch slots between them); `_ended_by_max_turns` flag set at 1434. `_handle_pass` at 690-697 (calls `_end_by_double_pass` on the 2nd consecutive pass, pre-increment step_count).
- Engine state init: `__init__` block at ~160-200 (the `_quota_ticks` SIEGE block at 173-177 is the pattern); `reset()` re-inits the same state (block "Reset SIEGE quota accounting"). New state must be added in BOTH places.
- Superko rollback: `_save_state()`/`_restore_state()` near `engine_v2.py:1499`; a rolled-back placement becomes a pass (347-354), so any counter incremented inside `_handle_placement` must be saved/restored.
- Pie swap: `_handle_pie_swap` at 703+ swaps piece_counts and negates the field; placement counters must swap with it.
- Observation: `_observe` at 1533-1570; metadata list gets gated appends (quota_frac pattern at 1561-1565), then `np.concatenate`. `state_dim` at `game_engine/game_def_v2.py:92-106` (capture_quota `extra` pattern).
- Serde: `WinCondition` at `game_engine/rules.py:210-247`; `to_dict` omit-if-default at 257-273; `from_dict` at 275-287. `WIN_CONDITION_TYPES` near rules.py:207 — `contested_majority` must NOT be added (never generated; SIEGE `capture_quota` precedent in the 240-244 comment).
- Trainer: `SelfPlayTrainer(game, TrainingConfig, MetricsConfig, seed=...)` then `.train()` — exact usage at `experiments/siege/calibrate.py:100-104`. Seat-swap eval: `sampled_mirror_eval(trainer, num_episodes, max_steps)` → `(p1_winrate, draw_rate, avg_length)` and `play_game(engine, a0, a1, deterministic=False, max_steps=...)` → `(winner_0indexed_or_None, length, _)`, both in `experiments/field_connect_probe/calibrate.py`.
- Harness anatomy to mirror: `experiments/siege/{build_games.py, scripted_agents.py, stage0_memo.py, calibrate.py, metrics.py, run_screen.py}`; tests at repo root (`test_siege_engine.py` style); comparator sources `experiments/fc_phase15/games/calibrated/{a0_baseline,a1_field_connect}.json` and `experiments/siege/games/calibrated/s_flip_r2.json` (calibrated, komi 0, exists — verify before Task 9).
- Run everything with `.venv/bin/python`; suite: `.venv/bin/python -m pytest test_*.py -q` from repo root (242 tests green at `3a378dd`).

## Locked constants (from spec §8 / prereg — NOT adjustable; the prereg is committed)

| Constant | Value |
|---|---|
| Substrate | hex_rhombus W=22, influence r=2/s=1.0/d=0.5/eps=0, field_flip, control_margin 0.0, pie ON |
| E grid × M_end grid | {0.75, 1.00, 1.25} × {8, 12} |
| Persistence | same leader ≥ M_end (komi-adj) at 3 consecutive ply-checks ending at a round-end (odd pre-increment step_count); leader-signed counter |
| min_turns_score_end / max_turns | 20 / 200 |
| Komi ladder | 0 first; then ±1, ±2 cells, smallest \|komi\|, direction by measured bias sign |
| Resolution order | score+komi → participation clause → stones tiebreak → draw |
| Lead tolerance | `CM_LEAD_TOL = 1e-9` |
| tvr gates | mean ≥ 0.75, no seed < 0.65, collapse < 0.20 → reserve 45 then 46, replace-in-slot |
| Stage-1 gates | bias ≤ 0.10; timeout ≤ 0.25; draw ≤ 0.05; score_margin share ≥ 0.25; engaged_share ∈ [0.02, 0.60]; double-pass share yellow > 0.50 |
| Stage-2 comparatives | flips F−S ≥ +0.5; length ≥ 10 more central (band [30,160], center 95); GO = 2/2 |
| Exploiter bands | trained F beats PassBot ≥ 0.90, beats Mirror ≥ 0.70 (each seat) |
| A1/A0 reproduction | a1 − a0 control_flip_rate ≥ 3.0 |
| Smoke pins | E=1.00, M_end=8, komi 0, seed 7; packer cross-distance ≥ 5; KILL-0b3 at min(turn 80, final ply) over ALL games, band (0.01, 0.60) |
| KILL-0a1 / KILL-0a2 | mean margin swing < −2 over pinned front set / analytic engaged@20% fill, E=1.0 > 0.60 |
| Blind labels | G / J / P |

---

### Task 1: WinCondition fields + serde (legacy-inert)

**Files:**
- Modify: `game_engine/rules.py:210-287` (WinCondition dataclass, to_dict, from_dict)
- Test: `test_frontline_engine.py` (new, repo root)

- [ ] **Step 1: Write the failing tests**

Create `test_frontline_engine.py`:

```python
"""FRONTLINE engine tests (contested_majority — spec §3/§5, prereg-locked).

Run: .venv/bin/python -m pytest test_frontline_engine.py -q
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from game_engine.factory import create_engine
from game_engine.game_def_v2 import GameDefV2
from game_engine.rules import (
    ActionRule, CaptureRule, PlacementRule, PropagationRule,
    TurnStructure, WinCondition, WIN_CONDITION_TYPES,
)

W = 22


def make_cm_game(
    engage_threshold: float = 1.0,
    end_margin: int = 8,
    min_turns: int = 20,
    komi_cells: int = 0,
    max_turns: int = 200,
    pie: bool = False,
) -> GameDefV2:
    """Frontline test fixture — prereg arm config, pie OFF by default so
    tests drive deterministic sequences (pie covered by its own test)."""
    return GameDefV2(
        game_id="f_test",
        num_dimensions=2,
        axis_size=W,
        topology_type="hex_rhombus",
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="field_flip"),
        propagation_rule=PropagationRule(
            prop_type="influence", radius=2, strength=1.0, decay=0.5),
        win_condition=WinCondition(
            condition_type="contested_majority",
            engage_threshold=engage_threshold,
            end_margin=end_margin,
            min_turns_score_end=min_turns,
            komi_cells=komi_cells,
            max_turns=max_turns,
            control_margin=0.0,
        ),
        pie_rule=pie,
    )


def test_wincondition_serde_roundtrip():
    wc = WinCondition(
        condition_type="contested_majority", engage_threshold=1.0,
        end_margin=8, min_turns_score_end=20, komi_cells=1, max_turns=200,
    )
    d = wc.to_dict()
    wc2 = WinCondition.from_dict(d)
    assert wc2.engage_threshold == 1.0
    assert wc2.end_margin == 8
    assert wc2.min_turns_score_end == 20
    assert wc2.komi_cells == 1


def test_legacy_serde_omits_frontline_keys():
    legacy = WinCondition(condition_type="connection")
    d = legacy.to_dict()
    for key in ("engage_threshold", "end_margin",
                "min_turns_score_end", "komi_cells"):
        assert key not in d, f"legacy to_dict leaked {key}"
    # back-compat: from_dict on a dict without the new keys
    wc = WinCondition.from_dict({"condition_type": "connection"})
    assert wc.engage_threshold == 0.0 and wc.komi_cells == 0


def test_contested_majority_not_generated():
    assert "contested_majority" not in WIN_CONDITION_TYPES


def test_legacy_canonical_hash_unchanged():
    src = Path("experiments/fc_phase15/games/calibrated/a1_field_connect.json")
    g = GameDefV2.from_dict(json.loads(src.read_text()))
    g2 = GameDefV2.from_dict(json.loads(json.dumps(g.to_dict())))
    assert g2.canonical_hash() == g.canonical_hash()
```

- [ ] **Step 2: Run tests to verify the right ones fail**

Run: `.venv/bin/python -m pytest test_frontline_engine.py -q`
Expected: `test_wincondition_serde_roundtrip` FAILS (`TypeError: unexpected keyword argument 'engage_threshold'`); the other three PASS (they only touch legacy behavior).

- [ ] **Step 3: Add the fields to WinCondition (rules.py, after `timeout_winner`)**

```python
    # FRONTLINE (contested_majority): a cell is engaged iff
    # min(I1, I2) >= engage_threshold; score = engaged cells led.
    # 0.0 = legacy-inert. NOT in WIN_CONDITION_TYPES (never generated) —
    # same precedent as capture_quota above.
    engage_threshold: float = 0.0
    # FRONTLINE: early-end margin in cells (0 = legacy-inert).
    end_margin: int = 0
    # FRONTLINE: no score-margin end or decisive double-pass before this ply.
    min_turns_score_end: int = 0
    # FRONTLINE: integer komi added to P2's score at every comparison.
    komi_cells: int = 0
```

In `to_dict()`, after the `timeout_winner` omission block:

```python
        if self.engage_threshold != 0.0:
            d["engage_threshold"] = self.engage_threshold
        if self.end_margin:
            d["end_margin"] = self.end_margin
        if self.min_turns_score_end:
            d["min_turns_score_end"] = self.min_turns_score_end
        if self.komi_cells:
            d["komi_cells"] = self.komi_cells
```

In `from_dict()`, after `timeout_winner=`:

```python
            engage_threshold=float(d.get("engage_threshold", 0.0)),
            end_margin=int(d.get("end_margin", 0)),
            min_turns_score_end=int(d.get("min_turns_score_end", 0)),
            komi_cells=int(d.get("komi_cells", 0)),
```

- [ ] **Step 4: Run tests + full suite**

Run: `.venv/bin/python -m pytest test_frontline_engine.py -q` → 4 passed.
Run: `.venv/bin/python -m pytest test_*.py -q` → all green (242+).

- [ ] **Step 5: Commit**

```bash
git add game_engine/rules.py test_frontline_engine.py
git commit -m "feat(frontline): WinCondition contested_majority fields, serde omit-defaults (legacy-inert)"
```

### Task 2: Per-player fields + contested_scores()

**Files:**
- Modify: `game_engine/engine_v2.py` (new module constant + two methods + state init)
- Test: `test_frontline_engine.py`

- [ ] **Step 1: Write the failing tests** (append to `test_frontline_engine.py`)

The straggler geometry is the spec §4.2 exact case: lone P2 stone, P1 at d1+d1+d2 → I1=1.25, I2=1.0 → exactly 1 engaged cell at E=1.0, P1-led.

```python
def _interior_cell(topo):
    """First cell with full 6/12 rings (mirrors siege stage0_memo)."""
    for cell in topo.active_cells:
        d1 = [c for c in topo.cells_within_radius(cell, 1) if c != cell]
        d2 = [c for c in topo.cells_within_radius(cell, 2)
              if topo.distance(cell, c) == 2]
        if len(d1) == 6 and len(d2) == 12:
            return cell, d1, d2
    raise RuntimeError("no interior cell")


def _set_board(engine, stones: dict[int, int]):
    engine.board_owners[:] = 0
    for c, owner in stones.items():
        engine.board_owners[c] = owner
    engine._recompute_field()


def test_contested_scores_straggler():
    engine = create_engine(make_cm_game())
    x, d1, d2 = _interior_cell(engine.topo)
    _set_board(engine, {x: 2, d1[0]: 1, d1[1]: 1, d2[0]: 1})
    s1, s2, engaged = engine.contested_scores()
    assert (s1, s2, engaged) == (1, 0, 1)   # spec §4.2 exact


def test_contested_scores_packing_zero():
    engine = create_engine(make_cm_game())
    x, _, _ = _interior_cell(engine.topo)
    far = x + 8  # same row, distance 8 > 2*r: kernels cannot overlap
    _set_board(engine, {x: 1, far: 2})
    assert engine.contested_scores() == (0, 0, 0)


def test_contested_scores_tie_cell_scores_no_one():
    engine = create_engine(make_cm_game())
    x, d1, _ = _interior_cell(engine.topo)
    # Empty cell x with one P1 and one P2 stone adjacent on opposite
    # sides: I1(x)=I2(x)=0.5 < E → not engaged at E=1.0. At E=0.5:
    # engaged, exact tie → neither scores.
    engine_lo = create_engine(make_cm_game(engage_threshold=0.5))
    _set_board(engine_lo, {d1[0]: 1, d1[3]: 2})
    s1, s2, engaged = engine_lo.contested_scores()
    assert s1 == s2  # symmetric config: tied cells score no one
    assert engaged >= 1
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest test_frontline_engine.py -q`
Expected: 3 new tests FAIL with `AttributeError: ... 'contested_scores'`.

- [ ] **Step 3: Implement.** Module constant next to `QUOTA_TICK_CAP_PER_MOVE` (engine_v2.py:~42):

```python
# FRONTLINE lead tolerance (prereg-locked). Kernel weights are dyadic
# (1.0/0.5/0.25) so field sums are float-exact; this only adjudicates
# genuinely tied cells (R17 ULP lesson kept for form).
CM_LEAD_TOL = 1e-9
```

Two methods, placed directly after `_recompute_field` (engine_v2.py:~1052):

```python
    def _per_player_fields(self) -> tuple[np.ndarray, np.ndarray]:
        """Per-player non-negative influence fields (I1, I2), recomputed
        from current owners via the kernel cache — the same arithmetic as
        _recompute_field split by owner (spec §3.1). Reads board_owners
        only, so ghost influence can never contaminate scoring."""
        rule = self.game.propagation_rule
        kernels = _influence_kernels(
            self.topo, rule.radius, rule.strength, rule.decay,
        )
        i1 = np.zeros(self.total_cells, dtype=np.float64)
        i2 = np.zeros(self.total_cells, dtype=np.float64)
        for cell in self.topo.active_cells:
            owner = int(self.board_owners[cell])
            if owner == 0:
                continue
            idx, w = kernels[cell]
            (i1 if owner == 1 else i2)[idx] += w
        return i1, i2

    def contested_scores(self) -> tuple[int, int, int]:
        """(S1, S2, engaged_count) for contested_majority (spec §3.2-3.3).

        Engaged: min(I1, I2) >= engage_threshold, over ACTIVE cells
        (empty and occupied both count — control-includes-empty
        convention). Score: engaged cells led beyond CM_LEAD_TOL;
        led-by-neither engaged cells score no one."""
        wc = self.game.win_condition
        i1, i2 = self._per_player_fields()
        active = np.asarray(list(self.topo.active_cells), dtype=np.intp)
        e1, e2 = i1[active], i2[active]
        engaged = np.minimum(e1, e2) >= wc.engage_threshold
        diff = e1 - e2
        s1 = int(np.count_nonzero(engaged & (diff > CM_LEAD_TOL)))
        s2 = int(np.count_nonzero(engaged & (diff < -CM_LEAD_TOL)))
        return s1, s2, int(np.count_nonzero(engaged))
```

- [ ] **Step 4: Run tests + suite**

Run: `.venv/bin/python -m pytest test_frontline_engine.py -q` → 7 passed.
Run: `.venv/bin/python -m pytest test_*.py -q` → all green.

- [ ] **Step 5: Commit**

```bash
git add game_engine/engine_v2.py test_frontline_engine.py
git commit -m "feat(frontline): per-player influence fields + contested_scores (spec §3.1-3.3)"
```

### Task 3: Score resolution (§3.7) + gated double-pass/timeout + placement tracking

**Files:**
- Modify: `game_engine/engine_v2.py` (`__init__`, `reset`, `_handle_placement`, `_handle_pie_swap`, `_save_state`, `_restore_state`, `_end_by_double_pass`, `_end_by_max_turns`, new `_resolve_contested_by_score`)
- Test: `test_frontline_engine.py`

- [ ] **Step 1: Write the failing tests**

```python
PASS = W * W  # pass action index (engine convention: total_cells = pass)


def test_passbot_loses_stones_tiebreak_at_komi0():
    # P1 places far-apart stones (no engagement → 0-0), P2 always passes.
    # Timeout: exact 0-0 tie → stones tiebreak → P1 wins (spec §4.4).
    g = make_cm_game(end_margin=999, min_turns=0, max_turns=8)
    engine = create_engine(g)
    engine.reset()
    p1_cells = [0, 8, 16, 176]  # pairwise distance > 4: never engaged
    i = 0
    while not engine.done:
        if engine.current_player == 1:
            engine.step(p1_cells[i]); i += 1
        else:
            engine.step(PASS)
    assert engine._ended_by_max_turns
    assert engine._winner == 1


def test_participation_clause_komi_passbot_draw():
    # komi_cells=1: zero-stone P2 would win 1 > 0 on score — the
    # participation clause downgrades to draw (spec §3.7).
    g = make_cm_game(end_margin=999, min_turns=0, komi_cells=1, max_turns=8)
    engine = create_engine(g)
    engine.reset()
    p1_cells = [0, 8, 16, 176]
    i = 0
    while not engine.done:
        if engine.current_player == 1:
            engine.step(p1_cells[i]); i += 1
        else:
            engine.step(PASS)
    assert engine._winner is None


def test_double_pass_before_min_turns_is_draw():
    g = make_cm_game(min_turns=20, max_turns=200)
    engine = create_engine(g)
    engine.reset()
    engine.step(0)      # P1 places (avoid empty-board double-pass edge)
    engine.step(PASS)   # P2
    engine.step(PASS)   # P1 → double-pass at step_count 2 < 20 → draw
    assert engine.done and engine._winner is None
    assert engine._ended_by_double_pass


def test_double_pass_after_min_turns_resolves_by_score():
    g = make_cm_game(end_margin=999, min_turns=4, max_turns=200)
    engine = create_engine(g)
    engine.reset()
    engine.step(0)      # P1
    engine.step(176)    # P2 (far away, no engagement)
    engine.step(8)      # P1
    engine.step(184)    # P2
    engine.step(PASS)   # P1, step_count 4 >= min_turns
    engine.step(PASS)   # P2 → resolve by score: 0-0 tie → stones 2-2 → draw
    assert engine.done and engine._winner is None
    assert engine._ended_by_double_pass


def test_superko_rollback_does_not_inflate_placements():
    g = make_cm_game()
    engine = create_engine(g)
    engine.reset()
    engine.step(0)
    assert engine._placements_made == [1, 0]
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest test_frontline_engine.py -q`
Expected: new tests FAIL (`AttributeError: _placements_made` / wrong winner — legacy double-pass draws and piece-majority timeout currently apply).

- [ ] **Step 3: Implement state.** In `__init__`, directly after the SIEGE quota block (engine_v2.py:~177):

```python
        # FRONTLINE contested_majority state (inert for every other family):
        # leader-signed early-end streak (+k = P1 qualified at k consecutive
        # ply-checks, -k = P2); per-player placement counts (participation
        # clause §3.7); end-cause observability flags.
        self._cm_streak: int = 0
        self._placements_made: list[int] = [0, 0]
        self._ended_by_score_margin: bool = False
        self._ended_by_double_pass: bool = False
```

In `reset()`, directly after the "Reset SIEGE quota accounting" block:

```python
        # Reset FRONTLINE contested_majority state
        self._cm_streak = 0
        self._placements_made = [0, 0]
        self._ended_by_score_margin = False
        self._ended_by_double_pass = False
```

- [ ] **Step 4: Track placements.** In `_handle_placement`, immediately after the line that writes the stone (`self.board_owners[cell] = ...` / piece_counts increment — locate with `grep -n "_handle_placement" game_engine/engine_v2.py`):

```python
        self._placements_made[self.current_player - 1] += 1
```

In `_save_state()`'s returned dict, alongside the `piece_counts` entry:

```python
            "placements_made": list(self._placements_made),
```

In `_restore_state()`, alongside the `piece_counts` restore:

```python
        self._placements_made = list(saved["placements_made"])
```

In `_handle_pie_swap`, next to the piece_counts swap:

```python
        # FRONTLINE: placement counts swap identity with the colours
        # (unused by every other family; reversing is observably inert).
        self._placements_made.reverse()
```

- [ ] **Step 5: Implement resolution + overrides.** New method after `contested_scores`:

```python
    def _resolve_contested_by_score(self) -> None:
        """Contested-majority terminal resolution (spec §3.7), shared by
        double-pass and timeout. Order: komi-adjusted score → stones
        tiebreak on EXACT ties → participation clause → draw. A
        score-leader always wins by score; pieces only break exact ties,
        so the R13/14 piece-majority exploit cannot recur. A player who
        placed zero stones the entire game can never be declared winner
        (pass-bot inaction floor, spec §4.4)."""
        wc = self.game.win_condition
        s1, s2, _ = self.contested_scores()
        s2_eff = s2 + wc.komi_cells
        if s1 > s2_eff:
            winner: Optional[int] = 1
        elif s2_eff > s1:
            winner = 2
        else:
            p1, p2 = self.piece_counts
            winner = 1 if p1 > p2 else 2 if p2 > p1 else None
        if winner is not None and self._placements_made[winner - 1] == 0:
            winner = None
        self.done = True
        self._winner = winner
```

Replace `_end_by_double_pass` body (keep + extend the docstring; legacy path identical):

```python
    def _end_by_double_pass(self) -> None:
        """End the game when both players passed consecutively.

        Legacy: draw (R13/R14 fix — piece-majority let a leader win
        without meeting the win condition).

        contested_majority (FRONTLINE, gated): the score IS the win
        condition, so at/after min_turns_score_end a double-pass resolves
        by score (spec §3.5, §3.7) — the legacy exploit cannot recur.
        Before min_turns: legacy draw (guards exploration-phase
        double-passes from instant komi wins).
        """
        self._ended_by_double_pass = True
        wc = self.game.win_condition
        if (
            wc.condition_type == "contested_majority"
            and self.step_count >= wc.min_turns_score_end
        ):
            self._resolve_contested_by_score()
            return
        self.done = True
        self._winner = None
```

In `_end_by_max_turns`, after the `timeout_winner` early-return block and BEFORE the `field_connection` branch:

```python
        if self.game.win_condition.condition_type == "contested_majority":
            # FRONTLINE: timeout resolves by score (spec §3.6-3.7).
            self._resolve_contested_by_score()
            return
```

- [ ] **Step 6: Run tests + suite**

Run: `.venv/bin/python -m pytest test_frontline_engine.py -q` → 12 passed.
Run: `.venv/bin/python -m pytest test_*.py -q` → all green (legacy double-pass/timeout untouched: the gate is the condition_type string).

- [ ] **Step 7: Commit**

```bash
git add game_engine/engine_v2.py test_frontline_engine.py
git commit -m "feat(frontline): score resolution order + gated double-pass/timeout + placement tracking (spec §3.5-3.7)"
```

### Task 4: Score-margin early-end (persistence streak + dispatch)

**Files:**
- Modify: `game_engine/engine_v2.py` (`_check_win_conditions` dispatch + new `_check_contested_majority`)
- Test: `test_frontline_engine.py`

- [ ] **Step 1: Write the failing tests**

Unit-test the streak mechanics directly (constructing a ≥8-cell lead through legal play is not unit-test material; the smoke covers integration):

```python
def _lead_board(engine):
    """Board with S1-S2 = +1 (the straggler config, spec §4.2 exact)."""
    x, d1, d2 = _interior_cell(engine.topo)
    _set_board(engine, {x: 2, d1[0]: 1, d1[1]: 1, d2[0]: 1})


def test_early_end_streak_fires_at_3_ending_odd():
    g = make_cm_game(end_margin=1, min_turns=20)
    engine = create_engine(g)
    engine.reset()
    _lead_board(engine)
    wc = g.win_condition
    for sc in (21, 22):
        engine.step_count = sc
        engine._check_contested_majority(wc)
        assert not engine.done
    engine.step_count = 23   # 3rd consecutive check, odd → round-end
    engine._check_contested_majority(wc)
    assert engine.done and engine._winner == 1
    assert engine._ended_by_score_margin


def test_early_end_streak_does_not_fire_at_even_parity():
    g = make_cm_game(end_margin=1, min_turns=20)
    engine = create_engine(g)
    engine.reset()
    _lead_board(engine)
    wc = g.win_condition
    for sc in (20, 21, 22):   # 3rd check lands EVEN → must not fire yet
        engine.step_count = sc
        engine._check_contested_majority(wc)
    assert not engine.done
    engine.step_count = 23    # 4th check, odd → fires now
    engine._check_contested_majority(wc)
    assert engine.done and engine._winner == 1


def test_early_end_min_turns_blocks_streak():
    g = make_cm_game(end_margin=1, min_turns=20)
    engine = create_engine(g)
    engine.reset()
    _lead_board(engine)
    wc = g.win_condition
    for sc in (15, 16, 17, 18, 19):
        engine.step_count = sc
        engine._check_contested_majority(wc)
    assert not engine.done and engine._cm_streak == 0


def test_early_end_leader_flip_resets_streak():
    g = make_cm_game(end_margin=1, min_turns=0)
    engine = create_engine(g)
    engine.reset()
    wc = g.win_condition
    _lead_board(engine)                  # P1 leads
    engine.step_count = 20
    engine._check_contested_majority(wc)
    assert engine._cm_streak == 1
    # Mirror ownership: now P2 leads — streak must restart at -1.
    x, d1, d2 = _interior_cell(engine.topo)
    _set_board(engine, {x: 1, d1[0]: 2, d1[1]: 2, d2[0]: 2})
    engine.step_count = 21
    engine._check_contested_majority(wc)
    assert engine._cm_streak == -1 and not engine.done


def test_early_end_komi_shifts_qualification():
    # komi_cells=1 turns P1's +1 raw lead into 0 → P1 never qualifies.
    g = make_cm_game(end_margin=1, min_turns=0, komi_cells=1)
    engine = create_engine(g)
    engine.reset()
    _lead_board(engine)
    wc = g.win_condition
    for sc in (20, 21, 22, 23):
        engine.step_count = sc
        engine._check_contested_majority(wc)
    assert not engine.done and engine._cm_streak == 0
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest test_frontline_engine.py -q`
Expected: 5 new FAIL with `AttributeError: _check_contested_majority`.

- [ ] **Step 3: Implement.** In `_check_win_conditions`, append after the `field_connection` elif (engine_v2.py:~1257):

```python
        elif ctype == "contested_majority":
            self._check_contested_majority(wc)
```

New method after `_check_field_connection`:

```python
    def _check_contested_majority(self, wc) -> None:
        """FRONTLINE early-end (spec §3.4): the same player must hold a
        komi-adjusted lead >= end_margin at 3 consecutive ply-checks
        ending at a round-end. At this call site step_count is
        PRE-increment, so a round-end (the check after P2's ply) is an
        ODD step_count — alternating games only, the family's sole
        registered turn structure; pie-swap plies skip the win check and
        preserve parity. Checks before min_turns_score_end reset the
        streak (they cannot count toward it). Leader-signed: a leader
        change restarts the streak at ±1; the intervening-odd-ply
        requirement means the lead survived the opponent's last word."""
        if self.step_count < wc.min_turns_score_end:
            self._cm_streak = 0
            return
        s1, s2, _ = self.contested_scores()
        lead = s1 - (s2 + wc.komi_cells)
        if lead >= wc.end_margin:
            self._cm_streak = self._cm_streak + 1 if self._cm_streak > 0 else 1
        elif -lead >= wc.end_margin:
            self._cm_streak = self._cm_streak - 1 if self._cm_streak < 0 else -1
        else:
            self._cm_streak = 0
            return
        if abs(self._cm_streak) >= 3 and self.step_count % 2 == 1:
            self._ended_by_score_margin = True
            self.done = True
            self._winner = 1 if self._cm_streak > 0 else 2
```

- [ ] **Step 4: Run tests + suite**

Run: `.venv/bin/python -m pytest test_frontline_engine.py -q` → 17 passed.
Run: `.venv/bin/python -m pytest test_*.py -q` → all green.

- [ ] **Step 5: Commit**

```bash
git add game_engine/engine_v2.py test_frontline_engine.py
git commit -m "feat(frontline): score-margin early-end with leader-signed 3-check persistence (spec §3.4)"
```

### Task 5: Observation floats + state_dim

**Files:**
- Modify: `game_engine/engine_v2.py:1560-1565` (`_observe` metadata block), `game_engine/game_def_v2.py:92-106` (`state_dim`)
- Test: `test_frontline_engine.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_state_dim_legacy_unchanged():
    src = Path("experiments/fc_phase15/games/calibrated/a1_field_connect.json")
    g = GameDefV2.from_dict(json.loads(src.read_text()))
    assert g.state_dim == g.total_cells * 2 + 3


def test_state_dim_contested_adds_three():
    g = make_cm_game()
    assert g.state_dim == g.total_cells * 2 + 3 + 3


def test_obs_floats_present_and_perspective_signed():
    g = make_cm_game(end_margin=8, min_turns=0)
    engine = create_engine(g)
    obs = engine.reset()
    assert obs.shape == (g.state_dim,)
    # Empty board: margin 0, engaged 0, armed 0.
    assert np.allclose(obs[-3:], [0.0, 0.0, 0.0])
    # Build the +1 P1 lead and a +2 streak, then check both perspectives.
    _lead_board(engine)
    engine._cm_streak = 2
    engine.current_player = 1
    obs1 = engine._observe()
    engine.current_player = 2
    obs2 = engine._observe()
    assert obs1[-3] == pytest.approx(1 / 8)      # score_margin_frac, own view
    assert obs2[-3] == pytest.approx(-1 / 8)
    assert obs1[-2] > 0                          # engaged_frac
    assert obs1[-1] == pytest.approx(2 / 3)      # armed_frac, leader view
    assert obs2[-1] == pytest.approx(-2 / 3)
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest test_frontline_engine.py -q`
Expected: `test_state_dim_contested_adds_three` and `test_obs_floats_present_and_perspective_signed` FAIL (dims off by 3); legacy test PASSES.

- [ ] **Step 3: Implement.** `game_def_v2.py` `state_dim`, after the capture_quota `extra`:

```python
        if self.win_condition.condition_type == "contested_majority":
            # FRONTLINE: score_margin_frac, engaged_frac, armed_frac.
            extra += 3
```

`engine_v2.py` `_observe`, after the quota_frac append and before `metadata = np.array(...)`:

```python
        if wc.condition_type == "contested_majority":
            # FRONTLINE (spec §3.9): own-perspective score margin (clip
            # ±2 keeps overshoot information), engaged share, and the
            # leader-signed persistence counter (clip ±1) — without the
            # counter the defender cannot distinguish "answer now or
            # lose" from "one round of slack" (SIEGE clock_frac lesson).
            s1, s2, engaged = self.contested_scores()
            lead_p1 = s1 - (s2 + wc.komi_cells)
            lead_self = float(lead_p1 if p == 1 else -lead_p1)
            m = max(1, wc.end_margin)
            metadata.append(float(np.clip(lead_self / m, -2.0, 2.0)))
            metadata.append(engaged / self.topo.num_active_cells)
            streak_self = self._cm_streak if p == 1 else -self._cm_streak
            metadata.append(float(np.clip(streak_self / 3.0, -1.0, 1.0)))
```

- [ ] **Step 4: Run tests + full suite (legacy dims are the critical regression)**

Run: `.venv/bin/python -m pytest test_frontline_engine.py -q` → 20 passed.
Run: `.venv/bin/python -m pytest test_*.py -q` → all green.

- [ ] **Step 5: Commit**

```bash
git add game_engine/engine_v2.py game_engine/game_def_v2.py test_frontline_engine.py
git commit -m "feat(frontline): 3 gated obs floats + state_dim (spec §3.9; legacy dims unchanged)"
```

### Task 6: Engine integration test (full game) + suite checkpoint

**Files:**
- Test: `test_frontline_engine.py`

- [ ] **Step 1: Add an end-to-end random-play smoke test**

```python
def test_full_random_game_terminates_with_known_end_cause():
    from training.utils import RandomAgent
    g = make_cm_game(pie=True)   # the real arm config has pie ON
    engine = create_engine(g)
    rng = np.random.default_rng(11)
    obs = engine.reset()
    agents = [RandomAgent(seed=int(rng.integers(2**31))) for _ in range(2)]
    while not engine.done:
        legal = engine.get_legal_actions()
        a, _, _ = agents[engine.get_current_player()].select_action(
            obs, legal_actions=legal, deterministic=False)
        obs, _, done, info = engine.step(a)
    causes = [engine._ended_by_score_margin,
              engine._ended_by_double_pass,
              engine._ended_by_max_turns]
    assert any(causes), "game must end via a known FRONTLINE cause"
    assert engine.step_count <= g.win_condition.max_turns
```

- [ ] **Step 2: Run the whole suite one more time**

Run: `.venv/bin/python -m pytest test_*.py -q`
Expected: all green, 21 frontline tests included. If the random game stalls or ends with no cause flag, debug BEFORE harness work (superpowers:systematic-debugging) — the engine is the foundation.

- [ ] **Step 3: Commit**

```bash
git add test_frontline_engine.py
git commit -m "test(frontline): end-to-end random-play termination smoke"
```

### Task 7: Scripted agents (MutualPacker, PassBot, MirrorAgent)

**Files:**
- Create: `experiments/frontline/__init__.py` (empty), `experiments/frontline/scripted_agents.py`
- Test: `test_frontline_engine.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_scripted_agents_basic_behavior():
    from experiments.frontline.scripted_agents import (
        MutualPacker, PassBot, MirrorAgent)
    g = make_cm_game(max_turns=40, min_turns=0, end_margin=999)
    engine = create_engine(g)
    obs = engine.reset()

    # PassBot always passes.
    pb = PassBot(player=2).bind(engine)
    a, _, _ = pb.select_action(obs, legal_actions=engine.get_legal_actions())
    assert a == engine.total_cells

    # MutualPacker stays >= 5 from every enemy stone.
    engine.reset()
    x, _, _ = _interior_cell(engine.topo)
    engine.board_owners[x] = 2
    engine._recompute_field()
    mp = MutualPacker(player=1).bind(engine)
    a, _, _ = mp.select_action(None, legal_actions=engine.get_legal_actions())
    assert engine.topo.distance(a, x) >= 5

    # MirrorAgent mirrors the opponent's last placement through the
    # point reflection c -> W*W-1-c.
    engine.reset()
    mi = MirrorAgent(player=2).bind(engine)
    mi.select_action(None, legal_actions=[engine.total_cells])  # snapshot empty board
    engine.step(45)   # P1 places
    a, _, _ = mi.select_action(None, legal_actions=engine.get_legal_actions())
    assert a == W * W - 1 - 45
```

- [ ] **Step 2: Run to verify failure** — `ModuleNotFoundError`.

- [ ] **Step 3: Implement `experiments/frontline/scripted_agents.py`**

```python
"""Deterministic scripted exploiter policies (prereg Stage 0b / Stage-2 bands).

MutualPacker: builds toward its own corner, never within graph distance 5
of any enemy stone (prereg pin: cross-player distance >= 5 so r=2 kernels
cannot overlap → packing-scores-zero check). PassBot: always passes
(inaction-floor probe). MirrorAgent: answers the opponent's last placement
with its point reflection c -> W*W-1-c (even-board mirror probe, spec §4.4).
ChainBuilder (front-builder) is imported from experiments.siege unchanged.

select_action signature matches RandomAgent: (obs, legal_actions,
deterministic) -> (action, log_prob, value).
"""
from __future__ import annotations

import numpy as np

from experiments.siege.scripted_agents import ChainBuilder  # noqa: F401  (re-export)

W = 22


class PassBot:
    """Always passes. Pass action index == engine.total_cells."""

    def __init__(self, player: int):
        self.player = player
        self.engine = None

    def bind(self, engine) -> "PassBot":
        self.engine = engine
        return self

    def select_action(self, obs, legal_actions=None, deterministic=False):
        return self.engine.total_cells, 0.0, 0.0


class MutualPacker:
    """Packs compactly toward its own corner, avoiding all enemy kernels.

    Corner: P1 -> cell 0, P2 -> cell W*W-1. Among legal placements at
    graph distance >= 5 from EVERY enemy stone, picks the cell closest to
    its corner (tie: lowest index). No qualifying cell -> pass.
    """

    def __init__(self, player: int):
        self.player = player
        self.corner = 0 if player == 1 else W * W - 1
        self.engine = None

    def bind(self, engine) -> "MutualPacker":
        self.engine = engine
        return self

    def select_action(self, obs, legal_actions=None, deterministic=False):
        engine = self.engine
        board, topo = engine.board_owners, engine.topo
        enemy = 3 - self.player
        enemy_cells = [c for c in topo.active_cells if int(board[c]) == enemy]
        placement = [a for a in legal_actions if a < engine.total_cells]
        ok = [a for a in placement
              if all(topo.distance(a, ec) >= 5 for ec in enemy_cells)]
        if not ok:
            return engine.total_cells, 0.0, 0.0
        best = min(ok, key=lambda a: (topo.distance(a, self.corner), a))
        return best, 0.0, 0.0


class MirrorAgent:
    """Plays the point reflection of the opponent's last placement.

    Detection: cells empty at the previous snapshot and now enemy-owned
    (flips recolor occupied cells, placements fill empty ones — so this
    isolates the placement). Mirror cell occupied/illegal, or no new
    enemy placement -> pass. Snapshot updates every select_action call.
    """

    def __init__(self, player: int):
        self.player = player
        self.engine = None
        self._prev = None

    def bind(self, engine) -> "MirrorAgent":
        self.engine = engine
        self._prev = None
        return self

    def select_action(self, obs, legal_actions=None, deterministic=False):
        engine = self.engine
        board = engine.board_owners
        enemy = 3 - self.player
        action = engine.total_cells  # default: pass
        if self._prev is not None:
            placed = [c for c in engine.topo.active_cells
                      if self._prev[c] == 0 and int(board[c]) == enemy]
            if len(placed) == 1:
                target = W * W - 1 - placed[0]
                if legal_actions and target in legal_actions:
                    action = target
        self._prev = board.copy()
        return action, 0.0, 0.0
```

Also create empty `experiments/frontline/__init__.py`.

- [ ] **Step 4: Run tests + suite** → all green.

- [ ] **Step 5: Commit**

```bash
git add experiments/frontline/__init__.py experiments/frontline/scripted_agents.py test_frontline_engine.py
git commit -m "feat(frontline): scripted exploiter agents — PassBot, MutualPacker, MirrorAgent (prereg Stage 0b)"
```

### Task 8: Stage 0a memo script (kernel arithmetic, pinned geometries)

**Files:**
- Create: `experiments/frontline/stage0_memo.py`
- Output: `experiments/frontline/STAGE0_MEMO.md`

This is prereg Stage 0a verbatim: (1) corrected flip-threshold table INCLUDING own-side d2 support; (2) engagement-saturation table, E × fill; (3) margin-swing on the pinned canonical set, vacuum + second-rank. KILL-0a1: mean margin swing < −2 over the pinned front set. KILL-0a2: analytic engaged@20% fill, E=1.0 > 0.60.

- [ ] **Step 1: Write the script.** Reuse `experiments/siege/stage0_memo.py`'s helpers (`min_attackers`, `pick_interior_cell`, `field_at` — copy them in unchanged rather than importing: the siege memo is a frozen campaign artifact and must not grow imports). New code:

```python
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


# --- copy field_at / min_attackers / pick_interior_cell verbatim from
# --- experiments/siege/stage0_memo.py lines 47-114 here (frozen-artifact
# --- copy, see plan Task 8 Step 1) ---


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
    s1_b, s2_b, _ = engine.contested_scores()
    engine.current_player = 1
    engine.step_count = 30          # past min_turns; parity irrelevant here
    engine._cm_streak = 0
    engine.step(place)
    s1_a, s2_a, _ = engine.contested_scores()
    flipped = int(engine.piece_counts[0]) - (
        sum(1 for o in pre_stones.values() if o == 1) + 1)
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
    d1_far = [x for x in d1 if topo.distance(x, east) >= 2]   # far from chain
    d1_near = [x for x in d1 if topo.distance(x, east) == 1 and x != east]
    d2_west = [x for x in d2 if topo.distance(x, east) > 2]
    behind = [east + W, east2 + W]    # second rank: next row behind chain
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
    # second-rank variants: enemy support row behind the chain
    for name in ("2chain_far", "2chain_near"):
        stones, trig = cfg[name]
        stones2 = dict(stones)
        for b in behind:
            stones2[b] = 2
        cfg[name + "_rank2"] = (stones2, trig)
    return cfg


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

    out += ["", "## 3. Margin swing at E=1.0 (engine-applied, pinned set)",
            "", "| config | before | after | swing | stones flipped |",
            "|---|---|---|---|---|"]
    swings = []
    front_keys = []
    for name, (stones, trig) in pinned_configs(engine.topo).items():
        r = margin_swing(engine, stones, trig)
        out.append(f"| {name} | {r['before']} | {r['after']} | "
                   f"{r['swing']} | {r['flipped']} |")
        if name != "straggler":
            swings.append(r["swing"])
            front_keys.append(name)

    mean_swing = sum(swings) / len(swings)
    k0a2 = sat[1.0][0.20]
    out += ["",
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
```

- [ ] **Step 2: Copy the three siege helpers in** (`field_at`, `min_attackers`, `pick_interior_cell` from `experiments/siege/stage0_memo.py:47-114`, verbatim, replacing the marked comment block).

- [ ] **Step 3: Sanity-check the pinned geometry assumptions before running** — `east = c + 1` and `east2 = c + 2` collinear at distances 1 and 2 (the test below makes this explicit). Add to `test_frontline_engine.py`:

```python
def test_stage0_pinned_geometry_assumptions():
    engine = create_engine(make_cm_game())
    topo = engine.topo
    x, _, _ = _interior_cell(topo)
    assert topo.distance(x, x + 1) == 1
    assert topo.distance(x, x + 2) == 2
    assert topo.distance(x, x + W) == 1   # next row is adjacent on hex_rhombus
```

If the `x + W` assertion fails, fix `behind` in `pinned_configs` to use a verified adjacent-row offset (check `topology.py` `_HEX_RHOMBUS_DELTAS`) — do NOT change the registered concept (a second enemy rank at distance 1-2 behind the chain).

- [ ] **Step 4: Run**

Run: `.venv/bin/python experiments/frontline/stage0_memo.py`
Expected: memo prints; section 1 shows lone=3, 2-chain end=4, 3-chain end > the memo profile (5 by count, all-d1 mix per arithmetic review), interior=6; section 2 shows engaged@20%/E=1.0 ≈ 0.10-0.11; section 3 front swings in the −2..0 range; both KILLs PASS. **If a KILL fires, STOP: that is a registered campaign outcome — apply the prereg KILL_INVALID inspection branch and report, do not "fix" thresholds.**

- [ ] **Step 5: Commit**

```bash
git add experiments/frontline/stage0_memo.py experiments/frontline/STAGE0_MEMO.md test_frontline_engine.py
git commit -m "stage0a(frontline): kernel memo — corrected thresholds, saturation, pinned margin swings (KILLs PASS)"
```

### Task 9: build_games.py + Stage 0b smoke

**Files:**
- Create: `experiments/frontline/build_games.py`
- Output: `experiments/frontline/games/*.json`, smoke report appended to `experiments/frontline/STAGE0_MEMO.md`

- [ ] **Step 1: Verify comparator sources exist**

Run: `ls experiments/siege/games/calibrated/s_flip_r2.json experiments/fc_phase15/games/calibrated/a1_field_connect.json experiments/fc_phase15/games/calibrated/a0_baseline.json`
Expected: all three listed. (If s_flip_r2.json is missing, use `experiments/siege/games/s_flip_r2.json` + komi from `experiments/siege/calibration.json` — but verify first; the calibrated file existed at SIEGE close.)

- [ ] **Step 2: Write `build_games.py`.** Mirror `experiments/siege/build_games.py` structure exactly (COMMON dict, grid builder, round-trip canonical-hash check, smoke). The frontline specifics:

```python
COMMON = dict(
    num_dimensions=2, axis_size=W, topology_type="hex_rhombus",
    turn_structure=TurnStructure(turn_type="alternating"),
    action_rule=ActionRule(action_types=("place",)),
    placement_rule=PlacementRule(target="empty", constraint="anywhere"),
    pie_rule=True,   # prereg: pie ON, komi 0 first
)
FIELD = dict(prop_type="influence", radius=2, strength=1.0, decay=0.5)
GRID_E = (0.75, 1.00, 1.25)
GRID_M = (8, 12)
SMOKE = dict(E=1.00, M=8, komi=0, seed=7)   # prereg-pinned


def build_f(e: float, m: int) -> GameDefV2:
    return GameDefV2(
        game_id=f"f_frontline_E{e:.2f}_M{m}".replace(".", "p"),
        capture_rule=CaptureRule(capture_type="field_flip"),
        propagation_rule=PropagationRule(**FIELD),
        win_condition=WinCondition(
            condition_type="contested_majority",
            engage_threshold=e, end_margin=m, min_turns_score_end=20,
            komi_cells=0, control_margin=0.0, max_turns=200),
        **COMMON,
    )
```

Smoke rollout loop: adapt `_run_rollout`/`_aggregate`/`smoke_arm` from `experiments/siege/build_games.py:132-316` with these changes (everything else verbatim):
- Per ply also record `engine.contested_scores()` → engaged trajectory and per-ply margin; per flip-ply record the margin swing (scores before vs after the step, mover-signed).
- Per game record end cause: `"score_margin" if engine._ended_by_score_margin else "double_pass" if engine._ended_by_double_pass else "timeout" if engine._ended_by_max_turns else "other"`, plus `engaged_at_80` = engaged_frac at `min(ply 80, final ply)`.
- Matchups (prereg-pinned, on the SMOKE cell only): 1000 random (seed 7 master rng, fresh RandomAgent pair per episode — copy the siege pattern verbatim); 200 ChainBuilder(P1, axis=0) vs ChainBuilder(P2, axis=1); 200 MutualPacker vs MutualPacker; 200 MirrorAgent(P2) vs ChainBuilder(P1); 200 PassBot(P2) vs ChainBuilder(P1).
- KILL asserts + contingency print:

```python
    # KILL-0b1 (build-regression): flips alive under random OR front-builder
    assert max(rand_agg["flips_per_game"], chain_agg["flips_per_game"]) >= 1.0, \
        "KILL-0b1 FIRED: flip mechanic dead"
    # KILL-0b2: packing scores zero
    assert packer_agg["mean_total_score"] <= 2.0, \
        "KILL-0b2 FIRED: mutual packers scored > 2 cells/game"
    # KILL-0b3 (design-model validation): random engaged_share at min(80, end)
    assert 0.01 < rand_agg["engaged_at_80"] < 0.60, \
        f"KILL-0b3 FIRED: engaged_share {rand_agg['engaged_at_80']:.3f}"
    # MIRROR CONTINGENCY (decision, not kill): mirror >= draw in >= 30%
    mirror_nonloss = mirror_agg["mirror_draw_or_win_share"]
    if mirror_nonloss >= 0.30:
        print(f"\n*** MIRROR_CONTINGENCY: mirror secured >= draw in "
              f"{mirror_nonloss:.0%} of games — prereg licenses ONE switch "
              f"to W=21 and a Stage-0a rerun. STOP and report. ***")
    else:
        print(f"mirror non-loss share {mirror_nonloss:.0%} < 30% — no contingency")
```

`main()`: write the 6 grid JSONs + round-trip canonical-hash check (siege pattern verbatim), copy the three comparator JSONs, run the smoke on the pinned cell, append the smoke tables to `STAGE0_MEMO.md` under a `## 4. Stage 0b smoke` heading.

- [ ] **Step 3: Run**

Run: `.venv/bin/python experiments/frontline/build_games.py`
Expected: 6 grid files + 3 comparator copies written and hash-verified; smoke tables print; KILLs PASS; mirror line prints either outcome. Runtime ~10-25 min (1800 rollouts on a 484-cell board). **If MIRROR_CONTINGENCY prints: stop the plan, report to the owner — the prereg's W=21 branch is a campaign decision, not a build decision.**

- [ ] **Step 4: Commit**

```bash
git add experiments/frontline/build_games.py experiments/frontline/games/ experiments/frontline/STAGE0_MEMO.md
git commit -m "stage0b(frontline): arm configs + pinned smoke (KILLs pass; mirror/pass-bot probes logged)"
```

### Task 10: calibrate.py (Stage 1)

**Files:**
- Create: `experiments/frontline/calibrate.py`
- Output: `experiments/frontline/calibration.{json,md}`, `experiments/frontline/games/calibrated/f_frontline.json`

- [ ] **Step 1: Write the eval helpers** (top of `calibrate.py`, after the siege-style import/path boilerplate — copy lines 36-75 of `experiments/siege/calibrate.py` for the boilerplate, dropping `eval_roles` imports):

```python
from experiments.field_connect_probe.calibrate import (  # noqa: E402
    play_game, sampled_mirror_eval,
)
from training.utils import RandomAgent  # noqa: E402

# Pre-registered Stage-1 gate constants (PREREGISTRATION.md "Stage 1").
TVR_MEAN_MIN = 0.75
TVR_SEED_MIN = 0.65
COLLAPSE_TVR = 0.20
BIAS_PASS = 0.10
KOMI_LADDER = (1, 2)            # tried as +k or -k by measured bias sign
TIMEOUT_SHARE_MAX = 0.25
DRAW_RATE_MAX = 0.05
SCORE_MARGIN_SHARE_MIN = 0.25
DOUBLE_PASS_YELLOW = 0.50
ENGAGED_BAND = (0.02, 0.60)
LENGTH_CENTER = 95.0
RESERVE_SEEDS = (45, 46)
GRID_E = (0.75, 1.00, 1.25)
GRID_M = (8, 12)


def trained_vs_random(trainer, n: int = 100, max_steps: int = 400) -> float:
    """Symmetric tvr: trained agent vs RandomAgent, both seat orders."""
    wins = 0
    half = n // 2
    for i in range(n):
        engine = create_engine(trainer.game)
        if i < half:
            a0, a1, seat = trainer.agents[0], RandomAgent(seed=9000 + i), 0
        else:
            a0, a1, seat = RandomAgent(seed=9000 + i), trainer.agents[1], 1
        winner, _, _ = play_game(engine, a0, a1, deterministic=False,
                                 max_steps=max_steps)
        wins += int(winner == seat)
    return wins / n


def eval_cell_games(trainer, n: int = 200, max_steps: int = 400) -> dict:
    """Mirrored-seat self-play eval collecting Stage-1 gate inputs.
    ALL games enter every statistic (prereg survivorship pin)."""
    half = n // 2
    rec = dict(p1_wins=0, draws=0, lengths=[], causes=[], engaged=[])
    for i in range(n):
        engine = create_engine(trainer.game)
        order = (0, 1) if i < half else (1, 0)
        a0, a1 = trainer.agents[order[0]], trainer.agents[order[1]]
        winner, length, _ = play_game(engine, a0, a1, deterministic=False,
                                      max_steps=max_steps)
        seat_of_p1 = 0  # seat 0 is always engine P1
        if winner is None:
            rec["draws"] += 1
        elif winner == seat_of_p1:
            rec["p1_wins"] += 1
        rec["lengths"].append(length)
        cause = ("score_margin" if engine._ended_by_score_margin
                 else "double_pass" if engine._ended_by_double_pass
                 else "timeout" if engine._ended_by_max_turns else "other")
        rec["causes"].append(cause)
        _, _, engaged = engine.contested_scores()
        rec["engaged"].append(engaged / engine.topo.num_active_cells)
    n_f = float(n)
    causes = rec["causes"]
    return dict(
        bias=abs(rec["p1_wins"] / n_f + 0.5 * rec["draws"] / n_f - 0.5),
        p1_share=rec["p1_wins"] / n_f,
        draw_rate=rec["draws"] / n_f,
        timeout_share=causes.count("timeout") / n_f,
        score_margin_share=causes.count("score_margin") / n_f,
        double_pass_share=causes.count("double_pass") / n_f,
        engaged_mean=float(np.mean(rec["engaged"])),
        mean_length=float(np.mean(rec["lengths"])),
    )
```

Note on `bias`: draws count half to each side (a draw-heavy meta must not masquerade as balance). Record this formula in calibration.md.

- [ ] **Step 2: Write the per-cell gate ladder** (gate ORDER is prereg-structural — skill before bias before end-cause before engaged):

```python
def train_one(game, budget, seed):
    cfg = TrainingConfig(total_steps=budget)   # mirror siege calibrate.py:95-104 EXACTLY
    trainer = SelfPlayTrainer(game, cfg, MetricsConfig(learning_curve_checkpoints=2), seed=seed)
    trainer.train()
    return trainer


def resolve_skill_gate(game, seeds, budget, used_reserves):
    """Gate (1). Collapse -> ONE replace-in-slot rerun (45 then 46, consumed
    in order across the whole grid, at most one per original seed); third
    collapse -> cell INVALID. Returns (trainers, tvrs, records, fail)."""
    trainers, tvrs, records = [], [], []
    for s in seeds:
        trainer = train_one(game, budget, s)
        tvr = trained_vs_random(trainer)
        rec = dict(orig_seed=s, final_seed=s, tvr=tvr, rerun=False)
        if tvr < COLLAPSE_TVR:
            if not used_reserves["available"]:
                return None, None, records + [rec], \
                    f"INVALID: seed {s} collapsed, reserves exhausted"
            reserve = used_reserves["available"].pop(0)
            trainer = train_one(game, budget, reserve)
            tvr2 = trained_vs_random(trainer)
            rec = dict(orig_seed=s, final_seed=reserve, tvr=tvr2,
                       rerun=True, orig_tvr=tvr)
            if tvr2 < COLLAPSE_TVR:
                return None, None, records + [rec], \
                    f"INVALID: seed {s}->{reserve} still collapsed"
            tvr = tvr2
        records.append(rec)
        trainers.append(trainer)
        tvrs.append(tvr)
    mean_tvr = sum(tvrs) / len(tvrs)
    if mean_tvr < TVR_MEAN_MIN or min(tvrs) < TVR_SEED_MIN:
        return None, None, records, (
            f"FAIL skill: mean {mean_tvr:.3f} (floor {TVR_MEAN_MIN}) "
            f"min {min(tvrs):.3f} (floor {TVR_SEED_MIN})")
    return trainers, tvrs, records, None


def calibrate_cell(e, m, seeds, budget, eval_n, used_reserves) -> dict:
    game = build_f(e, m)            # import from build_games
    trainers, tvrs, records, fail = resolve_skill_gate(
        game, seeds, budget, used_reserves)
    if fail:
        return dict(cell=f"E{e}_M{m}", verdict="FAIL", reason=fail,
                    records=records)
    # Gate (2): bias at komi 0, then the sign-directed ladder.
    for komi in (0, *KOMI_LADDER):
        evals = []
        for tr in trainers:
            if komi:
                tr.game.win_condition.komi_cells = komi_signed
            evals.append(eval_cell_games(tr, n=eval_n))
        bias = float(np.mean([ev["bias"] for ev in evals]))
        if komi == 0:
            # direction for the ladder: P1-favored -> positive komi (helps P2)
            p1_favored = np.mean([ev["p1_share"] for ev in evals]) > 0.5
        komi_signed = komi if p1_favored else -komi
        if bias <= BIAS_PASS:
            break
    else:
        return dict(cell=f"E{e}_M{m}", verdict="FAIL",
                    reason=f"bias {bias:.3f} > {BIAS_PASS} at all komi",
                    records=records)
    agg = {k: float(np.mean([ev[k] for ev in evals]))
           for k in ("draw_rate", "timeout_share", "score_margin_share",
                     "double_pass_share", "engaged_mean", "mean_length")}
    # Gate (3): end-cause health.
    if agg["timeout_share"] > TIMEOUT_SHARE_MAX:
        return dict(cell=f"E{e}_M{m}", verdict="FAIL",
                    reason=f"timeout {agg['timeout_share']:.2f}", records=records, agg=agg)
    if agg["draw_rate"] > DRAW_RATE_MAX:
        return dict(cell=f"E{e}_M{m}", verdict="FAIL",
                    reason=f"draws {agg['draw_rate']:.2f}", records=records, agg=agg)
    if agg["score_margin_share"] < SCORE_MARGIN_SHARE_MIN:
        return dict(cell=f"E{e}_M{m}", verdict="FAIL",
                    reason=f"score_margin share {agg['score_margin_share']:.2f}",
                    records=records, agg=agg)
    # Gate (4): engaged band.
    if not (ENGAGED_BAND[0] <= agg["engaged_mean"] <= ENGAGED_BAND[1]):
        return dict(cell=f"E{e}_M{m}", verdict="FAIL",
                    reason=f"engaged {agg['engaged_mean']:.3f}", records=records, agg=agg)
    flag = (" DOUBLE_PASS_YELLOW"
            if agg["double_pass_share"] > DOUBLE_PASS_YELLOW else "")
    return dict(cell=f"E{e}_M{m}", verdict="PASS" + flag, e=e, m=m,
                komi=komi_signed if bias <= BIAS_PASS and komi else 0,
                bias=bias, records=records, agg=agg, tvrs=tvrs)
```

(The `komi_signed` flow has one subtlety: at komi 0, `komi_signed` must be 0 — initialize `komi_signed = 0` before the loop. The retraining question — komi changes the game the policies were trained for — is resolved the same way siege handled the S komi sweep: re-evaluate the SAME trained policies with the komi applied at eval time, since komi only enters terminal/early-end comparisons, not placement legality. State this in calibration.md.)

Tie-break + winner write (prereg: length centrality → score_margin share → |bias|):

```python
    passing = [r for r in results if r["verdict"].startswith("PASS")]
    if not passing:
        print("F_GRID_UNRESOLVED — no passing cell; campaign NO-GO at Stage 1 "
              "(subject to the prereg KILL_INVALID inspection branch)")
        return
    passing.sort(key=lambda r: (abs(r["agg"]["mean_length"] - LENGTH_CENTER),
                                -r["agg"]["score_margin_share"],
                                r["bias"]))
    winner, runner_up = passing[0], (passing[1] if len(passing) > 1 else None)
```

Write `games/calibrated/f_frontline.json` (winner cell's game with its komi_cells baked in), `calibration.json` + regenerated `calibration.md` (every gate decision visible, the siege convention), and record the runner-up cell name (the licensed PARTIAL knob — prereg).

- [ ] **Step 3: CLI + main.** `--budget 3000 --eval-episodes 200 --seeds 42,43,44 --cells` (subset rerun support), siege-style. Reserves dict shared across cells: `used_reserves = {"available": [45, 46]}`.

- [ ] **Step 4: Dry-run on one cell with a toy budget to validate plumbing only**

Run: `.venv/bin/python experiments/frontline/calibrate.py --cells E1p00_M8 --budget 200 --eval-episodes 20`
Expected: trains, evaluates, writes calibration.json with a verdict (verdict itself is meaningless at budget 200 — this checks plumbing, not gates; do NOT commit a calibration.json from a toy run: delete it after inspection).

- [ ] **Step 5: Commit (code only)**

```bash
git add experiments/frontline/calibrate.py
git commit -m "feat(frontline): Stage-1 calibration driver — prereg gate ladder, sign-directed komi, replace-in-slot reruns"
```

### Task 11: metrics.py + run_screen.py (Stage 2)

**Files:**
- Create: `experiments/frontline/metrics.py`, `experiments/frontline/run_screen.py`
- Test: `experiments/frontline/test_frontline_metrics.py`

- [ ] **Step 1: metrics.py** — score-share progress + drama (diagnostic-only) + re-exports:

```python
"""FRONTLINE metrics (prereg Stage 1.5/2 definitions).

Drama is DIAGNOSTIC-ONLY by registration (closeness Goodhart — prereg
Stage 1.5); winner_behindness is imported from siege metrics unchanged.
control-flip instrumentation comes from the siege screen (identical r=2
instrumentation — the registered cross-arm comparable).
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from experiments.siege.metrics import winner_behindness  # noqa: E402, F401


def score_share_progress(s_self: int, s_opp: int) -> float:
    """progress_p = S_p / max(1, S_p + S_opp)  (spec §8 drama-trace row)."""
    return s_self / max(1, s_self + s_opp)
```

Test (`experiments/frontline/test_frontline_metrics.py`): `score_share_progress(0,0) == 0.0`, `(3,1) == 0.75`; `winner_behindness([0.5],[0.5]) == 0.0`. Run with `.venv/bin/python -m pytest experiments/frontline/test_frontline_metrics.py -q`.

- [ ] **Step 2: run_screen.py.** Start from a copy of `experiments/siege/run_screen.py` (the registered screen machinery) and make exactly these changes:

1. Constants block (replace siege's):

```python
ARMS = ("f_frontline", "s_flip_r2", "a1_field_connect", "a0_baseline")
LENGTH_BAND = (30.0, 160.0)
LENGTH_CENTER = 95.0
FLIP_DELTA_FLOOR = 0.5        # comparative 1: F - S >= +0.5 (DIRECTIONAL)
CENTRALITY_FLOOR = 10.0       # comparative 2: F >= 10 turns more central
COMPARATIVE_GO_MIN = 2        # GO = 2/2 (drama demoted by registration)
FLIP_EVENTS_BAND = (1.0, 20.0)
DISTINCT_FLIP_RATIO_MIN = 0.5
TIMEOUT_SHARE_MAX = 0.25
DRAW_RATE_MAX = 0.05
SCORE_MARGIN_SHARE_MIN = 0.25
ENGAGED_BAND = (0.02, 0.60)
BIAS_PASS = 0.10
TVR_MEAN_MIN, TVR_SEED_MIN = 0.75, 0.65
PASSBOT_BEAT_MIN = 0.90       # exploiter bands, each seat
MIRROR_BEAT_MIN = 0.70
A1_A0_FLIP_REPRO_MIN = 3.0    # instrumentation-reproduction check
PACKER_SCORE_MAX = 2.0
```

2. `instrumented_episode`: keep the siege flip/control instrumentation verbatim; add for the F arm a per-ply `(s1, s2, engaged)` trace via `engine.contested_scores()` and the end-cause classification (same expression as calibrate.py). Drama (diagnostic): per game, `winner_behindness(winner_share_trace, loser_share_trace)` using `score_share_progress`.
3. Bands: scored on F only (S/A1/A0 owe bias ≤ 0.10, no collapsed seed, tvr floors — comparator health per prereg; their failure prints `CAMPAIGN_UNRESOLVED — comparator failure`, never a family verdict).
4. Exploiter matches (new function): for each seed's trained F pair, play 50 games vs `PassBot` and 50 vs `MirrorAgent`, each seat; band = trained win share ≥ floors. Packer re-assert: 100 MutualPacker-vs-MutualPacker games on the calibrated F config, `mean(s1+s2 final) <= PACKER_SCORE_MAX`.
5. Reproduction check: `agg("a1_field_connect", "control_flip_rate") - agg("a0_baseline", "control_flip_rate") >= A1_A0_FLIP_REPRO_MIN` else `CAMPAIGN_UNRESOLVED`.
6. Verdict block: comparatives DIRECTIONAL (`f - s >= FLIP_DELTA_FLOOR`; centrality: `(|s_len - 95| - |f_len - 95|) >= CENTRALITY_FLOOR`); GO = 2/2 + all F bands + comparator health + reproduction check. Print `SCREEN_GO` / `SCREEN_NOGO` / `CAMPAIGN_UNRESOLVED` and write `screen_results.{csv,md}` (all stats over every eval game of the 3 final seeds — no filtering; state it in the md header).

- [ ] **Step 3: Smoke-test the screen plumbing on toy budgets**

Run: `.venv/bin/python experiments/frontline/run_screen.py --budget 200 --eval-episodes 10`
Expected: runs end-to-end on all 4 arms, writes outputs, prints a verdict line (meaningless at toy budget; delete outputs, do not commit them).

- [ ] **Step 4: Commit (code only)**

```bash
git add experiments/frontline/metrics.py experiments/frontline/run_screen.py experiments/frontline/test_frontline_metrics.py
git commit -m "feat(frontline): Stage-2 screen — directional comparatives, F bands, exploiter bands, repro check"
```

### Task 12: stage15_drama.py (diagnostic only)

**Files:**
- Create: `experiments/frontline/stage15_drama.py`

- [ ] **Step 1: Write it.** Loads `games/calibrated/f_frontline.json`, retrains seed 42 at `--budget 3000` (deterministic → same policy as calibration), plays `--n 200` trace-instrumented self-play games recording per-ply `score_share_progress` for both players, computes per-game `winner_behindness` (draws excluded from drama, counted in the report), prints + writes `stage15_drama.md`: campaign mean, share of games with drama > 0.01, and the yellow flag (`< 30% of games with per-game drama > 0.01` → `YELLOW`). No assert — diagnostic by registration; the report must state "DIAGNOSTIC-ONLY: no licensing role; Stage-2 GO is 2/2 comparatives."

- [ ] **Step 2: Plumbing dry-run** at `--budget 200 --n 20`, inspect output, delete it.

- [ ] **Step 3: Commit**

```bash
git add experiments/frontline/stage15_drama.py
git commit -m "feat(frontline): Stage-1.5 drama diagnostic (no licensing role, prereg)"
```

### Task 13: Blind-pack builder + RUN_CHECKLIST + final suite

**Files:**
- Create: `experiments/frontline/build_blind_pack.py`, `experiments/frontline/RUN_CHECKLIST.md`

- [ ] **Step 1: build_blind_pack.py.** Copies the `evaluations/stage3_ab/` machinery (BRIEFING.md template, `play.py` runpy shim, verdict templates — verify filenames with `ls evaluations/stage3_ab/`) into `evaluations/frontline_ab/` with: labels G/J/P; games = calibrated `f_frontline.json`, `s_flip_r2.json`, `a1_field_connect.json`; sealed `.blind_mapping.json` written with `json.dump` and a loud comment that it is opened only after all verdicts; BRIEFING adapted ONLY by label substitution (prereg: verdict instrument locked to the stage3_ab template — same Overall-1-10 anchors). Neutral pack name `frontline_ab` is already neutral (no treatment character leaked — "frontline" is the campaign name, matching SIEGE's renamed `stage3_ab` precedent is satisfied by NOT naming the treatment *mechanic*; if in doubt at run time, rename to `stage3_ab2`).

- [ ] **Step 2: RUN_CHECKLIST.md** — the campaign runbook (mirror `experiments/siege/RUN_CHECKLIST.md` shape):

```markdown
# FRONTLINE campaign runbook (prereg 3a378dd; spec §6-§8)

Interpreter: .venv/bin/python. STOP at any KILL — apply the prereg
KILL_INVALID inspection branch before classifying (clean kill → RETIRED).

0a. [ ] stage0_memo.py — KILL-0a1/0a2 asserted. Commit memo.
0b. [ ] build_games.py — KILL-0b1/2/3 asserted; MIRROR_CONTINGENCY check
        (>= 30% mirror non-loss → STOP, owner decision: W=21 branch).
1.  [ ] calibrate.py --budget 3000 --eval-episodes 200 --seeds 42,43,44
        (~1.5h). Passing cell → games/calibrated/f_frontline.json;
        record runner-up (PARTIAL knob). F_GRID_UNRESOLVED → NO-GO.
1.5 [ ] stage15_drama.py --budget 3000 --n 200 (~10 min). Diagnostic only.
2.  [ ] run_screen.py --budget 5000 --eval-episodes 200 (~2h).
        SCREEN_GO → blind; SCREEN_NOGO → campaign NO-GO;
        CAMPAIGN_UNRESOLVED → one retrain of the failing comparator.
3.  [ ] build_blind_pack.py; 2 independent agent teams, opposite orders,
        sealed mapping opened only after all verdicts; A1 validity
        [3.7, 4.4]; grammar per PREREGISTRATION.md Stage 3.
```

- [ ] **Step 3: Full suite, last time**

Run: `.venv/bin/python -m pytest test_*.py -q && .venv/bin/python -m pytest experiments/frontline/test_frontline_metrics.py -q`
Expected: all green.

- [ ] **Step 4: Commit**

```bash
git add experiments/frontline/build_blind_pack.py experiments/frontline/RUN_CHECKLIST.md
git commit -m "feat(frontline): blind-pack builder + campaign runbook — build complete, ready for Stage 0"
```

---

## Self-review (done at plan time)

- **Spec coverage:** §3.1-3.3 → Task 2; §3.4 → Task 4; §3.5-3.7 → Task 3; §3.8 (komi) → Tasks 1/3/10; §3.9 → Task 5; §5 build list → Tasks 1-7 (engine+agents), 8-13 (instrumentation+harness); §6 protocol → Tasks 8-13; prereg Stage 0a/0b/1/1.5/2/3 → Tasks 8/9/10/12/11/13. Drama-diagnostic demotion honored (Tasks 11, 12). Mirror contingency and KILL handling are STOP-and-report, never auto-fix.
- **Known judgment calls an executor must NOT silently change:** bias formula (draws count half — documented in calibration.md), komi applied at eval time without retraining (documented), `behind` row offset in stage0_memo (geometry-checked by test, concept locked).
- **Type consistency:** `contested_scores() -> (s1, s2, engaged)` used identically in Tasks 2/4/5/8/9/10/11; end-cause flags `_ended_by_score_margin/_ended_by_double_pass/_ended_by_max_turns` consistent across Tasks 3/4/9/10/11; scripted agent `select_action` signature matches RandomAgent everywhere.
