"""ProfitPilot HTTP API and static server — production-ready."""

import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import threading
import time
from decimal import Decimal, ROUND_CEILING
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request, urlopen

from .calculations import allocate_shared_expense, calculate_product, money, percent
from . import ai
from .ratelimit import auth_limiter, reset_request_limiter, api_limiter

CURRENCIES = {"USD", "EUR", "GBP", "ILS", "JOD", "SAR", "AED", "EGP"}
MAX_BODY = 256 * 1024
TRUST_PROXY = os.environ.get("DECISION_LAB_TRUST_PROXY") == "1"


def _client_ip(handler):
    """Return the real client IP, honouring X-Forwarded-For when behind a trusted proxy."""
    if TRUST_PROXY:
        forwarded = handler.headers.get("X-Forwarded-For", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return handler.client_address[0]


def _jsonable(value):
    if isinstance(value, Decimal):
        return format(value, ".2f")
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def normalize_product(data):
    if not isinstance(data, dict):
        raise ValueError("product details are required")
    name = str(data.get("name", "")).strip()
    currency = str(data.get("currency", "USD")).upper()
    if not name or len(name) > 120:
        raise ValueError("product name is required (up to 120 characters)")
    if currency not in CURRENCIES:
        raise ValueError("choose a supported currency")
    quantity = data.get("quantity")
    if isinstance(quantity, str) and quantity.isdigit():
        quantity = int(quantity)
    if isinstance(quantity, bool) or not isinstance(quantity, int) or not 1 <= quantity <= 1_000_000:
        raise ValueError("quantity must be a whole number greater than zero")
    unit_cost = money(data.get("unit_cost"), "unit purchase cost")
    selling_price_raw = data.get("selling_price")
    if selling_price_raw in (None, ""):
        selling_price_raw = 0
    selling_price = money(selling_price_raw, "selling price")
    discount_raw = data.get("discount_percent")
    if discount_raw in (None, ""):
        discount_raw = 0
    discount = percent(discount_raw, "discount")
    expenses = data.get("expenses", [])
    if not isinstance(expenses, list) or len(expenses) > 100:
        raise ValueError("expenses must be a list of up to 100 items")
    cleaned_expenses = []
    for expense in expenses:
        if not isinstance(expense, dict):
            raise ValueError("each expense needs a name and amount")
        amount_raw = expense.get("amount")
        if amount_raw in (None, ""):
            amount_raw = 0
        amount = money(amount_raw, "expense amount")
        allocation = expense.get("allocation", "direct")
        basis = expense.get("basis")
        if allocation == "shared" and basis not in ("quantity", "purchase_value", "weight"):
            raise ValueError("choose an allocation basis for each shared expense")
        if allocation not in ("shared", "direct"):
            raise ValueError("expense allocation must be direct or shared")
        cleaned_expenses.append({
            "name": str(expense.get("name", "Expense")).strip()[:80] or "Expense",
            "amount": format(amount, ".2f"), "allocation": allocation,
            "basis": basis if allocation == "shared" else None,
            "weight": str(expense.get("weight", "")) if basis == "weight" else None,
            "note": str(expense.get("note", ""))[:240],
        })
    target_basis = data.get("target_basis", "margin")
    if target_basis not in ("margin", "markup"):
        raise ValueError("target basis must be margin or markup")
    target_profit_amount_raw = data.get("target_profit_amount")
    if target_profit_amount_raw in (None, ""):
        target_profit_amount = None
    else:
        target_profit_amount = format(money(target_profit_amount_raw, "target profit"), ".2f")

    target_profit_percent_raw = data.get("target_profit_percent")
    if target_profit_percent_raw in (None, ""):
        target_profit_percent = None
    else:
        target_profit_percent = str(percent(target_profit_percent_raw, "target profit percentage", maximum=Decimal("10000")))

    return {"name": name, "category": str(data.get("category", ""))[:80],
            "currency": currency, "unit_cost": format(unit_cost, ".2f"),
            "quantity": quantity, "selling_price": format(selling_price, ".2f"),
            "discount_percent": str(discount), "expenses": cleaned_expenses,
            "target_profit_amount": target_profit_amount,
            "target_profit_percent": target_profit_percent,
            "target_basis": target_basis,
            "weight": str(data.get("weight", ""))[:40]}



def result_for(product, basis=None):
    expenses = [item["amount"] for item in product.get("expenses", [])]
    return calculate_product(product["unit_cost"], product["quantity"], expenses,
                             product["selling_price"], product["discount_percent"],
                             product.get("target_profit_amount"), product.get("target_profit_percent"),
                             basis or product.get("target_basis", "margin"))


def effective_product(store, owner, product):
    """Add direct expenses and reconciled shared allocations for one item."""
    result = dict(product)
    expenses = list(product.get("expenses", []))
    allocations = []
    for shared in store.list_shared_expenses(owner):
        ids = shared.get("product_ids", [])
        if product["id"] not in ids:
            continue
        participants = [store.get_product(owner, product_id) for product_id in ids]
        participants = [p for p in participants if p]
        basis_products = [{"id": p["id"], "quantity": p["quantity"],
                           "purchase_value": str(Decimal(p["unit_cost"]) * int(p["quantity"])),
                           "weight": p.get("weight") or "0"} for p in participants]
        shares = allocate_shared_expense(shared["amount"], basis_products, shared["basis"])
        share = shares.get(product["id"], Decimal("0.00"))
        if share:
            expenses.append({"name": shared["name"], "amount": format(share, ".2f"), "allocation": "shared", "basis": shared["basis"]})
            allocations.append({"id": shared["id"], "name": shared["name"], "basis": shared["basis"], "amount": format(share, ".2f")})
    result["expenses"] = expenses
    result["shared_allocations"] = allocations
    return result


def make_handler(store, web_root):
    web_root = Path(web_root).resolve()
    oauth_attempts = {}
    oauth_lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        server_version = "CostPilot/1"
        sys_version = ""

        def log_message(self, fmt, *args):
            # Keep local console logs concise and avoid reflecting user data.
            pass

        def end_headers(self):
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "same-origin")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; script-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def _send(self, status, data=None, *, cookie=None, content_type="application/json; charset=utf-8"):
            if content_type.startswith("application/json"):
                body = json.dumps(_jsonable(data), ensure_ascii=False, allow_nan=False).encode("utf-8")
            else:
                body = data or b""
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            if cookie:
                secure = "; Secure" if os.environ.get("DECISION_LAB_SECURE_COOKIE") == "1" else ""
                self.send_header("Set-Cookie", f"decision_session={cookie}; HttpOnly; SameSite=Lax; Path=/; Max-Age=2592000{secure}")
            self.end_headers()
            self.wfile.write(body)

        def _body(self):
            length = int(self.headers.get("Content-Length", "0"))
            if length < 0 or length > MAX_BODY:
                raise ValueError("request is too large")
            if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
                raise ValueError("request must use JSON")
            raw = self.rfile.read(length)
            try:
                return json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                raise ValueError("request JSON is invalid")

        def _token(self):
            for part in self.headers.get("Cookie", "").split(";"):
                key, sep, value = part.strip().partition("=")
                if sep and key == "decision_session":
                    return value
            return None

        def _session(self, create=False):
            token = self._token()
            session = store.resolve_session(token) if token else None
            if not session and create:
                fresh = store.create_guest_session()
                return fresh["owner"], fresh, fresh["token"]
            if not session:
                return None, None, None
            return session["owner"], session, token

        def _redirect(self, location, *, session_cookie=None, oauth_state_cookie=None, status=303):
            secure = "; Secure" if os.environ.get("DECISION_LAB_SECURE_COOKIE") == "1" else ""
            self.send_response(status)
            self.send_header("Location", location)
            self.send_header("Cache-Control", "no-store")
            if session_cookie:
                self.send_header("Set-Cookie", f"decision_session={session_cookie}; HttpOnly; SameSite=Lax; Path=/; Max-Age=2592000{secure}")
            if oauth_state_cookie is not None:
                max_age = 600 if oauth_state_cookie else 0
                self.send_header("Set-Cookie", f"decision_google_oauth={oauth_state_cookie}; HttpOnly; SameSite=Lax; Path=/auth/google/callback; Max-Age={max_age}{secure}")
            self.send_header("Content-Length", "0")
            self.end_headers()

        def _cookie(self, name):
            for part in self.headers.get("Cookie", "").split(";"):
                key, sep, value = part.strip().partition("=")
                if sep and key == name:
                    return value
            return None

        def _google_start(self, query):
            client_id = os.environ.get("GOOGLE_CLIENT_ID")
            client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
            redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI")
            if not (client_id and client_secret and redirect_uri):
                self._redirect("/?auth_error=google_unavailable")
                return
            state = secrets.token_urlsafe(32)
            verifier = secrets.token_urlsafe(48)
            challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
            now = int(time.time())
            attempt = {"verifier": verifier, "guest_token": self._token(),
                       "transfer_guest": parse_qs(query).get("transfer_guest", ["false"])[0] == "true",
                       "expires": now + 600}
            with oauth_lock:
                for old in [key for key, value in oauth_attempts.items() if value["expires"] < now]:
                    oauth_attempts.pop(old, None)
                if len(oauth_attempts) >= 1000:
                    oauth_attempts.pop(next(iter(oauth_attempts)))
                oauth_attempts[state] = attempt
            params = {"client_id": client_id, "redirect_uri": redirect_uri, "response_type": "code",
                      "scope": "openid email profile", "state": state, "code_challenge": challenge,
                      "code_challenge_method": "S256", "prompt": "select_account"}
            self._redirect("https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params),
                           oauth_state_cookie=state, status=302)

        def _google_callback(self, query):
            params = parse_qs(query)
            state = params.get("state", [""])[0]
            state_cookie = self._cookie("decision_google_oauth") or ""
            with oauth_lock:
                attempt = oauth_attempts.pop(state, None) if state and hmac.compare_digest(state, state_cookie) else None
            if not attempt or attempt["expires"] < int(time.time()):
                self._redirect("/?auth_error=google_state", oauth_state_cookie="")
                return
            if params.get("error"):
                self._redirect("/?auth_error=google_cancelled", oauth_state_cookie="")
                return
            try:
                code = params.get("code", [""])[0]
                if not code:
                    raise ValueError("missing authorization code")
                token_body = urlencode({"code": code, "client_id": os.environ["GOOGLE_CLIENT_ID"],
                    "client_secret": os.environ["GOOGLE_CLIENT_SECRET"], "redirect_uri": os.environ["GOOGLE_REDIRECT_URI"],
                    "grant_type": "authorization_code", "code_verifier": attempt["verifier"]}).encode()
                token_request = Request("https://oauth2.googleapis.com/token", data=token_body,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
                with urlopen(token_request, timeout=12) as response:
                    tokens = json.loads(response.read(64 * 1024).decode("utf-8"))
                access_token = tokens.get("access_token")
                if not access_token:
                    raise ValueError("Google did not return an access token")
                profile_request = Request("https://openidconnect.googleapis.com/v1/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"})
                with urlopen(profile_request, timeout=12) as response:
                    profile = json.loads(response.read(64 * 1024).decode("utf-8"))
                if profile.get("email_verified") not in (True, "true"):
                    raise ValueError("Google email is not verified")
                _, session = store.login_with_google(profile.get("email", ""), profile.get("sub", ""),
                    attempt["guest_token"], attempt["transfer_guest"])
                self._redirect("/?auth_success=google", session_cookie=session["token"], oauth_state_cookie="")
            except Exception:
                self._redirect("/?auth_error=google_failed", oauth_state_cookie="")

        def _require_csrf(self, token):
            if not store.validate_csrf(token, self.headers.get("X-CSRF-Token")):
                raise PermissionError("session check failed; refresh and try again")

        def _product_path(self, path):
            match = re.fullmatch(r"/api/products/([\w-]+)(?:/(calculate|scenarios|suggestions|ai-review))?", path)
            return match.groups() if match else (None, None)

        def do_GET(self):
            parsed = urlsplit(self.path)
            path = parsed.path
            try:
                # ── Health check (no auth required) ──────────────────────────
                if path == "/health":
                    self._send(200, {"status": "ok", "time": int(time.time())}); return

                if path == "/auth/google/start":
                    self._google_start(parsed.query); return
                if path == "/auth/google/callback":
                    self._google_callback(parsed.query); return
                if path == "/api/session":
                    owner, session, new_cookie = self._session(create=True)
                    csrf = session.get("csrf")
                    profile = None
                    if owner["type"] == "user":
                        with store._connect() as db:
                            row = db.fetchone(
                                "SELECT email FROM users WHERE id=" + ("%s" if store._USE_PG else "?"),
                                (owner["id"],),
                            )
                            profile = {"email": row["email"]} if row else None
                    self._send(200, {"owner_type": owner["type"], "profile": profile,
                                     "csrf": csrf}, cookie=new_cookie)
                    return
                if path == "/api/ai/status":
                    self._send(200, {"available": ai.configured()}); return
                owner, _, _ = self._session()
                if path.startswith("/api/") and not owner:
                    self._send(401, {"error": "session expired"}); return

                # ── General API rate limit ────────────────────────────────────
                ip = _client_ip(self)
                if api_limiter.is_limited(ip):
                    self._send(429, {"error": "too many requests, slow down"}); return

                if path == "/api/products":
                    products = store.list_products(owner)
                    for product in products:
                        effective = effective_product(store, owner, product)
                        product["shared_allocations"] = effective["shared_allocations"]
                        product["result"] = _jsonable(result_for(effective))
                    self._send(200, products); return
                if path == "/api/history":
                    self._send(200, store.list_history(owner)); return
                if path == "/api/shared-expenses":
                    self._send(200, store.list_shared_expenses(owner)); return
                product_id, suffix = self._product_path(path)
                if product_id and suffix == "scenarios":
                    product = store.get_product(owner, product_id)
                    if not product:
                        raise LookupError("product not found")
                    effective = effective_product(store, owner, product)
                    scenarios = store.list_scenarios(owner, product_id)
                    for s in scenarios:
                        s["result"] = _jsonable(result_for({**effective, **s}))
                    self._send(200, scenarios); return

                if path.startswith("/api/"):
                    self._send(404, {"error": "not found"}); return
                asset = "index.html" if path == "/" else path.lstrip("/")
                candidate = (web_root / asset).resolve()
                if candidate.parent != web_root or not candidate.is_file() or candidate.name not in ("index.html", "app.js", "styles.css"):
                    self._send(404, b"Not found", content_type="text/plain; charset=utf-8"); return
                types = {"index.html": "text/html; charset=utf-8", "app.js": "text/javascript; charset=utf-8", "styles.css": "text/css; charset=utf-8"}
                self._send(200, candidate.read_bytes(), content_type=types[candidate.name])
            except Exception:
                self._send(500, {"error": "request could not be completed"})

        def do_POST(self):
            self._mutate("POST")

        def do_PUT(self):
            self._mutate("PUT")

        def do_DELETE(self):
            self._mutate("DELETE")

        def _mutate(self, method):
            path = urlsplit(self.path).path
            try:
                payload = self._body() if method != "DELETE" else {}
                ip = _client_ip(self)

                # ── Auth endpoints with rate limiting ─────────────────────────
                if path == "/api/auth/signup" and method == "POST":
                    if auth_limiter.is_limited(f"{ip}:signup"):
                        self._send(429, {"error": "too many attempts, try again later"}); return
                    owner, _, token = self._session()
                    if not owner:
                        fresh = store.create_guest_session(); owner, token = fresh["owner"], fresh["token"]
                    if owner["type"] != "guest":
                        raise PermissionError("sign out before creating a new account")
                    self._require_csrf(token)
                    user, session = store.register(str(payload.get("email", "")), str(payload.get("password", "")), token,
                                                   transfer_guest=payload.get("transfer_guest") is True)
                    auth_limiter.reset(f"{ip}:signup")
                    self._send(201, {"profile": {"email": user["email"]}, "csrf": session["csrf"]}, cookie=session["token"]); return

                if path == "/api/auth/login" and method == "POST":
                    if auth_limiter.is_limited(f"{ip}:login"):
                        self._send(429, {"error": "too many login attempts, try again in 10 minutes"}); return
                    _, _, token = self._session()
                    self._require_csrf(token)
                    user, session = store.login(str(payload.get("email", "")), str(payload.get("password", "")))
                    auth_limiter.reset(f"{ip}:login")
                    self._send(200, {"profile": {"email": user["email"]}, "csrf": session["csrf"]}, cookie=session["token"]); return

                # ── Password reset — request ───────────────────────────────────
                if path == "/api/auth/request-password-reset" and method == "POST":
                    if reset_request_limiter.is_limited(f"{ip}:reset"):
                        self._send(429, {"error": "too many requests, try again later"}); return
                    _, _, token = self._session()
                    self._require_csrf(token)
                    email = str(payload.get("email", "")).strip().lower()
                    try:
                        from . import email as email_module
                        reset_token = store.create_password_reset_token(email)
                        if email_module.configured():
                            email_module.send_password_reset(email, reset_token)
                        else:
                            # Development mode: print the reset link to server console
                            base = os.environ.get("APP_BASE_URL", "http://127.0.0.1:8765")
                            print(f"[dev] Password reset link for {email}: {base}/reset-password?token={reset_token}")
                    except LookupError:
                        pass  # Do NOT reveal whether the email is registered
                    # Always return success to prevent email enumeration
                    self._send(200, {"message": "if that email is registered, a reset link has been sent"}); return

                # ── Password reset — confirm ───────────────────────────────────
                if path == "/api/auth/reset-password" and method == "POST":
                    _, _, token = self._session()
                    self._require_csrf(token)
                    reset_token = str(payload.get("token", ""))
                    new_password = str(payload.get("password", ""))
                    user = store.consume_password_reset_token(reset_token, new_password)
                    # Log user in with a fresh session after successful reset
                    fresh_session = store._new_session_public({"type": "user", "id": user["id"]})
                    self._send(200, {"profile": {"email": user["email"]}, "csrf": fresh_session["csrf"]},
                               cookie=fresh_session["token"]); return

                if path == "/api/session" and method == "POST" and payload.get("action") == "logout":
                    _, _, token = self._session(); self._require_csrf(token); store.logout(token)
                    fresh = store.create_guest_session()
                    self._send(200, {"owner_type": "guest", "csrf": fresh["csrf"]}, cookie=fresh["token"]); return

                owner, _, token = self._session()
                if not owner:
                    self._send(401, {"error": "session expired"}); return
                self._require_csrf(token)

                # ── General API rate limit ────────────────────────────────────
                if api_limiter.is_limited(ip):
                    self._send(429, {"error": "too many requests, slow down"}); return
                if path == "/api/products" and method == "POST":
                    product = store.save_product(owner, normalize_product(payload))
                    self._send(201, {**product, "result": _jsonable(result_for(product))}); return
                product_id, suffix = self._product_path(path)
                if product_id and not suffix and method == "PUT":
                    normalized = normalize_product(payload)
                    previous = store.get_product(owner, product_id)
                    if not previous:
                        raise LookupError("product not found")
                    if previous["currency"] != normalized["currency"] and any(
                            product_id in group.get("product_ids", []) for group in store.list_shared_expenses(owner)):
                        raise ValueError("remove shared expenses involving this product before changing its currency")
                    product = store.save_product(owner, {**normalized, "id": product_id})
                    self._send(200, {**product, "result": _jsonable(result_for(product))}); return
                if product_id and not suffix and method == "DELETE":
                    if not store.delete_product(owner, product_id):
                        raise LookupError("product not found")
                    self._send(200, {"deleted": True}); return
                if product_id and suffix == "calculate" and method == "POST":
                    saved = store.get_product(owner, product_id)
                    if not saved:
                        raise LookupError("product not found")
                    effective = effective_product(store, owner, saved)
                    inputs = normalize_product({**saved, **(payload.get("product", {}) if isinstance(payload, dict) else {})})
                    inputs["expenses"] = effective["expenses"]
                    basis = payload.get("target_basis", inputs.get("target_basis"))
                    result = result_for(inputs, basis)
                    history = store.add_history(owner, product_id, {"inputs": inputs, "result": _jsonable(result)})
                    self._send(200, {"result": _jsonable(result), "history": history}); return
                if product_id and suffix == "suggestions" and method == "POST":
                    saved = store.get_product(owner, product_id)
                    if not saved:
                        raise LookupError("product not found")
                    effective = effective_product(store, owner, saved)
                    current = result_for(effective)
                    if current["break_even_unit_price"] is None:
                        self._send(200, {"available": False, "reason_code": "full_discount", "reason": "break-even price cannot be reached with a full discount"}); return
                    candidate = (current["break_even_unit_price"] * Decimal("1.10")).quantize(Decimal("0.01"), rounding=ROUND_CEILING)
                    if candidate <= Decimal(saved["selling_price"]):
                        self._send(200, {"available": False, "reason_code": "price_already_high", "reason": "current original price is already at or above this comparison price"}); return
                    proposed = {**effective, "selling_price": format(candidate, ".2f")}
                    outcome = result_for(proposed)
                    self._send(200, {"available": True, "suggested_price": format(candidate, ".2f"),
                                     "current_result": _jsonable(current), "result": _jsonable(outcome),
                                     "profit_change": format(outcome["profit"] - current["profit"], ".2f"),
                                     "quantity_assumption": saved["quantity"],
                                     "discount_assumption": saved["discount_percent"]}); return
                if product_id and suffix == "ai-review" and method == "POST":
                    saved = store.get_product(owner, product_id)
                    if not saved:
                        raise LookupError("product not found")
                    if not ai.configured():
                        self._send(503, {"error": "AI review is not configured"}); return
                    effective = effective_product(store, owner, saved)
                    result = result_for(effective)
                    summary = {"currency": saved["currency"], "unit_cost": saved["unit_cost"],
                               "quantity": saved["quantity"], "expenses": [e["amount"] for e in effective["expenses"]],
                               "discount_percent": saved["discount_percent"], "selling_price": saved["selling_price"],
                               "final_unit_price": format(result["final_unit_price"], ".2f"),
                               "total_cost": format(result["total_cost"], ".2f"), "revenue": format(result["revenue"], ".2f"),
                               "profit": format(result["profit"], ".2f"),
                               "margin_percent": format(result["margin_percent"], ".2f") if result["margin_percent"] is not None else None,
                               "break_even_unit_price": format(result["break_even_unit_price"], ".2f") if result["break_even_unit_price"] is not None else None}
                    language = payload.get("language", "en") if isinstance(payload, dict) else "en"
                    if language not in ("en", "ar"):
                        language = "en"
                    try:
                        text = ai.review(summary, language)
                    except Exception:
                        self._send(502, {"error": "AI review could not be completed. Check the server configuration."}); return
                    self._send(200, {"review": text}); return
                if product_id and suffix == "scenarios" and method == "POST":
                    saved = store.get_product(owner, product_id)
                    if not saved:
                        raise LookupError("product not found")
                    sc_discount_raw = payload.get("discount_percent")
                    if sc_discount_raw in (None, ""):
                        sc_discount_raw = 0
                    scenario = {"name": str(payload.get("name", "")).strip()[:80],
                                "selling_price": format(money(payload.get("selling_price"), "selling price"), ".2f"),
                                "discount_percent": str(percent(sc_discount_raw, "discount")),
                                "target_basis": payload.get("target_basis", saved.get("target_basis", "margin"))}

                    if not scenario["name"]:
                        raise ValueError("scenario name is required")
                    effective = effective_product(store, owner, saved)
                    scenario["result"] = _jsonable(result_for({**effective, **scenario}))
                    self._send(201, store.save_scenario(owner, product_id, scenario)); return
                if path.startswith("/api/scenarios/") and method == "DELETE":
                    scenario_id = path.rsplit("/", 1)[-1]
                    if not store.delete_scenario(owner, scenario_id):
                        raise LookupError("scenario not found")
                    self._send(200, {"deleted": True}); return
                if path == "/api/allocations" and method == "POST":
                    allocation = allocate_shared_expense(payload.get("amount"), payload.get("products", []), payload.get("basis"))
                    self._send(200, allocation); return
                if path == "/api/shared-expenses" and method == "POST":
                    name = str(payload.get("name", "")).strip()
                    amount = money(payload.get("amount"), "shared expense")
                    basis, ids = payload.get("basis"), payload.get("product_ids")
                    if not name or len(name) > 80 or not isinstance(ids, list) or len(set(ids)) < 2:
                        raise ValueError("choose a name and at least two products")
                    products = [store.get_product(owner, product_id) for product_id in ids]
                    if any(product is None for product in products):
                        raise LookupError("one or more products were not found")
                    if len({product["currency"] for product in products}) != 1:
                        raise ValueError("shared expenses can only be allocated between products in the same currency")
                    basis_products = [{"id": p["id"], "quantity": p["quantity"],
                                       "purchase_value": str(Decimal(p["unit_cost"]) * int(p["quantity"])),
                                       "weight": p.get("weight") or "0"} for p in products]
                    allocate_shared_expense(amount, basis_products, basis)
                    saved = store.save_shared_expense(owner, {"name": name, "amount": format(amount, ".2f"), "basis": basis, "product_ids": ids})
                    self._send(201, saved); return
                if path.startswith("/api/shared-expenses/") and method == "DELETE":
                    if not store.delete_shared_expense(owner, path.rsplit("/", 1)[-1]):
                        raise LookupError("shared expense not found")
                    self._send(200, {"deleted": True}); return
                if path == "/api/preview" and method == "POST":
                    product = normalize_product(payload)
                    result = _jsonable(result_for(product))
                    history = store.add_history(owner, None, {"inputs": product, "result": result})
                    self._send(200, {"result": result, "history": history}); return
                if path.startswith("/api/scenarios/") and method == "PUT":
                    scenario_id = path.rsplit("/", 1)[-1]
                    existing = store.get_scenario(owner, scenario_id)
                    if not existing:
                        raise LookupError("scenario not found")
                    product = store.get_product(owner, existing["product_id"])
                    if not product:
                        raise LookupError("product not found")
                    sc_discount_raw = payload.get("discount_percent")
                    if sc_discount_raw in (None, ""):
                        sc_discount_raw = 0
                    scenario = {"id": scenario_id, "name": str(payload.get("name", "")).strip()[:80],
                                "selling_price": format(money(payload.get("selling_price"), "selling price"), ".2f"),
                                "discount_percent": str(percent(sc_discount_raw, "discount")),
                                "target_basis": payload.get("target_basis", product.get("target_basis", "margin"))}

                    if not scenario["name"]:
                        raise ValueError("scenario name is required")
                    effective = effective_product(store, owner, product)
                    scenario["result"] = _jsonable(result_for({**effective, **scenario}))
                    self._send(200, store.save_scenario(owner, existing["product_id"], scenario)); return
                self._send(404, {"error": "not found"})
            except PermissionError as error:
                self._send(403, {"error": str(error)})
            except LookupError as error:
                self._send(404, {"error": str(error)})
            except (ValueError, TypeError, KeyError) as error:
                self._send(400, {"error": str(error)[:200]})
            except Exception as e:
                import traceback
                traceback.print_exc()
                self._send(500, {"error": str(e)})

    return Handler


def main():
    from http.server import ThreadingHTTPServer
    import sys

    host = os.environ.get("DECISION_LAB_HOST", os.environ.get("HOST", "127.0.0.1"))
    port = int(os.environ.get("PORT", os.environ.get("DECISION_LAB_PORT", "8765")))

    from .store import Store, _USE_PG, DATABASE_URL

    if _USE_PG:
        store = Store()  # PostgreSQL — no file path needed
        print(f"[profitpilot] Database: PostgreSQL ({DATABASE_URL.split('@')[-1]})")
    else:
        data_dir = Path(os.environ.get("DECISION_LAB_DATA", str(Path.cwd() / ".decision-lab"))).expanduser()
        store = Store(data_dir / "decision-lab.sqlite3")
        print(f"[profitpilot] Database: SQLite ({data_dir / 'decision-lab.sqlite3'})")

    server = ThreadingHTTPServer(
        (host, port),
        make_handler(store, Path(__file__).resolve().parent.parent / "web"),
    )
    print(f"[profitpilot] Listening on http://{host}:{port}/")
    print(f"[profitpilot] Health check: http://{host}:{port}/health")
    if TRUST_PROXY:
        print("[profitpilot] Trusted proxy mode: ON (X-Forwarded-For honoured)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[profitpilot] Shutting down …")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
