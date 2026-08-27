from fastapi import APIRouter, Depends
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models import Document, Extraction
from backend.app.schemas import DocumentListOut, SearchResults

router = APIRouter(tags=["search"])


@router.get("/search", response_model=SearchResults)
async def search_documents(
    q: str = "",
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    if not q.strip():
        return SearchResults(query=q, results=[], total=0)

    search_term = f"%{q}%"

    query = (
        select(Document)
        .outerjoin(Extraction, Document.id == Extraction.document_id)
        .where(
            or_(
                Document.filename.ilike(search_term),
                Document.raw_text.ilike(search_term),
                Document.patient_mrn.ilike(search_term),
                Extraction.patient_name.ilike(search_term),
                Extraction.summary.ilike(search_term),
                Extraction.diagnoses_json.ilike(search_term),
            )
        )
        .distinct()
        .order_by(Document.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    count_query = (
        select(Document.id)
        .outerjoin(Extraction, Document.id == Extraction.document_id)
        .where(
            or_(
                Document.filename.ilike(search_term),
                Document.raw_text.ilike(search_term),
                Document.patient_mrn.ilike(search_term),
                Extraction.patient_name.ilike(search_term),
                Extraction.summary.ilike(search_term),
                Extraction.diagnoses_json.ilike(search_term),
            )
        )
        .distinct()
    )

    result = await db.execute(query)
    docs = result.scalars().all()

    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())

    results = [
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

    return SearchResults(query=q, results=results, total=total)
