
from PyPDF2 import PdfReader
import re
from typing import Dict, Tuple

# Simple regex-based marker extraction
MARKERS = {
    "Hemoglobin": r"(Hemoglobin|Hb)\s*[:\-]?\s*(\d+(\.\d+)?)",
    "RBC": r"(RBC|Red Blood Cells)\s*[:\-]?\s*(\d+(\.\d+)?)",
    "WBC": r"(WBC|White Blood Cells|Leukocytes)\s*[:\-]?\s*(\d+(\.\d+)?)",
    "Platelets": r"(Platelets|PLT)\s*[:\-]?\s*(\d+(\.\d+)?)",
    "Hematocrit": r"(Hematocrit|HCT)\s*[:\-]?\s*(\d+(\.\d+)?)",
}

def extract_text_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    text = []
    for page in reader.pages:
        text.append(page.extract_text() or "")
    return "\n".join(text)

def parse_markers(text: str) -> Dict[str, float]:
    found = {}
    for name, pattern in MARKERS.items():
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if m:
            try:
                found[name] = float(m.group(2))
            except:
                continue
    return found

def analyze_markers(markers: Dict[str, float]) -> Tuple[str, Dict[str, float]]:
    assessments = []
    # naive ranges for demo purposes (not medical advice)
    ranges = {
        "Hemoglobin": (12.0, 17.5),
        "RBC": (4.2, 6.1),
        "WBC": (4.0, 11.0),
        "Platelets": (150.0, 450.0),
        "Hematocrit": (36.0, 50.0),
    }
    for k, v in markers.items():
        if k in ranges:
            lo, hi = ranges[k]
            if v < lo:
                assessments.append(f"{k} is low ({v}); consider evaluation for deficiency or anemia.")
            elif v > hi:
                assessments.append(f"{k} is high ({v}); consider clinical correlation.")
            else:
                assessments.append(f"{k} is within the typical range ({v}).")
        else:
            assessments.append(f"{k}: {v}")
    if not assessments:
        summary = "No common CBC markers detected in the document."
    else:
        summary = " | ".join(assessments)
    return summary, markers
