import pytest
from fastapi.testclient import TestClient

from api import app
from food import normalize_product

OATS = {
    "product_name": "Rolled oats",
    "brands": "Example Mill",
    "code": "1234567890123",
    "serving_size": "40 g",
    "url": "https://world.openfoodfacts.org/product/1234567890123",
    "nutriments": {
        "energy-kcal_100g": 379,
        "energy-kcal_serving": 151.6,
        "proteins_100g": 13.2,
        "carbohydrates_100g": 67.7,
        "sugars_100g": 1,
        "fiber_100g": 10.1,
        "fat_100g": 6.5,
        "saturated-fat_100g": 1.1,
        "sodium_100g": 0.006,
        "sodium_unit": "g",
        "iron_100g": 0.004,
        "iron_unit": "g",
    },
}


def test_normalize_converts_sodium_and_iron_to_milligrams():
    food = normalize_product(OATS)
    by_id = {item["id"]: item for item in food["stats"]}
    assert food["name"] == "Rolled oats"
    assert by_id["energy-kcal"]["per_100g"] == 379
    assert by_id["energy-kcal"]["per_serving"] == 152
    assert by_id["fiber"]["per_100g"] == 10.1
    assert by_id["sodium"]["unit"] == "mg"
    assert by_id["sodium"]["per_100g"] == 6
    assert by_id["iron"]["per_100g"] == 4
    assert "vitamin-d" not in by_id


def test_iron_already_in_milligrams_is_not_scaled_again():
    product = {
        "product_name": "Cereal",
        "nutriments": {"iron_100g": 8, "iron_unit": "mg"},
    }
    food = normalize_product(product)
    assert food["stats"][0]["per_100g"] == 8
    assert food["stats"][0]["unit"] == "mg"


def test_food_route_uses_the_normalizer(monkeypatch):
    async def fake_lookup(barcode=None, query=None):
        assert barcode == "1234567890123"
        return {"matches": [normalize_product(OATS)]}

    monkeypatch.setattr("api.lookup_food", fake_lookup)
    client = TestClient(app)
    response = client.post("/food", json={"barcode": "1234567890123"})
    assert response.status_code == 200
    assert response.json()["matches"][0]["name"] == "Rolled oats"


def test_food_route_rejects_a_word_as_a_barcode():
    client = TestClient(app)
    response = client.post("/food", json={"barcode": "oats"})
    assert response.status_code == 422
