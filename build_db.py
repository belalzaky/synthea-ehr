# build_db.py — load five Synthea CSVs into a SQLite database (ehr.db)
#
# In the faers-sql project we built one table by hand, row by row, with
# INSERT statements. Here we use pandas' to_sql() method, which does the
# same thing automatically: it reads a CSV into a DataFrame, then writes
# the whole DataFrame into a SQLite table in one call.
#
# The result is a database with FIVE tables — one per CSV — all sitting
# inside the same file (ehr.db). That matters because SQLite (and SQL in
# general) can JOIN across tables in the same database. That's what we'll
# do in the next lap.

import sqlite3
import pandas as pd

DB_FILE = "ehr.db"
DATA_DIR = "data"

# The five main tables. The key on the left is what we'll call the table
# inside the database; the value on the right is the CSV filename.
TABLES = {
    "patients":     "patients.csv",
    "conditions":   "conditions.csv",
    "medications":  "medications.csv",
    "encounters":   "encounters.csv",
    "observations": "observations.csv",
}

# Open a connection to ehr.db (SQLite creates the file if it doesn't exist).
conn = sqlite3.connect(DB_FILE)

print(f"Loading CSVs into {DB_FILE}…\n")

for table_name, csv_file in TABLES.items():
    path = f"{DATA_DIR}/{csv_file}"

    # pd.read_csv() loads the CSV into a DataFrame — a familiar step.
    # low_memory=False avoids a pandas warning on mixed-type columns.
    df = pd.read_csv(path, low_memory=False)

    # df.to_sql() writes the entire DataFrame to the database as a table.
    #
    #   name=          → the table name inside the database
    #   con=           → the database connection to write to
    #   if_exists=     → "replace" means: drop and recreate the table on
    #                    every run, so we always start fresh
    #   index=False    → don't write pandas' row numbers as an extra column
    df.to_sql(table_name, con=conn, if_exists="replace", index=False)

    print(f"  ✓  {table_name:<14} {len(df):>7,} rows  ({len(df.columns)} columns)")

conn.close()
print(f"\nDatabase saved to: {DB_FILE}")
