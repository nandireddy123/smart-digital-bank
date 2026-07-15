# OOP Concepts — Interview Cheat Sheet

Every concept below is demonstrated somewhere real in this codebase, not as a
toy example. Use this as your script: read the file, then explain it in your
own words using the "why" given here.

---

### 1. Encapsulation
**Where:** `backend/app/models/person.py`, `models/account.py`

`Person` and `Account` store their data in "protected" attributes
(`self._full_name`, `self._balance`) and only expose them through `@property`
getters. `Person.email` even has a **setter** that validates the format before
allowing a change — so external code can never put the object into an invalid
state.

> *"I encapsulate balance behind a property so nothing outside the Account
> class can set it directly to a negative number — every change has to go
> through `deposit()` or `withdraw()`, which enforce the business rules."*

### 2. Abstraction
**Where:** `models/person.py` (`Person(ABC)`), `models/account.py` (`Account(ABC)`)

Both are Python `ABC`s with `@abstractmethod`s. You can never do
`Person(...)` or `Account(...)` directly — Python raises a `TypeError`. They
define *what* every subtype must be able to do (`get_dashboard_permissions()`,
`calculate_interest()`) without saying *how*.

### 3. Inheritance
**Where:** `models/people.py` (`Customer`, `Employee`, `Manager` extend
`Person`), `models/account.py` (`SavingsAccount`, `CurrentAccount`,
`StudentAccount` extend `Account`)

Each subclass reuses the parent's shared behaviour (`full_name`, `deposit()`,
`withdraw()`) for free and only implements what's different about it.

### 4. Polymorphism / Method Overriding
**Where:** `Account.withdraw()` in `models/account.py`

`withdraw()` is a **template method**: the steps are fixed (validate amount →
check status → check limit → check minimum balance → apply change), but it
calls `self.get_withdrawal_limit()`, which `SavingsAccount`, `CurrentAccount`,
and `StudentAccount` each override with a different number. The
`AccountService` calls `account.withdraw(amount)` without ever checking
`if account_type == "SAVINGS"` — the correct behaviour just happens.

> *"This is real polymorphism, not just method overriding for its own sake —
> the service layer is completely decoupled from which account type it's
> holding."*

### 5. Composition
**Where:** `models/people.py` — `Customer._accounts`

A `Customer` owns a list of `Account` objects it creates and controls. If the
`Customer` object goes away, so does its in-memory list — a strong "has-a"
relationship.

### 6. Aggregation
**Where:** `models/bank.py` — `Bank._branches`

`Bank` holds a list of `Branch` objects, but a `Branch` is meaningful and
persisted on its own even if it's never added to a particular `Bank` instance
in memory — a weaker "has-a" than Composition. Compare this directly against
Customer→Account above; that contrast is the whole point of this concept.

### 7. Association
**Where:** `models/bank.py` — `Bank.transfer_between_accounts(source, destination, amount)`

`Bank` operates on two `Account` objects it neither created nor owns — they're
just passed in as parameters. This is the weakest relationship: "I know about
you and can call your methods," nothing more.

### 8. Dependency
**Where:** every `services/*.py` constructor, e.g. `AuthService.__init__(self, user_repo: UserRepository)`

Services never construct their own repositories — they receive them (Dependency
Injection). This is exactly what makes them unit-testable: pass in a fake
repository instead of hitting a real database.

### 9. Static Methods
**Where:** `Account.is_valid_amount()` in `models/account.py`

A pure utility check that doesn't touch `self` or `cls` — no reason for it to
be anything but `@staticmethod`.

### 10. Class Methods
**Where:** `Employee.hired_by_manager(...)` in `models/people.py`

An alternate constructor used from `services/misc_services.py`
(`EmployeeManagementService`) that encodes the business rule "an Employee
always comes into existence because a Manager created them."

### 11. Custom Exceptions
**Where:** `core/exceptions.py`

`BankingException` is the base class; `InsufficientFundsError`,
`InvalidAmountError`, `AccountNotActiveError`, `MinimumBalanceViolationError`,
etc. all inherit from it. `main.py` has **one** global exception handler that
catches `BankingException` and converts it to clean JSON — every router just
raises the specific error and trusts it'll be handled correctly.

### 12. SOLID Principles
- **S**ingle Responsibility: `config.py` only loads config; repositories only
  run queries; services only hold business rules; routers only handle HTTP.
- **O**pen/Closed: adding a `FixedDepositAccount` means adding one new class
  to `account.py` — zero changes needed to `AccountService` or any router.
- **L**iskov Substitution: anywhere an `Account` is expected, any subclass
  works correctly (see the polymorphism example above).
- **I**nterface Segregation: `Account`'s abstract methods are the *minimum*
  every account type needs — no bloated "god interface."
- **D**ependency Inversion: services depend on repository *classes* (which
  could be swapped for fakes/mocks), not on raw SQL.

### 13. Repository Pattern
**Where:** `repositories/*.py`

The **only** place in the entire app that writes SQLAlchemy queries. Services
never call `db.query(...)` directly. `AccountRepository.to_domain()` is the
specific bridge that turns a persisted row into a rich, polymorphic domain
object.

### 14. Service Layer
**Where:** `services/*.py`

Sits between routers (HTTP concerns) and repositories (persistence concerns).
This is where business rules actually live — e.g. `AccountService.transfer()`
loads two accounts, calls the polymorphic domain methods on them, and only
then persists the result.

---

## The two-layer design, in one sentence

> *"Every table has a boring `*_orm.py` SQLAlchemy class that only knows how
> to talk to MySQL, and a separate rich domain class (in `person.py`,
> `people.py`, `account.py`, `bank.py`) that has real behaviour and
> demonstrates OOP. The Repository layer is the only place that converts
> between the two — that separation is what let me put every OOP concept
> somewhere it actually earns its place, instead of forcing it into the
> database models."*

This single sentence answers "walk me through your architecture" in an
interview, and every concept above gives you a concrete follow-up example.
