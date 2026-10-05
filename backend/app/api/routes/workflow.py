# Workflow API routes.

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_user
from backend.app.db.database import get_db
from backend.app.db.models import AuditLog, Patient, User
from backend.app.schemas.workflow import (
    WORKFLOW_STATUSES,
    WorkflowHistoryResponse,
    WorkflowProgressResponse,
    WorkflowResponse,
    WorkflowUpdateRequest,
)
from backend.app.services.workflow_service import (
    get_patient_workflow,
    get_workflow_step,
    get_workflow_steps,
    update_patient_workflow,
)


router = APIRouter(
    prefix="/workflow",
    tags=["Workflow"],
)


# ============================================================
# PATIENT VALIDATION
# ============================================================

def get_patient_or_404(
    patient_id: int,
    db: Session,
) -> Patient:
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

    return patient


# ============================================================
# CURRENT WORKFLOW
# ============================================================

@router.get(
    "/patient/{patient_id}",
    response_model=WorkflowResponse,
    status_code=status.HTTP_200_OK,
)
def get_current_workflow(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_patient_or_404(
        patient_id,
        db,
    )

    workflow = get_patient_workflow(
        db=db,
        patient_id=patient_id,
    )

    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return workflow


# ============================================================
# UPDATE WORKFLOW
# ============================================================

@router.post(
    "/update/{patient_id}",
    response_model=WorkflowResponse,
    status_code=status.HTTP_200_OK,
)
def update_workflow(
    patient_id: int,
    data: WorkflowUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update current patient workflow state.

    Workflow state is stored on the Patient model when the
    corresponding fields are available.
    """

    patient = get_patient_or_404(
        patient_id,
        db,
    )

    allowed_roles = {
        "Admin",
        "Senior Doctor",
        "Assistant Doctor",
        "Pathologist",
        "Radiologist",
        "Lab Staff",
    }

    current_role = None

    if getattr(current_user, "role", None) is not None:
        current_role = current_user.role.role_name

    if current_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update workflow",
        )

    if data.status is not None:
        if data.status not in WORKFLOW_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid workflow status",
            )

    if data.workflow_step is not None:
        if data.workflow_step < 1 or data.workflow_step > 11:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workflow step must be between 1 and 11",
            )

    workflow = update_patient_workflow(
        db=db,
        patient_id=patient_id,
        status=data.status,
        workflow_step=data.workflow_step,
    )

    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    # --------------------------------------------------------
    # Audit workflow change
    # --------------------------------------------------------

    audit_log = AuditLog(
        user_id=current_user.id,
        action="WORKFLOW_UPDATE",
        entity_type="patient_workflow",
        entity_id=patient.id,
        description=(
            f"Workflow updated. "
            f"Status={data.status or 'unchanged'}, "
            f"Step={data.workflow_step or 'unchanged'}"
        ),
    )

    db.add(audit_log)
    db.commit()

    result = get_patient_workflow(
        db=db,
        patient_id=patient_id,
    )

    return result


# ============================================================
# WORKFLOW PROGRESS
# ============================================================

@router.get(
    "/progress/{patient_id}",
    response_model=WorkflowProgressResponse,
    status_code=status.HTTP_200_OK,
)
def get_workflow_progress(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_patient_or_404(
        patient_id,
        db,
    )

    workflow = get_patient_workflow(
        db=db,
        patient_id=patient_id,
    )

    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient workflow not found",
        )

    return {
        "patient_id": workflow["patient_id"],
        "patient_code": workflow["patient_code"],
        "current_step": workflow["current_step"],
        "total_steps": workflow["total_steps"],
        "progress_percentage": workflow["progress_percentage"],
        "current_status": workflow["status"],
        "steps": get_workflow_steps(),
        "clinical_decision_support_only": True,
        "senior_doctor_final_authority": True,
    }


# ============================================================
# WORKFLOW HISTORY
# ============================================================

@router.get(
    "/history/{patient_id}",
    response_model=WorkflowHistoryResponse,
    status_code=status.HTTP_200_OK,
)
def get_workflow_history(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_patient_or_404(
        patient_id,
        db,
    )

    logs = (
        db.query(AuditLog)
        .filter(
            AuditLog.entity_type == "patient_workflow",
            AuditLog.entity_id == patient_id,
            AuditLog.action == "WORKFLOW_UPDATE",
        )
        .order_by(AuditLog.id.asc())
        .all()
    )

    items = []

    for log in logs:
        items.append(
            {
                "id": log.id,
                "patient_id": patient_id,
                "previous_status": None,
                "new_status": None,
                "previous_step": None,
                "new_step": None,
                "changed_by": log.user_id,
                "changed_at": log.created_at,
                "notes": log.description,
            }
        )

    return {
        "patient_id": patient_id,
        "items": items,
        "total": len(items),
    }


# ============================================================
# WORKFLOW STATUS LIST
# ============================================================

@router.get(
    "/statuses",
    status_code=status.HTTP_200_OK,
)
def get_workflow_statuses(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Return all supported patient statuses.
    """

    return {
        "total_statuses": len(WORKFLOW_STATUSES),
        "statuses": [
            {
                "step": index + 1,
                "status": workflow_status,
            }
            for index, workflow_status
            in enumerate(WORKFLOW_STATUSES)
        ],
        "clinical_workflow_steps": get_workflow_steps(),
    }


# ============================================================
# SINGLE WORKFLOW STEP
# ============================================================

@router.get(
    "/step/{step_number}",
    status_code=status.HTTP_200_OK,
)
def get_single_workflow_step(
    step_number: int,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Return details of one of the 11 main clinical workflow steps.
    """

    step = get_workflow_step(
        step_number,
    )

    if step is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow step not found",
        )

    return {
        "status": "success",
        "step": step,
    }