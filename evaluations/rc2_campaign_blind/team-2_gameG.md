# Team 2 — Game G verdict

> Copy this template to `team-2_gameG.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game G` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  4×4×4 board with MOORE adjacency (all Chebyshev-1 neighbors — 7 to 26 per cell). Placement must touch one of your own stones (first stone anywhere, re-arming at zero) and may target ANY cell: placing on an enemy stone REPLACES it; placing on your own stone is a legal no-op — but engine-verified, the own-adjacency constraint still applies, so a lone stone cannot no-op on itself. After EVERY action the CA runs THREE times from the actor's perspective; only neighbor counts 0-4 are in the table, so dense regions freeze. Key transitions: empty (3,3)→actor birth; own stones die at (0,1),(0,3),(3,0) and defect at (1,2),(3,1),(4,1); enemy stones die at (1,0),(0,3),(3,0) and defect to the actor at (1,3),(1,4),(2,1). Win: P1 connects z=0↔z=3, P2 connects x=0↔x=3 (Moore paths — diagonals count). 141-step limit → majority; double pass = draw; super-ko on the post-CA position.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Connection wins in all three real lines: P1 at ply 9, P2 at ply 14, P2 at ply 24 (policy baseline). No draws, no turn-limit games — Moore paths need only 4 stones, so races are decided fast.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: (1) Super-ko acts as an "annihilation guard": a lone stone attacking a lone stone would mutually annihilate (attacker dies via (0,1), victim via (1,0)) and recreate the initial empty board — so the engine rolls the attack back into a PASS (verified with `21,42`). (2) The board literally EMPTIED at ply 5 of the baseline line and the game kept going through re-arm placements. (3) A single placement can swing the board violently: ply 18 of the baseline flipped the count from P1=4/P2=1 to P1=1/P2=5; my Line-2 winning move produced a 5-cell delta (2 enemy stones flipped, 3 births) that completed my path *through the CA*, not the placement. (4) Own-stone no-op placements are legal but still require a neighboring own stone (engine rejected the lone-stone case).

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `0,0,3,1,19,4,34,0,49`
- Plan and what happened: I drove P1 with a two-ply-lookahead calculator built from the printed CA table (validated move-for-move against engine deltas over 19+ plies before trusting it). After the opening corner exchange (P2 replaced my (0,0,0); replacement is this game's direct capture), I re-armed at the opposite corner and raced a DIAGONAL z-chain — (3,0,0),(3,0,1),(2,0,2),(1,0,3) — exploiting Moore adjacency, where a 4-chain can slide diagonally and each stone keeps ≤2 own neighbors (straight/diagonal string middles at (2,0) and ends at (1,0) are fixed points of the CA table). Scripted P2 spent its tempo re-replacing my corner instead of putting two stones onto my chain (the only way to steal a string stone is the (2,1) defection, which needs TWO adjacent enemies), and my ply-9 placement completed z=0→z=3.
- Result (winner, end cause, plies): P1 win, connection, 9 plies.

### Line 2 — you as P2
- Moves: `0,2,17,3,2,6,3,12,0,9,0,6,1,1`
- Plan and what happened: Roles swapped: scripted P1 raced with the depth-1 policy while I drove P2 with the deeper search. The opening was a replacement knife-fight in the low-x planes (both of us overwriting and annihilating stones — the count seesawed 1-1, 2-1, 1-2 for ten plies). My last two moves set up a cascade: ply 13 P1 rebuilt at (1,0,0), and my ply-14 placement at (1,0,0)... rather, at cell 1, triggered a CA avalanche — delta: my two flips `X->O@(1,0,0)`, `X->O@(3,0,0)` plus three births at (1,1,0),(1,1,1),(2,1,1) — which assembled a completed x=0→x=3 path in a single tick, largely out of the opponent's own converted stones.
- Result: P2 win, connection, 14 plies. Engine-verified verbatim.

### Line 3 — adversarial / novelty-stress
- Moves: `21,42` and `42,21` (annihilation/super-ko), `0,0,2,1,0,1,1,3,18,2,2,18,17,17,16,0,32,5,3,1,1,5,32,3` (baseline melee)
- What you tried to break / stress, and what happened: (1) Lone-vs-lone contact: placing adjacent to an isolated enemy stone kills BOTH (actor's stone dies at (0,1), enemy's at (1,0), simultaneously in CA iteration 1) — which would recreate the empty initial position, so the engine's super-ko rolled the action back to a pass in both orderings. Mutual annihilation is thus literally unplayable from the opening: the rule interaction bans it. (2) The policy-baseline melee: violent oscillations (board fully EMPTY again at ply 5; five ownership swings of 3+ stones), a mid-game where P1=6/P2=1 flipped within two plies, and a P2 connection at ply 24 via cascade. All 24 plies engine-verified after I fixed my model's one legality bug (no-op self-placement needs a neighboring own stone — caught by an engine ILLEGAL rejection at ply 20 of the draft line). (3) The same-tick double-connection draw the rules warn about is real in principle (CA completes paths, as my Line 2 shows) but I could not engineer one deliberately.
- Result: annihilation probes: rolled back to passes (then game continues); baseline: P2 win by connection, ply 24.

### Additional lines (optional)
Model-validation trace: helper vs engine agreed on piece counts for every ply of the 19-ply prefix and the corrected 24-ply baseline — the quoted CA behaviors are engine-truth, not simulation.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Race a 4-stone string (straight or diagonal) between your faces while keeping every stone at ≤2 own neighbors and ≤1 enemy neighbor: string interiors ((2,0)) and ends ((1,0)) are CA fixed points, three-own-neighbor stones die on ANY action ((3,0)/(0,3)), and a stone with two adjacent enemies defects ((2,1)). Attack by replacement (placing on enemy stones), by pairing up against a string stone, or by engineering the (3,3) birth cell / multi-flip cascades that the 3× iteration amplifies. Never leave a stone lone near the enemy — it evaporates at (1,0)/(0,1).
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Yes, brutally and instantly: every lone stone near contact died on the next action; P2's corner replacements in Line 1 were punished by my simply out-racing them; P1's rebuilt (1,0,0) in Line 2 became a component of MY winning path one ply later (flipped by the cascade). The response economy is extreme — most stones on the board at any time are about to be someone else's.
- Topology/board effects on strategy: Moore adjacency makes 4-stone diagonal chains legal paths, so the goal distance is tiny and defense must be pre-emptive; it also caps table relevance at 4 neighbors, so dense blobs freeze into permanent walls while sparse skirmishes stay volatile. The 4×4×4 volume means nowhere is far: every stone interacts with up to 26 cells, and the 3× CA iteration propagates effects across half the board per action.
- Emergent concepts you'd name (or "none observed"): "string theory" (≤2-neighbor chains as the only stable shapes), "mutual annihilation" and its "super-ko guard" (the rules ban the opening trade by repetition), "replacement tempo" (placing on enemy stones as capture), "cascade finishing" (wins delivered by the CA converting enemy stones into your path — Line 2's ending), "freeze density" (counts >4 are immune — walls by crowding).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Skill decided every game — the depth-2 side won all three lines from either seat, and my Line-1 plan (diagonal chain + avoiding the two-enemy defection pattern) worked exactly as designed. But agency is mediated by heavy computation: with 3 iterations of a 26-neighbor CA per action, I could not verify a single move by hand, and to a human player outcomes would feel like a slot machine until the stable-shape theory is internalized.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  It is the third actor-perspective-CA game in this pack (with D and F) — arguably one design template with re-rolled parameters: swap the board (4D torus / flat grid / Moore 3D), the table, and the win condition, and you get D, F, or G. The genre ancestors are the same (two-color Life variants); connection wins are Hex's; replacement-capture is common.
- Honest novelty assessment after arguing that case: Within the family, G is the most distinctive: Moore-3D adjacency with a count-capped table (freeze-by-density is a genuinely clever consequence), 3× CA iteration (cascades as a first-class mechanic), replacement placement, and connection goals produce a game that plays NOTHING like D's constructive arming economy — it is a volatile skirmish racer where the CA itself finishes your path. The annihilation-guard super-ko interaction and the stable-string theory are original emergent structures. Novel in texture even if familial in template; and unlike its siblings, I found no degenerate exploit (no camping, no donation, no freeze-draw) — the opening is sound, races are fast, and passing is always bad.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — CA-game genre recognized (sibling of this pack's D and F), specific game unknown, no prior score recalled.
- P1-role experience sub-score (1-10): 4.5
- P2-role experience sub-score (1-10): 4.5
- Role-averaged sub-score: 4.5
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 3 — the deeper-searching side won from both seats (P1 in 9 plies, P2 in 14), and the only symmetric-strength game (policy baseline) went to P2 at ply 24, a single sample insufficient to overturn the impression that skill, not seat, decides.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.2**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  Of the three CA games in this pack, G is the only structurally sound one: all three of my lines ended in genuine connection wins (plies 9, 14, 24), fast and decisive, with no camping exploit, no opening donation, no freeze-draw — even the mutual-annihilation opening turns out to be self-banned by the super-ko interaction, a genuinely elegant accident. The strategy content is real and learnable (stable strings, replacement tempo, two-enemy defection raids), and Line 2's cascade finish — the CA converting the opponent's own stones into my winning path — is the most spectacular single move I saw across all seven games. It stays below the top anchors for one big reason: human illegibility. Three iterations of a 26-neighbor CA per action put every move beyond hand-verification (I needed a validated calculator to play at all), and the violent oscillations would read as randomness to anyone who hasn't built the theory. Sound, novel-textured, dramatic, but opaque: 4.2.
