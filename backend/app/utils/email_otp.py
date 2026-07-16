"""
email_otp.py
------------
Sends OTP emails. Tries, in order:

1. Resend (HTTP API) -- if RESEND_API_KEY is set. Works everywhere,
   including Render's free tier, because it's plain HTTPS, not SMTP.
2. Gmail SMTP -- if SMTP_USERNAME/PASSWORD are set. Works locally, but
   NOT on Render's free tier (Render blocks outbound SMTP ports on
   free web services as of Sept 2025).
3. Console/log fallback -- if neither is configured, for local dev.
"""
import smtplib
import logging
import requests
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger("email_otp")
logging.basicConfig(level=logging.INFO)


def _build_subject_and_body(otp_code: str, purpose: str) -> tuple[str, str]:
    subject_map = {
        "EMAIL_VERIFICATION": "Verify your Smart Digital Bank account",
        "PASSWORD_RESET": "Reset your Smart Digital Bank password",
    }
    subject = subject_map.get(purpose, "Your OTP Code")
    body = (
        f"Your OTP code is: {otp_code}\n\n"
        f"This code will expire in {settings.OTP_EXPIRE_MINUTES} minutes.\n"
        f"If you did not request this, please ignore this email."
    )
    return subject, body


def _send_via_resend(to_email: str, subject: str, body: str) -> bool:
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": settings.RESEND_FROM,
                "to": [to_email],
                "subject": subject,
                "text": body,
            },
            timeout=10,
        )
        if response.status_code >= 400:
            logger.error(f"Resend API error {response.status_code}: {response.text}")
            return False
        return True
    except Exception as exc:  # pragma: no cover
        logger.error(f"Resend request failed: {exc}")
        return False


def _send_via_smtp(to_email: str, subject: str, body: str) -> bool:
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, [to_email], msg.as_string())
        return True
    except Exception as exc:  # pragma: no cover
        logger.error(f"SMTP send failed for {to_email}: {exc}")
        return False


def send_otp_email(to_email: str, otp_code: str, purpose: str) -> None:
    subject, body = _build_subject_and_body(otp_code, purpose)

    if settings.RESEND_API_KEY:
        if _send_via_resend(to_email, subject, body):
            return
        logger.warning("Resend send failed, falling back to console log.")

    elif settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
        if _send_via_smtp(to_email, subject, body):
            return
        logger.warning("SMTP send failed, falling back to console log.")

    # ---- Local dev / fallback: no email service configured or all failed ----
    logger.info(
        "\n===== [DEV MODE - OTP EMAIL NOT ACTUALLY SENT] =====\n"
        f"TO: {to_email}\nSUBJECT: {subject}\n{body}\n"
        "=====================================================\n"
    )