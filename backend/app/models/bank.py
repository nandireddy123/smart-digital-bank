"""
bank.py
-------
`Bank` and `Branch` domain classes.

OOP concepts demonstrated here:

- **Aggregation**: `Bank` holds a list of `Branch` objects, but a
  `Branch` is meaningful and independently persisted even if it is
  never added to a particular in-memory `Bank` instance (weak "has-a").
  Contrast this with `Customer` -> `Account` in people.py, which is
  **Composition** (a stronger, owns-and-controls-lifecycle "has-a").

- **Association**: `Bank.transfer_between_accounts()` *uses* two
  `Account` objects that it neither owns nor creates -- they're just
  passed in. This is the weakest form of relationship: "Bank knows
  about Accounts and can operate on them," nothing more.

- **Dependency**: `TransactionService` (see services/transaction_service.py)
  *depends on* `Bank.transfer_between_accounts` and on the repository
  interfaces it's given in its constructor -- a dependency is simply
  "class A needs class B to do its job," typically shown by B being a
  parameter type in A's methods, which is exactly what happens in the
  service layer via constructor injection.
"""
from app.models.account import Account


class Branch:
    def __init__(self, branch_id: int, branch_name: str, branch_code: str, city: str | None = None):
        self._branch_id = branch_id
        self._branch_name = branch_name
        self._branch_code = branch_code
        self._city = city

    @property
    def branch_id(self) -> int:
        return self._branch_id

    @property
    def branch_name(self) -> str:
        return self._branch_name

    @property
    def branch_code(self) -> str:
        return self._branch_code

    def __repr__(self) -> str:
        return f"<Branch {self._branch_code} - {self._branch_name}>"


class Bank:
    def __init__(self, name: str = "Smart Digital Bank"):
        self._name = name
        self._branches: list[Branch] = []  # Aggregation

    @property
    def name(self) -> str:
        return self._name

    def add_branch(self, branch: Branch):
        self._branches.append(branch)

    @property
    def branches(self) -> list[Branch]:
        return list(self._branches)

    @staticmethod
    def transfer_between_accounts(source: Account, destination: Account, amount: float) -> dict:
        """Association: operates on two Account objects it does not own.
        Withdraws from source, deposits into destination, atomically
        from the caller's point of view (the service layer wraps this
        in a DB transaction so both sides commit or neither does)."""
        source.withdraw(amount)
        destination.deposit(amount)
        return {
            "source_balance": source.balance,
            "destination_balance": destination.balance,
        }
