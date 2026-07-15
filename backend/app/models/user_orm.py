"""
user_orm.py
-----------
Pure SQLAlchemy data-mapper for the `users` table.

Design note (important for interviews): this project deliberately
separates two things that are often mixed together in student
projects:

1. ORM models (this file, `*_orm.py`) -- dumb rows-as-objects, whose
   only job is talking to MySQL via SQLAlchemy.
2. Domain classes (models/person.py, models/account.py, etc.) -- real
   OOP business objects with behaviour, validation and polymorphism.

The **Repository layer** is the bridge between the two: it loads ORM
rows and turns them into rich domain objects. This keeps persistence
concerns and business logic decoupled (Single Responsibility + easier
to explain each OOP concept in isolation).
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, func
from sqlalchemy.orm import relationship

from app.database import Base


class UserORM(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    phone = Column(String(20))
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum("CUSTOMER", "EMPLOYEE", "MANAGER", name="role_enum"), nullable=False)
    is_email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    customer_profile = relationship("CustomerORM", back_populates="user", uselist=False)
    employee_profile = relationship("EmployeeORM", back_populates="user", uselist=False)
    manager_profile = relationship("ManagerORM", back_populates="user", uselist=False)


class OTPCodeORM(Base):
    __tablename__ = "otp_codes"

    otp_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    otp_code = Column(String(10), nullable=False)
    purpose = Column(Enum("EMAIL_VERIFICATION", "PASSWORD_RESET", name="otp_purpose_enum"), nullable=False)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
