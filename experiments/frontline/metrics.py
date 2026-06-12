"""FRONTLINE metrics (prereg Stage 1.5/2 definitions).

Drama is DIAGNOSTIC-ONLY by registration (closeness Goodhart — prereg
Stage 1.5); winner_behindness is imported from siege metrics unchanged.
control-flip instrumentation comes from the siege screen (identical r=2
instrumentation — the registered cross-arm comparable).
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from experiments.siege.metrics import winner_behindness  # noqa: E402, F401


def score_share_progress(s_self: int, s_opp: int) -> float:
    """progress_p = S_p / max(1, S_p + S_opp)  (spec §8 drama-trace row)."""
    return s_self / max(1, s_self + s_opp)
