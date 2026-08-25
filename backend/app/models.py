import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


def gen_uuid():
    return str(uuid.uuid4())


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    filename: Mapped[str] = mapped_column(String(255))
    doc_type: Mapped[str] = mapped_column(String(50), default="unknown")
    raw_text: Mapped[str] = mapped_column(Text, default="")
    source_image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    patient_mrn: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="uploaded")
    triage_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    extraction: Mapped[Optional["Extraction"]] = relationship(
        "Extraction", back_populates="document", uselist=False, cascade="all, delete-orphan"
    )


class Extraction(Base):
    __tablename__ = "extractions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("documents.id", ondelete="CASCADE"), unique=True
    )
    patient_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    patient_dob: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    patient_mrn: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    diagnoses_json: Mapped[str] = mapped_column(Text, default="[]")
    medications_json: Mapped[str] = mapped_column(Text, default="[]")
    lab_results_json: Mapped[str] = mapped_column(Text, default="[]")
    procedures_json: Mapped[str] = mapped_column(Text, default="[]")
    allergies_json: Mapped[str] = mapped_column(Text, default="[]")
    vital_signs_json: Mapped[str] = mapped_column(Text, default="[]")
    discharge_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    admission_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    attending_physician: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    summary: Mapped[str] = mapped_column(Text, default="")
    risk_flags_json: Mapped[str] = mapped_column(Text, default="[]")
    confidence_scores_json: Mapped[str] = mapped_column(Text, default="{}")
    raw_llm_response: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    document: Mapped["Document"] = relationship("Document", back_populates="extraction")


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    mrn: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    dob: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    document_count: Mapped[int] = mapped_column(default=0)
    latest_triage: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
