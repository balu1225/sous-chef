---
name: usda-nutrition
description: Canonical ingredient dictionary, USDA FoodData Central 100g macros, average item weights, and nutrition summary calculations.
---

# USDA Nutrition Engineering Standard

## 1. Principles & Normalization
1. **Base Normalization:** All nutritional values are stored per **100 grams** (USDA FoodData Central Foundation standard).
2. **Deterministic Lookup:** Nutrition math is pure arithmetic based on verified data.
3. **Open-Source Ready:** The ingredient database is isolated in `src/sous_chef/data/canonical_ingredients.json` to be exported into a standalone MIT open-source repo (Open Source mini-challenge).

## 2. Seed Ingredient Table (~50 Core Items)

| Canonical ID | Canonical Name | Energy (kcal / 100g) | Protein (g / 100g) | Avg Weight / Count (g) | Typical Shelf Life (days) | Common Synonyms |
|---|---|---|---|---|---|---|
| `egg_whole` | Whole Egg | 143 | 12.6 | 50.0 | 28 | egg, eggs, large egg, farm eggs |
| `milk_whole` | Whole Milk | 61 | 3.2 | 1.03 (g/ml) | 7 | milk, whole milk, vitamin d milk |
| `chicken_breast` | Chicken Breast | 165 | 31.0 | 174.0 | 2 | chicken breast, raw chicken, chicken |
| `ground_beef` | Ground Beef 85/15 | 215 | 18.6 | - | 2 | ground beef, minced beef, hamburger |
| `spinach_fresh` | Fresh Spinach | 23 | 2.9 | 30.0 (cup) | 5 | spinach, baby spinach, fresh spinach |
| `cheddar_cheese` | Cheddar Cheese | 403 | 24.9 | 28.0 (slice) | 21 | cheddar, cheese, shredded cheddar |
| `black_beans` | Black Beans (canned) | 91 | 6.0 | 425.0 (can) | 730 | black beans, canned black beans |
| `crushed_tomatoes`| Crushed Tomatoes | 32 | 1.6 | 794.0 (can) | 730 | canned tomatoes, crushed tomatoes |
| `white_rice` | White Rice (dry) | 365 | 7.1 | 185.0 (cup) | 365 | white rice, rice, jasmine rice |
| `olive_oil` | Extra Virgin Olive Oil | 884 | 0.0 | 14.0 (tbsp) | 365 | olive oil, extra virgin olive oil, evoo |

## 3. Macro Calculation Algorithm
When a recipe is cooked or an item is consumed:
```python
def calculate_item_macros(canonical_id: str, quantity: float, unit: str, ingredient_db: dict) -> dict:
    """Calculates kcal and protein for a given quantity of an ingredient."""
    data = ingredient_db.get(canonical_id)
    if not data:
        return {"kcal": 0.0, "protein_g": 0.0}

    # 1. Convert to grams
    if unit == "g":
        grams = quantity
    elif unit == "ml":
        density = data.get("density_g_per_ml", 1.0)
        grams = quantity * density
    elif unit == "count":
        avg_weight = data.get("avg_weight_g", 100.0)
        grams = quantity * avg_weight
    else:
        grams = quantity  # fallback

    # 2. Compute macros based on 100g reference
    kcal = round((grams / 100.0) * data["kcal_per_100g"], 1)
    protein = round((grams / 100.0) * data["protein_g_per_100g"], 1)

    return {"kcal": kcal, "protein_g": protein, "grams": round(grams, 1)}
```

## 4. Daily Nutrition Summary (`nutrition_summary`)
Tool output contract matching PDD Section 9:
```json
{
  "ok": true,
  "summary": {
    "date": "2026-10-20",
    "total_kcal": 1420.0,
    "total_protein_g": 94.5,
    "meals_logged": 2,
    "spoken_summary": "Today you've consumed approximately 1,420 calories and 95 grams of protein across 2 meals."
  }
}
```

## 5. Implementation Checklist
- [ ] 50 canonical items loaded in `src/sous_chef/data/canonical_ingredients.json`.
- [ ] Exact USDA FoodData Central values verified.
- [ ] Spoken alias resolver matches plurals and informal names ("eggs" -> `egg_whole`).
- [ ] Rounding conforms to single-decimal precision for user TTS.
