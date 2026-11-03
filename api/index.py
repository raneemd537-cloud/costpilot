"""Vercel entry point for ProfitPilot.

The application still uses its existing BaseHTTPRequestHandler router.
A persistent PostgreSQL DATABASE_URL is required on Vercel; SQLite is
not suitable for serverless ephemeral filesystems.
"""
import os
from pathlib import Path

from app.server import make_handler
from app.store import Store, _USE_PG

if not _USE_PG:
    raise RuntimeError(
        "ProfitPilot on Vercel requires DATABASE_URL pointing to PostgreSQL."
    )

ROOT = Path(__file__).resolve().parent.parent
store = Store()
handler = make_handler(store, ROOT / "web")
