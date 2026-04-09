#!/usr/bin/env python3
"""Inspect a specific game in detail.

Usage:
    python inspect_game.py --game-id abc123def456
    python inspect_game.py --game-id abc123def456 --show-rules
    python inspect_game.py --game-id abc123def456 --show-lineage
"""

import argparse
import json
import sys

from config import GenesisConfig
from tracking.database import GenesisDB
from tracking.reporter import GenesisReporter
from tracking.visualisation import GenesisVisualiser


def main():
    p = argparse.ArgumentParser(description="Inspect a Genesis game")
    p.add_argument("--game-id", type=str, required=True,
                   help="Game ID to inspect")
    p.add_argument("--db-path", type=str, default=None,
                   help="Path to SQLite database")
    p.add_argument("--show-rules", action="store_true",
                   help="Show full rule representation (JSON)")
    p.add_argument("--show-lineage", action="store_true",
                   help="Show evolutionary lineage")
    p.add_argument("--plot-lineage", action="store_true",
                   help="Generate lineage tree plot")
    args = p.parse_args()

    config = GenesisConfig()
    if args.db_path:
        config.tracking.db_path = args.db_path

    db = GenesisDB(config.tracking)

    game_data = db.get_game(args.game_id)
    if game_data is None:
        print(f"Game '{args.game_id}' not found in database.")
        db.close()
        sys.exit(1)

    # Detailed report
    reporter = GenesisReporter(db)
    report = reporter.game_report(args.game_id)
    print(report)

    # V3 fields (topology_type, action_rule)
    rule_rep = game_data.get("rule_representation")
    if isinstance(rule_rep, dict):
        topology_type = rule_rep.get("topology_type", "grid")
        action_rule = rule_rep.get("action_rule", {})
        action_types = ", ".join(action_rule.get("action_types", ["place"]))
        print(f"\nV3 FIELDS")
        print("-" * 40)
        print(f"  Topology: {topology_type}")
        print(f"  Action types: {action_types}")
        if "move" in action_rule.get("action_types", []):
            print(f"  Move constraint: {action_rule.get('move_constraint', 'adjacent_empty')}")

        # V4 CA fields
        ca_rule = rule_rep.get("ca_rule")
        if ca_rule:
            table = ca_rule.get("transition_table", {})
            steps = ca_rule.get("steps_per_turn", 1)
            max_nbrs = ca_rule.get("max_neighbors", 4)
            birth = sum(1 for k, v in table.items() if k.startswith("0,") and v != 0)
            death = sum(1 for k, v in table.items() if k.startswith("1,") and v == 0)
            convert = sum(1 for k, v in table.items()
                         if not k.startswith("0,") and v != 0
                         and int(k.split(",")[0]) != v)
            print(f"\n  CELLULAR AUTOMATON: Yes")
            print(f"  Steps per turn: {steps}")
            print(f"  Max neighbors: {max_nbrs}")
            print(f"  CA: {birth} birth, {death} death, {convert} conversion rules")
        else:
            print(f"\n  Cellular Automaton: No (classic)")
        print()

    # Full rule representation
    if args.show_rules:
        print("\n" + "=" * 60)
        print("FULL RULE REPRESENTATION")
        print("=" * 60)
        rules = game_data.get("rule_representation")
        if rules:
            print(json.dumps(rules, indent=2, default=str))
        else:
            print("No rule representation stored.")

    # Lineage
    if args.show_lineage:
        print("\n" + "=" * 60)
        print("EVOLUTIONARY LINEAGE")
        print("=" * 60)
        lineage = db.get_lineage(args.game_id)
        for i, ancestor in enumerate(lineage):
            prefix = "-> " if i > 0 else "** "
            go_ess = ancestor.get("go_essence", "N/A")
            gen = ancestor.get("generation", "?")
            parents = ancestor.get("parent_ids", [])
            score_str = f"{go_ess:.4f}" if isinstance(go_ess, float) else str(go_ess)
            print(
                f"  {prefix}{ancestor['game_id']} "
                f"(gen={gen}, go_essence={score_str}, "
                f"parents={parents})"
            )

    # Lineage plot
    if args.plot_lineage:
        vis = GenesisVisualiser(config.tracking, db)
        vis.plot_lineage_tree(args.game_id)
        print(f"\nLineage plot saved to {config.tracking.plot_dir}/")

    # Learning curves
    curves = db.get_learning_curves(args.game_id)
    if curves:
        print(f"\n{'='*60}")
        print(f"TRAINING RUNS ({len(curves)} runs)")
        print(f"{'='*60}")
        for run in curves:
            seed = run.get("run_seed", "?")
            final_wr = run.get("final_winrate", "?")
            vs_random = run.get("trained_vs_random", "?")
            avg_len = run.get("avg_game_length", "?")
            steps = run.get("training_steps", "?")
            curve = run.get("learning_curve", [])

            final_str = f"{final_wr:.3f}" if isinstance(final_wr, float) else str(final_wr)
            rand_str = f"{vs_random:.3f}" if isinstance(vs_random, float) else str(vs_random)
            len_str = f"{avg_len:.1f}" if isinstance(avg_len, float) else str(avg_len)

            print(f"\n  Run seed={seed}:")
            print(f"    Final winrate (p0 vs p1): {final_str}")
            print(f"    Trained vs random:        {rand_str}")
            print(f"    Avg game length:          {len_str}")
            print(f"    Training steps:           {steps}")
            if curve:
                print(f"    Learning curve ({len(curve)} points):")
                for point in curve[:5]:
                    ep, wr = point[0], point[1]
                    print(f"      Episode {ep:>6}: winrate={wr:.3f}")
                if len(curve) > 5:
                    print(f"      ... ({len(curve) - 5} more points)")

    db.close()


if __name__ == "__main__":
    main()
