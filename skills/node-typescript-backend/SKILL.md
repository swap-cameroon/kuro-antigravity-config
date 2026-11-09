---
name: node-typescript-backend
description: "Build production Node.js/TypeScript backends (Fastify, NestJS, Express): structure, validation, async, errors, config, testing, performance. Use when writing or reviewing Node/TS services or APIs."
license: MIT
metadata:
  version: "1.0.0"
---

# Node.js / TypeScript backend

Pair with `api-design`, `secure-by-design-coding`, `postgres`, `observability`, `test-strategy`.

## Project
- TypeScript `strict: true` (+ `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`), ESM, Node LTS pinned via `.nvmrc`/`engines`. ESLint (typescript-eslint, `no-floating-promises`, `no-misused-promises`) + Prettier. `pnpm` or `npm ci` with a committed lockfile.
- Layers: `routes/controllers` (HTTP only) -> `services` (business rules, no HTTP types) -> `repositories` (data access) ; domain types independent of the framework. Dependency injection by constructor/factory (NestJS DI or plain functions) so tests can swap adapters.
- Framework: Fastify for lean/fast services (schema-first, plugins); NestJS when the team wants opinionated modules/DI; Express only for small or legacy code.

## Validation & config
- Validate **all** external input at the boundary with Zod/TypeBox/Valibot (or Fastify JSON schema); infer types from schemas; never trust `req.body as T`.
- Config from env, parsed once with a schema at startup (fail fast); no `process.env` scattered in code; secrets from the platform, never in the repo.

## Async & errors
- `async/await` everywhere; always await or handle promises; use `Promise.allSettled`/bounded concurrency (`p-limit`) instead of unbounded `Promise.all` over user-sized arrays.
- Never block the event loop: no sync fs/crypto/JSON.parse of huge payloads on hot paths; offload CPU work to worker threads or a queue.
- Typed domain errors mapped centrally to HTTP problem responses; one error handler; do not leak stack traces. Handle `unhandledRejection` by logging and exiting (let the orchestrator restart).
- Timeouts + `AbortSignal` on every outbound call; retries with jitter only for idempotent operations (`http-resilience`).

## Data
- Parameterized queries only (Prisma/Drizzle/Kysely/knex); explicit transactions for multi-step writes; migrations versioned and reversible; avoid N+1 (batch/dataloader); pool sized to DB limits.

## Production
- Graceful shutdown (SIGTERM: stop accepting, drain, close pools, then exit). Health endpoints: liveness (process) vs readiness (dependencies).
- Structured logging with pino + request IDs; OTel auto-instrumentation; `helmet`, CORS allow-list, rate limiting, body size limits.
- Docker: multi-stage, `node:<lts>-slim`/distroless, non-root, `NODE_ENV=production`, `npm ci --omit=dev`, one process per container.

## Testing
Vitest/Jest unit tests on services; integration via Testcontainers (real Postgres/Redis) with the HTTP layer through `inject`/supertest; contract tests against the OpenAPI spec; coverage floor on changed code.

## Review checklist
Strict types, no `any` leaks - boundary validation - no floating promises - bounded concurrency - timeouts everywhere - parameterized SQL - graceful shutdown - no secrets in logs - tests for unhappy paths.
