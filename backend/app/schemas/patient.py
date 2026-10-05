# ============================================================
# MultiModalCancerTherapy
# backend/app/schemas/patient.py
# Patient Request / Response Schemas
# ============================================================

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# Patient Base
# ============================================================

class PatientBase(BaseModel):

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    age: Optional[int] = Field(
        default=None,
        ge=0,
        le=150
    )

    sex: Optional[str] = Field(
        default=None,
        max_length=10
    )

    phone: Optional[str] = Field(
        default=None,
        max_length=30
    )

    email: Optional[str] = Field(
        default=None,
        max_length=150
    )

    address: Optional[str] = None

    status: str = Field(
        default="registered",
        max_length=50
    )


# ============================================================
# Patient Create
# ============================================================

class PatientCreate(PatientBase):
    """
    Data required when creating a patient.
    """

    pass


# ============================================================
# Patient Update
# ============================================================

class PatientUpdate(BaseModel):
    """
    All fields are optional for partial update.
    """

    full_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    age: Optional[int] = Field(
        default=None,
        ge=0,
        le=150
    )

    sex: Optional[str] = Field(
        default=None,
        max_length=10
    )

    phone: Optional[str] = Field(
        default=None,
        max_length=30
    )

    email: Optional[str] = Field(
        default=None,
        max_length=150
    )

    address: Optional[str] = None

    status: Optional[str] = Field(
        default=None,
        max_length=50
    )


# ============================================================
# Patient Response
# ============================================================

class PatientResponse(PatientBase):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    patient_code: str

    created_by: Optional[int] = None

    created_at: datetime

    updated_at: datetime


# ============================================================
# Patient List Response
# ============================================================

class PatientListResponse(BaseModel):

    items: list[PatientResponse]

    total: int