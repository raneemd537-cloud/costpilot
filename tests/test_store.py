import tempfile
import unittest
import hashlib
import sqlite3
import time
from pathlib import Path

from app.store import Store


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.tmp.name) / "test.db")
        self.guest = self.store.create_guest_session()

    def tearDown(self):
        self.tmp.cleanup()

    def test_guest_products_and_scenarios_are_scoped_and_persist(self):
        product = self.store.save_product(self.guest["owner"], {"name": "Mug", "currency": "ILS"})
        self.store.save_scenario(self.guest["owner"], product["id"], {"name": "Sale", "selling_price": "20", "discount_percent": "10"})
        self.assertEqual(self.store.list_products(self.guest["owner"])[0]["name"], "Mug")
        self.assertEqual(len(self.store.list_scenarios(self.guest["owner"], product["id"])), 1)
        self.assertEqual(self.store.list_products({"type": "guest", "id": "other"}), [])

    def test_registration_can_explicitly_transfer_or_discard_guest_data(self):
        self.store.save_product(self.guest["owner"], {"name": "Keep me", "currency": "USD"})
        user, session = self.store.register("seller@example.test", "a-long-safe-password", self.guest["token"], transfer_guest=True)
        self.assertEqual(len(self.store.list_products({"type": "user", "id": user["id"]})), 1)
        empty_guest = self.store.create_guest_session()
        self.store.save_product(empty_guest["owner"], {"name": "Leave behind", "currency": "EUR"})
        second, _ = self.store.register("second@example.test", "a-long-safe-password", empty_guest["token"], transfer_guest=False)
        self.assertEqual(self.store.list_products({"type": "user", "id": second["id"]}), [])

    def test_registration_rejects_malformed_email_before_hashing(self):
        with self.assertRaisesRegex(ValueError, "valid email"):
            self.store.register("seller@invalid", "a-long-safe-password")

    def test_google_identity_is_idempotent_and_transfers_guest_workspace(self):
        self.store.save_product(self.guest["owner"], {"name": "Google product", "currency": "USD"})
        user, session = self.store.login_with_google("seller@example.test", "google-sub-1", self.guest["token"], True, "Seller Name")
        again, next_session = self.store.login_with_google("seller@example.test", "google-sub-1")
        self.assertEqual(user["id"], again["id"])
        self.assertEqual(user["display_name"], "Seller Name")
        self.assertEqual(again["display_name"], "Seller Name")
        self.assertEqual(session["owner"], next_session["owner"])
        self.assertEqual(len(self.store.list_products({"type": "user", "id": user["id"]})), 1)

    def test_google_identity_cannot_be_claimed_by_a_different_subject(self):
        self.store.login_with_google("seller@example.test", "google-sub-1")
        with self.assertRaisesRegex(ValueError, "Google account"):
            self.store.login_with_google("seller@example.test", "google-sub-2")

    def test_legacy_users_table_migrates_display_name_without_losing_account(self):
        legacy_path = Path(self.tmp.name) / "legacy-users.db"
        db = sqlite3.connect(legacy_path)
        db.execute(
            "CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT NOT NULL UNIQUE, "
            "salt BLOB NOT NULL, password_hash BLOB NOT NULL, created_at INTEGER NOT NULL, "
            "google_sub TEXT UNIQUE)"
        )
        salt = b"0123456789abcdef"
        password_hash = hashlib.scrypt(
            b"a-long-safe-password", salt=salt, n=2 ** 17, r=8, p=1,
            maxmem=256 * 1024 * 1024, dklen=32,
        )
        db.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
            ("legacy-user", "legacy@example.test", salt, password_hash, int(time.time()), None),
        )
        db.commit()
        db.close()

        upgraded = Store(legacy_path)
        with upgraded._connect() as conn:
            columns = {row["name"] for row in conn.execute("PRAGMA table_info(users)")}
            row = conn.fetchone("SELECT id, email, display_name FROM users WHERE id=?", ("legacy-user",))
        self.assertIn("display_name", columns)
        self.assertEqual(row["email"], "legacy@example.test")
        self.assertIsNone(row["display_name"])
        user, _ = upgraded.login("legacy@example.test", "a-long-safe-password")
        self.assertEqual(user["id"], "legacy-user")

    def test_product_removal_cascades_scenarios_but_not_calculation_history(self):
        owner = self.guest["owner"]
        product = self.store.save_product(owner, {"name": "Cup", "currency": "USD"})
        self.store.save_scenario(owner, product["id"], {"name": "A", "selling_price": 12, "discount_percent": 0})
        self.store.add_history(owner, product["id"], {"inputs": {"price": 12}, "result": {"profit": 3}})
        self.store.delete_product(owner, product["id"])
        self.assertEqual(self.store.list_scenarios(owner, product["id"]), [])
        self.assertEqual(len(self.store.list_history(owner)), 1)

    def test_shared_expenses_persist_and_are_owner_scoped(self):
        owner = self.guest["owner"]
        expense = self.store.save_shared_expense(owner, {"name": "Freight", "amount": "5.00", "basis": "quantity", "product_ids": ["p1", "p2"]})
        self.assertEqual(self.store.list_shared_expenses(owner)[0]["id"], expense["id"])
        self.assertEqual(self.store.list_shared_expenses({"type": "guest", "id": "other"}), [])
        self.assertTrue(self.store.delete_shared_expense(owner, expense["id"]))

    def test_deleting_product_removes_it_from_shared_expense_participants(self):
        owner = self.guest["owner"]
        a = self.store.save_product(owner, {"name": "A", "currency": "USD"})
        b = self.store.save_product(owner, {"name": "B", "currency": "USD"})
        self.store.save_shared_expense(owner, {"name": "Fee", "amount": "6.00", "basis": "quantity", "product_ids": [a["id"], b["id"]]})
        self.store.delete_product(owner, a["id"])
        remaining = self.store.list_shared_expenses(owner)
        self.assertEqual(remaining[0]["product_ids"], [b["id"]])

    def test_existing_sessions_migrate_to_readable_csrf_tokens(self):
        legacy_path=Path(self.tmp.name)/"legacy.db"
        token="legacy-session-token"
        db=sqlite3.connect(legacy_path)
        db.execute("CREATE TABLE sessions (token_hash TEXT PRIMARY KEY, owner_type TEXT NOT NULL, owner_id TEXT NOT NULL, csrf_hash TEXT NOT NULL, expires_at INTEGER NOT NULL)")
        db.execute("INSERT INTO sessions VALUES (?, 'guest', 'legacy-guest', ?, ?)",(hashlib.sha256(token.encode()).hexdigest(),"old-csrf-hash",int(time.time())+3600))
        db.commit();db.close()
        upgraded=Store(legacy_path)
        resolved=upgraded.resolve_session(token)
        self.assertTrue(resolved["csrf"])
        self.assertTrue(upgraded.validate_csrf(token,resolved["csrf"]))


if __name__ == "__main__":
    unittest.main()
