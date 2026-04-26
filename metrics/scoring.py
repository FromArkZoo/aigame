"""Go Essence metrics for evaluating generated games.

Implements all scoring dimensions of the Go Essence framework:
- Rule simplicity: how compact the game rules are (AST node count)
- Strategic depth: how much skill can be learned (learning curve analysis)
- Non-triviality: whether the game is balanced and learnable
- Strategic diversity: whether multiple viable strategies exist
- Composite Go Essence score combining all dimensions

All individual scores are normalized to the [0, 1] range.
"""

from __future__ import annotations

import math
import warnings
from typing import TYPE_CHECKING

import numpy as np
from scipy.optimize import curve_fit

from config import MetricsConfig

if TYPE_CHECKING:
    from game_engine.representation import GameDef
    from game_engine.game_def_v2 import GameDefV2


# ---------------------------------------------------------------------------
# Curve-fitting helpers
# ---------------------------------------------------------------------------

def _logarithmic_curve(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    """Logarithmic learning curve: a * log(b * x + 1) + c."""
    return a * np.log(b * np.clip(x, 1e-12, None) + 1.0) + c


def _exponential_saturation(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    """Exponential saturation curve: a * (1 - exp(-b * x)) + c.

    Models a learning curve that rises quickly at first and then levels off.
    """
    return a * (1.0 - np.exp(-b * x)) + c


def _fit_learning_curve(
    episodes: np.ndarray,
    winrates: np.ndarray,
) -> tuple[np.ndarray, str]:
    """Try to fit a learning curve to the data; return predicted values and model name.

    Attempts exponential saturation first, then logarithmic, then falls back
    to raw data if both fail.

    Returns
    -------
    predicted : np.ndarray
        Predicted winrate values at the given episode counts.
    model_name : str
        Which model was used ('exponential', 'logarithmic', or 'raw').
    """
    if len(episodes) < 3:
        return winrates.copy(), "raw"

    # Normalize episodes to [0, 1] for numerical stability during fitting
    x_max = float(np.max(episodes))
    if x_max == 0:
        return winrates.copy(), "raw"
    x_norm = episodes / x_max

    # Try exponential saturation first
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            popt, _ = curve_fit(
                _exponential_saturation,
                x_norm,
                winrates,
                p0=[0.5, 2.0, 0.3],
                maxfev=2000,
                bounds=([-2.0, 0.0, -1.0], [2.0, 50.0, 1.0]),
            )
        predicted = _exponential_saturation(x_norm, *popt)
        return np.clip(predicted, 0.0, 1.0), "exponential"
    except (RuntimeError, ValueError):
        pass

    # Fall back to logarithmic
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            popt, _ = curve_fit(
                _logarithmic_curve,
                x_norm,
                winrates,
                p0=[0.2, 1.0, 0.3],
                maxfev=2000,
                bounds=([-2.0, 0.0, -1.0], [2.0, 50.0, 1.0]),
            )
        predicted = _logarithmic_curve(x_norm, *popt)
        return np.clip(predicted, 0.0, 1.0), "logarithmic"
    except (RuntimeError, ValueError):
        pass

    return winrates.copy(), "raw"


def _compute_auc(episodes: np.ndarray, winrates: np.ndarray) -> float:
    """Compute normalized area under the learning curve using the trapezoidal rule.

    The AUC is normalized by the total episode range so the result is
    the average winrate across training.  Returns 0 for degenerate inputs.
    """
    if len(episodes) < 2:
        return 0.0
    span = float(episodes[-1] - episodes[0])
    if span <= 0:
        return 0.0
    # np.trapezoid was introduced in numpy 2.0; older versions use np.trapz
    _trapz = getattr(np, "trapezoid", getattr(np, "trapz", None))
    return float(_trapz(winrates, episodes) / span)


def _estimate_plateau_fraction(
    episodes: np.ndarray,
    winrates: np.ndarray,
    improvement_threshold: float = 0.01,
) -> float:
    """Estimate how far into training the learning curve plateaus.

    Returns the fraction of total training at which improvement per window
    drops below *improvement_threshold*.  A value close to 1.0 means the
    agent is still learning at the end (deep game).  A value close to 0.0
    means the agent plateaued very early (shallow game).
    """
    if len(episodes) < 4:
        return 0.5  # not enough data; return neutral

    n = len(winrates)
    window = max(1, n // 5)

    for i in range(window, n):
        recent_improvement = float(np.mean(winrates[max(0, i - window + 1) : i + 1])
                                    - np.mean(winrates[max(0, i - 2 * window + 1) : i - window + 1]))
        if abs(recent_improvement) < improvement_threshold:
            return float(episodes[i] - episodes[0]) / float(episodes[-1] - episodes[0])

    return 1.0  # never plateaued


# ---------------------------------------------------------------------------
# GoEssenceScorer
# ---------------------------------------------------------------------------

class GoEssenceScorer:
    """Computes all Go Essence metrics for a game.

    Each metric returns a score in [0, 1].  The composite ``go_essence``
    score combines them into a single quality measure that rewards games
    with simple rules yet deep, balanced, diverse strategy.
    """

    def __init__(self, config: MetricsConfig):
        self.config = config

    # ------------------------------------------------------------------
    # Individual metrics
    # ------------------------------------------------------------------

    def rule_simplicity(self, game) -> float:
        """Rule simplicity score (lower complexity = higher score).

        For V1 games: uses the total AST node count across all expression
        trees (transition, termination, reward).
        For V2 games: uses the total_complexity() method which counts
        meaningful rule parameters.

        .. math::

            \\text{simplicity} = \\frac{1}{1 + \\ln(\\text{total\\_nodes})}

        Returns a value in (0, 1] where 1 is the simplest possible game.
        """
        total_nodes = game.total_complexity()

        # Guard against pathological cases
        total_nodes = max(total_nodes, 1)

        simplicity = 1.0 / (1.0 + math.log(total_nodes))
        return float(np.clip(simplicity, 0.0, 1.0))

    def strategic_depth(
        self,
        learning_curve: list[tuple[int, float]],
        training_budget: int,
    ) -> float:
        """Strategic depth from learning-curve analysis.

        Three sub-signals are combined:

        1. **AUC** -- area under the normalized learning curve.  Higher AUC
           means the agent consistently improves, suggesting depth.
        2. **Plateau fraction** -- how late into training the agent plateaus.
           Later plateaus imply more to learn.
        3. **Late-stage sensitivity** -- improvement in the second half of
           training compared to the first half.  Continued improvement late
           in training indicates depth.

        The final score is the mean of the three sub-signals, clipped to [0, 1].

        Parameters
        ----------
        learning_curve : list of (episode, winrate) tuples
            The training history.  Winrates should be in [0, 1].
        training_budget : int
            The total episode budget allocated for training.
        """
        # --- edge cases ---
        if not learning_curve or len(learning_curve) < 2:
            return 0.0

        episodes = np.array([pt[0] for pt in learning_curve], dtype=np.float64)
        winrates = np.array([pt[1] for pt in learning_curve], dtype=np.float64)

        # Replace any NaNs / infs with 0
        nan_mask = ~np.isfinite(winrates)
        if np.any(nan_mask):
            winrates[nan_mask] = 0.0
        nan_mask_ep = ~np.isfinite(episodes)
        if np.any(nan_mask_ep):
            episodes[nan_mask_ep] = 0.0

        # Sort by episode in case it's not already sorted
        sort_idx = np.argsort(episodes)
        episodes = episodes[sort_idx]
        winrates = winrates[sort_idx]

        # Clip winrates to [0, 1]
        winrates = np.clip(winrates, 0.0, 1.0)

        # 1. AUC (normalized by range so it represents average winrate)
        auc = _compute_auc(episodes, winrates)

        # 2. Plateau fraction
        plateau_frac = _estimate_plateau_fraction(episodes, winrates)

        # 3. Late-stage sensitivity
        mid = len(winrates) // 2
        if mid > 0:
            first_half_mean = float(np.mean(winrates[:mid]))
            second_half_mean = float(np.mean(winrates[mid:]))
            # Positive late sensitivity => still improving
            late_sensitivity = max(0.0, second_half_mean - first_half_mean)
            # Scale: 0.5 improvement across halves => perfect score
            late_sensitivity = min(late_sensitivity / 0.5, 1.0)
        else:
            late_sensitivity = 0.0

        # Composite depth
        depth = (auc + plateau_frac + late_sensitivity) / 3.0
        return float(np.clip(depth, 0.0, 1.0))

    def non_triviality(
        self,
        trained_vs_random_winrate: float,
        p1_winrate: float,
    ) -> float:
        """Non-triviality score.

        Two factors:

        * **Balance** -- how close the first-player winrate is to 50%.
          A perfectly balanced game gets 1.0; a completely one-sided game
          gets 0.0.

          .. math:: \\text{balance} = 1 - 2 |p_1\\text{winrate} - 0.5|

        * **Competence** -- a trained agent should soundly beat a random
          agent.  If the trained winrate is below 0.55 a penalty is applied,
          because it suggests the game cannot be learned.

        The final score is ``balance * competence``, clipped to [0, 1].

        Parameters
        ----------
        trained_vs_random_winrate : float
            Winrate of a trained agent vs. a random baseline, in [0, 1].
        p1_winrate : float
            Winrate of player 1 when two equally trained agents play,
            in [0, 1].
        """
        # Sanitize inputs
        if not math.isfinite(trained_vs_random_winrate):
            trained_vs_random_winrate = 0.0
        if not math.isfinite(p1_winrate):
            p1_winrate = 0.5

        trained_vs_random_winrate = float(np.clip(trained_vs_random_winrate, 0.0, 1.0))
        p1_winrate = float(np.clip(p1_winrate, 0.0, 1.0))

        # Balance factor: 1.0 when exactly 50/50, 0.0 when 100/0 or 0/100
        balance_factor = 1.0 - 2.0 * abs(p1_winrate - 0.5)

        # Competence factor: smooth sigmoid ramp from 0.5 (coin-flip)
        # Any improvement over random gets partial credit; higher is better.
        # Maps [0.5, 1.0] -> [0.0, 1.0] with a smooth curve.
        edge = max(0.0, trained_vs_random_winrate - 0.5) * 2.0  # 0..1
        competence_factor = edge ** 0.5  # concave ramp: small edges get credit

        score = balance_factor * competence_factor
        return float(np.clip(score, 0.0, 1.0))

    def seat_balance(
        self,
        trained_p0_winrate: float,
        heuristic_p0_winrate: float,
        heuristic_decisive_rate: float,
        greedy_p0_winrate: float = 0.5,
        greedy_decisive_rate: float = 0.0,
    ) -> float:
        """Seat-balance score combining training, random, and greedy signals.

        R16: added greedy-vs-greedy as a third signal. R15 human eval showed
        random-vs-random alone misses bias that only appears under skilled
        play (rank-3 Moore: 13/16/1 random, 20/20 P1 greedy).

        Takes the worst (most pessimistic) reading among available signals.
        When a signal's decisive rate is below 0.25 it's ignored as too
        noisy.

        Returns
        -------
        float
            1.0 for a perfectly balanced game, 0.0 for a one-sided game.
        """
        t_dev = abs(float(np.clip(trained_p0_winrate, 0.0, 1.0)) - 0.5)
        devs = [t_dev]

        if math.isfinite(heuristic_decisive_rate) and heuristic_decisive_rate >= 0.25:
            devs.append(abs(float(np.clip(heuristic_p0_winrate, 0.0, 1.0)) - 0.5))

        if math.isfinite(greedy_decisive_rate) and greedy_decisive_rate >= 0.25:
            devs.append(abs(float(np.clip(greedy_p0_winrate, 0.0, 1.0)) - 0.5))

        worst_dev = max(devs)
        balance = 1.0 - 2.0 * worst_dev
        return float(np.clip(balance, 0.0, 1.0))

    def strategic_diversity(self, cross_play_results: list[float]) -> float:
        """Strategic diversity from cross-play between independently trained agents.

        If multiple agents trained from scratch converge on the same strategy,
        their head-to-head winrates will be close to 0.5.  If they develop
        *different* strategies, some matchups will be lopsided -- but the
        variance is a sign of diversity.

        Actually, we want the *mean absolute deviation from 0.5* to be
        **small** -- close to 0.5 everywhere means the agents are evenly
        matched, which can indicate diverse but balanced strategies.  If one
        agent always dominates, the game likely has a single dominant strategy.

        .. math::

            \\text{diversity} = 1 - 2 \\cdot \\overline{|w_i - 0.5|}

        Parameters
        ----------
        cross_play_results : list of float
            Winrates from head-to-head matches between independently trained
            agents.  Each value should be in [0, 1].

        Returns
        -------
        float
            Score in [0, 1] where 1.0 means maximum strategic diversity
            (all matchups perfectly balanced) and 0.0 means a single
            dominant strategy.
        """
        if not cross_play_results:
            return 0.5  # no data; return neutral

        winrates = np.array(cross_play_results, dtype=np.float64)

        # Replace NaN / inf with 0.5 (neutral)
        bad = ~np.isfinite(winrates)
        if np.any(bad):
            winrates[bad] = 0.5

        winrates = np.clip(winrates, 0.0, 1.0)

        mean_dev = float(np.mean(np.abs(winrates - 0.5)))
        diversity = 1.0 - 2.0 * mean_dev
        return float(np.clip(diversity, 0.0, 1.0))

    # ------------------------------------------------------------------
    # Composite score
    # ------------------------------------------------------------------

    def composite_score(
        self,
        simplicity: float,
        depth: float,
        non_triviality: float,
        diversity: float,
    ) -> float:
        """Go Essence composite score.

        The composite score rewards games that combine simple rules with deep,
        non-trivial, diverse strategy.  The formula is:

        .. math::

            \\text{GoEssence} = \\frac{
                \\text{depth}^{w_d} \\cdot \\text{diversity}^{w_{\\text{div}}}
                \\cdot \\text{non\\_triviality}
            }{
                (1 - \\text{simplicity})^{w_s} + \\epsilon
            }

        The raw value is then rescaled into [0, 1] via a sigmoid-style
        normalization.

        Parameters
        ----------
        simplicity, depth, non_triviality, diversity : float
            Individual metric scores, each in [0, 1].

        Returns
        -------
        float
            Composite Go Essence score in [0, 1].
        """
        w_d = self.config.depth_weight
        w_div = self.config.diversity_weight
        w_s = self.config.simplicity_weight
        epsilon = 1e-8

        # Sanitize inputs
        simplicity = float(np.clip(simplicity, 0.0, 1.0))
        depth = float(np.clip(depth, 0.0, 1.0))
        non_triviality = float(np.clip(non_triviality, 0.0, 1.0))
        diversity = float(np.clip(diversity, 0.0, 1.0))

        # Numerator: weighted geometric-additive blend.
        # Non-triviality and diversity boost the score but don't zero it --
        # depth alone still produces signal for evolution to follow.
        # Floors ensure a deep game always ranks above nothing.
        non_triv_factor = 0.1 + 0.9 * non_triviality
        diversity_factor = 0.2 + 0.8 * diversity
        numerator = (depth ** w_d) * (diversity_factor ** w_div) * non_triv_factor

        # Denominator: simplicity penalty -- lower simplicity means higher penalty
        simplicity_penalty = (1.0 - simplicity) ** w_s + epsilon

        raw = numerator / simplicity_penalty

        # Normalize into [0, 1] using a sigmoid-style mapping.
        # raw can theoretically be very large (when simplicity ~ 1).
        # We use: score = 2 * sigmoid(raw) - 1 = (1 - exp(-raw)) / (1 + exp(-raw))
        # which maps [0, inf) -> [0, 1).
        # To keep the mapping responsive in the typical range (raw in [0, 5]),
        # we scale: score = raw / (raw + 1)  (hyperbolic saturation).
        score = raw / (raw + 1.0)

        return float(np.clip(score, 0.0, 1.0))

    # ------------------------------------------------------------------
    # Novelty
    # ------------------------------------------------------------------

    def structural_fingerprint(self, game) -> tuple:
        """Return a structural fingerprint for novelty comparison."""
        topology_type = getattr(game, 'topology_type', 'grid')
        capture_type = game.capture_rule.capture_type if hasattr(game, 'capture_rule') else 'none'
        win_type = game.win_condition.condition_type if hasattr(game, 'win_condition') else 'unknown'
        action_types = tuple(game.action_rule.action_types) if hasattr(game, 'action_rule') else ('place',)
        num_dims = game.num_dimensions if hasattr(game, 'num_dimensions') else 0
        uses_ca = getattr(game, 'uses_ca', False)
        ca_steps = game.ca_rule.steps_per_turn if (uses_ca and game.ca_rule) else 0
        return (topology_type, capture_type, win_type, action_types, num_dims, uses_ca, ca_steps)

    def novelty_score(self, game, population_fingerprints: list[tuple]) -> float:
        """Score how novel this game's structure is vs the population. 1.0=unique, lower=common."""
        fp = self.structural_fingerprint(game)
        if not population_fingerprints:
            return 1.0
        count = sum(1 for f in population_fingerprints if f == fp)
        return 1.0 / (1.0 + count)

    # ------------------------------------------------------------------
    # Full evaluation pipeline
    # ------------------------------------------------------------------

    def evaluate_game(
        self,
        game,
        training_results: dict,
        cross_play_results: list[float] | None = None,
        population_fingerprints: list[tuple] | None = None,
    ) -> dict:
        """Full evaluation pipeline for a single game.

        Parameters
        ----------
        game : GameDef
            The game definition to evaluate.
        training_results : dict
            Must contain:
            - ``'learning_curve'``: list of ``(episode, winrate)`` tuples
            - ``'trained_vs_random_winrate'``: float
            - ``'p1_winrate'``: float
            - ``'training_budget'``: int
            Optional:
            - ``'avg_game_length'``: float (games < 15 moves get score 0)
            - ``'max_turns'``: int (for timeout penalty)
            - ``'per_run_trained_vs_random'``: list[float] (per-run winrates
              vs random, for training stability penalty)
        cross_play_results : list of float, optional
            Winrates from head-to-head between independently trained agents.
            Defaults to ``[0.5]`` (neutral) if not provided.

        Returns
        -------
        dict
            Dictionary with all individual scores and the composite
            ``'go_essence'`` score.
        """
        simplicity = self.rule_simplicity(game)
        depth = self.strategic_depth(
            training_results["learning_curve"],
            training_results["training_budget"],
        )
        non_triv = self.non_triviality(
            training_results["trained_vs_random_winrate"],
            training_results["p1_winrate"],
        )
        diversity = self.strategic_diversity(cross_play_results or [0.5])

        # R15 seat balance, R16 extended to include greedy probe.
        trained_p0 = training_results.get("p0_winrate", training_results.get("p1_winrate", 0.5))
        heur_p0 = training_results.get("heuristic_p1_winrate", 0.5)
        heur_dec = training_results.get("heuristic_decisive_rate", 0.0)
        greedy_p0 = training_results.get("greedy_p1_winrate", 0.5)
        greedy_dec = training_results.get("greedy_decisive_rate", 0.0)
        seat_bal = self.seat_balance(trained_p0, heur_p0, heur_dec, greedy_p0, greedy_dec)

        composite = self.composite_score(simplicity, depth, non_triv, diversity)

        # --- Minimum game length penalty ---
        # Games that end very quickly are likely degenerate.  Apply a
        # smooth ramp: full score at >= 15 moves, linearly down to 20%
        # at 0 moves.  This preserves some signal for evolution even on
        # short games (hard zero gave evolution nothing to differentiate).
        avg_game_length = training_results.get("avg_game_length")
        if avg_game_length is not None and avg_game_length < 15:
            length_factor = 0.2 + 0.8 * (avg_game_length / 15.0)
            composite *= max(0.2, length_factor)

        # --- Seat balance penalty (R15: uses combined trained+heuristic signal) ---
        # Replaces the previous training-only balance penalty. Trained-vs-
        # trained balance can be spoofed by mixed-strategy equilibria; the
        # heuristic (random-vs-random seat-swapped) probe exposes structural
        # first-mover bias that trained agents can't cancel out. seat_bal
        # takes the worse of the two signals. Smooth ramp with 0.2 floor so
        # evolution still has differentiating signal on marginal cases.
        if seat_bal < 0.8:  # equivalent to |worst_dev| > 0.1
            composite *= max(0.2, seat_bal)

        # --- Training stability penalty ---
        # If the game has multiple training runs, check consistency.
        # When min(trained_vs_random) < 0.2 * max(trained_vs_random),
        # at least one run collapsed — penalize with a smooth ramp.
        # Ratio 0.0 (complete collapse) -> 0.2 floor; ratio >= 0.2 -> 1.0.
        per_run_wr = training_results.get("per_run_trained_vs_random")
        if per_run_wr and len(per_run_wr) >= 2:
            min_wr = min(per_run_wr)
            max_wr = max(per_run_wr)
            if max_wr > 0.0:
                stability_ratio = min_wr / max_wr
                if stability_ratio < 0.2:
                    # Smooth ramp: ratio 0 -> 0.2 floor, ratio 0.2 -> 1.0
                    stability_factor = 0.2 + 0.8 * (stability_ratio / 0.2)
                    composite *= max(0.2, stability_factor)

        # --- "Ends before timeout" penalty ---
        # If avg_game_length > 0.9 * max_turns, the game likely never
        # reaches its win condition and just times out.  Smooth ramp from
        # 1.0 at 90% of max_turns down to 0.2 at 100% of max_turns.
        max_turns = training_results.get("max_turns")
        if avg_game_length is not None and max_turns is not None and max_turns > 0:
            timeout_ratio = avg_game_length / max_turns
            if timeout_ratio > 0.9:
                # Ramp: 0.9 -> 1.0, 1.0 -> 0.2
                timeout_factor = 1.0 - 0.8 * ((timeout_ratio - 0.9) / 0.1)
                composite *= max(0.2, timeout_factor)

        # --- Novelty bonus ---
        # If population fingerprints are provided, reward structural novelty
        # with up to a 10% bonus to encourage exploration.
        result = {
            "rule_simplicity": simplicity,
            "strategic_depth": depth,
            "non_triviality": non_triv,
            "strategic_diversity": diversity,
            "seat_balance": seat_bal,
        }
        if population_fingerprints is not None:
            nov = self.novelty_score(game, population_fingerprints)
            composite *= (1.0 + 0.1 * nov)
            composite = min(composite, 1.0)
            result["novelty"] = nov

        result["go_essence"] = composite
        return result
