"""Contract tests for the MCP server, through a real MCP client over
Streamable HTTP against a real uvicorn server and a real Postgres.

    KITCHEN_TEST_DSN="postgresql://user:pass@localhost:5432/kitchen_test" pytest -q
Uses the same test database as test_ledger.py; it is wiped per test.
"""
import json
import os
import socket
import threading
import time
from datetime import datetime, timedelta, timezone

import anyio
import httpx
import psycopg
import pytest
import uvicorn
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from config import Config, ConfigError
from ledger import Store
from runtime import DB_DOWN_MESSAGE
from server import build_app

DSN = os.environ.get("KITCHEN_TEST_DSN",
                     "host=/tmp port=5433 user=postgres dbname=kitchen")
TOKEN = "t" * 40
HOUSEHOLD = "demo"
UNREACHABLE_DSN = "host=127.0.0.1 port=1 user=nobody dbname=none connect_timeout=1"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class LiveServer:
    def __init__(self, config: Config):
        self.config = config
        self.server = uvicorn.Server(uvicorn.Config(
            build_app(config), host="127.0.0.1", port=config.port, log_level="warning"))
        self.thread = threading.Thread(target=self.server.run, daemon=True)

    @property
    def base(self) -> str:
        return f"http://127.0.0.1:{self.config.port}"

    def __enter__(self):
        self.thread.start()
        for _ in range(200):
            if self.server.started:
                return self
            time.sleep(0.02)
        raise RuntimeError("server did not start")

    def __exit__(self, *exc):
        self.server.should_exit = True
        self.thread.join(timeout=10)


def make_config(dsn=DSN, token=TOKEN, **overrides) -> Config:
    env = {"KITCHEN_DATABASE_URL": dsn, "KITCHEN_HOUSEHOLD_ID": HOUSEHOLD,
           "KITCHEN_PORT": str(_free_port()), "KITCHEN_DB_ACQUIRE_TIMEOUT_S": "1",
           "KITCHEN_TOOL_TIMEOUT_S": "4"}
    if token:
        env["KITCHEN_AUTH_TOKEN"] = token
    else:
        env["KITCHEN_ALLOW_NO_AUTH"] = "1"
    env.update(overrides)
    return Config.from_env(env)


@pytest.fixture
def db():
    with psycopg.connect(DSN, autocommit=True) as conn:
        conn.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
    store = Store(DSN, max_size=2)
    store.migrate()
    yield store
    store.close()


@pytest.fixture
def server(db):
    with LiveServer(make_config()) as srv:
        yield srv


def seed(store: Store):
    soon = (datetime.now(timezone.utc) + timedelta(hours=20)).isoformat()
    later = (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()
    store.ledger(HOUSEHOLD).apply_batch([
        {"type": "add", "item": "Milk", "qty": 1, "unit": "gallon", "zone": "fridge",
         "expires_at": later},
        {"type": "add", "item": "eggs", "qty": 6, "zone": "fridge"},
        {"type": "add", "item": "spinach", "qty": 1, "unit": "lb", "zone": "fridge",
         "expires_at": soon},
    ], idempotency_key="seed")


async def _session_call(srv, fn, token=TOKEN):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    async with httpx.AsyncClient(headers=headers, timeout=10) as http:
        async with streamable_http_client(f"{srv.base}/mcp", http_client=http) as (r, w, _):
            async with ClientSession(r, w) as session:
                init = await session.initialize()
                return await fn(session, init)


async def init_only(session, init):
    return init


def call(srv, fn, token=TOKEN):
    return anyio.run(_session_call, srv, fn, token)


def tool(srv, name, args=None):
    async def fn(session, _):
        return await session.call_tool(name, args or {})
    return call(srv, fn)


def payload(result) -> dict:
    """Structured content and the text block must always agree."""
    assert json.loads(result.content[0].text) == result.structuredContent
    return result.structuredContent


# ---------------------------------------------------------------- protocol
def test_negotiates_protocol_2025_11_25(server):
    init = call(server, init_only)
    assert init.protocolVersion == "2025-11-25"
    assert init.serverInfo.name == "sous-chef"
    assert "tool returned" in init.instructions


def test_lists_query_inventory_as_read_only(server):
    async def fn(session, _):
        return await session.list_tools()
    tools = {t.name: t for t in call(server, fn).tools}
    assert "query_inventory" in tools
    t = tools["query_inventory"]
    assert t.annotations.readOnlyHint is True
    assert set(t.inputSchema["properties"]) == {"item", "expiring_within_hours",
                                                "low_confidence_only"}
    assert len(t.description) < 200  # descriptions ride on every request


# ---------------------------------------------------------------- behavior
def test_query_all_items(server, db):
    seed(db)
    data = payload(tool(server, "query_inventory"))
    assert data["ok"] is True and data["count"] == 3
    names = [i["item"] for i in data["items"]]
    assert names == ["eggs", "milk", "spinach"]
    milk = next(i for i in data["items"] if i["item"] == "milk")
    assert milk["unit"] == "ml" and milk["qty"] == pytest.approx(3785.41)
    assert set(milk) == {"item", "qty", "unit", "zone", "expires_at", "confidence"}


def test_query_single_item_and_unknown_item(server, db):
    seed(db)
    data = payload(tool(server, "query_inventory", {"item": "EGGS"}))
    assert data["found"] is True and data["items"][0]["qty"] == 6
    data = payload(tool(server, "query_inventory", {"item": "kohlrabi"}))
    assert data["ok"] is True and data["found"] is False and data["items"] == []


def test_used_up_item_is_not_reported_as_in_stock(server, db):
    seed(db)
    db.ledger(HOUSEHOLD).apply_batch([{"type": "consume", "item": "eggs", "qty": 6}], "k2")
    data = payload(tool(server, "query_inventory", {"item": "eggs"}))
    assert data["found"] is False


def test_query_expiring_within(server, db):
    seed(db)
    data = payload(tool(server, "query_inventory", {"expiring_within_hours": 48}))
    assert [i["item"] for i in data["items"]] == ["spinach"]


def test_empty_kitchen(server):
    data = payload(tool(server, "query_inventory"))
    assert data == {**data, "ok": True, "count": 0, "items": []}


def test_only_configured_household_is_visible(server, db):
    seed(db)
    db.ledger("someone_else").apply_batch(
        [{"type": "add", "item": "caviar", "qty": 1}], "x")
    names = [i["item"] for i in payload(tool(server, "query_inventory"))["items"]]
    assert "caviar" not in names


# ---------------------------------------------------------------- validation
@pytest.mark.parametrize("args", [{"expiring_within_hours": 0},
                                  {"expiring_within_hours": -5},
                                  {"expiring_within_hours": "soon"},
                                  {"item": ""},
                                  {"item": "x" * 101}])
def test_rejects_bad_input(server, args):
    result = tool(server, "query_inventory", args)
    assert result.isError is True


def test_low_confidence_not_available_yet(server):
    result = tool(server, "query_inventory", {"low_confidence_only": True})
    assert result.isError is True
    assert payload(result)["error"]["code"] == "not_available_yet"


# ---------------------------------------------------------------- reliability
def test_database_down_gives_speakable_error(db):
    with LiveServer(make_config(dsn=UNREACHABLE_DSN)) as srv:
        result = tool(srv, "query_inventory")
        err = payload(result)["error"]
        assert result.isError is True
        assert err == {"code": "db_unavailable", "message": DB_DOWN_MESSAGE,
                       "retryable": True}
        assert httpx.get(f"{srv.base}/healthz").status_code == 200
        assert httpx.get(f"{srv.base}/readyz").status_code == 503


def test_unexpected_error_never_leaks_details(server, monkeypatch):
    from ledger import Ledger

    def boom(self, include_empty=False):
        raise RuntimeError("SELECT secret FROM internals at line 42")
    monkeypatch.setattr(Ledger, "list_items", boom)
    result = tool(server, "query_inventory")
    text = result.content[0].text
    assert payload(result)["error"]["code"] == "internal"
    assert "secret" not in text and "Traceback" not in text


def test_parallel_clients(server, db):
    seed(db)

    async def many():
        results = []

        async def one():
            async def fn(session, _):
                return await session.call_tool("query_inventory", {})
            results.append(await _session_call(server, fn))
        async with anyio.create_task_group() as tg:
            for _ in range(20):
                tg.start_soon(one)
        return results

    results = anyio.run(many)
    assert len(results) == 20
    assert all(payload(r)["count"] == 3 for r in results)


# ---------------------------------------------------------------- HTTP surface
def test_auth_required(server):
    for headers in ({}, {"Authorization": "Bearer wrong"},
                    {"Authorization": f"bearer {TOKEN}x"}):
        r = httpx.post(f"{server.base}/mcp", headers=headers, json={})
        assert r.status_code == 401
    with pytest.raises(Exception):
        call(server, init_only, token="nope" * 10)


def test_health_endpoints_are_public(server):
    assert httpx.get(f"{server.base}/healthz").json() == {"status": "ok"}
    assert httpx.get(f"{server.base}/readyz").json() == {"status": "ready"}


def test_readyz_reports_missing_schema():
    with psycopg.connect(DSN, autocommit=True) as conn:
        conn.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
    with LiveServer(make_config()) as srv:
        r = httpx.get(f"{srv.base}/readyz")
        assert r.status_code == 503 and r.json()["reason"] == "schema"


def test_no_auth_mode_for_local_dev(db):
    with LiveServer(make_config(token=None)) as srv:
        init = call(srv, init_only, token=None)
        assert init.protocolVersion == "2025-11-25"


# ---------------------------------------------------------------- config
@pytest.mark.parametrize("env, msg", [
    ({}, "KITCHEN_DATABASE_URL"),
    ({"KITCHEN_DATABASE_URL": "x"}, "KITCHEN_HOUSEHOLD_ID"),
    ({"KITCHEN_DATABASE_URL": "x", "KITCHEN_HOUSEHOLD_ID": "../etc"}, "KITCHEN_HOUSEHOLD_ID"),
    ({"KITCHEN_DATABASE_URL": "x", "KITCHEN_HOUSEHOLD_ID": "h"}, "KITCHEN_AUTH_TOKEN"),
    ({"KITCHEN_DATABASE_URL": "x", "KITCHEN_HOUSEHOLD_ID": "h",
      "KITCHEN_AUTH_TOKEN": "short"}, "at least 32"),
    ({"KITCHEN_DATABASE_URL": "x", "KITCHEN_HOUSEHOLD_ID": "h",
      "KITCHEN_ALLOW_NO_AUTH": "1", "KITCHEN_PORT": "99999"}, "KITCHEN_PORT"),
])
def test_config_fails_fast(env, msg):
    with pytest.raises(ConfigError, match=msg):
        Config.from_env(env)


def test_config_reads_platform_port():
    cfg = Config.from_env({"KITCHEN_DATABASE_URL": "x", "KITCHEN_HOUSEHOLD_ID": "h",
                           "KITCHEN_ALLOW_NO_AUTH": "1", "PORT": "9123"})
    assert cfg.port == 9123


# ---------------------------------------------------------------- write tools
def test_lists_write_tools_with_correct_annotations(server):
    async def fn(session, _):
        return await session.list_tools()
    tools = {t.name: t for t in call(server, fn).tools}
    assert "manage_inventory" in tools
    assert "undo_last_change" in tools
    assert tools["manage_inventory"].annotations.readOnlyHint is False
    assert tools["undo_last_change"].annotations.readOnlyHint is False


def test_manage_inventory_and_undo_end_to_end(server, db):
    # 1. Add items via manage_inventory
    ops = [{"type": "add", "item": "apples", "qty": 5, "unit": "count", "zone": "pantry"}]
    res = tool(server, "manage_inventory", {"operations": ops, "idempotency_key": "k_write_1"})
    data = payload(res)
    assert data["ok"] is True
    assert data["replayed"] is False
    assert len(data["changes"]) == 1
    assert data["changes"][0]["item"] == "apples"
    assert data["changes"][0]["after"] == 5.0

    # 2. Retrying with same key returns cached replayed result
    res_retry = tool(server, "manage_inventory", {"operations": ops, "idempotency_key": "k_write_1"})
    data_retry = payload(res_retry)
    assert data_retry["ok"] is True
    assert data_retry["replayed"] is True

    # 3. Query inventory verifies item is present
    q_data = payload(tool(server, "query_inventory", {"item": "apples"}))
    assert q_data["ok"] is True
    assert q_data["found"] is True
    assert q_data["items"][0]["qty"] == 5.0

    # 4. Undo the addition
    undo_res = tool(server, "undo_last_change", {"idempotency_key": "k_undo_1"})
    undo_data = payload(undo_res)
    assert undo_data["ok"] is True
    assert "undid" in undo_data
    assert undo_data["items"] == ["apples"]

    # 5. Query inventory verifies item is restored to 0 / gone
    q_after_undo = payload(tool(server, "query_inventory", {"item": "apples"}))
    assert q_after_undo["ok"] is True
    assert q_after_undo["found"] is False
