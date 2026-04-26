# Team-6 Evaluation — Game `deb4dfe0382d` (Run 14 Champion)

**Team ID:** team-6
**Game ID:** deb4dfe0382d
**Go Essence (DB):** 0.5174 (R14 rank 1)
**Strategic Depth (DB):** 0.7179
**ELO (DB):** 997

---

## Phase 1 — Rule Comprehension

**Board:** 2D, 8×8, **torus** topology, von Neumann (4-neighbor) adjacency. 64 cells total.

**Turn structure:** **ALTERNATING**, 1 piece per turn. (Not simultaneous — this game predates the R14 simultaneous frontier.)

**Action types:** Place only (no movement). Action IDs 0–63 for cells (x = a % 8, y = a // 8), action 64 = pass.

**Placement:** Anywhere empty. First-move anywhere.

**Capture:** **Custodian (Othello-style)**, threshold=1. For each axis direction from the placed cell, walk collecting consecutive enemies until a friendly cell closes the bracket → all captured enemies flip. **Axis walks DO NOT wrap on torus** (hard-coded `0 <= pos < axis_size` in `_capture_custodian`). This is the documented prompt-level quirk.

**Propagation:** **Influence**, radius=1, strength=1.8742, decay=0.4019. On every placement, `+1.8742` added to the placed cell and `+0.7532` added to each of its 4 von Neumann neighbors (signed +1 for P1, −1 for P2). **Propagation DOES wrap on torus** — I confirmed this empirically (edge placement adds −0.75 to the opposite edge cell). Values clamped to ±100.
**Critical nuance discovered:** when a custodian capture flips a cell's owner, the cell's `board_value` is **NOT reset** — the captured cell keeps the opponent's accumulated negative-signed influence. This produces the "poison-on-capture" mechanic that dominates tactical play.

**Win condition:** **Threshold** — first player whose sum of `board_values` on their own cells exceeds **+38.6164** (negated for P2) wins. `max_turns = 102`.

**State dimension:** 131. Num actions: 65.

**Not degenerate:** threshold is reachable in ~20 well-clustered moves (I hit it by move 21 in games 2 and 3). No double-pass exploit observed in any of my 3 games — all ended by threshold, not majority.

**Double-pass exploit check:** the game technically allows two consecutive passes to end by majority, but the threshold is easily reached before pass-spam becomes attractive. I did not see it fire.

---

## Phase 2 — Strategic Play (3 games)

### Game 1 (P1 me, P2 me, seat-swap in Game 3)
- Move sequence: `27,28,26,29,19,20,21,36,44,30,25,31,35,39,18,38,43,46,34,45,17,37,33,47,42,22,11`
- **Winner: P1** at move 27 (influence +39.45 > 38.62).
- Key moments:
  - Move 7: P1 (5,2) triggered custodian capture of P2's (4,2). **P1's effective influence DROPPED from +7.13 to +6.38 despite gaining 2 pieces** — the captured cell inherited the negative value P2 had placed. This is the "poison" discovery.
  - Move 9: P1 (4,5) captures 2 more O pieces. Piece count 8 vs 1, but influence nearly tied (+2.24 vs +1.87). Dramatically illustrates capture is anti-strategic.
  - Move 22: P2 plays (5,4) as a **deliberate sacrificial bait** — placing a stone knowing P1 can recapture via (5,6). If P1 takes the bait, P1 inherits 3 poisoned cells worth −5.6 effective. **P1 correctly declined the bait and cleansed (1,4)=33 instead.** This is a novel tactic.
  - Move 26: P2 tried (0,3) to capture 4 P1 cells along row 3. Piece count 14 vs 12, **but P2's effective influence CRASHED from +34.94 to +29.30**. The 4 captured cells (each with large positive values) flipped into P2 ownership as large negatives on P2's sum, self-destructing the position. Another capture-trap.
  - P1 won the threshold race by ~1 tempo.

### Game 2 (same seats)
- Move sequence: `36,0,37,1,44,8,45,9,28,2,46,10,35,16,38,17,43,18,27,19,29`
- **Winner: P1** at move 21 (+42.46 > 38.62).
- Both players built diagonally-opposed 3×3 clusters. The game was essentially a mirrored race. P1 won by one tempo. P2 never achieved a winning move despite symmetric play.

### Game 3 (seat-swap: I reasoned as old-P2 for new-P1, old-P1 for new-P2)
- Move sequence: `18,45,26,37,19,44,27,36,20,38,28,47,11,46,25,39,21,32,17,40,10`
- **Winner: P1** at move 21 (+40.95 > 38.62).
- Symmetric play again. Seat-swap did not break first-mover advantage — but this may reflect my sequential-reasoner bias rather than real player skill difference.

### Reflection
- All 3 games resolved **via threshold**, not majority / double-pass. **Zero double-pass exploits.** Max-turns cap never approached (longest game = 27 / 102 turns).
- Game lengths 21–27 moves match R14 training avg 22.5–32.5 — consistent.
- **First-mover advantage: decisive.** P1 won 3/3, including after seat-swap. P2 never closed the ~1.5-point tempo gap.

### Strategy Guides (condensed)
**P1:** Place centrally on torus. Grow 2x2→3x2→3x3 dense cluster. Cleanse empty cells with 2 friendly neighbors for ~+4.89 gain/move; 1-friend cells give ~+3.37. AVOID CAPTURES — they poison you. Ignore opponent's bracket-bait.

**P2:** Mirror with a cluster diagonally across. Race threshold. Consider poison-sacrifice bait (place knowing you'll be captured, to crash P1's influence). Use wrap adjacency (corners are effectively 2-friend when cluster wraps).

---

## Phase 3 — Strategic Analysis

- **Distinct strategies?** Largely no — optimal play converges to "cluster + cleanse tempo". The capture-based strategy is actively anti-strategic.
- **Counter-play?** Limited. Tactical variation lives in (a) cluster direction, (b) sacrifice-bait plays, (c) contest-at-boundary decisions. Strategically thin once the capture-is-bad insight is discovered.
- **Short-vs-long tension?** YES — custodian capture creates a real dilemma: reduce opponent pieces now at the cost of long-term poisoned influence. This is a genuine (albeit single-axis) strategic tension.
- **Emergent concepts:**
  - *Influence territory* (dense blocks compound their own field).
  - *Poisoning via capture* (captures inherit opponent-signed influence).
  - *Capture-decline as positive move* — **not** present in any standard abstract game I know.
  - *Sacrifice-bait* (place to be captured, poisoning the capturer).
  - *Tempo/race to threshold*.
- **Topology matters?** Mildly. Torus eliminates center/corner asymmetry (everything becomes homogeneous) but the custodian non-wrap keeps edge-relative thinking alive. Wrap-propagation gives corner clusters a minor pre-influence bonus.
- **First-mover advantage:** Clearly present. P1 won all 3/3 games, including seat-swap. This game is **balance-poor** in alternating turn structure.

---

## Phase 4 — Novelty Adversary + Rebuttal

### Adversary argument
This is **Othello + Go influence + torus + threshold scoring** — a re-skin under the transformation `{Othello capture, score = influence_sum_over_own_cells}`. Specifically:
- Custodian capture = Reversi/Othello rule, verbatim.
- Influence decay-radius scoring = classic pre-MCTS Go AI (Bouzy influence, Chen influence estimators).
- Torus topology is a known Go/connection-game modifier.
- Combination ≈ "Toroidal Othello scored by Bouzy influence," which is a 2-line rule change from known games.

### Rebuttal (citing Phase 2 moments)
1. **Othello expert transfer FAILS:** Captures hurt rather than help. Game 1 move 7 (P1 captured 1 O, lost 0.75 effective influence) and move 9 (P1 captured 2 O, influence at 2.24 with 8 pieces vs P2's 1.87 with 1 piece) show capture produces INVERSE of Othello's value function. Classical Othello strategy (maximize captures, corner-grab) is actively misleading.
2. **Go expert transfer FAILS:** Game 1 move 26 — P2's 4-piece custodian capture (a classically dominant Go/Othello move) destroyed +5.6 of P2's effective influence. No Go position has this property; Go captures are always net-positive in scoring.
3. **Novel tactic — sacrifice-bait:** Game 1 move 22 P2 (5,4). This is deliberate place-to-be-captured to poison the capturer. Closest analogs are Go ladder-breakers (but Go ladders are about liberties, not value inheritance). This tactic genuinely emerges only from custodian × signed-influence × owner-flip-without-value-reset.
4. **Capture-decline as winning move:** The correct P1 response to P2's (5,4) in Game 1 was "decline the bracket capture and cleanse elsewhere." No standard abstract game prioritizes decline-capture as default. Gomoku, Reversi, Go all reward capture.

### Resolution
The rules are indeed a structural composite of known mechanics (custodian + influence + torus + threshold). But the specific interaction creates one genuinely novel dominant-strategy inversion (capture-is-bad), which supports a sacrifice-bait sub-game. This is more than a pure re-skin but less than a fully new abstract.

**Novelty score: 4/10.**

---

## Phase 5 — Verdict

**Team ID:** team-6
**Game ID:** deb4dfe0382d
**Rules Summary:** 8×8 torus, alternating placement; Othello-style custodian capture (threshold 1, non-wrapping); influence propagation radius 1, strength 1.874, decay 0.402 (wrapping); win when own influence sum exceeds +38.62.
**Topology:** 2D torus, axis_size=8, 64 cells, von Neumann adjacency.
**Turn Structure:** alternating, 1 piece/turn.

### SCORES (1–10)

- **Strategic Depth: 5** — one genuine tension (capture-vs-cleanse) and one novel tactic (sacrifice-bait), but optimal play largely converges to a "dense cluster + cleanse" mirror race. Most decisions reduce to gradient-greedy cleansing. The DB score 0.7179 somewhat overstates depth.
- **Emergent Complexity: 6** — the capture-poison mechanic is emergent (combining two simple rules: custodian + signed influence + no-value-reset-on-flip). Sacrifice-bait tactic is real. But emergence is shallow; no ko-fights, no long-range forcing sequences.
- **Balance: 3** — P1 wins 3/3 in my games including after seat-swap. Clear first-mover advantage on alternating turn structure. Training DB shows 0.5 winrate but that reflects self-play training equilibrium, not human-play balance. A minor rule change (P2 starts with +1 free cleanse / threshold asymmetry) would fix this.
- **Novelty (post-adversary): 4** — not a pure Othello-on-torus re-skin (the poison mechanic and sacrifice-bait tactic have no clean analog), but the game is still clearly a composite of Othello + Go influence scoring + torus. The single novel tactic doesn't justify 7+.
- **Replayability: 4** — once you internalize "don't capture, cleanse instead," most games converge to mirror patterns. Some variation in sacrifice-trap execution, but not enough to reward many replays.
- **Overall "Would I play this again?": 4** — once or twice to appreciate the poison mechanic, then the tempo race becomes rote.

### CLOSEST KNOWN-GAME ANALOG
**Toroidal Othello with Bouzy-style influence scoring.** Not identical because (a) Othello's terminal condition is majority count, not threshold on influence, and (b) the no-value-reset-on-custodian-flip creates the poison mechanic that inverts Othello's "capture is good" heuristic.

### KILLER FLAWS
- **First-mover dominance:** P1 won 3/3 under equal skill, including seat-swap. This is the most serious concern.
- **Capture mechanic is a trap:** custodian capture is almost always anti-strategic (because of signed-influence inheritance), which makes 1/4 of the rule set (the capture rule) effectively vestigial/negative. Players who don't realize this will lose badly; players who do realize it will play a simpler game.
- **Strategic convergence:** optimal play on both sides = mirror cluster + cleanse tempo; no distinct playstyles.
- **No double-pass exploit observed** (positive finding — unlike Run 13's pilot failure mode).

### BEST QUALITY
The **custodian-capture-as-poison** inversion is genuinely interesting. Most abstract games reward aggression; this one punishes it (in a specific, legible way). The derived tactic of **sacrifice-bait** (deliberately placing to be captured to poison the opponent) is a mechanic I haven't seen elsewhere and is worth noting.

### IMPROVEMENT IDEAS
**Reset `board_values[cell] = 0` on custodian flip.** This would restore capture to its usual "always positive" role, which would open up a real tradeoff between capture and cleanse tempo. It would also remove the sacrifice-bait tactic, unfortunately — but more importantly it would likely restore balance (reducing first-mover advantage) because capture becomes a real counter to a pre-threshold P1 lead. Alternative: give P2 a small threshold handicap (P2 wins at +37.5) to correct first-mover advantage while keeping the poison-on-capture mechanic.

---

## Technical Notes

- **Engine verification:** every move in all 3 games was run through `play_helper.py --action play` or my `team6_inspect.py` helper. No proposed move was rejected.
- **Influence helper:** `/Users/jamesbrowne/aigame/team6_inspect.py` instantiates `GameEngineV2` and prints `board_values` + per-side effective influence totals after a sequence of moves. This was essential — `play_helper.py show` does not display the influence field, and without it threshold dynamics are invisible.
- **Seat-swap caveat:** I reasoned P1 and P2 sequentially as the same agent. Game 3 swap did not change outcome. Real human teams may see different play patterns, but the mechanical first-mover tempo advantage should reproduce.
- **Time budget:** ~28 minutes of effective reasoning across 3 games, within the 25-min-per-game guideline.
