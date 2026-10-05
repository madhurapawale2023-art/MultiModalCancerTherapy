# ============================================================
# MultiModalCancerTherapy
# backend/app/schemas/auth.py
# Authentication Schemas
# ============================================================

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# Login Request
# ============================================================

class LoginRequest(BaseModel):

    username: str = Field(
        ...,
        min_length=3,
        max_length=100
    )

    password: str = Field(
        ...,
        min_length=1,
        max_length=128
    )


# ============================================================
# Token Response
# ============================================================

class TokenResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"

    expires_in: int


# ============================================================
# User Response
# ============================================================

class UserResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    username: str

    full_name: str

    email: Optional[str] = None

    role: Optional[str] = None

    is_active: bool


# ============================================================
# Current User Response
# ============================================================

class CurrentUserResponse(UserResponse):
    """
    Current authenticated user.
    """

    pass


# ============================================================
# Authenticated User Response
# ============================================================

class AuthUserResponse(UserResponse):
    """
    Backward-compatible authenticated user response.
    """

    pass


# ============================================================
# Login Response
# ============================================================

class LoginResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"

    expires_in: int

    user: UserResponse


# ============================================================
# Generic Message Response
# ============================================================

class MessageResponse(BaseModel):

    message: str