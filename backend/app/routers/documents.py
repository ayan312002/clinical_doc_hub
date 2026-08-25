import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.database import get_db
from backend.app.models import Document, Extraction, PatientProfile
from backend.app.schemas import (
    DocumentListOut,
    DocumentOut,
    ExtractionOut,
    PatientProfileOut,
    UploadResponse,
)
from backend.app.services.extraction import process_document
from backend.app.services.parser import SUPPORTED_EXTENSIONS, parse_document
from backend.app.config import settings

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename
    content = await file.read()
    file_path.write_bytes(content)

    raw_text = ""
    try:
        raw_text = parse_document(str(file_path))
    except Exception as e:
        raw_text = f"[Parse error: {e}]"

    doc = Document(
        filename=file.filename,
        raw_text=raw_text,
        status="uploaded",
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    background_tasks.add_task(process_document, db, doc.id)

    return UploadResponse(
        document_id=doc.id,
        filename=doc.filename,
        status=doc.status,
        message="Document uploaded and queued for processing",
    )


@router.get("", response_model=list[DocumentListOut])
async def list_documents(
    skip: int = 0,
    limit: int = 50,
    status: str | None = None,
    triage: str | None = None,
    doc_type: str | None = None,
    patient_mrn: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Document)
    if status:
        query = query.where(Document.status == status)
    if triage:
        query = query.where(Document.triage_level == triage)
    if doc_type:
        query = query.where(Document.doc_type == doc_type)
    if patient_mrn:
        query = query.where(Document.patient_mrn == patient_mrn)
    query = query.order_by(Document.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
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


@router.get("/{document_id}", response_model=DocumentOut)
async def get_document(document_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Document)
        .where(Document.id == document_id)
        .options(selectinload(Document.extraction))
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    extraction_out = None
    if doc.extraction:
        e = doc.extraction
        extraction_out = ExtractionOut(
            id=e.id,
            document_id=e.document_id,
            patient_name=e.patient_name,
            patient_dob=e.patient_dob,
            patient_mrn=e.patient_mrn,
            diagnoses=json.loads(e.diagnoses_json) if e.diagnoses_json else [],
            medications=json.loads(e.medications_json) if e.medications_json else [],
            lab_results=json.loads(e.lab_results_json) if e.lab_results_json else [],
            procedures=json.loads(e.procedures_json) if e.procedures_json else [],
            allergies=json.loads(e.allergies_json) if e.allergies_json else [],
            vital_signs=json.loads(e.vital_signs_json) if e.vital_signs_json else [],
            discharge_date=e.discharge_date,
            admission_date=e.admission_date,
            attending_physician=e.attending_physician,
            summary=e.summary,
            risk_flags=json.loads(e.risk_flags_json) if e.risk_flags_json else [],
            confidence_scores=json.loads(e.confidence_scores_json) if e.confidence_scores_json else {},
            created_at=e.created_at.isoformat() if e.created_at else "",
        )

    return DocumentOut(
        id=doc.id,
        filename=doc.filename,
        doc_type=doc.doc_type,
        raw_text=doc.raw_text,
        patient_mrn=doc.patient_mrn,
        status=doc.status,
        triage_level=doc.triage_level,
        created_at=doc.created_at.isoformat() if doc.created_at else "",
        processed_at=doc.processed_at.isoformat() if doc.processed_at else None,
        extraction=extraction_out,
    )


@router.delete("/{document_id}")
async def delete_document(document_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await db.delete(doc)
    await db.commit()
    return {"detail": "Document deleted"}


@router.post("/{document_id}/reprocess", response_model=UploadResponse)
async def reprocess_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.extraction:
        await db.delete(doc.extraction)
        await db.commit()

    doc.status = "uploaded"
    await db.commit()

    background_tasks.add_task(process_document, db, doc.id)

    return UploadResponse(
        document_id=doc.id,
        filename=doc.filename,
        status="uploaded",
        message="Document queued for reprocessing",
    )


@router.get("/{document_id}/file")
async def get_document_file(document_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = Path(settings.UPLOAD_DIR) / doc.filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    media_types = {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    media_type = media_types.get(file_path.suffix.lower(), "application/octet-stream")

    preview_types = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp"}
    disposition = "inline" if file_path.suffix.lower() in preview_types else "attachment"

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=doc.filename,
        content_disposition_type=disposition,
    )
