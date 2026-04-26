"""Run random-vs-random games to verify P1 dominance."""
import sys, random
sys.path.insert(0, "/Users/jamesbrowne/aigame")

import sqlite3, json
from game_engine.game_def_v2 import GameDefV2
from game_engine.factory import create_engine

DB = "/Users/jamesbrowne/aigame/genesis_v2_run14.db"
GID = "992bf7dfc9f4"

def load():
    conn = sqlite3.connect(DB)
    row = conn.execute("SELECT rule_representation FROM games WHERE game_id=?", (GID,)).fetchone()
    conn.close()
    return GameDefV2.from_dict(json.loads(row[0]))

game = load()

results = []
for seed in range(20):
    random.seed(seed)
    engine = create_engine(game)
    engine.reset()
    round_num = 0
    collisions = 0
    while not engine.done and round_num < 150:
        round_num += 1
        p1_legal = engine.get_legal_actions(1)
        p2_legal = engine.get_legal_actions(2)
        # Random excluding pass when possible
        p1_place = [a for a in p1_legal if a < game.total_cells]
        p2_place = [a for a in p2_legal if a < game.total_cells]
        ap1 = random.choice(p1_place) if p1_place else game.total_cells
        ap2 = random.choice(p2_place) if p2_place else game.total_cells
        obs, r, done, info = engine.step_simultaneous(ap1, ap2)
        if info.get("collision"):
            collisions += 1

    results.append({
        "seed": seed,
        "p1": engine.piece_counts[0],
        "p2": engine.piece_counts[1],
        "winner": engine._winner,
        "rounds": round_num,
        "collisions": collisions,
    })

p1_wins = sum(1 for r in results if r["winner"] == 1)
p2_wins = sum(1 for r in results if r["winner"] == 2)
draws = sum(1 for r in results if r["winner"] is None)
avg_collisions = sum(r["collisions"] for r in results) / len(results)
avg_rounds = sum(r["rounds"] for r in results) / len(results)

print(f"Random vs random (20 games):")
print(f"  P1 wins: {p1_wins}/20 ({100*p1_wins/20:.0f}%)")
print(f"  P2 wins: {p2_wins}/20")
print(f"  Draws: {draws}/20")
print(f"  Avg rounds: {avg_rounds:.1f}")
print(f"  Avg collisions per game: {avg_collisions:.2f}")
print()
for r in results:
    w = "P1" if r["winner"] == 1 else ("P2" if r["winner"] == 2 else "draw")
    print(f"  seed={r['seed']:>2}: P1={r['p1']} P2={r['p2']} {w} rounds={r['rounds']} col={r['collisions']}")
