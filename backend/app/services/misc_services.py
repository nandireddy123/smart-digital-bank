"""
misc_services.py
-----------------
Remaining service-layer classes: transaction search/history, loans,
manager-creates-employee, notifications, support tickets.
"""
from app.repositories.account_repository import AccountRepository, TransactionRepository
from app.repositories.user_repository import UserRepository
from app.repositories.misc_repository import (
    LoanRepository, NotificationRepository, SupportRepository,
)
from app.core.exceptions import AccountNotFoundError, PermissionDeniedError
from app.core.security import hash_password
from app.models.people import Employee


class TransactionService:
    def __init__(self, account_repo: AccountRepository, txn_repo: TransactionRepository,
                 user_repo: UserRepository):
        self.account_repo = account_repo
        self.txn_repo = txn_repo
        self.user_repo = user_repo

    def _assert_owns_account(self, account_id: int, customer_user_id: int):
        customer = self.user_repo.get_customer_by_user_id(customer_user_id)
        account = self.account_repo.get_by_id(account_id)
        if not account or not customer or account.customer_id != customer.customer_id:
            raise AccountNotFoundError()
        return account

    def history(self, customer_user_id: int, account_id: int):
        self._assert_owns_account(account_id, customer_user_id)
        return self.txn_repo.list_by_account(account_id)

    def search(self, customer_user_id: int, account_id: int, keyword: str):
        self._assert_owns_account(account_id, customer_user_id)
        return self.txn_repo.search_by_account(account_id, keyword)

    def all_transactions_for_staff(self):
        return self.txn_repo.list_all()


class LoanService:
    LOAN_INTEREST_RATE = 9.5  # flat demo rate

    def __init__(self, loan_repo: LoanRepository, account_repo: AccountRepository,
                 user_repo: UserRepository):
        self.loan_repo = loan_repo
        self.account_repo = account_repo
        self.user_repo = user_repo

    def apply(self, customer_user_id: int, account_id: int, loan_type: str,
              principal_amount: float, tenure_months: int):
        customer = self.user_repo.get_customer_by_user_id(customer_user_id)
        account = self.account_repo.get_by_id(account_id)
        if not customer or not account or account.customer_id != customer.customer_id:
            raise AccountNotFoundError()

        return self.loan_repo.create(
            customer_id=customer.customer_id, account_id=account_id, loan_type=loan_type,
            principal_amount=principal_amount, interest_rate=self.LOAN_INTEREST_RATE,
            tenure_months=tenure_months,
        )

    def my_loans(self, customer_user_id: int):
        customer = self.user_repo.get_customer_by_user_id(customer_user_id)
        if not customer:
            return []
        return self.loan_repo.list_by_customer(customer.customer_id)

    def pending_loans(self):
        return self.loan_repo.list_pending()

    def decide(self, manager_user_id: int, loan_id: int, approve: bool):
        manager = self.user_repo.get_manager_by_user_id(manager_user_id)
        if not manager:
            raise PermissionDeniedError("Only managers can approve loans")
        loan = self.loan_repo.get_by_id(loan_id)
        if not loan:
            raise AccountNotFoundError()
        self.loan_repo.decide(loan, approve, manager.manager_id)

        if approve:
            account = self.account_repo.get_by_id(loan.account_id)
            domain_account = self.account_repo.to_domain(account)
            new_balance = domain_account.deposit(float(loan.principal_amount))
            self.account_repo.save_balance(account, new_balance)
        return loan


class EmployeeManagementService:
    """Manager-only: create Employee accounts. Demonstrates the
    `Employee.hired_by_manager` classmethod constructor being used
    from the service layer."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def create_employee(self, manager_user_id: int, full_name: str, email: str,
                         phone: str | None, password: str, branch_id: int | None):
        manager = self.user_repo.get_manager_by_user_id(manager_user_id)
        if not manager:
            raise PermissionDeniedError("Only a manager can create employees")

        existing = self.user_repo.get_by_email(email)
        if existing:
            from app.core.exceptions import UserAlreadyExistsError
            raise UserAlreadyExistsError(email)

        user = self.user_repo.create_user(
            full_name=full_name, email=email, phone=phone,
            password_hash=hash_password(password), role="EMPLOYEE",
        )
        user.is_email_verified = True  # staff accounts don't need self-verification
        self.user_repo.db.commit()

        employee_orm = self.user_repo.create_employee_profile(
            user_id=user.user_id, branch_id=branch_id, created_by_manager_id=manager.manager_id,
        )

        # Domain object built via its classmethod alternate constructor
        employee_domain = Employee.hired_by_manager(
            manager_id=manager.manager_id, user_id=user.user_id, full_name=full_name,
            email=email, phone=phone, employee_id=employee_orm.employee_id, branch_id=branch_id,
        )
        return employee_domain


class NotificationService:
    def __init__(self, notif_repo: NotificationRepository):
        self.notif_repo = notif_repo

    def notify(self, user_id: int, title: str, message: str):
        return self.notif_repo.create(user_id, title, message)

    def my_notifications(self, user_id: int):
        return self.notif_repo.list_by_user(user_id)


class SupportService:
    def __init__(self, support_repo: SupportRepository):
        self.support_repo = support_repo

    def create_ticket(self, user_id: int, subject: str, message: str):
        return self.support_repo.create(user_id, subject, message)

    def my_tickets(self, user_id: int):
        return self.support_repo.list_by_user(user_id)
