# Team 3 — Cross-game comparison

Filed after all seven per-game verdicts (team-3_gameA..G.md). Scores are the Overall
(1–10) from each Phase 5, anchored per the briefing (R8 4.10, R19 4.375, R20 3.73,
R21 3.69; 5.0 never cleared).

## Ranking (best → worst)

| Rank | Game | Overall | One-line summary |
|------|------|---------|------------------|
| 1 | D | 4.6 | 4D-torus CA race; calculable "harvest strikes"; fast, decisive, no degeneracy found |
| 2 | F | 4.6 | Actor-perspective CA flip game; two photo-finish races; gift-opening and opaque table blemishes |
| 3 | B | 4.5 | Go-capture + crosswise connection; dual-purpose-wall economy; one-tempo photo-finish |
| 4 | G | 4.2 | Moore-3D triple-CA; brilliant sparse-phase tactics; dense-phase cascades exceed human lookahead |
| 5 | A | 4.0 | Sierpinski custodian/connection race; good corridor terrain; capture layer nearly inert, over by ply ~10 |
| 6 | C | 3.8 | 3D Othello-flip connection; deepest per-move tactics in the pack; broken by the ply-2 pass-draw and P1 rush |
| 7 | E | 3.5 | Go variant; genuine dragon hunts; every competent game ends in a forced draw (zombie-mass exploit) |

D and F carry equal Overalls; D ranks above F on the tiebreak that matters to me:
D was the only game in the pack where my adversarial line found NO degeneracy (F has
the gift/pass opening and farming-arithmetic endgames), and D's fairness profile was
the most balanced of the seven (my lines split 1–1 by strike timing, vs F's double
P2 win).

## Most want to play again

**Game D — by a whisker (0.0 Overall points over F on paper; call it +0.1 of pure
replay appetite, and +0.1 to +0.4 over the rest of the field).** F gave me the two
most dramatic single moments of the campaign (a 30–29 finish decided by a ply-1 pass;
a self-extinction overwrite), but D is the game whose next match I can already feel:
I know the strike-ladder exists, I believe perfect P1 wins it, and I want to test
whether a P2 counter-ladder (pre-spending shared zones, sacrificial poising) can
refute it. A game that leaves you with a concrete, testable strategic conjecture
after two plays is the one you replay.

## The single most differentiating mechanic of the top-ranked game

**The poised-layer harvest strike.** In D, the actor-perspective mixed-3 birth rule
(empty cell at 1F+2E or 2F+1E births a stone for whoever just acted) interacts with
the 3^4-torus geometry (planes offset in two coordinates never touch, but the layer
between them puts every cell at exactly 1 friendly + 1 enemy) to create chargeable,
calculable detonations: one placement tips an entire layer and births 4–6 stones in
a single action. No other game in the pack has anything like it — B/A/C reward
line-by-line reading, F/G have CA births but they arrive as weather (F's border
dribbles, G's chaotic cascades). Only D turns the automaton into ARTILLERY: you
build quiet shapes, you charge a zone, and you choose the tick it fires. Both of my
decisive results (P1's ply-19 strike in Line 1, my ply-18 first-strike as P2 in
Line 2) were exactly timed, exactly predicted uses of this one mechanic — it converts
a stone race into a zone-timing duel, and that is what puts D at the top.

## Cross-cutting observations (offered for the record)

- **Actor-perspective CA is the pack's signature idea**, appearing in D, F, G. It is
  strongest where its consequences stay computable (D: 1 iteration, no flips) and
  weakest where they don't (G: 3 iterations × Moore-26 = chaos).
- **Every non-CA game's failure mode was an endgame/meta degeneracy**: B's ko-pass
  instant draw (minor), A's inert capture layer (moderate), C's ply-2 pass-draw
  (severe), E's zombie-mass forced draw (fatal). The engine family's shared rules
  (double-pass draw, no suicide check, capture-on-adjacent-placement-only) are the
  common root cause of C/E's breakage.
- **First-mover advantage was the modal fairness finding**: P1-favored in B, C, G
  (and A P2-favored via counter-seeding; F P2-favored via endgame parity; D/E near
  balanced). Only D and E drew a 3 on the fairness probe, and E's balance is the
  balance of universal draws.
- **Win-split across my played role-lines** (evaluator as stated role, decisive
  games only): as-P1 wins: B✓, C✓, G✓, D✓, A✗(P2 won), F✗(P2 won); as-P2 wins:
  A✓, F✓, D✓; as-P2 losses: B, C, E(draw), G. Net: the seat I drove won 7 of 12
  decisive lines — skill transfer between seats was real but seat-structure mattered
  more in B/C/G (P1) and A/F (P2).
