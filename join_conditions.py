# join_conditions.py — your first SQL JOIN: linking diagnoses to patients
#
# ── What is a JOIN? ───────────────────────────────────────────────────────────
#
# So far every query has read from ONE table at a time. A JOIN lets you
# combine two tables side-by-side in a single query, matching rows from
# one table to rows in the other.
#
# The two tables here:
#   conditions — one row per diagnosis  (has a PATIENT column)
#   patients   — one row per person     (has an Id column)
#
# The link between them:
#   conditions.PATIENT = patients.Id
#
# Every diagnosis row stores the UUID of the patient who has it (PATIENT).
# Every patient row has its own UUID (Id).
# A JOIN says: "find me every (diagnosis, patient) pair where those two
# UUIDs match — and then treat that pair as a single combined row."
#
# Visually:
#
#   conditions table          patients table
#   ──────────────────────    ──────────────────────────────
#   PATIENT        DESCRIPTION    Id              GENDER  BIRTHDATE
#   abc-123  →  Sinusitis         abc-123  ←──►   F       1990-03-12
#   def-456  →  Hypertension      def-456  ←──►   M       1975-07-04
#
#   After JOIN ON conditions.PATIENT = patients.Id:
#   ──────────────────────────────────────────────────────
#   DESCRIPTION    GENDER  BIRTHDATE
#   Sinusitis        F       1990-03-12
#   Hypertension     M       1975-07-04
#
# ── Table aliases (c and p) ───────────────────────────────────────────────────
#
# Both tables have columns called START, STOP, etc. Without aliases, SQL
# wouldn't know which table you mean when you write just "START".
# Aliases give each table a short nickname for the duration of the query:
#
#   FROM conditions c   →  "call conditions 'c' from here on"
#   JOIN patients   p   →  "call patients 'p' from here on"
#
# Then c.DESCRIPTION means "the DESCRIPTION column from conditions",
# and p.GENDER means "the GENDER column from patients".
# Aliases also just keep long queries readable — typing 'c' beats
# 'conditions' fifteen times.
#
# ── INNER JOIN (the default) ─────────────────────────────────────────────────
#
# When you write just JOIN, SQL does an INNER JOIN. It only keeps pairs
# where a match exists in BOTH tables. A diagnosis with no matching patient
# row would be silently dropped — and so would a patient with no diagnoses.
# (Other variants — LEFT JOIN, RIGHT JOIN — keep unmatched rows too. We'll
# get there in a later lap.)

import sqlite3

conn   = sqlite3.connect("ehr.db")
cursor = conn.cursor()

# ── Query A: see the join working ─────────────────────────────────────────────
#
# We pull three columns from two different tables in one query.
# Nothing is grouped or filtered yet — just a raw preview of what
# the join produces.

QUERY_A = """
    SELECT p.GENDER, p.BIRTHDATE, c.DESCRIPTION
    FROM conditions c
    JOIN patients p ON c.PATIENT = p.Id
    LIMIT 10
"""

print("── Query A: first 10 rows from a conditions–patients JOIN ───────────")
print(f"SQL:{QUERY_A}")

cursor.execute(QUERY_A)
rows    = cursor.fetchall()
headers = [d[0] for d in cursor.description]

print(f"{'GENDER':<8}{'BIRTHDATE':<14}{'DESCRIPTION'}")
print("─" * 65)
for gender, birthdate, desc in rows:
    print(f"{gender:<8}{birthdate:<14}{desc}")

# ── Query B: top 10 conditions among female patients ─────────────────────────
#
# Now we stack all four clauses together. The logical order SQL runs them:
#
#   1. FROM conditions c
#      JOIN patients p ON c.PATIENT = p.Id
#         → combine the two tables into one big joined result
#
#   2. WHERE p.GENDER = 'F'
#         → throw away every row where the patient is not female
#            (WHERE runs BEFORE grouping — it's still a sieve on rows)
#
#   3. GROUP BY c.DESCRIPTION
#         → collapse the surviving rows into one bucket per condition name
#
#   4. COUNT(*) AS n
#         → count how many rows are in each bucket
#
#   5. ORDER BY n DESC, LIMIT 10
#         → sort by count descending, keep top 10
#
# The key insight: JOIN just makes the two tables act like one.
# Everything you already know — WHERE, GROUP BY, COUNT, ORDER BY — works
# exactly the same way on the joined result.

QUERY_B = """
    SELECT c.DESCRIPTION, COUNT(*) AS n
    FROM conditions c
    JOIN patients p ON c.PATIENT = p.Id
    WHERE p.GENDER = 'F'
    GROUP BY c.DESCRIPTION
    ORDER BY n DESC
    LIMIT 10
"""

print("\n\n── Query B: top 10 conditions among female patients ─────────────────")
print(f"SQL:{QUERY_B}")

cursor.execute(QUERY_B)

print(f"{'Rank':<6}{'Condition':<45}{'Count':>6}")
print("─" * 57)
for rank, (desc, n) in enumerate(cursor.fetchall(), start=1):
    print(f"{rank:<6}{desc:<45}{n:>6,}")

conn.close()
