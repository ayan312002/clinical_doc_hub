from pydantic import BaseModel


class MedicationOut(BaseModel):
    name: str
    dosage: str | None = None
    frequency: str | None = None
    route: str | None = None
    confidence: float | None = None


class LabResultOut(BaseModel):
    test_name: str
    value: str | None = None
    unit: str | None = None
    reference_range: str | None = None
    flag: str | None = None
    confidence: float | None = None


class VitalSignOut(BaseModel):
    name: str
    value: str | None = None
    unit: str | None = None
    confidence: float | None = None


class DiagnosisOut(BaseModel):
    name: str
    confidence: float | None = None


class ExtractionOut(BaseModel):
    id: str
    document_id: str
    patient_name: str | None = None
    patient_dob: str | None = None
    patient_mrn: str | None = None
    diagnoses: list[DiagnosisOut] = []
    medications: list[MedicationOut] = []
    lab_results: list[LabResultOut] = []
    procedures: list[str] = []
    allergies: list[str] = []
    vital_signs: list[VitalSignOut] = []
    discharge_date: str | None = None
    admission_date: str | None = None
    attending_physician: str | None = None
    summary: str = ""
    risk_flags: list[str] = []
    confidence_scores: dict = {}
    created_at: str = ""


class DocumentOut(BaseModel):
    id: str
    filename: str
    doc_type: str
    raw_text: str = ""
    patient_mrn: str | None = None
    status: str
    triage_level: str | None = None
    created_at: str
    processed_at: str | None = None
    extraction: ExtractionOut | None = None


class DocumentListOut(BaseModel):
    id: str
    filename: str
    doc_type: str
    patient_mrn: str | None = None
    status: str
    triage_level: str | None = None
    created_at: str
    processed_at: str | None = None


class PatientProfileOut(BaseModel):
    id: str
    mrn: str
    name: str | None = None
    dob: str | None = None
    document_count: int = 0
    latest_triage: str | None = None
    created_at: str
    updated_at: str


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str


class SearchResults(BaseModel):
    query: str
    results: list[DocumentListOut]
    total: int


class TriageRuleOut(BaseModel):
    level: str
    reason: str
