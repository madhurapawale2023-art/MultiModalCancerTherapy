# Specialist management and specialist opinion API routes.

import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_user
from backend.app.db.database import get_db
from backend.app.db.models import AuditLog, Patient, Role, User


router = APIRouter(
    prefix="/specialists",
    tags=["Specialists"],
)


# ============================================================
# SPECIALIST OPINION REQUEST
# ============================================================

class SpecialistOpinionRequest(BaseModel):
    """
    Specialist opinion submitted as a JSON request body.
    """

    patient_id: int = Field(..., ge=1)

    specialist_role: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    opinion: str = Field(
        ...,
        min_length=1,
    )

    recommendation: Optional[str] = None


# ============================================================
# CREATE SPECIALIST OPINION
# ============================================================

@router.post(
    "/opinion",
    status_code=status.HTTP_201_CREATED,
)
def create_specialist_opinion(
    payload: SpecialistOpinionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    patient_id = payload.patient_id
    specialist_role = payload.specialist_role
    opinion = payload.opinion
    recommendation = payload.recommendation
    """
    Store a specialist opinion as an audit event because the
    current database schema does not contain a SpecialistOpinion
    table.
    """

    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    allowed_roles = {
        "Pathologist",
        "Radiologist",
        "Senior Doctor",
        "Assistant Doctor",
    }

    current_role = None

    if getattr(current_user, "role", None) is not None:
        current_role = current_user.role.role_name

    if current_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission to add "
                "specialist opinions"
            ),
        )

    if specialist_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid specialist role",
        )

    if not opinion or not opinion.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Opinion cannot be empty",
        )

    opinion_data = {
        "patient_id": patient_id,
        "specialist_id": current_user.id,
        "specialist_role": specialist_role,
        "opinion": opinion.strip(),
        "recommendation": (
            recommendation.strip()
            if recommendation and recommendation.strip()
            else None
        ),
    }

    audit_log = AuditLog(
        user_id=current_user.id,
        action="CREATE_SPECIALIST_OPINION",
        entity_type="specialist_opinion",
        entity_id=patient_id,
        description=json.dumps(
            opinion_data,
            ensure_ascii=False,
        ),
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return {
        "id": audit_log.id,
        "patient_id": patient_id,
        "specialist_id": current_user.id,
        "specialist_role": specialist_role,
        "opinion": opinion.strip(),
        "recommendation": opinion_data["recommendation"],
        "created_at": audit_log.created_at,
        "message": "Specialist opinion added successfully",
    }


# ============================================================
# GET SPECIALIST OPINIONS FOR PATIENT
# ============================================================

@router.get(
    "/patient/{patient_id}",
    status_code=status.HTTP_200_OK,
)
def get_specialist_opinions(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get specialist opinions stored as audit events.
    """

    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    logs = (
        db.query(AuditLog)
        .filter(
            AuditLog.entity_type == "specialist_opinion",
            AuditLog.entity_id == patient_id,
            AuditLog.action == "CREATE_SPECIALIST_OPINION",
        )
        .order_by(AuditLog.id.desc())
        .all()
    )

    opinions: List[Dict[str, Any]] = []

    for item in logs:
        data: Dict[str, Any]

        try:
            data = json.loads(item.description or "{}")
        except (TypeError, json.JSONDecodeError):
            data = {
                "opinion": item.description or "",
            }

        opinions.append(
            {
                "id": item.id,
                "specialist_id": data.get(
                    "specialist_id",
                    item.user_id,
                ),
                "specialist_role": data.get(
                    "specialist_role"
                ),
                "opinion": data.get(
                    "opinion"
                ),
                "recommendation": data.get(
                    "recommendation"
                ),
                "created_at": item.created_at,
            }
        )

    return {
        "patient_id": patient_id,
        "total": len(opinions),
        "opinions": opinions,
    }


# ============================================================
# GET AVAILABLE SPECIALISTS
# ============================================================

@router.get(
    "/available",
    status_code=status.HTTP_200_OK,
)
def get_available_specialists(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Return active users belonging to specialist roles.
    """

    specialist_roles = [
        "Senior Doctor",
        "Assistant Doctor",
        "Pathologist",
        "Radiologist",
    ]

    specialists = (
        db.query(User)
        .join(
            Role,
            User.role_id == Role.id,
        )
        .filter(
            User.is_active.is_(True),
            Role.role_name.in_(specialist_roles),
        )
        .order_by(User.full_name.asc())
        .all()
    )

    return {
        "total": len(specialists),
        "specialists": [
            {
                "id": specialist.id,
                "username": specialist.username,
                "full_name": specialist.full_name,
                "email": specialist.email,
                "role": specialist.role.role_name
                if specialist.role is not None
                else None,
            }
            for specialist in specialists
        ],
    }