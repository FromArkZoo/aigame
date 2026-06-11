# Team 1 — Game B verdict

## Phase 1 — Rule comprehension

- Mechanics in your own words: 3D **Menger-sponge** board, axis 9 (9³=729
  grid, only 400 active; the fractal holes `#` are permanent walls that block
  adjacency). Pure PLACE game (ids 0–728 = cell index `d0+9·d1+81·d2`; 729 =
  PASS; **730 = PIE-SWAP**, legal only as P2's first action). **Capture =
  outnumber:** after you place, any enemy stone adjacent to the placed cell
  that now has ≥2 of YOUR neighbours is removed (cleared). **Influence field:**
  every placement adds ±1 (P1 +, P2 −) to its closed neighbourhood (radius 1,
  decay 1.0 → full strength, no fall-off), permanent. **Win = THRESHOLD
  influence race:** your score = Σ board-value over the cells YOU OWN
  (sign-corrected); first past **+30** wins. komi 0; turn-limit-100 →
  more-stones tiebreak; double-pass → DRAW; super-ko rollback-to-pass on
  position repetition. **Ghost influence quirk (verified):** a captured stone's
  influence stays on the board with its ORIGINAL sign forever.
- What actually ends the game: in every competitive line the **threshold fired
  (~+33) around ply 17–18** — a dense ~9-stone cluster crosses +30 fast. I
  never hit the turn limit; double-pass draw is reachable only by mutual
  refusal.
- Surprises: (1) **+30 is reached in only ~9 well-packed stones** — the race is
  short. (2) **Capturing is a trap:** I spent two P2 stones to capture one P1
  stone (Line 3) and ended at score 0 while P1, reduced to a single stone, was
  at **+2** — the captured stone's +1 ghost scar boosted P1's neighbour and
  dragged my own cells down. (3) The 400-cell fractal board is far bigger than
  the ~9-stone race needs, so players never have to meet.

## Phase 2 — Strategic play (≥3 full lines, both roles)

### Line 1 — you as P1
- Moves: `546,728,465,727,547,726,466,725,548,724,467,723,537,722,538,721,539`
- Plan and what happened: I (P1) packed a dense cluster into the (6,6,6)
  corner — each new stone adjacent to my existing ones, so every cell's
  influence reinforced. P2 built its own cluster in the (8,8,8) corner. We
  never touched. Because I move first I crossed +30 one stone ahead of P2.
- Result: **P1 wins, threshold fired at +33 vs +28, 17 plies (9 vs 8 stones).**

### Line 2 — you as P2
- Moves: `546,730,506,465,507,547,425,466,497,548,498,467,416,537,488,538,489,539`
- Plan and what happened: P1 opened (6,6,6) for +1. As P2 I played the
  **PIE-SWAP** (730): the stone flipped to mine and I took the +1 and the
  tempo lead. From then I raced my cluster while original-P1 (now X) built its
  own. Having stolen the lead, I crossed +30 first.
- Result: **P2 wins, +33 vs +28, 18 plies (9 vs 8 stones)** — the swap converted
  P1's structural tempo win into mine.

### Line 3 — adversarial / novelty-stress
- Moves: `546,547,465,555`
- What you tried to break / stress: I tested whether the trailing side can
  **disrupt the leader by capturing**. P1 placed (6,6,6) then (6,6,5); as P2 I
  bracketed (6,6,6) with (7,6,6) and (6,7,6) → outnumber-captured the P1 stone.
  But **ghost influence punished me**: the removed P1 stone's +1 stayed,
  leaving me (2 stones) at score 0 while P1 (1 stone) sat at +2. I also probed
  super-ko by re-placing the captured cell — no rollback (the global position
  differed).
- Result: **Capture succeeded mechanically but lost the exchange** — P1 +2, P2
  0. Confirms aggression is self-defeating; racing dominates.

### Additional lines (optional)
I swept race/capture-hunter policy matchups (grow-vs-grow, grow-vs-hunt,
hunt-vs-hunt): **every disjoint matchup ended +33 vs +28 with the tempo leader
winning** at ply 17. Capture-hunter policies never improved on pure racing
because the clusters never met. Post-swap, the identical race flipped to a P2
win — confirming the outcome is decided by who holds the tempo lead, which the
pie-swap assigns.

## Phase 3 — Joint strategic analysis

- Core tactical loop: "Pick a high-degree corner of the sponge and pack a dense
  cluster, every stone adjacent to your own, so influence compounds (~+3–4 per
  interior stone) until you cross +30." The single most important decision is
  the **pie-swap** (whether to seize the tempo lead); after that it's a clean
  build race.
- Counterplay: Surprisingly, **responding to the opponent is usually wrong.**
  Attacking their cluster costs two tempi per capture AND leaves a same-sign
  ghost scar that helps them — Line 3 shows the captor going backwards. The
  only high-value "response" is the pie-swap.
- Topology/board effects: The Menger holes matter only in that they cap local
  degree (so you seek a full-degree-6 corner to maximise compounding); with 400
  cells and a 9-stone race, the topology mostly guarantees the two sides need
  never interact — which removes tension.
- Emergent concepts: **Ghost-influence-as-capture-tax** is a real, named
  emergent idea — captures are economically negative. But it manifests as a
  reason NOT to interact, so it suppresses rather than generates play.
- Player agency: **Moderate-low.** The pie-swap is a genuine, outcome-deciding
  choice and understanding the capture trap is real skill, but within the
  build, any dense fill reaches ~+33 — move-by-move choices barely move the
  result, and contact is to be avoided.

## Phase 4 — Novelty adversary

- Strongest re-skin case: Stones + outnumber capture + a Hex-style pie rule +
  an "influence/area" win is recognisably a **Go/area-control hybrid**: replace
  "territory" with "influence ≥ threshold" and you have a known abstract.
  The 3D fractal board is largely cosmetic — optimal play just finds one dense
  corner, exactly as on a flat board.
- Honest novelty assessment: **Moderate.** The genuinely original element is
  the **permanent ghost influence that makes capture a self-tax** — I have not
  seen that elsewhere, and it meaningfully changes how aggression is valued.
  But because optimal play is "race disjointly and never capture," the novel
  mechanic is mostly a deterrent, and the headline experience collapses to a
  tempo race decided by the pie-swap. Richer than a bare filling race, but the
  depth is largely optional.

## Phase 5 — Verdict

- P1-role experience sub-score (1-10): **3.7** — you win by default racing, and
  the build is satisfyingly compounding, but low move-to-move agency.
- P2-role experience sub-score (1-10): **3.6** — the pie-swap is a real and
  satisfying lever, but after it the game is the same disjoint race.
- Role-averaged sub-score: **3.65**
- **Fairness perception (1–5): 3** — Default (no swap) is P1-favored by one
  tempo (33–28), but the pie-swap hands P2 the lever to seize the lead (P2 then
  wins 33–28); whoever holds the tempo lead wins, and P2 gets the last word on
  who that is — a roughly balanced design with a slight P2 lean via the swap.
- **Overall (1-10): 3.6**
- Justification: Anchoring against R21 3.69 / R20 3.73, Game B lands right at
  the band. It is clearly a richer artifact than a bare race — Line 2 shows the
  pie-swap is a genuine outcome-deciding decision, and Line 3 surfaces a clever,
  counterintuitive ghost-influence capture-tax that real skill must respect.
  But Lines 1–2 plus the policy sweep show the headline game is still a
  disjoint tempo race to +30 in ~9 stones where the deep mechanics function as
  *deterrents to interaction* rather than engines of play, and within the build
  any dense fill scores ~+33. Genuine cleverness wrapped around a low-agency
  racy core lands it at **3.6** — a touch under the anchors, anchoring down for
  the potemkin depth.
