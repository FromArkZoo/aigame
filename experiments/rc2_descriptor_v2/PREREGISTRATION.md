# RC2 descriptor redesign (drama_v2 + insertion guards) — pre-registration (locked before any probe data)

Registered origin: Phase D NOGO (`evaluations/rc2_phase_d/RESULTS.md`, merged `ff3715b`):
random-rollout drama Goodharts under archive search; descriptor redesign precedes any
archive spend. Single-doc spec+prereg (Phase D pattern). Zero PPO; rollouts only.

## Design

**TacticalAgent** (new, `metrics/tactical_agent.py`; `training/` untouched): per ply —
1. WIN-IN-1: exhaustive scan of legal placement actions (boards here ≤ 484 cells; scan
   all legal when ≤ 512, else top-64 by heuristic) via cloned-engine step; play any
   immediately winning action.
2. BLOCK-WIN-IN-1: same scan from the opponent's seat on the current position; if the
   opponent has winning placements, play into one of those cells if legal (random
   seeded choice among them), else fall through.
3. Else: densify heuristic (GreedyAgent's friendly_adj − enemy_adj), seeded tie-breaks.
Pie rule: always swap when offered (GreedyAgent precedent).

**drama_v2** = winner_behindness on tactical-vs-tactical traces, reusing the LOCKED
Phase A progress-trace formulas (`metrics/descriptors.py` obs_* functions; only the
policy generating ownership snapshots changes). Protocol: n=100 rollouts/game as 50
mirrored seed pairs (same seed, seats swapped), seed scheme: pair i → agent seeds
(1000·i+1, 1000·i+2), mirrored game swaps them. Draws skipped and counted.

**Insertion guards** (each a probe column; future archive candidates must pass all):
- **RUSH**: fires iff ≥ 25% of decisive tactical rollouts end with a winner in ≤ 6
  plies.
- **REACH** (threshold-family only): fires iff < 20% of tactical rollouts end decisively
  BEFORE max_turns (i.e., the win condition is effectively unreachable under competent
  play; timeout/draw saturation).
- **TILT**: fires iff P1 wins ≥ 80% of decisive games across the mirrored pairs
  (seat-tilt under competent play; mirroring removes seed luck).

## Probe set (17 games, all loadable today)

Phase D seven (from `evaluations/rc2_phase_d/games/*.json`, identities per
`.blind_mapping.json`): S1–S5 + C+ (d4015a646ae3) + C− (e1453dac5445), with blind agent
means 1.77 / 3.20 / 3.10 / 3.00 / 3.07 / 3.83 / 3.90 (RESULTS.md table). Plus the Phase B
10-game anchor set (loaders in `experiments/rc2_anchor/run_probe.py`, pods per its
prereg). Overlap (d4015, e1453) evaluated once, used in both bar sets.

## Bars (binary, point estimates; transcribed verbatim by the runner)

Guard calibration (each guard has a known positive from Phase D and protected negatives):
- **BAR G-RUSH**: RUSH fires on S1; does NOT fire on e1453, d4015, s_flip_r2,
  a1_field_connect.
- **BAR G-REACH**: REACH fires on S2; does NOT fire on e1453. (Other threshold games
  reported, not binding.)
- **BAR G-TILT**: TILT fires on ≥ 1 of {S4, S5}; does NOT fire on s_flip_r2 or
  a1_field_connect. (d4015 reported, not binding — its R8-era balance is unverified
  under tactical play.)

Quality-signal calibration:
- **BAR V2-RANK**: over the Phase D seven, drama_v2 of BOTH e1453 and d4015 exceeds
  drama_v2 of EVERY S-game on which at least one guard fires; and among guard-clean
  games, no S-game outranks both controls. (Spearman(drama_v2, blind mean) over all 7:
  reported, not binding.)
- **BAR V2-NONREG**: the four Phase B bars (mean(ABOVE)>mean(BELOW); ≤1 boundary
  inversion; e1453 above no ABOVE game; 573562833174 > e1453dac5445) PASS for drama_v2
  on the Phase B pods.

## Decision grammar (locked)

- All five bars pass → **DESCRIPTOR_V2_GO**: re-registration of the archive probe
  (Phase C machinery + drama_v2 + the three guards at insertion) is authorized as next.
- G-bars all pass, V2-RANK or V2-NONREG fails → **GUARDS_ONLY**: guards adopted for any
  future archive work; quality signal stays open; the single registered escalation is
  one MCTS/planning-trace drama probe.
- Any G-bar fails → **DESCRIPTOR_V2_KILL**: that guard's design returns to analysis;
  no archive re-registration; report which and why.
- Missing/unloadable games, wall cap (2 h), or harness failure → **PROBE_INCOMPLETE**.

## Honesty notes (pre-committed)

- TacticalAgent is a heuristic, not an oracle; the bars test whether it is competent
  ENOUGH to de-Goodhart the signal on known cases, nothing more. Its win/block scan is
  placement-only — move/multi-place subtleties (S1's 3-actions-per-turn) are handled by
  per-step win checks, which is exactly how S1's turn-1 win surfaces (engine checks wins
  after every step).
- Phase D's blind means are now training data for this design (declared); the
  protection against overfitting to 7 games is V2-NONREG on the independent Phase B set
  plus the future archive re-run being a fresh registration.
- Compute estimate: ~17 games × 100 rollouts with ≤512 clone-steps/ply ≈ tens of
  minutes; wall cap 2 h. n may be reduced to 60 ONLY by a pre-data amendment commit.
