# RC2 Campaign — build decisions log (pre-data, review-logged per §10)

The prereg (`PREREGISTRATION.md`, locked `72890a0`) pins every constant and bar
but leaves a handful of implementation-level choices open. Each is resolved
below from the spec + `PANEL_FINDINGS.md`, with its basis. Per §10 ("post-lock
code changes must be pre-data and review-logged"), these are recorded BEFORE any
campaign data and **await owner ratification before Task 1 touches code.**

Plan: `docs/superpowers/plans/2026-07-02-rc2-campaign-build.md`.

| # | Decision | Basis | Weight | Status |
|---|----------|-------|--------|--------|
| 1 | **Cell placement = Phase-C descriptor batch, verbatim.** Cell stays `(family, interaction_bin, length_bin)` from `qd_archive.cell_key` over a random-policy `run_protocol` batch; only the displacement/quality key swaps to floored T1-PG. Each genome eval runs BOTH a descriptor batch (cell) and a T1 eval (quality/validity/REACH). | `PANEL_FINDINGS.md:352/366` treat cell machinery as `qd_archive.py` verbatim; design doc "descriptor_row cells… Phase C verbatim." | **Methodological** | RECOMMENDED — pending |
| 2 | **Validity from the T1 games** (non-draw T1 share ≥0.50, mean T1 length ≥6, T1-PG non-nan), not the descriptor batch. | Prereg §4 [C13] "PG era" transcription. | Low | RECOMMENDED — pending |
| 3 | **Content-seed expansion.** T1 batch `b` derives 24 games from `rng = np.random.default_rng(eval_seed_for(canon, b))`; game `j`: `deep_seed, shallow_seed = rng.integers(0, 2**31-1, size=2)`; `deep_seat = 0 if j<12 else 1`. Anchor streams 42–47 stay CAL-only. | Prereg §2 pins the master formula `eval_seed_for`; the 24-game expansion is the free detail. | Low | RECOMMENDED — pending |
| 4 | **Guard stage gates EVERY insertion** — empty cell (first occupancy) OR strict improvement — not only "beats an existing incumbent." | Safety: a first-occupancy elite can reach the slate, so must pass RUSH/TILT/REACH. §4's "beats the incumbent" reads as "would enter the archive." | **Methodological** | RECOMMENDED — pending |
| 5 | **`rollout_tactical` lifted to `metrics/guard_probe.py`**; `rc2_descriptor_v2/run_probe.py` re-imports it (back-compat: `cal_g.py` still works). `TacticalAgent` already in `metrics/tactical_agent.py`. | §4 build item "rollout_tactical/TacticalAgent lifted into metrics/." | Low | RECOMMENDED — pending |
| 6 | **Net-free UCT reused from `anchor_calibration.py`** (do not refactor that locked §0 file) so the campaign T1 instrument is provably identical to the one CAL-I validates. `eval_seed_for` reused from `rc2_archive/run_probe.py`. | Instrument-identity: CAL-I validates instrument A; the campaign must run the same A. | Low | RECOMMENDED — pending |
| 7 | **T1 eval-count matching is a structural no-op** (every genome's T1-PG is a single n=24 batch → incumbent/challenger pooled_n always match). Re-eval adds full-conv batches to the SEPARATE full-conv ledger, never more T1 batches. | Prereg §3: two ledgers "never mixed"; re-eval writes full-conv only. | Low | RECOMMENDED — pending |

## Errata (pre-data, review-logged)

| # | Decision | Basis | Weight | Status |
|---|----------|-------|--------|--------|
| 8 | **Stream SPAN = 1_000_000** (plan originally said 4_000_000). The 4M span falsely overlapped the LOCKED campaign gen base (19M) with Phase C R2's recorded 17M stream — caught pre-data by the Task-3 disjointness assert itself. Prereg bases (19M×{1..5}) are locked and cannot move; SPAN was a plan-invented free variable. 1M is honest (real consumption ≤ ~30k seeds/stream: 3000-attempt Stage-0, ≤600×50 arm draws) and matches the repo's de-facto spacing precedent (recorded streams sit as close as 51M vs 52M). | Task-3 build blocker 2026-07-02; no prereg constant touched. | Low (plan errata, single valid fix) | APPLIED |

| 9 | **Per-eval timeout granularity: 180 s applies per atomic engine-touching unit** — each UCT game (via `future.result(timeout=180)`) and each descriptor batch — NOT per genome-stage aggregate. Any unit timing out → EVAL_TIMEOUT for the genome (consumes the budget slot, excluded from archives/bars, counted, per §2). Also fixes the §2-implied worker model: per-genome T1/guard games fan out over a persistent 7-worker pool (design doc "7 workers"); the archive/offer loop stays sequential (offers are order-dependent registered semantics). | §2's "per-eval wall timeout 180 s" is under-pinned at implementation level; the per-genome-aggregate reading would mass-timeout at the MEASURED T1 cost (~5.3 CPU-min/genome, `cost_tiering.json` — the §0-locked instrument), i.e. it contradicts the validated instrument, so the pathology-guard (per-unit) reading is the only coherent one. Phase C's sequential `signal.alarm` pattern doesn't compose with a pool; `future.result(timeout=)` preserves the guard. | **Methodological (implementation-level, single coherent reading)** | APPLIED (pre-data, review-logged) |

| 10 | **Near-dup screen floor pinned: L2 distance over `(interaction_rate, length_frac)` — the two continuous cell descriptors — with floor = 0.02.** The §7 screen fires iff identical family AND identical board/topology AND (descriptor L2 < 0.02 OR rules-diff limited to komi/max_turns fields). | Prereg §7 references "the pinned floor" but the lock never pins the number. 0.02 < half the smallest interaction bin width (0.05/2), so the screen can only fire on games whose descriptors are within re-binning noise of identical — true near-dups — never on genuinely different dynamics. Conservative by construction; preconditioned on identical family + board/topology. Pre-data (no campaign data exists). | **Methodological (constant pin, conservative)** | APPLIED (pre-data, review-logged) |

| 11 | **REACH-v3 polarity fixed: FIRED = VETO.** The PLAN (Task 4 brief text) inverted the registered polarity — it read a firing REACH (draws ≥ 5/24) as *keeping* a threshold genome and vetoed on draws < 5. Faithfully implemented + brief-verified per-task as written; caught PRE-DATA by the final whole-branch review. Fixed to fire→veto: a threshold genome with ≥ 5/24 of its own T1 games ending winner-None (the S2-style draw-pathology CAL-R validates — S2 fires 10/24, e1453 silent 1/24) is VETOED, exactly like RUSH/TILT. The comparison lives only in `guard_stage._verdict_from_shares` (run_campaign's pooled path imports it), so the flip propagates everywhere; direct `run_guard_stage` tests added each side of 5/24. | PREREGISTRATION.md §4 [C8]; cal_r.py bars B1/B2; PANEL_FINDINGS C8. Final whole-branch review 2026-07-02; registered constant (5/24) untouched. | **Critical errata, pre-data** | APPLIED |

## Open questions asked of the owner (2026-07-02)

- **Decision #4 (guard scope)** — recommended: gate every insertion. *RATIFIED as recommended.*
- **Decision #1 (descriptor batch retained for cells)** — recommended per panel; effectively spec-forced. *RATIFIED as recommended.*

## Owner ratification

- Date: 2026-07-02
- Decisions ratified as recommended: **ALL SEVEN (#1–#7)**, owner's words: "ratify all as recommended".
- Adjustments: none.
- Execution mode: subagent-driven build (fresh implementer per task + task review + final whole-branch review).
