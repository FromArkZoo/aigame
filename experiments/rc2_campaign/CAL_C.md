# CAL-C — pre-campaign cost projection  [§5(b)]

RC2 §5(b) pre-campaign gate. 20 fresh CAL genomes (seed base 19500000 = GEN_SEED_BASE + 500000) timed end-to-end through the FULL per-genome pipeline (descriptor batch + T1 + guard stage + full-conv re-eval), projected over the registered campaign shape (Stage-0 240 evals + 2 arms x 600 + 4 full-conv checkpoints) across 7 workers vs the 8.0h search-phase cap.

Draw: 39 attempts -> 20 accepted.

Timed: 20 of 20 genomes attempted; 0 failed.

## Per-genome timings (s)

| # | canon | family | descriptor | T1 | guard | full-conv | total |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | a8fb98011492ced4 | territory | 0.36 | 15.13 | 0.05 | 49.60 | 65.14 |
| 2 | 6bd34c12fb530833 | elimination | 0.01 | 0.06 | 0.01 | 0.24 | 0.32 |
| 3 | 854343fa18ac322b | threshold | 0.33 | 12.37 | 0.08 | 48.06 | 60.84 |
| 4 | a40063361629a16a | connection | 0.22 | 30.73 | 0.13 | 120.41 | 151.49 |
| 5 | d2ab58bc9d38b350 | threshold | 0.31 | 11.42 | 0.07 | 48.49 | 60.29 |
| 6 | b0f507798325ec9f | connection | 0.56 | 61.53 | 0.15 | 245.53 | 307.77 |
| 7 | e8bf5c6162b33ee2 | connection | 0.60 | 22.84 | 0.32 | 59.94 | 83.70 |
| 8 | 771f02050ad35466 | territory | 0.69 | 169.80 | 1.33 | 734.15 | 905.97 |
| 9 | 09b4dd288bfa63c1 | threshold | 0.47 | 46.65 | 0.18 | 262.94 | 310.25 |
| 10 | cf2c77a30ff9977a | threshold | 0.02 | 0.55 | 0.01 | 1.84 | 2.42 |
| 11 | c646eba40b36bfff | connection | 0.85 | 9.53 | 0.18 | 36.54 | 47.10 |
| 12 | 9e242fe1f7120b40 | elimination | 0.03 | 0.14 | 0.00 | 1.04 | 1.22 |
| 13 | b08aa82d660b90b0 | connection | 0.40 | 56.55 | 0.43 | 197.39 | 254.77 |
| 14 | 46e0ae7f5d9114e9 | threshold | 0.93 | 58.42 | 0.74 | 217.42 | 277.50 |
| 15 | f2c15c4fca4fed9e | territory | 1.24 | 29.38 | 0.55 | 105.41 | 136.58 |
| 16 | bcd7d96be9997635 | connection | 0.86 | 41.30 | 0.26 | 112.30 | 154.72 |
| 17 | 74bc2069a895817b | connection | 0.30 | 10.98 | 0.09 | 31.24 | 42.61 |
| 18 | 38e266f86ce17a8c | connection | 1.53 | 102.29 | 1.66 | 324.04 | 429.51 |
| 19 | 522f0befa393e3b7 | connection | 0.82 | 36.00 | 0.19 | 118.49 | 155.50 |
| 20 | b052479ba68c5f5b | elimination | 0.03 | 0.15 | 0.01 | 0.63 | 0.82 |

## Per-stage summary (s)

| stage | mean | sd | n |
|---|---:|---:|---:|
| descriptor_s | 0.528 | 0.417 | 20 |
| t1_s | 35.792 | 41.233 | 20 |
| guard_s | 0.321 | 0.447 | 20 |
| full_conv_s | 135.784 | 171.091 | 20 |
| total_s | 172.425 | 212.242 | 20 |

## Projection (§5(b) model)

search_phase_work = [Stage0: stage0_evals x (descriptor_n100 + T1 + stage0_offer_rate x guard)] + [arms: arm_evals_total x (descriptor_n50 + T1 + offer_rate x guard)] + [full-conv: n_checkpoints x n_arms x archive_size_estimate x full_conv]; wall = work / workers.

Assumptions (marked, not measured): offer_rate=0.3 (share of arm evals triggering the guard stage — guard was timed for EVERY CAL genome per Task 9's dispatch, not gated on would-enter status, so this discounts it back down); stage0_offer_rate=0.8 (init_archives() offers every valid Stage-0 genome to BOTH archives; archives start empty so the would-enter rate is high, and the runner's per-canon guard cache means the guard runs ONCE per genome even though it's offered to both archives, so this is not doubled); archive_size_estimate=50/arm/checkpoint; descriptor_n50 derived as descriptor_n100 x 0.5 (= N_STAGE1/N_STAGE0, not hardcoded).

| | optimistic (measured mean) | pessimistic (mean + 1 SD) |
|---|---:|---:|
| projected wall | 4.23h | 9.32h |

Cap: 8.0h. Verdict gates on the PESSIMISTIC projection (mean + 1 SD per stage) — a pre-launch cost gate should not clear on the optimistic case alone.

## Verdict: **RE-SCOPE REQUIRED**

within_cap=False, rescope_required=True. Over-cap -> RE-SCOPE REQUIRED (re-registration of B, never a silent change; OWNER-level decision — the runner does not read this file, it only informs the launch decision).

**Disposition (2026-07-03, owner decision):** RE-SCOPE resolved by BUILD_LOG
erratum #13 — full-conv checkpoint cadence re-registered 4 → 2 (300/600);
B=600 unchanged. Amended-shape projection on THIS file's measured data:
**6.88h pessimistic / 3.15h optimistic vs the 8.0h cap** (arithmetic pinned by
`test_cal_c.py::test_erratum_13_cadence_amendment_clears_cap_on_measured_cal_c_data`).
The measurements and verdict above stand as recorded for the superseded shape.


Wall time: 3448.5s. COMPLETE

**Second disposition (2026-07-04, BUILD_LOG erratum #14):** the projection
arithmetic above (both the 9.32h verdict and the #13 disposition's 6.88h
figure) carried a /7 double-count — `wall = work / workers` over per-genome
WALL means that already embed the within-genome fan-out. Proof internal to
this file: the 20-genome measurement run's wall time (3448.5s, recorded
below) equals the UNDIVIDED sum of per-genome totals, 7x the formula's
prediction. Corrected values on this file's measured data: superseded
4-checkpoint shape 65.25h pessimistic; #13 shape (B=600, 2 checkpoints)
48.20h / 22.03h; ratified S2 shape (B=300, checkpoints 150/300) **35.24h
pessimistic / 16.01h optimistic vs the amended 36h cap** (arithmetic pinned
by `test_cal_c.py::test_erratum_14_*`; history pinned against this file by
`test_erratum_13_history_stands_in_artifact_with_seven_x_defect`). The
measurements and per-genome records above are UNAFFECTED (the defect was
downstream arithmetic only); this artifact stands as recorded.
