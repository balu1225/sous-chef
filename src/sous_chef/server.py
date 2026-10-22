"""Sous-Chef MCP server (PDD Phase P1, step 1: skeleton).

Transport: MCP Streamable HTTP at /mcp, stateless, JSON responses, so any
number of instances can run behind a load balancer with no sticky sessions.
SDK: official `mcp` Python SDK 1.30.0 (FastMCP), latest protocol 2025-11-25.

Endpoints
  POST /mcp      MCP (bearer token required unless explicitly disabled)
  GET  /healthz  liveness: the process is up (no DB call)
  GET  /readyz   readiness: DB reachable and schema migrated

Tools in this step: query_inventory (read-only). Write tools arrive in
later P1 steps on top of the same runtime.

Run:  python server.py        (reads configuration from the environment)
"""
from __future__ import annotations

import hmac
import json
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated, Callable, Any
import uuid

import anyio
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import CallToolResult, ToolAnnotations
from pydantic import Field
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Mount, Route

from config import Config
from ledger import Store
from parser.amount_parser import parse_kitchen_utterance, format_spoken_quantity
from runtime import ToolFailure, run_blocking, run_tool, setup_logging
from matching import (
    get_all_recipes,
    find_recipe_by_id,
    match_recipes,
    execute_cooking_deduction,
)
from nutrition import calculate_meal_nutrition
from remedies import get_remedy_for_mishap
from bedrock import tag_recipe_ingredients, is_bedrock_configured
from shelf_life import (
    calculate_shelf_life,
    resolve_fifo_expiry,
    generate_duplicate_batch_advisory,
)

import urllib.parse
from polly_voice import synthesize_speech

log = logging.getLogger("kitchen_agent")

SERVER_NAME = "sous-chef"
SIMULATOR_DIR = Path(__file__).resolve().parent.parent.parent / "web_simulator"

INSTRUCTIONS = (
    "Sous-Chef manages one household's kitchen. Only state stock, recipes and "
    "nutrition that a tool returned in this conversation; never guess or invent "
    "items or amounts. If a tool returns ok=false, tell the user its "
    "error.message. Keep spoken replies under 25 words."
)

PUBLIC_PATHS = frozenset({"/healthz", "/readyz", "/", "/style.css", "/app.js",
                          "/api/inventory", "/api/inventory/move", "/api/converse",
                          "/api/nutrition", "/api/recipes", "/api/cooking", "/api/presence",
                          "/api/tts"})


@dataclass
class State:
    config: Config
    store: Store | None = None
    pending_clarification: dict | None = None
    active_cooking: dict | None = None
    last_cooked_meal: dict | None = None
    last_screen_presence: float = 0.0
    screen_active: bool = False

    def is_screen_active(self) -> bool:
        import time
        return self.screen_active and (time.time() - self.last_screen_presence < 25.0)



# --------------------------------------------------------------------------
# Tools
# --------------------------------------------------------------------------
def _item_view(row: dict) -> dict:
    """Section 9 output shape. Confidence scoring arrives in P2 (FR-6)."""
    return {"item": row["item"], "qty": row["qty"], "unit": row["unit"],
            "zone": row["zone"], "expires_at": row["expires_at"],
            "confidence": None}


def get_daily_nutrition(store: Store, household_id: str, date_str: str | None = None) -> dict[str, Any]:
    with store.pool.connection() as conn:
        target_date = date_str or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        row = conn.execute(
            "SELECT COALESCE(SUM(total_kcal), 0) AS total_kcal, "
            "COALESCE(SUM(total_protein_g), 0) AS total_protein, "
            "COUNT(*) AS meals_count "
            "FROM logged_meals "
            "WHERE household_id = %s AND created_at::date = %s::date",
            (household_id, target_date)
        ).fetchone()

        kcal = float(row["total_kcal"])
        prot = float(row["total_protein"])
        meals = int(row["meals_count"])

        msg = (f"Today you've consumed approximately {kcal:.0f} calories and {prot:.0f}g protein across {meals} meal(s)."
               if meals > 0 else "You haven't logged any meals today yet.")

        return {
            "date": target_date,
            "total_kcal": kcal,
            "total_protein_g": prot,
            "meals_logged": meals,
            "spoken_summary": msg
        }


def register_tools(mcp: FastMCP, state: State) -> None:


    def ledger():
        if state.store is None:
            raise ToolFailure("db_unavailable", "I can't reach your kitchen data "
                              "right now. Please try again in a moment.", retryable=True)
        return state.store.ledger(state.config.household_id)

    @mcp.tool(
        name="query_inventory",
        description=("Read current kitchen stock. Optional filters: one item name, "
                     "or items expiring within N hours. Quantities are in g, ml or "
                     "count."),
        annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True,
                                    destructiveHint=False, openWorldHint=False),
    )
    async def query_inventory(
        ctx: Context,
        item: Annotated[str | None, Field(
            min_length=1, max_length=100,
            description="Item name, e.g. 'milk'")] = None,
        expiring_within_hours: Annotated[int | None, Field(
            ge=1, le=720,
            description="Only items expiring within this many hours")] = None,
        low_confidence_only: Annotated[bool, Field(
            description="Only items we are unsure about")] = False,
    ) -> CallToolResult:

        async def handler() -> dict:
            if low_confidence_only:
                raise ToolFailure("not_available_yet",
                                  "I can't tell how sure I am about items yet.")
            led = ledger()
            timeout = state.config.tool_timeout_s
            now = datetime.now(timezone.utc)

            if item is not None:
                row = await run_blocking(lambda: led.get(item), timeout,
                                         retry_transient=True)
                rows = [row] if row and row["qty"] > 0 else []
            else:
                rows = await run_blocking(led.list_items, timeout, retry_transient=True)

            if expiring_within_hours is not None:
                cutoff = now + timedelta(hours=expiring_within_hours)
                rows = [r for r in rows if r["expires_at"]
                        and datetime.fromisoformat(r["expires_at"]) <= cutoff]
                rows.sort(key=lambda r: r["expires_at"])

            data = {"items": [_item_view(r) for r in rows], "count": len(rows),
                    "as_of": now.isoformat()}
            if item is not None:
                data["found"] = bool(rows)
            return data

        return await run_tool("query_inventory", state.config.household_id,
                              ctx.request_id, handler)

    @mcp.tool(
        name="manage_inventory",
        description=("Add, consume, discard or set kitchen stock in an atomic batch. "
                     "Requires an idempotency_key per utterance."),
        annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=True,
                                    destructiveHint=False, openWorldHint=False),
    )
    async def manage_inventory(
        ctx: Context,
        operations: Annotated[list[dict], Field(
            min_length=1, max_length=50,
            description="List of operations, e.g. [{'type':'add', 'item':'milk', 'qty':1, 'unit':'gallon'}]")],
        idempotency_key: Annotated[str, Field(
            min_length=1, max_length=128,
            description="Unique key per user utterance to prevent double application")],
    ) -> CallToolResult:

        async def handler() -> dict:
            led = ledger()
            timeout = state.config.tool_timeout_s
            result = await run_blocking(
                lambda: led.apply_batch(operations, idempotency_key=idempotency_key),
                timeout, retry_transient=False
            )
            return result

        return await run_tool("manage_inventory", state.config.household_id,
                              ctx.request_id, handler)

    @mcp.tool(
        name="undo_last_change",
        description=("Undo the most recent inventory change (or a specific batch). "
                     "Appends a compensating event; never deletes history."),
        annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=True,
                                    destructiveHint=False, openWorldHint=False),
    )
    async def undo_last_change(
        ctx: Context,
        idempotency_key: Annotated[str, Field(
            min_length=1, max_length=128,
            description="Unique key per user utterance")],
        batch_id: Annotated[str | None, Field(
            description="Optional specific batch UUID to revert (defaults to most recent)")] = None,
    ) -> CallToolResult:

        async def handler() -> dict:
            led = ledger()
            timeout = state.config.tool_timeout_s
            result = await run_blocking(
                lambda: led.undo(idempotency_key=idempotency_key, batch_id=batch_id),
                timeout, retry_transient=False
            )
            return result

        return await run_tool("undo_last_change", state.config.household_id,
                              ctx.request_id, handler)

    @mcp.tool(
        name="nutrition_summary",
        description="Get calories and protein consumed today based on logged meals.",
        annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True,
                                    destructiveHint=False, openWorldHint=False),
    )
    async def nutrition_summary(
        ctx: Context,
        period: Annotated[str, Field(description="Period: 'today' or 'week'")] = "today",
    ) -> CallToolResult:
        async def handler() -> dict:
            if state.store is None:
                raise ToolFailure("db_unavailable", "Kitchen database unavailable.", retryable=True)
            res = await run_blocking(
                lambda: get_daily_nutrition(state.store, state.config.household_id),
                state.config.tool_timeout_s, retry_transient=True
            )
            return {"summary": res}

        return await run_tool("nutrition_summary", state.config.household_id,
                              ctx.request_id, handler)

    @mcp.tool(
        name="suggest_recipes",
        description="Suggest meal options based on what's in kitchen stock, prioritizing food expiring within 48h.",
        annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True,
                                    destructiveHint=False, openWorldHint=False),
    )
    async def suggest_recipes(
        ctx: Context,
        goal: Annotated[str | None, Field(description="Optional goal: 'quick', 'use_expiring', or 'high_protein'")] = None,
        max_minutes: Annotated[int | None, Field(ge=5, le=180, description="Max preparation time in minutes")] = None,
    ) -> CallToolResult:
        async def handler() -> dict:
            led = ledger()
            rows = await run_blocking(led.list_items, state.config.tool_timeout_s, retry_transient=True)
            active = [_item_view(r) for r in rows if r["qty"] > 0]
            recipes = get_all_recipes(state.store, state.config.household_id)
            res = match_recipes(active, goal=goal, max_minutes=max_minutes, recipes=recipes)
            return res

        return await run_tool("suggest_recipes", state.config.household_id,
                              ctx.request_id, handler)

    @mcp.tool(
        name="cook_recipe",
        description="Record cooking a recipe ('I made it'). Atomically deducts ingredients and logs nutrition.",
        annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=True,
                                    destructiveHint=False, openWorldHint=False),
    )
    async def cook_recipe(
        ctx: Context,
        recipe_id: Annotated[str, Field(description="Recipe ID or recipe name")],
        idempotency_key: Annotated[str, Field(min_length=1, max_length=128)],
        servings_eaten: Annotated[float, Field(ge=0.25, le=20.0, description="Number of servings cooked")] = 2.0,
    ) -> CallToolResult:
        async def handler() -> dict:
            led = ledger()
            recipe = find_recipe_by_id(recipe_id, state.store, state.config.household_id)
            if not recipe:
                raise ToolFailure("recipe_not_found", f"I couldn't find a recipe matching '{recipe_id}'.")
            res = await run_blocking(
                lambda: execute_cooking_deduction(led, recipe, servings_eaten, idempotency_key, state.store, state.config.household_id),
                state.config.tool_timeout_s, retry_transient=False
            )
            return res

        return await run_tool("cook_recipe", state.config.household_id,
                              ctx.request_id, handler)

    @mcp.tool(
        name="save_custom_recipe",
        description="Save a custom family recipe by voice with ingredients, servings, and steps.",
        annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=True,
                                    destructiveHint=False, openWorldHint=False),
    )
    async def save_custom_recipe(
        ctx: Context,
        name: Annotated[str, Field(min_length=1, max_length=100)],
        ingredients: Annotated[list[dict], Field(description="Ingredients with item, qty, unit, and optional role")],
        idempotency_key: Annotated[str, Field(min_length=1, max_length=128)],
        servings: Annotated[float, Field(ge=0.5, le=20.0)] = 2.0,
        prep_minutes: Annotated[int, Field(ge=1, le=240)] = 15,
        steps: Annotated[list[str] | None, Field(description="Step instructions")] = None,
    ) -> CallToolResult:
        async def handler() -> dict:
            if state.store is None:
                raise ToolFailure("db_unavailable", "Kitchen database unavailable.")
            recipe_uuid = str(uuid.uuid4())
            with state.store.pool.connection() as conn:
                conn.execute("INSERT INTO households (household_id) VALUES (%s) ON CONFLICT DO NOTHING", (state.config.household_id,))
                conn.execute(
                    "INSERT INTO custom_recipes (recipe_id, household_id, name, servings, prep_minutes, ingredients, steps) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s) "
                    "ON CONFLICT (household_id, name) DO UPDATE SET "
                    "servings = EXCLUDED.servings, prep_minutes = EXCLUDED.prep_minutes, "
                    "ingredients = EXCLUDED.ingredients, steps = EXCLUDED.steps",
                    (recipe_uuid, state.config.household_id, name, servings, prep_minutes,
                     json.dumps(ingredients), json.dumps(steps or []))
                )
            nutr = calculate_meal_nutrition(ingredients)
            kcal = round(nutr["total_kcal"] / servings, 1)
            prot = round(nutr["total_protein_g"] / servings, 1)
            return {
                "saved": True,
                "recipe_id": recipe_uuid,
                "name": name,
                "servings": servings,
                "prep_minutes": prep_minutes,
                "kcal_per_serving": kcal,
                "protein_per_serving": prot,
                "spoken_message": f"Saved your recipe for {name}! Each serving has approximately {kcal:.0f} calories and {prot:.0f}g protein."
            }

        return await run_tool("save_custom_recipe", state.config.household_id,
                              ctx.request_id, handler)

    @mcp.tool(
        name="get_cooking_remedy",
        description="Get witty culinary advice and scientific kitchen remedies when food is burned, too salty, too spicy, too dry, or ruined.",
        annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True,
                                    destructiveHint=False, openWorldHint=False),
    )
    async def get_cooking_remedy(
        ctx: Context,
        mishap: Annotated[str, Field(description="Mishap type: burned, too_salty, too_spicy, too_dry, too_watery, too_sour, too_sweet, sauce_curdled, stuck_to_pan, bland, general")] = "general",
    ) -> CallToolResult:
        async def handler() -> dict:
            return get_remedy_for_mishap(mishap)

        return await run_tool("get_cooking_remedy", state.config.household_id,
                              ctx.request_id, handler)

    @mcp.tool(
        name="classify_recipe_ingredients",
        description="Classify recipe ingredients into core, optional, or staple roles using Amazon Bedrock Converse API.",
        annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True,
                                    destructiveHint=False, openWorldHint=False),
    )
    async def classify_recipe_ingredients(
        ctx: Context,
        recipe_name: Annotated[str, Field(min_length=1, max_length=100, description="Name of the recipe")],
        ingredients: Annotated[list[dict], Field(description="List of ingredients with name/item keys")],
    ) -> CallToolResult:
        async def handler() -> dict:
            return tag_recipe_ingredients(recipe_name, ingredients)

        return await run_tool("classify_recipe_ingredients", state.config.household_id,
                              ctx.request_id, handler)



# --------------------------------------------------------------------------
# HTTP app
# --------------------------------------------------------------------------
class BearerAuth:
    """Static bearer token gate for R1 (until OAuth / account linking, FR-23).
    Constant-time comparison; health endpoints stay public."""

    def __init__(self, app, token: str | None):
        self.app = app
        self.expected = f"Bearer {token}".encode() if token else None

    async def __call__(self, scope, receive, send):
        if (self.expected is None or scope["type"] != "http"
                or scope["path"] in PUBLIC_PATHS):
            return await self.app(scope, receive, send)
        provided = dict(scope["headers"]).get(b"authorization", b"")
        if hmac.compare_digest(provided, self.expected):
            return await self.app(scope, receive, send)
        response = JSONResponse({"error": "unauthorized"}, status_code=401,
                                headers={"WWW-Authenticate": "Bearer"})
        await response(scope, receive, send)


def _transport_security(config: Config) -> TransportSecuritySettings | None:
    if config.allowed_hosts:
        return TransportSecuritySettings(enable_dns_rebinding_protection=True,
                                         allowed_hosts=config.allowed_hosts,
                                         allowed_origins=config.allowed_origins)
    return None  # FastMCP auto-enables protection when bound to localhost


def make_alexa_response(
    speech_text: str,
    card_title: str | None = None,
    card_content: str | None = None,
    reprompt_text: str | None = None,
    end_session: bool = False,
) -> dict[str, Any]:
    """Formats an Alexa Skills Kit (ASK) v1.0 standard JSON response."""
    resp: dict[str, Any] = {
        "outputSpeech": {
            "type": "PlainText",
            "text": speech_text,
        },
        "shouldEndSession": end_session,
    }
    if card_title and card_content:
        resp["card"] = {
            "type": "Simple",
            "title": card_title,
            "content": card_content,
        }
    if reprompt_text and not end_session:
        resp["reprompt"] = {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text,
            }
        }
    return {
        "version": "1.0",
        "response": resp,
    }


def build_app(config: Config, store_factory: Callable[[Config], Store] | None = None):
    """Build the ASGI app. `store_factory` lets tests inject a Store."""
    state = State(config=config)
    mcp = FastMCP(
        SERVER_NAME,
        instructions=INSTRUCTIONS,
        host=config.host,
        port=config.port,
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
        transport_security=_transport_security(config),
        log_level=config.log_level,
    )
    register_tools(mcp, state)
    mcp_app = mcp.streamable_http_app()  # also creates mcp.session_manager

    def default_store(cfg: Config) -> Store:
        return Store(cfg.database_url, min_size=1, max_size=cfg.db_pool_max,
                     acquire_timeout=cfg.db_acquire_timeout_s,
                     statement_timeout_ms=cfg.db_statement_timeout_ms)

    factory = store_factory or default_store

    async def healthz(_: Request) -> JSONResponse:
        return JSONResponse({
            "status": "ok",
            "aws_bedrock": "live" if is_bedrock_configured() else "fallback_active",
            "protocol": "2025-11-25"
        })

    async def readyz(_: Request) -> JSONResponse:
        if state.store is None:
            return JSONResponse({"status": "unavailable", "reason": "database"}, 503)
        try:
            with anyio.fail_after(3):
                ok_db = await anyio.to_thread.run_sync(state.store.ping,
                                                       abandon_on_cancel=True)
                ok_schema = ok_db and await anyio.to_thread.run_sync(
                    state.store.schema_ready, abandon_on_cancel=True)
        except Exception:  # noqa: BLE001 - readiness must never raise
            return JSONResponse({"status": "unavailable", "reason": "database"}, 503)
        if not ok_schema:
            return JSONResponse({"status": "unavailable", "reason": "schema"}, 503)
        return JSONResponse({"status": "ready"})

    async def serve_index(_: Request) -> Response:
        index_file = SIMULATOR_DIR / "index.html"
        return HTMLResponse(index_file.read_text())

    async def serve_style(_: Request) -> Response:
        style_file = SIMULATOR_DIR / "style.css"
        return Response(style_file.read_text(), media_type="text/css")

    async def serve_app(_: Request) -> Response:
        app_file = SIMULATOR_DIR / "app.js"
        return Response(app_file.read_text(), media_type="application/javascript")

    async def serve_manifest(_: Request) -> Response:
        f = SIMULATOR_DIR / "manifest.json"
        return Response(f.read_text(), media_type="application/manifest+json")

    async def serve_sw(_: Request) -> Response:
        f = SIMULATOR_DIR / "sw.js"
        return Response(f.read_text(), media_type="application/javascript")

    async def api_inventory(_: Request) -> JSONResponse:
        if state.store is None:
            return JSONResponse({"items": []})
        led = state.store.ledger(state.config.household_id)
        rows = await run_blocking(led.list_items, state.config.tool_timeout_s, retry_transient=True)
        active = [_item_view(r) for r in rows if r["qty"] > 0]
        return JSONResponse({"items": active, "count": len(active)})

    async def api_inventory_move(request: Request) -> JSONResponse:
        if state.store is None:
            return JSONResponse({"error": "store_unavailable"}, status_code=503)
        body = await request.json()
        item = (body.get("item") or "").strip().lower()
        target_zone = (body.get("target_zone") or body.get("zone") or "fridge").strip().lower()
        if not item:
            return JSONResponse({"error": "item_required"}, status_code=400)
        exp_dt, is_perishable_outside, warning = calculate_shelf_life(item, target_zone)
        with state.store.pool.connection() as conn:
            conn.execute(
                "UPDATE inventory SET zone=%s, expires_at=%s, updated_at=now() "
                "WHERE household_id=%s AND item=%s",
                (target_zone, exp_dt, state.config.household_id, item)
            )
        zone_display = "Refrigerator" if target_zone == "fridge" else ("Freezer" if target_zone == "freezer" else "Pantry")
        msg = f"Moved {item} to {zone_display} and refreshed shelf-life."
        return JSONResponse({
            "ok": True,
            "moved": True,
            "item": {
                "name": item,
                "item": item,
                "zone": target_zone,
                "expires_at": exp_dt.isoformat(),
            },
            "zone": target_zone,
            "expires_at": exp_dt.isoformat(),
            "spoken_message": msg,
            "warning": warning
        })

    async def api_presence(request: Request) -> JSONResponse:
        import time
        body = await request.json() if request.method == "POST" else {}
        status = (body.get("status") or "active").strip().lower()
        now = time.time()
        if status in ("closed", "inactive"):
            state.screen_active = False
            state.last_screen_presence = 0.0
        else:
            state.screen_active = True
            state.last_screen_presence = now

        return JSONResponse({
            "ok": True,
            "status": status,
            "screen_active": state.is_screen_active(),
            "timestamp": now
        })

    async def api_tts(request: Request) -> Response:
        text = request.query_params.get("text", "").strip()
        if not text:
            return JSONResponse({"error": "text_required"}, status_code=400)

        # Synthesize with Amazon Polly Neural (Joanna)
        audio_data = await anyio.to_thread.run_sync(lambda: synthesize_speech(text))
        if audio_data:
            return Response(
                audio_data,
                media_type="audio/mpeg",
                headers={
                    "Cache-Control": "public, max-age=86400",
                    "Content-Disposition": "inline; filename=speech.mp3"
                }
            )
        return JSONResponse({"status": "polly_fallback", "message": "use_client_tts"}, status_code=200)

    async def api_nutrition(_: Request) -> JSONResponse:
        if state.store is None:
            return JSONResponse({"date": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "total_kcal": 0, "total_protein_g": 0, "meals_logged": 0})
        res = await run_blocking(lambda: get_daily_nutrition(state.store, state.config.household_id),
                                 state.config.tool_timeout_s, retry_transient=True)
        return JSONResponse(res)

    async def api_recipes(request: Request) -> JSONResponse:
        if request.method == "POST":
            body = await request.json()
            name = (body.get("name") or "").strip()
            if not name:
                return JSONResponse({"error": "name_required"}, status_code=400)
            raw_ingredients = body.get("ingredients", [])
            servings = float(body.get("servings", 2.0))
            prep_minutes = int(body.get("prep_minutes", 15))
            steps = body.get("steps", [])

            ingredients = []
            if isinstance(raw_ingredients, str):
                parsed = parse_kitchen_utterance(f"save recipe {name} with {raw_ingredients}")
                if parsed.items:
                    ingredients = [{"item": i.item, "qty": i.qty or 1.0, "unit": i.unit or "count"} for i in parsed.items]
                else:
                    parts = [p.strip() for p in raw_ingredients.split(",") if p.strip()]
                    ingredients = [{"item": p, "qty": 1.0, "unit": "serving"} for p in parts]
            elif isinstance(raw_ingredients, list):
                for entry in raw_ingredients:
                    if isinstance(entry, dict):
                        ingredients.append(entry)
                    elif isinstance(entry, str):
                        ingredients.append({"item": entry.strip(), "qty": 1.0, "unit": "count"})

            recipe_uuid = str(uuid.uuid4())
            with state.store.pool.connection() as conn:
                conn.execute("INSERT INTO households (household_id) VALUES (%s) ON CONFLICT DO NOTHING", (state.config.household_id,))
                conn.execute(
                    "INSERT INTO custom_recipes (recipe_id, household_id, name, servings, prep_minutes, ingredients, steps) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s) "
                    "ON CONFLICT (household_id, name) DO UPDATE SET "
                    "servings = EXCLUDED.servings, prep_minutes = EXCLUDED.prep_minutes, "
                    "ingredients = EXCLUDED.ingredients, steps = EXCLUDED.steps",
                    (recipe_uuid, state.config.household_id, name, servings, prep_minutes,
                     json.dumps(ingredients), json.dumps(steps))
                )
            nutr = calculate_meal_nutrition(ingredients)
            kcal = round(nutr["total_kcal"] / servings, 1)
            prot = round(nutr["total_protein_g"] / servings, 1)
            return JSONResponse({
                "saved": True,
                "recipe": {
                    "id": recipe_uuid,
                    "name": name,
                    "servings": servings,
                    "prep_minutes": prep_minutes,
                    "ingredients": ingredients,
                    "steps": steps,
                    "kcal_per_serving": kcal,
                    "protein_per_serving": prot
                }
            })
        recipes = get_all_recipes(state.store, state.config.household_id)
        return JSONResponse({"recipes": recipes, "count": len(recipes)})

    async def api_cooking(request: Request) -> JSONResponse:
        if request.method == "GET":
            return JSONResponse({"active_cooking": state.active_cooking})
        elif request.method == "POST":
            body = await request.json()
            action = body.get("action")
            if action == "start":
                recipe_id = body.get("recipe_id")
                recipe = find_recipe_by_id(recipe_id, state.store, state.config.household_id)
                if not recipe:
                    return JSONResponse({"error": "not_found"}, status_code=404)
                state.active_cooking = {
                    "recipe": recipe,
                    "step": 1,
                    "checked_prep": [],
                    "servings": float(body.get("servings", recipe.get("servings", 2)))
                }
                step1_inst = recipe.get("steps", [{}])[0].get("instruction", "Let us begin.")
                spoken = f"Let's make {recipe['name']}! Step 1: {step1_inst}"
                return JSONResponse({
                    "active_cooking": state.active_cooking,
                    "spoken_message": spoken,
                    "audio_url": f"/api/tts?text={urllib.parse.quote(spoken)}"
                })
            elif action == "stop":
                state.active_cooking = None
                return JSONResponse({"active_cooking": None})
            elif action == "check_prep":
                item = body.get("item")
                if state.active_cooking and item:
                    if item not in state.active_cooking["checked_prep"]:
                        state.active_cooking["checked_prep"].append(item)
                spoken = f"Checked off {item}."
                return JSONResponse({
                    "active_cooking": state.active_cooking,
                    "spoken_message": spoken,
                    "audio_url": f"/api/tts?text={urllib.parse.quote(spoken)}"
                })
            elif action == "next_step":
                if state.active_cooking:
                    recipe = state.active_cooking["recipe"]
                    steps = recipe.get("steps", [])
                    if state.active_cooking["step"] < len(steps):
                        state.active_cooking["step"] += 1
                        next_inst = steps[state.active_cooking["step"] - 1].get("instruction", "")
                        spoken = f"Step {state.active_cooking['step']}: {next_inst}"
                    else:
                        spoken = f"That was the final step for {recipe['name']}! Tap 'Complete Meal' to deduct ingredients."
                    return JSONResponse({
                        "active_cooking": state.active_cooking,
                        "spoken_message": spoken,
                        "audio_url": f"/api/tts?text={urllib.parse.quote(spoken)}"
                    })
                return JSONResponse({"active_cooking": None})
            elif action == "prev_step":
                if state.active_cooking:
                    if state.active_cooking["step"] > 1:
                        state.active_cooking["step"] -= 1
                    recipe = state.active_cooking["recipe"]
                    steps = recipe.get("steps", [])
                    prev_inst = steps[state.active_cooking["step"] - 1].get("instruction", "")
                    spoken = f"Going back to Step {state.active_cooking['step']}: {prev_inst}"
                    return JSONResponse({
                        "active_cooking": state.active_cooking,
                        "spoken_message": spoken,
                        "audio_url": f"/api/tts?text={urllib.parse.quote(spoken)}"
                    })
                return JSONResponse({"active_cooking": None})
            elif action == "set_step":
                if state.active_cooking:
                    step_val = int(body.get("step", 1))
                    recipe = state.active_cooking["recipe"]
                    steps = recipe.get("steps", [])
                    total = len(steps) or 1
                    state.active_cooking["step"] = max(1, min(step_val, total))
                return JSONResponse({"active_cooking": state.active_cooking})
            elif action == "set_servings":
                if state.active_cooking:
                    servings_val = float(body.get("servings", 2.0))
                    state.active_cooking["servings"] = servings_val
                return JSONResponse({"active_cooking": state.active_cooking})
            elif action == "finish":
                if state.active_cooking and state.store:
                    recipe = state.active_cooking["recipe"]
                    servings = float(state.active_cooking.get("servings", recipe.get("servings", 2)))
                    led = state.store.ledger(state.config.household_id)
                    cook_res = await run_blocking(
                        lambda: execute_cooking_deduction(led, recipe, servings, str(uuid.uuid4()), state.store, state.config.household_id),
                        state.config.tool_timeout_s, retry_transient=False
                    )
                    state.last_cooked_meal = recipe
                    state.active_cooking = None
                    spoken = cook_res["spoken_message"]
                    return JSONResponse({
                        "active_cooking": None,
                        "meal": cook_res,
                        "spoken_message": spoken,
                        "audio_url": f"/api/tts?text={urllib.parse.quote(spoken)}"
                    })
                state.active_cooking = None
                return JSONResponse({"active_cooking": None})
            elif action == "confirm_action":
                if state.active_cooking:
                    recipe = state.active_cooking["recipe"]
                    steps = recipe.get("steps", [])
                    if state.active_cooking["step"] < len(steps):
                        state.active_cooking["step"] += 1
                return JSONResponse({"active_cooking": state.active_cooking, "action_confirmed": True, "resume_music": True})
            return JSONResponse({"error": "invalid_action"}, status_code=400)

    async def api_converse(request: Request) -> JSONResponse:
        body = await request.json()

        # -------------------------------------------------------------
        # Alexa Skills Kit (ASK) Native Protocol Support
        # -------------------------------------------------------------
        if "request" in body and ("version" in body or "session" in body):
            req = body.get("request", {})
            req_type = req.get("type", "")

            if req_type == "LaunchRequest":
                return JSONResponse(make_alexa_response(
                    speech_text="Welcome to Sous-Chef! I can track your groceries, suggest meals with what's in your fridge, guide your cooking step-by-step, or rescue mishaps. What would you like to cook?",
                    card_title="Sous-Chef Voice Assistant",
                    card_content="Welcome to Sous-Chef!\n\nTry saying:\n• 'What can I make in 15 minutes?'\n• 'What is in my kitchen?'\n• 'I bought 2 eggs'\n• 'I burned the food'",
                    reprompt_text="You can ask: what can I cook for dinner, or what is in my kitchen."
                ))

            if req_type == "SessionEndedRequest":
                return JSONResponse(make_alexa_response("Goodbye!", end_session=True))

            if req_type == "IntentRequest":
                intent = req.get("intent", {})
                intent_name = intent.get("name", "")
                slots = intent.get("slots", {}) or {}

                if intent_name in ("AMAZON.StopIntent", "AMAZON.CancelIntent"):
                    return JSONResponse(make_alexa_response("Happy cooking with Sous-Chef! Goodbye.", end_session=True))

                if intent_name == "AMAZON.HelpIntent":
                    return JSONResponse(make_alexa_response(
                        speech_text="You can tell me what groceries you bought, ask what's in your fridge, ask for quick recipe ideas, or say 'help I burned the food' if you have a mishap. What would you like to do?",
                        card_title="Sous-Chef Help",
                        card_content="Try saying:\n• 'What can I make for dinner?'\n• 'What's in my fridge?'\n• 'I bought 1 gallon of milk'\n• 'The milk is spoiled'\n• 'How many calories did I eat?'",
                        reprompt_text="What would you like to do?"
                    ))

                if intent_name == "AMAZON.FallbackIntent":
                    return JSONResponse(make_alexa_response(
                        speech_text="I didn't quite catch that. You can ask what's in your kitchen, or ask what can I make in 15 minutes.",
                        reprompt_text="What would you like to cook?"
                    ))

                if state.store is None:
                    return JSONResponse(make_alexa_response("Kitchen ledger is starting up. Please try again in a moment.", end_session=False))

                led = state.store.ledger(state.config.household_id)

                if intent_name == "QueryInventoryIntent":
                    rows = await run_blocking(led.list_items, state.config.tool_timeout_s, retry_transient=True)
                    active = [r for r in rows if r["qty"] > 0]
                    if not active:
                        msg = "Your kitchen is currently empty. Tell me what groceries you bought to add them!"
                        card_txt = "Your kitchen is empty."
                    else:
                        items_spoken = ", ".join(format_spoken_quantity(r['qty'], r['unit'], r['item']) for r in active[:4])
                        msg = f"You have {len(active)} items in your kitchen: {items_spoken}."
                        card_txt = "\n".join(f"• {format_spoken_quantity(r['qty'], r['unit'], r['item'])} ({r.get('zone', 'pantry')})" for r in active)
                    return JSONResponse(make_alexa_response(
                        msg,
                        card_title="Kitchen Inventory",
                        card_content=card_txt,
                        reprompt_text="What would you like to cook with these items?"
                    ))

                if intent_name == "SuggestRecipeIntent":
                    max_min_raw = slots.get("MaxMinutes", {}).get("value")
                    max_min = int(max_min_raw) if max_min_raw and str(max_min_raw).isdigit() else None
                    rows = await run_blocking(led.list_items, state.config.tool_timeout_s, retry_transient=True)
                    active = [_item_view(r) for r in rows if r["qty"] > 0]
                    recipes = get_all_recipes(state.store, state.config.household_id)
                    match_res = match_recipes(active, max_minutes=max_min, recipes=recipes)
                    top = match_res.get("top_pick")
                    if top:
                        state.active_cooking = {
                            "recipe": top,
                            "step": 1,
                            "checked_prep": [],
                            "servings": top.get("servings", 2)
                        }
                        ing_lines = "\n".join(f"• {i['qty']} {i['unit']} {i['item']}" for i in top.get("ingredients", []))
                        card_txt = f"Recipe: {top['name']}\nPrep: {top.get('prep_minutes', 15)} mins | Servings: {top.get('servings', 2)}\n\nIngredients:\n{ing_lines}"
                        if state.is_screen_active():
                            screen_hint = "You can see the full recipe steps and timer right on your screen. Say 'next' when you're ready to start step 1."
                        else:
                            screen_hint = "Open and check, I have shared the recipe steps with your Sous-Chef screen companion. Would you like me to read Step 1 out loud?"
                        msg = f"{match_res['spoken_message']} {screen_hint}"
                    else:
                        msg = match_res["spoken_message"]
                        card_txt = msg
                    return JSONResponse(make_alexa_response(
                        msg,
                        card_title=f"Recipe: {top['name']}" if top else "Recipe Suggestions",
                        card_content=card_txt,
                        reprompt_text="Say 'next' to begin cooking, or ask for another suggestion."
                    ))

                if intent_name in ("AddInventoryIntent", "ManageInventoryIntent"):
                    food_item = (slots.get("FoodItem", {}).get("value") or "").strip()
                    qty_str = (slots.get("Quantity", {}).get("value") or "1").strip()
                    unit_str = (slots.get("Unit", {}).get("value") or "count").strip()
                    try:
                        qty_val = float(qty_str)
                    except ValueError:
                        qty_val = 1.0

                    if food_item:
                        try:
                            from ledger import normalize_unit
                            normalized_u = normalize_unit(unit_str)
                        except Exception:
                            normalized_u = "count"

                        ops = [{"type": "add", "item": food_item.lower(), "qty": qty_val, "unit": normalized_u, "zone": "pantry"}]
                        batch_res = await run_blocking(lambda: led.apply_batch(ops, idempotency_key=str(uuid.uuid4())),
                                                     state.config.tool_timeout_s, retry_transient=False)
                        msg = f"Added {qty_val:g} {unit_str} of {food_item} to your kitchen."
                        return JSONResponse(make_alexa_response(
                            msg,
                            card_title="Added to Kitchen",
                            card_content=f"Added: {qty_val:g} {unit_str} {food_item}",
                            reprompt_text="What else did you buy, or what would you like to cook?"
                        ))

                if intent_name == "DiscardInventoryIntent":
                    food_item = (slots.get("FoodItem", {}).get("value") or "").strip().lower()
                    if food_item:
                        rows = await run_blocking(led.list_items, state.config.tool_timeout_s, retry_transient=True)
                        active_items = {r["item"].lower().strip(): r for r in rows if r["qty"] > 0}
                        matched = active_items.get(food_item)
                        if not matched:
                            for name, r in active_items.items():
                                if food_item in name or name in food_item:
                                    matched = r
                                    break
                        if matched:
                            ops = [{"type": "discard", "item": matched["item"], "qty": matched["qty"], "unit": matched["unit"], "zone": matched["zone"]}]
                            await run_blocking(lambda: led.apply_batch(ops, idempotency_key=str(uuid.uuid4())),
                                               state.config.tool_timeout_s, retry_transient=False)
                            msg = f"I've removed the {matched['item']} from your kitchen."
                        else:
                            msg = f"I checked your kitchen, but you don't have {food_item} in stock."
                        return JSONResponse(make_alexa_response(
                            msg,
                            card_title="Discarded Item",
                            card_content=msg,
                            reprompt_text="What would you like to cook or check next?"
                        ))

                if intent_name == "CookingMishapIntent":
                    mishap = (slots.get("Mishap", {}).get("value") or "burned").strip().lower()
                    remedy_data = get_remedy_for_mishap(mishap)
                    return JSONResponse(make_alexa_response(
                        speech_text=remedy_data["spoken_message"],
                        card_title=f"Kitchen Rescue: {mishap.title()}",
                        card_content=f"Fix: {remedy_data.get('action', '')}\n\n{remedy_data.get('spoken_message', '')}",
                        reprompt_text="Say 'continue' or 'I checked it' to get back to your recipe."
                    ))

                if intent_name in ("CookingStepIntent", "AMAZON.NextIntent", "AMAZON.PreviousIntent"):
                    step_action = (slots.get("StepAction", {}).get("value") or ("previous" if intent_name == "AMAZON.PreviousIntent" else "next")).strip().lower()
                    if not state.active_cooking:
                        msg = "You don't have an active recipe cooking. Ask 'What can I make for dinner?' to start one!"
                        return JSONResponse(make_alexa_response(msg, reprompt_text="What would you like to cook?"))

                    recipe = state.active_cooking["recipe"]
                    steps = recipe.get("steps", [])

                    if any(w in step_action for w in ("done", "finished", "made", "complete")):
                        servings = float(state.active_cooking.get("servings", recipe.get("servings", 2)))
                        cook_res = await run_blocking(
                            lambda: execute_cooking_deduction(led, recipe, servings, str(uuid.uuid4()), state.store, state.config.household_id),
                            state.config.tool_timeout_s, retry_transient=False
                        )
                        state.last_cooked_meal = recipe
                        state.active_cooking = None
                        msg = cook_res["spoken_message"]
                        return JSONResponse(make_alexa_response(
                            msg,
                            card_title=f"Meal Logged: {recipe['name']}",
                            card_content=f"Cooked: {recipe['name']}\nServings: {servings}\n\nIngredients automatically deducted from kitchen ledger.",
                            end_session=False
                        ))
                    elif any(w in step_action for w in ("prev", "previous", "back", "repeat")):
                        # Move to previous step
                        curr = state.active_cooking["step"]
                        if curr > 1:
                            state.active_cooking["step"] -= 1
                        prev_s = steps[state.active_cooking["step"] - 1]
                        timer_hint = f" Set a {prev_s['timer_seconds'] // 60} minute timer if needed." if prev_s.get("timer_seconds") else ""
                        screen_hint = "You can see the step on your screen." if state.is_screen_active() else "Follow along on your Sous-Chef screen."
                        msg = f"Going back to Step {state.active_cooking['step']}: {prev_s['instruction']}{timer_hint} {screen_hint}"
                        return JSONResponse(make_alexa_response(
                            msg,
                            card_title=f"{recipe['name']} - Step {state.active_cooking['step']}",
                            card_content=msg,
                            reprompt_text="Say 'next' when ready to move on."
                        ))
                    else:
                        # Advance step
                        curr = state.active_cooking["step"]
                        if curr < len(steps):
                            state.active_cooking["step"] += 1
                            next_s = steps[state.active_cooking["step"] - 1]
                            timer_hint = f" Set a {next_s['timer_seconds'] // 60} minute timer if needed." if next_s.get("timer_seconds") else ""
                            if state.is_screen_active():
                                screen_hint = "You can see the step and timer on your screen."
                            else:
                                screen_hint = "Open and check your Sous-Chef screen companion anytime to follow along."
                            msg = f"Step {state.active_cooking['step']}: {next_s['instruction']}{timer_hint} {screen_hint}"
                        else:
                            msg = f"That was the final step for {recipe['name']}! Say 'I'm done' or 'I made it' to deduct the ingredients and log your nutrition."
                        return JSONResponse(make_alexa_response(
                            msg,
                            card_title=f"{recipe['name']} - Step {state.active_cooking['step']}",
                            card_content=msg,
                            reprompt_text="Say 'next' when ready, or 'I made it' when finished."
                        ))

                if intent_name == "NutritionIntent":
                    nutr = await run_blocking(lambda: get_daily_nutrition(state.store, state.config.household_id),
                                              state.config.tool_timeout_s, retry_transient=True)
                    return JSONResponse(make_alexa_response(
                        speech_text=nutr["spoken_summary"],
                        card_title="Daily Nutrition Summary",
                        card_content=f"Calories: {nutr.get('calories_today', 0)} kcal\nProtein: {nutr.get('protein_today_g', 0)}g\nMeals logged: {nutr.get('meals_logged', 0)}",
                        reprompt_text="What would you like to cook or check next?"
                    ))

                if intent_name == "SaveRecipeIntent":
                    rec_name = (slots.get("RecipeName", {}).get("value") or "My Recipe").strip().title()
                    ingredients = []
                    if state.active_cooking and state.active_cooking.get("recipe"):
                        ingredients = state.active_cooking["recipe"].get("ingredients", [])
                    elif state.last_cooked_meal and state.last_cooked_meal.get("ingredients"):
                        ingredients = state.last_cooked_meal.get("ingredients", [])

                    if ingredients:
                        recipe_uuid = str(uuid.uuid4())
                        servings = 2.0
                        prep_minutes = 15
                        with state.store.pool.connection() as conn:
                            conn.execute("INSERT INTO households (household_id) VALUES (%s) ON CONFLICT DO NOTHING", (state.config.household_id,))
                            conn.execute(
                                "INSERT INTO custom_recipes (recipe_id, household_id, name, servings, prep_minutes, ingredients, steps) "
                                "VALUES (%s, %s, %s, %s, %s, %s, %s) "
                                "ON CONFLICT (household_id, name) DO UPDATE SET "
                                "servings = EXCLUDED.servings, prep_minutes = EXCLUDED.prep_minutes, "
                                "ingredients = EXCLUDED.ingredients, steps = EXCLUDED.steps",
                                (recipe_uuid, state.config.household_id, rec_name, servings, prep_minutes,
                                 json.dumps(ingredients), json.dumps([]))
                            )
                        nutr = calculate_meal_nutrition(ingredients)
                        kcal = round(nutr["total_kcal"] / servings, 1)
                        prot = round(nutr["total_protein_g"] / servings, 1)
                        msg = f"Saved your recipe for {rec_name}! Each serving has approximately {kcal:.0f} calories and {prot:.0f} grams of protein."
                    else:
                        msg = f"I'd love to save '{rec_name}', but no recent meal was found. Try asking 'What can I make?' first!"
                    return JSONResponse(make_alexa_response(
                        msg,
                        card_title=f"Saved Recipe: {rec_name}",
                        card_content=msg,
                        reprompt_text="What would you like to cook next?"
                    ))

                # Fallback for unrecognized custom intents
                msg = "I heard your request. You can ask: 'What can I make in 15 minutes?', 'What is in my kitchen?', or 'I bought 2 eggs'."
                return JSONResponse(make_alexa_response(msg, reprompt_text="What would you like to cook?"))

        utterance = body.get("utterance", "")

        if state.store is None:
            return JSONResponse({"spoken_message": "Kitchen ledger is starting up. Please try again in a moment."})

        led = state.store.ledger(state.config.household_id)

        # Check if we were waiting for an answer to a clarifying question
        if state.pending_clarification:
            pending = state.pending_clarification
            state.pending_clarification = None
            combined_utterance = f"{pending['action']} {utterance}"
            res = parse_kitchen_utterance(combined_utterance)
            if not res.needs_clarification and res.items:
                ops = [{"type": res.action, "item": i.item, "qty": i.qty, "unit": i.unit, "zone": i.zone}
                       for i in res.items if i.qty is not None]
                if ops:
                    batch_res = await run_blocking(lambda: led.apply_batch(ops, idempotency_key=str(uuid.uuid4())),
                                                 state.config.tool_timeout_s, retry_transient=False)
                    names = [format_spoken_quantity(c['after'], c['unit'], c['item']) for c in batch_res.get("changes", [])]
                    msg = f"Got it! Added {', '.join(names)} to your kitchen."
                    return JSONResponse({"spoken_message": msg, "changes": batch_res.get("changes", [])})

        # Standard parse
        res = parse_kitchen_utterance(utterance)

        if res.needs_clarification:
            state.pending_clarification = {"action": res.action, "items": [i.item for i in res.items if i.needs_clarification]}
            return JSONResponse({"spoken_message": res.clarifying_question, "needs_clarification": True})

        if res.action == "query_all":
            rows = await run_blocking(led.list_items, state.config.tool_timeout_s, retry_transient=True)
            active = [r for r in rows if r["qty"] > 0]
            if not active:
                msg = "Your kitchen is currently empty. Tell me what groceries you bought to add them!"
            else:
                items_spoken = ", ".join(format_spoken_quantity(r['qty'], r['unit'], r['item']) for r in active[:4])
                msg = f"You have {len(active)} items in your kitchen: {items_spoken}."
            return JSONResponse({"spoken_message": msg, "items": [_item_view(r) for r in active]})

        elif res.action == "query_expiring":
            rows = await run_blocking(led.list_items, state.config.tool_timeout_s, retry_transient=True)
            cutoff = datetime.now(timezone.utc) + timedelta(hours=48)
            expiring = [r for r in rows if r["qty"] > 0 and r["expires_at"] and datetime.fromisoformat(r["expires_at"]) <= cutoff]
            if not expiring:
                msg = "Good news! Nothing is expiring in the next 48 hours."
            else:
                items_spoken = ", ".join(r["item"] for r in expiring)
                msg = f"Warning: {items_spoken} will expire within 48 hours. Consider using them for dinner!"
            return JSONResponse({"spoken_message": msg, "items": [_item_view(r) for r in expiring]})

        elif res.action == "discard" and res.items:
            names = [i.item for i in res.items]
            rows = await run_blocking(led.list_items, state.config.tool_timeout_s, retry_transient=True)
            active_items = {r["item"].lower().strip(): r for r in rows if r["qty"] > 0}
            to_discard_rows = []
            for name in names:
                if name in active_items:
                    to_discard_rows.append(active_items[name])
                else:
                    for a_name, r in active_items.items():
                        if name in a_name or a_name in name:
                            to_discard_rows.append(r)
                            break

            if not to_discard_rows:
                msg = f"I checked your kitchen, but you don't have {', '.join(names)} logged in stock right now."
                return JSONResponse({"spoken_message": msg})

            ops = [
                {
                    "type": "discard",
                    "item": r["item"],
                    "qty": r["qty"],
                    "unit": r["unit"],
                    "zone": r["zone"],
                }
                for r in to_discard_rows
            ]
            await run_blocking(lambda: led.apply_batch(ops, idempotency_key=str(uuid.uuid4())),
                               state.config.tool_timeout_s, retry_transient=False)
            names_discarded = [r["item"] for r in to_discard_rows]
            msg = f"I'm sorry to hear that. I'm removing the {', '.join(names_discarded)} from your kitchen."
            return JSONResponse({"spoken_message": msg, "discarded": names_discarded})

        elif res.action == "suggest_recipes":
            rows = await run_blocking(led.list_items, state.config.tool_timeout_s, retry_transient=True)
            active = [_item_view(r) for r in rows if r["qty"] > 0]
            recipes = get_all_recipes(state.store, state.config.household_id)
            goal = res.context.get("goal")
            max_min = res.context.get("max_minutes")
            match_res = match_recipes(active, goal=goal, max_minutes=max_min, recipes=recipes)
            top = match_res.get("top_pick")
            if top:
                state.active_cooking = {
                    "recipe": top,
                    "step": 1,
                    "checked_prep": [],
                    "servings": top.get("servings", 2)
                }
                if state.is_screen_active():
                    screen_hint = "You can see the full recipe steps and timer right on your screen."
                else:
                    screen_hint = "Open and check, I have shared the recipe steps with your Sous-Chef screen companion."
                spoken = f"{match_res['spoken_message']} {screen_hint}"
            else:
                spoken = match_res["spoken_message"]

            return JSONResponse({
                "spoken_message": spoken,
                "recipe": top,
                "suggestions": match_res.get("suggestions", []),
                "active_cooking": state.active_cooking,
                "screen_active": state.is_screen_active()
            })

        elif res.action == "kitchen_mishap":
            mishap_type = res.context.get("mishap_type", "general")
            remedy_data = get_remedy_for_mishap(mishap_type)
            return JSONResponse({
                "spoken_message": remedy_data["spoken_message"],
                "remedy": remedy_data,
                "active_cooking": state.active_cooking
            })

        elif res.action == "music_control":
            cmd = res.context.get("state", "play")
            msg = "Playing relaxing cooking music in your kitchen! 🎵" if cmd == "play" else "Paused cooking music."
            return JSONResponse({
                "spoken_message": msg,
                "music_command": cmd,
                "active_cooking": state.active_cooking
            })

        elif res.action == "timer_control":
            cmd = res.context.get("state", "start")
            msg = "Starting your step timer." if cmd == "start" else "Step timer paused."
            return JSONResponse({
                "spoken_message": msg,
                "timer_command": cmd,
                "active_cooking": state.active_cooking
            })

        elif res.action == "confirm_action":
            if state.active_cooking:
                recipe = state.active_cooking["recipe"]
                steps = recipe.get("steps", [])
                curr = state.active_cooking["step"]
                if curr < len(steps):
                    state.active_cooking["step"] += 1
                    next_s = steps[state.active_cooking["step"] - 1]
                    timer_hint = f" Set a {next_s['timer_seconds'] // 60} minute timer if needed." if next_s.get("timer_seconds") else ""
                    msg = f"Awesome! Stove is stopped and food is checked. Going back to your cooking flow! Step {state.active_cooking['step']}: {next_s['instruction']}{timer_hint}"
                else:
                    msg = f"Awesome! Stove is stopped and food is checked. That was your final step for {recipe['name']}! Say 'I made it' or 'I finished' to deduct your ingredients and log your nutrition."
                return JSONResponse({
                    "spoken_message": msg,
                    "action_confirmed": True,
                    "resume_music": True,
                    "active_cooking": state.active_cooking
                })
            else:
                msg = "All checked and set in your kitchen!"
                return JSONResponse({"spoken_message": msg})

        elif res.action == "check_prep_item":
            item_name = res.context.get("checked_item", "").lower()
            if state.active_cooking:
                recipe = state.active_cooking["recipe"]
                matched_ing = None
                for ing in recipe.get("ingredients", []):
                    if item_name in ing["item"].lower() or ing["item"].lower() in item_name:
                        matched_ing = ing["item"]
                        break
                checked_item = matched_ing or item_name
                if checked_item not in state.active_cooking["checked_prep"]:
                    state.active_cooking["checked_prep"].append(checked_item)

                all_ings = [i["item"] for i in recipe.get("ingredients", [])]
                remaining = [i for i in all_ings if i not in state.active_cooking["checked_prep"]]
                if not remaining:
                    steps = recipe.get("steps", [])
                    first_step = steps[0]["instruction"] if steps else "Start cooking!"
                    msg = f"Awesome! All ingredients for {recipe['name']} are ready! Step 1: {first_step}. Say 'Next' when you're ready!"
                else:
                    msg = f"Got it! Checked off {checked_item}. You still need {remaining[0]}."
                return JSONResponse({"spoken_message": msg, "active_cooking": state.active_cooking})
            else:
                msg = f"Got the {item_name}! Ask 'What can I make for dinner?' to start a recipe."
                return JSONResponse({"spoken_message": msg})

        elif res.action == "next_step":
            if state.active_cooking:
                recipe = state.active_cooking["recipe"]
                steps = recipe.get("steps", [])
                curr = state.active_cooking["step"]
                if curr < len(steps):
                    state.active_cooking["step"] += 1
                    next_s = steps[state.active_cooking["step"] - 1]
                    timer_hint = f" Set a {next_s['timer_seconds'] // 60} minute timer if needed." if next_s.get("timer_seconds") else ""
                    msg = f"Step {state.active_cooking['step']}: {next_s['instruction']}{timer_hint}"
                else:
                    msg = f"That was the final step for {recipe['name']}! Say 'I made it' or 'I'm done' to deduct the ingredients and log your nutrition."
                return JSONResponse({"spoken_message": msg, "active_cooking": state.active_cooking})
            else:
                msg = "You don't have an active recipe cooking. Say 'What can I make for dinner?' to start one!"
                return JSONResponse({"spoken_message": msg})

        elif res.action == "resume_cooking":
            if state.active_cooking:
                recipe = state.active_cooking["recipe"]
                steps = recipe.get("steps", [])
                curr = state.active_cooking["step"]
                curr_s = steps[curr - 1] if steps and curr <= len(steps) else {"instruction": "Cooking"}
                msg = f"Welcome back! You're making {recipe['name']} on Step {curr} of {len(steps)}: {curr_s['instruction']}. Say 'Next' when ready."
                return JSONResponse({"spoken_message": msg, "active_cooking": state.active_cooking})
            else:
                msg = "You're all caught up! No recipe is currently in progress."
                return JSONResponse({"spoken_message": msg})

        elif res.action == "cook_recipe":
            recipe = None
            if state.active_cooking:
                recipe = state.active_cooking["recipe"]
            else:
                rec_name = res.context.get("recipe_name", "")
                if rec_name:
                    recipe = find_recipe_by_id(rec_name, state.store, state.config.household_id)
                if not recipe:
                    rows = await run_blocking(led.list_items, state.config.tool_timeout_s, retry_transient=True)
                    active = [_item_view(r) for r in rows if r["qty"] > 0]
                    match_res = match_recipes(active)
                    recipe = match_res.get("top_pick")

            if not recipe:
                msg = "I'm not sure which recipe you cooked. You can say 'I made Grandma's Chili' or ask 'What can I make?'"
                return JSONResponse({"spoken_message": msg})

            servings = float(state.active_cooking.get("servings", recipe.get("servings", 2))) if state.active_cooking else 2.0
            cook_res = await run_blocking(
                lambda: execute_cooking_deduction(led, recipe, servings, str(uuid.uuid4()), state.store, state.config.household_id),
                state.config.tool_timeout_s, retry_transient=False
            )
            state.last_cooked_meal = recipe
            state.active_cooking = None
            msg = cook_res["spoken_message"]
            if not recipe.get("tags") or "custom" in recipe.get("tags", []):
                msg += " Say 'Save this as...' if you'd like to add it to your permanent recipes!"
            return JSONResponse({"spoken_message": msg, "meal": cook_res, "active_cooking": None})

        elif res.action == "save_recipe":
            rec_name = res.context.get("recipe_name", "My Custom Recipe").strip().title()
            ingredients = []
            if res.items:
                ingredients = [{"item": i.item, "qty": i.qty or 1.0, "unit": i.unit or "count"} for i in res.items]
            elif state.active_cooking and state.active_cooking.get("recipe"):
                ingredients = state.active_cooking["recipe"].get("ingredients", [])
            elif state.last_cooked_meal and state.last_cooked_meal.get("ingredients"):
                ingredients = state.last_cooked_meal.get("ingredients", [])

            if not ingredients:
                msg = f"I'd love to save '{rec_name}'! What ingredients did you use?"
                state.pending_clarification = {"action": f"save recipe {rec_name} with"}
                return JSONResponse({"spoken_message": msg})

            recipe_uuid = str(uuid.uuid4())
            servings = 2.0
            prep_minutes = 15
            with state.store.pool.connection() as conn:
                conn.execute("INSERT INTO households (household_id) VALUES (%s) ON CONFLICT DO NOTHING", (state.config.household_id,))
                conn.execute(
                    "INSERT INTO custom_recipes (recipe_id, household_id, name, servings, prep_minutes, ingredients, steps) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s) "
                    "ON CONFLICT (household_id, name) DO UPDATE SET "
                    "servings = EXCLUDED.servings, prep_minutes = EXCLUDED.prep_minutes, "
                    "ingredients = EXCLUDED.ingredients, steps = EXCLUDED.steps",
                    (recipe_uuid, state.config.household_id, rec_name, servings, prep_minutes,
                     json.dumps(ingredients), json.dumps([]))
                )
            nutr = calculate_meal_nutrition(ingredients)
            kcal = round(nutr["total_kcal"] / servings, 1)
            prot = round(nutr["total_protein_g"] / servings, 1)
            msg = f"Saved your recipe for {rec_name}! Each serving has approximately {kcal:.0f} calories and {prot:.0f}g protein. You can ask me to cook it anytime!"
            return JSONResponse({
                "spoken_message": msg,
                "saved_recipe": {
                    "id": recipe_uuid,
                    "name": rec_name,
                    "ingredients": ingredients,
                    "servings": servings,
                    "prep_minutes": prep_minutes,
                    "kcal_per_serving": kcal,
                    "protein_per_serving": prot
                }
            })

        elif res.action == "query_nutrition":
            nutr = await run_blocking(lambda: get_daily_nutrition(state.store, state.config.household_id),
                                      state.config.tool_timeout_s, retry_transient=True)
            return JSONResponse({"spoken_message": nutr["spoken_summary"], "nutrition": nutr})

        elif res.action == "undo":
            undo_res = await run_blocking(lambda: led.undo(idempotency_key=str(uuid.uuid4())),
                                     state.config.tool_timeout_s, retry_transient=False)
            names = undo_res.get("items", [])
            msg = f"Undid your last change. Restored {', '.join(names)}."
            return JSONResponse({"spoken_message": msg, "undone": names})

        elif res.action == "move_zone" and res.items:
            target_zone = res.context.get("target_zone", "fridge")
            moved_names = []
            for i in res.items:
                exp_dt, _, _ = calculate_shelf_life(i.item, target_zone)
                with state.store.pool.connection() as conn:
                    conn.execute(
                        "UPDATE inventory SET zone=%s, expires_at=%s, updated_at=now() "
                        "WHERE household_id=%s AND item=%s",
                        (target_zone, exp_dt, state.config.household_id, i.item)
                    )
                moved_names.append(i.item)
            zone_display = "refrigerator" if target_zone == "fridge" else target_zone
            msg = f"Moved your {', '.join(moved_names)} to the {zone_display} and refreshed shelf-life!"
            return JSONResponse({"spoken_message": msg, "moved": moved_names, "target_zone": target_zone})

        elif res.action in ("add", "consume") and res.items:
            ops = []
            warnings = []
            advisories = []
            if res.action == "add":
                existing_rows = await run_blocking(led.list_items, state.config.tool_timeout_s, retry_transient=True)
                existing_map = {r["item"]: r for r in existing_rows if r["qty"] > 0}
                for i in res.items:
                    if i.qty is None:
                        continue
                    exp_dt, is_perishable_outside, warn = calculate_shelf_life(i.item, i.zone)
                    if warn:
                        warnings.append(warn)
                    if i.item in existing_map:
                        ex = existing_map[i.item]
                        adv = generate_duplicate_batch_advisory(
                            i.item, ex["qty"], ex["unit"], ex["expires_at"], i.zone, ex["zone"]
                        )
                        if adv:
                            advisories.append(adv)
                    ops.append({
                        "type": "add",
                        "item": i.item,
                        "qty": i.qty,
                        "unit": i.unit,
                        "zone": i.zone,
                        "expires_at": exp_dt.isoformat()
                    })
            else:
                ops = [{"type": "consume", "item": i.item, "qty": i.qty, "unit": i.unit, "zone": i.zone}
                       for i in res.items if i.qty is not None]

            if ops:
                batch_res = await run_blocking(lambda: led.apply_batch(ops, idempotency_key=str(uuid.uuid4())),
                                             state.config.tool_timeout_s, retry_transient=False)
                names = [format_spoken_quantity(c['after'], c['unit'], c['item']) for c in batch_res.get("changes", [])]
                action_word = "Added" if res.action == "add" else "Used"
                msg = f"{action_word} {', '.join(names)} in your kitchen."
                if advisories:
                    msg += " " + " ".join(advisories)
                if warnings:
                    msg += " " + " ".join(warnings)
                return JSONResponse({"spoken_message": msg, "changes": batch_res.get("changes", [])})

        msg = f"I heard: '{utterance}'. You can ask 'What can I make in 15 minutes?', 'The milk is spoiled', or 'What is in my kitchen?'."
        return JSONResponse({"spoken_message": msg})

    @asynccontextmanager
    async def lifespan(_app):
        try:
            state.store = await anyio.to_thread.run_sync(factory, config)
        except Exception:  # noqa: BLE001
            log.exception(json.dumps({"event": "store_open_failed"}))
        log.info(json.dumps({"event": "startup", "server": SERVER_NAME,
                             "auth": bool(config.auth_token)}))
        try:
            async with mcp.session_manager.run():
                yield
        finally:
            if state.store is not None:
                await anyio.to_thread.run_sync(state.store.close)
            log.info(json.dumps({"event": "shutdown"}))

    app = Starlette(routes=[Route("/", serve_index, methods=["GET"]),
                            Route("/style.css", serve_style, methods=["GET"]),
                            Route("/app.js", serve_app, methods=["GET"]),
                            Route("/manifest.json", serve_manifest, methods=["GET"]),
                            Route("/sw.js", serve_sw, methods=["GET"]),
                            Route("/api/inventory", api_inventory, methods=["GET"]),
                            Route("/api/inventory/move", api_inventory_move, methods=["POST"]),
                            Route("/api/nutrition", api_nutrition, methods=["GET"]),
                            Route("/api/recipes", api_recipes, methods=["GET", "POST"]),
                            Route("/api/cooking", api_cooking, methods=["GET", "POST"]),
                            Route("/api/presence", api_presence, methods=["GET", "POST"]),
                            Route("/api/tts", api_tts, methods=["GET"]),
                            Route("/api/converse", api_converse, methods=["POST"]),
                            Route("/alexa", api_converse, methods=["POST"]),
                            Route("/healthz", healthz, methods=["GET"]),
                            Route("/readyz", readyz, methods=["GET"]),
                            Mount("/", app=mcp_app)],
                    lifespan=lifespan)

    app.state.kitchen = state
    return BearerAuth(app, config.auth_token)


def main() -> None:
    import uvicorn

    config = Config.from_env()
    setup_logging(config.log_level)
    uvicorn.run(build_app(config), host=config.host, port=config.port,
                log_level=config.log_level.lower(), timeout_graceful_shutdown=10)


if __name__ == "__main__":
    main()
