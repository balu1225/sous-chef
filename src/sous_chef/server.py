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
from typing import Annotated, Callable
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
                          "/api/inventory", "/api/converse"})


@dataclass
class State:
    config: Config
    store: Store | None = None
    pending_clarification: dict | None = None


# --------------------------------------------------------------------------
# Tools
# --------------------------------------------------------------------------
def _item_view(row: dict) -> dict:
    """Section 9 output shape. Confidence scoring arrives in P2 (FR-6)."""
    return {"item": row["item"], "qty": row["qty"], "unit": row["unit"],
            "zone": row["zone"], "expires_at": row["expires_at"],
            "confidence": None}


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
        return JSONResponse({"status": "ok"})

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

    async def api_inventory(_: Request) -> JSONResponse:
        if state.store is None:
            return JSONResponse({"items": []})
        led = state.store.ledger(state.config.household_id)
        rows = await run_blocking(led.list_items, state.config.tool_timeout_s, retry_transient=True)
        active = [_item_view(r) for r in rows if r["qty"] > 0]
        return JSONResponse({"items": active, "count": len(active)})

    async def api_converse(request: Request) -> JSONResponse:
        body = await request.json()
        utterance = body.get("utterance", "")

        if state.store is None:
            return JSONResponse({"spoken_message": "Kitchen ledger is starting up. Please try again in a moment."})

        led = state.store.ledger(state.config.household_id)

        # Check if we were waiting for an answer to a clarifying question
        if state.pending_clarification:
            pending = state.pending_clarification
            state.pending_clarification = None
            # Combine previous pending items with the new utterance
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

        elif res.action == "undo":
            undo_res = await run_blocking(lambda: led.undo(idempotency_key=str(uuid.uuid4())),
                                     state.config.tool_timeout_s, retry_transient=False)
            names = undo_res.get("items", [])
            msg = f"Undid your last change. Restored {', '.join(names)}."
            return JSONResponse({"spoken_message": msg, "undone": names})

        elif res.action in ("add", "consume") and res.items:
            ops = [{"type": res.action, "item": i.item, "qty": i.qty, "unit": i.unit, "zone": i.zone}
                   for i in res.items if i.qty is not None]
            if ops:
                batch_res = await run_blocking(lambda: led.apply_batch(ops, idempotency_key=str(uuid.uuid4())),
                                             state.config.tool_timeout_s, retry_transient=False)
                names = [format_spoken_quantity(c['after'], c['unit'], c['item']) for c in batch_res.get("changes", [])]
                action_word = "Added" if res.action == "add" else "Used"
                msg = f"{action_word} {', '.join(names)} in your kitchen."
                return JSONResponse({"spoken_message": msg, "changes": batch_res.get("changes", [])})

        msg = f"I heard: '{utterance}'. You can ask 'What's in my kitchen?', 'What is about to expire?', or say 'I bought 2 gallons of milk'."
        return JSONResponse({"spoken_message": msg})

    @asynccontextmanager
    async def lifespan(_app):
        # Opening the pool does not block on the database: if it is down at
        # boot, the server still starts, /readyz reports it, tools return a
        # speakable error, and the pool keeps reconnecting in the background.
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
                            Route("/api/inventory", api_inventory, methods=["GET"]),
                            Route("/api/converse", api_converse, methods=["POST"]),
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
