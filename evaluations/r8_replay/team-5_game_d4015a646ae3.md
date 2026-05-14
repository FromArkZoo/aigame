# R8 Replay Agent-Team Eval — team-5 — Game d4015a646ae3

**Team ID:** team-5
**Game ID:** d4015a646ae3 ("Connection Go", R8 top-1 by ELO 2304.6, Feb-2026 rating 8/10, GE 0.386 / rank 6 of 12 in current calibration slate)
**Substrate:** flat 2D 8×8 grid (axis 8, 64 active cells / 64 grid positions, max_degree 4, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game d4015a646ae3 --db genesis_v2_run8.db` (see `briefing_r8_d4015a646ae3.md` for full rules and engine internals).

---

## Phase 1 — Rule Comprehension

**Board.** Flat 8×8 grid, 64 active cells, no holes. Cell index `c = y*8 + x`. 4 corners (deg-2), 24 edges (deg-3), 36 interior (deg-4). 8×8 is unusually narrow — diameter is small; a face-to-face chain is only 8 stones long.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = 100.

**Action space.** 65 actions = 64 placement + 1 pass. No pie rule, no move actions.

**Placement & capture.** Placement: any empty cell, no first-move restriction. Capture rule = **surround threshold=3**, but verified empirically that on this engine, "threshold=3" actually means **"all neighbors are enemy"** (i.e. fully-surrounded, like Go's no-liberty rule). My probes:
- Interior P1 at (3,3) with 3 P2 neighbors (3,2),(3,4),(2,3): no capture.
- Same P1 with the 4th neighbor (4,3) also P2: **capture fires.**
- Cascades work: P2 placing (2,0) captured `(0,0),(1,0),(0,1)` in one move — all three were fully surrounded post-placement.

So "threshold-3 surround" on this 8×8 grid behaves as **classical Go surround** (corners need 2 enemies, edges 3, interior 4). The "3" parameter appears to be vestigial or mis-mapped in this engine version.

**Propagation.** influence, r=3, strength=0.715, decay=0.751. ±0.715 self, ±0.537 at d=1, ±0.403 at d=2, ±0.303 at d=3. Footprint of one stone is a 25-cell taxicab-disk (clamped to board). On an 8×8 grid, two stones at opposite corners barely overlap in influence; a centre stone touches everything within 6×6 — quite global.

**Win condition.** Hex-style asymmetric **connection**: P1 connects top↔bottom (y=0 ↔ y=7) via a chain of P1 stones; P2 connects left↔right (x=0 ↔ x=7). BFS over the player's owned stones. The threshold=0.5 parameter is vestigial. Verified by sanity-play (8 P1 stones at x=0 wins; mirror 8 P2 stones at x=7 does NOT win).

**Pie rule.** Off. R8 predates pie.

**Degeneracy check.**
- The `threshold-race > 0.500` line printed by the helper is hardcoded and irrelevant — Done=True / Winner=N flags drive verdict.
- "Effective score" in the helper output is influence-pressure, not win condition. Useful as positional momentum only.
- Surround "threshold=3" is effectively threshold=N for a cell with N neighbors (i.e. full enclosure), per empirical test — a real soft violation: the rule advertises 3 but enforces full-degree.
- No pie rule → first-mover advantage is uncompensated. Critical for an 8-stone-diameter board (see balance).

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run20_helper.py`. Action IDs = cell indices for placement; pass = 64.

### Game 1 — P1 race-to-wall (mid-board column), P2 mirrors vertically (wrong-axis)

Sequence: `27,28,19,20,11,12,3,4,35,36,43,44,51,52,59` (15 plies, **P1 wins at move 15**, no captures).

Plot:
- P1 builds x=3 column (y=3,2,1,0,4,5,6,7).
- P2 mirrors x=4 column (vertical wall).
- Move 15: P1 places (3,7), completing top↔bottom chain. P1 wins.
- P2's "mirror" strategy is **structurally wrong** — P2 needs left↔right, not top↔bottom. P2 has built an 7-stone vertical wall that contributes only to influence, not the win condition.

Reflection: This is the canonical race. P1's column = 8 stones; P2's row would need 8 stones. P1 moves first, so on alternation P1 fits move-numbers 1,3,5,7,9,11,13,15 = 8 plies; P2 fits 2,4,...,14 = 7 plies. **P1 wins by parity alone, with no defence available**, *provided* P2 cooperates by not building correctly. But even when P2 plays the right axis (Game 4 below), the parity still holds.

### Game 2 — P1 vertical x=3, P2 horizontal y=3 (correct axes, head-to-head race)

Sequence: `27,24,19,25,11,26,3,28,35,29,43,30,51,31,59` (15 plies, **P1 wins at move 15**, no captures).

Plot:
- P1 builds x=3 column at y=3,2,1,0,4,5,6,7. P2 builds y=3 row at x=0,1,2,4,5,6,7.
- They share cell (3,3) — and P1 got there first (move 1). So P2's row is broken in the middle by P1's stone.
- P2 cannot complete left↔right while (3,3) is P1's; P2 would need to capture (3,3). But (3,3)'s neighbors after move 4 include P1 stones at (3,2) — already non-capturable. **P2 has lost by move 1.**

Reflection: **The central cell is a "vault" — whoever takes it dictates the game.** P1 always takes it. This is *more* lopsided than vanilla Hex on an 8×8 because the connection diameter is so short that the central cell is on every minimum-length path. P1 wins by exactly 1 move (15 plies vs 16 P2 would need).

### Game 3 — Adversarial probe: surround-capture stress, edge-walking, parity check

Sequence: `8,1,9,17,10,11,16,2,24,25,32,33,40,41,48,49,56,3,0` (19 plies, **P1 wins at move 19**, no captures despite P2 attempts).

Plot:
- P1 builds x=0 column (y=1 first since y=0 is contested by P2 stones at (1,0),(2,0)).
- P2 systematically attacks: places (1,0), (2,0), (1,2),(1,3),...,(1,6) → shadows x=1.
- P1's chain at (0,1)..(0,7) stones each have only 2-3 neighbors (edge cells). P1's (0,1) neighbors: (0,0)=., (1,1)=X, (0,2)=X — only 1 enemy contact possible.
- For P2 to capture any P1 stone, P2 needs to enclose it. But each enclosure costs P2 ≥ degree-of-cell plies, during which P1 extends faster. **Capture mid-build is tempo-suicidal.**
- Move 19: P1 places (0,0), closing chain to y=0. Connection complete.

Reflection: **Chain stability dominates.** Once a P1 chain has formed, mid-chain stones have 2+ P1 neighbors and are immune to surround. Only the un-extended tip is theoretically capturable, but it costs P2 too many plies to do so. **Surround capture in this game is a paper threat** — it exists in the rules but never fires under realistic play in a 15-move game.

Across all four games I played, **captures fired in 0 of 4 strategic games** and only in artificial probes where I deliberately staged the capture. PPO's training data (avg 72.5-ply games) may differ, but at agent-team-play depth, captures are inert.

### Strategy guides

**P1 (offence — column race):** Take centre cell (3,3) or (4,4) move 1. Build column toward whichever face is closer, then back-fill the other side. Game ends in 15 plies. There is no decision tree — every game plays out identically. **A trained PPO and a 6-year-old human win the same way.**

**P2 (defence + counter-race):** Build the orthogonal row. You will lose by 1 ply if both sides race optimally. Your only winning theory: hope P1 wastes plies on captures or influence. Empirically, P1 never needs to. **P2 has no winning strategy without pie rule.**

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** **No.** I observed exactly one strategy: take centre, build your axis-aligned chain, win. Every viable game collapses to this. The "two-pronged" or "double-threat" Hex strategies that make 11×11 Hex deep do not appear at 8×8 — the board is too small for parallel threats.

**Counter-play.** **Essentially absent.** P2 has no winning line against optimal P1. The closest to counter-play is P2 attempting to **occupy P1's intended column**, but this just forces P1 to switch columns and pay 1 extra ply. P1 still wins.

**Short-term vs long-term.** Game-length 15-19 plies → effectively no long-term planning. Every move is tactically forced: "extend chain, or block opponent's chain centroid." Strategic horizon ≈ 3 plies. R8 era PPO trained for 1.44M steps; my analysis suggests most of that was learning the trivial "extend axis" policy.

**Emergent concepts observed.**
- **Centre vault** — cell (3,3) or (4,4) is structurally a must-take for P1; whoever gets it dictates the row/column it sits on.
- **Influence is irrelevant for winning** — every game I played ended via connection, with the helper's "effective score" being a rough proxy for nothing meaningful.
- **Surround capture is inert under realistic play** — fires in 0/4 of my non-staged games; tempo cost exceeds benefit.
- **Parity = first-mover advantage on a small board** — the 8-stone chain length × alternating turns means P1 wins by exactly 1 ply on a head-to-head race.

**Does the 8×8 grid matter?** Yes, **negatively**. Standard Hex is played on 11×11 with hex topology (degree-6) and pie rule. Reducing to 8×8 squares (degree-4) gives:
- Shorter diameter (8 vs 11) — fewer plies needed, less room for strategic shape.
- Fewer connection routes per stone (4 vs 6) — single-blocker stops a chain more effectively, BUT also lets P1 race more cleanly.
- The grid topology + no pie + 8-stone chain = **unbreakable P1 win.**

A 13×13 or 16×16 board would let captures and influence matter; 8×8 strips them out.

**Does the propagation kernel matter?** Almost not at all for win-detection. r=3 with decay 0.75 means a centre stone touches ~25 cells with non-trivial influence — but influence has zero gating effect on the connection BFS. The kernel might shape PPO's learned policy (it sees `board_values` in the observation), but to a human/agent-team player it is dead code. **Influence is a vestigial decoration**, not a mechanic.

**Capture-rule contribution.** **None observed.** Captures require full enclosure (verified empirically, ignoring the misleading "threshold=3" label). On a chain-building game where players extend by 1 stone per turn, building an enclosure costs 3+ tempi while the opponent extends by 3+ stones. Capture only fires when the defender has *already* lost positionally; it cannot reverse a game. In 4 strategic games, captures fired 0 times.

**First-mover advantage / seat balance.** **Catastrophically unbalanced.** No pie rule. 8-stone chain + alternating turns + first-move = P1 wins by exactly 1 ply on any head-to-head race. R8-era PPO 0.84/0.56 win-rate vs random reflects training noise and the fact that 1.44M steps wasn't enough to fully learn the trivial winning policy — not balance. **Under optimal play, P1 wins ~100%.**

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a **re-skin of Hex** on an 8×8 square grid, with vestigial surround capture and inert influence propagation.

(a) **Threshold-race influence games** are irrelevant here — the threshold is vestigial. The actual win is **connection**, which is **Hex's defining mechanic**.

(b) **Surround capture** is Go-derived (and the "threshold=3" implementation actually behaves as classical Go "no-liberties capture"), but as shown in Phase 3, it never fires in realistic play. So this layer adds **zero** to the game's strategic content. A pure-Hex version with no captures would play identically.

(c) **The combination "Hex + Go-surround + influence-deposit"** is novel as a *rule listing*, but functionally degenerate — the Go and influence parts are decorations that the connection-race never triggers. The *experienced* game is just Hex.

(d) **8×8 square grid substrate.** Hex is canonically played on rhombus 11×11 hexagonal. The square-grid variant (degree 4 instead of 6) is **strictly worse** — fewer routes, more single-blocker leverage. The narrow 8-axis adds further degeneracy: chain length = board width, so the racing player always finishes one ply ahead.

(e) **Expert-transfer test.** A Hex player understands this game in **30 seconds** ("Hex on squares, ignore the Go decoration"). The "novel" piece — captures + influence — is irrelevant to play. Net new content learned: zero.

**Closest known-game analogue:** **8×8 square-grid Hex without pie rule.** Inside Genesis: this game is closest to R8 sibling games using connection-win on flat grid. The Hex backbone is the defining substrate; the Go-surround and influence are silt on top.

**Comparison to R8's own 8/10 rating.** This *is* the R8 game rated 8/10 in February 2026. The R8 rubric must have been crediting:
- The clever rule *combination* on paper (which on play turns out to be inert decoration).
- The connection-win novelty *relative to* the surrounding R8 corpus (most of R8 used threshold-race; connection was rare and felt fresh).
- The high ELO (2304.6 top-1), reflecting intra-R8 dominance — but that's a comparative metric, not absolute quality.

Under the **R20 protocol**, none of these credits transfer. R20 rates absolute quality: balance, depth, replayability, novelty post-adversary. This game fails all four:
- Balance: P1 wins always. **Fail.**
- Depth: 3-ply horizon. **Fail.**
- Replayability: every game plays out the same. **Fail.**
- Novelty post-adversary: it's Hex, with two inert decorations. **Fail.**

The 8/10 rating was almost certainly inflated by (i) absence of pie rule in the rubric's balance check, and (ii) crediting nominal-rule novelty without playing through to confirm the decorations actually fire.

**Comparison to R19 best.** R19 menger top-1 `1f9191b5d4e6` (4.8/10) had genuine outnumber-2 captures firing every few moves. R19 production mean 4.375. **This game has no firing mechanics beyond the connection BFS.** Strictly thinner than R19 menger top. About on par with R19 production mean only because Hex-as-substrate is a respectable backbone — but you could replace this exact ruleset with a pure 8×8 Hex implementation and lose nothing.

**Player rebuttal (P1 + P2).**
- The connection-win on asymmetric goals **is** strategically rich at correct board sizes (11×11 Hex with pie is a famously deep game). The Hex backbone is real strategic infrastructure.
- The pie rule's absence + the 8-stone diameter destroys that depth completely — the game becomes a parity countdown.
- The Go-surround and influence-propagation rules **do not contribute** under realistic play. They are decorations the engine carries but the agent never invokes.
- The "novel rule combination" argument fails the "expert-transfer test": a Hex player learns nothing new here.

**Novelty score (post-adversary): 2/10.** This is a re-skin of Hex with two non-firing decorations on a sub-optimal substrate. Above pure clone (1) only because the engine *would* let surround capture and influence fire if the board were larger and the diameter longer. Below "rule-combination novelty" (4-5) because the combination doesn't change observed play. Anchors: R17 mean 3.50 (this is below); R8's own 8/10 (this rejects); R19 menger top 4.8 (this is well below).

---

## Phase 5 — Verdict

**Team ID:** team-5
**Game ID:** d4015a646ae3
**Rules Summary:** On a flat 8×8 grid with no pie rule, alternating placement with Go-style surround capture (engine actually requires full enclosure despite the "threshold=3" label) and r=3 influence propagation; the first player to form a Hex-style top↔bottom (P1) or left↔right (P2) chain wins. In practice the game is Hex on squares without pie, and the Go and influence layers never fire.
**Substrate:** flat 8×8 grid, 64/64 cells (no holes), max_degree 4, pie_rule=False.
**Turn Structure:** alternating, 1 piece per turn.
**Hybrid actions:** no (place-only).
**Soft violations flagged:**
- Surround "threshold=3" is mis-labeled — engine enforces full-degree (4 enemies needed at interior cells, 3 at edges, 2 at corners). True threshold ≈ degree, not 3.
- Helper's `Win: threshold-race > 0.500` header is hardcoded and wrong (acknowledged in briefing).
- `win_condition.threshold: 0.5` field is vestigial under connection-win.

### Scores (1–10)

- **Strategic Depth: 3** — 3-ply tactical horizon. One viable plan: take centre, race your axis. No long-term planning. The Hex backbone *could* give depth at 11×11+pie, but 8×8 without pie collapses to a parity countdown. Engine-measured 0.545 strategic-depth is generous — subjective depth is far lower.
- **Emergent Complexity: 2** — Centre-vault is the only emergent concept I named, and it's a direct consequence of asymmetric-goal + short-diameter geometry. No multi-step tactics arise. Influence and capture rules never fire in real play, so their "emergent" interactions are theoretical only.
- **Balance: 2** — Catastrophically unbalanced. No pie rule + 8-stone chain length + alternating turns = P1 wins by 1 ply on any head-to-head race. PPO 0.84/0.56 win-rates reflect undertrained agents, not actual balance. Under optimal play P1 wins ~100%.
- **Novelty (post-adversary): 2** — Re-skin of Hex on a square grid with two inert decorations. See Phase 4. Below R17 mean.
- **Replayability: 2** — Every game collapses to the same sequence: P1 builds an axis-aligned chain through the centre, wins in 15-19 plies. No meaningful position variety from move 1. Opening tree is ~4 cells (the 4 central cells), all equivalent by symmetry. There is no reason to play this twice.
- **Overall "Would an agent team play this again?": 3** — Above absolute floor because the Hex backbone is genuine strategic infrastructure (just deployed at the wrong scale), and the rule listing is interesting on paper. But once played, the game offers nothing: the decorations don't fire, the balance is broken, the depth is shallow. I would not voluntarily play another game. **Far below the Feb-2026 8/10 rating.** Lines up with R17 mean (3.50) and below R20 production mean (3.73).

### CLOSEST KNOWN-GAME ANALOG
**Hex on an 8×8 square grid without pie rule.** Inside the broader board-game literature: structurally identical to "Bridg-It" or other square-grid connection games, which are well-known to be solved/trivial at small board sizes. Inside Genesis: R8 sibling connection-win games on flat grid; the surround + influence decorations are inherited from R8's parent line but don't add subjective game content.

### KILLER FLAWS
- **No pie rule + 8-stone chain length = P1 wins by parity.** Verified across 4 independent games. P2 has no winning line under optimal play. This is structural, not a tuning issue.
- **Surround capture never fires in realistic play.** 0 captures across 4 strategic games (only fired in artificial probes I staged). The tempo cost of building an enclosure exceeds the value of the captured stone; meanwhile the chain extends past the capture attempt. Capture is paper-only.
- **Influence propagation is vestigial.** Connection win ignores `board_values`; the influence kernel only matters for PPO's observation, never for the actual win. A player needs to learn zero about influence to win — the kernel is dead weight from a player's perspective.
- **Surround "threshold=3" is mis-labeled.** Empirically requires full enclosure (degree-many enemies). A rule the player can't trust at face value is a quality flaw on top of the inert-mechanics flaw.
- **Centre cell decides the game on move 1.** No meaningful opening choice; (3,3) and (4,4) are equivalent and one of them is always best for P1.
- **No fallback rule for max_turn timeout.** Briefing notes: "if neither side connects in 100 plies, game ends without winner (draw)." Fine in theory, but under the trivial race strategy nobody ever reaches turn 100; this means the timeout rule is also vestigial.

### BEST QUALITY
**The Hex backbone is real.** Asymmetric face-connection goals are a deep idea, and the engine implements them correctly (BFS over the player's own stones; cross-axis goals on a single shared cell). If the same ruleset were ported to an 11×11 board with pie rule, this would be Hex — a known excellent game. The Feb-2026 rating was almost certainly responding to this Hex *potential* rather than the deployed play experience. **The crown jewel is the win condition; the flaw is everything around it failing to develop it.**

### 8×8 GRID STRUCTURAL CONTRIBUTION
**Negative.** The 8×8 square grid is the wrong substrate for a connection game. Hex uses 11×11 hex topology (degree 6 + pie) precisely because:
1. Hex topology has no "ladder break" — no two stones can be cross-axis blocked simultaneously.
2. 11×11 diameter is long enough that pie can balance first-mover.
3. Degree-6 lets multiple parallel threats co-exist; degree-4 makes single-blocker work.

8×8 squares strip all three properties. R19's finding that menger > carpet > grid for substrate quality applies here too: grid is the dullest possible substrate; combined with no pie + short diameter, it produces a degenerate Hex.

### IMPROVEMENT IDEAS
**Single best change:** **Add the pie rule.** This is the canonical Hex-balance fix and would address the catastrophic P1-wins-by-parity flaw with one line of rule change. R20+ corpus universally has pie; R8 omitted it. With pie alone, this game becomes a respectable miniature Hex — probably 5/10.

Secondary improvements:
- **Increase axis to 11 or 13.** Longer diameter gives room for two-pronged threats and ladder racing, which a 5-ply Hex player understands well. Combined with pie, would push toward 6/10.
- **Drop the surround capture and influence rules.** They are vestigial. Cleaner rules listing = better expert-transfer. The game *is* Hex; admit it.
- **Or, conversely: make the surround capture matter.** Lower the threshold to 2 (capture on outnumbering by 2 friendlies), so that captures actually fire mid-chain and add real tactical decisions. But this would change the game's identity entirely — it'd no longer be "Hex with decorations" but "Hex/Go hybrid."
- **For the fitness function:** This game's GE 0.386 / rank 6 of 12 (current calibration slate) probably *over-rewards* this game by giving rule-listing credit for the inert surround + influence layers. A fitness function that scored only on rules-that-fire-in-play would correctly demote this. The historical 8/10 was likely calibrated against the rule listing, not the play experience.

### Calibration takeaway

The February-2026 8/10 rating does not survive the R20 protocol. I score this game **3/10** overall — below R20 production mean (3.73), well below R19 menger top (4.8), and ≈ 5 points below the historical anchor. This is consistent with branch outcome #2 ("February rating was inflated; calibration drifted up"), but I cannot judge the cross-team spread alone. If the other 4 teams converge around 3-5/10, the anchor has drifted by ~4 points and R21 with `w_planning=0` is the correct response. If teams spread 2-8/10, the agent-eval itself is unstable and needs methodology rework before fitness redesign.

My read: the legendary 8/10 was paid for by the Hex backbone (a real asset) plus generous credit for nominal rule complexity that doesn't fire in play. Under a play-the-game-and-score-what-you-see rubric, that credit evaporates.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/r8_replay/team-5_game_d4015a646ae3.md`.*
