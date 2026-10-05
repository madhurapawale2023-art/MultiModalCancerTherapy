# ============================================================
# MultiModalCancerTherapy
# backend/app/core/dependencies.py
# Authentication + RBAC Dependencies
# ============================================================

from typing import Callable, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from backend.app.db.database import get_db
from backend.app.db.models import User
from backend.app.core.security import decode_access_token


# ============================================================
# OAuth2 Bearer Token
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)


# ============================================================
# Authentication Exception
# ============================================================

def authentication_error() -> HTTPException:
    """
    Standard authentication failure response.
    """

    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required.",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )


# ============================================================
# Get Current User
# ============================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Decode JWT and return the authenticated user.
    """

    payload = decode_access_token(token)

    if payload is None:
        raise authentication_error()

    subject = payload.get("sub")

    if subject is None:
        raise authentication_error()

    try:
        user_id = int(subject)

    except (TypeError, ValueError):
        raise authentication_error()

    query = (
        select(User)
        .options(
            joinedload(User.role)
        )
        .where(
            User.id == user_id
        )
    )

    user = db.scalar(query)

    if user is None:
        raise authentication_error()

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive."
        )

    return user


# ============================================================
# Current Active User
# ============================================================

def get_current_active_user(
    current_user: User = Depends(
        get_current_user
    )
) -> User:
    """
    Return active authenticated user.
    """

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user."
        )

    return current_user


# ============================================================
# Get Current User Role
# ============================================================

def get_current_user_role(
    current_user: User = Depends(
        get_current_active_user
    )
) -> Optional[str]:
    """
    Return current user's role name.
    """

    if current_user.role is None:
        return None

    return current_user.role.role_name


# ============================================================
# Require Specific Roles
# ============================================================

def require_roles(
    *allowed_roles: str
) -> Callable:
    """
    Create a dependency that allows only specific roles.

    Example:

        Depends(
            require_roles(
                "Admin",
                "Senior Doctor"
            )
        )
    """

    normalized_roles = {
        role.strip().lower()
        for role in allowed_roles
        if role and role.strip()
    }

    if not normalized_roles:
        raise ValueError(
            "At least one allowed role is required."
        )

    def role_dependency(
        current_user: User = Depends(
            get_current_active_user
        )
    ) -> User:

        if current_user.role is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User role is not assigned."
            )

        current_role = (
            current_user.role.role_name
            .strip()
            .lower()
        )

        if current_role not in normalized_roles:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission "
                    "to access this resource."
                )
            )

        return current_user

    return role_dependency


# ============================================================
# Convenience Role Dependencies
# ============================================================

def require_admin(
    current_user: User = Depends(
        require_roles("Admin")
    )
) -> User:
    """
    Admin-only access.
    """

    return current_user


def require_doctor(
    current_user: User = Depends(
        require_roles(
            "Senior Doctor",
            "Assistant Doctor"
        )
    )
) -> User:
    """
    Doctor-only access.
    """

    return current_user


def require_senior_doctor(
    current_user: User = Depends(
        require_roles("Senior Doctor")
    )
) -> User:
    """
    Senior Doctor-only access.
    """

    return current_user


def require_radiologist(
    current_user: User = Depends(
        require_roles("Radiologist")
    )
) -> User:
    """
    Radiologist-only access.
    """

    return current_user


def require_pathologist(
    current_user: User = Depends(
        require_roles("Pathologist")
    )
) -> User:
    """
    Pathologist-only access.
    """

    return current_user


def require_lab_staff(
    current_user: User = Depends(
        require_roles("Lab Staff")
    )
) -> User:
    """
    Lab Staff-only access.
    """

    return current_user