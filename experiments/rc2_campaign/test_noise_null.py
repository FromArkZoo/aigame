"""Synthetic tests for the NOISE-NULL §0 instrument (no campaign data)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.rc2_campaign.noise_null import (  # noqa: E402
    draw_rate_for_sigma,
    noise_null_floor,
    p90_minus_p10,
    sample_family_floored_pg,
    N_GAMES,
)


def test_draw_rate_recovers_target_sigma():
    # d calibrated for a target sigma must reproduce that per-genome SD.
    rng = np.random.default_rng(1)
    for sigma in (0.05, 0.087, 0.1016):
        d = draw_rate_for_sigma(sigma)
        # unfloored per-genome PG SD (floor would bias the check)
        p_side = (1 - d) / 2
        draws = rng.choice([0.0, 0.5, 1.0], size=(200_000, N_GAMES),
                           p=[p_side, d, p_side])
        pg = draws.mean(axis=1) - 0.5
        assert abs(pg.std() - sigma) < 0.003, (sigma, pg.std())


def test_draw_rate_clamped():
    # sigma above the fair-coin max -> d clamps to 0, never negative.
    assert draw_rate_for_sigma(0.5) == 0.0
    assert 0.0 <= draw_rate_for_sigma(0.087) <= 1.0


def test_floored_values_nonnegative():
    rng = np.random.default_rng(2)
    vals = sample_family_floored_pg(50, draw_rate_for_sigma(0.1016), rng)
    assert vals.shape == (50,)
    assert (vals >= 0).all()


def test_floor_monotonic_in_sigma():
    # More per-genome noise -> wider null spread -> higher floor.
    lo = noise_null_floor(24, 0.05, 4000, np.random.default_rng(3))
    hi = noise_null_floor(24, 0.1016, 4000, np.random.default_rng(3))
    assert hi > lo


def test_raw_reproduces_draft_reference():
    # The draft's provisional "approx 0.28 @ N=20, sigma=0.087" reproduces on
    # RAW (unfloored) T1-PG — this explains the draft number.
    raw = noise_null_floor(20, 0.087, 20_000, np.random.default_rng(95_000_000),
                           floored=False)
    assert 0.24 <= raw <= 0.32, raw


def test_floored_is_binding_and_lower():
    # The bar (§3/§6) compares FLOORED T1-PG; the floored floor is what binds,
    # and it is lower than the raw floor (raw was the draft's slip).
    seed = 95_000_000
    floored = noise_null_floor(20, 0.087, 20_000, np.random.default_rng(seed),
                               floored=True)
    raw = noise_null_floor(20, 0.087, 20_000, np.random.default_rng(seed),
                           floored=False)
    assert floored < raw
    assert 0.12 <= floored <= 0.18, floored


def test_reproducible_with_seed():
    a = noise_null_floor(30, 0.1016, 3000, np.random.default_rng(7))
    b = noise_null_floor(30, 0.1016, 3000, np.random.default_rng(7))
    assert a == b


def test_p90_minus_p10_basic():
    v = np.array([0.0, 0.0, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7])
    assert p90_minus_p10(v) > 0
    assert p90_minus_p10(np.zeros(10)) == 0.0
