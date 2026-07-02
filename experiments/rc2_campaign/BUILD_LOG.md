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

## Open questions asked of the owner (2026-07-02)

- **Decision #4 (guard scope)** — recommended: gate every insertion. *RATIFIED as recommended.*
- **Decision #1 (descriptor batch retained for cells)** — recommended per panel; effectively spec-forced. *RATIFIED as recommended.*

## Owner ratification

- Date: 2026-07-02
- Decisions ratified as recommended: **ALL SEVEN (#1–#7)**, owner's words: "ratify all as recommended".
- Adjustments: none.
- Execution mode: subagent-driven build (fresh implementer per task + task review + final whole-branch review).
