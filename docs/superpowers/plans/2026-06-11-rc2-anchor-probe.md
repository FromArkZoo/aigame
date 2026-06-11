# RC2 Phases A+B (Observer Field + Anchor Probe) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the measurement-only observer influence field + observer-based descriptor library, then run the pre-registered anchor probe testing whether cheap descriptor signals separate agent-judged game-quality pods where GE does not.

**Architecture:** Three new modules under `metrics/` (pure functions; zero engine/loop changes) + one experiment dir `experiments/rc2_anchor/` (PREREGISTRATION → probe runner → readout). The observer field reuses `engine_v2._influence_kernels` so parity with the in-game field is exact by construction. Rollout tracing mirrors `experiments/siege/anchor_drama.py`'s validated random+greedy protocol.

**Tech Stack:** Python 3 (`.venv/bin/python` ALWAYS — bare python3 lacks pytest/torch), numpy, pytest, sqlite3 (R21/R8 game loading). No PPO, no training anywhere in this build.

**Spec of record:** `docs/superpowers/specs/2026-06-11-rc2-selection-layer-design.md` (committed `0453e60`).

---

## Pre-verified facts (explorer-confirmed 2026-06-11; re-verify only if something fails)

- Generator gate at `game_engine/generator_v2.py:209-228` forces `prop_type='none'` off-threshold; propagation params SURVIVE in the genome.
- Kernel cache: `game_engine/engine_v2.py:45-78` `_influence_kernels(topo, radius, strength, decay)` → per-cell `(idx, weights)`; `_recompute_field` at ≈1041-1051 (returns early unless prop_type=='influence'); `_add_influence` ≈1013-1027; clip ±100.
- Field-dependent metrics that are DEAD for prop_type='none' (need the observer field): `controller_signs`/`count_controller_changes` (fc_phase15/metrics.py:13-21), `controlled_sets`/`progress_diff_field` (field_connect_probe/metrics.py:50-62), `maker_progress_span` (siege/metrics.py:75-126). Prop-agnostic and reusable as-is: `count_lead_changes`, `winner_behindness`, `largest_component`.
- anchor_drama.py (experiments/siege/): random+greedy rollout protocol (seeds `base*10_000+i` random / `base*29+31*i` greedy), DB loading via `SELECT rule_representation FROM games WHERE game_id = ?` with `contextlib.closing`, threshold per-player progress helpers `threshold_progress_p1/p2` (komi-aware, matches engine), family-drift guard pattern. DBs: `genesis_v2_run21_menger.db` (e1453dac5445), `genesis_v2_run21_grid.db` (573562833174); scores table has `go_essence` per game (35/65 grid, 64/76 menger rows).
- Agent-verdict anchors: R8 `d4015a646ae3` mean 4.10 (`evaluations/r8_replay/SUMMARY.md`); SIEGE blind S=s_flip_r2 4.10, A1=a1_field_connect 3.90 (`experiments/siege/RESULTS.md` §5); R21 slate per-game means in `evaluations/run21/SUMMARY.md` (573 and d995 tied top at 3.78; e1453 second-from-bottom; menger pod ≤3.7).
- R8 game config location is UNVERIFIED: `evaluations/r8_replay/` holds verdicts only. Task 5 includes a locate step across `genesis*.db` files; missing config = BLOCKED, not improvised.
- Suite baseline on this branch: 252-254 passed + pre-existing `test_ca_integration` collection error (+ a `test_parallel_finalize` failure that appears in some collections — both pre-exist on main).

## File structure

| File | Responsibility |
|---|---|
| `metrics/observer_field.py` (new) | Pure observer field over (topo, board_owners); parity + no-leak guarantees |
| `metrics/rollout_traces.py` (new) | Seeded random+greedy rollout harness returning per-ply traces + end info |
| `metrics/descriptors.py` (new) | Observer-based per-game descriptors (flip rate, lead changes, drama, interaction) |
| `test_rc2_metrics.py` (new, repo root) | All Phase-A tests (engine-test idiom: repo-root test_*.py) |
| `experiments/rc2_anchor/PREREGISTRATION.md` (new) | Locked pods, columns, bars, grammar |
| `experiments/rc2_anchor/run_probe.py` (new) | Anchor probe runner + readout writer |

---

### Task 1: PREREGISTRATION.md (locked before any probe data)

**Files:**
- Create: `experiments/rc2_anchor/PREREGISTRATION.md`

- [ ] **Step 1: Pin the anchor set.** Read `evaluations/run21/SUMMARY.md`'s per-game table and extract every R21 slate game id with its agent mean (7 games). Then write `experiments/rc2_anchor/PREREGISTRATION.md`:

```markdown
# RC2 anchor probe — pre-registration (locked before any probe data)

Spec: docs/superpowers/specs/2026-06-11-rc2-selection-layer-design.md (commit 0453e60).
Question: do cheap observer-based descriptor signals separate agent-judged quality
pods where GE provably does not? Zero PPO; rollouts only.

## Anchor set (every game with an agent-team verdict; pod rule applied to means)
- ABOVE pod (agent mean >= 3.9): d4015a646ae3 (R8, 4.10); s_flip_r2 (4.10);
  a1_field_connect (3.90).
- BUFFER (3.7 < mean < 3.9, reported but excluded from binary bars):
  573562833174 (3.78); d995... (3.78) [exact id from SUMMARY.md].
- BELOW pod (mean <= 3.7): e1453dac5445 + the remaining R21 slate games
  [exact ids + means transcribed from SUMMARY.md].
- Secondary check (the GE-inversion pair, binding): signal(573562833174) >
  signal(e1453dac5445) for any PASSING candidate.

## Protocol
n=200 rollouts/game (100 random-pair + 100 greedy-pair), seed 11, the
anchor_drama seeding scheme verbatim. Observer field r=2/s=1.0/d=0.5, margin 0.
Draws skipped and counted. Per-game bootstrap CI (1000 resamples).

## Candidate columns
1. obs_drama (primary).
2. blend = sqrt(norm(obs_drama) * norm(obs_lead_changes)); min-max norms over
   the anchor set (declared: ranking test, not absolute scale).
3. interaction_rate (cheap-skeptic control).
4. go_essence from the run DBs where stored (R21 games only; '—' elsewhere) —
   expected-FAIL control column.

## Bars (binary separation, point estimates; CIs reported, fragility flagged)
A candidate PASSES iff: mean(ABOVE) > mean(BELOW); AND at most 1 boundary
inversion (count of BELOW games scoring above the lowest ABOVE game); AND
e1453dac5445 not above any ABOVE-pod game; AND the secondary 573>e1453 check.

## Decision grammar (locked)
- Candidate 1 or 2 PASS -> PHASE_C_GO (register the archive-integration probe).
- Only candidate 3 PASS -> PHASE_C_GO_INTERACTION (interaction_rate primary;
  drama demoted to archive-axis-only).
- None pass -> RC2_KILL (descriptor redesign; Frontline becomes the sole
  active registered thread).
- GE passing (unexpected) -> flagged for honest synthesis; grammar unchanged.

Not altered after data.
```

(Replace the bracketed placeholders with the actual ids/means you transcribed — the committed file must contain ONLY concrete ids and numbers. If SUMMARY.md's table is ambiguous for any game, quote the ambiguity in the commit message rather than guessing.)

- [ ] **Step 2: Commit**

```bash
git add experiments/rc2_anchor/PREREGISTRATION.md
git commit -m "prereg(rc2): lock anchor pods, candidate columns, separation bars, decision grammar before any probe data"
```

---

### Task 2: observer_field.py

**Files:**
- Create: `metrics/observer_field.py`
- Test: `test_rc2_metrics.py` (new)

- [ ] **Step 1: Write failing tests** (`test_rc2_metrics.py`, repo root):

```python
"""RC2 Phase A: observer field + descriptor tests."""
import numpy as np

from game_engine.game_def_v2 import GameDefV2
from game_engine.rules import (
    PlacementRule, CaptureRule, PropagationRule, WinCondition, TurnStructure,
)
from game_engine.factory import create_engine
from metrics.observer_field import observer_field


def _game(prop_type: str, condition_type: str = "connection",
          radius: int = 2, strength: float = 1.0, decay: float = 0.5,
          axis: int = 7) -> GameDefV2:
    return GameDefV2(
        game_id=f"rc2_{prop_type}_{condition_type}", num_dimensions=2,
        axis_size=axis, topology_type="grid",
        placement_rule=PlacementRule(), capture_rule=CaptureRule(),
        propagation_rule=PropagationRule(prop_type=prop_type, radius=radius,
                                         strength=strength, decay=decay),
        win_condition=WinCondition(condition_type=condition_type,
                                   max_turns=60),
        turn_structure=TurnStructure(),
    )


def test_observer_parity_with_engine_field():
    # influence game whose params == observer defaults: observer must equal
    # the engine's own recomputed field exactly.
    game = _game("influence", condition_type="threshold")
    engine = create_engine(game)
    engine.reset()
    rng = np.random.default_rng(3)
    for _ in range(12):
        if engine.done:
            break
        engine.step(int(rng.choice(engine.get_legal_actions())))
    engine._recompute_field()
    obs = observer_field(engine.topo, engine.board_owners)
    assert np.array_equal(obs, engine.board_values)


def test_observer_nonzero_for_prop_none_and_no_leak():
    game = _game("none")
    engine = create_engine(game)
    engine.reset()
    rng = np.random.default_rng(4)
    for _ in range(8):
        if engine.done:
            break
        engine.step(int(rng.choice(engine.get_legal_actions())))
    before = engine.board_values.copy()
    obs = observer_field(engine.topo, engine.board_owners)
    assert np.count_nonzero(obs) > 0            # field defined for prop-none
    assert np.array_equal(engine.board_values, before)  # no leak
    assert np.all(before == 0.0)                # engine field genuinely dead


def test_observer_empty_board_zero():
    game = _game("none")
    engine = create_engine(game)
    engine.reset()
    assert np.count_nonzero(
        observer_field(engine.topo, engine.board_owners)) == 0
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest test_rc2_metrics.py -v`
Expected: FAIL — `metrics.observer_field` module not found.

- [ ] **Step 3: Implement** `metrics/observer_field.py`:

```python
"""Measurement-only observer influence field (RC2 Phase A).

Computes the influence field a game WOULD have under the validated
Field-Connect parameterization (r=2, strength 1.0, decay 0.5), from board
ownership alone. Pure function: never written to engine state, never read
by legality/wins/observations. Exists because generator_v2.py:209-228 forces
prop_type='none' for non-threshold win conditions, leaving board_values at
zero — which made every field-based behavior descriptor structurally dead
for most of the genome space (the fact that killed both QD pivot candidates
at the panel screen).

Parity guarantee: reuses engine_v2._influence_kernels (same cache, same
weights, same clip), so for an influence game with matching params the
observer field is array-equal to the engine's _recompute_field result.
"""
from __future__ import annotations

import numpy as np

from game_engine.engine_v2 import _influence_kernels

OBSERVER_RADIUS = 2
OBSERVER_STRENGTH = 1.0
OBSERVER_DECAY = 0.5


def observer_field(
    topo,
    board_owners: np.ndarray,
    radius: int = OBSERVER_RADIUS,
    strength: float = OBSERVER_STRENGTH,
    decay: float = OBSERVER_DECAY,
) -> np.ndarray:
    """Influence field implied by current stone ownership (P1 +, P2 -)."""
    field = np.zeros(topo.total_cells, dtype=np.float64)
    kernels = _influence_kernels(topo, radius, strength, decay)
    for cell in topo.active_cells:
        owner = int(board_owners[cell])
        if owner != 0:
            idx, w = kernels[cell]
            field[idx] += (1.0 if owner == 1 else -1.0) * w
    np.clip(field, -100.0, 100.0, out=field)
    return field
```

(If `metrics/` has no `__init__.py` or imports fail under pytest, mirror however `metrics/scoring.py` is imported by run.py — the package already exists; do not create a new package layout.)

- [ ] **Step 4: Run tests** — `.venv/bin/python -m pytest test_rc2_metrics.py -v` → 3 passed. Full suite `.venv/bin/python -m pytest test_*.py -q` → zero new failures.

- [ ] **Step 5: Commit**

```bash
git add metrics/observer_field.py test_rc2_metrics.py
git commit -m "feat(rc2): measurement-only observer field — kernel-cache parity, no engine leakage"
```

---

### Task 3: rollout_traces.py

**Files:**
- Create: `metrics/rollout_traces.py`
- Test: `test_rc2_metrics.py` (append)

- [ ] **Step 1: Write failing tests:**

```python
from metrics.rollout_traces import rollout_with_traces, run_protocol


def test_rollout_traces_shape_and_determinism():
    game = _game("none")
    r1 = rollout_with_traces(game, policy="random", seed=99)
    r2 = rollout_with_traces(game, policy="random", seed=99)
    assert r1["plies"] == r2["plies"] and r1["winner"] == r2["winner"]
    assert len(r1["owner_snapshots"]) == r1["plies"]
    # snapshots are copies, not views
    assert r1["owner_snapshots"][0] is not r1["owner_snapshots"][-1]
    assert r1["captures_total"] == r2["captures_total"]


def test_run_protocol_split():
    game = _game("none")
    out = run_protocol(game, n=6, base_seed=11)
    assert len(out) == 6
    assert sum(1 for r in out if r["policy"] == "random") == 3
    assert sum(1 for r in out if r["policy"] == "greedy") == 3
```

- [ ] **Step 2: Run to verify failure** (module missing).

- [ ] **Step 3: Implement** `metrics/rollout_traces.py`:

```python
"""Seeded rollout harness producing per-ply ownership traces (RC2 Phase A).

Protocol is anchor_drama.py's, factored for reuse: half random-pair, half
greedy-pair, deterministic seeds (random: base*10_000 + i; greedy:
base*29 + 31*i, offsets +1/+7 for the second agent — identical constants to
experiments/siege/anchor_drama.py so results remain comparable).
Returns OWNERSHIP SNAPSHOTS per ply (descriptors derive everything else via
the observer field), plus end info and capture counts attributed by
piece-count drops.
"""
from __future__ import annotations

import numpy as np

from game_engine.factory import create_engine


def _make_agents(policy: str, seed: int):
    if policy == "random":
        from training.utils import RandomAgent  # verify import path: where
        # trainer.py imports RandomAgent from; adjust to the real module.
        return RandomAgent(seed=seed), RandomAgent(seed=seed + 1)
    if policy == "greedy":
        # GreedyAgent needs (engine, player_num, seed) per trainer.py:661-686
        # — construction is finished inside rollout_with_traces once the
        # engine exists; return the constructor parameters here.
        return ("greedy", seed), ("greedy", seed + 7)
    raise ValueError(policy)


def rollout_with_traces(game, policy: str, seed: int) -> dict:
    engine = create_engine(game)
    obs = engine.reset()
    a, b = _make_agents(policy, seed)
    if policy == "greedy":
        from training.utils import GreedyAgent
        a = GreedyAgent(engine, player_num=1, seed=a[1])
        b = GreedyAgent(engine, player_num=2, seed=b[1])
    agents = [a, b]
    snapshots: list[np.ndarray] = []
    captures = 0
    prev_counts = list(engine.piece_counts)
    hard_cap = 2 * engine.game.max_game_steps
    while not engine.done and engine.step_count < hard_cap:
        legal = engine.get_legal_actions()
        agent = agents[engine.get_current_player()]
        action, _, _ = agent.select_action(obs, legal_actions=legal,
                                           deterministic=False)
        obs, _, _, info = engine.step(action)
        if not info.get("pie_swap"):
            for pidx in (0, 1):
                drop = prev_counts[pidx] - engine.piece_counts[pidx]
                if drop > 0:
                    captures += drop
            snapshots.append(engine.board_owners.copy())
        prev_counts = list(engine.piece_counts)
    return dict(
        policy=policy,
        plies=len(snapshots),
        owner_snapshots=snapshots,
        winner=engine._winner,
        timeout=bool(getattr(engine, "_ended_by_max_turns", False)),
        captures_total=captures,
        game_length=engine.step_count,
    )


def run_protocol(game, n: int, base_seed: int) -> list[dict]:
    """n rollouts: first half random-pair, second half greedy-pair."""
    half = n // 2
    out = []
    for i in range(half):
        out.append(rollout_with_traces(game, "random",
                                       seed=base_seed * 10_000 + i))
    for i in range(n - half):
        out.append(rollout_with_traces(game, "greedy",
                                       seed=base_seed * 29 + 31 * i))
    return out
```

The two `# verify import path` notes are mechanical-adaptation points: read `experiments/siege/anchor_drama.py`'s actual imports for RandomAgent/GreedyAgent and use those exact paths and constructor signatures (incl. whether GreedyAgent takes the engine positionally). Keep the seed constants EXACTLY as anchor_drama uses them.

- [ ] **Step 4: Run tests** → all pass; full suite zero new failures.

- [ ] **Step 5: Commit**

```bash
git add metrics/rollout_traces.py test_rc2_metrics.py
git commit -m "feat(rc2): seeded rollout-trace harness (anchor_drama protocol, ownership snapshots)"
```

---

### Task 4: descriptors.py

**Files:**
- Create: `metrics/descriptors.py`
- Test: `test_rc2_metrics.py` (append)

- [ ] **Step 1: Write failing tests** (closed-form fixtures — painted ownership arrays, no rollouts):

```python
from metrics.descriptors import (
    obs_progress_span, obs_lead_changes_from_snapshots,
    obs_control_flip_rate_from_snapshots, obs_drama_for_rollout,
    interaction_rate_for_rollout, descriptor_row,
)


def test_obs_progress_span_painted_board():
    game = _game("none", axis=5)
    engine = create_engine(game)
    engine.reset()
    topo = engine.topo
    owners = np.zeros(topo.total_cells, dtype=engine.board_owners.dtype)
    # P1 stones at (0,2),(2,2),(4,2): observer radius-2 influence spans all
    # 5 axis-0 coords -> span 1.0; P2 absent -> 0.0.
    for cell in (topo_cell(topo, 0, 2), topo_cell(topo, 2, 2),
                 topo_cell(topo, 4, 2)):
        owners[cell] = 1
    assert obs_progress_span(topo, owners, player=1, axis=0) == 1.0
    assert obs_progress_span(topo, owners, player=2, axis=0) == 0.0


def test_obs_lead_changes_sign_flips():
    # diffs +,-,+ across three snapshots -> 2 lead changes
    # (build three painted snapshots where P1's span leads, then P2's, then P1's)
    ...


def test_obs_control_flip_rate_counts_sign_changes():
    # two snapshots differing by one stone whose radius-2 kernel flips k cells'
    # controller sign -> flip count == k (compute k via observer_field directly
    # in the test, then assert the descriptor agrees)
    ...
```

(`topo_cell` = small test helper mapping (q, r)→cell index consistent with the topology's coords; lift from test_siege_engine.py's existing coordinate idiom. Fill the two `...` tests concretely during implementation — the assertion contracts are stated; constructing the painted snapshots takes the same painting pattern as the first test. The spec reviewer will check they are genuinely closed-form.)

- [ ] **Step 2: Run to verify failure.**

- [ ] **Step 3: Implement** `metrics/descriptors.py`:

```python
"""Observer-based per-game behavior descriptors (RC2 Phase A).

Every function takes ownership data (snapshots or arrays), computes the
observer field on demand, and reuses the validated metric implementations:
  - controller signs / flip counting: fc_phase15.metrics semantics at margin 0
  - lead changes: field_connect_probe.metrics.count_lead_changes
  - drama: experiments.siege.metrics.winner_behindness
Threshold-family progress uses score/threshold (komi-aware) like
experiments/siege/anchor_drama.py; connection/field families use
largest-component span fraction over OBSERVER-controlled cells.
"""
from __future__ import annotations

import numpy as np

from metrics.observer_field import observer_field
# count_lead_changes / largest_component / winner_behindness imports:
# use the same sys.path-free package imports anchor_drama.py uses
# (experiments.* modules import fine from repo root — mirror exactly).


def _controlled_cells(topo, field: np.ndarray, player: int,
                      margin: float = 0.0) -> set[int]:
    sign = 1.0 if player == 1 else -1.0
    return {c for c in topo.active_cells if sign * field[c] > margin}


def obs_progress_span(topo, owners: np.ndarray, player: int,
                      axis: int) -> float:
    """Span fraction along `axis` of the largest connected observer-controlled
    component (mirror of siege.metrics.maker_progress_span, observer-based)."""
    field = observer_field(topo, owners)
    cells = _controlled_cells(topo, field, player)
    if not cells:
        return 0.0
    # flood fill (same algorithm as siege.metrics) -> largest component ->
    # distinct axis coords / axis_size  [full implementation, ~15 lines]
    ...


def obs_lead_changes_from_snapshots(topo, snapshots, axis_p1: int,
                                    axis_p2: int) -> int: ...
def obs_control_flip_rate_from_snapshots(topo, snapshots) -> float: ...
def obs_drama_for_rollout(game, topo, rollout: dict) -> float | None: ...
def interaction_rate_for_rollout(topo, rollout: dict) -> float: ...


def descriptor_row(game, rollouts: list[dict]) -> dict:
    """Aggregate a game's descriptor values over a rollout list: means of
    per-rollout values; drama skips draws (None) and reports n_used."""
    ...
```

Implementation notes (binding):
- `obs_drama_for_rollout`: per-ply per-player progress traces — threshold-family games use the komi-aware score/threshold progress (lift the exact arithmetic from anchor_drama's `threshold_progress_p1/p2`, recomputing scores from snapshots × board values is NOT possible without the engine, so for threshold games compute progress from the OBSERVER field restricted to owned cells: sum(field[c] for owned c, sign-adjusted)/threshold — document this as the observer analogue and note it in PREREGISTRATION's protocol section if not already covered); connection/field/other families use `obs_progress_span` with P1 axis = `wc.target_dimension`, P2 axis = `target_dimension_p2 if >= 0 else (target+1) % num_dims`. Winner from `rollout["winner"]`; draws → None.
- `interaction_rate_for_rollout`: `captures_total / max(1, plies)` PLUS contact fraction = fraction of plies where the most recent placement is within graph distance 2 of an enemy stone (derivable from consecutive snapshots: the placed cell is the new nonzero); return their mean. State the formula in the docstring; it is pre-registered via the spec.
- The `...` bodies must be complete in the actual implementation — the contracts and reuse sources are fixed above; no design freedom beyond mechanical adaptation.

- [ ] **Step 4: Run tests** → all pass; full suite zero new failures.

- [ ] **Step 5: Commit**

```bash
git add metrics/descriptors.py test_rc2_metrics.py
git commit -m "feat(rc2): observer-based descriptor library (span, lead changes, flip rate, drama, interaction)"
```

---

### Task 5: run_probe.py + anchor-game loading

**Files:**
- Create: `experiments/rc2_anchor/run_probe.py`

- [ ] **Step 1: Locate the R8 anchor config.** Run:

```bash
for db in ~/aigame/genesis*.db; do echo "== $db"; sqlite3 "$db" \
  "SELECT game_id FROM games WHERE game_id LIKE 'd4015a646ae3%' LIMIT 1" 2>/dev/null; done
rg -l "d4015a646ae3" --glob "*.json" ~/aigame 2>/dev/null | head
```

Expected: at least one hit (an R8-era genesis DB or a JSON). Record the source. If NO hit: report BLOCKED with the search evidence (do not reconstruct the game from prose).

- [ ] **Step 2: Write run_probe.py.** Structure (mirror anchor_drama.py's conventions: GAME_SPECS dict, family-drift guard, contextlib.closing for DBs, loud missing-file errors, md report):

- GAME_SPECS: every PREREGISTRATION anchor game → loader (siege games dir JSONs for s_flip_r2 [use `experiments/siege/games/calibrated/s_flip_r2.json`] and a1/a0-style paths; run21 DBs for the slate; the located R8 source). Family field per game validated against the loaded `condition_type` (drift guard, same as anchor_drama).
- CLI: `--n 200 --seed 11 --games all|comma-list --out experiments/rc2_anchor/`.
- Per game: `run_protocol(game, n, seed)` → `descriptor_row(...)` → columns: obs_drama, blend (computed AFTER all games: min-max norms over the full anchor set, then sqrt(product)), interaction_rate, plus `go_essence` read from the game's source DB scores table (`'—'` when absent).
- Bootstrap: 1000 resamples over per-rollout values per game per column → 95% CI.
- Bars: transcribe from PREREGISTRATION verbatim as data (the fc_phase15 checks-list idiom): pod separation, ≤1 boundary inversion, e1453-not-above-ABOVE, secondary 573>e1453; evaluate per candidate column; GE column evaluated identically as the control.
- Verdict line printed + written: `PHASE_C_GO` / `PHASE_C_GO_INTERACTION` / `RC2_KILL` (+ `GE_CONTROL_PASSED` flag if it happens). Subset `--games` runs print `PROBE_INCOMPLETE (subset — no verdict)` and write no md (anchor_drama precedent).
- Output: `experiments/rc2_anchor/probe_results.md` (full table: game, pod, n_used, draws, all columns with CIs; bars table per candidate; verdict) + `probe_results.csv`.

- [ ] **Step 3: Smoke** — `.venv/bin/python experiments/rc2_anchor/run_probe.py --n 8 --seed 11 --games s_flip_r2,e1453` → table prints, `PROBE_INCOMPLETE`, no md. Then `--n 8 --games all` (verdict prints at noise level; delete the generated md/csv before committing; note R8 load worked).

- [ ] **Step 4: Commit**

```bash
git add experiments/rc2_anchor/run_probe.py
git commit -m "feat(rc2): anchor probe runner — 4 columns, bootstrap CIs, pre-registered separation bars"
```

---

### Task 6: regression + execution

- [ ] **Step 1:** Full suite: `.venv/bin/python -m pytest test_*.py experiments/siege/test_siege_metrics.py -q` → zero new failures vs branch base `da75882`. Working tree clean.
- [ ] **Step 2 (EXECUTION — the real probe):** `.venv/bin/python experiments/rc2_anchor/run_probe.py --n 200 --seed 11 --games all` (~60–90 min, zero PPO). Commit `probe_results.md` + `.csv` as `results(rc2): anchor probe readout — <verdict>`.
- [ ] **Step 3:** Write `experiments/rc2_anchor/RESULTS.md` (fc_phase15 format: decision first, protocol, table, honest synthesis incl. CI fragility flags and the GE control outcome, prereg audit). Commit. Merge decision per finishing-a-development-branch.

---

## Self-review notes

- Spec §3 (observer field + parity/no-leak invariants) → Task 2. §3 descriptor library → Task 4. §3 rollout harness factored → Task 3 (anchor_drama NOT modified — honored). §4 anchor set/columns/bars/grammar → Tasks 1, 5. §5 zero engine/loop changes → no task touches engine/, evolution/, run.py. §6 grammar → Task 5 verdict lines. §7 no-MCTS rationale → no MCTS column anywhere. ✓
- Buffer-pod refinement (573/d995 at 3.78 excluded from binary bars, 573>e1453 kept binding) is a spec amendment carried in Task 1's prereg — flagged here explicitly: the spec's §4 pod table listed 573 in ABOVE; the prereg supersedes with the buffer rule because 573's agent mean (3.78) sits below A1 (3.90) and forcing it into ABOVE would let the buffer dominate the bars. Committed before any data, so registration discipline holds.
- Tasks 4 and 5 contain deliberately contract-pinned stubs (`...`) where the implementation is mechanical adaptation of named, existing code — each names its exact source. Spec reviewers must verify the adaptations against those sources.
