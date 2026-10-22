"""Deterministic recipe matching engine and guided cooking state for Sous-Chef.

Adheres strictly to PDD Section 11 & recipe-matching-engine standards:
- 100% deterministic math; zero AI hallucinations.
- Hard filters reject recipes missing >= 2 core ingredients or with < 50% needed stock.
- Scoring formula:
    Score = (0.45 * C) + (0.30 * E_48h) + (0.10 * Conf) + (0.10 * Pref) + (0.05 * Variety) + GoalBoost
- Clamped cooking deduction ensuring stock is never left negative.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from sous_chef.nutrition import calculate_meal_nutrition, lookup_canonical
from sous_chef.ledger import Ledger, LedgerError, Store

SEED_FILE = Path(__file__).resolve().parent / "data" / "seed_recipes.json"

_SEEDS: list[dict[str, Any]] = []


def _load_seeds() -> list[dict[str, Any]]:
    global _SEEDS
    if not _SEEDS and SEED_FILE.exists():
        with open(SEED_FILE, "r", encoding="utf-8") as f:
            _SEEDS = json.load(f)
    return _SEEDS


def get_all_recipes(store: Store | None = None, household_id: str | None = None) -> list[dict[str, Any]]:
    """Combines hardcoded seed recipes with household custom recipes from DB."""
    recipes = list(_load_seeds())
    if store and household_id:
        try:
            with store.pool.connection() as conn:
                rows = conn.execute(
                    "SELECT recipe_id::text, name, servings, prep_minutes, ingredients, steps "
                    "FROM custom_recipes WHERE household_id = %s",
                    (household_id,)
                ).fetchall()
                for r in rows:
                    recipes.append({
                        "id": str(r["recipe_id"]),
                        "name": r["name"],
                        "servings": float(r["servings"]),
                        "prep_minutes": int(r["prep_minutes"]),
                        "tags": ["custom"],
                        "ingredients": r["ingredients"],
                        "steps": r["steps"] or []
                    })
        except Exception:
            pass
    return recipes


def find_recipe_by_id(recipe_id: str, store: Store | None = None, household_id: str | None = None) -> dict[str, Any] | None:
    for r in get_all_recipes(store, household_id):
        if r["id"] == recipe_id or r["name"].lower() == recipe_id.lower():
            return r
    return None


def match_recipes(
    inventory_items: list[dict[str, Any]],
    goal: str | None = None,
    max_minutes: int | None = None,
    never_suggest: list[str] | None = None,
    recipes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Scores candidate recipes against active stock.
    
    Returns structured recommendations and caring spoken advice.
    """
    if recipes is None:
        recipes = _load_seeds()

    never_set = set(i.lower().strip() for i in (never_suggest or []))
    now = datetime.now(timezone.utc)
    cutoff_48h = now + timedelta(hours=48)
    cutoff_5d = now + timedelta(days=5)

    # 1. Map available stock (only items with qty > 0)
    stock_map: dict[str, dict[str, Any]] = {}
    for r in inventory_items:
        qty = float(r.get("qty", 0))
        if qty <= 0:
            continue
        item_name = r["item"].lower().strip()
        canon = lookup_canonical(item_name)
        cid = canon[0] if canon else item_name
        stock_map[cid] = {
            "item": item_name,
            "qty": qty,
            "unit": r.get("unit", "count"),
            "expires_at": r.get("expires_at")
        }

    candidates = []

    for recipe in recipes:
        # Time filter (for busy days: "in 15 minutes or less")
        prep_min = recipe.get("prep_minutes", 15)
        if max_minutes is not None and prep_min > max_minutes:
            continue

        # Check never-suggest exclusions
        has_never = False
        for ing in recipe["ingredients"]:
            if ing["item"].lower() in never_set:
                has_never = True
                break
        if has_never:
            continue

        # Evaluate ingredients
        core_count = 0
        missing_core = []
        insufficient_core = False
        available_count = 0
        expiring_used = []
        total_ingredients = len(recipe["ingredients"])

        for ing in recipe["ingredients"]:
            name = ing["item"].lower().strip()
            role = ing.get("role", "core")
            canon = lookup_canonical(name)
            cid = canon[0] if canon else name

            if role == "core":
                core_count += 1

            in_stock = stock_map.get(cid)
            if in_stock and in_stock["qty"] > 0:
                available_count += 1
                req_qty = float(ing.get("qty", 1.0))
                # Check 50% quantity sufficiency for core items
                if role == "core" and in_stock["qty"] < (req_qty * 0.5):
                    insufficient_core = True

                # Check expiry boost
                exp_str = in_stock.get("expires_at")
                if exp_str:
                    try:
                        exp_dt = datetime.fromisoformat(exp_str)
                        if exp_dt <= cutoff_48h:
                            expiring_used.append({"item": name, "urgency": "48h"})
                        elif exp_dt <= cutoff_5d:
                            expiring_used.append({"item": name, "urgency": "5d"})
                    except Exception:
                        pass
            else:
                if role == "core":
                    missing_core.append(name)

        # Hard Filter 1: Reject if missing >= 2 core ingredients
        if len(missing_core) >= 2:
            continue

        # Hard Filter 2: Reject if available core stock is < 50% needed
        if insufficient_core:
            continue

        # 3. Deterministic Scoring
        coverage = available_count / max(1, total_ingredients)
        
        # Expiry score: 1.0 if any <= 48h, 0.5 if <= 5d, else 0.0
        exp_score = 0.0
        if any(e["urgency"] == "48h" for e in expiring_used):
            exp_score = 1.0
        elif any(e["urgency"] == "5d" for e in expiring_used):
            exp_score = 0.5

        confidence = 1.0  # Stubbed in R1 per D8
        preference = 0.5  # Standard baseline
        variety = 1.0     # Default variety weight

        score = (0.45 * coverage) + (0.30 * exp_score) + (0.10 * confidence) + (0.10 * preference) + (0.05 * variety)

        # Goal Boosts
        nutrition = calculate_meal_nutrition(recipe["ingredients"])
        base_servings = float(recipe.get("servings", 1.0))
        kcal_per_serv = round(nutrition["total_kcal"] / base_servings, 1)
        prot_per_serv = round(nutrition["total_protein_g"] / base_servings, 1)

        if goal == "quick" and prep_min <= 15:
            score += 0.15
        elif goal == "high_protein" and prot_per_serv >= 25.0:
            score += 0.15
        elif goal == "use_expiring" and exp_score > 0:
            score += 0.15

        candidates.append({
            "id": recipe["id"],
            "name": recipe["name"],
            "prep_minutes": prep_min,
            "servings": recipe.get("servings", 2),
            "score": round(score, 3),
            "coverage_pct": round(coverage * 100),
            "missing_core": missing_core,
            "expiring_used": [e["item"] for e in expiring_used],
            "kcal_per_serving": kcal_per_serv,
            "protein_per_serving": prot_per_serv,
            "ingredients": recipe["ingredients"],
            "steps": recipe.get("steps", [])
        })

    # Sort deterministically: score DESC, prep_minutes ASC, name ASC
    candidates.sort(key=lambda c: (-c["score"], c["prep_minutes"], c["name"]))

    if not candidates:
        if not stock_map:
            msg = "Your kitchen is currently empty. Tell me what groceries you bought so I can suggest delicious meals!"
        elif max_minutes is not None and max_minutes <= 15:
            msg = f"I couldn't find a complete meal you can make in {max_minutes} minutes with your current stock. Tell me what you'd like to cook, or check what is about to expire!"
        else:
            msg = "I couldn't find a full recipe matching your stock right now. Try adding a couple staples like eggs or rice!"
        return {"suggestions": [], "spoken_message": msg}

    top = candidates[0]
    backup = candidates[1] if len(candidates) > 1 else None

    # Caring, empathetic voice synthesis
    exp_note = ""
    if top["expiring_used"]:
        exp_note = f" using your {', '.join(top['expiring_used'])} before it spoils"

    missing_note = ""
    if top["missing_core"]:
        missing_note = f" (you'll just need to grab {top['missing_core'][0]})"

    if max_minutes is not None and max_minutes <= 15:
        msg = f"I hear you — busy days call for quick comfort! In just {top['prep_minutes']} minutes, you can make {top['name']}{exp_note}{missing_note}."
    else:
        msg = f"I recommend making {top['name']} tonight! It takes {top['prep_minutes']} minutes{exp_note}{missing_note}."

    if backup:
        msg += f" Or if you prefer, you can make {backup['name']} in {backup['prep_minutes']} minutes."

    return {
        "suggestions": candidates[:2],
        "top_pick": top,
        "backup_pick": backup,
        "spoken_message": msg
    }


def execute_cooking_deduction(
    ledger: Ledger,
    recipe: dict[str, Any],
    servings_eaten: float,
    idempotency_key: str,
    store: Store | None = None,
    household_id: str | None = None,
) -> dict[str, Any]:
    """Deducts ingredients from ledger and records the meal.
    
    Handles Edge Case E6: Clamps deduction to available stock so stock is never left negative.
    """
    base_servings = float(recipe.get("servings", 1.0))
    scale = servings_eaten / max(0.25, base_servings)

    # 1. Fetch current stock
    stock_rows = ledger.list_items()
    stock_dict = {r["item"].lower().strip(): r for r in stock_rows if r["qty"] > 0}

    ops = []
    deducted_names = []
    used_up_names = []

    for ing in recipe["ingredients"]:
        name = ing["item"].lower().strip()
        role = ing.get("role", "core")
        needed_qty = float(ing.get("qty", 1.0)) * scale
        unit = ing.get("unit", "count")

        # Find in stock
        canon = lookup_canonical(name)
        cid = canon[0] if canon else name

        matched_row = None
        for s_item, row in stock_dict.items():
            s_canon = lookup_canonical(s_item)
            s_cid = s_canon[0] if s_canon else s_item
            if s_cid == cid or s_item == name:
                matched_row = row
                break

        if matched_row:
            current_qty = float(matched_row["qty"])
            # Clamping logic (E6)
            deduct_qty = min(current_qty, needed_qty)
            if deduct_qty > 0:
                ops.append({
                    "type": "consume",
                    "item": matched_row["item"],
                    "qty": deduct_qty,
                    "unit": unit
                })
                deducted_names.append(matched_row["item"])
                if deduct_qty >= current_qty:
                    used_up_names.append(matched_row["item"])

    # Apply batch to ledger if operations exist
    batch_res = None
    if ops:
        batch_res = ledger.apply_batch(ops, idempotency_key=idempotency_key)

    # 2. Compute nutrition
    nutrition = calculate_meal_nutrition(recipe["ingredients"])
    total_kcal = round((nutrition["total_kcal"] / base_servings) * servings_eaten, 1)
    total_protein = round((nutrition["total_protein_g"] / base_servings) * servings_eaten, 1)

    # 3. Insert into logged_meals in DB
    meal_id = str(uuid.uuid4())
    if store and household_id:
        try:
            with store.pool.connection() as conn:
                conn.execute(
                    "INSERT INTO logged_meals (meal_id, household_id, recipe_id, recipe_name, servings, total_kcal, total_protein_g, details) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (meal_id, household_id, recipe.get("id"), recipe["name"], servings_eaten, total_kcal, total_protein,
                     json.dumps({"deducted": deducted_names, "used_up": used_up_names}))
                )
        except Exception:
            pass

    # Spoken feedback
    deduct_text = f"Deducted {', '.join(deducted_names)}." if deducted_names else ""
    used_text = f" Notice: {', '.join(used_up_names)} is now completely used up." if used_up_names else ""
    msg = (f"Bon appétit! Logged {servings_eaten:.1f} serving(s) of {recipe['name']}. "
           f"{deduct_text}{used_text} That adds approximately {total_kcal:.0f} calories and {total_protein:.0f} grams of protein.")

    return {
        "ok": True,
        "meal_id": meal_id,
        "recipe_name": recipe["name"],
        "servings": servings_eaten,
        "total_kcal": total_kcal,
        "total_protein_g": total_protein,
        "deducted_items": deducted_names,
        "used_up_items": used_up_names,
        "spoken_message": msg
    }
