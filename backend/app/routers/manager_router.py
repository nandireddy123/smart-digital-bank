from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import require_role
from app.models.user_orm import UserORM
from app.repositories.account_repository import AccountRepository, TransactionRepository
from app.repositories.user_repository import UserRepository
from app.repositories.misc_repository import LoanRepository, AuditLogRepository, BranchRepository
from app.services.account_service import AccountService
from app.services.misc_services import LoanService, EmployeeManagementService
from app.schemas.account_schemas import FreezeAccountRequest
from app.schemas.misc_schemas import LoanDecisionRequest
from app.schemas.auth_schemas import CreateEmployeeRequest

router = APIRouter(prefix="/api/manager", tags=["Manager"])


def get_account_service(db: Session = Depends(get_db)) -> AccountService:
    return AccountService(AccountRepository(db), TransactionRepository(db), UserRepository(db))


def get_loan_service(db: Session = Depends(get_db)) -> LoanService:
    return LoanService(LoanRepository(db), AccountRepository(db), UserRepository(db))


def get_employee_mgmt_service(db: Session = Depends(get_db)) -> EmployeeManagementService:
    return EmployeeManagementService(UserRepository(db))


@router.get("/employees")
def list_employees(current_user: UserORM = Depends(require_role("MANAGER")), db: Session = Depends(get_db)):
    repo = UserRepository(db)
    employees = repo.list_employees()
    return [
        {
            "employee_id": e.employee_id, "user_id": e.user_id,
            "designation": e.designation, "branch_id": e.branch_id,
            "full_name": e.user.full_name if e.user else None,
            "email": e.user.email if e.user else None,
        }
        for e in employees
    ]


@router.post("/employees")
def create_employee(payload: CreateEmployeeRequest,
                     current_user: UserORM = Depends(require_role("MANAGER")),
                     service: EmployeeManagementService = Depends(get_employee_mgmt_service)):
    employee = service.create_employee(
        current_user.user_id, payload.full_name, payload.email,
        payload.phone, payload.password, payload.branch_id,
    )
    return {"message": "Employee created", "employee_id": employee.employee_id, "role": employee.get_role()}


@router.post("/accounts/freeze")
def freeze_account(payload: FreezeAccountRequest,
                    current_user: UserORM = Depends(require_role("MANAGER")),
                    service: AccountService = Depends(get_account_service)):
    service.freeze_account(payload.account_id)
    return {"message": "Account frozen"}


@router.post("/accounts/activate")
def activate_account(payload: FreezeAccountRequest,
                      current_user: UserORM = Depends(require_role("MANAGER")),
                      service: AccountService = Depends(get_account_service)):
    service.activate_account(payload.account_id)
    return {"message": "Account activated"}


@router.get("/accounts")
def all_accounts(current_user: UserORM = Depends(require_role("MANAGER")),
                  service: AccountService = Depends(get_account_service)):
    accounts = service.list_all_accounts()
    return [
        {"account_id": a.account_id, "account_number": a.account_number,
         "account_type": a.account_type, "balance": float(a.balance), "status": a.status}
        for a in accounts
    ]


@router.get("/loans/pending")
def pending_loans(current_user: UserORM = Depends(require_role("MANAGER")),
                   service: LoanService = Depends(get_loan_service)):
    loans = service.pending_loans()
    return [
        {"loan_id": l.loan_id, "customer_id": l.customer_id, "loan_type": l.loan_type,
         "principal_amount": float(l.principal_amount), "tenure_months": l.tenure_months}
        for l in loans
    ]


@router.post("/loans/decide")
def decide_loan(payload: LoanDecisionRequest,
                 current_user: UserORM = Depends(require_role("MANAGER")),
                 service: LoanService = Depends(get_loan_service)):
    loan = service.decide(current_user.user_id, payload.loan_id, payload.approve)
    return {"message": f"Loan {loan.status.lower()}"}


@router.get("/reports/summary")
def reports_summary(current_user: UserORM = Depends(require_role("MANAGER")), db: Session = Depends(get_db)):
    account_repo = AccountRepository(db)
    txn_repo = TransactionRepository(db)
    accounts = account_repo.list_all()
    txns = txn_repo.list_all(limit=1000)
    return {
        "total_accounts": len(accounts),
        "total_balance": sum(float(a.balance) for a in accounts),
        "active_accounts": len([a for a in accounts if a.status == "ACTIVE"]),
        "pending_accounts": len([a for a in accounts if a.status == "PENDING"]),
        "frozen_accounts": len([a for a in accounts if a.status == "FROZEN"]),
        "total_transactions": len(txns),
    }


@router.get("/audit-logs")
def audit_logs(current_user: UserORM = Depends(require_role("MANAGER")), db: Session = Depends(get_db)):
    repo = AuditLogRepository(db)
    logs = repo.list_all()
    return [
        {"audit_id": l.audit_id, "user_id": l.user_id, "action": l.action,
         "details": l.details, "created_at": l.created_at.isoformat() if l.created_at else None}
        for l in logs
    ]


@router.get("/branches")
def list_branches(current_user: UserORM = Depends(require_role("MANAGER")), db: Session = Depends(get_db)):
    repo = BranchRepository(db)
    branches = repo.list_all()
    return [
        {"branch_id": b.branch_id, "branch_name": b.branch_name,
         "branch_code": b.branch_code, "city": b.city}
        for b in branches
    ]


@router.post("/branches")
def create_branch(branch_name: str, branch_code: str, city: str = "", address: str = "", ifsc_code: str = "",
                   current_user: UserORM = Depends(require_role("MANAGER")), db: Session = Depends(get_db)):
    repo = BranchRepository(db)
    branch = repo.create(branch_name, branch_code, address, city, ifsc_code)
    return {"message": "Branch created", "branch_id": branch.branch_id}
