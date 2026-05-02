# Run 19 Evaluation — team-2 — Game 5048f71b62fd

**Team ID:** team-2
**Game ID:** `5048f71b62fd` (Menger rank-3, GE 0.3158, ELO 2354.6)
**Substrate:** Menger sponge (axis 9, 400 active cells / 729 grid positions, max_degree 6)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game 5048f71b62fd` (see `briefing_menger_rank3.md`).
**Note:** Crossover from `ebf0a3e1c424` × `d21ef16c4945`. Eval report flags this as the gen-6 leader dethroned by outnumber-based games in gens 7-8.

---

## Phase 1 — Rule Comprehension

**Board.** Identical to menger rank-1 and rank-2: 9×9×9 menger sponge, 400/729 active. 8 max-degree-6 anchor cells at the (2,2,2)-class positions.

**Turn structure.** Alternating, P1 first. Max **71 turns** (lowest of the three menger games).

**Action space.** 730 actions = 729 placements + pass. Place-only.

**Capture (surround-2).** Go-style group capture. When a stone is placed, each enemy group adjacent to the placement is checked: if the group has 0 active liberties (no empty active cell adjacent to any group member), the entire group is removed. Holes do NOT count as liberties. **Critical mechanic difference from rank-1/rank-2's outnumber-2:** surround needs *all* liberties of a group filled (potentially many P2 stones for one capture) but captures *entire groups* at once.

**Propagation.** Influence, r=1, strength=1.0, decay=0.5 — identical to menger rank-1. Adjacent pair contributes +1.5/stone; 7-stone octahedral star yields +13.0.

**Win condition.** Threshold-race > **21.212** — **lowest of the 3 menger games** (29% lower than rank-1, 45% lower than rank-2). Combined with surround's group-capture pressure, games end quickly.

**Degeneracy check.**
- **Hole-as-liberty-stealer effect**: cells like (0,0,1), (1,0,0), (0,1,0) have only 2 active neighbours because 2 of 4 axis-aligned positions are holes. These cells are extremely surround-vulnerable (cost 2 P2 stones for 1 capture).
- Double-pass = immediate draw (verified across all 3 menger games).
- Surround at interior 6-degree anchors requires up to 6 P2 stones for 1 capture — much *less* effective than outnumber's 2-of-6 trigger.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run19_helper.py`.

### Game 1 — Mirror at the 6-degree interior anchor (full play-through)

Sequence: `182,546,181,545,183,547,173,537,191,555,101,465,263,627,102,626,110,618,174,554` (19 plies, P1 wins on ply 19).

Plot:
- Plies 1-14: octahedral stars at (2,2,2) and (6,6,6). Both at +13.0.
- Plies 15-18: shell-2 expansion. P1 plays (3,2,1)=102 → +16.0. P2 mirrors (5,6,7)=626 → +16.0. Continues with (2,3,1)=110 / (6,5,7)=618 → +19.0 each.
- **Ply 19 P1 plays (3,1,2)=174.** P1 score = +22.0 > 21.212 → **P1 wins.** P2's last move ply 18 was (1,3,2)-mirror=618, leaving them at +19.0 — never gets a 10th turn.

**Mirror = P1 wins by 1 ply at 10-vs-9 stones.** Same structural P1-by-1-ply tempo as rank-1 and rank-2. The lower threshold (21.2) means the game ends in just 19 plies under mirror — fastest of the three menger games.

The 7-stone star + 2 shell-2 stones is enough to cross 21.212 — much less stone-efficient game than rank-2 where 19+ stones are needed.

P1 reflection: Lower threshold compresses the game to 19 plies. Tactical decisions are concentrated in the first 14 plies (anchor + star); after that, 5 forced shell-2 moves cross threshold. No mid-game.

P2 reflection: Mirror loses by 1 ply — same as rank-1/rank-2. The lower threshold gives P2 *less* time to find an asymmetric counter; P2 must deviate by ply 8-10 or lose to the threshold race.

### Game 2 — Surround attack on a hole-vulnerable corner stone

Sequence: `0,1,9,81,162` (5 plies, surround capture fires).

Plot:
- P1 (0,0,0) [cell 0] — 3-degree corner anchor. Active neighbours: (1,0,0), (0,1,0), (0,0,1).
- P2 (1,0,0) [cell 1] — adjacent attack. (1,0,0) is itself hole-flanked: its active neighbours are (0,0,0), (2,0,0), and that's it ((1,1,0) and (1,0,1) are holes). So (1,0,0) is in fact immediately threat-vulnerable to P1.
- P1 (0,1,0) [cell 9] — extends own anchor group. P1 group is now {(0,0,0), (0,1,0)}. Liberties: (1,0,0)=P2 (not liberty), (0,2,0), (0,0,1), (1,1,0)=hole, (0,1,1)=hole. 2 active liberties.
- **P2 (0,0,1) [cell 81] — the hole-vulnerable trap-cell.** This is a SUICIDAL P2 move analytically — (0,0,1)'s active neighbours are only (0,0,0)=P1, (0,0,2)=empty. By placing (0,0,1), P2 creates a 1-liberty group. Why might P2 still play it? To extend its own group {(1,0,0), (0,0,1)}? But (1,0,0) and (0,0,1) are NOT adjacent (they don't share an axis-edge: (1,0,0)→(0,0,1) is a diagonal step). So they're separate groups.
- **P1 (0,0,2) [cell 162] — closes (0,0,1)'s last liberty. Surround-2 fires: P2 group {(0,0,1)} has 0 liberties → removed.** Score after: P1 = +2.5 (with (0,0,2) and own group), P2 = +0.5 (only (1,0,0) left).

The hole-as-liberty-stealer effect: (0,0,1) had only 2 active neighbours from the start (the rest holes); P2 placing there was a 1-move-from-death decision. P1 wins the exchange 1-for-0.

This is a real menger-specific mechanic. **The pilot is right that surround + fractal creates hole-amplified capture pressure on corner/edge cells.** But this is a tactical hazard for *both* players — it punishes whoever places into a hole-flanked cell first without group support.

### Game 3 — Surround attack on the 6-degree interior anchor (novelty adversary)

Sequence: `182,181,183,184,173,185` (6 plies — exploring P2's Go-style attack on interior).

Plot:
- P1 (2,2,2) [182] — interior anchor.
- P2 (1,2,2) [181] — Go-style approach.
- P1 (3,2,2) [183] — extends own group. P1 group {(2,2,2), (3,2,2)} has liberties: (2,1,2), (2,3,2), (2,2,1), (2,2,3), (4,2,2), (3,1,2), (3,2,1). 7 active liberties (note (3,2,3) is hole).
- P2 (4,2,2) [184] — closes 1 P1 liberty + extends own group. P2 group {(1,2,2), (4,2,2)} are NOT adjacent (distance 3) — these are 2 separate P2 groups.
- P1 (2,1,2) [173] — extends own group. P1 group {(2,2,2), (3,2,2), (2,1,2)}. Liberties: (2,0,2), (1,1,2)=hole, (3,1,2), (2,1,1)=hole, (2,1,3)=hole, (2,3,2), (2,2,1), (2,2,3), (3,2,1). 6 active liberties.
- P2 (5,2,2) [185] — extends own (4,2,2) group. P2 group {(4,2,2), (5,2,2)}. P2's separate (1,2,2) group still alone.

After 6 plies: P1 = +4.0 (3 stones in tight cluster), P2 = +3.0 (3 stones in 2 isolated 2-stone-groups + 1 lone). **Surround capture has not fired** because P1's group has 6 liberties — way too many to close in 6 P2 placements.

**At 6-degree interior anchors, surround capture is even WORSE than outnumber-2 for P2:**
- Outnumber-2 (rank-1): P2 needs 2 P2 neighbours of (2,2,2) to capture. Cost: 2 stones for 1 capture, but counter-sandwich available.
- Surround-2 (rank-3): P2 needs to close ALL 6 liberties of the (2,2,2) group (which P1 will extend, growing liberty count). Cost: 6+ stones for 1 capture. Much worse for P2.

This is a substantive independent finding: **surround capture amplifies the interior-anchor advantage for P1** because group capture cost grows with group size, while outnumber's cost stays fixed at 2.

### Strategy guides

**P1 (offence/threshold push):** Same 6-degree-anchor strategy as rank-1/rank-2. Build tight octahedral cluster. Avoid placing into hole-flanked corner/edge cells without immediate group support — hole-as-liberty-stealer makes single stones at (0,0,1)-class cells trivially capturable. Threshold reached at just 9-10 stones / 19 plies under mirror.

**P2 (defence + threshold contest):** Mirror loses by 1 ply (Game 1). Surround at interior anchors loses on liberty-cost arithmetic (Game 3). **Surround attack is only viable on hole-vulnerable cells (corner/edge with ≤2 active neighbours).** Best line: harass P1's early plies via corner sandwich while building own threshold. Even so, the structural P1-by-1-ply advantage holds.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Two-and-a-half:
1. **Interior-anchor cluster + race** (P1's playbook).
2. **Hole-vulnerable corner attack** (P2's playbook). Only effective at 2-active-neighbour cells; the pilot's listed "Game 1 surround at corner" is the canonical example.
3. **Group preservation** (Go-style life-and-death) — emergent from rules but DOES NOT play out in this game because the threshold race ends before group dynamics mature. **The pilot's "trade groups for tempo" advanced strategy is mostly theoretical** — at threshold 21.2 / 19-ply mirror end, there isn't time for a sacrifice trade to develop.

**Counter-play.** Real but limited. Surround capture creates Go-style life-and-death only on hole-vulnerable cells; on the 8 interior 6-degree anchors, it's strictly worse than outnumber-2.

**Short-term vs long-term.** **The shortest game of the three menger games** (avg 27 moves; mirror ends at ply 19). Tactical horizon ~5-7 plies, strategic horizon ~3 plies (anchor selection + first 1-2 expansions). **No room for Go-style positional play.**

**Emergent concepts observed.**
- **Hole-as-liberty-stealer at corner/edge cells.** Real and substrate-driven — only this menger game (with surround capture) triggers it.
- **Liberty-cost arithmetic at interior anchors.** Group size N → liberty count grows, P2 capture cost grows linearly. Makes interior anchoring more dominant than rank-1 because surround cost > outnumber cost at interior.
- **No Go-style life-and-death.** The game ends too fast for sacrifice trades or alive-vs-dead group distinctions to play out. The Go primitive is *present in rules* but *not active in play*.

**Does the menger substrate matter?** **Yes, more than for rank-1 and rank-2 — but only on a narrow subset of cells.** Hole-vulnerable corner/edge cells are the only ones where surround creates substrate-amplified capture pressure. Interior-anchor cells experience the *opposite* effect (surround is harder than outnumber). Net contribution: ~+0.5 of substrate-driven novelty over rank-1.

**Does the propagation kernel matter?** Same r=1 / d=0.5 as rank-1. Same conclusions.

**Capture-rule contribution.** Surround capture ADDS tactical interest in plies 3-8 via hole-vulnerable corner attacks. **It DOES NOT add the deep Go-style strategic layer the pilot claims** — the threshold race truncates the game before group dynamics develop. Net contribution: similar to outnumber, with different tactical flavour.

**First-mover advantage / seat balance.** Same structural P1-by-1-ply advantage. **PPO 0.500 trained-vs-trained** — likely the same knowledge-asymmetric equilibrium as the other menger games (P1 plays suboptimal corner anchors so P2 has hole-attack counters available).

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is influence + surround + threshold-race on the menger sponge. Argument:

(a) **Surround capture (Go)** is one of the oldest mechanics in board games (Go is ~3000 BCE). Its mechanics are fully understood.

(b) **Influence-based threshold-race** — same family as rank-1, rank-2.

(c) **The combination "surround + influence + threshold"** doesn't appear in published abstract-game literature. The closest is Sygo (Go with positional weight territories), but Sygo uses standard Go territory not radius-weighted influence. The novelty here is the combination itself.

(d) **Menger sponge substrate** — same novelty axis as rank-1/2. The substrate's contribution to *this game* is amplified by the hole-as-liberty-stealer effect — corner/edge cells with 2 active neighbours are surround-vulnerable in a way no regular grid would produce.

(e) **Comparison to R8's Connection Go (8/10 ceiling).** R8 was custodian + connection on a 2D grid. R19 menger rank-3 is surround + influence + threshold-race on 3D fractal. **Both inherit Go primitives** (R8 takes the connection objective, R19 menger rank-3 takes the surround capture). **R19 menger rank-3 is the closest R19 game to R8's strategic family.** However, R8's threshold-substitute (connection win) provides a clear narrative climax (reach the other side); R19 menger rank-3's threshold race lacks an equivalent narrative beat. **R19 menger rank-3 sits below R8 on narrative tension and well below on strategic climax** — but it's the closest match in family.

(f) **Expert-transfer test.** Go player + Tumbleweed player would understand the rules in 5 minutes. The non-obvious pieces: (i) hole-as-liberty-stealer (Go on a non-square substrate where some positions are forbidden), (ii) influence-as-scoring (departing from Go's territory), (iii) threshold-race-as-win (departing from Go's larger-territory wins). Total: ~10 minutes to functional understanding, ~30 to play well.

**Closest known-game analogue:** **Go with influence-weighted threshold scoring on a Menger sponge.** Within R19, this is the *only* surround-based game in the corpus and represents a structurally distinct branch from the outnumber-based menger rank-1/rank-2.

**Player rebuttal (P1 + P2).**
- The hole-as-liberty-stealer at corner/edge cells is genuinely substrate-driven and creates capture dynamics impossible on regular grids. **This is a strong, specific novelty.**
- Group preservation as a strategic concept is in the rules but doesn't play out under the low threshold — the game ends too quickly. The pilot's "trade groups for tempo" claim is theoretical, not observed. Subtracts from emergent-complexity.
- Subtracts from novelty: surround capture is the oldest mechanic in board games. The "novelty" here is in the combination + substrate, not in surround itself.

**Novelty score (post-adversary):** **6/10.** Above rank-1/rank-2 (both 5) by 1 because: (i) surround capture is structurally distinct from outnumber (group capture vs adjacent capture), creating a different flavor of game; (ii) the hole-as-liberty-stealer effect is genuinely substrate-amplified by surround in ways outnumber doesn't trigger. Below 7-8 because the Go-style depth doesn't actually play out under the low threshold — the game *uses* Go primitives but doesn't *exhibit* Go strategic depth.

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game ID:** 5048f71b62fd
**Rules Summary:** Place stones on a 9×9×9 menger sponge to accumulate influence on cells you own. Each placement adds ±1.0 to itself and ±0.5 to active 1-neighbours. Go-style surround capture: when a placement removes the last liberty of an enemy group, the entire group is removed. First to >21.2 effective influence wins; typical mirror game ends in 19 plies.
**Substrate:** Menger sponge, axis 9, 400/729 active, max_degree 6.
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no.
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 5** — Go-style group dynamics in rules + same anchor + cluster decisions as rank-1. **The pilot scored 6 here arguing surround adds Go-style life-and-death depth; I score 5 arguing the low threshold (21.2) cuts the game short before Go-style depth plays out.** Mirror ends at ply 19; sacrifice trades and alive/dead group distinctions don't have time to develop. Above rank-2 (4) because surround captures DO add tactical interest in the early game.

- **Emergent Complexity: 5** — Hole-as-liberty-stealer at corner/edge cells is a real emergent. Liberty-cost arithmetic at interior anchors is observable but mostly an absence-of-effect (surround can't reach interior groups). Same as rank-1's emergent vocabulary in count, with different content (group dynamics vs neighbour counts).

- **Balance: 3** — Mirror = P1 wins by 1 ply (verified ply 19, 10 stones vs 9). Surround at 6-degree anchors is *worse* P2 counter than outnumber at the same anchors. The only viable P2 attacks are on hole-vulnerable corner/edge cells, which are also losing P1 anchor selections. **Game is structurally P1-favoured under best play.** Same as rank-1.

- **Novelty (post-adversary): 6** — see Phase 4. Surround + fractal creates substrate-amplified capture pressure on hole-vulnerable cells, which is genuinely substrate-driven novelty unique to this game in the R19 menger top-3.

- **Replayability: 5** — Same 8-anchor opening tree, but the surround capture rule adds tactical variety in early plies (which corners to attack/defend, which liberties to close first). Above rank-1 (4) by ~1 because the hole-vulnerable cell map adds opening variety. Below pilot's 6 because the truncated game length limits position variety per game.

- **Overall "Would I play this again?": 5** — Once: yes, the surround mechanic on the menger fractal is interesting to feel — particularly the hole-as-liberty-stealer effect. Repeatedly: marginal. The threshold race ends the game before Go-style depth materialises; the games feel more like "tactical races with Go-flavored captures" than "real Go-influence hybrids." **Pilot's 6 felt high; I land on 5.** Anchored against R17 mean (3.50) and R8 ceiling (8/10): meaningfully above floor, well below ceiling.

### CLOSEST KNOWN-GAME ANALOG
**Go with influence-weighted threshold scoring on a Menger sponge.** The only surround-based game in R19's menger top-3, making it structurally distinct from rank-1 and rank-2 (which are parametric siblings). **The closest R19 game in the project corpus to R8's "Connection Go" family** — both inherit Go primitives, though R8 took connection-as-win and this game took surround-capture-as-disruption.

### KILLER FLAWS
- **Mirror = P1 wins by 1 ply** (structural, fastest of the three menger games at 19 plies).
- **Threshold (21.2) too low** to let Go-style depth develop. Group preservation, sacrifice, and life-and-death don't have time to play out before the threshold race ends the game.
- **Surround at interior 6-degree anchors is strictly worse than outnumber at the same cells** — this game's defining mechanic is a *liability* for P2 at the optimal P1 anchor positions, exactly the opposite of the design intent.
- **Hole-vulnerable cells punish naïve play.** The (0,0,1)-class cells with only 2 active neighbours are tactical traps; less-experienced players will lose stones to these without seeing the threat.
- **Eval report flags this game as gen-6 leader dethroned by outnumber.** The R19 evolution preferred outnumber-based games. From this evaluation, the "dethroning" looks justified — surround's marginal added depth doesn't compensate for the tactical fragility at hole-vulnerable cells, and the low threshold prevents the upside (Go-style depth) from materializing.

### BEST QUALITY
**Hole-as-liberty-stealer at corner/edge cells.** Cells like (0,0,1), (1,0,0), (0,1,0) — surrounded by holes on multiple axes — have only 2 active neighbours from the start. Surround capture at these cells costs only 2 P2 stones for 1 P1 capture, identical to outnumber-2 economics, but with the *flavor* of Go life-and-death rather than Tafl outnumbering. This substrate-amplified capture pressure is genuinely unique to surround + menger — no regular grid would produce 2-active-neighbour cells in the absence of board edges. **The strongest substrate-driven mechanic in any R19 game I've evaluated.**

### MENGER STRUCTURAL CONTRIBUTION
**Largest of the 3 menger games.** Where rank-1 and rank-2 had only the 8 interior anchor cells as substrate-driven structure, rank-3 also has the hole-vulnerable corner/edge map as a tactical layer. Estimated contribution: ~1 point of strategic depth + 1 point of novelty over a regular 9³ all-active analogue. **However, this is still less than the pilot's claimed 2 points** because the hole-vulnerable cells are a tactical layer (early-game corner attacks) rather than a positional layer (life-and-death game-defining).

### IMPROVEMENT IDEAS
**Single best change: pie rule.** Same as all R19 games. Mirror's 1-ply structural P1 win is the dominant balance issue.

Secondary improvements:
- **Increase threshold to 30+** to extend the game from 19 plies to ~30+ plies, allowing Go-style group dynamics to actually play out. The current threshold is *too low* for surround to express its strategic depth — this is the single biggest design flaw beyond the mirror imbalance.
- **Add ko rule** to prevent capture-recapture loops if any develop in extended play.
- **Combine surround capture with a connection secondary win** (R8's family) — adds narrative tension and gives the Go-style group dynamics a reason to develop fully. **Strongest R20 candidate from this evaluation, agreeing with the pilot.**

### Notes on the gen-6 dethroning
The eval report says this game led at gen 6 and was overtaken by outnumber-based games in gens 7-8. From this human evaluation, **the dethroning is partly justified and partly a measurement artifact.** Justified: at the 19-ply threshold-race horizon, surround's strategic depth advantage over outnumber doesn't materialise; outnumber is faster to learn and yields cleaner GE scores. Artifact: humans engaging the game beyond pure tempo race would prefer surround for its tactical variety. **R20 should consider raising the threshold for surround-based games, OR include a longer training budget for surround-based games to let PPO learn group dynamics fully, OR pair surround with a connection win to give the Go-style depth a reason to develop.**

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-2_game5048f71b62fd.md`.*
