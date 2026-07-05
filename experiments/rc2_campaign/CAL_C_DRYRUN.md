# CAL-C — pre-campaign cost projection  [§5(b)] (DRY RUN — wiring check only, NOT a binding projection)

RC2 §5(b) pre-campaign gate. 3 fresh CAL genomes (seed base 19500000 = GEN_SEED_BASE + 500000) timed end-to-end through the FULL per-genome pipeline (descriptor batch + T1 + guard stage + full-conv re-eval), projected over the registered campaign shape (Stage-0 240 evals + 2 arms x 600 + 4 full-conv checkpoints) across 7 workers vs the 8.0h search-phase cap.

Draw: 6 attempts -> 3 accepted.

Timed: 3 of 3 genomes attempted; 0 failed.

## Per-genome timings (s)

| # | canon | family | descriptor | T1 | guard | full-conv | total |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | a8fb98011492ced4 | territory | 0.04 | 3.05 | 0.03 | 2.92 | 6.05 |
| 2 | 6bd34c12fb530833 | elimination | 0.00 | 0.01 | 0.00 | 0.01 | 0.03 |
| 3 | 854343fa18ac322b | threshold | 0.04 | 1.25 | 0.03 | 2.07 | 3.39 |

## Per-stage summary (s)

| stage | mean | sd | n |
|---|---:|---:|---:|
| descriptor_s | 0.028 | 0.021 | 3 |
| t1_s | 1.436 | 1.529 | 3 |
| guard_s | 0.023 | 0.016 | 3 |
| full_conv_s | 1.669 | 1.496 | 3 |
| total_s | 3.155 | 3.014 | 3 |

## Projection (§5(b) model)

search_phase_work = [Stage0: stage0_evals x (descriptor_n100 + T1 + stage0_offer_rate x guard)] + [arms: arm_evals_total x (descriptor_n50 + T1 + offer_rate x guard)] + [full-conv: n_checkpoints x n_arms x archive_size_estimate x full_conv]; wall = work / workers.

Assumptions (marked, not measured): offer_rate=0.3 (share of arm evals triggering the guard stage — guard was timed for EVERY CAL genome per Task 9's dispatch, not gated on would-enter status, so this discounts it back down); stage0_offer_rate=0.8 (init_archives() offers every valid Stage-0 genome to BOTH archives; archives start empty so the would-enter rate is high, and the runner's per-canon guard cache means the guard runs ONCE per genome even though it's offered to both archives, so this is not doubled); archive_size_estimate=50/arm/checkpoint; descriptor_n50 derived as descriptor_n100 x 0.5 (= N_STAGE1/N_STAGE0, not hardcoded).

| | optimistic (measured mean) | pessimistic (mean + 1 SD) |
|---|---:|---:|
| projected wall | 0.11h | 0.22h |

Cap: 8.0h. Verdict gates on the PESSIMISTIC projection (mean + 1 SD per stage) — a pre-launch cost gate should not clear on the optimistic case alone.

## Verdict: **WITHIN CAP**

within_cap=True, rescope_required=False. Over-cap -> RE-SCOPE REQUIRED (re-registration of B, never a silent change; OWNER-level decision — the runner does not read this file, it only informs the launch decision).


Wall time: 9.5s. DRY RUN — non-binding
