# RC2 Phase D — blind-slate agent-team eval readout

**Decision criteria:** pre-registered in `PREREGISTRATION.md` (locked `f297eaf` before any
verdict data; blind pack committed `9e9abb2` before teams launched). 3 independent blind
teammates × 7 games = 21 verdicts, all filed before unblinding. Validity band PASSED →
the grammar is licensed.

## Verdict: **PHASE_D_NOGO — high drama does not transfer to agent-judged quality beyond the anchor range; archive integration is SHELVED pending descriptor redesign**

| bar | result | detail |
|---|---|---|
| VALIDITY | **PASS** | mean(C+ R8 anchor) = 3.83 ∈ [3.7, 4.5] (low edge; prior 4.10) |
| BAR D1 (slate beats plateau) | **FAIL** | archive slate mean 2.83 − C− 3.90 = **−1.07** (floor +0.3) |
| BAR D2 (top game ≥ 3.9) | **FAIL** | best slate game (S2) mean 3.20 |

## Unblinded table (Overall, 3 teams)

| label | identity | pooled drama | T1 | T2 | T3 | mean |
|---|---|---:|---:|---:|---:|---:|
| B | **C− (e1453, R21 GE-top plateau, prior 3.66)** | 0.048 | 3.6 | 4.3 | 3.8 | **3.90** |
| F | **C+ (d4015 R8 anchor, prior 4.10)** | 0.124 | 4.1 | 4.0 | 3.4 | **3.83** |
| D | S2 threshold torus custodian | 0.344 | 3.4 | 3.3 | 2.9 | 3.20 |
| E | S3 connection moore-3D CA | 0.306 | 2.3 | 3.7 | 3.3 | 3.10 |
| C | S5 territory hex place | 0.262 | 2.7 | 3.9 | 2.6 | 3.07 |
| G | S4 territory hex move+place | 0.280 | 2.6 | 3.9 | 2.5 | 3.00 |
| A | S1 connection moore-5D multi-place CA | 0.384 | 1.9 | 1.5 | 1.9 | **1.77** |

**Spearman(drama, blind mean) over all 7 games = −0.68.** Within the anchor range drama
ranked the controls correctly in Phase B; optimized 2–3× beyond it, the correlation
INVERTS: the archive's top-drama elite is the worst game any campaign has fielded (1.77,
unanimous), and the plateau control beat every archive game.

## Mechanism (from the evaluators' play, not our speculation)

- **S1 (drama 0.384): forced first-turn win.** P1 places 3 collinear stones along the
  3-cell axis inside one multi-place turn; P2 never moves. All three teams found it
  independently. Its drama is CA churn measured on random rollouts that never play the
  winning line.
- **S2 (0.344): unreachable threshold → draw saturation** under competent play (full
  board scores ≈ −0.7 vs threshold 36.9); random rollouts end differently, so the
  archive's validity guard (rollout draws < 50%) did not catch it.
- **S4/S5 (0.28/0.26): tempo races with near-zero agency** — P1 wins 28–27 by parity in
  ~all competently-played lines; random-rollout lead oscillation produced the drama.
- **S3 (0.306): real two-sided CA play but chaotic and first-mover-tilted** — the only
  slate game where any team found genuine counterplay.
- **Root cause, stated plainly: obs_drama is computed on random+greedy rollout traces.
  Archive search optimized for games whose RANDOM-play trajectories oscillate — first-turn
  wins, dead win conditions, and parity races all maximize winner-behindness in rollouts
  while having no competent-play depth. Phase B's anchors couldn't reveal this because
  they were pre-shaped by selection for playability; unconstrained optimization found the
  proxy's failure modes within 600 evals.** This is Goodhart-under-optimization of the
  measurement policy, not an archive-mechanics failure (Phase C's machinery did exactly
  what it was asked: it climbed the signal).

## Reported, not binding (per prereg)

- Fairness/role splits: A, E, C, G, D flagged P1-favored >80/20 under competent play by
  at least one team (A unanimous, structural); B and F read balanced (both seats won).
- CA-churn question: ANSWERED — in S1 the CA layer is fully inert noise; in S3 it
  contributes one real mechanic (sacrificial cascade disruption) inside an otherwise
  first-mover-tilted race.
- Controls nearly tied (3.90 vs 3.83) and C− scored +0.24 over its R21 prior — within
  3-team drift; the validity band (registered on C+ only) held at its low edge.
- Team agreement is strongest exactly where it matters: unanimous bottom for S1
  (1.5–1.9), top-2 = {B, F} for all three teams.

## Registered consequence (per the locked NOGO branch)

Archive integration is shelved. **Descriptor redesign precedes any further archive
spend**, with the registered first candidates now sharpened by mechanism:
1. **Competent-play traces**: compute drama on stronger-policy rollouts (greedy-vs-greedy
   minimum; planning/MCTS where budget allows) — random-play drama is the broken proxy.
2. **Agency/decisiveness guards at insertion**: reject genomes with first-K-ply forced
   wins (scripted-rush probe), unreachable win conditions (threshold reachability under
   competent play), and >80/20 seat tilt under mirrored competent rollouts.
3. CA-churn weighting only after 1–2 (S3 suggests CA is salvageable, not the root cause).

Phase C's validated machinery (qd_archive, eval-count matching, re-eval) is unaffected
and waits on a trustworthy quality signal. GE remains diagnostic-only. The Frontline
rebuild (SIEGE RESULTS §7) remains the registered parallel thread.
