# Run 21 Agent-Team Eval — team-1 — Game e1453dac5445

**Team ID:** team-1
**Game ID:** e1453dac5445 (menger slate **rank 1 / R21 top**, 20-seed mean GE 0.177, σ 0.101, calibrated komi_p2 0.00)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game e1453dac5445` (see `briefing_menger_e1453dac5445.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 Menger sponge, 400 active cells of 729 (Hausdorff 2.727). Cell = z·81 + y·9 + x. The z=0/z=2/z=6/z=8 faces are Sierpinski carpets (64 active each); z=1/3/4/5/7 are heavily punched (whole rows of holes). The central 3×3×3 and recursive sub-cubes are dead — the active set is a thin shell, so neighborhoods are sparse and a stone rarely reaches its full 6-degree.

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = 100 (in practice the race ends ~ply 19).

**Action space.** 731 actions = 729 placement + pass (729) + pie/swap (730). Place-only (D1 hybrid ban). `first_move_anywhere=true`; `adjacent_empty` is **vestigial** (legal set stays broad — confirmed live).

**Placement & capture.** Capture = **outnumber-2**. A stone is **cleared to empty** when enemy neighbors exceed friendly neighbors by ≥2 in its radius-1 lattice neighborhood. Verified live: P1's isolated stone at (2,0,0) was cleared the instant P2 held both (1,0,0) and (3,0,0) (2 enemy − 0 friendly = 2). Interior stones in a friendly cluster are capture-immune (their own neighbors are friendly, so they can't be outnumbered). Capture costs the attacker **two stones to remove one** — a tempo loss in a race.

**Propagation.** influence, radius=1, strength=1.0, **decay=1.0** (flat — no distance falloff). Each placed stone deposits +1 on its own cell and +1 on every active radius-1 neighbor, signed by player. This flatness is R21's structural signature vs R20's decay-0.5–0.7 champions. Verified: a contiguous strip grows the accumulator ~3/stone (interior cell = self +1 + 2 friendly neighbors).

**Win condition.** threshold-race (dispatch verified NOT connection). First player whose effective owned-influence accumulator (sum of board_values over own cells) exceeds **30.0** wins. `target_dimension_p2=-1` ⇒ P2 mirrors P1's accumulator (symmetric race on the same metric). komi_p2 = 0.00.

**Pie rule.** True. Action 730. Verified live: P2 swapping at ply 2 flips P1's opening stone to P2 ownership and inherits the tempo — a genuine opening-balance lever.

**Degeneracy check.**
- Influence **is** load-bearing (it is the win metric) — unlike R8 where influence was decorative. Positive.
- `adjacent_empty` constraint vestigial (overridden by anywhere-placement).
- Komi gate did NOT lock in: residual P1 bias 0.060 at komi=0; positive komi overcorrects and flips P2 ahead, so komi=0 is the lesser bias (below the G3 0.10 target). Balance rests on the pie swap alone.
- Holes dominate geometry: 329/729 dead cells; play concentrates on the dense carpet faces (z=0/2/6/8).

---

## Phase 2 — Strategic Play

All moves engine-verified. Place ids = cell indices; pass = 729; pie = 730.

### Game 1 — P1 packs left strip vs P2 packs right strip (uncontested mirror race)
Sequence: `0,6,1,7,2,8,9,15,11,17,18,24,19,25,20,26,27,33,28,34,29,35,...` (38 plies played).
Plot: Both sides build dense 3-wide contiguous strips on the z=0 carpet face. Scores climb in perfect lockstep (P1 always +3 ahead because it moves first): ply 15 P1+24/P2+19, ply 17 P1+27/P2+24, **ply 19 P1 crosses to +32 → Done, Winner=1** (10th P1 stone). P2 is at +27, one move behind.
Reflection: With flat decay, the binding constraint is **contiguity** — each adjacent friendly stone is worth a full +1 to its neighbor. The race is a packing sprint and **P1 wins by exactly one tempo** in any mirror.

### Game 2 — P2 contests via capture instead of racing
Sequence: `2,1,72,3` (4 plies) + extension.
Plot: P1 plays isolated (2,0,0); P2 brackets with (1,0,0) then (3,0,0) → **capture fires, (2,0,0) cleared**, P1 pieces 2→1. But P2 spent **two** placements to delete **one** P1 stone worth only +1 — a net tempo and score loss for the would-be-racer. Against a P1 who packs densely, the capturable targets (isolated/edge stones) don't exist, so harassment can't catch up.
Reflection: Capture is a **deterrent against loose play**, not an engine of comebacks. It punishes scattering but cannot beat tight packing.

### Game 3 — Pie-swap balance line
Sequence: `0,730,1` then race.
Plot: P1 opens (0,0,0); P2 plays **730 (swap)** → P1's stone becomes P2's, P1 owns nothing, P2 +1. Now P1 must catch up while P2 holds the tempo. This is the mechanism that disincentivizes P1 from grabbing the single best opening cell — if P1's opening is too strong, P2 simply takes it.
Reflection: Pie does real work, but because *every* opening cell is roughly equivalent (+1, flat field), the swap only neutralizes the ~1-tempo edge partially; the residual 0.060 bias the briefing flags is real and showed up as P1's clean tempo win in Game 1.

### Strategy guides
**P1 (offence):** Pick the densest reachable carpet face (z=0), pack a contiguous block (a 3-wide strip compounds fastest), keep stones mutually adjacent so they are capture-immune, and ride the one-tempo lead to 30.
**P2 (defence):** Either mirror-pack and lose by a tempo, or swap at ply 2 to inherit the lead. Capture-harassment only pays if P1 plays loosely; against tight packing it loses tempo.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** **Essentially one** (dense-pack-the-densest-region) plus a binary opening choice (swap / don't). This matches the engine's low strategic_diversity (0.181). Capture-harass is a viable *response to a mistake*, not an independent winning plan.
**Counter-play.** Partial. The only real counter to P1's tempo is the pie swap; capture cannot overcome packing.
**Short-term vs long-term.** Short. The race ends ~ply 19; decay=1.0 makes it the fastest of the menger pod. ~3–4-ply lookahead suffices. No medium-term territory horizon.
**Emergent concepts observed.** (1) contiguity-as-armor (dense interior = both max score and capture-immunity — these two objectives align, collapsing diversity); (2) tempo lockout in the mirror; (3) swap-to-inherit. Modest set.
**Does menger matter?** Only as a *constraint map* — the holes pick which regions are dense, but the dynamics (pack tight, race to 30) would survive on any substrate with comparable density. The 3D-ness is barely used: play stays on the 2D carpet faces because cross-z neighbors are mostly holes. A flat carpet would preserve ~90% of the dynamics.
**Does the propagation kernel matter?** Yes — it *is* the win metric. But decay=1.0 makes it maximally local-contiguity-rewarding, which *reduces* strategic variety rather than enriching it. r=1 + flat = "score = count your adjacencies."
**Capture contribution.** Near-zero in equilibrium; fires only against loose play. Deterrent, not driver.
**First-mover advantage / seat balance.** Real residual P1 edge (one tempo / bias 0.060). Pie partially corrects; komi=0 because komi overcorrects. Not rush-broken, but not cleanly balanced either.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This is a **territory/influence packing race** dressed on a fractal.
(a) Threshold-race on summed owned-influence ≈ a simplified **Go territory/área count** or a **majority-fill race**; "first to 30 contiguity-points" is a scoring sprint.
(b) Capture analog: outnumber-2 → **Ataxx/Tafl**-style flanking removal.
(c) "outnumber + flat-influence + threshold-race" — no published game uses exactly this, but each component is old; the combination is an R17–R20 family staple (this is the 4th menger threshold-race game in the slate alone).
(d) Substrate: Menger-sponge play is genuinely unusual, but here the holes only *restrict* the board; no fractal-specific tactic emerged (play collapses to 2D faces).
(e) Expert-transfer: a Go/Ataxx player learns this in ~5 min — "pack tight, don't get flanked, race to 30."

**Closest known-game analogue:** a single-metric influence/territory **fill-race with flanking capture** — closest to a stripped-down Go-area-scoring sprint on a punched board.
**Comparison to R8 Connection Go (4.10).** R8 had a genuine asymmetric strategic axis (cut vs race; one stone defeats a plan). This game has **no comparable counter-strategy** — packing dominates and capture can't beat it. Thinner than R8.
**Comparison to R19/R20 best.** It is the same threshold-race family as R19 menger top (4.8) but with decay flattened to 1.0, which *narrows* the strategy space (more pack-convergence, less spreading nuance). Not richer than R19/R20 tops; arguably a step toward a faster, shallower variant.

**Novelty score (post-adversary): 3.5/10.** Above pure re-skin (2–3) because the flat-decay + fractal combination is a structurally distinct point in the family and influence genuinely drives the win. Below R8 (4.10) / R19 top (4.8) because no new *strategic* idea emerges — decay=1.0 reduces rather than expands depth.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game ID:** e1453dac5445
**Rules Summary:** On a Menger sponge, both players race to pile up 30 points of contiguous own-color influence; flanking an isolated enemy stone (2-to-0 neighbors) deletes it, but dense packing is both the fastest way to score and immune to capture — so the game is a packing sprint that P1 wins by one tempo unless P2 swaps seats.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=True, komi_p2=0.00.
**Turn Structure:** alternating, 1 piece/turn.
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** vestigial `adjacent_empty`; komi gate did not lock in (residual bias 0.060, komi overcorrects → served at 0).

### Scores (1–10)
- **Strategic Depth: 4** — One dominant plan (pack densest region) + a binary swap decision. Score-maximization and capture-immunity *coincide* (dense = high-score AND safe), which collapses the decision space. The engine's strategic_depth 0.595 overstates the subjective experience; lookahead beyond ~4 plies rarely changes anything.
- **Emergent Complexity: 3.5** — Contiguity-as-armor is a genuine emergent alignment, and the swap-to-inherit trick is non-obvious, but little else surfaces. Captures are a deterrent that almost never fires in equilibrium.
- **Balance: 4** — Pie does real work, but residual P1 tempo edge (bias 0.060) is real and uncorrected by komi (which overcorrects). P1 wins clean mirrors by one move.
- **Novelty (post-adversary): 3.5** — see Phase 4. Flat-decay fractal packing race; influence is load-bearing (a plus over R8), but no new strategic idea.
- **Replayability: 3.5** — Low strategic_diversity (0.181) is felt: lines converge on packing the same dense faces. Opening variety is shallow because every cell is +1.
- **Overall "Would an agent team play this again?": 4.0** — A clean, fast, comprehensible packing race — above R20 production mean (3.73), but below R8 (4.10) and well below R19 menger top (4.8) and the 5.0 G1 ceiling. The R21 "headline" is a *faster/flatter* member of the existing family, not a deeper one.

### CLOSEST KNOWN-GAME ANALOG
A single-metric influence **fill-race with flanking (Ataxx-style) capture** — essentially stripped-down Go area-scoring on a punched board. Inside the corpus it is a flatter sibling of the R19/R20 menger threshold-race games.

### KILLER FLAWS
- **Score-max and safety coincide** → one dominant strategy, low diversity, shallow decisions.
- **decay=1.0 narrows the game**: full-value adjacency means "pack tight" is unconditionally optimal; spreading/positional nuance is removed.
- **Residual first-mover edge** the komi gate could not close.
- 3D substrate barely used — play lives on 2D carpet faces; the sponge is decoration.

### BEST QUALITY
Influence is genuinely the win condition (not decorative as in R8), and **contiguity-as-armor** — the elegant coincidence that the densest cluster is also the uncapturable one — is the one crown-jewel observation. Unfortunately that same coincidence is what flattens the strategy space.

### MENGER STRUCTURAL CONTRIBUTION
Weak. The sponge only chooses *which* regions are dense; no fractal-specific tactic emerges and cross-z play is suppressed by holes. The game would lose little flattened to the 2D carpet. Consistent with R19's menger>carpet>grid finding being driven by metric artifacts more than by genuine topology-dependent strategy.

### IMPROVEMENT IDEAS
**Single best change:** decouple score from safety — e.g. make **interior** cells worth *less* (cap or diminishing returns on already-high cells) so players must *spread* to score, exposing stones to capture. That would turn the trivial "pack tight" into a real risk/reward tension and revive strategic diversity.
Secondary:
- Lower decay back toward 0.5–0.7 (more spreading nuance) or add a second scored dimension.
- Make captures *flip* (custodian-style) instead of clear, so harassment yields a swing big enough to challenge packing.
- Use the z-axis: reward cross-layer connectivity to force genuine 3D play.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-1_gamee1453dac5445.md`.*
