"""RC2 campaign runner — PG-driven QD search (forked from Phase C).

Implements experiments/rc2_campaign/PREREGISTRATION.md (LOCKED, `72890a0`)
plus the ratified BUILD_LOG decisions (#1-#9). Fork of
experiments/rc2_archive/run_probe.py: same stage machine (Stage 0 fresh
sample -> shared archive init -> matched-budget arms R/M -> bars), with the
quality signal swapped from drama to planning-gap per the locked contract:

  - Per-genome eval = descriptor batch (Phase C verbatim, cell placement,
    BUILD_LOG #1) + T1 planning-gap batch (net-free UCT@128 vs @16, n=24,
    pg_eval.py) — both content-seeded (eval_seed_for, batch_index 0).
  - Validity from the T1 games (§4 step 3 [C13], BUILD_LOG #2).
  - Guard stage (RUSH/TILT/REACH-v3, guard_stage.py) gates EVERY insertion
    (BUILD_LOG #4); the archive calls it only for genomes that would enter.
  - Two ledgers never mixed (§3 [C9]): T1 for insertion, full-conv (256v16,
    n=48) written at re-eval checkpoints 300/600 (erratum #13) and read by
    BAR H.
  - BAR W-PG at Stage-0 close (preempts arms, §9); BAR H-PG post-arms with
    the registered saturation contingency (bars.py, §6).
  - CAL-I is a PRE-campaign artifact (cal_i.py, §5): the runner refuses to
    start a real campaign without cal_i.json, and a recorded FAIL routes to
    PROBE_INVALID through the §9 chain.
  - The runner stops at "slate-ready": when BAR W ∧ BAR H pass it records
    SLATE_PENDING (NOT a §9 token — the slate stage runs later, manually);
    §9 tokens PROBE_INVALID / PROBE_INCOMPLETE / ARCHIVE_KILL /
    SEARCH_NEUTRAL are emitted as usual via bars.decide_verdict.

Worker/timeout model (BUILD_LOG #9, ratified): one persistent
ProcessPoolExecutor(max_workers=7); each genome's T1/full-conv UCT games and
guard-stage tactical rollouts fan out as pool tasks guarded by
future.result(timeout=180) per atomic engine unit; the descriptor batch runs
inline under the Phase C signal.alarm(180). Any unit timeout / engine
exception -> EVAL_TIMEOUT / EVAL_ERROR for that genome (budget slot
consumed, excluded from archives and bars, counted, §2). The genome/offer
loop stays SEQUENTIAL (offers are order-dependent registered semantics).
Pool tasks are module-level functions taking the serialized game dict and
rebuilding with GameDefV2.from_dict inside the worker (engines may not
pickle cleanly; the cal_r/anchor_calibration load-by-key pattern).

Usage:
    .venv/bin/python experiments/rc2_campaign/run_campaign.py [--smoke]
        [--resume] [--out DIR] [--b-arm N]

--smoke runs a miniature end-to-end pass on seed bases INSIDE the recorded
smoke range (seeds.RECORDED_STREAMS["smoke"], 999_000_000+ — recorded
precisely so the campaign bases avoid it), ignores the early-exit gates so
every code path is exercised, writes to experiments/rc2_campaign/smoke/,
and NEVER emits a verdict token. assert_disjoint() still runs (and must
pass) in smoke mode: it validates the REGISTERED campaign constants.

Checkpoints: written every 25 genome-evals and at stage boundaries
(atomic tmp+rename); --resume continues from the last checkpoint.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import signal
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeout
from concurrent.futures.process import BrokenProcessPool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import EvolutionConfig, GameConfig  # noqa: E402
from evolution.operators_v2 import MutationOperatorV2  # noqa: E402
from evolution.qd_archive import BatchResult, cell_key  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from game_engine.generator_v2 import GameGeneratorV2  # noqa: E402
from metrics.descriptors import (  # noqa: E402
    descriptor_row,
    interaction_rate_for_rollout,
    obs_drama_for_rollout,
)
from metrics.guard_probe import (  # noqa: E402
    rollout_tactical,
    rush_share,
    tilt_p1_share,
)
from metrics.rollout_traces import run_protocol  # noqa: E402
from experiments.rc2_archive.run_probe import eval_seed_for  # noqa: E402
from experiments.rc2_campaign import seeds  # noqa: E402
from experiments.rc2_campaign.bars import (  # noqa: E402
    BAR_W_FLOOR,
    bar_h,
    bar_w,
    decide_verdict,
)
from experiments.rc2_campaign.campaign_archive import CampaignArchive  # noqa: E402
from experiments.rc2_campaign.guard_stage import (  # noqa: E402
    N_PAIRS,
    _verdict_from_shares,
    guard_pair_seeds,
)
from experiments.rc2_campaign.pg_eval import (  # noqa: E402
    FULL_DEEP,
    FULL_N,
    FULL_SHALLOW,
    T1_DEEP,
    T1_N,
    T1_SHALLOW,
    pg_game,
    pg_seeds,
    pg_summarise,
)

# ---------------------------------------------------------------------------
# Pre-registered constants — experiments/rc2_campaign/PREREGISTRATION.md.
# Transcribed as data; not altered after data. Seed bases live in seeds.py
# (base 19 x {1..5}, [C1]); assert_disjoint() runs first in main().
# ---------------------------------------------------------------------------
B_ARM = 300                          # §2 as amended by BUILD_LOG erratum #14
                                     # (was 600; owner-ratified 2026-07-04
                                     # mid-search at R=50/M=0 — wall-clock
                                     # telemetry only; BAR W banked pre-
                                     # amendment, arm T1 PGs unconsulted)
REEVAL_STEP = 150                    # §3 as amended by errata #13 then #14
REEVAL_AT = (150, 300)               # checkpoints (150, 300): the #13
                                     # 2-checkpoints-per-arm shape at half B
assert tuple(range(REEVAL_STEP, B_ARM + 1, REEVAL_STEP)) == REEVAL_AT

N_STAGE0 = 100                       # descriptor batch n, Stage 0 (Phase C)
N_STAGE1 = 50                        # descriptor batch n, arms (Phase C)
BAR_W_MIN_VALID = 20                 # §6: qualifying family quota
STAGE0_MIN_TOTAL_VALID = 150         # §2
STAGE0_MAX_EVALS = 240               # §2 cap (normal stop)
STAGE0_MAX_ATTEMPTS = 3000           # §2 cap (-> PROBE_INCOMPLETE)
REDRAW_CAP = 50                      # Phase C carry-over (§2)

T1_MIN_NONDRAW_SHARE = 0.5           # §4 step 3 [C13] (T1 games, BUILD_LOG #2)
T1_MIN_MEAN_LENGTH = 6.0

EVAL_TIMEOUT_S = 180                 # §2, per atomic engine unit (BUILD_LOG #9)
WALL_CAP_S = 36 * 3600               # §6/§9 as amended by erratum #14 (was
                                     # 8h, sized by the /7-defective model;
                                     # 36h clears the corrected pessimistic
                                     # S2 projection of 35.24h)
WORKERS = 7                          # BUILD_LOG #9 / design doc
TOP_K = 10
FULL_CONV_BATCH_BASE = 1000          # checkpoint k -> batch_index 1000+k;
                                     # T1 always uses batch_index=0 (never collides)
CHECKPOINT_EVERY = 25
FAMILIES = ("territory", "elimination", "connection", "threshold")

N_BOOT = 1000                        # report CIs only (BOOT_SEED, §2)
CI_LO, CI_HI = 2.5, 97.5

CAL_I_JSON = HERE / "cal_i.json"     # §5 pre-campaign artifact (Task 8)

# --- smoke constants (monkeypatch-able; bases INSIDE the recorded smoke
# range 999_000_000..999_100_000 — seeds.RECORDED_STREAMS["smoke"]) ---------
SMOKE_GEN_SEED_BASE = 999_000_000
SMOKE_ARM_R_SEED_BASE = 999_020_000
SMOKE_ARM_M_MUT_SEED = 999_040_000
SMOKE_ARM_M_SEL_SEED = 999_050_000
SMOKE_BOOT_SEED = 999_060_000
SMOKE_DESCRIPTOR_N = 6
SMOKE_T1_N = 4
SMOKE_T1_DEEP, SMOKE_T1_SHALLOW = 16, 4
SMOKE_FULL_DEEP, SMOKE_FULL_SHALLOW, SMOKE_FULL_N = 16, 4, 2
SMOKE_B_ARM = 4
SMOKE_REEVAL_AT = (2, 4)
SMOKE_BAR_W_MIN_VALID = 2
SMOKE_MIN_TOTAL_VALID = 4
SMOKE_STAGE0_MAX_EVALS = 6
SMOKE_STAGE0_MAX_ATTEMPTS = 300
SMOKE_GUARD_PAIRS = 2
SMOKE_WORKERS = 2
SMOKE_WALL_CAP = 1800


# ---------------------------------------------------------------------------
# Pool workers (module-level: picklable under spawn; ALL parameters are
# explicit arguments — workers never read monkeypatched module constants)
# ---------------------------------------------------------------------------

class EvalTimeout(Exception):
    pass


def _alarm_handler(signum, frame):  # pragma: no cover - signal plumbing
    raise EvalTimeout()


def _pg_game_worker(game_dict: dict, deep_seed: int, shallow_seed: int,
                    deep_seat: int, deep_sims: int, shallow_sims: int) -> dict:
    """One UCT deep-vs-shallow game (rebuilds the game inside the worker)."""
    game = GameDefV2.from_dict(game_dict)
    return pg_game(game, deep_seed, shallow_seed, deep_seat,
                   deep_sims, shallow_sims)


def _tactical_worker(game_dict: dict, seed_p1: int, seed_p2: int) -> dict:
    """One tactical-vs-tactical guard rollout; returns only winner/plies
    (the guard-share inputs) to keep the IPC payload small."""
    game = GameDefV2.from_dict(game_dict)
    r = rollout_tactical(game, seed_p1, seed_p2)
    return {"winner": r["winner"], "plies": r["plies"]}


# ---------------------------------------------------------------------------
# Descriptor batch (inline; Phase C signal.alarm pattern — the batch is one
# atomic engine unit under BUILD_LOG #9)
# ---------------------------------------------------------------------------

def compute_descriptor_batch(game: GameDefV2, canon: str, batch_index: int,
                             batch_n: int) -> tuple[BatchResult, list[dict]]:
    """One seeded random-policy rollout batch -> BatchResult (+ raw rollouts
    for the one-time descriptor_row cross-check). Raises EvalTimeout /
    engine exceptions; the caller decides budget accounting."""
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
    """Exact-equality assert vs the locked descriptor_row (Phase B/C
    pattern); no-ops after the first successful check."""
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
    print("  [cross-check] descriptor_row exact-equality PASSED", flush=True)


# ---------------------------------------------------------------------------
# Pure helpers (unit-tested without the engine)
# ---------------------------------------------------------------------------

def t1_validity(t1: dict) -> str | None:
    """§4 step 3 [C13] transcription, PG era (BUILD_LOG #2): validity from
    the T1 games. None = valid, else the rejection reason."""
    if t1["non_draw_share"] < T1_MIN_NONDRAW_SHARE:
        return "draw_majority"
    if t1["mean_length"] < T1_MIN_MEAN_LENGTH:
        return "too_short"
    if math.isnan(t1["raw_pg"]):
        return "pg_nan"
    return None


def family_floored_pgs(stage0_records: list[dict]) -> dict[str, list[float]]:
    """BAR W population (§6): Stage-0 VALID genomes' floored T1-PG grouped
    by win-condition family."""
    out: dict[str, list[float]] = defaultdict(list)
    for rec in stage0_records:
        if rec["valid"]:
            out[rec["family"]].append(rec["t1"]["floored_pg"])
    return dict(out)


def family_table(fpgs: dict[str, list[float]], min_valid: int) -> dict:
    """Report-only per-family stats (§8 Stage-0 family table, UNSAMPLED
    marks). qualifying/live agree with bars.bar_w by construction (same
    percentile call, same floor); bar_w stays the authority for the bar."""
    rows: dict[str, dict] = {}
    for fam in FAMILIES:
        vals = fpgs.get(fam, [])
        row: dict = {"n_valid": len(vals), "qualifying": len(vals) >= min_valid}
        if row["qualifying"]:
            p90, p10 = np.percentile(vals, [90, 10])
            row.update(p10=float(p10), p90=float(p90),
                       spread=float(p90 - p10),
                       live=bool((p90 - p10) >= BAR_W_FLOOR))
        rows[fam] = row
    return rows


def select_bar_checkpoint(completed_r: list[int], completed_m: list[int],
                          reeval_at: tuple[int, ...], wall_hit: bool
                          ) -> tuple[str, int | str]:
    """§9 rule 2 salvage. Returns:
      ("final", B)        — both arms completed the terminal checkpoint,
                            no wall cap;
      ("salvage", ck)     — wall cap hit AFTER both arms passed the
                            penultimate registered checkpoint (150 at the
                            registered cadence, erratum #14): bars evaluate
                            at the last mutual checkpoint, B_effective = ck;
      ("incomplete", why) — otherwise (PROBE_INCOMPLETE).
    """
    final_ck = reeval_at[-1]
    if not wall_hit and final_ck in completed_r and final_ck in completed_m:
        return ("final", final_ck)
    if wall_hit:
        mutual = sorted(set(completed_r) & set(completed_m))
        salvage_min = reeval_at[-2] if len(reeval_at) >= 2 else reeval_at[-1]
        if mutual and mutual[-1] >= salvage_min:
            return ("salvage", mutual[-1])
        return ("incomplete", "wall_cap")
    return ("incomplete", "arms_under_budget")


def pre_slate_token(*, cal_i_pass: bool, incomplete: str | None,
                    bar_w_verdict: str, bar_h_verdict: str) -> str:
    """§9 precedence chain up to (not including) the slate, via the locked
    bars.decide_verdict. The slate stage runs later, manually, so a run
    whose chain reaches the slate records SLATE_PENDING — NOT a §9 token.
    (SLATE_INCOMPLETE is passed as the sentinel slate verdict purely
    because decide_verdict requires one; it is reachable only when
    BAR W ∧ BAR H pass, and is mapped to SLATE_PENDING here.)"""
    token = decide_verdict(cal_i_pass=cal_i_pass, incomplete=incomplete,
                           bar_w_verdict=bar_w_verdict,
                           bar_h_verdict=bar_h_verdict,
                           slate_verdict="SLATE_INCOMPLETE")
    return "SLATE_PENDING" if token == "SLATE_INCOMPLETE" else token


def heritability(m_log: list[dict]) -> dict:
    """§6 registered next-step inputs [C14] (reported only, §8): Pearson r
    of parent-at-selection vs child first-batch raw T1-PG, restricted to
    parents with floored PG > 0; timeout/error children excluded. The
    floored r is a diagnostic on the same restricted pairs."""
    pairs = [(r["parent_t1_raw"], r["child_t1_raw"]) for r in m_log
             if r.get("parent_t1_raw") is not None
             and r.get("child_t1_raw") is not None
             and max(r["parent_t1_raw"], 0.0) > 0.0]
    out = {"raw_r": None, "floored_r": None, "n_pairs": len(pairs)}
    if len(pairs) < 3:
        return out
    px, cy = zip(*pairs)
    if float(np.std(px)) > 0.0 and float(np.std(cy)) > 0.0:
        out["raw_r"] = float(np.corrcoef(px, cy)[0, 1])
    fx = [max(v, 0.0) for v in px]
    fy = [max(v, 0.0) for v in cy]
    if float(np.std(fx)) > 0.0 and float(np.std(fy)) > 0.0:
        out["floored_r"] = float(np.corrcoef(fx, fy)[0, 1])
    return out


def bar_h_inputs(arch_r: CampaignArchive, arch_m: CampaignArchive,
                 top_k: int = TOP_K) -> dict:
    """BAR H-PG inputs (§6): top-10 mean floored full-conv PG per arm;
    joint_cells = per jointly filled cell, whether M's elite STRICTLY
    beats R's on full_conv_mean_floored (same-elite ties from the shared
    Stage-0 init count as non-wins; reported separately). m/r elite counts
    are the FULL-CONV-RATED counts — an elite whose full-conv could not be
    measured cannot enter a top-10 mean."""
    def top_mean(arch):
        tops = arch.top_elites_by_full_conv(top_k)
        if len(tops) < top_k:
            return float("nan")
        return float(np.mean([e.full_conv_mean_floored for e in tops]))

    rated_r = sum(1 for e in arch_r.cells.values() if e.full_conv)
    rated_m = sum(1 for e in arch_m.cells.values() if e.full_conv)
    joint = sorted(set(arch_r.cells) & set(arch_m.cells))
    joint_wins = [bool(arch_m.cells[c].full_conv_mean_floored
                       > arch_r.cells[c].full_conv_mean_floored)
                  for c in joint]
    ties = sum(1 for c in joint
               if arch_m.cells[c].canon == arch_r.cells[c].canon)
    return dict(top10_r=top_mean(arch_r), top10_m=top_mean(arch_m),
                r_rated=rated_r, m_rated=rated_m,
                joint_n=len(joint), joint_wins=joint_wins,
                same_elite_ties=ties)


def load_cal_i(smoke: bool) -> dict:
    """§5: CAL-I is a pre-campaign artifact (cal_i.py). A real campaign
    refuses to start without it; smoke never reads it (and never emits a
    token, so the chain input is moot)."""
    if smoke:
        return {"verdict": "SKIPPED_SMOKE"}
    if not CAL_I_JSON.exists():
        raise SystemExit(
            "CAL-I artifact missing (experiments/rc2_campaign/cal_i.json). "
            "Prereg §5: run cal_i.py BEFORE any search spend.")
    return json.loads(CAL_I_JSON.read_text())


# ---------------------------------------------------------------------------
# Campaign driver
# ---------------------------------------------------------------------------

class Campaign:
    def __init__(self, out_dir: Path, smoke: bool, b_arm: int = B_ARM) -> None:
        self.out = Path(out_dir)
        self.smoke = smoke
        self.t0 = time.monotonic()
        self.incomplete: str | None = None
        self.wall_cap_hit = False
        self.eval_counters: dict[str, int] = defaultdict(int)

        if smoke:
            # Registered smoke range (seeds.RECORDED_STREAMS["smoke"]):
            # bases live INSIDE it so campaign bases provably avoid them.
            self.gen_seed_base = SMOKE_GEN_SEED_BASE
            self.arm_r_seed_base = SMOKE_ARM_R_SEED_BASE
            mut_seed = SMOKE_ARM_M_MUT_SEED
            sel_seed = SMOKE_ARM_M_SEL_SEED
            self.boot_seed = SMOKE_BOOT_SEED
            self.n_stage0 = self.n_stage1 = SMOKE_DESCRIPTOR_N
            self.t1_n, self.t1_deep, self.t1_shallow = (
                SMOKE_T1_N, SMOKE_T1_DEEP, SMOKE_T1_SHALLOW)
            self.full_n, self.full_deep, self.full_shallow = (
                SMOKE_FULL_N, SMOKE_FULL_DEEP, SMOKE_FULL_SHALLOW)
            self.bar_w_min_valid = SMOKE_BAR_W_MIN_VALID
            self.min_total_valid = SMOKE_MIN_TOTAL_VALID
            self.stage0_max_evals = SMOKE_STAGE0_MAX_EVALS
            self.stage0_max_attempts = SMOKE_STAGE0_MAX_ATTEMPTS
            self.guard_pairs = SMOKE_GUARD_PAIRS
            self.workers = SMOKE_WORKERS
            self.b_arm = SMOKE_B_ARM
            self.reeval_at = SMOKE_REEVAL_AT
            self.wall_cap = SMOKE_WALL_CAP
        else:
            # A --b-arm override (re-registered scopes only) must keep the
            # REGISTERED full-conv re-eval cadence: checkpoints every
            # REEVAL_STEP evals (§3), so b_arm must be a positive multiple
            # of it — otherwise the reeval_at derivation below silently
            # drops the terminal checkpoint and the §9 salvage arithmetic
            # (penultimate-checkpoint rule) breaks.
            if b_arm < REEVAL_STEP or b_arm % REEVAL_STEP != 0:
                raise SystemExit(
                    f"--b-arm must be a positive multiple of the registered "
                    f"full-conv re-eval cadence REEVAL_STEP={REEVAL_STEP} "
                    f"(§3: checkpoints every {REEVAL_STEP} evals/arm); "
                    f"got {b_arm}.")
            self.gen_seed_base = seeds.GEN_SEED_BASE
            self.arm_r_seed_base = seeds.ARM_R_SEED_BASE
            mut_seed = seeds.ARM_M_MUT_SEED
            sel_seed = seeds.ARM_M_SEL_SEED
            self.boot_seed = seeds.BOOT_SEED
            self.n_stage0, self.n_stage1 = N_STAGE0, N_STAGE1
            self.t1_n, self.t1_deep, self.t1_shallow = T1_N, T1_DEEP, T1_SHALLOW
            self.full_n, self.full_deep, self.full_shallow = (
                FULL_N, FULL_DEEP, FULL_SHALLOW)
            self.bar_w_min_valid = BAR_W_MIN_VALID
            self.min_total_valid = STAGE0_MIN_TOTAL_VALID
            self.stage0_max_evals = STAGE0_MAX_EVALS
            self.stage0_max_attempts = STAGE0_MAX_ATTEMPTS
            self.guard_pairs = N_PAIRS
            self.workers = WORKERS
            self.b_arm = b_arm
            # registered cadence: full-conv re-eval every 150 evals
            # (erratum #14; REEVAL_AT for the registered B=300)
            self.reeval_at = tuple(range(REEVAL_STEP, b_arm + 1, REEVAL_STEP))
            self.wall_cap = WALL_CAP_S

        self.descriptor_n = self.n_stage0
        # One generator instance hosts generate_game + quick_reject; game
        # content depends only on the per-call seed (Phase C verified:
        # identical canonical hashes across fresh instances).
        self.gen = GameGeneratorV2(GameConfig(), seed=0)
        # State filled by stages
        self.cal_i: dict = {}
        self.stage0_records: list[dict] = []
        self.stage0_progress = {"attempts": 0, "evaluated": 0}
        self.bar_w_result: dict | None = None
        self.bar_h_result: dict | None = None
        self.bar_h_detail: dict | None = None
        self.bar_mode: str | None = None
        self.b_effective: int | None = None
        self.archives: dict[str, CampaignArchive] = {}
        self.bar_archives: dict[str, CampaignArchive] | None = None
        self.init_counters: dict[str, dict] = {}
        self.arm_state: dict = {
            "R": {"evals": 0, "attempt": 0, "skips": 0, "log": []},
            "M": {"evals": 0, "attempt": 0, "skips": 0, "log": []},
        }
        self.checkpoints_completed: dict[str, list[int]] = {"R": [], "M": []}
        self.checkpoint_archives: dict[str, dict] = {"R": {}, "M": {}}
        self.guard_cache: dict[str, dict] = {}
        self.sel_rng = np.random.default_rng(sel_seed)
        self.mut_rng = np.random.default_rng(mut_seed)
        self.mut_op = MutationOperatorV2(EvolutionConfig(), self.mut_rng)
        self._pool: ProcessPoolExecutor | None = None

    # -- pool plumbing (BUILD_LOG #9) -----------------------------------

    @property
    def pool(self) -> ProcessPoolExecutor:
        if self._pool is None:
            self._pool = ProcessPoolExecutor(max_workers=self.workers)
        return self._pool

    def shutdown(self) -> None:
        if self._pool is not None:
            self._pool.shutdown(wait=False, cancel_futures=True)
            self._pool = None

    @staticmethod
    def _cancel(futs) -> None:
        for f in futs:
            f.cancel()

    def _collect(self, futs) -> list:
        """Per-unit future.result(timeout=180) (BUILD_LOG #9). On failure,
        cancels the genome's pending tasks and re-raises (EvalTimeout for a
        timed-out unit). A broken pool is dropped so it rebuilds lazily."""
        results = []
        try:
            for f in futs:
                results.append(f.result(timeout=EVAL_TIMEOUT_S))
        except FuturesTimeout as exc:
            self._cancel(futs)
            raise EvalTimeout(str(exc)) from exc
        except Exception as exc:
            self._cancel(futs)
            if isinstance(exc, BrokenProcessPool):
                self._pool = None
            raise
        return results

    # -- wall (search-phase cap, §9) ------------------------------------

    def wall_exceeded(self) -> bool:
        if time.monotonic() - self.t0 > self.wall_cap:
            self.incomplete = "wall_cap"
            return True
        return False

    # -- per-genome evaluation (§4 steps 2-3) ---------------------------

    def pg_batch_pooled(self, game: GameDefV2, canon: str, batch_index: int,
                        deep_sims: int, shallow_sims: int, n: int) -> dict:
        """T1 / full-conv PG batch with per-game pool fan-out; summarised
        identically to pg_eval.pg_batch (same seeds, same summary)."""
        gd = game.to_dict()
        futs = [self.pool.submit(_pg_game_worker, gd, ds, ss, seat,
                                 deep_sims, shallow_sims)
                for (ds, ss, seat) in pg_seeds(canon, batch_index, n)]
        return pg_summarise(self._collect(futs), n)

    def eval_genome_or_none(self, game: GameDefV2, canon: str, prefix: str,
                            cross_check: bool = False
                            ) -> tuple[BatchResult, tuple, dict] | None:
        """Both-evals-per-genome (BUILD_LOG #1): descriptor batch (cell
        placement, Phase C verbatim) + T1 PG batch (quality/validity/REACH
        draws). None on EVAL_TIMEOUT/EVAL_ERROR (counted; the caller
        consumes the budget slot)."""
        try:
            dbatch, rollouts = compute_descriptor_batch(
                game, canon, 0, self.descriptor_n)
        except EvalTimeout:
            self.eval_counters[f"{prefix}_eval_timeout"] += 1
            return None
        except Exception as exc:
            self.eval_counters[f"{prefix}_eval_error"] += 1
            print(f"  [eval_error] {canon[:12]} descriptor: "
                  f"{type(exc).__name__}: {exc}", flush=True)
            return None
        if cross_check:
            cross_check_against_descriptor_row(game, dbatch, rollouts)
        cell = cell_key(game, dbatch)
        try:
            t1 = self.pg_batch_pooled(game, canon, 0, self.t1_deep,
                                      self.t1_shallow, self.t1_n)
        except EvalTimeout:
            self.eval_counters[f"{prefix}_eval_timeout"] += 1
            return None
        except Exception as exc:
            self.eval_counters[f"{prefix}_eval_error"] += 1
            print(f"  [eval_error] {canon[:12]} T1: "
                  f"{type(exc).__name__}: {exc}", flush=True)
            return None
        return dbatch, cell, t1

    # -- guard stage (§4 step 4; BUILD_LOG #4/#9) -----------------------

    def guard_stage_pooled(self, game: GameDefV2, canon: str, family: str,
                           reach_draw_count: int, reach_n: int) -> dict:
        """guard_stage.run_guard_stage with the tactical rollouts fanned
        out over the pool. Veto pricing stays single-sourced in
        guard_stage._verdict_from_shares. Raises on unit timeout/error."""
        gd = game.to_dict()
        seed_pairs = [p for (m, s) in guard_pair_seeds(canon, self.guard_pairs)
                      for p in (m, s)]
        futs = [self.pool.submit(_tactical_worker, gd, p1, p2)
                for (p1, p2) in seed_pairs]
        records = self._collect(futs)
        dec_r, rush = rush_share(records)
        _, tilt = tilt_p1_share(records)
        out = _verdict_from_shares(rush, tilt, reach_draw_count, reach_n,
                                   family)
        out["decisive"] = dec_r
        out["reach_share"] = (reach_draw_count / reach_n if reach_n
                              else float("nan"))
        return out

    def _guard_fn_for(self, t1: dict):
        """guard_fn(game, canon, family) closure for CampaignArchive.offer:
        REACH input = the genome's own T1 draw count (§4). Cached per canon
        (deterministic: content-derived seeds + deterministic T1), so the
        same Stage-0 genome offered to both archives runs the rollouts
        once."""
        def guard_fn(game, canon, family):
            if canon in self.guard_cache:
                return self.guard_cache[canon]
            res = self.guard_stage_pooled(game, canon, family,
                                          reach_draw_count=t1["draws"],
                                          reach_n=t1["n"])
            self.guard_cache[canon] = res
            return res
        return guard_fn

    def offer_rec(self, arch: CampaignArchive, rec: dict) -> str:
        """Archive offer; a guard-stage unit timeout/engine error means the
        genome is NOT inserted (slot already consumed, counted — §2)."""
        try:
            return arch.offer(rec["game"], rec["canon"], rec["cell"],
                              rec["dbatch"], rec["t1"]["raw_pg"],
                              self._guard_fn_for(rec["t1"]))
        except EvalTimeout:
            self.eval_counters["guard_eval_timeout"] += 1
            return "guard_eval_timeout"
        except Exception as exc:
            self.eval_counters["guard_eval_error"] += 1
            print(f"  [guard_error] {rec['canon'][:12]}: "
                  f"{type(exc).__name__}: {exc}", flush=True)
            return "guard_eval_error"

    # -- full-conv ledger (§3, two ledgers never mixed) ------------------

    def _full_conv_fn(self, batch_index: int):
        """Full-conv ledger writer: raw PG at 256v16 n=48 (§3). None on
        EVAL_TIMEOUT/EVAL_ERROR — the elite keeps its ledger and the
        archive counts reeval_failed."""
        def fn(game, canon):
            try:
                return self.pg_batch_pooled(
                    game, canon, batch_index, self.full_deep,
                    self.full_shallow, self.full_n)["raw_pg"]
            except EvalTimeout:
                self.eval_counters["full_conv_timeout"] += 1
                return None
            except Exception as exc:
                self.eval_counters["full_conv_error"] += 1
                print(f"  [full_conv_error] {canon[:12]}: "
                      f"{type(exc).__name__}: {exc}", flush=True)
                return None
        return fn

    def ensure_full_conv(self, arch: CampaignArchive) -> None:
        """§3: an elite lacking a full-conv batch at bar time receives one
        before the bar is computed (reserved batch_index after the
        checkpoint indices; never collides with T1's 0)."""
        fn = self._full_conv_fn(FULL_CONV_BATCH_BASE + len(self.reeval_at))
        for cell in sorted(arch.cells):
            e = arch.cells[cell]
            if not e.full_conv:
                v = fn(e.game, e.canon)
                if v is not None:
                    e.full_conv.append(v)
                    self.eval_counters["full_conv_bar_topup"] += 1

    # -- CAL-I gate ------------------------------------------------------

    def cal_i_pass(self) -> bool:
        if self.smoke:
            return True   # smoke skips CAL-I and never emits a token
        return (self.cal_i or {}).get("verdict") == "PASS"

    # -- Stage 0 ----------------------------------------------------------

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
        print("=== Stage 0: fresh CAL-disjoint sample ===", flush=True)
        self.descriptor_n = self.n_stage0
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
                # Registered (Phase C carry-over): attempt caps exhausted
                # before quotas -> PROBE_INCOMPLETE (the eval-cap stop above
                # is a NORMAL stop).
                self.incomplete = "stage0_attempts_exhausted"
                break
            game = self.gen.generate_game(
                seed=self.gen_seed_base + self.stage0_progress["attempts"])
            self.stage0_progress["attempts"] += 1
            # Registered §2 exclusion: simultaneous-move genomes are
            # quick-rejected pre-eval (UCT instrument constraint; counted).
            if game.turn_structure.turn_type == "simultaneous":
                self.eval_counters["stage0_sim_excluded"] += 1
                continue
            if not self.gen.quick_reject(game):
                self.eval_counters["stage0_quick_reject"] += 1
                continue
            canon = game.canonical_hash()
            if canon in seen:
                self.eval_counters["stage0_dedup"] += 1
                continue
            seen.add(canon)
            res = self.eval_genome_or_none(game, canon, prefix="stage0",
                                           cross_check=True)
            self.stage0_progress["evaluated"] += 1
            family = game.win_condition.condition_type
            if res is None:
                # consumed budget; recorded so the canon stays "seen" for
                # the arms' dedup (registered: dedup vs everything
                # previously seen, including Stage-0 candidates)
                rec = {"game": game, "canon": canon, "family": family,
                       "dbatch": None, "cell": None, "t1": None,
                       "valid": False, "invalid_reason": "eval_failed"}
            else:
                dbatch, cell, t1 = res
                reason = t1_validity(t1)
                rec = {"game": game, "canon": canon, "family": family,
                       "dbatch": dbatch, "cell": cell, "t1": t1,
                       "valid": reason is None, "invalid_reason": reason}
                if reason is not None:
                    self.eval_counters[f"stage0_invalid_t1_{reason}"] += 1
            self.stage0_records.append(rec)
            ev = self.stage0_progress["evaluated"]
            if ev % CHECKPOINT_EVERY == 0:
                save_checkpoint(self, "stage0_running")
            if ev % 20 == 0:
                counts = {f: len(v)
                          for f, v in self._valid_by_family().items()}
                print(f"  evaluated {ev} "
                      f"(attempts {self.stage0_progress['attempts']}): "
                      f"valid by family {counts}", flush=True)

    def compute_bar_w(self) -> None:
        """BAR W-PG at Stage-0 close (§6; §9: preempts the arms)."""
        fpgs = family_floored_pgs(self.stage0_records)
        self.bar_w_result = bar_w(fpgs, min_valid=self.bar_w_min_valid)
        table = family_table(fpgs, self.bar_w_min_valid)
        for fam, row in table.items():
            if not row["qualifying"]:
                print(f"  family {fam}: UNSAMPLED ({row['n_valid']} valid)",
                      flush=True)
            else:
                print(f"  family {fam}: n={row['n_valid']} "
                      f"p90-p10={row['spread']:.4f} "
                      f"{'LIVE' if row['live'] else 'dead'}", flush=True)
        print(f"  BAR W-PG: {self.bar_w_result['n_live']} LIVE of "
              f"{self.bar_w_result['n_qualifying']} qualifying -> "
              f"{self.bar_w_result['verdict']}", flush=True)

    # -- Stage 1 ----------------------------------------------------------

    def init_archives(self) -> None:
        """Both arms' archives initialize from the same Stage-0 valid set
        (§2). Guard gates every would-enter offer (BUILD_LOG #4)."""
        for arm in ("R", "M"):
            arch = CampaignArchive()
            for rec in self.stage0_records:
                arch.mark_seen(rec["canon"])     # incl. invalid: budget spent
            for rec in self.stage0_records:
                if rec["valid"]:
                    self.offer_rec(arch, rec)
            self.archives[arm] = arch
            # snapshot so guard-veto counts split init vs arm phase (§8)
            self.init_counters[arm] = dict(arch.counters)
            print(f"  arm {arm} initialized: coverage {arch.coverage}, "
                  f"QD {arch.qd_score:.3f}", flush=True)

    def draw_candidate_R(self):
        arch = self.archives["R"]
        st = self.arm_state["R"]
        for _ in range(REDRAW_CAP):
            game = self.gen.generate_game(
                seed=self.arm_r_seed_base + st["attempt"])
            st["attempt"] += 1
            if game.turn_structure.turn_type == "simultaneous":
                self.eval_counters["R_sim_excluded"] += 1
                continue
            if not self.gen.quick_reject(game):
                self.eval_counters["R_quick_reject"] += 1
                continue
            canon = game.canonical_hash()
            if arch.is_seen(canon):
                self.eval_counters["R_dedup"] += 1
                continue
            return game, canon, None
        return None

    def draw_candidate_M(self):
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
            if child.turn_structure.turn_type == "simultaneous":
                self.eval_counters["M_sim_excluded"] += 1
                continue
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
              f"({'random' if arm == 'R' else 'MAP-Elites'}) ===", flush=True)
        self.descriptor_n = self.n_stage1
        arch = self.archives[arm]
        st = self.arm_state[arm]
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
            res = self.eval_genome_or_none(game, canon, prefix=arm)
            st["evals"] += 1
            t1 = cell = None
            if res is None:
                outcome = "eval_failed"
            else:
                dbatch, cell, t1 = res
                reason = t1_validity(t1)
                if reason is not None:
                    self.eval_counters[f"{arm}_invalid_t1_{reason}"] += 1
                    outcome = f"t1_invalid_{reason}"
                else:
                    outcome = self.offer_rec(arch, {
                        "game": game, "canon": canon, "cell": cell,
                        "dbatch": dbatch, "t1": t1})
            entry = {
                "step": st["evals"], "child_canon": canon,
                "child_t1_raw": (t1["raw_pg"] if t1 else None),
                "child_t1_floored": (t1["floored_pg"] if t1 else None),
                "cell": ("/".join(map(str, cell)) if cell else None),
                "outcome": outcome,
            }
            if arm == "M":
                entry["parent_canon"] = parent.canon
                entry["parent_t1_raw"] = parent.t1_raw
                entry["parent_t1_floored"] = parent.t1_floored
            st["log"].append(entry)
            if st["evals"] in self.reeval_at:
                ordinal = self.reeval_at.index(st["evals"])
                print(f"  [{arm}] full-conv re-eval at {st['evals']} evals "
                      f"(coverage {arch.coverage})", flush=True)
                arch.reeval_full_conv(
                    self._full_conv_fn(FULL_CONV_BATCH_BASE + ordinal))
                if st["evals"] not in self.checkpoints_completed[arm]:
                    self.checkpoints_completed[arm].append(st["evals"])
                # archive snapshot: the §9 salvage rule evaluates bars AT
                # the last mutual checkpoint, so the state must survive
                # further evals
                self.checkpoint_archives[arm][str(st["evals"])] = \
                    arch.to_dict()
                save_checkpoint(self, f"arm_{arm}_running")
            if st["evals"] % CHECKPOINT_EVERY == 0:
                save_checkpoint(self, f"arm_{arm}_running")
                print(f"  [{arm}] {st['evals']}/{self.b_arm} evals, "
                      f"coverage {arch.coverage}, QD {arch.qd_score:.3f}",
                      flush=True)

    # -- bars + pre-slate token ------------------------------------------

    def finalize_bars(self) -> None:
        """BAR H-PG (§6) at final budget or the §9 salvage checkpoint."""
        if self.incomplete is None:
            # Strict conformance: the search-phase cap is re-checked at
            # emission (re-eval/bar loops between budget steps cannot be
            # interrupted, so the final crossing is caught here).
            self.wall_exceeded()
        self.wall_cap_hit = self.incomplete == "wall_cap"
        if self.incomplete is not None and not self.wall_cap_hit:
            return    # non-wall incompleteness: chain short-circuits
        mode, val = select_bar_checkpoint(
            self.checkpoints_completed["R"], self.checkpoints_completed["M"],
            self.reeval_at, self.wall_cap_hit)
        self.bar_mode = mode
        if mode == "incomplete":
            if self.incomplete is None:
                self.incomplete = val
            return
        self.b_effective = val
        if mode == "salvage":
            # §9: bars evaluate at the last mutual checkpoint,
            # B_effective reported; the wall-cap incompleteness is salvaged.
            self.incomplete = None
            arch_r = CampaignArchive.from_dict(
                self.checkpoint_archives["R"][str(val)], GameDefV2.from_dict)
            arch_m = CampaignArchive.from_dict(
                self.checkpoint_archives["M"][str(val)], GameDefV2.from_dict)
        else:
            arch_r, arch_m = self.archives["R"], self.archives["M"]
        self.ensure_full_conv(arch_r)
        self.ensure_full_conv(arch_m)
        self.bar_archives = {"R": arch_r, "M": arch_m}
        inputs = bar_h_inputs(arch_r, arch_m)
        self.bar_h_detail = {k: v for k, v in inputs.items()
                             if k != "joint_wins"}
        self.bar_h_detail["joint_m_wins"] = sum(inputs["joint_wins"])
        self.bar_h_result = bar_h(inputs["top10_m"], inputs["top10_r"],
                                  inputs["m_rated"], inputs["r_rated"],
                                  joint_cells=inputs["joint_wins"])
        print(f"  BAR H-PG [{mode}, B_effective={val}]: "
              f"{self.bar_h_result['metric']} {self.bar_h_result['detail']} "
              f"-> {self.bar_h_result['verdict']}", flush=True)

    def pre_slate_token_now(self) -> str:
        return pre_slate_token(
            cal_i_pass=self.cal_i_pass(),
            incomplete=self.incomplete,
            bar_w_verdict=(self.bar_w_result or {}).get(
                "verdict", "PROBE_INCOMPLETE"),
            bar_h_verdict=(self.bar_h_result or {}).get(
                "verdict", "PROBE_INCOMPLETE"),
        )


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def write_reports(p: Campaign, token: str) -> None:
    out = p.out
    out.mkdir(parents=True, exist_ok=True)
    boot_rng = np.random.default_rng(p.boot_seed)
    bar_archs = p.bar_archives or p.archives

    # ---- CSV: stage0 + final elites ----
    with open(out / "campaign_results.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["section", "arm", "canon", "family", "cell",
                    "t1_raw", "t1_floored", "non_draw_share", "mean_length",
                    "full_conv_mean_floored", "n_full_conv",
                    "valid", "outcome"])
        for rec in p.stage0_records:
            t1 = rec["t1"]
            if t1 is None:
                w.writerow(["stage0", "", rec["canon"][:16], rec["family"],
                            "", "", "", "", "", "", "", False, "eval_failed"])
                continue
            cell = rec["cell"]
            w.writerow(["stage0", "", rec["canon"][:16], rec["family"],
                        "/".join(map(str, cell)) if cell else "",
                        f"{t1['raw_pg']:.6f}", f"{t1['floored_pg']:.6f}",
                        f"{t1['non_draw_share']:.4f}",
                        f"{t1['mean_length']:.2f}", "", "",
                        rec["valid"], rec["invalid_reason"] or ""])
        for arm, arch in sorted(bar_archs.items()):
            for cell in sorted(arch.cells):
                e = arch.cells[cell]
                fc = e.full_conv_mean_floored
                w.writerow(["final_elite", arm, e.canon[:16], cell[0],
                            "/".join(map(str, cell)),
                            f"{e.t1_raw:.6f}", f"{e.t1_floored:.6f}", "", "",
                            "" if math.isnan(fc) else f"{fc:.6f}",
                            len(e.full_conv), "", ""])

    # ---- arm logs ----
    for arm in ("R", "M"):
        log = p.arm_state[arm]["log"]
        fieldnames = sorted({k for row in log for k in row}) or ["step"]
        with open(out / f"arm_{arm}_log.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(log)

    # ---- markdown report ----
    lines: list[str] = []
    title = "RC2 campaign — results"
    if p.smoke:
        title += " (SMOKE RUN — recorded smoke seed range, NOT a verdict)"
    lines.append(f"# {title}\n")
    lines.append(
        f"Protocol per experiments/rc2_campaign/PREREGISTRATION.md (locked) "
        f"+ BUILD_LOG #1-#9: B={p.b_arm}/arm, full-conv re-eval at "
        f"{tuple(p.reeval_at)}, T1 {p.t1_deep}v{p.t1_shallow} n={p.t1_n}, "
        f"full-conv {p.full_deep}v{p.full_shallow} n={p.full_n}, descriptor "
        f"n {p.n_stage0}/{p.n_stage1}, guard {p.guard_pairs} mirrored pairs, "
        f"{p.workers} workers, per-unit timeout {EVAL_TIMEOUT_S}s, "
        f"search-phase wall cap {p.wall_cap / 3600:.1f}h.\n")

    lines.append("## CAL-I (pre-campaign instrument gate, §5)\n")
    v = (p.cal_i or {}).get("verdict", "MISSING")
    lines.append(f"- cal_i.json verdict: **{v}**")
    if p.cal_i.get("verdict_detail"):
        lines.append(f"- detail: {p.cal_i['verdict_detail']}")
    lines.append("")

    lines.append("## Stage 0 — BAR W-PG (within-family validity)\n")
    lines.append(f"Attempts {p.stage0_progress['attempts']}, evaluated "
                 f"{p.stage0_progress['evaluated']}, valid "
                 f"{sum(1 for r in p.stage0_records if r['valid'])}.\n")
    fpgs = family_floored_pgs(p.stage0_records)
    table = family_table(fpgs, p.bar_w_min_valid)
    lines.append(f"| family | n_valid | p10 | p90 | p90-p10 | LIVE "
                 f"(floor {BAR_W_FLOOR}) |")
    lines.append("|---|---:|---:|---:|---:|---|")
    for fam in FAMILIES:
        row = table[fam]
        if not row["qualifying"]:
            lines.append(f"| {fam} | UNSAMPLED ({row['n_valid']}) | | | | |")
        else:
            lines.append(
                f"| {fam} | {row['n_valid']} | {row['p10']:.4f} | "
                f"{row['p90']:.4f} | {row['spread']:.4f} | "
                f"{'YES' if row['live'] else 'no'} |")
    if p.bar_w_result:
        lines.append(f"\nBAR W-PG: {p.bar_w_result['n_live']} LIVE of "
                     f"{p.bar_w_result['n_qualifying']} qualifying -> "
                     f"**{p.bar_w_result['verdict']}**\n")
    else:
        lines.append("\nBAR W-PG: not computed (Stage 0 did not close)\n")

    lines.append("## Stage 1 — BAR H-PG (matched-budget search value)\n")
    if p.bar_mode:
        lines.append(f"Bar evaluation mode: **{p.bar_mode}**"
                     + (f", B_effective={p.b_effective}"
                        if p.b_effective else "") + ".\n")
    lines.append("| arm | evals | coverage | QD-score (floored T1) | "
                 "top-10 mean floored full-conv [95% CI] | "
                 "full-conv-rated | skips |")
    lines.append("|---|---:|---:|---:|---|---:|---:|")
    for arm in ("R", "M"):
        arch = bar_archs.get(arm)
        if arch is None:
            lines.append(f"| {arm} | not run | | | | | |")
            continue
        tops = arch.top_elites_by_full_conv(TOP_K)
        vals = [e.full_conv_mean_floored for e in tops]
        if len(tops) >= TOP_K:
            res = [float(np.mean(boot_rng.choice(vals, size=len(vals),
                                                 replace=True)))
                   for _ in range(N_BOOT)]
            lo = float(np.percentile(res, CI_LO))
            hi = float(np.percentile(res, CI_HI))
            mean_str = f"{np.mean(vals):.4f} [{lo:.4f}, {hi:.4f}]"
        else:
            mean_str = f"only {len(tops)} rated elites"
        rated = sum(1 for e in arch.cells.values() if e.full_conv)
        lines.append(f"| {arm} | {p.arm_state[arm]['evals']} | "
                     f"{arch.coverage} | {arch.qd_score:.3f} | {mean_str} | "
                     f"{rated} | {p.arm_state[arm]['skips']} |")
    if p.bar_h_result:
        d = p.bar_h_detail or {}
        lines.append(f"\nBAR H-PG ({p.bar_h_result['metric']}): "
                     f"{p.bar_h_result['detail']} -> "
                     f"**{p.bar_h_result['verdict']}**")
        lines.append(f"- R_top10 (saturation watch, switch at 0.40): "
                     f"{d.get('top10_r', float('nan')):.4f}")
        lines.append(f"- jointly filled cells: {d.get('joint_n', 0)}; "
                     f"M strict wins {d.get('joint_m_wins', 0)}; "
                     f"same-elite ties {d.get('same_elite_ties', 0)}")
    else:
        lines.append("\nBAR H-PG: not computed "
                     f"({p.incomplete or 'arms not run'})")
    lines.append("")
    if "R" in bar_archs and "M" in bar_archs:
        for arm in ("R", "M"):
            tops = bar_archs[arm].top_elites_by_full_conv(TOP_K)
            fams: dict[str, int] = defaultdict(int)
            for e in tops:
                fams[e.cell[0]] += 1
            lines.append(f"Arm {arm} top-10 family composition: "
                         f"{dict(sorted(fams.items()))}.")
        h = heritability(p.arm_state["M"]["log"])
        fmt = lambda r: "n/a" if r is None else format(r, ".3f")  # noqa: E731
        lines.append(f"\nParent-child T1-PG heritability (arm M, parents "
                     f"floored>0): raw r = {fmt(h['raw_r'])}, floored r "
                     f"(diagnostic) = {fmt(h['floored_r'])} over "
                     f"{h['n_pairs']} pairs.\n")

    lines.append("## Full-conv re-eval ledger (repricing diagnostic)\n")
    for arm in ("R", "M"):
        arch = bar_archs.get(arm)
        if arch is None:
            continue
        ranges = [max(e.full_conv) - min(e.full_conv)
                  for e in arch.cells.values() if len(e.full_conv) >= 2]
        if ranges:
            lines.append(f"- arm {arm}: {len(ranges)} multi-batch elites, "
                         f"max full-conv range {max(ranges):.4f}, "
                         f"mean {np.mean(ranges):.4f}")
        else:
            lines.append(f"- arm {arm}: no multi-batch elites")
    lines.append("")

    lines.append("## Counters\n")
    for k in sorted(p.eval_counters):
        lines.append(f"- {k}: {p.eval_counters[k]}")
    for arm, arch in sorted(p.archives.items()):
        init = p.init_counters.get(arm, {})
        total = arch.counters
        init_str = ", ".join(f"{k}={v}" for k, v in sorted(init.items()) if v)
        arm_str = ", ".join(
            f"{k}={v - init.get(k, 0)}" for k, v in sorted(total.items())
            if v - init.get(k, 0))
        lines.append(f"- arm {arm} archive (stage0 init): {init_str or '—'}")
        lines.append(f"- arm {arm} archive (arm phase): {arm_str or '—'}")
    lines.append(f"- wall time: {(time.monotonic() - p.t0) / 60:.1f} min")
    if p.wall_cap_hit:
        lines.append(f"- wall cap HIT"
                     + (f"; salvaged at B_effective={p.b_effective} (§9)"
                        if p.bar_mode == "salvage" else ""))
    if p.incomplete:
        lines.append(f"- INCOMPLETE: {p.incomplete}")
    lines.append("")

    lines.append("## Pre-slate verdict\n")
    lines.append(
        "This runner stops at slate-ready. SLATE_PENDING is recorded when "
        "BAR W ∧ BAR H pass and is NOT a §9 token — the slate stage (§7) "
        "runs later, manually, and emits the §9 slate verdicts "
        "(GO / GO-PARTIAL / NO-GO / CAMPAIGN_UNRESOLVED / SLATE_INCOMPLETE). "
        "§9 tokens PROBE_INVALID / PROBE_INCOMPLETE / ARCHIVE_KILL / "
        "SEARCH_NEUTRAL are emitted here as usual via bars.decide_verdict.\n")
    if p.smoke:
        lines.append(f"SMOKE RUN — would-be pre-slate token "
                     f"(not registered): {token}")
    else:
        lines.append(f"PRE-SLATE TOKEN: **{token}**")
    lines.append("")

    (out / "campaign_results.md").write_text("\n".join(lines))
    print(f"\nReports written to {out}/campaign_results.{{md,csv}}",
          flush=True)


# ---------------------------------------------------------------------------
# Checkpointing (atomic tmp+rename; every 25 evals + stage boundaries)
# ---------------------------------------------------------------------------

def _serialize_stage0(rec: dict) -> dict:
    return {"game": rec["game"].to_dict(), "canon": rec["canon"],
            "family": rec["family"],
            "dbatch": rec["dbatch"].to_dict() if rec["dbatch"] else None,
            "cell": list(rec["cell"]) if rec["cell"] else None,
            "t1": rec["t1"], "valid": rec["valid"],
            "invalid_reason": rec["invalid_reason"]}


def _deserialize_stage0(rec: dict) -> dict:
    return {"game": GameDefV2.from_dict(rec["game"]), "canon": rec["canon"],
            "family": rec["family"],
            "dbatch": (BatchResult.from_dict(rec["dbatch"])
                       if rec["dbatch"] else None),
            "cell": tuple(rec["cell"]) if rec["cell"] else None,
            "t1": rec["t1"], "valid": rec["valid"],
            "invalid_reason": rec["invalid_reason"]}


def save_checkpoint(p: Campaign, stage: str) -> None:
    ck = {
        "stage": stage,
        "smoke": p.smoke,
        "b_arm": p.b_arm,
        "cal_i": p.cal_i,
        "incomplete": p.incomplete,
        "wall_cap_hit": p.wall_cap_hit,
        "bar_mode": p.bar_mode,
        "b_effective": p.b_effective,
        "bar_w_result": p.bar_w_result,
        "bar_h_result": p.bar_h_result,
        "bar_h_detail": p.bar_h_detail,
        "eval_counters": dict(p.eval_counters),
        "stage0_progress": p.stage0_progress,
        "stage0_records": [_serialize_stage0(r) for r in p.stage0_records],
        "archives": {arm: a.to_dict() for arm, a in p.archives.items()},
        "init_counters": p.init_counters,
        "arm_state": p.arm_state,
        "checkpoints_completed": p.checkpoints_completed,
        "checkpoint_archives": p.checkpoint_archives,
        "sel_rng": p.sel_rng.bit_generator.state,
        "mut_rng": p.mut_rng.bit_generator.state,
        "cross_checked": _CROSS_CHECKED,
        "elapsed": time.monotonic() - p.t0,
    }
    tmp = p.out / "checkpoint.json.tmp"
    tmp.write_text(json.dumps(ck))
    tmp.rename(p.out / "checkpoint.json")


def load_checkpoint(p: Campaign) -> str:
    global _CROSS_CHECKED
    ck = json.loads((p.out / "checkpoint.json").read_text())
    if ck["smoke"] != p.smoke:
        raise SystemExit("checkpoint smoke flag mismatch")
    if ck.get("b_arm", B_ARM) != p.b_arm:
        raise SystemExit("checkpoint b_arm mismatch")
    p.cal_i = ck["cal_i"]
    p.incomplete = ck["incomplete"]
    p.wall_cap_hit = ck["wall_cap_hit"]
    p.bar_mode = ck["bar_mode"]
    p.b_effective = ck["b_effective"]
    p.bar_w_result = ck["bar_w_result"]
    p.bar_h_result = ck["bar_h_result"]
    p.bar_h_detail = ck["bar_h_detail"]
    p.eval_counters.update(ck["eval_counters"])
    p.stage0_progress = ck["stage0_progress"]
    p.stage0_records = [_deserialize_stage0(r) for r in ck["stage0_records"]]
    p.archives = {arm: CampaignArchive.from_dict(a, GameDefV2.from_dict)
                  for arm, a in ck["archives"].items()}
    p.init_counters = ck["init_counters"]
    p.arm_state = ck["arm_state"]
    p.checkpoints_completed = ck["checkpoints_completed"]
    p.checkpoint_archives = ck["checkpoint_archives"]
    p.sel_rng.bit_generator.state = ck["sel_rng"]
    p.mut_rng.bit_generator.state = ck["mut_rng"]
    _CROSS_CHECKED = ck["cross_checked"]
    p.t0 = time.monotonic() - ck["elapsed"]
    return ck["stage"]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    # [C1] hard disjointness assert against ALL recorded streams — the
    # runner refuses to start on overlap (validates the REGISTERED campaign
    # constants; runs in smoke mode too).
    seeds.assert_disjoint()

    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--b-arm", type=int, default=B_ARM)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    out = Path(args.out) if args.out else (
        HERE / "smoke" if args.smoke else HERE)
    out.mkdir(parents=True, exist_ok=True)
    p = Campaign(out, smoke=args.smoke, b_arm=args.b_arm)
    p.cal_i = load_cal_i(args.smoke)

    stage = "start"
    if args.resume and (out / "checkpoint.json").exists():
        stage = load_checkpoint(p)
        print(f"Resumed from checkpoint at stage '{stage}'", flush=True)
        if stage == "terminal":
            raise SystemExit(
                "run already reached a terminal verdict — see "
                f"{out / 'campaign_results.md'}")

    def finish_early() -> None:
        token = p.pre_slate_token_now()
        write_reports(p, token)
        save_checkpoint(p, "terminal")
        label = ("SMOKE would-be pre-slate token (not registered)"
                 if p.smoke else "PRE-SLATE TOKEN")
        print(f"\n{label}: {token}", flush=True)

    try:
        if stage == "start":
            print(f"CAL-I: {p.cal_i.get('verdict')}", flush=True)
            stage = "cal_checked"
            save_checkpoint(p, stage)
            # Early exits (suppressed in smoke so every path is exercised)
            if not p.smoke and not p.cal_i_pass():
                finish_early()
                return

        if stage in ("cal_checked", "stage0_running"):
            p.run_stage0()
            p.compute_bar_w()
            stage = "stage0_done"
            save_checkpoint(p, stage)
            # §9: BAR W is decided at Stage-0 close and preempts the arms.
            if not p.smoke and (p.incomplete
                                or p.bar_w_result["verdict"] != "PASS"):
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

        p.finalize_bars()
        token = p.pre_slate_token_now()
        write_reports(p, token)
        save_checkpoint(p, "terminal")
        label = ("SMOKE would-be pre-slate token (not registered)"
                 if p.smoke else "PRE-SLATE TOKEN")
        print(f"\n{label}: {token}", flush=True)
    finally:
        p.shutdown()


if __name__ == "__main__":
    main()
