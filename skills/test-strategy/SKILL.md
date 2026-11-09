---
name: test-strategy
description: "Design a pragmatic test strategy: pyramid, unit/integration/e2e/contract split, fixtures, flakiness, coverage and mutation testing, CI speed. Use when planning tests, fixing weak or flaky suites, or deciding what to test."
license: MIT
metadata:
  version: "1.0.0"
---

# Test strategy

Framework-specific guidance: `spring-testing`, `api-contract-testing`, `angular-developer` (testing refs), `perf` for load. This skill decides **what to test where**.

## Map requirements to tests
Every acceptance criterion (`AC-n.m` from the PRD, see `product-requirements`) has at least one automated test that cites it. Risky areas (money, auth, data migration, concurrency) get more depth than CRUD.

## Pyramid (adapt to the architecture)
| Layer | Scope | Share | Speed target |
| :-- | :-- | :-- | :-- |
| Unit | pure logic, one class/function, no IO | ~70% | ms |
| Integration | real DB/queue via Testcontainers, HTTP layer, repositories | ~20% | seconds |
| Contract | consumer/provider API (OpenAPI, Pact) | as needed | seconds |
| E2E | few critical user journeys through the real UI/stack | ~5-10% | minutes |
Prefer testing behavior at the lowest layer that can observe it. Do not mock what you own; fake or containerize external systems; mock only at boundaries you do not control.

## Writing good tests
- Arrange-Act-Assert; one behavior per test; name states behavior (`rejects_expired_token`).
- Deterministic: inject clock, random seeds, IDs; no sleeps (wait on conditions); no shared mutable state; independent and order-agnostic; isolated data per test.
- Assert outcomes, not implementation details (avoid verifying private calls).
- Builders/fixtures for data; property-based tests for parsers, serializers and invariants (Hypothesis, fast-check, jqwik).
- Test the unhappy paths: validation, authz denial, timeouts, retries, partial failure, idempotency, concurrency.

## Quality signals (use together)
- Line/branch coverage as a **floor** (e.g. 80% on changed code), never a target to game.
- **Mutation testing** (PIT, Stryker, mutmut) on core domain code: surviving mutants reveal weak assertions.
- Flake rate < 1%: quarantine with an owner and a deadline, then fix (`systematic-debugging`).
- Defect escape analysis: each production bug adds a regression test at the right layer.

## E2E (Playwright/Cypress)
Stable selectors (`data-testid`/roles), no UI login repetition (seed auth state), network stubbing only for third parties, traces/screenshots on failure, run against an ephemeral environment, include accessibility checks (axe) on key pages.

## CI
Run fast tests on every commit, full suite on PR/merge, E2E on merge and nightly; parallelize and shard; cache dependencies; fail fast; publish reports/artifacts. Gate: all green + coverage floor + no new flaky tests.

## Output
A short `TEST_PLAN.md`: risk areas, layer per risk, tooling, environments, data strategy, exit criteria. State what is not covered and why.
