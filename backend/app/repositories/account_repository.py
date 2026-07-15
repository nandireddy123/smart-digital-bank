"""
account_repository.py
----------------------
Repository Pattern for accounts and transactions. Also contains the
mapping functions that translate an `AccountORM` row into a rich
domain `Account` object (Savings/Current/Student) and back -- this is
the bridge between the persistence layer and the OOP domain layer.
"""
from sqlalchemy.orm import Session

from app.models.banking_orm import AccountORM, TransactionORM
from app.models.account import Account, build_account


class AccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, account_number: str, customer_id: int, account_type: str,
               branch_id: int | None, min_balance: float) -> AccountORM:
        account = AccountORM(
            account_number=account_number,
            customer_id=customer_id,
            account_type=account_type,
            branch_id=branch_id,
            balance=0,
            status="PENDING",
            min_balance=min_balance,
        )
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def get_by_id(self, account_id: int) -> AccountORM | None:
        return self.db.query(AccountORM).filter(AccountORM.account_id == account_id).first()

    def get_by_number(self, account_number: str) -> AccountORM | None:
        return self.db.query(AccountORM).filter(AccountORM.account_number == account_number).first()

    def list_by_customer(self, customer_id: int) -> list[AccountORM]:
        return self.db.query(AccountORM).filter(AccountORM.customer_id == customer_id).all()

    def list_pending(self) -> list[AccountORM]:
        return self.db.query(AccountORM).filter(AccountORM.status == "PENDING").all()

    def list_all(self) -> list[AccountORM]:
        return self.db.query(AccountORM).all()

    def approve(self, account: AccountORM, employee_id: int):
        account.status = "ACTIVE"
        account.approved_by_employee_id = employee_id
        self.db.commit()

    def set_status(self, account: AccountORM, status: str):
        account.status = status
        self.db.commit()

    def save_balance(self, account: AccountORM, new_balance: float):
        account.balance = new_balance
        self.db.commit()
        self.db.refresh(account)

    @staticmethod
    def to_domain(account_orm: AccountORM) -> Account:
        """Maps a persisted row -> a polymorphic domain object."""
        return build_account(
            account_orm.account_type,
            account_id=account_orm.account_id,
            account_number=account_orm.account_number,
            customer_id=account_orm.customer_id,
            balance=float(account_orm.balance),
            status=account_orm.status,
            min_balance=float(account_orm.min_balance or 0),
        )


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, reference_no: str, account_id: int, transaction_type: str,
               amount: float, balance_after: float, description: str | None,
               related_account_id: int | None = None) -> TransactionORM:
        txn = TransactionORM(
            reference_no=reference_no,
            account_id=account_id,
            related_account_id=related_account_id,
            transaction_type=transaction_type,
            amount=amount,
            balance_after=balance_after,
            description=description,
            status="SUCCESS",
        )
        self.db.add(txn)
        self.db.commit()
        self.db.refresh(txn)
        return txn

    def list_by_account(self, account_id: int) -> list[TransactionORM]:
        return (
            self.db.query(TransactionORM)
            .filter(TransactionORM.account_id == account_id)
            .order_by(TransactionORM.created_at.desc())
            .all()
        )

    def search_by_account(self, account_id: int, keyword: str) -> list[TransactionORM]:
        like = f"%{keyword}%"
        return (
            self.db.query(TransactionORM)
            .filter(
                TransactionORM.account_id == account_id,
                (TransactionORM.description.ilike(like)) | (TransactionORM.reference_no.ilike(like)),
            )
            .order_by(TransactionORM.created_at.desc())
            .all()
        )

    def list_all(self, limit: int = 200) -> list[TransactionORM]:
        return self.db.query(TransactionORM).order_by(TransactionORM.created_at.desc()).limit(limit).all()
