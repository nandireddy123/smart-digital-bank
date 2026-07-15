from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class ProfileResponse(BaseModel):
    user_id: int
    full_name: str
    email: str
    phone: str | None
    role: str

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    address: str | None = None


class LoanApplicationRequest(BaseModel):
    account_id: int
    loan_type: str
    principal_amount: float = Field(..., gt=0)
    tenure_months: int = Field(..., gt=0)


class LoanResponse(BaseModel):
    loan_id: int
    loan_type: str
    principal_amount: float
    interest_rate: float
    tenure_months: int
    status: str
    applied_at: datetime

    class Config:
        from_attributes = True


class LoanDecisionRequest(BaseModel):
    loan_id: int
    approve: bool


class SupportTicketRequest(BaseModel):
    subject: str = Field(..., min_length=3, max_length=150)
    message: str = Field(..., min_length=5, max_length=1000)


class NotificationResponse(BaseModel):
    notification_id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
