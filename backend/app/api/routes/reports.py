# Patient report aggregation API routes.

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_user
from backend.app.db.database import get_db
from backend.app.db.models import User
from backend.app.schemas.report import (
    PatientReportResponse,
    ReportSummaryResponse,
    ReportStatusResponse,
)
from backend.app.services.report_service import (
    get_ai_analyses,
    get_ai_recommendations,
    get_clinical_records,
    get_patient_report,
    get_report_summary,
    get_ultrasound_cases,
    get_ultrasound_images,
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


# ============================================================
# REPORT STATUS
# ============================================================

@router.get(
    "/status",
    response_model=ReportStatusResponse,
    status_code=status.HTTP_200_OK,
)
def report_status(
    current_user: User = Depends(get_current_user),
):
    """
    Return report service availability.
    """

    return {
        "status": "ready",
        "message": "Report service is available",
        "patient_id": None,
    }


# ============================================================
# PATIENT REPORT SUMMARY
# ============================================================

@router.get(
    "/patient/{patient_id}/summary",
    response_model=ReportSummaryResponse,
    status_code=status.HTTP_200_OK,
)
def patient_report_summary(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return report counts and latest AI record IDs.
    """

    summary = get_report_summary(
        db=db,
        patient_id=patient_id,
    )

    return summary


# ============================================================
# COMPLETE PATIENT REPORT
# ============================================================

@router.get(
    "/patient/{patient_id}",
    response_model=PatientReportResponse,
    status_code=status.HTTP_200_OK,
)
def patient_report(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return the complete aggregated report for a patient.
    """

    report = get_patient_report(
        db=db,
        patient_id=patient_id,
    )

    return report


# ============================================================
# CLINICAL RECORDS
# ============================================================

@router.get(
    "/patient/{patient_id}/clinical",
    status_code=status.HTTP_200_OK,
)
def patient_clinical_records(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Return all clinical records for a patient.
    """

    records = get_clinical_records(
        db=db,
        patient_id=patient_id,
    )

    return {
        "status": "success",
        "patient_id": patient_id,
        "items": records,
        "total": len(records),
    }


# ============================================================
# ULTRASOUND CASES
# ============================================================

@router.get(
    "/patient/{patient_id}/ultrasound",
    status_code=status.HTTP_200_OK,
)
def patient_ultrasound_cases(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Return all ultrasound cases for a patient.
    """

    cases = get_ultrasound_cases(
        db=db,
        patient_id=patient_id,
    )

    return {
        "status": "success",
        "patient_id": patient_id,
        "items": cases,
        "total": len(cases),
    }


# ============================================================
# ULTRASOUND IMAGES
# ============================================================

@router.get(
    "/ultrasound-case/{ultrasound_case_id}/images",
    status_code=status.HTTP_200_OK,
)
def ultrasound_case_images(
    ultrasound_case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Return all images for an ultrasound case.
    """

    images = get_ultrasound_images(
        db=db,
        ultrasound_case_id=ultrasound_case_id,
    )

    return {
        "status": "success",
        "ultrasound_case_id": ultrasound_case_id,
        "items": images,
        "total": len(images),
    }


# ============================================================
# AI ANALYSES
# ============================================================

@router.get(
    "/patient/{patient_id}/ai-analysis",
    status_code=status.HTTP_200_OK,
)
def patient_ai_analyses(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Return all AI analyses for a patient.
    """

    analyses = get_ai_analyses(
        db=db,
        patient_id=patient_id,
    )

    return {
        "status": "success",
        "patient_id": patient_id,
        "items": analyses,
        "total": len(analyses),
        "clinical_decision_support_only": True,
        "senior_doctor_review_required": True,
    }


# ============================================================
# AI RECOMMENDATIONS
# ============================================================

@router.get(
    "/patient/{patient_id}/recommendations",
    status_code=status.HTTP_200_OK,
)
def patient_ai_recommendations(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Return all AI recommendations for a patient.
    """

    recommendations = get_ai_recommendations(
        db=db,
        patient_id=patient_id,
    )

    return {
        "status": "success",
        "patient_id": patient_id,
        "items": recommendations,
        "total": len(recommendations),
        "clinical_decision_support_only": True,
        "senior_doctor_review_required": True,
    }


# ============================================================
# REPORT SEARCH / SUMMARY FILTER
# ============================================================

@router.get(
    "/patient/{patient_id}/overview",
    status_code=status.HTTP_200_OK,
)
def patient_report_overview(
    patient_id: int,
    include_clinical: bool = Query(default=True),
    include_ultrasound: bool = Query(default=True),
    include_ai: bool = Query(default=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Return a flexible report overview.
    """

    result: Dict[str, Any] = {
        "status": "success",
        "patient_id": patient_id,
        "summary": get_report_summary(
            db=db,
            patient_id=patient_id,
        ),
    }

    if include_clinical:
        result["clinical_records"] = get_clinical_records(
            db=db,
            patient_id=patient_id,
        )

    if include_ultrasound:
        result["ultrasound_cases"] = get_ultrasound_cases(
            db=db,
            patient_id=patient_id,
        )

    if include_ai:
        result["ai_analyses"] = get_ai_analyses(
            db=db,
            patient_id=patient_id,
        )
        result["ai_recommendations"] = get_ai_recommendations(
            db=db,
            patient_id=patient_id,
        )

    result["clinical_decision_support_only"] = True
    result["senior_doctor_review_required"] = True

    return result