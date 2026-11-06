"""Send transactional emails. Three providers:
  console  — prints to stdout (good for local dev, no setup needed)
  smtp     — any SMTP server (Gmail, SES, Postmark, etc.)
  resend   — Resend.com API (simplest hosted option)
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Thread
import httpx
from . import config


def _html(link: str) -> str:
    return f"""\
<div style="font-family:system-ui,sans-serif;max-width:480px;margin:0 auto;padding:24px;color:#0f0f18">
  <h1 style="font-size:22px;margin-bottom:16px">Verify your VoxReel account</h1>
  <p style="color:#3f3f46;line-height:1.6;font-size:15px">
    Click the button below to confirm your email and set your password.
    The link expires in 24 hours.
  </p>
  <a href="{link}" style="display:inline-block;background:linear-gradient(120deg,#8B5CF6,#EC4899);color:#fff;
     padding:12px 28px;border-radius:12px;text-decoration:none;font-weight:600;margin:20px 0">
    Verify email &rarr;
  </a>
  <p style="color:#71717a;font-size:13px;margin-top:24px">
    If you didn't create a VoxReel account, you can ignore this email.
  </p>
  <p style="color:#a1a1aa;font-size:12px;margin-top:8px">
    Or paste this link into your browser:<br>
    <span style="word-break:break-all">{link}</span>
  </p>
</div>"""


def _send(to: str, subject: str, html: str):
    provider = config.MAIL_PROVIDER
    if provider == "console":
        print(f"\n{'='*60}\n  EMAIL → {to}\n  Subject: {subject}\n{'='*60}\n{html}\n{'='*60}\n")
        return
    if provider == "resend":
        r = httpx.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {config.RESEND_API_KEY}"},
            json={"from": config.MAIL_FROM, "to": [to], "subject": subject, "html": html},
            timeout=30,
        )
        r.raise_for_status()
        return
    # SMTP
    msg = MIMEMultipart("alternative")
    msg["From"] = config.MAIL_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html"))
    ctx = smtplib.ssl.create_default_context()
    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
        server.ehlo()
        server.starttls(context=ctx)
        server.ehlo()
        if config.SMTP_USER:
            server.login(config.SMTP_USER, config.SMTP_PASS)
        server.sendmail(config.MAIL_FROM, to, msg.as_string())


def send_verification(to: str, link: str):
    """Send the email verification link. Runs in a thread so the API doesn't block."""
    Thread(target=_send, args=(to, "Verify your VoxReel account", _html(link)), daemon=True).start()
