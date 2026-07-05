# Plan: apply ratified BAR H v2 re-registration (erratum/decision #15)

Spec (ratified, committed): `experiments/rc2_campaign/PREREGISTRATION_BARH_V2.md`
(owner ratified 2026-07-05: "go with your recommendations" — RATIFY branch).
Gear: G2. Pattern: erratum #14 apply (test-first, review-logged per parent §10,
independent review before merge). Branch: `barh-v2-apply` off main `da9ecfc`.

## Tasks

1. **Tests first (red):**
   - `test_bars.py` saturation pins → v2: constant 10, contested semantics,
     detail strings; keep all chain/decide_verdict tests untouched.
   - New `test_barh_v2_reanalysis.py`: pins the reanalysis outcome against the
     terminal `checkpoint.json` (skip-if-absent): joint 15, same-canon 5,
     contested 10, M strict 7, frac 0.700 → bar_h PASS → pre_slate_token
     SLATE_PENDING. Also pins Phase-C-consistency arithmetic from the spec §3.
2. **bars.py:** `SATURATION_MIN_JOINT` 20→10 (name kept per spec header;
   comment points at v2 §2); `bar_h` kwarg `joint_cells`→`contested_cells`;
   detail strings "contested cells missing or < 10" / "M-win frac over
   contested".
3. **run_campaign.py `bar_h_inputs`:** exclude same-canon cells from the win
   list (numerator AND denominator); return `contested_wins` + `contested_n`
   alongside `joint_n`/`same_elite_ties`; caller + results-writer lines
   updated; docstring cites v2 §2.
4. **Docs:** BUILD_LOG #15 (third post-lock amendment; basis + rejected
   alternatives already in the spec); parent `PREREGISTRATION.md` §6 inline
   [AMENDED ...] note; spec status DRAFT→RATIFIED.
5. **`reanalyze_barh_v2.py`:** load terminal checkpoint → final archives via
   `CampaignArchive.from_dict` → `bar_h_inputs` → `bar_h` → `pre_slate_token`
   with the recorded cal_i/bar_w/incomplete inputs → write
   `REANALYSIS_BARH_V2.md` tagged **BARH-V2-REANALYSIS** (spec §5). Run it;
   expected token SLATE_PENDING.
6. **Full suite** (151 + new) green.
7. Independent code review (requesting-code-review) → fix-first → merge to
   main → push (owner consent via ratification message).
8. Slate build + blind pack (`slate.py` + `build_blind_pack.py`) on the final
   archives — deterministic, orchestrator-side; blind teams remain
   owner-present work.
9. Housekeeping: gitignore `campaign.pid`; memory + lab notebook updates.

## Non-goals

No instrument changes (256v16 stays); no re-run of any search compute; no
slate-selection amendment (spec §4 rejected worst-first contrast);
campaign_results.md stays as the v1 historical artifact.
