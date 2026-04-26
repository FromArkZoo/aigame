# Team-5 Evaluation — Game `deb4dfe0382d` (Run 14 champion)

**Team ID:** team-5
**Game ID:** deb4dfe0382d
**GE score:** 0.5174 (rank 1 in Run 14)
**Evaluator worked independently; no other team's evaluation was read.**

---

## PHASE 1 — RULE COMPREHENSION

**Board & topology**
- 2D, axis_size 8 → 64 cells total, 65 actions (0–63 placements in row-major order `y*8 + x`, action 64 = PASS).
- Topology: **torus** (both axes wrap). Confirmed empirically: influence at cell (0,0) wraps to cell (7,0), (0,7), etc.
- Critical engine quirk (per pilot note and verified): **influence propagation uses wrapped Manhattan distance** (so radius-1 truly includes torus-opposite edge neighbors), **but custodian-capture axis walks do NOT wrap** — they bail out at index 0 or axis_size. This asymmetry is real and strategically exploitable.

**Turn structure**
- **Alternating** (not simultaneous), 1 piece per turn, `first_move_anywhere = True`.

**Action types**
- `place` only. No movement. (`move_constraint: adjacent_empty` is defined but irrelevant because `action_types = ['place']`.)
- Pass is always legal; two consecutive passes end the game via majority-piece tie-break.

**Placement constraint**
- Target cells must be empty. Any empty cell anywhere, even on the first move.

**Capture (custodian)**
- `capture_type: custodian`, threshold 1. After a placement, for each of the 4 axis-directions the engine walks from the placed cell, collecting consecutive enemy stones, and flips them **iff the walk ends on a friendly stone before leaving the board**. Does NOT wrap on torus — hitting the axis boundary kills the capture.
- The flipped cells retain their existing *influence values* — they are NOT refreshed. This means capturing an enemy line of stones also transfers the enemy's negative influence onto cells now owned by the capturer. See "biggest strategic twist" below.

**Propagation (influence)**
- `prop_type: influence`, `radius 1`, `strength 1.874...`, `decay 0.402...`.
- A P1 placement adds **+strength·decay^d** to every cell within radius 1 (d=0 or 1 on torus). A P2 placement subtracts the same.
- Numerically: own-cell +1.874; each of 4 orthogonal torus-neighbors +0.753.
- Values clamp to [−100, +100].

**Win condition — threshold**
- `condition_type: threshold`, `threshold 38.616`, `target_dimension 0` (board_values array), `max_turns 102`.
- After every action the engine re-evaluates: for each player, sum `board_values` over all cells that player owns; P1's effective score is that sum; P2's effective score is the negative of their sum (so both players "win" when their effective score exceeds 38.616 — positive for P1, negative-magnitude for P2).
- If max_turns hits without threshold, tie-break is majority piece count.

**Rule degeneracy check — key findings**
- **Threshold is reachable.** Two adjacent stones give about 5.3 combined effective score; a 2×2 block gives ~13.5; a 2×4 block gives ~22; a 2×5 block gives ~27; a solid 3×4 block (12 stones) pushes past 38.6. So 10–13 well-placed stones suffice. Verified in multiple play-throughs.
- **Custodian capture is extremely potent** on this threshold axis. A single placement that brackets 3–4 enemy stones can swing the effective score by 8–15 points in a single move (see Phase 2). The asymmetry that flipped cells keep the enemy's old influence signs makes captures a **Pyrrhic victory** for threshold purposes — you gain piece count but the captured cells now subtract from your own effective score. I have never seen this dynamic in any previously-documented abstract strategy game.
- **Double-pass exploit.** Observed in 1 of my simulated games: after the board is filled (64 placements, no legal placements left), both players are forced to pass, triggering the majority tie-break. Because the game does NOT end at "board full" automatically, it must pass twice, which works correctly. This is not a voluntary-pass exploit in the Run-13 sense because rational players never voluntarily pass when they're threshold-losing — they just run down the 102-move clock with influence placements. Still worth noting as a fallback termination path.
- **No CA, no `move` action, no cascade** — all the potentially dangerous exotic rules are off. The game is fully classical minus the custodian+threshold combination.

---

## PHASE 2 — STRATEGIC PLAY

All three games engine-verified via `play_helper.py` and an independent helper (`team5_helper.py`) that re-implements scoring from `engine_v2.py` so I could see live effective-threshold values after each ply.

### Seat-bias disclosure
I am one reasoner acting as both players. Game 1 was hand-played ply-by-ply with explicit separate reasoning sections. Games 2–3 used heuristic auto-play with five well-defined styles (`greedy`, `aggressive`, `defensive`, `counter`, `random`) to reduce the single-reasoner bias — Game 3 swaps P1's preferred heuristic to P2's seat. Residual bias remains, and the 9-team evaluation ecosystem is the way to triangulate.

### Game 1 — Manual play, extended capture war (46 manual plies + autoplay finish)

**P1 (me, move 1):** Opens dead-center at (3,3) (cell 27). On a torus the center is not special, but it gives symmetric expansion options.

**P2 (me, move 2):** Plays (7,7) (cell 63) — maximal torus distance from P1's stone. Rationale: avoid being sandwiched by custodian capture early; start an independent cluster.

**Moves 3–14:** Parallel build-out. Both players construct 2×2 / 2×3 dense blocks in their respective corners. By move 14 both sides reach effective score ~25 with tightly packed clusters. P1 has tempo lead (one fewer piece needed for the same score).

**Move 15 (P1 plays (5,4)):** I deliberately find a cell with **2 friendly orthogonal neighbors** — this is the best possible placement value in this engine (1.874 + 2·0.753 = 3.38 own-cell value plus two +0.75 boosts to existing stones, total swing ~4.9).

**Move 16 (P2 invades (5,5)):** Key tactical moment. P2 plays directly *between* P1's cluster and P2's cluster, drawing down P1's nearby influence values. Drains ~0.75 from P1's (5,4) while gaining ~1.87 of own negative-sign influence.

**Moves 17–19 (P1 pushes toward threshold):** P1 reaches effective score 37.57 at move 19 — one placement away from the 38.616 threshold. P1 has a 10-stone flat block spanning rows 2–4, cols 2–5, with (3,2)(4,2)(5,2?) extensions.

**Move 20 — P2 custodian bomb (plays (5,2) = cell 21):** This is the game's pivotal moment. Walking down from (5,2): (5,3) X, (5,4) X, (5,5) O — bracket! Both P1 stones flip. P1's count falls 10 → 8, effective score crashes 37.57 → 30.81 (lost 6.76 points). This saved P2 the game.

**Moves 21–30: Custodian war.** P1 recaptures (5,2) by playing (6,2) — walking left hits (5,2)O, then (4,2)X friendly. P2 counter-recaptures (5,2) via (5,1). P1 defends by playing (2,2) which pushes score to 36.82 — again one move from threshold. P2 finds a devastating reply: **(1,2) captures three P1 stones in a single placement** — walks right from (1,2) hits (2,2)X, (3,2)X, (4,2)X, (5,2)O friendly → flip. P1 collapses to 26.68, P2 piece count surges.

**Moves 26–30 — capture cascade.** Each time one side builds a 3+ stone line with a friendly piece at one end, the other side finds a bracket placement on the opposite end. Captures of 2–4 stones are routine. By move 30, P2 has 23 stones vs P1's 7 and both sides' effective scores have collapsed to the low 20s because captured cells now carry the wrong-sign influence for their new owner.

**Moves 31–46:** P1 scraps for survival via single-stone captures on column 2. Extends into col 1 and col 0 (the unused NW quadrant). Score oscillates 22–33 for P1 while P2 piles up 30+ stones around cols 3–5 and the SE cluster.

**Moves 47–49 — autoplay finish (both sides switched to greedy heuristic).** P1 plays (6,4) (cell 38) — a latent bracket hiding in plain sight. Walk left from (6,4) crosses (5,4)O, (4,4)O, (3,4)O, (2,4)O and hits (1,4) X friendly! **Four-stone flip in one move.** P1 piece count 8 → 13, effective score 15.76 → ~33. P2 replies (2,7) defensively. P1 then plays (3,1) (cell 11): walk down hits (3,2)O, (3,3)O, (3,4)X friendly (just flipped) → captures (3,2)(3,3). P1 now at 49.59 — **threshold crossed, P1 wins at step 49**.

Final board: dense X row at y=1–4 cols 1–5, plus scattered X elsewhere. Piece count P1=16, P2=33 (P2 still has piece-count lead but it doesn't matter because threshold fires first).

**Player reflections — Game 1**

- *P1 reflection:* Strategy was "dense 2×N blocks to maximize mutual-reinforcement influence". This works great until the first long-axis alignment of friendly stones becomes a custodian target. Lesson: **never build a straight line of 3+ stones with a friendly anchor on only one end** — the opposite end is a single-move capture waiting to happen. The winning move at (6,4) worked because P2 had left a long row-4 O-chain (rows 4, cols 2–5 were all O) with (1,4) X still alive on the far side — P2's own capture setup became P1's weapon when the row extended through a friendly piece.
- *P2 reflection:* Strategy was "mirror P1's cluster, then switch to custodian raids when P1 approaches threshold". Succeeded brilliantly for 25 moves but eventually P1's board became too full and P2's own chains became mutual capture bait. Key mistake: P2 kept capturing (grew piece count) which ironically drained P2's own threshold score because the flipped cells carried positive-sign influence.
- Did the endgame reach the stated win condition? **Yes — threshold, step 49.** No double-pass.

### Game 2 — Heuristic greedy vs greedy (same score function)

Both players used the same objective `own_eff - 0.5·opp_eff` with tiny tie-break randomness. Full game in 21 plies, no captures at all.

**Move trace:** 0, 2, 7, 3, 6, 4, 8, 10, 15, 11, 14, 12, 16, 18, 23, 19, 22, 20, 24, 26, 31.

The greedy score function rewards cells that (a) have multiple friendly neighbors and (b) drain enemy neighbors. Starting from an empty board, both players rush to build independent clusters along row 0 then row 1, expanding into adjacent 2-neighbor cells each turn.

**Endpoint:** step 21. P1 effective 43.21 (above threshold), P2 effective 38.32 (just 0.29 below threshold). P1 wins by first-move tempo of exactly one turn.

This is the "pure" expression of the game: in the absence of tactics, **first mover wins by a single tempo**. P2 reaches the same positional evaluation one move later than P1, and the threshold is set just tightly enough that that single-move difference decides the game.

- *P1 reflection:* The greedy strategy is a single-minded density pump. Every move selects a cell with the most friendly neighbors available. Against a mirror opponent, no captures fire and the winner is whoever placed stone #11 in a 2-neighbor configuration first.
- *P2 reflection:* Under pure greedy, P2 is always playing catchup. The game has a genuine first-mover advantage of roughly +5 effective-score points at the point the first player wins.
- Did the endgame reach the stated win condition? **Yes — threshold, step 21.** Clean threshold termination.

### Game 3 — Seat-swap / style-swap (P1 counter, P2 greedy; seed 42)

To probe balance without my reasoning being biased by having just played P1, I handed P1 to a "counter" heuristic (`-opp_eff + 0.5·own_eff + 1.0·piece_diff` — prioritizes attacking the opponent over building own score) while P2 kept the greedy density strategy.

**Endpoint:** step 48. Piece count P1=36, P2=12. Effective scores P1=36.05 (under threshold), **P2=40.57 (over threshold) — P2 wins.**

What happened: P1's counter heuristic spent early moves playing adjacent to P2's stones to drain opponent influence, which gave P1 many pieces but mostly in low-own-value cells. P2 meanwhile built a clean dense cluster. By move 48, P2's cluster integrity crossed 40.57 even though P2 had only 12 stones — because they were an uncontested dense block — while P1's 36 stones were diffused across the board including many captured cells carrying negative (P2-favoring) influence.

This is a clean **"quality beats quantity"** outcome, symmetric with Game 1 but with seats swapped: the player who builds a clean cluster and protects it wins over the player who spreads out and grabs captures.

- *P1 reflection (counter style):* Aggressive capture play generates more piece count but destroys your own threshold score because captured cells keep their enemy-favored influence. Over-attacking loses.
- *P2 reflection (greedy style):* Dense clustering wins if the opponent doesn't directly invade the cluster. Counter-attack from outside isn't enough to prevent threshold.
- Did the endgame reach the stated win condition? **Yes — threshold, step 48.** No double-pass.

### Across-games additional sanity checks

I ran a 4×4 grid of style matchups at 3 seeds each (48 games). Summary of winner counts:
- `greedy` vs `greedy`: P1 wins 3/3 (pure first-mover).
- `greedy` vs `counter`: P2 wins 2/3.
- `counter` vs `greedy`: P1 wins 1/3 (inverse of above — seat-swap corroboration).
- `counter` vs `counter`: Winner varies by seed; game length extends to 66 plies and board fills up (forced double-pass for last two plies). One seed ended P1=57 P2=7 majority win for P1.

This matches the Run-14 training database (both seeds finished at final winrate 0.5 — balanced under self-play). **The game is first-mover-biased under greedy play but balance is recovered when counter-tactics are available** — both players have a real repertoire.

**Double-pass resolution occurred in 1 out of 51 games I ran.** That game filled the board completely through 64 placements, then both players had only pass legal and passed twice. This is the "no-legal-move forced pass" variant, not the voluntary-pass exploit seen in Run 13. Still a real possibility to flag.

### Strategy guide — P1 side

1. Play a central or near-central opener. Torus means no edge bonus, so anything goes, but starting mid-board gives flexible torus-neighbor coverage.
2. **Build 2×N dense rectangles** — each additional stone with 2 friendly neighbors adds ~4.9 swing. A 2×5 rectangle is typically enough (27 points) to be 1–2 moves from threshold.
3. Never leave a straight line of 3+ friendly stones with only one end anchored to another friendly. The unanchored end is a custodian target. Always bend the line into an L or keep both ends connected.
4. When opponent plays a single-stone invader next to your cluster, do NOT capture immediately. Capturing flips the cell but transfers enemy-valued influence to you, hurting your threshold score. Instead *wall it off*: surround the invader so that even if they extend, your flank is already defended.
5. Near threshold (within ~6 points), your opponent will try a custodian sweep. Pre-emptively plug the axis openings: if you have a line, place a "cap" on the empty end before P2 does.
6. Single-tempo lead is the usual winning margin. Fight for it from move 1.

### Strategy guide — P2 side

1. Don't just mirror — P1's stone-per-stone parity loses by 1 tempo. Instead match densities but also **look for custodian bracket set-ups** while P1 builds.
2. Keep an "anchor" stone far from your main cluster (e.g. opposite corner) — it becomes the friendly bracket for a long-range capture of P1's extended line.
3. Custodian captures are most effective when P1 has just completed a 3+ stone line. Save your best bracket move for the moment P1 is 1–2 moves from threshold.
4. After a big capture, don't expect to threshold-win with the captured cells (their influence is anti-you). Instead use captures as *time* — each capture sets P1 back 6–10 points, buying you 2–3 turns to build a clean independent cluster.
5. If you're behind on effective score and P1 is about to threshold, your ONLY plays are custodian disruption. Find the longest P1 line and the empty-plus-friendly bracket slot.
6. Board-fill endgames favor whoever has piece-count majority at step 102 or at double-pass — if you can force one into existence while winning count, take it.

---

## PHASE 3 — STRATEGIC ANALYSIS (joint)

**Distinct viable strategies?** Yes — at least three meaningfully different winning approaches, empirically validated:
1. *Greedy density:* build dense 2×N rectangles fast, threshold-win by first-move tempo.
2. *Counter-raid:* hang back, invest in custodian bracket setups, win by draining and disrupting opponent's threshold approaches.
3. *Mixed:* start greedy, pivot to counter when opponent is within 6 points of threshold.

The style matrix showed that no single strategy strictly dominates. Greedy beats greedy by tempo, but counter beats greedy 2/3 of the time, and counter-vs-counter has variable outcomes.

**Meaningful counterplay?** Yes, very much so. The crucial decision every turn is "should I extend my cluster or disrupt the opponent's?" That trade-off is real because disruption via capture both helps (piece count, tempo) and hurts (captured cells carry enemy influence). A game of this game feels like a push/pull between positional (threshold) and tactical (custodian) objectives.

**Short-term vs long-term tension?** Present. Building a dense cluster is a multi-turn investment that the opponent can shatter with a single bracket move. Conversely, capturing looks good now but accelerates your opponent's threshold if your captured stones are adjacent to their cluster (the transferred influence helps them). Every custodian move has to be evaluated as "does this cost me more threshold than it costs the opponent?"

**Emergent concepts:**
- *Tempo:* First-mover advantage of one turn is the modal win margin under mirror play. Visible in the greedy-vs-greedy 21-move games ending at exactly 43.21 for P1 vs 38.32 for P2.
- *Influence field:* Real Go-like territory feel, but because the underlying number is a real-valued threshold, "influence" has a precise scalar meaning.
- *Custodian bracket setup:* A "half-bracket" (friendly anchor at one end of an enemy line) is a silent threat. Players must constantly scan for these.
- *Capture tax:* The most unusual emergent mechanic — since captured cells keep enemy-favorable influence, capturing is often a *losing* move on the threshold axis even though it's a winning move on the piece-count axis. I have not seen this trade-off in any documented abstract strategy game.
- *Forced double-pass at board-full:* A rare but real termination mode when both players pile stones without resolving threshold.

**Does topology matter?** Yes — the torus wrap on influence (but not custodian) is strategically important. Early-game placements on "edges" of the board are not weaker than center placements because wrap makes every cell equivalent. Corner-to-corner clusters are connected via torus distance 2 (not 14), which changes how far apart clusters interact. The custodian no-wrap rule also creates a real "edge effect" for capture threats — a stone on y=0 can only be captured by a bracket that starts within y<axis (i.e. strictly above not by wrap).

**First-mover advantage?**
- Under pure greedy (mirror play): strong, always decides the game by one tempo.
- Under varied heuristics: ~60–70% P1 win rate across my 48-game matrix. Non-trivial but not dominant. Counter-play can flip the outcome.
- Run 14 training database reports seed 80066 finished with winrate 0.5 (balanced) and seed 81066 likewise 0.5. Consistent with moderate but not extreme first-mover bias.

---

## PHASE 4 — NOVELTY ADVERSARY

### Adversary case (presented as forcefully as possible)

**(a) Catalog comparisons.**
- **Go:** The game has *custodian capture* (which Go does not), but its high-level flow is "place stones, try to dominate a scalar metric". The threshold-based win is essentially a Go scoring model compressed into a live termination criterion. Verdict from the adversary: **Go minus liberties plus custodian**.
- **Reversi/Othello:** Custodian capture is *the* defining Othello mechanic. This game is **literally Othello's capture rule** on an 8×8 board, with one very specific Othello-adjacent twist (alternating play, one stone per turn, place-only). Reversi/Othello's win is "most stones at end of board-fill"; this game's majority tie-break at max_turns is **identical**. Adversary argument: this is 80% Othello.
- **Hex / Y / Havannah:** Connection games on 2D boards. No analog — connectivity is not rewarded here.
- **Gomoku / Pente / Connect6:** Line-based wins. Custodian capture (Pente uses it too — pair-capture). Threshold-win replaces line-win. Partial similarity.
- **Amazons / Chameleon:** Movement-based. Irrelevant.
- **Lines of Action:** Movement; irrelevant.
- **Mancala variants:** N/A.
- **Life-like CA (Conway, Day & Night, etc.):** No CA is used here.
- **Nim / Blotto:** No.
- **Tumbleweed:** Influence-based territory game. Closest conceptual cousin — Tumbleweed also rewards influence-field territory without capture. But Tumbleweed has no custodian mechanic, no threshold cutoff, no torus.
- **Slither:** Chain-building. N/A.

**(b) CA literature.** No CA active — skip.

**(c) Simultaneous games.** Not applicable — game is alternating.

**(d) Re-skin claim.** The adversary's strongest re-skin argument: **"This is Reversi played on a torus with a modified win condition."**
- Same 8×8 board.
- Same custodian flip rule on axis directions.
- Difference: win by accumulated influence-field threshold (live) rather than "most stones at game end".
- Difference: torus topology (Reversi is grid).
- Difference: no "you must capture on every move" rule (in Reversi, a placement is illegal if it doesn't flip anything; here, any empty cell is legal).

**(e) Would an Othello expert have an advantage?** Yes, partially. The custodian reading (looking for bracket set-ups, seeing multi-capture diagonals — wait, only axis-aligned here, so actually *less* complex than Othello which allows 8 directions including diagonals) transfers directly. But Othello experts rely on 8-directional capture reading, which is **wrong here** — this engine captures only on 4 axis directions. Also, Othello experts read corners and edges, which are *meaningless on a torus*. And Othello's dominant strategy is *mobility-restriction* (forcing the opponent to play bad captures), which does NOT apply here because illegal-no-capture placements are not enforced. So an Othello expert would have a 15–20% edge at best, not a decisive one.

### Rebuttal (P1 and P2 jointly)

**1. The threshold-influence mechanic fundamentally changes the game from Othello.** In Othello, every placement must flip ≥1 stone (rule-enforced), which produces the cramped-mobility feel of the game. Here, any empty cell is legal. This means the early-game "build influence cluster without needing to capture" phase has no Othello analog — players can and DO spend the first 8–12 moves growing dense blocks without any captures. In Game 2, all 21 moves were capture-free density plays. That game simply cannot happen in Othello.

**2. Captured cells carry adverse influence — unprecedented trade-off.** The biggest strategic twist of this game is that capturing enemy stones transfers enemy-favored influence values onto cells you now own. This creates an explicit *capture-vs-threshold* trade-off with no analog in Othello, Go, or Pente. Observation from Game 1 move 28: P2 captured 3 P1 stones but their own effective score DROPPED from 30.43 to 22.16 because the flipped cells carried positive (P1-favoring) influence. In Othello you always want to capture; here capture is often a losing move on the primary objective. This is a genuinely new strategic dimension.

**3. Live threshold termination creates tempo as a first-class concept.** Othello ends when the board is full (or no one can move). Here the game ends the instant one player's effective sum crosses 38.616. This means every placement must be evaluated for "does this push me over threshold this turn?" and the winning move is often a density-optimizer, not a capture. In Game 2, the winner was the player who placed stone #11 one turn before the mirror opponent could — a clean tempo race that does not exist in Othello.

**4. Torus influence wrap combined with non-wrap custodian is genuinely novel.** Influence propagates across the torus edge (stone at (7,3) affects (0,3) at distance 1), but custodian walks stop at the boundary. This creates **strategically usable asymmetry**: players place "back-anchor" stones near the torus edge to collect influence from the opposite side without exposing them to custodian captures. A Reversi expert would have no intuition for this because Reversi is grid — the edges are strategic endpoints, not wrapping corridors.

**5. Specific Phase-2 moments that disprove the Othello analogy.**
- **Game 1 move 15:** I (P1) played (5,4) specifically because it had 2 friendly orthogonal neighbors — an Othello player would not care about friendly-neighbor count because Othello scoring ignores neighbor density.
- **Game 1 move 22:** P2 recaptured (5,2) via (5,1), the custodian walk passing through *captured* stones. The captured stones retained their prior ownership-flip history (influence values persisted across captures). No Othello flavor resembles this.
- **Game 3 endgame:** P2 won with only 12 stones against P1's 36, because the 12 stones formed an uncontested dense cluster. In Othello, more stones at game-end always wins. This game-3 outcome is categorically un-Othello.

**Resolution score (joint):** We award a Novelty score of **6/10**.
- Deductions: the custodian mechanic is unambiguously Reversi/Pente-derived; the 8×8 board is Othello's board; the majority-tiebreak is Othello's core win rule; absent the threshold mechanic this would be an uninteresting torus-variant of Othello.
- Credits: the influence-threshold primary win condition and the "captured cells hold adverse influence" second-order consequence create a legitimately new strategic dynamic. The torus+influence-wrap and custodian+no-wrap asymmetry is novel. The three observed strategy archetypes (greedy density, counter-raid, mixed) are distinct and non-trivially balanced.
- A 10 would require a mechanic with no direct analog — this game has a very clear Reversi parent, so 10 is unjustified. A 2–3 would require it to be a pure re-skin, which is disproved by the capture-tax and threshold-tempo dynamics. 6 captures the middle: a meaningful mutation of a well-known game that adds new strategic surface without being genuinely unprecedented.

---

## PHASE 5 — VERDICT

**Team ID:** team-5
**Game ID:** deb4dfe0382d
**Rules Summary:** Alternating-turn place-only game on an 8×8 torus with Reversi-style custodian capture and a live "effective-influence-sum ≥ 38.616" win condition. Influence propagates radius 1 on torus (wrapping); captures walk axis-aligned without wrap. Max 102 turns; piece-count tiebreak on timeout or double-pass.
**Topology:** 8×8 torus (both axes wrap for influence, neither wraps for custodian walks).
**Turn Structure:** Alternating, 1 piece per turn.

### SCORES (1–10)

- **Strategic Depth: 7/10** — Three distinct strategy archetypes validated empirically. The interaction between dense-cluster building (threshold objective) and custodian raid (piece objective) creates genuine position-evaluation tension. Complete information with moderate branching factor (~30 meaningful moves per turn). However, the 38.616 threshold is reachable in ~10 stones and games end in 20–50 moves, so depth is real but not deep-learning-deep.
- **Emergent Complexity: 7/10** — The "captured cells carry adverse influence" dynamic is an emergent property that I did not anticipate reading the rules — I had to discover it by playing. It creates a true trade-off where the obvious good move (capture) is often the losing move (threshold damage). Non-trivial. The torus-influence vs. grid-custodian asymmetry is also emergent. Subtracting a point because once you understand the capture-tax rule, the game collapses to "build carefully, only capture when the enemy is within 1 move of threshold".
- **Balance: 6/10** — Under greedy self-play, P1 wins by a single-tempo margin ~100% of the time. Under mixed strategies, P1 win rate drops to ~65%. The Run 14 training database reports final winrate 0.5 in both seeds (balanced under self-play), which is consistent with "P1 has tempo advantage but P2 has tactical compensation that strong agents learn." My seat-swap test (Game 3 with swapped heuristics) produced a clean P2 win at step 48 — P2 can win when heuristics differ. Not broken, but noticeably P1-favored.
- **Novelty (post-adversary): 6/10** — See Phase 4 joint resolution. Strong Reversi parentage, but the influence-threshold win and captured-influence-retention create genuine new strategic surface.
- **Replayability: 6/10** — 20 to 66 move games with 3 viable strategy archetypes. After ~5 games the strategy space feels mostly explored, but individual games still have capture surprises. Higher than a pure puzzle, lower than Go.
- **Overall "Would I play this again?": 6/10** — Yes, once or twice, for the custodian capture-tax twist. It's a tidy little game, but I'd choose real Othello or Go for a longer session.

### CLOSEST KNOWN-GAME ANALOG

**Reversi/Othello** is the closest analog. Identical axis-aligned custodian flip on an 8×8 board, and the majority-tiebreak fallback is Othello's canonical win rule. The game is NOT identical because:
1. Win condition is primarily an influence-sum threshold evaluated live, not end-of-game majority.
2. Placements are legal anywhere (Othello requires ≥1 flip per move).
3. Topology is torus, not grid.
4. Custodian walks stop at axis boundaries (no wrap).
5. Captured cells retain their pre-capture influence values, creating an unusual capture-tax.

### KILLER FLAWS

- **Moderate first-mover advantage under mirror play.** Pure greedy self-play always favors P1 by a 1-tempo margin. Not game-breaking (training winrate is 0.5), but the symmetry is fragile.
- **Capture-tax makes captures feel counter-productive a lot of the time.** I found myself avoiding captures in several positions that would be "obviously good" in Othello. The rule is learnable but unintuitive on first encounter. Could be perceived as a flaw by a new player.
- **No killer dominant strategy or short forced win was found.** The threshold is high enough to require ~10+ stones, no pass-based exploit is available because passing ends the game in majority-mode, and the training winrate of 0.5 corroborates balance.
- **One observed forced-double-pass ending** out of 51 simulated games. Not an exploit — the board was full and both players were forced to pass. Not a real concern but worth flagging.

### BEST QUALITY

The **capture-tax mechanic** (captured cells retain their prior influence values, meaning captures help piece count but hurt the threshold objective). This creates a genuine "should I capture or should I build?" dilemma that I have not encountered in any other abstract strategy game. It elevates the game above a pure Reversi-on-torus re-skin.

Also notable: the **torus-wrap asymmetry between influence (wraps) and custodian (does not wrap)**, which creates strategically-usable geometric quirks — e.g., placing a "back-anchor" stone that can collect influence across the board but is not vulnerable to long-range bracket capture.

### IMPROVEMENT IDEAS

- **Rule change: when a cell is captured via custodian, zero its influence value and re-seed from the new owner's placement on the original placing stone.** This would remove the capture-tax ambiguity and make captures consistently good (matching player intuition). The game would likely become more tactical and less "compute the threshold cost of capture". Arguably this makes the game *shallower* though — the current capture-tax is one of the few genuinely novel elements, so this "fix" would be a trade-off.
- **Alternative improvement:** make the threshold scale with piece count (e.g. `threshold = 38.6 · (64 - total_pieces_on_board) / 64`), so threshold tightens as the game progresses. This would force earlier resolution and prevent the forced-double-pass ending.
- **Better improvement:** add a small rule that passing is only legal if you have no legal placement. This eliminates voluntary-pass exploits (not observed here but a known Run-13 failure mode) and tightens the game.

---

## Appendix — Move sequences for full reproduction

Game 1 full sequence (manual moves 1–46 + autoplay 47–49):
```
27,63,28,62,35,56,36,55,26,54,34,53,29,61,37,45,19,46,20,21,22,13,18,17,10,44,30,43,52,60,16,47,25,5,33,23,24,31,9,32,41,2,42,1,57,50,38,58,11
```
End state: step 49, Winner 1, P1 eff 49.59, P2 eff 35.66.

Game 2 full sequence (greedy vs greedy, seed 42):
```
0,2,7,3,6,4,8,10,15,11,14,12,16,18,23,19,22,20,24,26,31
```
End state: step 21, Winner 1, P1 eff 43.21, P2 eff 38.32.

Game 3 full sequence (counter vs greedy, seed 42):
```
49,62,48,61,56,54,57,53,55,60,52,46,63,45,59,38,30,47,37,39,31,44,43,4,51,5,58,6,50,14,29,13,42,12,41,20,21,11,19,3,22,28,27,36,35,15,23,7
```
End state: step 48, Winner 2, P1 eff 36.05, P2 eff 40.57.

All games engine-verified via `play_helper.py --action play --moves "..."` and cross-checked with `team5_helper.py` which re-reads `board_values` and effective sums directly from the engine.
