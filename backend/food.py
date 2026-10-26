"""Look up a packaged food on Open Food Facts and return label numbers.

The barcode or name is not logged or stored. Open Food Facts is a public
food database; a missing product just means we could not find that package.
"""

from typing import Any, Optional

import httpx

USER_AGENT = "Panel to Table/0.1 (school project; nutrition label lookup)"
PRODUCT_URL = "https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
SEARCH_URL = "https://search.openfoodfacts.org/search"
PRODUCT_FIELDS = "code,product_name,generic_name,brands,serving_size,nutriments,url"

# Open Food Facts stores most weights in grams. The label people expect
# uses milligrams for sodium, cholesterol, and iron, and micrograms for vitamins.
FIELDS = [
    ("energy-kcal", "Calories", "kcal", "kcal"),
    ("proteins", "Protein", "g", "g"),
    ("carbohydrates", "Carbohydrates", "g", "g"),
    ("sugars", "Sugars", "g", "g"),
    ("fiber", "Fiber", "g", "g"),
    ("fat", "Fat", "g", "g"),
    ("saturated-fat", "Saturated fat", "g", "g"),
    ("sodium", "Sodium", "g", "mg"),
    ("cholesterol", "Cholesterol", "g", "mg"),
    ("iron", "Iron", "g", "mg"),
    ("vitamin-d", "Vitamin D", "µg", "µg"),
    ("vitamin-b12", "Vitamin B12", "µg", "µg"),
]

_TO_MG = {"g": 1000, "mg": 1, "µg": 0.001, "ug": 0.001, "mcg": 0.001}
_TO_UG = {"g": 1_000_000, "mg": 1000, "µg": 1, "ug": 1, "mcg": 1}


class FoodLookupError(Exception):
    def __init__(self, message: str, status_code: int = 404):
        super().__init__(message)
        self.status_code = status_code


def normalize_product(product: dict) -> Optional[dict]:
    if not product:
        return None
    name = (product.get("product_name") or product.get("generic_name") or "").strip()
    nutriments = product.get("nutriments") or {}
    stats = []
    for key, label, default_unit, display_unit in FIELDS:
        per_100 = _convert(nutriments.get(f"{key}_100g"), nutriments.get(f"{key}_unit"), default_unit, display_unit)
        per_serving = _convert(nutriments.get(f"{key}_serving"), nutriments.get(f"{key}_unit"), default_unit, display_unit)
        if per_100 is None and per_serving is None:
            continue
        stats.append(
            {
                "id": key,
                "label": label,
                "unit": display_unit,
                "per_100g": per_100,
                "per_serving": per_serving,
            }
        )
    if not name and not stats:
        return None
    barcode = str(product.get("code") or "").strip() or None
    brands = product.get("brands") or ""
    if isinstance(brands, list):
        brands = ", ".join(str(item) for item in brands if item)
    return {
        "name": name or "Unnamed product",
        "brand": str(brands).split(",")[0].strip() or None,
        "barcode": barcode,
        "serving": (product.get("serving_size") or "").strip() or None,
        "stats": stats,
        "url": product.get("url") or (f"https://world.openfoodfacts.org/product/{barcode}" if barcode else None),
    }


def _convert(value: Any, unit: Optional[str], default_unit: str, display_unit: str) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    source = (unit or default_unit).replace("μg", "µg")
    if source == display_unit:
        converted = number
    elif display_unit == "mg":
        factor = _TO_MG.get(source)
        if factor is None:
            return None
        converted = number * factor
    elif display_unit == "µg":
        factor = _TO_UG.get(source)
        if factor is None:
            return None
        converted = number * factor
    else:
        return None
    if display_unit == "kcal":
        return float(round(converted))
    if abs(converted) >= 10:
        return round(converted, 1)
    return round(converted, 2)


async def lookup_food(barcode: Optional[str] = None, query: Optional[str] = None) -> dict:
    barcode = (barcode or "").strip()
    query = (query or "").strip()
    if barcode and not barcode.isdigit():
        raise FoodLookupError("A barcode should be digits only.", 422)
    if barcode and not 6 <= len(barcode) <= 14:
        raise FoodLookupError("That barcode length does not look like a food package.", 422)
    if not barcode and len(query) < 2:
        raise FoodLookupError("Enter a barcode or at least two letters of a food name.", 422)

    try:
        async with httpx.AsyncClient(timeout=12, headers={"User-Agent": USER_AGENT}) as client:
            if barcode:
                products = [await _product(client, barcode)]
            else:
                codes = await _search_codes(client, query)
                products = [await _product(client, code) for code in codes]
    except (httpx.HTTPError, ValueError) as exc:
        raise FoodLookupError("The food database didn't respond. Try again in a moment.", 502) from exc

    matches = []
    for product in products:
        normalized = normalize_product(product)
        if normalized:
            matches.append(normalized)
    if not matches:
        raise FoodLookupError("We couldn't find nutrition numbers for that food.", 404)
    return {"matches": matches[:5]}


async def _read_json(response: httpx.Response) -> dict:
    if response.status_code >= 500:
        raise FoodLookupError("The food database didn't respond. Try again in a moment.", 502)
    try:
        payload = response.json()
    except ValueError as exc:
        raise FoodLookupError("The food database didn't respond. Try again in a moment.", 502) from exc
    return payload if isinstance(payload, dict) else {}


async def _product(client: httpx.AsyncClient, barcode: str) -> Optional[dict]:
    response = await client.get(PRODUCT_URL.format(barcode=barcode), params={"fields": PRODUCT_FIELDS})
    payload = await _read_json(response)
    if payload.get("status") != 1:
        return None
    product = payload.get("product")
    return product if isinstance(product, dict) else None


async def _search_codes(client: httpx.AsyncClient, query: str) -> list[str]:
    response = await client.get(SEARCH_URL, params={"q": query, "page_size": 5})
    payload = await _read_json(response)
    codes: list[str] = []
    for hit in payload.get("hits") or []:
        code = str((hit or {}).get("code") or "").strip()
        if code and code not in codes:
            codes.append(code)
    return codes
