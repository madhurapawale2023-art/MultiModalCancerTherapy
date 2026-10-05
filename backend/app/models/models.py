"""
Compatibility model module.

The application's canonical SQLAlchemy models are defined in:
    backend.app.db.models

This module re-exports those models so older imports continue
to work without creating duplicate ORM table definitions.
"""

from backend.app.db.models import (
    AIAnalysis,
    AIRecommendation,
    AuditLog,
    ClinicalRecord,
    Patient,
    Role,
    UltrasoundCase,
    UltrasoundImage,
    User,
)


__all__ = [
    "Role",
    "User",
    "Patient",
    "ClinicalRecord",
    "UltrasoundCase",
    "UltrasoundImage",
    "AIAnalysis",
    "AIRecommendation",
    "AuditLog",
]