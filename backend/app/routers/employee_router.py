from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import require_role
from app.models.user_orm import UserORM
from app.repositories.account_repository import AccountRepository, TransactionRepository
from app.repositories.user_repository import UserRepository
from app.services.account_service import AccountService
from app.services.misc_services import TransactionService
from app.schemas.account_schemas import ApproveAccountRequest

router = APIRouter(prefix="/api/employee", tags=["Employee"])


def get_account_service(db: Session = Depends(get_db)) -> AccountService:
    return AccountService(AccountRepository(db), TransactionRepository(db), UserRepository(db))


def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    return TransactionService(AccountRepository(db), TransactionRepository(db), UserRepository(db))


@router.get("/customers")
def list_customers(current_user: UserORM = Depends(require_role("EMPLOYEE", "MANAGER")),
                    db: Session = Depends(get_db)):
    repo = UserRepository(db)
    customers = repo.list_customers()
    result = []
    for c in customers:
        result.append({
            "customer_id": c.customer_id, "user_id": c.user_id,
            "kyc_verified": c.kyc_verified,
            "full_name": c.user.full_name if c.user else None,
            "email": c.user.email if c.user else None,
        })
    return result


@router.post("/customers/{customer_id}/verify-kyc")
def verify_kyc(customer_id: int,
                current_user: UserORM = Depends(require_role("EMPLOYEE")),
                db: Session = Depends(get_db)):
    repo = UserRepository(db)
    customer = repo.get_customer_by_id(customer_id)
    employee = repo.get_employee_by_user_id(current_user.user_id)
    repo.verify_kyc(customer, employee.employee_id)
    return {"message": "Customer KYC verified"}


@router.get("/accounts/pending")
def pending_accounts(current_user: UserORM = Depends(require_role("EMPLOYEE")),
                      service: AccountService = Depends(get_account_service)):
    accounts = service.list_pending_accounts()
    return [
        {"account_id": a.account_id, "account_number": a.account_number,
         "account_type": a.account_type, "customer_id": a.customer_id, "status": a.status}
        for a in accounts
    ]


@router.post("/accounts/approve")
def approve_account(payload: ApproveAccountRequest,
                     current_user: UserORM = Depends(require_role("EMPLOYEE")),
                     service: AccountService = Depends(get_account_service)):
    service.approve_account(current_user.user_id, payload.account_id)
    return {"message": "Account approved and activated"}


@router.get("/transactions")
def all_transactions(current_user: UserORM = Depends(require_role("EMPLOYEE", "MANAGER")),
                      service: TransactionService = Depends(get_transaction_service)):
    txns = service.all_transactions_for_staff()
    return [
        {"transaction_id": t.transaction_id, "reference_no": t.reference_no,
         "account_id": t.account_id, "transaction_type": t.transaction_type,
         "amount": float(t.amount), "status": t.status,
         "created_at": t.created_at.isoformat() if t.created_at else None}
        for t in txns
    ]
