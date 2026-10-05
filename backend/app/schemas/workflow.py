# Workflow request and response schemas.

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# WORKFLOW STATUSES
# ============================================================

WORKFLOW_STATUSES: List[str] = [
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
# WORKFLOW STEP
# ============================================================

class WorkflowStep(BaseModel):
    step: int
    key: str
    name: str


# ============================================================
# WORKFLOW UPDATE REQUEST
# ============================================================

class WorkflowUpdateRequest(BaseModel):
    status: Optional[str] = None

    workflow_step: Optional[int] = Field(
        default=None,
        ge=1,
        le=11,
    )


# ============================================================
# WORKFLOW RESPONSE
# ============================================================

class WorkflowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    patient_id: int
    patient_code: str

    status: str

    current_step: int
    total_steps: int

    progress_percentage: float

    step_details: Optional[WorkflowStep] = None

    clinical_decision_support_only: bool = True
    senior_doctor_final_authority: bool = True


# ============================================================
# WORKFLOW PROGRESS RESPONSE
# ============================================================

class WorkflowProgressResponse(BaseModel):
    patient_id: int
    patient_code: str

    current_step: int
    total_steps: int
    progress_percentage: float

    current_status: str

    steps: List[WorkflowStep] = []

    clinical_decision_support_only: bool = True
    senior_doctor_final_authority: bool = True


# ============================================================
# WORKFLOW HISTORY ITEM
# ============================================================

class WorkflowHistoryItem(BaseModel):
    id: Optional[int] = None

    patient_id: int

    previous_status: Optional[str] = None
    new_status: Optional[str] = None

    previous_step: Optional[int] = None
    new_step: Optional[int] = None

    changed_by: Optional[int] = None

    changed_at: Optional[datetime] = None

    notes: Optional[str] = None


# ============================================================
# WORKFLOW HISTORY RESPONSE
# ============================================================

class WorkflowHistoryResponse(BaseModel):
    patient_id: int
    items: List[WorkflowHistoryItem] = []

    total: int = 0


# ============================================================
# WORKFLOW STATUS RESPONSE
# ============================================================

class WorkflowStatusListResponse(BaseModel):
    statuses: List[str] = WORKFLOW_STATUSES
    total: int = len(WORKFLOW_STATUSES)