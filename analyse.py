#!/usr/bin/env python3
"""Generate a summary report and plots from Genesis engine results.

Usage:
    python analyse.py [--db-path genesis_results.db] [--plot-dir plots]
"""

import argparse
import sys

from config import GenesisConfig
from tracking.database import GenesisDB
from tracking.visualisation import GenesisVisualiser
from tracking.reporter import GenesisReporter


def main():
    p = argparse.ArgumentParser(description="Analyse Genesis engine results")
    p.add_argument("--db-path", type=str, default=None,
                   help="Path to SQLite database (default: from config)")
    p.add_argument("--plot-dir", type=str, default=None,
                   help="Directory for plots (default: from config)")
    args = p.parse_args()

    config = GenesisConfig()
    if args.db_path:
        config.tracking.db_path = args.db_path
    if args.plot_dir:
        config.tracking.plot_dir = args.plot_dir

    db = GenesisDB(config.tracking)

    if db.game_count() == 0:
        print("No data found in database. Run the engine first:")
        print("  python run.py --generations 5 --population 20 --training-budget 1000")
        db.close()
        sys.exit(1)

    # Generate text report
    reporter = GenesisReporter(db)
    report = reporter.summary_report()
    print(report)

    # Generate plots
    vis = GenesisVisualiser(config.tracking, db)
    plot_paths = vis.generate_all_plots()

    if plot_paths:
        print(f"\nPlots saved to {config.tracking.plot_dir}/:")
        for name, path in plot_paths.items():
            if path:
                print(f"  {name}: {path}")
    else:
        print("\nNo plots generated (insufficient data).")

    db.close()


if __name__ == "__main__":
    main()
