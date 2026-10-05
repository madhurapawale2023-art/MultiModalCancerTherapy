# Report aggregation and AI report business logic.

from typing import List, Optional

from sqlalchemy.orm import Session

from backend.app.db.models import (
    AIAnalysis,
    AIRecommendation,
    ClinicalRecord,
    UltrasoundCase,
    UltrasoundImage,
)


# ============================================================
# CLINICAL RECORD SERVICES
# ============================================================

def get_clinical_records(
    db: Session,
    patient_id: int,
) -> List[ClinicalRecord]:
    """
    Get all clinical records for a patient.
    """

    return (
        db.query(ClinicalRecord)
        .filter(ClinicalRecord.patient_id == patient_id)
        .order_by(ClinicalRecord.id.desc())
        .all()
    )


def get_latest_clinical_record(
    db: Session,
    patient_id: int,
) -> Optional[ClinicalRecord]:
    """
    Get the latest clinical record for a patient.
    """

    return (
        db.query(ClinicalRecord)
        .filter(ClinicalRecord.patient_id == patient_id)
        .order_by(ClinicalRecord.id.desc())
        .first()
    )


# ============================================================
# ULTRASOUND CASE SERVICES
# ============================================================

def get_ultrasound_cases(
    db: Session,
    patient_id: int,
) -> List[UltrasoundCase]:
    """
    Get all ultrasound cases for a patient.
    """

    return (
        db.query(UltrasoundCase)
        .filter(UltrasoundCase.patient_id == patient_id)
        .order_by(UltrasoundCase.id.desc())
        .all()
    )


def get_latest_ultrasound_case(
    db: Session,
    patient_id: int,
) -> Optional[UltrasoundCase]:
    """
    Get the latest ultrasound case for a patient.
    """

    return (
        db.query(UltrasoundCase)
        .filter(UltrasoundCase.patient_id == patient_id)
        .order_by(UltrasoundCase.id.desc())
        .first()
    )


# ============================================================
# ULTRASOUND IMAGE SERVICES
# ============================================================

def get_ultrasound_images(
    db: Session,
    ultrasound_case_id: int,
) -> List[UltrasoundImage]:
    """
    Get all images belonging to an ultrasound case.
    """

    return (
        db.query(UltrasoundImage)
        .filter(
            UltrasoundImage.ultrasound_case_id == ultrasound_case_id
        )
        .order_by(UltrasoundImage.image_number.asc())
        .all()
    )


# ============================================================
# AI ANALYSIS SERVICES
# ============================================================

def get_ai_analyses(
    db: Session,
    patient_id: int,
) -> List[AIAnalysis]:
    """
    Get all AI analyses for a patient.
    """

    return (
        db.query(AIAnalysis)
        .filter(AIAnalysis.patient_id == patient_id)
        .order_by(AIAnalysis.id.desc())
        .all()
    )


def get_latest_ai_analysis(
    db: Session,
    patient_id: int,
) -> Optional[AIAnalysis]:
    """
    Get the latest AI analysis for a patient.
    """

    return (
        db.query(AIAnalysis)
        .filter(AIAnalysis.patient_id == patient_id)
        .order_by(AIAnalysis.id.desc())
        .first()
    )


# ============================================================
# AI RECOMMENDATION SERVICES
# ============================================================

def get_ai_recommendations(
    db: Session,
    patient_id: int,
) -> List[AIRecommendation]:
    """
    Get all AI recommendations for a patient.
    """

    return (
        db.query(AIRecommendation)
        .filter(AIRecommendation.patient_id == patient_id)
        .order_by(AIRecommendation.id.desc())
        .all()
    )


def get_latest_ai_recommendation(
    db: Session,
    patient_id: int,
) -> Optional[AIRecommendation]:
    """
    Get the latest AI recommendation for a patient.
    """

    return (
        db.query(AIRecommendation)
        .filter(AIRecommendation.patient_id == patient_id)
        .order_by(AIRecommendation.id.desc())
        .first()
    )


# ============================================================
# REPORT SUMMARY
# ============================================================

def get_report_summary(
    db: Session,
    patient_id: int,
) -> dict:
    """
    Build a complete patient report summary using
    the actual project database models.
    """

    clinical_count = (
        db.query(ClinicalRecord)
        .filter(ClinicalRecord.patient_id == patient_id)
        .count()
    )

    ultrasound_case_count = (
        db.query(UltrasoundCase)
        .filter(UltrasoundCase.patient_id == patient_id)
        .count()
    )

    ultrasound_image_count = (
        db.query(UltrasoundImage)
        .join(
            UltrasoundCase,
            UltrasoundImage.ultrasound_case_id == UltrasoundCase.id,
        )
        .filter(UltrasoundCase.patient_id == patient_id)
        .count()
    )

    ai_analysis_count = (
        db.query(AIAnalysis)
        .filter(AIAnalysis.patient_id == patient_id)
        .count()
    )

    ai_recommendation_count = (
        db.query(AIRecommendation)
        .filter(AIRecommendation.patient_id == patient_id)
        .count()
    )

    latest_analysis = get_latest_ai_analysis(
        db,
        patient_id,
    )

    latest_recommendation = get_latest_ai_recommendation(
        db,
        patient_id,
    )

    return {
        "patient_id": patient_id,

        "clinical_records": clinical_count,

        "ultrasound_cases": ultrasound_case_count,

        "ultrasound_images": ultrasound_image_count,

        "ai_analyses": ai_analysis_count,

        "ai_recommendations": ai_recommendation_count,

        "total_records": (
            clinical_count
            + ultrasound_case_count
            + ultrasound_image_count
            + ai_analysis_count
            + ai_recommendation_count
        ),

        "latest_ai_analysis_id": (
            latest_analysis.id
            if latest_analysis is not None
            else None
        ),

        "latest_recommendation_id": (
            latest_recommendation.id
            if latest_recommendation is not None
            else None
        ),
    }


# ============================================================
# COMPLETE REPORT DATA
# ============================================================

def get_patient_report(
    db: Session,
    patient_id: int,
) -> dict:
    """
    Return the complete report data for a patient.

    This is aggregation only. It does not create an
    independent clinical decision.
    """

    clinical_records = get_clinical_records(
        db,
        patient_id,
    )

    ultrasound_cases = get_ultrasound_cases(
        db,
        patient_id,
    )

    ai_analyses = get_ai_analyses(
        db,
        patient_id,
    )

    ai_recommendations = get_ai_recommendations(
        db,
        patient_id,
    )

    ultrasound_images = []

    for case in ultrasound_cases:
        images = get_ultrasound_images(
            db,
            case.id,
        )

        ultrasound_images.extend(images)

    return {
        "patient_id": patient_id,

        "clinical_records": clinical_records,

        "ultrasound_cases": ultrasound_cases,

        "ultrasound_images": ultrasound_images,

        "ai_analyses": ai_analyses,

        "ai_recommendations": ai_recommendations,

        "summary": get_report_summary(
            db,
            patient_id,
        ),

        "clinical_decision_support_only": True,

        "requires_senior_doctor_review": True,
    }