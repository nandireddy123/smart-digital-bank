"""
exceptions.py
-------------
Custom Exception classes for the banking domain.

Interview note: this demonstrates **Custom Exceptions** + **Inheritance**.
`BankingException` is the abstract-ish base; every specific business
error inherits from it, so a router can either catch a very specific
error (e.g. InsufficientFundsError) or catch the broad base class and
still handle it correctly. This is the same principle behind Python's
own exception hierarchy (ValueError -> Exception).
"""


class BankingException(Exception):
    """Base class for every custom exception in this project."""

    def __init__(self, message: str = "A banking error occurred"):
        self.message = message
        super().__init__(self.message)


class InsufficientFundsError(BankingException):
    def __init__(self, available: float, requested: float):
        message = (
            f"Insufficient funds: available ₹{available:.2f}, "
            f"requested ₹{requested:.2f}"
        )
        super().__init__(message)


class InvalidAmountError(BankingException):
    def __init__(self, amount: float):
        super().__init__(f"Invalid transaction amount: ₹{amount:.2f}")


class AccountNotActiveError(BankingException):
    def __init__(self, status: str):
        super().__init__(f"Account is not active (current status: {status})")


class AccountNotFoundError(BankingException):
    def __init__(self):
        super().__init__("Account not found")


class UserAlreadyExistsError(BankingException):
    def __init__(self, email: str):
        super().__init__(f"A user with email '{email}' already exists")


class InvalidCredentialsError(BankingException):
    def __init__(self):
        super().__init__("Invalid email or password")


class OTPInvalidOrExpiredError(BankingException):
    def __init__(self):
        super().__init__("OTP is invalid or has expired")


class EmailNotVerifiedError(BankingException):
    def __init__(self):
        super().__init__("Please verify your email before logging in")


class PermissionDeniedError(BankingException):
    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(message)


class MinimumBalanceViolationError(BankingException):
    def __init__(self, min_balance: float):
        super().__init__(f"Balance cannot go below the minimum required ₹{min_balance:.2f}")
