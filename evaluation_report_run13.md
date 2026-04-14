# Run 13 Evaluation Report

**Database**: `genesis_v2_run13.db`
**Config**: 11 generations (0-10), pop 50, 10k training budget, 2 runs, 25% immigration, 2D only, 50% CA probability
**Seed games**: `567384041c59` (Run 12 best CA), `484fcb3b0471` (Run 10 hex champion)
**Duration**: ~34.8 hours
**Evaluation protocol**: Tiered agent-team evaluation with mandatory Novelty Adversary
- 1 pilot team (champion only)
- 7 teams on each of top 3 games (ranks 1-3)
- Total: 22 independent team evaluations

---

## Executive Summary

**Run 13 produced its first successful CA games**, but the champion did not deliver a breakthrough. The Go Essence metric ranked a CA game first (`06bab8a32425`, GE 0.521), but rigorous human evaluation placed a *classic* game in rank-3 position (`531634cee158`) as the strongest title in the run. All three tier-1 games scored in the 4-6/10 range for human play — none reached the 7-8/10 bar set by Run 8's champion.

The most valuable outcomes of Run 13 are **not the games themselves** but the insights:
- **CA games can now compete** (first time in the project): 9 of top-20 are CA games, vs 0 in Run 12
- **Engine bug discovered**: `topology.distance()` used Manhattan on all topologies — breaking influence propagation on hex/moore/torus for every run since V3
- **The Go Essence metric mis-ranked** the top 3 games relative to human evaluation
- **Specific CA rules matter more than CA in principle**: 136 of 147 transition entries were inert in the champion
- **P1 first-move advantage is endemic** across placement-only games with no pie/swap rule

---

## Final Leaderboard (Go Essence)

| Rank | Game ID | GE | ELO | Depth | Non-Triv | Complex | Type |
|------|---------|------|------|-------|----------|---------|------|
| 1 | `06bab8a32425` | 0.521 | 1115 | 0.796 | 0.938 | 17 | **CA** |
| 2 | `558e1f1be563` | 0.486 | 1003 | 0.658 | 0.959 | 16 | Classic |
| 3 | `531634cee158` | 0.482 | **2972** | 0.757 | 0.825 | 15 | Classic |
| 4 | `8a5c2fa6b962` | 0.448 | 953 | 0.784 | 0.693 | — | Classic |
| 5 | `86c5fa02b866` | 0.427 | 953 | 0.693 | 0.693 | — | **CA** |
| 6 | `8d867ff722e3` | 0.423 | 1007 | 0.495 | 1.000 | — | Classic |
| 7 | `d28875734e5f` | 0.419 | 2982 | 0.491 | 1.000 | — | Classic |
| 8 | `fb24cb748f78` | 0.416 | 954 | 0.651 | 0.748 | — | **CA** |
| 9 | `016af6839f95` | 0.415 | 952 | 0.613 | 0.800 | — | **CA** |
| 10 | `1e994e4334e0` | 0.404 | 2945 | 0.658 | 0.693 | — | Classic |

**CA games in top 10**: 4/10 (vs 0/10 in Run 12)
**CA games in top 20**: 9/20
**Highest-ELO game**: rank-3 `531634cee158` at 2972 — suggests this is the most consistently winning game against the arena

---

## Human Evaluation Results — Top 3 Games

### Methodology

Each tier-1 game received 7 independent team evaluations (1 pilot + 6 production teams on the champion; 7 teams each on ranks 2-3). Every evaluation ran all 5 phases including:
- **Phase 1**: Rule comprehension with degeneracy-check
- **Phase 2**: 3 engine-verified playthroughs with seat-swap on game 3
- **Phase 3**: Joint strategic analysis
- **Phase 4**: Mandatory Novelty Adversary (compare vs Hex, Y, Havannah, Chameleon, Life-like CAs, etc.)
- **Phase 5**: Structured verdict with 6 numeric scores

### Aggregate Scores

| Metric | Rank 1 (CA champ) | Rank 2 (influence) | Rank 3 (outnumber) |
|--------|-------------------|--------------------|--------------------|
| **Overall** | **5.0** | **4.3** | **5.9** |
| Strategic Depth | 5.3 | 5.0 | 6.1 |
| Balance | 5.0 | 5.1 | **6.9** |
| Novelty (post-adversary) | 4.7 | 4.3 | 5.0 |
| Emergent Complexity | 5.1 | 4.3 | 6.0 |
| Replayability | 4.7 | 4.0 | 5.7 |
| **Inter-team stdev (Overall)** | 1.8 | 1.3 | 0.5 |

**Key finding**: Rank-3 scored highest on every axis, with the tightest inter-team agreement (stdev 0.5). The Go Essence metric put it last of the three tier-1 games — a clear ranking inversion.

---

## Game 1: `06bab8a32425` — "CA-Hex" (rank 1 by GE)

**Format**: 2D 8×8 hex, CA (2 steps/turn), adjacent_to_own placement with overwrite, connection win (Hex-style two-face targets), super-ko active, no explicit capture.

**Team-by-team overall scores**: 5, 3, 3, 7, 7, 3, 6, 6 (mean 5.0, stdev 1.8)

**Consensus findings**:
- Not a re-skin of any single known game
- Novelty lives in *dynamics* (overwrite + super-ko + CA interaction), not *structure*
- 136 of 147 CA transition entries are inert (identity). Only 2-4 rules fire in typical play
- The `1,1,4 → 2` flip rule is genuinely novel (creates density-tax on aggressive play) but rarely fires
- The `0,4,0 → 1` birth rule creates a "compactness premium" for wall-building

**Disagreement** (largest inter-team variance of any game): half the teams saw uniform P1 wins (3/3 games) and scored the balance failure as fatal (3/10). The other half saw split outcomes (1-2 P2 wins) and rated the overwrite+CA interactions as sufficiently rich (6-7/10).

**Closest analog**: Hex — identical topology and connection goal. Secondary: Immigration Game (2-color Life) grafted onto Hex.

**Killer flaws**:
1. No pie/swap rule → P1 first-move advantage
2. CA mostly dormant — strategic weight carried by 2 rules, not 7
3. Silent ko-as-pass can trap a player without them knowing

**Best quality**: Density-aware walls via overwrite + CA survivability (multiple teams). The `F/1F+4X → X` flip rule (pilot + team 6).

---

## Game 2: `558e1f1be563` — "Hex Influence Threshold" (rank 2 by GE)

**Format**: 2D 8×8 hex, adjacent_to_any placement, no capture, radius-1 signed influence (±1.42, decay 0.456), threshold win at ≈39.66.

**Team-by-team overall scores**: 5.2, 3, 4, 5, 3, 4, 5 (mean 4.3, stdev 1.0)

**Consensus findings**:
- Closest analog: **Tumbleweed** (Zapawa 2021) — hex influence-majority territory game — and "No-Capture Go on hex"
- Engine bug discovered by Team 6: `topology.distance()` uses raw Manhattan regardless of topology, so on hex, the two "hex diagonals" are adjacent cells but receive zero influence exchange. Inverts Go's "edge stones are weak" rule — boundary cells become optimal
- P1 tempo advantage without komi; greedy 1-ply is near-optimal
- Team 7 found a **non-transitive strategy matrix** — density > density-mirror, anti > density, anti-vs-anti stalls — rare real emergent property

**Killer flaws**:
1. Greedy local hill-climb defeats any long-term plan (placements are permanent)
2. Threshold barely reachable under contested play → many games end in draws or piece-count tiebreaks
3. P1 structural first-mover advantage in density play

**Best quality**: The poison/reinforcement swing mechanic — "every enemy stone adjacent to your cluster subtracts 0.65 from your own-cell value" makes every placement dual-purpose (team-1, team-4).

---

## Game 3: `531634cee158` — "Hex Outnumber Territory" (rank 3 by GE; human winner)

**Format**: 2D 8×8 offset-hex, adjacent_to_own placement, outnumber-3 capture, territory win at ~54.75% (unreachable in practice, games resolve via double-pass majority).

**Team-by-team overall scores**: 6, 6, 6, 6, 6.2, 5, 6 (mean 5.9, stdev 0.5)

**Consensus findings** (remarkably high inter-team agreement):
- Well-balanced: self-play 50/50, random-play 3-2 to P2 across 5 seeds, no seat bias
- Average game length 65-80 moves — meaningful depth
- Three viable macro-strategies: blob-builder, snake/flank, capture-hunter
- **Triangle-kill motif** — 3 friendly stones around an enemy captures. Not present in Go (liberty-based), Hex (no capture), Othello (line-based) — genuinely emergent from outnumber-3 on hex-6
- **Wedge tesuji** (team 4) — diagonal-seam placement triggers multi-capture; real learnable tactical motif
- **Walking-dead fragile stones** (team 3) — 3 enemy neighbors, one-move-from-death; inverts Go invasion logic

**Closest analog**: Atari Go on hex with majority capture — not a published game. Secondary: Slither (Mark Steere, but different action space).

**Killer flaws** (none absolute):
1. Territory threshold 0.5475 is dead — games resolve by double-pass majority, not capture race
2. Isolated stones are immortal under outnumber-3 — inverts Go invasion logic but feels degenerate
3. Propagation fields inert but still stored (rule complexity inflation)
4. No ko rule explicitly (super-ko handles it but lazily)

**Best quality**: Feedback loop between connective wall-building and triangle-shape captures (team 7). The adjacent_to_own growth constraint forces Go-like shape reading (team 1, team 5).

---

## Cross-Cutting Discoveries

### 1. Engine Bug: `topology.distance()` Manhattan-only

**Reporter**: Team 6 (rank-2 evaluation)
**Severity**: High — affects all influence-propagation games across every run since V3

**Details**: `topology.distance()` at `topology.py:261-265` computed Manhattan distance on raw coordinates regardless of `topology_type`. For hex, the two "hex diagonals" at a cell are hex-adjacent (distance 1 in graph) but Manhattan-2 in raw coords, so influence propagation (which uses `cells_within_radius`) did not reach them. Same issue on moore (diagonals are Chebyshev-1, Manhattan-2) and torus (wrap-around not considered).

**Impact**: Possibly every influence-based game in Runs 7-13 was subtly broken on non-grid topologies. Games that evolved despite the bug likely selected for strategies that worked *around* the truncated influence kernel. Fixing this may produce qualitatively different games from Run 14 onward.

**Status**: Fixed in this commit. Hex uses axial distance; Moore uses Chebyshev; Torus uses wrapped Manhattan.

### 2. Double-Pass Majority Exploit

**Reported by**: Teams 2, 3 on rank-1; team 2 on rank-3
**Severity**: Medium — affects most games ending in double-pass

**Details**: When both players pass consecutively, the engine ends the game via majority-piece tiebreaker. This enables an exploit: a leading player can pass on turn N, then if the opponent also passes, the game ends in their favor without requiring them to reach the actual win condition.

**Impact**: Several games in Run 13 (including rank-3) resolve ≥90% of games by double-pass majority, never reaching their stated win condition. This inflates the perceived success of the win-condition design.

**Fix direction**: Require win condition to trigger the game end (not double-pass), or treat double-pass as a draw rather than a majority win.

### 3. Ranking Metric vs Human Judgment Divergence

The Go Essence metric and human evaluation disagreed on all three tier-1 games:

| Rank by GE | Game | GE | Human Mean | Human Rank |
|-----------|------|-----|-----------|-----------|
| 1 | `06bab8a32425` | 0.521 | 5.0 | 2 |
| 2 | `558e1f1be563` | 0.486 | 4.3 | 3 |
| 3 | `531634cee158` | 0.482 | **5.9** | **1** |

Strategic depth metric (auto) vs human depth rating:

| Game | Auto depth | Human depth |
|------|-----------|-------------|
| rank 1 | 0.796 | 5.3/10 |
| rank 2 | 0.658 | 5.0/10 |
| rank 3 | 0.757 | 6.1/10 |

The correlation holds roughly but the automated metric systematically *over-values* the CA champion (auto 0.796 vs human 5.3) and *under-values* the balance quality of rank-3. This suggests adding a balance-quality signal to Go Essence may help future runs.

### 4. Novelty Adversary Phase Was High-Signal

Without the mandatory Novelty Adversary, novelty scores would likely have been inflated by 1-3 points across all games. In the pilot, the adversary phase explicitly *reduced* the novelty score from an intuitive "seems new" reading to a rigorous 6/10 based on a specific coordinate-transformation attempt. Team 7 on rank-1 noted the same: the adversary's catalog comparison forced a genuine defense, not a hand-wave.

**Recommendation**: Keep the Novelty Adversary phase for Run 14+ evaluation.

---

## Failure Modes Observed

| Failure | Games affected | Count |
|---------|----------------|-------|
| P1 first-move advantage without pie rule | All 3 tier-1 games | 3/3 |
| CA rules mostly inert in typical play | Rank 1 | 1/3 |
| Double-pass majority ends game without win condition | Ranks 1, 3 | 2/3 |
| Greedy 1-ply is near-optimal (no long-horizon tension) | Rank 2 | 1/3 |
| Isolated stones are immortal (degenerate "atari" reasoning) | Rank 3 | 1/3 |

---

## Recommendations for Run 14

### Code-level changes (done or planned)

1. ✅ **Fix `topology.distance()`** — now topology-aware (axial/Chebyshev/wrapped)
2. ✅ **Add simultaneous turn type** — directly addresses the P1 first-move advantage
3. ⏳ **Fix double-pass majority** — change to draw, or require win condition to fire
4. ⏳ **Dense CA rule requirement** — during generation, require at least N live rules that fire in stability check
5. ⏳ **Prop-field complexity penalty** — don't store inert propagation params on CA games (already set to "none" but fields persist)

### Generator changes

6. **Tighten CA live-rule count** — reject CA rules where <3 rules fire in the stability check
7. **Simultaneous at 30-50%** — force exploration of the new axis
8. **Keep CA at 30%** — enough to compete, not enough to dominate

### Evolutionary changes

9. **Seed with rank-3 `531634cee158`** — strongest human-validated game in Run 13
10. **Seed with `06bab8a32425`** — best CA game for gene-pool CA diversity
11. **Consider also `8a5c2fa6b962`** (rank 4, moore/connection, GE 0.448) — best moore-topology classic game for topological diversity

### Metric/scoring changes

12. **Add balance sub-metric** to Go Essence — currently `non_triviality` includes balance, but a weighted balance term might prevent the CA champion (non_triv 0.938 but actual balance 5/10) from over-ranking
13. **Penalize double-pass endings** in fitness when both players had legal non-pass moves

---

## Run 14 Proposed Configuration

```bash
.venv/bin/python run.py \
  --generations 10 \
  --population 50 \
  --training-budget 10000 \
  --num-runs 2 \
  --immigration-rate 0.25 \
  --max-dimensions 2 \
  --ca-probability 0.3 \
  --simultaneous-probability 0.5 \
  --db-path genesis_v2_run14.db \
  --seed-db genesis_v2_run13.db \
  --seed-games 531634cee158 06bab8a32425
```

**Rationale**:
- `--simultaneous-probability 0.5`: force heavy exploration of the new axis; P1 advantage should disappear for these games
- `--ca-probability 0.3`: keep CA available but step back from 50% so simultaneous can shine
- 2D-only: confirmed optimal across Runs 11-13
- Seed with the human winner (`531634cee158`) plus the CA champion for lineage diversity

---

## Files

- **Database**: `genesis_v2_run13.db` (500 games, 380 scored)
- **Training log**: `run13_output.log` (complete)
- **Team evaluation reports**: `evaluations/run13/team-{1-7,pilot}_game{06bab8a32425,558e1f1be563,531634cee158}.md` (22 files)
- **Evaluation protocol**: `v2-evaluation-prompt-run13.txt` (includes mandatory Novelty Adversary phase)

---

## Verdict

Run 13 demonstrated that **tuning CA generation works** — CA games compete for the first time since CA was introduced — but did not produce a standout game. The most strategically satisfying game (`531634cee158`) is a classical-mechanics hex variant that emerged *despite* the CA focus.

The run's lasting value is in the **infrastructure and insight**:
- The Manhattan distance bug discovery retroactively explains weaknesses in Runs 7-12 influence-based games
- The inversion between GE ranking and human ranking is the clearest evidence yet that the fitness function needs a balance-quality term
- The novelty adversary protocol produces more honest scores than unadversarial evaluation

The key unexplored frontier — **simultaneous play** — was identified during this evaluation and has been built into the engine. Run 14 will be the first project run with a mechanic that structurally eliminates the P1 first-move advantage that has plagued every game through Run 13.
