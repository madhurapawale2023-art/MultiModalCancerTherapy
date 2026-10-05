# ============================================================
# MultiModalCancerTherapy
# backend/app/core/security.py
# Password Hashing + JWT Security
# ============================================================

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
from jose import JWTError, jwt

from .config import settings


# ============================================================
# Password Hashing
# ============================================================

def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    """

    if not password:
        raise ValueError("Password cannot be empty.")

    password_bytes = password.encode("utf-8")

    salt = bcrypt.gensalt()

    hashed = bcrypt.hashpw(
        password_bytes,
        salt
    )

    return hashed.decode("utf-8")


# ============================================================
# Password Verification
# ============================================================

def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.
    """

    if not plain_password or not hashed_password:
        return False

    try:

        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )

    except (ValueError, TypeError):

        return False


# ============================================================
# JWT Token Creation
# ============================================================

def create_access_token(
    subject: str,
    role: Optional[str] = None,
    expires_minutes: Optional[int] = None,
    additional_claims: Optional[dict[str, Any]] = None
) -> str:
    """
    Create a JWT access token.
    """

    if expires_minutes is None:
        expires_minutes = (
            settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=expires_minutes
        )
    )

    payload: dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }

    if role is not None:
        payload["role"] = role

    if additional_claims:
        payload.update(additional_claims)

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


# ============================================================
# JWT Token Decode
# ============================================================

def decode_access_token(
    token: str
) -> Optional[dict[str, Any]]:
    """
    Decode and validate a JWT access token.
    """

    if not token:
        return None

    try:

        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[
                settings.JWT_ALGORITHM
            ]
        )

        subject = payload.get("sub")

        if not subject:
            return None

        return payload

    except JWTError:

        return None


# ============================================================
# Extract User ID from Token
# ============================================================

def get_token_subject(
    token: str
) -> Optional[str]:
    """
    Return the subject/user identifier from JWT.
    """

    payload = decode_access_token(token)

    if payload is None:
        return None

    subject = payload.get("sub")

    if subject is None:
        return None

    return str(subject)


# ============================================================
# Extract Role from Token
# ============================================================

def get_token_role(
    token: str
) -> Optional[str]:
    """
    Return the role stored in JWT.
    """

    payload = decode_access_token(token)

    if payload is None:
        return None

    role = payload.get("role")

    if role is None:
        return None

    return str(role)