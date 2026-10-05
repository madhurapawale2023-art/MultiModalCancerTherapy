# AI analysis API routes.

from typing import Any, Dict, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from backend.app.core.dependencies import get_current_user
from backend.app.services.ai_service import (
    get_ai_service_status,
    run_ai_pipeline,
)
from backend.app.utils.file_handler import save_file


router = APIRouter(
    prefix="/api/ai",
    tags=["AI Analysis"],
)


# ============================================================
# AI SERVICE STATUS
# ============================================================

@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
)
def ai_status(
    current_user=Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Return AI model and artifact availability.
    """

    result = get_ai_service_status()

    return {
        **result,
        "user_id": getattr(current_user, "id", None),
    }


# ============================================================
# RUN AI ANALYSIS
# ============================================================

@router.post(
    "/analyze",
    status_code=status.HTTP_200_OK,
)
def analyze(
    payload: Dict[str, Any],
    current_user=Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Run the available AI pipeline.

    Supported payload examples:

    {
        "clinical_data": {
            "age": 45,
            "sex": "F"
        }
    }

    or

    {
        "ultrasound_image_path": "path/to/image.jpg"
    }

    or both.
    """

    clinical_data: Optional[Dict[str, Any]] = payload.get(
        "clinical_data"
    )

    ultrasound_image_path: Optional[str] = payload.get(
        "ultrasound_image_path"
    )

    if clinical_data is not None and not isinstance(
        clinical_data,
        dict,
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="clinical_data must be an object",
        )

    if ultrasound_image_path is not None and not isinstance(
        ultrasound_image_path,
        str,
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="ultrasound_image_path must be a string",
        )

    if not clinical_data and not ultrasound_image_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Provide clinical_data or ultrasound_image_path "
                "to run AI analysis."
            ),
        )

    try:
        result = run_ai_pipeline(
            clinical_data=clinical_data,
            ultrasound_image_path=ultrasound_image_path,
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {exc}",
        ) from exc

    return {
        "status": result.get("status", "success"),
        "clinical": result.get("clinical"),
        "ultrasound": result.get("ultrasound"),
        "multimodal": result.get("multimodal"),
        "fusion_method": result.get(
            "fusion_method",
            "Late Evidence Integration",
        ),
        "clinical_decision_support_only": True,
        "senior_doctor_review_required": True,
        "created_by": getattr(current_user, "id", None),
    }


# ============================================================
# CLINICAL ANALYSIS
# ============================================================

@router.post(
    "/clinical",
    status_code=status.HTTP_200_OK,
)
def clinical_analysis(
    payload: Dict[str, Any],
    current_user=Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Run clinical AI analysis only.
    """

    clinical_data = payload.get("clinical_data", payload)

    if not isinstance(clinical_data, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Clinical input must be an object",
        )

    try:
        result = run_ai_pipeline(
            clinical_data=clinical_data,
            ultrasound_image_path=None,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clinical AI analysis failed: {exc}",
        ) from exc

    return {
        "status": "success",
        "clinical": result.get("clinical"),
        "clinical_decision_support_only": True,
        "senior_doctor_review_required": True,
        "created_by": getattr(current_user, "id", None),
    }


# ============================================================
# ULTRASOUND ANALYSIS
# ============================================================

@router.post(
    "/ultrasound",
    status_code=status.HTTP_200_OK,
)
def ultrasound_analysis(
    payload: Dict[str, Any],
    current_user=Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Run ultrasound AI analysis.
    """

    image_path = payload.get(
        "ultrasound_image_path",
        payload.get("image_path"),
    )

    if not image_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ultrasound_image_path is required",
        )

    if not isinstance(image_path, str):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="ultrasound_image_path must be a string",
        )

    try:
        result = run_ai_pipeline(
            clinical_data=None,
            ultrasound_image_path=image_path,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ultrasound AI analysis failed: {exc}",
        ) from exc

    return {
        "status": "success",
        "ultrasound": result.get("ultrasound"),
        "clinical_decision_support_only": True,
        "senior_doctor_review_required": True,
        "created_by": getattr(current_user, "id", None),
    }


# ============================================================
# MULTIMODAL ANALYSIS
# ============================================================

@router.post(
    "/multimodal",
    status_code=status.HTTP_200_OK,
)
def multimodal_analysis(
    payload: Dict[str, Any],
    current_user=Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Run multimodal late evidence integration.

    Clinical and ultrasound inputs are not artificially paired.
    """

    clinical_data = payload.get("clinical_data")

    ultrasound_image_path = payload.get(
        "ultrasound_image_path"
    )

    if clinical_data is not None and not isinstance(
        clinical_data,
        dict,
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="clinical_data must be an object",
        )

    if ultrasound_image_path is not None and not isinstance(
        ultrasound_image_path,
        str,
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="ultrasound_image_path must be a string",
        )

    if not clinical_data and not ultrasound_image_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Provide clinical_data or "
                "ultrasound_image_path."
            ),
        )

    try:
        result = run_ai_pipeline(
            clinical_data=clinical_data,
            ultrasound_image_path=ultrasound_image_path,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multimodal analysis failed: {exc}",
        ) from exc

    return {
        "status": "success",
        "clinical": result.get("clinical"),
        "ultrasound": result.get("ultrasound"),
        "multimodal": result.get("multimodal"),
        "fusion_method": "Late Evidence Integration",
        "direct_training_pair_available": False,
        "artificial_patient_pairing": False,
        "clinical_decision_support_only": True,
        "senior_doctor_review_required": True,
        "created_by": getattr(current_user, "id", None),
    }


# ============================================================
# ULTRASOUND IMAGE UPLOAD
# ============================================================

@router.post(
    "/ultrasound/upload",
    status_code=status.HTTP_201_CREATED,
)
async def upload_ultrasound_image(
    file: UploadFile = File(...),
    patient_id: Optional[str] = Form(default=None),
    current_user=Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Store an uploaded ultrasound image and return its stored path
    so it can be passed to the ultrasound AI endpoint.

    Uses the existing upload directory + file handler utilities.
    """

    if file is None or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An ultrasound image file is required.",
        )

    content = await file.read()

    try:
        stored_path = save_file(
            content=content,
            original_filename=file.filename,
            destination="ultrasound",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return {
        "status": "success",
        "message": "Ultrasound image uploaded successfully.",
        "file_name": stored_path.name,
        "image_path": str(stored_path),
        "patient_id": patient_id,
        "clinical_decision_support_only": True,
        "senior_doctor_review_required": True,
        "created_by": getattr(current_user, "id", None),
    }