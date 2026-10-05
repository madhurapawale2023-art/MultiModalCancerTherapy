"""
Dataset and trained-model metadata service.

Reads the existing clinical training CSV (READ-ONLY) and the
existing model metadata JSON files so the Dashboard can display
REAL project values instead of hardcoded numbers.

The training CSV is never modified.

No DNA testing functionality is included.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd


# ============================================================
# Project paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Candidate locations for the existing clinical training CSV.
CLINICAL_CSV_CANDIDATES = (
    PROJECT_ROOT
    / "datasets"
    / "raw"
    / "clinical"
    / "Thyroid Disease Data"
    / "thyroidDF.csv",
    PROJECT_ROOT
    / "datasets"
    / "raw"
    / "clinical"
    / "thyroidDF.csv",
)

CLINICAL_FEATURE_INFO = (
    PROJECT_ROOT / "models" / "clinical" / "feature_info.json"
)

FINAL_METRICS = PROJECT_ROOT / "models" / "final_ml_metrics.json"

ULTRASOUND_MODEL_INFO = (
    PROJECT_ROOT / "models" / "image" / "ultrasound_model_info.json"
)

FUSION_CONFIG = PROJECT_ROOT / "models" / "multimodal_fusion_config.json"


# ============================================================
# Simple in-memory cache (the CSV is read at most once per change)
# ============================================================

_lock = threading.Lock()

_cache: Dict[str, Any] = {}


# ============================================================
# Helpers
# ============================================================

def _read_json(path: Path) -> Dict[str, Any]:
    """
    Read a JSON file safely and return a dictionary.
    """

    try:
        with open(path, "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)

        if isinstance(data, dict):
            return data

        return {}

    except Exception:
        return {}


def find_clinical_csv() -> Optional[Path]:
    """
    Return the existing clinical training CSV path if present.
    """

    for candidate in CLINICAL_CSV_CANDIDATES:

        if candidate.exists() and candidate.is_file():
            return candidate

    return None


def _value_counts(
    frame: "pd.DataFrame",
    column: str,
) -> Dict[str, int]:
    """
    Return a JSON-safe value-count dictionary for a column.
    """

    if column not in frame.columns:
        return {}

    counts = frame[column].value_counts(dropna=True)

    return {
        str(key): int(value)
        for key, value in counts.items()
    }


# ============================================================
# Clinical training CSV summary (READ-ONLY)
# ============================================================

def get_clinical_dataset_summary(
    force: bool = False,
) -> Dict[str, Any]:
    """
    Read the existing clinical training CSV (READ ONLY) and return
    a compact summary. The CSV is never modified.

    The result is cached and only recomputed when the file
    modification time changes.
    """

    csv_path = find_clinical_csv()

    if csv_path is None:
        return {
            "available": False,
            "reason": "Clinical training CSV not found.",
        }

    try:
        modified_time = csv_path.stat().st_mtime
    except OSError:
        modified_time = 0.0

    with _lock:

        cached = _cache.get("clinical_csv")

        if (
            not force
            and cached is not None
            and cached.get("modified_time") == modified_time
        ):
            return cached["summary"]

    try:
        frame = pd.read_csv(csv_path)
    except Exception as error:

        return {
            "available": False,
            "reason": f"Unable to read training CSV: {error}",
        }

    target_distribution = _value_counts(frame, "target")

    age_statistics: Dict[str, Any] = {}

    if "age" in frame.columns:

        ages = pd.to_numeric(
            frame["age"],
            errors="coerce",
        ).dropna()

        if not ages.empty:

            age_statistics = {
                "min": int(ages.min()),
                "max": int(ages.max()),
                "mean": round(float(ages.mean()), 2),
                "median": round(float(ages.median()), 2),
                "count": int(ages.count()),
            }

    try:
        relative_path = str(
            csv_path.relative_to(PROJECT_ROOT)
        ).replace("\\", "/")
    except ValueError:
        relative_path = str(csv_path).replace("\\", "/")

    summary: Dict[str, Any] = {
        "available": True,
        "file_name": csv_path.name,
        "relative_path": relative_path,
        "rows": int(frame.shape[0]),
        "columns": int(frame.shape[1]),
        "column_names": [str(name) for name in frame.columns.tolist()],
        "target_column": (
            "target" if "target" in frame.columns else None
        ),
        "target_classes": len(target_distribution),
        "target_distribution": target_distribution,
        "sex_distribution": _value_counts(frame, "sex"),
        "referral_source_distribution": _value_counts(
            frame,
            "referral_source",
        ),
        "age_statistics": age_statistics,
    }

    with _lock:
        _cache["clinical_csv"] = {
            "modified_time": modified_time,
            "summary": summary,
        }

    return summary


# ============================================================
# Model metadata
# ============================================================

def get_clinical_model_metadata() -> Dict[str, Any]:
    """
    Return clinical model metadata from existing project artifacts.
    """

    feature_info = _read_json(CLINICAL_FEATURE_INFO)

    final_metrics = _read_json(FINAL_METRICS)

    metrics: Dict[str, Any] = {}

    if isinstance(final_metrics, dict):
        metrics = final_metrics.get("clinical_model", {}) or {}

    return {
        "feature_info": feature_info,
        "metrics": metrics,
    }


def get_ultrasound_model_metadata() -> Dict[str, Any]:
    """
    Return ultrasound model metadata from existing project artifacts.
    """

    info = _read_json(ULTRASOUND_MODEL_INFO)

    final_metrics = _read_json(FINAL_METRICS)

    segmentation: Dict[str, Any] = {}

    if isinstance(final_metrics, dict):
        segmentation = (
            final_metrics.get("ultrasound_segmentation", {}) or {}
        )

    if segmentation:
        info = {**info, "final_metrics": segmentation}

    return info


def get_multimodal_metadata() -> Dict[str, Any]:
    """
    Return multimodal fusion metadata from existing project artifacts.
    """

    fusion_config = _read_json(FUSION_CONFIG)

    final_metrics = _read_json(FINAL_METRICS)

    summary: Dict[str, Any] = {}

    if isinstance(final_metrics, dict):
        summary = final_metrics.get("multimodal", {}) or {}

    return {
        "fusion_config": fusion_config,
        "summary": summary,
    }
