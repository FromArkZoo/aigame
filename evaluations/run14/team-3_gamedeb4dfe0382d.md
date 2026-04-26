# Team-3 Evaluation — Game `deb4dfe0382d` (Run 14 Champion, GE=0.5174)

Team ID: team-3
Game ID: deb4dfe0382d
Date: 2026-04-22
Played independently; verdict formed before reading any other team's evaluation.

---

## PHASE 1 — RULE COMPREHENSION

### Board & topology
- 2-D board, axis size 8, **torus** wrap.
- 64 cells (state dim 131 in the generator, but the playable surface is 64 + 1 pass action = 65 actions).
- Adjacency: von Neumann (4-neighbour) with wrap-around on both axes. On a torus every cell is interior; there are no edges or corners.

### Turn structure
- **Alternating**, 1 piece per turn. Not simultaneous. (Run 14's novel simultaneous-play family is not used here; this is a classic alternating game.)

### Action types
- `place` on any empty cell, plus an explicit PASS action (id 64). `first_move_anywhere=True` — no opening restriction.
- No move/slide actions.

### Capture rule
- **Custodian** (Othello-style axis-line bracketing). Walks along the four axis directions from the placed stone; if the walk passes over a consecutive run of enemy stones and terminates on a friendly stone, all bracketed enemies flip to the mover.
- `threshold: 1` in the rule blob is not actually used by the custodian branch — the engine only needs at-least-one-enemy-then-friendly.
- Verified from engine source (`engine_v2._capture_custodian`): **on torus the walk is clamped to `0 <= pos < axis_size` — custodian does NOT wrap**, even though influence propagation does. This asymmetry is real and strategically material.

### Propagation (influence)
- `strength = 1.8742`, `decay = 0.4019`, `radius = 1`.
- On torus with radius 1 this touches the placed cell (dist 0) and its 4 von-Neumann neighbours (dist 1, wrapped).
- Sign is +1.874 at (distance 0) for P1 placements, −1.874 for P2. Each neighbour gets ±0.753.
- Values accumulate permanently; captures flip ownership but DO NOT reset `board_values`. An enemy cell you capture still carries its accumulated +/−, which can reduce your threshold total when you "own" it.

### Win condition
- `threshold` — a player wins when the sum of `board_values` over the cells they own, with sign-flip for P2, exceeds **38.616**.
- `max_turns = 102`. If nobody crosses threshold and nobody double-passes, majority piece count at turn 102 decides.
- Consecutive-pass rule is active: two passes in a row → `_end_by_max_turns` → majority rule. The **double-pass majority exploit is reachable**, though it is unlikely to fire here because threshold is cheap to reach (see below).

### Degenerate-rule flags
- **Threshold is reachable** — a 3×3 solid cluster (9 own cells) totals 34.9 (just under); a 3×4 block (12 cells) totals 48.1; a 4×4 block hits 66.1 (well over). Reaching threshold needs roughly a dozen connected stones, which is well within typical game length. Training data shows avg game length 22–33, consistent with races that end on threshold.
- **Custodian is NOT inert.** It triggers often once stones line up. Captures of 3–4 pieces in one move happened multiple times in Phase 2.
- **No double-pass exploit** fires in normal play because threshold is cheaper to reach than majority.
- **Torus wrap only affects influence, not capture.** A player who "runs a line off the side of the world" does not close it into a capturing bracket — a subtle asymmetry.
- One latent quirk: because captured cells retain prior enemy `board_value`, **captures are threshold-negative for the capturer** in absolute terms (they add accumulated negative value into your own sum). They are still net positive for piece-differential and for denying the opponent, but the "free stones" instinct is wrong — every capture lowers your own threshold progress in the short term.

No rules appear degenerate in the "P1 wins in ≤5 moves" sense. But see Phase 3 re. structural first-mover advantage.

---

## PHASE 2 — STRATEGIC PLAY

Every move below was engine-verified via `play_helper.py … --action play`. I was the same reasoner for both seats; Game 3 swaps seats (P2 is treated as the "disruption" side). Seat-identity bias acknowledged.

### Game 1 — centre opening, disruptive mid-game

Full move list (engine-verified):
`27, 63, 35, 55, 28, 62, 36, 54, 37, 53, 29, 61, 43, 45, 44, 21, 30, 46, 38, 42, 51, 20, 52, 22, 12, 34, 23, 26, 19, 60, 31, 47, 39`

Move-by-move commentary (abbreviated after move 15, where the capture cascade begins):

- **M1 P1 (3,3)=27**: Centre; symmetry on torus means any cell is equivalent, but (3,3) anchors a mid-board cluster.
- **M2 P2 (7,7)=63**: Opposite pole; torus-distance 8 (maximum). Pure mirror strategy.
- **M3 P1 (3,4)=35**: Connected extension.
- **M4 P2 (7,6)=55**: Mirror.
- **M5–12**: Both players grow 2×3 blocks. After M12, P1 eff = 21.79, P2 eff = 21.79 (exactly tied).
- **M13 P1 (3,5)=43**, **M14 P2 (5,5)=45**: P2 broke mirror to play (5,5), one cell away from P1's cluster. This is a contact move.
- **M15 P1 (4,5)=44**: P1 densifies. After M15: P1=28.55, P2=23.66. P1 leads by ~5.
- **M16 P2 (5,2)=21 — CAPTURE (5,3),(5,4)**: P2 notices that (5,5) is friendly and the walk up from (5,2) passes (5,3),(5,4),(5,5). Placing at (5,2) captures the column. This swings differential: P1 drops 28.55→22.54, P2 drops 23.66→19.53 (both drop because cells with high positive `board_value` simply change sides). Piece counts flip from 8/7 to 6/10.
- **M17 P1 (6,3)=30 — CAPTURE (5,3)**: Immediate counter-bracket. P1=8, P2=9.
- **M18 P2 (6,5)=46**: Densify cluster.
- **M19 P1 (6,4)=38 — CAPTURE (5,4)**: Recovers another. P1=10, P2=9.
- **M20 P2 (2,5)=42 — CAPTURE (3,5),(4,5)**: P2 notices (5,5) is friendly; walking right from (2,5) crosses two P1 stones and ends at a P2 friend. 2-piece capture.
- **M21 P1 (3,6)=51 — CAPTURE (3,5)**: Recovers.
- **M22 P2 (4,2)=20 — CAPTURE (4,3),(4,4)**: The sneakiest capture of the game. (4,5) was still P2 from the M20 capture, so the walk down column 4 from (4,2) terminates at a friendly P2 and flips (4,3),(4,4). Double capture. P1 drops 35.31→26.29; P2 drops 27.41→21.77.
- **M23 P1 (4,6)=52**: Placement value move — (4,6) already had high prior `board_value` from previous placements; it also sits in P2's cluster perimeter, reducing P2's own-cell contributions from the wider pattern. P1 eff 29.67, P2 eff 20.27.
- **M24 P2 (6,2)=22 — CAPTURE (6,3),(6,4)**: Another double capture along column 6. P1 drops to 23.66, P2 to 17.64.
- **M25 P1 (4,1)=12 — CAPTURE (4,2),(4,3),(4,4),(4,5)**: **Quadruple capture.** Walking down column 4 from (4,1) passes four O's and ends at P1's (4,6). Piece count goes 7/17 → 12/13; P1 eff 26.29→35.31.
- **M26 P2 (2,4)=34 — CAPTURE (3,4),(4,4),(5,4)**: Triple capture across row 4. P1 drops to 22.91.
- **M27 P1 (7,2)=23 — CAPTURE (5,2),(6,2)**: Row 2 double.
- **M28 P2 (2,3)=26 — CAPTURE (3,3),(4,3),(5,3)**: Triple row 3.
- **M29 P1 (3,2)=19 — CAPTURE (3,3),(3,4)**: Column 3 double.
- **M30 P2 (4,7)=60 — CAPTURE (4,5),(4,6)**: Column 4 double.
- **M31 P1 (7,3)=31 — CAPTURE (4,3),(5,3),(6,3)**: Triple row 3 recovery, walking from (7,3) left to friend (3,3).
- **M32 P2 (7,5)=47**: Build move; no capture available worth more.
- **M33 P1 (7,4)=39 — CAPTURE (4,4),(5,4),(6,4)**: Triple row 4. Final tally: P1 eff = 42.83 > 38.62 threshold. **P1 wins.**

Endgame: reached the stated threshold (42.83 > 38.62). No pass, no double-pass, no max-turn timeout.

### Game 2 — greedy mirror race

Move list: `18, 63, 26, 62, 34, 61, 42, 60, 50, 59, 49, 56, 41, 55, 33, 54, 25, 53, 17, 52, 43`

P1 opens (2,2), P2 plays opposite corner (7,7). Both then build dense vertical clusters with NO attempt at disruption (the driver picked purely by "maximise own threshold total plus diff"). **P1 wins at move 21** by threshold (41.71). No captures occurred the entire game — the two clusters simply raced.

Headline: **pure greedy play → first mover wins by exactly one tempo.**

### Game 3 — seat swap, P2 plays adjacent-contact opening

Move list: `27, 26, 35, 25, 43, 33, 42, 34, 51, 32, 50, 24, 49, 40, 41, 47, 59, 39, 58, 31, 57, 55, 3`

P1 plays (3,3); P2 plays (2,3) adjacent, attempting early disruption. Both then build. P2's adjacent opening actually anchored a strong left-edge cluster (column 0–1), but still couldn't catch up on tempo. P1 wins at move 23 with a clever (3,0) finishing move that uses torus wrap: (3,0) and (3,7) are adjacent on the torus, so the finishing placement touches both ends of P1's column-3 spine. P1 eff 41.32.

### Strategy guide — Player 1 (first mover)

1. Build a dense, square-ish cluster (3×3 or 3×4 maximises own/neighbour ratio).
2. Every placement should have at least one pre-existing friendly neighbour; solitary placements waste 0.75 × k in stacked influence.
3. In the threshold race, 2 compact placements ≈ +3.4 threshold; 12 well-connected stones will win.
4. Stay vigilant for enemy custodian setups. The danger signature is an enemy stone two cells from one of your friends on the same axis (e.g., P2 at (5,2) while you have (5,3),(5,4),(5,5)... wait, (5,5) mine and (5,2) enemy, (5,3),(5,4) between). If the enemy completes the bracket, you lose the stones between.
5. When behind on captures, look for your own "friendly end of a long enemy run" — those are 3–4 piece recoveries in a single stone. Game 1's M25 and M33 show these are possible.
6. Torus wrap finishes: a lone stone placed on the opposite side of your existing column (e.g., (3,0) when you already own (3,7)) closes an influence ring and pushes totals fast.

### Strategy guide — Player 2 (second mover)

1. **Greedy mirroring loses.** You are always one tempo behind; P1 crosses threshold first.
2. Introduce a contact move on turn 2 or 4. The purpose is not to capture today but to be the "friendly end" of a future custodian walk.
3. Target cell pattern `Enemy — Enemy — ... — My old stone` along an axis. Place at the open end to bracket. Single placements routinely capture 2–4 stones. See Game 1 M22 and M28.
4. Captures DROP both players' absolute totals, but they lower the opponent's more than yours when the captured cells had significant enemy +value. Net: favourable for trailing player.
5. Accept that capture-heavy play produces oscillating piece counts. Be prepared for the opponent's counter-capture on the next turn.
6. Custodian does not wrap on torus — do NOT plan a bracket that relies on crossing y=0/7 or x=0/7 boundaries.

### Endgame convergence
All three games reached the stated threshold condition. No double-pass resolutions, no max-turn timeouts. The threshold value (38.6) is well-calibrated — reachable in 10–15 compact placements, which matches training runs.

---

## PHASE 3 — STRATEGIC ANALYSIS (joint)

### Distinct viable strategies?
Two strategies are clearly identifiable:
- **Race / cluster strategy** (both players greedy, building isolated clusters).
- **Contact / custodian strategy** (play near enemy stones to set up captures).

In Game 2, both players played pure race; P1 won on tempo.
In Game 1, P2 switched to contact after move 16 and the game became a violent capture oscillation — but P1 still won because P1's capture opportunities were equally numerous and the tempo never flipped.
In Game 3, P2 opened with contact; P1 still won.

So: **there are two strategies, but one dominates (race from the first-mover seat).** Contact play is a real skill tree for Player 2, but it cannot overcome the tempo deficit when P1 also plays correctly.

### Meaningful counter-play?
Yes, at the tactical level. Every capture creates a counter-capture opportunity — the recaptures in Game 1 flowed both directions repeatedly. Tactical counter-play is strong and intricate.

At the strategic level, however, Player 2 has no discovered counter-plan that reliably upsets P1's tempo advantage.

### Short-term vs long-term tension?
Modestly yes. Captures are threshold-negative in absolute terms (you eat your own influence sum) but they are differential-positive when they knock the leader back. So capturing is a sacrifice of short-term threshold progress for medium-term delay. This is a real trade-off and it showed up in Games 1 and 2.

### Emergent concepts?
- **Tempo/initiative**: the game is fundamentally about who crosses 38.6 first. Every "wasted" move (capture that doesn't net positive differential) costs tempo.
- **Territory**: clusters behave like mini-territories. Value scales roughly with perimeter × density.
- **Influence ring**: because (x,0) and (x,7) are torus-adjacent, an 8-long column in one axis closes into a ring, packing extra stacked influence. Game 3 M23 exploited this.
- **Sandwich vs bracket**: custodian threat can be threatened for several moves before execution. Leaves a "pre-capture gradient" on the board that players must read.
- **Ko-lite behaviour**: mutual alternating captures of a single cell did not occur in our games (no super-ko rollback triggered), but the capture-recapture oscillation is reminiscent of a many-cell ko.

### Does topology matter?
Yes. Torus wrap in influence changes the calculus of corner/edge play (there are no corners). The non-wrapping custodian creates a paradox: a stone at (5,0) and (5,7) are influence-adjacent but cannot custodian-bracket through the wrap. This means placements near "the seam" behave asymmetrically depending on whether you're computing influence or planning a capture.

### First-mover advantage — quantified
- Game 1: P1 wins (turn 33, lots of captures both sides).
- Game 2: P1 wins (turn 21, no captures).
- Game 3 (P2 opening with contact): P1 wins (turn 23).

**3/3 P1 wins.** With the same reasoner in both seats, this is a strong signal that P1 has a structural tempo advantage. I estimate P1 win rate ≥ 70% under strong greedy play, possibly higher. Training data (0.5/0.5 split) doesn't disconfirm this strongly — those are PPO self-play totals and may undersample optimal greedy opens; note that one of the two training seeds terminated with end-winrate 0.86 for one side, not 0.50, suggesting the symmetry claim is soft.

Seat-identity caveat: same human-like reasoner. Triangulation by inter-team comparison is needed.

---

## PHASE 4 — NOVELTY ADVERSARY (MANDATORY)

### Adversary argument

**Claim**: this game is a blend of **Othello/Reversi** (custodian capture, alternating placement, axis brackets) and a weighted **Go-influence** scoring function, played on a torus. Neither ingredient is novel; the combination is a superficial mashup.

Specific rule correspondences:

(a) **Othello/Reversi**
- Axis-line bracket capture: identical. "Walk along collecting consecutive enemy cells; if walk ends on a friendly cell, flip all captured" is verbatim the Othello rule, minus the 8-direction (diagonals). Here only 4 axis directions are used (no diagonals on a von Neumann board), which is a degenerate subset.
- Placement on empty cells, alternating turns, no moves. All Othello.
- No constraint that placement must capture (that's the ONLY rule difference vs. Othello's "legal move must flip at least one stone"). This is a well-known simplification called "Free Othello" or "Anytime Reversi".

(b) **Go / territorial influence**
- The 1.874 × 0.4019^distance rule is a radial influence function indistinguishable from Chinese-style "influence" heuristics used by Go engines since the 1990s (CrazyStone, Zen, later AlphaGo's territory maps).
- Win-by-threshold-sum-over-own-cells is mathematically identical to "first to territory score T wins" — a well-known Go variant (Ing rules have a threshold; Japanese rules use area count).

(c) **Life-like CA check**
- No cellular automaton here. The "non-trivial CA entries" test is vacuous — classic mechanics only.

(d) **Simultaneous game check**
- Not applicable; alternating.

(e) **Topology transformation**
- The torus is just an 8×8 Othello board with wrap. Torus Othello has been studied (Schmittmann & Mertens have references in puzzle-game literature). The only genuinely new mechanic is **influence wraps but captures don't** — and that's a one-line asymmetry, not a new strategic universe.

(f) **"Expert at known game" test**
- An Othello expert would immediately understand the capture mechanics and the threat structure (XOX-bracket, wedge, quiet move).
- A Go player would recognise the territory/influence race and play compact shapes.
- Combine: a strong Reversi/Othello player with basic Go intuition (or just the ability to count influence) would be competitive within 5–10 games.

(g) **Rebrand hypothesis**
- "Othello on an 8×8 torus with 4-direction custodian and a Go-style territory win condition." — this is a one-sentence description in prior-art terms. The parameter values (1.874, 0.402, 38.6) are tuned numbers, not new mechanics.

Therefore the game is NOT novel. Novelty score argued: **2–3**.

### Rebuttal (Players 1 & 2 joint)

The adversary's argument is mostly correct on components but underrates the emergent dynamics. Concrete playthrough evidence:

1. **Captures are threshold-negative — not Othello-like.** In Othello, capturing stones is strictly positive (you gain area and you take stones from the opponent). Here, because `board_values` persist through flips, a capture DROPS your own threshold total in absolute terms. An Othello expert executing an "obvious flip" would be wrong about the sign of their move in some positions; our Game 1 M16 and M20 illustrate this directly. This emerges from the COMBINATION of custodian + influence; neither rule alone produces it. An Othello expert's intuition would mislead them.

2. **The double-capture trap via "friendly remnant" from a prior capture.** Game 1 M22: P2 places (4,2); the bracket closes at (4,5), which was P2-friendly only because of a capture two moves earlier. The capture-recapture chain compresses temporal state into spatial structure in a way Othello never has (Othello's capture state never "decays" — it's static). Tracking "where are my temporary outposts" is a distinct skill.

3. **Threshold race + territory = pace pressure.** Unlike Go (no time pressure) and Othello (territory determined at the end), this game ends abruptly when one side crosses 38.6. That makes TEMPO the primary resource. Every defensive capture that burns your own cluster value is a real sacrifice — not a feature of either parent game.

4. **Torus asymmetry (influence wraps / capture doesn't) creates genuinely novel positions.** Game 3 M23: P1 plays (3,0) to close a torus-wrap ring and swing own-sum past threshold. This exploits a board topology that no known Reversi or Go variant uses — classical Reversi on a torus exists but the influence-wrap/capture-no-wrap split is sui generis to this engine.

5. **Our own play encountered states an Othello expert would misjudge.** At M16, a naive Othello instinct says "capture 2 stones, great." Actual effect: own threshold drops 4 points and piece differential swings. Only by computing the 64-cell effective board did we correctly rank moves. That is not Othello.

The pure-mechanic reductionism of the adversary is missing the interaction term. The game is NOT "just Othello on a torus" any more than "chess with a 9×9 board" is a new game — but the extra win condition and the value-persistence during captures DO create meaningfully new tactical categories.

### Team novelty resolution: **4 / 10**.

The building blocks are well-known: custodian capture (Othello), influence field (Go), torus topology (many variants). The unique strategic interaction — capture-during-threshold-race with value-persistence — is real but modest. Strong Othello + Go players would adapt in hours, not weeks. The game is a reasonable hybrid but not a new genre.

Strongest adversary argument: "Othello + Go-influence on a torus." Accepted. Rebuttal: capture-sign inversion and threshold tempo create novel tactics, but not a fundamentally new strategic landscape.

---

## PHASE 5 — VERDICT

Team ID: team-3
Game ID: deb4dfe0382d
Rules Summary: Alternating placement on an 8×8 torus; Othello-style axis-bracket captures (no wrap); each placement spreads decaying ±influence to neighbours; win when own-cells' summed influence exceeds 38.62.
Topology: 8×8 torus (wraps on both axes)
Turn Structure: alternating (1 piece / turn)

### SCORES (1–10)

- **Strategic Depth: 6** — Two distinct skill trees (cluster race vs custodian tactics). Tempo management and capture-sign inversion create real choices. But the state is fully observable, the action space is small (65), and search depth rarely exceeds 3 ply in hand play. Mid-tier depth.
- **Emergent Complexity: 6** — Captures form chains and cascades (Game 1 saw 6 captures ≥2 stones in 10 turns). Value persistence creates "ghost influence" on captured cells, a non-obvious emergent rule. Torus+capture asymmetry produces genuine positional oddities. However, the emergence is within a well-understood framework; nothing truly novel like CA stripes or simultaneous equilibria.
- **Balance: 3** — **P1 wins 3/3 under strong play.** Seat-swap Game 3 kept P1 winning despite P2 playing an aggressive contact opening. Same reasoner caveat applies, but the tempo-based race has a structural first-mover bias that I could not find a P2 counter for. Training-run data shows 0.5/0.5 for seed 80066 but seed 81066 ended at 0.86 — not a strong symmetry claim. Needs a small komi (threshold differential for P2 ≈ 2–4) to restore balance.
- **Novelty (post-adversary): 4** — "Othello-flavoured territory race on a torus" largely captures it. The combination produces one clear new idea (capture is threshold-negative for the capturer) and one clear topology trick (influence-wrap / capture-no-wrap). Not nothing, but not new-genre.
- **Replayability: 5** — The mechanics reward practice. The cluster-shape decisions and capture-chain reading both improve with experience. But the dominant P1 path ("build a compact block and reach 38.6 first") will get solved by a strong engine in a short study.
- **Overall "Would I play this again?": 5** — Interesting once; interesting twice; after that, the structural imbalance dominates and it becomes an Othello-variant exercise.

### CLOSEST KNOWN-GAME ANALOG
**Torus Othello + Go-influence threshold.** Distinct because:
(i) captures retain prior-owner influence, causing capture-sign inversion;
(ii) torus asymmetry between influence (wraps) and custodian (doesn't) is an engine-level quirk rather than a published variant.
Not identical to either parent.

### KILLER FLAWS
- **First-mover advantage is large** (3/3 observed). No discovered symmetry-breaking rule (no komi, no pie rule). A strong P1 heuristic wins by pure cluster-build.
- **Custodian capture can destabilise** in the mid-game but resolves in favour of whoever was ahead on tempo — captures don't change the winner, just the move count.
- **Capture is threshold-negative in absolute terms**, which makes "free captures" a trap for novices. This is arguably interesting rather than a flaw, but it's also confusing and engine-level-specific.
- The **double-pass exploit is latent** but did not fire in our games — threshold is cheap to reach, so no one needs to pass.
- No **ko rule**: super-ko is in the engine and could rollback a loop, but we did not trigger it.

### BEST QUALITY
**Capture cascades across a torus board.** Game 1 turns 16–33 show eight 2–4-piece captures in 17 moves. This is visually and mechanically spectacular — the board churns between ownership patterns, and every move has calculable bracket-implications four directions × two senses = 8 potential captures to scan. That's a respectable tactical game.

### IMPROVEMENT IDEAS
One rule change that would materially improve balance: **reset `board_values` to 0 on captured cells when ownership flips.** This does two things: (i) removes the confusing "capture-is-negative" trap, making the game more readable, (ii) makes captures unambiguously good, which should help the trailing player recover tempo and reduce first-mover dominance. Alternatively: introduce a **pie rule** (P2 may swap after P1's first move), which is the standard fix for games with provable first-move bias.

---

## Engine-verification note
All 77 moves across 3 games were executed via `play_helper.py --action play --moves …`. Every capture was validated against both the rule and the rendered board. Best-move candidates at each turn were enumerated via direct `GameEngineV2` simulation of every legal action. No hand-reasoned moves went uncommitted without engine check.

## Seat-identity caveat
Both seats were played by the same reasoner. Game 3's seat swap reduces but does not eliminate the bias. The P1 3-0 sweep is internally consistent but should be triangulated against other teams' results before concluding P1 dominance is as strong as it looks here.
