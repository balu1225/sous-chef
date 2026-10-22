"""Sous-Chef Smart Perishability, Zone-Aware Shelf Life, and FIFO Duplicate Engine.

Handles:
1. Dynamic shelf-life calculation based on item category and storage zone (Fridge, Pantry, Freezer).
2. Accelerated spoilage warnings for perishables left outside the refrigerator (e.g., milk/meat at room temp).
3. FIFO (First-In, First-Out) duplicate batch preservation: earlier expiring stock is NEVER masked by a new purchase.
4. Smart advisories alerting the household when an existing older batch needs to be consumed first.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


# --------------------------------------------------------------------------
# Perishable Categories & Shelf Life Durations (in days)
# --------------------------------------------------------------------------

SHELF_LIFE_DAYS: dict[str, dict[str, int]] = {
    # Dairy
    "whole milk": {"fridge": 7, "pantry": 1, "freezer": 90},
    "milk": {"fridge": 7, "pantry": 1, "freezer": 90},
    "oat milk": {"fridge": 10, "pantry": 1, "freezer": 60},
    "almond milk": {"fridge": 10, "pantry": 1, "freezer": 60},
    "cream": {"fridge": 7, "pantry": 1, "freezer": 60},
    "yogurt": {"fridge": 14, "pantry": 1, "freezer": 60},
    "cheddar cheese": {"fridge": 28, "pantry": 2, "freezer": 180},
    "cheddar": {"fridge": 28, "pantry": 2, "freezer": 180},
    "cheese": {"fridge": 21, "pantry": 2, "freezer": 180},
    "butter": {"fridge": 60, "pantry": 7, "freezer": 180},

    # Meat & Seafood (Critical spoilage danger outside!)
    "chicken breast": {"fridge": 2, "pantry": 1, "freezer": 180},
    "chicken": {"fridge": 2, "pantry": 1, "freezer": 180},
    "ground beef": {"fridge": 2, "pantry": 1, "freezer": 120},
    "beef": {"fridge": 4, "pantry": 1, "freezer": 180},
    "fish": {"fridge": 2, "pantry": 1, "freezer": 90},
    "salmon": {"fridge": 2, "pantry": 1, "freezer": 90},
    "pork": {"fridge": 3, "pantry": 1, "freezer": 180},
    "turkey": {"fridge": 2, "pantry": 1, "freezer": 180},

    # Eggs
    "eggs": {"fridge": 21, "pantry": 2, "freezer": 90},
    "egg": {"fridge": 21, "pantry": 2, "freezer": 90},

    # Delicate Produce & Greens
    "baby spinach": {"fridge": 5, "pantry": 1, "freezer": 60},
    "fresh spinach": {"fridge": 5, "pantry": 1, "freezer": 60},
    "spinach": {"fridge": 5, "pantry": 1, "freezer": 60},
    "mushrooms": {"fridge": 7, "pantry": 2, "freezer": 90},
    "mushroom": {"fridge": 7, "pantry": 2, "freezer": 90},
    "berries": {"fridge": 5, "pantry": 1, "freezer": 180},
    "strawberries": {"fridge": 4, "pantry": 1, "freezer": 180},

    # Bakery & Produce
    "bread": {"pantry": 7, "fridge": 14, "freezer": 90},
    "bananas": {"pantry": 5, "fridge": 7, "freezer": 90},
    "banana": {"pantry": 5, "fridge": 7, "freezer": 90},
    "apples": {"pantry": 14, "fridge": 30, "freezer": 180},
    "apple": {"pantry": 14, "fridge": 30, "freezer": 180},
    "potatoes": {"pantry": 45, "fridge": 30, "freezer": 180},
    "potato": {"pantry": 45, "fridge": 30, "freezer": 180},
    "onion": {"pantry": 45, "fridge": 30, "freezer": 180},
    "garlic": {"pantry": 60, "fridge": 30, "freezer": 180},
    "tomatoes": {"pantry": 7, "fridge": 12, "freezer": 180},
    "tomato": {"pantry": 7, "fridge": 12, "freezer": 180},

    # Dry Pantry Staples (Low spoilage risk)
    "white rice": {"pantry": 365, "fridge": 365, "freezer": 365},
    "rice": {"pantry": 365, "fridge": 365, "freezer": 365},
    "pasta": {"pantry": 365, "fridge": 365, "freezer": 365},
    "spaghetti": {"pantry": 365, "fridge": 365, "freezer": 365},
    "black beans": {"pantry": 365, "fridge": 365, "freezer": 365},
    "crushed tomatoes": {"pantry": 365, "fridge": 365, "freezer": 365},
    "olive oil": {"pantry": 365, "fridge": 365, "freezer": 365},
}

# Items that are highly perishable and dangerous if kept at room temperature
HIGH_PERISHABLE_ITEMS = frozenset({
    "milk", "whole milk", "oat milk", "almond milk", "cream", "yogurt",
    "chicken", "chicken breast", "ground beef", "beef", "fish", "salmon",
    "pork", "turkey", "baby spinach", "fresh spinach", "spinach", "berries", "strawberries"
})


def calculate_shelf_life(item: str, zone: str | None = None) -> tuple[datetime, bool, str | None]:
    """Calculates the expiration datetime for an item based on its storage zone.

    Returns:
        (expires_at, is_perishable_outside, advisory_warning)
    """
    clean_item = item.lower().strip()
    clean_zone = (zone or "pantry").lower().strip()

    # Normalize zone names
    if "fridge" in clean_zone or "refrigerator" in clean_zone:
        target_zone = "fridge"
    elif "freezer" in clean_zone or "frozen" in clean_zone:
        target_zone = "freezer"
    else:
        target_zone = "pantry"

    # Lookup shelf life days
    item_days = SHELF_LIFE_DAYS.get(clean_item, {})
    days = item_days.get(target_zone)

    if days is None:
        # Generic fallbacks
        if clean_item in HIGH_PERISHABLE_ITEMS:
            days = 1 if target_zone == "pantry" else (7 if target_zone == "fridge" else 90)
        else:
            days = 365 if target_zone == "pantry" else 30

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=days)

    is_perishable_outside = False
    warning = None

    if clean_item in HIGH_PERISHABLE_ITEMS and target_zone == "pantry":
        is_perishable_outside = True
        warning = (
            f"Heads up! {item.title()} spoils very quickly if left outside the refrigerator! "
            f"I've set its shelf-life to 24 hours. Please move it to the fridge as soon as possible."
        )

    return expires_at, is_perishable_outside, warning


def resolve_fifo_expiry(
    existing_expiry: datetime | str | None,
    new_expiry: datetime | str | None
) -> datetime | None:
    """Implements First-In, First-Out (FIFO) batch expiration resolution.

    Ensures that adding a newly purchased batch does not mask or overwrite
    an older batch that is expiring sooner!
    """
    dt_existing = None
    if isinstance(existing_expiry, str):
        try:
            dt_existing = datetime.fromisoformat(existing_expiry)
        except Exception:
            dt_existing = None
    elif isinstance(existing_expiry, datetime):
        dt_existing = existing_expiry

    dt_new = None
    if isinstance(new_expiry, str):
        try:
            dt_new = datetime.fromisoformat(new_expiry)
        except Exception:
            dt_new = None
    elif isinstance(new_expiry, datetime):
        dt_new = new_expiry

    if dt_existing and dt_new:
        # Preserve whichever expires first (FIFO)
        return min(dt_existing, dt_new)
    return dt_existing or dt_new


def generate_duplicate_batch_advisory(
    item: str,
    existing_qty: float,
    existing_unit: str,
    existing_expiry: datetime | str | None,
    new_zone: str,
    existing_zone: str | None = None
) -> str | None:
    """Generates an intelligent spoken advisory when a user adds an item

    that is already tracked in stock, alerting them to older expiring batches.
    """
    if existing_qty <= 0:
        return None

    dt_existing = None
    if isinstance(existing_expiry, str):
        try:
            dt_existing = datetime.fromisoformat(existing_expiry)
        except Exception:
            pass
    elif isinstance(existing_expiry, datetime):
        dt_existing = existing_expiry

    now = datetime.now(timezone.utc)

    # Check if existing batch is in the pantry (outside) while item is perishable
    if existing_zone == "pantry" and item.lower() in HIGH_PERISHABLE_ITEMS:
        return (
            f"Note: You already have {existing_qty:.0f} {existing_unit} of {item} in the pantry outside. "
            f"Remember to refrigerate or use that older batch first before it spoils!"
        )

    if dt_existing:
        diff_hours = (dt_existing - now).total_seconds() / 3600.0
        if diff_hours <= 48:
            return (
                f"Note: You already have {existing_qty:.0f} {existing_unit} of {item} expiring within 48 hours. "
                f"Be sure to use that older batch first!"
            )
        elif diff_hours <= 120:
            diff_days = max(1, int(diff_hours // 24))
            return (
                f"Note: You already have {existing_qty:.0f} {existing_unit} of {item} expiring in {diff_days} days. "
                f"Use the older batch first!"
            )

    return f"Added to your existing {item} in stock."
