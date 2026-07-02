"""Campaign seed bases (base 19 x {1..5}) + hard disjointness assert (prereg
§2 [C1]). The runner calls assert_disjoint() and refuses to start on overlap."""
from __future__ import annotations

GEN_SEED_BASE = 19_000_000
ARM_R_SEED_BASE = 38_000_000
ARM_M_MUT_SEED = 57_000_000
ARM_M_SEL_SEED = 76_000_000
BOOT_SEED = 95_000_000
SPAN = 1_000_000

def _campaign_ranges() -> dict[str, tuple[int, int]]:
    return {n: (b, b + SPAN) for n, b in {
        "gen": GEN_SEED_BASE, "arm_r": ARM_R_SEED_BASE,
        "arm_m_mut": ARM_M_MUT_SEED, "arm_m_sel": ARM_M_SEL_SEED,
        "boot": BOOT_SEED}.items()}

RECORDED_STREAMS = {
    **{f"phaseC_b13_{i}": (b, b + SPAN) for i, b in enumerate(
        (13_000_000, 26_000_000, 39_000_000, 52_000_000, 65_000_000))},
    **{f"phaseCr2_b17_{i}": (b, b + SPAN) for i, b in enumerate(
        (17_000_000, 34_000_000, 51_000_000, 68_000_000, 85_000_000))},
    "anchor_small": (42, 48),   # streams 42..47 inclusive
    "smoke": (999_000_000, 999_100_000),
}

def _overlap(a, b):
    return a[0] < b[1] and b[0] < a[1]

def assert_disjoint() -> None:
    for name, rng in _campaign_ranges().items():
        for other, orng in RECORDED_STREAMS.items():
            if _overlap(rng, orng):
                raise RuntimeError(f"seed overlap: campaign {name}{rng} vs {other}{orng}")
