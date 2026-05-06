"""R20 S2 — two-tier PPO smoke gate.

Per R19_postmortem.md § Tier 2: the existing 3000-ep smoke gate
over-rejected 5/9 R19 borderline seeds (m1-m5: PPO-marginal at 3000 ep,
but evolution at 10000 ep + C2 found exactly that family in top-1 and
top-3 of menger). Cost was ~4-5 generations of evolution to rediscover
seeds the gate had filtered out.

Fix: the gate becomes binary on catastrophic failures only; everything
else is borderline and gets a 6000-ep retry. A borderline seed clears
Tier 2 if either the soft floors finally pass OR the seat bias drops
by >= 0.05 between Tier 1 and Tier 2 (showing PPO is making progress
under longer training, just not finished).

Tier 1 (existing harness, 3000-ep PPO): hard-drops only on catastrophic
failures.

Tier 2 (this module's contribution): re-runs PPO at 6000 ep on
borderline seeds and applies the progress check.

CATASTROPHIC THRESHOLDS (per postmortem):
  - seat_bias >= 0.45 (≥95% one-seat winrate — structural, no PPO budget fixes)
  - sampled_avg_len < 15 (degenerate quick-end)
  - greedy_p1_wr >= 0.95 AND seat_bias >= 0.40 (greedy player dominates)

BORDERLINE = passed Tier-1 catastrophic checks but failed soft floors:
  - sampled_avg_len < length_floor (the existing 8 OR 10% × active_cells)
  - 0.30 < seat_bias < 0.45

PASS_TIER2 (borderline survives Tier 2):
  - soft floors clear at 6000 ep, OR
  - tier1.seat_bias - tier2.seat_bias >= 0.05 (progress signal)
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from experiments.r18_ppo_smoke.harness import (
    LENGTH_FLOOR_FRACTION,
    LENGTH_FLOOR_MIN,
    SEAT_BIAS_THRESHOLD,
    SmokeVerdict,
    smoke_test,
)
from game_engine.game_def_v2 import GameDefV2


# Catastrophic thresholds (binary drop, no Tier 2 retry possible).
CATASTROPHIC_SEAT_BIAS = 0.45
CATASTROPHIC_GREEDY_WR = 0.95
CATASTROPHIC_GREEDY_BIAS = 0.40
CATASTROPHIC_LENGTH_MIN = 15.0

# Tier-2 progress threshold: seat_bias must drop by at least this much
# between Tier 1 (3000 ep) and Tier 2 (6000 ep) to count as "PPO is
# making progress, just not finished."
TIER2_SEAT_BIAS_PROGRESS = 0.05

# Default Tier-2 training budget (postmortem § Tier 2: 2× the smoke budget).
DEFAULT_TIER2_BUDGET = 6000


# Classification strings (machine-readable; keep stable for downstream consumers).
CLS_CATASTROPHIC = "catastrophic"
CLS_BORDERLINE = "borderline"
CLS_PASS = "pass"


@dataclass
class TwoTierVerdict:
    """Combined Tier-1 + optional Tier-2 verdict for a single seed game.

    ``tier2`` is populated iff Tier 1 classified the seed as borderline.
    ``final_passed`` is the gate's overall decision.
    ``final_classification`` is one of:
      - "pass_tier1"        — Tier 1 cleared all soft floors
      - "pass_tier2"        — Tier 1 borderline, Tier 2 cleared
      - "drop_catastrophic" — Tier 1 hit a catastrophic threshold
      - "drop_persistent"   — Tier 1 borderline, Tier 2 still failed
    """

    game_id: str
    tier1: SmokeVerdict
    tier2: SmokeVerdict | None
    final_passed: bool
    final_classification: str
    tier1_classification: str
    rationale: str
    tier2_seat_bias_progress: float | None  # tier1.seat_bias - tier2.seat_bias
    extras: dict = field(default_factory=dict)

    def to_json(self) -> str:
        d = asdict(self)
        return json.dumps(d, indent=2, default=str)


def classify_tier1(v: SmokeVerdict) -> tuple[str, str]:
    """Return (classification, rationale) for a Tier-1 SmokeVerdict.

    Catastrophic checks fire first (binary drop). Anything that survives
    them but failed the soft floors is borderline. Everything else passes.
    """
    if v.seat_bias >= CATASTROPHIC_SEAT_BIAS:
        return (
            CLS_CATASTROPHIC,
            f"seat_bias {v.seat_bias:.2f} >= {CATASTROPHIC_SEAT_BIAS} "
            "(structural; no PPO budget will fix it)",
        )
    if v.sampled_avg_length < CATASTROPHIC_LENGTH_MIN:
        return (
            CLS_CATASTROPHIC,
            f"sampled_avg_len {v.sampled_avg_length:.1f} < "
            f"{CATASTROPHIC_LENGTH_MIN:.1f} (degenerate quick-end)",
        )
    if (
        v.greedy_p1_winrate >= CATASTROPHIC_GREEDY_WR
        and v.seat_bias >= CATASTROPHIC_GREEDY_BIAS
    ):
        return (
            CLS_CATASTROPHIC,
            f"greedy_p1_wr {v.greedy_p1_winrate:.2f} >= "
            f"{CATASTROPHIC_GREEDY_WR} AND seat_bias {v.seat_bias:.2f} >= "
            f"{CATASTROPHIC_GREEDY_BIAS} (greedy dominates)",
        )
    if v.passed:
        return CLS_PASS, "all Tier-1 soft floors cleared"
    return (
        CLS_BORDERLINE,
        "soft floors failed but no catastrophic threshold; eligible for Tier 2: "
        + "; ".join(v.drop_reasons),
    )


def evaluate_tier2(
    tier1: SmokeVerdict,
    tier2: SmokeVerdict,
) -> tuple[bool, str, float]:
    """Decide whether a borderline seed clears Tier 2.

    Returns (passed, rationale, seat_bias_progress).
    Pass conditions (either suffices):
      A) Tier 2 cleared all soft floors (tier2.passed == True).
      B) Seat bias dropped by >= TIER2_SEAT_BIAS_PROGRESS between tiers
         (PPO making measurable progress on the structural axis).
    """
    progress = tier1.seat_bias - tier2.seat_bias
    if tier2.passed:
        return True, (
            "Tier 2 cleared all soft floors at 6000 ep "
            f"(seat_bias {tier1.seat_bias:.2f}->{tier2.seat_bias:.2f}, "
            f"len {tier1.sampled_avg_length:.1f}->{tier2.sampled_avg_length:.1f})"
        ), progress
    if progress >= TIER2_SEAT_BIAS_PROGRESS:
        return True, (
            f"Tier 2 seat_bias progress {progress:+.3f} "
            f"(>= {TIER2_SEAT_BIAS_PROGRESS}); "
            f"PPO is converging, evolution + C2 will close the rest"
        ), progress
    return False, (
        f"Tier 2 still failing soft floors AND progress {progress:+.3f} "
        f"< {TIER2_SEAT_BIAS_PROGRESS}; structurally biased"
    ), progress


def two_tier_smoke(
    game: GameDefV2,
    *,
    tier1_budget: int = 3000,
    tier2_budget: int = DEFAULT_TIER2_BUDGET,
    eval_episodes: int = 100,
    seed: int = 42,
) -> TwoTierVerdict:
    """Run the two-tier gate end-to-end on ``game`` and return the verdict.

    Tier 2 uses the same seed as Tier 1; trajectories diverge under the
    longer budget but the comparison is "what does PPO do with more
    training" rather than "is this a different random seed."
    """
    t1 = smoke_test(
        game,
        training_budget=tier1_budget,
        eval_episodes=eval_episodes,
        seed=seed,
    )
    tier1_cls, tier1_rationale = classify_tier1(t1)

    if tier1_cls == CLS_CATASTROPHIC:
        return TwoTierVerdict(
            game_id=game.game_id,
            tier1=t1,
            tier2=None,
            final_passed=False,
            final_classification="drop_catastrophic",
            tier1_classification=tier1_cls,
            rationale=tier1_rationale,
            tier2_seat_bias_progress=None,
        )
    if tier1_cls == CLS_PASS:
        return TwoTierVerdict(
            game_id=game.game_id,
            tier1=t1,
            tier2=None,
            final_passed=True,
            final_classification="pass_tier1",
            tier1_classification=tier1_cls,
            rationale=tier1_rationale,
            tier2_seat_bias_progress=None,
        )

    # Borderline: run Tier 2 retry.
    t2 = smoke_test(
        game,
        training_budget=tier2_budget,
        eval_episodes=eval_episodes,
        seed=seed,
    )
    t2_passed, t2_rationale, progress = evaluate_tier2(t1, t2)

    return TwoTierVerdict(
        game_id=game.game_id,
        tier1=t1,
        tier2=t2,
        final_passed=t2_passed,
        final_classification="pass_tier2" if t2_passed else "drop_persistent",
        tier1_classification=tier1_cls,
        rationale=f"Tier 1: {tier1_rationale} | Tier 2: {t2_rationale}",
        tier2_seat_bias_progress=progress,
    )


def load_game(path: str | Path) -> GameDefV2:
    """Load a GameDefV2 from a JSON file (matching r18_ppo_smoke convention)."""
    with open(Path(path)) as f:
        return GameDefV2.from_dict(json.load(f))
