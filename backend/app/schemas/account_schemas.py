from datetime import datetime
from pydantic import BaseModel, Field


class OpenAccountRequest(BaseModel):
    account_type: str = Field(..., pattern="^(SAVINGS|CURRENT|STUDENT)$")


class AccountResponse(BaseModel):
    account_id: int
    account_number: str
    account_type: str
    balance: float
    status: str
    interest_rate: float
    min_balance: float

    class Config:
        from_attributes = True


class DepositRequest(BaseModel):
    account_id: int
    amount: float = Field(..., gt=0)
    description: str | None = None


class WithdrawRequest(BaseModel):
    account_id: int
    amount: float = Field(..., gt=0)
    description: str | None = None


class TransferRequest(BaseModel):
    from_account_id: int
    to_account_number: str
    amount: float = Field(..., gt=0)
    description: str | None = None


class TransactionResponse(BaseModel):
    transaction_id: int
    reference_no: str
    account_id: int
    transaction_type: str
    amount: float
    balance_after: float
    description: str | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ApproveAccountRequest(BaseModel):
    account_id: int


class FreezeAccountRequest(BaseModel):
    account_id: int
