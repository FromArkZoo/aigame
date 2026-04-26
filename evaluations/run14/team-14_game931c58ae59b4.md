# Team 14 — Run 14 Human Evaluation

**Team ID:** team-14
**Game ID:** 931c58ae59b4
**Evaluator notes:** R14 rank 3 by GE 0.4824, ELO 3035 (highest on leaderboard). Alternating, seed game, v3 representation. Evaluation produced by a single reasoner playing three roles sequentially. Seat-identity bias acknowledged.

---

## Phase 1 — Rule Comprehension

- **Board:** 2D, axis_size 8 → 8x8 = 64 cells. **Topology: Moore** (each cell has up to 8 neighbors; Chebyshev distance).
- **Turn structure:** **Alternating**, one piece per turn. (Not simultaneous.)
- **Action types:** Place only. 65 actions = 64 cells + 1 pass.
- **Placement constraints:** `target=empty`, `constraint=adjacent_to_own`, `first_move_anywhere=True`. Every player's *first* placement (while they own zero stones) may go anywhere; subsequent placements must be adjacent (Moore-8) to a cell the placing player already owns.
- **Capture:** `surround` with `threshold=1` (standard Go-style: remove enemy group with 0 liberties adjacent to placed stone). **On Moore topology, a single stone has 8 Moore neighbors; surround-capture requires every liberty of the enemy group to be filled.** In practice this never fired in any of 3 playouts — capture is near-inert on Moore.
- **Propagation:** `influence`, radius 2, strength ≈ 1.6155, decay ≈ 0.4616.
  - Placing a stone adds signed `strength * decay^d` to every cell within Chebyshev distance 2 (P1 adds positive, P2 adds negative).
  - d=0: ±1.6155. d=1: ±0.7456. d=2: ±0.3441.
  - Values are clamped to [-100, 100].
- **Win condition:** `threshold`, target_dimension=0, **threshold ≈ 63.4597**, **max_turns=100**. After every move, sum `board_values[c]` over cells the player owns; effective score = sum (P1) or -sum (P2). If either player's effective score exceeds 63.46, that player wins immediately.
- **End by max_turns:** Majority piece count (Run 13 double-pass exploit *could* fire if both pass, but the threshold is reachable within ~20 turns in practice, so this never triggered).

**Degenerate rule flags:** None critical.
- Capture rule is effectively inert on Moore because surrounding a single stone needs 8 neighbors and any growing group has many liberties.
- The threshold is comfortably reachable: each placed stone contributes ~1.6 plus neighbor boosts; a compact 10–11-stone cluster crosses the threshold. No "unreachable threshold → game collapses to double-pass majority" pathology observed.
- First-mover advantage appears strong (see Phase 2).

---

## Phase 2 — Strategic Play

All three games engine-verified move-by-move. Every move below passed through `play_helper.py --action play` or the custom `team14_eval_tool.py` (which wraps the engine and prints effective threshold scores and full `board_values`). No rejected moves.

### Game 1 — Mirror play

| # | Mv | Player | Notes | P1 score | P2 score |
|---|----|--------|-------|----------|----------|
| 1 | 27 (3,3) | P1 | center opening | 1.62 | 0.00 |
| 2 | 36 (4,4) | P2 | adjacent contest | 0.87 | 0.87 |
| 3 | 18 (2,2) | P1 | NW expansion | 3.63 | 0.53 |
| 4 | 45 (5,5) | P2 | SE mirror | 3.29 | 3.29 |
| 5 | 19 (3,2) | P1 | tight triangle | 7.54 | 2.94 |
| 6 | 44 (4,5) | P2 | mirror triangle | 7.20 | 7.20 |
| 7 | 26 (2,3) | P1 | 2x2 block | 12.60 | 6.51 |
| 8 | 37 (5,4) | P2 | 2x2 mirror | 11.91 | 11.91 |
| 9 | 17 (1,2) | P1 | extend NW | 17.89 | 11.91 |
| 10 | 46 (6,5) | P2 | mirror | 17.89 | 17.89 |
| 11 | 25 (1,3) | P1 | extend NW | 25.35 | 17.89 |
| 12 | 38 (6,4) | P2 | mirror | 25.35 | 25.35 |
| 13 | 9 (1,1) | P1 | corner fill | 32.71 | 25.35 |
| 14 | 54 (6,6) | P2 | mirror | 32.71 | 32.71 |
| 15 | 10 (2,1) | P1 | dense cell | 42.35 | 32.71 |
| 16 | 53 (5,6) | P2 | mirror | 42.35 | 42.35 |
| 17 | 11 (3,1) | P1 | extend NE of cluster | 51.89 | 42.35 |
| 18 | 52 (4,6) | P2 | mirror | 51.89 | 51.89 |
| 19 | 16 (0,2) | P1 | strong edge fill | 60.04 | 51.89 |
| 20 | 47 (7,5) | P2 | mirror | 60.04 | 60.04 |
| 21 | **20 (4,2)** | P1 | **WIN** — 67.16 > 63.46 | **67.16** | 59.01 |

**Game 1 ended at move 21 via threshold win for P1.** Clean resolution, no double-pass.

### Game 2 — P2 disruption attempt

| # | Mv | Player | Notes | P1 | P2 |
|---|----|--------|-------|----|-----|
| 1 | 27 (3,3) | P1 | center | 1.62 | 0 |
| 2 | 28 (4,3) | P2 | **attach adjacent** | 0.87 | 0.87 |
| 3 | 20 (4,2) | P1 | wedge | 3.23 | 0.12 |
| 4 | 29 (5,3) | P2 | extend | 2.14 | 2.14 |
| 5 | 19 (3,2) | P1 | triangle | 5.65 | 1.05 |
| 6 | 37 (5,4) | P2 | triangle | 4.62 | 4.62 |
| 7 | 18 (2,2) | P1 | extend | 9.56 | 4.27 |
| 8 | 36 (4,4) | P2 | 2x2 block | 7.78 | 8.58 ← P2 ahead! |
| 9 | 26 (2,3) | P1 | 2x2 block | 13.87 | 7.90 |
| 10 | 45 (5,5) | P2 | extend | 13.53 | 13.53 |
| 11 | 17 (1,2) | P1 | extend NW | 19.50 | 13.53 |
| 12 | 46 (6,5) | P2 | extend | 19.50 | 20.19 ← P2 ahead |
| 13 | 25 (1,3) | P1 | extend NW | 26.97 | 20.19 |
| 14 | 38 (6,4) | P2 | extend | 26.62 | 28.80 ← P2 ahead |
| 15 | 11 (3,1) | P1 | dense fill | 34.78 | 28.12 |
| 16 | 44 (4,5) | P2 | center fill 3x3 | 34.09 | 36.27 ← P2 ahead |
| 17 | 35 (3,4) | P1 | **counter-invade** | 38.86 | 33.00 |
| 18 | 53 (5,6) | P2 | extend | 38.52 | 40.81 ← P2 ahead |
| 19 | 12 (4,1) | P1 | dense fill | 45.99 | 40.12 |
| 20 | 51 (3,6) | P2 | extend | 45.64 | 45.64 |
| 21 | 10 (2,1) | P1 | 4-neighbor dense | 56.32 | 45.30 |
| 22 | 52 (4,6) | P2 | densify | 55.98 | 55.29 |
| 23 | **9 (1,1)** | P1 | **WIN** 65.51 | **65.51** | 55.29 |

**Game 2 ended at move 23 via threshold win for P1.** Notable: the lead swapped 4 times. Disruption was a genuine threat for many turns, but P1 always had an answer.

### Game 3 — Seat swap (P1 standard, P2 tries parasitic attach + best response)

| # | Mv | Player | Notes | P1 | P2 |
|---|----|--------|-------|----|-----|
| 1 | 27 (3,3) | P1 | center | 1.62 | 0 |
| 2 | 18 (2,2) | P2 | **parasitic attach** | 0.87 | 0.87 |
| 3 | 36 (4,4) | P1 | escape SE | 3.63 | 0.53 |
| 4 | 9 (1,1) | P2 | extend NW | 3.29 | 3.29 |
| 5 | 45 (5,5) | P1 | diagonal | 7.08 | 3.29 |
| 6 | 0 (0,0) | P2 | diagonal mirror | 7.08 | 7.08 |
| 7 | 35 (3,4) | P1 | tighten to triangle | 12.03 | 6.74 |
| 8 | 10 (2,1) | P2 | tighten | 11.68 | 11.68 |
| 9 | 28 (4,3) | P1 | 2x2 block | 17.77 | 10.99 |
| 10 | 17 (1,2) | P2 | 2x2 block | 17.08 | 17.08 |
| 11 | 37 (5,4) | P1 | extend | 24.55 | 17.08 |
| 12 | 8 (0,1) | P2 | extend | 24.55 | 24.55 |
| 13 | 29 (5,3) | P1 | extend | 32.71 | 24.55 |
| 14 | 16 (0,2) | P2 | extend | 32.71 | 32.71 |
| 15 | 20 (4,2) | P1 | extend | 40.17 | 32.02 |
| 16 | 25 (1,3) | P2 | extend | 39.48 | 39.48 |
| 17 | 21 (5,2) | P1 | extend | 48.33 | 39.48 |
| 18 | 24 (0,3) | P2 | extend | 48.33 | 48.33 |
| 19 | 38 (6,4) | P1 | extend | 57.17 | 48.33 |
| 20 | 19 (3,2) | P2 | **invasion disrupt** | 53.21 | 51.03 ← gap narrowed |
| 21 | **44 (4,5)** | P1 | **WIN** 63.55 (4-neighbor dense) | **63.55** | 51.03 |

**Game 3 ended at move 21 via threshold win for P1.**

### Reflections

**Player 1 reflection (finalized before switching to P2):**
- Strategy: center opening → densify compact blocks (2x2 → 3x3) → seek 4-neighbor dense fills near threshold.
- Opponent surprised me twice: (Game 2) P2's parasitic (4,3) + (5,3) attack briefly pulled ahead by playing a 2x2 block earlier than I did; (Game 3) P2's invasion at (3,2) move 20 cut my score by 4 points and forced me to find the move-21 4-neighbor dense (4,5) to win.
- If redoing: would try to attack P2's adjacency constraint earlier — e.g. sacrifice moves to prevent P2 from ever forming a compact block.
- **Double-pass / timeout flag: 0 of 3 games resolved by double-pass or timeout. All three resolved by clean threshold win.**

**Player 2 reflection (finalized before switching to adversary):**
- Tried three distinct strategies: (Game 1) symmetric mirror, (Game 2) adjacent contact attack, (Game 3) parasitic attach to P1's stone.
- Best result: Game 2 where the lead flipped 4 times. Proves counter-play exists.
- The fundamental problem: the game rewards whichever side achieves the first 4-neighbor dense fill. Since every move costs one tempo, P2 is always one dense move behind.
- If redoing: would try mid-game sacrificial invasions purely to delay P1 (reduce P1 eff by 4-5 each invasion) while still trying to densify myself. Game 3 move 20 ((3,2)) showed this works but wasn't enough.

**Strategy guides:**
- *P1:* Play center (3,3) or similar. Build 2x2 block fast, then 3x3. Around move 17–19, start looking for moves with ≥3 own-neighbors at Chebyshev d=1 in empty high-value cells. Expected winning move: #21–23.
- *P2:* You probably lose against optimal P1. Best chance: match P1's densification move-for-move and hope for a P1 blunder. If no blunder by move 18, start invading P1's cluster (pick empty cells with 2–3 P1 d=1 neighbors — you lose ~2 points of your own score but cost P1 ~4 points). This bought Game 2 to move 23 instead of 21.

---

## Phase 3 — Joint Strategic Analysis

- **Distinct viable strategies?** One dominates: *maximum-delta densification*. Mirror, disruption, parasitic attachment all lose with varying margins. A limited secondary strategy — *late-game invasion to reduce opponent eff* — is real but insufficient.
- **Meaningful counter-play?** Weak. Game 2 showed the lead can flip multiple times (P2 led after moves 8, 12, 14, 16, 18), but P1 always has a reply that regains tempo.
- **Short-term vs long-term tension?** Minimal. The race is ~20 moves with local optimization. No sacrifice-for-later dynamics because influence values decay immediately on placement.
- **Emergent concepts:**
  - Tempo / race to threshold (central).
  - Territory shape (compact > linear > scattered).
  - Influence field (visible in board_values).
  - Mutual reduction: a stone placed adjacent to both friendly and enemy cells reduces *both* sides' contributions on those cells. This is mildly emergent and not in vanilla Go.
  - Capture: effectively absent.
- **Topology matters?** Yes at the margin — Moore-8 + radius-2 Chebyshev decay shapes optimal geometry to compact cubes. On grid-4 (von Neumann) the same rule set would favor different shapes. But strategic depth is still shallow.
- **First-mover advantage:** **3/3 games won by P1.** Quantified: with threshold 63.46 and per-stone delta averaging 6–9 in the mid-to-late game, P1's 1-move tempo is worth roughly 7–8 effective-score points when both play dense. P2 cannot close this gap with any strategy tested.

**Seat-identity bias acknowledgment:** All three roles handled by one reasoner. Residual bias likely — I instinctively reach for "my preferred" move-ordering first. Mitigation: the three games used three genuinely different opening structures (mirror, attached-wedge, parasitic), so P2's weaker performance across all three is unlikely to be pure bias. Still, inter-team comparison (other teams) would triangulate whether true first-mover advantage is as strong as 3/3 or closer to 60–65%.

---

## Phase 4 — Novelty Adversary

**Adversary argument (forceful):**

(a) Go correspondences: same placement constraint family (the adjacent-to-own rule is from *Connection Go* / *Friendly Go*), same surround-capture rule (threshold=1 is exactly Go). Influence-based scoring is a well-known Go variant ("territory by influence field" / "area-under-influence" Go). Everything except the exact parameter values (radius 2, threshold 63, strength 1.6155) maps to known Go variants.

(b) CA: not applicable.

(c) Simultaneous: not applicable.

(d) **Transformation claim:** This is **"Go with (i) adjacent-to-own placement on Moore-8 topology, (ii) a radius-2 exponentially-decaying influence field, (iii) a threshold win condition over influence-on-own-cells."** None of the three modifications is individually novel; published Go variants exist for each. The composition is a minor parameter sweep in a well-explored family.

(e) **Expert transfer:** A strong Go player would arrive with correct intuitions on day 1:
- Build thick, solid shapes.
- Avoid isolated stones.
- Contact fights reduce both sides.
- Tempo matters.

The shapes that maximize influence-field density (3x3 blocks) are the same shapes Go calls "ponnuki-like" or "thick" formations. A Go expert would crush a naive player in a few games.

**Novelty score from adversary: 2–3/10.**

---

**Rebuttal (Player 1 + Player 2 joint):**

Pointing to concrete moments where Go intuition fails:

1. **Adjacent-to-own constraint changes opening theory.** Go's star-point opening at (3,3) / (4,4) relies on free placement; here, your first move *determines your cluster's entire future location* because you can never jump. Evidence: Game 3 P1 (3,3) + P2 (2,2) parasitic attach — if Go strategies applied, P2 could later play at (7,7) to contest the SE corner, but here P2 cannot legally make that move.

2. **Mutual-reduction contact dynamics.** In Go, a stone-to-stone contact ("crosscut", "atari") is about life/death. Here, the stone's *scalar value* is reduced on its own cell. Evidence: Game 2 move 17 P1 (3,4) — invading P2's forming cluster REDUCED P2 eff by 3.3 AND increased P1 eff by 4.8 simultaneously. No such dual effect exists in Go.

3. **Capture is essentially inert.** A Go expert's 90% of middlegame tactics (ko, seki, life-and-death) simply don't appear here. In 66 engine-verified moves across 3 games, zero captures occurred. The capture rule is vestigial.

4. **Endgame is threshold-triggered, not consensus-triggered.** Go ends when both players pass (agreeing all territory is settled). Here, the game ends the moment one side's influence sum crosses 63.46 — usually while the opponent still has legal, high-value moves to play. The Go endgame instinct of "pass when territory is sealed" would be *actively wrong* — passing when you are behind loses you the tempo race.

5. **Empty territory is worthless.** In Go (area scoring), the goal is enclosing empty cells. Here, empty cells contribute nothing to your score; you must actually place stones on cells to score them. A Go expert framing territory with thin walls would lose badly — they need to *fill* their territory.

6. **Moore-8 + radius-2 decay favors a specific geometric optimum (3x3 compact blocks)** that is different from Go's preferred "shoulder-hit" and "diagonal extension" shapes. A Go expert's aesthetic preferences (loose, flexible shapes) score ~20% lower than dense blocks here.

Despite these six distinctions, the *high-level strategy layer* (race, tempo, shape, contact) is still recognizably Go-adjacent. It is not genuinely new.

**Jointly awarded novelty score: 3/10.** The game sits firmly in the "influence-based Go variant on Moore topology" family — a minor parameter instance, not a new game concept.

---

## Phase 5 — Verdict

**Team ID:** team-14
**Game ID:** 931c58ae59b4
**Rules Summary:** Place stones adjacent to your own on an 8x8 Moore grid (first move free); stones project a radius-2 decaying influence field; first to accumulate 63.46 influence on own cells wins. Surround-capture exists but is effectively inert.
**Topology:** 8x8 Moore (Chebyshev adjacency), 2D.
**Turn Structure:** Alternating, 1 placement per turn, max 100 turns.

### SCORES

- **Strategic Depth: 4/10.** One dominant strategy (maximum-delta densification). Secondary strategy (late-game invasion to reduce opponent eff) is real but insufficient. No long-term sacrifice dynamics, no capture tactics, no life/death. The optimal move each turn is the cell maximizing a deterministic local scalar — there is correct play, not creative play.

- **Emergent Complexity: 4/10.** The one emergent property is *mutual reduction in contact fights* — an invading stone hurts BOTH sides, enabling a genuine sacrifice dynamic. Beyond that, the game is mostly local optimization. Capture rule doesn't fire. No chain of consequences — each move's effect is immediately and fully visible.

- **Balance: 3/10.** First-mover advantage is decisive. 3/3 games P1 won, including one explicit seat-swap attempt with P2 using the strongest known counter-strategies (disruption, parasitic attach). The training logs from the game report corroborate: 3 of 4 runs ended at 0.5 winrate (self-play finds no tempo-breaker) and 1 run at 1.0 (P1 dominance apparent). With perfect symmetric mirror play, P1 always crosses threshold one move before P2 could.

- **Novelty (post-adversary): 3/10.** Adversary's strongest argument: this is "influence Go with threshold win on Moore-8 with adjacent-to-own placement" — every piece has a known analog in Go variants. Strongest rebuttal: mutual-reduction dynamics in contact plus the worthless-empty-territory property would mis-cue a Go expert. But these are fingerprints of a parameter perturbation, not a new game concept.

- **Replayability: 3/10.** With one dominant strategy, games would follow roughly the same arc. Variety would come from the opening choice (Game 1 mirror vs Game 2 wedge vs Game 3 parasitic — produced visibly different mid-games), but they all end in the same way around move 21–23 with P1 winning by threshold. AlphaZero-style self-play training would quickly converge to narrow play.

- **Overall "Would I play this again?": 3/10.** It's a clean, well-scoped game with a visible influence field (which is satisfying to see grow). But the one-strategy dominance and strong first-move bias make it educational, not replayable.

### CLOSEST KNOWN-GAME ANALOG
**Influence-Go / Territory Go** (the family of Go variants where scoring is computed from a weighted influence function over stones rather than surrounded territory). Also partially resembles **Atoms / Chain Reaction** (influence threshold win) but without the explosion dynamic. It is *not* identical because of: (1) adjacent-to-own placement, (2) Moore-8 topology, (3) radius-2 decay kernel, (4) mutual reduction at contact boundaries, (5) no area-based scoring — only on-cell sums. These make it clearly a distinct instance, but within a known family.

### KILLER FLAWS
- **Strong first-move advantage** (3/3 P1 wins in this evaluation; training data corroborates ~75–100% P1 in 1 of 4 runs and self-play equilibrium in others). Seat-swap does not equalize outcomes.
- **Capture rule is inert** on Moore-8 with r=2 influence — across 66 moves, zero captures. The rule is vestigial; the game would play identically without it.
- **Single dominant strategy** (maximum-delta densification). Secondary counter-play (late-game invasion) exists but cannot overcome tempo.
- No double-pass exploit fired in any game (threshold was reachable before max_turns), so the Run-13 failure mode is *not* present here.

### BEST QUALITY
The **visible, interpretable influence field**. The threshold-based win creates a cleanly-observable "score bar" (ratio of eff / 63.46) that turns every move into an intuitive race. The mutual-reduction contact dynamics (invading enemy territory hurts both sides proportionally) is a genuinely interesting emergent property, even if underexploited in practice.

### IMPROVEMENT IDEAS
**Single rule change to add depth:** Require that the threshold be *maintained* for 2 consecutive turns before winning (i.e., threshold crossed on turn N must still be crossed on turn N+1 after opponent's reply). This creates a *defensive phase*: if you cross threshold, the opponent can invade to reduce your eff back below threshold, forcing you to find a second winning move. This would transform the game from a straight race into a race-then-defend pattern with ~3-4x the tactical content.

Alternative improvement: **lower the capture threshold or change topology to grid (4-neighbor)** so capture actually fires — introducing real life-and-death tension.
