# Audit log API routes.

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_user
from backend.app.db.database import get_db
from backend.app.db.models import AuditLog, User


router = APIRouter(
    prefix="/api/audit",
    tags=["Audit Logs"],
)


# ============================================================
# CREATE AUDIT LOG
# ============================================================

@router.post(
    "/log",
    status_code=status.HTTP_201_CREATED,
)
def create_audit_log(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Create an audit log entry for the current user.
    """

    action = payload.get("action")

    if not action:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="action is required",
        )

    log = AuditLog(
        user_id=current_user.id,
        action=str(action),
        entity_type=payload.get("entity_type"),
        entity_id=payload.get("entity_id"),
        description=payload.get("description"),
        ip_address=payload.get("ip_address"),
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return {
        "status": "success",
        "message": "Audit log created successfully",
        "audit_log": {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "description": log.description,
            "ip_address": log.ip_address,
            "created_at": log.created_at,
        },
    }


# ============================================================
# GET AUDIT LOG BY ID
# ============================================================

@router.get(
    "/{audit_id}",
    status_code=status.HTTP_200_OK,
)
def get_audit_log(
    audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get one audit log entry.
    """

    log = (
        db.query(AuditLog)
        .filter(AuditLog.id == audit_id)
        .first()
    )

    if log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found",
        )

    return {
        "status": "success",
        "audit_log": {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "description": log.description,
            "ip_address": log.ip_address,
            "created_at": log.created_at,
        },
    }


# ============================================================
# LIST AUDIT LOGS
# ============================================================

@router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
def list_audit_logs(
    user_id: Optional[int] = Query(default=None),
    entity_type: Optional[str] = Query(default=None),
    entity_id: Optional[int] = Query(default=None),
    action: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    List audit logs with optional filters.
    """

    query = db.query(AuditLog)

    if user_id is not None:
        query = query.filter(
            AuditLog.user_id == user_id
        )

    if entity_type:
        query = query.filter(
            AuditLog.entity_type == entity_type
        )

    if entity_id is not None:
        query = query.filter(
            AuditLog.entity_id == entity_id
        )

    if action:
        query = query.filter(
            AuditLog.action == action
        )

    logs = (
        query
        .order_by(AuditLog.id.desc())
        .limit(limit)
        .all()
    )

    items = []

    for log in logs:
        items.append(
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "description": log.description,
                "ip_address": log.ip_address,
                "created_at": log.created_at,
            }
        )

    return {
        "status": "success",
        "items": items,
        "total": len(items),
    }


# ============================================================
# GET CURRENT USER AUDIT LOGS
# ============================================================

@router.get(
    "/user/me",
    status_code=status.HTTP_200_OK,
)
def get_my_audit_logs(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get audit logs created by the current user.
    """

    logs = (
        db.query(AuditLog)
        .filter(
            AuditLog.user_id == current_user.id
        )
        .order_by(AuditLog.id.desc())
        .limit(limit)
        .all()
    )

    items = [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "description": log.description,
            "ip_address": log.ip_address,
            "created_at": log.created_at,
        }
        for log in logs
    ]

    return {
        "status": "success",
        "user_id": current_user.id,
        "items": items,
        "total": len(items),
    }


# ============================================================
# GET AUDIT LOGS FOR ENTITY
# ============================================================

@router.get(
    "/entity/{entity_type}/{entity_id}",
    status_code=status.HTTP_200_OK,
)
def get_entity_audit_logs(
    entity_type: str,
    entity_id: int,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get audit logs associated with one entity.
    """

    logs = (
        db.query(AuditLog)
        .filter(
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == entity_id,
        )
        .order_by(AuditLog.id.desc())
        .limit(limit)
        .all()
    )

    items = [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "description": log.description,
            "ip_address": log.ip_address,
            "created_at": log.created_at,
        }
        for log in logs
    ]

    return {
        "status": "success",
        "entity_type": entity_type,
        "entity_id": entity_id,
        "items": items,
        "total": len(items),
    }