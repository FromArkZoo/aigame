# Run 15 Evaluation Report

**Database**: `genesis_v2_run15.db`
**Config**: 11 generations (0-10), pop 50, 10k training budget, 2 runs, 25% immigration, 2D-only, ca-prob 0.3, sim-prob 0.5, sim×CA bias 0.4; seeded with R14 champion `deb4dfe0382d` and R13 human winner `531634cee158`
**Run duration**: ~22h (launched 2026-04-23 14:21, completed 2026-04-24 ~13:00)
**R15 engine/scoring changes**: CA step-loop symmetry, CA rule-table symmetry, double-pass→draw, new seat-balance metric using random-vs-random heuristic probe, sim×CA co-occurrence bias
**Human evaluation protocol**: 22 team evaluations (1 pilot + 6 production on rank 1, 5 each on ranks 2, 3, and 5)

---

## Executive Summary

**R15 produced no breakthrough game**. All four tier-1 games scored 1.8–3.4/10 in human evaluation. The GE champion (`1565501cfecf`, simultaneous torus threshold) scored 2.43 — the *lowest* champion human-rating any run has produced, below R14's 4.57 and well below R8's 8/10. The lowest-scored game in the evaluation set was the sim×CA candidate (`2e5262b76311`) at 1.80 — confirming that once the R14 engine bug is fixed, the sim×CA "signal" is simply gone.

The run's most important outcome is again **not a game** but a set of diagnostic findings. Human evaluation surfaced **three new engine issues** and confirmed **two known failure modes that the generator did not filter**:

### New engine issues (not in R14 eval)
1. **`_check_threshold` iteration-order bias** (`engine_v2.py:748-761`): when both players cross the threshold on the same tick (common in simultaneous games), `for player in (1, 2)` returns on P1 regardless of margin. 2 of 7 champion teams documented P2 outscoring P1 (e.g., 42.6 vs 41.85, 43.88 vs 39.30) but P1 still winning.
2. **`_check_connection` iteration-order bias** (`engine_v2.py:741`): same pattern in connection-win games. Triggered the sim×CA champion's P1 bias on top of the torus-wrap bug.
3. **CA step-ordering bias**: even with both the step-loop fix *and* the rule-table symmetry fix in place, P1's CA step runs before P2's each tick. In any empty-cell birth race with mixed neighbors, P1 wins by order. Team-21 measured 28 P1 / 9 P2 / 13 draws in 50 random sim×CA games — clear residual bias.

### Known issues the generator failed to filter
4. **Torus + connection = 2-move forced win**: any cell and its wrap-opposite count as connected on the torus, so a single stone at `(k, 0)` connects to its wrap-adjacent `(k, 7)`. Documented as broken in SUMMARY.md for R10 but the generator permitted it again in R15. All 5 sim×CA teams found the 2-move win.
5. **Moore + surround-capture = dead rule**: 8-neighbor adjacency makes interior stones structurally ungappable. 0 captures across 15 rank-3 games. Same pattern as R13/R14.

### Seat-balance metric has a blindspot
The new R15 seat-balance metric uses a random-vs-random probe — but teams 7, 14, and most champion teams explicitly flagged that bias only appears under *skilled* play. Random-vs-random on rank-2 went 20/30 P1 (within tolerance), but skilled greedy-vs-greedy goes 3/3 P1. The metric I added is a strict improvement over nothing but fails to catch this class of bias.

---

## Final Leaderboard — GE vs Human

| GE Rank | Game ID | GE | Mechanics | Human Mean | Stdev | Teams | Human Rank | Δ |
|------|---------|------|------|-----------|-----|-----|-----|---|
| 1 | `1565501cfecf` | 0.318 | SIM torus threshold, no capture, no CA | **2.43** | 0.5 | 7 | **3** | −2 |
| 2 | `d8f2ae54f399` | 0.255 | Alt grid surround threshold, influence | **3.40** | 0.9 | 5 | **1** | +1 |
| 3 | `3bde3258978e` | 0.201 | Alt moore surround threshold, influence | **3.10** | 0.5 | 5 | **2** | +1 |
| 5 | `2e5262b76311` | 0.145 | SIM torus CA connection adj_to_own | **1.80** | 0.4 | 5 | **4** | 0 |

**GE ranking inverted** at the top: the GE champion is 3rd by human verdict; the GE rank-2 game is actually best. This is a worse inversion than R13 (rank-3 was human winner there) and R14 (GE top held but all scores compressed).

---

## Per-Game Findings

### Game 1 — `1565501cfecf` "Sim Torus Threshold" (GE rank 1, human rank 3)

**Format**: 2D 8×8 torus, simultaneous turn structure (pieces_per_turn=1, same-cell collisions annihilate), place-only on empty cells (no adjacency constraint), no capture, **radius-3 signed influence** (strength 0.966, decay 0.587), threshold win at effective own-cell sum > 38.627. Gen 9. No CA.

**Team-by-team Overall scores**: pilot 2, team-1 3, team-2 2, team-3 3, team-4 3, team-5 2, team-6 2 → **mean 2.43, stdev 0.5** (tightest consensus in the run).

**Consensus findings**:
- **P1 wins every competent game.** Tie-break bias in `_check_threshold` iteration: when both players cross threshold on the same tick, `for player in (1, 2)` returns on P1 first. Observed:
  - Pilot Game 1: both 39.98 at R10 → P1 wins
  - Team-3 Game 1: both 38.864 at R10 → P1 wins
  - Team-6 Game 1: both 39.976 at R10 → P1 wins
  - Team-4 Game 1: P2 at 42.60, P1 at 41.85, both cross → **P1 still wins despite P2's margin**
  - Team-4 Game 3: P2 at 43.88, P1 at 39.30, both cross → **P1 still wins despite P2's +4.58 margin**
  - Team-2 Game 2: P2 at 41.98, P1 at 39.40, both cross → **P1 still wins despite P2's margin**
- **Monotone state**: no capture, no CA, no movement → trailing player cannot recover.
- **Dominant strategy**: "antipodal 3×3 cluster + extension" resolves every game in 10-12 rounds.
- **Collision mechanic strategically inert**: never optimal in mirror play, mutual cost equals P1's cost.
- **Dominant opener is trivial**: antipodal placement produces zero interaction in radius-3 kernel on 8×8 torus.

**Closest analog**: Blotto with spatial coupling + Tumbleweed influence projection. Team-6's framing: "simultaneous didn't eliminate first-mover advantage — merely relocated it from move-order to win-check-order."

**Killer flaws**:
1. `_check_threshold` iteration-order bias gives P1 every same-tick crossing regardless of score margin
2. No recovery mechanic (trailing player cannot catch up)
3. Collision mechanic decorative — never fires in optimal play
4. Dominant strategy deterministic, resolves in 10-12 rounds

**Best quality**: Signed radial influence field is a clean, legible scoring primitive. Multiple teams suggested porting the scoring mechanic to a fairer game framework.

---

### Game 2 — `d8f2ae54f399` "Grid Influence Surround Threshold" (GE rank 2, human rank 1)

**Format**: 2D 8×8 grid, alternating, place-anywhere, Go-style surround capture (threshold 1, effectively inert), radius-1 signed influence (strength 0.932, decay 0.510), threshold win at own-cell sum > 22.645. Gen 10.

**Team-by-team Overall scores**: team-7 3, team-8 3, team-9 3, team-10 3, team-11 5 → **mean 3.40, stdev 0.9**.

**Consensus findings**:
- **Surround capture is inert**: 0 captures across 5 teams × 3 games = 15 games, 330+ moves total. 4-move capture cost far exceeds the threshold-race timeline (21-26 moves).
- **P1 dominates under skilled play**: teams 7, 8, 9, 10 all saw P1 win 3/3 (or 2/3 + seat-swap P2 win via P1 blunder). Team-11 found a specific P2 counter ("edge-sprawl") that exploits the non-torus grid's reduced edge influence leakage.
- **Dominant strategy**: greedy +2.84 "2-adjacency" cell selection, falling back to "1-adjacency" (+1.89).
- **Zero double-pass draws** across all 15 games — threshold is reachable under both players' play.

**Disagreement**: team-11's Overall 5 is the run's highest outlier. Their finding (edge-sprawl P2 counter) is specific and reproducible but requires non-greedy P2 play. The other 4 teams restricted themselves to symmetric or greedy-greedy play and saw 100% P1.

**Closest analog**: "Go-lite with Bouzy-style influence scoring and threshold win". ~70% skill transfer for a Go player per multiple teams. Novel wrinkle: captured-stone-influence-persistence (value doesn't reset on capture) has no Go analog.

**Killer flaws**:
1. First-mover advantage (100% under greedy-vs-greedy; 67% under random)
2. Capture rule is vestigial — never fires in skilled play
3. Narrow dominant strategy
4. Short games (21-26 moves) leave no middlegame

**Best quality**: The adjacency-multiplier compounding mechanic, combined with the mutual-contact influence nerf (enemy adjacency subtracts from both players' own-cell values). This IS a real emergent property, and it's what lifted team-11's Novelty 6.

---

### Game 3 — `3bde3258978e` "Moore Influence Surround Threshold" (GE rank 3, human rank 2)

**Format**: Identical rules to Game 2 **except topology = moore (8-connected Chebyshev)**. This was the intended A/B test on topology.

**Team-by-team Overall scores**: team-12 4, team-13 ~2.5, team-14 3, team-15 3, team-16 ~3 → **mean ~3.10, stdev 0.5**.

**A/B comparison vs Game 2**: Moore version scores very slightly lower (3.10 vs 3.40). The Moore topology does NOT help — it further *entrenches* the dominant-cluster strategy (8 neighbors give even more compound) and makes capture structurally impossible (8 liberties to close). Grid version is strictly better per human verdict.

**Consensus findings**:
- **P1 wins 3/3 in every team's playthroughs** (team-13 ran 20-trial greedy probe: 20/20 P1).
- **Capture completely dead on Moore**: 0 captures in 15 scored games across teams.
- **Teams land on same optimal strategy independently**: team-13 "tight-cluster center", team-14 "compact central cluster", team-15 "build densest Moore cluster". One dominant strategy.
- Team-12 is the outlier at Overall 4: they found 2-ply lookahead can beat 1-ply in P2's seat (Depth 5).
- Team-14 explicitly flagged the R15 seat-balance metric as a false-positive here: "30 random-vs-random games split 13/16/1 (P2 slight edge) — passes the seat-balance check. Under skilled play first-mover wins 3/3."

**Closest analog**: Tumbleweed with 8-neighbor radius-1 influence, Go-shaped capture layer on top that never activates. Identical analog to Game 2.

**Killer flaws**: Same as Game 2 plus Moore-topology-dead capture.

**Best quality**: The mutual-contact influence penalty (territorial separation inverse to Go's invasion dynamic). Same emergent property as Game 2; topology doesn't add to it.

**A/B takeaway**: identical rules on grid outperform moore for human play because grid leaves some edge asymmetry for counter-strategies; moore flattens everything into dense-cluster-wins.

---

### Game 5 — `2e5262b76311` "Sim-CA Torus Connection" (GE rank 5, human rank 4)

**Format**: 2D 8×8 torus, **simultaneous**, placement `adjacent_to_own` (first_move_anywhere=True), no capture, **CA with steps_per_turn=2 and ~6 non-identity transitions** (earlier eval-prompt claim of "75/75 non-identity" was my error — my Python identity check was broken by JSON string-key deserialization), connection win (dim 1 vs dim 0). Gen 3.

**Team-by-team Overall scores**: team-17 2, team-18 2, team-19 2, team-20 2, team-21 1 → **mean 1.80, stdev 0.4**. Lowest-scored and tightest-consensus game in the run.

**Consensus findings** (5 of 5 teams converge on the same diagnosis):
- **2-move torus-wrap forced win**: `connects_faces` treats wrap-adjacent cells as connected. P1 plays `(k, 0)` then `(k, 7)` — one cell is wrap-adjacent to the other, satisfying `adjacent_to_own` AND completing the dim-1 connection. This is a regression of the known R10 bug; the generator should have filtered torus+connection games.
- **`_check_connection` iteration-order bias**: same shape as `_check_threshold` — when both players complete connection same tick, `for player in (1, 2)` returns P1. Team-18's empirical probe: 191/200 P1 wins in wrap-vs-wrap races.
- **CA is dormant**: games end in 2-5 rounds before CA rules can fire. Only 6 non-identity rules in a 75-entry table; most games never trigger any.
- **CA step-order bias** (team-21): even with rule-table symmetry enforced, P1's step runs first in every tick. In a 50-game random probe, 28 P1 wins / 9 P2 / 13 draws. This is an ordering artifact that the R15 symmetry fixes did not address.
- **Simultaneous mechanic ineffective**: teams 17-18 note P2's only counter is same-cell collision blocking, which is a matching-pennies guess across 8 columns (~12.5% success) and P1 simply re-picks.
- **Collisions rarely fire**: the `adjacent_to_own` placement constraint + 2-tick game length means collision opportunities are minimal.

**Closest analog**: Hex on a torus (with simultaneous overlay and dormant CA). Torus + connection is a known-degenerate Hex variant; the CA and simultaneous layers add no emergent content.

**Killer flaws** (ranked by frequency across 5 teams):
1. Torus-wrap 2-move forced win (5/5 teams)
2. `_check_connection` P1 iteration-order bias (5/5 teams)
3. CA dormant (5/5 teams)
4. Adjacency-restricted placement blocks defense (team-17, team-18)
5. CA step-order bias gives P1 contested births (team-21)

**Verdict on the R15 sim×CA premise**: Dead. Post-engine-fix, the sim×CA signal from R14 did not reproduce. Teams explicitly framed this as the hypothesis being answered: "did sim×CA break through post-fix?" → **no**. The R14 apparent signal was the CA step-loop bug making P1-biased CA games look non-trivial in GE (high non-triv, high diversity). With the bug fixed AND the rule table symmetric, sim×CA games have nothing to offer beyond what pure simultaneous or pure CA games offer.

---

## Cross-Cutting Discoveries

### 1. NEW engine issue: `_check_threshold` iteration-order bias

**Severity**: HIGH — structurally determines outcome of every tied same-tick threshold crossing
**Reporters**: pilot, teams 1-6 on champion (7/7 unanimous), plus team-7/19 analogously for other check functions

**Details**: `engine_v2.py:748-761`:
```python
def _check_threshold(self, threshold: float) -> None:
    for player in (1, 2):
        total_value = sum(...)
        effective = total_value if player == 1 else -total_value
        if effective > threshold:
            self._winner = player
            self.done = True
            return
```

When both players cross the threshold on the same tick (the common case in symmetric simultaneous play, and also possible in alternating games ending in the same turn), the loop returns on P1. Concrete data from eval:
- Pilot: 2/3 symmetric ties → P1 wins by iteration order
- Team-4 Game 1: P2 scored 42.60, P1 scored 41.85, both cross → P1 wins
- Team-4 Game 3: P2 scored 43.88, P1 scored 39.30, both cross → P1 wins
- Team-2 Game 2: P2 scored 41.98, P1 scored 39.40, both cross → P1 wins

**This is worse than a symmetric-tie bug** — P1 wins any same-tick crossing regardless of margin.

**Fix directions**:
1. **Draw on simultaneous crossings**: if both players cross same tick, winner = None.
2. **Margin-based resolution**: compare effective margins, higher wins.
3. **Check-after-all-effects**: compute both players' effective values first, then decide.

Recommended: option 2 (margin-based) — it preserves decisive outcomes but eliminates the iteration-order artifact.

### 2. NEW engine issue: `_check_connection` iteration-order bias

Same pattern as #1 for connection-win games. `engine_v2.py:~741` — `for player in (1, 2)` returns on P1. Teams 17-21 on sim×CA and team-19 on threshold-crossings both confirmed. Same fix applies.

### 3. NEW engine issue: CA step ordering favors P1

**Severity**: MEDIUM — residual bias even after step-loop fix and rule-table symmetry
**Reporter**: team-21 (primary), teams 17-20 implicit

**Details**: The R15 step-loop fix runs both perspectives per step:
```python
if uses_ca:
    for _ in range(self.game.ca_rule.steps_per_turn):
        self._run_ca_step(1)
        self._run_ca_step(2)
```

P1's step runs first. If the CA has a birth rule that fires on an empty cell with mixed neighbors, P1 claims the cell on its step. P2's subsequent step sees the cell as owned (no longer empty) and skips it. So P1 wins any CA-driven birth race.

**Team-21 empirical**: 50 random sim×CA games → 28 P1 / 9 P2 / 13 draws. Residual P1 bias even with structurally symmetric rule tables.

**Fix directions**:
1. **Compute both perspectives from shared snapshot, apply both outcomes simultaneously**: if both perspectives would birth different owners, resolve as draw (cell stays empty) or collision-annihilation.
2. **Randomize order**: coin-flip whether P1 or P2 runs first each tick.
3. **Single combined rule table** that operates on actual state (not perspective) and treats ties symmetrically.

Option 1 is the cleanest fix and mirrors the collision-annihilation semantic already used for placements in simultaneous games.

### 4. Known issue: torus + connection win still broken

Documented in SUMMARY.md for R10. Generator should filter this combo. Resurfaced in R15 on `2e5262b76311`. All 5 sim×CA teams found the 2-move wrap-win.

**Fix**: Generator quick-reject: `if topology == "torus" and win_condition == "connection": reject`.

### 5. Known issue: Moore topology makes surround-capture dead

Recurring pattern across R13, R14, R15 evaluations. Moore 8-connectivity means interior stones have 8 liberties; capture cost exceeds threshold-race timeline. 0 captures in 15 games on rank-3.

**Fix direction**: Either (a) downgrade moore→grid when capture is present (already done for CA per generator code, should be applied to classical capture too), or (b) up the capture threshold on Moore to require actual group surrounds.

### 6. R15 seat-balance metric has a skilled-play blindspot

**Severity**: MEDIUM — the new metric is strict improvement over R14 but misses the class of bias that trained play reveals
**Reporters**: teams 7, 11, 14 on grid/moore surround games; most champion teams

**Details**: The R15 metric probes `heuristic_p1_winrate` using random-vs-random seat-swapped games. This catches *structural* bias that random play can't escape (e.g., R14's CA step-loop bug). But it misses bias that requires skilled play to surface, because:
1. Random play on the champion rarely produces symmetric threshold crossings — the tie-break bias simply doesn't fire often enough to move the metric.
2. Random play on rank-2 goes 67% P1 (caught!), but games like rank-3 Moore go 13/16/1 in random (balanced) while 20/20 P1 under greedy.
3. Complex strategies that expose bias (edge-sprawl counter on rank-2, 2-ply P2 lookahead on rank-3) don't appear in random probes.

**Fix direction for R16**: Add a **greedy-vs-greedy** or **1-ply-lookahead** probe paired with seat swap, in addition to (not replacing) the random probe. The greedy probe surfaces bias under deterministic "best simple heuristic" play, which covers the R15 champion's case.

### 7. Metric/human divergence is worse in R15 than R14

| Run | Top-GE game human rank | Top-GE to human correlation (ordinal) |
|---|---|---|
| R13 | Tier-1 human winner was rank 3 by GE | Inverted at the top |
| R14 | GE champion held top human rank | Compressed but correctly ordered |
| R15 | GE champion is 3rd by human | **Fully inverted at the top** |

This is the **worst GE/human inversion the project has observed**. Part of it is the three new engine issues (tie-break biases) that the metric has no visibility into. Part is the seat-balance blindspot.

---

## Failure Modes Observed

| Failure | Games affected | Team-evaluations documenting |
|---|---|---|
| `_check_threshold` P1 iteration bias | Champion (sim torus threshold) | 7/7 champion teams |
| `_check_connection` P1 iteration bias | Rank 5 (sim×CA connection) | 5/5 sim×CA teams |
| CA step-order P1 bias | Rank 5 (sim×CA) | team-21 primary, 17-20 implicit |
| Torus-wrap 2-move connection win | Rank 5 (sim×CA) | 5/5 sim×CA teams |
| Moore makes surround dead | Rank 3 | 5/5 rank-3 teams |
| First-mover advantage (alternating games) | Rank 2, Rank 3 | 10/10 teams |
| Seat-balance metric misses skilled-play bias | Champion, Rank 2, Rank 3 | explicit flags from teams 7, 11, 14 |
| Simultaneous collision decorative in optimal play | Champion, Rank 5 | 10/12 sim teams |
| Capture rule inert (all games) | Rank 2, Rank 3 | 10/10 teams |

---

## Recommendations for Run 16

R15's engineering changes were correct in direction (CA step-loop fix, rule-table symmetry, double-pass draw, seat-balance metric) but the human eval exposed that fitness engineering alone will not catch all engine bias. R16 needs **both** more engine fixes AND a stronger metric.

### Engine fixes (must land before R16)

1. **Fix iteration-order biases in `_check_threshold` and `_check_connection`** (`engine_v2.py:741, :748-761`). Recommended: margin-based resolution. When both players cross same tick, compare effective margins; higher wins; equal is a draw.

2. **Fix CA step-ordering bias** (`engine_v2.py:255-258`). Recommended: compute both perspectives from shared pre-step snapshot, then apply both outcomes. If a cell is birthed to both players by different perspectives, treat as a collision (cell stays empty).

3. **Generator: quick-reject torus + connection games**. Add to `quick_reject()` in `generator_v2.py`.

4. **Generator: downgrade moore → grid when capture is present** (currently only done for CA). Same pattern.

### Scoring changes

5. **Add a greedy-vs-greedy seat-balance probe** alongside the random probe. Take worst of the three signals (trained, random, greedy).

6. **Optional: weight seat-balance higher in composite** — currently it multiplies with floor 0.2. Consider a hard cap (e.g., composite × min(1.0, 2*seat_balance)) so severe imbalance caps the total.

### Evolutionary strategy

7. **Reconsider seeding strategy**. R15 was seeded with R14's champion `deb4dfe0382d` and R13's human winner `531634cee158`. Neither appears in R15's top 20. The seed genes may have been actively bred out because the R14 champion's "capture-as-poison" mechanic requires custodian capture + signed influence, a combination the R15 generator rarely preserves through mutation/crossover.

8. **Reconsider the sim×CA focus**. R15 produced 61 sim×CA games (target met) but they fail to survive evaluation. Two possible conclusions:
   - (a) Sim×CA genuinely adds no value once the engine is bias-free. Reduce to baseline probability.
   - (b) Sim×CA needs different generator support than we've given it (different placement constraints, different CA rule density, different win conditions).

   Recommend (a) for R16 (save the evolutionary budget), with (b) as a targeted future experiment if a specific mechanic is motivated.

### What's actually *good* about R15

- **The engineering changes verifiably worked at the micro level**: CA step-loop symmetry test passes, rule-table symmetry chain tests pass, double-pass draws verified.
- **The evaluation protocol is mature**: 22 independent teams, high inter-team agreement on every game (stdev 0.4-0.9).
- **The project's ability to find bugs via human eval is real and reproducible**: 3 new engine issues found in R15, all actionable, all replicable.
- **The inversion is honest signal**: GE no longer tracks human judgment and that's a calibration problem, not a regression of the run itself.

---

## Proposed Run 16 Configuration

```bash
# BEFORE running R16:
# 1. Fix _check_threshold and _check_connection iteration-order bias (engine_v2.py)
# 2. Fix CA step-ordering to compute both perspectives from shared snapshot (engine_v2.py)
# 3. Add torus+connection to generator quick_reject
# 4. Downgrade moore+capture to grid+capture in generator
# 5. Add greedy-vs-greedy seat-balance probe to trainer.evaluate()
# 6. Take worst-of-three for seat_balance metric in scoring.py

.venv/bin/python run.py \
  --generations 10 \
  --population 50 \
  --training-budget 10000 \
  --num-runs 2 \
  --immigration-rate 0.25 \
  --max-dimensions 2 \
  --ca-probability 0.2 \
  --simultaneous-probability 0.5 \
  --db-path genesis_v2_run16.db \
  --seed-db genesis_v2_run14.db \
  --seed-games deb4dfe0382d 531634cee158
```

Rationale for the knob tweaks:
- **ca-probability 0.3 → 0.2**: R15 showed CA doesn't add value beyond simultaneous alone. Reduce evolutionary budget on CA.
- **sim_ca_bias**: leave at default 0.4. If CA prob drops, co-occurrence still drops proportionally.
- **Seeds unchanged**: still start from R13+R14 human winners.

---

## Files

- **Database**: `genesis_v2_run15.db` (500 games, 341 scored)
- **Training log**: `run15_output.log`
- **Team evaluation reports**: `evaluations/run15/team-{1-21,pilot}_game{id}.md` (22 files)
- **Evaluation protocol**: `v2-evaluation-prompt-run15.txt`
- **Simultaneous-play helper**: `sim_play_helper.py` (introduced by pilot, surfaced `play_helper.py` missing sim support)

---

## Verdict

R15 confirmed something the project has been circling for three runs: **bug-finding is the main output, games are secondary**. The run produced no game near R8's 8/10 bar, and the GE champion scores at the bottom of human evaluation because the metric cannot see inside the engine where three bias sources were hiding.

The **sim×CA premise is dead**. With the R14 step-loop bug fixed and rule-table symmetry enforced, sim×CA games contribute no emergent value and should not be the organizing principle of future runs.

The **simultaneous-play premise is weaker than R14 suggested** but not dead. Simultaneous alone produced interesting games in R15 but they all trip on the `_check_threshold` iteration bias. The right R16 question is: with margin-based threshold resolution and CA step snapshot fix, can simultaneous games actually break through?

The **fitness metric needs another pass**. The R15 seat-balance metric correctly penalizes some bias but misses the class that requires skilled play to expose. A greedy-vs-greedy probe is the next iteration.

The **project's diagnostic discipline is the real asset**. Across R13, R14, R15, human evaluation has found: stability check perspective bug (R13), Manhattan distance (R13), CA step-loop (R14), CA rule-table asymmetry (R14), threshold iteration-order (R15), connection iteration-order (R15), CA step-order (R15), torus-wrap connection (R15 recurrence), Moore capture deadness (R15 recurrence). None of these would have been caught by the fitness metric alone. The 22-team evaluation protocol is the most reliable correctness tool in the project.
