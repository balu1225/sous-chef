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
    ("pasta", "pantry", "mass"),
    ("spaghetti", "pantry", "mass"),
    ("black beans", "pantry", "count"),
    ("crushed tomatoes", "pantry", "count"),
    ("tomatoes", "pantry", "count"),
    ("tomato", "pantry", "count"),
    ("olive oil", "pantry", "volume"),
    ("butter", "fridge", "mass"),
    ("garlic", "pantry", "count"),
    ("onion", "pantry", "count"),
    ("mushrooms", "fridge", "mass"),
    ("mushroom", "fridge", "mass"),
    ("bread", "pantry", "count"),
    ("potatoes", "pantry", "count"),
    ("potato", "pantry", "count"),
    ("yogurt", "fridge", "volume"),
    ("apples", "pantry", "count"),
    ("apple", "pantry", "count"),
    ("bananas", "pantry", "count"),
    ("banana", "pantry", "count"),
]


from dataclasses import dataclass, field



@dataclass
class ParsedItem:
    item: str
    qty: float | None
    unit: str | None
    zone: str
    needs_clarification: bool = False


@dataclass
class ParseResult:
    action: str  # "add", "consume", "discard", "query_all", "query_expiring", "suggest_recipes", "cook_recipe", "check_prep_item", "next_step", "resume_cooking", "query_nutrition", "undo", "unknown"
    items: list[ParsedItem]
    needs_clarification: bool = False
    clarifying_question: str | None = None
    context: dict[str, Any] = field(default_factory=dict)


def parse_kitchen_utterance(text: str) -> ParseResult:
    """Parses a kitchen speech command.

    If an item is detected but lacks a quantity, marks it for clarification.
    """
    clean = text.lower().strip()
    clean = re.sub(r"[^\w\s/.-]", " ", clean)

    # 1. Nutrition Query
    if any(q in clean for q in ["today s nutrition", "todays nutrition", "nutrition today", "how many calories", "how much protein", "nutrition summary"]):
        return ParseResult(action="query_nutrition", items=[])

    # 2. Recipe Suggestions (e.g. "What can I make in 15 minutes?")
    if any(q in clean for q in ["what can i make", "what can i cook", "suggest a recipe", "suggest dinner", "what s for dinner", "what is for dinner", "recipe suggestion", "what should i make", "what can i prepare"]):
        max_min = 15 if any(w in clean for w in ["15 min", "15 minute", "15 minutes", "quick", "busy day", "fast", "rush", "hurry"]) else None
        goal = "quick" if max_min else ("high_protein" if "protein" in clean else ("use_expiring" if any(w in clean for w in ["expir", "spoil"]) else None))
        return ParseResult(action="suggest_recipes", items=[], context={"max_minutes": max_min, "goal": goal})

    # 3. Guided Cooking & Kitchen Media Commands
    if any(q in clean for q in ["play music", "play cooking music", "start music", "cooking music", "play some music", "turn on music", "resume music"]):
        return ParseResult(action="music_control", items=[], context={"state": "play"})

    if any(q in clean for q in ["stop music", "pause music", "turn off music", "stop the music", "quiet"]):
        return ParseResult(action="music_control", items=[], context={"state": "stop"})

    if any(q in clean for q in ["start timer", "start the timer", "run timer", "set timer", "begin timer"]):
        return ParseResult(action="timer_control", items=[], context={"state": "start"})

    if any(q in clean for q in ["stop timer", "pause timer", "cancel timer", "reset timer"]):
        return ParseResult(action="timer_control", items=[], context={"state": "stop"})

    if any(q in clean for q in [
        "i stopped the stove", "stopped the stove", "stopped stove", "stove is stopped",
        "turn off the stove", "stove is off", "turned off the stove", "turned off stove",
        "mixed it", "stirred it", "i stirred", "i mixed", "checked it", "all checked",
        "done with that", "i did it", "all done", "ready to continue", "i am done", "i'm done", "done"
    ]) and not any(q in clean for q in ["i made", "i cooked", "done cooking", "finished cooking"]):
        return ParseResult(action="confirm_action", items=[], context={"confirmed": True})

    if any(q in clean for q in ["where was i", "continue cooking", "resume cooking"]):
        return ParseResult(action="resume_cooking", items=[])

    if any(q in clean for q in ["next step", "what s next", "what is next", "go to next step"]):
        return ParseResult(action="next_step", items=[])

    prep_match = re.search(r"\b(?:i got the|i have the|got the|have the|checked)\s+([a-z\s]+)", clean)
    if prep_match:
        item_text = prep_match.group(1).strip()
        return ParseResult(action="check_prep_item", items=[], context={"checked_item": item_text})

    cook_match = re.search(r"\b(?:i made|i cooked|finished cooking|i m done cooking|i am done cooking)\s*([a-z\s]*)?", clean)
    if cook_match and not any(q in clean for q in ["what can i make", "what should i make", "save"]):
        recipe_name = (cook_match.group(1) or "").strip()
        return ParseResult(action="cook_recipe", items=[], context={"recipe_name": recipe_name})

    save_match = re.search(
        r"\b(?:save (?:this )?(?:recipe )?(?:called |as )|save what i (?:cooked|made) as |save recipe )\s*['\"]?([a-z0-9\s\-_]+?)['\"]?(?:\s+(?:with|having|using)\s+(.+))?$",
        clean
    )
    if save_match:
        recipe_name = save_match.group(1).strip()
        tail = save_match.group(2) or ""
        save_items: list[ParsedItem] = []
        target_text = tail.strip()
        if target_text:
            found_items: list[tuple[int, str, str, str]] = []
            for name, zone, family in KNOWN_ITEMS:
                pattern = r"\b" + re.escape(name) + r"\b"
                match = re.search(pattern, target_text)
                if match:
                    found_items.append((match.start(), name, zone, family))

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

            for i, (start_idx, name, zone, family) in enumerate(filtered_items):
                prev_end = filtered_items[i - 1][0] + len(filtered_items[i - 1][1]) if i > 0 else 0
                context_window = target_text[prev_end:start_idx].strip()
                qty, unit = _extract_qty_and_unit(context_window, target_text[start_idx:])
                save_items.append(ParsedItem(item=name, qty=qty or 1.0, unit=unit or "count", zone=zone))

        return ParseResult(action="save_recipe", items=save_items, context={"recipe_name": recipe_name})

    # 4. Kitchen Mishaps & Funny Culinary Remedies ("Did it wrong")
    if any(q in clean for q in ["burned it", "i burned", "food burned", "burned the", "pan is smoking", "is smoking", "it charred", "burnt", "charred", "smells burnt"]):
        return ParseResult(action="kitchen_mishap", items=[], context={"mishap_type": "burned"})

    if any(q in clean for q in ["too salty", "oversalted", "way too salty", "added too much salt", "dumped salt", "so salty"]):
        return ParseResult(action="kitchen_mishap", items=[], context={"mishap_type": "too_salty"})

    if any(q in clean for q in ["too spicy", "too hot", "mouth is on fire", "mouth on fire", "too much chili", "too much pepper", "burning my tongue"]):
        return ParseResult(action="kitchen_mishap", items=[], context={"mishap_type": "too_spicy"})

    if any(q in clean for q in ["too dry", "meat is dry", "chicken is dry", "overcooked", "like rubber", "shoe leather", "too chewy"]):
        return ParseResult(action="kitchen_mishap", items=[], context={"mishap_type": "too_dry"})

    if any(q in clean for q in ["too watery", "too runny", "sauce is watery", "soup is thin", "diluted", "runny sauce", "sauce is runny"]):
        return ParseResult(action="kitchen_mishap", items=[], context={"mishap_type": "too_watery"})

    if any(q in clean for q in ["too sour", "too acidic", "too much lemon", "too much vinegar", "puckering"]):
        return ParseResult(action="kitchen_mishap", items=[], context={"mishap_type": "too_sour"})

    if any(q in clean for q in ["too sweet", "accidentally added sugar", "tastes like dessert"]):
        return ParseResult(action="kitchen_mishap", items=[], context={"mishap_type": "too_sweet"})

    if any(q in clean for q in ["curdled", "sauce broke", "cream split", "sauce separated", "separated sauce"]):
        return ParseResult(action="kitchen_mishap", items=[], context={"mishap_type": "sauce_curdled"})

    if any(q in clean for q in ["stuck to the pan", "stuck to pan", "eggs stuck", "food is sticking", "pan stuck", "sticking to pan"]):
        return ParseResult(action="kitchen_mishap", items=[], context={"mishap_type": "stuck_to_pan"})

    if any(q in clean for q in ["bland", "tastes like nothing", "no flavor", "tastes like cardboard", "needs flavor"]):
        return ParseResult(action="kitchen_mishap", items=[], context={"mishap_type": "bland"})

    if any(q in clean for q in ["i messed up", "i did it wrong", "help i ruined it", "i made a mistake", "i ruined dinner", "what did i do wrong", "i ruined it", "i did something wrong"]):
        return ParseResult(action="kitchen_mishap", items=[], context={"mishap_type": "general"})

    # 4. Check for Query / Inspection / Undo
    if any(q in clean for q in ["what is about to expire", "what s about to expire", "what is expiring", "what is spoiling"]) and not any(w in clean for w in ["is spoiled", "are spoiled", "went bad", "gone bad", "rotten"]):
        return ParseResult(action="query_expiring", items=[])

    if any(q in clean for q in ["what s in my kitchen", "what is in my kitchen", "what do i have",
                                "what s in the fridge", "what is in the fridge", "list inventory",
                                "kitchen stock", "what is in my"]):
        return ParseResult(action="query_all", items=[])

    if any(q in clean for q in ["undo that", "undo", "revert"]):
        return ParseResult(action="undo", items=[])

    # 5. Detect items mentioned in utterance
    found_items: list[tuple[int, str, str, str]] = []  # (start_idx, item_name, zone, family)
    for name, zone, family in KNOWN_ITEMS:
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

    # 6. Check for Spoiled / Discard intent
    if any(w in clean for w in ["is spoiled", "are spoiled", "spoiled", "went bad", "gone bad", "is rotten", "are rotten", "rotten", "throw away", "throw out", "toss out", "discard", "expired"]):
        # Spoiled items discard entire stock; NO quantity needed!
        return ParseResult(
            action="discard",
            items=[ParsedItem(item=name, qty=None, unit=None, zone=zone, needs_clarification=False)
                   for _, name, zone, _ in filtered_items]
        )

    # 6.1 Check for Relocate / Move zone intent (e.g. "move milk to fridge", "put milk in refrigerator")
    is_move_verb = any(v in clean for v in ["move ", "relocate ", "transfer "])
    is_put_verb = (clean.startswith("put ") or " put " in clean) and not any(w in clean for w in ["left ", "bought", "purchased", "added"])
    has_target_zone = any(z in clean for z in ["fridge", "refrigerator", "freezer", "pantry", "outside", "counter"])

    # If it's "put", ensure there is no explicit quantity phrase (e.g. "put 2 lbs of chicken")
    has_num_or_unit = bool(re.search(r"\b(\d+(\.\d+)?|half|quarter|dozen|two|three|four|five|six|seven|eight|nine|ten)\s*(lbs?|pounds?|gallons?|cups?|oz|ounces?|grams?|kg|liters?|cartons?|bottles?)?\b", clean))
    
    if (is_move_verb or (is_put_verb and not has_num_or_unit)) and has_target_zone:
        target_zone = "fridge"
        if any(z in clean for z in ["freezer", "freeze", "frozen"]):
            target_zone = "freezer"
        elif any(z in clean for z in ["pantry", "outside", "counter", "cupboard", "cabinet", "room temp"]):
            target_zone = "pantry"
        elif any(z in clean for z in ["fridge", "refrigerator", "cooler"]):
            target_zone = "fridge"

        return ParseResult(
            action="move_zone",
            items=[ParsedItem(item=name, qty=None, unit=None, zone=target_zone, needs_clarification=False)
                   for _, name, _, _ in filtered_items],
            context={"target_zone": target_zone}
        )

    # 7. Action Intent: consume vs add
    action = "add"
    if any(w in clean for w in ["used", "ate", "consumed", "finished"]):
        action = "consume"

    # Check if user explicitly mentioned a zone when adding/storing items
    detected_zone = None
    if any(z in clean for z in ["in the freezer", "in freezer", "into freezer", "to freezer", "frozen"]):
        detected_zone = "freezer"
    elif any(z in clean for z in ["in the pantry", "in pantry", "into pantry", "outside", "on the counter", "on counter", "room temp", "cabinet", "cupboard"]):
        detected_zone = "pantry"
    elif any(z in clean for z in ["in the fridge", "in fridge", "into fridge", "to fridge", "in refrigerator", "into refrigerator"]):
        detected_zone = "fridge"

    parsed_items: list[ParsedItem] = []
    unspecified_items: list[str] = []

    for i, (start_idx, name, zone, family) in enumerate(filtered_items):
        item_zone = detected_zone or zone
        # Look at the substring preceding this item up to the previous item
        prev_end = filtered_items[i - 1][0] + len(filtered_items[i - 1][1]) if i > 0 else 0
        context_window = clean[prev_end:start_idx].strip()

        qty, unit = _extract_qty_and_unit(context_window, clean[start_idx:])

        if qty is None:
            # Quantity was NOT found! Mark for clarification.
            parsed_items.append(ParsedItem(item=name, qty=None, unit=None, zone=item_zone, needs_clarification=True))
            unspecified_items.append(name)
        else:
            parsed_items.append(ParsedItem(item=name, qty=qty, unit=unit, zone=item_zone, needs_clarification=False))

    ctx = {"zone": detected_zone} if detected_zone else {}

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
            context=ctx,
        )

    return ParseResult(action=action, items=parsed_items, needs_clarification=False, context=ctx)


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
