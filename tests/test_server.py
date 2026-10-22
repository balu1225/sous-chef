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
    hz = httpx.get(f"{server.base}/healthz").json()
    assert hz["status"] == "ok"
    assert "aws_bedrock" in hz
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


def test_api_cooking_and_timer_flow(server, db):
    headers = {"Authorization": f"Bearer {TOKEN}"}

    # 1. Start cooking spinach scramble
    start_res = httpx.post(f"{server.base}/api/cooking", json={"action": "start", "recipe_id": "spinach_scramble"}, headers=headers)
    assert start_res.status_code == 200
    state = start_res.json()["active_cooking"]
    assert state is not None
    assert state["recipe"]["id"] == "spinach_scramble"
    assert state["step"] == 1

    # 2. Check prep item (e.g. eggs)
    prep_res = httpx.post(f"{server.base}/api/cooking", json={"action": "check_prep", "item": "eggs"}, headers=headers)
    assert prep_res.status_code == 200
    assert "eggs" in prep_res.json()["active_cooking"]["checked_prep"]

    # 3. Next step
    next_res = httpx.post(f"{server.base}/api/cooking", json={"action": "next_step"}, headers=headers)
    assert next_res.status_code == 200
    assert next_res.json()["active_cooking"]["step"] == 2

    # 4. Confirm timer alert action ("i stopped the stove" / "done")
    confirm_res = httpx.post(f"{server.base}/api/converse", json={"utterance": "I stopped the stove"}, headers=headers)
    assert confirm_res.status_code == 200
    data = confirm_res.json()
    assert data.get("action_confirmed") is True
    assert data.get("resume_music") is True
    assert "Stove is stopped" in data["spoken_message"] or "stove is stopped" in data["spoken_message"].lower()

    # 5. Stop cooking
    stop_res = httpx.post(f"{server.base}/api/cooking", json={"action": "stop"}, headers=headers)
    assert stop_res.status_code == 200
    assert stop_res.json()["active_cooking"] is None


def test_api_converse_music_and_spoiled_food(server, db):
    headers = {"Authorization": f"Bearer {TOKEN}"}

    # Test music commands
    music_res = httpx.post(f"{server.base}/api/converse", json={"utterance": "play cooking music"}, headers=headers)
    assert music_res.status_code == 200
    assert music_res.json().get("music_command") == "play"

    stop_music_res = httpx.post(f"{server.base}/api/converse", json={"utterance": "stop music"}, headers=headers)
    assert stop_music_res.status_code == 200
    assert stop_music_res.json().get("music_command") == "stop"

    # Add milk to inventory first
    add_res = httpx.post(f"{server.base}/api/converse", json={"utterance": "I bought 1 gallon of milk"}, headers=headers)
    assert add_res.status_code == 200
    assert "milk" in add_res.json()["spoken_message"].lower()

    # Discard spoiled milk
    spoil_res = httpx.post(f"{server.base}/api/converse", json={"utterance": "the milk is spoiled"}, headers=headers)
    assert spoil_res.status_code == 200
    spoil_data = spoil_res.json()
    assert "removing" in spoil_data["spoken_message"].lower() or "discarded" in spoil_data["spoken_message"].lower()

    # Verify inventory no longer has milk
    inv_res = httpx.get(f"{server.base}/api/inventory", headers=headers)
    assert inv_res.status_code == 200
    items = inv_res.json()["items"]
    assert not any(i["item"] == "milk" for i in items)


def test_get_cooking_remedy_tool_and_dialogue(server, db):
    headers = {"Authorization": f"Bearer {TOKEN}"}

    # 1. Test FastMCP tool: get_cooking_remedy
    res = tool(server, "get_cooking_remedy", {"mishap": "too_salty"})
    data = payload(res)
    assert "remedy_steps" in data
    assert "quip" in data
    assert "salt" in data["category"].lower() or "salted" in data["category"].lower()

    # 2. Test Conversational API: "I burned the chicken"
    burn_res = httpx.post(f"{server.base}/api/converse", json={"utterance": "I burned the food"}, headers=headers)
    assert burn_res.status_code == 200
    burn_data = burn_res.json()
    assert "remedy" in burn_data
    assert burn_data["remedy"]["type"] == "burned"
    assert len(burn_data["remedy"]["remedy_steps"]) > 0

    # 3. Test Conversational API: "The soup is way too salty"
    salt_res = httpx.post(f"{server.base}/api/converse", json={"utterance": "It's way too salty"}, headers=headers)
    assert salt_res.status_code == 200
    salt_data = salt_res.json()
    assert "remedy" in salt_data
    assert salt_data["remedy"]["type"] == "too_salty"


def test_save_custom_recipe_flow(server, db):
    headers = {"Authorization": f"Bearer {TOKEN}"}

    # 1. Test POST /api/recipes with string ingredients (from web companion form)
    form_res = httpx.post(
        f"{server.base}/api/recipes",
        json={
            "name": "Grandma's High-Protein Scramble",
            "prep_minutes": 10,
            "servings": 2,
            "ingredients": "3 eggs, 1 cup spinach, 2 oz cheddar"
        },
        headers=headers
    )
    assert form_res.status_code == 200
    data = form_res.json()
    assert data["saved"] is True
    assert data["recipe"]["name"] == "Grandma's High-Protein Scramble"
    assert data["recipe"]["kcal_per_serving"] > 0
    assert data["recipe"]["protein_per_serving"] > 0

    # Verify recipe is now in GET /api/recipes
    get_res = httpx.get(f"{server.base}/api/recipes", headers=headers)
    assert get_res.status_code == 200
    recipes = get_res.json()["recipes"]
    assert any(r["name"] == "Grandma's High-Protein Scramble" for r in recipes)

    # 2. Test saving by voice after cooking a meal:
    seed(db)
    # Start and finish cooking a recipe
    cook_res = httpx.post(f"{server.base}/api/converse", json={"utterance": "I cooked Spinach & Cheddar Scramble"}, headers=headers)
    assert cook_res.status_code == 200

    # User says: "Save what I cooked as Post-Workout Fuel"
    save_voice_res = httpx.post(f"{server.base}/api/converse", json={"utterance": "save what i cooked as Post-Workout Fuel"}, headers=headers)
    assert save_voice_res.status_code == 200
    save_data = save_voice_res.json()
    assert "saved_recipe" in save_data
    assert save_data["saved_recipe"]["name"] == "Post-Workout Fuel"
    assert len(save_data["saved_recipe"]["ingredients"]) > 0
    assert "Saved your recipe for Post-Workout Fuel" in save_data["spoken_message"]


def test_amazon_bedrock_recipe_classifier(server):
    # Test FastMCP tool: classify_recipe_ingredients
    res = tool(server, "classify_recipe_ingredients", {
        "recipe_name": "Tofu Stir Fry",
        "ingredients": [
            {"item": "firm tofu"},
            {"item": "olive oil"},
            {"item": "sesame seeds"}
        ]
    })
    data = payload(res)
    assert "ingredients" in data
    roles = {item["name"]: item["role"] for item in data["ingredients"]}
    assert "firm tofu" in roles
    assert roles["firm tofu"] == "core"
    assert roles.get("olive oil") == "staple"
    assert roles.get("sesame seeds") == "optional"
    assert data.get("source") in ("amazon_bedrock", "deterministic_fallback")


def test_alexa_skills_kit_integration(server, db):
    seed(db)
    headers = {"Authorization": f"Bearer {server.config.auth_token}"}

    # 1. Alexa LaunchRequest
    launch_payload = {
        "version": "1.0",
        "session": {"new": True, "sessionId": "amzn1.echo-api.session.test"},
        "request": {
            "type": "LaunchRequest",
            "requestId": "amzn1.echo-api.request.launch",
            "timestamp": "2026-10-22T00:00:00Z",
            "locale": "en-US"
        }
    }
    launch_res = httpx.post(f"{server.base}/alexa", json=launch_payload, headers=headers)
    assert launch_res.status_code == 200
    launch_body = launch_res.json()
    assert launch_body["version"] == "1.0"
    assert "outputSpeech" in launch_body["response"]
    assert "Welcome to Sous-Chef" in launch_body["response"]["outputSpeech"]["text"]
    assert launch_body["response"]["shouldEndSession"] is False
    assert "card" in launch_body["response"]

    # 2. Alexa QueryInventoryIntent
    query_payload = {
        "version": "1.0",
        "session": {"new": False, "sessionId": "amzn1.echo-api.session.test"},
        "request": {
            "type": "IntentRequest",
            "requestId": "amzn1.echo-api.request.query",
            "timestamp": "2026-10-22T00:01:00Z",
            "locale": "en-US",
            "intent": {
                "name": "QueryInventoryIntent",
                "confirmationStatus": "NONE",
                "slots": {}
            }
        }
    }
    query_res = httpx.post(f"{server.base}/api/converse", json=query_payload, headers=headers)
    assert query_res.status_code == 200
    query_body = query_res.json()
    assert "You have" in query_body["response"]["outputSpeech"]["text"]
    assert "card" in query_body["response"]

    # 3. Alexa SuggestRecipeIntent
    suggest_payload = {
        "version": "1.0",
        "session": {"new": False, "sessionId": "amzn1.echo-api.session.test"},
        "request": {
            "type": "IntentRequest",
            "requestId": "amzn1.echo-api.request.suggest",
            "timestamp": "2026-10-22T00:02:00Z",
            "locale": "en-US",
            "intent": {
                "name": "SuggestRecipeIntent",
                "confirmationStatus": "NONE",
                "slots": {
                    "MaxMinutes": {"name": "MaxMinutes", "value": "15"}
                }
            }
        }
    }
    sug_res = httpx.post(f"{server.base}/alexa", json=suggest_payload, headers=headers)
    assert sug_res.status_code == 200
    sug_body = sug_res.json()
    assert "outputSpeech" in sug_body["response"]
    assert "Spinach & Cheddar Scramble" in sug_body["response"]["outputSpeech"]["text"] or "recipe" in sug_body["response"]["outputSpeech"]["text"].lower()

    # Verify active cooking station now synced on server
    cook_state_res = httpx.get(f"{server.base}/api/cooking", headers=headers)
    assert cook_state_res.status_code == 200
    assert cook_state_res.json()["active_cooking"] is not None

    # 4. Alexa CookingStepIntent -> Next Step
    step_payload = {
        "version": "1.0",
        "session": {"new": False, "sessionId": "amzn1.echo-api.session.test"},
        "request": {
            "type": "IntentRequest",
            "requestId": "amzn1.echo-api.request.step",
            "timestamp": "2026-10-22T00:03:00Z",
            "locale": "en-US",
            "intent": {
                "name": "CookingStepIntent",
                "confirmationStatus": "NONE",
                "slots": {
                    "StepAction": {"name": "StepAction", "value": "next"}
                }
            }
        }
    }
    step_res = httpx.post(f"{server.base}/alexa", json=step_payload, headers=headers)
    assert step_res.status_code == 200
    assert "Step 2" in step_res.json()["response"]["outputSpeech"]["text"]

    # 5. Alexa CookingMishapIntent -> Rescue
    mishap_payload = {
        "version": "1.0",
        "session": {"new": False, "sessionId": "amzn1.echo-api.session.test"},
        "request": {
            "type": "IntentRequest",
            "requestId": "amzn1.echo-api.request.mishap",
            "timestamp": "2026-10-22T00:04:00Z",
            "locale": "en-US",
            "intent": {
                "name": "CookingMishapIntent",
                "confirmationStatus": "NONE",
                "slots": {
                    "Mishap": {"name": "Mishap", "value": "burned"}
                }
            }
        }
    }
    mishap_res = httpx.post(f"{server.base}/alexa", json=mishap_payload, headers=headers)
    assert mishap_res.status_code == 200
    assert "burned" in mishap_res.json()["response"]["outputSpeech"]["text"].lower() or "heat" in mishap_res.json()["response"]["outputSpeech"]["text"].lower()

    # 6. Alexa AddInventoryIntent
    add_payload = {
        "version": "1.0",
        "session": {"new": False, "sessionId": "amzn1.echo-api.session.test"},
        "request": {
            "type": "IntentRequest",
            "requestId": "amzn1.echo-api.request.add",
            "timestamp": "2026-10-22T00:05:00Z",
            "locale": "en-US",
            "intent": {
                "name": "AddInventoryIntent",
                "confirmationStatus": "NONE",
                "slots": {
                    "Quantity": {"name": "Quantity", "value": "2"},
                    "Unit": {"name": "Unit", "value": "cartons"},
                    "FoodItem": {"name": "FoodItem", "value": "oat milk"}
                }
            }
        }
    }
    add_res = httpx.post(f"{server.base}/alexa", json=add_payload, headers=headers)
    assert add_res.status_code == 200
    assert "Added 2 cartons of oat milk" in add_res.json()["response"]["outputSpeech"]["text"]

    # 7. Alexa Stop / Session Ended
    stop_payload = {
        "version": "1.0",
        "session": {"new": False, "sessionId": "amzn1.echo-api.session.test"},
        "request": {
            "type": "IntentRequest",
            "requestId": "amzn1.echo-api.request.stop",
            "timestamp": "2026-10-22T00:06:00Z",
            "locale": "en-US",
            "intent": {
                "name": "AMAZON.StopIntent"
            }
        }
    }
    stop_res = httpx.post(f"{server.base}/alexa", json=stop_payload, headers=headers)
    assert stop_res.status_code == 200
    assert stop_res.json()["response"]["shouldEndSession"] is True


def test_perishability_outside_warning_and_move_endpoint(server, db):
    headers = {"Authorization": f"Bearer {server.config.auth_token}"}

    # 1. Add milk outside in pantry -> triggers critical warning
    add_outside_res = httpx.post(
        f"{server.base}/api/converse",
        json={"utterance": "I left 1 gallon of milk outside on the counter"},
        headers=headers
    )
    assert add_outside_res.status_code == 200
    add_data = add_outside_res.json()
    assert "milk" in add_data["spoken_message"].lower()
    assert "Left outside" in add_data["spoken_message"] or "spoils rapidly" in add_data["spoken_message"] or "fridge" in add_data["spoken_message"]

    # Verify inventory item is marked zone = pantry
    inv_res = httpx.get(f"{server.base}/api/inventory", headers=headers)
    assert inv_res.status_code == 200
    milk_item = next(i for i in inv_res.json()["items"] if i["item"] == "milk")
    assert milk_item["zone"] == "pantry"

    # 2. Add duplicate batch of milk in fridge -> FIFO earlier expiry preserved + advisory returned
    add_fresh_res = httpx.post(
        f"{server.base}/api/converse",
        json={"utterance": "I put 1 gallon of milk in the fridge"},
        headers=headers
    )
    assert add_fresh_res.status_code == 200
    fresh_data = add_fresh_res.json()
    # Spoken message informs user about existing batch to use first
    assert "existing batch" in fresh_data["spoken_message"].lower() or "first" in fresh_data["spoken_message"].lower()

    # Total quantity is now 2 gallons
    inv_res2 = httpx.get(f"{server.base}/api/inventory", headers=headers)
    milk_item2 = next(i for i in inv_res2.json()["items"] if i["item"] == "milk")
    assert milk_item2["qty"] == 7570.82

    # 3. Test POST /api/inventory/move to move milk to fridge
    move_res = httpx.post(
        f"{server.base}/api/inventory/move",
        json={"item": "milk", "target_zone": "fridge"},
        headers=headers
    )
    assert move_res.status_code == 200
    move_data = move_res.json()
    assert move_data["moved"] is True
    assert move_data["item"]["zone"] == "fridge"
    assert "Moved milk to Refrigerator" in move_data["spoken_message"]

    # 4. Test conversational move: "put milk in freezer"
    conv_move_res = httpx.post(
        f"{server.base}/api/converse",
        json={"utterance": "put milk in freezer"},
        headers=headers
    )
    assert conv_move_res.status_code == 200
    conv_move_data = conv_move_res.json()
    assert "freezer" in conv_move_data["spoken_message"].lower()
    assert "milk" in conv_move_data["spoken_message"].lower()





