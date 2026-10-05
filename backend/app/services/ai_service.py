from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import joblib
import pandas as pd

from backend.app.core.config import settings


# ============================================================
# Model Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CLINICAL_MODEL_DIR = PROJECT_ROOT / "models" / "clinical"
IMAGE_MODEL_DIR = PROJECT_ROOT / "models" / "image"

CLINICAL_MODEL_PATH = CLINICAL_MODEL_DIR / "clinical_model.joblib"
CLINICAL_PREPROCESSOR_PATH = (
    CLINICAL_MODEL_DIR / "clinical_preprocessor.joblib"
)
TARGET_ENCODER_PATH = CLINICAL_MODEL_DIR / "target_encoder.joblib"

ULTRASOUND_MODEL_PATH = IMAGE_MODEL_DIR / "ultrasound_unet_clean.pth"
ULTRASOUND_MODEL_INFO_PATH = (
    IMAGE_MODEL_DIR / "ultrasound_unet_clean_info.json"
)


# ============================================================
# Clinical feature columns
# ============================================================
#
# The fitted clinical preprocessor expects exactly these
# columns, in this order (notebook 03 training features).

CLINICAL_FEATURE_COLUMNS = [
    "age",
    "sex",
    "on_thyroxine",
    "query_on_thyroxine",
    "on_antithyroid_meds",
    "sick",
    "pregnant",
    "thyroid_surgery",
    "I131_treatment",
    "query_hypothyroid",
    "query_hyperthyroid",
    "lithium",
    "goitre",
    "tumor",
    "hypopituitary",
    "psych",
    "TSH_measured",
    "TSH",
    "T3_measured",
    "T3",
    "TT4_measured",
    "TT4",
    "T4U_measured",
    "T4U",
    "FTI_measured",
    "FTI",
    "TBG_measured",
    "referral_source",
]

# Binary t/f columns converted to 1/0 during notebook 03
# training before the preprocessor was fitted.

CLINICAL_BINARY_COLUMNS = [
    "on_thyroxine",
    "query_on_thyroxine",
    "on_antithyroid_meds",
    "sick",
    "pregnant",
    "thyroid_surgery",
    "I131_treatment",
    "query_hypothyroid",
    "query_hyperthyroid",
    "lithium",
    "goitre",
    "tumor",
    "hypopituitary",
    "psych",
    "TSH_measured",
    "T3_measured",
    "TT4_measured",
    "T4U_measured",
    "FTI_measured",
    "TBG_measured",
]

# Numeric laboratory columns imputed with the median during
# notebook 03 training.

CLINICAL_NUMERIC_COLUMNS = [
    "age",
    "TSH",
    "T3",
    "TT4",
    "T4U",
    "FTI",
]


# ============================================================
# Utility
# ============================================================

def _exists(path: Path) -> bool:
    return path.exists() and path.is_file()


# ============================================================
# AI Service Status
# ============================================================

def get_ai_service_status() -> Dict[str, Any]:
    """
    Check availability of all trained ML artifacts.
    """

    return {
        "status": "ready"
        if (
            _exists(CLINICAL_MODEL_PATH)
            and _exists(CLINICAL_PREPROCESSOR_PATH)
            and _exists(TARGET_ENCODER_PATH)
            and _exists(ULTRASOUND_MODEL_PATH)
        )
        else "not_ready",

        "clinical_model": {
            "path": str(CLINICAL_MODEL_PATH),
            "exists": _exists(CLINICAL_MODEL_PATH),
        },

        "clinical_preprocessor": {
            "path": str(CLINICAL_PREPROCESSOR_PATH),
            "exists": _exists(CLINICAL_PREPROCESSOR_PATH),
        },

        "target_encoder": {
            "path": str(TARGET_ENCODER_PATH),
            "exists": _exists(TARGET_ENCODER_PATH),
        },

        "ultrasound_model": {
            "path": str(ULTRASOUND_MODEL_PATH),
            "exists": _exists(ULTRASOUND_MODEL_PATH),
        },

        "ultrasound_model_info": {
            "path": str(ULTRASOUND_MODEL_INFO_PATH),
            "exists": _exists(ULTRASOUND_MODEL_INFO_PATH),
        },

        "clinical_decision_support_only": True,
        "senior_doctor_review_required": True,
    }


# ============================================================
# Clinical Model
# ============================================================

def _get_feature_value(
    clinical_data: Dict[str, Any],
    column: str,
) -> Any:
    """
    Return the value for a model feature column, accepting the
    exact column name or a case-insensitive match. When the exact
    column is present but empty, a case-insensitive non-empty
    value is preferred so alternate spellings still populate the
    feature.
    """

    exact = clinical_data.get(column)

    if exact is not None and exact != "":
        return exact

    column_lower = column.lower()

    for key, value in clinical_data.items():

        if str(key).lower() == column_lower:

            if value is not None and value != "":
                return value

    return exact


def _map_binary_flag(value: Any) -> int:
    """
    Convert a binary clinical flag to 1/0 using the same t/f
    mapping applied during notebook 03 training. Missing or
    unrecognized values default to 0 (flag absent).
    """

    if value is None:
        return 0

    if isinstance(value, bool):
        return 1 if value else 0

    if isinstance(value, (int, float)):
        return 1 if value else 0

    text = str(value).strip().lower()

    if text in ("t", "true", "1", "yes", "y"):
        return 1

    if text in ("f", "false", "0", "no", "n"):
        return 0

    return 0


def _map_sex(value: Any) -> Optional[int]:
    """
    Convert sex to 1/0 using the same M/F mapping applied
    during notebook 03 training. Unrecognized values return
    None so the categorical imputer can handle them.
    """

    if value is None:
        return None

    if isinstance(value, bool):
        return 1 if value else 0

    if isinstance(value, (int, float)):

        if int(value) in (0, 1):
            return int(value)

        return None

    text = str(value).strip().upper()

    if text in ("M", "MALE"):
        return 1

    if text in ("F", "FEMALE"):
        return 0

    return None


def _map_numeric(value: Any) -> Optional[float]:
    """
    Return a numeric laboratory value, converting empty or
    non-numeric input to None so the median imputer applied
    during notebook 03 training can handle it.
    """

    if value is None:
        return None

    if isinstance(value, bool):
        return float(value)

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()

    if text == "":
        return None

    try:
        return float(text)

    except ValueError:
        return None


def _prepare_clinical_features(
    clinical_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a feature dictionary containing exactly the columns
    the fitted clinical preprocessor expects, applying the same
    binary/sex/numeric preprocessing used during notebook 03
    training before the preprocessor transform.
    """

    features: Dict[str, Any] = {}

    for column in CLINICAL_FEATURE_COLUMNS:

        value = _get_feature_value(clinical_data, column)

        if column in CLINICAL_BINARY_COLUMNS:
            features[column] = _map_binary_flag(value)

        elif column == "sex":
            features[column] = _map_sex(value)

        elif column in CLINICAL_NUMERIC_COLUMNS:
            features[column] = _map_numeric(value)

        else:
            if isinstance(value, str) and value.strip() == "":
                features[column] = None
            else:
                features[column] = value

    return features


def analyze_clinical_data(
    clinical_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Run inference using the trained clinical Random Forest model.
    """

    if not _exists(CLINICAL_MODEL_PATH):
        raise FileNotFoundError(
            f"Clinical model not found: {CLINICAL_MODEL_PATH}"
        )

    if not _exists(CLINICAL_PREPROCESSOR_PATH):
        raise FileNotFoundError(
            f"Clinical preprocessor not found: "
            f"{CLINICAL_PREPROCESSOR_PATH}"
        )

    if not _exists(TARGET_ENCODER_PATH):
        raise FileNotFoundError(
            f"Target encoder not found: {TARGET_ENCODER_PATH}"
        )

    model = joblib.load(CLINICAL_MODEL_PATH)
    preprocessor = joblib.load(CLINICAL_PREPROCESSOR_PATH)
    target_encoder = joblib.load(TARGET_ENCODER_PATH)

    feature_data = _prepare_clinical_features(clinical_data)

    dataframe = pd.DataFrame([feature_data])

    transformed_data = preprocessor.transform(dataframe)

    prediction = model.predict(transformed_data)

    probabilities = None

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(transformed_data)[0]

    predicted_encoded = prediction[0]

    try:
        decoded_prediction = target_encoder.inverse_transform(
            [[predicted_encoded]]
        )[0][0]
    except Exception:
        decoded_prediction = str(predicted_encoded)

    probability_value = None

    if probabilities is not None:
        probability_value = float(max(probabilities))

    return {
        "module": "clinical",
        "prediction": str(decoded_prediction),
        "confidence": probability_value,
        "model": "RandomForestClassifier",
        "model_path": str(CLINICAL_MODEL_PATH),
        "clinical_decision_support_only": True,
    }


# ============================================================
# Ultrasound Model
# ============================================================

def analyze_ultrasound_data(
    image_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Ultrasound inference placeholder.

    The trained artifact is verified here, while the exact
    UNetSmall architecture from notebook 04 should be used
    for final image inference.
    """

    if not _exists(ULTRASOUND_MODEL_PATH):
        raise FileNotFoundError(
            f"Ultrasound model not found: {ULTRASOUND_MODEL_PATH}"
        )

    model_info: Dict[str, Any] = {}

    if _exists(ULTRASOUND_MODEL_INFO_PATH):
        try:
            with open(
                ULTRASOUND_MODEL_INFO_PATH,
                "r",
                encoding="utf-8",
            ) as file:
                model_info = json.load(file)
        except Exception:
            model_info = {}

    return {
        "module": "ultrasound",
        "status": "model_available",
        "model_path": str(ULTRASOUND_MODEL_PATH),
        "image_path": image_path,
        "model_info": model_info,
        "inference_ready": True,
        "note": (
            "Final segmentation inference must use the exact "
            "UNetSmall architecture from notebook 04."
        ),
        "clinical_decision_support_only": True,
    }


# ============================================================
# Multimodal Late Evidence Integration
# ============================================================

def generate_multimodal_result(
    clinical_result: Optional[Dict[str, Any]] = None,
    ultrasound_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Combine clinical and ultrasound evidence without creating
    artificial patient pairing.
    """

    clinical_available = clinical_result is not None
    ultrasound_available = ultrasound_result is not None

    return {
        "fusion_method": "Late Evidence Integration",

        "clinical_evidence_available": clinical_available,

        "ultrasound_evidence_available": ultrasound_available,

        "direct_training_pair_available": False,

        "artificial_patient_pairing": False,

        "requires_senior_doctor_review": True,

        "clinical_decision_support_only": True,

        "clinical_result": clinical_result,

        "ultrasound_result": ultrasound_result,

        "message": (
            "Multimodal evidence is presented as clinical decision "
            "support. No artificial clinical-ultrasound patient "
            "pairing is performed."
        ),
    }


# ============================================================
# Complete AI Pipeline
# ============================================================

def run_ai_pipeline(
    clinical_data: Optional[Dict[str, Any]] = None,
    ultrasound_image_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute the complete AI pipeline.
    """

    clinical_result = None
    ultrasound_result = None

    if clinical_data:
        clinical_result = analyze_clinical_data(clinical_data)

    if ultrasound_image_path:
        ultrasound_result = analyze_ultrasound_data(
            ultrasound_image_path
        )

    multimodal_result = generate_multimodal_result(
        clinical_result=clinical_result,
        ultrasound_result=ultrasound_result,
    )

    return {
        "status": "success",

        "clinical": clinical_result,

        "ultrasound": ultrasound_result,

        "multimodal": multimodal_result,

        "fusion_method": "Late Evidence Integration",

        "clinical_decision_support_only": True,

        "senior_doctor_review_required": True,
    }