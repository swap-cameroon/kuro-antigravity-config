---
name: product-requirements
description: "Turn a vague idea into a testable PRD: problem, users, journeys, scope, edge cases, acceptance criteria. Use when starting a product or feature, clarifying requirements, or writing user stories."
license: MIT
metadata:
  version: "1.0.0"
---

# Product requirements (PRD)

Output: `PRD.md` that a designer, engineer and tester can each act on without asking the author. For existing undocumented code use `spec-miner` instead.

## Process
1. **Frame the problem** (not the solution): who has it, how they cope today, what it costs, how we will know it is solved (1-3 measurable outcomes with baseline and target).
2. **Ask only blocking questions** (max 5): those whose answer changes scope, architecture or priority. State assumptions for the rest and mark them `ASSUMPTION`.
3. **Users & jobs**: 1-3 personas with the job they hire the product for. No demographics filler.
4. **Journeys**: for each primary job, the happy path as numbered steps, then variants: first-time, returning, error, offline/slow, permission denied, empty state.
5. **Scope**: must / should / could (MoSCoW) and explicit **non-goals**. Anything not listed is out.
6. **Requirements** as user stories with acceptance criteria in Given/When/Then, each independently testable and numbered (`AC-1.2`) so tests and PRs can cite them.
7. **Non-functional**: performance target, availability, security/privacy/regulatory, accessibility, i18n, supported platforms, data retention. Use numbers, not adjectives.
8. **Risks & open questions** with an owner and a decide-by date.

## Quality bar
- Every story: one actor, one outcome, one value ("so that"). Split any story with "and".
- Every criterion is observable and binary; reject "fast", "intuitive", "robust" without a number.
- Edge cases checklist: empty, max size, concurrency, duplicate submit, timezone/locale, partial failure, abuse.
- Trace: outcome -> journey -> story -> AC. Orphans are deleted or justified.
- Hand-off: Njoya consumes NFRs and constraints; Lukong maps AC to tests; Endeley reads availability and data-retention.

## Template
```
# PRD: <name>            Status: draft | Owner: <role> | Date: <YYYY-MM-DD>
## 1. Problem & outcomes   (metric, baseline, target)
## 2. Users & jobs
## 3. Journeys             (happy path + variants)
## 4. Scope                (Must / Should / Could / Non-goals)
## 5. Requirements         (US-n, AC-n.m Given/When/Then)
## 6. Non-functional
## 7. Assumptions, risks, open questions (owner, due)
```
