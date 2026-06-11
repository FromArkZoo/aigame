# RC2 descriptor-v2 probe — results

n=100 tactical-vs-tactical rollouts/game as 50 mirrored seed pairs (pair i -> agent seeds (1000*i+1, 1000*i+2), i=0..49; mirrored game swaps them across seats). TacticalAgent per metrics/tactical_agent.py (WIN-IN-1 -> BLOCK-WIN-IN-1 -> densify; always swaps on pie). drama_v2 = winner_behindness via the LOCKED metrics.descriptors.obs_drama_for_rollout on tactical traces; per-game mean over non-draw rollouts, draws counted. Hard cap 2*max_game_steps. Protocol + bars per experiments/rc2_descriptor_v2/PREREGISTRATION.md (locked).

Total wall: 4349s (cap 7200s). Workers: 7 (per-rollout results depend only on (game, seed pair); scheduling cannot change them).

## Per-game table

Set: D = Phase D seven, B = Phase B anchor ten (overlap pair evaluated once, canonical-hash-checked against the blind pack). Agent mean: Phase D blind mean / Phase B registered agent mean (d4015 and e1453 carry their Phase D blind means 3.83 / 3.90).

| game | set | family | agent mean | n | decisive | draws | drama_v2 | RUSH (share) | REACH (share) | TILT (P1 share) | mean plies | wall s |
|---|---|---|---:|---:|---:|---:|---:|---|---|---|---:|---:|
| S1 | D | connection | 1.77 | 100 | 79 | 21 | 0.1457 | FIRES (1.00) | n/a (—) | no (0.80) | 4.0 | 1238 |
| S2 | D | threshold | 3.20 | 100 | 100 | 0 | 0.3715 | no (0.00) | no (1.00) | no (0.66) | 35.5 | 12 |
| S3 | D | connection | 3.10 | 100 | 91 | 9 | 0.3271 | no (0.00) | n/a (—) | no (0.65) | 119.4 | 594 |
| S4 | D | territory | 3.00 | 100 | 100 | 0 | 0.3119 | no (0.00) | n/a (—) | FIRES (0.80) | 55.2 | 8 |
| S5 | D | territory | 3.07 | 100 | 100 | 0 | 0.3119 | no (0.00) | n/a (—) | FIRES (0.80) | 55.2 | 5 |
| d4015a646ae3 | D+B | connection | 3.83 | 100 | 100 | 0 | 0.1077 | no (0.00) | n/a (—) | no (0.45) | 56.7 | 40 |
| e1453dac5445 | D+B | threshold | 3.90 | 100 | 100 | 0 | 0.0323 | no (0.00) | no (1.00) | no (0.17) | 20.0 | 316 |
| s_flip_r2 | B | field_connection | 4.10 | 100 | 100 | 0 | 0.1219 | no (0.00) | n/a (—) | no (0.22) | 194.2 | 20060 |
| a1_field_connect | B | field_connection | 3.90 | 100 | 100 | 0 | 0.1219 | no (0.00) | n/a (—) | no (0.22) | 194.2 | 6697 |
| d995cf010504 | B | threshold | 3.78 | 100 | 100 | 0 | 0.0429 | no (0.00) | no (1.00) | no (0.25) | 16.7 | 12 |
| 573562833174 | B | connection | 3.78 | 100 | 75 | 25 | 0.2162 | no (0.00) | n/a (—) | no (0.44) | 67.8 | 62 |
| b12ff78f1c1d | B | threshold | 3.72 | 100 | 100 | 0 | 0.0725 | no (0.00) | no (1.00) | no (0.23) | 20.2 | 16 |
| e52e8889517a | B | threshold | 3.68 | 100 | 100 | 0 | 0.0391 | no (0.00) | no (1.00) | no (0.26) | 23.4 | 373 |
| bfd1bb7ced76 | B | threshold | 3.68 | 100 | 100 | 0 | 0.0391 | no (0.00) | no (1.00) | no (0.26) | 23.4 | 374 |
| 1fea3357dca4 | B | threshold | 3.50 | 100 | 100 | 0 | 0.0317 | no (0.00) | no (1.00) | no (0.22) | 36.4 | 595 |

## Bars (transcribed verbatim; point estimates)

| bar | text | detail | pass |
|---|---|---|:---:|
| G-RUSH | RUSH fires on S1; does NOT fire on e1453, d4015, s_flip_r2, a1_field_connect. | S1=FIRES; e1453dac5445=no; d4015a646ae3=no; s_flip_r2=no; a1_field_connect=no | PASS |
| G-REACH | REACH fires on S2; does NOT fire on e1453. (Other threshold games reported, not binding.) | S2=no; e1453dac5445=no | FAIL |
| G-TILT | TILT fires on >= 1 of {S4, S5}; does NOT fire on s_flip_r2 or a1_field_connect. (d4015 reported, not binding — its R8-era balance is unverified under tactical play.) | S4=FIRES, S5=FIRES; s_flip_r2=no, a1_field_connect=no | PASS |
| V2-RANK | over the Phase D seven, drama_v2 of BOTH e1453 and d4015 exceeds drama_v2 of EVERY S-game on which at least one guard fires; and among guard-clean games, no S-game outranks both controls. (Spearman(drama_v2, blind mean) over all 7: reported, not binding.) | controls e1453=0.0323, d4015=0.1077; guard-fired S: S1=0.1457, S4=0.3119, S5=0.3119 (all < min(controls)=0.0323: no); guard-clean S: S2=0.3715, S3=0.3271 (none > max(controls)=0.1077: no) | FAIL |
| V2-NONREG | the four Phase B bars (mean(ABOVE)>mean(BELOW); <=1 boundary inversion; e1453 above no ABOVE game; 573562833174 > e1453dac5445) PASS for drama_v2 on the Phase B pods. | 1. mean(ABOVE)=0.1172 vs mean(BELOW)=0.0355 -> YES; 2. inversions=0 (min ABOVE=0.1077) -> YES; 3. e1453=0.0323 <= min(ABOVE)=0.1077 -> YES; 4. 573=0.2162 > e1453=0.0323 -> YES | PASS |

Spearman(drama_v2, blind mean) over the Phase D seven: **-0.3063** (reported, not binding; Phase D random-rollout drama scored −0.68 on the same seven).

## Verdict

```
DESCRIPTOR_V2_KILL
```

## Notes

- BLOCK-WIN-IN-1 is constructed exactly (no win-condition-delta approximation): the engine's step() is trust-the-caller, so the forced opponent action is a scratch-clone restore + current_player override + step; the engine's own win check decides. Placement-only per the prereg (opponent pass/move/multi-place wins are not blocked; multi_place games are scanned one placement deep — the S1-style first-strike threat).
- Clone = create-once scratch engine + full mutable-state snapshot/restore (measured faster than copy.deepcopy ~1.3 ms and re-create+replay ~15 ms per clone; verified state-identical to deepcopy+step in test_rc2_descriptor_v2.py). Live engines are never mutated by the scans.
- REACH is threshold-family-only (n/a elsewhere); binding only on S2 (must fire) and e1453 (must not). Other threshold games' REACH flags are reported, not binding. TILT on d4015 is reported, not binding.
- metrics/descriptors.py, metrics/rollout_traces.py, training/, game_engine/, evolution/ untouched; drama_v2 imports the locked obs_drama_for_rollout (threshold-family dual parameterization and all formula choices inherited unchanged).
