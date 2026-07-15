"""
banking_orm.py
--------------
ORM models for accounts, transactions, cards, loans, notifications,
audit logs and support tickets.
"""
from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, Date, DateTime,
    Enum, ForeignKey, func
)
from sqlalchemy.orm import relationship

from app.database import Base


class AccountORM(Base):
    __tablename__ = "accounts"

    account_id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(20), nullable=False, unique=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"))
    account_type = Column(Enum("SAVINGS", "CURRENT", "STUDENT", name="account_type_enum"), nullable=False)
    balance = Column(Numeric(15, 2), nullable=False, default=0)
    status = Column(Enum("PENDING", "ACTIVE", "FROZEN", "CLOSED", name="account_status_enum"), default="PENDING")
    approved_by_employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=True)
    interest_rate = Column(Numeric(5, 2), default=0)
    min_balance = Column(Numeric(15, 2), default=0)
    created_at = Column(DateTime, server_default=func.now())

    customer = relationship("CustomerORM", back_populates="accounts")
    transactions = relationship("TransactionORM", foreign_keys="TransactionORM.account_id", back_populates="account")


class TransactionORM(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    reference_no = Column(String(40), nullable=False, unique=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=False)
    related_account_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=True)
    transaction_type = Column(
        Enum("DEPOSIT", "WITHDRAW", "TRANSFER_OUT", "TRANSFER_IN", name="txn_type_enum"),
        nullable=False,
    )
    amount = Column(Numeric(15, 2), nullable=False)
    balance_after = Column(Numeric(15, 2), nullable=False)
    description = Column(String(255))
    status = Column(Enum("SUCCESS", "FAILED", "PENDING", name="txn_status_enum"), default="SUCCESS")
    created_at = Column(DateTime, server_default=func.now())

    account = relationship("AccountORM", foreign_keys=[account_id], back_populates="transactions")


class CardORM(Base):
    __tablename__ = "cards"

    card_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=False)
    card_number = Column(String(20), nullable=False, unique=True)
    card_type = Column(Enum("DEBIT", name="card_type_enum"), default="DEBIT")
    expiry_date = Column(Date, nullable=False)
    cvv_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class LoanORM(Base):
    __tablename__ = "loans"

    loan_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=False)
    loan_type = Column(String(50), nullable=False)
    principal_amount = Column(Numeric(15, 2), nullable=False)
    interest_rate = Column(Numeric(5, 2), nullable=False)
    tenure_months = Column(Integer, nullable=False)
    status = Column(Enum("PENDING", "APPROVED", "REJECTED", "CLOSED", name="loan_status_enum"), default="PENDING")
    approved_by_manager_id = Column(Integer, ForeignKey("managers.manager_id"), nullable=True)
    applied_at = Column(DateTime, server_default=func.now())
    decided_at = Column(DateTime, nullable=True)


class NotificationORM(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    title = Column(String(150), nullable=False)
    message = Column(String(500), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class AuditLogORM(Base):
    __tablename__ = "audit_logs"

    audit_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    action = Column(String(150), nullable=False)
    details = Column(String(500))
    ip_address = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())


class SupportTicketORM(Base):
    __tablename__ = "support_tickets"

    ticket_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    subject = Column(String(150), nullable=False)
    message = Column(String(1000), nullable=False)
    status = Column(Enum("OPEN", "IN_PROGRESS", "RESOLVED", name="ticket_status_enum"), default="OPEN")
    created_at = Column(DateTime, server_default=func.now())
