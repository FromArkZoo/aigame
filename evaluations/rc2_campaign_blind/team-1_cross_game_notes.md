# Team 1 — Cross-game comparison (after all 7 verdicts filed)

Evaluation order played: D, G, B, C, E, A, F. All lines engine-verified
via `play.py`; every decisive claim below traces to a terminal state the
engine printed.

## Ranking by Overall score

| Rank | Game | Overall | One-line character |
|------|------|---------|--------------------|
| 1 | C | 4.5 | Connection-Othello with the enemy-adjacency "gate" economy — novel, legible, knife-sharp 20-ply fights |
| 2 | D | 4.4 | 4-D torus actor-CA harvest race — deepest emergent tactics (coups, suicide-strikes, cold wars), machine-only calculation load |
| 3 | B | 4.2 | Gonnect-like Go-capture connection race — most human-playable, least novel, undead-stone and draw-loophole warts |
| 4 | A | 4.1 | Hex-family crawl race on a Sierpinski carpet — crisp one-tempo finishes and real opening theory, capture layer nearly vestigial |
| 5 | G | 4.1 | Moore-3D connection CA — highest raw novelty (founder's-curse ko parity, frozen triangles), unplayably treacherous |
| 6 | F | 3.95 | Flat actor-CA majority grind — brilliant isolation-flip rule (poisoned opener), chaotic and foggy in play |
| 7 | E | 3.9 | Stone-scoring Go with movement — sound but derivative, with a degenerate 40-ply shuffle endgame |

Tiebreak note (A vs G, both 4.1): I rank A ahead on playability and
mistake-attributability; G ahead on novelty. A's decisive games felt like
games; G's felt like defusing ordnance.

## Which would I most want to play again?

**Game C, by 0.1 Overall points over Game D** (4.5 v 4.4) — and by a
wider subjective margin than the score suggests. C is the only entry
where every one of my losses and wins traced to a crisp, human-graspable
refutation (an anchored flip, a self-ungating block, an illegal defense),
and both decisive lines ended with a placement that flipped the winning
path into existence — the most satisfying terminal moves I played all
campaign. D I'd happily replay with a solver at hand; C I'd replay for
fun.

## The single most differentiating mechanic of the top-ranked game

**C's enemy-adjacency placement gate**: every stone after your first must
be placed adjacent to an ENEMY stone. This one constraint generates the
game's entire identity — you can never privately develop or reinforce
your own structure; every defensive move must be legally "earned" through
contact; blocking moves systematically UNGATE the opponent by giving them
placement rights next to your new stone; and whole classes of natural
defenses are simply illegal (my Line-2 opponent could not block my
winning cell at all). No other game in the pack — and no published game I
know — builds its strategy space on that inversion; it is the difference
between playing a connection game and negotiating one.

## Cross-cutting observations (offered for the record)

- End-cause coverage across my 21 filed lines: connection wins ×8,
  territory-threshold win ×1 (F, step 67), turn-limit tiebreaks ×3
  (E ×2, F ×1), double-pass draws ×9 (including engineered stress
  terminals; two arrived via super-ko rollbacks converting real moves
  into passes).
- The engine family shares systemic quirks that shaped every game where
  they applied: no self-capture check (undead zero-liberty stones in B
  and E), double-pass-draw as an absolute out (fill-out draw loopholes in
  B/E; gate-lock draws in C), and super-ko rollback-to-pass (weaponizable:
  it ended games in B, E, and G).
- Fairness across the pack: no game showed strong seat bias in my play;
  the recurring structural pattern is RESPONDER advantage in the CA games
  (D, F: mixed cells belong to whoever acts next; F additionally taxes
  the opener with a forced donation) and first-mover tempo in the
  connection games (A, C), partially offset by counter-corner/counter-
  blocking resources. My 12 decisive-or-tiebreak results split 6–6
  between the seats.
