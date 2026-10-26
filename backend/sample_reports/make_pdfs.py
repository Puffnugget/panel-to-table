"""Build synthetic lab PDFs. Values are made up. They are not a real person's results."""

from pathlib import Path

from fpdf import FPDF

HERE = Path(__file__).resolve().parent


def _write(path: Path, lines: list[str]) -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=14)
    pdf.cell(0, 10, "Example lab report - not a real patient", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=12)
    for line in lines:
        pdf.cell(0, 8, line, new_x="LMARGIN", new_y="NEXT")
    pdf.output(path)


def build(folder: Path = HERE) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    _write(
        folder / "example-standard.pdf",
        [
            "LDL Cholesterol 142 mg/dL Reference 0-99",
            "HDL Cholesterol 46 mg/dL",
            "Triglycerides 160 mg/dL",
            "Fasting Glucose 104 mg/dL",
            "Hemoglobin A1c 5.8 %",
            "Vitamin D, 25-Hydroxy 16 ng/mL",
            "Ferritin 18 ng/mL 13-150",
            "Vitamin B12 420 pg/mL",
        ],
    )
    _write(
        folder / "example-si-units.pdf",
        [
            "LDL Cholesterol 3.2 mmol/L",
            "HDL Cholesterol 1.4 mmol/L",
            "Triglycerides 1.8 mmol/L",
            "Glucose 5.4 mmol/L",
            "Hemoglobin A1c 36 mmol/mol",
            "Vitamin D 75 nmol/L",
            "Ferritin 40 mcg/L 15-150",
            "Vitamin B12 300 pmol/L",
        ],
    )
    blank = FPDF()
    blank.add_page()
    blank.output(folder / "example-unreadable.pdf")


if __name__ == "__main__":
    build()
