# Team 1 — Game A verdict

> Copy this template to `team-1_gameA.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game A` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  8×8 grid, von Neumann adjacency. Placement must touch ANY stone (either colour; first stone anywhere), MOVE actions relocate one of your stones to an adjacent cell and OVERWRITE enemy stones (verified capture-by-move), and a one-iteration CA runs after every action from the actor's perspective. The live table rows: empty cells with a 2:1 mixed neighborhood (either ratio) birth a stone for the ACTOR; a totally isolated stone flips to the NON-actor every tick (so your first placement instantly becomes the opponent's — the "donation"); a stone with exactly 3 actor-neighbors and exactly 1 own-support converts to the actor; a stone of the actor's with 1 own + 3 enemy neighbors defects to the opponent. Win: first to own 30 of 64 cells; 100-ply stone-count tiebreak; double-pass draw; super-ko (post-CA).
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Threshold win in both competitive lines (line 1: P1 reaches exactly 30 at ply 53; line 2: P2 reaches exactly 30 at ply 58). Double-pass draws in the probes: the instant ply-2 draw (both players pass the empty board) and the ply-3 draw in the oscillation exhibit. No tiebreak.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: (1) The donation renders directly in the placement delta — P1 places at (3,3) and the delta reads ".->O@(3,3)": the stone materializes as the opponent's. (2) A PASS mutates the board: P2's pass flipped the lone stone to X (flagged CA mutation on a pass tick). (3) The second consecutive pass produced NO mutation ("board delta: none") where the table said the lone stone should flip again — consistent with the post-CA super-ko check suppressing an oscillation that would recreate an earlier position — and the game ended as a draw with the stone stranded. (4) Mid-game, the CA repeatedly out-ran my expectations in BOTH directions: X birthed a stone inside my zone off my own two stones (the 1F+2E actor rule), and later my border chain converted two X stones in one tick while simultaneously making my own old wedge defect at (1F,3E) — all reconcilable with the table afterwards.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `64,27,35,28,36,29,20,30,37,38,21,31,22,39,23,46,45,53,44,47,26,54,34,52,42,43,19,51,18,50,41,49,33,40,25,58,17,57,32,48,24,56,16,62,11,63,10,55,9,61,8,60,12,59,13`
- Plan and what happened: I opened with the pass-gambit; scripted P2 placed and donated its stone to me. From the gift I snowballed: converted P2's chain stones whenever they sat at exactly one own-support ((4,3) at ply 7, (5,3) at ply 11, and later the engine auto-converted P2's (3,5) wedge for me), pre-filled the border cells where P2 could have birth-farmed off my stones ((0,4) and the y=5 band), and out-expanded P2's southeast fortress into the larger northwest territory.
- Result (winner, end cause, plies): P1 (me) win, territory threshold (exactly 30/64), ply 53, final 30-22.

### Line 2 — you as P2
- Moves: `64,27,35,28,36,20,29,21,12,152,19,37,21,30,22,38,13,46,44,52,43,53,51,60,59,61,18,54,26,62,34,63,42,55,50,47,58,39,11,31,10,23,9,4,17,2,25,14,33,5,41,40,49,6,57,1,8,15`
- Plan and what happened: This time scripted P1 played the pass-gambit, forcing ME to donate — the fairness-critical test. As donor I fought back with the full toolkit: an early MOVE-overwrite (action 152, my (5,2) onto X's (5,3) — capture-by-move verified), the discovery that 2×2 blocks are conversion-immune (conversion requires EXACTLY one own-support), a southeast fortress built on that principle, and a same-tick counter-conversion when X's CA-birthed spear at (5,5) split my line (my (5,6) converted it right back). X's southwest wall squeezed my territory below 30 on my own count — but X's mid-game fill order marched into my row-0/row-1 chain's conversion range, and at ply 50 one placement of mine converted X's (5,1) (my third stone closing the 3F,1E pattern) while my old (4,2) wedge simultaneously defected to X — a double-edged CA tick that still left me ahead. I finished 30-27.
- Result: P2 (me) win, territory threshold, ply 58. The donor recovered and won — evidence the donation costs roughly a tempo, not the game.

### Line 3 — adversarial / novelty-stress
- Moves: `64,64` and `27,64,64`
- What you tried to break / stress, and what happened: (1) The rational-equilibrium probe: if both players understand the donation, does anyone have to move? No — pass, pass, game over: DRAW at ply 2 on an empty board. The opening is a genuine zugzwang-flavoured standoff (softened by line 2's evidence that donating is playable). (2) The oscillating lone stone: P1 places (donates, stone appears as O), P2 passes (stone flips to X via CA-on-pass), P1 passes (no mutation — oscillation apparently super-ko-suppressed — and double pass ends it as a draw with the twice-flipped stone stranded as X). (3) MOVE-overwrite and move-id encoding were verified inside line 2 (actions 152 and the earlier probe grammar from the same engine family). All flags and deltas consistent.
- Result: DRAW ply 2; DRAW ply 3. Both exhibits document the game's strangest structural corner: the empty board is already a legal final position.

### Additional lines (optional)
None — lines 1 and 2 are long (53 and 58 plies) and between them exercise both roles, both opening postures (beneficiary and donor), births, conversions, defections, wedges, fortresses, and move-captures.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Support-count arithmetic: keep your own stones at 0 or 2+ own-support (exactly-1 is the conversion window; totally isolated is defection), force the OPPONENT's stones into exactly-1 territory and wrap them with three of yours, and place so that frontier empties show 2-of-yours + 1-of-theirs on YOUR tick (actor births). The MOVE-overwrite is the eraser for enemy wedges that the CA can't touch.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Constantly: X's spear into my fortress was punished by a same-tick counter-conversion; my careless wedge at (4,2) was eventually punished by the (1F,3E) defection rule the moment its neighborhood tipped; X's fill order was punished by my waiting conversion chain (two stones in one tick at ply 50). The CA means responses often fire simultaneously with your own plans — a single placement can convert, birth, and defect in the same delta, and reading those combinations IS the game.
- Topology/board effects on strategy: Von Neumann 4-adjacency keeps the CA table small enough to actually calculate (unlike its 26-neighbor sibling in this slate), edge and corner cells have fewer neighbors so conversion patterns (needing 3 actor-neighbors) are impossible against 3-neighbor edge cells — making edge chains structurally safe — and the any-stone placement adjacency fuses the whole game into one connected mass where every frontier is shared.
- Emergent concepts you'd name (or "none observed"): "Donation" (first stone defects — the opening is a gift-exchange negotiation); "pass-gambit" (refusing to move first); "conversion window" (exactly-1 own-support is the only vulnerable state); "fortress arithmetic" (2×2 blocks are permanently conversion-immune); "actor harvest" (2:1 mixed empties always birth to the mover); "edge sanctuaries" (3-neighbor cells can never be wrapped); "wedge-and-eraser" (inert enemy stones vs. move-overwrite).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Highest agency of the slate's three CA games: the 1-iteration CA is calculable, and both my wins trace to specific chosen techniques (pre-filling birth cells in line 1; the fortress and the ply-50 conversion trap in line 2). The engine still produced genuine surprises (the (5,5) birth, my wedge's defection), but they were recoverable, not decisive — I mispredicted details, never the plot.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  It is the third game in this slate built on the same actor-perspective-CA chassis (with C and E) — dial changes only: 2D grid, 1 iteration, territory-30 goal, plus a move action. Externally, two-player Life-variants and majority-conversion cellular games are known genres, "surround to convert" echoes Othello-family flipping, and first-to-N-cells is a stock territory dial. An unsympathetic evaluator calls it "the slate's CA engine, easy mode."
- Honest novelty assessment after arguing that case: The chassis-sharing discount is real (this is my third rodeo with actor-perspective tables, and the skills transferred). But A's specific table produces the slate's most distinctive OPENING phenomenon — the donation/zugzwang standoff, where placing first is a gift and the empty board is one double-pass from being a final position — and its conversion-window arithmetic (exactly-1 support vulnerable, 2×2 immune) is a crisp, learnable combat system that neither sibling has. Moderate novelty overall: derivative framework, genuinely fresh personality.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — no external prior recognized; noted mechanical kinship to slate-games C and E (same CA framework, different parameters), treated as a novelty discount, not an identification.
- P1-role experience sub-score (1-10): 4.5 — line 1's snowball required real technique (conversion timing, birth-cell pre-filling) and the pass-gambit opening decision was genuinely interesting.
- P2-role experience sub-score (1-10): 4.5 — the donor comeback in line 2 was the most satisfying long grind of my slate: fortress arithmetic discovered under pressure, and a conversion trap that swung the game at ply 50.
- Role-averaged sub-score: 4.5
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 3 — the side I drove won both competitive lines from OPPOSITE opening postures (beneficiary 30-22, donor 30-27), which suggests the donation costs about a tempo and skill dominates structure; the deeper asymmetry (whoever must break the pass standoff donates) applies to whichever player blinks, not to a fixed seat.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.3**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  Game A is the best-playing of the slate's three CA games: the 1-iteration table is calculable enough that my plans (line 1's conversion snowball, line 2's fortress-and-trap comeback) succeeded through foresight rather than luck, both lines ran 50+ plies of continuously meaningful decisions, and the support-count combat system (conversion windows, 2×2 immunity, edge sanctuaries) is crisp emergent design. Its blemishes: the opening donation makes pass-the-hot-potato the theoretically correct start and leaves an instant ply-2 draw sitting at the root (engine-verified in line 3) — a structural oddity even if line 2 shows donating is playable — and the chassis is shared with two slate siblings, discounting novelty. Balanced (one win each way from opposite postures), clean engine, high agency: 4.3, just under R19.
