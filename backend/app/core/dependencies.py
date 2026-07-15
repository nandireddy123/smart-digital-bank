"""
dependencies.py
----------------
FastAPI dependencies used to protect routes:

- get_current_user: decodes the JWT and loads the User row.
- require_role(...): a dependency *factory* that returns a dependency
  restricting a route to one or more roles. This is how
  Role-Based Access Control (RBAC) is implemented across the app.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import decode_access_token
from app.models.user_orm import UserORM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserORM:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(UserORM).filter(UserORM.user_id == int(user_id)).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def require_role(*allowed_roles: str):
    """Dependency factory -> returns a dependency that only lets
    through users whose role is in `allowed_roles`.

    Usage:  Depends(require_role("MANAGER"))
            Depends(require_role("EMPLOYEE", "MANAGER"))
    """

    def role_checker(current_user: UserORM = Depends(get_current_user)) -> UserORM:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' is not authorized for this action",
            )
        return current_user

    return role_checker
