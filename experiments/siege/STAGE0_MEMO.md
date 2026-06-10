# Stage 0a — flip thresholds at r=2/d=0.5/eps=0 (computed from engine kernels)

| position | min attackers | distances |
|---|---|---|
| lone stone | 3 | d1+d1+d2 |
| chain end (1 own neighbour) | 4 | d1+d1+d1+d2 |
| chain interior (2 own neighbours) | 5 | d1+d1+d1+d1+d2 |
| dense interior (3 own neighbours) | 8 | d1+d1+d1+d2+d2+d2+d2+d2 |

engine cross-check: PASS (2 adjacent: net=+0.0000, no flip; 2 adjacent + 1 distance-2: net=-0.2500, flip)

**Pre-registered kill check: lone stone needs 3 attackers -> PASS**
