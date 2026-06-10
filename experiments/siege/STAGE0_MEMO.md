# Stage 0a — flip thresholds at r=2/d=0.5/eps=0 (computed from engine kernels)

| position | min attackers | distances |
|---|---|---|
| lone stone | 3 | d1+d1+d2 |
| chain end (1 own neighbour) | 4 | d1+d1+d1+d2 |
| chain interior (2 own neighbours) | 7 | d1+d1+d2+d2+d2+d2+d2 |
| dense interior (3 own neighbours) | 99 | none<=7 |

**Pre-registered kill check: lone stone needs 3 attackers -> PASS**
