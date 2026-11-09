---
name: technical-writing
description: "Write clear technical docs: README, ADRs, API docs, runbooks, tutorials, changelogs, onboarding. Use when documenting code, a decision, an API or an operation, or improving unclear documentation."
license: MIT
metadata:
  version: "1.0.0"
---

# Technical writing

Docs are a product with a reader and a job. Name the reader and the job before writing; pick the doc type (Diataxis): **tutorial** (learn by doing), **how-to** (solve a task), **reference** (look up facts), **explanation** (understand why). Do not mix types in one page.

## Principles
- Lead with the answer/outcome; prerequisites next; steps after. Short sentences, active voice, one idea per paragraph, consistent terms (build a glossary if the domain needs it).
- Every command and snippet must be copy-pasteable and **actually run**; show expected output. Pin versions and OS differences.
- Examples over adjectives; a working example is worth a paragraph.
- Stale docs are worse than none: keep docs next to code, review them in the same PR, add a "Last verified" date where drift is likely.
- Never include secrets or real customer data; use obvious placeholders (`<API_KEY>`).

## Templates
**README**: one-line purpose - badges (build, version, license) - quickstart in <5 commands - usage example - configuration table (name, default, description) - architecture link - contributing/testing - support/license.

**ADR** (`docs/adr/NNNN-title.md`): Status - Context (forces, constraints) - Decision - Alternatives considered (why rejected) - Consequences (good, bad, follow-ups). Immutable once accepted; supersede with a new ADR.

**Runbook**: trigger/alert - impact - prerequisites/access - diagnosis steps with commands and expected output - mitigation/rollback - escalation contacts - verification - post-incident links. Written to be followed at 3 a.m. by someone new.

**API reference**: generated from OpenAPI where possible (`api-design`); add task-based guides, auth walkthrough, error catalogue, rate limits, changelog/deprecations.

**Changelog / release notes**: user-facing impact first, grouped (Added/Changed/Fixed/Security), link to migration steps for breaking changes (`git-workflow-release`).

**Onboarding**: day-1 checklist, local setup verified from a clean machine, who-owns-what, glossary, first good issues.

## Review checklist
Right audience and type - answer in the first screen - steps reproducible on a clean environment - no broken links (check them) - no jargon without definition - headings scannable - diagrams as text (Mermaid) so they diff - accessibility: alt text, descriptive link text.
