# Team 1 — Game G verdict

> Copy this template to `team-1_gameG.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game G` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  8×8 plain grid, von Neumann adjacency, free placement anywhere empty (no growth constraint). Go-style surround capture: after your placement, any adjacent enemy group with zero liberties is removed. Win by asymmetric Hex-style connection: P1 connects the top face (y=0) to the bottom face (y=7); P2 connects the left face (x=0) to the right face (x=7). Positional super-ko is enforced by rolling the offending action back into a PASS. Two consecutive passes draw; 100-ply limit falls back to a stone-count tiebreak. There is also an influence field: each placement radiates strength 0.715 with decay 0.751 out to distance 3, positive for P1, negative for P2 — but nothing in the rules ties it to legality or winning, and the rules themselves document "ghost influence" (captured stones' influence persists forever), so it is decoration.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Connection win twice (my line 1: P1 win at ply 43; my line 2: P2 win at ply 28); double-pass draw once (line 3, ply 11). No game reached the 100-ply tiebreak, though my analysis of blockade positions suggests high-level play could get there via mutual walls plus two-eyed living groups.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: Two genuine surprises. (1) Suicide is legal and the stone SURVIVES: in line 3 O placed at (0,0) with both neighbors X — zero liberties — and the stone stayed on the board permanently (capture only ever triggers when someone places next to an enemy group, and a 0-liberty group has no adjacent empty cell to place into, so it is effectively immortal unless a neighboring stone is first captured). This creates "immortal blocker" stones the Go-trained eye does not expect, and since connection paths count all your stones, a suicide stone can even serve as a path link. (2) The super-ko rollback converts a capture-retake into a PASS, silently burning the mover's turn — in line 1 my scripted P2 lost a full tempo to it at ply 16, and I verified the identical shape again at ply 35 (my own recapture would have recreated the ply-33 position, so I had to play a connecting move first, exactly like a real ko fight). I also verified ghost influence numerically: after O(0,4) was captured, the influence sum at that cell was +1.20, which only reconciles with the placement history if the dead stone's −0.715 is still being counted.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `28,35,36,44,45,43,37,53,54,62,46,55,47,61,63,55,55,20,21,13,14,22,23,31,39,30,29,15,7,5,23,6,38,15,22,7,12,4,3,18,4,17,13`
- Plan and what happened: I descended the center as X while scripted-competent O counter-walled. The southeast corner produced a real Go fight: I captured O(7,6) with (7,7), O's retake was super-ko-banned (rolled back to a pass), and I sealed the bottom. The north became a capture war: O captured my (7,2) cutting stone (a genuinely strong scripted reply), I re-took at (7,2), killed O's three-stone cutting group {(6,2),(6,3),(7,3)} with (6,4) — a 4-cell delta — then won the semeai against O's entire five-stone northern edge group, capturing six stones with (3,0) after O extended into atari, and finally linked (4,0)-(4,1)-(5,1)-(5,2) down my central spine.
- Result (winner, end cause, plies): P1 (me) win, connection top-to-bottom, ply 43. Final count P1=20, P2=9 after four separate capture events.

### Line 2 — you as P2
- Moves: `27,36,35,43,34,42,33,41,32,40,44,52,45,53,46,54,51,50,59,60,58,57,47,55,51,59,19,51`
- Plan and what happened: As O I built a row-5 wall under X's descent, sealing each western probe ((2,4)→(2,5), (1,4)→(1,5), (0,4)→(0,5)). X wedged at (4,5) — the critical test — and I atari'd from below; X's escape group crawled east along my wall, and every escape stone it added was matched by a wall stone of mine one row lower that doubled as my own path. When X blocked my final link at (3,6) I ran the three-stone capture ladder against the bottom edge ((2,6)-atari, (4,7)-atari, then (1,7) capturing {(3,6),(3,7),(2,7)}), sealed the east end at (7,6) BEFORE revealing my last link, killed X's one-liberty re-block with (3,7), and connected with (3,6).
- Result: P2 (me) win, connection left-to-right at ply 28: (0,5)-(1,5)-(2,5)-(3,5)-(3,6)-(4,6)-(5,6)-(6,6)-(7,6). Move-order mattered: my analysis showed that revealing (3,6) before sealing (7,6) loses to X's east-side counter-ladder, which would have completed X's own column-7 path while I chased.
- 
### Line 3 — adversarial / novelty-stress
- Moves: `1,32,8,0,24,45,40,46,33,64,64`
- What you tried to break / stress, and what happened: Three probes. (1) Suicide: O played (0,0) with zero liberties, capturing nothing — the engine placed it and left it there (immortal 0-liberty stone; see Phase 1). (2) Ghost influence: I surrounded and captured O(0,4) with (0,3),(0,5),(1,4), then rendered --values: the captured stone's negative influence is still in the field (cell reads +1.20, not the +1.91 the live stones alone would give). (3) Pass semantics: a single pass answered by a placement continues the game; two consecutive passes ended it as a draw. Earlier, in line 1, I also stress-tested the super-ko rule twice — both a rollback-to-pass and a legal delayed recapture.
- Result: DRAW, double pass, ply 11. All engine behaviors flagged and consistent, including the two surprises documented in Phase 1.

### Additional lines (optional)
The line-1 prefix up to ply 16 doubles as a super-ko demonstration line: `...,63,55` — O's attempted ko retake at (7,6) was rolled back to a PASS with an explicit `!! SUPER-KO` flag. I confirmed the flag fires on the position-recreation check, not merely on the cell: my own later recapture of the same point (ply 35 area) was allowed once the surrounding stones had changed.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Dual-purpose stones: the best moves simultaneously extend your connection and reduce the opponent's (my (5,3) in line 1 linked three of my groups while putting a three-stone O group in atari; O's (7,1) in the same line captured my cutting stone while blocking column 7). The second tactical pillar is the wedge-and-ladder: invading an enemy wall gap creates a 2-liberty stone whose escape ladder the defender must read precisely — chasing in the wrong direction hands the attacker a completed path (my line-2 analysis found the losing chase explicitly: laddering X down column 7 would have built X's winning column).
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Constantly. Every wedge had a correct atari side and a wrong one; every block had a capture answer; O's strongest scripted move (capturing my (7,2)) forced me to win a semeai rather than just race. The ko machinery adds tempo tactics: a banned retake costs a full move, so setting up positions where the opponent's natural reply is ko-banned is real, engine-enforced counterplay.
- Topology/board effects on strategy: The plain 8×8 grid means no terrain — all structure is player-made walls. Von Neumann adjacency makes diagonals non-connecting for BOTH sides, so crosscuts are mutual cutting fights (unlike Hex, where one side's diagonal connects). Edges are capture amplifiers: every kill in my lines happened against an edge, where escape ladders run out of liberties — but an edge ladder along your own winning axis is an escape ladder (the column-7 motif appeared in both lines 1 and 2).
- Emergent concepts you'd name (or "none observed"): "Dual-purpose stone" (block that is also path); "wedge ladder" (wall invasion whose refutation direction decides the game); "ko tempo theft" (super-ko rollback burns the mover's turn); "immortal suicide blocker" (the 0-liberty stone quirk — never exploited in my competitive lines but clearly exploitable); "edge semeai" (capture races resolve at the board rim, which is also where connections terminate — the same real estate serves both purposes, which is the game's best idea).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? My choices, thoroughly. Line 1 swung on move-level tactics (the (6,4) capture, the semeai count at (3,0)); line 2 swung on move ORDER (seal (7,6) before revealing (3,6)). Unlike a pure race, mid-game reversals are available at every stage via capture. This is the highest-agency game of the set I have played so far.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  This is Gonnect (Neto, 2000) — Go rules with a connect-opposite-sides win — with the serial numbers lightly filed: same free placement, same surround capture, same super-ko, same "connection through your own stones" goal on a small Go-like board. The deltas are minor: goals are asymmetric per player (in Gonnect either player may connect either pair of sides), passing is allowed (Gonnect forbids it) with a double-pass draw bolted on, and there's a cosmetic influence field that affects nothing. One could also call it "Hex with Go captures on a square grid," a known variant family.
- Honest novelty assessment after arguing that case: The Gonnect reduction is strong — stronger than any reduction available for the other games I've evaluated so far — and the influence field being provably inert makes the most distinctive-looking rules text pure decoration. What survives the reduction: the asymmetric axis assignment does change opening theory (each player has a preferred wall orientation, making second-player blocking walls double-purposed in a way Gonnect's symmetric goals don't force), and the legal-suicide-stone quirk is a real rules divergence from all Go-family priors (Go removes or forbids such stones) with genuine tactical implications. Net: low-to-moderate novelty as a design, but the deviations are load-bearing, not cosmetic.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): I recognize the design as very close to Gonnect (a published connection-Go variant). I do not recognize this specific instance or recall any prior score for it.
- P1-role experience sub-score (1-10): 4.5 — line 1 was the best single game of my evaluation so far: ko, semeai, a six-stone kill, and a breakthrough that I had to earn tactically.
- P2-role experience sub-score (1-10): 4.5 — the wall-and-wedge-capture game as O was equally rich, and the move-order subtlety at the end ((7,6) before (3,6)) was a genuine find.
- Role-averaged sub-score: 4.5
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 3 — each role won its competitive line (P1 at ply 43, P2 at ply 28), P1's tempo edge and P2's dual-purpose blocking traded off visibly, and no structural one-way street appeared in either direction.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.3**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  Game G delivered the deepest and most decision-dense play of my slate: line 1 contained an engine-adjudicated ko, two atari exchanges, a three-stone and a six-stone capture, and a semeai whose count decided the game; line 2 was won by capture-ladder reading and endgame move-order — all of it my choices, none of it race-on-rails. Fairness looks healthy (one win each way). It loses ground on novelty — the Gonnect reduction is uncomfortably tight, and the influence field is verifiably inert decoration (ghost influence and all), which pads the rules without touching the game. The suicide-survives quirk is interesting but smells like an artifact rather than a design choice, and could be degenerate at high level (permanent unkillable blockers). Weighing best-in-slate play quality against derivative design and one inert mechanic: 4.3, just under the R19 anchor, anchored down per the briefing.
