"""Fix #1 (Postgres): Reliable household inventory ledger.

Design
- One Postgres database for all households; every row carries household_id,
  and every query filters on it. Row-level security in schema.sql adds a
  second wall so one household can never read another's data.
- Append-only event log is the source of truth; `inventory` is a projection
  updated in the same transaction (fast reads, full audit, free undo).
- Every voice utterance is one atomic batch with an idempotency key, so a
  retried request never double-applies ("add 6 eggs" twice).
- Writes for one household are serialized with a transaction-scoped advisory
  lock, so any number of server instances can run safely side by side.
- Quantities are exact decimals (NUMERIC), never floats.
- Strict validation: known units, positive finite quantities, no negative stock,
  no mixing unit families (mass vs volume vs count) on one item.
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool

D = Decimal
# unit -> (family, factor to base unit). Base units: count, g, ml.
UNITS = {
    "count": ("count", D(1)), "each": ("count", D(1)), "item": ("count", D(1)),
    "piece": ("count", D(1)), "dozen": ("count", D(12)),
    "carton": ("count", D(1)), "bottle": ("count", D(1)), "box": ("count", D(1)),
    "bag": ("count", D(1)), "can": ("count", D(1)), "jar": ("count", D(1)),
    "pack": ("count", D(1)), "package": ("count", D(1)), "container": ("count", D(1)),
    "bunch": ("count", D(1)), "bar": ("count", D(1)), "clove": ("count", D(1)),
    "slice": ("count", D(1)), "block": ("count", D(1)),
    "g": ("mass", D(1)), "gram": ("mass", D(1)), "kg": ("mass", D(1000)),
    "oz": ("mass", D("28.3495")), "lb": ("mass", D("453.592")),
    "lbs": ("mass", D("453.592")),
    "ml": ("volume", D(1)), "l": ("volume", D(1000)), "liter": ("volume", D(1000)),
    "litre": ("volume", D(1000)), "tsp": ("volume", D("4.92892")),
    "tbsp": ("volume", D("14.7868")), "cup": ("volume", D("236.588")),
    "pint": ("volume", D("473.176")), "quart": ("volume", D("946.353")),
    "gallon": ("volume", D("3785.41")), "fl_oz": ("volume", D("29.5735")),
}
BASE_UNIT = {"count": "count", "mass": "g", "volume": "ml"}
MAX_BASE_QTY = D(1_000_000)
Q = D("0.0001")  # stored precision
HOUSEHOLD_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
SCHEMA_FILE = Path(__file__).resolve().parent.parent.parent / "db" / "schema.sql"
if not SCHEMA_FILE.exists():
    SCHEMA_FILE = Path(__file__).with_name("schema.sql")



class LedgerError(ValueError):
    """Raised for invalid operations; the whole batch is rolled back."""


def normalize_item(name: str) -> str:
    item = " ".join(str(name).lower().strip().split())
    if not item:
        raise LedgerError("Item name is empty")
    return item


def normalize_unit(unit: str | None) -> str:
    u = (unit or "count").lower().strip().replace(" ", "_").rstrip(".")
    if u in UNITS:
        return u
    if u.endswith("s") and u[:-1] in UNITS:
        return u[:-1]
    if u.endswith("es") and u[:-2] in UNITS:
        return u[:-2]
    raise LedgerError(f"Unknown unit '{unit}'")


def to_base(qty, unit) -> tuple[str, Decimal]:
    try:
        q = D(str(qty))
    except (InvalidOperation, ValueError):
        raise LedgerError(f"Quantity '{qty}' is not a number") from None
    if not q.is_finite() or q <= 0:
        raise LedgerError("Quantity must be a positive number")
    family, factor = UNITS[normalize_unit(unit)]
    base = (q * factor).quantize(Q)
    if base > MAX_BASE_QTY:
        raise LedgerError("Quantity is unrealistically large")
    if base <= 0:
        raise LedgerError("Quantity is too small")
    return family, base


def parse_ts(value) -> datetime | None:
    if value is None or isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        raise LedgerError(f"Bad date '{value}'") from None


def check_household(household_id: str) -> str:
    if not HOUSEHOLD_ID.match(household_id or ""):
        raise LedgerError("Invalid household id")
    return household_id


class Store:
    """Owns the connection pool. Create one per process.

    Every pooled session is pinned to UTC (so timestamps serialize the same
    regardless of the server's TimeZone setting) and gets a statement timeout,
    so one slow query can never hang a request. Connections are health-checked
    on checkout, which survives free-tier databases dropping idle connections.
    """

    def __init__(self, dsn: str, min_size: int = 1, max_size: int = 10, *,
                 acquire_timeout: float = 30.0, statement_timeout_ms: int = 5000):
        if statement_timeout_ms <= 0:
            raise ValueError("statement_timeout_ms must be positive")

        def configure(conn):
            conn.execute("SET TIME ZONE 'UTC'")
            conn.execute(f"SET statement_timeout = {int(statement_timeout_ms)}")
            conn.execute("SET idle_in_transaction_session_timeout = "
                         f"{int(statement_timeout_ms) * 2}")

        self.pool = ConnectionPool(dsn, min_size=min_size, max_size=max_size,
                                   kwargs={"autocommit": True, "row_factory": dict_row},
                                   configure=configure,
                                   check=ConnectionPool.check_connection,
                                   timeout=acquire_timeout, open=True)

    def ping(self) -> bool:
        """True if a pooled connection can run a trivial query."""
        with self.pool.connection() as conn:
            return conn.execute("SELECT 1 AS ok").fetchone()["ok"] == 1

    def schema_ready(self) -> bool:
        """True if the ledger tables exist (migrations have been run)."""
        with self.pool.connection() as conn:
            row = conn.execute("SELECT to_regclass('public.inventory') IS NOT NULL "
                               "AND to_regclass('public.events') IS NOT NULL AS ok"
                               ).fetchone()
            return bool(row["ok"])

    def migrate(self):
        with self.pool.connection() as conn:
            conn.execute(SCHEMA_FILE.read_text())

    def ledger(self, household_id: str) -> "Ledger":
        return Ledger(self.pool, check_household(household_id))

    def close(self):
        self.pool.close()


class Ledger:
    """All operations for one household."""

    def __init__(self, pool: ConnectionPool, household_id: str):
        self.pool = pool
        self.hid = check_household(household_id)

    def _run(self, idempotency_key: str, source: str, body):
        if not idempotency_key:
            raise LedgerError("idempotency_key is required")
        with self.pool.connection() as conn, conn.transaction():
            conn.execute("SELECT set_config('app.household_id', %s, true)", (self.hid,))
            conn.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                         (self.hid,))
            prior = conn.execute(
                "SELECT result FROM batches WHERE household_id=%s AND idempotency_key=%s",
                (self.hid, idempotency_key)).fetchone()
            if prior:
                return {**prior["result"], "replayed": True}
            conn.execute("INSERT INTO households (household_id) VALUES (%s) "
                         "ON CONFLICT DO NOTHING", (self.hid,))
            batch_id = uuid.uuid4()
            conn.execute("INSERT INTO batches (batch_id, household_id, idempotency_key,"
                         " source, result) VALUES (%s,%s,%s,%s,'{}')",
                         (batch_id, self.hid, idempotency_key, source))
            result = {"batch_id": str(batch_id), **body(conn, batch_id),
                      "replayed": False}
            conn.execute("UPDATE batches SET result=%s WHERE batch_id=%s",
                         (Jsonb(result), batch_id))
            return result

    # ---------- writes ----------
    def apply_batch(self, ops: list[dict], idempotency_key: str,
                    source: str = "voice") -> dict:
        """Apply all ops atomically. Retrying with the same key returns the
        original result without re-applying.

        op: {"type": add|consume|discard|set, "item": str, "qty": num,
             "unit": str, "zone": str?, "expires_at": ISO date?}
        """
        if not ops:
            raise LedgerError("No operations given")
        return self._run(idempotency_key, source, lambda conn, bid: {
            "changes": [self._apply_op(conn, bid, op) for op in ops]})

    def _apply_op(self, conn, batch_id, op) -> dict:
        kind = op.get("type")
        if kind not in ("add", "consume", "discard", "set"):
            raise LedgerError(f"Unknown operation '{kind}'")
        item = normalize_item(op.get("item", ""))
        family, qty = to_base(op.get("qty"), op.get("unit"))
        row = conn.execute("SELECT * FROM inventory WHERE household_id=%s AND item=%s",
                           (self.hid, item)).fetchone()

        if row and row["family"] != family:
            raise LedgerError(f"'{item}' is tracked in {BASE_UNIT[row['family']]}, "
                              f"not {BASE_UNIT[family]}")
        current = row["qty_base"] if row else D(0)
        if kind == "add":
            new = current + qty
        elif kind == "set":
            new = qty
        else:  # consume / discard
            if current < qty:
                raise LedgerError(f"Only {current.normalize():f} {BASE_UNIT[family]} "
                                  f"of '{item}' in stock, cannot remove "
                                  f"{qty.normalize():f}")
            new = current - qty

        zone = op.get("zone") or (row["zone"] if row else None)
        expires = parse_ts(op.get("expires_at")) if kind in ("add", "set") else None
        if expires is None and row:
            expires = row["expires_at"]

        conn.execute("INSERT INTO events (event_id, household_id, batch_id, type, item,"
                     " family, qty_base, zone, expires_at) "
                     "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                     (uuid.uuid4(), self.hid, batch_id, kind, item, family, qty,
                      zone, expires))
        conn.execute("INSERT INTO inventory (household_id, item, family, qty_base, zone,"
                     " expires_at, updated_at) VALUES (%s,%s,%s,%s,%s,%s, now()) "
                     "ON CONFLICT (household_id, item) DO UPDATE SET "
                     "qty_base=EXCLUDED.qty_base, zone=EXCLUDED.zone, "
                     "expires_at=EXCLUDED.expires_at, updated_at=now()",
                     (self.hid, item, family, new, zone, expires))
        return {"item": item, "type": kind, "before": float(current),
                "after": float(new), "unit": BASE_UNIT[family]}

    def undo(self, idempotency_key: str, batch_id: str | None = None) -> dict:
        """Revert a batch (default: the most recent one not yet undone) by
        appending an 'undo' event and rebuilding the affected items."""
        def body(conn, new_batch):
            reverted = self._reverted(conn)
            if batch_id is None:
                row = conn.execute(
                    "SELECT batch_id FROM batches WHERE household_id=%s "
                    "AND source <> 'undo' AND NOT (batch_id = ANY(%s)) "
                    "ORDER BY batch_seq DESC LIMIT 1",
                    (self.hid, list(reverted))).fetchone()
                if row is None:
                    raise LedgerError("Nothing to undo")
                target = row["batch_id"]
            else:
                try:
                    target = uuid.UUID(str(batch_id))
                except ValueError:
                    raise LedgerError("Unknown batch") from None
                if target in reverted:
                    raise LedgerError("That change was already undone")
            items = [r["item"] for r in conn.execute(
                "SELECT DISTINCT item FROM events WHERE household_id=%s AND batch_id=%s"
                " AND type <> 'undo'", (self.hid, target))]
            if not items:
                raise LedgerError("Unknown batch")
            conn.execute("INSERT INTO events (event_id, household_id, batch_id, type,"
                         " reverts_batch) VALUES (%s,%s,%s,'undo',%s)",
                         (uuid.uuid4(), self.hid, new_batch, target))
            reverted.add(target)
            for item in items:
                self._rebuild_item(conn, item, reverted)
            return {"undid": str(target), "items": sorted(items)}

        return self._run(idempotency_key, "undo", body)

    def _reverted(self, conn) -> set:
        return {r["reverts_batch"] for r in conn.execute(
            "SELECT reverts_batch FROM events WHERE household_id=%s AND type='undo'",
            (self.hid,))}

    @staticmethod
    def _replay(rows, reverted) -> dict | None:
        state = None
        for e in rows:
            if e["type"] == "undo" or e["batch_id"] in reverted:
                continue
            qty = state["qty_base"] if state else D(0)
            if e["type"] == "add":
                qty += e["qty_base"]
            elif e["type"] == "set":
                qty = e["qty_base"]
            else:
                qty = max(D(0), qty - e["qty_base"])
            state = {"family": e["family"], "qty_base": qty, "zone": e["zone"],
                     "expires_at": e["expires_at"]}
        return state

    def _events_for(self, conn, item):
        return conn.execute("SELECT * FROM events WHERE household_id=%s AND item=%s "
                            "ORDER BY seq", (self.hid, item)).fetchall()

    def _rebuild_item(self, conn, item, reverted):
        state = self._replay(self._events_for(conn, item), reverted)
        if state is None:
            conn.execute("DELETE FROM inventory WHERE household_id=%s AND item=%s",
                         (self.hid, item))
        else:
            conn.execute(
                "INSERT INTO inventory (household_id, item, family, qty_base, zone,"
                " expires_at, updated_at) VALUES (%s,%s,%s,%s,%s,%s, now()) "
                "ON CONFLICT (household_id, item) DO UPDATE SET family=EXCLUDED.family,"
                " qty_base=EXCLUDED.qty_base, zone=EXCLUDED.zone,"
                " expires_at=EXCLUDED.expires_at, updated_at=now()",
                (self.hid, item, state["family"], state["qty_base"], state["zone"],
                 state["expires_at"]))

    # ---------- reads ----------
    def _read(self, sql, params):
        with self.pool.connection() as conn, conn.transaction():
            conn.execute("SELECT set_config('app.household_id', %s, true)", (self.hid,))
            return conn.execute(sql, params).fetchall()

    def get(self, item: str) -> dict | None:
        rows = self._read("SELECT * FROM inventory WHERE household_id=%s AND item=%s",
                          (self.hid, normalize_item(item)))
        return self._fmt(rows[0]) if rows else None

    def list_items(self, include_empty: bool = False) -> list[dict]:
        sql = "SELECT * FROM inventory WHERE household_id=%s"
        if not include_empty:
            sql += " AND qty_base > 0"
        return [self._fmt(r) for r in self._read(sql + " ORDER BY item", (self.hid,))]

    def history(self, item: str | None = None, limit: int = 50) -> list[dict]:
        if item:
            rows = self._read("SELECT * FROM events WHERE household_id=%s AND item=%s "
                              "ORDER BY seq DESC LIMIT %s",
                              (self.hid, normalize_item(item), limit))
        else:
            rows = self._read("SELECT * FROM events WHERE household_id=%s "
                              "ORDER BY seq DESC LIMIT %s", (self.hid, limit))
        return [dict(r) for r in rows]

    def verify(self) -> list[str]:
        """Check the projection matches a full replay of the event log."""
        problems = []
        with self.pool.connection() as conn, conn.transaction():
            conn.execute("SELECT set_config('app.household_id', %s, true)", (self.hid,))
            reverted = self._reverted(conn)
            items = [r["item"] for r in conn.execute(
                "SELECT DISTINCT item FROM events WHERE household_id=%s "
                "AND item IS NOT NULL", (self.hid,))]
            for item in items:
                want = self._replay(self._events_for(conn, item), reverted)
                have = conn.execute("SELECT qty_base FROM inventory WHERE "
                                    "household_id=%s AND item=%s",
                                    (self.hid, item)).fetchone()
                w = want["qty_base"] if want else None
                h = have["qty_base"] if have else None
                if w != h:
                    problems.append(f"{item}: projection {h} != replay {w}")
        return problems

    @staticmethod
    def _fmt(row) -> dict:
        return {"item": row["item"], "qty": float(row["qty_base"]),
                "unit": BASE_UNIT[row["family"]], "zone": row["zone"],
                "expires_at": row["expires_at"].isoformat() if row["expires_at"] else None,
                "updated_at": row["updated_at"].isoformat()}
