# Team 2 — Cross-game comparison (all 7 games)

Filed after completing all seven per-game verdicts (order played: A, D, B, F, E, C, G).

## Ranking by Overall score

| Rank | Game | Overall | One-line identity |
|------|------|---------|-------------------|
| 1 | D | 4.3 | 4D-torus actor-perspective CA territory race — arming/harvest economy, immortal triangles, pass-traps |
| 2 | B | 4.2 | Gonnect-like connection Go on 8×8 — dual-purpose dragons, suicide-persistence wall theory |
| 3 | G | 4.2 | Moore-3D 3×-iterated CA connection racer — stable strings, cascade finishes, annihilation-guard |
| 4 | A | 4.1 | Sierpinski-carpet custodian/Hex hybrid — tunnel cells, wall-win duality, seal pockets |
| 5 | C | 3.9 | Parasitic-placement 3D custodian/Hex — flip-tennis, legality shadows, camping draw flaw |
| 6 | E | 3.6 | Stone-count Go with relocations — no-life eye-stuffing, full-board freeze-draw |
| 7 | F | 3.0 | Flat-grid CA territory race — opening-donation degeneracy, rational 2-ply draw |

Tie-break note: B and G both scored 4.2; I rank B above G because B's depth is human-accessible while G's is locked behind CA computation.

## Which would I most want to play again?

**Game B** — even though it sits 0.1 Overall points below my top-ranked D. The divergence is deliberate and informative: D outscores B on novelty and structural soundness, but B produced the single best play experience of the campaign — my scripted opponent legitimately beat me at ply 48 with a dragon that was simultaneously fleeing capture and completing its own connection, and correcting that one-ply lapse flipped the game. I want revenge games in B; I want to *study* D. Relative to the third game I'd revisit (C's engaged mode, before its camping flaw intrudes), B leads by roughly a full experiential point; relative to D, my play-again preference inverts the 0.1-point score gap.

## The single most differentiating mechanic of the top-ranked game

Game D's **actor-perspective CA sweep — tempo literally is territory**. Every action (even a pass) resolves every contested cell on the whole board in the actor's favor: cells at (2,1)/(1,2) mixed neighbor counts belong to whoever moves next. Nothing else in the pack converts initiative into material so directly, and it generates D's entire strategic economy — arming cells for your own next sweep, denying arming to the opponent, immortal-triangle defense, multi-birth cascade turns, sacrifice finishers, and the pass-trap (the leader can never pass because a return pass draws). F and G share the actor-perspective CA template, but F's parameterization collapses into an opening-donation degeneracy and G's into (magnificent) chaos; D's parameterization is the one where the tempo-harvest economy stays legible enough to plan around, which is why it tops my ranking.

## Blind structural observation (offered as evaluator context, not identification)

The seven games appear to form three families with parameter variation: custodian-capture + Hex-connection games (A, C — differing in board topology and in placement-adjacency polarity: own-adjacent vs enemy-adjacent), Go-engine games (B, E — connection win vs stone-count win, both with legal-suicide persistence quirks), and actor-perspective CA games (D, F, G — differing in board, table, iteration count, and win condition). Within each family, the parameter choices swing quality enormously (D 4.3 vs F 3.0 on near-identical chassis), and the recurring cross-family failure mode is the double-pass/draw rule interacting with placement-legality constraints to give losing players a draw veto (C's camping at 24-0, E's board-freeze at 33-31, F's rational 2-ply draw, D's pass-trap). The games that escaped that failure mode (A, B, G) did so because their placement rules keep both players perpetually able and motivated to move.
