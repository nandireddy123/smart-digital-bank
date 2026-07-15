"""
account.py
----------
Abstract `Account` base class + three concrete account types.

OOP concepts demonstrated here:

- **Abstraction**: `Account` declares `calculate_interest()` and
  `get_withdrawal_limit()` as abstract -- every account type MUST
  decide its own interest and withdrawal rules.

- **Polymorphism / Method Overriding**: `withdraw()` in the base class
  is a *template method* -- it defines the fixed steps (validate
  amount -> check status -> check the withdrawal limit -> apply the
  balance change) but calls `self.get_withdrawal_limit()`, which each
  subclass overrides differently. The account service never needs to
  know or care *which* subclass it's holding -- `account.withdraw(500)`
  just works correctly for Savings, Current or Student accounts.

- **Static Methods**: `Account.is_valid_amount()` doesn't need `self`
  or `cls` -- it's a pure utility check, so it's a `@staticmethod`.

- **Custom Exceptions**: raises `InsufficientFundsError`,
  `InvalidAmountError`, `AccountNotActiveError`,
  `MinimumBalanceViolationError` from core/exceptions.py.
"""
from abc import ABC, abstractmethod
from decimal import Decimal

from app.core.exceptions import (
    InsufficientFundsError,
    InvalidAmountError,
    AccountNotActiveError,
    MinimumBalanceViolationError,
)


class Account(ABC):
    def __init__(self, account_id: int, account_number: str, customer_id: int,
                 balance: float, status: str = "PENDING", min_balance: float = 0.0):
        self._account_id = account_id
        self._account_number = account_number
        self._customer_id = customer_id
        self._balance = Decimal(str(balance))
        self._status = status
        self._min_balance = Decimal(str(min_balance))

    # ---------- Encapsulated properties ----------
    @property
    def account_id(self) -> int:
        return self._account_id

    @property
    def account_number(self) -> str:
        return self._account_number

    @property
    def balance(self) -> float:
        return float(self._balance)

    @property
    def status(self) -> str:
        return self._status

    def activate(self):
        self._status = "ACTIVE"

    def freeze(self):
        self._status = "FROZEN"

    @staticmethod
    def is_valid_amount(amount: float) -> bool:
        """Pure utility -- doesn't touch instance/class state, so it's static."""
        return amount is not None and amount > 0

    def _ensure_active(self):
        if self._status != "ACTIVE":
            raise AccountNotActiveError(self._status)

    # ---------- Abstract -- every subtype implements its own rule ----------
    @abstractmethod
    def calculate_interest(self) -> float:
        """Returns the interest amount for the current balance."""
        raise NotImplementedError

    @abstractmethod
    def get_withdrawal_limit(self) -> float:
        """Returns the max amount that can be withdrawn in one transaction."""
        raise NotImplementedError

    @abstractmethod
    def account_type(self) -> str:
        raise NotImplementedError

    # ---------- Template methods (shared behaviour, built on the abstract hooks) ----------
    def deposit(self, amount: float) -> float:
        if not Account.is_valid_amount(amount):
            raise InvalidAmountError(amount)
        self._ensure_active()
        self._balance += Decimal(str(amount))
        return float(self._balance)

    def withdraw(self, amount: float) -> float:
        if not Account.is_valid_amount(amount):
            raise InvalidAmountError(amount)
        self._ensure_active()

        limit = self.get_withdrawal_limit()
        if amount > limit:
            raise InvalidAmountError(amount)  # exceeds this account type's per-transaction limit

        remaining = self._balance - Decimal(str(amount))
        if remaining < 0:
            raise InsufficientFundsError(float(self._balance), amount)
        if remaining < self._min_balance:
            raise MinimumBalanceViolationError(float(self._min_balance))

        self._balance = remaining
        return float(self._balance)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self._account_number} balance=₹{self._balance}>"


class SavingsAccount(Account):
    """Higher interest, lower per-transaction withdrawal limit."""
    INTEREST_RATE = 0.04  # 4% p.a.
    WITHDRAWAL_LIMIT = 50_000.0
    DEFAULT_MIN_BALANCE = 1_000.0

    def calculate_interest(self) -> float:
        return round(self.balance * self.INTEREST_RATE, 2)

    def get_withdrawal_limit(self) -> float:
        return self.WITHDRAWAL_LIMIT

    def account_type(self) -> str:
        return "SAVINGS"


class CurrentAccount(Account):
    """No interest, built for businesses -- higher withdrawal limit, no min balance."""
    INTEREST_RATE = 0.0
    WITHDRAWAL_LIMIT = 500_000.0
    DEFAULT_MIN_BALANCE = 0.0

    def calculate_interest(self) -> float:
        return 0.0

    def get_withdrawal_limit(self) -> float:
        return self.WITHDRAWAL_LIMIT

    def account_type(self) -> str:
        return "CURRENT"


class StudentAccount(Account):
    """Slightly higher interest than Savings to encourage saving, very
    small withdrawal limit, zero minimum balance."""
    INTEREST_RATE = 0.05
    WITHDRAWAL_LIMIT = 10_000.0
    DEFAULT_MIN_BALANCE = 0.0

    def calculate_interest(self) -> float:
        return round(self.balance * self.INTEREST_RATE, 2)

    def get_withdrawal_limit(self) -> float:
        return self.WITHDRAWAL_LIMIT

    def account_type(self) -> str:
        return "STUDENT"


ACCOUNT_CLASS_MAP = {
    "SAVINGS": SavingsAccount,
    "CURRENT": CurrentAccount,
    "STUDENT": StudentAccount,
}


def build_account(account_type: str, **kwargs) -> Account:
    """Simple Factory function -- given a string account_type coming
    from the database, returns the correct polymorphic Account
    subclass instance. Keeps 'if type == ...' logic in exactly one
    place instead of scattered through the service layer."""
    account_cls = ACCOUNT_CLASS_MAP.get(account_type)
    if account_cls is None:
        raise ValueError(f"Unknown account type: {account_type}")
    return account_cls(**kwargs)
