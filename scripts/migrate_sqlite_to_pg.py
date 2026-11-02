"""One-time migration from SQLite to PostgreSQL.

Usage:
    DATABASE_URL=postgresql://user:pass@host/db \\
    DECISION_LAB_DATA=.decision-lab \\
    python scripts/migrate_sqlite_to_pg.py

What this script does:
  1. Reads every row from the local SQLite database.
  2. Inserts it into the target PostgreSQL database (ON CONFLICT DO NOTHING).
  3. Verifies that row counts match after migration.
  4. Is safe to re-run — existing rows are skipped.

Requirements:
    pip install psycopg2-binary
"""
import json
import os
import sqlite3
import sys
from pathlib import Path

# Validate prerequisites
if not os.environ.get("DATABASE_URL"):
    print("ERROR: DATABASE_URL is not set.", file=sys.stderr)
    sys.exit(1)

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("ERROR: psycopg2-binary is not installed.\nRun: pip install psycopg2-binary", file=sys.stderr)
    sys.exit(1)

DATA_DIR = Path(os.environ.get("DECISION_LAB_DATA", ".decision-lab")).expanduser()
DB_FILE = DATA_DIR / "decision-lab.sqlite3"

if not DB_FILE.exists():
    print(f"ERROR: SQLite database not found at {DB_FILE}", file=sys.stderr)
    sys.exit(1)

TABLES = [
    "users",
    "sessions",
    "products",
    "scenarios",
    "history",
    "shared_expenses",
    "password_reset_tokens",
]


def migrate():
    src = sqlite3.connect(str(DB_FILE))
    src.row_factory = sqlite3.Row
    dst = psycopg2.connect(os.environ["DATABASE_URL"])
    dst.autocommit = False
    cur = dst.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    safe_url = os.environ["DATABASE_URL"].split("@")[-1]
    print(f"[migrate] Source : {DB_FILE}")
    print(f"[migrate] Target : {safe_url}")
    print()

    total = 0
    for table in TABLES:
        # Check if table exists in SQLite
        exists = src.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
        ).fetchone()
        if not exists:
            print(f"  {table:30s} — not in SQLite, skipping")
            continue

        rows = src.execute(f"SELECT * FROM {table}").fetchall()
        if not rows:
            print(f"  {table:30s} — 0 rows")
            continue

        cols = list(rows[0].keys())
        col_str = ", ".join(cols)
        placeholders = ", ".join(["%s"] * len(cols))

        migrated = skipped = 0
        for row in rows:
            values = [bytes(v) if isinstance(v, memoryview) else v for v in row]
            try:
                cur.execute(
                    f"INSERT INTO {table} ({col_str}) VALUES ({placeholders}) "
                    f"ON CONFLICT DO NOTHING",
                    values,
                )
                if cur.rowcount > 0:
                    migrated += 1
                else:
                    skipped += 1
            except Exception as exc:
                dst.rollback()
                print(f"\n  ERROR migrating {table}: {exc}", file=sys.stderr)
                src.close()
                dst.close()
                sys.exit(1)

        dst.commit()
        total += migrated
        print(f"  {table:30s} — {migrated} migrated, {skipped} already existed")

    # Verify counts
    print("\n[migrate] Verifying row counts …")
    mismatch = False
    for table in TABLES:
        exists = src.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
        ).fetchone()
        if not exists:
            continue
        sqlite_count = src.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        pg_count = cur.fetchone()["count"]
        status = "✓" if sqlite_count == pg_count else "✗ MISMATCH"
        print(f"  {table:30s} SQLite={sqlite_count}  PostgreSQL={pg_count}  {status}")
        if sqlite_count != pg_count:
            mismatch = True

    src.close()
    dst.close()

    if mismatch:
        print("\n[migrate] WARNING: Row count mismatch detected. Re-run the script to retry.", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"\n[migrate] Complete. {total} rows migrated successfully.")


if __name__ == "__main__":
    migrate()
