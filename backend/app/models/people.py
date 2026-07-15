"""
people.py
---------
Concrete `Person` subclasses: Customer, Employee, Manager.

OOP concepts demonstrated here:

- **Inheritance**: all three classes extend `Person` and reuse its
  `full_name`, `email`, `phone` properties for free.

- **Polymorphism / Method Overriding**: each class overrides
  `get_dashboard_permissions()` and `get_role()` differently. Code
  that only knows it has "a Person" (e.g. a notification service that
  greets `person.full_name`) can call the *same* method name on any
  of the three and get behaviour appropriate to that subtype --
  without an if/elif chain checking the type.

- **Composition**: `Customer` *owns* a list of `Account` domain
  objects (`self._accounts`). If the Customer object is discarded,
  the in-memory list of Account objects goes with it -- a "has-a,
  cannot exist independently in this context" relationship.

- **Class Methods**: `Employee.hired_by_manager` is a `@classmethod`
  used as an alternate constructor, matching the business rule
  "Employees cannot self-register; only a Manager creates them."
"""
from app.models.person import Person


class Customer(Person):
    def __init__(self, user_id: int, full_name: str, email: str, phone: str | None,
                 customer_id: int, kyc_verified: bool = False):
        super().__init__(user_id, full_name, email, phone)
        self._customer_id = customer_id
        self._kyc_verified = kyc_verified
        self._accounts = []  # Composition: Customer owns its Account objects

    @property
    def customer_id(self) -> int:
        return self._customer_id

    @property
    def kyc_verified(self) -> bool:
        return self._kyc_verified

    def mark_kyc_verified(self):
        self._kyc_verified = True

    def add_account(self, account):
        """Composition in action -- an Account only makes sense as
        part of a Customer's portfolio in this domain."""
        self._accounts.append(account)

    @property
    def accounts(self) -> list:
        return list(self._accounts)  # return a copy -> protects internal state (encapsulation)

    def total_balance(self) -> float:
        return sum(acc.balance for acc in self._accounts)

    # ---------- Polymorphic overrides ----------
    def get_role(self) -> str:
        return "CUSTOMER"

    def get_dashboard_permissions(self) -> list[str]:
        return [
            "view_dashboard", "edit_profile", "change_password",
            "view_accounts", "open_account", "deposit", "withdraw",
            "transfer", "view_transactions", "search_transactions",
            "apply_loan", "view_loan_status", "notifications", "contact_support",
        ]


class Employee(Person):
    def __init__(self, user_id: int, full_name: str, email: str, phone: str | None,
                 employee_id: int, branch_id: int | None, created_by_manager_id: int | None):
        super().__init__(user_id, full_name, email, phone)
        self._employee_id = employee_id
        self._branch_id = branch_id
        self._created_by_manager_id = created_by_manager_id  # Association: Employee -> Manager (who hired them)

    @property
    def employee_id(self) -> int:
        return self._employee_id

    @property
    def branch_id(self) -> int | None:
        return self._branch_id

    @classmethod
    def hired_by_manager(cls, manager_id: int, user_id: int, full_name: str,
                          email: str, phone: str | None, employee_id: int, branch_id: int | None):
        """Alternate constructor (classmethod) enforcing the business
        rule that an Employee always comes into existence *because* a
        Manager created them."""
        return cls(user_id, full_name, email, phone, employee_id, branch_id, manager_id)

    def get_role(self) -> str:
        return "EMPLOYEE"

    def get_dashboard_permissions(self) -> list[str]:
        return [
            "view_dashboard", "verify_customers", "approve_accounts",
            "view_customers", "view_transactions", "help_customers", "search_customers",
        ]


class Manager(Person):
    def __init__(self, user_id: int, full_name: str, email: str, phone: str | None,
                 manager_id: int, branch_id: int | None):
        super().__init__(user_id, full_name, email, phone)
        self._manager_id = manager_id
        self._branch_id = branch_id

    @property
    def manager_id(self) -> int:
        return self._manager_id

    def get_role(self) -> str:
        return "MANAGER"

    def get_dashboard_permissions(self) -> list[str]:
        return [
            "view_dashboard", "manage_employees", "freeze_accounts",
            "activate_accounts", "approve_loans", "view_reports",
            "view_audit_logs", "manage_branches", "view_all_customers",
            "view_all_transactions",
        ]
