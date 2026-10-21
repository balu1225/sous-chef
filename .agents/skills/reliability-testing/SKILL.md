---
name: reliability-testing
description: Pytest harness, contract test fixtures, synthetic DB outage simulators, and the 25-phrase golden set for Sous-Chef.
---

# Reliability & Golden Set Testing Engineering Standard

## 1. Testing Philosophy (Reliability #1)
- Never ship a tool without an automated contract test.
- Every test must verify the uniform error envelope: no unhandled exceptions or raw SQL ever escape.
- Fast execution: Full test suite must complete in $< 10$ seconds locally.

## 2. Pytest Fixture Architecture (`tests/conftest.py`)
```python
import pytest
import psycopg2
from sous_chef.ledger import Store

@pytest.fixture(scope="session")
def db_connection():
    """Provides a connection to local test postgres with UTC session."""
    conn = psycopg2.connect("dbname=sous_chef_test user=postgres host=localhost port=5432")
    with conn.cursor() as cur:
        cur.execute("SET TIME ZONE 'UTC';")
        cur.execute("SET statement_timeout = 2500;")
    yield conn
    conn.close()

@pytest.fixture
def clean_store(db_connection):
    """Wraps each test in a rolled-back transaction to keep test runs isolated."""
    db_connection.autocommit = False
    store = Store(db_connection)
    yield store
    db_connection.rollback()
```

## 3. Synthetic DB Outage & Timeout Test
Verify Decision D4 (hard 4.0s timeout and worker thread non-blocking behavior):
```python
import time
import pytest
from unittest.mock import patch
from sous_chef.server import call_tool_safe

def test_hard_timeout_returns_spoken_error():
    """Verify that a hanging DB query aborts in <= 4.0s and returns a safe voice envelope."""
    def mock_hanging_query(*args, **kwargs):
        time.sleep(6.0)
        return {"items": []}

    start = time.time()
    result = call_tool_safe(mock_hanging_query, timeout_seconds=4.0)
    elapsed = time.time() - start

    assert elapsed < 4.5, f"Timeout took too long: {elapsed}s"
    assert result["ok"] is False
    assert result["error"]["code"] == "db_timeout"
    assert result["error"]["retryable"] is True
```

## 4. The 25-Phrase Golden Test Set

| # | Spoken Input Phrase | Expected Tool Call | Expected Invariant / Outcome |
|---|---|---|---|
| 1 | "I bought 2 gallons of whole milk." | `manage_inventory` (add) | Adds 7570.82 ml of `milk_whole` to projection. |
| 2 | "I just got a dozen eggs and a bunch of spinach." | `manage_inventory` (batch add) | Adds 12 count eggs and 1 count spinach in one atomic batch. |
| 3 | "What's in my kitchen?" | `query_inventory` | Returns all positive inventory items formatted with spoken units. |
| 4 | "What is about to expire?" | `query_inventory` (expiring_days=2) | Returns only items with `expires_at <= NOW() + 48h`. |
| 5 | "Undo that." | `undo_last_change` | Appends compensating event; reverses last batch exactly. |
| 6 | "I used half a cup of milk." | `manage_inventory` (use) | Deducts 118.29 ml from milk stock. |
| 7 | "I bought chicken." | `amount-parser` (clarification) | Prompts: "How much chicken did you buy?" |
| 8 | "1 and a half pounds." | `manage_inventory` (add) | Resolves prior chicken prompt; adds 680.39 g chicken breast. |
| 9 | "What can I make for dinner?" | `suggest_recipes` | Ranks recipes prioritizing items expiring within 48h. |
| 10 | "Can I make Grandma's Chili?" | `suggest_recipes` (specific) | Checks required ingredients and reports missing items if any. |
| 11 | "I made Grandma's Chili, 2 servings." | `cook_recipe` | Deducts scaled ingredients; logs meal with calories and protein. |
| 12 | "How many calories today?" | `nutrition_summary` | Returns aggregated kcal and protein for today. |
| 13 | "I bought a couple of apples." | `manage_inventory` (add) | Adds 2 count apples. |
| 14 | "I used the rest of the spinach." | `manage_inventory` (use all) | Deducts full remaining spinach quantity to 0.0. |
| 15 | "I used 10 gallons of milk." | `manage_inventory` (deduct) | Returns error: `insufficient_stock`. |
| 16 | "I bought 500 grams of cheddar cheese." | `manage_inventory` (add) | Adds 500.0 g cheddar. |
| 17 | "Save recipe: Quick Rice Bowl." | `save_custom_recipe` | Saves custom family recipe to database. |
| 18 | "What's spoiling this week?" | `query_inventory` (expiring_days=7) | Returns items expiring in next 7 days. |
| 19 | "I bought a pinch of salt." | `manage_inventory` (add) | Adds 0.5 g salt. |
| 20 | "I made 4 servings of Cheesy Rice." | `cook_recipe` | Deducts scaled rice, beans, cheddar. |
| 21 | "How much protein did I have today?" | `nutrition_summary` | Returns spoken protein breakdown. |
| 22 | "Undo." | `undo_last_change` | Reverses Cheesy Rice meal deduction. |
| 23 | "Repeat last action." | `idempotency check` | Returns identical previous response with no duplicate rows. |
| 24 | "Simulate database offline." | `health_check` | Returns HTTP 503 degraded without crash loops. |
| 25 | "What's in the fridge?" | `query_inventory` (location=fridge) | Filters items stored in refrigerator. |

## 5. Implementation Checklist
- [ ] Pytest runner executes all unit and contract tests in `tests/`.
- [ ] Golden set test runner checks all 25 phrases against mock responses.
- [ ] Synthetic DB timeout test passes reliably under 4.5 seconds.
