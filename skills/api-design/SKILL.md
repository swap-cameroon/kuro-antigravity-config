---
name: api-design
description: "Design or review HTTP/REST APIs: resources, OpenAPI, errors, pagination, versioning, idempotency, auth. Use when defining endpoints or contracts, or reviewing an API for consistency and evolvability."
license: MIT
metadata:
  version: "1.0.0"
---

# API design

Contract first: write or update the OpenAPI spec before code, then generate server stubs/clients or contract tests (`api-contract-testing`). Security details: `secure-by-design-coding`; resilience: `http-resilience`.

## Resources & methods
- Nouns, plural, lowercase, hyphenated: `/orders/{id}/items`. Max two nesting levels; otherwise filter (`/items?orderId=`).
- `GET` safe+idempotent, `PUT` full replace (idempotent), `PATCH` partial, `DELETE` idempotent, `POST` create/non-idempotent actions. Model verbs as sub-resources (`POST /orders/{id}/cancellations`) rather than RPC paths.
- Status codes: 200/201 (+`Location`)/202 (async)/204; 400 malformed, 401 unauthenticated, 403 forbidden, 404, 409 conflict, 412 precondition, 422 semantic validation, 429 (+`Retry-After`), 5xx never leaks internals.

## Errors (one shape everywhere)
Use RFC 9457 `application/problem+json`: `type`, `title`, `status`, `detail`, `instance`, plus `errors[]` with `pointer` and `code` for field problems. Machine-readable `code`s are part of the contract; messages are not.

## Collections
- Cursor pagination (`?limit=50&cursor=...`, response `next_cursor`) for anything that can grow or change; offset only for small, stable sets. Cap `limit` server-side.
- Filtering `?status=open&created_after=...`, sorting `?sort=-created_at`, sparse fields `?fields=`. Document defaults and the stable sort key.

## Evolution
- Additive changes are non-breaking (new optional field/endpoint/enum value *only if clients must tolerate unknowns* - say so in the spec). Removing, renaming, tightening validation or changing semantics is breaking.
- Version in the path (`/v1`) or a header, one strategy only. Deprecate with `Deprecation`/`Sunset` headers and a dated policy.
- Never reuse a field name with a new meaning.

## Reliability semantics
- Unsafe `POST` accepts `Idempotency-Key`; store key + response for a TTL; same key with a different body -> 422.
- Optimistic concurrency: `ETag` + `If-Match` -> 412/409 on conflict.
- Long operations: 202 + `Location` of a status resource; support webhook or polling with backoff hints.
- Timestamps ISO 8601 UTC; money as integer minor units + currency; IDs opaque strings (UUIDv7/ULID), never sequential for public resources.

## Auth & limits
OAuth2/OIDC bearer tokens with scoped permissions; check authorization per object, not only per route (BOLA/IDOR). Rate limit per client with `RateLimit-*` headers. Validate request size and content type.

## Review checklist
Consistent naming and casing - one error format - pagination on every list - idempotency on unsafe creates - documented authz per operation - examples for every response - no breaking change vs previous spec (run `oasdiff` or equivalent) - spec lints clean (Spectral).
