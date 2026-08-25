import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models import Document, Extraction, PatientProfile
from backend.app.schemas import DocumentListOut, PatientProfileOut

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("", response_model=list[PatientProfileOut])
async def list_patients(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PatientProfile).order_by(PatientProfile.updated_at.desc()).offset(skip).limit(limit)
    )
    profiles = result.scalars().all()
    return [
        PatientProfileOut(
            id=p.id,
            mrn=p.mrn,
            name=p.name,
            dob=p.dob,
            document_count=p.document_count,
            latest_triage=p.latest_triage,
            created_at=p.created_at.isoformat() if p.created_at else "",
            updated_at=p.updated_at.isoformat() if p.updated_at else "",
        )
        for p in profiles
    ]


@router.get("/{mrn}", response_model=PatientProfileOut)
async def get_patient(mrn: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PatientProfile).where(PatientProfile.mrn == mrn))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientProfileOut(
        id=profile.id,
        mrn=profile.mrn,
        name=profile.name,
        dob=profile.dob,
        document_count=profile.document_count,
        latest_triage=profile.latest_triage,
        created_at=profile.created_at.isoformat() if profile.created_at else "",
        updated_at=profile.updated_at.isoformat() if profile.updated_at else "",
    )


@router.get("/{mrn}/documents", response_model=list[DocumentListOut])
async def get_patient_documents(mrn: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Document)
        .where(Document.patient_mrn == mrn)
        .order_by(Document.created_at.desc())
    )
    docs = result.scalars().all()
    return [
        DocumentListOut(
            id=d.id,
            filename=d.filename,
            doc_type=d.doc_type,
            patient_mrn=d.patient_mrn,
            status=d.status,
            triage_level=d.triage_level,
            created_at=d.created_at.isoformat() if d.created_at else "",
            processed_at=d.processed_at.isoformat() if d.processed_at else None,
        )
        for d in docs
    ]


@router.get("/{mrn}/timeline")
async def get_patient_timeline(mrn: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Document, Extraction)
        .outerjoin(Extraction, Document.id == Extraction.document_id)
        .where(Document.patient_mrn == mrn)
        .order_by(Document.created_at.desc())
    )
    rows = result.all()

    timeline = []
    for doc, extraction in rows:
        entry = {
            "document_id": doc.id,
            "filename": doc.filename,
            "doc_type": doc.doc_type,
            "triage_level": doc.triage_level,
            "created_at": doc.created_at.isoformat() if doc.created_at else "",
        }
        if extraction:
            entry["summary"] = extraction.summary
            entry["diagnoses"] = json.loads(extraction.diagnoses_json) if extraction.diagnoses_json else []
            entry["medications"] = json.loads(extraction.medications_json) if extraction.medications_json else []
        timeline.append(entry)

    return {"mrn": mrn, "timeline": timeline}
