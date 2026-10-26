"""Marker table for the blood-test rebuild.

Ranges are the starting points from the blood-test plan. Adult lipids follow
NCEP ATP III cut points. Under-20 lipids follow the NHLBI 10–19 column.
The see-a-doctor cutoffs apply on top of any range printed by a lab.
"""

MARKERS = [
    {
        "id": "ldl",
        "name": "LDL cholesterol",
        "canonical_unit": "mg/dL",
        "units": ["mg/dL", "mmol/L"],
        "conversions": {"mmol/L": {"multiply": 38.6}},
        "aliases": ["ldl cholesterol", "ldl-c", "ldl"],
        "plausible": (1, 700),
        "scale": (0, 250),
        "groups": {
            "adult": [
                {"high": 100, "tier": "in_range", "note": "optimal"},
                {"low": 100, "high": 130, "tier": "in_range", "note": "near_optimal"},
                {"low": 130, "high": 160, "tier": "borderline", "direction": "high"},
                {"low": 160, "high": 190, "tier": "out_of_range", "direction": "high"},
                {"low": 190, "tier": "see_doctor", "direction": "high"},
            ],
            "youth": [
                {"high": 110, "tier": "in_range"},
                {"low": 110, "high": 130, "tier": "borderline", "direction": "high"},
                {"low": 130, "high": 190, "tier": "out_of_range", "direction": "high"},
                {"low": 190, "tier": "see_doctor", "direction": "high"},
            ],
        },
    },
    {
        "id": "hdl",
        "name": "HDL cholesterol",
        "canonical_unit": "mg/dL",
        "units": ["mg/dL", "mmol/L"],
        "conversions": {"mmol/L": {"multiply": 38.6}},
        "aliases": ["hdl cholesterol", "hdl-c", "hdl"],
        "plausible": (1, 200),
        "scale": (0, 100),
        "groups": {
            "adult_male": [
                {"high": 40, "tier": "out_of_range", "direction": "low"},
                {"low": 40, "tier": "in_range"},
            ],
            "adult_female": [
                {"high": 50, "tier": "out_of_range", "direction": "low"},
                {"low": 50, "tier": "in_range"},
            ],
            # Over 45 is the usual youth band. 40 through 45 is borderline.
            "youth": [
                {"high": 40, "tier": "out_of_range", "direction": "low"},
                {"low": 40, "high": 45, "high_inclusive": True, "tier": "borderline", "direction": "low"},
                {"low": 45, "low_inclusive": False, "tier": "in_range"},
            ],
        },
    },
    {
        "id": "triglycerides",
        "name": "Triglycerides",
        "canonical_unit": "mg/dL",
        "units": ["mg/dL", "mmol/L"],
        "conversions": {"mmol/L": {"multiply": 88.6}},
        "aliases": ["triglycerides", "triglyceride"],
        "plausible": (1, 5000),
        "scale": (0, 600),
        "fasting_required": True,
        "groups": {
            "adult": [
                {"high": 150, "tier": "in_range"},
                {"low": 150, "high": 200, "tier": "borderline", "direction": "high"},
                {"low": 200, "high": 500, "tier": "out_of_range", "direction": "high"},
                {"low": 500, "tier": "see_doctor", "direction": "high"},
            ],
            "youth": [
                {"high": 90, "tier": "in_range"},
                {"low": 90, "high": 130, "tier": "borderline", "direction": "high"},
                {"low": 130, "high": 500, "tier": "out_of_range", "direction": "high"},
                {"low": 500, "tier": "see_doctor", "direction": "high"},
            ],
        },
    },
    {
        "id": "glucose",
        "name": "Fasting glucose",
        "canonical_unit": "mg/dL",
        "units": ["mg/dL", "mmol/L"],
        "conversions": {"mmol/L": {"multiply": 18}},
        "aliases": ["fasting glucose", "blood glucose", "glucose"],
        "plausible": (20, 700),
        "scale": (40, 220),
        "fasting_required": True,
        "groups": {
            "all": [
                {"high": 70, "tier": "see_doctor", "direction": "low"},
                {"low": 70, "high": 100, "tier": "in_range"},
                {"low": 100, "high": 126, "tier": "out_of_range", "direction": "high", "note": "prediabetes"},
                {"low": 126, "tier": "see_doctor", "direction": "high"},
            ],
        },
    },
    {
        "id": "a1c",
        "name": "Hemoglobin A1c",
        "canonical_unit": "%",
        "units": ["%", "mmol/mol"],
        "conversions": {"mmol/mol": {"multiply": 0.0915, "add": 2.15}},
        "aliases": ["hemoglobin a1c", "glycated hemoglobin", "hba1c", "a1c"],
        "plausible": (3, 20),
        "scale": (4, 10),
        "groups": {
            "all": [
                {"high": 5.7, "tier": "in_range"},
                {"low": 5.7, "high": 6.5, "tier": "out_of_range", "direction": "high", "note": "prediabetes"},
                {"low": 6.5, "tier": "see_doctor", "direction": "high"},
            ],
        },
    },
    {
        "id": "vitamin_d",
        "name": "Vitamin D (25-hydroxy)",
        "canonical_unit": "ng/mL",
        "units": ["ng/mL", "nmol/L"],
        "conversions": {"nmol/L": {"divide": 2.5}},
        "aliases": ["25-hydroxy vitamin d", "vitamin d, 25-hydroxy", "25-hydroxy", "vitamin d"],
        "plausible": (1, 200),
        "scale": (0, 80),
        "groups": {
            "all": [
                {"high": 12, "tier": "out_of_range", "direction": "low"},
                {"low": 12, "high": 20, "tier": "borderline", "direction": "low"},
                {"low": 20, "high": 50, "high_inclusive": True, "tier": "in_range"},
                {"low": 50, "low_inclusive": False, "tier": "see_doctor", "direction": "high"},
            ],
        },
    },
    {
        "id": "ferritin",
        "name": "Ferritin",
        "canonical_unit": "ng/mL",
        "units": ["ng/mL", "mcg/L"],
        "conversions": {"mcg/L": {"multiply": 1}},
        "aliases": ["ferritin"],
        "plausible": (1, 50000),
        "scale": (0, 400),
        "ferritin": True,
        "groups": {},
    },
    {
        "id": "b12",
        "name": "Vitamin B12",
        "canonical_unit": "pg/mL",
        "units": ["pg/mL", "pmol/L"],
        "conversions": {"pmol/L": {"divide": 0.74}},
        "aliases": ["vitamin b12", "cobalamin", "b12"],
        "plausible": (1, 20000),
        "scale": (0, 1000),
        "groups": {
            "all": [
                {"high": 200, "tier": "out_of_range", "direction": "low"},
                {"low": 200, "high": 300, "tier": "borderline", "direction": "low"},
                {"low": 300, "tier": "in_range"},
            ],
        },
    },
]

MARKER_ORDER = [marker["id"] for marker in MARKERS]
BY_ID = {marker["id"]: marker for marker in MARKERS}


def group_name(marker_id: str, age: int, sex: str) -> str:
    marker = BY_ID[marker_id]
    if "all" in marker["groups"]:
        return "all"
    if age < 20:
        return "youth"
    if marker_id == "hdl":
        return "adult_female" if sex == "female" else "adult_male"
    return "adult"
