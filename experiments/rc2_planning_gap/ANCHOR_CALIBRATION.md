# RC2 planning-gap — closeness-confound anchor calibration

Registered obligation: rc2_descriptor_v2/RESULTS.md binding input (c) — quality signal demonstrated on the S4/S5 vs d4015 pair BEFORE any search spend. Protocol pre-committed in `anchor_calibration.py`; bar applied verbatim.

Signal: PG = seat-balanced score of net-free UCT@256 vs UCT@16 − 0.5 (uniform prior, random-rollout leaf, c_puct 1.5); n=48 per game (streams [42, 43], draws = 0.5). Net-free is required: rc2_learnability recorded PPO pass-collapse on 3/4 anchors, so net-guided search would inherit poisoned priors.

| game | blind mean | family | PG (mean) | per-stream PG | W/D/L (deep) | mean plies |
|---|---:|---|---:|---|---|---:|
| S4 | 3.0 | territory | **-0.323** | -0.312, -0.333 | 8/1/39 | 58.6 |
| S5 | 3.07 | territory | **+0.052** | +0.021, +0.083 | 26/1/21 | 54.0 |
| d4015a646ae3 | 3.83 | connection | **+0.438** | +0.417, +0.458 | 45/0/3 | 60.6 |
| e1453dac5445 (diagnostic) | 3.9 | threshold | **-0.229** | -0.333, -0.125 | 13/0/35 | 36.9 |

## Verdict: **PASS**

PG(d4015) +0.438 vs PG(S4) -0.323, PG(S5) +0.052 — bar: PG(d4015) strictly above both

Reading: PG ≈ 0 — deep search buys nothing (parity race / greedy-sufficient play); PG >> 0 — lookahead wins (live tactics). The closeness confound predicts S4/S5 near 0, d4015 above.

Wall time: 781.4s. COMPLETE

## Inspection addendum (post-verdict, mechanism — `negative_pg_check.py`)

The PASS stands on its registered terms, but two games (S4 −0.323, e1453
−0.229) show NEGATIVE planning gaps — deep search losing to shallow — which a
healthy signal shouldn't produce for free. Mechanism checked, non-binding:

1. **Pass-attractor hypothesis REJECTED.** Deep UCT pass shares are 0.00–0.03
   on all three games inspected — the pass-collapse failure mode that killed
   naive learnability does NOT recur in search form.
2. **Negative PG is relative, not absolute.** On S4 and e1453 BOTH depths beat
   RandomAgent 8/8; the deep side is a strong player losing to another strong
   player. The mechanism is rollout-model misspecification: UCT@256 converges
   harder toward lines the uniform-random rollout model scores as winning, and
   on parity-race (S4) and threshold (e1453) boards that model is wrong enough
   that more search amplifies its error. UCT@16 stays closer to the random
   prior and exploits the over-committed deep lines.
3. **d4015 shows a true gradient.** It is the only inspected game where
   vs-random discriminates budgets (0.750 @16 → 1.000 @256) — independent
   corroboration that its +0.438 PG reflects live tactics, not an artifact.

Consequences (parallel to the learnability addendum's "ordering among
collapsed games is noise"): the informative region of PG is **PG > 0**; the
ordering AMONG negative-PG games measures rollout-model misalignment, not
relative depth, and must not be read as a quality ranking. For any search
spend on PG: descriptor-v2 binding inputs still apply — RUSH + TILT guards on
insertion, REACH redesigned on end-cause — and the standing lesson that
range-valid ≠ maximand-valid above the anchor range means periodic agent
slates remain the registered ground truth. A search process maximizing PG
could in principle favor games whose dynamics make random rollouts
informative (model-alignment) rather than deep; the diagnostic that e1453
lands NEGATIVE while d4015 lands at +0.438 is the first evidence PG separates
those two properties correctly at anchor range.
