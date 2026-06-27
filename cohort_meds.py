# cohort_meds.py — top medications among patients with a specific condition
#
# Real-world-evidence (RWE) question:
#   "Among all patients in the database who have hypertension,
#    what are the 10 most commonly prescribed medications?"
#
# This is a standard cohort query: first define who is in the cohort
# (patients with the condition), then ask something about those patients
# (what medications they take).

import sqlite3

CONDITION = "Hypertension"

conn   = sqlite3.connect("ehr.db")
cursor = conn.cursor()

# ── Step 1: just see the top 20 conditions ────────────────────────────────────

QUERY_TOP = """
    SELECT DESCRIPTION, COUNT(*) AS n
    FROM conditions
    GROUP BY DESCRIPTION
    ORDER BY n DESC
    LIMIT 20
"""

print("Top 20 most common conditions\n")
print(f"{'Rank':<6}{'Count':>6}  Condition")
print("─" * 60)

cursor.execute(QUERY_TOP)
for rank, (desc, n) in enumerate(cursor.fetchall(), 1):
    marker = "  ◄── chosen" if desc == CONDITION else ""
    print(f"{rank:<6}{n:>6,}  {desc}{marker}")

# ── Step 2: top 10 meds for the hypertension cohort ──────────────────────────
#
# What is a subquery?
# ───────────────────
# A subquery is a complete SELECT statement nested inside another SELECT.
# SQL runs the inner query first, produces a result, and then the outer
# query uses that result.
#
# Here the inner (sub) query is:
#
#   SELECT PATIENT FROM conditions WHERE DESCRIPTION = 'Hypertension'
#
# This returns a list of patient UUIDs — every patient who has a hypertension
# diagnosis. Think of it as building a VIP list.
#
# The outer query then uses that list via IN:
#
#   WHERE PATIENT IN (...)
#
# IN works like Python's "in" operator: it keeps only the rows where the
# PATIENT column appears somewhere in the subquery's list.
# So the outer query sees only medication rows belonging to hypertension patients.
#
# Why not just JOIN medications to conditions directly?
# ─────────────────────────────────────────────────────
# The double-counting trap. A patient can have the same condition recorded
# more than once (e.g. hypertension diagnosed at several different visits).
# If you JOIN medications to conditions, that patient's medication rows get
# duplicated once for every matching conditions row.
#
# Example with one patient, two hypertension rows, one medication:
#
#   conditions rows          medications rows
#   ────────────────────     ────────────────────
#   PATIENT   DESCRIPTION    PATIENT   DESCRIPTION
#   abc-123   Hypertension   abc-123   Lisinopril
#   abc-123   Hypertension   (one row)
#
#   After JOIN: Lisinopril appears TWICE — once per conditions row.
#   COUNT(*) would count it twice. Wrong.
#
# The subquery avoids this entirely. It only asks "is this patient's ID
# in the hypertension list?" — a yes/no check per medication row, so each
# medication row is counted exactly once regardless of how many times the
# condition appears for that patient.

QUERY_MEDS = """
    SELECT DESCRIPTION, COUNT(*) AS n
    FROM medications
    WHERE PATIENT IN (
        SELECT PATIENT
        FROM conditions
        WHERE DESCRIPTION = ?
    )
    GROUP BY DESCRIPTION
    ORDER BY n DESC
    LIMIT 10
"""

print(f"\n\nTop 10 medications among patients with {CONDITION!r}\n")
print(f"{'Rank':<6}{'Medication':<52}{'Count':>6}")
print("─" * 64)

cursor.execute(QUERY_MEDS, (CONDITION,))
for rank, (med, n) in enumerate(cursor.fetchall(), 1):
    print(f"{rank:<6}{med:<52}{n:>6,}")

# ── Bonus: how big is this cohort? ────────────────────────────────────────────

cursor.execute(
    "SELECT COUNT(DISTINCT PATIENT) FROM conditions WHERE DESCRIPTION = ?",
    (CONDITION,)
)
cohort_size = cursor.fetchone()[0]
print(f"\nCohort size: {cohort_size} unique patients with {CONDITION!r}")

conn.close()
