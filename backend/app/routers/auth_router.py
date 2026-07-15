from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.schemas.auth_schemas import (
    RegisterRequest, VerifyOTPRequest, LoginRequest, TokenResponse,
    ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest,
)
from app.core.dependencies import get_current_user
from app.models.user_orm import UserORM

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


@router.post("/register")
def register(payload: RegisterRequest, service: AuthService = Depends(get_auth_service)):
    user = service.register_customer(payload.full_name, payload.email, payload.phone, payload.password)
    return {"message": "Registered successfully. An OTP has been sent to your email.", "user_id": user.user_id}


@router.post("/verify-otp")
def verify_otp(payload: VerifyOTPRequest, service: AuthService = Depends(get_auth_service)):
    service.verify_email_otp(payload.email, payload.otp_code)
    return {"message": "Email verified successfully. You can now log in."}


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)):
    return service.login(payload.email, payload.password)


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, service: AuthService = Depends(get_auth_service)):
    service.request_password_reset(payload.email)
    return {"message": "If that email exists, an OTP has been sent."}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, service: AuthService = Depends(get_auth_service)):
    service.reset_password(payload.email, payload.otp_code, payload.new_password)
    return {"message": "Password reset successfully. You can now log in."}


@router.post("/change-password")
def change_password(payload: ChangePasswordRequest,
                     current_user: UserORM = Depends(get_current_user),
                     service: AuthService = Depends(get_auth_service)):
    service.change_password(current_user, payload.old_password, payload.new_password)
    return {"message": "Password changed successfully."}
