import base64
from pathlib import Path

import fitz  # PyMuPDF

try:
    import docx
except ImportError:
    docx = None

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}


def parse_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    return "\n".join(text_parts).strip()


def parse_docx(file_path: str) -> str:
    if docx is None:
        raise ImportError("python-docx not installed")
    document = docx.Document(file_path)
    return "\n".join(p.text for p in document.paragraphs).strip()


def parse_txt(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8", errors="replace").strip()


def parse_image(file_path: str) -> str:
    if pytesseract is None or Image is None:
        raise ImportError("pytesseract and Pillow required for OCR")
    img = Image.open(file_path)
    return pytesseract.image_to_string(img).strip()


def image_to_base64(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def parse_document(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return parse_pdf(file_path)
    elif ext in (".docx", ".doc"):
        return parse_docx(file_path)
    elif ext in (".txt", ".md"):
        return parse_txt(file_path)
    elif ext in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
        return parse_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def detect_doc_type(text: str, filename: str) -> str:
    lower_text = text.lower()
    lower_name = filename.lower()

    if any(k in lower_name for k in ["discharge", "summary"]):
        return "discharge_summary"
    if any(k in lower_name for k in ["lab", "result", "blood"]):
        return "lab_report"
    if any(k in lower_name for k in ["intake", "admission", "registration"]):
        return "intake_form"
    if any(k in lower_name for k in ["note", "progress", "hpi"]):
        return "physician_notes"
    if any(k in lower_name for k in ["imaging", "xray", "mri", "ct"]):
        return "imaging_report"
    if any(k in lower_name for k in ["medication", "med list", "prescription"]):
        return "medication_list"

    if "discharge" in lower_text[:500]:
        return "discharge_summary"
    if "lab result" in lower_text[:500] or "reference range" in lower_text[:1000]:
        return "lab_report"
    if "chief complaint" in lower_text[:500] or "history of present" in lower_text[:500]:
        return "physician_notes"
    if "vital signs" in lower_text[:500] or "blood pressure" in lower_text[:500]:
        return "intake_form"

    return "unknown"
