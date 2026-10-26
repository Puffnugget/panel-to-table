"""Pick a few recipes whose tags match flagged markers."""

import json
from pathlib import Path

RECIPES = json.loads((Path(__file__).with_name("recipes.json")).read_text())

TAG_MAP = {
    ("ldl", "high"): {"fiber", "heart", "unsaturated_fat"},
    ("hdl", "low"): {"omega3", "heart"},
    ("triglycerides", "high"): {"omega3", "heart", "low_sugar"},
    ("glucose", "high"): {"blood_sugar", "fiber", "whole_grain"},
    ("a1c", "high"): {"blood_sugar", "fiber", "whole_grain"},
    ("vitamin_d", "low"): {"vitamin_d"},
    ("ferritin", "low"): {"iron", "vitamin_c"},
    ("b12", "low"): {"b12"},
}
TIP_TIERS = {"borderline", "out_of_range"}
DAY = (
    ("breakfast", "Breakfast"),
    ("lunch", "Lunch"),
    ("dinner", "Dinner"),
)


def _preferences(results: list[dict]) -> tuple[set[str], set[str]]:
    desired: set[str] = set()
    excluded: set[str] = set()
    for item in results:
        if item["id"] == "ferritin" and item.get("direction") == "high":
            excluded.add("iron")
        if item["id"] == "vitamin_d" and item.get("direction") == "high":
            excluded.add("vitamin_d")
        if item["tier"] not in TIP_TIERS:
            continue
        desired |= TAG_MAP.get((item["id"], item.get("direction")), set())
    return desired, excluded


def _eligible(results: list[dict]) -> tuple[set[str], list[dict]]:
    desired, excluded = _preferences(results)
    pool = [recipe for recipe in RECIPES if excluded.isdisjoint(set(recipe["tags"]))]
    return desired, pool


def _score(recipe: dict, desired: set[str]) -> int:
    return len(desired & set(recipe["tags"]))


def _public(recipe: dict) -> dict:
    return {
        "title": recipe["title"],
        "url": recipe["url"],
        "tags": recipe["tags"],
        "source": recipe["source"],
    }


def _join(names: list[str]) -> str:
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return f"{', '.join(names[:-1])}, and {names[-1]}"


def _why(recipe: dict, results: list[dict]) -> str:
    tags = set(recipe["tags"])
    matched = []
    for item in results:
        if item["tier"] not in TIP_TIERS:
            continue
        wanted = TAG_MAP.get((item["id"], item.get("direction")), set())
        if wanted & tags and item["name"] not in matched:
            matched.append(item["name"])
    if matched:
        return f"This lines up with the food ideas for your {_join(matched)}."
    if any(item["tier"] == "see_doctor" for item in results):
        return "An everyday published recipe. Markers that need a doctor do not choose the menu."
    return "An everyday published recipe for a result in the usual range."


def select_recipes(results: list[dict], limit: int = 4) -> list[dict]:
    desired, pool = _eligible(results)

    if desired:
        ranked = [recipe for recipe in pool if _score(recipe, desired) > 0]
        ranked.sort(key=lambda recipe: (-_score(recipe, desired), recipe["title"]))
    else:
        ranked = [recipe for recipe in pool if "balanced" in recipe["tags"]]
        ranked.sort(key=lambda recipe: recipe["title"])
    if not ranked:
        ranked = sorted(pool, key=lambda recipe: recipe["title"])
    return [_public(recipe) for recipe in ranked[:limit]]


def plan_meals(results: list[dict]) -> dict:
    """One day of breakfast, lunch, and dinner from the same recipe rules."""
    desired, pool = _eligible(results)
    used: set[str] = set()
    day = []
    for slot, label in DAY:
        choices = [recipe for recipe in pool if slot in recipe.get("slots", []) and recipe["url"] not in used]
        if not choices:
            choices = [recipe for recipe in pool if recipe["url"] not in used]
        if desired:
            choices.sort(key=lambda recipe: (-_score(recipe, desired), recipe["title"]))
        else:
            preferred = [recipe for recipe in choices if "balanced" in recipe["tags"]]
            choices = preferred or choices
            choices.sort(key=lambda recipe: recipe["title"])
        picked = choices[:3]
        for recipe in picked:
            used.add(recipe["url"])
        day.append(
            {
                "slot": slot,
                "label": label,
                "options": [{"why": _why(recipe, results), "recipe": _public(recipe)} for recipe in picked],
            }
        )
    if desired:
        summary = (
            "One day of meals for markers that were borderline or outside the usual range. "
            "Markers that need a doctor do not choose the menu."
        )
    elif any(item["tier"] == "see_doctor" for item in results):
        summary = "One day of everyday meals. Markers that need a doctor do not choose the menu."
    else:
        summary = "One day of everyday meals. Nothing entered called for a special food focus."
    return {"summary": summary, "day": day}
