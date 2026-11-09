---
name: python-fastapi
description: "Build and review modern Python services with FastAPI, Pydantic v2, async SQLAlchemy, typing, uv/ruff/pytest. Use when writing Python APIs, workers or data-facing backends."
license: MIT
metadata:
  version: "1.0.0"
---

# Python / FastAPI

Pair with `api-design`, `secure-by-design-coding`, `postgres`, `observability`, `test-strategy`.

## Tooling
- Python >= 3.12, `uv` (or Poetry) with a lockfile; `pyproject.toml` single source of config. `ruff` (lint+format), `mypy --strict` or `pyright`, `pytest`, `pre-commit`.
- Layout: `src/<pkg>/{api,services,repositories,models,schemas,core}`; `api` thin, business logic in `services`, no framework imports in the domain.

## FastAPI essentials
- Pydantic v2 models for request/response; `response_model` on every route (prevents leaking fields); `model_config = ConfigDict(extra="forbid")` on inputs; constrained types (`conint`, `EmailStr`, `StringConstraints`).
- Dependencies (`Depends`) for DB session, auth, settings; settings via `pydantic-settings` loaded once; no globals.
- `async def` only when every call inside is non-blocking (async DB driver, `httpx.AsyncClient`); otherwise use plain `def` (runs in the threadpool). Never call blocking code (requests, sync SQLAlchemy, `time.sleep`) inside `async def`; use `run_in_threadpool`.
- Lifespan context for startup/shutdown (create/close pools and HTTP clients once). Background work: queue (Celery/Arq/RQ), not `BackgroundTasks` for anything important.
- Errors: custom exceptions + exception handlers returning RFC 9457 problem JSON; `HTTPException` only at the edge.

## Data (SQLAlchemy 2.x)
Async engine + `async_sessionmaker`, one session per request, explicit transaction boundaries, `selectinload`/`joinedload` to avoid N+1, Alembic migrations (reversible, reviewed autogenerate). Parameterized queries only; never f-string SQL.

## Security
OAuth2/JWT via a vetted library, short-lived tokens, per-object authorization in the service layer, password hashing with argon2/bcrypt, CORS allow-list, request size limits, rate limiting, no `eval/pickle` on untrusted data, `bandit` + `pip-audit` in CI.

## Performance & ops
Uvicorn/Gunicorn workers sized to CPU, `uvloop`, connection pools sized to DB, `orjson` responses for hot paths, caching with explicit TTL and invalidation, pagination everywhere. Health/readiness endpoints, structured logs (`structlog`), OTel instrumentation. Docker: multi-stage with `uv`, non-root, slim base.

## Testing
`pytest` + `httpx.AsyncClient` (ASGI transport), `pytest-asyncio`, factories (`factory_boy`/polyfactory), Testcontainers for Postgres, `freezegun`/injected clock, property tests with Hypothesis for parsers and invariants, coverage floor on changed code.

## Review checklist
Typed and `mypy` clean - `response_model` set - no blocking calls in async paths - sessions/transactions scoped - migrations reversible - secrets from env - tests for 4xx/5xx paths - dependencies audited.
