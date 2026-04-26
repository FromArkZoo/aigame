"""Analyze CA transition table for game 992bf7dfc9f4."""
import json
import sqlite3

GAME_ID = "992bf7dfc9f4"
DB = "genesis_v2_run14.db"

conn = sqlite3.connect(DB)
row = conn.execute("SELECT rule_representation FROM games WHERE game_id = ?", (GAME_ID,)).fetchone()
rules = json.loads(row[0])
conn.close()

ca = rules["ca_rule"]
table = ca["transition_table"]
# Parse keys
parsed = {}
for k, v in table.items():
    s, f, e = map(int, k.split(","))
    parsed[(s, f, e)] = v

# Identity map: a transition is "trivial" if new_state == state (cell state unchanged)
# Find non-trivial transitions
nontrivial = []
birth = []       # state 0 -> 1 or 2
death = []       # state 1 -> 0
conversion = []  # state 1 -> 2  or  2 -> 1  (state flip)
empty_to_enemy = []  # state 0 -> 2 — "enemy emerges"
friendly_stays = 0
enemy_stays = 0

for (s, f, e), ns in sorted(parsed.items()):
    trivial = (ns == s)
    if not trivial:
        nontrivial.append(((s, f, e), ns))
    if s == 0 and ns == 1:
        birth.append(((s, f, e), ns))
    elif s == 0 and ns == 2:
        empty_to_enemy.append(((s, f, e), ns))
    elif s == 1 and ns == 0:
        death.append(((s, f, e), ns))
    elif s == 2 and ns == 0:
        pass  # enemy death
    elif s == 1 and ns == 2:
        conversion.append(((s, f, e), ns))
    elif s == 2 and ns == 1:
        conversion.append(((s, f, e), ns))

print(f"Total entries: {len(parsed)}")
print(f"Non-trivial (state changes): {len(nontrivial)}")
print(f"Trivial (identity): {len(parsed) - len(nontrivial)}")
print()
print(f"Birth (empty -> friendly): {len(birth)}")
for (k, ns) in birth:
    print(f"  (s={k[0]}, f={k[1]}, e={k[2]}) -> {ns}")
print()
print(f"Empty -> ENEMY (strange birth): {len(empty_to_enemy)}")
for (k, ns) in empty_to_enemy:
    print(f"  (s={k[0]}, f={k[1]}, e={k[2]}) -> {ns}")
print()
print(f"Death (friendly -> empty): {len(death)}")
for (k, ns) in death:
    print(f"  (s={k[0]}, f={k[1]}, e={k[2]}) -> {ns}")
print()
print(f"Conversion (1<->2): {len(conversion)}")
for (k, ns) in conversion:
    print(f"  (s={k[0]}, f={k[1]}, e={k[2]}) -> {ns}")

# Print full table sorted nicely
print("\nFull table (only non-trivial):")
print(f"  {'key':>20}  {'old':>3} -> {'new':>3}")
for (k, ns) in nontrivial:
    print(f"  (s={k[0]}, f={k[1]}, e={k[2]})  {k[0]:>3} -> {ns:>3}")

# Now think about per-player perspective. From P1 acting:
# - friendly=P1, enemy=P2
# From P2 acting:
# - friendly=P2, enemy=P1
# In simultaneous, step 1 is P1 perspective, step 2 is P2 perspective.
# But steps_per_turn=1 here, so only one CA step per simultaneous round,
# alternating perspective per round (step index mod 2).

# Each round runs step_simultaneous, which calls _run_ca_step ONCE
# with acting_player = 1 if step_count is even else 2. Wait let me reread...
# Actually: for i in range(steps_per_turn): acting_player = 1 if i%2==0 else 2
# Since steps_per_turn=1, only i=0, so acting_player always = 1 (P1 perspective!)
# That means CA is biased to P1 each turn!
print("\n\n*** CRITICAL: steps_per_turn =", ca["steps_per_turn"])
print("    step_simultaneous loop: for i in range(steps_per_turn): acting=1 if i%2==0 else 2")
print("    Since steps_per_turn=1, i=0 always -> acting_player=1 (P1 ALWAYS)")
print("    CA is evaluated from P1 perspective EVERY round. This is a P1 advantage!")
