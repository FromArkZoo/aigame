# Team 1 — Game F verdict

> Copy this template to `team-1_gameF.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game F` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  9×9 board with a Sierpinski-carpet hole pattern (64 active cells; 17 holes that block adjacency). Players alternate placing stones; after your first stone, every placement must be orthogonally adjacent to one of your own stones (the constraint re-arms to "place anywhere" if you ever lose all stones). After a placement, Othello-style custodian capture runs along both board axes from the placed cell: a consecutive run of enemy stones terminated by your own stone flips to your colour. Win by connection, Hex-style with asymmetric goals: P1 connects the x=0 face to the x=8 face, P2 connects y=0 to y=8, via orthogonal adjacency of own stones (holes block paths). Two consecutive passes draw; at 100 plies the higher stone count wins. The key emergent structure: the carpet's central holes leave only rows {0,2,6,8} and columns {0,2,6,8} as full-length corridors, so all strategy funnels into corridor choice and the 16 corridor crossings.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Connection win fired in 3 of my 4 lines (P2 connection at ply 18, ply 18, and ply 26); double-pass draw fired once (line 3, ply 10). I never reached the 100-ply tiebreak. I also established by argument (and could not refute by play) that super-ko can never actually fire in this game: placements only add or recolor stones, so the stone count strictly increases with every non-pass action and no earlier position can recur — the super-ko rule is vestigial here, alongside the two threshold fields the rules themselves flag as vestigial.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: Three probes, all behaving exactly as documented: (1) placement into a hole (cell 13) is rejected with a clear "cell is a HOLE" message; (2) placement not adjacent to my stones is rejected, and the engine's legal list (e.g. exactly {12, 22, PASS} for a lone stone at (3,2) with one neighbor occupied and one neighbor a hole) matched my hand-computed adjacency model; (3) after my entire side was flipped away (line 4), the legal list expanded to all 54 empty cells, confirming the first_move_anywhere re-arm. No surprises — the engine matched the rules text precisely, including the multi-stone custodian flip rendered as an explicit board delta (`X->O@(0,1) X->O@(0,2)`).

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `54,60,55,51,56,42,57,33,58,24,59,69,68,78,77,15,76,6`
- Plan and what happened: I raced row 6 from the left edge ((0,6) then eastward), reasoning that an edge-anchored run can never be custodian-flipped along its own axis. Scripted-competent P2 instead staked (6,6) — the live crossing of my row and its column — and grew column 6 in both directions. My row hit the O wall at x=6; the bypass race for (6,7) was structurally lost (P2 reaches it in one move from its blob, I need two), and my southern detour via (5,7),(5,8) arrived a tempo late.
- Result (winner, end cause, plies): P2 win, connection (column 6 complete y=0..8), ply 18.

### Line 2 — you as P2
- Moves: `60,56,59,65,58,74,51,47,42,38,33,29,24,20,23,11,22,2`
- Plan and what happened: I played the strategy that beat me in line 1: P1 (scripted competent) opened (6,6) planning row 6; as P2 I immediately staked (2,6) — the intersection of his row with my chosen column 2 — then sealed the hole-constricted south bottleneck ((2,7),(2,8)) before walling north. Every "defensive" move was simultaneously a cell of my own winning path, while P1's pivot (up column 6 to row 2, then west along row 2) needed ≥13 stones against my 9. P1's counterplay never generated a single custodian threat against my wall: I verified the geometry — each of my column cells was either hole-armored ((6,3),(6,4) analogues) or had an unreachable far flank.
- Result: P2 (me) win, connection (column 2 complete y=0..8), ply 18 — P1's fastest remaining completion was ply 25+.

### Line 3 — adversarial / novelty-stress
- Moves: `21,20,22,11,23,12,24,2,81,81`
- What you tried to break / stress, and what happened: I tried to force a custodian capture at a natural collision front (P2 chasing an eastward P1 row-2 chain), and found the adjacency-growth rule strangles every flip attempt: the attacker needs stones at BOTH ends of the victim run, but can only free-place one stone per game and can never legally grow around a moving front (the carpet holes close the flanking routes — row 3's holes at x=3,4,5 kill every southern loop). I then verified pass semantics: single pass answered by a placement does not end the game; two consecutive passes ended it immediately. Separately I probed illegal actions (hole placement, non-adjacent placement) — both cleanly rejected — and confirmed `--values` reports no influence field for this game.
- Result: DRAW, double pass, ply 10. Engine flags and legality checks all consistent.

### Additional lines (optional)
Line 4 (second adversarial line, moves `9,27,18,28,81,29,81,20,81,11,81,2,81,1,81,0,45,38,81,47,81,56,81,65,81,74`): to prove the capture mechanic CAN fire, I had to script P1 as a fully cooperative victim (placing a 2-stone column run between P2's free-placed anchor at (0,3) and the open corner, then passing seven times while P2 walked the ring around the (1,1) hole). P2's placement at (0,0) on ply 16 flipped both P1 stones in one custodian capture, wiping P1 to zero stones — and the engine correctly re-armed first_move_anywhere (P1's legal set became all 54 empty cells). P1 free-placed a block at (0,5); P2 simply pivoted to column 2 and won by connection at ply 26. Conclusion: capture requires opponent cooperation bordering on surrender; in competitive play the mechanic is latent.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Stake a corridor crossing that sits on BOTH your own winning path and the opponent's, then extend your wall so that every defensive move is also a path move. Good moves do double duty; bad moves (like my line-1 edge crawl) spend tempo on cells that only serve one purpose. Sealing the hole-constricted side of a crossing first (e.g. (6,7) south of (6,6), where (7,7) is a hole) buys custodian-proof "armor" for free.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? When P1 raced a naked row (line 1), the punishing response was the intersection stake — one stone that blocked the row AND started the winning column. When P1 pivoted around my wall (line 2), each pivot was punished by the wall cells I was going to play anyway. The game absolutely rewards responding — but asymmetrically: the second staker's responses are free (on-path) while the first player's responses are detours. Custodian "threats" turned out to be non-threats once I checked the adjacency geometry: the flanking cell was always unreachable or a hole.
- Topology/board effects on strategy: The carpet is the game. The central 3×3 hole block plus the four satellite holes reduce the board to four row corridors × four column corridors, so the real decision space is: which corridor, which crossing, which side of the crossing to seal first. Holes armor stones against sandwiches ((4,6) can never be vertically flipped — both vertical neighbors are holes) and create one-cell bottlenecks (column 2's south continuation is uniquely (2,7) because (1,7) and (3,7) flank it awkwardly). The mini-rings around the small holes (e.g. cells circling (1,1)) are the only loops that ever enabled a capture.
- Emergent concepts you'd name (or "none observed"): "Corridor duel" (the reduction of the whole game to 4×4 corridor crossings); "double-duty stake" (the second player's intersection stone that is simultaneously block and path); "hole armor" (stones adjacent to holes on a flip axis are permanently uncapturable); "latent capture" (a rules-prominent mechanic that competitive geometry almost never lets fire).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Choices decide it, but mostly ONE choice: the opening stake. After both stakes are down, the race unfolds close to deterministically — in both competitive lines the winner was decided by move 2-4 and confirmed by counting stones-to-completion. Mid-game agency is real but thin (ordering your wall to pre-empt the opponent's arrival cell).

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  This is Hex with the serial numbers filed off: asymmetric face-to-face connection goals, first player left-right, second player top-bottom, on a square-adjacency board. The Othello custodian rule is bolted on but (as my lines 3-4 show) almost never fires in competitive play, so functionally you are playing a connection race — Hex's core — with a Sierpinski stencil laid over the board, which merely shrinks the strategy space to a 4×4 corridor lattice. The adjacent-to-own-stone growth rule resembles growth games in the Domineering/Amazons family of constrained placement, and "connection game on a holed board" is a known Hex variant genre.
- Honest novelty assessment after arguing that case: The reduction misses two things that actually changed how the game plays. First, the growth constraint inverts Hex's balance: in Hex the first player is favored (hence pie rules); here my play and geometric analysis both say the SECOND player is favored, because the second staker takes the live intersection after seeing the first player's commitment, and the growth rule prevents the first player from contesting distant cells. A re-skin does not usually flip the fundamental advantage. Second, the hole-armor/bottleneck interaction between the carpet and the (mostly latent) custodian rule creates genuinely new local considerations (which side of a crossing to seal first). Net: a recombination with one real emergent property, not a plain re-skin — but also not a fully novel system, since one mechanic (capture) is nearly decorative and another (super-ko) is provably dead code.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — I recognize the ingredient games (Hex, Othello, Sierpinski carpet) but do not recognize this specific composite or any prior score for it.
- P1-role experience sub-score (1-10): 3.5 — playing P1 felt structurally uphill: my tempo advantage evaporated at the opponent's first stake, and my best analysis found no P1 plan that beats a competent P2 wall.
- P2-role experience sub-score (1-10): 5 — the P2 wall strategy was genuinely satisfying to discover and execute: intersection stake, bottleneck seal, armored wall, all engine-confirmed.
- Role-averaged sub-score: 4.25
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 4 — both competitive lines ended in a P2 connection at ply 18, and the geometry (second staker always claims the live corridor intersection, and every P2 defensive move is also a P2 path move while P1's detour costs ≥2 extra stones against a 1-ply tempo lead) suggests this is structural, not an artifact of my play.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.1**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  Game F earns an anchor-level score: the corridor topology is a genuinely good strategic skeleton (lines 1-2 show real opening-level decisions with readable, engine-verifiable consequences), the engine is immaculate (every probe in lines 3-4 behaved exactly as documented, including the multi-stone flip and the first_move_anywhere re-arm), and the emergent second-staker advantage is an interesting property. It stays at 4.1 rather than higher because of three quality deductions established in play: the custodian capture — the game's most distinctive-looking mechanic — is effectively latent (line 4 needed a scripted-surrender victim to make it fire even once), the super-ko rule is provably unreachable, and competitive games appear to be decided within the first four plies (both real lines were counted out by move 4 and ended identically at ply 18), which caps mid-game agency. Anchoring down against drift per the briefing: 4.1, at R8's level and below R19.
