import pytest

from backend.app.services.extraction import apply_triage_rules


class TestTriageRules:
    def test_critical_keyword(self):
        text = "Patient presents with STAT order for cardiac arrest"
        labs = []
        level, reasons = apply_triage_rules(text, labs)
        assert level == "critical"
        assert any("cardiac arrest" in r.lower() for r in reasons)

    def test_critical_lab_value(self):
        text = "Lab results reviewed"
        labs = [{"test_name": "Glucose", "value": "550", "flag": "critical_high"}]
        level, reasons = apply_triage_rules(text, labs)
        assert level == "critical"
        assert any("Glucose" in r for r in reasons)

    def test_high_keyword(self):
        text = "Results show elevated glucose levels, requires follow-up"
        labs = []
        level, reasons = apply_triage_rules(text, labs)
        assert level == "high"

    def test_normal(self):
        text = "Patient is stable, routine follow-up in 2 weeks"
        labs = []
        level, reasons = apply_triage_rules(text, labs)
        assert level == "normal"

    def test_abnormal_lab_not_critical(self):
        text = "Lab results reviewed"
        labs = [{"test_name": "WBC", "value": "15.0", "flag": "abnormal_high"}]
        level, reasons = apply_triage_rules(text, labs)
        assert level in ("normal", "high")
