#!/usr/bin/env python3
"""Post-run audit: compare GE/depth/diversity for games tagged with each
soft quick_reject rule vs untagged games.

Usage:
    python scripts/audit_soft_rules.py --db genesis_v2_run17.db

For each soft rule that fired in the run, prints a summary:
    n_violating, n_clean, mean GE (violating), mean GE (clean), Δ, p-value

Use this to decide whether a soft rule should be folded into the hard
gate (Δ < 0 with tight CI) or removed (Δ >= 0).
"""

import argparse
import json
import sqlite3
from collections import defaultdict
from statistics import mean, stdev


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db", required=True, help="SQLite database from a run")
    p.add_argument(
        "--metrics",
        nargs="+",
        default=["go_essence", "strategic_depth", "strategic_diversity"],
        help="Score columns to compare (default: go_essence depth diversity)",
    )
    return p.parse_args()


def welch_t(a: list[float], b: list[float]) -> tuple[float, float]:
    """Return (delta, two-sided p-value) for unequal-variance t-test.

    Implemented inline so the script has no scipy dependency.
    """
    if len(a) < 2 or len(b) < 2:
        return (mean(a) - mean(b) if a and b else 0.0, float("nan"))
    ma, mb = mean(a), mean(b)
    va, vb = stdev(a) ** 2, stdev(b) ** 2
    na, nb = len(a), len(b)
    se = (va / na + vb / nb) ** 0.5
    if se == 0:
        return (ma - mb, float("nan"))
    t = (ma - mb) / se
    # df via Welch-Satterthwaite
    df = (va / na + vb / nb) ** 2 / (
        (va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1)
    )
    # Two-sided p-value via normal approximation (df typically > 30 here)
    import math
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2))))
    return (ma - mb, p)


def main() -> None:
    args = parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row

    # Pull every game with its rule_representation and scores in one query.
    rows = conn.execute(
        """
        SELECT g.game_id, g.rule_representation, s.go_essence,
               s.strategic_depth, s.strategic_diversity,
               s.rule_simplicity, s.non_triviality
        FROM games g
        LEFT JOIN scores s USING (game_id)
        """
    ).fetchall()

    if not rows:
        print(f"No games in {args.db}")
        return

    # Bucket games by which soft rules they tripped.
    by_rule: dict[str, list[dict]] = defaultdict(list)
    clean: list[dict] = []
    for r in rows:
        if r["go_essence"] is None:
            continue  # game never scored (training failed)
        if not r["rule_representation"]:
            continue
        rep = json.loads(r["rule_representation"])
        violations = (rep.get("metadata") or {}).get("soft_violations") or []
        record = {m: r[m] for m in args.metrics}
        record["game_id"] = r["game_id"]
        if violations:
            for v in violations:
                by_rule[v].append(record)
        else:
            clean.append(record)

    if not by_rule:
        print(
            f"No soft_violations found in {args.db}. Either the run was in "
            "strict mode (no violations possible) or no rules fired. "
            "Re-run with --audit-soft-rules to populate."
        )
        return

    print(
        f"\n=== Soft-rule audit: {args.db} ===\n"
        f"Total games scored: {sum(len(v) for v in by_rule.values()) + len(clean)}\n"
        f"Clean (no soft rules tripped): {len(clean)}\n"
    )

    # Header
    metric_cols = "  ".join(f"{m:>12}" for m in args.metrics)
    print(f"{'rule':<32}  {'n':>4}  " + metric_cols)
    print("-" * (32 + 6 + 14 * len(args.metrics)))

    for rule, hits in sorted(by_rule.items()):
        cells = []
        for m in args.metrics:
            tagged = [h[m] for h in hits if h[m] is not None]
            untagged = [c[m] for c in clean if c[m] is not None]
            if not tagged:
                cells.append(f"{'-':>12}")
                continue
            delta, p = welch_t(tagged, untagged)
            tagged_m = mean(tagged)
            sig = "*" if p < 0.05 else " "
            cells.append(f"{tagged_m:>6.3f}{sig}Δ{delta:+.3f}")
        print(f"{rule:<32}  {len(hits):>4}  " + "  ".join(cells))

    print(
        "\nReading: per cell, '<mean>*Δ<delta>' shows the violating-games "
        "mean and the gap to clean games. '*' means p<0.05 (Welch t-test, "
        "normal approx). Negative Δ ⇒ rule is justified (violations score "
        "worse). Positive Δ ⇒ rule is over-rejecting playable games — "
        "consider removing or relaxing.\n"
    )

    conn.close()


if __name__ == "__main__":
    main()
