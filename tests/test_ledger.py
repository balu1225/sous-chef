"""Run against a real Postgres:
    KITCHEN_TEST_DSN="postgresql://user:pass@localhost:5432/kitchen_test" pytest -q
The test database is wiped on every test.
"""
import os
import threading

import psycopg
import pytest

from ledger import LedgerError, Store

DSN = os.environ.get("KITCHEN_TEST_DSN",
                     "host=/tmp port=5433 user=postgres dbname=kitchen")


@pytest.fixture
def store():
    with psycopg.connect(DSN, autocommit=True) as conn:
        conn.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
    s = Store(DSN, max_size=8)
    s.migrate()
    yield s
    s.close()


@pytest.fixture
def led(store):
    return store.ledger("h1")


def groceries(led, key="k1"):
    return led.apply_batch([
        {"type": "add", "item": "Milk", "qty": 2, "unit": "gallons", "zone": "fridge"},
        {"type": "add", "item": "eggs", "qty": 6, "unit": "count", "zone": "fridge"},
        {"type": "add", "item": "spinach", "qty": 1, "unit": "lb", "zone": "fridge",
         "expires_at": "2026-10-20T00:00:00+00:00"},
    ], idempotency_key=key)


def test_multi_item_batch_and_unit_conversion(led):
    groceries(led)
    assert led.get("milk")["qty"] == pytest.approx(7570.82)
    assert led.get("milk")["unit"] == "ml"
    assert led.get("EGGS")["qty"] == 6
    assert led.get("spinach")["expires_at"].startswith("2026-10-20")
    assert len(led.list_items()) == 3


def test_exact_decimal_math(led):
    for i in range(10):
        led.apply_batch([{"type": "add", "item": "flour", "qty": "0.1", "unit": "kg"}],
                        f"f{i}")
    assert led.get("flour")["qty"] == 1000.0


def test_retry_with_same_key_does_not_double_apply(led):
    first = groceries(led)
    second = groceries(led)
    assert second["replayed"] is True
    assert second["batch_id"] == first["batch_id"]
    assert led.get("eggs")["qty"] == 6


def test_failed_op_rolls_back_whole_batch(led):
    groceries(led)
    with pytest.raises(LedgerError, match="Only 4"):
        led.apply_batch([
            {"type": "consume", "item": "eggs", "qty": 2},
            {"type": "consume", "item": "eggs", "qty": 10},
        ], idempotency_key="k2")
    assert led.get("eggs")["qty"] == 6
    led.apply_batch([{"type": "consume", "item": "eggs", "qty": 2}], "k2")
    assert led.get("eggs")["qty"] == 4


def test_validation(led):
    groceries(led)
    for i, bad in enumerate((
            {"type": "add", "item": "rice", "qty": -1, "unit": "g"},
            {"type": "add", "item": "rice", "qty": "lots", "unit": "g"},
            {"type": "add", "item": "rice", "qty": "NaN", "unit": "g"},
            {"type": "add", "item": "rice", "qty": 1, "unit": "bushel"},
            {"type": "add", "item": "", "qty": 1},
            {"type": "explode", "item": "rice", "qty": 1},
            {"type": "add", "item": "milk", "qty": 1, "unit": "lb"},
            {"type": "add", "item": "rice", "qty": 1, "unit": "g",
             "expires_at": "next tuesday"})):
        with pytest.raises(LedgerError):
            led.apply_batch([bad], idempotency_key=f"bad-{i}")
    with pytest.raises(LedgerError):
        led.apply_batch([{"type": "add", "item": "rice", "qty": 1}], "")


def test_undo_last_utterance(led):
    groceries(led)
    led.apply_batch([{"type": "consume", "item": "eggs", "qty": 2},
                     {"type": "add", "item": "rice", "qty": 500, "unit": "g"}], "k2")
    res = led.undo("u1")
    assert res["items"] == ["eggs", "rice"]
    assert led.get("eggs")["qty"] == 6
    assert led.get("rice") is None
    assert led.undo("u1")["replayed"] is True  # retried "undo" doesn't undo twice
    led.undo("u2")
    assert led.list_items() == []
    with pytest.raises(LedgerError, match="Nothing to undo"):
        led.undo("u3")
    assert led.verify() == []


def test_set_discard_and_projection_matches_replay(led):
    groceries(led)
    led.apply_batch([{"type": "set", "item": "eggs", "qty": 3}], "k2")
    led.apply_batch([{"type": "discard", "item": "spinach", "qty": 1, "unit": "lb"}],
                    "k3")
    assert led.get("eggs")["qty"] == 3
    assert led.get("spinach")["qty"] == 0
    assert "spinach" not in [i["item"] for i in led.list_items()]
    assert led.verify() == []
    assert len(led.history("eggs")) == 2


def test_event_log_is_append_only(store, led):
    groceries(led)
    with psycopg.connect(DSN, autocommit=True) as conn:
        with pytest.raises(psycopg.errors.RaiseException):
            conn.execute("UPDATE events SET qty_base = 999")


def test_concurrent_writes_from_many_connections(store):
    def worker(n):
        ledger = store.ledger("h1")
        for i in range(20):
            ledger.apply_batch([{"type": "add", "item": "eggs", "qty": 1}], f"{n}-{i}")

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    led = store.ledger("h1")
    assert led.get("eggs")["qty"] == 160
    assert led.verify() == []


def test_concurrent_retries_apply_once(store):
    led = store.ledger("h1")
    threads = [threading.Thread(target=groceries, args=(led, "same"))
               for _ in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert led.get("eggs")["qty"] == 6


def test_households_are_isolated(store):
    groceries(store.ledger("smith"))
    jones = store.ledger("jones")
    assert jones.list_items() == []
    groceries(jones)  # same idempotency key in another household is independent
    assert jones.get("eggs")["qty"] == 6
    with pytest.raises(LedgerError):
        store.ledger("../etc/passwd")


def test_row_level_security_blocks_other_households(store):
    groceries(store.ledger("smith"))
    with psycopg.connect(DSN, autocommit=True) as conn:
        conn.execute("DROP ROLE IF EXISTS kitchen_app")
        conn.execute("CREATE ROLE kitchen_app LOGIN")
        conn.execute("GRANT USAGE ON SCHEMA public TO kitchen_app")
        conn.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES "
                     "IN SCHEMA public TO kitchen_app")
    app_dsn = DSN.replace("user=postgres", "user=kitchen_app")
    with psycopg.connect(app_dsn) as conn:
        conn.execute("SELECT set_config('app.household_id', 'jones', true)")
        assert conn.execute("SELECT count(*) FROM inventory").fetchone()[0] == 0
        conn.rollback()
        conn.execute("SELECT set_config('app.household_id', 'smith', true)")
        assert conn.execute("SELECT count(*) FROM inventory").fetchone()[0] == 3
    with psycopg.connect(DSN, autocommit=True) as conn:
        conn.execute("REVOKE ALL ON ALL TABLES IN SCHEMA public FROM kitchen_app")
        conn.execute("REVOKE USAGE ON SCHEMA public FROM kitchen_app")
        conn.execute("DROP ROLE kitchen_app")


def test_fifo_expiry_preservation_for_duplicate_batches(led):
    # Batch 1: 1 gallon milk left outside, expires soon
    led.apply_batch([
        {"type": "add", "item": "milk", "qty": 1, "unit": "gallons", "zone": "pantry",
         "expires_at": "2026-10-23T10:00:00+00:00"}
    ], idempotency_key="batch-1-outside")

    item1 = led.get("milk")
    assert item1["qty"] == 3785.41
    assert "2026-10-23" in item1["expires_at"]

    # Batch 2: Fresh 1 gallon milk placed in fridge, expires 7 days later
    led.apply_batch([
        {"type": "add", "item": "milk", "qty": 1, "unit": "gallons", "zone": "fridge",
         "expires_at": "2026-10-30T10:00:00+00:00"}
    ], idempotency_key="batch-2-fresh")

    item2 = led.get("milk")
    assert item2["qty"] == 7570.82
    # FIFO Invariant: earlier expiry must NOT be overwritten by later expiry
    assert "2026-10-23" in item2["expires_at"]

    # Replay must produce identical FIFO result with zero discrepancies against projection
    assert led.verify() == []
