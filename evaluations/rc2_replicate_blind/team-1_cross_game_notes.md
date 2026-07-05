# Team 1 — Cross-game comparison (all 7 games)

Filed after completing all seven per-game verdicts (order played: F, G, C, B, E, D, A).
All scores anchored per the briefing (R8 4.10, R19 4.375, R20 3.73, R21 3.69; 5.0 ceiling; anchored DOWN).

## Ranking by Overall score

| Rank | Game | Overall | One-line character |
|------|------|---------|--------------------|
| 1 | C | 4.4 | 4D-torus actor-CA territory race: bombs, leeches, fortress planes — most novel AND controllably deep |
| 2 | G | 4.3 | Connection-Go (Gonnect-like): ko, semeai, eye-fill kills — deepest classical fighting, weakest novelty |
| 3 | A | 4.3 | 2D actor-CA territory: donation openings, conversion windows, 2×2 immunity — best CA-game agency |
| 4 | D | 4.2 | Enemy-adjacent placement + 3D Othello flips + connection: most original placement rule, draw-attractor-riddled |
| 5 | E | 4.2 | 3D Moore triple-iteration CA connection: detonating completions, stretched chains — spectacular but chaotic |
| 6 | F | 4.1 | Sierpinski-carpet Hex with latent custodian capture: clean corridor duel, decided by ply 4, P2-tilted |
| 7 | B | 4.0 | Stone-count Go with suicide-stays: whole-army captures and immortal pockets — high drama, degenerate corners |

Tie-breaks: G over A because G's move-to-move tactical depth (a real ko, a counted semeai, capture races) exceeds anything in A, and A carries a root-level oddity (the empty board is one double-pass from a final position); D over E because D's strategy space (soil control, anchor warfare, quarantine) was legible enough to reason about and act on, while E's three-iteration cascades repeatedly outran even careful analysis — equal scores, different failure modes (hollow equilibrium vs. low tactical legibility).

## Which would I most want to play again, and by how much?

**Game C, by 0.1 Overall points** over the runner-up (G at 4.3). Beyond the score gap, C is the game where my strongest strategic discoveries happened (the 5-stone bomb, engine-verified with a bonus birth through the torus seam; the leech, which won a full game by feeding on the opponent's structure), and the one whose losing lines most made me want another attempt — the mark of a game with unexplored depth rather than exhausted depth.

## The single most differentiating mechanic of the top-ranked game

The **actor-perspective CA harvest**: after every action, every contested empty cell at a 2:1 mixed neighborhood resolves to whoever just moved. This one rule converts tempo itself into territory — it creates the bomb (one placement detonating four simultaneous births along corridor geometry), the leech (building adjacent to the enemy so THEIR stones supply your birth counts), and pending-cell timing (never complete a pattern the opponent will harvest on their tick). Layered over the 4D 3-torus — where every axis line is a 3-clique and wrap adjacency produces births flat-board intuition misses — it yields strategy that is genuinely new while remaining calculable: none of the other six games has a mechanic that is simultaneously this original and this governable. (Games A and E share the chassis but not the effect: A's table softens it into a slower conversion war, and E's triple iteration pushes the same idea past the edge of what a player can reliably read.)

## Slate-level observations (offered for whatever they're worth)

- Three of seven games (C, E, A) share one visible framework (actor-perspective totalistic CA, placement constraints, identical helper text), and two pairs share win-condition skeletons (F/G-style connection, B/C/A-style territory). I evaluated each on its own merits and discounted within-slate chassis reuse under novelty, per game files.
- The count-blind double-pass draw rule appears in all seven games and is load-bearing in three verdicts (B: 32-0 position drawn; D: starved draw at 12-1 and the spite-pass button; E: an accidental draw from two super-ko-rolled futile moves). If one engine-level rule were to be reconsidered slate-wide, it is this one.
- Fairness probes across the slate: F=4 (P2-leaning, structural), G=3, C=3, B=3, E=3, D=3.5 (mild P2 lean), A=3. Role win split from my driven lines: P1-role wins in F(0/1), G(1/1), C(1/1), B(1/1), E(1/1), D(0/1 + draw), A(1/1); P2-role wins in G, C, B, E, D, A (F P2-role: win as scripted-strategy but my driven line 2 won as P2; see files). No game produced an unwinnable seat in my play, but F's corridor geometry is the closest to a structural tilt.
