# RC2 planning-gap — blind-seven range validation

Phase-D-style Spearman over the full blind seven — the check that killed drama (−0.68 random-rollout, −0.31 competent-trace). Protocol frozen in `anchor_calibration.py`; S1/S2/S3 fresh, the four anchors reused verbatim (identical protocol + seeds). Bar pre-committed in `blind_seven_validation.py` with four of seven values known; fairness against the known values is argued in the script docstring.

| game | blind mean | family | PG | per-stream | W/D/L (deep) |
|---|---:|---|---:|---|---|
| S1 | 1.77 | connection | **+0.000** | -0.042, +0.042 | 24/0/24 |
| S4 | 3.0 | territory | **-0.323** | -0.312, -0.333 | 8/1/39 |
| S5 | 3.07 | territory | **+0.052** | +0.021, +0.083 | 26/1/21 |
| S3 | 3.1 | connection | **+0.479** | +0.500, +0.458 | 47/0/1 |
| S2 | 3.2 | threshold | **+0.198** | +0.125, +0.271 | 25/17/6 |
| d4015a646ae3 | 3.83 | connection | **+0.438** | +0.417, +0.458 | 45/0/3 |
| e1453dac5445 (contested) | 3.9 | threshold | **-0.229** | -0.333, -0.125 | 13/0/35 |

## Verdict: **PASS**

Spearman(raw PG, blind) over seven = +0.286 — bar: > 0; diagnostics: six excl. e1453 +0.771, floored +0.334

Wall time: 576.6s. COMPLETE

## Reading (post-verdict, non-binding)

1. **The contested point IS the gap.** e1453 alone drags Spearman from +0.771
   to +0.286 — every other disagreement is marginal. Where the two ground
   truths concur, PG tracks quality strongly; where they split (blind 3.90 vs
   R21 agent depth rank 6/7), PG sides with the agents, consistent with the
   anchor-calibration addendum.
2. **S1 lands at exactly 0.000 (24/24).** The blind-worst game (1.77, the
   RUSH-flagged ≤6-ply race) has literally zero planning content — the
   cleanest possible confirmation of the signal's semantics at the bottom of
   the range. Drama gave this game 0.146 and ranked it above both controls.
3. **One above-anchor surprise: S3 (+0.479) edges d4015 (+0.438).** Within
   joint noise (n=48 each), but S3 is an archive elite the blind teams scored
   3.10 — whether its tactics are genuinely as live as d4015's is exactly the
   above-anchor-range question only agent judgment settles. REGISTERED NOTE:
   include S3 in the next periodic agent slate.
4. Cumulative scoreboard on these seven: GE failed (R19–R21), random-rollout
   drama −0.68, competent-trace drama −0.31, naive learnability inverted at
   the pair gate, **planning-gap +0.286 / +0.771** — the first candidate with
   the right sign, twice registered, zero bars adjusted post-data.
