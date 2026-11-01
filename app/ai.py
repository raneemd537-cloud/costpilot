"""Optional, explicitly invoked OpenAI financial review. Arithmetic stays local."""
import json
import os
from urllib.request import Request, urlopen


def configured():
    return bool(os.environ.get("OPENAI_API_KEY"))


def review(summary, language="en"):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("AI review is not configured")
    model = os.environ.get("DECISION_LAB_AI_MODEL", "gpt-5.4-mini")
    prompt = {
        "language": language,
        "currency": summary["currency"],
        "unit_cost": summary["unit_cost"],
        "quantity": summary["quantity"],
        "seller_expenses": summary["expenses"],
        "discount_percent": summary["discount_percent"],
        "original_selling_price": summary["selling_price"],
        "final_unit_price": summary["final_unit_price"],
        "total_cost": summary["total_cost"],
        "revenue": summary["revenue"],
        "profit": summary["profit"],
        "margin_percent": summary["margin_percent"],
        "break_even_unit_price": summary["break_even_unit_price"],
    }
    payload = json.dumps({
        "model": model,
        "store": False,
        "max_output_tokens": 500,
        "instructions": (
            "Review this seller's product economics. Explain the deterministic figures, identify up to 3 risks or useful questions, "
            "and suggest non-numeric next steps. Never recalculate or invent financial numbers, predict demand, or change prices. "
            "Clearly state that this is a general AI review, not a forecast. Respond in the requested language."
        ),
        "input": json.dumps(prompt, ensure_ascii=False),
    }, ensure_ascii=False).encode("utf-8")
    request = Request("https://api.openai.com/v1/responses", data=payload, method="POST", headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json",
    })
    with urlopen(request, timeout=25) as response:
        data = json.loads(response.read(128 * 1024).decode("utf-8"))
    text = "\n".join(
        part.get("text", "")
        for item in data.get("output", []) if item.get("type") == "message"
        for part in item.get("content", []) if part.get("type") == "output_text"
    ).strip()
    if not text or len(text) > 6000:
        raise RuntimeError("AI review returned an unusable response")
    return text
