import pytest

from rules import analyze_payload, classify_marker, convert_value


def one(marker_id, value, unit, age=34, sex="female", fasting=True, lab_low=None, lab_high=None):
    return classify_marker(marker_id, value, unit, age, sex, fasting, lab_low, lab_high)


def test_a1c_edges():
    assert one("a1c", 5.6, "%")["tier"] == "in_range"
    assert one("a1c", 5.7, "%")["tier"] == "out_of_range"
    assert one("a1c", 6.4, "%")["tier"] == "out_of_range"
    assert one("a1c", 6.5, "%")["tier"] == "see_doctor"
    assert one("a1c", 6.5, "%")["foods"] == []


def test_glucose_edges_and_fasting():
    assert one("glucose", 69, "mg/dL")["tier"] == "see_doctor"
    assert one("glucose", 70, "mg/dL")["tier"] == "in_range"
    assert one("glucose", 99, "mg/dL")["tier"] == "in_range"
    assert one("glucose", 100, "mg/dL")["tier"] == "out_of_range"
    assert one("glucose", 125, "mg/dL")["tier"] == "out_of_range"
    assert one("glucose", 126, "mg/dL")["tier"] == "see_doctor"
    unrated = one("glucose", 180, "mg/dL", fasting=False)
    assert unrated["tier"] == "unrated"
    assert unrated["foods"] == []


def test_ldl_adult_and_youth_switch_at_20():
    assert one("ldl", 99, "mg/dL", age=34)["tier"] == "in_range"
    assert one("ldl", 100, "mg/dL", age=34)["tier"] == "in_range"
    assert one("ldl", 129, "mg/dL", age=34)["tier"] == "in_range"
    assert one("ldl", 130, "mg/dL", age=34)["tier"] == "borderline"
    assert one("ldl", 159, "mg/dL", age=34)["tier"] == "borderline"
    assert one("ldl", 160, "mg/dL", age=34)["tier"] == "out_of_range"
    assert one("ldl", 189, "mg/dL", age=34)["tier"] == "out_of_range"
    assert one("ldl", 190, "mg/dL", age=34)["tier"] == "see_doctor"
    assert one("ldl", 120, "mg/dL", age=19)["tier"] == "borderline"
    assert one("ldl", 120, "mg/dL", age=20)["tier"] == "in_range"
    assert one("ldl", 109, "mg/dL", age=16)["tier"] == "in_range"
    assert one("ldl", 110, "mg/dL", age=16)["tier"] == "borderline"
    assert one("ldl", 130, "mg/dL", age=16)["tier"] == "out_of_range"
    assert one("ldl", 190, "mg/dL", age=16)["tier"] == "see_doctor"


def test_hdl_depends_on_sex_for_adults_only():
    assert one("hdl", 40, "mg/dL", age=30, sex="male")["tier"] == "in_range"
    assert one("hdl", 39, "mg/dL", age=30, sex="male")["tier"] == "out_of_range"
    assert one("hdl", 50, "mg/dL", age=30, sex="female")["tier"] == "in_range"
    assert one("hdl", 49, "mg/dL", age=30, sex="female")["tier"] == "out_of_range"
    assert one("hdl", 42, "mg/dL", age=16, sex="male")["tier"] == "borderline"
    assert one("hdl", 42, "mg/dL", age=16, sex="female")["tier"] == "borderline"
    assert one("hdl", 45, "mg/dL", age=16)["tier"] == "borderline"
    assert one("hdl", 46, "mg/dL", age=16)["tier"] == "in_range"
    assert one("hdl", 39, "mg/dL", age=16)["tier"] == "out_of_range"


def test_triglyceride_edges():
    assert one("triglycerides", 149, "mg/dL", age=40)["tier"] == "in_range"
    assert one("triglycerides", 150, "mg/dL", age=40)["tier"] == "borderline"
    assert one("triglycerides", 199, "mg/dL", age=40)["tier"] == "borderline"
    assert one("triglycerides", 200, "mg/dL", age=40)["tier"] == "out_of_range"
    assert one("triglycerides", 499, "mg/dL", age=40)["tier"] == "out_of_range"
    assert one("triglycerides", 500, "mg/dL", age=40)["tier"] == "see_doctor"
    assert one("triglycerides", 500, "mg/dL")["foods"] == []
    assert one("triglycerides", 89, "mg/dL", age=16)["tier"] == "in_range"
    assert one("triglycerides", 90, "mg/dL", age=16)["tier"] == "borderline"
    assert one("triglycerides", 129, "mg/dL", age=16)["tier"] == "borderline"
    assert one("triglycerides", 130, "mg/dL", age=16)["tier"] == "out_of_range"
    unrated = one("triglycerides", 400, "mg/dL", fasting=False)
    assert unrated["tier"] == "unrated"


def test_vitamin_d_and_b12_edges():
    assert one("vitamin_d", 11.9, "ng/mL")["tier"] == "out_of_range"
    assert one("vitamin_d", 12, "ng/mL")["tier"] == "borderline"
    assert one("vitamin_d", 19.9, "ng/mL")["tier"] == "borderline"
    assert one("vitamin_d", 20, "ng/mL")["tier"] == "in_range"
    assert one("vitamin_d", 50, "ng/mL")["tier"] == "in_range"
    high = one("vitamin_d", 50.1, "ng/mL")
    assert high["tier"] == "see_doctor"
    assert high["foods"] == []
    assert "salmon" not in high["foods"]
    assert one("b12", 199, "pg/mL")["tier"] == "out_of_range"
    assert one("b12", 200, "pg/mL")["tier"] == "borderline"
    assert one("b12", 299, "pg/mL")["tier"] == "borderline"
    assert one("b12", 300, "pg/mL")["tier"] == "in_range"


def test_ferritin_lab_range_and_30_cutoff():
    low = one("ferritin", 9, "ng/mL", lab_low=13, lab_high=150)
    assert low["tier"] == "out_of_range"
    assert low["direction"] == "low"
    assert "lentils" in low["foods"]
    assert "lean beef" in low["foods"]
    assert "vitamin C" in low["tip"]
    assert "Below your lab's range" in low["message"]
    assert one("ferritin", 20, "ng/mL", lab_low=13, lab_high=150)["tier"] == "in_range"
    high = one("ferritin", 151, "ng/mL", lab_low=13, lab_high=150)
    assert high["tier"] == "see_doctor"
    assert high["foods"] == []
    assert one("ferritin", 29, "ng/mL")["tier"] == "out_of_range"
    assert one("ferritin", 30, "ng/mL")["tier"] == "in_range"


def test_lab_range_overrides_table_but_not_see_doctor():
    overridden = one("ldl", 118, "mg/dL", age=40, lab_low=0, lab_high=100)
    assert overridden["tier"] == "out_of_range"
    assert overridden["foods"]
    safety = one("ldl", 195, "mg/dL", age=40, lab_low=0, lab_high=300)
    assert safety["tier"] == "see_doctor"
    assert safety["foods"] == []


def test_unit_conversions():
    assert convert_value("ldl", 3, "mmol/L") == pytest.approx(115.8)
    assert convert_value("triglycerides", 2, "mmol/L") == pytest.approx(177.2)
    assert convert_value("glucose", 5.5, "mmol/L") == pytest.approx(99)
    assert convert_value("a1c", 48, "mmol/mol") == pytest.approx(6.542)
    assert convert_value("vitamin_d", 50, "nmol/L") == pytest.approx(20)
    assert convert_value("ferritin", 30, "mcg/L") == pytest.approx(30)
    assert convert_value("b12", 148, "pmol/L") == pytest.approx(200)
    assert one("a1c", 48, "mmol/mol")["tier"] == "see_doctor"
    assert one("vitamin_d", 50, "nmol/L")["tier"] == "in_range"
    assert one("b12", 148, "pmol/L")["tier"] == "borderline"
    assert one("glucose", 7, "mmol/L")["tier"] == "see_doctor"


def test_impossible_values_stop_analysis():
    payload = {
        "age": 30,
        "sex": "male",
        "test_date": "2026-10-01",
        "fasting": True,
        "markers": [
            {"id": "ldl", "value": -5, "unit": "mg/dL"},
            {"id": "hdl", "value": 50, "unit": "mg/dL"},
        ],
    }
    with pytest.raises(ValueError):
        analyze_payload(payload)
    with pytest.raises(ValueError):
        one("glucose", 0, "mg/dL")
    with pytest.raises(ValueError):
        one("b12", 100000, "pg/mL")


def test_nonfasting_glucose_does_not_raise_focus_or_callout():
    result = analyze_payload(
        {
            "age": 28,
            "sex": "female",
            "test_date": "2026-09-01",
            "fasting": False,
            "markers": [{"id": "glucose", "value": 180, "unit": "mg/dL"}],
        }
    )
    assert result["see_doctor"] == []
    assert result["focus"] == ["balanced"]
    assert result["results"][0]["tier"] == "unrated"


def test_see_doctor_is_listed_and_gets_no_food_tips():
    result = analyze_payload(
        {
            "age": 52,
            "sex": "female",
            "test_date": "2026-10-01",
            "fasting": True,
            "markers": [
                {"id": "ldl", "value": 198, "unit": "mg/dL"},
                {"id": "hdl", "value": 38, "unit": "mg/dL"},
                {"id": "a1c", "value": 6.6, "unit": "%"},
                {"id": "vitamin_d", "value": 62, "unit": "ng/mL"},
            ],
        }
    )
    assert result["see_doctor"] == ["ldl", "a1c", "vitamin_d"]
    by_id = {item["id"]: item for item in result["results"]}
    assert by_id["ldl"]["foods"] == []
    assert by_id["a1c"]["foods"] == []
    assert by_id["vitamin_d"]["foods"] == []
    assert by_id["hdl"]["foods"]
    assert "heart" in result["focus"]
    assert "blood_sugar" not in result["focus"]
    assert "vitamin_d" not in result["focus"]
    assert "60 minutes" not in result["activity"]
    assert "150 minutes" in result["activity"]


def test_youth_activity_line():
    result = analyze_payload(
        {
            "age": 16,
            "sex": "female",
            "test_date": "2026-09-14",
            "fasting": True,
            "markers": [{"id": "ferritin", "value": 9, "unit": "ng/mL", "lab_low": 13, "lab_high": 150}],
        }
    )
    assert result["activity"].startswith("Aim for 60 minutes")
    assert result["focus"] == ["iron_b12"]
    assert result["results"][0]["tier"] == "out_of_range"
