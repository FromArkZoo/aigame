# RC2 Campaign Runner — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the RC2 campaign runner that drives planning-gap-driven QD search (Phase C ARCHIVE_GO machinery with quality = floored T1-PG instead of drama), applies the §6 bars via a pure `decide_verdict` over the §9 precedence chain, and produces a 7-label blind slate — implementing the LOCKED preregistration `experiments/rc2_campaign/PREREGISTRATION.md` (`72890a0`).

**Architecture:** A "drop-in swap" of the Phase C archive: cells stay descriptor-based (`evolution/qd_archive.py` verbatim — `cell_key` over a random-policy descriptor batch), but the displacement key and QD quality become `max(T1-PG, 0)` from a *separate* net-free UCT evaluation, elites carry a second full-convention PG ledger written only at re-eval checkpoints, and an insertion-time guard stage (RUSH/TILT tactical rollouts + REACH-v3 draw share) vetoes degenerate would-be inserters. The runner forks `experiments/rc2_archive/run_probe.py`'s stage machine. A pure `decide_verdict` transcribes the §0-finalized constants and is exhaustively branch-tested pre-data.

**Tech Stack:** Python 3.13 (`.venv/bin/python`), numpy, `ProcessPoolExecutor` for parallel eval, plain `pytest` (no config; tests are `test_*.py` importing top-level packages with repo root as cwd). Reuses `game_engine/`, `evolution/`, `metrics/`, `training/`, `experiments/mcts_phase1/`, and the locked §0 CAL artifacts.

## Global Constraints

Every task's requirements implicitly include this section. Values are transcribed **verbatim** from the locked prereg / §0 files — never recompute or "improve" them; they are data.

- **Interpreter / cwd:** run everything as `.venv/bin/python …` from repo root `/Users/jamesbrowne/aigame`. Tests: `.venv/bin/python -m pytest <file> -v`.
- **Prereg authority:** `experiments/rc2_campaign/PREREGISTRATION.md` (`72890a0`) is the contract. On any conflict with the older design doc (`docs/superpowers/specs/2026-06-12-rc2-campaign-design.md`), the prereg wins.
- **Quality signal:** insertion/QD quality = `max(T1-PG, 0)` (floored). Raw T1-PG always recorded. Insertion requires **strict** improvement on floored T1-PG; 0-vs-0 never displaces (first occupancy still counts coverage).
- **T1 instrument:** net-free UCT@128 vs UCT@16, n=24 (12 seat-balanced each way), draws=0.5, `max_steps=400`. Reuse `experiments/rc2_planning_gap/anchor_calibration.py`'s `UCTAgent`/`UCTEvaluator`/`UniformEvaluator` (the SAME instrument CAL-I validates).
- **Full-conv instrument:** UCT@256 vs UCT@16, n=48. Written to the full-conv ledger only at re-eval checkpoints.
- **Budget:** B = **600** evaluated genomes per arm. Re-eval checkpoints at eval counts **150 / 300 / 450 / 600** per arm.
- **Stage 0:** stop when every sampleable family has ≥ **20** valid genomes AND total valid ≥ **150**; caps **240** evaluated / **3000** attempts; `REDRAW_CAP=50`.
- **Seed bases (base 19 × {1..5}):** Stage-0/CAL generation **19_000_000**; arm R **38_000_000**; arm M mutation rng **57_000_000**; arm M cell-selection rng **76_000_000**; bootstrap **95_000_000**. Content-derived eval seed: `eval_seed = (int(canonical_hash()[:16],16) + 7919*batch_index) mod 2^31` (reuse `experiments/rc2_archive/run_probe.py::eval_seed_for`).
- **Guard constants (§0-finalized, CAL-G/CAL-R):** RUSH `≥0.25` of decisive tactical games end in `≤6` plies; TILT P1-win share `≥0.625` (15/24) of decisive tactical games; REACH-v3 (threshold family only) `≥5/24` of the genome's own T1 games end winner-None.
- **Bar constants (§0-finalized):** CAL-I threshold `0.431` (= 3·σ_diff, σ_diff=0.1437); BAR W-PG floored floor `0.167`; BAR H-PG floor `0.05`; saturation switch at R_top10 `≥0.40` → per-cell M-wins `≥60%` on `≥20` joint cells; S-GO-1 `≥4.10`; S-GO-2 separation `≥+0.4`; min-contrast precondition `<0.15` → SEPARATION_UNDERDETERMINED; d4015 validity band `[3.48, 4.18]`; search-phase wall cap `8 h`.
- **Registered exclusion:** genomes with simultaneous-move turn structure are quick-rejected (UCT instrument constraint); counted and reported as UNSAMPLED contribution.
- **Prereg discipline:** the prereg is locked pre-data. Post-lock code decisions must be pre-data and review-logged (see "Pre-data build decisions" below). No constant changes after data.

## Pre-data build decisions (review-logged per §10)

The lock pins all constants and bars but leaves a few implementation-level choices open. These are resolved here from the spec + `PANEL_FINDINGS.md`, and must be **ratified by the owner before Task 1 runs** (they are pre-data; log ratification in `experiments/rc2_campaign/BUILD_LOG.md`, Task 0).

1. **Cell placement = Phase-C descriptor batch, verbatim.** The QD cell stays `(family, interaction_bin, length_bin)` from `evolution/qd_archive.py::cell_key` over a random-policy descriptor batch (`run_protocol`). Only the displacement/quality key swaps to floored T1-PG. Basis: `PANEL_FINDINGS.md:352/366` treat the cell machinery as `qd_archive.py` verbatim; design doc "descriptor_row cells… Phase C verbatim." Consequence: each genome eval runs **both** a descriptor batch (for the cell) and a T1-PG eval (for quality/validity/REACH). The descriptor batch's drama is recorded but non-binding.
2. **Validity from the T1 games** (not the descriptor batch): non-draw T1 share ≥0.50, mean T1 game length ≥6 plies, T1-PG non-nan (prereg §4 [C13] "PG era" transcription).
3. **Content-seed expansion.** A genome's T1 batch `b` derives its 24 games from `rng = np.random.default_rng(eval_seed_for(canon, b))`: for game `j`, `deep_seed, shallow_seed = rng.integers(0, 2**31-1, size=2)`; `deep_seat = 0 if j < 12 else 1`. Deterministic, content-derived per the §2 formula. The fixed anchor streams (42–47) stay CAL-only. Descriptor batch keeps its Phase-C seed (`eval_seed_for(canon, b)` → `run_protocol`).
4. **Guard stage gates every insertion** — empty cell (first occupancy) OR strict improvement — not only "beats an existing incumbent." A first-occupancy elite can reach the slate, so it must pass RUSH/TILT/REACH too. (§4's "beats the incumbent" reads as "would enter the archive"; empty cell = trivially enters.)
5. **`rollout_tactical` lifted to `metrics/guard_probe.py`**; `experiments/rc2_descriptor_v2/run_probe.py` re-imports it from there (back-compat: `cal_g.py` still works). `TacticalAgent` already lives in `metrics/tactical_agent.py`.
6. **Net-free UCT reused from `anchor_calibration.py`** (do not duplicate/refactor that locked §0 file) so the campaign T1 instrument is provably identical to the one CAL-I validates. `eval_seed_for` reused from `rc2_archive/run_probe.py`.
7. **T1 eval-count matching is structurally a no-op** (every genome's T1-PG is a single n=24 batch, so incumbent and challenger pooled_n always match). Re-eval adds full-conv batches to the *separate* full-conv ledger, never more T1 batches — so T1 pooled_n never grows. Keep the comparison as strict floored-T1-PG.

---

## File structure

New files (all under `experiments/rc2_campaign/` unless noted):

- `metrics/guard_probe.py` — lifted `rollout_tactical` + guard share functions (RUSH/TILT). One responsibility: tactical-rollout guard primitives, reusable across CAL-G and the campaign.
- `pg_eval.py` — genome-based net-free UCT PG evaluator (T1 + full-conv), content-seeded. Reuses `anchor_calibration` UCT classes.
- `seeds.py` — campaign seed-base constants + `assert_disjoint()` against all recorded stream families.
- `campaign_archive.py` — `CampaignElite` / `CampaignArchive`: PG-quality MAP-Elites archive with the full-conv ledger and a guard hook. Reuses `qd_archive` cell/bin helpers.
- `guard_stage.py` — orchestrates the insertion guard stage (RUSH/TILT via `guard_probe`, REACH-v3 via the genome's T1 draws) with content-derived mirrored seeds; returns a veto decision + per-guard reasons.
- `bars.py` — pure bar evaluators (BAR W-PG, BAR H-PG + saturation switch, slate bars) and the pure `decide_verdict` over the §9 precedence chain. Constants transcribed from §0.
- `slate.py` — slate composition + constraints (family cap, near-dup screen) + substitution log.
- `build_blind_pack.py` — 7-label blind-pack generator (fork of `experiments/frontline/build_blind_pack.py`, multi-dim `describe_rules` from `evaluations/rc2_phase_d/play.py`).
- `grep_verdicts.py` — pre-unblind identifier/recognition grep guard.
- `run_campaign.py` — the runner (stage machine: CAL-I → Stage 0 → arms → re-eval → write results), forked from `rc2_archive/run_probe.py`.
- `cal_i.py` — pre-campaign CAL-I instrument check (streams 46/47).
- `cal_c.py` — pre-campaign CAL-C cost projection (20 fresh genomes through the full pipeline).
- Tests colocated: `test_guard_probe.py`, `test_pg_eval.py`, `test_seeds.py`, `test_campaign_archive.py`, `test_guard_stage.py`, `test_bars.py`, `test_slate.py`, `test_blind_pack.py`.

Modified: `experiments/rc2_descriptor_v2/run_probe.py` (re-import `rollout_tactical` from `metrics.guard_probe`).

Task dependency order: 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12. Tasks 8 (bars/verdict), 9 (slate), 10 (blind pack) depend only on data shapes and can be built in parallel once 7 lands if using subagents.

---

### Task 0: Build log + owner ratification of pre-data decisions

**Files:**
- Create: `experiments/rc2_campaign/BUILD_LOG.md`

- [ ] **Step 1: Write the build log** capturing the 7 pre-data build decisions above verbatim, each with its basis citation, and an "Owner ratification" line left blank.

- [ ] **Step 2: Obtain owner sign-off** on the 7 decisions (this is a checkpoint — do not proceed to Task 1 until ratified; record date + the decision the owner made if any is adjusted).

- [ ] **Step 3: Commit**

```bash
git add experiments/rc2_campaign/BUILD_LOG.md
git commit -m "build(rc2-campaign): pre-data build-decisions log (Task 0)"
```

---

### Task 1: Lift `rollout_tactical` + guard primitives into `metrics/guard_probe.py`

**Files:**
- Create: `metrics/guard_probe.py`
- Modify: `experiments/rc2_descriptor_v2/run_probe.py` (re-import for back-compat)
- Test: `experiments/rc2_campaign/test_guard_probe.py`

**Interfaces:**
- Produces: `rollout_tactical(game: GameDefV2, seed_p1: int, seed_p2: int) -> dict` (keys incl. `winner`, `plies`, `game_length`, `timeout`); `rush_share(records: list[dict]) -> tuple[int, float]` returns `(decisive, share_le6)`; `tilt_p1_share(records: list[dict]) -> tuple[int, float]` returns `(decisive, p1_win_share)`; constants `RUSH_PLY_CAP=6`, `RUSH_SHARE=0.25`, `TILT_SHARE_REPRICED=0.625`.
- Consumes: `metrics.tactical_agent.TacticalAgent`, `game_engine.factory.create_engine`, `game_engine.game_def_v2.GameDefV2`.

- [ ] **Step 1: Write the failing test** `test_guard_probe.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from metrics.guard_probe import (
    rollout_tactical, rush_share, tilt_p1_share,
    RUSH_PLY_CAP, RUSH_SHARE, TILT_SHARE_REPRICED,
)
from experiments.rc2_descriptor_v2.run_probe import load_roster_game


def test_constants():
    assert RUSH_PLY_CAP == 6 and RUSH_SHARE == 0.25 and TILT_SHARE_REPRICED == 0.625


def test_rollout_tactical_deterministic():
    game = load_roster_game("d4015a646ae3")
    a = rollout_tactical(game, 11, 22)
    b = rollout_tactical(game, 11, 22)
    assert a["winner"] == b["winner"] and a["plies"] == b["plies"]


def test_share_helpers_ignore_draws():
    recs = [
        {"winner": 1, "plies": 4}, {"winner": 2, "plies": 10},
        {"winner": None, "plies": 400}, {"winner": 1, "plies": 6},
    ]
    dec, s6 = rush_share(recs)
    assert dec == 3 and abs(s6 - 2/3) < 1e-9      # 2 of 3 decisive end <=6 plies
    dec2, p1 = tilt_p1_share(recs)
    assert dec2 == 3 and abs(p1 - 2/3) < 1e-9      # 2 of 3 decisive won by P1


def test_backcompat_reexport():
    from experiments.rc2_descriptor_v2.run_probe import rollout_tactical as rt
    assert rt is rollout_tactical
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest experiments/rc2_campaign/test_guard_probe.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'metrics.guard_probe'`.

- [ ] **Step 3: Create `metrics/guard_probe.py`** — move the body of `rollout_tactical` (currently `experiments/rc2_descriptor_v2/run_probe.py:201-237`) here verbatim, plus the share helpers derived from `guard_rush`/`guard_tilt` (returning counts, not the boolean — the campaign applies its own re-priced thresholds):

```python
"""Tactical-rollout guard primitives (RC2). Lifted from rc2_descriptor_v2 so
the campaign guard stage and CAL-G share one implementation (prereg §4 [C2])."""
from __future__ import annotations

from game_engine.factory import create_engine
from game_engine.game_def_v2 import GameDefV2
from metrics.tactical_agent import TacticalAgent

RUSH_PLY_CAP = 6          # "winner in <= 6 plies"
RUSH_SHARE = 0.25         # ">= 25% of decisive tactical games"
TILT_SHARE_REPRICED = 0.625   # CAL-G re-price (15/24); prereg §4


def rollout_tactical(game: GameDefV2, seed_p1: int, seed_p2: int) -> dict:
    # --- verbatim from rc2_descriptor_v2/run_probe.py:201-237 ---
    # (build TacticalAgent seat-1/seat-2, loop engine.step to done or
    #  2*max_game_steps; return dict(policy, plies, owner_snapshots, winner,
    #  timeout, captures_total, game_length))
    ...


def rush_share(records: list[dict]) -> tuple[int, float]:
    """(decisive_count, share of decisive games ending in <= RUSH_PLY_CAP plies)."""
    decisive = [r for r in records if r["winner"] is not None]
    if not decisive:
        return 0, float("nan")
    return len(decisive), sum(1 for r in decisive if r["plies"] <= RUSH_PLY_CAP) / len(decisive)


def tilt_p1_share(records: list[dict]) -> tuple[int, float]:
    """(decisive_count, share of decisive games won by P1)."""
    decisive = [r for r in records if r["winner"] is not None]
    if not decisive:
        return 0, float("nan")
    return len(decisive), sum(1 for r in decisive if r["winner"] == 1) / len(decisive)
```

Copy the exact `rollout_tactical` body from the source file (do not paraphrase it). Then in `experiments/rc2_descriptor_v2/run_probe.py`, replace the local `def rollout_tactical(...)` with `from metrics.guard_probe import rollout_tactical` (keep `guard_rush`/`guard_tilt`/`pair_seeds` where they are — `cal_g.py` imports them from run_probe).

- [ ] **Step 4: Run tests to verify they pass** (and that CAL-G's import path still resolves)

Run: `.venv/bin/python -m pytest experiments/rc2_campaign/test_guard_probe.py test_rc2_descriptor_v2.py -v`
Expected: PASS (all).

- [ ] **Step 5: Commit**

```bash
git add metrics/guard_probe.py experiments/rc2_descriptor_v2/run_probe.py experiments/rc2_campaign/test_guard_probe.py
git commit -m "feat(rc2-campaign): lift rollout_tactical + guard shares into metrics/guard_probe (Task 1)"
```

---

### Task 2: Genome-based PG evaluator (`pg_eval.py`)

**Files:**
- Create: `experiments/rc2_campaign/pg_eval.py`
- Test: `experiments/rc2_campaign/test_pg_eval.py`

**Interfaces:**
- Consumes: `experiments.rc2_planning_gap.anchor_calibration.{UCTAgent, MAX_STEPS}`, `experiments.rc2_archive.run_probe.eval_seed_for`, `game_engine.factory.create_engine`, `training.utils.play_game`.
- Produces:
  - `pg_seeds(canon: str, batch_index: int, n: int = 24) -> list[tuple[int,int,int]]` → list of `(deep_seed, shallow_seed, deep_seat)`.
  - `pg_game(game, deep_seed, shallow_seed, deep_seat, deep_sims, shallow_sims) -> dict` → `{score, winner, length}` (score 0.5 draw / 1.0 deep-win / 0.0 deep-loss).
  - `pg_batch(game, canon, batch_index=0, deep_sims=128, shallow_sims=16, n=24) -> dict` → `{raw_pg, floored_pg, wins, draws, losses, n, non_draw_share, mean_length, scores}`.
  - Constants `T1_DEEP=128`, `T1_SHALLOW=16`, `FULL_DEEP=256`, `FULL_SHALLOW=16`, `T1_N=24`, `FULL_N=48`.

- [ ] **Step 1: Write the failing test** `test_pg_eval.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.rc2_campaign.pg_eval import (
    pg_seeds, pg_batch, T1_DEEP, T1_SHALLOW, T1_N,
)
from experiments.rc2_descriptor_v2.run_probe import load_roster_game

CANON = "0" * 64  # 16 leading hex zeros -> deterministic seed base


def test_seat_balance_and_determinism():
    s = pg_seeds(CANON, 0, n=24)
    assert len(s) == 24
    assert [seat for *_ , seat in s][:12] == [0] * 12   # first half deep=P1
    assert [seat for *_ , seat in s][12:] == [1] * 12
    assert pg_seeds(CANON, 0) == pg_seeds(CANON, 0)      # deterministic
    assert pg_seeds(CANON, 0) != pg_seeds(CANON, 1)      # batch_index varies


def test_pg_batch_shape_and_reproducible():
    game = load_roster_game("d4015a646ae3")
    r1 = pg_batch(game, "d4015a646ae30000" + "0" * 48, deep_sims=32, shallow_sims=8, n=8)
    r2 = pg_batch(game, "d4015a646ae30000" + "0" * 48, deep_sims=32, shallow_sims=8, n=8)
    assert r1["raw_pg"] == r2["raw_pg"]                  # reproducible
    assert r1["wins"] + r1["draws"] + r1["losses"] == 8
    assert abs(r1["raw_pg"] - (sum(r1["scores"]) / 8 - 0.5)) < 1e-12
    assert r1["floored_pg"] == max(r1["raw_pg"], 0.0)
    assert 0.0 <= r1["non_draw_share"] <= 1.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest experiments/rc2_campaign/test_pg_eval.py -v`
Expected: FAIL (`No module named 'experiments.rc2_campaign.pg_eval'`).

- [ ] **Step 3: Implement `pg_eval.py`** (adapts `anchor_calibration.play_cell`/`summarise` to arbitrary genomes with content-derived seeds — build decision #3/#6):

```python
"""Genome-based net-free UCT planning-gap evaluator (RC2 campaign).

Reuses anchor_calibration's UCT instrument (same one CAL-I validates) but
seeds each genome's games from the content-derived eval_seed_for formula
(prereg §2) instead of the fixed anchor streams. See BUILD_LOG decisions 3/6.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game_engine.factory import create_engine  # noqa: E402
from training.utils import play_game  # noqa: E402
from experiments.rc2_planning_gap.anchor_calibration import UCTAgent, MAX_STEPS  # noqa: E402
from experiments.rc2_archive.run_probe import eval_seed_for  # noqa: E402

T1_DEEP, T1_SHALLOW, T1_N = 128, 16, 24
FULL_DEEP, FULL_SHALLOW, FULL_N = 256, 16, 48


def pg_seeds(canon: str, batch_index: int, n: int = T1_N) -> list[tuple[int, int, int]]:
    rng = np.random.default_rng(eval_seed_for(canon, batch_index))
    out = []
    for j in range(n):
        deep_seed, shallow_seed = (int(x) for x in rng.integers(0, 2**31 - 1, size=2))
        out.append((deep_seed, shallow_seed, 0 if j < n // 2 else 1))
    return out


def pg_game(game, deep_seed, shallow_seed, deep_seat, deep_sims, shallow_sims) -> dict:
    engine = create_engine(game)
    deep = UCTAgent(engine, deep_sims, deep_seed)
    shallow = UCTAgent(engine, shallow_sims, shallow_seed)
    agents = (deep, shallow) if deep_seat == 0 else (shallow, deep)
    winner, length, _ = play_game(engine, agents[0], agents[1],
                                  deterministic=True, max_steps=MAX_STEPS)
    score = 0.5 if winner is None else float(winner == deep_seat)
    return dict(score=score, winner=winner, length=length)


def pg_batch(game, canon: str, batch_index: int = 0,
             deep_sims: int = T1_DEEP, shallow_sims: int = T1_SHALLOW,
             n: int = T1_N) -> dict:
    cells = [pg_game(game, ds, ss, seat, deep_sims, shallow_sims)
             for (ds, ss, seat) in pg_seeds(canon, batch_index, n)]
    scores = [c["score"] for c in cells]
    wins = sum(1 for c in cells if c["score"] == 1.0)
    draws = sum(1 for c in cells if c["score"] == 0.5)
    losses = sum(1 for c in cells if c["score"] == 0.0)
    raw = float(np.mean(scores)) - 0.5
    return dict(raw_pg=raw, floored_pg=max(raw, 0.0), wins=wins, draws=draws,
                losses=losses, n=n, non_draw_share=(wins + losses) / n,
                mean_length=float(np.mean([c["length"] for c in cells])),
                scores=scores)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest experiments/rc2_campaign/test_pg_eval.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/rc2_campaign/pg_eval.py experiments/rc2_campaign/test_pg_eval.py
git commit -m "feat(rc2-campaign): genome-based content-seeded PG evaluator (Task 2)"
```

---

### Task 3: Seed constants + disjointness assert (`seeds.py`) [C1]

**Files:**
- Create: `experiments/rc2_campaign/seeds.py`
- Test: `experiments/rc2_campaign/test_seeds.py`

**Interfaces:**
- Produces: constants `GEN_SEED_BASE=19_000_000`, `ARM_R_SEED_BASE=38_000_000`, `ARM_M_MUT_SEED=57_000_000`, `ARM_M_SEL_SEED=76_000_000`, `BOOT_SEED=95_000_000`; `RECORDED_STREAMS: dict[str, tuple[int,int]]` (each family's `(base, span)` claimed range — base-13 Phase C, base-17 Phase C R2, anchor small seeds 42–47, smoke offsets); `assert_disjoint() -> None` raising `RuntimeError` on any overlap.

- [ ] **Step 1: Write the failing test** `test_seeds.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pytest
from experiments.rc2_campaign import seeds


def test_bases_are_base19():
    assert seeds.GEN_SEED_BASE == 19_000_000
    assert seeds.ARM_R_SEED_BASE == 38_000_000
    assert seeds.ARM_M_MUT_SEED == 57_000_000
    assert seeds.ARM_M_SEL_SEED == 76_000_000
    assert seeds.BOOT_SEED == 95_000_000


def test_disjoint_passes_on_registered_layout():
    seeds.assert_disjoint()  # the registered bases must not overlap recorded streams


def test_disjoint_catches_overlap(monkeypatch):
    # A base colliding with Phase C base-13 (13_000_000 .. +span) must raise.
    monkeypatch.setattr(seeds, "GEN_SEED_BASE", 13_000_100)
    with pytest.raises(RuntimeError):
        seeds.assert_disjoint()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest experiments/rc2_campaign/test_seeds.py -v`
Expected: FAIL (`No module named 'experiments.rc2_campaign.seeds'`).

- [ ] **Step 3: Implement `seeds.py`.** Each campaign base claims `[base, base + SPAN)` with `SPAN = 1_000_000` (real consumption is tens of thousands: 3000-attempt Stage-0, ≤600×50 arm draws; 1M matches the repo's de-facto stream spacing — Phase C R2's 51M sits 1M below Phase C's 52M. **Errata 2026-07-02:** the plan originally said 4M, which falsely overlaps the locked 19M gen base with Phase C R2's 17M stream — caught by the assert itself during build; BUILD_LOG decision #8). Recorded streams to avoid: Phase C base-13 families (`13/26/39/52/65 ×1e6`, each +SPAN), Phase C R2 base-17 families (`17/34/51/68/85 ×1e6`), anchor small seeds `42..47`, smoke offsets. `assert_disjoint()` checks every campaign base-range against every recorded range for interval overlap and raises `RuntimeError(f"seed overlap: {name} vs {other}")` on the first hit. (Anchor seeds 42–47 are tiny and never collide with the 1e6-scale bases, but assert them explicitly for the audit trail.)

```python
"""Campaign seed bases (base 19 x {1..5}) + hard disjointness assert (prereg
§2 [C1]). The runner calls assert_disjoint() and refuses to start on overlap."""
from __future__ import annotations

GEN_SEED_BASE = 19_000_000
ARM_R_SEED_BASE = 38_000_000
ARM_M_MUT_SEED = 57_000_000
ARM_M_SEL_SEED = 76_000_000
BOOT_SEED = 95_000_000
SPAN = 1_000_000

def _campaign_ranges() -> dict[str, tuple[int, int]]:
    return {n: (b, b + SPAN) for n, b in {
        "gen": GEN_SEED_BASE, "arm_r": ARM_R_SEED_BASE,
        "arm_m_mut": ARM_M_MUT_SEED, "arm_m_sel": ARM_M_SEL_SEED,
        "boot": BOOT_SEED}.items()}

RECORDED_STREAMS = {
    **{f"phaseC_b13_{i}": (b, b + SPAN) for i, b in enumerate(
        (13_000_000, 26_000_000, 39_000_000, 52_000_000, 65_000_000))},
    **{f"phaseCr2_b17_{i}": (b, b + SPAN) for i, b in enumerate(
        (17_000_000, 34_000_000, 51_000_000, 68_000_000, 85_000_000))},
    "anchor_small": (42, 48),   # streams 42..47 inclusive
    "smoke": (999_000_000, 999_100_000),
}

def _overlap(a, b):
    return a[0] < b[1] and b[0] < a[1]

def assert_disjoint() -> None:
    for name, rng in _campaign_ranges().items():
        for other, orng in RECORDED_STREAMS.items():
            if _overlap(rng, orng):
                raise RuntimeError(f"seed overlap: campaign {name}{rng} vs {other}{orng}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest experiments/rc2_campaign/test_seeds.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/rc2_campaign/seeds.py experiments/rc2_campaign/test_seeds.py
git commit -m "feat(rc2-campaign): seed bases + disjointness assert (Task 3)"
```

---

### Task 4: Guard stage orchestrator (`guard_stage.py`) [C2, C8]

**Files:**
- Create: `experiments/rc2_campaign/guard_stage.py`
- Test: `experiments/rc2_campaign/test_guard_stage.py`

**Interfaces:**
- Consumes: `metrics.guard_probe.{rollout_tactical, rush_share, tilt_p1_share, RUSH_SHARE, TILT_SHARE_REPRICED, RUSH_PLY_CAP}`, `experiments.rc2_archive.run_probe.eval_seed_for`.
- Produces:
  - `guard_pair_seeds(canon: str, n_pairs: int = 12) -> list[tuple[tuple[int,int],tuple[int,int]]]` — content-derived mirrored pairs (build decision: base seeds from `eval_seed_for`, mirrored structure from `pair_seeds`).
  - `run_guard_stage(game, canon: str, family: str, reach_draw_count: int, reach_n: int = 24, n_pairs: int = 12) -> dict` → `{passed: bool, rush_share, tilt_share, reach_share, decisive, vetoes: list[str]}`. `vetoes` names each failing guard (`"rush"`, `"tilt"`, `"reach"`); REACH-v3 only applies when `family == "threshold"`.

- [ ] **Step 1: Write the failing test** `test_guard_stage.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from experiments.rc2_campaign import guard_stage as gs


def test_pair_seeds_content_derived_and_mirrored():
    p = gs.guard_pair_seeds("a" * 64, n_pairs=12)
    assert len(p) == 12
    (a, b), (c, d) = p[0]
    assert (c, d) == (b, a)                    # mirrored
    assert gs.guard_pair_seeds("a" * 64) != gs.guard_pair_seeds("b" * 64)  # content


def test_reach_only_binds_threshold():
    # Non-threshold family: REACH never vetoes regardless of draw count.
    r = gs._verdict_from_shares(rush=0.30, tilt=0.50, reach_count=0,
                                reach_n=24, family="connection")
    assert "reach" not in r["vetoes"]
    # Threshold family with too few draws -> reach veto.
    r2 = gs._verdict_from_shares(rush=0.30, tilt=0.50, reach_count=4,
                                 reach_n=24, family="threshold")
    assert "reach" in r2["vetoes"] and r2["passed"] is False


def test_thresholds_applied():
    # rush below 0.25 -> rush veto; tilt below 0.625 -> tilt veto.
    r = gs._verdict_from_shares(rush=0.10, tilt=0.40, reach_count=10,
                                reach_n=24, family="threshold")
    assert set(r["vetoes"]) == {"rush", "tilt"}
    r_ok = gs._verdict_from_shares(rush=0.30, tilt=0.70, reach_count=6,
                                   reach_n=24, family="threshold")
    assert r_ok["passed"] is True and r_ok["vetoes"] == []
```

Note the guard semantics: RUSH **vetoes** when the rush share is *too high* (game is a rush) — a genome PASSES rush iff `rush_share < RUSH_SHARE`? **Verify against CAL-G before implementing** (see Step 3): in CAL-G the guards *fire* on degenerate games and firing = veto. RUSH fires (vetoes) when `share >= RUSH_SHARE`; TILT fires (vetoes) when `p1_share >= TILT_SHARE_REPRICED`; REACH-v3 fires (**keeps**, threshold-validity) when `draws >= 5/24`, so for threshold family a *veto* is `draws < 5`. Encode exactly this.

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest experiments/rc2_campaign/test_guard_stage.py -v`
Expected: FAIL (`No module named ...guard_stage`).

- [ ] **Step 3: Verify guard polarity, then implement.** Read `experiments/rc2_campaign/cal_g.py` (`evaluate()`, `_diag_from_shares`) and `cal_r.py` (`summarise`) to confirm: CAL-G targets S1 (RUSH fires), S4/S5 (TILT fires); controls stay silent. So "fires" = the guard's condition is met on a *bad* game. In the insertion pipeline a fired guard = **veto**. REACH-v3 is inverted: it's a *validity* guard for the threshold family — it fires (good) when `draws >= 5/24`, so a threshold genome with `draws < 5` is vetoed; non-threshold families are never REACH-vetoed. Implement:
  **Errata 2026-07-02 (BUILD_LOG #11):** the REACH sentence above is INVERTED — per §4/[C8]/CAL-R a fired REACH (draws ≥ 5/24, the S2-style draw pathology) VETOES a threshold genome exactly like RUSH/TILT, and draws < 5 passes; caught pre-data by the final whole-branch review and fixed fire→veto.

```python
"""Insertion guard stage (prereg §4 steps 4). RUSH/TILT from 12 mirrored
TacticalAgent pairs (n=24, content-derived seeds); REACH-v3 from the genome's
own T1 draw count (threshold family only). Fired guard = veto."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
from metrics.guard_probe import (  # noqa: E402
    rollout_tactical, rush_share, tilt_p1_share,
    RUSH_SHARE, TILT_SHARE_REPRICED,
)
from experiments.rc2_archive.run_probe import eval_seed_for  # noqa: E402

N_PAIRS = 12
REACH_FIRE_COUNT = 5      # >= 5/24 winner-None keeps a threshold genome


def guard_pair_seeds(canon, n_pairs=N_PAIRS):
    rng = np.random.default_rng(eval_seed_for(canon, 0) ^ 0x6EAC)  # guard-stage stream
    out = []
    for _ in range(n_pairs):
        a, b = (int(x) for x in rng.integers(1, 2**31 - 1, size=2))
        out.append(((a, b), (b, a)))
    return out


def _verdict_from_shares(rush, tilt, reach_count, reach_n, family):
    vetoes = []
    if not np.isnan(rush) and rush >= RUSH_SHARE:
        vetoes.append("rush")
    if not np.isnan(tilt) and tilt >= TILT_SHARE_REPRICED:
        vetoes.append("tilt")
    if family == "threshold" and reach_count < REACH_FIRE_COUNT:
        vetoes.append("reach")
    return dict(passed=not vetoes, rush_share=rush, tilt_share=tilt,
                reach_count=reach_count, family=family, vetoes=vetoes)


def run_guard_stage(game, canon, family, reach_draw_count, reach_n=24, n_pairs=N_PAIRS):
    records = []
    for (s1, s2), (s3, s4) in guard_pair_seeds(canon, n_pairs):
        for (p1, p2) in ((s1, s2), (s3, s4)):
            r = rollout_tactical(game, p1, p2)
            records.append(dict(winner=r["winner"], plies=r["plies"]))
    dec_r, rush = rush_share(records)
    dec_t, tilt = tilt_p1_share(records)
    out = _verdict_from_shares(rush, tilt, reach_draw_count, reach_n, family)
    out["decisive"] = dec_r
    return out
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest experiments/rc2_campaign/test_guard_stage.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/rc2_campaign/guard_stage.py experiments/rc2_campaign/test_guard_stage.py
git commit -m "feat(rc2-campaign): insertion guard stage (RUSH/TILT/REACH) (Task 4)"
```

---

### Task 5: Campaign archive with PG quality + full-conv ledger (`campaign_archive.py`) [C9]

**Files:**
- Create: `experiments/rc2_campaign/campaign_archive.py`
- Test: `experiments/rc2_campaign/test_campaign_archive.py`

**Interfaces:**
- Consumes: `evolution.qd_archive.{cell_key, validity as descriptor_validity, INTERACTION_EDGES, LENGTH_EDGES, bin_index}` (cell helpers reused verbatim); a `BatchResult` for the descriptor batch (import from `evolution.qd_archive`).
- Produces:
  - `@dataclass CampaignElite`: fields `game, canon, cell, descriptor_batch: BatchResult, t1_raw: float, t1_floored: float, full_conv: list[float]` (full-conv PG values per re-eval batch). Property `full_conv_mean_floored -> float` = `mean(max(v,0) for v in full_conv)` or `nan` if empty.
  - `class CampaignArchive`: `__init__(self)`; `seen`/`is_seen`/`mark_seen`; `offer(game, canon, cell, descriptor_batch, t1_raw, guard_fn) -> str` where `guard_fn(game, canon, family) -> dict` is the Task-4 stage (called only when the genome would enter — build decision #4); `reeval_full_conv(full_conv_fn)` appends one full-conv PG to every elite; `top_elites_by_full_conv(k)`; `coverage`; `qd_score` (Σ floored T1 over cells); `to_dict`/`from_dict`.
  - Outcome strings: `"invalid_<reason>"`, `"filled_empty_cell"`, `"lost_first_batch"`, `"replaced"`, `"guard_vetoed_<guard>"`.

- [ ] **Step 1: Write the failing test** `test_campaign_archive.py` (uses stub games + stub guard/full-conv fns, no engine):

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from evolution.qd_archive import BatchResult
from experiments.rc2_campaign.campaign_archive import CampaignArchive, CampaignElite


class StubWin:
    def __init__(self, ct="connection", mt=100):
        self.condition_type, self.max_turns = ct, mt

class StubGame:
    def __init__(self, ct="connection"):
        self.win_condition = StubWin(ct)
    def to_dict(self):
        return {"ct": self.win_condition.condition_type}

def desc_batch(interaction=0.1, length=40.0, n=20):
    # non-draw majority, length ok -> descriptor-valid
    return BatchResult(batch_n=n, dramas=[0.3] * n, draws=0,
                       interactions=[interaction] * n, lengths=[length] * n)

PASS_GUARD = lambda g, c, fam: {"passed": True, "vetoes": []}
VETO_GUARD = lambda g, c, fam: {"passed": False, "vetoes": ["rush"]}
FULL = lambda g, c: 0.2


def test_empty_cell_fills_when_guard_passes():
    a = CampaignArchive()
    out = a.offer(StubGame(), "c1", ("connection", 2, 2), desc_batch(), 0.30, PASS_GUARD)
    assert out == "filled_empty_cell" and a.coverage == 1


def test_guard_vetoes_first_occupancy():
    a = CampaignArchive()
    out = a.offer(StubGame(), "c1", ("connection", 2, 2), desc_batch(), 0.30, VETO_GUARD)
    assert out == "guard_vetoed_rush" and a.coverage == 0


def test_strict_improvement_only_and_floor():
    a = CampaignArchive()
    cell = ("connection", 2, 2)
    a.offer(StubGame(), "c1", cell, desc_batch(), 0.30, PASS_GUARD)
    # equal floored PG never displaces
    assert a.offer(StubGame(), "c2", cell, desc_batch(), 0.30, PASS_GUARD) == "lost_first_batch"
    # 0-vs-0 never displaces (both floor to 0)
    b = CampaignArchive()
    b.offer(StubGame(), "z1", cell, desc_batch(), -0.1, PASS_GUARD)   # floored 0 -> fills empty
    assert b.offer(StubGame(), "z2", cell, desc_batch(), -0.2, PASS_GUARD) == "lost_first_batch"
    # strictly better displaces (guard runs because it would enter)
    assert a.offer(StubGame(), "c3", cell, desc_batch(), 0.45, PASS_GUARD) == "replaced"


def test_descriptor_invalid_rejected_before_guard():
    a = CampaignArchive()
    bad = BatchResult(batch_n=20, dramas=[0.3] * 5, draws=15,  # draw majority
                      interactions=[0.1] * 20, lengths=[40.0] * 20)
    out = a.offer(StubGame(), "c1", ("connection", 2, 2), bad, 0.9, PASS_GUARD)
    assert out.startswith("invalid_")


def test_reeval_full_conv_ledger():
    a = CampaignArchive()
    a.offer(StubGame(), "c1", ("connection", 2, 2), desc_batch(), 0.30, PASS_GUARD)
    a.reeval_full_conv(FULL)
    a.reeval_full_conv(lambda g, c: -0.1)   # negative -> floors to 0 in mean
    elite = next(iter(a.cells.values()))
    assert elite.full_conv == [0.2, -0.1]
    assert abs(elite.full_conv_mean_floored - 0.1) < 1e-12   # mean(0.2, 0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest experiments/rc2_campaign/test_campaign_archive.py -v`
Expected: FAIL (`No module named ...campaign_archive`).

- [ ] **Step 3: Implement `campaign_archive.py`.** Reuse `cell_key`/`validity`/`bin_index` from `qd_archive`; the caller passes the pre-computed `cell` (from `cell_key(game, descriptor_batch)`) and the descriptor batch (for the validity guard on the *descriptor* — but per build decision #2 the binding validity is the T1 guard, applied by the caller before `offer`; here `offer` re-checks descriptor validity only as the coverage guard for cell occupancy). Order inside `offer`: descriptor validity → floored-PG strict-improvement test (skip guard on a sure loss) → guard stage (only if it would enter) → insert.

```python
"""Campaign MAP-Elites archive: cells stay descriptor-based (qd_archive
verbatim), displacement key = floored T1-PG, elites carry a separate
full-conv PG ledger (prereg §3 [C9]). Guard stage runs only for genomes
that would enter (BUILD_LOG decision 4)."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from evolution.qd_archive import BatchResult, validity as descriptor_validity


@dataclass
class CampaignElite:
    game: object
    canon: str
    cell: tuple
    descriptor_batch: BatchResult
    t1_raw: float
    t1_floored: float
    full_conv: list = field(default_factory=list)

    @property
    def full_conv_mean_floored(self) -> float:
        if not self.full_conv:
            return float("nan")
        return float(np.mean([max(v, 0.0) for v in self.full_conv]))


class CampaignArchive:
    def __init__(self):
        self.cells: dict[tuple, CampaignElite] = {}
        self.seen: set[str] = set()
        self.counters: dict[str, int] = {}

    def _bump(self, key):
        self.counters[key] = self.counters.get(key, 0) + 1

    def is_seen(self, canon): return canon in self.seen
    def mark_seen(self, canon): self.seen.add(canon)

    def offer(self, game, canon, cell, descriptor_batch, t1_raw, guard_fn) -> str:
        self._bump("offered")
        reason = descriptor_validity(descriptor_batch)
        if reason is not None:
            self._bump(f"invalid_{reason}")
            return f"invalid_{reason}"
        floored = max(t1_raw, 0.0)
        incumbent = self.cells.get(cell)
        if incumbent is not None and floored <= incumbent.t1_floored:
            self._bump("lost_first_batch")
            return "lost_first_batch"
        # Would enter -> run the guard stage (decision 4).
        family = game.win_condition.condition_type
        guard = guard_fn(game, canon, family)
        if not guard["passed"]:
            g = guard["vetoes"][0]
            self._bump(f"guard_vetoed_{g}")
            return f"guard_vetoed_{g}"
        elite = CampaignElite(game=game, canon=canon, cell=cell,
                              descriptor_batch=descriptor_batch,
                              t1_raw=t1_raw, t1_floored=floored)
        self.cells[cell] = elite
        self._bump("replaced" if incumbent is not None else "filled_empty_cell")
        return "replaced" if incumbent is not None else "filled_empty_cell"

    def reeval_full_conv(self, full_conv_fn) -> None:
        for cell in sorted(self.cells):
            e = self.cells[cell]
            e.full_conv.append(full_conv_fn(e.game, e.canon))

    def top_elites_by_full_conv(self, k):
        rated = [e for e in self.cells.values() if e.full_conv]
        return sorted(rated, key=lambda e: e.full_conv_mean_floored, reverse=True)[:k]

    @property
    def coverage(self): return len(self.cells)

    @property
    def qd_score(self): return float(sum(e.t1_floored for e in self.cells.values()))

    def to_dict(self):
        return {"seen": sorted(self.seen), "counters": dict(self.counters),
                "cells": [{"cell": list(e.cell), "canon": e.canon,
                           "game": e.game.to_dict(),
                           "descriptor_batch": e.descriptor_batch.to_dict(),
                           "t1_raw": e.t1_raw, "t1_floored": e.t1_floored,
                           "full_conv": list(e.full_conv)}
                          for e in self.cells.values()]}

    @classmethod
    def from_dict(cls, d, game_from_dict):
        a = cls(); a.seen = set(d["seen"]); a.counters = dict(d["counters"])
        for entry in d["cells"]:
            cell = tuple(entry["cell"])
            a.cells[cell] = CampaignElite(
                game=game_from_dict(entry["game"]), canon=entry["canon"], cell=cell,
                descriptor_batch=BatchResult.from_dict(entry["descriptor_batch"]),
                t1_raw=entry["t1_raw"], t1_floored=entry["t1_floored"],
                full_conv=list(entry["full_conv"]))
        return a
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest experiments/rc2_campaign/test_campaign_archive.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/rc2_campaign/campaign_archive.py experiments/rc2_campaign/test_campaign_archive.py
git commit -m "feat(rc2-campaign): PG-quality archive + full-conv ledger (Task 5)"
```

---

### Task 6: Bars + pure `decide_verdict` (`bars.py`) [C3, C4, C6, C7, C12]

**Files:**
- Create: `experiments/rc2_campaign/bars.py`
- Test: `experiments/rc2_campaign/test_bars.py`

**Interfaces:**
- Produces (all pure, no I/O):
  - Constants: `CAL_I_THRESHOLD=0.431`, `BAR_W_FLOOR=0.167`, `BAR_H_FLOOR=0.05`, `SATURATION_R_TOP10=0.40`, `SATURATION_M_WIN_FRAC=0.60`, `SATURATION_MIN_JOINT=20`, `SGO1_BAR=4.10`, `SGO2_SEP=0.4`, `MIN_CONTRAST=0.15`, `D4015_BAND=(3.48, 4.18)`.
  - `bar_w(family_floored_pgs: dict[str, list[float]], min_valid=20) -> dict` → `{qualifying: list[str], live: dict[str,bool], n_qualifying, n_live, verdict}` where verdict ∈ `{"PASS", "ARCHIVE_KILL", "PROBE_INCOMPLETE"}` (P90−P10 of floored T1-PG ≥ floor → LIVE; ≥2 qualifying, ≥2 LIVE → PASS; <2 qualifying → PROBE_INCOMPLETE; else ARCHIVE_KILL).
  - `bar_h(top10_m, top10_r, m_elites, r_elites, joint_cells=None) -> dict` → `{verdict, metric, detail}`; verdict ∈ `{"PASS","SEARCH_NEUTRAL","PROBE_INCOMPLETE"}`; applies the saturation switch when `top10_r >= 0.40`.
  - `slate_bars(team_scores: dict[str, list[float]], top3_ids, contrast_ids, full_pg: dict[str,float], d4015_score) -> dict` → `{sgo1, sgo2, separation_state, campaign_valid, verdict}` with verdict ∈ `{"GO","GO-PARTIAL","NO-GO","CAMPAIGN_UNRESOLVED","SEPARATION_UNDERDETERMINED"}`.
  - `decide_verdict(*, cal_i_pass, incomplete, bar_w_verdict, bar_h_verdict, slate_verdict) -> str` — the §9 precedence chain, evaluated strictly in order, exactly one token out.

- [ ] **Step 1: Write the failing test** `test_bars.py` — exercise **every branch** of `decide_verdict` and each bar's boundaries (this is the "ALL branches synthetically tested pre-run" obligation, §10):

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from experiments.rc2_campaign import bars as B


def test_decide_verdict_precedence_all_branches():
    d = B.decide_verdict
    assert d(cal_i_pass=False, incomplete=None, bar_w_verdict="PASS",
             bar_h_verdict="PASS", slate_verdict="GO") == "PROBE_INVALID"
    assert d(cal_i_pass=True, incomplete="wall_cap", bar_w_verdict="PASS",
             bar_h_verdict="PASS", slate_verdict="GO") == "PROBE_INCOMPLETE"
    assert d(cal_i_pass=True, incomplete=None, bar_w_verdict="ARCHIVE_KILL",
             bar_h_verdict="PASS", slate_verdict="GO") == "ARCHIVE_KILL"
    assert d(cal_i_pass=True, incomplete=None, bar_w_verdict="PROBE_INCOMPLETE",
             bar_h_verdict="PASS", slate_verdict="GO") == "PROBE_INCOMPLETE"
    assert d(cal_i_pass=True, incomplete=None, bar_w_verdict="PASS",
             bar_h_verdict="SEARCH_NEUTRAL", slate_verdict=None) == "SEARCH_NEUTRAL"
    assert d(cal_i_pass=True, incomplete=None, bar_w_verdict="PASS",
             bar_h_verdict="PROBE_INCOMPLETE", slate_verdict=None) == "PROBE_INCOMPLETE"
    for sv in ("GO", "GO-PARTIAL", "NO-GO", "CAMPAIGN_UNRESOLVED", "SLATE_INCOMPLETE"):
        assert d(cal_i_pass=True, incomplete=None, bar_w_verdict="PASS",
                 bar_h_verdict="PASS", slate_verdict=sv) == sv


def test_bar_w_quantifier():
    live = {f"F{i}": [0.0, 0.30] for i in range(2)}    # spread 0.30 >= floor -> LIVE
    dead = {"D": [0.10, 0.12]}                          # spread ~0 -> DEAD
    small = {"S": [0.0] * 5}                            # < 20 -> not qualifying
    fams = {**{k: v * 15 for k, v in live.items()}, "D": dead["D"] * 20, "S": small["S"]}
    r = B.bar_w(fams)
    assert r["n_qualifying"] == 3 and r["n_live"] == 2 and r["verdict"] == "PASS"
    r2 = B.bar_w({"D": dead["D"] * 20})
    assert r2["verdict"] == "PROBE_INCOMPLETE"          # <2 qualifying
    r3 = B.bar_w({"D": dead["D"] * 20, "E": dead["D"] * 20})
    assert r3["verdict"] == "ARCHIVE_KILL"              # 2 qualifying, 0 live


def test_bar_h_normal_and_saturation():
    assert B.bar_h(0.30, 0.20, 12, 12)["verdict"] == "PASS"        # gap 0.10 >= 0.05
    assert B.bar_h(0.22, 0.20, 12, 12)["verdict"] == "SEARCH_NEUTRAL"  # gap 0.02
    assert B.bar_h(0.30, 0.20, 8, 12)["verdict"] == "PROBE_INCOMPLETE" # <10 elites
    # saturation: R_top10 >= 0.40 -> switch to per-cell wins
    sat = B.bar_h(0.55, 0.45, 12, 12, joint_cells=[True] * 13 + [False] * 8)
    assert sat["metric"] == "per_cell_wins"
    assert sat["verdict"] in ("PASS", "SEARCH_NEUTRAL")            # 13/21 -> ~0.62 >= 0.60 PASS
    assert B.bar_h(0.55, 0.45, 12, 12, joint_cells=[True] * 10)["verdict"] == "PROBE_INCOMPLETE"


def test_slate_bars():
    # top-3 mean high, contrast low, separation clear, d4015 in band -> GO
    ts = {"m1": [4.2, 4.1, 4.3], "m2": [3.9]*3, "m3": [3.8]*3,
          "c1": [3.4]*3, "c2": [3.3]*3}
    full = {"m1": 0.4, "m2": 0.35, "m3": 0.3, "c1": 0.1, "c2": 0.05}
    r = B.slate_bars(ts, ["m1", "m2", "m3"], ["c1", "c2"], full, d4015_score=3.9)
    assert r["verdict"] == "GO"
    # min-contrast too small -> SEPARATION_UNDERDETERMINED -> GO-PARTIAL if sgo1 & band
    full2 = {"m1": 0.4, "m2": 0.35, "m3": 0.3, "c1": 0.28, "c2": 0.27}  # min-max < 0.15
    r2 = B.slate_bars(ts, ["m1", "m2", "m3"], ["c1", "c2"], full2, d4015_score=3.9)
    assert r2["separation_state"] == "SEPARATION_UNDERDETERMINED"
    assert r2["verdict"] == "GO-PARTIAL"
    # d4015 out of band -> CAMPAIGN_UNRESOLVED regardless
    r3 = B.slate_bars(ts, ["m1", "m2", "m3"], ["c1", "c2"], full, d4015_score=4.9)
    assert r3["verdict"] == "CAMPAIGN_UNRESOLVED"
    # sgo1 fails (no top-3 reaches 4.10) -> NO-GO
    ts_low = {k: [3.5]*3 for k in ts}
    r4 = B.slate_bars(ts_low, ["m1", "m2", "m3"], ["c1", "c2"], full, d4015_score=3.9)
    assert r4["verdict"] == "NO-GO"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest experiments/rc2_campaign/test_bars.py -v`
Expected: FAIL (`No module named ...bars`).

- [ ] **Step 3: Implement `bars.py`** transcribing the constants and the §6/§9 logic. Key details: P90/P10 via `np.percentile(vals, [90, 10])`; per-game team score = mean of the 3 team verdicts; S-GO-2 pools the top-3 verdicts (9 values) minus the contrast-2 pool (6 values); the min-contrast precondition compares `min(full_pg over top pool) - max(full_pg over contrast pool)`.

```python
"""Pure bars + precedence-chain verdict (prereg §6/§9). Constants are §0-final;
transcribed as data, synthetically branch-tested before any campaign data."""
from __future__ import annotations
import numpy as np

CAL_I_THRESHOLD = 0.431
BAR_W_FLOOR = 0.167
BAR_H_FLOOR = 0.05
SATURATION_R_TOP10 = 0.40
SATURATION_M_WIN_FRAC = 0.60
SATURATION_MIN_JOINT = 20
SGO1_BAR = 4.10
SGO2_SEP = 0.4
MIN_CONTRAST = 0.15
D4015_BAND = (3.48, 4.18)


def bar_w(family_floored_pgs, min_valid=20):
    qualifying = [f for f, v in family_floored_pgs.items() if len(v) >= min_valid]
    live = {}
    for f in qualifying:
        p90, p10 = np.percentile(family_floored_pgs[f], [90, 10])
        live[f] = (p90 - p10) >= BAR_W_FLOOR
    n_q, n_l = len(qualifying), sum(live.values())
    if n_q < 2:
        verdict = "PROBE_INCOMPLETE"
    elif n_l < 2:
        verdict = "ARCHIVE_KILL"
    else:
        verdict = "PASS"
    return dict(qualifying=qualifying, live=live, n_qualifying=n_q,
                n_live=n_l, verdict=verdict)


def bar_h(top10_m, top10_r, m_elites, r_elites, joint_cells=None):
    if m_elites < 10 or r_elites < 10:
        return dict(verdict="PROBE_INCOMPLETE", metric="top10_gap",
                    detail="archive < 10 elites")
    if top10_r >= SATURATION_R_TOP10:
        if joint_cells is None or len(joint_cells) < SATURATION_MIN_JOINT:
            return dict(verdict="PROBE_INCOMPLETE", metric="per_cell_wins",
                        detail="< 20 joint cells")
        frac = sum(1 for w in joint_cells if w) / len(joint_cells)
        return dict(verdict="PASS" if frac >= SATURATION_M_WIN_FRAC else "SEARCH_NEUTRAL",
                    metric="per_cell_wins", detail=f"M-win frac {frac:.3f}")
    gap = top10_m - top10_r
    return dict(verdict="PASS" if gap >= BAR_H_FLOOR else "SEARCH_NEUTRAL",
                metric="top10_gap", detail=f"gap {gap:+.3f}")


def slate_bars(team_scores, top3_ids, contrast_ids, full_pg, d4015_score):
    def pool(ids):
        return [v for i in ids for v in team_scores[i]]
    per_game = {i: float(np.mean(v)) for i, v in team_scores.items()}
    sgo1 = any(per_game[i] >= SGO1_BAR for i in top3_ids)
    top_pool, contrast_pool = pool(top3_ids), pool(contrast_ids)
    sep = float(np.mean(top_pool)) - float(np.mean(contrast_pool))
    min_contrast = min(full_pg[i] for i in top3_ids) - max(full_pg[i] for i in contrast_ids)
    if min_contrast < MIN_CONTRAST:
        sep_state = "SEPARATION_UNDERDETERMINED"
    else:
        sep_state = "OK"
    campaign_valid = D4015_BAND[0] <= d4015_score <= D4015_BAND[1]
    if not campaign_valid:
        verdict = "CAMPAIGN_UNRESOLVED"
    elif not sgo1:
        verdict = "NO-GO"
    elif sep_state == "SEPARATION_UNDERDETERMINED":
        verdict = "GO-PARTIAL"
    elif sep >= SGO2_SEP:
        verdict = "GO"
    else:
        verdict = "NO-GO"
    return dict(sgo1=sgo1, sgo2=sep, separation_state=sep_state,
                campaign_valid=campaign_valid, verdict=verdict)


def decide_verdict(*, cal_i_pass, incomplete, bar_w_verdict, bar_h_verdict, slate_verdict):
    if not cal_i_pass:
        return "PROBE_INVALID"
    if incomplete is not None:
        return "PROBE_INCOMPLETE"
    if bar_w_verdict == "PROBE_INCOMPLETE":
        return "PROBE_INCOMPLETE"
    if bar_w_verdict == "ARCHIVE_KILL":
        return "ARCHIVE_KILL"
    if bar_h_verdict == "PROBE_INCOMPLETE":
        return "PROBE_INCOMPLETE"
    if bar_h_verdict == "SEARCH_NEUTRAL":
        return "SEARCH_NEUTRAL"
    return slate_verdict   # GO / GO-PARTIAL / NO-GO / CAMPAIGN_UNRESOLVED / SLATE_INCOMPLETE
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest experiments/rc2_campaign/test_bars.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/rc2_campaign/bars.py experiments/rc2_campaign/test_bars.py
git commit -m "feat(rc2-campaign): pure bars + decide_verdict, all branches tested (Task 6)"
```

---

### Task 7: Campaign runner (`run_campaign.py`) — stage machine

**Files:**
- Create: `experiments/rc2_campaign/run_campaign.py`
- Test: extends `test_campaign_archive.py` or a new `test_run_campaign_smoke.py` (smoke only — real runs are hours)

**Interfaces:**
- Consumes: everything above + `config.{GameConfig, EvolutionConfig}`, `game_engine.generator_v2.GameGeneratorV2`, `evolution.operators_v2.MutationOperatorV2`, `metrics.rollout_traces.run_protocol`, `metrics.descriptors.{obs_drama_for_rollout, interaction_rate_for_rollout}`, `evolution.qd_archive.{BatchResult, cell_key}`.
- Produces: a `--smoke` end-to-end pass writing `experiments/rc2_campaign/smoke/` outputs and NO verdict token; `--resume`; checkpoint every 25 evals + stage boundaries.

This task **forks `experiments/rc2_archive/run_probe.py`** (the stage machine, `Probe` class, `run_stage0`, `draw_candidate_R/M`, `run_arm`, `save_checkpoint`/`load_checkpoint`, `main`). Change list (apply as edits to the fork, keep structure/logging verbatim where unchanged):

- [ ] **Step 1: Fork the file** — copy `rc2_archive/run_probe.py` to `experiments/rc2_campaign/run_campaign.py`; swap constants to the Global Constraints values (`GEN_SEED_BASE=19_000_000` etc. from `seeds.py`; `B_ARM=600`; `REEVAL_AT=(150,300,450,600)`; `BAR_W_MIN_VALID=20`; `STAGE0_MIN_TOTAL_VALID=150`; `STAGE0_MAX_EVALS=240`; `STAGE0_MAX_ATTEMPTS=3000`). Import `assert_disjoint` and call it first in `main()`.

- [ ] **Step 2: Add the simultaneous-move exclusion** to the candidate-draw path — after `gen.generate_game(...)`, reject (counted `sim_excluded`) any genome whose `game.turn_structure.turn_type == "simultaneous"`, before `quick_reject`. (Registered §2 exclusion; ~30% of space; report the count.)

- [ ] **Step 3: Replace the per-genome evaluation** so each evaluated genome produces both a descriptor batch and a T1 batch:

```python
def eval_genome(self, game, canon, batch_index=0):
    # descriptor batch (Phase C: cell + reported drama)
    seed = eval_seed_for(canon, batch_index)
    rollouts = run_protocol(game, self.descriptor_n, seed)
    topo = game.get_topology()
    dramas, draws, inter, lengths = [], 0, [], []
    for r in rollouts:
        d = obs_drama_for_rollout(game, topo, r)
        (dramas.append(float(d)) if d is not None else None) or (draws := draws)
        if d is None: draws += 1
        inter.append(interaction_rate_for_rollout(topo, r)); lengths.append(float(r["game_length"]))
    dbatch = BatchResult(self.descriptor_n, dramas, draws, inter, lengths)
    cell = cell_key(game, dbatch)
    # T1 PG batch (quality + validity + REACH draws)
    t1 = pg_batch(game, canon, batch_index)   # Task 2
    return dbatch, cell, t1
```

Wire the T1 validity guard (build decision #2): a genome with `t1["non_draw_share"] < 0.5` or `t1["mean_length"] < 6` or `isnan(t1["raw_pg"])` is counted invalid and NOT offered. Otherwise call `archive.offer(game, canon, cell, dbatch, t1["raw_pg"], guard_fn)` where `guard_fn` closes over `run_guard_stage(game, canon, family, reach_draw_count=t1["draws"])`. Set `self.descriptor_n` = `N_STAGE1 = 50` for arms and `N_STAGE0 = 100` for Stage 0 (Phase C batch sizes).

- [ ] **Step 4: Point re-eval at the full-conv ledger** — replace `arch.reeval_all(...)` with `arch.reeval_full_conv(lambda g, c: pg_batch(g, c, batch_index=<checkpoint_idx>, deep_sims=256, shallow_sims=16, n=48)["raw_pg"])`. Ensure an elite lacking a full-conv batch at bar time gets one before bars are computed (§3).

- [ ] **Step 5: Replace the verdict + reporting** — compute `family_floored_pgs` from Stage-0 valid genomes, call `bars.bar_w`; after arms, `bars.bar_h`; assemble the final `decide_verdict(...)` inputs (slate is a later manual stage, so `run_campaign.py` stops at "slate-ready" and writes the BAR W/H verdicts + the pre-slate token, emitting `SLATE_PENDING` when W∧H pass). Write `campaign_results.md` (CAL / BAR W table / BAR H table / counters / pre-slate verdict) and per-arm CSV logs, mirroring `write_reports`.

- [ ] **Step 6: Smoke test** — write `test_run_campaign_smoke.py` that runs `main(["--smoke"])` on a tiny budget (monkeypatch `B_ARM=4`, `STAGE0_MAX_EVALS=6`, `descriptor_n=6`, T1 `n=4`, sims 16/4) over a disjoint smoke seed base and asserts: it completes, writes `smoke/campaign_results.md`, emits no verdict token, and the archive has ≥1 elite. Keep it under ~2 min.

Run: `.venv/bin/python -m pytest experiments/rc2_campaign/test_run_campaign_smoke.py -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add experiments/rc2_campaign/run_campaign.py experiments/rc2_campaign/test_run_campaign_smoke.py
git commit -m "feat(rc2-campaign): runner stage machine (Stage0 + arms + re-eval) (Task 7)"
```

---

### Task 8: Pre-campaign CAL-I (`cal_i.py`) [§5]

**Files:**
- Create: `experiments/rc2_campaign/cal_i.py`

**Interfaces:**
- Consumes: `anchor_calibration.play_cell` (roster anchors, streams 46/47, T1 config 128v16 n=24). Produces `CAL_I.md`/`.json`: `PG(d4015) − PG(S4) ≥ 0.431` on fresh streams 46/47 → PASS/`PROBE_INVALID`.

- [ ] **Step 1: Write it** as a driver mirroring `cal_r.py`'s structure (`ProcessPoolExecutor`, `STREAMS=(46,47)`, `play_cell(k, stream, idx, deep_sims=128, shallow_sims=16, games_per_stream=12)`), computing `pg(d4015) − pg(S4)`, comparing to `bars.CAL_I_THRESHOLD`, writing verdict `PASS`/`FAIL`. Include an `--from-cache` path for re-derivation.

- [ ] **Step 2: Dry-run on 2 streams × few idx** to confirm it wires (do not treat as the binding measurement — that runs pre-campaign). Commit.

```bash
git add experiments/rc2_campaign/cal_i.py
git commit -m "feat(rc2-campaign): pre-campaign CAL-I instrument check (Task 8)"
```

---

### Task 9: Pre-campaign CAL-C (`cal_c.py`) [§5]

**Files:**
- Create: `experiments/rc2_campaign/cal_c.py`

**Interfaces:**
- Times 20 fresh genomes (CAL stream, disjoint) through the FULL per-genome pipeline — descriptor batch + T1 eval + one guard stage + one full-conv re-eval — and projects campaign wall for B=600×2 + Stage-0 240 over 7 workers. Output `CAL_C.md`/`.json` with the projection vs the 8 h cap; over-cap → flags re-scope (never silent).

- [ ] **Step 1: Write it** reusing `run_campaign.eval_genome`, `run_guard_stage`, and a single `pg_batch(..., 256, 16, 48)`; sum wall, extrapolate, compare to `8*3600`. Commit.

```bash
git add experiments/rc2_campaign/cal_c.py
git commit -m "feat(rc2-campaign): pre-campaign CAL-C cost projection (Task 9)"
```

---

### Task 10: Slate builder (`slate.py`) [C6, C10]

**Files:**
- Create: `experiments/rc2_campaign/slate.py`
- Test: `experiments/rc2_campaign/test_slate.py`

**Interfaces:**
- Produces `build_slate(m_elites: list[CampaignElite], d4015, s3, near_dup_floor: float) -> dict` → `{games: list, substitutions: list[str], family_composition}`. Composition: top-3 M by full-conv PG + 2 contrast (guard-passing M elites from the lowest full-conv-PG tertile) + d4015 + S3 (carry-in, non-binding). Constraints applied in PG order with next-best substitution (all logged): (1) family cap — max 2 of the top-3 per win-condition family; (2) near-duplicate screen — skip a candidate iff identical family + identical board/topology + `descriptor_row` distance below `near_dup_floor`, or rules-diff limited to komi/max_turns. Ties broken lexicographically on `canonical_hash`.

- [ ] **Step 1: Write the failing test** with stub elites (id, family, full_conv_mean_floored, descriptor_row vector) covering: top-3 selection by PG desc; family-cap substitution (3rd same-family candidate skipped, logged); near-dup substitution; contrast = lowest tertile; d4015+S3 appended; total 7 games. Include the exhaustion fallback (when only 2 families hold elites, the cap can't bind — documented in `PANEL_FINDINGS.md:352` — assert it degrades gracefully rather than erroring).

- [ ] **Step 2–4: Implement, run, verify.** Reuse `metrics.descriptors.descriptor_row` for the near-dup distance.

- [ ] **Step 5: Commit**

```bash
git add experiments/rc2_campaign/slate.py experiments/rc2_campaign/test_slate.py
git commit -m "feat(rc2-campaign): slate builder + substitution log (Task 10)"
```

---

### Task 11: Blind-pack generator (`build_blind_pack.py`) + verdict grep (`grep_verdicts.py`) [C11, C15]

**Files:**
- Create: `experiments/rc2_campaign/build_blind_pack.py`, `experiments/rc2_campaign/grep_verdicts.py`
- Test: `experiments/rc2_campaign/test_blind_pack.py`

**Interfaces:**
- `build_blind_pack.py`: fork `experiments/frontline/build_blind_pack.py` — widen `LABELS` 3→7 (`A..G`), swap the inline siege `PLAY_PY` for the multi-dim `describe_rules`/`decode`/`print_legal`/`render_board` engine from `evaluations/rc2_phase_d/play.py`, keep `replace_exact` count-asserted substitution, the sealed shuffle seed (`--seed` required, no default), per-team `team_orders`, the fairness-perception probe, cross-game comparison, and role win-split logging. Add the mandatory **recognition-disclosure line** to each verdict template ("if you believe you can identify this game or recall a prior score, say so and continue"). Register the out-of-bounds list from prereg §7 in the BRIEFING.
- `grep_verdicts.py`: `scan_verdicts(pack_dir) -> list[tuple[str,str,str]]` greps filed verdict files for identifier strings (`d4015`, `Connection Go`, `S3`, `run8`, …) **carving out** the compliant "R8"/"run8"-in-anchor-line false positives (`PANEL_FINDINGS.md:406`); returns `(file, identifier, line)` hits. The orchestrator runs this before unblinding.

- [ ] **Step 1: Write the failing test** — build a dry-run pack from 7 stub games; assert: 7 label files + 7×N verdict templates + sealed `.blind_mapping.json` (with `label_seed`), the recognition line present in every template, the out-of-bounds list present in the BRIEFING, action-id lines regenerated from each game's geometry, and `grep_verdicts.scan_verdicts` flags a planted "d4015" but not a compliant "R8 4.10" anchor line.

- [ ] **Step 2–4: Implement, run, verify** (use `--dry-run` so no real slate games are needed).

- [ ] **Step 5: Commit**

```bash
git add experiments/rc2_campaign/build_blind_pack.py experiments/rc2_campaign/grep_verdicts.py experiments/rc2_campaign/test_blind_pack.py
git commit -m "feat(rc2-campaign): 7-label blind-pack generator + verdict grep (Task 11)"
```

---

### Task 12: Full suite green + integration dry-run

**Files:** none new.

- [ ] **Step 1: Run the whole campaign test suite**

Run: `.venv/bin/python -m pytest experiments/rc2_campaign/ -v`
Expected: all PASS.

- [ ] **Step 2: Run the runner smoke end-to-end** (`--smoke`) and eyeball `smoke/campaign_results.md` — confirm Stage-0 table, both arms hit budget, re-eval populated the full-conv ledger, no verdict token emitted.

- [ ] **Step 3: Regression-check reused modules** — `.venv/bin/python -m pytest test_rc2_descriptor_v2.py test_rc2_archive.py experiments/rc2_campaign/test_noise_null.py -v` (the guard-lift back-compat + untouched machinery).

- [ ] **Step 4: Commit any fixes; write a short `README_BUILD.md`** in `experiments/rc2_campaign/` documenting the run order: CAL-I → CAL-C → (owner go) → `run_campaign.py` → slate build → blind pack → 3 tmux teams → `grep_verdicts` → unblind → `decide_verdict`.

```bash
git add experiments/rc2_campaign/README_BUILD.md
git commit -m "docs(rc2-campaign): build complete — run order + suite green (Task 12)"
```

---

## Self-review

**Spec coverage** (prereg §-by-§): §0 constants → Global Constraints + `bars.py`/`guard_stage.py`/`pg_eval.py` (✓). §2 search space/Stage-0/arms/seeds/sim-exclusion → Task 3 (seeds), Task 7 steps 1–2 (✓). §3 two ledgers + floored quality → Task 5 (✓). §4 insertion pipeline (quick_reject → T1 → validity → guard → insert) → Task 7 step 3 + Task 4 + Task 5 (✓). §5 CAL-I/CAL-C → Tasks 8–9 (✓). §6 bars → Task 6 (✓). §7 slate + blinding → Tasks 10–11 (✓). §9 precedence chain → Task 6 `decide_verdict` (✓). §10 build obligations (guard lift, two-ledger store, slate builder+log, blind-pack gen, disjointness assert, pure decide_verdict all-branches-tested) → Tasks 1, 5, 10, 11, 3, 6 (✓).

**Placeholder scan:** the only `...` placeholders are (a) the verbatim `rollout_tactical` body in Task 1 Step 3 (explicitly "copy exact from source line 201-237") and (b) the `guard_pair_seeds` XOR salt — both are precise instructions, not TBDs. Task 7's fork uses a walrus in the drama loop (`(dramas.append(...)) or (draws := draws)`) that is ugly — the implementer should write the plain `if d is None: draws += 1 else: dramas.append(float(d))` form shown just below it; flagged here to fix on implementation.

**Type consistency:** `t1["raw_pg"]`/`floored_pg`/`draws`/`non_draw_share`/`mean_length` (Task 2) are consumed identically in Tasks 5 and 7; `guard_fn(game, canon, family) -> {"passed", "vetoes"}` matches between Task 4 (`run_guard_stage`) and Task 5 (`offer`); `CampaignElite.full_conv_mean_floored` (Task 5) feeds `bar_h`/slate (Tasks 6, 10); `decide_verdict` token set matches §9 exactly.

**Open items for the owner (pre-data, Task 0):** ratify the 7 build decisions — especially #1 (descriptor batch retained for cells) and #4 (guard gates first occupancy), which have methodological weight.
