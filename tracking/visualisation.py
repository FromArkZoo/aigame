"""Matplotlib plotting utilities for analysing Genesis Creativity Engine results."""

import matplotlib
matplotlib.use("Agg")  # headless — no GUI required
import matplotlib.pyplot as plt
import numpy as np
import os
import json
from typing import List, Optional

from config import TrackingConfig


class GenesisVisualiser:
    """Generate analysis plots for the Genesis engine."""

    def __init__(self, config: TrackingConfig, db: "GenesisDB"):
        self.config = config
        self.db = db
        os.makedirs(config.plot_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _save(self, fig, filename: str):
        """Save a figure to the configured plot directory and close it."""
        path = os.path.join(self.config.plot_dir, filename)
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return path

    # ------------------------------------------------------------------
    # Plots
    # ------------------------------------------------------------------

    def plot_go_essence_over_generations(self) -> Optional[str]:
        """Plot best, mean, median Go Essence score across generations.

        Saved to ``<plot_dir>/go_essence_generations.png``.
        Returns the path to the saved image or ``None`` if no data.
        """
        stats = self.db.get_generation_stats()
        if not stats:
            return None

        generations = [s["generation"] for s in stats]
        best = [s["best_go_essence"] for s in stats]
        mean = [s["mean_go_essence"] for s in stats]
        median = [s["median_go_essence"] for s in stats]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(generations, best, "o-", label="Best", linewidth=2)
        ax.plot(generations, mean, "s--", label="Mean", linewidth=1.5)
        ax.plot(generations, median, "^:", label="Median", linewidth=1.5)

        # Shade standard deviation band around the mean
        stds = [s["std_go_essence"] for s in stats]
        mean_arr = np.array(mean)
        std_arr = np.array(stds)
        ax.fill_between(
            generations,
            mean_arr - std_arr,
            mean_arr + std_arr,
            alpha=0.15,
            label="Mean +/- 1 std",
        )

        ax.set_xlabel("Generation")
        ax.set_ylabel("Go Essence Score")
        ax.set_title("Go Essence Score Over Generations")
        ax.legend()
        ax.grid(True, alpha=0.3)
        return self._save(fig, "go_essence_generations.png")

    def plot_top_games_learning_curves(self, n: int = 5) -> Optional[str]:
        """Plot learning curves of the top *n* games overlaid.

        Saved to ``<plot_dir>/top_learning_curves.png``.
        """
        top_games = self.db.get_top_games(n)
        if not top_games:
            return None

        fig, ax = plt.subplots(figsize=(10, 6))
        has_data = False

        for game in top_games:
            game_id = game["game_id"]
            runs = self.db.get_learning_curves(game_id)
            if not runs:
                continue
            # Average the learning curves across independent runs
            all_curves = [r["learning_curve"] for r in runs if r.get("learning_curve")]
            if not all_curves:
                continue

            # Find the shortest curve length to align them
            min_len = min(len(c) for c in all_curves)
            if min_len == 0:
                continue

            episodes = [pt[0] for pt in all_curves[0][:min_len]]
            winrates_stack = np.array(
                [[pt[1] for pt in curve[:min_len]] for curve in all_curves]
            )
            mean_wr = winrates_stack.mean(axis=0)
            label = f"{game_id[:12]}... (GE={game.get('go_essence', 0):.3f})"
            ax.plot(episodes, mean_wr, linewidth=1.5, label=label)
            has_data = True

        if not has_data:
            plt.close(fig)
            return None

        ax.set_xlabel("Training Episode")
        ax.set_ylabel("Win Rate")
        ax.set_title(f"Learning Curves — Top {n} Games")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        return self._save(fig, "top_learning_curves.png")

    def plot_metric_distributions(self, generation: int = -1) -> Optional[str]:
        """Plot histograms of each metric for a given generation.

        If *generation* is ``-1`` (default), the latest generation is used.
        Saved to ``<plot_dir>/metric_distributions.png``.
        """
        # Determine which generation to use
        gen_stats = self.db.get_generation_stats()
        if not gen_stats:
            return None

        if generation == -1:
            target_gen = gen_stats[-1]["generation"]
        else:
            target_gen = generation

        # Fetch all games in that generation with their scores
        rows = self.db.conn.execute(
            '''SELECT s.rule_simplicity, s.strategic_depth,
                      s.non_triviality, s.strategic_diversity, s.go_essence
               FROM games g
               JOIN scores s ON g.game_id = s.game_id
               WHERE g.generation = ?''',
            (target_gen,),
        ).fetchall()

        if not rows:
            return None

        metrics = {
            "Rule Simplicity": [r["rule_simplicity"] for r in rows],
            "Strategic Depth": [r["strategic_depth"] for r in rows],
            "Non-Triviality": [r["non_triviality"] for r in rows],
            "Strategic Diversity": [r["strategic_diversity"] for r in rows],
            "Go Essence": [r["go_essence"] for r in rows],
        }

        fig, axes = plt.subplots(2, 3, figsize=(14, 8))
        axes = axes.flatten()

        for idx, (name, values) in enumerate(metrics.items()):
            ax = axes[idx]
            vals = np.array(values)
            bins = max(5, min(30, len(vals) // 2))
            ax.hist(vals, bins=bins, edgecolor="black", alpha=0.7)
            ax.set_title(name)
            ax.set_xlabel("Score")
            ax.set_ylabel("Count")
            if len(vals) > 0:
                ax.axvline(vals.mean(), color="red", linestyle="--",
                           label=f"Mean={vals.mean():.3f}")
                ax.legend(fontsize=7)

        # Hide unused subplot(s)
        for idx in range(len(metrics), len(axes)):
            axes[idx].set_visible(False)

        fig.suptitle(f"Metric Distributions — Generation {target_gen}", fontsize=14)
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        return self._save(fig, "metric_distributions.png")

    def plot_elo_distribution(self) -> Optional[str]:
        """Plot ELO rating distribution of current game pool.

        Saved to ``<plot_dir>/elo_distribution.png``.
        """
        rows = self.db.conn.execute(
            "SELECT elo FROM scores WHERE elo IS NOT NULL"
        ).fetchall()
        if not rows:
            return None

        elos = np.array([r["elo"] for r in rows])
        fig, ax = plt.subplots(figsize=(10, 6))
        bins = max(5, min(50, len(elos) // 3))
        ax.hist(elos, bins=bins, edgecolor="black", alpha=0.7, color="steelblue")
        ax.axvline(elos.mean(), color="red", linestyle="--",
                   label=f"Mean={elos.mean():.1f}")
        ax.axvline(np.median(elos), color="green", linestyle=":",
                   label=f"Median={np.median(elos):.1f}")
        ax.set_xlabel("ELO Rating")
        ax.set_ylabel("Count")
        ax.set_title("ELO Rating Distribution")
        ax.legend()
        ax.grid(True, alpha=0.3)
        return self._save(fig, "elo_distribution.png")

    def plot_lineage_tree(self, game_id: str) -> Optional[str]:
        """Plot evolutionary lineage of a game as a simple tree diagram.

        Saved to ``<plot_dir>/lineage_<game_id>.png``.
        """
        lineage = self.db.get_lineage(game_id)
        if not lineage:
            return None

        # Build adjacency: child -> parents
        id_to_game = {g["game_id"]: g for g in lineage}
        edges = []
        for game in lineage:
            parents = game.get("parent_ids")
            if isinstance(parents, list):
                for pid in parents:
                    if pid in id_to_game:
                        edges.append((pid, game["game_id"]))

        # Assign y-positions by generation, x-positions within generation
        gen_groups: dict = {}
        for g in lineage:
            gen = g.get("generation", 0)
            gen_groups.setdefault(gen, []).append(g["game_id"])

        positions = {}
        for gen in sorted(gen_groups.keys()):
            ids = gen_groups[gen]
            for i, gid in enumerate(ids):
                positions[gid] = (i - (len(ids) - 1) / 2.0, -gen)

        fig, ax = plt.subplots(figsize=(max(8, len(lineage) * 1.2), max(6, len(gen_groups) * 2)))

        # Draw edges
        for parent_id, child_id in edges:
            px, py = positions.get(parent_id, (0, 0))
            cx, cy = positions.get(child_id, (0, 0))
            ax.annotate(
                "",
                xy=(cx, cy),
                xytext=(px, py),
                arrowprops=dict(arrowstyle="->", color="gray", lw=1.2),
            )

        # Draw nodes
        for gid, (x, y) in positions.items():
            game = id_to_game.get(gid, {})
            go_ess = game.get("go_essence")
            label = gid[:8]
            if go_ess is not None:
                label += f"\n{go_ess:.3f}"
            color = "gold" if gid == game_id else "lightblue"
            ax.plot(x, y, "o", markersize=20, color=color, markeredgecolor="black")
            ax.text(x, y, label, ha="center", va="center", fontsize=6)

        ax.set_title(f"Lineage of {game_id[:16]}...")
        ax.set_ylabel("Generation (deeper = older)")
        ax.set_xticks([])
        ax.grid(False)

        # Sanitise game_id for filename
        safe_id = "".join(c if c.isalnum() or c in "_-" else "_" for c in game_id)
        return self._save(fig, f"lineage_{safe_id}.png")

    def plot_score_correlations(self) -> Optional[str]:
        """Scatter matrix of metric scores (simplicity vs depth, etc).

        Saved to ``<plot_dir>/score_correlations.png``.
        """
        rows = self.db.conn.execute(
            '''SELECT rule_simplicity, strategic_depth,
                      non_triviality, strategic_diversity, go_essence
               FROM scores'''
        ).fetchall()
        if not rows:
            return None

        names = [
            "Rule Simplicity",
            "Strategic Depth",
            "Non-Triviality",
            "Strategic Diversity",
            "Go Essence",
        ]
        keys = [
            "rule_simplicity",
            "strategic_depth",
            "non_triviality",
            "strategic_diversity",
            "go_essence",
        ]
        data = {k: np.array([r[k] for r in rows]) for k in keys}

        n_metrics = len(keys)
        fig, axes = plt.subplots(n_metrics, n_metrics, figsize=(14, 14))

        for i in range(n_metrics):
            for j in range(n_metrics):
                ax = axes[i][j]
                xi = data[keys[j]]
                yi = data[keys[i]]
                if i == j:
                    # Diagonal: histogram
                    bins = max(5, min(30, len(xi) // 3))
                    ax.hist(xi, bins=bins, alpha=0.7, edgecolor="black")
                else:
                    ax.scatter(xi, yi, s=8, alpha=0.5)
                    # Compute correlation
                    if len(xi) > 1 and np.std(xi) > 0 and np.std(yi) > 0:
                        corr = np.corrcoef(xi, yi)[0, 1]
                        ax.set_title(f"r={corr:.2f}", fontsize=7)

                if i == n_metrics - 1:
                    ax.set_xlabel(names[j], fontsize=7)
                else:
                    ax.set_xticklabels([])
                if j == 0:
                    ax.set_ylabel(names[i], fontsize=7)
                else:
                    ax.set_yticklabels([])
                ax.tick_params(labelsize=5)

        fig.suptitle("Score Correlations", fontsize=14)
        fig.tight_layout(rect=[0, 0, 1, 0.97])
        return self._save(fig, "score_correlations.png")

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def generate_all_plots(self) -> dict:
        """Generate all standard analysis plots.

        Returns a dict mapping plot name to saved file path (or ``None``
        if there was insufficient data for a particular plot).
        """
        results = {
            "go_essence_generations": self.plot_go_essence_over_generations(),
            "top_learning_curves": self.plot_top_games_learning_curves(),
            "metric_distributions": self.plot_metric_distributions(),
            "elo_distribution": self.plot_elo_distribution(),
            "score_correlations": self.plot_score_correlations(),
        }
        return results
