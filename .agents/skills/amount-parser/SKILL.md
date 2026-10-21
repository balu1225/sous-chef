---
name: amount-parser
description: Rule-based parsing of spoken kitchen quantities, base-unit conversions, display formatting, and ambiguity resolution.
---

# Spoken Amount Parser Engineering Standard

## 1. Principles
1. **Deterministic Rule-Based Logic:** Plain code handles parsing and math. LLMs are never used for arithmetic or unit conversion.
2. **Base Unit Normalization:** Convert all spoken inputs into `count`, `g`, or `ml`.
3. **Spoken-Friendly Readback:** Never read raw base units back to voice users (e.g., convert `3785.41 ml` back to "1 gallon of milk").

## 2. Spoken Fraction & Colloquial Quantities Table

| Spoken Phrase | Parsed Number | Canonical Base Unit |
|---|---|---|
| "a couple" / "a couple of" | 2.0 | count |
| "a few" | 3.0 | count |
| "a dozen" | 12.0 | count |
| "half a dozen" | 6.0 | count |
| "half" / "half of" | 0.5 | (contextual or count) |
| "a quarter" / "a fourth" | 0.25 | (contextual or count) |
| "1 and a half" / "one and a half" | 1.5 | - |
| "a pinch" | 0.5 | g |
| "a bunch" / "a head" | 1.0 | count |

## 3. Unit Conversion Ratios to Base Units

### Volume (Base Unit: `ml`)
- `tsp` / `teaspoon`: `4.9289 ml`
- `tbsp` / `tablespoon`: `14.7868 ml`
- `fl oz` / `fluid ounce`: `29.5735 ml`
- `cup`: `236.588 ml`
- `pint`: `473.176 ml`
- `quart`: `946.353 ml`
- `gallon`: `3785.41 ml`
- `liter` / `l`: `1000.0 ml`
- `ml` / `milliliter`: `1.0 ml`

### Mass (Base Unit: `g`)
- `oz` / `ounce`: `28.3495 g`
- `lb` / `pound`: `453.592 g`
- `kg` / `kilogram`: `1000.0 g`
- `g` / `gram`: `1.0 g`

### Count (Base Unit: `count`)
- `item`, `piece`, `egg`, `slice`, `can`, `bottle`, `pack`: `1.0 count`

## 4. Ambiguity Resolution (Single Clarifying Question)
When a user provides an item with no quantity or an ambiguous relative phrase without prior context:
- *User:* "I bought milk."
- *Clarification rule:* If quantity is missing, DO NOT guess. Return a structured clarification request:
  ```json
  {
    "ok": false,
    "needs_clarification": true,
    "question": "How much milk did you buy?",
    "item": "milk"
  }
  ```
- *Rule:* Only **one** clarifying question is allowed per turn to prevent voice interrogation fatigue.

## 5. Spoken Readback Formatter
When reading inventory or meal deductions back over TTS:
```python
def format_spoken_quantity(amount: float, unit: str, item_name: str) -> str:
    """Formats raw base units into natural spoken language."""
    if unit == "ml":
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
        return f"{int(amount) if amount.is_integer() else amount} {item_name}"
    return f"{amount} {unit} of {item_name}"
```

## 6. Implementation Checklist
- [ ] Regex patterns for mixed fractions (e.g., `(\d+)\s+and\s+a\s+half`).
- [ ] Mappings for colloquial quantities (`couple`, `few`, `dozen`).
- [ ] Strict rejection when mixing unit families (e.g. `g` + `ml`).
- [ ] Formatter verified against golden set spoken expectations.
