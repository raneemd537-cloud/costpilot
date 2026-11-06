"""Persistence layer: SQLite (local) or PostgreSQL (production).

Set DATABASE_URL to a postgresql:// connection string to use PostgreSQL.
Leave it unset to use the local SQLite file at DECISION_LAB_DATA.

Public API is identical for both backends so the rest of the application
does not need to know which database is in use.
"""

import hashlib
import hmac
import json
import os
import re
import secrets
import time
import uuid
from contextlib import closing, contextmanager
from pathlib import Path

# ---------------------------------------------------------------------------
# Backend detection
# ---------------------------------------------------------------------------

DATABASE_URL = os.environ.get("DATABASE_URL", "")
_USE_PG = DATABASE_URL.startswith("postgresql") or DATABASE_URL.startswith("postgres")

if _USE_PG:
    try:
        import psycopg2
        import psycopg2.extras
        import psycopg2.pool
    except ImportError as _e:
        raise ImportError(
            "psycopg2-binary is required for PostgreSQL. "
            "Run: pip install psycopg2-binary"
        ) from _e
else:
    import sqlite3

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _id():
    return str(uuid.uuid4())


def _owner_key(owner):
    if owner.get("type") not in ("guest", "user") or not owner.get("id"):
        raise ValueError("invalid owner")
    return owner["type"], owner["id"]


def _ph(n=1):
    """Return n positional placeholders for the active backend."""
    if _USE_PG:
        return tuple(f"%s" for _ in range(n))
    return tuple("?" for _ in range(n))


def _P(*_):
    """Single placeholder string."""
    return "%s" if _USE_PG else "?"


# ---------------------------------------------------------------------------
# SQLite DDL
# ---------------------------------------------------------------------------

_SQLITE_DDL = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY, email TEXT NOT NULL UNIQUE,
    salt BLOB NOT NULL, password_hash BLOB NOT NULL, created_at INTEGER NOT NULL,
    google_sub TEXT UNIQUE, display_name TEXT
);
CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY, owner_type TEXT NOT NULL,
    owner_id TEXT NOT NULL, csrf_hash TEXT NOT NULL, csrf_token TEXT NOT NULL,
    expires_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS sessions_owner ON sessions(owner_type, owner_id);
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY, owner_type TEXT NOT NULL, owner_id TEXT NOT NULL,
    data TEXT NOT NULL, created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS products_owner ON products(owner_type, owner_id);
CREATE TABLE IF NOT EXISTS scenarios (
    id TEXT PRIMARY KEY, product_id TEXT NOT NULL, owner_type TEXT NOT NULL,
    owner_id TEXT NOT NULL, data TEXT NOT NULL, created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS scenarios_product ON scenarios(owner_type, owner_id, product_id);
CREATE TABLE IF NOT EXISTS history (
    id TEXT PRIMARY KEY, product_id TEXT, owner_type TEXT NOT NULL,
    owner_id TEXT NOT NULL, data TEXT NOT NULL, created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS history_owner ON history(owner_type, owner_id, created_at DESC);
CREATE TABLE IF NOT EXISTS shared_expenses (
    id TEXT PRIMARY KEY, owner_type TEXT NOT NULL, owner_id TEXT NOT NULL,
    data TEXT NOT NULL, created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS shared_expenses_owner
    ON shared_expenses(owner_type, owner_id, created_at DESC);
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    token_hash TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    expires_at INTEGER NOT NULL,
    used INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS prt_user ON password_reset_tokens(user_id);
"""

# ---------------------------------------------------------------------------
# PostgreSQL DDL
# ---------------------------------------------------------------------------

_PG_DDL = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY, email TEXT NOT NULL UNIQUE,
    salt BYTEA NOT NULL, password_hash BYTEA NOT NULL,
    created_at BIGINT NOT NULL,
    google_sub TEXT UNIQUE, display_name TEXT
);
CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY, owner_type TEXT NOT NULL,
    owner_id TEXT NOT NULL, csrf_hash TEXT NOT NULL,
    csrf_token TEXT NOT NULL, expires_at BIGINT NOT NULL
);
CREATE INDEX IF NOT EXISTS sessions_owner ON sessions(owner_type, owner_id);
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY, owner_type TEXT NOT NULL, owner_id TEXT NOT NULL,
    data TEXT NOT NULL, created_at BIGINT NOT NULL, updated_at BIGINT NOT NULL
);
CREATE INDEX IF NOT EXISTS products_owner ON products(owner_type, owner_id);
CREATE TABLE IF NOT EXISTS scenarios (
    id TEXT PRIMARY KEY, product_id TEXT NOT NULL,
    owner_type TEXT NOT NULL, owner_id TEXT NOT NULL,
    data TEXT NOT NULL, created_at BIGINT NOT NULL, updated_at BIGINT NOT NULL
);
CREATE INDEX IF NOT EXISTS scenarios_product
    ON scenarios(owner_type, owner_id, product_id);
CREATE TABLE IF NOT EXISTS history (
    id TEXT PRIMARY KEY, product_id TEXT,
    owner_type TEXT NOT NULL, owner_id TEXT NOT NULL,
    data TEXT NOT NULL, created_at BIGINT NOT NULL
);
CREATE INDEX IF NOT EXISTS history_owner
    ON history(owner_type, owner_id, created_at DESC);
CREATE TABLE IF NOT EXISTS shared_expenses (
    id TEXT PRIMARY KEY, owner_type TEXT NOT NULL, owner_id TEXT NOT NULL,
    data TEXT NOT NULL, created_at BIGINT NOT NULL
);
CREATE INDEX IF NOT EXISTS shared_expenses_owner
    ON shared_expenses(owner_type, owner_id, created_at DESC);
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    token_hash TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    expires_at BIGINT NOT NULL,
    used SMALLINT NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS prt_user ON password_reset_tokens(user_id);
"""


# ---------------------------------------------------------------------------
# Store class
# ---------------------------------------------------------------------------

class Store:
    _USE_PG = _USE_PG  # expose for server.py introspection

    def __init__(self, path=None):
        """
        path  – Path to the SQLite file (used only when DATABASE_URL is not set).
              May be None when PostgreSQL is active.
        """
        if _USE_PG:
            self._pool = psycopg2.pool.ThreadedConnectionPool(1, 20, DATABASE_URL)
            self._init_pg()
        else:
            if path is None:
                raise ValueError("path is required when DATABASE_URL is not set")
            self.path = str(path)
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
            self._init_sqlite()

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _init_sqlite(self):
        # Use the raw connection directly during schema init (before cursor wrapper is needed)
        with closing(sqlite3.connect(self.path, timeout=10)) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys=ON")
            with conn:
                for statement in _SQLITE_DDL.strip().split(";"):
                    s = statement.strip()
                    if s:
                        conn.execute(s)

                # Schema migrations
                session_cols = {r["name"] for r in conn.execute("PRAGMA table_info(sessions)")}
                user_cols = {r["name"] for r in conn.execute("PRAGMA table_info(users)")}

                if "google_sub" not in user_cols:
                    conn.execute("ALTER TABLE users ADD COLUMN google_sub TEXT")
                if "display_name" not in user_cols:
                    conn.execute("ALTER TABLE users ADD COLUMN display_name TEXT")
                conn.execute(
                    "CREATE UNIQUE INDEX IF NOT EXISTS users_google_sub "
                    "ON users(google_sub) WHERE google_sub IS NOT NULL"
                )
                if "csrf_token" not in session_cols:
                    conn.execute(
                        "ALTER TABLE sessions ADD COLUMN csrf_token TEXT NOT NULL DEFAULT ''"
                    )
                for row in conn.execute(
                    "SELECT token_hash FROM sessions WHERE csrf_token=''"
                ).fetchall():
                    csrf = secrets.token_urlsafe(24)
                    conn.execute(
                        "UPDATE sessions SET csrf_hash=?, csrf_token=? WHERE token_hash=?",
                        (self._token_hash(csrf), csrf, row["token_hash"]),
                    )

    def _init_pg(self):
        with self._connect() as db:
            for statement in _PG_DDL.strip().split(";"):
                s = statement.strip()
                if s:
                    db.execute(s)
            db.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS display_name TEXT")

    # ------------------------------------------------------------------
    # Connection context managers
    # ------------------------------------------------------------------

    @contextmanager
    def _connect(self):
        if _USE_PG:
            conn = self._pool.getconn()
            try:
                conn.autocommit = False
                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                yield _PgCursor(cur, conn)
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                self._pool.putconn(conn)
        else:
            with closing(sqlite3.connect(self.path, timeout=10)) as conn:
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA foreign_keys=ON")
                with conn:
                    yield _SqliteCursor(conn)

    # ------------------------------------------------------------------
    # Hashing helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _token_hash(token):
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _password_hash(password, salt):
        return hashlib.scrypt(
            password.encode("utf-8"), salt=salt, n=2 ** 17, r=8, p=1,
            maxmem=256 * 1024 * 1024, dklen=32,
        )

    # ------------------------------------------------------------------
    # Session helpers
    # ------------------------------------------------------------------

    def _new_session(self, db, owner):
        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(24)
        expires = int(time.time()) + 60 * 60 * 24 * 30
        if _USE_PG:
            db.execute(
                "INSERT INTO sessions VALUES (%s,%s,%s,%s,%s,%s)",
                (self._token_hash(token), owner["type"], owner["id"],
                 self._token_hash(csrf), csrf, expires),
            )
        else:
            db.execute(
                "INSERT INTO sessions VALUES (?,?,?,?,?,?)",
                (self._token_hash(token), owner["type"], owner["id"],
                 self._token_hash(csrf), csrf, expires),
            )
        return {"token": token, "csrf": csrf, "owner": owner}

    def create_guest_session(self):
        with self._connect() as db:
            return self._new_session(db, {"type": "guest", "id": _id()})

    def _new_session_public(self, owner):
        """Create a new session and return it. Used by server after password reset."""
        with self._connect() as db:
            return self._new_session(db, owner)

    def resolve_session(self, token):
        if not token:
            return None
        h = self._token_hash(token)
        p = "%s" if _USE_PG else "?"
        with self._connect() as db:
            row = db.fetchone(f"SELECT * FROM sessions WHERE token_hash={p}", (h,))
            if not row or row["expires_at"] < int(time.time()):
                if row:
                    db.execute(f"DELETE FROM sessions WHERE token_hash={p}", (h,))
                return None
            return {
                "owner": {"type": row["owner_type"], "id": row["owner_id"]},
                "csrf_hash": row["csrf_hash"],
                "csrf": row["csrf_token"],
            }

    def validate_csrf(self, token, csrf):
        session = self.resolve_session(token)
        return bool(
            session and csrf
            and hmac.compare_digest(session["csrf_hash"], self._token_hash(csrf))
        )

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def register(self, email, password, guest_token=None, transfer_guest=False):
        email = email.strip().lower()
        if (
            len(email) > 254
            or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)
            or len(password) < 12
            or len(password) > 1024
        ):
            raise ValueError(
                "enter a valid email and a password of at least 12 characters"
            )
        salt = os.urandom(16)
        user = {"id": _id(), "email": email}
        p = "%s" if _USE_PG else "?"

        with self._connect() as db:
            try:
                db.execute(
                    f"INSERT INTO users (id,email,salt,password_hash,created_at) "
                    f"VALUES ({p},{p},{p},{p},{p})",
                    (user["id"], email, salt,
                     self._password_hash(password, salt), int(time.time())),
                )
            except Exception as exc:
                # duplicate email
                if "UNIQUE" in str(exc).upper() or "unique" in str(exc):
                    raise ValueError(
                        "account could not be created with those details"
                    )
                raise
            if guest_token:
                old_hash = self._token_hash(guest_token)
                guest = db.fetchone(
                    f"SELECT owner_type, owner_id FROM sessions WHERE token_hash={p}",
                    (old_hash,),
                )
                if guest and guest["owner_type"] == "guest" and transfer_guest:
                    old_id = guest["owner_id"]
                    for table in ("products", "scenarios", "history", "shared_expenses"):
                        db.execute(
                            f"UPDATE {table} SET owner_type={p}, owner_id={p} "
                            f"WHERE owner_type={p} AND owner_id={p}",
                            ("user", user["id"], "guest", old_id),
                        )
                db.execute(
                    f"DELETE FROM sessions WHERE token_hash={p}", (old_hash,)
                )
            session = self._new_session(db, {"type": "user", "id": user["id"]})
        return user, session

    def login(self, email, password):
        email = email.strip().lower()
        p = "%s" if _USE_PG else "?"
        with self._connect() as db:
            row = db.fetchone(f"SELECT * FROM users WHERE email={p}", (email,))
            salt = bytes(row["salt"]) if row else bytes(16)
            actual = self._password_hash(password, salt)
            expected = bytes(row["password_hash"]) if row else bytes(32)
            if not row or not hmac.compare_digest(actual, expected):
                raise ValueError("email or password is incorrect")
            user = {"id": row["id"], "email": row["email"]}
            return user, self._new_session(db, {"type": "user", "id": user["id"]})

    def login_with_google(self, email, google_sub, guest_token=None,
                          transfer_guest=False, display_name=None):
        email = email.strip().lower()
        google_sub = str(google_sub).strip()
        display_name = str(display_name or "").strip()[:120] or None
        if len(email) > 254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise ValueError("Google account did not provide a valid email")
        if not google_sub or len(google_sub) > 255:
            raise ValueError("Google account identity is invalid")
        p = "%s" if _USE_PG else "?"
        with self._connect() as db:
            row = db.fetchone(
                f"SELECT * FROM users WHERE google_sub={p}", (google_sub,)
            )
            if row and row["email"] != email:
                conflict = db.fetchone(
                    f"SELECT id FROM users WHERE email={p}", (email,)
                )
                if conflict and conflict["id"] != row["id"]:
                    raise ValueError(
                        "Google account email is already linked to another account"
                    )
                db.execute(
                    f"UPDATE users SET email={p} WHERE id={p}", (email, row["id"])
                )
            elif not row:
                row = db.fetchone(f"SELECT * FROM users WHERE email={p}", (email,))
                if row and row["google_sub"]:
                    raise ValueError("email is linked to a different Google account")
                if row:
                    db.execute(
                        f"UPDATE users SET google_sub={p} WHERE id={p}",
                        (google_sub, row["id"]),
                    )
                else:
                    user_id = _id()
                    salt = os.urandom(16)
                    random_pw = secrets.token_urlsafe(48)
                    db.execute(
                        f"INSERT INTO users (id,email,salt,password_hash,created_at,google_sub) "
                        f"VALUES ({p},{p},{p},{p},{p},{p})",
                        (user_id, email, salt,
                         self._password_hash(random_pw, salt),
                         int(time.time()), google_sub),
                    )
                    row = db.fetchone(
                        f"SELECT * FROM users WHERE id={p}", (user_id,)
                    )
            if display_name:
                db.execute(
                    f"UPDATE users SET display_name={p} WHERE id={p}",
                    (display_name, row["id"]),
                )
            user = {"id": row["id"], "email": email, "display_name": display_name or row["display_name"]}
            if guest_token:
                old_hash = self._token_hash(guest_token)
                guest = db.fetchone(
                    f"SELECT owner_type, owner_id FROM sessions WHERE token_hash={p}",
                    (old_hash,),
                )
                if guest and guest["owner_type"] == "guest" and transfer_guest:
                    for table in ("products", "scenarios", "history", "shared_expenses"):
                        db.execute(
                            f"UPDATE {table} SET owner_type={p}, owner_id={p} "
                            f"WHERE owner_type={p} AND owner_id={p}",
                            ("user", user["id"], "guest", guest["owner_id"]),
                        )
                db.execute(
                    f"DELETE FROM sessions WHERE token_hash={p}", (old_hash,)
                )
            session = self._new_session(db, {"type": "user", "id": user["id"]})
        return user, session

    def logout(self, token):
        p = "%s" if _USE_PG else "?"
        h = self._token_hash(token or "")
        with self._connect() as db:
            db.execute(f"DELETE FROM sessions WHERE token_hash={p}", (h,))

    # ------------------------------------------------------------------
    # Password reset
    # ------------------------------------------------------------------

    def create_password_reset_token(self, email: str):
        """Create a single-use 1-hour password-reset token for *email*.

        Returns the plain-text token (to be emailed) or raises LookupError
        if the email is not registered.
        """
        email = email.strip().lower()
        p = "%s" if _USE_PG else "?"
        with self._connect() as db:
            row = db.fetchone(f"SELECT id FROM users WHERE email={p}", (email,))
            if not row:
                raise LookupError("no account with that email address")
            # Invalidate any previous unused tokens for this user
            db.execute(
                f"DELETE FROM password_reset_tokens WHERE user_id={p}", (row["id"],)
            )
            token = secrets.token_urlsafe(32)
            token_hash = self._token_hash(token)
            expires = int(time.time()) + 3600  # 1 hour
            db.execute(
                f"INSERT INTO password_reset_tokens VALUES ({p},{p},{p},0)",
                (token_hash, row["id"], expires),
            )
        return token

    def consume_password_reset_token(self, token: str, new_password: str):
        """Validate *token*, set *new_password*, mark token as used.

        Raises ValueError for invalid/expired/used tokens or weak passwords.
        Returns the user dict on success.
        """
        if len(new_password) < 12 or len(new_password) > 1024:
            raise ValueError("password must be at least 12 characters")
        token_hash = self._token_hash(token)
        p = "%s" if _USE_PG else "?"
        with self._connect() as db:
            row = db.fetchone(
                f"SELECT * FROM password_reset_tokens WHERE token_hash={p}",
                (token_hash,),
            )
            if not row:
                raise ValueError("invalid or expired reset link")
            if row["used"]:
                raise ValueError("this reset link has already been used")
            if row["expires_at"] < int(time.time()):
                db.execute(
                    f"DELETE FROM password_reset_tokens WHERE token_hash={p}",
                    (token_hash,),
                )
                raise ValueError("this reset link has expired")
            salt = os.urandom(16)
            new_hash = self._password_hash(new_password, salt)
            db.execute(
                f"UPDATE users SET salt={p}, password_hash={p} WHERE id={p}",
                (salt, new_hash, row["user_id"]),
            )
            db.execute(
                f"UPDATE password_reset_tokens SET used=1 WHERE token_hash={p}",
                (token_hash,),
            )
            # Revoke all sessions for this user (security: log out all devices)
            db.execute(
                f"DELETE FROM sessions WHERE owner_type='user' AND owner_id={p}",
                (row["user_id"],),
            )
            user_row = db.fetchone(
                f"SELECT id, email FROM users WHERE id={p}", (row["user_id"],)
            )
            return {"id": user_row["id"], "email": user_row["email"]}

    # ------------------------------------------------------------------
    # Products
    # ------------------------------------------------------------------

    @staticmethod
    def _decode(row):
        data = json.loads(row["data"])
        data.update({"id": row["id"]})
        return data

    def list_products(self, owner):
        kind, ident = _owner_key(owner)
        p = "%s" if _USE_PG else "?"
        with self._connect() as db:
            rows = db.fetchall(
                f"SELECT * FROM products WHERE owner_type={p} AND owner_id={p} "
                f"ORDER BY updated_at DESC",
                (kind, ident),
            )
        return [self._decode(r) for r in rows]

    def get_product(self, owner, product_id):
        kind, ident = _owner_key(owner)
        p = "%s" if _USE_PG else "?"
        with self._connect() as db:
            row = db.fetchone(
                f"SELECT * FROM products WHERE id={p} AND owner_type={p} AND owner_id={p}",
                (product_id, kind, ident),
            )
        return self._decode(row) if row else None

    def save_product(self, owner, data):
        kind, ident = _owner_key(owner)
        product_id = data.get("id") or _id()
        now = int(time.time())
        payload = {k: v for k, v in data.items() if k not in ("id", "created_at", "updated_at")}
        encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False)
        p = "%s" if _USE_PG else "?"
        with self._connect() as db:
            row = db.fetchone(
                f"SELECT id FROM products WHERE id={p} AND owner_type={p} AND owner_id={p}",
                (product_id, kind, ident),
            )
            if data.get("id") and not row:
                raise LookupError("product not found")
            if row:
                db.execute(
                    f"UPDATE products SET data={p}, updated_at={p} "
                    f"WHERE id={p} AND owner_type={p} AND owner_id={p}",
                    (encoded, now, product_id, kind, ident),
                )
            else:
                db.execute(
                    f"INSERT INTO products VALUES ({p},{p},{p},{p},{p},{p})",
                    (product_id, kind, ident, encoded, now, now),
                )
        return self.get_product(owner, product_id)

    def delete_product(self, owner, product_id):
        kind, ident = _owner_key(owner)
        p = "%s" if _USE_PG else "?"
        with self._connect() as db:
            groups = db.fetchall(
                f"SELECT id, data FROM shared_expenses WHERE owner_type={p} AND owner_id={p}",
                (kind, ident),
            )
            for group in groups:
                gdata = json.loads(group["data"])
                if product_id in gdata.get("product_ids", []):
                    gdata["product_ids"] = [
                        i for i in gdata["product_ids"] if i != product_id
                    ]
                    if gdata["product_ids"]:
                        db.execute(
                            f"UPDATE shared_expenses SET data={p} WHERE id={p}",
                            (json.dumps(gdata, ensure_ascii=False), group["id"]),
                        )
                    else:
                        db.execute(
                            f"DELETE FROM shared_expenses WHERE id={p}", (group["id"],)
                        )
            result_rows = db.execute(
                f"DELETE FROM products WHERE id={p} AND owner_type={p} AND owner_id={p}",
                (product_id, kind, ident),
            )
            db.execute(
                f"DELETE FROM scenarios WHERE product_id={p} AND owner_type={p} AND owner_id={p}",
                (product_id, kind, ident),
            )
            return (result_rows if isinstance(result_rows, int)
                    else result_rows.rowcount) > 0

    # ------------------------------------------------------------------
    # Scenarios
    # ------------------------------------------------------------------

    def save_scenario(self, owner, product_id, data):
        kind, ident = _owner_key(owner)
        if not self.get_product(owner, product_id):
            raise LookupError("product not found")
        scenario_id = data.get("id") or _id()
        now = int(time.time())
        payload = {k: v for k, v in data.items() if k not in ("id", "created_at", "updated_at")}
        encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False)
        p = "%s" if _USE_PG else "?"
        with self._connect() as db:
            row = db.fetchone(
                f"SELECT id FROM scenarios WHERE id={p} AND owner_type={p} "
                f"AND owner_id={p} AND product_id={p}",
                (scenario_id, kind, ident, product_id),
            )
            if data.get("id") and not row:
                raise LookupError("scenario not found")
            if row:
                db.execute(
                    f"UPDATE scenarios SET data={p}, updated_at={p} "
                    f"WHERE id={p} AND owner_type={p} AND owner_id={p}",
                    (encoded, now, scenario_id, kind, ident),
                )
            else:
                db.execute(
                    f"INSERT INTO scenarios VALUES ({p},{p},{p},{p},{p},{p},{p})",
                    (scenario_id, product_id, kind, ident, encoded, now, now),
                )
            row = db.fetchone(
                f"SELECT * FROM scenarios WHERE id={p}", (scenario_id,)
            )
        return self._decode(row)

    def list_scenarios(self, owner, product_id):
        kind, ident = _owner_key(owner)
        p = "%s" if _USE_PG else "?"
        with self._connect() as db:
            rows = db.fetchall(
                f"SELECT * FROM scenarios WHERE product_id={p} AND owner_type={p} "
                f"AND owner_id={p} ORDER BY created_at",
                (product_id, kind, ident),
            )
        return [self._decode(r) for r in rows]

    def get_scenario(self, owner, scenario_id):
        kind, ident = _owner_key(owner)
        p = "%s" if _USE_PG else "?"
        with self._connect() as db:
            row = db.fetchone(
                f"SELECT * FROM scenarios WHERE id={p} AND owner_type={p} AND owner_id={p}",
                (scenario_id, kind, ident),
            )
        return {**self._decode(row), "product_id": row["product_id"]} if row else None

    def delete_scenario(self, owner, scenario_id):
        kind, ident = _owner_key(owner)
        p = "%s" if _USE_PG else "?"
        with self._connect() as db:
            result = db.execute(
                f"DELETE FROM scenarios WHERE id={p} AND owner_type={p} AND owner_id={p}",
                (scenario_id, kind, ident),
            )
        return (result if isinstance(result, int) else result.rowcount) > 0

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def add_history(self, owner, product_id, data):
        kind, ident = _owner_key(owner)
        history_id = _id()
        now = int(time.time())
        encoded = json.dumps(data, ensure_ascii=False, allow_nan=False)
        p = "%s" if _USE_PG else "?"
        with self._connect() as db:
            db.execute(
                f"INSERT INTO history VALUES ({p},{p},{p},{p},{p},{p})",
                (history_id, product_id, kind, ident, encoded, now),
            )
        return {"id": history_id, "created_at": now, **data}

    def list_history(self, owner, limit=10000):
        kind, ident = _owner_key(owner)
        p = "%s" if _USE_PG else "?"
        limit = min(max(int(limit), 1), 10000)
        with self._connect() as db:
            rows = db.fetchall(
                f"SELECT * FROM history WHERE owner_type={p} AND owner_id={p} "
                f"ORDER BY created_at DESC LIMIT {p}",
                (kind, ident, limit),
            )
        return [
            {"id": r["id"], "product_id": r["product_id"],
             "created_at": r["created_at"], **json.loads(r["data"])}
            for r in rows
        ]

    # ------------------------------------------------------------------
    # Shared expenses
    # ------------------------------------------------------------------

    def save_shared_expense(self, owner, data):
        kind, ident = _owner_key(owner)
        expense_id = data.get("id") or _id()
        payload = {k: v for k, v in data.items() if k not in ("id", "created_at")}
        encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False)
        p = "%s" if _USE_PG else "?"
        with self._connect() as db:
            if data.get("id"):
                result = db.execute(
                    f"UPDATE shared_expenses SET data={p} "
                    f"WHERE id={p} AND owner_type={p} AND owner_id={p}",
                    (encoded, expense_id, kind, ident),
                )
                if (result if isinstance(result, int) else result.rowcount) == 0:
                    raise LookupError("shared expense not found")
            else:
                db.execute(
                    f"INSERT INTO shared_expenses VALUES ({p},{p},{p},{p},{p})",
                    (expense_id, kind, ident, encoded, int(time.time())),
                )
        return {"id": expense_id, **payload}

    def list_shared_expenses(self, owner):
        kind, ident = _owner_key(owner)
        p = "%s" if _USE_PG else "?"
        with self._connect() as db:
            rows = db.fetchall(
                f"SELECT id, data, created_at FROM shared_expenses "
                f"WHERE owner_type={p} AND owner_id={p} ORDER BY created_at DESC",
                (kind, ident),
            )
        return [
            {"id": r["id"], "created_at": r["created_at"], **json.loads(r["data"])}
            for r in rows
        ]

    def delete_shared_expense(self, owner, expense_id):
        kind, ident = _owner_key(owner)
        p = "%s" if _USE_PG else "?"
        with self._connect() as db:
            result = db.execute(
                f"DELETE FROM shared_expenses WHERE id={p} AND owner_type={p} AND owner_id={p}",
                (expense_id, kind, ident),
            )
        return (result if isinstance(result, int) else result.rowcount) > 0


# ---------------------------------------------------------------------------
# PostgreSQL cursor wrapper (mirrors sqlite3 API used by the Store)
# ---------------------------------------------------------------------------

class _PgCursor:
    """Thin wrapper so PostgreSQL cursor matches the sqlite3 connection API."""

    def __init__(self, cur, conn):
        self._cur = cur
        self._conn = conn

    def execute(self, sql, params=()):
        self._cur.execute(sql, params)
        return self._cur.rowcount

    def fetchone(self, sql, params=()):
        self._cur.execute(sql, params)
        return self._cur.fetchone()

    def fetchall(self, sql, params=()):
        self._cur.execute(sql, params)
        return self._cur.fetchall()



# ---------------------------------------------------------------------------
# SQLite cursor wrapper — same interface as _PgCursor
# ---------------------------------------------------------------------------

class _SqliteCursor:
    """Wraps sqlite3.Connection to expose the same API as _PgCursor."""

    def __init__(self, conn):
        self._conn = conn

    def execute(self, sql, params=()):
        return self._conn.execute(sql, params).rowcount

    def fetchone(self, sql, params=()):
        return self._conn.execute(sql, params).fetchone()

    def fetchall(self, sql, params=()):
        return self._conn.execute(sql, params).fetchall()
