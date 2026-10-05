# ============================================================
# MultiModalCancerTherapy
# backend/app/schemas/ai.py
# AI / Multimodal Decision-Support Schemas
# ============================================================

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# Clinical Prediction
# ============================================================

class ClinicalPrediction(BaseModel):

    diagnosis_code: str = Field(
        ...,
        min_length=1,
        max_length=20
    )

    probability: float = Field(
        ...,
        ge=0.0,
        le=1.0
    )


# ============================================================
# Clinical Evidence
# ============================================================

class ClinicalEvidence(BaseModel):

    top_prediction: Optional[ClinicalPrediction] = None

    top_predictions: list[ClinicalPrediction] = Field(
        default_factory=list
    )

    model: str = "Clinical Random Forest"


# ============================================================
# Ultrasound Evidence
# ============================================================

class UltrasoundEvidence(BaseModel):

    model: str = "UNetSmall"

    original_image_size: list[int] = Field(
        default_factory=list
    )

    processed_image_size: list[int] = Field(
        default_factory=lambda: [224, 224]
    )

    segmentation_pixels: int = Field(
        default=0,
        ge=0
    )

    segmentation_area_ratio: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0
    )


# ============================================================
# Multimodal Status
# ============================================================

class MultimodalStatus(BaseModel):

    clinical_data_available: bool = False

    ultrasound_data_available: bool = False

    direct_training_pair_available: bool = False

    fusion_method: str = (
        "Late Evidence Integration"
    )

    requires_senior_doctor_review: bool = True


# ============================================================
# AI Analysis Request
# ============================================================

class AIAnalysisRequest(BaseModel):

    patient_id: int

    clinical_record_id: Optional[int] = None

    ultrasound_image_id: Optional[int] = None

    clinical_input: Optional[dict[str, Any]] = None


# ============================================================
# AI Analysis Create
# ============================================================

class AIAnalysisCreate(BaseModel):

    patient_id: int

    clinical_record_id: Optional[int] = None

    ultrasound_image_id: Optional[int] = None

    clinical_input: Optional[dict[str, Any]] = None


# ============================================================
# AI Analysis Update
# ============================================================

class AIAnalysisUpdate(BaseModel):

    status: Optional[str] = Field(
        default=None,
        max_length=30
    )

    multimodal_summary: Optional[dict[str, Any]] = None

    requires_doctor_review: Optional[bool] = None


# ============================================================
# AI Analysis Response
# ============================================================

class AIAnalysisResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: Optional[int] = None

    patient_id: int

    clinical_record_id: Optional[int] = None

    ultrasound_image_id: Optional[int] = None

    clinical_evidence: Optional[ClinicalEvidence] = None

    ultrasound_evidence: Optional[UltrasoundEvidence] = None

    multimodal_status: MultimodalStatus = Field(
        default_factory=MultimodalStatus
    )

    model_version: Optional[str] = None

    status: str = "success"

    requires_doctor_review: bool = True

    created_at: Optional[datetime] = None


# ============================================================
# AI Recommendation Request
# ============================================================

class AIRecommendationRequest(BaseModel):

    patient_id: int

    ai_analysis_id: Optional[int] = None

    recommendation_text: str = Field(
        ...,
        min_length=1
    )

    evidence_summary: Optional[str] = None

    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0
    )


# ============================================================
# AI Recommendation Create
# ============================================================

class AIRecommendationCreate(
    AIRecommendationRequest
):
    """
    Backward-compatible recommendation create schema.
    """

    pass


# ============================================================
# AI Recommendation Review
# ============================================================

class AIRecommendationReview(BaseModel):

    doctor_status: str = Field(
        ...,
        min_length=1,
        max_length=30
    )

    doctor_notes: Optional[str] = None


# ============================================================
# AI Recommendation Update
# ============================================================

class AIRecommendationUpdate(BaseModel):

    doctor_status: Optional[str] = Field(
        default=None,
        max_length=30
    )

    doctor_notes: Optional[str] = None


# ============================================================
# AI Recommendation Response
# ============================================================

class AIRecommendationResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    patient_id: int

    ai_analysis_id: Optional[int] = None

    recommendation_text: Optional[str] = None

    evidence_summary: Optional[str] = None

    confidence: Optional[Decimal] = None

    doctor_status: str

    doctor_notes: Optional[str] = None

    reviewed_by: Optional[int] = None

    reviewed_at: Optional[datetime] = None

    created_at: datetime


# ============================================================
# AI Status Response
# ============================================================

class AIStatusResponse(BaseModel):

    status: str = "ready"

    clinical_model_loaded: bool = False

    ultrasound_model_loaded: bool = False

    multimodal_enabled: bool = True

    tirads_classifier_enabled: bool = False

    message: str = (
        "AI clinical decision-support services "
        "are available."
    )


# ============================================================
# AI Health Response
# ============================================================

class AIHealthResponse(BaseModel):

    status: str = "healthy"

    clinical_model: bool = False

    ultrasound_model: bool = False

    multimodal_service: bool = False


# ============================================================
# Final Multimodal Decision-Support Response
# ============================================================

class MultimodalDecisionSupportResponse(BaseModel):

    status: str = "success"

    patient_id: int

    clinical_evidence: Optional[ClinicalEvidence] = None

    ultrasound_evidence: Optional[UltrasoundEvidence] = None

    multimodal_status: MultimodalStatus = Field(
        default_factory=MultimodalStatus
    )

    recommendation: Optional[str] = None

    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0
    )

    disclaimer: str = (
        "AI output is clinical decision support only "
        "and does not replace professional medical judgment."
    )


# ============================================================
# AI Result Response
# ============================================================

class AIResultResponse(
    MultimodalDecisionSupportResponse
):
    """
    Backward-compatible final AI result schema.
    """

    pass