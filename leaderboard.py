#!/usr/bin/env python3
"""Show the current leaderboard of top games.

Usage:
    python leaderboard.py [--top 20] [--db-path genesis_results.db]
"""

import argparse
import sys

from config import GenesisConfig
from tracking.database import GenesisDB


def main():
    p = argparse.ArgumentParser(description="Genesis engine leaderboard")
    p.add_argument("--top", type=int, default=20,
                   help="Number of top games to show (default: 20)")
    p.add_argument("--db-path", type=str, default=None,
                   help="Path to SQLite database")
    args = p.parse_args()

    config = GenesisConfig()
    if args.db_path:
        config.tracking.db_path = args.db_path

    db = GenesisDB(config.tracking)

    if db.game_count() == 0:
        print("No data found. Run the engine first:")
        print("  python run.py --generations 5 --population 20 --training-budget 1000")
        db.close()
        sys.exit(1)

    top_games = db.get_top_games(args.top)

    print(f"\n{'='*80}")
    print(f"  GENESIS CREATIVITY ENGINE — TOP {min(args.top, len(top_games))} GAMES")
    print(f"{'='*80}\n")

    header = (
        f"{'Rank':<6}{'Game ID':<15}{'Go Essence':<13}{'Depth':<9}"
        f"{'Diversity':<11}{'Simplicity':<12}{'Non-Triv':<10}"
        f"{'ELO':<9}{'Gen':<5}{'Dim':<5}{'Acts':<5}"
    )
    print(header)
    print("-" * len(header))

    for i, g in enumerate(top_games):
        print(
            f"{i+1:<6}"
            f"{g.get('game_id', '?'):<15}"
            f"{g.get('go_essence', 0):<13.4f}"
            f"{g.get('strategic_depth', 0):<9.3f}"
            f"{g.get('strategic_diversity', 0):<11.3f}"
            f"{g.get('rule_simplicity', 0):<12.3f}"
            f"{g.get('non_triviality', 0):<10.3f}"
            f"{g.get('elo', 1500):<9.1f}"
            f"{g.get('generation', '?'):<5}"
            f"{g.get('state_dim', '?'):<5}"
            f"{g.get('num_actions', '?'):<5}"
        )

    print(f"\nTotal games in database: {db.game_count()}")
    print(f"Total generations: {db.generation_count()}")

    # Generation improvement summary
    gen_stats = db.get_generation_stats()
    if gen_stats:
        print(f"\n{'Gen':<6}{'Best':<12}{'Mean':<12}{'Median':<12}{'Std':<10}")
        print("-" * 52)
        for gs in gen_stats:
            print(
                f"{gs['generation']:<6}"
                f"{gs.get('best_go_essence', 0):<12.4f}"
                f"{gs.get('mean_go_essence', 0):<12.4f}"
                f"{gs.get('median_go_essence', 0):<12.4f}"
                f"{gs.get('std_go_essence', 0):<10.4f}"
            )

    db.close()


if __name__ == "__main__":
    main()
