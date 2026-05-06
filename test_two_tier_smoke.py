#!/usr/bin/env python3
"""Two-tier smoke gate classification tests (R20 S2).

Tests classify_tier1 + evaluate_tier2 against the postmortem's spec, using
hand-crafted SmokeVerdict instances. PPO itself is exercised by the
existing r18_ppo_smoke harness tests; this module gates ONLY the gate logic.

Per R19_postmortem.md:
- Tier 1 catastrophic = seat_bias >= 0.45, OR sampled_avg_len < 15,
  OR (greedy_p1_wr >= 0.95 AND seat_bias >= 0.40)
- Borderline = soft-floor failure (length_floor or seat_bias > 0.30) but
  not catastrophic
- Tier 2 pass = soft floors clear at 6000 ep OR seat_bias dropped >= 0.05

Run as: .venv/bin/python test_two_tier_smoke.py
"""

from __future__ import annotations

import sys
import traceback

from experiments.r18_ppo_smoke.harness import SmokeVerdict
from experiments.r20_smoke_two_tier.harness import (
    CATASTROPHIC_GREEDY_BIAS,
    CATASTROPHIC_GREEDY_WR,
    CATASTROPHIC_LENGTH_MIN,
    CATASTROPHIC_SEAT_BIAS,
    CLS_BORDERLINE,
    CLS_CATASTROPHIC,
    CLS_PASS,
    TIER2_SEAT_BIAS_PROGRESS,
    classify_tier1,
    evaluate_tier2,
)


passed: list[str] = []
failed: list[tuple[str, str]] = []


def case(name: str, fn) -> None:
    try:
        fn()
        passed.append(name)
        print(f"  PASS  {name}")
    except Exception as e:  # noqa: BLE001
        failed.append((name, traceback.format_exc()))
        print(f"  FAIL  {name}: {e}")


def make_verdict(
    *,
    sampled_avg_length: float = 30.0,
    seat_bias: float = 0.10,
    greedy_p1_winrate: float = 0.50,
    length_floor: float = 8.0,
    passed_overall: bool | None = None,
    drop_reasons: list[str] | None = None,
) -> SmokeVerdict:
    """Build a SmokeVerdict with the gate-relevant fields, sensible defaults
    for the rest. Auto-derives passed/drop_reasons from soft-floor checks
    if not explicitly provided.
    """
    if drop_reasons is None:
        drop_reasons = []
        if sampled_avg_length < length_floor:
            drop_reasons.append(
                f"sampled_avg_length {sampled_avg_length:.1f} < floor {length_floor:.1f}"
            )
        # Soft seat-bias floor (existing harness): 0.30
        if seat_bias > 0.30:
            drop_reasons.append(
                f"seat bias {seat_bias:.2f} > 0.30 (forced-win)"
            )
    if passed_overall is None:
        passed_overall = len(drop_reasons) == 0
    return SmokeVerdict(
        game_id="test_game",
        topology_type="grid",
        axis_size=4,
        num_dimensions=2,
        passed=passed_overall,
        drop_reasons=drop_reasons,
        sampled_avg_length=sampled_avg_length,
        length_floor=length_floor,
        active_cells=16,
        greedy_p1_winrate=greedy_p1_winrate,
        seat_bias=seat_bias,
        seat_bias_threshold=0.30,
        deterministic_avg_length=2.0,
        trained_p0_winrate=0.5,
        trained_vs_random_winrate=0.5,
        heuristic_p1_winrate=0.5,
        training_budget=3000,
        eval_episodes=100,
        seed=42,
        elapsed_seconds=10.0,
    )


# ----------------------------------------------------------------------
# classify_tier1 tests
# ----------------------------------------------------------------------


def test_clean_pass() -> None:
    v = make_verdict(sampled_avg_length=30.0, seat_bias=0.10)
    cls, _ = classify_tier1(v)
    assert cls == CLS_PASS, f"clean game should pass, got {cls}"


def test_catastrophic_seat_bias() -> None:
    v = make_verdict(sampled_avg_length=30.0, seat_bias=CATASTROPHIC_SEAT_BIAS)
    cls, rat = classify_tier1(v)
    assert cls == CLS_CATASTROPHIC, f"got {cls}"
    assert "seat_bias" in rat


def test_catastrophic_seat_bias_above() -> None:
    v = make_verdict(sampled_avg_length=30.0, seat_bias=0.50)
    cls, _ = classify_tier1(v)
    assert cls == CLS_CATASTROPHIC


def test_catastrophic_length() -> None:
    v = make_verdict(
        sampled_avg_length=10.0, seat_bias=0.10, length_floor=8.0,
    )
    cls, rat = classify_tier1(v)
    assert cls == CLS_CATASTROPHIC, f"len 10 < 15 should be catastrophic, got {cls}"
    assert "len" in rat or "length" in rat.lower()


def test_catastrophic_greedy_dominance() -> None:
    v = make_verdict(
        sampled_avg_length=30.0,
        seat_bias=CATASTROPHIC_GREEDY_BIAS,
        greedy_p1_winrate=CATASTROPHIC_GREEDY_WR,
    )
    cls, _ = classify_tier1(v)
    assert cls == CLS_CATASTROPHIC


def test_borderline_soft_seat_bias() -> None:
    """Seat bias 0.36 (R19 m1-m5 cluster value) — borderline, NOT catastrophic."""
    v = make_verdict(sampled_avg_length=39.7, seat_bias=0.36, length_floor=40.0)
    cls, rat = classify_tier1(v)
    assert cls == CLS_BORDERLINE, (
        f"R19 m1-m5 seat bias 0.36 + len 39.7 must be borderline, got {cls}: {rat}"
    )


def test_borderline_length_only() -> None:
    """Length below soft floor but above the catastrophic 15 threshold,
    seat bias clean — borderline."""
    v = make_verdict(sampled_avg_length=18.0, seat_bias=0.10, length_floor=20.0)
    cls, _ = classify_tier1(v)
    assert cls == CLS_BORDERLINE, f"got {cls}"


def test_pass_at_exact_soft_threshold() -> None:
    """Seat bias exactly 0.30 (the existing soft floor) — should still pass.
    The harness's existing condition uses `> 0.30`."""
    v = make_verdict(sampled_avg_length=30.0, seat_bias=0.30)
    cls, _ = classify_tier1(v)
    assert cls == CLS_PASS, f"seat bias 0.30 == soft floor should pass, got {cls}"


def test_catastrophic_length_at_boundary() -> None:
    """sampled_avg_len exactly 15.0 should NOT be catastrophic (strict < check)."""
    v = make_verdict(sampled_avg_length=15.0, seat_bias=0.10, length_floor=8.0)
    cls, _ = classify_tier1(v)
    assert cls != CLS_CATASTROPHIC


# ----------------------------------------------------------------------
# evaluate_tier2 tests
# ----------------------------------------------------------------------


def test_tier2_soft_floors_clear() -> None:
    """Tier 2 cleared all floors — pass via condition A."""
    t1 = make_verdict(sampled_avg_length=39.7, seat_bias=0.36, length_floor=40.0)
    t2 = make_verdict(sampled_avg_length=45.0, seat_bias=0.20, length_floor=40.0)
    ok, _, progress = evaluate_tier2(t1, t2)
    assert ok, "Tier 2 with cleared floors must pass"
    # Even though A passed, progress is reported.
    assert abs(progress - 0.16) < 1e-6, f"progress mismatch: {progress}"


def test_tier2_progress_signal() -> None:
    """Tier 2 still failing soft floors but seat bias dropped >= 0.05 — pass via B."""
    t1 = make_verdict(sampled_avg_length=39.7, seat_bias=0.36, length_floor=40.0)
    t2 = make_verdict(sampled_avg_length=39.5, seat_bias=0.30, length_floor=40.0)
    # Note: t2 still soft-fails on length, but seat bias dropped 0.06 >= 0.05.
    ok, rat, progress = evaluate_tier2(t1, t2)
    assert ok, f"Tier 2 progress 0.06 should pass (got rat={rat})"
    assert "progress" in rat.lower()
    assert progress >= TIER2_SEAT_BIAS_PROGRESS


def test_tier2_persistent_failure() -> None:
    """Tier 2 failing AND no meaningful progress — drop persistent."""
    t1 = make_verdict(sampled_avg_length=39.7, seat_bias=0.36, length_floor=40.0)
    t2 = make_verdict(sampled_avg_length=39.5, seat_bias=0.34, length_floor=40.0)
    # progress = 0.02, < 0.05.
    ok, rat, progress = evaluate_tier2(t1, t2)
    assert not ok, f"Tier 2 progress 0.02 should fail (got rat={rat})"
    assert progress < TIER2_SEAT_BIAS_PROGRESS


def test_tier2_seat_bias_worsened() -> None:
    """Tier 2 actually got WORSE — drop persistent, progress is negative."""
    t1 = make_verdict(sampled_avg_length=39.7, seat_bias=0.36, length_floor=40.0)
    t2 = make_verdict(sampled_avg_length=38.0, seat_bias=0.42, length_floor=40.0)
    ok, _, progress = evaluate_tier2(t1, t2)
    assert not ok
    assert progress < 0


def test_tier2_progress_at_exact_threshold() -> None:
    """Progress exactly 0.05 should pass (>= check)."""
    t1 = make_verdict(sampled_avg_length=39.7, seat_bias=0.40, length_floor=40.0)
    t2 = make_verdict(sampled_avg_length=39.5, seat_bias=0.35, length_floor=40.0)
    ok, _, progress = evaluate_tier2(t1, t2)
    assert abs(progress - 0.05) < 1e-9
    assert ok, "progress == 0.05 must pass"


# ----------------------------------------------------------------------
# Postmortem-grounded scenarios — the actual R19 m1-m5 numbers
# ----------------------------------------------------------------------


def test_r19_m1_m5_pattern_borderline_then_pass_via_progress() -> None:
    """R19 m1-m5 had len ~39.7 (just under 40.0 floor), seat_bias 0.36.
    Postmortem hypothesis: at 6000 ep PPO closes some of the gap. Even
    if soft floors don't fully clear, a 0.05 drop in seat_bias is enough.
    """
    t1 = make_verdict(sampled_avg_length=39.7, seat_bias=0.36, length_floor=40.0)
    cls, _ = classify_tier1(t1)
    assert cls == CLS_BORDERLINE
    # Hypothetical Tier 2: still slightly under length floor, seat bias 0.30.
    t2 = make_verdict(sampled_avg_length=39.9, seat_bias=0.30, length_floor=40.0)
    ok, _, progress = evaluate_tier2(t1, t2)
    assert ok
    assert progress == 0.36 - 0.30


def test_r19_g1_pattern_drops_catastrophic() -> None:
    """R19 g1 (R8 Connection Go on grid): seat_bias 0.50 — catastrophic."""
    v = make_verdict(sampled_avg_length=20.0, seat_bias=0.50)
    cls, _ = classify_tier1(v)
    assert cls == CLS_CATASTROPHIC, "g1's 0.50 bias must be hard-dropped"


# ----------------------------------------------------------------------
# Entry
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("\n=== Two-tier smoke gate tests (S2, R20) ===\n")

    case("clean game passes", test_clean_pass)
    case("catastrophic seat bias 0.45", test_catastrophic_seat_bias)
    case("catastrophic seat bias > 0.45", test_catastrophic_seat_bias_above)
    case("catastrophic length < 15", test_catastrophic_length)
    case("catastrophic greedy dominance (wr 0.95 + bias 0.40)",
         test_catastrophic_greedy_dominance)
    case("borderline: R19 m1-m5 numbers", test_borderline_soft_seat_bias)
    case("borderline: length only", test_borderline_length_only)
    case("seat bias exactly 0.30 passes (soft floor is >)",
         test_pass_at_exact_soft_threshold)
    case("length exactly 15.0 not catastrophic", test_catastrophic_length_at_boundary)
    case("tier2 condition A: soft floors clear", test_tier2_soft_floors_clear)
    case("tier2 condition B: progress signal", test_tier2_progress_signal)
    case("tier2 persistent failure", test_tier2_persistent_failure)
    case("tier2 worsened (negative progress)", test_tier2_seat_bias_worsened)
    case("tier2 progress at exact threshold", test_tier2_progress_at_exact_threshold)
    case("R19 m1-m5 round-trip: borderline then pass via progress",
         test_r19_m1_m5_pattern_borderline_then_pass_via_progress)
    case("R19 g1 catastrophic (0.50 seat bias)",
         test_r19_g1_pattern_drops_catastrophic)

    print(f"\n{len(passed)} passed, {len(failed)} failed")
    if failed:
        print("\n--- failures ---")
        for name, tb in failed:
            print(f"\n{name}:\n{tb}")
        sys.exit(1)
    sys.exit(0)
