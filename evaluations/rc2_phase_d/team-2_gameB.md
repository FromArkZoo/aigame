# Team 2 — Game B verdict

## Phase 1 — Rule comprehension

- Mechanics in your own words:
  A 3D **Menger-sponge** board (9×9×9, only 400 active cells; the fractal holes
  `#` block adjacency and are never playable). Players alternate placing one
  stone (PLACE) or PASS; P2's first action may instead be **PIE-SWAP** (id 730),
  which hands P1's opening to P2 (stone flips colour, influence negates, goals
  swap). Every placement adds **+1 (P1) / −1 (P2) influence to its own cell and
  all distance-1 neighbours** (decay 1.0, no falloff). Your **score = sum of the
  influence field over the cells you occupy** (P2 sign-corrected); first to
  **exceed 30** wins. Capture is **outnumber**: after your placement, any enemy
  stone adjacent to it that now has ≥2 of your neighbours is removed. The
  decisive "ghost influence" quirk: a captured stone's influence **stays on the
  board with its original sign forever**. Turn-limit (100) tiebreak = more
  stones; double-pass = draw.
- What actually ends the game / frequency: every decisive line I played ended
  by **threshold win** ("win condition fired"). P1 won 2 (symmetric race;
  build-through-invasion), P2 won 1 (pie-swap). No draws or turn-limit
  tiebreaks occurred, though invasion play trended toward one.
- Surprises: (1) Capturing is often **self-defeating** — the removed enemy's
  ghost influence cancels your own, so my forced corner capture left both my
  stones on net-0 ground (score stayed 0). (2) Invading the enemy cluster
  drives the **invader's own score negative** (its stones sit on enemy
  influence), so invasion is pure denial, never a scoring play. (3) The engine
  validates illegal ids (a hole placement was flagged ILLEGAL and rejected).

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `0,162,1,163,2,164,9,171,11,173,18,180,19,181,20,182,3,165,12`
- Plan and what happened: I (P1) packed a dense ring+block cluster in the
  d2=0 pocket while P2 built a mirror-image cluster two layers away (no
  influence overlap). Dense friendly adjacency makes score grow super-linearly
  (8-stone ring = 24). I reached the threshold one tempo ahead.
- Result: **P1 win, threshold, 19 plies** (P1 +32 vs P2 +27).

### Line 2 — you as P2
- Moves: `1,730,162,0,163,2,164,9,171,11,173,18,180,19,181,20,182,3,165,12`
- Plan and what happened: I (P2) let P1 open in a strong pocket, then **pie-
  swapped** to steal the opening stone, converting P1's tempo lead into mine.
  I then built the exact winning shape around the stolen stone while original-
  P1 built one stone behind.
- Result: **P2 win, threshold, 20 plies** (P2 +32 vs P1 +27).

### Line 3 — adversarial / novelty-stress
- Moves: `0,81,1,83,2,99,9,101,11,4,18,22,19,27,20,29,3,729,12,729,21,729,28,729,84,729,102,729,165,729,183`
- What I tried to break / stress: I drove P2 to **invade** P1's cluster (8
  stones hugging P1) to deny the threshold, and tested capture/ghost mechanics.
  Invasion shaved P1 from +32 to +27 at 10 stones — a real spoiler — but P2's
  own score fell to **−3**, and one invader (with two P1 neighbours) was
  auto-captured. P1 then escaped upward into clean Menger pockets (z-cells 84,
  102, 165, 183) to finish.
- Result: **P1 win, threshold, 27 plies** (P1 +31 vs P2 −3).

### Additional lines (optional)
Capture/ghost probe `0,1,2`: P1 captured P2's stone but both P1 stones ended on
net-0 influence (score 0) — verified poison-on-capture via `--values`.

## Phase 3 — Joint strategic analysis

- Core tactical loop: place so each new stone maximises its own cell value
  (self +1 plus friendly neighbours) **and** raises adjacent friendly cells —
  i.e. grow a dense, hole-respecting blob. The Menger holes are the key
  constraint: you route clusters around them and use the third dimension to
  keep packing.
- Counterplay: invasion genuinely reduces the leader's score (−1 per adjacency)
  but is **self-harming** (invader's score goes negative) and exposes invaders
  to outnumber-capture — so it can only delay, pushing toward the stone-count
  tiebreak. Capturing is double-edged because of ghost poison. The strongest
  response to a strong opening is the **pie-swap** (Line 2).
- Topology effects: the fractal holes make dense clusters **defensible**
  (limited adjacency for invaders) and tend to push the two sides into
  separate pockets — interaction is optional, so games can resemble parallel
  build-races decided by tempo.
- Emergent concepts: ghost-poison (capture as a trap), self-harming invasion
  as denial, pie-swap tempo theft, super-linear cluster scoring.
- Player agency: high — every result turned on my choices (build site, swap
  decision, invade-vs-race), not on engine randomness.

## Phase 4 — Novelty adversary

- Strongest re-skin case: at heart it is an **influence/area race** (Go-style
  influence projection with a numeric threshold win), a well-trodden idea; the
  pie rule is borrowed from Hex/Twixt, and outnumber-capture is a known custom-
  capture variant.
- Honest novelty assessment: moderate-to-good. The *combination* is distinctive
  and the parts genuinely interlock (unlike many of these games where influence
  is vestigial — here it IS the win condition). The **ghost-influence poison**
  turning capture into a liability, and invasion being a score-negative denial
  tool, are real emergent dynamics I exploited live. The Menger-sponge board is
  an unusual, functional substrate. Docked because forced interaction is weak —
  the path of least resistance is two parallel races.

## Phase 5 — Verdict

- P1-role experience sub-score (1-10): 4.4
- P2-role experience sub-score (1-10): 4.3 (pie-swap is a satisfying lever)
- Role-averaged sub-score: 4.35
- **Fairness perception (1-5):** 3 — Symmetric racing gives P1 a one-tempo edge
  (Line 1, 32 vs 27), but the pie-swap fully neutralises it (Line 2 flipped the
  same race to P2), so net-balanced.
- **Overall (1-10, anchored): 4.3**
- One-paragraph justification: B is the most coherent game I've seen here — its
  influence field, threshold win, capture, and pie rule all genuinely interact,
  and I won/lost decisive games on my own decisions (Lines 1–3). The
  ghost-poison-on-capture and self-harming-invasion dynamics are real emergent
  texture I exploited at the board, and the working pie rule gives it a credible
  balance mechanism most of these games lack. I anchor it below the never-
  cleared 5.0 and a touch under R19's top because the fractal topology lets both
  sides retreat into defensible pockets, so the dominant line is two parallel
  build-races where forced interaction is optional and any real interaction
  (invasion/capture) is self-harming — strong machinery, slightly thin conflict.
  Lands at 4.3, my current leader.
