# RC2 learnability — closeness-confound anchor calibration

Registered obligation: rc2_descriptor_v2/RESULTS.md binding input (c) — quality signal demonstrated on the S4/S5 vs d4015 pair BEFORE any search spend. Protocol pre-committed in `anchor_calibration.py`; bar applied verbatim.

Signal: L = tvr(trained) − tvr(untrained); PPO budget 3000, seeds [42, 43], tvr n=100 seat-swapped stochastic (frontline/siege convention).

| game | blind mean | family | L (mean) | per-seed L | untrained → trained |
|---|---:|---|---:|---|---|
| S4 | 3.0 | territory | **-0.365** | -0.380, -0.350 | 0.365 → 0.000 |
| S5 | 3.07 | territory | **-0.355** | -0.440, -0.270 | 0.355 → 0.000 |
| d4015a646ae3 | 3.83 | connection | **-0.385** | -0.380, -0.390 | 0.385 → 0.000 |
| e1453dac5445 (diagnostic) | 3.9 | threshold | **+0.165** | +0.050, +0.280 | 0.515 → 0.680 |

## Verdict: **FAIL**

L(d4015) -0.385 vs L(S4) -0.365, L(S5) -0.355 — bar: L(d4015) strictly above both

Context (non-binding): FRONTLINE clean-kill datum at the same budget/convention — dead family L ≈ +0.04; live families S/A1 L ≥ +0.28.

Wall time: 199.6s. COMPLETE

## Inspection addendum (post-verdict, mechanism — `collapse_check.py`)

The FAIL is not a quality ranking; it is a measurement-validity finding. All three
light games — including the blind-preferred control — collapse to trained tvr
**exactly 0.000** (6/6 independent runs). Mechanism confirmed on d4015: the trained
policy passes **60% of its moves as P1, 79% as P2** (mean self-play game lengths
27/70 plies). This is the self-play pass-collapse attractor: mutual pass is a
low-regret equilibrium under ±1 terminal rewards, and a pass-heavy policy loses
every game to random's accidental scoring. The signal as defined therefore measures
"does PPO self-play at budget 3000 avoid the pass attractor on this board", not
strategic depth.

Two inversions, not one:

1. The registered bar: d4015 (blind 3.83) ranks below S4/S5 (blind 3.00/3.07) —
   all three collapsed; the ordering among collapsed games is noise.
2. Diagnostic: e1453 (the R21 GE-top that agents ranked 6/7) is the ONLY game that
   trains (+0.165) — naive learnability would crown the known-shallow game.

Why the FRONTLINE validation datum did not transfer: there, all arms ENGAGED and
learnability separated a family where engagement is punished (F) from families
where it pays (S/A1) — i.e., it detected a passivity gradient between large
purpose-built games. On the small evolved-archive games the dominant failure mode
is outright equilibrium collapse, which hits good and bad games alike.

## Consequence for the RC2 track

- **Naive self-play learnability is DEAD as a maximand candidate** — do not spend
  search on it. (The 15-minute gate did exactly its registered job: ~200 s of
  compute killed the candidate before any search spend.)
- Any learnability REDESIGN (e.g., trained-vs-fixed-opponent curves, entropy-floored
  training, best-response-to-random improvement) is a NEW candidate and must re-run
  this same calibration before search spend.
- **Planning-gap** (deep-vs-shallow search delta on a shared position set) becomes
  the lead candidate by default: it requires no gradient equilibrium and directly
  measures what closeness cannot fake. **Periodic agent slates** remain the
  ground-truth fallback.
- Side finding, recorded: PPO-at-3000 collapses on 3 of 4 archive games tested
  (including the R8-era anchor) — any historical or future signal that runs
  self-play PPO on small evolved games inherits this attractor unless guarded
  (cf. R-series collapsed-seed reserves, which priced exactly this).
