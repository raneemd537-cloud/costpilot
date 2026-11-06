import os
import sys
import traceback
from pathlib import Path
from io import BytesIO
from email.message import Message
from http import HTTPStatus

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path.home() / ".profitpilot-data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

os.environ["DECISION_LAB_DATA"] = str(DATA_DIR)
os.environ["DECISION_LAB_SECURE_COOKIE"] = "1"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.store import Store
from app.server import make_handler

store = Store(DATA_DIR / "decision-lab.sqlite3")
Handler = make_handler(store, BASE_DIR / "web")


class WSGIHandler(Handler):
    def send_response(self, code, message=None):
        self._status = code
        self._response_headers = []

    def send_header(self, keyword, value):
        self._response_headers.append((keyword, str(value)))

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; style-src 'self' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; script-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; base-uri 'none'; "
            "frame-ancestors 'none'; form-action 'self'"
        )
        self.send_header("Cache-Control", "no-store")


def application(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET").upper()
    handler = object.__new__(WSGIHandler)

    handler.command = method

    handler.client_address = (
        environ.get("REMOTE_ADDR", "127.0.0.1"),
        int(environ.get("REMOTE_PORT", "0") or 0),
    )

    handler.path = environ.get("PATH_INFO", "/")
    query = environ.get("QUERY_STRING", "")
    if query:
        handler.path += "?" + query

    handler.headers = Message()
    for key, value in environ.items():
        if key.startswith("HTTP_"):
            name = key[5:].replace("_", "-")
            handler.headers[name] = value
    for key in ("CONTENT_TYPE", "CONTENT_LENGTH"):
        if environ.get(key):
            handler.headers[key.replace("_", "-")] = environ[key]

    handler.rfile = environ.get("wsgi.input", BytesIO())
    handler.wfile = BytesIO()
    handler._response_headers = []
    handler._status = 500

    try:
        dispatch = {
            "GET": handler.do_GET,
            "HEAD": handler.do_GET,
            "POST": handler.do_POST,
            "PUT": handler.do_PUT,
            "DELETE": handler.do_DELETE,
        }
        action = dispatch.get(method)

        if action:
            action()
        else:
            handler.send_response(405)
            handler.send_header("Content-Type", "text/plain; charset=utf-8")
            handler.send_header("Content-Length", "0")
            handler.end_headers()

        body = handler.wfile.getvalue()
        if method == "HEAD":
            body = b""

        status_text = HTTPStatus(handler._status).phrase
        start_response(
            f"{handler._status} {status_text}",
            handler._response_headers
        )
        return [body]

    except Exception:
        traceback.print_exc()
        body = b'{"error":"request could not be completed"}'
        start_response(
            "500 Internal Server Error",
            [
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Length", str(len(body))),
                ("Cache-Control", "no-store"),
            ],
        )
        return [body]
