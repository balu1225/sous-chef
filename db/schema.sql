-- Kitchen agent ledger schema (Postgres 14+). Safe to run repeatedly.

CREATE TABLE IF NOT EXISTS households (
    household_id TEXT PRIMARY KEY CHECK (household_id ~ '^[A-Za-z0-9_-]{1,64}$'),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- One row per utterance / request. Holds the idempotency key and the result
-- returned to the caller, so retries get the same answer.
CREATE TABLE IF NOT EXISTS batches (
    batch_id        UUID PRIMARY KEY,
    batch_seq       BIGINT GENERATED ALWAYS AS IDENTITY,
    household_id    TEXT NOT NULL REFERENCES households ON DELETE CASCADE,
    idempotency_key TEXT NOT NULL,
    source          TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    result          JSONB NOT NULL,
    UNIQUE (household_id, idempotency_key)
);

-- Append-only source of truth. Never UPDATE or DELETE rows here.
CREATE TABLE IF NOT EXISTS events (
    seq           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_id      UUID UNIQUE NOT NULL,
    household_id  TEXT NOT NULL REFERENCES households ON DELETE CASCADE,
    batch_id      UUID NOT NULL REFERENCES batches ON DELETE CASCADE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    type          TEXT NOT NULL CHECK (type IN ('add','consume','discard','set','undo')),
    item          TEXT,
    family        TEXT CHECK (family IN ('count','mass','volume')),
    qty_base      NUMERIC(14,4) CHECK (qty_base > 0),
    zone          TEXT,
    expires_at    TIMESTAMPTZ,
    reverts_batch UUID REFERENCES batches ON DELETE CASCADE,
    CHECK ((type = 'undo') = (reverts_batch IS NOT NULL)),
    CHECK (type = 'undo' OR (item IS NOT NULL AND family IS NOT NULL
                             AND qty_base IS NOT NULL))
);
CREATE INDEX IF NOT EXISTS events_household_item ON events (household_id, item, seq);
CREATE INDEX IF NOT EXISTS events_household_undo ON events (household_id)
    WHERE type = 'undo';

-- Current stock, derived from events in the same transaction.
CREATE TABLE IF NOT EXISTS inventory (
    household_id TEXT NOT NULL REFERENCES households ON DELETE CASCADE,
    item         TEXT NOT NULL,
    family       TEXT NOT NULL CHECK (family IN ('count','mass','volume')),
    qty_base     NUMERIC(14,4) NOT NULL CHECK (qty_base >= 0),
    zone         TEXT,
    expires_at   TIMESTAMPTZ,
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (household_id, item)
);
CREATE INDEX IF NOT EXISTS inventory_expiring ON inventory (household_id, expires_at)
    WHERE qty_base > 0;

-- Block edits to the event log at the database level.
CREATE OR REPLACE FUNCTION events_append_only() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'events is append-only';
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS events_no_update ON events;
CREATE TRIGGER events_no_update BEFORE UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION events_append_only();

-- Logged meals: Tracks cooked meals and nutrition consumption per household.
CREATE TABLE IF NOT EXISTS logged_meals (
    meal_id         UUID PRIMARY KEY,
    household_id    TEXT NOT NULL REFERENCES households ON DELETE CASCADE,
    recipe_id       TEXT,
    recipe_name     TEXT NOT NULL,
    servings        NUMERIC(6,2) NOT NULL DEFAULT 1.0,
    total_kcal      NUMERIC(10,2) NOT NULL DEFAULT 0,
    total_protein_g NUMERIC(10,2) NOT NULL DEFAULT 0,
    details         JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS logged_meals_household_date ON logged_meals (household_id, created_at);

-- Custom family recipes saved by voice.
CREATE TABLE IF NOT EXISTS custom_recipes (
    recipe_id       UUID PRIMARY KEY,
    household_id    TEXT NOT NULL REFERENCES households ON DELETE CASCADE,
    name            TEXT NOT NULL,
    servings        NUMERIC(6,2) NOT NULL DEFAULT 1.0,
    prep_minutes    INT NOT NULL DEFAULT 15,
    ingredients     JSONB NOT NULL,
    steps           JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (household_id, name)
);

-- Row-level security: a second wall between households. The app sets
-- app.household_id at the start of every transaction. Policies apply when the
-- app connects as a non-owner role (recommended in production).
ALTER TABLE batches        ENABLE ROW LEVEL SECURITY;
ALTER TABLE events         ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory      ENABLE ROW LEVEL SECURITY;
ALTER TABLE logged_meals   ENABLE ROW LEVEL SECURITY;
ALTER TABLE custom_recipes ENABLE ROW LEVEL SECURITY;
DO $$
DECLARE t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY['batches','events','inventory','logged_meals','custom_recipes'] LOOP
        IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = t
                       AND policyname = t || '_household') THEN
            EXECUTE format(
                'CREATE POLICY %I ON %I USING (household_id = '
                'current_setting(''app.household_id'', true)) WITH CHECK '
                '(household_id = current_setting(''app.household_id'', true))',
                t || '_household', t);
        END IF;
    END LOOP;
END $$;

