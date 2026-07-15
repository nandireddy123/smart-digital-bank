"""
user_repository.py
-------------------
Repository Pattern: this class is the ONLY place in the app that
writes raw SQLAlchemy queries against the users/customers/employees/
managers/otp tables. Services never touch `db.query(...)` directly --
they call repository methods. This means if we ever swapped MySQL for
something else, only this file (and its siblings) would need to change.
"""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.user_orm import UserORM, OTPCodeORM
from app.models.profile_orm import CustomerORM, EmployeeORM, ManagerORM
from app.config import settings


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------- Users ----------
    def get_by_email(self, email: str) -> UserORM | None:
        return self.db.query(UserORM).filter(UserORM.email == email).first()

    def get_by_id(self, user_id: int) -> UserORM | None:
        return self.db.query(UserORM).filter(UserORM.user_id == user_id).first()

    def create_user(self, full_name: str, email: str, phone: str | None,
                     password_hash: str, role: str) -> UserORM:
        user = UserORM(
            full_name=full_name, email=email, phone=phone,
            password_hash=password_hash, role=role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def mark_email_verified(self, user: UserORM):
        user.is_email_verified = True
        self.db.commit()

    def update_password(self, user: UserORM, new_password_hash: str):
        user.password_hash = new_password_hash
        self.db.commit()

    def update_profile(self, user: UserORM, full_name: str | None, phone: str | None):
        if full_name:
            user.full_name = full_name
        if phone:
            user.phone = phone
        self.db.commit()
        self.db.refresh(user)
        return user

    # ---------- Profiles ----------
    def create_customer_profile(self, user_id: int) -> CustomerORM:
        customer = CustomerORM(user_id=user_id)
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def get_customer_by_user_id(self, user_id: int) -> CustomerORM | None:
        return self.db.query(CustomerORM).filter(CustomerORM.user_id == user_id).first()

    def get_customer_by_id(self, customer_id: int) -> CustomerORM | None:
        return self.db.query(CustomerORM).filter(CustomerORM.customer_id == customer_id).first()

    def list_customers(self) -> list[CustomerORM]:
        return self.db.query(CustomerORM).all()

    def verify_kyc(self, customer: CustomerORM, employee_id: int):
        customer.kyc_verified = True
        customer.verified_by_employee_id = employee_id
        self.db.commit()

    def create_employee_profile(self, user_id: int, branch_id: int | None, created_by_manager_id: int) -> EmployeeORM:
        employee = EmployeeORM(user_id=user_id, branch_id=branch_id, created_by_manager_id=created_by_manager_id)
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)
        return employee

    def get_employee_by_user_id(self, user_id: int) -> EmployeeORM | None:
        return self.db.query(EmployeeORM).filter(EmployeeORM.user_id == user_id).first()

    def list_employees(self) -> list[EmployeeORM]:
        return self.db.query(EmployeeORM).all()

    def create_manager_profile(self, user_id: int, branch_id: int | None) -> ManagerORM:
        manager = ManagerORM(user_id=user_id, branch_id=branch_id)
        self.db.add(manager)
        self.db.commit()
        self.db.refresh(manager)
        return manager

    def get_manager_by_user_id(self, user_id: int) -> ManagerORM | None:
        return self.db.query(ManagerORM).filter(ManagerORM.user_id == user_id).first()

    # ---------- OTP ----------
    def create_otp(self, user_id: int, otp_code: str, purpose: str) -> OTPCodeORM:
        otp = OTPCodeORM(
            user_id=user_id, otp_code=otp_code, purpose=purpose,
            expires_at=datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
        )
        self.db.add(otp)
        self.db.commit()
        self.db.refresh(otp)
        return otp

    def get_valid_otp(self, user_id: int, otp_code: str, purpose: str) -> OTPCodeORM | None:
        return (
            self.db.query(OTPCodeORM)
            .filter(
                OTPCodeORM.user_id == user_id,
                OTPCodeORM.otp_code == otp_code,
                OTPCodeORM.purpose == purpose,
                OTPCodeORM.is_used.is_(False),
                OTPCodeORM.expires_at >= datetime.utcnow(),
            )
            .order_by(OTPCodeORM.otp_id.desc())
            .first()
        )

    def mark_otp_used(self, otp: OTPCodeORM):
        otp.is_used = True
        self.db.commit()
