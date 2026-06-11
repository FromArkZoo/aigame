# Team 1 — Game E verdict

## Phase 1 — Rule comprehension

- Mechanics in your own words: 3D **Moore** board, axis 4 (4³=64 cells, up to
  **26 neighbours** — orthogonal + all diagonals). PLACE (ids 0–63; 64 = PASS;
  no pie); target = **any** cell (placing on an enemy stone replaces it, on your
  own is a no-op) but you must place **adjacent to one of YOUR stones** (first
  stone anywhere). **A cellular automaton runs 3× after every action**:
  totalistic from the acting player's view, `new = T(state, #friendly,
  #enemy)`, only for neighbour counts ≤4 (cells with >4 of a colour are
  frozen). Classic capture/influence are disabled. **Win = CONNECTION
  (Hex-style):** P1 connects faces d2=0↔d2=3, P2 connects d0=0↔d0=3, paths via
  Moore adjacency (so diagonals connect — paths are very short). Super-ko
  active; turn limit 141 → stone-count tiebreak; double-pass → DRAW.
- What actually ends the game: **P1's connection firing on its 4th stone (ply
  7)** in every line I played — a straight d2-column (0,0,0)→(0,0,3) connects
  the two faces and is CA-stable. I never reached the turn limit and never saw
  P2 get a decisive tick.
- Surprises: The CA's real-world effect is almost entirely **destructive and
  anti-strategic**: (1) a **lone stone with 0 friendly + 1 enemy neighbour
  instantly dies** (verified `0,16`: P2's blocker vanished same turn); (2) an
  **over-cluster self-destructs** — I built a 2×2 P1 face and the CA emptied the
  whole thing (verified `0,64,1,64,4,64,5` → board empty). So the only durable
  structure is a thin chain (≤2 friendly neighbours) — which is exactly the
  winning column.

## Phase 2 — Strategic play (≥3 full lines, both roles)

### Line 1 — you as P1
- Moves: `0,12,16,13,32,14,48`
- Plan and what happened: I (P1) ran a straight d2-column
  (0,0,0)→(0,0,1)→(0,0,2)→(0,0,3). P2 raced its own d0-row in the d1=3 plane,
  fully disjoint from my column (no CA interaction). My column is CA-stable
  (interior stones have 2 friendly, 0 enemy → frozen), so it completed
  untouched one tempo before P2's row.
- Result: **P1 wins by connection, ply 7 (P1=4 stones, P2=3).**

### Line 2 — you as P2
- Moves: `0,42,16,43,32,58,48`
- Plan and what happened: Driving P2, I tried to disrupt P1's column. I could
  not: every cell adjacent to a column stone is also adjacent to a neighbouring
  column stone, so any blocker I place is a lone-stone-next-to-enemy and the CA
  vaporises it before my support can arrive. I instead built a safe off-column
  cluster, but it could neither reach the column nor complete my own d0
  connection before P1 finished.
- Result: **P1 wins, ply 7 (P1=4, P2=3)** — I (P2) had no available counterplay.

### Line 3 — adversarial / novelty-stress
- Moves: `0,16` (lone-blocker death) and `0,64,1,64,4,64,5` (over-cluster
  self-destruct)
- What you tried to break / stress: I attacked the engine's two CA edge rules.
  (a) Placing a P2 blocker directly on the column path — the CA emptied it the
  same turn (0 friendly + 1 enemy). (b) Building a dense 2×2 P1 face — the CA
  annihilated all four stones (3 friendly + 0 enemy → empties). Together these
  prove blocking is impossible and blobbing is suicidal, so the column is
  impregnable.
- Result: both CA deletions confirmed; the column win is unblockable.

### Additional lines (optional)
Tested unopposed (P2 passing) and two different P2 disruption shapes: **all
ended P1-win at ply 7**. No P2 line I could construct delayed P1 past its 4th
stone.

## Phase 3 — Joint strategic analysis

- Core tactical loop: "P1 plays a straight d2-column and wins on move 4." That
  is the whole game with competent P1. The CA does not create a richer loop; it
  removes loops by deleting anything that isn't a thin chain.
- Counterplay: **None found.** P2 cannot place a durable stone adjacent to the
  column (CA kills it), cannot out-tempo P1 (second mover, and its own
  connection also needs 4), and cannot exploit the CA to flip column stones in
  time (the flip rule needs 2 supported enemy neighbours, which can't be
  assembled beside the column before move 4).
- Topology/board effects: Moore-26 adjacency makes connection trivially short
  (4 stones span 4 layers, diagonals allowed), which is the root of the
  degeneracy; the CA's count cap (>4 → frozen) means dense interiors never
  change, so the CA only ever bites the sparse edges where lone/over-clustered
  stones sit.
- Emergent concepts: The only emergent rule of thumb is "build thin chains, never
  blocks or blobs" — but it leads straight to the forced column win, so it is
  anti-strategic rather than generative.
- Player agency: **Effectively zero.** P1 has one obvious winning script; P2 has
  no legal way to interfere. The result is decided by the rules, not the players.

## Phase 4 — Novelty adversary

- Strongest re-skin case: Strip the CA and this is **3D Hex on a Moore lattice
  with no pie rule** — a known trivial first-player win. The CA is the novel
  wrapper, but in competitive play it reduces to "unsupported stones die,"
  which only reinforces the first-player win.
- Honest novelty assessment: **Low in effect, despite an ambitious mechanic.**
  The CA table is genuinely original and the lone-death / over-cluster-death
  behaviours are interesting to analyse, but they do not produce a playable
  contest — they channel the game into a 4-move forced P1 connection. Novel
  machinery, degenerate game.

## Phase 5 — Verdict

- P1-role experience sub-score (1-10): **2.6** — you win in four moves, but it's
  a script, not a contest.
- P2-role experience sub-score (1-10): **1.8** — no legal counterplay exists;
  you lose on move 4 every time.
- Role-averaged sub-score: **2.2**
- **Fairness perception (1–5): 1** — Strongly P1-favored: P1 won every line
  (both roles) by an unblockable 4-move column; P2 has no mechanism to delay or
  contest it.
- **Overall (1-10): 2.3**
- Justification: Anchoring DOWN hard against drift, E sits near the floor.
  Lines 1–2 show a **forced 4-move P1 win with zero P2 counterplay**, and Line
  3 shows why: the CA deletes both lone blockers and dense blobs, leaving the
  thin d2-column — P1's instant win — as the only viable structure. The
  mechanics are ambitious (a 3D-Moore CA connection game) but the realized game
  is degenerate, heavily seat-decided, and burdened with a large non-functional
  rule table, so it fails non-triviality and simplicity at once. It lands at
  **2.3**, below the contact-race games, because at least those last a full game
  and finish 28–27, whereas E is over in four moves.
