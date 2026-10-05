# Report request and response schemas.

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict


# ============================================================
# LAB REPORT SCHEMAS
# ============================================================

class LabReportCreate(BaseModel):
    patient_id: int
    test_name: str
    test_value: Optional[str] = None
    reference_range: Optional[str] = None
    unit: Optional[str] = None
    test_date: Optional[datetime] = None
    entered_by: Optional[int] = None


class LabReportResponse(BaseModel):
    id: Optional[int] = None
    patient_id: int
    test_name: str
    test_value: Optional[str] = None
    reference_range: Optional[str] = None
    unit: Optional[str] = None
    test_date: Optional[datetime] = None
    verification_status: Optional[str] = None
    entered_by: Optional[int] = None
    created_at: Optional[datetime] = None


# ============================================================
# PATHOLOGY REPORT SCHEMAS
# ============================================================

class PathologyReportCreate(BaseModel):
    patient_id: int
    sample_type: Optional[str] = None
    test_name: Optional[str] = None
    findings: Optional[str] = None
    diagnosis: Optional[str] = None
    entered_by: Optional[int] = None


class PathologyReportResponse(BaseModel):
    id: Optional[int] = None
    patient_id: int
    sample_type: Optional[str] = None
    test_name: Optional[str] = None
    findings: Optional[str] = None
    diagnosis: Optional[str] = None
    verification_status: Optional[str] = None
    entered_by: Optional[int] = None
    created_at: Optional[datetime] = None


# ============================================================
# IMAGING REPORT SCHEMAS
# ============================================================

class ImagingReportCreate(BaseModel):
    patient_id: int
    imaging_type: str
    findings: Optional[str] = None
    impression: Optional[str] = None
    created_by: Optional[int] = None


class ImagingReportResponse(BaseModel):
    id: Optional[int] = None
    patient_id: int
    imaging_type: str
    findings: Optional[str] = None
    impression: Optional[str] = None
    verification_status: Optional[str] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None


# ============================================================
# IMAGING FILE SCHEMAS
# ============================================================

class ImagingFileCreate(BaseModel):
    patient_id: int
    file_name: str
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    description: Optional[str] = None
    uploaded_by: Optional[int] = None


class ImagingFileResponse(BaseModel):
    id: Optional[int] = None
    patient_id: int
    file_name: str
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    description: Optional[str] = None
    uploaded_by: Optional[int] = None
    created_at: Optional[datetime] = None


# ============================================================
# MOLECULAR / IHC SCHEMAS
# DNA TESTING IS NOT INCLUDED
# ============================================================

class MolecularRecordCreate(BaseModel):
    patient_id: int
    marker_name: Optional[str] = None
    marker_value: Optional[str] = None
    test_method: Optional[str] = None
    interpretation: Optional[str] = None
    recorded_by: Optional[int] = None


class MolecularRecordResponse(BaseModel):
    id: Optional[int] = None
    patient_id: int
    marker_name: Optional[str] = None
    marker_value: Optional[str] = None
    test_method: Optional[str] = None
    interpretation: Optional[str] = None
    recorded_by: Optional[int] = None
    created_at: Optional[datetime] = None


# ============================================================
# CLINICAL RECORD REPORT
# ============================================================

class ClinicalRecordReport(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int

    source_patient_id: Optional[Any] = None
    age: Optional[Any] = None
    sex: Optional[Any] = None

    on_thyroxine: Optional[Any] = None
    query_on_thyroxine: Optional[Any] = None
    on_antithyroid_meds: Optional[Any] = None
    sick: Optional[Any] = None
    pregnant: Optional[Any] = None
    thyroid_surgery: Optional[Any] = None
    i131_treatment: Optional[Any] = None

    query_hypothyroid: Optional[Any] = None
    query_hyperthyroid: Optional[Any] = None
    lithium: Optional[Any] = None
    goitre: Optional[Any] = None
    tumor: Optional[Any] = None
    hypopituitary: Optional[Any] = None
    psych: Optional[Any] = None

    tsh_measured: Optional[Any] = None
    t3_measured: Optional[Any] = None
    tt4_measured: Optional[Any] = None
    t4u_measured: Optional[Any] = None
    fti_measured: Optional[Any] = None
    tbg_measured: Optional[Any] = None

    tsh: Optional[Any] = None
    t3: Optional[Any] = None
    tt4: Optional[Any] = None
    t4u: Optional[Any] = None
    fti: Optional[Any] = None
    tbg: Optional[Any] = None

    referral_source: Optional[Any] = None
    target_code: Optional[Any] = None
    clinical_notes: Optional[Any] = None

    entered_by: Optional[int] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ============================================================
# ULTRASOUND IMAGE REPORT
# ============================================================

class UltrasoundImageReport(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ultrasound_case_id: int

    image_number: Optional[Any] = None
    image_filename: Optional[Any] = None
    image_path: Optional[Any] = None

    mask_filename: Optional[Any] = None
    mask_path: Optional[Any] = None

    width: Optional[Any] = None
    height: Optional[Any] = None

    has_annotation: Optional[Any] = None
    annotation_points: Optional[Any] = None
    region_type: Optional[Any] = None
    number_of_annotation_points: Optional[Any] = None

    segmentation_pixels: Optional[Any] = None
    segmentation_area_ratio: Optional[Any] = None

    created_at: Optional[datetime] = None


# ============================================================
# ULTRASOUND CASE REPORT
# ============================================================

class UltrasoundCaseReport(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int

    case_number: Optional[Any] = None
    age: Optional[Any] = None
    sex: Optional[Any] = None

    composition: Optional[Any] = None
    echogenicity: Optional[Any] = None
    margins: Optional[Any] = None
    calcifications: Optional[Any] = None
    tirads: Optional[Any] = None

    reportbacaf: Optional[Any] = None
    reporteco: Optional[Any] = None
    case_notes: Optional[Any] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    images: List[UltrasoundImageReport] = []


# ============================================================
# AI ANALYSIS REPORT
# ============================================================

class AIAnalysisReport(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int

    clinical_record_id: Optional[int] = None
    ultrasound_image_id: Optional[int] = None

    clinical_top_prediction: Optional[Any] = None
    clinical_top_probability: Optional[Any] = None
    clinical_predictions: Optional[Any] = None

    ultrasound_segmentation_area: Optional[Any] = None
    ultrasound_evidence: Optional[Any] = None

    fusion_method: Optional[Any] = None
    multimodal_summary: Optional[Any] = None

    model_version: Optional[Any] = None
    status: Optional[Any] = None

    requires_doctor_review: Optional[Any] = None

    created_by: Optional[int] = None
    created_at: Optional[datetime] = None


# ============================================================
# AI RECOMMENDATION REPORT
# ============================================================

class AIRecommendationReport(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int

    ai_analysis_id: Optional[int] = None

    recommendation_text: Optional[Any] = None
    evidence_summary: Optional[Any] = None
    confidence: Optional[Any] = None

    doctor_status: Optional[Any] = None
    doctor_notes: Optional[Any] = None

    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None

    created_at: Optional[datetime] = None


# ============================================================
# REPORT SUMMARY
# ============================================================

class ReportSummaryResponse(BaseModel):
    patient_id: int

    clinical_records: int = 0
    ultrasound_cases: int = 0
    ultrasound_images: int = 0
    ai_analyses: int = 0
    ai_recommendations: int = 0

    total_records: int = 0

    latest_ai_analysis_id: Optional[int] = None
    latest_recommendation_id: Optional[int] = None


# ============================================================
# COMPLETE PATIENT REPORT
# ============================================================

class PatientReportResponse(BaseModel):
    patient_id: int

    clinical_records: List[ClinicalRecordReport] = []
    ultrasound_cases: List[UltrasoundCaseReport] = []
    ultrasound_images: List[UltrasoundImageReport] = []

    ai_analyses: List[AIAnalysisReport] = []
    ai_recommendations: List[AIRecommendationReport] = []

    summary: ReportSummaryResponse

    clinical_decision_support_only: bool = True
    requires_senior_doctor_review: bool = True


# ============================================================
# REPORT STATUS
# ============================================================

class ReportStatusResponse(BaseModel):
    status: str
    message: str
    patient_id: Optional[int] = None