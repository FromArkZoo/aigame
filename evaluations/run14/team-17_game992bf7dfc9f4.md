# Team-17 Evaluation — Game 992bf7dfc9f4 (Run 14)

**Team ID**: team-17
**Game ID**: 992bf7dfc9f4
**R14 rank**: 5 by GE 0.4196, ELO 2953
**Claimed novelty**: simultaneous turn structure + active CA rule (the sim×CA hybrid; R15 premise)

---

## PHASE 1 — RULE COMPREHENSION

### Board
- 2D **grid** (NOT torus), axis_size 8 → 64 cells.
- von Neumann adjacency (4 neighbours, no wrap).

### Turn Structure — **SIMULTANEOUS**, 1 piece per turn
- Both players submit a move each tick; resolved by `step_simultaneous`.
- **Collision resolution**: if both players pick the SAME empty cell, `collision=True` → **mutual annihilation**: neither stone is placed (confirmed empirically).
- If one player passes and the other places, the placer places; the passer does nothing.
- Two consecutive passes in the SAME tick → game ends by majority (`_end_by_max_turns`).

### Action Space
- 65 actions: 0–63 place at cell `y*8 + x`, action 64 = pass.

### Placement Constraint
- Target: empty cells only.
- Constraint: **adjacent_to_own** (must be von-Neumann-adjacent to one of your own stones), EXCEPT `first_move_anywhere=True` while that player has 0 pieces.

### No classic capture, no propagation
- `capture_type = "none"`, `prop_type = "none"`. All captures/flips are via the CA.

### Cellular Automaton — **ACTIVE, but asymmetric**
- 75-entry transition table indexed by `(state, friendly_count, enemy_count)` with state ∈ {0=empty, 1=friendly, 2=enemy}.
- 30 entries have `f+e > 4` and are **unreachable** on a grid (max 4 neighbours).
- Of the 45 reachable entries, **9 are non-trivial** (identity on the other 36).
- `steps_per_turn = 1`.
- **Critical asymmetry (confirmed in engine_v2.py:252–254)**: in simultaneous mode, the CA step's "acting_player" is `1 if i % 2 == 0 else 2`. With `steps_per_turn=1` and `i=0`, **the CA always runs from P1's perspective**. It never runs from P2's perspective. This is the structural P1-favouring flaw.

**Reachable non-trivial transitions (friendly=P1, enemy=P2 always)**:
| State | f | e | New | Effect |
|-------|---|---|-----|--------|
| P1 | 0 | 1 | P2 | Lonely P1 flanked by 1 P2 → flips to P2 (hurts P1) |
| P1 | 0 | 2 | empty | P1 outnumbered 0:2 → dies |
| P1 | 1 | 2 | empty | P1 outnumbered 1:2 → dies |
| P1 | 1 | 3 | empty | P1 outnumbered 1:3 → dies |
| empty | 2 | 0 | P1 | Empty with 2 P1, 0 P2 → **BIRTH for P1** |
| P2 | 2 | 0 | P1 | P2 surrounded by 2 P1, 0 P2 → flips to P1 |
| empty | 2 | 1 | P1 | Empty with 2 P1, 1 P2 → **BIRTH for P1** |
| P2 | 3 | 0 | empty | P2 surrounded by 3 P1 (isolated) → dies |
| empty | 4 | 0 | P1 | Empty fully surrounded by P1 → **BIRTH for P1** |

**Summary**: P1 has **three birth rules** and one flip-to-P1 and one kill-P2 rule. P2 has **zero birth rules** and one flip-to-P2 (only against isolated P1 stones). This is fundamentally asymmetric — the CA is a P1 growth engine. P2 has no spontaneous growth, only placement.

### Win Condition
- Territory threshold: win if owning > 62.53% of cells → **> 40.02**, so **≥ 41 pieces** wins. Max 100 turns.

### Degenerate-rule flags
- **P1-biased CA**: confirmed. Structural first-mover advantage that simultaneous play does NOT neutralise.
- **Opening-stone flip vulnerability**: a lone P1 first move can be CAPTURED on the very first tick if P2 plays an adjacent cell (rule `1,0,1 → 2`). Verified in Game 3 Turn 1.
- **Double-pass majority exploit**: reachable when P2 walls P1 off and P1 has no legal non-suicide placement. Fired in Game 3.
- **Adjacency lock / territory cutoff**: if one side walls off an empty region, the other side cannot grow into it.

---

## PHASE 2 — STRATEGIC PLAY (3 games, every move engine-verified)

All moves were submitted through `step_simultaneous` via a custom harness `/tmp/play_simul.py`; illegal moves were caught by `engine.get_legal_actions(player=…)` before commit.

### GAME 1 — Central opening, both players cluster
Opening: P1 (3,3)=27, P2 (4,4)=36 (offset to avoid collision).

Moves played (comma-separated):
- P1: 27,19,26,11,12,17,16,2,13,33,40,49,6,15,23,31,57,58,42,29
- P2: 36,35,28,44,20,43,37,34,45,38,46,47,51,52,53,55,54,63,60,61

**Result**: **P1 wins at Turn 20**, P1=41 vs P2=20. Territory threshold crossed cleanly (no pass).

Key moments:
- T3: CA births P1 at (2,2) after L-shape formed (2 P1 neighbours at (2,2)).
- T6: Double CA birth at (1,1) and (1,3).
- T7: Double CA birth at (0,1) and (0,3).
- T9: Double births at (0,0) and (4,0) — birth cascade accelerates.
- T10: Triple birth at (5,0), (0,4).
- Over the game: P1 grew at ≈ +2 to +3 pieces/turn via placement+CA births; P2 at +1/turn via placement only.

### GAME 2 — P1 corner-ish opening, P2 contests with closer-than-Game-1 placement
Opening: P1 (2,2)=18, P2 (5,5)=45.

Moves:
- P1: 18,26,27,11,25,16,3,4,5,6,7,23,31,33,41,49,57,58
- P2: 45,44,43,35,36,34,42,52,53,50,46,54,55,38,47,63,62,61

**Result**: **P1 wins at Turn 18**, P1=41 vs P2=18. Cleaner win than Game 1.

Key moments:
- T9: **Triple birth** at (0,0), (5,1), (4,2) — best CA tick of the evaluation.
- T10: Triple birth at (6,1), (5,2), (4,3). (4,3) was birthed as P1 because the CA saw 2 P1 and 1 P2 neighbours at that empty cell (rule 0,2,1→1). This demonstrates the CA can steal empty cells from P2's growth path.
- Game ended even faster than Game 1 because the corner-ish opening let P1 extend into unconstrained territory quickly.

### GAME 3 — SEAT SWAP: I played P2 adversarially, P1 played known best strategy
Opening: P1 (3,3)=27, **P2 (3,4)=35 (adjacent to P1 lone stone)**.

**Turn 1 discovery**: P2's adjacent placement triggered CA rule `(1,0,1) → 2` on P1's lone stone. **P1's opening move got captured**. Post-T1: P1=0, P2=2. This is a genuine P2 opening exploit.

Moves:
- P1: 27,45,37,44,52,54,55,63,61,59,58,49,48,41,33,38,30,22,14,6,24,16,42,64,64,64,64,64,64,64,64
- P2: 35,36,37,34,43,28,37,29,20,19,26,18,17,9,10,11,12,13,21,5,25,16,16,24,8,1,2,3,4,0,64

T3 collision at 37=(5,4): both players played (5,4) → mutual annihilation (confirmed `collision=True` in info).

**Result**: **P1 wins at Turn 31 via DOUBLE-PASS MAJORITY**, P1=35 vs P2=29. P1 never reached the 41-piece threshold because P2 walled P1 off, but P2 could not reach majority either. The game ended on both-players-pass in the same tick; majority (35>29) gave P1 the win.

Key moments:
- T1: P2 captured P1's opener via CA flip.
- T7: P1 regrew a cluster from (5,5) and caught up to P2.
- T13: P1 overtook P2 in piece count (the CA engine compounded).
- T22: P2 achieved a full wall that cut P1 off from the top of the board. P1's only legal non-suicide move became PASS.
- T23: P2 placed at (0,2)=16. CA killed P1 at (0,3)=24 via rule `(1,1,2) → 0` (P1 with 1 friendly + 2 enemy died). **P2 can kill P1 perimeter pieces if P2 has a wall close to the P1 piece.**
- T24–T30: P2 filled remaining empties; P1 forced to pass every tick.
- T31: both passed → majority wins → P1.

### Reflections

#### Player 1 strategy guide
- **Open NEAR centre but not the exact mid-cell P2 will predict**. A move like (2,2) or (3,3) is fine if followed instantly by an adjacent-support placement.
- **The opening move is the only vulnerable moment**. A lone P1 stone with any adjacent P2 neighbour dies via `(1,0,1)`. If P2 plays directly adjacent, you must make sure your next placement shores up your cluster.
- **Build L-shapes to trigger CA births**. Every 3 stones around a common empty cell produces +1 free stone per tick. Aim for placements that set up 2 simultaneous births.
- **Once you have a 2×2 block, you are essentially immune to CA corrosion**: every stone has f ≥ 2 and no rule kills a stone with f ≥ 2 regardless of enemy count.
- **Growth rate is +2 to +3 pieces/tick** against any P2 that also grows. You reach 41 pieces around turn 17–20.
- **Avoid placing into hostile territory** — a P1 stone with f=1 + e=2 dies immediately per `(1,1,2) → 0`. Always back-fill from your cluster outwards.

#### Player 2 strategy guide
- **Opening theory is forced**: the ONLY strong P2 move against a central P1 opener is to play an adjacent cell and let `(1,0,1)` flip the P1 stone. Without this, P2 falls behind immediately.
- **After the opening, P2 has no CA growth**. You are in a territorial race at +1/turn against P1 at +2–3/turn. You WILL lose on threshold.
- **Best fallback: wall + cut-off**. Play a solid wall between P1 and empty territory. P1's adjacency-constraint means P1 cannot grow into regions disconnected from its cluster. This forces the game toward double-pass majority, where the outcome is decided by who had the larger piece count at the walling moment.
- **Collision denial** is a legitimate tempo tool but costs you a turn too; only deploy when you can predict P1's move with high confidence (e.g. the only remaining legal cell).
- **Kill opportunities arise only at the perimeter** — P1 edge stones with f=1 can be killed if P2 fills the right empty cell to give them e=2.
- **P2 cannot win clean**. The best possible outcome with optimal play is a loss via majority with a narrower margin than the threshold-win P1 ideally pursues.

#### Double-pass / timeout flag
- Game 1: threshold win, no passes.
- Game 2: threshold win, no passes.
- Game 3: **resolved by double-pass majority** at turn 31 (not threshold).

1 of 3 games ended by double-pass. Below the "flag if ≥2" threshold, but notable because it was produced by genuinely correct P2 play — not random passing. In longer/more adversarial play this mode could dominate.

---

## PHASE 3 — STRATEGIC ANALYSIS (joint)

### Are there distinct viable strategies, or does one approach dominate?
Three strategies exist:
1. **P1 CA-cluster grow** — dominant, compound-growth.
2. **P2 opener-capture + growth-race** — catches up in piece count temporarily but loses long-run.
3. **P2 wall-and-stall** — forces double-pass majority; P1 still wins on piece count because of the birth-rule lead.

P1's approach strictly dominates in the games I played. All three games were P1 wins.

### Meaningful counter-play?
**Partially.** P2 has one real move (opener-capture) and one meaningful defensive pattern (wall-off). Neither is sufficient to win against competent P1 play. Counter-play exists tactically but not strategically.

### Short-term vs long-term tension?
Yes:
- P1's opener is exposed to (1,0,1) flip — a short-term risk paid for the long-term CA payoff.
- P2's adjacency-plant in T1 sacrifices a tempo (P2 is starting adjacent to P1's stone instead of building own cluster) for an immediate flip.
- P2's wall-building sacrifices local pressure for territorial cut-off.

### Emergent concepts
- **Cluster immunity**: a cluster with 2×2 or denser is CA-immune.
- **Birth cascades**: one placement can induce 2–3 simultaneous births on the same tick (peak triple-birth observed in Game 2 T9 and T10).
- **Tempo collisions**: deliberate same-cell placement for denial.
- **Adjacency cut-off**: like Go's "isolation" but more absolute — the side cut off literally cannot play into the region.
- **Opening-move capture**: the flip rule on lone pieces creates an opening theory similar to Othello's corner-exposure but operating on the first tick.

### Does topology matter?
Yes — edges have fewer neighbours, which lowers the threshold for cluster immunity. An 8×8 grid with von Neumann adjacency gives a specific growth geometry. On a torus this would play differently (edges removed means P2's wall-and-cut-off strategy breaks — there's nowhere to wall to).

### First-mover advantage — QUANTIFIED
In simultaneous play one would EXPECT first-mover advantage to be ~0. Here it is **catastrophic**:
- I played P1 in Games 1 & 2 (won both, both by threshold, at turns 20 and 18).
- I played P2 in Game 3 with the strongest P2 strategy I could find (opener capture + wall). I still lost.
- 3 of 3 games, P1 wins.
- The winrate table in the game DB shows all 4 training seeds at exactly 0.500 — but these are likely showing `p0 vs p1` within self-play against a mirrored opponent where both are equally weak / equally strong, which is NOT a P1-vs-P2 fairness measure. The GE ranking at 0.4196 hides the asymmetry.

**Conclusion**: the simultaneous turn structure does NOT eliminate first-mover advantage in this game. The CA rule's P1-only perspective completely defeats the simul mechanic's balance intent.

### Seat-identity bias acknowledgment
I reasoned as a single agent across P1 and P2 roles. The seat-swap in Game 3 was imperfect because I was also generating the "strong P1" moves in Game 3 while simultaneously generating the "strong P2" adversary moves. However, even with my genuine best-effort P2 play exploiting the opener-capture trick, I lost. If there is a stronger P2 line I am missing, inter-team comparison will surface it.

---

## PHASE 4 — NOVELTY ADVERSARY

### (a) Broad comparison against known abstract games
- **Go**: territory win is shared, but Go has liberty-based capture, no CA, and strict alternation. Adjacent_to_own placement is not a Go rule. The "cluster immunity" dynamic here superficially resembles Go's life-and-death but operates by a CA threshold rather than by liberty counting.
- **Reversi/Othello**: piece-flipping is shared with the `(1,0,1) → 2` rule, but Othello flips by axis-line bracketing, not by CA neighbour count. Different mechanism.
- **Hex / Y / Havannah / Gomoku / Pente / Connect6 / Amazons / Lines of Action / Mancala / Tumbleweed / Slither**: none share the defining CA + simultaneous + territory-threshold combination.
- **Nim / Blotto / RPS**: this is not an allocation/single-shot game; multi-turn CA dynamics dominate.

### (b) CA literature check
- **Conway's Life (B3/S23)**: player-agnostic; this game is player-aware. No correspondence.
- **HighLife (B36/S23), Day&Night (B3678/S34678)**: player-agnostic.
- **Immigration Game**: 2-colour Life where births inherit the colour of the majority of 3 live neighbours. CLOSEST analog structurally — both are 2-colour CAs with birth/survival rules. BUT: Immigration's rules are Life-like (birth on exactly 3 live, die on <2 or >3); this game has rules like birth on 2 or 4 friendly with tolerance for 1 enemy. Immigration is also SYMMETRIC between colours; this game is asymmetric (only P1 perspective runs). Different CA class.
- The transition table here does not match any published CA I can identify.

### (c) Simultaneous-game comparison
- **Diplomacy**: simultaneous orders, but with negotiation, variable unit types, and support rules. This game has none of those.
- **Gungo (simultaneous Go)**: closest structural peer. Gungo uses simultaneous placement with collision rules, but no CA and Go-style capture. This game replaces Go capture with CA birth/death.
- **Blotto / Scaled RPS**: single-shot; this is multi-turn.

### (d) Topology/coordinate-transformation re-skin argument
Could this be "Game X on an 8×8 grid with different coordinates"? No — the CA table is a specific 9-rule set that is not a known game's rule set. The adjacent_to_own placement + CA-birth combo is distinctive.

### (e) Expert-transfer test
- A **Go expert** would recognise territorial aim and cluster-survival intuition but would misopen by playing a lone central stone that gets captured on T1.
- An **Othello expert** would recognise the corner-capture pattern but have no intuition for CA-birth cascades.
- A **Life expert** would understand neighbour-threshold dynamics but has no intuition for player-aware rules.
No expert gets an immediate advantage; all need new theory for this game.

### Rebuttals

**P1**: "In Game 2 T9 I got a triple birth — one placement produced three new P1 stones via CA propagation on the SAME tick. No known Go or Othello or Hex move has this property. The birth cascade is a unique emergent mechanic."

**P2**: "In Game 3 T1, placing adjacent to P1's opening stone captured it. This means opening theory for this game has NO analog in Go (where a lone stone can't be captured in one move), Othello (lone stones can't be reached on the first move), or Hex (stones never disappear). The opening-capture dynamic is genuinely new."

**Verdict on novelty**: the sim+CA combination IS a new abstract game mechanically. However, its NOVELTY SCORE is held down by two concerns:
1. The **asymmetric CA perspective** (only P1's perspective runs) is almost certainly an unintentional engine artefact rather than designed. If it's a bug, the game's "true" form — with P1/P2 alternating CA perspectives — may be the more interesting design.
2. The **territory threshold + adjacency-cutoff** interaction creates a dominant strategy (P1 cluster-grows; P2 walls).

**Novelty score: 5/10.** The sim+CA hybrid deserves exploration but this specific instantiation is partly a broken game whose P1-only-CA-perspective is the source of both its distinctiveness and its imbalance.

---

## PHASE 5 — VERDICT

**Team ID**: team-17
**Game ID**: 992bf7dfc9f4
**Rules Summary**: 2-player simultaneous placement on an 8×8 grid with von Neumann adjacency, adjacent-to-own placement constraint, and an asymmetric player-aware cellular automaton running from P1's perspective every tick. Win by holding > 62.5% of cells.
**Topology**: 2D grid, 8×8, von Neumann (non-wrap).
**Turn Structure**: **simultaneous** (both players commit, collisions mutually annihilate).

### SCORES (1-10)

- **Strategic Depth: 4** — opening has one critical decision (lone-stone exposure vs collision risk). Mid-game is a cluster-growth compound-interest race with few branching decisions. Endgame can collapse into wall-and-stall. P1's optimal play is a near-deterministic algorithm.

- **Emergent Complexity: 5** — real emergent behaviours exist (birth cascades, cluster immunity, adjacency cutoff, opening-capture, collision denial). However, the P1-only CA perspective means half the potential emergent space (P2-perspective CA) never materialises.

- **Balance: 2** — **I played 3 games and Player 1 won all 3**, including the seat-swap game where I actively adversarially played P2. The "simultaneous turn structure" does NOT neutralise the first-mover advantage because the CA always runs from P1's perspective. The DB's 0.500 winrates appear to be from self-play symmetric setups, which mask the P1-vs-P2 imbalance. Balance here is essentially broken.

- **Novelty (post-adversary): 5** — the simultaneous+CA combination is genuinely new (no Go, Hex, Othello, Life, Immigration, Gungo, Diplomacy analog). BUT the asymmetric CA perspective is likely an engine oversight, not an intentional design feature, which costs novelty credit. The strongest adversary argument — "this is Immigration Game + simultaneous + territorial win" — partially rebutted because Immigration is symmetric between colours while this game is not.

- **Replayability: 3** — the opening-theory space has ~2 meaningful choices (central vs adjacent-to-central, with the known answer depending on what P2 does). Mid-game P1 play is nearly mechanical. There's no reason to replay unless you want to stress-test the P2 wall strategy.

- **Overall "Would I play this again?": 3** — I would play it once more to try the P2 collision-denial opening more carefully, but I don't expect a different outcome. The game is too one-sided to be fun repeatedly.

### CLOSEST KNOWN-GAME ANALOG
**Immigration Game + simultaneous placement + territory-threshold win** — but (a) Immigration is symmetric, this is asymmetric; (b) Immigration rules are Life-like (B3/S23), this is not; (c) Immigration has no adjacency-to-own constraint; (d) Immigration has no territorial threshold. So: not identical, more a cousin than a reskin.

### KILLER FLAWS
1. **P1-only CA perspective** (engine_v2.py:252–254): `steps_per_turn=1` + the alternating-perspective logic means the CA only ever runs from P1's view. This gives P1 all the birth rules for free and P2 none. It is the single biggest flaw.
2. **Opening-move capture exploit**: a lone P1 first move gets CA-flipped on the first tick if P2 plays adjacent. P1 must always fear this; P2 always has this tool. Asymmetric opening theory.
3. **Double-pass majority reachable**: if P2 walls off P1's cluster, P1 has no legal non-suicide move, the game falls through to majority, and the side with more pieces at the wall-off moment wins. This happened in Game 3.
4. **Adjacency-cutoff trap**: the `adjacent_to_own` constraint means a walled-off region is unreachable. Combined with simultaneous play, this produces large dead zones where neither player can contest.
5. **Dead CA entries**: 30 of 75 transition table entries correspond to impossible states (f+e>4) and never fire. Another 36 are identity (no-op). Only 9 transitions are active — the CA is sparse.

### BEST QUALITY
The **CA birth cascade** is genuinely interesting. Placing a single stone can produce 2 or 3 simultaneous births when the placement completes several 2-neighbour empty-cell patterns at once. This gives P1 a compound-interest dynamic that feels novel and produces some delightful tactics (e.g. Game 2 T9's triple birth). If the perspective-asymmetry were fixed so both players got this, the game could be genuinely interesting.

### IMPROVEMENT IDEAS
**Primary fix**: change `steps_per_turn` from 1 to 2, so the CA runs once from P1's perspective AND once from P2's perspective every tick. This would restore symmetry without changing the rule table. (Alternatively: change the "acting_player" selection in simultaneous mode to alternate P1/P2 across ticks, or to run BOTH perspectives on every tick.)

If the above fix is applied, I predict this game becomes a 7/10 novelty candidate and a genuine balance-test for the simul+CA premise.

---

## Appendix — Data from my playthroughs

- Game 1: P1 wins by threshold, turn 20, 41 vs 20.
- Game 2: P1 wins by threshold, turn 18, 41 vs 18.
- Game 3 (seat-swap, I played P2 adversarially): P1 wins by double-pass majority, turn 31, 35 vs 29.

Best single CA tick observed: Game 2 Turn 9 — one P1 placement (5,0)=5 produced three additional P1 stones via CA births at (0,0), (5,1), (4,2). Net +4 from one move. No P2 equivalent exists in the rule table.

Engine cross-checks performed:
- Verified `step_simultaneous` resolution with collision=True (Game 3 T3).
- Verified `(1,0,1) → 2` flip on P1 opening stone (Game 3 T1).
- Verified `(0,2,0) → 1` birth rule (Game 1 T3).
- Verified `(0,2,1) → 1` birth rule (Game 1 T4).
- Verified `(1,1,2) → 0` death rule (Game 3 T23, P1 at (0,3) dying after P2 added a second enemy neighbour).
- Verified that `get_legal_actions` correctly filters by adjacent_to_own per player (Game 3 post-T24, P1 had only `pass` available).
- Verified double-pass resolution via majority (Game 3 T31).
