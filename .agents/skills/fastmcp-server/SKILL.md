---
name: fastmcp-server
description: Standards, architecture blueprints, and reliability rules for building FastMCP 1.30.0 Streamable HTTP servers for Sous-Chef.
---

# FastMCP Server Engineering Standard

## 1. Pinned Dependencies & Transports
- **MCP Python SDK:** Pin strictly to `mcp>=1.30.0,<2.0.0` (FastMCP). Do NOT upgrade to 2.x (which renames FastMCP to `MCPServer` and changes protocols).
- **Protocol:** Negotiates official protocol `2025-11-25`.
- **Transport:** Streamable HTTP on `/mcp/<secret-token>`. Do NOT use deprecated HTTP+SSE.
- **Port:** Default `8000` (or `PORT` environment variable).

## 2. Mandatory Reliability Wrapper (Decisions D3 & D4)
FastMCP 1.x runs sync tool functions directly on the asynchronous event loop. A slow database query or network stall blocks all concurrent requests.
**Rule:** Every tool handler MUST be wrapped with a threadpool executor and a hard **4.0-second timeout cap**:

```python
import concurrent.futures
from functools import wraps
from typing import Any, Callable, Dict

executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

def safe_tool(timeout_seconds: float = 4.0) -> Callable:
    """Wraps sync ledger calls in a worker thread with a hard timeout cap.
    Guarantees that a slow DB call never starves the event loop and always returns
    a spoken-safe error envelope before the voice assistant times out.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Dict[str, Any]:
            future = executor.submit(func, *args, **kwargs)
            try:
                return future.result(timeout=timeout_seconds)
            except concurrent.futures.TimeoutError:
                return {
                    "ok": False,
                    "error": {
                        "code": "db_timeout",
                        "message": "Kitchen ledger took too long to respond. Please try again in a moment.",
                        "retryable": True
                    }
                }
            except Exception as exc:
                return {
                    "ok": False,
                    "error": {
                        "code": "internal_error",
                        "message": "A temporary error occurred in the kitchen ledger.",
                        "retryable": True
                    }
                }
        return wrapper
    return decorator
```

## 3. Strict Response Envelope (PDD Section 9 & Decision D3)
Raw database exceptions, stack traces, and SQL queries MUST NEVER reach the voice client or user.
Every tool must return one of two structured dictionaries:

### Success Response:
```json
{
  "ok": true,
  "<resource_key>": ...
}
```

### Error Response:
```json
{
  "ok": false,
  "error": {
    "code": "string_identifier",
    "message": "Spoken-friendly message suitable for TTS",
    "retryable": true
  }
}
```

Standard error codes:
- `db_timeout`: Query took longer than 4.0 seconds.
- `db_unavailable`: Connection pool exhausted or database offline.
- `invalid_input`: Missing or malformed parameters.
- `item_not_found`: Requested item is not present in inventory.
- `insufficient_stock`: Not enough quantity to deduct.
- `unit_mismatch`: Attempting to mix count/weight/volume units.

## 4. Health Checks (Decision D9)
The server MUST boot even if the database is temporarily offline or waking up.
Expose two Starlette routes:
1. `GET /health/live`: Returns `{"status": "alive"}` immediately (HTTP 200).
2. `GET /health/ready`: Probes the database connection pool (`SELECT 1`). Returns HTTP 200 if connected, or HTTP 503 `{"status": "degraded", "db": "unavailable"}` if cold/down.

## 5. Idempotency Key Handling
All write tools (`manage_inventory`, `undo_last_change`, `cook_recipe`) require an `idempotency_key` (UUID or client-generated string per utterance).
- If the same key is received again, return the exact previous result without duplicating ledger events.

## 6. Implementation Checklist
- [ ] Dependencies pinned: `mcp>=1.30.0,<2.0.0`, `starlette`, `uvicorn`, `psycopg2-binary`.
- [ ] FastMCP initialized with `title="Sous-Chef"`.
- [ ] Routes mounted: `/mcp/<secret-path>`, `/health/live`, `/health/ready`.
- [ ] All `@mcp.tool()` handlers wrapped with `@safe_tool(timeout_seconds=4.0)`.
- [ ] Server boot verified without a running database.
