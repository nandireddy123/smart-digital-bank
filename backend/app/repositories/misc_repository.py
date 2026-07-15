from sqlalchemy.orm import Session
from datetime import datetime

from app.models.banking_orm import (
    LoanORM, NotificationORM, AuditLogORM, SupportTicketORM,
)
from app.models.profile_orm import BranchORM


class LoanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, customer_id: int, account_id: int, loan_type: str,
               principal_amount: float, interest_rate: float, tenure_months: int) -> LoanORM:
        loan = LoanORM(
            customer_id=customer_id, account_id=account_id, loan_type=loan_type,
            principal_amount=principal_amount, interest_rate=interest_rate,
            tenure_months=tenure_months, status="PENDING",
        )
        self.db.add(loan)
        self.db.commit()
        self.db.refresh(loan)
        return loan

    def list_by_customer(self, customer_id: int) -> list[LoanORM]:
        return self.db.query(LoanORM).filter(LoanORM.customer_id == customer_id).all()

    def list_pending(self) -> list[LoanORM]:
        return self.db.query(LoanORM).filter(LoanORM.status == "PENDING").all()

    def get_by_id(self, loan_id: int) -> LoanORM | None:
        return self.db.query(LoanORM).filter(LoanORM.loan_id == loan_id).first()

    def decide(self, loan: LoanORM, approve: bool, manager_id: int):
        loan.status = "APPROVED" if approve else "REJECTED"
        loan.approved_by_manager_id = manager_id
        loan.decided_at = datetime.utcnow()
        self.db.commit()


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, title: str, message: str) -> NotificationORM:
        note = NotificationORM(user_id=user_id, title=title, message=message)
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    def list_by_user(self, user_id: int) -> list[NotificationORM]:
        return (
            self.db.query(NotificationORM)
            .filter(NotificationORM.user_id == user_id)
            .order_by(NotificationORM.created_at.desc())
            .all()
        )

    def mark_read(self, notification: NotificationORM):
        notification.is_read = True
        self.db.commit()


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def log(self, user_id: int | None, action: str, details: str | None = None, ip_address: str | None = None):
        entry = AuditLogORM(user_id=user_id, action=action, details=details, ip_address=ip_address)
        self.db.add(entry)
        self.db.commit()

    def list_all(self, limit: int = 300) -> list[AuditLogORM]:
        return self.db.query(AuditLogORM).order_by(AuditLogORM.created_at.desc()).limit(limit).all()


class SupportRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, subject: str, message: str) -> SupportTicketORM:
        ticket = SupportTicketORM(user_id=user_id, subject=subject, message=message)
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def list_by_user(self, user_id: int) -> list[SupportTicketORM]:
        return self.db.query(SupportTicketORM).filter(SupportTicketORM.user_id == user_id).all()

    def list_all(self) -> list[SupportTicketORM]:
        return self.db.query(SupportTicketORM).order_by(SupportTicketORM.created_at.desc()).all()


class BranchRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[BranchORM]:
        return self.db.query(BranchORM).all()

    def get_by_id(self, branch_id: int) -> BranchORM | None:
        return self.db.query(BranchORM).filter(BranchORM.branch_id == branch_id).first()

    def create(self, branch_name: str, branch_code: str, address: str | None,
               city: str | None, ifsc_code: str | None) -> BranchORM:
        branch = BranchORM(
            branch_name=branch_name, branch_code=branch_code,
            address=address, city=city, ifsc_code=ifsc_code,
        )
        self.db.add(branch)
        self.db.commit()
        self.db.refresh(branch)
        return branch
