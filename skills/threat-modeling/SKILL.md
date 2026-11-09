---
name: threat-modeling
description: "Build a threat model before or during design: assets, trust boundaries, STRIDE threats, ranked risks, mitigations. Use for new systems, new features touching auth or data, or architecture security reviews."
license: MIT
metadata:
  version: "1.0.0"
---

# Threat modeling

Run it at design time (cheapest fix) and again when a trust boundary changes. Output `THREAT_MODEL.md`; feed mitigations into Victor's ADRs, Lucas's tests and Marcus's gate. Code-level hunting is `security-auditor` / `llm-sast-scanner`.

## 1. Scope the model (4 questions)
What are we building? What can go wrong? What will we do about it? Did we do a good job? Write the scope, version and date at the top.

## 2. Draw the system
List, from the repo and ARCHITECTURE.md (do not guess; mark unknowns `UNVERIFIED`):
- **Actors**: anonymous, user, admin, service accounts, third parties, insiders.
- **Assets**: data (PII, credentials, payment, tokens), capabilities (admin APIs), availability, reputation.
- **Components & data flows**: client, API, workers, queues, datastores, third-party APIs, CI/CD, secrets store.
- **Trust boundaries**: internet/DMZ, tenant/tenant, user/admin, service/service, prod/non-prod, vendor.
Mermaid data-flow diagram preferred so it can live in Git.

## 3. Enumerate threats with STRIDE per flow crossing a boundary
| Letter | Threat | Typical question |
| :-- | :-- | :-- |
| S | Spoofing | Can someone pretend to be another user/service? token theft, weak service auth |
| T | Tampering | Can data or code be altered in transit/at rest/in the pipeline? |
| R | Repudiation | Could an actor deny an action? are audit logs tamper-evident? |
| I | Information disclosure | Leaks via errors, logs, IDOR, caches, backups, side channels? |
| D | Denial of service | Unbounded input, expensive queries, no rate limits, single points of failure? |
| E | Elevation of privilege | Missing authz checks, confused deputy, SSRF to metadata, injection to RCE? |
Add abuse cases (business-logic abuse: coupon farming, enumeration, mass export) and, for LLM features, prompt injection and tool-abuse paths.

## 4. Rank
Score each threat: likelihood (1-3) x impact (1-3) -> High/Med/Low, with the reasoning in one line. Do not average away a critical impact.

## 5. Decide
For each High/Med: **mitigate** (control + owner + test), **transfer**, **accept** (named approver, expiry date) or **eliminate** (remove the feature/data). Prefer eliminating data over protecting it.

## 6. Output table
`ID | Flow/asset | STRIDE | Threat | Risk | Mitigation | Verified by (test/scan) | Status`

## Rules
- Every High has a mitigation with a test or monitoring alert, else the gate is not passed.
- Re-open the model when adding an actor, data class, external integration or boundary.
- Keep it short: a one-page model that is maintained beats a 40-page model that is not.
