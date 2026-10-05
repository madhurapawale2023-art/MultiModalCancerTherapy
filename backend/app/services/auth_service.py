# ============================================================
# MultiModalCancerTherapy
# backend/app/services/auth_service.py
# Authentication Service
# ============================================================

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from backend.app.core.config import settings
from backend.app.core.security import (
    create_access_token,
    verify_password,
)
from backend.app.db.models import User


# ============================================================
# Find User by Username
# ============================================================

def get_user_by_username(
    db: Session,
    username: str
) -> Optional[User]:
    """
    Find an active or inactive user by username.
    """

    normalized_username = username.strip()

    if not normalized_username:
        return None

    query = (
        select(User)
        .options(
            joinedload(User.role)
        )
        .where(
            User.username == normalized_username
        )
    )

    return db.scalar(query)


# ============================================================
# Find User by ID
# ============================================================

def get_user_by_id(
    db: Session,
    user_id: int
) -> Optional[User]:
    """
    Find user by primary key.
    """

    query = (
        select(User)
        .options(
            joinedload(User.role)
        )
        .where(
            User.id == user_id
        )
    )

    return db.scalar(query)


# ============================================================
# Verify User Credentials
# ============================================================

def authenticate_user(
    db: Session,
    username: str,
    password: str
) -> Optional[User]:
    """
    Verify username and password.
    """

    user = get_user_by_username(
        db,
        username
    )

    if user is None:
        return None

    if not user.is_active:
        return None

    if not verify_password(
        password,
        user.password_hash
    ):
        return None

    return user


# ============================================================
# Get Role Name
# ============================================================

def get_user_role(
    user: User
) -> Optional[str]:
    """
    Return user's role name.
    """

    if user.role is None:
        return None

    return user.role.role_name


# ============================================================
# Create Login Token
# ============================================================

def create_user_access_token(
    user: User
) -> str:
    """
    Create JWT token for authenticated user.
    """

    role_name = get_user_role(user)

    return create_access_token(
        subject=str(user.id),
        role=role_name,
        additional_claims={
            "username": user.username,
            "full_name": user.full_name
        }
    )


# ============================================================
# Login User
# ============================================================

def login_user(
    db: Session,
    username: str,
    password: str
) -> Optional[dict]:
    """
    Authenticate user and return login information.
    """

    user = authenticate_user(
        db,
        username,
        password
    )

    if user is None:
        return None

    access_token = create_user_access_token(
        user
    )

    role_name = get_user_role(user)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": (
            settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        ),
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "role": role_name,
            "is_active": user.is_active
        }
    }