"""Email sender for password-reset and future transactional emails.

Requires environment variables:
    SMTP_HOST       - e.g. smtp.gmail.com or smtp.sendgrid.net
    SMTP_PORT       - e.g. 587 (STARTTLS) or 465 (SSL)
    SMTP_USER       - sender username / login
    SMTP_PASSWORD   - sender password / API key
    SMTP_FROM       - display name + address, e.g. "ProfitPilot <noreply@example.com>"
    APP_BASE_URL    - public root URL, e.g. https://profitpilot.com

All settings are optional at import time. Call configured() before sending.
"""

import os
import smtplib
import ssl
from email.headerregistry import Address
from email.message import EmailMessage


def configured() -> bool:
    """Return True if SMTP credentials are present in the environment."""
    return bool(
        os.environ.get("SMTP_HOST")
        and os.environ.get("SMTP_USER")
        and os.environ.get("SMTP_PASSWORD")
    )


def _base_url() -> str:
    return os.environ.get("APP_BASE_URL", "http://127.0.0.1:8765").rstrip("/")


def send_password_reset(to_email: str, token: str) -> None:
    """Send a password-reset email containing a single-use link.

    Raises RuntimeError if SMTP is not configured.
    Raises smtplib.SMTPException on delivery failure.
    """
    if not configured():
        raise RuntimeError(
            "Email is not configured. Set SMTP_HOST, SMTP_USER, and SMTP_PASSWORD."
        )

    reset_url = f"{_base_url()}/reset-password?token={token}"

    msg = EmailMessage()
    msg["Subject"] = "Reset your ProfitPilot password"
    msg["From"] = os.environ.get("SMTP_FROM", os.environ.get("SMTP_USER", ""))
    msg["To"] = to_email

    # Plain-text body
    msg.set_content(
        f"Hi,\n\n"
        f"We received a request to reset the password for your ProfitPilot account.\n\n"
        f"Click the link below to choose a new password. This link expires in 1 hour "
        f"and can only be used once.\n\n"
        f"{reset_url}\n\n"
        f"If you did not request a password reset, you can safely ignore this email. "
        f"Your password will not change.\n\n"
        f"— The ProfitPilot Team\n"
    )

    # HTML body
    msg.add_alternative(
        f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="font-family:system-ui,sans-serif;color:#111;background:#fff;padding:32px 16px">
  <div style="max-width:480px;margin:0 auto">
    <h1 style="font-size:20px;margin-bottom:8px">Reset your password</h1>
    <p style="color:#444;margin-bottom:24px">
      We received a request to reset the password for your ProfitPilot account.<br>
      This link expires in <strong>1 hour</strong> and can only be used once.
    </p>
    <a href="{reset_url}"
       style="display:inline-block;background:#2563eb;color:#fff;text-decoration:none;
              padding:12px 24px;border-radius:6px;font-weight:600">
      Reset password
    </a>
    <p style="margin-top:32px;font-size:13px;color:#888">
      If you did not request a password reset, you can safely ignore this email.
      Your password will not change.
    </p>
    <hr style="border:none;border-top:1px solid #eee;margin:32px 0">
    <p style="font-size:12px;color:#aaa">
      ProfitPilot &mdash; Product Cost &amp; Profit Lab
    </p>
  </div>
</body>
</html>""",
        subtype="html",
    )

    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASSWORD"]

    context = ssl.create_default_context()

    if port == 465:
        # SMTP over SSL
        with smtplib.SMTP_SSL(host, port, context=context, timeout=15) as server:
            server.login(user, password)
            server.send_message(msg)
    else:
        # SMTP with STARTTLS (port 587 or 25)
        with smtplib.SMTP(host, port, timeout=15) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(user, password)
            server.send_message(msg)
