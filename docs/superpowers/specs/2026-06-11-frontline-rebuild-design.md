# Frontline rebuild — design spec

**Status:** registered escalation from the SIEGE campaign (experiments/siege/RESULTS.md §7.1; both
arms NO-GO fired the escalation clause). Parent registration: docs/pivot_menu_synthesis_2026-06-10.md
(candidate #3 verdict + dissent 3, which located the viable region this spec builds in).
**Rule of record:** fresh spec + prereg BEFORE any engine code (SIEGE RESULTS §7.1, verbatim).
**Pre-lock review:** three adversarial lenses (degeneracy / methodology / arithmetic) applied to a
draft of this spec + prereg on 2026-06-11, all verdicts SURVIVES WITH FIXES; every fix is folded
in below (§11).

## 1. Motivation

Frontline (contested-majority scoring) is the registered next family because it is the only
candidate that makes packing worth literally **zero by definition** rather than by gradient
pressure: the score support is the intersection of both players' influence supports, so a stone
placed away from all enemy influence scores nothing. R21's confirmed root cause (anti-synergistic
capture → non-interactive packing races) is attacked at the win function itself.

The original probe was killed at synthesis on arithmetic, not concept (pivot menu §3). The four
registered defects, each with its registered fix:

| # | Original defect | Registered fix (this spec) |
|---|---|---|
| D1 | Engagement margin 0.25 saturates: P(engaged) ≈ 0.97 per cell on a 41%-full 484-cell board → engaged_share>0.90 kill fires on random rollouts (distribution mismatch, false kill) | engage threshold **E ≈ 1.0** (§4.1: same model gives ≈ 0.06 engaged share at realistic fill); behavioral-rate kills on random play excluded by category (§6 Stage-0 note) |
| D2 | Flip threshold coupled to the scoring margin | **decoupled**: flips keep `control_margin = 0.0`; the SIEGE STAGE0_MEMO arithmetic holds for lone stones and 2-chains; chain rows for L≥3 need own-side d2 terms and are re-derived in §4.2 / Stage 0a (a 3-chain end needs 4 attackers ALL at d1 — the memo's d1+d1+d1+d2 profile gives net exactly 0.0000, no flip) |
| D3 | Terminal-only scoring pins game_length = max_turns and decisiveness constant (pinned-signal trap inside its own screen) | **score-margin early-end rule** (§3.4): lead ≥ M_end persisting through 3 consecutive ply-checks ending at a round-end, after a min-turn floor |
| D4 | Double-pass → draw makes passing a dead action | **double-pass resolves by main score** (§3.5) — safe here because the score IS the win condition; the R13/14 "win without meeting the win condition" exploit cannot recur (a leader wins by score, never by pieces, except at exact score ties — §3.5) |

Fifth defect, resolved by D1+D2 jointly rather than its own lever: the easiest flip was
**score-negative for the capturer** (deleting a straggler's kernel disengaged 18 cells the
capturer was scoring; exact recomputation: ΔS = −14 at margin 0.25). §4.2 shows that at E = 1.0
the same flip has margin swing Δ(S1−S2) = −1, deep flips are excluded by the flip condition
itself, and front flips are bounded tactical trades. Stage 0a kills the family cheaply if this
analysis is wrong on engine kernels.

Inputs inherited from SIEGE §7.3: the hex_rhombus win-graph asymmetry (§5 blind finding) is **moot
here by construction** — no connection win exists in this family; only tempo asymmetry remains,
handled by pie. Per-role tvr floors are n/a (symmetric game).

## 2. Goal & hypothesis

**Hypothesis:** on the proven-live r=2 flip substrate (s_flip_r2: blind 4.10, flips 7.84/game),
replacing the connection win with contested-majority scoring + score-margin termination produces
the first blind plateau break (≥ +1.0 over A1, i.e. absolute ≈ 5.0) by making interaction the sole
scoring channel and capture a live tactical trade instead of an anti-synergistic one.

**Single manipulated variable vs S (= s_flip_r2):** win/termination structure only. Substrate,
flip mechanics, board, and training recipe are identical — exactly parallel to SIEGE's M-vs-S
design logic.

## 3. The rebuilt ruleset (`condition_type = "contested_majority"`)

Substrate (identical to S/A1): hex_rhombus W=22 (484 cells), influence r=2 / strength 1.0 /
decay 0.5 / eps 0, capture `field_flip` at `control_margin 0.0`, pie ON. Two substrate notes the
draft review surfaced: (i) **positional superko is provably inert in this family** (stone count
strictly increases with every placement — flips conserve count and nothing removes stones), kept
only for substrate parity with S/A1; (ii) **flips are non-optional and board-global**
(`_capture_field_flip` scans all cells on every placement, engine_v2.py:919-965) — Stage-0a triad
events are forced consequences of placement, not choices.

1. **Per-player fields.** I1(c), I2(c) ≥ 0: sum of own-stone kernels (signed field = I1 − I2;
   same kernel cache, recomputed from owners like `_recompute_field`, engine_v2.py:1038-1051).
2. **Engagement.** Cell c is *engaged* iff min(I1(c), I2(c)) ≥ `engage_threshold` E. Empty and
   occupied cells both count (control-includes-empty convention, engine_v2.py:1347-1353).
3. **Score.** S_p = #{engaged cells where p leads the signed field beyond FP tolerance 1e-9
   (R17 ULP lesson, engine_v2.py:1387-1397)}. Led-by-neither engaged cells score no one. Kernel
   weights are dyadic (1.0/0.5/0.25), so field sums are float-exact; exact ties at fronts are a
   normal, common state, and the 1e-9 tolerance only adjudicates genuine ties.
4. **Score-margin early-end.** A *round-end* is the win-check after P2's ply (post-increment even
   step_count — both players have moved; the engine checks wins before advancing the player, so
   the check site must be pinned to P2-completed plies). The same player must lead by ≥
   `end_margin` M_end (komi-adjusted) at **3 consecutive ply-checks ending at a round-end** (two
   round-ends + the intervening odd ply), all at step_count ≥ `min_turns`: then that player wins,
   end_cause `"score_margin"`. The intervening-ply requirement means the lead must survive the
   opponent's last word — a one-placement cascade spike re-created each round by the player moving
   last before the checks cannot fire it. The persistence counter is leader-signed (a leader
   change resets it).
5. **Double-pass.** Before `min_turns`: legacy draw (guards accidental exploration-phase
   double-passes from ending games at komi rungs). At or after `min_turns`: resolved by score
   (§3.7 resolution order).
6. **Timeout.** max_turns T: resolved by score (§3.7 resolution order; gated branch beside the
   field_connection count tiebreak, engine_v2.py:1441-1463).
7. **Score resolution order (double-pass and timeout).** (i) Compare S1 vs S2 + komi_cells;
   strictly higher wins — EXCEPT a player who has placed zero stones the entire game can never be
   declared winner (downgraded to draw). (ii) Exact tie → more stones on board wins; equal →
   draw. The participation clause + stones tiebreak close the **pass-bot inaction floor** (§4.4):
   without them, total abstention guarantees a non-loss at komi 0 and an outright win at any
   non-zero komi rung. A score-leader still always wins by score — pieces only ever break exact
   score ties, so the R13/14 exploit (winning by pieces while behind on the win condition) cannot
   recur.
8. **Komi.** Count-based: `komi_cells` integer added to S2 at every score comparison (early-end
   persistence checks, double-pass, timeout). Default 0 with pie ON (precedent: A1 bias 0.050 and
   s_flip_r2 PASS at komi 0). Fallback ladder is **sign-symmetric** {±1, ±2} — smallest |komi|
   passing, direction chosen by the measured bias sign at komi 0 (a one-sided ladder can only move
   bias one way and would fail for a sign reason, not a game reason). The C2 fractional-threshold
   komi pathology cannot recur on an integer cell count.
9. **Observation** (+3 gated floats, quota_frac pattern, engine_v2.py:1561-1565):
   `score_margin_frac` = clip((S_self − S_opp_eff)/M_end, −2, 2), `engaged_frac` =
   engaged/num_active, and `armed_frac` = leader-signed persistence counter / 3 (own-perspective).
   Without score visibility the early-end is unlearnable (SIEGE clock_frac lesson); without the
   counter, the defender cannot distinguish "answer now or lose" from "one round of slack" — the
   same lesson applied to the new rule's own state. Legacy obs dims unchanged.

## 4. Design arithmetic (Fermi here; exact engine-kernel computation = Stage 0a, post-lock)

Kernel at r=2/s=1.0/d=0.5 on hex (ring sizes 6, 12): 1.0 at d0, 0.5 at d1, 0.25 at d2;
19-cell disc. Model is interior-cell (324/484 cells have the full disc; boundary discs are
smaller, making these saturation figures slight over-estimates — conservative for the D1
argument). All kernel sums are dyadic-exact.

### 4.1 D1 check — engagement unsaturates at E = 1.0
Model: random fill, per-side stone density ρ, Bernoulli at d0 (ρ) + Poisson rings (λ1 = 6ρ,
λ2 = 12ρ). P(I_p ≥ 1.0) = ρ + (1−ρ)·P(0.5·X1 + 0.25·X2 ≥ 1).
- **Defect reproduction (sanity check of the model):** at E = 0.25 engagement per side = "any
  stone within d2": at 41% fill P(reached by both) = (1 − 0.795¹⁹)² ≈ **0.975** — reproduces the
  registered 0.97.
- At E = 1.0, 41% fill: 0.74 per side → **0.54** both. At turn-80 fill (~40 stones/side,
  ρ ≈ 0.083): 0.25 per side → **0.06** both. At 20% fill (ρ = 0.10): **0.11** both.
With the early-end rule games end well before 41% fill, and trained play concentrates engagement
into front bands rather than spreading it. Saturation headroom vs the 0.60 band top is ~6–10×.

### 4.2 D5 check — flip score-impact at E = 1.0 (exact, in-vacuum; verified on engine kernels)
The registered Stage-0a metric is the **margin swing Δ(S_capturer − S_opponent)** — the game's
only currency — not the capturer's absolute ΔS (which double-counts engagement the opponent also
loses). Canonical triad, pinned by exact geometry in the prereg:
- **Straggler** (lone enemy stone x, minimal 3 attackers d1+d1+d2): I1(x) = 1.25, I2(x) = 1.0 →
  net +0.25, flips. x's cell is the only engaged cell (I2 ≥ 1.0 nowhere else); capturer led it.
  Post-flip the disc disengages: ΔS_cap = −1, margin swing **−1** (was −14 exact at margin 0.25).
  Near-neutral, no longer self-harming.
- **Deep flip excluded structurally:** a flip requires net capturer control at the stone's cell
  *including the stone's own +1.0* (engine_v2.py:919-965, strict `>` at margin 0,
  engine_v2.py:917); inside enemy concentration the net is enemy-positive, so the "flip backfires
  deep in enemy territory" case cannot fire.
- **2-chain front** (memo profile d1+d1+d1+d2 on chain-end x): I1(x) = 1.75 vs I2(x) = 1.5 → +0.25,
  flips; the flipped stone then puts the chain neighbour at net ≥ +0.25 (exact worst case) → the
  cascade converts the whole 2-chain. Exact vacuum outcomes by attacker geometry: margin swing
  **−1** (attackers far from the neighbour) to **−2** (attackers near). The positional payoff —
  two converted stones, front destroyed — is unscored by the instantaneous metric, and in-vacuum
  triads structurally overstate score-negativity (post-flip enemy field vanishes entirely, which
  no real front allows). Prereg therefore also pins **second-rank variants** (an enemy support row
  behind the chain) where engagement persists post-flip.
- **3-chain front:** the memo's chain-end row drops the own-side d2 term (x–y–z linear: z is at
  d2 of x → I2(x) = 1.75, net 0.0000 with the memo profile — no flip). Corrected threshold:
  **4 attackers all at d1** (2.0 > 1.75 → +0.25, flips; x and y convert, z survives at net 0 worst
  case and is stranded as a new straggler — cascade is real but partial for L≥3). Corrected
  interior row for L≥4: 6 attackers, not 5. Stage 0a re-derives the full table including own-d2
  support before any other use.
**Stage 0a kill: mean margin swing < −2 across the pinned canonical front set** (exact vacuum
values −1 to −2 — the bar fires only if this arithmetic is wrong on engine kernels, i.e. the
anti-synergy defect survived the rebuild).

### 4.3 D3 check — early-end calibration shape
Trained fronts ≈ front length O(W) × band width 2–3 → ~44–66 engaged cells; mid-game leads of
5–12 cells are the plausible decisive range → M_end grid {8, 12}. Canonical vacuum cascades swing
the margin by only 1–2; dense-front cascades plausibly more — hence the 3-consecutive-checks
persistence rule (§3.4) rather than a single-check trigger. **min_turns = 20 is load-bearing, not
belt-and-braces:** adversarial search on exact kernels reaches a stable lead of 8 (= M_end low
rung) from 6 stones/side at step 12; the floor is what excludes steps ~12–18, and additionally
guards the RC2-Phase-D first-turn-win degeneracy shape.

### 4.4 Degenerate-strategy floor (the §11 review's findings, resolved or registered)
- **Pass-bot:** score support = intersection of supports ⇒ total inaction pins S1=S2=0 for the
  whole game. Unfixed, that is a guaranteed draw at komi 0 and a guaranteed WIN at any non-zero
  komi rung — invisible to PPO at calibration, discoverable by blind agent teams (the SIEGE
  dissent's "numerically-passing turtle"). Fixed by §3.7 (participation clause + stones tiebreak:
  pass-bot now loses at komi 0, draws at best on komi rungs) and gated: scripted pass-bot in
  Stage 0b; Stage-2 band trained-F-beats-pass-bot ≥ 0.90.
- **Mirror:** W=22 admits the fixed-point-free reflection (i,j)→(21−i,21−j); dyadic exactness
  means a mirroring opponent restores exact field antisymmetry (no ULP escape), pinning
  S1=S2 at every check; pie does not break it (mirroring is a second-mover strategy) and the
  stones tiebreak cannot (counts stay equal). Whether the flip cascade preserves the mirror is
  plausible but unproven → tested, not assumed: scripted mirror agent in Stage 0b, Stage-2 band
  trained-F-beats-mirror ≥ 0.70, and a registered pre-Stage-1 contingency (switch to W=21; the
  odd board's center cell breaks the pairing) if the mirror secures ≥ draw at material rates.
- **Stall/forestall surfaces probed and held:** (i) a passing leader cannot stall to timeout —
  flips fire only on the mover's placement, so passing makes the trailer's stones immortal while
  gifting tempi; (ii) a trailer cannot forestall forever via engagement-destruction — T=200 is
  the backstop the leader wins on score; (iii) flip-tennis is self-limiting — each re-flip costs
  a fresh placement (2 cells/round on 484 cells within T=200). No rule change needed.
- **Packing / turtle meta:** disjoint packing → 0–0 by construction; mutual avoidance → 0–0
  timeout draws → caught by draw ≤ 0.05 and timeout ≤ 0.25 gates, plus the pass-bot band.

## 5. Engine changes (all additive + gated; legacy bit-identical; NO code before prereg lock)

- `WinCondition` fields (rules.py:230-247 serde pattern, omit-defaults): `engage_threshold: float
  = 0.0`, `end_margin: int = 0`, `min_turns_score_end: int = 0`, `komi_cells: int = 0`;
  `condition_type "contested_majority"` NOT added to WIN_CONDITION_TYPES (never generated —
  SIEGE capture_quota precedent).
- Per-player field accessor (I1/I2 recompute from owners; kernel cache reuse) — the shared
  dependency of Stage 0a's script, Stage-1 gate (4), and the trace instrumentation.
- Win dispatch branch + leader-signed persistence counter (§3.4).
- Gated overrides: `_end_by_double_pass` (min_turns guard + §3.7 resolution),
  `_end_by_max_turns` (§3.7 resolution).
- +3 gated obs floats (§3.9).
- Instrumentation (itemized — the original family died one stage from missing logs):
  contested_majority branch of the progress-trace recorder (score-share trace), trace-instrumented
  eval path (siege anchor_drama.py `play_with_trace` covers S/A1/A0 families only), per-ply
  engaged_share + end-cause + per-flip margin-swing loggers.
- Scripted agents: front-builder (reuse siege/scripted_agents.py chain-builder), mutual-packer,
  pass-bot, mirror (all trivial; geometries pinned in prereg).
- Harness under `experiments/frontline/` mirroring `experiments/siege/` anatomy
  (PREREGISTRATION → build+smoke → calibrate → screen → blind pack).
- Full suite green (`python -m pytest test_*.py -q`, 242+ tests); canonical hashes unchanged.

## 6. Experiment protocol

Arms: **F** = f_frontline (treatment); **S** = s_flip_r2 (comparator, retrained in-campaign —
already adjudicated by SIEGE, its grammar is NOT re-litigated); **A1** = field_connect anchor;
**A0** = baseline (screen only, registered job: the A1/A0 control_flip_rate ladder must reproduce
the on-disk ordering — the campaign's instrumentation-reproduction check). Stages 0/1/1.5/2/3
with kill bars: see PREREGISTRATION.md (experiments/frontline/), the locked document of record.

**Stage 0 distribution-mismatch note (D1 lesson, registered):** Stage 0 kill bars are restricted
to *arithmetic and mechanism-liveness* facts. Behavioral rates on random rollouts (early-end
frequency, draw rates) are LOGGED, not killed on. The one apparent exception, KILL-0b3
(random-rollout engaged_share band), is registered as a **design-model validation kill**: it fires
only if §4.1's arithmetic is wrong by ~6× — a design-assumption death, not a distribution
mismatch. Trained-play behavior is gated at Stage 1/2, where the original probe's false-kill
defect cannot recur.

## 7. Pre-registered decision rule (locked at prereg commit; not altered after data)

With blind campaign means F, S, A1 (2 independent agent teams, sealed labels, seat-swapped,
opposite orders; verdict instrument = the stage3_ab BRIEFING.md template, Overall 1–10, label
substitution only):

- **CAMPAIGN VALIDITY:** A1 ∈ [3.7, 4.4] (band widened from SIEGE's [3.9, 4.4] on the two on-disk
  A1 observations: 3.90 boundary-exact, 4.15); outside → CAMPAIGN_UNRESOLVED → one cheap blind
  replicate, whose numbers then adjudicate alone. A second consecutive validity failure →
  **CAMPAIGN_INVALID**: F undecided, family neither GO'd nor retired, rules track NOT declared
  exhausted.
- **GO:** F − A1 ≥ +1.0 AND F > S with F − S ≥ +0.3 → plateau break. Family enters the
  generator/evolution track, gated on the RC2 selection-layer workstream (GE stays
  diagnostic-only).
- **PARTIAL:** (F > S AND F − A1 < +1.0) OR |F − S| < 0.3 → exactly one licensed
  re-parameterization: the **runner-up Stage-1 cell** by the registered tie-break (re-assert its
  Stage-1 gates at its registered komi — no new grid — then screen, then blind once). The second
  blind is adjudicated GO-else-NO-GO: no further PARTIAL, no further knobs. If no second cell
  passed Stage 1, the knob is VOID and PARTIAL → NO-GO.
- **NO-GO (F ≤ S outside the tie band, or a clean kill at any earlier stage):** contested-majority
  RETIRED. The 2026-06-10 pivot menu is then exhausted on the rules side (SIEGE retired, z_flip
  sub-bar, Frontline retired, FamilyMAP/Deep-Grid superseded) → the **RC2 selection layer becomes
  the sole registered track** (planning-gap / learnability / periodic agent slates per
  experiments/rc2_descriptor_v2/RESULTS.md).
- **KILL_INVALID branch (kills must be clean to retire a family):** a Stage-0/1 kill attributable
  on inspection to implementation error rather than design arithmetic → fix and rerun that stage
  ONCE; only a clean kill, or the rerun's kill, maps to RETIRED. (The original Frontline died at
  Stage 0 on three methodology artifacts and was resurrected — a 2-hour memo-script bug must not
  permanently close the rules program.)
- **Comparator failure is never a family verdict:** S or A1 failing its own health checks at any
  stage (collapse, bias > 0.10, tvr floor) → CAMPAIGN_UNRESOLVED → one retrain; S blind mean
  outside [3.7, 4.5] → verdicts provisional, one replicate.
- **Mirror contingency (pre-Stage-1, one use):** if Stage 0b shows the scripted mirror securing
  ≥ draw in ≥ 30% of games vs the front-builder, switch the board to W=21 and restart from Stage
  0a (one licensed switch; comparability note: S/A1 stay at W=22, weakening cross-arm
  comparatives — recorded honestly as a cost, not hidden).

## 8. Pre-registered defaults (locked constants)

| Constant | Value | Rationale |
|---|---|---|
| Board / field | hex_rhombus W=22; r=2/s=1.0/d=0.5/eps=0 | proven-live substrate (S blind 4.10); W=21 contingency per §7 |
| `control_margin` (flips) | 0.0 | D2 decoupling; flip thresholds per §4.2 corrected table |
| E calibration grid | {0.75, 1.00, 1.25} | §4.1; ~1.0 is the registered region |
| M_end grid | {8, 12} | §4.3 |
| Early-end persistence | same leader, ≥ M_end at 3 consecutive ply-checks ending at a round-end (round-end = post-P2 check) | §3.4; survives the opponent's last word |
| min_turns_score_end | 20 | load-bearing (§4.3); also guards double-pass before 20 (§3.5) |
| max_turns T | 200 | legacy; timeout share gated ≤ 0.25 |
| Komi ladder | komi_cells {0, then ±1, ±2}, pie ON; smallest \|komi\| passing, direction by measured bias sign | §3.8; precedent: bias 0.050 at komi 0 |
| Score resolution | score+komi → participation clause → stones tiebreak → draw | §3.7; pass-bot floor |
| FP lead tolerance | 1e-9 | R17 ULP lesson; dyadic-exact sums make it tie-only |
| Seat bias gate | ≤ 0.10 | inherited (fc_phase15/SIEGE convention) |
| tvr gate | mean ≥ 0.75, no seed < 0.65; collapse (< 0.20) → rerun ladder 45→46, **replace-in-slot** | blind-validated S measured 0.780 — a 0.80 floor is a calibrated false-kill; the SIEGE +0.15-over-baseline clause is inert for symmetric games (noted, retained only for grammar parity) |
| Comparatives (2, after drama demotion) | control_flip_rate F − S ≥ +0.5; game_length ≥ 10 turns more central (band [30,160], center 95) | directional, both-arms-movable; GO = 2/2 |
| Drama | **diagnostic-only, never a comparative** | F's score-share trace is closeness-by-construction — the rc2 descriptor-v2 Goodhart relocated; cross-family traces incommensurable |
| score_margin end-cause share | ≥ 0.25 (Stage 1 & 2) | rebuilt mechanism must be load-bearing |
| engaged_share trained band | [0.02, 0.60] (final-ply mean, all end-causes) | contested state load-bearing, not saturated; 0.01 floor for the random-rollout 0b band is intentional (different distribution) |
| Exploiter bands (Stage 2) | trained F beats pass-bot ≥ 0.90; beats mirror ≥ 0.70 (each seat) | §4.4 |
| Double-pass share | diagnostic, yellow flag > 0.50 | decisive double-passes must not displace the early-end mechanism silently |
| Blind labels | G / J / P (fresh; Q,Z,K,M,T,D,V,X burned) | sealed-mapping convention |
| A1 validity band | [3.7, 4.4]; S sanity flag [3.7, 4.5] | §7 |
| Stage-1 tie-break | game_length centrality closest to 95 → max score_margin share → min \|bias\| | length first, so the carried cell is not the one that fights screen comparative 2 |
| Stage-2 aggregation | ALL eval games of the 3 final seeds; no game- or seed-level filtering of any statistic | R21 Probe B survivorship lesson |

## 9. Budget (honest)

Build ~1–1.5 days (per-player fields, dispatch + overrides, 3 obs floats, 3 scripted agents,
instrumentation, harness, tests) + Stage 0a ~2h (kernel memo script incl. corrected threshold
table) + Stage 0b in build smoke + Stage 1 ~1.5h (6 cells × 3 seeds, PPO 3000, n=200; S/A1
calibration re-asserted from SIEGE artifacts) + Stage 1.5 ~10 min (diagnostic) + Stage 2 ~2h
(4 arms × 3 seeds @ PPO 5000, n=200) + Stage 3 ~1h. **Total ≈ 2–2.5 days wall.** The W=21
contingency, if it fires, adds ~0.5 day (Stage 0 rerun + recalibration).

## 10. Relationship to the RC2 workstream

Independent and already registered to proceed regardless of this campaign's outcome (SIEGE §7.2).
Nothing in this spec gates RC2; a Frontline GO adds the family as the substrate for the next
evolution campaign once RC2 produces a trusted selection signal.

## 11. Pre-lock review provenance

Three independent adversarial agents (degeneracy / methodology / arithmetic lenses) reviewed the
2026-06-11 draft before lock; all returned SURVIVES WITH FIXES. Material catches, all folded in:
pass-bot inaction floor (FATAL as drafted → §3.7); even-board mirror (§4.4 + W=21 contingency);
STAGE0_MEMO chain rows missing own-side d2 support (§4.2 corrected table — the original family's
error class, caught again); KILL-0a1 re-based on margin swing with pinned geometries; drama
demoted to diagnostic (closeness Goodhart); tvr floor re-calibrated below the blind-validated
reference; round-end parity + persistence hardening; armed-counter observability; sign-symmetric
komi; comparator-failure / double-validity-failure / PARTIAL-second-pass grammar completion;
KILL_INVALID branch; A0 given a registered job; survivorship and verdict-instrument pins.
