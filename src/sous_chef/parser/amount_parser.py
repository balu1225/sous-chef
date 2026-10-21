"""Rule-based kitchen amount parser.

Strict rule: NEVER guess quantities. If an item is mentioned without an amount,
trigger a single clarifying question.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

# Number words and colloquial quantities
NUM_WORDS: dict[str, float] = {
    "a": 1.0,
    "an": 1.0,
    "one": 1.0,
    "two": 2.0,
    "three": 3.0,
    "four": 4.0,
    "five": 5.0,
    "six": 6.0,
    "seven": 7.0,
    "eight": 8.0,
    "nine": 9.0,
    "ten": 10.0,
    "eleven": 11.0,
    "twelve": 12.0,
    "a couple": 2.0,
    "couple": 2.0,
    "a few": 3.0,
    "few": 3.0,
    "a dozen": 12.0,
    "dozen": 12.0,
    "half a dozen": 6.0,
    "half dozen": 6.0,
    "a pinch": 0.5,
    "pinch": 0.5,
    "a bunch": 1.0,
    "bunch": 1.0,
    "a head": 1.0,
    "head": 1.0,
}

# Unit mappings -> (canonical family, factor to base unit)
UNIT_TABLE: dict[str, tuple[str, float]] = {
    # Volume (base: ml)
    "gallon": ("volume", 3785.41),
    "gallons": ("volume", 3785.41),
    "gal": ("volume", 3785.41),
    "quart": ("volume", 946.353),
    "quarts": ("volume", 946.353),
    "qt": ("volume", 946.353),
    "pint": ("volume", 473.176),
    "pints": ("volume", 473.176),
    "pt": ("volume", 473.176),
    "cup": ("volume", 236.588),
    "cups": ("volume", 236.588),
    "tablespoon": ("volume", 14.7868),
    "tablespoons": ("volume", 14.7868),
    "tbsp": ("volume", 14.7868),
    "teaspoon": ("volume", 4.9289),
    "teaspoons": ("volume", 4.9289),
    "tsp": ("volume", 4.9289),
    "fl oz": ("volume", 29.5735),
    "fluid ounce": ("volume", 29.5735),
    "fluid ounces": ("volume", 29.5735),
    "liter": ("volume", 1000.0),
    "liters": ("volume", 1000.0),
    "l": ("volume", 1000.0),
    "ml": ("volume", 1.0),
    "milliliter": ("volume", 1.0),
    "milliliters": ("volume", 1.0),

    # Mass (base: g)
    "pound": ("mass", 453.592),
    "pounds": ("mass", 453.592),
    "lb": ("mass", 453.592),
    "lbs": ("mass", 453.592),
    "ounce": ("mass", 28.3495),
    "ounces": ("mass", 28.3495),
    "oz": ("mass", 28.3495),
    "kilogram": ("mass", 1000.0),
    "kilograms": ("mass", 1000.0),
    "kg": ("mass", 1000.0),
    "gram": ("mass", 1.0),
    "grams": ("mass", 1.0),
    "g": ("mass", 1.0),

    # Count (base: count)
    "count": ("count", 1.0),
    "item": ("count", 1.0),
    "items": ("count", 1.0),
    "piece": ("count", 1.0),
    "pieces": ("count", 1.0),
    "slice": ("count", 1.0),
    "slices": ("count", 1.0),
    "can": ("count", 1.0),
    "cans": ("count", 1.0),
    "bottle": ("count", 1.0),
    "bottles": ("count", 1.0),
    "carton": ("count", 1.0),
    "cartons": ("count", 1.0),
}

# Known pantry/fridge staples
KNOWN_ITEMS = [
    ("whole milk", "fridge", "volume"),
    ("milk", "fridge", "volume"),
    ("eggs", "fridge", "count"),
    ("egg", "fridge", "count"),
    ("baby spinach", "fridge", "mass"),
    ("fresh spinach", "fridge", "mass"),
    ("spinach", "fridge", "mass"),
    ("chicken breast", "fridge", "mass"),
    ("chicken", "fridge", "mass"),
    ("ground beef", "fridge", "mass"),
    ("beef", "fridge", "mass"),
    ("cheddar cheese", "fridge", "mass"),
    ("cheddar", "fridge", "mass"),
    ("cheese", "fridge", "mass"),
    ("white rice", "pantry", "mass"),
    ("rice", "pantry", "mass"),
    ("black beans", "pantry", "count"),
    ("crushed tomatoes", "pantry", "count"),
    ("olive oil", "pantry", "volume"),
    ("butter", "fridge", "mass"),
    ("apples", "pantry", "count"),
    ("apple", "pantry", "count"),
    ("bananas", "pantry", "count"),
    ("banana", "pantry", "count"),
]


@dataclass
class ParsedItem:
    item: str
    qty: float | None
    unit: str | None
    zone: str
    needs_clarification: bool = False


@dataclass
class ParseResult:
    action: str  # "add", "consume", "query", "undo", "unknown"
    items: list[ParsedItem]
    needs_clarification: bool = False
    clarifying_question: str | None = None


def parse_kitchen_utterance(text: str) -> ParseResult:
    """Parses a kitchen speech command.

    If an item is detected but lacks a quantity, marks it for clarification.
    """
    clean = text.lower().strip()
    clean = re.sub(r"[^\w\s/.-]", " ", clean)

    # 1. Check for Query / Inspection
    if any(q in clean for q in ["what is about to expire", "what s about to expire", "expiring", "spoil"]):
        return ParseResult(action="query_expiring", items=[])

    if any(q in clean for q in ["what s in my kitchen", "what is in my kitchen", "what do i have",
                                "what s in the fridge", "what is in the fridge", "list inventory",
                                "kitchen stock", "what is in my"]):
        return ParseResult(action="query_all", items=[])

    if any(q in clean for q in ["undo that", "undo", "revert"]):
        return ParseResult(action="undo", items=[])

    # 2. Determine Action Intent (add vs consume)
    action = "add"
    if any(w in clean for w in ["used", "ate", "consumed", "finished", "cooked", "threw out", "discarded"]):
        action = "consume"

    # 3. Detect items mentioned in utterance
    found_items: list[tuple[int, str, str, str]] = []  # (start_idx, item_name, zone, family)
    for name, zone, family in KNOWN_ITEMS:
        # Match as whole word phrase
        pattern = r"\b" + re.escape(name) + r"\b"
        match = re.search(pattern, clean)
        if match:
            found_items.append((match.start(), name, zone, family))

    # Remove sub-matches (e.g. if 'whole milk' matched, remove 'milk')
    filtered_items: list[tuple[int, str, str, str]] = []
    found_items.sort(key=lambda x: (x[0], -len(x[1])))
    covered_ranges: list[tuple[int, int]] = []

    for start, name, zone, family in found_items:
        end = start + len(name)
        if any(cs <= start and end <= ce for cs, ce in covered_ranges):
            continue
        covered_ranges.append((start, end))
        filtered_items.append((start, name, zone, family))

    filtered_items.sort(key=lambda x: x[0])

    if not filtered_items:
        return ParseResult(action="unknown", items=[])

    parsed_items: list[ParsedItem] = []
    unspecified_items: list[str] = []

    for i, (start_idx, name, zone, family) in enumerate(filtered_items):
        # Look at the substring preceding this item up to the previous item
        prev_end = filtered_items[i - 1][0] + len(filtered_items[i - 1][1]) if i > 0 else 0
        context_window = clean[prev_end:start_idx].strip()

        qty, unit = _extract_qty_and_unit(context_window, clean[start_idx:])

        if qty is None:
            # Quantity was NOT found! Mark for clarification.
            parsed_items.append(ParsedItem(item=name, qty=None, unit=None, zone=zone, needs_clarification=True))
            unspecified_items.append(name)
        else:
            parsed_items.append(ParsedItem(item=name, qty=qty, unit=unit, zone=zone, needs_clarification=False))

    # If any items lack quantity, formulate a single polite clarifying question
    if unspecified_items:
        if len(unspecified_items) == 1:
            q = f"How much {unspecified_items[0]} did you {action}?"
            if unspecified_items[0] in ("eggs", "apples", "bananas"):
                q = f"How many {unspecified_items[0]} did you {action}?"
        else:
            items_str = " and ".join(unspecified_items)
            q = f"How much of the {items_str} did you {action}?"

        return ParseResult(
            action=action,
            items=parsed_items,
            needs_clarification=True,
            clarifying_question=q,
        )

    return ParseResult(action=action, items=parsed_items, needs_clarification=False)


def _extract_qty_and_unit(pre_text: str, post_text: str) -> tuple[float | None, str | None]:
    """Finds quantity numbers and units from the surrounding text."""
    combined = pre_text + " "

    # 1. Check for mixed fractions like "1 and a half" or "2 1/2"
    mixed_frac = re.search(r"(\d+)\s+and\s+(a\s+)?(half|quarter|fourth)", combined)
    if mixed_frac:
        whole = float(mixed_frac.group(1))
        frac = 0.5 if "half" in mixed_frac.group(3) else 0.25
        return whole + frac, _find_unit(combined)

    num_match = re.search(r"(\d+(\.\d+)?)", combined)
    qty: float | None = None
    if num_match:
        qty = float(num_match.group(1))
    else:
        # Check written number words sorted by descending length (e.g. "a dozen" before "a")
        for word in sorted(NUM_WORDS.keys(), key=len, reverse=True):
            pattern = r"\b" + re.escape(word) + r"\b"
            if re.search(pattern, combined):
                qty = NUM_WORDS[word]
                break

    if qty is None:
        return None, None

    unit = _find_unit(combined)
    return qty, unit or "count"


def _find_unit(text: str) -> str | None:
    for unit in UNIT_TABLE:
        pattern = r"\b" + re.escape(unit) + r"\b"
        if re.search(pattern, text):
            return unit
    return None


def format_spoken_quantity(amount: float, unit: str, item_name: str) -> str:
    """Formats raw base units into natural spoken language."""
    if unit == "ml":
        if abs(amount - 7570.82) < 100:
            return f"2 gallons of {item_name}"
        if abs(amount - 3785.41) < 100:
            return f"1 gallon of {item_name}"
        if abs(amount - 946.35) < 50:
            return f"1 quart of {item_name}"
        if abs(amount - 236.59) < 20:
            return f"1 cup of {item_name}"
        return f"{int(amount)} milliliters of {item_name}"
    elif unit == "g":
        if abs(amount - 453.59) < 20:
            return f"1 pound of {item_name}"
        if amount >= 1000:
            return f"{amount/1000:.1f} kilograms of {item_name}"
        return f"{int(amount)} grams of {item_name}"
    elif unit == "count":
        val = int(amount) if amount.is_integer() else amount
        return f"{val} {item_name}"
    return f"{amount} {unit} of {item_name}"
