# RC2 campaign — results

Protocol per experiments/rc2_campaign/PREREGISTRATION.md (locked) + BUILD_LOG #1-#9: B=300/arm, full-conv re-eval at (150, 300), T1 128v16 n=24, full-conv 256v16 n=48, descriptor n 100/50, guard 12 mirrored pairs, 7 workers, per-unit timeout 180s, search-phase wall cap 36.0h.

## CAL-I (pre-campaign instrument gate, §5)

- cal_i.json verdict: **PASS**
- detail: PG(d4015a646ae3) +0.2917 - PG(S4) -0.4583 = separation +0.7500 vs bar >= 0.431 -> PASS

## Stage 0 — BAR W-PG (within-family validity)

Attempts 484, evaluated 240, valid 153.

| family | n_valid | p10 | p90 | p90-p10 | LIVE (floor 0.167) |
|---|---:|---:|---:|---:|---|
| territory | 31 | 0.0000 | 0.4167 | 0.4167 | YES |
| elimination | UNSAMPLED (0) | | | | |
| connection | 80 | 0.1250 | 0.4792 | 0.3542 | YES |
| threshold | 42 | 0.0000 | 0.4583 | 0.4583 | YES |

BAR W-PG: 3 LIVE of 3 qualifying -> **PASS**

## Stage 1 — BAR H-PG (matched-budget search value)

Bar evaluation mode: **final**, B_effective=300.

| arm | evals | coverage | QD-score (floored T1) | top-10 mean floored full-conv [95% CI] | full-conv-rated | skips |
|---|---:|---:|---:|---|---:|---:|
| R | 300 | 17 | 7.604 | 0.4823 [0.4745, 0.4901] | 17 | 0 |
| M | 300 | 26 | 11.458 | 0.4974 [0.4948, 0.4995] | 26 | 0 |

BAR H-PG (per_cell_wins): joint cells missing or < 20 -> **PROBE_INCOMPLETE**
- R_top10 (saturation watch, switch at 0.40): 0.4823
- jointly filled cells: 15; M strict wins 7; same-elite ties 5

Arm R top-10 family composition: {'connection': 7, 'territory': 2, 'threshold': 1}.
Arm M top-10 family composition: {'connection': 4, 'territory': 6}.

Parent-child T1-PG heritability (arm M, parents floored>0): raw r = 0.232, floored r (diagnostic) = 0.218 over 299 pairs.

## Full-conv re-eval ledger (repricing diagnostic)

- arm R: 12 multi-batch elites, max full-conv range 0.1146, mean 0.0312
- arm M: 13 multi-batch elites, max full-conv range 0.0938, mean 0.0232

## Counters

- M_dedup: 164
- M_eval_error: 1
- M_invalid_t1_draw_majority: 57
- M_invalid_t1_too_short: 33
- M_quick_reject: 23
- R_invalid_t1_draw_majority: 88
- R_invalid_t1_too_short: 43
- R_quick_reject: 113
- R_sim_excluded: 148
- stage0_eval_timeout: 2
- stage0_invalid_t1_draw_majority: 43
- stage0_invalid_t1_too_short: 42
- stage0_quick_reject: 92
- stage0_sim_excluded: 152
- arm M archive (stage0 init): filled_empty_cell=14, guard_vetoed_reach=1, guard_vetoed_tilt=55, invalid_draw_majority=21, lost_first_batch=51, offered=153, replaced=11
- arm M archive (arm phase): filled_empty_cell=12, guard_vetoed_reach=1, guard_vetoed_rush=4, guard_vetoed_tilt=13, invalid_draw_majority=15, lost_first_batch=145, offered=209, replaced=19
- arm R archive (stage0 init): filled_empty_cell=14, guard_vetoed_reach=1, guard_vetoed_tilt=55, invalid_draw_majority=21, lost_first_batch=51, offered=153, replaced=11
- arm R archive (arm phase): filled_empty_cell=3, guard_vetoed_reach=1, guard_vetoed_tilt=43, invalid_draw_majority=23, lost_first_batch=93, offered=169, replaced=6
- wall time: 1141.1 min

## Pre-slate verdict

This runner stops at slate-ready. SLATE_PENDING is recorded when BAR W ∧ BAR H pass and is NOT a §9 token — the slate stage (§7) runs later, manually, and emits the §9 slate verdicts (GO / GO-PARTIAL / NO-GO / CAMPAIGN_UNRESOLVED / SLATE_INCOMPLETE). §9 tokens PROBE_INVALID / PROBE_INCOMPLETE / ARCHIVE_KILL / SEARCH_NEUTRAL are emitted here as usual via bars.decide_verdict.

PRE-SLATE TOKEN: **PROBE_INCOMPLETE**
