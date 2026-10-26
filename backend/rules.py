"""Classify marker values and pick food and activity tips.

The app never diagnoses. A see-a-doctor result gets a callout and no food tips.
"""

import math
from typing import Any, Optional

from markers import BY_ID, MARKER_ORDER, group_name
from recipes import plan_meals, select_recipes

TIPS = {
    "ldl": {
        "high": {
            "foods": ["oats", "beans", "lentils", "olive oil", "nuts", "fish"],
            "tip": "Oats, beans, and lentils are the usual picks. Olive oil, nuts, and fish can stand in for butter and fried food.",
        }
    },
    "hdl": {
        "low": {
            "foods": ["fatty fish"],
            "tip": "Regular aerobic activity helps. Fewer sugary drinks and refined carbs, and fatty fish a couple of times a week, are the usual suggestions.",
        }
    },
    "triglycerides": {
        "high": {
            "foods": ["fatty fish"],
            "tip": "Regular aerobic activity helps. Fewer sugary drinks and refined carbs, and fatty fish a couple of times a week, are the usual suggestions.",
        }
    },
    "glucose": {
        "high": {
            "foods": ["whole grains", "beans", "vegetables"],
            "tip": "Choose whole grains more often than refined ones. Pair carbs with fiber and protein, and cut back on sugary drinks.",
        }
    },
    "a1c": {
        "high": {
            "foods": ["whole grains", "beans", "vegetables"],
            "tip": "Choose whole grains more often than refined ones. Pair carbs with fiber and protein, and cut back on sugary drinks.",
        }
    },
    "vitamin_d": {
        "low": {
            "foods": ["salmon", "trout", "fortified milk", "eggs"],
            "tip": "Salmon, trout, fortified milk or plant milk, and eggs show up often. Supplements only if a doctor suggests them.",
        }
    },
    "ferritin": {
        "low": {
            "foods": ["lentils", "lean beef", "fortified cereal", "beans", "tofu"],
            "tip": "Eat a vitamin C food at the same meal.",
        }
    },
    "b12": {
        "low": {
            "foods": ["fish", "meat", "eggs", "dairy", "fortified cereal", "nutritional yeast"],
            "tip": "Fish, meat, eggs, and dairy are common sources. Fortified cereal or nutritional yeast helps if you don't eat animal foods.",
        }
    },
}

FOCUS_BY_MARKER = {
    "ldl": "heart",
    "hdl": "heart",
    "triglycerides": "heart",
    "glucose": "blood_sugar",
    "a1c": "blood_sugar",
    "vitamin_d": "vitamin_d",
    "ferritin": "iron_b12",
    "b12": "iron_b12",
}
FOCUS_ORDER = ["heart", "blood_sugar", "iron_b12", "vitamin_d"]
TIP_TIERS = {"borderline", "out_of_range"}


def convert_value(marker_id: str, value: float, unit: str) -> float:
    marker = BY_ID[marker_id]
    if unit not in marker["units"]:
        raise ValueError(f"{marker['name']} does not use the unit {unit}.")
    if unit == marker["canonical_unit"]:
        return float(value)
    spec = marker["conversions"][unit]
    converted = float(value)
    if "multiply" in spec:
        converted *= spec["multiply"]
    if "divide" in spec:
        converted /= spec["divide"]
    if "add" in spec:
        converted += spec["add"]
    return converted


def _in_band(value: float, band: dict) -> bool:
    low = band.get("low")
    high = band.get("high")
    if low is not None:
        if band.get("low_inclusive", True):
            if value < low:
                return False
        elif value <= low:
            return False
    if high is not None:
        if band.get("high_inclusive", False):
            if value > high:
                return False
        elif value >= high:
            return False
    return True


def _table_hit(marker_id: str, value: float, age: int, sex: str) -> dict:
    marker = BY_ID[marker_id]
    if marker.get("ferritin"):
        return {"tier": "in_range", "direction": None, "note": None}
    bands = marker["groups"][group_name(marker_id, age, sex)]
    for band in bands:
        if _in_band(value, band):
            return {
                "tier": band["tier"],
                "direction": band.get("direction"),
                "note": band.get("note"),
            }
    raise ValueError(f"No range matched {marker['name']}.")


def _validate_possible(marker: dict, value: float) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{marker['name']} is outside a possible human range, so nothing was analyzed.")
    low, high = marker["plausible"]
    if value < low or value > high:
        raise ValueError(
            f"{marker['name']} is outside a possible human range, so nothing was analyzed."
        )


def _tips_for(marker_id: str, tier: str, direction: Optional[str]) -> tuple[list[str], Optional[str]]:
    if tier not in TIP_TIERS or not direction:
        return [], None
    # High ferritin and high vitamin D never get food ideas, even below the see-a-doctor line.
    if marker_id == "ferritin" and direction == "high":
        return [], None
    if marker_id == "vitamin_d" and direction == "high":
        return [], None
    advice = TIPS.get(marker_id, {}).get(direction)
    if not advice:
        return [], None
    return list(advice["foods"]), advice["tip"]


def _message(marker: dict, tier: str, direction: Optional[str], note: Optional[str], range_source: str) -> str:
    name = marker["name"]
    if tier == "unrated":
        return "No status for this one. The usual ranges assume a fasting test."
    if tier == "see_doctor":
        if marker["id"] == "vitamin_d" and direction == "high":
            return "Vitamin D over 50 ng/mL is high enough to ask a doctor about. Vitamin D food tips are turned off."
        if marker["id"] == "ferritin" and direction == "high":
            return "This is above the lab's range. A doctor should sort out why. Iron-rich food tips are turned off."
        if marker["id"] == "glucose" and direction == "low":
            return "Fasting glucose under 70 is low enough to ask a doctor about. Food tips are turned off for this marker."
        if marker["id"] == "glucose" and direction == "high":
            return "Fasting glucose at or above 126 is high enough for a doctor, not this app, to interpret. Food tips are turned off."
        if marker["id"] == "a1c":
            return "A1c at or above 6.5 is in the range clinicians discuss with patients. See a doctor. Food tips are turned off for this marker."
        if marker["id"] == "triglycerides":
            return "Triglycerides at or above 500 need a doctor. Food tips are turned off for this marker."
        if marker["id"] == "ldl":
            return "LDL at or above 190 mg/dL should be seen by a doctor before any food changes based on it."
        return f"{name} is far enough from the usual range that a doctor should see it. Food tips are turned off for this marker."
    if range_source == "lab" and tier == "in_range":
        return "Inside the range printed on the lab report. Keep it up."
    if range_source == "lab" and tier == "out_of_range":
        side = "below" if direction == "low" else "above"
        return f"{side.capitalize()} your lab's range. Bring this up at your next checkup."
    if tier == "in_range" and note == "near_optimal":
        return "Near the optimal zone. Under 100 mg/dL is the usual LDL goal. Keep it up."
    if tier == "in_range":
        if marker["id"] == "ferritin" and range_source == "ferritin_30":
            return "At or above 30 ng/mL. Without your lab's own range, a high value is not flagged here."
        return "In the usual range. Keep it up."
    if tier == "borderline":
        if marker["id"] == "vitamin_d":
            return "In the inadequate band (12–19 ng/mL). Food ideas are below. This is not a diagnosis."
        if marker["id"] == "b12":
            return "In the marginal band (200–299 pg/mL). Food ideas are below. This is not a diagnosis."
        return "In the borderline band. Food ideas are below. This is not a diagnosis."
    if marker["id"] == "ferritin" and range_source == "ferritin_30":
        return "Under 30 ng/mL often suggests low iron stores. Bring this up at your next checkup."
    if note == "prediabetes":
        return "In the prediabetes range used by the ADA. Bring this up at your next checkup. This app is not diagnosing diabetes."
    return "Outside the usual range. Bring this up at your next checkup."


def _band_edges(band: dict, scale_min: float, scale_max: float) -> tuple[float, float]:
    start = scale_min if band.get("low") is None else band["low"]
    end = scale_max if band.get("high") is None else band["high"]
    if band.get("low_inclusive") is False and band.get("low") is not None:
        start = band["low"]
    return start, end


def _zones_from_bands(bands: list[dict], scale_min: float, scale_max: float) -> list[dict]:
    zones = []
    for band in bands:
        start, end = _band_edges(band, scale_min, scale_max)
        start = max(scale_min, start)
        end = min(scale_max, end)
        if end <= start:
            continue
        zones.append({"start": start, "end": end, "tier": band["tier"]})
    return zones


def _normal_band(zones: list[dict], scale_min: float, scale_max: float) -> tuple[float, float]:
    in_range = [zone for zone in zones if zone["tier"] == "in_range"]
    if not in_range:
        return scale_min, scale_max
    return min(zone["start"] for zone in in_range), max(zone["end"] for zone in in_range)


def _expand_scale(scale_min: float, scale_max: float, *points: float) -> tuple[float, float]:
    nums = [point for point in points if point is not None]
    if not nums:
        return scale_min, scale_max
    low = min([scale_min, *nums])
    high = max([scale_max, *nums])
    if high == low:
        high = low + 1
    return low, high


def _bar(
    marker: dict,
    value: float,
    age: int,
    sex: str,
    lab_low: Optional[float],
    lab_high: Optional[float],
    use_lab: bool,
) -> dict:
    scale_min, scale_max = marker["scale"]
    scale_min, scale_max = _expand_scale(scale_min, scale_max, value, lab_low, lab_high)
    if marker.get("ferritin"):
        zones, band_low, band_high = _ferritin_zones(value, lab_low, lab_high, scale_min, scale_max)
    elif use_lab and (lab_low is not None or lab_high is not None):
        zones, band_low, band_high = _lab_zones(marker, age, sex, lab_low, lab_high, scale_min, scale_max)
    else:
        bands = marker["groups"][group_name(marker["id"], age, sex)]
        zones = _zones_from_bands(bands, scale_min, scale_max)
        band_low, band_high = _normal_band(zones, scale_min, scale_max)
    return {
        "min": scale_min,
        "max": scale_max,
        "value": value,
        "zones": zones,
        "band_low": band_low,
        "band_high": band_high,
    }


def _see_doctor_edges(marker: dict, age: int, sex: str) -> list[dict]:
    if marker.get("ferritin") or not marker["groups"]:
        return []
    bands = marker["groups"][group_name(marker["id"], age, sex)]
    return [band for band in bands if band["tier"] == "see_doctor"]


def _lab_zones(marker, age, sex, lab_low, lab_high, scale_min, scale_max):
    zones = [{"start": scale_min, "end": scale_max, "tier": "in_range"}]
    if lab_low is not None and lab_low > scale_min:
        zones = [
            {"start": scale_min, "end": lab_low, "tier": "out_of_range"},
            {"start": lab_low, "end": scale_max, "tier": "in_range"},
        ]
    if lab_high is not None and lab_high < scale_max:
        rebuilt = []
        for zone in zones:
            if zone["end"] <= lab_high or zone["start"] >= lab_high:
                if zone["start"] >= lab_high:
                    rebuilt.append({**zone, "tier": "out_of_range"})
                else:
                    rebuilt.append(zone)
                continue
            rebuilt.append({**zone, "end": lab_high})
            rebuilt.append({"start": lab_high, "end": zone["end"], "tier": "out_of_range"})
        zones = rebuilt
    for band in _see_doctor_edges(marker, age, sex):
        start, end = _band_edges(band, scale_min, scale_max)
        zones = _paint(zones, start, end, "see_doctor")
    band_low = lab_low if lab_low is not None else scale_min
    band_high = lab_high if lab_high is not None else scale_max
    return zones, band_low, band_high


def _paint(zones: list[dict], start: float, end: float, tier: str) -> list[dict]:
    if end <= start:
        return zones
    painted = []
    for zone in zones:
        if zone["end"] <= start or zone["start"] >= end:
            painted.append(zone)
            continue
        if zone["start"] < start:
            painted.append({**zone, "end": start})
        painted.append({"start": max(zone["start"], start), "end": min(zone["end"], end), "tier": tier})
        if zone["end"] > end:
            painted.append({**zone, "start": end})
    return [zone for zone in painted if zone["end"] > zone["start"]]


def _ferritin_zones(value, lab_low, lab_high, scale_min, scale_max):
    if lab_low is None and lab_high is None:
        zones = [
            {"start": scale_min, "end": min(30, scale_max), "tier": "out_of_range"},
            {"start": min(30, scale_max), "end": scale_max, "tier": "in_range"},
        ]
        return zones, 30, scale_max
    zones, band_low, band_high = _lab_zones(
        {"id": "ferritin", "ferritin": True, "groups": {}},
        30,
        "female",
        lab_low,
        lab_high,
        scale_min,
        scale_max,
    )
    if lab_high is not None:
        zones = _paint(zones, lab_high, scale_max, "see_doctor")
    return zones, band_low, band_high


def _classify_ferritin(value: float, lab_low: Optional[float], lab_high: Optional[float]) -> dict:
    if lab_high is not None and value > lab_high:
        return {"tier": "see_doctor", "direction": "high", "note": None, "range_source": "lab"}
    if lab_low is not None and value < lab_low:
        return {"tier": "out_of_range", "direction": "low", "note": None, "range_source": "lab"}
    if lab_low is None and lab_high is None:
        if value < 30:
            return {"tier": "out_of_range", "direction": "low", "note": None, "range_source": "ferritin_30"}
        return {"tier": "in_range", "direction": None, "note": None, "range_source": "ferritin_30"}
    if lab_low is None and value < 30:
        return {"tier": "out_of_range", "direction": "low", "note": None, "range_source": "ferritin_30"}
    return {"tier": "in_range", "direction": None, "note": None, "range_source": "lab"}


def classify_marker(
    marker_id: str,
    raw_value: float,
    unit: str,
    age: int,
    sex: str,
    fasting: bool,
    lab_low: Optional[float] = None,
    lab_high: Optional[float] = None,
) -> dict[str, Any]:
    marker = BY_ID[marker_id]
    canonical = convert_value(marker_id, raw_value, unit)
    _validate_possible(marker, canonical)
    canonical_low = convert_value(marker_id, lab_low, unit) if lab_low is not None else None
    canonical_high = convert_value(marker_id, lab_high, unit) if lab_high is not None else None
    if canonical_low is not None and canonical_high is not None and canonical_low > canonical_high:
        raise ValueError(f"{marker['name']} has a lab range that runs backwards.")

    if marker.get("fasting_required") and not fasting:
        hit = {
            "tier": "unrated",
            "direction": None,
            "note": None,
            "range_source": "fasting_required",
        }
        foods, tip = [], None
    elif marker.get("ferritin"):
        hit = _classify_ferritin(canonical, canonical_low, canonical_high)
        foods, tip = _tips_for(marker_id, hit["tier"], hit["direction"])
    else:
        table = _table_hit(marker_id, canonical, age, sex)
        range_source = "table"
        tier = table["tier"]
        direction = table["direction"]
        note = table["note"]
        use_lab = canonical_low is not None or canonical_high is not None
        if tier != "see_doctor" and use_lab:
            range_source = "lab"
            if canonical_low is not None and canonical < canonical_low:
                tier, direction, note = "out_of_range", "low", None
            elif canonical_high is not None and canonical > canonical_high:
                tier, direction, note = "out_of_range", "high", None
            else:
                tier, direction, note = "in_range", None, None
        hit = {"tier": tier, "direction": direction, "note": note, "range_source": range_source}
        foods, tip = _tips_for(marker_id, tier, direction)

    use_lab = hit["range_source"] == "lab"
    return {
        "id": marker_id,
        "name": marker["name"],
        "value": round(canonical, 2),
        "unit": marker["canonical_unit"],
        "entered_value": raw_value,
        "entered_unit": unit,
        "tier": hit["tier"],
        "direction": hit["direction"],
        "message": _message(marker, hit["tier"], hit["direction"], hit["note"], hit["range_source"]),
        "foods": foods,
        "tip": tip,
        "bar": _bar(marker, canonical, age, sex, canonical_low, canonical_high, use_lab),
    }


def _activity(age: int, results: list[dict]) -> str:
    if age < 20:
        text = "Aim for 60 minutes of activity a day."
    else:
        text = "Aim for at least 150 minutes of moderate activity a week."
    heart_habit = any(
        item["id"] in {"hdl", "triglycerides"} and item["tier"] in TIP_TIERS
        for item in results
    )
    if heart_habit:
        text += " Regular aerobic activity, such as brisk walking, is one of the habits suggested when HDL is low or triglycerides are high."
    return text


def _focus(results: list[dict]) -> list[str]:
    found = []
    for item in results:
        if item["tier"] not in TIP_TIERS:
            continue
        if item["id"] in {"ferritin", "vitamin_d"} and item["direction"] != "low":
            continue
        if item["id"] == "b12" and item["direction"] != "low":
            continue
        label = FOCUS_BY_MARKER[item["id"]]
        if label not in found:
            found.append(label)
    found.sort(key=lambda label: FOCUS_ORDER.index(label))
    return found or ["balanced"]


def analyze_payload(payload: dict) -> dict:
    age = payload["age"]
    sex = payload["sex"]
    fasting = payload["fasting"]
    markers = payload["markers"]
    if not markers:
        raise ValueError("Enter at least one marker.")
    seen = set()
    classified = []
    for item in markers:
        marker_id = item["id"]
        if marker_id not in BY_ID:
            raise ValueError(f"Unknown marker: {marker_id}.")
        if marker_id in seen:
            raise ValueError(f"{BY_ID[marker_id]['name']} was entered twice.")
        seen.add(marker_id)
        classified.append(
            classify_marker(
                marker_id,
                item["value"],
                item["unit"],
                age,
                sex,
                fasting,
                item.get("lab_low"),
                item.get("lab_high"),
            )
        )
    classified.sort(key=lambda item: MARKER_ORDER.index(item["id"]))
    see_doctor = [item["id"] for item in classified if item["tier"] == "see_doctor"]
    focus = _focus(classified)
    return {
        "see_doctor": see_doctor,
        "results": classified,
        "focus": focus,
        "activity": _activity(age, classified),
        "recipes": select_recipes(classified),
        "meals": plan_meals(classified),
    }

