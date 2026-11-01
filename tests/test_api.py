import json
import os
import http.client
from urllib.parse import parse_qs, urlsplit
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

from app.server import make_handler
from app.store import Store


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.store = Store(Path(cls.tmp.name) / "api.db")
        cls.http = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(cls.store, Path(__file__).parents[1] / "web"))
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.http.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.thread.join()
        cls.tmp.cleanup()

    def setUp(self):
        self.cookie = None
        self.csrf = None
        self.call("GET", "/api/session")

    def call(self, method, path, data=None, headers=None, cookie=None, csrf=None):
        headers = dict(headers or {})
        if data is not None:
            headers["Content-Type"] = "application/json"
        if cookie or self.cookie:
            headers["Cookie"] = cookie or self.cookie
        chosen_csrf = csrf if csrf is not None else self.csrf
        if chosen_csrf is not None:
            headers["X-CSRF-Token"] = chosen_csrf
        payload = json.dumps(data).encode() if data is not None else None
        request = Request(self.base + path, data=payload, method=method, headers=headers)
        try:
            response = urlopen(request)
        except HTTPError as error:
            response = error
        if response.headers.get("Set-Cookie"):
            self.cookie = response.headers["Set-Cookie"].split(";", 1)[0]
        body = response.read()
        result = json.loads(body) if body and response.headers.get("Content-Type", "").startswith("application/json") else body
        if isinstance(result, dict) and result.get("csrf"):
            self.csrf = result["csrf"]
        return response.status, result, response.headers

    def raw_get(self, path, cookie=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.http.server_port)
        headers = {"Cookie": cookie or self.cookie} if cookie or self.cookie else {}
        conn.request("GET", path, headers=headers)
        response = conn.getresponse()
        result = response.status, response.read(), response.getheaders()
        conn.close()
        return result

    def test_google_oauth_redirect_uses_pkce_and_bound_state_cookie(self):
        config = {"GOOGLE_CLIENT_ID": "client.apps.googleusercontent.com", "GOOGLE_CLIENT_SECRET": "secret",
                  "GOOGLE_REDIRECT_URI": self.base + "/auth/google/callback"}
        with patch.dict(os.environ, config):
            status, _, headers = self.raw_get("/auth/google/start?transfer_guest=true")
        header_map = dict(headers)
        query = parse_qs(urlsplit(header_map["Location"]).query)
        self.assertEqual(status, 302)
        self.assertEqual(query["response_type"], ["code"])
        self.assertEqual(query["code_challenge_method"], ["S256"])
        self.assertTrue(query["state"][0])
        self.assertIn("decision_google_oauth=", header_map["Set-Cookie"])

    def test_google_oauth_callback_rejects_state_mismatch(self):
        config = {"GOOGLE_CLIENT_ID": "client.apps.googleusercontent.com", "GOOGLE_CLIENT_SECRET": "secret",
                  "GOOGLE_REDIRECT_URI": self.base + "/auth/google/callback"}
        with patch.dict(os.environ, config):
            _, _, headers = self.raw_get("/auth/google/start")
            oauth_cookie = next(value.split(";", 1)[0] for name, value in headers if name.lower() == "set-cookie")
            status, _, callback_headers = self.raw_get("/auth/google/callback?state=wrong&code=nope",
                                                        cookie=f"{self.cookie}; {oauth_cookie}")
        self.assertEqual(status, 303)
        self.assertIn("auth_error=google_state", dict(callback_headers)["Location"])

    def test_google_oauth_accepts_only_verified_google_email(self):
        class Response:
            def __init__(self, payload): self.payload = json.dumps(payload).encode()
            def __enter__(self): return self
            def __exit__(self, *_): return None
            def read(self, _limit): return self.payload
        config = {"GOOGLE_CLIENT_ID": "client.apps.googleusercontent.com", "GOOGLE_CLIENT_SECRET": "secret",
                  "GOOGLE_REDIRECT_URI": self.base + "/auth/google/callback"}
        with patch.dict(os.environ, config):
            _, _, start_headers = self.raw_get("/auth/google/start")
            state_cookie = next(value.split(";", 1)[0] for name, value in start_headers if name.lower() == "set-cookie")
            state = state_cookie.split("=", 1)[1]
            with patch("app.server.urlopen", side_effect=[Response({"access_token": "access"}),
                    Response({"sub": "google-user-verified", "email": "verified@example.test", "email_verified": True})]):
                status, _, callback_headers = self.raw_get(f"/auth/google/callback?state={state}&code=auth-code",
                    cookie=f"{self.cookie}; {state_cookie}")
        self.assertEqual(status, 303)
        self.assertIn("auth_success=google", dict(callback_headers)["Location"])
        session_cookie = next(value.split(";", 1)[0] for name, value in callback_headers if name.lower() == "set-cookie" and value.startswith("decision_session="))
        _, session, _ = self.call("GET", "/api/session", cookie=session_cookie)
        self.assertEqual(session["profile"]["email"], "verified@example.test")

    def test_google_oauth_rejects_unverified_email(self):
        class Response:
            def __init__(self, payload): self.payload = json.dumps(payload).encode()
            def __enter__(self): return self
            def __exit__(self, *_): return None
            def read(self, _limit): return self.payload
        config = {"GOOGLE_CLIENT_ID": "client.apps.googleusercontent.com", "GOOGLE_CLIENT_SECRET": "secret",
                  "GOOGLE_REDIRECT_URI": self.base + "/auth/google/callback"}
        with patch.dict(os.environ, config):
            _, _, start_headers = self.raw_get("/auth/google/start")
            state_cookie = next(value.split(";", 1)[0] for name, value in start_headers if name.lower() == "set-cookie")
            state = state_cookie.split("=", 1)[1]
            with patch("app.server.urlopen", side_effect=[Response({"access_token": "access"}),
                    Response({"sub": "google-unverified", "email": "unverified@example.test", "email_verified": False})]):
                status, _, callback_headers = self.raw_get(f"/auth/google/callback?state={state}&code=auth-code",
                    cookie=f"{self.cookie}; {state_cookie}")
        self.assertEqual(status, 303)
        self.assertIn("auth_error=google_failed", dict(callback_headers)["Location"])
        with self.store._connect() as db:
            self.assertIsNone(db.execute("SELECT id FROM users WHERE email=?", ("unverified@example.test",)).fetchone())

    def test_guest_product_calculation_scenario_history_and_validation(self):
        status, product, _ = self.call("POST", "/api/products", {"name": "Tea", "currency": "ILS", "unit_cost": "5", "quantity": 4, "expenses": [], "selling_price": "10", "discount_percent": "0"})
        self.assertEqual(status, 201)
        status, result, _ = self.call("POST", f"/api/products/{product['id']}/calculate", {"product": product, "target_basis": "margin"})
        self.assertEqual(status, 200)
        self.assertEqual(result["result"]["profit"], "20.00")
        self.assertEqual(len(self.call("GET", "/api/history")[1]), 1)
        self.assertEqual(self.call("POST", f"/api/products/{product['id']}/scenarios", {"name": "Promo", "selling_price": 8, "discount_percent": 5})[0], 201)
        self.assertEqual(self.call("POST", "/api/products", {"name": "bad", "quantity": 0})[0], 400)

    def test_csrf_required_and_users_cannot_read_guest_products(self):
        status, _, _ = self.call("POST", "/api/products", {"name": "No token"}, csrf="wrong")
        self.assertEqual(status, 403)
        self.call("POST", "/api/products", {"name": "Private", "currency": "USD", "unit_cost": 1, "quantity": 1, "selling_price": 2, "discount_percent": 0})
        guest_id = self.cookie
        status, signup, _ = self.call("POST", "/api/auth/signup", {"email": "a@example.test", "password": "a-long-safe-password", "transfer_guest": False})
        self.assertEqual(status, 201, signup)
        self.assertNotEqual(self.cookie, guest_id)
        self.assertEqual(self.call("GET", "/api/products")[1], [])

    def test_mutating_request_without_csrf_is_rejected(self):
        self.assertEqual(self.call("POST", "/api/products", {"name": "No token"}, csrf="")[0], 403)

    def test_shared_expenses_allocate_reconcile_and_refuse_mixed_currencies(self):
        p1=self.call("POST","/api/products",{"name":"A","currency":"USD","unit_cost":"10","quantity":1,"selling_price":"20","discount_percent":0})[1]
        p2=self.call("POST","/api/products",{"name":"B","currency":"USD","unit_cost":"20","quantity":2,"selling_price":"30","discount_percent":0})[1]
        status, shared, _=self.call("POST","/api/shared-expenses",{"name":"Freight","amount":"1.00","basis":"quantity","product_ids":[p1["id"],p2["id"]]})
        self.assertEqual(status,201)
        products=self.call("GET","/api/products")[1]
        amounts={p["id"]:p["shared_allocations"][0]["amount"] for p in products}
        self.assertEqual(amounts[p1["id"]],"0.33")
        self.assertEqual(amounts[p2["id"]],"0.67")
        p3=self.call("POST","/api/products",{"name":"C","currency":"EUR","unit_cost":"2","quantity":1,"selling_price":"4","discount_percent":0})[1]
        status,_,_=self.call("POST","/api/shared-expenses",{"name":"Mixed","amount":"2","basis":"quantity","product_ids":[p1["id"],p3["id"]]})
        self.assertEqual(status,400)
        self.assertEqual(self.call("DELETE",f"/api/shared-expenses/{shared['id']}")[0],200)

    def test_manual_preview_is_recorded_and_saved_scenario_can_be_updated(self):
        preview={"name":"Draft","currency":"USD","unit_cost":"10","quantity":1,"selling_price":"25","discount_percent":0}
        status, result, _=self.call("POST","/api/preview",preview)
        self.assertEqual(status,200)
        self.assertEqual(result["result"]["profit"],"15.00")
        self.assertEqual(len(self.call("GET","/api/history")[1]),1)
        product=self.call("POST","/api/products",{"name":"Cup","currency":"USD","unit_cost":"10","quantity":1,"selling_price":"20","discount_percent":0})[1]
        scenario_status, scenario, _=self.call("POST",f"/api/products/{product['id']}/scenarios",{"name":"Spring","selling_price":"20","discount_percent":0})
        self.assertEqual(scenario_status,201,scenario)
        status, updated, _=self.call("PUT",f"/api/scenarios/{scenario['id']}",{"name":"Spring edit","selling_price":"24","discount_percent":"10"})
        self.assertEqual(status,200,updated)
        self.assertEqual(updated["result"]["final_unit_price"],"21.60")

    def test_product_currency_cannot_change_under_a_shared_expense(self):
        a=self.call("POST","/api/products",{"name":"Share A","currency":"USD","unit_cost":"5","quantity":1,"selling_price":"10","discount_percent":0})[1]
        b=self.call("POST","/api/products",{"name":"Share B","currency":"USD","unit_cost":"6","quantity":1,"selling_price":"12","discount_percent":0})[1]
        self.assertEqual(self.call("POST","/api/shared-expenses",{"name":"Fee","amount":"3","basis":"quantity","product_ids":[a["id"],b["id"]]})[0],201)
        status, response, _=self.call("PUT",f"/api/products/{a['id']}",{**a,"currency":"EUR"})
        self.assertEqual(status,400,response)

    def test_profit_suggestions_are_user_triggered_deterministic_and_do_not_add_history(self):
        product=self.call("POST","/api/products",{"name":"Notebook","currency":"USD","unit_cost":"10","quantity":2,"selling_price":"9","discount_percent":0})[1]
        before=len(self.call("GET","/api/history")[1])
        status, suggestion, _=self.call("POST",f"/api/products/{product['id']}/suggestions",{})
        self.assertEqual(status,200)
        self.assertEqual(suggestion["suggested_price"],"11.00")
        self.assertEqual(suggestion["result"]["profit"],"2.00")
        self.assertEqual(suggestion["profit_change"],"4.00")
        self.assertEqual(len(self.call("GET","/api/history")[1]),before)

    def test_suggestion_explains_when_existing_price_is_already_higher(self):
        product=self.call("POST","/api/products",{"name":"High-price item","currency":"USD","unit_cost":"10","quantity":1,"selling_price":"20","discount_percent":0})[1]
        status,suggestion,_=self.call("POST",f"/api/products/{product['id']}/suggestions",{})
        self.assertEqual(status,200)
        self.assertFalse(suggestion["available"])
        self.assertEqual(suggestion["reason_code"],"price_already_high")

    def test_ai_review_is_user_triggered_server_side_and_not_recorded_as_history(self):
        product=self.call("POST","/api/products",{"name":"Secret item","currency":"USD","unit_cost":"10","quantity":1,"selling_price":"20","discount_percent":0})[1]
        before=len(self.call("GET","/api/history")[1])
        with patch.dict(os.environ,{"OPENAI_API_KEY":"mock-key"}), patch("app.server.ai.review",return_value="Review only.") as review:
            status,result,_=self.call("POST",f"/api/products/{product['id']}/ai-review",{"language":"en"})
        self.assertEqual(status,200,result)
        self.assertEqual(result["review"],"Review only.")
        summary=review.call_args.args[0]
        self.assertEqual(summary["profit"],"10.00")
        self.assertNotIn("name",summary)
        self.assertEqual(len(self.call("GET","/api/history")[1]),before)

    def test_ai_review_reports_unconfigured_without_external_call(self):
        product=self.call("POST","/api/products",{"name":"Tea","currency":"USD","unit_cost":"1","quantity":1,"selling_price":"2","discount_percent":0})[1]
        with patch.dict(os.environ,{},clear=True):
            status,result,_=self.call("POST",f"/api/products/{product['id']}/ai-review",{})
        self.assertEqual(status,503)
        self.assertIn("not configured",result["error"])

    def test_empty_and_null_optional_fields_are_handled_cleanly(self):
        payload = {
            "name": "Lamp", "currency": "USD", "unit_cost": "15.00", "quantity": 2,
            "selling_price": "", "discount_percent": "", "target_profit_amount": "",
            "target_profit_percent": "", "expenses": [{"name": "Box", "amount": ""}]
        }
        status, product, _ = self.call("POST", "/api/products", payload)
        self.assertEqual(status, 201, product)
        self.assertEqual(product["selling_price"], "0.00")
        self.assertEqual(product["discount_percent"], "0")
        self.assertEqual(product["expenses"][0]["amount"], "0.00")
        preview_status, preview, _ = self.call("POST", "/api/preview", payload)
        self.assertEqual(preview_status, 200, preview)

    def test_scenarios_recalculate_dynamically_when_product_costs_change(self):
        product = self.call("POST", "/api/products", {
            "name": "Chair", "currency": "USD", "unit_cost": "10.00", "quantity": 1,
            "selling_price": "15.00", "discount_percent": "0"
        })[1]
        scenario_status, scenario, _ = self.call("POST", f"/api/products/{product['id']}/scenarios", {
            "name": "Higher Price", "selling_price": "20.00", "discount_percent": "0"
        })
        self.assertEqual(scenario_status, 201)
        self.assertEqual(scenario["result"]["profit"], "10.00")
        # Update product unit cost to 18.00
        update_status, updated, _ = self.call("PUT", f"/api/products/{product['id']}", {
            **product, "unit_cost": "18.00"
        })
        self.assertEqual(update_status, 200)
        # Fetch scenarios and verify that profit reflects the new cost (20.00 - 18.00 = 2.00)
        list_status, scenarios, _ = self.call("GET", f"/api/products/{product['id']}/scenarios")
        self.assertEqual(list_status, 200)
        self.assertEqual(scenarios[0]["result"]["profit"], "2.00")


if __name__ == "__main__":
    unittest.main()

