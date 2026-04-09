"""Text summary report generation for the Genesis Creativity Engine."""

from typing import Optional


class GenesisReporter:
    """Generate text summary reports."""

    def __init__(self, db: "GenesisDB"):
        self.db = db

    # ------------------------------------------------------------------
    # Full summary
    # ------------------------------------------------------------------

    def summary_report(self) -> str:
        """Generate a full text summary report.

        Includes:
        - Overall statistics (total games, generations, best score)
        - Top 10 games with scores
        - Generation-over-generation improvement
        - Metric statistics
        """
        lines = []
        lines.append("=" * 70)
        lines.append("  GENESIS CREATIVITY ENGINE — SUMMARY REPORT")
        lines.append("=" * 70)
        lines.append("")

        # -- Overall statistics ----------------------------------------
        total_games = self.db.game_count()
        total_generations = self.db.generation_count()

        top_games = self.db.get_top_games(1)
        best_score = top_games[0]["go_essence"] if top_games else None
        best_game_id = top_games[0]["game_id"] if top_games else "N/A"

        lines.append("OVERALL STATISTICS")
        lines.append("-" * 40)
        lines.append(f"  Total games tracked   : {total_games}")
        lines.append(f"  Total generations     : {total_generations}")
        if best_score is not None:
            lines.append(f"  Best Go Essence score : {best_score:.4f}")
            lines.append(f"  Best game ID          : {best_game_id}")
        else:
            lines.append("  Best Go Essence score : N/A (no games recorded)")
        lines.append("")

        # -- Top 10 games ----------------------------------------------
        top10 = self.db.get_top_games(10)
        if top10:
            lines.append("TOP 10 GAMES BY GO ESSENCE")
            lines.append("-" * 40)
            header = (
                f"  {'Rank':<5} {'Game ID':<20} {'GoEss':>7} {'Depth':>7} "
                f"{'Simpl':>7} {'Diver':>7} {'NonTr':>7} {'ELO':>8}"
            )
            lines.append(header)
            for rank, game in enumerate(top10, 1):
                gid = game["game_id"][:18]
                go_ess = game.get("go_essence") or 0.0
                depth = game.get("strategic_depth") or 0.0
                simpl = game.get("rule_simplicity") or 0.0
                diver = game.get("strategic_diversity") or 0.0
                nontr = game.get("non_triviality") or 0.0
                elo = game.get("elo") or 1500.0
                lines.append(
                    f"  {rank:<5} {gid:<20} {go_ess:>7.4f} {depth:>7.4f} "
                    f"{simpl:>7.4f} {diver:>7.4f} {nontr:>7.4f} {elo:>8.1f}"
                )
            lines.append("")

        # -- Generation-over-generation improvement --------------------
        gen_stats = self.db.get_generation_stats()
        if gen_stats:
            lines.append("GENERATION-OVER-GENERATION PROGRESS")
            lines.append("-" * 40)
            header = (
                f"  {'Gen':<5} {'Pop':>5} {'Best':>8} {'Mean':>8} "
                f"{'Median':>8} {'Std':>8}"
            )
            lines.append(header)
            for gs in gen_stats:
                gen = gs["generation"]
                pop = gs.get("population_size", 0)
                best = gs.get("best_go_essence", 0.0) or 0.0
                mean = gs.get("mean_go_essence", 0.0) or 0.0
                median = gs.get("median_go_essence", 0.0) or 0.0
                std = gs.get("std_go_essence", 0.0) or 0.0
                lines.append(
                    f"  {gen:<5} {pop:>5} {best:>8.4f} {mean:>8.4f} "
                    f"{median:>8.4f} {std:>8.4f}"
                )

            # Improvement summary
            if len(gen_stats) >= 2:
                first_best = gen_stats[0].get("best_go_essence", 0.0) or 0.0
                last_best = gen_stats[-1].get("best_go_essence", 0.0) or 0.0
                improvement = last_best - first_best
                lines.append("")
                lines.append(
                    f"  Improvement (best) from gen {gen_stats[0]['generation']} "
                    f"to gen {gen_stats[-1]['generation']}: "
                    f"{improvement:+.4f}"
                )
            lines.append("")

        # -- Metric statistics across all games ------------------------
        rows = self.db.conn.execute(
            '''SELECT
                 AVG(rule_simplicity)      AS avg_simp,
                 AVG(strategic_depth)      AS avg_depth,
                 AVG(non_triviality)       AS avg_nontr,
                 AVG(strategic_diversity)  AS avg_diver,
                 AVG(go_essence)           AS avg_go,
                 MIN(go_essence)           AS min_go,
                 MAX(go_essence)           AS max_go,
                 AVG(elo)                  AS avg_elo
               FROM scores'''
        ).fetchone()

        if rows and rows["avg_go"] is not None:
            lines.append("AGGREGATE METRIC STATISTICS (ALL GAMES)")
            lines.append("-" * 40)
            lines.append(f"  Avg Rule Simplicity     : {rows['avg_simp']:.4f}")
            lines.append(f"  Avg Strategic Depth     : {rows['avg_depth']:.4f}")
            lines.append(f"  Avg Non-Triviality      : {rows['avg_nontr']:.4f}")
            lines.append(f"  Avg Strategic Diversity  : {rows['avg_diver']:.4f}")
            lines.append(f"  Avg Go Essence          : {rows['avg_go']:.4f}")
            lines.append(f"  Min Go Essence          : {rows['min_go']:.4f}")
            lines.append(f"  Max Go Essence          : {rows['max_go']:.4f}")
            lines.append(f"  Avg ELO                 : {rows['avg_elo']:.1f}")
            lines.append("")

        lines.append("=" * 70)
        lines.append("  END OF REPORT")
        lines.append("=" * 70)
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Single game report
    # ------------------------------------------------------------------

    def game_report(self, game_id: str) -> str:
        """Detailed report for a single game.

        Includes:
        - Rule representation summary (complexity, dimensions)
        - All metric scores
        - Training curve summary
        - Lineage / ancestry
        """
        game = self.db.get_game(game_id)
        if game is None:
            return f"Game '{game_id}' not found in the database."

        lines = []
        lines.append("=" * 70)
        lines.append(f"  GAME REPORT — {game_id}")
        lines.append("=" * 70)
        lines.append("")

        # -- Basic info ------------------------------------------------
        lines.append("GAME PROPERTIES")
        lines.append("-" * 40)
        lines.append(f"  Game ID          : {game['game_id']}")
        lines.append(f"  Generation       : {game.get('generation', 'N/A')}")
        parents = game.get("parent_ids")
        if parents:
            lines.append(f"  Parent IDs       : {', '.join(str(p) for p in parents)}")
        else:
            lines.append("  Parent IDs       : None (seed game)")
        lines.append(f"  State dimension  : {game.get('state_dim', 'N/A')}")
        lines.append(f"  Num actions      : {game.get('num_actions', 'N/A')}")
        lines.append(f"  Num players      : {game.get('num_players', 'N/A')}")
        lines.append(f"  Observation type : {game.get('observation_type', 'N/A')}")
        lines.append(f"  Rule complexity  : {game.get('rule_complexity', 'N/A')}")
        lines.append(f"  Created at       : {game.get('created_at', 'N/A')}")
        lines.append("")

        # -- Scores ----------------------------------------------------
        lines.append("METRIC SCORES")
        lines.append("-" * 40)
        score_fields = [
            ("Rule Simplicity", "rule_simplicity"),
            ("Strategic Depth", "strategic_depth"),
            ("Non-Triviality", "non_triviality"),
            ("Strategic Diversity", "strategic_diversity"),
            ("Go Essence", "go_essence"),
            ("ELO Rating", "elo"),
        ]
        for label, key in score_fields:
            val = game.get(key)
            if val is not None:
                if key == "elo":
                    lines.append(f"  {label:<24}: {val:.1f}")
                else:
                    lines.append(f"  {label:<24}: {val:.4f}")
            else:
                lines.append(f"  {label:<24}: N/A")
        lines.append("")

        # -- Training curves -------------------------------------------
        runs = self.db.get_learning_curves(game_id)
        lines.append("TRAINING RUNS")
        lines.append("-" * 40)
        if not runs:
            lines.append("  No training runs recorded.")
        else:
            lines.append(f"  Number of runs: {len(runs)}")
            for run in runs:
                lines.append(f"  --- Run (seed={run.get('run_seed', '?')}) ---")
                lines.append(f"    Final win rate       : {run.get('final_winrate', 'N/A')}")
                lines.append(f"    Trained vs random    : {run.get('trained_vs_random', 'N/A')}")
                lines.append(f"    Avg game length      : {run.get('avg_game_length', 'N/A')}")
                lines.append(f"    Training steps       : {run.get('training_steps', 'N/A')}")
                curve = run.get("learning_curve")
                if curve and len(curve) > 0:
                    first_wr = curve[0][1] if len(curve[0]) > 1 else "?"
                    last_wr = curve[-1][1] if len(curve[-1]) > 1 else "?"
                    lines.append(
                        f"    Learning curve       : {len(curve)} checkpoints, "
                        f"start={first_wr}, end={last_wr}"
                    )
        lines.append("")

        # -- Lineage ---------------------------------------------------
        lineage = self.db.get_lineage(game_id)
        lines.append("LINEAGE / ANCESTRY")
        lines.append("-" * 40)
        if len(lineage) <= 1:
            lines.append("  No ancestors found (root / seed game).")
        else:
            for ancestor in lineage:
                aid = ancestor["game_id"]
                gen = ancestor.get("generation", "?")
                go_ess = ancestor.get("go_essence")
                go_str = f"{go_ess:.4f}" if go_ess is not None else "N/A"
                marker = " <-- THIS GAME" if aid == game_id else ""
                lines.append(
                    f"  Gen {gen}: {aid[:24]:<24} GoEssence={go_str}{marker}"
                )
        lines.append("")

        # -- Rule representation summary -------------------------------
        rule_rep = game.get("rule_representation")
        if rule_rep:
            lines.append("RULE REPRESENTATION (SUMMARY)")
            lines.append("-" * 40)
            if isinstance(rule_rep, dict):
                for k, v in rule_rep.items():
                    v_str = str(v)
                    if len(v_str) > 80:
                        v_str = v_str[:77] + "..."
                    lines.append(f"  {k}: {v_str}")
            else:
                rep_str = str(rule_rep)
                if len(rep_str) > 200:
                    rep_str = rep_str[:197] + "..."
                lines.append(f"  {rep_str}")
            lines.append("")

        lines.append("=" * 70)
        lines.append("  END OF GAME REPORT")
        lines.append("=" * 70)
        return "\n".join(lines)
