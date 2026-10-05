# ============================================================
# MultiModalCancerTherapy
# backend/app/db/models.py
# SQLAlchemy ORM Models
# PostgreSQL schema: multimodal
# ============================================================

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


# ============================================================
# Roles
# ============================================================

class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {
        "schema": "multimodal"
    }

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    role_name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    users: Mapped[list["User"]] = relationship(
        back_populates="role"
    )


# ============================================================
# Users
# ============================================================

class User(Base):
    __tablename__ = "users"
    __table_args__ = {
        "schema": "multimodal"
    }

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    email: Mapped[Optional[str]] = mapped_column(
        String(150),
        unique=True,
        nullable=True
    )

    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    role_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(
            "multimodal.roles.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    role: Mapped[Optional["Role"]] = relationship(
        back_populates="users"
    )


# ============================================================
# Patients
# ============================================================

class Patient(Base):
    __tablename__ = "patients"
    __table_args__ = {
        "schema": "multimodal"
    }

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    patient_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    age: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    sex: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True
    )

    phone: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True
    )

    email: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True
    )

    address: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="registered",
        nullable=False,
        index=True
    )

    created_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey(
            "multimodal.users.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    clinical_records: Mapped[list["ClinicalRecord"]] = relationship(
        back_populates="patient",
        cascade="all, delete-orphan"
    )

    ultrasound_cases: Mapped[list["UltrasoundCase"]] = relationship(
        back_populates="patient"
    )

    ai_analyses: Mapped[list["AIAnalysis"]] = relationship(
        back_populates="patient",
        cascade="all, delete-orphan"
    )

    ai_recommendations: Mapped[list["AIRecommendation"]] = relationship(
        back_populates="patient",
        cascade="all, delete-orphan"
    )


# ============================================================
# Clinical Records
# ============================================================

class ClinicalRecord(Base):
    __tablename__ = "clinical_records"
    __table_args__ = {
        "schema": "multimodal"
    }

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    patient_id: Mapped[int] = mapped_column(
        ForeignKey(
            "multimodal.patients.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    source_patient_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        index=True
    )

    age: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    sex: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True
    )

    on_thyroxine: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )

    query_on_thyroxine: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )

    on_antithyroid_meds: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )

    sick: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )

    pregnant: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )

    thyroid_surgery: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )

    i131_treatment: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )

    query_hypothyroid: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )

    query_hyperthyroid: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )

    lithium: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )

    goitre: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )

    tumor: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )

    hypopituitary: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )

    psych: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )

    tsh_measured: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )

    t3_measured: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )

    tt4_measured: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )

    t4u_measured: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )

    fti_measured: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )

    tbg_measured: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )

    tsh: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True
    )

    t3: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True
    )

    tt4: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True
    )

    t4u: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True
    )

    fti: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True
    )

    tbg: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True
    )

    referral_source: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    target_code: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        index=True
    )

    clinical_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    entered_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey(
            "multimodal.users.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    patient: Mapped["Patient"] = relationship(
        back_populates="clinical_records"
    )


# ============================================================
# Ultrasound Cases
# ============================================================

class UltrasoundCase(Base):
    __tablename__ = "ultrasound_cases"
    __table_args__ = {
        "schema": "multimodal"
    }

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    patient_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(
            "multimodal.patients.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    case_number: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        nullable=False,
        index=True
    )

    age: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    sex: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True
    )

    composition: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    echogenicity: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    margins: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    calcifications: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    tirads: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        index=True
    )

    reportbacaf: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    reporteco: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    case_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    patient: Mapped[Optional["Patient"]] = relationship(
        back_populates="ultrasound_cases"
    )

    images: Mapped[list["UltrasoundImage"]] = relationship(
        back_populates="ultrasound_case",
        cascade="all, delete-orphan"
    )


# ============================================================
# Ultrasound Images
# ============================================================

class UltrasoundImage(Base):
    __tablename__ = "ultrasound_images"
    __table_args__ = (
        UniqueConstraint(
            "ultrasound_case_id",
            "image_number",
            name="uq_ultrasound_case_image"
        ),
        {
            "schema": "multimodal"
        },
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    ultrasound_case_id: Mapped[int] = mapped_column(
        ForeignKey(
            "multimodal.ultrasound_cases.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    image_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    image_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    image_path: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    mask_filename: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    mask_path: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    width: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    height: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    has_annotation: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    annotation_points: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True
    )

    region_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    number_of_annotation_points: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    segmentation_pixels: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    segmentation_area_ratio: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    ultrasound_case: Mapped["UltrasoundCase"] = relationship(
        back_populates="images"
    )


# ============================================================
# AI Analyses
# ============================================================

class AIAnalysis(Base):
    __tablename__ = "ai_analyses"
    __table_args__ = {
        "schema": "multimodal"
    }

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    patient_id: Mapped[int] = mapped_column(
        ForeignKey(
            "multimodal.patients.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    clinical_record_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(
            "multimodal.clinical_records.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    ultrasound_image_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(
            "multimodal.ultrasound_images.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    clinical_top_prediction: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )

    clinical_top_probability: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True
    )

    clinical_predictions: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True
    )

    ultrasound_segmentation_area: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True
    )

    ultrasound_evidence: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True
    )

    fusion_method: Mapped[str] = mapped_column(
        String(100),
        default="Late Evidence Integration",
        nullable=False
    )

    multimodal_summary: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True
    )

    model_version: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="completed",
        nullable=False
    )

    requires_doctor_review: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey(
            "multimodal.users.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    patient: Mapped["Patient"] = relationship(
        back_populates="ai_analyses"
    )


# ============================================================
# AI Recommendations
# ============================================================

class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"
    __table_args__ = {
        "schema": "multimodal"
    }

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    patient_id: Mapped[int] = mapped_column(
        ForeignKey(
            "multimodal.patients.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    ai_analysis_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(
            "multimodal.ai_analyses.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    recommendation_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    evidence_summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    confidence: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True
    )

    doctor_status: Mapped[str] = mapped_column(
        String(30),
        default="pending_review",
        nullable=False
    )

    doctor_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    reviewed_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey(
            "multimodal.users.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    patient: Mapped["Patient"] = relationship(
        back_populates="ai_recommendations"
    )


# ============================================================
# Audit Logs
# ============================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = {
        "schema": "multimodal"
    }

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(
            "multimodal.users.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    entity_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    entity_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    ip_address: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )