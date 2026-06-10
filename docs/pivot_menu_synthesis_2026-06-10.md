# aigame Pivot Decision — Synthesis Judgment

All five candidates survived all three adversarial lenses (no fatal flaws anywhere), so the ranking turns on: breadth of root-cause attack, severity of fixable issues, probe economics, and composition. I spot-verified the load-bearing disputed code facts on disk before ranking: trainer.py:99-100 does instantiate per-seat PolicyNetworks; `_capture_field_flip` is at engine_v2.py:905; the control_flip_rate ladder (10.606 / 5.298 / ~4.2) and flip-capture 7.09 events/game are in `/Users/jamesbrowne/aigame/experiments/fc_phase15/RESULTS.md`; and `/Users/jamesbrowne/aigame/game_engine/generator_v2.py:213-224` really forces `prop_type='none'` for every non-threshold win condition — the fact that guts both QD candidates' descriptors as written.

## Ranked table

| Rank | Candidate | Root causes attacked | Verdicts | Probe cost | Disposition |
|---|---|---|---|---|---|
| 1 | **SIEGE** (asymmetric Maker–Breaker on r=2 field) | RC1 maximally; RC2 by omission | 3/3 survive; all issues spec-grade | ~2.5–3 days wall incl. build | **Run it.** Absorbs #2 as its control arm |
| 2 | **z_flip_r2** (flip-capture on r=2 field) | RC1 residual only | 3/3 survive; cleanest verdict set | ~half day post-build | Absorbed into #1 as arm S; standalone fallback if M dies at calibration |
| 3 | **Frontline** (contested-majority scoring) | RC1 structurally; RC2 piloted | 3/3 survive; probe self-kills on arithmetic as registered | ~2 days, but needs a near-redesign first | Designated next-family candidate if the SIEGE campaign NO-GOes |
| 4 | **FamilyMAP** (family-indexed MAP-Elites over rules) | Both, in principle | 3/3 survive; compute claim off ~10x, descriptors dead off-threshold | ~1.5 day build + 130–180h Stage-2 as written | Defer; register the RC2 follow-on now, run after instrumentation fix |
| 5 | **Deep-Grid MAP-Elites** (QD selection, PPO-free ladder) | RC2; RC1 conditionally | 3/3 survive; star witness (573) fails its own gates | ~3h P0, but P0 unrunnable as specced | Superseded by #4's machinery; harvest its archive hygiene |

## Per-candidate verdicts

**1. SIEGE.** The only design where the opponent's structure is the *entire* win function for one player — Breaker scores exclusively by flipping Maker stones — so root cause 1 is attacked at its maximum, on the one field config with proven live dynamics (flip rate 10.6) using the one capture proven to fire (7.09/game), with zero training-code delta (per-seat policies already exist). Its modal kill, asymmetric balance, sits at the cheapest stage (calibration, ~4h) and a kill there is itself informative. The sharpest lens findings are all screen-spec, not concept: two of four screen signals are Goodharted toward M by construction (flip events are Breaker's literal win condition; control-margin drama saturates on Breaker wins), the Breaker trained-vs-random gate is vacuous (a random Breaker beats a random Maker on timeout), and the phase-1.5 CSV shows a collapsed seed can masquerade as perfect balance (C1 seed42: tvr 0.000, seat_balance 0.000) — every one has a concrete pre-registration fix, grafted below. The Stage-0 memo also contains a real arithmetic error (3 distance-2 attackers give 0.75 < 1.0; at least 2 must be adjacent) and analyzes lone stones when Maker builds chains holding ~2.0 own-field — the quota can be starved by a Maker who leaves no stragglers, which is exactly what the Stage-1 quota-share gate exists to catch.

**2. z_flip_r2.** Cleanest verdicts of the five and the cheapest falsification, with every engine claim verified at file:line by the reviewers; the methodology lens's best catches were an arithmetically inert seed-45 guard (a collapsed seed caps the 4-seed tvr aggregate at 0.775 < 0.80, so the "rescue" can never rescue) and a missing campaign-validity control before permanent family closure. But standalone it attacks only the residual of root cause 1, leaves GE untouched, carries a demonstrated novelty ceiling ~4, and the FC family is registered closed — its honest value is as the in-campaign control the pivot needs anyway. SIEGE's arm S *is* this candidate, freshly pre-registered as the brief requires, so ranking it second costs nothing: it runs either way.

**3. Frontline.** The most conceptually novel attack on root cause 1 — packing scores literally zero because the score support is the intersection of both influence supports — and the only candidate that fixes the C2 komi problem by construction (count-based score). But all three lenses converged on the same verdict: the probe as registered is decided by arithmetic before play matters. Stage 0a needs per-ply logs that don't exist anywhere on disk; Stage 0b's engaged_share>0.90 kill fires near-deterministically on random rollouts (P(engaged) ~0.97 at margin 0.25 on a 41%-full 484-cell board) — a false kill from distribution mismatch; and terminal-only scoring pins game_length=200 and decisiveness constant for F1/F2, recreating trap 1 inside its own screen. The degeneracy lens adds that the easiest flip is score-negative for the capturer (deleting a kernel disengages ~19 cells) — the same anti-synergistic capture shape as R21's confirmed root cause. The viable region (margin ~1.0, decoupled flip threshold, score-margin early-end rule, double-pass resolution) is outside the registered ladder; that's a redesign, not a fix. Keep the concept on the bench as the next family if SIEGE's family dies.

**4. FamilyMAP.** The only candidate that attacks both root causes in one structure, and its funnel discipline (cheap gates before any PPO) is genuinely good. But three load-bearing specs are contradicted by the repo: D3 drama is identically zero for non-influence families (generator_v2.py:213-224, verified), D2's plateau-percentile bins saturate exactly where interaction lives, and the within-cell fitness was already measured on disk as noisy and non-discriminating (mcts_phase1: sigma_WR 0.105–0.224, all substrates 0.725–0.825) — plus the Stage-2 compute claim is off roughly 10x against on-disk timing (17.4 s/game at 256 sims). The P2 GO bar is also a best-of-6 survivorship gate with ~25–50% null false-GO at the stated verdict budget. None of this kills the lever, but it means an instrumentation build (a measurement-only observer influence field for all genomes) must precede even its cheap anchor probe.

**5. Deep-Grid MAP-Elites.** Same dead-descriptor disease as FamilyMAP, plus a self-contradiction at its center: 573, the motivating rescue case, fails the proposal's own Tier-0 gates (0.50 seat bias, komi/pie-unfixable per run21/SUMMARY.md), so "the archive makes family deletion structurally impossible" is false as written; and per-seed CSV data shows D2 *rewards training collapse* (collapsed seeds posted the highest lead_changes). Its Phase 1 (4 generations) also ends one generation before the only validated compounding evidence (R21's top-2 were gen-5 children). Its best ideas — challenger eval-count matching, periodic full-archive re-eval, cross-cell blind slates — should be harvested into the eventual RC2 workstream rather than run as proposed.

## Recommendation

**Run SIEGE as the pivot campaign, with z_flip_r2 absorbed as the in-campaign control arm S, and register the selection-layer (RC2) follow-on now so a SIEGE GO cannot defer it.** This fills pivot seat (a) with the strongest interaction-forcing design, properly registers the post-hoc flip-on-r2 candidate as the brief demands, and gives the campaign a built-in fallback: if asymmetric balance dies at calibration (the modal kill), the campaign continues as S vs A1 vs A0 — which is exactly z_flip_r2's registered probe, so the calibration spend is never wasted. Frontline (rebuilt at margin ~1.0 with a decoupled flip threshold and a score-margin early-end rule) is the registered next family if both M and S NO-GO.

### Grafts (each named with source)

1. **Arm S = z_flip_r2, with its verdict fixes**: median-of-seeds tvr gating (the seed-45 recompute is arithmetically inert for tvr — z_flip_r2 methodology lens); distinct-stones-flipped >= 0.5 x flip-events anti-flip-tennis diagnostic (z_flip_r2 degeneracy lens); campaign-validity band — if in-campaign A1 lands outside [3.9, 4.4], verdict is CAMPAIGN_UNRESOLVED and triggers a cheap replicate, never permanent closure (z_flip_r2 methodology lens); tie band |M−S| < 0.3 treated as deferred, not a sign call (same source).
2. **Per-role drama signal** (winner behind on its OWN progress trace: largest-component differential for connection, quota_frac for Breaker) replacing raw control-margin drama, which structurally saturates on Breaker wins — from SIEGE's relevance lens, using Frontline's sqrt-deficit-weighted winner-behindness formulation; raw lead_changes stays demoted to diagnostic per Browne's negative human-preference correlation (both Frontline and SIEGE proposed this independently).
3. **Anchor-calibrate the new drama signal before it becomes a bar** (retro-compute on A0/A1 traces + R21 extremes; must rank A1 > A0 consistent with the 2/2 blind preference, else demoted to diagnostic) — the project's own 15-min-probe rule, surfaced by SIEGE's methodology lens; scoped as a mini-compute step per Frontline's methodology lens finding that no per-ply logs exist.
4. **Gate ordering and collapse handling**: tvr gate evaluated *before* any bias computation; a collapsed seed triggers a fresh-seed rerun, never exclusion (collapse mimics perfect balance — C1 s42 on disk) — SIEGE methodology lens.
5. **De-Goodhart the screen**: flip events demoted to band-only sanity [1,20]; GO requires M >= 2/3 on objective-neutral comparatives (control_flip_rate, game_length centrality, per-role drama) with pre-registered effect-size floors — SIEGE methodology lens, floors per the honest-denoiser doctrine.
6. **Stage-0 memo redone on chains, not lone stones** (chain-end ~4 attackers, interior ~5–7 with cascade rollup; the published 3x0.25=0.75<1.0 error fixed) plus a scripted chain-builder rollout gate so flip-firing is tested against connection-shaped play, not just random stragglers — SIEGE degeneracy + relevance lenses.
7. **clock_frac added to observations** (Breaker's timeout strategy is unlearnable without it) and **role-pie** (P2 chooses role after move 1) pre-registered as the balance lever of last resort if the (N,T) grid fails — SIEGE degeneracy lens.
8. **One eps=0.25 @ r=2 sensitivity cell at calibration** — the registered untested design region, and the pre-bound single-knob PARTIAL re-parameterization, addressing the blind teams' unmet blur critique — SIEGE relevance lens.
9. **Timeout-share gate tightened to <= 0.25 of all games** (denominator pinned) plus a Breaker-passivity diagnostic; quota-share and timeout-share gates re-asserted at Stage-2 PPO-5000, not calibration-only — SIEGE relevance + methodology lenses.
10. **RC2 follow-on registered now** (from FamilyMAP/MAP-Elites): next workstream after this campaign, regardless of outcome, is the selection-layer probe — gated on building the measurement-only observer influence field so descriptors are defined for all genomes (the generator_v2.py:213 fact), using within-R21 binary separation bars instead of the underpowered cross-campaign Spearman, and inheriting challenger eval-matching + cross-cell slates + periodic re-eval from the MAP-Elites proposal. The capture_quota condition type built for SIEGE is reusable as a FamilyMAP gene, so the engine work double-counts.

### Honest caveats

- SIEGE's wall-clock is ~2.5–3 days including build — about 1.5x the registered ~1-day-build envelope, mostly the role-matrix eval runner and the asymmetric verdict protocol, which is new instrumentation needing its own pre-registration.
- "Packing scores zero" is overstated early in training: at init, Breaker wins nearly everything passively on timeout. The quota-share >= 0.20 and timeout-share <= 0.25 gates are what stand between SIEGE and a turtle meta; if they fail across the whole (N,T) grid, believe them and kill it.
- A GO here is a rules win only. GE remains untrusted and the generator remains blind; the RC2 registration (graft 10) is what prevents a SIEGE success from recreating the "iterate on the winner" overhang that produced four GE-tuning runs.

## Probe outline

See `probe_spec_outline` for the pre-registerable skeleton (arms, signals with movability arguments, numbered bars, gates, stop rules, compute).

## Dissents

See `dissents` — four recorded, including a cost-minimalist case for running z_flip_r2 alone and a selection-first case for leading with QD.

---

## Probe spec outline (pre-registerable skeleton)

```
SIEGE PIVOT CAMPAIGN — pre-registerable skeleton (single PREREGISTRATION.md committed before any training; spec §7 decision grammar applied verbatim; all engine additions gated + legacy bit-identical, 239-test suite green)

ARMS (4 in screen, 3 in blind):
- M = SIEGE: P1 Maker wins by field_connection (existing, gated; A1 tvr 0.863); P2 Breaker wins by capture_quota N field_flip events (counted on DISTINCT Maker stones, per-turn tick cap — anti flip-tennis graft) OR timeout_winner=P2 at turn T. Both players field_flip; positional superko; hex_rhombus, r=2/decay 0.5/eps 0. Obs adds quota_frac AND clock_frac (graft 7).
- S = z_flip_r2: symmetric field_flip + field_connection on the identical substrate. Fresh pre-registration of the post-hoc candidate (per corrections brief); single manipulated variable vs M = win-structure asymmetry.
- A1 = field_connect reference, retrained in-campaign (bit-identical retraining proven).
- A0 = legacy baseline, retrained in-campaign (anchors template signals; screen only, not blind).

STAGE 0 (pre-build, ~0.5 day, zero engine code):
- Flip-threshold memo at r=2/d=0.5 redone on CHAINS: lone stone needs 3 attackers incl. >=2 adjacent (fixes the 0.75<1.0 error); chain-end ~4; interior ~5-7 with cascade rollup. KILL: lone-stone flip needs >4 coordinated attackers.
- 1000 random rollouts + scripted greedy chain-builder rollouts per arm; flip-locus (frontier vs straggler) logged. KILL: <1 flip/game in M or S under EITHER policy (surround-0.000 analog, tested against connection-shaped play).

STAGE 1 CALIBRATION (~4-5h honest, PPO 3000, n=200/cell — 2x the original claim per methodology verdict):
- M: (N,T) grid {3,5,8}x{80,120,160}, 3 seeds. Gates per cell: role bias <= 0.10 via cross-seed role matrices, computed ONLY after the tvr gate (collapsed seed -> fresh-seed rerun, never exclusion); quota share of Breaker wins >= 0.20; timeout share <= 0.25 of ALL games (denominator pinned). Tie-break among passing cells (pre-registered): max quota share, then min |bias|. Fallback lever of last resort if grid fails: role-pie (P2 chooses role after move 1) — one registered retry, not open-ended.
- S: pie rule at komi 0.00 first (probe precedent: A1 bias 0.050), komi grid 0.00-0.30 fallback; bias <= 0.10.
- One eps=0.25@r2 sensitivity cell on S, diagnostic only; pre-bound as the SINGLE licensed PARTIAL re-parameterization knob.
- KILL: entire (N,T) grid + role-pie retry leaves bias > 0.10 -> M dead (Tafl analog); campaign CONTINUES as S vs A1 vs A0 under z_flip_r2's registered bars. Calibration spend never wasted.

STAGE 1.5 SIGNAL ANCHOR-CALIBRATION (15-min-probe rule, mini-compute):
- Per-role drama (sqrt-deficit-weighted winner-behindness on each player's OWN progress trace: largest-controlled-component differential for connection roles, quota_frac for Breaker) retro-computed on freshly rolled A0/A1 traces + R21 extremes. BAR: ranks A1 > A0 (consistent with 2/2 blind preference) and does not rank e1453 top. FAIL: drama demoted to diagnostic; GO becomes 2/2 of remaining comparatives.

STAGE 2 SCREEN (~2.5h, 4 arms x seeds 42/43/44 @ PPO 5000, n=200):
Comparative signals, M vs S, all objective-neutral and both-arms-movable:
1. control_flip_rate — identical r=2 instrumentation in all field arms; proven movable by capture-free arms (A0 5.298, A1 10.606 on disk). Floor: delta >= 0.5 absolute (A1 per-seed CV ~1%, so point-delta wins are banned).
2. game_length centrality in [30,160], center 95 — every arm has a length; phase-1.5 spread 61.9-155 shows both directions move. Floor: >= 10 turns more central.
3. per-role drama (anchor-calibrated above) — every game produces both progress traces under identical instrumentation. Floor: delta >= 0.05.
Band-only sanity (NOT comparative — de-Goodhart graft): flip events/game in [1,20] with distinct-stones-flipped >= 0.5 x events; quota share >= 0.20 and timeout share <= 0.25 RE-ASSERTED on the 5000-step runs; draw <= 0.05 (S/A1/A0 only; M structurally drawless — stated, not credited); per-role tvr >= 0.80 BASELINE-ADJUSTED (trained-Breaker improvement over random-Breaker-vs-random-Maker win rate — fixes the vacuous gate) with mandatory per-seed inspection; role/seat bias <= 0.10.
GO: M >= 2/3 comparative signals + all sanity bands. STOP RULES: M fails but S clears the z_flip_r2 template (>= 3/4 vs A0 incl. thick-Hex tripwire, lead_changes-only version) -> blind runs S vs A1 only. Both fail -> NO blind (~50 min saved), campaign NO-GO at screen.

STAGE 3 BLIND (~60 min: 2 independent teams, fresh neutral labels, sealed mapping opened after all verdicts; role-swapped matches, role-averaged verdicts; protocol itself pre-registered incl. a fairness-perception probe question; role win split logged, flag > 80/20):
Games: M, S, A1 (in-campaign). BARS:
- CAMPAIGN VALIDITY: A1 in [3.9, 4.4]; outside -> CAMPAIGN_UNRESOLVED -> one cheap blind replicate, no permanent classification.
- GO: M - A1 >= +1.0 AND M > S with |M-S| >= 0.3 (implies absolute ~>= 5.0 if A1 reproduces — registered as actual plateau-break, first in 5 runs).
- PARTIAL: |M-S| < 0.3 or M > S but M - A1 < +1.0 -> exactly one licensed re-parameterization: the eps=0.25@r2 cell, nothing else.
- M <= S: asymmetric-objectives direction RETIRED (not reparameterized); S adjudicated under z_flip_r2's own grammar (S - A1 >= +1.0 reopens the FC family; S <= A1 closes it permanently, with the validity band guarding the closure).
- Both NO-GO: registered escalation -> Frontline rebuilt (margin ~1.0, decoupled flip_margin, score-margin early-end rule, double-pass resolves by main score) as the next family.

REGISTERED FOLLOW-ON (fires on ANY outcome, prevents the iterate-on-winner overhang): RC2 selection-layer workstream — build the measurement-only observer influence field (generator_v2.py:213-224 makes current descriptors zero off-threshold), then the QD anchor probe with within-R21 binary separation bars (R8/A1 above plateau pod; no cross-campaign Spearman), inheriting challenger eval-matching, cross-cell slates, and periodic full-archive re-eval from the MAP-Elites proposal. GE stays diagnostic-only meanwhile.

COMPUTE (honest): build ~1-1.5 days (win_condition_p2 dispatch, quota counter + distinct-stone accounting, timeout_winner, 2 obs floats, role-matrix eval runner, tests) + Stage 0 ~0.5 day + Stage 1 ~4-5h + Stage 2 ~2.5h + Stage 3 ~1h. Total ~2.5-3 days wall — ~1.5x the registered envelope, declared upfront.
```

## Dissents (recorded in full)

1. Cost-minimalist dissent: z_flip_r2 alone (Q/Y/Z, ~half a day after a 2-4h build) buys the single cleanest bit of information for the least money, and SIEGE stacks an unvalidated balance problem (Tafl's historic failure mode) plus ~1.5 days of new engine/eval code on top of it. Overridden because z_flip_r2 standalone cannot break the plateau (novelty ceiling ~4 demonstrated, root cause 2 untouched, FC family registered closed), and the SIEGE campaign contains the entire z_flip_r2 probe as arm S at the marginal cost of one extra arm — the information is bought either way.

2. Selection-first dissent: the GE rank-inversion is the generator's disease; any rules win still leaves selection blind, and FamilyMAP is the only candidate attacking both root causes in one structure — sequencing it second risks another rules family being judged by instruments we already know are broken. Overridden on verified code facts: both QD candidates' behavioral descriptors read board_values, which generator_v2.py:213-224 zeroes for every non-threshold genome (verified on disk this session), their within-cell fitness was already measured noisy and non-discriminating in mcts_phase1, and FamilyMAP's Stage-2 compute claim is off ~10x against on-disk timing. They need an instrumentation build before their own cheap probes are even runnable; registering the RC2 follow-on now (graft 10) preserves the attack without betting the campaign on dead descriptors.

3. Frontline-first dissent: it is the only candidate that makes packing worth literally zero by definition rather than by gradient pressure, the only one with no published-game analogue (the novelty ceiling that capped FC does not obviously apply), and its degeneracy lens explicitly located a viable region (margin ~1.0). Overridden on probe economics: as registered it self-kills on arithmetic at three independent stages (Stage 0a needs logs that do not exist, Stage 0b's saturation kill fires on a distribution mismatch, terminal-only scoring pins 2/4 screen signals), its easiest capture is score-negative for the capturer — the same anti-synergy shape as R21's confirmed root cause — and the fix set amounts to a redesign. It is preserved as the registered next family on a SIEGE-campaign NO-GO, which is a better use of it than leading with a spec known to need rebuilding.

4. Degeneracy-lens minority view on the top pick itself: SIEGE's headline claim ('packing scores zero') is overstated early in training — at initialization Breaker wins nearly everything by passive timeout, so the family's interaction-forcing property is carried entirely by the quota-share >= 0.20 and timeout-share <= 0.25 gates rather than by the win condition per se. If those gates only just clear, the blind campaign may meet a numerically-passing turtle game and burn the campaign spend. The ranking accepts this because the gates are cheap, pre-registered, re-asserted at screen strength, and a grid-wide gate failure is itself a clean family kill — but the owner should treat marginal gate passes as a yellow flag, not a green light.

## Provenance

Produced 2026-06-10 by a 25-agent ultracode workflow (run `wf_c971c5cc-c7b`): repo evidence scout + 3 external-methods research agents -> 5 independent design seats (new-family / qd-selection / fc-flip-r2 / qd-over-rules / wildcard) -> 3 adversarial lenses per design (degeneracy, methodology, relevance; 5/5 designs survived 3/3 with zero fatal flaws) -> synthesis judge. The synthesis agent reports spot-verifying load-bearing code claims on disk (trainer.py:99-100 per-seat policies; engine_v2.py:905 _capture_field_flip; generator_v2.py:213-224 prop_type=none off-threshold). Re-verify these during the PREREGISTRATION.md build.
