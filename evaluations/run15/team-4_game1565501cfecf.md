# Team-4 evaluation — Game `1565501cfecf` (Run 15 champion)

Team ID: `team-4`
Game ID: `1565501cfecf`
Evaluator: single-agent run (all three roles sequentially; seat-bias acknowledged in Phase 3).
Independent pass: yes — the pilot evaluation at `team-pilot_game1565501cfecf.md` was not read during this assessment.

---

## Phase 1 — Rule Comprehension

### Board, topology, actions

- **Board:** 8×8 grid (64 cells).
- **Topology:** torus — both axes wrap. Radius-3 influence propagation wraps around edges. Capture-walks would not wrap per pilot caveat, but capture is disabled here.
- **Num actions:** 65 (64 placements + 1 pass at action 64).
- **Action types:** `place` only. The `move_constraint: adjacent_empty` in the rule dict is inert (no move actions exist).
- **Placement constraint:** any empty cell, any time, for either player (`target=empty, constraint=anywhere, first_move_anywhere=True`).

### Turn structure — SIMULTANEOUS (key feature)

- `turn_structure.turn_type = "simultaneous"`, `pieces_per_turn = 1`.
- Both players submit one action per tick; engine resolves via `step_simultaneous(a_p1, a_p2)`.
- **Collision resolution (empirically verified):** if both players target the same empty cell, **both stones annihilate** — the cell stays empty, both players forfeit the placement. Test: `--rounds "27:27"` → board remained empty after round 1, step_count=1, piece counts stayed at 0/0.
- **Double-pass (R15 rule):** Two simultaneous passes end the game as a **DRAW** (winner=None). Verified with `--rounds "27:pass,pass:pass"` → "GAME OVER: Draw".

### Capture / CA

- `capture_type: none`. No CA. No captures. **Pure placement + influence-threshold game.** Nothing ever leaves the board except via collision.

### Propagation (influence)

- `prop_type: influence`, `radius: 3`, `strength ≈ 0.9657`, `decay ≈ 0.5867`.
- Signed field: P1 positive, P2 negative. A single stone produces (approximately, on the torus):
  - self: +0.966
  - Manhattan r=1: +0.57 each
  - r=2: +0.33 each
  - r=3: +0.19 each
- Adjacent opposing stones attenuate each other's own-cell value: each owns a cell with signed value ≈ ±0.40 instead of ±0.97.

### Win condition

- `condition_type: threshold`, `threshold ≈ 38.627`, `target_dimension = 0`.
- `_check_threshold` (engine_v2.py:748–761) iterates `for player in (1, 2)` and returns on the first player whose `effective` sum-over-owned-cells exceeds threshold. **P1 wins simultaneous ties by iteration order** (R15 pilot flag — empirically confirmed below).
- `max_turns: 100`. Beyond that, majority-pieces tiebreak; but double-pass → draw (R15).

### Degeneracy / degenerate-rule checks

- **CONFIRMED asymmetry (R15 pilot flag):** In a constructed mirror-symmetric endgame (P1 cluster translated by (4,4) on the torus to give P2), both players reach 38.92 on the same tick; engine returns `winner=0` (P1). Trace:
  ```
  tick 1  P1=0.97   P2=0.97
  tick 5  P1=13.54  P2=13.54
  tick 9  P1=34.71  P2=34.71
  tick 10 P1=38.92  P2=38.92  → winner=0 (P1) [1. -1.]
  ```
  This is the `engine_v2.py:748-761` bias. It is **directly exploitable** in mirror-matched play and, as Games 1 and 3 below show, even when P2 is objectively ahead in raw influence, P2 can lose on a same-tick crossing.
- Double-pass = draw ✓ (not a silent P1 win).
- Threshold 38.6 is reachable within ~10–14 pieces per side (verified; no non-convergent games).
- No "pass-spam" win, no inert captures, no CA.

---

## Phase 2 — Strategic Play

**Protocol.** Three games, each move engine-verified via `sim_play_helper.py`. Games 1 & 2: I play as P1 first (freezing P1 reasoning before reading P2 reasoning). Game 3: seat swap — I play as P2 first. Single-agent caveat (seat-identity bias) is noted here and revisited in Phase 3.

### Game 1 — both players build antipodal clusters

- P1 plan: central 3×4 cluster at rows 2–4, cols 2–5.
- P2 plan: antipodal (via torus wrap) cluster at rows 5–7, cols 4–7, then encroach from the south.

Moves (12 rounds, as `a_p1:a_p2` pairs):
```
27:55, 28:63, 35:62, 36:54, 26:47, 34:46, 19:61, 20:53, 21:45, 37:52, 29:44, 43:60
```

Outcome trace (abbreviated):
- Round 11 (11 pieces each): P1=38.41, P2=38.41 — identical.
- Round 12 (12 pieces each): P1=41.85, P2=42.60 — **P2 is ahead**, but both cross threshold on the same tick.
- **Result: P1 wins. Winner=0, rewards [1.0, -1.0].**

**This is the pilot bias firing on an ordinary game, not a contrived symmetric construction.** P2 out-scored P1 on the crossing tick and still lost.

P1 reflection: strategy was "claim a tight 3×4 cluster for density." Worked. I wouldn't do anything differently — except note that I was lucky P2 chose antipodal rather than adjacent-aggressive play (adjacent attack would have attenuated my stones).

P2 reflection: "build antipodal cluster, then encroach." The encroach stones at (4,5) (round 11) and (4,7) (round 12) nudged me ahead in raw score but didn't change the crossing-tick parity. **I would change:** delay my threshold-crossing stone by one tick (play a filler move that doesn't cross), forcing P1 into a position where P1 crosses alone (and loses? no — P1 just wins unilaterally then). The real fix needs P2 to cross a tick BEFORE P1, which requires fundamentally different pacing from P1.

Endgame reached stated win condition (threshold crossing), not by double-pass.

### Game 2 — P2 plays adjacent-attack

- P1 plan: NW-quadrant cluster (rows 2–4, cols 1–4), then expand.
- P2 plan: attack P1's cluster from the west/north with a border to attenuate.

Moves (14 rounds):
```
27:32, 28:33, 19:40, 20:41, 35:48, 36:49, 26:39, 25:31, 18:0, 17:8, 50:16, 42:24, 10:2, 11:3
```

Outcome trace:
- Round 8 (8 pieces each): P1=22.73, P2=21.68 — P1 slight lead.
- Round 12 (12 each): P1=31.97, P2=31.97 — dead even.
- Round 14 (14 each): P1=39.13, P2=31.59 — **P1 crosses alone, P2 lagged**. Rewards [1.0, -1.0].

P1 reflection: by expanding north onto rows 0–1, I diluted P2's adjacency attack (those new P1 stones had no P2 neighbors), boosting my score. Strategy: "if P2 attacks on one side, expand the opposite side."

P2 reflection: adjacency attack attenuates BOTH sides' own-cell values, so if I don't have strict piece-count parity or a stronger internal cluster, I lose the trade. **I would change:** instead of clinging to the attack front, I should have built a second compact cluster in an unoccupied quadrant of the torus to catch up. Splitting into two tight clusters of 6 instead of one stretched 14 would have given me more self-support density.

Endgame reached stated win condition via solo P1 crossing (legitimate win, no bias needed).

### Game 3 — seat swap, P2 plays adjacent cluster under P1

- I committed the P2 reasoning first: build a tight 3×3 block at rows 2–4, cols 2–4, then add extensions downward.
- P1 reasoning committed after: corner cluster at rows 0–2, cols 0–4 (wrap-advantaged).

Moves (13 rounds; includes one illegal-move correction as required evidence):
```
0:27, 1:28, 8:19, 9:20, 16:35, 17:36, 2:18, 10:26, 3:34, 11:42, 12:43, 4:51, 5:44
```
- Note: attempted `18:17` in round 10 was REJECTED (action 18 already owned by P2 round 7; action 17 already owned by P1 round 6). Replaced with `11:42`. **Legal-action constraint empirically confirmed — engine is strict.**

Outcome trace:
- Round 8 (8 each): P1=22.91, P2=22.91 — even.
- Round 9 (9 each): P1=25.81, P2=27.61 — **P2 ahead**.
- Round 12 (12 each): P1=35.10, P2=37.20 — P2 still ahead.
- Round 13 (13 each): P1=39.30, P2=43.88 — P2 out-scored P1 by **4.58 points** but BOTH CROSS THE THRESHOLD ON THE SAME TICK.

**Result: P1 wins. Winner=0, rewards [1.0, -1.0].**

This is the most damning demonstration of the tie-break bias: P2 was winning on raw influence throughout the whole mid-late game, scored 43.88 vs P1's 39.30 on the crossing tick, and still lost because `_check_threshold` iterates P1 first.

P2 reflection (my voice as P2): I executed on cluster density (3×3 core) and P1's attack ran out of productive squares after round 6. I was on track for a "legitimate" P2 win — except the engine's return-on-first-cross means I need not to just reach threshold while ahead, but to reach it a TICK before P1. **To actually win as P2 in this game, I must deliberately slow P1 (collision-sniping high-value P1 moves) or build in a region P1 literally cannot influence.** The latter is hard on an 8×8 torus with radius-3 influence.

P1 reflection (seat-swap role): I was outplayed on density — P2's 3×3 block is strictly denser than my 3×5 block because the torus has no edges/corners, so my "corner" advantage was illusory. **I won only because of the iteration-order bias.** On a fairer engine I would have lost this game.

Endgame reached stated win condition (threshold), but the winner assignment relied on the bias.

### Games resolving by double-pass draw: 0 / 3. Games resolving at max_turns: 0 / 3. All three games reached the stated win condition within 14 ticks (fast).

### Seat-swap scoreboard

| Game | P1 seat | P2 seat | Winner | P1 final score | P2 final score | Fair winner (by raw score)? |
|------|---------|---------|--------|----------------|----------------|-----------------------------|
| 1    | me-as-P1 | me-as-P2 | **P1** (engine) | 41.85 | 42.60 | P2 (by 0.75) |
| 2    | me-as-P1 | me-as-P2 | **P1** (engine) | 39.13 | 31.59 | P1 (legitimate) |
| 3    | me-as-P2 | me-as-P1 | **P1** (engine) | 39.30 | 43.88 | P2 (by 4.58) |

**P1 won all three games (3/3). On raw score, P2 should have won 2/3.** The engine bias flipped Games 1 and 3.

### Strategy guides

**P1 strategy guide.** (i) Play first move near center of any chosen quadrant. (ii) Build the tightest possible 3×3 or 3×4 block — corners of the cluster give highest return per stone. (iii) If opponent plays adjacent-aggressive, expand on the opposite face of your cluster to build stones with no opposing neighbors. (iv) Pace yourself to cross threshold on the SAME tick as P2 if at all possible — you win ties. Never cross a tick early if you can help it. (v) Use collision (matching P2's target exactly) as a denial weapon on P2's pivotal moves.

**P2 strategy guide.** (i) You need to cross the threshold a tick BEFORE P1, not just with a higher score. Same-tick ties go to P1. (ii) This means your cluster must be strictly denser than P1's, AND you must avoid any turn where you add less influence than P1 does. (iii) Prefer a location far enough from P1 that their radius-3 field doesn't attenuate your own-cell values. (iv) Consider collision-sniping: if P1 telegraphs a high-value placement (e.g. filling a cluster gap), target the same cell to annihilate both stones — you break even on the tick but deny P1 their cluster gain. This converts a symmetric-pace race into a P1-disrupted race. (v) Split builds are usually bad — commit to one tight cluster and a small detached "influence spoiler" at most.

---

## Phase 3 — Strategic Analysis (joint P1/P2 discussion)

**Are there distinct viable strategies?** Modestly. The core dominant pattern is "build a tight cluster of 10–14 stones." Within that: (a) antipodal builds (both players far apart) give high raw scores but are prone to same-tick crossing → P1 advantage; (b) adjacent-attack builds let one player attenuate the other but also self-attenuate; (c) split-cluster builds are strictly worse than single-cluster due to loss of internal self-support. So the strategic tree is shallow — ~3 macro-strategies, only one (tight cluster, crossing on own terms) is clearly optimal.

**Counter-play.** Limited. Adjacency attack exists but is a negative-sum trade. Collision-denial exists (mutual annihilation) but costs the denier a tempo equal to what they deny. On an 8×8 torus with radius-3 influence, once both players commit to a cluster there is no ko-like tactical threat — stones don't move or die, so positions only accrete.

**Short- vs long-term tension.** Weak. Every placement adds monotonically to your score (modulo opposing attenuation). There is no sacrifice-for-later dynamic; you cannot trade a stone for a better future position because stones cannot be removed.

**Emergent concepts.** Territory: yes, in a soft-influence sense. Influence/tempo: partially — pace parity matters. Mutual annihilation (the simultaneous-game signature): present but underpowered; collisions are pure tempo losses for both. Ko fights: absent. Seki/life-and-death: absent (no captures).

**Does topology matter?** Yes, but subtly. The torus makes every cell equivalent (no corners/edges), which actually flattens strategic variety — classical corner/edge theory (Go, Reversi) doesn't apply. Radius-3 wrap means two "opposite corners" of the 8×8 are only Manhattan-4 apart on the torus, still within influence range. The topology homogenises the board to a single undifferentiated surface.

**First-mover advantage in a simultaneous game.**

- **Seat-swap evidence: 3/3 wins for P1 across Games 1–3, despite seat swap in Game 3.**
- In Games 1 and 3, P2's final score was higher than P1's; P2 still lost.
- The simultaneous mechanic did NOT eliminate first-mover advantage. It *moved* the advantage from "more pieces / better position" (classical) to "wins iteration-order ties on threshold-crossing ticks" (engineered-in). In mirror-symmetric play, P1 wins with probability 1. Under realistic play where both sides converge toward a tight cluster, same-tick crossings are common (because the threshold is reached gradually and clusters of similar density arrive at similar scores), so the bias fires often.
- **Quantitative estimate:** across 3 games, P1 won on the iteration-order bias in 2/3 games (67% of games would have gone differently on a fair engine). This is a serious balance defect.

**Seat-identity caveat.** Single-agent pass introduces correlation: my "P1" and "P2" strategies share an author. I mitigated by committing reasoning per-side before reading the other side, and by swapping seats in Game 3. The 3/3 P1 sweep is very unlikely to be author-bias: in Game 3 I deliberately made P2's plan first and stronger (3×3 dense block), and P2 still lost to iteration-order. The bias is real.

---

## Phase 4 — Novelty Adversary (mandatory)

### Adversary opening

This game is **Reversi / Othello with influence-weighted scoring, on a torus, with simultaneous turns.** Strip the ornaments and you have: place stones on a grid; count a scalar to determine the winner; no mobility, no captures. That's the Reversi/territory family at its most stripped-down.

(a) **Catalog comparisons.**

- **Go:** Go is this game's obvious comparison — influence, territory, capture. But Go has capture and liberties, which this game lacks entirely. Score attribution by *sum of a Gaussian-like radial kernel on owned stones* is not Go scoring. Partial analog only.
- **Reversi/Othello:** both end by scalar threshold on piece control. Othello's capture-by-flanking is absent here, but the scoring concept (count your influence) is directly analogous. **This game is Othello without the flanking mechanic — a strict subset of Othello rules.** That is a strong "not novel" signal.
- **Hex / Y / Havannah:** connectivity games. No connectivity win here → not analogous.
- **Gomoku / Connect6 / Pente:** n-in-a-row. No linear condition here → not analogous.
- **Amazons:** move + shoot. No movement here → not analogous.
- **Lines of Action:** movement + connectivity. Not analogous.
- **Tumbleweed:** the **closest named analog** — Tumbleweed places stones whose "height" is determined by line-of-sight to existing friendly stones, and the winner controls more cells. Tumbleweed uses sightline instead of radius, hex instead of square torus, and threshold-by-majority instead of by absolute value, but the meta is identical: **"place and accumulate a spatial control metric that rewards clustering."** A Tumbleweed player would understand this game instantly.
- **Slither:** captures by sliding — not analogous.
- **Blotto / Colonel Blotto:** simultaneous resource allocation with territory scoring. Strong analog for the *simultaneous* axis. Each tick, both players allocate 1 "unit" to a cell; value is a spatial score. This is essentially iterated Blotto on a geometric surface.
- **Life-like CA games:** no CA here.
- **Slither, Nim:** no relevant overlap.

(b) **CA analysis.** Not applicable — this game has no CA.

(c) **Simultaneous-game comparisons.**

- **Diplomacy:** order-writing with simultaneous resolution, but Diplomacy's mechanic is supports/cuts/retreats. Only shared primitive is "submit secret orders, resolve at once" — superficial.
- **RPS-scaled games:** 2-player games where each side has K alternatives; here K ≈ 64 cells, so "RPS-64 per tick." At this scale the RPS dynamic is weak — collision is the only direct conflict, and it costs both players equally.
- **Blotto (Colonel):** best analog. Iterated 1-unit Blotto on a grid with radial scoring. Not identical (Blotto is single-shot and has a fixed total allocation), but structurally very close.
- **Gungo (simultaneous Go variants):** same "both move at once" primitive, different resolution. Closest spirit to this game. If one exists with influence scoring, this is that.

(d) **Topology / coordinate re-skin argument.** This game is essentially **"Othello minus flanking, on a torus, with simultaneous turns, and with Gaussian-radial scoring instead of flip-based scoring."** Under the transformation "scoring function: f(count of adjacent friendlies) → f(radial influence)" it collapses to a family of weighted-territory games. The radius parameter is tuned but not novel.

(e) **Would an expert at Tumbleweed or Othello have an advantage?** Yes, substantially. The cluster-density intuition transfers directly from Tumbleweed. The "count what you control" intuition transfers from Othello. A Go 1-dan would have less of an edge, because Go's tactical structure (life/death, ko, liberties) doesn't appear here. **An intermediate Tumbleweed player would outperform an inexperienced player within one evening of play.**

### Adversary's strongest argument

This game is a simultaneous variant of Tumbleweed/Othello with radial scoring on a torus. The "simultaneous" axis contributes little because (i) collisions are pure mutual waste, (ii) the only other simultaneity-specific mechanic is the threshold tie-break, which is an **engine bug** that rewards P1, not a deliberate game-design feature. Strip the bug and you have a game that would play close to a classical alternating weighted-territory game. **Novelty score: 3.**

### Rebuttal (P1+P2 joint)

1. **Tumbleweed disanalogy.** Tumbleweed's stones have a height = number of friendly stones in line-of-sight. That is a *countable, integer* metric with a line-of-sight anisotropic signal. This game's scoring is a *real-valued Gaussian-like radial kernel* that decays isotropically with radius. The strategic implication is genuinely different: in Tumbleweed, a single unblocked friendly stone at distance 10 contributes as much as one at distance 2 (binary sightline). Here, a friendly at distance 3 contributes ~0.19 and one at distance 4 contributes 0 (hard cutoff). **Cluster compactness dominates here; in Tumbleweed it doesn't.** Phase 2 moment: in Game 2 round 10, extending to row 0 (distance-4 from cluster core) added no support; Tumbleweed strategy (reaching for far sightline bonuses) would fail here.

2. **Othello disanalogy.** Othello requires flanking for scoring. In Phase 2 no stone ever flipped — you own what you place. The strategic tree is totally different: Othello punishes corner/edge mistakes and rewards flipping cascades. Here every placement monotonically adds value and no flips occur. **These games do not share any tactical moment.**

3. **Torus matters.** Phase 2 Games 1 and 3 both showed "antipodal" builds exploiting wrap — on a torus, two clusters offset by (4,4) are mutually invisible to each other. A square-board version would have asymmetric corners and wouldn't admit this translation-symmetric attack. Specifically: Game 1 round 1 P2 at (7,6) is distance-5 from P1's (3,3) on a square 8×8 but distance-4 on a torus — within-wrap that makes the game effectively smaller and more race-like.

4. **Simultaneous really does matter — just in the wrong way.** Phase 2 Game 3 showed P2 objectively outscoring P1 (43.88 vs 39.30) but losing on the same-tick crossing. No classical alternating game can produce this outcome. Whether this is "novel strategic texture" or "exploitable engine bug" is debatable, but the game-state space explored is materially different from any alternating analog.

5. **Collision mechanic.** Phase 2 showed that collision-denial exists but is symmetric tempo loss. In Go or Othello, there's no analog. In Diplomacy there is (bouncing), but Diplomacy's bouncing stems from support dynamics, not coincident placement. The collision mechanic here is genuinely simpler than any I've seen in a named abstract game — which cuts both ways for novelty (simpler = less to design, but also less derivative).

### Resolution — novelty score

Weighing the adversary's strong Tumbleweed/Othello case against (a) the real radial-Gaussian-on-torus scoring twist, (b) the simultaneous-turn axis (however flawed in current implementation), and (c) the collision primitive:

**Novelty: 4/10.** The game is close-to-but-not-identical-to Tumbleweed; the simultaneous mechanic is a real addition but its in-game contribution is mostly "tie-break bias." Strip the engine bug, and novelty drops to ~3. Include the bug and you have a game whose defining characteristic is a flaw, which isn't creativity.

---

## Phase 5 — Verdict

Team ID: `team-4`
Game ID: `1565501cfecf`
Rules Summary: Simultaneous placement on an 8×8 torus. Stones emit signed radial influence (radius 3, strength ≈0.97, decay ≈0.59). First player whose sum-of-owned-cell-values exceeds ≈38.63 wins; same-tick ties go to P1 by engine iteration order. No captures, no CA. Double-pass is a draw.
Topology: 8×8 torus (both axes wrap).
Turn Structure: simultaneous (`step_simultaneous`); collisions → both stones annihilate.

### SCORES (1–10)

- **Strategic Depth: 4/10.** Shallow tree: essentially one macro-strategy ("build the densest cluster and pace to cross first"). No captures, no movement, no CA, no life/death. The threshold and radius combine so that almost any tight cluster of 10–14 stones crosses — reaching the endgame is mechanical. Counter-play is limited to adjacent-attack (negative-sum) or collision-denial (symmetric tempo loss).

- **Emergent Complexity: 3/10.** Some emergent concepts (cluster density, influence pacing, collision denial) but none rise to Go-like richness. No ko, no seki, no sacrifice dynamics, no tempo lines that unfold over many moves. What emerges is a race between two monotonically-growing scores on a homogeneous surface.

- **Balance: 2/10.** P1 won 3/3 games in Phase 2, including two games where P2 ended with a higher raw score. The simultaneous threshold mechanic does not eliminate first-mover advantage — it concentrates it into an iteration-order tiebreak (`engine_v2.py:748-761`) that fires whenever both players cross on the same tick, which is common in symmetric or near-symmetric play. Seat-swap in Game 3 did not change the outcome. **R15's seat-balance metric should have caught this; that it didn't is evidence the metric is still under-calibrated for threshold-tie scenarios.**

- **Novelty (post-adversary): 4/10.** Closest analog is Tumbleweed (stones-with-spatial-value-metric, threshold-to-win). The Gaussian radial kernel + torus + simultaneous axis is genuinely a different combination, and no named abstract game matches all three. However, the simultaneous mechanic's primary effect in play is "P1 wins ties" — a flaw, not creativity — and stripping that reveals a game very close to weighted-territory Tumbleweed.

- **Replayability: 3/10.** With the iteration-order bias known, optimal play is "P1 matches P2's pace and wins ties." P2's counter (race a tick ahead) is hard on a symmetric torus. Known results converge to a small set of opening patterns (tight 3×3 cluster). 2–3 plays and the repertoire is exhausted.

- **Overall "Would I play this again?": 3/10.** Interesting to probe for ~30 minutes; no reason to revisit.

### CLOSEST KNOWN-GAME ANALOG

**Tumbleweed** (Mike Zapawa, 2020). Both are place-only games where a stone's "value" depends on its spatial relationship to friendly stones, and the winner is decided by a scalar aggregation of those values. Differences: Tumbleweed uses line-of-sight height (integer, anisotropic) on a hex board with alternating turns; this game uses radial Gaussian decay (real-valued, isotropic) on a torus with simultaneous turns. The strategic *concept* — "build clusters that mutually reinforce" — is shared.

### KILLER FLAWS

1. **Iteration-order tiebreak (the R15 pilot flag, confirmed in Phase 2 Games 1 and 3):** `_check_threshold` iterates `for player in (1, 2)`; whenever both players cross threshold on the same tick, P1 wins unconditionally. In Game 3, P2 led 43.88 vs 39.30 and still lost. Seat-swap did not help. This is an engineered-in first-mover advantage that negates the simultaneous mechanic's point.
2. **Homogeneous torus topology:** every cell is equivalent, which flattens strategic variety. Corner/edge theory is absent, so cluster placement decisions reduce to "distance from opponent" only.
3. **No subtraction primitive:** no captures and no CA means stones only accrete. There is no long-term tension, no sacrifice, no comeback mechanic. Whoever pulls ahead usually stays ahead.

### BEST QUALITY

**The signed radial influence field as a scoring primitive.** The Gaussian-kernel scoring is cleaner and more geometrically intuitive than line-of-sight (Tumbleweed) or flip-cascades (Othello). It produces a legible, inspectable influence-field map that makes strategic positions visually readable — "lean into the positive contours, avoid the negative contours." This mechanic is worth porting to a better-balanced game framework.

### IMPROVEMENT IDEAS

**Single most-impactful rule change:** resolve simultaneous threshold ties as a DRAW, not P1-wins. (Concretely: change `_check_threshold` so it accumulates every player who crosses this tick, and if more than one crosses, set winner=None.) This restores the symmetry that "simultaneous" promises, forces P2 to actually out-pace P1 (not just match), and turns every Phase 2 "P1 wins on bias" game into a draw — which is a much more honest signal to the GE metric that the game is actually balanced. A secondary fix would be adding a small amount of asymmetric noise (e.g. P2 places second so if both crossed this tick, the "later" placement counts), but that undermines simultaneity in a different way. The draw-on-tie fix is cleanest and preserves the design intent of the game.
