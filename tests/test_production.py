import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from app.server import make_handler
from app.store import Store
from app.ratelimit import RateLimiter, auth_limiter, reset_request_limiter, api_limiter


class ProductionReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.sqlite3"
        self.store = Store(self.db_path)
        self.web_root = Path(self.temp_dir.name) / "web"
        self.web_root.mkdir()
        (self.web_root / "index.html").write_text("<!doctype html><title>CostPilot</title>", encoding="utf-8")
        self.handler_cls = make_handler(self.store, self.web_root)

        # Clear rate limiters
        auth_limiter.purge_expired()
        with auth_limiter._lock:
            auth_limiter._buckets.clear()
        with reset_request_limiter._lock:
            reset_request_limiter._buckets.clear()
        with api_limiter._lock:
            api_limiter._buckets.clear()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_rate_limiter_logic(self):
        limiter = RateLimiter(max_calls=3, window_seconds=10)
        self.assertFalse(limiter.is_limited("user1"))
        self.assertFalse(limiter.is_limited("user1"))
        self.assertFalse(limiter.is_limited("user1"))
        self.assertTrue(limiter.is_limited("user1"))
        self.assertFalse(limiter.is_limited("user2"))
        limiter.reset("user1")
        self.assertFalse(limiter.is_limited("user1"))

    def test_password_reset_store_workflow(self):
        # Register a user
        user, _ = self.store.register("owner@example.com", "SuperSecurePassword123!")

        # Request reset token
        token = self.store.create_password_reset_token("owner@example.com")
        self.assertTrue(token)

        # Non-existent user should raise LookupError
        with self.assertRaises(LookupError):
            self.store.create_password_reset_token("unknown@example.com")

        # Weak password should raise ValueError
        with self.assertRaises(ValueError):
            self.store.consume_password_reset_token(token, "short")

        # Successful reset
        updated_user = self.store.consume_password_reset_token(token, "NewSuperPassword456!")
        self.assertEqual(updated_user["id"], user["id"])

        # Token cannot be reused
        with self.assertRaises(ValueError):
            self.store.consume_password_reset_token(token, "AnotherPassword789!")

        # Login with old password fails
        with self.assertRaises(ValueError):
            self.store.login("owner@example.com", "SuperSecurePassword123!")

        # Login with new password succeeds
        logged_in_user, session = self.store.login("owner@example.com", "NewSuperPassword456!")
        self.assertEqual(logged_in_user["id"], user["id"])
        self.assertTrue(session["token"])

    def test_health_endpoint(self):
        import io
        from unittest.mock import MagicMock

        class MockSocket:
            def __init__(self, data=b""):
                self.rfile = io.BytesIO(data)
                self.wfile = io.BytesIO()

            def makefile(self, mode, *args, **kwargs):
                if "b" in mode:
                    return self.rfile if "r" in mode else self.wfile
                raise NotImplementedError

            def sendall(self, data):
                self.wfile.write(data)

        # Send GET /health
        raw_request = b"GET /health HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n"
        sock = MockSocket(raw_request)
        handler = self.handler_cls(sock, ("127.0.0.1", 12345), MagicMock())
        output = sock.wfile.getvalue().decode("utf-8")
        self.assertIn("200 OK", output)
        self.assertIn('"status": "ok"', output)


if __name__ == "__main__":
    unittest.main()
