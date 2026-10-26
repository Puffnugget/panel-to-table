from pathlib import Path

from fastapi.testclient import TestClient

from api import app
from parse_pdf import parse_pdf_bytes
from sample_reports.make_pdfs import build

ROOT = Path(__file__).resolve().parents[1]


def setup_module():
    build(ROOT / "sample_reports")


def test_standard_pdf_finds_values_without_analyzing():
    data = (ROOT / "sample_reports" / "example-standard.pdf").read_bytes()
    parsed = parse_pdf_bytes(data)
    assert parsed["ok"] is True
    by_id = {item["id"]: item for item in parsed["candidates"]}
    assert by_id["ldl"]["value"] == 142
    assert by_id["ldl"]["unit"] == "mg/dL"
    assert by_id["ldl"]["lab_high"] == 99
    assert by_id["glucose"]["value"] == 104
    assert by_id["a1c"]["value"] == 5.8
    assert by_id["a1c"]["unit"] == "%"
    assert by_id["vitamin_d"]["value"] == 16
    assert by_id["ferritin"]["lab_low"] == 13
    assert by_id["ferritin"]["lab_high"] == 150
    assert by_id["b12"]["value"] == 420
    assert "tier" not in by_id["ldl"]


def test_si_unit_pdf():
    data = (ROOT / "sample_reports" / "example-si-units.pdf").read_bytes()
    parsed = parse_pdf_bytes(data)
    by_id = {item["id"]: item for item in parsed["candidates"]}
    assert by_id["ldl"]["unit"] == "mmol/L"
    assert by_id["ldl"]["value"] == 3.2
    assert by_id["a1c"]["unit"] == "mmol/mol"
    assert by_id["vitamin_d"]["unit"] == "nmol/L"
    assert by_id["b12"]["unit"] == "pmol/L"
    assert by_id["ferritin"]["unit"] == "mcg/L"


def test_unreadable_pdf_asks_for_manual_entry():
    data = (ROOT / "sample_reports" / "example-unreadable.pdf").read_bytes()
    parsed = parse_pdf_bytes(data)
    assert parsed["ok"] is False
    assert parsed["candidates"] == []
    assert "enter the values by hand" in parsed["message"]


def test_parse_route_discards_non_pdf():
    client = TestClient(app)
    response = client.post("/parse-report", files={"file": ("notes.txt", b"LDL 100", "text/plain")})
    assert response.status_code == 200
    assert response.json()["ok"] is False


def test_analyze_route_uses_json_not_genome_text():
    client = TestClient(app)
    response = client.post(
        "/analyze",
        json={
            "age": 16,
            "sex": "female",
            "test_date": "2026-09-14",
            "fasting": True,
            "markers": [
                {"id": "ferritin", "value": 9, "unit": "ng/mL", "lab_low": 13, "lab_high": 150}
            ],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["results"][0]["tier"] == "out_of_range"
    assert "traits" not in body
    assert "scores" not in body


def test_health():
    client = TestClient(app)
    assert client.get("/health").json()["status"] == "healthy"
