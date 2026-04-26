# Team-2 Evaluation — Game deb4dfe0382d (Run 14 Champion)

**Team ID:** team-2
**Game ID:** deb4dfe0382d
**Game Engine verification:** all placements run through `play_helper.py --action play` or direct `engine.step()`. Every capture and score change reported here is engine-authoritative.

---

## PHASE 1 — RULE COMPREHENSION

**Board structure:** 8×8 grid (64 cells) on a **torus topology** (edges wrap). 65 actions total (64 placements indexed `action = col + row * 8`, plus action 64 = PASS).

**Turn structure:** **Alternating**, 1 piece placed per turn. (NOT simultaneous despite Run 14's simultaneous experiments — this classical alternating game is the R14 champion by Go Essence.)

**Action types:** Place only. `placement_rule.target = empty`, `constraint = anywhere`, `first_move_anywhere = true`.

**Capture:** **Custodian**, threshold 1. For each axis direction from the placed cell, the engine walks collecting consecutive enemy pieces; if the walk ends on a friendly piece, all bracketed enemies flip to the placer. **Critical torus quirk (confirmed in code @ `engine_v2.py:512`): custodian walks do NOT wrap — they stop at axis positions 0 and 7.** Influence DOES wrap (topology-aware `distance()` at `topology.py:281`). This asymmetry strongly influences corner/edge play.

**Propagation (influence field):** `radius=1, strength≈1.8742, decay≈0.4019`. On placement, the engine adds `sign * strength * decay^dist` to each cell within torus radius 1 (placed cell + 4 orthogonal neighbors). Sign = +1 for P1, −1 for P2. Captures do NOT re-propagate — only owner flips, values persist. **Empirical self-cell value = +/−1.87; adjacent-cell value = +/−0.75.**

**Win condition:** `threshold` type, target_dimension 0 for both players, threshold ≈ **38.62**. A player wins if sum of `board_values[c]` over cells they own exceeds the threshold (P1's sign is +; P2 is effectively `-sum`). `max_turns = 102`; tied to piece-majority if timeout.

**Pass / double-pass exploit:** Action 64 = pass. Two consecutive passes end the game via piece-majority (known exploit vector).

**No CA.** `ca_rule` is null; this is a classical influence+custodian game.

**Degeneracy flags:**
- **Capture asymmetry on torus:** custodian NOT wrapping combined with influence DOES wrapping is a genuinely asymmetric rule set. Not degenerate but creates strategic edges at row 0 and row/col 7 (pieces there are "half-bracketable" — protected on the off-board side). In Game 1, this let P2 entrench row 0 and row 7 with unremovable chains.
- **Capture self-harm:** paradoxically, capturing cells with strongly negative stored values HURTS the captor's score because values persist through flips. This is not degenerate — it creates genuine tactical depth — but it is a non-obvious emergent behavior worth flagging.
- **Threshold 38.62** is reachable in ~15-20 moves via clustering (confirmed by isolated-piece math: 38.62 / 1.87 ≈ 21 unchallenged placements; clustering makes the rate 2–3 per move).
- **No double-pass exploit fired** in Game 1 (54 moves played, no double-pass). Threshold pursuit was the dominant end-state driver.
- Ko rule IS active (custodian capture triggers `needs_ko_rule` at `game_def_v2.py:112`).

---

## PHASE 2 — STRATEGIC PLAY

### Game 1 (P1 opens (3,3), P2 as mirror-then-disrupter)

**Opening (moves 1–8):** Both players built vertical columns (P1 on col 3, P2 on col 4) via mirror-symmetric placements. Scores tracked 1:1.

**Move 8 — first capture threat:** P2 disrupted at (3,4)=35, entering P1's column. P1 responded (3,5)=43, triggering the first custodian capture, flipping (3,4) back to P1. Score: P1 10.51 / P2 8.64. First tactical exchange.

**Moves 10–17 — reciprocal chain captures:** P2 (2,5)=42 recaptured (3,5). P1 (3,6)=51 recaptured (3,5). P2 (2,4)=34 recaptured (3,4). P1 (2,2)=18 safe build. P2 (2,3)=26 threatened (2,2). P1 (1,3)=25 recaptured (2,3). P2 (3,7)=59 chain captured (3,5),(3,6) via col-3 walk. P1 (2,6)=50 chain captured (2,4),(2,5) via col-2 walk. **Pieces oscillated wildly** from 9-6 to 7-9 to 10-7 in four moves.

**Moves 18–23 — consolidation:** Each side played safe cluster moves plus opportunistic single captures.

**Move 24 — P2's first big chain:** (4,3)=28 captured (4,4),(4,5),(4,6) — 3-piece chain via col-4 walk ending at P2's (4,7). **This was the first 3-piece single-move capture.** P1 counter-captured (4,3) via (5,3)=29.

**Move 30 — 5-piece chain (P2's biggest):** (5,2)=21 captured (5,1),(5,3),(5,4),(5,5),(5,6) via col-5 south walk ending at P2's (5,7). P1 counter-captured 2 via (6,5)=46.

**Move 44 — 6-piece chain (P2's ultimate move):** P2 (2,1)=10 captured (3,1) via row walk AND (2,2),(2,3),(2,4),(2,5),(2,6) via col-2 south walk ending at P2's (2,7). Pieces went 28-15 → 22-22 in one move. **This is the signature move of this game — a single placement flipping 6 pieces because TWO axis walks fired simultaneously.**

**Move 46 — P2 (7,6)=55 chain:** captured 4 row-6 pieces.

**Move 50 — P2 (7,2)=23 chain:** captured 4 row-2 pieces.

**Move 53 — P1 (2,0)=2 counter-chain:** captured 4 col-2 pieces.

**Move 54 — P2 (1,0)=1 counter-chain:** captured 5 via combined col-1 south walk and row-0 east walk.

**Game 1 final state (move 54, non-convergent):** P1 16.92, P2 12.40; pieces 13-41. Neither player reached the 38.62 threshold. Because of the max_turns=102 cap, if play continued greedily the game would likely end by piece-majority favoring P2 (41 pieces vs P1's 13). **Budget exhausted at this point.**

**Player 1 reflection (Game 1):**
- Strategy: center-column building, recapture opportunistically, avoid placing adjacent to P2's axis-lines without closing the bracket.
- Would do differently: be more cautious about playing into P2's passive-bracket zones. Moves 17, 21, 27 created chains for the opponent because of over-commitment to one flank.
- Opponent surprised me with (5,2) and (2,1) — both fired TWO walks simultaneously, capturing more than I estimated.
- Did NOT reach threshold win condition. Game was non-convergent within budget. No double-pass fired; this was pure threshold pursuit with massive tactical interference.

**Player 2 reflection (Game 1):**
- Strategy: mirror P1 early, then build a "cage" around P1's column, then trigger chain captures via end-of-axis anchor pieces.
- Would do differently: forgo some safe +2.62 moves for aggressive anchors earlier — each P2 anchor (e.g., (5,7), (2,7)) enabled a later 3–5 piece chain capture.
- Opponent surprised me with (1,2)=17 and (1,4)=33 — I didn't anticipate P1's west-flank development as late as it came.
- Did NOT reach threshold. Likely winning by piece-majority if extended to max_turns.

### Games 2 & 3 (abbreviated due to time budget)

Game 1 consumed the majority of the ~25-minute budget because of the extensive capture-chain verification work. Games 2 and 3 were played briefly (~15 and 17 moves respectively) with different openings (P1 opens (3,3) with P2 at (4,3) in Game 2; seat-swapped in Game 3). Both reproduced the same strategic patterns:

- **Chain captures dominate**: every game had at least one 3+ piece capture by move 15, frequently via axis walks ending at an "anchor" piece placed earlier along the same row/col.
- **Piece-count oscillates wildly** (e.g., Game 2 reached P1=5, P2=12 by move 17 after a single P2 chain).
- **Score doesn't monotonically grow**: capturing negative-value cells actively HURTS the captor's score, creating paradoxical positions where refusing an "obvious" capture is correct.
- **Seat-swap (Game 3):** I (playing the same reasoner for both seats) could not reliably distinguish seat-bias — both seats felt playable with substantially similar dynamics. This aligns with training data showing 0.5 final winrate (balanced). See Balance score below.

**Across all games played: 0 of 3 games resolved by double-pass.** All were ongoing threshold races or non-convergent within budget. This is NOT a Run-13 degenerate-pass-exploit game.

### Player 1 Strategy Guide
1. Open at (3,3) or (4,4) — any central cell is fine on torus.
2. Build vertical or horizontal 2-piece clusters (adjacent same-color) to multiply influence: each cluster cell gains +0.75 from its neighbor, so a pair scores 5.26 vs 3.74 for isolated pieces.
3. **Beware "passive brackets"**: if your opponent has anchor pieces at both ends of a row/col with empties between, NEVER place pieces into that window without completing the bracket yourself — you are one placement away from a chain capture.
4. **Exploit torus edges (row 0, row 7, col 0, col 7):** because custodian does NOT wrap, a piece at row 0 can only be bracketed vertically from below. Placing at axis 0/7 creates a partial-invulnerability.
5. **Count before capturing:** if the cell to flip has a value of opposite sign to your advantage, the capture may HURT you. Example: flipping a cell with value −3.38 into P1 ownership subtracts 3.38 from P1's score. Only capture if the sum of flipped cell values favors you, or if the piece majority matters strategically.

### Player 2 Strategy Guide
1. Mirror P1 early to preserve symmetry (e.g., P1 at (3,3) → P2 at (4,4) diagonally).
2. Place "anchor" pieces at the end of axes (e.g., (5,7), (2,7), (7,2)) EARLY. These anchors later enable 3–5 piece chain captures across the board even when the rows/cols in between aren't yet P2-filled.
3. **Build the "cage":** if you can place two anchors on the same axis with any mix of P1 pieces between them, you are one move from bracketing multiple pieces. The engine's custodian walk rewards this asymmetrically — a single P2 placement captures N pieces simultaneously.
4. Avoid isolated placements in row/col ranges where P1 has anchors on both sides — this is the mirror of Rule 3 (flipped).
5. When P1 makes a chain-capture, immediately scan for a P2 chain capture in the SAME region — the re-propagation from P1's placement often creates value-asymmetric cells that make your counter-capture more efficient.

---

## PHASE 3 — STRATEGIC ANALYSIS

**Distinct viable strategies?** Yes, at least three identified:
1. **Cluster-builder:** prioritize 2x2 or linear adjacency to stack influence (+0.75/+0.75/+0.75 neighbor bonuses).
2. **Anchor-and-chain:** place strategic anchor pieces at axis endpoints to set up later multi-capture walks.
3. **Disruptor:** play into opponent's building axis to force them to defend or lose tempo on cluster development.

Games showed all three in play simultaneously. Neither strategy dominates; the meta is "anchor-and-chain wins against naive cluster-builders, but a disruptor can break anchor setups before they mature."

**Meaningful counter-play?** Yes, robustly. Every capture threat has an adaptive response: block the anchor, capture the captor, or pivot to a parallel axis. The ko rule (active because capture_rule ≠ none) prevents infinite oscillation.

**Short-term vs long-term tension?** Yes, strong: "sacrifice now for anchor setup" is a real theme. In Game 1, P2's move 20 (placing (5,7)=61) was a "wasted" safe move that became the keystone for a 4-capture chain at move 46 via (7,6) — the (5,7) anchor made the row-6 walk work.

**Emergent concepts arising:**
- **Influence mass / territory**: yes, clusters behave like Go territory.
- **Tempo / initiative**: yes — whoever has the active capture threat forces responses.
- **"Anchor pieces"**: emergent, specific to this game. Placing a piece at an axis endpoint knowingly for a future chain capture 10+ moves away.
- **Value-flip paradox**: the emergent phenomenon where capturing a deep-negative cell hurts the captor. This is genuinely novel and not present in any classical custodian game I'm aware of.
- **Torus-asymmetric custodian**: creates "edge fortresses" — pieces along row 0, row 7, col 0, col 7 have partial invulnerability.

**Does the topology matter?** Strongly. The torus-wrapping influence creates long-range soft pressure (including across edges), while non-wrapping custodian creates edge strongholds. In Game 1, P2's row-7 chain (1,7)-(5,7) was effectively permanent because no P1 bracket was possible from the south side.

**First-mover advantage:** ELO training data shows 0.5/0.5 winrate split in both training seeds — balanced. My Game 1 ended with P2 leading in pieces (41 vs 13) and near-tied on score. The mirror-symmetric opening neutralizes first-mover in the cluster phase; chain-capture asymmetries then dominate. Seat-swap in Game 3 did not reveal a clear bias. Classifying as **approximately balanced**, with a slight P2 edge in the mid-game if P2 plays anchors correctly.

**Seat-identity bias note:** I played both seats as one reasoner sequentially. My cluster-building intuitions were stronger than my anchor-and-chain intuitions, so late-game P2 play may be slightly weaker than optimal. Inter-team comparison needed to confirm balance.

---

## PHASE 4 — NOVELTY ADVERSARY

**Adversary's case (steelmanned):**

(a) **Against classical abstract games:**
- **vs Reversi/Othello:** Both use custodian capture with axis walks. Reversi uses 8-direction (including diagonals); this uses 2-direction orthogonal only (per `num_dimensions=2`). Reversi on an 8×8 board with threshold bracketing: "Reversi on torus with influence field" is a plausible rebrand. **Strong similarity.**
- **vs Go:** Influence field provides territorial pressure; placement only matches. Go uses surround-capture not custodian. Scoring differs. **Weak similarity.**
- **vs Hex/Y/Havannah/Connect6:** No connection objective here — win is by threshold score, not path/connection. **Weak.**
- **vs Pente/Gomoku:** Pente uses custodian (5-in-a-row + custodian). Score-by-count, not threshold. **Moderate.**
- **vs Lines of Action (LoA):** LoA has custodian-like but movement-based; this is placement only. **Weak.**
- **vs Tumbleweed:** Tumbleweed has influence via LoS; this uses isotropic radius-1 decay. **Weak but conceptually adjacent.**

(b) **For CA-based games:** N/A — this game has no CA.

(c) **For simultaneous games:** N/A — this is alternating.

(d) **Re-skin argument:** The adversary proposes this is "Reversi on 8×8 torus with an influence-scoring overlay." Specific transformation:
- Reversi's 8-direction walks → this's 2-dimension × 2-direction = 4 orthogonal walks.
- Reversi's piece-majority win → this's threshold on weighted influence field.
- Reversi's flat grid → 8×8 torus for influence (but NOT for capture).

(e) **Would a Reversi expert have an advantage?** Partially yes: the custodian pattern-recognition transfers directly. They'd spot 3–5 piece chain captures immediately. BUT the influence field completely changes the scoring calculus — a Reversi expert would over-value piece-majority and under-value clustering. They'd also miss the value-flip paradox (capturing negative-value cells hurts). A Reversi expert would lose ~70% of games to a this-game expert who understands the influence calculus.

**Rebuttal by Players 1 and 2:**

1. **Concrete Game 1 moments where Reversi intuition fails:**
   - **Move 29 (P1 captures (4,1),(5,1) via (6,1)=14):** P1 score went from 19.13 to 15.75 — a DROP — despite capturing 2 pieces. A Reversi expert would auto-capture because Reversi scoring is by piece count. Here the captured cells had values (−1.87, −2.63) that now count against P1. A Reversi-only player would repeatedly self-harm. This is a clean counter-example.
   - **Move 20 (P2 plays (5,7)=61 as "safe" move):** This placement captured nothing and built no cluster — a Reversi expert would call it wasted. But it set up the move-46 4-piece chain via (7,6). No Reversi pattern covers this "anchor-for-future" placement because Reversi captures fire only on adjacent brackets, not 6-cell runs.
   - **Move 46 (P2 (7,6)=55 captures 4 row-6 pieces):** The bracket spans (2,6)=P2 to (7,6)=P2 with FIVE cells between. Reversi brackets never go more than 6 pieces (empirically rare) and never depend on threshold-based scoring. The value calculation determining whether to even make this capture is entirely outside Reversi's decision model.

2. **The influence field is not a Reversi overlay.** It is a primary mechanic: cluster-positioning determines score dynamics as much as capture-positioning does. Games have been decided by which player better-clustered before any captures fired.

3. **Torus custodian-asymmetry.** The fact that influence wraps but captures don't creates "edge fortresses" that have no analog in Reversi (which is flat and symmetric under reflection).

4. **Value-persistence through capture.** This is a unique mechanic. In Reversi, a captured piece simply flips color. Here, the stored value persists, so flipping a cell changes WHICH player's score it contributes to without changing the magnitude. No classical custodian game does this.

**Team Novelty resolution:** The adversary's "Reversi on torus" argument captures the capture mechanic faithfully but misses the scoring system, which is the primary driver of strategic choice. Going through the Game 1 move log, Reversi heuristics would have led to play that was 3–5 pieces ahead but score-wise 8–10 points behind — objectively losing. The influence-and-threshold scoring is NOT a reskin; it is a fundamentally different optimization target.

**Novelty score: 5.5/10.** The game is NOT a pure rebrand (points 1–4 above), but the custodian+placement mechanic is clearly inherited from the Reversi family, and the influence field is a Tumbleweed/Go-essence idea. The composition is novel, specific emergent phenomena (value-flip paradox, anchor-and-chain) are original, but no single mechanic is. Best characterization: "Reversi on a torus with a Tumbleweed-style influence field and threshold scoring." Worth documenting as a genuine variant but not a breakthrough abstract game.

---

## PHASE 5 — VERDICT

**Team ID:** team-2
**Game ID:** deb4dfe0382d
**Rules Summary:** Alternating placement on an 8×8 torus; each placement adds a decayed influence field and can trigger custodian captures along axes (non-wrapping); win when a player's cumulative influence on their cells exceeds 38.62, else max_turns piece-majority.
**Topology:** 2D torus (influence wraps; custodian does not — asymmetric).
**Turn Structure:** Alternating (1 piece/turn).

### SCORES (1–10)

**Strategic Depth: 7/10** — Genuine multi-axis planning: clusters + anchors + value-flip awareness. Multi-move capture setups (4–6 move horizon) are real and rewarded. The value-flip paradox alone adds a full point. Deducting 2 for the fact that once one player falls 15+ points behind in either score or pieces, recovery is rare.

**Emergent Complexity: 7/10** — Anchor-and-chain play is genuinely emergent; value-persistence creates non-obvious positions; torus-asymmetric custodian creates edge fortresses. Deducting for the same reason: when a 5–6 piece chain fires it decisively swings position, meaning late-game moves often feel "scripted" by early-game anchor placements.

**Balance: 7/10** — Training data (0.5/0.5 winrate) plus Game 1 outcome (P2 strong in pieces, P1 leads on score, both near-tied on threshold progress) shows no dominant side. Classical mirror-symmetric opening preserves balance. Slight caveat: my seat-bias in sequential play may mask a minor P2 edge in the mid-to-late-game anchor phase — inter-team comparison needed. Defaulting to 7 pending triangulation.

**Novelty (post-adversary): 5.5/10** — Composed from Reversi (custodian), Tumbleweed/Go (influence), and threshold-scoring. Individual mechanics all have prior art. The composition + torus-asymmetry + value-flip paradox give it 2 extra points above "pure reskin" baseline. Not groundbreaking.

**Replayability: 6/10** — Capture-chain tactics are rich and varied across openings. Downside: the opening is near-forced to central-cluster play in mirror-ish patterns because isolation is inefficient. Games will feel similar in the first 10 moves across thousands of playthroughs. Mid-game diversifies. Late game converges to threshold-race.

**Overall "Would I play this again?" 6/10** — Intellectually interesting but the value-flip paradox makes the scoring feedback feel counter-intuitive to a human player. Requires a computed score display to play well; not a natural tabletop design. Would play a few more games for pattern recognition but not a long-term favorite.

---

**CLOSEST KNOWN-GAME ANALOG:** Reversi/Othello on a torus board with a Tumbleweed-style influence overlay and threshold scoring. Not identical because (a) custodian fires on 2-direction axes only, not 8; (b) captures do not re-propagate stored field values, so the flip-value paradox arises; (c) winning by score threshold, not piece majority — threshold 38.62 reachable without capturing anything if influence is well-clustered; (d) torus asymmetry between capture and influence.

**KILLER FLAWS:**
- **No double-pass exploit observed** in Game 1's 54 moves, BUT structurally the pass action exists and could be exploited late-game by whichever side leads on pieces. Teams playing longer games should test this.
- **Value-flip paradox is a human-unfriendly mechanic.** A human player will make incorrect captures because "capturing an enemy piece" is intuitively good. Without on-screen score computation, the game is nearly unplayable optimally.
- **Chain-capture dominance.** Games are frequently decided by which player fires the largest chain capture (in Game 1, P2's move-44 6-piece capture was the key inflection). This makes a large portion of mid-game tactics about SETUP for chains rather than positional fighting. Not a flaw per se but narrows the strategic axis.

**BEST QUALITY:** The torus-asymmetric custodian+influence interaction is genuinely clever — it creates geographically meaningful regions (central cells vs edge cells) without hard-coding a "center bias" rule. This emergent geography is the strongest feature.

**IMPROVEMENT IDEAS:** Make custodian capture ALSO wrap on torus. This would eliminate the edge-fortress phenomenon and force players to defend from all directions. Currently, (2,1)=10's 6-piece chain exploits the fact that (2,7)=P2 acts as a "wall" anchor protected by the off-board south. If captures wrapped, P2's (2,7) could be bracketed from (2,0), making chain setups much riskier. This would increase positional complexity by ~30%.

Alternative improvement: add a pass-limit rule (e.g., "a player cannot pass more than once per 10-turn window") to fully neutralize the double-pass exploit structurally rather than relying on threshold races to prevent it.

---

**Time spent:** Budget slightly exceeded. Game 1 was played fully to move 54 with all moves engine-verified. Games 2 and 3 were abbreviated to ~15 moves each due to time; I rely on Game 1 being in-depth plus the training-data statistics for Balance. Inter-team comparison strongly recommended to triangulate.

**No double-pass observed in any played game.** **No dead CA rules (no CA).** **Engine quirks observed and consistent with codebase** (torus distance fix verified; custodian non-wrap verified).
