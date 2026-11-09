---
name: e2e-testing
description: "Write and run end-to-end tests in a real browser against the real running stack (Playwright): journeys, selectors, seeded data, UI-API consistency, accessibility, traces. Use for user-journey tests, integration smoke checks and acceptance automation."
license: MIT
metadata:
  version: "1.0.0"
---

# End-to-end testing (real browser, real stack)

An E2E test answers one question: **can a real user complete this journey on the real, running system?** Unit and API tests cannot answer it. Backend-only green is not a QA pass for anything with a UI. Strategy and pyramid: `test-strategy`; a11y rules: `ui-design-a11y`; independent human-style testing: `exploratory-testing`.

## Non-negotiables
1. **Real stack**: start the actual app (and DB) and test through the browser. Never mock your own backend in E2E. Stub only third parties you do not own.
2. **First test is the smoke test**: open the app, log in **through the UI** with a seeded account, reach the main screen. If this fails nothing else matters: it exercises the wiring between UI, API, data and browser security in one step.
3. **Journeys come from the PRD**: one test per primary journey, named with its acceptance ids (`AC-3.4 books a room`). No journey in the PRD = no test; no test = not accepted.
4. **UI and API must agree**: after a UI action, verify the backend state through the API or DB (an item created in the UI is returned by the API, and vice versa). The UI must show what the server holds.
5. **Fail on console errors and failed requests**: collect `console.error`, `pageerror` and non-2xx/3xx API responses; fail the test unless expected.

## Playwright setup (default tool; Cypress is acceptable if already present)
- `npm init playwright@latest`; `playwright.config.ts` with `webServer: { command: 'npm start', url: 'http://127.0.0.1:PORT/api/health', reuseExistingServer: !process.env.CI }`, `use.baseURL`, `trace: 'retain-on-failure'`, `screenshot: 'only-on-failure'`, `retries: process.env.CI ? 1 : 0`.
- Deterministic data: dedicated test database/file, reset or seed before the run via a script or API; each test creates its own data with unique names; never depend on test order.
- Auth: log in via the UI in the smoke test and in one test per role; other tests may reuse `storageState` produced by a setup project.
- Selectors in priority order: `getByRole`, `getByLabel`, `getByText`, then `data-testid`. Never CSS/XPath tied to layout.
- Waits: rely on auto-waiting and `expect(locator).toBeVisible()`; never `waitForTimeout`. Wait on conditions (response, URL, text), not time.
- Concurrency journeys (double booking): use two browser contexts and assert exactly one succeeds.

## What to assert
User-visible outcomes (text, state, navigation), error messages for invalid input and forbidden actions, role-based visibility (employee cannot see manager views), empty/loading/error states, keyboard-only completion of the primary journey, and accessibility with `@axe-core/playwright` on each main page (no serious/critical violations).

## Flakiness policy
A flaky test is a bug: reproduce with `--repeat-each=20`, fix the cause (race, shared state, bad wait). No blind retries to get green. Quarantine only with an owner and a deadline.

## CI
Run the full E2E suite on every PR against an ephemeral stack, upload `playwright-report` and traces as artifacts, block merge on failure. Minimal matrix: Chromium always; add WebKit/Firefox when browser-specific risk exists.

## Report
State: command run, number of tests passed/failed, the journeys covered by AC id, what was **not** covered, and attach trace paths. Never claim "tested in the browser" without having executed the suite.
