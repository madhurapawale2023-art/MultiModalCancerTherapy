"""
Main FastAPI application for MultiModalCancerTherapy.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import (
    ai,
    audit,
    auth,
    dashboard,
    patients,
    reports,
    specialists,
    workflow,
)
from backend.app.core.config import get_cors_origins, settings
from backend.app.db.database import check_database_connection


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description=(
        "AI-powered clinical decision support system for "
        "multimodal cancer therapy recommendation."
    ),
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTES
# ============================================================

app.include_router(auth.router)
app.include_router(ai.router)
app.include_router(audit.router)
app.include_router(dashboard.router)
app.include_router(patients.router)
app.include_router(reports.router)
app.include_router(specialists.router)
app.include_router(workflow.router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "application": settings.APP_NAME,
        "status": "running",
        "message": "MultiModalCancerTherapy API is running",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    database_ok = check_database_connection()

    return {
        "status": "healthy" if database_ok else "unhealthy",
        "application": settings.APP_NAME,
        "database": "PostgreSQL" if database_ok else "Unavailable",
        "database_connection": database_ok,
        "clinical_decision_support_only": True,
        "senior_doctor_review_required": True,
    }


# ============================================================
# APPLICATION INFO
# ============================================================

@app.get("/api/info")
def application_info():
    return {
        "application": settings.APP_NAME,
        "version": "1.0.0",
        "backend": "FastAPI",
        "database": "PostgreSQL",
        "frontend": "AngularJS 1.8.x",
        "ai_type": "Clinical Decision Support",
        "fusion_method": "Late Evidence Integration",
        "dna_testing": False,
        "senior_doctor_final_authority": True,
    }