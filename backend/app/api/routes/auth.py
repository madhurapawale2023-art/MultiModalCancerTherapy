from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_active_user
from backend.app.db.database import get_db
from backend.app.db.models import User
from backend.app.schemas.auth import (
    AuthUserResponse,
    LoginRequest,
    LoginResponse,
)
from backend.app.services.auth_service import login_user


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


# ============================================================
# Login
# ============================================================

@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user",
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    result = login_user(
        db=db,
        username=payload.username,
        password=payload.password,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return LoginResponse(
        access_token=result["access_token"],
        token_type=result.get("token_type", "bearer"),
        expires_in=result.get("expires_in", 1800),
        user=result["user"],
    )


# ============================================================
# Current Authenticated User
# ============================================================

@router.get(
    "/me",
    response_model=AuthUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user",
)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
):
    role_name = None

    if current_user.role is not None:
        role_name = current_user.role.role_name

    return AuthUserResponse(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        email=current_user.email,
        role=role_name,
        is_active=current_user.is_active,
    )