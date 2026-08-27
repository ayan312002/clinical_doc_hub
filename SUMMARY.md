# Clinical Document Intelligence Hub — Summary

## 1. Problem Understanding and Objective

The client is a mid-size healthcare provider whose clinical and administrative staff spend significant time manually reviewing patient documents — intake forms, discharge summaries, lab reports, and physician notes — to extract key information for care coordination and decision-making.

This manual process has three core problems:

- **Slow** — Delays care coordination as staff must read through entire documents to find relevant data points
- **Inconsistent** — Different staff members extract different fields, with no standard for what to capture or how to categorize urgency
- **Error-prone** — Critical details get missed: an overlooked allergy, an abnormal lab value buried in a paragraph, a medication interaction that goes unnoticed

The objective is to build a working AI prototype that demonstrates how AI can transform fragmented healthcare data into consistent, decision-ready outputs — reducing the manual burden on clinical and administrative teams.

**Deliverables achieved:**
- A working prototype that accepts clinical document inputs (text, PDF, or image)
- Structured information extraction with confidence scoring
- Clear, readable summaries and triage classifications for a clinical audience
- Multi-format support matching the document types staff currently handle

---

## 2. Solution Architecture and Design Flow

```
                         ┌──────────────────────────────────────────┐
                         │           Clinical Doc Hub               │
                         └──────────────────────────────────────────┘

  ┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │  Staff    │────▶│  React UI    │────▶│  FastAPI     │────▶│  SQLite      │
  │  Uploads  │     │  (Port 3000) │     │  (Port 8000) │     │  Database    │
  │  Document │     │              │     │              │     │              │
  └──────────┘     └──────────────┘     └──────┬───────┘     └──────────────┘
                                               │
                              ┌─────────────────┼─────────────────┐
                              │                 │                 │
                         ┌────▼────┐     ┌──────▼──────┐   ┌─────▼─────┐
                         │  Parser │     │  LLM Calls  │   │  Triage   │
                         │  Layer  │     │ (OpenRouter) │   │  Rules    │
                         └────┬────┘     └──────┬──────┘   └─────┬─────┘
                              │                 │                 │
                              │    ┌────────────┼────────────┐   │
                              │    │            │            │   │
                              │ ┌──▼──┐  ┌──────▼──┐  ┌─────▼┐  │
                              │ │Extract│  │Summarize│  │Triage│◀─┘
                              │ │(JSON) │  │ (Text)  │  │(JSON)│
                              │ └──┬──┘  └──────┬──┘  └──┬───┘
                              │    │            │        │
                              └────┼────────────┼────────┘
                                   │            │
                              ┌────▼────────────▼────┐
                              │   Dashboard Display   │
                              │  • Extracted Data     │
                              │  • AI Summary         │
                              │  • Risk Flags         │
                              │  • Patient MRN Link   │
                              └───────────────────────┘
```

**Data flow in the clinical context:**

1. **Upload** — Staff uploads a document through the web interface (PDF discharge summary, DOCX physician notes, scanned image lab report, or text-based intake form)
2. **Parse** — System extracts raw text using format-specific parsers (PyMuPDF for PDFs, python-docx for DOCX, Tesseract OCR for scanned images)
3. **Extract** — LLM pulls structured clinical data: diagnoses, medications with dosage/frequency/route, lab results with reference ranges and abnormal flags, vital signs, procedures, allergies — the same fields staff currently extract by hand
4. **Summarize** — LLM generates a concise clinical summary written in language appropriate for healthcare professionals
5. **Triage** — LLM classifies urgency (critical/high/routine/normal) while rule-based checks catch critical lab values and keywords — ensuring no critical case slips through
6. **Link** — Documents auto-linked to patient profiles by MRN, building a longitudinal view
7. **Display** — Staff views structured data, AI summary, risk flags, and confidence scores in the dashboard

---

## 3. Implementation Highlights

### Multi-Format Document Ingestion

The system handles the exact document types used in clinical settings:

| Format | Parser | Use Case |
|--------|--------|----------|
| PDF | PyMuPDF (fitz) | Discharge summaries, lab reports |
| DOCX | python-docx | Physician notes, intake forms |
| TXT/MD | Direct read | Text-based notes, medication lists |
| Images (PNG/JPG/TIFF) | Tesseract OCR | Scanned lab reports, handwritten notes |

Document type is auto-detected via filename keywords and content analysis (e.g., "reference range" indicates a lab report, "chief complaint" indicates physician notes).

### Structured Clinical Extraction

The LLM extracts data into a consistent schema covering every field a clinician would need:

- **Patient info**: Name, DOB, MRN, attending physician
- **Diagnoses**: With confidence scores
- **Medications**: Name, dosage, frequency, route, confidence
- **Lab results**: Test name, value, unit, reference range, flag (normal/abnormal/critical)
- **Vital signs**: Name, value, unit, confidence
- **Procedures** and **Allergies**: As listed
- **Risk flags**: Abnormal values, potential drug interactions, missing critical data

### Confidence Scoring

Each extracted field carries a confidence score (0.0–1.0) so clinicians know which data points need verification. The system also provides aggregate confidence scores for patient info, diagnoses, medications, and lab results — giving staff an immediate sense of extraction reliability.

### Dual Triage System

Two independent triage mechanisms run in parallel:

- **LLM triage**: AI classifies urgency based on the full clinical context
- **Rule-based triage**: Deterministic checks for critical lab values (potassium <2.5 or >6.5, glucose <40 or >500, sodium <120 or >160) and high-priority keywords (cardiac arrest, sepsis, hemorrhage, stat)

The final triage is the higher-priority result of the two. This ensures that even if the LLM misclassifies a case, the rule-based system catches critical conditions.

### Patient MRN Linking

Documents are auto-linked to patient profiles by MRN. When a new document is processed, the system creates or updates a patient profile — incrementing document count, updating name/DOB if not already present, and tracking the latest triage level. This builds a longitudinal view across multiple document types per patient.

### Live Status Updates

The document list and detail pages auto-refresh every 10 seconds, so staff see real-time processing status without manually refreshing. A spinner indicates documents still being processed.

---

## 4. Challenges and Learnings

### Data Quality Gap

The prototype uses clean, well-formatted synthetic data. Real clinical documents are messy — inconsistent formatting across departments, handwritten notes, poor scan quality, abbreviations that vary by institution. A production system would need fine-tuning on the client's actual document templates and formats to achieve reliable extraction accuracy.

**What we learned**: The LLM handles formatted text well but would benefit significantly from few-shot examples using the client's actual documents. The extraction schema should be validated against what the client's staff actually needs — they may prioritize different fields than what we assumed.

### Triage Calibration

The rule-based thresholds are simplified heuristics. Real clinical triage depends on patient context — a potassium of 6.5 means something very different for a patient with chronic kidney disease vs. an acute presentation. The dual approach (AI + rules) is a starting point, but would require clinician input to validate and refine against actual patient outcomes.

**What we learned**: The LLM triage is surprisingly good at context-aware classification (it caught a critical case that the rules missed because the lab value was borderline but the clinical context was severe). However, without validation against real outcomes, we can't trust it as a standalone system.

### LLM Reliability

Free-tier models occasionally return empty or malformed responses. The retry logic handles this gracefully, but it adds latency and doesn't guarantee success. A production deployment would need a paid model with guaranteed uptime, or a fine-tuned model that's more predictable on clinical text.

**What we learned**: The JSON mode is critical for structured extraction — without it, the LLM sometimes wraps JSON in markdown code blocks or adds explanatory text. Even with JSON mode, validation and retry logic is necessary.

### Privacy and Compliance

The prototype stores documents locally with no encryption at rest and no access controls. A real deployment needs HIPAA-compliant storage, audit logging, role-based access control, and Business Associate Agreements (BAAs) with the LLM provider. This is non-negotiable for any clinical system.

### Confidence Validation

Confidence scores are LLM self-assessments, not validated against ground truth. Without a feedback loop where clinicians verify extractions, we can't measure actual accuracy or calibrate the confidence scores. This is a critical gap for production use.

---

## 5. Demo Summary and Next Steps

### What's Demonstrated

The prototype includes 3 sample clinical documents across 2 patients with linked MRNs:

| Document | Patient | Type | Triage |
|----------|---------|------|--------|
| `discharge_summary_thompson.pdf` | Margaret Thompson (MRN-2024-0847) | Discharge Summary | Routine |
| `lab_report_martinez.pdf` | Carlos Martinez (MRN-2024-0562) | Lab Report | Normal |
| `physician_notes_thompson_day3.txt` | Margaret Thompson (MRN-2024-0847) | Physician Notes | Routine |

The demo shows the full workflow: upload → extract → triage → view in dashboard with structured data, AI summary, risk flags, and confidence scores. Patient profiles are auto-linked by MRN, showing a longitudinal view across document types.

### What Would Make It Production-Ready

| Enhancement | Why It Matters |
|-------------|----------------|
| **Fine-tune on real client documents** | Extraction accuracy depends on matching the client's specific document formats, templates, and terminology. Few-shot examples from actual clinical notes would significantly improve reliability. |
| **Replace SQLite with PostgreSQL** | SQLite doesn't support concurrent writes. A production system needs a proper database for multiple simultaneous users and data integrity. |
| **WebSocket for real-time updates** | Polling every 10 seconds works for a prototype but is inefficient. WebSocket or Server-Sent Events would provide instant status updates. |
| **Batch processing** | Staff may need to ingest dozens of documents at once (e.g., importing a patient's full history). Bulk upload with progress tracking is essential. |
| **Clinician review interface** | Allow staff to verify, correct, and annotate extracted data. This creates a feedback loop that improves extraction accuracy over time and builds trust in the system. |
| **HIPAA compliance** | Encryption at rest and in transit, audit logging, role-based access control, BAA with LLM provider, data retention policies. |
| **EHR integration** | Connect with existing Electronic Health Record systems via FHIR/HL7 standards so extracted data flows directly into the patient's record. |
| **Multi-document comparison** | Compare lab results across visits, track medication changes, identify trends — turning isolated documents into a longitudinal clinical narrative. |
