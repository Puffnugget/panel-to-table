from rules import analyze_payload


def analyze(markers, age=40, sex="male", fasting=True):
    return analyze_payload(
        {
            "age": age,
            "sex": sex,
            "test_date": "2026-08-01",
            "fasting": fasting,
            "markers": markers,
        }
    )


def test_high_ldl_returns_high_fiber_recipes():
    result = analyze([{"id": "ldl", "value": 170, "unit": "mg/dL"}])
    assert 1 <= len(result["recipes"]) <= 5
    assert any("fiber" in recipe["tags"] for recipe in result["recipes"])


def test_high_ferritin_never_returns_iron_recipes():
    result = analyze(
        [
            {"id": "ferritin", "value": 400, "unit": "ng/mL", "lab_low": 15, "lab_high": 150},
            {"id": "ldl", "value": 170, "unit": "mg/dL"},
        ]
    )
    assert result["results"][0]["id"] == "ldl"
    assert all("iron" not in recipe["tags"] for recipe in result["recipes"])
    assert any("fiber" in recipe["tags"] for recipe in result["recipes"])


def test_high_vitamin_d_never_returns_vitamin_d_recipes():
    result = analyze(
        [
            {"id": "vitamin_d", "value": 62, "unit": "ng/mL"},
            {"id": "b12", "value": 180, "unit": "pg/mL"},
        ]
    )
    assert all("vitamin_d" not in recipe["tags"] for recipe in result["recipes"])
    assert any("b12" in recipe["tags"] for recipe in result["recipes"])


def test_balanced_profile_still_gets_recipes():
    result = analyze(
        [
            {"id": "ldl", "value": 90, "unit": "mg/dL"},
            {"id": "hdl", "value": 55, "unit": "mg/dL"},
            {"id": "glucose", "value": 88, "unit": "mg/dL"},
        ]
    )
    assert result["focus"] == ["balanced"]
    assert result["recipes"]
    assert all("balanced" in recipe["tags"] for recipe in result["recipes"])


def _meal_recipes(result):
    return [option["recipe"] for slot in result["meals"]["day"] for option in slot["options"]]


def test_day_has_breakfast_lunch_and_dinner():
    result = analyze([{"id": "ldl", "value": 170, "unit": "mg/dL"}])
    slots = [slot["slot"] for slot in result["meals"]["day"]]
    assert slots == ["breakfast", "lunch", "dinner"]
    urls = [slot["options"][0]["recipe"]["url"] for slot in result["meals"]["day"]]
    assert len(urls) == len(set(urls))
    assert any("fiber" in recipe["tags"] for recipe in _meal_recipes(result))


def test_meal_plan_skips_iron_when_ferritin_is_high():
    result = analyze(
        [
            {"id": "ferritin", "value": 400, "unit": "ng/mL", "lab_low": 15, "lab_high": 150},
            {"id": "ldl", "value": 170, "unit": "mg/dL"},
        ]
    )
    assert all("iron" not in recipe["tags"] for recipe in _meal_recipes(result))
    reasons = " ".join(option["why"] for slot in result["meals"]["day"] for option in slot["options"])
    assert "Ferritin" not in reasons
    assert "LDL" in reasons


def test_meal_plan_skips_vitamin_d_foods_when_vitamin_d_is_high():
    result = analyze(
        [
            {"id": "vitamin_d", "value": 62, "unit": "ng/mL"},
            {"id": "b12", "value": 180, "unit": "pg/mL"},
        ]
    )
    assert all("vitamin_d" not in recipe["tags"] for recipe in _meal_recipes(result))
    assert any("b12" in recipe["tags"] for recipe in _meal_recipes(result))


def test_see_doctor_marker_does_not_choose_the_menu():
    result = analyze([{"id": "ldl", "value": 198, "unit": "mg/dL"}])
    reasons = " ".join(option["why"] for slot in result["meals"]["day"] for option in slot["options"])
    assert "LDL" not in reasons
    assert result["meals"]["day"]
