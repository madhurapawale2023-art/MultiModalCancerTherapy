# ============================================================
# MultiModalCancerTherapy
# backend/app/schemas/clinical.py
# Clinical Data Schemas
# Based on thyroidDF.csv
# ============================================================

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# Clinical Base
# ============================================================

class ClinicalBase(BaseModel):

    age: Optional[int] = Field(
        default=None,
        ge=0,
        le=150
    )

    sex: Optional[str] = Field(
        default=None,
        max_length=10
    )

    # --------------------------------------------------------
    # Clinical boolean features
    # --------------------------------------------------------

    on_thyroxine: Optional[bool] = None

    query_on_thyroxine: Optional[bool] = None

    on_antithyroid_meds: Optional[bool] = None

    sick: Optional[bool] = None

    pregnant: Optional[bool] = None

    thyroid_surgery: Optional[bool] = None

    i131_treatment: Optional[bool] = None

    query_hypothyroid: Optional[bool] = None

    query_hyperthyroid: Optional[bool] = None

    lithium: Optional[bool] = None

    goitre: Optional[bool] = None

    tumor: Optional[bool] = None

    hypopituitary: Optional[bool] = None

    psych: Optional[bool] = None

    # --------------------------------------------------------
    # Measurement flags
    # --------------------------------------------------------

    tsh_measured: Optional[bool] = None

    t3_measured: Optional[bool] = None

    tt4_measured: Optional[bool] = None

    t4u_measured: Optional[bool] = None

    fti_measured: Optional[bool] = None

    tbg_measured: Optional[bool] = None

    # --------------------------------------------------------
    # Laboratory values
    # --------------------------------------------------------

    tsh: Optional[Decimal] = None

    t3: Optional[Decimal] = None

    tt4: Optional[Decimal] = None

    t4u: Optional[Decimal] = None

    fti: Optional[Decimal] = None

    tbg: Optional[Decimal] = None

    # --------------------------------------------------------
    # Other clinical information
    # --------------------------------------------------------

    referral_source: Optional[str] = Field(
        default=None,
        max_length=50
    )

    clinical_notes: Optional[str] = None


# ============================================================
# Clinical Create
# ============================================================

class ClinicalCreate(ClinicalBase):

    patient_id: int

    source_patient_id: Optional[int] = None

    target_code: Optional[str] = Field(
        default=None,
        max_length=20
    )


# ============================================================
# Clinical Update
# ============================================================

class ClinicalUpdate(BaseModel):

    age: Optional[int] = Field(
        default=None,
        ge=0,
        le=150
    )

    sex: Optional[str] = Field(
        default=None,
        max_length=10
    )

    on_thyroxine: Optional[bool] = None
    query_on_thyroxine: Optional[bool] = None
    on_antithyroid_meds: Optional[bool] = None
    sick: Optional[bool] = None
    pregnant: Optional[bool] = None
    thyroid_surgery: Optional[bool] = None
    i131_treatment: Optional[bool] = None
    query_hypothyroid: Optional[bool] = None
    query_hyperthyroid: Optional[bool] = None
    lithium: Optional[bool] = None
    goitre: Optional[bool] = None
    tumor: Optional[bool] = None
    hypopituitary: Optional[bool] = None
    psych: Optional[bool] = None

    tsh_measured: Optional[bool] = None
    t3_measured: Optional[bool] = None
    tt4_measured: Optional[bool] = None
    t4u_measured: Optional[bool] = None
    fti_measured: Optional[bool] = None
    tbg_measured: Optional[bool] = None

    tsh: Optional[Decimal] = None
    t3: Optional[Decimal] = None
    tt4: Optional[Decimal] = None
    t4u: Optional[Decimal] = None
    fti: Optional[Decimal] = None
    tbg: Optional[Decimal] = None

    referral_source: Optional[str] = Field(
        default=None,
        max_length=50
    )

    target_code: Optional[str] = Field(
        default=None,
        max_length=20
    )

    clinical_notes: Optional[str] = None


# ============================================================
# Clinical Response
# ============================================================

class ClinicalResponse(ClinicalBase):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    patient_id: int

    source_patient_id: Optional[int] = None

    target_code: Optional[str] = None

    entered_by: Optional[int] = None

    created_at: datetime

    updated_at: datetime


# ============================================================
# Clinical List Response
# ============================================================

class ClinicalListResponse(BaseModel):

    items: list[ClinicalResponse]

    total: int


# ============================================================
# Clinical AI Prediction
# ============================================================

class ClinicalPrediction(BaseModel):

    diagnosis_code: str

    probability: float = Field(
        ge=0.0,
        le=1.0
    )


# ============================================================
# Clinical AI Response
# ============================================================

class ClinicalAIResponse(BaseModel):

    top_prediction: ClinicalPrediction

    top_predictions: list[ClinicalPrediction]

    model_name: str = "Clinical Random Forest"