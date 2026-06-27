# query.py — connect to ehr.db and run first SQL checks
#
# Two things to verify after loading:
#   1. Row counts — did every table load completely?
#   2. A quick preview — does the patients table look right?

import sqlite3

conn   = sqlite3.connect("ehr.db")
cursor = conn.cursor()

# ── 1. Row count for each table ───────────────────────────────────────────────
#
# sqlite_master is a special built-in table that SQLite maintains for you.
# It lists every table (and index, view, etc.) in the database.
# We query it here just to get the table names dynamically, so we don't have
# to hard-code them.

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
table_names = [row[0] for row in cursor.fetchall()]

print("Row counts in ehr.db\n")
print(f"{'Table':<16}{'Rows':>10}")
print("─" * 27)

for name in table_names:
    cursor.execute(f"SELECT COUNT(*) FROM {name}")
    count = cursor.fetchone()[0]
    print(f"{name:<16}{count:>10,}")

# ── 2. Preview the patients table ─────────────────────────────────────────────
#
# SELECT * FROM patients LIMIT 3 — same pattern as faers-sql.
# The new thing: because the columns in patients are wide, we print them
# one per line (transposed view) so they're readable in the terminal.

print("\n\nFirst 3 rows of patients (column-by-column view)\n")

cursor.execute("SELECT * FROM patients LIMIT 3")
rows    = cursor.fetchall()
headers = [d[0] for d in cursor.description]

for i, row in enumerate(rows, start=1):
    print(f"─── Patient {i} " + "─" * 40)
    for col, val in zip(headers, row):
        print(f"  {col:<25} {val}")
    print()

conn.close()
