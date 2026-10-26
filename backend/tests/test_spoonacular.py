import asyncio

import pytest

from spoonacular import SpoonacularError, blood_filters, generate_day


def test_see_doctor_ldl_does_not_set_a_fiber_target():
    filters = blood_filters(
        [{"id": "ldl", "tier": "see_doctor", "direction": "high", "name": "LDL cholesterol"}]
    )
    assert "minFiber" not in filters


def test_high_ldl_asks_for_fiber_and_high_ferritin_skips_liver():
    filters = blood_filters(
        [
            {"id": "ldl", "tier": "out_of_range", "direction": "high", "name": "LDL cholesterol"},
            {"id": "ferritin", "tier": "see_doctor", "direction": "high", "name": "Ferritin"},
        ]
    )
    assert filters["minFiber"] == 5
    assert "liver" in filters["excludeIngredients"]


def test_high_glucose_caps_sugar():
    filters = blood_filters(
        [{"id": "glucose", "tier": "out_of_range", "direction": "high", "name": "Fasting glucose"}]
    )
    assert filters["maxSugar"] == 12


def test_unknown_diet_is_rejected_before_the_network():
    with pytest.raises(SpoonacularError) as caught:
        asyncio.run(generate_day([], "pizza", []))
    assert caught.value.status_code == 422


def test_meal_plan_route_returns_the_generated_day(monkeypatch):
    from fastapi.testclient import TestClient

    import api

    async def fake_day(results, diet, intolerances):
        assert diet == "vegan"
        assert intolerances == ["peanut"]
        assert results[0]["id"] == "ldl"
        return {
            "summary": "A new day from Spoonacular.",
            "day": [
                {
                    "slot": "breakfast",
                    "label": "Breakfast",
                    "options": [
                        {
                            "why": "Spoonacular picked this.",
                            "recipe": {
                                "title": "Oats",
                                "url": "https://spoonacular.com/recipes/oats-1",
                                "tags": [],
                                "source": "Spoonacular",
                                "image": None,
                            },
                        }
                    ],
                }
            ],
        }

    monkeypatch.setattr(api, "generate_day", fake_day)
    client = TestClient(api.app)
    response = client.post(
        "/meal-plan",
        json={
            "age": 40,
            "sex": "female",
            "test_date": "2026-08-01",
            "fasting": True,
            "diet": "vegan",
            "intolerances": ["peanut"],
            "markers": [{"id": "ldl", "value": 170, "unit": "mg/dL"}],
        },
    )
    assert response.status_code == 200
    assert response.json()["meals"]["day"][0]["options"][0]["recipe"]["title"] == "Oats"
