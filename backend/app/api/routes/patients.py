from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.dependencies import (
    get_current_user,
    require_roles,
)
from backend.app.db.database import get_db
from backend.app.db.models import Patient
from backend.app.schemas.patient import (
    PatientCreate,
    PatientListResponse,
    PatientResponse,
    PatientUpdate,
)
from backend.app.services.patient_service import generate_patient_code


router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


# ============================================================
# ROLE PROTECTION
# ============================================================

manage_patients = require_roles(
    "Admin",
    "Senior Doctor",
    "Assistant Doctor",
)


# ============================================================
# LIST PATIENTS
# ============================================================

@router.get(
    "/",
    response_model=PatientListResponse,
)
def list_patients(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    patients: List[Patient] = (
        db.query(Patient)
        .order_by(Patient.id.desc())
        .all()
    )

    return {
        "items": patients,
        "total": len(patients),
    }


# ============================================================
# GET SINGLE PATIENT
# ============================================================

@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return patient


# ============================================================
# CREATE PATIENT
# ============================================================

@router.post(
    "/",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user=Depends(manage_patients),
):
    patient = Patient(
        patient_code=generate_patient_code(db),
        full_name=patient_data.full_name,
        age=patient_data.age,
        sex=patient_data.sex,
        phone=patient_data.phone,
        email=patient_data.email,
        address=patient_data.address,
        status=patient_data.status,
        created_by=current_user.id,
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    return patient


# ============================================================
# UPDATE PATIENT
# ============================================================

@router.put(
    "/{patient_id}",
    response_model=PatientResponse,
)
def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(manage_patients),
):
    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    update_data = patient_data.model_dump(
        exclude_unset=True
    )

    allowed_fields = {
        "full_name",
        "age",
        "sex",
        "phone",
        "email",
        "address",
        "status",
    }

    for field, value in update_data.items():
        if field in allowed_fields:
            setattr(patient, field, value)

    db.commit()
    db.refresh(patient)

    return patient


# ============================================================
# DELETE PATIENT
# ============================================================

@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(manage_patients),
):
    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    db.delete(patient)
    db.commit()

    return None