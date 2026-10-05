# Dashboard API route.
#
# Aggregates real project data (database counts, model readiness,
# training CSV summary and model metadata) for the AngularJS dashboard.
#
# No DNA testing functionality is included.

from typing import Any, Callable, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_user
from backend.app.db.database import get_db
from backend.app.db.models import (
    AIAnalysis,
    AIRecommendation,
    ClinicalRecord,
    Patient,
    UltrasoundCase,
    UltrasoundImage,
)
from backend.app.services.ai_service import get_ai_service_status
from backend.app.services.dataset_service import (
    get_clinical_dataset_summary,
    get_clinical_model_metadata,
    get_multimodal_metadata,
    get_ultrasound_model_metadata,
)


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


# ============================================================
# SAFE DATABASE COUNTER
# ============================================================

def _safe_count(
    query_factory: Callable[[], int],
) -> int:
    """
    Run a count query and return 0 when the table/query is
    unavailable. Dashboard must still load when the database is
    partially empty.
    """

    try:
        return int(query_factory())

    except Exception:
        return 0


# ============================================================
# DASHBOARD DATA
# ============================================================

@router.get(
    "",
    status_code=status.HTTP_200_OK,
)
@router.get(
    "/",
    include_in_schema=False,
    status_code=status.HTTP_200_OK,
)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Return aggregated live dashboard data.

    All values are derived from the existing database, training CSV
    and trained-model metadata. No values are hardcoded.
    """

    # --------------------------------------------------------
    # Patient summary
    # --------------------------------------------------------

    total_patients = _safe_count(
        lambda: db.query(Patient).count()
    )

    status_rows = []

    try:
        status_rows = (
            db.query(
                Patient.status,
                func.count(Patient.id),
            )
            .group_by(Patient.status)
            .all()
        )
    except Exception:
        status_rows = []

    patients_by_status: Dict[str, int] = {
        str(row[0]): int(row[1])
        for row in status_rows
    }

    inactive_statuses = {
        "completed",
        "archived",
        "closed",
        "cancelled",
    }

    active_cases = sum(
        count
        for status_name, count in patients_by_status.items()
        if status_name.strip().lower() not in inactive_statuses
    )

    # --------------------------------------------------------
    # Record / review counts
    # --------------------------------------------------------

    clinical_records = _safe_count(
        lambda: db.query(ClinicalRecord).count()
    )

    ultrasound_cases = _safe_count(
        lambda: db.query(UltrasoundCase).count()
    )

    ultrasound_images = _safe_count(
        lambda: db.query(UltrasoundImage).count()
    )

    ai_analyses = _safe_count(
        lambda: db.query(AIAnalysis).count()
    )

    ai_recommendations = _safe_count(
        lambda: db.query(AIRecommendation).count()
    )

    pending_reviews = _safe_count(
        lambda: (
            db.query(AIRecommendation)
            .filter(
                AIRecommendation.doctor_status
                == "pending_review"
            )
            .count()
        )
    )

    # --------------------------------------------------------
    # Model readiness + metadata + dataset summary
    # --------------------------------------------------------

    return {
        "patients": {
            "total": total_patients,
            "active": active_cases,
            "by_status": patients_by_status,
        },

        "records": {
            "clinical_records": clinical_records,
            "ultrasound_cases": ultrasound_cases,
            "ultrasound_images": ultrasound_images,
            "ai_analyses": ai_analyses,
            "ai_recommendations": ai_recommendations,
            "pending_reviews": pending_reviews,
        },

        "ai": get_ai_service_status(),

        "clinical_model": get_clinical_model_metadata(),

        "ultrasound_model": get_ultrasound_model_metadata(),

        "multimodal": get_multimodal_metadata(),

        "dataset": get_clinical_dataset_summary(),

        "clinical_decision_support_only": True,

        "senior_doctor_final_authority": True,
    }
