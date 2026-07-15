from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user_orm import UserORM
from app.repositories.account_repository import AccountRepository, TransactionRepository
from app.repositories.user_repository import UserRepository
from app.repositories.misc_repository import LoanRepository
from app.services.account_service import AccountService
from app.services.misc_services import TransactionService, LoanService
from app.schemas.account_schemas import (
    OpenAccountRequest, DepositRequest, WithdrawRequest, TransferRequest,
)
from app.schemas.misc_schemas import LoanApplicationRequest

router = APIRouter(prefix="/api/customer", tags=["Customer"])


def get_account_service(db: Session = Depends(get_db)) -> AccountService:
    return AccountService(AccountRepository(db), TransactionRepository(db), UserRepository(db))


def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    return TransactionService(AccountRepository(db), TransactionRepository(db), UserRepository(db))


def get_loan_service(db: Session = Depends(get_db)) -> LoanService:
    return LoanService(LoanRepository(db), AccountRepository(db), UserRepository(db))


@router.get("/accounts")
def list_accounts(current_user: UserORM = Depends(require_role("CUSTOMER")),
                   service: AccountService = Depends(get_account_service)):
    accounts = service.list_my_accounts(current_user.user_id)
    return [
        {
            "account_id": a.account_id, "account_number": a.account_number,
            "account_type": a.account_type, "balance": float(a.balance),
            "status": a.status, "interest_rate": float(a.interest_rate or 0),
            "min_balance": float(a.min_balance or 0),
        }
        for a in accounts
    ]


@router.post("/accounts/open")
def open_account(payload: OpenAccountRequest,
                  current_user: UserORM = Depends(require_role("CUSTOMER")),
                  service: AccountService = Depends(get_account_service)):
    account = service.open_account(current_user.user_id, payload.account_type)
    return {"message": "Account requested. Awaiting employee approval.", "account_number": account.account_number}


@router.post("/deposit")
def deposit(payload: DepositRequest,
            current_user: UserORM = Depends(require_role("CUSTOMER")),
            service: AccountService = Depends(get_account_service)):
    txn = service.deposit(current_user.user_id, payload.account_id, payload.amount, payload.description)
    return {"message": "Deposit successful", "reference_no": txn.reference_no, "balance_after": float(txn.balance_after)}


@router.post("/withdraw")
def withdraw(payload: WithdrawRequest,
             current_user: UserORM = Depends(require_role("CUSTOMER")),
             service: AccountService = Depends(get_account_service)):
    txn = service.withdraw(current_user.user_id, payload.account_id, payload.amount, payload.description)
    return {"message": "Withdrawal successful", "reference_no": txn.reference_no, "balance_after": float(txn.balance_after)}


@router.post("/transfer")
def transfer(payload: TransferRequest,
             current_user: UserORM = Depends(require_role("CUSTOMER")),
             service: AccountService = Depends(get_account_service)):
    txn = service.transfer(current_user.user_id, payload.from_account_id, payload.to_account_number,
                            payload.amount, payload.description)
    return {"message": "Transfer successful", "reference_no": txn.reference_no, "balance_after": float(txn.balance_after)}


@router.get("/transactions/{account_id}")
def transaction_history(account_id: int,
                         current_user: UserORM = Depends(require_role("CUSTOMER")),
                         service: TransactionService = Depends(get_transaction_service)):
    txns = service.history(current_user.user_id, account_id)
    return [_serialize_txn(t) for t in txns]


@router.get("/transactions/{account_id}/search")
def search_transactions(account_id: int, keyword: str,
                         current_user: UserORM = Depends(require_role("CUSTOMER")),
                         service: TransactionService = Depends(get_transaction_service)):
    txns = service.search(current_user.user_id, account_id, keyword)
    return [_serialize_txn(t) for t in txns]


@router.post("/loans/apply")
def apply_loan(payload: LoanApplicationRequest,
                current_user: UserORM = Depends(require_role("CUSTOMER")),
                service: LoanService = Depends(get_loan_service)):
    loan = service.apply(current_user.user_id, payload.account_id, payload.loan_type,
                          payload.principal_amount, payload.tenure_months)
    return {"message": "Loan application submitted", "loan_id": loan.loan_id, "status": loan.status}


@router.get("/loans")
def my_loans(current_user: UserORM = Depends(require_role("CUSTOMER")),
             service: LoanService = Depends(get_loan_service)):
    loans = service.my_loans(current_user.user_id)
    return [
        {
            "loan_id": l.loan_id, "loan_type": l.loan_type,
            "principal_amount": float(l.principal_amount), "interest_rate": float(l.interest_rate),
            "tenure_months": l.tenure_months, "status": l.status,
        }
        for l in loans
    ]


def _serialize_txn(t):
    return {
        "transaction_id": t.transaction_id, "reference_no": t.reference_no,
        "transaction_type": t.transaction_type, "amount": float(t.amount),
        "balance_after": float(t.balance_after), "description": t.description,
        "status": t.status, "created_at": t.created_at.isoformat() if t.created_at else None,
    }
