"""
profile_orm.py
--------------
ORM models for customers, employees, managers and branches.
Each "profile" table has a 1:1 relationship back to `users`,
mirroring the Customer/Employee/Manager IS-A Person relationship
at the database level.
"""
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database import Base


class BranchORM(Base):
    __tablename__ = "branches"

    branch_id = Column(Integer, primary_key=True, index=True)
    branch_name = Column(String(100), nullable=False)
    branch_code = Column(String(20), nullable=False, unique=True)
    address = Column(String(255))
    city = Column(String(100))
    ifsc_code = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())


class CustomerORM(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)
    date_of_birth = Column(Date)
    address = Column(String(255))
    kyc_verified = Column(Boolean, default=False)
    verified_by_employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=True)

    user = relationship("UserORM", back_populates="customer_profile")
    accounts = relationship("AccountORM", back_populates="customer")


class EmployeeORM(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"))
    designation = Column(String(100), default="Bank Employee")
    created_by_manager_id = Column(Integer, ForeignKey("managers.manager_id"), nullable=True)

    user = relationship("UserORM", back_populates="employee_profile")


class ManagerORM(Base):
    __tablename__ = "managers"

    manager_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"))

    user = relationship("UserORM", back_populates="manager_profile")
