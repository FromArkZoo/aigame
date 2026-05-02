# Run 19 Evaluation — team-pilot — Game ce3a09e05cef

**Team ID:** team-pilot
**Game ID:** `ce3a09e05cef` (Carpet rank-1, GE 0.3547, ELO 2280.5)
**Substrate:** Sierpinski carpet (axis 9, 64 active cells / 81 grid positions, max_degree 4)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game ce3a09e05cef`
**Soft violation:** `sierpinski_threshold_inert` (flagged in rule blob).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9 grid with 17 inactive holes per the level-2 Sierpinski carpet pattern: a central 3×3 hole at (3..5, 3..5), and four 1×1 corner holes at (1,1), (4,1), (7,1) — and mirrored on rows 4 and 7. 64 active cells. Cell index = y·9 + x. Max degree 4 (axis-aligned, no diagonals); cells adjacent to holes have fewer than 4 active neighbours.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max 100 turns.

**Action space.** 82 actions = 81 placements + 1 pass. **Place-only**, D1 hybrid ban active. Placement legal at any empty active cell.

**Capture (outnumber-2).** When you place a stone, check each of its enemy neighbours: if that enemy has ≥2 of YOUR stones among its own neighbours (counting your just-placed stone), the enemy is removed from the board entirely. Pieces are cleared, not flipped.

**Propagation (influence, r=2, s=1.0, d=0.5).** Placement adds ±1.0 to the placed cell, ±0.5 to BFS-distance-1 cells (graph distance through active-cell adjacency, not Manhattan), and ±0.25 to distance-2 cells. Sign = +1 for P1, −1 for P2. **Holes block propagation paths**: a stone near the central hole reaches fewer cells than the same stone in the open grid. Critical strategic mechanic.

**Win (threshold-race > 30.0).** After each move, sum each player's `board_values` over cells they currently OWN. First to exceed 30.0 wins. Captured stones remove their cell from the captor's loss column AND deny the opponent ownership — but residual `board_values` at the captured cell persist (just don't count for either side once empty).

**Degeneracy check.**
- `sierpinski_threshold_inert` soft violation flagged. Engine still allows play. Worth probing whether the threshold is actually reachable in skilled play within max_turns.
- 64 active cells with threshold 30 means each player needs ≈12-15 stones at avg per-stone effective value of ≈2.0 to win. Tight clustering required; loose spreads can't reach 30.
- Captures clear stones but DON'T zero out residual board_values. Subtle but matters for ownership-after-capture math.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run19_helper.py`.

### Game 1 — Symmetric corner clusters (mirror)

Sequence: `0,8,2,6,18,26,20,24,1,7,9,17,11,15,19,25,3,5,12,14,21,23` (21 plies). P1 wins.

Plot:
- P1 builds top-left 3×3 cluster (minus the hole at (1,1)): (0,0), (2,0), (0,2), (2,2). P2 mirrors to top-right around the hole at (7,1): (8,0), (6,0), (8,2), (6,2).
- Both fill in remaining cells of their 3×3-minus-hole corner. After move 16, both at +20.0, both with 8 stones, mirrored exactly.
- Both expand toward the central column row 0–2: P1 plays (3,0), (3,1), (3,2); P2 mirrors (5,0), (5,1), (5,2).
- **Move 21: P1 plays (3,2), reaches +31.25, crosses threshold.** P2 was at +26.75 — one move behind.

Reflection: **First-mover advantage decides under symmetric play.** Both sides have identical local geometry; both build identical clusters; P1 always crosses 30 first because P1 commits each round one tempo earlier. The trained-vs-trained 0.500 winrate must come from P2 playing asymmetrically.

### Game 2 — Sandwich attack (P2 captures corners)

Sequence: `0,9,2,1,18,11,20,3,4,12,5,13` (12 plies, in progress).

Plot:
- P1 (0,0); P2 (0,1) — sandwich setup, no immediate threat.
- P1 (2,0) — building toward corner cluster.
- **P2 (1,0): captures (0,0).** (0,0)'s P2-friendly neighbours = {(1,0)=just-placed, (0,1)=earlier P2, (1,1)=hole}. Two friendlies, threshold met. P1 stone removed. Net: P2 spent 2 moves to remove 1 P1 stone, but has 2 stones in good position.
- P1 (0,2); **P2 (2,1): captures (2,0).** Same pattern: (2,0)'s P2 neighbours = {(1,0), (2,1), (3,0)=empty}. Two friendlies, captured.
- After 6 moves: P1 has 1 stone (just (0,2)), P2 has 3 stones in a tight L-shape supporting each other.
- P1 (2,2) → P1 has 2 stones; P2 (3,0) → builds further. Score at move 8: P1 +2.0, P2 +2.5. **P2 ahead despite P1 going first.**
- P1 plays (4,0)/(5,0)/(2,2) trying to disperse to safer ground. P2 (3,1)(2,1) cluster keeps growing. By move 11-12, scores are level around +4.

Reflection: **Sandwich attack is the genuine P2 counter to mirror.** Each capture trades 2 P2 stones for 1 P1 stone — but P2's 2 stones are mutually reinforcing (mutual distance-2 contributes +0.25 each), while P1 has 1 stone with empty surroundings. Outnumber-2 + corner geometry creates a structural P2 advantage when P1 anchors at a corner.

**The trap is weakest where the cell has fewer active neighbours.** A stone at (4,2) has neighbours {(3,2), (5,2), (4,1)=hole, (4,3)=hole}: only 2 attack vectors. P2 must place at BOTH (3,2) and (5,2) to capture, slower and committing.

### Game 3 — Hole-edge anchoring (mirror, N vs S)

Sequence: `22,58,21,57,23,59,12,66,14,68,3,54,5,56,4,55` (16 plies, in progress).

Plot:
- P1 anchors north-of-central-hole: (4,2), (3,2), (5,2), (3,1), (5,1) — 5 stones along the southern edge of the top half. Each has reduced neighbours due to (4,1), (3,3), (5,3) being holes.
- P2 mirrors south-of-central-hole: (4,6), (3,6), (5,6), (3,7), (5,7) — same shape, opposite side.
- Both expand to row 0 / row 6 respectively. Move 16: P1 +20.0 with 8 stones; P2 +18.5 with 8 stones. **P1 ahead by 1.5** despite identical move counts.

Reflection: **Even hole-edge anchoring doesn't fix the tempo asymmetry.** The carpet's holes create local asymmetries (P1's north anchor is in a slightly different geometric environment than P2's south) but the influence kernel + threshold-race still rewards going first.

### Strategy guides

**P1 (offence/threshold push):** Anchor in a corner or hole-edge. Each placement should be distance ≤ 2 from existing P1 stones to maximise mutual reinforcement (+0.25 boosts to existing stones plus +0.5/+0.25 to the new stone from its neighbours). Avoid overextending — a single stone with empty surroundings is a sandwich target. Pre-emptively defend corners by placing on the "inside" (e.g., (1,0) and (0,1) as your second/third moves to deny P2 the sandwich pattern).

**P2 (defence + offence):** Pure mirror loses on tempo. The sandwich attack is the equaliser: when P1 anchors at a corner stone, place on its two non-hole neighbours to capture. Each capture costs you 2 stones but gains 2 stones of your own + denies P1 1 stone + denies P1 the captured cell's influence. After a few captures, build a tight cluster from the sandwich stones — they're mutually reinforcing and contribute +1.0 + 0.5×N_adj_own to each other. A successful 4-capture sequence puts P2 ahead on both stones and influence.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Yes, two:
1. **Cluster-and-race** (P1's playbook). Build a mutually-reinforcing 3×3-shaped cluster around a corner hole, expand along board edges. Wins under mirror via tempo.
2. **Sandwich-and-pivot** (P2's playbook). Trade 2 stones for 1 capture wherever P1 anchors at a corner. The captures create a P2 cluster as a side-effect of attack. Wins under standard P1 corner play.

**Counter-play.** Real but knowledge-asymmetric. P1's only counter to sandwich is to NOT anchor at corners — anchor at hole-edge cells with 2 active neighbours, which P2 must commit double-stones to capture. But this trades capture-resistance for reduced influence reach (cells next to holes have BFS-distance reach blocked).

**Short-term vs long-term.** Threshold 30 / per-move gain ≈ 1.5–3.0 → ~10–20 plies per side to threshold. Real games last 28–34 moves total per training metrics. Decisions are mostly 4–6 plies ahead. Long-term planning (10+ moves) doesn't materially change anything because the influence kernel is short-range.

**Emergent concepts observed.**
- **Sandwich trap.** Place at two cells flanking a P1 corner stone; second placement triggers outnumber-2 capture. Same family as R17 team-1's "sandwich trap" but achieved via outnumber-2 instead of custodian.
- **Hole-bottleneck.** Influence routes around holes via graph distance. Stones placed near the central hole have reduced reach but also reduced sandwich vulnerability.
- **Cluster reinforcement.** Distance-1 own stones contribute +0.5 each to a placement's effective; distance-2 own stones contribute +0.25. A 3×3 cluster's interior cells (when intact) have effective value ~2.5–3.0 per stone — far above an isolated +1.0 stone.
- **Tempo crossover.** When both sides race symmetrically, P1 wins because P1 commits one ply earlier each round. Threshold-race + go-first is a structural P1 lead unless P2 deviates.

**Does the carpet substrate matter?** *Partially.* The 17 holes in 81 cells (~21% holes) create local geometric variation: corner cells around (1,1)/(7,1)/(1,7)/(7,7) have 4 neighbours minus the hole = 3 neighbours, and central-hole-adjacent cells like (4,2), (4,6), (2,4), (6,4) have only 2 active neighbours. This makes some cells harder to capture (sandwich requires both axes filled) and reduces influence reach near holes. But the broad strategic loop — cluster, race, occasionally sandwich — works on a hole-free 9×9 grid too. **The substrate adds 1 dimension of geometric awareness** (which cells are sandwich-resistant) but doesn't fundamentally change the strategic family. Could plausibly be flattened to a regular grid with similar play, losing maybe 0.5 points of depth.

**Does the propagation kernel matter?** *Yes, a lot.* Without influence, capture would be meaningless on a board this size — there'd be no scoring system to win. The r=2, decay=0.5 kernel sets the cluster reinforcement geometry: r=1 would force tighter clusters; r=3 would reward looser spreads. The current kernel is well-tuned to the substrate's hole spacing.

**Capture-rule contribution.** Captures fired in 2 of 3 games (the sandwich-attack scenario). Frequency: 2 captures in 12 moves = 1 in 6. Influence on outcome: captures are decisive when they occur because the trading is favourable for the attacker (2-for-1 stone, +cluster building). Without captures (Game 1 and Game 3), the game is pure tempo race won by P1. **Captures are the only real balance mechanism.**

**First-mover advantage / seat balance.** Heavily P1-favoured under symmetric play (Games 1 & 3). Balanced when P2 plays asymmetric counter (Game 2). The training's 0.500 final winrate reflects PPO learning the asymmetric counter; a naïve evaluator playing P2 with mirror loses every time. **This is knowledge-asymmetric balance**, not seat-symmetric balance.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is influence + capture + threshold-race on a fractal substrate. Argument:

(a) **Influence-based scoring** is a known mechanic. Reversi/Othello uses local-neighbour ownership flips; territorial Go has implicit "territory" scoring; modern abstracts like *Sygo* or *Tumbleweed* (2020) use weight-based field scoring. Threshold-race specifically (cross 30 first) is found in racing games like *Yinsh*, but with capture-as-removal rather than influence accumulation.

(b) **Outnumber-2 capture** is closest to *Tafl* family (sandwich-and-remove with adjacency count) and *Ataxx* (stone outnumbering on placement). Distinct from Othello (custodian flip, not removal) and from Go (group-liberty surround).

(c) **The combination** "outnumber-2 + influence + threshold-race" doesn't appear in published abstract-board-game literature as far as I'm aware. It's structurally similar to a Go-Reversi hybrid but uses neither's primary scoring mechanism.

(d) **Sierpinski carpet substrate.** Fractal-substrate abstract games are rare. *Connection Hex* on hex grid is the closest published case of non-rectangular tactical substrate. The carpet's specific hole pattern is a genuine novelty axis — the game would feel different on a regular grid (less hole-bottleneck strategy, more uniform cluster building).

(e) **Expert-transfer test.** A Go + Othello + Hex player working together would understand the rules in 5–10 minutes. The novel pieces they'd have to internalise: (i) influence-as-scoring (vs Go's territory scoring), (ii) the specific outnumber-2 trigger condition (counts neighbours of the *enemy* stone, not the placement target), (iii) hole-bottleneck reach effects.

**Closest known-game analogue:** **A short-range Reversi-Tafl hybrid with weight scoring on a holey grid.** No exact analogue. The closest published example is *Tumbleweed* (Mike Zapawa, 2020) which uses neighbour-count for placement strength, but Tumbleweed is on hex with no captures.

**Comparison to R8's Connection Go (8/10 ceiling).** R8 was custodian + connection on a 2D grid — connectivity-driven, Hex-family, with custodian flips as a chain-completer. R19 carpet rank-1 is in a **completely different family**: no connectivity, all influence-scoring. It cannot directly compete with R8's Connection Go on its own terms. What R19 has that R8 lacks: a working capture mechanism that creates stone-trading dynamics. What R8 has that R19 lacks: a clear, narrative-shaped winning chain that generates Hex-style "build and block" tension. R19 is less narratively tight than R8.

**Player rebuttal (P1 + P2).**
- The sandwich-attack producing a self-supporting cluster (Game 2) IS a real combinatorial discovery — Tafl doesn't do this because Tafl has no influence scoring; Reversi doesn't because Reversi's flipping makes captures non-permanent. The R19 carpet game's specific combination produces this trade.
- The hole-bottleneck strategic axis (Game 3) is genuinely substrate-specific. The same rules on a 9×9 grid would not have the "hole-edge cells are sandwich-resistant" sub-game.
- Subtracting from novelty: the soft `sierpinski_threshold_inert` violation suggests that under formal scoring, the threshold may be unreachable on this substrate — a structural concern worth flagging (though training metrics show games do end via threshold within max_turns).

**Novelty score (post-adversary):** **5/10.** Above pure re-skin (2–3) because the outnumber-2 + influence + threshold-race combination produces sandwich-attack dynamics not present in any single ancestor. Below 7 because (i) the strategic family (capture + scoring race) is well-established, (ii) the carpet substrate adds local geometric flavour but doesn't change the strategic skeleton, (iii) compared to R8's clean Hex-meets-Othello combinatorics, this game's interaction layer is shallower. Above R17 mean (3.50) because the sandwich-attack as P2 counter is genuinely emergent and balance-restoring.

---

## Phase 5 — Verdict

**Team ID:** team-pilot
**Game ID:** ce3a09e05cef
**Rules Summary:** Place stones on a 9×9 carpet (17 holes) to accumulate influence on cells you own. Each placement spreads ±1.0/±0.5/±0.25 within graph-radius 2; captures fire when an enemy stone has ≥2 of your stones among its neighbours. First to >30.0 effective influence wins.
**Substrate:** Sierpinski carpet, axis 9, 64/81 active, max_degree 4.
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** `sierpinski_threshold_inert` — threshold may be borderline reachable; verify against training data.

### Scores (1–10)

- **Strategic Depth: 5** — Tempo race + cluster reinforcement + sandwich tactics + hole-bottleneck awareness. Decisions are 4–6 plies deep; no 10+ ply planning. The capture-trading dynamic adds genuine choice but mostly within a small known set.
- **Emergent Complexity: 5** — Sandwich attack + cluster reinforcement are emergent and non-obvious. Hole-bottleneck strategy is substrate-specific. But the rule set is small and the emergent vocabulary correspondingly limited.
- **Balance: 4** — Mirror = P1 win. P2 must use the sandwich counter. PPO-trained 0.500 winrate reflects asymmetric play, not seat symmetry. **Knowledge-asymmetric balance** — same kind of balance failure R17 team-1 saw (4.14 anchor) but here the asymmetry is sharper because P1's natural play is the "wrong" play.
- **Novelty (post-adversary): 5** — see Phase 4. Above re-skin, below "genuinely new". The outnumber+influence+threshold combination is not published; the sandwich-as-cluster-builder is a real combinatorial discovery; but the family is recognisable.
- **Replayability: 4** — Once mirror = P1 win and sandwich = P2 counter are known, openings collapse to a small set. Carpet's 64-cell space limits position variety. Hole-edge anchoring offers some variation but doesn't change outcome materially.
- **Overall "Would I play this again?": 5** — Once: yes, to feel the sandwich. Repeatedly: no, the strategic surface is shallow once both playbooks are known.

### CLOSEST KNOWN-GAME ANALOG
**A short-range Reversi-Tafl hybrid with weight-based threshold scoring on a Sierpinski carpet.** No exact published analogue. Within this project corpus, no R8–R18 game shares this combination. R8's Connection Go is a different family (connectivity-driven, custodian capture).

### KILLER FLAWS
- **Mirror = P1 win.** First-mover advantage under symmetric play is structural to threshold-race + go-first. Balance only via P2 playing asymmetric counter — knowledge-asymmetric balance is a fragile balance.
- **`sierpinski_threshold_inert` soft violation.** The rule blob is flagged for a known soft violation; worth verifying threshold is consistently reachable in real play (training data suggests yes, with avg 32 moves; but the margin between threshold and average final score should be checked).
- **Shallow long-term planning.** Threshold 30 / per-move gain ≈2 → 15-move horizon. No 20-ply planning surface. Tactical depth without strategic depth.
- **Capture mechanic is binary.** Stones either get captured or don't; there's no partial-capture or capture-cascade dynamic that would deepen the trade calculus.

### BEST QUALITY
**The sandwich-attack-as-cluster-builder.** The 2-for-1 stone trade is roughly even; the *cluster* P2 builds via the sandwich is the real prize, because those 2 stones are mutually reinforcing and become the seed of P2's threshold push. This combinatorial side-effect — attack creates structure — is the game's crown jewel. Same family as R17 team-1's sandwich trap, transferred from custodian capture to outnumber-2 with similar effect.

### CARPET STRUCTURAL CONTRIBUTION
**Modest, not transformative.** The carpet's holes create local strategic variation (hole-edge cells are sandwich-resistant; influence routes around the central hole). But the same outnumber+influence+threshold game on a 9×9 grid would preserve >80% of the strategic surface. **Could be flattened to a 9×9 grid with maybe −0.5 depth.** The carpet specifically adds: (a) sandwich-resistance on hole-edge cells, (b) influence reach inhomogeneity, (c) approximately 21% reduction in usable cells. Compared to R17's 3D-4³ "modest, not transformative" finding, this is similar — fractal substrate as multiplier on tactical surface area, not new strategic dimension.

### IMPROVEMENT IDEAS
**Single best change: pie rule** (R17/R18 deferred this; R19 should test). After P1's first move, P2 may swap colours instead of placing. This nullifies the corner-anchor → mirror = P1 win dynamic by punishing P1 for any opening that's strong enough to mirror profitably. The trained-vs-trained 0.500 winrate would survive; the un-trained 100% P1-mirror win would not.

Secondary improvements:
- **Reduce threshold to 25** — would shorten games to 18–22 moves and tighten decisions; R17 found shorter games scored worse on depth, so this might trade depth for clarity.
- **Increase capture threshold to 3** — would make sandwich attacks require more committed surrounding, deepening the capture calculus. Possibly reverses the balance toward P1.
- **Add the central 3×3 hole as four 1×1 holes instead** (more like a Vicsek pattern) — would distribute hole-bottlenecks more evenly and might restore mirror-like symmetry where balance is structural rather than knowledge-based.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-pilot_gamece3a09e05cef.md`.*
