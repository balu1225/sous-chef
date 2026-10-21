---
name: postgres-ledger
description: Core invariants, SQL triggers, advisory locking, and state projection rules for Sous-Chef's append-only ledger.
---

# Postgres Ledger Engineering Standard

## 1. Core Invariants (P0 Foundation)
1. **Append-Only Event Log:** The `inventory_events` table is write-only. Events are NEVER updated, overwritten, or deleted.
2. **Database Trigger Enforcement:** An unconditional PostgreSQL trigger blocks any `UPDATE` or `DELETE` attempt on `inventory_events`:
   ```sql
   CREATE OR REPLACE FUNCTION prevent_event_mutation()
   RETURNS TRIGGER AS $$
   BEGIN
       RAISE EXCEPTION 'inventory_events is append-only: updates and deletes are forbidden';
   END;
   $$ LANGUAGE plpgsql;

   CREATE TRIGGER trg_no_event_mutation
   BEFORE UPDATE OR DELETE ON inventory_events
   FOR EACH ROW EXECUTE FUNCTION prevent_event_mutation();
   ```
3. **Compensating Events for Undo:** Undo operations insert a new compensating event (`event_type = 'undo'`), never modifying past rows.
4. **Projection Invariant:** At all times, `inventory_projection` must match the exact sum of all valid events in `inventory_events`. A `verify(household_id)` helper audits this.

## 2. Concurrency & Advisory Locks
To eliminate race conditions across multiple server instances or simultaneous voice requests:
- Every mutation transaction MUST acquire an exclusive transactional advisory lock scoped to the `household_id`:
  ```sql
  SELECT pg_advisory_xact_lock(hashtext(%s));
  ```
- Because it is transaction-scoped (`_xact_`), the lock is automatically released on `COMMIT` or `ROLLBACK`. No orphaned locks can exist.

## 3. Session Timezone Pinning (Friction Log F1)
PostgreSQL sessions must be explicitly pinned to UTC to prevent local server timezone discrepancies in expiry dates:
```python
def configure_connection(conn):
    with conn.cursor() as cur:
        cur.execute("SET TIME ZONE 'UTC';")
        cur.execute("SET statement_timeout = 2500;")  # 2.5s DB query timeout
```

## 4. Base Units & Strict Math
Quantities in the database are stored exclusively in **base units**:
- **Count:** `count` (e.g. 6 eggs -> `6.0 count`)
- **Mass:** `g` (e.g. 1 kg flour -> `1000.0 g`)
- **Volume:** `ml` (e.g. 1 gallon milk -> `3785.41 ml`)

### Rules:
- All database columns for quantity use `NUMERIC(12, 4)`. Floating point `REAL` or `DOUBLE PRECISION` is strictly forbidden to prevent floating-point drift.
- Mixing unit families in a single item (e.g., adding `100 ml` to `500 g` of flour) raises a `UnitFamilyMismatchError`.
- Quantities can never be negative in `inventory_projection`. Any operation deducting more than available stock raises `InsufficientStockError`.

## 5. Idempotent Batches
One voice utterance equals one atomic batch:
```sql
CREATE TABLE IF NOT EXISTS inventory_batches (
    batch_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id VARCHAR(64) NOT NULL,
    idempotency_key VARCHAR(128) NOT NULL UNIQUE,
    utterance TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```
- If an `idempotency_key` has already been processed, the store immediately returns the cached batch result without executing new events.

## 6. Implementation Checklist
- [ ] DB connection pool uses `SET TIME ZONE 'UTC'`.
- [ ] Every write query executes inside `pg_advisory_xact_lock`.
- [ ] Database trigger active on `inventory_events`.
- [ ] All units mapped to base units (`count`, `g`, `ml`).
- [ ] `verify(household_id)` unit tests pass.
