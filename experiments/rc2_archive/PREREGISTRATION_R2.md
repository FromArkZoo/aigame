# RC2 Phase C — 2×-budget replicate (R2) pre-registration (locked before any R2 data)

Fires per the locked ARCHIVE_NEUTRAL branch of `PREREGISTRATION.md` (run-1 heritability
r = 0.344 ≥ 0.3 → "one 2×-budget replicate is registered"). Run-1 readout: `RESULTS.md`
(`f079589`).

## Protocol (everything not listed here is IDENTICAL to PREREGISTRATION.md by reference)

- base_seed = 17 → seed streams 17M (Stage-0 gen) / 34M (arm-R gen) / 51M (mutation rng)
  / 68M (selection rng) / 85M (bootstrap), derived by the same ×{1..5} rule as run 1's
  13M/26M/39M/52M/65M. All R2 streams are disjoint from every run-1 stream (run-1 attempt
  offsets stay below 13M+2k, 26M+15k; nearest pairs 51M/52M and 65M/68M cannot collide).
- B = 600 genome-evals per arm (2× run 1); full-archive re-eval after every 100 evals
  (100, 200, 300, 400, 500, 600 = final). All other constants unchanged: n=100 Stage-0 /
  n=50 Stage-1, quotas 15/120/160/2000, floors CAL 0.15 / BAR W 0.064 / BAR H 0.03,
  validity guard, eval-count matching, dedup, timeout/error accounting, 10h wall cap.
- Fresh CAL and fresh Stage 0 run under the R2 streams (the replicate independently
  re-tests the instrument and BAR W, not only BAR H).
- Content-derived eval seeds are unchanged by design: a genome appearing in both runs
  receives identical batches (deterministic measurement, shared by construction).
- Invocation (transcribed):
  `.venv/bin/python -u experiments/rc2_archive/run_probe.py --base-seed 17 --b-arm 600
   --out experiments/rc2_archive/replicate2x`

## Decision grammar (locked)

The runner applies the SAME grammar; R2's emitted token is interpreted as follows:

- R2 ARCHIVE_GO (BAR H ≥ 0.03 at B=600) → **Phase C concludes ARCHIVE_GO**: register
  Phase D (cross-cell blind-slate agent-team eval of arm M top elites) + the
  loop-integration spec (run.py:593 scores_map).
- R2 ARCHIVE_NEUTRAL → **Phase C concludes ARCHIVE_SHELVED**: archive integration is
  shelved pending descriptor/operator work; the top-K binding-metric design (run-1
  honest-synthesis §3: top-10 saturates against the territory ceiling while coverage/QD/
  per-cell wins favor M) becomes a REQUIRED input to any future archive registration —
  but no metric is changed retroactively for R2.
- R2 PROBE_INVALID / ARCHIVE_KILL / PROBE_INCOMPLETE → resolved on their own terms
  (instrument/confound/completeness), reported, and Phase C pauses for cause analysis;
  run-1's NEUTRAL stands meanwhile.

No further replicates are authorized by this registration regardless of outcome.

## Audit note

Committed before any R2 data. The only code change since run 1 is the parameterization
itself (`--base-seed`, `--b-arm`, derived streams + re-eval cadence) with a hard assert
that base 13 reproduces run 1's registered constants byte-for-byte; 34 unit tests green
post-change. Bars, mechanics, and grammar code paths are untouched.
