"""RC2 Phase C archive-integration probe runner.

Implements experiments/rc2_archive/PREREGISTRATION.md (the locked contract):
CAL instrument gate (573/e1453 drama gap at n=100), Stage 0 fresh-sample
within-family bar (BAR W), Stage 1 matched-budget two-arm search (random vs
MAP-Elites, BAR H on top-10 pooled dramas), and the locked decision grammar
(PROBE_INVALID / ARCHIVE_KILL / ARCHIVE_GO / ARCHIVE_NEUTRAL /
PROBE_INCOMPLETE).

metrics/descriptors.py and metrics/rollout_traces.py are LOCKED: per-rollout
values are assembled here from their public functions and cross-checked
against descriptor_row on the first Stage-0 genome (exact-equality assert,
the Phase B pattern).

Usage:
    .venv/bin/python experiments/rc2_archive/run_probe.py [--smoke]
        [--resume] [--out DIR]

--smoke runs a miniature end-to-end pass on seed streams DISJOINT from the
probe streams (registered: smoke drama values do not inform bars), ignores
the early-exit gates so every code path is exercised, and never emits a
verdict token.

Checkpoints: written every 25 genome-evals and at stage boundaries;
--resume continues from the last checkpoint.
"""
from __future__ import annotations

import argparse
import csv
import json
import signal
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import EvolutionConfig, GameConfig  # noqa: E402
from evolution.operators_v2 import MutationOperatorV2  # noqa: E402
from evolution.qd_archive import (  # noqa: E402
    BatchResult,
    QDArchive,
    validity,
)
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from game_engine.generator_v2 import GameGeneratorV2  # noqa: E402
from metrics.descriptors import (  # noqa: E402
    descriptor_row,
    interaction_rate_for_rollout,
    obs_drama_for_rollout,
)
from metrics.rollout_traces import run_protocol  # noqa: E402
from experiments.rc2_anchor.run_probe import load_game_from_db  # noqa: E402

# ---------------------------------------------------------------------------
# Pre-registered constants — experiments/rc2_archive/PREREGISTRATION.md.
# Transcribed as data; not altered after data.
# ---------------------------------------------------------------------------
BASE_SEED = 13
STAGE0_GEN_SEED_BASE = 13_000_000   # Stage-0 attempt i -> seed base + i
ARM_R_GEN_SEED_BASE = 26_000_000    # arm-R attempt j -> seed base + j
ARM_M_MUT_SEED = 39_000_000         # arm-M mutation rng
ARM_M_SEL_SEED = 52_000_000         # arm-M cell-selection rng
BOOT_SEED = 65_000_000              # bootstrap rng (reports only)

N_STAGE0 = 100                      # CAL + Stage-0 batch size
N_STAGE1 = 50                       # all Stage-1 batches
B_ARM = 300                         # genome-evals per arm
REEVAL_AT = (100, 200, 300)         # full-archive re-eval after these evals

CAL_FLOOR = 0.15                    # drama(573) - drama(e1453) >= 0.15
BAR_W_SPREAD_FLOOR = 0.064          # = 3 x hw(100); hw(n) = 0.015*sqrt(200/n)
BAR_W_MIN_VALID = 15                # genomes for a family to be SAMPLED
STAGE0_MIN_TOTAL_VALID = 120
STAGE0_MAX_EVALS = 160
STAGE0_MAX_ATTEMPTS = 2000
BAR_H_FLOOR = 0.03                  # = hw(50)
TOP_K = 10

EVAL_TIMEOUT_S = 180
WALL_CAP_S = 10 * 3600
REDRAW_CAP = 50                     # per-step candidate re-draws
# Registered semantics: a step whose 50 re-draws all fail is SKIPPED
# (counted, no budget) and the arm continues to its full B. There is no
# stall guard beyond the registered 10h wall cap (review 2026-06-11: an
# unregistered consecutive-skip terminator was removed — it could emit
# PROBE_INCOMPLETE on runs the locked contract says must continue).

FAMILIES = ("territory", "elimination", "connection", "threshold")

# CAL references (Phase B GAME_SPECS sources + families; drift-guarded).
CAL_SPECS = (
    ("573562833174", "genesis_v2_run21_grid.db", "connection"),
    ("e1453dac5445", "genesis_v2_run21_menger.db", "threshold"),
)

N_BOOT = 1000
CI_LO, CI_HI = 2.5, 97.5

CHECKPOINT_EVERY = 25


# ---------------------------------------------------------------------------
# Evaluation (content-derived seeds; per-eval timeout)
# ---------------------------------------------------------------------------

class EvalTimeout(Exception):
    pass


def _alarm_handler(signum, frame):  # pragma: no cover - signal plumbing
    raise EvalTimeout()


def eval_seed_for(canon: str, batch_index: int) -> int:
    """Registered: (int(canonical_hash[:16], 16) + 7919*batch_index) mod 2^31."""
    return (int(canon[:16], 16) + 7919 * batch_index) % (2 ** 31)


def compute_batch(game: GameDefV2, canon: str, batch_index: int,
                  batch_n: int) -> tuple[BatchResult, list[dict]]:
    """One seeded rollout batch -> BatchResult (+ raw rollouts for the
    one-time descriptor_row cross-check). Raises EvalTimeout / engine
    exceptions; the caller decides budget accounting."""
    seed = eval_seed_for(canon, batch_index)
    signal.signal(signal.SIGALRM, _alarm_handler)
    signal.alarm(EVAL_TIMEOUT_S)
    try:
        rollouts = run_protocol(game, batch_n, seed)
        topo = game.get_topology()
        dramas: list[float] = []
        draws = 0
        interactions: list[float] = []
        lengths: list[float] = []
        for r in rollouts:
            d = obs_drama_for_rollout(game, topo, r)
            if d is None:
                draws += 1
            else:
                dramas.append(float(d))
            interactions.append(interaction_rate_for_rollout(topo, r))
            lengths.append(float(r["game_length"]))
    finally:
        signal.alarm(0)
    return (
        BatchResult(batch_n=batch_n, dramas=dramas, draws=draws,
                    interactions=interactions, lengths=lengths),
        rollouts,
    )


_CROSS_CHECKED = False


def cross_check_against_descriptor_row(game: GameDefV2, batch: BatchResult,
                                       rollouts: list[dict]) -> None:
    """Exact-equality assert vs the locked descriptor_row (Phase B pattern);
    no-ops after the first successful check."""
    global _CROSS_CHECKED
    if _CROSS_CHECKED:
        return
    row = descriptor_row(game, rollouts)
    ours_drama = float(np.mean(batch.dramas)) if batch.dramas else float("nan")
    assert (row["obs_drama"] == ours_drama
            or (np.isnan(row["obs_drama"]) and np.isnan(ours_drama))), \
        f"drama cross-check failed: {row['obs_drama']} != {ours_drama}"
    assert row["obs_drama_n"] == len(batch.dramas)
    assert row["draws"] == batch.draws
    assert row["interaction_rate"] == batch.mean_interaction(), \
        "interaction cross-check failed"
    assert row["game_length"] == batch.mean_length(), \
        "game_length cross-check failed"
    _CROSS_CHECKED = True
    print("  [cross-check] descriptor_row exact-equality PASSED")


# ---------------------------------------------------------------------------
# Decision grammar (locked; pure function, synthetically tested in
# test_rc2_archive.py before any probe data)
# ---------------------------------------------------------------------------

def decide_verdict(cal_gap: float, family_spreads: dict,
                   top10_m: float, top10_r: float,
                   m_elites: int, r_elites: int,
                   incomplete: str | None) -> str:
    """family_spreads: SAMPLED families only (n_valid >= the quota), each
    with p90_p10. Grammar order: incompleteness, CAL, sampled-family count,
    BAR W, archive sizes, BAR H — per the locked grammar.
    """
    # "Wall cap hit, attempt caps exhausted before quotas, unloadable
    # reference games ... -> PROBE_INCOMPLETE"
    if incomplete is not None:
        return "PROBE_INCOMPLETE"
    # "CAL bar fail -> PROBE_INVALID"
    if cal_gap < CAL_FLOOR:
        return "PROBE_INVALID"
    # "< 2 sampled families -> PROBE_INCOMPLETE"
    if len(family_spreads) < 2:
        return "PROBE_INCOMPLETE"
    # "BAR W: LIVE iff P90 - P10 >= 0.064; passes iff >= 2 sampled families
    # are LIVE. BAR W fail -> ARCHIVE_KILL"
    live = sum(1 for f in family_spreads.values()
               if f["p90_p10"] >= BAR_W_SPREAD_FLOOR)
    if live < 2:
        return "ARCHIVE_KILL"
    # "either archive < 10 elites -> PROBE_INCOMPLETE"
    if m_elites < TOP_K or r_elites < TOP_K:
        return "PROBE_INCOMPLETE"
    # "BAR H: top10(M) - top10(R) >= 0.03" -> ARCHIVE_GO else ARCHIVE_NEUTRAL
    if top10_m - top10_r >= BAR_H_FLOOR:
        return "ARCHIVE_GO"
    return "ARCHIVE_NEUTRAL"


# ---------------------------------------------------------------------------
# Probe driver
# ---------------------------------------------------------------------------

class Probe:
    def __init__(self, out_dir: Path, smoke: bool, base_seed: int = BASE_SEED,
                 b_arm: int = B_ARM) -> None:
        self.out = out_dir
        self.smoke = smoke
        self.t0 = time.monotonic()
        self.incomplete: str | None = None
        self.eval_counters: dict[str, int] = defaultdict(int)

        # Seed streams derive from base_seed exactly as the registered
        # constants do from base 13 (13M/26M/39M/52M/65M = 13M x {1..5});
        # base_seed 17 (the R2 replicate) gives 17M/34M/51M/68M/85M —
        # disjoint from every run-1 stream.
        self.base_seed = base_seed
        self.stage0_seed_base = base_seed * 1_000_000
        self.arm_r_seed_base = 2 * base_seed * 1_000_000
        mut_seed = 3 * base_seed * 1_000_000
        sel_seed = 4 * base_seed * 1_000_000
        self.boot_seed = 5 * base_seed * 1_000_000
        assert (base_seed != BASE_SEED
                or (self.stage0_seed_base, self.arm_r_seed_base, mut_seed,
                    sel_seed, self.boot_seed)
                == (STAGE0_GEN_SEED_BASE, ARM_R_GEN_SEED_BASE,
                    ARM_M_MUT_SEED, ARM_M_SEL_SEED, BOOT_SEED)), \
            "derived seed streams must reproduce the registered constants"

        if smoke:
            # Registered: smoke streams are DISJOINT from probe streams.
            self.seed_offset = 777_000
            self.n_stage0, self.n_stage1 = 10, 10
            self.bar_w_min_valid, self.min_total_valid = 2, 8
            self.stage0_max_evals, self.stage0_max_attempts = 24, 300
            self.b_arm, self.reeval_at = 10, (5, 10)
            self.wall_cap = 1800
        else:
            self.seed_offset = 0
            self.n_stage0, self.n_stage1 = N_STAGE0, N_STAGE1
            self.bar_w_min_valid = BAR_W_MIN_VALID
            self.min_total_valid = STAGE0_MIN_TOTAL_VALID
            self.stage0_max_evals = STAGE0_MAX_EVALS
            self.stage0_max_attempts = STAGE0_MAX_ATTEMPTS
            self.b_arm = b_arm
            # registered cadence: full-archive re-eval every 100 evals,
            # final re-eval at B (REEVAL_AT for the registered B=300)
            self.reeval_at = tuple(range(100, b_arm + 1, 100))
            self.wall_cap = WALL_CAP_S

        # One generator instance hosts generate_game + quick_reject; game
        # content depends only on the per-call seed (verified: identical
        # canonical hashes across fresh instances).
        self.gen = GameGeneratorV2(GameConfig(), seed=0)
        # State filled by stages
        self.cal: dict = {}
        self.stage0_records: list[dict] = []
        self.stage0_progress = {"attempts": 0, "evaluated": 0}
        self.family_spreads: dict = {}
        self.archives: dict[str, QDArchive] = {}
        self.arm_state: dict = {
            "R": {"evals": 0, "attempt": 0, "skips": 0, "log": []},
            "M": {"evals": 0, "attempt": 0, "skips": 0, "log": []},
        }
        self.reeval_records: dict[str, list] = {"R": [], "M": []}
        self.sel_rng = np.random.default_rng(sel_seed + self.seed_offset)
        self.mut_rng = np.random.default_rng(mut_seed + self.seed_offset)
        self.mut_op = MutationOperatorV2(EvolutionConfig(), self.mut_rng)

    # -- plumbing ------------------------------------------------------

    def wall_exceeded(self) -> bool:
        if time.monotonic() - self.t0 > self.wall_cap:
            self.incomplete = "wall_cap"
            return True
        return False

    def eval_or_none(self, game: GameDefV2, canon: str, batch_index: int,
                     batch_n: int, cross_check: bool = False
                     ) -> BatchResult | None:
        """Budget-consuming eval; None on timeout/engine error (counted)."""
        try:
            batch, rollouts = compute_batch(game, canon, batch_index, batch_n)
        except EvalTimeout:
            self.eval_counters["eval_timeout"] += 1
            return None
        except Exception as exc:  # engine/harness error — registered EVAL_ERROR
            self.eval_counters["eval_error"] += 1
            print(f"  [eval_error] {canon[:12]}: {type(exc).__name__}: {exc}")
            return None
        if cross_check:
            cross_check_against_descriptor_row(game, batch, rollouts)
        return batch

    def topup_eval_fn(self):
        """evaluate_batch for archive top-ups/re-evals: returns None on
        failure so the archive abandons/skips (never crashes the run)."""
        def fn(game, batch_index, batch_n):
            return self.eval_or_none(game, game.canonical_hash(),
                                     batch_index, batch_n)
        return fn

    # -- CAL -----------------------------------------------------------

    def run_cal(self) -> None:
        print("=== CAL: instrument check (573 vs e1453) ===")
        dramas = {}
        for gid, db, family in CAL_SPECS:
            try:
                game = load_game_from_db(db, gid)
            except SystemExit as exc:
                self.incomplete = f"cal_unloadable:{gid} ({exc})"
                return
            if game.win_condition.condition_type != family:
                raise SystemExit(
                    f"family drift: {gid} is "
                    f"{game.win_condition.condition_type}, registered {family}")
            canon = game.canonical_hash()
            batch = self.eval_or_none(game, canon, 0, self.n_stage0)
            if batch is None or not batch.dramas:
                self.incomplete = f"cal_eval_failed:{gid}"
                return
            dramas[gid] = batch.mean_drama()
            print(f"  {gid}: obs_drama={dramas[gid]:.4f} "
                  f"(n_used={len(batch.dramas)}, draws={batch.draws})")
        self.cal = {
            "drama_573": dramas["573562833174"],
            "drama_e1453": dramas["e1453dac5445"],
            "gap": dramas["573562833174"] - dramas["e1453dac5445"],
        }
        print(f"  CAL gap = {self.cal['gap']:.4f} (floor {CAL_FLOOR})")

    def cal_failed(self) -> bool:
        return bool(self.cal) and self.cal["gap"] < CAL_FLOOR

    # -- Stage 0 -------------------------------------------------------

    def _valid_by_family(self) -> dict[str, list]:
        out: dict[str, list] = {f: [] for f in FAMILIES}
        for rec in self.stage0_records:
            if rec["valid"]:
                out[rec["family"]].append(rec)
        return out

    def stage0_quotas_met(self, valid_by_family: dict) -> bool:
        total = sum(len(v) for v in valid_by_family.values())
        return (total >= self.min_total_valid
                and all(len(valid_by_family[f]) >= self.bar_w_min_valid
                        for f in FAMILIES))

    def run_stage0(self) -> None:
        print("=== Stage 0: fresh sample ===")
        seen = {rec["canon"] for rec in self.stage0_records}
        while True:
            if self.wall_exceeded():
                return
            valid_by_family = self._valid_by_family()
            if self.stage0_quotas_met(valid_by_family):
                break
            if self.stage0_progress["evaluated"] >= self.stage0_max_evals:
                break
            if self.stage0_progress["attempts"] >= self.stage0_max_attempts:
                # Registered: "attempt caps exhausted before quotas
                # -> PROBE_INCOMPLETE" (generation stalled; the 160-eval
                # stop above is a NORMAL stop, not an attempt-cap stop).
                self.incomplete = "stage0_attempts_exhausted"
                break
            game = self.gen.generate_game(
                seed=self.stage0_seed_base + self.seed_offset
                + self.stage0_progress["attempts"])
            self.stage0_progress["attempts"] += 1
            if not self.gen.quick_reject(game):
                self.eval_counters["stage0_quick_reject"] += 1
                continue
            canon = game.canonical_hash()
            if canon in seen:
                self.eval_counters["stage0_dedup"] += 1
                continue
            seen.add(canon)
            batch = self.eval_or_none(game, canon, 0, self.n_stage0,
                                      cross_check=True)
            self.stage0_progress["evaluated"] += 1
            family = game.win_condition.condition_type
            if batch is None:
                # consumed budget; recorded so the canon stays "seen" for
                # the arms' dedup (registered: dedup vs everything
                # previously seen, including Stage-0 candidates)
                rec = {"game": game, "canon": canon, "family": family,
                       "batch": None, "valid": False,
                       "invalid_reason": "eval_failed"}
            else:
                reason = validity(batch)
                rec = {"game": game, "canon": canon, "family": family,
                       "batch": batch, "valid": reason is None,
                       "invalid_reason": reason}
                if reason is not None:
                    self.eval_counters[f"stage0_invalid_{reason}"] += 1
            self.stage0_records.append(rec)
            ev = self.stage0_progress["evaluated"]
            if ev % CHECKPOINT_EVERY == 0:
                save_checkpoint(self, "stage0_running")
            if ev % 20 == 0:
                counts = {f: len(v)
                          for f, v in self._valid_by_family().items()}
                print(f"  evaluated {ev} "
                      f"(attempts {self.stage0_progress['attempts']}): "
                      f"valid by family {counts}")

        # BAR W summary over SAMPLED families
        self.family_spreads = {}
        for fam in FAMILIES:
            recs = self._valid_by_family()[fam]
            if len(recs) < self.bar_w_min_valid:
                print(f"  family {fam}: UNSAMPLED ({len(recs)} valid)")
                continue
            dramas = [r["batch"].mean_drama() for r in recs]
            p90 = float(np.percentile(dramas, 90))
            p10 = float(np.percentile(dramas, 10))
            spread = p90 - p10
            self.family_spreads[fam] = {
                "n_valid": len(recs), "p10": p10, "p90": p90,
                "p90_p10": spread,
                "live": spread >= BAR_W_SPREAD_FLOOR,
            }
            print(f"  family {fam}: n={len(recs)} p90-p10={spread:.4f} "
                  f"{'LIVE' if spread >= BAR_W_SPREAD_FLOOR else 'dead'}")

    def bar_w_failed(self) -> bool:
        live = sum(1 for f in self.family_spreads.values() if f["live"])
        return len(self.family_spreads) >= 2 and live < 2

    # -- Stage 1 -------------------------------------------------------

    def init_archives(self) -> None:
        eval_fn = self.topup_eval_fn()
        for arm in ("R", "M"):
            arch = QDArchive(batch_n=self.n_stage1)
            for rec in self.stage0_records:
                arch.mark_seen(rec["canon"])     # incl. invalid: budget spent
            for rec in self.stage0_records:
                if rec["valid"]:
                    arch.offer(rec["game"], rec["canon"], rec["batch"],
                               eval_fn)
            self.archives[arm] = arch
            print(f"  arm {arm} initialized: coverage {arch.coverage}, "
                  f"QD {arch.qd_score:.3f}")

    def draw_candidate_R(self) -> tuple | None:
        arch = self.archives["R"]
        st = self.arm_state["R"]
        for _ in range(REDRAW_CAP):
            game = self.gen.generate_game(
                seed=self.arm_r_seed_base + self.seed_offset + st["attempt"])
            st["attempt"] += 1
            if not self.gen.quick_reject(game):
                self.eval_counters["R_quick_reject"] += 1
                continue
            canon = game.canonical_hash()
            if arch.is_seen(canon):
                self.eval_counters["R_dedup"] += 1
                continue
            return game, canon, None
        return None

    def draw_candidate_M(self) -> tuple | None:
        arch = self.archives["M"]
        st = self.arm_state["M"]
        if not arch.cells:
            return None
        for _ in range(REDRAW_CAP):
            st["attempt"] += 1
            cells = sorted(arch.cells)
            cell = cells[int(self.sel_rng.integers(0, len(cells)))]
            parent = arch.cells[cell]
            child = self.mut_op.mutate_game(parent.game)
            if not self.gen.quick_reject(child):
                self.eval_counters["M_quick_reject"] += 1
                continue
            canon = child.canonical_hash()
            if arch.is_seen(canon):
                self.eval_counters["M_dedup"] += 1
                continue
            return child, canon, parent
        return None

    def run_arm(self, arm: str) -> None:
        print(f"=== Stage 1, arm {arm} "
              f"({'random' if arm == 'R' else 'MAP-Elites'}) ===")
        arch = self.archives[arm]
        st = self.arm_state[arm]
        eval_fn = self.topup_eval_fn()
        draw = self.draw_candidate_R if arm == "R" else self.draw_candidate_M
        while st["evals"] < self.b_arm:
            if self.wall_exceeded():
                return
            cand = draw()
            if cand is None:
                st["skips"] += 1
                continue
            game, canon, parent = cand
            arch.mark_seen(canon)
            batch = self.eval_or_none(game, canon, 0, self.n_stage1)
            st["evals"] += 1
            if batch is None:
                outcome = "eval_failed"
            else:
                outcome = arch.offer(game, canon, batch, eval_fn)
            entry = {
                "step": st["evals"], "child_canon": canon,
                "child_batch_drama": (batch.mean_drama()
                                      if batch and batch.dramas else None),
                "outcome": outcome,
            }
            if arm == "M":
                entry["parent_canon"] = parent.canon
                entry["parent_pooled_drama"] = parent.pooled_drama
            st["log"].append(entry)
            if st["evals"] in self.reeval_at:
                print(f"  [{arm}] re-eval at {st['evals']} evals "
                      f"(coverage {arch.coverage})")
                self.reeval_records[arm].extend(
                    [dict(r, cell=list(r["cell"]), at_evals=st["evals"])
                     for r in arch.reeval_all(eval_fn)])
            if st["evals"] % CHECKPOINT_EVERY == 0:
                save_checkpoint(self, f"arm_{arm}_running")
                print(f"  [{arm}] {st['evals']}/{self.b_arm} evals, "
                      f"coverage {arch.coverage}, QD {arch.qd_score:.3f}")

    # -- verdict -------------------------------------------------------

    def top10_mean(self, arm: str) -> float:
        arch = self.archives.get(arm)
        if arch is None:
            return float("nan")
        tops = arch.top_elites(TOP_K)
        if len(tops) < TOP_K:
            return float("nan")
        return float(np.mean([e.pooled_drama for e in tops]))

    def heritability(self) -> tuple[float | None, int]:
        pairs = [(r["parent_pooled_drama"], r["child_batch_drama"])
                 for r in self.arm_state["M"]["log"]
                 if r.get("parent_pooled_drama") is not None
                 and r.get("child_batch_drama") is not None]
        if len(pairs) < 3:
            return None, len(pairs)
        px, cy = zip(*pairs)
        if float(np.std(px)) == 0.0 or float(np.std(cy)) == 0.0:
            return None, len(pairs)
        return float(np.corrcoef(px, cy)[0, 1]), len(pairs)

    def verdict_now(self, enforce_budget: bool) -> str:
        if enforce_budget and self.incomplete is None:
            # Strict conformance: the 10h cap is re-checked at verdict
            # emission (re-eval/top-up loops between budget steps cannot
            # be interrupted, so the final crossing is caught here).
            self.wall_exceeded()
        if enforce_budget and self.incomplete is None:
            for arm in ("R", "M"):
                if self.arm_state[arm]["evals"] < self.b_arm:
                    self.incomplete = f"arm_{arm}_under_budget"
        return decide_verdict(
            cal_gap=self.cal.get("gap", float("-inf")),
            family_spreads=self.family_spreads,
            top10_m=self.top10_mean("M"),
            top10_r=self.top10_mean("R"),
            m_elites=self.archives["M"].coverage if "M" in self.archives else 0,
            r_elites=self.archives["R"].coverage if "R" in self.archives else 0,
            incomplete=self.incomplete,
        )


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def write_reports(p: Probe, verdict: str) -> None:
    out = p.out
    out.mkdir(parents=True, exist_ok=True)
    boot_rng = np.random.default_rng(p.boot_seed)

    # ---- CSV: stage0 + final elites ----
    with open(out / "probe_results.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["section", "arm", "canon", "family", "cell",
                    "pooled_drama", "pooled_n", "interaction", "length",
                    "valid", "outcome"])
        for rec in p.stage0_records:
            b = rec["batch"]
            if b is None:
                w.writerow(["stage0", "", rec["canon"][:16], rec["family"],
                            "", "", "", "", "", False, "eval_failed"])
                continue
            w.writerow(["stage0", "", rec["canon"][:16], rec["family"], "",
                        f"{b.mean_drama():.6f}", b.batch_n,
                        f"{b.mean_interaction():.6f}",
                        f"{b.mean_length():.2f}",
                        rec["valid"], rec["invalid_reason"] or ""])
        for arm, arch in sorted(p.archives.items()):
            for cell in sorted(arch.cells):
                e = arch.cells[cell]
                w.writerow(["final_elite", arm, e.canon[:16], cell[0],
                            f"{cell[1]}/{cell[2]}",
                            f"{e.pooled_drama:.6f}", e.pooled_n, "", "",
                            "", ""])

    # ---- arm logs ----
    for arm in ("R", "M"):
        log = p.arm_state[arm]["log"]
        if not log:
            continue
        fieldnames = sorted({k for row in log for k in row})
        with open(out / f"arm_{arm}_log.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(log)

    # ---- markdown report ----
    lines: list[str] = []
    title = "RC2 Phase C archive probe — results"
    if p.smoke:
        title += " (SMOKE RUN — disjoint seed streams, NOT a verdict)"
    lines.append(f"# {title}\n")
    lines.append(
        f"Protocol per experiments/rc2_archive/PREREGISTRATION.md (locked): "
        f"base_seed {p.base_seed}, Stage-0 n={p.n_stage0}, "
        f"Stage-1 n={p.n_stage1}, B={p.b_arm}/arm, re-eval at "
        f"{tuple(p.reeval_at)}.\n")

    lines.append("## CAL\n")
    if p.cal:
        lines.append(f"- drama(573562833174) = {p.cal['drama_573']:.4f}")
        lines.append(f"- drama(e1453dac5445) = {p.cal['drama_e1453']:.4f}")
        lines.append(f"- gap = {p.cal['gap']:.4f} (floor {CAL_FLOOR}) -> "
                     f"{'PASS' if p.cal['gap'] >= CAL_FLOOR else 'FAIL'}\n")
    else:
        lines.append("- not run / unloadable\n")

    lines.append("## Stage 0 — BAR W (within-family separation)\n")
    lines.append(f"Attempts {p.stage0_progress['attempts']}, evaluated "
                 f"{p.stage0_progress['evaluated']}, valid "
                 f"{sum(1 for r in p.stage0_records if r['valid'])}.\n")
    lines.append("| family | n_valid | p10 | p90 | p90-p10 | LIVE "
                 f"(floor {BAR_W_SPREAD_FLOOR}) |")
    lines.append("|---|---:|---:|---:|---:|---|")
    for fam in FAMILIES:
        fs = p.family_spreads.get(fam)
        if fs is None:
            n = sum(1 for r in p.stage0_records
                    if r["valid"] and r["family"] == fam)
            lines.append(f"| {fam} | UNSAMPLED ({n}) | | | | |")
        else:
            lines.append(
                f"| {fam} | {fs['n_valid']} | {fs['p10']:.4f} | "
                f"{fs['p90']:.4f} | {fs['p90_p10']:.4f} | "
                f"{'YES' if fs['live'] else 'no'} |")
    live_n = sum(1 for f in p.family_spreads.values() if f["live"])
    lines.append(f"\nBAR W: {live_n} LIVE of {len(p.family_spreads)} sampled "
                 f"-> {'PASS' if live_n >= 2 else 'FAIL'}\n")

    lines.append("## Stage 1 — BAR H (matched-budget search value)\n")
    lines.append("| arm | evals | coverage | QD-score | top-10 mean drama "
                 "[95% CI] | skips |")
    lines.append("|---|---:|---:|---:|---|---:|")
    for arm in ("R", "M"):
        arch = p.archives.get(arm)
        if arch is None:
            lines.append(f"| {arm} | not run | | | | |")
            continue
        tops = arch.top_elites(TOP_K)
        top_dramas = [e.pooled_drama for e in tops]
        # CI: bootstrap over each top elite's pooled per-rollout dramas,
        # re-meaning the 10 per-elite means per resample.
        if len(tops) >= TOP_K:
            res_means = []
            for _ in range(N_BOOT):
                vals = []
                for e in tops:
                    pe = np.asarray(e.pooled_dramas, dtype=float)
                    vals.append(float(np.mean(
                        boot_rng.choice(pe, size=pe.size, replace=True))))
                res_means.append(float(np.mean(vals)))
            lo = float(np.percentile(res_means, CI_LO))
            hi = float(np.percentile(res_means, CI_HI))
            mean_str = f"{np.mean(top_dramas):.4f} [{lo:.4f}, {hi:.4f}]"
        else:
            mean_str = f"only {len(tops)} elites"
        lines.append(f"| {arm} | {p.arm_state[arm]['evals']} | "
                     f"{arch.coverage} | {arch.qd_score:.3f} | {mean_str} | "
                     f"{p.arm_state[arm]['skips']} |")
    if "M" in p.archives and "R" in p.archives:
        d = p.top10_mean("M") - p.top10_mean("R")
        lines.append(f"\nBAR H: top10(M) - top10(R) = {d:.4f} "
                     f"(floor {BAR_H_FLOOR}) -> "
                     f"{'PASS' if d >= BAR_H_FLOOR else 'FAIL'}\n")

        shared = sorted(set(p.archives["M"].cells)
                        & set(p.archives["R"].cells))
        if shared:
            m_wins = ties = 0
            for c in shared:
                dm = p.archives["M"].cells[c].pooled_drama
                dr = p.archives["R"].cells[c].pooled_drama
                if p.archives["M"].cells[c].canon == p.archives["R"].cells[c].canon:
                    ties += 1          # same elite (shared Stage-0 init)
                elif dm > dr:
                    m_wins += 1
            losses = len(shared) - m_wins - ties
            lines.append(f"Jointly filled cells: {len(shared)}; arm M wins "
                         f"{m_wins}, same-elite ties {ties}, losses "
                         f"{losses}.\n")
        for arm in ("R", "M"):
            tops = p.archives[arm].top_elites(TOP_K)
            fams: dict[str, int] = defaultdict(int)
            for e in tops:
                fams[e.cell[0]] += 1
            lines.append(f"Arm {arm} top-10 family composition: "
                         f"{dict(sorted(fams.items()))}.")
        r, n_pairs = p.heritability()
        lines.append(f"\nParent-child drama heritability (arm M): "
                     f"r = {'n/a' if r is None else format(r, '.3f')} "
                     f"over {n_pairs} pairs.\n")

    lines.append("## Re-eval re-pricing (phantom diagnostic)\n")
    for arm in ("R", "M"):
        recs = p.reeval_records[arm]
        if not recs:
            continue
        deltas = [abs(r["pooled_after"] - r["pooled_before"])
                  for r in recs if r["fresh_batch"] is not None]
        if deltas:
            lines.append(
                f"- arm {arm}: {len(recs)} re-evals, max |repricing| "
                f"{max(deltas):.4f}, mean {np.mean(deltas):.4f}")
    lines.append("")

    lines.append("## Counters\n")
    for k in sorted(p.eval_counters):
        lines.append(f"- {k}: {p.eval_counters[k]}")
    for arm, arch in sorted(p.archives.items()):
        lines.append(f"- arm {arm} archive: "
                     + ", ".join(f"{k}={v}" for k, v in
                                 sorted(arch.counters.items()) if v))
    lines.append(f"- wall time: {(time.monotonic() - p.t0) / 60:.1f} min")
    if p.incomplete:
        lines.append(f"- INCOMPLETE: {p.incomplete}")
    lines.append("")

    lines.append("## Verdict\n")
    if p.smoke:
        lines.append(f"SMOKE RUN — would-be token (not registered): {verdict}")
    else:
        lines.append("```")
        lines.append(verdict)
        lines.append("```")
    lines.append("")

    (out / "probe_results.md").write_text("\n".join(lines))
    print(f"\nReports written to {out}/probe_results.{{md,csv}}")


# ---------------------------------------------------------------------------
# Checkpointing
# ---------------------------------------------------------------------------

def save_checkpoint(p: Probe, stage: str) -> None:
    ck = {
        "stage": stage,
        "smoke": p.smoke,
        "base_seed": p.base_seed,
        "b_arm": p.b_arm,
        "cal": p.cal,
        "incomplete": p.incomplete,
        "eval_counters": dict(p.eval_counters),
        "family_spreads": p.family_spreads,
        "stage0_progress": p.stage0_progress,
        "stage0_records": [
            {"game": r["game"].to_dict(), "canon": r["canon"],
             "family": r["family"],
             "batch": r["batch"].to_dict() if r["batch"] else None,
             "valid": r["valid"], "invalid_reason": r["invalid_reason"]}
            for r in p.stage0_records
        ],
        "archives": {arm: a.to_dict() for arm, a in p.archives.items()},
        "arm_state": p.arm_state,
        "reeval_records": p.reeval_records,
        "sel_rng": p.sel_rng.bit_generator.state,
        "mut_rng": p.mut_rng.bit_generator.state,
        "cross_checked": _CROSS_CHECKED,
        "elapsed": time.monotonic() - p.t0,
    }
    tmp = p.out / "checkpoint.json.tmp"
    tmp.write_text(json.dumps(ck))
    tmp.rename(p.out / "checkpoint.json")


def load_checkpoint(p: Probe) -> str:
    global _CROSS_CHECKED
    ck = json.loads((p.out / "checkpoint.json").read_text())
    if ck["smoke"] != p.smoke:
        raise SystemExit("checkpoint smoke flag mismatch")
    if ck.get("base_seed", BASE_SEED) != p.base_seed \
            or ck.get("b_arm", B_ARM) != p.b_arm:
        raise SystemExit("checkpoint base_seed/b_arm mismatch")
    p.cal = ck["cal"]
    p.incomplete = ck["incomplete"]
    p.eval_counters.update(ck["eval_counters"])
    p.family_spreads = ck["family_spreads"]
    p.stage0_progress = ck["stage0_progress"]
    p.stage0_records = [
        {"game": GameDefV2.from_dict(r["game"]), "canon": r["canon"],
         "family": r["family"],
         "batch": BatchResult.from_dict(r["batch"]) if r["batch"] else None,
         "valid": r["valid"], "invalid_reason": r["invalid_reason"]}
        for r in ck["stage0_records"]
    ]
    p.archives = {arm: QDArchive.from_dict(a, GameDefV2.from_dict)
                  for arm, a in ck["archives"].items()}
    p.arm_state = ck["arm_state"]
    p.reeval_records = ck["reeval_records"]
    p.sel_rng.bit_generator.state = ck["sel_rng"]
    p.mut_rng.bit_generator.state = ck["mut_rng"]
    _CROSS_CHECKED = ck["cross_checked"]
    p.t0 = time.monotonic() - ck["elapsed"]
    return ck["stage"]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--base-seed", type=int, default=BASE_SEED)
    ap.add_argument("--b-arm", type=int, default=B_ARM)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    out = Path(args.out) if args.out else (
        HERE / "smoke" if args.smoke else HERE)
    out.mkdir(parents=True, exist_ok=True)
    p = Probe(out, smoke=args.smoke, base_seed=args.base_seed,
              b_arm=args.b_arm)

    stage = "start"
    if args.resume and (out / "checkpoint.json").exists():
        stage = load_checkpoint(p)
        print(f"Resumed from checkpoint at stage '{stage}'")
        if stage == "terminal":
            raise SystemExit(
                "run already reached a terminal verdict — see "
                f"{out / 'probe_results.md'}")

    def finish_early() -> None:
        verdict = p.verdict_now(enforce_budget=False)
        write_reports(p, verdict)
        save_checkpoint(p, "terminal")
        print(f"\nVERDICT: {verdict}")

    if stage == "start":
        p.run_cal()
        stage = "cal_done"
        save_checkpoint(p, stage)
        # Early exits (suppressed in smoke so every path is exercised)
        if not p.smoke and (p.incomplete or p.cal_failed()):
            finish_early()
            return

    if stage in ("cal_done", "stage0_running"):
        p.run_stage0()
        stage = "stage0_done"
        save_checkpoint(p, stage)
        if not p.smoke and (p.incomplete or len(p.family_spreads) < 2
                            or p.bar_w_failed()):
            finish_early()
            return

    if stage == "stage0_done":
        p.init_archives()
        stage = "arms_init"
        save_checkpoint(p, stage)

    if stage in ("arms_init", "arm_R_running"):
        p.run_arm("R")
        stage = "arm_R_done"
        save_checkpoint(p, stage)

    if stage in ("arm_R_done", "arm_M_running") and p.incomplete is None:
        p.run_arm("M")
        stage = "arm_M_done"
        save_checkpoint(p, stage)

    verdict = p.verdict_now(enforce_budget=True)
    write_reports(p, verdict)
    save_checkpoint(p, "terminal")
    label = "SMOKE would-be token" if p.smoke else "VERDICT"
    print(f"\n{label}: {verdict}")


if __name__ == "__main__":
    main()
