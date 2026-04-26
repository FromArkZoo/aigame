"""Analyze the CA transition table for game 992bf7dfc9f4.

The table is keyed by "state,friendly_neighbors,enemy_neighbors" -> new_state
(in the *abstract* frame where state 1 = acting player, state 2 = opponent).
Print a clear summary and classify each entry.
"""
import sqlite3, json, sys

DB = "/Users/jamesbrowne/aigame/genesis_v2_run14.db"
GID = "992bf7dfc9f4"

conn = sqlite3.connect(DB)
row = conn.execute("SELECT rule_representation FROM games WHERE game_id=?", (GID,)).fetchone()
rules = json.loads(row[0])
tt = rules["ca_rule"]["transition_table"]

# Parse keys
entries = []
for k, v in tt.items():
    s, f, e = map(int, k.split(","))
    entries.append((s, f, e, v))

entries.sort()

STATE = {0: "empty", 1: "FRIEND", 2: "ENEMY"}
count_birth = 0
count_death = 0
count_convert = 0  # friend<->enemy
count_identity = 0

active = []
for s, f, e, ns in entries:
    note = ""
    if ns == s:
        note = "identity"
        count_identity += 1
    else:
        if s == 0 and ns != 0:
            note = f"BIRTH -> {STATE[ns]}"
            count_birth += 1
        elif s == 1 and ns == 0:
            note = "DEATH (friend)"
            count_death += 1
        elif s == 2 and ns == 0:
            note = "DEATH (enemy)"
            count_death += 1
        elif s == 1 and ns == 2:
            note = "CONVERT friend->enemy (friend dies+enemy born)"
            count_convert += 1
        elif s == 2 and ns == 1:
            note = "CONVERT enemy->friend (capture)"
            count_convert += 1
        else:
            note = f"? {s}->{ns}"
        active.append((s, f, e, ns, note))

print("Transition table (abstract frame; 0=empty, 1=FRIEND-of-acting, 2=ENEMY-of-acting)")
print(f"{'state':<7}{'own_n':<7}{'opp_n':<7}{'->new':<7}  note")
for s, f, e, ns in entries:
    n = STATE[s]
    nn = STATE[ns]
    flag = "" if ns == s else "  *ACTIVE*"
    print(f"{n:<7}{f:<7}{e:<7}{nn:<7}{flag}")

print()
print(f"Totals: {len(entries)} entries")
print(f"  Identity (no change): {count_identity}")
print(f"  Birth (empty -> piece): {count_birth}")
print(f"  Death (piece -> empty): {count_death}")
print(f"  Conversion (friend<->enemy): {count_convert}")
print(f"  TOTAL ACTIVE (non-trivial): {count_birth+count_death+count_convert}")

print()
print("=== ACTIVE ENTRIES (only) ===")
for s, f, e, ns, note in active:
    print(f"  state={STATE[s]:<7} own_n={f} opp_n={e}  ->  {STATE[ns]:<7}  {note}")
