# ============================================================
# MultiModalCancerTherapy
# backend/app/schemas/ultrasound.py
# Ultrasound Data Schemas
# Based on XML + Ultrasound Image Processing
# ============================================================

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# Ultrasound Case Base
# ============================================================

class UltrasoundCaseBase(BaseModel):

    case_number: int

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
    # XML ultrasound descriptors
    # --------------------------------------------------------

    composition: Optional[str] = Field(
        default=None,
        max_length=100
    )

    echogenicity: Optional[str] = Field(
        default=None,
        max_length=100
    )

    margins: Optional[str] = Field(
        default=None,
        max_length=100
    )

    calcifications: Optional[str] = Field(
        default=None,
        max_length=100
    )

    tirads: Optional[str] = Field(
        default=None,
        max_length=20
    )

    reportbacaf: Optional[str] = None

    reporteco: Optional[str] = None

    case_notes: Optional[str] = None


# ============================================================
# Ultrasound Case Create
# ============================================================

class UltrasoundCaseCreate(UltrasoundCaseBase):

    patient_id: Optional[int] = None


# ============================================================
# Ultrasound Case Update
# ============================================================

class UltrasoundCaseUpdate(BaseModel):

    patient_id: Optional[int] = None

    age: Optional[int] = Field(
        default=None,
        ge=0,
        le=150
    )

    sex: Optional[str] = Field(
        default=None,
        max_length=10
    )

    composition: Optional[str] = Field(
        default=None,
        max_length=100
    )

    echogenicity: Optional[str] = Field(
        default=None,
        max_length=100
    )

    margins: Optional[str] = Field(
        default=None,
        max_length=100
    )

    calcifications: Optional[str] = Field(
        default=None,
        max_length=100
    )

    tirads: Optional[str] = Field(
        default=None,
        max_length=20
    )

    reportbacaf: Optional[str] = None

    reporteco: Optional[str] = None

    case_notes: Optional[str] = None


# ============================================================
# Ultrasound Image Base
# ============================================================

class UltrasoundImageBase(BaseModel):

    image_number: int

    image_filename: str = Field(
        ...,
        max_length=255
    )

    image_path: str

    mask_filename: Optional[str] = Field(
        default=None,
        max_length=255
    )

    mask_path: Optional[str] = None

    width: Optional[int] = Field(
        default=None,
        ge=1
    )

    height: Optional[int] = Field(
        default=None,
        ge=1
    )

    has_annotation: bool = False

    annotation_points: Optional[Any] = None

    region_type: Optional[str] = Field(
        default=None,
        max_length=50
    )

    number_of_annotation_points: Optional[int] = Field(
        default=None,
        ge=0
    )


# ============================================================
# Ultrasound Image Create
# ============================================================

class UltrasoundImageCreate(UltrasoundImageBase):

    ultrasound_case_id: int


# ============================================================
# Ultrasound Image Response
# ============================================================

class UltrasoundImageResponse(
    UltrasoundImageBase
):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    ultrasound_case_id: int

    segmentation_pixels: Optional[int] = Field(
        default=None,
        ge=0
    )

    segmentation_area_ratio: Optional[Decimal] = Field(
        default=None,
        ge=0.0,
        le=1.0
    )

    created_at: datetime


# ============================================================
# Ultrasound Case Response
# ============================================================

class UltrasoundCaseResponse(
    UltrasoundCaseBase
):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    patient_id: Optional[int] = None

    created_at: datetime

    updated_at: datetime

    images: list[UltrasoundImageResponse] = []


# ============================================================
# Ultrasound Case List Response
# ============================================================

class UltrasoundCaseListResponse(BaseModel):

    items: list[UltrasoundCaseResponse]

    total: int


# ============================================================
# Segmentation Evidence
# ============================================================

class SegmentationEvidence(BaseModel):

    model_name: str = "UNetSmall"

    original_image_size: list[int]

    processed_image_size: list[int]

    segmentation_pixels: int = Field(
        ge=0
    )

    segmentation_area_ratio: float = Field(
        ge=0.0,
        le=1.0
    )


# ============================================================
# Ultrasound AI Result
# ============================================================

class UltrasoundAIResponse(BaseModel):

    status: str = "success"

    evidence: SegmentationEvidence

    model_version: Optional[str] = None


# ============================================================
# Combined Ultrasound Analysis Response
# ============================================================

class UltrasoundAnalysisResponse(BaseModel):

    ultrasound_case_id: Optional[int] = None

    ultrasound_image_id: Optional[int] = None

    case_number: Optional[int] = None

    image_filename: Optional[str] = None

    tirads: Optional[str] = None

    segmentation: SegmentationEvidence

    requires_doctor_review: bool = True