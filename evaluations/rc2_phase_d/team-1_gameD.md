# Team 1 — Game D verdict

## Phase 1 — Rule comprehension

- Mechanics in your own words: 3D **torus**, axis 4 (4³=64 cells, **every cell
  degree 6**, all axes wrap — no edges). PLACE only (ids 0–63; 64 = PASS; no
  pie) with the **forced-contact constraint: you must place adjacent to an
  ENEMY stone** (waived only while you have zero stones; re-arms if you are ever
  wiped to zero). **Capture = custodian/Othello:** after placing, along each
  axis line, runs of enemy stones bracketed between the placed stone and another
  of yours are **flipped** to your colour — but the line-walk **clamps at the
  0..3 bounds and does NOT wrap** (verified per `--rules`). **Influence field**
  (radius 2, strength 1.098, decay 0.797), permanent. **Win = THRESHOLD
  influence race:** Σ board-value over your owned cells (sign-corrected) > 36.94.
  **Ghost influence:** a flipped stone keeps its ORIGINAL-sign influence forever.
  Super-ko active; turn limit 100 → more-stones tiebreak; double-pass → DRAW.
- What actually ends the game: the **threshold firing (~+37–44) around ply
  33–55** in my games; I did not reach the turn limit in competitive lines.
  Scores are volatile (single flips swing ±13), so the threshold is crossed
  only after surviving the opponent's flip-backs.
- Surprises: (1) **Flipping is a trap.** Custodian flips gain you stones but the
  flipped cell keeps the enemy's old (now opposite-sign-to-you) influence, so a
  stone you flipped often sits on net-enemy influence and *subtracts* from your
  score. (2) **Stone count is decoupled from score** — in several games the
  loser had MORE stones. (3) A player can be **flipped to zero stones**,
  re-arming "place anywhere."

## Phase 2 — Strategic play (≥3 full lines, both roles)

### Line 1 — you as P1
- Moves: `0,2,1,3,6,7,4,5,9,10,11,8,14,12,13,15,18,19,16,22,21,26,25,30,24,27,28,31,29,17,23,20,33,34,38,42,37,36,32,35,39,41,40,43,45`
- Plan and what happened: I (P1) built a compact influence cluster, always
  placing on the required enemy-adjacent cell that **grew my own influence
  without bracketing** (avoiding self-harmful flips). P2 mirrored. My positive
  influence accumulated steadily and I crossed +36.94 one tempo ahead.
- Result: **P1 wins, threshold at +43.8 vs +27.7, ply 45 (P1=22, P2=23).**

### Line 2 — you as P2
- Moves: `0,2,1,3,6,7,4,5,9,10,11,8,12,13,14,15,18,19,16,22,26,23,20,27,24,17,33,34,35,39,43,21,25,38,37,28,44,31,30,47,46,29,45,32,48,36,40,41,42`
- Plan and what happened: Driving P2, I played the *correct* strategy — quiet
  influence-building, refusing to flip — against a P1 that flipped
  aggressively. My discipline paid off relatively (I reached **+30.5**, my best
  result of any line), and P1's flipping bloated its stone count to 35 while
  hurting its own score. But I was still one tempo short: P1 crossed +37.18
  before I crossed +36.94.
- Result: **P1 wins, +37.18 vs +30.51, ply 49 (P1=35, P2=14)** — I lost by
  tempo despite playing the better style.

### Line 3 — adversarial / novelty-stress
- Moves: `0,2,1,3,6,10,5,4,7,11,8,9,13,14,15,12,18,34,17,16,20,24,21,22,25,26,29,28,30,31,19,35,23,27,32,33,36,37,40,39,41,45,44,60,48,43,49,61,50,57,51,53,63,47,52` (flip-greedy P2 vs quiet P1), plus `20,21,22` (single-flip + ghost probe).
- What you tried to break / stress: I made P2 **maximise custodian flips** to
  see if aggression pays. It is actively self-defeating: P2 flooded to **31
  stones** but its score collapsed to **+7.9** while a non-flipping P1 reached
  +40.4 — the ghost influence on every flipped cell dragged P2 down. The
  `20,21,22` probe shows the mechanism directly: P1 flips one P2 stone but the
  cell keeps its −influence, so P1's gain is partly cancelled.
- Result: **flipping confirmed a trap; P1 wins +40.4 vs +7.9, ply 55** with
  fewer stones.

### Additional lines (optional)
Across policy combinations (quiet-build vs quiet-build, flip-greedy vs
quiet, quiet vs flip-greedy), **P1 won every line** — even when P1 played the
weaker style. The first-move tempo is decisive and there is no pie rule to
offset it.

## Phase 3 — Joint strategic analysis

- Core tactical loop: "Place the mandatory enemy-adjacent stone that maximises
  your own positive influence while **not** bracketing enemy stones into a
  flip." The skill is navigating the forced-contact rule without triggering the
  ghost-influence self-tax.
- Counterplay: Two-sided in score terms — flips genuinely swing the board
  (Line 1/Line 2 scores were close, tied at one point in self-play) — but the
  best counterplay is *restraint*, and even perfect restraint loses to the
  first player by a tempo (Line 2). Aggressive counterplay (flipping the
  opponent) backfires (Line 3).
- Topology/board effects: The torus removes edges, so every cell is symmetric
  and influence accumulates evenly; the custodian clamp (no wrap) is the one
  asymmetry, but it rarely matters because flipping is undesirable anyway.
- Emergent concepts: "**Flip-tax**" (capturing costs you score via ghost
  influence) and "**count≠score**" (more stones can lose). Both are real and
  recurred in every game.
- Player agency: **Moderate.** More than the pure tempo races — flip decisions
  and influence shaping matter, and a wrong flip can cost you the game — but the
  meta-outcome is still tempo-decided for the first player.

## Phase 4 — Novelty adversary

- Strongest re-skin case: **Othello (custodian flips) crossed with an
  influence-area race**, on a torus. Flipping is Reversi; threshold-on-influence
  is the same engine family as Game B; the torus is cosmetic. Strip the ghost
  influence and it is "Reversi where you score field control."
- Honest novelty assessment: **Moderate.** The genuinely original element is
  the **ghost-influence flip-tax**, which inverts the usual Othello incentive
  (here you do NOT want to flip), plus the count≠score decoupling. That is a
  real, non-obvious idea. But, as in Game B, the novel mechanic manifests as a
  *deterrent* (don't flip) wrapped around a first-player influence race, and
  there is no balancing lever, so the realised game is thinner than the rulebook
  suggests.

## Phase 5 — Verdict

- P1-role experience sub-score (1-10): **3.6** — you win, and avoiding the
  flip-trap while shaping influence is a genuine (if subtle) skill.
- P2-role experience sub-score (1-10): **3.0** — competitive on score (Line 2
  reached +30.5) but structurally one tempo behind with no lever to recover.
- Role-averaged sub-score: **3.3**
- **Fairness perception (1–5): 2** — P1-favored: P1 won every configuration I
  tried, including when it played the weaker style, and there is no pie rule to
  offset the first-move tempo.
- **Overall (1-10): 3.4**
- Justification: Anchoring near R20/R21 (3.7/3.69) but below, D is a richer
  artifact than the pure races — Lines 1–2 show real influence-shaping and
  close score contests, and Line 3 surfaces a genuinely clever ghost-influence
  flip-tax that makes the obvious Othello aggression self-defeating. But the
  capture mechanic, like Game B's, ends up as a *trap to avoid* rather than a
  tool to use, the game is clearly P1-favored with no balancing pie, and the
  core remains a forced-contact influence race the first player wins on tempo.
  Functional-but-negative-space depth without a fairness fix lands it at **3.4**,
  just under the anchor band.
