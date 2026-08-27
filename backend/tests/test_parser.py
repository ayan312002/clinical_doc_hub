import pytest
from pathlib import Path

from backend.app.services.parser import parse_pdf, parse_txt, detect_doc_type

SAMPLES_DIR = Path(__file__).parent.parent.parent / "samples"


class TestParsePdf:
    def test_parse_discharge_summary(self):
        pdf_path = SAMPLES_DIR / "discharge_summary_thompson.pdf"
        if not pdf_path.exists():
            pytest.skip("Sample file not found")
        text = parse_pdf(str(pdf_path))
        assert len(text) > 100
        assert "Margaret Thompson" in text
        assert "MRN-2024-0847" in text

    def test_parse_lab_report(self):
        pdf_path = SAMPLES_DIR / "lab_report_martinez.pdf"
        if not pdf_path.exists():
            pytest.skip("Sample file not found")
        text = parse_pdf(str(pdf_path))
        assert len(text) > 100
        assert "Robert Martinez" in text
        assert "Glucose" in text


class TestParseTxt:
    def test_parse_physician_notes(self):
        txt_path = SAMPLES_DIR / "physician_notes_thompson_day3.txt"
        if not txt_path.exists():
            pytest.skip("Sample file not found")
        text = parse_txt(str(txt_path))
        assert len(text) > 100
        assert "Margaret Thompson" in text


class TestDetectDocType:
    def test_discharge_summary(self):
        text = "DISCHARGE SUMMARY\nPatient: John Doe\nAdmission Date: 2026-01-01"
        assert detect_doc_type(text, "discharge.pdf") == "discharge_summary"

    def test_lab_report(self):
        text = "Lab Results\nGlucose: 120 mg/dL\nReference Range: 70-100"
        assert detect_doc_type(text, "labs.pdf") == "lab_report"

    def test_physician_notes(self):
        text = "Chief Complaint: Headache\nHistory of Present Illness: Patient reports..."
        assert detect_doc_type(text, "notes.txt") == "physician_notes"

    def test_intake_form(self):
        text = "Vital Signs:\nBlood Pressure: 120/80\nHeart Rate: 72"
        assert detect_doc_type(text, "intake.pdf") == "intake_form"

    def test_unknown(self):
        text = "Some random text with no medical keywords"
        assert detect_doc_type(text, "unknown.pdf") == "unknown"
