"""
create_first_manager.py
------------------------
Run this ONCE after setting up the database to create the very first
Manager login (since managers can't self-register, someone has to be
the first). Run from the backend/ folder:

    python create_first_manager.py

Then log in on the frontend with the email/password you enter here,
and use the Manager Dashboard to create Employees.
"""
import sys
import os

sys.path.append(os.path.dirname(__file__))

from app.database import SessionLocal, Base, engine
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password
from app.models import user_orm, profile_orm, banking_orm  # noqa: F401


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    repo = UserRepository(db)

    print("=== Create the first Manager account ===")
    full_name = input("Full name: ").strip() or "Bank Manager"
    email = input("Email: ").strip()
    password = input("Password (min 6 chars): ").strip()

    existing = repo.get_by_email(email)
    if existing:
        print(f"A user with email {email} already exists. Aborting.")
        return

    user = repo.create_user(
        full_name=full_name, email=email, phone=None,
        password_hash=hash_password(password), role="MANAGER",
    )
    user.is_email_verified = True
    db.commit()

    repo.create_manager_profile(user.user_id, branch_id=None)
    print(f"\nManager account created! You can now log in as {email}.")


if __name__ == "__main__":
    main()
