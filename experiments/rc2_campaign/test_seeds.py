import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pytest
from experiments.rc2_campaign import seeds


def test_bases_are_base19():
    assert seeds.GEN_SEED_BASE == 19_000_000
    assert seeds.ARM_R_SEED_BASE == 38_000_000
    assert seeds.ARM_M_MUT_SEED == 57_000_000
    assert seeds.ARM_M_SEL_SEED == 76_000_000
    assert seeds.BOOT_SEED == 95_000_000


def test_disjoint_passes_on_registered_layout():
    seeds.assert_disjoint()  # the registered bases must not overlap recorded streams


def test_disjoint_catches_overlap(monkeypatch):
    # A base colliding with Phase C base-13 (13_000_000 .. +span) must raise.
    monkeypatch.setattr(seeds, "GEN_SEED_BASE", 13_000_100)
    with pytest.raises(RuntimeError):
        seeds.assert_disjoint()
