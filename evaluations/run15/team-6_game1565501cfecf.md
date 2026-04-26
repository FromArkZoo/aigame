# Team-6 evaluation — Game 1565501cfecf (R15 champion)

Team ID: team-6
Game ID: 1565501cfecf
Generation: 9
GE Score: 0.318 (Go-essence)
Evaluated: 2026-04-22

This evaluation was performed independently by team-6. I was aware a pilot evaluation exists but did not cross-reference conclusions until after forming my own. My findings converge with the pilot on the key structural observations (check-order bias, dominant antipodal-cluster strategy) and add an extra test: whether P2 can force a one-round-faster win by exploiting P1 sub-optimal shape (answer: yes, but only if P1 deviates from the canonical 3x3).

---

## Phase 1 — Rule comprehension

**Board.** 8x8 torus (64 cells), two-dimensional. Every cell is topologically equivalent; all "corners" and "edges" are wrap-equivalent.

**Turn structure.** `simultaneous`, `pieces_per_turn=1`. Each round both players submit one action through `engine.step_simultaneous(a1, a2)`. Collision rule: if both target the same non-pass cell, **both placements are cancelled — mutual annihilation**. Verified in probe (`rounds "27:27"` → both pieces gone, owners all empty). Single pass does nothing; two passes in the same round → immediate draw. Verified with `rounds "27:63, pass:pass"` → game ends with P1=P2=1 stone, winner=None, step_count=2.

**Actions.** Place-only. 65 action IDs: 0..63 = board cell `y*8 + x`, action 64 = pass. Placement target must be empty; constraint is `anywhere`; `first_move_anywhere=true` (no opening restriction). No movement and no removal once placed (stones are permanent except for annihilation at placement).

**Capture.** `capture_type=none`. No capture mechanic is active. This means the board-state over pieces is strictly monotonic — piece counts only rise or stay equal (equal only on mutual annihilation).

**Propagation.** `influence`, radius=3, strength=0.9657, decay=0.5867. When a stone is placed, signed value (positive for P1, negative for P2) is added to every cell within Manhattan distance <= 3 on the torus. Contribution at distance d is approximately `strength * decay^d`:
  - d=0: +0.966 (own cell)
  - d=1: +0.567
  - d=2: +0.333
  - d=3: +0.195
  Footprint per stone = 1 + 4 + 8 + 12 = 25 cells. Torus wrap means influence loops around edges. Note `board_values` is additive — values from multiple stones stack; opposing stones cancel. A 3x3 cluster sees each own-cell inflated to +3.86 (corner of cluster) to +4.56 (center) from the sum of the 9 nearby friends.

**Win condition.** `threshold`, threshold=38.627, `target_dimension=0`. Win when `sum(board_values[c] for c owned by player)` (sign-corrected for P2) > 38.627. `max_turns=100`. Per R15 rule change, **double-pass ends as DRAW**; max-turns-without-winner also counts back to piece-majority (but no game I played reached max-turns).

**CA.** None. This is a classical game.

**Degeneracy flags / observations:**
- **Threshold-check iteration bias (confirmed): `engine_v2.py:_check_threshold` lines 748-761 loops `for player in (1, 2)`. If both players cross on the same simultaneous tick, P1 wins by iteration order. This is the single biggest quality signal for this game.**
- Per-stone contribution to own-cell value is capped near 1.0 (zero-enemy case). Threshold = 38.63 is thus roughly equivalent to "~39 own-cell-equivalents of influence mass on your stones", i.e. ~12 stones isolated or ~10 stones in a 3x3 + extension. Reached in 10 rounds experimentally. No way to reach threshold in <=9 rounds — I checked a 3x3 cluster at 9 stones tops out at 34.713.
- Monotone state + no capture/movement + simultaneous threshold + no interaction at antipode = extreme dominant strategy: **"play tightest possible cluster as far from the opponent as possible"**. The torus is conveniently sized so that P1's 3x3 at (2..4, 2..4) and P2's 3x3 at (6..0, 6..0) (wrapping) have centres at Manhattan distance 4 on torus and do not overlap within r=3.
- Action 64 = pass. Two passes → draw. I verified this (game ends in 1 step, winner=None).
- No CA transition table exists here, so the R15 "CA symmetric under player swap" claim is vacuous for this game.

## Phase 2 — Strategic play

**Methodology.** I used `sim_play_helper.py` which calls `engine.step_simultaneous` properly. Every move was submitted as a `p1:p2` pair and engine-verified. I played all three games sequentially (same agent in both seats) and acknowledge the seat-identity bias in the analysis. I read moves against the visible `--show-values` field.

### Game 1 — Symmetric antipodal 3x3 (baseline)

Goal: confirm threshold-check tie-break behavior.

Moves (`p1:p2`):
`27:63, 19:55, 26:62, 28:56, 35:7, 18:54, 20:0, 34:48, 36:6, 43:61`

P1 builds 3x3 centered at (3,3) [cells (2,2) through (4,4)]. P2 builds 3x3 at torus antipode (6,6)-(0,0) (wraps). Both mirror exactly.

- R1..R8: same-shape construction; both own_sum rises symmetrically.
- R9: both complete the 3x3. own_sum = **34.713 each**. Neither has crossed threshold.
- R10: both extend by one peripheral cell (P1 plays (3,5)=43 south-extension; P2 plays (5,7)=61 which is its mirror). own_sum = **39.976 each**, exceeding 38.627.

Both cross on the same tick → **P1 wins** by check-order. Resolution: stated win condition. Zero collisions (play is anti-coordinated by construction).

### Game 2 — P2 plays non-antipodal (corner-on-corner contest)

Goal: test whether cluster conflict creates real strategic dynamics.

Moves:
`27:0, 19:1, 26:8, 28:9, 35:2, 18:16, 20:17, 34:10, 36:24, 37:3, 29:11, 44:25`

P1 builds 3x3 at (2..4, 2..4). P2 builds 3x3 at (0..2, 0..2), which overlaps P1's radius-3 field heavily — the (2,2) P1 cell and (2,2) P2 cell would collide; the clusters touch diagonally at the (2,2)/(2,2) interface.

- R9: P1=27.607, P2=25.809. Both below Game-1 level (34.7) because of mutual cancellation in the contact zone.
- R10-R12: both players extend their clusters AWAY from the contact zone (P1 extends south/east, P2 extends north/west). P1's extension moves (37, 29, 44 = (5,4), (5,3), (4,5)) pushed into free space; P2's extensions (3, 11, 25 = (3,0), (3,1), (1,3)) tried to mirror, but P1's southern extensions had cleaner free space.
- R12: P1=38.844 (crosses), P2=36.070. **P1 wins**.

Observations:
- The ~2.8-point gap at R12 is asymmetric in P1's favor even though both played the same mirror logic. Cause: every extension move P2 tries near (2,2) is *closer* to P1's cluster (at (3,3)) than P1's extensions are to P2's cluster (at (1,1)). The geometry is subtly biased because both clusters are in the same quadrant; the contact zone is between them. P1 naturally extends into the larger open region. In perfectly-antipodal play this asymmetry vanishes, so Game 2 is an example of "P2 chose a worse shape", not an inherent geometric bias.
- No collisions occurred.
- Resolution: stated win condition.

### Game 3 — Seat-swap: team-6 now plays P2

Following prompt instruction, I swap seat identity. In games 1-2 I played P1 (or drove both from a P1 perspective); in game 3 I drive P2's play and try to *find a winning line for P2*.

I try two ideas here:

**(a) Can P2 reach threshold in fewer rounds than P1?** No — the first threshold-crossable shape is a 3x3 + 1 peripheral (~39.976 own_sum), and both players need 10 rounds to build it. Since they play simultaneously, both arrive at R10. So the earliest anyone can win is R10, and on that tick P1 wins the check-order.

**(b) Can P2 exploit a sub-optimal P1 shape?** If P1 plays a non-compact 3x3 (e.g. L-shape that leaves one cell empty), P1's R9 own_sum is lower than 34.713; P2 keeping optimal 3x3 reaches 34.713. Then at R10, P2 could cross with a good extension before P1 can.

Test the idea: have P1 play a "distracted" 3x3 missing cell (4,4)=36 and substitute (3,5)=43 early. P2 plays clean antipodal 3x3.

Moves (team-6 = P2):
`27:63, 19:55, 26:62, 28:56, 35:7, 18:54, 20:0, 34:48, 43:6, 21:61`

- R1-R8 mirror. R9: P1 plays (3,5)=43 instead of (4,4)=36. Now P1 has a cross-shape with the (4,4) hole → P1 own_sum = 33.305 vs P2 own_sum = 34.713. P2 is 1.4 ahead.
- R10: P1 tries to recover with (5,2)=21 (east extension). P2 plays (5,7)=61 (standard mirror extension).
  - P1 own_sum = 37.123 (crosses 38.63? no, just under)
  - P2 own_sum = **39.586** (crosses 38.63)
  - **P2 wins** (only P2 crossed; no tie-break needed).

This is a real seat-swap victory: if P1 makes a meaningful shape error *before* R9, P2 has a clean win. But vs optimal-3x3 P1, P2 still cannot win — Game 1 shows that.

Post-swap reflection: the seat-swap result is "P2 can win iff P1 blunders, else P2 must lose by tie-break". So the seat-swap evidence is **mixed with a strong P1 bias**: in any symmetric play, P1 wins; P2's wins require P1 error.

### Double-pass draw check

I did not encounter a double-pass in natural play because threshold is always reachable by round 10 under normal strategy. But I verified the mechanic separately: `rounds "27:63,pass:pass"` → step_count=2, winner=None, rewards (0, 0). Zero of 3 natural games ended in double-pass.

### Player strategy guides

**P1 strategy (for a competent opponent):**
1. Place stones to form a compact 3x3 block. Any 3x3 position is equivalent by torus symmetry — but choose coordinates such that your opponent, if they mirror, lands at antipode (for 8x8, anchor at (2..4, 2..4)).
2. Don't play near the opponent's cluster — contact dilutes your field.
3. Order of moves within the cluster is irrelevant (influence is commutative and associative).
4. On R10, play any cell adjacent to your 3x3 edge. You'll cross 38.627 immediately.
5. If opponent doesn't play the antipodal mirror, you have more room — either extend more (won't matter; you'll still win at R10) or maintain your cluster and let them bleed themselves.

**P2 strategy (against competent P1):**
1. You cannot win against optimal P1. The threshold-check iterates P1 first; in any round where both cross, P1 wins.
2. Best practical plan: mirror P1 antipodally and pray for a blunder. If P1 deviates from the compact 3x3 before round 10, you can steal the win by crossing alone.
3. Do NOT play near P1. Every cell near P1 has large positive value, so placing there actively lowers your own_sum (you take ownership of a P1-dominant cell).
4. Collision threats (placing on P1's probable next cell) are not worth attempting — you lose a tempo you can't afford.
5. Passing is always a net negative (no progress toward threshold).

### Did 2+ games end in double-pass? No. All 3 games resolved by threshold.

## Phase 3 — Strategic analysis (joint)

- **Distinct viable strategies?** No. One dominant strategy — "compact 3x3 cluster, placed at torus antipode from opponent, extend on R10" — wins for P1 or ties for P2 in all balanced cases. Any deviation is strictly worse.
- **Meaningful counter-play?** Extremely limited. No capture, no movement, no CA ⇒ every placement is permanent; trailing player has no recovery. The *only* counter-tool is mutual-annihilation collision, which requires predicting P1's cell in simultaneous play — even if guessed right, it costs P2 as much as P1 (both lose a tempo). P2's best shot is P1-blunder exploitation (Game 3).
- **Short-term vs long-term tension?** Essentially none. Every stone monotonically increases own_sum; there is no sacrifice, no "spend now for advantage later". The closest thing is "play at interior of cluster (higher own-cell boost from friends) vs boundary (more new own-cells)" — but the math makes these nearly equivalent, so there's no real decision.
- **Emergent concepts?**
  - *Territorial clustering* (mild) — friendly-neighbor stacking creates cluster-interior gradient up to 4.56 at center.
  - *Antipode as Schelling point* — on torus, the antipode is uniquely a "safe" cluster location.
  - *Check-order as tempo* — the closest thing to initiative in this game; trivializes most symmetric play.
  - Collision deterrent — dormant in my games; could matter in AI-vs-AI play if both players chase the same Schelling cell.
- **Does topology matter?** Yes and no. Torus removes corners/edges and makes every cell equivalent. This is essential to the dominant strategy (antipodal 3x3 clusters only work because both clusters have full r=3 influence footprints, unlike edge cells on a non-wrapping grid). But within the torus, every game position is positionally equivalent under translation — so strategic richness comes only from *relative* cluster positioning, of which there are essentially 2 cases: antipodal (balanced) or sub-antipodal (P1 advantage grows).
- **First-mover advantage (simultaneous variant):**
  - Games 1-2: P1 wins both (one by check-order, one by cluster-contact asymmetry).
  - Game 3 (seat-swap): P2 wins because P1 played a deliberately-degraded shape. Vs. optimal P1, P2 cannot win.
  - **Quantification:** in 2 of 3 games P1 wins; in the 3rd, the only reason P2 wins is P1's intentionally sub-optimal play. Against equally-skilled play, **P1 wins 100% of symmetric games by structural tie-break.** The simultaneous mechanic did NOT eliminate first-mover advantage — it relocated it from move-order to win-check-order.

Seat-swap bias self-check: I played both seats with the same underlying agent; no model-vs-model difference. I acknowledge this limits the Game-3 "P2 insight" claim — an adversarial optimizer would never deliberately play sub-optimal P1 just to let P2 win. The robust take is: **with same-strength agents on both sides, P1 wins.**

## Phase 4 — Novelty adversary

### Adversary case (arguing the game is NOT novel)

**(a) Known game catalog:**
- **Go:** Nope — no capture, no liberties, no ko, no territory-by-enclosure. Only commonality is "stones on a grid".
- **Hex, Y, Havannah, Tumbleweed:** All connection-based or LOS-based. This game is neither.
- **Reversi/Othello:** Custodian flip is absent. No capture at all.
- **Gomoku/Pente/Connect6:** No line-forming condition.
- **Amazons:** Movement + shooting. Nope.
- **Lines of Action, Chameleon, Slither, Mancala variants:** No movement, no capture, no resource bank here.
- **Tumbleweed:** Closest territorial analog by the "each stone projects onto cells, score = sum of stones under your control weighted by influence" framing. Differences: Tumbleweed uses line-of-sight stacking on hex; this game uses exponential-decay radius on torus. Conceptually parallel, mechanically different.
- **Blotto / Colonel Blotto:** Strongest abstract-game analog for the *simultaneous-allocation* dimension. This game is Blotto-like in that per round both players allocate a "unit" to a "theater" (cell) simultaneously; same-cell conflict → both lose. But Blotto has no board structure, no spatial coupling, and no accumulation — so the mapping is lossy.
- **Simultaneous Go / Gungo:** Matches turn structure exactly but has Go's capture mechanic. This game has no capture.
- **Life-like CA (Life, HighLife, Day & Night):** Irrelevant — no CA step in this game. (The prompt asked me to check; I can confirm CA is vacuous here.)

**(b) CA literature:** Not applicable — no transition table.

**(c) Simultaneous games:**
- **Diplomacy:** Simultaneous order resolution is conceptually aligned, but Diplomacy's support/attack/standoff taxonomy is much richer. Here only "same-cell → annihilation" is modeled.
- **RPS-scale simultaneous games:** Partial fit for the collision sub-game — but that sub-game is embedded in a positional accumulation structure that pure RPS lacks.
- **Gungo (simultaneous Go):** Turn structure matches; mechanic differs (no capture here).

**(d) Re-skin claim.** Strongest: "**Spatial Blotto on torus with exponential-decay scoring and mutual-annihilation**." The transformation is: cells→theaters; radius-decay influence→theater coupling; threshold→victory-point cap. But the mapping loses:
- the board / wrap topology (no Blotto variant I know uses torus)
- the *cumulative* allocation (Blotto is one-shot)
- the continuous-valued field (Blotto theaters are won/lost binary)

So it's "Blotto-inspired" but not a re-skin.

**(e) Expert-transfer test.** A Tumbleweed expert would immediately grasp the "project + count" logic; a Blotto expert would grasp the "simultaneous allocation + collision". But neither would independently know to (i) cluster at antipode on a torus, (ii) avoid contact zones that cancel influence, (iii) leverage the threshold-check tie-break. The meta-strategy is simple enough that a smart newcomer will figure it out in 5-10 games, but no single existing game transfers completely.

### Rebuttal (from P1 and P2 acting jointly)

Specific moments where known-game analogies broke:

1. **Game 1 R1 (P1=27, P2=63):** both players placed at maximum torus distance with *zero* field interaction. In Tumbleweed, stones always interact because LOS is global; there is no torus-antipodal "safe placement". In Go, stones at antipode still compete for territory implicitly via end-game counting. In Blotto, there's no spatial structure so "antipode" doesn't mean anything. **None of these games have a position that's genuinely 'free of opponent'. This game does, on R1.** That's a genuine novelty of the torus-plus-radius-decay combination.

2. **Game 3 R10 P2 extension (5,7)=61:** P2 crossed threshold while P1 only reached 37.12. In any Go/Othello/Tumbleweed position, crossing a "scoring threshold" with a single placement requires a multi-stone combination effect; here it's a simple "add one stone, own_sum jumps by 5.26". That scalar-jump threshold crossing is not a normal abstract-game rhythm — it's more like racing games (first-past-the-post numerical), which none of the catalog games share.

3. **Negative-value "spoiler" squares:** in Games 2-3 I considered placing P2 stones on cells inside P1's field. These cells have large positive value (from P1's influence); placing a P2 stone there *reduces* P2's own_sum by (P1_influence_at_cell - P2's new projection onto cell) which is typically > 0 and hurts P2. This creates a region of the board that's *forbidden under self-interest*, which no catalog game reproduces. Blotto theaters don't have pre-existing value; Tumbleweed stones don't punish you for placing in strong-opponent areas; Go would *reward* you for entering opponent territory to invade.

4. **Mutual-annihilation collision as dormant deterrent:** in my 3 games, zero collisions occurred. The threat functions as a *Schelling-point deterrent*: any cell a rational P1 would play, rational P2 would also play → neither plays it (instead both retreat to antipode). Diplomacy and Gungo actively weaponize simultaneous moves; here they produce anti-coordination equilibrium. This is qualitatively different from the catalog.

### Novelty score

**Novelty score: 4/10.**
- Above 3 because the specific combination (torus × simultaneous × collision × exponential-decay influence × threshold) has no single named predecessor I can point to, and the "dormant collision as anti-coordination" dynamic plus "forbidden zone inside enemy field" are genuinely distinctive.
- Below 6 because the playable strategy compresses to a one-line prescription that transfers trivially from territorial intuition. Tumbleweed + Blotto spans 80% of the design space; the remainder is a narrow delta that a human learns in under 30 minutes.

## Phase 5 — Verdict

Team ID: team-6
Game ID: 1565501cfecf
Rules Summary: Simultaneous place-one-stone per round on an 8x8 torus; each stone radiates signed influence (radius=3, strength=0.966, decay=0.587); win by sum of board_values at your owned cells exceeding 38.627. Collisions (same cell) annihilate both stones. No capture, no CA. Threshold check iterates P1 before P2.
Topology: 8x8 torus, Von Neumann adjacency, 64 cells, fully wrapped.
Turn Structure: **simultaneous**.

### SCORES (1-10)

- **Strategic Depth: 3** — One dominant strategy ("compact 3x3 cluster at antipode, extend R10") resolves the game in 10 rounds. Spoiler plans for the trailing player don't work because of monotone state and the threshold-check bias. Decision tree has trivial width after you learn the shape.
- **Emergent Complexity: 3** — Radius-decay produces a genuinely continuous value gradient (visible when dumping `board_values`) which is prettier than pure discrete territorial games. But only one behavior emerges at strategic play (cluster + extend). No ko fights, no tempo battles, no trade-offs.
- **Balance: 2** — P1 wins 100% of symmetric-play games through the threshold-check iteration order. Seat-swap evidence: P1 wins Game 1, P1 wins Game 2, P2 only wins Game 3 because P1 was deliberately sub-optimal. Against same-strength play, P1 always wins. This is a structural flaw, not a play artifact.
- **Novelty (post-adversary): 4** — Strongest adversary claim: "Spatial Blotto on torus with decay-influence scoring". Rebuttal: antipode exists here as a *zero-interaction* placement (no Blotto analog); negative-value "self-punishing" cells exist (no Blotto/Tumbleweed analog); mutual-annihilation is dormant deterrent rather than active weapon (no Diplomacy/Gungo analog). Net: distinctive combination, shallow playable meta.
- **Replayability: 2** — Once the antipodal-3x3 script is known, games are 10 rounds with predetermined outcome. Torus symmetry eliminates even the "which 3x3 position" variation. Almost nothing to explore after ~5 games.
- **Overall "Would I play this again?": 2** — Not as a human abstract game. Possibly as an AI-training testbed for simultaneous-allocation mechanics, but the imbalance would produce a biased training signal.

### CLOSEST KNOWN-GAME ANALOG
**Spatial Colonel Blotto on a torus with exponential-decay scoring**, with Tumbleweed as the closest pure-territorial analog. Not identical to either: Blotto lacks spatial structure and accumulation; Tumbleweed uses LOS on hex and has no simultaneous mechanic. The combination is new, but the combination's emergent strategy space is a proper subset of both.

### KILLER FLAWS
1. **Structural P1 advantage via threshold-check iteration order** (`engine_v2.py:_check_threshold` loops player 1 before player 2; first crosser wins). In symmetric simultaneous play, P1 wins every tie. Confirmed in Game 1 (both own_sum=39.976 → P1 wins).
2. **No recovery mechanic for trailing player** — monotone state (no capture, no move, no CA) means the behind-by-any-margin player cannot catch up. The only tool is same-cell collision, which is symmetric in cost and cannot be forced in simultaneous play.
3. **Dominant strategy compresses game to 10-round script** with near-deterministic outcome for matched agents. Non-trivial branching factor from the trained-vs-random ELO gap (0.42-0.60) mostly reflects "random players don't find the 3x3 antipode" rather than meaningful strategic depth.
4. **Seat-balance metric apparently did not catch the check-order bias.** This champion has a clear P1 bias confirmable in <60 seconds of symmetric probing, yet scored highly enough to be named champion. Worth flagging as a metric-calibration issue.

### BEST QUALITY
The continuous radius-decay influence field plus torus topology generates genuinely novel *static* positions — the antipodal 3x3 cluster + one extension displays a 4.89-valued center tapering smoothly to -4.89 at the opposing center in a visually rich gradient. The mutual-annihilation collision rule, as a *dormant* Schelling-point deterrent rather than active weapon, is an unusual simultaneous-game dynamic worth studying. These two ingredients would be excellent in a *deeper* game that also provided recovery mechanics.

### IMPROVEMENT IDEAS
**Primary:** break the tie-break. Replace `_check_threshold`'s iteration-order winner with a post-round ordering rule — e.g. "winner = player whose most-recent placement produced the larger own_sum *increase*"; or declare a draw when both cross on the same round. This removes the structural P1 win on every symmetric game and would immediately expose whether any genuine P2 strategy exists.

**Secondary:** add a capture or conversion mechanic so the trailing player has a recovery option. For example, "at end of round, any cell owned by player X where effective value for X is now negative (enemy has projected over) is removed (becomes empty) or flipped". This restores contestability: enemy clustering can reclaim your stones, giving P2 a meaningful way to push back.

---

## Protocol notes

- `play_helper.py --action play` processes moves sequentially and misplays simultaneous games. I used `sim_play_helper.py` which wraps `step_simultaneous`. Every move submitted was engine-verified.
- All 3 games resolved by the stated threshold win condition; none by double-pass. Double-pass behavior verified separately.
- I was a single agent playing both seats sequentially. I acknowledge the seat-identity bias: a genuine P2 optimizer would not accept the blunder-exploitation path as a win. The robust conclusion is: **under matched play, P1 wins; P2 has no winning line.**
- Flag for aggregator: the GE-champion status of a game with an obvious check-order P1 bias is itself a calibration signal. The R15 seat-balance metric either did not probe symmetric-tie scenarios, or did but weighted other axes higher. Worth a follow-up.
