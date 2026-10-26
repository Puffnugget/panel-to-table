"""Read lab PDFs in memory and return candidate values. Nothing is analyzed here."""

import io
import re
from typing import Optional

import pdfplumber

from markers import BY_ID, MARKER_ORDER, MARKERS

UNREADABLE = "We couldn't read this one; enter the values by hand."

_ALIAS_PAIRS = sorted(
    ((alias.lower(), marker["id"]) for marker in MARKERS for alias in marker["aliases"]),
    key=lambda pair: len(pair[0]),
    reverse=True,
)

_UNITS = [
    ("mmol/mol", r"mmol\s*/\s*mol"),
    ("mmol/L", r"mmol\s*/\s*l"),
    ("nmol/L", r"nmol\s*/\s*l"),
    ("pmol/L", r"pmol\s*/\s*l"),
    ("mg/dL", r"mg\s*/\s*dl"),
    ("ng/mL", r"ng\s*/\s*ml"),
    ("pg/mL", r"pg\s*/\s*ml"),
    ("mcg/L", r"mcg\s*/\s*l"),
    ("%", r"%"),
]


def parse_pdf_bytes(data: bytes) -> dict:
    try:
        text = _extract_text(data)
    except Exception:
        return _fail()
    if not text.strip():
        return _fail()
    candidates = _candidates_from_text(text)
    if not candidates:
        return _fail()
    found = {item["id"] for item in candidates}
    return {
        "ok": True,
        "message": "Check these numbers before analyzing. The PDF is not saved.",
        "candidates": candidates,
        "missing": [marker_id for marker_id in MARKER_ORDER if marker_id not in found],
    }


def _extract_text(data: bytes) -> str:
    pages = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    return "\n".join(pages)


def _fail() -> dict:
    return {"ok": False, "message": UNREADABLE, "candidates": [], "missing": list(MARKER_ORDER)}


def _candidates_from_text(text: str) -> list[dict]:
    found = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        matched = _match_line(line)
        if not matched or matched["id"] in found:
            continue
        found[matched["id"]] = matched
    return [found[marker_id] for marker_id in MARKER_ORDER if marker_id in found]


def _match_line(line: str) -> Optional[dict]:
    lowered = line.lower()
    for alias, marker_id in _ALIAS_PAIRS:
        if marker_id == "hdl" and re.search(r"non[-\s]?hdl", lowered):
            continue
        match = re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", lowered)
        if not match:
            continue
        return _read_rest(marker_id, line, line[match.end() :])
    return None


def _read_rest(marker_id: str, line: str, rest: str) -> Optional[dict]:
    number = re.search(r"\d+(?:\.\d+)?", rest)
    if not number:
        return None
    value = float(number.group(0))
    unit, unit_found = _unit_in(rest, marker_id)
    lab_low, lab_high = _range_in(rest[number.end() :])
    marker = BY_ID[marker_id]
    return {
        "id": marker_id,
        "name": marker["name"],
        "value": value,
        "unit": unit,
        "unit_found": unit_found,
        "lab_low": lab_low,
        "lab_high": lab_high,
        "source_line": line.strip(),
    }


def _unit_in(text: str, marker_id: str) -> tuple[str, bool]:
    marker = BY_ID[marker_id]
    lowered = text.lower()
    for unit, pattern in _UNITS:
        if unit not in marker["units"]:
            continue
        if re.search(pattern, lowered):
            return unit, True
    return marker["canonical_unit"], False


def _range_in(text: str) -> tuple[Optional[float], Optional[float]]:
    match = re.search(r"(\d+(?:\.\d+)?)\s*[-–—]\s*(\d+(?:\.\d+)?)", text)
    if not match:
        return None, None
    return float(match.group(1)), float(match.group(2))
