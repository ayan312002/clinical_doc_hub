import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Document, Extraction, PatientProfile
from backend.app.prompts.extraction import (
    DOCUMENT_TYPE_PROMPT,
    EXTRACTION_SYSTEM_PROMPT,
    SUMMARY_SYSTEM_PROMPT,
    TRIAGE_SYSTEM_PROMPT,
)
from backend.app.services.llm import call_llm, call_llm_with_retry
from backend.app.services.parser import detect_doc_type, image_to_base64, parse_document

logger = logging.getLogger(__name__)

TRIAGE_RULES = {
    "critical_keywords": [
        "stat", "emergency", "critical", "life-threatening", "cardiac arrest",
        "respiratory failure", "sepsis", "hemorrhage", "anaphylaxis",
    ],
    "critical_lab_thresholds": {
        "glucose": (40, 500),
        "potassium": (2.5, 6.5),
        "sodium": (120, 160),
        "creatinine": (0.1, 10.0),
        "hemoglobin": (5.0, 20.0),
        "wbc": (1.0, 30.0),
        "platelets": (20, 500),
    },
    "high_keywords": [
        "abnormal", "elevated", "decreased", "critical value",
        "requires follow-up", "urgent",
    ],
}


def apply_triage_rules(text: str, lab_results: list[dict]) -> tuple[str, list[str]]:
    reasons = []
    level = "normal"

    lower_text = text.lower()
    for kw in TRIAGE_RULES["critical_keywords"]:
        if kw in lower_text:
            reasons.append(f"Contains critical keyword: '{kw}'")
            level = "critical"

    for lab in lab_results:
        name_lower = lab.get("test_name", "").lower()
        flag = lab.get("flag", "")
        if "critical" in str(flag):
            if level != "critical":
                level = "critical"
            reasons.append(f"Critical lab value: {lab.get('test_name')} = {lab.get('value')}")

    if level == "normal":
        for kw in TRIAGE_RULES["high_keywords"]:
            if kw in lower_text:
                reasons.append(f"Contains high-priority keyword: '{kw}'")
                level = "high"
                break

    if not reasons:
        reasons.append("No rule-based flags triggered")

    return level, reasons


async def process_document(db: AsyncSession, document_id: str):
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        logger.error(f"Document {document_id} not found")
        return

    doc.status = "processing"
    await db.commit()

    try:
        if not doc.raw_text:
            doc.raw_text = parse_document(doc.raw_text or doc.filename)

        if not doc.doc_type or doc.doc_type == "unknown":
            doc.doc_type = detect_doc_type(doc.raw_text, doc.filename)

        extraction_result = await call_llm_with_retry(
            system_prompt=EXTRACTION_SYSTEM_PROMPT,
            user_content=f"Extract structured clinical data from this document:\n\n{doc.raw_text}",
        )
        extraction_data = extraction_result if isinstance(extraction_result, dict) else {}

        summary_text = ""
        try:
            summary_result = await call_llm(
                system_prompt=SUMMARY_SYSTEM_PROMPT,
                user_content=f"Generate a clinical summary for this document:\n\n{doc.raw_text}",
                response_format=None,
            )
            summary_text = summary_result if isinstance(summary_result, str) else json.dumps(summary_result)
        except Exception as e:
            logger.warning(f"Summary generation failed, using fallback: {e}")
            summary_text = f"Clinical document: {doc.filename}. Extraction completed but summary generation failed."

        llm_triage = "routine"
        try:
            triage_result = await call_llm_with_retry(
                system_prompt=TRIAGE_SYSTEM_PROMPT,
                user_content=f"Classify the urgency of this clinical document:\n\n{doc.raw_text}",
            )
            llm_triage = triage_result.get("level", "routine") if isinstance(triage_result, dict) else "routine"
        except Exception as e:
            logger.warning(f"LLM triage failed, using rule-based only: {e}")

        lab_results = extraction_data.get("lab_results", [])
        rule_triage, rule_reasons = apply_triage_rules(doc.raw_text, lab_results)

        priority = {"critical": 3, "high": 2, "routine": 1, "normal": 0}
        final_triage = llm_triage if priority.get(llm_triage, 0) >= priority.get(rule_triage, 0) else rule_triage

        extraction = Extraction(
            document_id=doc.id,
            patient_name=extraction_data.get("patient_name"),
            patient_dob=extraction_data.get("patient_dob"),
            patient_mrn=extraction_data.get("patient_mrn"),
            diagnoses_json=json.dumps(extraction_data.get("diagnoses", [])),
            medications_json=json.dumps(extraction_data.get("medications", [])),
            lab_results_json=json.dumps(extraction_data.get("lab_results", [])),
            procedures_json=json.dumps(extraction_data.get("procedures", [])),
            allergies_json=json.dumps(extraction_data.get("allergies", [])),
            vital_signs_json=json.dumps(extraction_data.get("vital_signs", [])),
            discharge_date=extraction_data.get("discharge_date"),
            admission_date=extraction_data.get("admission_date"),
            attending_physician=extraction_data.get("attending_physician"),
            summary=summary_text,
            risk_flags_json=json.dumps(extraction_data.get("risk_flags", []) + rule_reasons),
            confidence_scores_json=json.dumps(extraction_data.get("confidence_scores", {})),
            raw_llm_response=json.dumps(extraction_data),
        )
        db.add(extraction)

        patient_mrn = extraction_data.get("patient_mrn")
        if patient_mrn:
            doc.patient_mrn = patient_mrn
            await _link_patient(db, patient_mrn, extraction_data, final_triage)

        doc.triage_level = final_triage
        doc.status = "completed"
        doc.processed_at = datetime.now(timezone.utc)

        await db.commit()

    except Exception as e:
        logger.error(f"Processing failed for document {document_id}: {e}")
        doc.status = "failed"
        await db.commit()
        raise


async def _link_patient(
    db: AsyncSession, mrn: str, extraction_data: dict, triage_level: str
):
    result = await db.execute(select(PatientProfile).where(PatientProfile.mrn == mrn))
    profile = result.scalar_one_or_none()

    if profile:
        profile.document_count += 1
        profile.updated_at = datetime.now(timezone.utc)
        if triage_level in ("critical", "high"):
            profile.latest_triage = triage_level
        if extraction_data.get("patient_name") and not profile.name:
            profile.name = extraction_data["patient_name"]
        if extraction_data.get("patient_dob") and not profile.dob:
            profile.dob = extraction_data["patient_dob"]
    else:
        profile = PatientProfile(
            mrn=mrn,
            name=extraction_data.get("patient_name"),
            dob=extraction_data.get("patient_dob"),
            document_count=1,
            latest_triage=triage_level,
        )
        db.add(profile)
