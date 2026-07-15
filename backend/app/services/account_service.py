"""
account_service.py
-------------------
Business logic for opening accounts and running deposit / withdraw /
transfer operations.

This is where the domain layer (models/account.py) and the
persistence layer (repositories) meet: we load an `AccountORM` row,
convert it to a rich `Account` domain object with `AccountRepository.to_domain()`,
call polymorphic business methods on it (`.deposit()`, `.withdraw()`),
then persist the resulting balance back.
"""
from app.repositories.account_repository import AccountRepository, TransactionRepository
from app.repositories.user_repository import UserRepository
from app.core.security import generate_account_number, generate_reference_no
from app.core.exceptions import AccountNotFoundError, PermissionDeniedError
from app.models.account import SavingsAccount, CurrentAccount, StudentAccount
from app.models.bank import Bank


MIN_BALANCE_BY_TYPE = {
    "SAVINGS": SavingsAccount.DEFAULT_MIN_BALANCE,
    "CURRENT": CurrentAccount.DEFAULT_MIN_BALANCE,
    "STUDENT": StudentAccount.DEFAULT_MIN_BALANCE,
}
INTEREST_RATE_BY_TYPE = {
    "SAVINGS": SavingsAccount.INTEREST_RATE * 100,
    "CURRENT": CurrentAccount.INTEREST_RATE * 100,
    "STUDENT": StudentAccount.INTEREST_RATE * 100,
}


class AccountService:
    def __init__(self, account_repo: AccountRepository, txn_repo: TransactionRepository,
                 user_repo: UserRepository):
        self.account_repo = account_repo
        self.txn_repo = txn_repo
        self.user_repo = user_repo

    def open_account(self, customer_user_id: int, account_type: str):
        customer = self.user_repo.get_customer_by_user_id(customer_user_id)
        if not customer:
            raise PermissionDeniedError("Only customers can open accounts")

        account_number = generate_account_number()
        min_balance = MIN_BALANCE_BY_TYPE[account_type]
        account = self.account_repo.create(
            account_number=account_number,
            customer_id=customer.customer_id,
            account_type=account_type,
            branch_id=None,
            min_balance=min_balance,
        )
        account.interest_rate = INTEREST_RATE_BY_TYPE[account_type]
        self.account_repo.db.commit()
        return account

    def list_my_accounts(self, customer_user_id: int):
        customer = self.user_repo.get_customer_by_user_id(customer_user_id)
        if not customer:
            return []
        return self.account_repo.list_by_customer(customer.customer_id)

    def _load_owned_account(self, account_id: int, customer_user_id: int):
        customer = self.user_repo.get_customer_by_user_id(customer_user_id)
        account_orm = self.account_repo.get_by_id(account_id)
        if not account_orm or not customer or account_orm.customer_id != customer.customer_id:
            raise AccountNotFoundError()
        return account_orm

    def deposit(self, customer_user_id: int, account_id: int, amount: float, description: str | None):
        account_orm = self._load_owned_account(account_id, customer_user_id)
        domain_account = self.account_repo.to_domain(account_orm)

        new_balance = domain_account.deposit(amount)  # polymorphic call

        self.account_repo.save_balance(account_orm, new_balance)
        txn = self.txn_repo.create(
            reference_no=generate_reference_no("DEP"), account_id=account_id,
            transaction_type="DEPOSIT", amount=amount, balance_after=new_balance,
            description=description or "Cash deposit",
        )
        return txn

    def withdraw(self, customer_user_id: int, account_id: int, amount: float, description: str | None):
        account_orm = self._load_owned_account(account_id, customer_user_id)
        domain_account = self.account_repo.to_domain(account_orm)

        new_balance = domain_account.withdraw(amount)  # polymorphic call -- rules differ per account type

        self.account_repo.save_balance(account_orm, new_balance)
        txn = self.txn_repo.create(
            reference_no=generate_reference_no("WDR"), account_id=account_id,
            transaction_type="WITHDRAW", amount=amount, balance_after=new_balance,
            description=description or "Cash withdrawal",
        )
        return txn

    def transfer(self, customer_user_id: int, from_account_id: int, to_account_number: str,
                 amount: float, description: str | None):
        source_orm = self._load_owned_account(from_account_id, customer_user_id)
        dest_orm = self.account_repo.get_by_number(to_account_number)
        if not dest_orm:
            raise AccountNotFoundError()

        source_domain = self.account_repo.to_domain(source_orm)
        dest_domain = self.account_repo.to_domain(dest_orm)

        # Association: Bank operates on two Account objects it doesn't own
        result = Bank.transfer_between_accounts(source_domain, dest_domain, amount)

        self.account_repo.save_balance(source_orm, result["source_balance"])
        self.account_repo.save_balance(dest_orm, result["destination_balance"])

        ref = generate_reference_no("TRF")
        out_txn = self.txn_repo.create(
            reference_no=ref, account_id=source_orm.account_id, related_account_id=dest_orm.account_id,
            transaction_type="TRANSFER_OUT", amount=amount, balance_after=result["source_balance"],
            description=description or f"Transfer to {to_account_number}",
        )
        self.txn_repo.create(
            reference_no=generate_reference_no("TRF"), account_id=dest_orm.account_id,
            related_account_id=source_orm.account_id, transaction_type="TRANSFER_IN",
            amount=amount, balance_after=result["destination_balance"],
            description=description or f"Transfer from {source_orm.account_number}",
        )
        return out_txn

    # ---------- Employee actions ----------
    def list_pending_accounts(self):
        return self.account_repo.list_pending()

    def approve_account(self, employee_user_id: int, account_id: int):
        employee = self.user_repo.get_employee_by_user_id(employee_user_id)
        if not employee:
            raise PermissionDeniedError("Only employees can approve accounts")
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise AccountNotFoundError()
        self.account_repo.approve(account, employee.employee_id)
        return account

    # ---------- Manager actions ----------
    def freeze_account(self, account_id: int):
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise AccountNotFoundError()
        self.account_repo.set_status(account, "FROZEN")
        return account

    def activate_account(self, account_id: int):
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise AccountNotFoundError()
        self.account_repo.set_status(account, "ACTIVE")
        return account

    def list_all_accounts(self):
        return self.account_repo.list_all()
