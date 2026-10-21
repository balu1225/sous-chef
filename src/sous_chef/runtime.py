"""Shared plumbing every MCP tool goes through (PDD Sections 10.4 and 15).

- One response envelope: {"ok": true, ...} or {"ok": false, "error": {...}}.
- Errors are short, speakable and safe: never stack traces or SQL text.
  Full details go to the server log only.
- Blocking ledger calls run in a worker thread so they never stall the
  event loop, and every call has a hard timeout.
- Reads are retried once on a transient database failure. Writes are never
  retried here; a client retry with the same idempotency key is the only
  safe write retry, and the ledger already handles that.
- One structured JSON log line per tool call.
"""
from __future__ import annotations

import hashlib
import json
import logging
import sys
import time
import uuid
from typing import Any, Callable

import anyio
import psycopg
from mcp.types import CallToolResult, TextContent
from psycopg_pool import PoolTimeout

from ledger import LedgerError

log = logging.getLogger("kitchen_agent")

DB_DOWN_MESSAGE = "I can't reach your kitchen data right now. Please try again in a moment."
TIMEOUT_MESSAGE = "That took too long. Please try again."
INTERNAL_MESSAGE = "Something went wrong on my side. Your data is safe."


class ToolFailure(Exception):
    """A failure we deliberately report to the caller."""

    def __init__(self, code: str, message: str, retryable: bool = False):
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable


TRANSIENT = (psycopg.OperationalError, PoolTimeout)


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root = logging.getLogger("kitchen_agent")
    root.handlers[:] = [handler]
    root.setLevel(level)
    root.propagate = False


def hash_household(household_id: str) -> str:
    """Logs carry a hashed household id, never the raw one."""
    return hashlib.sha256(household_id.encode()).hexdigest()[:12]


def _envelope(payload: dict, is_error: bool) -> CallToolResult:
    text = json.dumps(payload, default=str, separators=(",", ":"))
    return CallToolResult(content=[TextContent(type="text", text=text)],
                          structuredContent=payload, isError=is_error)


def success(data: dict) -> CallToolResult:
    return _envelope({"ok": True, **data}, is_error=False)


def failure(code: str, message: str, retryable: bool) -> CallToolResult:
    return _envelope({"ok": False, "error": {"code": code, "message": message,
                                             "retryable": retryable}}, is_error=True)


def classify(exc: BaseException) -> ToolFailure:
    """Map any exception to a safe, speakable failure."""
    if isinstance(exc, ToolFailure):
        return exc
    if isinstance(exc, LedgerError):
        # Ledger messages are written for users ("Unknown unit 'bushel'").
        return ToolFailure("invalid_request", str(exc))
    if isinstance(exc, TRANSIENT):
        return ToolFailure("db_unavailable", DB_DOWN_MESSAGE, retryable=True)
    if isinstance(exc, TimeoutError):
        return ToolFailure("timeout", TIMEOUT_MESSAGE, retryable=True)
    return ToolFailure("internal", INTERNAL_MESSAGE)


async def run_blocking(fn: Callable[[], Any], timeout_s: float, *,
                       retry_transient: bool) -> Any:
    """Run a blocking call in a thread with a hard timeout.

    The Postgres statement_timeout bounds the abandoned thread's work if the
    caller gives up first, so nothing runs unbounded in the background.
    """
    attempts = 2 if retry_transient else 1
    deadline = time.monotonic() + timeout_s
    for attempt in range(1, attempts + 1):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError
        try:
            with anyio.fail_after(remaining):
                return await anyio.to_thread.run_sync(fn, abandon_on_cancel=True)
        except TRANSIENT:
            if attempt == attempts:
                raise
            log.warning(json.dumps({"event": "read_retry", "attempt": attempt}))
            await anyio.sleep(0.1)


async def run_tool(tool: str, household_id: str, request_id: Any,
                   handler: Callable[[], Any]) -> CallToolResult:
    """Execute a tool handler (an async callable returning a dict) inside the
    standard envelope, error mapping and logging."""
    call_id = uuid.uuid4().hex[:16]
    started = time.perf_counter()
    try:
        data = await handler()
        result, outcome, code = success(data), "ok", None
    except Exception as exc:  # noqa: BLE001 - every failure must be mapped
        # Cancellation (client went away) is a BaseException and passes through.
        fail = classify(exc)
        if fail.code == "internal":
            log.error(json.dumps({"event": "tool_crash", "tool": tool,
                                  "call_id": call_id}), exc_info=exc)
        result, outcome, code = failure(fail.code, fail.message, fail.retryable), "error", fail.code
    log.info(json.dumps({
        "event": "tool_call", "tool": tool, "call_id": call_id,
        "jsonrpc_id": request_id, "household": hash_household(household_id),
        "duration_ms": round((time.perf_counter() - started) * 1000, 1),
        "outcome": outcome, "error_code": code}, default=str))
    return result
