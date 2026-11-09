---
name: exploratory-testing
description: "Independent black-box exploratory testing and user acceptance (UAT): charters, tours, oracles, bug reports, sign-off with evidence. Use for acceptance testing, manual verification of the real app, bug triage, and acting as the customer."
license: MIT
metadata:
  version: "1.0.0"
---

# Exploratory testing and UAT (the independent tester)

The tester is the customer's proxy. **Independence is the whole point**: builders cannot certify their own work, and a test that only mirrors the implementation cannot find what the implementation got wrong. Automation of the same journeys lives in `e2e-testing`.

## Independence rules (UAT mode)
- **Black box**: use only the running app, the PRD and its acceptance criteria. Do not read the source or the builders' tests before the first full pass; do not ask builders for hints.
- **Do not fix** what you find. Report it. A tester who fixes loses independence and hides the defect from the process.
- **Real conditions**: real browser, the documented start command, a fresh data state, the accounts the documentation gives. If the documented way does not work, that is the first bug.
- Evidence or it did not happen: screenshots, exact inputs, console/network errors, timestamps.

## Session method
1. **Charter** (60-90 min, one per session): `Explore <area> with <data/accounts/tools> to discover <risk or information>`.
2. **Journeys first**: execute every PRD journey as each persona/role, by hand, end to end. Record pass/fail per acceptance id.
3. **Tours** to go beyond the happy path: *money* (what the product is for), *landmark* (every main screen), *back-alley* (rarely used features), *saboteur* (invalid, extreme, malicious input; double submit; back button; two tabs/two users at once), *impatient* (fast clicks, interrupts), *after-hours* (time/timezone/expiry), *rotate roles* (can this role see or do what it should not?).
4. **Heuristics**: SFDIPOT (Structure, Function, Data, Interfaces, Platform, Operations, Time); boundaries and equivalence classes; CRUD completeness; state transitions; permissions matrix.
5. **Oracles** (how you know it is wrong): PRD, consistency with itself, similar products, user expectations, standards, common sense, and history (did it work before?).
6. Take notes as you go: what was tried, what was seen, questions, risks.

## Bug report (one file per bug: `BUG-NNN.md`)
`Title (symptom, not guess) - Severity - Frequency - Environment (URL, commit, browser) - Steps to reproduce (numbered, exact data) - Expected - Actual - Evidence - Notes`. Describe **what you observed**, not the suspected cause.
Severity: **S1** blocks a primary journey or loses/corrupts data or breaks security; **S2** a main feature wrong with a workaround; **S3** minor/cosmetic; **S4** suggestion. Any S1 fails the acceptance gate.

## UAT sign-off (`UAT_REPORT.md`)
| Journey / AC id | Persona | Result | Evidence | Bugs |
| :-- | :-- | :-- | :-- | :-- |
Then: sessions run, areas **not** tested and why, open bugs by severity, a clear **GO / NO-GO** with reasons. GO requires: every primary journey passed by hand in the real UI, no open S1, S2s accepted explicitly by the product owner.

## After a fix
Re-test the reproduction exactly, then run a short regression tour around the changed area, and confirm a regression test exists (`e2e-testing`). Verify the fix in the real UI, not by reading the diff.

## Tone
Factual and specific. "I clicked 'Save' with an empty title and the page reloaded with no message" beats "the form is broken". Never blame; never claim coverage you did not exercise.
