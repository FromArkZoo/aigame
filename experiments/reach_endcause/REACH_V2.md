# REACH-v2 — end-cause guard redesign

Descriptor-v2 binding input (b): REACH redesigned on end-CAUSE (decided BY the win condition vs by attrition/timeout). Protocol pre-committed in `reach_v2.py`; bars mirror the original G-REACH wording verbatim (fires on S2; silent on e1453; other threshold games reported, not binding). Tactical rollouts: descriptor-v2 convention (100/game, 50 mirrored seed pairs).

| game | blind mean | wc_share (v2) | v1 decisive share | fires | end causes (wc/maxT/noMv/dblP/margin/timeout) | mean plies |
|---|---:|---:|---:|---|---|---:|
| S2 (binding) | 3.2 | **1.00** | 1.00 | — | 100/0/0/0/0/0 | 35.5 |
| e1453dac5445 (binding) | 3.9 | **1.00** | 1.00 | — | 100/0/0/0/0/0 | 21.0 |
| 1fea3357dca4 | None | **1.00** | 1.00 | — | 100/0/0/0/0/0 | 37.4 |
| b12ff78f1c1d | None | **1.00** | 1.00 | — | 100/0/0/0/0/0 | 21.2 |
| bfd1bb7ced76 | None | **1.00** | 1.00 | — | 100/0/0/0/0/0 | 24.4 |
| d995cf010504 | None | **1.00** | 1.00 | — | 100/0/0/0/0/0 | 17.7 |
| e52e8889517a | None | **1.00** | 1.00 | — | 100/0/0/0/0/0 | 24.4 |

## Verdict: **FAIL**

B1 fires-on-S2: FAIL (wc_share 1.00); B2 silent-on-e1453: PASS (wc_share 1.00)

Wall time: 404.9s. COMPLETE

## Inspection addendum (post-verdict, mechanism — engine end-site audit)

The FAIL is real, and the finding is bigger than the guard:

1. **Measurement validity confirmed.** Audit of every `done = True` site in
   engine_v2: the win-condition dispatcher is exclusive by condition_type, so
   for threshold-family games `_check_threshold` is the ONLY flag-free end
   (`_check_elimination` is live only for ctype="elimination";
   `_resolve_contested_by_score` only for contested_majority, via flagged
   paths). wc_share = done-with-no-flag is exact for this family.
2. **The descriptor-v2 attrition hypothesis is REFUTED.** "S2 ends
   decisively under tactical play (custodian-capture dynamics produce winners
   without threshold-crossing saturation)" was the RESULTS.md interpretation —
   measured end causes show S2 crosses its threshold in 100/100 tactical
   rollouts, 35.5 mean plies (rollouts byte-identical to the descriptor-v2
   convention; same mean plies). The capture dynamics FEED the crossing, not
   replace it.
3. **Threshold-unreachability is policy-relative.** TacticalAgent reaches
   S2's threshold easily; the blind teams ("threshold 36.9 unreachable;
   peaks ~+10; draw-prone") did not. Therefore NO end-cause definition over
   tactical rollouts can fire on S2 — the premise of an end-cause guard on
   THIS rollout policy is false, and binding input (b) cannot be satisfied
   on the tactical-rollout basis.
4. **Registered successor: REACH-v3 = the same end-cause question under the
   play that exhibits the pathology.** Under the PG convention's UCT games
   (the policy now load-bearing for selection), S2 produced 17/48 draws —
   no winner by ANY cause — vs ≤1/48 for every other blind-seven game and
   0/48 for e1453. A draw-share guard over UCT screening games keys on
   end-cause (decided by the win condition vs not decided at all), costs
   nothing extra in-loop (the screening games already exist), and must be
   validated on FRESH seed streams before adoption.
