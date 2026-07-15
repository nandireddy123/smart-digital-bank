"""
test_account_domain.py
-----------------------
Unit tests for the pure-Python domain layer (models/account.py,
models/people.py). These need NO database connection -- that's the
whole point of keeping business logic in domain objects separate from
the ORM/repository layer. Run with:

    cd backend
    pytest ../tests/test_account_domain.py -v
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from app.models.account import SavingsAccount, CurrentAccount, StudentAccount, build_account
from app.core.exceptions import (
    InsufficientFundsError, InvalidAmountError, MinimumBalanceViolationError, AccountNotActiveError,
)


def make_active_savings(balance=5000.0):
    acc = SavingsAccount(account_id=1, account_number="123", customer_id=1,
                          balance=balance, status="ACTIVE", min_balance=1000.0)
    return acc


def test_deposit_increases_balance():
    acc = make_active_savings(1000)
    new_balance = acc.deposit(500)
    assert new_balance == 1500
    assert acc.balance == 1500


def test_deposit_rejects_non_positive_amount():
    acc = make_active_savings(1000)
    with pytest.raises(InvalidAmountError):
        acc.deposit(0)
    with pytest.raises(InvalidAmountError):
        acc.deposit(-50)


def test_withdraw_respects_minimum_balance():
    acc = make_active_savings(1500)  # min_balance=1000
    with pytest.raises(MinimumBalanceViolationError):
        acc.withdraw(600)  # would leave 900, below the 1000 minimum


def test_withdraw_respects_savings_limit():
    acc = make_active_savings(100_000)
    with pytest.raises(InvalidAmountError):
        acc.withdraw(60_000)  # savings limit is 50,000 per transaction


def test_withdraw_insufficient_funds():
    acc = make_active_savings(1000)
    acc._min_balance = 0  # bypass min-balance rule to isolate this test
    with pytest.raises(InsufficientFundsError):
        acc.withdraw(5000)


def test_frozen_account_blocks_transactions():
    acc = make_active_savings(1000)
    acc.freeze()
    with pytest.raises(AccountNotActiveError):
        acc.deposit(100)
    with pytest.raises(AccountNotActiveError):
        acc.withdraw(100)


def test_polymorphic_withdrawal_limits_differ_by_type():
    savings = SavingsAccount(1, "1", 1, 100_000, "ACTIVE", 0)
    current = CurrentAccount(2, "2", 1, 100_000, "ACTIVE", 0)
    student = StudentAccount(3, "3", 1, 100_000, "ACTIVE", 0)

    assert savings.get_withdrawal_limit() == 50_000
    assert current.get_withdrawal_limit() == 500_000
    assert student.get_withdrawal_limit() == 10_000

    # Same method call, three different behaviours -- polymorphism.
    with pytest.raises(InvalidAmountError):
        student.withdraw(20_000)
    assert current.withdraw(20_000) == 80_000


def test_interest_calculation_differs_by_type():
    savings = SavingsAccount(1, "1", 1, 10_000, "ACTIVE", 0)
    current = CurrentAccount(2, "2", 1, 10_000, "ACTIVE", 0)
    student = StudentAccount(3, "3", 1, 10_000, "ACTIVE", 0)

    assert savings.calculate_interest() == 400.0   # 4%
    assert current.calculate_interest() == 0.0     # 0%
    assert student.calculate_interest() == 500.0   # 5%


def test_build_account_factory_returns_correct_subclass():
    acc = build_account("STUDENT", account_id=1, account_number="1", customer_id=1, balance=0)
    assert isinstance(acc, StudentAccount)
    assert acc.account_type() == "STUDENT"


def test_build_account_rejects_unknown_type():
    with pytest.raises(ValueError):
        build_account("CRYPTO", account_id=1, account_number="1", customer_id=1, balance=0)


def test_transfer_between_accounts_moves_money_atomically():
    from app.models.bank import Bank
    source = make_active_savings(5000)
    dest = CurrentAccount(2, "2", 2, 1000, "ACTIVE", 0)

    result = Bank.transfer_between_accounts(source, dest, 1000)

    assert result["source_balance"] == 4000
    assert result["destination_balance"] == 2000
