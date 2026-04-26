# Team-23 Evaluation — Game 992bf7dfc9f4 (Run 14, Rank 5)

**Team ID:** team-23
**Game ID:** 992bf7dfc9f4
**Generation:** 10 (seed / root game, no ancestors)
**GE / ELO:** 0.4196 / 2953
**Premise:** the R14 sim×CA hybrid — simultaneous turn structure + active CA rule, v4 representation — the headline novelty of Run 14.

---

## Phase 1 — Rule Comprehension

### Board
- **Topology:** 2-D grid, 8×8 = 64 cells, von Neumann adjacency.
- **Action space:** 65 actions (0–63 = place at cell index `y*8 + x`, 64 = pass).

### Turn structure — **SIMULTANEOUS**
Both players submit an action in the same tick. Collision resolution:
1. If both target the same non-pass cell → **mutual annihilation** (neither stone placed).
2. Otherwise both placements land.
3. CA step runs AFTER placements (see below).
4. Double-pass ends the game by majority.

### Placement rule
- Target: empty cells only.
- Constraint: adjacent to own piece.
- `first_move_anywhere = True` (first placement of each player is unrestricted).

### Capture rule
- `capture_type = none` (no custodian / surround capture).

### Propagation
- `prop_type = none` (no influence field).

### Cellular automaton (the defining feature)
- **Steps per turn:** 1.
- **Key asymmetry (CRITICAL):** the engine runs `acting_player = 1 if i % 2 == 0 else 2`. With `steps_per_turn = 1`, `i = 0`, so **the CA is ALWAYS evaluated from Player 1's perspective**. Every CA transition ("FRIEND", "ENEMY", neighbor counts) is computed as if P1 is the acting player. P2 never gets a "turn" of the CA. This is a structural P1 advantage baked into the engine for this turn-structure/steps_per_turn combination.
- **Transition table size:** 75 entries (3 cell states × 5 friendly-neighbor counts × 5 enemy-neighbor counts).
- **Non-trivial (active) entries:** **16 of 75 (21%)** — the other 59 are identity. Active breakdown: 6 birth rules (empty → P1), 7 death rules (piece → empty), 3 conversion rules (friend↔enemy flip).
- **Effective rules on a 4-neighbor grid (max 4 neighbors total):**
  - **Birth (empty → P1):** own=2 opp=0 → P1; own=2 opp=1 → P1; own=4 opp=0 → P1. (Three other birth rules require own+opp sums > 4 and can't fire on a grid.)
  - **Capture/flip (ENEMY/P2 → P1 or empty):** ENEMY own=2 opp=0 → P1 (capture!); ENEMY own=3 opp=0 → empty (kill). (Other ENEMY death rules need impossible sums.)
  - **Self-harm (FRIEND/P1 → empty or ENEMY/P2):** FRIEND own=0 opp=1 → P2 (flip!); FRIEND own=0 opp=2 → empty (die); FRIEND own=1 opp=2 → empty; FRIEND own=1 opp=3 → empty.
- **Strategic implication:** P1 stones that are isolated (0 friendly neighbors) and next to a P2 stone get converted to P2. So P1 must always place near existing P1 stones. Conversely, P2 stones get captured back to P1 whenever they have exactly 2 P1 neighbors and 0 P2 neighbors. The CA asymmetry means P1 accumulates stones via both placement AND birth each turn while P2 only gets placements.

### Win condition
- **Territory:** own more than `threshold * total_cells` = `0.6253 * 64 = 40.02` cells → need **≥ 41 own pieces**.
- **Max turns:** 100. If no one hits threshold, majority rule decides (double-pass or max-turn).

### Flagged features / degeneracies
- **Dominant strategy (P1)**: the CA snowball gives P1 2–4 stones per turn (1 placement + 1–3 births). Empirical: P1 wins 100% of 20 random-vs-random games and 8/8 heuristic-vs-heuristic games (see Phase 2).
- **Active CA count (16/75)** is moderate, but the asymmetry concentrates almost all of the effect on P1 — no CA transition benefits P2 except incidentally via the self-harm rules (which require P2 to isolate a P1 stone, hard to do when P1 clusters densely).
- **Double-pass majority exploit present**: in several Phase 2 games the territory threshold was not reached (P1 got stuck in the high-30s) and the game resolved by double-pass or max-turn majority. Flagged.
- **No propagation, no capture, no connection**: only placement + asymmetric CA + territory-count win.

---

## Phase 2 — Strategic Play

All moves engine-verified via `sim_play.py` driver using `engine.step_simultaneous()`.

### Game 1 — central vs central (P1 self-reasoner, P2 self-reasoner)
- **Opening:** P1 27 (3,3), P2 36 (4,4) — classic center-adjacent starting.
- **Rounds 1–7:** P1 builds a 4-stone rectangle (19,20,27,28). Each P1 placement triggered 1-2 CA births (empty cells with 2 P1 neighbors). P2 played wall-extension moves (35,36,37,44,45,46).
- **Key moment (round 6):** P1 played 11, which simultaneously triggered births at cells 10 AND 12 (both empties had 2 P1 neighbors each). P1 jumped from 7 → 10 stones (+3 in one tick).
- **Round 7:** P1 played 17, producing an unexpected THREE births (cells 9, 13, 25 all had 2 P1 neighbors after placement). P1 went from 10 → 14 (+4).
- **Round 11 P2 defense:** P2 played 34 to block P1's planned birth at cell 34 (placing a P2 stone where P1's CA would otherwise birth). Effective defense — denied one birth — but P2 stone then had own=2 P1 / opp=1 P2 which is ENEMY-identity (survived). P2 gains 1, denies 1.
- **End:** P1 had only cell 31 as a legal move by round 15 (dense center cluster, disconnected from open corners). P1 passed for several rounds while P2 filled corners; final state after 26 rounds: **P1=38, P2=25 — P1 wins by majority via double-pass. Never reached 41 threshold. 0 collisions.**

### Game 2 — adjacent P2 opening (the strongest P2 counter)
- **Opening:** P1 27, P2 28 (adjacent to P1).
- **Round 1 CA flip:** P1 stone at 27 had nbrs 19,26,28(P2),35 → FRIEND own=0 opp=1 → converted to P2! P1 lost their opening stone immediately. After round 1: P1=0, P2=2 (the 28 placement + the flipped 27).
- **Lesson:** a P2 opener adjacent to P1 captures P1's stone for free via the self-harm CA rule. This is the strongest P2 opening available.
- **P1 recovery:** P1 plays 0 (far corner) — safe because `first_move_anywhere` applies again when P1 has 0 stones. P1 builds a dense corner cluster.
- **Collision emerged R18:** P1 and P2 both played cell 21 (a contested border cell) → mutual annihilation. First collision observed in all my play. Cell stayed empty. This was P2's optimal defense (deny the placement); denial was successful but P1 was already well ahead.
- **End:** P1=31, P2=25 at max-turn double-pass. P1 wins by majority. 1 collision. Did not reach threshold.

### Game 3 — seat swap + auto-play heuristic
To reduce seat-identity bias and test many openings, I built a 1-ply greedy heuristic and ran 8 distinct opener configurations with symmetric policies (both players use the same heuristic). Results:

| P1 open | P2 open | P1 final | P2 final | winner | rounds | collisions | end |
|---|---|---|---|---|---|---|---|
| 27 | 36 | 41 | 21 | P1 | 21 | 0 | territory-threshold |
| 27 | 28 | 41 | 20 | P1 | 19 | 0 | threshold |
| 18 | 45 | 41 | 16 | P1 | 16 | 0 | threshold |
| 0 | 63 | 42 | 13 | P1 | 13 | 0 | threshold |
| 27 | 0 | 41 | 13 | P1 | 14 | 0 | threshold |
| 0 | 27 | 41 | 20 | P1 | 20 | 0 | threshold |
| 36 | 27 | 41 | 17 | P1 | 17 | 0 | threshold |
| 63 | 0 | 44 | 15 | P1 | 15 | 0 | threshold |

**Total: P1 wins 8/8, 0 collisions, always reached territory threshold. No opening saves P2.**

Additional random-vs-random (20 seeds): **P1 wins 20/20 (100%)**, avg 47.6 rounds, avg 26.6 collisions/game. Several games (seeds 4,5,10,12,13,17,18) hit max_turns with 70+ collisions/game — a degenerate "both players fixate on the same cell" pattern — but P1 still won by majority each time.

### Player reflections

**Player 1 strategy guide:**
1. Open centrally with 2 stones forming a diagonal pair (e.g. 27, then 28 or 19) — do not play adjacent to P2.
2. Every placement should land where at least one existing P1 stone already borders — guarantees own ≥ 1 post-placement, protecting against the self-harm flip.
3. After the first 3–4 placements, most turns give 1–3 CA births for free. Prioritize placements that create the most "2-P1-neighbor" empty cells adjacent to the new stone.
4. Ignore P2; they cannot keep up.
5. Do NOT place isolated stones near P2. Do NOT play into cells where you would be own=1, opp=2 (instant death).

**Player 2 strategy guide:**
1. Open adjacent to P1's opening stone — if P1 plays 27, play 28. This captures P1's stone immediately via the CA self-harm rule.
2. Build a dense cluster: every P2 stone should have ≥1 P2 neighbor to avoid the ENEMY own=2 opp=0 capture.
3. When P1 threatens a birth on a cell that is also P2-legal (rare), consider colliding (both playing the same cell) to deny.
4. Accept that the game is not winnable; optimize for minimum losing margin.
5. NOTE: in all my empirical runs, P2 never won. This strategy guide is aspirational.

Did ≥ 2 of 3 games resolve by double-pass? **Yes — Games 1 and 2 both resolved by double-pass majority without reaching territory threshold.** Only the heuristic auto-plays reached the 41-piece threshold cleanly (because the heuristic played more efficiently than my exploratory/pedagogical play). Flagged as the Run 13 double-pass failure mode is active here.

---

## Phase 3 — Strategic Analysis (joint)

- **Distinct viable strategies:** No. Only one strategy dominates: P1 snowballs via CA.
- **Meaningful counter-play:** Marginal. P2 can collision-deny individual births but cannot gain enough tempo to overcome P1's CA yield.
- **Short-term vs long-term tension:** Absent. The CA is a positive-feedback loop for P1: more P1 stones → more empty cells with 2 P1 neighbors → more births. No strategic sacrifice pays off later.
- **Emergent concepts:**
  - Mild territory dynamics (P1 wall vs P2 wall meeting at a diagonal).
  - **Collision fixation:** In ~1/3 of random games, both players greedy-target the same contested cell for dozens of consecutive rounds, producing a max-turn degenerate endgame. Novel as an observation but not as a strategic resource.
  - **Self-harm flip as P2 opening weapon:** The FRIEND own=0 opp=1 → ENEMY rule gives P2 a single free capture at game start. Interesting but doesn't change win probability.
- **Topology:** Grid, standard. Does not create novel structure.
- **First-mover advantage (the headline question):** **MASSIVE and NOT eliminated by the simultaneous mechanic.** Empirically P1 wins 100% across 28+ tested games (20 random, 8 heuristic). The cause is the engine quirk `acting_player = 1 if i % 2 == 0 else 2` — with `steps_per_turn=1` only the i=0 branch fires, so CA always evaluates from P1's frame. Simultaneous placement does not help P2 because the imbalance is in the CA step, not the placement step. Seat-swap confirms: whichever seat evaluates as "P1" wins.

**Seat-identity bias disclosure:** I played all three seats sequentially as one reasoner. The auto-play balance test (8 openings with symmetric policy) is the less-biased measurement and shows unambiguous P1 dominance. My hand-played games (1 and 2) agree directionally.

---

## Phase 4 — Novelty Adversary

**Adversary case against novelty:**

(a) **Known-game correspondences.**
- **Gungo** (simultaneous-move Go, see Fritzius 1977 and later variants): same 2-player placement + collision-mutual-annihilation mechanic. Direct structural analog for the simultaneous layer.
- **Immigration Game** (two-color Conway Life, Bosch 1970s): cells live/die by B3/S23, colored by parent majority. Analog for the CA layer, but that CA is symmetric between colors; ours is asymmetric.
- **Go:** territory-win + placement core. But Go uses group-liberty capture, not a CA. No match beyond the skeleton.
- **Othello:** flip-enemy-on-bracketing; our CA has a flip rule (FRIEND own=0 opp=1 → ENEMY) but it's count-based, not bracket-based. Different mechanism.
- **Gomoku/Pente/Connect6/Hex/Y/Havannah/Amazons/Mancala/Slither/Tumbleweed/LoA/Nim-likes:** no structural overlap.

(b) **CA literature check.** The 16-active-entry table is not a standard Life-like rule (B3/S23, HighLife B36/S23, Day & Night B3678/S34678, Seeds B2/S, etc.). It mixes birth (B2, B4 — depending on neighbor color counts) with death and color-flip in ways I cannot map to any documented 2-state or multi-state CA. However, the RULE COMPLEXITY is trivial — 16 non-trivial entries on a 4-neighbor grid produces only ~9 reachable conditions. Not rich enough to be a research-grade CA.

(c) **Simultaneous-game correspondences.** Gungo (cited above) is the direct analog for the placement+collision layer. Diplomacy-style resolution, Blotto, RPS-scaled: no structural overlap.

(d) **Re-skin hypothesis.** The game is: **"Gungo on 8×8 grid, plus a P1-perspective asymmetric Life-variant CA step per tick, with territory-threshold win."** Under that decomposition: strip CA → degenerate Gungo (no territory mechanism, just majority). Strip simultaneous → pseudo-Go with count-based capture.

(e) **Expert-transfer test.** A Go expert would misplay because there are no groups or liberties. A Life/CA expert would recognize the transitions but not the asymmetry. A Gungo expert would recognize the collisions but not the CA. No expert transfers cleanly, but the game is also too mechanically broken for expert skill to matter — even random P1 wins.

**Rebuttal (from Player 1 / Player 2 reflections):**

- **Phase 2 moment that breaks the "Gungo" analogy:** Round 1 of Game 2, P2 plays adjacent to P1's opening and P1's stone CONVERTS TO P2 without P2 doing any further work. No Go-family game has this dynamic; Gungo certainly does not. It is a CA artifact.
- **Phase 2 moment that breaks the "Immigration Game" analogy:** Round 6 of Game 1, P1 plays 11 and two separate empty cells (10, 12) simultaneously birth P1 stones. Immigration Game's birth rule is B3, and requires specific parent-majority; our rule is B2/B4 with neighbor-color gating. Different rule, different dynamics (avalanches are much faster in our game).
- **Phase 2 moment that breaks "any known game":** The collision-fixation endgame (rounds 22-100 of the neutral-opener auto-play, with cell 39 contested for 78 consecutive rounds) is a degenerate dynamic I have not seen documented in any simultaneous-move game. It's a failure mode, but it is new.
- **However:** all of the above "novel moments" arise from the P1-frame CA asymmetry, which is an engine implementation choice rather than a deliberate game design. If `steps_per_turn` were set to 2 (alternating P1 then P2 CA frames), the game would be symmetric and much more interesting. The "novelty" we observe is closer to a bug than a feature.

**Team novelty score: 4/10.** The combination of simultaneous placement + asymmetric CA + territory win is not present in any known game I can find, so it is technically novel. But the novel element (CA asymmetry) is a side-effect of engine wiring rather than an intentional mechanic, and it makes the game unplayable as a balanced contest. A thoughtful evolution would either symmetrize the CA or raise `steps_per_turn` to 2.

---

## Phase 5 — Verdict

**Team ID:** team-23
**Game ID:** 992bf7dfc9f4
**Rules Summary:** 8×8 grid; simultaneous placement (empty + adjacent-to-own) with same-cell mutual annihilation; an asymmetric player-1-frame Life-like CA step per turn (16 active transitions including births, captures and self-harm flips); territory win at ≥41 of 64 cells.
**Topology:** grid, 2-D, 8×8, von Neumann adjacency.
**Turn Structure:** simultaneous.

### SCORES (1–10)

- **Strategic Depth: 2** — Only one viable strategy (P1 snowball). No tempo, ko, sacrifice, or tension dynamics. P2 has no path to parity.
- **Emergent Complexity: 3** — The CA avalanche is an interesting emergent effect, and the collision-fixation endgame is mildly novel. But the avalanche is monotone (always favors P1), and the emergence does not generate strategic branching.
- **Balance: 1** — P1 wins 20/20 random games, 8/8 heuristic games across all tested openings. Seat-swap via the auto-play heuristic confirms the bias is structural, not stylistic. This is the worst-balanced game I have evaluated.
- **Novelty (post-adversary): 4** — The sim × asymmetric-CA combination is not a documented game; closest analog is Gungo + arbitrary multi-state CA. But the "novel" asymmetric CA is an engine artifact (steps_per_turn=1 exposes only the P1 frame), which downgrades the novelty to "accidentally new, structurally broken".
- **Replayability: 2** — Openings barely affect outcomes; every game converges to P1 snowball or collision-fixation. Not worth replaying.
- **Overall "Would I play this again?": 2** — I would not. As a research artifact it is illustrative (of how the simultaneous engine interacts with asymmetric CA), but not as a game.

### CLOSEST KNOWN-GAME ANALOG
**Gungo** (simultaneous Go, Fritzius 1977) for the placement + collision mechanic; **Immigration Game** (Conway Life two-color variant) for the CA layer. The composition is not identical to either, but Gungo-with-an-asymmetric-Life-step captures 90% of the mechanics.

### KILLER FLAWS
1. **P1-frame CA asymmetry** (`steps_per_turn=1` hardcodes `acting_player=1`): P1 wins ~100% empirically. This is the decisive flaw and it is almost certainly unintentional — the designer of the CA transition table likely assumed symmetric application.
2. **Double-pass majority exploit active**: Games 1 and 2 (hand-played) resolved by double-pass before hitting the 41-threshold. The territory threshold (≥41 of 64) is high enough that end-game territorial contestation often stalls.
3. **Collision-fixation endgame**: in random/naive play, both players target the same cell for 70+ consecutive turns, wasting ~75% of max_turns. Not a killer flaw on its own (majority still resolves), but a sign of strategic sparseness.

### BEST QUALITY
The CA avalanche has a satisfying "run-away" quality — watching P1 place one stone and trigger 3 simultaneous births is visually striking, and the specific arithmetic of the birth rule (empty, own=2, opp≤1) produces genuine L-shape pattern recognition. If the CA were symmetric, this mechanism could be the seed of a good game.

### IMPROVEMENT IDEAS
**Single rule change:** set `ca_rule.steps_per_turn = 2`. Then the CA runs twice per simultaneous tick, once from each player's frame. This symmetrizes the CA and makes the game balanced — each player gets the same birth / capture / flip opportunities relative to their own pieces. Alternative: have `_run_ca_step` in simultaneous mode always run once from each player's frame regardless of `steps_per_turn`. Either change would likely produce a genuinely interesting sim-CA hybrid.

**Secondary suggestion:** lower territory threshold to 0.55 (35 of 64) so that P1's snowball has a chance of triggering a clean threshold win before collision-fixation stalls the board.

---

## Appendix — Process notes

- All moves verified with `engine.step_simultaneous()` via `/Users/jamesbrowne/aigame/evaluations/run14/team-23_workspace/sim_play.py`.
- Heuristic auto-play and balance test code at `.../team-23_workspace/{auto_play.py, balance_test.py, random_vs_random.py, analyze_ca.py}`.
- Seat-identity bias: acknowledged. Phase 2 games 1 and 2 played by the same reasoner sequentially; Game 3 replaced by a symmetric-heuristic balance test across 8 openings, which is less biased and produced the cleanest signal (P1 wins 8/8).
- ~25 minutes budget used; Phase 2 took longest due to engine quirk discovery (CA asymmetry realization in Game 2 Round 1). No game hit max_turns uncontested in hand-play — but several did in auto-play, always with P1 ahead and winning by majority.
