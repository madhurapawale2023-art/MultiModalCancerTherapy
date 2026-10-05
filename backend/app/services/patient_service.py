# Patient workflow/business logic.

from typing import List, Optional

from sqlalchemy.orm import Session

from backend.app.db.models import Patient


def generate_patient_code(db: Session) -> str:
    """
    Generate a unique patient code.

    Example:
        PAT-0001
        PAT-0002
        PAT-0003
    """

    last_patient = (
        db.query(Patient)
        .order_by(Patient.id.desc())
        .first()
    )

    next_id = 1 if last_patient is None else last_patient.id + 1

    return f"PAT-{next_id:04d}"


def create_patient(
    db: Session,
    full_name: str,
    age: Optional[int] = None,
    sex: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    address: Optional[str] = None,
    status: str = "registered",
    created_by: Optional[int] = None,
) -> Patient:
    """
    Create and save a new patient.
    """

    patient = Patient(
        patient_code=generate_patient_code(db),
        full_name=full_name,
        age=age,
        sex=sex,
        phone=phone,
        email=email,
        address=address,
        status=status,
        created_by=created_by,
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    return patient


def get_patient(
    db: Session,
    patient_id: int,
) -> Optional[Patient]:
    """
    Get one patient by ID.
    """

    return (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )


def get_patient_by_code(
    db: Session,
    patient_code: str,
) -> Optional[Patient]:
    """
    Get one patient by patient code.
    """

    return (
        db.query(Patient)
        .filter(Patient.patient_code == patient_code)
        .first()
    )


def get_all_patients(
    db: Session,
) -> List[Patient]:
    """
    Get all patients.
    """

    return (
        db.query(Patient)
        .order_by(Patient.id.desc())
        .all()
    )


def search_patients(
    db: Session,
    search_text: str,
) -> List[Patient]:
    """
    Search patients by name or patient code.
    """

    search = search_text.strip()

    if not search:
        return get_all_patients(db)

    pattern = f"%{search}%"

    return (
        db.query(Patient)
        .filter(
            (Patient.full_name.ilike(pattern))
            | (Patient.patient_code.ilike(pattern))
        )
        .order_by(Patient.id.desc())
        .all()
    )


def update_patient(
    db: Session,
    patient: Patient,
    data: dict,
) -> Patient:
    """
    Update patient fields.
    """

    allowed_fields = {
        "full_name",
        "age",
        "sex",
        "phone",
        "email",
        "address",
        "status",
    }

    for field, value in data.items():
        if field in allowed_fields:
            setattr(patient, field, value)

    db.commit()
    db.refresh(patient)

    return patient


def delete_patient(
    db: Session,
    patient: Patient,
) -> bool:
    """
    Delete a patient.
    """

    db.delete(patient)
    db.commit()

    return True