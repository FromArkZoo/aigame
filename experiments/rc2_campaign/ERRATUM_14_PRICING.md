# Erratum #14 pricing — corrected campaign cost model (RATIFIED: S2)

Status: S2 RATIFIED by owner 2026-07-04 ("ratify S2 - apply the checklist
and resume") and APPLIED per §5 (BUILD_LOG erratum #14). Original draft
status preserved below for the record.

**Cap sizing note (apply-time deviation from §4's "32h"):** the pinned
gate arithmetic keeps the registered conservative ARCHIVE_SIZE_ESTIMATE=50
(Phase C measured 31–42), giving the S2 shape a from-scratch pessimistic
projection of **35.24h — a 32h cap would fail its own gate.** The cap was
therefore set to **36h**. This document's §3/§4 figures used
observed-coverage bands (18–40) and are the tighter realistic estimate;
the 36h cap only adds headroom against the model's own conservatism.

Draft status (2026-07-04 ~12:50): campaign PAUSED at `arm_R_running`
(R=50/600, M=0, elapsed 4.918h frozen, checkpoint intact). §5 below is the
amendment checklist for whichever scenario the owner ratifies.

## 1. The defect

`cal_c.py` (~line 306) computes `wall_s = total_work_s / workers`. But the
per-stage means it sums (`t1_s` 35.79s, `full_conv_s` 135.78s, ...) were
measured as **per-genome wall times with the 7-worker within-genome fan-out
already active** (erratum #9 design: genomes evaluate sequentially, each
genome's games fan across the pool). Dividing by 7 again double-counts the
parallelism.

Proof (CAL-C's own run is the counterexample): 20 genomes took 57.5 min
wall = 3450s ≈ the **undivided** sum 20 × 172.4s = 3448s. The formula
predicts 493s (8.2 min) for its own measurement run — off by 7.0x.

In-campaign confirmation: arm R measured **63.1s/eval** (50 evals in
0.876h, elapsed 4.042→4.918), within CAL-C's measured per-genome
distribution (t1 mean 35.8s, +1SD 77.0s). Stage 0 ran at a consistent
~60s/eval. The machine is on-model; the projection was wrong.

Blast radius: the 9.32h RE-SCOPE verdict, the A/B/C/D owner briefing, and
erratum #13's arithmetic (6.88h pessimistic) all inherit the /7.
`test_cal_c.py::test_erratum_13_*` pins the flawed formula.

## 2. Corrected model

wall = Σ per-genome wall costs (no division):

- per arm eval: opt 36.1s (CAL-C means, quiet machine) / real 63.1s
  (observed in-campaign today) / pess 77.8s (mean+1SD)
- full-conv re-eval per archive genome: opt 135.8s / real 172.4s
  (CAL-C total_s mean) / pess 306.9s (+1SD; heavy right tail, whale 906s)
- coverage per checkpoint (observed 14 at init, 15 at R=50; CAL-C's flat 50
  replaced): early ckpt 18/20/25, final ckpt 25/30/40 (opt/real/pess)
- attempts overhead (~1.8-2.0 attempts/eval × ~0.5-0.9s descriptor) is
  inside the observed band; negligible separately

## 3. Scenario grid (hours; TOTAL includes the 4.918h already spent)

| scenario | design | remaining real | TOTAL real | TOTAL pess | cap needed (pess×1.15) |
|---|---|---|---|---|---|
| S0/S1 registered | B=600, RA=(300,600) | 24.9 | 29.9 | 40.9 | **47h** |
| S2 half | B=300, RA=(150,300) | 14.4 | 19.4 | 27.9 | **32h** |
| S3 quarter | B=150, RA=(150,) | 7.3 | 12.2 | 17.1 | **20h** |
| S4 minimal | B=100, RA=(100,) | 5.5 | 10.4 | 15.0 | **17h** |

**The registered 8h cap is dead under every design**: solving for max B
inside the remaining 3.08h gives B≈58/arm realistic and **negative**
pessimistic (the two final full-conv re-evals alone cost 4.3h pessimistic).
No amendment that preserves the cap yields a search campaign; erratum #14
must amend the cap (§6/§9) whatever else it does.

Optional engineering lever — across-genome pipelining: workers idle ~30%
between genome waves; keeping the pool saturated across genome boundaries
has a ~1.43x ceiling (S2: 19.4h→15.0h real, cap 32h→24h). Results-identical
(per-game seeding is scheduler-independent) but it is mid-campaign runner
surgery; erratum #11's lesson argues for verifying via smoke + a replayed
stage-0 slice byte-compare if adopted. Not required for feasibility.

## 4. Recommendation: S2 — B=300/arm, REEVAL_STEP 150→(150,300), cap 8h→32h

- Feasible without runner surgery: 19.4h realistic total (overnight+day),
  32h cap absorbs the pessimistic tail.
- **Robustness**: mutual checkpoint at 150 restores real salvage — a
  wall-cap or crash past both arms' 150 yields bars at B_effective=150
  (GO-PARTIAL path per the ratified panel delta) instead of
  PROBE_INCOMPLETE. S3/S4's single checkpoint re-creates the
  all-or-nothing failure mode that doomed the current run.
- **Minimal prereg distance**: half the registered search per arm, same
  2-checkpoints-per-arm shape as erratum #13 (which set step 300 at B=600;
  this restores step 150 at B=300 — cadence-per-B is unchanged).
- Preserves everything banked: Stage 0 (240 evals, BAR W-PG PASS 3/3
  LIVE), CAL-I PASS, arm R's 50 evals, and the RNG streams — resume
  continues the same draw sequence; R has not passed 150, so the new
  checkpoint schedule triggers correctly.
- Costs half the search breadth vs registered B=600. If that is
  unacceptable, S1 at a 47h cap (or ~35h with the pipelining lever) is the
  honest price of keeping B=600.

## 5. Amendment checklist for S2 (apply only after ratification)

1. `run_campaign.py`: `REEVAL_STEP` 300→150; `B_ARM` 600→300; module
   assert (line ~127) then holds as (150,300); §3/§9 prereg inline text —
   second post-lock amendment, mirror the #13 edit style.
2. `checkpoint.json`: `b_arm` 600→300 field edit (load_checkpoint raises
   on mismatch, line ~1241) — or relax the check to allow a ratified
   reduction; field edit is smaller.
3. `cal_c.py` (~306): `wall_s = total_work_s` (drop `/ workers`); keep
   `workers` in the report line for context. Re-emit CAL_C.md disposition.
4. `test_cal_c.py::test_erratum_13_*`: re-pin to corrected arithmetic;
   add `test_erratum_14_*` pinning the grid above from cal_c.json data.
5. `BUILD_LOG.md`: erratum #14 entry (defect, proof, grid, decision,
   rejected alternatives S0/S1/S3/S4 with numbers).
6. Wall cap: `WALL_CAP_S` 8h→32h (§6/§9 amendment).
7. Re-launch: `caffeinate -i .venv/bin/python -u
   experiments/rc2_campaign/run_campaign.py --resume` on a quiet machine;
   verify the resume banner shows `arm_R_running` and reeval_at (150,300).

Measured inputs pinned in `.sp20/lab/rc2-campaign.jsonl` (2026-07-04
record) and reproducible via the scratchpad grid script.
