"""
auth_service.py
----------------
Service Layer: contains business logic/orchestration for
registration, login, OTP verification and password reset. Routers
call into this layer; this layer calls into repositories. Routers
never talk to SQLAlchemy directly (Separation of Concerns / SOLID's
Single Responsibility Principle).

**Dependency** in action: `AuthService.__init__` takes a `UserRepository`
instance rather than creating one itself -- this is Dependency
Injection, which makes the service easy to unit test (you can pass in
a fake repository in tests instead of hitting a real database).
"""
from app.repositories.user_repository import UserRepository
from app.core.security import (
    hash_password, verify_password, create_access_token, generate_otp,
)
from app.core.exceptions import (
    UserAlreadyExistsError, InvalidCredentialsError,
    OTPInvalidOrExpiredError, EmailNotVerifiedError,
)
from app.utils.email_otp import send_otp_email


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo  # Dependency injected, not created here

    def register_customer(self, full_name: str, email: str, phone: str | None, password: str):
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise UserAlreadyExistsError(email)

        user = self.user_repo.create_user(
            full_name=full_name, email=email, phone=phone,
            password_hash=hash_password(password), role="CUSTOMER",
        )
        self.user_repo.create_customer_profile(user.user_id)

        otp_code = generate_otp()
        self.user_repo.create_otp(user.user_id, otp_code, "EMAIL_VERIFICATION")
        send_otp_email(email, otp_code, "EMAIL_VERIFICATION")
        return user

    def verify_email_otp(self, email: str, otp_code: str):
        user = self.user_repo.get_by_email(email)
        if not user:
            raise OTPInvalidOrExpiredError()

        otp = self.user_repo.get_valid_otp(user.user_id, otp_code, "EMAIL_VERIFICATION")
        if not otp:
            raise OTPInvalidOrExpiredError()

        self.user_repo.mark_otp_used(otp)
        self.user_repo.mark_email_verified(user)
        return user

    def login(self, email: str, password: str) -> dict:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        if user.role == "CUSTOMER" and not user.is_email_verified:
            raise EmailNotVerifiedError()

        token = create_access_token({"sub": str(user.user_id), "role": user.role})
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": user.role,
            "full_name": user.full_name,
        }

    def request_password_reset(self, email: str):
        user = self.user_repo.get_by_email(email)
        if not user:
            # Don't reveal whether the email exists -- standard security practice
            return
        otp_code = generate_otp()
        self.user_repo.create_otp(user.user_id, otp_code, "PASSWORD_RESET")
        send_otp_email(email, otp_code, "PASSWORD_RESET")

    def reset_password(self, email: str, otp_code: str, new_password: str):
        user = self.user_repo.get_by_email(email)
        if not user:
            raise OTPInvalidOrExpiredError()

        otp = self.user_repo.get_valid_otp(user.user_id, otp_code, "PASSWORD_RESET")
        if not otp:
            raise OTPInvalidOrExpiredError()

        self.user_repo.mark_otp_used(otp)
        self.user_repo.update_password(user, hash_password(new_password))

    def change_password(self, user, old_password: str, new_password: str):
        if not verify_password(old_password, user.password_hash):
            raise InvalidCredentialsError()
        self.user_repo.update_password(user, hash_password(new_password))
