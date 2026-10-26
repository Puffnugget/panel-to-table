"""Ask Spoonacular for a fresh breakfast, lunch, and dinner.

The API key stays on the server. Diet and allergy choices are forwarded as
Spoonacular filters and are not logged. A new request uses a random sort, so
generating again returns a different day.
"""

import os
import random
import re
from pathlib import Path
from typing import Optional

import httpx

from recipes import TIP_TIERS, _join

SEARCH_URL = "https://api.spoonacular.com/recipes/complexSearch"
USER_AGENT = "Panel to Table/0.1 (school project; meal plan lookup)"

DIETS = {
    "gluten free": "Gluten free",
    "ketogenic": "Ketogenic",
    "vegetarian": "Vegetarian",
    "lacto-vegetarian": "Lacto-vegetarian",
    "ovo-vegetarian": "Ovo-vegetarian",
    "vegan": "Vegan",
    "pescetarian": "Pescetarian",
    "paleo": "Paleo",
    "primal": "Primal",
    "low fodmap": "Low FODMAP",
    "whole30": "Whole30",
}

INTOLERANCES = {
    "dairy": "Dairy",
    "egg": "Egg",
    "gluten": "Gluten",
    "grain": "Grain",
    "peanut": "Peanut",
    "seafood": "Seafood",
    "sesame": "Sesame",
    "shellfish": "Shellfish",
    "soy": "Soy",
    "sulfite": "Sulfite",
    "tree nut": "Tree nut",
    "wheat": "Wheat",
}


class SpoonacularError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


def blood_filters(results: list[dict]) -> dict:
    """Nutrient filters only for borderline and out-of-range markers.

    A high ferritin still excludes liver, including when that marker needs a
    doctor, so the search does not come back with an iron-focused organ meat.
    """
    params: dict = {}
    tips = [item for item in results if item.get("tier") in TIP_TIERS]
    if any(item["id"] == "ldl" and item.get("direction") == "high" for item in tips):
        params["minFiber"] = 5
    if any(item["id"] in {"glucose", "a1c", "triglycerides"} and item.get("direction") == "high" for item in tips):
        params["maxSugar"] = 12
    if any(item["id"] == "ferritin" and item.get("direction") == "high" for item in results):
        params["excludeIngredients"] = "beef liver,chicken liver"
    return params


def _why(results: list[dict], diet: str, intolerances: list[str]) -> str:
    bits = ["Spoonacular picked this from the diet and allergies you selected."]
    if diet:
        bits.append(f"Diet: {DIETS[diet]}.")
    if intolerances:
        names = [INTOLERANCES[item] for item in intolerances]
        bits.append(f"Left out: {_join(names)}.")
    leaned = []
    for item in results:
        if item.get("tier") not in TIP_TIERS:
            continue
        if item["id"] == "ldl" and item.get("direction") == "high":
            leaned.append(item["name"])
        elif item["id"] in {"glucose", "a1c", "triglycerides"} and item.get("direction") == "high":
            leaned.append(item["name"])
    if leaned:
        bits.append(f"The search also leaned on your {_join(leaned)}.")
    if any(item.get("tier") == "see_doctor" for item in results):
        bits.append("Markers that need a doctor did not set the search.")
    return " ".join(bits)


def _recipe_url(title: str, recipe_id: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "recipe"
    return f"https://spoonacular.com/recipes/{slug}-{recipe_id}"


def _image(recipe: dict) -> Optional[str]:
    image = recipe.get("image")
    if isinstance(image, str) and image.startswith("http"):
        return image
    recipe_id = recipe.get("id")
    if not recipe_id:
        return None
    kind = recipe.get("imageType") or "jpg"
    return f"https://img.spoonacular.com/recipes/{recipe_id}-312x231.{kind}"


def _option(recipe: dict, why: str) -> dict:
    return {
        "why": why,
        "recipe": {
            "title": recipe.get("title") or "Untitled recipe",
            "url": _recipe_url(recipe.get("title") or "recipe", int(recipe["id"])),
            "tags": [],
            "source": "Spoonacular",
            "image": _image(recipe),
        },
    }


def _take(recipes: list[dict], used: set[int]) -> Optional[dict]:
    for recipe in recipes:
        recipe_id = recipe.get("id")
        if recipe_id in used or recipe_id is None:
            continue
        used.add(recipe_id)
        return recipe
    return None


async def _search(client: httpx.AsyncClient, params: dict) -> list[dict]:
    try:
        response = await client.get(SEARCH_URL, params=params)
    except httpx.HTTPError as exc:
        raise SpoonacularError("Spoonacular didn't respond. Try again in a moment.") from exc
    if response.status_code in {401, 403}:
        raise SpoonacularError("The Spoonacular key was rejected. Check the key on the server.")
    if response.status_code == 402:
        raise SpoonacularError("Spoonacular's daily limit was reached. Try again tomorrow.")
    if response.status_code >= 400:
        raise SpoonacularError("Spoonacular didn't respond. Try again in a moment.")
    try:
        payload = response.json()
    except ValueError as exc:
        raise SpoonacularError("Spoonacular didn't respond. Try again in a moment.") from exc
    results = payload.get("results") if isinstance(payload, dict) else None
    return results if isinstance(results, list) else []


def _load_local_key() -> None:
    """Read a gitignored backend/.env when the process was started without the key."""
    if os.environ.get("SPOONACULAR_API_KEY", "").strip():
        return
    path = Path(__file__).with_name(".env")
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("SPOONACULAR_API_KEY="):
            os.environ["SPOONACULAR_API_KEY"] = stripped.split("=", 1)[1].strip().strip('"').strip("'")
            return


async def generate_day(results: list[dict], diet: Optional[str], intolerances: Optional[list[str]]) -> dict:
    chosen_diet = (diet or "").strip().lower()
    if chosen_diet and chosen_diet not in DIETS:
        raise SpoonacularError("Pick a diet from the list.", 422)
    chosen_intolerances: list[str] = []
    for item in intolerances or []:
        name = str(item).strip().lower()
        if name not in INTOLERANCES:
            raise SpoonacularError("Pick allergies from the list.", 422)
        if name not in chosen_intolerances:
            chosen_intolerances.append(name)

    _load_local_key()
    key = os.environ.get("SPOONACULAR_API_KEY", "").strip()
    if not key:
        raise SpoonacularError("Add a Spoonacular API key on the server to generate a new day.", 503)

    filters = blood_filters(results)
    safety = {key_name: value for key_name, value in filters.items() if key_name == "excludeIngredients"}
    nutrients = {key_name: value for key_name, value in filters.items() if key_name != "excludeIngredients"}
    base = {
        "sort": "random",
        "instructionsRequired": "true",
        **safety,
    }
    if chosen_diet:
        base["diet"] = chosen_diet
    if chosen_intolerances:
        base["intolerances"] = ",".join(chosen_intolerances)

    async with httpx.AsyncClient(timeout=12, headers={"User-Agent": USER_AGENT, "x-api-key": key}) as client:
        breakfast = await _search(
            client,
            {**base, **nutrients, "type": "breakfast", "number": 3, "offset": random.randrange(0, 30)},
        )
        if not breakfast:
            breakfast = await _search(client, {**base, "type": "breakfast", "number": 3, "offset": 0})
        mains = await _search(
            client,
            {**base, **nutrients, "type": "main course", "number": 6, "offset": random.randrange(0, 30)},
        )
        if len(mains) < 2:
            mains = await _search(client, {**base, "type": "main course", "number": 6, "offset": 0})

    used: set[int] = set()
    picked = [_take(breakfast, used), _take(mains, used), _take(mains, used)]
    if any(recipe is None for recipe in picked):
        raise SpoonacularError(
            "Spoonacular didn't find enough recipes for those restrictions. Try fewer boxes.",
            404,
        )

    why = _why(results, chosen_diet, chosen_intolerances)
    labels = (("breakfast", "Breakfast"), ("lunch", "Lunch"), ("dinner", "Dinner"))
    return {
        "summary": "A new day from Spoonacular. Generate again for a different set of recipes.",
        "day": [
            {"slot": slot, "label": label, "options": [_option(recipe, why)]}
            for (slot, label), recipe in zip(labels, picked)
        ],
    }
