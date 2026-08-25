# Clinical Document Intelligence Hub

## Approach
This prototype demonstrates how AI can transform fragmented healthcare data into structured, decision-ready outputs. It accepts clinical documents in multiple formats (PDF, DOCX, TXT, images), extracts structured clinical data using LLMs, and presents actionable intelligence through a web interface.

## AI Models & Tools
- **LLM Provider**: OpenRouter (free tier) — auto-routes to best available free model
- **Primary Models**: Nemotron 3 Ultra, Gemma 4, Llama 4 Scout (via OpenRouter free routing)
- **PDF Parsing**: PyMuPDF (fitz)
- **DOCX Parsing**: python-docx
- **OCR**: Tesseract (fallback for image-based documents)
- **Backend**: Python 3.11 + FastAPI + SQLAlchemy + SQLite
- **Frontend**: React 18 + Vite + Tailwind CSS

## Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- OpenRouter API key (free at https://openrouter.ai)

### 1. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env
# Edit .env and add your OPENROUTER_API_KEY
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Docker (alternative)
```bash
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
docker compose up --build
```

## API Endpoints
- `POST /documents/upload` — Upload a clinical document
- `GET /documents` — List all documents (supports filters: status, triage, doc_type, patient_mrn)
- `GET /documents/{id}` — Get document with full extraction
- `DELETE /documents/{id}` — Delete a document
- `POST /documents/{id}/reprocess` — Re-run extraction
- `GET /search?q=` — Full-text search across documents
- `GET /patients` — List patient profiles
- `GET /patients/{mrn}` — Get patient profile
- `GET /patients/{mrn}/documents` — Get all documents for a patient
- `GET /patients/{mrn}/timeline` — Patient document timeline
- `GET /health` — Health check

## Architecture
```
React Frontend (port 3000)
    ↕ REST API
FastAPI Backend (port 8000)
    ├── Document Parser (PDF/DOCX/TXT/Image)
    ├── LLM Service (OpenRouter)
    │   ├── Structured Extraction (JSON)
    │   ├── Clinical Summarization
    │   └── Triage Classification
    ├── Triage Rules Engine (keyword + threshold)
    └── Patient Linking (MRN-based)
    ↕
SQLite Database
```

## Sample Data
Run `python scripts/generate_samples.py` to create synthetic clinical documents in `samples/`.

## Limitations
- Free OpenRouter models have rate limits (~20 req/min, daily caps)
- OCR quality depends on document image quality
- Triage rules are simplified — not a substitute for clinical judgment
- No authentication/authorization (prototype only)
- No HIPAA compliance measures (prototype only)

## Future Improvements
- Add user authentication and role-based access
- Implement HIPAA-compliant audit logging
- Add batch processing for bulk document ingestion
- Integrate with EHR systems via HL7 FHIR
- Add document comparison and trend analysis
- Implement feedback loop to improve extraction accuracy
