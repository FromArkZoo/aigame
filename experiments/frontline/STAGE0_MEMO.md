# Stage 0a — FRONTLINE kernel memo (prereg 3a378dd, pinned)

## 1. Corrected flip thresholds (own-side d2 support included)

| position | min attackers | distances |
|---|---|---|
| lone stone | 3 | d1+d1+d2 |
| 2-chain end | 4 | d1+d1+d1+d2 |
| 3-chain end (linear; own d2 term) | 4 | d1+d1+d1+d1 |
| 4-chain interior (linear) | 6 | d1+d1+d1+d1+d2+d2 |

## 2. Analytic engagement saturation (interior-cell model)

| E \ fill | 10% | 20% | 41% |
|---|---|---|---|
| 0.75 | 0.039 | 0.227 | 0.717 |
| 1.0 | 0.013 | 0.107 | 0.544 |
| 1.25 | 0.003 | 0.042 | 0.376 |

## 3. Margin swing at E=1.0 (engine-applied, pinned set)

Pinned cells (cell index, axial (q, r) with cell = r*W + q; W = 22; second-rank offset = +2W, axial (0, +2) = two rows behind, verified distance 2 from each chain stone):

- straggler: {24(2, 1):P1, 46(2, 2):P2, 67(1, 3):P1} -> P1 plays 2(2, 0)
- 2chain_far: {24(2, 1):P1, 45(1, 2):P1, 46(2, 2):P2, 47(3, 2):P2, 67(1, 3):P1} -> P1 plays 2(2, 0)
- 2chain_near: {24(2, 1):P1, 25(3, 1):P1, 45(1, 2):P1, 46(2, 2):P2, 47(3, 2):P2} -> P1 plays 2(2, 0)
- 3chain_4d1: {24(2, 1):P1, 45(1, 2):P1, 46(2, 2):P2, 47(3, 2):P2, 48(4, 2):P2, 67(1, 3):P1} -> P1 plays 25(3, 1)
- 2chain_far_rank2: {24(2, 1):P1, 45(1, 2):P1, 46(2, 2):P2, 47(3, 2):P2, 67(1, 3):P1, 91(3, 4):P2, 92(4, 4):P2} -> P1 plays 2(2, 0)
- 2chain_near_rank2: {24(2, 1):P1, 25(3, 1):P1, 45(1, 2):P1, 46(2, 2):P2, 47(3, 2):P2, 91(3, 4):P2, 92(4, 4):P2} -> P1 plays 2(2, 0)
- 3chain_4d1_rank2: {24(2, 1):P1, 45(1, 2):P1, 46(2, 2):P2, 47(3, 2):P2, 48(4, 2):P2, 67(1, 3):P1, 91(3, 4):P2, 92(4, 4):P2} -> P1 plays 25(3, 1)

| config | before | after | swing | stones flipped |
|---|---|---|---|---|
| straggler | 0 | 0 | 0 | 1 |
| 2chain_far | 0 | 0 | 0 | 2 |
| 2chain_near | 0 | 0 | 0 | 2 |
| 3chain_4d1 | -3 | 0 | 3 | 2 |
| 2chain_far_rank2 | -1 | 0 | 1 | 1 |
| 2chain_near_rank2 | 0 | 0 | 0 | 2 |
| 3chain_4d1_rank2 | -3 | 1 | 4 | 1 |

A d1-support variant (second rank at +W) suppresses the flip (swing +1/+2, 0 flips); recorded during build review.


Mean swing, front-only (chain rows, vacuum + rank2): 1.33; all rows (incl. straggler): 1.14. KILL-0a1 applied to the lower of the two.

**KILL-0a1: mean front margin swing = 1.14 (PASS)**
**KILL-0a2: engaged@20% fill, E=1.0 = 0.107 (PASS)**

## 4. Stage 0b smoke

Pinned cell: `f_frontline_E1p00_M8` (E=1.00, M_end=8, komi_cells=0, seed=7). 1000 random rollouts + 200 per scripted matchup. All scripted pairings are deterministic: each row is 200 identical games (run as registered).

| matchup | n | flips/g | mean len | score_margin% | double_pass% | timeout% | other% | mean s1 | mean s2 | eng@80 | eng final | P1 win% | P2 win% | draw% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| random | 1000 | 29.242 | 168.2 | 66.4 | 0.1 | 33.5 | 0.0 | 28.38 | 28.05 | 0.024 | 0.145 | 51.5 | 48.5 | 0.0 |
| chain_vs_chain | 200 | 25.000 | 200.0 | 0.0 | 0.0 | 100.0 | 0.0 | 12.00 | 10.00 | 0.004 | 0.045 | 100.0 | 0.0 | 0.0 |
| packer_vs_packer | 200 | 0.000 | 200.0 | 0.0 | 0.0 | 100.0 | 0.0 | 0.00 | 0.00 | 0.000 | 0.000 | 0.0 | 0.0 | 100.0 |
| chain_vs_mirror | 200 | 3.000 | 200.0 | 0.0 | 0.0 | 100.0 | 0.0 | 4.00 | 6.00 | 0.000 | 0.021 | 0.0 | 100.0 | 0.0 |
| chain_vs_passbot | 200 | 0.000 | 200.0 | 0.0 | 0.0 | 100.0 | 0.0 | 0.00 | 0.00 | 0.000 | 0.000 | 100.0 | 0.0 | 0.0 |

Engaged-share trajectory (mean engaged_frac at ply 20 / 40 / 80 / final):

| matchup | @20 | @40 | @80 | final |
|---|---|---|---|---|
| random | 0.000 | 0.003 | 0.024 | 0.145 |
| chain_vs_chain | 0.037 | 0.079 | 0.004 | 0.045 |
| packer_vs_packer | 0.000 | 0.000 | 0.000 | 0.000 |
| chain_vs_mirror | 0.000 | 0.000 | 0.000 | 0.021 |
| chain_vs_passbot | 0.000 | 0.000 | 0.000 | 0.000 |

Mover-signed margin swing per flip-ply (mean, n flip-plies): random -1.05 (n=22605), chain_vs_chain -1.00 (n=800), packer_vs_packer n/a (n=0), chain_vs_mirror -1.50 (n=400), chain_vs_passbot n/a (n=0)

**KILL-0b1: max(random, chain) flips/game = 29.242 >= 1.0 (PASS)**
**KILL-0b2: mutual-packer mean total score = 0.000 <= 2.0 (PASS)**
**KILL-0b3: random engaged_share at min(80, end) = 0.024 in (0.01, 0.60) (PASS)**

**MIRROR_CONTINGENCY FIRED: mirror secured >= draw in 100% of games vs front-builder (threshold 30%). Registered contingency: ONE licensed switch to W=21 + Stage-0a rerun — owner decision required before Stage 1. Not a kill; build continues.**

PassBot probe: P1 (front-builder) win share 100%, timeout share 100%, mean final scores 0.0-0.0 (stones tiebreak; pass-bot placed zero stones and can never win per the participation clause).
