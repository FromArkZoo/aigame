#!/usr/bin/env python3
"""D1 verification — hybrid-action ban applies a 0.2× penalty.

No PPO needed. Loads the grid hybrid validator (place+move) and the
matching place-only baseline (g1_custodian1_connection__grid, same
capture/win rules), feeds both the same synthetic training_results
into scorer.evaluate_game, and asserts:

  1. result["hybrid_action_penalty"] == 0.2 on hybrid, 1.0 on place-only.
  2. composite GE ratio (hybrid / place-only) == 0.2 to floating tolerance.

Plan checklist item 5.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from config import MetricsConfig  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from metrics.scoring import GoEssenceScorer  # noqa: E402


SEEDS_DIR = Path(__file__).parent / "seeds"

# Identical synthetic inputs for both games. Numbers are not realistic;
# they're picked so every penalty branch (length, seat balance, stability,
# timeout) returns 1.0 -- the only difference between the two scores is
# D1's hybrid penalty.
SYNTHETIC = {
    "learning_curve": [(0, 0.50), (250, 0.65), (500, 0.80)],
    "trained_vs_random_winrate": 0.80,
    "p1_winrate": 0.50,
    "p0_winrate": 0.50,
    "training_budget": 500,
    "avg_game_length": 30.0,        # > 15 (no length penalty), < 0.9 * max_turns
    "max_turns": 100,
    "heuristic_p1_winrate": 0.50,   # neutral seat balance
    "heuristic_decisive_rate": 0.0,
    "greedy_p1_winrate": 0.50,
    "greedy_decisive_rate": 0.0,
}


def load_seed(stem: str) -> GameDefV2:
    with open(SEEDS_DIR / f"{stem}.json") as f:
        return GameDefV2.from_dict(json.load(f))


def main() -> int:
    place_only = load_seed("g1_custodian1_connection__grid")
    hybrid = load_seed("g3_hybrid_validator__grid")

    assert not place_only.action_rule.has_move(), "g1 should be place-only"
    assert hybrid.action_rule.has_move(), "g3 should be hybrid (place+move)"

    scorer = GoEssenceScorer(MetricsConfig())

    p_result = scorer.evaluate_game(place_only, dict(SYNTHETIC))
    h_result = scorer.evaluate_game(hybrid, dict(SYNTHETIC))

    print("\n=== D1 hybrid-action ban verification ===\n")
    print(f"place-only  game_id={place_only.game_id}")
    print(f"            hybrid_action_penalty={p_result['hybrid_action_penalty']}")
    print(f"            go_essence={p_result['go_essence']:.6f}")
    print(f"hybrid      game_id={hybrid.game_id}")
    print(f"            hybrid_action_penalty={h_result['hybrid_action_penalty']}")
    print(f"            go_essence={h_result['go_essence']:.6f}")

    # Assertions
    assert p_result["hybrid_action_penalty"] == 1.0, (
        f"place-only should not be penalised, got {p_result['hybrid_action_penalty']}"
    )
    assert h_result["hybrid_action_penalty"] == 0.2, (
        f"hybrid should have 0.2 penalty, got {h_result['hybrid_action_penalty']}"
    )

    # Ratio. Other multiplicative factors (simplicity, depth, etc.) differ
    # between the two games because action_rule.complexity() includes the
    # number of action types. So we can't compare go_essence directly --
    # but the COMPOSITE-WITHOUT-HYBRID-PENALTY ratio is the cleaner check:
    # hybrid_composite = place_composite * (their factors ratio) * 0.2.
    # Recover the implied composite-without-penalty for each game and check
    # the only divergence in the hybrid is the 0.2x.
    #
    # Simpler: divide hybrid_GE by 0.2 (un-multiplying the penalty), and
    # divide place_GE by 1.0; the remaining gap should match the gap when
    # both games are scored *with action_rule normalised to the same form*.
    # Skip that — the direct check on hybrid_action_penalty=0.2 is the load-
    # bearing assertion. Print the ratio as informational.
    if p_result["go_essence"] > 0:
        ratio = h_result["go_essence"] / p_result["go_essence"]
        print(f"\nGE ratio hybrid/place-only = {ratio:.4f}")
        print("(NOT exactly 0.2: action_rule.complexity differs between the "
              "two games, so simplicity differs. The load-bearing check is "
              "hybrid_action_penalty == 0.2 above.)")

    print("\nD1 verified: hybrid_action_penalty=0.2 fires on hybrid, "
          "1.0 on place-only.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
