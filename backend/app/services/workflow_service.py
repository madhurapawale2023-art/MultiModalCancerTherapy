# Patient workflow and clinical progress business logic.

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.db.models import Patient


# ============================================================
# WORKFLOW DEFINITIONS
# ============================================================

WORKFLOW_STEPS: List[Dict[str, Any]] = [
    {
        "step": 1,
        "key": "registration",
        "name": "Patient Registration",
    },
    {
        "step": 2,
        "key": "clinical_assessment",
        "name": "Clinical Assessment",
    },
    {
        "step": 3,
        "key": "laboratory",
        "name": "Laboratory Evaluation",
    },
    {
        "step": 4,
        "key": "pathology",
        "name": "Pathology Evaluation",
    },
    {
        "step": 5,
        "key": "ultrasound",
        "name": "Ultrasound Evaluation",
    },
    {
        "step": 6,
        "key": "radiology_review",
        "name": "Radiology Review",
    },
    {
        "step": 7,
        "key": "ai_analysis",
        "name": "AI Analysis",
    },
    {
        "step": 8,
        "key": "multimodal_review",
        "name": "Multimodal Evidence Review",
    },
    {
        "step": 9,
        "key": "specialist_review",
        "name": "Specialist Review",
    },
    {
        "step": 10,
        "key": "treatment_plan",
        "name": "Treatment Planning",
    },
    {
        "step": 11,
        "key": "senior_doctor_decision",
        "name": "Senior Doctor Final Decision",
    },
]


# ============================================================
# PATIENT STATUS DEFINITIONS
# ============================================================

PATIENT_STATUSES: List[str] = [
    "Registered",
    "Clinical Assessment Pending",
    "Clinical Assessment Completed",
    "Laboratory Evaluation Pending",
    "Pathology Evaluation Pending",
    "Ultrasound Pending",
    "Radiology Review Pending",
    "AI Analysis Pending",
    "AI Analysis Completed",
    "Multimodal Review Pending",
    "Specialist Review Pending",
    "Treatment Planning Pending",
    "Treatment Plan Prepared",
    "Senior Doctor Review Pending",
    "Treatment Decision Pending",
    "Treatment Decision Approved",
    "Treatment Decision Deferred",
    "Follow-up Required",
    "Completed",
    "Archived",
]


# ============================================================
# INTERNAL ATTRIBUTE HELPERS
# ============================================================

def _patient_has_field(field_name: str) -> bool:
    """
    Check whether the Patient model contains a given field.
    """

    return hasattr(Patient, field_name)


def _set_patient_field(
    patient: Patient,
    field_name: str,
    value: Any,
) -> bool:
    """
    Safely set a Patient model field only when it exists.
    """

    if not _patient_has_field(field_name):
        return False

    setattr(patient, field_name, value)
    return True


# ============================================================
# WORKFLOW INFORMATION
# ============================================================

def get_workflow_steps() -> List[Dict[str, Any]]:
    """
    Return all clinical workflow steps.
    """

    return [dict(step) for step in WORKFLOW_STEPS]


def get_workflow_step(
    step_number: int,
) -> Optional[Dict[str, Any]]:
    """
    Return a single workflow step.
    """

    for step in WORKFLOW_STEPS:
        if step["step"] == step_number:
            return dict(step)

    return None


def get_statuses() -> List[str]:
    """
    Return all supported patient workflow statuses.
    """

    return list(PATIENT_STATUSES)


# ============================================================
# CURRENT PATIENT WORKFLOW STATE
# ============================================================

def get_patient_workflow(
    db: Session,
    patient_id: int,
) -> Optional[Dict[str, Any]]:
    """
    Return the current workflow information for a patient.
    """

    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if patient is None:
        return None

    current_status = getattr(
        patient,
        "status",
        None,
    )

    current_step = getattr(
        patient,
        "workflow_step",
        None,
    )

    if current_step is None:
        current_step = getattr(
            patient,
            "current_step",
            None,
        )

    if current_step is None:
        current_step = 1

    try:
        current_step = int(current_step)
    except (TypeError, ValueError):
        current_step = 1

    step_details = get_workflow_step(current_step)

    return {
        "patient_id": patient.id,
        "patient_code": patient.patient_code,
        "status": current_status or PATIENT_STATUSES[0],
        "current_step": current_step,
        "step_details": step_details,
        "total_steps": len(WORKFLOW_STEPS),
        "progress_percentage": round(
            (current_step / len(WORKFLOW_STEPS)) * 100,
            2,
        ),
        "clinical_decision_support_only": True,
        "senior_doctor_final_authority": True,
    }


# ============================================================
# UPDATE WORKFLOW
# ============================================================

def update_patient_workflow(
    db: Session,
    patient_id: int,
    status: Optional[str] = None,
    workflow_step: Optional[int] = None,
) -> Optional[Patient]:
    """
    Update patient workflow state.

    Only existing Patient fields are modified, making this
    service compatible with the current database model.
    """

    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if patient is None:
        return None

    if workflow_step is not None:
        if workflow_step < 1 or workflow_step > len(WORKFLOW_STEPS):
            raise ValueError(
                f"workflow_step must be between 1 and "
                f"{len(WORKFLOW_STEPS)}"
            )

        if _patient_has_field("workflow_step"):
            patient.workflow_step = workflow_step
        elif _patient_has_field("current_step"):
            patient.current_step = workflow_step

    if status is not None:
        if status not in PATIENT_STATUSES:
            raise ValueError(
                "Invalid patient workflow status"
            )

        _set_patient_field(
            patient,
            "status",
            status,
        )

    db.commit()
    db.refresh(patient)

    return patient


# ============================================================
# MOVE TO NEXT STEP
# ============================================================

def move_to_next_step(
    db: Session,
    patient_id: int,
) -> Optional[Patient]:
    """
    Move patient to the next workflow step.
    """

    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if patient is None:
        return None

    current_step = getattr(
        patient,
        "workflow_step",
        None,
    )

    if current_step is None:
        current_step = getattr(
            patient,
            "current_step",
            1,
        )

    try:
        current_step = int(current_step)
    except (TypeError, ValueError):
        current_step = 1

    next_step = min(
        current_step + 1,
        len(WORKFLOW_STEPS),
    )

    if _patient_has_field("workflow_step"):
        patient.workflow_step = next_step
    elif _patient_has_field("current_step"):
        patient.current_step = next_step

    step_details = get_workflow_step(next_step)

    if step_details is not None:
        default_status = PATIENT_STATUSES[
            min(next_step - 1, len(PATIENT_STATUSES) - 1)
        ]

        _set_patient_field(
            patient,
            "status",
            default_status,
        )

    db.commit()
    db.refresh(patient)

    return patient


# ============================================================
# WORKFLOW VALIDATION
# ============================================================

def can_access_step(
    current_step: int,
    requested_step: int,
) -> bool:
    """
    Check whether a requested workflow step is reachable.

    A later clinical step is not treated as completed merely
    because a UI request was made for it.
    """

    if current_step < 1:
        current_step = 1

    if requested_step < 1:
        return False

    if requested_step > len(WORKFLOW_STEPS):
        return False

    return requested_step <= current_step


def is_final_decision_step(
    step_number: int,
) -> bool:
    """
    Check whether the step is the Senior Doctor final
    treatment decision step.
    """

    return step_number == len(WORKFLOW_STEPS)


# ============================================================
# WORKFLOW COMPLETION
# ============================================================

def is_workflow_completed(
    patient: Patient,
) -> bool:
    """
    Determine whether the patient reached the final workflow step.
    """

    current_step = getattr(
        patient,
        "workflow_step",
        None,
    )

    if current_step is None:
        current_step = getattr(
            patient,
            "current_step",
            None,
        )

    try:
        current_step = int(current_step)
    except (TypeError, ValueError):
        return False

    return current_step >= len(WORKFLOW_STEPS)