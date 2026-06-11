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

Pinned cells (cell index, axial (q, r) with cell = r*W + q; W = 22; second-rank offset = +W, axial (0, +1) = next row, verified distance 1 from each chain stone):

- straggler: {24(2, 1):P1, 46(2, 2):P2, 67(1, 3):P1} -> P1 plays 2(2, 0)
- 2chain_far: {24(2, 1):P1, 45(1, 2):P1, 46(2, 2):P2, 47(3, 2):P2, 67(1, 3):P1} -> P1 plays 2(2, 0)
- 2chain_near: {24(2, 1):P1, 25(3, 1):P1, 45(1, 2):P1, 46(2, 2):P2, 47(3, 2):P2} -> P1 plays 2(2, 0)
- 3chain_4d1: {24(2, 1):P1, 45(1, 2):P1, 46(2, 2):P2, 47(3, 2):P2, 48(4, 2):P2, 67(1, 3):P1} -> P1 plays 25(3, 1)
- 2chain_far_rank2: {24(2, 1):P1, 45(1, 2):P1, 46(2, 2):P2, 47(3, 2):P2, 67(1, 3):P1, 69(3, 3):P2, 70(4, 3):P2} -> P1 plays 2(2, 0)
- 2chain_near_rank2: {24(2, 1):P1, 25(3, 1):P1, 45(1, 2):P1, 46(2, 2):P2, 47(3, 2):P2, 69(3, 3):P2, 70(4, 3):P2} -> P1 plays 2(2, 0)

| config | before | after | swing | stones flipped |
|---|---|---|---|---|
| straggler | 0 | 0 | 0 | 1 |
| 2chain_far | 0 | 0 | 0 | 2 |
| 2chain_near | 0 | 0 | 0 | 2 |
| 3chain_4d1 | -3 | 0 | 3 | 2 |
| 2chain_far_rank2 | -2 | 0 | 2 | 0 |
| 2chain_near_rank2 | -1 | 0 | 1 | 0 |

**KILL-0a1: mean front margin swing = 1.20 (PASS)**
**KILL-0a2: engaged@20% fill, E=1.0 = 0.107 (PASS)**
