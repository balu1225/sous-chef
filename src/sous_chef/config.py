"""Server configuration, read once from environment variables at startup.

Bad configuration fails fast with a clear message instead of surfacing later
as a confusing runtime error. Secrets come only from the environment, never
from the repo (PDD Section 14).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

from ledger import LedgerError, check_household

load_dotenv()


class ConfigError(RuntimeError):
    """Raised when the environment is missing or has an invalid setting."""


def _int(env, name: str, default: int, lo: int, hi: int) -> int:
    raw = env.get(name)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except ValueError:
        raise ConfigError(f"{name} must be an integer, got {raw!r}") from None
    if not lo <= value <= hi:
        raise ConfigError(f"{name} must be between {lo} and {hi}, got {value}")
    return value


def _float(env, name: str, default: float, lo: float, hi: float) -> float:
    raw = env.get(name)
    if raw is None or raw == "":
        return default
    try:
        value = float(raw)
    except ValueError:
        raise ConfigError(f"{name} must be a number, got {raw!r}") from None
    if not lo <= value <= hi:
        raise ConfigError(f"{name} must be between {lo} and {hi}, got {value}")
    return value


def _bool(env, name: str) -> bool:
    return env.get(name, "").strip().lower() in ("1", "true", "yes")


def _list(env, name: str) -> list[str]:
    return [p.strip() for p in env.get(name, "").split(",") if p.strip()]


@dataclass(frozen=True)
class Config:
    database_url: str
    household_id: str
    auth_token: str | None
    host: str = "127.0.0.1"
    port: int = 8000
    allowed_hosts: list[str] = field(default_factory=list)
    allowed_origins: list[str] = field(default_factory=list)
    db_pool_max: int = 5
    db_acquire_timeout_s: float = 2.5
    db_statement_timeout_ms: int = 3000
    tool_timeout_s: float = 8.0
    log_level: str = "INFO"

    @classmethod
    def from_env(cls, env=None) -> "Config":
        env = os.environ if env is None else env

        database_url = env.get("KITCHEN_DATABASE_URL", "").strip()
        if not database_url:
            raise ConfigError("KITCHEN_DATABASE_URL is required")

        # R1 serves one household. Per-household OAuth replaces this (FR-23).
        try:
            household_id = check_household(env.get("KITCHEN_HOUSEHOLD_ID", "").strip())
        except LedgerError:
            raise ConfigError("KITCHEN_HOUSEHOLD_ID is required: 1-64 chars of "
                              "letters, digits, '-' or '_'") from None

        auth_token = env.get("KITCHEN_AUTH_TOKEN", "").strip() or None
        if auth_token is None and not _bool(env, "KITCHEN_ALLOW_NO_AUTH"):
            raise ConfigError("KITCHEN_AUTH_TOKEN is required (or set "
                              "KITCHEN_ALLOW_NO_AUTH=1 for local development only)")
        if auth_token is not None and len(auth_token) < 32:
            raise ConfigError("KITCHEN_AUTH_TOKEN must be at least 32 characters")

        log_level = env.get("KITCHEN_LOG_LEVEL", "INFO").strip().upper()
        if log_level not in ("DEBUG", "INFO", "WARNING", "ERROR"):
            raise ConfigError("KITCHEN_LOG_LEVEL must be DEBUG, INFO, WARNING or ERROR")

        # Hosting platforms commonly inject PORT; KITCHEN_PORT wins if both exist.
        port_env = dict(env)
        if not port_env.get("KITCHEN_PORT") and port_env.get("PORT"):
            port_env["KITCHEN_PORT"] = port_env["PORT"]

        return cls(
            database_url=database_url,
            household_id=household_id,
            auth_token=auth_token,
            host=env.get("KITCHEN_HOST", "127.0.0.1").strip() or "127.0.0.1",
            port=_int(port_env, "KITCHEN_PORT", 8000, 1, 65535),
            allowed_hosts=_list(env, "KITCHEN_ALLOWED_HOSTS"),
            allowed_origins=_list(env, "KITCHEN_ALLOWED_ORIGINS"),
            db_pool_max=_int(env, "KITCHEN_DB_POOL_MAX", 5, 1, 50),
            db_acquire_timeout_s=_float(env, "KITCHEN_DB_ACQUIRE_TIMEOUT_S", 2.5, 0.5, 60),
            db_statement_timeout_ms=_int(env, "KITCHEN_DB_STATEMENT_TIMEOUT_MS",
                                         3000, 100, 60000),
            tool_timeout_s=_float(env, "KITCHEN_TOOL_TIMEOUT_S", 8.0, 1, 60),
            log_level=log_level,
        )
