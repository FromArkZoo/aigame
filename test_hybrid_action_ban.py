#!/usr/bin/env python3
"""D1 patch test — hybrid-action penalty in GoEssenceScorer.evaluate_game.

R17 22-team eval + R18 5-substrate run found 0% move-action usage across
every hybrid game evaluated. D1 applies a hard 0.2x soft-ban so place-only
wins selection in evolution. This test exercises the patch end-to-end:
identical training_results, only `action_rule.has_move()` differs, and
the hybrid game's go_essence comes out exactly 5x lower.

Run as: .venv/bin/python test_hybrid_action_ban.py
"""
from __future__ import annotations

import sys
import traceback
from dataclasses import dataclass, field

from config import MetricsConfig
from metrics.scoring import GoEssenceScorer


# Minimal stubs — evaluate_game only touches `total_complexity()`,
# `action_rule.has_move()`, `topology_type`, and the optional `uses_ca` /
# `ca_rule` / `capture_rule` / `win_condition` / `num_dimensions` attrs
# referenced by structural_fingerprint (only when novelty is asked for).

@dataclass
class _ActionRuleStub:
    has_move_value: bool = False
    action_types: tuple = ("place",)

    def has_move(self) -> bool:
        return self.has_move_value


@dataclass
class _GameStub:
    complexity: int = 10
    action_rule: _ActionRuleStub = field(default_factory=_ActionRuleStub)
    topology_type: str = "grid"

    def total_complexity(self) -> int:
        return self.complexity


def _scorer() -> GoEssenceScorer:
    return GoEssenceScorer(MetricsConfig())


def _training_results() -> dict:
    """Healthy training_results that don't trip any of the other penalties.

    avg_game_length 30 (above the 15-move floor, below 90% of max_turns=200);
    p0_winrate 0.5 (max non_triv balance); trained_vs_random 0.85 (high
    competence); learning_curve climbs steadily. No per_run series so the
    stability penalty is skipped.
    """
    return {
        "learning_curve": [(500*i, 0.1 + 0.08*i) for i in range(1, 11)],
        "training_budget": 5000,
        "trained_vs_random_winrate": 0.85,
        "p1_winrate": 0.5,
        "p0_winrate": 0.5,
        "heuristic_p1_winrate": 0.5,
        "heuristic_decisive_rate": 0.0,
        "greedy_p1_winrate": 0.5,
        "greedy_decisive_rate": 0.0,
        "avg_game_length": 30.0,
        "max_turns": 200,
    }


def _check(label: str, ok: bool, *, detail: str = "") -> bool:
    status = "PASS" if ok else "FAIL"
    print(f"  {status} | {label}{(': ' + detail) if detail else ''}")
    return ok


def _approx(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(a - b) <= tol


def test_place_only_unaffected():
    sc = _scorer()
    game = _GameStub(action_rule=_ActionRuleStub(has_move_value=False))
    res = sc.evaluate_game(game, _training_results())
    return _check(
        "place-only game -> hybrid_action_penalty == 1.0",
        _approx(res["hybrid_action_penalty"], 1.0),
        detail=f"penalty={res['hybrid_action_penalty']} ge={res['go_essence']:.4f}",
    )


def test_hybrid_penalised_5x():
    sc = _scorer()
    place_only = _GameStub(action_rule=_ActionRuleStub(has_move_value=False))
    hybrid = _GameStub(action_rule=_ActionRuleStub(
        has_move_value=True, action_types=("place", "move")
    ))
    res_p = sc.evaluate_game(place_only, _training_results())
    res_h = sc.evaluate_game(hybrid, _training_results())
    # Both pass through identical math except the 0.2x penalty on hybrid.
    expected_h = res_p["go_essence"] * 0.2
    return _check(
        "hybrid game's go_essence is exactly 0.2x the place-only equivalent",
        _approx(res_h["go_essence"], expected_h)
        and _approx(res_h["hybrid_action_penalty"], 0.2),
        detail=f"place-only ge={res_p['go_essence']:.6f} | "
               f"hybrid ge={res_h['go_essence']:.6f} | "
               f"expected={expected_h:.6f}",
    )


def test_subscores_unchanged_by_hybrid_penalty():
    """Penalty applies only to composite — sub-scores should be identical."""
    sc = _scorer()
    place_only = _GameStub(action_rule=_ActionRuleStub(has_move_value=False))
    hybrid = _GameStub(action_rule=_ActionRuleStub(
        has_move_value=True, action_types=("place", "move")
    ))
    res_p = sc.evaluate_game(place_only, _training_results())
    res_h = sc.evaluate_game(hybrid, _training_results())
    keys_should_match = (
        "rule_simplicity", "strategic_depth",
        "non_triviality", "strategic_diversity", "seat_balance",
    )
    all_match = all(_approx(res_p[k], res_h[k]) for k in keys_should_match)
    return _check(
        "hybrid penalty leaves sub-scores untouched (only composite drops)",
        all_match,
        detail="; ".join(
            f"{k}: p={res_p[k]:.4f} h={res_h[k]:.4f}" for k in keys_should_match
        ),
    )


def test_place_only_zero_stays_zero_under_hybrid():
    """A hybrid game whose composite is already 0 (e.g. seat-balance hard zero)
    stays at 0 — the 0.2x multiplier is harmless."""
    sc = _scorer()
    # Force seat-balance hard-zero by setting heur_p0 deeply asymmetric.
    tr = _training_results()
    tr["heuristic_p1_winrate"] = 0.99
    tr["heuristic_decisive_rate"] = 1.0
    tr["greedy_p1_winrate"] = 0.99
    tr["greedy_decisive_rate"] = 1.0
    hybrid = _GameStub(action_rule=_ActionRuleStub(
        has_move_value=True, action_types=("place", "move")
    ))
    res = sc.evaluate_game(hybrid, tr)
    return _check(
        "hybrid game with seat-balance-zeroed composite stays at 0",
        _approx(res["go_essence"], 0.0)
        and _approx(res["hybrid_action_penalty"], 0.2),
        detail=f"ge={res['go_essence']} penalty={res['hybrid_action_penalty']}",
    )


def test_penalty_applied_before_substrate_novelty_bonus():
    """The 1.05x non-grid topology multiplier should apply ON TOP of the
    hybrid penalty, not the other way around. So a hybrid non-grid game
    is penalised then mildly bonus'd, NOT vice-versa.
    Verify: hybrid_non_grid_ge ≈ place_only_grid_ge * (depth/topology_factor) * 0.2 * 1.05
    Easier check: hybrid_non_grid / place_only_non_grid == 0.2 (penalty
    isolates cleanly even with the substrate bonus active)."""
    sc = _scorer()
    place_only_carpet = _GameStub(
        topology_type="sierpinski",
        action_rule=_ActionRuleStub(has_move_value=False),
    )
    hybrid_carpet = _GameStub(
        topology_type="sierpinski",
        action_rule=_ActionRuleStub(
            has_move_value=True, action_types=("place", "move")
        ),
    )
    res_p = sc.evaluate_game(place_only_carpet, _training_results())
    res_h = sc.evaluate_game(hybrid_carpet, _training_results())
    if res_p["go_essence"] == 0.0:
        return _check("hybrid:place-only ratio is 0.2 with non-grid bonus",
                      False, detail="place-only carpet ge=0; can't compute ratio")
    ratio = res_h["go_essence"] / res_p["go_essence"]
    return _check(
        "hybrid:place-only ratio is exactly 0.2 even on non-grid topology",
        _approx(ratio, 0.2, tol=1e-6),
        detail=f"place_only={res_p['go_essence']:.6f} hybrid={res_h['go_essence']:.6f} "
               f"ratio={ratio:.6f}",
    )


def test_r18_top_games_unaffected():
    """Sanity: every R18 substrate's top game is place-only, so D1 is a
    no-op for them. We approximate by running place-only stubs and
    checking penalty=1.0 for all."""
    sc = _scorer()
    substrates = ["sierpinski", "vicsek", "menger", "grid"]
    all_unaffected = True
    detail_parts = []
    for sub in substrates:
        game = _GameStub(
            topology_type=sub,
            action_rule=_ActionRuleStub(has_move_value=False),
        )
        res = sc.evaluate_game(game, _training_results())
        affected = not _approx(res["hybrid_action_penalty"], 1.0)
        if affected:
            all_unaffected = False
        detail_parts.append(f"{sub}={res['hybrid_action_penalty']}")
    return _check(
        "R18 top games (all place-only across substrates) -> penalty 1.0",
        all_unaffected,
        detail=", ".join(detail_parts),
    )


def main() -> int:
    print("=" * 72)
    print("D1 patch — hybrid-action ban tests")
    print("=" * 72)
    tests = [
        test_place_only_unaffected,
        test_hybrid_penalised_5x,
        test_subscores_unchanged_by_hybrid_penalty,
        test_place_only_zero_stays_zero_under_hybrid,
        test_penalty_applied_before_substrate_novelty_bonus,
        test_r18_top_games_unaffected,
    ]
    passed = failed = 0
    for t in tests:
        try:
            ok = t()
            passed += int(ok)
            failed += int(not ok)
        except Exception:
            failed += 1
            print(f"  FAIL | {t.__name__}: exception")
            traceback.print_exc()
    print("-" * 72)
    print(f"{passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
