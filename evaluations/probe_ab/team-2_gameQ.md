# Probe A/B Eval — team-2 — Game Q

**Team ID:** team-2
**Game Label:** Q (blind; do not consult `.blind_mapping.json`)
**Substrate:** hex_rhombus (axial triangular lattice), axis 22, 484 total cells / 484 active, max_degree 6, pie_rule=True
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `evaluations/probe_ab/play.py --game Q` (run `--rules` first for rules; `--control` for influence map).

---

## Phase 1 — Rule Comprehension

**Rules derivation.** All mechanics below derived from `play.py --game Q --rules` and observed engine behavior.

**Board.** Hex-adjacency rhombus, axis 22 (484 cells, all active). Axial (q, r); cell index = q + 22*r. Rows sheared. Interior degree 6; acute-corner degree 2; obtuse-corner degree 3.

**Turn structure.** Alternating, 1 stone/turn, P1 first. Max_turns = 200.

**Action space.** 486 actions = 484 placement + pass(484) + pie_swap(485). Placement legal at any empty cell.

**Placement & capture.** Capture rule = **outnumber-2** (threshold 2). After placing, any single enemy *stone* with ≥2 friendly (mover-owned) neighbours is immediately removed (Ataxx-style; single stones, not groups). Verified both directions: P1 placing the 2nd neighbour of a lone P2 stone removes it (`231,230,229` → P2's 230 cleared); P2 capturing a P1 stone with 3 P2 neighbours (`207,209,229,231,251,253,230,252` → P1's central 230 cleared). Consequence: a lone stone pushed next to ≥2 enemies dies instantly, so the contested centre is lethal to unsupported stones.

**Propagation.** Influence field, radius=1, strength=1.0, decay=0.7. Each placed stone adds ±1.0 at its cell and ±0.7 to each immediate neighbour (radius 1 only). Sign +1 P1 / −1 P2. Clamped [−100,100]. The field *is* the score substrate.

**Win condition (score race).** First player whose **sum of board_values over the cells it occupies exceeds 36.0** wins (P1 positive; P2's negative sum negated). Komi bonus = komi_p2·36.0 = 0. Equal → n/a (threshold race). Timeout (200): player with **more stones on the board** wins (piece-count majority, NOT score); equal → draw. Komi_p2 = 0.0.

**Pie rule.** After P1's first stone, P2 may swap (485): inherits the stone, becomes first mover. Verified (`230,485` → differential −1.00, P2 now owns the +1 stone).

**Degeneracy check.**
- **Persistent-influence ledger (significant quirk).** The field is additive and capture does **not** subtract a removed stone's deposit. Verified: one P1 stone = 1.00; two = 2.00; but `231,230,229` (P2 plays 230 between them, then is captured) = **0.60 = 2.0 − 2×0.7** — the captured P2 stone's −0.7 scars persist forever. Captured stones leave permanent influence; board_values is path-dependent on full placement history, not on current stones.
- **Win/timeout mismatch:** the live objective is a *score* threshold, but timeout is decided by *stone count* — two different currencies, so a suppressed race silently switches objective at turn 200.
- **Geometry:** degree-6 interior maximizes cluster score density; acute-corner (deg-2) stones are capturable by just 2 enemies (all their neighbours).

---

## Phase 2 — Strategic Play

All moves engine-verified via `play.py --game Q`. Placement id = q + 22*r; pass=484; swap=485. Status line reports the P1−P2 score differential vs threshold 36.0.

### Game 1 — Symmetric separated race (first-mover test)
Sequence: `230,92,231,93,229,91,252,114,208,70,209,71,251,113,232,94,228,90,274,136,186,48,188,50,272,134` (P1 builds a compact cluster around (10,10); P2 builds the identical shape around (4,4), far enough that the radius-1 fields never touch).
Plot: Both pump score by clustering (each interior stone ≈ 1.0 + 0.7·neighbours). A 7-stone "flower" = 23.80; ~13 tightly-packed stones cross 36. P1, moving first, reaches the threshold one tempo ahead → **done at ply 25, winner=1**, differential 2.40 (P1 ≈38.2 vs P2 ≈35.8 with one fewer stone).
Reflection: In a pure race the first mover wins by exactly one tempo. Komi=0 does nothing; only the **pie rule** can balance this.

### Game 2 — Interface capture battle
Sequence: `207,209,229,231,251,253,230,252` (P1 column q=9, P2 column q=11, then P1 pushes the centre 230, P2 answers 252).
Plot: P1's central stone 230 ends with three P2 neighbours (231, 252, 209) → **captured**; the centre goes empty, differential −0.30 (P2 ahead). The contested seam between two clusters is decided by who completes the 2nd/3rd adjacency first.
Reflection: Lone stones poked into the seam die to outnumber-2. You must advance the seam with *supported* stones; the centre is the most dangerous, least rewarding place to fight.

### Game 3 — Denial via sacrificial scarring (defensive ceiling test)
Sequence: `230,484,231,484,229,484,252,484,208,484,209,484,251,484,232,233,228,227,274,296,186,164,188,189,272` then `…,272,484,253`.
Plot: P1 builds its 13-stone winning cluster; P2, instead of racing, lands 5 perimeter stones (233/227/296/164/189) each touching exactly one P1 ring-2 stone (so each survives and deposits a permanent −0.7 scar). P1's score at 13 stones is dragged from 38.2 down to **33.20 — below threshold**, so denial *does* delay. But P2 built nothing; P1 adds one strong infill (253, adjacent to 4 P1 stones) → **done at ply 27, winner=1**, differential 39.80.
Reflection: Scarring delays the race by ~1–2 stones but costs P2 its own race entirely. **Pure disruption loses.** The dominant mode is therefore "build fastest," with contesting only worthwhile where it's locally free.

### Strategy guides
**P1 (race to 36):** Build one compact cluster — density is everything (each added interior cell ≈ +3–4). Start off-centre/near an edge so the seam toward the opponent is short and your interior is uncapturable. Don't fight in the centre; infill your own blob.
**P2 (defence + contest; pie/komi-aware):** If P1 opens with a strong central stone, **swap (485)** — the first-mover wins symmetric races, so take that seat. If you must contest, do it only with supported stones that can't be outnumbered, and prefer racing your own cluster to pure scarring (scarring loses on tempo). If the race stalls into mutual capture, pivot to the **stone-count timeout** objective.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Weakly. The viable plan is "build a compact cluster to 36 first." Capture skirmishes and sacrificial scarring exist but are sub-optimal vs straight racing (demonstrated: denial dragged P1 to 33.2 but cost P2 the game). A secondary plan (play for the stone-count timeout) exists only if the race is mutually suppressed.
**Counter-play.** Mostly absent at the strategic level: the best answer to a builder is to build faster, not to interfere. Local counter-play is real (outnumber-2 captures, seam fights) but rarely changes the race outcome.
**Short-term vs long-term.** Short. The race resolves in ~13 stones / ~25 plies; the planning horizon is "where to site one cluster." The 22-wide board adds siting choices but not deeper horizons than R21's 9×9.
**Emergent concepts observed.** Cluster-density optimization; Ataxx capture tug-of-war at seams; **sacrificial scarring** (persistent-ledger denial); a latent second objective (stone-count timeout). Real but mostly local emergence.
**Does hex_rhombus topology matter?** Less than for a connection game. Degree-6 raises cluster score density and makes outnumber-2 easier to trigger, but the race + outnumber dynamic survives on a square grid (degree 4) with a rescaled threshold. Topology *tunes* Q; it isn't *structural* to it.
**Does the propagation kernel matter?** Yes — the radius-1/decay-0.7 field is the score itself, and its short radius is what makes tight clustering the only efficient way to accumulate. But it merely sets the scoring gradient; it doesn't create strategic structure the way Z's kernel does.
**Capture-rule contribution.** Outnumber-2 fires readily (verified both directions) and disciplines the seam — you can't shove unsupported stones forward. But because contesting loses to racing, captures stay tactical sideshows rather than the main event.
**First-mover advantage / seat balance.** Strong and sharp: the symmetric race is won by exactly one tempo (Game 1, 38.2 vs 35.8). Komi_p2=0 adds nothing; balance rests entirely on the **pie rule**, which works but leaves a knife-edge race underneath.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Q is a re-skin of **an influence/territory accumulation race + Ataxx capture**. Argument:
(a) "Sum of influence over your stones past a threshold" is a territorial/area-score race — the scoring spirit of Go-influence and point-accumulation abstracts.
(b) Capture analog: outnumber→**Ataxx/Tafl** (you die when sufficiently outnumbered by adjacent enemies). Outnumber-2 is squarely the Ataxx/replication-capture family.
(c) "Outnumber-2 + radius-1 influence + score-threshold" = build the densest blob fastest while not getting outnumbered — i.e., Ataxx-style capture grafted onto an influence-area race. No single published game *is* this, but every component is standard, and the composition adds no forced interaction.
(d) Substrate: hex-rhombus degree-6 differs from R17–R21's menger/carpet/grid, but it only tunes density here; not structural.
(e) Expert transfer: a Go/Ataxx player learns Q in ~10 minutes. The only irreducible new piece is the **persistent-influence ledger** (captured stones leave permanent scars) — and that reads more like an unintended artifact than a designed mechanic.

**Closest known-game analogue:** an **Ataxx-capture × Go-influence point race** — cluster for area, die when outnumbered.
**Comparison to R8 Connection Go (anchor 4.10).** Different family (race vs connection). Q is thinner: R8's connection forced engagement; Q's race lets players ignore each other.
**Comparison to R19/R20/R21 best.** Thinner than R19 5.0 / R20 4.80; roughly at R21 3.69. The persistent-scar quirk is the only thing that isn't off-the-shelf, and it's likely an artifact.

**Novelty score (post-adversary):** **3.0/10.** Above pure re-skin (2–3) only because the persistent-influence ledger enables genuine sacrifice-denial plays not present in the parent games. Below novel (8–9) because it is Ataxx capture + influence-area race with weak forced interaction. Anchor: R17 3.50, R8 4.10, R19 4.8/5.0, R20 4.80, R21 3.69.

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game Label:** Q
**Rules Summary:** Race to pile up influence by packing a tight cluster past a score threshold, while Ataxx-style outnumber-2 capture punishes unsupported stones — and dead stones leave permanent influence scars.
**Substrate:** hex_rhombus, axis 22, 484/484 cells, max_degree 6, pie_rule=True, komi_p2=0.0.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only).
**Soft violations flagged:** persistent-influence ledger (captures don't subtract deposits); win-vs-timeout currency mismatch (score race → stone-count tiebreak).

### Scores (1–10)
- **Strategic Depth: 3.5** — one dominant plan (build densest cluster fastest); contesting is demonstrably inefficient, so forced interaction is weak and the horizon is short.
- **Emergent Complexity: 4** — outnumber capture tug-of-war, sacrificial scarring, and a latent stone-count regime give some emergence, but the optimum (cluster up) is clear.
- **Balance: 5** — symmetric race won by exactly one tempo; pie corrects *who builds*, but the underlying race is a knife-edge and offense dominates defense.
- **Novelty (post-adversary): 3.0** — Ataxx capture + influence-area race; only the persistent-scar ledger is unusual (and likely artifactual).
- **Replayability: 3.5** — siting variety exists but converges toward "find best cluster start"; weak interaction limits surprise on repeat play.
- **Overall "Would an agent team play this again?": 3.6** — a coherent but shallow race with a notable degeneracy and little forced engagement; sits around R21 (3.69), just under. Anchors: R8 4.10, R19 4.8/5.0, R20 4.80, R21 3.69.

### CLOSEST KNOWN-GAME ANALOG
An **Ataxx-capture × influence-area point race** — no exact published twin, but every part is off-the-shelf. In-corpus, distinct from R8 (connection) and closest in spirit to prior influence/score-race attempts.

### KILLER FLAWS
- **Weak forced interaction:** pure disruption loses to straight racing (verified: scarring dragged P1 to 33.2 but cost P2 the game), so games tend toward two parallel solitaire builds.
- **Persistent-scar degeneracy:** captured stones leave permanent influence, making board_values path-dependent and the score subtly non-physical — reads as a bug, not a feature.

### BEST QUALITY
The **sacrificial-scar** play: because a captured stone's negative deposit is permanent, you can spend stones to permanently depress an opponent's score even after they're removed. It's the one tactic with no clean analogue in the parent games — though it's double-edged that it likely stems from an engine artifact.

### HEX_RHOMBUS STRUCTURAL CONTRIBUTION
Mostly cosmetic. Degree-6 raises cluster score density and eases outnumber-2 captures, but the race-plus-outnumber dynamic would survive a square-grid flatten with a rescaled threshold. Against R19's menger > carpet > grid finding, Q does not exploit topology structurally; 22×22 adds siting options, not depth. The board is bigger than it needs to be — a single ~13-stone cluster decides everything on 484 cells.

### IMPROVEMENT IDEAS
**Single best change:** **Decide the game by score at timeout (and recompute the field on capture).** Aligning the live objective (score) with the tiebreak removes the currency mismatch, and lifting the persistent-scar artifact makes captures physical. Then add a mechanism that *forces* interaction — e.g., a shared/contested scoring zone both players must occupy — so racing in separate corners is no longer viable. (Falsifiable: replays should then show players contesting a common region rather than building in isolation.)
Secondary:
- Lower the threshold or shrink the board so clusters must collide, forcing seams and capture fights.
- Give P2 a small komi in addition to pie to soften the one-tempo race knife-edge.

---

## Q-vs-Z Comparison

**Which game would you rather play again?** **Z.**
**By how many Overall points?** **+0.6 Overall in favour of Z** (Z 4.2 vs Q 3.6).
**Key differentiator:** Z forces interaction through Hex's connect/cut duality — every move you must both connect and cut, so you can never ignore the opponent. Q's score race lets both sides build in parallel (pure interference loses on tempo), collapsing it toward two solitaire cluster-builds punctuated by local captures. Forced, structural engagement is the dynamic that most separates them, and it favours Z.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/probe_ab/team-2_gameQ.md`.*
