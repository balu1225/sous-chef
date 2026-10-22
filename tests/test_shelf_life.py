import pytest
from datetime import datetime, timezone, timedelta
from sous_chef.shelf_life import (
    calculate_shelf_life,
    resolve_fifo_expiry,
    generate_duplicate_batch_advisory,
    HIGH_PERISHABLE_ITEMS,
)

def test_shelf_life_perishable_outside_vs_fridge():
    # Milk outside has 24h shelf life and spoilage warning
    expires_outside, is_outside, warning_outside = calculate_shelf_life("milk", "pantry")
    now = datetime.now(timezone.utc)
    assert (expires_outside - now).total_seconds() <= 86400 + 60
    assert is_outside is True
    assert warning_outside is not None
    assert "left outside" in warning_outside.lower() or "fridge" in warning_outside.lower()

    # Milk in fridge has 7-day shelf life and no warning
    expires_fridge, is_fridge, warning_fridge = calculate_shelf_life("milk", "fridge")
    assert (expires_fridge - now).days >= 6
    assert is_fridge is False
    assert warning_fridge is None

    # Milk in freezer has 90-day shelf life
    expires_freezer, is_freezer, warning_freezer = calculate_shelf_life("milk", "freezer")
    assert (expires_freezer - now).days >= 89
    assert is_freezer is False

def test_fifo_resolution():
    now = datetime.now(timezone.utc)
    t_early = now + timedelta(days=1)
    t_late = now + timedelta(days=7)

    # When new batch has later expiry, keep earlier
    assert resolve_fifo_expiry(t_early, t_late) == t_early

    # When new batch has earlier expiry, use new earlier
    assert resolve_fifo_expiry(t_late, t_early) == t_early

    # String format handling
    assert resolve_fifo_expiry(t_early.isoformat(), t_late.isoformat()) == t_early

    # None handling
    assert resolve_fifo_expiry(t_early, None) == t_early
    assert resolve_fifo_expiry(None, t_late) == t_late

def test_duplicate_batch_advisory():
    now = datetime.now(timezone.utc)
    expiring_soon = now + timedelta(hours=36)

    advisory = generate_duplicate_batch_advisory(
        item="milk",
        existing_qty=1.0,
        existing_unit="gallons",
        existing_expiry=expiring_soon,
        new_zone="fridge",
        existing_zone="fridge"
    )
    assert advisory is not None
    assert "older batch first" in advisory.lower()
    assert "48 hours" in advisory

    # If existing batch was outside in pantry
    advisory_outside = generate_duplicate_batch_advisory(
        item="milk",
        existing_qty=1.0,
        existing_unit="gallons",
        existing_expiry=expiring_soon,
        new_zone="fridge",
        existing_zone="pantry"
    )
    assert "pantry outside" in advisory_outside
    assert "refrigerate or use that older batch" in advisory_outside
