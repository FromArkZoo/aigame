# Team-18 Evaluation — Game `4d9c5796dd18`

- **Run:** R16, Generation 10, parent `fd78496038d2`, GE rank 5.
- **DB:** `genesis_v2_run16.db`
- **Engine:** `play_helper.py` (alternating) + custom helper `_team18_play.py` for board-value inspection.

---

## PHASE 1 — Rule Comprehension

**Board:** 2D 8×8 (64 cells). Topology = `moore` (8 face+diagonal neighbours per interior cell, 5 on edges, 3 in corners). Note: `play_helper.py rules` mislabels this as "von Neumann" — verified against `topology.py::_build_moore_neighbors`.

**Turn structure:** **Alternating**, 1 piece per turn. Action 64 = pass; two consecutive passes end as draw. P1 moves first.

**Action types:** `place` only (no movement). Placement target = empty cell, anywhere; first move anywhere.

**Capture (surround):** Go-style — after each placement, any enemy group with zero adjacent-empty liberties (using moore adjacency, so 8-direction) is removed. With moore + 8-neighbour adjacency, capture is *very* hard in the interior (need all 8 cells filled) but possible in corners (3 neighbours) and edges (5 neighbours). I verified empirically that an interior single stone CAN be surrounded with 8 enemy moves, but in normal play the threshold-win triggers first.

**Propagation (influence):** Radius 2 (moore distance), strength 1.6836, decay 0.7205. Each placed P1 stone adds `strength * decay^d` to all cells within radius (positive); each P2 stone subtracts. Self-cell (d=0) gets +1.684, d=1 gets +1.213, d=2 gets +0.875.

**Win condition:** First player whose **own-cell value sum** crosses **50.508** wins. R16's `_check_threshold` uses margin tie-break for same-tick crossings (not P1-iteration-bias). Max turns = 100; on max-turns it's piece-majority; on double-pass it's a draw.

**Generator note:** R16 explicitly *downgrades* moore→grid when surround-capture is present (per the prompt) because moore makes interior groups un-gappable. This game ID still has `topology=moore + capture=surround`, suggesting it was either grandfathered (parent generation 9, before that filter, per metadata) or the filter only applies for new mutations. Either way the surround rule is inert for interior play.

**Degeneracy flags:**
- **Surround capture is mostly inert.** Threshold (50.5) is reached around stone 6–8 placed by either player; corner/edge captures are theoretically possible but I never saw one matter in 3 played games and 5 greedy-vs-greedy probes (max ply ≈ 19, no captures).
- **First-move tempo dominates.** A 1-stone tempo gap consistently translates into P1 crossing the threshold first. Every greedy-vs-greedy game in my 5-trial probe ended with P1 winning at move 19.
- **No double-pass risk:** threshold is reachable in ~7 moves of unopposed play; even contested games converge in 13–19 moves.

---

## PHASE 2 — Strategic Play

Each move was engine-verified through `play_helper.py` or my helper `_team18_play.py`. Reasoning kept role-separated.

### Game 1 — P1 vs P2, both pursuing a "build cluster" strategy

| # | Player | Move | Cell | Sums after move (P1 / P2) |
|---|--------|------|------|---------------------------|
| 1 | P1 | 27 | (3,3) | 1.68 / 0.00 |
| 2 | P2 | 36 | (4,4) — adjacent to disrupt | 0.47 / 0.47 |
| 3 | P1 | 18 | (2,2) — pivot to safe corner cluster | 3.71 / -0.40 (P2 dragged negative!) |
| 4 | P2 | 45 | (5,5) — mirror | 2.83 / 2.83 |
| 5 | P1 | 9  | (1,1) | 8.69 / 2.83 |
| 6 | P2 | 54 | (6,6) — mirror | 8.69 / 8.69 |
| 7 | P1 | 17 | (1,2) | 16.97 / 8.69 |
| 8 | P2 | 46 | (6,5) — mirror | 16.97 / 16.97 |
| 9 | P1 | 10 | (2,1) | 27.68 / 16.97 |
| 10 | P2 | 53 | (5,6) — mirror | 27.68 / 27.68 |
| 11 | P1 | 19 | (3,2) — central reinforcer | 39.27 / 26.81 |
| 12 | P2 | 44 | (4,5) — mirror | 38.39 / 38.39 |
| 13 | P1 | 26 | (2,3) — *winning move* | **51.53 / 36.65 → P1 wins** |

**Winner: P1, threshold-cross on turn 13.**

### Game 2 — P2 switches to aggressive disruption strategy

P2 plays adjacent to P1 every move to suppress, instead of mirroring.

| # | Player | Move | Cell | Sums (P1 / P2) |
|---|--------|------|------|----------------|
| 1 | P1 | 27 | (3,3) | 1.68 / 0.00 |
| 2 | P2 | 28 | (4,3) — adjacent disrupt | 0.47 / 0.47 |
| 3 | P1 | 9 | (1,1) — flee | 3.90 / 0.47 |
| 4 | P2 | 36 | (4,4) — reinforce + still suppress (3,3) | 2.69 / 3.37 |
| 5 | P1 | 18 | (2,2) | 7.48 / 1.62 |
| 6 | P2 | 37 | (5,4) — extend cluster, suppress (3,3) | 6.60 / 7.28 |
| 7 | P1 | 10 | (2,1) | 14.01 / 6.41 |
| 8 | P2 | 44 | (4,5) | 13.14 / 13.82 (P2 ahead!) |
| 9 | P1 | 19 | (3,2) — front-line triple-reinforcer | 20.89 / 10.86 |
| 10 | P2 | 29 | (5,3) — symmetric triple | 19.14 / 19.82 (P2 ahead again) |
| 11 | P1 | 26 | (2,3) — front-line triple | 28.98 / 17.20 |
| 12 | P2 | 45 | (5,5) — triple | 28.10 / 28.78 (P2 ahead) |
| 13 | P1 | 17 | (1,2) — quadruple | 42.99 / 28.78 |
| 14 | P2 | 52 | (4,6) — best-available | 42.99 / 38.81 |
| 15 | P1 | 11 | (3,1) — *winning move (gains +14.2 by claiming a heavily-radiated empty cell)* | **57.19 / 37.06 → P1 wins** |

**Winner: P1, threshold-cross on turn 15.** P2's aggressive disrupt strategy actually pulled them ahead at three different mid-game checkpoints (M8, M10, M12), but P1's structural one-tempo lead converted at the end, when both players' clusters had radiated enough that high-value empty cells exist for the leader to claim.

### Game 3 — Seat swap (mirror opening)

P1 plays (4,4), P2 plays (3,3) (the disrupt-style opener swapped). Both pursue mirror cluster strategies in opposite quadrants.

Result: **P1 wins on move 13 (52.60 / 38.39)** — same outcome as Game 1's mirror line. Seat swap had **no effect**: whoever moves first wins under symmetric play.

### Quantitative seat-balance probe

Greedy-vs-greedy (per-move maximizer of `own − opponent`) ran 5 trials:
- **P1 wins 5/5**, all in 19 moves with 10 P1 stones to 9 P2 stones.

Skill check (random vs greedy):
- Random P1 vs Greedy P2 → P2 wins 10/10.
- Greedy P1 vs Random P2 → P1 wins 10/10.

So skill matters (greedy crushes random in either seat), but at equal skill the first-mover wins 100%.

### Player reflections

**P1 strategy guide:** Place centrally on move 1 (3,3) or (4,4). On move 3, pivot diagonally away from P2's adjacent disrupt — start your real cluster in a quadrant where P2 has minimal reach. From there, fill the cluster with cells that are dist-1 to maximally many of your existing stones (front-line "triple/quadruple reinforcers"). The winning move is usually a placement that *claims* an empty cell already heavily radiated by your stones — a single such claim can add 10+ to your sum.

**P2 strategy guide:** Adjacent disrupt is *better* than mirror (it kept me even at three midgame checkpoints in Game 2 vs always-behind in Game 1's mirror), but it does not overcome the structural one-tempo gap. There is no winning P2 strategy I found; the best you can do is force the game to last until move 15 instead of 13. In live play I recommend disrupting AND staying tight enough that your own cluster is also high-value — anything looser and you lose by 13.

### Surprises

- The *adjacent disrupt* tactic is asymmetric: it hurts both players, but P2 (placing second on a smaller cluster) gets relatively more cluster-suppression bang for the buck. This is interesting but not enough to overcome tempo.
- The "claim an existing high-influence empty cell" winning-move pattern (Game 2 move 15: claiming (3,1) added +14.2 in one shot) is more tactical than I expected. It rewards reading the value field, not just stone counts.

All three games ended via threshold cross. None reached max_turns or double-pass.

---

## PHASE 3 — Strategic Analysis (joint)

**Acknowledging seat-identity bias:** all three games and probes were run by one agent playing both sides; my P1 and P2 reasoning are not independent. I tried to mitigate by writing each move's reasoning before peeking at the result and by varying P2 strategy between games.

**Distinct viable strategies:** Two clearly distinct approaches exist:
1. **Mirror cluster build** — opposite-quadrant tight cluster. Loses cleanly to the first-mover.
2. **Adjacent disrupt** — place next to opponent's stones to suppress. Closes the gap mid-game but doesn't win.

There is real strategic texture in *which* cluster cell to claim each turn (front-line reinforcer vs corner extender vs disrupt). The value field changes with every move, so each turn has a non-trivial best move.

**Counter-play:** The disrupt strategy is genuine counter-play to clustering — Game 2 vs Game 1 shows ~3-point swing in P2's favour when P2 disrupts. But it doesn't flip the result, only the margin.

**Short vs long-term tension:** Mild. There's tension between tight-clustering (high own-value but easy to suppress at the front) vs fan-out (each new stone adds less to existing cells but is harder for opponent to suppress). Real but not deep.

**Emergent concepts:** *Influence* and *territory* are the dominant concepts (literally: the engine has `propagation_rule.prop_type = "influence"`). *Tempo* is overwhelming. *Initiative* is conserved (P1 never relinquishes it). No ko, no mutual annihilation, no genuine sacrifice tactics — capture rule is dormant.

**Topology effects:** Moore distance changes the propagation footprint to a square (5×5 within radius-2) instead of a Manhattan diamond. This makes diagonal cluster patterns more efficient than orthogonal ones — Game 1's diagonal line (1,1)-(2,2)-(3,3) is the optimal seed because each pair is moore-distance 1. The choice of moore over grid materially changes the game.

**First-mover advantage (quantified):** In 5 greedy-vs-greedy trials and 3 hand-played games (one with seat-swap-equivalent mirror), **P1 won 8/8**. The R16 greedy-vs-greedy seat-balance probe should be flagging this. From the training-run records in the database, two of four runs hit final win-rate 1.000 for P0 (trained vs trained), which is consistent with P1-favoured asymmetry.

---

## PHASE 4 — Novelty Adversary (mandatory)

**Adversary opens:** This is just **Reversi/Othello with continuous influence numerics**. Both involve placing stones on an 8×8 board with each placement affecting nearby cells. The win condition is "highest score on your own colour." A Reversi expert would recognise the threshold-race + cluster-building skeleton in 30 seconds.

**Adversary continues:** It's also simply **Tumbleweed-on-a-square-board**. Tumbleweed has graded-influence territory ("how much line-of-sight do my stacks throw") with a stake-claim mechanic. Replace LoS with radius-2 decaying influence and you have this game. Or even more basic: **Go with weighted scoring** — propagation is just an oracle for "how much area do my stones control." Strip the propagation and you have a stripped-down Go where territory accrues by scalar contribution rather than by enclosure.

**Adversary's "is it just X" test:** "X = Reversi with smoothed scoring." A Reversi player would transfer immediately because (a) flips don't exist here so it's actually *easier* than Reversi, (b) the cluster-building heuristic is identical, (c) the threshold-vs-final-count distinction is small.

### Player rebuttals (tied to Phase 2 moments)

**P1's rebuttal:** Reversi has *flipping* — the entire strategic core is "force a flank." This game has *no flips at all* (capture is moore-surround, which never fires). The actual strategic primitive is *radius-2 numeric superposition*, which Reversi does not have. In Game 2 move 15, the winning move worked because (3,1) had accumulated +5.39 of *empty-cell* value from existing P1 stones — claiming an empty high-influence cell adds that pre-existing radiation to your score. No Reversi move resembles this; in Reversi, an empty cell has no score.

**P2's rebuttal:** Tumbleweed is closer than Reversi but still wrong. Tumbleweed uses *line-of-sight* (axis-aligned rays through a hex) and *stack heights* with *one-shot stake claims*. This game uses *euclidean-style decaying influence* (continuous floats) and *unbounded multi-stone reinforcement* — two stones don't replace one; each independently adds. The Game 2 mid-game pattern where P2 was *ahead at moves 8/10/12 but still lost* would not happen in Tumbleweed (Tumbleweed lead translates to win); it happened here because the sums update non-linearly with each stone's reach into newly-claimed empty cells. That's a distinctive numerical-field dynamic.

**Vs Go with weighted scoring:** Go has chains and liberties that *matter*. Here capture is dormant (verified: 0 captures across all 3 hand-played games and 5 greedy probes). What's left is just radial propagation arithmetic — which is *thinner* than Go, not a re-skin of it.

**Closest known analog:** The closest fit I can find is the *Tumbleweed/Go-territory hybrid* family, but the radius-2 numeric decay with continuous floats and threshold-race ending puts it just outside any one of them. No expert would transfer immediately; they'd need a few games to internalise that capture is dead and the game is purely an influence-arithmetic race.

**Novelty score: 4/10.** It's not "X on a hex board" (would be 2-3) but it's also not emergent dynamics with no analog (would be 7+). It's a recognisable territory-influence game with one numerical twist (continuous radial decay + scalar threshold) sitting on top of dormant Go-capture rules.

---

## PHASE 5 — Verdict

```
Team ID: team-18
Game ID: 4d9c5796dd18
Rules Summary: 8×8 moore-topology placement game; each stone radiates radius-2 decaying
  influence (±1.684 with decay 0.72); first player whose own-cell value sum exceeds 50.508
  wins. Surround-capture rule present but practically dormant on moore adjacency.
Topology: 8×8 moore (8 neighbours interior)
Turn Structure: alternating, 1 piece/turn
```

### SCORES (1-10)

- **Strategic Depth: 4** — Real choices each turn (which dist-1 reinforcer to play, when to disrupt vs build, when to claim a high-radiation empty cell), but the strategy collapses to a tempo race with one main dimension. No deep tactical patterns (no ko, no sacrifice, no genuine zugzwang). The Game 2 winning-move pattern (claim a high-value empty cell) is the only truly tactical idea I found.

- **Emergent Complexity: 3** — Influence and tempo emerge cleanly. Territory emerges weakly (clusters are de-facto territory). Capture, despite being in the rules, is non-emergent — it never fires. CA rules N/A. No surprise dynamics from the moore + radius-2 + decay combination beyond "diagonal lines are efficient."

- **Balance: 2** — **Severe first-mover imbalance.** Greedy-vs-greedy: P1 wins 5/5. Hand-played mirror line: P1 wins move 13. Hand-played disrupt line: P2 leads at three midgame points but loses move 15. Seat-swap had zero effect. The R16 worst-of-three seat-balance probe should be catching this; if it is not, this is a calibration miss.

- **Novelty (post-adversary): 4** — Recognisable territory-influence family with one numerical twist (continuous radial decay + scalar threshold). Not a direct re-skin, but a Reversi/Tumbleweed/Go-territory player would orient quickly.

- **Replayability: 3** — Once you internalise "play (3,3), then (1,1)/(2,2)-style diagonal cluster, claim front-line triples, finish by claiming a high-radiation empty cell," there's not much to discover. Some variation in which-quadrant-to-build, but the essential plan is fixed.

- **Overall "Would I play this again?": 3** — One or two games to feel the influence numerics is interesting; after that the seat imbalance kills replay value.

### CLOSEST KNOWN-GAME ANALOG
**Tumbleweed × Reversi-territory hybrid.** Tumbleweed contributes the graded-influence territorial-claim mechanic; Reversi contributes the place-only-on-an-8×8 threshold-scoring shell. Not identical: this game uses radial euclidean-ish decay (vs Tumbleweed's LoS), has no flipping (vs Reversi's flank-flips), and has a scalar threshold ending (vs both games' final-count). It's a recognisable cousin, not a re-skin.

### KILLER FLAWS
1. **Severe P1 tempo advantage at greedy and trained skill levels** (8/8 in my probes; 2/4 training runs hit P0=1.000). The threshold-race structure mathematically guarantees that whoever moves first crosses the threshold one move earlier under symmetric play.
2. **Surround-capture rule is dormant** because moore adjacency makes interior groups un-gappable before the threshold fires. The rule contributes nothing strategically. R16's own generator policy says "downgrade moore→grid when surround capture is present" — this game appears to predate that filter (parent generation 9, listed in metadata).
3. **Mirror strategy is fully cancellable** — Game 1 and Game 3 both showed perfect symmetric value sums tick-by-tick, with the only difference being P1 closes first. There's no reward for playing well in mirror; only for breaking mirror, and breaking it costs P2.

### BEST QUALITY
The continuous-influence value field is genuinely engaging to read. Game 2's move-15 winning play (claiming an empty cell that had silently accumulated +5.39 of P1 radiation, gaining +14.2 in one move) is the kind of pattern recognition you don't get in pure-stone games. If the seat imbalance were fixed, this could be a real "chess-like reading" surface.

### IMPROVEMENT IDEAS
**Either** (a) require P2 to place 2 stones on their first turn (chess-style "second-move compensation"), **or** (b) make the threshold asymmetric (P1 needs 55, P2 needs 50) tuned to undo the one-tempo advantage. The cleanest fix is (a) — pie-rule-equivalent compensation. Empirically a 1-stone P2 first-turn handicap would offset the ~10-point gap I observed at threshold-cross.

A secondary improvement: drop the surround-capture rule entirely (it's inert here) **or** switch the topology to grid (4-neighbour) so capture becomes meaningful — but grid would shrink the radius-2 propagation footprint to a Manhattan diamond, weakening the influence dynamics. The pie-rule compensation is the cleaner fix.
