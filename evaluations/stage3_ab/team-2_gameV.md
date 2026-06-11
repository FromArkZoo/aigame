# Stage 3 blind eval — team-2 — Game V

**Team ID:** team-2
**Game Label:** V (blind; do not consult `.blind_mapping.json`)
**Substrate:** hex_rhombus (axial triangular lattice), axis 22, 484 total cells / 484 active, max_degree 6.
**Evaluator:** single-agent team running both player roles and Novelty Adversary sequentially.
**Helper:** `evaluations/stage3_ab/play.py --game V` (run `--rules` first; `--control` for influence map).

---

## Phase 1 — Rule Comprehension

**Rules derivation.** Derived entirely from `play.py --game V --rules` and observed engine behaviour.

**Board.** Hex-adjacency rhombus, axis 22 (484 cells, all active). Axial (q, r); cell index = q + 22*r; rows sheared (row r shifts right by r). Neighbour set: standard axial hex {(±1,0),(0,±1),(+1,−1),(−1,+1)}. Interior degree 6; acute corner (0,0) degree 2.

**Turn structure.** Alternating, 1 stone/turn. Max_turns = 200 (timeout).

**Action space.** 486 actions = 484 placement (0..483) + pass (484) + pie_swap (485). Placement legal at any empty cell.

**Placement & capture.** Capture rule = **influence-flip (conversion)**. After each placement, EVERY enemy stone standing on a cell now dominated by the active player's influence is CONVERTED to the active player's colour. Conversions cascade: each flip swings that cell's field by ±2.0 and can trigger further flips in the same turn. Same radius/strength/decay as propagation. Verified thresholds: a lone enemy stone (own field −1.0) flips when ≥3 of its 6 neighbours are yours (3·0.5 = +1.5 ⇒ net +0.5 > 0). A stone with friendly neighbours of its own resists (each friendly neighbour adds ∓0.5/∓0.25 support, raising the bar to 4+ enemy stones). Verified cascade: flanking a 3-stone enemy row converted all three at once.

**Propagation.** Influence field radius=2, strength=1.0, decay=0.5; P1 +, P2 −; clamped [−100,100]. Lone interior stone controls a 19-cell hexagon (sheared tips). Identical kernel to the propagation used by the capture check.

**Win condition(s).** Influence-field connection (IDENTICAL to the standard here). P1-controlled if board_values > 0, P2 if < 0, else contested. **P1 connects r=0↔r=21; P2 connects q=0↔q=21**, checked after each placement. Same CRITICAL property observed: the win-graph excludes the pure-horizontal (q±1, r) step. A fully P2-controlled flat row does not win; P1's vertical thread conducts through horizontal squeezes. ⇒ P2's axis is structurally harder (needs a ≥2-row staircase).

**Pie rule.** ON. After P1's first stone, P2 may swap (485): inherits the stone, move passes to P1. Verified.

**Komi_p2.** 0.0 (timeout tiebreak only).

**Degeneracy check.**
- **Display/win mismatch (soft violation):** same as the standard — the `--control` map prints "−"/"+" by sign of field, but the win-graph drops horizontal adjacency, so a visually-complete controlled row is not a win. Misleading feedback.
- **Flip volatility:** capture is now LIVE and frequent. Thin/isolated connection stones are removable for ~3 enemy stones (verified: an isolated spacing-4 column stone flipped away). This is a feature (Othello/Ataxx swings) but introduces real instability; building requires solid, mutually-supporting groups.
- No non-termination: cascades resolve deterministically within a placement; timeout count rule guarantees an end. No infinite loop observed; cross-turn flip/re-flip ping-pong is possible but bounded by the 200-turn count rule.
- Acute-corner degree-2 quirk present (matters less here — flips, not surround, are the live mechanic).

---

## Phase 2 — Strategic Play (both roles)

All moves engine-verified through `play.py --game V`. Action IDs = q + 22*r; pass=484; swap=485.

### Game 1 — as Player 1 (P1 WINS)
Sequence: `184,181,250,187,118,178,316,190,52,196,382,404,383,405,426,449,448,471,470` (winner=1; P1 controlled-count 98).
Plot: same central-spine plan as the standard, but note the FLIP payoff — P2's bottom-edge cutting stones (404,405,426) sat adjacent to P1's **solid doubled descent** (382+383, 448+449). Because the descent was solid (mutual support), P1's influence dominated those cells and P2's cutters were CONVERTED to P1 (final P1=98 vs 91 in the surround-variant line). Cutting a solid group literally backfired — the cut stones became my connection. P1 linked r=0↔r=21.
Reflection: binding constraint = **play solid**. In V, thin spines get flipped apart; thick spines flip the attacker. Tempo + the easier axis + flip-backfire made the P1 seat feel comfortably winning.

### Game 2 — as Player 2 (the P2 handicap, with a flip tool)
Sequences:
- Flip-disruption line: `52,206,140,250,228,227,272,484,360,484,448,484` — as P2 I flipped P1's just-placed mid-column stone (8,10) by pre-surrounding it (206,250,227); P1's column broke and even after rerouting P1 stalled at largest-component 42 (though still leading on raw count 76–24).
- Isolated-stone flip proof: `140,118,484,162,484,139` — P1's lone (8,6) converted to P2 (P1→0).
Plot: V hands P2 a genuine weapon X lacks — I can DISSOLVE P1's connection by flipping thin links, forcing P1 to spend tempo playing thick. But my own win remained blocked by the directional asymmetry: a solid P1 spine cannot be flipped (mutual support) and still pinches my row to a non-conducting flat line. So I could harass effectively yet rarely convert to a P2 connection; my realistic plan was disruption + timeout count.
Reflection: the pie swap (tested: P1 centre → P2 swap claims the stone, move to P1) again fixes only tempo. Flips make P2 more ACTIVE than in the surround variant, but do not cure the harder axis.

### Game 3 — Adversarial / novelty-stress (flip/cascade stress)
Sequences: cluster cascade `206,228,208,229,251,230,209,484,252,484,250,484,231` (a 3-stone P2 row entirely converted to P1); lone flip `231,230,229,484,252` (one P2 stone flipped by 3 P1 neighbours); reverse flip `184,162,484,206,484,185` (a P1 stone flipped by 3 P2 stones).
Plot: I stress-tested the conversion engine. Flips are symmetric, threshold-based (≥3 unsupported neighbours), and cascade simultaneously across clusters. They reward LOCAL MATERIAL SUPERIORITY and punish overextension — an Othello/Ataxx layer grafted onto the Hex race. No oscillation or crash; swings were large but deterministic and position-driven, not random.

### Strategy guides
**As Player 1:** Build a SOLID vertical spine (spacing ≤2 so stones support each other). Let P2 attack it — adjacent attackers on a solid group get flipped into your colour, advancing your connection for free. Take the centre, win on tempo + the easier axis.
**As Player 2:** Use flips as your main weapon: pre-surround P1's thin links to convert them, forcing P1 thick and slow. Keep your own groups solid (avoid donating flips). Anchor walls edge-to-edge. Play for disruption + a timeout count lead; outright connection is hard.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Yes, and more textured than the surround variant: P1 = solid spine + flip-backfire; P2 = flip-harassment + thick staircase. Both roles have live, distinct playbooks; P1's remains stronger.
**Counter-play.** Strong and dynamic. Connection ↔ capture are now intertwined: blocking with thin stones risks conversion; defending = playing solid; attacking solid groups = donating material. Cascades enable sacrifice/bait tactics absent from X.
**Short-term vs long-term.** Sharper tactics than the surround variant (every close contact can swing via a flip) layered on the same medium-horizon race. 22×22 supports long horizons; flips add a faster tactical clock on top.
**Emergent concepts observed.** Influence-blob connections; Othello-style cluster conversion and cascades; solid-vs-thin material tension; cutter-backfire; bait-and-reflip swings; flank-anchored walls; tempo.
**Does hex_rhombus topology matter?** Yes for both the blob shape AND the flip threshold (6 neighbours ⇒ 3-to-flip rule, 4+ to flip a supported stone). On a square grid the conversion arithmetic and staircase change; the flavour is more lattice-dependent here than in X.
**Does the propagation kernel matter?** Critically — the SAME kernel drives both control and conversion, so radius/decay set connection thickness AND flip thresholds simultaneously. Not decorative in any sense.
**Capture-rule contribution.** LARGE — this is the variant's whole identity. Flips fired routinely in close combat, dissolved thin connections, converted clusters, and made "attack a solid group" self-defeating. Night-and-day vs the inert surround capture of the other variant.
**First-mover advantage / seat balance.** Still P1-favored (own-the-crossing + easier axis). Flips give P2 a disruption tool that narrows P1's margin but does not flip the seat balance; pie corrects tempo only.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a re-skin of **Hex × Othello/Ataxx**. Argument:
(a) Edge-to-edge connection win = Hex exactly.
(b) The capture is field-dominance conversion = Othello/Reversi flip logic (and the cascade is pure Reversi), with an Ataxx "convert adjacent enemies" feel; the radius-2 field just makes the flip condition fuzzy rather than line-of-flanking.
(c) "Influence-dominance conversion + influence propagation + edge-to-edge connection" — I know of no published game that fuses Reversi-style conversion with a Hex connection goal on a hex influence field; the components are old but this specific fusion is not obviously prior, and it is more than the sum (cutter-backfire, solid-vs-thin) emerges.
(d) Substrate: same 22×22 hex-rhombus as the corpus's recent work but flatter/larger than R17–R21's menger/carpet/grid; the lattice does carry weight here via the flip arithmetic.
(e) Expert transfer: a Hex+Othello player gets the core in ~15 min; the irreducible novel piece is that CONNECTION stones are continuously convertible territory — your wall is never safe, your opponent's wall is always a takeover target.

**Closest known-game analogue:** Hex crossed with Reversi/Ataxx — "connection Hex where stones flip like Othello discs."
**Comparison to R8 Connection Go (replay anchor 4.10).** Same connection family; here the capture is far more load-bearing than R8's and creates swingier play. Comparable-to-slightly-richer depth, with more volatility.
**Comparison to R19/R20/R21 best.** Richer in emergent tactics than R21 (3.69) and arguably than R20-mean; below R19's 5.0 ceiling because the spine is still Hex and the directional imbalance + flip volatility cap it. The live capture is its edge over the surround sibling.

**Novelty score (post-adversary):** **4.5**/10. Above re-skin (2–3) because the Reversi-conversion-on-a-Hex-connection fusion produces genuinely new tactics (cutter-backfire, solid-vs-thin, cascades); below genuinely-novel (8–9) because both parents are famous and the connection skeleton is Hex. Anchors: R17 3.50, R8 4.10, R19 4.8/5.0, R20 4.80, R21 3.69.

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game Label:** V
**Rules Summary:** Hex-connection on a 22×22 hex rhombus where stones paint radius-2 influence blobs AND flip like Othello discs — win by linking your two edges while converting enemy stones caught in your dominant influence (cascades included).
**Substrate:** hex_rhombus, axis 22, 484/484 cells, max_degree 6, pie_rule=ON, komi_p2=0.0.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only; pass + pie-swap available)
**Soft violations flagged:** control-map/win-detection mismatch (full-looking controlled row is not a win); flip-induced instability of thin connections (feature with a volatility cost).

### Per-role sub-scores (1–10)

**As Player 1:**
- Strategic Depth: 5 — solid-spine construction, flip-backfire exploitation, crossing/route/tempo choices.
- Emergent Complexity: 5 — Hex bridges/cuts PLUS Othello cascades, cutter-backfire, bait-and-reflip.
- Replayability: 4 — flip tactics add opening/midgame variety beyond the standard spine.

**As Player 2:**
- Strategic Depth: 4 — active flip-harassment is real, but conversion to a P2 win is rare on the harder axis.
- Emergent Complexity: 5 — same rich conversion dynamics from the disrupting side.
- Replayability: 3 — directional handicap + misleading win feedback still bound the seat.

### Role-averaged scores (1–10)

- **Strategic Depth: 4.5** — connection race plus a live conversion layer; meaningful decisions both seats.
- **Emergent Complexity: 5.0** — cascades, cutter-backfire, solid-vs-thin material tension arise from one flip rule.
- **Balance: 3** — same P1 directional lean as the sibling; flips arm P2 but don't fix the axis; pie corrects tempo only.
- **Novelty (post-adversary): 4.5** — see Phase 4; Hex × Othello/Ataxx fusion.
- **Replayability: 4.0** — flip volatility broadens the tactical tree.
- **Overall "Would an agent team play this again?": 4.2** — the live conversion mechanic makes this the more engaging of the pair and lifts it above R8/R21; held below the R19 ceiling by the unfixed P1 lean, the win-feedback wart, and swing-heavy instability. Anchors: R8 4.10, R19 4.375/4.8/5.0, R20 3.73/4.80, R21 3.69.

### Fairness perception (mandatory)

**Fairness perception: 2 — P1-favored: identical win-graph asymmetry to its sibling (a full P2 row does not connect, a squeezed P1 spine does), and although flips let P2 harass, a solid P1 spine is flip-proof and still pinches P2's row dead; pie fixes only tempo.**

### CLOSEST KNOWN-GAME ANALOG
Inside the corpus: R8 Connection Go (connection + capture + influence), but with a far more active capture. In the literature: Hex crossed with Reversi/Ataxx (Othello-style conversion driving a connection race).

### KILLER FLAWS
- Structural P1 advantage in the win-connectivity graph (horizontal step excluded), un-fixed by the pie rule — shared with the sibling.
- Flip volatility makes thin connections unstable; combined with the control-map/win mismatch, a player can be misled about both who owns a region AND whether they've won.

### BEST QUALITY
**Cutter-backfire:** attacking a solid connection with adjacent stones converts those stones into the defender's colour, fusing the capture and connection mechanics into one elegant idea. The Othello-style cascade on a Hex spine is the crown jewel and is what separates this game from its inert-capture sibling.

### HEX_RHOMBUS STRUCTURAL CONTRIBUTION
The degree-6 lattice shapes BOTH the connection blob and the conversion arithmetic (3-to-flip / 4-to-flip-supported), so topology is more load-bearing here than in the surround variant — a square grid would change the flip math and the staircase. Still no menger>carpet topology dividend (R19), but the 22×22 size plus the flip layer give longer and busier games than R21's 9×9.

### IMPROVEMENT IDEAS
**Single best change:** fix the win-connectivity graph to the full hex 6-neighbourhood so P1 and P2 are symmetric, leaving the pie rule as the sole balancer — this removes the structural P1 edge and the control-map lie while keeping the (genuinely good) flip mechanic intact.
Secondary:
- Damp flip volatility slightly (e.g., require strict field margin or cap cascade depth) so connections aren't quite so fragile, preserving Othello swings without chaos.
- Render the control map per the actual win-graph (or annotate non-conducting regions) to end the feedback mismatch.

---

## Cross-game comparison (assigned games: V and X)

**Ranking of your assigned games by Overall score:** V = 4.2, X = 4.0. (Both share the same board, connection win, pie rule, komi and timeout; they differ ONLY in the capture rule.)
**Which game would you most want to play again?** **V**, by **+0.2 Overall**.
**By how many Overall points above the next-ranked game?** +0.2 Overall (V 4.2 vs X 4.0).
**Key differentiator:** the **capture rule**. X's surround (Go) capture is effectively vestigial in connection play — it costs 6 stones to take one interior stone, so it almost never fires and rerouting is always cheaper. V's influence-flip (Reversi/Ataxx) capture is LIVE and central: it converts enemy stones caught in your dominant field, cascades across clusters, dissolves thin connections, and makes attacking a solid group backfire into the attacker's loss. That single change turns an inert "fat-stroke Hex" into a swingy Hex × Othello hybrid with materially more emergent tactics and novelty — at the cost of added volatility. Note the shared ceiling: both inherit the same structural P1 advantage (the win-graph excludes the horizontal step) that the pie rule does not correct, which is why neither clears the mid-4 range.

---

*Output saved to `evaluations/stage3_ab/team-2_gameV.md`.*
