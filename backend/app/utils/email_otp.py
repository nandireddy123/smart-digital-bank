"""
email_otp.py
------------
Sends OTP emails via SMTP. If no SMTP credentials are configured
(the default for local development), it falls back to printing the
OTP to the console/server log, so you can run and demo the whole
Register -> OTP -> Verify flow locally without setting up a real
mailbox.
"""
import smtplib
import logging
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger("email_otp")
logging.basicConfig(level=logging.INFO)


def send_otp_email(to_email: str, otp_code: str, purpose: str) -> None:
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

    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        # ---- Local dev fallback: no SMTP configured ----
        logger.info(
            "\n===== [DEV MODE - OTP EMAIL NOT ACTUALLY SENT] =====\n"
            f"TO: {to_email}\nSUBJECT: {subject}\n{body}\n"
            "=====================================================\n"
        )
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, [to_email], msg.as_string())
    except Exception as exc:  # pragma: no cover
        logger.error(f"Failed to send OTP email to {to_email}: {exc}")
        # Still log it so local dev / demo never gets blocked by a mail failure
        logger.info(f"OTP for {to_email} was: {otp_code}")
