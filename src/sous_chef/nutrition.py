"""USDA Nutrition module for Sous-Chef.

Provides deterministic nutritional lookups based on USDA FoodData Central 100g standards.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).resolve().parent / "data" / "canonical_ingredients.json"

_INGREDIENTS: dict[str, dict[str, Any]] = {}
_SYNONYM_MAP: dict[str, str] = {}


def _load_data() -> None:
    global _INGREDIENTS, _SYNONYM_MAP
    if _INGREDIENTS:
        return
    if not DATA_FILE.exists():
        return
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        _INGREDIENTS = json.load(f)

    for cid, data in _INGREDIENTS.items():
        _SYNONYM_MAP[cid.lower()] = cid
        _SYNONYM_MAP[data["name"].lower()] = cid
        for syn in data.get("synonyms", []):
            _SYNONYM_MAP[syn.lower()] = cid


_load_data()


def lookup_canonical(name: str) -> tuple[str, dict[str, Any]] | None:
    """Matches a spoken or typed ingredient name to a canonical ingredient."""
    _load_data()
    clean = name.lower().strip()
    cid = _SYNONYM_MAP.get(clean)
    if cid:
        return cid, _INGREDIENTS[cid]

    # Partial / substring match
    for syn, c in _SYNONYM_MAP.items():
        if syn in clean or clean in syn:
            return c, _INGREDIENTS[c]
    return None


def calculate_item_macros(name: str, qty: float, unit: str) -> dict[str, float]:
    """Calculates calories and protein based on USDA 100g baseline."""
    match = lookup_canonical(name)
    if not match:
        return {"kcal": 0.0, "protein_g": 0.0, "grams": 0.0}

    cid, data = match
    family = data.get("family", "count")

    # 1. Convert to grams
    grams = 0.0
    if unit in ("g", "gram", "grams"):
        grams = qty
    elif unit in ("kg", "kilogram", "kilograms"):
        grams = qty * 1000.0
    elif unit in ("lb", "lbs", "pound", "pounds"):
        grams = qty * 453.592
    elif unit in ("oz", "ounce", "ounces"):
        grams = qty * 28.3495
    elif unit in ("ml", "milliliter", "milliliters"):
        density = data.get("density_g_per_ml", 1.0)
        grams = qty * density
    elif unit in ("gallon", "gallons"):
        density = data.get("density_g_per_ml", 1.0)
        grams = qty * 3785.41 * density
    elif unit in ("cup", "cups"):
        density = data.get("density_g_per_ml", 1.0)
        grams = qty * 236.588 * density
    elif unit in ("count", "item", "piece", "can", "bottle"):
        avg_weight = data.get("avg_weight_g", 100.0)
        grams = qty * avg_weight
    else:
        grams = qty

    # 2. Compute macros
    kcal = round((grams / 100.0) * data.get("kcal_per_100g", 0.0), 1)
    protein = round((grams / 100.0) * data.get("protein_g_per_100g", 0.0), 1)

    return {"kcal": kcal, "protein_g": protein, "grams": round(grams, 1)}


def calculate_meal_nutrition(ingredients: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregates nutritional breakdown across multiple ingredients."""
    total_kcal = 0.0
    total_protein = 0.0
    breakdown = []

    for ing in ingredients:
        name = ing.get("item") or ing.get("name", "")
        qty = float(ing.get("qty") or ing.get("amount", 1.0))
        unit = ing.get("unit", "count")
        macros = calculate_item_macros(name, qty, unit)
        total_kcal += macros["kcal"]
        total_protein += macros["protein_g"]
        breakdown.append({
            "item": name,
            "qty": qty,
            "unit": unit,
            "kcal": macros["kcal"],
            "protein_g": macros["protein_g"]
        })

    return {
        "total_kcal": round(total_kcal, 1),
        "total_protein_g": round(total_protein, 1),
        "breakdown": breakdown
    }
