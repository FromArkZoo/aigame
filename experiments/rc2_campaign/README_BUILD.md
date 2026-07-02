# RC2 campaign — build complete, run order

Build status: Tasks 0-12 done, full suite green (137 passed,
`experiments/rc2_campaign/`), runner smoke verified end-to-end, regression
suite on reused modules green. Interpreter: `.venv/bin/python` from repo
root.

## Prerequisites

- `PREREGISTRATION.md` is LOCKED (`72890a0`).
- `BUILD_LOG.md` decisions #1-#10 are ratified and logged (owner sign-off,
  Task 0). No campaign spend starts without this.

## Run order

1. **CAL-I — instrument gate (§5).**
   `.venv/bin/python cal_i.py --real` (~30-60 min). Measures whether the T1
   planning-gap instrument still separates the registered anchor pair on
   fresh streams at campaign settings. Writes `cal_i.json`. FAIL ->
   `PROBE_INVALID`, campaign does not launch. `run_campaign.py` refuses to
   start without a `cal_i.json` PASS (smoke mode never reads or writes it).

2. **CAL-C — cost projection (§5b).**
   `.venv/bin/python cal_c.py --real`. Times ~20 fresh genomes through the
   full per-genome pipeline (descriptor batch + T1 + guard stage + one
   full-conv re-eval) and projects the full campaign wall over the 8h
   search-phase cap. Over-cap -> re-scope B (re-registration) BEFORE launch;
   owner decision, not automatic.

3. **Owner go.** Manual checkpoint: CAL-I PASS + CAL-C within cap +
   BUILD_LOG ratified -> owner authorizes the real run.

4. **Campaign search.**
   `.venv/bin/python run_campaign.py` (8h search-phase wall cap; `--resume`
   picks back up from checkpoint after an interruption; `--b-arm` overrides
   the per-arm budget for re-registered scopes only). Runs Stage 0 (fresh
   CAL-disjoint sample, shared archive init) then matched-budget arms R
   (random) and M (MAP-Elites), evaluating BAR W-PG and BAR H-PG. Emits a
   pre-slate §9 token (`PROBE_INVALID` / `PROBE_INCOMPLETE` / `ARCHIVE_KILL`
   / `SEARCH_NEUTRAL` / `SLATE_PENDING`) via `bars.decide_verdict`.
   `SLATE_PENDING` is not itself a final verdict — it hands off to slate
   build.

5. **Slate build (§7).** On `SLATE_PENDING`: the orchestrator calls
   `slate.build_slate(m_elites, d4015, s3)` to compose the 7-game blind
   slate (top-3 M-elites by full-conv PG + 2 contrast elites + d4015 anchor
   + S3 carry-in), writes it to a slate JSON, then:
   `.venv/bin/python build_blind_pack.py --seed <sealed> --slate-json <path> --out-dir evaluations/<pack>`
   builds the labeled A-G blind pack for 3 independent teams (21 verdicts).

6. **Blind evaluation.** 3 independent blind tmux teams file 21 verdicts —
   real teammates, clean context, no aigame memory (SIEGE/frontline
   precedent).

7. **Verdict grep, unblind, decide.**
   `.venv/bin/python grep_verdicts.py evaluations/<pack>` scans all 21 filed
   verdicts for accidental identifier leakage BEFORE the sealed mapping is
   opened; any hit must be dispositioned first. Then unblind (open
   `.blind_mapping.json`), compute slate bars, and call
   `bars.decide_verdict(...)` for the final §9 token (`GO` / `GO-PARTIAL` /
   `NO-GO` / `CAMPAIGN_UNRESOLVED` / `SLATE_INCOMPLETE`, plus the pre-slate
   tokens if search itself failed).

## Module map

- `metrics/guard_probe.py` — rollout-tactical guard primitive + share
  helpers (backcompat re-export point).
- `pg_eval.py` — planning-gap instrument (net-free UCT batch eval).
- `seeds.py` — CAL-disjoint seed derivation + disjointness assertion.
- `guard_stage.py` — mirrored-pair guard stage (tilt veto).
- `campaign_archive.py` — two-ledger elite store (T1 + full-conv), floored
  quality, strict-improvement insertion.
- `bars.py` — pure BAR W / BAR H thresholds + `decide_verdict` precedence
  chain (§6/§9).
- `run_campaign.py` — orchestrator: Stage 0 -> arms R/M -> bars -> pre-slate
  token. Supports `--smoke` and `--resume`.
- `cal_i.py` / `cal_c.py` — pre-campaign gates (§5): instrument check, cost
  projection. Both support `--real` and `--dry-run`.
- `slate.py` — pure slate composition (§7), no engine/IO.
- `build_blind_pack.py` — blind-pack builder; also supports `--dry-run`
  (stand-in games, plumbing check only).
- `grep_verdicts.py` — pre-unblind blinding-breach scan.

## Smoke / dry-run artifacts

`run_campaign.py --smoke`, `cal_i.py --dry-run`, `cal_c.py --dry-run`, and
`build_blind_pack.py --dry-run` all write to untracked scratch
(`experiments/rc2_campaign/smoke/`, `*_dryrun.json`, `*_DRYRUN.md`,
`evaluations/<pack>_dryrun/`) and never emit a registered §9 token. Delete
freely between runs; nothing under version control depends on them.
