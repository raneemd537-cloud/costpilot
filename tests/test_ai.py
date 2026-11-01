import json
import os
import unittest
from unittest.mock import patch

from app import ai


class _Response:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, _limit):
        return json.dumps(self.body).encode()


class AiTests(unittest.TestCase):
    def test_review_uses_server_key_and_responses_api(self):
        payload = {"currency": "USD", "unit_cost":"10.00", "quantity":2,
                   "expenses":["1.00"], "discount_percent":"0", "selling_price":"12.00",
                   "final_unit_price":"12.00", "total_cost":"21.00", "revenue":"24.00",
                   "profit":"3.00", "margin_percent":"12.50", "break_even_unit_price":"10.50"}
        response = {"output": [{"type": "message", "content": [{"type": "output_text", "text": "Review text."}]}]}
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-secret", "DECISION_LAB_AI_MODEL": "test-model"}), \
             patch("app.ai.urlopen", return_value=_Response(response)) as call:
            self.assertEqual(ai.review(payload, "en"), "Review text.")
        request = call.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.openai.com/v1/responses")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-secret")
        body = json.loads(request.data)
        self.assertFalse(body["store"])
        self.assertEqual(body["model"], "test-model")
        self.assertIn('"profit": "3.00"', body["input"])

    def test_review_fails_closed_without_server_key(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(ai.configured())
            with self.assertRaisesRegex(RuntimeError, "not configured"):
                ai.review({}, "en")

