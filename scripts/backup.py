"""Daily SQLite backup script — safe hot backup using sqlite3.Connection.backup().

Usage:
    python scripts/backup.py

Environment variables:
    DECISION_LAB_DATA   Path to the data directory (default: .decision-lab)
    BACKUP_DIR          Where to write backups     (default: .backups)
    BACKUP_KEEP_DAYS    Days of backups to retain  (default: 14)

Schedule with cron or a Railway cron job:
    0 3 * * * cd /app && python scripts/backup.py
"""
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

DATA_DIR = Path(os.environ.get("DECISION_LAB_DATA", ".decision-lab")).expanduser()
DB_FILE = DATA_DIR / "decision-lab.sqlite3"
BACKUP_DIR = Path(os.environ.get("BACKUP_DIR", ".backups"))
KEEP_DAYS = int(os.environ.get("BACKUP_KEEP_DAYS", "14"))


def run():
    if not DB_FILE.exists():
        print(f"[backup] Database not found at {DB_FILE}. Nothing to back up.", file=sys.stderr)
        sys.exit(0)

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = BACKUP_DIR / f"decision-lab-{stamp}.sqlite3"

    # sqlite3.Connection.backup() performs a safe online backup — no locking issues
    src = sqlite3.connect(str(DB_FILE))
    dst = sqlite3.connect(str(dest))
    src.backup(dst)
    dst.close()
    src.close()

    size_kb = dest.stat().st_size // 1024
    print(f"[backup] Written: {dest}  ({size_kb} KB)")

    # Prune old backups beyond retention period
    cutoff = datetime.now(timezone.utc) - timedelta(days=KEEP_DAYS)
    pruned = 0
    for old in BACKUP_DIR.glob("decision-lab-*.sqlite3"):
        try:
            ts_str = old.stem.replace("decision-lab-", "")
            ts = datetime.strptime(ts_str, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            if ts < cutoff:
                old.unlink()
                pruned += 1
        except ValueError:
            pass
    if pruned:
        print(f"[backup] Pruned {pruned} backup(s) older than {KEEP_DAYS} days.")
    print("[backup] Done.")


if __name__ == "__main__":
    run()
